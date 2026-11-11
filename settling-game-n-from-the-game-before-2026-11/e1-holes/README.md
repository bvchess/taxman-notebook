# E1, the hole law

Run on batmobile on 2026-11-10, 21:35 to 22:20 PST, from the branch `holes-e1` of the research repository (never
pushed): the code is commit 57d7491, on top of master e36cd09, and the fingerprint example alone is its parent 943a945.
The branch's head, 997305b, only formats the example.  The binaries are here: `restricted` (the example, built from
57d7491), `taxman.holes-e1` (its `taxman`), and `setup_digest.base` and `setup_digest.new` (943a945 and 57d7491).

## The question

At each exchange step n of the list, the optimal set of game n is that of game n − 1 with x, the shadow of n, exchanged
for n.  The hole law says that the board n − 1 without x, Y = {1, …, n − 1} ∖ {x}, scores opt(n − 1) − x at best.  Each
x here is at most n − 1 and above (n − 1)/2, so it divides no number of the board: the recorded game of n − 1 without its
move x is a legal game on Y, and opt(Y) ≥ opt(n − 1) − x always.  The question is whether Y does better.

## The option

`examples/restricted.rs`, `solve N --holes Z,...`: game N on the board 1..=N without the holes, as an exact standalone
search (no moves of an earlier game, so no seed, no ceiling and no near-repeat cut; `--tactic prev_cap=off --tactic
near_repeat=off` were given as well).  `Tables::with_holes` takes the holes out of every list of maximal factors and
composites, so the frames follow the maximal-factor rule of the holes theorem (X9, docs/theory/exactness.md, "Boards
with holes"): a hole is never in the pot, never a move and never tax, and a move needs one of its maximal factors in the
pot.  Setup takes the numbers of Y above n/2 as its sources, makes a frame alone of a number up to n/2 that pays for no
source (one layer above it), gives an empty frame h to a layer of only closed frames between two with freedoms, and on a
board with holes orders the frames by layer.  The moves of the best promotion set are refereed on Y
(`game::replay_with_holes`) and must score ΣU\*(Y) + the promotion sum.  X9 needs no hypothesis on the holes, so no hole
set is refused but one with a number off the board or given twice.

What the answer is: ΣU\*(Y) + P\*, the score of a legal game of Y, so a lower bound on opt(Y), and opt(Y) itself exactly
when some best game of Y plays all of U\*(Y) (X9; the bottom-layers theorem F4 is not claimed on Y, so this is all of
U\*(Y), not only its layers 3 and up).  Setup cannot check that, so it is the one assumption of an equality; an excess
over opt(n − 1) − x needs no assumption, since the moves are a legal game.  On Y the maximal-factor rule and the
game's own rule (any proper divisor in the pot) can differ, but not here: x divides nothing on the board.

## The checks, before any measurement

Every comparison agreed; nothing was measured before they did.

* **Boards with holes, `restricted check-holes`** (check-holes-*.txt): every board n = 1 to 60 with no hole, with every
  single hole (1,830 boards), and with 520 random pairs and 515 random triples of holes, 2,925 boards in all.  On every
  one the frame model's answer equals (a) the heaviest L ⊆ Y ∩ {2, …, ⌊n/2⌋} with U\*(Y) ∪ L playable on Y, found by a
  walk over the playable sets with `playable::playable` on the tables of Y (X9's statement, which needs no U); (b) the
  best score on Y by exhaustive search with the maximal-factor rule (`brute::solve_by`), so U holds on all of them; (c)
  U\*(Y) made again by descending greedy over the sources of Y; and its moves are refereed, with no legal move left.  The
  60 boards with no hole score the built-in table's.  30 of the boards have an empty frame h.  On 371 of them the game's
  own rule (`brute::solve`) scores more than the maximal-factor rule: those are hole sets where a hole is a maximal
  factor, the case X9's rule is written for.
* **No holes, nothing changed**: the fingerprint of the setup of every board 1 to 10239 (`examples/setup_digest.rs`:
  the moves with no promotions, the frames' names, claims, moves and factors, the candidates, the problem's digest, and
  the moves the recorded promotions make, for the games of the table) is the same, byte for byte, from the build of
  943a945 (digest.base.txt) and of 57d7491 (digest.new.txt); `taxman regress --to 1000` matches the table on all 1,000
  games (regress-1-1000.txt); and `taxman verify-results results/optimal.jsonl.gz` accepts all 5,060 games, the repeats'
  problems set up again by the new build (verify-results.txt).

## The runs

`run-e1.sh`: each board on 16 threads at idle priority (`--background`), stopped at 30 minutes; none came near it.  The
lines are in e1.jsonl, the progress lines in e1-*.err, and the same solves with their moves in e1-show.jsonl.
e1-referee.txt replays every set by the plain rules of Taxman on Y with a separate Python referee (the same scores, no
legal move left) and lists how each differs from the recorded optimal set of n − 1.

| n | n − 1 | x | opt(n − 1) | opt(Y) | opt(n − 1) − x | difference | nodes | seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 741 | 740 | 374 | 172,899 | 172,767 | 172,525 | +242 | 24 | 0.03 |
| 1083 | 1082 | 578 | 369,966 | 369,726 | 369,388 | +338 | 161 | 0.09 |
| 1209 | 1208 | 638 | 460,433 | 460,252 | 459,795 | +457 | 4,502 | 0.14 |
| 1599 | 1598 | 814 | 805,436 | 805,304 | 804,622 | +682 | 17,091 | 0.42 |
| 1677 | 1676 | 902 | 885,956 | 885,868 | 885,054 | +814 | 25,840 | 0.72 |
| 1729 | 1728 | 935 | 941,678 | 941,348 | 940,743 | +605 | 119,648 | 1.45 |
| 1767 | 1766 | 986 | 981,744 | 981,540 | 980,758 | +782 | 15,319 | 0.48 |
| 1833 | 1832 | 946 | 1,055,687 | 1,055,643 | 1,054,741 | +902 | 108,266 | 1.24 |
| 2067 | 2066 | 1034 | 1,346,448 | 1,346,345 | 1,345,414 | +931 | 37,635 | 1.32 |
| 2139 | 2138 | 1102 | 1,442,915 | 1,442,764 | 1,441,813 | +951 | 68,464 | 1.57 |
| 2301 | 2300 | 1166 | 1,668,926 | 1,668,661 | 1,667,760 | +901 | 7,333,543 | 87.65 |

opt(Y) is the frame model's answer ΣU\*(Y) + P\*; seconds are wall time of setup and search together, and the search
of 2300 took 23 minutes of CPU.  Each search completed.

## The result

The hole law fails at all eleven games: Y scores more than opt(n − 1) − x, by 242 to 951.  The excesses are proven
without U, since each is a legal game on Y, refereed twice; given U on Y they are the exact excess, and without it the
true excess is at least as large.

How Y does better, against the recorded optimal set of n − 1 (e1-referee.txt): in six games Y plays that set with x
exchanged for one smaller number y, a promotion, and the excess is y: 1082 plays 338 for 578, 1598 plays 682 for 814,
1676 plays 814 for 902, 1728 plays 605 for 935, 1766 plays 782 for 986, 1832 plays 902 for 946.  740 drops 374 and 44
and plays 286 (242 = 286 − 44).  The other four change more: 1208 exchanges five numbers (312, 375, 414, 495, 506 for
351, 372, 460, 462, 638), 2066 five, 2138 three and 2300 thirteen.
