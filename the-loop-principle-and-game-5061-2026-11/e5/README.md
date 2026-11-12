# E5: the parity bound's own cascade

Experiment E5 of the loops study (`../study-report.md`, Section 8), run 2026-11-11 from 06:20 to 07:20 PST.  Words are
the study's (Section 1): P the largest prime of n, c = n/P, the cell (k, j) = k·P_j; D and A the recorded change from
n − 1 to n (the moves of the committed optimal set of n − 1 that the set of n gives up, and the moves it takes up
besides n); rise = δ − δ_PB = gap(n) − gap(n − 1).

## What was run

* **The parity sets.**  `paritydump` (`solver/noframe/examples/paritydump.rs` on the research branch `loops-e5`,
  commit 49f6788, never merged) uses the prover's `Meet` (weighted matroid intersection over the parity vectors, W1)
  on boards n − 1 and n for the eleven games.  For each board it prints the heaviest set that `Meet` finds, with its
  weight split (`split`: w1 of each free candidate, w2 = s − w1; the split proves the value), and the heaviest set
  nearest the recorded optimal set (weights M·s ± 1).  On board n it also prints the heaviest set nearest that set of
  n − 1: the parity bound's own change, as small as it can be.  It then applies the game's change to a heaviest set of
  n − 1 (D forced, A barred) and asks whether the result, with n, is independent on board n and what it weighs.
  Finally, for each cell of D, A and n on each board, it asks whether some heaviest set holds the cell and whether
  some heaviest set avoids it.  Output: `paritydump.jsonl` (110 lines, 1 m 27 s on one thread).

      nice -n 19 .../release/examples/paritydump 2512 1168 2224 2768 3184 4432 688 1328 1460 4975 4893 > e5/paritydump.jsonl

* **Cell form.**  `analyze.py` → `analyze_out.txt`: both changes in cells, the comparison on the window (columns
  0..3, all rows) and on the whole board, the game's change applied, and the *defect* of each board.  The defect is
  the pair (parity only, recorded only) between the recorded set and the nearest heaviest set; PB − opt is its
  difference in sums.
* **The configurations.**  `cores.py` → `cores_out.txt` (helpers in `oddcore.py`): the circuits behind the exchanges
  where the two changes part, and probes that apply those exchanges to the recorded sets.  A probe reports whether
  the result is independent at both parities and an inclusion-minimal core of its own instance.

All run as `nice -n 19 python3 -I e5/SCRIPT` from the loops folder; copies of the three scripts are in commit 9af61b3
of the branch `loops-e5`, under `lab/work/loops/e5/`.  The PB values agree with
`../../succession/settle.csv` (its `bound` column) at all 22 boards.  `test.jsonl` is an early trial on 1168 and 688,
superseded by `paritydump.jsonl`.

## Results

| n | c·P | depth | rise | parity change = game's: window / whole board | forced at n − 1 and n | defect, n − 1 → n |
|---|---|---|---|---|---|---|
| 1168 | 16·73 | 1 | 0 | yes / yes | yes | the same 3-for-3 exchange (77) |
| 2224 | 16·139 | 2 | 0 | yes / yes | yes | the same 11 for 11 (754) |
| 2768 | 16·173 | 2 | 0 | yes / yes | yes | the same 8 for 8 (867) |
| 3184 | 16·199 | 3 | 0 | yes / yes | yes | the same 11 for 11 (1117) |
| 4432 | 16·277 | 3 | 0 | yes / yes | yes | the same 15 for 15 (2321) |
| 4975 | 25·199 | 2 | 0 | yes / yes | yes | the same 24 for 24 (2342) |
| 4893 | 21·233 | 3 | 0 | yes / yes | yes | the same 20 for 20 (2043) |
| 2512 | 16·157 | 2 | +98 | yes / no: also 833 → 931 | yes | gains 931 for 833 (813 → 911) |
| 688 | 16·43 | 1 | −2 | yes / no | 44 in no heaviest set of 687 | loses (68, 266, 275) for (44, 238, 325) (55 → 53) |
| 1328 | 16·83 | 1 | −32 | yes / no | 44 in no heaviest set of 1327 | loses 76 for 44 (315 → 283) |
| 1460 | 20·73 | 1 | −39 | no / no | 316 in none at 1459; 710 in all, 426 in none at 1460 | loses 316, gains 710 for 426 and 639 (426 → 387) |

"Forced" means that every heaviest set of n − 1 holds D and avoids A, and every heaviest set of n holds A and n and
avoids D.  So the agreement does not depend on which heaviest sets are taken.

**The clean games.**  At all seven games with rise 0 (16P at depths 1, 2, 2, 3 and 3; 25P at depth 2; 21P at depth
3), the parity bound's change is the game's (D, A) cell for cell, on the whole board.  For 16P that is
(8,1) + (6,2) + (4,3) out and (6,1) + (4,2) in; at 4975 (9,0) + (10,1) out and (10,0) in; at 4893 (10,0) out and
(9,0) in.  The game's change applied to a heaviest set of n − 1 gives a heaviest set of n, and the defect of n − 1
passes to n unchanged, member for member.  The kill criterion of E5 (the parity set differing from the game's on the
window while the values agree) is met at none of them.

