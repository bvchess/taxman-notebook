# The loop principle and game 5061 (2026-11)

Part of the [lab notebook](../README.md).

Started 2026-11-11.  Concluded 2026-11-11.

**Question.**  Is one mechanism behind the shortfall of a searched game, the points by which opt(n) falls below its
ceiling, so that a precise principle can be stated, proved for more than the 8p and 12p families, and used to settle
game 5061, the first game past the proven chain, whose best-known score the parity bound says may be short by 492?

**Answer.**  One part is proved, one is measured, and the proofs of the rest failed.  The proved part is a formula for
how the parity bound moves from game n − 1 to game n (Theorem A, now W4 to W6 of [the parity-bound file on
master](https://github.com/bvchess/taxman/blob/287486e/docs/theory/parity-bound.md#the-parity-steps), commit
[287486e](https://github.com/bvchess/taxman/commit/287486e)): the gap between the parity bound and opt(n) changes only
at relaxations and restrictions, and at an exchange only if the exchange law fails.  The measured part is the principle,
that in a window clean to depth 3 the gap does not change, true at all 126 relaxations and restrictions of the chain
from 187 and at 234 of the 238 past 5060.  The proofs failed in two ways.  The family tables, which would prove the
family laws as the 8p and 12p theorems do, settle games only under an extra hypothesis, that some optimal set of the
game lies in a closed state of the table, and only 8P has no open state.  The gluing route to 5061 fails even at the
proven games 3297 and 3507, because it needs a payment-scheme argument that no table supplies.  The owner parked 5061
pending [the study of 5060's proof](../search/where-a-proofs-work-goes-the-small-primes-and-the-gap-2026-11/README.md),
and the 40P table (E17) was never built.

The principle matters because a rule that proves a game from the game before it turns "probably optimal" into
"optimal if the game before it is", at a cost of seconds and not of CPU-hours.  The proven chain spent 10,149 CPU-hours
on 1,745 searched games, and the best-known games past 5060 cannot be proved at that price.  Game 5061 is the test: its
best-known score is either optimal, and the gap to the parity bound rises by 492 at the first game past the chain, or
short.

## Method

### The words

*The shortfall, the gap, the rise.*  The *shortfall* of game n is δ(n) = opt(n − 1) + n − opt(n), the points by which
its best score falls below its *ceiling* ([settling game n from the game
before](../settling-game-n-from-the-game-before-2026-11/README.md) defines the game, statement U, U\*, optimal sets and
the single-loss rule).  The *parity bound* PB(n) is an upper bound of opt(n) computed from the numbers' parity
vectors, with no search ([the parity
bound](https://github.com/bvchess/taxman/blob/287486e/docs/theory/parity-bound.md#the-parity-bound)).  Its *gap* is
gap(n) = PB(n) − opt(n), its own shortfall is δ_PB(n) = PB(n − 1) + n − PB(n), and the *rise* is rise(n) = gap(n) −
gap(n − 1) = δ(n) − δ_PB(n).  At a game with rise 0 the parity bound's increment is the game's.  Past 5060, opt(n) is
replaced by the best-known score, so a rise there says that a score is short only if the law that predicts it holds.

*Greedy basis and the span conjecture.*  The *greedy basis* G(n) of the sources' vectors keeps, going down the sources,
each whose vector is not a sum of those kept ([the greedy-basis
proposition](https://github.com/bvchess/taxman/blob/287486e/docs/theory/parity-bound.md#the-greedy-basis-proposition)).
G(n) = U\*(n) exactly when the [span
conjecture](https://github.com/bvchess/taxman/blob/287486e/docs/theory/sources.md#the-span-conjecture) (♦) holds in game
n, which the prover has checked at every game to 100,000.  Q\*(n) is the largest total of numbers up to n/2 that are
independent at both parities together with G(n), so PB(n) = ΣG(n) + Q\*(n).

*Three kinds of step.*  The succession study's names for them are used in the work: a *relaxation* is an even n whose
half n/2 was in U\*(n − 1), a *restriction* is an odd n that adds n alone to U\*, and an *exchange* is an odd n that
displaces one source x, the shadow of n.  The theory's names are half-in, added and exchange step.  An even n whose half
was not in U\* is a *half-out* step.

*The exchange law.*  At every exchange step δ(n) = x, the shadow.  The previous entry could not prove it.

*Columns, cells, hubs, depth.*  Write P for the largest prime of n, c = n/P for its cofactor, and P₁ > P₂ > … for the
primes below P.  A number whose largest prime is P_j is the *cell* k·P_j, in *row* k of *column* j.  A cell lists its
column factors, the cells k/q · P_j for the primes q dividing k, and its *hub*, the row number k, which every cell of
row k lists.  A hub pays for at most one move, so hubs are the one resource that columns share.  The window of n is
*clean to depth d* when (c + 1)·P_i > n for every i from 1 to d, so that the d columns below n's hold exactly the rows
1 to c, as n's does.  The depth is computed from n's factorization alone.

*The change, the pattern, the family law.*  Between the recorded optimal sets of n − 1 and n, D is the set of moves
given up and A the set taken up besides n, so δ(n) = ΣD − ΣA.  When every member is a cell of a column within twelve
primes of P, the lists of cells are the change's *pattern*, a formula in P, P₁, P₂, … that can be evaluated at any n of
the same cofactor.  A *family law* says that all games of one cofactor in a clean window follow one pattern.  The 8p and
12p theorems prove the patterns δ(8P) ≥ 4P₁ and δ(12P) ≥ 6P₁.

*State, witness, gluing.*  For a game n and a set of columns (a *region*), the *cells* of the region are its numbers
k·P_j with k composite.  An optimal set S of n holds some of them, its *state*.  A *witness* of a state is a set of
cells of board n − 1, worth at least the target more, that the *gluing lemma* proves playable with the rest of S,
whatever the rest is.  A state with no witness is *open*.

### The work

A brief ([brief.md](brief.md), with its scripts and tables) tabulated how the proven and the best-known games change
from n − 1 to n.  A study read it and wrote a report in three rounds ([study-report.md](study-report.md)), asking the
coordinator for experiments, which the coordinator ran.  A referee, a reader who had not seen the study's reasoning,
checked the proof of Theorem A.  All of it ran on 2026-11-11, in Pacific time, on batmobile, at low priority.

| label | what it does | ran | what it could decide or kill |
|---|---|---|---|
| brief | the predictors, the families, the clean windows and the parity form, on 1,745 searched games of 2 to 5060 and 1,712 of 5061 to 10000 | to 05:40 | none |
| study, round 1 | Theorem A, the clean-window principle, the cascade, the exchange law, the gap | to 06:15 | none |
| referee of Theorem A | the proof step by step, and the greedy basis from scratch on every board 3 to 5060 | 06:15 to 06:27 | any error in the proof |
| flagged plays | one level-4 play of each game where the clean-window form says a score is short | 05:46 to 06:16 | a raise names a short score and confirms the form at that game |
| E5 | the parity bound's own heaviest sets at 11 games, in cell form beside the game's change | 06:20 to 07:20 | killed if at a clean game the parity change differs from the game's while the values agree |
| E7 | the odd cores of the window instance, for cofactors up to 40 | 06:40 to 08:05 | whether the finite window problem can be the same for the game and the bound |
| E8 | game n with everything outside columns 0 to 3 fixed as in n − 1, at 31 clean 16P and 20P games | 06:44 to 06:56 | whether δ(n) is the window's own optimization |
| E6 | from the exact proof of n − 1, how many refuted sets are bound to x (the exchange law's obligation), at 11 exchanges | 07:28 to 07:31 | the size of the obligation |
| study, round 2 | game 5061, the 21P family, the sharpened exchange target | to 08:24 | none |
| E10 | the parity bound's change at 5061, 5019, 3297 and 3507 | 08:15 to 08:40 | whether 5061 is the proven precedents' case |
| E11 | game 5061 with everything outside a region fixed as in the proven 5060 | 08:37 to 08:52 | a better game (5061 short), or none |
| E14 | the seal: whether the cascade frees anything outside the window or the region | 08:54 to 09:20 | the sealing lemma |
| E9 | the parity hole law (T) at the 11 exchanges, by an exact search | 09:23 to 10:23 | (T) as the one-board target of the exchange law |
| E13 | sizing a transfer proof of the exchanges of 5216 to 5279, and two measurements | 09:24 to 10:13 | its cost; to be run only if cheap |
| study, round 3 | a proof of 5061 as a finite table, sized | to 10:18 | none |
| E16 | an independent reading of the gluing lemma by a reader who had not seen E12 | 10:19 to 11:03 | any error in the lemma |
| E12 | the window-law enumerator: finite case tables of the family laws, by the gluing lemma (round 3: E12b and E12c) | 08:45 to 10:10, and 11:40 on | a table with no open state proves a family law |
| E15 | the gluing proof of 5061, built and run on 5061, 3297 and 3507 | 10:20 to 12:10 | every state closed at 746 or more proves 5061; the calibration at 3297 and 3507 |

The study set a criterion for each experiment before it ran, in its sections 8 and 14, and the table gives the sharpest.

## Results

### Theorem A: how the parity bound moves

**At an exchange the parity bound rises by n less the smallest source that the sum needs, and the promotions it allows
do not change.**  Let n ≥ 3 be odd, and V the span over GF(2) of the vectors of the sources of board n − 1.  If v(n) is
not in V, G(n) = G(n − 1) + n.  If v(n) is in V, exactly one set C ⊆ G(n − 1) sums to v(n), its members lie in n's
layer, and with x_G its smallest member G(n) = G(n − 1) − x_G + n, Q\*(n) = Q\*(n − 1), and PB(n) = PB(n − 1) + n − x_G.
So δ_PB(n) = x_G.  Given (♦) the source that U\* gives up at an exchange step is x_G, and x_G is the shadow of n at
every one of the 1,750 odd boards of the chain where v(n) is in V (measured).  The theorem needs no search, no statement
U and no (♦).

*What follows from it.*

* **The exchange law is the statement that the gap does not change at an exchange.**  Given (♦) at n − 1 and n,
  δ(n) = x if and only if rise(n) = 0, and the law's open half, δ(n) ≥ x, is gap(n) ≥ gap(n − 1).
* **The gap stays at primes, odd semiprimes and half-out steps.**  At every prime, and every odd n ≥ 189 with two prime
  factors (the semiprime formula gives δ(n) = x_G), rise(n) = 0, with no conjecture.  At a half-out step δ_PB(n) = 0,
  and given U and (♦) at n − 1 rise(n) = 0.
* **So the gap of the chain changes only at relaxations and restrictions**, and at an exchange only if the exchange law
  fails, which no game of the chain shows.  gap(5060) = 2,557 is a sum over those steps alone: 389 relaxations and 132
  restrictions raised it, 315 and 171 lowered it, and 20 of the falls are at games at the ceiling.
* **The three kinds of step in the parity bound** match the frame model's.  At a restriction Q\* can only fall, at a
  relaxation n/2 joins the numbers up to n/2, and at an exchange Q\* does not change; given U and (♦) the gap is
  Q\*(n) − P\*(n), so the whole gap lives in the promotion problem.
* **The transfer lemma bounds the gap's change from below.**  If a heaviest set I of the parity bound of n − 1 holds the
  moves D that the game gives up and avoids the ones A it takes up, and (I − D + A + n) is independent at both parities
  on board n, then rise(n) ≥ 0.  A game that scores opt(n − 1) + PB(n) − PB(n − 1) proves the other direction.

*The checks.*  The referee ([check-a/referee.md](check-a/referee.md)) found the proof correct and closed two wording
gaps: the spans in "the same span at each parity" are of the vectors without extra coordinates, and the layer fact (the
members of C lie in n's layer) is what makes the other members' vectors the same at the other parity.  The game lemma
needed one hypothesis stated, that A ∩ T′ is empty.  The referee's own code computed G(m) from scratch on every board 3
to 5060 and found at each of the 1,750 odd boards where v(n) is in V (676 primes, 971 odd semiprimes from 189 and 103
others) that G(n) = G(n − 1) − x_G + n and PB(n) − PB(n − 1) = n − x_G, and at the 779 where it is not that G(n) = G(n −
1) + n.  Of the even boards, 1,388 have n/2 in G(n − 1) and 1,141 do not, and the classification agrees with the
succession study's at every board.  The rise is 0 at all 971 odd semiprimes and 676 primes, at all 1,074 exchanges of
the chain and at all 1,141 half-out games.

*On master.*  The commit [287486e](https://github.com/bvchess/taxman/commit/287486e) adds the theorem as W4, its
corollary for where the gap stays as W5 and the transfer lemma as
[W6](https://github.com/bvchess/taxman/blob/287486e/docs/theory/parity-bound.md#the-transfer-lemma), under the theory's
names for the steps, with
[solver/noframe/tests/parity_steps.rs](https://github.com/bvchess/taxman/blob/287486e/solver/noframe/tests/parity_steps.rs),
which checks W4 on the prover's committed parity bounds of 2 to 5060.  The game lemma is left out.

### The clean-window principle

**In a window clean to the depth of its cascade the gap does not change; this is measured, and no proof reaches it.**
Three forms were stated.  The *parity form* (P1) says that a relaxation or restriction in a window clean to the depth of
its cascade has opt(n) = opt(n − 1) + PB(n) − PB(n − 1).  The *inequality* (P2) says opt(n) ≤ opt(n − 1) + PB(n) −
PB(n − 1) there, which is what settles a game: a game that scores the right side is optimal, and the right side takes
seconds.  The *cascade* (P3) is the mechanism, in the next section.

Relaxations and restrictions from 187 on with rise 0, by the depth to which the window is clean:

| range | depth 0 | 1 | 2 | 3 | 4 | 5 or more | depth 2 or more | depth 3 or more |
|---|---|---|---|---|---|---|---|---|
| chain 187 to 5060 | 350 of 1,281 | 107 of 156 | 55 of 56 | 30 of 30 | 29 of 29 | 67 of 67 | 181 of 182 (9.9% of the CPU) | 126 of 126 (6.1%) |
| best-known 5061 to 10000 | 349 of 1,077 | 75 of 124 | 67 of 88 | 44 of 48 | 29 of 29 | 161 of 161 | 301 of 326 | 234 of 238 |

* **At depth 1 the inequality fails on the chain.**  Of 156 games, 107 have rise 0, 27 rise above 0 and 22 fall below
  it, and the 22 break the inequality, so depth 1 is no hypothesis.
* **The single exception at depth 2 is 2512 = 16·157.**  Its window is clean to depth 2, while its 16P cascade ends in
  column 3, which holds the rows 17 and 18 (17·139 = 2363 and 18·139 = 2502, both at most 2512).  The recorded change is
  the 16P pattern, δ = 1,156, and δ_PB = 1,058, so the gap rose by 98.  The inequality holds and the equality fails.  So
  the hypothesis is "clean to the ladder's depth", 3 for 16P, and "depth 3" is the uniform hypothesis that fits every
  cofactor the chain shows clean.
* **Past 5060 the exceptions at depth 3 or more** are 5943 and 6657 (21P, rise +496 and +764), 9510 (30P, +20) and 9140
  (20P, −1).  A rise above 0 can only be a short best-known score at n, and a rise below 0 only a short one at n − 1, so
  these four say that 5943, 6657 and 9510 are short and that 9139 is short by 1, unless the form fails there.  At depth
  2 there are 21 more past 5060, 16 of them in the cofactors 30, 32 and 36, which have no game of the chain clean to
  depth 2 at all.
* **The games that the form covers.**  Beyond the families 8P and 12P, depth 2 or more holds 43 games of the chain (42
  with rise 0; 5.1% of the CPU) and 174 past 5060 (149 with rise 0); depth 3 or more holds 14 games of the chain (all
  rise 0, 1.3%) and 86 past 5060 (82 with rise 0).  The dearest clean games beyond them are 4975 = 25·199 (142
  CPU-hours), 4976 = 16·311 (141), 4432 = 16·277 (75), 4925 = 25·197 (41) and 4893 = 21·233 (29), all at rise 0.
* **Plays at the flagged games raised none.**  The 25 games that the form flags past 5060, which [the audit of the
  best-known games](../how-many-best-known-games-past-5060-are-short-2026-11/README.md#what-the-audit-found) lists with
  the 1,559 target games where a streak of short games can start, got one level-4 play each on the first of the seeds 41
  to 43 not yet played (23 plays; 9390 and 9510 had had all three), and none rose.  The 13 plays of 5061 from the proven
  5060 (one flagged play and 12 of the hammer, at levels 4 and 5) found nothing either.  So no flagged game was shown
  short.  `improve.py` applied every family pattern to the best-known game of n − 1 past 5060: of 732 pattern sets below
  the best-known δ that it tried, one was playable and improved a game, 7944 (24P), to 19,854,251, 4 above its
  best-known 19,854,247, replayed by the rules.  A level-4 play of 7944 then raised it by the same 4.
* **What a proof would need.**  The transfer lemma reduces rise ≥ 0 to applying the game's change to a heaviest set of
  the parity bound of n − 1.  In a clean column the parity bound's use of the hubs is the game's (the four layer-3
  sources of a column span the two combinations that 4P_j and 6P_j need, and hub 4 or hub 6 pays once), so a proof of P1
  for a cofactor is the family's proof written twice, once with payment schemes and once with spans.  What stops a
  general proof is the coupling through far hubs, which no clean window controls.

### The cascade

**In a clean window the change from n − 1 to n is an alternating path along the columns through the hubs.**  The cell n
takes a hub from the cell of the next column, that cell falls back on a factor of its own column, the move it frees
takes the next hub from the column below, and so on to a loss.  The pattern of a family is the list of cells the path
passes.  In 1168 = 16·73, with P₁, P₂, P₃ = 71, 67, 61, game 1167 holds the move 1136 = 16P₁ paying with the hub 16, 568
= 8P₁, 852 = 12P₁, the move 402 = 6P₂ with the hub 6, 804 = 12P₂ and the move 244 = 4P₃ with the hub 4.  Game 1168 has n
paying with the hub 16, so 1136 falls back on 568, 852 moves to the freed 284, 426 takes the hub 6 from 402, 804 moves
to 402, and 268 takes the hub 4 from 244, which is given up: δ = 568 + 402 + 244 − 426 − 268 = 520 = δ_PB.

| family | pattern, δ = | depth | chain: hits / searched | past 5060 | clean: hits |
|---|---|---:|---|---|---|
| 8P | 4P₁ | 1 | 106 of 106 | 89 of 89 | 192 of 192 |
| 12P | 6P₁ | 1 | 75 of 76 | 63 of 63 | 127 of 127 |
| 16P | 8P₁ + 6P₂ + 4P₃ − 6P₁ − 4P₂ | 3 | 36 of 60 | 49 of 49 | 53 of 53 |
| 20P | 10P₁ + 6P₂ + 9P₂ − 6P₁ − 10P₂ | 2 | 7 of 50 | 36 of 41 | 43 of 43 |
| 24P | 12P₁ + 10P₂ − 10P₁ | 2 | 16 of 42 | 30 of 34 | 22 of 22 |
| 40P | 18P₁ | 1 | 18 of 28 | 23 of 23 | 13 of 13 |
| 21P | 10P − 9P = P | 0 | 7 of 47 | 34 of 39 | |

In clean windows the patterns of 8, 12, 16, 20, 24 and 40 are exact at 450 of 450 games of both ranges, and elsewhere
they hit about half.  Fitted on 187 to 5060, the patterns of 39 families agree with 691 of their 828 searched games past
5060.  The other loop rules are narrower:

* **A single loss in the cluster is exact at 463 of the 1,745 searched games** of 2 to 5060 (20.4% of the chain's CPU,
  half of it exchanges), and no rule that loses one cluster member can pass 498 games (20.6%).
* **A crude cascade predictor is exact at 569** (30.8%), as often as the single-loss rule, and every move that changes
  lies within three primes of P at 1,045 of the 1,692 searched games from 187 (69.9% of the CPU).
* **δ_PB alone hits 758** of the 1,745 (38.8% of the CPU), more than any other single predictor.
* **The gap is not a sum of loop losses.**  A clean loop is a circuit the parity bound prices exactly, so it adds
  nothing.  The gap is a running sum of defects of steps in unclean windows, created where n's arrival makes an odd core
  and dissolved where it removes one.  The dearest game, 4983 = 3·11·151 (1,094 CPU-hours, 10.8% of the chain's CPU),
  has δ_PB = 0 and δ = 246, a regular pattern of eight moves in six rows of three columns that the parity bound does
  not see; its family 33P has 13 restrictions from 3333 on (six in the chain) with δ_PB = 0 and δ from 88 to 386.

**E5 shows the cascade at the level of sets.**  `paritydump` found a heaviest set independent at both parities of boards
n − 1 and n, nearest the recorded sets, at 11 games.  At all seven games with rise 0 (16P at depths 1, 2, 2, 3 and 3;
25P at depth 2; 21P at depth 3) the parity bound's change is the game's change, cell for cell, on the whole board, and
forced: every heaviest set of n − 1 holds D and avoids A, and every heaviest set of n holds A and n and avoids D.  The
kill criterion did not fire.  At the four games with rise ≠ 0 the models part through a parity circuit that runs through
cells of the cascade:

| n | rise | what the parity bound does that the game cannot |
|---|---:|---|
| 2512 = 16·157 | +98 | an exchange far from the window, 833 out and 931 in, which the cascade opens by dropping (4,3) and breaking a 55-member circuit through column 3's cells (4,3), (9,3), (12,3) and (18,3); in the game the exchange closes a 14-member odd core on the rows 45 to 105 of the columns of 19 and 23 |
| 688 = 16·43 | −2 | n − 1's heaviest sets hold hub 4 by a rotation (68 for 44, 266 for 238, 275 for 325, worth +2) that the game cannot play, blocked by a circuit through the rows 18 and 20 of column 3, which only an unclean column holds; the cascade's last rung gives that holder up |
| 1328 = 16·83 | −32 | the same at hub 4, with 76 for the game's 44 (worth 48 within an exchange), blocked in the game by a circuit through row 18 of column 2 |
| 1460 = 20·73 | −39 | the same at hub 4, through column −1 (the prime above P), whose cells 9·79 and 12·79 compete for the same hubs |

**E8 shows the other half: the change is the window's own optimization.**  With every promotion outside columns 0 to 3
fixed as in the committed set of n − 1 and the window free, the best score equals opt(n) at all 31 clean 16P and 20P
games of the chain, 2512 included, and the best set is the committed set of n on the window.  The depth that reaches
opt(n) is the family's: 3 at all 24 games of 16P (short by 8 to 56 at depth 2) and 2 at all 7 games of 20P (short by 10
to 30 at depth 1), measured without the recorded sets of n.  The restricted solves were checked first on 1,677
restricted problems of boards 1 to 60 against an oracle that shares nothing with the search (1,620 equal, 57 refused as
they must be), and each took under a second.

**E7 shows when the finite window problem is the same for the game and the bound.**  The *odd cores* of a window
instance are the cores whose lists are independent over GF(2), the configurations on which the two models can part.
Enumerating the window instance for each cofactor c and depth d found:

| (c, d) | columns | odd cores | complete? |
|---|---:|---:|---|
| (16, 3) | 4 | 0 | yes |
| (17, 5) | 6 | 0 | yes, so none for c ≤ 17 in up to 6 columns |
| (40, 1) | 2 | 0 | yes, so no two-column odd core for c ≤ 40 |
| (20, 2) and (24, 2) | 3 | 2 each, on 7 members | yes |
| (30, 3) | 4 | 4,142 with 3 columns | 3 columns only |
| (36, 3) | 4 | 69,357 with 3 columns | 3 columns only |

The window instance has an odd core exactly when c ≥ 18 and d ≥ 2 in the windows tested, and the smallest has the rows
{8, 12, 18} in three columns.  An odd core in the window does not force a rise: the clean games of these cofactors at
depth 2 or more all have rise 0 in the chain, and E5 finds the parity change equal to the game's at 4975 = 25·199 and
4893 = 21·233, whose windows have odd cores.  So the absence of an odd core is a sufficient test and not a necessary
one.

### The exchange law

**Theorem A reduces the exchange law to one question about one family of promotion sets.**  By Theorem A the family ℒ of
promotion sets that the parity bound admits is the same for boards n − 1 and n at an exchange, and given U at both games
the law, opt(n) = opt(n − 1) + n − x, says P\*(n) = P\*(n − 1): the heaviest promotion sets of n − 1 and of n are
equally heavy, though the games differ in which members of ℒ are playable.  The one-board target is the *parity hole
law* (T): for an exchange step n with shadow x and B = U\*(n − 1) − x, every promotion set L with U\*(n − 1) ∪ L
independent at both parities and B ∪ L playable on board n − 1 weighs at most P\*(n − 1).  Given U at n and (♦) it
implies the law's inequality, opt(n) ≤ opt(n − 1) + n − x.  It differs from the failed hole law of the previous entry in
one thing: x stays in the parity constraint and leaves only the playability test.

* **E6: no refuted set is bound to x** at any of the 11 cheap exchanges (741 to 2301).  The exact proof of n − 1,
  searched alone from its committed promotions, refuted 20 to 572,315 distinct sets a game worth more than P\*(n − 1)
  and none had every core through x, in both variants (default tactics, and with the rule of symmetric pairs off).  At
  2301 a few cuts are bound to x: 6 node conflicts, 2 or 3 failed promotions and 3 nogoods, all but one of which game
  2301 refuses as well; the one that it can promote is the nogood {602, 826, 1058, 1113, 1118}, whose refuted set has
  another core without x.  The result could not have failed, since the committed scores give P\*(n) = P\*(n − 1); it
  checks them.  It also shows that the earlier entry's detours, the sets of the board without x, lie outside ℒ at all 11
  games and are refused by parity.
* **E9: (T) holds at all 11 games.**  The prover searched every promotion set of the board, not only the frame solver's
  candidates, with x barred from the picks and forced in the parity solve alone, and found none worth more than P\*(n −
  1), at 741 to 2301 (2301 on 16 threads: 1,504,929 nodes, 278.6 s).  The ghost search took the plain search's tree to
  within a few dozen nodes, and the search that bars x everywhere found a set above P\*(n − 1) at all 11 games, as the
  earlier entry says there are.  The one-board target holds where it was tested.
* **E13 sized a transfer proof, and did not run it.**  At an exchange, the proof tree of n − 1 is a proof of n at every
  node whose cut has a core without x, so only the nodes whose cut is bound to x need a search.  In 5216 to 5279, 16
  games are exchanges and 15 are repeats; the one searched exchange is 5217, and it needs the proof tree of 5216 (gap
  2,126), about 85 CPU-hours by the chain's growth and 8 to 11 hours on 16 threads with the trace, which needs the
  owner's approval.  Two measurements ran: the whole proof of 4692 transfers to 4693 (638,887 steps in 105 s on 7
  threads; 243,528 refuted sets, 0 bound to x), and the first 20 million steps of the proof of 4406, for the exchange
  4407 (30 minutes on 14 threads), held none.

### Game 5061

**5061 = 3·7·241 is a restriction in the 21P family's regime (ii), and the parity bound recovers 492 points more than
the best-known game does.**  Game 5060 is proven (opt 8,053,621, gap 2,557).  The best-known score of 5061 is 8,057,936,
so δ = 746 against δ_PB = 254, a rise of 492 and a gap of 3,049 if the score is right; the root bounds give opt(5061) ≤
8,059,751.  In 5060, column 0 holds the moves 6P = 1446 and 9P = 2169, with 18P paying by the hub 18.  When 5061 arrives
it pays with 7P, 14P falls back on 2P, 6P has nothing and leaves, and 18P takes 6P and lets the hub 18 go.  The hub
lands in a far region, where the best-known game buys back 700 by moving the hubs 18, 27, 29, 30 and 32 among the
columns of 151, 157 and 163, so δ = 1446 − 700 = 746.  The proven 5019 = 21·239, in the same regime, recovers 942 and
loses 492.

**The 21P family has two regimes, read in game n − 1.**  The hub 18 decides, without an exception in 69 games.  In
regime (i) the hub is held by a cell of column −1, −2 or −3, and the change is a single-column cascade with δ = 10P − 9P
= P and rise 0, at all 7 games of the chain and all 36 past 5060.  In regime (ii) 18P holds the hub itself, the cascade
ends by releasing the hub 20 into a far column, and δ = 6P less the far recovery.  The five regime-(ii) games past 5060
(5061, 5943, 6153, 6573, 6657) are exactly the five exceptions, with rises 492, 496, 568, 764 and 764; in the proven
range 2 of 16 have a positive rise, 12 rise 0 and 2 fall.  The two proven exceptions are 3297 and 3507, where the parity
bound recovers 776 and 824 against the game's 540 and 609.

**E10: the parity bound's extra 492 is a far-region odd core, the same at 3297, 3507 and 5061.**

| n | δ | δ_PB | rise | the parity bound's own change | the game's change |
|---|---:|---:|---:|---|---|
| 5019 = 21·239 | 492 | 492 | 0 | −6·239 + 6·157 | the same, forced |
| 3297 = 21·157 | 402 | 166 | 236 | −6·157 + 8·97 | 6P out, then 3 cells out and 4 in, in the columns of 97, 101, 103 |
| 3507 = 21·167 | 393 | 178 | 215 | −6·167 + 8·103 | 6P out, then 4 out and 5 in, in 103, 107, 109, 113 |
| 5061 = 21·241 | 746 | 254 | 492 | −6·241 + 8·149 | 6P out, then 4 out and 5 in, in 151, 157, 163 |

At 5061 the parity bound's change is one exchange, 6P out and 8·149 = 1192 in, where the game recovers 700 over five
cells, and 492 = 1192 − 700.  In the parity bound's heaviest set of n − 1, the cell 8q has a circuit at parity 1 of 21
members in five columns that 6P's departure breaks.  The extra, applied to the recorded set of n, is independent at both
parities and unplayable, and the residual of the result has 19 members of the same shape (hubs 8, 12, 20, 27 and 30
listed three times each and hub 18 four times), with a minimal core of 11 members at 5061 and 12 at 3297 and 3507.  The
shape is the same column for column and row for row at all three games, and the rises at 3297 and 3507 are proven.  The
natural reading, that the extra is one cell of a hub row added to the best-known game, fails: the recorded set plus 8q
is dependent at a parity.  The extra is an exchange of several cells around 8q.

**E11: no game of 5061 above 8,057,936 has the proven 5060's set outside any region.**  The restricted solve of 5061
with every candidate outside a region fixed (or barred) as in the proven optimal set of 5060 returned 8,057,936, the
best-known game itself, in every region: the columns of 151, 157, 163, 241 and 251 (36 free candidates), E10's eight
columns (149 to 631), and the bands of all primes 127 to 257, 101 to 313, 53 to 509 and 29 to 1013, where 816 of the
1,380 candidates are free and 120 fixed (26,390 steps, 4.88 s).  A band of all primes from 13 up was stopped at 10
minutes and 17.7 million steps with no better set.  The calibration passes: at 3297 and 3507, proven, the region solves
return opt(n) with the recovery 6P − δ = 540 and 609, the chain's values, in the regions of the committed change and in
E10's with the column of 113 added; E10's region at 3507 without that column falls 33 short.  So 5061 is not short by a
rearrangement of the far columns with 5060's set elsewhere.  It could still be short by a game that changes 5060's set
among the 11-smooth candidates or keeps U\* in part.

**E14: the seal.**  The literal test of the sealing lemma, that no circuit through a ladder cell leaves the window,
fails at all six 16P games tested, clean or not, since the ladder cells are the window's hub holders.  The operative
test, that the cascade frees no element outside the window, holds at the four games whose column 3 has no row 18 (2224,
2768, 3184, 4432) and fails at 1168 and 2512, which have it, through the same four cells.  At 5061 E10's region is
sealed in the parity model: its change stays inside it and frees nothing outside.  The study's smaller region is not, by
one cell, 8·149 through hub 8.  The holders of the hubs 8, 12, 16 and 20 (8·631, 12·421, 16·313, 20·251) are the
heaviest cells of their hubs in every heaviest set of 5060 and 5061 and do not move.  With E11, E10's region is both
sealed in the parity model and exhausted in the game, for the configuration with 5060's set outside.

**The judgment after E10, E11 and E14 stayed undecided.**  For a short score: the five regime-(ii) games past 5060 are
the five exceptions, with rises of 1.75 to 2.4 P, against 2 of 16 in the proven range at 1.3 to 1.5 P, a one-in-thirty-
thousand event under the proven rate, which a heuristic that finds the first-order recovery and not every reshuffle of
three columns explains with no coincidence.  For a genuine rise: the two proven precedents with the same mechanism, the
parity bound's change matching them column for column, and 13 plays of 5061 that found nothing.  The study put the two
near even.

### The family tables and the gluing lemma

**A proof of a family law can be a finite table, if a lemma lets a witness on board n − 1 glue to the rest of an optimal
set.**  The 8p and 12p proofs delete n from an optimal set of n and put cells back in n − 1 through re-payments.  The
study replaced the payment schemes by *core domination*, the gluing lemma.  Let n ≥ 187, R a set of columns of primes
P_j with 2P_j² > n, S a playable set of n whose cells in R are W, O = S − W, and W′ a set of cells of board n − 1.  Call
X ⊆ W′ *column-closed* when every column factor outside W′ that a member lists is listed by another member, with rows(X)
the rows it uses and R1(X) the rows whose hub exactly one member lists.  If every column-closed X ⊆ W′ has a
column-closed Y ⊆ W with rows(Y) ⊇ rows(X) and R1(Y) ⊆ R1(X), then O ∪ W′ is playable on board n − 1 and δ(n) ≥ ΣW′ − ΣW
+ n, with the repairs of E16 below.  The proof is half a page: a core of O ∪ W′ meets W′ in a column-closed set X, and
replacing X by Y gives a core of S, which is playable.

**E16: the lemma is correct once repaired, and the generalized form was wrong as written.**  A referee who had not seen
the study read only the lemma and the sources it cites.  The clean-window form is correct with two repairs: n must be a
cell (c composite), and in a one-column window with c ≥ 2P the hub is also a column factor.  The generalized form, for
any region with 2P_j² > n and S only playable, failed three ways, each with a counterexample: G1, column-closed must be
read in the pool of O and W′ (n = 200, R = {11, 13}, S = O = {22, 26}, W′ = {44, 52}: {44, 52} is a core); G2, n must
not be in O (n = 191, R = {11}: opt(190) = 11,637 is below ΣS = 11,647, and δ(191) = 181 is below 191); G3, the δ clause
needs ΣS = opt(n) (S = W′ = ∅ gives δ(n) ≥ n, false at 191).  The checks: the three facts the lemma rests on hold on all
9,814 boards from 187 to 10,000 with 2P² > n for every prime of the region, and on the 21,674 clean windows of the form
n = c·P, of which 15,974 are one-column windows with c ≥ 2P where the first repair applies; 300,000 random states of
boards 196 to 440 per reading found no counterexample to the repaired form (the hypothesis held with a closed X in
20,501 states, 5,412 of them with W′ not inside W) and 47 to the literal reading; on the committed optimal sets of the
257 clean windows with c composite, c ≤ 24 and at most 10 cells, from 187 to 5060, 45,949 sets W′ met the hypothesis,
1,138 non-trivially, and O ∪ W′ was playable every time (865 windows had too many cells and were skipped).

**E12: the tables settle games only under a hypothesis that the tables cannot discharge.**  The enumerator
(`window_law.py`) lists the states of a clean window that hold the sources U gives and have no core, and for each looks
for a witness that gains the family's law at every prime whose window is clean to that depth.  A state with no witness
is open.  The first round gave:

| family | states | closed | open | clean games in a closed state, witness = law |
|---|---:|---:|---:|---|
| 8P (depth 1) | 3 (28 with the sources free) | all | 0 | 192 of 192 |
| 12P (depth 1) | 9 (1,812 free) | 6 (1,809) | 3, the same 3 | 127 of 127 |
| 16P (depth 3) | 125 | 120 | 5 | 53 of 53 |

* **8P reproduces the 8p theorem in full**, with no hypothesis even with the sources free.
* **12P reproduces the 12p theorem up to its hypothesis.**  The 3 open states hold 4P and 6P, 4P and 6P₁, or 6P and 4P₁;
  a put-back needs hub 8 alone, and whether that is safe depends on the cell that holds hub 8 off the window.  The 12p
  theorem settles them with its hypothesis that 8t is in the optimal set, a far cell outside the window.
* **16P gives a theorem with two hypotheses**: S holds the 24 source cells of the window, and its candidates are none of
  the 5 open sets.  All 53 clean 16P games, 9 proven and 44 best-known, hold the 24 sources and lie in the one state
  {8P, 6P₁, 4P₂}, whose witness is the cascade and gives exactly the law.
* **40P has no table.**  With every source of the window held, the layer-3 sources 22, 33, 39 and 26 close a cycle, so
  no state exists; the chain's two clean games 4120 and 4360 hold every source but 22P₁, which leaves 413,343 states,
  and the Python tool's signature check was too slow (a sample of 150 states had not finished in 13 minutes).  A check
  local to the change would do it.  The build was named E17 and dropped, since its table could add only games settled
  under the hypothesis below, and 40P's games of the chain are all proven.

The second round of the tables, E12b and E12c, added the column of hub 8's holder and the families 21P, 20P, 24P and
25P:

| table | region | states | closed | open | settled past 5060, given U and the hypothesis |
|---|---|---:|---:|---:|---:|
| 16Ph8 | depth 3 and the column of 8's holder | 230 | 220 | 10 | 44 |
| 12Ph8 | depth 1 and that column | 12 | 11 | 1 | 63 |
| 21P | column 0 | 32 | 5 | 27 | 34 |
| 21Pm1 | column 0 and column −1 | 567 | 324 | 243 | 34 |
| 20P | depth 2 | 7,400 | 7,104 | 296 | 36 |
| 24P | depth 2 | 13,824 | 12,614 | 975 (+235 excluded by optimality) | 20 |
| 25P | depth 2 | 4,096 | 2,635 | 1,461 | 12 |

**The hypothesis behind every count.**  A table proves δ(n) ≥ L from any optimal set of n that holds the region's
sources and lies in a closed state.  Statement U gives an optimal set that holds the sources, and does not say which
state it lies in.  So every "settled" count rests on U and on the hypothesis that some optimal set of n lies in a closed
state.  The counts are the games past 5060 whose best-known set lies in a closed state and whose best-known δ equals the
law, and the best-known set lying in a closed state does not discharge the hypothesis, since the best-known set is not
known to be optimal.  The tables with no open state settle games on U alone, and only 8P is one, whose 89 games past
5060 the 8p theorem already settles without U; the 12P count of 63 is likewise the 12p theorem's games.  A table keeps
open a state in which the family's law is false: 8 games of 21P in the chain (231, 273, 357, 399, 609, 651, 861, 903)
have δ < P, and 4975 and 7925 of 25P sit in a state where the law gives δ = 10P₁ − P, below 9P₁.  Before the tables ran,
the study had counted that about 230 of the 1,712 searched games past 5060 would rest on a proven predecessor and U,
against 152 for the 8p and 12p theorems.

### E15: the gluing proof of 5061 fails, even at the proven games

**The proof of δ(5061) ≥ 746 by a finite table of states and witnesses was built and run, and it does not close.**  The
tool (`gluing`, an example of the frame solver) reproduces E12's five tables byte for byte (12P with the sources free in
0.1 s against 62 s).  It decides, for every state that an optimal set of game N can have on a region, a witness on board
N − 1 that gains the target, or a heavier set of board N that the state covers, which excludes the state by optimality,
and it extends an open state by a column that its uncovered hubs name.

| game | base region | target | closed | excluded | open | time on 12 threads |
|---|---|---|---:|---:|---:|---:|
| 5061 | 241, 251, 157 | δ ≥ 746 | 80,841 | 26,546 | 27,221 | 102 s |
| 3297 | 157, 163, 101 | δ ≥ 402 | 84,616 | 22,980 | 27,012 | 178 s |
| 3507 | 167, 173, 107 | δ ≥ 393 | 86,436 | 21,328 | 26,844 | 131 s |

Each base region has the same 134,608 states, and a closed state is proved: if S is in it, δ(n) is at least the target
whatever S holds off the region.  At every game the recorded set's own state is among the open ones.  Searching that
state exhaustively on E10's eight columns, with every change of the candidates allowed, found no witness at any of the
three games (5061: 6,634 nodes in 0.1 s, and 191,355 nodes with the column of 313 added; 3297: 8,609 nodes; 3507: 9,612
nodes), and the nearest miss is a group of cells that uses some hub once.  **The calibration fails**: the proven δ(3297)
= 402 and δ(3507) = 393 are not reached on the regions that hold their changes.

*Why.*  A witness at a recorded state is necessarily an optimal set of n − 1, which the peel plays.  The one the step
comes from holds a column-closed group that uses some hub once (27 at 5061; 18, 27 and 30 at 3297; 12 and 20 at 3507),
and S, which reached n by moving those cells, holds no group to stand for it.  The lemma has to allow every possible
rest of the board, and some rest could close a core through that hub; S's own rest does not, since O ∪ W′ is playable.
So the open state is a limit of core domination at this step, the limit that E12b met at 12P's case B2, and no better
game: E11 found none.  Growth does not close it: the natural witness (the committed set of n − 1 on the region) is not
covered on any region tested, up to every prime from 127 to 1013 at 5061 (140 columns), 89 to 823 at 3297 (120) and 89
to 877 at 3507 (128), and the combined sets O ∪ W′ were played by the peel and replayed by the rules (8,053,621 =
opt(5060) at 5061, 3,418,627 at 3297 and 3,871,751 at 3507).  Growing every open state would take at least 180 CPU-hours
(a sample of 28 of the 27,221 states: 11 trees closed completely and 17 reached the 30 s limit), and was not run,
because the best-known state alone shows that the theorem does not follow from the table.

**What a proof needs is an argument about how S's rest pays the hub**, as the 12p proof makes for case B2 by a closed-
walk argument on S's payment scheme, and not a wider region.  The 107,387 states of 5061's base region that are closed
or excluded need nothing more, and a scheme argument could be limited to the open ones.  The study's plan (its section
15) had counted a proof of 5061 and of about 230 games past 5060 on this route, and the plan does not hold.

## Limits

* **The principle is measured, and past 5060 the measurements are against best-known scores.**  Every rise there is
  agreement with best-known scores, and a rise above 0 means a short score only if the form holds.
* **Theorem A is proved; everything that rests on U or (♦) says so.**  The checks of (♦) are computations to 100,000.
* **The clean-window form's hypothesis is a proxy.**  Clean to depth d is computed from n's factorization, and the
  ladder's depth depends on the cofactor (1 for 8, 12 and 40; 2 for 20 and 24; 3 for 16; more for 30, 32 and 36).  At
  1460 the circuit that parts the models runs through column −1, which cleanliness to the right does not control.
* **The experiments are at the games asked for.**  E5 is at 11 games, E6 and E9 at 11 exchanges, and E8 at 31 clean
  games of the 16P and 20P families, all at the chain's recorded sets.  E8 fixes the committed set of n − 1 outside the
  window, one optimal set of it.
* **E6 could not have failed**: the committed scores give P\*(n) = P\*(n − 1) at its exchanges.  It counts the
  obligation and shows where it lives.
* **E11 fixes 5060's set outside the region**, so it does not exclude a better game of 5061 that changes the set of 5060
  among the 11-smooth candidates or keeps U\* only in part.
* **The tables rest on U and on the hypothesis that some optimal set lies in a closed state.**  The gluing lemma is
  proved by the study and refereed once; the repaired statements are those of E16.
* **The study's report keeps its words.**  It writes "restriction", "relaxation" and "exchange" for the steps that the
  theory now calls added, half-in and exchange, and its file list names the study's own folders.

## Decision

Theorem A is in the repository as W4 to W6, with its test.  No rule of the solver or the miner changed.  The brief, the
study and the experiments are kept here as a record, and:

* The clean-window parity form is a flag for the miner and not a theorem.  It points at 25 games past 5060 that would be
  short if it held, and the 23 plays of them raised none.  How many best-known games past 5060 are short is measured by
  [a sampling test of the targets](../how-many-best-known-games-past-5060-are-short-2026-11/README.md#the-claim), not by
  this form.
* The family tables are kept as a method and as a statement of what each family law needs.  Only 8P is settled by a
  table with no hypothesis, and the 8p theorem was already proved without one.
* **5061 stays best-known.**  Its score, 8,057,936, is neither proved optimal nor shown short.  The owner parked the
  proof pending [the study of 5060's proof, where a proof's work goes: the small primes and the
  gap](../search/where-a-proofs-work-goes-the-small-primes-and-the-gap-2026-11/README.md), and the 40P table (E17) was
  not built.

What would reopen it:

* a payment-scheme argument for the gluing lemma's open states (a closed-walk argument of the 12p proof's kind for a hub
  that S's rest pays once), which would let the tables prove the families and 5061 under U, and would be tried first at
  the proven games 3297 and 3507, whose recovery of 540 and 609 it must return;
* a proof of rise ≥ 0 at a clean window for one cofactor, as the family's proof written twice, with a lemma that a far
  hub's holder is never displaced by a window cell;
* a proof of the exchange law from (T), which E6 and E9 show holds at 11 exchanges, using the transfer argument at the
  nodes (E13's build, which needs the owner's approval to run);
* a play or a search that raises a game flagged by the form, which would show a score short and confirm the form there,
  or a flagged game that no play can raise, which would be a counterexample;
* a game of 5061 above 8,057,936, which would show the score short.

## Files

The work ran in the lab folder `lab/work/loops/`, whose files these are, with their paths as they were there.  The
scripts run as `nice -n 19 python3 -I SCRIPT` from that folder, use the standard library only, and read the committed
results, the gap dashboard's `games.csv`, the best-known file and the previous entry's tables and loaders
([settle.csv](../settling-game-n-from-the-game-before-2026-11/settle.csv),
[past5060.csv](../settling-game-n-from-the-game-before-2026-11/past5060.csv) and
[common.py](../settling-game-n-from-the-game-before-2026-11/common.py)).  The copies of the markdown files are verbatim
but for the following.  In [study-report.md](study-report.md), [check-a/words.md](check-a/words.md) and
[check-a/theorem-a.md](check-a/theorem-a.md) the links to the theory's files by their lab paths now name the files at
commit 287486e.  In `study-report.md` and `study/section4.md` "chain game" is "game of the chain" in three places, since
the retired word means a game at its ceiling.  In `e13/README.md` "cap" is "limit" in two places.  The files held no
mention of the model that wrote the reports.  The study's reports write the study's names for the steps (restriction,
relaxation) and P, P₁ for the repository's p, r.

* [brief.md](brief.md): the research brief the study read.  Its scripts: [predict.py](predict.py) (a line a searched
  game; its output `predict.jsonl`, 1.2 MB, is not copied), [chain.py](chain.py) → [chain.jsonl](chain.jsonl) and
  [chain_log.txt](chain_log.txt), [tables.py](tables.py) → [tables_out.txt](tables_out.txt), [patterns.py](patterns.py)
  → [patterns_out.txt](patterns_out.txt) and [patterns.jsonl](patterns.jsonl), [examples.py](examples.py) →
  [examples_out.txt](examples_out.txt), [explore.py](explore.py), [improve.py](improve.py) →
  [improve_out.txt](improve_out.txt) and [improved.jsonl](improved.jsonl); [predict_log.txt](predict_log.txt).
* [study-report.md](study-report.md): the report, Sections 0 to 15 in three rounds.  [study/](study/): its scripts and
  outputs (`depth_check.py`, `coverage.py`, `rise_kinds.py`, `hubs.py`, `family21.py`, `family21_regimes.py`,
  `g5061.py`, `onecell.py`, `size5061.py`, each with its `_out.txt`) and the texts of its Sections 4 and 10
  ([section4.md](study/section4.md), [section5061.md](study/section5061.md)).
* [check-a/](check-a/): the referee's notes on Theorem A ([referee.md](check-a/referee.md)), the theorem as the referee
  read it ([theorem-a.md](check-a/theorem-a.md), [words.md](check-a/words.md)), and the numeric checks
  ([check_a.py](check-a/check_a.py), [check_a2.py](check-a/check_a2.py)).
* [flagplay.sh](flagplay.sh), [flag-targets.txt](flag-targets.txt) and [flagplays.log](flagplays.log): the plays of the
  flagged games, one play each, with the result of each (the old and the new score, and the gain in parentheses).
* [e5/](e5/): the parity sets (`paritydump.jsonl`, 110 lines, made by the example `paritydump` of the branch loops-e5:
  `paritydump 2512 1168 2224 2768 3184 4432 688 1328 1460 4975 4893`), `analyze.py` → `analyze_out.txt` and `cores.py`
  with `oddcore.py` → `cores_out.txt`.  The early trial `test.jsonl` is not copied.
* [e6/](e6/): E6's runs (`run-e6.sh`, one line a game in `e6-default.jsonl` and `e6-symmetry-off.jsonl`, the sample of
  2301's x-bound sets, progress lines, `checks.txt`, and `e1_sets.py` → `e1_sets_out.txt`).  Not copied: the binaries
  `obligation` and `taxman.loops-e6` (61 and 71 MB) and the earlier builds' runs `run1/` and `run2/`.
* [e7/](e7/): `window_cores.py` (rows from the top down), `window_cores_up.py` (from the bottom up) and `summarize.py` →
  `summary_small.txt` and `summary_c36_d2.txt`, with the outputs of the Python runs, `rust_summary_c36_d2.json`, and
  the lists of finished tasks of the Rust port `windowcores` (branch loops-e5).  Not copied: `rust_cores_c36_d2.jsonl`
  (21 MB, every odd core of (36, 2)) and `stopped/`, the empty outputs of runs replaced by better methods.
* [e8/](e8/): `run-e8.sh`, `e8.jsonl` (a line a game and depth), `check-bars-1-60.txt` and the progress lines.
* [e9/](e9/): `run-e9.sh`, `e9.jsonl` (every run), one `e9-N-MODE.json` a run, the 16-thread runs of 2301 and the check
  of the threaded path, `summarize.py` → `summary.md`.  Not copied: the binary `ghost` and `v1/`, `v2/`, the superseded
  versions of the tool (3.4 and 4.1 MB).
* [e10/](e10/): `paritydump.jsonl` (the dump of 5061, 5019, 3297, 3507 and their predecessors), `analyze.py` →
  `analyze_out.txt` and `probe.py` → `probe_out.txt`.
* [e11/](e11/): `run-e11.sh`, `e11.jsonl` (a line a game and region, with its moves), `referee.py` →
  `referee_out.txt` (the replay by the research repository's independent referee), the bands' prime lists
  (`specs1.txt` to `specs3.txt`) and `widest-stopped.txt`.  Not copied: the binary `restricted` (64 MB).
* [e12/](e12/): `window_law.py`, `check_data.py`, `diagnose.py`, the outputs (`out_*.txt`, `check_data_*.txt`,
  `diagnose_*.txt`) and the tables (`table_*.jsonl`).  Not copied: `table_20P.jsonl` (1.2 MB) and `table_24P.jsonl`
  (2.4 MB); `table_40P.jsonl` and `table_40P_local21.jsonl` are empty.
* [e13/](e13/): the two measurements' lines and progress.  Not copied: the binary `obligation`.
* [e14/](e14/): `seal.py` → `seal_out.txt` (`seal_a_out.txt` is Part A alone), `paritydump-5061.jsonl` and
  `hubcells.txt`. Not copied: the binary `paritydump`.
* [e15/](e15/): the printed outputs of the base runs (`base*.txt`), the exhaustive searches of the recorded states
  (`recorded*.txt`), the natural witness on wide regions (`cover*.txt`), `diag.py` and `open_kinds.py` with their
  outputs, and the growth sample's printout.  Not copied, and in the lab folder `lab/work/loops/e15/`:
  `base5061.jsonl.gz`, `base3297.jsonl.gz` and `base3507.jsonl.gz` (2.4 MB each: every base state, one line each, with
  its outcome and witness), `grow5061-sample.jsonl` (1.4 MB) and `port/`, whose five tables are identical to E12's.
* [e16/](e16/): the lemma as the referee read it (`lemma.md`), the referee's notes and the four checks with their logs.
* [patches/](patches/): the code of the experiments, as `git am` patches (see Commits).

Not copied: the best-known file (137 MB at the time) and the gap dashboard's `games.csv`.  The coordinator's decisions,
among them the owner's parking of 5061, are in its log, and none is kept here.

## Commits

The branches `loops-e5`, `loops-e6` and `loops-e15` of the research repository were never pushed, so `git show` may not
find their commits.  The patches were made with `git format-patch` from the merge base of each branch with master, which
is [79faea3](https://github.com/bvchess/taxman/commit/79faea3) for all three, and apply in order with `git am`.  The
branch `loops-e15` is `loops-e6` and three more commits, so its folder holds those three, numbered 0015 to 0017, to be
applied after the 14 patches of `loops-e6`.  Applied to a clone of the repository with `git am`, the patches of
`loops-e5` on 79faea3, of `loops-e6` on 79faea3, and of `loops-e6` and then `loops-e15` on 79faea3 each rebuilt the tree
of their branch's tip.

* [patches/loops-e5/](patches/loops-e5/) (9 patches): `paritydump` (E5), `windowcores` (E7) with the lab's scripts that
  the branch holds, `paritydump` reading best-known games past the chain (E10), and `window_law.py` with its checks and
  its README (E12, E12b and E12c).
* [patches/loops-e6/](patches/loops-e6/) (14 patches): E1's three commits (the setup fingerprint, restricted problems of
  the frame model, and the formatting), as in [the earlier
  entry](../settling-game-n-from-the-game-before-2026-11/README.md#commits), then the trace of the search's refutations
  with the example `obligation` (E6; 0004, 0006 and 0007), the subcommand `window` of `restricted` (E8, 0005, and E11's
  region option, 0008), `paritydump` as taken from `loops-e5` (0009 and 0010) with its option for cells and threads
  (0011, E14), and the prover's parity bound from another board with the example `ghost` (E9; 0012 to 0014).
* [patches/loops-e15/](patches/loops-e15/) (3 patches): the example `gluing` (E15), its grown regions, stages and
  options (`--only`, `--cover`), and its formatting.

On master of the research repository in the same hours, [287486e](https://github.com/bvchess/taxman/commit/287486e)
(06:47) added Theorem A as W4 to W6 of `docs/theory/parity-bound.md`, with `solver/noframe/tests/parity_steps.rs` and
the glossary, theory index, statements, evidence and test catalog; the commit 79faea3, the base of the patches, is the
prover's `moves` bounded by the unit-weight parity bound.  The commit that adds this entry also adds its rows to the
register's files of [the theory and its proofs](../register/theory-and-proofs.md) and [the unsound
mode](../register/unsound-mode.md).
