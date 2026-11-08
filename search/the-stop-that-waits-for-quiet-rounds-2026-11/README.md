# The stop that waits for quiet rounds (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-08.  Concluded 2026-11-08.

**Question.**  Main's [9477c8b](https://github.com/bvchess/taxman/commit/9477c8b) makes the unsound mode's stop
(`--stop-growth 25`) ask its band only once the last 4 rounds raised nothing (`--stop-quiet 4`; 0 is the old rule), and
makes `--push-growth 25` the default.  [B15](../simulating-stop-rules-on-lines-already-made-2026-11/README.md) simulated
the rule on lines played with no stop, which cannot say what a chain does, since a changed line changes the games above
it.  Does the mode do what B15 expected, does the rule pay as the default, and at which level should the mode run for the
most games at opt(n) per unit of work?  This is B17 of the unsound mode.

**Answer.**  Keep `--stop-quiet 4`.  On 3001-4000 it took level 2 from 932 to 954 games at opt(n) of 1,000 (1,681 to
1,396 points short) for 1.0% more work, and level 3 from 957 to 960 for 0.8%.  The streaks of 3332, 3750, 3774 and 3850
did not begin, as B15 expected, and 3384 and 4107 stay lost.  On 4001-5060 it changed 2 lines of level 2 and 3 of level 3
and no score.  Level 3 over level 2 buys 6 to 7 games of 1,000 for 55% to 66% more work, so level 2 gives the most games
at opt(n) per unit of work.  Level 3 with no stop scores opt(n) in 976 of the 1,000 games of 3001-4000 where level 3 with
the stop scores 960, for 45% more work.  One seed.

## Method

