# Settling game n from the game before (2026-11)

Part of the [lab notebook](../README.md).

Started 2026-11-10.  Concluded 2026-11-10.

**Question.**  Can a theorem, or a cheap procedure proved correct, settle game n from the proven game n − 1 at games that
no rule of the solver settles?  To settle game n is to prove its *shortfall*, δ(n) = opt(n − 1) + n − opt(n): the points
by which its best score falls below its *ceiling*, opt(n − 1) + n.

**Answer.**  For two families of games, yes.  The 8p theorem and the 12p theorem prove an upper bound on opt(n) at
n = 8p and n = 12p, p a prime, that a game reaches at 103 and 73 games of the proven chain and at 89 and 63 games past
5060, so each of those games is optimal if the game before it is (the 12p games given statement U).  For the largest
target left, the exchange law (at an odd n that displaces one kept source x, δ(n) = x; 10.0% of the chain's search time
and 185 searched games past 5060), the study proved the structure and no theorem, and the hole law that would have split
it from n (the game n − 1 played without x scores opt(n − 1) − x) is false at all 11 games tested.  The laws also pointed
the miner at short best-known games: one play each raised three of them by exactly the predicted amounts, and 12 games
rose by 277 points in all.

A rule of this kind turns "game n is probably optimal" into "game n is optimal if game n − 1 is".  That is the claim the
unsound mode's objective needs, since a proof of a game past 5060 costs about tenfold more for every 476 points of the
root's gap, and the gaps there run from 2,090 to 11,686
([root bounds](../search/root-bounds-for-the-odd-cores-past-5060-2026-11/README.md),
[proofs one game at a time](../proofs-past-5060-one-game-at-a-time-2026-11/README.md)).

## Method

### The words

