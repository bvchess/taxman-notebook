## 1. Words

The game, playable sets, instances, lists, payment schemes, layers, sources, U\*, the parity vectors, PB, the gap,
δ, δ_PB and rise are S's (S 1.1 to 1.4), and the three kinds of searched step S 2.2's.  v(s) is the incidence vector
of s over GF(2) (ones at its maximal factors), e_s the unit vector of s ≤ n/2.  Ω(x) is the number of prime factors
of x with multiplicity.

* **Columns and cells (B 1, made precise).**  P = P₀ is the largest prime factor of n, c = n/P its cofactor, and
  P₁ > P₂ > … the primes below P.  A number w whose largest prime factor is P_j is the *cell* (k, j) with k = w/P_j,
  in *row* k and *column* j.  Column j of board m is the set of its cells (k, j) ≤ m: the rows it holds are the k
  with kP_j ≤ m, since for P_j > c every k ≤ c has its primes below P_j.  Column 0 of board n holds exactly the rows
  1..c.
* **Clean (B 1, the definition this report uses).**  The window of n is *clean to depth d* when (c + 1)P_i > n for
  every 1 ≤ i ≤ d.  Then columns 1..d of board n, and of board n − 1, hold exactly the rows 1..c, as column 0 does.
  The depth is computed from n's factorization alone (`patterns.clean_depth`).  Cleanliness to depth d says nothing
  about columns beyond d, and nothing about the hubs.
* **Hubs.**  A cell (k, j) has the maximal factors (k/q, j) for the primes q dividing k, which lie in its column, and
  the number k itself, the *hub* of row k, which every cell of row k lists.  A hub k ≤ c lies in every column's
  row-k cell's list, in clean and unclean columns alike, and it is listed by numbers that are no cell of the window
  (hub 12 by 12t for every prime t ≤ n/12).  In a payment scheme a hub pays for at most one member, so the hubs are
  the only resource the columns share; the column factors (k/q, j) are private to their column.
* **The change and the pattern (B 1).**  D is the set of moves of the recorded optimal set of n − 1 that the recorded
  optimal set of n gives up, A those it takes up besides n; δ(n) = ΣD − ΣA.  When every member of D and A is a cell
  (k, j) with |j| ≤ 12, the pair (D, A) in cell labels is the *pattern*, a formula in P₀, P₁, …  The *depth of a
  pattern* is the largest column index it uses; the *depth of a family* is the depth of its commonest pattern on
  187..5060 (`study/depth_check.py` prints them: 8 → 1, 12 → 1, 16 → 3, 20 → 2, 24 → 2, 40 → 1).
* **G(m)**, the greedy basis of the sources' vectors of board m: the sources kept when they are taken by decreasing
  value and each is kept whose vector is not in the span of those kept before it ([the greedy-basis proposition
  W3](https://github.com/bvchess/taxman/blob/287486e/docs/theory/parity-bound.md#the-greedy-basis-proposition)).  G(m) = U\*(m) exactly when (♦) holds in game
  m (W3), which is checked to 100,000.
* **Q\*(m)**, the parity bound's promotion sum: the largest ΣL over sets L of numbers of 2..⌊m/2⌋ such that G(m) ∪ L
  is independent at both parities.  By W3, PB(m) = ΣG(m) + Q\*(m) (every heaviest set holds exactly G(m) among the
  sources, so the maximum over heaviest sets is the maximum over their lower parts).

