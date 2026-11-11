# Succession: settling game n from game n − 1

*A research brief, written 2026-11-10 for a reader who has only this document.  Its subject: theorems, or provably
correct cheap procedures, that settle game n of Taxman from a proven game n − 1, for the games that no current rule
settles.*

## 0. The question in one page

Taxman on 1..n: the player takes a number that still has a proper divisor on the board, and the taxman takes all its
remaining proper divisors; at the end the taxman takes what is left.  opt(n) is the best score.  Games 1..5060 are
proven optimal by an exact branch and bound, the frame solver (past 2531 given statement U, Section 1.3).  Past 5060, to
10,000, there are only best-known games (the highest found, none proven) from a heuristic mode.  The objective is
excellent games to 10,000 and a claim that a very high share of them are optimal.  Exact proofs past 5060 are mostly out
of reach: a proof's cost grows about tenfold per 476 points of the root's gap (the parity bound less the score), and the
gaps past 5060 run from 2,090 to 11,686.  The recent attempts to make the search itself cheaper have failed (Section 4).

**The question.**  Find theorems, or provably correct cheap procedures, that settle game n from a proven game n − 1 (its
score, its optimal sets, the by-products of its proof) for games no current rule settles, or that bound
opt(n) − opt(n − 1) tightly enough that the search of n becomes cheap.  Settling n means proving its *shortfall*
δ(n) = opt(n − 1) + n − opt(n) below the *ceiling* opt(n − 1) + n.  In a chain of proofs each such rule makes a searched
game free once the game before it is proven (a proof of 5260 is running; the block 5216-5279 has the smallest gaps past
5060).  For the claim it turns "n is likely optimal" into "n is optimal if n − 1 is".

**What the data say** (Section 5):

1. **The cost does not lie close below the ceiling.**  The 1,745 searched games of 2..5060 took all 10,149 CPU-hours of
   the chain.  Those within 100, 300 and 1,000 points of their ceiling hold 2.6%, 25.2% and 30.2% of that CPU (15.2
   points of the 25.2 are two games); 70% lies 1,001 to 3,000 below.  The median δ is 0.32 n.  A slightly sharper
   ceiling would settle almost nothing: a rule must find δ(n) itself.
2. **Three kinds of step need searches**, told apart by how the kept sources U\* change: *relaxations* (even n whose
   half was a kept source; 61.8% of the CPU), *restrictions* (odd n that takes a spare factor of its frame, a freedom;
   28.3%) and *exchanges* (odd n that displaces one kept source, always its shadow, n with each prime replaced by the
   prime below it; 10.0%).  Past 5060 they are 1,096, 429 and 185 of the 1,710 searched games.
3. **Two kinds of exact law fit the data and are unproven.**  At every exchange δ(n) is the displaced source (1,074 of
   1,074 in 2..5060, and the 185 searched past 5060); the semiprime formula J3 proves it in layer 2 only.  And
   δ(8P) = 4P₁, δ(12P) = 6P₁ (P the largest prime of n, P₁ the prime before it) at every searched game of these
   cofactors from 205 to 5060 (and at 148 of 152 past 5060).  Together they are 14.9% of the chain's CPU and 337 of the
   1,710 searched games past 5060.
4. **The parity bound's own increment predicts δ** with rank correlation 0.99 (equal in 43% of the searched games,
   within 100 in 91%), but the gap can fall from n − 1 to n (at 466 searched games), so the inequality a proof would
   need is false in general.
