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

**The mechanism in one sentence.**  The hub 8 can pay one 8t; in game n − 1 it pays 8P₁ and frees 4P₁ to be a move;
in game n it must pay 8P (to keep the move 4P = n/2, which is worth more), so 4P₁ reverts to a factor; and nothing
else can take 4P₁'s place, because the only numbers that share its factors (6P₁ through 2P₁, and 8P₁ through 4P₁)
have private alternatives (3P₁ and 8).

