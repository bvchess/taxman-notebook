# Succession study: settling game n from game n − 1

*Study report, 2026-11-10.  Scripts and outputs are in `study/` beside this file; every script runs as
`nice -n 19 python3 -I study/SCRIPT` from the succession folder and reads only the brief's inputs.*

Each claim below is marked **proved** (from the rules of the brief and the theory docs), **proved given U** (statement
U at the games named), or **measured**.  "Best-known" means an unproven top score.

## 1. The exchange law in layer 3: what it is really about

**Setting.**  n odd of layer 3, U\*(n) = U\*(n − 1) − x + n, with x the displaced source.  Write A = U\*_3(n − 1),
A′ = U\*_3(n) = A − x + n, and Q for the numbers of layer 2 up to n/2 (the same on both boards, since n is odd).

**Reduction (proved given U at n and n − 1).**  Given U at n, an optimal set of n is U\*(n) ∪ L with L a heaviest
promotion set of n (U\* is a maximal playable set of sources, so an optimal set that contains U\*_{≥3} has exactly U\*
as its sources, by F4 for layer 2); and from 187 on no promotion lies in layer 2 (F10), so the only layer instance that
differs between U\*(n) ∪ L on board n and U\*(n − 1) ∪ L on board n − 1 is layer 3's: members A′ ∪ L_3 against A ∪ L_3,
both over the full pool Q.  Hence, given U at both games,

    the exchange law  opt(n) = opt(n − 1) + n − x   ⟺   P\*(n) = P\*(n − 1),

and a sufficient condition is that some heaviest promotion set of n is a promotion set of n − 1 (upper bound) and
some heaviest one of n − 1 is one of n (lower bound; this is the single-loss rule with x_min = x, measured at all 79).

**Measured (`study/exch_all_out.txt`, all 73 searched layer-3 exchanges of 2..5060):** U holds at n and n − 1; the
recorded heaviest promotion sets of n and n − 1 are the *same set*; it is a promotion set of both boards.

**Measured, and decisive for the shape of a proof (`study/promsets_out.txt`, `study/promsets_full_out.txt`):** the
families of promotion sets are *not* the same.  Over all 73 searched layer-3 exchanges (100 random maximal sets of
layer 3 per board and game), 14% of the sets of n are not sets of n − 1 on average (0% to 53%; some difference at 67
of the 73 games), and the same the other way round (0% to 68%); the full-board check at 741, 1209, 2301, 4953 agrees
(8 to 15 of 40 sets).  So no theorem of the form "Prom(Π_n) = Prom(Π_{n−1})" exists; the law is a
statement about the *heaviest* set only, and a proof must use optimality (an improvement argument), not a bijection of
playable sets as in J3.

**The circuit is a box (measured on every layer-3 exchange, searched or repeat, of 3..8191; `study/boxes_out.txt`).**
Write n = pqr (p ≤ q ≤ r primes) and p′, q′, r′ for the primes just below.  The GF(2) circuit of v(n) in A is the
*box* {p′, p} × {q′, q} × {r′, r} less n: eight numbers (six when two primes coincide), every one of their twelve layer-2
edges listed by exactly two of them, x = p′q′r′ its smallest member.  At 196 of the 201 exchanges the circuit is the
whole box less n; at the 5 others two consecutive primes of n coincide (7473 = 3·47·53, 7429 = 17·19·23, ...) and the
circuit is a prism or a smaller cycle inside the box.  In every case the seven other box members lie in U\*(n − 1).

**Private pairs (proved, for p = 3).**  Let n = 3qr with x = 2q′r′ > n/2.  Then each of the four edges qr, q′r, qr′,
q′r′ is listed by exactly two numbers of the board, its two box multiples (t·qr ≤ 3qr forces t ∈ {2, 3}, and
x > n/2 forces q′r′ > 3qr/4, so t·q′r′ ≤ 3qr forces t ∈ {2, 3}; the other two by the same count).  In a layer-3
instance that holds both members of such a pair, the pair behaves as one member listing the other four edges:

> **Pair lemma (proved).**  In an instance let a and b be members, e a factor listed by a, b and no other member, and
> L(a) ∩ L(b) = {e}.  Replace a and b by one member c listing (L(a) ∪ L(b)) ∖ {e}.  The instance has a core iff the
> new one has.  *Proof.*  A core holding a holds b (e needs a second lister) and conversely; T ↦ T − a − b + c and
> its inverse carry cores to cores, since every factor other than e that a or b lists is listed by some third member
> of a core (L(a) and L(b) meet only in e), and a core avoiding a and b never lists e.  ∎

So given U, with R the members outside the box, T + n (board n) reduces to R + N + V₁ + V₂ and T + x (board n − 1) to
R + X + V₁ + V₂, where the virtual members list N = {2q, 3q, 2r, 3r}, X = {2q′, 3q′, 2r′, 3r′},
V₁ = {2q′, 3q′, 2r, 3r}, V₂ = {2q, 3q, 2r′, 3r′} (3q′r′ is free on board n and 2qr on board n − 1, each with a private
edge).  The two boards differ only in which of the two opposite corners N and X of this 4-cycle is present.  The
exchange law says: the heaviest R is worth the same with either corner.

