# Forecasting Spot Market Direction, Volatility, and Price Acceleration via Derivatives

## Markets

### Observation

Markets consist of:

- [Spot markets](https://en.wikipedia.org/wiki/Spot_market): direct asset trading  
- [Derivatives markets](https://en.wikipedia.org/wiki/Derivatives_market): contracts derived from the underlying  

Price is driven by:

$$
\text{Price Change} \propto \text{Spot Order Flow} + \text{Derivatives Hedging Flow}
$$

- Spot Order Flow: natural buying/selling  
- Hedging Flow: trading driven by options hedging  

Impact depends on scale:

| Derivatives vs Spot | Impact |
|---|---|
| Larger | Dominant |
| Similar | Significant |
| Smaller | Secondary |

---

## Core Mechanism

When traders buy options, market makers (MMs) take the opposite side.

- MMs accumulate **delta exposure**
- They hedge by trading the underlying asset

Typical behavior:

| Position | Price Up | Price Down |
|---|---|---|
| Short gamma | Buy → amplify | Sell → amplify |
| Long gamma | Sell → resist | Buy → resist |

→ **Hedging flows move the spot market**

As price moves:

- Delta changes  
- Hedging adjusts  
- Feedback loop forms  

→ Drives **volatility and acceleration**


## Delta Hedging ([Black-Scholes](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model))

The model assumes a perfectly hedged portfolio earns the risk-free rate:

$$
\dfrac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \dfrac{\partial^2 V}{\partial S^2} + rS \dfrac{\partial V}{\partial S} - rV = 0
$$

### Delta

$$
\Delta = \dfrac{\partial V}{\partial S}
$$

- Measures sensitivity to price  
- Interpreted as **share equivalent**

Example:

- $\Delta = 0.6$ → behaves like 0.6 shares  

### Delta Hedging

$$
\text{Hedge} = -\Delta
$$

- Short call (−Δ) → **buy shares**  
- Long call (+Δ) → **sell shares**

→ Keeps position **delta neutral**

### Gamma

$$
\Gamma = \dfrac{\partial^2 V}{\partial S^2} = \dfrac{\partial \Delta}{\partial S}
$$

- Measures how delta changes  
- Drives **hedging intensity**

| Gamma | Effect |
|---|---|
| Long | Mean-reverting, stable |
| Short | Trending, volatile |

## Forecasting with Delta & Gamma

- **Delta → direction**
- **Gamma → intensity**

| Delta | Gamma | Market Behavior |
|---|---|---|
| Short | High short | Strong uptrend, volatile |
| Long | High short | Strong downtrend, volatile |
| Any | High long | Slow, mean-reverting |
| Any | Low | Spot-driven |

## OpEx (Expiration Effects)

At expiration:

- Gamma disappears  
- Hedges are unwound  

Effects:

- Reduced hedging pressure  
- Regime shift  
- Possible reversals  

## Gamma Exposure (GEX)

### Definition

$$
\text{GEX} = \sum (\Gamma \times \text{Position Size} \times \text{Contract Multiplier})
$$

Measures how much **hedging must change** when price moves.

---

### Interpretation

| GEX | Behavior |
|---|---|
| Positive (long gamma) | Stable, mean-reverting |
| Negative (short gamma) | Trending, volatile |

---

### Gamma Flip

$$
\text{GEX} = 0
$$

- Boundary between regimes  
- Acts as support/resistance  

---

## Proposal: Effective Hedging Impact (EHI)

### Definition

$$
\text{EHI} = \sum_{i} \left( \Gamma_i \times \text{Size}_i \times \text{Multiplier}_i 
\times \dfrac{\text{Derivatives notional}}{\text{Market depth}} \right)
$$

EHI extends GEX by weighting hedging pressure against the market's capacity to
absorb it - the same gamma hits harder in a thin market than a deep one.

| EHI | Regime |
|---|---|
| Large positive | Long gamma — suppressed, mean-reverting |
| Near zero | Transitional — near gamma flip |
| Large negative | Short gamma — amplified, trending |

> **Note:** EHI is a proposed extension, not an established metric. Market depth
> is often approximated by average daily volume in practice.


## Key Insight

**Delta determines direction — Gamma determines acceleration**

In highly financialized markets:

**Hedging flows can dominate price movement**