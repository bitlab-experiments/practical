"""
gex.py
------
Gamma Exposure (GEX) calculation and regime analysis.

Key concepts
------------
- GEX per strike = Gamma × OpenInterest × ContractMultiplier × Spot²
- Net GEX = Σ(Call GEX) − Σ(Put GEX)
  (dealers assumed long calls / short puts → puts flip sign)
- Positive GEX → dealers buy dips, sell rips → vol suppression
- Negative GEX → dealers amplify moves → volatile, trending

Exports
-------
compute_gex(enriched_chain, multiplier)  -> pd.DataFrame  (per-strike GEX)
net_gex(gex_df)                          -> float
gex_flip_point(gex_df)                   -> float | None
ehi_summary(enriched_chain, spot_hist)   -> dict (GEX scaled by derivatives/depth)
gex_vs_realized(spot_history, gex_series) -> pd.DataFrame
"""

import numpy as np
import pandas as pd
from typing import Optional


CONTRACT_MULTIPLIER = 100  # equity standard: 1 contract = 100 shares


def _resolve_oi(row) -> int:
    """Open interest with 20% volume fallback (matches compute_gex)."""
    oi = row.get("openInterest", 0)
    oi = int(oi) if pd.notna(oi) else 0
    if oi == 0:
        vol = row.get("volume", 0)
        vol = int(vol) if pd.notna(vol) else 0
        oi = int(vol * 0.20)
    return oi


def compute_gex(
    enriched_chain: dict,
    multiplier: int = CONTRACT_MULTIPLIER,
    max_expiry_days: int = 60,
) -> pd.DataFrame:
    """
    Compute GEX across all strikes and expiries (up to max_expiry_days out).

    Parameters
    ----------
    enriched_chain   : output of greeks.enrich_chain()
    multiplier       : contract multiplier (100 for equities)
    max_expiry_days  : ignore far-dated expiries (they have low weight)

    Returns
    -------
    DataFrame with columns:
        strike, expiry, T,
        call_gex, put_gex, net_gex_strike,
        call_oi, put_oi, call_gamma, put_gamma, call_iv, put_iv
    """
    spot = enriched_chain["spot"]
    rows = []
    oi_fallback_count = 0

    today = pd.Timestamp.today().normalize()

    for expiry, leg in enriched_chain["chains"].items():
        exp_dt = pd.Timestamp(expiry)
        days_out = (exp_dt - today).days
        if days_out < 0 or days_out > max_expiry_days:
            continue

        calls = leg["calls"].copy()
        puts  = leg["puts"].copy()

        for _, c in calls.iterrows():
            gamma = c.get("gamma", np.nan)

            # Skip if gamma is unusable
            if np.isnan(gamma) or gamma == 0:
                continue

            oi_raw = c.get("openInterest", 0)
            oi_raw = int(oi_raw) if pd.notna(oi_raw) else 0
            oi = _resolve_oi(c)
            if oi == 0:
                continue
            if oi_raw == 0 and oi > 0:
                oi_fallback_count += 1

            call_gex = gamma * oi * multiplier * spot ** 2 / 1e9  # in billions

            # Find matching put by strike
            put_row = puts[puts["strike"] == c["strike"]]
            if len(put_row):
                p_gamma_val = put_row["gamma"].values[0]
                p_gamma = 0.0 if (np.isnan(p_gamma_val) or p_gamma_val == 0) else p_gamma_val

                p_oi = _resolve_oi(put_row.iloc[0])
                p_iv = put_row["iv"].values[0] if "iv" in put_row.columns else np.nan
            else:
                p_gamma, p_oi, p_iv = 0.0, 0, np.nan

            put_gex = p_gamma * p_oi * multiplier * spot ** 2 / 1e9

            rows.append({
                "strike":         c["strike"],
                "expiry":         expiry,
                "days_to_expiry": days_out,
                "T":              c.get("T", days_out / 365),
                "call_gamma":     gamma,
                "put_gamma":      p_gamma,
                "call_oi":        int(oi),
                "put_oi":         p_oi,
                "call_iv":        c.get("iv", np.nan),
                "put_iv":         p_iv,
                "call_gex":       call_gex,
                "put_gex":        put_gex,
                "net_gex_strike": call_gex - put_gex,
            })

    if oi_fallback_count > 0:
        print(f"  ⚠️  OI unavailable for {oi_fallback_count} strikes — used volume as fallback. "
              f"Run during market hours for accurate GEX.")

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Aggregate across expiries for same strike
    agg = (
        df.groupby("strike")
        .agg(
            call_gex       = ("call_gex",       "sum"),
            put_gex        = ("put_gex",        "sum"),
            net_gex_strike = ("net_gex_strike", "sum"),
            call_oi        = ("call_oi",        "sum"),
            put_oi         = ("put_oi",         "sum"),
            call_gamma     = ("call_gamma",     "mean"),
            put_gamma      = ("put_gamma",      "mean"),
            call_iv        = ("call_iv",        "mean"),
            put_iv         = ("put_iv",         "mean"),
        )
        .reset_index()
        .sort_values("strike")
    )
    return agg


