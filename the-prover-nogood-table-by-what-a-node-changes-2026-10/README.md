# The prover nogood table by what a node changes (2026-10)

Part of the [lab notebook](../README.md).

Started 2026-10-31.  Concluded 2026-10-31.

**Question.**  On a long search of the prover (`exact`, in `solver/noframe`) the table of nogoods holds up to 20,000
sets of about 40 members, and every node read all of it several times.  Can a node read the table at the cost of what
the node changes, with the same search trees?
**Answer.**  Yes.  Each nogood now watches two members that are not forced, as a SAT solver's clause does, and for each
of the two sets a node asks about, the table keeps how many members of each nogood lie outside the set last asked
about.  The phases of a node that read the table (propagation, the two scans for learning and for choosing the
conflict, and the packing cut) took 37% of a node on a search from scratch at game 1475 (4,724 nogoods on average) and
60% with the full table (17,830 to 18,496 nogoods); they take 4.5% and 5.7%.  Game 1475 for 200,000 nodes took 706.7 s
and takes 411.5 s, and 20,000 nodes with the full table took 130.5 s and take 49.6 s, each with the same search tree.
Nine other games, whose tables are small, take 84.2 s against 97.2 s.  The change is kept.  A long search now spends its
time on the parity solve (65%), the matching update (12%) and the playability check of the forced picks (10%).

## Method

