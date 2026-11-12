# Referee report: the gluing lemma

Read: lemma.md; playability.md (P2, P7); frame-model.md (F3, F4, F10); N1.  Not read: e12/ and the study report.
Scripts and logs are in this folder; all ran single-threaded at idle priority.

## Verdicts

* **Original form (clean window, S optimal): correct**, with two repairs to the wording.  (a) n must be a cell, that
  is c composite: the model presumes it ("(c, 0) = n"), and for prime c, n is in U\*₂ ⊆ S and so in O, and O ∪ W′
  is not a set of board n − 1.  (b) Step 3, second bullet: in a one-column window with c ≥ 2P (P = 7, n = 196, say)
  a row k can be a multiple of P; then the hub k of the cell kP is also one of its column factors, (k/P)·P, and it is
  the first bullet, not a member of K − X, that covers it.  The three facts as stated still hold there (computed).
* **Generalized form (2P_j² > n, S only playable): wrong as written; correct with three stated repairs** (gaps G1 to
  G3 below).  With them it needs S only playable, except for its δ clause.

## The three facts

Under 2P_j² > n they are proved, without F4 or F10.  Let x = kP_j ≤ n be a cell (k composite).  If a region prime
P_i divided k, then x ≥ 2P_iP_j ≥ 2·min(P_i, P_j)² > n.  So each cell has one column and one row, P_j divides it
once, and no hub is a multiple of a region prime: a hub is neither a cell nor a column factor.  mf(x) is the hub k
and the column factors (k/q)P_j (fact 2).  If y ≤ n has as a maximal factor a multiple mP_j with m ≥ 2 (a column
factor or a cell), then y = (pm)P_j with pm composite, a cell of column j (facts 1 and 3).  A cell with a hub h as a
maximal factor lies in row h.  A prime row's column factor is in layer 2 and at most n/2.

A clean window of two or more primes has c < P − 1, which gives 2P_j² > n; a one-column window {P} has it iff
c < 2P.  So the clean form is a case of the generalized one, except one-column windows with c ≥ 2P (repair (b)).

F4 and F10 (with N1 inside F4) enter only once: an optimal S plays no number of layer 2 up to n/2, so a prime row's
column factor is never in S or in O ∪ W′.  Nothing else needs optimality but the δ clause.

## The steps

All four steps are valid under 2P_j² > n.  Step 1: a member of O has no cell as a maximal factor (fact 3), and n is
a maximal factor of nothing.  Step 2: fact 1.  Step 3: the first bullet is column-closure; the second needs a hub to
be no cell (so h ∉ S ⇔ h ∉ O ∪ W′) and no column factor (so a second member of X listing h would be in row h); the
third needs fact 1 and that o lists f in S, so f ∉ S and the member of Y in row f lists it.  Step 4 is P7.

Hidden assumptions, as asked:
* *Hubs that are moves.*  Hubs are never cells, so a hub is in S iff in O iff in O ∪ W′; in O it is listed in
  neither instance.  rows and R1 may be counted by occupancy (the hypothesis is then free of O) or only at hubs outside
  O (a weaker hypothesis); the proof works with either.
* *n/2 on board n − 1.*  Harmless to the lemma: W′ may hold it, nothing lists it there, and no step distinguishes
  sources.  It concerns only which W′ an enumeration must use.
* *Composite rows.*  A composite row's column factor is a cell, and its multiples are cells of its column: fact 1
  holds.
* *O listing a cell.*  Impossible: a prime multiple of a cell is a cell, so in W, not O.
* *R2.*  Not needed: rows(Y) ⊇ rows(X) and R1(Y) ⊆ R1(X) imply R2(X) ⊆ R2(Y).

## Gaps of the generalized form

* **G1: column-closed must be read in the pool of O ∪ Z.**  With S only playable, O can hold a prime row's column
  factor qP_j.  Read literally ("every column factor outside Z"), step 2 fails: K ∩ W′ need not be column-closed.
  Counterexample: n = 200, R = {11, 13}, S = O = {22, 26} (playable), W = ∅, W′ = {44, 52}.  No X ⊆ W′ is closed
  literally (22 and 26 are each listed once), so the hypothesis holds vacuously; but 44 and 52 list only 4, and
  {44, 52} is a core.  Read in the pool, X = {44, 52} is closed and has no Y, as it should.  Repair: "outside Z and
  O", or assume S plays no qP_j (q prime, P_j ∈ R).  With the first, the hypothesis depends on O: an enumeration that
  ignores O misses the sets X that are closed only because O holds their column factors.
* **G2: n ∉ O.**  n = 191, R = {11}, S the committed optimal set (it holds 191), W′ = W =
  {88, 99, 110, 132, 154, 165, 176}: the hypothesis holds with Y = X, yet O ∪ W′ = S is not on board 190, and the
  conclusions fail: opt(190) = 11,637 < ΣS = 11,647, and δ(191) = 181 < 191.  Repair: n is a cell of R or n ∉ S.
* **G3: the δ clause needs ΣS = opt(n).**  S = W′ = ∅ gives δ(n) ≥ n, false at 191.  In general
  δ(n) ≥ ΣW′ − ΣW + n − (opt(n) − ΣS).

## What I computed

* `referee_facts.py` (log `referee_facts.log`): every check of the facts section, on every board 187 to 10,000.
  Region form, R = every prime with 2P² > n and 4P ≤ n (a sub-region only drops columns): 9,814 boards, no failure.
  Clean form, every n = cP with c ≥ 4 and the window of primes ≤ P: 21,674 windows.  The 15,974 that hold a prime
  with 2P_j² ≤ n are all one-column windows with c ≥ 2P.  There facts 1 to 3 as stated hold, but P² divides a cell,
  the hub is a column factor (in 15,158 of them also a cell), and another row's cell lists it: repair (b).  The other
  5,700 windows pass every check.
* `referee_brute.py` (log `referee_brute.log`): 300,000 random states per reading, on boards 196 to 440 with regions of
  one to four primes, four of them one-column windows with c ≥ 2P.  Pool reading, any playable S: the hypothesis held
  with a closed X in 20,501 states, 5,412 of them with W′ ⊄ W; no counterexample.  Literal reading, O free of layer 2
  up to n/2 (the original form): 12,541 and 3,328; no counterexample.  Literal reading, O free to hold the numbers
  qP_j: 47 counterexamples; the first, at n = 252, has 26 ∈ O, and {8, 52} is the core.  It also replays the G1
  and G2 examples.
* `referee_real.py` (log `referee_real.log`): the original form on the committed optimal sets.  Every clean window
  with c composite, c ≤ 24 and at most 10 cells, for n from 187 to 5,060 (257 windows), was run against every W′:
  45,949 sets W′ met the hypothesis, 1,138 of them non-trivially, and O ∪ W′ was playable every time.  It also asserts
  that no committed set plays a number of layer 2 up to n/2.
* `referee_numeric.py`: a search for a failure of the inequality opt(n − 1) ≥ ΣO + ΣW′ itself under the literal
  reading, with S = S\* + qP_j − s and one added cell, for n from 187 to 400.  It found none, but almost no states
  in that family qualified, so it tells us little.  G1 stands on the playability claim, which fails outright.
