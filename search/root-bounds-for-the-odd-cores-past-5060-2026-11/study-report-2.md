# The second study: routes to cheaper proofs past 5060 (INTERIM: waits on the experiments of Section 4)

*Second study, independent of study-report-1.md.  Scripts and logs in `study-2/`.  Facts labeled proved / measured /
conjecture as in the brief.*

## 0. Summary

Ideas by promise, each with its validity, measured effect and cost per node.  Numbers from n ≤ 2176 in plain Python
(`study-2/`); the end of the chain needs the experiments of Section 4.

1. **The smooth/fiber split with an exact smooth oracle shared by all nodes and games** (Sections 2.4, 3).  Bound:
   ΣU\* + max_X [E(X) + F_N(X)] over hub sets X, E the smooth sub-board's exact optimum with X deleted, F_N the
   fiber-only parity bound at the node with the other hubs contracted.  *Proved valid.*  Why it is different: every
   unit of the gap is a smooth odd core (fixing the smooth configuration to the optimum's leaves 3-11% of the gap at
   1000-2176, Section 1.1; nothing in the gap is matroidal, 2.5), and the smooth sub-board is the same for runs of
   games and for every node, so its exactness can be paid once.  *Measured limit:* at the optimum's own hub set X\* the
   bound is opt + 89, 178, 12, ≤ 346 at 1000, 1500, 2000, 2176 (closes at most 58%, 56%, 98%, and at least 55% of
   the gap; the 2176 run did not finish); what it misses are
   mixed odd cores made by the hubs fiber rows list but do not pay (an ordering constraint the hub-set interface
   cannot carry).  *Cost per node:* one fiber matroid intersection per hub set tried (tens), plus oracle lookups;
   the oracle is a list of near-optimal smooth configurations built once per smooth sub-board (its size is open).  If
   it closes 55% at every node the 5061-5560 band costs 10³-10⁴ fewer nodes; it is the only idea here with a slope
   change in reach, and it rests on three open numbers (Section 4, items 1-3).
2. **C2, the fiber-demand condition** (2.1-2.2).  *Proved* necessary; closes 70% of the root gap at 1000 against 45%
   for the first study's smooth condition and cuts 24 of 24 sampled nodes, but it is a condition on the heaviest set
   and so its bound is a truncated proof tree (2.3): useful as a diagnostic and as the branching target (resolve the
   hub contention first), not as a bound.  Cost: a peel per hub choice (cheap as a test; a sub-search as a bound).
3. **Per-fiber exactness** inside idea 1 (2.4, Experiment H): removes the fiber-side GF(2) slack at 1000 and 2000
   (8, 12) but not the mixed cores (174 at 1500).  Cheap (fibers are boards up to n/29); a refinement, not a lever.

Limitation results: (a) any bound computed by testing a condition on the heaviest set costs a truncated proof (2.3);
(b) the union-block matroid that encodes hub payers with distinct hubs is weaker than the parity bound and the
heaviest set already satisfies it, so hub counting mod 2 is empty and all the gap needs smooth exactness (2.5);
(c) increment bounds need a certificate of n − 1's near-optimal landscape, and replaying, margins or local formulas
each cost a proof (2.6); (d) the Lagrangian form of the split is harder to compute than the split (2.8).  On the
constant: gap ∝ n² is the knot's linear growth times the n-scale of a smooth substitution; probably c = 0 with a
log factor, which changes nothing in practice (2.7).

## 1. Cheap checks run

### 1.1 Where the gap lives: smooth choice or fiber choice (measured, `study-2/exp_a.py`)

Smooth = every prime ≤ 23.  "Smooth-fixed" = the parity bound with the smooth candidates (≤ n/2) fixed to S\*'s choice
(picked or barred) and the fiber candidates free; "fiber-fixed" the other way round.

