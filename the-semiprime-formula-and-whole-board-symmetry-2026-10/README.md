# The semiprime formula and whole-board symmetry (2026-10)

Part of the [lab notebook](../README.md).

Started 2026-10-31.  Concluded 2026-10-31.

**Question.**  The frame solver ends some games by [a repeat
(R6)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/search-rules.md#the-repeat-lemma) and prunes its
search by [exchanging primes
(R2)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/search-rules.md#the-prime-exchange-theorem).  Both are
stated in the frame model, and R6 needs [statement
U](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/exactness.md#statement-u).  Can the prover, which works on
the whole board, settle games or prune its search by whole-board versions of the two?  **Answer.**  The repeat rule
pays, and one case of it is all of the cost.  All 176 games of 1301-2175 that the frame solver settled as repeats
and the prover had to search are odd numbers with two prime factors, and for these opt(n) = opt(n − 1) + n − x is a
theorem that needs no statement U: [the semiprime formula
(J3)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/arrival.md#the-semiprime-formula).  It removes those
176 searches, 84.0 of the 226.0 thread-hours and 115.1 of the 309.2 million nodes of the run of 1301-2175, and settles
568 of the 1,589 games of 2176-5060 that are neither prime nor at their ceiling.  The prover proves them with it from
commit 2896cdd on.  The prime exchanges hold on the whole board too, but would cut at most 0.1 to 0.2% of the nodes at
the open units of 1302 and 0.0% at 1328, where the frame solver's rule leaves 0.75 to 0.88 of its nodes: not built.

## Method

The terms are those of the [glossary](https://github.com/bvchess/taxman/blob/2896cdd/docs/GLOSSARY.md).

* **The data**, as of commit 2896cdd: the committed chain `results/optimal.jsonl.gz` (to 5060); the prover's result
  lines for 2..1300 and for 1301-2175 (`solver/noframe/data/exact_parity_2_1300.jsonl` and
  `exact_parity_1301_2175.jsonl`, the latter the cloud run of [the proofs of
  1301-2175](../the-model-free-proofs-of-1301-2175-cost-and-the-cloud-run-2026-10/README.md)); and the prover's
  enumeration of every optimal set of the games to 989 (`solver/noframe/data/optsets_2_989.jsonl`).
* **An independent check.**  `tx.py` tests playability by dismantling ([the core theorem
  (P7)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/playability.md#the-core-theorem)), runs descending
  greedy for U\*, and lists every optimal set of a small board with an exhaustive branch and bound.  It shares no code
  with the prover or the frame solver, and the checks below that test playability use it.
* **Two programs in Rust**, `symroot.rs` and `symsample.rs`: research examples built in a worktree of the prover and not
  committed.  `symsample.rs` runs `exact`'s search for a number of seconds, from the roles that [the bottom-layers
  theorem (F4)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/frame-model.md#the-bottom-layers-theorem)
  gives every optimal set for layers 1 and 2, and pauses.  It tests each open unit, a subtree the search has still to
  explore, with the prime-exchange inequalities of section 2 below (a *hopeless* test, and the parity bound with a
  Lagrangian on the inequalities), then searches each unit to the end to count the nodes a cut there would save.  The
  share it prints is the nodes the rule cuts over the nodes of the first stretch and of the units.  It is a lower bound
  on what the rule saves, since it sees only the units open at one moment and not the nodes inside the others.

## Results

### 1. Repeats: the semiprime formula (J3)

**The repeats that cost the prover.**  The frame solver settled 369 games of 1301-2175 as repeats (`repeats.py`):

| the repeats of 1301-2175 | games | what the prover did |
|---|---|---|
| even, at their ceiling | 193 | no search: the relation `chain` proves a game at its ceiling |
| odd, two prime factors, repeating n − 1, below the ceiling | 176 | searched every one: 84.0 thread-hours, 115,121,302 nodes |

No odd repeat with three or more prime factors occurs before 2176.  From 2176 to 5060 the committed chain has 495 odd
repeats with two prime factors and 6 with three, among the 1,589 games that are neither prime nor at their ceiling
(`t5.py`).

**The formula** (proven on the whole board).  Let n be odd with two prime factors, counted with multiplicity, such as 15
or 25.  Let G_n be the graph whose vertices are the primes up to n/2 and one more vertex g, and whose edges are the
numbers of layer 2 up to n, pq the edge p–q and p² the edge p–g.  Suppose that n closes a cycle in G_n with
U\*_2(n − 1), the numbers of layer 2 in U\*(n − 1), and let x be the smallest member of that cycle other than n.  Then:

1. U\*_2(n) = U\*_2(n − 1) − x + n;
2. opt(n) = opt(n − 1) + n − x;
3. S ↦ (S ∖ {n}) ∪ {x} maps the optimal sets of game n one to one onto those of game n − 1.

The hypothesis holds for every odd n ≥ 189 with two prime factors.  The theorem and its proof are in the theory (commit
45b542b), under [the semiprime
formula](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/arrival.md#the-semiprime-formula) of arrival.md.
It rests on [the bottom-layers theorem
(F4)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/frame-model.md#the-bottom-layers-theorem), [the layer
theorem (F3)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/frame-model.md#the-layer-theorem), [the
two-factor
proposition (P11)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/playability.md#the-two-factor-proposition)
and part (b) of [the greedy
algorithm](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/primer/greedy.md#the-greedy-algorithm), with no
statement U, no conjecture and no frame model.  The idea of the proof:

* F4 says every optimal set S of game n plays the largest prime q(n) and no other, has exactly U\*_2(n) among its
  sources of layer 2, and holds a forest of layer 2 in G_n.
* For odd n the boards n − 1 and n have the same numbers up to n/2, so S and S − n + x have the same layer instance at
  every layer but 2: n and x are sources of layer 2 and members of no pool.
* In layer 2 the swap keeps a forest, because the only path of S_2 between the ends of x goes through n.  By F3,
  S − n + x is playable in game n − 1.  The converse swap does the same for an optimal set of n − 1.
* Part 1 is the scan of descending greedy in layer 2: the forest exchange of the heaviest basis when the heaviest
  element is added.

The formula asks neither that the frames of layer 2 be closed in games n − 1 and n, nor that game n be a repeat.  It
holds at the 8 games to 989 where layer 2 has a freedom: 49, 51, 111, 119, 141, 143, 183 and 185 (49 and 143 are
repeats, the other six are not).  It is the sharp form, at odd numbers with two prime factors, of a cut the prover
already has for the game before (`with_smaller_games`, off in the committed runs): every set that beats V(n) holds n,
since opt(n − 1) = V(n − 1) ≤ V(n).

**Where the hypothesis fails.**  Without a cycle there is no x.  13 odd numbers with two prime factors close no cycle,
all at most 187 (9, 15, 21, 25, 33, 35, 55, 77, 85, 115, 121, 145 and 187, `t6.py`).  Game 21 = 3·7 closes no cycle with
U\*_2(20) = {14, 15} and falls one short of its ceiling; game 33 closes none and is at its ceiling.  For an even n = 2p
the prime p is a new vertex and n its only edge, so n never closes a cycle; the game is at its ceiling by [the half
lemma](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/neighbors.md#the-half-lemma), since an optimal game
of n − 1 plays no prime but q(n − 1) > p.

**The checks.**

* *Exhaustive search* (`t1.py`, `t2.py`, `ex.py`).  `tx.py`'s branch and bound agrees with OEIS A019312 for n = 2..40.
  Game 39 is the one game to 40 with a cycle and an x (x = 22), and its unique optimal set is that of game 38 with 22
  exchanged for 39.  The exhaustive solver of `heuristics/evaluation/certify.py` (pot states, no theory) confirms
  20, 21, 32, 33, 38 and 39 and the optimal sets of 38 and 39 (`cert_ex.py`), and the optimal sets of 48 to 51
  (`cert_48_51.txt`; 94.5 s for 51).  The unique optimal set of 49 is that of 48 with 25 exchanged for 49, and that of
  51 is that of 50 with 26 exchanged for 51: on both boards layer 2 has a freedom, and 51 is no repeat.
* *Every optimal set to 989* (`t3.py`, `t9.py`).  Of the 189 odd numbers to 989 with two prime factors that close a
  cycle, 182 have every optimal set enumerated, 191 sets in all (183 in games where layer 2 is closed, 8 in games where
  it has a freedom).  For each of the 191, S − n + x is playable in game n − 1.  In the 181 pairs where games n − 1 and
  n are both enumerated, every optimal set of n holds n and not x, every one of n − 1 holds x, and the exchange maps the
  sets of n exactly onto those of n − 1: no exception.
* *The scores* (`t8.py`).  The formula holds at all 427 odd numbers with two prime factors and a cycle in 2..2175,
  whose scores the prover proves, and at all 568 in 2176..5060 of the committed chain.
* *Random sets* (`t7.py`, `t7m.py`).  804 random playable sets on boards to 400, with the right largest prime and
  U\*_2, random small numbers of layer 2 and random numbers of layers 3 and up: each swap S − n + x, and T − x + n on
  the board n − 1, is playable, with 0 failures.  The mutation check swaps n for a source of layer 2 off the cycle, and
  the check sees it as unplayable on 36 of 40 boards (the other 4 cross the same cut).
* *Part 1* is asserted in `t6.py` for every odd number to 400 with two prime factors and a cycle.

**In the prover.**  Commit 2896cdd adds the relation `semiprime` beside `chain` and `prime` (`src/semiprime.rs`):
`exact` proves such a game from game n − 1 with no search, when V(n) = V(n − 1) + n − x.  Its classification of the 875
games of 1301-2175, in the prover's [proofs
guide](https://github.com/bvchess/taxman/blob/2896cdd/solver/noframe/docs/proofs.md), is `chain` 270, `prime` 115,
`semiprime` 176 and `none` 314.  The cloud run was made before the formula and searched
490 games, the 314 and the 176.

**What it saves.**

| range | games | saved |
|---|---|---|
| 1301-2175 | 176 searches | 84.0 of the run's 226.0 thread-hours (37.2%), 115.1 of its 309.2 million nodes |
| 2176-5060 | 568 of the 1,589 games that are neither prime nor at their ceiling (36%) | their searches, once game n − 1 is proven |

### 2. Symmetry: the prime exchanges on the whole board

**The same-floor form** (proven here; it is not in the theory).  Let p < q be primes with p² > n and ⌊n/p⌋ = ⌊n/q⌋.
Let π exchange p and q in every number.  Then π maps {1, …, n} onto itself and playable sets to playable sets, and
every optimal set S of game n has c_p(S) ≤ c_q(S), where c_r(S) is the sum of x/r over the members x of S divisible
by r.

*Proof.*  Since q > p > √n, no number up to n is divisible by p², q² or pq, so every x ≤ n is pt, qt or t, with t prime
to pq.  Now pt ≤ n iff t ≤ ⌊n/p⌋ = ⌊n/q⌋ iff qt ≤ n, so π permutes the board.  π is multiplicative and permutes the
primes, so it maps the maximal factors of x onto those of π(x) and keeps divisibility.  It maps the own instance of S,
its payment schemes and their precedences, onto those of π(S), so S is playable iff π(S) is, a set being playable iff
its own instance is.  The weights differ by Σπ(S) − ΣS = (q − p)(c_p(S) − c_q(S)), and an optimal S has Σπ(S) ≤ ΣS.  ∎

More generally, for any p < q with p² > n, an optimal set with no member pt for t > ⌊n/q⌋ keeps c_p ≤ c_q, since π(S)
stays on the board: a disjunctive constraint, for the nodes that bar those members.  Letting F4 rule out the
obstructions (all of them numbers of layer 2 outside U\*_2) added no pair at 1300 or 2000 (`sym.py`).

**The form relative to F4's roles** (proven here).  Let p < q be primes with p² > n, on a board whose frames of layer 2
are closed (every n ≥ 187), such that (i) ⌊n/(2p)⌋ = ⌊n/(2q)⌋ and (ii) every t with ⌊n/q⌋ < t ≤ ⌊n/p⌋ is a prime.
Then every optimal set S has c_p(S_{≥3}) ≤ c_q(S_{≥3}), the cofactor sums over its members of layers 3 and up.

*Proof.*  By F4, S = {q(n)} ∪ U\*_2 ∪ X with X = S_{≥3}.  By (i), π maps the numbers up to n/2 onto themselves.  By
(ii), it maps the numbers of layers 3 and up onto themselves: such a number pt has t composite, so t ≤ ⌊n/q⌋ and
qt ≤ n.  Let S′ = {q(n)} ∪ U\*_2 ∪ π(X).  Its layer instances at 1 and 2 are S's, the same members and, at 2, the
pool of all primes up to n/2.  At a layer k ≥ 3 the members are π(X_k) and the pool is the numbers of layer k − 1 up
to n/2 outside S′, which is π of S's pool (at k = 3, all numbers of layer 2 up to n/2, which π maps onto themselves).
π keeps divisibility and maps maximal factors to maximal factors, so it maps each layer instance of S onto that of S′,
schemes and precedences with it, and S′ is playable (F3).  Then ΣS′ − ΣS = (q − p)(c_p(X) − c_q(X)).  ∎

**Use in the search**, as R2 is used in the frame model: cut a node whose forced picks have c_p above c_q(forced) plus
c_q(free) for a pair; bar a free x divisible by p when c_p(forced) + x/p exceeds c_q(forced) + c_q(free); or add a
Lagrangian μ(c_q − c_p) to the weights of the parity bound.  All three are sound beside F4's roles, since both hold for
every optimal set: if opt(n) > V, every optimal set obeys the roles and every pair's inequality, so it survives every
cut.

**Checks** (`t10.py`).  On every optimal set the prover enumerates, for every 7th game of 187..989, the image under
every pair is on the board and playable (the independent check) and the inequality holds: 24,916 (set, pair) checks of
the same-floor form and 47,628 of the form relative to F4, with no exception.

**How much it touches.**

* *The classes are few and small.*  At 1300 the whole-board classes of primes in (√n, n/4] are {101, 103, 107},
  {109, 113}, {131, 137, 139}, {149, 151, 157}, {163, …, 181}, {191, …, 211}, {223, …, 257} and {263, …, 317}, against
  the frame solver's {41, 43}, {59, 61}, {67, 71}, {73, 79}, {89, …, 107}, {109, …, 139} and {149, 151, 157}: the frame
  model sees only some multiples, so its classes are larger.  With F4's roles every multiple of a prime above n/4 lies
  in layers 1 and 2 and is fixed, so only the primes in (√n, n/4] matter.  The same-floor pairs move 88 of the 706
  numbers of layers 3 and up at 1300 and 208 of 1119 at 2000 (`sym.py`); the form relative to F4 moves 175 against 88
  at 1300, 151 against 136 at 1328 and 244 against 208 at 2000 (`sym2.py`).
* *The root breaks nothing.*  The parity bound's heaviest set at the roles of F4 breaks no inequality at 1300 (32 pairs,
  gap 151) or at 1475 (39 pairs, gap 590), so a Lagrangian on the inequalities lowers the root bound by 0
  (`symroot.rs`).
* *The open units of a paused search* (`symsample.rs`), from F4's roles:

| game | form | paused | open units | nodes in them | the rule cuts |
|---|---|---|---|---|---|
| 1302 | same-floor | 10 s, 2,048 nodes | 73 | 11,982 | 2 units, 13 nodes (0.1%) |
| 1302 | relative to F4 | 10 s, 2,048 nodes | 73 | 11,982 | 3 units, 22 nodes (0.2%) |
| 1328 | same-floor | 120 s, 27,904 nodes | 79 | 133,988 | 1 unit of 1 node (0.0%) |
| 1328 | relative to F4 | 120 s, 28,928 nodes | 67 | 133,159 | 1 unit of 1 node (0.0%) |

The frame solver's rule left 0.88 of the nodes in the solver and 0.86 in the GF(2) branch and bound when it was
measured ([dominance and symmetry](../search/dominance-and-symmetry-2026-10/README.md)), and about 0.75 in production
([prime exchanges in the search](../search/prime-exchanges-in-the-search-2026-10/README.md)).  The whole board gives
much less: the classes are smaller, and those that matter for the prover involve only the numbers of layers 3 and up
that are multiples of primes in (√n, n/4].

### 3. What stays open

* **A general whole-board R6**, opt(n) ≤ opt(m) + ΣU\*(n) − ΣU\*(m) for a game m whose problem n repeats.  Not proven:
  the proof of R6 needs statement U at n.  The prover does not need it for its cost, since every repeat that costs is an
  odd number with two prime factors.
* **A layer-3 version of J3 with the barred bound** (not written up).  For an odd n with three or more prime factors
  that is a repeat by [the arrival lemma
  (J1)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/arrival.md#the-arrival-lemma), where n joins only a
  closed frame M, closed without n: if the barred bound at V(n) certifies every member of U\* in M, then every set that
  beats V(n) and obeys F4 plays U\* ∩ M, holds no other number of M, and the exchange S − n + x (x the source that U\*
  gives up) is playable in game n − 1 by F3 and [the joining lemma
  (F2)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/frame-model.md#the-joining-lemma).  So V(n) =
  V(n − 1) + n − x would be proven.  Only 6 games to 5060 would be settled, none before 2176.
* **No such exchange at an even n or at layer 3 without the barred bound.**  At an even n the swap from game n to game
  n − 1 loses n/2 to the factors and gives a bound above the ceiling.  At an odd n with three prime factors F4 does not
  fix layer 3, and the exchange needs statement U at n.

## Decision

* **Kept: the semiprime formula (J3).**  It is proven in the theory (commit 45b542b) and built into the prover as the
  relation `semiprime` (commit 2896cdd); the checks above are its evidence.
* **Measured, not built: the whole-board prime exchanges.**  The theorems are proven and the checks pass, but the rule
  would cut at most 0.2% of the nodes at the units sampled, against the frame solver's 0.75 to 0.88 of its nodes.  It is
  not in the theory or the prover.  It would reopen if a change to the search put more of the tree on numbers of layers
  3 and up that are multiples of primes in (√n, n/4], the only numbers it moves.
* **Open:** the general whole-board R6, and the layer-3 form of J3 (6 games to 5060).

## Files

The scripts need the standard library of Python 3 only.  Those that read the repository read a checkout of the main
repository at commit 2896cdd: the folder named by the environment variable `TAXMAN_REPO`, or the current folder.  Run
them as `python3 THIS_FOLDER/SCRIPT ARGUMENTS`, from the top of that checkout.  Each `*_output.txt` is the script's
output, made on 2026-10-31 with the data of 2896cdd.

* `tx.py`: the independent tools (playability, descending greedy, the exhaustive search), imported by the others.
* `data.py`: reads the committed chain, the prover's result lines, and the enumerated optimal sets, rebuilt from the
  recorded game and the listed differences.
* `repeats.py`: the table of repeats of 1301-2175 and the prover's cost on them (`repeats_output.txt`).
* `t5.py`: the repeats and the searched games of 2176-5060 (`t5_output.txt`).
* `t1.py`: the exhaustive search against OEIS A019312, n = 2..40 (`t1_output.txt`).
* `t2.py 40`: the semiprime step by brute force on the boards to 40 (`t2_output.txt`).
* `ex.py`: the sets and the cycles at 21, 33, 39, 49, 51, 111 and 119, and the exchange at 38 and 39 (`ex_output.txt`).
* `cert_ex.py 48 49 50 51`: the exhaustive solver of `heuristics/evaluation/certify.py` on the games named, with every
  optimal set; `cert_48_51.txt` is its output (the first run, on 20, 21, 32, 33, 38 and 39, was not saved).
* `t6.py`: the cycle and x of every odd number to 400 with two prime factors, part 1 asserted, and the games where the
  hypothesis fails or layer 2 is open (`t6_output.txt`).  `t7.py` and `t7m.py` import its functions.
* `t3.py 989`: the bound against the proven scores, and the exchange on every enumerated optimal set (`t3_output.txt`).
* `t9.py`: part 3, the one-to-one map between the enumerated sets of n and n − 1 (`t9_output.txt`).
* `t8.py`: the formula against the scores of 2..5060 and the thread-hours of the 176 (`t8_output.txt`).  `t9.py`
  imports its functions.
* `t7.py 400` and `t7m.py`: the random sets and the mutation check (`t7_output.txt`, `t7m_output.txt`).
* `sym.py 1300 2000` and `sym2.py 1300 1328 2000`: the classes of the two prime exchanges and the numbers they move
  (`sym_output.txt`, `sym2_output.txt`).
* `t10.py`: both prime exchanges on every enumerated optimal set (`t10_output.txt`; it takes under 10 minutes).  It
  imports `pairs` from `sym2.py`.
* `symroot.rs` and `symsample.rs`: the Rust measurements.  Copy them into `solver/noframe/examples/` of the prover at
  2896cdd; the module comment of each says how to run it.  `symroot.rs` prints a line a game, whose output was not
  kept.  `symsample_1328.json` is `symsample.rs` on 1328 at 120 s, and `symsample_f4.json` its two lines with `f4` on
  1302 at 10 s and 1328 at 120 s.  The line of the same-floor form on 1302 was not kept.

## Commits

* 45b542b (2026-10-31): the semiprime formula (J3) in docs/theory/arrival.md.
* 2896cdd (2026-10-31): the relation `semiprime` in the prover.
