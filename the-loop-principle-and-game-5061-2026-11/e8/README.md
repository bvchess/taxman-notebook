# E8, locality

Run on batmobile on 2026-11-11, 06:44 to 06:56 PST, from the branch `loops-e6` of the research repository (never
pushed): the code is commit 068a78b, the subcommand `window` of `examples/restricted.rs`, on 39dbd08 (the trace of E6),
on E1's three patches (0b82f86, 3f4b784, ce07a86, applied with `git am` to master 79faea3 without a conflict).  The
binary `restricted` here was built from the source of 068a78b.

## The question

The loops study's E8 (study-report.md, Section 8): at clean 16P and 20P games, solve game n with every promotion outside
columns 0 to 3 fixed as in the committed optimal set of n − 1 and the window free, and compare the best score with
opt(n).  Equal scores say that δ(n) is the window's own optimization, what Section 5.3's finite configuration assumes.

## The option

`restricted window N --depth D` (default D = 3).  P is the largest prime of N and P1 > P2 > … the primes below it; the
window is the candidates of N's root problem whose largest prime is one of P, P1, …, PD (the cells of columns 0 to D,
study-report.md Section 1).  Every other candidate is fixed (promoted at the root) if the committed optimal set of N − 1
holds it and barred if not, and the search is E2's (`Prepared::restricted`, an exact standalone search with no seed, no
ceiling and no near-repeat cut).  The answer is ΣU\*(N) plus the heaviest promotion set that respects the restriction,
the moves refereed on the board as `solve` referees them.  A member of the set of N − 1 up to N/2 outside the window that
is no candidate of game N could not be fixed; the line lists them as `unfixable` (there were none).

Each game was run at D = 0, 1, 2 and 3: D = 3 is the study's cell, and the smaller windows say how deep the change
reaches.

## The checks

* `restricted check-bars 1 60` on this build (check-bars-1-60.txt): 1,677 restricted problems of boards 1 to 60,
  1,620 equal to the oracle's answer (the heaviest L with U\* ∪ L playable that respects the restriction, by a walk over
  the playable sets, which shares nothing with the frames or the search) and 57 numbers that are no candidate refused,
  as they must be; no mismatch.  E1 and E2 checked the rest of the tool (../../succession/e1-holes/README.md,
  ../../succession/e2-bars/README.md); the library differs from theirs only by E6's trace, which is off here.
* The window's best set reproduces the committed optimal set of n on the window at every game (`window_promoted`
  against `window_committed` in e8.jsonl).

## The runs

`run-e8.sh`, at `nice -n 19` and `--background`, 4 threads, `--tactic symmetry=off` (the restricted root is a node).
First the six games asked for, 16P: 3184, 3728, 3824 (clean to depth 3) and 20P: 3620, 3940 (depth 2), 3980 (depth 3),
and 2512, the study's exception at depth 2; then, since each solve took under a second, every other 16P and 20P game of
the chain clean to depth 2 or more.  One JSON line a game and depth in e8.jsonl.  Every search completed in one step;
seconds are wall time of setup and search.

"short" is opt(n) less the restricted problem's best score; "least depth" is the smallest D whose window reaches opt(n).

