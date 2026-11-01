# The gate on whole games (2026-10)

Part of the [lab notebook](../../README.md).

Started 2026-10-31.  Concluded 2026-11-01.

**Question.**  Which gate policy makes the full chain of games 1 to 5060 the fastest?  The gate is the gap from which a
node branches on the conflict that conflict branching chooses
([the design](https://github.com/bvchess/taxman/blob/7a856a3/solver/docs/design/search.md#conflict-branching)).

**Answer.**  A fixed gate of 300 from the root, with no gate trial.  On the seven whole games that both policies
finished it took 0.18 to 0.56 of the hours of the policy it replaces (a gate of 1,200, then a trial that picks a gate
after 50 million steps), and it finished 5052 in 1.97 hours where that policy had not in 3.0.  This overturns the trial
of [a gate for each game](../a-gate-for-each-game-2026-10/README.md), which rested on 24 small units of a search, where
a gate of 300 took 1.70 times the CPU of 1,200.  Those units lie deep in a search, and the gate matters most at the top
of the tree, which the old policy builds at 1,200 before its trial runs.

## Method

*The policies.*  The re-run of the chain (tag `rerun-2026-10`, commit 3ca11bf) searched every game with
`--gate 1200 --gate-trial 1000,800,600`.  It starts at a gate of 1,200, and once the search has taken 50 million steps
a trial solves 24 of its units under each gate and keeps the gate of least CPU.  We call this the re-run's policy (the
folders of the runs call it `default`).  The other policy is a fixed gate, `--gate 300`, with no trial.  Every run of
the study used the re-run's build, so only the gate differs.

*The reason.*  The re-run took 997 million nodes and 1.30 hours of its own search on 4875, and 901 million nodes and
1.19 hours on 4879.  The original chain (the
[committed file](https://github.com/bvchess/taxman/blob/7a856a3/results/optimal.jsonl.gz), build a88dc7f, whose gate was
300) took 186 million nodes and 0.94 hours on 4875, and 181 million nodes and 0.64 hours on 4879.  A game's hours are
the `seconds.own` of its line, else its `seconds.search`.

*Phase A, units.*  22 games, the costliest of the original chain by own hours (4890 to 5060), each searched on four
threads for 5,400 s, eleven at a time, with `--gate 1200 --gate-trial 2000,1000,800,600,400,300,150
--gate-trial-plan after=15000000`.  The trial ran at 15 million steps and wrote its CPU under each of eight gates.  This
is the method of [the October entry](../a-gate-for-each-game-2026-10/README.md), on more games and more gates.

*Phase B, a game in the re-run's setup.*  The first try, 4875 and 4879 with the lines of games 1 to n - 1 in `--out`,
did not start: the solver refuses an `--out` file that holds the line of n - 1 alone, because it checks the game each
line was built from.  The second try, B2, ran 4875 at a gate of 300 on 88 threads with its lines 1 to 4874 and the
carried nogoods of 4872, as the re-run had set it up.

*Phase C, whole games side by side.*  4875, 4879, 4893 and 5052 under each policy, 4875 at a gate of 150, and 4984 at a
gate of 300.  One run at a time on 88 threads with the re-run paused, all with `--use-prev --force-search` (the game
before from the built-in table, no carried nogoods), capped at 3 hours.

*Phase D, more games in the re-run's setup.*  3942, 4192 and 3441 at a gate of 300, set up as in B2, against the
re-run's lines of the same games.  They are the first, fifth and third costliest games below 4875 in the re-run's file
(the second and fourth, 3940 and 3440, neighbor 3942 and 3441).

*Comparing hours.*  The pairs of phase C are like for like: one setup, each run alone on the machine.  The re-run's
lines are not, since their `seconds.own` counts the time a game was the oldest of its window, which is not a game's cost
where games share threads.  For the pairs against the re-run, B2 and phase D, the nodes are the check.

## Results

**1. On the trial's units, gates of 600 and below lose and a trial gains 6%.**  The 22 games hold 151.4 hours of own
search in the original chain, 79% of the 191.3 hours of games 4875 to 5060.  Each search stopped at its limit with 74 to
91 million nodes, and its trial took its 24 units at 15.1 to 15.8 million steps.  Weighted by those hours, the CPU of
the units under each gate against the gate of 1,200 projects:

| gate | 150 | 300 | 400 | 600 | 800 | 1,000 | 1,200 | 2,000 |
|---|---|---|---|---|---|---|---|---|
| projected CPU | 2.858 | 1.704 | 1.327 | 1.048 | 0.989 | 0.990 | 1.000 | 1.064 |
| games of 22 under 1.000 | 0 | 2 | 9 | 17 | 17 | 16 | | 7 |

A trial that keeps the gate of least CPU projects 0.936 (0.937 with the solver's margin of 3%), over 1,200 to 600 as
over all eight gates.  At 300, 20 of the 22 games took 1.04 to 2.82 times the CPU of 1,200, and only 4893 and 4968 took
less (0.97 and 0.96).  The searches kept 600 on eleven games, 1,200 on six, 800 on three, and 400 and 1,000 on one
each.  The two heaviest games, 4983 and 4984, hold 41% of the weight, and both lose at 600 (1.09 and 1.46 times) and at
300 (1.80 and 2.67 times).  The units said a trial wins, and a low fixed gate loses.

**2. Whole games said the opposite.**  The hours and the nodes, in millions, of a fixed gate of 300 against the policy
it replaces:

| game | setup | gate of 300 | the policy replaced | hours | nodes |
|---|---|---|---|---|---|
| 4875 | B2 | 0.252 h, 125 | the re-run: 1.30 h, 997 | 0.19 | 0.13 |
| 4875 | C | 0.287 h, 173 | the re-run's policy: 1.252 h, 1,141 | 0.23 | 0.15 |
| 4879 | C | 0.280 h, 167 | the re-run's policy: 1.273 h, 1,152 | 0.22 | 0.15 |
| 4893 | C | 0.400 h, 221 | the re-run's policy: 1.111 h, 972 | 0.36 | 0.23 |
| 5052 | C | 1.974 h, 1,113 | the re-run's policy: not done at 3.0 h, 2,610 | under 0.66 | under 0.43 |
| 3942 | D | 0.134 h, 140 | the re-run: 0.74 h, 804 | 0.18 | 0.17 |
| 4192 | D | 0.137 h, 82 | the re-run: 0.53 h, 369 | 0.26 | 0.22 |
| 3441 | D | 0.320 h, 250 | the re-run: 0.58 h, 527 | 0.56 | 0.47 |

* **The seven finished pairs** take 0.18 to 0.56 of the hours and 0.13 to 0.47 of the nodes.
* **Every trial chose 600.**  Each of the four runs of the re-run's policy chose 600 at its trial (at 52 to 55 million
  nodes).  The three that finished took 4.4 to 6.9 times the nodes of the fixed gate, and 5052's had taken 2.3 times by
  its cap.  The re-run's own trials on 3441, 4192, 4875 and 4879 chose 600, and its trial on 3942 chose 1,000.
* **Phase C reproduces the re-run.**  Its runs of the re-run's policy took 0.96 and 1.07 of the re-run's hours on 4875
  and 4879.
* **A gate of 300 beats 150.**  On 4875 a gate of 150 took 92 million nodes against 173 million, and 0.325 hours
  against 0.287: a node at 150 costs 2.1 times a node at 300.
* **The nodes at 300 are close to the original chain's**: 173 and 167 million on 4875 and 4879 against 186 and 181
  million, 0.93 and 0.92 of them.
* **4984 did not finish.**  At 300 it reached 1,851 million nodes at its cap of 3 hours.  The original chain's line of
  it holds 3,873 million nodes and 17.6 hours.  The run of the re-run's policy was stopped after 14 s when phase D
  began, and 4968, the last game planned for phase C, did not run.

**3. Why the units misled.**  The units come from a checkpoint deep in a search: 15 million steps in phase A, 52 to 55
million nodes in the trials of phase C.  Deep in a search a lower gate costs more than it saves, which is what the
units measured.  At the top of the tree a lower gate saves most, and the re-run's policy builds the top at 1,200: after
its trial switched to 600 the three games that finished still took 4.4 to 6.9 times the nodes of the fixed gate from the
root.  So a gate that is right for the units of a checkpoint is the wrong policy for a game.  No run isolates the top of
the tree (a gate of 1,200 for the first steps and 300 after would), so this reading fits the runs and is not tested.

The weak assumption of [the October entry](../a-gate-for-each-game-2026-10/README.md) was that a game's units say what
its whole search does (its result 6 calls it the weak one).  Its 4984 evidence was units as well, in the 60 units of its
panel and in the sweep of 2026-10-27 on 30 fresh and 12 hard units of 4984
([the sweep](../the-root-gap-and-the-size-of-a-game-2026-10/README.md#2026-10-27-a-sweep-of-the-settings-on-game-4984)).
[The choice of the conflict at lower gates](../the-choice-of-the-conflict-at-lower-gates-2026-10/README.md) was measured
on 60 units a game too, and we have not repeated it on whole games.

**4. Small games can grow at 300.**  The tripwire tests pin the nodes of small searches, and seven pins moved with the
default, all up, by 1.02 to 1.79 times: five of game 1000's and two of game 800's.  Game 1000 went from 2,026 to 2,841
nodes by default and from 2,991 to 5,361 with nogoods off.  The scores never move.  The cost falls on small games, and
the costliest games decide the chain: in phase D all three games run, among the five costliest below 4875, gained
(result 2).

**5. The cost of the method.**  Phase A took 3.0 hours on 44 threads (two waves of eleven games) and misled.  B2, one
whole game, took 15 minutes (19:01 to 19:17 PDT on 2026-10-31) and overturned it, so a whole game belongs before the
units.  After a fixed gate of 300 had finished, the study let the re-run's policy run to its end or its cap on the four
games of phase C, 6.6 hours in all.  A race decides as well: cap the slower arm at 1.2 times the winner's time, which
would have taken 3.5 hours here.

## Decision

The default became a fixed gate of 300 with no trial (commit 200c122): `CONFLICT_BRANCHING_GAP` went from 1,200 to 300,
and the trial runs only where `--gate-trial GATES` asks for it, as a way to measure.  The commit records the tripwire
pins that moved, and [gate-trial.md](https://github.com/bvchess/taxman/blob/7a856a3/solver/docs/design/gate-trial.md)
holds the study.  It was made at 05:51 PST on 2026-11-01, on four games of phase C; phase D (07:14 to 07:50 PST) agreed
with it.  Commit aaba59b (07:36 PST) added to each game's line the seconds `cpu`, `active` and `waiting`
and the stamps `started` and `finished`, so that a run's cost is read from its lines.  A full run of games 1 to 5060
started at 08:24 PST on 2026-11-01 with that build.  The re-run stopped at 4879 and is kept as a record.

What would reopen it, the likeliest first:

1. **The full run's lines.**  A game at a gate of 300 that takes much longer than the original chain's line of it.
   4984 is the first to watch: 4983 and 4984 hold 41% of phase A's weight, 4984 had not finished at 3 hours, and 4983
   was not run whole.
2. **A gate scaled to the game**, a fraction of the root gap: not tried on whole games.
3. **A switch inside a game**, 1,200 for the first steps and 300 after: it tests the reading of result 3.

## Files

The runs were on a machine of 88 threads, in a folder of their own: `a/`, `b/`, `c/` and `d/` (a folder a run, with its
`out.jsonl`, checkpoints and carried nogoods) and `logs/` (`study.log` and the standard error of each run).  The
`out.jsonl` files of the runs of phases B and D hold the lines 1 to n - 1 of the games (up to 36 MB), and the logs of
phase A are 31 KB each, so none is copied.  Copied here:

* `run-study.sh` (phases A and B), `run-b.sh` (B2), `run-c.sh` (C) and `run-d.sh` (D): the scripts as they ran, with
  their paths replaced by the environment variables `STUDY_DIR`, `TAXMAN`, `CHAIN_DATA` and `RERUN_SH`, which default to
  places beside the script.  Each pauses the re-run for its phase and resumes it on exit.
* `study.log`: `logs/study.log`, the timeline and each run's result line.  Its times are the machine's Pacific time, PDT
  until the clocks went back at 02:00 on 2026-11-01 and PST after, so that 01:00 to 02:00 occurs twice (the 118 minutes
  of 5052 at a gate of 300 show as 58 between 00:14:14 and 01:12:40).  The trial line that it quotes for each game of
  phase A is cut at 60 characters.
* `phase-a-trial-lines.txt`: the trial line of each of phase A's 22 games, made in `logs/` by
  `grep -h "gate trial" a-*.err | sort -t= -k2 -n`.
* `phase_a.py` and its output `phase-a-cpu.txt`: result 1.
  `TAXMAN_RESULTS=results/optimal.jsonl.gz python3 phase_a.py > phase-a-cpu.txt`, the file as of commit 7a856a3.
* `whole_games.py` and its output `whole-games.txt`: the hours and nodes of result 2, from the last line of each
  run's `out.jsonl`, the re-run's results file and the original chain's.
  `STUDY_DIR=... RERUN_RESULTS=... TAXMAN_RESULTS=... python3 whole_games.py > whole-games.txt`.

## Commits

On master of [bvchess/taxman](https://github.com/bvchess/taxman), all 2026-11-01:

* 200c122: the default search policy is a fixed gate of 300 with no gate trial (`src/search/mod.rs`, the tripwire pins
  in `tests/tripwires.rs`, the docs).
* aaba59b: a game's line says what it cost and how long it took.
* 7a856a3: STATUS records the full run in flight.

The study ran on the re-run's build, 3ca11bf (tag `rerun-2026-10`).  The original chain's lines of 4875 and 4879 come
from build a88dc7f.