5. **The single-loss rule** (n − 1's optimal set plus n, less its smallest move that makes it playable) holds at 598
   searched games (30.9% of their CPU) and misses by a median of 180 points at the others.
6. **Reusing n − 1's search** in any form measured (trees, nogoods, joint search, replay) lost or saved little; the one
   thing carried in full is the ceiling (Section 4).

Sections 1 and 2 give the game, the model and what changes from n − 1 to n; Section 3 every existing rule, with its
proof idea and share; Section 4 what failed; Section 5 the tables; Section 6 worked examples; Section 7 open directions;
Section 8 what a useful answer looks like; Section 9 the files.  Facts are marked *proved* or *measured*.

## 1. The game and the model

### 1.1 The game

The *board* of game n is {1, ..., n}; the *pot* starts as the whole board.  A *move* takes a number x still in the pot
that has at least one proper divisor still in the pot.  The player scores x, and the *taxman* takes every proper divisor
of x still in the pot (the move's *tax*).  When no number in the pot has a proper divisor in it, the game ends, and the
taxman takes the rest.  The *score* is the sum of the moves, and opt(n) is the best score (OEIS A019312).  Example:
game 6 has the optimal game 5, 4, 6 (the taxman takes 1, then 2, then 3), so opt(6) = 15.  opt(5060) = 8,053,621, about
0.315 n².

Notation, fixed throughout.  Ω(x) is the number of prime factors of x with multiplicity, its *layer* (Ω(12) = 3).
mf(x) = {x/p : p prime, p | x} are the *maximal factors* of x (mf(12) = {4, 6}; a prime's is {1}).  A *source* is a
number above n/2: it divides no other number of the board, so it is never tax.  A *factor* is a number up to n/2.  q(n)
is the largest prime at most n.  For a set S, ΣS is its sum and S_k its members of layer k.  A set S ⊆ {2, ..., n} is
*playable* (on board n) when some game plays all of its members; an *optimal set* is the set of moves of an optimal
game.  The *ceiling* of game n is opt(n − 1) + n, and

    δ(n) = opt(n − 1) + n − opt(n)

is the *shortfall* of game n below its ceiling.  It is the number this brief is about: settling game n from game n − 1
means proving the value of δ(n).

**Lifting lemma (proved).**  x can be played exactly when some member of mf(x) is in the pot.

### 1.2 Playability

The *own instance* of a set S has *members* S and *pool* (∪_{x∈S} mf(x)) ∖ S.  Member x *lists* L(x) = mf(x) ∖ S.  A
*payment scheme* gives each member a distinct factor it lists, pay(x) ∈ L(x).  Its *precedence* is the digraph on S with
an edge a → b (a ≠ b) when pay(a) | b or a | b: a must come before b.

* **Theorem P2 (playability).**  S is playable iff some payment scheme has an acyclic precedence; every topological
  order of it is then a game playing S.
* **Lemma P3 (flat cycles).**  Every cycle of a precedence lies in one layer, and on each of its edges a → b, b lists
  pay(a).
* **Theorem F3 (layers).**  S is playable iff every *layer instance* is: members S_k, pool the numbers of layer k − 1 up
  to n/2 that are not in S.  So a number y ≤ n/2 of layer j is either a move (a member at layer j) or a factor (in the
  pool at layer j + 1), never both, and the layers couple only through that choice.
* **Peel, Theorem P4.**  A *front move* pairs a member that lists one live factor with that factor; a *back move* pairs
  a factor listed by one live member with that member; each removes the pair.  An instance is playable iff some
  (equivalently every) run of peel pairs every member.
* **Cores, Theorems P5 and P7.**  A *core* is a nonempty set T of members in which every factor listed by a member of T
  is listed by at least two members of T.  Deleting members that list a factor no other remaining member lists leaves a
  *residual* that does not depend on the order; it is the union of every core, and S is playable iff it is empty.
* **Exclusion, Theorem P8.**  If S ∖ E is playable in an instance with its pool fixed, so is S ∖ (E ∩ R), R the
  residual: a minimal set of members to give up lies in the residual.  On the board the pool is not fixed: giving up a
  move y ≤ n/2 of layer k − 1 returns y to the pool at layer k, which can break a core there.
* **Independence, Lemma P10.**  The lists of a playable set are linearly independent over GF(2).  An *odd core* is a
  core whose lists are independent too (the first is {12, 18, 20, 30, 45} on board 45); odd cores are what make the
  parity bound below exceed opt(n).

Playable sets are closed under removal: a subset of a playable set is playable.

### 1.3 The frame model

The *frame solver* works in a reformulation whose words this brief uses.

* **Frames.**  The *frame graph* joins each source to its maximal factors; a *frame* is a component (sources of one
  layer k and the factors of layer k − 1 that can pay for them).  A frame's *freedoms* are its factors less the sources
  it keeps; a frame with none is *closed*.
* **U\*.**  *Descending greedy* takes the sources from n down and keeps each that is playable with those kept.  U\* (or
  U\*(n)) is what it keeps; ΣU\* is called *in_the_bag*.  Among the sources, U\* is also the greedy GF(2) basis of their
  maximal-factor vectors wherever conjecture (♦) holds (checked in every game to 100,000).
* **Bottom layers, Theorems F4 and F10 (proved).**  Every optimal set plays q(n) and no other prime, and exactly U\*_2
  among the sources of layer 2.  From n = 187 on, layer 2 is one closed frame and no optimal set plays a number of layer
  2 up to n/2.  So from 187 on the action is in layers 3 and up.
* **Promotions.**  The model fixes the sources to U\* and asks which factors to *promote* (play as moves).  A *promotion
  set* is an L ⊆ {2, ..., ⌊n/2⌋} with U\* ∪ L playable (the exactness theorem X7); a *candidate* is an x with U\* ∪ {x}
  playable.  P\*(n), or P\*(Π_n), is the heaviest promotion set's sum.  The frames with freedoms are numbered by layer
  (*frame h*); a promoted number of layer k leaves the factors of the frame of layer k + 1 and becomes a move of the
  frame of layer k, one frame forward.
* **The root problem Π_n** is what setup hands the search: the frames with freedoms, their moves and factors, the
  candidates with their home frames, and the limit on the number of promotions.  Two games with equal root problems have
  the same promotion sets and the same P\*.
* **Statement U** (open; proved at every game the whole-board prover has proved, to 2531): some optimal set of n
  contains all of U\*(n) in layers 3 and up.  **Corollary X8:** ΣU\* + P\* ≤ opt(n), with equality iff U holds at n.
  The frame solver's scores past 2531 rest on U; the rules of this brief are wanted with or without it (say which).

### 1.4 The parity bound

Split the coordinates 1..⌊n/2⌋ into blocks by layer.  For x of layer k, v(x) is its maximal-factor vector over GF(2) (in
block k − 1) and e_x the unit vector of x if x ≤ n/2 (in block k).  The *parity-i vector* of x is v(x) if Ω(x) ≢ i (mod
2), e_x if Ω(x) ≡ i and x ≤ n/2, and a private coordinate if Ω(x) ≡ i and x > n/2.  A set is *independent at both
parities* if its parity-0 and its parity-1 vectors are each independent.  These define two linear matroids M₀ and M₁ on
{2..n}.

* **Theorem W1 (parity bound).**  A playable set is independent at both parities (it is P10, read block by block).  So
  PB(n), the heaviest common independent set of M₀ and M₁, is at least opt(n).  It is a weighted matroid intersection,
  computed in seconds at n = 5000, and the frame solver's root bound equals it at every board measured (2..10,000).
* **The parity ceiling (proved).**  PB(n) ≤ PB(n − 1) + n.  **The prime step (proved).**
  PB(p) = PB(p − 1) + p − q(p − 1), as for opt.
* **The gap** of game n is PB(n) − opt(n), and **δ_PB(n)** = PB(n − 1) + n − PB(n) ≥ 0 is the parity bound's own
  shortfall below its parity ceiling: computable exactly, in polynomial time.  The identity

      δ(n) = δ_PB(n) + rise(n),   rise(n) = gap(n) − gap(n − 1),

  holds by definition.  Where the gap does not change from n − 1 to n, the parity bound's increment is the game's.

### 1.5 The search and what it costs

The frame solver is a branch and bound over promotion sets.  A node fixes some candidates in and some out, its bound is
the parity bound with those choices (about 1 ms a node), and it is cut when the bound is at most the incumbent;
otherwise it branches on the members of a *conflict* (a minimal unpromotable subset of its heaviest independent set),
which it learns as a *nogood*.  Three things come from game n − 1:

* **The seed.**  The search starts from the best of the greedy set, a rounding of the root's matching, and the
  *survivors* of n − 1's promotions (those still candidates and promotable, largest first), improved by a local search.
* **The ceiling.**  The promotion sum n + opt(n − 1) − in_the_bag(n) is a proven bound; reaching it ends the search.  It
  never cuts a node, since a node is cut only at or below the incumbent, which stays below the ceiling until the end.
* **The near-repeat cut** (Section 3.6).

A proof's cost is set by the root's gap.  Over the 1,745 searches that proved games of 1..5060, the rank correlation of
the gap with the node count is 0.96, and the cost grows about tenfold per 476 points of gap.  At the end of the chain
the gaps are 2,300 to 2,600 and a dear game costs 100 to 1,100 CPU-hours.  Past 5060 the gaps of the best-known scores
run from 2,090 (in the block 5216-5279) to 11,686, with a median of 5,211 among the games that need a search.  Six
attempts to carry root-bound work into the search failed this month (Section 4.5), and the search is hard to improve;
that is why rules that skip it matter.

## 2. What changes from game n − 1 to game n

### 2.1 The price of room for n

**Proposition A (proved here, from the lemmas of Section 3).**  For n ≥ 2, call a set T of board n − 1 *open to n* when
T is playable on board n − 1 and T ∪ {n} is playable on board n.  Then

    opt(n) = n + max{ΣT : T open to n},   so   δ(n) = opt(n − 1) − max{ΣT : T open to n}.

*Proof.*  Every optimal game of n plays n (monotonicity N3 for composite n, the prime lemma N1 for prime n), and its
moves less n are playable on board n − 1 (the ceiling lemma N4).  Conversely T ∪ {n} is a game of n.  ∎

So δ(n) is the price, in game n − 1, of keeping room for n: game n − 1 loses δ(n) points from its optimum when it must
leave a way to play n.  By the layer theorem F3, only the layer instance at k = Ω(n) decides whether a playable T is
open to n: n joins the members T_k, against the pool of layer k − 1 numbers up to n/2 outside T.  n is paid by one of
its maximal factors, which must not be played, and must not be taken first as tax by another move.

Two cheap upper bounds on δ(n) are proved:

* **Even n: δ(n) ≤ n/2.**  The number s = n/2 divides no other number of board n − 1, so it is never tax there.  Drop it
  from an optimal set of n − 1 (if it is there) and play n last, paid by s.  If an optimal game of n − 1 leaves s out,
  δ(n) = 0 (the half lemma N7).
* **Any n: δ(n) ≤ x_min(n)**, the *single-loss rule*'s loss: x_min is the smallest move x of the recorded optimal set M
  of n − 1 such that M ∪ {n} ∖ {x} is playable (0 if M ∪ {n} is).  That set is playable, so its score is a lower bound.

No cheap lower bound on δ(n) is known besides δ(n) ≥ 0 and the exact rules of Section 3.

### 2.2 Four kinds of step

How U\* changes from n − 1 to n sorts every composite n into four kinds, read from ΣU\*(n) − ΣU\*(n − 1) (the two
readings, by sums and by the sets of the arrival study, agree on all 8,189 boards 3..8191).  The counts are of the
proven games 2..5060 and of the best-known games 5061..10000 (Section 5 has the tables and their sources):

| kind | what n does | U\*(n) | promotion sets | 2..5060: ceiling / repeat / searched (CPU share) | 5061..10000: ceiling / repeat / searched |
|---|---|---|---|---|---|
| half-out | n even, n/2 ∉ U\*(n − 1) | U\*(n − 1) + n | the same problem (half law) | 1,136 / 0 / 0 | 1,118 / 0 / 0 |
| exchange | n odd, displaces a source x | U\*(n − 1) − x + n | a frame swaps one move | 0 / 995 / 79 (10.0%) | 0 / 973 / 185 |
| restrict | n odd, takes a freedom | U\*(n − 1) + n | Prom(Π_n) ⊆ Prom(Π_{n−1}) | 278 / 0 / 497 (28.3%) | 331 / 0 / 429 |
| relax | n even, s = n/2 ∈ U\*(n − 1) | U\*(n − 1) − s + n | Prom(Π_{n−1}) ⊆ Prom(Π_n) | 216 / 0 / 1,169 (61.8%) | 256 / 0 / 1,096 |

Primes (677 and 552) are a fifth kind, settled by the prime formula; twelve trivial boards make up the rest of 2..5060.

* **Exchange.**  In every exchange step measured, x is the *shadow* of n: n with each prime factor replaced by the prime
  just below it (the shadow of 4953 = 3·13·127 is 2·11·113 = 2486).  In every one of the 79 searched exchange steps of
  2..5060, and the 185 of 5061..10000 by the best-known scores, P\* did not change: δ(n) = x.  The parity bound does not
  change either: rise(n) = 0 in all 79.  Over GF(2) the step is invisible: given (♦), x is the smallest member of the
  circuit of v(n) in U\*(n − 1) (J1), so U\*(n) spans what U\*(n − 1) spans, and a set independent with one is
  independent with the other.  The game sees the difference only through odd cores.  In layer 2 (odd semiprimes) the
  semiprime formula J3 proves δ(n) = x; the searched exchanges of 2..5060 are in layer 2 below 189 (51, 111, 119, 141,
  183, 185) and layer 3 from 741 on.
* **Restrict.**  n odd takes a freedom of its frame and U\* gains n alone.  Every promotion set of n is one of n − 1
  (delete n from the game, N4; the numbers up to n/2 are the same), so the ceiling as a promotion sum is P\*(n − 1), and
  δ(n) = P\*(n − 1) − P\*(n), the fall of P\*.  **Theorem D(b)** (October study, proved): the proof of n has to refute
  exactly the promotion sets of n worth more than P\*(n), and they all lie in the band (P\*(n), P\*(n − 1)] of sets of
  n − 1, about which the proof of n − 1 claimed nothing.
* **Relax.**  n even with s = n/2 ∈ U\*(n − 1): s leaves the moves of its frame (frame h) and becomes a factor and a
  candidate of the frame of n (frame h + 1), and n is a new move that s can pay for.  Every promotion set of n − 1 is
  one of n (s is listed by n alone), so P\*(n) ≥ P\*(n − 1) and δ(n) = s − (P\*(n) − P\*(n − 1)) ∈ [0, s].  A promotion
  set of n that holds s is, less s, a promotion set of n − 1, which bounds it only by P\*(n − 1) + s.  **Theorem D(a)**
  (proved): once the incumbent reaches P\*(n − 1), every set the proof of n must refute is unpromotable in n − 1.  s is
  no candidate of any earlier game.

**The node-level facts** (the widening study, 2026-10-22, on the 49 searched games of 4548-4917): in a restriction,
every node's completions are promotion sets of n − 1, but n − 1 bounds them only by P\*(n − 1), above anything n can
reach; in a relaxation, the freed s is a promotion or a candidate at every node examined.  So the near-repeat cut
(Section 3.6) reaches only the exchanges, the one kind where the incumbent can reach P\*(n − 1).

## 3. The rules that settle game n from game n − 1

Of the 5,059 proven games 2..5060, 677 are settled by the prime formula, 1,630 by the ceiling, 995 as repeats below the
ceiling, 12 are trivial, and 1,745 needed a search, which took all of the chain's 10,149 CPU-hours (Table 1).  Past
5060, by the best-known scores, 552, 1,705, 973 and 1,710 of 4,940 (Table 2).  The rules, with what each rests on:

### 3.1 The prime formula (N5, proved on the whole board)

For a prime p ≥ 3, opt(p) = opt(p − 1) + p − q(p − 1), and T ↦ (T ∖ {q(p − 1)}) ∪ {p} maps the optimal sets of p − 1
onto those of p.  *Proof idea:* an optimal game opens with the largest prime and plays no other (the prime lemma N1: a
prime takes only 1, so it is legal only as the first move, and q(n) divides nothing else since a prime lies in (n/2,
n]); the two primes q(p − 1) and p are indistinguishable to the rest of the game, so exchanging the first move maps
games to games both ways.  Settles 677 of 2..5060 and 552 of 5061..10000.

### 3.2 The ceiling (N4) and the step theorem (N6), proved on the whole board

opt(n) ≤ opt(n − 1) + n: deleting the move n from a game of n leaves a game of n − 1, since n is nobody's tax and
deleting a move only leaves more in the pot.  **Step theorem:** game n is at its ceiling iff some optimal set of n − 1
stays playable with n added, and then the optimal sets of n are exactly those T ∪ {n}.  A test of one optimal set of
n − 1 can miss the ceiling where n − 1 has several (685 has three, and two stay playable with 686).  The chain settles a
game at its ceiling when its start finds a set there: 490 games by the start, 4 by a short search, 1,136 as repeats at
the ceiling.  In all, 1,630 of 2..5060 (32%), and 1,705 of 5061..10000 by the best-known scores.

### 3.3 The half lemma (N7, proved) and the half law (measured)

For even n, if some optimal game of n − 1 does not play n/2, then δ(n) = 0: n/2 divides no number of board n − 1 but
itself, so it stays in the pot, and n follows the last move.  Given U at n − 1, the game made from a heaviest promotion
set plays U\*(n − 1) and promotions up to (n − 1)/2, so it leaves n/2 out exactly when n/2 ∉ U\*(n − 1).  **The half
law** (measured on every even board to 8190 but 14): game n poses the root problem of n − 1 iff n/2 ∉ U\*(n − 1).  These
are the 1,136 half-out games of 2..5060, all at the ceiling.

### 3.4 Repeats (the repeat lemma R6, the arrival lemma J1 and its corollary J2)

Game n is a *repeat* of game m when their root problems are equal; then P\*(n) = P\*(m), and given U at n,
opt(n) − ΣU\*(n) ≤ opt(m) − ΣU\*(m), with the same promotion set optimal in both.  **J1** says when it happens: if the
frame of game n that holds n is closed (and closed without n, for odd n; for even n, the frames that hold the maximal
factors of n/2 are closed too), then Π_n = Π_{n−1}; for odd n given (♦), U\*(n) = U\*(n − 1) + n − x with x the smallest
member of the circuit of v(n), and for even n U\*(n) = U\*(n − 1) + n.  *Proof idea:* the root problem sees only frames
with freedoms, and n changes only the frames it joins, which the hypotheses keep closed.  **J2:** in layer 2 the
hypotheses need no conjecture.  **The cofactor rule** (measured from 188 on; its first case is J2): with c the cofactor
of n (n over its largest prime factor), c = 1 (n prime) gives the prime formula, c prime or twice a prime a repeat, and
c = 9 the ceiling.  The repeats are the 995 exchange games below the ceiling (every repeat below the ceiling is an
exchange) and 1,136 half-out games at it; they rest on U.

### 3.5 The semiprime formula (J3, proved on the whole board, no U)

For odd n with two prime factors that closes a cycle with U\*_2(n − 1) in the graph G_n (vertices: the primes up to n/2
and a ground vertex g; edges: the numbers of layer 2, pq as p–q and p² as p–g), with x the smallest other member of that
cycle: opt(n) = opt(n − 1) + n − x, and S ↦ (S ∖ {n}) ∪ {x} maps the optimal sets of n onto those of n − 1.  The
hypothesis holds for every odd n ≥ 189 with two prime factors.  *Proof idea:* F4 fixes layer 2 of every optimal set
(U\*_2 and no number of layer 2 up to n/2 from 187 on), and an exchange of x for n inside a forest of G_n changes no
other layer instance (n and x are both in layer 2, and the numbers up to n/2 are the same on both boards).  It is the
template for an exchange rule: an exchange inside one layer instance whose optimal part is fixed.  971 games of
189..5060 and 947 of 5061..10000; the prover uses it in place of 176 searches of 1301-2175.

### 3.6 The near-repeat lemma (R7, proved, node by node)

A search of n may end a node once the incumbent reaches a proven bound Z ≥ P\*(Π_m) of an earlier game m, if every
remaining candidate is a candidate of Π_m with the same home, the node's promotions are a promotion set of Π_m, and on
every frame the node's candidates touch, m's moves are among n's and n's extra factors pay for no move of m's frame and
no remaining candidate.  Then every completion is a promotion set of Π_m.  The chain uses m = n − 1.  It reaches only
the near repeats, the exchanges, since only there does the incumbent reach P\*(n − 1).  Measured: a one-move swap (4901)
is cut at 74.8% of its units and 4693 is proven in 30 steps against 572,354; a *factor swap* (4899: the moves
2546 = 2·19·67 and 3819 and their private factor 1273 give way to 3266, 4899 and 1633 = 23·71), which acts as one move
with four payers, is cut at none; over the chain the near repeats hold 6.0% of the searched steps.

### 3.7 Bounds carried between games

Lower bounds are games: monotonicity N3 extends a finished game of n − 1 to n; N4 cuts a game of n down to n − 1 losing
at most n; N5 exchanges the first move at a prime; R6 carries a promotion set to a repeat.  Upper bounds pass from n − 1
to n by adding n (N4), from n to n − 1 unchanged (N3), across a prime by N5, to an odd semiprime by J3, and to a repeat
by R6 (which needs U at n).  So a proof of n − 1 gives game n the bound opt(n − 1) + n and nothing finer, except at a
prime, a semiprime or a repeat.

### 3.8 Measured laws and heuristics (none settles a game)

* **The shadow law** (measured): if the optimal sets of n − 1 and n have the same promotions and differ by one move x
  given up for n, x is the shadow of n (odd n) or n/2 (even n).  True at all 1,729 such swaps of 1..4955.
* **The exchange law** (named here, measured): at every exchange step δ(n) = x, the shadow; 1,074 of 1,074 in 2..5060
  (995 repeats, 79 searched), and the 185 searched exchanges of 5061..10000 by the best-known scores.  Proved in layer 2
  (J3) and, given U, at repeats.  Open in layer 3, where the 79 searched exchanges hold 10.0% of the chain's CPU.
* **The single-loss rule** (Section 2.1) is optimal at 3,829 of the 4,954 games 2..4955 (77%), short at 1,125, from
  n = 21 on and in every thousand (19% to 25%).  At 178 of the 181 violations that can be settled, no optimal set of
  n − 1 meets the rule: an optimal game of n gives up several heavier moves and takes lighter ones (median 3 dropped, at
  most 20, the drops outweighing the additions besides n by exactly δ(n)).  It stays false with the extra condition that
  nothing more fits (77, 81, 84 are violations of that form).
* **The wiki's procedure** (insert n into n − 1's game before the move that would take its last divisor) skips at most
  one move and is optimal at 45% of 2..1000.  An older reuse with a looser test recorded seven scores too low (621-623,
  676-679) until 2021: no rule of this brief may rest on a recorded game without a proof.

## 4. What was tried, and why it failed

Every item below is measured in the project's lab notebook; the study should not propose them again without a new idea.

### 4.1 Reusing n − 1's search in n's (October 2026)

* **The trees do not repeat.**  Over fourteen consecutive pairs of searched games of 1460-2172, the share of n's steps
  taken at nodes that n − 1 also visited has a median of 0.15%: 100% for the two near repeats, 5% to 39% where P\* moved
  by 8 to 296, 0.2% or less where it moved by 179 to 714.  At a fixed level a restriction pair (1472→1475) shares the
  root and nothing else.
* **Theorem D** (Section 2.2) is why: across a relaxation every set n must refute is unpromotable in n − 1; across a
  restriction n's obligation is the band (P\*(n), P\*(n − 1)], which n − 1's proof never examined.  A value fact of
  n − 1 settles a subtree of n only with a margin of P\*(n − 1) − P\*(n).  The one value fact that carries in full is
  the ceiling.
* **Nogoods carried** (a conflict set of n − 1 that is still unpromotable from n's root, checked in microseconds, valid
  without a check across a restriction): 59% to 100% stay valid and they answer most lookups, yet the search ran ×1.31
  slower in geometric mean over 8 pairs (×0.90 to ×2.74), because they change which conflict a node branches on.
* **Perfect reuse is worth little.**  With every piece of work reused, a run of games costs its dearest member.  Over
  the 400 exhausted searches of 2176-3312, cutting runs where the gaps differ, the total over the sum of the runs'
  dearest is 1.22 (equal gaps), 1.29 (within 10), 1.41 (within 50): a saving of 18% to 29%.
* **Joint search, replay, aspiration.**  A joint search of a run is exact but costs the sum of disjoint trees; a replay
  of a near repeat saves only strong branching where the trees differ; a start from a floor at P\* − 1 saves 11-12%.
* **What does carry** is bound state that is not a value (signings and multipliers of a GF(3)-signed bound, valid in any
  game).  That improves a bound; it does not settle games.

### 4.2 Bounds from games above n (October 2026)

A game m > n bounds n only through a relaxation of n's search problem, whose root bound is never smaller than n's own
(none of 972 relaxing pairs of 2..1300).  Of 416 exhausted games of 1..1300 only 1023 can be derived from above (from
1024), 0.55% of the nodes.

### 4.3 A floor on the move count (October 2026)

If "some optimal game of n has at least as many moves as the game of n − 1" were a theorem, a search could demand at
least F promotions.  Measured on 35 searches: it cuts nodes in one (4176: 13.8% of the steps) and saves nothing in the
others, since at nearly every bound check the heaviest set already has the members the floor asks for.

### 4.4 Widening the near-repeat cut (October 2026)

On the 49 searched games of 4548-4917: restrictions hold 69.1% of the steps, relaxations 19.2%, relaxations measured
from n − 2 across a prime 8.8%, near repeats 2.4%.  No reference game can reach the first two kinds (Section 2.2).  In a
relaxation, n's optimum holds s at every step measured (and at 1,133 of the 1,169 searched relaxations of 2..5060), and
is, less s, a set of n − 1 worth s − (P\*(n) − P\*(n − 1)) below n − 1's optimum (6 at 4900, 572 at 4880, 1,554 at
4884): n's proof is about a band of n − 1's sets that n − 1's search pruned whole.  For factor swaps, sound widenings of
the cut changed nothing, no renaming of the swapped numbers was found at any unit, and half the units of 4899 hold a
promotion set of 4899 that is not one of 4898.

### 4.5 Root work carried into the proof search (2026-11-10)

A tighter root bound (the smooth bound, which also asks the smooth numbers of each layer to be playable among
themselves) closes 839 of the 1,940 points of 4848's gap.  Six ways of using it inside the search all lost: the root's
cores as nogoods cut the steps to 0.87 times and raised the CPU to 1.66 times; barring smooth members of mixed
conflicts, 0.88 and 1.06 times; hub-ownership branching doubled the branchings.

### 4.6 The corner of a near repeat (sketch, October 2026, not a lemma)

For a one-move swap (m of n − 1 given up for n), a promotion set of n that leaves some *payer* of m (a maximal factor of
m) in the frame at the end of a winning order is a promotion set of n − 1 (play the order without n, then m last), so it
is worth at most P\*(n − 1).  The proof of n then needs to refute only the sets that use up every payer of m.  At 4953
the payers are 22 (it pays for 48 numbers), 226 (8) and 1243 (2); the new move's are 39 (31), 381 (6) and 1651 (2).  Not
proven with care, not built, not measured.  Twenty-one of the 67 searched odd swaps of 1..4955 are of one kind, 2·11·p →
3·13·q with q the prime after p (741, 1209, 1833, 2301, 4953, ...), and there n's search repeats n − 1's to within 11%
of its nodes.

### 4.7 Proofs of single games past 5060 (2026-11-10)

Standalone proofs (no seed, no ceiling, no near-repeat cut) of 5304 and 5260 ran 2.65 and 2.79 hours of 16 threads and
did not finish; 5264 was stopped at 0.56 hours.  Each search reached its best-known score within 14 minutes and found
nothing above it: what is left is the proof.  A proof of 5260 is running now.

## 5. The data

Sources: `settle_out.txt` (Tables 1 and 2) and `analyze_out.txt` (Tables 3 and 4), made by the scripts of Section 9 from
the committed results (games 2..5060, proven; CPU is each line's `seconds.cpu`) and the gap dashboard's games.csv (made
2026-11-09; past 5060 its scores are best-known, and the running unsound mode has raised a few since).

### Table 1: how the proven games were settled

A game's *outcome*: *prime* (proof kind prime_formula), *ceiling* (score = opt(n − 1) + n, whatever the proof kind),
*repeat* (proof kind same_search, below the ceiling), *searched* (proof kind exhausted, below the ceiling), trivial
(boards with nothing to search).

| n | trivial | prime | ceiling | repeat | searched | CPU-hours |
|---|---|---|---|---|---|---|
| 2-1000 | 12 | 168 | 323 | 185 | 311 | 0.0 |
| 1001-2000 | 0 | 135 | 309 | 205 | 351 | 0.4 |
| 2001-3000 | 0 | 127 | 321 | 195 | 357 | 57 |
| 3001-4000 | 0 | 120 | 310 | 203 | 367 | 940 |
| 4001-4500 | 0 | 60 | 175 | 100 | 165 | 698 |
| 4501-5060 | 0 | 67 | 192 | 107 | 194 | 8,454 |
| 2-5060 | 12 | 677 | 1,630 | 995 | 1,745 | 10,149 |

All the CPU is in the searched games, and it is concentrated: the 10 dearest hold 54.6%, the 50 dearest 79.9%, and 4983
alone 10.8%.  **How far below the ceiling the searched games fell**, δ(n) in bands, with each band's share of the
searched CPU of its range of n in brackets:

| n | games | median δ | 1-10 | 11-30 | 31-100 | 101-300 | 301-1,000 | 1,001-3,000 |
|---|---|---|---|---|---|---|---|---|
| 2-1000 | 311 | 105 | 19 (1.8%) | 45 (3.2%) | 83 (24.5%) | 131 (30.9%) | 33 (39.6%) | 0 |
| 1001-2000 | 351 | 412 | 8 (1.2%) | 13 (3.5%) | 44 (13.9%) | 65 (29.2%) | 221 (52.3%) | 0 |
| 2001-3000 | 357 | 765 | 6 (1.4%) | 6 (0.2%) | 30 (4.4%) | 38 (31.2%) | 167 (45.9%) | 110 (16.9%) |
| 3001-4000 | 367 | 1,120 | 2 (0.1%) | 8 (1.1%) | 32 (9.1%) | 40 (15.0%) | 67 (17.5%) | 218 (57.2%) |
| 4001-4500 | 165 | 1,502 | 2 (0.2%) | 4 (2.0%) | 8 (4.7%) | 13 (13.2%) | 15 (11.8%) | 123 (68.2%) |
| 4501-5060 | 194 | 1,763 | 3 (0.3%) | 4 (0.1%) | 8 (1.0%) | 24 (24.1%) | 14 (2.8%) | 140 (71.7%) |
| 2-5060 | 1,745 | 580 | 40 (0.3%) | 80 (0.3%) | 205 (2.0%) | 311 (22.5%) | 517 (5.0%) | 591 (69.8%) |

(One game, 4693, falls 3,179 below and is left out; it is an exchange that the near-repeat cut proves in 30 steps.)
**Plainly: the cost does not lie close below the ceiling.**  The searched games within 10, 30, 100, 300 and 1,000 points
of their ceiling hold 0.3%, 0.6%, 2.6%, 25.2% and 30.2% of the searched CPU, and of the 25.2% within 300, 15.2 points
are two games (4983, δ = 246; 5054, δ = 121).  From 3001 on the shares are within 0.3 points of these.  The median δ is
0.32 n.  A slightly sharper ceiling would settle almost nothing; a rule must find δ(n), which is about a third of n.
Yet the ceiling is the tighter root bound (δ < gap) in 751 of the 1,745 searched games, which hold 81.4% of the CPU, by
a median of 346 points (2,342 at 4983, 2,499 at 5054); the search cannot use that, because the ceiling bounds the root
only.

By kind of step (Section 2.2) the shares of the searched CPU are the same from 3001 and from 4001 on.

### Table 2: the games past 5060, by the best-known scores

| n | prime | ceiling | repeat | searched |
|---|---|---|---|---|
| 5061-6000 | 106 | 310 | 188 | 336 |
| 6001-7000 | 117 | 351 | 193 | 339 |
| 7001-8000 | 107 | 360 | 205 | 328 |
| 8001-9000 | 110 | 334 | 196 | 360 |
| 9001-10000 | 112 | 350 | 191 | 347 |
| 5061-10000 | 552 | 1,705 | 973 | 1,710 |

The classification is games.csv's: a game is at its ceiling when its best-known score is the best-known score of n − 1
plus n, so it is settled once n − 1 is proven; a repeat is a best-known line of method repeat.  (One odd semiprime,
8617, is listed as searched because its best-known line came from another pass; J3 settles it from 8616.)  By kind, the
1,710 searched games are 1,096 relaxations, 429 restrictions and 185 exchanges.  Their best-known δ has the quartiles
1,488, 2,666 and 3,540 (10th and 90th percentiles 289 and 4,356); 60 are within 100 of the ceiling and 393 within 1,000.
Their gaps have a median of 5,211.

### Table 3: the single-loss rule

On the recorded optimal set of n − 1 (2..4955 from the October study, 4956..5060 by `single_loss_tail.py`, which agrees
with it on ten games checked).  *Exact*: S\*(n − 1) + n is playable; *holds*: x_min = δ(n); *fails*: x_min > δ(n).

| outcome, kind | games | exact | holds | fails | CPU share of the fails | shortfall where it fails: median, 90th percentile |
|---|---|---|---|---|---|---|
| prime | 677 | 1 | 676 | 0 | | |
| ceiling | 1,630 | 1,629 | 0 | 1 (686) | | 196 |
| repeat (all exchanges) | 995 | 0 | 995 | 0 | | |
| searched, restrict | 497 | 0 | 140 | 357 | 62.5% | 171, 1,198 |
| searched, relax | 1,169 | 0 | 379 | 790 | 83.3% | 186, 1,071 |
| searched, exchange | 79 | 0 | 79 | 0 | 0 | |
| searched, all | 1,745 | 0 | 598 | 1,147 | 69.1% | 180, 1,096 |

The rule holds at every exchange, with x_min the shadow, and at 598 searched games in all, which hold 30.9% of the
searched CPU.  Where it fails, its shortfall is 1-10 points at 65 games, 11-100 at 355, 101-300 at 263, 301-1,000 at 316
and more at 148.  At 686 the recorded set of 685 is the wrong one of three.

### Table 4: the increments of the searched games

| kind | games | (opt(n) − opt(n − 1))/n: 10%, 25%, 50%, 75%, 90% | median δ/n | δ = δ_PB (games, CPU) | \|rise\| ≤ 10 | ≤ 100 | rise > 0 | rise < 0 |
|---|---|---|---|---|---|---|---|---|
| restrict | 497 | 0.54, 0.62, 0.71, 0.92, 0.97 | 0.29 | 197, 39.9% | 248 | 446 | 132 | 168 |
| relax | 1,169 | 0.51, 0.56, 0.68, 0.87, 0.97 | 0.32 | 482, 28.4% | 605 | 1,059 | 389 | 298 |
| exchange | 79 | 0.42, 0.45, 0.46, 0.49, 0.50 | 0.54 | 79, 100% | 79 | 79 | 0 | 0 |
| all | 1,745 | 0.51, 0.56, 0.68, 0.87, 0.97 | 0.32 | 758, 38.8% | 932 | 1,584 | 521 | 466 |

* **What predicts δ.**  Rank correlations with δ over the searched games: δ_PB 0.99, x_min 0.75, n 0.65, gap(n − 1)
  0.63, the largest prime of n 0.50, the layer −0.07; for δ/n, δ_PB 0.75 and the rest 0.38 or less.  The rise δ − δ_PB
  has quartiles −4, 0 and 9, 5th and 95th percentiles −93 and 104, and extremes −550 and 385.  Outside the searched
  games the rise is 0 but at 20 games at the ceiling, where the gap falls (343, 812, ..., 4374).
* **By layer.**  Restrictions of layer 4 are cheap (110 games, median δ 100, 1.8% of the CPU); those of layers 3 and 5
  are dear (315 games, median 806, 18.7%; 53 games, median 1,020, 7.7%).  Relaxations of layers 4, 5, 7 and 9 hold
  13.8%, 22.7%, 8.6% and 8.1% of the CPU.
* **Simple formulas.**  P is the largest prime of n and P₁ the prime before it.  δ(n) is the shadow of n at all 79
  searched exchanges (10.0% of the CPU) and at 96 restrictions (2.8%); it is n/2 with P replaced by P₁ at 215
  relaxations (5.1%), among them 111 of the 114 searched games 8P (all but 24, 40, 184: δ(8P) = 4P₁) and 78 of the 81
  games 12P (all but 60, 84, 204: δ(12P) = 6P₁); no simple formula fits the rest (56.4% and 25.2% of the CPU in
  relaxations and restrictions).  Past 5060 the best-known scores agree with δ(8P) = 4P₁ at 88 of 89 and with
  δ(12P) = 6P₁ at 60 of 63 games, all searched.  Of the four exceptions, 9304, 9564 and 9924 beat the formula, and 9732
  was 384 short of it in games.csv; the unsound mode has since raised 9732 to the formula's score.

## 6. Worked examples

Each is computed from the rules alone by `examples.py` (U\* by descending greedy, every promotion set enumerated, peel
for playability), and agrees with the committed opt(n).  All optimal sets below 425 are unique.  Below 187 layer 2 still
has freedoms, so layer-2 numbers up to n/2 (14, 35, ...) can be promotions.

### 6.1 Settled by the ceiling: 62 → 63 = 3²·7 (restrict)

U\*(62) has 24 sources summing to 1,143, and P\*(62) = 58, by {28, 30}: opt(62) = 1,201.  The source 63 takes a freedom
and U\*(63) = U\*(62) + 63 (sum 1,206); the candidates stay {8, 12, 18, 20, 27, 28, 30} and P\* stays 58.  The optimal
set of 62 plus 63 passes peel: in a legal order 63 comes after 42, which takes 21, and takes only 9; 45 then pays 15,
and 36 and 54 pay 18 and 27.  So opt(63) = 1,264 = opt(62) + 63, proven by the ceiling.  The numbers 9P (cofactor 9)
reach their ceiling at all 94 games of 188..5060 and at all 84 of 5061..10000 by the best-known scores; why is open.

### 6.2 A searched relaxation where the single-loss rule holds: 39 → 40 = 2³·5

U\*(39) sums to 485 and holds s = 20; the candidates are {8, 12, 18}; P\*(39) = 18 by {18}; opt(39) = 503.  At 40, s
leaves U\* (it becomes a factor and a candidate) and U\*(40) = U\*(39) − 20 + 40 (sum 505); the candidates are {8, 12,
18, 20}; the promotion sets are ∅, {8}, {12}, {18}, {20}; P\*(40) = 20; opt(40) = 525, δ = 18.  Why 18 cannot stay with
both 20 and 40: the residual of S\*(39) + 40 is the core {24, 36, 40}, which lists only 8 and 12 (18 and 20 are moves).
The other way to make room, giving up s = 20 so that 40 is paid by 20, costs 20 > 18.  The rule gives up 18 and is
exact; in the optimal game 40 is paid by 8.  The search had to show that no set of 40 beats 525, though the ceiling is
543.

### 6.3 A searched restriction: 54 → 55 = 5·11

P\*(54) = 61 by {14, 20, 27} (opt 940).  At 55, U\* gains 55 alone, the candidates shrink from 11 to {8, 12, 18, 20,
27}, and P\*(55) = 47 by {20, 27}: opt(55) = 981, δ = 14 = the fall of P\*.  The obligation of Theorem D(b) is concrete
here: six promotion sets of 54 are worth more than 47 ({14, 20, 27} 61, {10, 20, 27} 57, {8, 21, 27} 56, {15, 18, 20}
53, {4, 20, 27} 51, {21, 27} 48), and none stays playable with 55.  With S\*(54), the residual is {14, 33, 34, 35, 49,
51, 55}, a cycle of edges in layer 2 (14 = 2–7, 35 = 5–7, 55 = 5–11, 33 = 3–11, 51 = 3–17, 34 = 2–17) with 49 on 7.
Giving up 14 breaks it; the rule is exact.

### 6.4 A miss of the single-loss rule: 76 → 77 = 7·11 (restrict)

P\*(76) = 126 by {27, 28, 35, 36} (opt 1,869); ceiling 1,946.  The residual of S\*(76) + 77 is {35, 49, 55, 77}: the
edges 35 = 5–7, 55 = 5–11, 77 = 7–11 and 49 = 7² on vertex 7, four members over the three factors 5, 7, 11.  The rule
gives up the smallest, 35 (the shadow of 77), for 1,911.  But P\*(77) = 94 by {28, 30, 36}: the optimum gives up 27 and
35 and adds 30, for opt(77) = 1,914 and δ = 32, a trade no single loss finds (32 is not a move of 76).  In the optimal
game 45 pays 9 (freed by dropping 27), 75 pays 15, and 30 pays 6.  The band (94, 126] holds 27 promotion sets of 76, and
the proof of 77 must show each incompatible with 77.

A relaxation miss, 53 → 54 = 2·3³: s = 27 stays (as a promotion) and 54 must be paid by its other maximal factor 18,
which S\*(53) plays; giving up 18 alone costs 18, but the optimum gives up 18 and 21 and adds 14 and 20, for δ = 5 (P\*:
39 → 61, with 27 now counted as a promotion).

### 6.5 An exchange: 50 → 51 = 3·17

U\*(51) = U\*(50) − 26 + 51, with 26 = 2·13 the shadow of 51; the candidates are the same eight, P\* = 39 by {18, 21} in
both, δ = 26.  The residual of S\*(50) + 51 is {21, 26, 34, 39, 49, 51}: the cycle 3–13–2–17–3 of 39, 26, 34 and 51,
with 21 = 3–7 and 49 = 7² hanging on it, six members over five factors.  26 is the smallest member of the cycle other
than 51, and J3 proves δ(51) = 26.  The first searched exchange of layer 3 is 741 = 3·13·19, which gives up
374 = 2·11·17 with the same 44 promotions (P\* = 13,565); 374 is paid by one of 22, 34, 187, and 741 by one of 39, 57,
247.

## 7. Open directions

These are the leads the data shows; the study may find better ones.  Each names the share it could settle.

**7.1 The exchange law in layer 3.**  Conjecture: if n is odd and U\*(n) = U\*(n − 1) − x + n, then
opt(n) = opt(n − 1) + n − x (equivalently, given U at both games, P\*(n) = P\*(n − 1)).  The lower bound is a game:
S\*(n − 1) − x + n is playable at every searched exchange (the single-loss rule holds there with x_min = x), so only the
upper bound opt(n) ≤ opt(n − 1) + n − x is open.  What is known: it holds at all 1,074 exchanges of 2..5060 and all 185
searched ones past 5060 by the best-known scores; the step is invisible over GF(2), so the parity bound moves by n − x
too; J3 proves it in layer 2, where F4 fixes the layer; in layer 3 the pool of layer 3's instance is also fixed from 187
on (no optimal set plays a number of layer 2 up to n/2), but the instance has freedoms, takes promotions from layer 4,
and its members can list three factors, so odd cores occur; the corner sketch (Section 4.6) cuts the obligation to the
sets that use up every payer of x.  A natural route is J3's: a map from the optimal sets of n into the playable sets of
n − 1 (S ↦ S − n + x, with a repair inside layer 3's instance) that loses nothing.  Payoff: the 79 searched exchanges of
2..5060 hold 10.0% of the chain's CPU; past 5060 the law would settle 185 of the 1,710 searched games (10.8%), and with
the 973 repeats every exchange game would be settled from n − 1 without U.

**7.2 Relaxations (62% of the CPU).**  The optimum of n plays s = n/2 in 1,133 of the 1,169 searched relaxations (the
others are 2^k, 3·2^k and some 2^k·P), so n is paid by another maximal factor n/p, p odd, and δ(n) is the price, in game
n − 1 with s made a free candidate, of reserving one n/p for n.  Two families obey a single exchange exactly:
δ(8P) = 4P₁ at 111 of the 114 searched 8P and δ(12P) = 6P₁ at 78 of 81 (every miss below 205), so the optimum keeps
s = 4P or 6P and gives up the number of the same cofactor one prime lower (at 5052 the promotion 2526 = 6·421 displaces
2514 = 6·419).  These two families hold 4.9% of the chain's CPU and 152 of the 1,710 searched games past 5060, where the
best-known scores agree at 148.  Proving them is a second concrete target; the method might reach the other cofactors of
s, for which no simple formula fits (cofactors 16, 20, 24, 30, 36, 40 fit at 0 to 4 games each).

**7.3 Restrictions (28% of the CPU).**  δ(n) is the fall of P\*, and Theorem D(b) puts the proof of n inside the band of
n − 1's promotion sets between P\*(n) and P\*(n − 1).  In 96 searched restrictions (2.8% of the CPU) δ(n) is the shadow
of n.  Layer-4 restrictions are cheap (median δ = 100), layer 3 and 5 dear (median 806 and 1,020).  The dearest game of
the chain, 4983 = 3·11·151 (10.8% of all its CPU), is a restriction with δ = 246 and a gap of 2,588: its band is only
246 points wide, but the search pays for a gap ten times as wide.

**7.4 The parity bound's increment.**  δ_PB(n) = PB(n − 1) + n − PB(n) predicts δ(n) almost perfectly: rank correlation
0.99 over the searched games, equal in 758 of 1,745 (38.8% of their CPU), within 10 in 932 and within 100 in 1,584.
Since δ = δ_PB + rise, a theorem "gap(n) ≥ gap(n − 1) − E(n)" with E computable would give opt(n) ≤
opt(n − 1) + PB(n) − PB(n − 1) + E(n), and with a game at that score it settles n.  It is false with E = 0: the gap
falls at 466 searched games (to −550) and at 20 games at the ceiling.  The rises do not run in streaks (consecutive
searched games with nonzero rises: 256 pairs of the same sign, 323 opposite).  What makes the gap fall (which odd cores
of n − 1 the arrival of n dissolves) is open; a local condition under which it cannot fall would settle every game with
rise 0 that meets it.

**7.5 A relative bound at the nodes.**  A bound on the root alone cannot shorten a search (a node is cut only at or
below the incumbent), so an increment bound must be exact or apply node by node.  In a restriction, every completion of
a node of n's search is a promotion set of n − 1 that is open to n.  A lower bound L(node) on the price of room for n
among the node's completions would let the search cut the node when P\*(n − 1) − L(node) ≤ the incumbent, that is, when
L(node) ≥ δ(n): a priced form of the near-repeat lemma.  In a relaxation the same holds for the completions that play s,
with P\*(n − 1) + s in place of P\*(n − 1).

**7.6 Things any rule must respect.**  A game can have several optimal sets (all are unique below 425; 30 games of
425-779 have two or three; every complete enumeration from 780 to 989 found one); the step theorem needs every optimal
set of n − 1 (685 → 686).  A rule proved on the whole board, like J3, needs no statement U and serves both programs; a
rule in the frame model needs U at the games it uses.  The number 1 is never a move, so no single exchange gives δ = 1
(21, 78 and 4116 have δ = 1).

## 8. What a useful answer looks like

* **A theorem** that settles a class of steps from game n − 1, with a test of when it applies that is cheap to compute
  (from the factorization of n, U\*(n − 1) and the frames, the optimal set of n − 1, or the parity bound), a proof, and
  what it rests on (the rules alone, U, (♦)).  It is judged by the share of the searched games, and of their CPU, that
  it settles in 2..5060 (Tables 1 and 3) and by the share of the 1,710 searched games of 5061..10000 it covers (Table
  2).  A partial result counts: the exchange law alone is worth 10% of the CPU.
* **An increment bound** opt(n) ≤ opt(n − 1) + n − L(n), proven, judged by how close L(n) comes to δ(n) (Table 4 and
  `searched.csv`); one that is exact on a class of games settles them, and a bound that can be applied at every node of
  a search is judged by the share of the band it closes.
* **A conjecture with a sharp test** is useful too: the coordinator checks it on 2..5060 and on the best-known games.
* **Experiments.**  The study may ask for any computation, and the coordinator runs it: light scripts (peel, the parity
  bound, enumeration of promotion sets below about n = 300) at once, solver runs of up to 10 minutes on 4 threads while
  a proof occupies the machine.

## 9. Files

Everything is in /home/brian/taxman_work/lab/work/succession/.  Each script runs as `nice -n 19 python3 -I SCRIPT` from
that folder, uses the standard library only, and reads, never writes, the inputs: the committed results
(`/home/brian/taxman_work/research/results/optimal.jsonl.gz`, games 1..5060), the gap dashboard's
`/home/brian/taxman_work/lab/work/gapdash/games.csv` (2..10000: score, parity bound, gap, ΣU\*, kind; best-known past
5060), the arrival study's `arrival.jsonl.gz` (U\* gained and lost, boards 3..8191) and the single-loss study's
`core_full.jsonl` (n = 2..4955), both in the notebook at `/home/brian/taxman_work/research/solver/notebook/`.

* `common.py`: the loaders, the number tables, peel (`playable`), the residual, and a legal order from a payment scheme.
* `test_peel.py` → `test_peel_out.txt`: peel against a search over all orders (every set of at most 6 members of boards
  2..12), every recorded optimal set of 2..5060 playable, and the optimal set of 20 with 21 unplayable.
* `settle.py` → `settle_out.txt`, `settle.csv` (one row a game 2..5060: outcome, proof kind, δ, ceiling, parity bound,
  gap, rise, the steps of PB, ΣU\* and P\*, CPU seconds, nodes, layer, cofactor, step kind) and `past5060.csv` (5061..
  10000: kind, best-known score and δ, gap, rise, step kind): Tables 1 and 2.
* `single_loss_tail.py` → `single_loss_tail.jsonl`, `single_loss_tail_out.txt`: the single-loss rule on 4956..5060, with
  a cross-check against the October study on ten games.
* `analyze.py` → `analyze_out.txt`, `searched.csv` (one row a searched game: step kind, δ, δ_PB, rise, gap, x_min, the
  rule's verdict, CPU-hours, nodes): Tables 3 and 4 and the formulas of Section 7.
* `examples.py` → `examples_out.txt`: the worked examples of Section 6.
