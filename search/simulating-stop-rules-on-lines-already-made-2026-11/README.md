# Simulating stop rules on lines already made (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  The unsound mode's stop (`--stop-growth 25`, asked from level 1's budget of 131,072 work) ends a searched
game's rounds once its growth is within ±25.
[B14](../tuning-the-unsound-mode-on-a-long-chain-2026-11/README.md) found that it saves 27% of the work at level 2 and is
where games are lost: it ended five games of 3001-4000 that start streaks of short games (3332, 3384, 3750, 3774, 3850)
and 4107 of 4001-5060.  Is there a stop rule that saves most of what ±25 saves and loses none of those six, or far fewer
games overall?  This is B15 of the unsound mode.  It ran no solver and changed no code.

**Answer.**  Ask the band only after 4 rounds in a row with no gain (k4).  Simulated on lines that ran with no stop, k4
loses 7 of 2,060 games of level 2 where ±25 loses 12, and saves 28.5% of the seeded plays' work where ±25 saves 28.9%.
It ends none of 3332, 3750, 3774 and 3850 before their last gain.  It does not keep 3384 and 4107, and no rule that
saves a worthwhile share does: they gain only in round 10 or 11, and until then look like the 416 other stopped games
that gain nothing more.  Only a stop asked from level 2's budget keeps all six, and at level 2 that is no stop.  At
levels 3 to 6 on 4561-5060 no rule loses a game but the one-sided ones, and k4 costs 0.1 point of the work saved.  k4 has
to be measured in the mode, since a changed line changes the games above it.

## Method

*The words.*  A game's *gap* is its bound less its score, and its *growth* the gap less the gap of the line of n − 1 it
started from.  A *gain* is a round that raised the score.

*The lines.*  B14's `part1/l2-stopoff` and `part1/l2-control` (4001-5060) and `part2/h-control-l2` (3001-4000), level 2
with no stop, and [E2](../the-datasheet-of-the-unsound-mode-2026-11/README.md)'s chains at levels 3 to 6 (old efforts 4
to 7) over 4561-5060, five chains of 100 games, which had no stop either.  A game's line is the first written for it, as
played: the repair rewrote 2 to 4 lines of each B14 run, changing a line's moves and score and not its rounds.  The gap
below a game is the parity bound of n − 1 ([parity_2_8191](../the-parity-bound-against-the-frame-bound-2026-10/parity_2_8191.jsonl.gz))
less the score of the line it began from, which gives the growth that every B14 line records.

*The simulation* ([b15lib.py](b15lib.py)).  A rule is asked after each round from the first whose work reaches its gate.
It says yes when the growth at the score after that round is within its band and the last k rounds raised nothing.  The
first yes ends the rounds, and the game *loses* the points between that score and the final score of the line with no
stop.  The stop acts on a game's seeded play, so the 3 or 4 games a data set that were played twice with the unseeded
play kept are not simulated, and *saved* is a share of the seeded plays' work.  The default rule saves 27.2% of the work
of both plays in stopoff, where B14's real stop saved 27%.

*The work after a round.*  A line records the work only at its gains and its end, and a round with no gain costs more
as the game goes on, since the trajectories widen their neighborhoods (4005: 18,000 work a round to round 9, 48,000
after).  The straight line between the recorded rounds is 40% too high at the real stops of level 2.  The work is taken
instead from the end of every other line of the same game that began from the same moves and agrees with it as far as it
went, and between known rounds in proportion to a model of a round's cost: a trajectory plays at stage 0, then 1, then
2, as `stage_rounds` counts, at costs 0.15, 0.5 and 1 that fit the real stops.  Against the stops that the default arms
made on the same games, the model alone puts the simulated default stop on the arm's round in 88% to 92% of 224 to 481
games a data set (the straight line, 50% to 58%), nearly all the others one round off; the work at those rounds is off
by 5.6% to 8.0%, and the work saved 0.7% to 2.4% too high ([out.txt](out.txt), second section).  The nine games that the
default loses and the arm played from the same moves stop on the arm's rounds.  Losses are exact given the round and
savings are estimates: other costs, (0.1, 0.63, 1), (0.2, 0.4, 1) or equal, leave the default's lost games at 12, move
k4's from 7 to at most 8, and the shares by up to 2.4 points.

