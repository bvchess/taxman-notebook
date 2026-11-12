# E11, the region solve of game 5061

Run on batmobile on 2026-11-11, 08:37 to 08:52 PST, from the branch `loops-e6` of the research repository (never
pushed): the code is commit cc01e81, the subcommand `window` of `examples/restricted.rs` with a region of any columns
(`--primes`), on E8's 068a78b and E6's commits.  The binary `restricted` here was built from cc01e81.

## The question

The loops study's E11 (study-report.md, Sections 10.3, 10.5 and 14).  Game 5061 = 3·7·241, a restriction, has the
best-known score 8,057,936 (δ = 746 against δ_PB = 254, rise 492); 5060 is proven.  Solve game 5061 with every
candidate outside a region of columns fixed (or barred) as the proven optimal set of 5060 has it, the region free.  A
score above 8,057,936 would be a better game of 5061; a score of 8,057,936 says no game with 5060's set outside the
region does better.  The proven 3297 and 3507, the same regime-(ii) mechanism, calibrate the method: their recoveries
R = 6P − δ must come out 540 and 609.

## The option

`restricted window N --primes Q,...`: the region is the candidates of game N's root problem whose largest prime is one
of the primes given (the cells of their columns, study-report.md Section 1).  Every other candidate is fixed if the
committed optimal set of N − 1 holds it and barred if not (no member of that set outside a region failed to be a
candidate of game N).  The search is E2's and E8's, exact and standalone, with no seed, no ceiling and no near-repeat
cut, `--tactic symmetry=off`; the answer is ΣU\*(N) plus the heaviest promotion set that respects the restriction.  The
line gives the score, δ = score(N − 1) + N − score, and the moves (`--show`).  `run-e11.sh` runs it on 16 threads at
`--background` and `nice -n 19`, stopped at 30 minutes.

## The checks

* Every answer's moves are replayed by the plain rules with the research repository's independent referee
  (`solver/tools/check_results.py`, which shares no code with the solver): the same score, and no legal move left
  (`referee.py` → `referee_out.txt`).
* At 3297 and 3507, proven, the region solve returns opt(n) and R = 540 and 609, the chain's values (the calibration).
* The tool is E8's (its checks are in ../e8/README.md: 1,620 restricted problems against an oracle, no mismatch), with
  the region given by primes in place of a depth.

## The regions

* The study's region at 5061: the columns of 151, 157, 163 (where the best-known change lives), 241 (P) and 251 (column
  −1).  The calibration regions by the same rule: the columns of the committed change from n − 1 to n, P's and column
  −1: 97, 101, 103, 157, 163 at 3297 and 103, 107, 109, 113, 167, 173 at 3507.
* Wider at 5061: Section 14's (149..167 and columns 0, −1), then bands of all primes from 139 to 251, 127 to 257, 101
  to 313, 53 to 509 and 29 to 1013.
* E10's regions (../e10/README.md): 149, 151, 157, 163, 241, 251, 421, 631 at 5061; 97, 101, 103, 107, 157, 163, 271,
  409 at 3297; 103, 107, 109, 167, 173, 283, 433 at 3507, and the last with 113 added.
* One more band, all primes from 13 up (only the candidates whose primes are all at most 11 fixed, nearly the whole
  problem), was stopped at 10 minutes, 17.7 million steps, with no set better than the best-known one found
  (`widest-stopped.txt`, its last progress line; the progress lines are in e11-5061.err).  It was not going to finish
  within the 30-minute limit, and it held the threads the E10 regions needed.

## The results

"free", "fixed" and "barred" count the candidates of game n's root; "target" is opt(n) at 3297 and 3507 and the
best-known score at 5061.