## 2. The 8P law, proved on the whole board: δ(8P) ≥ 4P₁

**Theorem 8P (proved; no U, no (♦)).**  Let n = 8P with P prime, n ≥ 187, and P₁ the prime before P, with
9P₁ > 8P.  Then opt(n) ≤ opt(n − 1) + n − 4P₁.  Hence if a game of n scores opt(n − 1) + n − 4P₁ (the single-loss
game S\*(n − 1) − 4P₁ + 8P, checked by peel), then δ(n) = 4P₁ exactly, and n is settled from n − 1.

*Facts used.*  (i) mf(8P) = {4P, 8}; 4P is listed (as a maximal factor) by 8P alone on board n, since 12P > n.
(ii) mf(8P₁) = {4P₁, 8}; 4P₁ is listed by 8P₁ alone, since 12P₁ > 8P (from 9P₁ > 8P).  (iii) mf(4P₁) = {2P₁, 4};
2P₁ is listed by 4P₁ and 6P₁ alone (10P₁ > 8P); 3P₁ is listed by 6P₁ alone (9P₁ > 8P); mf(6P₁) = {6, 2P₁, 3P₁}.
(iv) mf(4P) = {2P, 4}; 2P is listed by 4P and 6P alone (10P > 8P); 3P by 6P alone (9P > 8P).  (v) F4/F10 at n:
an optimal set S of n holds no number of layer 2 up to n/2 and S₂ = U\*₂(n), so in S's layer-3 instance the pool is
every number of layer 2 up to n/2, and 4, 2P, 3P, 2P₁, 3P₁ are in it.  (vi) The layer theorem F3; the precedence of
P2 (a → b when pay(a) | b; within one layer instance a | b never happens); the extension lemma P6.  (vii)
*Re-payment:* if a member a of an instance lists a factor f that no other member lists, changing pay(a) to f keeps
a scheme's precedence acyclic (a's out-edges a → b, pay(a) | b, disappear; nothing else changes) and frees a's old
payment.  (viii) A subset of a playable set is playable, and S − 8P is playable on board n − 1 (the ceiling lemma N4's
argument: 8P is in no pool, and (n − 1)/2 drops only 4P, which is in no list of S − 8P by (i)).

*Proof.*  Let S be an optimal set of n and T = S − 8P, playable on board n − 1 by (viii), so ΣT ≤ opt(n − 1) at
least; we show ΣT ≤ opt(n − 1) − 4P₁, which gives opt(n) = ΣT + 8P ≤ opt(n − 1) + n − 4P₁.  (That S plays 8P is
monotonicity N3.)

*Case A: 4P ∉ S.*  Then T + 4P is playable on board n − 1, so ΣT + 4P ≤ opt(n − 1) and ΣT ≤ opt(n − 1) − 4P <
opt(n − 1) − 4P₁.  Indeed 4P is a source of board n − 1 (4P > (n − 1)/2), so it enters no pool, and only the
layer-3 instance changes: it gains the member 4P, listing 2P and 4 by (v).  If 6P ∉ T, 2P is listed by no member of
T (iv) and P6 applies.  If 6P ∈ T, re-pay 6P with 3P (private to it, (iv), (vii)); then 2P is paid by nobody, so
pay(4P) = 2P extends the scheme; its new edges are 4P → 6P (2P | 6P) and a → 4P for the member a paying 4, if any,
and 6P has no out-edge (3P divides no member), so no cycle passes through 4P.

*Case B: 4P ∈ S.*  In S's layer-4 instance 8P lists {8} only, so pay(8P) = 8 and 8 ∉ S.  Sub-case B1: 8P₁ ∈ S.
Then 8P₁ lists {4P₁, 8} ∖ S; if 4P₁ ∈ S both 8P and 8P₁ would list {8} alone, a core; so 4P₁ ∉ S and pay(8P₁) = 4P₁.
We show T + 4P₁ is playable on board n − 1, whence ΣT + 4P₁ ≤ opt(n − 1).  By F3 check the layer instances of
T + 4P₁; only layers 3 and 4 change.  *Layer 4:* members T₄ = S₄ − 8P, pool as S's less 4P₁; the only member that
listed 4P₁ is 8P₁ (ii).  Take S's layer-4 scheme restricted to T₄ (acyclic, 8 unused) and set pay(8P₁) = 8: 8P₁
gets no in-edge (nobody pays 4P₁ or 8 besides itself), so no cycle passes through it.  *Layer 3:* members
T₃ + 4P₁ = S₃ + 4P₁, pool every layer-2 number up to (n − 1)/2 (v).  4P₁ lists 2P₁ and 4.  If 6P₁ ∉ T, 2P₁ is
private to 4P₁ (iii) and P6 applies.  If 6P₁ ∈ T, re-pay 6P₁ with 3P₁ (private, (iii), (vii)); then pay(4P₁) = 2P₁:
new edges 4P₁ → 6P₁ and (4-payer) → 4P₁; 6P₁ has no out-edge; acyclic.  Sub-case B2: 8P₁ ∉ S.  Then T + 8P₁ is
playable on board n − 1 (8P₁ is a source there, so only layer 4 changes: pay(8P₁) = 8, which T₄'s scheme leaves
unused, and 8P₁ gets no in-edge since nobody pays 4P₁ (ii) or 8), so ΣT ≤ opt(n − 1) − 8P₁ < opt(n − 1) − 4P₁.  ∎

