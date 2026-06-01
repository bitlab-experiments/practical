"""
demo.py
-------
Runs the full GEX pipeline on SYNTHETIC data so you can verify
the logic without needing live API access (useful for CI / testing).

Also shows how to wire real data in.
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ── Import our modules ──────────────────────────────────────────────────────
from greeks import bs_price, bs_greeks, implied_vol
from gex    import compute_gex, net_gex, gex_flip_point, gex_summary, regime_stats


def make_synthetic_chain(
    spot: float = 500.0,
    r: float = 0.045,
    atm_iv: float = 0.18,
    n_strikes: int = 30,
    strike_width: float = 5.0,
    expiries_days: list = [7, 14, 30, 45],
) -> dict:
    """
    Build a synthetic options chain for testing.
    OI is fabricated with a typical smile-like distribution
    (heaviest near ATM, skewed towards puts for protective demand).
    """
    today = pd.Timestamp.today().normalize()
    chains = {}

    # Strike ladder centered on spot
    half = n_strikes // 2
    strikes = np.arange(spot - half * strike_width,
                        spot + half * strike_width + 1,
                        strike_width)

    for days in expiries_days:
        T = days / 365.0
        expiry = (today + pd.Timedelta(days=days)).strftime("%Y-%m-%d")

        call_rows, put_rows = [], []
        for K in strikes:
            moneyness = (K - spot) / spot

            # Vol smile: higher IV for OTM puts (skew), slight smile for calls
            iv_call = atm_iv + 0.05 * (moneyness ** 2) + 0.01 * max(moneyness, 0)
            iv_put  = atm_iv + 0.05 * (moneyness ** 2) - 0.03 * moneyness  # put skew

            c_price = bs_price(spot, K, T, r, iv_call, "call")
            p_price = bs_price(spot, K, T, r, iv_put,  "put")

            # OI: bell-shaped, heavier on puts (typical for index options)
            dist = abs(moneyness)
            base_oi = int(10000 * np.exp(-30 * dist**2))
            call_oi = max(100, base_oi + np.random.randint(-200, 200))
            put_oi  = max(100, int(base_oi * 1.4) + np.random.randint(-200, 200))  # put heavy

            call_rows.append({
                "strike": K, "bid": c_price * 0.98, "ask": c_price * 1.02,
                "lastPrice": c_price, "openInterest": call_oi,
                "impliedVolatility": iv_call, "volume": call_oi // 10,
            })
            put_rows.append({
                "strike": K, "bid": p_price * 0.98, "ask": p_price * 1.02,
                "lastPrice": p_price, "openInterest": put_oi,
                "impliedVolatility": iv_put, "volume": put_oi // 10,
            })

        chains[expiry] = {
            "calls": pd.DataFrame(call_rows),
            "puts":  pd.DataFrame(put_rows),
        }

    return {
        "spot":     spot,
        "ticker":   "SYNTHETIC",
        "expiries": list(chains.keys()),
        "chains":   chains,
        "r":        r,
    }


def make_synthetic_spot_history(
    spot: float = 500.0,
    n_days: int = 252,
    annual_vol: float = 0.18,
    drift: float = 0.08,
) -> pd.DataFrame:
    """Simulate GBM price path."""
    np.random.seed(42)
    dt = 1 / 252
    returns = (drift - 0.5 * annual_vol**2) * dt + annual_vol * np.sqrt(dt) * np.random.randn(n_days)
    prices = spot * np.exp(np.cumsum(returns))
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=n_days)
    return pd.DataFrame({"Close": prices, "Open": prices * 0.999,
                          "High": prices * 1.005, "Low": prices * 0.995}, index=dates)


def demo_greeks():
    print("=" * 55)
    print("  BLACK-SCHOLES GREEKS DEMO")
    print("=" * 55)

    S, K, T, r, sigma = 500, 500, 0.25, 0.045, 0.20
    call = bs_greeks(S, K, T, r, sigma, "call")
    put  = bs_greeks(S, K, T, r, sigma, "put")

    print(f"\n  ATM option: S={S}, K={K}, T={T}y, r={r*100:.1f}%, σ={sigma*100:.0f}%")
    print(f"\n  {'Greek':<10}  {'Call':>10}  {'Put':>10}")
    print(f"  {'─'*35}")
    for key in ["delta", "gamma", "theta", "vega", "rho"]:
        print(f"  {key:<10}  {call[key]:>10.6f}  {put[key]:>10.6f}")

    # IV round-trip test
    call_price = bs_price(S, K, T, r, sigma, "call")
    iv_back = implied_vol(call_price, S, K, T, r, "call")
    print(f"\n  IV round-trip: input={sigma*100:.2f}% → price=${call_price:.4f} → recovered={iv_back*100:.2f}%")
    assert abs(iv_back - sigma) < 1e-5, "IV solver failed!"
    print("  ✓ IV solver accurate to 5 decimal places")


def demo_gex():
    print("\n" + "=" * 55)
    print("  GEX CALCULATION DEMO")
    print("=" * 55)

    chain = make_synthetic_chain(spot=500.0, atm_iv=0.18)

    # Add Greeks (chain is already enriched in synthetic mode)
    # We mimic the enrich step by adding gamma from BS directly
    spot = chain["spot"]
    r    = chain["r"]

    for expiry, leg in chain["chains"].items():
        T = (pd.Timestamp(expiry) - pd.Timestamp.today().normalize()).days / 365.0
        for df, otype in [(leg["calls"], "call"), (leg["puts"], "put")]:
            gammas, deltas, ivs = [], [], []
            for _, row in df.iterrows():
                iv = float(row["impliedVolatility"])
                g  = bs_greeks(spot, row["strike"], T, r, iv, otype)
                gammas.append(g["gamma"])
                deltas.append(g["delta"])
                ivs.append(iv)
            df["gamma"] = gammas
            df["delta"] = deltas
            df["iv"]    = ivs
            df["T"]     = T

    summary = gex_summary(chain)
    gex_df  = summary["gex_df"]

    print(f"\n  Spot Price : ${summary['spot']:,.2f}")
    print(f"  Net GEX    : {summary['net_gex']:+.3f}B")
    flip_str = "N/A" if not summary["flip_point"] else f"${summary['flip_point']:,.2f}"
    print(f"  Flip Point : {flip_str}")
    print(f"  Regime     : {summary['regime']}")

    print(f"\n  Top 5 strikes by |GEX|:")
    top5 = gex_df.reindex(gex_df["net_gex_strike"].abs().nlargest(5).index)
    print(f"  {'Strike':>8}  {'Call GEX':>10}  {'Put GEX':>10}  {'Net GEX':>10}")
    print(f"  {'─'*45}")
    for _, row in top5.iterrows():
        print(f"  {row['strike']:>8.0f}  {row['call_gex']:>10.4f}  {row['put_gex']:>10.4f}  {row['net_gex_strike']:>+10.4f}")

    return summary, chain


def demo_regime_analysis():
    print("\n" + "=" * 55)
    print("  REGIME vs REALIZED MOVE ANALYSIS")
    print("=" * 55)

    # Simulate daily GEX series (varying over time)
    spot_hist = make_synthetic_spot_history()
    n = len(spot_hist)
    np.random.seed(7)

    # Synthetic GEX: oscillates between positive and negative regimes
    t = np.linspace(0, 4 * np.pi, n)
    gex_vals = 2 * np.sin(t) + 0.5 * np.random.randn(n)
    gex_series = pd.Series(gex_vals, index=spot_hist.index, name="gex")

    from gex import gex_vs_realized
    merged = gex_vs_realized(spot_hist, gex_series, forward_days=1)
    stats  = regime_stats(merged)

    print(f"\n  Correlation(GEX, next-day abs move): "
          f"{merged['gex'].corr(merged['fwd_abs_return']):.4f}")

    print(f"\n  Realized move by GEX regime (1-day forward):")
    print(f"  {'Regime':<22}  {'N':>5}  {'Mean |Δ%|':>10}  {'Median |Δ%|':>12}  {'Std':>8}")
    print(f"  {'─'*62}")
    for regime, row in stats.iterrows():
        print(f"  {str(regime):<22}  {row['n_days']:>5.0f}  "
              f"{row['mean_abs_move']:>10.3f}%  {row['median_abs_move']:>12.3f}%  {row['std_move']:>8.3f}%")


if __name__ == "__main__":
    demo_greeks()
    summary, chain = demo_gex()
    demo_regime_analysis()

    print("\n" + "=" * 55)
    print("  All demos passed. Ready for live data.")
    print("  Run: python main.py --asset spy --plot")
    print("=" * 55 + "\n")
