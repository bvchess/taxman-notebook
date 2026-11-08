# Tuning the unsound mode on a long chain (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  The unsound mode (`taxman solve LO-HI --unsound --effort L --out FILE`) ends a game's rounds when the
game's gap has not grown (`--stop-growth`), and plays a game twice when its gap jumps (`--push-growth`).
[B13](../stopping-and-pushing-by-the-gap-2026-11/README.md) chose their values on the lines of 4561-5060 that E2 and B11
made, and on chains of 200 games over 4861-5060.  Which values should be the defaults on one long chain, 4001-5060,
as the run past 5060 will be, do they hold on 3001-4000, which no study has tuned on, and what does each level give on
a long chain?  This is B14 of the unsound mode.

**Answer.**  Make the push `--push-growth 25` and keep the other values, with low confidence.  On the chain of 1,060 games
it took level 2 from 1,015 games at opt(n) to 1,039 for 4% more time, on both halves; on 3001-4000 it gained 4 games for
10% more time, and the halves disagree.  The stop (25) and the unseeded play at the game's own level stay: stop 50 gave
the same lines in 1% less time, stop off 16 games for 18% more time, and the unseeded play at level 1 saved 4% of the
time and cost 240 points once.  The new rules do not keep their lead over the mode before B13 on 3001-4000: that mode
scores opt(n) in 951 games of 1,000 against 932, for 30% more time, because the stop ended the rounds of five games that
went on to streaks of 26 short games.  Level 3 scores opt(n) in 1,046 of the 1,060 games (98.7%) and level 4 in the same
1,046, for 42% more time.  A chain of 1,060 games costs nothing against chains of 100: no streak crosses a restart, and
level 3's lines over 4861-5060 are those of B13's chain of 200 game for game.  One seed, two stretches, one machine.

## Method

*The words.*  A game is *short* when its score is below opt(n).  Its *gap* is its bound (the parity bound, which no play
exceeds) less its score, and its *growth* the gap less the gap of the line of n − 1 it started from.  A *streak* is a run
of consecutive short games, its *start* the first of them and its *tail* the games after the start, which the start hands
its shortfall on to.  The *stop* ends a searched game's rounds once its growth is within ±T (`--stop-growth T`), asked
from the end of level 1's rounds on.  The *push* plays a game a second time, unseeded, and keeps the better line, when
the growth of its seeded play is above T (`--push-growth T`); the push *flags* a game when it would play it twice.  The
*control* is the mode before B13: `--stop-growth off --push-growth off --unseeded-every 8`.  A *level* L is a budget of
2^L × 65,536 work for a game's rounds ([the unsound mode's document](https://github.com/bvchess/taxman/blob/ecb4bc4/solver/docs/unsound.md)
has the rest).

*The build.*  Master [ecb4bc4](https://github.com/bvchess/taxman/commit/ecb4bc4), release without fat LTO
(`profile.release.lto=false`, `codegen-units=16`), built once at -j 4 and copied, so that no later build changed it.
Every line records `"build": {"commit": "ecb4bc4...", "dirty": false}`.

*The arms.*  An arm is one run `taxman solve LO-HI --unsound --effort L --seed 1 --threads 8 --out FILE` with the options
of its row, and no `--from-known` and no `--stop-at-known`: its first game starts from the table's game LO − 1, and every
later game from the run's own line.  [run_jobs.py](run_jobs.py) started them side by side at nice 19 and recorded each
pid, so that an arm that was clearly losing could be stopped with SIGTERM to its own pid; none was.

| arm | level | options changed from the defaults (`--stop-growth 25 --push-growth 50 --unseeded-every 0`) |
|---|---|---|
| l1, l2, l3, l4 | 1 to 4 | none |
| l2-push25, l2-push100 | 2 | `--push-growth 25`, `--push-growth 100` |
| l2-stop50, l2-stopoff | 2 | `--stop-growth 50`, `--stop-growth off` |
| l2-unseeded1 | 2 | `--unseeded-effort 1` |
| l2-control | 2 | the control |

Part 1 ran the ten arms over 4001-5060 (1,060 games each) at once, 80 threads of `--threads`, from 19:22 to 22:36
(Pacific time, 2026-11-07).  Part 2 ran the held-out stretch 3001-4000 (1,000 games) with the choice of Part 1
(`--push-growth 25`, the rest the defaults) at levels 2 and 3 (h-choice-l2, h-choice-l3), the control at level 2
(h-control-l2) and, beside the three the question asked for, the defaults at level 2 (h-default-l2), from 21:38 to 23:03,
beside the last three arms of Part 1.  The machine has 88 hardware threads on 44 cores, and each run makes the next
game's setup on a thread beside its 8.  Its load average was 75 at 19:36, 69 at 20:56 and 18 at 22:37, so the arms that
ended last ran on a machine that was emptying: their seconds are lower than they would have been at the start's load (the
second half of l4 took less time than the first, at larger n).  The work of a game is the same at any load, and is given
beside the seconds.

