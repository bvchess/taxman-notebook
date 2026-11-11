# Proofs past 5060, one game at a time (2026-11)

Part of the [lab notebook](../README.md).

Started 2026-11-10.  Concluded 2026-11-10.

**Question.**  Can the frame solver, in its exact mode, prove a game past 5060 on its own, with no proven game below it,
in about an hour of 16 threads?  If it could, a random sample of such proofs would measure how many of the best-known
scores past 5060 are optimal.

**Answer.**  No.  Up to 5060 a proof from nothing costs what the chain paid: five games, proved again, took 0.93 to 1.17
times the chain's CPU.  A fit to the chain's proofs predicted about an hour of 16 threads for each of the three games
past 5060 with the smallest gaps, and the fit failed.  The searches of 5304 and 5260 ran three times that prediction,
2.65 and 2.79 hours, and did not finish, and 5264 was stopped after 0.56 hours.  Each search reached its game's
best-known score within 14 minutes and found nothing above it, so what is left is the proof.  The random sample is
dropped.

## Method

*The words.*  The chain is the committed results of games 1 to 5060, each proven.  A best-known score is the highest
found for a game that no exact search has proved optimal.  A game's *gap* is its root's parity bound less its best-known
score, or less opt(n) for a game of the chain ([the
glossary](https://github.com/bvchess/taxman/blob/aeffc29/docs/GLOSSARY.md#bounds) defines the bounds).  A proof is
*exhausted* when the search ran to its end.  The *ceiling* is a bound from the score of n − 1 that ends a search when
the incumbent reaches it, and the *near-repeat cut* is a cut that rests on a proven n − 1.

*Why a game past 5060 is proven alone.*  The exact mode takes the moves for n − 1 from one place, the completed line of
n − 1 in its `--out` file.  That file is checked when it is opened: each line is replayed and must rest on lines the
file holds, so a file with the line of n − 1 must hold the chain from game 1.  The check refuses unsound lines, and
`--known-to` is a flag of the unsound mode only, so no best-known line past 5060 can seed an exact run from the command
line.  The library's `solver::solve_game` takes such a seed, a `Prev` whose `proof` is none and whose `assumes` is not
empty, and no command exposes it.  Past 5060 the command line proves a game *standalone*, with no seed, no ceiling and
no near-repeat cut, or not at all.

*The two arms of phase 1.*  Phase 1 proved again games that the chain had proved by an exhausted search, to compare what
a proof from nothing costs with what the chain paid.

* **standalone**: `--out` is a new file, so the game has no moves for n − 1.  It is what a game past 5060 gets.
* **seeded**: `--out` is a copy of the committed lines 1 to n − 1, so that n − 1's moves seed the search and the finder,
  with `--tactic prev_cap=off` (no ceiling) and `--tactic near_repeat=off`.  It is what a game past 5060 would get if
  the exact mode took n − 1's best-known line as a seed.

Both arms used the same settings:

* `--force-search`, so that no prime shortcut and no repeat settles a game, and no carried nogoods;
* 16 threads at `nice -n 19`, with the default gate (300);
* the default finder, which starts after 1,000,000 steps, runs for 900 seconds and has a thread beside the 16;
* a checkpoint directory of its own, and a time limit that stops a search and records an unfinished line with its best
  so far.

Phase 2 used the standalone arm.

*The budget.*  No proof got less than its predicted cost.  A game the chain proved got 3 times the chain's CPU-hours.  A
game past 5060 got 3 times the CPU-hours that a fit predicts at its gap.  The fit is to the chain's 359 exhausted proofs
of games 4001 to 5060, ln(CPU-hours) = −56.84 + 7.78 ln(gap), about the chain's 90th percentile at a given gap.  The
time limit was the budget's wall time on 16 threads, and a job whose budget passed 100 CPU-hours was not started.  The
first five runs, the standalone arm of phase 1, had a fixed limit of an hour.  The four cheap games finished within
1,037 seconds, and standalone 5019 was stopped by a signal at 864 seconds and resumed from its checkpoint with what was
left of its budget.

*The games of phase 1.*  The plan asked for four games of 4900 to 5060 whose chain proof cost 1 to 5 CPU-hours and one
that cost 20 to 50.  No exhausted search of 4900 to 5060 cost under 7.1 CPU-hours (5004 and 5008 cost 7.1 and 7.2, and
the median is 44), so the four cheap games are the last ones below 4900 with no near-repeat cut, 4848, 4864, 4865 and
4872.  The fifth, 5019, is the cheapest game of 4900 to 5060 in the 20 to 50 band.

*The games of phase 2.*  Phase 2 was to run if phase 1's standalone costs came within about 3 times the chain's, and
they did.  Its games are the three past 5060 with the smallest gaps: 5304 (gap 2,093), 5260 (2,106) and 5264 (2,090),
each proved standalone.  The fit predicts 14 to 15 CPU-hours for each, about an hour of 16 threads.  A random sample of
ten games of 5061 to 10000 (seed 2026) was planned first and dropped, because the median gap past 5060 is 5,177, which
the fit's formula puts at about 16,000 CPU-hours.  Game 7100 (gap 3,823, about 1,500 CPU-hours by the fit) was dropped
too.

*The games above a proven game.*  A range run from a proven game N to M, with N's line as the moves for N + 1, applies
the chain's ceiling, prime formula, repeats and near-repeat cut, and each game of the range gets the budget of its own
gap.  It was to settle the games that share a proven game's gap, 5305 to 5309 from 5304 and 5261 to 5264 from 5260.  A
test on games 501 to 505, from a standalone proof of 500, settled each as the chain did: the repeats by `same_search`,
503 by the prime formula and 504 by the ceiling.

*Checkpoints.*  From 5260 on, the checkpoint of a search that its budget stopped is kept, so that a longer run can
resume it.  5304's, the first to stop, was deleted before that change.

All runs used the clean build of master aeffc29 and ran on 2026-11-10, from 05:18 to 16:12 Pacific time.

## Results

### Phase 1: a proof from nothing costs what the chain's did

All 10 runs proved opt(n), each by an exhausted search.  The table gives CPU-hours, the fit's being what it predicts at
the game's gap, and the ratios in the text are these runs' against the chain's.

| n | gap | fit CPU-h | chain CPU-h | standalone CPU-h | seeded CPU-h | standalone CPU / fit | standalone wall h |
|---|---|---|---|---|---|---|---|
| 4848 | 1,940 | 7.8 | 3.69 | 3.42 | 3.58 | 0.44 | 0.22 |
| 4864 | 1,944 | 8.0 | 4.50 | 4.41 | 4.29 | 0.55 | 0.28 |
| 4865 | 1,944 | 8.0 | 3.90 | 4.56 | 4.15 | 0.57 | 0.29 |
| 4872 | 1,898 | 6.6 | 3.57 | 4.12 | 3.89 | 0.62 | 0.26 |
| 5019 | 2,272 | 26.8 | 22.99 | 23.06 | 21.28 | 0.86 | 1.45 |

Standalone, the CPU was 0.93 to 1.17 times the chain's and the steps 1.15 to 1.49 times.  A step cost less CPU here than
in the chain, which ran 88 threads where these ran 16 on a machine with room to spare.  The seed from n − 1's moves,
with no ceiling and no near-repeat cut, saves little: 0.91 to 1.05 of the standalone CPU and 0.95 to 0.99 of its steps.
It helped most in 4865, whose standalone start was 391 below opt(n) after a minute and reached it after 15 minutes.  The
fit was high for every game: the costs were 0.44 to 0.86 of its prediction.

### Phase 2: none of the three smallest gaps was proven

| n | gap | fit CPU-h | budget CPU-h | spent CPU-h | wall h | steps | best-known reached | how it ended |
|---|---|---|---|---|---|---|---|---|
| 5304 | 2,093 | 14.1 | 42.4 | 42.4 | 2.65 | 360.7M | after 3 min | at its budget |
| 5260 | 2,106 | 14.8 | 44.5 | 44.5 | 2.79 | 345.2M | after 10 min | at its budget |
| 5264 | 2,090 | 14.0 | 41.9 | 8.9 | 0.56 | 63.5M | after 14 min | stopped on request |

Each search reached the best-known score early and found nothing above it, so its open work is proof, not the search for
a better game.  The progress lines give no measure of what is left.  The queues held about 900 to 2,200 units, none
spilled, and the workers stayed busy (99.9% efficiency) to the end.  The 5264 run was stopped by a signal at 2,024
seconds, at the request of the coordinator, once 5304 and 5260 had run their budgets without finishing.

### The cost against the gap

Up to 5019 the fit overestimated the cost, which was 0.44 to 0.86 of its prediction.  Past 5060 it underestimates by
more than 3 times, since 5304 and 5260 ran 3 times its prediction and did not finish.  The two sides can be read
directly: 5019, with a gap of 2,272, took 23 CPU-hours, and 5260 and 5304, with smaller gaps of 2,106 and 2,093, took
more than 44 and 42 without finishing.  The fit was made on games up to 5060, and these runs are its first test past
them.  Why the cost leaves it was not studied.

### Not run: a search from a floor

The coordinator asked for an upper bound on 5061 by a search from a floor, an incumbent worth the best-known score plus
1,000 with no set behind it.  By [the floor lemma
(R5)](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/search-rules.md#the-floor-lemma) such a search proves
opt(5061) no higher than the floor if it ends having found nothing.  The build cannot run one.

* No flag of `solve` and no tactic gives a start value.  The ceiling (`prev_cap`) is an upper bound that ends a search
  when the incumbent reaches it, not a floor.
* The search always starts from a set.  `search::start_incumbent` builds one from the greedy set, the seed, the dive and
  the local search, and the engine starts with that set's value and the set as its payload (`Start::Fresh` in
  `search_forgetting`, `solver/frame/src/search/mod.rs`).
* [The design's test table](https://github.com/bvchess/taxman/blob/aeffc29/solver/docs/design/tests.md) says of R5 "No
  check: no code starts a search from a floor."  The library had one, `search::search_above` (commit 742e88a, used by
  the ledger and recorded in [the floors
  entry](../search/proving-an-upper-bound-part-of-the-way-searches-under-a-floor-2026-10/README.md)), and the cleanup
  removed it with the ledger.

The smallest change is a `floor: Option<u64>` through `search_forgetting`, which with it skips `start_incumbent` and
starts the engine from `Start::Fresh` with the floor as the best value and an empty payload.  The end of the search and
`resume_point` would read an empty payload as "no set found" (`SearchResult::floor_held`).  The checkpoint's header
(`src/search/header.rs`) would record the floor, so that a search resumes only under its own, and the finder would not
run under a floor, since it starts from the incumbent's set.  A held floor is a bound, not a game, so it needs a command
that writes no results line, `taxman floor N SCORE`, which sets the board up, takes the score less `in_the_bag` as the
floor, runs the search and prints whether the floor held, and a test of R5, which has none.

## Limits

* **Three games, the three of the smallest gaps.**  The fit's exponent is 7.8, so a game of a larger gap costs more.  By
  the fit, no game past 5060 is cheaper than these.
* **Two searches ran 3 times the fit and one 0.64 times it.**  Whether 5260 or 5264 would finish at 4 times or at 10
  times the fit is not known, since the progress lines say nothing of how much of the tree is left.
* **One run for each game and arm.**  The chain's CPU is that of a machine running 88 threads and these runs' that of
  16.
* **Phase 1's games are below 5060** and were proved by the chain by an exhausted search.

## Decision

The random sample of proofs past 5060 is dropped, and no proof of a game past 5060 is planned on the exact mode as it
stands.  Its cheapest games cost more than 40 CPU-hours without an end in sight, and the typical game costs far more
than that.

What would reopen it:

* a resume of 5260 or 5264 from its kept checkpoint, if a measure of what a proof past 5060 costs is wanted: the cost is
  then more than 44.5 CPU-hours and not yet known;
* a cheaper proof, by a bound that does more at the nodes than the GF(2) bound.  The [six experiments of carrying the
  root's bound work into the search](../search/root-work-carried-into-the-proof-search-2026-11/README.md) did not find
  one;
* the floor search above, built, which would bound opt(n) from above without proving a value;
* many hundreds of CPU-hours of EC2 for each game, which needs the approval of whoever owns the AWS account, with a cost
  estimate.

## Files

The runs were made in the scratch folder `lab/work/proofs/`, whose files these are, but for the binary and the
checkpoints below.  The paths in `score.py` and `run.sh` are those of the scratch folder.

| file | what |
|---|---|
| [run.sh](run.sh) | `./run.sh batch FILE` runs the jobs of FILE in order, skipping those done, then writes `results.md`; `./run.sh ARM N` runs one |
| [score.py](score.py) | the helpers of `run.sh` (the chain's prefix, the time spent, a game's lines, the best-known score, the budget), and `score.py table`, which makes `results.md` |
| [phase1.jobs](phase1.jobs), [phase2.jobs](phase2.jobs) | the jobs, `ARM N` a line (`follow` jobs are in the second and did not run) |
| [results.md](results.md) | the full tables of both phases, with the chain's steps, the budgets, the start and the time to the final best |
| [out/](out/) | `ARM-N.jsonl`, the results lines of game N (an unfinished search records its best so far); `ARM-N.known`, the best-known score and the bound when a game past 5060 began |
| [log/](log/) | `ARM-N.log`, each run's standard output and error, with a progress line a minute |
| [jobs.log](jobs.log) | when each job started and ended, Pacific time |

Not kept here are the binary `taxman-aeffc29` (85 MB), a copy of the clean build of master aeffc29, the output of the
three batch shells (`jobs.log` has their lines), and the checkpoints of the searches that their budgets stopped.  The
checkpoints are in the scratch folder, `lab/work/proofs/kept/`: `standalone-5260/` (4.1 MB) and `standalone-5264/`
(3.7 MB).  The checkpoint of 5304 was deleted.  Run from the scratch folder with the same binary and the flags of `run.sh` (its
`common` and `proof` lists), this resumes one:

```
taxman-aeffc29 solve N --out out/standalone-N.jsonl --checkpoint-dir kept/standalone-N --threads 16 --window 1 \
    --progress 60 --force-search --tactic prev_cap=off --tactic near_repeat=off
```

## Commits

* [aeffc29](https://github.com/bvchess/taxman/commit/aeffc29) (main repository): the build of every run, a clean build
  (the results lines name it so).  The runs changed no code.
* The commit that adds this entry and its rows in [the register's file of the start and the
  wall](../register/start-and-wall.md).
