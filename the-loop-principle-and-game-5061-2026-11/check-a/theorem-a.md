## 3. What is proved

### 3.1 The parity bound's exchange formula

**Theorem A (proved; no U, no (♦)).**  Let n ≥ 3 be odd, and let V be the span over GF(2) of the vectors v(s) of
the sources s of board n − 1.

1. If v(n) ∉ V, then G(n) = G(n − 1) + n.
2. If v(n) ∈ V, there is exactly one set C ⊆ G(n − 1) with Σ_{c ∈ C} v(c) = v(n); let x_G be its smallest member.
   Then G(n) = G(n − 1) − x_G + n, G(n) and G(n − 1) have the same span at each parity, Q\*(n) = Q\*(n − 1), and

       PB(n) = PB(n − 1) + n − x_G,   that is   δ_PB(n) = x_G.

*Proof.*  On boards n − 1 and n the numbers up to n/2 are the same, since n is odd, so every number but n has the
same vectors on both, and the sources of board n are those of board n − 1 and n.  The greedy algorithm on board n
keeps n first (v(n) ≠ 0) and then takes the old sources in the old order.  Write K_y for the sources of board n − 1
above y that G(n − 1) keeps.

*Part 1.*  Suppose, by induction down the sources, that board n keeps n and exactly K_y above y.  Board n keeps y iff
v(y) ∉ span(K_y + n).  If y ∈ G(n − 1) and v(y) ∈ span(K_y + n), then v(n) ∈ span(K_y + y) ⊆ V, against the
hypothesis; so y is kept.  If y ∉ G(n − 1), v(y) ∈ span(K_y) ⊆ span(K_y + n), and y is rejected.

