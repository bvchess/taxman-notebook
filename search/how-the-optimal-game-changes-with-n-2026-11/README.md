# How the optimal game changes with n (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-06.  Concluded 2026-11-06.

**Question.**  How does the optimal promotion set of game n differ from what the game of n − 1 gives it, and from the
sets at which the unsound mode's large neighborhood search sticks?  Which promotions change together, can the change be
foreseen from the games before or from n, and what neighborhood or seed would hold it?  This is study E5 of the unsound
mode (`taxman solve LO-HI --unsound --effort E`), whose rounds fix a random 70-90% of the incumbent's promotions and
search the rest.

**Answer.**  From n − 1 to n the optimal set changes only in a searched game, and then by a small swap: a median of 2
drops and 1 or 2 additions, 5 or more drops in a quarter of the steps, the same size from 1001 to 5060.  The promotions
that change at one step are tied to each other far more than chance: 88-89% share their largest prime or their cofactor
with another change of the step, against 41-49% of random sets.  They lie low in the range (a median 0.36 n, against
0.43 n for the kept promotions), in the frame where n arrives and near n's largest prime, and the steps before predict
them only weakly.  The swaps that the search of the pilot [P1](../the-unsound-mode-on-the-hard-games-2026-11/README.md)
could not make are larger, 6 to 13 promotions each way, and their connected region in the frame model is about half
the incumbent.  No small group holds them: no relation of numbers joins a stuck swap into one group, and windows of
size and groups grown in the frame model hold them only at 80 to 100 freed promotions.  Two findings point to cheaper
remedies: the drops lie low in size, and the start's local search walks away from the optimal set.  What survives of
the moves of n − 1 before that search, though a median 1,165 points lower, is fewer drops from the optimal set than
the start in 24 of the 40 games of P1 whose start fell short.

**Proposal.**  Two changes to the rounds, both drawn so that a neighborhood's random choices come from the generator of
(seed, n, round, k) alone (section 6):

1. **A share tilted toward the small promotions.**  Free each promotion with a probability proportional to a fixed
   weight of its size x/n, 4.9 near n/4 falling to 0.3 near n/2, fitted on the steps of 1001-3440.  On data the fit
   never saw, at the default expected share of 0.2 it lifts the short starts expected at opt(n) after one round from
   4.6 to 15.0 of 40.  At an expected share of 0.4, 80 to 106 freed promotions, a round of 64 frees the whole swap of
   each stuck set with chance 0.20 to 1.00, an expected 6.0 of the 8, against 0.3 for the uniform share.
2. **More trajectories, from the survivors of the games before.**  Begin a trajectory from each distinct set that
   survives of the moves of n − 1, n − 2, …, n − 8, as well as from the start: a mean of 3.0 trajectories a game.  One
   round from each holds an expected 2.7 of the 6 games that both of the pilot's seeds missed in 256 rounds (the
   survivors of 4224 are the optimal set of 4232 itself), and on the other games about what the start's own rounds of
   the same work hold.

Their cost is the open question: the tilted share at 0.4 frees as many promotions as `--fix 0.5,0.7`, and its steps
must be measured.

## Method

*The data.*  The committed results file, `results/optimal.jsonl.gz` at master
[fa05cac](https://github.com/bvchess/taxman/blob/fa05cac/results/README.md) (the run of 2026-11-01, results commit
5bd5d48), gives every game 1-5060 with its moves, its promotions (exactly its moves up to n/2, in every game) and its
method.  The pilot [P1](../the-unsound-mode-on-the-hard-games-2026-11/README.md) gives 126 unsound lines (two seeds on
63 searched games of 3441-5060), with their final promotions but not their start's.  So the starts of P1's 40 games
whose start fell short were played again here at effort 0, the start alone ([run_starts.py](run_starts.py)): each
start scores what both of P1's seeds started at, so it is the same start.

