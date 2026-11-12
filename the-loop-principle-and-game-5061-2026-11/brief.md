# Loops: one mechanism behind the shortfall

*A research brief, written 2026-11-11, an addendum to the succession brief
(/home/brian/taxman_work/lab/work/succession/brief.md, cited as "S" with its section numbers).  The game, opt(n), the
frame model, U\* and statement U, the parity bound PB, the shortfall δ(n) = opt(n − 1) + n − opt(n), δ_PB, rise, gap
(S 1.1-1.4) and the kinds of searched step (S 2.2) are S's and are not defined again.  Facts are marked *proved* or
*measured*; "best-known" means the highest score found, not proven.*

## 0. The question in one page

**The question.**  The rules that settle game n from game n − 1 (S 3) look like one mechanism in several shapes.
Making room for n costs δ(n), and the cost seems set by a small cluster: n and its prime-shifted neighbors (Section 1),
such as the box of eight numbers of 741 = 3·13·19 down to its shadow 374, the numbers 8r, 4p, 4r around the hub 8 for
n = 8p (r the prime below p), and the 4-cycle over 4p, 4r, 8, 12 for n = 12p.  n closes the cluster into a loop, and
δ(n) is the value of the member forced out.  The side conditions of the 8p and 12p theorems (9r > 8p, 15r > 12p) say
the loop is clean; at 184 and 204 a detour (9r, 15r) breaks the bound.  The exchange law (δ = the shadow at every
exchange: 1,074 of 1,074 to 5060, and every searched one past it) holds although its loop is not clean: E1 found
detours of 13 to 78 members that the optimum never takes.  The study's task: state the principle precisely, find how
far it reaches, prove what it can, find the property behind the exchange law, and judge whether the gap above the
parity bound is a sum of such loop losses.

**What the data add** (Section 4; measured unless marked):

1. **One forced-out member is too narrow.**  The single loss in the cluster is exact at 463 of the 1,745 searched games
   of 2..5060, 20.4% of the chain's CPU, half of it the exchanges; no rule that loses one cluster member can pass 498
   games (20.6%).
2. **The loss cascades along prime shifts.**  Write the numbers near n as k·P_j, P_j the j-th prime below n's largest
   prime P.  n takes a small factor (a *hub*) from its payer, the payer re-pays inside its column, the move that frees
   takes a hub from the column below, and so on (Section 5.1).  At 1,045 of the 1,692 searched games from 187 (69.9% of
   the CPU) every move that changes lies within three primes of P, and a crude cascade predictor is exact at 569
   (30.8%), as often as the single-loss rule.  Each cofactor repeats a pattern, such as δ(16P) = 8P₁ + 6P₂ + 4P₃ −
   6P₁ − 4P₂; fitted on 187..5060, the patterns of 39 families agree with 691 of their 828 searched games past 5060.
3. **Cleanliness is measurable**: the window is clean to depth d when the columns of P₁ to P_d hold only the rows that
   P's column holds.  Where it is clean to a pattern's depth, the patterns of 8P, 12P, 16P, 20P, 24P and 40P are exact
   at 450 of 450 games of both ranges.
4. **The loops are even cores, not odd ones**: each shared factor is listed twice, so the lists sum to zero over GF(2),
   and the parity bound sees the loop (Section 2).  rise = 0 at all 264 searched exchanges and all 333 searched 8P and
   12P from 205, both ranges; and in windows clean to depth 2, at 181 of 182 relaxations and restrictions of the chain
   (9.9% of the CPU).  The sharpest candidate is the parity form: in a clean window the gap does not change, so
   δ(n) = δ_PB(n), computable in seconds.
5. **So the gap is not a sum of loop losses.**  It changes only at unclean steps, both ways.  The dearest game, 4983
   (10.8% of the CPU), has δ_PB = 0 and δ = 246: the parity bound sees no loop, yet the change is a regular pattern
   of eight moves that its family 33P repeats.
6. **By-products.**  25 games past 5060 in clean windows have rise ≠ 0, flagging a best-known score that may be short
   (5061 by 492 points if the parity form holds); and a pattern game of 7944 beats its best-known score by 4.

So the question changes in two ways: "one member forced out" becomes "a cascade along the columns", and the loop
principle turns out to be the parity bound's own exchange, so the target is S 7.4's question, when the gap cannot
change, with a local test of cleanliness.

