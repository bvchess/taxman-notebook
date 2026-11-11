# Odd cores and the parity bound: a research brief

*Written 2026-11-10 for a reader who has only this document.  Its subject: an upper bound on the best score of the
game Taxman that is computable and much tighter than the one in use, and why the obvious ways to get one have failed.*

## 0. The question in one page

Taxman on the numbers 1..n is a puzzle whose best score opt(n) is known exactly, by proof, for every n ≤ 5060.  The
proofs are branch and bound searches whose upper bound is the **parity bound** PB(n): the heaviest set of numbers whose
incidence vectors over GF(2) are independent in two matroids (Section 1.4).  Past 5060 the best scores known are found
by heuristic searches; about 97% of them are probably optimal, and in rehearsals on known games the short ones fell 1
to 65 points short.

A proof's cost is set by the **gap** PB(n) − opt(n).  Over the 1,745 searches that proved games of 1..5060, the rank
correlation of the gap with the search's node count is 0.96 overall, and 0.82 to 0.96 within each thousand games.  The
nodes go up about tenfold per 400-500 points of gap at n ≈ 4000-5000 (Section 5.2).  Gaps of 2,000-2,100 cost about
10⁸ nodes, and 2,400-2,700 about 10⁹, which at 0.67 ms a node is about 190 CPU-hours.  Past 5060 the gap starts at
3,049 (game 5061), has a median of 5,177 and reaches 11,686 by 10,000.  It grows like n²: from 1000 to 10,000 the gap
is a steady 2.6 to 3.9 × 10⁻⁴ of the score.  To bring them into the range proven so far (10⁸-10⁹ nodes), the first
searched games past 5060 (gaps 3,000-3,350) need the gap cut by 13-37%, a typical game of the 6000s by 40-55%, and one
near 10,000 by 75-80%, **at every node of the search**, not only at the root.

The parity bound fails only where its heaviest set contains an **odd core**: a set of moves that cannot be played
(every factor they could pay with is wanted twice) but whose vectors are independent over GF(2).  Optimizing over
playable sets instead of GF(2)-independent ones is NP-hard on general instances of the same shape (Section 1.5), so a
tighter bound has to use the arithmetic of Taxman.  Every relaxation tried so far closed a share of the gap that falls
as the gap grows, and each gave a constant factor in a search, not a change of slope.  This brief gives the definitions
and theorems exactly (Section 1), what is known about where the gap lives (Section 2), worked examples from n = 45 to
5000 (Section 3), every attempt and why it failed (Section 4), the data (Section 5), the open directions (Section 6)
and what a useful answer looks like (Section 7).  Facts are labeled *proved*, *measured* (a computation, no proof) or
*conjecture*.

## 1. The game, the model and the bound

### 1.1 The game

The *board* of game n is {1, ..., n}; the *pot* starts as the whole board.  A *move* takes a number x still in the pot
that has at least one proper divisor still in the pot; the player scores x, and the taxman takes every proper divisor
of x still in the pot.  When no number in the pot has a proper divisor in it, the game ends (the taxman takes the
rest).  The *score* is the sum of the moves, and opt(n) is the best score.  Example: game 6 has the optimal game 5, 4,
6 (the taxman takes 1, then 2, then 3), so opt(6) = 15.  opt is OEIS A019312; opt(n)/(n²/2) tends to a constant
between 1/2 and 35/48 (Hensley 1988); opt(5000) = 7,868,316 ≈ 0.315 n².