def net_gex(gex_df: pd.DataFrame) -> float:
    """Total net GEX across all strikes (billions USD)."""
    if gex_df.empty:
        return 0.0
    return float(gex_df["net_gex_strike"].sum())


def gex_flip_point(gex_df: pd.DataFrame) -> Optional[float]:
    """
    Estimate the 'GEX flip' strike — where dealer gamma exposure crosses zero.
    This is the strike where net_gex changes sign (interpolated).
    Returns None if no sign change exists.
    """
    if gex_df.empty:
        return None

    df = gex_df.sort_values("strike").copy()
    df["cumulative_gex"] = df["net_gex_strike"].cumsum()

    sign_changes = df["cumulative_gex"].apply(np.sign).diff().abs() > 0
    flip_rows = df[sign_changes]
    if flip_rows.empty:
        return None

    # Linear interpolation between the two strikes that straddle zero
    idx = flip_rows.index[0]
    loc = df.index.get_loc(idx)
    if loc == 0:
        return float(df["strike"].iloc[0])

    s1 = df["strike"].iloc[loc - 1]
    s2 = df["strike"].iloc[loc]
    g1 = df["cumulative_gex"].iloc[loc - 1]
    g2 = df["cumulative_gex"].iloc[loc]
    # interpolate
    flip = s1 + (s2 - s1) * (-g1) / (g2 - g1)
    return float(flip)


def derivatives_notional(
    enriched_chain: dict,
    multiplier: int = CONTRACT_MULTIPLIER,
    max_expiry_days: int = 60,
) -> float:
    """
    Total options notional: Σ(OI × multiplier × spot) over the GEX expiry window.
    """
    spot = enriched_chain["spot"]
    today = pd.Timestamp.today().normalize()
    total_oi = 0

    for expiry, leg in enriched_chain["chains"].items():
        days_out = (pd.Timestamp(expiry) - today).days
        if days_out < 0 or days_out > max_expiry_days:
            continue
        for side in ("calls", "puts"):
            for _, row in leg[side].iterrows():
                total_oi += _resolve_oi(row)

    return float(total_oi * multiplier * spot)


def spot_market_depth(spot_hist: pd.DataFrame, lookback: int = 20) -> float:
    """Average daily dollar volume as a proxy for spot market depth."""
    tail = spot_hist.tail(lookback)
    if tail.empty:
        return 0.0
    close = tail["Close"].squeeze()
    volume = tail["Volume"].squeeze()
    return float((volume * close).mean())


def ehi_regime(net_ehi: float) -> str:
    """Regime label from net EHI (adaptive band near zero)."""
    band = max(0.01, 0.15 * abs(net_ehi))
    if net_ehi > band:
        return "positive — vol suppression likely"
    if net_ehi < -band:
        return "negative — vol amplification likely"
    return "neutral / near flip — regime uncertain"


def scale_gex_to_ehi(gex_df: pd.DataFrame, scale: float) -> pd.DataFrame:
    """Scale per-strike GEX columns to EHI."""
    if gex_df.empty:
        return gex_df.copy()
    ehi_df = gex_df.copy()
    for col in ("call_gex", "put_gex", "net_gex_strike"):
        ehi_df[col] = ehi_df[col] * scale
    return ehi_df.rename(columns={
        "call_gex": "call_ehi",
        "put_gex": "put_ehi",
        "net_gex_strike": "net_ehi_strike",
    })


def ehi_summary(
    enriched_chain: dict,
    spot_hist: pd.DataFrame,
    multiplier: int = CONTRACT_MULTIPLIER,
    max_expiry_days: int = 60,
    adv_lookback: int = 20,
) -> dict:
    """
    Effective Hedging Impact: GEX × (derivatives notional / spot market depth).

    Returns GEX summary fields plus net_ehi, ehi_df, scale, and liquidity inputs.
    """
    base = gex_summary(
        enriched_chain,
        multiplier=multiplier,
        max_expiry_days=max_expiry_days,
    )
    notional = derivatives_notional(
        enriched_chain, multiplier=multiplier, max_expiry_days=max_expiry_days
    )
    depth = spot_market_depth(spot_hist, lookback=adv_lookback)
    scale = notional / depth if depth > 0 else 0.0

    gex_df = base["gex_df"]
    ehi_df = scale_gex_to_ehi(gex_df, scale)
    net_ehi = base["net_gex"] * scale

    return {
        **base,
        "net_ehi":                net_ehi,
        "ehi_regime":             ehi_regime(net_ehi),
        "ehi_df":                 ehi_df,
        "ehi_scale":              scale,
        "derivatives_notional":   notional,
        "spot_market_depth":      depth,
        "adv_lookback":           adv_lookback,
    }


