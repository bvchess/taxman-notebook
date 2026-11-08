# Stopping and pushing by the gap (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  A line's *gap* is its game's bound less its score, the bound being the parity bound, which no play
exceeds, and its *growth* the gap less the gap of the line of n − 1 it started from (the question called it the step).
Does the unsound mode gain, in games at opt(n) and in time, by ending a game's rounds where its gap has not grown, the
game being probably done, and by playing it again where its gap jumps, the game being probably short?  This is B13 of
the unsound mode (`taxman solve LO-HI --unsound --effort L --out FILE`).

**Answer.**  Yes, both, and the two together make every eighth game played twice unnecessary.  At level 3, a stop once
the gap is within 25 of the gap below, from the end of level 1's rounds on (`--stop-growth 25`), with an unseeded
second play of a game whose gap grew by more than 50 (`--push-growth 50`) and no game played twice for its n, took
4861-5060 from master's 198 of 200 games at opt(n) to 200 in 44% less time, and changed no line of 5061-5260 in 43%
less time.  The push alone played 4950 twice and so removed the one streak of the range at its start (+286
points), for 9% more time; the stop alone saved a third of the time, and in its first form, a growth of at most 0,
lost 20 points at 5060, which the band of ±25 keeps.  The bound costs 0.02 s a game at n = 5,000 and 0.05 s at 8,000.
Playing more games twice for their n is dearer for less: every fourth game kept master's 198 for 27% more time.  One
seed, two ranges, level 3.

## Method

*The bound.*  The parity bound of n is `in_the_bag` plus the frame solver's GF(2) bound of the root's node, with at
most `max_total` promotions: [the parity bound against the frame
bound](../the-parity-bound-against-the-frame-bound-2026-10/README.md) found the two equal on every board 2..8191, and
its `parity_2_8191.jsonl.gz` has the parity bound of each.  The proven lines' `in_the_bag + setup.cap` is the ceiling,
not the bound.

*Part 1, offline.*  The lines of [E2](../the-datasheet-of-the-unsound-mode-2026-11/README.md) (the chains of 100 games
over 4561-5060, levels 1 to 6, old efforts 2 to 7, before the repair) and of
[B11](../unseeded-games-above-a-short-game-2026-11/README.md)'s Part 2 (four chains of 200 games at level 3, 4861-5060
and 5061-5260, with and without every eighth game played twice; a game's last line counts).  A line's `improvements`
give the round, the work and the score of each gain, so a rule that ends a game's rounds is simulated exactly while it
ends them after the game's last gain: the line is then the same, and the rest of its work saved.  A stop before the
last gain changes the line, and counts as a loss.  The growth of a game is taken over the line of n − 1 that it
started from (`prev.score`, or the file's line before it).
A rule asked from the end of level 1's rounds on reads the game's score and work there from its *twin*, its line in
E2's chain at level 1 of the same segment, where the lines of n − 1 to n − 8 that the two start from are the same
moves (their `prev.moves_digest` agree) and both are searched; a game with no twin is counted apart.

*Part 2, in the mode.*  The study's build on master [5b27523](https://github.com/bvchess/taxman/commit/5b27523), release
without fat LTO, at -j 4: the bound in every game's setup, the stop and the push, and `--unseeded-effort L` for the
schedules.  Every arm is a chain at level 3 (524,288 work) with the defaults of the options that shape the rounds and
seed 1, from the table's 4860 or 5060.  An arm's line depends on nothing but the game, its start, the moves below, the
level, the seed and the options, so the numbers of games and points do not depend on the threads or the load; the
times are one sample each, of arms run together on the same threads.  The machine has 88 threads; the study used at
most 48, at nice 19, with nothing else heavy beside it, on 2026-11-07 from 15:04 to 18:56 (Pacific time).  Batch F's
master ran its last 22 minutes alone, after the arm beside it had ended.

## Part 1: the rules on the existing lines

**The growth of the proven games.**  On 3001-5060 it is 0 on 81.0% of the 2,060 games, above 0 on 10.1% (above 50
on 5.6%, 100 on 3.0%, 200 on 1.0% and 300 on 0.15%) and below 0 on 8.9% (below −50 on 5.5%); over 1001-5060 it runs
from −550 (4445) to 385 (4384).  In E2's 45 runs the 29 games that start a streak of short games have a growth of a
median 133, from −43 to 531, 24 of them above 0, and the 3,861 games at opt(n) from −409 to 321.

**The stop, from the start of the rounds.**  Stop a searched game at the first point, the end of its start or of a
round that raised its score, where its growth is at most T.  The share of the chains' work saved with the line
unchanged, and the lines changed:

| level | T = −25 | T = 0 | T = 25 |
|---|---|---|---|
| 1 (E2) | 8.1%, 7 changed | 63.6%, 13 | 68.7%, 19 |
| 3 (E2) | 8.1%, 8 | 64.1%, 12 | 69.8%, 18 |
| 6 (E2) | 8.2%, 9 | 65.4%, 12 | 71.2%, 18 |
| 3 (B11, 4 chains) | 7.8%, 24 | 50.5%, 31 | 54.5%, 37 |

Most games reach a growth of 0 at their start and stop there, which saves two thirds of the work, but a game whose
gap at opt(n) is smaller than the gap below (8.9% of the proven games) stops before its gains: 4768 and 5024 lose
242, 4864 117.  Nearly every lost gain comes in level 1's rounds (at 3,513 to 59,029 work, against level 1's budget of
131,072), so the stop waits for them.

