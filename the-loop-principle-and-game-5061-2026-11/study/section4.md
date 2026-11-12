
## 4. The clean-window statement

### 4.1 The data by depth (measured; `study/depth_check_out.txt`, `study/coverage_out.txt`)

Relaxations and restrictions from 187 on, rise = 0 / games, by the depth to which the window is clean:

| range | depth 0 | 1 | 2 | 3 | 4 | 5 or more | depth ≥ 2 | depth ≥ 3 |
|---|---|---|---|---|---|---|---|---|
| chain 187..5060 | 350/1281 | 107/156 (27 above, 22 below) | 55/56 | 30/30 | 29/29 | 67/67 | 181/182 (9.9% of the CPU) | 126/126 (6.1%) |
| best-known 5061..10000 | 349/1077 | 75/124 | 67/88 (10 above, 11 below) | 44/48 | 29/29 | 161/161 | 301/326 | 234/238 |

Beyond the families 8P and 12P, which L2 and L4 settle, depth ≥ 2 holds 43 chain games (42 with rise 0; 5.1% of the
CPU: 16P 24, 20P 7, 21P 6, 18P 2, 24P 2, 25P 2) and 174 past 5060 (149 with rise 0), depth ≥ 3 holds 14 chain games
(all rise 0, 1.3%) and 86 past 5060 (82 with rise 0).  The dearest clean games beyond 8P and 12P are 4975 = 25·199
(142 CPU-hours), 4976 = 16·311 (141), 4432 = 16·277 (75), 4925 = 25·197 (41) and 4893 = 21·233 (29), all at rise 0.

The exceptions past 5060 at depth ≥ 3 are 5943 and 6657 (21P, rise +496 and +764), 9510 (30P, +20) and 9140 (20P,
−1).  A rise above 0 can come only from a short best-known at n, a rise below 0 only from a short best-known at n − 1
(δ = bk(n − 1) + n − bk(n)), so 5943, 6657 and 9510 say "n is short" and 9140 "9139 is short by 1", unless the
conjecture fails there; the coordinator's flag list holds 5943, 6657, 9510 and 9139.  The 21P family's other games
from 4683 on lose exactly P (B 4.5), which is what the parity form predicts for these two.

At depth 2 the chain's single exception is 2512 (Section 4.2).  Past 5060, depth 2 adds 21 exceptions, 16 of them in
the cofactors 30, 32 and 36 (30P: 8 of 9 games, 32P: 6 of 6, 36P: 2 of 2, rises from −144 to +60), which have no
game of the chain clean to depth 2 at all; the others are 20P (3 of 36) and 21P (5 of 31).  Their ladders are longer
(mf(32P) = {16P, 32} with the hubs 32, 16, 8, …; mf(36P) = {18P, 12P, 36}; mf(30P) = {15P, 10P, 6P, 30}), so depth
2 is below their cascades' depth, and the negative rises at 32P and 36P are either short predecessors (all six 32P
predecessors are in the flag list) or genuine falls of the gap below the cascade's depth.  That is the one test of
the inequality the plays will give: a play that raises bk(n − 1) by exactly −rise confirms the prediction; a play
that finds nothing is evidence, not proof, that depth 2 is too shallow for 32P and 36P.

### 4.2 The exception 2512 = 16·157

P₁, P₂, P₃ = 151, 149, 139.  The window is clean to depth 2 and not 3: column 3 holds the rows 17 and 18 (17·139 =
2363, 18·139 = 2502 ≤ 2512).  The ladder of game 2511 is the family's (hub 16 at (16, 1), 6 at (6, 2), 4 at (4, 3),
`study/hubs_out.txt`), the recorded change is the family's pattern, δ = 8P₁ + 6P₂ + 4P₃ − 6P₁ − 4P₂ = 1156, and the
16P law holds.  δ_PB = 1058.  So on board 2512 some set independent at both parities makes room for 2512 for 98 less
than any game does: the parity bound's augmenting path from n ends elsewhere than the game's, through a configuration
of column 3 that the clean picture lacks (its rows 17 and 18 put 9P₃ = 1251 below n/2 as a candidate of layer 3 and
18P₃ = 2502 on the board as a source of layer 4 listing 9P₃, 6P₃ and 18), and that configuration is independent at
both parities but not playable: an odd core, created by n's arrival, worth 98.  Experiment E5 shows it exactly.

