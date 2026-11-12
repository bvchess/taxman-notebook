# E13, the transfer proof: sizing, and two measurements

Run on batmobile on 2026-11-11, 09:24 to 10:13 PST, from the branch `loops-e6` of the research repository (never
pushed), with E6's example `obligation` (commit 3133af1; the binary here).  Nothing here ran longer than its 30-minute
limit, and the proof tree the block needs was not started: it is far beyond the hour that needs approval first.

## The question

The study's E13 (Sections 12 and 14): at an exchange n, the proof tree of n − 1 is a proof of n at every node whose cut
has a core without x (the shadow), and only the nodes whose cut is x-bound need a search of their own.  Deliver exact
proofs of the exchanges of the block 5216..5279 at the cost of the checks, and measure how often a node needs its own
search.  The coordinator asked to size it first and report the cost before any run longer than an hour.

## Sizing the block

In 5216..5279 (`../../succession/past5060.csv`) sixteen games are exchange steps.  Fifteen are repeats (5219, 5221,
5223, 5239, 5241, 5245, 5249, 5251, 5255, 5257, 5259, 5263, 5267, 5269, 5277): their root problem is the game
before's, so the rule of repeats settles them with no search, and a transfer proof would add nothing.  **One, 5217
(layer 3, cofactor 111, best-known δ 2,666, gap 2,126), is a searched exchange**, and its transfer proof needs the
proof tree of 5216 (a relaxation, gap 2,126, best-known δ 2,170).

* The nearest measured cost: 5260 (a relaxation, gap 2,106) was proven standalone in 596 million steps and 78.5
  CPU-hours (`results/beyond-the-chain.jsonl`).  The chain's cost grows about tenfold per 476 points of gap, so 5216 at
  2,126 is about 85 CPU-hours: some 5.5 hours on 16 threads, and with E6's trace on (1.5 to 2 times slower in E6's
  measurements) 8 to 11 hours.
* What it would save: 5217's own search (the chain proves an exchange from the game before it, with the near-repeat
  cut; how much 5217 would cost is not known until it is run).  Since the chain must prove 5216 anyway, the transfer
  proof's extra cost is the trace on 5216's run, about 40 to 85 CPU-hours, against 5217's own search.  Not run: it
  needs the owner's approval.

## Two measurements at late exchanges

E6's trace, run as in E6 (a standalone search of n − 1 from its committed promotions; every refuted set, node conflict,
failed promotion and nogood classed by the peel: x-bound or not, and if x-bound whether game n can promote it).

| n | x | the proof of n − 1 | threads | steps | seconds | refuted sets | node conflicts | failed promotions | nogoods | x-bound (any kind) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 4693 | 3179 | complete, default tactics | 7 | 638,887 | 105 | 243,528 | 202,961 | 41,658 | 849 | 0 |
| 4693 | 3179 | complete, symmetry off | 7 | 640,504 | 102 | 247,013 | 202,212 | 41,028 | 970 | 0 |
| 4407 | 2398 | stopped at 30 minutes (720 units open) | 14 | 20,264,637 | 1,802 | 8,194,118 | 5,780,094 | 1,564,824 | 67,246 | 0 |

4406's root problem is 4404's (the chain proved 4405 and 4406 as repeats of it, 38 million steps and 5.7 CPU-hours);
the exchange 4407 itself took 7.7 CPU-hours in the chain, so it is a case where a transfer would save real time.  The
run with the trace did not finish within its limit.

What they show:

* **4693: the whole proof of 4692 transfers.**  Every cut has a core without x, in both variants; with symmetry off, E6's
  inference (its README, item 2) gives that the bound's family holds no x-bound set above P\*(4692).  A transfer proof
  of 4693 would need no search of its own at any node.  (The chain settled 4693 in 30 steps with the near-repeat cut,
  so this is a measurement, not a saving.)
* **4407: nothing x-bound in the 20 million steps searched** (about half of the proof, judging by the chain's 38
  million steps for the same problem, though a standalone search from the optimum takes a different tree).

With E6's eleven games, the count of cuts that need a search of their own is: none at eleven exchanges (E6's ten other
than 2301, and 4693), one nogood at 2301, none so far in the part of 4407 searched.

## What the build would need

E6's trace already classes every cut of a proof of n − 1 for transfer, at microseconds a cut (the in-search classing
makes the search 1.5 to 2 times slower; recording the cuts and classing them afterwards in parallel would cost less).
A transfer *proof* of n needs two more things, neither built:

1. **The bound cuts on board n.**  Section 12 says the parity bound at each node of n − 1's proof equals the same
   node's bound on board n (Theorem A's argument with the node's picks and bars).  The frame solver's nodes are frame
   states of Π_{n−1}; the same node on board n is a frame state of Π_n, whose candidates and frames can differ (x's
   factors, n's).  A proof must either replay each bound cut on board n or prove the equality for the frame states.
2. **A search of n at each node whose cut is x-bound and does not transfer**, from that node's promotions and
   candidates (E2's restricted problems do this: the node's promotions fixed, its other candidates barred).

## Files

e13-TAG-4693.json and e13-default-4407.json (the lines), their .err (progress lines) and samples files, obligation (the
binary), run.started, run.ended, run4407.started and run4407.ended (the times).