*The estimate before the runs.*  B13's level 3 took 817 s per 100 games of 4861-5060 on 8 threads.  I took the games of
4001-5060 to cost 0.55 of those on average (E2's chains rise from 0.46 to 0.9 hours per 100 games from 4561 to 5060),
the busy machine 1.25 times, and each level up 1.6 times: 0.7 hours for level 1, 1.1 for level 2, 1.7 for level 3, 2.7 to
3.5 for level 4, 1.8 for the control, and no arm over 5 hours.  The runs took 1.5, 1.8, 2.3, 3.2 and 2.5 hours (l1, l2, l3,
l4, the control): the games of 4001-5060 cost 0.94 of the games of 4861-5060 at level 3 (772 s against 821 s per 100
games), not 0.55.  Level 4 came in under 5 hours because the machine emptied as the other arms ended; at 54 minutes I
had projected 4 to 5.5 hours for it.

*The analysis* ([b14.py](b14.py); the output is [part1-out.txt](part1-out.txt) and [part2-out.txt](part2-out.txt)).  A
game's line is the last line the file has for it, so a line that the repair wrote again counts.  *Time* is the sum of the
games' `seconds` (the repair's walks, 22 to 55 s a run, are not in it); a run's wall time agrees with it to within 1%.
The rule of the study, for two arms X and Y on the same games: X is *better* when it has more games at opt(n) for at
most 10% more time, or the same games and the same points short in less time (or fewer points short in no more time).
It is applied to the whole range and to each half, 4001-4530 and 4531-5060 (3001-3500 and 3501-4000 in Part 2).
*Checks.*  All 14,622 lines of the 14 runs pass: unsound, the build above, the arm's level, seed, threads and options,
`bound` equal to `parity` of
[parity_2_8191.jsonl.gz](../the-parity-bound-against-the-frame-bound-2026-10/parity_2_8191.jsonl.gz), no score above the
bound or above opt(n), the first game's `prev.source` the table and every other `run`, and `growth` equal to the gap less
the gap of the line below.

## Part 1: 4001-5060

Games at opt(n) of 1,060, with the first half and the second in parentheses (530 games each); the other columns are the
whole range.

| arm | at opt(n) | points short | s / 100 games | M work / 100 | rounds ended by the stop | pushed | played twice for n |
|---|---|---|---|---|---|---|---|
| l1 | 1,009 (501, 508) | 2,468 | 507 | 6.2 | 0 | 60 (5.7%) | 0 |
| l2 | 1,015 (507, 508) | 2,009 | 607 | 8.5 | 235 (22.2%) | 58 (5.5%) | 0 |
| l3 | 1,046 (516, 530) | 186 | 772 | 13.1 | 237 (22.4%) | 58 (5.5%) | 0 |
| l4 | 1,046 (516, 530) | 186 | 1,093 | 22.0 | 238 (22.5%) | 58 (5.5%) | 0 |
| l2-push25 | 1,039 (516, 523) | 572 | 633 | 8.9 | 235 (22.2%) | 73 (6.9%) | 0 |
| l2-push100 | 1,030 (507, 523) | 1,094 | 564 | 7.8 | 235 (22.2%) | 32 (3.0%) | 0 |
| l2-stop50 | 1,015 (507, 508) | 2,009 | 600 | 8.2 | 257 (24.2%) | 58 (5.5%) | 0 |
| l2-stopoff | 1,031 (513, 518) | 1,051 | 718 | 11.6 | 0 | 59 (5.6%) | 0 |
| l2-unseeded1 | 1,015 (507, 508) | 2,249 | 581 | 7.7 | 236 (22.3%) | 58 (5.5%) | 0 |
| l2-control | 1,034 (513, 521) | 1,212 | 831 | 13.6 | 0 | 0 | 132 (12.5%) |

