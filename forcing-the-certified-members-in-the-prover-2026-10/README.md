# Forcing the certified members in the prover (2026-10)

Part of the [lab notebook](../README.md).

Started 2026-10-31.  Concluded 2026-10-31.

**Question.**  The prover's `upper` program certifies, game by game, the members of U\* of layers 3 and up that every
set beating the recorded score must play: it bars one member at a time, and the member is certified when the parity
bound falls to the score or below ([the barred bound
(W2)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/parity-bound.md#the-barred-bound), [the upper part,
game
by game](https://github.com/bvchess/taxman/blob/2896cdd/solver/noframe/docs/proofs.md#the-upper-part-game-by-game)).
Does `exact` search fewer nodes if it starts from the roles of [the bottom-layers theorem
(F4)](https://github.com/bvchess/taxman/blob/2896cdd/docs/theory/frame-model.md#the-bottom-layers-theorem) with every
certified member forced as well, and if the certification is repeated with those members forced, round after round?
**Answer.**  No.  Games 1309, 1508 and 1920 took the same numbers of nodes with and without the forced members: 17,887,
24,078 and 18,887.  Two reasons explain it, both proven: the repetition certifies nothing after its first round, and the
search already forces the same members at its root.  Not kept; the code was never merged.

## Method

**The change.**  Commit df9f8ce (2026-10-31, branch `prover-certified`, deleted) added:

* `upper::certify` in `solver/noframe/src/upper.rs`.  It bars each member of U\*_{≥3} from the starting roles
  and certifies the members whose parity bound is at most the target V, or whose barring is infeasible.  With its
  iteration on, it forces the certified members, bars the members still open again, and repeats until a round certifies
  nothing.  It returns the roles with the certified members forced, the number of rounds and the number of members the
  first round certified.
* `exact --fix-certified 1` (off by default), which searches from the roles of F4 with the certified members forced.
  The search is a proof, because every set that beats V and obeys F4 holds each certified member: if some set beats V,
  an optimal set does, and it holds them all.  A certificate is relative to its target, so `exact` certifies against
  the target it searches, the recorded score.
* `upper --iterate 1`, which writes the same certification game by game, and tests that check it against every
  playable set that obeys F4.

The patch of that commit, against fdc4e62, is `forcing-df9f8ce.patch` in this folder; `git am` on fdc4e62 gives the
commit back.  It holds the text written for the prover's proofs guide as well.

**The comparison.**  `exact` on games 1309, 1508 and 1920, one thread, release build, from the roles of F4 alone and
with `--fix-certified 1`:

```
./target/release/exact --list 1309,1508,1920 --fix-certified 1 --out C.jsonl
./target/release/upper --list 1309,1508,1920 --iterate 1 --out ITER.jsonl
```

The first line is the forced run (the run from the roles of F4 alone is the same command without the flag), and the
second the certification in rounds.  The result lines are not kept.

**Where the iteration was checked.**  The tests on boards 2..60 at the claims V, V − 1, V − 2 and V − 5, and `upper
--iterate 1` on boards 2..400 and on the 61 searched games of 1301-1400.

## Results

| game | nodes from the roles of F4 | nodes with the certified members forced |
|---|---|---|
| 1309 | 17,887 | 17,887 |
| 1508 | 24,078 | 24,078 |
| 1920 | 18,887 | 18,887 |

* **The iteration finds nothing after its first round.**  Checked on boards 2..60 at the four claims, and by `upper
  --iterate 1` on boards 2..400 and on the 61 searched games of 1301-1400: 0 members gained after round 1, and 2 rounds
  each, the second certifying nothing.  The iteration costs about three times one round.
* **The certification itself is cheap and changes nothing.**  On the three games it took 1.4 to 2.7 seconds
  (`certify_secs`), and they have 373, 436 and 565 members, of which it certified 368, 431 and 554.

**Why the iteration finds nothing** (proven).  The parity bound is the exact maximum over the sets independent at both
parities, within the roles.  Let C be the certified members, and u a member that is still open, so that the bound with
u barred is above V.  Some heaviest set H lacks u and weighs more than V.  H holds every member c of C, since a set that
lacks c weighs at most V.  So forcing C leaves H allowed, the bound with u barred stays where it was, and u stays open.
The proof uses that the bound is an exact maximum, and says nothing of a bound that is not.

**Why the search does not need it** (proven).  At every node, the root included, the search's propagation forces each
free member of the parity bound's heaviest set whose barring alone brings the bound to the target, and repeats until
nothing more is forced (lines 1072 to 1111 of
[solver/noframe/src/game.rs](https://github.com/bvchess/taxman/blob/2896cdd/solver/noframe/src/game.rs)).  A member is
certified when barring it alone brings the parity bound to the target, or makes the node infeasible, so that
propagation is the certification at the root.  A search started from the forced roles starts where the search from the
roles of F4 arrives after its root, and both take the same nodes.  The prover's [proofs
guide](https://github.com/bvchess/taxman/blob/2896cdd/solver/noframe/docs/proofs.md) already said that a node forces
the members whose barring alone brings the bound to the target.

## Decision

* **Not kept.**  The forced members change no node count, and the iteration gains no member.  The code was not merged
  and its branch is deleted; the patch in this folder is its record.
* **What survives is an idea, untested:** barring a free number whose forcing alone brings the parity bound to the
  target.  No set that beats the target can hold it, so it can be barred, which is the converse of the forced picks.
  It goes to the work on the prover's branching.
* **What would reopen it:** a bound that is not an exact maximum, for which the first reason does not hold.

## Files

* `forcing-df9f8ce.patch`: the patch of the unmerged commit df9f8ce, against fdc4e62 (`git format-patch`, 936 lines).
  It changes `solver/noframe/src/upper.rs`, `src/bin/exact.rs`, `src/bin/upper.rs`, `tests/exact.rs`, and
  `docs/proofs.md` and `docs/reproducing.md` of the prover.

## Commits

* df9f8ce (2026-10-31): the change, against fdc4e62 (2026-10-30).  It was never merged, and its branch is deleted, so
  `git show df9f8ce` may not find it; the patch is its record.