Notation, fixed throughout.  Ω(x) is the number of prime factors of x with multiplicity, its *layer* (Ω(12) = 3,
Ω(1) = 0).  mf(x) = {x/p : p prime, p | x} are the *maximal factors* of x (mf(12) = {4, 6}; a prime's is {1}).  Every
f ∈ mf(x) has Ω(f) = Ω(x) − 1.  A *source* is a number above n/2 (it divides nothing else on the board, so it is never
tax); a *factor* is a number up to n/2.  For a set S, ΣS is its sum, S_k its members in layer k.  q(n) is the largest
prime ≤ n.  A set S ⊆ {2, ..., n} is *playable* when some game plays all of its members (and possibly others).

**Lemma (lifting).**  If a proper divisor of x is in the pot, so is a maximal factor of x.  So x can be played exactly
when some member of mf(x) is in the pot.  *(Proved.)*

### 1.2 Playability: schemes, peel, cores

The *own instance* of S has members S and pool F(S) = (∪_{x∈S} mf(x)) ∖ S; member x *lists* L(x) = mf(x) ∖ S.  A
*payment scheme* gives each member a distinct factor it lists, pay(x) ∈ L(x).  Its *precedence* is the digraph on S
with an edge a → b (a ≠ b) when pay(a) | b or a | b: a must come before b.

**Theorem P2 (playability).**  S is playable iff some payment scheme has an acyclic precedence; then every topological
order of that precedence is a game playing S.  *(Proved.)*

**Lemma P3 (flat cycles).**  Every cycle of the precedence lies in one layer, and on each of its edges a → b, pay(a) is
a maximal factor of b (b lists pay(a)).  *Proof:* φ(x) = Ω(pay(x)) never falls along an edge and rises unless pay(a) ∈
mf(b).  *(Proved.)*

**Layer theorem F3.**  S is playable iff each *layer instance* is: members S_k, pool the numbers of layer k − 1 up to
n/2 not in S.  *(Proved.)*  So a game is a chain of independent layer problems coupled only through which numbers up
to n/2 are played: a number y of layer j ≤ n/2 is either a move (a member of layer j's instance) or a factor (in the
pool of layer j + 1's instance), never both.

**Peel.**  A *front move* pairs a member that lists one live factor with it; a *back move* pairs a factor listed by one
live member with that member; each removes the pair.  **Theorem P4:** an instance is playable iff some (equivalently
every) run of peel pairs every member.  *(Proved.)*

A *core* is a nonempty set T of members in which every factor listed by a member of T is listed by at least two
members of T (a member listing nothing is a core).  *Dismantling* repeatedly deletes a member that lists a factor no
other remaining member lists; what remains is the *residual* R.  **Theorems P5, P7:** R does not depend on the order,
it is the union of every core, and the instance is playable iff R = ∅.  *(Proved.)*  In coding-theory language the
cores are the *stopping sets* of a parity-check matrix with variables = members, checks = factors; peel is the erasure
decoder.

**Theorem P8 (exclusion).**  Let an instance have members S and residual R, and E ⊆ S.  If S ∖ E is playable in the
instance (same pool), so is S ∖ (E ∩ R).  For a *separated* S ⊆ {2..n} (no member a maximal factor of another, e.g. a
set of sources) the same holds on the board.  Hence every minimal exclusion set lies in R, and every heaviest playable
subset of S keeps all members outside R.  *Proof:* a core surviving the exclusion of E ∩ R lies in R and avoids E.
*(Proved; {2, 4} on board 4 shows separation is needed.)*

**Independence.**  Over a field 𝔽, v(x) ∈ 𝔽^{1..⌊n/2⌋} has a 1 at each maximal factor of x; e_x is the unit vector of
x ≤ n/2.  S is *independent with its own coordinates* when {v(x) : x ∈ S} ∪ {e_x : x ∈ S, x ≤ n/2} is linearly
independent; equivalently the list vectors u(x) (v(x) with S's coordinates deleted) are independent.

**Lemma P9/P10 (independence).**  If S is playable, ordering the pairs of a complete peel (back moves in order made,
then front moves in reverse) makes the list matrix upper triangular with nonzero diagonal, for any nonzero entries.
So a playable set is independent with its own coordinates over every field and under every choice of nonzero entries
("signing").  *(Proved.)*

**Proposition P11 (two factors).**  If every member lists at most two factors, view members as edges between their two
factors (a member with one factor is an edge to a *ground* vertex).  Then playable ⟺ lists independent over GF(2) ⟺
the graph is a forest.  *(Proved.)*  So GF(2) independence is exact on members with at most two live factors.

**Theorem C2 (counting).**  For a set T of |S| factors of the pool let per(S, T) be the number of payment schemes of S
with payment set T (the permanent of the columns T of the list matrix).  Then S has a payment scheme iff some per(S, T)
≥ 1; S is independent with own coordinates over GF(2) iff some per(S, T) is odd (det ≡ per mod 2); S is playable iff
some per(S, T) = 1 (two schemes with one payment set differ by flat alternating cycles, which are precedence cycles).
*(Proved.)*  The three bounds that correspond are the Franklín–Moniot matching bound, the parity bound and opt(n).

### 1.3 The frame model in brief

The proofs run in a reformulation; the reader needs only its dictionary.

* **Frames.**  The *frame graph* joins each source to its maximal factors; a *frame* is a component (some sources of
  one layer k and all factors, of layer k − 1, that can pay for them).  A frame's *freedoms* are its factors less the
  sources it keeps; a frame with none is *closed*.
* **U\*.**  *Descending greedy* takes the sources from n down and keeps each that is playable together with those kept
  (the sources are separated, so this is a test on the sources' instance).  U\* is what it keeps.  *Span conjecture
  (♦):* every source it rejects has v(s) equal to a GF(2) sum of v of kept sources above it; certified in every game to
  100,000, open in general.  Given (♦), U\* is the greedy GF(2) basis of the sources' vectors.
* **Bottom layers (F4, proved).**  Every optimal set plays q(n) and no other prime, and exactly U\*_2 among the sources
  of layer 2; from n = 187 on (square theorem F10, proved) layer 2 is one closed frame and an optimal set plays no
  number of layer 2 up to n/2.  So from 187 on the action is in layers 3 and up.
* **Promotions.**  The frame solver fixes the sources to U\* and searches which factors to *promote* (play).  Frames
  with freedoms are numbered by layer: for n ≥ 187, *frame h* is layer h + 3 (frame 0 = layer 3, frame 2 = layer 5).
  A *candidate of home h* is a factor of frame h (a number of layer h + 2 up to n/2) that could be played, becoming a
  move of frame h − 1.  P\* is the heaviest promotion set; the solver reports ΣU\* + P\*.
* **Statement U** (open; certified wherever the whole-board prover has run, n ≤ 2531): some optimal set contains every
  member of U\* in layers ≥ 3.  Given U at n, ΣU\* + P\* = opt(n) (exactness theorem X7 and corollary X8, proved).  The
  proofs past 2531 rest on U; this brief does not depend on that.
* **The frame bound B2** is the heaviest set of candidates independent "in every frame" over GF(2), within the
  promotion limit.  **Comparison theorem B6** (proved): ΣU\* + frame bound equals the parity bound with picks U\* and
  bars everything outside U\* ∪ candidates, so it is at most PB(n), and the promotion limit never lowers it.
  *Measured:* it equals PB(n) at every board 2..8191 and at all 4,940 games 5061..10000.  So the frame solver's root
  bound is the parity bound, and nothing in the model's fixings costs or gains anything at the root.
* **Theorems that settle games without a search** (all proved): the ceiling opt(n) ≤ opt(n − 1) + n; the prime formula
  opt(p) = opt(p − 1) + p − q(p − 1); the semiprime formula J3: for odd n with two prime factors that closes a cycle
  with U\*_2(n − 1) (every such n ≥ 189), opt(n) = opt(n − 1) + n − x, x the smallest other member of that cycle.  A
  *repeat* (a game posing the same frame-model problem as an earlier one, given U) is settled by that game.

### 1.4 The parity bound

Split the coordinates 1..⌊n/2⌋ into *blocks* by layer: block j holds the numbers up to n/2 of layer j.  For x of
layer k, v(x) lies in block k − 1 and e_x (if x ≤ n/2) in block k.  E₀ is the union of the even blocks, E₁ of the odd.

**Definition.**  The *parity-i vector* of x ∈ {2..n} is v(x) if Ω(x) ≢ i (mod 2); e_x if Ω(x) ≡ i and x ≤ n/2; and a
private *extra coordinate* if Ω(x) ≡ i and x > n/2.  S is *independent at parity i* if its parity-i vectors are
independent over GF(2), and *independent at both parities* if at both.  M_i is the linear matroid on {2..n} so defined.
With picks Y and bars Z: I is independent *together with Y* when Y ∪ I is.

**Theorem W1 (parity bound).**  Every playable set is independent at both parities.  Hence for disjoint picks Y and
bars Z with Y independent at both parities, every playable S ⊇ Y with S ∩ Z = ∅ has ΣS ≤ ΣY + max{ΣI : I ∩ (Y ∪ Z) = ∅,
I independent at both parities together with Y}; and PB(n) := max{ΣI : I independent at both parities} ≥ opt(n).
*Proof.*  The family {v(s)} ∪ {e_s : s ≤ n/2} lies in blocks; a vanishing combination splits into one in E₀ and one in
E₁; the part in E_i is exactly the parity-i vectors of the members without an extra coordinate there, and an element
with a private coordinate never enters a dependency.  So *independent at both parities ⟺ independent with own
coordinates*, which a playable set is by P10.  ∎ *(Proved.)*

*Example.*  On board 10, E₀ = {1, 4}, E₁ = {2, 3, 5}.  At parity 0 every prime has v = e₁, so a set independent at
parity 0 holds at most one prime, as a game does; 4 and 8 share e₄.  At parity 1, {4, 6, 9} is dependent (v(4) + v(9)
= e₂ + e₃ = v(6)) and indeed unplayable.  The heaviest set is {6, 7, 8, 9, 10} = 40 = opt(10).

*The per-layer reading* (proved, immediate from the blocks).  Block j carries v(x) for the layer-(j + 1) members and
e_y for the layer-j members up to n/2.  Independence of block j says exactly that the list matrix of the layer-(j + 1)
instance (rows: its members; columns: layer-j numbers up to n/2 not played) has independent rows over GF(2).  M₀ is the
direct sum of the even blocks, M₁ of the odd ones, and each element x of layer k up to n/2 sits in two consecutive
blocks: as a row of layer k's instance (block k − 1) and as a deleted column of layer k + 1's instance (block k).
**So PB(n) is a weighted matroid intersection in which every element is shared by two adjacent layer problems.**

**Computing and certifying.**  PB(n) is a maximum-weight common independent set of M₀ and M₁, found by weighted matroid
intersection (shortest augmenting paths in the exchange graph, lengths +w inside, −w outside).  It is certified by a
*weight split* w = w₀ + w₁ under which the set I is a max-weight independent set of M₀ for w₀ and of M₁ for w₁: then
every common independent J has w(J) = w₀(J) + w₁(J) ≤ w₀(I) + w₁(I) (weak duality); a split always exists (Frank).
The same split bounds the sets that avoid a member x of I, by one exchange in each matroid: w(I) − w(x) + max(0, w(y))
with y the best replacement.  The prover accepts a value only with its split.  At n = 5000, PB takes about 7 s from
scratch in the prover, about 0.02 s at the frame solver's root, and about 1 ms per search node incrementally; a plain
Python implementation (beside this brief) takes 8.5 s.

**How the searches use it.**  Both programs branch on sets of moves.  A node fixes some numbers in (picks) and some out
(bars) and computes the parity bound with them; it is cut when the bound is at most the score to beat.  Otherwise the
weight split prices each member of the heaviest set: a member whose barring alone brings the bound to the target is
forced in, and a number outside whose forcing alone does so is barred.  If the heaviest set is playable (peel), it is a
game.  If not, a minimal unplayable subset (a *conflict*, found by a deletion filter with peel) must lose a member; the
node branches on which, choosing the conflict whose children fall furthest below the gap, and learns conflicts as
*nogoods*.  The frame solver does the same within the frame model, its candidates in place of the numbers up to n/2.
Every unit of a node's gap is paid for by such branchings, which is why the root gap governs the tree.

**Proposition W3 (greedy basis).**  Every heaviest set independent at both parities holds, among the sources, exactly
the greedy GF(2) basis of the sources' vectors v(s) taken by decreasing value; this is U\* iff (♦) holds.  *Proof
idea:* a source has a private coordinate at its own parity, so among the sources only v(s) matters, and a source left
out would replace any smaller member of its circuit.  *(Proved.)*  So PB(n) = ΣU\* + max{ΣI : I ⊆ {2..n/2}, I ∪ U\*
independent at both parities} wherever (♦) holds (every game checked).

Two consequences used below, both proved here (short proofs, checked numerically on 2..10000):

* **The parity ceiling.**  PB(n) ≤ PB(n − 1) + n.  *Proof:* let I be heaviest on board n.  If n is odd the coordinates
  of boards n and n − 1 coincide and I ∖ {n} is independent on board n − 1.  If n is even, m = n/2 is a coordinate on
  board n and a source with a private coordinate on board n − 1; only v(n) and e_m use coordinate m, so I ∖ {n}, with
  e_m replaced by a private coordinate, stays independent.  Either way Σ(I ∖ {n}) ≤ PB(n − 1).  ∎
* **The prime step.**  For a prime p, PB(p) = PB(p − 1) + p − q(p − 1).  *Proof:* the coordinates agree; p and q =
  q(p − 1) have the same parity-0 vector e₁ and private parity-1 coordinates, so they are parallel in M₀ and free in
  M₁; e₁ is in the span of no composite's vector, so every heaviest set holds the largest prime, and swapping q for p
  is a bijection.  ∎  (The game obeys the same rule: opt(p) = opt(p − 1) + p − q(p − 1), the prime formula.)

### 1.5 Odd cores

**Definition.**  An *odd core* of an instance is a core whose list vectors are linearly independent over GF(2).  By C2
it has an odd number of schemes onto some payment set but never exactly one.  The parity bound exceeds opt(n) only
through sets independent with own coordinates that are unplayable, and each such set contains an odd core (its
residual is a core, P7, and its lists are part of an independent family).  *(Proved.)*  By the exclusion theorem P8,
applied to one layer instance with its pool fixed, a minimal set of deletions that makes that layer playable lies in
the layer's residual, the union of its odd cores.  On the board there is a second way: dropping a played number of
layer k − 1 adds it to the pool of layer k, which can break a core there (adding a factor never creates one).  That is
why P8 needs separation on the board, and it is how optima often break cores (Section 3.5).  Section 2.2 measures what
deletions within the residuals cost against what the optimum does instead.

* **Where they live.**  By P11 an odd core needs a member with three or more live factors; and since a core with every
  column met evenly would be a GF(2) dependency, it also needs a factor listed by an odd number ≥ 3 of its members.
  Below 45 the only numbers with three maximal factors are 30 and 42, and their factors 15 and 21 have no second
  lister, so **no board n ≤ 44 has an odd core and PB(n) = opt(n) there** (C3, proved).
* **The first odd core** is {12, 18, 20, 30, 45} on board 45: lists 12: {4, 6}, 18: {6, 9}, 20: {4, 10}, 30: {6, 10,
  15}, 45: {9, 15}.  Every factor is listed twice (6 three times): a core.  Its only payment set is all five factors,
  with per = 3 (30 pays 6, 10 or 15, and the rest is then forced), so it is GF(2)-independent; its integer determinant
  is 3, so GF(3) sees it.  PB(45) = opt(45) = 660 all the same: no heaviest set needs it.  **The first board where PB
  exceeds opt is 78** (1992 against 1991; Section 3.2).
* **Theorem B5 (GF(3) signings are exact, frame by frame).**  A frame (layer instance) is winnable with a set applied
  iff the set is independent there under *every* signing over GF(3).  *Proof:* for a stalled peel, put values on the
  stalled members' incidences that sum to 0 at every live factor (1, 2 for two listers; 1, 1, 1 for three); the
  stalled rows then sum to zero modulo the triangular parts.  *(Proved.)*  Over any field with ≥ 3 elements, a zero
  pattern has full row rank under every choice of nonzero entries iff it has a matching of all rows that is the only
  matching between its row and column sets (Hershkowitz–Schneider 1993).  Over GF(2) this fails: the plain signing is
  the only one, and an odd core is independent under it.
* **Hardness.**  On posets of two ranks, the game is a maximum uniquely restricted matching, NP-hard on bipartite
  graphs (Golumbic–Hirst–Lewenstein 2001; Franklín–Moniot 2023, Theorem 2), APX-complete on bipartite graphs of degree
  3, and not approximable within n^{1/3−ε} unless NP = ZPP.  Each layer instance of Taxman is such a problem.  So
  unless P = NP no polynomial bound is exact on all instances of this shape, and the hard part needs members with three
  or more distinct primes.
* **A small lemma (proved here).**  A core whose members all list two factors except one member w listing three
  factors {a, b, c} is a tree (or path) through a, b and c plus the hyperedge w, and has exactly 3 schemes (w pays a, b
  or c; the tree then pays uniquely, rooted at the vertex w took).  Its vectors are GF(2)-independent because e_a +
  e_b + e_c has odd weight and the tree's edges span only even-weight vectors.  Its integer determinant is ±1 or ±3, so
  a fixed field sees it only by luck of signs.  With one member of four factors in place of w, the same shape is
  GF(2)-dependent (an even core): in this family the wide member must list an odd number of factors.

## 2. Where the gap comes from

Throughout, H(n) is a heaviest set of the parity bound (computed by the script beside this brief, which reproduces
PB(n) exactly on 133 boards checked against the project's values) and S\*(n) the recorded optimal set.

### 2.1 What the gap is not

* **Not the sources.**  H and S\* hold the same sources (W3 and certified (♦)), so the gap is entirely in the numbers
  up to n/2.  *(Proved given (♦); certified.)*
* **Not the count.**  H has exactly as many numbers up to n/2 as S\* at all 361 boards of 880-1300, at 758 of 760
  searched games of 1301-2175 (at 1320 and 1322 the heaviest set found has one fewer), and at all 54 boards sampled
  below (every hundred to 5000).  *(Measured.)*  The promotion limit never lowers the bound (B6, proved).  The error is
  which numbers, never how many.
* **Not the frame model.**  PB = ΣU\* + frame bound everywhere measured (B6).  On 5,496 boards from 1173 on some numbers
  are independent at both parities together with U\* but fail the frame model's candidate test through an odd core;
  no heaviest set found holds one, and forcing one in costs at least 187 (near n/2 − y).  *(Measured.)*
* **Not a short incumbent.**  Past 5060 the measured gap is PB minus a best-known score, but where that score is short
  it is short by 1-65 points (median 1-30 in rehearsals on 3001-5060), against gaps of 2,090 and more.

So **all of the gap is odd-core slack**: by Section 1.5 every unit of it is there because some heavier GF(2)-independent
set is unplayable through odd cores.  The useful decompositions are by layer, by kind of core, and by how the optimum
repairs them.

### 2.2 The anatomy at the root, from small n to 5060

| n | gap | promotions | swaps each way | excess by layer (H − S\* on the swapped numbers) | residual of H by layer: members/pool (members with ≥3 live factors) |
|---|---|---|---|---|---|
| 300 | 4 | 17 | 1 | L5 +4 | L5 7/7 (1) |
| 600 | 106 | 33 | 6 | L3 +123, L4 −17 | L4 36/36 (17), L5 18/19 (6) |
| 1000 | 214 | 58 | 9 | L3 −212, L4 +367, L5 +59 | L4 56/56 (39), L5 34/34 (12) |
| 1500 | 401 | 88 | 7 | L3 +178, L4 +66, L5 +157 | L4 64/65 (43), L5 51/51 (24), L6 26/26 (12) |
| 2000 | 491 | 113 | 10 | L3 +26, L4 +1092, L5 −627 | L4 95/99 (66), L5 50/50 (24), L6 36/37 (15) |
| 2176 | 767 | 125 | 11 | L3 +140, L4 +56, L5 +544, L6 +27 | L4 109/110 (76), L5 70/70 (38), L6 43/43 (22) |
| 2500 | 1048 | 140 | 11 | L3 +181, L4 −348, L5 +1215 | L4 105/109 (75), L5 90/90 (51), L6 45/45 (23) |
| 3000 | 734 | 161 | 7 | L4 +394, L5 −17, L6 +357 | L5 103/103 (65), L6 54/55 (25), L7 21/21 (8) |
| 3500 | 917 | 193 | 14 | L4 +1331, L5 −623, L6 +945, L7 −1008, L8 +1552, L9 −1280 | L4 106/116, L5 118/118, L6 68/68, L8 13/13 |
| 4000 | 1206 | 210 | 10 | L4 −2134, L5 +3202, L6 −96, L7 +234 | L4 93/103 (66), L5 166/166 (117), L6 66/67, L7 33/33 |
| 4500 | 1597 | 237 | 17 | L3 +276, L4 −2378, L5 +3395, L6 +588, L7 −284 | L4 123/136, L5 159/159 (115), L6 81/84, L7 53/53 |
| 5000 | 2073 | 264 | 17 | L3 +244, L4 −2557, L5 +4346, L6 +1688, L7 −1648 | L4 73/82 (56), L5 171/171 (126), L6 98/99, L7 40/40, L8 21/22 |
| 5060 | 2557 | 268 | 17 | L3 +130, L4 −1081, L5 +3112, L6 +524, L7 −128 | L4 129/144, L5 173/173 (129), L6 101/102, L7 38/38 |

(`census.csv` beside this brief has all 54 boards, every hundred to 5000 plus 4050, 4176, 4983 and 5060.)  What the
table shows, all *measured*:

1. **The cores are in layers 4 to 8, never layer 3.**  Layer 3 is frame 0, whose GF(2) bound is exact at every root
   and node measured for n ≥ 187 (the anatomy study: 841 cores at 361 roots of 880-1300, all odd, all in frames 1-3;
   and no layer-3 residual at any board of this census from 200 on).  Layer 7 appears at 1800 and regularly from 2700,
   layer 8 from 3500.
2. **Layer 5 (frame 2) carries most of it.**  Its residual is square (members = pool), from 34 members at 1000 to 171
   at 5000, with a growing share listing three or more live factors (35% at 1000, 54% at 2176, 74% at 5000).  Layer
   5's excess is the largest positive term at most boards from 2500 on, often several thousand, offset by a negative
   excess in layer 4.  At search nodes, frame 2 holds 50-83% of the conflicts met and 85-97% of the branchings, and a
   bound exact in frame 2 alone (GF(2) elsewhere) cuts 40 of 45 nodes of gap under 1,000.
3. **Few swaps, large net, across layers.**  H and S\* differ in 7 to 23 numbers each way, yet the excess per layer
   runs to thousands with alternating signs.  At about half the boards from 4000 on, H plays one or two more numbers of
   layer 5 and as many fewer of layer 4.  The layer-4 numbers it does not play stay in the pool of layer 5, where they
   pay for the extra layer-5 moves.
4. **Both sets close layer 5.**  The layer-5 instance is square in H and in S\* alike (at 5000: H 299 members over 299
   factors, S\* 297 over 297; also layer 7).  The bound does not overfill the frame; it fills it with a set whose
   square matrix is nonsingular over GF(2) but not triangular.  A closed frame is playable iff its square matrix has
   exactly one perfect matching (C2).
5. **Repair is by substitution, not deletion.**  Deleting members of the residuals (chosen greedily, layer by layer:
   each time the member whose removal shrinks the residual most) makes H playable with few deletions but heavy ones: at
   5000, 19 deletions worth 37,682 (5 in layer 4, 6 in L5, 5 in L6, 2 in L7, 1 in L8), against a gap of 2,073.  At
   1000, 5 deletions worth 1,948 against 214.  The optimum instead exchanges near-equal numbers so that every core
   breaks.  The bound "dodges" any single constraint the same way, by swapping in a near-equal alternative.
6. **One knot per layer.**  A greedy packing of disjoint minimal cores finds one per layer in layers 5-8 at every
   board sampled: the minimal cores overlap into a single knot (at 5000 layer 5, 37 distinct minimal cores in 40 random
   deletion orders, of 20 members and more, most of 40-70, each with 1.3-1.5 times as many factors as members).
   Layer 4 from about 3500 on is different: three disjoint small cores, which are the templates of Section 2.4.

### 2.3 How it changes with n

| band of n | median gap | gap / n | gap / score (×10⁻⁴) | gap / (PB − ΣU\*) |
|---|---|---|---|---|
| 1000-1999 | 287 | 0.17 | 3.9 | 0.52% |
| 2000-2999 | 680 | 0.26 | 3.4 | 0.46% |
| 3000-3999 | 1,256 | 0.35 | 3.2 | 0.43% |
| 4000-4999 | 1,636 | 0.37 | 2.6 | 0.37% |
| 5000-5999 | 2,982 | 0.55 | 3.2 | 0.44% |
| 6000-6999 | 4,752 | 0.74 | 3.7 | 0.53% |
| 7000-7999 | 4,724 | 0.64 | 2.7 | 0.39% |
| 8000-8999 | 7,268 | 0.83 | 3.2 | 0.44% |
| 9000-9999 | 10,320 | 1.07 | 3.6 | 0.51% |

*(Measured; past 5060 against best-known scores.)*  A power law fitted over 2000-10000 gives gap ∝ n^2.00; the
promotions part PB − ΣU\* is about 7% of the score.  **The parity bound's relative error is a constant, about 3 × 10⁻⁴,
with waves of ±25% a few hundred games long.**  The residual of layer 5 grows roughly linearly (34, 70, 171 members at
1000, 2176, 5000), and its minimal cores from about 25 to 40-90 members, so the gap per unit of core grows with n: each
substitution costs a difference of near-equal numbers, whose scale grows with the numbers.  Conjecture (worth
settling, Section 6): (PB(n) − opt(n))/n² tends to a positive constant near 1 × 10⁻⁴, a "local" constant of the divisor
lattice's top layers, as opt(n)/n² is.  If so, no bound whose relative error is a fixed fraction of PB's can keep proofs
affordable, and the target is a bound whose error grows more slowly than n².

### 2.4 Templates: small cores lifted by large primes

The small disjoint cores of layer 4 at large n are copies of small boards' odd cores multiplied by large primes.  For a
base set B of numbers and primes P₁, ..., P_r, the *lift* is {m·P_i}.  A lifted member m·P lists the hub m (a smooth
number of the layer below, unplayed, shared by every copy) and the fiber factors (m/q)·P.  Three recur (*measured*:
T11 and T14 at 3500, 4500, 5000 and 5060, T23 at 3500, 5000 and 5060, each time with other primes):

| template | members (cofactor × large prime) | members/pool | at 5000 | base |
|---|---|---|---|---|
| T11 | {12, 18, 20, 27, 30}·P₁ ∪ {18, 27, 30}·P₂ ∪ {12, 18, 20}·P₃ | 11/13 | P = 149, 157, 241 (also at 2176: 61, 67, 107) | layer-3 numbers on 2, 3, 5 |
| T14 | {45, 50, 63, 70, 75, 98, 105}·P ∪ the same·P′ | 14/21 | P, P′ = 43, 47 (29/31 at 3500, 37/41 at 4500) | the odd core of board 105 |
| T23 | {28, 42, 45, 50, 52, 63, 70, 75, 78}·59 ∪ {28, 30, 42, 45, 50, 52, 63, 75, 78}·61 ∪ {30, 42, 45, 63, 70}·71 | 23/34 | as shown | the odd core of board 78 |

T11 at 5000 has pool {12, 18, 20, 27, 30} ∪ 149·{4, 6, 9, 10} ∪ 157·{6, 9} ∪ 241·{4, 6}; of its 78 possible payment
sets of 11 factors, 23 receive an odd number of schemes (so it is GF(2)-independent), none exactly one (so it is a
core); the counts are 0, 2, 3, 4 or 5.  *The big knots of layers 5-7 are not templates of this simple kind*: their
minimal cores mix the smooth part (all primes ≤ 23) with fibers of single large primes.  In frame 2 at 3940-4548 the
graph is a smooth core of treewidth at least 9 plus 22-52 fibers (one per prime above √(n/8)) of treewidth at most 3,
joined at 14-21 hubs (16, 24, 36, 40, ...) whose *twin families* {16·p}, {24·p}, ... hold 65-88% of the movers.

### 2.5 What fixed fields and signings see

Per C2 and B5, other fields or signings see some cores.  On the residual blocks of the heaviest sets (*measured*):

* At the roots of 78-1300 (1,055 games with a gap), the heaviest set's residual is dependent over GF(3) with 0/1 entries
  in 412, over GF(5) in 30, GF(7) in 12; with Koszul signs ((−1)^i at x/p, i the index of p among x's primes) in 209,
  39, 27; never over the rationals.  Of 658 square residuals, the integer determinant is ±1 in 408 (plain) and 572
  (Koszul), and ±1 under both in 54%.
* On the census here (44 boards of 1000-5060), each whole residual block of layers 4-8 loses rank at most 2 over
  GF(3), GF(5) or GF(7) under plain or Koszul entries, most of them 0 or 1; the layer-4 blocks, which hold the
  templates, lost rank at 2 of the 44 boards.  A fixed field sees one or two dimensions of a knot that holds dozens of
  minimal cores.
* As bounds, the plain GF(3) signing closed 2% of the gap at n ≥ 1700, plain plus three random signings 9%: the bound
  moves to an alternative the field does not see.  Only signings built for the cores actually met closed much (Section
  4).

## 3. Worked examples

### 3.1 n = 45: an odd core that does not weigh in

Above.  The core {12, 18, 20, 30, 45} is the "theta" shape of the lemma in Section 1.5 (path 10–4–6–9–15 via 20, 12,
18, 45, and the hyperedge 30 = {6, 10, 15}), per = 3, det = 3.  The parity bound is exact at 45 because no heavier set
of the right kind uses it.

### 3.2 n = 78: the first gap

U\* has 31 sources worth 1,859.  opt(78) = 1,991: S\* = U\* ∪ {27, 30, 36, 39}.  PB(78) = 1,992: H = U\* ∪ {28, 30, 36,
39}.  The bound plays 28 = 2²·7 where the optimum plays 27 = 3³, for +1.  In H's layer-3 instance (pool: the layer-2
numbers up to 39 not played), the residual is the odd core K₇₈ = {28, 30, 42, 45, 50, 52, 63, 75, 78} with lists

    28: 4 14     42: 6 14 21    50: 10 25    63: 9 21     78: 6 26  (39 is played)
    30: 6 10 15  45: 9 15       52: 4 26     75: 15 25

As a graph, the two-factor members form two paths, 14–4–26–6 (28, 52, 78) and 21–9–15–25–10 (63, 45, 75, 50), and the
hyperedges 30 = {6, 10, 15} and 42 = {6, 14, 21} tie their ends.  Onto all nine factors it has 5 schemes (odd: GF(2)
independent) and integer determinant 1, so no field with 0/1 entries sees it.  S\* breaks it by not playing 28: then 14
is listed by 42 alone, and peel unravels the knot; 27 takes 28's place at a cost of 1.  Deleting 28 would cost 28; the
optimum substitutes for 1.  Gaps in 78..600 are small and come and go (1 at 78, 18 at 81, 0 at 84, 3 at 105, 24 at 120,
0 at 121, 6 at 192, ..., 4 at 300, 29 at 400, 106 at 600).

### 3.3 n = 105 and 300: two more small cores

* At 105 (gap 3: H plays 45, S\* plays 42) the core is K₁₀₅ = {45, 50, 63, 70, 75, 98, 105} over {9, 10, 14, 15, 21,
  25, 35}: 45: 9 15; 50: 10 25; 63: 9 21; 70: 10 14 35; 75: 15 25; 98: 14 (49 played); 105: 15 21 35.  3 schemes,
  determinant −1.  It is T14's base.
* At 300 (gap 4: H plays 112 = 2⁴·7, S\* plays 108 = 2²·3³) the core is in layer 5: {112, 120, 176, 200, 264, 280, 300}
  over {16, 24, 40, 56, 60, 88, 100}, all two-factor members (112: 16 56; 176: 16 88; 264: 24 88; 280: 40 56; 200: 40
  100; 300: 60 100) on the path 24–88–16–56–40–100–60 plus the hyperedge 120 = {24, 40, 60}: the theta shape, 3
  schemes, determinant −3 (GF(3) sees this one).

### 3.4 n = 2176: a mid-size root

ΣU\* = 1,381,223 (823 sources); opt = 1,494,161 = ΣU\* + 112,938 from 125 numbers up to n/2; PB = 1,494,928; gap 767.
H also plays 125, differing in 11 each way:

| layer | H only | S\* only | excess |
|---|---|---|---|
| 3 | 805 = 35·23 | 665 = 35·19 | +140 |
| 4 | 644 = 28·23, 650 = 50·13, 676 = 52·13, 732 = 12·61, 836 = 44·19 | 636 = 12·53, 666 = 18·37, 686 = 98·7, 690 = 30·23, 804 = 12·67 | +56 |
| 5 | 750 = 150·5, 882 = 126·7, 924 = 84·11, 1072 = 16·67 | 684 = 36·19, 696 = 24·29, 728 = 56·13, 976 = 16·61 | +544 |
| 6 | 756 = 108·7 | 729 = 3⁶ | +27 |

The residual has 109 members over 110 factors in layer 4, 70/70 in layer 5 and 43/43 in layer 6.  One piece is the
template T11 with primes 61, 67, 107 (members 732, 1098, 1647, 1220, 1830 = 61·{12, 18, 27, 20, 30}; 1206, 1809, 2010 =
67·{18, 27, 30}; 1284, 1926, 2140 = 107·{12, 18, 20}).  S\* omits 732, and among the swaps is a *rectangle*: H plays
732 = 12·61 and 1072 = 16·67, S\* plays 976 = 16·61 and 804 = 12·67, for a loss of (16 − 12)(67 − 61) = 24.  The bound
prefers the diagonal that puts the larger cofactor on the larger prime, which completes an odd core; the optimum takes
the lighter diagonal there.

### 3.5 n = 5000: a root at the end of the chain

ΣU\* = 7,312,736 (1,900 sources: 1 prime, 367 of layer 2, 631 of 641 sources of layer 3, every source of layers ≥ 4);
opt = 7,868,316 with 264 numbers up to n/2 (54 of layer 3, 101 of layer 4, 56 of layer 5, 29 of layer 6, 16 of layer 7,
...); PB = 7,870,389; gap 2,073.  H has 264 too, 17 swaps each way.  Layer by layer:

| layer | H only | S\* only | excess |
|---|---|---|---|
| 3 | 1570 = 10·157, 2065 = 35·59, 2355 = 15·157 | 1413 = 9·157, 2135 = 35·61, 2198 = 14·157 | +244 |
| 4 | 1375, 1708, 1715, 1845, 1925, 1935, 2130 | 1521, 1524, 1617, 1647, 1666, 1722, 1770, 1806, 1917 | −2,557 |
| 5 | 1650 = 150·11, 1710 = 90·19, 1755 = 135·13, 2142 = 126·17 | 1372 = 196·7, 1539 = 81·19 | +4,346 |
| 6 | 1400 = 200·7, 1848 = 168·11 | 1560 = 120·13 | +1,688 |
| 7 | 1680 = 240·7 | 1568 = 224·7, 1760 = 160·11 | −1,648 |

Layer instances (members/pool), H against S\*: L3 685/709 and 685/709; L4 533/578 and 535/578; **L5 299/299 and
297/297**; L6 152/153 and 151/155; L7 72/72 and 73/73.  H's residual: L4 73/82 (the three templates: T14 on 43, 47;
T11 on 149, 157, 241; T23 on 59, 61, 71); L5 171/171 with 126 wide members, one knot; L6 98/99; L7 40/40; L8 21/22.
S\* plays all 11 members of T11 and breaks it in the fiber of 157, in layer 3: it plays 1413 = 9·157 (so 4239 =
27·157 lists only the hub 27, and peel unravels the template) and not 1570 = 10·157 or 2355 = 15·157 (so 4710 = 30·157
lists four factors instead of two); H's 1570 + 2355 outweigh S\*'s 1413 + 2198 by 314.  The knot of layer 5 the
optimum breaks by playing two fewer layer-5 numbers and two more of layer 4.  The greedy deletions of Section 2.2 make
H playable at a cost of 37,682.

## 4. What was tried, and why it failed or stalled

Root shares are of the GF(2) (= parity) gap; "constant factor" means the trees shrank by a factor that did not grow
with the gap, so the slope of cost against gap was unchanged.

| idea | result | obstacle |
|---|---|---|
| Franklín–Moniot matching bound (Hall's condition instead of GF(2)) | gap about 10× the parity bound's (1,170 against 130 at ~1000); proofs past 989 stalled at 10⁷-10⁸ nodes | blind to even cores (cycles of two-factor members) |
| **Parity / GF(2) bound** (two-matroid intersection) | the one change of slope in the project's history: log₁₀ nodes +0.14 per 100 n against +0.48; proofs 12-613× smaller at 880-1300; exact on two-factor members | odd cores |
| Lagrangian over learned conflicts (cover cuts Σ_K x ≤ \|K\| − 1) on top of GF(2) | closes 7-36% of the root gap at 936-1300; the LP over *all* conflicts 46%, falling 3.8 points per 100 n; in branch and bound 6.2× fewer nodes, 24% slower; beside the parity bound in the prover: nothing at 990 | a cover cut of a 13-34-member core is weak (the LP keeps (\|K\|−1)/\|K\| of each member), and near-equal alternatives are other cores |
| Rank cuts on unions of tight cuts (exact rank by exhaustion) | with cover cuts: 54% at 880-1300; with the matching LP's cuts too, 66%, residual growing 13.9 per 100 n | unions affordable to check (≤ 26-48 members) do not reach the family |
| Counting cuts (first mover takes all its factors) | not built: valid but dominated by rank cuts | Hall-type surplus: every subset of a core lists more factors than members |
| Lorea's hypergraphic matroid per frame (every subset lists more factors than members) | sees none of the 14 cores at 936-1300 | same surplus |
| Fixed other fields at the root (GF(3), GF(5), GF(7), Q; plain and Koszul) | heaviest set dependent in some field in 54% of games 78-1300; as a bound, plain GF(3) closes 2%, plus 3 random signings 9% | the bound moves to cores the field does not see |
| **Multi-field bound A1**: GF(2) matroids plus GF(3) signings built for the cores the LP meets, coupled by Lagrange multipliers, LP solved with rank inequalities | closes 62% at ≤ 2175, 46% at 17 roots of 2200-3400, falling 3.8 ± 1.1 points per 100 of gap (37-40% at gaps 1,300-1,450); in branch and bound trees 5× smaller at 23 GF(2) nodes' cost each; the tree reduction falls with the gap (slope test killed it); at nodes of gap ≥ 500 it cuts none | cost (tens of seconds a root, 0.1-0.6 s a node); the family is fragmented (57% of cores found cannot be placed in 8 signings a frame); deep nodes meet cores the root never saw |
| **Per-frame exact bound**: Lagrangian decomposition, frames 1-3 solved exactly (their own branch and bound), copies of shared candidates priced | strongest where computable: 15-100% (mean 59%) at 19 roots of 900-1300, 15-39% at 1254-1300 within budget; at nodes cuts 29 and 27 of 30 (GF(2) 20, 14); in branch and bound 2.8× fewer nodes at 28× the time | each frame's exact problem holds the same cores (up to 100,000 nodes a frame); **at the GF(2) split's multipliers the exact frames gain at most 11: all the gain is in re-fitting multipliers**; subgradient stalls |
| **Hybrid bound exact in a few frames** (GF(2) matroids jointly with exact winnability of frame 2, no splitting) | exact in frame 2 alone cuts 40 of 45 nodes of gap < 1,000; frame 3 alone closes 16%, frame 1 25% | computing it costs a median 1.08× the node's own proof; frame 2's local situation recurs at only 3-22% of checks, so nothing to cache |
| The exact problem of frame 2 | a heaviest uniquely restricted matching covering the frame's moves, tied to frames 1 and 3 by GF(2); at 3940-4548 one connected graph of 520-770 vertices, no 4-cycle, cycle rank 264-459; after every fixing the GF(2) bound allows, treewidth ≥ 9-12 | known exact algorithms by treewidth need ~10¹¹-10¹⁵ states a bag; no easy class contains these graphs |
| Flat-cycle (Joswig–Pfetsch) cuts x(C) ≤ \|C\|/2 − 1 on the matching LP, with cover and rank cuts | +0.12 of the gap from the cycles; total 0.34 at roots, 0.40 at nodes, below A1; where separation finished no cycle was violated and 37-78% remained | what remains is not cycle-shaped |
| A conflict's "knot" (its images under twin swaps) imposed as a bound | lowers a node's bound by about one exclusion (66-78 points); would save 0.6-3.6% of steps | the images are many and cheap to dodge |
| Charging each disjoint conflict its cheapest member | 12-20% of the node gap at 3940-4875 | 1.7 disjoint conflicts a frame; the knot is one |
| Lagrangian of symmetric pairs' inequalities (prime exchange c_p ≤ c_q) | ×1.01 nodes | the pairs are the root's, not the node's |
| Multipliers fitted at the root, used at nodes; root cut pools at nodes | 2% of open nodes cut at 2700-3440 (7-10% at 936, 1215); root cuts at root multipliers 1.26× fewer nodes, at node multipliers 4.2× fewer in 1.9× the time | the root's cores are not the deep nodes' cores |
| Refitted Lagrangian (strong bound) at nodes | cuts 92% of open nodes of gap < 50, none of gap ≥ 300; 164-234× the GF(2) bound's cost | strong only where the tree is not |
| Decomposition across frames (AND/OR at a home) | killed: a home touches 8-10 of the 9-16 cores of the heaviest set | no separator |
| A floor on the move count | not a theorem; and would cut 0% at 34 of 35 items | — |
| Forcing members certified by barred parity bounds | the same trees | the parity bound is an exact max; propagation already forces them |

Two readings of this record are worth stating as lessons.

* **Root gaps overpredict.**  Every bound that closed a large share at the root closed less at deep nodes, because the
  nodes meet cores the root never sees, and because the share falls with the gap.  A useful bound must close a fixed
  share at every node at a cost of about a millisecond (the GF(2) bound's), or be strong enough at the root to settle a
  game outright, or to fix most of its variables.
* **The coupling between layers is where integrality is lost.**  Making a layer exact helps a lot when it is coupled to
  the others jointly (the hybrid bound), and much less through a Lagrangian split of the shared elements (the per-frame
  bound), because at the GF(2) split each layer alone can nearly reach its GF(2) value with a playable configuration;
  what is impossible is to do so consistently on the elements two layers share.

**A limit on single-matroid strengthenings (proved here, with measured rates).**  Suppose one tries to replace a
layer's GF(2) block by another matroid M on the same elements that contains every playable configuration (so that the
bound stays a two-matroid intersection).  Fix the pool.  The proper subsets of a minimal core are core-free, hence in
M; so a minimal core is either M-independent or an M-circuit.  If two minimal cores C₁, C₂ sharing e were both
M-circuits, circuit elimination would give an M-circuit inside (C₁ ∪ C₂) ∖ e, which must contain a core.  **So if
(C₁ ∪ C₂) ∖ e is core-free, no such matroid excludes both C₁ and C₂.**  On H's residuals this obstruction is common:
of the (pair, shared member) eliminations tested, 302 of 673 at 600 (layer 4), 157 of 180 at 1000 (layer 5), 720 of
1,865 at 2176 (layer 5), and 841 of 3,285 (layer 5), 877 of 3,704 (layer 6) and 474 of 1,050 (layer 7) at 5000 are
core-free.  A matroid relaxation can therefore exclude only an elimination-consistent subfamily of the cores; GF(2)'s
dependent sets are one such family (the even cores).  This does not rule out a better matroid, but it rules out one
that excludes "all small cores", and it explains why stronger relaxations have been three or more matroids coupled by
multipliers, which brings back the duality gap.

## 5. The data

### 5.1 The gap past 5060, by band of 500

4,940 games: 1,710 searched (below their ceiling), 1,705 at the ceiling n + opt(n − 1), 973 repeats of an earlier
game's problem, 552 primes.  Gap = PB − best-known score.

| band | games | searched | min | 10th pct | 25th | median | 75th | 90th | max | gap/n median |
|---|---|---|---|---|---|---|---|---|---|---|
| 5061-5560 | 500 | 174 | 2,090 | 2,170 | 2,433 | 2,752 | 2,954 | 3,054 | 3,346 | 0.52 |
| 5561-6060 | 500 | 181 | 2,455 | 2,954 | 3,261 | 3,527 | 3,997 | 4,200 | 4,413 | 0.60 |
| 6061-6560 | 500 | 168 | 3,421 | 3,852 | 4,420 | 4,800 | 4,995 | 5,164 | 5,358 | 0.76 |
| 6561-7060 | 500 | 170 | 3,809 | 3,979 | 4,241 | 4,428 | 5,643 | 6,343 | 6,862 | 0.65 |
| 7061-7560 | 500 | 164 | 3,762 | 4,128 | 4,440 | 4,572 | 4,677 | 5,093 | 5,359 | 0.62 |
| 7561-8060 | 500 | 170 | 4,526 | 4,782 | 5,071 | 5,625 | 6,188 | 6,723 | 7,107 | 0.72 |
| 8061-8560 | 500 | 175 | 4,752 | 4,975 | 5,548 | 6,153 | 7,535 | 8,253 | 8,590 | 0.75 |
| 8561-9060 | 500 | 182 | 6,597 | 6,872 | 7,251 | 8,120 | 8,595 | 8,710 | 8,959 | 0.92 |
| 9061-9560 | 500 | 176 | 7,600 | 7,841 | 8,552 | 9,605 | 10,467 | 10,672 | 11,322 | 1.04 |
| 9561-10000 | 440 | 150 | 9,822 | 10,050 | 10,330 | 10,734 | 11,261 | 11,468 | 11,686 | 1.11 |

Over all 4,940: minimum 2,090, 10th percentile 3,046, median 5,177, 90th percentile 10,330.  For comparison, the proven
range: median 1,538 at 4001-4500, 1,793 at 4501-5000, 2,686 at 5001-5500.  The first searched games past 5060 have
gaps 3,049 (5061 = 3·7·241, a rise of 492 over 5060), 3,049, 3,063, ..., 3,346 (5096), then 2,694 at 5140.

### 5.2 Proof cost against the gap (the 1,745 exhaustive proofs of 1..5060)

Nodes are the frame solver's search steps; CPU-hours on an 88-thread two-socket Xeon.

| gap | proofs | median nodes | 10th-90th percentile | most | median CPU-hours |
|---|---|---|---|---|---|
| 0-99 | 287 | 8 | 1 - 114 | 388 | 0 |
| 250-499 | 237 | 9.9 × 10³ | 2.7 × 10³ - 4.6 × 10⁴ | 2.6 × 10⁵ | 0.001 |
| 750-999 | 164 | 2.6 × 10⁵ | 4.3 × 10⁴ - 3.7 × 10⁶ | 1.9 × 10⁷ | 0.03 |
| 1,250-1,499 | 198 | 1.2 × 10⁷ | 1.9 × 10⁶ - 7.3 × 10⁷ | 1.4 × 10⁸ | 1.3 |
| 1,750-1,999 | 71 | 2.2 × 10⁷ | 1.1 × 10⁷ - 1.5 × 10⁸ | 3.8 × 10⁸ | 3.7 |
| 2,000-2,099 | 34 | 1.2 × 10⁸ | 1.2 × 10⁷ - 2.2 × 10⁸ | 2.5 × 10⁸ | 24 |
| 2,100-2,199 | 18 | 5.9 × 10⁷ | 5.1 × 10⁷ - 7.1 × 10⁷ | 9.0 × 10⁷ | 11 |
| 2,200-2,399 | 19 | 4.3 × 10⁸ | 1.7 × 10⁸ - 8.6 × 10⁸ | 1.0 × 10⁹ | 73 |
| 2,400-2,700 | 18 | 9.7 × 10⁸ | 3.9 × 10⁸ - 5.0 × 10⁹ | 6.9 × 10⁹ (4983) | 186 |

Spearman(gap, nodes) = 0.96 over all; 0.96, 0.87, 0.82, 0.84, 0.84 and 0.95 within the thousands 0-999 ... 5000-5060.
The 89 proofs with gap ≥ 2,000 took 8,524 of the 10,149 CPU-hours.  Fits of log₁₀ nodes on the 1,250 proofs with gap ≥
500: 3.85 + gap/476 (residual sd 0.60); 2.77 + 0.180·gap/√n (sd 0.54); −4.29 + 8.46 log₁₀ gap − 4.29 log₁₀ n (sd 0.52,
the best), i.e. nodes ∝ (gap/√n)^8.5.  On 4000-5060 alone, 3.79 + gap/503.  A node cost 0.24 ms at 2000-2500, 0.51 at
4000-4500 and 0.67 at 5000.  So **10⁸ nodes ≈ 20 CPU-hours and 10⁹ ≈ 190** at n ≈ 5000.  Caution: within a narrow
range of n the root gap predicts poorly (games 4900-4929 all had gap 2,048 and took 2.3-4.0 × 10⁸ steps, 4935-4945 had
2,137-2,191 and took 0.8-1.3 × 10⁸): the size is decided by the node gaps below the root.  Earlier builds of the frame
solver grew tenfold per about 250 points over 1301-3312; the whole-board prover's searches of 2..2530 grow tenfold per
201 points (R² 0.88), at several times the cost a node.

### 5.3 What a reduction of the gap buys past 5060

Apply a reduction s to the gap of each searched game past 5060, and count those that land at about 10⁸ nodes (gap ≤
2,100) or 10⁹ (≤ 2,650), the thresholds read off Section 5.2 at n ≈ 5000.  This assumes the bound closes the share s at
every node, so that the tree is that of a game with the smaller gap, and that the cost per node stays near the GF(2)
bound's.  "Reach" is the last game of an unbroken run from 5061 in which every searched game is within the threshold;
ceilings, primes and repeats follow from their predecessors without a search.

| reduction | searched games ≤ 10⁸ (of 1,710) | ≤ 10⁹ | reach at 10⁸ | reach at 10⁹ | ≤ 10⁹ by band of 500 from 5061 |
|---|---|---|---|---|---|
| 0 | 2 | 59 | 5060 | 5060 | 55, 4, 0, 0, 0, 0, 0, 0, 0, 0 |
| 10% | 29 | 142 | 5060 | 5060 | 124, 18, 0, ... |
| 25% | 101 | 272 | 5060 | 5627 | 174, 96, 2, 0, ... |
| 50% | 428 | 880 | 5942 | 6374 | 174, 181, 162, 114, 161, 59, 29, 0, 0, 0 |

If the threshold scales as √n (the better fit), the counts at 50% become 737 and 1,027 and the reach 6159 and 6590;
the picture is the same.  The reduction the median searched game of each band needs to reach 10⁹ nodes (10⁸): 4% (24%)
at 5061-5560, 24% (40%) at 5561-6060, 41-45% (53-56%) at 6061-7560, 53-57% (63-66%) at 7561-8560, 67-75% (74-81%) at
8561-10000.  The worst game of 5061-5560 needs 21%.

### 5.4 Structure in the gap

* **It changes only at searched games** (*proved* for primes, by the prime step: the gap is unchanged; *proved* for
  ceilings, by the parity ceiling: it can only fall; *measured* for repeats, where it is unchanged).  In 2001-5060 the
  gap rose by 2,066 in all: +2,957 at searched games, −891 at 11 ceilings; it is constant across primes (374) and
  repeats (605).  Of 1,083 searched games, 479 left it unchanged, 319 raised it and 285 lowered it; the median |change|
  is 10 and the 90th percentile 121.  In 5061-10000 the rises sum to 11,343 at searched games and −2,432 at 20 ceilings.
  The gap takes only 509 distinct values in 3,060 games of 2001-5060 (runs of equal gap average 5 games, the longest
  36).
* **Which games raise it.**  By the cofactor rule (n divided by its largest prime factor), a game whose cofactor is 1,
  a prime, twice a prime or 9 is a prime, a repeat or at its ceiling, so the gap moves only at n whose cofactor is
  composite (and not 2p or 9): these are the "searched" games.  Among them (3001-10000), odd n with four distinct primes
  raise it most (four prime factors: mean +130, 92% of them positive; five: mean +264, 83%); odd n = pqr raise it in
  only 6% but sometimes by a lot (6573 = 3·7·313 and 6657 = 3·7·317: +764 each; 5061 = 3·7·241: +492); even n with two
  distinct primes and at most five prime factors raise it in 1-3%.  The largest rises: 9900 = 2²3²5²11 (+1,140), 8670
  = 2·3·5·17² (+830), 9405 = 3²·5·11·19 (+782), 9075 = 3·5²·11² (+750), 9555 = 3·5·7²·13 (+688), 8085 = 3·5·7²·11
  (+674).  The largest falls: 9594 = 2·3²·13·41 (−824), 6740 = 2²·5·337 (−808), 6620 = 2²·5·331 (−764), 9744 (−660),
  6528 (−654).
* **Smooth n raise the gap.**  A new number n rich in small primes joins the smooth core of the high layers, where the
  knots are; n = c·P with P a large prime joins a fiber and usually does not.
* **Waves.**  A third of the gap's variance between 2176 and 3312 is predicted out of sample by counts, tier by tier
  (numbers m with n/(k+1) < m ≤ n/k), of numbers with three or more distinct primes (R² 0.31; 0.68 over 1301-3312).

## 6. Open questions and directions

What is known and what is conjecture, then the directions, the four most promising first.

**Known (proved):** W1, W3, the per-layer reading, B5 (GF(3) signings are exact frame by frame), NP-hardness of the
two-rank problem, the parity ceiling, the prime step, the 3-scheme lemma, the matroid-obstruction lemma.  **Measured:**
gap ∝ n² with gap/score ≈ 3 × 10⁻⁴; cores only in layers ≥ 4 for n ≥ 187, mostly layer 5; H and S\* of equal size with
few swaps; layer 5 closed in both; templates T11, T14, T23; the record of Section 4.  **Open:** everything below.

1. **A relaxation of one layer that is used jointly with the others.**  The target is a family 𝓕 between the
   playable configurations of a layer (rows R of layer k and deleted columns D of layer k − 1 leaving a peelable
   matrix) and its GF(2)-independent ones, cheap, and combined with GF(2) on the other layers *jointly*, as the hybrid
   bound is, not through a weight split (at the GF(2) split an exact layer gains nothing).  The prize is known: exact
   in layer 5 alone, the joint bound cuts 40 of 45 nodes of gap under 1,000.  Two forms: (a) 𝓕 a matroid replacing the
   GF(2) block of layer 5, so the bound stays a two-matroid intersection, polynomial and certified by a weight split;
   by the obstruction lemma it can exclude only an elimination-consistent family of cores, and the question is which
   such family is largest on Taxman's layers and whether its independence test is fast; (b) 𝓕 not a matroid, with a
   duality certificate of its own (an LP over 𝓕's hull jointly with the two matroid polytopes, say), which must then be
   computable in milliseconds and must not lose its share as the gap grows.  *Cheap test:* the share of the gap closed
   at the roots of 1000-5000, using the census and templates here.

2. **Templates and local corrections.**  *Conjecture:* the odd cores of the heaviest sets come from finitely many
   patterns of the smooth part (cofactors with small primes) lifted by large primes and joined at hubs, as T11, T14 and
   T23 are; the knots of layers 5-7 are unions of such lifts sharing the smooth core.  If the lifts of a pattern over
   disjoint sets of large primes interact only through hubs whose state the parity bound already decides, the gap would
   be a sum of local terms, each computable exactly once per pattern and range of primes, and a bound "PB minus the
   provable local losses" might be proved by an exchange argument.  The rectangle swap of Section 3.4 is the simplest
   local loss: (m₂ − m₁)(P₂ − P₁).  *Cheap test:* classify the minimal cores of the residuals of 2000-5060 by their
   pattern after dividing out the large primes; measure how much of each root gap the cheapest local repair of each
   pattern instance explains.

3. **The asymptotic constant of the gap.**  Prove or refute that (PB(n) − opt(n))/n² → c > 0, and compute c from a
   local model (Hensley's bounds L_p ≤ C ≤ L_p + 2/p for opt come from p-smooth sub-boards; the same blocks {k·d : d
   p-smooth} may carry the parity bound).  A positive constant would mean that a fixed share of the score is lost to
   odd cores of bounded "shape", and it would say which shapes, hence which corrections a bound needs; c = 0 would say
   the waves dominate and the end of the chain is cheaper than it looks.  The random 3-XORSAT analogy (a 2-core of full GF(2)
   rank exists between densities 0.818 and 0.918) predicts that odd cores are generic in this regime, not accidents.

4. **A bound for the increment instead of the gap.**  The gap changes only at searched games, by a rise that is 0 at
   44-52% of them, with a 90th percentile of |rise| of 121 (2001-5060) and 223 (5061-10000).  A proof of game n from a
   proven game n − 1 needs only an upper bound on opt(n) − opt(n − 1).  The parity bound supplies PB(n) − opt(n − 1)
   = [PB(n) − PB(n − 1)] + gap(n − 1): it carries the whole accumulated gap of n − 1 into the proof of n.  The ceiling,
   the prime formula, the semiprime formula J3 and repeats are *differential* arguments that carry none, and with them
   65% of the games past 2000 need no search; but none is known for an n whose cofactor is composite.  A target: when
   the optimal sets of n − 1 and n differ by n replacing one move x, x has always been the *shadow* of n (n with each
   prime factor replaced by the next smaller prime) for odd n, or n/2 for even n, in all 1,729 such pairs to 4955
   (measured; proved at primes).  A theorem "opt(n) ≤ opt(n − 1) + n − σ(n) under conditions checkable from the frames
   of n", σ(n) the cheapest exchange that makes room for n, would settle those games with no search; no route to one is
   known.

5. **Non-linear invariants of 2-adic type.**  For a closed (square) frame, playable ⟺ per = 1; GF(2) checks per mod 2.
   per mod 4 (and mod 2^k for fixed k) of a 0/1 matrix is computable in polynomial time (Valiant), and the small cores
   above have per = 3 or 5.  Is there a tractable relaxation over sets that uses per mod 4, or a quadratic-form
   refinement of GF(2) rank, that excludes a stable share of odd cores?  A test of the heaviest set alone is easy; a
   bound needs an optimization structure, which is the hard part.

6. **Structured signings.**  B5 says GF(3) signings see every core, but only signings built for the cores met worked,
   and the family fragmented.  Signings modulo diagonal scaling are determined by their values around the cycles of the
   incidence graph; multiplicative signings (σ(x, x/p) = χ(p) for a character χ) are diagonal-equivalent to the plain
   one and give nothing, Koszul signs see 13% of square residuals.  *Conjecture C2 (from the project's agenda):* for
   numbers on three primes, members of degree d + 1 over factors of degree d form a honeycomb, schemes are lozenge
   tilings, and in a region without holes all tilings have one sign, so GF(p) sees such a core exactly when p divides
   its number of tilings.  A rule that predicts the right few signings per template would make a cheap multi-field
   bound.

7. **Symmetry and twin families.**  The bound dodges each constraint by swapping a member for a twin (m·p for m·p′, or
   16·p for 12·p).  A relaxation stated on orbits (aggregate variables for a twin family, with constraints valid for
   every member of the orbit) might not be dodged that way; the knot measurement says imposing one conflict's images
   is worth about one exclusion, so the orbit constraints would have to carry more than conflicts.

8. **An impossibility theorem.**  Show that every LP relaxation formed by a fixed number of matroid polytopes per layer
   (or by cover and rank inequalities of cores of bounded size), coupled through shared elements, has an integrality
   gap of order n² on Taxman, for instance by averaging fractional solutions over twin swaps.  That would explain the
   falling shares of Section 4 and say that only integer reasoning (search, or exactness on a frame jointly) closes the
   gap, which would redirect the effort to making that reasoning cheaper.

## 7. What a useful answer looks like

Any of these would be useful.

* **A new valid upper bound or a tightening rule**, with a proof (weak duality, an exchange argument or a structural
  theorem), an estimate of the share of the gap it removes at n ≈ 5000-10000 and why that share should not fall with
  the gap, its cost to evaluate (and incrementally at a node, after fixing some numbers in and some out), and a
  certificate a separate program can check.  The bar: about 25% at every node for the games just past 5060, 50% to
  reach the 6000s, 75% near 10,000; a node budget of about 1-10 ms.  A root-only bound helps only if it closes nearly
  all of the gap (a game is settled when the bound is at most the best-known score) or fixes most numbers in or out.
* **An argument that a class of approaches cannot help**, such as Section 6, item 8, or a strengthening of the
  obstruction lemma that bounds what any matroid relaxation can exclude.
* **A local theory** of where the gap comes from (templates, the asymptotic constant) that predicts gap(n) from n's
  arithmetic better than the 31% of variance explained so far.

**Cheap checks on small n.**  Everything in Sections 1-3 can be recomputed from the definitions: the parity bound by
weighted matroid intersection over GF(2) bit vectors (an implementation takes 0.25 s at n = 1000 and 8.5 s at 5000 in
plain Python), playability by peel, cores by dismantling.  Validity of a new bound can be checked against opt(n) for
n ≤ 5060; useful values:

| n | opt(n) | PB(n) | | n | opt(n) | PB(n) |
|---|---|---|---|---|---|---|
| 78 | 1,991 | 1,992 | | 900 | 254,657 | 254,776 |
| 81 | 2,105 | 2,123 | | 1000 | 315,426 | 315,640 |
| 105 | 3,434 | 3,437 | | 1100 | 381,834 | 382,012 |
| 120 | 4,593 | 4,617 | | 1200 | 454,985 | 455,186 |
| 300 | 28,691 | 28,695 | | 1300 | 532,268 | 532,419 |
| 400 | 50,437 | 50,466 | | 2176 | 1,494,161 | 1,494,928 |
| 500 | 78,934 | 78,938 | | 4050 | 5,160,836 | 5,161,849 |
| 600 | 112,623 | 112,729 | | 5000 | 7,868,316 | 7,870,389 |
| 700 | 155,113 | 155,135 | | 5060 | 8,053,621 | 8,056,178 |
| 800 | 201,990 | 202,168 | | | | |

The parity bound is exact for n ≤ 77 and at 225 of the 298 boards below 300 (gaps there at most 24); from 300 on only
19 boards are exact, the last 527.  The template cores T11, T14 and T23 at n = 5000, and K₇₈, K₁₀₅ and the 300-core,
are small enough to test any proposed local invariant by hand or by brute force.  A bound that does not see K₇₈
(determinant 1, 5 schemes) will not see much at the end of the chain.

## Files beside this brief

* `parity.py`: the parity bound of n from the definitions (greedy basis of the sources, then weighted matroid
  intersection over GF(2)), the heaviest set, its residual layer by layer, and the comparison with the recorded optimal
  set.  `python3 -I parity.py N ...`.  It agrees with the project's values on every board checked.
* `cores.py`: minimal cores inside those residuals, with sizes, live-factor counts, primes, fiber members, and for
  small square cores the number of schemes and the integer determinant.  `python3 -I cores.py N [K]`.
* `census.csv`: one row per board of the census of Section 2.2 (every hundred from 100 to 5000, plus 4050, 4176, 4983
  and 5060): parity bound, opt, gap, ΣU\*, number of promotions, swaps, the excess by layer (L3-L11, summing to the gap)
  and each layer's residual as members/pool/members with three or more live factors.
