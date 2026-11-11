# Working notes (the study, 2026-11-10)

Scratch for study-report-1.md.  Each entry is one idea or one check, appended as it is done.

## N1. The fiber reframing (a reading of Section 2.4, proved from the definitions)

A number x = k·p with p its largest prime has mf(x) = {k} ∪ {(k/q)·p : q | k}.  So for a prime p, the *fiber*
F_p = {k·p : k ≤ n/p, p ∤ k} is closed under maximal factors except through the *hub* k = x/p.  F_p is a copy of the
board ⌊n/p⌋ with the layer shifted by one, where every member k·p has one extra factor, its hub k, that no other member
of F_p lists.  Consequences:

* A fiber alone (all hubs available) is always playable: every member has a private factor.  So *all* the difficulty
  of a layer instance at large n is hub contention between fibers and the smooth core (members whose primes are all
  small).  GF(2) sees hub capacity (column k used once) exactly; what it misses is the order.
* A precedence cycle in a layer (P3: flat) that passes through hubs alternates: the user u of hub a (in fiber P)
  precedes every other lister a·P' of a; inside P' a chain of fiber-internal precedences (payments (a'/q)·P' dividing
  the next member) leads to the member of P' that uses some hub b; and so on round.  T11's cycle:
  27P₂ pays 27 → 27P₁ pays 9P₁ → 18P₁ pays 18 → 18P₂ pays 9P₂ → 27P₂ (lists 9P₂).
* For p > n/200 (n = 5000: p > 25) the hubs are numbers below 200, never played at that n (the lightest promotion at
  5000 is 1372).  So hub *states* are not search variables; only hub *assignment* (which fiber's member pays with
  the hub, and when) is.

This is not a bound.  It says where to look: the obstruction is a cycle of hub hand-offs, and each fiber's part of
the cycle is a chain inside a tiny board (≤ 200).

## N2. Payment branching (a search change, not a bound) — weak on its own

Branch on a wide member w of the conflict: children "w ∉ S" and, for each f ∈ L(w), "f is live when w plays".  In
child f: f barred, every other lister of f comes after w so cannot pay with f, hence S∖{w} is playable in the instance
with column f removed.  Valid relaxation: replace v(w) by e_f in the block (proved above by the last-mover argument).
On K₇₈ with w = 30: children "pays 10" and "pays 15" leave K₇₈∖{30} GF(2)-dependent (an even cycle appears),
"pays 6" does not; recursing on 42, 28, ... every payment can be fixed with GF(2) still satisfied, because the
remaining obstruction is the precedence cycle 30→42→63→45→30, which projections never see.  At a leaf where all
payments are fixed the GF(2) bound is just the matching bound.  So payment branching needs precedence reasoning to
finish, and the existing conflict branching already gets there.  Keep as a footnote only.

## N3. Data look: where the knots live, in fiber terms (measured here, parity.py + cores.py)

cores.py at n = 1000: layer 4's minimal cores (23-33 members) mix fibers of 13, 19, 23, 29, 31 with cofactor patterns
{27, 28, 30, 42, 45, 50, 52} (K₇₈'s base), {12, 18, 20, 27, 30} (T11's base), {18, 20, 27, 28, 30, 42}, plus 6-13
smooth members (441, 490, 525, 625, 686, 735, 875 ...).  Layer 5's cores (26-28 members) are 15-17 smooth members plus
fibers of 13, 23, 41, 61 with patterns {36, 40, 54, 56, 60}, {24, 36, 40}, {16, 24}, {16}.

fibercheck.py (H's layer instance restricted to members whose largest prime is > T = ⌊√(n/8)⌋ or > 23, peeled on
its own; and the complement):

| n | layer | full residual | fiber-only (p > T) members / residual | fiber-only (p > 23) | smooth-only (p ≤ 23) members / residual |
|---|---|---|---|---|---|
| 1000 | 4 | 56 | 81 / 0 | 45 / 0 | 55 / 40 |
| 1000 | 5 | 34 | 27 / 0 | 12 / 0 | 37 / 0 |
| 2176 | 4 | 109 | 199 / 16 | 150 / 16 | 83 / 49 |
| 2176 | 5 | 70 | 76 / 0 | 48 / 0 | 68 / 53 |
| 2176 | 6 | 43 | 28 / 0 | 15 / 0 | 47 / 40 |

Reading: in layer 5 (the layer that carries the gap) the fiber members alone peel completely; the smooth members alone
(p ≤ 23) already stall on 53 of 68 at 2176.  So the *obstruction* of layer 5 sits in the 23-smooth part, and the
fibers of large primes are the twins the bound dodges with.  In layer 4 at 2176 the fiber-only sub-instance stalls
on 16 members: that is T11 on 61, 67, 107, a pure fiber core (its hubs 12, 18, 20, 27, 30 are layer 3).  Lightest
promotion at 2176: 452 in both H and S*, so no hub below 200 is ever a move there.

## N4. Elimination graph (measured here, elim.py): what one matroid can exclude

n = 1000, layer 4: 45 distinct minimal cores sampled from 80 random deletion orders (sizes 16-33, union = the whole
residual of 56); 990 pairs share a member; 414 pairs are *incompatible* (some shared e with (C₁ ∪ C₂)∖e core-free).
The maximum set of pairwise compatible cores has 6 members: **no matroid that contains the playable sets can have more
than 6 of these 45 cores as circuits.**  Layer 5: 9 distinct cores (25-30 members), all 36 pairs incompatible: a
matroid excludes at most ONE of them.  (2176 and 5000 running.)

## N5. The layer-5 knot is 23-smooth (measured here, fibercheck.py)

Extending the table of N3 to 3000-5000 (fiber = largest prime > T = ⌊√(n/8)⌋; at these n, T ≥ 19 and the p > 23 split
gives the same numbers at 5000):

| n | layer | full residual | fiber-only members / residual | smooth-only (p ≤ 23) members / residual |
|---|---|---|---|---|
| 3000 | 5 | 103 | 97 / 0 | 85 / 67 |
| 3000 | 6 | 54 | 31 / 0 | 58 / 47 |
| 4000 | 4 | 93 | 346 / 46 | 94 / 0 |
| 4000 | 5 | 166 | 149 / 32 | 101 / 99 |
| 4000 | 6 | 66 | 52 / 0 | 76 / 48 |
| 5000 | 4 | 73 | 433 / 73 | 100 / 0 |
| 5000 | 5 | 171 | 184 / 0 | 115 / 101 |
| 5000 | 6 | 98 | 63 / 0 | 89 / 86 |
| 5000 | 7 | 40 | 20 / 0 | 52 / 30 |

So at 5000, H's layer-5 members whose primes are all ≤ 23 (115 of 299) stall on their own at 101 members, using only
the smooth columns; the 184 fiber members peel completely on their own.  Same in layers 6 and 7.  Layer 4 is the
mirror image: its residual is entirely fiber members (the templates T11, T14, T23), the smooth part is clean.
Lightest promotion at 5000: 1172 (H and S*).

Why this matters: a maximal factor of a 23-smooth number is 23-smooth, so the smooth members of a layer list only
smooth columns, and their lists depend only on which smooth numbers of the layer below are promoted.  Playable sets
are closed under subsets (proved: skip a move; every later pot is a superset).  Hence **"the smooth sub-instance of
every layer is playable" is a valid necessary condition that depends only on the smooth promotion decisions**, a
ground set that grows like a power of log n, and that cannot be dodged by a twin swap (twins m·p ↔ m·p' are not
smooth).  H violates it at every board from 2176 on.

## N6. The smooth knot by smoothness bound, and its core catalog (measured here)

fibercheck2.py at 5000, H's layer instance restricted to B-smooth members, stalled/members:
B = 13: L6 54/54 (L5 clean); B = 17: L6 56/68; B = 19: L5 82/95, L6 74/79, L7 30/48; B = 23: L5 101/115, L6 86/89,
L7 30/52.  So layer 6's knot is 13-smooth and layer 5's needs 17 and 19.

smoothcat.py at 5000, layer 5, B = 23: 115 smooth members, residual 101 over 111 columns, 82 wide; 300 random
deletion orders give 222 distinct minimal cores and the count is still growing linearly (53, 104, 151, 190, 222 after
each 60); sizes 32-69 (median 47); free members (promotable, ≤ n/2) per core 9-24 (median 15).  So the smooth knot's
minimal cores are many (thousands or more) and each nogood has 10-30 free literals: a smooth *core catalog* is NOT a
set of short clauses.  The exact-smooth search is the form that stands, not the clause form.

pbsmooth.py (best-first B&B on the parity bound with smooth-playability, Python): at 600 (B = 23) 300 nodes, bound
112729 → 112725 of opt 112623, unfinished; at 1000, 607 nodes (63 s), 315640 → 315580 of opt 315426 (28% of the gap
so far), unfinished: the conflicts met are layer-4 smooth cores of 16-25 members with 4-10 free members and 3-5
promoted columns; the bound dodges among smooth alternatives too, at n where most numbers are smooth.

## N8. The hub interface (measured here, hubcheck.py)

Fiber members (largest prime > 23) of H's layer instances list these many distinct smooth columns (hubs): 2176: L4 17,
L5 7, L6 3; 5000: L4 36, L5 21, L6 9, L7 4, L8 1.  Stripped of their hubs the fiber members stall: 2176: 43/150, 11/48,
3/15; 5000: 90/433, 66/184, 11/63, 6/20, 1/3 (one member per layer lists only its hub).  So the fibers need the hubs;
"all hubs to the smooth members" is not a valid relaxation, but the coupling between the smooth sub-board and the
fibers of a layer runs through a few dozen columns.

## N9. PB_s at 2176 and 1500 with small B (measured here, pbsmooth.py)

PB_13(2176) = 1,494,847: closes 81 of the gap of 767 (10.6%) in 26 nodes (27 s); bars 810 = 2·3⁴·5, picks 600; the
conflicts met were layer-6 smooth cores of 15 and 27 members (4 and 9 free).  PB_11(2176) = 1,494,860 (8.9%, 9
nodes).  PB_13(1500): unfinished after 157 nodes (54 s), best open bound 709,616 (7.7% of 401 so far), dodging among
layer-5 13-smooth cores of 30 members with 9 free members and 10 promoted columns.  So the 13-smooth condition alone
is worth 28% at 1000 and about 10% at 2176: a falling share, like the brief's relaxations.  The 23-smooth condition,
which is the one that holds the layer-5 knot at 5000 (N6: it needs primes 17-23), is unmeasured past 1000 here.

Addendum (B = 23 and 19 at 2176, 150-node limit, ~135 s each): both unfinished; best open bound 1,494,888 in both,
so PB_23(2176) and PB_19(2176) are ≤ 1,494,888, i.e. they close at least 40 of 767 (5.2%); the true value is lower
(the search was still finding smooth cores at that bound: layer-4 smooth cores of 28-38 members with 11-14 free
members at B = 23, layer-5 cores of 26 members with 5 free and 11 promoted columns at B = 19).  Not conclusive either
way in Python; E1 is the measurement.

# Round 2 (2026-11-10, after E1, E5, E6)

## R1. Digest of the experiments (the project's, not mine)

E1 (e1/README.md): PB_s with B = 23 closes 55% at 2176, 27% at 3000, 33% at 4000, 28.5% at 5000, 37.5% at 5060,
31.5% at 5061, 28.4% at 5096 (≥ 34.6% at 5140, running).  PB − PB_s = 959 at both 5060 and 5061 (same smooth
sub-board), 949 at 5096.  Cost: best-first, 20 ms a node from scratch, 264k-282k nodes at 5060-5061 (22-25 min on 4
threads); half the reduction in the first few thousand nodes, the last 10% in 60-65% of the time; ~900k open nodes
with bound in (incumbent, PB_s] at the end.  Branchings mostly in layer 6 at 5060-5096.  At every leaf the whole
layer instances still stall (5000: 155 of layer 5's members), through cores that mix smooth and fiber members.
The depth-first form with the solver's warm starts should cost ~1 ms a node.  Smooth conflicts are global nogoods.

E5: templates as local losses killed as stated; 35 of 52 repairs need numbers outside the template (mostly smooth
drops of layers 4-7); T14's loss has a formula (45 → 42 in all fibers but the largest prime's), T11 three
mechanisms, T23 none; 34% of layer-4 differences lie in template fibers.  The smooth class carries the gap.

E6 (4848 standalone, 13.5M branchings): by subtree weight 85% of barred members and 89% of conflict members are
smooth, 92-100% in layers 5-7; fiber branchings are 40% by count in small deep subtrees of gap < 300; in mixed
conflicts the choice rule shows no preference.  So the outer search already spends its weight on the smooth knot.

E4 (already known): carrying nogoods between games is worth ≤ 1.3×; bound structure carries (signings: 0.75 of the
next root's share with no refit).

## R2. E1's leaves: what stalls after the smooth knot is broken (measured here, leafres.py)

The leaf of E1 at 5000 (PB_s = 7,869,799, 264 promotions) and 5060 (8,055,219, 268), rebuilt as G + leaf_promotions
and peeled layer by layer.  Residual = smooth (primes ≤ 23) + fiber members; "B-only stall" = the residual of the
B-smooth members taken alone (so B = 23 gives 0 at every layer, as the leaf requires):

| n | layer | residual | smooth | fiber, by largest prime | B-only stall for B = 29 / 31 / 37 / 41 / 47 |
|---|---|---|---|---|---|
| 5000 | 4 | 74 | 0 | 41:7 43:7 47:7 59:9 61:10 71:5 97:2 101:7 149:5 157:3 163:5 239:1 241:3 409:2 619:1 | 0 / 0 / 0 / 0 / 21 |
| 5000 | 5 | 155 | 90 | 31:16 37:11 47:10 53:8 59:4 61:1 71:4 83:5 113:3 199:2 311:1 | 0 / 104 of 145 / 117 / 117 / 119 |
| 5000 | 6 | 77 | 66 | 41:5 61:3 103:2 151:1 | 0 / 0 / 0 / 0 / 0 |
| 5000 | 7 | 33 | 27 | 31:3 47:2 73:1 | 0 / 30 of 59 / 30 / 30 / 30 |
| 5000 | 8 | 23 | 22 | 37:1 | 0 / 0 / 23 of 31 / 23 / 23 |
| 5060 | 4 | 130 | 48 | 41:7 43:12 47:7 59:9 61:9 71:5 97:6 101:7 151:5 163:3 167:5 241:1 251:3 421:2 631:1 | 0 / 0 / 0 / 0 / 21 |
| 5060 | 5 | 165 | 100 | 31:16 37:12 47:10 53:8 59:4 73:4 83:5 113:3 199:2 313:1 | 0 / 114 of 145 / 128 / 128 / 130 |
| 5060 | 6 | 87 | 70 | 31:6 41:5 61:3 103:2 157:1 | 0 / 0 / 0 / 81 of 112 / 81 |
| 5060 | 7 | 34 | 28 | 31:3 47:2 79:1 | 0 / 31 of 58 / 31 / 31 / 31 |
| 5060 | 8 | 23 | 22 | 37:1 | 0 / 0 / 23 / 23 / 23 |

Sampled minimal cores at the 5000 leaf: layer 5: 57 members (51 smooth) on fibers 31, 37; 37 (31 smooth) on 31, 47;
77 (54) on 31, 47, 83, 113, 199, 311.  Layer 6: 42-48 members (31-37 smooth) on 41, 61, 103, 151.  Layer 7: 25 (22)
on 47, 73.  Layer 8: 21 (20) on 37.  Layer 4 at 5000: the templates only (T23 on 59, 61, 71; T14 on 41/43/47), no
smooth member; at 5060 layer 4 has 48 smooth members in its residual too.

Reading: what survives PB_23 is the same smooth knot re-tied through one or two fibers of primes 31-53 per layer,
and a 31- or 37-smooth exact condition already stalls on it (104 of 145 in layer 5 at 5000).  Raising B to 31-41 is
the next tier; the layer-4 templates (primes 41-251) are a separate, fiber-only matter.

## R3. Uniform GF(3) signings for the templates (measured here, signcheck.py, signcheck2.py)

A uniform signing gives entry s(m, m/q) to every (m·P, (m/q)·P) and h(m) to every (m·P, m), the same in every fiber.
T11 at 5000 (primes 149, 157, 241; 11 members, 13 columns, 9 cofactor edges, 5 hubs): 0 of 16,384 uniform signings
make it GF(3)-dependent; the same at 2176 (61, 67, 107).  Non-uniform (one sign per entry, 28 entries): 611 of
20,000 random signings kill it; K₇₈: 242 of 2,000.  Sanity: theta core of board 45, plain signing → rank 4 of 5
(det 3); K₇₈ plain → rank 9 of 9 (det 1).  T14 (22 keys) and T23 (32 keys) not searched.  So a signing that kills a
template must differ between its fibers and cannot be fixed once for all primes: the template-signing idea is dead
in its cheap form.

## R4. The break-even arithmetic for a node-level bound (derived, from the brief's fit)

With nodes N(g) = 10^(3.85 + g/476) and 0.67 ms a node, a bound tighter by r at every node that costs c ms extra a
node pays iff 10^(r/476) > 1 + c/0.67.  At 1 ms an inner GF(2) solve: b inner nodes need r ≥ 476·log10(1 + b/0.67):
b = 1 → 190, 3 → 350, 10 → 570, 30 → 790, 100 → 1,040, 1,000 → 1,510.  PB − PB_s = 959 at the end of the chain is worth at
most ~70 inner nodes a node; a 10× saving needs it in ~7.  E1's root needed ~3,300 nodes for half the reduction.

## R5. Fiber hub demands at E1's leaf for 5000 (measured here, hubdemand.py, 7.5 min)

d_p = (fiber-p members in the layer) − (max matching of them into their unpromoted fiber factors); the fiber then
pays ≥ d_p members with distinct hubs it lists, which the smooth members cannot use.  Per layer: fibers with demand
/ total demand D / hubs listed per fiber (in brackets) / result of the assignment search:

| layer | smooth members | fibers with demand | D | demands (p: d_p [hubs listed]) | assignment keeping smooth playable |
|---|---|---|---|---|---|
| 3 | 19 | 21 | 29 | 31: 4 [12], 53: 4 [19], 41: 2, 43: 2, others 1 | none in 200,000 (cut off) |
| 4 | 100 | 11 | 11 | 47, 61, 97, 101, 149, 157, 163, 239, 241, 409, 619: 1 each | found at once: {8, 12, 18, 20, 27, 28, 30, 42, 44, 45, 50} |
| 5 | 114 | 11 | 18 | 31: 4 [16], 47: 3 [10], 37: 2 [11], 83: 2 [5], 53, 59, 61, 71, 113, 199, 311: 1 | none in 200,000 (cut off) |
| 6 | 88 | 4 | 4 | 41: 1 [5], 61: 1 [3], 103: 1 [2], 151: 1 [1] | third tried: {32, 48, 72, 112} |
| 7 | 53 | 3 | 3 | 31: 1 [3], 47: 1 [2], 73: 1 [1] | NONE (2 assignments, exhaustive) |
| 8 | 28 | 1 | 1 | 37: 1 [1] | NONE (exhaustive) |

So the PB_s leaf violates the hub-demand condition in layers 7 and 8 for certain, and probably in 3 and 5.  Validity
of the condition: proved (report, 8.0).  Caveats: members with p² | x have their hub x/p counted as a fiber factor
(demand undercounted: safe); hubs that are not smooth are offered to the fibers (assignment easier: safe).

# Round 3 (2026-11-10, after E11 and E8)

## R6. Digest (the project's results)

E11, PB_sh with B = 23 (e1/hubs.jsonl): 1000 73.8%, 2000 55.0%, 2176 72.1% (5.5 s), 3000 92.4% finished (PB_sh =
opt + 56; 2.30M nodes, 1,103 s on 16 threads; 1.74M hub checks, all but the last failed; 543k distinct conflicts,
54 literals a branching, 1.95 live children), 4000 ≥ 64.6% (1 h time limit, 8.79M nodes, 7.0M open, 8.18M hub checks all
failed, 94 literals a branching, 1.82 children, 5.48M distinct conflicts), 5000 ≥ 46.3% (1 h, 3.24M nodes, 5.3M
open, 2.18M hub checks all failed, 78 literals, 2.76 children), 5060 ≥ 47.9% (1.5 h, 3.91M nodes, 10.3M open, 55k
hub checks, 27 literals, 4.08 children: still E1's smooth branching).  The exact counting form (each fiber chooses
which d_p members pay their hubs, the rest matched) was used; it is monotone, 8.0's form is not.

E8 (bsweep.jsonl): 3000: B = 17 19.8%, 19 22.1%, 29-37 33.1% (0.4 s), 47 79.4% (16.5 s, 16k nodes).  4000: 23
33.2%, 31 55.2% (70 s), 37 71.8% (336 s), 41 71.8%.  5000: 17 4.7%, 19 15.4%, 29 28.5% (68 s), 31 ≥ 34.8% at 300 s
(47.3% at 2,634 s), 37 ≥ 34.5% at 300 s, 47 ≥ 44.5% at 300 s.

Other: the second study's split bound killed; its smooth near-optimal oracle infeasible (2.35M configurations
within 300 of the smooth optimum at 1000, ×10 per 50 points); E1's root cores as nogoods in a proof of 4848 running;
plain searches of 5304 and 5260 (gaps 2,093 and 2,106) ran 42-44 CPU-hours, 345-361M nodes, unfinished.

## R7. Hub-ownership branching at E1's leaf for 5000 (measured here, hubbranch.py)

Node = E1's leaf (picks 77, bars 7), bound 7,869,799.  Child S: coordinate a removed from every fiber lister's row;
child F: from every smooth lister's row (sources in G included).  Drops (parent − child):

| layer | hub a | fiber listers (sources) / smooth listers | S | F | literal bars (E11's kind) |
|---|---|---|---|---|---|
| 7 | 64 | 10 (9) / 0 | 946 | 0 | un-promote 2336: 16 |
| 5 | 16 | 29 (28) / 0 | 1,364 | 0 | un-promote 2488: 8 |
| 8 | 128 | 3 (3) / 2 | 424 | 0 | un-promote 2368: 368; bar smooth 2016/2160/2240/2400/2496: 66/210/290/312/378 |
| 7 | 160 | 2 (2) / 5 | 0 | 113 | un-promote 2232: 127, 2480: 375; bar 1760: 113; un-promote column 1936: 289 |
| 5 | 150 | 2 (2) / 5 | −47 | −47 | un-promote 2108/2170/2325/2356/2418/1953: 136/343/498/384/504/126 |
| 6 | 112 | 5 (5) / 3 | 0 | 0 | un-promote 2214/2296/2460: 151/233/397 |

Negative drops: projecting a picked row shrinks the fixed span and frees other elements; take min(parent, child).
Lessons: S (the orbit constraint "no fiber pays a") is decisive where sources list a with no other hub (946, 1,364,
424 against 8-368 for one literal); F is invisible to GF(2) (the smooth side's need is an order fact): F must be
realized as the smooth residual's literal children with the smooth rows projected.  Each parity bound at this node
took ~2-5 s in Python (the picks make the problem small).
