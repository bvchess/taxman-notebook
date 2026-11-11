# E2, the 12P law with a candidate fixed and one barred

Run on batmobile on 2026-11-10, 22:09 to 22:21 PST, from the branch `holes-e1` of the research repository (never
pushed), commit 57d7491, the build of E1 (../e1-holes/restricted; its README has the code and the checks of boards with
holes).

## The question

For n = 12P with P prime and P1 the prime before P, the 12P law says opt(n) = opt(n − 1) + n − 6P1.  The study splits
the promotion sets of the root problem Π_n by whether they promote 6P, 4P and 4P1; two of the three cases are proved,
and the one left is run (b): 6P promoted and 4P not.  A best score of that case at or below the law's score confirms the
law at the game, given U; one above it would be a counterexample.

## The option

`restricted solve N --fix F,... --bar B,...`: the exact standalone search of game N (no seed, no ceiling, no near-repeat
cut) whose root is the node that promotes the fixed candidates, over the other candidates less the barred ones
(`Prepared::restricted`).  A set Q can be promoted from that node exactly when F ∪ Q can be promoted from the root, so its
answer is the heaviest promotion set of Π_n that holds every fixed number and no barred one, and the score is ΣU\*(n) +
its sum: the best score of the games that play all of U\* and respect the restriction (the exactness theorem (X7)).
Setup refuses a number that is no candidate of the root, a number both barred and fixed, and the tactic `symmetry`,
whose rule (R2) is proved of a root problem's root; the runs give `--tactic symmetry=off`.  `--in-ustar` reports
whether numbers are in U\*(n).

## The checks

Every comparison agreed.

* **`restricted check-bars 1 120`** (check-bars-*.txt): on every board 1 to 120, each of its 1,149 candidates barred,
  each fixed, and each of the 16,362 pairs of a barred and a fixed candidate, 18,660 restricted problems, each against
  the heaviest L ⊆ {2, …, ⌊n/2⌋} with U\* ∪ L playable that holds the fixed number and not the barred one, found by a
  walk over the playable sets with `playable::playable` (X7's statement, sharing nothing with the frames or the search);
  and on 117 boards a number up to n/2 that is no candidate, barred, was refused.  Every single candidate could be fixed,
  so the case of a fixed set that cannot be promoted from the root did not come up.
* **`restricted check-chain 300 500 700 1000 1667`** (check-chain*.txt): on these boards of the chain, the recorded
  promotion set fixed in whole scores opt(n) on all five, and each of its 237 members barred scores at most opt(n).

## The runs

`run-e2.sh`: run (b) at each game on 16 threads at idle priority, with 8P, 8P1 and 12P1 checked in U\*(n).  The lines
are in e2.jsonl (with the promotion set of each), the progress lines in e2-*.err.

| n | P | P1 | fixed 6P | barred 4P | 8P, 8P1, 12P1 in U\*(n) | best score | opt(n − 1) + n − 6P1 | difference | nodes | seconds |
|---:|---:|---:|---:|---:|:---|---:|---:|---:|---:|---:|
| 1668 | 139 | 137 | 834 | 556 | 1112, 1096, 1644: yes | 878,104 | 878,104 | 0 | 25,365 | 1.08 |
| 2004 | 167 | 163 | 1002 | 668 | 1336, 1304, 1956: yes | 1,264,085 | 1,264,085 | 0 | 25,347 | 1.26 |
| 2316 | 193 | 191 | 1158 | 772 | 1544, 1528, 2292: yes | 1,692,121 | 1,692,121 | 0 | 3,645,088 | 40.46 |
| 2748 | 229 | 227 | 1374 | 916 | 1832, 1816, 2724: yes | 2,377,810 | 2,377,810 | 0 | 67,057 | 2.11 |

Seconds are wall time of setup and search; each search completed.

## The result

Run (b) reaches the law's score exactly at all four games and never passes it, so the 12P law holds at them given U.
That could not have come out otherwise: at these four games the law's score is the committed score of game n, which is
ΣU\* + P\*(Π_n) by the chain's exact search, and no restricted problem of Π_n scores more than Π_n itself; and the
recorded optimal set of each already promotes 6P and not 4P, so case (b) holds an optimal set.  None of the four best
sets of case (b) promotes 4P1.
