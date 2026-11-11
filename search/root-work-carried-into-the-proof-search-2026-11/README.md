# Root work carried into the proof search (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-10.  Concluded 2026-11-10.

**Question.**  A separate program can compute, at the root of a game, a bound tighter than the one the search uses, with
the conflicts and the hubs it meets on the way.  Does that work, done once at the root and used inside the exact search
of a proof, make the proof cheaper?  Six experiments, all on game 4848, tried it in six ways.

**Answer.**  No: root work does not pay inside the search.  The root's bound is real, since it closes 839 of the 1,940
points of the gap of 4848, but each use of it inside the search removes work that the search does anyway or costs more
than it saves.  The two that cut the steps most, the root's cores as nogoods at nine times the store and a rule that
bars smooth members in mixed conflicts, cut them to 0.87 and 0.88 times and raised the CPU to 1.66 and 1.06 times, and
the worst, hub-ownership branching, doubled the branchings (1.96 times).  The search already branches on the smooth
members where its work is.

## Method

### The words

*Smooth and fiber.*  A number is *smooth* when all its prime factors are at most 23, and a *fiber* number when it has a
prime factor above 23.  A fiber number a · p, with p above 23, is in the fiber of p.  The bound 23 is the *smoothness
bound*, B; one root search used B = 31.  A number's *layer* is its number of prime factors, counted with multiplicity
([the glossary](https://github.com/bvchess/taxman/blob/ba59242/docs/GLOSSARY.md#the-frame-model) defines the layers).

*The smooth bound.*  The parity bound is the frame solver's bound at a game's root ([the
glossary](https://github.com/bvchess/taxman/blob/ba59242/docs/GLOSSARY.md#bounds)).  The smooth bound, PB_s, adds one
condition to the parity bound's: in every layer, the smooth numbers of the set must be playable among themselves.  Every
playable set meets it, so PB_s is an upper bound on opt(n), given [statement
U](https://github.com/bvchess/taxman/blob/ba59242/docs/theory/exactness.md#statement-u) as for every proof past 2531.  A
program apart from the solver, the example `e1_smooth.rs` of the research repository's branch `e1-smooth-bound`,
computes it at a game's root by a best-first branch and bound.  At the root of 4848 it gives 7,393,307, against the
parity bound's 7,394,146 and opt(4848)'s 7,392,206, so it closes 839 of the 1,940 points of the gap, 43.3%.

*Cores, hubs and bars.*  When the smooth numbers of a layer cannot all be played, the program finds a *core*, a smallest
set of numbers that cannot all be promoted together.  A core is a conflict of the root, so it holds at every node of the
search.  A *hub* is a smooth number a that a fiber number a · p lists as a maximal factor and that smooth numbers of the
same conflict list as well.  The number a pays for at most one move, a fiber or a smooth one, so a game uses it for one
of the two sides.  At the root, a candidate y is *barred* when the smooth bound with y promoted is below opt(n), so that
no set that promotes y reaches opt(n).

*The search's words.*  A step is one candidate that a node's loop tries, and the `nodes` of the results lines count
steps ([the glossary](https://github.com/bvchess/taxman/blob/ba59242/docs/GLOSSARY.md#the-search) defines the search's
terms).  A *branching* is a step of a node that chooses a branch: the child promotes a member of the node's conflict,
and the node goes on without that member, which is then barred.  A branching is a *choice* when its conflict has two or
more members and strong branching picks the member to bar, and *forced* when the child promotes the node's forced
members and the node's loop ends.  A conflict is *mixed* when it holds smooth and fiber members.

### The game and the baseline

Every experiment is on game 4848, whose gap is 1,940 and whose opt(4848) is 7,392,206, 534,239 promotions.  The baseline
is the standalone proof of 4848 of [the proofs entry](../../proofs-past-5060-one-game-at-a-time-2026-11/README.md): no
seed, no ceiling and no near-repeat cut, 16 threads, 23,075,195 steps and 12,324 CPU-seconds in 780 seconds.  The proofs
of the experiments used its flags (`--force-search`, `--tactic prev_cap=off`, `--tactic near_repeat=off`, `--window 1`,
the default gate), at idle priority.  The proofs of E6, E7, E2 and E14 shortened the finder to 60 seconds
(`--finder-seconds 60`).  The finder only offers sets, so it changes how soon the incumbent is found, and the three
baselines, with finders of 900 and 60 seconds, took 22.7 to 23.1 million steps.

The branchings of the baseline come from two traced proofs, which change nothing in the search: E6's, on 4 threads, with
13,462,572 branchings in 22,681,368 steps, and the one that sampled nodes for E2, on 16 threads, with 13,695,832 in
23,063,758.  A proof's CPU depends on the build and on the load of the machine.  The builds of E2-lite and E9b had no
link-time optimization, as the study's brief asked, and ran on a loaded machine, so their CPU is compared with the
baseline's only with care.  The steps and the branchings do not depend on either, and they are what the rules compare.

### The six experiments

Each experiment's rule was fixed before it ran, by the study that proposed it or by the coordinator: it *confirms* an
idea at its first bound and *kills* it at its second.  The label of each is the study's, kept because the folders, the
patches and the register use it.  All ran on 2026-11-10, in Pacific time.

| label | what it does | ran | rule, on the baseline's count | code |
|---|---|---|---|---|
| E2-lite | loads the root's smooth cores as nogoods before the proof | 15:20 to 16:55 | steps: confirms at 0.5 or less, kills above 0.8 | 5953b6e, fac59be |
| E2 | runs the smooth test at 240 sampled nodes of the proof | 16:46 to 17:01 | solves to cut a node of gap 300 to 958: confirms at about 10 or fewer, kills at as many as the node's subtree has steps | 4b8ca97, 915e689, 4aef47a |
| E6 | measures which members the search bars, smooth or fiber | 09:39 to 10:42 | no number: smooth-first branching is in effect or it is not | 4b8ca97 |
| E7 | bars a smooth member of a mixed conflict | 16:32 to 16:46 | branchings: confirms at 0.7 or less, kills at 0.95 or more | 915e689 |
| E9b | loads the root's bars as one-member nogoods | 17:05 to 17:35 | steps: confirms at 0.5 or less, kills above 0.8 | c235b4a |
| E14 | gives a mixed conflict's hub away to one side in each child | 17:47 to 18:28 | branchings: confirms at 0.5 or less, kills at 0.9 or more | 96345d1, 64111a2 |

## Results

### The six against their rules

| experiment | result | against the rule |
|---|---|---|
| E2-lite | 0.983 times the steps with 37,774 nogoods, 0.871 with 330,476; CPU 1.26 and 1.66 times | killed, above 0.8 in both |
| E2 | 0 of 120 nodes of gap 300 to 958 cut within 10 solves; a cut spends 6.2 and 10.2 solves for each step it saves | killed |
| E6 | 85.2% of the steps below choices lie under a smooth member that was barred; 41.9% of the candidates are smooth | the search already branches on the smooth members where its work is |
| E7 | 0.894 times the branchings, 0.876 times the steps; CPU 1.06 times | between the two bounds, and no cheaper in CPU |
| E9b | 1.016 times the steps; CPU 1.04 times | killed |
| E14 | 1.96 times the branchings; CPU 1.86 times; the propagating form 1.005 times | killed |

### E2-lite: the root's cores as nogoods

*Question.*  Does loading every smooth core that the root search meets into the solver's store of nogoods, before the
proof starts, cut the steps of a standalone proof of 4848?

*Method.*  The program writes each distinct core it finds, in every deletion order, as the core's *literals*: its
members up to n/2 and the promotions that its members have as maximal factors.  The solver's store of carried nogoods
([carried nogoods](https://github.com/bvchess/taxman/blob/ba59242/solver/docs/design/carried-nogoods.md)) reads them as
the nogoods of the game before.  It checks each set at the root by the peel that the search learns its own nogoods by,
keeps the frame-minimal conflict that the peel finds inside it, and uses the nogoods only to prune: it rules out a
candidate that would complete one and ends a node whose forced members complete one.  A core is a valid nogood because a
set that holds the sources and all of a core's literals holds its members with lists no longer than where the core was
found, so the set is not playable.  The solver's own validation kept every set (none had a member that was not a
candidate, and none was promotable), and a check from the definitions alone, with `check_nogoods.py` and `parity.py`,
passed every core and every kept nogood.  The proof was the baseline's command with `--carried-dir`.

*Results.*  The root searches, on 8 threads:

| B | smooth bound at 4848 | share of the gap | nodes | seconds | cores exported | nogoods kept |
|---|---|---|---|---|---|---|
| 23 | 7,393,307 | 43.3% | 76,720 | 304 | 80,619 | 37,774 |
| 31 | at most 7,392,984, stopped | at least 59.9% | 1,064,912 | 2,411 | 648,004 | 311,690 |

The B = 31 search stopped at its 2,400-second limit with 2.5 million nodes open, and its cores are valid all the same,
since a core does not depend on the search ending.  The cores of B = 23 and 31 together are 330,476 nogoods.  The
proofs, on 16 threads, all ended `proof=exhausted` at 7,392,206:

| proof | nogoods loaded | steps | times the baseline | CPU-s | times the baseline | wall s |
|---|---|---|---|---|---|---|
| baseline | none | 23,075,195 | 1 | 12,324 | 1 | 780 |
| B = 23 | 37,774 | 22,674,927 | 0.983 | 15,562 | 1.26 | 2,024 |
| B = 23 and 31 | 330,476 | 20,090,478 | 0.871 | 20,431 | 1.66 | 1,510 |

The store was used a great deal and changed little:

| proof | candidates the store ruled out | nodes it ended | own nogoods learned | candidates ruled out by them |
|---|---|---|---|---|
| baseline | | | 217,515 | 10,674,195 |
| B = 23 | 11,894,090 | 3,146,044 | 229,556 | 9,343,061 |
| B = 23 and 31 | 20,484,663 | 3,303,905 | 199,307 | 8,790,941 |

The 37,774 nogoods ended 14% of the nodes and the steps fell 1.7%.  Nearly every node that the store ended stood in for
one that the search would have spent anyway: a node whose forced members complete a core is, without the store, a node
that branches on that core and whose children die at once.  That reading is not measured node by node, but the counts
fit it, since the search learned about as many nogoods of its own.  The cores of B = 31 do better (0.87) at nine times
the store, but the CPU rises to 1.66 times.  The store costs every step, about 4.5% of the CPU at 20,000 nogoods and 10%
at 50,545 ([the root gap and the size of a game,
2026-10-28](../the-root-gap-and-the-size-of-a-game-2026-10/README.md#2026-10-28-what-the-store-costs-a-step)), and E9b's
proof with a store too small to cost anything, on the same kind of build, took 3% more CPU a step than the baseline, so
most of the rise in CPU is the store's own work.  5019 was not run, since the rule asks for it only if 4848 gains.

*Verdict.*  Not kept: the steps fall to 0.98 times, and to 0.87 times at nine times the nogoods, with 1.26 and 1.66
times the CPU.

### E2: the smooth test at nodes

*Question.*  At a node of the proof, can the smooth test cut the node within a few GF(2) solves?  The test is a
depth-first search over smooth cores, begun from the node's own promotions and bars, with the proof's final incumbent as
its target.  It cuts the node when every leaf of the test is at or below the target, and stops with no cut at the first
smooth-playable set above the target or at a budget of 10⁴ solves.  The study's arithmetic was that the whole of the
smooth bound's reduction near 5060, 959 points, is worth at most about 70 inner solves a node, and 10 times fewer steps
would need it in about 7.

*Method.*  A traced proof of 4848 (the one with 13,695,832 branchings) sampled its branchings' nodes with the numbers
they had promoted and their candidates.  A script drew 60 nodes at random in each of four bands of the node's gap, its
bound less the incumbent: 100 to 299, 300 to 599, 600 to 958 and 959 to 1,499.  It drew only from nodes met with the
proof's final incumbent in place, so that the gap is against the test's target.  The bands hold 8,874,848, 2,892,910,
320,862 and 17,538 of the trace's branchings.  The test ran at each of the 240 nodes from scratch, with the smooth cores
and the pricing, and recorded whether it cut, the solves it used, the bound it reached, and from the trace the node's
subtree in steps.  A policy is a gap threshold, below which a node gets the test, and a budget of solves.  A cut saves
the rest of the node's loop and costs its solves, and an uncut node costs the lesser of its solves and the budget.  The
sample's means, times the bands' populations, give each policy's totals.

*Results.*  At all 240 nodes the program's bound equals the solver's.

| gap band | cut within 10⁴ solves | within 10 | within 30 | within 100 | median solves of a cut | median loop of a node, in steps | solves a cut spends for each step it saves | mean bound reduction, of the mean gap |
|---|---|---|---|---|---|---|---|---|
| 100 to 299 | 48 of 60 | 20 | 40 | 47 | 13 | 6 | 2.6 | 166 of 199 |
| 300 to 599 | 28 of 60 | 0 | 5 | 12 | 144 | 44 | 6.2 | 215 of 393 |
| 600 to 958 | 3 of 60 | 0 | 0 | 0 | 2,371 | 382 | 10.2 | 103 of 701 |
| 959 to 1,499 | 0 of 60 | 0 | 0 | 0 | | 5,172 | | 74 of 1,037 |

In the bands from 300 up, the nodes that the test does not cut have a smooth-playable set above the incumbent, 32 of 60
at 300 to 599, 57 of 60 at 600 to 958 and all 60 above, and it takes a median of 36, 91 and 196 solves to find that set.
A solve costs 6.74 ms against 0.54 ms for a step of the proof, 12.4 steps.  At budgets of 10 solves or more, a solve
saves between 0.14 and 0.36 steps of the proof, and every policy loses even with the solve priced at a single step, by
26 million to 630 million steps against the proof's 23 million.  The savings are an upper bound, since the subtrees of
cut nodes that lie inside cut nodes are counted for each node that holds them.

*Verdict.*  Not kept, killed by its rule: a cut at gap 300 to 958 spends 6 to 10 times as many solves as the steps it
saves, and not one of the 120 nodes was cut within 10 solves.

### E6: which members the search bars

*Question.*  Does the search bar smooth members or fiber members of its conflicts?  If it already bars smooth ones where
its work is, an order that puts the smooth knot first is in effect already, and a gain from root work has to come from
the bound.  If it bars fiber members, smooth-first branching would be a real change.

*Method.*  The search wrote a trace of every branching of a standalone proof of 4848 on 4 threads: its kind, its gap,
the size of the child's subtree in steps, its conflict's members and the member branched on.  A script classified each
member as smooth or fiber and weighted a branching by 1 (count) or by 1 plus the steps in its child's subtree (the work
that the choice leaves to explore).  Subtrees cut short by a unit handed on or by the end of the run give a short count:
7,671 of the choices' and 1,580 of the forced branchings'.

*Results.*  The proof has 13,462,572 branchings: 6,456,191 choices (48.0%), which hold 79.7% of the subtree weight,
6,926,958 forced branchings (51.5%), which hold 20.3%, and 79,423 whose conflict has one member (0.6%).  The member that
a choice bars is smooth in 60.5% of the choices and in 85.2% of the weight.  By layer, with the candidates for
comparison:

| layer | candidates, smooth of all | barred member smooth, by count | by steps below |
|---|---|---|---|
| 3 | 119 of 571 | 0.0% | 3.6% |
| 4 | 163 of 386 | 46.6% | 68.0% |
| 5 | 128 of 204 | 49.6% | 93.7% |
| 6 | 78 of 99 | 82.4% | 91.5% |
| 7 | 41 of 44 | 99.8% | 99.9% |
| 8 and 9 | 27 of 27 | 100% | 100% |
| all | 559 of 1,334 | 60.5% | 85.2% |

The smooth candidates are 41.9% of all, and the search bars them in 85.2% of the weight, in 93.7% in layer 5 and 91.5%
in layer 6.  By the gap of the node, the share by weight is 57.9% below 300, 85.5% from 300 to 999 and 89.7% from 1,000.
In a choice whose conflict mixes the two kinds, the barred member is smooth in 64.6% of the choices, where a blind pick
within the conflict would give 52.6%, and in 62.6% of the weight, where a blind pick would give 65.3%.  So by count the
search prefers the smooth members, and by weight it shows no preference.

*Verdict.*  Measured: smooth-first branching is already in effect where the work is, so a gain from root work has to
come from the bound or from reusing its work.  E7 tested the one remaining form, a rule that bars smooth members in
mixed conflicts.

### E7: barring a smooth member in mixed conflicts

*Question.*  In a mixed conflict, where the search shows no preference by weight, does barring a smooth member (the rule
`TAXMAN_BAR_SMOOTH=23`) shrink the proof?  Any member of a conflict is as good a branch as any other for exactness,
since every completion leaves one out, so the rule changes only the tree.  Strong branching still prices every member,
so the forced members it finds are the same, and only the choice among the members whose removal lowers the bound most
is restricted.

*Results.*  The proof ended `proof=exhausted` at 7,392,206 on 16 threads.  It took 20,205,269 steps (0.876 times the
baseline's 23,075,195), 12,037,956 branchings (0.894 times E6's 13,462,572) and 13,055 CPU-seconds (1.06 times the
baseline's 12,324).  The trace confirms that the rule worked: the barred member of a mixed conflict is smooth in 100% of
the choices.  Choices are 48.7% of the branchings and hold 80.0% of the subtree weight, as in E6.

*Verdict.*  Not kept.  The rule fixed in advance confirms at 0.7 and kills at 0.95, and 0.89 is between them, so by it
the experiment neither confirms nor kills.  The steps fall by 12%, more than the spread of three baseline proofs of 4848
(22.7 to 23.1 million steps), and the CPU rises by 6%, so the proof is no cheaper.

### E9b: the root's bars in the search

*Question.*  The smooth bound bars many candidates at the root of 4848.  Does a proof with those bars loaded take fewer
steps than the baseline's?

*Method.*  A bar of y says that the smooth bound with y promoted is at most 7,392,205, opt(4848) less one, so every set
that promotes y scores less than opt(4848).  Barring y is then safe, since an optimal set that played a barred y would
score less than itself.  The program listed each candidate's GF(2) bound with it fixed the other way, and ran the smooth
bound with each candidate outside the heaviest set promoted, against the target 7,392,205.  It tested all 313 candidates
outside the heaviest set whose plain bound with them promoted is at most 839 above the target, the root's reduction, and
29 beyond it, at 841 to 938 above.  Of the 342 tests, which took 2.25 thread-hours, 309 are bars: 307 of the 313, and 2
of the 29.  The plain bound already bars 68 candidates at this target, which were not tested.

The store of nogoods does not keep a one-member set, since y alone can be promoted and only the score bars it.  So a
directory of stores may hold `bars-N.txt`, which the store adds for game N unchecked as nogoods of one member.  At the
start of every unit's node the store rules the candidate out of the node's candidates, and every node below draws its
candidates from its parent's, so y is never promoted, and each bound, heaviest set, forced member and conflict of the
search is computed without it.  The optimal game of 4848 (261 promotions) plays none of the 309 bars.

*Results.*  The proof, on 16 threads, ended `proof=exhausted` at 7,392,206:

| proof | bars | steps | times the baseline | CPU-s | times the baseline | wall s |
|---|---|---|---|---|---|---|
| baseline | none | 23,075,195 | 1 | 12,324 | 1 | 780 |
| with the bars | 309 | 23,437,471 | 1.016 | 12,843 | 1.04 | 1,026 |

The store ruled 309 candidates out, once each, at the root unit's node and ended no node.  The search learned 224,526
nogoods of its own against 217,515 and ruled out 10,742,143 candidates by them against 10,674,195.  The bars are numbers
outside the root's heaviest set, and the search's own bounds and pricing keep them out of the nodes that make the tree.

*Verdict.*  Not kept: 1.016 times the steps and 1.04 times the CPU, with the same opt(4848).  The 1.6% is no gain, and
it is about the size of the baseline's variation from run to run (see the limits).

### E14: hub-ownership branching

*Question.*  In a mixed conflict, a fiber number a · p and some smooth members share the hub a.  Does a branching that
gives a away cut the branchings of the proof of 4848?  The hub a pays for at most one move, so every game is a game of
one of two graphs.  In the graph S(a) no fiber is paid by a, and in F(a) no smooth move is.  A set that is promotable
with fewer edges is promotable with all of them, so a set found in either graph is a game.  The rule
(`TAXMAN_HUB_BRANCH`) makes two children with the node's own promotions and candidates, one in each graph, and the
node's loop ends, so the two cover every completion.  Each child is searched as a nested search over a search space of
its own, the model with the edges left out, a rebuilt GF(2) graph and the symmetry rule of the full model, which takes
in the parent's nogoods.  A unit handed on while a child runs becomes a unit of the full graph, a superset, so nothing
is lost.  The hub is the one with most smooth listers in the conflict, then most fibers.  The study predicted that the
fiber side would not fall at the GF(2) level, since the smooth knot's need for a is an order fact.

*Method.*  Two proofs on 16 threads with the flags of E7, which are the baseline's with a finder of 60 seconds.  E14
gives hubs away at depth 1 (one hub step on a path) at gap 300 or more.  E14b, the propagating form, branches on a hub
only where one child is cut on sight, so that the node goes on in the other child with the hub given away, and looks at
up to 3 hubs for one.

*Results.*  Both proofs ended `proof=exhausted` at 7,392,206.

| proof | branchings | steps | CPU-s | times the baseline's branchings |
|---|---|---|---|---|
| traced baseline, 16 threads | 13,695,832 | 23,063,758 | 12,555 | 1 |
| E14, depth 1, gap 300 or more | 26,803,125 | 44,810,455 | 23,353 | 1.96 |
| E14b, propagating only | 13,767,091 | 23,189,934 | 14,353 | 1.005 |

Against E6's 13,462,572 branchings, E14 has 1.99 times.  Its 5,637 hub steps added 21.7 million steps, about 3,850 a hub
step.  Both children always have games and both stay large: on game 3000 at depth 1, S took about 220 steps and F about
135 on average, and none of 588 hub steps had a dead child, so the two together cost about 3 times what the standard
branching spends on the same nodes.  At 3000, depth 1 gives 1.3 to 1.6 times the steps of the baseline's 314,270, and
depth 3 gives 2 times, because every level repeats the games in which a pays nobody.  Two other runs, at depths 3 and 6,
had not finished at 400 seconds, with 12 and 8 times the baseline's steps by then.  E14b fired 29 times in the whole
proof, so there are no free hub fixings, since neither child is ever dead on sight, and its extra CPU is the
cut-on-sight solves.

*Verdict.*  Not kept, killed at 1.96 times the branchings, against the kill line of 0.9.  The same opt(n) came out on
games 1500, 2176, 3000 and 4848, but that is a check and not a proof of the rule's soundness.

### What the six share

In each, the root's work is correct and the search already does the same work, or does it more cheaply, where the work
is.

* **The store prunes leaves.**  The cores as nogoods (E2-lite) and the bars (E9b) barely move the count of steps, which
  fits a store that removes refutations that the search would have made at nearly the same cost.
* **A solve costs more than it saves.**  The smooth test (E2) takes 12.4 steps a solve and saves a fraction of a step a
  solve, and it can cut only the nodes of a small gap, where the subtrees are small.  Where the gap is large, the nodes
  have a smooth-playable set above the incumbent, which the test finds and cannot cut.
* **The search already goes where the work is.**  It bars smooth members in 85% of the weight (E6), a rule that bars
  them more often saves 12% of the steps and costs more CPU (E7), and a branching on the hubs doubles the work, because
  the fiber side stays as large as the node (E14).

The study's report reads the measurements together as follows: the proof's search is in effect an enumeration of the
smooth-playable configurations above the incumbent, each refuted through its fiber context in a small subtree, so the
smooth bound does not shrink that enumeration, it is the enumeration.  Only a bound that is tighter on the smooth part
shrinks it.  This is the study's reading of E6 together with its root runs, not a measurement of this entry.

## Limits

* **One game, 4848, and one proof for each setting.**  The baseline's step count varies from run to run: three baseline
  proofs of 4848 took 22.7 to 23.1 million steps, and four baseline proofs of game 3000 took 287,464 to 314,270 steps,
  9% apart.  The 1.96 of E14, the 0.87 of E2-lite and the 0.88 of E7 are outside that variation, and the 1.016 of E9b is
  about its size.
* **The CPU is compared with care.**  E2-lite and E9b ran builds without link-time optimization, on a machine at a load
  of about 95 on 88 hardware threads, and the baseline's build had it.  E6 ran on 4 threads.
* **E2's test ran from scratch,** at 6.74 ms a solve.  The study's design warm-starts it from the node's bound, which
  would cost less a solve.  Every policy still loses with the solve priced at one step, so the cost of a solve is not
  what decides it.  The sample is 60 nodes in each of four bands of 4848's proof, drawn at the final incumbent.
* **E6 and E7 weight by the steps below a branching,** and some subtrees were cut short by a hand-off.  The conclusions
  rest on shares of 85% and more, which 9,251 short subtrees of 13.5 million branchings do not move.
* **E7's verdict is a reading of the rule's two lines.**  The study fixed no line for the area between them.
* **Validity.**  Everything here is given statement U, like every proof past 2531.  The soundness of E14's rule is
  argued and checked on four games, not proved.
* **Nothing was run on another game,** so how the factors move with n is not measured.

## Decision

None of the six is kept, and the solver is unchanged.  The code of each lives on unpushed branches of the research
repository, kept here as patches.  The switches `TAXMAN_BRANCH_TRACE`, `TAXMAN_BAR_SMOOTH` and `TAXMAN_HUB_BRANCH` were
experiments and were not merged.

What would reopen it:

* a test at a node that cuts the nodes of gap 300 to 958 within a few solves, where E2 found medians of 144 and 2,371
  solves, or a bound that cuts far more nodes there;
* hub-ownership branching at hubs where one side is nearly dead, such as hubs 64 and 16 at the root, which the outer
  search's conflicts do not hold;
* a measurement on another game, past 5060 or where the search's tree has a different shape, if a root bound tighter
  than the smooth bound is found;
* a store of cores whose lookups cost less, if a larger B pays, since B = 31 gave 0.87 times the steps.

## Files

The experiments ran in the scratch folder `lab/work/oddcore/`, in the folders `e2/`, `e2-nodes/`, `e6/`, `e7/`, `e9b/`
and `e14/`, and each keeps its folder here.  No binary is kept (86 to 104 MB each), and neither are the two traces of
1.2 GB each (`e6/trace/`, the sampled-node proof's `e2-nodes/run/trace/`), the exported cores and the nogood stores (12
MB to 364 MB), and the checkpoints.  The paths in the scripts are those of the scratch folder.

* [patches/](patches/): the code, as `git am` patches.  `patches/e6-branch-classes/` holds five patches and
  `patches/e2-root-cores/` three, each made with `git format-patch --no-merges BRANCH ^master ^e1-smooth-bound`, so they
  apply in order to the tip of the branch `e1-smooth-bound` (7a4a74a), which is master's ba59242 with one more file,
  `solver/frame/examples/e1_smooth.rs`.  The three patches that change that file need it.  The program is not part of
  this entry.  A comment of the patch of 4aef47a and one of `e2_analyze.py` cite the study's report, and cite it here as
  "the study's report" in place of its file name.
* [e2-lite/](e2-lite/): E2-lite.
  * [prove.sh](e2-lite/prove.sh) (`./prove.sh TAG N STORE_DIR [LIMIT]`): a standalone proof with a store, the baseline's
    flags, at idle priority.  [jobs.log](e2-lite/jobs.log), [out/](e2-lite/out/) and [logs/](e2-lite/logs/) have each
    proof's times, results line and log.  The proof of B = 23 ran the build of 5953b6e with the store's read limit at
    200,000, and the proof of B = 23 and 31 the build of fac59be with it at 1,000,000.
  * [root.jsonl](e2-lite/root.jsonl): the two root searches' result lines, with their logs `logs/root-4848-23.log` and
    `logs/root-4848-31.log`.  [validate.jsonl](e2-lite/validate.jsonl): the store's validation of the cores, by
    `examples/e2_validate.rs` (the second line is a 20,000-core test under the old read limit).
  * [check_nogoods.py](e2-lite/check_nogoods.py) (`python3 -I check_nogoods.py N EXPORT.jsonl KEPT.txt`) checks the
    cores and the kept nogoods from the definitions, with [parity.py](e2-lite/parity.py), a script of the study's brief
    that computes the parity bound and its cores; [check.jsonl](e2-lite/check.jsonl) is what it printed.
* [e2-nodes/](e2-nodes/): E2.
  * [draw_sample.py](e2-nodes/draw_sample.py) (`draw_sample.py PREFIX 534239 60 sample.txt`) draws the sample from the
    trace's node files, and [sample.txt](e2-nodes/sample.txt) is the 240 nodes drawn, one a line.
  * [e2-results.jsonl](e2-nodes/e2-results.jsonl): the lines of `e1_smooth --nodes sample.txt`, one a node, with the
    solves, the cut and the bound reached.  The command's flags were not recorded.
  * [e2_analyze.py](e2-nodes/e2_analyze.py) (`python3 -I e2_analyze.py e2-results.jsonl $(cat populations.txt) 0.54`)
    makes [results.md](e2-nodes/results.md), the band tables, the policies and each node's line, with the populations in
    [populations.txt](e2-nodes/populations.txt).  [standalone-4848.jsonl](e2-nodes/standalone-4848.jsonl) and
    [standalone-4848.log](e2-nodes/standalone-4848.log) are the traced proof that the sample came from, 16 threads, 60
    seconds of the finder.
* [e6/](e6/): E6.  [analyze.py](e6/analyze.py) (`python3 -I analyze.py 4848 PREFIX [BOUND]`) reads the trace files and
  makes [results.md](e6/results.md), whose tables are by layer, by weight, by gap and by the conflict's composition.
  [standalone-4848.jsonl](e6/standalone-4848.jsonl) and [standalone-4848.log](e6/standalone-4848.log) are the traced
  proof, 4 threads.  [candidates.txt](e6/candidates.txt) is the search's 1,334 candidates, the base rate of the tables.
* [e7/](e7/): E7.  [standalone-4848.jsonl](e7/standalone-4848.jsonl) and [standalone-4848.log](e7/standalone-4848.log)
  are the proof with the rule, and [results.md](e7/results.md) is E6's analysis of its trace, whose title still reads
  "E6 branch classes".
* [e9b/](e9b/): E9b.
  * [run.sh](e9b/run.sh) (`./run.sh N KNOWN LIST PARALLEL THREADS SECONDS`) runs the tests of a list, with
    [list-1.txt](e9b/list-1.txt), [list-2.txt](e9b/list-2.txt) and [list-3.txt](e9b/list-3.txt) the 342 candidates
    tested.
  * [window-4848.jsonl](e9b/window-4848.jsonl): each candidate's bound with it fixed the other way and its excess over
    the score; [results.jsonl](e9b/results.jsonl): each test's line; [jobs.log](e9b/jobs.log) and
    [logs/bars-4848.log](e9b/logs/bars-4848.log): the times and the proof's log.
  * [bars-4848.txt](e9b/bars-4848.txt): the 309 bars.  [prove.sh](e9b/prove.sh) (`./prove.sh TAG N STORE_DIR [LIMIT]`)
    is the proof, whose line is [proof/bars-4848.jsonl](e9b/proof/bars-4848.jsonl).
  * [singletons-test.txt](e9b/singletons-test.txt) and [singletons-validate.jsonl](e9b/singletons-validate.jsonl): the
    store's validation of four one-member sets, all dropped.
* [e14/](e14/): E14.  [run1/](e14/run1/) is E14 and [run2/](e14/run2/) E14b, each a results line and the log.
  [smoke/](e14/smoke/) holds the results lines of the runs on games 1500, 2176 and 3000, named
  `PREFIX-GAME-SETTING.jsonl` with the setting `DEPTH,GAP` of `TAXMAN_HUB_BRANCH`.  The prefixes `base` and `b` are
  baselines and `p` is the propagating form.  The prefixes `hub`, `smoke`, `d` and `sync` are variants and early runs
  that the builder's report does not describe, and three files are empty.

## Commits

The commits are on the branches `e6-branch-classes` and `e2-root-cores` of the research repository, never pushed and to
be deleted, so `git show` may not find them, and the patches are the record.  The lines of the proofs name the commit
that was checked out when each build was made and mark it dirty, since the changes were committed afterwards: E6's proof
names ba59242, E7's and the sampled-node proof's 4b8ca97, E14's 4aef47a, and E2-lite's two proofs 7a4a74a and 5953b6e.

`e6-branch-classes`, each against the commit before it, from 7a4a74a:

* 4b8ca97 (09:39): the trace of the branchings behind `TAXMAN_BRANCH_TRACE` (E6).
* 915e689 (16:32): the rule that bars a smooth member behind `TAXMAN_BAR_SMOOTH` (E7), and the trace's sample of nodes
  behind `TAXMAN_BRANCH_TRACE_NODES` (for E2).
* 4aef47a (17:01): `e1_smooth --nodes FILE`, the smooth test at sampled nodes (E2).
* 96345d1 (17:48): hub-ownership branching behind `TAXMAN_HUB_BRANCH` (E14).
* 64111a2 (18:17): E14's counts of the children of hub steps, those with no game and their steps, by side.

`e2-root-cores`, from 7a4a74a:

* 5953b6e (15:41): `e1_smooth --export`, which writes every distinct core as a store of nogoods;
  `examples/e2_validate.rs`, which checks a store at a game's root as a search does; the store's counts at the end of a
  search; and `--carried-dir` reading up to 200,000 sets (E2-lite).
* fac59be (16:29): the read limit at 1,000,000 sets, and `e1_smooth --picks`, `--bars` and `--window`.
* c235b4a (17:14): `bars-N.txt` in a directory of stores (E9b).

The commit that adds this entry and its rows in the register's files of [nogoods and
conflicts](../../register/nogoods-and-conflicts.md), [stronger bounds](../../register/stronger-bounds.md) and
[branching](../../register/branching.md).
