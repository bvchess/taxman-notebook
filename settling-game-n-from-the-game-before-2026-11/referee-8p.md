# Referee notes on Theorem 8P

Written 2026-11-10 while checking `theorem-8p.md`.  Part 1: the lemmas and the step-by-step audit.  Part 2 (below):
the checks run and the verdict.

## 1. The cited results, as stated in the theory

* **P2** (playability.md): S ⊆ {2..n} is playable iff some injective pay gives each x ∈ S a maximal factor of x outside
  S with acyclic precedence; precedence has a → b when pay(a) | b or a | b.
* **P6** (extension): T playable *in an instance* (same pool), x a member outside T listing a factor f that no member of
  T lists ⇒ T ∪ {x} playable in the instance.  Hypotheses: T playable in the instance; f listed by x; f listed by no
  member of T.
* **P7** (core theorem): an instance is playable iff its residual (dismantling by back moves) is empty.  Used only by
  my own check.
* **F3** (layer theorem, frame-model.md): S playable iff every layer instance is; layer instance at k = members S_k,
  pool = numbers of layer k − 1 up to n/2 not in S.  Within one layer instance the precedence has only edges
  a → b with pay(a) | b, and since pay(a) is one layer below b, pay(a) | b iff b lists pay(a) (pay(a) ∈ mf(b) and in
  the pool).  No a | b edge between distinct members of one layer.
* **F10** part 2 (square theorem): n ≥ 187 ⇒ every optimal set plays exactly U*_2 in layer 2 and no number of layer 2
  up to n/2.  Standing: proved (boards 187..2499 and primes in short intervals below 396,738 by computation, Dusart
  above).  This is a whole-board statement about *every* optimal set, which is what fact (v) needs.
* **N3**: every optimal game of n plays n.  **N4**: S playable in game n ⇒ S ∖ {n} playable in game n − 1.
  Also N3: a set without n is playable in game n iff in game n − 1, so "playable on board n − 1" for a set ⊆
  {2..n − 1} is just "playable"; the own instance does not mention the board.

## 2. The facts (i)–(viii)

Let n = 8P, P ≥ 29 (n ≥ 187 and 8·23 = 184 < 187), P₁ the prime before P, 9P₁ > 8P.

* (i) mf(8P) = {4P, 8}.  Numbers with 4P as a maximal factor: 4P·r, r prime: 8P, 12P, 4P².  12P > n, 4P² > n.  OK.
* (ii) mf(8P₁) = {4P₁, 8}.  4P₁·r: 8P₁, 12P₁ (> 8P since 12P₁ > 9P₁ > 8P), 4P₁² (> 8P as P₁ ≥ 23).  OK.
* (iii) mf(4P₁) = {2P₁, 4}.  2P₁·r: 4P₁, 6P₁, 10P₁ (> 8P), 2P₁² (> 8P).  3P₁·r: 6P₁, 9P₁ (> 8P by hypothesis),
  3P₁², 15P₁.  mf(6P₁) = {6, 2P₁, 3P₁}.  OK.  Note 9P₁ ≠ 8P for a prime P₁ ≥ 3, so 9P₁ > 8P ⇔ 9P₁ > 8P − 1: the
  hypothesis reads the same on both boards.
* (iv) mf(4P) = {2P, 4}; 2P·r: 4P, 6P (10P > n); 3P·r: 6P (9P > n).  OK.
* (v) By F10 (n ≥ 187) S holds no layer-2 number ≤ n/2 = 4P.  Layer-3 pool of S on board n = all layer-2 numbers
  ≤ 4P.  4, 2P, 3P, 2P₁, 3P₁ are layer 2 and ≤ 4P (3P₁ < 3P < 4P; 2P₁ < 2P).  OK.  For T = S − 8P on board n − 1 the
  layer-3 pool is layer-2 numbers ≤ 4P − 1 not in T: the same set, since 4P is layer 3.  Likewise the layer-2 pool
  (primes ≤ 4P − 1 vs ≤ 4P: same, 4P not prime) and the pools of layers ≥ 5 (layer ≥ 4 numbers ≤ 4P, and 8P > n/2 is
  in no pool).  Only the layer-4 pool can differ, through 4P and 4P₁, which the proof tracks.
* (vi) P2's precedence within a layer: as above.  P6: hypotheses noted.
* (vii) Re-payment.  Within one layer instance: a lists f, no other member lists f.  New pay(a) = f is a scheme
  (nobody else pays f since nobody else lists it).  Edges out of a: old ones (old pay(a) | b) vanish; *new* ones
  a → b with f | b would need b to list f (same-layer argument), and none does.  Edges into a unchanged.  Removing
  out-edges creates no cycle.  The note "nothing else changes" silently covers the new-edge question; it holds for
  the reason just given, and the proof's text ("3P divides no member") shows the author saw it.  OK.
