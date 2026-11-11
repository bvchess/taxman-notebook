# Root bounds for the odd cores past 5060 (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-10.  Concluded 2026-11-10.

**Question.**  A proof of a game past 5060 is dear because the parity bound, the bound it starts from, lies thousands of
points above the best-known score, and a proof's cost grows with that gap.  Can a tighter bound, computed once at the
game's root, close enough of the gap to prove games or to make their proofs cheap?  Two independent studies proposed
such bounds, and seven experiments tried them.

**Answer.**  No.  The tighter bounds are real and proved, given statement U, and where they finish they are strong: the
hub bound closes 92.4% of the gap at 3000 and 65.7% at 4000.  But the share they close falls as n grows, and computing
them costs far more than the proof of the same game: at 4000 the chain's proof took 999 CPU-seconds, and the hub bound
took 51,075 thread-seconds.  At 5000 to 5061 the runs stopped at an hour had closed at least 40.5% to 48.0%, and were
still moving slowly.  No game past 5060 is proved by them.  They give limits on three games: 5061 is within 1,815 points
of its best-known score, 5096 within 2,397 and 5140 within 1,717, where the parity bound gives 3,049, 3,346 and 2,694.
The owner stopped the line after the last experiment's run at 5000.  The solver is unchanged.

The experiments that carry the root's work into the proof's search, and fail, are in the companion entry [root work
carried into the proof search](../root-work-carried-into-the-proof-search-2026-11/README.md).

## Method

### The words