**The stop from the end of level 1's rounds on** ([part1_band.py](part1_band.py)).  The one-sided stop, a growth of at
most T, and the band, a growth from −T to T, which goes on where the gap shrank by more than T:

| level | at most 0 | at most 25 | within 0 | within 25 |
|---|---|---|---|---|
| 2 (E2) | 31.4%, none changed | 35.5%, none | 23.6%, none | 29.9%, none |
| 3 (E2) | 48.9%, 5060 −20 | 55.3%, 5060 −20 | 36.6%, none | 46.9%, none |
| 4 (E2) | 58.3%, 5060 −20 | 65.9%, 5060 −20 | 43.6%, none | 55.9%, none |
| 6 (E2) | 62.4%, 5060 −20 | 70.9%, 5060 −20 | 46.7%, none | 60.2%, none |
| 3 (B11, 4861-5060) | 35.4%, 5060 −20 twice | 39.0%, the same | 26.5%, none | 32.9%, none |

The one-sided stop loses 5060, whose gap at level 1's end is 43 below the gap of 5059 and whose last gain comes in
level 3's last round, and in a streak it would stop a game that recovers late (4968 of B11's chain without, at 584,995
work; 4956 at level 6): games with no twin, where the chain below is short.  The band keeps all three.

**The push** ([part1.py](part1.py)): the games whose growth after the level's budget is above T, among the games that
start a streak and the games at opt(n):

| level | T = 0 | T = 50 | T = 100 | T = 200 |
|---|---|---|---|---|
| 1 (E2) | 3 of 4 starts, 44 of 471 at opt | 3 of 4, 24 | 2 of 4, 14 | 1 of 4, 5 |
| 3 (E2) | 2 of 2, 45 of 486 | 2 of 2, 24 | 2 of 2, 14 | 1 of 2, 5 |
| 6 (E2) | 1 of 1, 46 of 494 | 1 of 1, 25 | 1 of 1, 15 | 1 of 1, 5 |
| 3 (B11) | 2 of 2, 34 of 380 | 2 of 2, 21 | 2 of 2, 16 | 2 of 2, 6 |

The starts are 4950 (growth 312 to 376), 5040 (133) and, at levels 1 and 2, 4914 (82 to 86); 5060's (−43) is the
only one that no T catches.  A game at opt(n) whose gap jumps is pushed for nothing: 5% of them at T = 50.

**The choice.**  The stop within 25 of the gap below from the end of level 1's rounds on, which saves 47 to 60% of the
work at levels 3 to 6 and changed no line; and the push at T = 50, which catches every start of a streak with a growth
above 0 for 5% of the games at opt(n), where T = 100 misses 4914.  Part 2 measured the one-sided stop at T = 0 first
(batches A and C), then the band at 25 (batches D and F).

## Part 2: the rules in the mode

### The bound in every game

