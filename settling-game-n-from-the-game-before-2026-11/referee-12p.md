# Referee notes on Theorem 12P

Written 2026-11-10 while checking `theorem-12p.md` (section 4 of `study-report.md`).  Part 1: the setting and the
step-by-step audit.  Part 2 (below): the checks run and the verdict.  The lemmas cited are those the 8P referee
listed (`referee-8p.md`, section 1): P2, P3, P6, P7, F3, F10, N3, N4, and the re-payment step (vii) of
Theorem 8P, which that referee closed (a re-paid member gains no new out-edge, since within a layer "f | b" means
"b lists f" and f is listed by nobody else).

## 1. The setting

n = 12P, P prime, n ≥ 187 (so P ≥ 17), P₁ the prime before P, 15P₁ > 12P (so P₁ > 0.8P; with P ≥ 17 this first holds
at P = 19, n = 228).  n/2 = 6P.  Layers: 12P, 12P₁, 8P, 8P₁, 8t′ are layer 4; 6P, 4P, 12, 8, 6P₁, 4P₁, 4t′, 10P,
10P₁, 14P₁, 9P, 9P₁, 6t′ are layer 3; 2P, 3P, 5P, 2P₁, 3P₁, 5P₁, 7P₁, 2t′, 3t′, 4, 6 are layer 2.

*Who lists what, on board n (x·r ≤ 12P, r prime).*  Verified by hand and by `referee_check.py` part A:

* 4P: 8P, 12P.  6P: 12P.  5P: 10P.  3P: 6P, 9P.  2P: 4P, 6P, 10P (14P > n).
* 4P₁: 8P₁, 12P₁ (20P₁ > 16P).  6P₁: 12P₁ (18P₁ > 14.4P).  5P₁: 10P₁ (15P₁ > 12P: **the binding use of the
  hypothesis**).  3P₁: 6P₁, 9P₁.  7P₁: 14P₁ (21P₁ > n).
* **2P₁: 4P₁, 6P₁, 10P₁, and also 14P₁ when 14P₁ ≤ 12P.**  The hypothesis gives P₁ > 0.8P, and 14P₁ ≤ 12P needs
  only P₁ ≤ 6P/7 ≈ 0.857P.  Among the 12P games with 15P₁ > 12P this happens at n = 276 (P₁ = 19, 14·19 = 266) and
  n = 444 (P₁ = 31, 434).  The proof's layer-3 steps "pay(6P₁) = 2P₁ (10P₁ takes 5P₁)" (B-G4, G2-i, and B1) silently
  assume that 4P₁, 6P₁, 10P₁ are the only listers of 2P₁.  See section 3, "the 14P₁ slip".
* t′ prime in (4P/3, 3P/2]: 8t′ ≤ n and > 6P; 4t′ < 6P (3P/2 is not an integer), 4t′ > 16P/3 > 4P; 4t′ listed by
  8t′ alone (12t′ > n); 2t′ by 4t′, 6t′ (10t′ > n); 3t′ by 6t′ alone (9t′ > n: the binding use of t′ > 4P/3).
* Board n − 1: (n − 1)/2 = 6P − 1.  6P becomes a source; every other number above keeps its side.  The layer-2 pool
  (primes ≤ 6P − 1) and the layer-3 pool (layer-2 numbers ≤ 6P − 1, all of them factors by F10 at n) are those of
  board n.  The layer-4 pool loses 6P (listed by 12P alone, and 12P is gone) and otherwise changes only through the
  numbers the proof moves (6P₁, 4P₁, 4t′, 4P).  Layers ≥ 5: unchanged.

*Where U enters.*  U says some optimal set of n contains all of U\*(n) in layers ≥ 3.  The proof takes S to be that
set; the hypotheses put 8P, 8P₁, 12P₁, 8t′ (all layer 4) in U\*(n), so they are in S, and 12P ∈ S by N3.  The text
says "every optimal set S of n holds ..." which U does not give; but the proof needs only one optimal set S, since the
conclusion is ΣT ≤ opt(n − 1) − bound with ΣT = ΣS − 12P = opt(n) − 12P.  An overstatement, harmless.