def gex_summary(
    enriched_chain: dict,
    multiplier: int = CONTRACT_MULTIPLIER,
    max_expiry_days: int = 60,
) -> dict:
    """
    High-level GEX summary for an asset.

    Returns
    -------
    dict with: spot, net_gex, flip_point, regime, gex_df
    """
    gex_df = compute_gex(enriched_chain, multiplier, max_expiry_days=max_expiry_days)
    if gex_df.empty:
        return {"spot": enriched_chain["spot"], "net_gex": 0, "flip_point": None,
                "regime": "unknown", "gex_df": gex_df}

    total_gex  = net_gex(gex_df)
    flip       = gex_flip_point(gex_df)
    spot       = enriched_chain["spot"]

    if total_gex > 0.5:
        regime = "positive — vol suppression likely"
    elif total_gex < -0.5:
        regime = "negative — vol amplification likely"
    else:
        regime = "neutral / near flip — regime uncertain"

    return {
        "spot":      spot,
        "net_gex":   total_gex,
        "flip_point": flip,
        "regime":    regime,
        "gex_df":    gex_df,
    }

def gex_summary_by_expiry(
    enriched_chain: dict,
    multiplier: int = CONTRACT_MULTIPLIER,
    max_expiry_days: int = 60,
) -> dict:
    """
    Break down GEX by expiry bucket to show where gamma pressure is concentrated.

    Returns
    -------
    dict with keys: 0dte, weekly, monthly, and a per_expiry breakdown
    """
    spot = enriched_chain["spot"]
    today = pd.Timestamp.today().normalize()
    
    buckets = {"0dte": 0.0, "weekly": 0.0, "monthly": 0.0}
    per_expiry = {}

    for expiry, leg in enriched_chain["chains"].items():
        days_out = (pd.Timestamp(expiry) - today).days
        if days_out < 0 or days_out > max_expiry_days:
            continue

        # Compute GEX for this single expiry
        single_chain = {**enriched_chain, "chains": {expiry: leg}}
        gex_df = compute_gex(
            single_chain, multiplier=multiplier, max_expiry_days=days_out + 1
        )

        if gex_df.empty:
            continue

        expiry_gex = float(gex_df["net_gex_strike"].sum())
        per_expiry[expiry] = {"days_out": days_out, "net_gex": expiry_gex}

        if days_out == 0:
            buckets["0dte"] += expiry_gex
        elif days_out <= 7:
            buckets["weekly"] += expiry_gex
        else:
            buckets["monthly"] += expiry_gex

    return {
        "spot":       spot,
        "buckets":    buckets,
        "per_expiry": per_expiry,
    }

# ---------------------------------------------------------------------------
# GEX vs Realized Move Analysis
# ---------------------------------------------------------------------------

def gex_vs_realized(
    spot_history: pd.DataFrame,
    gex_series: pd.Series,
    forward_days: int = 1,
) -> pd.DataFrame:
    """
    Measure correlation between lagged GEX and forward realized move.

    Parameters
    ----------
    spot_history : DataFrame with DatetimeIndex and 'Close' column
    gex_series   : pd.Series with DatetimeIndex, values = net GEX
    forward_days : how many days forward to measure realized move

    Returns
    -------
    DataFrame with columns: date, gex, fwd_return, fwd_abs_return, gex_regime
    """
    close = spot_history["Close"].squeeze()
    fwd_return = close.pct_change(forward_days).shift(-forward_days)
    fwd_abs    = fwd_return.abs()

    merged = pd.DataFrame({
        "close":          close,
        "gex":            gex_series,
        "fwd_return":     fwd_return,
        "fwd_abs_return": fwd_abs,
    }).dropna()

    merged["gex_regime"] = pd.cut(
        merged["gex"],
        bins=[-np.inf, -1, 0, 1, np.inf],
        labels=["strongly negative", "mildly negative", "mildly positive", "strongly positive"],
    )

    return merged


def regime_stats(gex_realized_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summary statistics of realized moves per GEX regime.
    """
    stats = (
        gex_realized_df
        .groupby("gex_regime", observed=True)
        .agg(
            n_days          = ("fwd_abs_return", "count"),
            mean_abs_move   = ("fwd_abs_return", "mean"),
            median_abs_move = ("fwd_abs_return", "median"),
            std_move        = ("fwd_abs_return", "std"),
            mean_return     = ("fwd_return",     "mean"),
        )
    )
    stats["mean_abs_move"]   = (stats["mean_abs_move"] * 100).round(3)
    stats["median_abs_move"] = (stats["median_abs_move"] * 100).round(3)
    stats["std_move"]        = (stats["std_move"] * 100).round(3)
    stats["mean_return"]     = (stats["mean_return"] * 100).round(3)
    return stats
