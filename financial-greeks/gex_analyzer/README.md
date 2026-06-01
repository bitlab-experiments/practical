# GEX / EHI Analyzer

A Python toolkit that computes **Gamma Exposure (GEX)** and **Effective Hedging Impact (EHI)** from live options data via `yfinance`, and charts the results against spot price history.

EHI scales raw GEX by how large the options market is relative to spot liquidity — see the [parent README](../README.md#a-simple-proposal-effective-hedging-impact-ehi) for the full theoretical motivation.

---

## What It Does

| Step | Module | Description |
|------|--------|-------------|
| 1 | `data_fetcher.py` | Spot OHLCV history + full options chain (`yfinance`) |
| 2 | `greeks.py` | IV solver (Brent) + Black–Scholes Greeks |
| 3 | `gex.py` | Per-strike GEX, net GEX, flip point, EHI scaling, regimes |
| 4 | `main.py` | CLI pipeline + matplotlib charts |
| 5 | `demo.py` | Synthetic data demo (no network) |

The live pipeline calls **`ehi_summary()`**, which computes GEX first, then applies the liquidity scale. GEX-only helpers (`gex_summary`, `compute_gex`) remain available for scripts and backtests.

---

## Quick Start

```bash
pip install -r requirements.txt

# Demo on synthetic data (no network)
python demo.py

# Live analysis — SPY
python main.py --asset spy

# Gold ETF, 6-month spot history
python main.py --asset gold --period 6mo

# Individual stock
python main.py --asset AAPL --period 1y

# Oil ETF, 90-day expiry window for GEX/EHI
python main.py --asset USO --max-expiry-days 90
```

Charts are written under `calculations/` with a UTC timestamp in the filename, e.g.  
`calculations/spy_gex_2026-06-01-08-42-43-UTC.png`.  
Each image also shows `Generated: YYYY-MM-DD HH:MM:SS UTC` in the bottom-right corner.

---

## CLI Output

After a run, the console reports:

| Field | Meaning |
|-------|---------|
| **NET GEX** | Total net gamma exposure (billions USD, $B) |
| **NET EHI** | `NET GEX × (derivatives notional / spot depth)` |
| **scale** | `derivatives_notional / spot_market_depth` (dimensionless) |
| **NOTIONAL** | Σ(OI × 100 × spot) over expiries ≤ `max_expiry_days` |
| **ADV DEPTH** | 20-day average daily dollar volume (`Volume × Close`) |
| **0DTE / WEEKLY / MONTHLY** | GEX and EHI broken down by expiry bucket |
| **FLIP PT** | Strike where cumulative GEX crosses zero (unchanged by EHI scale) |
| **GEX REG / EHI REG** | Regime labels (see below) |

Top-strike table is sorted by **|net EHI|** per strike.

---

## Data Sources (all free)

| Data | Source | Notes |
|------|--------|-------|
| Spot OHLCV | `yfinance` | ETFs, stocks; used for ADV depth proxy |
| Options chain | `yfinance` | Calls + puts, OI, bid/ask, volume |
| IV (if missing) | Computed | Brent inversion of Black–Scholes |
| Risk-free rate | `^IRX` | 13-week T-bill; fallback 4.5% |

**Supported assets (friendly names):**

| Name | Ticker |
|------|--------|
| `sp500` | SPY |
| `gold` | GLD |
| `oil` | USO |
| `vix` | ^VIX |
| Any US ticker | Pass through uppercase, e.g. `AAPL` |

Run during **market hours** when possible: if open interest is zero, the code uses **20% of daily volume** as an OI proxy (same rule for GEX and notional).

---

## Theory

### Implied Volatility

When `impliedVolatility` from `yfinance` is missing or unreliable, IV is solved by inverting Black–Scholes with Brent’s method on `[0.001, 20.0]`.

### Black–Scholes Greeks

```
d1 = [ln(S/K) + (r + σ²/2)·T] / (σ·√T)
d2 = d1 − σ·√T

Gamma = φ(d1) / (S·σ·√T)     (same for calls and puts)
```

### GEX per strike

Dealers are assumed **long calls** and **short puts**:

```
GEX_call(K) = Γ × OI_call × 100 × S² / 1e9     (+, in $B)
GEX_put(K)  = Γ × OI_put  × 100 × S² / 1e9     (−)
Net_GEX(K)  = GEX_call(K) − GEX_put(K)

Net GEX = Σ_K Net_GEX(K)
```

Only expiries with **0 ≤ DTE ≤ max_expiry_days** (default 60) are included. Strikes with zero gamma are skipped.

### EHI (Effective Hedging Impact)

```
Derivatives notional = Σ (OI_i × 100 × S)     over same expiry window as GEX
Spot market depth    = mean(Volume × Close)   over last 20 trading days
Scale                = Derivatives notional / Spot market depth

Net EHI              = Net GEX × Scale
EHI per strike       = Net_GEX(K) × Scale     (columns: net_ehi_strike, call_ehi, put_ehi)
```

EHI uses the **same OI and expiry filters** as GEX so the ratio is consistent. The flip strike is computed from unscaled GEX (scaling is a positive constant, so the flip level does not move).

> **Note:** EHI is a proposed extension documented in the parent README, not an industry-standard published metric. ADV is a coarse proxy for true order-book depth.

### Regime labels

**GEX** (`gex_summary`):

| Net GEX | Label |
|---------|--------|
| > +0.5 $B | positive — vol suppression likely |
| < −0.5 $B | negative — vol amplification likely |
| otherwise | neutral / near flip — regime uncertain |

**EHI** (`ehi_regime`): same wording, with a band `max(0.01, 0.15 × |net EHI|)` around zero for the transitional zone.

---

## Charts

Three-panel dark-theme figure:

1. **Spot price history** — with current spot and GEX flip level (if found)
2. **Net EHI by strike** — green / red bars by sign
3. **Call vs put open interest** — thousands of contracts

Title shows **GEX ($B)**, **net EHI**, and **EHI regime**.

---

## Programmatic API

```python
from data_fetcher import fetch_spot_history, fetch_options_chain, get_risk_free_rate
from greeks import enrich_chain
from gex import ehi_summary, gex_summary, compute_gex, gex_vs_realized, regime_stats

spot_hist = fetch_spot_history("spy", period="1y")
chain = fetch_options_chain("spy")
enriched = enrich_chain(chain, r=get_risk_free_rate())

summary = ehi_summary(enriched, spot_hist, max_expiry_days=60)
print(summary["net_gex"], summary["net_ehi"], summary["ehi_scale"])
print(summary["ehi_df"][["strike", "net_ehi_strike"]].head())

# GEX-only (no liquidity scale)
gex_only = gex_summary(enriched, max_expiry_days=60)

# Historical regime study (requires a time series of daily net GEX)
# result = gex_vs_realized(spot_hist, gex_series, forward_days=1)
# print(regime_stats(result))
```

### `ehi_summary` return keys

| Key | Type | Description |
|-----|------|-------------|
| `spot` | float | Live spot from chain |
| `net_gex` | float | Total GEX ($B) |
| `net_ehi` | float | Scaled EHI |
| `ehi_scale` | float | Notional / depth |
| `derivatives_notional` | float | USD |
| `spot_market_depth` | float | USD (ADV proxy) |
| `adv_lookback` | int | Days for ADV (default 20) |
| `flip_point` | float \| None | GEX flip strike |
| `regime` | str | GEX regime |
| `ehi_regime` | str | EHI regime |
| `gex_df` | DataFrame | Per-strike GEX ($B) |
| `ehi_df` | DataFrame | Per-strike EHI (`net_ehi_strike`, …) |

---

## Project Structure

```
gex_analyzer/
├── data_fetcher.py   # yfinance: spot, options, risk-free rate
├── greeks.py         # IV solver + Black–Scholes Greeks
├── gex.py            # GEX, EHI, flip point, expiry buckets
├── main.py           # CLI + charts → calculations/
├── demo.py           # Synthetic demo
├── calculations/     # Timestamped PNG outputs (gitignored optional)
└── requirements.txt
```

---

## Extending the Project

### Historical EHI / GEX backtesting

Store daily EOD options snapshots → call `ehi_summary` or `gex_summary` per day → compare `net_ehi` / `net_gex` to forward realized vol via `gex_vs_realized`.

### Add Deribit (crypto)

```python
import requests
r = requests.get(
    "https://www.deribit.com/api/v2/public/get_book_summary_by_currency",
    params={"currency": "BTC", "kind": "option"},
)
```

### Paid data upgrades

- **Tradier** — pre-computed Greeks  
- **CBOE DataShop** — official index options history  
- **Polygon.io** — real-time options with Greeks  