*Precedence within a layer instance* (F3 + P3): the only edges are a → b with pay(a) | b, i.e. pay(a) ∈ mf(b).  A set
is playable iff each layer instance has an acyclic scheme.  All the proof's acyclicity arguments are per layer.

## 2. The cycle lemma and the hub-8 fact

* **Cycle lemma.**  S playable, {8P₁, 8P, 12P₁, 12P} ⊆ S, 6P, 6P₁ ∈ S.  Lists: 8P₁: {4P₁, 8} ∖ S; 8P: {4P, 8} ∖ S;
  12P₁: {4P₁, 12} ∖ S; 12P: {4P, 12} ∖ S.  If none of 4P₁, 4P, 8, 12 is in S, each of the four factors is listed by
  exactly two of the four members: a core (P7).  If any is in S, four members list at most three factors: no
  injective scheme.  **Correct**, and it needs no hypothesis beyond the mf sets (true for every prime P ≥ 5).
* **Hub-8 fact.**  mf(8t) = {4t, 8} for a prime t ≥ 3 (and {8} for 16, {12, 8} for 24); if another member pays 8,
  8t ∈ S must pay 4t, so 4t ∉ S.  **Correct.**  8t′ ≠ 8P, 8P₁ since t′ > P.

## 3. The proof, case by case

Throughout, S is the optimal set given by U, π an acyclic scheme of its layer-4 instance, σ of its layer-3 instance,
T = S − 12P (playable on n − 1 by N4).

* **A1 (6P ∉ S, 9P ∉ S).**  T + 6P on board n − 1: 6P is a source there (6P > 6P − 1), so only the layer-3 instance
  changes: members S₃ + 6P, pool unchanged.  6P lists 3P, listed by no member (6P ∉ S, 9P ∉ S); P6.  ΣT ≤ opt(n − 1)
  − 6P < opt(n − 1) − 6P₁.  **Correct.**
* **A2 (6P ∉ S, 4P ∉ S).**  Layer 3 of T + 6P: if 10P ∈ S re-pay it with 5P (in the pool by F10, listed by 10P alone),
  then 2P is paid by nobody (its listers are 4P ∉ S, 6P, 10P); pay(6P) = 2P.  Out-edges of 6P: to 10P only, which has
  none (5P divides no other member).  Acyclic.  **Correct.**  (If 10P ∉ S, P6 directly.)
* **A3 (6P ∉ S, 4P ∈ S).**  8P lists {8} ∖ S, so 8 ∉ S and pay(8P) = 8; 8t′ pays 4t′, so 4t′ ∉ S.  T′ = T − 4P + 6P
  + 4t′ on n − 1.  Layer 4: members S₄ − 12P; pool = π's pool − 6P − 4t′ + 4P.  Scheme: pay(8P) = 4P (listed by 8P
  alone now), pay(8t′) = 8, others as π.  In-edges to 8t′ need pay(a) ∈ {4t′, 8}: none; in-edges to 8P need pay(a) ∈
  {4P, 8}: 8t′ only; out-edges of 8P: 4P | b only for b = 12P, gone.  So no cycle through 8t′ or 8P, and the rest is
  π.  Layer 3: members S₃ − 4P + 6P + 4t′; pay(6P) = 2P after 10P → 5P (4P no longer a member), pay(4t′) = 2t′ after
  6t′ → 3t′ (listed by 6t′ alone, in the pool); the out-edges 6P → 10P and 4t′ → 6t′ end in sinks; removing 4P removes
  edges only.  Acyclic.  Gain 2P + 4t′ > 2P + 16P/3 > 6P > 6P₁.  **Correct.**
