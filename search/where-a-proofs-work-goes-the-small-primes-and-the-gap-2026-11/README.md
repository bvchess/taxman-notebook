# Where a proof's work goes: the small primes and the gap (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-11.  Concluded 2026-11-11.

**Question.**  Does the work of a proof of a hard game lie in the arrangements of its small-prime numbers, or in the gap
that the search must close, so that a proof could be made cheaper by listing those arrangements or by counting the cheap
trades between them?

**Answer.**  No to both: the work lies in the gap, wherever the gap lies.  With the 13-smooth part of 5060 (its
candidates whose primes are all at most 13) fixed as in the optimal set, the rest of the game solves in 1,746 steps and
1.7 CPU seconds, against the chain's 1.2 billion steps; but listing the arrangements of that part is 915 times the plain
search's steps at 1500, at least 120 times its CPU at 2380 and at least 8.4 times the chain's CPU at 5060.  The size of
a tree follows the gap, at 5060 log10(steps) = −0.11 + 0.00290 × gap over 52 searches, a decade per 345 points, and the
small primes add nothing at matched gap.  Counting the cheap trades does not track the tree either, by a test run in
October ([local prime exchanges at the nodes](../local-prime-exchanges-at-the-nodes-2026-10/README.md)) that the second
study quotes.  The one sound cut that is left, a charge by split prices, is expected to save a few percent, and was
not built.

The question matters because a proof past 5060 is dear, about tenfold for every 476 points of the root's gap by a fit to
the chain's proofs ([root bounds](../root-bounds-for-the-odd-cores-past-5060-2026-11/README.md)), and a cheaper proof
needs some structure of the tree to exploit.  The [loops
study](../../the-loop-principle-and-game-5061-2026-11/README.md) had just solved game 5061 in seconds with the
candidates outside a region fixed as in the proven 5060, which suggested that the small-prime numbers carry the work.
This entry tests that suggestion, and the earlier hope of [the anatomy of a hard
subtree](../the-anatomy-of-a-hard-subtree-2026-10/README.md) that the cheap trades could be counted.

## Method

### The words

