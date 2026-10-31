# Cheaper prover nodes, same trees (2026-10)

Part of the [lab notebook](../README.md).

Started 2026-10-31.  Concluded 2026-10-31.

**Question.**  Where does a node of the prover's search (`exact`, in `solver/noframe`) spend its time, and how much
cheaper can a node be made while every game keeps its search tree: the same verdict and the same node count?
**Answer.**  About half of a node went into building the elimination over GF(2) of the [parity
bound](https://github.com/bvchess/taxman/blob/0ef05d1/docs/theory/parity-bound.md#the-parity-bound) again at every
solve (53 of 115 s at game 2044, 20 of 52 s at game 988), and much of the rest into exchange graphs whose circuits were
bitsets over every number.  A child takes its parent's elimination and circuits, less what its own roles change;
circuits are short lists kept across exchanges; the deletion filter dismantles only the residual.  On a panel of nine
games the time of `exact --threads 1` fell from 801.7 s to 239.5 s (0.30 of master's), with master's verdict and node
count on every game.  Two follow-ups came after.  `exact` no longer pauses for the Lagrangian bound's warm-up when that
bound stays off, which took the panel to 203.3 s and made the trees independent of the clock.  The check of the
certificate reduces every circuit afresh, which costs 15% on the panel (234.3 s, 0.29 of master's) and makes the bound
rest on the theorem and weak duality alone.  All of it is kept.

## Method

**Terms.**  A *solve* computes the parity bound at a node: the heaviest set of numbers that is independent at both
parities, found by shortest augmenting paths.  A child's solve starts from its parent's set (a *warm start*); when the
warm start gives up on a negative cycle (a *fallback*), the solve is redone from scratch.  The *elimination* is the
row reduction over GF(2) of the vectors of the set's members.  The *circuit* of a *candidate*, a number outside the set,
is its unique expression as a sum of members of the set.  The *exchange graph* of a solve takes its arcs from the
circuits.  The *roles* are the forced, barred and free numbers a node starts from; `exact` starts from the roles of
[the bottom-layers theorem
(F4)](https://github.com/bvchess/taxman/blob/0ef05d1/docs/theory/frame-model.md#the-bottom-layers-theorem).  The *open
units* of a search are the subtrees it has still to explore when it pauses.

* **Machine.**  The lab machine, one thread at nice 19 and one run at a time, beside the chain (a `taxman` process at
  nice 10 that kept all 88 threads busy).  Seconds are those of one loaded thread: rough, a few tens of percent apart
  between runs.  Node counts and the fingerprints below are exact.
* **Builds.**  Release builds of the `exact` binary of `solver/noframe`, each in a cargo target directory of its own
  (`nice -n 19 cargo build --release --manifest-path solver/noframe/Cargo.toml --target-dir DIR --bin exact`).  Master's
  binary was built from fdc4e62, before any change.  The builds are not kept.
* **The panel.**  `panel.sh BINARY LABEL [GAMES]` runs `exact --from N --to N --threads 1 --out runs/LABEL/out.jsonl
  --checkpoints runs/LABEL/ckpt_N` for each game, with a fresh checkpoint directory each, so that no search resumes.
  `compare.sh BASE LABEL...` tabulates nodes and seconds against a base run.  `exact` starts from the roles of F4 by
  default.
* **The fingerprint.**  `exact` paused every search at 20 s for the warm-up of the Lagrangian bound (a second bound,
  over the nogoods), and did so even when that bound stayed off, as it does with the parity bound.  It then restarted
  the open units from scratch.  A cold start can pick another heaviest set where several tie, so a tree, and its
  counters, depended on where the pause fell.  So the check of same trees is also made by a scratch example,
  `nodecost.rs`: `nodecost N...` runs the search of `exact` from the roles of F4 with no pause, and prints the verdict,
  the nodes, `Prover::stats`, the nogoods and every field of `MeetStats`.  Every step was checked against master's
  output (`fingerprint-master.txt`) on 798, 864, 988, 1771 and 2033, and the final build on 1584 too.
* **The profile.**  Timers (`Instant`) around each phase of a node and of a parity solve, and counters, behind a cargo
  feature `profile`, printed per thread when a `Prover` is dropped.  They are kept out of the commits; the instrumented
  diff is `v4-instrumented.patch` (against fdc4e62, the changes as of the fourth build with the timers).  The timers
  cost a few percent.

**The panel**: six games that took 2-60 s in the prover's result files for 2..1300 and 1301-2175 (plain root), spread
over n, and the three games (1309, 1508, 1920) named when the work was set.

| game | nodes | seconds in the result file | why |
|---|---|---|---|
| 988 | 19,568 | 25.4 (laptop, plain root) | many conflicts and fallbacks |
| 1347 | 14,393 | 34.6 | 1300s |
| 1584 | 26,516 | 57.2 | 1500s |
| 1771 | 5,553 | 11.1 | 1700s |
| 2033 | 2,747 | 8.8 | 2000s, few nodes |
| 2044 | 12,546 | 42.6 | 2000s |
| 1309 | 17,887 | 45.3 | named |
| 1508 | 24,078 | 63.5 | named |
| 1920 | 18,887 | 46.3 | named |

## Results

### The profile before (master, with timers)

2044 took 115 s over 12,546 nodes (9.2 ms a node, the game's setup included), and 988 took 52 s over 19,568 nodes.

| phase | 2044 s | 988 s |
|---|---|---|
| parity solves, in all | 89.6 | 41.8 |
| - setup: the forced numbers' rows built again, every free number classified | 42.0 | 16.2 |
| - the parent's members added again | 10.7 | 3.8 |
| - exchange graphs: circuits by reduction / arcs | 10.8 / 5.1 | 3.8 / 2.3 |
| - searches for an improving cycle | 6.1 | 6.3 |
| - the split's search again in `finish` / its checks | 2.2 / 2.0 | 1.9 / 1.4 |
| - solves from scratch after a fallback (setup, augmentations) | 1.5 + 1.6 + part of the graphs | 1.4 + 1.3 + part |
| matching | 15.9 | 5.3 |
| deletion filter (`minimal_unplayable`) | 4.9 (125 calls) | 4.1 (549 calls) |
| `playable` of the forced picks | 2.5 | 1.7 |
| forced picks from the dual, nogood propagation | 0.7, 0.3 | 0.4, 1.1 |

* A solve is 1.2 to 1.35 a node, and a node is mostly a leaf: at 2044, 2,025 of 12,546 nodes branch, 6.2 children
  each.
* The rows' combinations and the circuits were bitsets over every number (32 words at 2044), though an exchange graph
  had about 1,300 circuit arcs (79 million over 60,594 graphs) for several hundred candidates: a circuit holds one or
  two members.
* At 2044 there were 1,267 insertions and 20,800 row eliminations a node, each elimination over the row's vector and
  its 32-word combination.
* The matching's 15.9 s at 2044 are nearly all the 41 open units that `exact` restarted after its 20-s pause in that
  run, each solved from scratch (about 0.36 s each); an incremental update costs about 0.1 ms.
* Fallbacks of the warm starts: 527 of 15,253 at 2044 (3.5%), 2,261 of 26,367 at 988 (8.6%), each a solve from scratch
  of 22 to 54 augmentations with an exchange graph.  At 2044 they were half of all the exchange graphs.

### The changes, in order

Seconds are those of `nodecost` (search only, no pause) on 798, 864, 1771, 2033 and 988.

| build | what | seconds |
|---|---|---|
| master | | 4.21, 7.48, 29.79, 23.00, 49.93 |
| 1 | the deletion filter on the residual alone | 3.65, 4.89, 25.00, 19.70, 34.89 |
| v1 | changes 1 to 5 | 1.87, 2.43, 6.80, 6.12, 22.76 |
| v3 | + 6, 7 | 1.70, 2.25, 5.51, 4.60, 20.26 |
| v4, the final build | + 8 | 1.65, 2.18, 5.29, 4.61, 15.40 |

988's last figure is the final build's; the v4 run gave 19.24.  1584 took 124.03 s on master and 36.87 s on the final
build.  All eight changes are kept.

1. **The deletion filter dismantles only the residual.**  Each trial of `Board::minimal_unplayable` peeled the whole
   board (O(n) each, |S| trials).  Dropping a member c only makes removals easier, so the residual of S − c is what
   dismantling R − c leaves, with c no longer a pick; when c is outside R and a maximal factor of no member of R, it is
   R itself.  At 2044 it took 4.9 s before and 0.04 s after; at 988, 4.1 s and 0.12 s.  It was tested against the plain
   filter on random sets of boards 30 to 400.  A first version also added a member outside R back into R after a
   successful trial; that is harmless, since such a member always has a factor private to it, but wrong in principle,
   and was fixed before the commit.
2. **Forced rows without combinations, one reduction an add.**  A forced number is untracked, so its row's combination
   is zero, and its reduction and insertion skip the combinations (41 to 9 words an elimination at 2044).  Classifying
   the free numbers needs only independence.  `add` reduced each number twice (to test, then to insert); `try_add`
   reduces once into two buffers.  The setup at 2044 fell from 42.0 to 22.7 s.
3. **The split from the last search.**  When the last search for an improving cycle finds none, its distances are those
   that `finish` computes (same sources, no hubs, tolerant, the sink only read), so `finish` reuses them.  At 2044 that
   took 2.2 s before and 0.08 s after.  The count of `foreign` forced numbers, a statistic, was quadratic and is
   linear.
4. **The matching from scratch stops at the cheapest path.**  Its Dijkstra ran to the end at every augmentation; it
   stops once the distance popped reaches the cheapest path to the sink t (exact: nothing later is cheaper, and the
   potentials and the dual take distances only up to it), and its sources are heapified (distinct keys, so the same
   pops).  The gain is small: the open units' solves at 2044 went from about 0.36 to 0.22 s each (with the timers),
   because t's potential lies below most right vertices' by about BIG, a large constant, while forced picks are
   unmatched, so the search still covers most of the graph.  It was tested against the search run to the end (the same
   matching and dual).
5. **The child's start derived from the parent's state.**  The workspace keeps the state its last certified solve left
   (rows, candidates, set, circuits), known by the certificate's id (`Warm::id`, unique across workspaces).  A parent
   with two or more children saves a copy (`Meet::save`), and each child puts it back (`Meet::restore`); the first
   child and a node's own second solve find it still there.  `Meet::derive` then makes the start that a build would
   make:
   * a member forced now stops being tracked, its bit leaving every combination;
   * a member barred now leaves the span (`Rref::remove`);
   * a candidate outside the set keeps its circuit less the members forced now;
   * it becomes independent when its circuit held a member barred now (its expression in the old basis is the only
     one, and used that member);
   * it is a loop when nothing is left of its circuit;
   * anything else (a forced number outside the set, a role going back) falls to the build.

   At 2044 the setup (42.0 s) and the members' adds (10.7 s) became derive (2.2 s) and restore and save (1.1 s).  Nearly
   every warm start derives: all of 2044's, and all but 7 of 988's 26,353 (in the run with timers), the 7 being those
   whose forced numbers include one outside the parent's set.  Tested: a derived start gives the whole bound of a built
   one (value, set, loops, bounds without each member, split) on 6,847 random solves, 5,741 of them derived; removing
   either rule (untracking, or independence after a barred member) fails the test.
6. **Circuits kept across an exchange.**  After an exchange only three things are reduced again: the circuits that held
   a member that left, the members that left, and the independent numbers of a class into which an independent number
   entered (a circuit is a number's unique expression in the set).  Only 36% of the circuits stay, since the members
   that leave are in many circuits, so the reductions at 2044 went from 7.0 to 5.7 s.  In the tests every circuit kept
   or derived is checked against a reduction at every exchange.
7. **Circuits as lists.**  A circuit holds one or two members, yet the bitsets over every number were scanned in the
   arcs, the searches and the checks of `finish`.  As lists, the arcs at 2044 fell from 5.2 to 1.4 s, the searches from
   6.0 to 5.1, and the checks from 1.9 to 1.1.
8. **Combinations over the candidates.**  The rows' combinations run over tracking bits given to the candidates as they
   first appear (18 words at 2044 instead of 32).  The gain is about 5%.  Tested: on families of 100 to 200 numbers
   whose candidates grow over 3 to 4 words, a workspace that saw other roles gives the bounds of a fresh one.

Build v1 on the panel took 299.0 s against master's 801.7 s, with the same nodes on every game but 1584, at 26,507
against 26,516: its pause at 20 s fell elsewhere.  Without the pause (`nodecost`), 1584 gives master's 26,516 nodes and
every counter, in 45.1 s against 124.0 s.

**Soundness.**  The certificate is still checked explicitly: `finish` tests conditions (1) to (3) of the module comment
of [parity.rs](https://github.com/bvchess/taxman/blob/0ef05d1/solver/noframe/src/parity.rs) against the circuits of the
set, and the bound rests on that check and weak duality.  What changed is where the circuits come from.  Before, the
last exchange graph reduced every candidate against the rows; afterward, a circuit may be derived from the parent's or
kept from the last exchange graph, by the rule that a circuit is its number's unique expression in a basis.  The rules
are proved in the comments (`Meet::derive`, `Meet::circuits`) and checked in the tests against a reduction at every
exchange.  The first follow-up below makes the check independent of them.

**Tried and not kept, or not tried:**

* An early cut from the parent's certificate: the bound it gives a child barring member x is `without[x]`, which is
  above the target for every member the parent leaves free (else the parent forces it), so it never cuts a child.
* Heapifying the parity searches' sources, a d-ary or indexed heap, and pivots instead of reductions for the circuits
  that change: not tried; each is worth a few percent at most of what is left.
* Skipping `playable` of the forced picks at a first child (its forced set is its parent's): not tried; about 12% of 8%.

### The profile after (with timers)

2044 took 20.3 s (its search ended before the 20-s pause in this run, so no open unit restarted), and 988 took 21.8 s.

| phase | 2044 s | 988 s |
|---|---|---|
| parity solves, in all | 14.8 | 14.5 |
| - searches for an improving cycle | 4.6 | 5.6 |
| - exchange graphs: circuits by reduction / arcs | 3.7 / 1.2 | 2.5 / 0.9 |
| - derive / restore and save | 1.4 / about 1.0 | 1.3 / 0.4 |
| - solves from scratch after a fallback (setup, augmentations) | 0.7 + 1.2 + part of the graphs | 0.9 + 1.2 + part |
| - the checks of `finish` | 0.9 | 0.9 |
| `playable` of the forced picks | 1.7 | 1.5 |
| matching (incremental: copy, repairs, read) | 1.4 | 3.1 |
| forced picks from the dual, nogood propagation | 0.5, 0.2 | 0.4, 0.9 |
| deletion filter | 0.04 | 0.12 |

A node at 2044 costs about 1.2 ms of parity and 0.3 ms of the other phases listed, on this machine's loaded thread.
What is left is spread: the label-correcting searches, the reductions after exchanges, the fallbacks' solves from
scratch (about 18% of 988's time), and `playable`.

### The panel, before and after

`exact --threads 1` on one loaded thread, after changes 1 to 8 (commits a2e5a06 and 39fd1ea) and before the two
follow-ups.  Every game has the verdict "proven" and the nodes of master.

| game | nodes | master s | after s | ratio |
|---|---|---|---|---|
| 988 | 19,568 | 52.1 | 21.1 | 0.40 |
| 1309 | 17,887 | 84.6 | 31.4 | 0.37 |
| 1347 | 14,393 | 77.2 | 28.4 | 0.37 |
| 1508 | 24,078 | 131.5 | 48.2 | 0.37 |
| 1584 | 26,516 | 139.0 | 36.6 | 0.26 |
| 1771 | 5,553 | 40.0 | 5.9 | 0.15 |
| 1920 | 18,887 | 126.2 | 28.6 | 0.23 |
| 2033 | 2,747 | 31.5 | 5.3 | 0.17 |
| 2044 | 12,546 | 119.6 | 33.9 | 0.28 |
| all | 142,175 | 801.7 | 239.5 | 0.30 |

The seconds include each game's setup (the root's bounds, U\*, the roles), a few seconds at n = 2000, and, for the games
over 20 s, the open units restarted from scratch after the pause.  Per node without them (`nodecost`), 1584 fell from
4.68 to 1.39 ms, 1771 from 5.37 to 0.95, 2033 from 8.37 to 1.68, and 988 from 2.55 to 0.79: 3.4 to 5.6 times less at n
= 1584 to 2044.

### The two follow-ups

The branch was rebased onto 2896cdd (the semiprime relation) without a conflict.  1347 and 2033 are odd semiprimes that
the semiprime formula proves, so `exact` no longer searches them by default; the panel runs after that pass `--all 1`
(`panel2.sh` beside `panel.sh`), which searches them as before.

**The check of the certificate reduces every circuit afresh (12819be).**  The bound must rest on the theorem and weak
duality, not on the rules by which the search keeps or derives circuits.  So `finish` reduces the circuit of every
candidate against the rows before it checks conditions (1) to (3) and computes the bounds without each member, and it
confirms each loop it reports (a number it says depends on the forced ones alone) by a reduction, its combination of
tracked members empty; a failure makes the solve fall back.  A fallback after a derived start builds its forced numbers
and loops afresh: before, it reused the derived loops, which a test found when a spoiled circuit made a derived loop
wrong and the solve came out uncertified.

* Test: with one circuit of the put-back state spoiled (a member dropped or added, or the number made independent),
  every child's bound and its bounds without a member equal enumeration; 488 of 1,659 spoiled starts fell back.  With
  the fresh reduction removed, the test fails on a bound of 65 against the truth of 83: a spoiled circuit does reach
  the bound without it.
* Same trees: the searches without a pause (`nodecost`) give master's nodes, counters and every parity statistic at 798,
  864, 988, 1584, 1771 and 2033, and the panel gives master's nodes on every game.
* Cost, alternating the build before it and this one, two runs each (search seconds):

| game | before | after | cost |
|---|---|---|---|
| 988 | 19.7, 19.1 | 21.3, 21.5 | +10% |
| 1771 | 5.2, 4.2 | 6.3, 6.4 | +35% |
| 2033 | 4.5, 3.4 | 5.4, 5.5 | +38% |

The pass of reductions is fixed work a solve, so it weighs most where a solve is cheap: at large n with few exchanges.
On the panel (one run each) 203.3 s became 234.3 s, +15%, within the noise of single runs here.

**`exact` pauses for the warm-up only when the Lagrangian bound will be turned on (f0c9973).**  The pause existed for
the Lagrangian bound, which is off with the parity bound, yet every search over 20 s paused and restarted its open units
with a matching and a parity solve from scratch: 41 to 57 units at 2044, by where the pause fell.  Worse for a proof's
record, the tree then depended on the clock: 1584 took 26,507 nodes in one build and 26,516 in master and the final
build.  A search that will not turn the bound on runs to its end or to `--seconds`.  The pause at `--seconds` and the
checkpoint are as before: 1771 with `--seconds 6` paused after 5,376 nodes with 23 open units, saved its checkpoint, and
the next run finished it (5,553 nodes in all).  One thing went: after a pause at the deadline such a search used to run
its open units again for a few hundred nodes before saving the checkpoint; it saves at once.

* Run to run: two runs of 1584 gave 26,516 nodes each (42.5 and 42.3 s) and two of 2044 12,546 each (22.5 and 27.5 s),
  with the final build; every panel game gave master's nodes in both builds since this change.  These are also the
  counts of the searches without a pause, so `exact`'s trees are those of `nodecost`.
* The panel, `exact --threads 1 --all 1`, seconds on one loaded thread:

| game | nodes | master | pause, before the follow-ups | no pause (f0c9973) | no pause, fresh check (12819be) |
|---|---|---|---|---|---|
| 988 | 19,568 | 52.1 | 21.1 | 20.8 | 22.0 |
| 1309 | 17,887 | 84.6 | 31.4 | 27.8 | 28.7 |
| 1347 | 14,393 | 77.2 | 28.4 | 25.4 | 26.7 |
| 1508 | 24,078 | 131.5 | 48.2 | 36.7 | 52.5 |
| 1584 | 26,516 | 139.0 | 36.6 | 35.5 | 42.5 |
| 1771 | 5,553 | 40.0 | 5.9 | 5.8 | 6.8 |
| 1920 | 18,887 | 126.2 | 28.6 | 21.9 | 26.5 |
| 2033 | 2,747 | 31.5 | 5.3 | 4.9 | 6.0 |
| 2044 | 12,546 | 119.6 | 33.9 | 24.5 | 22.5 |
| all | 142,175 | 801.7 | 239.5 | 203.3 | 234.3 |

Dropping the pause saved most at the games whose searches passed 20 s with many open units (2044 from 33.9 to 24.5 s,
1508 from 48.2 to 36.7, 1920 from 28.6 to 21.9).  Single runs on this loaded machine differ by up to a third (2044: 22.5
and 27.5 s for the same build and tree), so the last column's rise over the one before it is the check's cost measured
above, blurred by that noise.

**Checks.**  `cargo fmt --check` and `cargo clippy --all-targets` are clean; the parity, game and upper tests,
`--test exact` and the frame crate's docs test pass.

## Decision

* **Kept: all four commits**, on master.  They change no verdict and no node count (the panel, and the fingerprints of
  798, 864, 988, 1584, 1771 and 2033), and the panel takes 234.3 s against master's 801.7 s with the fresh check,
  203.3 s without it.
* **Open, each a candidate for a later entry.**  Each can return another heaviest set where several tie, so each can
  change a tree and is judged by node counts as well as seconds.
  * *Warm-start fallbacks.*  3.5% (2044) to 8.6% (988) of the warm starts give up on a negative cycle away from the root
    (after 20 scans a vertex on average) and solve from scratch, 22 to 54 augmentations each: about 18% of 988's time
    after this work.  Canceling the cycle (a Bellman-Ford pass from the warm state, or a larger budget) would keep
    most of them warm.
  * *Cold restarts of units.*  The cloud's passes of 300 s restart their open units from scratch at every pass, as the
    pause at 20 s did (a matching and a parity solve each), and a search resumed from a checkpoint restarts its units
    the same way.
  * *A unit's first node.*  A restarted unit's matching from scratch costs about 0.22 s at 2044, because t's potential
    lies about BIG below the right vertices' while forced picks are unmatched.  A checkpoint that kept each unit's
    matching and certificate would let it start warm, with other duals or sets where they tie.

## Files

`panel.sh`, `panel2.sh` and `compare.sh` take the folder that holds `runs/` from the environment variable
`NODECOST_DIR`, or the folder of the script; `compare.sh` needs `jq`.  `nodecost.rs` is a scratch example, not
committed.

* `panel.sh BINARY LABEL [GAMES]`: the panel, one game at a time on one thread at nice 19; writes `runs/LABEL/out.jsonl`
  (`exact`'s lines) and `runs/LABEL/N.err` (stderr: the profile, in a build with the feature `profile`).  The default
  games are the nine.
* `panel2.sh BINARY LABEL [GAMES]`: the same with `--all 1`, for builds on 2896cdd and later.
* `compare.sh BASE LABEL...`: one row a game, with the verdict, nodes and seconds of each run, whether its verdict and
  nodes equal BASE's, and its seconds as a ratio of BASE's.
* `nodecost.rs`: copy it to `solver/noframe/examples/` of the prover and build it with `cargo build --release --example
  nodecost`; `nodecost N...` prints the fingerprint of each game.  It was built and run on fdc4e62 and on the branch
  rebased onto 2896cdd; the functions it calls (`Prover::new`, `with_parity`, `run_units`, `parity_stats`) exist at
  0ef05d1 too, where it was not rebuilt.
* `v4-instrumented.patch`: the timers and counters behind the feature `profile`, with the changes as of the fourth
  build (`git apply` on fdc4e62; build with `--features profile`).
* `fingerprint-master.txt`: `nodecost 798 864 1771 2033 988` on master fdc4e62.  `fingerprint-master-1584.txt`: the same
  for 1584.  `fingerprint-final.txt`: the final build before the follow-ups on 798, 864, 1771, 2033, 988 and 1584.  The
  final build differs from master's in the seconds and in one added field of the parity statistics, `derived`, and in
  nothing else.

## Commits

On master of [bvchess/taxman](https://github.com/bvchess/taxman), all 2026-10-31:

* a2e5a06: the deletion filter dismantles only the residual; the matching's search from scratch stops at the cheapest
  path, its sources heapified (changes 1 and 4).
* 39fd1ea: the parity solves derive their start from the parent's state (`Meet::save`, `Meet::restore`,
  `Meet::derive`), circuits as lists kept across exchanges, combinations over the candidates only, forced rows without
  combinations, one reduction an add, the split from the last search (changes 2, 3 and 5 to 8).
* f0c9973: `exact` pauses for the warm-up only when the Lagrangian bound will be turned on.
* 12819be: the parity bound's check reduces every circuit afresh, and confirms each loop by a reduction.