* **B (6P ∈ S).**  6P₁ ∉ S by the cycle lemma.  **Correct.**
* **B-G4 (4P₁ ∈ S).**  Forced: 8P₁ → 8 (so 8 ∉ S), 8P → 4P (so 4P ∉ S), 12P → 12 (so 12 ∉ S), 12P₁ → 6P₁, 8t′ → 4t′
  (so 4t′ ∉ S).  T″ = T − 4P₁ + 6P₁ + 4t′.  Layer 4: pool = π's − 6P − 6P₁ − 4t′ + 4P₁; scheme pay(12P₁) = 12,
  pay(8P₁) = 4P₁, pay(8t′) = 8, others as π; injective (12 was 12P's, 8 was 8P₁'s, 4P₁ was a move).  In-edges: 8t′
  none; 8P₁ only from 8t′ (8); 12P₁ only from 8P₁ (4P₁; 6P₁ is a member, 12 its own).  No cycle through any of the
  three; the rest is π.  **Correct.**  Layer 3: pay(6P₁) = 2P₁ after 10P₁ → 5P₁ (and 4P₁ removed) — **and 14P₁ → 7P₁
  when 14P₁ ≤ n, which the text omits**; pay(4t′) = 2t′ after 6t′ → 3t′; sinks.  Gain 6P₁ + (4t′ − 4P₁) > 6P₁.
  **Correct once the 14P₁ slip is closed.**
