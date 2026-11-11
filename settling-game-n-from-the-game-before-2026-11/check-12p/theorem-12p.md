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

**Theorem 12P (proved given U at n).**  Hypotheses: n = 12P with P prime, n ≥ 187, 15P₁ > 12P; U at n; 8P, 8P₁
and 12P₁ in U\*(n); and some prime t′ in (4P/3, 3P/2] with 8t′ ∈ U\*(n), t′ the largest such.  Then
δ(n) ≥ min(6P₁, 4t′); in particular, when 4t′ ≥ 6P₁, opt(n) ≤ opt(n − 1) + n − 6P₁, and the law's game settles n.

*Facts.*  Given U, every optimal set S of n holds 8P, 8P₁, 12P₁ and 8t′.  From t′ > 4P/3: 9t′, 10t′, 12t′ > n, so 4t′ is
listed by 8t′ alone, 2t′ by 4t′ and 6t′ alone, 3t′ by 6t′ alone.  From 15P₁ > 12P: 4P₁ is listed by 8P₁ and 12P₁
alone, 6P₁ by 12P₁ alone, 5P₁ by 10P₁ alone.  4P is listed by 8P and 12P, 6P by 12P alone, 5P by 10P alone, 3P by 6P
and 9P.  *The hub-8 fact:* in a scheme of S, whichever member pays 8, every other 8t ∈ S pays 4t, so that 4t ∉ S.  The
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
  no in-edge, 8P₁'s only in-edge is from 8t′, 12P₁'s only in-edge is from 8P₁: no cycle.  Layer 3: pay(6P₁) = 2P₁
  (10P₁ takes 5P₁; 4P₁ is gone), pay(4t′) = 2t′ (6t′ takes 3t′); sinks.  Gain 6P₁ + 4t′ − 4P₁ > 6P₁.
* *B1: 4P₁ ∉ S and some scheme of S pays 12P with 12.*  As proved above: T + 6P₁ is playable.  Bound 6P₁.
* *G2: 4P₁ ∉ S and every scheme pays 12P with 4P* (so 4P ∉ S, 8P pays 8, 8P₁ pays 4P₁, 8t′ pays 4t′).  *G2-i:* some
  such scheme pays 12P₁ with 12.  Then in T + 6P₁ the layer-4 scheme is unchanged (nobody paid 6P₁) and
  pay(6P₁) = 2P₁ in layer 3: bound 6P₁.  *G2-ii:* every scheme pays 12P₁ with 6P₁ and 12 goes to some other 12t₀.
  Then T + 4t′ is playable on n − 1: pay(8P) = 4P (free, listed by 8P alone), pay(8t′) = 8, 8t′ without in-edge, 8P's
  only in-edge from 8t′; layer 3 as before.  Bound 4t′.  (Remark: here t₀ ≤ 3P/4, since for t₀ ∈ (3P/4, P) the
  cycle lemma with t₀ in place of P₁ makes 6t₀ a factor, private to 12t₀, so 12t₀ could take it and free 12 for 12P,
  against the case's assumption.)

In every case ΣT ≤ opt(n − 1) − min(6P₁, 4t′), with 6P₁ itself except possibly in G2-ii.  ∎

*What is left open.*  G2-ii with 4t′ < 6P₁: an optimal set of n in which 12P can only be paid with 4P, 12P₁ only
with 6P₁, and 12 goes to a 12t₀ with t₀ ≤ 3P/4.  The proof gives δ ≥ 4t′ there, 2 to 46 points short of the law.
Without U the sources 8P, 8P₁, 12P₁, 8t′ may be missing from S, and the argument needs the single-addition steps of
Theorem 8P's sub-case B2 for each; not done.

**Counts (`study/twelvep_hyp_out.txt`, `study/twelvep_hyp_tail_out.txt`).**  Of the 75 games 12P (P prime) of
228..5052, 73 meet the hypotheses (228 has no 8t′ in U\*, 348 has 15P₁ ≤ 12P); at 58 of them 4t′ ≥ 6P₁, so the law
δ(12P) = 6P₁ is proved given U at n, and the chain's game settles the game; at the other 15 (372, 516, 996, 1236, 1668,
1812, 2004, 2316, 2388, 2748, 3252, 3396, 3804, 4236, 4308) the proof gives δ ≥ 4t′, 2 to 26 points below the measured
δ = 6P₁.  Past 5060 all 63 searched 12P games meet the hypotheses (5061..8191 from the arrival file, 8192..10000 by
descending greedy): 48 with the law proved given U at n, so each is optimal whenever its predecessor is (their
best-known scores meet the law, per the coordinator), and 15 with the bound δ ≥ 4t′ only (5556, 5604, 6276, 6564,
6852, 7188, 7212, 7404, 7428, 7716, 9132, 9276, 9732, 9876, 9948; 2 to 46 points below the law).
Every one of the 76 surveyed optimal sets of n is in case B1 with 4P₁ ∉ S; the open case G2-ii has never been seen.
Experiment E2 (b) at 1668, 2004, 2316, 2748, all in the short list, is exactly a test of G2-ii.

