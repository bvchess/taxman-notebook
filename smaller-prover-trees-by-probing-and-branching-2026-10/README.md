# Smaller prover trees by probing and branching (2026-10)

Part of the [lab notebook](../README.md).

Started 2026-10-31.  Concluded 2026-10-31.

**Question.**  The prover's search grows tenfold per 210 points of the root's parity gap ([the proofs
guide](https://github.com/bvchess/taxman/blob/0ef05d1/solver/noframe/docs/proofs.md#to-2175-on-a-cloud-machine)).  Which
set a node branches on, in what order, and what it can bar or force before branching decide the tree.  Can any of them
cut the nodes of the panel, soundly?
**Answer.**  Yes, by two changes that together cut the nine-game panel from 125,500 nodes and 195.3 s to 21,218 nodes
and 40.4 s, and 24 games from 352,294 nodes to 45,965.  *Probing* bars every number outside a node's heaviest set whose
forcing alone brings the parity bound to the target; it is read from the certificate with no extra solve, and alone it
gives 31,803 nodes and 35.8 s on the panel.  *Branching* learns up to four conflicts of the node's set that share no
free member, and branches on the one with the smallest expected tree.  The gain grows with the gap: games 1548, 1587
and 1612 (gaps 458, 484 and 443) took 10 to 15 times fewer nodes and 11 to 18 times fewer seconds.  Game 1475 (gap 590),
which took 6.3 million nodes in the committed run, was still unfinished after 2,400 s.  Both changes are kept, and the
searches from one below the recorded score still find a set worth the score on the games checked.

## Method

**Terms.**  A node's *target* is the score the search must beat; the node is cut when its parity bound is at or below
it, and its *gap* is its bound less the target, in points.  When the node's heaviest set is unplayable, a *conflict* is
a minimal unplayable subset of it, found by the deletion filter (`Board::minimal_unplayable`).  A completion must leave
out some member of a conflict, so the children partition on which: each child bars one *free* member of the conflict,
one that is not forced.  A *nogood* is a conflict the search stores and reuses at every node.  *Probing* bars a free
number outside the heaviest set when forcing it alone brings the parity bound to the target.  The *bound without a
member* is the parity bound with that member barred (`Bound::without`, read from the certificate).

* **Build and runs.**  Release builds of the prover's `exact`, one game at a time on one thread at nice 19 with default
  options (the roles of [the bottom-layers theorem
  (F4)](https://github.com/bvchess/taxman/blob/0ef05d1/docs/theory/frame-model.md#the-bottom-layers-theorem), the
  parity bound): `panel.sh BINARY LABEL GAME...` runs `exact --from N --to N --threads 1 --out out/LABEL-N.jsonl
  --checkpoints ckpt/LABEL-N`.  Node counts are exact; seconds are those of one thread beside the chain and vary up to
  40% from run to run, except in the tables marked as run alternately on a quiet machine.
* **The panel.**  Games 1000, 1040, 1196, 1771, 2030 and 2044, which took 2 to 60 s on the cloud machine (8.9, 31, 25,
  11, 11 and 43 s) and spread over n, and 1309, 1508 and 1920, whose master numbers the project's owner had given (the
  nodes agree).
* **Study knobs.**  A temporary environment variable `PB` (`"probe=1,learn=1,order=1,fresh=2,pick=1"`), read in
  `Prover::new`, let one binary run every variant.  It is not in the commits, and the study builds are not kept; the
  legend is in Files.
* **The base.**  Master was fdc4e62 for the screening, and 12819be for the final tables, after [the work on the cost of
  a node](../cheaper-prover-nodes-same-trees-2026-10/README.md) had merged: master's residual-only deletion filter
  replaced the study's bisecting filter and scratch dismantler, its order gained a `hold` argument (forced members
  tried last), and the circuits of `parity.rs` were lists, which `forcing_cut` reads.  Master's node counts did not
  change in that work, and its seconds fell 3 to 4 times.

## Results

### The baseline

| game | nodes (fdc4e62) | seconds | nodes (master2) | seconds |
|---|---|---|---|---|
| 1000 | 7,958 | 18.3 | 7,958 | 18.8 |
| 1040 | 17,622 | 53.7 | 18,026 | 52.8 |
| 1196 | 16,904 | 49.0 | 16,904 | 49.2 |
| 1771 | 5,553 | 20.3 | 5,553 | 30.5 |
| 2030 | 3,661 | 39.6 | 3,661 | 32.0 |
| 2044 | 12,546 | 117.5 | 12,546 | 94.8 |
| 1309 | 17,887 | 83.9 | 17,887 | 76.2 |
| 1508 | 24,078 | 132.5 | 24,078 | 129.3 |
| 1920 | 18,887 | 128.7 | 18,887 | 111.1 |
| sum | 125,096 | 643.5 | 125,500 | 594.8 |

`exact` paused every search at a 20-s warm-up and restarted the open units from scratch, even with the parity bound,
for the Lagrangian bound's sake, so the tree of a game over 20 s depended on the clock.  For measurement only, master2
is fdc4e62 with the warm-up taken out when the Lagrangian bound is off, the change that the work on the cost of a node
committed as f0c9973; it differs from fdc4e62 only at 1040, 18,026 nodes against 17,622.  A study binary with no knob
set reproduces fdc4e62's node counts exactly.  The first screen below is against fdc4e62, the later tables against
master2.

### Screening on the first base (the games 1000, 1771, 2030, then 1040, 1196, 2044)

Node ratios against master, summed over the games.

| variant (knobs) | 1000 / 1771 / 2030 | 1040 / 1196 / 2044 |
|---|---|---|
| bisecting filter (same result, fewer peels) | 1.00 | |
| learn=1 (learn the disjoint conflicts of the set) | 0.59 | |
| learn=1, order=1 (dearest child first) | 0.52 | |
| probe=1 (bar non-members whose forcing alone brings the bound to the target) | 0.29 | 0.25 |
| probe=1, learn=1 | 0.17 | |
| probe=1, order=1 | 0.25 | |
| probe=1, order=3 (cheapest child first) | 0.53 | |
| probe=1, order=2 (descending numbers) | 0.63 | |
| probe=1, learn=1, order=1 | 0.14 | 0.08 |
| probe=1, learn=1, order=1, fresh=2 (the filter removes free members first) | 0.11 | 0.06 |

The last row is 0.074 over all six games (1,939 + 2,824 of 17,172 + 47,072 nodes); the ratios of the second group and
the last row are computed from the run outputs.  Probing alone cuts the nodes to 0.29 and 0.25 of master's, learning
alone to 0.59, and all of them together to 0.11 and 0.06.

### Choosing the conflict: the weight

The study's rule `pick=1` takes, among the conflicts inside the set (stored or fresh), the one with the least weight,
the sum over its free members of 10^((bound without the member − target) / slope).  A child barring a member has a gap
of that bound less the target, and a search grows tenfold per 210 points of gap, so the weight estimates the size of
the conflict's tree.  The frame solver's [conflict
branching](https://github.com/bvchess/taxman/blob/0ef05d1/solver/docs/design/search.md#conflict-branching) weighs a
conflict the same way, with the slope 291.  With B for probe=1, learn=1, order=1, fresh=2, pick=1, on 1508, 1309 and
1196 (master2: 24,078 + 17,887 + 16,904 = 58,869 nodes):

| variant | 1508 | 1309 | 1196 | sum | ratio to master2 |
|---|---|---|---|---|---|
| B, slope 210 | 10,935 | 4,214 | 757 | 15,906 | 0.27 |
| B, slope 100 | 7,821 | 4,383 | 792 | 12,996 | 0.22 |
| B, slope 50 | 5,798 | 4,581 | 845 | 11,224 | 0.19 |
| B, slope 25 | 4,619 | 4,885 | 848 | 10,352 | 0.18 |
| B, slope 10 | 4,824 | 4,616 | 877 | 10,317 | 0.18 |
| B, slope 400 | 11,113 | 5,286 | 755 | 17,154 | 0.29 |
| B, slope 210, learn=2 | 7,782 (102 s) | 1,814 | 669 | 10,265 | 0.17, 1.4 times the seconds |
| B, slope 210, probe=2 | 9,296 (766 s) | 3,983 | 729 | 14,008 | 0.24, 4 ms a probe |

A small slope makes the choice lexicographic on the members' bounds, largest first: the conflict whose cheapest member
to leave out is dearest.  A first production version that compared (largest bound, number of free members) instead took
1508 to 15,373 nodes: the cheapest member is often the same number in several conflicts, so the tie decides, and fewer
members is the wrong tie-break.  Comparing the whole descending list is the fix, and it is what "the lexicographic
rank" means below.

### The study rebuilt on master 12819be

The panel on the rebuilt study, alternating master and the build per game, one thread, a quiet machine (nodes, seconds):

| game | master | probing only | probing and branching (package A) |
|---|---|---|---|
| 1000 | 7,958  7.7 | 2,689  2.3 | 1,422  1.6 |
| 1040 | 18,026  24.3 | 5,161  4.6 | 1,965  2.5 |
| 1196 | 16,904  16.5 | 4,437  2.7 | 880  1.1 |
| 1771 | 5,553  7.0 | 1,234  1.8 | 276  1.1 |
| 2030 | 3,661  8.1 | 1,137  2.4 | 504  1.7 |
| 2044 | 12,546  28.0 | 1,990  3.7 | 229  1.4 |
| 1309 | 17,887  30.2 | 5,123  5.6 | 4,616  5.9 |
| 1508 | 24,078  50.9 | 4,180  6.3 | 4,817  9.2 |
| 1920 | 18,887  27.1 | 5,852  6.4 | 823  2.0 |
| sum | 125,500  199.7 | 31,803  35.8 | 15,532  26.5 |

Master's 1040 is 18,026 here, and was 17,622 in the first screen, which came before the warm-up change.  Package A is
what the first rebuilt study did: learn the disjoint conflicts (up to 16), hold forced members last in the filter,
choose the conflict by the lexicographic rank (largest bound without first), and order the children dearest first.

### The ablations of package A

On 1508, 1309, 1920, 1040 and 2044, probing always on (sum of nodes; probing alone is 22,306 nodes, 25.7 s):

| variant | nodes | seconds |
|---|---|---|
| A, all of the package | 12,450 | 21.1 |
| A, no learning (cap 1) | 20,972 | 28.7 |
| A, the filter without `hold` | 13,239 | 21.7 |
| A, children in ascending numeric order (no sorting by price) | **10,035** | 17.3 |
| A, children cheapest first | 12,522 | 20.7 |
| A, children descending numeric | 16,148 | 27.0 |
| A, the conflict with the fewest free members (master's rule) | 22,865 | 47.6 |
| ascending, no `hold`, learning 16 | 11,083 | 17.8 |

With the children ascending, the cap on the conflicts learned gives:

| cap | 1 | 2 | 3 | 4 | 6 | 16 | 32 |
|---|---|---|---|---|---|---|---|
| nodes | 17,447 | 10,330 | 9,650 | 9,288 | 10,505 | 10,035 | 10,035 |

* **The order of the children.**  Dearest first won before probing (0.14 of master's nodes against 0.17 in the first
  screen) and loses with it, 12,450 nodes against 10,035, so the children stay in ascending order, master's.
* **Learning** matters: the nodes are 1.7 times higher with a cap of 1 than of 16.  Any cap from 2 to 32 does about
  the same; 4 is used.

### The rule for the conflict, on 24 games

The choice of the conflict is game-dependent and swings single games by factors of 3 to 7 either way.  On 1575, 1584 and
1600, master's rule (fewest free members) takes 2,692, 3,441 and 1,757 nodes, and the lexicographic rank 18,803,
11,574 and 7,767.  On 1508 the rank takes 2,380 nodes, master's rule with the children ascending 9,470, and with the
children dearest first 14,771.  The weight over the free members, 10^(g / slope) with g the bound without the member
less the target, over 24 games (the nine of the panel, and 936, 950, 988, 1100, 1190, 1225, 1254, 1280, 1575, 1584,
1600, 1770, 1912, 2025 and 2040; master's total is 352,294 nodes), with the children ascending and learning capped at 4:

| rule | nodes | seconds |
|---|---|---|
| lexicographic rank | 69,196 | 103.4 |
| fewest free members | 49,652 | 75.1 |
| weight, slope 210 | **45,965** | 75.2 |
| weight, slope 400 | 46,525 | 72.9 |

* **The slope.**  Slope 210, the measured growth, is used.  On 1575, 1584, 1600, 1508 and 1309 together the weight with
  slope 25 takes 35,440 nodes (1508: 2,218; 1575: 15,515) against 19,667 for slope 210 (computed from the run
  outputs; slope 100 gives 26,343, slope 400 19,101, and the fewest free members 19,975).
* **The worst game.**  The weight's worst game of the 24 is 1508, with 10,956 nodes against 2,380 for the rank.
* **The cap and the filter**, with the weight rule: learning capped at 1, 2, 4 and 8 gives 80,740, 49,548, 45,965 and
  45,594 nodes over the 24 games, and the filter without `hold` 53,428.

### The final build

Commits 7c916de (probing) and 0ef05d1 (learning and the weighted choice), on master 12819be.  The nine-game panel,
alternating master and the final build per game, one thread, a quiet machine (nodes, seconds):

| game | master | final |
|---|---|---|
| 1000 | 7,958  7.3 | 1,326  1.5 |
| 1040 | 18,026  24.8 | 2,186  2.7 |
| 1196 | 16,904  15.6 | 1,918  2.0 |
| 1771 | 5,553  6.8 | 554  1.3 |
| 2030 | 3,661  8.3 | 315  1.5 |
| 2044 | 12,546  26.9 | 459  1.7 |
| 1309 | 17,887  28.0 | 2,479  1.8 |
| 1508 | 24,078  51.0 | 10,956  25.6 |
| 1920 | 18,887  26.5 | 1,025  2.2 |
| sum | 125,500  195.3 | 21,218  40.4 |

Probing alone (commit 7c916de) is 31,803 nodes and 35.8 s, against 199.7 s for master in that run (the table above).
The final build has fewer nodes and more seconds than probing alone, because of 1508 (10,956 nodes and 25.6 s against
4,180 and 6.3 s).  On the panel alone the lexicographic rank is ahead of the weight, with 13,252 nodes and 19.5 s
(computed from the run outputs; 1508 takes 2,380); over the 24 games the weight is ahead, 45,965 nodes against 69,196,
and it was chosen for that total.  Over the 24 games, master's 352,294 nodes became 45,965 (0.13).

**The high-gap games.**  Games 1548, 1587 and 1612, whose gaps are 458, 484 and 443 and whose master searches take
130,000 to 200,000 nodes, with `exact --seconds 1500`, one thread, master and then the final build:

| game | master nodes | seconds | final nodes | seconds |
|---|---|---|---|---|
| 1548 | 131,571 | 256.7 | 12,771 | 23.7 |
| 1587 | 163,998 | 202.7 | 12,747 | 11.6 |
| 1612 | 195,765 | 297.5 | 13,212 | 20.2 |
| sum | 491,334 | 756.9 | 38,730 | 55.5 |

The nodes fall 10.3, 12.9 and 14.8 times, and the seconds 10.8, 17.5 and 14.7 times.

**Game 1475** (gap 590; the committed run took 6.3 million nodes).  The final build had not finished it after 305,664
nodes and 900 s (2.45 to 3.3 ms a node, 10,785 nogoods of about 38 members at the checkpoint).  After 2,400 s of one
thread it had searched 564,224 nodes, with 75 open units (145 at 183,296 nodes and 140 at 305,664), and was not
finished.  A node scans the whole nogood table several times (propagation, learning, the choice), which a long search
pays for; an index of the nogoods by their members is the next cost to cut, and has nothing to do with branching.

### Soundness

**Probing** (proved in the commit message of 7c916de and the module comment of `Meet::forcing_cut` in
[parity.rs](https://github.com/bvchess/taxman/blob/0ef05d1/solver/noframe/src/parity.rs)).  Let S be the node's heaviest
set, independent at both parities, and y a number outside it.  In each parity class, the heaviest independent set that
holds y is S with y added, less the lightest member of y's circuit in S if S + y is dependent: the heaviest basis
through an element of a matroid is the heaviest basis exchanged with it, and the independent sets of any size are the
bases of the matroid padded with dummies of weight 0.  By weak duality, a set independent in both classes that holds y
weighs at most the bound plus, for each class, the split weight of y less the least split weight over y's circuit in S
(nothing if S + y is independent).  When that is at most the target, no set that beats the target holds y, so the node
bars y.  The test reads the circuits and the weight split of the certificate, so it costs no further solve.  This is
the converse of the forced picks, the idea that [the entry on forcing the certified
members](../forcing-the-certified-members-in-the-prover-2026-10/README.md) left open.

**Branching.**  Every choice is among conflicts of the node's set, so every partition is exact and every conflict
learned is a nogood whatever the roles.  The deletion filter's test compares the filter with the plain one in the same
order.

**Checks.**

* [`examples/paritycheck.rs`](https://github.com/bvchess/taxman/blob/0ef05d1/solver/noframe/examples/paritycheck.rs)
  runs the search against the target one below the recorded score and must find a playable set worth the score, which
  replays by the rules; a bound or a pruning rule that cut an optimal game would make it fail.  The probing-only build
  passed on the nine panel games and on the 62 games of 187..1000 step 3 that need a search.  The final build passed on
  the nine panel games and 1575, 1584 and 1600 (12 games), and on 96 more: the same 62 games and the 34 games of
  1001..1400 step 7 that need a search.
* Tests: `game::` (11), `parity::` (6; `check_forcing` compares `forcing_cut` with enumeration at the first and last
  candidate outside the set, cold and warm), `tests/exact` (3), the docs test (31).  `cargo fmt` and clippy are clean.
  The pause test of `game.rs` moved from game 600 to 930, because with the rules the search of 600 is too short to
  pause twice.  The intersection test of `parity.rs` takes 19 s and the pause test 12 s, both over the 3-s limit
  before this work too.

### Tried and not kept

* **Exact probing** (probe=2: solving with the 8 candidates nearest the target forced, those within 40 points of the
  bound's estimate).  27% of the near misses are bars, but a probe is a solve of about 4 ms: 1508 took 766 s against
  69 s, for 15% fewer nodes.
* **Learning also the conflicts that avoid each free member of the smallest** (learn=2).  1508 took 7,782 nodes against
  10,935 and 1309 1,814 against 4,214, but the seconds were 1.4 times higher with the filter of that day; not rebuilt
  on the faster filter.
* **A packing cut on the parity bound**: the bound less, for conflicts of the set disjoint in their free members, the
  least drop of a member of each.  It is sound, because lowering the split weights of any set of members keeps S
  optimal, so the drops add.  It cut 0 of 1,775 and 0 of 1,068 branching nodes with the conflicts in the nogood table,
  and 0 of 1,218 and 568 with up to 12 disjoint conflicts a node: the conflicts' cheapest members are too cheap, as in
  the frame solver's screen.
* **The order of the children**: dearest first loses with probing (12,450 nodes against 10,035 for ascending);
  cheapest first and descending numbers do worse in the first screen (0.53 and 0.63 of master's nodes against 0.29 for
  probing alone) and in the ablation (12,522 and 16,148 nodes).
* **The ranks of the conflict**: the lexicographic rank, and the rank by (largest bound, number of free members), are
  worse in total than the weight; see the 24 games.
* **A small slope**: slope 25 does well on 1508 (2,218 nodes) and badly on 1575 (15,515), and takes 35,440 nodes on
  five games against 19,667 for slope 210.

## Decision

* **Kept: probing (7c916de) and the learned, weighted branching (0ef05d1).**  The panel falls from 125,500 to 21,218
  nodes and the 24 games from 352,294 to 45,965, and the nodes of the games with the highest gaps by a factor of 10 to
  15.
* **What would reopen the choice of the conflict:** a rule that does not swing single games by factors of 3 to 7 (1508
  is 2,380 nodes under the rank and 10,956 under the weight; 1575 is 2,692 under master's rule and 18,803 under the
  rank).
* **Next cost:** the nogood table scanned several times a node, which games like 1475 pay for.

## Files

The scripts read the folder named by the environment variable `STUDY_DIR`, or the folder of the script, which holds the
builds they run (`exact-study`, `exact-abl`, `exact-abl2`, `exact-abl3`, `exact-master2`, `exact-master3`, `exact-v6`)
and where they write `out/LABEL-N.jsonl`, `out/LABEL-N.log` and `ckpt/`.  The builds, with the knob code of the study
builds and the run outputs, are not kept; the scripts record which variant ran on which games.

* `panel.sh BINARY LABEL GAME...`: one game at a time, one thread, nice 19.
* `variant.sh BINARY LABEL PB-SETTINGS GAME...`: the same with the knobs of the variable `PB` (`-` for none).  Every
  script below runs it.
* `ab.sh LABEL_A BIN_A LABEL_B BIN_B GAME...`: two builds alternately, one game at a time, as the tables of master
  against a build were made.
* `base2.sh`: master2 on the nine games (the second baseline).
* `screen1.sh`, `screen2.sh`, `screen3.sh`, `screen4.sh`: the first screening on 1000, 1771, 2030 (1 and 2), on 1040,
  1196, 2044 and on both groups with `fresh=2` (3), and `probe=1, learn=1, order=1, fresh=2` with and without `pick=1`
  on 1309, 1508, 1920 (4).
* `screen5.sh`, `screen6.sh`: the choice of the conflict on 1508, 1309, 1196: slopes 100 and 400, `learn=2`, `probe=2`
  (5), slopes 50, 25 and 10, and slope 100 with `learn=2` (6).
* `abl1.sh`, `abl2.sh`, `abl3.sh`: the ablations of package A on 1508, 1309, 1920, 1040, 2044: the package, learning,
  `hold`, the orders and the rank (1), more orders and caps (2), caps 1, 2, 3 and 6 (3).
* `abl4.sh`: the same variants on 1575, 1584, 1600.
* `abl5.sh`: the slopes 25, 100, 210 and 400 of the weight, and master's rule, on 1575, 1584, 1600, 1508, 1309.
* `abl6.sh`, `abl7.sh`: the four rules for the conflict on the 24 games (6), and the weight with learning capped at 1, 2
  and 8 and without `hold` (7).
* `pcheck2.sh BINARY LABEL`: `examples/paritycheck.rs` built as BINARY on the panel and 1575, 1584, 1600, then on the
  sweeps of 187..1000 step 3 and 1001..1400 step 7 (the final build's check); the lines go to
  `out/LABEL-panel.jsonl`, `out/LABEL-sweep1.jsonl` and `out/LABEL-sweep2.jsonl`.  `pcheck.sh` is the same for an
  earlier build, on the panel and the sweeps of 187..1000 step 3 and 1001..1400 step 5.
* `hard2.sh`: games 1548, 1587 and 1612 with `--seconds 1500`, the final build and master, one after the other.
* `table.py LABELS GAMES`: with LABELS and GAMES comma-separated, prints nodes, seconds and the ratio of nodes to the
  first label, for each game and in sum.  The numbers marked "computed from the run outputs" above came from it.

**Knobs of `PB`.**  The screening build `exact-study`: `probe=1` probing, `probe=2` exact solves of the 8 candidates
nearest the target; `learn=1` the disjoint conflicts of the set, `learn=2` also the conflicts that avoid each free
member of the smallest; `order=1` the children dearest first, `order=2` descending numbers, `order=3` cheapest first;
`fresh=2` the filter removes free members first; `pick=1` the conflict of least weight; `slope=S` the S of the weight.
The ablation builds, with probing always on: `learn=0` one conflict only; `hold=0` the filter without `hold`; `order=0`
ascending numbers, `1` dearest first, `2` cheapest first, `3` descending numbers; `rank=0` the fewest free members,
`1` the lexicographic rank, `2` the weight; `cap=N` the most conflicts learned; `slope=S`.  With no knob set, a
build runs its package.

## Commits

On master of [bvchess/taxman](https://github.com/bvchess/taxman), both 2026-10-31:

* 7c916de: the prover bars the numbers whose forcing alone brings the parity bound to the target (`Meet::forcing_cut`).
* 0ef05d1: a node learns several conflicts of its set and branches on the one with the smallest expected tree; the
  deletion filter holds the forced members last.
