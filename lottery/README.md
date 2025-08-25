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
\{5, 12, 27, 35, 40, 43\}
$$

or:

$$
\{7, 12, 27, 35, 45, 48\}
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

Imagine that we have a vertical line with 49 points on it, each represents a number in our game.

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
P(pairs \ge 1) = 1 - \dfrac{{n - k + 1 \choose k}}{{n \choose k}} =  1 - \dfrac{{44 \choose 6}}{{49 \choose 6}} = 1 - \dfrac{7,059,052}{13,983,816} = \dfrac{6,924,764}{13,983,816} \approx 0.4951984494 = 49.52\\%
$$

### 1.2. The probability of exactly 1 pair of consecutive numbers in a result

To imagine picking up exactly 1 pair of consecutive numbers, we can think of the picks as containing one block (2 consecutive numbers), and other 5 non-consecutive numbers.

`p-p-3-p-5-p-6-p-8-p-10-11-12-13-14-15-16-17...49`

So it would be starting with a consecutive pair as a block, then add 4 more non-consecutive numbers around it.

There are 48 possible consecutive pairs i.e. 1-2, 2-3, ... 48-49. They can be splitted on 2 cases:
1. Edge case: with consecutive pair {1, 2} or {48, 49}.
2. General case: all other consecutive pairs.

For all cases, we choose a consecutive pair:

$$
pair = \{m, m + 1\}
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
exclude = \{m - 1, m + 2\}
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

### Conclusion

Every exact 6-number combination is equally likely. However, some structural patterns (like consecutive pairs) occur quite often, even though players tend to avoid them. While this doesn’t raise your odds of winning, it may increase your expected payout by making it less likely you’ll have to share the jackpot if you do win.

## 2. 