# How many best-known games past 5060 are short (2026-11)

Part of the [lab notebook](../README.md).

Started 2026-11-11.  Concluded 2026-11-11.

**Question.**  How many of the 4,940 best-known games past 5060 (5061 to 10000) score below opt(n), measured with no
statistical model and with a confidence bound?

**Answer.**  About 193 are short, and with 95% confidence at most about 573.  So at least 88% of the 4,940 games are at
opt(n), and the central estimate is about 96%.  Two pieces of work give it.  An audit found that every best-known game
agrees with every proved relation, so a short streak can start only at one of 1,559 *target* games, the games that no
proved relation settles from the game before.  A stratified sample of 262 targets, one fresh play each, raised one.

The claim matters because the unsound mode's objective is to play excellent games to 10000 and to claim that most of
them are optimal, and proofs past 5060 are dear: the first, of 5260, took 78.5 CPU-hours
([the first proofs past 5060](../the-first-proofs-past-5060-2026-11/README.md)).  The statistical model that made the
claim before this entry failed its held-out check on the proven games, so this entry measures it instead.

## Method

### The words

*Best-known, short, streak, root.*  Past 5060 each game has a *best-known* score, the highest score the unsound mode has
found, with no proof.  It is a lower bound of opt(n).  A game is *short* when its best-known score is below opt(n).  A
*streak* is a run of consecutive short games, and its *root* is its lowest game: a short game whose game below is not
short.

*Settled, target.*  A proved relation can fix the score of game n from the score of game n − 1: the prime formula, the
repeat lemma, the half lemma, the ceiling, the 8p and 12p theorems and the semiprime formula are the ones used.  Then
game n is optimal whenever game n − 1 is.  So a short game is either a root or lies in a streak that a root started,
and a root can only be a game that no proved relation settles.  Those games are the *targets*.

