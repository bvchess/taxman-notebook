# Repairing games from above (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-07.  Concluded 2026-11-07.

**Question.**  In the unsound mode a game that falls short hands its shortfall on to the games above it, which start
from its line.  Can the games above a short game repair it, and does the simplest repair a run can make improve the
lines?  This is B10 of the unsound mode (`taxman solve LO-HI --unsound --effort E --out FILE`).

**Answer.**  If their lines were optimal, the games above would repair nearly every short game: what survives of the
proven game of n + 1 is opt(n) in 57 of 73 hard games, and trajectories from the proven games above bring 72 of the 73
to opt(n), against 65 to 67 without, almost all of it before any round.  In a run the lines above a short game are made
from it and mostly survive no better, so the repair kept is the cheap part: a walk down from each line a run records,
which replaces every line below that what survives of a line above beats.  It runs no rounds and took 0.2 to 1% of a
chain's time.  On 4561-5060 at effort 4 it raised the games at opt(n) from 479 to 482 of 500; past the table, on
5061-5260 at effort 4, it raised 2 of the 200 lines by 15 points each.  No line of any chain scored lower with it.  It is
on by default; `--no-repair` turns it off.

## Method

A game of the unsound mode ([unsound.md](https://github.com/bvchess/taxman/blob/56dcbdd/solver/docs/unsound.md)) starts
from the run's line of n − 1: a prime plays the prime formula on it, a repeat plays an earlier line's promotions, and a
searched game starts from what survives of it and stops at the run's ceiling, n + score(n − 1).  So a short line is
handed upward until a searched game reaches opt(n) on its own; the [datasheet of the unsound
mode](../the-datasheet-of-the-unsound-mode-2026-11/README.md) (E2) found 81 to 87% of its short games handed on, and the
streak of 4950 lasting 18 to 50 games.  Every run below used `--back 8 --tilt 25 --widen 4 --seed 1` (the defaults), at
nice 19 on a machine of 88 threads that other work shared.  "Without" is master 50db88e's build, "with" this study's
on 50db88e, both built for release without fat LTO.  The commit, [56dcbdd](https://github.com/bvchess/taxman/commit/56dcbdd),
is that code rebased onto master 954d664 (B9), whose setups made while the game before plays now share one store of
boards with the boards the repair keeps; its build gives the same lines, but for the times, the threads and the build,
on 32 threads: 4761-4860 at effort 1 with the repair against the chain of the same games below, 4561-4600 at effort 2
with it against the build on 50db88e, and without it against 954d664's ([rebase/](rebase/), [same.py](same.py)).
The quality numbers rest on the lines, which do not depend on the threads or the load; the times are one sample each.

## What the proven games above could give

**A game above, taken down.**  The moves of a game of N, less those above n, are a game of n: leaving a move out only
leaves more numbers on the board, so every kept move still has a proper divisor when it is made.  This is the
construction of [the ceiling lemma
(N4)](https://github.com/bvchess/taxman/blob/56dcbdd/docs/theory/neighbors.md#the-ceiling-lemma), once for each number
above n.  The solver already takes such a game down for a trajectory of `--back`:
[`Board::seed`](https://github.com/bvchess/taxman/blob/56dcbdd/solver/frame/src/board.rs) drops the moves above n, and
`search::seed_survivors` keeps the candidates among the rest that n's frames can still promote, from the largest down,
and makes their moves.  Those survivors beat a greedy finish of the same moves (the largest legal move first) in 227 of
the 288 pairs of a game and a proven game above it, and tie it in the other 61 ([projection.py](projection.py),
[projection-out.txt](projection-out.txt)).

**The study.**  `--above J`, built for it, gives game n a trajectory from each distinct set that survives of the moves
for n + 1, ..., n + J, and with `--from-known` takes them from the built-in table.  The 73 games are P1's 63, the
near-ties 3968, 4134, 4225 and 4950, E2's games first short in a run, and 3610 and 3844, the other two games that [race
R1](../a-share-of-tilted-neighborhoods-2026-11/README.md) missed at effort 7 ([games-part1.txt](games-part1.txt)).  Each
was played alone from the proven game of n − 1 with `--stop-at-known`, at efforts 4 and 7, with J of 0, 1, 2 and 4
([run_part1.py](run_part1.py)).

| J, the games above | at effort 4 | at effort 7 |
|---|---|---|
| 0: the start and `--back 8` alone | 65 of 73 | 67 of 73 |
| 1, 2 or 4 | 72 | 72 |

What survives of the proven game n + j is opt(n) itself in 57, 43, 24 and 10 of the 73 games for j of 1 to 4 (5060 has
no game above it in the table), so nearly all of the gain is in round 0: with J ≥ 1, 65 games hold opt(n) before any
round, 41 of them by the trajectory from n + 1.  Of the 8 games that effort 4 misses without the games above, 6 are
reached at work 0 from n + 1, 3723 from n + 1 after 22,899 work, and 3968 by no arm, since what survives of 3969 to 3971
is 3 short of opt(3968).  The games where it matters:

| n | survivors of n + 1 .. n + 4, short of opt(n) | effort 4, J = 0 | J = 1 | J = 2 | J = 4 | effort 7, J = 0 |
|---|---|---|---|---|---|---|
| 3552 | 1376, 1376, 1534, 1534 | 47010 (−7) | 25432 (−7) | 25432 (−7) | 49170 (−7) | 47010 (−7) |
| 3610 | 0, 1133, 1133, 1133 | − | 0 (+1) | 0 (+1) | 0 (+1) | − |
| 3723 | 882, 2133, 2280, 2280 | − | 22899 (+1) | 31246 (+1) | 22672 (+1) | 3060015 (−4) |
| 3844 | 0, 0, 0, 1275 | − | 0 (+1) | 0 (+1) | 0 (+1) | − |
| 3904 | 1065, 2319, 2319, 2319 | 23723 (−1) | 13438 (−1) | 16120 (+1) | 16120 (+1) | 23723 (−1) |
| 3927 | 1948, 1948, 2528, 2528 | 46204 (−1) | 15873 (+1) | 15873 (+1) | 24199 (+1) | 46204 (−1) |
| 3968 | 3, 3, 3, 1905 | − | − | − | − | − |
| 4134 | 0, 1368, 2550, 2550 | − | 0 (+1) | 0 (+1) | 0 (+1) | − |
| 4225 | 0, 0, 0, 0 | − | 0 (+1) | 0 (+1) | 0 (+1) | − |
| 4752 | 2225, 2225, 2225, 2225 | 15705 (−3) | 15256 (−3) | 15256 (−3) | 15256 (−3) | 15705 (−3) |
| 4950 | 0, 2468, 2468, 2468 | − | 0 (+1) | 0 (+1) | 0 (+1) | − |
| 5040 | 0, 0, 0, 0 | − | 0 (+1) | 0 (+1) | 0 (+1) | 2389779 (−1) |

A cell is the work at which the game reached opt(n) and the trajectory that made it ("−j" the survivors of n − j, "+j"
those of n + j), or "−" if it did not; with J ≥ 1, effort 7 reaches each game where effort 4 does.
[part1-out.txt](part1-out.txt) has every game.  This is an upper bound: the proven game of n + 1 is optimal, often at
its ceiling, where its optimal set less n + 1 is an optimal set of n ([the step
theorem](https://github.com/bvchess/taxman/blob/56dcbdd/docs/theory/neighbors.md#the-step-theorem)), and often a prime
made from opt(n).

**In a run.**  The same measures on E2's own lines ([run_inrun.py](run_inrun.py), [inrun/](inrun/)): each game short in
E2 was played again from E2's line of n − 1 with E2's lines of the 8 games above it as `--above 8`.  In the streak of
4950 at efforts 4 and 7, what survives of the lines above never beats the short line, since they are a prime and
repeats made from it and searches stopped at the ceiling it set; replayed at effort 4 with them, 4950, 4952, 4953 and
4956 end where E2's games did, after the full budget.  In the streak of 5040, 5043 reached opt(5043) on its own, and
what survives of it is opt(n) in 5042, 5041 and 5040.  So the search from above adds nothing in a run, and a replay
would cost a level's budget a game; the survivors carry the repair, at no work.

## The repair

The design, in [unsound.rs, "The repair"](https://github.com/bvchess/taxman/blob/56dcbdd/solver/frame/src/solver/unsound.rs)
and [unsound.md, "The repair"](https://github.com/bvchess/taxman/blob/56dcbdd/solver/docs/unsound.md#the-repair):

* **When.**  After each line a run records, it walks down the games below: for each, what survives on its board of each
  line within 8 games above that the walk has written (the line just recorded, and those it replaced), the heaviest.  If
  that scores more than the game's line, it proves the line short and replaces it, and the walk goes on from the new
  line too, until a game with none of its lines within 8 above.  A prime is played again from the repaired line below
  it; a trivial line is optimal and the table's lines are proven, so neither is weighed.  The run keeps the boards of its
  last 8 games for the walk and sets up again one it lacks.  There is no replay and no sweep.
* **What it changes above.**  Nothing the walk does not reach: the games above the line just recorded are not played
  yet.  A repeat of a repaired game plays its new promotions, and later games begin their `--back` trajectories from
  the new lines.
* **The file and the line.**  A replaced line is appended again, the line as played with the new moves, promotions and
  score, `at_ceiling` and `prev.short_by` of the new score, and `"repaired":{"from":5043,"was":8000285,"seconds":0.082}`.
  The last line of a game is the game's, and a later line must be a repair that scores more.  A run that opens the file
  takes the walk up where its last lines leave it, so a run cut short by a stop ends with the lines of one that ran on.
* **Effort and determinism.**  The repair runs no rounds, so the work of a level still bounds the run; a line still
  depends on nothing but the game, its start, the moves it starts from, the level, the seed and the options, never on
  the threads; and the rounds at E + 1 begin with those at E from the same moves.

The commit also adds `--above J` (0 by default, for measuring) and `survivor_scores`, the score of what survives of each
game a trajectory could begin from, in a searched line.

## The evidence

**In the known range.**  One chain of 4561-5060 at effort 4 on 4 threads, without and with the repair
([part3.py](part3.py), [differ.py](differ.py), [part3-out.txt](part3-out.txt)).  The streaks are written as in E2: the
game where each starts, its length, its shortfall at the first game, and the game that ended it.

| 4561-5060, effort 4 | games at opt(n) | streaks of short games |
|---|---|---|
| without | 479 of 500 (95.8%) | 4950 (18, 143; 4968), 5040 (3, 11; 5043) |
| with | 482 (96.4%) | 4950 (18, 143; 4968) |

The walk after 5043 replaced the lines of 5042, 5041 and 5040, each by opt(n), 11 points up; the streak of 4950 stays,
since the games above it stay short.  The other chains that finished show the same.  On 4861-5060 at effort 2 the
repair raises the games at opt(n) from 140 to 143 of 200 by the same three games (master's chain there is E2's line for
line, but for where 4961 took the line of 4960 from).  E2's chains of 4861-5060 at efforts 1 and 3, which stand in for
"without", hold 116 and 148 of 200, and the same chains with the repair 119 and 151.  E2's chain of 4761-4860 at effort
1 holds 93 of 100 and the same with the repair 95: 4842 proved 4841 short by 254, and the walk raised 4841 and 4840 by
254 each.  The
chains of 4861-5060 at effort 7 were stopped at 5009 and 5007, when the scope of the study was cut: on the 147 games
both reached, the repair found nothing, and the scores are the same.

**Past the table.**  5061-5260 at effort 4 on 4 threads, without and with the repair: the lines differ in score in two
games, 5104 and 5105, each 15 points higher with the repair, which the walk replaced after 5106 scored 15 above the
run's ceiling; the other 198 scores are the same.

**No line lower.**  In every pair of chains no game scored lower with the repair ([part3-out.txt](part3-out.txt)).  A
repaired line scores more than the line it replaces by construction, and the games after a repair, which begin
trajectories from the new lines, scored the same.

**The cost.**  The repair's walks took 23.1 s of the 9,523 s of the games of 4561-5060 (0.24%), 11.9 s of 5,912 s past
the table (0.20%), and 0.4 to 1% of the shorter chains of efforts 1 to 3; most of it is the boards set up again when a
walk goes past the 8 the run keeps.  The games' seconds for 100 games were 1,859 without and 1,905 with on 4561-5060, and 2,969 and
2,956 past the table, within the machine's noise.  The repair does no work; the chains' work differs by 0.05 to 1.1%,
up or down, only through the games after a repair.

## What is left for the full measurement

* **How often a game above escapes on its own,** at each level and past the table, on more seeds: the repair gains only
  where a searched game above a streak reaches a better set without the streak's help.
* **The chains of effort 7** run to their end, and the levels 5 and 6.
* **A game above that does not start from the short line,** such as a search from no seed, would break the inheritance
  that keeps the streak of 4950; with what survives of an optimal game above being opt(n) in most hard games, the walk
  could then repair the streak.  Not tried.

## Files

The commands ran in the study's scratch folder, with the binaries `taxman-50db88e` (master) and `taxman-b10` (this
study's, built before the commit's last edits, which renamed a function and changed comments and the help's spacing).
The lines are gzipped.

* [run_part1.py](run_part1.py), [games-part1.txt](games-part1.txt), [part1/](part1/): Part 1's arms, a game a command
  (`nice -n 19 python3 -I run_part1.py --bin TAXMAN --effort E --above J --games games-part1.txt --out part1/eE-aJ.jsonl
  --log part1/eE-aJ.log`), made by the study's first build, which had no repair and named `survivor_scores` `survivors`.
  The arm of effort 7 with J = 0 was stopped after 28 games, line for line those of R1's arm K25W4, which stands in for
  the other 45.  With this commit's build, give `--no-repair`: a run would weigh a game against the line of a game up to
  8 above it in the same file.
* [part1.py](part1.py) and [part1-out.txt](part1-out.txt) (`python3 -I part1.py part1`): the tables of Part 1, reading
  R1's lines from its folder.
* [projection.py](projection.py) and [projection-out.txt](projection-out.txt) (`python3 -I projection.py
  part1/e7-a4.jsonl.gz`): the greedy finish against the solver's survivors.
* [run_inrun.py](run_inrun.py), [show_inrun.py](show_inrun.py), [inrun/](inrun/): E2's short games played again from
  E2's lines, at effort 0 (`-x0`; `-x0t` with primes and repeats searched, `--tactic same_search=off --tactic
  prime_shortcut=off`) and at effort 4 with `--above 8` (`-x4`), by the first build; `python3 -I show_inrun.py
  ../the-datasheet-of-the-unsound-mode-2026-11/runs/e4-4861.jsonl.gz inrun/e4-4861-x0/inrun.jsonl.gz` prints one.
* [check/](check/): the first run of the repair, 5040-5045 at effort 4 into a file of E2's lines of 4961-5039 with
  `"repaired":null` added (`taxman-b10 solve 5040-5045 --unsound --effort 4 --back 8 --tilt 25 --widen 4 --seed 1
  --threads 4 --out e4-5040.jsonl`), and its output.
* [part3/](part3/): the chains, `m-` master's and `b-` this study's, named by effort and first game, each one command
  (`taxman solve LO-HI --unsound --effort E --back 8 --tilt 25 --widen 4 --seed 1 --threads T --out FILE`; the runs past
  the table give the defaults); the logs have the commands and times.  The chains of effort 7 ran on 6 threads, then 8
  from 09:01 and 12 from 10:13, both arms alike.
* [part3.py](part3.py), [differ.py](differ.py) and [part3-out.txt](part3-out.txt): the tables of the evidence, from
  `python3 -I part3.py WITHOUT WITH` and `python3 -I differ.py WITHOUT WITH` for each pair.
* [rebase/](rebase/) and [same.py](same.py): the runs of the commit rebased onto 954d664, on 32 threads with the
  defaults (`taxman solve LO-HI --unsound --effort E --seed 1 --threads 32 --out FILE`, the run of 4761-4860 with them
  named, `--back 8 --tilt 25 --widen 4`, and `--no-repair` for
  `post-e2-4561-norepair`, and the same command for 954d664's `master-e2-4561` and the build on 50db88e's `pre-e2-4561`
  on 4 threads), and `python3 -I same.py A B` for each pair in [rebase/same-out.txt](rebase/same-out.txt): no line
  differs but for the times, the threads, the build and the keys that 954d664 lacks.