The seconds per 100 games by half ([part1-out.txt](part1-out.txt) has them for every arm) show the load: l3 took 789 and
754 and l4 1,207 and 978, the second half faster than the first at larger n.

### The streaks

All 14 short games of l3 and l4 are in 4001-4530: three streaks, which start at 4107 (28 points short), 4134 (1) and 4225
(4), and the second half of 4001-5060 is at opt(n) in all 530 games.  Level 2 adds 4116 (9 games), 4914 (21 games,
1,551 points) and 5060, the last game (20 points); level 1 adds 4205 and 4329.  The tables count the short games that
remain after the repair.  The streaks of the ten arms:

| first game | l1 | l2 | l3 | l4 | push25 | push100 | stop50 | stopoff | unseeded1 | control |
|---|---|---|---|---|---|---|---|---|---|---|
| 4107 (28 short, growth −22) | 1 | 1 | 1 | 1 | 1 | 1 | 1 | none | 1 | none |
| 4116 (28, growth 29) | 9 | 9 | none | none | none | 9 | 9 | 4 | 9 | 4 |
| 4134 (1, growth 47) | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| 4205 (17, growth −126) | 3 | none | none | none | none | none | none | none | none | none |
| 4225 (4, growth 98) | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |
| 4329 (56, growth 98) | 3 | none | none | none | none | none | none | none | none | none |
| 4914 (61 to 106, growth 82) | 21 | 21 | none | none | 6 | 6 | 21 | 11 | 21 | 6 |
| 4950 (143, growth 376) | none | none | none | none | none | none | none | none | none | 2 |
| 5060 (20, growth −43) | 1 | 1 | none | none | 1 | 1 | 1 | 1 | 1 | 1 |

A cell is the streak's length in games.  What ended each streak: a later game that searched to opt(n) in every case but
the last row (the end of the range) and l2-stopoff's 4116, where the repair's walk raised 4120 to 4122 from 4121 to 4123
and left 4116 to 4119 short.  The streaks that the rules cannot see are the ones that start at a game the push does not
flag: 4 of 6 at level 2 with the push at 50 (4107, 4116, 4134, 5060) and 2 of 3 at level 3 (4107, 4134); with the push at
25 only 4107 and 5060.

* **4134 and 4225 are in every arm.**  4134 starts 1 point short with a growth of 47, and its tail costs 130 points: 4136
  is a searched game that ends 32 short ([part1-games.txt](part1-games.txt)).  The push at 25 plays it, and the unseeded
  play is also 1 short.  4225 is pushed in eight arms and the unseeded play is also 4 short, in all of them, so the
  two plays reach the same set, which no seed or level here moves (level 4 included).
* **4107 is the stop's loss.**  Its rounds end at a growth of −22 with 28 points short; stop off runs 11 rounds instead of
  9 and ends at opt(n) with a growth of −50.  Only the two arms without a stop (stopoff, control) have no streak at 4107.