**Terms.**  A *nogood* is a minimal unplayable set of numbers that a search has found: no playable set holds all its
members, so it holds at every node of the game's search.  A node's *roles* mark each number forced, barred or free.
*Propagation* applies the nogoods to the roles: a nogood with a barred member holds already, one whose members are all
forced ends the node, and one whose members but one are forced bars the last.  The nogoods *inside a set* are those
with every member in the set.  A node asks for them in two sets: its *branching set*, the heaviest set of its [parity
bound](https://github.com/bvchess/taxman/blob/de56c17/docs/theory/parity-bound.md#the-parity-bound), where they are the
conflicts it can learn and branch on, and the *picks* of its matching, where the packing cut uses them (both are in
[the entry on probing and branching](../smaller-prover-trees-by-probing-and-branching-2026-10/README.md), which named
the table as the next cost).

* **The long search.**  Game 1475 (root gap 590; the committed run took 6.3 million nodes), `exact --from 1475 --to
  1475 --threads 1`, in two forms.  From scratch with `--budget 200000`: the table grows to 8,884 nogoods, 4,724 on
  average over the 56,160 branching nodes; master took 11.8 minutes.  The *window with the full table*: resumed from the
  checkpoint that a search of 2,400 s left (564,224 nodes, 17,830 nogoods of 8 to 66 members, 41 on average, 75 open
  units; the branching entry's run), for 20,000 more nodes (`resume.sh`).  `--budget` deletes the checkpoint, so each
  run copies it first.
* **Builds.**  Release builds of the prover's `exact`, each in a cargo target directory of its own; master's builds from
  `git archive` trees of 0ef05d1 and of c0d0d3e, the commit of [the entry on
  threads](../one-prover-game-on-many-threads-2026-10/README.md), which keeps the one-thread trees of 0ef05d1.  The
  change was built on 0ef05d1 first and rebased onto c0d0d3e.  The builds are not kept.
* **The profile.**  `Instant` timers around the phases of a node, and counters, behind a cargo feature `profile`,
  printed when a `Prover` is dropped.  They are kept out of the commit; `profile-build.patch` is the instrumented build
  of the new table.  Master's profile build was the same timers on 0ef05d1.  The timers cost a few percent.
* **Same trees.**  A scratch example, `nogoodcheck.rs`, runs the search of `exact` (the roles of [the bottom-layers
  theorem](https://github.com/bvchess/taxman/blob/de56c17/docs/theory/frame-model.md#the-bottom-layers-theorem), the
  parity bound, one thread, no pause) and prints the verdict, the nodes, `Prover::stats`, the parity bound's counters,
  the size of the nogood table and an FNV hash of its members in order.  It compiles against the old table (a list of
  lists) and the new; `out/cmpfp.sh` diffs two outputs without their seconds.  The `exact --all 1` lines of the panel
  (`panel.sh`, `out/table.py`) are compared in nodes, `matching_nodes`, `branched_on_sources` and `barred_upper`.
* **Debug checks.**  Debug builds check every propagation against a scan of the table (`Prover::propagate_by_scan`) and
  every `inside` query against a filter over all nogoods (`Nogoods::scan`, a `debug_assert` in `Nogoods::inside`), so
  every search test of `game.rs` and `team.rs` is also a test of the table; `nogoods.rs` tests a random tree of roles
  against the scan.
* **Machine.**  The lab machine, one thread at nice 19 and one run at a time, beside the chain (at idle priority) and,
  now and then, another job of up to 4 threads.  Seconds are those of one thread, a few percent apart between repeats.
  Node counts and the fingerprints are exact.

## The change

[`src/nogoods.rs`](https://github.com/bvchess/taxman/blob/de56c17/solver/noframe/src/nogoods.rs) is a table `Nogoods` in
place of the list of lists of members.  It keeps every nogood's members, in the order learned (ascending), because a
node branches on the free members of a nogood in that order and the choice of the conflict breaks ties by table order.

* **Propagation, with two watched members.**  Each nogood watches two members that are not forced.  A node looks at the
  nogoods that watch a number it forced since its parent's propagation reached its fixpoint, where it changes no more
  roles (the trail, found by comparing the roles with the parent's).  It moves the watch to another member that is not
  forced or, if every member but the other watch is forced, bars that one (or ends the node, if it is forced too).
* **Why the watches need no undoing.**  The roles of a child extend its parent's, so a member that is not forced at a
  node is not forced at its ancestors, and the watches that fit a node fit its parent and its next child.  A watch left
  on a forced member is allowed only where the nogood has a barred member, and that holds at every descendant.  What
  breaks the argument is a nogood that the parent never saw: a node learns nogoods after its propagation, and the
  threads trade them between children.  So the children of a node examine whole the nogoods added since the node was
  propagated (`Base::checked`, the table's length at its fixpoint), and a unit's first node, which has no parent,
  examines all of them.  Examining a nogood costs two reads when both its watches are not forced.
* **The nogoods inside a set, with counts.**  For each of the two sets the search asks about, `inside(Set, set)` keeps
  the set last asked about, for each nogood the number of its members outside it, and the list of the nogoods with none
  (ascending, so the order of the old scan stays).  A query goes over the numbers that left or entered, updating the
  counts of the nogoods that hold them (a list of nogoods for each number), and counts afresh the nogoods learned since.
* **The same choice.**  The choice of the conflict weighs each candidate once and takes the first lightest; `min_by`
  weighed each twice a comparison, with the same result.
* **Memory.**  Three arrays of about 18,000 nogoods of 41 numbers (members, watch lists, occurrence lists), 9 MB at the
  limit of 20,000.

## Results

### The profile before (0ef05d1) and after

Game 1475 from scratch, 200,000 nodes, `exact --threads 1 --budget 200000`.  Seconds with the timers; the node's
microseconds and calls are those of the build before.

| phase | calls a node | before s | before, us a node | after s |
|---|---|---|---|---|
| propagation | 2.53 | 218.0 | 1,090 | 10.3 (the trail 3.1, the watches 7.0) |
| parity solve and forcing cut | 4.08 | 282.3 | 1,412 | 278.9 |
| matching update | 2.35 | 54.2 | 271 | 49.9 |
| `playable` of the forced picks | 2.44 | 43.8 | 219 | 40.7 |
| forced picks (`bound_barring`) | 2.33 | 10.2 | 51 | 9.4 |
| learning: the nogoods inside the set (the scan and `known`) | 0.28 | 9.2 + 0.2 | 46 + 1 | 1.3 |
| choosing the conflict | 0.28 | 7.9 | 40 | 1.4 |
| packing cut | 0.28 | 9.6 | 48 | 6.2 |
| learning: the peels (`minimal_unplayable`) | 0.04 | 2.8 | 14 | 2.9 |
| all, with the timers | | 664.5 | | 426.6 |
| all, without the timers (`nogoodcheck`) | | 706.7 | | 411.5 |

The phases listed leave 25 s of the 664.5 s before.  Propagation made 2.53 calls and 3.2 rounds a node before, and one
round a call after.  The last row compares master at 0ef05d1 (706.7 s) with the change rebased onto c0d0d3e (411.5 s);
the same change on 0ef05d1 took 421.7 s, and the three runs have one tree (below).  A node cost 3.53 ms before and 2.06
ms after.

With the full table (the window: 20,000 nodes, 6.5 ms a node before, 18,496 nogoods at the end), with the timers:

| phase | before s | after s |
|---|---|---|
| propagation | 69.5 | 1.4 |
| parity solve and forcing cut | 30.8 | 28.7 |
| matching update | 11.2 | 10.0 |
| `playable` of the forced picks | 5.1 | 4.0 |
| learning: the nogoods inside the set | 3.4 | 0.3 |
| choosing the conflict | 2.8 | 0.16 |
| packing cut | 2.8 | 0.9 |
| all | 130.5 | 49.6 |

The window is 2.6 times as fast.  Before, propagation alone was 53% of a node (3,475 us a node: 1.08 ms for each pass
over the table, 58 ns a nogood).  The four phases that read the table (propagation, the scan and `known`, the choice,
the packing cut) were 245.0 s of 664.5 s (37%) from scratch and 78.5 s of 130.5 s (60%) in the window; they are 19.2 s
of 426.6 s (4.5%) and 2.8 s of 49.6 s (5.7%) after.

**What the counters say** (200,000 nodes, after): 11.1 numbers forced on the trails a node (2.5 propagation calls a
node); 244 watch entries visited a node (22 for each number forced) and 400 members read looking for a watch; 3.7
nogoods examined whole a node (those learned since the parent) and 0.23 moved watches; 2,111,317 nogoods inside the
branching set over the 56,160 branching nodes (37.6 a branching node).  A query went over 369,861 numbers that left or
entered the branching set and 450,203 for the picks, 6.6 and 8.0 a query.  A query costs 23 us at a branching node
instead of 168 us.

### Same trees

The verdict, the nodes, `Prover::stats`, the parity bound's counters, and the size and in-order hash of the nogood
table are equal on one thread, between master c0d0d3e and the rebased change, and between 0ef05d1 and the change on it,
on these games (verdict "proven" in all): 798 (598 nodes), 864 (688), 988 (3,427), 1309 (2,479), 1508 (10,956), 1771
(554), 1920 (1,025), 2033 (212), 2044 (459), 1548 (12,771), 1587 (12,747) and 1612 (13,212), with tables of 38 to 1,016
nogoods.  At 1475 the three builds give the same 200,001 nodes, 8,884 nogoods, hash `3727f074a890ed8c` and statistics
[18 new conflicts, 56,142 known conflicts, 1,852,164 forced picks, 200,126 children, 4,653 cut by the bound, 0 by the
Lagrangian bound, 102,984 by the parity bound, 0 parity bounds not certified], and the same parity counters.

The `exact --all 1` lines are equal in the four fields on 988 (3,427 nodes), 1309 (2,479), 1508 (10,956), 1771 (554),
1920 (1,025), 2044 (459), 1548 (12,771), 1587 (12,747) and 1612 (13,212).  Seconds of these games, master c0d0d3e then
the change (`out/table.py panel-master2 panel-rebased`):

| game | nodes | master s | change s |
|---|---|---|---|
| 988 | 3,427 | 4.25 | 4.12 |
| 1309 | 2,479 | 3.56 | 3.54 |
| 1508 | 10,956 | 24.63 | 18.03 |
| 1771 | 554 | 1.27 | 1.28 |
| 1920 | 1,025 | 2.17 | 2.32 |
| 2044 | 459 | 1.73 | 1.72 |
| 1548 | 12,771 | 24.17 | 21.38 |
| 1587 | 12,747 | 15.00 | 13.92 |
| 1612 | 13,212 | 20.37 | 17.93 |
| all | 57,630 | 97.2 | 84.2 |

Game 1508 takes 27% less time, the high-gap games 1548, 1587 and 1612 take 7% to 12% less, and the five games of a few
seconds each are within 7% of master's either way (1920 is the slower, 2.17 s to 2.32 s).

### Sharing nogoods between a game's threads

`exact --from 1540 --to 1540 --threads 4 --all 1` at nice 19, once each (`share.sh`).  The sharing is the `--share`
knob of [the entry on threads](../one-prover-game-on-many-threads-2026-10/README.md): a thread that joins a game starts
from the game's table, and every 10 s each thread imports the others' nogoods.  On one thread 1540 takes 118,246 nodes
and 215.8 s on the new table.

| build | `--share` | nodes | wall s | thread s |
|---|---|---|---|---|
| master c0d0d3e | none | 146,722 | 74.7 | 296.4 |
| master c0d0d3e | 10 | 144,331 | 94.6 | 376.0 |
| new table | none | 150,748 | 70.8 | 280.9 |
| new table | 10 | 144,348 | 69.5 | 275.5 |

With the full scans, sharing cost 27% of the time: a thread that joins takes the game's table, and every node reads all
of it.  With the new table a larger table costs nothing at a node, sharing is neutral in time (69.5 s against 70.8 s)
and takes 4% off the nodes.  At 1540 the table is small, so the gain in nodes is small, but the case for sharing is no
longer against it.  One run each, on 4 threads of a loaded machine: differences of a few percent are noise.

### Tried and not kept

* **A flat copy of the old scan** (`inside` over a contiguous array, an `all` per nogood): 183 us a query against 168 us
  for the lists.  The cost is the number of nogoods read, not the layout.
* **Counters of the unforced members of each nogood**, updated as roles change.  They need undoing when the search goes
  back up, and a number is in about 500 nogoods, so 11 numbers a node cost as much as a pass over the table.
* **The candidates from the occurrence lists of the forced numbers**, each read whole: about the cost of one pass.
* **A bitset for each nogood and a subset test word by word**: estimated at 40 us a query from the sizes, not built,
  against 23 us for the counts, which ride on the sets changing by 2 to 8 numbers a query.
* **Not tried, small:** a watch-list entry that carries the other watch, to skip a satisfied nogood without reading it;
  a preference for a barred member as the new watch.  Both save a part of the 7.0 s of the watches in 427.

### What a long search spends on next

Game 1475, 200,000 nodes, 427 s:

* the parity solve and forcing cut, 65%: 4.08 solves a node and 1,394 us of the node's 2.1 ms;
* the matching update, 12% (0.25 ms a node);
* `Board::playable` of the forced picks, 10% (2.44 peels a node, 84 us each: a child's forced picks are its parent's
  plus a few, so an incremental check is the next candidate, and it is no question of the table);
* the forced picks 2.3%, the table 4-6%, the peels 0.7%.

### Candidates that change the tree (not done)

* **The table at its limit.**  The window's 20,000 nodes learned 666 nogoods and ended with 18,496, 1,504 short of the
  limit of 20,000.  At that rate the limit is soon reached, and the rest of game 1475's 6.3 million nodes would run with
  a frozen table: it learns nothing and replaces nothing, so a nogood of no use stays.  A table that forgets (the frame
  solver's clearing took [22-26% less time](../search/forgetting-nogoods-2026-10/README.md)) or holds more (50,545
  nogoods took [0.946 of the steps there](../search/the-root-gap-and-the-size-of-a-game-2026-10/README.md), and no less
  CPU) was priced by the scan; the table now costs little, so both are worth measuring.
* **The packing cut** costs 6.2 s of 426.6 (1.5%) and cut nothing in the earlier counts (0 of 1,775 and 0 of 1,068
  branching nodes).
* **The Lagrangian bound's `Lag::terms`** still reads its own copy of the nogoods at every node.  `exact` uses that
  bound only without the parity bound.

## Decision

* **Kept: the table of de56c17.**  It changes no verdict, no node count and no table (twelve games to the end, and
  game 1475 at 200,001 nodes), and takes game 1475's 200,000 nodes from 706.7 s to 411.5 s and its window from 130.5 s
  to 49.6 s.
* **Open, each a candidate for a later entry:** a table that forgets or holds more, and the packing cut (1.5% of a node,
  and a cut of nothing in the earlier counts), either of which can change a tree; and an incremental `playable` for the
  forced picks (10% of a node), which does not.
* **For the code.**  On the rebase onto c0d0d3e, `Prover::team` takes the lists and builds the table (`.into()`), and
  `trade` reads `Nogoods::since` and adds with `Nogoods::extend`.  A nogood that arrives at any time is examined whole
  by every node propagated before it (`checked`), so trading needs nothing more.  `Prover::nogoods` is a `Nogoods`
  (checkpoints use `to_vec` and `From<Vec<Vec<u32>>>`), and the packing cut and the lookups take `&mut self` because of
  the counts.

## Files

The scripts read the folder named by the environment variable `NOGOODS_DIR`, or the folder of the script, which holds
the builds they run in `bin/` (`exact-master`, `exact-master2`, `exact-final`, `exact-rebased`, `exact-prof-before`,
`exact-prof-v2`, `exact-prof-v2b`, `nogoodcheck-master`, `nogoodcheck-final`, `nogoodcheck-master2`,
`nogoodcheck-rebased`) and where they write `out/` and `ckpt/`.  The builds and the checkpoints are not kept.

* `nogoodcheck.rs`: the scratch example of the fingerprint; copy it to `solver/noframe/examples/` and build it with
  `cargo build --release --example nogoodcheck`; `nogoodcheck BUDGET N...` (BUDGET 0: none).  It compiles against the
  table as a list of lists (0ef05d1) and against `Nogoods` (the change).
* `profile-build.patch`: the instrumented build of the new table against 0ef05d1 (`patch -p1` from the repository's top;
  `cargo build --release --features profile`): the timers and counters, the feature `profile` in `Cargo.toml`, the
  module `nogoods.rs` as it stood before the last clean-ups, and its use in `game.rs`.  It adds the module to `lib.rs`.
* `queue.sh`: the first measurement queue, on 0ef05d1 and the change on it: the fingerprints of twelve games and of 1475
  at 200,000 nodes, a panel (its output is not kept), and the two profiles of 1475 from scratch.  `queue2.sh`: the queue
  after the rebase onto c0d0d3e: the fingerprints, 1475 at 200,000 nodes, and the panels of master and the change.
* `panel.sh BINARY LABEL GAME...`: `exact --all 1` on each game, one thread, a fresh checkpoint directory each; writes
  `out/LABEL/N.jsonl`.
* `resume.sh BINARY LABEL EXTRA_NODES`: the window; resumes the checkpoint of game 1475 for EXTRA_NODES more nodes.
* `share.sh`: game 1540 on 4 threads, with and without `--share 10`, master c0d0d3e and the rebased build.
* `out/cmpfp.sh A B`: diffs two fingerprints without their seconds.  `out/table.py BASE LABEL...`: nodes and seconds of
  panel runs against the base run, and whether the four counters are equal.
* `out/fp-master.txt` (0ef05d1), `out/fp-final.txt` (the change on 0ef05d1), `out/fp-master2.txt` (c0d0d3e) and
  `out/fp-rebased.txt` (the change on c0d0d3e): the fingerprints of the twelve games.  `out/long-master.txt`,
  `out/long-final.txt` and `out/long-rebased.txt`: the same builds on 1475 at 200,000 nodes.
* `out/long-prof-before.txt` and `out/long-prof-v2b.txt`: the profiles of 1475 from scratch before and after (the
  counters of "what the counters say" are in the second).  `out/prof-before.txt` and `out/prof-v2.txt`: the profiles of
  the window, the second from an earlier build of the table than `profile-build.patch` makes, with fewer timers.
* `out/panel-master2/` and `out/panel-rebased/`: the `exact --all 1` line of each of nine games on c0d0d3e and on the
  change.  `out/t1540/`: the lines (`.jsonl`) and the timing output (`.txt`) of 1540 on 4 threads, and `rebased-1.jsonl`
  on one thread.

## Commits

On master of [bvchess/taxman](https://github.com/bvchess/taxman), 2026-10-31:

* de56c17: the prover reads its nogood table by what a node changes (`src/nogoods.rs`, on master 6fde939).
