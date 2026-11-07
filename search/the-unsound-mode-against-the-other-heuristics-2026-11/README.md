# The unsound mode against the other heuristics (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  The repository has other heuristic strategies besides the unsound mode: seven in `moniot/` (C++, by
another author) and five in `heuristics/strategies/` (Python) with the continuation chain.  On the same games, by the
same measures and with their time, is the unsound mode better than they are, as good as the best of them, or not?  The
games are 4561-5060, the top of the known range, where opt(n) is proven, and 5061-5160, past it, where it is not.

**Answer.**  The unsound mode is better in every score measure, and the heuristics win only in time.  On 4561-5060 the
unsound mode at level 1 (131,072 work, 37.6 core-seconds a game) scores opt(n) in 471 of 500 games (94.2%) and 99.9999%
of the points.  No heuristic scores opt(n) in more than 13 of its games: the continuation chain, 13 of 74 (17.6%) at 598
core-seconds a game; solvent, the best that played all 500, 0 of 500 and 99.899% of the points at 36.5 core-seconds.  No
heuristic scores higher than the unsound mode on any game of either stretch (level 1 on 4561-5060, level 6 on both),
and only the chain ever ties it, on 13 games.  On 5061-5160 the unsound mode at level 6 holds the best score found on
all 100 games; the chain falls 700 to 1,684 points short on the 23 games it reached, solvent a median
10,811 on 96, solvent-b a median 7,052 on 24, and moniot OneTax a median 99,576 on 13.  The heuristics win in time
alone:
moniot's strategies take 0.006 to 7 core-seconds a game, less than the 13.0 that the unsound mode's start takes on its
own, but leave 1.4% to 38% of the points on the table.  opt(n) itself lies 0.245% of the points below the
Franklín–Moniot bound on 4561-5060; the unsound mode from level 1 up lies 0.245% below it too, and the heuristics
lie farther: solvent 0.346%, solvent-b 0.324%, the chain 0.247%.  It is one seed of the unsound mode, and several of
the heuristics ran on some of the games only (section "What ran").

## Method

*The strategies.*

