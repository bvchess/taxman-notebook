# E6, the exchange law's obligation

Run on batmobile on 2026-11-11, from the branch `loops-e6` of the research repository (never pushed).  The runs
reported here are of 07:28 to 07:31 PST, with the example `obligation` of commit 3133af1 and the library of 4018e07 (the
same library: 3133af1 changes only the example).  The code is three commits on E8's 068a78b, which is on E1's three
patches (0b82f86, 3f4b784, ce07a86, applied with `git am` to master 79faea3 without a conflict):

* 39dbd08: `search::trace`, a hook that a caller installs once a process, which the bound check of a node calls with
  each heaviest set that reaches the node's need and cannot be promoted, and the nogood table with each nogood it
  learns; and the example `obligation`;
* 4018e07: the trace also reports each child whose promotion fails, and the example classes those sets too;
* 3133af1: a sample's sum less P\*(n − 1) is written as a signed number.

The binaries here are `obligation` (3133af1) and `taxman.loops-e6` (4018e07).  run1/ holds the same runs with the
build of 39dbd08 (06:57 to 07:05, no failed promotions traced), run2/ with the build of 4018e07 (07:13 to 07:16); they
agree with the runs below in every class, and their counts differ as a multi-threaded search's tree does.

## The question

The loops study's E6 (study-report.md, Sections 6.3 and 8).  At an exchange step n, U\*(n) = U\*(n − 1) − x + n, x the
shadow of n.  With B = U\*(n − 1) − x = U\*(n) − n, a set L of numbers up to n/2 is

* *x-bound* when U\*(n − 1) ∪ L is unplayable and B ∪ L is playable: every core of U\*(n − 1) ∪ L holds x (x divides no
  number of the board, so taking it out changes no list, and "no core without x" is "B ∪ L playable");
* *n-bound* when U\*(n) ∪ L is unplayable and B ∪ L is playable; so an x-bound set is n-bound exactly when it cannot be
  promoted in Π_n, by the exactness theorem (X7).

A set that is not x-bound has a core without x, which is a core with U\*(n) too: it cannot be promoted in Π_n either.
The study asks, from an exact proof of n − 1: how many of the sets it refuted above P\*(n − 1) are x-bound (the size of
the obligation), and whether every x-bound one is n-bound.

## What was run

`obligation N` searches game N − 1 exactly, as a standalone search from its committed optimal promotion set: the
incumbent is P\*(N − 1) from the start, so the search refutes only sets worth more, and no game before N − 1 is used (no
ceiling, no near-repeat cut).  16 threads, `--background`, `nice -n 19`, stopped at 30 minutes (none came near it).
The trace hands the example:

* each *refuted set* R = P ∪ I\*: a node's promotions P with its bound's heaviest set I\*, which reaches the node's need
  and cannot be promoted; and the node's conflict K, the one it branches on (P ∪ K cannot be promoted);
* each *nogood* learned (a set that cannot be promoted from the root; every conflict a node uses is a nogood less the
  node's promotions);
* each *failed promotion*: a child whose promotion of its forced members, or of its one member, fails (P ∪ added cannot
  be promoted).

Each distinct set is classed with the plain peel of `playable::playable`, which shares nothing with the frames or the
search: unplayable with U\*(n − 1) (a check of the model), x-bound or not, promotable in Π_n or not.  An x-bound
conflict, nogood or failed promotion *transfers* when game n cannot promote it either.

Two variants: the solver's default tactics, and `--tactic symmetry=off`, so that the proof sets nothing aside by the
rule of symmetric pairs (see "What the counts show", item 2).

## The checks

* checks.txt: on one thread the search takes the same steps with the trace installed and without it (741, 1209, 1599,
  1677, 2067); `taxman solve` takes the same steps from E1's build, which has no trace, and from this one (740, 1208,
  1598, 2066); `taxman regress --to 1000` matches the table on all 1,000 games.
* In every run below: the search completed at P\*(n − 1), which it started from, and P\*(n) = P\*(n − 1) by the committed
  scores (the exchange law at the game); no refuted set was worth P\*(n − 1) or less; the peel found every refuted set,
  node conflict, failed promotion and nogood unplayable with U\*(n − 1), as the model did; every nogood is minimal by
  deletion; no set that is not x-bound was promotable in Π_n.
* e1_sets.py (e1_sets_out.txt), a side check below, with its own peel and GF(2) elimination.

## The runs

`run-e6.sh` (`TAG=symmetry-off EXTRA="--tactic symmetry=off"` for the second).  One JSON line a game in e6-TAG.jsonl,
samples in e6-TAG-samples-N.jsonl, progress lines in e6-TAG-N.err.  Counts are of distinct sets; seconds are wall time of
the search.