**Coverage (measured, `study/eightp_out.txt` and the count in `study/coverage_out.txt`).**  Of the 114 searched
8P games of 2..5060, 103 meet the hypotheses n ≥ 187 and 9P₁ > 8P (every one from 248 on; 152 meets the second
but not the first, and 24, 40, 56, 88, 104, 136, 184, 232, 296, 424 fail the second), and δ = 4P₁ at every one of
them: the theorem plus the single-loss game settles 103 searched games, 1.95% of the chain's CPU.  Cross-check against the chain (`study/eightp_check_out.txt`): at all 103 games 8P
of 248..5048 with 9P₁ > 8P, the game S\*(n − 1) − 4P₁ + 8P is playable on board n and scores exactly opt(n), as the
theorem demands.  Random promotion sets of 2008, 2056, 2104 and 5048 confirm both cases of the proof in the frame
model (`study/eightp_cases_out.txt`, `study/eightp_caseb_out.txt`: 160 sets in case A, 76 in case B, no failure).
Past 5060 all 89 searched 8P games meet the hypotheses, and the coordinator reports that the best-known
scores now meet δ = 4P₁ at all 89 (two of them, 8696 and 9304, after the law flagged their predecessors as short and
the heuristic raised them to the law's value).  So each of those 89 games is proven optimal on the whole board as
soon as its predecessor is, with no search and no statement U.  The law's three misses in 2..5060 (24, 40, 184) and
the games 56..424 all fail the hypothesis 9P₁ > 8P, so the hypothesis is not an artifact: at 184 = 8·23 the number
9P₁ = 171 is on the board and the theorem's re-payment of 6P₁ with 3P₁ is not available.

**Independent check.**  The coordinator's referee (a reader who had not seen this reasoning;
`check-8p/referee.md`) finds the proof correct, every step within the hypotheses of P2, P6, F3, F10, N3, N4, and the
case split exhaustive.  It closed one implicit point in the re-payment fact (vii): no new out-edge a → b with f | b
appears, since within one layer instance f | b means b lists f, and f is listed by no one else.  It notes that all 103
proven games are in sub-case B1 with 6P₁ ∈ T, so cases A, B2 and B1 without 6P₁ rest on the proof alone; that the bare
inequality is false at 184 (its optimal set plays 114 = 6P₁ and 171 = 9P₁, both listing 57); that n ≥ 187 enters only
through F10; and that 9P₁ > 8P is sufficient, not necessary (232, 296, 424 have δ = 4P₁).

**The mechanism in one sentence.**  The hub 8 can pay one 8t; in game n − 1 it pays 8P₁ and frees 4P₁ to be a move;
in game n it must pay 8P (to keep the move 4P = n/2, which is worth more), so 4P₁ reverts to a factor; and nothing
else can take 4P₁'s place, because the only numbers that share its factors (6P₁ through 2P₁, and 8P₁ through 4P₁)
have private alternatives (3P₁ and 8).

## 3. The exchange law in layer 3: what is proved, what is not, and why

**3.1 What the data rule out.**  Section 1 showed that the families of promotion sets of n and n − 1 differ (14% of
random maximal promotion sets of one board are unplayable with the other board's U\* on average, up to 53% and 68%;
`study/promsets_out.txt`, `study/promsets_full_out.txt`),
although their heaviest members coincide at all 73 searched exchanges.  So the exchange law is a statement about the
optimum alone.  J3's method (a weight-preserving bijection of playable sets) cannot prove it, and neither can the
brief's corner sketch (Section 4.6): on board n every payer of x (2q′, 2r′, q′r′) has a box multiple in the set
(2q′r, 2qr′, 3q′r′), so no payer is ever free at the end of a game; the obligation it was meant to cut is everything.

**3.2 Why the 8P technique does not transfer.**  Theorem 8P works because when n is removed from an optimal set of n,
a *single* number worth at least the law's value (4P₁, or 8P₁) can be put back, paid through factors whose only
other users have private alternatives.  Across an exchange, the number to put back is x = 2q′r′ > n/2, a source;
every number not in the set that could compensate is a promotion (< n/2 < x), so no single addition is worth x, and
the only route is x itself.  x needs q′r′ (held by 3q′r′, whose alternatives 3q′ and 3r′ are hubs with many users) or
2q′ or 2r′ (hubs).  In the random sets that fail, the core on board n − 1 is large (20 to 40 members: the box's six
middle members, a dozen promotions, a dozen other sources, `study/improve_out.txt`), and the cheapest repair removes
a small promotion (12, 20, 44, 76 at 741).  At the optimum the repair costs 0 at all 73 games, and nothing local
explains why.

