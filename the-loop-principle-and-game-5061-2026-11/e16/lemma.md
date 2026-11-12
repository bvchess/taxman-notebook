# The gluing lemma, for an independent reading

Copied 2026-11-11 from e12/README.md (its model, the lemma and its proof) and from the study report (the generalized statement only).

## The model

n = c·P, the window columns P_0 = P, P_1, …, P_d clean ((c + 1)·P_j > n).  A *cell* is (k, j) = k·P_j for a
composite k ≤ c.  It lists its *column factors* (k/q, j), one for each prime q dividing k, and its *hub* k.

Three facts of a clean column, each checked from the factorization:
* A column factor is a maximal factor of cells of its own column only.
* A cell's maximal factors are its column factors and its hub, so a cell shares nothing with the rest of the board
  but hubs.
* No number off the window lists a cell.

The layer-2 cells (q, j) and P_j are left out of the cells.  From 187 on an optimal set plays no layer-2 number up to
n/2 and no prime but q(n) (F4 and F10), and a layer-2 cell above n/2 is a factor of no cell; so a column factor of a
prime row is always in the pool.  *Sources* are the cells of rows k > c/2, *candidates* those of rows k ≤ c/2.  On
board n − 1 the cell (c/2, 0) = n/2 is a source, and (c, 0) = n is gone.

**The gluing lemma (core domination).**  This replaces the acyclicity lemma of Section 11.2, item 2: it needs no
payment schemes, and so nothing about which hubs the rest of the board holds.

For a set Z of cells, call X ⊆ Z, X ≠ ∅, *column-closed in Z* when each column factor in Z's pool (a prime row's
always, a composite row's when its cell is not in Z) that a member of X lists is listed by another member of X.  Its
*signature* is (R1, R2): the rows that one member of X uses, and those that two or more use.

> Let n ≥ 187, S an optimal set of n, W its cells, O = S − W, and W′ a set of cells of board n − 1.  Suppose that
> every X column-closed in W′ has a Y column-closed in W with rows(Y) ⊇ rows(X) and R1(Y) ⊆ R1(X).  Then O ∪ W′
> is playable on board n − 1, and so δ(n) ≥ ΣW′ − ΣW + n.

*Proof.*  By the core theorem (P7) it suffices that O ∪ W′ has no core.

1. *The lists of O are the same.*  The lists of O's members are the same in S and in O ∪ W′: they differ only at
   cells, which no member of O lists, and at n, which nothing lists.
2. *A core K of O ∪ W′ meets W′ in a column-closed set.*  Let X = K ∩ W′.  A column factor is listed by cells alone,
   so X is column-closed in W′ (or empty, and then K ⊆ O is a core of S).  Let Y be the set that the hypothesis
   gives.
3. *K* = (K − X) ∪ Y is a core of S.*  Each factor listed by a member of K* is listed by another member of K*:
   * Y's column factors are listed twice within Y.
   * A hub that two or more members of Y use is covered.  A hub that one member of Y uses is in R1(Y) ⊆ R1(X), so
     one member of X lists it, and K covers it by a member of K − X.
   * A factor listed by a member o of K − X is listed in K by another member of K.  If that member is in X, the
     factor is a hub of a row of X, and rows(Y) ⊇ rows(X) gives a member of Y that lists it.  A non-hub factor of o
     is listed by no cell, so another member of K − X lists it.
   * Hubs that are moves of O are in neither pool, and the argument holds as it stands.
4. *Contradiction.*  K* is a core of the playable set S, against P7.  ∎

**The enumeration** (`window_law.py`):
* *States:* every set W of cells of board n that holds n and every source (statement U gives the sources when they
  lie in U*(n)), plus any candidates, and has no core in its own window instance (S is playable).
* *For each state, a witness:* W′ = (the sources less n) plus candidates, satisfying the lemma's domination, with

## The generalized statement (to check as well)

**Statement (E12's, generalized to a region).**  Let n ≥ 187 and let R be a set of columns of primes P_j with
2P_j² > n; the *cells* of R are the numbers k·P_j with k composite and k·P_j ≤ n.  Let S be a playable set of n, W
its cells, O = S − W, and W′ a set of cells of board n − 1.  For a set Z of cells, X ⊆ Z nonempty is *column-closed
in Z* when every column factor outside Z that a member of X lists is listed by another member of X; its signature is
R1(X), the rows whose hub exactly one member of X lists, and R2(X), the rows listed by two or more.  If every X
column-closed in W′ has a Y column-closed in W with rows(Y) ⊇ rows(X) and R1(Y) ⊆ R1(X), then O ∪ W′ is playable
on board n − 1, so opt(n − 1) ≥ ΣO + ΣW′ and δ(n) ≥ ΣW′ − ΣW + n.

The claim is that the proof above carries over with "clean column" replaced by 2P_j² > n for every prime P_j of R, and with S only playable (not optimal).
