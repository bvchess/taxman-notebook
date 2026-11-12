# Can a proof count the cheap trades instead of searching them?  (trades)

Started 2026-11-11 13:49 PST.  Concluded 2026-11-11 14:55 PST.

## The idea, and the answer

**The idea.**  A hard search pays the bound's gap a little at a time.  When the search leaves a member of a conflict
out, its bound falls only a little, because a near-equal number steps in, often the member with one prime traded for a
smaller one: 1292 = 68·19 gives way to 1156 = 68·17, and the bound falls by 136.  These prices are nearly fixed.  If the
tree were just every combination of such trades whose prices fit under the gap, a proof could count or price the
combinations instead of visiting them.  Today's study of 5060 seemed to point the same way: with the small-prime
candidates fixed as in the optimal set, the rest of the proof is easy.

**The answer: no.**

* **The count does not track the tree.**  The test that the October study proposed was run on 2026-10-18.  It counted,
  along each of 400 random leaves' paths, the combinations of trades whose prices fit the gap.  At unit 3300-14 the
  median count is 1,957,024 against the tree's 104,400 leaves, and the count spreads 1,000-fold from path to path.
  What a node can trade depends on what was traded above it.
* **Which numbers carry the gap does not matter; how much gap there is does.**  At game 5060, 52 searches with
  different parts of the candidates fixed as in the optimal set follow one line, within a factor of 2.5: a decade of
  steps per 345 points of gap.  At the same gap, fixing the small-prime part makes the tree no smaller than fixing
  other numbers does (−0.14 ± 0.14 decades).  At game 2380, fixing the small-prime part makes the tree larger
  (+0.71 ± 0.31 decades).  The small primes matter only because they carry more of the gap: fixing 5060's 350
  small-prime candidates removes 1,366 of its 2,557 points, while 350 drawn at random remove 843 to 1,041, and 350
  large-prime ones 549.
* **The ways to charge trades soundly are measured, or bounded by measurements, and none is worth more than a
  constant factor.**  Charging the cheapest member of each disjoint conflict covers 12-20% of a node's gap even at
  exact prices, which are not sound to add.  A conflict with its trade images lowers a node's bound by about one trade.
  All conflicts together, in an LP, close 46% of the root's gap at games 851-1310, a share that falls with n.

So a proof gets cheaper only by closing gap at the nodes, wherever the gap lies.  Counting trades does not do that.  The
one new structural fact is narrow.  At 5060 the bound's error splits almost exactly into an error on the small-prime
part and an error on the rest, but the second error is no fixed cost: under a wrong arrangement of the small primes it
is more than 2.5 times larger.

## Terms

