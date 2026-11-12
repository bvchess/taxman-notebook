# Move counts past 5060 (2026-11)

Part of the [lab notebook](../README.md).

Started 2026-11-10.  Concluded 2026-11-10.

**Question.**  The owner asked whether mining could use the move count.  The optimal game usually plays the most moves a
game can, so does a best-known game past 5060 with fewer moves show that its score falls short, and point the miner at
it?

**Answer.**  No.  2,520 of the 4,940 best-known games past 5060 play fewer moves than ν(n), the matching bound on the
most moves, but ν(n) overshoots the most moves ℓ(n) from game 5136 on.  At both ends of all 20 runs of such games the
best-known game plays exactly ℓ(n) moves, proved for 40 games by a unit-weight parity bound that this entry adds to the
prover's `moves` tool.  Move counts give no sign of short scores past 5060.

## Method

*The words.*  A *best-known* score is the highest found for a game that no exact search has proved optimal, and the
*miner* is the unsound mode's root-first search for scores above the best-known ones.  The *moves* of a game are the
numbers it plays.  The *maximal factors* of a number are its quotients by its primes, and 12 has the maximal factors 6
and 4, with 1 the only maximal factor of a prime.  ν(n) is the matching number of the graph that joins each number of 2
to n to its maximal factors, and ℓ(n) is the most moves of a game of n.  Then ℓ(n) ≤ ν(n), so a legal game with ν(n)
moves is a longest game.  Also ℓ(n − 1) ≤ ℓ(n) ≤ ℓ(n − 1) + 1, with ℓ(n) = ℓ(n − 1) for a prime n ≥ 3 ([the length lemma
(Q3)](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/uniqueness-and-longest-games.md#the-length-lemma)).  A
game's *shortfall* is ν(n) less the moves of its game.  Every game from 836 to 4949 of the chain has ν(n) moves, and
before that ν(n) = ℓ(n) + 1 only at 51, 182 and 183 ([how far an optimal game falls short of a longest
one](../how-far-an-optimal-game-falls-short-of-a-longest-one-2026-10/README.md)).

*The first check, `short.py`.*  It computes ν(n) for n = 2 to 10000, one augmenting-path search for each new vertex, and
checks ν(21) = 9, ν(51) = 23 and ν(833) = 363, ν(n) against the prover's `nu` field for 2 to 4949, and the move count of
each proven game 836 to 5060 against ν(n).  For n = 5061 to 10000 it takes the best-known line, the one of the highest
score in the miner's file `best-known.jsonl` and the last if tied, and compares its moves with ν(n).  The file was read
at 15:42 Pacific time on 2026-11-10.

*The second check, the prover's `moves`.*  The tool settles ℓ(n) game by game in increasing order, between the moves of
the recorded game, which replay by the rules and give a lower bound, and the least of ν(n) and what ℓ(n − 1) allows,
which is ℓ(n − 1) + 1, or ℓ(n − 1) for a prime n ≥ 3.  Where they leave a gap it runs a branch and bound under unit
weights.  That search did not decide 5136 in 100,001 nodes (50 s) or 9456 in 20,001 nodes (32 s), and five searches of
5136, 5232, 7824, 8688 and 9456 were stopped by a signal after 346 to 660 s, undecided.

*The change, commit c9483b0.*  A playable set is independent at both parities, so ℓ(n) is at most the largest set of the
numbers 2 to n that is independent at both ([the parity bound
(W1)](https://github.com/bvchess/taxman/blob/aeffc29/docs/theory/parity-bound.md#the-parity-bound), here with every
weight 1).  The prover's `moves` now takes the least of ν(n), what ℓ(n − 1) allows and this bound, and sets the `how`
field of its line to `parity` when the recorded moves meet the bound and to `predecessor` when they meet what the game
before allows.  The line gains a `parity` field.  A test checks that at 51, 182 and 183, where ν(n) = ℓ(n) + 1, the
bound is ℓ(n).  The bound costs 3.7 to 19.3 s a game on one thread, with no search.

*The runs.*  `extract.py` writes the best-known lines of the games to check, and `moves` reads them.  The first run took
the first game of five runs of short games, 5136, 5232, 7824, 8688 and 9456, and the games just outside the first block,
5135 and 5562, as controls.  The second took the games at both ends of every run of equal shortfall.

## Results

### Half of the best-known games past 5060 are short of ν(n)

* **2,520 of the 4,940 games have fewer moves than ν(n)**, 1,944 by 1 and 576 by 2, and none has more.  The 2,420 others
  have ν(n) moves.  Every best-known line has distinct moves in 2 to n.
* **They lie in 8 blocks of consecutive games:** 5136 to 5561, 6672 to 6684, 6690 to 6857, 7248 to 7397, 7824 to 8153,
  8304 to 8477, 8592 to 9017 and 9168 to 10000.  The games from 5061 to 5135 and from 5562 to 6671 have ν(n) moves.
* **No line of any score of a short game has ν(n) moves**, in the whole of `best-known.jsonl`.  The miner has played 441
  of the 2,520 short games and 156 games with ν(n) moves.  It raised the score of 26 short games, and of 3 others, and
  none of them reached ν(n) moves.

Two readings fit.  Either the search misses longest games, and these 2,520 games are probably short, far more than the
113 short games that the model of which best-known scores are optimal expects, or ν(n) overshoots ℓ(n) there.

### ν(n) overshoots ℓ(n): the best-known game is a longest game

| n | ν(n) | moves | parity bound | ℓ(n) | how |
|---|---|---|---|---|---|
| 5135 | 2,224 | 2,224 | | 2,224 | the matching (control) |
| 5136 | 2,225 | 2,224 | 2,224 | 2,224 | the parity bound |
| 5232 | 2,269 | 2,267 | 2,267 | 2,267 | the parity bound |
| 5562 | 2,407 | 2,407 | | 2,407 | the matching (control) |
| 7824 | 3,385 | 3,384 | 3,384 | 3,384 | the parity bound |
| 8688 | 3,761 | 3,759 | 3,759 | 3,759 | the parity bound |
| 9456 | 4,087 | 4,085 | 4,085 | 4,085 | the parity bound |

* **Every end of every run is settled.**  The 20 maximal runs of games of the same shortfall (`blocks.py` lists them)
  have 40 end games.  At each the best-known game has ℓ(n) moves, 34 by the parity bound and 6 by the game before, where
  the recorded moves are ℓ(n − 1) + 1 and ℓ(n − 1) is settled.  The first game of a block and the one before it show the
  change: 5135 plays ν(n) moves and 5136 plays one fewer, which is all it can.
* **So the shortfall is ν(n) overshooting, not shortness.**  The best-known game plays the most moves a game can at all
  40 games.  The 2,480 games between the ends are not proved.
* **The first overshoot since 183 is 5136.**  ℓ(n) = ν(n) for 184 to 5135.

### The overshoot follows a rule on primes, not proved

Let c(n) be the number of primes p with 48 ≤ ⌊n/p⌋ ≤ 53.  The shortfall equals the larger of c(n) − 3 and 0 at 4,821 of
the 4,940 games (`blocks.py`).  Where c(n) is at least 4 a block lies, and its first game is 48p for a prime p and its
last 54q − 1 for a prime q.

| first game | last game | p of the first, 48p | q of the last, 54q − 1 |
|---|---|---|---|
| 5136 | 5561 | 107 | 103 |
| 6672 | 6857 | 139 | 127 |
| 7248 | 7397 | 151 | 137 |
| 7824 | 8153 | 163 | 151 |
| 8304 | 8477 | 173 | 157 |
| 8592 | 9017 | 179 | 167 |
| 9168 | 10000 | 191 | cut off by the top of the range |

* **The rule fails at 119 games, in two places.**  At 6685 to 6689 the best-known game plays ν(n) moves where the rule
  says 1 short, and at 9552 to 9665 it plays 2 short where the rule says 3.  A legal game cannot play more than ℓ(n), so
  the rule is not the overshoot there.  No game falls short by more than the rule says.
* **The rule says nothing of 51, 182 and 183.**

## Limits

* **40 games are proved, the ends of the runs.**  The best-known games between them play ν(n) less the shortfall of
  their run, and `moves` has not run on them.  It costs 3.7 to 19.3 s a game, about 9 CPU-hours for the 2,480 by
  interpolating the times measured.
* **The rule on primes is a pattern.**  It matches 4,821 of 4,940 games and is not proved.
* **The best-known file changes** as the miner finds higher scores, and the lines read are those of 15:42 on 2026-11-10.
  A later line of a game may have other moves, and a line cannot have more than ℓ(n).
* **The question is of move counts alone.**  Whether the best-known scores are optimal is not answered here.

## Decision

The miner does not use move counts, since the best-known game plays the most moves it can at every game checked.  A
best-known game with fewer moves than the proved ℓ(n) would have been a sign of a score below opt(n), and none of the 40
is.

The change to the prover's `moves` is on the branch `moves-check` of the main repository, one commit (c9483b0) on
master's ba59242, not merged.  Whether to harvest it onto master is under consideration.  The commit is kept as a patch.

What would reopen it:

* a best-known game with fewer moves than the ℓ(n) that `moves` proves, which would be a short game;
* a run of `moves` on the 2,480 games between the ends, if the shortfall of the interior games should be proved;
* a proof of the rule on primes, which would give ℓ(n) with no run.

## Files

The checks were made in the scratch folder `lab/work/moves/`, whose files these are, but for the files below that were
not copied.  The paths in the scripts are those of the scratch folder.

| file | what |
|---|---|
| [short.py](short.py) | the first check, `nice -n 19 python3 -I short.py`, standard library only, 28 s; it reads `best-known.jsonl`, the committed results, the prover's data and the miner's ledger, and writes `nu.csv` and `short.csv`; its output is `report.txt` |
| [report.txt](report.txt) | the script's checks, and a line for each of the 2,520 short games |
| [nu.csv](nu.csv) | n, ν(n), moves, score and shortfall for every n of 5061 to 10000 |
| [short.csv](short.csv) | the 2,520 short games with the lines of each in `best-known.jsonl`, the most moves of any of them, and the miner's rows for the game and the rows that raised its score |
| [blocks.py](blocks.py) | `python3 -I blocks.py > blocks-output.txt`: the 20 runs, whether `moves` settled each end, the rule on primes and the blocks; it reads `nu.csv` and `check/` |
| [blocks-output.txt](blocks-output.txt) | its output, written when this entry was made |
| [check/extract.py](check/extract.py) | `python3 -I extract.py OUT.jsonl N...` writes the best-known lines of the games to `OUT.jsonl` for `moves --results` |
| [check/best7.jsonl](check/best7.jsonl), [check/ends.jsonl](check/ends.jsonl) | those lines for the 7 first games and the 35 other ends |
| [check/tool7.jsonl](check/tool7.jsonl), [check/ends-a.jsonl](check/ends-a.jsonl), `ends-b`, `ends-c`, `ends-d` | what `moves` printed for them: n, the recorded moves, ν(n), the parity bound, ℓ(n) and how |
| [check/calib.jsonl](check/calib.jsonl), [check/calib9456.jsonl](check/calib9456.jsonl), [check/control5562.jsonl](check/control5562.jsonl) | the first runs of the tool, before the parity bound: 5135 and 5136 and 9456 with a node budget, and the control 5562 |
| [check/run5.sh](check/run5.sh) and `check/search*.log` | the five searches without the parity bound, each stopped by a signal |
| [patches/](patches/) | the commit c9483b0 as a `git am` patch, made with `git format-patch -1 c9483b0` |

Not kept here are the prover's build of the branch, `lab/work/cargo-target-moves/release/moves`, the miner's file
`best-known.jsonl`, which grows as the miner runs, and its ledger.  The best-known lines of the games checked are in
`check/`.  The command lines of the runs of `tool7.jsonl` and `ends-*.jsonl` were not recorded; `run5.sh` shows the
form, `moves --list N --results FILE --out FILE`, with the node budget that those runs did not need.

## Commits

* c9483b0 (branch `moves-check` of the main repository, never pushed): the prover's `moves` takes the unit-weight parity
  bound, in `solver/noframe/src/moves.rs` and `solver/noframe/src/bin/moves.rs`.  Its parent is
  [ba59242](https://github.com/bvchess/taxman/commit/ba59242), which differs from aeffc29 by one document.
* The commit that adds this entry and its row in [the register's file of the theory and its
  proofs](../register/theory-and-proofs.md).
