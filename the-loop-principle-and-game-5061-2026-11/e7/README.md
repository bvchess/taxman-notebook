# E7: does the window instance have an odd core?

Experiment E7 of the loops study (`../study-report.md`, Section 8; the instance is Section 5.3's), run 2026-11-11 from
06:40 to 08:05 PST.  Playability, cores and odd cores are those of
`/home/brian/taxman_work/research/docs/theory/playability.md`.

## The instance, made precise

For a cofactor c and depth d: d + 1 clean columns j = 0..d, each holding the rows 1..c.  The cell (k, j) = k·P_j
lists its column factors (k/q, j), one for each prime q dividing k, and its hub k, which every cell of row k lists.

* **Members: the cells of the composite rows** (layer 3 and up).  A layer-2 cell (q, j) lists P_j and the prime hub q,
  and only layer-2 cells list those.  So the layer-2 members of a core form a core by themselves, of members listing
  two factors each, which is never odd (P11), and no odd core holds a layer-2 cell.
* **The pool.**  A column factor of a prime row, and P_j, is always in the pool: from 187 on a game plays no prime but
  q(n) and no number of layer 2 up to n/2 (F4, F10), and a layer-2 cell above n/2 is no factor of any cell.  A column
  factor (m, j) of a composite row is in the pool unless the cell (m, j) is a move.  A hub is in the pool: it is a
  number up to c, never a move of these games.  As a wider check, `--hubs-removable` also lets any hub out of the pool.
* **Column factors are private to their column.**  In a clean column, (c + 1)·P_j > n, so a number listing k·P_j is a
  cell of the same column.  The hubs are the only factors shared between columns.
* **Enumerated:** every pair (T, X) of disjoint sets of cells, T nonempty and X the moves outside T (kept to cells
  that a member of T lists), such that T is a core of the instance whose pool leaves out T and X, and T's lists are
  independent over GF(2): the odd cores.  For each, whether T + X is independent with its own lists, so that a set
  independent at both parities can hold it.
* **Inclusion.**  A window (c', d') with c' ≤ c and d' ≤ d holds exactly the odd cores of (c, d) whose rows are at
  most c' and which use at most d' + 1 columns, since the conditions involve only T's own lists.

## What was run

* `window_cores.py` (Python, rows from c down; every core condition is checked when its factor's row is reached; at
  every step the lists so far, with undecided factors counted in the pool, must be independent, since a later
  decision is a projection that keeps any dependency; columns in canonical order).  It ran for (16, 3), (20, 2),
  (24, 2) and (40, 1), and with hubs removable for (16, 3).  Outputs: `out_cC_dD.txt` (summary), `cores_cC_dD.jsonl`
  (every core).
* Cross-checks, all giving the same cores: `window_cores_up.py`, the same search with the rows from 4 up
  (`up_cores_*.jsonl`); `window_cores.py --guided`, which first lists one column's feasible prefixes; the Rust port
  `windowcores` (`solver/noframe/examples/windowcores.rs`, branch `loops-e5`, commit 9af61b3), which reproduces every
  case above and the sanity cases.  The sanity cases: on (45, 0) with hubs removable it finds the first odd core of
  the theory, {12, 18, 20, 30, 45} (C3), and on (45, 1) that core doubled across two columns.
* `windowcores 36 2` (8 threads, 38 minutes, 1.25·10⁹ nodes): every odd core with at most three nonempty columns and
  rows up to 36.  Output: `rust_cores_c36_d2.jsonl` (`.done` lists the finished tasks), `rust_summary_c36_d2.json`.
* `windowcores 17 D` for D = 3, 4, 5 (`rust_cores_c17_d*.jsonl`, each under a second).
* `summarize.py` → `summary_small.txt` (the Python runs) and `summary_c36_d2.txt` (the Rust run, with the cores of
  each cofactor 20, 24, 30, 32, 36 listed apart): per file, the cores, the distinct T, and the minimal ones (no proper part of T is a
  core of the same instance; every odd core holds one), each column with dim, the dimension of its cycle space.  An
  independent T is exactly a direct sum of the columns' cycle spaces, read as sets of rows.

`stopped/` holds the empty outputs of runs stopped and replaced by better methods.

## Results

| (c, d) | columns | odd cores (T, X) | minimal | distinct minimal T | complete? |
|---|---|---|---|---|---|
| (16, 3) | 4 | 0 | 0 | 0 | yes |
| (17, 5) | 6 | 0 | 0 | 0 | yes (so none for c ≤ 17 in up to 6 columns) |
| (40, 1) | 2 | 0 | 0 | 0 | yes (so no two-column odd core for c ≤ 40) |
| (20, 2) | 3 | 2 | 2 | 2 | yes |
| (24, 2) | 3 | 2 | 2 | 2 | yes |
| (30, 3) | 4 | 4,142 with 3 columns | 2,122 | 378 | 3 columns only |
| (32, 4) | 5 | 4,142 with 3 columns (none uses rows 31, 32) | 2,122 | 378 | 3 columns only |
| (36, 3) | 4 | 69,357 with 3 columns | 2,285 | 541 | 3 columns only |

Columns are counted up to their order.  Every minimal core found has T + X independent, so a set independent at both
parities can hold it.  The cores with four or five nonempty columns of (30, 3), (32, 4) and (36, 3) were not
enumerated.  By Knuth's random-probe estimate the search takes about 6·10¹⁰ nodes for (30, 3) and 5·10¹³ for (32, 4)
and for (36, 3), against 1.25·10⁹ for (36, 2).  Existence there is settled by inclusion.

**The two cores of (20, 2) and (24, 2).**  Both have 7 members on 3 rows, every column of dim 1:

* rows {8, 12, 18}: column a holds T {8, 12, 18} with X {9}; column b T {12, 18} with X {4, 9}; column c T {8, 12}
  with X {6};
* rows {12, 18, 20}: column a holds T {12, 18, 20} with X {9, 10}; column b T {12, 20} with X {6, 10}; column c
  T {12, 18} with X {4, 9}.

Checked by hand for the first.  The lists are (8,a): (4,a), h8; (12,a): (4,a), (6,a), h12; (18,a): (6,a), h18;
(12,b) and (18,b): (6,b) and their hubs; (8,c) and (12,c): (4,c) and their hubs.  Each factor is listed twice and each
hub two or three times, so T is a core.  The column cycles {8, 12, 18}, {12, 18} and {8, 12} are independent as sets
of rows, so the 7 lists on 7 coordinates are independent.  In a 20P game with the window clean to depth 2 this is a
configuration of the cells 8P_j, 12P_j and 18P_j with the moves 9P_a, 4P_b, 9P_b and 6P_c.  The second core holds row
20 in two columns, one of which may be n's own.

**The shape of every minimal core found.**  Three columns.  The 23 smallest (7 members on 3 rows; 22 of them with
rows up to 30) all repeat the pattern above: one column holds the three rows on a path of shared column factors, each
of the other two holds two of the rows joined by one shared column factor, and the moves strip the private factors,
so that the three column cycles span all sets of the three rows.  Their row sets are {8, 12, 18}, {12, 18, 20}, {8, 12, 30}, {8, 20, 30},
{12, 18, 27}, {12, 18, 28}, {12, 20, 30}, {12, 28, 30}, {18, 20, 30}, {18, 27, 30}, {20, 28, 30} and {16, 24, 36}.
The larger minimal cores (up to 18 members on up to 9 rows) have column dims such as (1, 1, 2), (1, 2, 2) and
(1, 2, 3).  The rows 8, 12, 18, 20, 27, 28 and 30 carry almost all of them up to c = 30.

**With hubs out of the pool** (`--hubs-removable`, the wider question), (16, 3) has 8 odd cores, 4 distinct T.  All
lie in two columns on the semiprime rows 4, 6, 9, 10 and 15, with two or three of those hubs out of the pool.  They
need small numbers to be moves or unavailable to the window, which they are not in these games.

## What it decides

By the study's criteria (Section 8, E7):

* **Within the windows tested, the window instance has an odd core exactly when c ≥ 18 and d ≥ 2.**  None in two
  columns for any c ≤ 40, none for c ≤ 17 in up to six columns, and the core on rows {8, 12, 18} in every window with
  three columns and c ≥ 18.
* **The "same finite problem" explanation can hold** wherever the window has no odd core: every cofactor up to 17 at
  any depth up to 5 (8P, 12P, 16P among them) and every cofactor up to 40 at depth 1 (40P).  This agrees with E5: at
  every clean 16P game the parity bound's change is the game's, and 2512 parts through a circuit outside the window,
  not through an odd core inside it.
* **It cannot hold as it stands** for any cofactor from 18 on at depth 2 or more: 18P, 20P, 21P, 24P and 25P at depth
  2 (the two 7-member cores, realizable, from c = 18 and c = 20), 30P and 36P at depth 3 and 32P at depth 4
  (thousands).  There the two models can part inside a clean window, and a proof of P1 needs more than the window:
  an argument that these configurations never price a heaviest set of the parity bound above the game, or a deeper
  hypothesis.
* **An odd core in the window is not enough for a rise.**  The chain's games of these cofactors at depth 2 or more all
  have rise 0 (study, Section 4.1: 20P 7, 21P 6, 18P 2, 24P 2, 25P 2), and E5 finds the parity bound's change equal to
  the game's, cell for cell and forced, at 4975 = 25·199 (depth 2) and 4893 = 21·233 (depth 3), whose windows have
  odd cores.  So the absence of an odd core is a sufficient test, not a necessary one.  Past 5060 the exceptions at
  depth 2 fall in cofactors whose windows have odd cores (30P 8 of 9, 32P 6 of 6, 36P 2 of 2, 20P 3 of 36, 21P 5 of
  31; study, Section 4.1).  The flagged plays tell, game by game, whether each is a short best-known game or the
  parity bound taking such a core.
