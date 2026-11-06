# The unsound mode on the hard games (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-06.  Concluded 2026-11-06.

**Question.**  On the hard games of 3441-5060, how many does the first form of the unsound mode (`taxman solve --unsound
--effort E`) bring to the known score within 256 rounds, at which round, and does a second seed reach the games the
first misses?  The answer says whether the mode is ready for E1, the planned run of the whole machine, or which
technique the games it misses call for.

**Answer.**  Each seed brings 56 of the 63 sampled games (88.9%) to the known score within 256 rounds, and the better of
the two seeds 57 (90.5%).  By the sample, the mode holds the known score in an estimated 95.1% of the 568 searched
games of 3441-5060 with one seed (90% interval 91.2-97.6%), against 71.9% (67.5-76.8%) for the start alone.  Most of the
gain comes in the first rounds: 8 rounds (effort 4) reach 71% of the sample with either seed, 32 rounds 78% to 82.5%.
The misses are stuck, not short of time: of the 7 games each seed missed, 5 (seed 1) and 6 (seed 2) had made their last
improvement by round 16, 6 games are missed by both seeds and end at the same score under both, and a second seed
recovers one game of seven.  The mode is ready for
the cheap levels; for the top levels the games it misses call for a different neighborhood or a restart, which a test
on 13 games can examine before E1.

## Method

