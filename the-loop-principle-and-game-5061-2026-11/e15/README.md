# E15: the gluing proof of 5061, built and run, and where it stops

## The idea, and the answer

To prove that the best-known game of 5061 (8,057,936) is optimal given statement U, it is enough to show that δ(5061)
≥ 746, where δ(n) = opt(n − 1) + n − opt(n) and opt(5060) = 8,053,621 is proven.  The study's plan (study-report.md,
Section 15) does that locally.  Take an optimal set S of 5061 and look only at a region of the board: a few columns of
cells k·P.  Whatever S holds there (its *state*), find another set of cells for the same region, on board 5060, that
gains 746 and that the *gluing lemma* proves playable with the rest of S, whatever the rest is.  Then S less 5061, with
the region swapped, is a playable set of 5060 worth ΣS − 5061 + 746, so opt(5061) ≤ opt(5060) + 5061 − 746.  The
states are finite, so the proof is a finite table.

The tool is built (`solver/frame/examples/gluing.rs`), and it reproduces E12's tables byte for byte.  At 5061 it settles
107,387 of the 134,608 states of the three-column base region 241, 251, 157 (80,841 by a witness that gains 746 or
more, 26,546 by optimality).  But **the method does not prove 5061, and it fails the calibration**.  The proven games 3297 and 3507,
the same regime-(ii) step, are not proven by it either: at each of the three games the recorded set's own state has
no witness on E10's eight-column region, by an exhaustive search.  The optimal set of n − 1 that the step comes from
holds a column-closed group of cells that uses some hub once, and S, which reached n by moving those cells, holds no
such group to stand for it.  The lemma has to allow every possible rest of the board, and some rest could close a core
through that hub.  Adding columns does not help: with every column from 127 (at 5061) or 89 (at 3297 and 3507) up to
n/4, the set of n − 1 is still not covered.  So the open states are not better games (E11 found none), and growth does not close them.  They
are a limit of core domination at this step, the one E12b found at 12P's case B2, and they need an argument about how
the rest of S pays the hub (a payment-scheme argument, as L4's proof makes).

## Terms

* **Cell, row, hub, column factor.**  For a prime P with 2P² > n, the cells of P's column are the numbers k·P ≤ n with k
  composite; k is the cell's row, or hub.  A cell's maximal factors are its hub k and its column factors (k/q)·P, one
  for each prime q dividing k.  A column factor of a prime row is a number of layer 2 up to n/2, which no optimal set
  plays from 187 on (F4, F10); a column factor of a composite row is a cell.
* **Source, candidate, state.**  Sources are the cells above n/2, candidates the others.  Given U at n, some optimal set
  S of n holds U\*(n), so on the region it holds exactly the sources in U\*(n) (n among them: 5061 = 21·241 is a cell).
  S's state is the set of candidates it holds.  A state has no core in its *window instance* (members its cells, pool
  every hub and every column factor that is not a member), since such a core is a core of S.
* **Column-closed, profile.**  A nonempty X ⊆ Z is column-closed in Z when every column factor outside Z that a member of
  X lists is listed by another member of X.  Its profile is the rows it uses once and the rows it uses twice or more.
* **Covers.**  W, S's cells, covers W′, a set of cells of board n − 1, when every X column-closed in W′ has a Y
  column-closed in W that uses every row X uses and uses once only rows X uses once.
* **Witness, exclusion, open.**  A witness of a state is a W′ it covers, holding the sources less n, whose candidates
  are worth at least the target more than the state's: 746 at 5061, δ(n) at the calibration games.  A state is
  *excluded* when it covers a heavier set of board n (same sources), since S with that set would beat the optimal S.  A
  state with neither is *open*.
* **Free cell.**  A cell whose column factors are all members lists its hub alone, so it can join or leave any
  column-closed set.  The tool keeps free cells apart, as counts by row, which makes a dense column cost no more than its
  other cells (over the columns of 5061's E10 region, the most column-closed parts of one column fell from 126,976 to
  684).

## The lemma, and the three conditions it is used under

The gluing lemma (study-report.md, Section 15.2; refereed in ../e16/referee.md): if W covers W′, then O ∪ W′ is
playable on board n − 1, O = S − W, and δ(n) ≥ ΣW′ − ΣW + n.  The referee found the generalized statement correct with
three repairs, and every use here meets them:

* **G1.**  S plays no layer-2 number qP for a region prime P: S is optimal and n ≥ 187, so F4 and F10 give it.
* **G2.**  n is a cell of the region: 5061 = 21·241, 3297 = 21·157 and 3507 = 21·167, and the tool refuses a base
  region without n's column.
* **G3.**  The δ clause needs ΣS = opt(n): S is an optimal set.