*The words* are [B14's](../tuning-the-unsound-mode-on-a-long-chain-2026-11/README.md#method): a game is *short* when its
score is below opt(n), a *streak* is a run of consecutive short games, a game's *gap* is the parity bound less its score
and its *growth* the gap less the gap of the line below.  The *stop* ends a searched game's rounds once its growth is
within ±25, and a *quiet round* is one that did not raise the game's score.  The *push* plays a game twice, unseeded, when
its seeded play's growth exceeds 25.  A game's *work* is the steps of its rounds and 32 for each neighborhood
([the unsound mode's document](https://github.com/bvchess/taxman/blob/9477c8b/solver/docs/unsound.md#the-level-of-effort)).

*The arms.*  Each is `taxman solve LO-HI --unsound --effort L --seed 1 --threads 8 --out FILE` with the options of its
row, on master 9477c8b (release without fat LTO, built once and copied), with no `--from-known` and no
`--stop-at-known`.  The defaults are `--stop-growth 25 --stop-quiet 4 --push-growth 25 --unseeded-every 0`.
[run_jobs.py](run_jobs.py) started the five at once at nice 19 and recorded their pids ([jobs.txt](jobs.txt)), from 05:00
to 07:52 (Pacific time, 2026-11-08); none failed or was stopped.  The comparisons are B14's arms, which ran the same games
on ecb4bc4, the commit before 9477c8b, with the old rule and `--push-growth 25` given where it was not the default.

| arm | games | level | options | compared with |
|---|---|---|---|---|
| q2-h | 3001-4000 | 2 | the defaults | h-choice-l2 (`--stop-quiet 0`), h-control-l2 (the mode before B13) |
| q2 | 4001-5060 | 2 | the defaults | l2-push25 (`--stop-quiet 0`) |
| q3-h | 3001-4000 | 3 | the defaults | h-choice-l3 (`--stop-quiet 0`) |
| off3-h | 3001-4000 | 3 | `--stop-growth off` | q3-h, h-choice-l3 |
| q3 | 4001-5060 | 3 | the defaults | l3 (`--stop-quiet 0 --push-growth 50`) |

*Work, not seconds.*  Another chain of the solver ran beside these on 44 threads, and B14's times were measured under
other loads: the seconds of an arm are 1.1 to 1.5 times its comparison's and mean nothing across studies, while the work
is the same at any load.  B14's rule, with work in place of seconds: X is *better* than Y when it has more games at
opt(n) for at most 10% more work, or the same games and points short for less work.  *Seeded work* counts the seeded
plays alone, which the stop acts on and the push does not add to.

*The analysis* ([b17.py](b17.py), output [out.txt](out.txt)) reads the arms and B14's; a game's line is the last line the
file has for it.  All 5,123 lines of the five arms pass its checks: unsound, the build, the arm's level, seed, threads
and options, `bound` equal to `parity` of
[parity_2_8191.jsonl.gz](../the-parity-bound-against-the-frame-bound-2026-10/parity_2_8191.jsonl.gz), no score above the
bound or opt(n), `prev.source` the table for the first game and `run` for every later one (an unseeded play's line has
`prev` null), and `growth` equal to the gap less the gap below.

## Results

Games at opt(n), with the halves in parentheses (3001-3500 and 3501-4000, 4001-4530 and 4531-5060); points short, work
and seconds for the whole range; the shares of games stopped and pushed, with the halves.

| arm | at opt(n) | points short | M work / 100 games | M seeded work / 100 | s / 100 games | stopped | pushed |
|---|---|---|---|---|---|---|---|
| q2-h | 954 (480, 474) | 1,396 | 10.5 | 8.0 | 507 | 19.2% (19.4, 19.0) | 8.6% (8.6, 8.6) |
| h-choice-l2 | 932 (479, 453) | 1,681 | 10.4 | 7.9 | 338 | 19.6% (19.6, 19.6) | 8.5% (8.6, 8.4) |
| h-control-l2 | 951 (478, 473) | 1,393 | 14.3 | 10.6 | 441 | 0 | 0 |
| q3-h | 960 (483, 477) | 1,286 | 17.4 | 12.6 | 767 | 19.5% (19.8, 19.2) | 8.5% (8.4, 8.6) |
| h-choice-l3 | 957 (482, 475) | 1,325 | 17.2 | 12.5 | 508 | 19.7% (19.8, 19.6) | 8.5% (8.4, 8.6) |
| off3-h | 976 (491, 485) | 625 | 25.3 | 20.4 | 1,024 | 0 | 8.7% (8.6, 8.8) |
| q2 | 1,039 (516, 523) | 572 | 8.9 | 6.9 | 704 | 22.2% (21.5, 22.8) | 6.9% (7.2, 6.6) |
| l2-push25 | 1,039 (516, 523) | 572 | 8.9 | 6.9 | 633 | 22.2% (21.5, 22.8) | 6.9% (7.2, 6.6) |
| q3 | 1,046 (516, 530) | 186 | 13.8 | 10.0 | 929 | 22.3% (21.5, 23.0) | 6.6% (7.0, 6.2) |
| l3 | 1,046 (516, 530) | 186 | 13.1 | 10.0 | 772 | 22.4% (21.5, 23.2) | 5.5% (5.7, 5.3) |

* **On 3001-4000 the rule gains for a little work.**  q2-h against h-choice-l2: +22 games at opt(n), 285 points fewer
  short, 1.010 times the work, better on the whole range and on both halves (+1 and +21 games).  q3-h against
  h-choice-l3: +3 games, 39 points, 1.008 times the work, better on all three.  B15 expected about 0.6% more work; the
  seeded plays took 1.0% more.  33 played lines of q2-h differ from h-choice-l2's, the first at 3198.
* **On 4001-5060 it changes no score.**  q2 and l2-push25 differ in the played line of 2 games, with the same score in all
  1,060 and 1.001 times the work, which the rule calls worse.  q3 and l3 differ in 3 games with the same scores and 1.051
  times the work (the seeded plays 1.001; the rest is the push at 25 playing 12 more games).
* **The streaks.**  On 3001-4000 level 2 goes from 15 streaks (68 short games) to 11 (46) and level 3 from 12 (43) to 9
  (40).  The rule ended the streaks of 3332 (1 game), 3750 (10), 3774 (1) and 3850 (10) at level 2, and of 3332, 3750 and
  3774 at level 3, where 3850 was at opt(n) already; it began none.  On 4001-5060 both rules have the same streaks: 4107,
  4134, 4225, 4914 and 5060 at level 2, the first three at level 3.
* **No arm scores below its comparison** with `--stop-quiet 0`, nor off3-h below q3-h.  Against h-control-l2 (no stop,
  no push, every eighth game played twice) q2-h is lower in 22 games, 562 points in all, in the streaks of 3174
  (3175-3178, 32 points each), 3384 (3384-3387, 47), 3565 (3568-3569, 41) and 3888 (3888-3894, 2; 3895-3899, 30), and
  higher in 17 (559 points), for 0.735 times the work.

The seven games of B15: the points short at the end, then whether the stop ended the rounds and how many ran.

| game | B15 expected | h-choice-l2 | q2-h | h-choice-l3 | q3-h | off3-h |
|---|---|---|---|---|---|---|
| 3332 | opt(n) | 1; stopped, 7 | 0; ran 9 | 1; stopped, 7 | 0; stopped, 12 | 0; ran 14 |
| 3384 | lost | 47; stopped, 9 | 47; stopped, 9 | 47; stopped, 9 | 47; stopped, 9 | 0; ran 19 |
| 3750 | opt(n) | 33; stopped, 10 | 0; ran 18 | 33; stopped, 10 | 0; ran 23 | 0; ran 23 |
| 3774 | opt(n) | 5; stopped, 9 | 0; stopped, 14 | 5; stopped, 9 | 0; stopped, 14 | 0; ran 23 |
| 3850 | opt(n) | 8; stopped, 8 | 0; stopped, 14 | 0; stopped, 8 | 0; stopped, 10 | 0; ran 16 |
| 3576 | opt(n) | 0; stopped, 7 | 0; stopped, 7 | 0; stopped, 7 | 0; stopped, 7 | 0; ran 13 |

4107 is 28 short in q2, q3, l2-push25 and l3, the stop ending its rounds at round 9, as B15 expected.  Every game B15
expected to go on to opt(n) did, at both levels.

*Level 3 with no stop.*  off3-h against q3-h: +16 games at opt(n) (+8 in each half), 661 points fewer short, 1.454 times
the work (1.616 seeded), "neither" by the rule.  The 16 games are in the streaks of 3174, 3384, 3565 and 3888, and off3-h
has 9 streaks of 24 short games where q3-h has 9 of 40.  Each added game costs 4.9 M work, against 11.5 M for the step
from q2-h to q3-h.

*The levels.*  Level 3 over level 2 adds 6 games of 1,000 on 3001-4000 (110 points) for 1.656 times the work, and 7 of
1,060 on 4001-5060 (386 points) for 1.548 times: 11.5 and 7.4 M work for each added game, where an average game at
opt(n) costs 0.110 and 0.091 M at level 2 and 0.181 and 0.140 at level 3.

## What it means

* **The default.**  `--stop-quiet 4` pays: 22 games and 285 points on 3001-4000 for 1.0% more work, better by the rule on
  both halves, and no score lost on 4001-5060.  B15 expected it to end four streak starts (3332, 3750, 3774, 3850) and it
  ended all four.  The gain is those four starts, so it is as much their luck as a rate.
* **The level.**  Of the two levels run with the defaults, level 2 gives the most games at opt(n) per unit of work: 96.8% of
  the 2,060 games at 10.5 and 8.9 M work per 100, against 97.4% at 17.4 and 13.8 for level 3.  Level 3 is for a user who
  values the last 0.6% of the games at more than 60% more work.  Level 1 is cheaper per game still (B14: 0.065 M per game
  on 4001-5060) but 6 games behind level 2 there under B14's options, and was not run with the push at 25.
* **The stop.**  3384 and 4107 are the rule's remaining losses: the stop ends their rounds at round 9, before the one late
  gain that B15 found in round 10 or 11.  A user who wants every game the mode can reach sets `--stop-growth off` and pays
  45% more work at level 3.  Whether level 2 with no stop buys games more cheaply than level 3 with it is open: B14's
  l2-stopoff gave +16 games for 36% more work on 4001-5060, under other options.

## What the data cannot tell

* **One seed, one build, two stretches.**  The gain is four streak starts and 33 of 1,000 played lines; another seed
  would move which games start streaks.
* **The games past 5060.**  The known games stand in for them.  4001-5060 shows no effect of the rule, so its effect on
  a longer chain is read off 3001-4000, where games are smaller.
* **Not run:** level 1 with the defaults, level 2 with no stop, a second seed.
* **Threads.**  The five processes ran 8 workers each (about 38 busy threads at the first sample) beside the thread that
  makes the next game's setup.

## Files

* [run_jobs.py](run_jobs.py): the driver of B14 (`nice -n 19 python3 -I run_jobs.py --bin TAXMAN --jobs jobs.txt --dir DIR
  --progress 1800`), a job a line of [jobs.txt](jobs.txt).
* [runs/](runs/): the arms' lines (`ARM.jsonl.gz`), their logs, `driver.log` and `pids.txt`.
* [b17.py](b17.py) (`python3 -I -B b17.py > out.txt`): the checks, the tables above, the streaks, the seven games, every
  game lower than its comparison and the levels.  It reads
  [b14.py](../tuning-the-unsound-mode-on-a-long-chain-2026-11/b14.py) and B14's lines.
* [out.txt](out.txt): its output.

## Commits

* [9477c8b](https://github.com/bvchess/taxman/commit/9477c8b) (main repository): the build of every run.  The study
  changed no code.
* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).