The glossary ([docs/GLOSSARY.md](https://github.com/bvchess/taxman/blob/287486e/docs/GLOSSARY.md)) defines a *candidate* (a number the search may
promote), a *promotion set*, a *conflict* (candidates that cannot all be promoted from a node, so that every completion
leaves one out), opt(n) and a search *step*.  The words of this study:

* **The GF(2) bound** bounds the best score below every node of the frame solver's search
  ([solver/docs/design/gf2-bound.md](https://github.com/bvchess/taxman/blob/287486e/solver/docs/design/gf2-bound.md)).  Its **gap** at a problem's
  root is how far it lies above opt(n), in points of score.
* **An exclusion** is the search going on without one member of a conflict.  Its **price** is how much the node's
  bound falls when it does ([the anatomy of a hard
  subtree](https://github.com/bvchess/taxman-notebook/blob/main/search/the-anatomy-of-a-hard-subtree-2026-10/README.md)).
* **A trade** is the exclusion whose substitute shares a cofactor with the member: x = m·p leaves and y = m·q comes in,
  at a price near (p − q)·m.  1292 = 68·19 for 1156 = 68·17 is a trade at 136.
* **The small-prime part at B** is the set of candidates whose primes are all at most B: at 5060 and B = 13, 350 of the
  1,380 candidates, such as 1560 = 2³·3·5·13.  The [study of 5060](../core5060/README.md) calls it the smooth part.
  The **large-prime part** is the other candidates, each with some prime above B, such as 1292 = 2²·17·19.
* **Fixing a part** promotes the members of the part that the committed optimal set holds and bars the others.  The
  candidates outside the part stay free.  The search then starts from a score to beat of opt(n) − 1, so it must find a
  game worth opt(n) and prove that none scores more.  Every such search here returned opt(n).

## 1. The count does not track the tree

The October study's first hypothesis was that a hard tree is the number of combinations of fixed-price exclusions
that fit under its gap.  [Local prime exchanges at the
nodes](https://github.com/bvchess/taxman-notebook/blob/main/search/local-prime-exchanges-at-the-nodes-2026-10/README.md#4-ride-along-are-the-trees-the-count-of-fixed-prices)
ran the hypothesis's own test on 2026-10-18, on fresh traces of the anatomy's three units.  A node's *menu* is what
reaching each of its children costs.  For 400 random leaves of each unit, the test counted the combinations along the
leaf's path that take one child at each node and whose costs add up to no more than the unit's gap.  It counted them at
fixed prices (each pair of conflict and member at its median over the tree) and at the prices met:

| unit | gap | leaves | prices | count of a path, p10 | median | p90 | median count over the leaves |
|---|---:|---:|---|---:|---:|---:|---:|
| 3300-14 | 998 | 104,400 | fixed | 64,178 | 1,957,024 | 76,257,113 | 18.7 |
| | | | as met | 63,338 | 1,962,970 | 74,989,884 | 18.8 |
| 3441-1262 | 970 | 88,755 | fixed | 82,801 | 1,617,769 | 23,477,194 | 18.2 |
| 3441-5459 | 960 | 4,706 | fixed | 2,922 | 35,384 | 362,084 | 7.5 |

* **The prices are fixed, as the hypothesis says.**  The counts at fixed prices and at the prices met agree within 3%
  at the median and 10% at the deciles.
* **But the tree is not their product.**  A path's count is 7 to 19 times the leaves at the median, and it spreads two
  to three decades from path to path.  An exclusion changes the bound's heaviest set, so the conflicts, and the trades
  on offer, below a node depend on the choices above it.
* **A count would be no proof anyway.**  The search closes a leaf when its bound falls below what a completion needs.
  A method that skips leaves must show each of them closed, which takes a bound at the node that already sees the
  combined price of the trades below it: a stronger bound, not a count.

The trace was not made again, since the test was already done on the same units and with the same tool.

## 2. Which numbers carry the gap does not matter

The study of 5060 read its result as the small primes' doing.  With the 13-smooth part fixed, the rest of 5060 is
proved in 1,746 steps at a gap of 1,191, while the October units needed 10⁵ to 10⁶ steps at gaps near 1,000.  Those
units are of games 3300 and 3441, though, whose numbers, and so whose prices (about a tenth of a member's value), are
smaller.  The fair control fixes other parts of 5060 itself and compares at the same gap.  `fix-smooth` gained two
options for it: `--rough` fixes the large-prime part instead of the small-prime part, and `--random K` fixes only K
members of the part, drawn at random.

**The same number of free candidates, different parts fixed** (5060, 1,030 candidates free in each but the second):

| part fixed | free | gap | steps |
|---|---:|---:|---:|
| the 350 small-prime candidates (B = 13) | 1,030 | 1,191 | 1,802 |
| the 1,030 large-prime candidates, the small primes free | 350 | 1,281 | 1,842 |
| 350 candidates drawn at random, three draws | 1,030 | 1,516-1,714 | 18,098-74,532 |
| 350 large-prime candidates drawn at random | 1,030 | 2,008 | 1,980,177 |

With the small primes free and all their trades open, a gap of 1,281 is closed in 1,842 steps, as fast as the small
primes fixed close 1,191.  Fixing 350 other candidates leaves more gap, and the tree grows with that gap.

**Steps by gap, over all the runs** (the median steps of the finished searches, the runs in parentheses):

| gap | 5060: small primes fixed | 5060: small primes free | 5060: drawn from all | 2380: small primes fixed | 2380: small primes free |
|---|---:|---:|---:|---:|---:|
| 600-799 | | | 76 (3) | 46,985 (2) | 2,950 (3) |
| 800-999 | | | 943 (2) | 481,426 (2) | 17,902 (4) |
| 1,000-1,199 | 1,802 (3) | | | | |
| 1,200-1,399 | 4,729 (1) | 5,903 (3) | | | |
| 1,400-1,599 | 14,873 (6) | 9,873 (7) | 18,868 (6) | | |
| 1,600-1,799 | 437,955 (2) | 31,007 (5) | 60,212 (2) | | |
| 1,800-1,999 | 175,923 (3) | 450,204 (2) | | | |

*Small primes fixed* means some or all of the small-prime part (B = 7 to 17) fixed and every other candidate free;
*small primes free* means some or all of the large-prime part (B = 11 to 23) fixed and every small-prime candidate
free.

* **At 5060 the gap decides, among problems fixed as in the optimal set.**  Over the 52 finished searches of gap 250
  or more, log10(steps) = −0.11 + 0.00290 × gap, a decade per 345 points, with a residual sd of 0.39 decades.  The
  free candidates add a little (steps grow as their number to the power 1.0 ± 0.35).  Given both, fixing the
  small-prime part changes the steps by −0.14 ± 0.14 decades: nothing.
* **At 2380 the small primes fixed make the tree larger.**  Over its 32 searches the same fit gives +0.71 ± 0.31
  decades for fixing the small-prime part, five times the steps at the same gap and free count.  The residuals are
  larger there (sd 0.50).
* **Fixing a few members at the optimum prunes no more than the gap they remove.**  At 2380 the whole search takes
  16,915,916 steps at a gap of 1,137.  Fixing 10 random candidates leaves the gap at 1,137 in one draw, and the search
  takes 15,532,575 steps, 8% fewer.  The other small draws fall with their gaps: 1,097-1,107 take 5.9-7.6 million
  steps, 1,063 take 2.7-4.0 million and 1,010-1,017 take 0.4-1.5 million.  Near the root the line is steep, a decade
  per about 90 points of gap.
* **The small primes carry more of the gap per member.**  Fixing 5060's 350 small-prime candidates removes 1,366 points,
  3.9 a member; 350 drawn from all remove 843-1,041; 350 drawn from the large-prime part remove 549, 1.6 a member.
  That, not the trades among them, is why fixing them makes the rest easy.
* **The trade the study of 5060 cites is not among the small primes.**  1292 = 2²·17·19 and 1156 = 2²·17² both hold 17,
  so the fix at B = 13 leaves that trade free.  Of the eight trades the anatomy met most at 3300, six hold a prime above
  13, and the cheapest exchange large primes on small cofactors: 1572 = 12·131 for 1524 = 12·127 at 48.

## 3. The bound's error splits by the largest prime, but is no fixed cost

At 5060 the gap left with the small-prime part fixed and the gap left with the large-prime part fixed add up nearly to
the root's.  So the bound's error is nearly the sum of an error on each part.  A random split does not add up so:

| game | split | gap with one side fixed | with the other fixed | sum | root's gap |
|---:|---|---:|---:|---:|---:|
| 5060 | small primes at B = 13, the rest | 1,191 | 1,281 | 2,472 | 2,557 |
| 5060 | B = 11 | 1,905 | 542 | 2,447 | 2,557 |
| 5060 | B = 7 | 2,156 | 0 | 2,156 | 2,557 |
| 5060 | 350 or 400 at random, the rest (four draws) | 912-1,654 | 264-795 | 1,394-2,246 | 2,557 |
| 2380 | B = 13 | 271 | 566 | 837 | 1,137 |
| 2380 | B = 17 | 271 | 696 | 967 | 1,137 |
| 2380 | 150 or 200 at random, the rest (two draws) | 639-757 | 93 | 732-850 | 1,137 |

At 2380 the split by the largest prime adds up no better than a random one, so the near sum is a fact of 5060, not yet
a rule.

If the large-prime part's error were the same whatever the small primes did, a proof could charge it once: decide the
small-prime part with the bound less 1,191, and the gap left to search would be about 1,281, not 2,557.  It is not the
same.  The study of 5060's random paths through its tree over the 13-smooth part recorded arrangements of it whose
bound exceeds opt(5060), each setting 13 to 27 of its 350 members otherwise than the optimal set.  Under one of them,
with a bound 3 points above opt(5060), the search proves in 72,778 steps that no game scores within 3,000 of
opt(5060).  The large-prime part's error under that arrangement is more than 3,003 points, against 1,191 under the
optimal arrangement.  Under a second, no game within 8,000 of opt turned up in 5,917,336 steps (stopped at 300
seconds).

So a part's error depends on its context, and is larger where the arrangement is wrong.  That is also why the study of
5060 found wrong arrangements refuted in a step or two: there the exclusions are dear, and a gap of 3,003 takes 72,778
steps where the line of section 2, fitted near the optimal arrangement, would give about 4·10⁸.  The steps a point of
gap costs depend on the problem, then, and the problems near the optimum are the dear ones, whichever primes are free.

## 4. The sound methods, and what each would need

| method | what makes it sound | what was measured | why it does not pay |
|---|---|---|---|
| A knapsack over prices: the bound less the cheapest set of exclusions that hits every known conflict | Not the prices as they are: the bound is a matroid intersection, and two exclusions can cost less than the sum of their prices.  The bound's weight split makes it sound: each side is one matroid, whose exclusion costs are supermodular, so a set of exclusions costs at least the sum of each member's split price, the price that forced members already use | With exact prices, the cheapest members of the heaviest set's disjoint conflicts sum to a median 12% of a node's gap at 3940-4548 and 20% at 4875 ([where 4875 spends](https://github.com/bvchess/taxman-notebook/blob/main/search/where-the-search-of-4875-spends-and-which-conflict-to-branch-on-2026-10/README.md)); the cover LP over all conflicts closes 46% of the root's gap at 851-1310, falling 3.8 points per 100 n, and makes trees 6.2 times smaller in more time ([how far nogoods can go](https://github.com/bvchess/taxman-notebook/blob/main/search/how-far-can-nogoods-go-2026-10/README.md)) | A cut needs the charge to pass the node's slack.  A few cheap conflicts never do that high in the tree, and the split prices are at most the exact ones |
| A memo of a core's resolution, reused across contexts | A nogood is a fact of the root and holds anywhere, and the search learns it already.  A price is not: it spreads 6-12% over contexts, so a memo must store a lower bound valid in the new context, which means pricing again (the tactic `price_reuse` carries prices only where that is proved).  A part's error is no constant either (section 3) | Learning each conflict's closure under the cheap trades takes 37-49% off three hard units and 4.5% off whole games ([cheap exchanges](https://github.com/bvchess/taxman-notebook/blob/main/search/conflicts-closed-under-cheap-exchanges-2026-10/README.md)); no two of 3300-14's 512,966 nodes share their state, so no subtree can be reused | The cores repeat, but their contexts do not |
| Exact accounting: many leaves made one case | A symmetry or a dominance between the leaves | Local prime exchanges are symmetries of a node only where the root's symmetric pairs already are (119 of 152,088 swaps at 3300-14 otherwise); 3-18% of the others are a dominance on samples ([local prime exchanges](https://github.com/bvchess/taxman-notebook/blob/main/search/local-prime-exchanges-at-the-nodes-2026-10/README.md)); the knot of a conflict and its trade images lowers a node's bound by one trade, 66-78 points, and saves 0.6-3.6% of the steps ([what the learning leaves](https://github.com/bvchess/taxman-notebook/blob/main/search/what-the-learning-leaves-in-the-hardest-searches-2026-10/README.md#the-knot-in-the-bound)) | Under the big exclusions the bound's substitute is rarely an image of the conflict, so there is nothing to merge |

The knapsack's sound form is short to state.  The GF(2) bound V is the weight of the heaviest common independent set of
two matroids (the limit on its size is a truncation of one of them, still a matroid), and its weight split w = w_A + w_B
makes that set heaviest in each matroid alone, so V = g_A(E) + g_B(E), with g(X) the heaviest independent subset of X.
Removing a set T of candidates lowers g by d(T) = g(E) − g(E − T), which is supermodular because g is submodular, and a
supermodular d with d(∅) = 0 has d(T) ≥ Σ_{t ∈ T} d({t}).  A completion F leaves out a set T that hits every known
conflict, so w(F) ≤ g_A(E − T) + g_B(E − T) ≤ V − Σ_{t ∈ T} (d_A(t) + d_B(t)): the node's bound may drop by the
cheapest such sum.  The measurements above, at exact prices, bound what it could give.

## Recommendations

1. **Close the avenue of counting trades.**  Gain: none expected.  Evidence: the count is 7-19 times the
   leaves and spreads 1,000-fold (section 1); the small-prime trades add nothing at equal gap at 5060, and the opposite
   at 2380 (section 2); the sound pricing bounds are measured at 12-20% of a node's gap, one trade, or a constant factor
   at more CPU (section 4).  Cost: none.
2. **If a pricing bound is tried at all, try the split-price cut of section 4, and screen it first.**  It is the most
   promising sound method here: the search already computes each member's split price for its forced members, so the
   cut costs a few more peels a node to find disjoint conflicts.  Gain: a few percent of the steps, judging by the
   exact-price screen (12-20% of a node's gap) and the knot (0.6-3.6%).  Cost: a few days for the cut, its proof in
   the theory and its tests.  Deciding test, before building: at 200 sampled nodes of slack 300 or more in units of
   4983 and 5060, the share that the sum of split prices would cut; build it only if that share is above 10%.
3. **Read the study of 5060's third recommendation as answered.**  Its small-prime fix is a reduction of the gap, at the
   same steps per point as any other.  Its second recommendation, the fixed-part check on best-known games past the
   chain, stands, and section 3 adds a variant: alternate the fixes, solving the small-prime part with the rest fixed,
   then the rest with the small-prime part fixed, each exact in seconds at 5060.  It is a finder, not a proof.  Test:
   run it on the best-known games 5061-5260 and count the improvements.
4. **Judge any bound by the gap it closes at the nodes that hold the tree.**  At 5060 the steps grow a decade per 345
   points of gap, and near the root of 2380 a decade per about 90.  The prior pricing bounds close their points near
   the leaves, where the subtrees are a step or two, so they save little.  Test for any candidate bound, before it is
   built into the search: sample nodes of slack 300 or more in a unit of 4983 or 5060, and measure how often it cuts
   them.
5. **A decomposition by largest prime would need a proof that one part's error is at least some L under every
   arrangement of the other.**  Section 3 shows the error varies, from 1,191 at the optimal arrangement to more than
   3,003 at a wrong one.  If it is least at the optimal arrangement, L = 1,191 would hold, and the search left would
   face a gap near 1,281 instead of 2,557; but no construction is known that proves such a bound without enumerating
   the arrangements.  It is the one open structural question here, and it is theory before it is a build.

## Checks

* **Every search on a proven game returned its known optimum.**  All 93 searches with a part fixed that finished (57
  full runs, and 36 scans that finished within their limit of steps) found opt(n), as their score to beat of
  opt(n) − 1 requires.
* **The control reproduces the study of 5060.**  The 13-smooth fix takes 1,802 steps here against 1,746 there, on 16
  threads each; the gaps agree, 1,191.
* **The trees are the search's own.**  The tool is the study of 5060's `restricted`, whose checks are in its README;
  the new options only choose which candidates are fixed.  A 16-thread search's step count varies a few percent from
  run to run (1,730 to 1,802 for the same problem).
* **The fits are least squares** on log10 of the steps, with standard errors from the residuals, over the finished
  searches only.  Searches stopped at a limit are left out, which biases the slope down at the largest gaps.

## Files

* `restricted`: the binary (see Provenance).  `fix-smooth N --smooth B [--rough] [--random K [--seed R]
  [--complement]]` fixes a part; `--complement` fixes the members of the part not drawn.
* `run-fix.sh` runs the controls, one argument a run (`N:B:PART[:K[:SEED[:c]]]`), into `fix.jsonl`, with the engine's
  lines in `fix-N.err`.  `scan-gaps.sh` runs the same with a limit of one step into `scan.jsonl`, to read the gaps.
* `summarize_fix.py` makes the tables of sections 2 and 3: `python3 -I summarize_fix.py fix.jsonl scan.jsonl --bands
  --pairs --fit [--min-gap G]`.
* `run-arrangements.py` searches the arrangements of section 3, from the leaves of
  `../core5060/tree-5060-13-s2.jsonl`, into `arrangements-below3000.jsonl` (the first, finished) and
  `arrangements.jsonl` (two, stopped at 300 seconds), with the engine's lines in `arrangements.err`;
  `summarize_arrangements.py` makes their table.
* `analysis.txt` is the output of both scripts: every run, the bands, the splits, the fits over gaps of 250 and of
  1,100 or more with each run's residual, and the arrangements.

## Provenance

Run on batmobile on 2026-11-11 between 14:08 and 14:47 PST, from the branch `trades` of the research repository, which
is never pushed: master at 287486e with the branch `loops-core` (58222ed, the study of 5060's tool) merged in, then
e27fb6f (`--rough`, `--random`) and f434dd6 (`--complement`).  The lines of `fix.jsonl` and `scan.jsonl` without the
field `complement` came from the build of e27fb6f, the others and the arrangements from that of f434dd6, the binary
here; the two search alike.  Every run was at `chrt -i 0 nice -n 19` on 16 threads, one
run at a time, while the machine ran other work at idle priority, so seconds are wall time under load; CPU seconds are
the engine's.  The controls took 2.8 CPU hours and the arrangements about 3.  The October numbers are quoted from the
notebook's entries, whose data and scripts are there.