The tool checks on the tables of n (`Tables::max_factors` and `max_composites`) the facts the lemma rests on: 2P² > n for
every column, a cell's maximal factors are its hub and its column factors, and nothing off a column lists its cells or
its column factors.

## How the tool decides

* **Covering.**  A set is column-closed exactly when each of its columns' parts is column-closed or empty, so the
  profiles of a set are those of its columns' parts combined row by row.  One profile *stands for* another when a Y of
  the first can be chosen for an X of the second; that relation survives adding the same part to both, so only the
  profiles nothing else stands for are kept, on both sides, at every column.  Free cells enter as counts: a row with a
  free cell can be used once more, and the hardest X's use every free cell they can.
* **States.**  Every candidate subset of the base region whose window instance has no core, by a walk over the
  candidates.  The core test is a dismantling (P5, P7); on every base state it agrees with the crate's peel
  (`playable::playable_against`), and every covered set the searches find is checked by the peel too.
* **Witnesses.**  A search column by column over the candidate subsets of each column, with the covering checked as each
  column is chosen (an X of the columns chosen so far is an X of the final W′), the core test of the partial set, and a
  bound on the gain.  It tries one changed column, then two, then three (`--changes`); `--exhaustive` takes any change.
* **Exclusions.**  The same search on board n with a gain of 1, changing at most two columns.
* **Growth.**  An open state is extended by a column of `--pool`: the one whose rows the Y's nearest to the uncovered X's
  missed most often.  Its extensions (its held sources and any of its candidates, with no core) are grouped by the new
  column's core parts and free cells, since a witness that keeps the new column as it is serves the whole group, and
  only the extensions it does not serve are solved one by one, up to `--max-columns` columns.
* **The recorded game.**  The recorded set of n (the committed one, or the best-known one) is solved first, and its
  witness is glued to the rest of it and decided by the crate's peel on board n − 1, independently of the lemma; with
  `--cover`, the tool asks whether its state covers the committed set of n − 1 on the region, the natural witness, and
  glues that.

## Results

### The port's check against E12

`gluing family 8|12|16 [--no-sources] --table FILE` writes E12's tables in E12's order and format.  All five agree with
E12's byte for byte (`cmp`): table_8P, table_12P and table_16P with the sources fixed, and table_8P_nosources and
table_12P_nosources with them free (`port/`).  The counts are E12's: 8P 3 states, all closed; 12P 9, 3 open; 16P 125,
5 open ({4P, 6P}, {4P, 6P, 8P₁}, {4P, 6P, 8P₂}, {4P, 6P, 8P₃}, {8P, 4P₁, 6P₁}); 12P with the sources free 1,812, the
same 3 open.  12P with free sources takes 0.1 s, against E12's 62 s.  The tables were checked again after the free cells
were kept apart, with the same result.

### The base regions: one table for every state

Every state of the three-column base region, solved without growth: a witness changing up to all three columns, an
exclusion changing up to two.  The three base regions have the same shape (column 0 with rows to 21, column −1 with
rows to 20, and a column with rows to 32), so the same 134,608 states; the outcomes differ with the weights.

| game | base region | target | closed | excluded | open | time on 12 threads |
|---|---|---:|---:|---:|---:|---:|
| 5061 | 241, 251, 157 | δ ≥ 746 | 80,841 | 26,546 | 27,221 | 102 s |
| 3297 | 157, 163, 101 | δ ≥ 402 | 84,616 | 22,980 | 27,012 | 178 s |
| 3507 | 167, 173, 107 | δ ≥ 393 | 86,436 | 21,328 | 26,844 | 131 s |

A closed state is proved: if S has that state, δ(n) is at least the target, whatever S holds off the region.  An
excluded state is no optimal set's.  At every game the recorded set's own state is among the open ones, as the study
found by hand at 5061 (Section 15.3).  Of 5061's open states, most miss one hub, usually a high row of column 157 (32
in 6,627 of them, 28 in 4,164, 24 in 2,256, 30 in 2,138), whose other cells lie in columns such as 149 and 151
(`open_kinds5061.txt`).

### The recorded states on E10's regions: no witness of any shape

The recorded set's state (the best-known one at 5061, the committed ones at 3297 and 3507), solved with E10's region as
the base and an exhaustive search (`--exhaustive`, every change of the candidates, the sources kept):

| game | region | search | result | the nearest miss |
|---|---|---:|---|---|
| 5061 | E10: 241, 251, 157, 163, 149, 151, 421, 631 | 6,634 nodes, 0.1 s | no witness | an X using hubs 8, 12, 16, 18, 20 once; the nearest Y misses 16 |
| 5061 | E10 and 313 (16·313 holds hub 16 in E14) | 191,355 nodes, 2.2 s | no witness | hubs 8, 12, 16, 18, 20, 24, 27, 30 once; misses 24 |
| 3297 | E10: 157, 163, 97, 101, 103, 107, 271, 409 | 8,609 nodes, 0.1 s | no witness | hubs 8, 12, 16, 18, 20 once; misses 16 |
| 3507 | E10 and 113: 167, 173, 103, 107, 109, 113, 283, 433 | 9,612 nodes, 0.2 s | no witness | hubs 8, 12, 16, 18, 20 once; misses 16 |

