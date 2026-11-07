# Unseeded games above a short game (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  In a chain of the unsound mode a short game hands its shortfall on, since the games above start from its
line, and the repair cannot pull it up from lines made from it.  Does a game played with nothing from the games below
it, *unseeded*, reach opt(n) where the chain does not; does the repair's walk from such a line pull the short game up;
and does a run that plays some games twice, also unseeded, score more?  This is B11 of the unsound mode (`taxman solve
LO-HI --unsound --effort E --out FILE`).

**Answer.**  Yes to all three.  Unseeded, 11 of the 20 games above the stuck 4950 reach opt(n) at effort 4 (old
numbering; 524,288 work) and 13 at effort 7 (old numbering; 4,194,304 work), where E2's chain has 17 of the 20 short;
above the stuck 4914, 9 and 17.  An unseeded game is weaker than one seeded with the proven game below (55 against 62 of
P1's 63 at effort 4), so it is a way past a short line, not a better play.  The repair's walk from the unseeded line of
4951 raised 4950 to opt(4950), and the chain played on from it held opt(n) in all 18 games of 4950's streak.  A run
that plays every eighth game twice, as any game and unseeded, and keeps the better line (`--unseeded-every 8`, made
the default) took the chain of 4861-5060 at effort 4 from 182 to 198 of 200 games at opt(n), cutting 4950's streak from
18 games to 2 with no score lower, for 24% more time and 33% more work.  Past the table, on 5061-5260, it changed no
score, for 25% more time.  It rests on one seed and one long streak.

## Method

*The levels.*  The runs use master 56dcbdd's numbering of the levels of effort.  A study beside this one renumbers
them: old efforts 2 to 7 become levels 1 to 6, with the same budgets.  So effort 4 here is 524,288 work and effort 7
4,194,304.

*Unseeded.*  `--unseeded`, built for this study, plays every game with nothing from the moves of the games below it.
The game is searched, never played by the prime formula or as a repeat.  Its start (the greedy set, the dive and the
local search of a proven search's start) has no seed, and its rounds follow the start's trajectory alone, with no
trajectory of `--back`.  It has no run's ceiling, so its rounds run to the level's budget, or to the table's score
with `--stop-at-known`.  The tilt, the widening and the seed of the rounds are the defaults'.  Its line has no `prev`
and no ceiling, and `"unseeded":true`.

*Part 1: games alone.*  Each game was one command, `taxman solve N --unsound --effort E --unseeded --stop-at-known
--threads 4 --out FILE` ([run_games.py](run_games.py)).  The games were 4951-4970 and 4915-4934
([games-above.txt](games-above.txt)), the 20 above each of the stuck 4950 and 4914, at efforts 4 and 7, and P1's 63
([games-p1.txt](games-p1.txt)) at effort 4.  A level runs the rounds of the levels below first, and with
`--stop-at-known` a game ends at the same round at every level once it reaches opt(n).  So a game at opt(n) at effort
4 has the same line at effort 7, and the arm of effort 7 played only the 20 games that effort 4 missed.  Against them
stand the same games played normally from the proven game below (`--from-known`, the defaults).  For the games it has
(4928, 4929, 4952, 4953, 4970 and P1's 63), that is [race R1](../a-share-of-tilted-neighborhoods-2026-11/README.md)'s
arm K25W4 at effort 7, read at effort 4 where its improvement's work settles it; the other 35, and 4116, which R1's
line does not settle, were run here at effort 4.

*The walk.*  [make_walk_file.py](make_walk_file.py) made a file of
[E2](../the-datasheet-of-the-unsound-mode-2026-11/README.md)'s chain of 4861-5060 at effort 4, played on: its lines of
4861-4950, with `"repaired":null` added, which this build's reader needs, then the unseeded line of 4951, the lowest
game above 4950 that reached opt(n).  A run that opens a file takes up the repair's walk from its last line, so `taxman
solve 4951-4951 --unsound --effort 4 --threads 4 --out FILE` walked down from 4951 and played nothing.  The chain was
then played on from the walked file to the game that ended the streak in E2, `taxman solve 4952-4968 --unsound
--effort 4 --threads 3`.

*Part 2: games played twice.*  Four chains at once, each `taxman solve LO-HI --unsound --effort 4 --unseeded-every K
--seed 1 --threads 5 --out FILE` with the other defaults, the repair among them ([run_chains.py](run_chains.py)): K = 8
(*with*) and 0 (*without*), over 4861-5060, from the table's 4860, and 5061-5260, from the table's 5060.  Each chain
used 6 threads, its 5 and the one that makes the next game's setup.

*The builds and the machine.*  Master [56dcbdd](https://github.com/bvchess/taxman/commit/56dcbdd) with the study's
code, release without fat LTO, at -j 4: Part 1 and the walk with `--unseeded` alone (`taxman-b11-p1`), Part 2 with the
code of the commit (`taxman-b11`, before the default and the docs changed).  Every line the study wrote records
`"build": {"commit":"56dcbdd...","dirty":true}`.  The commit, rebased onto master 19a6c24, which numbers the levels one
lower, gives the same lines: its run of 4861-4880 at level 3 on 20 threads is Part 2's chain with, line for line, but
for the times, the threads, the build and the level's number ([rebase/](rebase/)).  Nothing in a line depends on the threads.  The times are of a machine
of 88 threads shared with another study of up to 56, at nice 19, on 2026-11-07 (Pacific time): Part 1 from 11:40 to
12:31, the walk at 11:40 and from 12:19 to 12:31, Part 2 from 12:32 to 14:17.

## Part 1: what a game makes of its board alone

Games at opt(n), each alone, with `--stop-at-known`:

| games | from the proven game below, effort 4 | effort 7 | unseeded, effort 4 | effort 7 |
|---|---|---|---|---|
| 4951-4970, above the stuck 4950 | 20 of 20 | 20 | 11 | 13 |
| 4915-4934, above the stuck 4914 | 20 of 20 | 20 | 9 | 17 |
| P1's 63 | 62 of 63 | 63 | 55 | |

* **Unseeded, a game reaches opt(n) above a stuck game where the chain does not.**  In E2's chain at effort 4 the games
  4950 to 4967 fall 43 to 176 short.  Unseeded, 4951 to 4960 reach opt(n) at effort 4, after 49,755 to 149,647 work,
  and 4964 and 4969 at effort 7; 4961 to 4967 end 110 short at effort 4, and all but 4964 at effort 7 too.  Above 4914,
  which is short in E2's chains at efforts 1 to 3, 9 games reach opt(n) at effort 4 and 17 at effort 7.
* **Unseeded is weaker than seeded with the proven game.**  Seeded from the proven game of n − 1, every game of the 40
  holds opt(n) at effort 4, most before any round.  Unseeded, a game needs rounds, and of P1's games it misses 8 at
  effort 4 (3441, 3567, 3723, 3741, 3850, 4104, 4136 and 4914, 1 to 75 short), against 1 seeded (3723, 3 short).  So
  the unseeded play is no replacement for the seeded one, only a way past a short line.
* **Its start costs more.**  The start of an unseeded game took a median 20 s with its setup, alone on 4 threads,
  against 7.7 s from the proven game, since its local search starts from the greedy set, lower than a seed.  A game
  that reached opt(n) at effort 4 took a median 24 s, one that ran the budget 91 s, and one that ran effort 7's 594 s.

[part1-out.txt](part1-out.txt) has every game: the work at which each arm reached opt(n), or how far short it ended.

## The walk from the unseeded 4951

The repair's walk from the unseeded line of 4951 replaced E2's line of 4950, 143 short, by opt(4950): what survives of
the unseeded game of 4951 in 4950 is an optimal game of 4950, as it is of the proven 4951 (B10).  The walk took 3.0 s,
most of it setting up boards again.  The chain played on from the walked file then held opt(n) in every game from 4952
to 4968 ([walk-out.txt](walk-out.txt)):

| games 4950-4968 at effort 4 | short games | the streak of 4950 |
|---|---|---|
| E2's chain | 18 | 18 games, 143 short at 4950, ended by 4968 |
| with the unseeded 4951 and the walk, played on | 0 | none |

So one unseeded game above the stuck game removed the whole streak: the walk repaired the game below it, and the games
above started from opt lines.  4951 is a prime in the chain, played by the prime formula from 4950's short line, so a
run that played only its searched games twice would have passed it by.

## Part 2: games played twice

*The design* ([unsound.md, "Games played twice"](https://github.com/bvchess/taxman/blob/5b27523/solver/docs/unsound.md#games-played-twice)).
`--unseeded-every K` plays a game whose n is a multiple of K twice: as any game is, then unseeded on the same board, as
`--unseeded` plays it; a prime, which has no board, sets one up.  The line is the better play's, the seeded one on a
tie, as that play alone writes it, with `other`, what the other play came to (its method, score, rounds, steps, work and
seconds).  So the games above start from the better line, and the repair walks down from it as from any line.

* **Every K-th game by n, not a trigger.**  Nothing in a line tells a short game from an optimal one: E2 found that
  neither the ceiling, nor the rounds' improvements, nor the score of n + 1 shows the shortfalls.  A choice by n alone
  keeps a line a function of the game, its start, the moves it starts from, the level, the seed and the options, never
  of the threads or of where a run began.  A game is played twice whatever its method, since a repeat hands a shortfall
  on every time (E2: 0 recoveries in 81 primes and repeats after a short game).
* **The cost, and the budget.**  Each play counts against a budget of its own, the level's.  The unseeded play has no
  ceiling, so it runs the whole budget, and a game played twice does up to twice a level's work.  The line's `work` is
  its own play's, and `other.work` the other's.  With K = 8 that is a full budget for one game in 8, expected at about
  a third more work than a chain's, where some searched games stop at the ceiling and primes and repeats do none.
* **K = 8.**  A streak then ends within 8 games of where it starts, if the unseeded play at the next multiple of 8
  reaches a better score; above 4950 the unseeded games of Part 1 reach opt(n) within effort 4's budget.  No other K was
  measured.

*The known range.*  The streaks are written as in E2: the game where each starts, its length, its shortfall at the first
game, and the game that ended it ([part2-out.txt](part2-out.txt)).

| 4861-5060, effort 4 | games at opt(n) | streaks of short games | work per 100 games | seconds per 100 games |
|---|---|---|---|---|
| without | 182 of 200 (91.0%) | 4950 (18, 143; 4968) | 21.3 million | 2,451 |
| with, K = 8 | 198 (99.0%) | 4950 (2, 143; 4952) | 28.4 million (+33%) | 3,029 (+24%) |

* **The unseeded play of 4952 ended the streak.**  It reached opt(4952), 143 above the seeded play, and 4953 to 4967
  started from it and held opt(n).  4950 and 4951 stay 143 short: what survives of 4952 in 4950 is no better (of the
  proven 4952 it is 2,468 short of opt(4950), B10), and 4951 is a prime played from 4950.  The unseeded play of 5040
  reached opt(5040), 11 above the seeded play, so the streak of 5040, which the repair ends after 3 games without it
  (from 5043), never began.
* **The unseeded play scored more than the seeded one in 2 of the 25 games played twice**, as much in 15, and less in 8,
  by 4 to 394.
* **No score was lower.**  The 16 games whose scores differ are 4952 to 4967, each higher by 43 to 176.
* **The time.**  The other plays of the 25 games played twice, 23 of them unseeded, took 1,704 of the 6,057 s of the
  games, an unseeded play a median 76 s on 5 threads, and the chains' wall times were 4,916 s without and 6,069 s with (+23%), from their files' last writes
  ([part2/ends.txt](part2/ends.txt)).  The repair's walks took 10 to 13 s a chain.

*Past the table.*  On 5061-5260 no score differs, and no line's moves.  The unseeded play of 5104 scored 15 above its
seeded play and was kept, and the chain went on from it; without, the repair's walk from 5106 replaced 5104 and 5105 by
the same moves, as in B10.  The unseeded play scored more in 1 of the 25 games played twice, as much in 20, and less in
4.  The cost was 25.8 against 18.7 million work per 100 games (+38%) and 3,136 against 2,511 s (+25%); the wall times
were 5,036 and 6,284 s.

*The chains without are master's.*  The chain without of 4861-5060 is E2's line for line but for 5040 to 5042, which
the repair raised (B10), and the one of 5061-5260 is B10's chain with the repair, line for line.

## Decision

Kept, on by default (`--unseeded-every 8`; `--unseeded-every 0` turns it off), in code commit
[5b27523](https://github.com/bvchess/taxman/commit/5b27523), on master 19a6c24, whose levels are numbered one lower:
the runs' effort 4 is its level 3.  The tail behind
a stuck game is the main loss of the unsound mode at every level from effort 1 up (81 to 87% of the short games in E2),
and more effort does not cut it: in E2, levels 5 and 6 added nothing to level 4, at twice the time a level.  Playing every eighth game
twice cuts the tail for about a quarter more time.  The evidence is one long streak in the known range and none past it;
a run that meets no stuck game pays the quarter for nothing.  `--unseeded`, every game unseeded alone, stays as a
measuring option.

What would reopen it: the full measurement (more seeds, levels and ranges) finding the gain too rare for the cost, or a
cheaper K or unseeded level doing as well.

## What is left

* **Other K, and an unseeded play at a lower level** than the game's, which would cost less; neither was measured.
* **The full measurement:** levels 1 to 3, where E2 found more streaks (4914's among them), and 5 to 7, more seeds,
  runs of 1,000 games, and more of the range past the table.
* **The games between a stuck game and the next game played twice** stay short unless what survives of the line above
  beats them, as 4950 and 4951 did here.

## Files

The commands ran in the study's scratch folder.  The lines are gzipped, a file an arm; [optlib.py](optlib.py) reads
opt(n) from the committed results and the last line of each game of a file.

* [run_games.py](run_games.py), [games-above.txt](games-above.txt), [games-p1.txt](games-p1.txt), [part1/](part1/):
  Part 1's arms, a game a command, six or four at once (`nice -n 19 python3 -I run_games.py --bin taxman-b11-p1
  --jobs JOBS --dir part1 --parallel P`, JOBS a line `ARM N` a game).  `u4` and `u7` are unseeded at efforts 4 and 7,
  `s4` from the proven game below at effort 4; the logs have each command and its time.
* [part1.py](part1.py) and [part1-out.txt](part1-out.txt) (`python3 -I part1.py`): Part 1's tables, reading R1's
  lines from its entry.
* [make_walk_file.py](make_walk_file.py), [walk/](walk/): the walk test.  `e4-walk-4951` is the file made (`python3 -I
  make_walk_file.py cont-e4.jsonl 4951 u4/4951.jsonl FILE`) and walked (`taxman-b11-p1 solve 4951-4951 --unsound
  --effort 4 --threads 4 --out FILE`), `e4-on-4951` a copy of it played on (`taxman-b11-p1 solve 4952-4968 --unsound
  --effort 4 --threads 3 --out FILE`), each with its log.
* [walk.py](walk.py) and [walk-out.txt](walk-out.txt) (`python3 -I walk.py
  ../the-datasheet-of-the-unsound-mode-2026-11/continue/cont-e4.jsonl.gz walk/e4-on-4951.jsonl.gz 4948 4970`): the
  streak before and after.
* [run_chains.py](run_chains.py), [part2/](part2/): Part 2's four chains (`nice -n 19 python3 -I run_chains.py --bin
  taxman-b11 --dir part2 --threads 5`), with their logs and the times of their files' last writes
  ([part2/ends.txt](part2/ends.txt)).  A log's exit line for a chain without was written when the chain with beside it
  ended, so its time is not that chain's.
* [part2.py](part2.py) and [part2-out.txt](part2-out.txt) (`python3 -I part2.py WITHOUT WITH` for each range): Part 2's
  tables.
* [check.py](check.py) and [check-out.txt](check-out.txt) (`python3 -I check.py part1/*.jsonl.gz walk/*.jsonl.gz
  part2/*.jsonl.gz`): every line unsound, of the study's build where the study wrote it, no score above opt(n), and the
  better play kept.
* [rebase/](rebase/) and [same.py](same.py): the rebased commit's run (`taxman solve 4861-4880 --unsound --effort 3
  --seed 1 --threads 20 --out FILE`) and its comparison with Part 2's chain with (`python3 -I same.py
  rebase/with-l3-4861.jsonl.gz part2/with-e4-4861.jsonl.gz`, in [rebase/same-out.txt](rebase/same-out.txt)).