* **4116 and 4914 depend on the push's T and on chance.**  At 25 the push plays 4116 (growth 29), whose unseeded play
  reaches opt(n), and plays 4920 (growth 42, after 4914's tail grew by 18 points), whose unseeded play reaches opt(n)
  and ends the tail at 6 games.  At 50 neither is pushed, and the tail runs to 4935.  With the push at 100 and in the
  control 4914 is not pushed, its line stays 106 short instead of 61, and 4920 searches to opt(n) from it: the same end
  by chance, since the games that started 4920 from the line 61 short ended 79 short.
* **The repair clears short streaks of one to three games, and only those.**  When a game above reaches opt(n) at a lower
  gap, its walk raises the games below it: 3440 (37 points, a streak start that the push had played twice with no gain)
  in all four arms of Part 2, 4448-4449 and 5040-5042 in l1, 4275-4276 in l2-push100 and the control, 5040-5042 in
  l2-unseeded1.  It raised 0 to 5 lines of a Part 1 arm.  It leaves the longer streaks: stopoff's repair raised 4120 to
  4122 (28 points) from 4123 and left 4116 to 4119 short, and the control's raised 3300 to 3302 by 1 point (13 to 12
  short) and left the streak of four games, since 3303 is itself 12 short ([part1-out.txt](part1-out.txt),
  [part2-out.txt](part2-out.txt), "Lines the repair raised").

### The push's cost

The unseeded plays took 13 to 27% of the seconds of an arm with the push (31% in the control).  In l2 (push 50) 53 of the
58 pushed games were at opt(n) already,
and the four whose unseeded play scored more are 4275 (19 points), 4914 (45), 4950 (143) and 5040 (11).

| arm | pushed | seeded play at opt(n) already | unseeded play better | points gained | seconds of the unseeded plays | share of the arm's seconds |
|---|---|---|---|---|---|---|
| l2-push100 | 32 | 30 | 2 (4950, 5040) | 154 | 781 | 13.0% |
| l2 (push 50) | 58 | 53 | 4 | 218 | 1,300 | 20.2% |
| l2-push25 | 73 | 65 | 6 (adds 4116, 4920) | 325 | 1,655 | 24.7% |
| l1 | 60 | 52 | 4 | 240 | 968 | 18.0% |
| l3 | 58 | 54 | 3 | 173 | 1,921 | 23.5% |
| l4 | 58 | 55 | 2 | 154 | 3,084 | 26.6% |
| l2-control | 132 played twice for n | | 3 (4120, 4952, 5040) | | 2,713 | 30.8% |

From 100 to 50 the push plays 26 more games for two more rescues (519 s), from 50 to 25 15 more games for two more (355
s): on this stretch each step down was cheaper per rescue than the one before, and T below 25 is not tried.  On
3001-4000 the step from 50 to 25 played 26 more games for one rescue.  The control's every eighth game played twice costs
2,713 s for three rescues, of which the push at 50 makes two.

### The choice

Rule of the study, on the whole range and on each half, all at level 2, X against Y ([part1-out.txt](part1-out.txt) has
every pair):

| option | X against Y | games at opt(n) | time of X over Y | halves | X is |
|---|---|---|---|---|---|
| push T | 25 against 50 | +24 (+9, +15) | 1.04 | agree | better |
| push T | 100 against 50 | +15 (0, +15) | 0.93 | agree | better |
| push T | 25 against 100 | +9 (+9, 0) | 1.12 | agree | neither |
| stop T | 50 against 25 | 0 | 0.99 | agree | better (the same lines) |
| stop T | off against 25 | +16 (+6, +10) | 1.18 | agree | neither (over 10% more time) |
| unseeded level | 1 against 2 | 0 (points short +240) | 0.96 | the halves disagree | no winner |
| control | the control against the defaults | +19 (+6, +13) | 1.37 | agree | neither |
| control | the choice (push 25) against the control | +5 (+3, +2) | 0.76 | agree | better |

* **The push: 25.**  It beats 50 on both halves.  100 also beats 50 on both halves, and the rule cannot separate 100
  from 25 (nine games for 12% more time).  100's gain over 50 is the luck of 4914 (6 games against 21, see above), not a
  property of the setting: it flags neither 4116 nor 4920.  So 25.
