# The datasheet of the unsound mode (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  The unsound mode plays a range of games with no proof, at a level of effort from 0 to 7.  Played as a user
plays it, as chains of 100 games over the top of the known games 4561-5060 (each game starting from the run's own line of
the game before), what share of the games gets opt(n) at each level, how far short are the others, how long does a
shortfall last, and how long does a level take, on 4 threads and on more?  The options are `--back 8 --tilt 25 --widen 4`,
which [race R1](../a-share-of-tilted-neighborhoods-2026-11/README.md) chose.

**Answer.**  The chains score opt(n) in 5.6, 89.0, 94.2, 95.8, 97.2, 97.2, 97.2 and 98.8% of the 500 games at levels 0 to
7, in 0.05, 0.10, 0.15, 0.24, 0.42, 0.77, 1.4 and 2.5 hours for 100 games alone on 4 threads (0.01 to 0.59 hours on 64
threads); the proven mode took a mean 19.4 hours for 100 games on 88 threads (0.65 to 79.7 by segment).  The share stops
growing after level 4: levels 5 and 6 add nothing, and level 7 adds 1.6 points by repairing two stuck games.  The chain
starts no shortfall of its own: every streak of short games starts at a game that is also short when played alone from the
proven game before it.  But 81 to 87% of the short games are handed on from the game before, a streak lasts a median 3 to 7
games within a segment, and the streak of game 4950 lasts 18 to 50 games when the chain is played on.  Against games
seeded with proven games, a chain of 100 games costs 1.0 point at level 7 (5 games), 2.2 to 2.4 at levels 4 to 6 and 9.6
at level 1.  The top level should stay at 7: level 8 on 64 threads takes about what the proven mode takes for n up to
4860.  A replay from the moves of n + 1 would have found none of the 91 shortfalls counted at levels 2 to 7.  It is one
seed and five segments.

## Method