*Part 2.*  C exists since G(n − 1) spans V ([the greedy algorithm](https://github.com/bvchess/taxman/blob/287486e/docs/theory/primer/greedy.md#the-greedy-algorithm)
keeps a basis of the span), and is unique since G(n − 1) is independent.  The vectors of different layers lie on
disjoint coordinates (the maximal factors of a number of layer k have layer k − 1), so every member of C has n's
layer.  Down the sources: for y > x_G in G(n − 1), v(y) ∈ span(K_y + n) would give v(n) ∈ span(K_y + y), a
representation of v(n) by members of G(n − 1) all above x_G, against uniqueness; so y is kept, and a rejected y
stays rejected as in part 1.  At y = x_G: v(x_G) = v(n) + Σ_{C − x_G} v(c) ∈ span(K_{x_G} + n), so x_G is rejected.
For y < x_G: the kept set above y on board n is K_y − x_G + n, whose span equals span(K_y): it contains v(n) =
Σ_C v(c) with C ⊆ K_y, and conversely v(x_G) = v(n) + Σ_{C − x_G} v(c); so y's decision is the same on both
boards.  Hence G(n) = G(n − 1) − x_G + n.

*The spans at each parity.*  At the parity of n's layer, n and x_G have extra coordinates and the other members
contribute the same vectors on both boards.  At the other parity, G(n − 1) contributes v(x_G) and the vectors of its
other members, G(n) contributes v(n) and the same others, and the two spans are equal by the two identities above.
A set L of numbers up to n/2 is independent at parity i together with G exactly when the classes of its parity-i
vectors modulo the span of G's parity-i vectors are independent (the primer), so the same sets L are admissible for
G(n) and for G(n − 1): Q\*(n) = Q\*(n − 1).  With PB = ΣG + Q\* (Section 1), PB(n) = PB(n − 1) − x_G + n.  ∎

**Corollary A1 (the exchange step; proved given (♦) at n − 1 and n).**  At every exchange step, U\*(n) =
U\*(n − 1) − x + n with x the shadow (measured) and δ_PB(n) = x.  So the exchange law δ(n) = x holds at n if and
only if rise(n) = 0, and its open half δ(n) ≥ x is gap(n) ≥ gap(n − 1).  Without (♦) the same holds with x_G, which
descending greedy's twin, the greedy basis, computes in the same time.  *Checked*: rise = 0 at all 103 exchange rows
of settle.csv, searched and repeats (`study/rise_kinds_out.txt`).

**Corollary A2 (semiprimes and primes; proved).**  For odd n ≥ 189 with two prime factors, rise(n) = 0: J3 gives
δ(n) = x, the smallest other member of the cycle n closes with U\*₂(n − 1) in G_n, and in layer 2 the greedy basis is
U\*₂ and the circuit of v(n) is that cycle, so x_G = x.  At a prime p, rise(p) = 0 by the prime step of PB and N5.
*Checked*: rise = 0 at all 971 odd semiprimes from 189 and all 676 primes of the chain.

**Corollary A3 (half-out games; proved given U at n − 1 and (♦) at n − 1).**  Let n be even with n/2 ∉ G(n − 1).
Then δ_PB(n) = 0, and given U at n − 1 (which with (♦) makes n/2 ∉ U\*(n − 1) the half lemma's hypothesis) δ(n) = 0,
so rise(n) = 0.  *Proof.*  No number of board n − 1 lists n/2 (its next multiple is n), so on board n no vector of a
member of a heaviest set I of board n − 1 has a one at the coordinate n/2, while v(n) has one there; so I + n is
independent at both parities on board n (at the other parity n has an extra coordinate), and PB(n) ≥ PB(n − 1) + n,
with equality by the parity ceiling.  ∎  *Checked*: rise = 0 at all 1,141 half-out games of the chain.

### 3.2 The three kinds of step in the parity bound

**Proposition B (proved).**  Let n ≥ 3.
1. *Odd n, restriction (v(n) ∉ V).*  G(n) = G(n − 1) + n, every L admissible for G(n) is admissible for G(n − 1),
   and δ_PB(n) = Q\*(n − 1) − Q\*(n) ≥ 0.
2. *Odd n, exchange (v(n) ∈ V).*  Theorem A.
3. *Even n, s = n/2.*  G(n) = G(n − 1) − s + n when s ∈ G(n − 1) (relaxation), and G(n − 1) + n when s ∉ G(n − 1)
   (half-out, A3).  In a relaxation s joins the numbers up to n/2, with e_s at the parity of its layer in place of its
   extra coordinate, every L admissible for G(n − 1) is admissible for G(n) (v(n) has a one at s that no other vector
   has), and δ_PB(n) = s − (Q\*(n) − Q\*(n − 1)) ∈ [0, s].

*Proof.*  Part 1 is part 1 of Theorem A with the span argument: adding n to the fixed part can only shrink the
admissible family.  Part 3: n is kept first; an old source y ≠ s is decided as on board n − 1, since v(n) has a one
at the coordinate s that no old source's vector has, so v(n) ∉ span of any set of old vectors and the argument of
Theorem A, part 1, applies; s is no source of board n.  The rest is the definitions.  ∎

This is S 2.2's table with Prom replaced by the parity-feasible family ℒ and P\* by Q\*.  Given U at n and (♦) at n,
opt(n) = ΣU\*(n) + P\*(n) (X8) and PB(n) = ΣU\*(n) + Q\*(n), so

    gap(n) = Q\*(n) − P\*(n),

and rise(n) = [Q\*(n) − Q\*(n − 1)] − [P\*(n) − P\*(n − 1)]: at a restriction, the parity relaxation's fall less the
game's; at a relaxation, the parity relaxation's gain less the game's.  The whole gap is the promotion problem's.

### 3.3 Two one-line lemmas that say what a proof of the parity form needs

Let n be a relaxation or restriction, T′ an optimal set of n − 1 and S\* an optimal set of n with S\* = T′ − D + A + n.

**Lemma C (the transfer lemma; proved).**  If some heaviest set I of board n − 1 independent at both parities has
D ⊆ I, A ∩ I = ∅, and I − D + A + n independent at both parities on board n, then rise(n) ≥ 0.  *Proof.*  PB(n) ≥
Σ(I − D + A + n) = PB(n − 1) + n − δ(n), so δ_PB(n) ≤ δ(n).  ∎

**Lemma D (the game lemma; proved).**  If some heaviest set I of board n − 1 and a heaviest set J of board n with
n ∈ J have J = I − D_Q + A_Q + n, and T′ − D_Q + A_Q + n is playable on board n, then rise(n) ≤ 0; a game of n
scoring opt(n − 1) + PB(n) − PB(n − 1) proves the same.  *Proof.*  opt(n) ≥ ΣT′ − ΣD_Q + ΣA_Q + n = opt(n − 1) +
PB(n) − PB(n − 1).  ∎

So rise ≤ 0 is always certified by a game, and the proof direction is rise ≥ 0: that the game's change (D, A) can be
applied to a parity-optimal set.  In a window clean to the cascade's depth the measured (D, A) lies in the window's
cells; what Lemma C then needs is that a parity-optimal set of n − 1 agrees with the game's on the window and that the
cascade's independence on board n is decided inside the window plus the hubs.  Section 4.4 says where that fails.

### 3.4 What this settles about the gap, before any conjecture

Combining A1 to A3 with Proposition B: **the gap of the chain changes only at relaxations and restrictions**, and at
an exchange only where the exchange law fails, which the chain never shows (B 4.5's 264 searched exchanges, and here
all 103 exchange rows).  This is the proved part of B 4.5's judgment and of Section 7.

