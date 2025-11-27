# String Metrics

## Edit-based

### [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
Counts:
- Insertions
- Deletions
- Substitutions

Definition:

$$
\text{lev}(a,b) =
\begin{cases}
  |a| & \text{if } |b| = 0, \\
  |b| & \text{if } |a| = 0, \\
  \text{lev}(\text{tail}(a), \text{tail}(b)) & \text{if } \text{head}(a) = \text{head}(b), \\
  1 + \min
  \begin{cases}
    \text{lev}(a, \text{tail}(b)) \\
    \text{lev}(\text{tail}(a), b) \\
    \text{lev}(\text{tail}(a), \text{tail}(b))
  \end{cases} & \text{otherwise}
\end{cases}
$$

where:

- $\text{tail}(x)$: string of $x$ but excludes first character. I.e. $\text{tail}(x_0x_1...x_n) = x_1x_2...x_n$.
- $\text{head}(x)$: first character of $x$ i.e. $\text{head}(x) = x_0 = x[0]$.

## Sequence-based

### [Jaro Similarity](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance#Jaro_similarity)
Considers:
- Character order
- Matching position

Definition:

$$
S_j =
\begin{cases}
  0 & \text{if } m = 0 \\
  \dfrac{1}{3} \left( \dfrac{m}{|s_1|} + \dfrac{m}{|s_2|} + \dfrac{m - t}{m} \right) & \text{otherwise}
\end{cases}
$$

where:
- $S_j$: Jaro similarity score.
- $|s_i|$: length of string $s_i$.
- $m$: number of matching characters.
- $t$: number of transpositions.

### [Jaro-Winkler Similarity](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance#Jaro%E2%80%93Winkler_similarity)
Does:
- Introduce prefix scale $p$.
- Give more accurate answer when the strings have a common prefix.

Definition:

$$
S_w = S_j + \ell p (1 - S_j)
$$

where:

- $S_j$: Jaro similarity score of strings s1 and s2.
- $\ell$: length of common prefix at the start of the string (up to 4 characters).
- $p$: constant scaling factor - how much score is adjusted upwards for common prefixes. Standard value is $p = 0.1$.

## Token-based

### [Overlap (Szymkiewicz–Simpson) Coefficient](https://en.wikipedia.org/wiki/Overlap_coefficient)
- Measures overlap between 2 (character in this case) sets.

Definition:

$$
O(A, B) = \dfrac{|A \cap B|}{\text{min}(|A|, |B|)}
$$

where:
- $O(A, B)$: Overlap similarity score of set $A$ and $B$.
- $A$: set of n-grams of string $s_1$.
- $B$: set of n-grams of string $s_2$.
- $|A|$: length of set $A$.
- $|B|$: length of set $B$.
- $|A \cap B|$: length of intersection set of $A$ and $B$.


### [Jaccard Coefficient](https://en.wikipedia.org/wiki/Jaccard_index)
- Intersection over union of token sets.

Definition:

$$
J(A, B) = \dfrac{|A \cap B|}{|A \cup B|}
$$

where:
- $J(A, B)$: Jaccard similarity score of set $A$ and $B$.
- $|A \cup B|$: length of union set of $A$ and $B$.

### [Dice-Sørensen Coefficient](https://en.wikipedia.org/wiki/Dice-S%C3%B8rensen_coefficient)
- Emphasizes common tokens.

$$
DS(A, B) = \dfrac{|A \cap B|}{|A| + |B|}
$$

where:
- $DS(A,B)$: Dice-Sørensen similarity score of set A and B.