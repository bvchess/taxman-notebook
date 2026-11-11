# Odd cores: ideas for a tighter bound, and what cannot work

*The study, 2026-11-10.  Status: INTERIM, waiting on experiments listed in Section 5.  Everything here was derived from
brief.md and checked with the scripts in study-1/ (parity.py and cores.py beside the brief, plus fibercheck.py, elim.py,
pbsmooth.py, smoothcat.py there).  Labels: proved, measured (here or in the brief), conjecture.*

## 0. Summary

*Round 2 (Sections 6-10, after E1/E5/E6) in brief: PB_s closes 27-38% at 3000-5096 and does not fall with the gap;
PB − PB_s carries across games with the same smooth sub-board (959 at 5060 and 5061).  What survives it is the same
smooth knot re-tied through one or two fibers of primes 31-53 per layer.  The node-level use (E2, Section 7) must
buy 959 points within ~7 GF(2) solves a node to give 10×; only a measurement at deep nodes can say.  New ideas,
ranked: PB_sh, the smooth bound with the fibers' hub demands (validated: E1's leaf at 5000 violates it in layers 7
and 8; Section 8.0, experiment E11); raising B to 31-41 (Section 8.1, E8); interval certificates (8.3); root
forcing (8.4).  Killed here: a fixed GF(3) signing for the templates (no uniform signing kills T11).*