At a recorded state a witness is necessarily an optimal set of n − 1: a gain of δ(n) or more makes O ∪ W′ worth at least
opt(n − 1), so exactly that.  So the table says that no optimal set of n − 1 that agrees with S off the region (and holds its sources) is covered by
S's state.  **The calibration fails**: the proven δ(3297) = 402 and δ(3507) = 393 are not reached by the lemma on the
regions that hold their changes.  Growth gives the same answer: from the base region, the growth adds 163, 149, 151, 421
and 631 in that order, and the best-known state of 5061 is still open on the eight columns (`grow5061-sample.txt`).

### The natural witness, on wide regions

The natural witness is the committed set of n − 1 on the region.  `--cover` asks whether the recorded state covers it,
and glues it to the rest of the recorded set (O ∪ W′) for the crate's peel on board n − 1:

| game | region | gain | covered | O ∪ W′ by the peel | replayed by the rules |
|---|---|---:|---|---|---:|
| 5061 | E10 | 746 | no | playable, 2,189 members | 8,053,621 = opt(5060) |
| 5061 | all 140 primes from 127 to 1013 | 746 | no | playable | 8,053,621 |
| 3297 | E10 | 402 | no | playable, 1,427 members | 3,418,627 = opt(3296) |
| 3297 | all 120 primes from 89 to 823 | 402 | no | playable | 3,418,627 |
| 3507 | E10 and 113 | 393 | no | playable, 1,521 members | 3,871,751 = opt(3506) |
| 3507 | all 128 primes from 89 to 877 | 393 | no | playable | 3,871,751 |

So the witness is a real optimal set of n − 1 (the committed one), and the lemma cannot certify it.  A column that both sets
hold alike can only help the covering (a Y can use it as X does), and the 120 to 140 columns of these regions help
none of the three: growth cannot close these states.  Smaller primes were left out for cost, since the tool enumerates
every candidate subset of each column and the count grows fast as P falls (2¹³ at 113 for 5061, 2¹⁷ at 59 for 3297);
the usable columns (2P² > n) start at 53 and 41.

The smallest uncovered X, found by `diag.py`, a brute force that shares no code with the tool, over E10's region:

* **5061**: {12·251, 18·251, 20·251, 12·157, 18·157, 20·157, 27·157}, hubs 12, 18 and 20 twice and 27 once, the only
  one in one or two columns.  In 5060's set, 10·157 and 12·157 are held, so 20·157 lists only 4·157 and the column-157
  part is closed; the best-known game moved 157's cells to 6·157 and 16·157, and S has no second closed group using hubs
  12, 18 and 20 twice to stand for it.
* **3297**: {18·103, 27·103, 30·103}, hubs 18, 27 and 30 once, and two more in column 103.  In 3296's set 10·103 and
  15·103 are held, so 30·103 lists only 6·103; 3297's set holds 14·103 for 15·103, and there 30·103 lists 15·103 as well.
* **3507**: {18·167, 12·173, 18·173, 20·173}, hub 18 twice and 12 and 20 once, regime (ii)'s own structure: in 3506's
  set 6·167 and 9·167 are held, so 18·167 lists its hub alone; in 3507's set 6·167 is gone.  Four more lie in columns 109
  and 113.

### Growth, sampled and sized

Every 1000th of 5061's 27,221 open base states (28 of them) was grown from the pool 163, 149, 151, 421, 631 up to E10's
eight columns, at most 30 s a tree and 10⁶ nodes a search (`grow5061-sample.*`), in 91 s on 12 threads.  11 trees
finished, and each closed completely: every extension of those base states is closed or excluded.  The other 17 reached the time limit, with 104 states open at eight columns and 1,683 not
reached.  The trees took 24 s each on average, so growing all 27,221 would take at least 180 CPU-hours (15 hours on 12
threads) even cut at 30 s a tree.  That is past the 3-hour bound, and it was not run: the best-known state alone shows
the theorem does not follow from the table.

## What this proves, and what it needs

* **Not proved: δ(5061) ≥ 746.**  The best-known game's own state has no witness on E10's region, on E10 and 313, or, for
  the natural witness, on any region of columns from 127 to 1013.  The table cannot prove the theorem without a further
  fact, whatever the other states do.