* (viii) T = S − 8P playable on board n − 1: N4 directly.  OK.

## 3. The proof

* S optimal set of n, 8P ∈ S (N3), T = S − 8P playable on n − 1 (N4).  Goal ΣT ≤ opt(n − 1) − 4P₁ gives
  opt(n) = ΣT + 8P ≤ opt(n − 1) + n − 4P₁.  Correct.
* **Case A, 4P ∉ S.**  4P > (n − 1)/2: a source on board n − 1, so in no pool there; 4P ∉ T.  Claim T ∪ {4P}
  playable.  Layer 4 of T ∪ {4P} on n − 1: members S₄ − 8P; pool = S's layer-4 pool minus 4P (4P was in it on board
  n, as 4P ∉ S and 4P ≤ n/2); only 8P listed 4P (i), and 8P is gone, so the restricted scheme stands.  Layer 3:
  members S₃ ∪ {4P}, pool unchanged; 4P lists {2P, 4}.  6P ∉ T: no member of S₃ lists 2P (iv) ⇒ P6.  6P ∈ T: re-pay
  6P with 3P (3P in pool, listed by 6P alone (iv)); 2P now paid by nobody (only 4P, 6P list it); pay(4P) = 2P;
  out-edges of 4P: to b with 2P ∈ mf(b), b ∈ members: 6P only; 6P has no out-edge (3P ∈ mf(b) ⇒ b = 6P or 9P > n);
  in-edges of 4P from the 4-payer.  No cycle through 4P, none elsewhere.  Correct.  Then ΣT + 4P ≤ opt(n − 1) and
  4P > 4P₁.  Correct.
* **Case B, 4P ∈ S.**  8P lists {4P, 8} ∖ S = {8} ∖ S; S playable ⇒ 8 ∉ S, pay(8P) = 8.  Correct.
  * **B1, 8P₁ ∈ S.**  If 4P₁ ∈ S, {8P, 8P₁} both list {8}: a core.  So 4P₁ ∉ S, pay(8P₁) = 4P₁ (8 is 8P's).
    T ∪ {4P₁}: 4P₁ < 4P so ≤ (n − 1)/2: a layer-3 number that leaves the layer-4 pool and joins layer 3's members.
    Layer 4: only 8P₁ listed 4P₁ (ii); 8 ∈ pool (8 ∉ S, layer 3, ≤ n/2) and unused once 8P is gone; pay(8P₁) = 8;
    in-edges to 8P₁ need pay(a) ∈ {4P₁, 8}: none.  Acyclic.  Layer 3: 4P₁ lists {2P₁, 4}.  6P₁ ∉ T ⇒ 2P₁ listed by no
    member (iii) ⇒ P6.  6P₁ ∈ T ⇒ re-pay 6P₁ with 3P₁ (private, (iii)), pay(4P₁) = 2P₁, out-edge only to 6P₁, which
    has none; in-edges from the 4-payer.  Acyclic.  Correct.  ΣT + 4P₁ ≤ opt(n − 1).
  * **B2, 8P₁ ∉ S.**  8P₁ > 4P (P₁ > P/2), a source on n − 1: only layer 4 changes; 8P₁ lists {4P₁, 8} ∩ pool ∋ 8,
    unused; pay(8P₁) = 8; in-edges need pay(a) ∈ {4P₁, 8}: 4P₁ is either a member of S (then nobody pays it) or in
    the pool listed by 8P₁ alone (ii); 8 is nobody's.  Acyclic.  ΣT + 8P₁ ≤ opt(n − 1), 8P₁ > 4P₁.  Correct.
* Case split complete: {4P ∉ S} ∪ {4P ∈ S, 8P₁ ∈ S} ∪ {4P ∈ S, 8P₁ ∉ S}; sub-splits on 6P, 6P₁ complete.

So far every step follows.  Where the hypotheses enter: n ≥ 187 only through F10 (fact (v)); 9P₁ > 8P through (ii)
12P₁ > n, (iii) 10P₁ > n and 9P₁ > n.  The binding use is 9P₁ > n: that 3P₁ is listed by 6P₁ alone, in sub-case B1 with
6P₁ ∈ T.  The others need only P₁ > 2P/3 and P₁ > 4P/5.

## 4. Checks run (`referee_check.py`, output in `referee_check_out.txt`)

My own code, standard library: playability by the residual of the own instance (dismantling, P5/P7), not the author's
`common.playable` (which is peel, P4).

* **A. Arithmetic facts (i)–(iv)** for every prime P, 29 ≤ P ≤ 50,000, with 9P₁ > 8P (5,121 primes): the numbers
  ≤ 8P having 4P, 4P₁, 2P₁, 3P₁, 2P, 3P as a maximal factor are exactly {8P}, {8P₁}, {4P₁, 6P₁}, {6P₁}, {4P, 6P},
  {6P}; the mf sets; 8P₁ > 4P; 4P₁ < 4P; the layers.  0 failures.  (These are also proved by the one-line arguments
  of section 2; the run guards against a slip.)
* **B. The inequality on every 8P game of 2..5060.**  δ − 4P₁ = 0 at every 8P game from 56 on except 184, where
  δ = 48 < 76 = 4P₁: **the bare inequality is false at 184**, which fails both hypotheses (184 < 187, and
  9·19 = 171 ≤ 184).  At 24 and 40, δ > 4P₁ (the inequality holds, the single-loss game does not reach it).
* **C. The proof walked on the recorded optimal set S of each of the 103 games meeting the hypotheses.**  8P ∈ S; no
  layer-2 number ≤ n/2 in S; S playable by residual; case found; the set the proof constructs (T + 4P, T + 4P₁ or
  T + 8P₁) playable by residual; ΣT + bound ≤ opt(n − 1); ΣT ≤ opt(n − 1) − 4P₁; δ = 4P₁.  0 problems.  Every one of
  the 103 falls in **sub-case B1 with 6P₁ ∈ T** (4P ∈ S, 8P₁ ∈ S, 6P₁ ∈ S).  So the chain never exercises case A,
  case B2 or B1 without 6P₁; those rest on the proof alone (A: P6 or the 6P/3P re-payment; B2: a source added with
  the unpaid factor 8; B1 − 6P₁: P6).  I audited each by hand in section 3 and find them sound; they are the simpler
  branches.  The author's random promotion sets (frame model) do exercise case A (160 sets) and B1 (76 sets).
* The author's `study/eightp_check.py` rerun: 103 pass, 0 fail (the single-loss game S*(n − 1) − 4P₁ + 8P is
  playable and scores opt(n)).