*Round 3 (Sections 11-12, after E11 and E8): PB_sh is 92% at 3000 but its search dodges at the hub conflicts the way
the parity bound dodged at cores, one twin at a time (every smooth-playable leaf fails the hub test; ~90 literals
and ~2 live children a branching; 5-10M open nodes).  The proposal is hub-ownership branching: at a demanded hub,
one child says "no fiber member pays it" (the hub projected off every fiber lister's row: an orbit constraint that
no twin undoes; measured at E1's leaf for 5000 it drops the bound by 946 and 1,364 where barring one fiber literal
drops 16 and 8), and the other children are the smooth residual's literals with the hub taken from the smooth
rows (the smooth side's need is an order fact invisible to GF(2), so it is left to the peel).  Sections 11.2-11.3,
experiment E12; the same rule for the outer search's mixed conflicts, E14.  Raise B to 31-37 after that (E13).
Root-only use buys near-optimality certificates, δ = PB_sh − best-known, by a depth-first search to a target
rather than best-first to the value (11.6, E12b, E15); outright proofs by the root bound will be rare.*

1. **The gap of layers 5-7 lives in the 23-smooth numbers** (measured here).  At n = 5000, H's layer-5 instance has 299
   members; the 115 whose primes are all ≤ 23 stall under peel *by themselves* (101 of them remain), while the 184
   members with a prime above 23 peel completely by themselves.  Same at 2176, 3000 and 4000, and in layers 6 and 7
   (5060 not run; the census shows the same residual sizes there).  Since
   a maximal factor of a smooth number is smooth, the smooth members of a layer list only smooth columns, so **"the
   smooth sub-instance of every layer is playable" is a valid necessary condition (proved) that depends only on the
   smooth promotion decisions** (235 numbers at 5000, 326 at 10,000, growing like a power of log n), and **a twin swap
   cannot dodge it** (twins m·p ↔ m·p' are not smooth).  Layer 4 is the mirror image: its residual is entirely the
   lifted templates (T11, T14, T23), and its smooth part is clean.  This splits the problem into a smooth core whose
   ground set barely grows and a fiber part made of small lifted patterns; the best idea (Section 1.1) is a bound,
   or a search order, that is exact on the smooth sub-board.  Finished measurements with a small smoothness bound:
   "every 13-smooth sub-instance is playable" closes 28% of the gap at n = 1000 (8 parity bounds) but only 10.6% at
   2176 (26 bounds), because at 2176 the layer-5 knot needs primes 17-23, which B = 13 does not see.  The 23-smooth
   version, the one that holds the knots at 2176-5000, is beyond my Python search past 1000; whether it closes a
   share that does not fall is experiment E1, and it decides the idea.
2. **A quantitative limit on matroid relaxations** (measured here, from the brief's lemma): of 56 minimal cores sampled
   in H's layer-5 knot at 5000, no matroid containing the playable sets can have more than 8 as circuits; 10 of 56 in
   layer 6, 4 of 25 in layer 7; 5 of 48 at 2176.  A single-matroid replacement of a GF(2) block is dead (Section 2).
3. Nogoods carry from game n − 1 to game n (proved for odd n; Section 1.3), but the project has measured that carrying
   them is worth at most 1.3× and that what carries usefully is bound structure; a smooth-exact bound is bound
   structure that would carry (Section 1.3).  A cheap check remains: what the solver's conflict branching picks,
   smooth members or fiber twins (E6).
4. The record in the brief's Section 4 is explained by the smooth/fiber split (Section 2.3): every relaxation tried
   acts on cores one at a time, and the heaviest set dodges by moving a fiber member; the smooth knot stays.

## 1. Ideas, ranked by promise

### 1.1 Exactness on the 23-smooth sub-board, computed once and used at every node

**The idea.**  Let B = 23 (or the largest prime that keeps the catalog small).  A number is *smooth* when all its
primes are ≤ B.  For each layer k, the *smooth sub-instance* of a set S has members the smooth members of S in layer k
and lists the unpromoted smooth maximal factors.  Define

    PB_s(n) = max { ΣI : I independent at both parities, and every smooth sub-instance of I is playable }.

*Valid upper bound (proved).*  Playable sets are closed under subsets: drop a move from a game, and every later pot is
a superset of what it was, so every later move still has its payment.  So if S is playable, the smooth members of
layer k are playable with the same lists (their lists use only smooth columns, and those columns' state depends only
on smooth promotions).  Hence opt(n) ≤ PB_s(n) ≤ PB(n).

*Why it should not be dodged.*  The brief's lesson is that every constraint on one core is dodged by a near-equal
alternative, and the alternatives are twins m·p ↔ m·p'.  The smooth sub-instance has no twins of that kind: its
members and columns are the 23-smooth numbers, a fixed finite structure for a given n (235 promotable ones at 5000).
Dodging within it means moving to another smooth configuration, and *all* smooth configurations can be enumerated or
their cores cataloged once per root.  H violates the condition at every census board from 2176 on, by a lot (101 of
115 smooth members stall at 5000).

*What it would take off the gap.*  One finished data point (measured here, pbsmooth.py): at n = 1000 with B = 13,
PB_13(1000) = 315,581 against PB = 315,640 and opt = 315,426, so the condition "every 13-smooth sub-instance is
playable" alone closes 28% of the gap, and the branch and bound that computes it took 8 parity bounds (1 s in
Python): the heaviest set needed one bar (308 = 2²·7·11) to become 13-smooth-playable.  With B = 7 it closes nothing
at 1000; with B = 23 the Python search reached the same 28% in 600 nodes without finishing (the rest of the gap at
1000 needs primes 17-23, or is not smooth at all).  **At 2176 the small-B versions are weak: PB_13(2176) closes
10.6% of the gap (81 of 767, 26 nodes, 27 s), PB_11(2176) 8.9%**; at 1500, PB_13 had closed 7.7% after 157 nodes
without finishing.  So the 13-smooth condition alone has a falling share, like every relaxation in the brief's
record.  The case for the idea rests on B = 23 (or 19): at 5000 the layer-5 knot needs primes 17-23 (with B = 13 the
layer-5 smooth members peel; with B = 19, 82 of 95 stall; with B = 23, 101 of 115), and at 2176 likewise (B = 13:
layer 5 clean, 18 of 34 stall in layer 6; B = 19: 39 of 59 in layer 5; B = 23: 53 of 68 in layer 5 and 40 of 47 in
layer 6).  So PB_13 at 2176 could only act on layer 6, and did.  The 23-smooth bound is unsettled past 1000 here:
at 2176 the Python search reached 1,494,888 (at least 5.2% closed) after 159 nodes and 140 s without finishing,
still meeting smooth cores of 28-38 members with 11-14 free members; my implementation is too slow (2-8 s a bound)
and the 23-smooth sub-board at n ≤ 2176 is a large part of the board, so the search there is close to a proof.  The ceiling is the brief's hybrid bound (exact in all of frame 2: cuts 40 of 45 nodes of gap
< 1000), of which smooth exactness is the part that does not depend on the fibers.  E1 asks for the measurement in
the real solver at 2176-5061; it is the experiment that decides the idea.

*Cost at a node, and the design with the search.*  Three ways to use it, cheapest first:

(a) **Smooth nogood catalog.**  Enumerate the minimal cores of the smooth sub-instances once per root and use them as
    nogoods at every node.  *Measured here (smoothcat.py, Section 3): this is weaker than I first hoped.*  The smooth
    knot of layer 5 at 5000 has hundreds of distinct minimal cores at least (222 from 300 random orders, still
    growing), of 32-69 members with 9-24 free (promotable) members each.  So the nogoods are long, and the brief's
    experience with cover cuts of 13-34-member cores applies.  A catalog may still help as a nogood store (it never
    hurts), but it is not the mechanism.
(b) **Smooth-first search.**  Branch on smooth promotions first (119 numbers in layers 4-5 at 5000, 235 in all),
    with the parity bound; at a leaf of the smooth decisions every smooth sub-instance is playable by construction,
    and the rest of the search is over fiber promotions, whose cores are the small lifted templates (T11, T14, T23).
    The smooth sub-board hardly changes from n − 1 to n (only when n or n/2 is smooth), so the smooth part of the tree
    and its nogoods carry across games (Section 1.3).  The question is how many nodes the smooth part needs.
(c) **Smooth-exact bound at nodes** (the brief's hybrid bound restricted to the smooth members: exact winnability
    tested on them only).  The hybrid bound on all of frame 2 cost a node's proof because it solved the fibers'
    choices too; on the smooth members alone the instance is 115 members over 111 columns at 5000, with no twins.
    The strongest form, and the one E1/E2 measure first.

*What kind of improvement.*  (b) is a different decomposition of the search (the owner's second kind); (c) is a
bound that is much better at deep nodes if the smooth knot is what the deep nodes meet (the brief: 85-97% of the
branchings are in frame 2, whose knot is smooth); (a) is a nogood store.  Judge by E1-E3 and E6.

*Risk.*  The smooth sub-board is itself a Taxman-like problem (NP-hard in shape) and at n ≤ 1000 it is most of the
board; the bet is that at the end of the chain its promotable part (235 numbers, 119 in layers 4-5) is small enough to
catalog once.  A second risk: cores that mix smooth and fiber members (70 of the 171 in H's layer-5 residual at 5000
are fiber members hanging on the smooth knot) may keep part of the gap after the smooth knot is excluded.  E1
measures both.

### 1.2 The fiber part: lifted templates, and what a fiber is

**Reading (proved from the definitions).**  For x = k·p with p its largest prime, mf(x) = {k} ∪ {(k/q)·p : q | k}.
So the *fiber* of p, F_p = {k·p : k ≤ n/p}, is closed under maximal factors except through the *hub* k = x/p, and
F_p is a copy of board ⌊n/p⌋ with the layer shifted by one, in which every member has one extra factor (its hub)
that no other member of F_p lists.  Hence a fiber alone, with its hubs available, is always playable; all of a
layer's difficulty is hub contention between fibers and with the smooth members, and GF(2) sees hub capacity
(column k used once) exactly.  What it misses is the order: a precedence cycle through hubs (P3: flat) alternates hub
edges (the user of hub a precedes every other lister a·p') with chains inside fibers.  T11's cycle at 2176 is 27P₂
pays 27 → 27P₁ pays 9P₁ → 18P₁ pays 18 → 18P₂ pays 9P₂ → 27P₂ lists 9P₂.  For p > n/200 the hubs are below 200 and
are never moves at the end of the chain (lightest promotion 1172 at 5000), so hub *states* are not search variables.

**Measured (here).**  In layer 4 at 5000, H's residual (73 members) is entirely fiber members, in 5 distinct minimal
cores from 60 random orders, pairwise disjoint and compatible: the templates T11, T14, T23 of the brief, lifts of the
cores of boards 45-105 over primes 43-241.  In layer 5 the fiber members peel on their own (N5).

**Idea.**  Because the layer-4 cores are lifts of a finite list of base cores (the brief's conjecture in direction
2), and the lifts over disjoint prime sets meet only at hubs whose states are fixed, a *template catalog* (base core,
hubs, fiber factors, and the cheapest repair of each lift as a function of its primes) is a local correction to the
bound: PB minus the provable loss of each template instance.  The rectangle swap (m₂ − m₁)(P₂ − P₁) of the brief's
3.4 is the simplest such loss.  Proof route: an exchange argument on the template's fibers, since by the fiber
reading the only way out of a lifted core is through a hub or through a fiber factor of the same fiber.  I have not
proved it; it is a conjecture with a cheap test (E5).  What it would take off the gap: layer 4's share, which by the
census is the negative term at most boards from 4000 on (the bound plays *fewer* layer-4 numbers than the optimum
and more of layer 5), so the template losses are real but the layer-5 smooth knot is the larger term.  Rank it
second, after 1.1, and only in layer 4.

### 1.3 Nogoods carry over from game n − 1 to game n

**Claim (proved).**  A conflict is a set K of members of one layer instance that is unplayable given the promoted
columns D it lists; it is a fact about the lists of K's members, i.e. about mf(x) ∩ [1, n/2] for x ∈ K.  For odd n
the numbers up to n/2 are those of board n − 1, so every list is unchanged and every conflict of game n − 1 is a
conflict of game n.  For even n the one new column m = n/2 is listed only by its multiples in the layer above, i.e.
by n = 2m itself, which was not on board n − 1; m keeps its own list, so every conflict of game n − 1 survives in
this case too.  (Adding a row never breaks a conflict; adding a column never creates one, brief 1.5.)  The frame
solver's nogoods are stated on candidates of frames, which may be renumbered between games; the transfer must map
them by number.

**Already measured by the project (the coordinator, from the notebook of 2026-10-15 and today): not worth it.**
Carrying re-validated nogoods into the next game made the next search 1.31× *slower* in CPU over eight pairs of
1463-2172; consecutive searched games keep the same root gap and relearn many of the same nogoods, but their trees
share a median 0.15% of their steps, and perfect reuse would save only 1.2-1.4×.  The chain carries a store since
about 4980 (checked at the next root, used only to prune); four games of 4848-4872 proved standalone took 1.25-1.5×
the chain's nodes.  So the claim above is true and useless: proof costs come from each game's own search.  What the
same notebook entry found worth carrying is *bound structure*: the multi-field bound's signings and multipliers
carry with no check and close a median 0.75 of the next root's own share with no refit.  That bears on 1.1: a
smooth-exact bound or a smooth-core catalog is bound structure of exactly that kind, and the smooth sub-board changes
between consecutive games only when n or n/2 is smooth, so it would carry across games the way the signings do.

## 2. Limitations

### 2.1 What one matroid can exclude (measured here)

The brief's lemma: if minimal cores C₁, C₂ share e and (C₁ ∪ C₂) ∖ e is core-free, no matroid containing the playable
sets has both as circuits.  Call such a pair *incompatible*.  elim.py samples minimal cores of H's residual by random
deletion orders, tests every pair sharing a member over each shared member, and computes the exact independence
number of the incompatibility graph: the most of the sampled cores that any one matroid could exclude.

| n | layer | residual | distinct minimal cores sampled | sizes (min/median/max) | pairs sharing a member | incompatible | **most a matroid can exclude** |
|---|---|---|---|---|---|---|---|
| 1000 | 4 | 56 | 45 | 16/23/33 | 990 | 414 | 6 |
| 1000 | 5 | 34 | 9 | 25/26/30 | 36 | 36 | 1 |
| 2176 | 4 | 109 | 50 | 11/41/57 | 1207 | 601 | 7 |
| 2176 | 5 | 70 | 48 | 26/37/47 | 1128 | 651 | 5 |
| 2176 | 6 | 43 | 27 | 15/27/33 | 351 | 144 | 6 |
| 5000 | 4 | 73 | 5 | 11/14/23 | 3 | 0 | 5 |
| 5000 | 5 | 171 | 56 | 20/55/78 | 1534 | 693 | 8 |
| 5000 | 6 | 98 | 56 | 29/38/52 | 1540 | 596 | 10 |
| 5000 | 7 | 40 | 25 | 23/25/29 | 300 | 203 | 4 |

(80 random orders at 1000 and 2176, 60 at 5000; the sample is a lower bound on the number of minimal cores, so the
true fraction excludable is smaller still.)  So in the knots of layers 5-7 a matroid can exclude roughly one core
in six to ten, and the excluded family must be pairwise compatible, which the knot's overlapping cores rarely are.
Layer 4 at 5000 is different: its 5 cores (the templates) are disjoint and all compatible, so a matroid *could*
exclude all of them; that is consistent with their being small lifted patterns (Section 1.2).

Caveat on the lemma's reach: a matroid can also exclude a set Z ⊋ K that is an M-circuit without K being one, so
"excludes K" here means "has K as a circuit"; but any M-dependent set contains an M-circuit, which contains a core,
and the elimination argument applies to all circuits, so the excluded family of core-containing circuits is still
elimination-closed.  The measured numbers bound the minimal cores only.

**Conclusion (proved + measured):** replacing a layer's GF(2) block by any single matroid leaves the knot nearly
intact; every stronger relaxation needs three or more matroids coupled by multipliers, or integer reasoning.  That
is form (a) of the brief's direction 1 closed, and form (b) left.

### 2.2 Averaging over twin swaps does not give an n² integrality gap by itself

The brief's direction 8 proposes to show an integrality gap of order n² for LPs with cover cuts of bounded-size cores
by averaging fractional solutions over twin swaps.  The obstacle: at the end of the chain the knots' members are mostly
sources, fixed in.  T11 at 5000 has one non-source member (1788 = 12·149); its cover cut, with the ten sources at 1,
is the bar x₁₇₈₈ = 0, which no average over swaps of 1788 with 12·p' can satisfy unless every 12·p' is at 0.  So the
average over the twin group of H violates exactly the cuts of cores with ≤ 1 free member, which are the ones the LP
turns into fixings.  A limitation theorem for cover-cut LPs needs a model of the *chain* of near-equal alternatives
(bar 1788 → the next heaviest set holds another template with another free member → ...), i.e. of the knot's density,
not a single averaging.  I did not find one; the smooth/fiber split suggests the chain is a chain of fiber choices
hanging off one smooth knot, so a counting model of the fibers (how many twins per cofactor, how many are needed to
exhaust the hubs) is the place to look.  Left as a direction, labeled conjecture.

### 2.3 Why the record of Section 4 looks the way it does

Every method in the brief's table acts on cores one at a time (a cover cut, a rank cut, a signing built for a core,
a conflict's images), and reports a share that falls with the gap.  The split of Section 1.1 explains both: the
obstruction is one smooth knot per layer (one connected residual of 101 smooth members at 5000), whose minimal cores
overlap in dozens of ways (56 sampled; N4), while the *heaviest set's* freedom is in the fibers (184 members that peel
on their own; twins by the dozen per hub).  A constraint on one core is met by moving one fiber member; the smooth
knot is untouched and the next core is ready.  Only a constraint stated on the whole smooth configuration (Section
1.1) or integer search gets past it, and the per-frame exact bounds that did (hybrid, exact frame 2) cost a proof
because they solved the fibers too.

## 3. Cheap checks run

All in /home/brian/taxman_work/lab/work/oddcore/study-1/ (scripts, outputs *.out, and notes.md with the raw tables),
single-threaded, each under a minute except pbsmooth.py.

1. **fibercheck.py, fibercheck2.py** (N3, N5, N6 in notes.md): H's layer instance split into members whose largest
   prime is > T = ⌊√(n/8)⌋ (or > B) and the rest, each peeled on its own.

   | n | layer | full residual | fiber-only members / residual | smooth-only (p ≤ 23) members / residual |
   |---|---|---|---|---|
   | 2176 | 4 | 109 | 199 / 16 (= T11 on 61, 67, 107) | 83 / 49 |
   | 2176 | 5 | 70 | 76 / 0 | 68 / 53 |
   | 3000 | 5 | 103 | 97 / 0 | 85 / 67 |
   | 4000 | 4 | 93 | 346 / 46 | 94 / 0 |
   | 4000 | 5 | 166 | 149 / 32 | 101 / 99 |
   | 5000 | 4 | 73 | 433 / 73 | 100 / 0 |
   | 5000 | 5 | 171 | 184 / 0 | 115 / 101 |
   | 5000 | 6 | 98 | 63 / 0 | 89 / 86 |
   | 5000 | 7 | 40 | 20 / 0 | 52 / 30 |

   By smoothness bound at 5000: the 13-smooth members of layer 6 stall by themselves (54 of 54); layer 5 needs
   B = 19 (82 of 95 stall) and B = 23 (101 of 115).  Lightest promotion: 452 at 2176, 1172 at 5000, in H and S*
   alike, so hubs below 200 are never moves there.
2. **elim.py** (Section 2.1): the incompatibility graph of sampled minimal cores and its independence number.
3. **smoothcat.py** (N6): the smooth knot of layer 5 at 5000 has ≥ 222 distinct minimal cores (300 random orders,
   count still growing linearly), sizes 32-69, free members 9-24 each.
4. **pbsmooth.py**: a best-first branch and bound for PB_s(n) in Python (parity bound with picks and bars; branch on
   a minimal smooth core's free members and promoted columns; the first node whose heaviest set is smooth-playable
   is the answer).  Finished: **PB_13(1000) = 315,581 in 8 nodes, 28% of the gap** (one bar, 308); PB_7(1000) =
   PB (0%).  Unfinished: B = 23 at 600, 300 nodes, 112,729 → 112,725 (opt 112,623); B = 23 at 1000, 607 nodes
   (63 s), 315,640 → 315,580 (also 28% so far), dodging among layer-4 smooth cores of 16-25 members with 4-10 free
   members.  At these n most numbers are 23-smooth, so the 23-smooth sub-board is most of the board and this is
   close to a full proof.  Finished at 2176: **PB_13(2176) = 1,494,847, 10.6% of the gap of 767, 26 nodes (27 s)**;
   PB_11(2176) = 1,494,860, 8.9%, 9 nodes.  Unfinished: B = 13 at 1500, 157 nodes, 7.7% so far; **B = 23 and B = 19
   at 2176, 159 and 158 nodes (~135 s each), best open bound 1,494,888 in both, so PB_23(2176) ≤ 1,494,888: at least
   5.2% of the gap, true value unknown** (the search was still meeting smooth cores of 26-38 members with 5-14 free
   members at that bound).  The Python search cannot settle the 23-smooth bound at 2176; the measurement that
   matters is E1 at 2176-5060 in the real solver with B = 23.
5. **cores.py at 1000** (N3): the cofactor patterns of the layer-4 cores are K₇₈'s and T11's bases lifted by 13-31
   plus smooth members; the layer-5 cores are 60% smooth.
6. **hubcheck.py**: the hub interface between the smooth and fiber parts of H's layers (Section 4): at 5000, 36, 21,
   9, 4 hubs listed by fiber members in layers 4-7; fiber members stripped of their hubs stall at 90/433, 66/184,
   11/63, 6/20.

## 4. Next step

Run **E1** (the smooth-exact root bound at 2176-5061) and **E6** (what the conflict branching picks) first; both are
cheap and together they decide whether the smooth/fiber split is the right axis for the search.

* If E1 closes ≥ 50% at 4000-5060 without falling, build form (c) or (b) of Section 1.1 and run E2 on nodes.
* If E1 closes little, the remaining gap is in the fiber-smooth mixed cores, and the next question is the hub
  interface.  Measured here (hubcheck.py): at 5000 the fiber members of H's layer-5 instance list only 21 smooth
  columns (hubs) in all, and they need them (stripped of their hubs, 66 of the 184 fiber members stall, one with an
  empty list); layer 6 has 9 hubs, layer 7 has 4, layer 4 has 36.  So the smooth sub-board and the fibers of a
  layer are coupled through a few dozen columns; the exact bound of a layer is "smooth-exact given which hubs the
  fibers take", and a search over hub allotments (21 hubs, each to the smooth side or to one of its fiber listers)
  with the fibers solved as tiny boards is the next decomposition to size.  Note that reserving all hubs for the
  smooth members is *not* a valid relaxation (the fibers may use them); only the smooth sub-instance with all its
  columns available is.
* Nogood transfer (the former E4) is already answered by the project: about 1.3×, below the bar; dropped.

## 5. Experiments requested

The solver team has the machinery for all of these (the hybrid bound, the conflict finder, nogood learning).  Costs
are guesses from the brief's figures.

**E1. The smooth-exact root bound.**  At the roots of 2176, 3000, 4000, 5000, 5060, 5061, 5096, 5140 (the last three
are the first searched games past the end of the chain), compute PB_s(n) = the heaviest set independent at both parities whose
B-smooth sub-instance of every layer is playable, for B = 23 (and B = 13 if the 23 catalog is large), with the
hybrid bound's machinery restricted to the smooth members (exact winnability tested only on them), or by a branch
and bound on smooth promotions with the parity bound.  Report: the share of the root gap closed, the number of
smooth-promotion nodes, the time.  *Confirms* if the share is ≥ 50% at 4000-5060 and does not fall from 2176 to
5060; *kills* the idea as a bound if it is under 25% or falls like the Lagrangian's shares (3.8 points per 100 of
gap).  Cost: a root solve per board, probably seconds to minutes each given that the hybrid bound took tens of
seconds with all of frame 2.

**E2. The same at nodes.**  On a sample of search nodes of one proof at 4000-5060 (as in the brief's "40 of 45 nodes
of gap < 1000" test): how many nodes does the smooth-exact bound cut that GF(2) does not, by node gap band (< 300,
300-1000, ≥ 1000)?  *Confirms* if it cuts a fixed share at every band (the brief's bar: 25% of the gap at every
node); *kills* if it cuts only nodes of small gap, as the refitted Lagrangian did.

**E3. Size of the smooth core catalog.**  At 5000 and 5060: enumerate all minimal cores of the smooth sub-instances
over all smooth configurations reachable in the search (or: run the search with smooth-first branching and count
the distinct smooth conflicts met).  Report the count, the size distribution, and the number of *free* literals per
nogood (free members plus promoted columns).  *Confirms* if the catalog is in the thousands or less and most
nogoods have ≤ 6 free literals (then propagation does the work at microseconds a node); *kills* if it is
unbounded or the nogoods are long.  Cost: one instrumented run.

**E4. Nogood transfer.**  Withdrawn: already measured by the project at about 1.3× (Section 1.3).

**Order.**  E1, E5 and E6 first (the coordinator's plan); E2 and E3 only if E1 is promising.  If E1 confirms, also
record whether the smooth-exact value at the root of game n, computed once, is still the smooth-exact value at the
root of n + 1 when neither n + 1 nor (n + 1)/2 is 23-smooth: that is the carry-across-games property of Section 1.3.

# Round 2 (after E1, E5, E6; 2026-11-10)

*Status: round 2, written after the results in e1/, e5/, e6/.  The round-1 sections above stand as written; what
they predicted is settled here.  Raw tables of this round: study-1/notes.md, entries R1-R4.*

## 6. What the experiments settled

* **E1.**  PB_s (B = 23) closes 55% at 2176 and 27-38% at every board from 3000 to 5096 (31.5% at 5061, 28.4% at
  5096; ≥ 34.6% at 5140, still running).  Not the 50% I asked for, but a share that does not fall with the gap,
  which no relaxation in the brief's record had.  PB − PB_s is the same number, 959, at 5060 and 5061 (same smooth
  sub-board), 949 at 5096: the carry-across-games property holds.  Cost: 264k-282k best-first nodes at 20 ms (from
  scratch) at 5060-5061, 22-25 min on 4 threads; the depth-first form with warm starts should be ~1 ms a node.
  What is left at every leaf is the same smooth knot re-tied through one or two fibers of primes 31-53 per layer
  (R2 in notes.md, measured here from E1's leaves: at 5000 the 31-smooth members of the leaf's layer 5 already
  stall by themselves, 104 of 145; layer 7 needs 31, layer 8 needs 37, layer 6 at 5060 needs 41).
* **E5.**  Templates as local losses: killed.  Their repairs need smooth drops outside the template in 35 of 52
  instances; only T14 has a formula.  Idea 1.2 is withdrawn as a bound; the templates remain a fiber-only residual
  of layer 4 (R2).
* **E6.**  The search already branches on the smooth knot where the weight is (85-89% of subtree weight; 92-100% in
  layers 5-7); fiber branchings are small deep subtrees of gap < 300.  So form (b) of 1.1, smooth-first branching,
  is already in effect, and any gain must come from the bound (form (c)) or from reusing its work.
* **E4.**  Carrying nogoods across games: ≤ 1.3×, dropped.  Bound structure carries; PB_s is bound structure.

Reading E1 and E6 together: the outer search is, in effect, an enumeration of the smooth-playable configurations
above the incumbent (E1 left ~900,000 open nodes with bound in (incumbent, PB_s] at 5060), each refuted through its
fiber context in a small subtree.  PB_s does not shrink that enumeration; it is the enumeration.  A tighter bound
on the smooth part (Section 8.1, raising B) shrinks it; a cheaper per-node form of PB_s (Section 7) shrinks the
refutations.

## 7. Turning PB_s into something a proof can use (E2, designed)

### 7.1 The arithmetic that any node-level use must beat

Let the outer search's node count follow the brief's fit N(g) = 10^(3.85 + g/476) in the root gap g (0.67 ms a
node at 5000).  A bound that is tighter by r at every node makes the tree that of a game of gap g − r, i.e.
10^(r/476) times smaller; if it costs c extra milliseconds a node the proof costs N(g − r)·(0.67 + c).  So the
extra cost pays only if

    10^(r/476) > 1 + c/0.67,

i.e. r > 476·log₁₀(1 + c/0.67).  At 1 ms an inner node (the depth-first form), an inner search of b nodes must buy

| inner nodes b | 1 | 3 | 10 | 30 | 100 | 1,000 |
|---|---|---|---|---|---|---|
| reduction r needed to break even | 190 | 350 | 570 | 790 | 1,040 | 1,510 |

against PB − PB_s = 959 at the end of the chain.  **So the whole of PB_s (959) is worth at most ~70 inner nodes a node, and
a 10× saving needs it in ~7.**  At the root the E1 search needed ~3,300 nodes for half the reduction and ~100,000
for 90% (e1/README.md, convergence).  Nothing like that can run at every node.  The proof-cost case for E2 is that
*deep* nodes are different: most of the smooth literals are fixed there (E6: 99% of branchings sit at nodes with
24 or more promotions), so the inner search at a deep node may be a handful of GF(2) solves.  That is the one
number E2 must measure, and it cannot be guessed from the root.

For a proof near 5061 (gap 3,049): plain, N = 1.8 × 10¹⁰ nodes ≈ 3,400 CPU-hours by the fit.  If PB_s held its 959
at every node for c ≤ 3 ms, the tree would be that of gap 2,090, 1.7 × 10⁸ nodes, ≈ 170 CPU-hours: the cost of a
game at the present end of the chain.  At c = 10 ms, 500 CPU-hours; at c = 70 ms, break-even with the plain proof.

### 7.2 The design: a budgeted depth-first smooth test, run where it can cut

At an outer node v with GF(2) bound PB(v) and incumbent T (gap g_v = PB(v) − T):

1. **Skip** when g_v > r_max, the most the smooth test can take off (959 at B = 23 near 5060; take the root's
   PB − PB_s).  The test cannot cut there, and the subtree below will bring nodes into range.
2. **Otherwise run the test**: a depth-first search over smooth conflicts, warm-started from v's `Gf2Bound`
   (`push_all` / `remove_candidate`, the children's certified bounds from the exchange graph without a solve), with
   target T: it stops at the first smooth-playable set above T (no cut) or when every node is at or below T (cut),
   with a **budget** b of GF(2) solves.  Over budget: no cut, continue the outer search as usual.
3. **Every smooth conflict met goes to a global store** (valid at every node of the game and at the next games with
   the same smooth sub-board, e1/README.md): a node's heaviest set is checked against the store before the peel and
   the deletion filter, and a stored conflict all of whose literals but one are fixed at v forces the last one out.
4. **The root test is run once per smooth sub-board** (it changes only when n or n/2 is 23-smooth, about one game in
   ten past 5000), and its value PB_s(root) seeds r_max and the store.

The test is exact within its budget: a cut is a proof that no family member above T extends v's fixings (the same
argument as E1's validity, with v's picks and bars added), so the outer search stays sound; a missed cut costs only
time.

### 7.3 What E2 measures, and what kills it

Sample outer nodes from a standalone proof with a trace (e6 has one for 4848: 13.5M branchings with gap bands and
subtree sizes), stratified by gap band: 60 nodes each in g_v ∈ [100, 300), [300, 600), [600, 959), [959, 1,500).
At each, run the depth-first smooth test with B = 23, target = the proof's incumbent, warm-started, budget 10⁴
solves, and record: cut or not; GF(2) solves used; the reduction reached (PB(v) − best open bound at the stop); and
from the trace, the node's outer subtree size.  Then for each policy (threshold r_max, budget b ∈ {3, 10, 30, 100,
1,000}) compute over the sample

    saved = Σ_cut (subtree − solves used),   wasted = Σ_uncut solves used,