**3.3 A cleaner sufficient condition: the hole law (proved reduction, given U at n).**  Let Y be board n − 1 with the
hole x (Y = {1, …, n − 1} ∖ {x}).  *Proposition.*  Given U at n, opt(n) ≤ n + opt(Y).  *Proof.*  An optimal set S of n
has exactly U\*(n) as its sources (U for layers ≥ 3, F4 for layers 1 and 2, and U\* is a maximal playable set of
sources), so x ∉ S; S − n is playable on board n − 1 (N4), and the same game is legal on Y, since the hole x is a
source and so no move's maximal factor.  ∎  Also opt(Y) ≥ opt(n − 1) − x (drop x).  Hence

> **the hole law** opt(Y) = opt(n − 1) − x ("excluding the shadow from game n − 1 costs exactly the shadow")
> implies the exchange law's upper bound at n, given U at n.

The hole law is a statement about one board and one number, with no n in it; the solver's model is already proved
for boards with holes (the holes theorem X9), so it is testable game by game.  Whether it holds is open: at 741,
excluding 374 frees the edge 22, and the one promotion that could use it, 44, must be blocked in layer 4 for the law
to hold; the committed opt(741) says it is (otherwise S\*(740) − 374 + 741 + 44 would beat opt(741), since 741 can
pay with 247, which 494 does not use).  This is experiment E1 below.

**E1's answer (coordinator, `e1-holes/README.md`): the hole law is false at all eleven games.**  opt(Y) exceeds
opt(n − 1) − x by 242 to 951 (741: 242, 1083: 338, 1209: 457, 1599: 682, 1677: 814, 1729: 605, 1767: 782, 1833: 902,
2067: 931, 2139: 951, 2301: 901), each excess a legal game on Y checked by two referees, no U involved.  So the
exchange law needs n itself, and these games are the sets the box forbids.  Their shape (`study/e1_cores.py` →
`study/e1_cores_out.txt`): at six of the eleven, the best set of Y is S\*(n − 1) with x exchanged for *the shadow of
x*, y = x with its largest prime replaced by the prime below (1083: 578 = 2·17² for 338 = 2·13²; 1599: 814 = 2·11·37
for 682 = 2·11·31; 1677: 902 for 814; 1729: 935 = 5·11·17 for 605 = 5·11²; 1767: 986 = 2·17·29 for 782 = 2·17·23;
1833: 946 = 2·11·43 for 902 = 2·11·41), and the excess is y; at 741 it is 286 = 2·11·13 for x and 44; at the other
four, 3 to 13 numbers change.  In every case the set plus n is unplayable on board n, with a core of 13 to 78 members
that holds n and three or five other box members (the r-side 2q′r, 2qr, 3q′r at the six single swaps), the added
promotion y, and a dozen to sixty sources, and the set less its additions plus n is playable.  So what n forbids is
not a local pattern: the shadow y of x fits on Y through the hub edges x released, and n's arrival, through the box's
r-side, takes those edges back along a long chain.  The exchange law remains open; its proof must be global.

**3.4 The box as a theorem target.**  Section 1's pair lemma reduces every layer-3 exchange with smallest prime 3
to the 4-cycle N–V₂–X–V₁ of virtual members over the super-edges Q = {2q, 3q}, Q′ = {2q′, 3q′}, R = {2r, 3r},
R′ = {2r′, 3r′}, with board n holding N (= Q ∪ R) and board n − 1 holding X (= Q′ ∪ R′), both holding V₁ = Q′ ∪ R and
V₂ = Q ∪ R′.  The law says: the heaviest set of other members R₀ with R₀ + V₁ + V₂ + N playable weighs the same as
with X in place of N.  Over GF(2) the two are the same problem (N + V₁ + V₂ = X); the game differs only through odd
cores, and the measured law says the heaviest set never meets one.  For the smallest prime p ≥ 5 (12 of the 73
searched exchanges, 46 of the 185 past 5060: 1183 = 7·13², 2945 = 5·19·31, …) the private pairs do not exist (qr is
listed by 2qr, 3qr, 5qr, …), and the structure is the same box without the contraction.

**3.6 The local form of the obstruction: an augmenting path inside the box (proved as stated).**  Take the scheme
of an optimal set S of n that a run of peel produces (P4).  In it 3q′r′ pays q′r′, and in each of the pairs
{n, 2qr}, {2q′r, 3q′r}, {2qr′, 3qr′} one member pays the pair's private edge and the other a hub edge: e₁ ∈ N,
e₂ ∈ V₁, e₃ ∈ V₂ (a pair leaves the peel when one of its hub edges turns private, and its partner then takes the
private edge).  On board n − 1 the box needs, with 2qr paying qr, one hub edge each for the pairs V₁, V₂ and
{x, 3q′r′} (an edge of X = Q′ ∪ R′).  If the members outside the box keep their payments, the box can be re-matched
from e₁, e₂, e₃ alone exactly when (e₁ ∈ R and e₂ ∈ Q′) or (e₁ ∈ Q and e₃ ∈ R′): the chain 2qr → qr, 2q′r → e₁,
x → e₂ (or 2qr → qr, 2qr′ → e₁, 3q′r′ → e₃, x → q′r′), which is what the optimal sets do at 741 and 2301 (1534 takes
767, 1298 takes 118, x takes 22).  Otherwise the box needs a fourth hub edge of Q′ ∪ R′ that no member outside the
box pays with, or those members must be re-routed.  So T + x fails on board n − 1 only when the members outside the
box, in every scheme of S, hold every edge of Q′ ∪ R′ that the chains would need: a Hall condition on four hub edges,
each with many listers (2q′·t, 3q′·t, 2r′·t, 3r′·t).  Acyclicity after the re-matching is a second condition; the
sink arguments of Theorems 8P and 12P do not apply, since none of the hub edges is private.  A proof of the exchange
law has to show that a heaviest set never spends all four edges of Q′ ∪ R′ outside the box in that way; nothing in
the weights makes that obvious, since the members that use them (2q′t, …) are not comparable to those that use
Q ∪ R (2qt, …).

