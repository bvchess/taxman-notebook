# Referee's notes on Section 3 (Theorem A and its corollaries)

Written as the check proceeds, 2026-11-11.  Definitions are taken from docs/theory/parity-bound.md,
docs/theory/primer/greedy.md and the brief's Section 1; nothing is assumed that those do not state.

## Part 1: the setting, checked against the definitions

* Board m has the coordinates 1..⌊m/2⌋, 1 among them (Ω(1) = 0, coordinate 1 in E₀).  For odd n,
  ⌊n/2⌋ = ⌊(n − 1)/2⌋ = (n − 1)/2: boards n − 1 and n have the same coordinates.  ✓
* Sources of board m: numbers > m/2.  For odd n, sources of n − 1 are the numbers ≥ (n + 1)/2 and ≤ n − 1; sources
  of n are the same and n.  ✓ (the proof's first sentence)
* A source has no e_s; its parity vectors are v(s) (at the parity ≢ Ω(s)) and a private extra coordinate (at the
  parity ≡ Ω(s)).  A number x ≤ n/2 has v(x) and e_x, no extra.  (parity-bound.md, the definition; W3 step 1.)
* Every number x ≤ n − 1 has the same two parity vectors on boards n − 1 and n (odd n): same coordinates, same
  maximal factors (all ≤ x/2 ≤ (n − 1)/2), same e_x, same extra.  ✓
* v(n) ≠ 0 for every n ≥ 2 (mf(n) is nonempty; a prime has v = e₁).  So the greedy on board n keeps n first.  ✓
* No ties in the greedy order: sources have distinct values.  ✓
* The greedy basis G(m) spans the whole family of sources' vectors (primer, "What the scan finds" (a)), and is
  independent.  ✓
* PB(m) = ΣG(m) + Q*(m): by W3 every heaviest set independent at both parities holds exactly G(m) among the sources,
  so it is G(m) ∪ L with L ⊆ 2..⌊m/2⌋ and G(m) ∪ L independent at both parities; conversely every such G(m) ∪ L is
  a set independent at both parities.  ✓ (words.md's derivation is right.)

## Part 2: Theorem A, step by step

**Part 1 (v(n) ∉ V).**  Induction down the sources with the hypothesis "board n has kept n and exactly K_y above
y".  Case y ∈ G(n − 1): v(y) ∉ span(K_y).  If v(y) ∈ span(K_y + n), the representation uses n (else
v(y) ∈ span(K_y)), so v(n) = v(y) + (a sum over K_y) ∈ span(K_y + y) ⊆ V, against the hypothesis.  Case
y ∉ G(n − 1): v(y) ∈ span(K_y) ⊆ span(K_y + n).  Both follow.  ✓

**Part 2, C exists and is unique.**  V = span of all sources' vectors of board n − 1; G(n − 1) is a basis of that
family's span (primer (a)), so v(n) ∈ V is a sum over a subset C of G(n − 1), unique because G(n − 1) is
independent (two representations would differ by a vanishing nonempty combination).  v(n) ≠ 0 so C ≠ ∅ and x_G
exists.  ✓

**Every member of C has n's layer.**  v(c) lives on the coordinates of layer Ω(c) − 1.  Group C by layer: the
members of a layer k ≠ Ω(n) sum to a vector on layer-(k − 1) coordinates that must vanish (v(n) is zero there and
no other layer reaches those coordinates); a nonempty subset of the independent G(n − 1) cannot sum to zero, so
that group is empty.  ✓  (Not needed for G(n); needed for the spans at each parity, below.)

**Down the sources.**  Hypothesis for y > x_G: board n has kept n and exactly K_y.  y ∈ G(n − 1): if
v(y) ∈ span(K_y + n) then v(n) ∈ span(K_y + y), a representation of v(n) by members of G(n − 1) all above x_G,
hence a subset of G(n − 1) summing to v(n) that misses x_G: a second representation, against uniqueness.  ✓
y ∉ G(n − 1): rejected as in part 1.  ✓  At y = x_G: C − x_G ⊆ K_{x_G} (its members are in G(n − 1) and above
x_G), so v(x_G) = v(n) + Σ_{C − x_G} v(c) ∈ span(K_{x_G} + n): rejected.  ✓  For y < x_G: the kept set above y
on board n is K_y − x_G + n (by the induction, K_y here holds x_G); C ⊆ K_y, so v(n) ∈ span(K_y), so
span(K_y − x_G + n) ⊆ span(K_y); and v(x_G) ∈ span(K_y − x_G + n), so span(K_y) ⊆ span(K_y − x_G + n).  Equal
spans, so y's decision is the same.  ✓  Hence G(n) = G(n − 1) − x_G + n.  ✓

**The spans at each parity.**  What the admissible family at parity i depends on: a set L of numbers up to n/2 has
parity-i vectors in E_i, with no extra coordinates; G is independent at parity i (its v's are independent, its
extras private); G ∪ L is independent at parity i iff no nonempty L′ ⊆ L has Σ_{L′} (parity-i vectors) in the span
of G's parity-i vectors.  Such a sum has zeros at every extra coordinate, and the extras are private, so it lies in
that span iff it lies in W_i(G) := span{v(s) : s ∈ G, Ω(s) ≢ i}.  So the admissible family at parity i is
determined by W_i(G) alone.

* Parity i ≡ Ω(n) (mod 2): n and x_G have extras there (both have layer Ω(n), by the layer fact above), so they
  are absent from W_i; the other members are the same on both boards.  W_i(G(n)) = W_i(G(n − 1)).  ✓
  *Wording*: the theorem says "the same span at each parity"; at this parity the spans of the full parity-i
  families differ by the private coordinates of x_G and n.  The statement should say the spans of the vectors
  without extra coordinates, or that the same sets L are admissible.  The conclusion is unaffected.
* Parity i ≢ Ω(n): n and x_G contribute v(n) and v(x_G); every member of C has layer Ω(n), so C − x_G
  contributes its v's to both W_i's; v(n) = Σ_C v(c) ∈ W_i(G(n − 1)) and v(x_G) = v(n) + Σ_{C − x_G} v(c)
  ∈ W_i(G(n)).  Equal.  ✓  (Here the layer fact is load-bearing: if some c ∈ C had Ω(c) ≡ i its parity-i vector
  would be an extra, not v(c).  The proof's sentence "the other members contribute the same vectors on both
  boards" does not say this; the layer fact two sentences earlier supplies it.)

**Q*(n) = Q*(n − 1).**  The same L range over 2..(n − 1)/2 on both boards with the same parity vectors, and the
same L are admissible at each parity.  ✓  PB(n) = ΣG(n) + Q*(n) = ΣG(n − 1) − x_G + n + Q*(n − 1).  ✓

**Verdict on Theorem A so far: correct.**  Two wording gaps, both closed above: "same span at each parity" is true
of the spans without extra coordinates (which is all Q* sees), and the layer fact is what makes the other members'
contributions "the same" at the parity ≢ Ω(n).

Sanity check at n = 3: board 2 has G(2) = {2}, V = span{e₁}; v(3) = e₁ ∈ V, C = {2}, x_G = 2, G(3) = {3},
PB(3) = PB(2) + 3 − 2 = 3 (the two primes share e₁ at parity 0, so {3} is the heaviest set).  ✓

## Part 3: the numeric check (check_a.py, check_a2.py in this folder; 34 s and 43 s at nice 19)

Independent of the proof: the greedy basis G(m) computed from scratch on every board 3..5060 (sources taken from m
down, Gaussian elimination over GF(2) on bitsets, with each pivot row carrying the sources that sum to it), and the
parity bound PB read from settle.csv's `bound` column (the notebook's parity bound, which solver/noframe/src/parity.rs
defines with the coordinates 1..⌊n/2⌋, 1 included, and an extra coordinate for each source: the doc's definition).

* Odd n: v(n) ∈ V at 1,750 boards (676 primes, 971 odd semiprimes ≥ 189, 103 others), v(n) ∉ V at 779.  At every one
  of the 1,750, G(n) = G(n − 1) − x_G + n with x_G from the unique representation, every member of C has n's layer, and
  PB(n) − PB(n − 1) = n − x_G.  At every one of the 779, G(n) = G(n − 1) + n and PB(n) ≤ PB(n − 1) + n.
* Even n: s = n/2 ∈ G(n − 1) at 1,388 boards, where G(n) = G(n − 1) − s + n and 0 ≤ δ_PB ≤ s; s ∉ G(n − 1) at 1,141,
  where G(n) = G(n − 1) + n and δ_PB = 0.
* The classification by v(n) ∈ V and by s ∈ G(n − 1) agrees with settle.csv's `step` column (built from U\*) at every
  board 3..5060 with no exception, as (♦) says it must.
* δ(n) = x_G at all 676 primes, all 971 odd semiprimes ≥ 189 and all 103 other exchanges (rise = 0 at each); x_G is
  the shadow of n at all 1,750.  settle.csv has 1,074 exchange rows (995 repeats, 79 searched), all with rise 0;
  the report's "103 exchange rows" are the 1,074 less the 971 odd semiprimes ≥ 189 that A2 counts separately.

Agreement is not proof; the proof is checked in Parts 2 and 4.  The check rules out a definitional slip (coordinate 1,
the extras, the range of L) between the report, the doc and the prover.

## Part 4: the corollaries, Proposition B and the lemmas

**A1 (given (♦) at n − 1 and n).**  By W3, G(n − 1) = U\*(n − 1) and G(n) = U\*(n).  An exchange step is, by the
brief's definition, U\*(n) = U\*(n − 1) − x + n for some source x, so G(n) ≠ G(n − 1) + n, so part 2 of Theorem A
applies and x = x_G: δ_PB(n) = x.  Then δ(n) = δ_PB(n) + rise(n) = x + rise(n), so δ(n) = x iff rise(n) = 0 and
δ(n) ≥ x iff gap(n) ≥ gap(n − 1).  ✓  "x the shadow" is marked measured, as it is.  ✓  Without (♦), δ_PB(n) = x_G is
Theorem A itself.  ✓  Correct.

**A2 (no U, no (♦)).**  Three facts are used without citation; all three are in the theory:
1. G(m) splits by layer: vectors of different layers lie on disjoint coordinates, so a source's vector lies in the
   span of the kept sources iff it lies in the span of the kept sources of its own layer.  So G(m) ∩ layer 2 is the
   scan on the layer-2 sources alone.
2. The layer-2 sources' vectors (v(pq) = e_p + e_q, v(p²) = e_p) are independent over GF(2) iff the edges form a
   forest in G_n with its ground vertex g: the two-factor proposition P11 (playability.md), parts 2 and 3.
3. Descending greedy on the sources decides a layer-2 source by its layer-2 instance alone (F3), and keeps it iff it
   closes no cycle with the kept layer-2 sources: F4's proof, step 3 (frame-model.md), "on these sources it is the
   scan".
So G(m) ∩ layer 2 = U\*₂(m) with no conjecture.  For odd n = pq or p² ≥ 189, J3's hypothesis holds (its step 7, by
F10), C ⊆ G(n − 1) ∩ layer 2 = U\*₂(n − 1) (the layer fact of Theorem A), and the path of n in that forest sums to
v(n) (e_p + e_q along a p–q path; e_p along a p–g path, since g has no coordinate), so by uniqueness C is that path,
the cycle less n, and x_G = min C = J3's x.  J3 gives δ(n) = x, Theorem A gives δ_PB(n) = x_G = x, so rise(n) = 0.  ✓
At a prime p: v(p) = e₁ ∈ V, C = {q(p − 1)} (the one prime in G(p − 1), kept first among the primes; only primes
reach coordinate 1), so δ_PB(p) = q(p − 1) and N5 gives δ(p) = q(p − 1): rise = 0.  ✓  So the "prime step of PB" is
a case of Theorem A.  Correct, with the three citations supplied.

**A3 (given U at n − 1 and (♦) at n − 1).**  δ_PB(n) = 0 needs neither: s = n/2 is a maximal factor of no x ≤ n − 1
(x = sp ≥ 2s = n), so no vector of a member of I has a 1 at s, and s ∉ I by W3 (s ∉ G(n − 1)); I's members keep
their parity vectors on board n (shown in Part 1's bullet, which holds for even n too since only coordinate s is
new and nobody but n and s uses it); v(n) has a 1 at s and n has an extra at the other parity; so I + n is
independent at both parities on board n and PB(n) ≥ PB(n − 1) + n.  The parity ceiling PB(n) ≤ PB(n − 1) + n: I
checked it (take a heaviest I of board n; I − n is independent at both parities on board n − 1, because the only
change is that s, if in I, trades e_s for a private extra, and coordinate s, which only n's vector used, disappears).
✓  δ(n) = 0: (♦) at n − 1 makes s ∉ U\*(n − 1); U at n − 1 with F4 (U\*₁ = {q}, U\*₂) gives an optimal set T ⊇
U\*(n − 1), and T holds no other source (a source y ∉ U\* was rejected because the kept sources above it with y are
unplayable, and that set would lie in T: X8's proof, step 1), so T avoids s and the half lemma N7 gives δ(n) = 0.  ✓
Correct as stated; the first conclusion is unconditional.

**Proposition B.**  Part 1: Theorem A part 1; G(n − 1) ∪ L ⊆ G(n) ∪ L and independence passes to subsets, with the
same vectors on both boards; δ_PB = Q\*(n − 1) − Q\*(n) ≥ 0 by PB = ΣG + Q\*.  ✓  Part 3: the sources of board n are
those of board n − 1 less s plus n; n is kept first; for an old source y > s the kept set above y on board n is
K_y + n by the induction of Theorem A part 1, since v(n) has a 1 at s and no old source's vector does, so v(n) is
outside the span of every set of old vectors; the two cases follow.  ✓  Relaxation: L admissible for G(n − 1) has
L ⊆ 2..s − 1; G(n − 1) − s and L keep their vectors on board n; adding n is independent at both parities (the 1 at s;
the extra).  ✓  δ_PB = s − (Q\*(n) − Q\*(n − 1)): arithmetic from PB = ΣG + Q\* and ΣG(n) = ΣG(n − 1) − s + n; ≤ s
since the family grows; ≥ 0 by the parity ceiling.  ✓  Correct.  gap(n) = Q\*(n) − P\*(n) given U and (♦) at n: X8
and W3.  ✓  The rise formula that follows needs U and (♦) at n − 1 as well; the text names n only.  (Minor.)

**Lemma C.**  Σ(I − D + A + n) = PB(n − 1) − ΣD + ΣA + n = PB(n − 1) + n − δ(n), using D ⊆ I and A ∩ I = ∅ (both
hypotheses) and δ(n) = ΣD − ΣA (from S\* = T′ − D + A + n with D ⊆ T′, A ∩ T′ = ∅, n ∉ T′, the section's convention).
PB(n) ≥ that, so δ_PB(n) ≤ δ(n), rise ≥ 0.  ✓  Correct.  (It does not need n to be a relaxation or restriction.)

**Lemma D.**  PB(n) − PB(n − 1) = n − ΣD_Q + ΣA_Q needs D_Q ⊆ I and A_Q ∩ I = ∅, which "J = I − D_Q + A_Q + n" means.
opt(n) ≥ Σ(T′ − D_Q + A_Q + n) needs that set playable (hypothesis).  Σ(T′ − D_Q + A_Q + n) ≥ ΣT′ − ΣD_Q + ΣA_Q + n
needs A_Q ∩ (T′ − D_Q) = ∅: a member of A_Q already in T′ is counted once on the left and twice on the right.
(Σ(T′ − D_Q) ≥ ΣT′ − ΣD_Q holds whether or not D_Q ⊆ T′.)  That hypothesis is not stated; with it, rise ≤ 0.  ✓  The
second sentence (a game scoring opt(n − 1) + PB(n) − PB(n − 1) gives rise ≤ 0) is immediate.  ✓  Correct once
A_Q ∩ T′ = ∅ is said (it is what "T′ − D_Q + A_Q" means under the section's convention, but Lemma D's D_Q, A_Q are the
parity bound's change, not the game's, so the convention does not supply it).

**3.4.**  Every n ≥ 3 is a prime, an exchange, a restriction, a relaxation or half-out (Theorem A and B.3 split the
odd and even cases; given (♦) the split by G is the split by U\*).  rise = 0 at primes (A2), at exchanges iff the
exchange law holds (A1, given (♦) at n − 1 and n), at half-out games given U and (♦) at n − 1 (A3).  So on the chain,
where (♦) is checked on every board and the scores past 2531 themselves rest on U, the gap moves only at relaxations
and restrictions.  ✓  Correct under those hypotheses.