scale by the band's population in the trace, and report the proof-cost ratio (new/old) for 4848 and, through the
fit, for 5061.  Also record how often a stored conflict (from the root run) settles a node without a solve.

*Confirms* if at nodes of gap 300-959 the test cuts most nodes within b ≤ 10 solves (then the 5061 proof costs
about what 5060 did, by 7.1); *marginal* if it needs 30-100 (a 2-3× gain at best, worth having only if it carries to
larger n); *kills* if cutting a node of gap 300-959 costs as many solves as its subtree has nodes, as the hybrid
bound did (median 1.08×).  Cost: one instrumented run over 240 nodes, each ≤ 10⁴ solves at ~1 ms: under an hour.

### 7.4 Cheaper forms, if the full test is too dear

* **A cut at one level** (b = 1): price each literal of a stored smooth conflict with the weight split (certified from
  the exchange graph, no solve); cut when every literal's exclusion bound is ≤ T.  Worth one exclusion, ~70 points
  (the brief's knot measurement), so it cuts nodes of gap < 70 only; the solver's own conflict branching already
  does as much.  Not worth building on its own.
* **Pricing with PB_s at the root** (forced members): x is forced in when PB_s(bar x) ≤ T.  With PB_s(bar x) ≈
  PB(bar x) − r, x is forced when its exclusion cost is ≥ g − r (2,090 at 5061) instead of ≥ g (3,049).  Few
  candidates have exclusion costs in that window (sources are fixed already, and fiber twins cost tens), so I expect
  few extra fixings; cheap to count (E9).
* **Raise the reduction instead of lowering the cost**: Section 8.1.

## 8. More ideas, ranked

### 8.0 PB_s with fiber hub demands (new; validated at E1's leaf for 5000)

**The idea.**  PB_s lets the smooth members use every smooth column.  But the fibers need hubs too: in layer k, the
members of fiber p (largest prime p > B) pay with a fiber factor (m/q)·p or with their hub m, and at most ν_p of
them can pay with fiber factors, ν_p the maximum matching of fiber p's members into its unpromoted fiber factors.
So at least d_p = |members of fiber p| − ν_p of them pay with hubs, distinct hubs that they list, and those hubs
are then paid, hence unavailable to the smooth members.  Define

    PB_sh(n) = max { ΣI : I independent at both parities, and in every layer there is an assignment of d_p distinct
                     hubs to each fiber p, from the hubs its members list, such that the smooth sub-instance of I
                     is playable without the assigned hubs }.

*Valid (proved, sketch).*  In a playable S, each column of a layer is paid by at most one member (the payer takes
it), so the fiber members' hub payments are distinct and are not the smooth members' payments; the members paying
with fiber factors form a matching into the unpromoted fiber factors, so the hub payers of fiber p number ≥ d_p.
Order the smooth members as in the game; each pays a column not listed by any earlier smooth member (an earlier
lister would have taken it); so with the fiber-paid hubs removed the smooth sub-instance back-peels from the last
member.  Hence opt ≤ PB_sh ≤ PB_s.  (Columns divisible by p² and hubs that are not smooth only weaken the demand or
widen the assignment, which keeps the bound valid.)

*Measured here (study-1/hubdemand.py, R5 in notes.md).*  At E1's leaf for 5000 (23-smooth-playable in every layer),
the demands are: layer 5, 11 fibers (31, 37, 47, 53, 59, 61, 71, 83, 113, 199, 311) demanding 18 hubs of the 21
listed; layer 3, 21 fibers demanding 29; layer 4, 11 demanding 11; layer 6, 4 demanding 4; layer 7, 3 demanding 3;
layer 8, 1 demanding 1.  **In layers 7 and 8 no assignment keeps the smooth sub-instance playable** (2 and 1
assignments, all tested), so PB_sh < PB_s at 5000; in layers 5 and 3 none was found in 200,000 assignments (the
search was cut off), in layers 4 and 6 one exists.  So the condition bites where PB_s stops, and it does so through
the *counting* part of the hub coupling, which no twin swap changes: a twin m·p' has the same cofactor, lists the
same hub, and needs a fiber factor of its own fiber.

*Cost.*  The demands are matchings (microseconds); the assignment search is a small DFS with monotone pruning (a
partial removal that already stalls the smooth members cannot be completed), over at most a few hundred hubs per
layer; it runs at E1's leaves only, and when it fails the branching literals are the stalled smooth cores' literals
plus the free members and promoted fiber factors of the fibers with demand.  So it adds little to E1's cost per
node and nothing to the outer search's.  *What it would take off:* unknown; it removes the mixed cores whose fiber
part is a hub shortage, which R2 says is the shape of what survives PB_23 (one or two fibers per layer tied to the
smooth knot).  It is complementary to raising B (8.1): B captures the *order* coupling of fibers 31-41 exactly,
the demands capture the counting coupling of *all* fibers at no cost.  **E11** measures it.  Rank: first.

### 8.1 Raise the smoothness bound: PB_s with B = 31-41 (the next tier of the same knot)

**Measured here (R2).**  At E1's leaf for 5000 (a set that is 23-smooth-playable in every layer), the members of
layer 5 whose primes are all ≤ 31 stall by themselves: 104 of 145; with B = 37, 117 of 156.  Layer 7 needs B = 31
(30 of 59 stall), layer 8 needs 37 (23 of 31), and at 5060 layer 6 needs 41 (81 of 112).  The sampled minimal cores
of the leaf's residual are 51 smooth members plus fibers of 31 and 37; 31 smooth plus 31 and 47; 36 smooth plus 41,
61, 103, 151.  So what survives PB_23 is the same knot, re-tied through one or two fibers of primes 31-53 per layer,
and the fibers of 31-53 are copies of boards 94-161, which have odd cores of their own (K₇₈'s base lifted).

**The idea.**  Same bound, same machinery, B raised to 31, 37 or 41: those fibers join the exact part, so their
twins (m·31 ↔ m·37) are inside the exact search and no longer a dodge.  Validity as before (proved).  The cost
grows: the B-smooth promotable set at 5000 is 235 numbers at B = 23 and roughly 300-350 at B = 41 (the fibers of
29-41 add their layer-4 and layer-5 members below n/2), and the smooth sub-board then changes between games about
twice as often (n or n/2 41-smooth).  The gain: by R2, the next layer of the knot in every layer; a guess is a
share of 50-60% at 5000-5100 against 28-37% now, and the increments (PB_23 − PB_31, PB_31 − PB_41) say how much
sits in each tier.  What kind of improvement: a tighter root bound that carries across games; its use at nodes is
Section 7's question again with a larger r (the break-even table says r = 1,500 buys 1,000 inner nodes).  **E8**
measures it.  Rank: first, because it is the only idea here with a measured handle on what it would remove.

### 8.2 A fixed GF(3) signing for the lifted templates of layer 4

**The fact (proved, B5 and P10).**  Any signing of a layer's block over any field gives a matroid that contains
the playable sets, so PB with layer 4's GF(2) block replaced by a GF(3) block with signing σ is a valid bound, still
a two-matroid intersection with a weight-split certificate.  The brief found that fixed signings close 2-9% because
the bound moves to a core the signing does not see, and that signings built for met cores (A1) fragment.

**The twist.**  The layer-4 residual at 5000 is the three templates and nothing else (R2); at 5060 the templates
plus 48 smooth members.  A template is a lift: its members are m·P for cofactors m of a fixed base pattern and
primes P that vary with n, its columns the hubs m and the fiber factors (m/q)·P.  A *uniform* signing, σ(m·P,
(m/q)·P) = s(m, m/q) and σ(m·P, m) = h(m), depends only on the cofactors, so it is the same in every fiber and at
every n, and it kills every instance of the pattern at once if it kills the pattern — the twin dodge (the same
template on other primes) does not escape it.  The base patterns have 10-30 cofactor edges, so the signings can be
searched exhaustively (study-1/signcheck.py; result in Section 10).  The loss to guard against: a signing that is not
balanced on an even cycle of two-factor members makes that cycle GF(3)-independent, which GF(2) excluded; a uniform
signing on template cofactors touches wide members' rows only, but a wide member becomes a two-factor member when
one of its factors is promoted, so the check is PB_σ ≤ PB at every census board.

**Checked here, and killed in this form (signcheck.py, signcheck2.py).**  Of the 16,384 uniform signings of T11
(9 cofactor edges, 5 hubs), *none* makes the instance at 5000 (primes 149, 157, 241) or at 2176 (61, 67, 107)
dependent over GF(3).  Signings exist, as B5 says: 3% of random entrywise signings (28 entries, one sign each) kill
T11 at 5000, and 12% kill K₇₈; but they give the same cofactor edge different signs in different fibers of the
instance, so they cannot be fixed once for all primes, and a signing built for one instance is dodged by the same
template on other primes, which is what the brief's A1 found.  (The rank code was checked on the theta core of
board 45, dependent under the plain signing as its determinant 3 requires, and on K₇₈, independent as its
determinant 1 requires.)  T14 (22 keys) and T23 (32 keys) were not searched; T11 is the commonest template (22 of
E5's 52 instances), so the idea does not survive without it.  **Withdrawn; E10 withdrawn with it.**  What remains
of it: a third matroid per instance met, which is A1, already measured.

### 8.3 Interval certificates for the far end of the chain

Not a bound: a different product.  A proof that opt(n) ≤ best-known + δ costs what a game of gap (gap − δ) costs:
by the fit, δ = 476 buys a factor 10, δ = 959 a factor 100.  For the objective "excellent games to 10,000 and a
claim that most are optimal", a certified interval [best-known, best-known + δ] with δ of a few hundred (0.01% of
the score at 5000) is a weaker but affordable statement for the games whose gap is 3,000-5,000, and it needs no new
code: the incumbent is raised by δ.  Worth stating because the brief's Section 5.3 shows that the first 500 games
past 5060 need only a 4-24% reduction to reach 10⁹ nodes, which an interval of δ = 150-800 supplies outright.
Rank: third, as a fallback the owner may or may not want; it is sound and immediate.

### 8.4 Root forcing with PB_s (cheap, probably small)

x is forced in when PB_s(bar x) ≤ incumbent; with PB_s(bar x) ≈ PB(bar x) − 959 the forcing threshold on x's
exclusion cost drops from the gap to the gap − 959.  Each test is an E1 run with x barred, which should be much
shorter than the root's (a bar lowers every bound).  I expect few candidates in the window, since the costly
exclusions are sources (fixed) and the rest are twins costing tens; but a dozen fixings at the root of 5061 would be
worth having, and the count is cheap (E9).  Rank: fourth.

### 8.5 What I looked at and do not recommend

* **Per-fiber exact tables** (fibers of large primes are boards ≤ 200): a fiber alone is always playable, so the
  table would have to be indexed by hub availability, 2^(hubs listed) entries; and E6 says the fiber subtrees are
  already small.  Gain under 15%.
* **Payment or hub branching** (round 1, N2): projections never see precedence cycles.
* **Enumerating smooth-playable configurations and solving fibers below each**: ≥ 900,000 configurations above the
  incumbent at 5060 (E1's open nodes); that is the outer search's size, not a saving.
* **A conditional proof with the smooth part fixed from game n − 1** (the optimum's smooth configuration seems to
  change only when the smooth sub-board does): unsound as a proof; usable only in the unsound mode as a heuristic.

## 9. Experiments requested, round 2

**E11. PB_sh, the hub-demand strengthening (Section 8.0).**  Add to E1's leaf test: compute each fiber's demand
d_p (matching into unpromoted fiber factors), then a DFS over assignments of d_p distinct listed hubs per fiber with
monotone pruning, testing the smooth sub-instance without the assigned hubs; a leaf passes only if every layer has
an assignment.  When a layer has none, branch on the literals of the stalled smooth cores met plus the free members
and promoted fiber factors of the fibers with demand (a partition, as E1's).  Run at 2176, 3000, 4000, 5000, 5060,
5061 with B = 23 and report PB_sh, the share, nodes and time, and at the leaf the demands by layer.  *Confirms* if
the share rises by ≥ 10 points over PB_s at 5000-5061 at ≤ 2× E1's time; *kills* if it rises by < 3 points (then
the leftover is the order coupling, and only 8.1 remains).  Cost: E1's machinery plus a day of coding; runs of
minutes to an hour per board.

**E2 (Section 7.3), the node-level test.**  Confirms if nodes of gap 300-959 are cut within ~10 GF(2) solves;
kills if cutting costs as many solves as the subtree has nodes.  Under an hour on 4 threads.

**E8. PB_s with a higher B.**  E1's program at 4000, 5000, 5060 with B = 31, 37, 41 (and 47 if 41 is affordable),
reporting share, PB − PB_s, nodes, time, and the leaf's residual by largest prime as in R2.  *Confirms* if the share
reaches ≥ 50% at 5000-5060 with a root time ≤ 1 hour on 4 threads; *kills* if each step of B adds under 5 points
of share or the time grows more than 10× per step.  Also record PB_s at 5061 with the same B, to see whether the
carry (PB − PB_s equal at 5060 and 5061) survives the larger smooth sub-board.  Cost: 3 boards × 3-4 values of B,
each up to an hour: half a day of 4 threads.

**E9. Root forcing with PB_s at 5061.**  List the candidates of the heaviest set whose exclusion bound PB(bar x)
lies in (incumbent, incumbent + 1,200]; for the 30 cheapest, run E1 with x barred and report whether PB_s(bar x) ≤
incumbent (x forced).  Likewise for the 30 best numbers outside the heaviest set with PB(pick x) in that window
(x barred if PB_s(pick x) ≤ incumbent).  *Confirms* if ≥ 15 of 60 are fixed; *kills* if < 5.  Cost: up to 60 short
E1 runs, a few hours on 4 threads; stop early if the first 10 fix nothing.

**E10. The template signing.**  Withdrawn: no uniform signing kills T11 (Section 8.2).

**E7 (optional, cheap).**  In mixed conflicts, prefer barring a smooth member (E6 shows no preference now): one
standalone proof of 4848 with the rule, node count against 13.5M branchings.  *Confirms* at ≤ 0.7×; *kills* at
≥ 0.95×.  Cost: one proof, ~10 CPU-hours.

Order: E11 and E8 first (root-only, cheap, and they compose: the best bound is PB_sh at the larger B); E2 next if
the owner wants the bound inside the search at all; E9 and E7 last.

## 10. Cheap checks of round 2

1. **leafres.py** (R2): E1's leaves at 5000 and 5060 rebuilt from leaf_promotions (weights agree with PB_s), their
   residuals by layer split into smooth and fiber members by largest prime, the stall of the B-smooth members alone
   for B = 29-53, and sampled minimal cores with their fiber primes.  Table in R2.
2. **signcheck.py, signcheck2.py**: exhaustive search over the 16,384 uniform GF(3) signings of T11 at 5000 and 2176:
   none kills it; random entrywise signings kill it 3% of the time (611 of 20,000) and K₇₈ 12% of the time; the rank
   code verified on the theta core of board 45 (plain signing kills, det 3) and K₇₈ (plain does not, det 1).  T14 and
   T23 skipped (2²² and 2³² signings).
3. **hubdemand.py** (R5): at E1's leaf for 5000, each fiber's hub demand per layer (matching) and an exhaustive or
   200,000-assignment search for a hub assignment that keeps the smooth sub-instance playable: none in layers 7 and 8
   (exhaustive), none found in layers 3 and 5 (cut off), one in layers 4 and 6.  7.5 minutes.

**E5. Templates as local losses (layer 4).**  At 3500, 4500, 5000, 5060: list the layer-4 residual's minimal cores
with their base pattern (members divided by their largest prime) and primes; for each template instance compute the
cheapest repair found by the solver (the loss in S* on that template's numbers).  *Confirms* the local-loss
conjecture if the repair is always inside the template's fibers and hubs and its cost is a function of the primes
only; *kills* if the optimum repairs templates through numbers outside them (as it did at 5000 through 1413 = 9·157,
which *is* in T11's fiber of 157, so that case confirms).  Cost: a script over existing results.

**E6. Which members the conflict branching picks.**  In one proof at 4000-5060, classify every branching's conflict
members as smooth (primes ≤ 23) or fiber, and the member chosen to bar.  If the search already branches mostly on
smooth members, idea (b) of Section 1.1 is nearly what it does and the gain must come from the catalog (a); if it
branches on fiber members (the twins), smooth-first branching is a real change.  Cost: instrumentation of one run.

# Round 3 (after E11 and E8; 2026-11-10)

*Status: round 3.  The question: PB_sh is nearly exact where it finishes (92.4% at 3000, PB_sh = opt + 56); how to
make it finish at 4000-5060, and then use it.  Raw notes: study-1/notes.md, R6-R8.*

## 11. What E11 and E8 say

* **PB_sh (B = 23)**: 73.8% at 1000, 55.0% at 2000, 72.1% at 2176 (5.5 s), **92.4% at 3000** (finished, 2.3M
  nodes, 1,103 s on 16 threads); ≥ 64.6% at 4000 (1 h, 8.8M nodes, 7.0M open), ≥ 46.3% at 5000 (1 h, 3.2M nodes),
  ≥ 47.9% at 5060 (1.5 h, 3.9M nodes, 10.3M open).  Within 2× E1's time it adds only 2-8 points at 5000-5060.
* **Every smooth-playable leaf fails the hub test** (hub_failed = hub_checks at every board but the final leaf at
  3000: 2.18M of 2.18M at 5000, 8.18M at 4000).  So the hub condition is as strong as hoped, and the search it
  induces is the problem: a hub conflict has 78-99 literals on average at 4000-5000 (27 at 5060, where the time is
  still E1's smooth branching) and 1.8-2.8 live children; 5.5M distinct conflicts in 8.8M nodes at 4000.
* **The B ladder** (E8): at 4000, 33% (23) → 55% (31, 70 s) → 72% (37, 336 s) → 72% (41); at 3000, 33% for B =
  29-37 and 79% at 47 (16 s); at 5000, 28% (23, 29) → ≥ 35% (31, 37 at 300 s; 47.3% at 31 after 2,634 s) → ≥ 45%
  (47 at 300 s).  Raising B is cheap where the next tier is one fiber and dear where it is many.

### 11.1 Why the tree is large, and what a leaf test cannot do

Two facts set the size of E11's tree.  First, the tree an exact search clears is not "every assignment with bound
above the value" but the tree *its branching rule generates*: a rule whose children keep nearly the parent's bound
makes a long plateau.  Second, PB_sh acts only at smooth-playable leaves, so the *keys* that steer and prune the
search are still GF(2) bounds, and nothing below the first E1 leaf is pruned by the hub condition until a leaf is
met.  Together they explain the numbers: E11's hub conflicts are resolved by barring one of ~90 literals, most of
them fiber members or promoted fiber factors of the fibers with demand, and barring one is met by the heaviest
set with a *twin* (the same cofactor in another fiber, 16·31 for 16·37), whose demand is the same.  The twin
dodge, which the smooth condition removed from the smooth part, is back at the hub conflicts, one literal at a
time: that is the plateau of 5-10M open nodes, and the 1.8-2.8 live children per branching say the search is close
to a chain of such dodges.

So "an algorithm that reaches PB_sh's value without clearing E1's tree" means a **branching rule whose children
both fall, and which a twin cannot undo**.  The hub is the resource the fibers contend for, and it is shared by the
twins; branch on it.

### 11.2 Hub-ownership branching (the proposal)

At a hub conflict in layer k, choose a hub a (a smooth column of layer k's pool) that the fibers demand and the
smooth members need.  Two children:

* **S** ("no fiber member of layer k pays with a"): every fiber member x of layer k with a ∈ mf(x) has coordinate a
  removed from v(x).  Valid: if no fiber member pays a, the set is playable in the instance where the fiber members
  do not list a (a column nobody in a sub-instance pays with can be removed from their lists; back-peel from the
  last mover), hence independent there.
* **F** ("some fiber member of layer k pays with a"): every smooth member of layer k with a ∈ mf(x) has coordinate
  a removed from v(x), including the smooth *sources* in U\*.  Valid by the same argument: the payer takes a, so no
  smooth member pays it.

The two children cover every game, and each changes the matroid itself (a projection of a few rows), which the
parity bound handles as it is: the vectors change, the algorithm does not.  Neither child can be undone by a twin:
S removes a from *all* fibers' listers at once, F from all smooth listers.  In the frame solver the same thing can
be done without a projection API by splitting column a into a_s and a_f at the branching, fiber rows on a_f and
smooth rows on a_s, and deleting one of the two in each child (within each child the capacity is the original
one, so the children are exact; the split is never used unsplit).

What it costs: two GF(2) solves per branching instead of ~2 live children of ~90 priced literals (the same), and
the hub test as before.  What I expected it to buy: both children's bounds falling by a real amount.  The
measurement (11.3) says half of that: S falls hard where sources list the hub, F does not fall at all at the
GF(2) level, and the proposal is revised there (S plus the smooth residual's literals).

Three refinements for the search that computes the value:

1. **Which hub.**  Prefer a hub demanded by a fiber whose members list no other hub (then S is nearly dead: a
   source must fall back on a fiber factor, or the child is infeasible) and listed by many smooth members of the
   stalled residual (then F hurts the knot).  After each hub decision re-run the hub test; branch on smooth literals
   when the smooth sub-instance stalls with the hubs already given away, on hubs when it is the demands that fail.
2. **Keys.**  The children's keys are their solved bounds (two solves a branching; the projection is a change of a
   few vectors, so a warm start from the parent applies).  The one-step certified prices stay for the literal
   branchings.
3. **The value needs best-first; a proof does not.**  To use the bound in a proof the question is "PB_sh ≤ T?"
   with T the incumbent, a depth-first search that prunes at T and never holds a queue; the plateau between T and
   PB_sh is never cleared.  Best-first with its 5-10M-node queue is for measuring the value only.

### 11.3 Measured at E1's leaf for 5000 (hubbranch.py), and what it changes in the proposal

The node is E1's leaf (77 picks, 7 bars, bound 7,869,799 = PB_s; incumbent 7,868,316).  For a hub a of a layer,
the bounds of children S and F, against the bounds after barring single literals of E11's kind.  "Drop" is the
node's bound minus the child's; a negative drop is a child whose projected matroid let the bound rise (a projection
of a *picked* row shrinks the span of the fixed part, so other elements come free; the child's bound must then be
taken as min(parent, child), which is valid since the parent's bound holds for the child's games).

| layer | hub | listers: fiber (sources) / smooth | child S drop | child F drop | literal bars E11 would use: drop |
|---|---|---|---|---|---|
| 7 | 64 (fiber 73's only hub) | 10 (9) / 0 | **946** | 0 | un-promote 2336 = 32·73: 16 |
| 5 | 16 (fiber 311's only hub) | 29 (28) / 0 | **1,364** | 0 | un-promote 2488 = 8·311: 8 |
| 8 | 128 (fiber 37's only hub) | 3 (3) / 2 | **424** | 0 | un-promote 2368 = 64·37: 368; bar smooth 2016, 2160, 2240, 2400, 2496: 66, 210, 290, 312, 378 |
| 7 | 160 (contended, 5 smooth listers) | 2 (2) / 5 | 0 | 113 | un-promote 2232, 2480 (fiber 31): 127, 375; bar smooth 1760: 113; un-promote column 1936: 289 |
| 5 | 150 (contended, 5 smooth listers) | 2 (2) / 5 | −47 → 0 | −47 → 0 | un-promote fiber-31 factors 2108, 2170, 2325, 2356, 2418, 1953: 136, 343, 498, 384, 504, 126 |
| 6 | 112 (contended, 3 smooth listers) | 5 (5) / 3 | 0 | 0 | un-promote 2214, 2296, 2460 (fiber 41): 151, 233, 397 |

Two lessons, which change 11.2:

* **Child S is the orbit-level constraint, and it is decisive exactly where the twin dodge lives.**  "No fiber pays
  hub 64" forces all nine sources listing 64 onto fiber factors at once: a drop of 946 where un-promoting one
  source's fiber factor drops 16, because the one un-promotion is met by promoting a twin (8·p' for 8·311, 32·p'
  for 32·73) and the orbit constraint is not.  The same at hubs 16 (1,364 against 8) and 128 (424 against 368).
* **Child F does not act through the GF(2) bound.**  Removing a hub from the smooth members' rows changes the rank
  little or not at all (0, 0, 113): the smooth knot's need for the hub is an *order* fact, which only the peel sees.
  So F must not be scored by its GF(2) bound; in F the smooth sub-instance without a stalls by construction (the hub
  test failed), and that residual is a smooth core whose literals (free smooth members, promoted smooth columns)
  are the children, with drops of 66-378 here, and which no twin can dodge.

**The proposal, revised.**  At a hub conflict in layer k pick a hub a demanded by a fiber with demand (prefer one
listed by sources with no other hub, then one listed by smooth members of the stalled residual).  Children:

1. **S**: no fiber member of layer k pays a (project a off every fiber lister's row; the bound min(parent, child));
2. **the literals of the smooth residual that stalls once a is removed from the smooth rows**: bar one free smooth
   member or un-promote one promoted smooth column, as E1 does for a smooth core; these children also carry "some
   fiber pays a" (the smooth rows projected), which is what makes them exact as a partition with S.

Against E11's branching (≈ 90 literals, most of them the fibers' free members and promoted fiber factors, 1.8-2.8
live, each met by a twin), this replaces the whole fiber side of the conflict by one child whose drop is the sum
of the twins' escapes, and keeps the smooth side as it was.  Where no smooth member lists a (hubs 64, 16), S is the
only child that costs anything, so the hub is given to the fibers at no cost and the search moves to the next hub;
the contended hubs are few per layer (R5: of the 21 hubs demanded in layer 5, those the smooth residual lists).

What this does *not* settle: whether the tree below is small.  The literal drops at this node (66-504) are large
because the node's 77 picks leave few alternatives; higher in the tree the dodges are cheaper, which is why E11's
band of 369 points under PB_s holds over 8M nodes at 5000 (about 160 points per decade, against the outer search's
476).  E12 measures it; the first number to look at is the drop of child S at the root's first hub conflict.

### 11.4 Combine with B = 37?

Yes, but second.  The two act on different couplings: B = 37 makes the fibers of 29-37 exact (order and counting),
the hub test takes the counting of every fiber; at 4000 B = 37 alone gives 71.8% in 336 s where PB_sh (B = 23)
gave ≥ 64.6% in an hour, and at 5000 B = 31 costs 78× B = 23's thread-time for 47%.  The B ladder is cheap where
the next tier is one fiber (4000: 31 and 37) and dear where it is many (5000); the hub test is uniform.  The order:
first make PB_sh finish with hub-ownership branching at B = 23 (E12); then PB_sh at B = 31 and 37 at 4000 and 5000
(E13), expecting the hub test to carry less of the load as B rises and the smooth search more.  Do not raise B
past the point where the smooth sub-board changes at most games (at B = 41 about one game in five has n or n/2
smooth), or the carry across games is lost.

### 11.5 What the root run can hand to the proof search

* **The branching rule itself, not the bound.**  The outer search's conflicts are 25-32% mixed (E6), and a mixed
  conflict is resolved today by barring one member, which a twin undoes.  The S child of 11.3 applies to the outer
  search unchanged: when a conflict K mixes fiber members and smooth members through a hub a, the children are S
  ("no fiber member of the layer pays a": a projected off every fiber lister, which the frame solver can do with
  the column split of 11.2, a split column and a pick) and, for the case "some fiber pays a", the usual bars of K's
  smooth members and un-promotions of K's promoted smooth columns, with the smooth rows projected.  S replaces the
  bars of K's fiber members, which twins undo, by one child whose drop is the sum of their escapes (946 and 1,364
  against 16 and 8 at the 5000 leaf).  This is the one transfer that can change the outer tree's shape; E14
  measures it on 4848.
* **The conflict store.**  Smooth and hub conflicts are global nogoods (e1/README.md); the running experiment
  loads E1's root cores into a proof of 4848.  Expect little from pruning alone (E4's lesson: the trees of
  different contexts share few steps) and more from propagation, since a stored conflict with all literals but one
  fixed bars the last.
* **Hub assignments.**  The leaf of PB_sh carries, for each layer, a hub assignment under which the smooth part is
  playable.  As a *heuristic order* for the outer search (try the leaf's assignment first) it may find the
  incumbent's structure faster; as a constraint it is not valid (other assignments exist).
* **Cuts.**  The hub conflicts as cover cuts in a Lagrangian: the brief's record says cover cuts of 13-34-member
  cores were weak; these have 27-99 literals.  Not recommended.

### 11.6 What a root-only use buys

* **Proving a game outright** needs PB_sh(n) ≤ best-known.  At 3000 PB_sh = opt + 56, so even the finished bound
  leaves a residual; the residual is what the fibers' order coupling and the layer-4 templates keep.  Outright
  proofs will be rare: no game past 5060 has a parity gap under 2,090, and 92% of that is 170-270 points left.
* **Near-optimality certificates** are the real product: "opt(n) ≤ best-known + δ" with δ = PB_sh − best-known.  At
  3000, δ = 56 is 0.002% of the score; at the end of the chain a finished PB_sh at 90% would give δ ≈ 200-350 (0.003%).
  The certificate is checkable by the prover: the weight split of the leaf's GF(2) bound plus the branching tree
  with, at each leaf, the stalled smooth sub-instance or the failed hub test from the definitions (check_leaf.py and
  check_hubs.py already do the leaf part).  It carries: PB − PB_sh is the same at games with the same smooth
  sub-board (959 at 5060 and 5061 for PB_s), and ceilings, primes and repeats pass a certificate on with their own
  arguments (δ_{n+1} = δ_n at a ceiling game whose best-known is opt(n) + n + 1... only if that ceiling is tight;
  otherwise δ grows by the slack).  For the objective "excellent games to 10,000 and a claim that most are
  optimal", δ of a few hundred at every searched game is a statement the project does not have today.
* **A smaller proof**: a proof with target T = best-known still runs the outer search with GF(2) keys; the root's
  PB_sh does not change those keys.  What changes the outer tree is the branching rule (11.5) and, if E2's
  arithmetic allows, the node-level test.  So root-only use buys certificates and fixings, not proofs.

## 12. Experiments requested, round 3

**E12. Hub-ownership branching in the E11 program** (the revised form of 11.3: child S = "no fiber pays a" with
the fiber listers' rows projected, plus the smooth literals of the residual that stalls without a, with the smooth
rows projected; child bounds min(parent, child)).  Run at 3000 (reference: 2.3M nodes), 4000 (≥ 64.6%, unfinished
at 8.8M) and 5000, best-first for the value, same time limits; log at every hub branching the drop of S and of the best
smooth literal.  *Confirms* if 3000 finishes in under a tenth of the nodes and 4000 finishes within the time limit;
*kills* if S's drop at the root's first hub conflicts is under 100 (then the fibers with demand have alternatives
there, and the twin dodge is not at the hubs), or if the tree is no smaller.  Cost: a day of coding (the E1 program
rebuilds its matroid per node, so a projection is a change to the lists it builds from), runs of an hour.

**E12b. Certificates by target instead of value.**  The same program depth-first with the target best-known + δ,
no queue: it certifies "opt ≤ best-known + δ" when it exhausts.  Run at 5000, 5060, 5061 with δ = 1,200, 900, 600,
300, reporting nodes and time for each (E1's convergence profile predicts seconds for the first and the hour for
the last).  Not a confirm/kill experiment: it gives the δ the project can certify per hour of 16 threads at the
end of the chain, which is the product of Section 11.6.

**E13. PB_sh with B = 31 and 37** at 4000 and 5000, after E12.  *Confirms* if ≥ 80% at both within an hour on 16
threads; *kills* if B = 37 adds under 5 points over PB_sh(23) at 5000.

**E14. Hub-ownership branching in the outer search.**  In the frame solver, for a mixed conflict (smooth and fiber
members sharing a hub), branch on the hub's side with the column split; one standalone proof of 4848 (reference
13.5M branchings, and the 4848 run with the nogood store for comparison).  *Confirms* at ≤ 0.5× the branchings;
*kills* at ≥ 0.9×.  Cost: the solver change (a split column is a new element with a pick), and one proof,
~10 CPU-hours.

**E15. Certificates.**  For 5061, 5096, 5140 and the plain-search casualties 5260 and 5304: the finished PB_sh (or
its upper range at the time limit) as δ = PB_sh − best-known, with the leaf checked by check_hubs.py; the question is
only whether the project wants to publish "within δ".  No new code.

Order: E12 first; E14 in parallel if a builder is free (it does not depend on E12); E13 after E12; E15 is free.