* **B1 (4P₁ ∉ S, some scheme π pays 12P with 12).**  The text says "As proved above"; nothing above proves it (the
  only earlier mention, the measured mechanism, is data).  **A gap in the text; the claim is true.  Proof:**
  Layer 3 of T + 6P₁: as in B-G4 (2P₁'s listers 4P₁ ∉ S, 10P₁ → 5P₁, 14P₁ → 7P₁; sinks).  Layer 4: pool loses 6P
  and 6P₁ (listed by 12P alone and by 12P₁ alone).  Sub-cases on π:
  (a) pay(12P₁) = 4P₁: nobody paid 6P₁; π restricted to T₄ serves.
  (b) pay(12P₁) = 6P₁: set pay(12P₁) = 12 (free: 12P gone, 12 ∉ S).  Any cycle passes through 12P₁ and enters it
  from a member paying 4P₁, which can only be 8P₁.  (b-i) pay(8P₁) = 8: no in-edge, acyclic.  (b-ii) pay(8P₁) = 4P₁:
  the cycle enters 8P₁ from the member h paying 8 in π, if any.  h absent (8 ∈ S or 8 unpaid): acyclic.  h = 8P: 8P's
  in-edges need pay(a) = 4P, and 4P's other lister 12P pays 12: none.  h = 8t′: 8t′'s in-edges need pay(a) = 4t′,
  listed by 8t′ alone: none.  h = some other 8u (a source 8u > 6P, or a promoted 16, 24, 40, …): then 8P does not pay
  8, so 4P ∉ S and pay(8P) = 4P, and π has the edges h → 8P (8 | 8P), 8P → 12P (4P | 12P) and 12P → b for every
  member b with 12 | b.  A cycle of the new scheme is 12P₁ → b ⇝ h → 8P₁ → 12P₁ with 12 | b, and its segment b ⇝ h
  avoids 12P₁ and 8P₁ (8P₁'s only out-edge is to 12P₁), so it is made of π-edges; then 12P → b ⇝ h → 8P → 12P is a
  closed walk in π, against its acyclicity.  So the new scheme is acyclic in every sub-case.  ∎  Bound 6P₁.
* **G2 (4P₁ ∉ S, every scheme pays 12P with 4P).**  Then 4P ∉ S, and in every scheme 8P → 8, 8P₁ → 4P₁, 8t′ → 4t′
  (so 8, 4t′ ∉ S), 12P₁ → 6P₁ or 12.  **Correct.**  The split G2-i / G2-ii is complete.
  * **G2-i** (some such scheme pays 12P₁ with 12): nobody paid 6P₁; layer 4 of T + 6P₁ is π restricted; layer 3 as in
    B1.  **Correct with the 14P₁ fix.**
  * **G2-ii** (every scheme pays 12P₁ with 6P₁): T + 4t′; layer 4: pay(8P) = 4P (listed by 8P alone on n − 1),
    pay(8t′) = 8, 8t′ without in-edge, 8P's only in-edge from 8t′, 8P without out-edge; layer 3: 4t′ → 2t′ after
    6t′ → 3t′.  **Correct**; the bound 4t′ holds whether 12 goes to a 12t₀ or is itself a move of S.
    The *Remark* (t₀ ≤ 3P/4) is not fully justified: "the cycle lemma with t₀ in place of P₁" needs 8t₀ ∈ S, which
    nothing gives.  If 8t₀ ∉ S, 4t₀ ∈ S and 6t₀ ∈ S, 12t₀ lists {12} alone and the case's assumption stands with t₀
    ∈ (3P/4, P).  The remark is not used by the theorem.
* **Case split.**  {6P ∉ S: 9P ∉ S | 4P ∉ S | 4P ∈ S} ∪ {6P ∈ S: 4P₁ ∈ S | 4P₁ ∉ S and (some scheme pays 12P with 12
  | every scheme pays 12P with 4P, then 12P₁ with 12 in some | with 6P₁ in every)}.  12P lists {4P, 12} ∖ S in case B,
  so it pays one of them in every scheme.  Complete.
* **The conclusion** ΣT ≤ opt(n − 1) − min(6P₁, 4t′), with 6P₁ except in G2-ii: follows.

*The 14P₁ slip, closed.*  When 14P₁ ≤ n, 14P₁ may be a member of S₃ paying 2P₁.  Re-pay it with 7P₁: 7P₁ ≤ 6P
exactly when 14P₁ ≤ 12P, it is layer 2 and so in the pool (F10), and 14P₁ is its only lister (21P₁ > n).  After the
re-payment 14P₁ has no out-edge (7P₁ divides no other member), so it is a sink like 10P₁, and the argument of each
layer-3 step goes through unchanged.  The slip affects B-G4, B1 and G2-i at the two games 276 and 444 only (and
nothing at the other 71 of 228..5052, where 14P₁ > n); it is a slip of the text, not of the theorem.

## 4. Checks run (`referee_check.py`, output in `referee_check_out.txt`)

My own code, standard library; playability by the residual of the instance (P5/P7), not the author's peel.

* **A. Arithmetic facts** for every prime P in 19..50,000 with 15P₁ > 12P (5,125 primes): every lister list of
  section 1, the mf sets, the sides of n/2, the layers, no collisions.  0 failures.  14P₁ ≤ 12P at exactly two of
  the 5,125: n = 276 and 444; everywhere else the text's lister list for 2P₁ is right.
* **B. The proof walked on the recorded optimal set** of each 12P game of 228..5052 whose S holds 8P, 8P₁, 12P₁ and
  an 8t′ (73 games; 228 has no 8t′ in S, 348 fails 15P₁ > 12P, as the author says).  12P ∈ S, no layer-2 number ≤ n/2
  in S, S and T playable; the case decided from S's layer-4 instance (whether a scheme with pay(12P) = 12 exists, by
  the residual with 12P's list cut to {12}); the constructed set playable; ΣT + bound ≤ opt(n − 1); ΣT ≤ opt(n − 1) −
  min(6P₁, 4t′); δ = 6P₁ whenever 4t′ ≥ 6P₁, δ ≥ 4t′ otherwise.  0 problems.  **All 73 are case B1** (6P ∈ S, 4P₁ ∉
  S, 12P can pay 12), the case the text leaves unproved; the other cases (A1, A2, A3, G4, G2-i, G2-ii) rest on the
  proof alone, which I audited in section 3.  At 276 and 444 the recorded S holds 14P₁, listing 2P₁ (part E: S has
  schemes with 14P₁ paying 2P₁ and schemes without; T + 6P₁'s layer 3 is playable with the text's two re-payments
  alone there, and with 14P₁ → 7P₁ added), so the slip is real in the recorded sets and the closure works.
* **C. U\*(n) by my own descending greedy** (residual-based) at 276, 444, 1668, 2004, 2316, 2748, 4308: 8P, 8P₁,
  12P₁ ∈ U\*, the t′ lists match the author's, U\*_{≥3} ⊆ S and the sources of S are exactly U\*.  The author's
  `study/twelvep_hyp.py` rerun gives its recorded output (114 games 228..8191, 89 with 4t′ ≥ 6P₁, failures 228 and
  348).
* **D. Random layer-4 instances** at 276, 444, 996, 1668, 2004 (150 samples each): a random playable set of layer-4
  members holding 12P, 8P, 8P₁, 12P₁, 8t′ against a pool shaped by a random set of layer-3 moves, biased so that some
  other 8u must pay 8.  For each sample the case is decided as the proof decides it and the layer-4 instance the proof
  builds on board n − 1 is tested by its residual: A3 199, G4 61, B1 242 (of which **144 with another 8u paying 8**
  while 12P pays 12, 12P₁ pays 6P₁ and 8P₁ pays 4P₁: the sub-case that needs the acyclicity argument of section 3,
  never seen in the chain), G2-ii 28, A1/A2 152.  0 failures.  (G2-i did not arise; its layer-4 step is a plain
  restriction.)

## 5. Where the hypotheses enter

* **U at n**, with 8P, 8P₁, 12P₁, 8t′ ∈ U\*(n): only to put those four in one optimal set S.  Nothing else in the
  proof uses U, and one optimal set suffices (section 1).  The theorem would be cleaner as "if some optimal set of n
  holds 8P, 8P₁, 12P₁ and 8t′, then ...", with U + U\* as one way to get the hypothesis.
* **n ≥ 187**: F10, so that 4, 6, 2P, 3P, 5P, 2P₁, 3P₁, 5P₁, 7P₁, 2t′, 3t′ are in the layer-3 pool.
* **15P₁ > 12P**: binding only as "5P₁ is listed by 10P₁ alone" (the re-payment of 10P₁ in B-G4, B1, G2-i when 10P₁
  ∈ S); the other uses (6P₁ private to 12P₁, 4P₁ to 8P₁ and 12P₁, 7P₁ to 14P₁) need only P₁ > 2P/3.  It does *not*
  give 14P₁ > n (that needs P₁ > 6P/7), which is the slip.
* **t′ ∈ (4P/3, 3P/2]**: 8t′ on the board and a source; 4t′ a factor below n/2 and private to 8t′; 2t′ listed by
  4t′, 6t′ only; 3t′ private to 6t′ (binding: 9t′ > n ⇔ t′ > 4P/3).  "Largest such t′" only makes the bound best.
* **The cycle lemma** needs none of these beyond the mf sets.

## 6. Verdict

**Correct for the proved cases, with two gaps in the text that I closed; the bound δ ≥ 4t′ in G2-ii is proved.**

1. *B1 is asserted, not proved* ("As proved above" points at the measured mechanism, which is data).  It is true;
   the proof is in section 3, and its one nontrivial sub-case (12P → 12, 12P₁ → 6P₁, 8P₁ → 4P₁, another 8u → 8) uses
   the acyclicity of S's own scheme through the chain 8u → 8P → 12P → 12t.  Every proven 12P game is in B1, so this
   is the case the theorem's coverage claims rest on.
2. *The 14P₁ slip*: the layer-3 re-payment steps assume 2P₁'s listers are 4P₁, 6P₁, 10P₁; 14P₁ is on the board at
   276 and 444 (and in S there).  Closed by re-paying 14P₁ with 7P₁, private to it.
3. The G2-ii *Remark* (t₀ ≤ 3P/4) is unjustified as written (needs 8t₀ ∈ S); it is not used.
4. "Every optimal set holds ..." overstates U; the proof needs one optimal set and has it.

The case split is complete; every forced payment is forced; every constructed set is playable by the arguments of
section 3 (and by the residual on the 73 recorded sets and 680 random layer-4 instances); the gains are as claimed.

## 7. The second draft (2026-11-10, later): G2-ii closed, δ ≥ 6P₁ in every case

Refereed against the updated Section 4 of `study-report.md`.

* **Transcription of the repairs.**  The theorem now takes "some optimal set S of n holds 8P, 8P₁, 12P₁, 8t′" as
  its hypothesis (U + U\* as the way to get it); the Facts list 14P₁ among 2P₁'s listers and 7P₁ private to 14P₁;
  "the layer-3 step for 6P₁" (10P₁ → 5P₁, 14P₁ → 7P₁, then 6P₁ → 2P₁ into sinks) is stated once and used in B-G4
  (with 4P₁ removed), B1, G2-i, G2-ii; B1 carries the closed-walk proof.  All faithful.  B1's text takes a = 8P₁
  paying 4P₁ and "the member before 8P₁ pays 8, say 8u"; the sub-cases with 8P₁ paying 8, or with nobody paying 8,
  have no in-edge to 12P₁ or to 8P₁ and are covered a fortiori (the text is compressed there, not wrong).
* **The new G2-ii step.**  Setting: 6P ∈ S, 6P₁, 4P₁, 4P ∉ S; in σ: 12P → 4P, 8P → 8, 8P₁ → 4P₁, 8t′ → 4t′, 12P₁
  → 6P₁.  New set T + 6P₁ on n − 1.  Layer 3: the step for 6P₁ (4P₁ ∉ S).  Layer 4: pool = σ's − 6P − 6P₁; scheme
  8P → 4P (in the pool, listed by 8P alone now), 8P₁ → 8 (8 ∉ S since 8P paid it; released), 12P₁ → 4P₁ (in the
  pool; released), others as σ, none of which paid 4P, 8 or 4P₁.  Injective: yes.  Edges: 8P has no out-edge (4P | b
  only for b = 12P, gone); 8P₁'s out-edges go to every 8u, its in-edges need pay(a) ∈ {4P₁, 8} = from 12P₁ only;
  12P₁'s out-edge goes to 8P₁ only, its in-edges need pay(a) = 12, i.e. the 12-payer of σ if there is one.  So a
  cycle must be 12t₀ → 12P₁ → 8P₁ → 8u ⇝ 12t₀ with 8u ∉ {8P, 8P₁} and the walk 8u ⇝ 12t₀ among unchanged members
  (it avoids 12P₁, 8P₁ by simplicity and 8P as a sink), hence made of σ's edges (edges depend on pay(a) and b only).
  In σ: 8P → 8u (8 | 8u), 12t₀ → 12P (12 | 12P), 12P → 8P (4P | 8P): the closed walk 8P → 8u ⇝ 12t₀ → 12P → 8P
  holds a cycle, against σ's acyclicity (F3/P2).  **Correct.**  The empty walk (8u = 12t₀, e.g. 24 paying 12) is
  covered.
* **A hole in the case description, closed.**  G2-ii is stated as "12P₁ pays 6P₁ and 12 goes to some other 12t₀".
  Two shapes are left out: 12 ∈ S (a move; then 12P pays 4P and 12P₁ pays 6P₁ in every scheme, so this is G2 and not
  G2-i), and 12 in the pool paid by nobody in σ (possible: 12P₁ → 12 would close the cycle 12P₁ → 12P → 8P → 8P₁ →
  12P₁).  In both, 12P₁ has no in-edge in the new scheme, so no cycle passes through 12P₁, hence none through 8P₁,
  and 8P is a sink: the same construction works with nothing to argue.  The text should say "12 is a move, unpaid,
  or paid by some 12t₀"; with that, the split {A1 | A2 | A3} ∪ {G4 | B1 | G2-i | G2-ii} is complete, as before.
* **The conclusion** ΣT ≤ opt(n − 1) − 6P₁ in every case: A1, A2 give 6P > 6P₁; A3 gives 2P + 4t′ > 6P; G4 gives
  6P₁ + 4t′ − 4P₁ > 6P₁; B1, G2-i, G2-ii give 6P₁.  Nothing else changed.  t′ is still needed, by A3 and G4 only.
* **Check** (`referee_check_g2ii.py`, part F in `referee_check_out.txt`): random playable layer-4 instances of 276,
  444, 996, 1668, 2004, 4308 in the G2 shape, biased so that 12 is contested or a move; where no scheme pays 12P
  with 12 and none pays 12P₁ with 12, the instance of T + 6P₁ on n − 1 with the proof's three payments forced is
  tested by its residual: 633 G2-ii samples (374 with 12 a move, 259 with 12 paid by some 12t₀), 0 failures.
  (567 samples fell in B1; "12 unpaid" did not arise, and needs no argument.)
* Stale sentences to drop: "the open case G2-ii has never been seen" and "E2 (b) ... is exactly a test of G2-ii".

**Verdict on the second draft: correct.**  The new G2-ii step is sound; the case description should name the two
trivial shapes of 12; the theorem as now stated, δ(12P) ≥ 6P₁ given one optimal set holding 8P, 8P₁, 12P₁ and 8t′,
with n ≥ 187, 15P₁ > 12P and t′ prime in (4P/3, 3P/2], is proved.

## 8. The theory-file version: docs/theory/below-the-ceiling.md (worktree theorem-12p)

Refereed as written (L1 to L4), 2026-11-10.  Numerical claims checked in part G of `referee_check_out.txt`.

* **L1 (re-payment).**  The preliminary remark is right: within a layer instance an edge a → b means b lists pay(a)
  (a ∤ b in one layer; pay(a) one layer down divides b only as a maximal factor), so edges depend on payments alone and
  an unpaid factor may enter or leave the pool with no change to any scheme's precedence.  Part 1: with pay(a) = f
  unpaid by others, a's out-edges go to the members listing f and its in-edges come from the payers of factors a
  lists; condition (i) makes a's successors sinks, condition (ii) leaves a no in-edge; either way no cycle through a,
  and the rest is the old scheme.  Correct, for a changed payment and for a joining number alike.  Part 2: each y
  listing f is re-paid with its private g_y by part 1 (vacuous condition (i)); after that y has no out-edge, since
  nobody, x included, lists g_y; then f is unpaid and x joins by part 1 (i).  Correct; the clause "and x does not"
  is exactly what keeps y a sink once x is in.
* **L2.**  Step 1's lister facts hold (12p, 9p, 10p, 12r, 9r, 10r > n; 8r > 4p as r > p/2; 6r > 4p as r > 2p/3).
  Step 3 is L1 part 2 with (x, y, f, g) as given: x lists f, only y among members lists f, g is y's own and x does
  not list it.  Case A: layer 3 by step 3, layer 4 by the remark (4p unpaid once n is gone).  B1: 8r → 8 by L1 (ii),
  then 4r unpaid leaves the pool.  B2: 8r joins paying 8 by L1 (ii): nobody pays 4r or 8.  All as the 8P referee
  found; the file's version is cleaner and equally complete ({4p ∉ S} ∪ {4p ∈ S, 8r ∈ S} ∪ {4p ∈ S, 8r ∉ S}).
* **L3.**  Simpler than the report's: whichever of 4p, 4r, 8, 12 are moves, every factor one of the four lists is
  listed by another of them, so the four are a core (a member listing nothing is one too).  Correct for distinct
  primes ≥ 5 (the mf sets need p, r ∉ {2, 3}).  The example at 372 checks: S(371) holds the six numbers, and
  S(371) − 172 + 372 has residual exactly {232, 248, 348, 372}.
* **L4, structure (1): one fixed scheme σ.**  B2 splits on σ's payment to 12r (6r, 4r or 12) and to n (4p or 12,
  since n lists {4p, 12} ∖ S in case B): the three sub-cases (12r → 4r or 12; 12r → 6r and n → 12; 12r → 6r and
  n → 4p) cover every σ.  Complete, and the quantifiers over schemes are gone.  The first sub-case merges the
  report's B1(a) and G2-i rightly: all that matters is that σ does not pay 6r.
* **(2): A1 dropped.**  Case A1 (4p ∉ S) joins 6p through 2p after 10p → 5p (step 3), with no use of 9p; A2 (4p ∈ S)
  is the report's A3.  Complete.
* **(3): the uses of L1 in L4.**  Step 3: 6p through 2p needs 4p ∉ M (then 10p, listing 2p, has 5p private; 6p does
  not list 5p); 6r through 2r needs 4r ∉ M (10r has 5r, 14r has 7r, 7r in the pool exactly when 14r ≤ n); 4t through
  2t (6t has 3t; 4t does not list 3t): each is L1 part 2.  A2, layer 4: 8p → 4p (L1 (i), vacuous: no other lister),
  then 8t → 8 (L1 (ii): nobody else pays 4t or 8); then 6p, 4t unpaid leave the pool.  B1, layer 4: 12r → 12, then
  8r → 4r, then 8t → 8, each by L1 (ii) at its moment (when 12r moves, 4r has entered the pool and 8r still pays 8;
  when 8r moves, 4r is unpaid; when 8t moves, 8 is released); the order is right and necessary.  B2 sub-case 2:
  12r → 12 and the closed walk n → b ⇝ h → 8p → n of σ, with the branches "nobody pays 8" and "h = 8p" (8p then has
  no in-edge, since 4p is unpaid once n is gone); the walk b ⇝ h misses 12r and 8r, so it is σ's.  Correct.  B2
  sub-case 3: 8p → 4p (sink, L1 (i)), 8r → 8 (no in-edge, L1 (ii)), 12r → 4r: if 12 is a move or unpaid, L1 (ii);
  if some 12s pays 12, the closed walk 8p → b ⇝ 12s → n → 8p of σ, with b ≠ 8p since 8p has no out-edge.  Correct,
  and it names the two shapes of 12 my section 7 asked for.
* **(4): any t in (4p/3, 3p/2].**  Nothing used "largest"; the gains 2p + 4t > 6p and 2r + 4t > 6r need only
  t > 4p/3 and t > r.  Fine.
* **(5): the repairs.**  One optimal set (statement and proof); 14r among 2r's listers with 7r private to it (step 1),
  7r in the pool when 14r ≤ n (step 2), used in step 3; B1's and G2-ii's closed-walk proofs (B2, sub-cases 2 and 3).
  All transcribed faithfully.
* **Side claims checked (part G).**  248: opt(247) + 248 − 116 = 19,291 = opt(248) and S(247) − 116 + 248 = S(248).
  372: 43,698 = opt(372) and S(371) − 174 + 372 = S(372).  184 rises by 136 > 108 and S(184) holds 91, 114, 171.
  204 rises by 129 > 126, S(204) holds 136, 104, 156, 184, 130, 195.  Rises of exactly n − 6r at 156, 228, 348 and
  n − 4r at 152, 232, 296, 424.  The exchange S(n − 1) − 4r + n reaches opt(n) at all 103 games 8p of 248..5048 with
  9r > n, and S(n − 1) − 6r + n at all 73 games 12p of 228..5052 whose recorded S holds 8p, 8r, 12r and some 8t
  (the first 276).
* **Wording, not errors.**  The closing paragraph says t enters "through 9t > n ... and through 8t ≤ n"; step 3 also
  uses 10t > n (2t listed by 4t and 6t alone) and 12t > n (4t private to 8t), both implied by t > 4p/3.  In B2
  sub-case 2 the clause "only 8r, paying 4r, can be one" silently covers the branch where 8r pays 8 (no in-edge to
  12r at all).

**Verdict on the file: correct as written.**
