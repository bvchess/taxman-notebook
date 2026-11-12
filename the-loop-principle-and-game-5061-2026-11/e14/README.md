# E14 extended, the seal

Run on batmobile on 2026-11-11, 08:54 to 09:20 PST, from the branch `loops-e6` of the research repository (never
pushed).  The parity sets of 5060 and 5061 come from `paritydump` (`solver/noframe/examples/paritydump.rs`, E5's tool,
cherry-picked from the branch `loops-e5` as 7ec482e and a6140fc), with commit b0d765a, which adds `--cells` and
`--threads` to its forced check.  The binary here was built from b0d765a.  The 16P games use E5's output
(`../e5/paritydump.jsonl`).  The analysis is `seal.py` (`nice -n 19 python3 -I e14/seal.py` from the loops folder).

## The question

The study's E14 (Section 14) and the seal of its local proof of 5061 (Sections 10.4 part 3 and 10.5 item 4).

* **Section 14:** at the clean 16P games of E5, for every element outside the window, whether its circuit in a
  heaviest set of n − 1 passes through a ladder cell ((8, 1), (6, 1), (6, 2), (4, 2), (4, 3)); at 2512 the same for
  column 3's rows.  The prediction: the sealing lemma holds where the window is clean to depth 3 and fails at 2512
  only through row 18.
