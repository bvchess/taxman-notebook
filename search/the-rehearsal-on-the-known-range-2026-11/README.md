# The rehearsal on the known range (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-08.  Concluded 2026-11-09.

**Question.**  Past 5060 no game is proven, so how often the unsound procedure scores opt(n), and how many games it
leaves short, can only be estimated.  Run on the proven games 3001-5060 as if they were unknown, how often does it
score opt(n), and does its estimate of the streaks still short hold?

**Answer.**  The procedure scored opt(n) on 2,006 of the 2,060 games (97.4%) after pass 1, on 2,047 after pass 2 and on
2,050 (99.5%) after pass 3, and pass 4 raised nothing.  The four passes took 283 thread-hours.  The 10 games left lie in
two streaks, 3844-3847 and 4134-4139.  The estimate said about 0.5 streaks were left after pass 3, and 2 were.  One run,
one sequence of seeds.

## Method

*The words.*  A game is *short* when its best-known score is below opt(n), a *streak* is a run of consecutive short
games, its *root* is its lowest game, and a *miss* is a game short after a pass.  A game's *layer* is its number of
prime factors with repeats (12 is in layer 3).  The
[descent](https://github.com/bvchess/taxman/blob/bd6381b/solver/docs/unsound/shortfalls.md#the-descent) has roots of
its own, gains of a pass, which the table calls *descent roots*.

*The run.*  [run.sh](run.sh) ran the procedure as it runs past 5060: master
[bd6381b](https://github.com/bvchess/taxman/commit/bd6381b), the built-in table cut at 3000 ([`--known-to
3000`](https://github.com/bvchess/taxman/blob/bd6381b/solver/docs/unsound/best-known.md#a-rehearsal-on-proven-games)),
a best-known file that began empty, level 3, 44 threads, one pass at a time, from 2026-11-08 22:56 to 2026-11-09 05:22
(Pacific time).  Pass 1 used seed 1 and the default stop.  Pass k from 2 on used seed k and `--stop-growth off`, until a
pass raised no new streak.

*The estimate.*  If each pass finds a steady share c of the streaks still short, the streaks a pass finds fall by a
factor 1 − c from one pass to the next, and after pass k about (streaks found in pass k) × (1 − c) / c are left.  A pass
finds the streaks of the games it raised.

*The analysis.*  [analysis.py](analysis.py) (output [out.txt](out.txt)) recomputes every number below from the lines.  A
game's best-known score after pass k is the best of its lines in passes 1 to k, which the best-known file also gives;
the script checks that they agree.

## Results

| pass | at opt(n) | misses | streaks | points short | raised games | raised streaks | descent: roots, played again, raised | estimate of streaks left | thread-hours |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2,006 (97.4%) | 54 | 12 | 1,472 | | | 0, 0, 0 | | 54.8 |
| 2 | 2,047 (99.4%) | 13 | 4 | 211 | 47 | 10 | 11, 88, 6 | | 76.4 |
| 3 | 2,050 (99.5%) | 10 | 2 | 134 | 3 | 2 | 2, 16, 0 | 0.5 | 75.4 |
| 4 | 2,050 (99.5%) | 10 | 2 | 134 | 0 | 0 | 0, 0, 0 | 0.0 | 76.2 |

* **The table matches score.txt**, recomputed from the lines.  After pass 4 the streaks left are 3844-3847 and 4134-4139.
* **The estimate was too low.**  After pass 3 it was c = 1 − 2/10 = 0.80 and 2 × 0.2 / 0.8 = 0.5 streaks left, and after
  pass 4 it was 0.0.  Two were left both times.
* **A pass's own file can lose a game that its best-known file keeps**: 5060 scored 34 and 45 points below its
  best-known line in passes 2 and 4, and 3311 scored 26 below in pass 3.
* **Thread-hours** are 44 threads times the wall-clock hours of [run.log](run.log), 282.9 over 6.43 h in all.  They count
  the threads held, not CPU time; the games' seconds in the logs plus the repair's walks give 282.1.

### Streak survival

Pass 1's 12 streaks were 12 after pass 1, then 4 after pass 2, 2 after pass 3 and 2 after pass 4: pass 2 closed 8 of
12, pass 3 2 of 4 and pass 4 none of 2.

| streak | games | points short | root's rounds ended by the stop | closed in pass |
|---|---|---|---|---|
| 3174-3179 | 6 | 163 | no | 2 |
| 3192-3197 | 6 | 156 | yes | 2 |
| 3311 | 1 | 40 | yes | 2 |
| 3384-3387 | 4 | 188 | yes | 2 |
| 3565-3569 | 5 | 325 | no | 3 |
| 3723 | 1 | 3 | yes | 2 |
| 3844-3847 | 4 | 48 | no | not |
| 3888-3899 | 12 | 360 | no | 2 |
| 3968 | 1 | 3 | no | 3 |
| 4107 | 1 | 28 | yes | 2 |
| 4134-4139 | 6 | 130 | no | not |
| 4225-4231 | 7 | 28 | no | 2 |

* **Size and shortfall do not tell the survivors apart.**  The 8 streaks closed in pass 2 average 4.8 games and 121
  points short (up to 12 and 360), the 2 closed in pass 3 3.0 and 164, and the 2 survivors 4 and 6 games and 48 and 130
  points, or 12 and 22 points a game against 25 for those closed in pass 2.
* **How pass 1 ended a root's rounds may.**  Its stop ended the rounds of 5 of the 12 roots, and pass 2 closed all 5.  Of
  the other 7, pass 2 closed 3, pass 3 2 and 2 survived.  Pass 2 also changed the seed and added the descent, so this
  shows no cause.

### Where the streaks start

Pass 1's 2,060 lines are 247 primes, 867 repeats, 221 searched games at their ceiling (score(n) = score(n − 1) + n) and
725 searched games below it.  It left 54 games short: 12 roots (short while the game below is at opt(n − 1)) and 42
followers, of them 21 repeats, 5 primes and 16 searched games.

* **Every root was a searched game below its ceiling**, 12 of the 725, as it should be: a game at its ceiling is optimal
  if the game below is ([the ceiling
  lemma](https://github.com/bvchess/taxman/blob/bd6381b/docs/theory/neighbors.md#the-ceiling-lemma)), and so is a prime.
  No repeat was a root.
* **Roots are 1.7 per 100 such games**, and 2.2, 2.2 and 1.1 in layers 3, 4 and 5 or more, with 4 roots each:

| layer of n | games | searched below the ceiling | roots among them | per 100 of them |
|---|---|---|---|---|
| 1 (primes) | 247 | 0 | 0 | |
| 2 (all repeats) | 536 | 0 | 0 | |
| 3 | 527 | 184 | 4 | 2.2 |
| 4 | 364 | 181 | 4 | 2.2 |
| 5 or more | 386 | 360 | 4 | 1.1 |
| all | 2,060 | 725 | 12 | 1.7 |

## What it means

The procedure's record on proven games run as unknown is 97.4% at opt(n) after pass 1 and 99.5% after passes 3 and 4,
on 283 thread-hours.

The estimate was too low after pass 3 (about 0.5 left, in fact 2), and pass 4 found neither.  The streaks are not alike:
the easy ones are found first and the hard ones survive, so the estimate of what is left past 5060 needs a model that
allows for that, and the survival counts (12, 4, 2, 2) are its first data.  4134-4139 also survived [test
1](../a-second-pass-from-the-lines-above-2026-11/README.md), from 19 chains.  3844-3847 did not: test 1's file held it
at opt(n), so a chain of other settings reaches it.

It cannot tell more than that:

* **One run, one sequence of seeds**, with 12 streaks and 2 survivors.
* **The known range is easier than the games past 5060.**  In the production best-known file on 2026-11-09 at 04:00,
  the median gap of a game's line to the parity bound was 0.38 n in 4501-5000, where the lines are proven, and 0.51 to
  0.75 n in the bands of 500 games from 5001 to 8000 (the parity bound is known to 8191).  And 640 of the 2,000 games
  above 8000 had been raised since pass 1, by pass 2 and its push-down, against 47 of this range's 2,060 in its pass 2.
  So the share at opt(n) there is likely lower.  The estimate past 5060 rests on that range's own counts, with this run
  as its check.

## Files

* [run.sh](run.sh), [run.log](run.log): the four passes (`./run.sh` beside `taxman-bd6381b`, the release build of the
  change master holds as bd6381b, whose lines name it as commit 0900018 with a dirty tree, its commit before the merge)
  and their output.
* [p1.jsonl.gz](p1.jsonl.gz) to [p4.jsonl.gz](p4.jsonl.gz) and [p1.log](p1.log) to [p4.log](p4.log): each pass's lines
  and log, the lines gzipped with `gzip -9 -n`.  [best-known.jsonl.gz](best-known.jsonl.gz): the best-known file after
  pass 4.
* [score.py](score.py) and [score.txt](score.txt): the score after each pass, which run.sh asked for; it also wrote
  `scores-K.json`, not kept here.
* [analysis.py](analysis.py) (`nice -n 19 python3 -I analysis.py > out.txt`) and [out.txt](out.txt): the checks and the
  tables above, from the committed results and these files.

## Commits

* [bd6381b](https://github.com/bvchess/taxman/commit/bd6381b) (main repository): the build of every pass.  The study
  changed no code.
* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).