**3.7 The box law, tested beyond exchanges (`study/boxlaw.py` → `study/boxlaw_out.txt`).**  The box is not special
to exchanges: for every odd n of layer 3 in 189..5060 whose box less n lies in the optimal set of n − 1 (303 games),
the box is an even core at n, so some member must go, and the game S\*(n − 1) − min(B) + n gives δ(n) ≤ min(B); that
bound holds at all 303.  Equality: at all 78 where min(B) is a source (73 searched exchanges, 5 repeats), and at 92 of
the 225 where min(B) is a promotion (restrictions of layer 3 such as 455 = 5·7·13, where the box {3,5}×{5,7}×{11,13}
has two promotions, 165 and 195, and δ = 165); at the other 133 restrictions δ is smaller, by 1 to 240 points (273:
min(B) = 110, δ = 11).  The difference has a reason: a dropped promotion y ≤ n/2 returns to the pool of the layer
above, where it can pay for a number that was blocked (P8's remark), so the game recovers part of y; a dropped source
returns nothing.  So the exchange law is the statement that the hub edges of a dropped source never buy anything
back, and the 92 exact restrictions are the games where the returned promotion buys nothing either.  Neither is
proved; the sharp form of the conjecture is: *for odd n of layer 3 whose box less n lies in an optimal set of n − 1
and whose lightest box member x is a source, opt(n) = opt(n − 1) + n − x.*

**3.5 Coverage if proved.**  79 searched exchanges of 2..5060 (10.0% of the chain's CPU: 73 in layer 3, 6 in layer 2
already covered by J3) and 185 of the 1,710 searched games past 5060, plus the 973 repeats, which would then rest on
the law instead of on U.

## 4. The 12P law: the mechanism, the proved part, and the gap

Let n = 12P, P prime, n ≥ 187, P₁ the prime before P, with 15P₁ > 12P (so 4P₁ is listed by 8P₁ and 12P₁ only,
6P₁ by 12P₁ only, 5P₁ by 10P₁ only; true from 228 on).  s = 6P = n/2.  mf(12P) = {6P, 4P, 12}, mf(12P₁) = {6P₁, 4P₁, 12},
mf(8P) = {4P, 8}, mf(8P₁) = {4P₁, 8}; 4P is listed by 8P and 12P only.

**The measured mechanism (`study/twelvep_all_out.txt`, all 76 searched 12P games of 204..5052: 75 alike and at the law, and 204, alike but 3 short
of it, where 15P₁ ≤ n).**  In the optimal set of n − 1: 12P₁ pays 12, 6P₁ is a move (paid by 2P₁), 8P₁ pays 4P₁, the hub 8 pays
8t′ with t′ the largest prime at most 1.5P, and 4t′ is a move.  In the optimal set of n: 12P pays 12, 12P₁ pays 6P₁,
and 6P₁ is the one move lost; 6P stays a move, paid as before.  So L(n) = L(n − 1) − 6P₁ + 6P.

**Why not a cheaper loss?  The cycle lemma (proved).**  *In any playable set that holds 8P₁, 8P, 12P₁ and 12P, at
most one of 6P and 6P₁ is a move.*  Proof: if both are moves, the four members list exactly {4P₁, 8}, {4P, 8},
{4P₁, 12}, {4P, 12} less whatever of 4P₁, 4P, 8, 12 is itself a move; with none a move this is a 4-cycle, every factor
listed twice, a core (P7); with one of them a move it is four members over three factors, with no injective payment.
∎  So the alternative "12P pays 4P, 8P takes 8, 8t′ falls back on 4t′" (loss 4t′, which is *smaller* than 6P₁ at 20 of
the 71 games 228..5052, by 2 to 26 points, `study/twelvep_min_out.txt`) is never available: S\*(n − 1) − 4t′ + 12P is
unplayable at 1668, 2004, 4308, with residual exactly {8P₁, 8P, 12P₁, 12P}.  The law δ(12P) = 6P₁ is the cycle
lemma plus the choice of the cheaper of 6P and 6P₁.

**Theorem 12P (proved; given U at n, which supplies its one hypothesis about an optimal set).**  Let n = 12P with
P prime, n ≥ 187 and 15P₁ > 12P, and let t′ be a prime in (4P/3, 3P/2].  Suppose some optimal set S of n holds 8P,
8P₁, 12P₁ and 8t′ (U at n gives one whenever these four lie in U\*(n), which setup checks).  Then
opt(n) ≤ opt(n − 1) + n − 6P₁, and the law's game settles n.  (One optimal set suffices, since every optimal set
weighs opt(n).  An earlier version of this theorem proved only δ ≥ min(6P₁, 4t′), with case G2-ii open; the referee's
closed-walk argument for B1 closes G2-ii too, below.)