The setup that a run makes of the next game while a game plays computes the bound: `in_the_bag` plus `NodeBound::root`,
the GF(2) bound of the root's node, on the game's board.  A board with no candidates has the bound `in_the_bag`; a
prime, which the prime formula plays with no board, gets a board set up for its bound (the one its unseeded play
searches, if it is played twice).  The bound of n − 1 is the run's, or set up once for the first game of a run.  Every
line of every run of the study's build records `bound`, and it is the parity bound of `parity_2_8191.jsonl.gz` on all
2,281 games played and 4 lines repaired ([part2.py](part2.py) checks it, and that no score is above it or above
opt(n)).

The cost, on one thread of the machine while 40 others ran ([boundcost.rs](boundcost.rs)): the bound 0.017-0.018 s
at n = 5,000 and 0.052-0.053 s at 8,000, and a prime's board 0.20-0.27 s and 0.51-0.52 s more.  All of it is made on
the thread that makes the next game's setup, beside the game in play.

### The design

* `--stop-growth T` (T ≥ 0, or `off`): a searched game's rounds end once its gap is within T of the gap below, asked
  after each round from the one that reaches level 1's budget on.  So level 1 plays as before, and a level still plays
  the rounds of the levels below first.  `enough` of the rounds is now given the work of the rounds so far beside the
  promotion sum.  The unseeded play of a game played twice has no stop, as it has no ceiling.  The line records
  `growth`, and `growth_stop`, whether the stop ended the rounds before the budget.
* `--push-growth T` (any T, or `off`): a game whose gap grew by more than T in its play is played twice, as
  `--unseeded-every K` plays a game whose n is a multiple of K: an unseeded play on its board, at the level's budget,
  and the better line kept (`pushed`).  Its unseeded play counts against a budget of its own, the level's, as a game
  played twice for its n does.  A pushed game at a lower level can keep a score that a higher level, whose seeded play
  brings the growth to T or below, does not reach, so with the push a higher level's line no longer always scores at
  least as much; its seeded play still does.
* *The push's action* ([push.py](push.py), [push-out.txt](push-out.txt)).  On the flagged starts, played from the
  chains' own lines below, which are the same moves at every level of E2: more rounds (the next levels' lines) took
  4914 to opt(n) at 4 times level 1's budget and twice level 2's, never moved 4950 up to level 6 (79 short), and took
  5040 to opt(n) only at level 6.  Unseeded (`--unseeded` at level 6 with `--stop-at-known`), 4950 reached opt(n) after
  43,479 work, inside level 1's budget, 5040 after 286,254, past level 2's, and 4914 after 1,236,810, past level 4's.
  So the push replays the game unseeded at the level's budget.  On 5061, whose gap grows by 492 from the table's
  5060, neither helps: the seeded play holds 8,057,936 at levels 3 to 6, and the unseeded play reaches it only at
  level 6.
* *A fault found and fixed.*  A prime played twice remembered the problem of the board of its unseeded play for the
  repeats, and when its prime-formula line was kept, which records no setup, the next game that repeated the problem
  found no promotions and the run failed (`k1l1-4861` of batch B at 4862; 37 and 38 on a small board).  Master never
  plays a prime twice (no prime is a multiple of 8), but the push and an odd K do.  The fixed build remembers the
  problem only when the unseeded line is kept.
* *What a line depends on.*  The bound depends on n, the growth on n and the moves for n − 1, so a line still depends on
  the game, its start, the moves it starts from, the level, the seed and the options, never on the threads.  With both
  rules off, the study's build gives master's lines: 4861-4880 at level 3 with `--unseeded-every 8`, line for line but
  for the times, the threads, the build and the keys added ([same.py](same.py)).

### 4861-5060, the known games

