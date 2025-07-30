# Fun: Love as a Dynamical System & Forecasting Relationships

## Love As A Dynamical System

Steven H. Strogatz first proposed a linear system in his book [Nonlinear Dynamics and Chaos: With Applications to Physics, Biology, Chemistry and Engineering](https://books.google.com.vn/books/about/Nonlinear_Dynamics_and_Chaos.html?id=1wrsEAAAQBAJ&source=kp_book_description&redir_esc=y):

$$
\begin{cases}
\dfrac{dR}{dt} = aJ \\
\dfrac{dJ}{dt} = -bR
\end{cases}
\quad \text{with } a, b > 0
$$

Here, $R$ and $J$ represent Romeo and Juliet, respectively.
- Unlike the classical play, in his version of the story (his own circumstance with his girl friend as he admitted), as Juliet's love increases, it accelerates Romeo's love: ($\dfrac{dR}{dt} = aJ$), but the opposite happens for Juliet ($\dfrac{dJ}{dt} = -bR$): as Romeo loves Juliet more, she pulls away from him.
- This system can lead to oscillatory or unstable behavior, depending on the parameters.

<img src="phases/RJ.png" alt="Cosmos MCP Screenshot 1" width="222">

A phase portrait of such system shows that this results in a never ending circle of love and hate between the pair, where they only love each other only 1/4 of the time (i.e. when both $R, J > 0$).

This is a fun example of modeling love as a dynamical system using differential equations. Such models can be extended or modified to represent more complex relationship dynamics.

## Generalization

We can consider the more general system:

$$
\begin{cases}
\dfrac{dR}{dt} = aR + bJ \\
\dfrac{dJ}{dt} = cR + dJ
\end{cases}
$$

This is a linear system with matrix form:

$$
\dfrac{d}{dt}
\begin{bmatrix}
R \\ J
\end{bmatrix}
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
\begin{bmatrix}
R \\ J
\end{bmatrix}
$$

The dynamics depend on the eigenvalues of the coefficient matrix:

$$
A = \begin{bmatrix}
a & b \\
c & d
\end{bmatrix}
$$

Spiral sinks/sources, nodes, saddles, or centers can all emerge, depending on:
  -	Trace: $\tau = a + d$
  -	Determinant: $\Delta = ad - bc$
  -	Discriminant: $\tau^2 - 4\Delta$

### Romantic Archetypes Based on Signs of $a$ and $b$

Consider Romeo’s equation:

$$
\dfrac{dR}{dt} = aR + bJ
$$

- $a > 0$: Romeo is self-encouraging—gets more excited by his own love.
- $a < 0$: Romeo is self-doubting—his own love overwhelms or discourages him.
-	$b > 0$: Romeo is reactive to Juliet’s love (positive feedback).
-	$b < 0$: He is repelled by Juliet’s attention (negative feedback).

Similarly for Juliet:

$$
\dfrac{dJ}{dt} = cR + dJ
$$

Same idea: signs of $c$ and $d$ define her archetype.

**General archetypes can be summarized in this table:**

| name | $a$ or $d$ | $b$ or $c$ | description |
|---|---|---|---|
| Eager Beaver | > 0 | > 0 | Reponds strongly to other's affection and their own feelings. Explosive lover. |
| Cautious Lover | < 0 | > 0 | Encouraged by other's love but represses their own feelings. |
| Hermit | < 0 | < 0 | Withdraws from both their own and other's feelings. |
| Contrarian | > 0 | < 0 | Gains confidence when other ignores them. |

<!-- ## Phase Portraits

What happens if the pair gets together ? -->

<!-- <img src="phases/identical-pairs.png" alt="Identical pairs" width="555">

<img src="phases/mixed-pairs.png" alt="Mixed pairs" width="555"> -->

## Extensions

### 1. Rhett and Scarlett - Gone with the Wind
[Rinaldi et al. (2013) in their essay: *A mathematical model of "Gone with the Wind"*](https://www.researchgate.net/publication/257219064_A_mathematical_model_of_Gone_with_the_Wind) proposed a model on the love story between Scarlett O'Hara and Rhett Butler from "Gone with the Wind":

$$
\begin{cases}
\dfrac{dx_1(t)}{dt} = -\alpha_1x_1(t) + \rho_1A_2 + R_1(x_2) \\
\dfrac{dx_2(t)}{dt} = -\alpha_2x_2(t) + \rho_2A_1 + R_2(x_1)
\end{cases}
$$

where:

$$
A_i = \sum_{h}\lambda^h_jA^h_i
$$

This is the appeal of an individual $i$ to individual $j$. It can be composed of various components $A^h_i$ such as physical attractiveness, intelligence etc. which are independent on the feeling $x_i$ for the partner. 

This is perceived by individual $j$ as shown by the coefficient $\lambda^h_j$.

Then we have:

$$
R_i(x_j) = k_ix_jexp(-x_j/\beta_i)
$$

This show that the lover's reactions first increase with the love of the partner and then decrease. Individuals of this kind are called insecure, or, sometimes, refusers, because they react less and less strongly when the love of the partner exceeds a certain threshold. 

This can be simplified and understood as:

$$
\begin{cases}
\dot{R} = -R + AS + kSe^{-S} \\
\dot{S} = -S + AR + kRe^{-R}
\end{cases}
$$

where:

- $R$: Rhett's love for Scarlett.
- $S$: Scarlett's love for Rhett.

The equations shows that:
- Both Rhett and Scarlett are cautious lovers, as shown by the terms $-R$ and $-S$. The more Scarlett loves, the more she pulls back and the more Rhett loves, the more he pulls back.
- The exponential terms $kSe^{-S}$ and $kSe^{-R}$ describe how the lovers react to each other. The negative exponents cause the function to have a maximum i.e. when Scarlett loves Rhett to a certain level, the love begins to have less effect on him and vice versa.
- In this regard, we can see the terms $AR$ and $AS$ as the minimum amount of love that one will always have for the other. 

### 2. Darcy and Elizabeth - Pride and Prejudice

Again, [Rinaldi et al. (2014) in the essay: *A Mathematical Model of "Pride and Prejudice"*](https://www.researchgate.net/publication/260373742_A_Mathematical_Model_of_Pride_and_Prejudice) further extends this model to introduce "lover's memories":

$$
\begin{cases}
\dfrac{dx_1(t)}{dt} = -\alpha_1x_1(t) + \rho_1A_2 + R_1(x_2) \\
\dfrac{dx_2(t)}{dt} = -\alpha_2x_2(t) + \rho_2A_1 + R_2(x_1)
\end{cases}
$$

where $\dot{x_1}$ represents Darcy's love for Elizabeth as it progresses over time and $\dot{x_2}$ represents Elizabeth's love for Darcy as it progresses over time.

This is similar to the model introduced to describe Scarlett and Rhett from *"Gone with the Wind"* where:

$$
A_i = \sum_{h}\lambda^h_jA^h_i
$$

describes the attractiveness (appeal) of individual $i$ to individual $j$. It's not an absolute character of the individual, but rather a value perceived by his/her partner. As such, the appeal $A_i$ of individual $i$ varies discontinuously each time the partner $j$ discovers some relevant hidden aspect of the character of $i$.

The difference this time is in the terms $R_1(x_2)$ and $R_2(x_1)$ where they are described as:

$$
R_{1}(x_2) = \dfrac{e^{x_2} - e^{-x_2}}{e^{x_2} / R^{+}_{1} - e^{-x_2} / R^{-}_{1}}
$$

$$
R_{2}(x_1) = \dfrac{e^{x_1} - e^{-x_1}}{e^{x_1} / R^{+}_{2} - e^{-x_1} / R^{-}_{2}}
$$

with:
- $R^{+}_{1} = 2$
- $R^{+}_{2} = 1$
- $R^{-}_{1} = R^{-}_{2} = -1$

This reflects the most standard individuals, often called secure. They are those who like to be loved. An individual $i$ belonging to this class is formally characterized by an increasing function $R_i(x_j)$ that identifies the flow of interest generated in individual $i$ by the love $x_j$ of the partner.

The authors do not explain why these values
were chosen, but it is likely that $R^{+}_{1}$ and $R^{+}_{2}$ signify how lovers respond to positive love from the other. From the story, Darcy reacts more positively to Elizabeth's love compare to Elizabeth's somewhat "more chill" attitude.

In the same way $R^{-}_{1}$ and $R^{-}_{2}$ represent how the characters respond when the other is disinterested.

Finally, the coefficient $\alpha$ indicates the rate of which individuals lose memories of their partner after separating. The authors set:

$$
\alpha_{1} = 0.1
$$

$$
\alpha_{2} = 0.3
$$

This reflects the story where Elizabeth's initial negative impression of Darcy was forgotten and later allowed her affection to increase.

So the system for Darcy and Elizabeth is:

$$
\begin{cases}
\dot{D} = -\alpha_{D} D + \rho_{D} A_{E} + \dfrac{e^{E} - e^{-E}}{e^{E} / R^{+}_{D} - e^{-E} / R^{-}_{D}} \\
\dot{E} = -\alpha_{E} E + \rho_{E} A_{D} + \dfrac{e^{D} - e^{-D}}{e^{D} / R^{+}_{E} - e^{-D} / R^{-}_{E}}
\end{cases}
$$

where:
- $\alpha$: forgetting coefficient, indicating the rate of which individuals lose memories of their partner after separating.
- $A_{E}$: Elizabeth's appeal to Darcy.
- $A_{D}$: Darcy's appeal to Elizabeth.
- $\rho_{D}$: sensitivity of Darcy character to the appeal of Elizabeth.
- $\rho_{E}$: sensitivity of Elizabeth character to the appeal of Darcy.
- $D$: Darcy's love for Elizabeth.
- $E$: Elizabeth's love for Darcy.


with values:

- $\alpha_{D} = 0.1$
- $\alpha_{E} = 0.3$
- $R^{+}_{D} = 1$
- $R^{+}_{E} = 2$
- $R^{-}_{D} = R^{-}_{E} = -1$