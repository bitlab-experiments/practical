"""
main.py
-------
Main entry point: runs the full GEX pipeline for a given asset.

Usage
-----
    python main.py --asset sp500
    python main.py --asset AAPL --period 6mo
    python main.py --asset gold --plot
"""

import argparse
import warnings
from datetime import datetime, timezone

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")


def run_analysis(asset: str, period: str = "1y", plot: bool = True, max_expiry_days: int = 60):
    from data_fetcher import fetch_spot_history, fetch_options_chain, get_risk_free_rate
    from greeks import enrich_chain
    from gex import ehi_summary, regime_stats, gex_vs_realized

    print(f"\n{'='*60}")
    print(f"  GEX / EHI ANALYZER  —  {asset.upper()}")
    print(f"{'='*60}\n")

    # 1. Spot history
    print(f"[1/4] Fetching spot price history ({period}) ...")
    spot_hist = fetch_spot_history(asset, period=period)
    current_price = float(spot_hist["Close"].iloc[-1])
    print(f"      Spot price: ${current_price:,.2f}")
    print(f"      Bars loaded: {len(spot_hist)}")

    # 2. Options chain
    print(f"\n[2/4] Fetching options chain ...")
    chain = fetch_options_chain(asset)
    print(f"      Expiries available: {len(chain['expiries'])}")
    print(f"      Spot (live): ${chain['spot']:,.2f}")

    # 3. Risk-free rate + Greeks
    print(f"\n[3/4] Enriching chain with IV & Greeks ...")
    r = get_risk_free_rate()
    print(f"      Risk-free rate: {r*100:.2f}%")
    enriched = enrich_chain(chain, r=r)
    # Get spot from enriched chain
    spot = enriched["spot"]  # ← add this

    # Check ATM strikes specifically
    first_expiry = list(enriched["chains"].keys())[0]
    calls = enriched["chains"][first_expiry]["calls"]
    # Replace hardcoded range with spot-relative filter
    atm = calls[(calls["strike"] >= spot * 0.95) & (calls["strike"] <= spot * 1.05)]
    print("ATM calls sample:")
    print(atm[["strike", "iv", "gamma", "openInterest", "bid", "ask", "lastPrice"]].to_string())

    # 4. GEX + EHI
    print(f"\n[4/4] Computing GEX & EHI (expiries ≤ {max_expiry_days}d) ...")
    summary = ehi_summary(
        enriched, spot_hist, multiplier=100, max_expiry_days=max_expiry_days
    )
    gex_df = summary["gex_df"]
    ehi_df = summary["ehi_df"]
    scale  = summary["ehi_scale"]

    from gex import gex_summary_by_expiry
    expiry_breakdown = gex_summary_by_expiry(
        enriched, multiplier=100, max_expiry_days=max_expiry_days
    )
    ehi_buckets = {k: v * scale for k, v in expiry_breakdown["buckets"].items()}

    print(f"\n{'─'*50}")
    print(f"  NET GEX  : {summary['net_gex']:+.2f}B")
    print(f"  NET EHI  : {summary['net_ehi']:+.4f}  (scale {scale:.4f})")
    print(f"  NOTIONAL : ${summary['derivatives_notional']/1e9:.2f}B")
    print(f"  ADV DEPTH: ${summary['spot_market_depth']/1e9:.2f}B  ({summary['adv_lookback']}d)")
    print(f"  0DTE GEX : {expiry_breakdown['buckets']['0dte']:+.2f}B")
    print(f"  0DTE EHI : {ehi_buckets['0dte']:+.4f}")
    print(f"  WEEKLY   : {expiry_breakdown['buckets']['weekly']:+.2f}B  |  EHI {ehi_buckets['weekly']:+.4f}")
    print(f"  MONTHLY  : {expiry_breakdown['buckets']['monthly']:+.2f}B  |  EHI {ehi_buckets['monthly']:+.4f}")
    flip_pt = 'N/A' if summary['flip_point'] is None else f"${summary['flip_point']:,.2f}"
    print(f"  FLIP PT  : {flip_pt}")
    print(f"  GEX REG  : {summary['regime']}")
    print(f"  EHI REG  : {summary['ehi_regime']}")
    print(f"{'─'*50}\n")

    if not ehi_df.empty:
        top = ehi_df.reindex(ehi_df["net_ehi_strike"].abs().nlargest(10).index)[
            ["strike", "call_oi", "put_oi", "call_ehi", "put_ehi", "net_ehi_strike"]
        ]
        print("Top 10 strikes by |net EHI|:")
        print(top.to_string(index=False, float_format="{:+.4f}".format))

    if plot:
        _plot(spot_hist, ehi_df, summary, asset)

    return summary, spot_hist