| n | region (primes) | free | fixed | barred | best score | target | δ | R = 6P − δ | steps | seconds |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5061 | 151, 157, 163, 241, 251 | 36 | 258 | 1086 | 8,057,936 | 8,057,936 | 746 | 700 | 25 | 0.65 |
| 3297 | 97, 101, 103, 157, 163 | 37 | 171 | 675 | 3,421,522 | 3,421,522 | 402 | 540 | 56 | 0.40 |
| 3507 | 103, 107, 109, 113, 167, 173 | 45 | 182 | 714 | 3,874,865 | 3,874,865 | 393 | 609 | 85 | 0.34 |
| 5061 | 149, 151, 157, 163, 167, 241, 251 | 53 | 255 | 1072 | 8,057,936 | 8,057,936 | 746 | 700 | 154 | 0.72 |
| 5061 | 139, 149, 151, 157, 163, 167, 173, 233, 239, 241, 251 | 80 | 250 | 1050 | 8,057,936 | 8,057,936 | 746 | 700 | 159 | 0.78 |
| 5061 | all 23 primes 127 to 257 | 161 | 238 | 981 | 8,057,936 | 8,057,936 | 746 | 700 | 184 | 0.81 |
| 5061 | all 40 primes 101 to 313 | 268 | 215 | 897 | 8,057,936 | 8,057,936 | 746 | 700 | 201 | 0.81 |
| 5061 | all 82 primes 53 to 509 | 533 | 174 | 673 | 8,057,936 | 8,057,936 | 746 | 700 | 4,352 | 2.21 |
| 5061 | all 161 primes 29 to 1013 | 816 | 120 | 444 | 8,057,936 | 8,057,936 | 746 | 700 | 26,390 | 4.88 |
| 5061 | E10: 149, 151, 157, 163, 241, 251, 421, 631 | 48 | 255 | 1077 | 8,057,936 | 8,057,936 | 746 | 700 | 82 | 0.69 |
| 3297 | E10: 97, 101, 103, 107, 157, 163, 271, 409 | 48 | 168 | 667 | 3,421,522 | 3,421,522 | 402 | 540 | 105 | 0.36 |
| 3507 | E10: 103, 107, 109, 167, 173, 283, 433 | 40 | 182 | 719 | 3,874,832 | 3,874,865 | 426 | 576 | 56 | 0.56 |
| 3507 | E10 and 113 | 48 | 180 | 713 | 3,874,865 | 3,874,865 | 393 | 609 | 85 | 0.34 |

At 5061 the region's best game is the best-known game itself, member for member, at every width (e11.jsonl's moves
against the best-known file's).

## What it decides

* **No game of 5061 better than 8,057,936 has the proven set of 5060 outside any of these regions**, up to the
  columns of all 161 primes from 29 to 1013, where 816 of the root's 1,380 candidates are free and only 120 are fixed.
  The best in every region is the best-known game, R = 700.  So 5061 is not short by a rearrangement of the far
  columns, of E10's region (the 19-member odd core over 149, 151, 163, 251, 421 and 631) or of anything near it,
  with 5060's set elsewhere: the recovery the parity bound sees (1192 = 8·149 entering for 6·241) is not playable with
  5060's set outside.  With E10's core this is the genuine reading's evidence; it is not a proof, since a better game
  could change the set of 5060 among the 11-smooth candidates or keep U\* only in part.
* **The calibration passes**: at 3297 and 3507 the region solve returns opt(n) with R = 540 and 609, the chain's values,
  in the regions of the committed change and in E10's.  E10's region at 3507 lacks the column of 113 (the committed
  change gives up 1582 = 14·113) and falls 33 short (R = 576); with 113 it reaches opt(3507).
* At 5061 the narrowest region (36 free candidates) already gives R = 700, and widening never changes it: by the
  study's Section 10.4, part 2 needs R_t ≤ 700 at every t an optimal set can use, and these runs show R ≤ 700 for the
  configuration with 5060's set outside, at t = 157 and any column up to 1013 freed with it.

## Files

run-e11.sh (the runs; each argument N:Q,Q,...), e11.jsonl (one line a game and region, with the moves), e11-N.err
(progress lines), referee.py and referee_out.txt (the replay), widest-stopped.txt (the stopped band), specs1.txt to
specs3.txt (the bands' prime lists), restricted (the binary).  The branch's code is kept as patches in ../e6/patches/;
cc01e81 is the eighth.
