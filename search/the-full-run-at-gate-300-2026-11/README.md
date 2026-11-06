# The full run at gate 300 (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-01.  Concluded 2026-11-06.

**Question.**  With the policy that [the gate entry](../the-gate-on-whole-games-2026-10/README.md) chose, a fixed gate
of 300 with no gate trial, how long does the chain of games 1 to 5060 take on one machine, and where did that policy win
or lose against the runs before it?

**Answer.**  The chain took 116.6 hours of wall time on 88 threads, from 08:24 PST on 2026-11-01 to 05:00 PST on
2026-11-06, and 10,149 CPU hours.  On games 1 to 4879 it took 0.63 of the hours of the re-run (27.3 against 43.6, on the
same machine), and on games 4875 to 5060 0.47 of the hours of the original file (92.0 against 197.6).  It won on the
long stretches and lost on patches of consecutive games: on 12 games to the re-run's gate of 1,200 with the trial, by up
to 10.5 times the hours (4433), and on every game searched from 4984 to 5022 to the original file's policies there (a
switch to off at 4984, then a gate of 1,200), by 1.3 to 3.4 times the nodes (4991, 4992, 4995 and 4998 by 2.1 to 3.4
times the hours).  From 5024 to 5060 it won on every game, at 0.23 to 0.41 of the nodes.  The two games that the gate
entry had not run whole finished at 300: 4983 in 12.5 hours and 4984 in 11.4, a fifth of the run's hours between them.

## Method