**2512, rise +98.**  On the window the parity bound's change is the 16P cascade, forced.  The 98 is one more exchange
off the window, 833 = 7²·17 out and 931 = 7²·19 in, which the cascade opens.  In the heaviest set of 2511 (every
one holds D), 931 has a circuit at parity 1 of 55 members, and the circuit passes through column 3's cells
(4,3) = 556, (9,3) = 1251, (12,3) = 1668 and (18,3) = 2502.  The last is the row that the unclean column holds,
18·139 ≤ 2512; row 17 is not in the circuit.  So 931 cannot replace 833 there.  On 2512 the cascade drops (4,3), and
931 becomes independent at parity 1.  At parity 0 its circuit is {833, 1309, 1463, 2057, 2299}, so it replaces 833.
In the game the exchange is unplayable: applied to the recorded set of 2511 or of 2512 it is independent at both
parities and closes an odd core of 14 members.  Those members are rows 45, 50, 63, 70, 75, 98 and 105 times the
primes 19 and 23 (855, 950, 1035, 1150, 1197, 1330, 1425, 1449, 1610, 1725, 1862, 1995, 2254, 2415), a two-column
structure with the rows as shared hubs.  So the study's expected answer is half right.  Column 3's unclean row 18
takes part, as part of the circuit that blocks the exchange at 2511, not as the odd core.  The odd core lies far from
the window and exists in the recorded sets of both 2511 and 2512; what n's arrival changes is the circuit.

**688, 1328, 1460, the negative rises.**  At each, the defect of n − 1 holds the game's holder of hub 4 on the
recorded side: 44 = 4·11 at 687 and 1327, and 316 = (4,−1) at 1459.  No heaviest set of n − 1 holds it.  Its
circuit at parity 1 in the heaviest set of n − 1 runs:

* at 687, through column 3's rows 9, 10, 12, 18 and 20 (31·k), two of them rows that only the unclean column holds
  (it holds rows up to 22);
* at 1327, through (6,2) = 438, (9,2) = 657 and (18,2) = 1314, the last a row that only the unclean column 2 holds;
* at 1459, through column 1's rows 9, 10, 12, 18 and 20 (column 1 is clean; these are the cells the cascade moves)
  and column −1's rows 9 and 12.

The parity bound holds a heavier configuration through hub 4 instead:

* At 687, the rotation 44 → 68 = (4,7), 238 → 266 = (14,6) and 325 → 275 = (25,9), worth +2.  Of its seven parts
  only the whole rotation is both independent and a gain.  Applied to the recorded set of 687, it closes an odd core
  of 23 members (rows 18 to 125 in columns 6, 8, 9, 10 and 11).
* At 1327, 76 = 4·19 for 44 within the exchange (44, 475, 546) → (76, 462, 575), worth 48.
* At 1459, (459, 567) for (316, 588), worth 122.

The cascade of n gives up the holder of hub 4 in each model: the game gives up 44, 44 and 316; the parity bound 68
and 76, and at 1460 (9,1).  That removes the hub-4 part of the defect:

* at 688, all 2 of it (without 68 the rest of the rotation is worth −22, and the parity set of 688 returns to the
  game's cells);
* at 1328, 32 = 76 − 44 of the 48; the part (475, 546) → (462, 575), worth 16, survives in the defect of 1328;
* at 1460, the game's change (−316 − 710 + 426) against the parity bound's (−639) moves the defect by −39.

So the "odd core of n − 1 that the step dissolves" is in each case the configuration that lets the parity bound price
hub 4 above any game of n − 1.  It goes when the cascade's last rung gives hub 4's holder up.

## What it decides

By the study's criteria (Section 8, E5):

* **At the clean games the parity bound's augmenting path is the game's cascade, cell for cell, and forced.**  On the
  whole board, not only the window; it holds at the 25P and 21P games as well as 16P.  So a proof of P1 can be the
  family proof written twice (Section 4.4), and the kill criterion does not fire.
* **2512's extra 98** is an exchange outside the window (833 → 931), unplayable in the game through a 14-member odd
  core on the rows 45..105 of the columns of 19 and 23.  The cascade's last loss, (4,3), opens it by breaking a
  parity-1 circuit that runs through column 3's rows 4, 9, 12 and 18, the last of them the unclean row.  So
  cleanliness to depth 3 matters here as the study predicted, but through a circuit, not through an odd core inside
  the window.
* **The negative rises** dissolve the hub-4 part of the defect of n − 1.  The parity bound held hub 4 with a heavier
  cell than any game can (blocked in the game by a circuit through an unclean column), and the cascade's last rung
  gives that holder up in both models.
* **Common to the four non-zero rises:** a parity circuit through cells of the cascade that the step opens or
  closes.  At 2512, 688 and 1328 it also runs through rows that only an unclean column holds (row 18 of column 3 or 2;
  rows 18 and 20 of column 3 at 688).  At 1460 it runs through the clean column 1 and column −1, and the step's own
  change differs from the game's on the window.