* **The stop: 25.**  Stop 50 gives the same score on all 1,060 games and ends 22 more games' rounds, for 3.5% less work
  and 1% less time, a margin that one timing cannot show.  Stop off adds 16 games for 18% more time and is not better by
  the rule, and is where the games are lost ([Part 2](#part-2-the-held-out-stretch-3001-4000)).
* **The unseeded play's level: the game's own.**  Level 1 saves 4% of the time.  In the first half it scores the same,
  7% faster, and in the second it ends 4914 at 101 short instead of 61 (240 points) for 3% less time.
* **Every eighth game played twice: off.**  The schedule costs the control 28 to 31% of its seconds and makes 3 rescues
  in 4001-5060 (4120, 4952, 5040) and 4 in 3001-4000 (3344, 3584, 3696, and 2 of the 30 points of 3888).  The push at 25
  makes the equivalent of all three of the first (it plays 4116, 4950 and 5040 itself) and three more (4275, 4914, 4920),
  and three of the four of the second, with five more (3090, 3174, 3300, 3572, 3610).

## Part 2: the held-out stretch 3001-4000

| arm | at opt(n) | points short | s / 100 games | M work / 100 | rounds ended by the stop | pushed | played twice for n |
|---|---|---|---|---|---|---|---|
| h-choice-l2 | 932 (479, 453) | 1,681 | 338 | 10.4 | 196 (19.6%) | 85 (8.5%) | 0 |
| h-choice-l3 | 957 (482, 475) | 1,325 | 508 | 17.2 | 197 (19.7%) | 85 (8.5%) | 0 |
| h-default-l2 | 928 (479, 449) | 1,737 | 309 | 9.6 | 196 (19.6%) | 59 (5.9%) | 0 |
| h-control-l2 | 951 (478, 473) | 1,393 | 441 | 14.3 | 0 | 0 | 125 (12.5%) |

The first half is 3001-3500 and the second 3501-4000.  The runs took 52, 57, 74 and 85 minutes (h-default-l2,
h-choice-l2, h-control-l2, h-choice-l3).

* **The choice does not keep its lead over the control.**  On 4001-5060 the choice beat the control on both halves (+5
  games, 24% less time).  On 3001-4000, h-choice-l2 against h-control-l2 has 19 games fewer at opt(n) for 23% less time
  (the control takes 30% more).  By the rule the choice is better on the first half (+1 game, 22% less time) and neither
  on the second (−20 games), so the halves disagree and the whole range is neither.
* **The choice against the defaults** (h-choice-l2 and h-default-l2): +4 games and 56 points for 10% more time (1.094):
  better on the whole range and on the second half (+4 games, 8% more time), worse on the first (the same lines in 11%
  more time).  The halves disagree.  The 4 games are one rescue, 3584 (14 points short in the default, 0 with the push at 25),
  for 26 more games pushed, 260 s of unseeded play.
* **Where the control wins.**  15 streaks start in h-choice-l2, and 11 at a game the push does not flag.  Eight of them
  start at a game whose rounds the stop ended, at a growth of −13 to 25; the control has no streak at five of the eight
  (3332, 3384, 3750, 3774, 3850), which are 26 short games, and the same streak at 3192, 3311 and 3723.  3750, for
  example, is stopped after 10 rounds at a growth of 7 with 33 points short; the control runs 18 rounds and ends at opt(n)
  with a growth of −26 ([part2-games.txt](part2-games.txt)).  In the other direction, the push reaches opt(n) at 3090,
  3300, 3572 and 3610, where the control is short (16 games).
* **Level 3 against level 2** (the choice): 957 against 932 games at opt(n) for 50% more time; 12 streaks against 15.

## The levels

Over 4001-5060 on 8 threads of a busy machine (Part 1, the defaults), and over 4561-5060 against
[E2](../the-datasheet-of-the-unsound-mode-2026-11/README.md)'s chains of 100 games over the same games (E2's old efforts 2
to 5 are levels 1 to 4; its chains ran on 4 threads, before the stop, the push and the repair):

| level | 4001-5060: at opt(n) | hours / 100 games | 4561-5060: at opt(n), this chain | at opt(n), E2 | hours / 100 games, this chain (8 threads) | hours / 100 games, E2 (4 threads) | M work / 100, this chain | M work / 100, E2 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1,009 (95.2%) | 0.141 | 478 of 500 | 471 | 0.157 | 0.26 | 6.2 | 5.4 |
| 2 | 1,015 (95.8%) | 0.169 | 478 | 479 | 0.182 | 0.41 | 8.4 | 10.0 |
| 3 | 1,046 (98.7%) | 0.214 | 500 | 486 | 0.206 | 0.72 | 12.7 | 19.4 |
| 4 | 1,046 (98.7%) | 0.304 | 500 | 486 | 0.270 | 1.34 | 21.0 | 37.3 |

On 3001-4000 the choice scores 932 (93.2%) at level 2 in 0.094 hours per 100 games and 957 (95.7%) at level 3 in 0.141.
E2's alone estimates on 8 threads were 0.09, 0.14, 0.25 and 0.46 hours; a busy machine takes about 1.7 times as long as an
idle one (E2), so the measured hours here are not comparable with those.  Converted by E2's speedup of 1.68 from 4 to 8
threads, E2's busy hours are 0.155, 0.24, 0.43 and 0.80, against 0.157, 0.18, 0.21 and 0.27 here: the same at level 1,
and 1.3, 2.1 and 2.9 times faster at levels 2 to 4, in step with the work the stop saves (the work is 0.84, 0.65 and 0.56
of E2's).

* **Level 4 is not worth its time over level 3** on 4001-5060: the same 1,046 games, the same 186 points, 42% more time.
* **A chain of 1,060 games costs nothing against chains of 100, here.**  Level 3 scores 500 of the 500 games of
  4561-5060 where E2's chains scored 486 (the rules, not the length, make that difference), and its 200 games of 4861-5060
  have the lines of B13's chain of 200 from the table's 4860 on every game, in 821 s per 100 games against B13's 817.  No
  streak of any arm crosses a restart from a proven game every 100 games, from 4001 or from 4561; in Part 2 one streak of
  the control's does (3300, 3 games).  The cost of a chain is the tail behind each stuck game: at level 3 14 short
  games, 3 starts and 11 in tails.
* **The stretches differ more than the levels.**  With the push at 25, level 2 has 5 streak starts in 1,060 games of
  4001-5060 and 15 in 1,000 games of 3001-4000, the smaller games; level 3 has 3 (the push at 50) and 12.

## What it means

* **The defaults to recommend.**  `--push-growth 25`, the stop at 25, the unseeded play at the game's level, no game
  played twice for its n, and level 3 for a user who wants the most games at opt(n) for the time.  Of these only the
  push changes.  I am not sure of it: its gain is three rescued games in 2,060 (4116, 4920, 3584), each worth a streak of
  4 to 15 games, for 4% and 10% more time, on one seed.  This study changed no code.  A push below 25, a second seed
  over both stretches and level 3 with the stop off would reopen it.
* **The stop is where the games are lost.**  Its band of ±25 treats a game whose growth is within it as done, and a game
  can be within it and still short: 3750's incumbent had a growth of 7 and its optimum −26; 4107's −22 and −50.  On
  3001-4000 that is five streak starts in 1,000 games, 26 short games; the stop saves 15% of the time (27% of the work)
  at level 2 on 4001-5060.  Whether that is worth it is for the user to say; the rule of the study says yes.  A user who
  wants every game at opt(n) should set `--stop-growth off`; level 3 with the stop off is not measured.
* **The streaks no setting fixed.**  On 4001-5060, 4134 and 4225 in every arm, and 4107 in every arm with a stop.  On
  3001-4000, 3174, 3192, 3311, 3565, 3723, 3888 and 3968 in all four.  Two kinds.  The push at 25 flags 4134, 4225,
  3174 and 3968, and their unseeded play scores what the seeded play did (1, 4 and 3 points short) or little more (3174:
  49 to 32), so a second play at the same budget reaches nearly the same incumbent and gives nothing.  The others
  (3192, 3311, 3565, 3723, 3888, and 4107) it does not flag, at growths from −35 to 19: the optimum's gap is smaller than
  the gap below by about the shortfall, so the gap cannot tell a short game from a done one.  11 of the choice's 15
  streak starts on 3001-4000 are of this kind.  They need another signal; the scores of the survivors, which each line
  records, are one candidate.
* **The repair clears the short streaks and not the long ones.**  It cleared nine streaks of one to three games in
  the 14 runs (listed above), each when the game above them reached opt(n), and left every streak of four games or more
  (it raised some games of stopoff's 4116 and the control's 3300 and left the rest).  A streak ends when a later game searches
  to opt(n), 1 to 21 games after its start.
* **What B13 did not see.**  Its stop and push were chosen on 4561-5060, where the long chain scores 478 to 500 of 500
  games at levels 1 to 4 and has few streaks; the stop costs games on 4001-4530 and on 3001-4000.

## What the data cannot tell

* **One seed, two stretches, few events.**  The differences between arms are a handful of streaks: the 24 games of the push
  at 25 over 50 are two rescues (4116, 4920) and the length of one tail.  Another seed would move 4914's tail (the arms
  that differ in how it ends differ by chance), and no interval on 1,060 games means anything.
* **Not the games past 5060.**  The known games stand in for them; the streak starts of level 2 with the push at 25 fall
  from 15 in 3001-4000 to 5 in 4001-5060, so the data show no steady rise with n.
* **The times are those of a busy machine** and of arms that ended at different times; the second half of the slowest
  arms is understated, which favors the control, level 4 and h-choice-l3.  Work per 100 games does not depend on the load.
* **Level 3 with the stop off, a push below 25 and a stop band between 0 and 25 are not tried.**  The stop's loss is read
  off the control at level 2, which also changes the push and the games played twice.
* **The lines of two arms diverge once they differ**, so a difference of games at opt(n) at the end of a streak is not
  attributable to the setting alone; the streak table names the games.

## Files

The commands ran in the study's scratch folder; the lines are gzipped, an arm a file, with its log.

* [run_jobs.py](run_jobs.py): the driver (`nice -n 19 python3 -I run_jobs.py --bin TAXMAN --jobs JOBS --dir DIR
  --progress 1800`), a job a line of [part1-jobs.txt](part1-jobs.txt) or [part2-jobs.txt](part2-jobs.txt).
* [part1/](part1/) and [part2/](part2/): the arms' lines (`ARM.jsonl.gz`), their logs (`ARM.log`, the commands, the pids
  and the summary lines), `driver.log` and `pids.txt`.
