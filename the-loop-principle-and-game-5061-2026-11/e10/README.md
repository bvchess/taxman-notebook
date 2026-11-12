# E10: the parity bound's change at the 21P steps 5061, 5019, 3297 and 3507

Experiment E10 of the loops study (`../study-report.md`, Sections 10.2, 10.5 and 14), run 2026-11-11 from 08:15 to
08:40 PST.  Words are E5's (`../e5/README.md`): D and A the recorded change from n − 1 to n; I(n − 1) the heaviest
set of n − 1 independent at both parities nearest the recorded set; I(n) the heaviest set of n nearest I(n − 1), the
parity bound's own change; W(n − 1) the heaviest set of n − 1 holding D and avoiding A; J = W(n − 1) − D + A + n;
K(n) the heaviest set of n nearest J.  The *defect* of a board is the pair (parity only, recorded only) between its
recorded set and its nearest heaviest set.  A number is written k·p, p its largest prime.

## What was run

* `paritydump --best FILE 5061 5019 3297 3507` (`solver/noframe/examples/paritydump.rs`, branch `loops-e5`, commit
  5c0a290).  The recorded sets: the committed chain up to 5060; 5061 the highest score of
  `/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl` (one line, 8,057,936, method search).  Output:
  `paritydump.jsonl`, 40 lines, with the weight split of each plain set; about 4 minutes on one thread.
* `analyze.py` → `analyze_out.txt`: the two changes, the forced cells, the game's change applied, the defects, the
  circuits of the cells K − J, and the probe (the extra J → K applied to the recorded set of n, its minimal core).
* `probe.py` → `probe_out.txt`: the circuits of the parity bound's added cell, the whole residual of the probe set by
  column with each factor's listing count, and the one-cell reading.

Scripts run as `nice -n 19 python3 -I e10/SCRIPT` from the loops folder; copies are in the same commit.

## Results

| n | δ | δ_PB | rise | the parity bound's own change | the game's change |
|---|---|---|---|---|---|
| 5019 = 21·239 | 492 | 492 | 0 | −6·239 + 6·157 | the same, forced |
| 3297 = 21·157 | 402 | 166 | 236 | −6·157 + 8·97 | −6P, then 3 cells out and 4 in, in the columns of 97, 101, 103 |
| 3507 = 21·167 | 393 | 178 | 215 | −6·167 + 8·103 | −6P, then 4 out and 5 in, in 103, 107, 109, 113 |
| 5061 = 21·241 | 746 | 254 | 492 | −6·241 + 8·149 | −6P, then 4 out and 5 in, in 151, 157, 163 (best-known) |

**5019** (rise 0): the parity bound's change is the game's, forced (every heaviest set of 5018 holds 6·239 and avoids
6·157, every heaviest set of 5019 the reverse), and the defect passes from 5018 to 5019 unchanged.  Both models put
6·157 = 942 back for 6P.

**The 492 at 5061, named.**  The parity bound's own change is one exchange: 6P = 1446 out, 8·149 = 1192 in, so
δ_PB = 1446 − 1192 = 254.  The game recovers 700 (its five-cell shuffle) where the parity bound recovers 1192, and
492 = 1192 − 700.  Three things hold the same way at 3297 and 3507, the proven precedents, with q = 97 and 103:

1. **What keeps 8q out at n − 1.**  In I(n − 1), 8q has a circuit at parity 1 of 21 members in five columns, of the
   same shape at all three games:

   | rows | 5061 | 3297 | 3507 |
   |---|---|---|---|
   | 6, 9, 18 | 241 (column 0) | 157 | 167 |
   | 9, 10, 12, 18, 20 | 251 (column −1) | 163 | 173 |
   | 15, 18, 20, 27, 30 | 149 (the column of q) | 97 | 103 |
   | 10, 15, 18, 27, 30 | 163 | 107 | 109 |
   | 6, 8, 12 | 421 (12·421 holds the hub 12) | 271 | 283 |

   6P is in the circuit; its departure breaks the circuit, and 8q enters (no circuit at either parity in I(n) less
   8q).  The column-0 cells are 6P, 9P and 18P, the cells of regime (ii) (18P paying with the hub 18).
2. **What the game cannot do.**  The parity bound's extra beyond the game's change, J → K, is worth 576 at 5061 (−6·157,
   −9·163, −14·163 + 8·149, 10·163, 15·163), 244 at 3297 and 223 at 3507.  The rise is that, less what the defect of
   n − 1 already held in the same cells: 84 at 5061 (the heaviest sets of 5060 already hold 12·151 and 16·157 and
   avoid 10·157, 12·157 and 16·151, the cells the best-known game moves to at 5061), and 8 at 3297 and at 3507.
   Applied to the recorded set of n, the extra is independent at both parities and unplayable, and the residual of
   the result has 19 members of the same shape at all three games:

   | rows | 5061 | 3297 | 3507 |
   |---|---|---|---|
   | 8 (the far holder of hub 8) | 631 | 409 | 433 |
   | 8, 12 | 421 | 271 | 283 |
   | 12, 18, 20 (column −1) | 251 | 163 | 173 |
   | 18, 27, 30 | 163 | 103 | 109 |
   | 12, 18, 20, 27, 30 | 151 | 101 | 107 |
   | 8, 18, 20, 27, 30 (the column of q) | 149 | 97 | 103 |

   Its members list the hubs 8, 12, 20, 27 and 30 three times each and the hub 18 four times; every column factor
   they list is listed two or three times.  The residual is a union of odd cores (the set is independent), so no game
   holds it.  A minimal core inside it has 11 members at 5061 and 12 at 3297 and 3507.
3. **The one-cell reading fails**, as Section 10.2 found for other cells: the recorded set plus 8q is dependent (at
   parity 1 at 5061, parity 0 at 3297 and 3507).  The parity bound's extra is an exchange of several cells around
   8q, not a cell added.

So the parity bound's extra 492 is a hub-8 cell of the far region, 8·149, entering when 6P leaves.  It enters
through the odd core above, in which hubs 8, 12, 18, 20, 27 and 30 are each listed three or four times, a GF(2)
combination that no payment scheme realizes.  The columns are 149, 151, 163, 251 (column −1), 421 and 631, not 157
or 241.  The configuration matches 3297's and 3507's column for column and row for row, and their rises are proven.

**The forced cells at 5061.**  Every heaviest set of 5060 holds 6P and 15·163, and 12·151 and 16·157 (which the
best-known game adds at 5061); none holds 10·157, 12·157 or 16·151 (which it drops) or 6·157, 9·163, 14·163 (which
it adds).  Every heaviest set of 5061 holds 5061, 15·163, 12·151 and 16·157 and none holds 6P.  So the parity bound
needs neither 6·157 nor the column-163 cells the best-known game takes, and the two models part on exactly the cells
listed in item 2.

## What it decides

By the study's criteria (Sections 10.2 and 14, E10):

* **The parity bound's change at 5061 is a far-region odd core, not a playable recovery.**  Applied to the best-known
  set of 5061 it closes an odd core, so it names no better game.
* **Its shape is the proven precedents' exactly.**  The circuit that holds 8q back at n − 1 (21 members) and the odd
  core that the extra closes in the recorded set of n (19 members) are, column for column and row for row, those of
  3297 and 3507, whose rises are proven.  So 5061 is the precedents' case.  That is evidence for the genuine reading,
  not a proof: another game of 5061 might still recover more than 700 without this core.  E11 (the region solve over
  the columns this names, 149, 151, 157, 163, 241, 251, 421, 631) is the test.
* **5019's step** is the clean case of the same regime: one exchange, the same in both models and forced.