*Facts.*  From t′ > 4P/3: 9t′, 10t′, 12t′ > n, so 4t′ is listed by 8t′ alone, 2t′ by 4t′ and 6t′ alone, 3t′ by 6t′
alone.  From 15P₁ > 12P: 4P₁ is listed by 8P₁ and 12P₁ alone, 6P₁ by 12P₁ alone, 5P₁ by 10P₁ alone, 7P₁ by 14P₁
alone (21P₁ > n); 2P₁ is listed by 4P₁, 6P₁, 10P₁ and, when 14P₁ ≤ n (only at 276 and 444), by 14P₁.  4P is listed
by 8P and 12P, 6P by 12P alone, 5P by 10P alone, 2P by 4P, 6P, 10P (14P > n), 3P by 6P and 9P.  *The layer-3 step
for 6P₁* (used below whenever 4P₁ ∉ S): re-pay 10P₁ with 5P₁ and 14P₁ with 7P₁ if they are members; then 2P₁ is
paid by nobody, and pay(6P₁) = 2P₁ adds only the edges 6P₁ → 10P₁ and 6P₁ → 14P₁, into sinks.  *The hub-8 fact:* in a scheme of S, whichever member pays 8, every other 8t ∈ S pays 4t, so that 4t ∉ S.  The
re-payment step (vii) and the sink argument are those of Theorem 8P; T = S − 12P is playable on board n − 1.

*Proof, by cases on S.*  Write t′ as above; in every case 4t′ ∉ S whenever 8 is paid to 8P or 8P₁.

* *A (6P ∉ S), A1: 9P ∉ S.*  T + 6P is playable (3P private, P6): ΣT ≤ opt(n − 1) − 6P.
* *A2: 6P ∉ S, 4P ∉ S.*  Re-pay 10P with 5P; then pay(6P) = 2P adds the one edge 6P → 10P, a sink: same bound.
* *A3: 6P ∉ S, 4P ∈ S.*  Then 8P lists {8} and pays 8, so 8t′ pays 4t′.  T′ = T − 4P + 6P + 4t′ is playable on
  n − 1.  Layer 4: 4P is a factor again, listed by 8P alone (12P is gone): pay(8P) = 4P, pay(8t′) = 8; 8t′ has no
  in-edge, 8P's only in-edge is from 8t′, and 8P has no out-edge.  Layer 3: pay(6P) = 2P after 10P takes 5P, and
  pay(4t′) = 2t′ after 6t′ takes 3t′; the new edges 6P → 10P and 4t′ → 6t′ end in sinks.  Gain 2P + 4t′ > 6P.
* *B (6P ∈ S).*  By the cycle lemma 6P₁ ∉ S.
* *B-G4: 4P₁ ∈ S.*  Then 8P₁ lists {8} and pays 8, 8P pays 4P (so 4P ∉ S), 12P pays 12, 12P₁ pays 6P₁, 8t′ pays 4t′.
  T″ = T − 4P₁ + 6P₁ + 4t′ is playable on n − 1.  Layer 4: pay(12P₁) = 12 (free), pay(8P₁) = 4P₁, pay(8t′) = 8; 8t′ has
  no in-edge, 8P₁'s only in-edge is from 8t′, 12P₁'s only in-edge is from 8P₁: no cycle.  Layer 3: the step for 6P₁ (4P₁ is gone, so 2P₁ is free once 10P₁ and 14P₁ are re-paid), and pay(4t′) = 2t′
  after 6t′ takes 3t′; all new edges end in sinks.  Gain 6P₁ + 4t′ − 4P₁ > 6P₁.