## 1. Words added to those of S

* **prev(p)** is the prime just below the prime p; 2 has none.  The **shifts** Sh(m) are the numbers made from m by
  replacing any of its odd prime factors, counted with multiplicity, by prev(p), m included: Sh(39) = {39, 26, 33, 22}.
* The **cluster** C(n) is Sh(n) and Sh(f) for each maximal factor f of n, less n.  For 741 it holds the box less 741;
  for n = 8P (P prime) it is {8P₁, 4P, 4P₁, 8}; for 12P, {12P₁, 8P, 8P₁, 6P, 6P₁, 4P, 4P₁, 12, 8}.  P₁ = prev(P).
* **Cells and columns.**  P = P₀ is the largest prime of n, P₁, P₂, … the primes below it, P₋₁, P₋₂, … those above.
  w is the *cell* (k, j), in *row* k of *column* j, when w = k·P_j with P_j the largest prime of w.  n is the cell (c,
  0), c = n/P its cofactor.  Small numbers such as 4, 6, 8, 16 are *hubs*: the hub k is a maximal factor of every
  cell of row k and pays for at most one of them.  The **window is clean to depth d** when (c + 1)·P_i > n for
  1 ≤ i ≤ d: columns 1 to d hold exactly the rows k ≤ c, as column 0 does.  9r > 8p is clean to depth 1 for c = 8.
* **The change.**  D is the set of moves of the optimal set of n − 1 that the optimal set of n gives up, A the moves it
  takes up besides n, so δ(n) = ΣD − ΣA, on the recorded sets (committed to 5060, best-known past it; from 425 on a game
  can have several optimal sets, so the sizes are upper bounds).  When every member of D and A is a cell with
  |j| ≤ 12, the two lists of cells are the change's **pattern**, a formula δ = Σ_D k·P_j − Σ_A k·P_j that can be
  evaluated at any n of the same cofactor.

## 2. The principle, in candidate precise forms

Four forms, from narrow to wide.  S is an optimal set of n − 1.

* **(F1) The single loss in the cluster.**  β(n) is the smallest y in C(n) ∩ S with S − y + n playable (peel).  That
  set is a game of n, so δ(n) ≤ β(n) (proved); the principle is equality.  Simpler variants: the *shift* (the shadow
  for odd n, n/2 with P lowered to P₁ for even n) and the smallest member of C(n) ∩ S.
* **(F2) The family law.**  For each cofactor c one pattern π_c gives δ(cP) for every prime P whose window is clean
  to π_c's depth.  L2 and L4 are π₈ = [4P₁] and π₁₂ = [6P₁]; the exchange law is π = [the shadow] for the exchange
  cofactors; the data show longer ones, like π₁₆ = [8P₁ + 6P₂ + 4P₃] − [6P₁ + 4P₂].
* **(F3) Locality.**  Some optimal sets of n and n − 1 agree outside n and the cells of a window of small depth, so δ(n)
  is a finite optimization over the window with the rest of the board fixed, and cleanliness says the rest of the
  board offers no way around.
* **(F4) The parity form.**  δ(n) = δ_PB(n): the gap does not change from n − 1 to n.

**Why (F4) belongs with the others.**  The cluster is a core whose lists sum to zero over GF(2), since each shared
factor is listed by exactly two members: an *even* core in S's words (S 1.2), a circuit of one of the parity
matroids (S 1.4).  For 8P with 4P and 4P₁ moves, the parity-1 vectors of 8P, 8P₁, 4P and 4P₁ are e(4P) + e(8),
e(4P₁) + e(8), e(4P) and e(4P₁), which sum to zero; the six numbers of the cycle lemma L3 do the same; the box of an
exchange is a circuit at parity 0 (S 2.2).  So the parity bound cannot hold the whole loop either, and measured, its
increment is the game's at every clean loop seen: rise = 0 at all 79 searched exchanges and at all 106 searched 8P
and 75 searched 12P of 205..5060 (settle.csv), and at the cascades of Section 5.1 and 5.2.  The gap above the parity
bound is made of odd cores (the notebook's anatomy-of-the-gap entry: odd cores of two- and three-factor movers in
frames 1 to 3), which a clean loop does not create.