* **Section 10.4, the seal per hub at 5061:** for the hubs 12, 16, 18, 27, 29, 30, 32 (and E10's 8 and 20), their
  holders in every heaviest set of 5060 and 5061, forced or not, and whether a circuit of a region cell passes through
  them; "the holder of hub h in every optimal set is the heaviest h-cell that needs it, and the region's cells are
  lighter".

## What was run

* `paritydump --best FILE --cells (509 cells) --threads 16 5061` under `chrt --idle 0` (12 minutes): the heaviest sets
  of 5060 and 5061 nearest the recorded sets (the committed 5060, the best-known 5061) and E10's other lines, and for
  each cell h·p of the nine hubs (p a prime above h's largest prime, h·p ≤ 5061; 509 cells) on each board, whether
  some heaviest set holds it and whether some avoids it.  Output `paritydump-5061.jsonl`; the cells are `hubcells.txt`.
* `seal.py` → `seal_out.txt`: the circuits (the members of a heaviest set whose parity vectors sum to an outside
  element's, W1), with one GF(2) basis per board and parity; hub holders in peel's payment scheme of the recorded sets
  (the study's `study/hubs.py`).  Part A: the 16P games; Part A2: what the cascade frees; Part B: the hubs at 5061;
  Part B2: what the change 5060 → 5061 frees.

## The results

**Part A, the literal test: it fails at every game, clean or not, and is the wrong test.**  At all six games many
elements outside the window have a circuit through a ladder cell (heavy elements, at least as heavy as 4P₃: 88 to 225
a game; light ones, the hubs and small numbers: 85 to 230).  The ladder cells are the window's hub holders: (8, 1)
with (16, 1) carries the hub coordinate 16, (6, 2) the hub 6, (4, 3) the hub 4, so every element whose combination
needs one of those coordinates runs through them, as do the hubs' own unit vectors (4's circuit holds (4, 3), 16's
(8, 1)).  The cascade moves each hub one column up and keeps those spans, so a circuit through a ladder cell is no
exchange the cascade opens.

**Part A2, the operative test: what the cascade frees.**  An element outside the window and outside both heaviest sets
is *freed* at a parity when it has a circuit in the heaviest set of n − 1 (nearest the committed set) and none in the
heaviest set of n nearest it (E5's `near_prev`, the parity bound's own change).

| n | clean to | column 3 holds row 18 | parity change outside the window | freed elements | the window cells their circuits meet |
|---:|---:|---|---|---:|---|
| 1168 = 16·73 | 1 | yes (18·61 = 1098) | none | 31, at parity 1 | (4,3), (9,3), (12,3), (18,3) |
| 2224 = 16·139 | 2 | no (rows to 17) | none | 0 | |
| 2768 = 16·173 | 2 | no (rows to 17) | none | 0 | |
| 3184 = 16·199 | 3 | no | none | 0 | |
| 4432 = 16·277 | 3 | no | none | 0 | |
| 2512 = 16·157 | 2 | yes (18·139 = 2502) | 931 in, 833 out | 12, at parity 1 | (4,3), (9,3), (12,3), (18,3), or none |

At every game the near_game and plain heaviest sets of n − 1 are the same set.

**Part B, the hubs at 5061.**

| hub | game holder, 5060 | game holder, 5061 | the holder is the heaviest hub cell in the set | hub cells in every heaviest set (5060; 5061) | free |
|---:|---|---|---|---|---:|
| 8 | 5048 = 8·631 | 5048 | yes | 51; 52 (1192 = 8·149 added) | 0 |
| 12 | 5052 = 12·421 | 5052 | yes | 38; 38 | 0 |
| 16 | 5008 = 16·313 | 5008 | yes | 29; 29 | 0 |
| 18 | 4338 = 18·241 | 2826 = 18·157 | no: 5058, 4986, 4878, 4842, 4734, 4626 pay otherwise | 36; 36 | 0 |
| 20 | 5020 = 20·251 | 5020 | yes | 28; 28 | 0 |
| 27 | 4239 = 27·157 | 4401 = 27·163 | no: 4887, 4833, 4671, 4509 (, 4401) | 21; 21 | 0 |
| 29 | 4727 = 29·163 | 4727 | no: 5017, 4843 | 3; 3 | 0 |
| 30 | 4710 = 30·157 | 4530 = 30·151 | no: 5010, 4890 (, 4710) | 21; 21 | 0 |
| 32 | 4832 = 32·151 | 5024 = 32·157 | at 5061 yes, at 5060 no: 5024 | 16; 16 | 0 |

*No hub cell is free*: every cell of the nine hubs is in every heaviest set of 5060 and 5061 or in none, so the
heaviest sets agree on the hub cells whichever is taken.  The holders of the hubs 8, 12, 16 and 20 (8·631, 12·421,
16·313, 20·251, all sources) are the heaviest cells of their hubs in both games, in every heaviest set, and do not
move from 5060 to 5061; 16·313 is outside both regions, 8·631 and 12·421 are in E10's region (it holds their
columns), and 20·251 is column −1, in both.  The holders of 18, 27, 29, 30 and 32 are cells of the columns 151, 157,
163 and 241, which the best-known game reshuffles.  The recorded sets and the heaviest sets differ on hub cells only at 1192 = 8·149
(parity only, at 5061), at 1572 = 12·131, 1884 = 12·157 against 1812 = 12·151 and 2416 = 16·151 against 2512 =
16·157 (5060), and at 1647 = 27·61 and 1830 = 30·61 against 1770 = 30·59 (both games).

**Part B2, what the change 5060 → 5061 frees.**  With the heaviest set of 5060 nearest the committed set and the
heaviest set of 5061 nearest it:

* the study's region (columns of 151, 157, 163, 241, 251): the parity change leaves it at one cell, 1192 = 8·149
  entering (through the hub 8; E10's 492), and frees no element outside it;
* E10's region (149, 151, 157, 163, 241, 251, 421, 631): the parity change stays inside it and frees no element
  outside it.

Circuits of light region cells (the primes 241, 251 and small cells) pass through the far holders 5048, 5052, 5008,
5017, 5010, as the hub numbers' circuits do at the 16P games; as there, none of them is freed.

## What it decides

* **The sealing lemma, in the form that holds:** "the cascade frees no element outside the window" (not "no circuit
  passes through a ladder cell", which the hub coordinates make false at every game).  Measured: it holds at the four
  games whose column 3 has no row 18 (2224 and 2768, clean to depth 2; 3184 and 4432, clean to depth 3), and fails at
  exactly the two whose column 3 holds row 18, 1168 and 2512, through the same four cells (4, 3), (9, 3), (12, 3),
  (18, 3), the circuit E5 found for 931.  At 1168 nothing enters (the freed elements stay dependent at parity 0); at
  2512 931 enters.  So the prediction is confirmed with its condition sharpened: the lemma needs column 3 without row
  18 (18·P₃ > n − 1), which "clean to depth 2" gives at 2224 and 2768 and depth 3 gives always.
* **The seal at 5061 (the parity side):** E10's region is sealed (the change stays inside and frees nothing outside);
  the study's smaller region is not, by exactly one cell, 8·149 through the hub 8, so the region for 5061's local
  proof must hold the column of 149.  The holders of hubs 8, 12, 16 and 20 are the heaviest cells of their hubs in
  every heaviest set and never move: the per-hub statement "the holder is the heaviest h-cell, and the region's cells
  are lighter" holds for those four hubs at both boards.  For 18, 27, 29, 30 and 32 the holders are cells of the
  region itself, which is why the region must contain their columns.
* With E11 (no better game with 5060's set outside any region up to the columns of all primes 29..1013), the region
  of E10 is both sealed in the parity model and exhausted in the game, for the configuration with 5060's set outside.

## Files

seal.py and seal_out.txt (all parts; seal_a_out.txt is Part A alone), paritydump-5061.jsonl and paritydump-5061.err,
hubcells.txt, paritydump (the binary), hubs5061.started and hubs5061.ended (the run's times).
