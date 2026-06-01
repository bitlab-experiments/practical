"""
data_fetcher.py
---------------
Pulls spot price history and options chain data via yfinance.
Supports: S&P500 (SPY/SPX), Gold (GLD), Oil (USO), individual stocks.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional


ASSET_MAP = {
    "sp500": "SPY",
    "gold":  "GLD",
    "oil":   "USO",
    "vix":   "^VIX",
}


def resolve_ticker(asset: str) -> str:
    """Map friendly name to ticker, or pass through if already a ticker."""
    return ASSET_MAP.get(asset.lower(), asset.upper())


def fetch_spot_history(
    asset: str,
    period: str = "1y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch OHLCV history for an asset.

    Parameters
    ----------
    asset   : ticker or friendly name (sp500, gold, oil, or e.g. AAPL)
    period  : yfinance period string (1mo, 3mo, 6mo, 1y, 2y, 5y)
    interval: bar size (1d, 1wk, 1h)

    Returns
    -------
    DataFrame with columns: Open, High, Low, Close, Volume
    """
    ticker = resolve_ticker(asset)
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No price data returned for ticker '{ticker}'")
    df.index = pd.to_datetime(df.index)
    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def fetch_options_chain(asset: str) -> dict:
    """
    Fetch the full options chain for all available expiries.

    Returns
    -------
    dict with keys:
        'spot'      : float  — current spot price
        'ticker'    : str
        'expiries'  : list[str]
        'chains'    : dict[expiry -> {'calls': DataFrame, 'puts': DataFrame}]
    """
    ticker = resolve_ticker(asset)
    tk = yf.Ticker(ticker)

    spot_info = tk.fast_info
    try:
        spot = spot_info.last_price
    except Exception:
        hist = tk.history(period="1d")
        spot = float(hist["Close"].iloc[-1])

    expiries = tk.options
    if not expiries:
        raise ValueError(f"No options data available for '{ticker}'")

    chains = {}
    for exp in expiries:
        try:
            opt = tk.option_chain(exp)
            calls = opt.calls.copy()
            puts  = opt.puts.copy()
            # Ensure numeric columns
            for df in (calls, puts):
                for col in ["strike", "bid", "ask", "lastPrice", "openInterest", "impliedVolatility", "volume"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
            chains[exp] = {"calls": calls, "puts": puts}
        except Exception as e:
            print(f"  [warn] Skipping expiry {exp}: {e}")
            continue

    return {
        "spot":     spot,
        "ticker":   ticker,
        "expiries": list(chains.keys()),
        "chains":   chains,
    }


def get_risk_free_rate() -> float:
    """Approximate risk-free rate from 13-week T-bill (^IRX)."""
    try:
        irx = yf.download("^IRX", period="5d", progress=False, auto_adjust=True)
        if isinstance(irx.columns, pd.MultiIndex):
            irx.columns = irx.columns.get_level_values(0)
        rate = float(irx["Close"].dropna().iloc[-1]) / 100.0
        return rate
    except Exception:
        return 0.045  # fallback: 4.5%
