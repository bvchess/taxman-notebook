# The audit of the best-known games past 5060

A best-known score is the score of a game that someone found, so it is a lower bound of opt(n) and no more.  Every known
relation between neighboring games turns two such scores into a statement: if the relation is a theorem, one of the two
games is certainly short; if it is a conjectured law, one of them is short if the law holds, and the row is a target for
the miner or a counterexample to the law.  `audit.py` checks every game from 5061 to 10000 against every relation that
applies to it, and lists where they disagree.

    cd /home/brian/taxman_work/lab/work/audit && nice -n 19 python3 -I audit.py        # about three minutes
    nice -n 19 python3 -I selftest.py        # optional, about three minutes: plants defects, checks each is found

| file | holds |
|---|---|
| `summary.txt` | per relation, the games it applies to, the games where the best-known score meets it with equality, the games it says are short; one line saying whether every best-known game agrees with every proved relation; the projections by window; the largest disagreements with the laws; the checks of the inputs |
| `disagreements.csv` | one row for each (game, relation) that disagrees: `n`, `relation`, `proved` (`yes`, `yes, given U`, `no`), `short_game` and `short_is` (`n`, `n-1`, or `n via projection from N=...`), `at_least` (how far short, at least), `known_score` and `must_reach` of the short game, `note` |
| `projections.jsonl` | each projection that beats a best-known score: the game, the source N, the score, the moves (replayed by the rules) |
| `constructions.jsonl` | each other game that the audit built from a recorded line (the relations N3, N6, S1, R6), replayed, that beats a best-known score |
| `targets.csv` | the mining targets: the games past 5060 that no proved relation settles from the game before ([below](#the-mining-targets)) |
| `consistency.csv` | where the miner's root problems or the dashboard's sums of U\* differ from J2, J3, the half law or the shadow law (these test inputs, not scores) |

The script reads `best-known.jsonl` once, at its start, up to the size the file has then (it is appended to while the
miner runs), and `summary.txt` records the time, the size and a hash of those bytes; a later run reads a later file.  Its other
inputs are the proven chain `results/optimal.jsonl.gz` (games 1..5060), `results/beyond-the-chain.jsonl` (5260 to 5264),
the dashboard's `gapdash/games.csv` (the sum of U\* and the parity bound of every game to 10000), and
`succession/past5060.csv` (to check the step kinds).  It imports `succession/common.py` for the loaders and the peel,
with bytecode writing off, and writes only here.

## How a score is read

Write A for the best-known score of n − 1 (opt(n − 1) where n − 1 is proven, which is 5060 and 5260 to 5264) and B for
the best-known score of n.  The audit replays every recorded line by the rules of the game before it uses it, so A ≤
opt(n − 1) and B ≤ opt(n).  A relation has one of three shapes, and each gives a different statement.

* **An equality** opt(n) = opt(n − 1) + n − c (N5, J3, and the laws).  If B − A < n − c then n is short by at least
  n − c − (B − A), since opt(n) = opt(n − 1) + n − c ≥ A + n − c > B.  If B − A > n − c then n − 1 is short by at least
  B − A − (n − c), since opt(n − 1) = opt(n) − n + c ≥ B − n + c > A.
* **An upper bound** opt(n) ≤ opt(n − 1) + n − c (N4, L2, L4, the parity inequality).  Only n − 1 can be short: when
  B − A > n − c, by at least the difference.
* **A lower bound**, a game of n built from a game of n − 1 or of N (N3, N6, N7, S1, R6, projections).  Only n can be
  short: when the built game scores more than B, by at least the difference.

## Reading a disagreement

* A row whose `proved` is `yes` proves that `short_game` is short by at least `at_least`: its best-known score is below
  opt, whatever statement U says.  Where the audit could build the better game it is in `constructions.jsonl` or
  `projections.jsonl`, replayed by the rules, and `must_reach` is the score it gives.  `yes, given U` is the same given
  statement U at the game the note names.
* A row whose `proved` is `no` is a conjectured law.  If the law holds, `short_game` is short by at least `at_least` and
  should reach `must_reach`; if the miner plays it and finds nothing, the row is a counterexample to the law at that game,
  which is the more useful finding.  `at_least` bounds the shortfall from below, and the true one can be larger.
* A relation constrains differences between neighbors, so a stretch of games that are all short by the same amount, or
  short in step with a law, passes every row.
* The laws overlap the proved relations (an exchange at a semiprime is J3, at a repeat R6), so a game can appear under
  several relations; `summary.txt` counts the games that are certainly short once.
* A *contradiction* (`summary.txt`) is a proven game, or a proved bound, against a best-known score: a bug in an input or
  a counterexample to U.  There are none unless it says so.

## The relations

"Proved" is as stated in `docs/theory/` and is used as stated, with its hypotheses checked per game.  The relations
that rest on statement U say so.  J3, L2, L4 and STRUCT's F10 rest on the finite part of the square theorem, which is a
computation (`docs/theory/evidence.md`).

| relation | what it says | where it is proved, or why it is believed | hypotheses checked per game | rests on U |
|---|---|---|---|---|
| **N3** | a game of n − 1 gives a game of n that scores more: n follows the last move, or goes just before the move m after which no proper divisor of n is left, with m left out if n takes m or takes all of m's tax | neighbors.md, "Monotonicity" (N3), step 3 | every recorded line of n − 1 (not only the highest) is extended this way on board n | no |
| **N4** | opt(n) ≤ opt(n − 1) + n | neighbors.md, "The ceiling lemma" (N4) | none | no |
| **N5** | n prime: opt(n) = opt(n − 1) + n − q(n − 1) | neighbors.md, "The prime formula" (N5), whole board | n prime | no |
| **N6** | if some optimal set of n − 1 stays playable with n added, opt(n) = opt(n − 1) + n | neighbors.md, "The step theorem" (N6) | a recorded line of n − 1, plus n, is playable (peel on the layer instance of n, which by the layer theorem F3 is the only one that changes); the line need not be optimal, so the audit reads the construction, not the theorem's "optimal set" | no |
| **N7a** | even n: if a game of n − 1 leaves n/2 out, n follows its last move | neighbors.md, "The half lemma" (N7) | a recorded line of n − 1 does not play n/2 | no |
| **N7b** | the same, with the hypothesis read on U\*: n/2 not in U\*(n − 1) (the sum of U\* rises by n) | the half lemma, and the half law's reading in arrival.md | n even, the step is half-out | **yes**, at n − 1 |
| **S1** | the line of n − 1 plus n, less its smallest move x that makes it playable, is a game of n: opt(n) ≥ A + n − x | succession/brief.md, 2.1 (the single-loss rule): a playable set is a game (P2) | x is found on the layer instance only, among the members of the residual and their maximal factors (`summary.txt` checks this against the whole-set peel) | no |
| **R6** | games with one root problem share P = score − ΣU\* of their best line: a game of one is a game of each other, made from the same promotions | search-rules.md, "The repeat lemma" (R6), part 1 | same setup digest (the solver's own comparison of root problems); each line plays all of U\* and promotions (its moves above n/2 add to the sum of U\*); where the transfer is short the audit builds it and replays it.  Part 2 (an upper bound given U) is not used: it can only bound a best-known score from above, and a proven member gives no more than part 1 does | no (part 1) |
| **J3** | n odd with two prime factors, n ≥ 189: opt(n) = opt(n − 1) + n − x, x the smallest other member of the cycle n closes with U\*₂(n − 1) | arrival.md, "The semiprime formula" (J3), whole board | x is found by the forest that descending greedy keeps among the layer-2 sources of n − 1, and checked against the sum of U\* (`consistency.csv`) | no |
| **J1, J2** | when the frame of n is closed, n poses the root problem of n − 1 (n − 2 across a prime) and U\* changes by n − x or n | arrival.md, J1 and J2 (J2: two prime factors, no conjecture) | J1's closed frames are **not recomputed**; its conclusion, equal root problems, is what R6 reads from the digests.  J2 is checked on the digests at every n ≥ 188 with two prime factors, and the half law at every half-out and relax game (`consistency.csv`) | no |
| **L2** | n = 8p ≥ 187, r the prime before p, 9r > n: opt(n) ≤ opt(n − 1) + n − 4r | below-the-ceiling.md, L2, whole board | all three | no |
| **L4** | n = 12p ≥ 187, 15r > n, some optimal set holds 8p, 8r, 12r and 8t for a prime t in (4p/3, 3p/2]: opt(n) ≤ opt(n − 1) + n − 6r | below-the-ceiling.md, L4 | 8p, 8r, 12r and some 8t lie in U\*(n) (descending greedy as a GF(2) basis on layer 4); where they do not, the game is skipped and counted | **yes**, at n |
| **PROJ** | the moves of a game of N that are at most n, in order, are a game of n | follows from the ceiling lemma N4 (a game of n without the move n is a game of n − 1) applied once for each number above n; `solver/docs/unsound/shortfalls.md` uses it as the miner's repair.  Each projection that beats a score is replayed here as well | none; every recorded line of every N ≤ 10000 is projected onto every smaller n | no |
| **PROVEN** | a proven line is a game, so a best-known score below it is short; one above it would contradict the proof | results/README.md | games 5260 to 5264 | only a contradiction does (the proofs past 2531 rest on U) |
| **W1** | opt(n) ≤ PB(n) | parity-bound.md, W1 | PB from games.csv | no |
| **STRUCT** | an optimal game is over (N2), opens with q(n) and plays no other prime (N1), and from 187 on plays no number of layer 2 up to n/2 (F10) | neighbors.md, N1 and N2; frame-model.md, F10 | the best line of n | no |
| **EXL** | at an exchange step (n odd, U\* gains n and loses a source x) δ(n) = x, the shadow of n | succession/brief.md, 3.8 and 7.1, and loops/study-report.md, 3.1: at an exchange δ_PB = x (Theorem A, proved), so the law says the gap does not change; measured at all 1,074 exchanges of 2..5060; proved in layer 2 (J3) and at repeats by R6 | x is read from the sum of U\*, and checked against the shadow | the law is open |
| **FAM8, FAM12** | δ(8P) = 4P₁, δ(12P) = 6P₁ (P₁ the prime before P) | L2 and L4 prove δ ≥ 4P₁ and ≥ 6P₁ (the upper bound above); the law is measured (loops/brief.md, 4.2) | the window is clean to depth 1: (c + 1)·P₁ > n | the law is open |
| **FAM16, FAM20, FAM24, FAM40** | δ(16P) = 8P₁ + 6P₂ + 4P₃ − 6P₁ − 4P₂; δ(20P) = 10P₁ + 6P₂ + 9P₂ − 6P₁ − 10P₂; δ(24P) = 12P₁ + 10P₂ − 10P₁; δ(40P) = 18P₁ | loops/brief.md, 4.3: the modal pattern of each cofactor, exact at 450 of 450 games clean to the pattern's depth (chain and past 5060) | the window is clean to the pattern's depth, 3, 2, 2 and 1: (c + 1)·P_i > n for i up to the depth | the laws are open |
| **COF9** | n = 9P is at its ceiling | arrival.md, "The cofactor rule" (measured at all 94 games of 188..5060) | none | open |
| **CWEQ, CWEQ2** | at a relaxation or restriction n ≥ 187 clean to depth 3 (CWEQ) or exactly 2 (CWEQ2), δ = δ_PB: opt(n) = opt(n − 1) + PB(n) − PB(n − 1) | loops/study-report.md, 4.3 (P1): 126 of 126 chain games at depth ≥ 3, 181 of 182 at depth ≥ 2 | the step kind from the sum of U\*, the clean depth from n's factorization | open |
| **CWINEQ** | the same, as an inequality at depth ≥ 2: opt(n) ≤ opt(n − 1) + PB(n) − PB(n − 1) | loops/study-report.md, 4.3 (P2); no counterexample among the 182 proven games | as above | open |

**Rows to read with care.**  At cofactor 33 the parity bound is blind (loops/brief.md, 4.4: δ_PB = 0 while δ is 88 to
386), so a CWEQ or CWEQ2 row at 33P, such as 9339, is not a target.  At depth 2 the equality is weaker evidence than at
depth 3 (CWEQ2 failed once in the chain, at 2512; the cofactors 30, 32 and 36 have ladders deeper than 2), which is why
CWEQ2 is its own relation.

## The mining targets

`targets.csv` lists the games past 5060 where a short streak can start: those whose best-known score no proved relation
determines from the game before.  A game that is settled inherits its score from its neighbor, so a short best-known
score there is the neighbor's shortfall carried; at a target the score is the miner's own.  A game is **settled**, and
left out, when its best-known score meets the relation with equality, by the first that holds of: N5 (a prime), N7 (an
even half-out step, which is at its ceiling), N4 (at its ceiling, B = A + n), L2 and L4 (at the bound, with the
hypothesis met), J3 (an odd semiprime from 189 on; it is added to the list of relations that settle, though R6 covers every
one of them as well) and R6 (a later member of a group of games that pose one root problem; the earlier member is the
game before or the one before a prime).  The count of each is in `summary.txt`.  The list is as of the best-known file
read, so a play that raises a game to its ceiling, or a neighbor that does, takes it off.

| column | meaning |
|---|---|
| `step`, `brief_step` | the kind of step as `docs/theory/parity-bound.md` W4 names it (`exchange`, `added`, `half-in`, `half-out`) and as the succession brief does (`exchange`, `restrict`, `relax`, `half-out`); both are read from the change of the sum of U\*, which equals W4's by the greedy basis (♦) |
| `layer`, `cofactor` | the number of prime factors of n, and n over its largest prime factor |
| `parity_gap` | PB(n) less the best-known score: the gap the proof would have to close, at most the true one |
| `best_known`, `delta_best_known` | the score, and best-known(n − 1) + n less it (the shortfall below the ceiling that the best-known scores show) |
| `plays` | how many rows the game has in the ledgers of dedicated plays, each row counted once: `rootfirst/ledger2.tsv` (the root-first plays), `rootfirst/ledger.tsv` (the pilot's first round, at level 3) and `hammer/ledger.tsv`; each row is one play of one seed at one level |
| `seeds_levels` | those plays, as `s41L4` for seed 41 at level 4, with `x2` after a play made twice, and an `h` after a play from the hammer's ledger (`s51L4h`); the ledgers have times of day only, so there are no dates.  The pilot's ledger has five columns and no level; it is read as level 3, which is the level of that round (`rootfirst/run.sh`) |
| `raised_by_play`, `best_raise` | whether any play's new score was above its known score, and the largest such raise |
| `law_disagreements` | the conjectured laws that the game disagrees with: each relation, which game it says is short, and by how much at least; rows at n − 1 or n + 1 that name this game count |

To regenerate it, run the audit (the command above): it reads the best-known file and the ledgers once at its start, so the
list follows both, and `summary.txt` gives the count, its split by step kind and by plays so far (0, 1, 2, 3 or more), the
number raised by a dedicated play, and the time at which each ledger was read.

## Projections and the window

The audit projects every recorded line (all the lines of the file and the proven lines) of every N ≤ 10000 onto every
smaller n, so the window is every N − n at once.  `summary.txt` gives the games beaten, the largest gain and the total gain
for N − n ≤ 8 (the window of the miner's repair), 40, 100, 400 and with no limit, so a wider window that finds more shows
as a larger count.  A projection that beats a score is replayed by the rules before it is written.  A projected game that
is not over could be played on, so a projection is a lower bound only; the audit does not complete projections.

## What the audit does not see

* The hypotheses of J1 (closed frames) for n with three or more prime factors: the frame model is not rebuilt here.
* Games built from a line of m < n − 1 by repeated N3 (the miner starts from the survivors of lines up to 8 games below).
* The sums of U\* are the dashboard's, checked against the best-known file's `in_the_bag` at every game and against a
  GF(2) greedy computation on boards spread over the range (`summary.txt`, data checks); the span conjecture (♦) is what
  makes that computation U\*.
* Root problems are the miner's digests.  Where a digest differs the games are not grouped, so R6 sees no pair there.
* Proofs of the chain past 2531 rest on statement U (results/README.md), so a relation that speaks for the proven game
  5060 inherits that.

Four environment variables are test aids: `AUDIT_TOP` (stop at a smaller game), `AUDIT_BEST` (read another best-known
file), `AUDIT_LEDGER` (read other play ledgers: paths separated by commas, each with an optional `:mark` for its
`seeds_levels`, as `path:h`; the default mark is `h` in a folder called hammer, none elsewhere) and `AUDIT_OUT` (write the
files elsewhere).  `selftest.py` needs none of
them.