## 5. What breaks at 184, and the strength of the hypotheses

At 184 = 8·23, P₁ = 19: S(184) plays 92 = 4P, 152 = 8P₁, 114 = 6P₁ and 171 = 9P₁, not 76 = 4P₁; 114 and 171 both
list 57 = 3P₁, so 3P₁ is not private to 6P₁ and T + 76 is unplayable (checked).  S(184) also plays 91 = 7·13, a
layer-2 number ≤ 92: F10 fails below 187, as it says it does.  Game 184 drops 76 and gains 28 = 4·7 (δ = 76 − 28),
which is what the proof rules out from 187 on: with 9P₁ > n the move 4P₁ re-enters through 2P₁ (6P₁ moving to 3P₁)
and never needs 4.

* **n ≥ 187** enters only through F10, for fact (v): that 2P, 3P, 2P₁, 3P₁ (and 4) are factors, not moves, in every
  optimal set.  F10 is sharp at 186, and the proof needs F10 for *every* optimal set, so the bound cannot be lowered
  by this proof.  Since 8·23 = 184 < 187 < 232 = 8·29, the hypothesis amounts to P ≥ 29.
* **9P₁ > 8P** is used three times: 12P₁ > n (4P₁ private to 8P₁, cases B1 and B2), 10P₁ > n (2P₁ listed by 4P₁
  and 6P₁ only, B1) and 9P₁ > n itself (3P₁ private to 6P₁, B1 with 6P₁ ∈ T).  The last is the binding one.  It is
  sufficient, not necessary: at 232, 296 and 424 (n ≥ 187, 9P₁ ≤ 8P, and 9P₁ ∈ S at each) δ = 4P₁ still holds and
  T + 4P₁ is still playable.  To drop it one would need 6P₁ or 9P₁ to have another factor of its own (9 for 9P₁, which 18,
  27, 45, 63, … also list; 6 for 6P₁), and no privacy argument gives that.  So the hypothesis is needed by this
  proof, and some hypothesis is needed by the theorem (184), but the exact line 9P₁ > 8P is the proof's, not the
  truth's.
* The theorem inherits F10's standing: proved for every n ≥ 187, with a computation for 187..2499 and for the primes
  in short intervals below 396,738, and Dusart's Proposition 6.8 above.  Nothing else outside the proved theory is
  used: no U, no (♦), no frame-model assumption.

## 6. Verdict

**Correct.**  Every step follows from the cited results within their hypotheses; the case split is complete; the two
re-payments are valid within a layer instance (the one point the text leaves implicit, that a re-paid member gains
no new out-edge, holds because within a layer "f | b" is "b lists f", and f is listed by nobody else).  The proof's
single-loss corollary needs, per game, a game reaching the bound, which the chain supplies at all 103 proven games.