**Cleanliness, in the proofs.**  In L2 and L4 the side conditions serve one step: a number that joins T = S − n in game
n − 1 pays with a factor whose other listers each have a factor of their own (the re-payment lemma L1).  9r > 8p keeps
3r for 6r alone, 15r > 12p keeps 5r for 10r alone: column 1 has no row beyond c that lists what the loop needs.  The
clean depth of Section 1 is the simplest test of this kind that a script can apply.

## 3. What is proved already

* The prime formula N5, the simplest loop: C(p) = {prev(p)} and δ(p) = prev(p), on the whole board.
* The semiprime formula J3 (docs/theory/arrival.md): for odd n ≥ 189 with two prime factors, δ(n) is the smallest
  other member of the cycle n closes with U\*₂(n − 1), on the whole board (the shadow by the shadow law, measured).
* The 8p theorem L2 (docs/theory/below-the-ceiling.md): n = 8p ≥ 187 and 9r > n give δ(n) ≥ 4r, on the whole board.
  With the single-loss game it settles 103 searched games of 2..5060 (1.95% of the CPU) and, by E3, all 89 searched 8p
  past 5060 once their predecessors are proven.
* The cycle lemma L3 and the 12p theorem L4: n = 12p ≥ 187, 15r > n, and an optimal set of n holding 8p, 8r, 12r and
  8t for a prime t in (4p/3, 3p/2] (which U gives when the four lie in U\*(n)) give δ(n) ≥ 6r: 73 searched games of
  2..5060 (2.94%) and 63 past 5060, given U at n.
* The re-payment lemma L1, the tool of both proofs.  Upper bounds on δ, each a game: n/2 for even n, x_min, β.
* For the exchange law (S 7.1; the succession study's report, sections 1 and 3): given U at both games it is
  P\*(n) = P\*(n − 1); the promotion sets of the two games differ (14% on average), so a proof must use optimality;
  the pair lemma reduces the box with smallest prime 3 to a 4-cycle; the hole law fails at all eleven games of E1.

## 4. The tables

Sources: tables_out.txt, patterns_out.txt and chain.jsonl, made from predict.jsonl (Section 8).  The searched games are
S's 1,745 of 2..5060 (all of the chain's 10,149 CPU-hours) and 1,712 of 5061..10000 by the current best-known file
(not prime, below the ceiling, not a repeat: 1,095 relaxations, 432 restrictions, 185 exchanges, 12 of them odd
semiprimes that J3 settles).  Past 5060 δ is best-known(n − 1) + n − best-known(n), so a hit there is agreement with
best-known scores.  CPU shares are of the whole chain.

### 4.1 The predictors (Table 1)

A predictor *hits* a game when its value equals δ(n).  Hits, and their share of the CPU:

| predictor | 2..5060 (1,745) | relax (1,169) | restrict (497) | exchange (79) | past 5060 (1,712): relax / restrict / exchange |
|---|---|---|---|---|---|
| shift (shadow or half) | 390 (17.9%) | 215 (5.1%) | 96 (2.8%) | 79 (10.0%) | 475: 165 / 125 / 185 |
| smallest member of C(n) ∩ S | 456 (20.3%) | 275 (7.3%) | 102 (3.1%) | 79 (10.0%) | 559: 241 / 133 / 185 |
| β (F1) | 463 (20.4%) | 281 (7.4%) | 103 (3.1%) | 79 (10.0%) | 569: 249 / 135 / 185 |
| δ is the value of a member of C(n) | 498 (20.6%) | 305 (7.4%) | 114 (3.2%) | 79 (10.0%) | 600: 255 / 160 / 185 |
| cascade (from 187: 1,692) | 569 (30.8%) | 361 (16.3%) | 135 (4.5%) | 73 (10.0%) | 289 of the 728 of 5061..7160 (β 228, x_min 281): 162 / 61 / 66 |
| x_min (any single move of S) | 598 (30.9%) | 379 (10.3%) | 140 (10.6%) | 79 (10.0%) | 711: 369 / 157 / 185 |
| δ_PB (F4) | 758 (38.8%) | 482 (17.6%) | 197 (11.3%) | 79 (10.0%) | 910: 499 / 226 / 185 |
| family's commonest pattern, game left out (F2; from 187: 1,692) | 509 (23.3%) | 331 (16.1%) | 112 (3.5%) | 66 (3.7%) | 738: 413 / 188 / 137 |
| pattern of the family's previous searched game (from 187) | 441 (38.5%) | 295 (15.2%) | 88 (19.5%) | 58 (3.7%) | 877: 494 / 209 / 174 |
| β, cascade or either pattern (from 187) | 673 (50.7%) | 422 (18.6%) | 178 (22.1%) | 73 (10.0%) | 970: 545 / 240 / 185 (cascade to 7160) |

