# Two chains past 5060 (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-08.

**Question.**  Past 5060 nothing is proven.  Played on 5061-8191, how often do level 3 with the stop on growth (chain A)
and level 4 with no stop (chain B) score differently on a game, why, how late do level 4's gains come, and does the
parity bound show the difference?

**Answer.**  On the 1,979 games both chains played, 5061-7039, A scores less than B on 205 (10.4%) and B less than A on
55 (2.8%), in 27 streaks.  At 10 streak starts the stop ended A's rounds before B's last gain, at 15 A ran its budget
and B gained in a later round, and at 2 the lower chain ran the round of the other's last gain and missed it, from
different seeds.  B's last gain needs more work than level 3's budget on 5.3% of its searched games, against 0.6% on
[E2](../the-datasheet-of-the-unsound-mode-2026-11/README.md)'s level-4 chains of 4561-5060.  The parity bound's growth
has the same tails for A, B and the better of the two, so it cannot see shortfalls of this size.  One seed each, and no
proof past 5060.

## Method

*The words* are [B14's](../tuning-the-unsound-mode-on-a-long-chain-2026-11/README.md#method): a game is *searched* when
its method is `search`; its *gap* is its parity bound less its score, and its *growth* the gap less the gap of the line
below it started from.  Level L runs rounds until their work reaches 2^L × 65,536 (524,288 at level 3, 1,048,576 at
level 4; [the unsound mode's
document](https://github.com/bvchess/taxman/blob/5bb470c/solver/docs/unsound/play.md#the-level-of-effort)).  The *stop*
ends a searched game's rounds once its growth is within ±25, and the *push* plays a game a second time, unseeded, when
its growth is above 25 ([the bound and the
gap](https://github.com/bvchess/taxman/blob/5bb470c/solver/docs/unsound/shortfalls.md#the-bound-and-the-gap)).  With no
opt(n) the chains are compared with each other: on a game one is *higher* and the other *lower*.  A *streak* is a run of
consecutive games where they differ, and its *start* the first of them, B's where B scores more there and A's where A
does.

*The runs.*  Both on master [ecb4bc4](https://github.com/bvchess/taxman/commit/ecb4bc4) (B14's build), side by side at
nice 19 on 44 threads each from 2026-11-07 23:20 (Pacific time), each game starting from the chain's own line for the
game below:

```
taxman solve 5061-8191 --unsound --effort 3 --push-growth 25 --seed 1 --threads 44 --out a-l3.jsonl
taxman solve 5061-8191 --unsound --effort 4 --push-growth 25 --stop-growth off --seed 1 --threads 44 --out b-l4.jsonl
```

A ended at 05:00 on 2026-11-08 with all 3,131 games.  B is the reference, since B14 found level 4 equal to level 3 on
4001-5060 and the stop where level 3 lost games.  A signal stopped B in game 7040 ([commands.txt](commands.txt), 06:40),
so its 1,979 lines are a pure level-4 chain of 5061-7039.  The best-known file, which master
[b16f75f](https://github.com/bvchess/taxman/commit/b16f75f) added and
[be943c4](https://github.com/bvchess/taxman/commit/be943c4) renamed, and into which A's lines were folded, is the next
entry's subject.

*The timing check* played games 6000, 7000 and 8000 unseeded at level 3 on 29 threads before the run: 24.0, 27.8 and
35.9 s for 12, 15 and 8 rounds, scoring within 579 points of the chains' lines ([out.txt](out.txt) compares them with
the chains' seconds).

*The analysis* is [two_chains.py](two_chains.py).  A game's line is the last the file has for it, and all 3,173 lines of
A and 1,995 of B pass its checks of the build, level, options, `bound` and `growth`.  A start's *cause* is read from the
lines: the play that wrote the higher chain's line made its last gain in some round, and the lower chain's play of the
same kind either ran that round (it *missed* the gain) or ended before it, by the stop or at its budget.  The *seeds* of
a seeded play are the line below, its trajectories and its survivors' scores, which a line records, except that the
line of an unseeded play records none for its game's seeded play.

## Part 1: where the chains differ

| games | in both | B scores more | A scores more | starts (B / A) | points (B / A) | A s/game | B s/game | A stopped | pushed (A / B) |
|---|---|---|---|---|---|---|---|---|---|
| 5061-5310 | 250 | 2 (0.8%) | 0 | 1 / 0 | 6 / 0 | 3.8 | 8.3 | 47 | 17 / 17 |
| 5311-5560 | 250 | 24 (9.6%) | 4 (1.6%) | 4 / 0 | 1,252 / 220 | 5.4 | 11.5 | 51 | 24 / 23 |
| 5561-5810 | 250 | 65 (26.0%) | 3 (1.2%) | 7 / 0 | 2,811 / 84 | 7.0 | 14.3 | 48 | 27 / 25 |
| 5811-6060 | 250 | 21 (8.4%) | 1 (0.4%) | 4 / 1 | 1,064 / 66 | 6.1 | 13.8 | 51 | 16 / 15 |
| 6061-6310 | 250 | 2 (0.8%) | 0 | 2 / 0 | 285 / 0 | 6.1 | 15.1 | 55 | 19 / 19 |
| 6311-6560 | 250 | 26 (10.4%) | 5 (2.0%) | 4 / 0 | 720 / 193 | 5.7 | 14.3 | 45 | 18 / 20 |
| 6561-6810 | 250 | 47 (18.8%) | 42 (16.8%) | 2 / 0 | 4,213 / 9,738 | 6.3 | 14.7 | 52 | 19 / 21 |
| 6811-7039 | 229 | 18 (7.9%) | 0 | 2 / 0 | 534 / 0 | 5.1 | 12.7 | 46 | 13 / 13 |
| 5061-7039 | 1,979 | 205 (10.4%) | 55 (2.8%) | 26 / 1 | 10,885 / 10,301 | 5.7 | 13.1 | 395 | 153 / 153 |

* **A few long streaks make the differences.**  The 260 games are 27 streaks; the longest, 6555-6599, holds 45 games and
  9,960 of the 21,186 points.
* **A scores more in six episodes**, each below a game where B led or had led within 8 games.  One, 6560-6599, holds 40
  of the 55 games and 9,695 of the 10,301 points: A's start from its own line below (53 points under B's) scored
  13,528,608, above both of B's plays (13,528,579 and 13,528,468).
* **Level 4 costs 2.31 times A's seconds a game** (13.1 against 5.7) and 2.9 times its work.  A stopped 395 of its 917
  searched games (43.1%) and pushed 153 (16.7%); B pushed 153.

## Part 2: the causes of the 27 streak starts

| cause, as the lines show it | starts | points at the starts | games, points in their streaks | in the unseeded play of a pushed game |
|---|---|---|---|---|
| the stop ended A's rounds, and B's last gain is in a later round | 10 | 600 | 32, 1,452 | 0 |
| A ran its budget, and B's last gain is in a later round | 15 | 615 | 213, 19,132 | 6 |
| the lower chain ran the round of the other's last gain and missed it | 2 | 114 | 15, 602 | 0 |

* **The stop** ended A's rounds at round 3 to 6, where B's last gain was in round 5 to 9, from the same seeds in all 10
  (5672 is read at 5673, from which the repair raised it).  In 7 the last 4 rounds before the stop raised nothing, so
  the rule of [B17](../the-stop-that-waits-for-quiet-rounds-2026-11/README.md), which waits for 4 quiet rounds and came
  after this run started, would end them too.
* **The budget** is the larger cause: A ran 8 to 13 rounds and B's last gain was in round 11 to 19.  Six are in the
  unseeded play of a pushed game, whose seeded plays' seeds are not recorded, and 8 of the other 9 have the same seeds.
* **A miss** needs different seeds: 5625 (B's gain in round 2, A ran 10 rounds) and 5819 (A higher; A's gain in round 6,
  B ran 14), both within 8 games of an earlier difference, as is the budget start 5814.  In all 684 seeded plays that
  began from the same seeds in both chains, B's improvements within A's rounds are A's; 202 began from different seeds.

## Part 3: how late the gains come

Searched games (not stopped at the ceiling) whose last gain, by the work recorded with it, is above the budgets of level
2 (262,144) and level 3 (524,288).  *Gained* games had a gain in their rounds.  Level 4 has the stop in B14, and none in
E2 and B.

| chain | games | searched | gained | above level 2's budget | above level 3's budget |
|---|---|---|---|---|---|
| B | 5061-5310 | 80 | 30 | 4 (5.0%) | 2 (2.5%) |
| B | 5311-5560 | 95 | 36 | 9 (9.5%) | 5 (5.3%) |
| B | 5561-5810 | 96 | 28 | 11 (11.5%) | 8 (8.3%) |
| B | 5811-6060 | 85 | 28 | 13 (15.3%) | 6 (7.1%) |
| B | 6061-6310 | 88 | 25 | 5 (5.7%) | 3 (3.4%) |
| B | 6311-6560 | 79 | 24 | 10 (12.7%) | 5 (6.3%) |
| B | 6561-6810 | 88 | 20 | 7 (8.0%) | 5 (5.7%) |
| B | 6811-7039 | 74 | 16 | 4 (5.4%) | 2 (2.7%) |
| B | 5061-7039 | 685 | 207 | 63 (9.2%) | 36 (5.3%) |
| E2, level 4 | 4561-5060 | 171 | 42 | 2 (1.2%) | 1 (0.6%) |
| B14, level 4 | 4561-5060 | 170 | 42 | 3 (1.8%) | 1 (0.6%) |
| A, level 3 | 5061-7039 | 684 | 206 | 42 (6.1%) | 7 (1.0%) |

* **Past 5060 the gains come later**: the share above level 2's budget goes from 1.2% and 1.8% to 9.2%, and above level
  3's from 0.6% to 5.3%.  B's segments peak at 15.3% and 8.3% in the first 1,000 games and give 5.4% and 2.7% in the
  last, a step up and no steady rise.
* **A round costs more and the last gain is in a later round**: the median work of a round is 79,924 against 61,520 in
  E2, the median round of the last gain 3 against 1, and 30.2% of searched games gain against 24.6%.
* **A gain above a budget may be that of the round that reaches it**, which the level plays: all 7 of A's above level
  3's budget are.

## Part 4: the parity bound

Per 100 searched games, the share with a growth above 100, 200 and 400 points in absolute value, and above 0.02, 0.04
and 0.08 of n.  Proven: opt(n) of 3001-5060, where B14's lines say which games are searched.  Past 5060: the better of
A and B, and A alone from 7040.

| games | searched | above 100 | 200 | 400 | above 0.02 n | 0.04 n | 0.08 n |
|---|---|---|---|---|---|---|---|
| proven 3001-5060 | 946 | 11.4 | 3.6 | 0.4 | 16.4 | 5.9 | 1.0 |
| 5061-6060 | 464 | 18.5 | 6.5 | 1.3 | 16.4 | 5.6 | 0.6 |
| 6061-7060 | 463 | 17.1 | 8.6 | 3.0 | 14.3 | 7.1 | 1.7 |
| 7061-8191 | 524 | 15.5 | 8.6 | 1.9 | 10.9 | 3.6 | 0.4 |
| 5061-8191 | 1,451 | 17.0 | 7.9 | 2.1 | 13.7 | 5.4 | 0.9 |

* **In points the tails are heavier past 5060, and scaled by n they match.**  The largest growth of a proven searched
  game is 385 points (4384), 0.0878 of n; past 5060, 14 of 1,451 searched games are above 385 points and 5 above
  0.0878 n.
* **The growth scales with n.**  Over the games whose growth is not 0, the 90th percentile of |growth| rises from 79
  points at 1001-1500 to 234 at 4501-5060, 3.0 times for a 3.8 times larger n, and is 0.042 to 0.064 of n in the eight
  proven windows of about 500 games and 0.031 to 0.070 in the six past 5060.
* **The bound cannot see shortfalls of this size.**  On 5061-7039 A, B and the better of the two have the same tails
  (below), though A is below the better of the two on 205 games (10,885 points) and B on 55 (10,301).  The push sees
  some: A's growth is above 25 at 11 of the 26 starts where A is lower, where it pushes 16.7% of its searched games.

| scores, 5061-7039 | searched | above 100 | 200 | 400 | above 0.02 n | 0.04 n | 0.08 n |
|---|---|---|---|---|---|---|---|
| A | 917 | 18.3 | 7.7 | 2.4 | 15.7 | 6.7 | 1.1 |
| B | 917 | 17.8 | 7.5 | 2.2 | 15.3 | 6.4 | 1.1 |
| the better of A and B | 917 | 18.0 | 7.6 | 2.2 | 15.5 | 6.4 | 1.2 |

## What it means

* **Level 3 falls short of level 4 on 10.4% of the games both played, and level 4 of level 3 on 2.8%.**  The better of
  the two is a lower bound on opt(n), so A scores opt(n) on at most 89.6% of these games and B on at most 97.2%.  In
  B14's range, 4001-5060, the two played the same moves on all 1,060 games.  Past 5060 the budget causes more of the
  difference than the stop, and level 4 does not contain level 3's rounds once the seeds differ.
* **The gains come later past 5060, so a level's fixed work buys less there:** level 4's last gain needs more work than
  level 3's budget on 5.3% of its searched games against 0.6%, and a round costs 30% more.
* **The bound cannot see shortfalls of this size; a comparison between independent runs can.**  Its tails look heavier
  in points past 5060, but the proven games' growth scales with n, and scaled by n the tails match.  Three sets of lines
  with very different known misses have the same tails.  The best-known file follows for that reason: runs offer their
  lines to it and seed from it.

## What the data cannot tell

* **One seed each.**  Another seed would move which games start streaks, and one streak holds 9,960 of the 21,186
  points.
* **No proof past 5060.**  The better of A and B is a lower bound on opt(n), a game both miss shows nowhere, and only A
  played 7040-8191.
* **The rest.**  A's stop is the gap alone, the rule before B17's, which this entry does not measure.  The seconds are
  those of two chains side by side on one machine.  The causes of the 3 starts with different seeds (5625, 5814, 5819)
  and of the 6 that are an unseeded play's rest on plays that did not begin alike or on seeds no line records.

## Files

The commands ran in the scratch folder `unsound-run/`; the lines are gzipped.

* [commands.txt](commands.txt): the commands of the run and of what followed it, with their times; the first two are
  this entry's chains.
* [runs/](runs/): the chains' lines (`a-l3.jsonl.gz`, `b-l4.to-7039.jsonl.gz`) and logs.
* [timing/](timing/): `u3-N.jsonl.gz`, `.log` and `.time` (GNU time) of `taxman solve N --unsound --unseeded --effort 3
  --seed 1 --threads 29`, for N = 6000, 7000 and 8000.
* [two_chains.py](two_chains.py) (`nice -n 19 python3 -I two_chains.py --results PATH > out.txt`, PATH being
  `results/optimal.jsonl.gz` of the main repository) and its output [out.txt](out.txt): the checks, the tables of this
  entry, the cause of every start, and the windows of the growth.  It reads B14's and E2's lines and the [parity
  bound](../the-parity-bound-against-the-frame-bound-2026-10/parity_2_8191.jsonl.gz).

## Commits

* [ecb4bc4](https://github.com/bvchess/taxman/commit/ecb4bc4) (main repository): the build of every run.  The study
  changed no code.
* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).