*Game, ceiling, shortfall.*  Game n is Taxman on the numbers 1 to n, and opt(n) is its best score; [the
glossary](https://github.com/bvchess/taxman/blob/e5258cd/docs/GLOSSARY.md#the-game) defines the game and its ceiling.
[The ceiling lemma](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/neighbors.md#the-ceiling-lemma) says
opt(n) is at most the ceiling, so δ(n) is at least 0.  An *optimal set* is the set of moves of an optimal game.

*Proven, best-known and the miner.*  The chain proves games 1 to 5060, past 2531 given statement U.  Past 5060 each game
has a *best-known* score, the highest the unsound mode has found, with no proof.  The unsound mode plays those games again
and again and keeps a play's score when it beats the best-known one; this entry calls that mining, and the program that
does it the miner.

*Statement U.*  A number's *layer* is its number of prime factors, counted with multiplicity, and a *source* is a number
above n/2.  U\*(n) is the set of sources that descending greedy keeps.  [Statement
U](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/exactness.md#statement-u) says that some optimal set of
game n holds every member of U\*(n) in layers 3 and up.  It is open, and holds at every game the prover has proved, to
2531.

*Kinds of step.*  Primes, games at their ceiling and repeats of an earlier game's root problem need no search.  A game
that does is of one of three kinds, by how U\* changes from n − 1 to n:

* a *relaxation*: an even n whose half n/2 was in U\*(n − 1);
* a *restriction*: an odd n that takes a spare factor of its
  [frame](https://github.com/bvchess/taxman/blob/e5258cd/docs/GLOSSARY.md#the-frame-model), so that U\* gains n alone;
* an *exchange*: an odd n that displaces one member x of U\*, always the *shadow* of n, which is n with each prime
  factor replaced by the prime just below it (the shadow of 4953 = 3·13·127 is 2·11·113 = 2486).

*Playability.*  A set of moves is *playable* when some game plays all of its members.  In a playable set each move x is
paid by its own maximal factor, one of the numbers x/s with s a prime.  A move *lists* its maximal factors that are not
moves themselves, and a *core* is a set of moves in which every factor that one lists is listed by another; a set that
holds a core is not playable.
[The theory](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/playability.md#payment-schemes) defines payment
schemes, layer instances and cores.

*The single-loss rule.*  Take the recorded optimal set of game n − 1, add n, and give up the one move of smallest value
that makes the set playable.  Its score is a lower bound on opt(n).

*The exchange law.*  The study's name for the observation that at every exchange step δ(n) = x, the displaced source.

*The 8p and 12p laws.*  For n = 8p and n = 12p, with p a prime and r the prime before p, the shortfall is 4r and 6r at
nearly every proven game (111 of 114 and 78 of 81 searched games).  A *law* is such an observation, until a theorem
proves it; the *law's score* at a game is opt(n − 1) + n less its amount.

*Promotion sets.*  Given statement U, an optimal set of game n is U\*(n) with a heaviest *promotion set*, a set of
numbers up to n/2 that U\*(n) can carry; P\*(n) is the sum of that set.

### The work

A brief ([brief.md](brief.md), with its scripts and tables) collected how the proven games were settled and
which rules exist.  The study read it, wrote its report ([study-report.md](study-report.md)) and asked the coordinator
for experiments, which the coordinator ran.  Two referees, readers who had not seen the study's reasoning, checked the
two theorems, one of them also the text that the theory carries.  All of it ran on 2026-11-10, in Pacific time.

| label | what it does | ran | rule fixed before it ran |
|---|---|---|---|
| brief | tables of how every proven game was settled, of the single-loss rule and of the increments; the rules that exist; what failed | 19:47 to 20:21 | none |
| mining | the laws, read against the best-known file, and one play of each game they flag | 20:21 to 21:21 | none |
| study, round 1 | the 8p theorem, the mechanism of 12p, the structure of the exchange law, the hole law | 20:21 to 21:21 | none |
| E3 | the 8p theorem against the best-known games past 5060, and against the chain: a peel check, no solver | to 21:21 | every game must pass |
| referee of the 8p theorem | the proof step by step, and the recorded optimal set of every covered game | 21:21 to 21:30 | none |
| E1 | the hole law at the 11 cheapest searched exchanges | 21:35 to 22:20 | equality at all 11 makes the hole law the target; an excess at one says the exchange law needs n itself |
| 12p theorem, first draft | the 12p mechanism and its cases, one case open | 21:38 | none |
| referee of the 12p theorem | pass 1, the first draft; pass 2, the closed case; pass 3, the theory file as written | 21:54 to 23:26 | none |
| E2 | the 12p cases with 6p fixed in and 4p barred, at four games | 22:09 to 22:21 | a best score at or below the law's score confirms the law at the game, given U; one above it is a counterexample |

## Results

### The experiments against their rules

| experiment | result | against the rule |
|---|---|---|
| E3 | the 8p bound is reached at 103 of 103 covered games of the chain and at 89 of 89 past 5060 | confirms |
| E1 | the hole law is false at 11 of 11 games | the hole law is killed, and the exchange law needs n itself |
| E2 | the best score equals the law's score at 4 of 4 games, which it could not have failed | confirms, vacuously |

### How the proven games were settled

**The search time of the chain went to games that fell far below their ceiling, so a sharper ceiling settles almost
nothing.**  Of the 5,059 proven
games 2 to 5060, 677 are settled by the prime formula, 1,630 by the ceiling, 995 as repeats below the ceiling and 12
trivially, and 1,745 by search.  The 1,745 searched games took all 10,149 CPU-hours of the chain, and the 10 dearest
hold 54.6%.  The searched games within 10, 30, 100, 300 and 1,000 points of their ceiling hold 0.3%, 0.6%, 2.6%, 25.2%
and 30.2% of that time, and of the 25.2% within 300, 15.2 points are two games (4983, δ = 246, and 5054, δ = 121).  The
median δ is 0.32 n.  So a rule has to find δ(n) itself, about a third of n.  Past 5060, by the best-known scores, 552
games are primes, 1,705 are at their ceiling, 973 are repeats and 1,710 need a search.

**Three kinds of step need searches.**

| kind | searched games, 2 to 5060 | share of their CPU | searched games, 5061 to 10000 |
|---|---|---|---|
| relaxation | 1,169 | 61.8% | 1,096 |
| restriction | 497 | 28.3% | 429 |
| exchange | 79 | 10.0% | 185 |

The even n whose half was not in U\*(n − 1) (1,136 games) are all at their ceiling.  The 995 repeats below the ceiling
are all exchanges, and so are the repeats past 5060 (973).

**The single-loss rule is optimal at 3,829 of the 4,954 games 2 to 4955, and short at 1,125.**  With the games to 5060
it is optimal at 3,911 of 5,059.  It holds at 598 of the 1,745 searched games, 30.9% of their time, and at every
exchange, where the move it gives up is the shadow; where it fails it misses by a median of 180 points.

**The parity bound's own increment predicts δ without settling it.**  Its rank correlation with δ over the searched
games is 0.99, and it is equal at 758 of the 1,745 (38.8% of their time).  But the gap between the parity bound and
opt(n) falls from n − 1 to n at 466 searched games, down to −550, so the inequality a proof would need is false in
general.

**Where a simple formula fits δ.**  δ(n) is the shadow at the 79 searched exchanges and at 96 restrictions (2.8% of the
time), and it is n/2 with its largest prime replaced by the prime before it at 215 relaxations (5.1%), among them 111 of
the 114 searched games 8p and 78 of the 81 games 12p.  No formula fits the other 914 relaxations and 393 restrictions,
which hold 81.6% of the time.  The targets of the study are the exchange law (10.0%) and the two families 8p and 12p
(4.9%): together 14.9% of the chain's time and 337 of the 1,710 searched games past 5060.

### The 8p theorem

**At n = 8p, game n falls at least 4r short of its ceiling, where p is a prime and r the prime before it.**  The factor 8
can pay for only one of n and 8r.  In game n − 1 it pays for 8r, which leaves 4r free to be a move.  In game n it pays
for n, so 8r pays with 4r, and 4r is lost.  The study's reports write P, P₁ and t′ where the repository writes p, r and
t; this entry uses the repository's letters.

**Statement.**  This is L2 of [docs/theory/below-the-ceiling.md](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/below-the-ceiling.md#the-8p-theorem)
(master e5258cd).  Let n = 8p ≥ 187 with p a prime, let r be the largest prime below p, and suppose that 9r > n.  Then
opt(n) ≤ opt(n − 1) + n − 4r.  It holds on the whole board, with no statement U.  So a game of n that scores
opt(n − 1) + n − 4r is optimal, and the game of n − 1 with 4r exchanged for n is such a game wherever it is playable.

**Proof idea.**  Delete n from an optimal set of game n, and put back one of 4p, 4r and 8r in game n − 1: it pays with a
factor that n paid with, or that only one other member lists, and that member has a factor of its own to move to ([the
re-payment lemma, L1](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/below-the-ceiling.md#the-re-payment-lemma)).
The number put back is worth at least 4r, so opt(n − 1) ≥ opt(n) − n + 4r.

**Coverage.**

* In the proven chain, 103 of the 114 searched games 8p meet the hypotheses (the other 11 are 24, 40, 56, 88, 104, 136,
  152, 184, 232, 296 and 424, which all fail 9r > n but 152, which is below 187).  They hold 1.95% of the chain's search
  time.  At all 103, from 248 to 5048, the recorded optimal set of n − 1 with 4r exchanged for n is playable and scores
  opt(n) (E3 on the chain, and the referee's own check).
* Past 5060, all 89 games 8p meet them.  At all 89 the best-known game of n − 1 less 4r plus n is playable and
  best-known(n) = best-known(n − 1) + n − 4r (E3, [e3_best_known_out.txt](study/e3_best_known_out.txt)).  So each is
  optimal whenever the game before it is, with no search and no statement U.  Two of the 89, 8696 and 9304, reached the
  bound only after the law flagged their predecessors 8695 and 9303 as short and the miner raised them
  ([the mining](#the-law-guided-mining)).

**The referee found the proof correct.**  Every step lies within the hypotheses of the lemmas it cites, and the case
split is exhaustive.  One point the text left implicit is closed: a re-paid member gains no new edge out, because in a
layer instance "f divides b" means "b lists f", and nobody else lists f.  The referee's checks ran on its own code, which
decides playability by the residual of an instance and shares nothing with the study's peel: the arithmetic facts for
all 5,121 primes 29 to 50,000 with 9r > n, and the proof walked on the recorded optimal set of each of the 103 games.
All 103 fall in one sub-case, 4p and 8r in the set and 6r a move, so the other cases rest on the proof, the referee's
audit by hand, and 235 of the study's random promotion sets of 2008, 2056, 2104 and 5048 (155 in case A and 80 in case
B), none of which failed.

**Where the hypotheses enter.**  The bound n ≥ 187 enters only through the square theorem (F10), which says that from
187 on no optimal set plays a number of layer 2 up to n/2.  The bound 9r > n keeps 3r listed by 6r alone.  Some hypothesis
is needed: game 184 = 8·23, which meets neither, rises by 136 over game 183, more than the 184 − 76 = 108 that the bound
allows.  The hypotheses are sufficient and not sharp: games 152, 232, 296 and 424 rise by exactly n − 4r all the same.

### The 12p theorem

**At n = 12p, game n falls at least 6r short of its ceiling, given an optimal set that holds four numbers.**  The factor
12 can pay for only one of n and 12r.  In game n − 1 it pays for 12r, which leaves 6r free to be a move.  In game n it
pays for n, so 12r pays with 6r.

**Statement.**  This is L4 of [docs/theory/below-the-ceiling.md](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/below-the-ceiling.md#the-12p-theorem).
Let n = 12p ≥ 187 with p a prime, let r be the largest prime below p, and suppose that 15r > n.  If some optimal set of
game n holds 8p, 8r, 12r and 8t for a prime t with 4p/3 < t ≤ 3p/2, then opt(n) ≤ opt(n − 1) + n − 6r.  Statement U at n
supplies such a set when the four lie in U\*(n), which the setup checks, and that is the only place U enters.

**Why n cannot lose less.**  [The cycle
lemma](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/below-the-ceiling.md#the-cycle-lemma) (L3) says that a
playable set holding 8p, 8r, 12p and 12r holds at most one of 6p and 6r, since the four share four factors in a cycle.  So
the cheaper loss that looks possible, giving up 4t (smaller than 6r at 15 of the 73 covered games of the chain, by 2 to
26 points), is never available: the game of n − 1 with 4t exchanged for n is unplayable at 1668, 2004 and 4308, with
residual exactly 8r, 8p, 12r and 12p.

**Coverage.**

* In the proven chain, 75 games 12p of 228 to 5052 are searched.  73 meet the hypotheses (228 has no 8t in U\*(n), and 348
  has 15r ≤ n), and at all 73 the bound is the law's, given U at n.  They hold 2.94% of the chain's search time.  The
  first is 276.
* Past 5060, all 63 games 12p meet them: 41 from 5061 to 8191, whose U\* the arrival file gives, and 22 from 8192 to
  10000, by descending greedy.  Each is optimal whenever the game before it is, given U at n.  Their best-known scores
  meet the law.

**The referee made three passes (21:54 to 23:26).**

* *Pass 1, on the first draft (22:11).*  Two gaps, both closed.  Case B1 of the draft, which holds all 73 proven games,
  had been asserted ("as proved above") and not proved, and the referee supplied the proof.  And 14r lists 2r when 14r ≤ n, as at
  276 and 444, which the layer-3 step had left out; 14r is re-paid with 7r, which only it lists.  Two lesser points: a
  remark about a prime t₀ was not justified (it is unused), and the statement said "every optimal set" where one
  suffices.  The draft proved the full bound only where 4t ≥ 6r, and δ ≥ 4t at the others, 15 of the 73 games of the
  chain and 15 of the 63 past 5060.
* *Pass 2, on the closed last case (22:32).*  The study closed that case, where 12r pays with 6r in every scheme, by the
  referee's closed-walk argument: a cycle in the new scheme would give one in the old.  The referee found the step
  correct, and asked that the case say "12 is a move, unpaid, or paid by some 12s", the two trivial shapes it had left
  out.  633 random layer-4 instances of that case at six games failed none (374 with 12 a move, 259 with 12 paid by some
  12s).  After this pass δ(12p) ≥ 6r holds in every case.
* *Pass 3, on the theory file (23:26).*  The file's text as written, L1 to L4, which had its case structure rewritten
  (one fixed payment scheme, case A1 dropped), is correct.  Two wording notes were fixed.

The referee's checks ran on its own code.  The arithmetic facts held for the 5,125 primes 19 to 50,000 with 15r > n, and
14r ≤ 12p at exactly two of them, 276 and 444.  The proof walked on the recorded optimal set of each of the 73 games found
all 73 in case B1 (6p a move, 4r not, and 12p able to pay with 12), so the other cases rest on the proof and on 682 random
layer-4 instances (68 more were unusable), none of which failed.  The numbers the theory file states were checked too:
the examples at 248 and 372, the failures at 184 and 204, and the games that reach the bound exactly although a
hypothesis fails.

**Where the hypotheses enter.**  The bound n ≥ 187 enters only through F10.  The bound 15r > n is binding only where it
keeps 5r listed by 10r alone, and the prime t enters in two cases, through 9t > n, which keeps 3t listed by 6t alone, and
through 8t ≤ n.  Some hypothesis is needed: game 204 = 12·17, with r = 13 and t = 23, meets all but 15r > n, and rises by
129 over game 203, more than the 204 − 78 = 126 that the bound allows.  Nor are they sharp: games 156, 228 and 348 rise by
exactly n − 6r.

### The exchange law

**What the study proved about the exchange law is its structure, and no proof of the law.**  The law says that at every
exchange step δ(n) = x, the shadow of n.  It holds at all 1,074 exchanges of 2 to 5060 (995 repeats and 79 searched) and at
all 185 searched exchanges past 5060 by the best-known scores.  The semiprime formula (J3) proves it in layer 2, where a
weight-preserving bijection of playable sets exists, and in the cases of repeats given statement U.  In layer 3, where
73 of the 79 searched exchanges lie, it is open.  What was established:

1. *A reduction (proved given U at n and n − 1).*  At an exchange of layer 3, opt(n) = opt(n − 1) + n − x if and only if
   P\*(n) = P\*(n − 1), because from 187 on only the layer instance at 3 differs between the two games.  The lower
   bound is a game (the single-loss rule holds at all 79 searched exchanges), so only opt(n) ≤ opt(n − 1) + n − x is
   open.  At all 73 searched layer-3 exchanges of 2 to 5060 the recorded heaviest promotion sets of the two games are the
   same set, and a promotion set of both boards.
2. *The families of promotion sets differ (measured), so no theorem about whole families can prove the law.*  Of 100
   random maximal promotion sets of each board and game, 14% of the sets of n are not sets of n − 1 on average (0% to 53%,
   at 67 of the 73 games), and the same the other way (0% to 68%, at 63 of the 73); a check of the whole board at 741,
   1209, 2301 and 4953 agrees, with 8 to 15 of 40 sets.  J3's method cannot reach layer 3, and the brief's corner sketch, which
   would cut the proof's obligation to the sets that use up every payer of x, is vacuous there: on board n every payer of
   x divides a box number that the set holds, so no payer is ever free at the end of a game.
3. *The box (measured).*  Write n = pqr, p ≤ q ≤ r primes, and p′, q′, r′ for the primes just below.  The GF(2) circuit of
   n's vector in U\*(n − 1) is the *box* {p′, p} × {q′, q} × {r′, r}, eight numbers with n among them (six when two
   primes coincide), less n.  Each of the box's twelve layer-2 numbers, such as p′q′, is listed by exactly two of its
   numbers, and x = p′q′r′ is the smallest.  This holds at 196 of the 201 exchanges of 3 to 8191 (searched or repeat);
   at the other 5, where two consecutive primes of n coincide, the circuit is a prism or a smaller cycle inside the box.
   The other members of the box lie in U\*(n − 1) at all 201.
4. *The pair lemma (proved).*  Let a and b be members of an instance, e a factor listed by a, by b and by no other member,
   with no other factor in common.  Replacing a and b by one member that lists the rest leaves the instance with a core
   exactly when it had one.  For exchanges with p = 3 the box's pairs of numbers are such pairs, and the box reduces to a
   four-cycle of four virtual members: boards n and n − 1 differ only in which of two opposite corners, N and X, is
   present, and the law says that the heaviest set outside the box weighs the same with either.  For p of 5 or more (12
   of the 73 searched exchanges, 46 of the 185 past 5060) the pairs do not exist, and the box stays uncontracted.
5. *An augmenting path inside the box (proved as stated).*  On board n − 1 the box needs one hub edge each for three pairs
   of its members, a hub edge being a layer-2 number such as 2q′ that many numbers of layer 3 list.  If the members outside the box keep their payments, the box can be re-matched from the three hub edges
   that the optimal set of n uses only under a condition on which of the box's four pairs of hub edges they lie in (the
   report's Section 3.6), as at 741 and 2301; otherwise it needs a fourth hub edge that nobody outside the box pays with.  A
   proof has to show that a heaviest set never spends all four edges outside the box, and nothing in the weights makes that
   obvious.
6. *The box law (measured; [boxlaw_out.txt](study/boxlaw_out.txt)).*  For each of the 303 odd n of layer 3 in 189 to 5060
   whose box less n lies in the optimal set of n − 1, the game of n − 1 less the box's smallest member plus n gives
   δ(n) ≤ that member, and it holds at all 303.  Equality holds at all 78 where the member is a source (73 searched
   exchanges and 5 repeats), and at 92 of the 225 where it is a promotion; at the other 133, δ is smaller by 1 to 240
   points, because a dropped promotion returns to the pool of the layer above, where it can pay for a number that was
   blocked, and a dropped source returns nothing.  So the exchange law says that the hub edges of a dropped source never
   buy anything back.
7. *The hole law, a cleaner sufficient condition (a proved reduction, given U at n).*  Let Y be board n − 1 without the
   hole x.  An optimal set S of n has exactly U\*(n) as its sources, so x is not in S, and S less n is playable on board
   n − 1 and, since x is a source, on Y.  Hence opt(n) ≤ n + opt(Y), and the hole law, opt(Y) = opt(n − 1) − x, would give
   the exchange law's upper bound.  E1 below tests it.

**If proved,** the law would settle the 79 searched exchanges of 2 to 5060 (10.0% of the chain's time; 6 of them in layer
2, already covered by J3) and 185 of the 1,710 searched games past 5060, and the 973 repeats there would rest on the law
instead of on statement U.  It stays open, and E1 shows its proof has to be global.

### E1: the hole law

*Question.*  At each exchange step n of the list, does board Y = {1, …, n − 1} without x, the shadow of n, score
opt(n − 1) − x at best?  A strict excess at one game would say the exchange law needs n itself.

*Method.*  The frame solver, through a new example program `restricted`, solves Y as an exact standalone search (no seed,
no ceiling, no near-repeat cut).  The model is sound for a board with holes by [the holes theorem
(X9)](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/exactness.md#boards-with-holes), which needs no
hypothesis on the holes.  The answer, ΣU\*(Y) plus the best promotion sum, is the score of a legal game of Y, replayed
by the program's referee on Y, so an excess over opt(n − 1) − x needs no assumption.  An equality would need some best
game of Y to play all of U\*(Y), which setup cannot check.  The 11 games are the cheapest searched exchanges, 741 to
2301.  Two checks came before any measurement:

* On 2,925 boards (n = 1 to 60 with no hole, with each single hole, and with 520 random pairs and 515 random triples of
  holes), the frame model's answer equals the heaviest set found by a walk over the playable sets (X9's statement, which
  needs no U), the best score by exhaustive search, and U\* made again by descending greedy; every comparison agreed.
* With no holes, nothing changed: the fingerprint of the setup of every board 1 to 10,239 is the same byte for byte
  before and after the commit, `taxman regress --to 1000` matches the table at all 1,000 games, and `verify-results`
  accepts all 5,060 games of the committed chain.

*Results.*  16 threads at idle priority; each search completed, the longest in 23 minutes of CPU at 2301.

| n | x | opt(n − 1) | opt(Y) | opt(n − 1) − x | excess | nodes |
|---:|---:|---:|---:|---:|---:|---:|
| 741 | 374 | 172,899 | 172,767 | 172,525 | +242 | 24 |
| 1083 | 578 | 369,966 | 369,726 | 369,388 | +338 | 161 |
| 1209 | 638 | 460,433 | 460,252 | 459,795 | +457 | 4,502 |
| 1599 | 814 | 805,436 | 805,304 | 804,622 | +682 | 17,091 |
| 1677 | 902 | 885,956 | 885,868 | 885,054 | +814 | 25,840 |
| 1729 | 935 | 941,678 | 941,348 | 940,743 | +605 | 119,648 |
| 1767 | 986 | 981,744 | 981,540 | 980,758 | +782 | 15,319 |
| 1833 | 946 | 1,055,687 | 1,055,643 | 1,054,741 | +902 | 108,266 |
| 2067 | 1034 | 1,346,448 | 1,346,345 | 1,345,414 | +931 | 37,635 |
| 2139 | 1102 | 1,442,915 | 1,442,764 | 1,441,813 | +951 | 68,464 |
| 2301 | 1166 | 1,668,926 | 1,668,661 | 1,667,760 | +901 | 7,333,543 |

The hole law fails at all 11 games, by 242 to 951.  A separate Python referee replays every set by the plain rules on Y
and agrees with each score, with no legal move left.

*How Y does better.*  At six games Y plays the recorded set of n − 1 with x exchanged for one smaller number y, a
promotion, and the excess is y: 578 for 338 at 1083, 814 for 682 at 1599, 902 for 814 at 1677, 935 for 605 at 1729, 986
for 782 at 1767, and 946 for 902 at 1833.  The number y is x with its largest prime lowered, to the prime below at five of
them, and from 17 to 11 at 1729.  At 741 the set drops 374 and 44 and plays 286 (242 = 286 − 44).  At the other four, 3
to 13 numbers change.  In every case the set plus n is unplayable on board n, with a core of 13 to 78 members that holds
n, one, three or five other members of the box, and the added promotion; and the set less its additions plus n is
playable ([e1_cores_out.txt](study/e1_cores_out.txt)).  So what n forbids is not a local pattern: the numbers that fit on
Y through the hub edges that x released are taken back, when n arrives, through the box's r-side along a long chain.

*Verdict.*  The hole law is killed, and the exchange law needs a global proof.

### E2: the 12p cases with a candidate barred

*Question.*  The 12p theorem's first draft left one case open, with 6p promoted and 4p not.  Does the best score of
that case at the games where 4t is smaller than 6r (1668, 2004, 2316, 2748) stay at or below opt(n − 1) + n − 6r?

*Method.*  The same program with `solve N --fix 6p --bar 4p`: the exact standalone search whose root promotes 6p over the
other candidates less 4p, so its answer is the heaviest promotion set that holds 6p and not 4p.  Checks first: on every
board 1 to 120, each candidate barred, each fixed, and each of the 16,362 pairs, 18,660 restricted problems, equal the
heaviest promotion set found by a walk over the playable sets that shares nothing with the search, and on 117 boards a
number up to n/2 that is no candidate, barred, was refused; on boards 300, 500, 700, 1000 and 1667 the recorded promotion
set fixed in whole scores opt(n), and each of its 237 members barred scores at most opt(n).

*Results.*  The best score equals opt(n − 1) + n − 6r at all four games and never passes it: 878,104 at 1668, 1,264,085 at
2004, 1,692,121 at 2316 and 2,377,810 at 2748, in 1 to 40 s.  8p, 8r and 12r are in U\*(n) at each, and none of the four
best sets promotes 4r.

*Verdict.*  Confirms, and could not have failed.  The law's score at these games is the committed score of game n, which
is ΣU\* + P\*, and no restricted problem scores more than the whole problem; the recorded optimal set of each already
promotes 6p and not 4p.  The case it was to test was closed by proof in pass 2.  No further run is wanted.

### The law-guided mining

**A theorem that bounds opt(n) from above is also a test of the game before it.**  If the best-known score of n exceeds
the bound that the best-known score of n − 1 gives, then n − 1 is short.  For 8p the theorem is proved, so a flag is a
proof that the game before is short, and so is one of the 12p law, given statement U.  The other laws are fits to the
proven games, and a flag is a hint.

*The laws read.*  [scan.py](lawscan/scan.py) fits δ(n) = k·r by the cofactor n/p, with p the largest prime factor of n, at
least 50, and r the prime before p, on the proven searched games.  It keeps a law that holds at 95% or more of at least 10
games; [scan2.py](lawscan/scan2.py) reads the exchange law and the weaker laws.  On the best-known file of 20:42:

| law | proven searched games where it holds | past 5060 |
|---|---|---|
| 8p, δ = 4r | 100 of 100 | all 89 hold |
| 12p, δ = 6r | 67 of 67 | all 63 hold |
| 39p, δ = 22r | 16 of 16 | all 23 hold |
| exchange, δ = the shadow | all 1,074 | all 1,158 steps hold (185 searched, 973 repeats) |
| 49p, δ = 25r | 11 of 12 | flags 5537, 6223 and 6419: the games before them are short by 5, 68 and 36 if the law holds |
| 40p, δ = 18r | 13 of 15 | flags 7960: 7959 is short by 2 if the law holds |

The 8p, 12p and 39p laws, the strong laws, cover 175 games past 5060.  On the gap dashboard's file of 2026-11-09 the 8p and
12p laws had four misses there: 9304, 9564, 9924 and 9732.  On the best-known file of 20:21 three of them met the laws,
the unsound mode having raised games since, and 9304 still beat the 8p law by 34.

*The plays.*  One play of a flagged game is a level-4 play of the unsound mode on 12 threads at idle priority, with
`--stop-growth off` and seed 41 ([play.sh](lawscan/play.sh); [what a level of
effort is](https://github.com/bvchess/taxman/blob/e5258cd/solver/docs/unsound/play.md#the-level-of-effort)).  A raised game
is also a lower bound on the game below it, since opt(n − 1) ≥ opt(n) − n, so the 8 games below each gain were played at
level 3, seed 41, the descent ([the
descent](https://github.com/bvchess/taxman/blob/e5258cd/solver/docs/unsound/shortfalls.md#the-descent), the push-down).

| game | best-known before | after | gain | flagged by | play |
|---:|---:|---:|---:|---|---|
| 9303 | 27,215,375 | 27,215,409 | +34 | 9304 beat the 8p law by 34 | level 4 |
| 8695 | 23,781,993 | 23,782,049 | +56 | 8696 beat the 8p law by 56 | level 4 |
| 7959 | 19,941,458 | 19,941,460 | +2 | 7960 beat the 40p law by 2 | level 4 |
| 8694 | | | +61 | below 8695 | push-down |
| 9300, 9301, 9302 | | | +34 each | below 9303 | push-down |
| 7953, 7954 | | | +8 each | below 7959 | push-down |
| 7956, 7957, 7958 | | | +2 each | below 7959 | push-down |

The three gains of the level-4 plays are exactly the amounts the laws predicted, and the 12 games together rose by 277
points (34 + 56 + 2 + 61 + 102 + 16 + 6).  The push-down below 7959 raised five of its eight games, and the one below
7953 raised none.  The 49p flags, 5536 (short by 5 if the law holds), 6222 (68) and 6418 (36), did not rise on seeds 41
and 42 at level 4, so the 49p law likely fails there.  The miner's ordinary list of 375 plays, from 12:16 to 21:52,
raised 2 games by 127 points, none in its last 142 plays.  After the gains all 152 games 8p and 12p past 5060 meet their
laws.

## Limits

* **Past 5060 the games are best-known.**  Each game "optimal if the game before it is" rests on the best-known score of
  the game before it being optimal.  The 12p results also rest on statement U at n.
* **Both theorems rest on F10's computation.**  The square theorem is proved by computation for the finite part, so
  n ≥ 187 inherits its standing.
* **The chain exercises one case of each proof.**  All 103 games 8p fall in one sub-case, and all 73 games 12p in case B1;
  the other cases rest on the proofs, the referees' audits and random instances.
* **The theorems' hypotheses are sufficient.**  Games 152, 232, 296 and 424 (8p) and 156, 228 and 348 (12p) reach the
  bound with a hypothesis failing, and no theorem covers them.
* **E1's excesses are lower bounds.**  Each is a legal game on Y, so the true excess is at least as large, and an
  equality would need a best game of Y to play all of U\*(Y).
* **The programs are not proved correct.**  The evidence is the checks of each: the 2,925 boards, 18,660 restricted
  problems and the setup fingerprint of 10,239 boards of E1 and E2, and the referees' own code.
* **The mining is one seed and one play a game.**  The 49p result is two seeds at level 4, not a refutation.  The laws
  were read on the best-known file of 20:42, and the file has changed since.
* **Four small counts of the study's report differ from its outputs, and this entry uses the outputs.**  For the 8p proof
  the report says 160 random sets in case A and 76 in case B; the outputs show 155 and 5, and 75 more in case B.  It says
  that 4t is smaller than 6r at 20 of 71 games; the output shows 15 of the 73 covered games.  It says that the cores of
  E1 hold "three or five" other box members; one game has one.  And it says that y is x with its largest prime lowered to
  the prime below; at 1729 it is lowered from 17 to 11.

## Decision

Both theorems are in the repository: the 8p theorem first as N8 of `neighbors.md` (master
[5725a83](https://github.com/bvchess/taxman/commit/5725a83)), then, with the 12p theorem and the two lemmas that both
proofs use, as L1 to L4 of
[docs/theory/below-the-ceiling.md](https://github.com/bvchess/taxman/blob/e5258cd/docs/theory/below-the-ceiling.md)
(master [e5258cd](https://github.com/bvchess/taxman/commit/e5258cd)).  `tests/below_the_ceiling.rs` checks both on the
committed chain, and the failures at 184 and 204.  The solver does not use them, and no rule of it changed.  The
mining is unchanged, and the scans are kept in [lawscan/](lawscan/).  The tool of E1 and E2 is not merged and is kept as
patches ([patches/holes-e1/](patches/holes-e1/)).  No further run of E2 is wanted.

What stands: the two theorems, the structure of the exchange law, and the failure of the hole law.

What would reopen it:

* a global proof of the exchange law, which would settle 10.0% of the chain's time and 185 searched games past 5060, and
  take statement U from the 973 repeats; the study's pointer is the Hall condition on four hub edges, that a heaviest set
  never spends all four outside the box;
* a theorem of the same pattern for another family: the 39p law holds at 16 of 16 proven games and at all 23 past 5060,
  and the 40p and 49p laws at 13 of 15 and 11 of 12;
* a rule for the 914 relaxations and 393 restrictions with no formula (81.6% of the chain's time), where the price of room
  for n is a global quantity, or the brief's open directions that the study did not take (a bound on the parity bound's
  increment, a relative bound at the nodes of a search);
* a game past 5060 that violates a theorem's bound, which would show a best-known score of its predecessor to be short.

## Files

The work ran in the scratch folder `lab/work/succession/`, whose files these are, with their paths as they were there.
The scripts run as `nice -n 19 python3 -I SCRIPT` from this folder, use the standard library only, and read the committed
results, the gap dashboard's `games.csv`, the best-known file and the notebook's arrival and single-loss files, which are
not copied.  The copies of [brief.md](brief.md), [study-report.md](study-report.md) and the two referees' notes are
verbatim, but for the following.  The notes were `check-8p/referee.md` and `check-12p/referee.md`, and they, the report
and the scripts cite each other by those names and as `../study-report.md`; here they are `referee-8p.md`,
`referee-12p.md` and `study-report.md`, and the three citations of that kind in `referee-12p.md` are rewritten to
these names.  The files held no mention of the model that wrote the reports, so none was replaced.
Four retired words were replaced by their current terms: in the brief, "all cores" by "every core" and "The
exact solver (the *frame solver*)" by "The *frame solver*", and in `referee-8p.md`, "free factor" by "unpaid factor" and
by "factor of its own".  The study's reports write P, P₁ and t′ for the repository's p, r and t.

* [brief.md](brief.md): the research brief the study read (rules, tables, worked examples, directions).
  [common.py](common.py) (loaders, number tables, peel, the residual), [test_peel.py](test_peel.py) →
  [test_peel_out.txt](test_peel_out.txt) (peel against all orders on every set of at most 6 members of boards 2 to 12,
  every recorded optimal set playable), [settle.py](settle.py) → [settle_out.txt](settle_out.txt),
  [settle.csv](settle.csv) and [past5060.csv](past5060.csv) (Tables 1 and 2),
  [single_loss_tail.py](single_loss_tail.py) → [single_loss_tail.jsonl](single_loss_tail.jsonl) and
  [single_loss_tail_out.txt](single_loss_tail_out.txt) (the rule on 4956 to 5060), [analyze.py](analyze.py) →
  [analyze_out.txt](analyze_out.txt) and [searched.csv](searched.csv) (Tables 3 and 4 and the formulas), and
  [examples.py](examples.py) → [examples_out.txt](examples_out.txt) (the worked examples).
* [study-report.md](study-report.md): the study's report, Sections 1 to 8.
* [referee-8p.md](referee-8p.md) and [referee-12p.md](referee-12p.md): the referees' notes.  The checks are in
  [check-8p/](check-8p/) (`referee_check.py` and its output, and `theorem-8p.md`, the draft the referee read) and
  [check-12p/](check-12p/) (`referee_check.py`, `referee_check_g2ii.py` for the closed case, the output of both in
  `referee_check_out.txt`, and `theorem-12p.md`).
* [study/](study/): the study's scripts and outputs, which the report cites.  `exch.py` → `exch_first_out.txt` (it ends in
  the traceback of an invalid argument after its games) and `exch_all_out.txt` (the 73 searched layer-3 exchanges);
  `promsets.py` → `promsets_out.txt` and `promsets_full.py` → `promsets_full_out.txt` (the families of promotion sets);
  `boxes.py` → `boxes_out.txt`, `boxlaw.py` → `boxlaw_out.txt`, `edges.py` → `edges_out.txt` and `improve.py` →
  `improve_out.txt` (the box); `eightp.py`, `eightp_check.py`, `eightp_cases.py` and `eightp_caseb.py` and their outputs
  (the 8p proof), with `coverage_out.txt` (the counts of games meeting the hypotheses, whose script was not kept as a file);
  `twelvep.py` → `twelvep_all_out.txt`, `twelvep_hyp.py` and `twelvep_hyp_tail.py` and their outputs, `twelvep_out.txt` and
  `twelvep_min_out.txt` (the 12p games; the two `twelvep_hyp` outputs count by the first draft's bound, min(6r, 4t));
  `e3_best_known.py` → `e3_best_known_out.txt` (E3); `e1_cores.py` → `e1_cores_out.txt` (the cores of E1);
  `cofactor.py` (the step c·p − 1 to c·p).
* [e1-holes/](e1-holes/) and [e2-bars/](e2-bars/): E1 and E2, each with its README.md (the question, the option, the
  checks and the results as the builder wrote them).  `run-e1.sh` and `run-e2.sh` run the games, `e1.jsonl` and `e2.jsonl`
  are the result lines, `e1-show.jsonl` the same solves with their moves, `e1-referee.txt` the Python referee's replay,
  `check-holes-*.txt`, `check-bars-*.txt` and `check-chain*.txt` the checks before them, `digest.base.txt` and
  `digest.new.txt` the setup fingerprints (equal), `regress-1-1000.txt` and `verify-results.txt` the two other checks of
  the build without holes, and the `.err` files each search's progress lines.
* [lawscan/](lawscan/): [scan.py](lawscan/scan.py) and [scan2.py](lawscan/scan2.py) (the laws; they print to the
  terminal, and no output was kept, so the table above is from the decisions log of 20:42), [play.sh](lawscan/play.sh)
  (one play of a game into the best-known file) and [ledger-rows.tsv](lawscan/ledger-rows.tsv): the rows of the miner's
  ledger for the nine level-4 plays of this entry (game, level, seed, known score before, score after, time of day).
* [patches/holes-e1/](patches/holes-e1/): the three commits of E1 and E2 as `git am` patches (see Commits).

Not copied: the binaries of E1 and E2 in `lab/work/succession/e1-holes/` (`restricted`, 63.6 MB, which the patches
build, `taxman.holes-e1`, 74.4 MB, and `setup_digest.base` and `setup_digest.new`, 13.4 and 14.7 MB), six empty `.err`
files of the checks, the `__pycache__` folders, the miner's best-known file and its ledger but for the nine rows above,
and the logs of the push-down plays (their gains are from the decisions log of 20:42 and 21:02).

## Commits

The branch `holes-e1` of the research repository was never pushed, and is to be deleted after this entry, so `git show`
may not find its commits.  The patches rebuild its tip, tree 40d32bf6, from master's e36cd09, which holds the first
proven games past the chain; they were made with `git format-patch --no-merges -o patches/holes-e1 holes-e1 ^master`, and
apply in order with `git am`.

* 943a945 (21:41): the example `setup_digest.rs`, a fingerprint of the setup of every board of a range, so that two
  builds that print the same lines set every board up the same way.
* 57d7491 (22:05): restricted problems of the frame model: a board with holes (X9), and candidates barred or fixed at the
  root.  `Tables::with_holes`, the setup of a board with holes, `Prepared::restricted`, `game::replay_with_holes`,
  `brute::solve_by`, and the example `restricted.rs` with the checks above.  7 files, 669 lines added and 26 removed.
  The binaries of E1 and E2 were built from it.  Its message ends in mid-sentence ("and the built-in table").
* 997305b (22:24): the example formatted as the crate is, with no change to what it does.

On master of the research repository, in the same hours:

* [5725a83](https://github.com/bvchess/taxman/commit/5725a83) (22:30): the 8p theorem as N8 of `neighbors.md`, with its
  tests in `tests/bottom_layers.rs`.
* [e5258cd](https://github.com/bvchess/taxman/commit/e5258cd) (23:26): `docs/theory/below-the-ceiling.md`, L1 to L4, and
  `tests/below_the_ceiling.rs`.

The commit that adds this entry also adds its rows to the register's files of [the theory and the
prover](../register/theory-and-the-prover.md) and [the unsound mode](../register/unsound-mode.md), and one sentence to
the register's row of the single-loss rule.