The *cascade* (chain.py) starts from a single loss in C(n), or a cluster member moved down its row, then moves
members of columns 1 to 4 up one column while the set stays playable: a game, so δ ≤ cascade ≤ β.  Past 5060 the
family patterns are fitted on 187..5060 alone, so that column is out of sample.  The previous pattern's 19.5% in
restrictions is more than half 4983 (10.8%, Section 5.3).  Of the rules that read only the prime-shifted neighbors, β
covers most; the cascade, which lets the loss move along the columns, matches the single-loss rule (from 187: 569 games
and 30.8% against 561 and 30.9%, each catching about 120 games the other misses, 10.4% and 10.5% of the CPU); δ_PB
alone beats them all (Section 4.5).

**By layer** (β; hits / searched, and the share of the class's CPU the hits hold): layer 3 restrictions 93/315 (15.2% of
a class with 18.7% of the CPU), layer 4 relaxations 203/434 (35.6% of 13.8%), layer 5 relaxations 41/383 (9.8% of
22.7%), layers 6 to 11 relaxations 37/346 (about 1% of 25.3%), layers 4 and 5 restrictions 7/163.  The loops reach the
low layers; the high ones have large cofactors, whose windows are never clean.

### 4.2 Families where one predictor is exact (Table 2)

Exact from n₀: it hits every searched game of the cofactor from n₀ on, both ranges, with at least 5 games after n₀:

| cofactor | law | from | games after n₀: chain + past | misses before n₀ |
|---|---|---|---|---|
| 8 | 4P₁ (the half; L2) | 232 | 106 + 89 | 24, 40, 184 |
| 12 | 6P₁ (the half; L4) | 228 | 75 + 63 | 60, 84, 204 |
| 96 | 48P₁ (the half) | 3936 | 3 + 12 | seven, the last 3552 |
| 152 | 68P₁ (β: the shadow of the half 76P) | 2888 | 4 + 7 | none |
| 39, 57, 65, 69, 91, 93, 119, 133 | the shadow | 1599, 1083, 3835, 4209, 2821, 2883, 2737, 2527 | 19+23, 16+17, 5+15, 4+13, 6+13, 6+12, 5+10, 5+9 | restrictions |
| 16, 25, 45 | δ_PB | 2608, 2225, 4815 | 28+49, 23+32, 2+18 | 14, 9, 11 |

