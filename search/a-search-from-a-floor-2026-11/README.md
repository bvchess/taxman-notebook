# A search from a floor (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-10.  Concluded 2026-11-10.

**Question.**  Can the frame solver bound a game's optimal score from above by a search from a floor, and would that
bound a game past 5060 more tightly than the bounds it has, at a cost the machine can pay?

**Answer.**  The solver can: `taxman floor N SCORE`, built on the branch `floor-search`, held at opt(n) on five proven
games, and on 4848 it cost 0.94 times the nodes and 0.97 times the CPU of the game's standalone proof.  The owner parked
it without merging it: the parity bound already proves every best-known game past 5060 within 0.049% of optimal, and a
floor tighter than that costs about a proof at the gap that is left, which only the games near 5060 can pay.

## Method

*The words.*  A game's score is its `in_the_bag` points plus the sum of its promotions, and the search looks for the
promotion set of the largest sum, its *incumbent* being the best set found so far.  A *floor* F is an incumbent worth F
with no set behind it.  A search from a floor that ends having found nothing proves that no game of n scores more than F
plus `in_the_bag` ([the floor lemma
(R5)](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/search-rules.md#the-floor-lemma)), given [statement
U](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/exactness.md#statement-u), as for every exhausted search
of the frame solver.  A search from a floor below opt(n) finds a game that scores more.  A *best-known* score is the
highest found for a game that no exact search has proved optimal.  A game's *gap* is its root's [parity
bound](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/parity-bound.md#the-parity-bound) less its best-known
score, or less opt(n) for a game of the chain.  A *standalone* proof is a proof with no moves for n − 1, as [the proof
test](../../proofs-past-5060-one-game-at-a-time-2026-11/README.md) ran them.

*Why a floor.*  A game past 5060 has a best-known score and no proof.  A floor at the best-known score plus d, if it
holds, bounds the game's optimum from above within d of that score.  Raising the floor by d acts as a bound d tighter at
every node, so the search costs about a proof of the game at gap − d.  The proof test found that the build could not run
one, and named the smallest change.

*The change*, on the branch `floor-search` of the main repository, one commit (0316cd8) on master's ba59242:

* `search::search_floor(prepared, cfg, floor, resume)` runs the exact search from an incumbent worth `floor` whose set
  is empty, with no start (greedy set, seed, dive, local search), no seed and no finder.  `search_forgetting` takes a
  `floor: Option<u64>`.  `SearchResult::floor_held` says that the search completed with nothing above the floor.  The
  end of the search and `resume_point` take the empty set worth the floor as the incumbent.  The earlier `search_above`
  (742e88a, removed in 7088401 with the ledger) did the same, without the checkpoint's record of the floor.
* The checkpoint header records the floor, a byte and a u64 after the tactics, so the format is version 9 (47 bytes).  A
  checkpoint resumes only under its own floor, and one of a search from a start resumes under none.  The probe's two
  windows are made again with `perf make-window`, and the probe's fingerprint stays aff672d2dccda0dc.
* `solver::floor` and the command `taxman floor N SCORE` set the board up as `solve` does (`prepare_search`, now
  shared), search from SCORE less `in_the_bag`, keep the checkpoint and clock of `solve`, and write no results line.
  The command prints `held` (opt(N) ≤ SCORE), `beaten` (a game that scores more, with its moves, which is opt(N) if the
  search ended) or `open` (stopped, nothing found).  It replays the moves of a game it finds and checks the outcome
  against the built-in table where the table has the game.
* Tests, since R5 had none.  On every game to 400 that needs a search, a floor below P\* finds it and one at P\* or
  above holds (one thread, and four threads without the rule of symmetric pairs on a sample).  A floor at P\* searches
  the tree of the search seeded with an optimal set, step for step (800: 1,103 steps; 1000: 1,734, in a release run).  A
  floor at a ceiling ends before the search starts.  A stopped search resumes under its own floor only.  The header
  round-trips.  The command holds at opt(800), is beaten at opt − 1, stops and resumes, and `solve` and another floor
  refuse its checkpoint.  Each new test uses under 1.1 s of CPU in the test profile.  The non-release suite, clippy, fmt
  and the docs test pass, and the floor tests pass in a release build.

*The checks on proven games.*  `validate.sh` ran 16 threads at nice 19 from 17:17 Pacific time.  For games 300, 700,
1200, 1600 and 2000 it searched from opt(n), which must hold, and from opt(n) − 1, which opt(n) itself must beat.  Then
it searched 4848 from opt − 300 (a limit of 1,200 s) and from opt (a limit of 2,400 s, about 3 times its standalone
proof).  The standalone proofs of 1200, 1600 and 2000 ran on the same build with no earlier game and the flags
`--force-search`, `--tactic prev_cap=off` and `--tactic near_repeat=off`, as the proof test ran 4848.

## Results

### The floor lemma holds on every proven game tried

| n | floor at | outcome | floor | root bound | nodes | CPU s | standalone proof: nodes, CPU s |
|---|---|---|---|---|---|---|---|
| 300 | opt | held | 2,138 | 2,142 | 1 | 0.001 | |
| 300 | opt − 1 | beaten by opt | 2,137 | 2,142 | 2 | 0.001 | |
| 700 | opt | held | 12,017 | 12,039 | 2 | 0.003 | |
| 700 | opt − 1 | beaten by opt | 12,016 | 12,039 | 4 | 0.003 | |
| 1200 | opt | held | 33,895 | 34,096 | 2,164 | 0.35 | 9,530, 1.17 |
| 1200 | opt − 1 | beaten by opt | 33,894 | 34,096 | 2,042 | 0.36 | |
| 1600 | opt | held | 58,799 | 59,148 | 4,550 | 1.08 | 9,773, 1.99 |
| 1600 | opt − 1 | beaten by opt | 58,798 | 59,148 | 4,579 | 1.06 | |
| 2000 | opt | held | 94,885 | 95,376 | 34,505 | 5.94 | 41,156, 6.93 |
| 2000 | opt − 1 | beaten by opt | 94,884 | 95,376 | 31,866 | 5.61 | |

The floor and the root bound are promotion sums, and opt(n) is the chain's (`opt.txt`).  A floor at opt held and one a
point below was beaten by opt(n), on all five games.  The ratio of the floor search's nodes to the standalone proof's
rises with the game, 0.23, 0.47 and 0.84 at 1200, 1600 and 2000.

### 4848 from opt: the floor search is the proof

The search from opt(4848) = 7,392,206, a floor of 534,239, held.

| run | nodes | CPU-hours | wall s |
|---|---|---|---|
| floor at opt, this build | 21,676,752 | 3.31 | 746 |
| standalone proof (the proof test's, build aeffc29) | 23,075,195 | 3.42 | 780 |
| seeded proof, no ceiling (the proof test's) | 21.9M | 3.58 | 828 |

The floor at opt took 0.94 of the standalone proof's nodes and 0.97 of its CPU.  It searches the tree that the seeded
search makes, since the seeded search also starts at opt.  The root's bound is 536,179, so the search closed a gap of
1,940.

### 4848 from opt − 300: beaten, but slowly

The search from a floor of 533,939 found a set above its floor after 3 minutes of 16 threads (0.74 CPU-hours, 4.6M
nodes), and its limit of 1,200 s stopped it at opt − 6, after 5.26 CPU-hours and 34.2M nodes.  That is 1.5 times the
standalone proof's CPU, unfinished.

| active | CPU | nodes | best less P\* |
|---|---|---|---|
| 3m00s | 44m | 4.6M | −130 |
| 4m30s | 1.1h | 7.0M | −121 |
| 14m30s | 3.8h | 23.4M | −39 |
| 15m30s | 4.1h | 25.1M | −15 |
| 16m30s | 4.3h | 27.2M | −6 |
| 20m00s (stopped) | 5.26h | 34.2M | −6 |

A search from a floor has no start and no finder, so it finds sets only through its tree, which a floor below P\* prunes
less than the proof's.  The standalone searches of the proof test, with a start and a finder, were at opt(n) within 1 to
15 minutes on the games the chain proved.  A floor below opt(n) is a slow way to find it.  The floor search is for a
floor that is expected to hold.

### Not run: game 5061

The planned run was a search of 5061 from its best-known score plus 1,000, with a budget of 60 CPU-hours on 16 threads,
then plus 500 if that held cheaply.  The owner changed the plan while the change was being built, to build and validate
only.  The costs below are estimates.  The best-known score of 5061 is 8,057,936 and its gap 3,049.

* A fit to the 1,250 chain proofs with gap 500 or more is log10 nodes ≈ 3.85 + gap/476 (residual standard deviation 0.60
  decades).  A floor 1,000 above the best-known score leaves a gap of 2,049, which the fit prices at 1.4e8 nodes.  The
  proof of 4848, at gap 1,940, took 2.3e7 nodes and 3.4 CPU-hours.
* Each 500 points tighter costs about ten times more, 10^(500/476) by the fit.
* A root bound from [the root-bound studies of 2026-11](../root-bounds-for-the-odd-cores-past-5060-2026-11/README.md)
  already proves 5061 within 1,815 points of its best-known score.

## Limits

* **The estimates for 5061 are not runs.**  Past 5060 the fit has been low: the exhausted search of 5260, at gap 2,106,
  took 596M nodes, 3.2 times the fit's 1.9e8 ([the first proofs past
  5060](../../the-first-proofs-past-5060-2026-11/README.md)).  A floor search near 5061 probably costs more than the
  estimate.
* **One run for each floor on 4848, and five small games.**  The CPU times are those of 16 threads at nice 19 on a
  machine shared with other work, and the comparison with a standalone proof at 4848 is of one game.
* **The standalone proofs of 1200, 1600 and 2000** ran on a build that their results lines name as a dirty ba59242, made
  from the branch's working tree a minute before its commit.  The floor runs used the build of the commit.

## Decision

Parked on 2026-11-10, not merged.  The branch `floor-search` keeps the code, and `patches/` the commit.  The reasons:

* **The parity bound already limits every best-known game past 5060.**  Given statement U, each of the 4,940 best-known
  scores is within 0.049% of optimal, the largest share being game 6664 with 6,862 points of 13,972,287, and within
  0.033% of the scores taken together.
* **A tighter limit costs a proof.**  A floor at the best-known score plus d costs about a proof at the gap less d.
  Near 5061 a limit of about 1,000 points costs about what the proof of 4848 cost, and each 500 points tighter about ten
  times more, while a root bound already proves 5061 within 1,815.  Farther up the floor reaches nothing new: the gap is
  3,823 at 7100 and 11,468 at 10000, so the same 1,000 points leaves a gap that no proof pays.
* **At a floor equal to the best-known score it is a proof,** at 0.97 times a standalone proof's CPU on 4848, so it is
  no cheaper way to prove a game.

What would reopen it:

* a need for proved limits tighter than the parity bound's on games near 5060;
* a test bench for bound work: a floor raised by d acts as a bound d tighter at every node, so a search from a floor
  predicts what a tighter bound would save, before the bound exists.

Three things to fix before any merge, and a cost to accept:

* The floor stands as an empty set worth the floor, which breaks the incumbent's rule that a set is worth its sum.  The
  code makes an exception, `stands`, in four places: the result of a search that starts at its ceiling, the offer of a
  resumed incumbent to the search's control, the assert at the end, and the check of a kept incumbent in `resume_point`.
  A type for "a set, or a bare value" would remove them.
* `search_forgetting` gains a 13th positional argument, mostly `None`.  An options struct would hold it.
* `solver/floor.rs` builds an engine configuration that repeats most of `solve`'s.
* The checkpoint format moves from 8 to 9, so a merged build cannot resume the checkpoints of older builds.

## Files

The runs were made in the scratch folder `lab/work/floor/`, whose files these are, but for the build and the checkpoint
below.  The paths in `run.sh` and `validate.sh` are those of the scratch folder.

| file | what |
|---|---|
| [patches/](patches/) | the commit 0316cd8 as one `git am` patch (`git format-patch`), unchanged, for master's ba59242 |
| [run.sh](run.sh) | `./run.sh TAG N SCORE [FLAG...]` runs one `taxman floor N SCORE` on 16 threads at nice 19, with its checkpoint in `ckpt/TAG`; the same command resumes a stopped search |
| [validate.sh](validate.sh) | the checks above, job after job |
| [opt.txt](opt.txt) | opt(n) of the games checked, from `results/optimal.jsonl.gz` |
| [out/](out/) | `TAG.txt`, a run's standard output: its summary line, and the moves of a game it found |
| [log/](log/) | `TAG.log`, a run's progress lines, for the two runs on 4848 (the other runs wrote none) |
| [jobs.log](jobs.log) | when each run started and ended, Pacific time |
| [standalone/](standalone/) | `sN.jsonl`, the standalone proofs of 1200, 1600 and 2000 |

Not kept here are the build `taxman-floor` (74 MB), a release build of 0316cd8, and the checkpoint of the stopped search
from opt − 300 (1.6 MB, in format 9, which only that build reads).  Both are in the scratch folder `lab/work/floor/`,
where `./run.sh v4848-below300 4848 7391906 --progress 30` resumes the search.  The fit, the gaps and the best-known
scores of the estimates are from the scratch folder's `lab/work/oddcore/brief.md` and `lab/work/gapdash/games.csv`, and
the owner's decision is in the coordinator's log; none of the three is kept here.

## Commits

* 0316cd8 (branch `floor-search` of the main repository, never pushed): the search from a floor, the command and the
  tests.  Its parent is [ba59242](https://github.com/bvchess/taxman/commit/ba59242), the master the proof test and the
  other studies of 2026-11-10 used, which differs from aeffc29, the proof test's build, by one document.
* The commit that adds this entry and its rows in [the register's file of the start and the
  wall](../../register/start-and-wall.md).
