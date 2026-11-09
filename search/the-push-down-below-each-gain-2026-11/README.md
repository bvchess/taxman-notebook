# The push-down below each gain (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-08.  Concluded 2026-11-09.

**Question.**  A pass over a range from the best-known lines plays the games in order, so the 8 games below a game whose
line beats its best-known one were played before that line existed, and never followed a trajectory from it.  Most games
stop at [the run's
ceiling](https://github.com/bvchess/taxman/blob/bd6381b/solver/docs/unsound/play.md#the-runs-ceiling), so a shortfall
carries up through them, and a gain found high in a streak means that the games below it may be short too.  Are the
games just below a gain raised more often than other games, and does a search from the gain's line find them?

**Answer.**  Yes, by a wide margin.  We searched the 8 games below each of pass 2's 23 breakthroughs (184 games, arm t)
and 184 games in random windows (arm c, the control).  Arm t raised 49 games in 10 streaks by 4,432 points in 13.2
thread-hours, arm c 6 games in 1 streak by 18 points in 14.8.  A follower then searched below every gain of pass 2, and
again below each gain it found: it raised 211 games in 27 streaks by 22,700 points in 102 thread-hours.  New streaks per
thread-hour came to 0.76 for arm t, 0.26 for the follower, 0.11 for pass 2 over pass 1 and 0.07 for arm c.  The unsound
mode searches below every gain in every run, as [the
descent](https://github.com/bvchess/taxman/blob/bd6381b/solver/docs/unsound/shortfalls.md#the-descent).  One seed.

## Method

*The words.*  A run *raises* a game when the best-known file takes the run's line of it over the line the file held; the
file's record names the run's file (`best_known.file`) and the score replaced (`best_known.was`), and the *points* are
the new score less the first `was`.  A *streak* is a run of consecutive raised games, and its *root* is its lowest.  A
pass's *breakthrough* is the first game of a streak of games it raised.  A *thread-hour* is a game's seconds times the
run's threads, in hours.  Pass 2 is the second pass of the production run over 5061-10000, from the lines of pass 1
(level 3, seed 2, no stop, `--above 8` but for 235 of its games).

*The mini-pass* ran from 2026-11-08 16:18 to 17:09 (Pacific time).  [windows.py](windows.py) chose the windows and
[minipass.sh](minipass.sh) ran them.  Arm t searched the 8 games below each breakthrough of pass 2 (23 breakthroughs, 22
windows, since two touch), arm c as many games in 23 random windows of 8, at least 16 games from any game pass 2 raised.
Both ran at level 3 with `--stop-growth off`, seed 3 and `--above 8`, on 20 threads an arm, the arms at once, from and
into the production best-known file, on master [f7b134c](https://github.com/bvchess/taxman/commit/f7b134c).

*The follower* ran from 2026-11-08 17:13 to 2026-11-09 06:37, while pass 2's two lanes (5061-9299 and 9300-10000)
played.  [follower.sh](follower.sh) ran [pushdown.py](pushdown.py) in a loop and searched the windows it printed, with
the mini-pass's options on 8 threads.  A gain of pass 2 is a game whose best-known line came from any file but pass 1's,
a root is a gain whose game below is no gain, and a round's windows are the 8 games below each root not yet taken,
merged where they touch, once the lane has played them.  A window that raises its bottom game makes a root below it, for
a later round.  Since 21:01 on 2026-11-08 pushdown.py ignores pass 3's files, which descend below their own gains; that
is its only change.

*The build.*  The push-down found far more than other games gave, so it became part of every run as B23, master
[bd6381b](https://github.com/bvchess/taxman/commit/bd6381b), with `--above 8` built in.  Pass 3 and [the
rehearsal](../the-rehearsal-on-the-known-range-2026-11/README.md) ran on it.

## Results

| | arm t | arm c |
|---|---|---|
| windows (games) | 22 (184) | 23 (184) |
| thread-hours | 13.2 | 14.8 |
| work, M | 34.6 | 35.5 |
| games raised | 49 (26.6 per 100 played) | 6 (3.3) |
| streaks | 10 | 1 |
| points | 4,432 | 18 |
| windows with a raise | 9 of 22 | 1 of 23 |
| streaks per thread-hour | 0.76 | 0.07 |

* **The games below a gain are raised 8 times as often**, and 9 of 22 windows gain against 1 of 23 (Fisher's exact
  test, p = 0.004).  Arm c's one streak is 7515-7520, 18 points; arm t's largest, 7424-7431, is 8 games and 2,728.
* **Nine of arm t's 10 streaks end directly below a game that pass 2 raised.**  The tenth, 6640-6646, stops below 6647,
  which no run raised; its window's other streak, 6648-6649, joins the breakthrough 6650.
* **In 8 of the 10 the root's line came from a line above**: from a trajectory that began from it in 7, and in
  6640-6646 from the repair's walk down from 6643, which a trajectory from 6650 made.  The roots of 6648-6649 and
  6732-6735 came from the game below ([records.tsv](records.tsv)).

| round | began | roots | windows | games played | games raised | streaks | points | thread-hours | streaks per thread-hour |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 17:13 | 20 | 18 | 157 | 60 | 11 | 3,613 | 14.3 | 0.77 |
| 2 | 19:06 | 17 | 17 | 136 | 40 | 7 | 5,057 | 17.6 | 0.40 |
| 3 | 21:26 | 31 | 27 | 245 | 73 | 13 | 10,112 | 39.2 | 0.33 |
| 4 | 02:31 | 20 | 20 | 160 | 28 | 6 | 3,020 | 25.4 | 0.24 |
| 5 | 05:51 | 5 | 5 | 40 | 10 | 2 | 898 | 4.4 | 0.45 |
| 6 | 06:26 | 1 | 1 | 8 | 0 | 0 | 0 | 1.3 | 0 |
| all | | 94 | 88 | 746 | 211 | 27 | 22,700 | 102.2 | 0.26 |

* **The rounds add to 39 streaks, and there are 27**: the streaks of a round touch those of earlier ones, and the 746
  games played are 641 different games.  Round 6 raised nothing, and with both lanes done the follower ended.
* **Twenty-five of the 27 streaks end directly below a game that an earlier run raised** (20 pass 2, 4 arm t, 1 arm c);
  8092-8095 and 8780-8783 do not.  The root's line came from a trajectory that began above it in 24 streaks, from the
  repair's walk from above in 1, from the game below in 1 and from the start in 1.

| | games played | thread-hours | streaks | streaks per thread-hour | points per thread-hour |
|---|---|---|---|---|---|
| arm t | 184 | 13.2 | 10 | 0.76 | 337 |
| the follower | 746 | 102.2 | 27 | 0.26 | 222 |
| pass 2 over pass 1 | 4,940 | 718.9 | 76 | 0.11 | 115 |
| arm c | 184 | 14.8 | 1 | 0.07 | 1 |

*How pass 2 was counted.*  A game is raised over pass 1 when its highest score in p2-l3s2.jsonl and u-l3s2.jsonl is
above its highest in a-l3, a2-l3 and b-l4: 676 of the 4,940 games, 82,687 points.  The thread-hours are the 4,940
plays' seconds times their threads (32, 40 or 44); the logs' seconds agree to 0.06%.  The carry (p2-carry.jsonl, one
game raised) is left out.

## What it means

Searching the games below a gain from the gain's line, again and down while it gains, finds far more per thread-hour
than a pass over other games: arm t at 7 times pass 2's rate and 11 times arm c's, the follower at 2.5 and 3.9 times,
with its yield falling from 0.77 in round 1 to 0.24 in round 4 (0.45 in the small round 5).  The gains are the lower
parts of the streaks that a pass found, which carried up from below: the pass raises a streak from the game where its
search first succeeds, and the games below, played before, stay short until a search starts from that line.  So the
unsound mode builds the push-down in as the descent.  It cannot tell more than that:

* **One seed** (3), and a control of 23 windows with one streak.
* **The follower searched from the lines as they stood** while the lanes still ran, a root's window once, and did not go
  back when a lane or another window later raised a line above it.
* **The runs shared the production best-known file**, so a gain of one could feed another: the follower searched from
  the lines of pass 2, the arms and its earlier rounds.  How far its lines fed pass 2's lanes is not measured.
* **Raised is not short.**  A game no run raised may be short; [the
  rehearsal](../the-rehearsal-on-the-known-range-2026-11/README.md) counts the games left short on a proven range.
* **The thread-hours are the games' seconds.**  By the wall clock the arms held 15.2 and 17.0 thread-hours, and the
  repair walks took 90 s (arm t), 92 s (arm c) and 741 s (the follower).
* **The descent is not the follower**: it runs inside the run, and this entry did not run it.

## Files

* [windows.py](windows.py), [windows.txt](windows.txt), [minipass.sh](minipass.sh), [minipass.log](minipass.log): the
  mini-pass (run in the production folder's `mini/`, where `../taxman-f7b134c` lies).
* [follower.sh](follower.sh), [pushdown.py](pushdown.py), [follower.log](follower.log), [handled.init](handled.init),
  [handled.txt](handled.txt): the follower, as it ran; handled.init holds the roots of the mini-pass and handled.txt
  the roots taken, a line a round.
* [t/](t/), [c/](c/), [pd/](pd/): each window's lines (`wLO-HI.jsonl.gz`, in pd/ `rK-wLO-HI.jsonl.gz` for round K, made
  with `gzip -9 -n`) and log.  The repair's lines of games below a window (6640 and 6641 of w6642-6649) are in the
  best-known file alone.
* [analysis.py](analysis.py) (`nice -n 19 python3 -I analysis.py > out.txt`, which reads the production folder's
  best-known file and pass files), [out.txt](out.txt), and [records.tsv](records.tsv), the best-known file's records of
  the arms' and the follower's files.  The script recomputes every number above, and checks that no line differs from
  the options above and that no other file's record of a game lies between those of its raises.
* [judge.py](judge.py), [judge.txt](judge.txt): the mini-pass's judge, which agrees, and its output.

## Commits

* [f7b134c](https://github.com/bvchess/taxman/commit/f7b134c) (main repository): the build of the mini-pass and the
  follower.  The study changed no code.
* [bd6381b](https://github.com/bvchess/taxman/commit/bd6381b): B23, the descent that the study led to.
* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).
