# Where the best scores came from (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-06.  Concluded 2026-11-06.

**Question.**  In the run of 2026-11-01, which proved every game 1 to 5060, how far was each searched game's start from
its best promotion sum (P*), what found it, and how soon?  The answers set the scale of the levels of effort of the planned
unsound mode (`taxman solve --unsound --effort E`), which plays a high-scoring game of n without proving it optimal, and
say which techniques could matter.

**Answer.**  The start held P* in 974 of the 1,749 searched games (55.7%), the finder found it in 211 (12.1%),
and the rest, 564, are labeled the tree search because nothing else is left (the data cannot say more; see "What the
data cannot tell").  When the start fell short it fell short by a median of 67 points (p90 264, maximum 1,957) of
promotion sums of 10^4 to 6 × 10^5, a median of 0.13% of the sum at 1001-2000 and 0.02% at 4001-5060.  By an upper bound on the own time at which each
game held its P*, 68% of the searched games held it within 1 s, 87% within 10 s, 98.4% within 60 s and 99.7% within
300 s; the finder's slowest find took 847 s.  The root bound equals P* only up to n = 1,000, so stopping at it
saves nothing where the work is.  The 93 games of 4801-5060 took 78% of the run's hours, and about 1% of those hours
passed before P* was held.

## Method

*The data.*  The run is the one of [the full run at gate 300](../the-full-run-at-gate-300-2026-11/README.md): build
[aaba59b](https://github.com/bvchess/taxman/commit/aaba59b), one machine, 88 threads, a window of 4 games, and for each
search that took 1,000,000 steps a finder on one thread beside the tree search, for 900 s at most.  Its result lines
(`strict.jsonl`, 5,060 lines) and the 1,751 profiles of its searches stayed on the machine that ran it, in
`~/taxman_work/chain2-data/`; the committed lines are those of results commit
[5bd5d48](https://github.com/bvchess/taxman/commit/5bd5d48).  The script reads them and changes nothing.

*What each file records.*

* **The result line** ([REFERENCE](https://github.com/bvchess/taxman/blob/d3258ec/solver/docs/REFERENCE.md)) gives the
  game's method (`trivial`, `prime`, `repeat`, `start` or `search`), its score, so its optimal promotion sum (the score
  less `in_the_bag`), the greedy set's sum, the ceiling `cap`, the nodes, `seconds.active_all_runs`, and
  `engine.finder`, the finder's report: the steps it started at (`at_nodes`), the incumbent then (`from`), its best,
  how many of its sets became the incumbent (`improved`), its seconds and `found_seconds`, the seconds from its start at
  which it reached its best ([finder.rs](https://github.com/bvchess/taxman/blob/d3258ec/solver/frame/src/search/finder.rs),
  `Report`).
* **The profile** ([profile.rs](https://github.com/bvchess/taxman/blob/d3258ec/solver/frame/src/search/profile.rs))
  has a `start` record, whose `incumbent` is the start's promotion sum; `node` records, of which the root (id 0) has the
  root's upper bound `bound`; a `steps` record at each checkpoint, with the steps and the search's own clock `active`;
  an `open` record after it, with the incumbent at that checkpoint; and an `end` record.  There is no record of each
  improvement of the incumbent.
* **The start** is the best of the greedy set, what survives of the game before's promotions, and the dive, improved by
  a local search ([incumbent.rs](https://github.com/bvchess/taxman/blob/d3258ec/solver/frame/src/search/incumbent.rs)).
  Only its sum is recorded, not which part made it.

*The clock.*  A game's time is its own `active_all_runs`, the time it had a worker, and the clock of the profile's
`steps` records is the same one (4984: 40,960.08 s in the profile's `end`, 40,960.37 s in the line), so the time a game
waited in the window is not counted.

*What the script does* ([collect.py](collect.py)).  It streams each profile line by line, skipping `node` lines but the
root's, and takes for each game of method `search` or `start`:

* P*, the start's sum and shortfall (P* less start), the root bound, and whether the start met the bound;
* the source of P*, in this order: **the start**, if the start's sum reached P*; **the tree search
  before the finder**, if the incumbent when the finder started (`from`) reached it; **the finder**, if the finder's best
  reached it; **the tree search** otherwise, which includes every game with no finder;
* the own time at which the game held its P*, as an interval: for the finder, the search's clock when the finder
  started (interpolated from the `steps` records by the steps taken) up to that plus `found_seconds`; for the tree
  search, from the last checkpoint below P* up to the first at or above it, or to the end of the search if no
  checkpoint shows it;
* the checkpoints at which the incumbent rose.

The 490 games of method `start` ran no search, because their start reached the ceiling (`cap`), so for them the start is
P*, and the script treats them as optimal at the start without a profile (2 of them have one).  Stretches of n
are 1-1000, 1001-2000, 2001-3000, 3001-4000, 4001-4400, 4401-4800 and 4801-5060.  [out.txt](out.txt) is everything the
script prints; [games.json](games.json) has one record per game of method `search` or `start`.

## Results

**1. Two thirds of the games take their moves from the game before, and cost nothing.**  A `prime`, `repeat` or `start`
game copies its moves from the game before, or from the formula, with no search; together they are 3,298 of the 5,060
games, 65.2%, and they and the 13 trivial games took 0.08 hours of the run's 118.84.  The 1,749 searched games took
99.93% of it.

| games | trivial | prime | repeat | start | search | from the game before |
|---|---|---|---|---|---|---|
| 1-1000 | 13 | 168 | 416 | 90 | 313 | 67.4% |
| 1001-2000 | 0 | 135 | 432 | 81 | 352 | 64.8% |
| 2001-3000 | 0 | 127 | 415 | 101 | 357 | 64.3% |
| 3001-4000 | 0 | 120 | 426 | 86 | 368 | 63.2% |
| 4001-4400 | 0 | 49 | 165 | 52 | 134 | 66.5% |
| 4401-4800 | 0 | 47 | 170 | 51 | 132 | 67.0% |
| 4801-5060 | 0 | 31 | 107 | 29 | 93 | 64.2% |
| 1-5060 | 13 | 677 | 2,131 | 490 | 1,749 | 65.2% |

A game of method `start` costs, by active seconds, a median of 0.01 (to 1000) rising to 0.54 (4801-5060), at most 1.6; a
`repeat` or `prime` game costs less than a second.  The cost of the setup and the start of a game is therefore a few
tenths of a second at n near 5,000.

**2. The start held P* in 55.7% of the searched games, and the root bound was never what stopped one past
n = 1,000.**

| games | searched | start optimal | start met the root bound | P* = root bound | P* = ceiling |
|---|---|---|---|---|---|
| 1-1000 | 313 | 228 (72.8%) | 66 (21.1%) | 68 (21.7%) | 2 |
| 1001-2000 | 352 | 173 (49.1%) | 0 | 0 | 1 |
| 2001-3000 | 357 | 180 (50.4%) | 0 | 0 | 0 |
| 3001-4000 | 368 | 174 (47.3%) | 0 | 0 | 1 |
| 4001-4400 | 134 | 81 (60.4%) | 0 | 0 | 0 |
| 4401-4800 | 132 | 82 (62.1%) | 0 | 0 | 0 |
| 4801-5060 | 93 | 56 (60.2%) | 0 | 0 | 0 |
| 1-5060 | 1,749 | 974 (55.7%) | 66 (3.8%) | 68 (3.9%) | 4 |

* **The root bound lies above P* from n = 1,001 on**, in all 1,436 searched games: by a median of 943 points
  (p90 1,783, from 48 to 2,620), 0.43% of P* at the median (p90 0.67%, maximum 1.13%).  Over all
  searched games the start lay below the bound by a median 680 in the games where it was optimal and 908 where it fell
  short, so the gap to the bound
  does not tell the two apart.
* **The ceiling** (n plus the score of the game before, as a promotion sum) was reached in 4 searched games besides the 490 that
  ended at it before a search.
* **The greedy set alone** was optimal in 59 searched games, all at n ≤ 1,000, and in 87 of the 403 games of method
  `search` or `start` there; above 1,000 in none of 1,836 (the last lines of [out.txt](out.txt)).  In 1,680 searched games the
  start beat the greedy set, and in 69 it equaled it.

**3. When the start fell short, it fell short by little, and less of the sum as n grew.**  Of the 775 searched games
whose start fell short:

| games | short | shortfall median | p90 | maximum | relative median | relative maximum |
|---|---|---|---|---|---|---|
| 1-1000 | 85 | 20 | 71 | 146 | 0.158% | 8.4% |
| 1001-2000 | 179 | 58 | 226 | 547 | 0.127% | 1.29% |
| 2001-3000 | 177 | 74 | 285 | 595 | 0.055% | 0.44% |
| 3001-4000 | 194 | 81 | 271 | 653 | 0.028% | 0.28% |
| 4001-4400 | 53 | 66 | 342 | 932 | 0.017% | 0.24% |
| 4401-4800 | 50 | 85 | 274 | 544 | 0.017% | 0.12% |
| 4801-5060 | 37 | 117 | 459 | 1,957 | 0.022% | 0.37% |
| 1-5060 | 775 | 67 | 264 | 1,957 | 0.051% | 8.4% |

The shortfall in points grows slowly with n while the sum grows with n, so the start is within 0.03% of P* at
the median from 3001 on.  The largest, 4851, started 1,957 below (533,291 of 535,248), and the finder reached the
P* 14.9 s into its own clock.

**4. The finder found P* in 211 games, in a median of 4.4 s on one thread, and the tree search found the rest
quickly, because it was short.**  The sources of P*:

| games | start | the finder | tree search before the finder | tree search (no finder, or the finder lost) |
|---|---|---|---|---|
| 1-1000 | 228 | 0 | 0 | 85 |
| 1001-2000 | 173 | 0 | 0 | 179 |
| 2001-3000 | 180 | 32 | 23 | 122 |
| 3001-4000 | 174 | 98 | 51 | 45 |
| 4001-4400 | 81 | 27 | 17 | 9 |
| 4401-4800 | 82 | 29 | 11 | 10 |
| 4801-5060 | 56 | 25 | 11 | 1 |
| 1-5060 | 974 | 211 | 113 | 451 |

* **The finder ran in 703 searches**, those that took 1,000,000 steps: none to 2000, 76 of 357 in 2001-3000, and
  almost all above 4,000.  1,046 searched games ended first, and 423 of them began below their P*.  Their search
  held P* within 70 s at the latest (section 5); no finder ever tried them.
* **The finder's time to its best**, among the 211 games it won, in seconds on its own clock (median / p90 / maximum):
  2001-3000 3.9 / 48.9 / 420.4; 3001-4000 8.4 / 120.1 / 300.4; 4001-4400 2.7 / 30.1 / 210.2; 4401-4800 2.8 / 26.9 /
  172.2; 4801-5060 3.9 / 378.6 / 846.8; all 4.4 / 90.1 / 846.8.  Cumulatively, 52 of the 211 within 1 s, 126 within
  10 s, 186 within 60 s, 205 within 300 s, 209 within 600 s and all within 900 s, its budget.  A median of 2 of its sets
  became the incumbent (p90 4, maximum 12).
* **The finder started** a median 5.9 s (p90 20.9, maximum 57.1 s) into the game's own clock, and its 211 games lasted a
  median 113.8 s (p90 821.4, maximum 32,778).
* **Where the finder ran and the start was already optimal**, which is 351 of the 703, it had nothing to find, and ran
  until the search ended or its 900 s were spent; 65 of the 703 searches ran it the full 900 s.
* **The finder never ran its 900 s without P*.**  Of the 239 games still short when the finder started, it
  reached P* in 211 (88%).  In the other 28 the search ended first, after 13 to 70 s of own time and with the
  finder 1.8 to 50 s into its run, and P* came from the tree search.
* **The tree search before the finder** found P* in the 113 games where the incumbent at the finder's start
  already held it.

**5. P* was held early, in a small share of the hours.**  The share of searched games that held P*
within T own seconds, by the upper end of each game's interval (so no game held it later):

| games | at the start | 1 s | 10 s | 60 s | 300 s | 900 s |
|---|---|---|---|---|---|---|
| 1-1000 | 72.8% | 100% | 100% | 100% | 100% | 100% |
| 1001-2000 | 49.1% | 84.9% | 100% | 100% | 100% | 100% |
| 2001-3000 | 50.4% | 53.8% | 94.7% | 99.2% | 99.7% | 100% |
| 3001-4000 | 47.3% | 47.3% | 70.4% | 95.4% | 99.7% | 100% |
| 4001-4400 | 60.4% | 60.4% | 74.6% | 98.5% | 100% | 100% |
| 4401-4800 | 62.1% | 62.1% | 79.5% | 99.2% | 100% | 100% |
| 4801-5060 | 60.2% | 60.2% | 64.5% | 94.6% | 95.7% | 100% |
| 1-5060 | 55.7% | 68.4% | 87.3% | 98.4% | 99.7% | 100% |

And the hours, among the searched games, with the hours that passed before P* was held (an upper bound):

| games | hours | held by (hours) | share | median game (s) |
|---|---|---|---|---|
| 1-1000 | 0.00 | 0.002 | 37% | 0.04 |
| 1001-2000 | 0.08 | 0.040 | 52% | 0.76 |
| 2001-3000 | 0.91 | 0.420 | 46% | 2.5 |
| 3001-4000 | 11.67 | 1.442 | 12.4% | 40.8 |
| 4001-4400 | 2.57 | 0.357 | 13.9% | 42.5 |
| 4401-4800 | 10.53 | 0.270 | 2.6% | 101 |
| 4801-5060 | 92.99 | 0.978 | 1.05% | 991 |
| 1-5060 | 118.76 | 3.509 | 2.95% | 2.8 |

* **The proofs are the cost.**  The 974 games whose start was optimal took 71.6 hours, 60% of the run's hours, all of it
  proof.  The 211 finder games took 34.9 hours of which P* was held, by an upper bound, in 2.7.  Of the 16
  games over 1 hour (73.4 hours in all), 11 started at P*; the other 5, 4970, 4992, 4995, 5054 and 5060, held
  it after 45, 855, 39, 60 and 855 s, in games of 1.8, 9.1, 6.0, 5.2 and 2.4 hours.
* **The tree search's time is bracketed only by the end of the game.**  All 451 games labeled tree search ended within
  70.5 s, before the first checkpoint; 2 of them have an `open` record, and it shows P*.  For the others the
  upper bound is the end of the search, a median 0.95 of the game's time.  The median upper bound is 1.0 s, p90 10.0 s,
  maximum 69.9 s.

## What this means for the unsound mode

* **The scale of the levels is seconds to minutes of own time per game, from 1 s to about 1,000 s.**  An upper bound says
  68% of the searched games held their P* within 1 s, 87% within 10 s, 98.4% within 60 s and 99.7% within 300 s.
  The slowest finds are the late games: 4851 (14.9 s after a start 1,957 short), 4992 (855 s) and 5060 (855 s), and the
  finder's maximum is 847 s on one thread.  Ten doublings from 1 s reach 1,024 s and cover all of the data.  Past n = 3,000 the share by 60 s is 94.6% to 98.5% in each stretch, so the top levels are what separate 95% from
  100%.  The proven run's tree search used all 88 threads while the finder used one, so a thread-second is not the same
  effort in the two, which limits what the figure says about the mode.
* **Stopping at the root bound would save no work.**  The bound equals P* in 68 searched games, all at
  n ≤ 1,000, which together took 0.002 hours.  From n = 1,001 on it lies above P* by a median 943 points, and
  does not tell a start that is optimal from one that fell short.  The ceiling stopped 494 games (490 + 4) in the proven
  run, but it is P* of the game before plus n, and an unsound game before may be lower than that, so the ceiling
  might not be a ceiling.  This entry measures neither the loss nor the saving; it does show that 9.7% of the games met
  it.
* **How much rides on the start: 55.7% of the searched games are exact at the start, 65.2% of all games are taken from
  the game before, and the other searched games are short by 0.03% of the sum at the median.**  The finder reached the
  P* in 211 of the 239 games that were short when it started, and the search ended first in the other 28.  A run that
  stops after the start would be exact in 974 of 1,749 searched games; one that adds 60 s of own time per game would
  be exact in 98.4% by the upper bound.  The start's own work is cheap: 0.5 s at n near 5,000.
* **The finder is worth running where the start fell short, which is not known beforehand.**  Of the 703 searches with a
  finder, 351 had an optimal start and spent up to 900 s on a finder that could not improve it.  Without a bound that
  tells the two apart, the unsound mode must spend its effort on every game.

## What the data cannot tell

* **When the tree search found P*.**  The profile records the incumbent at checkpoints, not at each
  improvement, and all 451 games ended before their first checkpoint but 2.  A game labeled tree search is one
  whose P* came neither with the start nor with the finder's best, and its time is known only to lie before the end
  of its search.  A set of the finder and the same set of the tree search cannot be told apart either: in one game (a
  checkpoint's record shows P* before the time the finder reported) the label finder may be the search.
* **How fast the finder would have been on the games it never ran in.**  The finder starts after 1,000,000 steps.  The
  1,046 searched games that ended earlier, 423 of them short at the start, have no finder's time; their P* came
  from the tree search on 88 threads.  The finder's times belong to the harder games, so they are not the
  distribution of the finder over all games.
* **The finder's clock.**  Its `found_seconds` runs from its own start on one thread, and the search's own clock at its
  start is interpolated between checkpoints.  The sum of the two is the game's own time to P* only if the
  finder thread ran while its game had a worker, and the finder, as part of the workers at idle priority on a machine
  loaded by 88 threads, may have run slower than it would alone.
* **Which part of the start made it.**  Only the sum is recorded, so the seed's survivors, the dive and the local
  search cannot be separated.  The greedy set shows that the whole start is the work: it was optimal in no game past
  1,000.
* **The mode itself.**  Multiple threads on the large neighborhood search, a budget counted in neighborhoods and not in
  seconds, a seed from an unsound game before, and the drift that gives: none ran here.  The shortfall of the start of a
  game seeded from an unsound game before is not that of these starts, which come from the proven game before.
* **Equal sums, different games.**  P* is a promotion sum.  A game that holds it is not the game of the
  proven run's line.

## Open

* The curve of V1a: every game from 3441 seeded with its proven game before, the finder on all threads until it holds
  the known score, gives the work each game needed, which this entry bounds from above only.
* A finder that starts at once on short searches would measure the 423 games whose P* was found by the tree
  search before any finder.
* A record of each improvement of the incumbent in the profile (its own clock, steps and source) would settle the 451
  games' labels.
* Whether a ceiling from an unsound game before can stop a game.

## Files

* [collect.py](collect.py): the script.  `nice -n 19 python3 -I collect.py [DATA_DIR [OUT_DIR]]` reads
  `DATA_DIR/results/strict.jsonl` and `DATA_DIR/profile/` (default `~/taxman_work/chain2-data`) with 4 processes, writes
  games.json to OUT_DIR, and prints the entry's numbers.  It takes about 4 minutes.
* [games.json](games.json): one record per game of method `search` or `start`: n, method, proof, opt, cap, greedy,
  nodes, active, cpu, the finder's report, start, root bound and gap, whether the start met the bound, the source of the
  P*, the interval of own time `t_lo` to `t_hi`, the checkpoints at which the incumbent rose, and the finder's start
  on the search's own clock.
* [out.txt](out.txt): the script's output, the source of every number above.

No code of the main repository changed.  The code read is that of commit
[d3258ec](https://github.com/bvchess/taxman/commit/d3258ec); the run's build is aaba59b.