The odd rows are exchange families (39p is the question's "39p law"); their misses below n₀ are all restrictions, and
from n₀ on the shadow is exact at their restrictions and exchanges alike.  No other even cofactor has an exact
one-member law.

### 4.3 Locality and the family laws (Table 3)

**Locality (F3).**  Of the 1,692 searched games of 187..5060, 1,045 (69.9% of the CPU) have every member of D and A
within three primes of P: relaxations 694 (34.5%), restrictions 278 (25.4%), exchanges 73 (10.0%); within twelve,
1,594 (96.3%), though for large cofactors twelve primes span most small numbers.  Past 5060, 1,310 and 1,599.  |D| +
|A| is 1 at 560 games, 2 to 5 at 547.

**Family laws (F2).**  The commonest pattern of each cofactor's searched games of 187..5060 is a candidate law.  The 39
families with at least 4 games on one pattern have 508 hits holding 23.6% of the CPU, and agree with 691 of their 828
searched games past 5060.  Selected rows ("clean": to the pattern's depth; hits / games of both ranges):

| c | pattern: δ = | chain hits / searched (family's CPU) | past | exact from (games) | clean, not clean |
|---|---|---|---|---|---|
| 8 | 4P₁ | 106/106 (1.95%) | 89/89 | 232 (195) | 192/192, 3/3 |
| 12 | 6P₁ | 75/76 (2.94%) | 63/63 | 228 (138) | 127/127, 11/12 |
| 16 | 8P₁ + 6P₂ + 4P₃ − 6P₁ − 4P₂ | 36/60 (2.67%) | 49/49 | 3664 (65) | 53/53, 32/56 |
| 20 | 10P₁ + 6P₂ + 9P₂ − 6P₁ − 10P₂ | 7/50 (0.71%) | 36/41 | 6940 (27) | 43/43, 0/48 |
| 24 | 12P₁ + 10P₂ − 10P₁ | 16/42 (0.55%) | 30/34 | 8088 (13) | 22/22, 24/54 |
| 40 | 18P₁ | 18/28 (0.13%) | 23/23 | 5080 (23) | 13/13, 28/38 |
| 21 | 10P − 9P = P | 7/47 (1.66%) | 34/39 | 6951 (25) | depth 0 |
| 25 | 9P₁ (the shadow) | 19/40 (2.11%) | 29/32 | 8275 (12) | 36/45, 12/27 |
| 33 | 10P + 12P + 16P₁ − 12P₁ − 16P | 4/28 (11.06%) | 0/8 | none | 0/9, 4/27 |

In clean windows the patterns of 8, 12, 16, 20, 24 and 40 are exact (450 of 450); elsewhere they hit about half.  At
35P and 45P one move is exchanged for a lighter one of its column (δ = 3P, 2P).  56P and 64P, whose families hold 10.5%
and 4.9% of the CPU, have patterns of five and three cells, exact only from 7672 and 8768 (patterns_out.txt).

### 4.4 Where the loop rules fail (Table 4)

β misses at 888 relaxations (54.4% of the CPU) and 394 restrictions (25.2%), by a median of 246 and 250 (1-10 at 50
games, 11-100 at 278, 101-300 at 372, 301-1,000 at 353, more at 224); at 5 restrictions no single cluster loss makes
room.  What breaks cleanliness, as far as the scripts can say:

* **An unclean window.**  755 of the 869 relaxation misses from 187, and 343 of the 386 restriction misses, have
  (c + 1)·P₁ ≤ n.  Large cofactors are never clean.
* **Detours through extra rows are a minority.**  A member of D or A in a row beyond c (a number that exists because
  the column is not clean, like 9r at 184) appears at 210 of the 869 relaxation misses (5.8% of the CPU) and 94 of the
  386 restriction misses (0.8%).
* **A cascade landing elsewhere.**  Seven of the eleven misses of the 16P pattern from 1000 on are the pattern with
  its last cell 4P₃ replaced by another cell of row 4 (at 1136, 1328, 1552, 1616, 2192, 3568, 3632); at all seven, and
  at 1168 and 4976, the cell given up is the move that pays with the hub 4 in a peel scheme of the set of n − 1.  So
  δ(16P) = 8P₁ − 6(P₁ − P₂) − (4P₂ − h₄), h₄ the holder of the hub 4 in game n − 1, reaches the unclean games too.
* **A blind parity bound.**  At 13 restrictions 33P from 3333 on (six in the chain) δ_PB = 0 while δ is 88 to 386.

### 4.5 The parity form and clean windows (Table 5)

rise = 0 at the searched games from 187, by clean depth (patterns_out.txt; chain CPU of the games in brackets):

| step | depth 0 | 1 | 2 | 3 | 4 or more |
|---|---|---|---|---|---|
| relax, chain | 202/850 (52.7%) | 75/110 (1.5%) | 49/50 (1.7%) | 28/28 (1.0%) | 96/96 (4.8%) |
| restrict, chain | 148/431 (14.3%) | 32/46 (11.6%) | 6/6 (2.1%) | 2/2 (0.3%) | - |
| exchange, chain | 70/70 (9.6%) | 3/3 (0.4%) | - | - | - |
| relax, past | 207/741 | 38/81 | 37/54 | 30/32 | 187/187 |
| restrict, past | 142/336 | 37/43 | 30/34 | 14/16 | 3/3 |
| exchange, past | 158/158 | 26/26 | - | - | 1/1 |

**In a window clean to depth 2 the gap does not change.**  Relaxations and restrictions of 187..5060 clean to depth 2:
rise = 0 at 181 of 182 (9.9% of the CPU; cofactors 8, 12, 16, 18, 20, 21, 24, 25).  The exception, 2512 = 16·157, has
rise 98 > 0 and obeys the 16P pattern: the law holds and the parity bound underprices it.  Past 5060: 301 of 326.  At
the other 25 the law fails or a best-known score is short (a rise above 0 points at n, below 0 at n − 1); they are
listed in patterns_out.txt.  Five are 21P (5061, 5943, 6153, 6573, 6657), the only games of that family from 4683 on,
besides 5019, that do not lose exactly P; their best-known δ exceeds δ_PB by 492 to 764.

**β and the gap.**  Where β hits, rise = 0 at 432 of 463 games; where it misses, rise = 0 at 326, rise > 0 at 507
(39.4% of the CPU), rise < 0 at 449 (19.9%).  gap(5060) = 2,557 = 3,636 from the searched games − 1,079 from twenty
games at the ceiling.

**Judgment on the gap.**  A clean loop is a GF(2) circuit that the parity bound prices exactly, so the gap changes only
at unclean steps, and there in both directions.  The gap is not a sum of loop losses: it is a running sum of the
defects of unclean steps, the part of the price of room for n that no circuit shows (rise > 0), less the part of an
earlier defect that n's arrival dissolves (rise < 0).

## 5. Worked examples

From examples_out.txt (examples.py): committed sets and scores, and the payments of one scheme that peel finds.  Each
re-payment can be checked by hand; playability of the whole set rests on peel.

**5.1 A cascade of three steps: 1168 = 16·73**, with P₁, P₂, P₃ = 71, 67, 61.  In game 1167, 1136 = 16P₁ pays with the
hub 16, the move 568 = 8P₁ with 284 = 4P₁, 852 = 12P₁ with 426 = 6P₁, the move 402 = 6P₂ with the hub 6, 804 = 12P₂
with 268 = 4P₂, and the move 244 = 4P₃ with the hub 4.  In game 1168, n pays with 16, so 1136 pays with 568, no longer
a move; 852 moves to the freed 284; 426 becomes a move and takes the hub 6 from 402, no longer a move; 804 moves to
402; 268 becomes a move and takes the hub 4 from 244, which is given up.  Each column repeats two re-payments one prime
lower.  δ = 568 + 402 + 244 − 426 − 268 = 520 = 429,072 + 1,168 − 429,720.  β = 568, the half; δ_PB = 520.

**5.2 A loss that moves down: 1060 = 20·53**, with P₁, P₂, P₃ = 47, 43, 41.  In game 1059, 940 = 20P₁ pays with the hub
20, the move 470 = 10P₁ with the hub 10, 860 = 20P₂ with 430 = 10P₂, and 820 = 20P₃ with 164.  In game 1060, n pays with
20, so 940 pays with 470, no longer a move, and the hub 10 passes to 410 = 10P₃, a move now, since 430 still pays 860.
δ = 470 − 410 = 60 = 10(P₁ − P₃), against β = 470 and x_min = 423; δ_PB = 60.

**5.3 The dearest game: 4983 = 3·11·151**, 1,094 CPU-hours.  P₁ = 149, and t = 157 is the prime after P.  Given up:
1510 = 10P, 1812 = 12P, 2384 = 16P₁, 2355 = 15t; taken up: 1413 = 9t, 1788 = 12P₁, 2198 = 14t, 2416 = 16P.
δ = 6P + 4P₁ − 8t = 906 + 596 − 1256 = 246.  n pays with 1661 = 11P, which 3322 = 22P had used; 3322 moves to
302 = 2P, which 1510 had used.  The residual of S(4982) + 4983 has 148 members, yet eight moves change, in six rows of
three columns.  δ_PB = 0: all of δ is a rise of the gap.  The same formula, t one or two primes above P, gives δ at
4587 and at 5181, 5511, 5709, 6963 and 7953 (best-known); β = 3322 and x_min = 1510.

## 6. Open directions

* **The parity form in clean windows.**  Conjecture: for n ≥ 187 clean to depth 2, gap(n) ≥ gap(n − 1), that is
  opt(n) ≤ opt(n − 1) + PB(n) − PB(n − 1).  True at all 182 relaxations and restrictions of 187..5060 it covers.  With
  a game at that score it settles n by one matroid intersection.  The window's cells (rows k ≤ c, columns 0 to 2) form
  one finite configuration for all large P, and L2 and L4 are its first two cases.
* **Family laws by one template.**  L2 and L4 delete n from an optimal set of n and put back cluster cells through
  re-payments.  The 16P, 20P, 24P and 40P patterns are exact in clean windows; a proof would put back the pattern's
  cells, and since each clean family is one finite picture, the case analysis could be generated and checked by a
  program, cofactor by cofactor.
* **The exchange law.**  The loop is the box, a circuit; the change is the one source x at all 264 searched exchanges
  (|D| + |A| = 1); rise = 0 at all of them.  So the law says the gap cannot fall at an exchange.  E1 shows the cost is
  global, so the property is not local cleanliness.  A candidate: the cores of boards n and n − 1 that hold the box
  correspond under x ↔ n with equal defects, since the boards differ only in which opposite corner of the pair lemma's
  4-cycle is present.
* **Where the parity bound is blind.**  The 33P restrictions with δ_PB = 0 follow δ = 6P + 4P₁ − 8t.  A proved lower
  bound on δ there would be the first rule that sees an odd core; 4983 alone is 10.8% of the CPU.
* **Cascades as alternating paths.**  Each step takes a factor from its payer, which takes another or stops being a
  move.  The cheapest such path whose precedence stays acyclic is a computable predictor between β and δ; chain.py's
  cascade is a crude version.

## 7. What a useful answer looks like

* **A precise principle with a proof for a family**: the clean-loop principle in form F2, F3 or F4 (or a better one),
  with a cheap test (from n's factorization, the game of n − 1, or the parity bound) and a proof for a family beyond 8p
  and 12p, saying what it rests on (the rules alone, U, (♦)).  It is judged by the share of the 1,745 searched games of
  2..5060 and of their CPU that it settles, and of the 1,712 past 5060 that it covers.  The clean-window parity form
  alone would settle about 10% of the chain's CPU.
* **Or the property behind the exchange law**, sharp enough to test: 10.0% of the CPU and 185 searched games past 5060,
  and with it the 973 repeats past 5060 would rest on the law instead of on U.
* **A judgment on the gap**: whether the defects of unclean steps can be bounded, and how.
* **Experiments**, which the coordinator runs: light scripts at once, and the experimental solver of E1 and E2
  (/home/brian/taxman_work/lab/work/succession/e1-holes/README.md and e2-bars/README.md), which solves boards with
  holes and root problems with candidates fixed in or barred.  One run it suggests: the best change inside a window,
  every promotion outside the window fixed to those of n − 1, which measures locality free of the recorded sets'
  arbitrariness.

## 8. Files

All in /home/brian/taxman_work/lab/work/loops/.  Each script runs as `nice -n 19 python3 -I SCRIPT` there, uses the
standard library and ../succession/common.py (peel, the residual, the loaders), and only reads its inputs: the committed
results, the best-known file /home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl (as of 2026-11-11 04:07
PST), the gap dashboard's games.csv (PB, 2..10000), and ../succession/settle.csv and past5060.csv.

* `predict.py` → `predict.jsonl`: a line per searched game: δ, δ_PB, step, layer, cofactor, CPU, the shift, β, x_min
  (1,745 of 1,745 agree with S's searched.csv), D and A; its `load_rows()` drops the eleven repeats past 5060.
* `chain.py` → `chain.jsonl`: the cascade, every searched game of 187..5060 and 5061..7160; it was stopped there
  (the games past 5060 take seconds each) and resumes where it stopped.
* `tables.py` → `tables_out.txt`: Tables 1 and 2, layers, failures, change sets, the parity cross-tables, detours.
* `patterns.py` → `patterns_out.txt`, `patterns.jsonl`: column form, the pattern predictors, Tables 3 and 5, the
  flagged games past 5060, the deviations from each family's pattern.
* `examples.py N ...` → `examples_out.txt`: Section 5.  `explore.py C ...`: a family's change sets in cells.
* `improve.py` → `improve_out.txt`, `improved.jsonl`: every family pattern applied to the best-known game of n − 1
  past 5060; one game, 7944, scoring 19,854,251, 4 above its best-known score, refereed by replay.