| n | gap | smooth-fixed gap | fiber-fixed gap | H_s gap (first study's smooth condition, e1 leaf) |
|---|---|---|---|---|
| 1000 | 214 | 8 (4%) | 206 (96%) | 118 (55%) |
| 1500 | 401 | 178 (44%) | 304 (76%) | — |
| 2000 | 491 | 54 (11%) | 301 (61%) | — |
| 2176 | 767 | 24 (3%) | 663 (86%) | 345 (45%) |

So given the optimum's smooth configuration, the parity bound is nearly exact (the fibers are handled well by GF(2));
given the fiber configuration it is not.  What remains after fixing the smooth part is layer 4's lifted templates (at
2176 the smooth-fixed residual is 16 fiber members in layer 4: T11) and, at 1500, mixed cores of layer 4 (26 smooth +
26 fiber members, whose smooth part alone peels).

### 1.2 What stalls in H_s, the heaviest set under the first study's smooth condition (measured)

At 2176 H_s (gap 345) still has residuals 99/101 (L4), 60/60 (L5), 41/41 (L6) with 56, 49, 38 smooth members; the smooth
rows alone peel (the condition holds), and they still peel when the hubs of *plugs* (fiber members whose only live
column is their hub) are removed.  The stall needs the other fiber members of the residual (42, 9, 2 per layer), which
have live internal columns.  So the remaining cores are *mixed*: smooth rows plus fiber rows that form internal cores
of their fibers; the fiber part demands hubs (Section 2.1), and the smooth part cannot spare them.

## 2. Ideas

### 2.1 The fiber-demand lemma and the C2 condition (proved)

Fix a layer k ≥ 5 instance; T = √(n/8); a *fiber* is the set of members whose largest prime p exceeds T; a fiber member
x = m·p lists its *hub* m (if unplayed) and *internal* columns (m/q)·p.  Internal columns are private to the fiber
(a column c·p with c < 8 would be needed to be shared, impossible in layer ≥ 5).

**Lemma (fiber demand).**  Let T ⊆ fiber p be an *internal core*: every internal column listed by a member of T is
listed by at least two members of T (a member listing no internal column counts).  In every playable set containing T
(and the layer-(k−1) numbers T's members list that are played), some member of T pays its hub.  *Proof:* if every member
of T paid an internal column, the restriction of the acyclic scheme would be an acyclic scheme of T in the internal
instance, so T would be internally playable; but a core is unplayable in its own instance (dismantling deletes nothing).
Shrinking lists (playing more of the layer below) keeps T a core.  ∎

**Condition C2.**  For every layer, with disjoint internal cores T₁, …, T_m of its fibers (hub sets H_i), there is a
choice h_i ∈ H_i of distinct hubs such that the smooth sub-instance (smooth rows over smooth columns) minus
{h₁, …, h_m} is playable.  Necessary for playability (by the lemma and because the smooth rows' scheme restricted to
the remaining columns is acyclic).  A violation gives a nogood: ∪T_i ∪ ∪_h Res(h) ∪ (played numbers these list),
where Res(h) is the smooth residual with hubs h removed.

C2 strictly contains the first study's condition (no hubs removed) and targets exactly the mixed cores of 1.2.

### 2.2 The C2 bound at the root (measured, `study-2/exp_b2.py`, `study-2/c2b.py`)

Best-first branch and bound on the parity bound, branching on a minimal core of the full layer instance when the
heaviest set violates C2, accepting a set that meets C2 only when it is the heap's maximum (the first version accepted
the first feasible node found and overstated the share; corrected).

| n | gap | C2 bound − opt | share closed | first study's smooth condition | nodes (parity evaluations) |
|---|---|---|---|---|---|
| 1000 | 214 | 65 | 70% | 45% | 3,800 |
| 1500 | 401 | ≤ 168 | ≥ 58% | — | 7,712 in 40 min, unfinished |
| 2000 | 491 | ≤ 366 | ≥ 25% | — | 4,207 in 40 min, unfinished (0.6 s a node: the hub-choice search) |