def _plot(spot_hist, gex_df, summary, asset):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
    except ImportError:
        print("\n[plot] matplotlib not installed — skipping charts.")
        return

    spot = summary["spot"]
    flip = summary["flip_point"]

    fig = plt.figure(figsize=(16, 10), facecolor="#0d1117")
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

    txt_color  = "#e6edf3"
    grid_color = "#21262d"
    call_color = "#3fb950"
    put_color  = "#f85149"
    net_color  = "#58a6ff"
    bg_color   = "#161b22"

    def style_ax(ax, title):
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=txt_color, labelsize=8)
        ax.set_title(title, color=txt_color, fontsize=10, pad=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(grid_color)
        ax.yaxis.label.set_color(txt_color)
        ax.xaxis.label.set_color(txt_color)
        ax.grid(True, color=grid_color, linewidth=0.5)

    # ── 1. Spot price history ──────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    close = spot_hist["Close"].squeeze()
    ax1.plot(close.index, close.values, color=net_color, linewidth=1.2)
    ax1.fill_between(close.index, close.values, close.values.min(), alpha=0.08, color=net_color)
    if flip:
        ax1.axhline(flip, color="#f0a500", linewidth=1, linestyle="--", label=f"GEX Flip ~${flip:,.0f}")
        ax1.legend(fontsize=8, facecolor=bg_color, labelcolor=txt_color)
    ax1.axhline(spot, color=txt_color, linewidth=0.6, linestyle=":", alpha=0.6)
    style_ax(ax1, f"{asset.upper()} — Price History")
    ax1.set_ylabel("Price")

    plot_df = gex_df
    if plot_df.empty:
        fig.text(0.5, 0.2, "No EHI data available", ha="center", color=txt_color, fontsize=14)
    else:
        # ── 2. EHI by strike (bar chart) ──────────────────────────────
        ax2 = fig.add_subplot(gs[1, 0])
        strikes = plot_df["strike"]
        net     = plot_df["net_ehi_strike"]
        colors  = [call_color if v >= 0 else put_color for v in net]
        ax2.bar(strikes, net, width=(strikes.max() - strikes.min()) / len(strikes) * 0.8,
                color=colors, alpha=0.85)
        ax2.axvline(spot, color=txt_color, linewidth=1.2, linestyle="--", label=f"Spot ${spot:,.0f}")
        if flip:
            ax2.axvline(flip, color="#f0a500", linewidth=1.2, linestyle=":", label=f"Flip ${flip:,.0f}")
        ax2.axhline(0, color=txt_color, linewidth=0.5)
        ax2.legend(fontsize=7, facecolor=bg_color, labelcolor=txt_color)
        style_ax(ax2, "Net EHI by Strike")
        ax2.set_xlabel("Strike")
        ax2.set_ylabel("EHI")

        # ── 3. Call vs Put OI ─────────────────────────────────────────
        ax3 = fig.add_subplot(gs[1, 1])
        width = (strikes.max() - strikes.min()) / len(strikes) * 0.4
        ax3.bar(strikes - width/2, plot_df["call_oi"] / 1e3, width=width,
                color=call_color, alpha=0.8, label="Call OI")
        ax3.bar(strikes + width/2, plot_df["put_oi"] / 1e3, width=width,
                color=put_color,  alpha=0.8, label="Put OI")
        ax3.axvline(spot, color=txt_color, linewidth=1.2, linestyle="--")
        ax3.legend(fontsize=7, facecolor=bg_color, labelcolor=txt_color)
        style_ax(ax3, "Call vs Put Open Interest (k)")
        ax3.set_xlabel("Strike")
        ax3.set_ylabel("OI (thousands)")

    # Title
    regime_color = call_color if "positive" in summary["ehi_regime"] else (
                   put_color  if "negative" in summary["ehi_regime"] else "#f0a500")
    fig.suptitle(
        f"{asset.upper()}  |  GEX: {summary['net_gex']:+.2f}B  |  "
        f"EHI: {summary['net_ehi']:+.4f}  |  {summary['ehi_regime']}",
        color=regime_color, fontsize=11, fontweight="bold", y=0.98
    )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    fig.text(
        0.99, 0.01, f"Generated: {generated_at}",
        ha="right", va="bottom", fontsize=8, color=txt_color, alpha=0.7,
    )

    out = f"/Users/macbook/Projects/experimental/practical/financial-greeks/gex_analyzer/calculations/{asset.lower()}_gex_{datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S-UTC")}.png"
    fig.savefig(out, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"\n[plot] Chart saved → {out}")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GEX Analyzer")
    parser.add_argument("--asset",  default="spy",  help="Ticker or friendly name (sp500, gold, oil, AAPL ...)")
    parser.add_argument("--period", default="1y",   help="History period (1mo, 3mo, 6mo, 1y, 2y)")
    parser.add_argument("--plot",   action="store_true", default=True, help="Generate charts")
    parser.add_argument("--max-expiry-days", type=int, default=60, help="Max DTE for GEX calc")
    args = parser.parse_args()

    run_analysis(
        asset           = args.asset,
        period          = args.period,
        plot            = args.plot,
        max_expiry_days = args.max_expiry_days,
    )