What 2512 means for the statements: the inequality gap(n) ≥ gap(n − 1) holds there (the gap rose by 98); the equality
fails; the hypothesis "clean to depth 2" is not the cascade's depth for 16P, and the right hypothesis is "clean to
the ladder's depth", 3 for 16P.  A rule built on the inequality does not settle 2512 (no game of 2512 reaches
opt(2511) + PB(2512) − PB(2511)) and claims nothing false; the family law, once proved, settles it.  Where the
window is unclean at the ladder's last rung the law is the sharper tool, and where it is clean the two agree.

### 4.3 Which statement is right

* **The equality rise = 0, under "clean to the ladder's depth", is the statement the mechanism predicts** (Section 2,
  P1): the two models take the same augmenting path.  Measured: no proven exception; among best-known games only the
  four flagged ones at depth ≥ 3.  Its weakness is the hypothesis: the ladder's depth depends on the cofactor (1 for
  8, 12 and 40; 2 for 20 and 24; 3 for 16; more for 30, 32, 36), so a rule needs a table d(c), proved cofactor by
  cofactor.  "Depth 3" is a uniform hypothesis that fits every cofactor the chain shows clean (8 to 25).
* **The inequality gap(n) ≥ gap(n − 1) is the statement to use**: with it, a game of n scoring opt(n − 1) + PB(n) −
  PB(n − 1) is optimal, a check of seconds.  It is not a separate principle with a proof of its own: the gap rises when
  n's arrival creates an odd core (2512) and falls when it dissolves one (the 20 ceiling games of the chain where it
  falls, all relaxations or restrictions at depth 0 or 1), and both come from configurations outside the clean
  window.  So it should carry the same hypothesis as the equality; at depth 2 it has no proven counterexample, and the
  32P and 36P plays are its test.
* **Something else.**  The brief's "if the gap cannot fall then opt(n) ≤ opt(n − 1) + PB(n) − PB(n − 1)" is one
  statement read twice: gap(n) ≥ gap(n − 1) *is* opt(n) ≤ opt(n − 1) + PB(n) − PB(n − 1).  The content is in proving
  the inequality under cleanliness, and that is as hard as proving the equality.

**The rule, as of now (unproven, for the claim past 5060).**  For a relaxation or restriction n with window clean to
depth 3 and n − 1 proven: if bk(n) = bk(n − 1) + PB(n) − PB(n − 1), then n is optimal under the conjecture P2; if
bk(n) is below that, play n (its target is known to the point); if above, play n − 1.  It covers 238 games past
5060, 234 at the target now, of which 86 are beyond 8P and 12P.  At depth 2 it covers 326, 301 at the target.  Until
P2 is proved these games are "optimal if n − 1 is, given P2", a consistency check and a flag, not a proof.

### 4.4 What a proof needs, and where the known technique stops

Lemma C reduces rise ≥ 0 to applying the game's change (D, A) to a parity-optimal set I of n − 1.  In a clean window
the sources of the window agree in both models (I ∩ sources = G(n − 1) = U\*(n − 1) given (♦); the game's optimal set
holds U\*(n − 1) given U), so the ladder's sources (16P₁, 12P_j, 10P_j, …) are common; what may differ are the
promotions, the cells up to n/2 (8P₁, 6P_j, 4P_j), and these are the rungs.  In the parity bound a column's hub use
is a *hub combination*: in a clean column the four layer-3 sources span e_{2P_j} + e_9 + e_10 + e_15 and e_{3P_j} +
e_9, so 4P_j joins the set iff e_4 + e_9 + e_10 + e_15 is not already in the span, and 6P_j iff e_6 + e_10 + e_15 is
not; clean columns offer the same two combinations, so across them at most one 4P_j and one 6P_j can be in I, which
is the game's "hub 4 pays once, hub 6 pays once".  So in clean columns the parity bound's ladder is the game's, and the
greedy assignment (the heaviest cell that needs a hub gets it) is forced in both.  A proof of P1 for a cofactor is
then the family's proof (Section 5.2) written twice, once with schemes and once with spans, and the two are the same
case analysis; the parity form has no proof cheaper than the family laws, only a wider reach (any cofactor whose
ladder stands in clean columns, with one computation instead of one theorem each).

What stops a general proof is the coupling through the far hubs: a window cell like 8P₁ lists the hub 8, held far
away (by 8·q(n/8)), in both models; a cascade that reaches a far hub leaves the window, and cleanliness says nothing
about where it lands.  In the measured clean games it never does (the far hubs never move, Section 5.1), and a lemma
that says why ("a far hub's holder is never displaced by a window cell, since the holder is heavier and has no
alternative that the window could use") would be the general piece: with it and the "no odd core in the window
instance" check of Section 5.3, P1 would follow for every cofactor by one argument.  Not proved here.