**Default tactics**

| n | x | P\*(n − 1) | steps | seconds | refuted sets | x-bound | node conflicts x-bound: transfer, not | failed promotions | x-bound: transfer, not | nogoods | x-bound: n-bound, promotable in Π_n |
|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---|
| 741 | 374 | 13,565 | 58 | 0.0 | 20 | 0 | 0, 0 | 8 | 0, 0 | 10 | 0, 0 |
| 1083 | 578 | 28,197 | 68 | 0.0 | 28 | 0 | 0, 0 | 14 | 0, 0 | 15 | 0, 0 |
| 1209 | 638 | 35,091 | 2,056 | 0.1 | 830 | 0 | 0, 0 | 282 | 0, 0 | 166 | 0, 0 |
| 1599 | 814 | 58,255 | 6,539 | 0.3 | 2,575 | 0 | 0, 0 | 784 | 0, 0 | 216 | 0, 0 |
| 1677 | 902 | 64,080 | 7,090 | 0.3 | 2,813 | 0 | 0, 0 | 1,137 | 0, 0 | 409 | 0, 0 |
| 1729 | 935 | 69,771 | 15,702 | 0.5 | 6,112 | 0 | 0, 0 | 2,308 | 0, 0 | 681 | 0, 0 |
| 1767 | 986 | 72,564 | 8,517 | 0.5 | 3,382 | 0 | 0, 0 | 1,548 | 0, 0 | 438 | 0, 0 |
| 1833 | 946 | 76,897 | 110,981 | 2.6 | 42,023 | 0 | 0, 0 | 15,144 | 0, 0 | 1,328 | 0, 0 |
| 2067 | 1034 | 100,979 | 15,393 | 1.1 | 6,640 | 0 | 0, 0 | 1,643 | 0, 0 | 331 | 0, 0 |
| 2139 | 1102 | 106,335 | 20,165 | 1.1 | 8,261 | 0 | 0, 0 | 2,739 | 0, 0 | 368 | 0, 0 |
| 2301 | 1166 | 125,095 | 1,402,972 | 41.8 | 544,553 | 0 | 5, 1 | 189,872 | 3, 0 | 5,428 | 2, 1 |

**Symmetry off**

| n | x | P\*(n − 1) | steps | seconds | refuted sets | x-bound | node conflicts x-bound: transfer, not | failed promotions | x-bound: transfer, not | nogoods | x-bound: n-bound, promotable in Π_n |
|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---|
| 741 | 374 | 13,565 | 58 | 0.0 | 20 | 0 | 0, 0 | 8 | 0, 0 | 10 | 0, 0 |
| 1083 | 578 | 28,197 | 87 | 0.1 | 41 | 0 | 0, 0 | 19 | 0, 0 | 23 | 0, 0 |
| 1209 | 638 | 35,091 | 2,468 | 0.3 | 1,121 | 0 | 0, 0 | 412 | 0, 0 | 261 | 0, 0 |
| 1599 | 814 | 58,255 | 6,969 | 0.6 | 2,935 | 0 | 0, 0 | 1,018 | 0, 0 | 280 | 0, 0 |
| 1677 | 902 | 64,080 | 9,862 | 0.5 | 3,987 | 0 | 0, 0 | 1,884 | 0, 0 | 544 | 0, 0 |
| 1729 | 935 | 69,771 | 22,439 | 0.7 | 9,476 | 0 | 0, 0 | 3,732 | 0, 0 | 957 | 0, 0 |
| 1767 | 986 | 72,564 | 10,631 | 0.4 | 4,495 | 0 | 0, 0 | 2,013 | 0, 0 | 548 | 0, 0 |
| 1833 | 946 | 76,897 | 169,684 | 4.1 | 71,642 | 0 | 0, 0 | 22,543 | 0, 0 | 2,012 | 0, 0 |
| 2067 | 1034 | 100,979 | 16,690 | 1.1 | 7,302 | 0 | 0, 0 | 1,749 | 0, 0 | 394 | 0, 0 |
| 2139 | 1102 | 106,335 | 22,726 | 1.2 | 9,649 | 0 | 0, 0 | 3,124 | 0, 0 | 533 | 0, 0 |
| 2301 | 1166 | 125,095 | 1,436,260 | 44.6 | 572,315 | 0 | 5, 1 | 193,836 | 2, 0 | 7,626 | 2, 1 |

## What the counts show

