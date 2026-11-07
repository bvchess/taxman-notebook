# The unsound mode on all threads (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  Why does the unsound mode (`taxman solve --unsound`) stop getting faster past about 32 threads, and does
a remedy that keeps every line make a run on many threads faster?

**Answer.**  A round lasted as long as its longest neighborhood: on 64 and 88 threads the rounds' wall time was the
longest neighborhoods summed, to within 1%, while the work spread over the threads was a quarter to a half of it.  The
remedy runs the rounds ahead of their ends, from a guess of where the next rounds start, has the allocator keep the
memory each neighborhood frees, and makes each game's setup while the game before plays.  Every line is the same as
before on every number of threads.  On 64 and 88 threads, games 4752, 4864 and 5016 alone take 1.39 to 1.73 times less
time than before, and the chain 4861-4960 on 88 threads 1.45 (effort 2) and 1.57 (effort 5) times less; on 4 threads
the games are 0 to 9% faster.  This is the evidence that the remedy is an improvement, on one machine shared with other
studies of 20 to 32 threads; the full measurement, on a quiet machine, is left for a later study.

## Method

*The mode.*  A searched game of the unsound mode
([unsound.md](https://github.com/bvchess/taxman/blob/50db88e/solver/docs/unsound.md)) makes the start of a proven
search, then plays rounds of 64 neighborhoods of large neighborhood search; a neighborhood frees a share of a
trajectory's incumbent and searches the rest as one unit of the engine on one thread.  Every neighborhood of a round
starts from the incumbents as the round starts, and on master a round ended, as a barrier, when its last neighborhood
did.

*The builds.*  Release without fat LTO (`--config profile.release.lto=false --config profile.release.codegen-units=16`),
at -j 4: master [50db88e](https://github.com/bvchess/taxman/commit/50db88e) *before*, and
[954d664](https://github.com/bvchess/taxman/commit/954d664) *after*.  The diagnosis ran master with lines on stderr
added, never committed ([instrument.patch](instrument.patch)): each neighborhood's start, end and steps, each round's
wall time, the process's CPU and page faults around each round, and the parts of each game.  The trials of the remedy
ran an early form of it with counters ([instrument-ahead.patch](instrument-ahead.patch)).

*The machine and the runs.*  Two sockets of 22 cores, 88 hyperthreads (Xeon E5-2699 v4).  Other studies ran beside
every run, at nice 19: 20 to 32 threads from 05:30 to 10:30 PST.  [run_b9.py](run_b9.py) ran each batch one command at
a time at nice 19 and wrote `runs.log`: the time, `uptime` and the count of processes named `taxman` before each run
(the other studies' binaries have other names, so it counts mine), and the seconds and CPU after it.  Every run of 88
threads ran with no other run of mine beside it, at a 1-minute load average of 34 to 124 before it.  The games alone
are 4752, 4864 and 5016, `--from-known --back 8 --tilt 25 --widen 4 --seed 1`, each run before next to its run after.
The chains are 4861-4960 with `--back 8 --tilt 25 --widen 4 --seed 1`, from the run's own lines.

## Where the time went

Games 4752 and 5016 alone at effort 5 on the instrumented master ([part1.py](part1.py)).  *Work over threads* is the
neighborhoods' times summed and spread evenly over the threads, and *busy* is that over the rounds' wall time:

| game | threads | game (s) | start (s) | rounds (s) | longest neighborhoods summed (s) | work over threads (s) | threads busy | time a step, against 4 threads | system CPU |
|---|---|---|---|---|---|---|---|---|---|
| 4752 | 4 | 80.6 | 4.29 | 75.9 | 13.9 | 72.1 | 95% | x1.00 | 2.7% |
| 4752 | 16 | 27.2 | 1.52 | 25.3 | 14.2 | 18.6 | 74% | x1.03 | 3.0% |
| 4752 | 32 | 21.8 | 0.92 | 20.6 | 17.7 | 11.6 | 56% | x1.28 | 3.2% |
| 4752 | 64 | 21.0 | 0.73 | 19.8 | 19.6 | 6.9 | 35% | x1.53 | 4.9% |
| 4752 | 88 | 19.8 | 0.63 | 18.8 | 18.7 | 4.9 | 26% | x1.49 | 4.8% |
| 5016 | 4 | 106.5 | 4.19 | 102.0 | 15.8 | 98.0 | 96% | x1.00 | 1.9% |
| 5016 | 16 | 44.8 | 1.81 | 42.6 | 22.2 | 34.0 | 80% | x1.39 | 2.0% |
| 5016 | 32 | 30.5 | 1.20 | 29.0 | 22.9 | 18.6 | 64% | x1.52 | 2.2% |
| 5016 | 64 | 33.0 | 1.05 | 31.6 | 31.5 | 16.2 | 51% | x2.64 | 3.3% |
| 5016 | 88 | 31.9 | 0.90 | 30.6 | 30.5 | 11.5 | 38% | x2.59 | 3.5% |

* **The barrier.**  From 32 threads the longest neighborhoods summed are most of the rounds' time, and on 64 and 88
  threads all of it.  The longest neighborhood of a round takes a median 3.2 (4752) and 2.7 (5016) times its round's
  mean, and up to 12.8 and 11.5 times: the tilted and widened ones, which reach the step limit.  On 88 threads 24
  threads have no neighborhood at all, since a round has 64.
* **A step costs more on many threads**, the same neighborhood (the same round and k) 1.03 to 1.52 times as long on 16
  and 32 threads as on 4 and 1.5 to 2.6 times on 64 and 88: 88 hyperthreads share 44 cores, and the other studies held
  20 to 32 threads.  The system's 2 to 5% of the CPU is mostly page faults, about 2,100 a neighborhood.
* **Between rounds**, 0.14 to 0.21 s in a game of 16 to 22 rounds: nothing.
* **Outside the rounds**, a searched game spends 0.15 to 0.24 s in its setup and 0.10 to 0.19 s in the start's dive,
  both on one thread, and 3.6 to 4.0 s on 4 threads in the start's local search, which runs on all of them (0.38 to
  0.46 s on 88).

The chain 4861-4960 (49 searched games, 38 repeats, 13 primes) on the instrumented master:

| effort | threads | games' seconds | start's local search | dive | rounds | longest neighborhoods summed | work over threads | setups: searched | repeat | prime | the rest on one thread |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 534.1 | 242.8 | 9.7 | 250.3 | 110.5 | 214.1 | 10.8 | 8.2 | 1.7 | 10.3 |
| 1 | 16 | 243.8 | 70.7 | 9.4 | 133.1 | 117.3 | 60.0 | 10.3 | 8.3 | 1.8 | 10.0 |
| 1 | 32 | 224.3 | 47.1 | 9.9 | 136.3 | 131.2 | 37.6 | 10.6 | 8.1 | 1.9 | 10.4 |
| 1 | 64 | 193.9 | 28.7 | 9.3 | 125.4 | 122.6 | 18.7 | 10.2 | 8.3 | 1.8 | 9.9 |
| 1 | 88 | 195.9 | 27.4 | 9.3 | 128.9 | 126.0 | 13.5 | 10.3 | 7.9 | 1.9 | 9.8 |
| 5 | 88 | 930.6 | 26.2 | 8.8 | 867.4 | 855.8 | 263.4 | 9.5 | 7.3 | 1.6 | 9.6 |

*The rest on one thread* is the survivors of the games before and the moves of the searched games, a repeat's moves and
a prime's formula, and the appending of the lines.  The games that search nothing take 0.13 to 0.15 s (a prime) and
0.25 to 0.29 s (a repeat) each on every number of threads.  With the setups and the dives, about 40 s of each chain runs
on one thread whatever the threads: 8% of the chain at effort 1 on 4 threads, 20% on 88.

## The remedy

The lines had to stay as they were, so a round keeps its definition, and neither a round of more neighborhoods nor a
window in place of the barrier, which would change the lines, was tried.

**1. The rounds run ahead of their ends** ([finder.rs, "Ahead of the end of a
round"](https://github.com/bvchess/taxman/blob/954d664/solver/frame/src/search/finder.rs)).  The threads keep a few
rounds in flight.  A round after the first starts from a guess of its trajectories' incumbents and stages: what the
round before gives if its neighborhoods still running find nothing better.  The guess is made again as each
neighborhood ends, and where it changes, that trajectory's neighborhoods in the rounds after are searched again.  A round
is taken only once all its neighborhoods have ended from its own views, so every neighborhood that counts is the one the
barrier searched.  A guess made once, when its round opens, was tried first: on 4752 at effort 5 on 56 threads it
searched 2,110 to 2,121 neighborhoods for the 1,408 that count, against 1,678 to 1,977 when the guess is made again (the
counters went to stderr, which was not kept).  The
rounds in flight, on 60 threads, with the guess made again ([depth/](depth/)):

| rounds in flight | 4752: game (s) | neighborhoods searched | CPU (s) | 5016: game (s) | neighborhoods searched | CPU (s) |
|---|---|---|---|---|---|---|
| 1 (the barrier) | 19.9 | 1,410 | 428 | 23.8 | 1,025 | 616 |
| 2 | 13.5 | 1,569 | 499 | 18.1 | 1,166 | 712 |
| 4 | 13.3 | 1,883 | 566 | 15.9 | 1,240 | 748 |
| 8 | 13.5 | 2,030 | 574 | 14.5 | 1,321 | 747 |

The rule kept is 1 + 4 × threads / 64 rounds in flight (2 on up to 16 threads, 7 on 88), and no round opens once the
work so far of the rounds before it reaches the budget.  The trials on 56 threads ran beside my own diagnosis chains of
16 and 32 threads, so that up to 88 threads of mine ran at once, over the 64 the brief allowed; their counts of
neighborhoods do not depend on the load.

**2. The allocator keeps freed memory** ([finder.rs,
`keep_freed_memory`](https://github.com/bvchess/taxman/blob/954d664/solver/frame/src/search/finder.rs)).  With every
thread busy, the threads of game 5016 on 88 threads were on a CPU 39% of the time they searched, with 30 s of system
CPU: each neighborhood's searcher allocates and frees its memory, which glibc's malloc gave back to the kernel and
faulted in again.  The glibc tunables on the rounds of 5016 at effort 5 on 88 threads, one run each: none, 22.6 to
22.9 s; a thread stack cache of 16 GiB, 21.9 s; an mmap threshold of 32 MiB, 22.6 s; a trim threshold of 16 GiB,
19.1 s, with 9 s of system CPU; the last two together, 16.7 to 19.6 s, 7 to 8 s.  The unsound mode sets those two
thresholds with `mallopt` before it starts a thread (it does nothing elsewhere than glibc), which took game 5016 from
23.3 and 24.1 s to 18.2 and 18.6 s on 88 threads and 4752 from 19.9 to 13.8 s ([keep/](keep/)).  Game 5016 at effort 4
on 16 threads peaked at 425 MB of memory against master's 350 MB.

**3. A run makes the next game's setup while a game plays**, with the start's dive ([unsound.rs, "A
range"](https://github.com/bvchess/taxman/blob/954d664/solver/frame/src/solver/unsound.rs)): neither depends on the
moves for n − 1.  A line's `seconds` then leave the setup out, but for the first game of a run.

## The remedy is an improvement

**The lines are the same.**  Every line of every run after is the line before, but for its seconds, threads and build:
the 53 lines of the games alone before and after on every thread count, and the first form's 36
([analyze_speed.py](analyze_speed.py), which stops on a difference), the chains (200 lines on 88 threads, 100 on 4 for
the first form at each level), and 38 games of an after chain on 4 threads stopped by the change of scope.  So the
quality at equal work is unchanged, and no race was run.

**The games alone**, in seconds, before and after, and the speedup over 4 threads of each build (the rounds' speedups
are within 0.1 of the game's):

| game | effort | before: 4, 64, 88 threads | after: 4, 64, 88 | after over before: 4, 64, 88 | speedup over 4, before: 64, 88 | after: 64, 88 | CPU, after over before: 64, 88 |
|---|---|---|---|---|---|---|---|
| 4752 | 5 | 82.2, 20.5, 21.4 | 76.5, 12.1, 13.9 | 1.07, 1.69, 1.53 | 4.0, 3.8 | 6.3, 5.5 | 1.24, 1.27 |
| 4752 | 7 | 300.3, 62.4, 63.7 | 275.7, 37.5, 37.4 | 1.09, 1.66, 1.70 | 4.8, 4.7 | 7.4, 7.4 | 1.19, 1.21 |
| 4864 | 5 | 111.4, 27.5, 28.2 | 107.7, 15.9, 17.8 | 1.03, 1.73, 1.59 | 4.0, 4.0 | 6.8, 6.1 | 1.24, 1.34 |
| 4864 | 7 | 427.5, 85.7, 86.5 | 398.9, 51.9, 51.3 | 1.07, 1.65, 1.69 | 5.0, 4.9 | 7.7, 7.8 | 1.17, 1.17 |
| 5016 | 5 | 105.7, 24.6, 24.6 | 105.6, 15.4, 17.8 | 1.00, 1.59, 1.39 | 4.3, 4.3 | 6.8, 5.9 | 1.21, 1.33 |
| 5016 | 7 | 439.2, 75.1, 76.7 | -, 50.0, 48.9 | -, 1.50, 1.57 | 5.8, 5.7 | -, - | 1.13, 1.16 |

5016 at effort 7 on 4 threads after was stopped by the change of scope.  The first form of the remedy, without the
allocator's setting (`part3/first-form/`), was run on every thread count: after over before 0.99 to 1.07 on 4 threads,
1.10 to 1.16 on 8, 1.23 to 1.44 on 16, 1.37 to 1.58 on 32, 1.28 to 1.47 on 64 and 1.02 to 1.29 on 88.

**The chains** 4861-4960:

| effort | threads | before (s) | after (s) | after over before | CPU, after over before |
|---|---|---|---|---|---|
| 2 | 4 | 896.9 | 822.7 (first form) | 1.09 | 0.99 |
| 5 | 4 | 4,479.3 | 4,394.7 (first form) | 1.02 | 1.03 |
| 5 | 4, its first 38 games | 1,234.0 | 1,121.4 | 1.10 | |
| 2 | 88 | 287.9 | 199.1 | 1.45 | 1.75 |
| 5 | 88 | 936.2 | 596.3 | 1.57 | 1.31 |

So on 88 threads a chain is 4.5 (effort 2) and 7.5 (effort 5) times faster than master's on 4, against master's 3.1
and 4.8.

**What it costs** is CPU: on 64 and 88 threads the games use 13 to 34% more, and the chain at effort 2 on 88 threads
75% more, for the neighborhoods searched again and those of rounds past the last.  On 4 threads it is within 4%.

## Left for later

The full measurement, on a quiet machine: the speedup on every thread count, chains at more levels, the share of the
time the setups ahead save, the rounds in flight on more machines, and the cost in CPU when other work wants the
threads.  On this machine, beside 20 to 32 threads of other studies, 88 threads were no faster than 64 after the
remedy.

## Files

* [run_b9.py](run_b9.py): runs a batch's commands one at a time at nice 19, logging the load before each and the
  seconds and CPU after it: `python3 -I run_b9.py BATCH DIR`, the batches being the `*.batch` files of each folder.
* [instrument.patch](instrument.patch): the lines on stderr of the diagnosis, on master 50db88e, never committed.
  [instrument-ahead.patch](instrument-ahead.patch): an early form of the remedy with counters, on 50db88e, never
  committed; `B9_DEPTH` sets the rounds in flight.
* [part1.py](part1.py): the tables of the diagnosis, `python3 -I part1.py diag diag-chain`.
* [analyze_speed.py](analyze_speed.py): the tables of the games and chains and the check that the lines are the same,
  `python3 -I analyze_speed.py games part3/games` (with `part3/first-form/games` after it for the first form) and
  `python3 -I analyze_speed.py chains part3/chains4-b part3/chains88`; [same_lines.py](same_lines.py) compares files of
  lines the same way; [test_cpu.py](test_cpu.py) gives the CPU of each test of a binary run alone.
* `diag/`, `diag-chain/`: the diagnosis's runs, `g{n}-t{threads}` and `c{effort}-t{threads}` (`.jsonl` the lines,
  `.log` stdout, `.err.gz` the stderr of the instrumented build), and the tunables on master, `diag/g5016-t64-*`;
  `diag-chain/beside-builds/` holds a first chain of 88 threads that ran beside my builds and was run again.
* `depth/`: the rounds in flight on 60 threads (the counters are the `B9A` line of each `.err.gz`).  `keep/`: the first
  form (`-a`) against the final one (`-k`, built from the tree of 954d664 before it was committed) on 88 threads.
* `part3/games/`, `part3/chains4-b/`, `part3/chains88/`: before (`-b`) and after (`-a`); `part3/first-form/`: the runs
  of the first form, an earlier version of 954d664 without the allocator's setting; the `stopped/` folders hold runs
  stopped part way.