## Results

Level 2: work saved; games lost (points lost).  A rule is the band of ±25 from 131,072 work unless it says otherwise,
and kK adds that the last K rounds raised nothing.  The pooled columns add stopoff and h-control, 2,060 games.

| rule | stopoff 4001-5060 | control 4001-5060 | h-control 3001-4000 | pooled saved | pooled lost (points) |
|---|---|---|---|---|---|
| ±25 (the mode's) | 31.7%; 3 (135) | 31.5%; 2 (47) | 26.0%; 9 (228) | 28.9% | 12 (363) |
| k1 | 31.7%; 3 (135) | 31.5%; 2 (47) | 25.9%; 7 (222) | 28.8% | 10 (357) |
| k2 | 31.7%; 3 (135) | 31.5%; 2 (47) | 25.7%; 6 (214) | 28.7% | 9 (349) |
| k3, k4 | 31.7%, 31.6%; 3 (135) | 31.4%; 2 (47) | 25.5%, 25.3%; 4 (165) | 28.6%, 28.5% | 7 (300) |
| k6 | 30.3%; 2 (56) | 30.2%; 2 (47) | 24.8%; 4 (165) | 27.6% | 6 (221) |
| gate 196,608 | 15.1%; 3 (114) | 14.9%; 1 (28) | 12.2%; 3 (63) | 13.6% | 6 (177) |
| gate 262,144 | 0.0%; 0 | 0.0%; 0 | 0.0%; 0 | 0.0% | 0 |
| ±10 | 28.8%; 2 (107) | 28.5%; 1 (19) | 21.9%; 5 (198) | 25.3% | 7 (305) |
| −10 to 25, k4 | 30.3%; 2 (107) | 30.0%; 1 (19) | 23.7%; 4 (165) | 27.0% | 6 (272) |
| up to 25, k4 | 38.1%; 5 (160) | 38.0%; 4 (72) | 35.9%; 6 (192) | 37.0% | 11 (352) |
| survivor within 200 | 5.9%; 0 | 5.9%; 0 | 6.6%; 5 (134) | 6.2% | 5 (134) |

Levels 3 to 6 (E2, 4561-5060, 235 searched games a level): work saved.

| rule | level 3 | level 4 | level 5 | level 6 |
|---|---|---|---|---|
| ±25, and k4 | 49.2%, 49.1% | 58.4%, 58.3% | 63.3%, 63.2% | 65.8%, 65.8% |
| gate 196,608 | 40.8% | 54.1% | 61.1% | 64.7% |
| gate 262,144 | 33.0% | 50.1% | 59.0% | 63.7% |
| ±10 | 43.6% | 51.7% | 55.8% | 58.6% |
| up to 25, k4 | 58.2% | 69.2% | 75.0% | 78.7% |

No rule loses a game at levels 3 to 6 but the last, which loses 1 game (20 points) at levels 3 to 5 and 2 (63 points) at
level 6.  These lines hold little for a stop to lose, since 486 of 500 games (494 at level 6) are at opt(n).

The six games: the points that the rule loses by ending the game's rounds before its last gain.

| game (rounds; gains) | ±25 | k1 | k2 | k4 | gate 196,608 | ±10 | −10 to 25, k4 | up to 25, k4 |
|---|---|---|---|---|---|---|---|---|
| 3332 (9; 6, 7, 8) | 1 | no | no | no | no | no | no | no |
| 3384 (12; 1, 10) | 47 | 47 | 47 | 47 | no | 47 | 47 | 47 |
| 3750 (18; 1, 2, 7, 10, 13, 14) | 33 | 33 | 33 | no | no | 33 | no | no |
| 3774 (17; 2, 9, 10) | 5 | no | no | no | no | no | no | no |
| 3850 (15; 8, 10) | 8 | 8 | no | no | no | no | no | no |
| 4107 (11; 11) | 28 | 28 | 28 | 28 | 28 | no | no | 28 |

Gate 262,144 ends none of them at level 2.

* **Two kinds of loss.**  The default's 12 lost games ([out.txt](out.txt), "The games that the default rule loses") are
  five that were still improving (3332, 3576, 3750, 3774 and 3850 gained in the round of their stop, and k4 lets them
  run), and seven that were not (3175, 3384, 3568, 3895, 4107, 4123, 4925).  Those gain nothing more until round 6 to 11,
  and then 28 to 79 points in the last one to three of their 8 to 12 rounds.  At the stop they stand at a growth of 0
  (4107: −22), as do most of the 416 other stopped games.
* **No signal for the second kind.**  Of the 50 gains of level 2 at or after the gate, 23 follow at most 2 rounds with
  no gain, which k3 and k4 protect, 4 follow 3 or 4 and 23 follow 5 or more.  A survivor of a game below scores within
  200 points of the start in 78% of the stopped games and in 7 of the 12 lost, so a rule that keeps those going saves
  6.2%.  Only a later gate helps: 196,608 keeps 3384 and halves the saving.
* **The band's edges.**  A band of ±10 loses as many games as k4 for 3.2 points less saved, and a lower limit of −10 with
  k4 keeps 4107 (growth −22) for 1.5 points: one game.  With no lower limit and k4 the saving is 37.0%, 11 games are
  lost, and 1 or 2 at levels 3 to 6.

## Decision

Make the stop ask only when the last 4 rounds raised nothing, besides the band of ±25 from 131,072 work.  It costs 0.4
point of the work saved at level 2 and 0.1 or less at levels 3 to 6, and ends none of the five games that were still
improving.  4 over 3 is a margin: 3750's gain at round 13 came after 2 quiet rounds.  3384 and 4107 stay lost, and a
user who cannot accept that sets `--stop-growth off` and gives up the 27%.

*The measurement the mode needs.*  The rule needs a count of rounds since the incumbent's last gain where the stop is
asked.  Run B14's arms h-default-l2 and l2 again with it (level 2, seed 1, 8 threads, 3001-4000 and 4001-5060) and judge
by B14's rule: games at opt(n) for time, the streak starts at the six games and elsewhere, and the work saved against
27%.  The simulation expects 0.4 point less saved, and 5 of the 9 games lost on 3001-4000 to run on: 3332, 3750, 3774
and 3850, four of the five games whose streaks B14 counted (26 short games), and 3576.  Also run level 3 over 3001-4000
with the stop off, ±25 and k4: no lines with no stop exist at level 3 on a hard stretch, and a game stopped there gives
up more points.

## What the data cannot tell

* **Few events, chosen on the lines they are measured on.**  The default loses 12 games and k4 keeps 5 of them.  One
  seed.
* **The games above.**  A game that ends sooner hands a lower line up, and may be played twice if its growth rises above
  the push's; the simulation sees neither.
* **Levels 3 to 6 only on 4561-5060**, where 97% to 99% of the games are at opt(n).
* **The work after a round is an estimate**: the simulated stop falls a round early or late in 10% to 12% of the games
  at level 2, and the known ends of other lines are no independent test, since the arms' variants stopped many of the
  same games at the same rounds.

## Files

* [b15lib.py](b15lib.py): the lines, the estimate of the work after a round, the rules and their totals.
* [b15.py](b15.py) (`nice -n 19 python3 -I b15.py > out.txt`): the tables above and the checks.  It reads B14's and E2's
  lines and the [b13lib.py](../stopping-and-pushing-by-the-gap-2026-11/b13lib.py) of B13.
* [out.txt](out.txt): its output, with the games that each rule loses, the estimate against the real stops, and the
  survivors' scores.

## Commits

* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).  The lines are B14's (main repository
  [ecb4bc4](https://github.com/bvchess/taxman/commit/ecb4bc4)) and E2's; the study changed no code.