| arm (batch, threads) | at opt(n) | streaks (first game: length, short) | points | work / 100 games | seconds / 100 games |
|---|---|---|---|---|---|
| master, every 8th twice (A, 8) | 198 | 4950: 2, 143 | | 28.4 M | 1,529 |
| stop at most 0 (A, 8) | 197 | 4950: 2, 143; 5060: 1, 20 | −20 | 17.3 M | 1,034 (−32%) |
| push 50 (A, 8) | 200 | none | +286 | 31.0 M | 1,670 (+9%) |
| stop at most 0, push 50 (A, 8) | 199 | 5060: 1, 20 | +266 | 19.9 M | 1,183 (−23%) |
| the same, none twice for its n (A, 8) | 199 | 5060: 1, 20 | +266 | 13.6 M | 816 (−47%) |
| master (F, 8) | 198 | 4950: 2, 143 | | 28.4 M | 1,473 |
| stop within 25, push 50, none twice for its n (F, 8) | 200 | none | +286 | 14.6 M | 822 (−44%) |

In every arm the moves differ from master's only at 4950 and 4951, raised by 143 each by the push (4950's unseeded
play reached opt(n), and 4951 is a prime played from it), and at 5060, lowered by 20 by the one-sided stop.  The push
played 12 games twice, 10 of them at opt(n) already (4875, 4890, 4935, 4940, 4968, 4983, 5016, 5022, 5049, 5054), and
kept the unseeded play at 4950 and 5040.  The stop ended the rounds of 50 to 55 of the 200 games.  With the push,
every eighth game played twice changed no score, for 45% more time.

### The schedules of games played twice

Unseeded plays for n alone, with the rules off (batch B, 6 threads each, beside batch C; batch E, 3 threads):

| arm | at opt(n) | work / 100 games | seconds / 100 games |
|---|---|---|---|
| master, every 8th twice | 198 | 28.4 M | 1,951 |
| every 4th twice | 198 | 35.6 M | 2,479 (+27%) |
| every 2nd twice | 200 | 50.0 M | 3,566 (+83%) |
| master at level 4 | 198 | 54.3 M | 3,530 (+81%) |
| every game twice, the unseeded play at level 1, on 4941-4970 (E) | 30 of 30 | 39.5 M | 6,617, 3.0 times the chosen setting's on the same threads (D) |

At about the same time, every second game played twice beats level 4: it plays 4950 itself twice, as the push does,
and level 4 holds 4950 143 short.  Every fourth game plays 4952 twice, as every eighth does, and keeps the streak.
Every game played twice with an unseeded play at level 1 catches 4950 at once (its unseeded play reaches opt(n) after
43,479 work), but costs every game, primes and repeats included, about 30 s of unseeded start on 3 threads.  Its run
of 4861-5060 in batch B failed at 4862 on the fault above, so it ran again on the streak alone, with the fixed build,
from master's lines below 4941.  No schedule gets more than the push, which costs 9% more than master: every fourth
game takes 27% more, every second 83% more, and every game at level 1 three times the chosen setting's time.

### 5061-5260, past the table

| arm (batch, threads) | lines that differ from master's | gap at 5061, 5160, 5260 | work / 100 games | seconds / 100 games |
|---|---|---|---|---|
| master, every 8th twice (C, 3) | | 3,049, 2,693, 2,106 | 25.8 M | 3,986 |
| stop at most 0, push 50 (C, 3) | none | the same | 19.0 M | 3,074 (−23%) |
| the same, none twice for its n (C, 3) | none | the same | 12.2 M | 2,020 (−49%) |
| stop within 25, push 50, none twice for its n (D, 3) | none | the same | 14.3 M | 2,278 (−43%) |

No line's moves differ from master's in any arm, and 5061 does not rise: its seeded and unseeded plays both hold
8,057,936, which either is opt(5061), with the largest growth of the gap seen (492, against 385 among the proven
games), or a shortfall that neither play at level 3 escapes.  The push played 11 games twice, among them 5061, and
kept no unseeded play.  Batch D ran beside the end of C, on the same threads, 46 minutes later.

## Decision

