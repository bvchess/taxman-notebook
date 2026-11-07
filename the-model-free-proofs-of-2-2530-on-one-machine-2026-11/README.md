# The model-free proofs of 2-2530 on one machine (2026-11)

Part of the [lab notebook](../README.md).

Started 2026-11-06.  Concluded 2026-11-07.

**Question.**  Can one build of the prover prove opt(n) = V(n), the recorded score, for every game from 2 to 2530 in one
run on one machine of 88 threads, where its proofs had reached 2175 from several runs and files?  **Answer.**  Yes.
`prover.sh 2 2530` from commit 9015f79 proved all 2,529 games in 19.3 hours: 795 searches took 1,957.8 million nodes and
1,698.5 thread-hours, and `prover.sh --verify 2 2530` prints `OK`.  The cost is in the games past 2175, which took 99.6%
of the hours; it follows the root's parity gap, and by that gap the next 100 games (2531-2630) would cost 55 to 90
thread-hours, about an hour on this machine.

## Method

**The command and the build.**  `solver/tools/cloud/prover.sh 2 2530`, as the runbook's section "On a machine of your
own" has it ([`solver/docs/runbook/prover.md`](https://github.com/bvchess/taxman/blob/574048d/solver/docs/runbook/prover.md#on-a-machine-of-your-own)):
`exact` in passes of 3600 s over the range, the dearest games first by the solver's nodes (`summarize.py order`), every
search from the roles of the bottom-layers theorem (F4), until every game has a line, then the check.  The build is
commit 9015f79 (2026-11-03), built for the machine's CPU (`RUSTFLAGS="-C target-cpu=native"`, which the log names
Broadwell) with rustc 1.99.1, in a clone that stayed as it was; `grep '^commit:' prover.log` shows that one commit, so
one build made every line.  The prover's sources have changed since, in comments, messages and tests (`git log
9015f79..cd3c3ac -- solver/noframe` lists the commits), so the run is reproduced at 9015f79.

**The machine and the dates.**  batmobile: two Intel Xeon E5-2699 v4 processors at 2.2 GHz, 22 cores each with two
threads, 88 CPUs and 756 GiB, Linux 5.15.  The run used 88 threads at idle priority.  It started by itself on
2026-11-06 at 05:02:41 PST, when the chain of the run of 2026-11-01 ended, and ended on 2026-11-07 at 00:21:24 PST with
`ended: complete`: 19.3 hours, 20 passes (19 of 3600 s and a last of 1,097 s), every one of them exiting with status 0.
It cost no money; its cost is its hours.

**What ran beside it.**  The machine was not otherwise idle.  From 2026-11-06 about 09:00 PST, experiments of the frame
solver's unsound mode ran beside the run on up to 8 threads at nice 19.  A `thread_secs` is the wall-clock time a thread
spent on a game, so any time a thread waited for a CPU counts, and the seconds below run a little long.  The nodes of a
search on one thread do not depend on that; those of a search on several threads vary a little with the timing, since
each thread keeps nogoods of its own.

**The cost model for the next 100 games.**  `exact --from 2531 --to 2630 --budget 1` (21 s on 4 threads, no search)
gives each game's relation and root parity bound; `next100.py` prices the games that need a search by the fit of log10
nodes on the root's parity gap, and tries the fit on the run's own games of 2176-2530.

## Results

**The check**, `TAXMAN_WORK=... solver/tools/cloud/prover.sh --verify 2 2530`, run on the run's machine at 00:24 and
again on the committed copy of the file (`solver/noframe/data/exact_parity_2_2530.jsonl`, 2,529 lines, 701,978 bytes):

```
games 2..2530: 2529 of 2529 have a line; searches: {'skipped': 1734, 'proven': 795}; proven by {'Franklín–Moniot bound': 45, 'parity bound': 199, 'search': 795, 'prime': 319, 'chain': 712, 'semiprime': 459}
without a line: none; score not the recorded optimum: none; not proven in 2..2530: none
searches that proved: 795, of them 795 from the roles of F4 (fix_low)
OK: opt(n) is proven equal to the recorded score for every n in 2..2530
```

It exits with status 0.  Every game has a line with the recorded score, no search found a set that beats it, and all 795
searches rest on F4 as well as on the bounds.  The 1,734 games with no search took 616 seconds in all, 1.7 at most.

| proven by | games |
|---|---|
| Franklín–Moniot bound already equals V(n) | 45 |
| parity bound at the root already equals V(n) | 199 |
| a search | 795 |
| `chain`: at its ceiling, V(n) = n + V(n − 1), predecessor proven | 712 |
| `prime`: by the prime formula, predecessor proven | 319 |
| `semiprime`: by the semiprime formula, predecessor proven | 459 |
| **every n in 2..2530** | **2,529** |

**The run.**  After the first pass 2,466 of the 2,529 games had lines and 63 searches were paused, then 2,496 and 33
after the third, 2,511 and 18 after the ninth, 2,519 and 10 after the fourteenth, 2,526 and 3 after the seventeenth, and
the last two games after the eighteenth.  The last search, 2346's, was alone on the machine for the last 1,097 s, on 88
threads.  The 795 searches took 1,957,790,341 nodes and **1,698.5 thread-hours**, 3.12 ms a node on average; the 88
threads were on a game for 99.9% of the 1,699 thread-hours of the run.  By stretch:

| games | proven by a search | nodes | thread-hours | ms a node |
|---|---|---|---|---|
| 2-1300 | 346 of 1,299 | 261,229 | 0.09 | 1.31 |
| 1301-2175 | 314 of 875 | 13,201,257 | 6.25 | 1.71 |
| 2176-2530 | 135 of 355 | 1,944,327,855 | 1,692.1 | 3.13 |

**The cost by band of 100 in n** (`summarize.py cost --band 100`, with the thread-hours added by `run_stats.py`; the
dearest game of each band in brackets):

| n | searches | the root's parity gap (mean) | median nodes | most nodes | nodes | thread-hours | ms a node |
|---|---|---|---|---|---|---|---|
| 2–99 | 3 | 7 | 1 | 10 (81) | 12 | < 0.01 | 0.42 |
| 100–199 | 4 | 9 | 1 | 4 (120) | 7 | < 0.01 | 1.86 |
| 200–299 | 12 | 8 | 1 | 8 (228) | 34 | < 0.01 | 3.24 |
| 300–399 | 27 | 18 | 4 | 15 (399) | 152 | < 0.01 | 3.95 |
| 400–499 | 33 | 20 | 7 | 54 (480) | 378 | < 0.01 | 3.54 |
| 500–599 | 30 | 46 | 25 | 295 (595) | 1,647 | < 0.01 | 1.47 |
| 600–699 | 30 | 73 | 34 | 541 (616) | 4,374 | < 0.01 | 1.05 |
| 700–799 | 31 | 75 | 65 | 598 (798) | 3,442 | < 0.01 | 1.67 |
| 800–899 | 38 | 85 | 94 | 1,286 (800) | 9,854 | < 0.01 | 1.27 |
| 900–999 | 32 | 166 | 390 | 9,780 (990) | 44,265 | 0.02 | 1.22 |
| 1000–1099 | 37 | 123 | 438 | 12,829 (1023) | 65,312 | 0.02 | 1.26 |
| 1100–1199 | 33 | 111 | 127 | 3,729 (1197) | 12,320 | 0.01 | 1.62 |
| 1200–1299 | 35 | 173 | 3,162 | 14,066 (1287) | 116,983 | 0.04 | 1.32 |
| 1300–1399 | 36 | 277 | 6,744 | 217,589 (1380) | 1,486,863 | 0.67 | 1.63 |
| 1400–1499 | 43 | 450 | 66,885 | 847,263 (1475) | 4,866,369 | 2.53 | 1.87 |
| 1500–1599 | 39 | 458 | 24,510 | 365,270 (1520) | 1,975,263 | 1.00 | 1.82 |
| 1600–1699 | 34 | 345 | 9,958 | 74,165 (1696) | 513,421 | 0.17 | 1.19 |
| 1700–1799 | 33 | 306 | 7,037 | 26,521 (1720) | 342,081 | 0.11 | 1.11 |
| 1800–1899 | 33 | 423 | 41,534 | 177,450 (1859) | 1,757,520 | 0.54 | 1.11 |
| 1900–1999 | 28 | 301 | 5,490 | 94,997 (1995) | 457,430 | 0.22 | 1.73 |
| 2000–2099 | 41 | 380 | 10,141 | 99,062 (2000) | 640,090 | 0.31 | 1.77 |
| 2100–2199 | 39 | 570 | 26,271 | 1,218,046 (2184) | 3,869,567 | 2.62 | 2.44 |
| 2200–2299 | 37 | 727 | 184,120 | 13,021,992 (2288) | 35,043,723 | 43.1 | 4.43 |
| 2300–2399 | 39 | 976 | 10,824,087 | 297,725,337 (2346) | 1,523,252,740 | 1,410.3 | 3.33 |
| 2400–2499 | 37 | 742 | 482,280 | 117,479,896 (2499) | 241,256,583 | 147.8 | 2.21 |
| 2500–2530 | 11 | 901 | 6,362,874 | 60,920,815 (2500) | 142,069,911 | 89.0 | 2.25 |

**The dear games.**  The games past 2175 took 99.6% of the thread-hours and 2300-2399 alone 83.0%.  The dearest 1, 5, 10
and 50 games took 17.4%, 43.8%, 65.0% and 97.6%.  71 searches took a million nodes or more, 27 ten million or more and 5
a hundred million or more; 63 took a thread-hour or more, 23 ten or more and 4 a hundred or more.  The 12 dearest:

| n | root gap | nodes | thread-hours | wall hours | threads | ms a node |
|---|---|---|---|---|---|---|
| 2346 | 1,346 | 297,725,337 | 295.2 | 19.3 | 88 | 3.57 |
| 2376 | 1,213 | 130,120,212 | 129.1 | 18.8 | 87 | 3.57 |
| 2379 | 1,213 | 129,956,386 | 126.5 | 16.3 | 72 | 3.50 |
| 2340 | 1,333 | 126,452,613 | 113.0 | 16.2 | 80 | 3.22 |
| 2375 | 1,171 | 70,119,590 | 80.1 | 16.4 | 76 | 4.11 |
| 2385 | 1,173 | 83,468,862 | 76.8 | 17.7 | 86 | 3.31 |
| 2343 | 1,248 | 91,670,920 | 73.7 | 12.7 | 73 | 2.89 |
| 2499 | 1,047 | 117,479,896 | 72.5 | 16.7 | 25 | 2.22 |
| 2344 | 1,248 | 91,646,061 | 72.4 | 16.3 | 16 | 2.84 |
| 2384 | 1,165 | 73,858,875 | 64.5 | 16.1 | 10 | 3.14 |
| 2380 | 1,137 | 60,011,228 | 55.9 | 15.2 | 79 | 3.36 |
| 2366 | 941 | 48,013,598 | 46.5 | 13.5 | 74 | 3.49 |

2346 ran on up to 88 threads over the whole run (1,062,725 thread-seconds, 69,509 s of wall time).  The root gaps of the
795 searches run from 1 to 1,346 (mean 329); those of the 135 searches of 2176-2530 from 547 to 1,346 (mean 815).  The
Franklín–Moniot bound's gap at 2530 is 5,233 against the parity gap of 893.

**What the cost follows**, as `summarize.py cost --band 100` prints its fits:

```
from n = 78: log10 nodes grows 0.244 ± 0.005 per 100 in n (R² 0.76)
from n = 78: log10 secs grows 0.230 ± 0.004 per 100 in n (R² 0.77)
from n = 78: log10 nodes grows 0.607 ± 0.008 per 100 of the root's parity gap (R² 0.87)
from n = 600: log10 nodes grows 0.231 ± 0.007 per 100 in n (R² 0.65)
from n = 600: log10 secs grows 0.228 ± 0.006 per 100 in n (R² 0.67)
from n = 600: log10 nodes grows 0.543 ± 0.008 per 100 of the root's parity gap (R² 0.88)
from n = 900: log10 nodes grows 0.217 ± 0.009 per 100 in n (R² 0.52)
from n = 900: log10 secs grows 0.225 ± 0.008 per 100 in n (R² 0.56)
from n = 900: log10 nodes grows 0.498 ± 0.008 per 100 of the root's parity gap (R² 0.88)
```

From 900 on, a search's nodes grow tenfold per 201 points of the root's parity gap, and its seconds 1.7 times per 100 in
n.  The gap explains the cost better than n does (R² 0.88 against 0.52), as in the cloud run of 2026-10 (tenfold per 210
points over 490 searches), and the gap itself rises with n past 2100: its mean is between 277 and 458 in every band from
1300 to 2099, then 570, 727 and 976 at 2100-2399, and 742 and 901 at 2400-2530.

**The time of a node.**  1.1 to 1.9 ms from 900 through 2099 (1.2 to 1.6 on the bands before), then 2.44, 4.43, 3.33,
2.21 and 2.25 ms from 2100.  Split by the threads a game ran on (thread-seconds over nodes, so the machine's other load
is in it):

| games | threads | games | nodes | thread-hours | ms a node |
|---|---|---|---|---|---|
| 900-1999 | 1 | 383 | 11.6 million | 5.3 | 1.65 |
| 2000-2199 | 1 | 80 | 4.5 million | 2.9 | 2.34 |
| 2200-2530 | 1 | 66 | 29.8 million | 20.7 | 2.49 |
| 2200-2530 | 2 to 8 | 41 | 496.2 million | 369.0 | 2.68 |
| 2200-2530 | 9 to 87 | 16 | 1,117.8 million | 1,005.4 | 3.24 |
| 2200-2530 | 88 | 1 | 297.7 million | 295.2 | 3.57 |

A node costs more on more threads, but these are different games: the dearest are the ones that took the threads.  All
58 searches that ran on more than one thread are in 2200-2530, and took 98.8% of that stretch's hours.

**Against the cloud run of 2026-10.**  The cloud run ([its entry](../the-model-free-proofs-of-1301-2175-cost-and-the-cloud-run-2026-10/README.md))
proved 1301-2175 from the plain root with the build of commit 4db7a14: 490 searches, 309.2 million nodes, 226.0
thread-hours.  This run searched 314 of those games, in 13.2 million nodes and 6.25 thread-hours.  The semiprime
formula settles the other 176, which took the cloud run 115.1 million nodes and 84.0 thread-hours.  On the 314 games
that both searched, the cloud run's build took 194.1 million nodes against 13.2 million, 14.7 times as many, and the
geometric mean of the ratio of the two builds' nodes is 13.7.  Over 2-1300, the retired file of the proofs from scratch
(557 searches, 2.76 million nodes, 1.17 thread-hours) is 346 searches, 0.26 million nodes and 0.09 thread-hours here,
the other 211 being `semiprime` games.  The build of this run has what the prover learned after the cloud run (the roles
of F4, the bars outside the heaviest set, the choice of the conflict by expected tree, the semiprime formula and cheaper
nodes), which the cloud run's build lacked.

**The next 100 games, 2531-2630.**  100 games, of which 39 need a search (27 `chain`, 12 `prime`, 22 `semiprime`), with
root gaps of 341 to 942 (mean 643, against 742 at 2400-2499).  `next100.py` gives:

| model | tried on the run's own games of 2176-2530 | the next 100 |
|---|---|---|
| log10 nodes on the gap, fitted on the gaps below 1000 (564 searches from 900 on; slope 0.506 per 100, residual sd 0.50 decades, mean 1.94 over the median) | the 112 searches of gap below 1000: 286 million nodes; the model, 395 million | 88 million nodes, 54 to 88 thread-hours (2.2 to 3.6 ms a node), 0.6 to 1.0 hours on 88 threads |
| the same on every gap (587 searches; slope 0.499) | the 135 searches: 1,944 million nodes; the model, 5,502 million | 80 million nodes, 49 to 80 thread-hours |
| the mean of the run's searches in the same 100 points of gap, with no model | | 76 million nodes, 59 thread-hours |
| log10 nodes on n (slope 0.217 per 100, residual sd 0.98 decades) | | 616 million nodes, 377 to 616 thread-hours |

The model on every gap overprices the games of the largest gaps (2.8 times the run's nodes on the 135 late searches,
most of them in the 2300s, whose gaps are 1,100 to 1,350).  The games of 2531-2630 have gaps below 942, where the data
are many, and there the model overprices the run's games by 1.4 times.  So the next 100 would cost about 60 to 90
thread-hours, about an hour on this machine without the other work, within a factor of two either way.  The fit on n,
whose residual is twice as wide, prices it higher.  By the model's median, the dearest of them would be 2550 (gap 942)
at 7 million nodes, and 2536 and 2535 (gap 924) at 6 million each; the run's own games of gap 950 (2504) and 887
(2490) took 29.9 and 18.6 million nodes, 20.6 and 9.8 thread-hours, so one of the 39 may take ten to twenty
thread-hours.

## What it means

* **The prover's proofs reach 2530**, by one build in one run on one machine, with no BASELINE and no joined files:
  opt(n) is proven equal to the recorded score for every n in 2..2530 on the whole board, and statement U holds at every
  such n.  The committed file replaces the three files of the runs before it.
* **The cost is in the games with the largest root gaps.**  A game of gap 1,346 took 295 thread-hours, and the gaps of
  the games past 2530 are measured in seconds (`exact --budget 1`), so the cost of a range is priced before it runs.
* **The proofs past 2530 are cheap in the near range**: by the gap model 2531-2630 would cost about 60 to 90
  thread-hours.  Whether to run them is for the project owner to decide; the project's priority is the unsound mode.

## Files

* `solver/noframe/data/exact_parity_2_2530.jsonl` of the main repository: the run's output, 2,529 lines, made by
  `solver/tools/cloud/prover.sh 2 2530` with commit 9015f79.  It replaces `exact_parity_2_1300.jsonl`,
  `exact_parity_1301_2175.jsonl` and `exact_parity_990_1300.jsonl`, which stay in the main repository's history.  The
  logs and the checkpoints are not kept.
* `run_stats.py`: the totals, the band table, the dearest games and the time of a node by threads, from the file; with
  the two retired files of the cloud run (`git show` of them at commit cd3c3ac) it prints the comparison above:
  `python3 -I run_stats.py FILE OLD_2_1300 OLD_1301_2175`.
* `next100.py` and `pre_2531_2630.jsonl`: the cost model for 2531-2630, and the classification of those 100 games made
  by `exact --from 2531 --to 2630 --budget 1 --threads 4 --out pre_2531_2630.jsonl` with the build of commit cd3c3ac:
  `python3 -I next100.py FILE pre_2531_2630.jsonl`.

## Commits

* 9015f79 (2026-11-03): the build of the run.
* 574048d (2026-11-07): records the run in the main repository: the file, the retired files, the readers, and 2530
  where the docs and the site named 2175.  It also makes `summarize.py check` read the games below A only from the
  files before the last, so that the baseline of a range from A > 2, now the whole of 2..2530, cannot stand in for a
  line the output lacks, and it moves the W = 20 test of the prover's proof from game 1133, which the formula now
  settles with no search, to game 1032.
