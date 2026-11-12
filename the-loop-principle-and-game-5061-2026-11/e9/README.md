# E9, the parity hole law (T)

Run on batmobile on 2026-11-11, 09:23 to 09:53 PST, and 2301 on 16 threads from 10:13 to 10:23, from the branch `loops-e6` of
the research repository (never pushed).  The search is the prover's (`solver/noframe`), with commit e939ea0
(`Prover::with_parity_forcing` and the example `ghost`) and df9b660 (its threaded option); the binary here is df9b660's.

## The question

The study's (T) (Section 12): at an exchange step n with shadow x and B = U\*(n − 1) − x, does any promotion set L with
U\*(n − 1) ∪ L independent at both parities and B ∪ L playable on board n − 1 weigh more than P\*(n − 1)?  x is a
*ghost*: it stays in the parity constraint and leaves the playability test.  (T) gives the exchange law's upper half
(given U at n and (♦)), so a "no" at every game makes it the one-board target; a set above P\*(n − 1) would be an
x-bound member of ℒ, which the law (proven at these games) says is n-bound.

## The tool

`ghost N --mode ghost|plain|hole`: the prover's exact branch and bound (the parity bound on, its weight split
certifying every bound; conflicts from minimal unplayable subsets; nogoods) on board n − 1, with U\*(n − 1) picked
(the committed set's sources, checked against descending greedy), the other sources barred, every number up to
(n − 1)/2 free (no bottom-layers roles, which are a theorem about the game's optimal sets), and the target such that a
set beats it exactly when its promotions weigh more than P\*(n − 1).  The question covers every number up to (n − 1)/2,
not only the frame solver's candidates.

* `ghost`: x barred from the picks, so every playability test, conflict and matching is that of B ∪ L; the parity
  bound picks x in every solve, with weight 0 (`with_parity_forcing`, the one change to the prover's library), so the
  sets it counts are independent at both parities together with all of U\*(n − 1).  The answer to (T).
* `plain`: the true game, x picked like the rest of U\*(n − 1).  It must find nothing, since n − 1 is proven: a check.
* `hole`: x barred everywhere: the game of the board without x with the sources B (E1's question, which found sets
  above P\*(n − 1) at every game).  It must find a set: a check that the search finds what is there.  It stops at the
  first set found, so its excess is not E1's best.

A set found is checked again: its playability by the board's peel and its independence at both parities by a parity
solve with every member picked (with x, in the ghost mode).  One thread a run, at idle priority (`chrt --idle 0`),
15 runs at a time, each stopped at 30 minutes (`run-e9.sh`).  v1/ and v2/ hold runs of two earlier versions, stopped
and superseded: a search of my own (slower), and a ghost made by giving x a private factor on a copy of the board,
which failed at 2067 (the private factor must be smaller than x, since the matching takes an edge's larger end as the
pick, and at 2067 x is the smallest source; the search ended at its root there).

## The checks

* `plain` finds no set above P\*(n − 1) at all eleven games (2301 on 16 threads), as the committed proofs require; its
  root parity bound is P\*(n − 1) plus the gap of n − 1 in `../../succession/settle.csv` at every game.
* `hole` finds a set above P\*(n − 1) at all eleven games, each playable by the peel and independent at both parities,
  as E1 says there are.
* The ghost's root parity bound equals the plain one at every game (x in both), and its root matching bound equals the
  hole's (x out of both): the two halves of the ghost are what they should be.  No parity solve was uncertified.

## The results

(summary.md, made by `summarize.py` from the lines in e9.jsonl)

| n | x | P\*(n − 1) | root parity bound above P\* (plain = ghost) | ghost: answer, nodes, seconds | plain: answer, nodes, seconds | hole: answer, set's excess, nodes |
|---:|---:|---:|---:|---|---|---|
| 741 | 374 | 13,565 | 106 | no set beats P\*, 23, 0.0 | no set beats P\*, 23, 0.0 | a set beats P\*, +8, 26 |
| 1083 | 578 | 28,197 | 73 | no set beats P\*, 24, 0.1 | no set beats P\*, 24, 0.1 | a set beats P\*, +264, 9 |
| 1209 | 638 | 35,091 | 194 | no set beats P\*, 6,165, 6.5 | no set beats P\*, 6,162, 6.6 | a set beats P\*, +3, 6,906 |
| 1599 | 814 | 58,255 | 433 | no set beats P\*, 2,815, 3.5 | no set beats P\*, 2,813, 3.0 | a set beats P\*, +38, 27 |
| 1677 | 902 | 64,080 | 352 | no set beats P\*, 25,401, 26.0 | no set beats P\*, 25,399, 26.8 | a set beats P\*, +16, 136 |
| 1729 | 935 | 69,771 | 336 | no set beats P\*, 24,208, 24.9 | no set beats P\*, 24,205, 23.8 | a set beats P\*, +1, 1,447 |
| 1767 | 986 | 72,564 | 308 | no set beats P\*, 3,792, 4.2 | no set beats P\*, 3,838, 3.8 | a set beats P\*, +11, 804 |
| 1833 | 946 | 76,897 | 524 | no set beats P\*, 90,155, 89.8 | no set beats P\*, 90,153, 87.6 | a set beats P\*, +1, 80 |
| 2067 | 1034 | 100,979 | 534 | no set beats P\*, 59,953, 95.2 | no set beats P\*, 59,953, 90.4 | a set beats P\*, +5, 3,796 |
| 2139 | 1102 | 106,335 | 478 | no set beats P\*, 26,892, 45.1 | no set beats P\*, 26,892, 45.8 | a set beats P\*, +7, 6,819 |
| 2301 | 1166 | 125,095 | 721 | stopped at 30 minutes, 724,736 | stopped at 30 minutes, 721,920 | a set beats P\*, +29, 13,980 |

At 2301, where one thread stopped at 30 minutes in both modes, the prover's campaign of 16 threads (`--threads 16`,
nogoods traded every 30 seconds) finished both:

| n | mode | answer | nodes | wall seconds | thread seconds |
|---:|---|---|---:|---:|---:|
| 2301 | ghost | no set beats P\* | 1,504,929 | 278.6 | 4,435 |
| 2301 | plain | no set beats P\* | 1,538,141 | 282.1 | 4,486 |
| 1209 | ghost (a check of the threaded path) | no set beats P\* | 7,585 | 2.4 | 32 |

## What it decides

* **(T) holds at all eleven games, 741 to 2301**, by an exact search over every promotion set of the board, not only
  the frame solver's candidates: no set independent at both parities with U\*(n − 1) and playable with x left out
  weighs more than P\*(n − 1).  With the law's derivation (Section 12), (T) is there the one-board target for the
  exchange law's upper half, and E1's detours (the hole runs' sets) are refused by parity alone.
* At the ten games 741 to 2139 the ghost search takes the plain search's tree to within a few dozen nodes: with x in the parity
  bound, the playability test with or without x makes the same refutations, which is E6's finding (no cut x-bound) in
  another solver.
* **2301 too**, the one game where E6 found a cut that does not transfer (the nogood {602, 826, 1058, 1113, 1118},
  x-bound and promotable in game 2301): that nogood refutes nothing (T) needs, since every set above P\*(2300) that
  holds it has another core without x or is outside ℒ.  By the study's criterion, equality everywhere: (T) is the
  one-board target, and a proof needs no transfer argument beyond it at these games.

## Files

run-e9.sh, e9-N-MODE.json (one line a run) and e9.jsonl (all of them), e9-N-MODE.err, summarize.py and summary.md,
ghost (the binary), e9-2301-ghost-16threads.jsonl, e9-2301-plain-16threads.jsonl and e9-threaded-checks.jsonl
(the 16-thread runs, with their .err; e9.jsonl holds them too), v1/ and v2/ (the superseded runs), and the files of the
runs' times.