Kept, on by default, in code commit [ecb4bc4](https://github.com/bvchess/taxman/commit/ecb4bc4) on master 5b27523:
`--stop-growth 25`, `--push-growth 50`, and `--unseeded-every 0`, since with the push every eighth game played twice
changed no score of either range for half again the time.  `--stop-growth off`, `--push-growth off` and
`--unseeded-every K` give the earlier forms back, and `--unseeded-effort L`, the level of the unseeded play, stays for
measuring.  The stop's floor at level 1 and its band of ±25 are what Part 1 showed loses no line; the push's 50
catches every streak start with a growth above 0 in E2's chains at levels 1 to 6.  The fault of a prime played twice is
fixed whatever the options.

What would reopen it: a streak whose first game the push misses (a growth of 50 or less, as 5060's −43 at levels 1 and
2), which every eighth game played twice would end within 8 games; a game that the band stops short of a gain; or the
full measurement (more seeds, levels and ranges) finding the push's games at opt(n), 10 of 12 here, too dear.

## What is left

* **Levels 1, 2, 4 to 6, and more seeds.**  At level 1 the stop does nothing (its floor is the budget), and the push
  is the gain; E2's lines suggest that the stop saves 30 to 60% of the work at levels 2 to 6.
* **The push's T and its level.**  An unseeded play at level 1's budget reached opt(4950), with a quarter of a level-3
  play's work; a cheaper push would let a lower T catch more starts.
* **5061.**  Its growth of 492 is the largest seen; a play at a higher level, or a search of its board, would say
  whether it is short.

## Files

The commands ran in the study's scratch folder; the lines are gzipped, a file an arm.  [b13lib.py](b13lib.py) reads
opt(n), the parity bound and the games of a file with the growth of each.

* [part1.py](part1.py), [part1-out.txt](part1-out.txt) (`python3 -I part1.py`): the growth of the proven games, of
  E2's streak starts, the stop from the start of the rounds, and the push.
* [part1_floor.py](part1_floor.py), [part1-floor-out.txt](part1-floor-out.txt): the stop from the end of a lower
  budget's rounds on (65,536 or 131,072 work), at T = −25 to 50.
* [part1_band.py](part1_band.py), [part1-band-out.txt](part1-band-out.txt): the one-sided stop against the band, from
  level 1's budget on.
* [part1_losses.py](part1_losses.py), [part1-losses-0.txt](part1-losses-0.txt) (`python3 -I part1_losses.py 0`): each
  line that the stop at T = 0 from the start would change.
* [push.py](push.py), [push-out.txt](push-out.txt), [push/](push/): the push's actions on the flagged starts, from
  the unseeded plays of `push/runs/` (`taxman solve N --unsound --effort 6 --unseeded [--stop-at-known] --threads 10`).
* [run_jobs.py](run_jobs.py): the driver of every run (`nice -n 19 python3 -I run_jobs.py --bins KEY=TAXMAN...
  --jobs JOBS --dir DIR`), a job a line of `chains/jobs-*.txt`, each with its log.
* [chains/](chains/): the batches A to F, their jobs, lines and logs, the outputs of `part2.py` (`a-out.txt`,
  `b-out.txt`, `c-out.txt`, `d-out.txt`, `e-out.txt`, `f-out.txt`), and the diffs of the builds (`build.diff` for
  batches A, B and C, `build-band.diff` for D, E and F, against master 5b27523).  [prefix.py](prefix.py) made batch
  E's file of the lines below 4941 (`python3 -I prefix.py chains/a/master-4861.jsonl 4941 chains/e/k1l1-4941.jsonl`).
* [part2.py](part2.py) (`python3 -I part2.py DIR ARM...`): an arm's games at opt(n), streaks, points against the
  first arm, games played twice and stopped, work and seconds, and the checks of every line.
* [same.py](same.py), [final/](final/): the lines of the rules off against master's (`final/off-4861`, against B11's
  `rebase/with-l3-4861`) and the commit's defaults against batch D's (`final/defaults-4861`, `python3 -I same.py A B
  --all`).
* [boundcost.rs](boundcost.rs): the cost of the bound, an example of the frame solver kept out of the build (copy it to
  `solver/frame/examples/`, then `cargo run --release --example boundcost -- N...`).

## Commits

* [ecb4bc4](https://github.com/bvchess/taxman/commit/ecb4bc4) (main repository): the bound in every game's setup, the
  stop and the push on growth, on by default with no game played twice for its n, `--unseeded-effort`, and the fix of
  a prime played twice.
* The commit that adds this entry, and the register's file of the unsound mode with the rows of its studies moved
  there from [start-and-wall.md](../../register/start-and-wall.md).