| n | P | clean to | columns 0 to 3 | fixed | barred | window | score at D = 3 | opt(n) | short at D = 0, 1, 2, 3 | least depth | seconds |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---:|---:|
| 1648 | 103 | 2 | 103, 101, 97, 89 | 85 | 327 | 13 | 857,731 | 857,731 | 72, 56, 32, 0 | 3 | 0.07 |
| 1712 | 107 | 2 | 107, 103, 101, 97 | 91 | 340 | 12 | 922,797 | 922,797 | 60, 28, 16, 0 | 3 | 0.07 |
| 1744 | 109 | 2 | 109, 107, 103, 101 | 92 | 348 | 12 | 958,939 | 958,939 | 48, 32, 8, 0 | 3 | 0.07 |
| 1808 | 113 | 2 | 113, 109, 107, 103 | 96 | 363 | 12 | 1,028,763 | 1,028,763 | 60, 28, 16, 0 | 3 | 0.07 |
| 2224 | 139 | 2 | 139, 137, 131, 127 | 123 | 447 | 12 | 1,557,422 | 1,557,422 | 68, 52, 16, 0 | 3 | 0.11 |
| 2512 | 157 | 2 | 157, 151, 149, 139 | 136 | 525 | 13 | 1,988,840 | 1,988,840 | 100, 52, 40, 0 | 3 | 0.10 |
| 2768 | 173 | 2 | 173, 167, 163, 157 | 140 | 571 | 12 | 2,412,201 | 2,412,201 | 96, 48, 24, 0 | 3 | 0.17 |
| 2896 | 181 | 2 | 181, 179, 173, 167 | 148 | 605 | 12 | 2,641,253 | 2,641,253 | 76, 60, 24, 0 | 3 | 0.20 |
| 3152 | 197 | 2 | 197, 193, 191, 181 | 172 | 658 | 12 | 3,127,627 | 3,127,627 | 84, 52, 40, 0 | 3 | 0.21 |
| **3184** | 199 | 3 | 199, 197, 193, 191 | 173 | 678 | 12 | 3,193,895 | 3,193,895 | 48, 32, 8, 0 | 3 | 0.22 |
| 3664 | 229 | 2 | 229, 227, 223, 211 | 196 | 754 | 12 | 4,231,106 | 4,231,106 | 88, 72, 48, 0 | 3 | 0.30 |
| **3728** | 233 | 3 | 233, 229, 227, 223 | 199 | 782 | 12 | 4,375,106 | 4,375,106 | 60, 28, 16, 0 | 3 | 0.28 |
| **3824** | 239 | 3 | 239, 233, 229, 227 | 202 | 808 | 12 | 4,606,067 | 4,606,067 | 80, 32, 8, 0 | 3 | 0.32 |
| 3856 | 241 | 4 | 241, 239, 233, 229 | 203 | 819 | 12 | 4,678,194 | 4,678,194 | 68, 52, 16, 0 | 3 | 0.31 |
| 4016 | 251 | 2 | 251, 241, 239, 233 | 208 | 864 | 12 | 5,073,142 | 5,073,142 | 116, 36, 24, 0 | 3 | 0.36 |
| 4208 | 263 | 2 | 263, 257, 251, 241 | 218 | 900 | 12 | 5,573,700 | 5,573,700 | 124, 76, 40, 0 | 3 | 0.39 |
| 4304 | 269 | 2 | 269, 263, 257, 251 | 225 | 921 | 12 | 5,822,820 | 5,822,820 | 108, 60, 24, 0 | 3 | 0.40 |
| 4336 | 271 | 3 | 271, 269, 263, 257 | 227 | 953 | 12 | 5,914,999 | 5,914,999 | 76, 60, 24, 0 | 3 | 0.41 |
| 4432 | 277 | 3 | 277, 271, 269, 263 | 233 | 969 | 12 | 6,176,469 | 6,176,469 | 84, 36, 24, 0 | 3 | 0.43 |
| 4496 | 281 | 3 | 281, 277, 271, 269 | 234 | 983 | 12 | 6,357,360 | 6,357,360 | 76, 44, 8, 0 | 3 | 0.47 |
| 4528 | 283 | 4 | 283, 281, 277, 271 | 234 | 998 | 12 | 6,447,337 | 6,447,337 | 64, 48, 24, 0 | 3 | 0.55 |
| 4688 | 293 | 3 | 293, 283, 281, 277 | 244 | 1005 | 12 | 6,911,250 | 6,911,250 | 108, 28, 16, 0 | 3 | 0.46 |
| 4976 | 311 | 2 | 311, 307, 293, 283 | 261 | 1074 | 12 | 7,794,798 | 7,794,798 | 156, 124, 40, 0 | 3 | 0.55 |
| 5008 | 313 | 2 | 313, 311, 307, 293 | 261 | 1082 | 12 | 7,892,779 | 7,892,779 | 96, 80, 56, 0 | 3 | 0.56 |
| **3620** | 181 | 2 | 181, 179, 173, 167 | 193 | 764 | 20 | 4,131,443 | 4,131,443 | 48, 30, 0, 0 | 2 | 0.28 |
| **3940** | 197 | 2 | 197, 193, 191, 181 | 200 | 827 | 20 | 4,881,823 | 4,881,823 | 46, 10, 0, 0 | 2 | 0.32 |
| **3980** | 199 | 3 | 199, 197, 193, 191 | 202 | 852 | 20 | 4,981,537 | 4,981,537 | 38, 20, 0, 0 | 2 | 0.30 |
| 4580 | 229 | 2 | 229, 227, 223, 211 | 230 | 997 | 20 | 6,586,833 | 6,586,833 | 38, 20, 0, 0 | 2 | 0.38 |
| 4660 | 233 | 3 | 233, 229, 227, 223 | 239 | 998 | 20 | 6,830,058 | 6,830,058 | 46, 10, 0, 0 | 2 | 0.48 |
| 4780 | 239 | 2 | 239, 233, 229, 227 | 246 | 1017 | 20 | 7,187,630 | 7,187,630 | 74, 20, 0, 0 | 2 | 0.52 |
| 4820 | 241 | 2 | 241, 239, 233, 229 | 251 | 1055 | 20 | 7,303,605 | 7,303,605 | 48, 30, 0, 0 | 2 | 0.28 |

The six games asked for are in bold; "fixed", "barred" and "window" are counts at D = 3.

## The result

**At every one of the 31 games, the window of columns 0 to 3 reaches opt(n) exactly**: the best completion of the
committed set of n − 1 outside the window is an optimal game of n.  So δ(n) is the window's own optimization at every
clean 16P and 20P game of the chain, the six asked for and the 25 others, 2512 included, and its best set is the
committed set of n on the window.  Within the window it is a one-step search.

The smaller windows fall short, and the depth that reaches opt(n) is the family's:

* 16P: depth 3 at all 24 games, short by 8 to 56 at depth 2, whether the window is clean to depth 2 (15 games), 3 (7)
  or 4 (2).  This is the three-rung ladder of the study's Section 5.1 (hubs 16, 6 and 4 each move a column up), measured without the
  recorded sets of n.
* 20P: depth 2 at all 7 games, short by 10 to 30 at depth 1.

What it decides, by the study's criterion: δ(n) is the window's own optimization at these games, which is what Section
5.3's enumeration assumes; and the depth that the enumeration needs is 3 for 16P and 2 for 20P, the same as the
families' pattern depths (study-report.md Section 1, `study/depth_check.py`).  What it does not say: the outside is the
committed set of n − 1, one optimal set of it; another optimal set of n − 1 fixed outside might need a wider window.

## Files

run-e8.sh (the runs), e8.jsonl (one line a game and depth: the columns, the window's candidates, the counts fixed and
barred, the score, opt(n), the window's part of the best set, of the set of n − 1 and of the committed set of n),
e8-N.err (progress lines), check-bars-1-60.txt (the check), restricted (the binary).  The branch's code is kept as
patches in ../e6/patches/ (068a78b is the fifth).