*The run.*  `solver/tools/cloud/chain.sh 5060` ran games 1 to 5060 in order on the build of commit aaba59b, with a
window of 4 games, on all 88 threads of one machine (two Intel Xeon E5-2699 v4), with the workers at idle priority and
each search reading the nogoods that earlier games learned.  The build's defaults gave it a gate of 300 and no gate
trial.  One invocation ran it, so no game was resumed.
[results/runs.md](https://github.com/bvchess/taxman/blob/5bd5d48/results/runs.md) has the command and the options, and
`results/optimal.jsonl.gz` of that commit holds the run's lines, byte for byte.

*A game's hours.*  Each file records a different clock, so each is read by its own:

* **the run:** `seconds.active_all_runs`, the time the game had at least one worker, from its setup to its line ([the
  clock](https://github.com/bvchess/taxman/blob/aaba59b/solver/frame/src/solver/clock.rs));
* **the re-run:** `seconds.own`, the time the game was the head of the window (its oldest game) with its search running
  ([the clock](https://github.com/bvchess/taxman/blob/3ca11bf/solver/frame/src/solver/clock.rs));
* **the original file:** `seconds.own` where its line has one (4899 on), else `seconds.search_all_runs`, the search's
  elapsed time over its invocations, which also counts the time it waited, suspended, behind older games.

The chain waits for the head and for no other game, so the head's time is what a game holds the chain up for, and the
`own` of the games of a stretch add up to near its wall time.  The run's head time is the finish of a game less the
finish of the game before it.  The run's `active` exceeds it by 0.3% over games 4984 to 5060 and 0.9% over 4880 to 4983,
where the dear games are, and by 1% to 22% below 4880, where a game's setup and its work ahead of the head count as well
([full-run.txt](full-run.txt), "Head time against active time").  So below 4880 the run's hours stand a little high
against the re-run's `own`, and its wins are a little understated.

*The re-run.*  Tag `rerun-2026-10`, commit 3ca11bf: games 1 to 4879 on the same machine, 88 threads, one invocation a
game, `--gate 1200 --gate-trial 1000,800,600`.  It starts at a gate of 1,200, and once a search has taken 50 million
steps a trial keeps the gate of least CPU among 1,000, 800, 600 and 1,200.  The gate study paused it more than once, so
its wall time is no measure and its per-game `own` is.  The run's build is the re-run's with the default gate changed
and the frame solver cleaned up (`git log 3ca11bf..aaba59b`: the old bounds, the switches and the lab removed), so the
run tests the policy as the build ships it.  The gate entry's own runs used the re-run's build and isolate the gate.

*The original file.*  The committed file before the run replaced it (`git show d05191a:results/optimal.jsonl.gz`), made
in six runs on a laptop, a cloud machine and this machine ([runs.md, "The earlier
file"](https://github.com/bvchess/taxman/blob/5bd5d48/results/runs.md#the-earlier-file)).  Only the sixth, games 4875 to
5060, ran on this machine, so only there are hours compared.  The five before it ran without conflict branching, on
other builds, and took 382 games from the bounds store with no search; with them the comparison is of nodes, over the
games each searched itself.  The sixth run's lab set the gate game by game, and its lines record it (the `lab` key and
`engine.gate_trial`).  A game's policy below is that record.

*The stretches.*  Games 1 to 4879 are cut after multiples of 25 where the run's hours turn from fewer than the re-run's
to more and back.  Games 4875 to 5060 are cut where the original file's gate changed, and once, at 5023, where the run's
result against it turns over.

## Results

**1. The chain took 116.6 hours of wall time, 77% of its hours on the last 186 games.**  The first game started at
08:24:54 PST on 2026-11-01 and the last finished at 05:00:56 PST on 2026-11-06: 419,762 s (the log: the solver exited
with status 0 after 419,763 s).  The games' active hours add up to 118.84, 1.019 of the wall time, since a game ahead of
the head may run beside it.  The workers used 10,149 CPU hours, 87.0 of the 88 threads on average.  1,749 games took a
search step, for 62.97 G nodes.

| games | active hours | share | CPU hours | nodes (M) | games searched |
|---|---|---|---|---|---|
| 1–4874 | 26.83 | 22.6% | 2,133 | 17,733 | 1,678 |
| 4875–4983 | 34.86 | 29.3% | 3,023 | 17,627 | 43 |
| 4984–5060 | 57.15 | 48.1% | 4,993 | 27,613 | 28 |
| 1–5060 | 118.84 | 100% | 10,149 | 62,973 | 1,749 |

The five dearest games, 4983, 4984, 4992, 4991 and 4995, took 45.8 hours, 38.5% of the run.

**2. Against the re-run, games 1 to 4879: 0.63 of the hours and 0.48 of the nodes.**  Hours are the run's `active` and
the re-run's `own`:

| games | run h | run nodes (M) | re-run h | re-run nodes (M) | hours | nodes |
|---|---|---|---|---|---|---|
| 1–3075 | 1.04 | 810 | 1.05 | 1,128 | 0.99 | 0.72 |
| 3076–3125 | 0.90 | 269 | 0.64 | 186 | 1.39 | 1.44 |
| 3126–3525 | 2.74 | 2,146 | 4.97 | 4,728 | 0.55 | 0.45 |
| 3526–3625 | 2.87 | 1,890 | 2.32 | 1,652 | 1.24 | 1.14 |
| 3626–4375 | 7.14 | 5,463 | 21.54 | 19,827 | 0.33 | 0.28 |
| 4376–4425 | 2.70 | 1,647 | 2.89 | 2,391 | 0.93 | 0.69 |
| 4426–4475 | 3.62 | 2,054 | 0.97 | 697 | 3.72 | 2.95 |
| 4476–4575 | 1.47 | 788 | 1.50 | 1,240 | 0.97 | 0.63 |
| 4576–4675 | 1.58 | 1,231 | 0.78 | 640 | 2.02 | 1.92 |
| 4676–4775 | 1.57 | 917 | 1.23 | 946 | 1.28 | 0.97 |
| 4776–4879 | 1.67 | 735 | 5.68 | 4,148 | 0.29 | 0.18 |
| 1–4879 | 27.30 | 17,950 | 43.59 | 37,583 | 0.63 | 0.48 |

* **The wins** are 3626–4375 (14.4 hours saved), 4776–4879 (4.0) and 3126–3525 (2.2), at 0.33, 0.29 and 0.55 of the
  hours.  They hold the dear games of the re-run: 4875 and 4879 (0.19 of its hours each), 3940 and 3942 (0.22 and 0.16),
  4192 (0.22) and 3441 (0.49).
* **The losses** are 4426–4475 (2.65 hours more, at 3.72 times), 4576–4675 (0.80 more), 4676–4775 (0.34 more), 3526–3625
  (0.55 more) and 3076–3125 (0.26 more).  The stretches 1–3075, 4376–4425 and 4476–4575 are even.  The hours ratios of
  1–3075 and 4476–4575 (0.99 and 0.97) lie above their nodes ratios (0.72 and 0.63) because `active` counts the setup
  that `own` leaves out.
* **Games, not stretches, decide.**  Of the 469 games of 1–4879 that took 0.01 hours or more in either file, the run
  took longer on 92, 6.26 hours longer in all, and less time on 377, 22.67 hours less in all.

**3. Against the original file, games 4875 to 5060: 0.47 of the hours, and a result that turns over at 5023.**  The
policy column is the original's gate:

| games | original's gate | run h | run nodes (M) | original h | original nodes (M) | hours | nodes |
|---|---|---|---|---|---|---|---|
| 4875–4983 | 300 | 34.86 | 17,627 | 126.41 | 25,613 | 0.28 | 0.69 |
| 4984–4990 | 300, then off | 11.38 | 6,247 | 17.65 | 3,873 | 0.64 | 1.61 |
| 4991–4992 | off, then 1200 | 15.89 | 6,879 | 7.45 | 3,168 | 2.13 | 2.17 |
| 4993–5023 | 1200 | 10.13 | 5,394 | 4.17 | 2,144 | 2.43 | 2.52 |
| 5024–5053 | 1200 | 6.57 | 2,937 | 18.46 | 11,225 | 0.36 | 0.26 |
| 5054–5060 | 1200, then 600 | 13.17 | 6,155 | 23.48 | 16,830 | 0.56 | 0.37 |
| 4984–5060 | | 57.15 | 27,613 | 71.20 | 37,241 | 0.80 | 0.74 |
| 4875–5060 | | 92.01 | 45,239 | 197.61 | 62,855 | 0.47 | 0.72 |

* **The 315 hours are not a wall time.**  The original's `search_all_runs` add up to 315.4 hours over these games, but
  they count the time a search waited behind older games and the invocations that a stop cut short.  The sixth run took
  191 hours of wall time from the start of its second invocation (01:54 UTC on 2026-10-22), the first to leave a line,
  to its last stop (01:01 UTC on 2026-10-30), and the 197.6 hours of `own` (with `search_all_runs` for the 24 games
  4875–4898, which have no `own`) come near it.
* **4875–4983 is no test of the gate.**  Both ran at 300 there.  The run's 0.28 of the hours and 0.69 of the nodes come
  from its tactics and builds: the original lacked carried nogoods and warm starts to 4983.  4901 is the extreme: it
  read 16,296 nogoods carried from 4900 (the run's `chain.err`) and took 11,040 nodes, against 230.5 million in the
  original.  The tactics of the two files agree from 4984 on.  The builds differ, and
  [runs.md](https://github.com/bvchess/taxman/blob/5bd5d48/results/runs.md) describes four of the sixth run's as keeping
  the trees.
* **From 4984 the result turns over between 5022 and 5024.**  On the 14 games that both files searched in 4984–5022 the
  run took 1.32 to 3.43 times the original's nodes (2.02 in all) and 1.28 times its hours (37.40 against 29.27).  On the
  14 of 5024–5060 it took 0.23 to 0.41 of the nodes (0.32 in all) and 0.47 of the hours (19.74 against 41.94).  The
  original's gate was 1,200 on both sides of the cut, and its build was the same on 5016 to 5022 and on 5024 to 5035
  (29aa8ba), so nothing in the policy changes there.  The loss on 4991, 4992, 4995 and 4998 (result 6) belongs to a run
  of games, and so does the win after it.
* **Per node the run was faster than the original at the same gate.**  4983 took 1.81 hours a billion nodes in the run
  and 5.08 in the original, 0.36 of it.  Cheaper steps in later builds and the other load of the machine, which the
  lines do not record, are not separated here.  Across the two files nodes say more about a policy than hours do.

*The five earlier runs, in nodes.*  They ran without conflict branching on other machines, so only the nodes of the
games each searched itself are compared:

| games | searched by the original | its nodes (M) | the run's nodes (M) | ratio | games from the store | the run's nodes (M) on them | the run's hours on them |
|---|---|---|---|---|---|---|---|
| 1–2175 | 731 | 48 | 9 | 0.18 | 0 | | |
| 2176–3440 | 451 | 17,728 | 2,818 | 0.16 | 0 | | |
| 3441–3914 | 179 | 21,284 | 5,745 | 0.27 | 0 | | |
| 3915–4547 | 151 | 29,748 | 5,858 | 0.20 | 167 | 539 | 1.16 |
| 4548–4874 | 35 | 9,185 | 1,599 | 0.17 | 215 | 1,165 | 1.76 |

The run took 0.16 to 0.27 of their nodes, which is conflict branching and the tactics after it more than the gate.  The
382 games that those runs took from the bounds store cost the run 1,704 million nodes and 2.92 hours, 2.5% of its hours.

**4. The dearest games.**  Twelve games took 56% of the run's hours.  Hours are the run's `active`:

| game | run h | CPU h | run nodes (M) | share (cumulative) | the other run: gate, hours, nodes (M) |
|---|---|---|---|---|---|
| 4983 | 12.48 | 1,094 | 6,890 | 10.5% (10.5%) | original, 300: 44.55, 8,770 |
| 4984 | 11.38 | 998 | 6,247 | 9.6% (20.1%) | original, 300 then off: 17.65, 3,873 |
| 4992 | 9.11 | 799 | 4,975 | 7.7% (27.7%) | original, off then 1200: 4.36, 1,955 |
| 4991 | 6.79 | 596 | 1,904 | 5.7% (33.4%) | original, off then 1200: 3.10, 1,213 |
| 4995 | 6.01 | 527 | 3,350 | 5.1% (38.5%) | original, 1200: 1.75, 978 |
| 5056 | 5.53 | 486 | 2,566 | 4.7% (43.2%) | original, 1200 then 600: 8.61, 6,203 |
| 5054 | 5.21 | 451 | 2,375 | 4.4% (47.5%) | original, 1200 then 600: 10.40, 7,448 |
| 5060 | 2.42 | 213 | 1,215 | 2.0% (49.6%) | original, 1200 then 600: 4.47, 3,179 |
| 5052 | 2.19 | 192 | 989 | 1.8% (51.4%) | original, 1200: 5.86, 4,094 |
| 5049 | 2.07 | 181 | 950 | 1.7% (53.2%) | original, 1200: 6.26, 4,051 |
| 4968 | 1.96 | 172 | 1,027 | 1.6% (54.8%) | original, 300: 5.40, 1,388 |
| 4970 | 1.78 | 155 | 911 | 1.5% (56.3%) | original, 300: 5.07, 1,286 |

The first five lie in the patch 4983–4995, where the policy lost on 4991, 4992 and 4995, won on 4983 and 4984 in hours,
and ran at the original's own gate on 4983.  The seven after them are wins at 0.33 to 0.64 of the original's hours (4968
and 4970 at the original's gate too, so they say nothing of the policy).

**5. Where gate 300 lost to the re-run: 12 games, 4.36 hours in all.**  The games that took 0.1 hour or more longer in
the run than in the re-run, with the gate the re-run's search ended with (its trial runs at 50 million steps or later):

| game | run h | run nodes (M) | re-run h | re-run nodes (M) | hours | nodes | the re-run's gate |
|---|---|---|---|---|---|---|---|
| 3102 | 0.37 | 61 | 0.14 | 23 | 2.64 | 2.70 | 1200 throughout |
| 3572 | 0.36 | 256 | 0.19 | 171 | 1.87 | 1.50 | 600 from 51M steps |
| 3576 | 0.38 | 274 | 0.22 | 189 | 1.73 | 1.45 | 1200, kept at 73M |
| 3577 | 0.50 | 378 | 0.24 | 214 | 2.06 | 1.77 | 600 from 103M |
| 4416 | 0.68 | 446 | 0.44 | 400 | 1.54 | 1.12 | 1200, kept at 76M |
| 4420 | 0.49 | 296 | 0.27 | 227 | 1.80 | 1.30 | 1200, kept at 71M |
| 4424 | 0.54 | 318 | 0.22 | 177 | 2.45 | 1.80 | 1200, kept at 68M |
| 4431 | 0.90 | 569 | 0.23 | 168 | 3.91 | 3.38 | 800 from 61M |
| 4432 | 0.85 | 540 | 0.25 | 177 | 3.42 | 3.04 | 1000 from 74M |
| 4433 | 0.72 | 263 | 0.07 | 30 | 10.46 | 8.86 | 1200 throughout |
| 4440 | 0.91 | 577 | 0.17 | 130 | 5.26 | 4.42 | 600 from 64M |
| 4539 | 0.18 | 106 | 0.08 | 67 | 2.30 | 1.59 | 1200 throughout |

* **The tree is bigger, not the node dearer.**  The hours ratio is 0.98 to 1.45 times the nodes ratio: a node at 300
  costs a little more than one at 1,200, in the direction the gate entry found for 150 against 300.
* **The incumbent is not the cause.**  The finder began at the same incumbent and ended at the same best in both files
  in all 12.
* **Chance is part of the small ratios.**  One policy gives different nodes in different runs: 4875 at 300 took 113
  million nodes here and 125 and 173 million in the gate entry's two runs (4879: 104 here and 167 there).  The ratios of
  3102 and of 4431, 4432, 4433 and 4440 (2.7 to 8.9 in nodes) are well beyond that, those of 4416 to 4424, 3572 to 3577
  and 4539 (1.1 to 1.8) are not.
* **The trial's own choice does not explain them.**  The re-run's gate ended at 1,200 in seven of the twelve (three of
  them searches too short for the trial), at 800 or 1,000 in two and at 600 in three.  On 4440 it built the top of the
  tree at 1,200, switched to 600 after 64 million steps, and took 130 million nodes against the run's 577.  The gate
  entry's reading, that a policy which builds the top at 1,200 loses to one that builds it low, does not hold on that
  game.

By the gate that the re-run's trial kept, in the games that took 0.01 hours or more in either file:

| the trial kept | games | run h | re-run h | hours | run nodes (M) | re-run nodes (M) | nodes | games where the run took longer |
|---|---|---|---|---|---|---|---|---|
| 600 | 73 | 7.40 | 18.19 | 0.41 | 5,364 | 16,031 | 0.33 | 4 |
| 800, 1,000 or 1,200 | 33 | 7.22 | 7.84 | 0.92 | 4,997 | 7,088 | 0.71 | 10 |
| no trial (the search ended before 50M steps) | 363 | 11.42 | 16.42 | 0.70 | 7,117 | 13,651 | 0.52 | 78 |

A trial that keeps 600 marks the games where 300 gains most (0.41 of the hours), and one that keeps a higher gate the
games where it gains little (0.92).  This is an association in the re-run's data, made after 50 million steps of a
search, and no run tested a rule built on it.

**6. Where gate 300 lost to the original file: 4991, 4992, 4995 and 4998, within a run of losses from 4984 to 5022.**
The games that took 0.1 hour or more longer in the run than in the original:

| game | run h | run nodes (M) | original h | original nodes (M) | hours | nodes | the original's gate |
|---|---|---|---|---|---|---|---|
| 4991 | 6.79 | 1,904 | 3.10 | 1,213 | 2.19 | 1.57 | off, then 1200 |
| 4992 | 9.11 | 4,975 | 4.36 | 1,955 | 2.09 | 2.54 | off, then 1200 |
| 4995 | 6.01 | 3,350 | 1.75 | 978 | 3.44 | 3.43 | 1200 |
| 4998 | 1.60 | 818 | 0.62 | 353 | 2.57 | 2.32 | 1200 |

* **Three more games lost by little**: 5016, 5020 and 5022 took 1.2 to 1.4 times the hours and 1.3 to 1.7 times the
  nodes (0.1 to 0.15 hour each), within the spread of one policy.  The small games of 5000–5015 lost in nodes by 1.3 to
  2.4 times too, by under 0.1 hour each.
* **The sum**: the run took 14.05 hours longer on these seven games, and 120.0 hours less on the 58 games where it took
  0.1 hour or more less.
* **The original's policy on these games**, as their `lab` keys record it.  4991 and 4992 began under the policy from
  4985, conflict branching off, and the lab then switched each partway to conflict branching on at a gate of 1,200
  (`branching_changes` 1; at 21:54 UTC on 2026-10-27 for 4991 and 02:45 on 2026-10-28 for 4992,
  [runs.md](https://github.com/bvchess/taxman/blob/5bd5d48/results/runs.md)).  4995 and 4998 ran at a gate of 1,200 from
  the root under the policy from 4995, with no switch (`branching_changes` 0).  None of the four used a gate trial.
* **The tactics are the same** in the two files for these games, and the finder began at the same incumbent and ended at
  the same best in all but 4992.  There the original began at the best, 554,676, that an earlier invocation had found,
  and the run's finder reached it 816 s into its 900 s, so the run searched at first with 554,488.
* **The hours ratio is 0.8 to 1.4 times the nodes ratio**, so these losses too are in the size of the trees.
* **The units agreed.**  On the units of 4984, 4992 and 4995 a gate of 600 took 1.10 to 1.55 times the CPU of 1,200, and
  on those of 5052 and 5054 0.68 and 0.83 ([the register](../../register/tactics-and-shortcuts.md), the row of
  2026-10-28).  On whole games the run's gate of 300 did the same: worse on 4992 and 4995, better on 5052 and 5054, and
  worse on 4984 in nodes.

**7. What the gate entry left open: 4983 and 4984 both finished at 300.**

| game | the run: hours, nodes (M), CPU hours | the original: gate, build, hours, nodes (M) | hours | nodes |
|---|---|---|---|---|
| 4983 | 12.48, 6,890, 1,094 | 300, c3357cd: 44.55, 8,770 | 0.28 | 0.79 |
| 4984 | 11.38, 6,247, 998 | 300 then off, 88b1228, four invocations: 17.65, 3,873 | 0.64 | 1.61 |

* **4983** ran at the original's gate, so this compares builds: 0.79 of the nodes, and 0.36 of the original's hours a
  node.  It shows no blow-up of the gate on the dearest game of the chain: 12.5 hours.
* **4984** took 6,247 million nodes at 300, 1.61 times the original's 3,873 million, and fewer hours (0.64) for the same
  per-node reason (0.40 of the original's hours a node).  The original's line is a mixture.  Its `tactics` say
  `conflict_branching=off`, the flag of its last invocation, but its policy from 4948 left conflict branching to the
  default (at 300) and its `lab` key records one switch to off (`branching_changes` 1, at 14:19 UTC on 2026-10-27 by
  [runs.md](https://github.com/bvchess/taxman/blob/5bd5d48/results/runs.md)), over four invocations.  So its nodes do
  not say what either setting took, and the line does not say how many nodes came before the switch.  The gate entry's
  capped run at 300 reached 1,851 million nodes in 3 hours; the run took 549 million nodes an hour over its 11.4.
* **Not measured:** 4983 or 4984 whole at a gate of 1,200 with the trial, or with conflict branching off, on the run's
  build.  The comparison that the gate entry wanted for them does not exist; the original's lines are the nearest.

## Decision

The default stays: a fixed gate of 300 with no gate trial.  It took 0.63 of the re-run's hours on games 1 to 4879, and
on 4984 to 5060, where the two files agree on everything but the gate and the build, 0.80 of the original's: it lost 8.1
hours on 4984–5022 and won 22.2 on 5024–5060.  A policy that took the faster of the two files in every game would have
saved at most 6.6 hours of 27.3 on 1–4879 and 14.4 of 92.0 on 4875–5060, and that bound counts chance, since one policy
varies between runs.

## What is still open

1.  **Why gate 300 lost on 4991, 4992, 4995 and 4998**, and on every searched game of 4984–5022, and why it won on every
   one of 5024–5060; and why it lost on 4431–4433, 4440 and 3102.  The trees are bigger, the incumbent is the same (but
   on 4992), the tactics are the same and the trial's own choice does not predict it.  Games 4431 to 4440 take under an
   hour at 300 and 4991, 4992 and 4995 take 6 to 9 hours, so a race of 300, 600 and 1,200 on these games, each on the
   run's build, would settle whether the loss is the gate.  The same race would give the missing whole-game comparison
   for 4984.
2.  **A gate set as a fraction of the root's gap** was never tested on whole games.  The root's gap does not predict a
   game's size in the chain's games (r = -0.71, [the root
   gap](../the-root-gap-and-the-size-of-a-game-2026-10/README.md)), so whether a fraction of it picks the games that
   want a high gate is not known.  That the result turns over between two neighboring games, 5022 and 5024, shows that
   consecutive games differ in what they want, and a rule from a game's own data could follow them.

## Files

The run's lines and log are in `~/taxman_work/chain2-data/` (`results/strict.jsonl`, `logs/chain.log`), the re-run's in
`~/taxman_work/chain-rerun-2026-10-data/results/strict.jsonl`; neither is copied here (38 MB and 37 MB).  The run's
lines are also `results/optimal.jsonl.gz` of the main repository at commit 5bd5d48.  The re-run's file is kept on the
machine only.

* `full_run.py`: reads the three files and prints every number of the entry.  `git show d05191a:results/optimal.jsonl.gz
  > original.jsonl.gz` makes the original file, and then `NOV1_RESULTS=chain2-data/results/strict.jsonl
  RERUN_RESULTS=chain-rerun-2026-10-data/results/strict.jsonl ORIGINAL_RESULTS=original.jsonl.gz
  NOV1_LOG=chain2-data/logs/chain.log python3 full_run.py > full-run.txt` (run in `~/taxman_work`).
* `full-run.txt`: its output.  Its sections are "The run", "Where the hours went", "Head time against active time", the
  run against the re-run, against the five earlier runs and against the original file, "The 12 dearest games", the games
  where the run took longer than the re-run and than the original file, "The run against the re-run by the gate the
  re-run's trial kept", "The games the gate study left open" and "Scores", which checks that the run's scores equal the
  original file's in all 5,060 games and the re-run's in all 4,879.

## Commits

On master of [bvchess/taxman](https://github.com/bvchess/taxman):

* aaba59b: the run's build (a game's line says what it cost and how long it took); the default gate of 300 is commit
  200c122.
* 3ca11bf: the re-run's build, tag `rerun-2026-10`.
* 5bd5d48: `results/optimal.jsonl.gz` becomes the file of this run, and `results/runs.md` records it.
* d05191a: the last commit that has the original file.