*Play, level, seed.*  A *play* is one run of the unsound mode on one game.  Its *level* sets how much work it does
(level 4 stops at 2⁴ × 65,536 units of work; [what a level of effort
is](https://github.com/bvchess/taxman/blob/287486e/solver/docs/unsound/play.md#the-level-of-effort)), and its *seed*
sets its random choices.  A play *raises* its game when its score is above the best-known score the game had before.

*Rehearsal, detection chance.*  A rehearsal runs the unsound procedure on the proven games 3001 to 5060 as if they were
unknown ([the rehearsal on the known range](../search/the-rehearsal-on-the-known-range-2026-11/README.md)).  Its short
games and roots are then known exactly, since opt(n) is proven.  The *detection chance* d is the chance that one fresh
play raises a root.

### The audit

The audit checks every game from 5061 to 10000 against every relation between neighboring games that applies to it.  It
replays each recorded line by the rules of the game first, so a best-known score is always the score of a legal game.
A relation has one of three shapes, and each says something different when a best-known score breaks it.  Write A and B
for the best-known scores of games n − 1 and n (opt where a game is proven):

* an *equality*, opt(n) = opt(n − 1) + n − c, says that n is short if B − A is below n − c, and that n − 1 is short if
  it is above;
* an *upper bound*, opt(n) ≤ opt(n − 1) + n − c, can only say that n − 1 is short;
* a *lower bound*, a game of n built from a game of n − 1 or of a later game, can only say that n is short.

The relations are of two kinds.  Fifteen are proved, some given statement U, and [audit/README.md](audit/README.md)
says for each where it is proved and which hypotheses the audit checks game by game.  Eleven are conjectured laws that
fit the proven games: the exchange law, six cofactor laws (for the cofactors 8, 12, 16, 20, 24 and 40), the cofactor
rule for 9P, and three forms of the clean-window parity form that [the loop
principle](../the-loop-principle-and-game-5061-2026-11/README.md) studies.  A proved relation's row names a game that is
certainly short.  A law's row names a game that is short if the law holds, and the game is then a target for the miner,
or a counterexample to the law.

### The sampling test

*The estimate in one line.*  The share of targets that one fresh play raises, divided by the chance d that a play
raises a root, estimates the roots, and the lengths of streaks turn roots into short games.

*The calibration of d.*  The rehearsals' short games, rebuilt from their append-only best-known files, give the roots
after pass 2 and after pass 3 of each of three rehearsals (R1, R2, R3).  Each root was played again, alone, into a fresh
copy of its state's best-known file: the 8 roots after pass 3 at levels 2, 3 and 4 on seeds 71 to 76 (144 plays), the
14 roots after pass 2 at level 4 on seeds 71 to 74 (56), and the 7 followers after pass 3 that are searched games below
their ceiling, as targets are (4136 and 4137 in each state, 4230 in R2), at level 4 on seeds 71 to 74 (28): 228 plays.
Seeds 71 to 76 had been used by no earlier play.

*How the rehearsals differ from the targets, and what the estimate does about each difference.*

* **Larger games.**  A level's work is fixed while a game's promotion candidates grow about as n, so a level-4 play at
  9,000 searches each candidate about as long as a level-3 play at 4,500.  A target of game n is given, for each root
  i, the chance at the level 4 − log₂(n / nᵢ), interpolated between the levels played and clamped to 2 to 4
  (*size-matched*).
* **More search before the test.**  The rehearsal roots had three passes, and the targets had two or three passes and 0
  to 6 dedicated plays.  A root that survived m plays is more likely a hard one, so the roots are weighed by their
  chance to have survived a target's earlier plays (*after prior plays*).
* **Few roots.**  8 instances on 6 games, 3 of them 4134, which no play of any level has reached.  The intervals
  resample the instances, so the mix of easy and hard roots is part of the interval.
* **A target inside a streak.**  The 7 followers measure how much less a target that is not a root yields: ρ times a
  root's rate.

*The sample.*  The frame is the 1,559 targets of the audit as written at 07:20.  They were put in four strata by their
dedicated plays so far (0, 1, 2, 3 or more) and drawn with proportional allocation: each stratum was put in a random
order (seed 20261111) and the strata were interleaved, so that the first k targets of the order hold each stratum in
proportion to its size, for every k.  Each target got one level-4 play on seed 71, which no play past 5060 had used, at
idle priority on 12 threads, into the shared best-known file.  No sample play was started after 11:30, a time fixed
before the run began, so the plays reached are a stratified random sample whatever they found.  A gain was pushed down
(the 8 games below it at level 3) and carried up (windows of 20 at level 3 while the top game of a window rose).

*The interval.*  A Monte Carlo resamples the 8 roots with replacement, draws each root's chance at each level from its
Jeffreys posterior, draws the roots from their posterior under a flat prior on 0 to 1,559, and draws their streak
lengths from the 31 streaks found past 5060 by single-game plays.  The 95% upper bound is the 95th percentile of the
draws.  A second reading (Bonferroni) divides the exact hypergeometric 97.5% upper bound on the raisable targets by
the 2.5% quantile of d.

## Results

### What the audit found

**Every best-known game past 5060 agrees with every proved relation.**  The audit read the best-known file once, at
07:54 on 2026-11-11 (6,907 lines), and finished at 07:57 in 162 s.

| relation | what it says | applies to | met with equality | short |
|---|---|---:|---:|---:|
| N3 | a game of n − 1, extended, is a game of n | 4,940 | 1,944 | 0 |
| N4 | the ceiling: opt(n) ≤ opt(n − 1) + n | 4,940 | 1,703 | 0 |
| N5 | the prime formula | 552 | 552 | 0 |
| N6 | a game of n − 1 that stays playable with n added reaches the ceiling | 1,712 | 1,709 | 0 |
| N7a, N7b | the half lemma, read on the line (N7b: on U\*, given U) | 1,118 | 1,118 | 0 |
| S1 | the single-loss rule | 3,241 | 2,238 | 0 |
| R6 | the repeat lemma, part 1 | 3,369 | 3,369 | 0 |
| J3 | the semiprime formula | 948 | 948 | 0 |
| L2 | the 8p theorem | 89 | 89 | 0 |
| L4 | the 12p theorem, given U | 63 | 63 | 0 |
| PROJ | the moves of a recorded game of N that are at most n are a game of n | 4,939 | 0 | 0 |
| PROVEN | the proven games 5260 to 5264 | 5 | 5 | 0 |
| W1 | the parity bound: opt(n) ≤ PB(n) | 4,940 | 0 | 0 |
| STRUCT | an optimal game opens with q(n), plays no other prime and, from 187, no number of layer 2 up to n/2 | 4,940 | 0 | 0 |

The proved relations name no game as certainly short, with or without statement U, and no proven game or proved bound
contradicts a best-known score.  The projection of every recorded line of every game N onto every smaller game beat no
best-known score, whatever the window N − n.  L4's hypothesis (8p, 8r, 12r and some 8t in U\*(n)) was met at every one
of its 63 games.  The relations are linked at
[neighbors.md](https://github.com/bvchess/taxman/blob/287486e/docs/theory/neighbors.md) (N3 to N7),
[arrival.md](https://github.com/bvchess/taxman/blob/287486e/docs/theory/arrival.md#the-semiprime-formula) (J3),
[below-the-ceiling.md](https://github.com/bvchess/taxman/blob/287486e/docs/theory/below-the-ceiling.md) (L2, L4) and
[search-rules.md](https://github.com/bvchess/taxman/blob/287486e/docs/theory/search-rules.md#the-repeat-lemma) (R6).

**Only the clean-window flags disagree.**  Every conjectured law that is not the clean-window parity form is met with
equality at every game it applies to:

| law | applies to | met with equality | short |
|---|---:|---:|---:|
| EXL, the exchange law | 1,158 | 1,158 | 0 |
| FAM8, FAM12 | 89, 63 | 89, 63 | 0 |
| FAM16, FAM20, FAM24, FAM40 | 44, 36, 20, 11 | 44, 36, 20, 11 | 0 |
| COF9, n = 9P is at its ceiling | 84 | 84 | 0 |
| CWEQ, the parity form at depth 3 | 408 | 404 | 4 |
| CWEQ2, at depth exactly 2 | 121 | 100 | 21 |
| CWINEQ, the inequality at depth 2 or more | 529 | 504 | 12 |

The 37 rows of [audit/disagreements.csv](audit/disagreements.csv) are those three relations and no others (4 of CWEQ,
21 of CWEQ2 and 12 of CWINEQ), and name 25 games that would be short if the laws held, 7 of them by 100 or more.  The
largest are 6573 and 6657 (at least 764), 6153 (568), 5943 (496), 5061 (492), 9339 (366) and 8243 (144).  The four rows
of CWEQ say that 5943, 6657 and 9510 are short, by at least 496, 764 and 20, and that 9139 is short by at least 1.  A
row of a conjectured law is a target for the miner, or a counterexample to the law.  What the plays of the flags found
is in [the loop principle](../the-loop-principle-and-game-5061-2026-11/README.md).

**The targets.**  1,559 of the 4,940 games have a best-known score that no proved relation determines from the game
before: 943 half-in steps (relaxations), 432 added steps (restrictions) and 184 exchanges, by the names of [the
parity steps](https://github.com/bvchess/taxman/blob/287486e/docs/theory/parity-bound.md#the-parity-steps).  The other
games are settled, each by the first of these that holds: the prime formula for 552, the half lemma for 1,118, the
ceiling for 585, the 8p and 12p theorems for 89 and 63, the semiprime formula for 948 and the repeat lemma for 26.  By
the dedicated plays they had had when the audit ran, 493 of the targets had had none, 547 one, 88 two and 431 three or
more.  41 games had been raised by a dedicated play (3,545 points in their largest raises), and 26 disagree with a
conjectured law.

**The checks of the inputs.**  All 6,913 recorded lines of the games 5060 to 10000 replay legally with the score
recorded, and the highest-scoring recorded line of each of the 4,941 games is over.  The sum of U\* in each of those
lines equals the gap dashboard's at every game, the step kinds agree with the succession study's at every game, and the
dashboard's parity bound obeys PB(n) ≤ PB(n − 1) + n and the prime step at every game.  The miner's root problems agree
with the arrival lemma's J2 at 1,248 games and with the half law at 2,470, and none differ
([audit/consistency.csv](audit/consistency.csv) holds only its header).  `selftest.py` plants a defect in a copy of a
best-known line (a game with one move left out is a legal game a few points lower) and checks that the audit lists the
game under the relation that applies; its output was not kept.

### The calibration: the chance d

Fresh plays of the rehearsal states' roots, raised over plays:

| roots | level 4 | level 3 | level 2 |
|---|---|---|---|
| after pass 3, 8 instances on 6 games | 17/48 = 0.35 (exact 95% 0.22 to 0.51) | 12/48 = 0.25 | 8/48 = 0.17 |
| the same without 4134's 3 instances | 17/30 = 0.57 | 12/30 = 0.40 | 8/30 = 0.27 |
| after pass 2, 14 instances | 29/56 = 0.52 | | |
| followers after pass 3 (4136, 4137, 4230) | 3/28 = 0.11 | | |

* **By root at level 4:** 3844 6 of 6, 5060 4 of 6, 3311 3 of 6, 3549 3 of 6, 4225 1 of 6, 4134 0 of 18.  Every raise
  reached opt(n) at level 4.
* **The passes leave the hard roots:** after pass 2 a play raises a root with chance 0.52, after pass 3 with 0.35.
* **The survivor test** ([the games every level-3 run
  misses](../search/the-games-every-level-3-run-misses-2026-11/README.md)) played the same 6 games at level 4 from the
  proven line of n − 1 and reached opt(n) in 8 of 18 plays, 0.44 a play against 0.47 here, but not game by game (3844: 0
  of 3 there, 6 of 6 here), so the two are not pooled.
* **Followers yield at ρ = 0.30 times a root's rate** (95% 0.15 to 1.00, capped at 1).  Only 4136, short by 31 more than
  the game below it, ever rose; 4137 and 4230, short by exactly what the game below them is, never did.

For the targets past 5060, the mean over the frame of one play's chance, with the 95% interval of the Monte Carlo
draws:

| reading | d |
|---|---|
| level 4 as played | 0.354 (0.23 to 0.65) |
| size-matched | 0.262 (0.16 to 0.55) |
| size-matched and after each target's prior plays | 0.157 (0.13 to 0.39) |
| the same, roots thinned by those plays | 0.177 (0.14 to 0.46) |

By dedicated plays so far (0, 1, 2, 3 or more) the last reading is 0.27, 0.15, 0.09 and 0.05: a root that has survived
three plays is most likely of 4134's kind.

### The sample

262 of the 1,559 targets were played (85 of 503 never played, 92 of 546 played once, 13 of 82 twice and 72 of 428 three
or more times), in 208 thread-hours at 238 s a play, on a machine shared with other experiments (load 80 to 112).  The
calibration took 43 thread-hours.  The run went from 07:27 to 11:33.

**One target rose: 5796.**  It was in the stratum of three or more plays (three earlier level-4 plays on seeds 41 to
43), and its play raised it by 54.  It is a root, since the 8 games below it did not rise, and its carry raised 5797 to
5807: a streak of 12 games and 1,627 points ([gains.tsv](sampling/gains.tsv)).  No other target rose, and none had been
raised by another play before its own.

### The estimate

A streak with kₛ targets is raised by the sample with expected count f·d·Dₛ, where f = 262 / 1,559 = 0.168 and Dₛ = 1 +
(kₛ − 1)ρ.  The detection mass M, the sum of the Dₛ, is Gamma(k + 1) with rate f·d under a flat prior, k = 1.  Streaks
and games are M times the streaks and games per unit of D of a pool of streaks.  The pool is the 31 streaks found past
5060 by single-game plays (30 of the root-first pilot's and 5796's; mean 15.65 games, median 6, largest 102), each
weighed by 1/Dₛ since a single-game play finds a streak in proportion to Dₛ; or the rehearsals' 8 streaks after pass 3
(mean 4.25 games, largest 7).

The reading fixed before the last plays came in was d size-matched and after prior plays, every target alike, ρ as
measured, and the found streaks.  The others show how far the claim leans on each choice:

| reading | streaks | streaks, 95% upper | short games | short games, 90% upper | short games, 95% upper |
|---|---:|---:|---:|---:|---:|
| **the reading above** | **25** | **81** | **193** | **459** | **573** |
| the same, roots thinned by the plays | 22 | 73 | 172 | 412 | 521 |
| the same, the rehearsals' streaks | 30 | 97 | 127 | 323 | 405 |
| the same, ρ = 1 (followers yield as roots do) | 19 | 68 | 107 | 300 | 376 |
| the same, ρ = 0 (only roots yield) | 38 | 130 | 592 | 1,690 | 2,161 |
| d size-matched, no history | 15 | 60 | 116 | 333 | 425 |
| d level 4 as played | 11 | 45 | 86 | 257 | 317 |

* **Read stratum by stratum,** each stratum's raises over its own d: the one raise, in the stratum of three or more
  plays where d = 0.049, stands for a detection mass of 122 and 622 games, and the strata with no raise give 0.  The two
  strata of targets played at most once (1,049) have 0 raises in 177 plays, and their 95% upper bound is 508 games.
* **Bonferroni:** at most 30 raisable targets in the frame (exact, 97.5%) and d ≥ 0.137 (97.5%) give M ≤ 219.
* **The model's claim, for comparison:** 88 short games (22 to 260).

### The claim

With 95% confidence at most about 570 of the 4,940 best-known games past 5060 are short, so at least 88% are at
opt(n), and the estimate is about 190 short games (96% at opt(n)) in about 25 streaks.  It assumes:

1. Every short game past 5060 lies in a streak that starts at a target.  This is proved: the rules settle every other
   game from the game below it.  L4 and N7b rest on statement U, and J3, L2 and L4 on the finite part of the square
   theorem.
2. The sample is a stratified random sample of the targets.  It is by design; its stop was a clock time.
3. A root past 5060 yields to one fresh level-4 play as the rehearsals' 8 roots after pass 3 do at the level with the
   same work per promotion candidate, thinned for the target's earlier plays.  This carries over the rehearsals' mix, in
   which 3 of 8 instances (1 of 6 games, 4134) yield to no play.  Roots of that kind are counted only through that
   share, and no sampling at level 4 sees them.
4. A target inside a streak yields at 0.30 times a root's rate, which rests on 3 games.
5. The streaks are like the 31 found past 5060.
6. The roots are spread over the strata like the targets.  Read stratum by stratum, the one find makes the estimate
   about 620.

The sensitivity table shows what each of the choices behind assumptions 3 and 4 moves: the 95% upper bound runs from 317
games (d as played) to 2,161 (ρ = 0, which counts only roots and credits no yield to a target inside a streak), against
the 573 of the reading fixed in advance.

## Why the claim moved off the statistical model

The unsound mode's previous claim came from model M1 of which best-known scores are optimal, in its version v3c, fitted
on the plays up to 04:43 on 2026-11-11.  It said that 88 games (22 to 260) are short and 98.2% (94.7% to 99.6%) are
optimal.  This test moved the claim off the model for one reason: the model's corrections do not carry over to the
proven games, where the truth is known.

v3c was held out on the proven range, 3001 to 5060, by rebuilding the pieces of its parent model M1 v2 without each
block of 250 games and predicting each rehearsal's state after each pass.  Summed over the range, as the mean of the
three rehearsals, v3c expected too many short games at every pass:

| after pass | v3c's short games | short games there were | ratio | M1 v2's short games, held out |
|---|---:|---:|---:|---:|
| 1 | 416.1 | 45.7 | 9.1 | 46.8 |
| 2 | 192.8 | 16.0 | 12.1 | 18.5 |
| 3 | 29.5 | 11.3 | 2.6 | 11.6 |
| 4 | 20.4 | 11.0 | 1.9 | 8.3 |

So v3c expected 1.9 to 12.1 times the short games there were, and 1.7 and 1.4 times the roots after passes 3 and 4.
Most of the excess is one factor, f, which v2 fitted to production's labels past 5060, where production's passes left
about 3.8 times the roots that v2's root model, fitted on 3001 to 5060, predicts.  Without f, v3c expects 2.8 and 2.9
times the short games after passes 1 and 2 and 0.54 and 0.37 times after passes 3 and 4, so no reading is calibrated at
every pass, while M1 v2's own held-out predictions came within 0.75 to 1.16 of the truth.  The check does not test v3c's
claim past 5060, whose parameters come from the plays there.  It shows that v3c's corrections belong to the state they
were fitted on, and v3c's earlier version v3b had already been wrong past 5060 (from the state of v2 at n ≤ 8480 it
expected 0.73 finds and the plays made 5).

The two claims overlap: the sample's estimate of 193 lies inside the model's 22 to 260, and the sample's 95% bound of
573 reaches past it.  The sample's bound rests on a calibration of 8 roots, and the model's on corrections fitted to the
state of the plays.

## Limits

* **One raise.**  The estimate rests on 1 raised target of 262, and its interval on a calibration of 8 roots on 6 games.
* **Three of the 8 calibration instances are one game.**  4134 yields to no play of any level, so the share of such
  roots past 5060 is the share the rehearsals show, and a sample at level 4 cannot see them.
* **The rehearsal roots have had three passes.**  The targets have had three passes up to 8660 and two above it, besides
  the push-downs and 0 to 6 dedicated plays.  Above 8660 the after-pass-3 mix is harder than theirs, so the calibration
  errs low on d there, and high on the count.
* **The audit does not see** J1's closed frames for games with three or more prime factors (the frame model is not
  rebuilt there), games built from a line of m < n − 1 by repeated N3, and root problems whose digests differ.  The
  proofs of the chain past 2531 rest on statement U, so a relation that speaks for the proven game 5060 inherits that.
* **A relation constrains neighbors only.**  A stretch of games that are all short by the same amount, or short in step
  with a law, passes every row.
* **The plays are one level and one seed.**  Targets that three plays of other seeds did not raise may yield to a
  higher level, which this test did not measure.

## Decision

The claim is the one above, and it replaces the model's 98.2%: at least 88% at opt(n) with 95% confidence, about 96% by
the central estimate.  The audit's list of targets is the frame for any later sample.  The audit and the sample change
no code and no rule of the miner.

What would tighten it:

* **More plays per target.**  The bound scales as 1/(f·d).  One more level-4 play of every target (about 17 hours on 72
  threads at the load of 2026-11-11) makes f = 1, and would put the 95% bound near 150 games if it raised nothing new.
* **A larger d.**  A level scaled to the game's size would recover the size match's loss (0.35 against 0.26), and a
  level-5 play would raise d further, which was not measured.  The heavily played targets, where d is 0.05, need several
  seeds or a higher level to be seen at all.
* **More roots in the calibration.**  The share of roots that no play reaches (4134) sets the history adjustment.  Two
  or three more rehearsal replicates (about 280 thread-hours each), or rehearsals of 2001 to 3000, would measure it on
  more than one game, and ρ rests on 3 games.
* **A proved rule for another family** takes its games out of the targets, as the 8p and 12p theorems took 152
  ([settling game n from the game before](../settling-game-n-from-the-game-before-2026-11/README.md)).

## Files

The work ran in the lab folders `lab/work/audit/` and `lab/work/sampling/`, which these files are, with their paths as
they were there.  The scripts use the standard library but `analyze.py`, which needs the lab's statistics environment
(`../stats-venv/bin/python`).  `audit.py` imports the loaders and the peel from `common.py` of the succession study,
which [its entry](../settling-game-n-from-the-game-before-2026-11/common.py) holds.  They read the best-known file, the
proven chain, the gap dashboard's `games.csv` and the play ledgers, which are not copied.

* [audit/](audit/):
  * [README.md](audit/README.md): what each relation is, where it is proved, how a disagreement is read, and what the
    audit does not see.
  * [audit.py](audit/audit.py) → [summary.txt](audit/summary.txt), [disagreements.csv](audit/disagreements.csv),
    [targets.csv](audit/targets.csv) and [consistency.csv](audit/consistency.csv) (empty but for its header): about
    three minutes, `nice -n 19 python3 -I audit.py`.
  * [selftest.py](audit/selftest.py): `nice -n 19 python3 -I selftest.py`, about three minutes.
* [sampling/](sampling/):
  * [README.md](sampling/README.md): the design, as fixed before the run, and the results.
  * [calib/make_states.py](sampling/calib/make_states.py) → [calib/roots.csv](sampling/calib/roots.csv), and
    [calib/jobs.csv](sampling/calib/jobs.csv): the calibration's states and its 228 jobs.
  * [frame/targets.csv](sampling/frame/targets.csv): the frame, a copy of the audit's targets as written at 07:20 (the
    audit's own file here is the run of 07:54, so the two differ in the plays and raises since).
  * [draw.py](sampling/draw.py) → [sample-order.csv](sampling/sample-order.csv): the order of the sample, seed 20261111.
  * [run.py](sampling/run.py) → [run.log](sampling/run.log) and [sample.tsv](sampling/sample.tsv): one row a sample play
    (order, n, stratum, the frame's best-known score, the known score when the play began, its score, gain, seconds,
    time).  [gains.tsv](sampling/gains.tsv): the one gain and the games its descent and its carry raised.
  * [analyze.py](sampling/analyze.py) → [analyze-out.txt](sampling/analyze-out.txt): every number of the estimate.

Not copied: the production best-known file (137 MB), the rehearsal states of `calib/states/` (130 MB), the 228
calibration plays `calib/plays/` (3.7 MB) and the 528 run files and logs of the sample plays `plays/` (6.9 MB), all in
the lab folder `lab/work/sampling/`; the empty `projections.jsonl` and `constructions.jsonl` of the audit, which hold
the games that a projection or a construction raised (there were none); and the build `taxman-aeffc29`.  The model's
files, with its README, are in `lab/work/gapdash/model/v3c/`.

## Commits

No code changed.  Every play ran the build of master [aeffc29](https://github.com/bvchess/taxman/commit/aeffc29)
(`taxman-aeffc29`, a clean build), and rehearsal 1 ran bd6381b, whose solver code is aeffc29's.  The relations the audit
reads are those of the theory at master
[287486e](https://github.com/bvchess/taxman/commit/287486e).  The commit that adds this entry also adds its rows to
[the register's file of the unsound mode](../register/unsound-mode.md).