1. **No refuted set is x-bound**, at any of the eleven games, in either variant: of 20 to 572,315 distinct sets a game
   above P\*(n − 1), every one has a core without x, which is a core with U\*(n) too, so game n refuses it the same way.
   The obligation of Section 6.3, counted as the study asks, is zero, and the question whether every x-bound refuted set
   is n-bound has no instance.  (It could not have failed: the committed scores give P\*(n) = P\*(n − 1), so no set
   above P\*(n − 1) can be promoted in Π_n.  The runs check that; they cannot decide it.)
2. **At ten of the games the bound's whole family holds no x-bound set above P\*(n − 1).**  With symmetry off, a proof
   sets a completion aside only by a bound, which sets aside only sets of the bound's family worth at most the incumbent
   (or sets outside the family), or because it holds a node's conflict with its promotions, a nogood, or a failed
   promotion's set, all of which the trace reports (search.md, the paragraph "Why the step is exact").  The bound's family is the
   candidate sets independent in every frame, which by the comparison theorem (B6, part 1) are the candidate sets L
   with U\*(n − 1) ∪ L independent at both parities: ℒ within the root's candidates.  A subset of an x-bound set that
   cannot be promoted is x-bound (B ∪ the subset is playable).  So where nothing the trace reports is x-bound, which is
   every game but 2301, no set of the family worth more than P\*(n − 1) is x-bound.  This is an inference from the
   search's exactness argument, not a computation of its own.
3. **At 2301 a few sets are x-bound**, in both variants: 6 node conflicts, 2 or 3 failed promotions and 3 nogoods of
   several thousand.  All but one transfer.  The one that does not is the nogood {602, 826, 1058, 1113, 1118}
   (2·7·43, 2·7·59, 2·23², 3·7·53, 2·13·43; x = 1166 = 2·11·53, n = 2301 = 3·13·59), which game 2301 can promote.  It
   was the conflict of one node, with 13 promotions, whose refuted set (450 above P\*(2300)) has another core, of 17
   members and without x, the same in game 2301 (e6-TAG-samples-2301.jsonl).  The other two x-bound nogoods,
   {602, 854, 1058, 1113, 1118} and {682, 1085, 1118}, are n-bound.  So every set the proof of 2300 refuted is refused
   in game 2301, and every conflict, nogood and failed promotion of the proof but that one nogood refuses in game 2301
   what it refused in game 2300; whether the family holds an x-bound set above P\*(2300) these counts leave open.
4. **E1's sets lie outside ℒ** (e1_sets_out.txt).  E1's best set on Y = board n − 1 without x has the sources B at all
   eleven games, and its part up to (n − 1)/2, L′, worth 242 to 951 more than P\*(n − 1), is x-bound and n-bound; and
   U\*(n − 1) ∪ L′ is dependent at a parity at all eleven, so the parity bound refuses it with no conflict.  This answers
   the parenthesis of the study's Section 6.2: the E1 detours are not members of ℒ, and both bounds refuse them.

## What it decides

By the study's criteria: the size of the obligation is zero at all eleven games, and no x-bound set above P\*(n − 1)
was met that game n can promote, so this is the branch where everything transfers; no improvement argument is needed at
these games.  The near-repeat shape holds node by node at ten games without exception, and at 2301 for all but one
nogood, whose sets game n refuses by another core without x.

The target the study names, "an x-bound set above P\*(n − 1) is n-bound", can be sharpened at these games to "no set of
ℒ worth more than P\*(n − 1) is x-bound": every such set has a core without x.  That gives the law's upper half where it
holds, given (♦) and U: a set promotable in Π_n is independent at both parities with U\*(n) (P10), so lies in the
family that Theorem A says both boards share, and if it were worth more than P\*(n − 1) its core without x would be a
core with U\*(n).  At ten of the eleven games the frame solver's own proof shows it within the root's candidates;
2301 is the game to test it at, on its x-bound nogood {602, 826, 1058, 1113, 1118}.  The x-bound sets that do exist
above P\*(n − 1), E1's, are refused by parity, not by playability.

## Files

run-e6.sh (the runs), e6-default.jsonl and e6-symmetry-off.jsonl (one line a game: the games' numbers, the search, and
the counts by class of the refuted sets, node conflicts, failed promotions and nogoods), e6-TAG-samples-N.jsonl (the
x-bound sets that game n can promote, with a minimal core in each game; `core_m_xbound` says whether every core of
U\*(n − 1) with the minimal core holds x), e6-TAG-N.err (progress lines), checks.txt, e1_sets.py and e1_sets_out.txt
(the side check), obligation and taxman.loops-e6 (the binaries), run1/ and run2/ (the earlier builds' runs; run1 has
the `regress` output of its build), patches/ (the branch `loops-e6` from master 79faea3, for `git am`: E1's three, then
39dbd08, 068a78b, 4018e07 and 3133af1 for E6 and E8, and the second round's commits after them).
