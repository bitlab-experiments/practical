# Fuzzy String Match

## Overview

Consider having an example list of medicament:

```json
[
  ...
  "Pantoprazol antacid Sandoz, magensaftresistente Filmtabletten",
  "Pantoprazol Axapharm 20 mg, magensaftresistente Tabletten",
  "Pantoprazol Axapharm 40 mg, magensaftresistente Tabletten",
  "Pantoprazol NOBEL 20 mg, magensaftresistente Tabletten",
  "Pantoprazol NOBEL 40 mg, magensaftresistente Tabletten",
  "Pantoprazol Nycomed 20 mg, magensaftresistente Tabletten",
  "Pantoprazol Nycomed 40 mg, magensaftresistente Tabletten",
  "Pantoprazol Nycomed i.v., Lyophilisat",
  "Pantoprazol Sandoz 20 mg, magensaftresistente Filmtabletten",
  "Pantoprazol Sandoz 40 mg, magensaftresistente Filmtabletten",
  "Pantoprazol Spirig HC 20 mg, magensaftresistente Tabletten",
  "Pantoprazol Spirig HC 40 mg, magensaftresistente Tabletten",
  "Pantoprazol Streuli 20 mg, Filmtabletten",
  "Pantoprazol Streuli 40 mg, Filmabletten",
  "Pantoprazol Zentiva 20 mg, Filmtabletten",
  "Pantoprazol Zentiva 40 mg, Filmtabletten",
  "Pantoprazol-Mepha 20 mg, Filmtabletten",
  "Pantoprazol-Mepha 40 mg, Filmtabletten",
  "Pantoprazol-Mepha gastro 20 mg, magensaftresistente Filmtabletten",
  "Pantoprazol-Mepha Teva 20 mg, magensaftresistente Filmtabletten",
  "Pantoprazol-Mepha Teva 40 mg, magensaftresistente Filmtabletten",
  ...
]
```

Given a user query like:

```json
"PANTOPRAZOL Mepha Filmtabl 40 mg 100 Stk"
```

A human can easily find the intended match:

```json
"Pantoprazol-Mepha 40 mg, Filmtabletten"
```

Machines, however, struggle with this because they rely on exact matching and lack semantic understanding. Fuzzy string matching helps by computing similarity scores even when:

- Word order differs
- Abbreviations appear (“Filmtabl” vs “Filmtabletten”)
- Casing varies
- Typos or spelling variations occur
- Extra information is present (e.g. quantity)

Fuzzy matching is widely used not only in product or medicament lookup, but also in:

- AI/NLP pipelines (entity resolution, text normalization, query expansion)
- Genomic sequence analysis (approximate matching of DNA/RNA sequences, variant detection)
- Record linkage (merging datasets with inconsistent naming)
- Search engines and autocomplete systems
- Fraud detection (matching near-duplicate entries)

Below is a summary of major fuzzy matching algorithm categories.

## 1. Edit-based Methods

### [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)

Measures the minimum number of:
- Insertions
- Deletions
- Substitutions

required to transform one string into another.

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

## 2. Sequence-based Methods

### [Jaro Similarity](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance#Jaro_similarity)

Considers character order and approximate positions.

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

Adds a prefix bonus.

Definition:

$$
S_w = S_j + \ell p (1 - S_j)
$$

where:

- $S_j$: Jaro similarity score of strings $s_1$ and $s_2$.
- $\ell$: length of common prefix at the start of the string (up to 4 characters).
- $p$: constant scaling factor - how much score is adjusted upwards for common prefixes. Standard value is $p = 0.1$.

## 3. Token-based Methods

These convert strings into sets of tokens or n-grams.

### [Overlap (Szymkiewicz–Simpson) Coefficient](https://en.wikipedia.org/wiki/Overlap_coefficient)
- Measures overlap between 2 (character in this case) sets.

Definition:

$$
O(A, B) = \dfrac{|A \cap B|}{\text{min}(|A|, |B|)}
$$

where:
- $O(A, B)$: Overlap similarity score of set $A$ and $B$.
- $A$: set of tokens or [n-grams](https://en.wikipedia.org/wiki/N-gram) of string $s_1$.
- $B$: set of tokens or [n-grams](https://en.wikipedia.org/wiki/N-gram) of string $s_2$.
- $|A|$: length of set $A$.
- $|B|$: length of set $B$.
- $|A \cap B|$: length of intersection set of $A$ and $B$.


### [Jaccard Index](https://en.wikipedia.org/wiki/Jaccard_index)
- Intersection over union of token sets.

Definition:

$$
J(A, B) = \dfrac{|A \cap B|}{|A \cup B|} = \dfrac{|A \cap B|}{|A| + |B| - |A \cap B|}
$$

where:
- $J(A, B)$: Jaccard similarity score of set $A$ and $B$.
- $|A \cup B|$: length of union set of $A$ and $B$.

### [Dice-Sørensen Coefficient](https://en.wikipedia.org/wiki/Dice-S%C3%B8rensen_coefficient)
- Emphasizes common tokens.

$$
DS(A, B) = \dfrac{2 |A \cap B|}{|A| + |B|}
$$

where:
- $DS(A,B)$: Dice-Sørensen similarity score of set A and B.