* *B1: 4P₁ ∉ S and some scheme σ of S pays 12P with 12.*  Then 6P₁ ∉ S (cycle lemma).  T + 6P₁ is playable on
  n − 1.  Layer 3: the step for 6P₁.  Layer 4: 12P is gone and 6P₁ leaves the pool; 12P₁ lists {4P₁, 12}.  If
  σ pays 12P₁ with 4P₁, σ restricted to T₄ is a scheme of the new instance (nobody paid 6P₁).  If σ pays 12P₁ with
  6P₁, re-pay it with 12, which 12P has released.  A cycle through 12P₁ in the new precedence would be
  12P₁ → b → ⋯ → a → 12P₁ with 12 | b and pay(a) | 12P₁, so pay(a) = 4P₁ and a = 8P₁, and the member before 8P₁ pays
  8, say 8u; the walk from b to 8u uses σ's edges among unchanged members.  If 8P pays 8 in σ (8u = 8P), 8P has no
  in-edge in the new precedence (nobody pays 4P, since 12P is gone, and 8 is its own), so no walk reaches it: no
  cycle.  If 8P pays 4P in σ, then σ has the edges 12P → b (12 | b), 8u → 8P (8 | 8P) and 8P → 12P (4P | 12P), so
  12P → b → ⋯ → 8u → 8P → 12P is a cycle of σ, against P2.  So the new precedence is acyclic.  Bound 6P₁.  (This
  proof is the referee's; the first draft asserted the case.)
* *G2: 4P₁ ∉ S and every scheme pays 12P with 4P* (so 4P ∉ S, 8P pays 8, 8P₁ pays 4P₁, 8t′ pays 4t′).  *G2-i:* some
  such scheme pays 12P₁ with 12.  Then in T + 6P₁ the layer-4 scheme is unchanged (nobody paid 6P₁) and layer 3
  takes the step for 6P₁: bound 6P₁.  *G2-ii:* in σ, 12P₁ pays 6P₁ and 12 goes to some other 12t₀.
  Then T + 6P₁ is playable on n − 1, with the scheme pay(8P) = 4P (free, since 12P is gone and 4P ∉ S), pay(8P₁) = 8
  (released by 8P), pay(12P₁) = 4P₁ (released by 8P₁), all else as in σ; layer 3 takes the step for 6P₁.  Acyclic:
  8P is a sink (4P divides no member); 8P₁'s only in-edge is from 12P₁ (nobody else pays 4P₁ or 8); so a cycle would
  be 12P₁ → 8P₁ → 8u → ⋯ → 12t₀ → 12P₁ with 8u ≠ 8P and the walk from 8u to 12t₀ made of σ's edges among unchanged
  members; but σ has 8P → 8u (8 | 8u), 12t₀ → 12P (12 | 12P) and 12P → 8P (4P | 8P), so σ would hold the cycle
  8P → 8u → ⋯ → 12t₀ → 12P → 8P, against P2.  Bound 6P₁.  (The weaker set T + 4t′, with pay(8P) = 4P and
  pay(8t′) = 8, is playable too and gave the earlier bound 4t′.)

In every case ΣT ≤ opt(n − 1) − 6P₁.  ∎

**Independent check** (`check-12p/referee.md`): correct for the proved cases, including the bound in G2-ii.  The
referee found and closed two gaps, now repaired above: case B1 had been asserted without proof (and all 73 proven
12P games are in B1), and the listers of 2P₁ had omitted 14P₁, which is on the board at 276 and 444.  It also noted
that the theorem needs only one optimal set holding the four sources, which is how it is now stated.

*What is left open.*  Nothing in the theorem's cases.  Without an optimal set holding 8P, 8P₁, 12P₁ and 8t′ (that
is, without U at n) the argument would need the single-addition steps of Theorem 8P's sub-case B2 for each missing
source; not done.  The closure of G2-ii is new and has not been refereed.

**Counts (`study/twelvep_hyp_out.txt`, `study/twelvep_hyp_tail_out.txt`).**  Of the 75 games 12P (P prime) of
228..5052, 73 meet the hypotheses (228 has no 8t′ in U\*, 348 has 15P₁ ≤ 12P); at all 73 the law
δ(12P) = 6P₁ is proved given U at n, and the chain's game settles the game.  (Before G2-ii was closed, the 15 games
372, 516, 996, 1236, 1668, 1812, 2004, 2316, 2388, 2748, 3252, 3396, 3804, 4236, 4308, where 4t′ < 6P₁, had only the
bound δ ≥ 4t′.)  Past 5060 all 63 searched 12P games meet the hypotheses (5061..8191 from the arrival file,
8192..10000 by descending greedy), so each is optimal whenever its predecessor is, given U at n; their best-known
scores meet the law (coordinator).
Every one of the 76 surveyed optimal sets of n is in case B1 with 4P₁ ∉ S; the open case G2-ii has never been seen.
Experiment E2 (b) at 1668, 2004, 2316, 2748, all in the short list, is exactly a test of G2-ii.

## 5. What the technique reaches, and what it does not

