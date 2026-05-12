# Helpful: Forecasting Spot Market Direction, Volatility, and Price Acceleration via Derivatives Markets

## Markets

### Observation

Modern markets usually consist of:

- [Spot markets](https://en.wikipedia.org/wiki/Spot_market), where the underlying asset is directly traded  
- [Derivatives markets](https://en.wikipedia.org/wiki/Derivatives_market), where contracts derive value from the underlying  

Price changes are mainly driven by order flow in the spot market (buying and selling). However, this flow comes from two main sources:

- Direct trading activity (investors, institutions)  
- Hedging activity caused by derivatives positions  

We can think of derivatives as influencing spot market behavior through hedging flows.

A simple way to think about it:

$$
\text{Price Change} \propto \text{Net Spot Order Flow} + \text{Hedging Flow from Derivatives}
$$

Where:
- Net Spot Order Flow: normal buying and selling  
- Hedging Flow from Derivatives: buying/selling caused by options hedging  

There are three cases where derivatives hedging influences the spot price, depending on the relative size of each market:


| Spot liquidity vs. Derivatives notional | Derivatives Hedge Role |
|---|---|
| Derivatives > Spot | Dominant - hedging flows can strongly drive price |
| Roughly equivalent | Significant - hedging flows bias price |
| Spot > Derivatives | Secondary - hedging flows nudge price |

### Logic

When traders buy call options, someone must take the opposite side of the trade. This counterparty is often a market maker (MM). If many traders buy calls, market makers will typically be net sellers - accumulating short call exposure.

Because of this, market makers carry delta exposure: their position becomes sensitive to price changes, as opposed to [delta neutral](https://en.wikipedia.org/wiki/Delta_neutral). To manage this risk, they hedge by trading the underlying asset.

In many common cases when MMs are short calls:

- If price goes up, they tend to buy more  
- If price goes down, they tend to sell  

And when MMs are long calls:

- If price goes up, they tend to sell
- If price goes down, they tend to buy more

This feedback effect comes from how delta changes as price moves. As a result, **derivatives indirectly move the spot price** through hedging flows. As price changes, delta also changes, forcing market makers to continuously rebalance their hedges - a key driver of short-term volatility and price acceleration.

At option expiration (OpEx), hedging pressure often changes regime rather than simply stopping.

As options expire, the associated gamma exposure disappears. Market makers no longer need to maintain the same hedges, and may unwind their positions in the underlying asset.

This can lead to:

- Reduced hedging pressure  
- A shift in market dynamics  
- In some cases, a reversal or acceleration of price trends  

Once the gamma "anchor" is removed, the spot market is less constrained by hedging flows and more driven by organic order flow.

To understand how market makers calculate and manage this exposure, we need to understand delta, delta hedging and gamma formally.

## Delta Hedging ([Black-Scholes Model](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model#))

The [Black-Scholes equation](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model#Black%E2%80%93Scholes_equation) states that a perfectly hedged portfolio, constructed by continuously buying and selling the underlying asset to offset option exposure, must grow at the risk-free rate. This eliminates arbitrage and defines the fair price of an option. It is the foundational model upon which most modern hedging strategies are built:

$$
\dfrac{\partial V}{\partial t} + \dfrac{1}{2}\sigma^2S^2 \dfrac{\partial^2V}{\partial S^2} + rS \dfrac{\partial V}{\partial S} - rV = 0
$$

where:
- $V$: The option price
- $S$: The underlying asset's price
- $t$: Time
- $\sigma$: Volatility of the underlying asset (standard deviation of returns)
- $r$: Risk-free interest rate

Each term has a financial interpretation:

| PDE Term | Greek | Scaling Factor | Meaning |
|---|---|---|---|
| $\dfrac{\partial V}{\partial t}$ | Theta $(\Theta)$ | none | Time decay of option value |
| $\dfrac{1}{2}\sigma^2S^2\Gamma$ | Gamma $(\Gamma)$ | $\dfrac{1}{2}\sigma^2S^2$ | Rebalancing P&L, scaled by volatility and price |
| $rS\Delta$ | Delta $(\Delta)$ | $rS$ | Financing cost of the delta hedge, scaled by rate and price |
| $rV$ | - | $r$ | Risk-free discounting of the option's value |

The equation states that these four effects must sum to zero for an arbitrage-free, perfectly hedged portfolio.

### [Delta](https://en.wikipedia.org/wiki/Greeks_(finance)#Delta)

Delta measures the rate of change of an option's price relative to the underlying asset's price:

$$
\Delta = \dfrac{\partial V}{\partial S}
$$

where:
- $V$: The option price  
- $S$: The underlying asset's price  

It tells us how much the option price changes when the stock price moves by 1 unit.

**Example**: suppose $\Delta = 0.6$:

- Stock goes up $1: option goes up ~$0.6  
- Stock goes down $1: option goes down ~$0.6  

The option behaves like holding 0.6 shares of stock.

- If a trader **buys** the call: their delta = **+0.6**  
- If a market maker **sells** the call: their delta = **-0.6**  

The market maker carries a delta of **-0.6**, meaning they lose when price rises and gain when it falls.

### [Delta Hedging](https://en.wikipedia.org/wiki/Hedge_(finance)#Delta_hedging)

To become delta neutral, a market maker must offset their position delta:

$$
\text{Hedge} = -(\text{Position Delta})
$$

Using the same example where $\Delta = 0.6$:

|  | MM is short calls | MM is long calls |
|---|---|---|
| Option delta | +0.6 | +0.6 |
| MM position delta | −0.6 | +0.6 |
| To hedge | Buy 0.6 shares | Sell 0.6 shares |
| Result | Options = -0.6<br>Stock = +0.6<br>**Total = 0** (delta neutral) | Options = +0.6<br>Stock = −0.6<br>**Total = 0** (delta neutral) |

### [Gamma](https://en.wikipedia.org/wiki/Greeks_(finance)#Gamma)

Gamma measures how much delta changes as price moves.
It is:
- The second derivative of option price with respect to asset price, and equivalently,
- The first derivative of delta with respect to asset price.

$$
\Gamma = \dfrac{\partial^2V}{\partial S^2} = \dfrac{\partial\Delta}{\partial S}
$$

There are several cases considering MM's gamma:

|  | Long Gamma (MM bought options) | Short Gamma (MM sold options) |
|---|---|---|
| Price rises | MM sells → move resisted | MM buys → move accelerates |
| Price falls | MM buys → move resisted | MM sells → move accelerates |
| Market character | Range-bound, mean-reverting | Trending, volatile, reflexive |
| Volatility effect | Suppressed | Amplified |
| Analogy | Shock absorber | Turbocharger |

Intuitively:

- A high, short gamma means delta changes rapidly as price moves, hence MM must rebalance frequently. This leads to volatility amplified through hedging flows - as MM are forced to make large, rapid hedge adjustments as price moves.

- A high, long gamma means delta changes rapidly as price moves, but MM hedging is counter-trend: they sell into rises and buy into falls. This suppresses volatility, as hedging flows absorb moves rather than amplify them, creating a gravitational pull toward the strike price.

- A low gamma, whether long or short, means delta is stable and hedging flows are small and infrequent - the amplifying or suppressing effects above are weak, and price is driven more by spot order flow than by hedging.

## Delta and Gamma as Forecasting Indicators

Understanding the role of delta and gamma in MM hedging allows us to estimate the likely direction of spot price movement and the potential for volatility, before it happens.

The two indicators work on different dimensions:

- **Delta exposure** tells us the **direction** of hedging pressure (are MMs net buyers or sellers as price moves?)

- **Gamma exposure** tells us the **intensity** of that pressure (how large and frequent will hedge rebalancing be?)

Together they define the hedging regime the market is currently in:

| Delta | Gamma | Implied Regime |
|---|---|---|
| Net negative (MMs short delta) | High, short | Strong trending up, high volatility |
| Net positive (MMs long delta) | High, short | Strong trending down, high volatility |
| Net negative (MMs short delta) | High, long | Upward pressure, but dampened - slow grind |
| Net positive (MMs long delta) | High, long | Downward pressure, but dampened - slow grind |
| Any | Low | Spot-driven - derivatives influence weak |

A key concept that follows from this is the **gamma flip level**: the price at which aggregate market gamma crosses from positive to negative (or vice versa), changing the hedging regime entirely. These levels often act as critical support/resistance zones in the spot market.

## Calculating Delta and Gamma from Market Data

In practice, delta and gamma are never calculated manually. They are computed 
continuously by exchanges and data providers, and are readable directly as 
columns in any options chain.

However, understanding where these numbers come from is useful for interpreting 
them correctly.

### From Market Price to Delta and Gamma

Given:

- $S$: Current stock price
- $K$: Strike price
- $T$: Time to expiration (in years)
- $r$: Risk-free rate
- $\sigma_{IV}$: Volatility of the underlying asset (market implied)
- $N(d)$: [Cumulative distribution function (CDF)](https://en.wikipedia.org/wiki/Cumulative_distribution_function) of the standard normal distribution
- $N'(d)$: [Probability density function (PDF)](https://en.wikipedia.org/wiki/Probability_density_function) of the standard normal distribution

**Option Delta Calculation**

For Call options:

$$
\Delta = N(d_1)
$$

For Put options:

$$
\Delta = N(d_1) - 1
$$

Where:

$$
d_1 = \dfrac{\ln\left(\dfrac{S}{K}\right) + \left( r + \dfrac{\sigma_{IV}^2}{2}\right)T}{\sigma_{IV}\sqrt{T}}
$$

**Option Gamma Calculation**

$$
\Gamma = \dfrac{N'(d_1)}{S\sigma_{IV}\sqrt{T}}
$$

### Concrete Example

Suppose:

- $S$ = $105
- $K$ = $115
- $T$ = 30 days = 30/365 = 0.0822 years
- $r$ = 5% = 0.05
- $\sigma_{IV}$ = 20% = 0.20

This is a slightly out-of-the-money call option.

Step 1: calculate $d_1$

$$
\begin{equation}
\begin{split}
d_1 &= \dfrac{\ln\left(\dfrac{S}{K}\right) + \left( r + \dfrac{\sigma_{IV}^2}{2}\right)T}{\sigma_{IV}\sqrt{T}} \\
    &= \dfrac{\ln\left(\dfrac{105}{115}\right) + \left( 0.05 + \dfrac{0.2^2}{2}\right)0.0822}{0.2\sqrt{0.0822}} \\
    &= \dfrac{-0.0909 + 0.07 \cdot 0.0822}{0.2867} \\
    &= -0.297
\end{split}
\end{equation}
$$

Step 2: calculate $\Delta$

$$
\Delta = N(d_1) = N(-0.297)
$$

Looking up the cumulative normal distribution:

$$
N(-0.297) \approx 0.3834
$$

Step 3: Calculate $\Gamma$

$$
\begin{equation}
\begin{split}
\Gamma &= \dfrac{N'(d_1)}{S\sigma_{IV}\sqrt{T}} \\
       &= \dfrac{N'(-0.297)}{105 \cdot 0.2 \cdot \sqrt{0.0822}} \\
       &= \dfrac{N'(-0.297)}{6.02081389847} \\ \\ \\
% \text{The standard normal PDF at } d_1 = −0.297: \\
N'(d_1) &= \dfrac{1}{\sqrt{2\pi}}e^{-\dfrac{(d_1)^2}{2}} \\
        &= \dfrac{1}{\sqrt{2\pi}}e^{-\dfrac{(−0.297)^2}{2}} \\
        &= 0.3989 \cdot e^{-0.0441045} \\
        &= 0.3989 \cdot 0.9568 \\
        &= 0.3817 \\ \\ \\
\Gamma &= \dfrac{0.3817}{6.0208} = 0.0634
\end{split}
\end{equation}
$$

## Regime Changes and Option Expiration (OpEx)

The hedging regimes described above are not static. They shift continuously as 
options are repriced, new positions are opened, and existing ones expire.

### Gamma Decay and Expiration

Gamma is not constant over the life of an option. As expiration approaches, 
gamma becomes increasingly concentrated around the strike price, small price 
moves near the strike cause large, rapid delta changes, forcing aggressive 
rebalancing by MMs.

At expiration, this gamma exposure disappears entirely. Options either expire 
worthless or are exercised, and the associated hedges are unwound.

This creates a predictable pattern around OpEx dates:

- **Pre-expiry**: gamma exposure is highest, hedging flows are most intense
- **At expiry**: gamma from that expiration drops to zero, reducing hedging pressure
- **Post-expiry**: spot market transitions back toward organic order flow

### Hedging Unwind

When options expire, MMs no longer need to maintain the delta hedges associated 
with those positions. They unwind by trading the underlying asset in the 
opposite direction of their hedge:

- A MM who was long shares to hedge a short call → sells those shares at expiry
- A MM who was short shares to hedge a long call → buys those shares back

This unwind activity can itself move the spot price, particularly when a large 
concentration of options expires at the same strike.

### Regime Shift at OpEx

The removal of gamma exposure changes the hedging regime entirely:

| Before OpEx | After OpEx |
|---|---|
| Price pinned near high open interest strikes | Price free to move away from strikes |
| Volatility suppressed or amplified by hedging | Volatility driven by organic order flow |
| MM hedging flows dominant | Spot order flow dominant |
| Gamma flip levels act as support/resistance | Those levels lose relevance |

This is why large OpEx dates - particularly monthly and quarterly expirations - 
are closely watched as potential inflection points. The expiry of a dominant 
gamma regime often marks the beginning of a new directional move or volatility 
expansion.

### Implication for Forecasting

Because gamma exposure shifts continuously and resets at each expiration, 
forecasting via derivatives requires monitoring aggregate gamma in real time 
rather than as a static snapshot. This is precisely what Gamma Exposure (GEX) 
measures - covered in the next section.

## Forecasting via Gamma Exposure (GEX) Indicator

### Gamma Exposure (GEX)

Gamma Exposure (GEX) measures the **aggregate gamma positioning** of market participants (primarily market makers) across all option strikes and expirations.

It is typically computed as:

$$
\text{GEX} = \sum (\Gamma \times \text{Position Size} \times \text{Contract Multiplier})
$$

Where:
- $\Gamma$: Option gamma  
- Position Size: Open interest (or estimated positioning)  
- Contract Multiplier: e.g. 100 shares per contract  

GEX represents how sensitive the market maker’s **total delta exposure** is to changes in the underlying price.

### Aggregate GEX Interpretation

|  | Positive GEX (Long Gamma) | Negative GEX (Short Gamma) |
|---|---|---|
| MM position | Long gamma | Short gamma |
| Hedging Direction | Counter-trend | Pro-trend |
| Price | Pinned near key levels | Price moves amplified |
| Volatility effect | Suppressed | Amplified |
| Market | Mean-revert | Trends strongly |

### Gamma Flip Level

The **gamma flip level** is the price at which:

$$
\text{Total GEX} = 0
$$

At this level:
- Market transitions stable to volatile and vice versa.
- It acts as support/resistance and regime boundary for volatility.

### Practical Use

GEX is used to:

- Identify volatility regimes  
- Detect potential breakout conditions  
- Locate price pinning levels  
- Anticipate hedging-driven flows  

In highly financialized markets, GEX can become a **dominant driver of short-term price dynamics**.