*The gap and the share.*  The parity bound is the frame solver's bound at a game's root ([the
glossary](https://github.com/bvchess/taxman/blob/ba59242/docs/GLOSSARY.md#bounds) defines it), and it lies above opt(n)
only because of odd cores ([what the parity bound
misses](https://github.com/bvchess/taxman/blob/ba59242/docs/theory/parity-bound.md#what-the-parity-bound-misses)).  The
*gap* of a game is the parity bound less opt(n), and past 5060, where opt(n) is not proved, less the best-known score.
The *share* of the gap that a bound closes is the points it takes off the parity bound, over the gap.  Every bound of
this entry is an upper bound on opt(n), given [statement
U](https://github.com/bvchess/taxman/blob/ba59242/docs/theory/exactness.md#statement-u), as for every proof past 2531.
Past 5060 a bound's value less the best-known score is a *limit*: opt(n) is at most the best-known score plus that many
points.

*Smooth, fiber and layer.*  A number is *smooth* when all its prime factors are at most 23, and a *fiber* number when it
has a prime factor above 23.  A fiber number a · p, with p the largest prime and above 23, is in the fiber of p.  The
bound 23 is the *smoothness bound*, B.  A number's *layer* is its number of prime factors, counted with multiplicity.
The moves of a game are paid in layers, each layer's moves by numbers of the layer below.

*Cores.*  A *core* of a layer is a nonempty set of its moves in which every number that a move could be paid with is
wanted by at least two moves of the set, so the set cannot be played.  An *odd core* is a core whose lists are linearly
independent over GF(2), which the parity bound therefore admits ([the
glossary](https://github.com/bvchess/taxman/blob/ba59242/docs/GLOSSARY.md#the-game) defines core and odd core).  A
core's *literals* are its members up to n/2 and the played numbers that its members list as maximal factors.  Any set
that holds all of a core's literals holds the core, so it cannot be played.

*The smooth bound, PB_s.*  PB_s adds one condition to the parity bound's: in every layer, the smooth numbers of the set
must be playable among themselves.  Every playable set meets it, because a subset of a playable set is playable and a
maximal factor of a smooth number is smooth.

*The hub bound, PB_sh.*  A fiber number a · p lists the smooth number a, its *hub*, among the numbers it can be paid
with.  A fiber's *demand* is its members less a largest matching of them into the fiber's own factors, the numbers a · p
lists that p divides.  In a game at least that many members of the fiber pay with their hubs, each hub is a distinct
number, and a number pays for one move only, so those hubs pay no smooth move.  PB_sh adds to PB_s: in every layer, some
choice of hubs for the fibers' demands, distinct across fibers, leaves the smooth numbers playable once the chosen hubs
are taken from their lists.  PB_sh is at most PB_s.

*The larger smoothness bound.*  PB_s with B of 31, 37 or 41 asks the same of a larger set of numbers, and costs more.

*The split bound.*  The split bound of the second study treats the smooth numbers and the fibers apart.  For a set X of
hubs that the fibers use, E(X) is the exact best score of the smooth numbers without the hubs X, and F(X) is the parity
bound of the fibers with only the hubs X among their columns.  The bound is the sources' sum plus the largest E(X) +
F(X) over all X.  X\* is the set of hubs that the fibers use in the recorded optimal game.

*Templates.*  The first study named three recurring patterns of fiber numbers, T11, T14 and T23, each a core of layer 4
by itself: members m · P for primes P above 23 and cofactors m from a short list.  The *territory* of a template is the
numbers whose largest prime is one of its primes, its fibers, and its hubs.

### How the bounds are computed

One program computes PB_s, PB_sh and the larger-B bounds: the example `e1_smooth.rs` of the research repository's branch
`e1-smooth-bound`.  It is a best-first branch and bound over the solver's GF(2) bound.  A node holds *picks*, numbers
forced in, and *bars*, numbers left out.  The node's bound is the parity bound's heaviest set under them, solved from
scratch.  If that set meets the extra condition it is a leaf, and its weight is a lower bound on the bound being
computed.  If not, a minimal core of the failure gives the branches: child i bars literal i and picks the literals
before it, so the children partition the sets that meet the condition.  A node whose bound is at or below the incumbent,
opt(n) or the best-known score, is dropped, and a literal whose bar alone leaves the bound at or below it is picked in
every child.  The queue is shared by the threads.  The search ends when the queue is empty, and the value is the best
leaf, or the incumbent when no leaf beat it.  A run stopped by its time limit reports a range: the largest open bound
above and the best leaf below, so the share that a stopped run reports is a lower bound on the share the bound closes.

For PB_sh a leaf that is smooth-playable is also tested for the hub condition, and when it fails, the literals of the
fibers involved and of the stalled smooth cores give the branches.  E12 changes how that branching is done.

### The studies and the experiments

Both studies read the same brief ([brief.md](brief.md), with [census.csv](census.csv), [cores.py](cores.py) and
[parity.py](parity.py)), which defines the game, the parity bound and what is known of the gap.  The first study
([study-report-1.md](study-report-1.md)) ranked ideas and asked for experiments in three rounds, each written after the
results of the one before.  The second study ([study-report-2.md](study-report-2.md)) worked without reading the first,
and asked for five experiments.  Each experiment's rule was fixed before it ran: it *confirms* an idea at its first
bound and *kills* it at its second.  The labels are the studies' and are kept because the folders, the patches and the
register use them.  All ran on 2026-11-10, in Pacific time.

| label | what it does | ran | rule | code |
|---|---|---|---|---|
| E1 | PB_s at 2176 to 5140 | 09:25 to 11:55 | confirms at a share of 50% or more at 4000 to 5060 that does not fall from 2176; kills under 25%, or if the share falls as the Lagrangian bound's did, 3.8 points per 100 of gap | 8a5345a, 5f5f808 |
| E5 | templates as local losses, from existing results | 09:50 to 09:55 | confirms if each template's repair lies in its territory at a cost that depends on its primes only; kills if the optimal game repairs templates through numbers outside | none, scripts |
| E11 | PB_sh at 2176 to 5061 | 11:55 to 17:21 | confirms at 10 points more than PB_s at 5000 to 5061 within 2 times E1's time; kills under 3 | 26416c8, 9c8f27c, 7a4a74a |
| E8 | PB_s with B of 31, 37, 41 at 4000, 5000, 5060 | results 14:17 to 17:30 | confirms at 50% or more at 5000 to 5060 in an hour on 4 threads; kills if each step of B adds under 5 points or costs over 10 times as much | the E1 program |
| E9 | root forcing at 5061 | 16:20 to 16:55 | confirms at 15 fixings in 60 tests; kills under 5 | fac59be, in the companion entry's patches |
| split bound | items 1, 4 and 2 of the second study | 13:15 to 16:20 | item 1 confirms if the share lost stays near 40% or falls; item 4 if the near-optimal smooth list has at most 10⁶ members at 5000; item 2 kills if the largest term exceeds the optimal set's term by more than half the gap | 84b7ff6, 19dd86f, 7151c78 |
| E12 | hub-ownership branching in PB_sh's search | 17:00 to 20:10 | confirms if 3000 finishes in under a tenth of E11's nodes and 4000 in the hour; kills if the child that gives a hub to the smooth side drops under 100 at the root's first hub conflicts, or the tree is no smaller | a8f66ea, d4ba11a, 3a4f697 |

Some experiments that the studies asked for were not run.  E12b would have proved limits of the form opt(n) at
most the best-known score plus a chosen amount at 5000, 5060 and 5061, by a depth-first search to a target.  Its mode is
in the code and untested.  E13 would have run PB_sh with B of 31 and 37 at 4000 and 5000.  The owner stopped the bound
line after E12's run at 5000 (19:21): at 4000 the chain's proof took 20 s on 88 threads, 999 CPU-seconds, PB_sh took
3,247 s on 16 threads and still ended at opt + 414, and its share of the gap falls with n.  E3, the count of the smooth
cores a search meets, was to run only if E1 looked promising, and no record shows a run of it.  The second study's item
3, the split bound at 30 nodes of a proof, was not run because item 2 killed the bound and the bound's cost at the root
did not fit a node; its item 5 was not run either.  E4 and E10 were withdrawn by the first study.  E2, E6, E7 and E14
are in the companion entry.  E15 asked for limits at 5061, 5096, 5140, 5260 and 5304 from the runs that existed: the
table of "What the bounds leave" gives the first three, and no bound was computed for the last two.

## Results

### The seven against their rules

| experiment | result | against the rule |
|---|---|---|
| E1 | PB_s closes 26.5% to 37.5% at every game of 4000 to 5096, and 55.0% at 2176 | neither confirms nor kills |
| E5 | a template's repair lies in its territory in 17 of 52 instances | killed as stated |
| E11 | PB_sh finishes at 92.4% at 3000; within 2 times E1's time it adds 1.6 to 2.0 points at 5000 to 5061 at equal thread time, 7.0 to 7.7 at equal wall time | does not confirm; kills at equal thread time, neither at equal wall time |
| E8 | at 4000 B of 37 closes 71.8%; at 5000 the step to 31 costs 78 times the thread time, and at 5060 it adds 3.4 points | killed at 5000 to 5060 |
| E9 | 60 of 60 tested candidates are barred at the root of 5061 | confirms |
| split bound | the optimal set's term closes 60% to 98% at 3000 to 5060, but the largest term at 2000 leaves 85% of the gap | killed by item 2; item 4 does not confirm |
| E12 | PB_sh finishes at 4000 in 3,247 s, and at 3000 in 0.35 of E11's nodes; at 5000 it is behind E11 | neither confirms nor kills |

### E1: the smooth bound

*Question.*  Does a bound that is exact on the smooth numbers of every layer close a large share of the gap, and a share
that does not fall with n?

*Method.*  The program above with B of 23, and of 13 as a control, on 4 threads at `nice 19`, beside the
production runs.  The checks were three.  PB_13 at 1000 and 2176 equals the first study's Python prototype.
With no incumbent, PB_s is the same on all 22 runs of B of 13 and 23 at 300 to 1300, so the incumbent's pruning is
exact.  And every leaf, 16 at 400 to 1300 and 6 at 2176 to 5000, passes `check_leaf.py`, which checks from the
definitions with the brief's `parity.py` and `cores.py` and no code of the solver.

*Results.*  The share is steady at about 30% from 3000 on:

| n | gap | PB_s | share | nodes | seconds on 4 threads |
|---|---|---|---|---|---|
| 1000 | 214 | 315,544 | 44.9% | 18 | 0.0 |
| 2176 | 767 | 1,494,506 | 55.0% | 812 | 1.3 |
| 3000 | 734 | 2,837,775 | 27.2% | 37 | 0.3 |
| 4000 | 1,206 | 5,035,680 | 33.2% | 2,810 | 11 |
| 5000 | 2,073 | 7,869,799 | 28.5% | 14,658 | 67 |
| 5060 | 2,557 | 8,055,219 | 37.5% | 263,621 | 1,294 |
| 5061 | 3,049 | 8,060,026 | 31.5% | 281,644 | 1,514 |
| 5096 | 3,346 | 8,172,863 | 28.4% | 186,382 | 868 |
| 5140 | 2,694 | at most 8,319,093 | at least 36.3% | 392,084 | stopped at 1,800 |

Over the 23 finished games of 1000 to 5096 the least-squares slope of the share against the gap is -0.45 points per 100
of gap, and from 3000 on it is +0.28, against the Lagrangian bound's -3.8.  The median share by thousand of n is 43%,
32%, 27%, 30% and 30%.  Two games dip under 25%: 2000 (24.6%) and 3500 (14.9%).  B of 13 is worth 0% to 7% from 3000 on.
The amount PB_s takes off the parity bound is nearly the same at neighboring games: 959 points at 5060 and at 5061,
whose smooth numbers are the same, 949 at 5096, and 200, 400 and 590 at 3000, 4000 and 5000.

A node costs 16 to 20 thread-milliseconds, 84% to 85% of it the GF(2) solve from scratch.  The last tenth of the
reduction is most of the time: at 5060 half of it was reached in the first 21 s (3,287 nodes), 90% at 481 s (98,427
nodes), 99% at 1,181 s and all of it at 1,294 s.  Leaves are rare: the best-first searches met one or two
smooth-playable sets above the incumbent in 186,000 to 282,000 nodes.  At every leaf the whole layer instances still
stall, through cores that mix smooth numbers with fibers of primes 31 to 53.  At 5000 layer 5 has 155 stalled members.

*Verdict.*  Neither confirms nor kills, by the rule.  No game of 4000 to 5140 is under 25% and the share does not fall
the Lagrangian bound's way, but the 50% is not reached.  At 5060 to 5096 PB_s takes 949 to 959 points off a gap of
2,557 to 3,346, at the root only.

### E11: the hub bound

*Question.*  Does adding the fibers' hub demands to PB_s raise the share by 10 points or more at 5000 to 5061 within
twice E1's time?

*Method.*  The hub condition, by layer: each fiber's demand by bipartite matching, its choices of hub payers, and a
depth-first search over the fibers that peels the smooth numbers after each step that takes a listed hub away.  A layer
with no passing choice is a conflict, and its literals branch.  The first test was too slow, so a second was built that
projects the choices onto the hubs that matter, keeps the minimal ones, drops fibers that can stay out of the way and
remembers failed states, with the same outcome and 28 times fewer peels at 2176.  The second gives the same PB_sh as the
first on all 12 games of 400 to 2176, and every leaf of the checks, 19 at 400 to 2176 and the one at 3000, passes
`check_hubs.py`, an independent check of the condition from the definitions.  PB_sh is the same with and without the
incumbent on 11 games of 400 to 2000.  E1 ran on 4 threads and E11 on 16, so the rule's "twice E1's time" is read two
ways: twice E1's wall time, and twice E1's thread-seconds.

*Results.*  With B of 23, on 16 threads from 3000 on, limited to an hour and to 1.5 hours at 5060 and 5061:

| n | gap | PB_sh | share | nodes | time | passes PB_s at |
|---|---|---|---|---|---|---|
| 2176 | 767 | 1,494,375, finished | 72.1% | 9,393 | 5.5 s on 4 threads | |
| 3000 | 734 | 2,837,297, finished | 92.4% | 2,302,566 | 1,103 s | at most 2.3 s |
| 4000 | 1,206 | at most 5,035,301 | at least 64.6% | 8,791,112 | 1 h, stopped | 4.4 s |
| 5000 | 2,073 | at most 7,869,430 | at least 46.3% | 3,239,055 | 1 h, stopped | 22.7 s |
| 5060 | 2,557 | at most 8,054,952 | at least 47.9% | 3,911,669 | 1.5 h, stopped | 379 s |
| 5061 | 3,049 | at most 8,059,751 | at least 40.5% | 4,442,031 | 1.5 h, stopped | 415 s |

At 3000 PB_sh is opt(3000) + 56, and its leaf passes both independent checks.  The gain over PB_s within twice
E1's time, against the rule's 10 points and 3 points:

| n | at 2 times E1's thread-seconds | at 2 times E1's wall time | at the time limit |
|---|---|---|---|
| 5000 | +1.6 | +7.7 | at least +17.8 |
| 5060 | +2.0 | +7.6 | at least +10.4 |
| 5061 | +1.9 | +7.0 | at least +9.0 |

The hub test takes 78% of the thread time at 3000, 50% at 4000, 30% at 5000 and 1% at 5060 and 5061, where the search
is still working through the smooth branching of E1.  Every smooth-playable leaf fails the hub test, in 8,182,938 of
8,182,938 checks at 4000, and a hub conflict has 94 literals and 1.8 live children on average, with 5.5 million distinct
conflicts in the 8.8 million nodes.  So the condition is as strong as hoped, and its search dodges at the hubs the way
the parity bound's search dodged at cores, one twin at a time.

*Verdict.*  Does not confirm.  At equal thread time the gain is under the kill line of 3 points, and at equal wall time
it is between the lines.  The bound itself is much stronger than PB_s, since it finishes at 92.4% at 3000.  What fails
the rule is the time to reach it: a best-first search for PB_sh first clears every node above PB_s.  A run of E11 at
4000 to completion on 32 threads for 4 hours was started and stopped at 336 s, at 58.7%, because E12 was to give that
value.

### E8: PB_s with a larger B

*Question.*  Does making the smooth numbers of the next primes exact, with B of 31, 37 and 41, raise the share to 50% at
5000 to 5060 in an hour on 4 threads?

*Method.*  The E1 program unchanged with `--smooth 31`, `37` and `41`, on 8 threads, an hour each.  The coordinator cut
B of 41 at 5000, since B of 37 added under a point there, and ran B of 37 at 5060 because B of 31 finished within its
hour.

*Results.*  Shares of the gap, with "at least" where the run stopped at its hour:

| n | B of 23 | B of 31 | B of 37 | B of 41 |
|---|---|---|---|---|
| 4000 | 33.2% in 11 s on 4 threads | 55.2% in 70 s on 8 | 71.8% in 336 s on 8 | 71.8% in 328 s on 8 |
| 5000 | 28.5% in 67 s on 4 | 47.3% in 2,634 s on 8 | at least 48.0% in 3,600 s on 8 | not run |
| 5060 | 37.5% in 1,294 s on 4 | 40.9% in 1,391 s on 8 | at least 44.5% in 3,600 s on 8 | not run |

The step from 23 to 31 adds 22.0 points at 4000 for 12.4 times the thread time, 18.8 points at 5000 for 78 times, and
3.4 points at 5060 for 2.1 times.  The step from 31 to 37 adds 16.6 points at 4000 and at least 0.7 at 5000.  At 4000 B
of 41 adds nothing to B of 37, so what B of 23 leaves at 4000 sits in the fibers of the primes 29 to 37.  At 5000 B of
29 gives exactly B of 23's value.  Within the rule's budget, an hour on 4 threads taken as half an hour on 8, B of 31
gives 45.3% at 5000 and 40.9% at 5060, and B of 37 gives 44.8% and 41.5%.

*Verdict.*  Killed at 5000 to 5060: no run reaches 50%, and each step of B adds under 5 points or costs over 10 times as
much.  At 4000 the tiers do pay, and B of 37 gives the tightest bound of the game, 71.8% in under 6 minutes on 8
threads.

### E9: root forcing at 5061

*Question.*  How many candidates can PB_s fix at the root of 5061, beyond what the parity bound fixes?  A candidate is
fixed when PB_s with it fixed the other way from its place in the heaviest set is at most the best-known score.

*Method.*  The program lists the parity bound with each candidate fixed the other way, 268 members of the heaviest set
and 1,112 candidates outside it, in 22 s on one thread.  No member lies within reach: forcing one in needs an exclusion
cost of 2,090 or more, and the dearest costs 1,405.  Of the candidates outside the set, 95 lie within 1,199 points of
the best-known score, and the 60 closest, those at most 959 above it, were tested by PB_s with the candidate picked,
on 4 threads, four at a time.  A candidate is barred when PB_s ends at or below the best-known score.

*Results.*  All 60 are barred.  The parity bound alone bars 12 of them.

| parity bound with the candidate picked, above the best-known score | tests | barred | seconds a test on 4 threads, median and most |
|---|---|---|---|
| 37 to 449 | 19 | 19 | 0.5, 2.0 |
| 565 to 718 | 21 | 21 | 5, 11 |
| 757 to 959 | 20 | 20 | 43, 185 |
| 1,006 to 1,141, probes | 4 | 0 | 333, 460 |
| 1,199, probe | 1 | stopped at 900 s | 900 |

The edge is sharp at 959, which is the root's own reduction PB less PB_s: each of the four probes past it ended with
PB_s exactly 959 below its parity bound, so none is barred.  The 60 tests took 1.55 thread-hours.  The fixings are
relative to the best-known score, which is not proved optimal: each says that no set above that score plays the
candidate.

*Verdict.*  Confirms, 60 of 60 against 15 needed.  Whether bars at the root shorten a proof was not measured here.  The
companion entry's E9b loaded 309 such bars into the proof of 4848 and found 1.016 times the steps.

### E5: templates as local losses

*Question.*  Each template's core in layer 4's residual of the parity bound's heaviest set H costs a local loss, and the
conjecture was that the optimal set S\* repairs it only inside the template's territory, at a cost that depends only on
the template's primes.  If it held, the templates would give a bound by formula.

*Method.*  An analysis of existing results with no solver run.  H comes from `parity.py` and S\* from the recorded
optimal game.  The sources are the same in both, so the differences are numbers up to n/2.  For each template instance,
the numbers of its territory that H and S\* differ in are swapped into H, and the swap is *clean* when it breaks every
template core and leaves no new residual in any layer.  Four games were run in full, 3500, 4500, 5000 and 5060, where a
search also found the other differences that a swap needed, and 26 more lightly.

*Results.*  Over 30 games there are 52 instances, 22 of T11, 17 of T14 and 13 of T23.

* S\* breaks every template core in its territory in 52 of 52 instances, which is forced, and no hub ever differs.
* The swap on the territory is clean alone in 17 of 52 (T11 6 of 22, T14 9 of 17, T23 2 of 13).  In the other 35 the
  swap needs numbers outside the territory, mostly smooth numbers of layers 4 to 7, and on the four full games 8 of 11.
* 131 of 386 differences of layer 4 (34%) lie in a template's fibers.  At 5000 the smooth differences weigh +4,597
  against a gap of 2,073.
* T14's loss is 3 times the sum of its primes but the largest in 12 of 17 instances.
* T11 repairs three ways in 15 of 22 instances and by a mix in 7, and which way the optimal set takes changes with n.
  The third, at 4800 to 5060, repairs T11 through the fiber of a prime that is not a T11 prime, at a loss of 954 to
  1,026.
* T23 has losses from -1,566 to +1,316 and no rule.

*Verdict.*  Not kept, killed as stated: the optimal set repairs templates through numbers outside them in 35 of 52
instances, and the cost is a function of the primes only for T14.  The templates are real but small beside the smooth
numbers, which carry the gap.

### The split bound

*Question.*  Does a bound that separates the smooth numbers from the fibers, joined only through the hubs that the
fibers use, close a large share at the end of the chain, given an exact answer for the smooth side that every node and
game could share?

*Method.*  The first item computes the bound's term at X\*, the second the largest term over all hub sets, and the
fourth counts the smooth configurations near the best, which a shared list would hold.  E(X) is the branch and bound of
E1 on the smooth sub-board with the hubs X deleted, started from the optimal set's own smooth part, which is playable
without X\*.  F(X) is one solve of the solver's GF(2) bound on the fibers.  X\* is taken from the optimal game's peel,
and a different peel gives a different X\*, by 0 to 2 hubs at 1000 to 2000 and up to 10 at 5000.  The largest term is
searched exactly at 1000 by a best-first branch and bound over hub sets, and elsewhere by a hill climb from X\*, which
gives a lower bound.  E and F agree with the second study's Python at 1000, 1500 and 2000 to the point.

*Results.*  Item 1, the term at X\*, with the share of the gap lost to the bound (the share closed is the rest):

| n | gap | smooth side | fiber side | term less opt(n) | share lost | E's search |
|---|---|---|---|---|---|---|
| 1000 | 214 | 81 | 8 | 89 | 41.6% | 34 nodes |
| 1500 | 401 | 0 | 178 | 178 | 44.4% | 486 nodes |
| 2000 | 491 | 0 | 12 | 12 | 2.4% | 200 nodes |
| 3000 | 734 | 0 | 14 | 14 | 1.9% | 31,841 nodes, 5 s |
| 4000 | 1,206 | 110 | 122 | 232 | 19.2% | 325,329 nodes, 95 s |
| 5000 | 2,073 | 63 | 745 | 808 | 39.0% | 2,777,670 nodes, 783 s |
| 5060 | 2,557 | 0 to 470 | 544 | 544 to 1,014 | 21.3% to 39.7% | stopped at 3,500 s |

At 3000 the descending peel's X\* gives opt + 92 where the ascending peel's gives opt + 14.  Item 1 confirms by its
rule, which asks that the share lost stay at or below 40%.

Item 4, the smooth configurations within a margin of E(empty set), at 1000: 615, 6,766, 57,029, 395,805 and 2,351,642
within 100, 150, 200, 250 and 300 points, a rise of 6 to 11 times for every 50.  At 5000 the search for E(empty set) did
not finish in 1,320 s, with 788,738 nodes done and 6.3 million open.  E(empty set) lies 1,377 above E(X\*) at 1000 and
at least 8,668 above it at 2000, so a list near E(empty set) holds no configuration that the queries near X\* could use.
Item 4 does not confirm, and the shared smooth list cannot be built.

Item 2, the largest term:

| n | gap | X\*'s term less opt(n) | largest term found less opt(n) | the difference | the difference over the gap | how |
|---|---|---|---|---|---|---|
| 1000 | 214 | 89 | 101 | 12 | 5.6% | search over hub sets, finished |
| 2000 | 491 | 12 | 428 | 416 | 84.7% | hill climb of radius 2, ended on its own after 4 rounds |
| 3000 | 734 | 14 | 174 | 160 | 21.8% | hill climb of radius 2, stopped at 1 h |
| 4000 | 1,206 | 232 | 300 | 68 | 5.6% | hill climb of radius 1, stopped at 1 h |

The best set at 2000 adds hubs 51 and 63 and removes 34, 52, 60 and 66, and its term checks twice, in the Rust program
and in the second study's Python.  It trades 870 of gain on the smooth side for 442 of loss on the fiber side.  The
bound at 2000 is then at least opt + 428, which closes at most 12.8% of the gap, where the term at X\* closes 97.6%.

*Verdict.*  Not kept, killed by item 2: the largest term at 2000 lies 416 above the optimal set's term, past the rule's
half of the gap.  The split's interface, a set of hubs, misses the order that the fibers impose through hubs they list
but do not pay, so the term at X\* overstates what the bound closes.  Item 3 would need hundreds to thousands of E
searches at each node, some as hard as E(empty set), and was not run.

### E12: hub-ownership branching

*Question.*  E11's search clears a long plateau because it resolves a layer that fails the hub test by barring one of
about 90 literals, and a twin of the same demand meets each bar.  Does branching on who pays a hub, in place of the
literals, make PB_sh finish at 3000 to 5000?

*Method.*  A hub a of layer k - 1 has fiber listers and smooth listers among the moves of layer k.  In a game either no
fiber move pays with a, side S, or one does and then no smooth move does, side F, since a number pays for one move.  A
number that no move pays with can be taken out of the lists and the set stays playable, so each side's games are
playable in the instance with the numbers dropped, and the two sides cover every game.  A node carries the hubs decided
each way on its path, and its bound is the heaviest set of its instance, or its parent's bound where that is lower.  A
leaf must also be independent in the root's frames, so that the value is at most PB_sh.  Two forms were built.

* The branching as the third round of the first study proposed it keeps a child S for every hub it takes.  At contended
  hubs, which a few fiber moves and several smooth moves list, that child drops about nothing and stays live, so the
  tree grew: 22,935 nodes against E11's 9,174 at 2176, and at 3000 about ten times E11's nodes for the same upper bound.
* The form that worked, `--probe`, solves each child S at once.  A dead S, one with no set above the incumbent or no set
  at all, gives the hub to the fibers for free.  A live S leaves the hub undecided, and the node branches on literals as
  before.

The nodes of the variants, each with the same value as E11's:

| n | E11 | a child S for every hub | `--probe` |
|---|---|---|---|
| 1000 | 477 | 319 | 254 |
| 1300 | 19,851 | 1,877 | 2,886 |
| 1500 | 416 | 707 | 405 |
| 2000 | 2,557 | 14,351 | 2,411 |
| 2176 | 9,174 | 22,935 | 8,561 |
| 3000 | 2,302,566 | stopped at 100 s, 294,000 nodes | 799,039 |

With the decisions acting on the tests only (`--no-project`) the value is PB_sh itself, which checks the branching.
Every mode gives E11's PB_sh on every game where E11 finished, 400 to 2176 and 3000.  Every leaf of the 27 of the check,
the two at 3000 and the one at 4000 passes `check_leaf.py` and `check_hubs.py`.  The boards ran with `--hubs --own
--probe` on 16 threads at `nice 19`, an hour each, on a machine at a load of 70 to 80.

*Results.*  PB_sh with B of 23:

| n | gap | E12 | nodes | time | E11 | nodes | time |
|---|---|---|---|---|---|---|---|
| 3000 | 734 | 2,837,297 = opt + 56, 92.4% | 799,039 | 397 s | the same, finished | 2,302,566 | 1,103 s |
| 4000 | 1,206 | 5,035,288 = opt + 414, 65.7% | 1,998,672 | 3,247 s | at most 5,035,301, at least 64.6% | 8,791,112, 7.0 million open | 3,600 s, stopped |
| 5000 | 2,073 | at most 7,869,467, at least 44.5% | 1,126,803, 2.2 million open | 3,600 s, stopped | at most 7,869,430, at least 46.3% | 3,239,055, 5.3 million open | 3,600 s, stopped |

At 3000 the tree is 0.35 of E11's and 2.8 times faster.  At 4000 PB_sh finishes within the hour, and E11 had not.  At
5000 it does slightly worse than E11.  The upper bound against time:

| n | at 900 s: E12, E11 | at 1,800 s | at 2,700 s | at 3,247 s |
|---|---|---|---|---|
| 4000 | 5,035,344, 5,035,350 | 5,035,313, 5,035,324 | | 5,035,288 finished, 5,035,305 |
| 5000 | 7,869,524, 7,869,496 | 7,869,498, 7,869,460 | 7,869,482, 7,869,442 | |

At the root's first hub conflict the child S drops 1,110 at 3000, 1,626 at 4000 and 2,108 at 5000, all at hub 16, so the
hub does cut where it counts.  Over a whole run the picture changes with n: 14.3% of the children S were cut at 3000,
8.8% at 4000 and 0.3% at 5000, with 11.4%, 10.4% and 15.7% having no set at all.  At 5000 the drops are rarely as large
as the gap left, so the probes cost time and settle little.  The thread-seconds:

| n | rule | GF(2) solves | smooth cores | pricing | hub test | instance builds | all |
|---|---|---|---|---|---|---|---|
| 3000 | E11 | 2,741 | 859 | 113 | 13,403 | | 17,117 |
| 3000 | E12 | 3,284 | 471 | 28 | 1,959 | 500 | 6,243 |
| 4000 | E11, 1 h | 23,936 | 3,548 | 457 | 28,194 | | 56,135 |
| 4000 | E12 | 37,807 | 2,665 | 296 | 5,174 | 5,133 | 51,075 |
| 5000 | E11, 1 h | 35,445 | 2,773 | 1,660 | 17,386 | | 57,264 |
| 5000 | E12, 1 h | 46,774 | 2,133 | 1,679 | 2,781 | 3,720 | 57,087 |

The hub test, E11's largest cost at 3000 and 4000, falls five to seven times because E12 runs it four to six times less
often, and the probes take its place: at 5000, 82% of E12's time is GF(2) solves, most of them of children S that turn
out live.

*Verdict.*  Neither confirms nor kills, by the rule.  4000 finishes within its hour, which is half of the confirm mark,
and 3000 takes 0.35 of E11's nodes where the mark is 0.1.  It is not killed, since the child's drops are in the
thousands and the tree is smaller.  It helps at 3000 to 4000 and not at 5000, which is where it was needed.

### What the bounds leave

The tightest upper bound that any run reached on each game, from a finished PB_s or PB_sh, or the largest bound still
open when a run stopped, since every set of the family above the incumbent lay in an open node:

| n | parity bound | score | tightest bound | from | above the score | share closed |
|---|---|---|---|---|---|---|
| 1000 | 315,640 | 315,426 | 315,482 | PB_sh, finished | 56 | 73.8% |
| 2176 | 1,494,928 | 1,494,161 | 1,494,375 | PB_sh, finished | 214 | 72.1% |
| 3000 | 2,837,975 | 2,837,241 | 2,837,297 | PB_sh, finished | 56 | 92.4% |
| 4000 | 5,036,080 | 5,034,874 | 5,035,214 | B of 37, finished | 340 | 71.8% |
| 5000 | 7,870,389 | 7,868,316 | 7,869,393 | B of 37, open at 1 h | 1,077 | 48.0% |
| 5060 | 8,056,178 | 8,053,621 | 8,054,952 | PB_sh, open at 1.5 h | 1,331 | 47.9% |
| 5061 | 8,060,985 | 8,057,936 | 8,059,751 | PB_sh, open at 1.5 h | 1,815 | 40.5% |
| 5096 | 8,173,812 | 8,170,466 | 8,172,863 | PB_s, finished | 2,397 | 28.4% |
| 5140 | 8,320,070 | 8,317,376 | 8,319,093 | PB_s, open at 30 min | 1,717 | 36.3% |

Up to 5060 the score is opt(n), and past 5060 it is the best-known score, so the last three rows are limits.  They are
0.021% to 0.029% of the score, against 0.032% to 0.041% for the parity bound.  They prove no
game, and the first study had hoped for limits of 200 to 350 points, from a finished PB_sh at 90%.

### What the bounds cost against the proofs

The chain proved each of these games with the solver's own search, and its record gives the cost
([chain-proofs.csv](chain-proofs.csv)).

| n | gap | the chain's proof, nodes and CPU-seconds | the root bound, share and thread-seconds |
|---|---|---|---|
| 2176 | 767 | 195,682 and 52 | PB_sh 72.1%, finished, 22 (5.5 s on 4 threads) |
| 3000 | 734 | 98,936 and 35 | PB_sh 92.4%, finished: 17,117 for E11, 6,243 for E12 |
| 4000 | 1,206 | 2,484,306 and 999 | PB_sh 65.7%, finished: 51,075 for E12; B of 37, 71.8%: 2,684 (336 s on 8 threads) |
| 5000 | 2,073 | 65,254,941 and 40,629 | at least 44.5% to 48.0%, not finished: 57,087 for E12 at 1 h |
| 5060 | 2,557 | 1,214,943,001 and 765,397 | PB_sh at least 47.9%, not finished: 86,408 in 1.5 h on 16 threads |

The thread-seconds of 2176, of B of 37 and of 5060 are the wall time times the threads, and the others are measured.  At
3000 the bound costs 180 times the whole proof and at 4000 51 times; at 5000 it has spent 1.4 times the proof's CPU and
is not done.  The ratio falls with n, since a proof's cost rises faster than the bound's, but the bound is not finished
at the last two games, so their rows give what the hour had reached and not the cost of finishing: at 5060 the 1.5 hours
are 0.11 of the proof's CPU.  No root bound closes the whole gap, so none replaces the proof, and the companion entry
shows that the root's work does not make the proof cheaper.  The second study's argument is the reason: a bound that
tests a condition on the heaviest set computes a proof tree cut short at the nodes where the condition holds, so it
cannot be cheaper than the proof by more than the share of the tree that those nodes cut.

### Where the gap lives

The studies' own measurements, in plain Python at games up to 5000 and not experiments of this entry, say why the
bounds stop where they do.

* At 5000 layer 5 has 299 members in the heaviest set, and the 115 smooth ones stall under the peel by themselves, 101
  of them, while the 184 with a prime above 23 peel completely by themselves.  The same holds at 2176, 3000 and 4000 and
  in layers 6 and 7.  So the condition that the smooth numbers be playable is a necessary one that depends only on the
  smooth decisions, which twin swaps of fiber numbers cannot dodge.
* No matroid that contains the playable sets can have more than 8 of 56 sampled cores of layer 5 at 5000 as circuits, 10
  of 56 in layer 6, 4 of 25 in layer 7 and 5 of 48 at 2176.  A single matroid cannot replace a GF(2) block.
* The second study fixed the optimal game's smooth choices and left the fibers free: the parity bound then leaves 4%,
  44%, 11% and 3% of the gap at 1000, 1500, 2000 and 2176.  With the fiber choices fixed it leaves 96%, 76%, 61% and
  86%.  So the gap is in the smooth configuration.  The report's summary gives 3% to 11% for the first fixing, and its
  table has 44% at 1500, so the table's numbers are used here.
* What PB_s and PB_sh leave at a leaf is the smooth knot tied again through one or two fibers of the primes 31 to 53 in
  each layer: layer 7 needs the prime 31, layer 8 the prime 37, and layer 6 at 5060 the prime 41.

## Limits

* **Past 5060 the score is best-known,** so the limits there are relative to it, and all values are given statement U.
* **One run of each setting.**  The runs were at `nice 19` beside the production runs, on a machine at a load of 70 to
  80 of 88 hardware threads, with 4, 8 or 16 threads each, so times and thread-time ratios carry the load and the
  threads' scaling, which was about 80%.
* **A stopped run's share is a lower bound.**  The shares at 5000 to 5061 at the hour may be higher at the end, and E12
  and E11 at 5000 moved slowly, 7,869,524 to 7,869,467 in 2,700 seconds for E12.
* **E1's rule read two ways for E11,** at equal wall time and at equal thread time, since the machines differ.
* **The programs are not proved correct.**  The evidence is the independent checks of every leaf, the agreement of every
  mode with E11's PB_sh on the games where it finished, and the agreement with the second study's Python.  The
  incumbent's pruning was checked on 22 runs.
* **The chain's proofs had help the bounds did not:** the seed from the game before.  The comparison of costs is of a
  proof and a bound on the same game, not of equal tasks.
* **The split bound's largest term is a lower bound** everywhere but at 1000, from a hill climb that was still rising at
  3000 and 4000.

## Decision

None of the bounds is kept in the solver, and the solver is unchanged.  The program is kept as patches.  The line
stopped at the owner's decision of 19:21, after E12's run at 5000, so E12b and E13 were not run.

The facts that stand: PB_s and PB_sh are valid bounds that close a share of the gap that falls with n at a cost that
rises past the proof's; the limits of the table above stand for 5061, 5096 and 5140; and 60 candidates are barred at
the root of 5061.

What would reopen it:

* a bound that resolves the hub contention without a search, or one whose expensive part is reused across nodes and
  games, which is the second study's reading of why every bound here costs a proof: a repair of the split bound would
  make the fibers exact per fiber and carry the order that they impose through hubs they list but do not pay;
* limits by a depth-first search to a target, E12b, if the aim becomes a limit on a game and not a proof, since its mode
  is in the code and untested;
* B of 31 or 37 with the hub bound, E13: at 4000 B of 37 alone closes 71.8% in 336 s on 8 threads, more than PB_sh's
  65.7% in 3,247 s on 16, and the two together were not run;
* a use of the root's bound inside the search that the companion entry's three ways do not cover.

## Files

The experiments ran in the scratch folder `lab/work/oddcore/`, and each keeps its folder here: [e1/](e1/) holds E1, E11
and E8, [e5/](e5/) E5, [e9/](e9/) E9, [f2-1/](f2-1/) the split bound, and [e12/](e12/) E12.  The studies' scripts and
notes are in [study-1/](study-1/) and [study-2/](study-2/).  The copies of the brief, the two reports and the first
study's notes are verbatim except for two kinds of change.  The name of the model that wrote the reports is replaced by
"the study", and the two folders and two report files that were named after it by `study-1`, `study-2`,
`study-report-1.md` and `study-report-2.md`; the comments of the scripts changed the same way.  And the words that the
notebook has retired are replaced by their current terms: "frontier" by "the end of the chain" (and by "boundary" where
the report means the edge of a set of nodes), "cap" by "time limit" or "limit", "catalogued" by "cataloged", "all cores"
by "every core", "one-level" by "at one level" and "a C2-feasible set" by "a set that meets C2".  The same holds for one
word of a comment of `e1/runs5.sh`.  The paths in the scripts are those of the scratch folder, with those two folder
names changed.  No binary is kept (`e9/e1_smooth-e9`, 104 MB), nor E5's cache of the heaviest sets and the recorded
games, which `fetch.py` makes again, and three empty files of stopped runs of the split bound are left out.

* [brief.md](brief.md): the research brief that both studies read, with [census.csv](census.csv) (54 games, every
  hundred from 100 to 5000 and four more, with the parity bound, opt(n), the gap and each layer's excess and residual),
  [parity.py](parity.py) (the parity bound and its heaviest set) and [cores.py](cores.py) (peeling and minimal cores),
  which the checks use.
* [study-report-1.md](study-report-1.md) and [study-report-2.md](study-report-2.md): the two studies' reports, as
  written but for the changes above.  The first is interim and has three rounds, the second is interim and waits on its
  experiments.
* [chain-proofs.csv](chain-proofs.csv): the chain's proofs at 2176, 3000, 4000, 5000 and 5060, from
  `lab/work/gapdash/proofs-gap.csv`: the gap, the nodes and the CPU-hours.
* [patches/](patches/): the code, as `git am` patches, in three series, as the branches made them and unedited.
  [patches/e1-smooth-bound/](patches/e1-smooth-bound/) has five patches that apply in order to master's ba59242, made
  with `git format-patch --no-merges e1-smooth-bound ^master`.  [patches/e12-hub-branching/](patches/e12-hub-branching/)
  has three that apply to the tip of the first series, 7a4a74a, and [patches/f2-split-bound/](patches/f2-split-bound/)
  three that apply to its fourth commit, 9c8f27c, each made with `git format-patch --no-merges BRANCH ^e1-smooth-bound`.
  The commit messages and comments of the patches cite the two reports by the file names that the reports had when they
  were written, which are `study-report-1.md` and `study-report-2.md` here.
* [e1/](e1/): E1, E11 and E8.
  * [results.jsonl](e1/results.jsonl): a line a run of 2176 to 5140 for B of 11, 13 and 23, in the fields `e1_smooth.rs`
    writes: `PB_s_upper` and `PB_s_lower` are a stopped run's range, `processed` the nodes solved and `leaf_promotions`
    the promotions of the leaf.  [small.jsonl](e1/small.jsonl) is 400 to 1300, [validate.jsonl](e1/validate.jsonl) 300
    to 1300 with and without the incumbent and with the other ground set, [sweep.jsonl](e1/sweep.jsonl) B of 23 at 1500
    to 4750, [bsweep.jsonl](e1/bsweep.jsonl) B of 17 to 47 at 3000 and 5000, [timing.jsonl](e1/timing.jsonl) the runs
    with timers and [dive.jsonl](e1/dive.jsonl) the depth-first dives.
  * [hubs.jsonl](e1/hubs.jsonl) is E11's runs of 3000 to 5061 with the faster test on 16 threads,
    [hubs-v1.jsonl](e1/hubs-v1.jsonl) the first test's runs, and [hubval.jsonl](e1/hubval.jsonl) and
    [hubval2.jsonl](e1/hubval2.jsonl) the checks at 400 to 2176.  [e8.jsonl](e1/e8.jsonl) is E8's runs.
    [table.md](e1/table.md) is E1's table.
  * [logs/](e1/logs/): each run's progress, every 20 s for E1 and 2 s for E11 and E8, the logs of stopped runs under
    their own names (`-v1`, `-stopped`, `-skipped`, `-probe`, `hubsfull-4000-23.log`).
  * [runs.sh](e1/runs.sh) to [runs8.sh](e1/runs8.sh) are the drivers in the order they ran, each resuming after an
    interruption.  [make_table.py](e1/make_table.py) (`python3 -I make_table.py results.jsonl more.jsonl > table.md`)
    makes the table.  [check_leaf.py](e1/check_leaf.py) and [check_hubs.py](e1/check_hubs.py) (`python3 -I check_leaf.py
    RESULTS.jsonl`) check the leaves from the definitions.  [e11_times.py](e1/e11_times.py) (`python3 -I e11_times.py N
    ...`) reads E11's crossing times off the logs.
* [e5/](e5/): E5.  [fetch.py](e5/fetch.py) (`nice -n 19 python3 -I -B fetch.py N ...`) caches the heaviest set and the
  recorded game, and [e5.py](e5/e5.py) (`nice -n 19 python3 -I -B e5.py [--light] N ...`) writes [out/](e5/out/), a
  report and a JSON file a game; `e5.py --summary` makes `out/summary.md`, the table of all 52 instances.
* [e9/](e9/): E9.  [run.sh](e9/run.sh) (`./run.sh LIST PARALLEL THREADS SECONDS`) runs the tests of a list, with
  [list-1.txt](e9/list-1.txt) the 12 closest candidates, [list-2.txt](e9/list-2.txt) the next 48 and
  [list-3.txt](e9/list-3.txt) the 5 probes past 959.  [window-5061.jsonl](e9/window-5061.jsonl) and
  [window-5061-all.jsonl](e9/window-5061-all.jsonl) list each candidate's fixed bound and its excess over the best-known
  score, [results.jsonl](e9/results.jsonl) and [out/](e9/out/) each test's line, and [logs/](e9/logs/) its progress.
  The build was the companion entry's commit fac59be.
* [f2-1/](f2-1/): the split bound.  [xstar.py](f2-1/xstar.py) (`python3 -I xstar.py N ... > xstar.jsonl`) makes X\* at
  each game, [xstar.jsonl](f2-1/xstar.jsonl) with [xstar_small.jsonl](f2-1/xstar_small.jsonl) and
  [xstar_large.jsonl](f2-1/xstar_large.jsonl) its two halves; [run_board.sh](f2-1/run_board.sh) (`./run_board.sh N
  [PEEL] [THREADS] [SECONDS]`) runs item 1 at a game; [make_table.py](f2-1/make_table.py) makes
  [table.md](f2-1/table.md) from [out/](f2-1/out/); [check_term.py](f2-1/check_term.py) (`python3 -I check_term.py N
  SECONDS H,H,...`) checks a term with the second study's Python.  `out/N_xstar.json` is item 1,
  `out/3000_xstar_asc.json` and `out/3000_xstar_desc.json` the other peels, `out/1000_enum.json` item 4,
  `out/1000_maxx.json` and `out/N_localR.json` item 2, and `out/2000_xbest.json` with `out/2000_xbest_python.txt` the
  check of 2000's best set.  [logs/](f2-1/logs/) has the progress lines.
* [e12/](e12/): E12.  [check.sh](e12/check.sh) and [check.jsonl](e12/check.jsonl) are the check at 400 to 2176 in three
  modes, and [check_leaf.out](e12/check_leaf.out) and [check_hubs.out](e12/check_hubs.out) check its 27 leaves.
  [variants.sh](e12/variants.sh) and [variants.jsonl](e12/variants.jsonl) are the variants at 1000 to 3000, a line a run
  with its tag in `variant`, and `python3 -I summary.py` ([summary.py](e12/summary.py)) prints one line a run.
  [boards.sh](e12/boards.sh) and [boards.jsonl](e12/boards.jsonl) are the three games, each line with `hub_log`, the
  first 60 hub branchings in full, and `own_stats`, the counters of the tables.  [leaf-3000.jsonl](e12/leaf-3000.jsonl)
  and [leaf-4000.jsonl](e12/leaf-4000.jsonl) are the leaves of the games, checked by
  `check_{leaf,hubs}-{3000,4000}.out`.  [target.sh](e12/target.sh) and [target_check.sh](e12/target_check.sh) are E12b's
  drivers, not run.  [logs/](e12/logs/) has each run's progress, every 5 or 20 s.
* [study-1/](study-1/) and [study-2/](study-2/): the studies' scripts and outputs, in Python, which the reports cite;
  [study-1/notes.md](study-1/notes.md) is the first study's raw notes, entries R1 to R8.

## Commits

The commits are on three branches of the research repository, never pushed and to be deleted, so `git show` may not find
them, and the patches are the record.  The lines of the runs name the commit that was checked out when each build was
made.  Each series is against the commit before it.

`e1-smooth-bound`, from master's ba59242:

* 8a5345a (09:42): the example `e1_smooth.rs`, PB_s, for E1.
* 5f5f808 (11:20): the thread time by part, the augmentations and the distinct conflicts.
* 26416c8 (11:55): the depth-first dive, and `--hubs`, PB_sh, for E11.
* 9c8f27c (12:33): `--every`, the seconds between progress lines.
* 7a4a74a (13:45): the faster hub test with the same outcome, for E11.

`e12-hub-branching`, from 7a4a74a:

* a8f66ea (17:22): `--own`, the branching on who pays a hub, `--no-project`, `--dfs` and `--target`, and in `src/gf2.rs`
  the instance with dropped factors.
* d4ba11a (17:37): the variants `--chain-forced`, `--probe` and `--no-root-check`.
* 3a4f697 (17:58): `Gf2Frames`, which makes again only the frames whose moves lose a factor, with a cache of 256
  instances a worker, and `--probe-live K`.

`f2-split-bound`, from 9c8f27c:

* 84b7ff6 (13:30): `--split --xstar`, the term of the split bound at X\*, for item 1.
* 19dd86f (14:48): `--margins`, the count of smooth configurations near the best, and `--max-x`, the search over hub
  sets, for items 4 and 2.
* 7151c78 (15:03): `--local R`, the hill climb over hub sets.

E9 was built from the companion entry's commit fac59be, which adds `--picks`, `--bars` and `--window` to the program.
Only the second series changes the solver's `src/`; the first and third change the example alone.

The commit that adds this entry also adds its rows to the register's file of [stronger
bounds](../../register/stronger-bounds.md).
