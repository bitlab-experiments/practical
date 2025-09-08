# Fun: Make better informed decisions when picking lottery numbers and why you should ignore your intuition

Consider a lottery game where participants pick 6 numbers out of 49 and assume that all numbers are uniformly distributed.


The total number of ways to choose 6 numbers out of 49 (if order matters) is defined by the [permutation formula](https://en.wikipedia.org/wiki/Permutation#k-permutations_of_n):

$$
P(n,k) = \dfrac{n!}{(n-k)!}
$$

The total number of ways to choose 6 numbers out of 49 (disregard ordering) is defined by the [combination formula](https://en.wikipedia.org/wiki/Combination):

$$
C(n,k) = {n \choose k} = \dfrac{P(n,k)}{k!} = \dfrac{n!}{k!(n - k)!}
$$

with $n = 49$, $k = 6$ we have:

$$
C(49, 6) = {49 \choose 6} = \dfrac{49!}{6!(49 - 6)!} = 13,983,816
$$

And so the chance that a ticket contains the right combination is:

$$
P(win) = \dfrac{1}{13,983,816} = 0.000000071511238 = 0.000007151124 \\% \approx 0 \\%
$$

Intuitively, we may tend to pick spread out numbers, covering a wide range.

e.g. 

$$
\lbrace 5, 12, 27, 35, 40, 43 \rbrace
$$

or:

$$
\lbrace 7, 12, 27, 35, 45, 48 \rbrace
$$

Those choices may feel natural, but they don’t actually improve your chance of winning.
While all tickets have the same chance of winning, choosing “non-intuitive” or unusual numbers may reduce the likelihood of splitting the prize with other winners. That’s the only way to make a practical improvement.

But how do we avoid picking numbers intuitively ? What patterns can we follow ?

## 1. High probability of one or more pairs of consecutive numbers

[Empirical data](data/data.txt) shows that pairs of consecutive numbers (e.g. 10 and 11, 36 and 37 etc.) frequently appear in drawn results.

So what is the probability of at least a pair of consecutive numbers show up from all the combinations?

And what is the probability of exactly one pair of consecutive numbers show up ?

If we can answer these questions, we can also answer what the probability of 2 pairs or more of consecutive numbers show up is:

$$
P(pairs \ge 2) = P(pairs \ge 1) - P(pairs = 1)
$$

[K Drakakis - A note on the appearance of consecutive numbers amongst the set of winning numbers in Lottery (2007)](https://www.researchgate.net/publication/228727998_A_note_on_the_appearance_of_consecutive_numbers_amongst_the_set_of_winning_numbers_in_Lottery) studied this and concluded that the winning 6 numbers (out of 49) contain 2 consecutive numbers with a surprisingly high probability (almost 50%).

### 1.1. Probability of one or more pairs of consecutive numbers in a result

Since it is hard to calculate the probability of at least one pair of consecutive numbers in a result, we can calculate the probability of no pair of consecutive numbers in a result instead, and subtract it from 1 to get the result.

Imagine that we have a horizontal line with 49 points on it, each represents a number in our game.

`1-2-3-4-5-6-7-8-9-10-11-12-13-14-15-16-17...49`

We want to pick 6 numbers and none of them is next to each other:

`p-2-p-4-p-6-p-8-p-10-p-12-13-14-15-16-17...49`

That means there must be a gap $g$ after each pick for each number. This gap must have its value of at least one space:

$$
g \ge 1
$$

We pick 6 numbers so the gap can be:

$$
g \ge k \implies g \ge 6
$$

However, notice that the last number that we pick doesn't have to have a gap after it (since there will be no other number to be picked anymore), so the gap must be:

$$
g \ge k - 1 \implies g \ge 5
$$

In general, g as the minimum gap can be defined as:

$$
g = k - 1
$$

So picking 6 non-consecutive numbers can be thought of as picking 6 points out of the line but the line is reduced by the minimum gap:

$$
n_{gap} = n - g = 49 - 5 = 44 
$$

So the total number of ways to pick 6 non-consecutive numbers out of 49 is:

$$
n_p = {n - g \choose k} = {n - k + 1 \choose k} = {44 \choose 6}
$$


The probability of at least one pair of consecutive numbers shows up in a result is:

$$
\begin{equation}
\begin{split}
P(pairs \ge 1) &= 1 - \dfrac{{n - k + 1 \choose k}}{{n \choose k}} \\
&=  1 - \dfrac{{44 \choose 6}}{{49 \choose 6}} \\
&= 1 - \dfrac{7,059,052}{13,983,816} \\
&= \dfrac{6,924,764}{13,983,816} \\
&= 0.4951984494 \approx 49.52 \\% \nonumber
\end{split}
\end{equation}
$$

### 1.2. The probability of exactly 1 pair of consecutive numbers in a result

To imagine picking up exactly 1 pair of consecutive numbers, we can think of the picks as containing one block (2 consecutive numbers), and other 4 non-consecutive numbers.

`p-p-3-p-5-p-6-p-8-p-10-11-12-13-14-15-16-17...49`

So it would be starting with a consecutive pair as a block, then add 4 more non-consecutive numbers around it.

There are 48 possible consecutive pairs i.e. 1-2, 2-3, ... 48-49. They can be splitted on 2 cases:
1. Edge case: with consecutive pair {1, 2} or {48, 49}.
2. General case: all other consecutive pairs.

For all cases, we choose a consecutive pair:

$$
pair = \lbrace m, m + 1 \rbrace
$$

#### 1.2.1. Edge case

In the edge case, if the pair is {1, 2} we'll ignore number 3, if the pair is {48, 49}, we'll ignore number 47.

So to pick 4 non-consecutive numbers, the length of the line now would be:

$$
n' = n - 3 = 49 - 3 = 46
$$

And the total combinations of each of the case is:

$$
n'_p = {n' - k' + 1 \choose k'} = {46 - 4 + 1 \choose 4} = {43 \choose 4} = 123,410
$$

And the total combinations for both edge case is:

$$
n_{pe} = 123,410 \times 2 = 246,820
$$

#### 1.2.2. General case

In the general case, we can pick:

$$
pair = \lbrace m, m + 1 \rbrace
$$

where 

$$
2 \le m \le 47
$$

In this case, we would exclude 2 numbers immediately before and after the pair's value:

$$
exclude = \lbrace m - 1, m + 2 \rbrace
$$

E.g. for pair {6, 7} we would exclude 5 and 8.

And so to pick 4 non-consecutive numbers, the length of the line now would be:

$$
n' = n - 4 = 49 - 4 = 45
$$

And the total combinations of each of the case is:

$$
n'_p = {n' - k' + 1 \choose k'} = {45 - 4 + 1 \choose 4} = {42 \choose 4} = 111,930
$$

There are 46 possible consecutive pairs in this case, so the total number of combinations is:

$$
n_{pg} = 46 \times 111,930 = 5,148,780
$$

#### 1.2.3. Total combinations and probability

The total number of combinations of 2 cases is:

$$
n_{pa} = n_{pe} + n_{pg} = 246,820 + 5,148,780 = 5,395,600
$$

The probability of exactly one consecutive pair show up on a result therefore is:

$$
P(pairs = 1) = \dfrac{n_{pa}}{{49 \choose 6}} = \dfrac{5,395,600}{13,983,816} = 0.38584603802 \approx 38.58 \\%
$$

### 1.3. The probability of 2 or more pairs of consecutive numbers in a result

The probability of 2 or more pairs of consecutive numbers in a result can now be calculated simply:

$$
P(pairs \ge 2) = P(pairs \ge 1) - P(pairs = 1) = 49.52 \\% - 38.58 \\% = 10.94 \\%
$$

## 2. High probability of 3 or more numbers in the same group

We can split the numbers 1-49 into 5 groups:

1. 1-10
2. 11-20
3. 21-30
4. 31-40
5. 41-49

There're 10 numbers in groups 1-4, and 9 numbers in group 5.

Since there're 5 groups and the draw contains 6 numbers, by the [pigeonhole principle](https://en.wikipedia.org/wiki/Pigeonhole_principle) at least one group will have at least 2 numbers in each draw.

But what is the probability of 3 or more numbers in the same group i.e. {12, 15, 17} or {32, 34, 37, 38} etc. ?

The total combinations of having 3 or more numbers in a group can be calculated as the sum of combinations of picking at least 3 numbers from that group and the remaining numbers from outside that group.

For example, the total combinations of picking 3 or more numbers from group 1 is:

$$
C(10, 3) \cdot C(39, 3) + C(10, 4) \cdot C(39, 2) + C(10, 5) \cdot C(39, 1) + C(10, 6) \cdot C(39, 0)
$$

This can be generalized as:

$$
c_g = \sum^{k}_{i = 3} C(n_g, i) \cdot C(n - n_g, k - i)
$$

Equivalently:

$$
c_g = \sum^{k}_{i = 3} {n_g \choose i} {n - n_g \choose k - i}
$$

where:

- $c_g$: total combinations of having at least $i$ numbers in group $g$.
- $n_g$: total numbers in group.
- $i$: quantity of minimum numbers in group where $i \le k$.
- $n$: total lottery numbers.
- $k$: total of lottery picks.

And so the total number of combinations that have 3 numbers or more in a group, for all groups, in general would be:

$$
c = \sum_{j = 1}^{g} \sum_{i = 3}^{k} C(n_j, i) \cdot C(n - n_j, k - i)
$$

Equivalently:

$$
c = \sum_{j = 1}^{g} \sum_{i = 3}^{k} {n_j \choose i} {n - n_j \choose k - i}
$$

where:

- $g$: number of groups.
- $n_j$: total numbers in group j.

Applying this to our 49/6 lottery with 5 groups, we'd have:

$$
c = \sum_{j = 1}^{5} \sum_{i = 3}^{6} {n_j \choose i} {49 - n_j \choose 6 - i}
$$

Since groups 1-4 are the same ($n_j = 10$, $49 - n_j = 39$), we have

$$
\begin{equation}
\begin{split}
c_{1-4} &= 4 \left( {10 \choose 3}{39 \choose 3} + {10 \choose 4}{39 \choose 2} + {10 \choose 5}{39 \choose 1} + {10 \choose 6}{39 \choose 0} \right) \\
&= 4 (1,096,680 + 155,610 + 9,828 + 210) = 5,049,312 \nonumber
\end{split}
\end{equation}
$$


Group 5 contains 9 numbers only, so $n_j = 9$, $49 - n_j = 40$. We have:

$$
\begin{equation}
\begin{split}
c_{5} &= {9 \choose 3}{40 \choose 3} + {9 \choose 4}{40 \choose 2} + {9 \choose 5}{40 \choose 1} + {9 \choose 6}{40 \choose 0} \\
&= 829,920 + 98,280 + 5,040 + 84 = 933,324 \nonumber
\end{split}
\end{equation}
$$

So finally:

$$
\begin{equation}
\begin{split}
c &= \sum_{j = 1}^{5} \sum^{6}_{i = 3} {n_j \choose i} {49 - n_j \choose 6 - i} \\
&= c_{1-4} + c_{5} = 5,049,312 + 933,324 = 5,982,636 \nonumber
\end{split}
\end{equation}
$$

The probability of 3 or more numbers in the same group would be:

$$
p = \dfrac{c}{{49 \choose 6}} = \dfrac{5,982,636}{13,983,816} = 0.42782570937 \approx 42.78 \\%
$$

## 3. High probability of more odd numbers and small numbers

Let's split our numbers 1-49 to 2 separate groups:

1. Odd / even and
2. Small / large

- For case #1 we know that there are 25 odd numbers, and 24 even numbers in 1-49 range.
- For case #2 let's call numbers 1-25 small, and 26-49 large so we have 25 small numbers and 24 large numbers.

So for both cases, we have 2 groups:
1. Odd (or small) numbers: 25 numbers.
2. Even (or large) numbers: 24 numbers.

Let's explore the probability of each and every distribution of numbers in these 2 groups in a draw.

We know that there can be 7 scenarios:

| Number | Scenario |
|--------|----------|
| 1      | 0-6      |
| 2      | 1-5      |
| 3      | 2-4      |
| 4      | 3-3      |
| 5      | 4-2      |
| 6      | 5-1      |
| 7      | 6-0      |

where 0-6 means 0 numbers from group 1 (odd/small) and 6 numbers from group 2 (even/large).

Each scenario come with its combination and probability:

| No. | Scenario | Combinations | Combinations result | Probability | Probability result |
|---|---|---|---|---|---|
| 1 | 0-6 | $${25 \choose 0} \cdot {24 \choose 6}$$ | $$134,596$$ | $$\dfrac{{25 \choose 0} \cdot {24 \choose 6}}{{49 \choose 6}}$$ | $$0.00962512664 \approx 0.96\\%$$ |  |
| 2 | 1-5 | $${25 \choose 1} \cdot {24 \choose 5}$$ | $$1,062,600$$ | $$\dfrac{{25 \choose 1} \cdot {24 \choose 5}}{{49 \choose 6}}$$ | $$0.07598784194 \approx 7.59\\%$$ |
| 3 | 2-4 | $${25 \choose 2} \cdot {24 \choose 4}$$ | $$3,187,800$$ | $$\dfrac{{25 \choose 2} \cdot {24 \choose 4}}{{49 \choose 6}}$$ | $$0.22796352583 \approx 22.8\\%$$ |
| 4 | 3-3 | $${25 \choose 3} \cdot {24 \choose 3}$$ | $$4,655,200$$ | $$\dfrac{{25 \choose 3} \cdot {24 \choose 3}}{{49 \choose 6}}$$ | $$0.33289911709 \approx 33.29\\%$$ |
| 5 | 4-2 | $${25 \choose 4} \cdot {24 \choose 2}$$ | $$3,491,400$$ | $$\dfrac{{25 \choose 4} \cdot {24 \choose 2}}{{49 \choose 6}}$$ | $$0.24967433782 \approx 25\\%$$ |
| 6 | 5-1 | $${25 \choose 5} \cdot {24 \choose 1}$$ | $$1,275,120$$ | $$\dfrac{{25 \choose 5} \cdot {24 \choose 1}}{{49 \choose 6}}$$ | $$0.09118541033 \approx 9.12\\%$$ |
| 7 | 6-0 | $${25 \choose 6} \cdot {24 \choose 0}$$ | $$177,100$$ | $$\dfrac{{25 \choose 6} \cdot {24 \choose 0}}{{49 \choose 6}}$$ | $$0.01266464032 \approx 1.27\\%$$ |

From this, we can see that the probability of a balance distribution (3-3) is 33.29%.
And so the probability of an imbalance distribution is:

$$
1 - 0.3329 = 0.6671 \approx 66.71\\%
$$

This is a much higher chance than that of a balance one (2 times).

Specifically, the probability of an imbalance distribution where there are more even numbers (or large numbers) than odd numbers (or small numbers) is:

$$
22.8 + 7.59 + 0.96 = 31.35\\%
$$


And the probability of an imblance distribution where there are more odd numbers (or small numbers) than even numbers (or large numbers) is:

$$
25 + 9.12 + 1.27 = 35.39\\%
$$

## Conclusion

Every exact 6-number combination is equally likely. However, some structural patterns (like consecutive pairs) occur quite often, even though players tend to avoid them. While this doesn’t raise your odds of winning, it may increase your expected payout by making it less likely you’ll have to share the jackpot if you do win.