*The mode.*  A game of the unsound mode
([unsound.rs](https://github.com/bvchess/taxman/blob/a2a1a2e/solver/frame/src/solver/unsound.rs); [REFERENCE, "An unsound
line"](https://github.com/bvchess/taxman/blob/a2a1a2e/solver/docs/REFERENCE.md#an-unsound-line) has the keys of a line)
is a prime formula, a repeat of an earlier line's promotions, or a `search`: the start of a proven search seeded with the
moves for n − 1, then rounds of 64 neighborhoods of large neighborhood search.  Effort E is a budget of work, 2^(E−1) ×
65,536 (the steps of the rounds and 32 for each neighborhood), and effort 0 is the start alone.  A searched game stops at
the run's ceiling, n + score(n − 1) of the moves it starts from.  `--back 8` adds a trajectory for each distinct set that
survives of the moves for n − 1 to n − 8, `--tilt 25` frees the small promotions more often in 25% of the neighborhoods,
and `--widen 4` moves a trajectory to larger neighborhoods after 4 rounds with no growth.

*The build.*  Master [a2a1a2e](https://github.com/bvchess/taxman/commit/a2a1a2e), release without fat LTO
(`profile.release.lto=false`, `codegen-units=16`), built at -j 4.  Every line records `"build": {"commit":
"a2a1a2e...", "dirty": false}`.  Master moved on to [50db88e](https://github.com/bvchess/taxman/commit/50db88e) while the
study ran: it makes the three options the defaults and changes nothing else in the rounds, so the datasheet is also that
of `taxman solve LO-HI --unsound --effort E` at 50db88e.

*Part 1: the chains.*  Five segments of 100 games (4561-4660, ..., 4961-5060), each at each level 0 to 7: 40 runs of

    taxman solve LO-HI --unsound --effort E --back 8 --tilt 25 --widen 4 --seed 1 --threads T --out FILE

with T = 4, and 8 at effort 7, and five more at effort 4 with `--past-ceiling`, to measure what the stop at the ceiling
costs.  There is no `--from-known` and no `--stop-at-known`: the first game of a run starts from the built-in table's
game LO − 1 (`prev.source` is `table`) and every later one from the run's own line (`run`), and a game plays its whole
budget unless it reaches its ceiling.  Each run has a file of its own.  [run_chains.py](run_chains.py) ran the 45 runs from
a queue, longest first, starting a run when its threads fit under 80 beside the running ones, at nice 19, from 01:27 to
04:47 on 2026-11-07 (Pacific time), 230 thread-hours.  The load average was 72 to 81 from about 01:35 to 04:10 and fell to
7 as the last runs ended.  I had estimated 0.15 ms of wall time a unit of work on 4 threads, 8 s for a start and 46% of the games searched, which makes
effort 7 on 4 threads about 8 hours a run.  The runs gave 0.10 to 0.12 ms, a median 6.5 to 7.2 s, 235 of 500 searched (47%),
and 3.3 hours for the longest run (effort 7 over 4861-4960 on 8 threads).

*Part 1b: the chain played on.*  A streak that reaches the end of a segment is cut there, since the next segment starts from
the table.  At levels 1 to 6 the streak that starts at game 4950 reaches 4960, so [run_continue.py](run_continue.py) copies
each such run's file for 4861-4960 to a file of its own and plays 4961-5060 on it, game 4961 starting from the line of 4960
(`prev.source` is `results`, the file's).

*Part 2: the threads.*  Games 4752, 4864 and 5016 at effort 5 with `--from-known --threads T` for T = 4, 8, 16, 32 and 64
([run_threads.py](run_threads.py)), one run at a time with nothing else of mine beside it (04:47 to 04:58).  The same script
then ran 15 more games, 3 in each segment (searched, run to their budget, after 8 games at opt(n)), alone on 4 threads (05:00
to 05:22), to compare the chain's seconds with an idle machine's.  `threads/threads.log` shows one to three running tasks at each start.

*The analysis* ([analyze.py](analyze.py); its output is [out.txt](out.txt)) checks every line and computes every number
below.  A game is short by opt(n) − score, with opt(n) from `results/optimal.jsonl.gz`.  A short game is *own* if the game
before it is at opt(n − 1), and *handed on* if the game before it is short too.  A *streak* is a stretch of consecutive
short games.  The *load factors* are the chain's seconds over the same game's alone; an *alone* time divides the chain's
seconds by them and converts thread counts by Part 2's speedups.  The race's lines are R1's arm `--tilt 25 --back 8 --widen
4` for its 65 hard games of 4561-5060, each played alone from its proven game of n − 1 at effort 7 with `--stop-at-known`,
on master 8dc6500.

## Results

**1. The lines pass the checks.**  All 5,730 checked lines (4,500 of Part 1, 30 of Part 2 and 1,200 of Part 1b, which
repeat Part 1's 600) are unsound, from build a2a1a2e (not dirty), at their effort and budget, with the study's options,
seed 1, their threads and neither measuring option; no score is above the table's; the first game of each run has
`prev.source` `table` (in Part 1b, game 4961 has `results`) and every later one `run`, with `prev.score` the score of the
line before it; a searched game's `work` is its steps plus 32 for each neighborhood; a searched game with work below its
budget is at its ceiling; and a game at its ceiling after a game at opt(n − 1) is at opt(n).  The lines of a game agree on
every thread count but for their seconds (12 comparisons).  Of the 65 hard games, 63 have at effort 7 the improvements of
the race's line through its stop, and the other 2 follow a short game.

**2. The share of optimal scores.**  Games at opt(n), of 100 a segment and 500 in all:

| effort | work | 500 games | 4561-4660 | 4661-4760 | 4761-4860 | 4861-4960 | 4961-5060 |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 28 (5.6%) | 15 | 1 | 0 | 3 | 9 |
| 1 | 65,536 | 445 (89.0%) | 100 | 100 | 93 | 59 | 93 |
| 2 | 131,072 | 471 (94.2%) | 100 | 100 | 100 | 75 | 96 |
| 3 | 262,144 | 479 (95.8%) | 100 | 100 | 100 | 83 | 96 |
| 4 | 524,288 | 486 (97.2%) | 100 | 100 | 100 | 89 | 97 |
| 5 | 1,048,576 | 486 (97.2%) | 100 | 100 | 100 | 89 | 97 |
| 6 | 2,097,152 | 486 (97.2%) | 100 | 100 | 100 | 89 | 97 |
| 7 | 4,194,304 | 494 (98.8%) | 100 | 100 | 100 | 94 | 100 |
| 4, past the ceiling | 524,288 | 486 (97.2%) | 100 | 100 | 100 | 89 | 97 |

By the method of the proven run (170 `search`, 62 `start`, 60 `prime` and 208 `repeat` games):

| effort | search | start | prime | repeat |
|---|---|---|---|---|
| 0 | 6 (3.5%) | 3 (4.8%) | 5 (8.3%) | 14 (6.7%) |
| 1 | 149 (87.6%) | 59 (95.2%) | 52 (86.7%) | 185 (88.9%) |
| 2 | 159 (93.5%) | 59 (95.2%) | 57 (95.0%) | 196 (94.2%) |
| 3 | 162 (95.3%) | 60 (96.8%) | 57 (95.0%) | 200 (96.2%) |
| 4, 5, 6 | 164 (96.5%) | 61 (98.4%) | 58 (96.7%) | 203 (97.6%) |
| 7 | 167 (98.2%) | 62 (100%) | 59 (98.3%) | 206 (99.0%) |

* **Effort 0 collapses in a chain.**  The start alone is short in some game of every segment and nothing repairs it: every
  later prime and repeat copies the short line and every later search starts from it, so 5 streaks cover 472 of the 500 games.
* **Levels 1 to 4 climb, 5 and 6 stand still, 7 steps up.**  The same 14 games are short at levels 4, 5 and 6 and with
  `--past-ceiling` (4950 to 4960 and 5040 to 5042); level 7 has 6 short (4950 to 4955).  All the shortfalls of levels 2 to 7
  lie in 4861-5060, and the first 300 games are at opt(n) from level 2 on.
* **The methods of the proven run do alike**, within two points, since a short line spreads to all of them.  The three games
  that the proven run played as repeats and this run searched (4562, 4661 and 4862) repeat a game before their segment,
  where the run has no line.

**3. The shortfalls and how they run in a chain.**

| effort | short | own | handed on | size: median / 90th / max | streaks | length: median / max | ended by a search / the end of the segment |
|---|---|---|---|---|---|---|---|
| 0 | 472 | 5 | 467 | 267 / 659 / 1,957 | 5 | 97 / 100 | 0 / 5 |
| 1 | 55 | 7 | 48 | 140 / 196 / 254 | 7 | 3 / 30 | 5 / 2 |
| 2 | 29 | 4 | 25 | 140 / 143 / 176 | 4 | 7 / 14 | 2 / 2 |
| 3 | 21 | 4 | 17 | 106 / 143 / 176 | 4 | 4.5 / 11 | 2 / 2 |
| 4 | 14 | 2 | 12 | 93 / 143 / 176 | 2 | 7 / 11 | 1 / 1 |
| 5 | 14 | 2 | 12 | 93 / 143 / 176 | 2 | 7 / 11 | 1 / 1 |
| 6 | 14 | 2 | 12 | 88 / 132 / 176 | 2 | 7 / 11 | 1 / 1 |
| 7 | 6 | 1 | 5 | 79 / 79 / 79 | 1 | 6 / 6 | 1 / 0 |

* **A short game is a handed-on one in 81 to 87% of the cases** at levels 1 to 7 (48 of 55, 25 of 29, 17 of 21, 12 of 14 and
  5 of 6) and in 99% at level 0.  A shortfall is a tail behind a stuck game, not a set of independent misses.
* **The sizes are small**: a median 79 to 140 points at levels 1 to 7 and at most 254, 32 parts per million of a score near
  8 million.  At level 4 the 7 prime and repeat games after a short game copy its size, and of 6 searched games 3 keep it,
  1 reduces it, 1 enlarges it and 1 reaches opt(n).
* **A prime or a repeat hands the shortfall on every time** (0 recoveries in the 81 that follow a short game, counted by level
  for levels 1 to 7), and a searched game recovers 5 of 22 at level 1, 2 of 12 at level 2, 2 of 8 at level 3, 1 of 6 at
  levels 4 to 6 and 1 of 3 at level 7.
* **Where a streak ends.**  A searched game that reaches opt(n) ends 5 of the 7 streaks of level 1, 2 of 4 at levels 2 and 3,
  1 of 2 at levels 4 to 6, and the one of level 7.  The others reach the end of their segment: 4950's at levels 1 to 6 and
  5060's, the last game, at levels 1 to 3.  The longest are 4914's 30 games at level 1 (110 points short at the start, repaired
  by the search of 4944) and 4950's 11 games at levels 1 to 6 (132 to 222 points short at the start, 176 at 4960).
* **Every streak starts at a game that is short alone.**  The 7, 4, 4, 2, 2, 2 and 1 streaks of levels 1 to 7 start at hard
  games that the race's line, seeded with the proven game, does not bring to opt(n) within the level's work (by its lower
  bound): 4840, 4851, 4914, 4950, 4992, 5040 and 5060 at level 1, 4914, 4950, 5040 and 5060 at levels 2 and 3.  None of the
  435 games that are not hard in the race starts a streak.  So the chain adds no stuck games; it adds the tail behind each.

**3b. The streak of 4950 played on.**  Part 1 cuts the streak that starts at game 4950 at the end of its segment, 4960, at
levels 1 to 6.  With the chain played on into 4961-5060 (Part 1b):

| effort | the streak that starts at 4950 | short games in 4961-5060: Part 1, then played on | games at opt(n) of the 200 of 4861-5060: Part 1, then played on |
|---|---|---|---|
| 1 | 50 games, ended by the search of 5000 | 7, 43 | 152 (76.0%), 116 (58.0%) |
| 2 | 42 games, ended by the search of 4992 | 4, 35 | 171 (85.5%), 140 (70.0%) |
| 3 | 42 games, ended by the search of 4992 | 4, 35 | 179 (89.5%), 148 (74.0%) |
| 4 | 18 games, ended by the search of 4968 | 3, 10 | 186 (93.0%), 179 (89.5%) |
| 5 | 18 games, ended by the search of 4968 | 3, 10 | 186 (93.0%), 179 (89.5%) |
| 6 | 33 games, ended by the search of 4983 | 3, 25 | 186 (93.0%), 164 (82.0%) |

* **The tail behind a stuck game is longer than a segment shows**: 18 to 50 games at levels 1 to 6, where the segment cut it
  at 11.  A later game repairs it when its start or rounds find opt(n) (the start of 4992 was at opt(n)), and more effort
  does not shorten the tail (33 games at level 6, against 18 at level 4 and 50 at level 1).
* **A longer run loses more.**  Played on, the 200 games of 4861-5060 hold 7 to 36 more short games than two segments do (the
  scores of 39 games of 4961-5060 differ from Part 1's at level 1, 31 at levels 2 and 3, 7 at levels 4 and 5, 22 at level 6).  The shares of
  the datasheet are those of runs of 100 games from a proven game.
* **No line of Part 1b shows the line before it short** (`prev.short_by` is 0 in all its games of 4961-5060).

**4. The run's ceiling.**  Searched games and their ceiling, of the 235 searched games of each level:

| effort | at the ceiling | of those below opt(n) | not at it, below opt(n) | not at it, at opt(n) | `prev.short_by` above 0 |
|---|---|---|---|---|---|
| 0 | 68 | 63 | 160 | 7 | 6 |
| 1 | 64 | 3 | 21 | 150 | 1 |
| 2 | 64 | 3 | 11 | 160 | 0 |
| 3 | 64 | 2 | 8 | 163 | 0 |
| 4 | 64 | 1 | 6 | 165 | 0 |
| 5 | 64 | 1 | 6 | 165 | 0 |
| 6 | 64 | 1 | 6 | 165 | 0 |
| 7 | 64 | 0 | 3 | 168 | 0 |

* **The stop loses almost nothing.**  64 searched games stop at their ceiling at every level from 1 up, a quarter of the
  searched games, and 3, 3, 2, 1, 1, 1 and 0 of them (levels 1 to 7) stop below opt(n) because the line before was short:
  4917, 4923 and 4959 at levels 1 and 2, 4917 and 4959 at level 3, 4959 at levels 4 to 6.
* **`--past-ceiling` at effort 4 changes no score.**  The same 14 games are short, and no game passed n + score(n − 1)
  (`prev.short_by` is 0 in all 235), so no line of n − 1 was shown short.  The run takes 37% more work (133.1 against 97.0
  million) and 31% more seconds (0.95 hours per 100 games against 0.72 on the busy machine).
* **At effort 0 the ceiling is wrong** for 63 of its 68 stopped games: the start alone reaches a ceiling made from a short line.

**5. Time.**  Seconds and hours as measured, with up to 80 threads busy on the machine's 44 cores (a prime or repeat game
takes 0.1 to 0.5 s, and the median of all 500 games is 0.5 s at every level, so the table gives the median of the 235
searched games, the ones that cost):

| effort | threads | median searched game, s | 90th percentile of the 500, s | start, s summed | rounds, s summed | hours per 100 games | by segment |
|---|---|---|---|---|---|---|---|
| 0 | 4 | 6.7 | 7.7 | 1,510 | 119 | 0.09 | 0.06 0.08 0.10 0.11 0.11 |
| 1 | 4 | 14.0 | 16.8 | 1,660 | 1,569 | 0.18 | 0.14 0.16 0.19 0.21 0.20 |
| 2 | 4 | 21.6 | 26.4 | 1,672 | 3,026 | 0.26 | 0.18 0.23 0.26 0.33 0.30 |
| 3 | 4 | 35.1 | 43.9 | 1,681 | 5,629 | 0.41 | 0.27 0.36 0.41 0.51 0.47 |
| 4 | 4 | 61.8 | 83.9 | 1,701 | 11,293 | 0.72 | 0.46 0.60 0.72 0.97 0.86 |
| 5 | 4 | 116.4 | 160.5 | 1,739 | 22,305 | 1.34 | 0.83 1.14 1.29 1.82 1.60 |
| 6 | 4 | 216.9 | 303.5 | 1,691 | 42,375 | 2.45 | 1.52 2.12 2.43 3.21 2.95 |
| 7 | 8 | 231.1 | 317.1 | 913 | 44,903 | 2.55 | 1.61 2.27 2.51 3.33 3.01 |
| 4, past the ceiling | 4 | 70.9 | 85.6 | 1,713 | 15,361 | 0.95 | 0.67 0.82 0.96 1.19 1.10 |

* **Time doubles per level** from level 2 on (rounds: 3,026, 5,629, 11,293, 22,305 and 42,375 s), and a unit of work takes
  much the same at every level: 103 to 119 s per million work on 4 threads (pooled), rising with n from 88 s over 4561-4660
  to 144 s over 4861-4960 at effort 5.  The start takes a median 6.5 to 7.2 s, and 3.8 s on 8 threads.
* **The busy machine is 1.7 to 1.8 times slower than an idle one.**  For the 18 games that ran alone at effort 5 on 4 threads
  (the same score and work as in the chain), the chain's seconds were a median 1.78 times those alone for the start (range
  1.54-1.98) and 1.73 for the rounds (1.68-1.83).  The last four runs (efforts 6 and 7 over 4861-4960 and 4961-5060) spent
  their final 6 to 17% on a machine that was emptying, after 04:14.
* **The proven mode over the same stretch** took 1.44, 0.65, 2.26, 12.93 and 79.74 hours of wall time for the five segments on
  88 threads with up to four games at once: a mean of 19.4 hours for 100 games (30.5 if the games' seconds are summed), and a
  mean of 1,673 CPU hours (122, 44, 169, 1,115 and 6,913).  Its searched games took a median 387 s and a 90th percentile of
  6,116 s.  This shows what a proof of these games cost in the run of 2026-11-01 to 11-06.  It does not show what the proven
  mode costs on a small machine or alone on a big one; the line of game 5000 has 499 s active and 5,730 s waiting of its 6,228 s.

**6. More threads.**  Games 4752, 4864 and 5016 at effort 5, alone (their lines are the same on every thread count), summed:

| threads | start, s | rounds, s | speedup of the start | speedup of the rounds | efficiency of the rounds |
|---|---|---|---|---|---|
| 4 | 12.4 | 248.5 | 1.00 | 1.00 | 1.00 |
| 8 | 7.2 | 148.1 | 1.72 | 1.68 | 0.84 |
| 16 | 4.5 | 88.1 | 2.76 | 2.82 | 0.71 |
| 32 | 2.7 | 65.2 | 4.61 | 3.81 | 0.48 |
| 64 | 2.1 | 59.9 | 5.87 | 4.15 | 0.26 |

Efficiency is the speedup over threads / 4.  The rounds of a game take 69 to 93 s on 4 threads and 17 to 23 s on 64, a speedup
of 3.97, 4.12 and 4.33.  A round of 64 neighborhoods cannot use more than 64 threads and ends with its slowest neighborhoods,
which fits a speedup that flattens at 32 threads (not measured).  The levels on other thread counts, alone, in hours per 100
games (the chain's seconds divided by the load factors and converted by these speedups):

| effort | 4 threads | 8 | 16 | 32 | 64 |
|---|---|---|---|---|---|
| 0 | 0.05 | 0.03 | 0.02 | 0.02 | 0.01 |
| 1 | 0.10 | 0.06 | 0.04 | 0.03 | 0.03 |
| 2 | 0.15 | 0.09 | 0.06 | 0.04 | 0.04 |
| 3 | 0.24 | 0.14 | 0.09 | 0.06 | 0.06 |
| 4 | 0.42 | 0.25 | 0.15 | 0.11 | 0.10 |
| 5 | 0.77 | 0.46 | 0.28 | 0.20 | 0.19 |
| 6 | 1.41 | 0.84 | 0.50 | 0.37 | 0.34 |
| 7 | 2.46 | 1.47 | 0.88 | 0.65 | 0.59 |

**7. The datasheet.**  The times are alone and estimated, as in the table above (the row of effort 7 converts the 8-thread
run to 4 threads by 1.68):

| effort | share of optimal scores | median searched game, 4 threads | hours per 100 games, 4 threads | hours per 100 games, 64 threads |
|---|---|---|---|---|
| 0 | 5.6% | 3.8 s | 0.05 | 0.01 |
| 1 | 89.0% | 8.0 s | 0.10 | 0.03 |
| 2 | 94.2% | 12 s | 0.15 | 0.04 |
| 3 | 95.8% | 20 s | 0.24 | 0.06 |
| 4 | 97.2% | 36 s | 0.42 | 0.10 |
| 5 | 97.2% | 67 s | 0.77 | 0.19 |
| 6 | 97.2% | 125 s | 1.41 | 0.34 |
| 7 | 98.8% | 224 s | 2.46 | 0.59 |
| proven mode | 100% | 387 s (88 threads) | 19.4 (88 threads; 0.65 to 79.7 by segment) | |

![The share of optimal scores against the hours per 100 games, a point per level, with the proven mode marked](datasheet.svg)

* **More effort stops paying after level 4.**  Levels 1 to 4 add 83.4, 5.2, 1.6 and 1.4 points, levels 5 and 6 add 0.0, and
  level 7 adds 1.6: the repair of two stuck games (5040, and 4950 from 11 games short to 6).  Level 4 costs 0.42 hours per 100
  games on 4 threads and level 7 costs 2.46.
* **The unsound mode's time reaches the proven mode's at about level 8 on a big machine.**  Level 7 on 64 threads takes 0.38,
  0.53, 0.59, 0.78 and 0.70 hours for the five segments, and level 8 would take twice that; the proven mode took 1.44, 0.65,
  2.26, 12.93 and 79.74.  So level 8 on 64 threads costs about what a proof of 4561-4860 costs on 88 threads, while level 7 on
  4 threads (1.56 to 3.22 hours) already takes as long as the proven mode on 88 for the first three segments (level 7 in
  4561-4660 and 4761-4860, level 5 in 4661-4760).  By CPU hours the proven mode costs 20, 5, 17, 87 and 594 times level 7's
  thread hours (6.2, 8.8, 9.7, 12.9 and 11.7 on 4 threads, against 122, 44, 169, 1,115 and 6,913), which doubling the time a
  level would match at levels 11, 9 and 11 for n up to 4860 and at 13 and 16 beyond.
* **The top level is 7.**  A user with many threads who asks for more than level 7 is about as well served by the proven mode up to
  4860, which gives a proof.  No level above 7 was measured, and each level costs twice the one below it and buys a stuck game
  at best.

**8. The chain against games seeded with proven games.**  The 65 hard games of the race among the 500, and all 500 (the 435
others held the known score at the start in the proven run, and are taken as at opt(n) when seeded; none starts a streak in
the chain):

| effort | hard games: race | hard games: chain | 500 games: race | 500 games: chain | cost of the chain | hard games lost / gained |
|---|---|---|---|---|---|---|
| 0 | 23 (35.4%) | 1 (1.5%) | 458 (91.6%) | 28 (5.6%) | 86.0 points | 22 / 0 |
| 1 | 58 (89.2%) | 52 (80.0%) | 493 (98.6%) | 445 (89.0%) | 9.6 | 6 / 0 |
| 2 | 61 (93.8%) | 59 (90.8%) | 496 (99.2%) | 471 (94.2%) | 5.0 | 2 / 0 |
| 3 | 61 (93.8%) | 59 (90.8%) | 496 (99.2%) | 479 (95.8%) | 3.4 | 2 / 0 |
| 4 | 62 (95.4%) | 61 (93.8%) | 497 (99.4%) | 486 (97.2%) | 2.2 | 2 / 1 |
| 5 | 63 (96.9%) | 61 (93.8%) | 498 (99.6%) | 486 (97.2%) | 2.4 | 2 / 0 |
| 6 | 63 (96.9%) | 61 (93.8%) | 498 (99.6%) | 486 (97.2%) | 2.4 | 2 / 0 |
| 7 | 64 (98.5%) | 62 (95.4%) | 499 (99.8%) | 494 (98.8%) | 1.0 | 2 / 0 |

* **The chain costs 1.0 to 9.6 points at levels 1 to 7**: 48, 25, 17, 11, 12, 12 and 5 games.  Every hard game that the chain
  loses follows a short game, and so does every short game among the 435 others (3 to 42 of them at levels 1 to 7).
* **The race's row is a lower bound** (a game counts when its improvement came within the level's work, as in R1).  In the 434
  game-levels of the 65 hard games where the chain's line is the race's line, the bound and the chain's exact result differ
  in 1 (game 5060 at effort 4, which the chain reaches in the round that crosses the budget).
* **On the hard games the chain is within 1 or 2 games of the race from level 2 up**; at level 1 it is 6 games and 9.2 points
  behind, and at level 0 it has 1 of the race's 23.

## What this means for the unsound mode

* **The datasheet is section 7.**  A user who names a level gets that share of optimal scores on games like these, in that
  time on an idle machine, with a tail behind each stuck game.  Level 1 is the first usable level in a chain (89%), level 4
  gets 97.2% in 0.42 hours per 100 games on 4 threads, and level 7 gets 98.8%.
* **Stop the top level at 7.**  The share does not grow at levels 5 and 6, level 7's gain is two games, and at level 8 the time
  on 64 threads reaches the proven mode's for n up to 4860, which gives a proof.  The proven mode's cost rises steeply with n
  (13 and 80 hours for the last two segments), so for larger n the level where the times meet is higher than 7; the limit is
  set by the share, which has little room left to grow.
* **The chain's cost is a tail behind stuck games, not a loss in each game.**  No game starts a streak that it would not start
  alone; 81 to 87% of the short games copy a shortfall that began at a stuck game, and the tail behind one lasts a median 3 to
  7 games in a segment and 18 to 50 when played on.  The share depends on how many stuck games a run meets and how soon a
  later search repairs each, so a longer run shares less (section 3b), and no level removes the tail.
* **Replaying a game from the moves of n + 1 is not worth building**, because the evidence it needs does not appear.  The
  line of n + 1 showed the game before it short in none of the 91 short games counted at levels 2 to 7 (1 of 53 at level 1 and
  6 of 467 at level 0), nor in Part 1b: a short line is passed on, and the next game's score stays under its own ceiling.  A
  perfect game n + 1 would have shown 4 of the 13 shortfalls at level 4, and `--past-ceiling` found none.  Nor does a stuck
  game's line show it: at level 7, 42 of 168 searched games at opt(n) that ran their whole budget improved in their rounds
  against 1 of 3 short.  What would help is more search on a stuck game (4950 is 143 short at levels 4 and 5, 132 at 6 and 79
  at 7); [P1](../the-unsound-mode-on-the-hard-games-2026-11/README.md) found that a second seed recovers one stuck game in
  seven.
* **What is left**: 4950 (79 short at level 7, handing on 5 games), the other stuck games of the race, and the range past 5060.

## What the data cannot tell

* **One seed, five segments, and few events.**  The streaks are the independent events: 7, 4, 4, 2, 2, 2 and 1 at levels 1 to
  7, all in 4861-5060 from level 2 on.  Level 7's gain over level 4 is the luck of two games, the shares of levels 4 to 6 are
  the same 14 games, and the tails of Part 1b vary from 18 to 50 games with no order in the level.  No interval on the 500
  games would mean anything.
* **A run of 100 games from a proven game is the unit of the datasheet.**  A longer run meets more stuck games and drags
  their tails (82 to 90% of 200 games at levels 4 to 6 against 93%, section 3b); a run of a thousand is not measured.
* **The known range stands in for the unknown games.**  The stuck games lie in the top two segments (4914, 4950, 5040, 5060),
  so the share past 5060 may be lower, and the proven mode's cost rises faster than the unsound mode's.
* **The times are those of a shared machine**, corrected by a factor from 18 games at effort 5 on 4 threads and applied to every
  level and thread count.  Part 2 has three games at one effort, and the rows for 8 to 64 threads are conversions, not runs.
  The row of effort 7 converts a run on 8 threads by an alone speedup (1.68), while the runs of efforts 6 and 7 on the busy
  machine, over the same segments, give 1.81 to 1.90; the row may be 10% low (twice effort 6's time is 2.8 hours).
* **The proven mode's seconds come from another run** (build aaba59b, 88 threads, up to four games at once, 2026-11-01 to
  11-06), so the comparison is one of orders of magnitude.
* **The race's lines are a lower bound at each level's budget** and come from build 8dc6500; the chain's lines are those of
  a2a1a2e, with the same rounds (63 of 65 lines agree at effort 7).

## Open

* The chains with a second and a third seed, to see whether 4950 and 5040 are the only stuck games of 4561-5060.
* Effort 7 on 4 threads, to replace the conversion, and levels 8 and 9.  Runs of 1,000 games, and the range past 5060.

## Files

* [run_chains.py](run_chains.py): the 45 runs of Part 1 from a queue.  `nice -n 19 python3 -I run_chains.py --bin TAXMAN
  --dir runs/`.  [runs/](runs/) holds `eE-LO.jsonl.gz` (the lines, with the moves) and `eE-LO.log` of each run (`e4pc-LO` for
  effort 4 past the ceiling), and `jobs.log`, the queue's starts and ends with the load.
* [run_continue.py](run_continue.py): Part 1b.  `nice -n 19 python3 -I run_continue.py --bin TAXMAN --runs runs/ --dir
  continue/`.  [continue/](continue/) holds `cont-eE.jsonl.gz` (the 100 lines of 4861-4960 copied from `runs/` and the 100 of
  4961-5060) and the logs.
* [run_threads.py](run_threads.py): Part 2 and the 15 games alone.  `nice -n 19 python3 -I run_threads.py --bin TAXMAN --dir
  threads/`, and the same with `--games` and `--threads 4` for the 15.  [threads/](threads/) holds `threadsN-T.jsonl.gz`, the
  logs and `threads.log`.
* [analyze.py](analyze.py): the checks of the lines, every number above and the chart.  `nice -n 19 python3 -I analyze.py >
  out.txt`, with `--results` the path of `results/optimal.jsonl.gz` if the notebook is not at `solver/notebook/`;
  [out.txt](out.txt) is its output and [datasheet.svg](datasheet.svg) the chart.  It reads R1's lines `k25w4-*.jsonl` from
  [R1's entry](../a-share-of-tilted-neighborhoods-2026-11/README.md).

No code of the main repository changed.  The code run is that of commit
[a2a1a2e](https://github.com/bvchess/taxman/commit/a2a1a2e).