*Candidate, gap, step.*  A *candidate* is a number that the search may promote, and a *promotion set* is a set of them
that can be promoted together.  The *GF(2) bound* bounds the best score below every node of the frame solver's search
([the bound](https://github.com/bvchess/taxman/blob/287486e/solver/docs/design/gf2-bound.md)).  Its *gap* at a problem's
root is how far it lies above opt(n), in points of score, and a search *step* is one of the engine's steps, the unit in
which the chain's proofs are counted ([the glossary](https://github.com/bvchess/taxman/blob/287486e/docs/GLOSSARY.md)).

*The smooth part and the large-prime part.*  The *smooth part at B* is the set of candidates of game n's root whose
primes are all at most B: at 5060 and B = 13, 350 of the 1,380 candidates, such as 1560 = 2³·3·5·13.  The brief called
it the core, which the glossary uses for another notion, and this entry does not; the folder `core5060/` keeps the
brief's name.  The *large-prime part* is the other candidates, each with some prime above B, such as 1292 = 2²·17·19.

*Arrangement, fixing.*  An *arrangement* of the smooth part says which of its members are promoted.  *Fixing* a part
promotes the members that the committed optimal set holds and bars the others, and leaves every candidate outside the
part free.  The search then starts from a score to beat of opt(n) − 1, so that it must find a game worth opt(n) and
prove that none scores more, and every such search here returned opt(n).  The *optimal arrangement* is the committed
set's.

*The plain search and the smooth-part tree.*  The *plain search* is the frame solver's search of the whole game, from an
incumbent worth opt(n), with no ceiling, seed, near-repeat cut or rule of symmetric pairs; at 5060 the chain's own proof
stands in for it.  The *smooth-part tree* decides the members of the smooth part one at a time, largest first, each
promoted or not, and a node lives while its GF(2) bound exceeds opt(n).  A *leaf* is a whole arrangement that lives.
Walking the whole tree and searching every leaf proves that nothing beats opt(n), and it is the plainest
arrangement-first proof.  A *depth cut* is the set of living nodes at one depth.

*Exclusion, price, trade.*  An *exclusion* is the search going on without one member of a conflict, and its *price* is
how much the node's bound falls when it does.  A *trade* is the exclusion whose substitute shares a cofactor with the
member: x = m·p leaves and y = m·q comes in, at a price near (p − q)·m, as 1292 = 68·19 for 1156 = 68·17 at 136.

### The work

Two studies ran on 2026-11-11, one after the other, on batmobile on 16 threads at idle priority.  The first
([core5060/](core5060/README.md), 10:45 to 13:45) asked whether a proof could list the arrangements of the small-prime
part.  The second ([trades/](trades/README.md), 13:49 to 14:55) asked what the first study's table meant, by comparing
fixed parts at the same gap, and whether the cheap trades could be counted.  Both used the example `restricted` of the
frame solver (the tool of [the loops study](../../the-loop-principle-and-game-5061-2026-11/README.md)'s E8 and E11,
which solves a restricted problem as an exact standalone search), with three subcommands of the first study
(`fix-smooth`, `smooth-tree`, `census`) and three options of the second (`--rough`, `--random`, `--complement`).  Every
search on a proven game returned its known optimum.

| study | what it did | games | runs |
|---|---|---|---|
| core5060 | fixed the small-prime part as in the optimal set, at B from 31 down to 7 | 5060 | 7 |
| | fixed wrong arrangements, estimated the smooth-part tree by Knuth's estimator, and walked it whole or by a sample | 1500, 2380, 5060 | 6 estimates (one at 1500, five at 5060), 4 walks |
| | counted the conflicts the search branches on, in its first 5 million steps | 5060 | 1 |
| trades | read the October test of the count of trades again | 3300-14, 3441-1262, 3441-5459 | none new |
| | fixed other parts of the candidates, and read each run's gap and steps | 2380, 5060 | 93 searches that finished (57 full runs and 36 scans of one step) |
| | searched the arrangements that the smooth-part tree's leaves hold | 5060 | 3 |

## Results

### The small-prime part fixed as in the optimal set: the rest is easy from B of 13 up

**Fixing the 13-smooth part as in the optimal set leaves a search that is fast down to B = 13 and explodes below.**
Each search had the score to beat opt(5060) − 1, and every one that finished found 8,053,621.

| B | smooth part | fixed | barred | free | gap | steps | CPU s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| none (the root) | 0 | 0 | 0 | 1,380 | 2,557 | 1,214,943,001 (the chain's proof) | 765,397 |
| 31 | 671 | 142 | 529 | 709 | 482 | 201 | 0.1 |
| 23 | 564 | 120 | 444 | 816 | 544 | 217 | 0.2 |
| 19 | 497 | 100 | 397 | 883 | 544 | 232 | 0.2 |
| 17 | 425 | 80 | 345 | 955 | 715 | 248 | 0.3 |
| 13 | 350 | 65 | 285 | 1,030 | 1,191 | 1,746 | 1.7 |
| 11 | 268 | 47 | 221 | 1,112 | 1,905 | 306,433 | 176 |
| 7 | 188 | 31 | 157 | 1,192 | 2,156 | stopped at 10,008,544 | 4,711 |

A wrong arrangement is refuted at once.  5059's optimal set fixed at B = 23 is refuted in 8 steps (gap 300) and at B =
13 in 458 steps (gap 766); 5060's set without 1575 has a bound 1,031 below opt at its root and takes 1 step; 5060's with
1701 for 1575 cannot be promoted at all; and the 797 leaves that Knuth's estimator reached at B = 13 and 17 had gaps of
1 to 95 and took 1 or 2 steps each.

### Listing the arrangements costs more than the search

**The arrangements whose bound exceeds opt are many, and walking the tree that finds them costs far more than the plain
search.**  At 1500 the whole tree was walked; at 2380 and 5060 it was estimated from a random sample of the nodes of a
depth cut, the depth cut's size over the sample's times what the sampled subtrees hold.

| game | plain search | the smooth-part tree at B = 13 | nodes | leaves | tree CPU s | against the plain search |
|---:|---|---|---:|---:|---:|---|
| 1500 | 7,088 steps, 1.5 CPU s | whole, largest first | 6,482,626 | 32,294 | 1,101 | 915 × the steps, 740 × the CPU |
| 1500 | | whole, smallest first | 6,096,186 | 32,294 | 817 | 860 ×, 550 × |
| 2380 | 16,915,916 steps, 3,683 CPU s | 140 of 400 sampled subtrees of a depth cut of at least 4,000 walked in 52 minutes, then stopped | | | at least 440,000 | at least 120 × the CPU |
| 5060 | the chain's 1,214,943,001 steps, 765,397 CPU s | 26 sampled subtrees of a depth cut of 6,751 begun in 1,700 s, 16 of them cut at the limit | at least 1.1·10⁹ | at least 2.4·10⁶ | at least 6.4·10⁶ | at least 0.9 × the steps, 8.4 × the CPU |

* **Every leaf is refuted in a few steps.**  At 1500 the 32,294 leaves' searches took 96,403 steps in all, at most 199
  for one, and 33 CPU seconds.  At 5060 every leaf searched took 1 or 2 steps.  The cost is all in the tree above them.
* **The order of the decisions hardly matters.**  Smallest first and largest first walk 6.1 and 6.5 million nodes at
  1500 with the same 32,294 leaves, as they must.
* **The subtrees are heavy-tailed, so estimates from samples run low.**  Knuth's estimator, 400 random paths, put the
  tree of 1500 at 2.3·10⁵ nodes and 1,400 leaves, 28 and 23 times too few, and one path held 95% of its leaf estimate.
  Two runs of it at 5060 gave 10^6.6 and 10^8.0 nodes.  A sample of 200 nodes of a depth cut of 4,622 came within 1.6
  times of the true count at 1500.  At 5060 the 10 subtrees that finished had a median of 20,000 nodes, while the 16 cut
  at the limit had passed 200,000 each and were still going, so the figures there are loose lower bounds.
* **The lower bounds are bounds on the estimates.**  By its 46th minute the 2380 run had spent 12.3 CPU hours, all on
  the sampled subtrees.  At 5060 a cut subtree counts only the nodes it walked.
* **Listing arrangements loses at every size measured, and loses by less in nodes as n grows.**  The ratio of its nodes
  to the plain search's steps falls from 915 at 1500 to at least 0.9 at 5060, a lower bound that the heavy tails make
  loose, so the true ratio there is likely several times larger.  In CPU the walk is at least 8.4 times the chain's
  proof at 5060, since a node of the walk costs 5.8 ms there and a step of the search 0.63 ms; at 1500 the two cost
  about the same, 0.17 and 0.21 ms.  The walk would have to be nine times cheaper a node and close to its lower bound to
  break even.

**The frame solver does not decide the small primes first, and should not.**  In its first 5 million steps at 5060, from
an incumbent worth opt − 1, 13-smooth numbers are 28% to 44% of the conflicts' members at every depth up to 220
promotions, where 99% of the conflicts are, and 25% of the root's candidates (350 of 1,380); 23-smooth numbers are 61%
of the members and 41% of the candidates.  The members branched on most include large primes: 2472 = 24·103 in 399,586
conflicts and 2512 = 16·157 in 259,178, then 1953, 1785, 1755 and 1782.  The conflicts have 17 members at the top of the
tree and 2 near the leaves, and each rules out every arrangement that holds it, so the search never meets most of the
32,294 living arrangements of 1500 one by one: its whole proof takes 7,088 steps.

### The count of trades does not track the tree

**A count of the combinations of trades that fit under the gap is 7 to 19 times the leaves, and spreads 1,000-fold from
path to path.**  [Local prime exchanges at the
nodes](../local-prime-exchanges-at-the-nodes-2026-10/README.md#4-ride-along-are-the-trees-the-count-of-fixed-prices) ran
the hypothesis's own test on 2026-10-18, on fresh traces of [the
anatomy's](../the-anatomy-of-a-hard-subtree-2026-10/README.md) three units: for 400 random leaves of each unit it
counted the combinations along the path that take one child at each node and whose costs add up to no more than the
unit's gap.  The trace was not made again.

| unit | gap | leaves | prices | count of a path, p10 | median | p90 | median count over the leaves |
|---|---:|---:|---|---:|---:|---:|---:|
| 3300-14 | 998 | 104,400 | fixed | 64,178 | 1,957,024 | 76,257,113 | 18.7 |
| | | | as met | 63,338 | 1,962,970 | 74,989,884 | 18.8 |
| 3441-1262 | 970 | 88,755 | fixed | 82,801 | 1,617,769 | 23,477,194 | 18.2 |
| 3441-5459 | 960 | 4,706 | fixed | 2,922 | 35,384 | 362,084 | 7.5 |

* **The prices are fixed, as the hypothesis says.**  The counts at fixed prices and at the prices met agree within 3% at
  the median and 10% at the deciles.
* **But the tree is not their product.**  An exclusion changes the bound's heaviest set, so the conflicts, and the
  trades on offer, below a node depend on the choices above it.
* **A count would be no proof anyway.**  The search closes a leaf when its bound falls below what a completion needs,
  and a method that skips leaves must show each of them closed, which takes a bound at the node that already sees the
  combined price of the trades below it: a stronger bound, not a count.

### Which numbers carry the gap does not matter, and how much gap there is does

**The first study read its table as the small primes' doing; at the same gap the small primes make no difference.**
With the 13-smooth part fixed, the rest of 5060 is proved in 1,746 steps at a gap of 1,191, while the October units
needed 10⁵ to 10⁶ steps at gaps near 1,000, but those are games 3300 and 3441, whose numbers and prices are smaller.
The fair control fixes other parts of 5060 itself and compares at the same gap.  `fix-smooth` gained `--rough`, which
fixes the large-prime part in place of the small-prime part, and `--random K`, which fixes only K members of a part,
drawn at random.

| part fixed at 5060 | free | gap | steps |
|---|---:|---:|---:|
| the 350 small-prime candidates (B = 13) | 1,030 | 1,191 | 1,802 |
| the 1,030 large-prime candidates, the small primes free | 350 | 1,281 | 1,842 |
| 350 candidates drawn at random, three draws | 1,030 | 1,516 to 1,714 | 18,098 to 74,532 |
| 350 large-prime candidates drawn at random | 1,030 | 2,008 | 1,980,177 |

With the small primes free and all their trades open, a gap of 1,281 is closed in 1,842 steps, as fast as the small
primes fixed close 1,191.  Fixing 350 other candidates leaves more gap, and the tree grows with that gap.  The median
steps of the finished searches, by band of gap:

| gap | 5060: small primes fixed | 5060: small primes free | 5060: drawn from all | 2380: small primes fixed | 2380: small primes free |
|---|---:|---:|---:|---:|---:|
| 600 to 799 | | | 76 (3) | 46,985 (2) | 2,950 (3) |
| 800 to 999 | | | 943 (2) | 481,426 (2) | 17,902 (4) |
| 1,000 to 1,199 | 1,802 (3) | | | | |
| 1,200 to 1,399 | 4,729 (1) | 5,903 (3) | | | |
| 1,400 to 1,599 | 14,873 (6) | 9,873 (7) | 18,868 (6) | | |
| 1,600 to 1,799 | 437,955 (2) | 31,007 (5) | 60,212 (2) | | |
| 1,800 to 1,999 | 175,923 (3) | 450,204 (2) | | | |

The runs are in parentheses.  *Small primes fixed* means some or all of the small-prime part (B = 7 to 17) fixed and
every other candidate free, and *small primes free* means some or all of the large-prime part (B = 11 to 23) fixed and
every small-prime candidate free.

* **At 5060 the gap decides, among problems fixed as in the optimal set.**  Over the 52 finished searches of gap 250 or
  more, log10(steps) = −0.11 + 0.00290 × gap, a decade per 345 points, with a residual sd of 0.39 decades.  The free
  candidates add a little (steps grow as their number to the power 1.0 ± 0.35).  Given both, fixing the small-prime part
  changes the steps by −0.14 ± 0.14 decades: nothing.  Over the 41 searches of gap 1,100 or more the slope on the gap
  alone is 0.00304, and given the gap and the free candidates fixing the small-prime part changes the steps by −0.10 ±
  0.15 decades.
* **At 2380 the small primes fixed make the tree larger.**  Over its 32 searches the same fit gives +0.71 ± 0.31 decades
  for fixing the small-prime part, five times the steps at the same gap and free count, with larger residuals (sd 0.50).
* **Fixing a few members as in the optimal set prunes no more than the gap they remove.**  At 2380 the whole search
  takes 16,915,916 steps at a gap of 1,137.  Fixing 10 random candidates leaves the gap at 1,137 in one draw, and the
  search takes 15,532,575 steps, 8% fewer.  The other small draws fall with their gaps: 1,097 to 1,107 take 5.9 to 7.6
  million steps, 1,063 take 2.7 to 4.0 million and 1,010 to 1,017 take 0.4 to 1.5 million.  Near the root the line is
  steep, a decade per about 90 points of gap.
* **The small primes carry more of the gap per member.**  Fixing 5060's 350 small-prime candidates removes 1,366 points,
  3.9 a member; 350 drawn from all remove 843 to 1,041; 350 drawn from the large-prime part remove 549, 1.6 a member.
  That, and not the trades among them, is why fixing them makes the rest easy.
* **The trade the first study cites is not among the small primes.**  1292 = 2²·17·19 and 1156 = 2²·17² both hold 17, so
  the fix at B = 13 leaves that trade free.  Of the eight trades the anatomy met most at 3300, six hold a prime above
  13, and the cheapest exchange large primes on small cofactors: 1572 = 12·131 for 1524 = 12·127 at 48.

### The bound's error splits by the largest prime, but is no fixed cost

At 5060 the gap left with the small-prime part fixed and the gap left with the large-prime part fixed add up nearly to
the root's, so the bound's error is nearly the sum of an error on each part.  A random split does not add up so:

| game | split | gap with one side fixed | with the other fixed | sum | root's gap |
|---:|---|---:|---:|---:|---:|
| 5060 | small primes at B = 13, the rest | 1,191 | 1,281 | 2,472 | 2,557 |
| 5060 | B = 11 | 1,905 | 542 | 2,447 | 2,557 |
| 5060 | B = 7 | 2,156 | 0 | 2,156 | 2,557 |
| 5060 | 350 or 400 at random, the rest (four draws) | 912 to 1,654 | 264 to 795 | 1,394 to 2,246 | 2,557 |
| 2380 | B = 13 | 271 | 566 | 837 | 1,137 |
| 2380 | B = 17 | 271 | 696 | 967 | 1,137 |
| 2380 | 150 or 200 at random, the rest (two draws) | 639 to 757 | 93 | 732 to 850 | 1,137 |

At 2380 the split by the largest prime adds up no better than a random one, so the near sum is a fact of 5060 and not
yet a rule.  If the large-prime part's error were the same whatever the small primes did, a proof could charge it once:
decide the small-prime part with the bound less 1,191, and the gap left to search would be about 1,281, not 2,557.  It
is not the same.  Random paths through the smooth-part tree of 5060 recorded arrangements whose bound exceeds opt(5060),
each setting 13 to 27 of its 350 members otherwise than the optimal set.  Under the first searched (leaf 294, 16 members
otherwise, a bound 3 points above opt) the search proves in 72,778 steps that no game scores within 3,000 of opt(5060),
so the large-prime part's error under that arrangement is more than 3,003 points, against 1,191 under the optimal
arrangement.  From opt − 8,000 that arrangement stopped at 300 seconds after 3,736,845 steps, and a second (leaf 352, 19
members otherwise, a bound 44 above opt) after 5,917,336, with no game found.

So a part's error depends on its context and is larger where the arrangement is wrong.  That is also why the first study
found wrong arrangements refuted in a step or two: there the exclusions are dear, and a gap of 3,003 takes 72,778 steps
where the line near the optimal arrangement would give about 4·10⁸.  The steps a point of gap costs depend on the
problem, and the problems near the optimal arrangement are the dear ones, whichever primes are free.

### The sound methods, and what each would need

| method | what makes it sound | what was measured | why it does not pay |
|---|---|---|---|
| a knapsack over prices: the bound less the cheapest set of exclusions that hits every known conflict | not the prices as they are, since the bound is a matroid intersection and two exclusions can cost less than the sum of their prices; the bound's weight split makes it sound, as each side is one matroid whose exclusion costs are supermodular, so a set of exclusions costs at least the sum of each member's split price | at exact prices, the cheapest members of the heaviest set's disjoint conflicts sum to a median 12% of a node's gap at 3940 to 4548 and 20% at 4875 ([where 4875 spends](../where-the-search-of-4875-spends-and-which-conflict-to-branch-on-2026-10/README.md)); the cover LP over all conflicts closes 46% of the root's gap at 851 to 1310, falling 3.8 points per 100 n, and makes trees 6.2 times smaller in more time ([how far nogoods can go](../how-far-can-nogoods-go-2026-10/README.md)) | a cut needs the charge to pass the node's slack, a few cheap conflicts never do that high in the tree, and the split prices are at most the exact ones |
| a memo of a core's resolution, reused across contexts | a nogood is a fact of the root and holds anywhere, and the search learns it already; a price is not, since it spreads 6 to 12% over contexts, so a memo must store a lower bound valid in the new context, which means pricing again; and a part's error is no constant either | learning each conflict's closure under the cheap trades takes 37 to 49% off three hard units and 4.5% off whole games ([cheap exchanges](../conflicts-closed-under-cheap-exchanges-2026-10/README.md)); no two of 3300-14's 512,966 nodes share their state | the cores repeat, but their contexts do not |
| exact accounting: many leaves made one case | a symmetry or a dominance between the leaves | local prime exchanges are symmetries of a node only where the root's symmetric pairs already are (119 of 152,088 swaps at 3300-14 otherwise), and 3 to 18% of the others are a dominance on samples ([local prime exchanges](../local-prime-exchanges-at-the-nodes-2026-10/README.md)); the knot of a conflict and its trade images lowers a node's bound by one trade, 66 to 78 points, and saves 0.6 to 3.6% of the steps ([what the learning leaves](../what-the-learning-leaves-in-the-hardest-searches-2026-10/README.md#the-knot-in-the-bound)) | under the big exclusions the bound's substitute is rarely an image of the conflict, so there is nothing to merge |

The knapsack's sound form is short to state.  The GF(2) bound V is the weight of the heaviest common independent set of
two matroids, and its weight split w = w_A + w_B makes that set heaviest in each matroid alone, so V = g_A(E) + g_B(E),
with g(X) the heaviest independent subset of X.  Removing a set T of candidates lowers g by d(T) = g(E) − g(E − T),
which is supermodular because g is submodular, and a supermodular d with d(∅) = 0 has d(T) ≥ Σ_{t ∈ T} d({t}).  A
completion F leaves out a set T that hits every known conflict, so w(F) ≤ g_A(E − T) + g_B(E − T) ≤ V − Σ_{t ∈ T}
(d_A(t) + d_B(t)): the node's bound may drop by the cheapest such sum.  The measurements at exact prices bound what it
could give.

## Limits

* **The fits are least squares on log10 of the steps**, with standard errors from the residuals, over the finished
  searches only.  Searches stopped at a limit are left out, which biases the slope down at the largest gaps.
* **The 2380 and 5060 fits disagree about the small primes** (+0.71 ± 0.31 decades at 2380, −0.14 ± 0.14 at 5060), so
  "nothing" is the 5060 result, and the 2380 residuals are larger (sd 0.50 against 0.39).
* **The walks at 2380 and 5060 are lower bounds.**  The subtrees are heavy-tailed, the 2380 walk was sized from 1500's
  and ran past its two-hour limit until it was stopped at 13:00, and a subtree cut at its limit counts only the nodes
  walked.
* **The near sum of the two errors is a fact of 5060**, which 2380 does not repeat.
* **The October test of the count was not repeated.**  It was run on 2026-10-18 on the three units and quoted here.
* **A 16-thread search's step count varies a few percent** from run to run (1,730 to 1,802 for the same problem), and
  seconds are wall time under load while other work ran at idle priority; CPU seconds are the engine's or the threads'.
* **The sound cuts are measured at exact prices or in October's entries**, not built, so each saving is a bound on what
  a cut could give and not a measurement of it.

## Decision

The solver is unchanged: the search follows conflicts priced by the bound, and the small-prime numbers come up in its
conflicts a little more often than among the candidates, at every depth.  Nothing of this entry is merged: the tool is
the example `restricted` on branches that were never pushed, kept here as patches.

* **The arrangement-first proof is dropped.**  It is 915 times the steps at 1500 and at least 8.4 times the CPU at 5060.
  If it is ever reopened, its deciding test is a 30-minute depth-cut sample at 4983, the chain's dearest proof at 1,094
  CPU-hours, after making its nodes cheaper (the walk's bound should stop at the need, as the search's does); it is dead
  if the sample's lower bound passes 4983's steps.
* **The avenue of counting trades is closed.**  The count is 7 to 19 times the leaves and spreads 1,000-fold, the
  small-prime trades add nothing at equal gap at 5060 and the opposite at 2380, and the sound pricing bounds are
  measured at 12 to 20% of a node's gap, one trade, or a constant factor at more CPU.
* **The fixed-part speed stays a tool.**  With the 13-smooth part of a best-known set fixed, the rest of a game the size
  of 5060 is solved exactly in seconds, which gives the best game with that small-prime arrangement or the proof that
  none exists without changing the small primes.  Its test, to run it over the best-known games 5061 to 5260 and count
  the improvements, was left for a later entry; the loops study's E11 found none at 5061 in a related region.
* **The split-price cut is the one sound method left, and it was not built.**  The search already computes each member's
  split price for its forced members, so the cut costs a few more peels a node to find disjoint conflicts.  It is
  expected to save a few percent of the steps, judging by the exact-price screen (12 to 20% of a node's gap) and the
  knot (0.6 to 3.6%), at a cost of a few days for the cut, its proof in the theory and its tests.
* **Any bound is to be judged by the gap it closes at the nodes that hold the tree.**  At 5060 the steps grow a decade
  per 345 points of gap, and near the root of 2380 a decade per about 90, and the prior pricing bounds close their
  points near the leaves, where the subtrees are a step or two.

What would reopen it:

* a screen of the split-price cut that comes out above 10%: at 200 sampled nodes of slack 300 or more in units of 4983
  and 5060, the share that the sum of split prices would cut; the cut is built only if that share is above 10%;
* a proof that one part's error is at least some L under every arrangement of the other: the error varies from 1,191 at
  the optimal arrangement to more than 3,003 at a wrong one, and if it is least at the optimal arrangement, L = 1,191
  would hold and the search left would face a gap near 1,281 instead of 2,557, but no construction proves such a bound
  without enumerating the arrangements, and it is theory before it is a build;
* a bound that closes gap at the nodes of slack 300 or more of a unit of 4983 or 5060, which is the test for any
  candidate before it goes into the search;
* a run of the fixed-part check over the best-known games 5061 to 5260 that improves some of them.

## Files

The work ran in the lab folders `lab/work/core5060/` and `lab/work/trades/`, whose files these are, with their paths as
they were there.  The scripts use the standard library only and are run with `python3 -I` or as shell scripts from their
folder.  Both READMEs are the studies' own reports, with these changes.  The links to the repository's files by their
lab paths (three in `core5060/README.md`, two in `trades/README.md`) now name the files at commit 287486e.  In
`core5060/README.md` the word "frontier", a retired word with another meaning there, is "depth cut" in seven places, and
in the comment of `core5060/run-walk.sh` the option's name is in backticks and "frontier" is "depth cut".  In
`trades/README.md` "cap" is "limit" once, and in the comment of `run-fix.sh` of each study "caps" is "limits".

* [core5060/](core5060/): [README.md](core5060/README.md), the first study's report.
  * `run-fix.sh` makes the fixed-part runs and the plain searches: `fix.jsonl`, `baseline.jsonl`, `fix-N.err`.
  * `run-tree.sh` runs Knuth's estimator: `tree-N-B-sS.jsonl`.
  * `run-walk.sh` runs the walks: `walk.jsonl`, with the lines of the sampled subtrees in `walk-5060-13--.err`;
    `walk-2380-13-stopped.err` holds the progress lines of the 2380 walk, whose last line was lost when it was stopped.
  * `census-5060-5M.jsonl`: the branching census of the first 5 million steps of 5060.
  * `summarize_tree.py`, `summarize_walk.py` and `summarize_census.py` make the tables.
* [trades/](trades/): [README.md](trades/README.md), the second study's report.
  * `run-fix.sh` runs the controls, one argument a run (`N:B:PART[:K[:SEED[:c]]]`), into `fix.jsonl`, with the engine's
    lines in `fix-N.err`; `scan-gaps.sh` runs the same with a limit of one step into `scan.jsonl`, to read the gaps.
  * `summarize_fix.py` makes the tables of the gaps and the fits: `python3 -I summarize_fix.py fix.jsonl scan.jsonl
    --bands --pairs --fit [--min-gap G]`; `analysis.txt` is its output (every run, the bands, the splits, the fits over
    gaps of 250 and of 1,100 or more with each run's residual) and the arrangements'.
  * `run-arrangements.py` searches the arrangements, from the leaves of `../core5060/tree-5060-13-s2.jsonl`, into
    `arrangements-below3000.jsonl` (finished) and `arrangements.jsonl` (two, stopped at 300 seconds), with the engine's
    lines in `arrangements.err`; `summarize_arrangements.py` makes their table.
* [patches/](patches/): the code of the two studies as `git am` patches (see Commits).

Not copied: the binary `restricted` of each study (93 MB, built from the patches), the empty `.err` files of the tree
runs, and the October numbers, which are quoted from the notebook's entries.

## Commits

The branches `loops-core` and `trades` of the research repository were never pushed, so `git show` may not find their
commits.  The patches were made with `git format-patch`, and apply in order with `git am` on the code they were made on.
`loops-core` was made from `loops-e6` at df9b660, so its two patches apply after the 14 patches of `loops-e6` in [the
loops study's entry](../../the-loop-principle-and-game-5061-2026-11/README.md#commits) on master 79faea3.  The branch
`trades` is master 287486e with `loops-core` merged in (ccf3714) and two more commits, so its patches apply after those
16 patches on master 287486e.  Each series was applied to a clone with `git am`, and rebuilt the tree of its branch's
commit (58222ed for `loops-core` and the tip of `trades`).  Later commits of `loops-core` belong to a later entry and
are not here.

* [patches/loops-core/](patches/loops-core/), the first study (12:32 to 12:53):
  * 5752398: the subcommands `fix-smooth`, `smooth-tree` and `census` of the example `restricted`, and a score to beat
    for every search (`--above S`), so that a search starts from an incumbent worth S that holds no set, and `window`
    shares its split of the candidates with `fix-smooth`.  1 file, 683 lines added and 19 removed.
  * 58222ed: the time limits of the searches and walks (`smooth-tree --exact` stops its walk at `--time-limit`), and a
    JSON line on stderr for each subtree walked.  1 file, 64 lines added and 24 removed.
* [patches/trades/](patches/trades/), the second study (14:08 to 14:24):
  * e27fb6f: `fix-smooth --rough` (the candidates outside the smooth part) and `--random K` with `--seed R` (only K
    candidates of the part, drawn at random).  1 file, 44 lines added and 10 removed.
  * f434dd6: `--complement`, with `--random K`, the part's members not drawn in place of the K drawn.  1 file, 15 lines
    added and 6 removed.

The commit that adds this entry also adds its rows to the register's files of [the start and the
wall](../../register/start-and-wall.md) and [the stronger bounds](../../register/stronger-bounds.md).
