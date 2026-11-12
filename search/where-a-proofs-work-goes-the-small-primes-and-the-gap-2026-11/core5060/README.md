# Is a proof's work in its small primes?  (core5060)

Started 2026-11-11 10:45 PST.  Concluded 2026-11-11 13:45 PST.

## The idea, and the answer

**The idea.**  The loops study's E11 found that game 5061 is solved in seconds once the candidates made only of small
primes are fixed as in the proven optimal set of 5060.  If nearly all of a proof's work goes into arranging those
small-prime numbers, a proof could list their arrangements, bound each one, and solve the rest exactly.  It might cost
far less than the 213 CPU hours that proved 5060.

**The answer: half of the idea holds, and the method it suggests does not pay.**

* **Once the small-prime part is fixed, the rest is easy.**  With every candidate whose primes are all at most 13 fixed
  as in the optimal set of 5060, the search proves opt(5060) in 1,746 steps (1.7 CPU seconds).  The whole proof took
  1.2 billion steps.  The time explodes only below B = 13: 306,433 steps at B = 11, more than 10 million at B = 7.
* **A wrong arrangement is refuted at once.**  A changed arrangement falls below opt at its root's bound, cannot be
  promoted at all, or is refuted in 1 to a few hundred steps.
* **But there are far too many arrangements.**  At game 1500, 32,294 arrangements of the 13-smooth part have a bound
  above opt, while the whole proof of 1500 takes 7,088 steps.  Listing the arrangements takes 915 times the plain
  search's steps at 1500, at least 120 times its CPU at 2380, and at least 8 times the chain's CPU at 5060.
* **The frame solver does not decide the small primes first, and should not.**  Small-prime numbers make up its
  conflicts all along its paths, a little more often than they occur among the candidates.  A conflict of a few
  members refutes every arrangement that holds them, so the search refutes arrangements in bulk, where a list pays for
  each one.

## Terms

