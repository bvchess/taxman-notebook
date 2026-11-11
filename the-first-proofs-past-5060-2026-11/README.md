# The first proofs past 5060 (2026-11)

Part of the [lab notebook](../README.md).

Started 2026-11-10.  Concluded 2026-11-10.

**Question.**  Does a proof past 5060 finish when it gets the whole machine, in place of the budget the [proof
test](../proofs-past-5060-one-game-at-a-time-2026-11/README.md) gave it, 3 times a fit's prediction?

**Answer.**  Yes, for one game.  The search of 5260, at gap 2,106, was exhausted after 78.5 CPU-hours in all, 5.3 times
the fit's prediction and 1.8 times the proof test's budget, and its score, 8,711,408, is its best-known score.  From it
the frame solver proved 5261 to 5264 in under 3 seconds in all, each at its best-known score.  The owner stopped the run
at 5265, the next game that needs a search, as more proofs of this chain would show little.

## Method

*The words.*  The chain is the committed results of games 1 to 5060, each proven.  A *best-known* score is the highest
found for a game that no exact search has proved optimal.  A game's *gap* is its root's [parity
bound](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/parity-bound.md#the-parity-bound) less its best-known
score.  A search is *exhausted* when it ran to its end, and a *standalone* proof has no moves for n − 1 to start from.
The *fit* is the proof test's, ln(CPU-hours) = −56.84 + 7.78 ln(gap), about the 90th percentile of the chain's proofs at
a gap, and its *budget* was 3 times the fit.

*The resume of 5260.*  The proof test stopped the search of 5260 at its budget, 44.5 CPU-hours and 345,174,524 nodes on
16 threads, and kept its checkpoint.  Resuming it was the first of that entry's conditions for reopening.  The resume
ran the same clean build of master (aeffc29) with the same flags, `--force-search` and the ceiling and the near-repeat
cut off, so that nothing rests on a game below 5260.  It ran on 88 threads at nice 19 with no time limit, from 19:21
Pacific time.  The mining filler, the unsound mode's search for scores above the best-known ones, ran behind it at idle
priority.

*The run from 5260.*  When the search of 5260 ended, a run in chain mode went on from it to 5279 with every tactic at
its default, on 88 threads with no time limit.  Its output file began as a copy of 5260's lines, so that 5260's moves
were the moves for 5261.  As in [the proof test's range
runs](../proofs-past-5060-one-game-at-a-time-2026-11/README.md#method), each game of the range takes the chain's
ceiling, prime formula, repeats and near-repeat cut.

*The priority.*  The resume of 5260 and the first minute of the run from it ran in the normal scheduling class at nice
19, which the idle class of the filler yields to, and not as the chain to 5060 ran, with `--background`.  The owner
asked whether the search threads still ran at the lowest priority.  At 19:54 the run from 5260 was stopped at 5265 and
resumed with `--background` (88 workers under SCHED_IDLE, 4 helper threads at nice 19), and the filler was stopped while
the proofs held the machine.

*The check.*  `taxman verify-results` replays the games of a results file and checks them as `solve` checks its `--out`
file when it opens it.  It passed on `out/standalone-5260.jsonl`.

## Results

### 5260: the first proof past 5060

| run | threads | CPU-hours | nodes | wall | outcome |
|---|---|---|---|---|---|
| the proof test | 16 | 44.46 | 345,174,524 | 2.79 h | stopped at its budget, at its best-known score since 10 minutes |
| the resume | 88 | 34.00 | 250,921,998 more | 31.7 min | exhausted at 19:53 |
| in all | | 78.45 | 596,096,522 | 3.31 h | exhausted, score 8,711,408 |

* **The score is the best-known score.**  The search found nothing above 8,711,408, so the best-known score of 5260 is
  opt(5260), given [statement U](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/exactness.md#statement-u),
  as for every exhausted search past 2531.  The results line says `proof=exhausted`.  The prover, which proves a game
  without the frame model, has no run on 5260 recorded here.
* **The cost is 5.3 times the fit and 1.8 times the budget.**  The fit gave 14.8 CPU-hours, the budget 44.5.  The budget
  stopped the search with 58% of its nodes done, and the rest, 250.9M nodes, took 34.0 CPU-hours: 7.4 million nodes a
  CPU-hour, against 7.8 million in the first run.
* **The cost is above every chain proof at its gap.**  The chain's 52 proofs at gaps 2,000 to 2,250, of games 4392 to
  5037, took a median 11.9 CPU-hours and at most 46.1, and a median 6.5e7 nodes and at most 2.5e8 (the cheapest, game
  4901, took 0.006 CPU-hours).  The proof of 5260 took 1.7 times the dearest in CPU-hours, 6.6 times the median, and 2.4
  times the most nodes.  The proof test saw the same at 5304, which ran 3 times the fit unfinished.  The chain's proofs
  of these gaps are of smaller games, and the cost at a fixed gap may rise with n, which this entry did not study.
* **The 88 threads ran 3.8 times the nodes a second of the 16.**  The nodes a second were 34 thousand on 16 threads and
  91 to 142 thousand on 88, 132 thousand on average.  The resume used 64 CPUs on average, 122,389 CPU-seconds in 1,904
  seconds, because the root bound's last run (at 5000, from 19:09 to about 20:09) held 16 threads at the same priority.

### 5261 to 5265: the games above a proven game

| n | gap | how | time | score | its best-known score |
|---|---|---|---|---|---|
| 5261 | 2,106 | the prime formula | 0.18 s | 8,711,432 | equal |
| 5262 | 2,106 | a repeat of 5260's search (`same_search`) | 1.02 s | 8,716,694 | equal |
| 5263 | 2,106 | a repeat of 5262 (`same_search`) | 0.56 s | 8,717,350 | equal |
| 5264 | 2,090 | the ceiling | 0.92 s | 8,722,614 | equal |
| 5265 | 2,110 | a search, stopped | 378 s, 6.7 CPU-hours | 8,727,688 so far | equal, unproven |

* **The four games took 2.7 seconds in all and no search.**  Each score equals the best-known score of its game.  5264
  is the game whose standalone proof the proof test stopped at 8.9 CPU-hours: from a proven 5263 its proof is the
  ceiling, and it took under a second.  The price of a run of games is the price of its first game that needs a search.
* **5265 was stopped after 49,660,572 nodes.**  Of the 4,940 games past 5060, 1,710 need a search, and 61 have a gap
  under 2,200, most of them 5216 to 5279, of which 19 need one, 5260 and 5265 among them.  The owner saw little benefit
  in proving more of this chain.  The model of which best-known scores are optimal (v3b, in the scratch folder) puts
  97.7% of the 4,940 at opt(n), and gives a play of the miner a chance of at most 0.4% to find a gain on a game of 5216
  to 5300 in its ranking, 0.2% at 5265.  The checkpoint of 5265 is kept.

## Limits

* **One game of 19.**  Nineteen games with a gap under 2,200 need a search, and 5260 is one of them.  The cost of the
  others, and of the games of larger gaps, is not measured.  The fit was low by 5.3 times here, and by more than 3 times
  at 5304, which ran its budget unfinished.
* **The CPU-hours of the two runs differ in load.**  The resume used 64 CPUs of its 88 threads on average: the root
  bound's run at 5000 held 16 threads at nice 19 beside it, and the mining filler ran at idle priority.
* **The proof is the frame solver's.**  It rests on statement U at 5260, and 5261 to 5264 rest on the proof of 5260:
  5262 and 5263 repeat its search, and 5261 and 5264 use the score of the game before.

## Decision

The proof of 5260 and the results lines of 5261 to 5264 are kept in this entry as the first proofs past 5060.  They are
not added to `results/optimal.jsonl.gz`, which holds the chain 1 to 5060.  The run stopped at 5265, and nothing runs.
Its checkpoint is kept, and the filler runs again.

What would reopen it:

* a use for proved scores past 5060.  Each further game that needs a search costs at least tens of CPU-hours, as 5260
  did, and the chain's own proofs at gap 2,620 cost about 450.  5265 resumes from its checkpoint, which holds 49.7M
  nodes and 6.7 CPU-hours;
* a cheaper proof, by a bound that does more at the nodes, which [the experiments of carrying the root's bound work into
  the search](../search/root-work-carried-into-the-proof-search-2026-11/README.md) did not find;
* [a search from a floor](../search/a-search-from-a-floor-2026-11/README.md), if a limit tighter than the parity bound's
  is wanted on a game near 5060 without a full proof.

## Files

The runs were made in the scratch folder `lab/work/proofs/`, whose files these are, but for the build and the
checkpoints below.  The files of the proof test are in [its
entry](../proofs-past-5060-one-game-at-a-time-2026-11/README.md), whose `out/standalone-5260.known` holds the best-known
score and the bound of 5260.

| file | what |
|---|---|
| [jobs.log](jobs.log) | the lines of `jobs.log` from the resume on, Pacific time; in its last line the owner is named by role, where the original names a person |
| [out/standalone-5260.jsonl](out/standalone-5260.jsonl) | the results lines of 5260: the proof test's two lines of a stopped search, which are those of the earlier entry, and the line of the proof |
| [out/follow-5260.jsonl](out/follow-5260.jsonl) | the output file of the run from 5260: 5260's three lines, then 5261 to 5264, then two lines of the stopped search of 5265 |
| [log/standalone-5260-resume.log](log/standalone-5260-resume.log) | the log of the resume, the lines after those of the earlier entry's `standalone-5260.log`, with a progress line a minute |
| [log/follow-5260.log](log/follow-5260.log) | the log of the run from 5260, both of its starts |

Not kept here are the build `taxman-aeffc29` (85 MB, a clean build of master aeffc29) and the checkpoints of the
searches that were stopped: `ckpt/follow-5260/n5265.ckpt` (9.6 MB) and `kept/standalone-5264/` (3.7 MB), in the scratch
folder.  The command lines of the two runs were typed by hand and not recorded.  These are reconstructed from the
results lines, which give the threads, the tactics and the limits, and from the proof test's command.  The resume was:

```
nice -n 19 taxman-aeffc29 solve 5260 --out out/standalone-5260.jsonl --checkpoint-dir kept/standalone-5260 \
    --threads 88 --window 1 --progress 60 --force-search --tactic prev_cap=off --tactic near_repeat=off
```

and the run from 5260 was

```
nice -n 19 taxman-aeffc29 solve 5261-5279 --out tmp/follow-5260.jsonl --checkpoint-dir ckpt/follow-5260 \
    --threads 88 --window 1 --progress 60
```

with `--background` added from 19:54.  The same commands resume a stopped search.  The model's ranking, the chain's
proofs by gap and the best-known scores that the text cites are in the scratch folder `lab/work/gapdash/`
(`model/v3b/ranking.csv`, `proofs-gap.csv`, `games.csv`), and the owner's decisions are in the coordinator's log; none
of these is kept here.

## Commits

* [aeffc29](https://github.com/bvchess/taxman/commit/aeffc29) (main repository): the build of every run, a clean build.
  The runs changed no code.
* The commit that adds this entry and its row in [the register's file of the start and the
  wall](../register/start-and-wall.md).
