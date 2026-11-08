# A second pass from the lines above (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-08.  Concluded 2026-11-08.

**Question.**  Folding the first-pass chains of the unsound mode on 3001-5060, with the built-in table cut at 3000,
leaves 33 of the 2,060 games below opt(n).  Does a second pass from the best-known lines close them, and does
`--above 8`, which adds trajectories from the best-known lines of the 8 games above each game, close more?  This is
test 1 of the rehearsal of the production passes on 3001-5060, which is planned.

**Answer.**  With `--above 8` the pass closed 26 of the 33 misses and 8 of their 10 streaks for 24.9 M work, without it
16 and 5 for 25.8 M.  The known range then holds 2,053 of 2,060 games at opt(n), or 2,043 without it, against 2,027
before.  With `--above 8` each of the 8 streaks closed at its first game, and in 7 the gain came from a trajectory that
began above the game.  One seed.

## Method

A game is *short* when its score is below opt(n), a *streak* is a run of consecutive short games (the [words of
B14](../tuning-the-unsound-mode-on-a-long-chain-2026-11/README.md#method)), and a *miss* is a game short in the first
pass.

*The first pass.*  [fold.sh](fold.sh) folded 19 chains of two studies, [tuning the unsound mode on a long
chain](../tuning-the-unsound-mode-on-a-long-chain-2026-11/README.md) (B14) and [the stop that waits for quiet
rounds](../the-stop-that-waits-for-quiet-rounds-2026-11/README.md) (B17), at levels 1 to 4 with seed 1 (12 chains cover
each game of 4001-5060 and 7 each of 3001-4000), into one best-known file, [start.jsonl.gz](start.jsonl.gz), on master
928ad6a with `--known-to 3000`.  A fold is a run over a chain's range with a copy of its file as `--out`: it plays nothing and offers
every line ([a rehearsal on proven
games](https://github.com/bvchess/taxman/blob/928ad6a/solver/docs/unsound/best-known.md#a-rehearsal-on-proven-games)).
The file has 980 of 1,000 games at opt(n) on 3001-4000 and 1,047 of 1,060 on 4001-5060, and its 33 misses lie in 10
streaks, 721 points short.

*The second pass.*  [arms.sh](arms.sh) played eight windows around the misses (81 games) at level 3 with
`--stop-growth off`, seed 2 and 22 threads, from 09:56 to 10:04 (Pacific time), the two arms at once, each from its own
copy of start.jsonl as its best-known file.  Arm a ran as it is, arm b with `--above 8`.  Work counts the steps of the
rounds and 32 for each neighborhood, of both plays of a game played twice.  [test1.py](test1.py) (output
[out.txt](out.txt)) checks every line and takes a game's line as its last; an arm closes a miss when its best-known
file holds opt(n) for it.

## Results

| | misses closed | streaks closed | points still short | M work | seconds | known range at opt(n) |
|---|---|---|---|---|---|---|
| start.jsonl | | | 721 | | | 2,027 of 2,060 |
| a | 16 of 33 | 5 of 10 | 294 | 25.8 | 461 | 2,043 of 2,060 |
| b (`--above 8`) | 26 of 33 | 8 of 10 | 133 | 24.9 | 443 | 2,053 of 2,060 |

The seconds are the games' wall time (the repair's walks add 9.2 and 8.8) and compare the arms, which ran at once.

* **Arm b closes everything arm a does and 10 misses more**: 3565-3566, 3723 and 4225-4231.  Neither moves 3968 or
  4134-4139.  The work for each miss closed is 0.96 M in arm b and 1.61 M in arm a.
* **No game fell below start.jsonl** in either best-known file, and the repair wrote no line again.

| streak | short at start | arm a | arm b |
|---|---|---|---|
| 3174 | 32 | closed, below 3173, round 2 | closed, above 3175, round 2 |
| 3179 | 3 | closed, below 3178, round 3 | closed, above 3180, round 1 |
| 3192-3197 | 156 | closed, the start's, round 9, unseeded play | closed, above 3198, round 2 |
| 3311 | 40 | closed, the start's, round 13 | closed, below 3310, round 13 |
| 3565-3566 | 130 | no gain | closed, above 3567, round 1 |
| 3723 | 3 | no gain | closed, above 3725, round 1 |
| 3888-3894 | 196 | closed, below 3884, round 8 | closed, above 3895, round 1 |
| 3968 | 3 | no gain | no gain |
| 4134-4139 | 130 | no gain | no gain |
| 4225-4231 | 28 | no gain | closed, above 4232, round 11, unseeded play |

A cell names the game whose survivors the last improving trajectory began from, and the round, at the streak's first
game.

*What the keys show.*  A line's `trajectories` names the game each trajectory began from and `improvements` the
trajectory and round of each gain, so the last improvement says which trajectory made the line.  A streak closes at its
first game, a *root* whose line a search raised, and the games after it follow (a repeat, a prime, or a search that
raises nothing past its start): arm b's 26 closed misses are 8 roots and 18 followers, arm a's 16 are 5 and 11.  Of
arm b's 8 roots, 7 came from a trajectory above the game, among them the roots of all three streaks only b closed.
Arm a's roots came from a game below (3174, 3179, 3888) or the start's trajectory (3192, in the push's unseeded play,
and 3311).  No line above held opt(n) outright: the survivors of the games above score 4 to 1,161 points below it at
all 8 roots, and six of the gains came in round 1 or 2.  That differs from the study of [repairing games from
above](../repairing-games-from-above-2026-11/README.md), where proven games above held opt(n) before any round for 65 of
73 hard games.  No arm of the study of [a share of tilted
neighborhoods](../a-share-of-tilted-neighborhoods-2026-11/README.md) improved 3968, 4134 or 4225; 4225 closes here.

*What they cannot show.*
* **The credit.**  A trajectory is added only if no earlier one began from the same set, so a set that a game below
  also gives is credited below.
* **The moves.**  The key says where the incumbent began, not how much of the line is the game above's moves.
* **The counterfactual.**  Neighborhood k works from trajectory k mod T, and T averages 3.2 in arm a and 6.3 in arm b,
  so the arms draw different neighborhoods from the first one.  Only the totals compare.
* **A restart.**  At 3192, 3565, 3888 and 4225 the first improvement is a round-0 one that scores what start.jsonl's
  line of the game does, so the trajectory began from a set as heavy as the first pass's.  A game starts from the moves
  for n − 1, and arm a's start scored 35 and 2 points less at 3565 and 3888.  Part of arm b's gain may be such a
  restart, not the moves of the lines above.

## What it means

A pass from the best-known lines with `--above 8` closes most of the streaks the first-pass chains left, for the work of
the pass without it, so the production passes use it.  It cannot tell more than that:

* **One seed**, one pass, 10 streaks.
* **A stronger first pass than a production one**: start.jsonl takes the better of 7 or 12 chains on each game, and a
  production first pass leaves more misses.
* **The windows hold the misses.**  What a full pass yields elsewhere, and its work there, are not measured; the full
  rehearsal on 3001-5060 is planned.

## Files

* [fold.sh](fold.sh) (`./fold.sh` beside `taxman-928ad6a`, a release build of 928ad6a, and a folder `fold/`): the fold.
  It wrote start.jsonl, which `gzip -9 -n` made [start.jsonl.gz](start.jsonl.gz).
* [fold/](fold/): the log of each fold.
* [arms.sh](arms.sh) (`./arms.sh` after fold.sh), its output [arms.log](arms.log): the second pass.
* [a/](a/), [b/](b/): each window's lines (`wFIRST-LAST.jsonl.gz`) and log, and the arm's best-known file after the
  pass.
* [test1.py](test1.py) (`python3 -I -B test1.py > out.txt`): the checks and the tables above.  It reads the helpers of [stopping and
  pushing by the gap](../stopping-and-pushing-by-the-gap-2026-11/b13lib.py) and the committed results.
* [out.txt](out.txt): its output.

## Commits

* [928ad6a](https://github.com/bvchess/taxman/commit/928ad6a) (main repository): the build of every run.  The study
  changed no code.
* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).