*Words.*  The *seed* of game n is the moves of game n − 1 up to n/2, what a search of n is seeded with (setup keeps the
seed's candidates: all of it in 39 of the 40 games where the candidates were computed).  At a step from n − 1 to n,
the *drops* D are the seed's members that the recorded promotions of n lack, and the *additions* A the promotions of n
that the seed lacks.  A *swap* from an incumbent X, a promotion set of game n, to the recorded optimal set O has the
drops X − O and the additions O − X.  A neighborhood of the search fixes part of X and leaves the rest and every other
candidate free, so it holds O exactly when it frees every drop.

*The frame model in Python* ([board.py](board.py)).  A set of moves is playable exactly when dismantling its own
instance deletes every member ([the core theorem
(P7)](https://github.com/bvchess/taxman/blob/fa05cac/docs/theory/playability.md#the-core-theorem)), and dismantling
splits by layer, since every cycle of a payment scheme lies in one layer ([the flat-cycle lemma
(P3)](https://github.com/bvchess/taxman/blob/fa05cac/docs/theory/playability.md#the-flat-cycle-lemma)).  The promotion
sets of game n are the sets L up to n/2 with U\* ∪ L playable ([the exactness theorem
(X7)](https://github.com/bvchess/taxman/blob/fa05cac/docs/theory/exactness.md#the-exactness-theorem)), with U\* the
recorded game's moves above n/2; every line of P1 and every start studied here plays the same U\*.  So the scripts test
a promotion set exactly, without the solver.  Their candidates, the x with U\* ∪ {x} playable, number what setup counts
on each of the 40 boards where they were computed, and their survivors of the seed of 5060 sum to 570,285, the start
that the entry on [game 5060's start](../the-start-of-game-5060-with-and-without-the-game-before-2026-11/README.md)
records.  The *survivors* of a seed are what [the search's
start](https://github.com/bvchess/taxman/blob/fa05cac/solver/docs/design/search.md#the-starting-incumbent-the-ceiling-and-the-seed)
keeps of it: its candidates that can still be promoted, from the largest down.

*Frames.*  Setup numbers the frames with freedoms by layer and merges those of one layer, so a promotion's frame in the
search is fixed by its layer ([the design, "Setup in the
code"](https://github.com/bvchess/taxman/blob/fa05cac/solver/docs/design/frame-model.md#setup-in-the-code)): a
promotion x of layer k leaves a frame of layer k + 1 and becomes a move of the frame of layer k.  The frame graph
itself gives nothing finer: on the boards of 3552 and 5060 each layer from 2 to 6 is one component holding all but at
most three of its sources.  "One frame" below means one layer; layers 3 to 6 hold 21-24%, 38-39%, 20-21% and 10-11%
of the promotions.

*Random sets.*  To say whether the changes at a step are related more often than chance, the script draws 20 pairs of
random sets of the sizes of D and A for each step: D′ from the seed and A′ from the numbers up to n/2 outside the
seed that some game within 100 of n promotes, a stand-in for the candidates that are often promoted.

*Times.*  The starts ran on 2026-11-06 from 16:19 to 16:28 PST, one game at a time on 2 threads at nice 19, on the
machine of 88 threads that runs the prover at idle priority beside another experiment on 8 threads; 496 s in all.
The scripts ran there the same evening, at nice 19 on one thread each, and made the outputs of this folder between
17:34 and 17:58 PST.

## Results

### 1. How the optimal set changes with n

**Only a searched game changes the set.**  In every one of the 676 primes, 2,131 repeats and 490 games at their ceiling
of 3-5060, the recorded promotions are exactly the seed, as [the step
theorem](https://github.com/bvchess/taxman/blob/fa05cac/docs/theory/neighbors.md#the-step-theorem) allows for the
primes and the ceiling.  Of the 1,749 searched games, 1,668 change the seed and 81 keep it:

| n | searched | no change | D: median, p90, max | A: median, p90, max | D ≥ 5 | D ≥ 10 | promotions, median |
|---|---|---|---|---|---|---|---|
| 2-1000 | 313 | 8 | 1, 5, 12 | 1, 4, 11 | 42 | 3 | 30 |
| 1001-2000 | 352 | 8 | 2, 8, 17 | 2, 8, 17 | 107 | 19 | 87 |
| 2001-3000 | 357 | 15 | 2, 8, 20 | 2, 7, 19 | 94 | 23 | 136 |
| 3001-4000 | 368 | 21 | 2, 9, 19 | 2, 8, 19 | 95 | 29 | 193 |
| 4001-5060 | 359 | 29 | 1, 6, 16 | 1, 5, 16 | 58 | 14 | 237 |
| 3441-5060 | 568 | 43 | 2, 8, 19 | 1, 7, 19 | 117 | 36 | 222 |
| all | 1,749 | 81 | 2, 7, 20 | 1, 7, 19 | 396 | 88 | 140 |

* **A step is a small swap, and never a gain in members.**  The median step drops 2 promotions and adds 1 or 2; one
  in four drops 5 or more, one in twenty 10 or more.  |A| is |D| in 633 searched games and |D| − 1 in 1,116, never more,
  and 518 steps drop one promotion and add none.  The set grows with n only through n/2, which the seed of an even n
  holds as a move of n − 1.
* **The size of the step does not grow with n.**  The medians and the 90th percentiles stay at 1-2 and 5-9 from 1001
  to 5060, while the sets grow from 87 to 237 promotions, so the share of the set that changes falls with n.
* **One optimal set is recorded a game.**  Another optimal set of n, or of n − 1, could be closer, so these counts
  bound the change from above.  It is rare at the n where it was looked for: of the 954 games whose optimal sets were
  enumerated, 30 have more than one, at most three, all in 425-779
  ([uniqueness.md](https://github.com/bvchess/taxman/blob/fa05cac/solver/noframe/docs/uniqueness.md)); and each of P1's
  112 lines that reached the known score holds the recorded set itself.

### 2. Where the changes lie

* **In the lower part of the range.**  All but 0.75% of the promotions of 1001-5060 lie above n/4, and the changed
  ones lie lower than the kept ones: the drops at a median 0.357 n (quartiles 0.32-0.41 n), the additions at 0.349 n
  (0.31-0.39 n), the kept promotions at 0.433 n (0.38-0.47 n), the same in 1001-3440 and in 3441-5060.
* **In the frame where n arrives.**  At an odd n the new source n joins the frame of its layer, and at an even n the
  old source n/2 becomes a promotion into the frame of its layer.  41-49% of the drops lie in that frame, against
  24-29% of the kept promotions; the additions, 23-35%.
* **Near n's largest prime.**  14-20% of the drops and additions are multiples of n's largest prime factor, against 4-8%
  of the kept promotions; 31-45% share a prime of 5 or more with n, against 21-34%.  Divisors of n are rare: at most
  2.2% of the drops and 2.5% of the additions.
* **At an even n, n/2 displaces its own kind.**  13-14% of the drops have the cofactor of n/2 (x over its largest prime),
  against 1-2% of the kept promotions: at 5052, the promotion 2526 = 6 · 421 displaces 2514 = 6 · 419.
* **A smooth n changes more.**  Where n's largest prime is at most 50, the median step drops 3 and 35-37% drop 5 or more;
  where it is above 50, the median drops 1 and 7-11% drop 5 or more.

### 3. What changes together

The drops and additions of one step are related to each other far more often than random sets of their sizes, by a
shared largest prime or cofactor most of all.  A changed promotion is *isolated* under a relation when no other change
of its step is related to it, and a step is *one group* when its changes are connected under it.  Over the 619 searched
steps of 1001-3440 and the 341 of 3441-5060 with two changes or more:

| relation | isolated, 1001-3440: steps, random | isolated, 3441-5060 | one group, 1001-3440 | one group, 3441-5060 |
|---|---|---|---|---|
| one frame (one layer) | 6.1%, 16.3% | 8.3%, 18.8% | 20.4%, 4.6% | 23.2%, 4.9% |
| the same largest prime | 21.6%, 63.0% | 17.7%, 69.7% | 7.3%, 0.4% | 10.3%, 0.6% |
| the same cofactor x/P(x) | 58.9%, 81.5% | 66.9%, 85.4% | 3.2%, 0.2% | 2.6%, 0.2% |
| the same largest prime or cofactor | 12.1%, 50.8% | 11.0%, 58.6% | 32.6%, 0.7% | 40.2%, 0.8% |
| a shared maximal factor | 53.8%, 77.4% | 63.1%, 82.9% | 5.2%, 0.2% | 6.2%, 0.2% |
| a shared prime of 5 or more | 9.8%, 34.8% | 8.0%, 34.4% | 40.1%, 5.3% | 47.8%, 7.5% |
| a shared prime | 0.0%, 1.1% | 0.1%, 1.2% | 99.7%, 93.0% | 99.4%, 92.6% |

* **The largest prime and the cofactor.**  Write a promotion x as c · P, with P its largest prime and c its cofactor.
  The cofactor c is a maximal factor of x, so it can pay for x, and it pays for one move at most among c · P, c · P′,
  …; the promotions with one P are multiples of P, which the frame graph joins through the numbers that P divides.
  Under "the same P or the same c" a changed promotion is isolated in 11-12% of the cases against 51-59% for random
  sets, and 33-40% of the steps are one group against under 1%.  At 3597 = 3 · 11 · 109 the step drops 10 · 109,
  12 · 109, 15 · 103 and 16 · 107 and adds 10 · 103, 12 · 103, 12 · 107 and 16 · 109: the cofactors 10, 12 and 16 move
  between the primes 103, 107 and 109.
* **One frame is a weak tie.**  A frame holds a fifth to two fifths of the promotions, so random sets share one often.

**In the frame model the drops lie in the conflicts that the additions make.**  Add A to the seed and dismantle: what
is left, the residual, is the union of the cores, and a minimal set of members whose removal makes the rest playable
within that instance lies in it ([the exclusion
theorem (P8)](https://github.com/bvchess/taxman/blob/fa05cac/docs/theory/playability.md#the-exclusion-theorem)).  The
*strict region* of A is the seed's promotions in that residual; the *wide region* adds the seed's promotions that are
maximal factors of the residual's members, which, freed, could pay for them.  Over the searched steps with two drops or
more:

| n | steps | D in the strict region | its size: median, share of the seed | D in the wide region | its size | a random D in the wide region |
|---|---|---|---|---|---|---|
| 1001-2000 | 226 | 88% | 31, 0.37 | 100% | 53, 0.67 | 18.2% |
| 2001-3000 | 225 | 78% | 32, 0.24 | 100% | 70, 0.53 | 9.6% |
| 3001-4000 | 220 | 66% | 42, 0.22 | 100% | 87.5, 0.47 | 7.2% |
| 4001-5060 | 166 | 56% | 27, 0.11 | 100% | 72, 0.30 | 4.4% |

Every drop of these steps lies in the wide region, and the drops outside the strict one are payers.  The instance keeps
the seed's promotions out of the pool, and the exclusion theorem's second part, which would put every needed removal in
the residual, holds only for a set none of whose members is a maximal factor of another.  The wide region is the part
of the seed that the swap touches, and it holds a third to two thirds of the seed.

### 4. Does the past predict the next step?

**The changes of the games before point to the next drops, but rarely to all of them.**  Take the promotions that
changed in the last k steps and are in the seed:

| n | k | share of D in them | by chance | lift | all of D in them | their number: median, p90 |
|---|---|---|---|---|---|---|
| 1001-3440 | 1 | 5.2% | 0.9% | 5.7 | 1.4% | 0, 3 |
| 1001-3440 | 10 | 34.0% | 7.9% | 4.3 | 7.8% | 7, 15 |
| 1001-3440 | 50 | 64.6% | 21.0% | 3.1 | 20.4% | 22, 32 |
| 1001-3440 | 200 | 78.2% | 32.8% | 2.4 | 36.0% | 37, 49 |
| 3441-5060 | 1 | 2.0% | 0.2% | 9.7 | 0.6% | 0, 1 |
| 3441-5060 | 10 | 22.0% | 3.4% | 6.4 | 2.5% | 6, 14 |
| 3441-5060 | 50 | 48.9% | 11.7% | 4.2 | 12.2% | 24, 34 |
| 3441-5060 | 200 | 70.5% | 23.0% | 3.1 | 28.0% | 51, 57 |

* **The step before says little.**  The change from n − 2 to n − 1 holds 2-5% of the next step's drops, 6-10 times
  chance, and all of them in about 1% of the steps.
* **The last 50 steps hold half the drops, and all of them in one step of 5 to 8**, freeing a median 22-24 promotions.
  The drops they hold are promotions that those steps added and the step drops again: 3549 adds 1071, 1092, 1120,
  1125, 1134, 1197, 1274, 1377 and 1440, and 3552 drops them all.
* **An earlier game is rarely a better seed.**  The moves of some game n − 2 to n − 20 are closer to opt(n) than n − 1's
  in 70 of 352 searched games of 1001-2000 and 41 of 568 of 3441-5060, by a median of 4 members, and equal to it in
  none.
* **n's factorization predicts the size of the step and where to look**, not which promotions change: a smooth n changes
  more (section 2), and the drops favor n's frame and the multiples of n's largest prime, by factors of 1.6-2.1 and
  2-5.

### 5. The stuck games and the short starts

The incumbents are the 8 *stuck sets* and the 40 *short starts*.  The stuck sets are the final sets of P1's lines that
never held the known score: in 3552, 3723, 3850, 4056, 4104 and 4232 both seeds end at the same set, and 3600 (seed 1)
and 4416 (seed 2) were missed by one seed.  The short starts are the starts of P1's games that fell short; those of
3552, 3723, 3850, 4232 and 4416 are also stuck sets, since their lines never moved.

**A stuck set is a swap of 6 to 13 promotions each way, for a gain of 1 to 97 points.**  D and A have the same size in
all 8, a median of 11, and the gain is a median 54 points.  A short start needs a median of 5.5 drops (3 to 21; 4851's
start, 1,957 short, needs 21), the same number of additions in 39 of 40, for a median gain of 86.

**No relation of numbers makes a stuck swap one group, and its region in the frame model is half the incumbent.**  The
stuck swaps fall into 4 to 8 groups under "the same largest prime or cofactor" and 2 to 4 under "a shared prime of 5 or
more"; 10 and 16 of the 40 short starts are one group.  The strict region of A holds D in 6 of the 8 stuck sets, at a
median 85 promotions (0.43 of the set), and the wide region holds it in all 8 and in all 40 short starts, at a median
159 (0.79) and 131.5 (0.56).  The group that frees a stuck swap is half the incumbent or more, not a dozen promotions.

**The mode's random share almost never frees a stuck swap.**  With 70-90% fixed, the chance that one neighborhood frees
every drop is 6 × 10⁻⁹ to 1.3 × 10⁻⁴ (4416, with 6 drops).  With 50-70% fixed it is 1.4 × 10⁻⁵ to 5 × 10⁻³, with
40-60% fixed 2 × 10⁻⁴ to 1.8 × 10⁻², a round of 64 then holding the swap with chance 0.013 to 0.27, and 0.68 for 4416.
The same computation predicts the pilot: of the 18 short starts to which it gives a chance between 0.05 and 0.5 at the
first round, it expects 5.3 at the known score after it, and P1's seeds brought 9 and 7 there; of the 22 below 0.05,
it expects 0.1, and neither seed brought any.  The model orders the games as the search found them, and its chances
are if anything low.

**Structure helps only at the size of half the incumbent.**  The chance that one neighborhood of at most K freed
promotions frees every drop, as a mean over the incumbents, for K freed at random, for the K nearest in size to one
drawn at random, and for groups grown from the strict or the wide regions of the candidates outside the incumbent
([swaps.py](swaps.py) gives the rules); in brackets, the number of incumbents where it is above 0:

| incumbents | K | random | window of size | grown, strict | grown, wide |
|---|---|---|---|---|---|
| 8 stuck | 60 | 3.4 × 10⁻⁵ | 0 [0] | 0.009 [1] | 0 [0] |
| 8 stuck | 80 | 2.4 × 10⁻⁴ | 0.056 [4] | 0.021 [5] | 0.007 [1] |
| 8 stuck | 100 | 1.2 × 10⁻³ | 0.128 [5] | 0.043 [7] | 0.008 [3] |
| 40 short starts | 40 | 1.5 × 10⁻³ | 0.004 [2] | 0.007 [15] | 0.031 [12] |
| 40 short starts | 60 | 5.7 × 10⁻³ | 0.018 [6] | 0.038 [24] | 0.053 [17] |
| 40 short starts | 100 | 3.2 × 10⁻² | 0.128 [22] | 0.160 [36] | 0.122 [26] |

At 20 or 40 freed promotions no rule frees any stuck swap.  A fixed band of sizes does no better: the promotions from
n/4 to 0.45 n hold every drop of all 8 stuck sets and of 26 of the 40 short starts, but they are 0.61 of the
incumbent; up to 0.42 n, 4 and 18, at 0.43-0.44.

**The start's local search walks away from the optimal set.**  The start is the best of the greedy set, the survivors
of the seed and a rounding of the root's matching, improved by a local search.  Against opt(n), the survivors of n − 1
need fewer drops than the start in 24 of the 40 short starts, as many in 11 and more in 5, a median 4 against 5.5,
though they fall short by a median 1,165 points (3 to 8,538), where the start falls short by a median 86.  At 4104 the
start is 36 short and 8 drops from opt(4104); the survivors of 4103 are 1,256 short and 2 drops from it, so a round of
the default share from them would hold it with chance 0.94, while P1's seeds climbed from the start to 1 short and
stuck 10 drops away.  The survivors of an earlier game are sometimes closer still: those of 4224 are the optimal set
of 4232, which both seeds missed 13 drops away, and those of 3548 are 3 drops from that of 3552 (round chance 0.46),
where the start is 11.  Some survivor gives a better chance at the first round than the start in 27 of the 40, the
survivors of n − 1 in 22 of them.  Over the 40 short starts, a round of 64 from the start and from each distinct set
among the survivors of n − 1 to n − J (a survivor equal to the start or to an earlier one gets no round):

| J | rounds a game, mean (most) | short starts expected at opt(n) | the 6 games both seeds missed |
|---|---|---|---|
| 0, the start alone | 1 | 5.4 | 0 |
| 1 | 1.8 (2) | 12.7 | 0.95 (4104 0.94, 4056 0.01) |
| 2 | 1.9 (3) | 12.7 | 0.95 |
| 4 | 2.3 (4) | 14.4 | 1.41 (3552 0.46) |
| 8 | 3.0 (5) | 16.7 | 2.67 (3552 0.71, 4104 0.94, 4232 1.00, 4056 0.02) |

At the same work the start's own rounds do about as well on the average game: P1's seeds brought 13 and 14 of the 40
to the known score by round 2 and 17 and 20 by round 4.  What the survivors buy is a different basin: 2.7 of the 6
games that the rounds from the start did not reach in 256 rounds.

### 6. The proposal

Both changes keep a neighborhood a function of the incumbent of its trajectory and of draws from the generator of
(seed, n, round, k), as the mode's neighborhoods are now
([finder.rs](https://github.com/bvchess/taxman/blob/fa05cac/solver/frame/src/search/finder.rs), `Lns::neighborhood`).

**1. A share tilted toward the small promotions** ([tilt.py](tilt.py)).  The expected share s freed is 1 less the
share drawn from `--fix`.  Each promotion x is freed with probability min(1, q · w(x)), with q set so that the expected
number freed is s times the promotions, and w(x) a fixed table of the size x/n in ten bins of n/40 from n/4 to n/2
(the few promotions below n/4 take the first bin's weight):

| x/n from | 0.250 | 0.275 | 0.300 | 0.325 | 0.350 | 0.375 | 0.400 | 0.425 | 0.450 | 0.475 |
|---|---|---|---|---|---|---|---|---|---|---|
| w | 4.87 | 4.70 | 3.48 | 2.41 | 1.53 | 1.12 | 0.76 | 0.45 | 0.28 | 0.33 |

The weight of a bin is the share of the drops in it over the share of the seed's promotions in it, over the searched
steps of 1001-3440.  The tests below use none of those steps.  A neighborhood draws one number of its generator for
each promotion, in the order of the promotions, and frees the promotion when the number is below its probability.
Against the uniform share at the same expected share, with each promotion freed independently (the mean chance that one
neighborhood frees every drop, and the geometric mean of the ratio):

| incumbents | share freed | tilted | uniform | ratio | tilted ahead in |
|---|---|---|---|---|---|
| 289 steps of 3441-5060 | 0.2 | 5.5 × 10⁻² | 1.2 × 10⁻² | 13.5 | 236 |
| 289 steps of 3441-5060 | 0.4 | 0.26 | 5.9 × 10⁻² | 10.4 | 230 |
| 8 stuck sets | 0.2 | 3.8 × 10⁻⁴ | 8.3 × 10⁻⁶ | 817 | 8 |
| 8 stuck sets | 0.4 | 5.4 × 10⁻² | 6.2 × 10⁻⁴ | 448 | 8 |
| 40 short starts | 0.2 | 3.5 × 10⁻² | 2.2 × 10⁻³ | 63 | 34 |
| 40 short starts | 0.4 | 0.20 | 2.1 × 10⁻² | 30 | 34 |

* **After one round of 64**, the short starts expected at opt(n) are 15.0 tilted against 4.6 uniform at the share 0.2,
  and 34.0 against 18.8 at 0.4; the stuck sets, 0.2 against 0.0 at 0.2 and 6.0 against 0.3 at 0.4.  At 0.4 the chance
  of a round for each stuck set is 0.999 (3552), 0.36 (3600), 0.20 (3723), 0.66 (3850), 0.95 (4056), 0.90 (4104),
  0.97 (4232) and 1.00 (4416).
* **The size is the feature that carries it.**  Adding the frame where n arrives and the multiples of n's largest
  prime (section 2) to the weights helps the steps (ratio 16.8 against 13.5 at 0.2) and lowers the stuck sets' (431
  against 817), so the proposal uses the size alone.
* **Its size is the share's.**  At 0.2 it frees as many promotions as the default does, at 0.4 as many as
  `--fix 0.5,0.7` does on average: 80 of the 199 promotions of 3552, 106 of the 266 of 5024.  P1 measured the default
  at a median 27 steps a neighborhood and 0.84 ms of a thread a step; what a tilted neighborhood costs, whose freed
  promotions are the small and entangled ones, is not known.

**2. Trajectories from the survivors of n − 1 to n − J** ([swaps.py](swaps.py)).  A game keeps a trajectory from its
start and one from what survives of the moves of each game n − 1, …, n − J, as `--survivors` keeps one from n − 1's
([REFERENCE, "An unsound line"](https://github.com/bvchess/taxman/blob/fa05cac/solver/docs/REFERENCE.md#an-unsound-line)).
A survivor equal to the start or to another survivor adds no trajectory, so J = 8 keeps a mean of 3.0 trajectories
(at most 5) on the 40 short starts.  Neighborhood k works from trajectory k mod T of the T kept, as with `--survivors`.
The survivors are a function of the moves of n − j, which the run has from its own lines (or the file's, or with
`--from-known` the table's), so no draw is added.  Section 5 gives each trajectory a round of 64; with the 64 shared,
the same work takes T rounds.  At J = 8 it holds 2.7 of the 6 games both seeds missed, against 0, and on the other
games it does about as well as the start's own rounds of the same work, so it costs them little; the trajectories
could also begin only once the start's has stalled.

**Not proposed.**  Neighborhoods that free a group joined by a relation of numbers, a window of sizes or a group grown
through the cores of the candidates: they free the stuck swaps only at 80 to 100 promotions, and then less reliably
than the tilted share at the same size (the window frees none of 3600, 3723 and 4104 at 100, while the tilted share
at 0.4 frees each stuck swap with chance 3.4 × 10⁻³ or more).  A seed from an earlier game in place of n − 1's: an
earlier game is closer to opt(n) in at most 20% of the steps (section 4).

## Decision

No code changed.  Both changes go to the unsound mode as proposals, to be tested on P1's 13 games before a run of the
whole machine: the tilted share at expected shares of 0.2 and 0.4 against the uniform share at the same, recording the
steps of each neighborhood; and the trajectories from the distinct survivors of n − 1 to n − 8.  The neighborhoods of
section 5 that this entry does not propose would be worth a test if a neighborhood of 80 to 100 freed promotions
proved cheap.

## What the data cannot tell

* **One optimal set is recorded a game**, so every swap is to that set (section 1).  That P1's lines found the recorded
  set each time says that at these n it is unique or that the search prefers it, not which.
* **The frames are the layers.**  The script computes no frame of setup's, only the layer of each number, which fixes
  its frame in the search; the merged frame of a layer is one block, so "one frame" is a coarse relation by
  construction.
* **The random sets stand in for the candidates** by the numbers promoted within 100 games; the true candidates are
  four to five times as many, mostly never promoted, and would make chance smaller still.
* **Containment is not success, and the first round is not the last.**  A neighborhood that frees every drop holds the
  optimal set, but its search may stop at its limit of 1,024 steps first.  A round that misses the swap can still move
  the incumbent, and nothing here says where: the chances are for the first round from the incumbent named.
* **The cost of a neighborhood is not measured.**  It is a size in promotions here; how a search's steps grow with the
  freed promotions, and whether a connected group costs more than as many scattered ones, needs the solver.
* **Sample sizes.**  The stuck sets are 8, one a game: the 6 games both seeds missed and one more of each seed.  The
  short starts are 40 games of 3465-5024, the steps every searched game.  The tilted share was fitted on one stretch
  and tested on the next; its gain on the stuck sets rests on 8 sets.
* **The starts are the same by their score.**  Each start of starts.jsonl scores what P1's seeds started at, and the
  code of the start did not change from P1's build (e37d6a1) to this one (fa05cac); P1's lines do not record the
  start's set to compare.

## Files

The scripts read the results file that `TAXMAN_RESULTS` names, else `results/optimal.jsonl.gz` of the main repository
whose checkout holds this notebook at `solver/notebook/`.  Each ran on one thread at nice 19 with `python3 -I -B`.

* [board.py](board.py): the number tables, the playability test by dismantling, the promotion sets, candidates and
  survivors of a game, and the frame graph by layer; the other scripts import it.
* [steps.py](steps.py): sections 1 to 4.  `nice -n 19 python3 -I -B steps.py > steps-out.txt` (about 90 s);
  [steps-out.txt](steps-out.txt) is its output, and [steps.json](steps.json) the drops and additions of every searched
  game, which it writes.
* [run_starts.py](run_starts.py): plays the 40 short starts at effort 0, one game at a time, appending to one file, so a
  rerun resumes.  `nice -n 19 python3 -I run_starts.py --bin TAXMAN --p1 ../the-unsound-mode-on-the-hard-games-2026-11
  --out starts.jsonl --log starts.log`; [starts.jsonl](starts.jsonl) holds the 40 unsound lines (with the moves and
  the promotions) and [starts.log](starts.log) the commands and their summary lines.
* [swaps.py](swaps.py): section 5 and the survivors of section 6.  `nice -n 19 python3 -I -B swaps.py
  ../the-unsound-mode-on-the-hard-games-2026-11 > swaps-out.txt` (about 10 minutes, and 10 more on a first run, which
  computes the candidates); [swaps-out.txt](swaps-out.txt) is its output, and [candidates.json](candidates.json) the
  candidates of the 40 games, which it writes on a first run and reads after.
* [tilt.py](tilt.py): the tilted share of section 6.  `nice -n 19 python3 -I -B tilt.py
  ../the-unsound-mode-on-the-hard-games-2026-11 > tilt-out.txt` (about 60 s); [tilt-out.txt](tilt-out.txt) is its
  output.

No code of the main repository changed.  The code run is that of commit
[fa05cac](https://github.com/bvchess/taxman/commit/fa05cac).