*The mode.*  A game of the mode ([unsound.rs](https://github.com/bvchess/taxman/blob/e37d6a1/solver/frame/src/solver/unsound.rs))
makes the start of a proven search, seeded with the moves for n − 1, and then plays rounds of large neighborhood
search ([finder.rs, "On many threads, alone"](https://github.com/bvchess/taxman/blob/e37d6a1/solver/frame/src/search/finder.rs)).
A round is 64 neighborhoods.  Each keeps a random 70-90% of the incumbent's promotions fixed, searches the rest exactly
for at most 1,024 steps, and the best set of the round becomes the incumbent.  Effort 0 is the start alone and effort E
is 2^(E−1) rounds, so a run at E does the rounds of E − 1 first.  A line records the start, the rounds that raised the
score, the rounds done, the steps and the seconds
([REFERENCE, "An unsound line"](https://github.com/bvchess/taxman/blob/e37d6a1/solver/docs/REFERENCE.md#an-unsound-line)).
`--from-known` seeds each game with the proven moves for n − 1, and `--stop-at-known` ends a game at the score of
the built-in table, the known score, and records the round at which it held it.

*The build.*  Master e37d6a1, release without fat LTO (`profile.release.lto=false`, `codegen-units=16`), built in 2 min
54 s.  Every one of the 126 lines records `"build": {"commit": "e37d6a1...", "dirty": false}`.

*The games.*  The entry [where the best scores came from](../where-the-best-scores-came-from-2026-11/README.md) (E0)
found that in the run of 2026-11-01 the start held the best score in 317 of the 568 searched games of 3441-5060, and
fell short in the other 251.  [select_games.py](select_games.py)
takes those 251, sorts them by n and keeps every 4th from the first: 63 games, 3441 to 5043.  [sample.json](sample.json)
has them with E0's numbers (the best score as a promotion sum `opt`, the run's start, the source of the best score, the
run's finder), and [games.txt](games.txt) the n alone.

*The runs.*  On 2026-11-06, 13:03 to 13:25 PST, on the machine of 88 threads that runs the prover on every thread at
idle priority: two processes at once, one a seed, each on 4 threads at nice 19, each game one command

```
taxman solve N --unsound --effort 9 --from-known --stop-at-known --seed S --threads 4 --out seed-S.jsonl
```

for S = 1 and S = 2 ([run_seed.py](run_seed.py) loops over the games; [seed-1.log](seed-1.log) and
[seed-2.log](seed-2.log) have its commands and the summary line of each game).  Effort 9 is 256 rounds.

*The analysis* ([analyze.py](analyze.py), whose output is [out.txt](out.txt)) checks the lines, then computes: per game,
the round at which each seed held the known score (`stop_at_known.round`), the round of its last improvement, its final
shortfall, its seconds and its steps per neighborhood (`steps` over `neighborhoods`); the share of the sample at the
known score after 0, 1, 2, 4, ..., 256 rounds, from the start and the improvements of each line; the estimate for the
568 games, (317 + 251 × the sample's share) / 568, with the exact binomial 90% interval (Clopper-Pearson) of the share;
and the costs.  The shortfall of a game is the known score less its score, in points.

## Results

**1. The lines pass the checks, and the start is stronger than E0's.**

* All 126 lines have method `search`, effort 9, 4 threads, `from_known`, the table as the source of the moves for
  n − 1 (none proves the game before short), and no score above the table's.
* The two seeds differ only after the start: the start, `in_the_bag` and the setup are the same in all 63 games.
* **The start agrees with E0's in 34 games and is higher in 29, never lower.**  In 23 of the 29, the start from the
  proven game of n − 1 already holds the known score (3441's start was 123 short in the run); in 6 it is higher and still
  short (3531: 198 to 54; 3850: 223 to 18; 4446: 378 to 82; 4664: 127 to 103; 4761: 98 to 49; 5024: 335 to 242).  The
  run of 2026-11-01 ran a window of 4 games, and a game there started from the best moves so far of the game before it,
  which were not yet the proven ones.  That probably explains the difference; it was not tested here.

**2. The curve.**  The share of the 63 games at the known score after R rounds, per seed and for the better of the two,
and for the games left short their median and maximum shortfall in points:

| effort | rounds | seed 1 | short: median / max | seed 2 | short: median / max | better of two | short: median / max |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 23 (36.5%) | 86 / 1957 | 23 (36.5%) | 86 / 1957 | 23 (36.5%) | 86 / 1957 |
| 1 | 1 | 32 (50.8%) | 97 / 1523 | 30 (47.6%) | 82 / 872 | 35 (55.6%) | 95.5 / 872 |
| 2 | 2 | 36 (57.1%) | 94 / 779 | 37 (58.7%) | 79.5 / 665 | 41 (65.1%) | 79.5 / 665 |
| 3 | 4 | 40 (63.5%) | 64 / 321 | 43 (68.3%) | 64.5 / 289 | 44 (69.8%) | 64 / 289 |
| 4 | 8 | 45 (71.4%) | 51.5 / 221 | 45 (71.4%) | 59 / 271 | 46 (73.0%) | 54 / 221 |
| 5 | 16 | 50 (79.4%) | 56 / 180 | 47 (74.6%) | 55 / 180 | 51 (81.0%) | 55 / 180 |
| 6 | 32 | 52 (82.5%) | 56 / 147 | 49 (77.8%) | 60 / 180 | 53 (84.1%) | 55 / 147 |
| 7 | 64 | 52 (82.5%) | 54 / 147 | 52 (82.5%) | 56 / 110 | 54 (85.7%) | 54 / 97 |
| 8 | 128 | 54 (85.7%) | 56 / 147 | 56 (88.9%) | 54 / 97 | 57 (90.5%) | 36 / 97 |
| 9 | 256 | 56 (88.9%) | 54 / 97 | 56 (88.9%) | 54 / 97 | 57 (90.5%) | 36 / 97 |

* **The start holds 23 games, so the 40 others are the ones the rounds work on.**  Of those 40, one round brings 9
  (seed 1) and 7 (seed 2) to the known score, 8 rounds 22 and 22, 64 rounds 29 and 29, and 256 rounds 33 and 33.
* **A game needs a median of 4 rounds (seed 1) and 3 (seed 2)** among the 33 that each seed reaches; 6 (seed 1) and 9 (seed 2)
  need more than 16 rounds, and 4 and 4 more than 64.  The late games differ by seed: 4180 is reached at round 238 by seed 1 and 36 by seed 2,
  4329 at 238 and 98, 4914 at 15 and 100.
* **The curve flattens but does not stop.**  From 32 to 256 rounds, 8 times the cost, seed 1 gains 4 games of 63
  (82.5% to 88.9%), seed 2 gains 7 and the better of two gains 4.
* **The games left short are short by little**: a median of 36 to 54 points and at most 97 after 256 rounds, of
  promotion sums of 2.7 × 10^5 to 5.6 × 10^5.

**3. The estimate for the 568 searched games of 3441-5060**, (317 + 251 × share) / 568, with the 90% interval of the
share carried through.  It is one estimate from one sample, and takes the 317 games whose start held the best score in
the run as still holding it (the second limit under "What the data cannot tell"):

| effort | rounds | seed 1 | seed 2 | better of two |
|---|---|---|---|---|
| 0 | 0 | 71.9% [67.5, 76.8] | 71.9% [67.5, 76.8] | 71.9% [67.5, 76.8] |
| 1 | 1 | 78.3% [73.4, 83.1] | 76.9% [72.0, 81.7] | 80.4% [75.4, 85.1] |
| 2 | 2 | 81.1% [76.1, 85.8] | 81.8% [76.8, 86.4] | 84.6% [79.7, 89.0] |
| 3 | 4 | 83.9% [79.0, 88.3] | 86.0% [81.1, 90.2] | 86.7% [81.9, 90.8] |
| 4 | 8 | 87.4% [82.6, 91.4] | 87.4% [82.6, 91.4] | 88.1% [83.3, 92.1] |
| 5 | 16 | 90.9% [86.4, 94.4] | 88.8% [84.1, 92.7] | 91.6% [87.2, 95.0] |
| 6 | 32 | 92.3% [88.0, 95.5] | 90.2% [85.6, 93.8] | 93.0% [88.8, 96.1] |
| 7 | 64 | 92.3% [88.0, 95.5] | 92.3% [88.0, 95.5] | 93.7% [89.6, 96.6] |
| 8 | 128 | 93.7% [89.6, 96.6] | 95.1% [91.2, 97.6] | 95.8% [92.1, 98.1] |
| 9 | 256 | 95.1% [91.2, 97.6] | 95.1% [91.2, 97.6] | 95.8% [92.1, 98.1] |

The better of two seeds is the work of two runs.  At equal total rounds it is within 4 games of one seed, in both
directions: two seeds of R rounds hold 35, 41, 44, 46, 51, 53, 54 and 57 games at R = 1, 2, 4, ..., 128, and one seed
of 2R rounds holds 36 and 37, 40 and 43, 45 and 45, 50 and 47, 52 and 49, 52 and 52, 54 and 56, and 56 and 56 (seeds 1
and 2).

**4. The games a seed missed were stuck early.**  Seed 1 missed 7 games (3552, 3600, 3723, 3850, 4056, 4104, 4232) and
seed 2 missed 7 (3552, 3723, 3850, 4056, 4104, 4232, 4416).

| n | start short | seed 1: last improvement, final short | seed 2: last improvement, final short | run of 2026-11-01: source, the finder's seconds to its best |
|---|---|---|---|---|
| 3552 | 97 | round 0, 97 | round 0, 97 | finder, 175 |
| 3600 | 262 | round 187, 74 | reached at round 12 | finder, 15 |
| 3723 | 3 | round 0, 3 | round 0, 3 | finder, 270 |
| 3850 | 18 | round 0, 18 | round 0, 18 | tree search (the finder stopped 8 short) |
| 4056 | 64 | round 39, 54 | round 114, 54 | tree search before the finder started |
| 4104 | 36 | round 3, 1 | round 1, 1 | finder, 0.2 |
| 4232 | 94 | round 0, 94 | round 0, 94 | finder, 151 |
| 4416 | 54 | reached at round 106 | round 0, 54 | finder, 172 |

* **Stuck, not short of time.**  By round 16 the last improvement had come in 5 of seed 1's 7 misses (4 never improved
  at all) and 6 of seed 2's 7 (5 never improved).  Three of the 14 misses had a later improvement: seed 1 on 3600 (round
  187) and on 4056 (round 39), seed 2 on 4056 (round 114).  A game that never improved in 256 rounds had 16,384 neighborhoods drawn
  and none found a better set; in 3552 the start is 97 short.
* **A second seed recovers one game in seven.**  Seed 2 reaches 1 of seed 1's 7 misses (3600, at round 12) and seed 1
  reaches 1 of seed 2's 7 (4416, at round 106).  Both seeds miss 6 games, 15% of the 40 games short at the start.
* **The two seeds end at the same score in all 6 games they both miss**, though they draw different neighborhoods, which
  suggests that the incumbent is a fixed point of the neighborhoods the mode draws, not the result of bad luck with a seed
  (two seeds cannot show it).
* **The stuck games are not the far ones.**  Their start is a median of 50 points short, against 96.5 for the other
  games short at the start, and their n runs from 3552 to 4232, against 3465 to 5024.
* **The run of 2026-11-01 found the best score of 4 of the 6** with its finder on one thread (the same kind of search with a
  different driver: timed rounds of 15 s that accept an improvement at once, odd rounds from the survivors of the seed), after 0.2, 151, 175
  and 270 seconds of its own clock; the tree search found the other two.  Each seed spent 330 to 430 thread-seconds
  on 3552, 3723 and 4232.  Of the 14 games the finder found after more than 10 seconds, 3 are missed by both seeds;
  of the 19 it found within 10 seconds, 1.

**5. The cost** (4 threads at nice 19, on a machine whose other threads run the prover at idle priority, in wall
seconds; the rounds' cost is measured on the 37 lines of at least 8 rounds, so that the 0.09 s (median) a line with
no round spends after the start, the replay and the write, weighs little; the start's seconds are those of every game
of the band, the mean of the two seeds):

| n | lines | seconds per round, median (min-max) | steps per neighborhood, median (min-max) | thread-ms per step, median | start in seconds, median (min-max) |
|---|---|---|---|---|---|
| 3441-3800 | 9 | 0.32 (0.23-0.35) | 19.0 (12.9-36.8) | 0.90 | 2.8 (2.3-4.9) |
| 3801-4200 | 11 | 0.31 (0.28-0.45) | 24.2 (22.4-35.6) | 0.79 | 4.1 (3.4-8.7) |
| 4201-4600 | 8 | 0.40 (0.39-0.63) | 34.9 (26.9-60.7) | 0.71 | 6.3 (5.0-11.9) |
| 4601-5060 | 9 | 0.62 (0.35-1.32) | 45.9 (21.4-117.1) | 0.91 | 8.4 (7.3-20.9) |
| all | 37 | 0.36 (0.23-1.32) | 26.9 (12.9-117.1) | 0.84 | 5.1 (2.3-20.9) |

* **A neighborhood takes 13 to 117 steps on average** (a line's mean), 27 at the median, against the 1,024 it is
  allowed.  The lines do not count the neighborhoods that reached the limit; in the study of 2026-10, on 2176-3440, 99.9%
  were searched to the end.
* **A round is search work, with a fixed part of about a quarter.**  The thread-milliseconds of a neighborhood (the
  round's wall time × 4 threads / 64) follow its steps, 5.8 + 0.63 × steps (correlation 0.97 over the 37 lines), so the
  part that does not depend on the steps is 25% of the 22.6 ms of a median neighborhood.  This is an upper bound, since the
  threads' waits at the end of a round count in it.  When the mode was built, its own check found 3 to 35 steps
  a neighborhood and took a round's time to be mostly the fixed cost of 64 engine runs; at 3441-5060 a step costs about
  0.8 ms of a thread's time, so 27 steps are most of the time of a neighborhood.
* **The start** takes 2.3 to 20.9 s, a median 5.1, growing with n; 4851, the game whose start in the run was 1,957
  short, took the longest.
**The cost of a level**, with the sample's mean start (5.7 s) and mean round (0.43 s), for a game on 4 threads and for
the 568 games of 3441-5060 with no stop at the known score:

| effort | rounds | seconds | thread-seconds | 568 games, thread-hours |
|---|---|---|---|---|
| 0 | 0 | 5.7 | 23 | 3.6 |
| 1 | 1 | 6.1 | 25 | 3.9 |
| 2 | 2 | 6.6 | 26 | 4.1 |
| 3 | 4 | 7.4 | 30 | 4.7 |
| 4 | 8 | 9.1 | 37 | 5.8 |
| 5 | 16 | 12.6 | 50 | 7.9 |
| 6 | 32 | 19.4 | 78 | 12.3 |
| 7 | 64 | 33.2 | 133 | 20.9 |
| 8 | 128 | 60.7 | 243 | 38.3 |
| 9 | 256 | 115.7 | 463 | 73.0 |

The 14 lines that ran all 256 rounds took 84.5 s at the median (69.9 to 160.6).  The two runs took 1,301 and 1,297 s
of lines in all, 0.72 hours of 4 threads.

## What this means for the unsound mode

* **The cheap levels work as designed.**  Efforts 0 to 6 give 71.9% to 93.0% by the estimate (the better of two seeds)
  for 3.6 to 12.3 thread-hours over the 568 games, and the share rises at nearly every doubling.  Effort 5 (16 rounds,
  50 thread-seconds a game) holds 89% to 91% of the 568 games by either seed's estimate.
* **The start from the proven game of n − 1 carries more than E0 found.**  It holds the known score in 23 of the 63
  games that the start of the run missed, so the start alone holds 71.9% of the 568 games where the run's start held
  55.8% (317 of 568).  What the real mode's start holds depends on the line of n − 1 it starts from, which may itself
  be short; this pilot does not measure that drift.
* **The top levels buy little for their cost, and the games they miss are fixed points.**  Going from effort 6 to
  effort 9 costs 6 times as much (78 to 463 thread-seconds a game) and adds 4 and 7 games of 63 for the seeds, 4 for the
  better of two.  The 6 games both seeds miss are not reached by this kind of round: 4 never moved off the start in
  16,384 neighborhoods each, and the two seeds end at the same score in all 6.  More rounds of the same neighborhoods
  and a second seed are unlikely to reach them.
* **What the stalls call for, in the order to try it** (each a hypothesis these data do not test):
  1. **Larger neighborhoods.**  A neighborhood fixes 70-90% of the incumbent's promotions and takes 27 steps on average
     of the 1,024 allowed, so the limit leaves room for a larger one; a fixed point of neighborhoods of this size may be
     left by one that fixes less.  The [study of 2026-10](../finders-for-good-games-that-are-not-sound-2026-10/README.md)
     found 70-90% fixed better than 50-80% at 5 CPU seconds, a budget of time, on a worse start; with a budget of rounds
     the answer may differ.  The test needs the share fixed as an option of the mode, and runs on 13 games: the 6 both
     seeds miss, the 2 that one seed misses (3600, 4416) and the 5 more that a seed reached after round 64 (4180, 4290,
     4329, 4872, 4914), 70 to 160 s each on 4 threads at effort 9.
  2. **Restarts from another base.**  The finder of the proven run alternates its rounds between the incumbent and the
     survivors of the game before, and found 4 of the 6 stuck games in 0.2 to 270 s on one thread.  The mode's rounds
     all start from the incumbent, and the second seed does not change the base.  The pilot cannot say whether the base,
     the immediate acceptance of an improvement or the length of the rounds made the difference.
  3. **Perturbation** (change many promotions at random, then descend) has no evidence here beyond the fixed points.
  4. **A capped tree search** finds 4056 within the million steps after which the run started its finder, and 3850,
     the other game the run's finder did not find, only within the 13.3 million steps of its whole search.  At 0.84 ms of
     a thread a step, a million steps cost 840 thread-seconds, against 463 for effort 9, so it is dearer than every
     level so far.
* **Before E1.**  A day of the whole machine is 2,112 thread-hours (88 threads × 24 h), 29 times the 73 thread-hours of
  effort 9 over the 568 games at this pilot's cost on a loaded machine.  If E1 runs the mode as it is, its top levels
  measure a curve that flattens at 85% to 90% of the sampled games, which the run's start missed.  The 13-game test
  above takes minutes and shows whether the curve E1 would publish has a different top.

## What the data cannot tell

* **One sample of 63 games.**  It is every 4th of the 251 games, sorted by n, so the intervals are binomial for 63
  trials and are not corrected for the sample being a quarter of the 251.  The 6 stuck games are too few to say what
  they have in common beyond the numbers above.
* **The sample was chosen by the start of the run, not the start of this build.**  23 of its 63 games hold the known
  score at the start, so it holds 40 games the rounds work on, not 63.  The 317 games whose run-start held the best
  score were not run, and the estimate takes them as holding it at every effort.  The starts of the 126 lines were
  never below the run's, which supports it for the 63 games.
* **The start comes from the proven game of n − 1.**  The mode starts from its own line of n − 1, which may be short.
  Its start, and the gain of the rounds, will differ.
* **Times on a loaded machine.**  Each seed ran on 4 threads at nice 19 beside idle-priority prover threads on the 88-thread
  machine, whose hyperthreads the prover shares.  The seconds and thread-seconds are for that machine at that load, and
  an idle machine may be faster per thread; the mode on all 88 threads feeds each round's 64 neighborhoods to 64
  threads, and the table of costs does not predict its wall time.  The fixed part of a neighborhood includes the waits at
  the end of a round.
* **A line ends at the known score.**  The rounds after that are not measured, so the cost of a level for a game
  that reaches the known score early is the sample's mean round, not a measurement of that game.
* **Reaching the known score is an equal score**, not the same moves.
* **Two seeds.**  The round at which a seed reaches a game varies by a factor of 6 or more between seeds (4180: 238 and
  36; 4914: 15 and 100), so the medians of the rounds needed are rough, and whether the 6 stuck games are fixed points
  or only unlucky needs more seeds.
* **Why the games stall.**  The data show that the incumbent stays; they do not test the neighborhoods' size, the base,
  or the length of the rounds.  The comparison with the run's finder differs in several ways at once.

## Open

* The 13-game test of larger neighborhoods, and of restarts from the survivors of the game before, with the setting as
  an option of the mode (the code of the mode changes, not this entry's).
* 8 seeds on the 6 stuck games at 256 rounds, to tell fixed points from unlucky draws.
* The start and the rounds seeded with the mode's own line of n − 1 instead of the proven one: the drift.
* The 317 games whose start held the best score in the run, to confirm that this build's start holds it.
* A line that goes on past the known score, which would measure the cost of the rounds for the games that reach it early.

## Files

* [select_games.py](select_games.py): picks the sample.  `python3 -I select_games.py
  ../where-the-best-scores-came-from-2026-11/games.json .` writes [sample.json](sample.json) and
  [games.txt](games.txt).
* [run_seed.py](run_seed.py): plays the games of a file for one seed, one command each, appending to one file, so a
  rerun resumes.  `nice -n 19 python3 -I run_seed.py --seed S --bin TAXMAN --games games.txt --out seed-S.jsonl
  --log seed-S.log`, for S = 1 and 2 at once.
* [seed-1.jsonl](seed-1.jsonl), [seed-2.jsonl](seed-2.jsonl): the 63 unsound lines of each seed (with the moves);
  [seed-1.log](seed-1.log), [seed-2.log](seed-2.log): the commands and their summary lines.
* [analyze.py](analyze.py): the checks of the lines and every number above.  `nice -n 19 python3 -I analyze.py >
  out.txt`; [out.txt](out.txt) is its output.

No code of the main repository changed.  The code run is that of commit
[e37d6a1](https://github.com/bvchess/taxman/commit/e37d6a1).