The glossary ([docs/GLOSSARY.md](https://github.com/bvchess/taxman/blob/287486e/docs/GLOSSARY.md)) defines the game, a *candidate* (a number the
search may promote), a *promotion set*, *opt(n)* and a search *step*.  The words of this study:

* **The GF(2) bound** is the frame solver's bound on every node of its search: an upper bound on the best score of the
  games below the node ([solver/docs/design/gf2-bound.md](https://github.com/bvchess/taxman/blob/287486e/solver/docs/design/gf2-bound.md)).  A
  bound's **gap** is how far it lies above opt(n), in points of score.
* **The smooth part at B** is the set of candidates of game n's root whose primes are all at most B: at 5060 and B = 13,
  350 of the 1,380 candidates, such as 1560 = 2³·3·5·13.  The brief called it the core; the glossary already uses
  "core" for a notion of playability, so this study does not.
* **An arrangement** of the smooth part says which of its members are promoted.  **Fixing** an arrangement promotes its
  members at the root and bars the rest of the smooth part; every other candidate stays free.  The **optimal
  arrangement** is the committed optimal set's.
* **The plain search** is the frame solver's search of the whole game, started from an incumbent worth opt(n), with no
  ceiling, seed, near-repeat cut or rule of symmetric pairs.  It is the baseline that an arrangement-first proof must
  beat.  At 5060 the chain's own proof stands in for it.
* **The smooth-part tree** decides the members of the smooth part one at a time, largest first, each promoted or not.
  A node lives while its GF(2) bound exceeds opt(n).  A **leaf** is a whole arrangement that lives.  Walking the whole
  tree and searching every leaf proves that nothing beats opt(n): every promotion set holds some arrangement, and the
  tree drops a node only when its bound rules out everything below it.  It is the plainest arrangement-first proof.

## 1. Fixed at the optimum: easy from B = 13 up

Fixing the smooth part as in the optimal set of 5060 leaves a search that is fast down to B = 13 and explodes below.
Each search had the score to beat opt(5060) − 1, so it had to find a game worth opt(5060), and every one that finished
found 8,053,621.

| B | smooth part | fixed | barred | free | gap of the bound | steps | CPU s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| none (the root) | 0 | 0 | 0 | 1,380 | 2,557 | 1,214,943,001 (the chain's proof) | 765,397 |
| 31 | 671 | 142 | 529 | 709 | 482 | 201 | 0.1 |
| 23 | 564 | 120 | 444 | 816 | 544 | 217 | 0.2 |
| 19 | 497 | 100 | 397 | 883 | 544 | 232 | 0.2 |
| 17 | 425 | 80 | 345 | 955 | 715 | 248 | 0.3 |
| 13 | 350 | 65 | 285 | 1,030 | 1,191 | 1,746 | 1.7 |
| 11 | 268 | 47 | 221 | 1,112 | 1,905 | 306,433 | 176 |
| 7 | 188 | 31 | 157 | 1,192 | 2,156 | stopped at 10,008,544 | 4,711 |

The small gap is not what makes the rest easy; the missing substitutes are.  At B = 13 the search closes a gap of 1,191
in 1,746 steps, where the units of [the anatomy of a hard
subtree](https://github.com/bvchess/taxman-notebook/blob/main/search/the-anatomy-of-a-hard-subtree-2026-10/README.md)
needed 10⁵ to 10⁶ steps for gaps near 1,000.  That entry found the proof paying its gap in exclusions that cost the
bound only a tenth of a member's value.  The bound can leave a member out cheaply because a near-equal substitute of the
same home steps in, often a twin with one prime exchanged: 1292 = 2²·17·19 gives way to 1156 = 2²·17².  Fixing the
small-prime numbers takes those cheap substitutes away.

## 2. Wrong arrangements: refuted at once

A wrong arrangement of the smooth part is refuted in a handful of steps, often by the bound at its root.  Each search
here had the score to beat opt(5060), so it proves that no game with the arrangement scores more.

| arrangement fixed | B | gap of the bound | steps | CPU s |
|---|---:|---:|---:|---:|
| 5059's optimal set | 23 | 300 | 8 | 0.02 |
| 5059's optimal set | 13 | 766 | 458 | 0.5 |
| 5060's without 1575 | 23 | −1,031 | 1 | 0.02 |
| 5060's with 1701 for 1575 | 23 | (cannot be promoted) | 0 | 0 |
| the 797 leaves reached by Knuth's estimator (section 3) | 13, 17 | 1 to 95 | 1 or 2 | 0.02 |

## 3. Counting the arrangements: far too many

The arrangements whose bound exceeds opt are many, and walking the tree that finds them costs far more than the plain
search.  At 2380 and 5060 the tree was estimated from a random sample of the nodes of a *depth cut*, the living nodes at
one depth: the depth cut's size over the sample's times what the sampled subtrees hold.

| game | plain search | the smooth-part tree at B = 13 | nodes | leaves | tree CPU s | against the plain search |
|---:|---|---|---:|---:|---:|---|
| 1500 | 7,088 steps, 1.5 CPU s | whole, largest first | 6,482,626 | 32,294 | 1,101 | 915 × the steps, 740 × the CPU |
| 1500 | | whole, smallest first | 6,096,186 | 32,294 | 817 | 860 ×, 550 × |
| 2380 | 16,915,916 steps, 3,683 CPU s | 140 of 400 sampled subtrees of a depth cut of at least 4,000 walked in 52 minutes, then stopped | | | at least 440,000 | at least 120 × the CPU |
| 5060 | the chain's 1,214,943,001 steps, 765,397 CPU s | 26 sampled subtrees of a depth cut of 6,751 begun in 1,700 s, 16 of them cut at the limit | at least 1.1·10⁹ | at least 2.4·10⁶ | at least 6.4·10⁶ | at least 0.9 × the steps, 8.4 × the CPU |

* **Every leaf is refuted in a few steps.**  At 1500 the 32,294 leaves' searches took 96,403 steps in all, at most 199
  for one, and 33 CPU seconds.  At 5060 every leaf searched took 1 or 2 steps.  The cost is all in the tree above them.
* **The order of the decisions hardly matters.**  Smallest first and largest first walk 6.1 and 6.5 million nodes at
  1500, with the same 32,294 leaves, as they must: whether an arrangement lives does not depend on the order.
* **The subtrees are heavy-tailed, so estimates from samples run low.**  Knuth's estimator, 400 random paths, put the
  tree of 1500 at 2.3·10⁵ nodes and 1,400 leaves, 28 and 23 times too few; one path held 95% of its leaf estimate.
  Two runs of it at 5060 gave 10^6.6 and 10^8.0 nodes.  A sample of 200 nodes of a depth cut of 4,622 came within 1.6
  times of the true count at 1500.  At 5060 the 10 subtrees that finished had a median of 20,000 nodes, while the 16
  cut at the limit had passed 200,000 each and were still going, so the figures there are loose lower bounds.
* **The lower bounds are bounds on the estimates.**  By its 46th minute the 2380 run had spent 12.3 CPU hours, all on
  the sampled subtrees, so the estimate of the whole tree is at least ten times that.  At 5060 a cut subtree counts
  only the nodes it walked.

## 4. Scaling

Listing arrangements loses at every size measured, and loses by less in nodes as n grows.  The ratio of its nodes to
the plain search's steps falls from 915 at 1500 to at least 0.9 at 5060.  The 5060 figure is a lower bound that the
heavy tails make loose, so the true ratio there is likely several times larger.  In CPU the walk is at least 8.4 times
the chain's proof at 5060: a node of the walk costs 5.8 ms there, a step of the search 0.63 ms.  At 1500 the two cost
about the same, 0.17 and 0.21 ms.

The cost of a proof varies by more than its n, so the trend alone does not settle what happens past 5060.  The chain's
proofs from 4500 to 5060 range from about 1 to 1,094 CPU hours, and 5260 took 78.5.  The measurements do settle 5060:
listing arrangements is no cheaper there, and it would have to be both nine times cheaper a node and close to its lower
bound to break even.

## 5. The frame solver's order: conflicts, not small primes

The frame solver does not decide the smooth part first, and section 3 says why it should not.  It branches on the
members of a *conflict*, a few members of the bound's heaviest set that cannot be promoted together.  It chooses the
conflict and the member by what leaving each out costs the bound
([solver/docs/design/search.md](https://github.com/bvchess/taxman/blob/287486e/solver/docs/design/search.md), "Conflict branching").  In the first 5
million steps of 5060, from an incumbent worth opt − 1:

* **13-smooth numbers are 28% to 44% of the conflicts' members at every depth** up to 220 promotions, where 99% of the
  conflicts are.  They are 25% of the root's candidates, 350 of 1,380.  23-smooth numbers are 61% of the members and
  41% of the candidates.  The search favors them a little, and decides them all along its paths, not first.
* **The members branched on most include large primes**: 2472 = 24·103 in 399,586 conflicts and 2512 = 16·157 in
  259,178, then 1953 = 63·31, 1785 = 105·17, 1755 = 135·13 and 1782 = 162·11.
* **Its conflicts refute arrangements in bulk.**  The conflicts have 17 members at the top of the tree and 2 near the
  leaves, and each rules out every arrangement that holds it.  So the search never meets most of the 32,294 living
  arrangements of 1500 one by one: its whole proof takes 7,088 steps.

So the proof's cost does lie in the small-prime numbers, as the substitutes that make exclusions cheap.  It does not lie
in a separable core whose arrangements could be listed first.

## What to keep

* **The fixed-part speed.**  With the 13-smooth part fixed, the rest of 5060 is proved in 1,746 steps, and a wrong
  arrangement is refuted in a few.  It is a fast exact check of a given arrangement, as E11 used it, and it measures
  how much of a search's cost the small-prime substitutes cause.
* **The solver's branching order.**  It follows conflicts priced by the bound, and small-prime members come up in them
  a little more often than among the candidates, at every depth.
* **The heavy tails.**  The subtrees of a fixed-order tree differ in size by orders of magnitude.  Knuth's estimator
  with hundreds of paths undercounts such a tree by tens of times, a sampled depth cut does better, and every run needs
  a hard time limit.

## Recommendations

1. **Drop the arrangement-first proof.**  It is 915 times the steps at 1500 and at least 8 times the CPU at 5060.  If it
   is ever reopened, its deciding test is a 30-minute depth-cut sample at 4983, the chain's dearest proof at 1,094 CPU
   hours, after making its nodes cheaper: the walk's bound should stop at the need, as the search's does.  It is dead
   if the sample's lower bound passes 4983's steps.
2. **Use the fixed-part check on best-known games past the chain.**  With the 13-smooth part of a best-known set fixed,
   the rest of a game the size of 5060 is solved exactly in seconds.  That finds the best game with that small-prime
   arrangement: a better game, or the proof that none exists without changing the small primes.  It needs an option to
   read the reference set from a file of best-known games, about an hour's work.  The test: run it over the best-known
   games 5061 to 5260 and count the improvements.  E11 found none at 5061 in a related region, so the gain is
   uncertain.
3. **Attack the cheap substitutes, not the arrangement.**  Without the 13-smooth twins, a gap of 1,191 closes in 1,746
   steps, against 10⁵ to 10⁶ steps for gaps near 1,000 with them.  That supports the open hypotheses of the anatomy
   entry: count or price the twin exchanges, (p − q)·m on a shared divisor m, instead of searching them one by one.
   This is where a much cheaper proof could come from, at the cost of research, not a build.  The test is the anatomy
   entry's first one, run on a unit of 5060: does the count of priced exclusions that fit the gap match the unit's
   leaves within a few times?

## Checks

* **Every search on a proven game returned its known optimum.**  With the score to beat opt(n) − 1, every finished run
  found opt(n).  With opt(n), none found more, every leaf searched among them.
* **The walk's bound is the search's.**  The walk uses the search's incremental GF(2) bound, and at every thousandth
  node the bound is computed again from the root: 16,511 nodes so compared at 1500 and 5060, none different.
* **The leaves do not depend on the order**: 32,294 at 1500 both ways.
* **The score to beat is the search's own incumbent.**  The tool is E8's and E11's, `restricted` (its checks are in
  ../loops/e8/README.md).  It gives the engine an incumbent worth the score and holding no set, so the search is the
  frame solver's own, cutting a node by the same need.

## Files

* `restricted`: the binary (see Provenance).
* `run-fix.sh` makes sections 1 and 2 and the plain searches: `fix.jsonl`, `baseline.jsonl`, `fix-N.err`.
* `run-tree.sh` runs Knuth's estimator: `tree-N-B-sS.jsonl`.
* `run-walk.sh` runs the walks: `walk.jsonl`, with the lines of the sampled subtrees in `walk-N-B-ABOVE.err`.
  `walk-2380-13-stopped.err` holds the progress lines of the 2380 walk, whose last line was lost when it was stopped.
* `census-5060-5M.jsonl` is the branching census of section 5.
* `summarize_tree.py`, `summarize_walk.py` and `summarize_census.py` make the tables; run them with `python3 -I`.

## Provenance

Run on batmobile on 2026-11-11 from the branch `loops-core` of the research repository, which is never pushed and was
made from `loops-e6` at df9b660.  The code is the subcommands `fix-smooth`, `smooth-tree` and `census` of
`examples/restricted.rs`, commits 5752398 and 58222ed.  The runs up to 12:07 PST ran on builds of the working tree on
the way to 5752398: the same searches and walks, without the time limits and the subtree lines.  The 5060 walk ran on
58222ed, the binary here.  Every run was at `chrt -i 0 nice -n 19` on 16 threads, while the machine ran other searches
at idle priority, so seconds are wall time under load; CPU seconds are the engine's or the threads' own.  The 2380
walk was sized from 1500's and ran past the two-hour limit, so the machine's owner had it stopped at 13:00 PST.