| strategy | where | what it does | gives moves |
|---|---|---|---|
| moniot OneTax, GreedyOneTax, PureOneTax | [moniot/](https://github.com/bvchess/taxman/blob/50db88e/moniot/README.md) (C++) | takes the largest number with one divisor left in the pot; OneTax with a tweak, GreedyOneTax choosing among them by take minus tax, PureOneTax with none | yes |
| moniot MaxTurn+, MaxTurn | moniot/ | takes the pick with the best take minus tax; MaxTurn+ then adds picks that cost nothing | yes |
| moniot OddsEvens, MaxPick | moniot/ | the largest prime, the odd numbers, then the even ones; the largest legal number | yes |
| cascade | [heuristics/](https://github.com/bvchess/taxman/blob/50db88e/heuristics/README.md) (Python) | the numbers above half the pot by band, by the matching theory, no search | yes |
| solvent | heuristics/ | greedy over the sets that stay payable, in O(n² log n) | yes |
| solvent-b | heuristics/ | solvent, then each pick that is also another pick's payment is banned in a rerun, kept if it scores more | yes |
| continuation chain | heuristics/ | game n from the set of game n - 1: flips, bundles, and solvent as a floor | its set, from which the chain derives a legal order |
| the unsound mode | the frame solver | the start of the proven search seeded with the moves for n - 1, then rounds of large neighborhood search | yes |

The Python onetax and maxturn of heuristics/ are written again from moniot's OneTax and MaxTurn and match them on every
game of 2 to 2000 (moniot/'s README); they never ran here (section "What ran"), and moniot's stand for them.

*The levels.*  The runs used master [50db88e](https://github.com/bvchess/taxman/commit/50db88e), whose lines record an
effort E and a budget of 2^(E-1) × 65,536 work.  Master [19a6c24](https://github.com/bvchess/taxman/commit/19a6c24)
numbers the levels from 1 to 6, the old effort E being level E - 1, with a budget of 2^L × 65,536, and this entry uses
that numbering.  The start alone (old effort 0) and the budget of 65,536 work (old effort 1) are no levels there, and
the tables name them for what they are.

*The stretches.*  4561-5060 (500 games) has opt(n) from `results/optimal.jsonl.gz`.  The unsound mode's lines there are
those of [study E2](../the-datasheet-of-the-unsound-mode-2026-11/README.md), five chains of 100 games, each from the
table's game before its first, at each effort 0 to 7, with `--back 8 --tilt 25 --widen 4 --seed 1` (master a2a1a2e,
which 50db88e makes the defaults) on 4 threads, 8 at level 6.  5061-5160 (100 games) is past the table and has no
opt(n): the reference for a game is the best score that any method here found for it, a lower bound on opt(n).  The
unsound mode ran there as one chain of 100 games, `taxman solve 5061-5160 --unsound --effort 7 --seed 1 --threads 4`,
from the table's game 5060, and the continuation chain from the table's moves for 5060.  A first plan also covered
1001-2000; the project owner dropped it, because the heuristics matter past 5060, where no one pays for optimal games,
and the known range serves as their proxy only at its top.

*The measures.*  For each row over the games it played:

* the games at the reference (count and share), the point share (the sum of the scores over the sum of the
  references) and the worst game (score over reference);
* the points below the [Franklín–Moniot bound](https://github.com/bvchess/taxman/blob/50db88e/docs/GLOSSARY.md),
  `1 - Σ score / Σ bound` over the row's games.  The bound is the weight of a maximum-weight matching of the
  maximal-factor graph, which no game can pass and opt(n) approaches within 0.25%.  [fm_bound.py](fm_bound.py)
  computes it for every game 2 to 5160 by mending a matching and its dual with one
  search for each n, and checks the dual (feasible, equal in weight) for every n; it agrees with all 1,999 bounds of
  `heuristics/results/fm_bound_2000.json`.  The repository's bound.py calls networkx, which is not installed here;
* the time as the mean over the games of the wall seconds, the threads the row used, and the core-seconds (wall
  seconds times threads), so that one thread of Python compares with 4 of the unsound mode.  The mean, not the median,
  since many games of the unsound mode end in under a second (a prime or a repeat);
* the hours that 100 games take on the machine's 88 CPUs.  Independent games (moniot's seven, cascade, solvent,
  solvent-b) run 88 at once, the longest first onto the least loaded CPU, a sample of fewer games repeated to 100.  A
  chain plays one game after another: the continuation chain on its one thread, the unsound mode on 64 threads,
  converted from its runs on 4 (8) by E2's measurements of the busy machine (1.78 and 1.73 times an idle one's for the
  start and the rounds) and of the speedups (5.87 and 4.15 on 64 threads).  The conversion gives E2's own datasheet
  figures for 4561-5060, 0.59 hours at level 6 and 0.10 at level 3.

*The runs.*  `taxman` was built from master 50db88e (`nice -n 19 cargo build --release --config
profile.release.lto=false --config profile.release.codegen-units=16 ... --bin taxman`, at -j 4, before any run); every
line of the unsound mode records `"build": {"commit": "50db88e...", "dirty": false}`.  moniot/ was copied to a scratch
folder and built there with its Makefile; heuristics/ was copied there too, and its modules run unchanged by
[h1_heuristics.py](h1_heuristics.py), which times each game on one thread (the call of the strategy alone, the divisor
tables built before) and records its moves.  [run_h1.py](run_h1.py) ran the jobs from a queue at nice 19, 8 threads at
once at first and 16 later, and the project owner raised the limit to 32 and then 56 threads for solvent-b.  The
solvent-b runs beyond the queue's parts were pools of workers that claim games between them, started by hand:

    nice -n 19 python3 -I h1_heuristics.py python --heuristics H --strategy solvent_b --lo 4561 --hi 5060 \
        --workers 20 --order spread --claims runs/heur/claims-solvent_b --deadline EPOCH \
        --skip 'runs/heur/B-solvent_b*.jsonl' --out runs/heur/B-solvent_b-pfull.jsonl

The pools had 20 and 13 workers on 4561-5060 and 4 and 3 on 5061-5160, from 10:47 and 11:44 until 13:48, and the whole
study ran from 07:07 to 14:04 on 2026-11-07 (Pacific time).  The first 25 games of solvent-b took a mean of 2,463 s
(41 minutes); 600 games would take 410 thread-hours, 9 to 10 hours on the 40 to 48 workers that the limit of 56 threads
left, more than the 6 hours that the project owner allowed.  So the pools play the games in the order of the van der
Corput sequence of their places, whose first half is every second game (the odd n), and a game starts only before
15:50.  The pools stopped at 13:48, at the project owner's direction, with 47 and 24 games finished, all of odd n.  The
machine was shared: the load average at a game's start was 76 for moniot's runs, cascade and solvent, 36 to 44 for
solvent-b, 47 to 65 for the chains, and 44 to 76 for the unsound mode on 5061-5160 (E2's runs: 72 to 81), so every
second here is a busy machine's.

*The checks* ([analyze.py](analyze.py), output [out.txt](out.txt)).  Every line is checked: no score above opt(n) where
the game is proven, none above the bound, and its moves replay as a legal game of the score the line gives.  The unsound
lines also pass E2's checks (unsound, the build, the effort and options, the threads, and each game started from the
run's line before it, the first from the table's).

## What ran

The study stopped when the question was answered, so the rows cover different games.  Each says what it covers and why.

| strategy | 4561-5060 | 5061-5160 | why |
|---|---|---|---|
| moniot OneTax | 493 (4561-5053) | 13 (5061-5073) | the runs went in the order of n and stopped there |
| moniot GreedyOneTax | 489 (4561-5049) | 10 (5061-5070) | the same |
| moniot PureOneTax | 469 (4561-5029) | 8 (5061-5068) | the same |
| moniot MaxTurn+ | 214 (4561-4774) | 0 | the same |
| moniot MaxTurn | 108 (4561-4668) | 0 | the same |
| moniot OddsEvens, MaxPick | 500 | 0 | the 5061-5160 runs did not start |
| Python onetax, maxturn | 0 | 0 | queued behind longer jobs, never started; moniot's OneTax and MaxTurn give the same scores |
| cascade | 500 | 100 | all |
| solvent | 500 | 96 (5065-5160) | the last four games were in play when it stopped |
| solvent-b | 47 | 24 | one game takes 16 to 122 minutes of Python, and none reached opt(n); odd n, spread over the range |
| continuation chain | 74 | 23 (5061-5083) | five chains of 100 in 4561-5060, stopped after 20, 20, 9, 12 and 13 games; the chain of 5061-5160 was to stop after 4 hours of its games, and stopped after 4.4 |
| the unsound mode | 500 at each of the start alone, 65,536 work and levels 1 to 6 | 100 at level 6 | levels 1 to 5 on 5061-5160 did not run |

The moniot rows are prefixes of the range.  The solvent-b rows are the games finished when the pools stopped, about 40
games in play being lost, so a game that takes long is more likely missing: its mean seconds are a low estimate.  The
47 games of 4561-5060 and the 24 of 5061-5160 are all of odd n, spread over the range (every eighth game at the start
of the order, with the five samples of the queue), and the shares of solvent-b are those of odd games.

## Results

**1. The lines pass the checks.**  All 7,894 lines of 4561-5060 (19 rows) and 374 of 5061-5160 (8 rows) replay as legal
games of the score they give, none ends with a legal move left, and none scores above opt(n) or above the bound.  The
unsound run of 5061-5160 went on from its file for its last two games (the queue was stopped, and the same command
finished them), so game 5159 started from `prev.source` `results` and the others from `run`, the first from `table`.

**2. 4561-5060.**  The first column group is the score, the second the time (means; the machine's 88 CPUs for 100
games).

| strategy | games | at opt(n) | point share | worst game | below the bound | threads | wall s | core-s | total wall s | 100 games on 88 CPUs, h |
|---|---|---|---|---|---|---|---|---|---|---|
| moniot OneTax | 493 | 0 | 98.840% | 98.65% | 1.402% | 1 | 6.54 | 6.54 | 3,223 | 0.0032 |
| moniot GreedyOneTax | 489 | 0 | 98.747% | 98.57% | 1.495% | 1 | 6.51 | 6.51 | 3,185 | 0.0032 |
| moniot PureOneTax | 469 | 0 | 96.760% | 96.28% | 3.477% | 1 | 6.54 | 6.54 | 3,069 | 0.0032 |
| moniot MaxTurn+ | 214 | 0 | 94.527% | 94.34% | 5.698% | 1 | 5.18 | 5.18 | 1,109 | 0.0025 |
| moniot MaxTurn | 108 | 0 | 90.396% | 90.26% | 9.818% | 1 | 4.97 | 4.97 | 537 | 0.0025 |
| moniot OddsEvens | 500 | 0 | 83.404% | 83.04% | 16.800% | 1 | 0.006 | 0.006 | 2.8 | 0.0000028 |
| moniot MaxPick | 500 | 0 | 62.081% | 61.78% | 38.071% | 1 | 0.60 | 0.60 | 302 | 0.0003 |
| cascade | 500 | 0 | 92.891% | 92.73% | 7.336% | 1 | 29.3 | 29.3 | 14,671 | 0.0131 |
| solvent | 500 | 0 | 99.899% | 99.84% | 0.346% | 1 | 36.5 | 36.5 | 18,229 | 0.0164 |
| solvent-b | 47 | 0 | 99.922% | 99.86% | 0.324% | 1 | 4,387 | 4,387 | 206,184 | 2.03 |
| continuation chain | 74 | 13 (17.6%) | 99.9956% | 99.98% | 0.247% | 1 | 598 | 598 | 44,223 | 16.6 |
| unsound, start alone | 500 | 28 (5.6%) | 99.9957% | 99.97% | 0.249% | 4 | 3.26 | 13.0 | 1,629 | 0.0089 |
| unsound, 65,536 work | 500 | 445 (89.0%) | 99.9998% | 100.00% | 0.245% | 4 | 6.46 | 25.8 | 3,229 | 0.0210 |
| unsound, level 1 | 500 | 471 (94.2%) | 99.9999% | 100.00% | 0.245% | 4 | 9.40 | 37.6 | 4,698 | 0.0323 |
| unsound, level 2 | 500 | 479 (95.8%) | 99.9999% | 100.00% | 0.245% | 4 | 14.6 | 58.5 | 7,311 | 0.0525 |
| unsound, level 3 | 500 | 486 (97.2%) | 100.0000% | 100.00% | 0.245% | 4 | 26.0 | 104 | 12,993 | 0.0964 |
| unsound, level 4 | 500 | 486 (97.2%) | 100.0000% | 100.00% | 0.245% | 4 | 48.1 | 192 | 24,044 | 0.18 |
| unsound, level 5 | 500 | 486 (97.2%) | 100.0000% | 100.00% | 0.245% | 4 | 88.1 | 353 | 44,067 | 0.34 |
| unsound, level 6 | 500 | 494 (98.8%) | 100.0000% | 100.00% | 0.245% | 8 | 91.6 | 733 | 45,816 | 0.59 |

The rows of out.txt also give the median seconds, the hours for 100 games one after another and the load.  opt(n)
itself is 0.245% of the points below the bound (per game: a median 0.246%, from 0.225% to 0.266%).

![The share of games at the reference score against the core-seconds a game, a point for each strategy and level, for
4561-5060 and 5061-5160](h1.svg)

![The same against the hours that 100 games take on the 88 CPUs](h1-machine.svg)

The first chart puts the core-seconds a game on the time axis, the second the hours for 100 games on the whole machine.
The chart's reading follows the table: every heuristic but the chain sits at 0%, and the unsound mode's points climb
from 5.6% at 13 core-seconds to 98.8% at 733.

* **The unsound mode's start alone already beats every heuristic that costs more than it does.**  At 13.0 core-seconds
  it scores 99.9957% of the points against solvent's 99.899% (36.5 core-seconds), cascade's 92.891% (29.3) and
  solvent-b's 99.922% (4,387).  On the 74 games that the chain (598) played it scores 99.9985% of the points against
  the chain's 99.9956%, and opt(n) in 37.8% of the games to the chain's 17.6%.  Only moniot's strategies cost less
  (0.006 to 6.5 core-seconds), and they score 62% to 98.8% of the points.
* **Level 1 costs what solvent costs and gets 94.2% of the games.**  Its 37.6 core-seconds are solvent's 36.5; solvent
  scores opt(n) in none of 500.  Levels 3 to 5 score opt(n) on the same 486 games, as E2 found, and level 6 adds 8,
  the tails behind two stuck games.
* **Where a heuristic could win game by game it does not.**  Of 22 comparisons of a strategy with the unsound mode at
  level 1 or 6, in none does the strategy score opt(n) on a game that the unsound mode misses, or score higher than it
  on any game: 0 games in each, against 44 to 494 games that the unsound mode has at opt(n) and the strategy does not
  (sign test, p below 1e-12).  The 29 games that level 1 misses and the 6 that level 6 misses are missed by every
  heuristic that played them.

**3. 5061-5160.**  The reference is the best score found for the game.

| strategy | games | at the best | points short of it (total) | point share of the best | worst game | below the bound | threads | wall s | core-s | total wall s | 100 games on 88 CPUs, h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| moniot OneTax | 13 | 0 | 1,274,494 | 98.786% | 98.76% | 1.467% | 1 | 7.40 | 7.40 | 96 | 0.0037 |
| moniot GreedyOneTax | 10 | 0 | 991,258 | 98.772% | 98.73% | 1.481% | 1 | 7.48 | 7.48 | 75 | 0.0039 |
| moniot PureOneTax | 8 | 0 | 2,199,452 | 96.593% | 96.57% | 3.655% | 1 | 7.38 | 7.38 | 59 | 0.0035 |
| cascade | 100 | 0 | 58,556,513 | 92.874% | 92.79% | 7.376% | 1 | 33.9 | 33.9 | 3,392 | 0.0146 |
| solvent | 96 | 0 | 1,015,761 | 99.871% | 99.85% | 0.398% | 1 | 41.9 | 41.9 | 4,021 | 0.0185 |
| solvent-b | 24 | 0 | 165,065 | 99.916% | 99.89% | 0.352% | 1 | 3,217 | 3,217 | 77,199 | 1.99 |
| continuation chain | 23 | 0 | 18,148 | 99.9903% | 99.98% | 0.268% | 1 | 666 | 666 | 15,324 | 18.5 |
| unsound, level 6 | 100 | 100 | 0 | 100.0000% | 100.00% | 0.270% | 4 | 203 | 813 | 20,328 | 0.78 |

* **The unsound mode holds the best on every game, and no heuristic scores higher on any.**  The best is a lower bound
  on opt(n): the stretch has no proof, and the heuristics here cannot show the unsound mode short.
* **The chain starts 700 points short and stays so.**  It scores 700 less than the unsound mode on games 5061-5071,
  708 less on 5072-5081 and 1,684 less on 5082 and 5083, each shortfall handed on from the game before; its search
  closed none (it ran its bundle search on 3 of 23 games).  The unsound mode searched 44 games of the 100 (10 were
  primes and 46 repeats), and none of its lines shows the line before it short (`prev.short_by` is 0).
* **The gap to the bound is a trend to read with care.**  The best known lies 0.270% below the bound over the 100 games,
  and by blocks of 25 games 0.258%, 0.263%, 0.271% and 0.286%; opt(n) lay 0.250% below it in the last segment of
  4561-5060.  The rise is larger than the segments of 4561-5060 show (below), and the data do not say whether the bound
  loosens or the unsound mode's chain falls short of opt(n) as it grows, which E2 saw a chain of 200 games do.

**4. The trend over the segments of 4561-5060.**  Games at opt(n) of the games played in each segment of 100, and the
points below the bound in percent (all rows are in out.txt):

| row | 4561-4660 | 4661-4760 | 4761-4860 | 4861-4960 | 4961-5060 |
|---|---|---|---|---|---|
| every heuristic but the chain, games at opt(n) | 0 | 0 | 0 | 0 | 0 |
| chain, games at opt(n) | 9 of 20 | 1 of 20 | 0 of 9 | 3 of 12 | 0 of 13 |
| unsound, level 1, games at opt(n) | 100 | 100 | 100 | 75 | 96 |
| unsound, level 6, games at opt(n) | 100 | 100 | 100 | 94 | 100 |
| opt(n), below the bound | 0.237 | 0.237 | 0.247 | 0.252 | 0.250 |
| unsound, level 1, below the bound | 0.237 | 0.237 | 0.247 | 0.253 | 0.250 |
| solvent, below the bound | 0.315 | 0.318 | 0.335 | 0.395 | 0.360 |
| solvent-b, below the bound | 0.295 | 0.298 | 0.312 | 0.366 | 0.329 |
| chain, below the bound | 0.244 | 0.234 | 0.258 | 0.249 | 0.262 |
| cascade, below the bound | 7.237 | 7.322 | 7.377 | 7.445 | 7.292 |
| moniot OneTax, below the bound | 1.318 | 1.431 | 1.389 | 1.381 | 1.487 |
| moniot PureOneTax, below the bound | 3.477 | 3.547 | 3.494 | 3.258 | 3.673 |
| moniot OddsEvens, below the bound | 16.748 | 16.799 | 16.726 | 16.675 | 17.034 |
| moniot MaxPick, below the bound | 37.995 | 38.007 | 38.047 | 38.067 | 38.216 |

* **opt(n) follows the bound with a gap that rises 0.004 points of percent a segment** (a fit to the five segments).
  The unsound mode from level 1 up is within 0.001 of it in every segment, so what it scores tracks opt(n); its share
  of games at opt(n) falls in the top two segments (stuck games at 4914, 4950, 5040), as E2 found.
* **A heuristic keeps its level.**  The gaps of solvent, cascade and the moniot strategies change by 0.05 to 0.3 points
  of percent over the five segments, up if anything (solvent 0.315 to 0.360, OneTax 1.318 to 1.487), and their share at
  opt(n) is 0 in every segment: they do not improve with n.  The rows that played a prefix (MaxTurn+, MaxTurn) have
  too few segments for a slope.
* **What carries past 5060** is a heuristic's gap to the bound, which rises by about as much as the best known does:
  solvent lies 0.398% below the bound on 5061-5160 against 0.346% on 4561-5060, solvent-b 0.352% against 0.324%, OneTax
  1.467% against 1.402%, cascade 7.376% against 7.336%, a rise of 0.03 to 0.07 points of percent, where the best known
  rose from 0.245% to 0.270%.

**5. Time.**  The table of section 2 and 3 holds the means; these are the readings.

* **One thread of Python against 4 threads of the unsound mode.**  In core-seconds a game, moniot's OneTax (6.5) costs
  half of the unsound mode's start alone (13.0), and cascade (29.3) and solvent (36.5) cost between the start alone and
  level 1 (37.6); the chain (598) costs between level 5 (353) and level 6 (733), and solvent-b (4,387, the games it
  finished) six times level 6.
* **On the 88 CPUs**, 100 games take 12 seconds of moniot's OneTax, 47 and 59 seconds of cascade and solvent, 32 seconds
  of the unsound mode's start alone, 2 minutes at level 1 and 35 minutes at level 6, against 2 hours of solvent-b
  and 16.6 hours of the chain, which plays its games one after another.  The independent heuristics gain from 88
  CPUs and the chain does not; the unsound mode gains less than games run 88 at once (E2 measured a speedup of 4.15 on
  64 threads over 4).
* **The busy machine.**  The loads above say that the seconds are not an idle machine's.  E2 measured a busy machine's
  seconds for the unsound mode at 1.73 times an idle one's (loads 72 to 81); the heuristics ran at 36 to 76, and no such
  factor was measured for them.  A game of solvent-b took from 984 s (n = 4897) to 7,308 s (n = 4689) at the same
  load of 15: the games differ more than the loads do.

## What this means

* **The unsound mode is better.**  From level 1 it scores opt(n) on 94.2% of the games where no heuristic reaches 18%,
  at the core-seconds of solvent (37.6 against 36.5), and from the start alone it scores more points than any heuristic
  that costs more than 13 core-seconds.  Past 5060, at level 6, it holds the best score on every game.
* **Where a heuristic wins.**  In time only: moniot's strategies take 12 seconds for 100 games on the machine, less than
  the unsound mode's 32, and give a game 1.4% to 38% under the bound, where the unsound mode gives it 0.25%.  Nobody
  wins on the score of a game: no heuristic scores opt(n) where the unsound mode does not, on 4561-5060, and none
  scores higher than level 6 on any of 5061-5160.
* **The continuation chain is the nearest heuristic in points, and the second dearest in time.**  It scores 99.9956% of
  the points, as the start alone does, but it falls short in 82.4% of its games, and each shortfall passes to the games
  after it, since a chain builds each game from its own game before.
* **Past 5060 the heuristics hold their level**, with gaps to the bound 0.03 to 0.07 points of percent larger; the
  best known lies 0.025 points farther from the bound than opt(n) does at 4561-5060, and the data cannot split that into
  the bound's loosening and the unsound mode's chain drifting from opt(n).

## What the data cannot tell

* **One seed.**  The unsound mode's lines are of the seed 1, and E2's are the only ones on 4561-5060; its shares have no
  interval, and level 6's 8 games over level 3 come from two stuck games and the games behind them.
* **The rows cover different games.**  A share of 17.6% for the chain is of 74 games, the first of five chains, and
  solvent-b's 0 is of 47 games of odd n; moniot's rows are prefixes of the range.  The comparisons with the unsound mode
  are over the games both played: level 1 scores opt(n) on all 74 of the chain's games and on 44 of solvent-b's 47.
* **Python's seconds are Python's.**  The Python strategies were not written for speed, and a fast implementation
  would change the ratios; the C++ of moniot/ is the fast case here, and it is the cheapest and the weakest.
* **The threads differ.**  The core-seconds make one thread comparable with four; a thread of a busy machine is not a
  thread of an idle one, and the unsound mode's speedup on 64 threads is a conversion, not a run.  The hours on the 88
  CPUs assume that 88 games at once each take the seconds measured, at the load of 76 that moniot's runs, cascade and
  solvent saw.
* **The chains' segments.**  The unsound mode's 4561-5060 chains and the continuation chain's start from the table's
  game before their first; a chain of 100 games meets stuck games that a longer one meets more of.
* **5061-5160 has no opt(n).**  The best known is a lower bound, found mostly by the unsound mode itself, so a
  game where it is short and the heuristics are shorter would not show.  Only level 6 ran there; the shares of the lower
  levels on these games are unknown.

## Open

* The unsound mode at levels 1 to 5 on 5061-5160, and its levels on a second seed.
* The moniot strategies and the Python onetax and maxturn on every game of both stretches, and solvent-b on more games.
* A proof of some games past 5060, to see how far the best known falls short of opt(n).

## Files

* [h1_heuristics.py](h1_heuristics.py): plays the strategies of moniot/ and heuristics/ and the chain, a line a game
  with
  the score, the seconds and the moves.
* [run_h1.py](run_h1.py): the queue of the jobs, at nice 19 under a limit of threads.  The unsound mode's chain on
  5061-5160 ran as a job of it, and its last two games by hand: `nice -n 19 taxman solve 5061-5160 --unsound --effort 7
  --seed 1 --threads 4 --out runs/unsound/e7-5061.jsonl`.
* [fm_bound.py](fm_bound.py): the bound of every game 2 to 5160, `python3 -I fm_bound.py --limit 5160
  --out fm_bound.json --committed fm_bound_2000.json`; [fm_bound.json](fm_bound.json) is its output.
* [analyze.py](analyze.py): the checks, every number above and the charts.  `nice -n 19 python3 -I analyze.py --results
  optimal.jsonl.gz > out.txt`, with `--e2` for E2's `runs/` if the entry is not beside it; [out.txt](out.txt) is its
  output, [h1.svg](h1.svg) and [h1-machine.svg](h1-machine.svg) the charts.
* [runs/heur/](runs/heur/): the lines of the heuristics, `B-NAME` for 4561-5060 and `C-NAME` for 5061-5160 (a job cut
  into parts has the files `NAME-pK`; `-pfull` and `-pfull2` are the pools of solvent-b), `.jsonl.gz` the lines with the
  moves, `.log` the commands; [moniot-baseline.json](runs/heur/moniot-baseline.json) is the cost of one moniot process
  on game 2 (1.7 to 2.9 ms, in every game of that program).  [runs/unsound/](runs/unsound/) has the unsound mode's
  lines of 5061-5160; [runs/jobs.log](runs/jobs.log) the queue's starts and ends with the load.  The lines of the
  unsound mode on 4561-5060 are E2's, in [its runs](../the-datasheet-of-the-unsound-mode-2026-11/runs/).

No code of the main repository changed.  The code run is that of commit
[50db88e](https://github.com/bvchess/taxman/commit/50db88e).