* **The calibration fails at 3297 and 3507**, the same way.  This is a gap in the method, not a better game: both games
  are proven, and the witness is an optimal set of n − 1 that the peel plays.
* **No better game of 5061 is named.**  The best-known state covers no heavier set of board 5061 on E10's region or on E10
  and 313 (the exclusion search, exhaustive there), and E11 found no better game with 5060's set outside any region up
  to the columns of 29 to 1013.  The other open states were searched for heavier sets changing at most two columns.
* **What the open states need.**  In each, the witness holds a column-closed group of cells that uses some hub once (27
  at 5061; 18, 27 and 30 at 3297; 12 and 20 at 3507), and S holds no group that stands for it.  The lemma must allow any
  rest of the board, and a rest that lists that hub could close a core through the group; S's own rest does not, since
  O ∪ W′ is playable.  So a proof needs a fact about how S's rest pays the hub: a payment-scheme argument, as L4's proof
  makes for 12P's case B2 (E12b), not a wider region.  The 107,387 states of 5061's base region that are closed or
  excluded need nothing more; the 27,221 open ones were not grown in full, since the best-known state alone settles the
  question of the theorem.
* **For later games.**  The same regime-(ii) structure appears at every 21P step of this kind (E10 found it column for
  column at 3297, 3507 and 5061), so the gluing table does not prove these steps on its own.  It does settle most states
  of a three-column region in seconds, which a scheme argument could then be limited to.

## Files

* `README.md`, this file.
* `port/`: the five E12 tables as the tool writes them, each identical to its file in `../e12/`.
* `base5061.jsonl.gz`, `base3297.jsonl.gz`, `base3507.jsonl.gz`: every base state, one line each (`base`, the leaf
  `counts` as closed, excluded, impossible, open, limit, and the `leaves`: region, state's candidate cells, outcome, and
  the witness or heavier set with its gain, or the nearest miss); `base*.txt`, the printed output of those runs,
  with the recorded set's leaf.
* `recorded5061-E10.txt`, `recorded5061-E10-313.txt`, `recorded3297-E10.txt`, `recorded3507-E10.txt`: the recorded
  states searched exhaustively on E10's regions.
* `cover*.txt`: the natural witness on E10's regions and on the wide ones, with O ∪ W′ decided by the peel and replayed.
* `diag.py` and `diag*.txt`: the smallest uncovered X of the natural witness, by brute force.
* `open_kinds.py` and `open_kinds5061.txt`: what 5061's open base states miss.
* `grow5061-sample.jsonl` and `.txt`: the growth sample.

## How it was run

On batmobile, 2026-11-11, from 10:20 to 12:10 PST, every run at `chrt -i 0 nice -n 19`, at most 12 threads.  The tool is
`solver/frame/examples/gluing.rs` on the research repository's branch `loops-e15` (from `loops-e6`; never pushed):
commit 7efd839 (the tool), 0a0ddbe (grouped growth, `--only`, `--cover`) and 4219bcf (rustfmt only); every output
here is from the binary of 0a0ddbe, built with `nice -n 19 cargo build --release -j 4 --example gluing`, and the
binary of 4219bcf writes the 16P table identically.  The commands, from the binary
`solver/frame/target/release/examples/gluing` of the worktree:

```text
gluing family 8|12|16 [--no-sources] --table port/table_cP[_nosources].jsonl
gluing game 5061 --base 241,251,157 --max-columns 3 --threads 12 --out base5061.jsonl
gluing game 3297 --base 157,163,101 --max-columns 3 --threads 12 --out base3297.jsonl
gluing game 3507 --base 167,173,107 --max-columns 3 --threads 12 --out base3507.jsonl
gluing game 5061 --base 241,251,157,163,149,151,421,631[,313] --limit 0 --exhaustive --node-limit 20000000
gluing game 3297 --base 157,163,97,101,103,107,271,409 --limit 0 --exhaustive --node-limit 20000000
gluing game 3507 --base 167,173,103,107,109,113,283,433 --limit 0 --exhaustive --node-limit 20000000
gluing game N --base REGION --max-columns 200 --limit 0 --cover      # E10's region, and every prime 127..1013 or 89..n/4
gluing game 5061 --base 241,251,157 --pool 163,149,151,421,631 --max-columns 8 --threads 12 \
    --only base5061.jsonl --stride 1000 --tree-seconds 30 --node-limit 1000000 --out grow5061-sample.jsonl
python3 -I diag.py N REGION 3;  python3 -I open_kinds.py base5061.jsonl.gz 241
```

The recorded sets are the committed `results/optimal.jsonl.gz` (built into the crate) to 5060, and for 5061 the highest
score of `/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl` (8,057,936).  U\*(n) is the crate's
(`Board::plain`).  The base outputs were written plain and compressed afterwards; `--only` reads a plain file.