* [b14.py](b14.py) (`python3 -I b14.py part1 l1 l2 l3 l4 l2-push25 l2-push100 l2-stop50 l2-stopoff l2-unseeded1
  l2-control --groups --levels > part1-out.txt`, and `python3 -I b14.py part2 h-choice-l2 h-choice-l3 h-default-l2
  h-control-l2 --range 3001-4000 --groups > part2-out.txt`): the checks, the tables of this entry, the streaks, the
  push's cost, the options against each other by the rule, and the levels against E2.  It reads
  [b13lib.py](../stopping-and-pushing-by-the-gap-2026-11/b13lib.py) of B13 and E2's and B13's lines.
* [part1-out.txt](part1-out.txt), [part2-out.txt](part2-out.txt): its output.
* [part1-games.txt](part1-games.txt), [part2-games.txt](part2-games.txt): the games around the streaks cited above, one line
  a game (`python3 -I b14.py part1 l2 l3 l2-push25 l2-stopoff l2-control --games 4912-4936`, the ranges 4105-4126,
  4133-4141, 4224-4233 and 4912-4936 of Part 1, and 3383-3389, 3749-3761, 3849-3861 and 3887-3900 of Part 2).

## Commits

* [ecb4bc4](https://github.com/bvchess/taxman/commit/ecb4bc4) (main repository): the build of every run.  The study
  changed no code.
* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).
