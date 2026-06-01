"""
greeks.py
---------
Black-Scholes implied volatility solver and Greeks calculator.

Exports
-------
implied_vol(market_price, S, K, T, r, option_type) -> float
bs_greeks(S, K, T, r, sigma, option_type)          -> dict
enrich_chain(chain_data, spot, r)                  -> dict
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import pandas as pd
import warnings

BOGUS_IVS = {0.015635, 0.031260, 0.062509, 0.125009, 0.250007, 0.500005}

def _is_bogus_iv(iv: float) -> bool:
    return any(abs(iv - b) < 1e-4 for b in BOGUS_IVS)

# ---------------------------------------------------------------------------
# Core Black-Scholes
# ---------------------------------------------------------------------------

def _d1_d2(S: float, K: float, T: float, r: float, sigma: float):
    """Compute d1 and d2 for Black-Scholes."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return np.nan, np.nan
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Theoretical Black-Scholes price."""
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    if np.isnan(d1):
        return np.nan
    if option_type.lower() == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def implied_vol(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    tol: float = 1e-6,
) -> float:
    """
    Solve for implied volatility using Brent's method.

    Returns np.nan if no solution found (deep ITM/OTM, zero-price options, etc.)
    """
    if T <= 0 or market_price <= 0 or S <= 0 or K <= 0:
        return np.nan

    intrinsic = max(0.0, (S - K) if option_type == "call" else (K - S))
    if market_price <= intrinsic:
        return np.nan

    def objective(sigma):
        return bs_price(S, K, T, r, sigma, option_type) - market_price

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            iv = brentq(objective, 1e-5, 20.0, xtol=tol, maxiter=200)
        return iv
    except (ValueError, RuntimeError):
        return np.nan


def bs_greeks(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
) -> dict:
    """
    Compute Black-Scholes Greeks.

    Returns
    -------
    dict with keys: delta, gamma, theta, vega, rho, iv (=sigma passed in)
    """
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    if np.isnan(d1):
        return dict(delta=np.nan, gamma=np.nan, theta=np.nan, vega=np.nan, rho=np.nan)

    phi_d1 = norm.pdf(d1)  # standard normal PDF at d1

    gamma = phi_d1 / (S * sigma * np.sqrt(T))
    vega  = S * phi_d1 * np.sqrt(T) / 100  # per 1% vol move

    if option_type.lower() == "call":
        delta = norm.cdf(d1)
        theta = (
            -S * phi_d1 * sigma / (2 * np.sqrt(T))
            - r * K * np.exp(-r * T) * norm.cdf(d2)
        ) / 365
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        delta = norm.cdf(d1) - 1
        theta = (
            -S * phi_d1 * sigma / (2 * np.sqrt(T))
            + r * K * np.exp(-r * T) * norm.cdf(-d2)
        ) / 365
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    return dict(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)


# ---------------------------------------------------------------------------
# Chain enrichment
# ---------------------------------------------------------------------------

def _mid_price(row) -> float:
    """Use mid of bid/ask; fall back to lastPrice."""
    bid = row.get("bid", np.nan)
    ask = row.get("ask", np.nan)
    last = row.get("lastPrice", np.nan)
    if pd.notna(bid) and pd.notna(ask) and bid > 0 and ask > 0:
        return (bid + ask) / 2.0
    if pd.notna(last) and last > 0:
        return last
    return np.nan

def _enrich_df(df, S, expiry_date, r, option_type):
    today = pd.Timestamp.today().normalize()
    T = max((pd.Timestamp(expiry_date) - today).days / 365.0, 1/365.0)

    rows = []
    for _, row in df.iterrows():
        K = row["strike"]
        mkt = _mid_price(row)
        yf_iv = row.get("impliedVolatility", np.nan)

        if pd.notna(yf_iv) and 0.08 < yf_iv < 5.0:
            iv = float(yf_iv)
        elif pd.notna(mkt) and mkt > 0:
            moneyness = K / S
            if 0.80 < moneyness < 1.20:
                iv = implied_vol(mkt, S, K, T, r, option_type)
            else:
                iv = np.nan
        else:
            iv = np.nan

        g = bs_greeks(S, K, T, r, iv, option_type) if pd.notna(iv) else \
            dict(delta=np.nan, gamma=np.nan, theta=np.nan, vega=np.nan, rho=np.nan)

        rows.append({**row.to_dict(), "mid": mkt, "T": T, "iv": iv, **g})

    result = pd.DataFrame(rows)

    # Track original IV before any patching
    result["_iv_original"] = result["iv"].copy()

    # Null out known bogus solver-fallback IVs
    result["iv"] = result["iv"].apply(
        lambda v: np.nan if (pd.notna(v) and _is_bogus_iv(v)) else v
    )

    # Interpolate genuinely missing IVs from valid neighbors
    result["iv"] = result["iv"].interpolate(method="linear", limit_direction="both")

    # Recompute Greeks for ALL rows where IV changed (not just NaN gamma)
    iv_changed = (
        (result["iv"] - result["_iv_original"]).abs() > 1e-6
    ) | (
        result["_iv_original"].isna() & result["iv"].notna()  # ← catches NaN→value
    )
    for idx in result[iv_changed].index:
        row = result.loc[idx]
        if pd.notna(row["iv"]):
            g = bs_greeks(S, row["strike"], T, r, row["iv"], option_type)
            for k, v in g.items():
                result.at[idx, k] = v

    result.drop(columns=["_iv_original"], inplace=True)
    return result


def enrich_chain(chain_data: dict, r: float = 0.045) -> dict:
    """
    Add IV + Greeks to every expiry in a chain_data dict (from data_fetcher).

    Returns the same structure with enriched DataFrames.
    """
    spot = chain_data["spot"]
    enriched_chains = {}

    for expiry, leg in chain_data["chains"].items():
        print(f"  Computing Greeks for expiry {expiry} ...", end="\r")
        calls = _enrich_df(leg["calls"], spot, expiry, r, "call")
        puts  = _enrich_df(leg["puts"],  spot, expiry, r, "put")
        enriched_chains[expiry] = {"calls": calls, "puts": puts}

    print(" " * 60, end="\r")  # clear progress line
    return {**chain_data, "chains": enriched_chains, "r": r}
