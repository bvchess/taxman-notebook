# One prover game on many threads (2026-10)

Part of the [lab notebook](../README.md).

Started 2026-10-31.  Concluded 2026-10-31.

**Question.**  The project's owner wants every game up to 2530 proven by the prover (`exact`, in `solver/noframe`).  An
estimate put the games 2176-2530 at 900 to 2,700 thread-hours, and its dearest games, 2340 and 2346 (root gaps about
1,340), at 190 to 590 thread-hours each: one to four weeks on one thread, while 86 of the lab machine's 88 threads
idle.  `exact` ran one game a thread, so a range took at least as long as its dearest game.  Can the idle threads help
the searches still running, losing no work, so that the wall time of a range approaches its total work over the
threads?
**Answer.**  Yes.  A game's search is a set of units, the roles of its open subtrees, and a thread with no game left to
start takes a unit from a game's pool or asks the worker that holds the largest open child for one.  Game 1540 (root
gap 554) took 309, 146 and 73 s on 1, 2 and 4 threads, for 309, 291 and 290 thread-seconds: 4.2 times as fast on four
threads.  On one thread the tree is master's exactly (118,246 nodes at 1540, 12,771 at 1548), and tests show that no
unit is lost.  A stop signal now pauses every search into its checkpoint and loses nothing, so that a run of weeks can
be stopped and resumed.  Only 1 to 4 threads were measured; the run on 88 threads is the next measurement.  Both
changes are kept.

## Method

**Terms.**  A *unit* is the roles (the forced, barred and free numbers) of an open subtree of a game's search, searched
depth first.  A game in progress has a *pool*, the units that no thread runs, and *workers*, the threads that run its
units, each with a prover of its own: its own matching, parity workspace and nogood table.  A worker's *offer* is the
estimated tree of the largest piece it would give away.  A *pass* is the stretch of `--seconds` after which `exact`
pauses every search that is still going and saves its *checkpoint* (the open units and the nogoods), which a later run
resumes; `prover.sh` runs passes.  *Thread-seconds* are the seconds of all a game's threads, added up.