(At 1500 and 2000 the best open node's bound is an upper bound on the C2 bound, so the shares are lower bounds.)  The remaining 30% at 1000 is a stall that C2 does not see: with the fiber cores' hubs granted,
the smooth part peels, yet the joint instance does not.  Mechanism (proved by inspection of the precedence): a fiber
member b that pays an internal column still *takes its hub as tax* when it plays, so the smooth rows that pay that hub
must precede b, while b's internal chain forces b before another fiber member a that takes a hub the smooth rows list
after... these are *mixed cycles* through two hubs, an ordering constraint, not a counting one.

At search nodes C2 carries fully (measured, `study-2/exp_c.py`): of 24 nodes of the parity tree at 1000 sampled at
depths 3, 6 and 10 (node gaps 1-99), the C2 bound cut all 24, in 2 to 410 parity evaluations each.

### 2.3 Limitation: a condition tested on the heaviest set is the proof tree, truncated (argument, measured at 1000)

Every bound of the form "max weight of a set that is parity-independent and satisfies a condition C on its heaviest
set" (the first study's smooth condition, C2, exactness in frame 2) is computed by a branch and bound that branches on
the same cores the proof branches on and stops where C holds.  Its tree is the proof's tree with the subtrees below
C-feasible nodes cut off.  At 1000 the C2 tree has 3,800 parity evaluations against a proof of a few thousand nodes;
at 5060 the first study's weaker condition took 263,621 nodes.  So no such bound can be cheaper than the proof by
more than the factor by which the C-feasible boundary shortens the tree, and C2's boundary is 70% of the way down.
This is why "exact in frame 2" cost 1.08 proofs per node.  **The lever is not a stronger condition on H but a bound
that resolves the hub contention without search, or whose expensive part is reusable across nodes and games.**

### 2.4 The smooth/fiber split bound (proved valid; measured limit)

Let X be a set of hubs.  E(X) = the exact optimum of the smooth sub-board (smooth sources fixed, smooth candidates
free) with the hubs X barred and deleted as columns; F(X) = the parity bound of the fiber part with every hub outside
X deleted (contracted).  **Theorem.**  opt(n) ≤ ΣU\* + max_X [E(X) + F(X)] ≤ PB(n).  *Proof:* in an optimal game let X
be the hubs paid by fiber rows; the smooth rows' scheme restricted to the other columns is acyclic (≤ E(X)); the fiber
rows' list matrix in game order is triangular on their payment columns, so deleting non-payment hub coordinates keeps
it so (≤ F(X)).  The upper bound by PB: a set independent on each side with the hub coordinates split is jointly
independent.  ∎  E depends only on the smooth sub-board and X, which is the same for runs of consecutive n and for
every node of a search that does not fix smooth candidates; F is a matroid intersection on the fibers alone.

Limit (measured, `study-2/exp_d.py`): at X\* = the hubs paid by fiber rows in a peel of S\*, the two sides against S\*'s
own parts:

| n | gap | E(X\*) − S\*'s smooth part | F(X\*) − S\*'s fiber part | E + F − opt | split closes at most |
|---|---|---|---|---|---|
| 1000 | 214 | 81 | 8 | 89 | 58% |
| 1500 | 401 | 0 | 178 | 178 | 56% |
| 2000 | 491 | 0 | 12 | 12 | 97.6% |
| 2176 | 767 | ≤ 346 together (E(X\*) unfinished after 18,585 nodes, 55 min; smooth-fixed gap is 24, so most of it is E's own slack) | | ≤ 346 | ≥ 55% |

The smooth side is *exact* at X\* at 1500 and 2000: the smooth sub-board with the fibers' hubs removed has S\*'s
smooth configuration as its optimum.  At 1000 it does 81 better, and that is the mixed-cycle loss of 2.2 (a smooth
configuration playable without X\*, heavier than S\*'s, that the fibers' scheme cannot be ordered with).  The fiber
side's loss at 1500 (178) is **not** removed by solving each fiber exactly with S\*'s hub assignment (measured,
`study-2/exp_h.py`: fiber-exact minus S\*'s fiber part is 0 at 1000, 174 at 1500, 0 at 2000).  At 1500 fiber 29 alone,
with its hubs {25, 26, 45, 50} and the rest deleted, prefers 609 = 21·29 to 435 = 15·29 (+174) and is playable by
itself in every layer; on the full board that swap leaves a layer-4 residual of 51 members (26 smooth, 22 fiber of
primes 29-47, 3 plugs) that is GF(2)-independent: a mixed odd core made by the fiber rows' *unpaid* hubs (12, 18, 30,
42: taken as tax, so the smooth payers of those hubs must play first) against the smooth part's own order.  So the
split's interface, hub *sets*, misses the ordering constraints the fibers impose through hubs they list but do not
pay, and that costs 42% of the gap at 1000, 43% at 1500 and 2% at 2000.  E(X\*) took 992, 7,858 and 4,735
smooth-parity evaluations at 1000, 1500, 2000 (0.1 s each in Python); at 2000 the fibers pay 49 of 56 hubs.  One-hub
moves from X\* at 1000 (`study-2/exp_g.py`, 27 of 32 hubs tried) raise E + F above its value at X\* by at most 2
(giving hub 27 back to the smooth part: E +335, F −333); adding a hub to X lowers E by more than F gains.  So max_X
is close to the X\* term at 1000, about opt + 90.

The smooth near-optimal list (`study-2/exp_f.py`, 1000): a naive k-best enumeration found 78 playable smooth
configurations within about 200 of the smooth optimum in 17,110 smooth-parity evaluations before its 20-minute
budget ran out (the enumeration splits each feasible leaf on its own members, which is wasteful, and its first
feasible leaf is not the optimum, so its margin is approximate).  Enough to say the list is not tiny and that a
better enumeration (or on-demand E(X) with a cache) is needed; Experiment 4 asks for the count at 5000.

### 2.5 Limitation: hub counting modulo GF(2) does not bite (proved construction, measured, `study-2/upb.py`)

The hub-demand structure of 2.1 can be made a matroid: in each block replace the GF(2) matroid by the *union* L′ ∨ L_int,
where L′ is GF(2) on the smooth coordinates (smooth rows' vectors, fiber rows as the unit of their hub, smooth columns'
units) and L_int GF(2) on the fiber coordinates (fiber rows' internal vectors, fiber columns' units).  A set is
union-independent iff it splits into hub payers with distinct hubs, jointly independent with the smooth rows, and an
internally independent rest; every playable set is (the proof of 2.4).  The union of two representable matroids is
represented by stacking the two matrices with a random scalar per element over a large field (the determinant of a
square minor is a polynomial in the scalars whose monomials are indexed by the splits, so it vanishes iff no split
works), so the bound stays a two-matroid intersection, certifiable by a weight split.  *Measured:* at 600 and 1000 the
parity bound's heaviest set is already union-independent, and the union-block bound alone is weaker than the parity
bound (gap 131 against 106 at 600, 601 against 214 at 1000: it misses the mixed even cycles GF(2) catches).  So the
part of the hub contention that C2 sees beyond the first study's condition (70% against 45% at 1000) is not a
counting fact visible mod 2; it is the smooth part's *exact* playability once the fibers' hubs are deducted, i.e. more
smooth odd cores.  Every share of the gap needs exactness on the smooth part; nothing in it is matroidal.

### 2.6 Increment bounds: why the proof of n re-proves gap(n − 1), and what would stop it (argument)

At a node N of game n's tree, PB_n(N) − v(n) = [PB_{n−1}(N) − opt(n − 1)] + [σ(n) − σ_PB(N)], where σ(n) = opt(n − 1) +
n − opt(n) is the game's shortfall from its ceiling and σ_PB(N) = n − [PB_n(N) − PB_{n−1}(N)] what the parity bound
pays to fit n at N.  The second bracket is small (the gap moves by a median 10 at searched games), the first is the
accumulated gap.  So the trees of n − 1 and n are nearly the same tree, each paying for the whole accumulated gap;
this is also why standalone proofs cost what chained ones do (brief, fact 7).  Three ways to carry the n − 1 proof
forward, and why each fails:

* *Replay the n − 1 tree's leaves on board n.*  A leaf L closes iff slack(L) + σ_PB(L) ≥ σ(n); slacks are spread over
  one branching step (about 70 points) and σ_PB(L) ≈ σ_PB(root), so this is the "gap change" test: when the gap falls
  at n most leaves close at once, when it rises few do.  Either way the replay costs one parity evaluation per leaf,
  i.e. one proof.  Nogood carrying (1.3×) is the cheap version of this.
* *Prove n − 1 with a margin m and list every playable set within m of optimal.*  The list settles game n without a
  search when σ(n) ≤ m, but the usable margin shrinks by σ at every searched game (a near-optimal set of n that plays
  n is, less n, a set within m + σ(n) of opt(n − 1)), so over a run of games the list would have to start with the sum
  of their σ's as its margin, and a proof with margin m costs 10^{m/476} proofs.  No gain.
* *A local formula for σ(n).*  For a fiber number n = c·P the row n joins fiber P (a copy of board ⌊n/P⌋, where the
  J3 cycle argument lives) and lists the hub c; σ(n) is the cheaper of the fiber's exchange (computable on the small
  board) and the smooth part's price for releasing c.  A theorem needs a lower bound on that price, which is a fact
  about every near-optimal set of n − 1: the landscape again.  *Conjecture:* σ(n) equals the fiber exchange exactly
  when the hub c is in the smooth part's residual (its knot) of layer Ω(n) − 1; checkable on the 1,729 pairs.

So the increment cannot be bounded without a certificate of n − 1's near-optimal landscape, and none is cheaper than
the proof.  What does carry is structure (2.4): the smooth sub-board, where all the exactness is needed, is the same
for runs of consecutive games.

### 2.7 The asymptotic constant (reasoning on the data; conjecture)

Fixing the smooth configuration to the optimum's leaves 3-11% of the gap (1.1), so gap(n) is a function of the smooth
sub-board and of the hubs the fibers demand.  The smooth residual grows about linearly in n (31, 59, 115 smooth
members of layer 5's residual at 1000, 2176, 5000) while the count of 23-smooth candidates grows only as a power of
log n, so the knot takes a growing *share* of the smooth part; and each substitution the optimum makes to break it
trades near-equal numbers whose difference scales with n (the spacing of smooth numbers of one layer near n/2 is
about n/(their count), i.e. n/polylog).  Hence gap ≈ (swaps) × (n/polylog) with the swaps growing like the knot:
n²/polylog, consistent with the measured n^{2.00} over one decade and with a slowly falling gap/n² (the brief's
waves).  *Conjecture:* (PB − opt)/n² → 0 like 1/(log n)^a with a small, i.e. c = 0 but only logarithmically; the
practical consequence is the same as c > 0 (no fixed-share relaxation keeps up) and the "removable part" is all of
it, since every unit is a smooth odd core given the fibers' hub demands.  A test that separates c > 0 from c = 0 at
the available n is not possible; I do not recommend spending on it.

### 2.8 The Lagrangian form of the split (measured: not the way to compute it)

E_μ (the smooth exact problem with hubs sellable at prices μ) is a much harder branch and bound than E(X): with sell
elements every stalled core can also be repaired by buying a hub back, and at 1000 E_μ did not finish in 400 s where
E(X) takes 30 s (992 nodes).  Subgradient steps from μ = 0 moved the bound from gap 1,924 to 1,549 in four steps of
50-100 s each (`study-2/exp_d_1000.log`, first run).  So the max over X should be computed as a search over hub sets
with E(X) cached, or the smooth side should be a precomputed list (3.1), not a priced sub-problem.

## 3. The proposal: an exact smooth oracle shared by every node and every game (conjecture, with the numbers above)

**Bound.**  B(N) = ΣU\* + max_X [E(X) + F_N(X)], the split of 2.4, at every node N of the frame solver's search,
where N's picks and bars on fiber candidates enter F_N (a matroid intersection on the fiber part, about three
quarters of the candidates at 5000) and N's picks and bars on smooth candidates enter the oracle's query.

**Oracle.**  Once per smooth sub-board (it changes only when n or n/2 passes a 23-smooth number: 235 candidates at
5000, 326 at 10,000; 31-smooth past 7,192 so that fibers of different primes share no internal column), enumerate the
playable smooth configurations within a margin m of E(∅) with their weights (3,000-50,000 configurations is the
guess; Experiment 4 measures it).  Index each by the hubs it can do without (a bit mask) and by its promotions.  A
query (X, picks, bars) scans the masks and verifies the top candidates by peel; if none is within the margin the
oracle answers E(∅) − m, which is still valid.  Cost per query about a millisecond in Rust for a list of 10⁵.

**Search over X.**  For a node, branch on the contended hubs (those listed both by a stalled smooth row of the
oracle's answer and by a fiber core of F_N's heaviest set) with the monotone bound E(X_in) + F_N(X_out); the hubs
that only one side wants are decided at once.  Expected tens of fiber evaluations per node.

**Why it could change the slope.**  Every share of the gap needs exactness on the smooth part (2.5) and the smooth
part is the same for runs of games and for every node (1.1); the split loses only mixed cycles, 2.4% of the gap at
2000.  A bound closing 90% at every node turns a gap of 3,000 into 300 (10⁴ fewer nodes at 10-100× the node cost);
the 6000s (gap 5,000) into 500.

**What would kill it.**  (a) max_X [E(X) + F(X)] far above E(X\*) + F(X\*) at 3000-5060 (the fibers buying hubs the
optimum's smooth part keeps); (b) the share falling at deep nodes (the brief's lesson), though here the expensive
part is node-independent, so a node pays only for F_N; (c) the list within a useful margin too large to scan, or the
margin too small to answer deep nodes; (d) mixed cycles growing with n (58% lost at 1000, 2.4% at 2000: the trend is
the right way but two points).

## 4. Experiments requested (interim: the report waits on these)

All on the real solver or its lab code; "split bound" = ΣU\* + max_X [E(X) + F_N(X)] of 2.4 with smooth = 23-smooth
(31-smooth past 7,192).

1. **The split's X\*-term at 3000, 4000, 5000, 5060.**  Compute E(X\*) (the smooth sub-board's exact optimum with
   the hubs paid by fiber rows in a peel of S\* barred and deleted: a branch and bound over the 235 smooth candidates
   with the smooth-only parity bound and peel) and F(X\*) (the fiber-only parity bound with the other hubs contracted).
   Report E + F − opt as a share of the gap, split into the smooth side (E − S\*'s smooth part) and the fiber side.
   *Confirms* if the share lost stays near 40% or falls (then the split closes ≥ 55% at the root at the end of the chain);
   *kills* if it rises past 60%.  Cost: four smooth B&Bs (the e1 machinery restricted to smooth elements; 10³-10⁵
   nodes each) plus four fiber matroid intersections.  This is the decisive number.
2. **max over X against the X\*-term, at 2000 and 4000.**  A search over hub sets with E(X) cached (branch on the
   hubs listed by both a stalled smooth row and a fiber core; bound E(X_in) + F(X_out)).  Report the number of E
   evaluations and max_X − (X\*-term).  *Kills* the proposal if the max exceeds the X\*-term by more than half the
   gap.  Cost: tens to hundreds of smooth B&Bs per board.
3. **The split at nodes.**  30 nodes of the proof of 4848 (e6's trace) with node gaps 300-2,000: the split bound
   (with the X-search of item 2) against the node's parity bound and the target.  *Confirms* if it cuts ≥ 60% of them
   and the share closed does not fall with depth; *kills* if under 30%.  Cost: 30 × item 2.
4. **The smooth near-optimal list at 5000.**  Enumerate the playable smooth configurations within margin m of E(∅)
   for m = 100, 300, 1000 (k-best branch and bound: split a feasible leaf on its own members).  Report the counts and
   the time.  *Confirms* the oracle if ≤ 10⁶ at m = 300; otherwise E(X) must be solved on demand (then item 2's
   evaluation counts set the per-node cost).  Cost: one smooth B&B with margin, hours at most.  (The Python version
   at 1000, `study-2/exp_f.py`, is running.)
5. **C2 as a diagnostic at the end of the chain.**  On the heaviest sets of 4000-5060: the C2 condition (2.1) per layer, with
   the number of fiber internal cores, their hub-set sizes, and whether C2 fails; and the C2 bound's root share at
   3000 if affordable (its branch and bound is the first study's with C2 in place of the smooth condition; 10⁴-10⁵
   nodes).  Not decisive; it calibrates how much of the gap at the end of the chain is hub contention against mixed order.