The two proofs above share one pattern, worth naming because it is what a settling rule looks like in this game.
A number n arrives; it takes a *hub* factor h (8 for 8P, 12 for 12P) that some member m₁ of game n − 1 was using;
m₁ falls back on a factor f₁ that was a move (4P₁, 6P₁), and the move f₁ is lost.  The loss is exact when (a) every
other member that could take f₁'s place has a private alternative, so nothing is gained elsewhere (Theorem 8P's
re-payment steps), and (b) no other way of fitting n is cheaper (the cycle lemma for 12P; for 8P, n's other factor 4P
is worth more than f₁).  The proof is then two or three re-payments and an application of P6, on the whole board, with
no statement U.  The chain's data says where else the same pattern holds exactly: the brief's Table 4 lists 215
relaxations with δ = n/2 with P replaced by P₁, of which 8P and 12P are 189; the other 26 (cofactors 20, 24, 36, ...)
are too few to earn a theorem each.  Where the data shows no formula (the other 914 searched relaxations and 393
restrictions, 82% of the chain's CPU), the hub is contested by several members with no private alternatives, and the
price of room for n is a global quantity, as the exchange law's failure at the level of sets shows.

For the exchanges (10% of the CPU), the box structure and the pair lemma are the right language, the set-level law is
dead, and the hole law (3.3) is the sharpest conjecture this study can offer: one board, one number, testable with the
solver's holes.

## 6. Experiments requested, in order of value

* **E1 (the hole law; decides whether the exchange law can be split from n).**  For the cheap searched exchanges
  741, 1083, 1209, 1599, 1677, 1729, 1767, 1833, 2067, 2139, 2301 (seconds each in the frame solver), solve board n − 1
  with the hole x (the shadow) and compare with opt(n − 1) − x.  Equality at all of them makes the hole law the target
  (and, with U at n, proves the exchange law at those games); a strict excess at any one says the law needs n itself,
  and names the set that beats opt(n − 1) − x, which shows what the box forbids.  Needs the solver to take a hole;
  the holes theorem X9 says the model is sound for it.
* **E2 (run; moot).**  Run (b) at 1668, 2004, 2316, 2748 returned the law's score, but as the builder notes a
  restricted problem of a proven game never exceeds opt(n), which is the law's score there, so the run could not
  have failed; and the case it was to test, G2-ii, is now closed by proof (Section 4).  No further E2 run is wanted.
* **E3 (settle the 89 games 8P past 5060 now).**  No experiment: for each, check by peel that the best-known game of
  n − 1 less 4P₁ plus 8P is playable (it is the single-loss game) and that best-known(n) = best-known(n − 1) + n − 4P₁;
  Theorem 8P then proves n optimal on the whole board whenever n − 1 is.  The same check on the 103 proven 8P games
  of 248..5048 is a cross-check of the theorem against the chain (every one must pass).

## 7. Summary

| result | status | games 2..5060 settled (CPU share) | games past 5060 |
|---|---|---|---|
| Theorem 8P: δ(8P) ≥ 4P₁ when 9P₁ > 8P | proved, whole board, no U | 103 searched (1.95%) | 89 of 1,710, all meeting the law |
| Theorem 12P: δ(12P) ≥ 6P₁ | proved given U at n (last case closed today, unrefereed) | 73 searched (2.94%) | 63 of 1,710, all meeting the law |
| Exchange law: box, pair lemma, set-level law false, corner sketch vacuous, hole-law reduction | structure proved; law open | 79 searched (10.0%) if proved | 185 (+973 repeats off U) |

## 8. Addendum (coordinator's requests)

**E3, run (`study/e3_best_known.py` → `study/e3_best_known_out.txt`).**  On the best-known file
(/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl, highest score per n, the last if tied; games
5061..10000): every one of the 89 games n = 8P (P prime) of 5061..10000 meets 9P₁ > 8P; at every one, 4P₁ is a move of
the best-known game of n − 1, that game less 4P₁ plus 8P is playable on board n (peel), and
best-known(n) = best-known(n − 1) + n − 4P₁.  So by Theorem 8P each of the 89 is optimal on the whole board whenever
its predecessor is: 89 of the 1,710 searched games past 5060 now carry no uncertainty of their own.  The list is in
the output file (5128, 5144, 5176, …, 9992).

**E2, specified in the frame solver's terms (superseded: run, moot, and the case is now proved; kept for the record).**  Everything here is given U at n (the frame model's own assumption),
with 8P, 8P₁ and 12P₁ in U\*(n), which the setup can check.  Then every promotion set L of n = 12P falls into a case
of Theorem 12P that is proved, or into one of three restricted problems:

* (a) *6P barred*: 6P is a candidate of n (it is n/2, listed by 12P alone); fix it out, so no promotion set holds it.
  Not a hole: 6P stays a factor that 12P can pay with.  This is case A (G1 inside it).
* (b) *6P fixed in, 4P barred*: 6P fixed as a promotion, 4P (a candidate of layer 3) fixed out.  Then 12P pays 4P or
  12; the sets in which it can pay 12 are case B1 (proved); the rest is G2.
* (c) *6P fixed in, 4P₁ fixed in*: 4P₁ a promotion (it is a candidate when 8P₁ can pay 8).  This is G4.

For each run, report ΣU\*(n) + P\* of the restricted problem and compare with opt(n − 1) + n − 6P₁ (= the law's
score).  If all three are at or below it at a game, then, given U at n, the law's upper bound holds at that game by
Theorem 12P's cases plus the three searches (no promotion set is left out: 6P out is (a); 6P in forces 6P₁ out by
the cycle lemma; then 4P₁ in is (c), else 12P pays 12 in some scheme (B1) or 4P is not a move and every scheme pays
12P with 4P, which is (b)).  Values below the law at every game also say the gap configurations are worse in
practice.  The four games: 1668, 2004, 2316, 2748 (each took under 0.01 CPU-hours in the chain, and at each the
competing loss 4t′ is smaller than 6P₁, so they are the games where a cheaper configuration would show if it
existed).  The constraint "12P pays 4P" itself is not a candidate constraint; (b) is its promotion-set form, since
12P pays 4P only when 4P is a factor, and the alternative in (b), 12P paying 12, is proved harmless.