* **Machine and builds.**  Release builds of `exact` (default flags: the roles of [the bottom-layers
  theorem](https://github.com/bvchess/taxman/blob/de56c17/docs/theory/frame-model.md#the-bottom-layers-theorem), the
  parity bound), at nice 19, on the lab machine while the chain held every thread at idle priority, so these threads
  shared physical cores with the chain's.  At most 4 threads at a time, about 42 minutes of measurement in all.  The
  builds: master (0ef05d1); `team1`, the first; `team2`, with the progress note, where a thread that joins a game
  starts from the game's nogoods; `team3`, the final, where joiners start empty.  They are not kept.
* **Noise.**  Master on 1548, one thread, took 20.35 s and 24.39 s in two runs a few minutes apart (12,771 nodes both),
  and the team build 23.92 s and 24.17 s.  So single runs differ by up to 20%.

### The design

[`src/team.rs`](https://github.com/bvchess/taxman/blob/de56c17/solver/noframe/src/team.rs) is the campaign of `exact`.

* **One lock.**  One mutex and one condvar serve the whole campaign (`team::Hub`).  Work moves rarely, so the lock is
  not a cost; the frame solver found the same with its one locked deque.
* **What a thread does** (`Hub::next_job`), the first of these it can: start the next game not yet started (set it up,
  become its first worker and take the pool's last unit); take the first unit of a pool, from the game with the fewest
  workers; or ask the worker with the largest offer for a unit, and wait (timeouts of 20 ms, and a wake-up at every
  gift, registration and exit).
* **Giving.**  A prover keeps a stack of frames, one for each node running its children: the roles its children derive
  from, its decisions, each child's estimated tree and which children are taken (`game::Frame`).  Before each child and
  each unit it polls its team (`game::Team`): halted? asked?  When asked, it makes a *gift* of the largest open child of
  the shallowest frame that has one: it marks the child taken, and the team puts it in the pool, under the lock.  The
  donor keeps the rest of its path warm; only the moved unit starts cold.  A child's estimate is 10^(gap/210), the gap
  being the node's bound less the target, or, with the child's member barred, the parity bound's `without` (the weight
  that [the branching](../smaller-prover-trees-by-probing-and-branching-2026-10/README.md) uses).  Each worker
  publishes the estimate of what it would give, so that an idle thread asks the worker holding the largest piece.
* **Ends.**  A worker that ends a unit takes the last unit of its pool (depth first, as one thread did) or leaves the
  game.  The last worker to leave ends the game: proven if the pool is empty; paused at the deadline, with the pool and
  the game's nogoods saved in its one checkpoint; or stopped by a worker that found a set beating the target or ran out
  of budget (the `halt` flag stops the others at their next poll).  A panicking thread stops the others instead of
  leaving them waiting.  The result line is appended and synced before the checkpoint is deleted (master deleted the
  checkpoint first).
* **No unit is lost.**  At every moment each unit of a game is in one place: the pool, or the run of one worker (the
  child it runs and the open children of its frames), which a pause returns to the pool before the worker leaves.  A
  gift moves a child from a frame to the pool under the lock and marks it taken, so the donor never runs it.  A game
  ends, under the lock, only when no worker runs.
* **Nogoods.**  Every 256 nodes (with the clock check) each worker adds what it learned to the game's table, which is
  deduplicated and limited to the prover's 20,000.  A joining thread may start from it, and the checkpoint holds it.
  `--share S` also imports the others' nogoods every S seconds.
* **The result line** keeps its fields (`nodes` summed, `secs` the wall time, setups included) and adds `thread_secs`
  (the threads' seconds summed, setups included) and `threads` (the most at once), both over every run.  The
  checkpoint carries them; a checkpoint without them ran on one thread.  `summarize.py exact` and `cost` count
  `thread_secs`, falling back to `secs`.
* **The Lagrangian warm-up** (`--parity 0`, or `--lagrangian 1`) keeps a game to one thread, as before.
* **`prover.sh`.**  `PASS_SECONDS` defaults to 3600 (it was 300) and `THREADS` to every CPU.  The runbook sets
  `PASS_SECONDS=300` for spot, and gains a section, [On a machine of your
  own](https://github.com/bvchess/taxman/blob/de56c17/solver/docs/runbook/prover.md#on-a-machine-of-your-own), with a
  calibration on 1301-2175 and the new range 2176-2530.

## Results

### One thread is the old search

1548 took 12,771 nodes on master and on `team1`.  1540 took 118,246 nodes on master (298.4 s) and on the team build
(309.4 s).

### 1540 to its end (root gap 554; the committed plain-root run took 886,419 nodes)

| build | threads | nodes | wall s | thread s | speedup | units moved |
|---|---|---|---|---|---|---|
| master | 1 | 118,246 | 298.4 | 298.4 | | |
| `team2`, one thread | 1 | 118,246 | 309.4 | 309.4 | 1.00 | 0 |
| `team3` (final) | 2 | 138,021 | 145.8 | 290.9 | 2.12 | 28 |
| `team3` (final) | 4 | 146,688 | 73.3 | 290.3 | 4.22 | 84 |
| `team2` (joiners take the table) | 2 | 92,900 | 101.7 | 202.5 | 3.04 | 22 |
| `team2` (joiners take the table) | 4 | 149,864 | 84.2 | 334.7 | 3.67 | 94 |
| `team2`, `--share 10` | 4 | 143,729 | 89.6 | 355.8 | 3.45 | 59 |

The speedup is the one-thread wall time over the row's.  The node counts swing by up to 25% either way with the timing
(92,900 to 149,864 at 2 to 4 threads, against 118,246 on one), since each thread's nogood table, and so its branching
choices, depend on what it searched.
The final build's thread-seconds were at or below one thread's (smaller tables, cheaper nodes).

### 1475 for 300 s (root gap 590; unfinished after 2,400 s on one thread)

| build | threads | nodes | nodes a second | open units at the pause | nogoods saved | units moved |
|---|---|---|---|---|---|---|
| `team2` | 1 | 105,472 | 351 | 90 | 4,493 | 0 |
| `team2` | 4 | 411,633 | 1,372 (3.9 times) | 301 | 14,509 | 11 |
| `team3` (final) | 4 | 473,528 | 1,574 (4.5 times) | 234 | 17,217 | 12 |

The largest resident memory on 4 threads was 51 to 53 MB.

### Resuming 1475 from the 4-thread checkpoint of `team2` (301 units, 14,509 nogoods), 4 threads, 60 s

| who starts from the checkpoint's nogoods | nodes in the minute | nodes a second |
|---|---|---|
| every thread (`team2`) | 39,081 | 637 |
| no thread (the nogood lines stripped from the file) | 94,263 | 1,556 |
| the first thread only (`team3`, final) | 80,056 | 1,321 |

The cold restart of 301 units costs little (1,321 to 1,556 nodes a second against 1,372 to 1,574 steadily), but a big
nogood table halves a thread's node rate, because a node scans the whole table several times (propagation, learning,
the choice of the conflict).  That decided the policy of the final build: the game's first thread of a run takes the
checkpoint's table, so that one thread resumes exactly as before; joiners start empty; `--share S` keeps the other
policy available.  [The entry on the nogood table](../the-prover-nogood-table-by-what-a-node-changes-2026-10/README.md)
removed the cost of a large table, and measured sharing again: neutral in time at 1540 on 4 threads (69.5 s with
`--share 10`, against 70.8 s without), with 4% fewer nodes.

### The tests

[`team::tests`](https://github.com/bvchess/taxman/blob/de56c17/solver/noframe/src/team.rs) (debug profile, CPU seconds
over two runs):

* `several_threads_reach_the_verdict_of_one` (1.3 s): game 600 on 1 and 3 threads, proven at opt(n) and beaten by a
  playable set worth opt(n) one below it; units are given away on 3 threads.
* `pauses_and_resumes_on_other_numbers_of_threads_lose_no_unit` (1.0 to 1.8 s): game 350 lists every set beating opt(n)
  less 10 in runs of 0.05 s on 3, 1, 2, 4, ... threads.  The sets found are one uninterrupted thread's 20, each once,
  after at least 3 pauses and with units given away.  Dropping every other gift on purpose fails it, which the verdict
  test alone would not see.
* `a_set_that_another_thread_finds_is_reported` (0.2 s): the first thread runs units barring the largest prime, where
  no set beats opt(n) less 1 (the bottom-layers theorem), and the second the unit forcing it; the second's set is the
  verdict.

The `game::` tests (11), `tests/exact` (3, which now check `threads` and `thread_secs` on every line), `tests/recorded`
and the docs test pass; `cargo fmt` and clippy are clean.  `prover.sh 1301 1310` with passes of 2 s on 3 threads took 8
passes and ended with its check passing.

### The clean stop (6fde939)

Before this commit a SIGTERM lost the pass in progress, up to `PASS_SECONDS` of each thread.  With it, a SIGINT or
SIGTERM pauses every search as the end of a pass does: each game's open subtrees from all its threads and its nogoods
go to its checkpoint, every finished game keeps its synced line, no game or unit starts, and `exact` exits with 128
plus the signal (130 or 143), which `prover.sh` already read as a stop by a signal.  A second signal ends `exact` at
once with the same status.
A checkpoint is written to a file and renamed, and a torn last line of the output is dropped on open, so both stay valid
after that.

The handler is a binding to the C library's `signal()` that sets one atomic flag
([`src/stop.rs`](https://github.com/bvchess/taxman/blob/de56c17/solver/noframe/src/stop.rs), no new dependency).  The
campaign polls the flag where it polls the deadline (`next_job`, the end of a unit, the warm-up pause) and in
`Team::halted`, which the searches already poll before every child.

A range from 2 stands alone: `prover.sh 2 B` checks the output file only (no `BASELINE`, which it refuses with A = 2),
so every proof of 2..B comes from one build.  The runbook's [On a machine of your
own](https://github.com/bvchess/taxman/blob/de56c17/solver/docs/runbook/prover.md#on-a-machine-of-your-own) gives the
steps for 2..2530 (clone, release build, rehearsal, tmux with the settings inside its command, watching, stopping and
resuming, the check), and the line of `prover.log` that names the commit now flags modified sources of the prover and
the gzip decoder as well.

* **Test.** `a_sigterm_pauses_every_search_into_its_checkpoint_and_a_rerun_finishes_them` in
  [`tests/exact.rs`](https://github.com/bvchess/taxman/blob/de56c17/solver/noframe/tests/exact.rs) (debug profile, about
  1.6 s of CPU with the `exact` processes): games 576, 620 and 624 on 3 threads, SIGTERM when the first line appears.
  It checks status 143; a checkpoint with open units and nodes for each game without a line (and none for those with
  one); and, after a rerun, one line per game, proven, at the recorded score, with the paused searches' nodes carried
  on.
* **Rehearsal** (release build, 3 threads, nice 19, passes of 30 s): `prover.sh 2 1300` in tmux, one SIGTERM 77 s in.
  Three searches paused with 27 to 50 open subtrees, the stop took 0.2 s with status 143, and a rerun resumed them and
  finished at 168 s in all.  The check passed from the output file alone: opt(n) is proven equal to the recorded score
  for every n in 2..1300.
* **`stoptry.sh`** repeats the test by hand on a list of games.

A kill with SIGKILL, a crash or a lost machine still sends the searches of the pass in progress back to their last
checkpoints, at most `PASS_SECONDS` of each thread.

### Weighed and not built

* **Pause and redistribute**: on an idle thread the busiest worker pauses, pushes its whole stack as units and
  continues from the deepest.  Simple, but every open sibling on its path starts cold (tens of units, about 0.2 s each
  at 2044) at every split.  Giving one child from the shallowest frame keeps everything else warm.
* **Ship the warm state with a gift** (the parent's matching and parity certificate): the parity workspace's saved state
  depends on the workspace's own numbering of the candidates, so it cannot be restored in another thread's workspace
  without more work.  A gift starts cold.
* **One request a game, answered by whichever worker polls first** (the frame solver's split requests): a random donor
  may hold only a small piece.  The published offers let the asker pick the worker with the largest piece.
* **Sharing nogoods at once, or periodically**: measured above, and not by default.  The frame solver's pilots found
  that sharing every nogood between 128 workers cost nodes (1225: 14.38 million nodes against 10.9 to 11.5 million), and
  its tables were cleared periodically; the prover's table is limited to 20,000 and never forgets, so a thread that
  imports a full table cannot learn its own.
* **A checkpoint without a pause** (each worker reports what a pause would leave, at its next poll): not built; the
  unit flow between the pool and the workers needs care so that a unit taken from the pool after a worker's report is
  not missed.  The stop handler made it unnecessary for stopping.

## Decision

* **Kept: c0d0d3e and 6fde939.**  Units are given one at a time from the shallowest frame, to the thread that asks the
  worker with the largest offer; joiners start with no nogoods; nothing is traded by default (`--share` stays a knob).
* **Passes.**  `PASS_SECONDS` is 3600 by default and 300 on spot.  The end of a pass restarts every open unit cold: on
  88 threads that is about 88 times 60 to 75 units (1475's pause on 4 threads left 234 to 301), a fraction of a second
  each, plus the game setups, estimated at well under 1% of a pass of 3600 s.
* **What would reopen it:** a measurement on 88 threads that shows the idle polling, the lock or the memory costing
  more than that.

### What is left

* **Measure at 88 threads.**  Only 1 to 4 threads were measured.  The calibration run of 1301-2175 is that measurement,
  since its last games run on many threads.  Watch `units moved`, `threads`, `thread_secs` against `secs` times
  `threads`, and the memory (each thread's prover holds the parity workspace and a saved state for each frame on its
  path).
* **The build at each resume.**  A record of the build at each resume, so that the passes and stops of one range are
  known to come from one build.
* **Longer passes.**  A pass costs the cold restart of its open units, and a stop no longer loses the pass, so passes
  longer than 3600 s are possible.
* **SIGHUP.**  `exact` handles SIGINT and SIGTERM; a SIGHUP is not handled.
* **`--budget`** is approximate on several threads: a joining thread gets what is left after the threads that already
  left the game.
* **The first thread of a resumed game** takes the union of all threads' tables, up to 20,000, so that after a pass on
  many threads it cannot learn new nogoods until the limit is lifted or the table changes (the cost of a large table
  went with the entry on the nogood table).  If it shows, give it a share of the table, or its own previous table.
* **Idle polling.**  Idle threads poll every 20 ms; at 88 threads with one game near its end that is about 4,000 short
  lock holds a second, measured as nothing at 4 threads.  A notify when a worker first has something to offer would
  remove the polling.

## Files

`runs/` holds the result line of `exact` for 1540, as the runs wrote it.  Its names say the build and the threads
(`t2-none-4-1540.jsonl`: `team2`, no sharing, 4 threads; `t2-10-4-1540.jsonl`: `team2`, `--share 10`;
`t3-4-1540.jsonl`: `team3`).  The 1475 runs ended at a pause and wrote no line, so their figures are not here.

* `runs/master-1540.jsonl`: master, one thread.
* `runs/t2-none-1-1540.jsonl`, `runs/t2-none-2-1540.jsonl` and `runs/t2-none-4-1540.jsonl`: `team2`, 1, 2 and 4 threads.
  The one-thread line stands for the table's one-thread row; the build notes say `team2` differs from the final build
  only in what a joining thread starts with.
* `runs/t2-10-4-1540.jsonl`: `team2` with `--share 10`, 4 threads.
* `runs/t3-2-1540.jsonl` and `runs/t3-4-1540.jsonl`: the final build, 2 and 4 threads.
* `stoptry.sh LIST THREADS [DELAY [RERUN_THREADS]]`: runs `exact` on the games of LIST (comma separated) with a
  checkpoint folder of its own, sends SIGTERM at the first line of output (plus DELAY seconds), reruns it, and prints
  the CPU time that the `exact` runs used (bash's `times`).  `STOP_DIR` names the folder for its work (default: the
  script's folder) and `EXACT_BIN` the `exact` binary.

## Commits

On master of [bvchess/taxman](https://github.com/bvchess/taxman), both 2026-10-31:

* c0d0d3e: `exact` searches a game on several threads when fewer games are left than threads (`src/team.rs`,
  `game::Frame`, `game::Team`, `prover.sh`, the runbook).
* 6fde939: `exact` stops cleanly on SIGINT and SIGTERM; `prover.sh 2 B` is the documented way to prove a whole range
  (`src/stop.rs`, the runbook).
