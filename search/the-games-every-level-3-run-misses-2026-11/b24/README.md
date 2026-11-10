# B24: can a change to the search's rounds reach the optimum of the games that every run misses?

Trial of 2026-11-09 (Pacific), builds from 14:20, plays from 14:32 to 18:40.  Trial builds on the branch
`b24-hard-search` of the research repository (worktree .claude/worktrees/b24-hard-search), never pushed; nothing
merged.

**Answer.**  No.  At level 3's budget none of the three changes reaches more of the 13 recurring starts than master
does: over seeds 31-36 master reaches opt(n) in 38 of 78 plays and V3, the larger step limit in the wide stages, in 37;
over seeds 31-33 master 19 of 39, V1 (widen after 2 quiet rounds) 17 and V2 (tilt 75 percent in the wide stages) 15.
Each change makes the wide rounds dearer, so at the same budget a game gets 18 to 27% fewer rounds, and the plays that
master reaches and a variant misses are mostly those where master's gain came in a round past the variant's last (V3:
7 of 8, V1: 5 of 5, V2: 4 of 5).  What a variant reaches that master misses, it reaches mostly at a wide stage, and the
two balance: 7 against 8 for V3.  No build missed a control, but 10 of the 13 controls hold opt(n) at the start.

Played alone from the proven n − 1 lines with no stop on growth, master reaches 11 of the 13 games at some seed, 49% of
its plays.  4134 is 1 short in every play of every build (18 plays), and 3968 3 short in all but one of its 18 (V3,
seed 31).

## The builds

Each is master's tree with one change (commits on `b24-hard-search`; `git diff master <commit>` shows it alone).  V0 is
the production build unsound-run/taxman-aeffc29, whose code is master's (ba59242 differs from aeffc29 in a doc only).

| variant | commit | change | why this value |
|---|---|---|---|
| V0 | aeffc29 | none | |
| V1 | 90fe578 | `unsound::WIDEN` 4 → 2 | The race chose 4 over 16 (same reach, less work); 2 never raced.  From surv(S) a round frees the swap with a median chance of 10⁻³ at stage 0 and 0.67 at stage 2 (the study).  With 2, a stalled trajectory reaches stage 2 at round 5, not 9; at stage costs of about 1 : 10 : 22 (E3a) that buys most of WIDEN 1's extra stage-2 rounds and keeps a second cheap round at stage 0. |
| V2 | 9defb6e | `finder::WIDE_TILT` = 75: at stages 1 and 2, 75 percent of a trajectory's neighborhoods tilt, at stage 0 still 25 (`Options::at_stage` sets the tilt, `neighborhood_k` draws by it) | 25 against 50 everywhere raced even, and the full tilt loses the easy games at a low budget, which stage 0's uniform draw finds; at stage 2 a tilted neighborhood frees a stuck swap a median 50 times as often as a uniform one (the study).  So tilt more only where the hard games go; 75 leaves a quarter uniform for drops that are not small. |
| V3 | 4a90337 | `finder::WIDE_UNIT_STEPS` = 4,096: at stages 1 and 2 a neighborhood takes up to 4,096 steps, at stage 0 still 1,024 (`Options::at_stage` sets `unit_nodes`) | The brief's value.  At 0.4-0.6 fixed a uniform round takes about 70,000 steps (E3a), so the limit binds there.  Confined to the wide stages: `UNIT_STEPS` also makes `ROUND_WORK`, the unit of every level's budget, and the finder beside a proof search, so changing it would change the budget too.  The budget is unchanged. |
| V4 | | not built | Nothing to combine: no variant beat V0. |

Each build: `cargo build --release` without LTO, codegen-units 16, at -j 4 and nice 19; the binaries are taxman-v0 to
taxman-v3 here, the targets ../cargo-target-b24-v1 to v3 (273 MB each).

## The test

Each game alone from its proven n − 1 line (`--known-to N-1`: the table's lines of N − 1 to N − 8 seed it), level 3
(524,288 work), no stop on growth, no best-known file, one play at a time on 8 threads at nice 19 ([run.sh](run.sh)):

    taxman-V solve N-N --unsound --effort 3 --stop-growth off --seed S --known-to N-1 --best-known off --threads 8 --out plays/V/gN-sS.jsonl

* **The recurring starts**, the study's 13 (../gapdash/hard/README.md): 3192, 3311, 3332, 3384, 3549, 3565, 3723,
  3844, 3968, 4107, 4134, 4225, 5060.
* **The controls**, the nearest of each one's three in starts.csv (searched below the ceiling, never short, same
  thousand, cofactor within a factor of 1.5): 3213, 3321, 3328, 3392, 3553, 3542, 3735, 3828, 3944, 4100, 4130, 4224,
  5054.
* **Seeds** 31-33 for V0 to V3 on all 26; then 34-36 for V0 and V3 on the 13 recurring starts, and for V1 on 3844, the
  one game it reached more often than V0.
* **The score** ([score.py](score.py)): the play's score against opt(n) of results/optimal.jsonl.gz.  A game whose gap
  grew by more than 25 is played twice (the push), and its work and seconds are both plays'.  Below the ceiling, as all
  26 are, a play runs its whole budget, so work is about the budget whatever the build; what varies is the overshoot of
  the last round.  The seconds are of a busy machine (load about 80 of 88).

## Results

| variant | recurring at opt(n), seeds 31-33: plays, games | seeds 34-36 | seeds 31-36: plays, games | controls missed (31-33) | work M, recurring / controls (31-33) | seconds, recurring / controls (31-33) | seeded rounds against V0 (same game and seed) |
|---|---|---|---|---|---|---|---|
| V0 | 19/39, 9/13 | 19/39, 9/13 | 38/78, 11/13 | 0/39 | 30.6 / 25.5 | 1,567 / 1,285 | |
| V1 | 17/39, 8/13 | | | 0/39 | 30.4 / 25.5 | 1,512 / 1,167 | −27% / −21% |
| V2 | 15/39, 8/13 | | | 0/39 | 31.2 / 26.1 | 1,507 / 1,307 | −19% / −17% |
| V3 | 21/39, 11/13 | 16/39, 8/13 | 37/78, 12/13 | 0/39 | 32.3 / 27.0 | 1,648 / 1,381 | −18% / −18% |

Over seeds 31-36 V3 costs 6.0% more work and 6.4% more seconds than V0 on the recurring starts (64.5 against 60.9 M,
3,146 against 2,958 s), and 6.0% and 7.5% on the controls: the round that crosses the budget is larger.

**Per game**, plays at opt(n) of 6 seeds (V1 and V2: of 3):

| game | 3192 | 3311 | 3332 | 3384 | 3549 | 3565 | 3723 | 3844 | 3968 | 4107 | 4134 | 4225 | 5060 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V0 | 1 | 1 | 6 | 6 | 3 | 4 | 2 | 1 | 0 | 6 | 0 | 3 | 5 |
| V3 | 2 | 1 | 6 | 5 | 1 | 2 | 2 | 1 | 1 | 6 | 0 | 5 | 5 |
| V1 (31-33) | 0 | 1 | 3 | 3 | 0 | 1 | 0 | 2 | 0 | 3 | 0 | 2 | 2 |
| V2 (31-33) | 1 | 1 | 3 | 3 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | 1 | 2 |

3844 is the one game where a variant led at seeds 31-33 and V0 reached nothing, so V1 also played it at seeds 34-36:
over the six seeds V1 reaches it 3 times (seeds 32, 33, 35), V0 and V3 once each (seed 36); in pairs V1 alone 3, V0
alone 1 (p = 0.63).  It is a lead at one game, against V1's losses at 3549 and 3723 (0 of 3 each, V0 2 of 3).

**The pairs that split** (same game and seed, one build at opt(n)), from [rounds.py](rounds.py):

* V3 against V0, seeds 31-36: V0 alone 8, V3 alone 7 (sign test p = 1).  Of V0's 8, 7 reached opt(n) in a round past
  the last round of V3's same play (3549 seeds 32 and 34 in rounds 13 and 12 against V3's 10; 3565 seeds 33 and 35, 13
  and 14 against 10 and 11; 3723 seed 31, 11 against 10; 3192 seed 36, 18 against 16; 5060 seed 35, 10 against 8).  Of
  V3's 7, 5 came at a wide stage (3192 seeds 31 and 35, 3723 seed 33, 4225 seeds 31 and 34) and 2 at stage 0 after a
  history that the wide rounds changed (3968 seed 31 in the unseeded play, 5060 seed 32).
* V1 against V0, seeds 31-33: V0 alone 5, V1 alone 3 (3844 seeds 32 and 33, 4225 seed 33); each of V0's 5 came in a
  round past V1's last.  V1 misses 3549 and 3723 at all three seeds.
* V2 against V0, seeds 31-33: V0 alone 5, V2 alone 1 (3192 seed 32); 4 of V0's 5 came past V2's last round.

## The rounds: does V3's larger step limit cut the rounds a game gets?

Yes.  At level 3's budget V3's seeded plays of the recurring starts get a median of 11 rounds against V0's 13.5, 18%
fewer in all (940 against 1,150), fewer in 76 of the 78 pairs of the same game and seed; the controls 11 against 14,
18% fewer, in all 39 pairs; the unseeded plays 14% fewer.  The median work of a round rises from 40.9k to 52.7k.  The
rounds of V0 and V3 are the same until a trajectory first stands at a wide stage, so the whole cut falls on the rounds
after the 4th.  V1 and V2 cut them as much or more (27% and 19% on the recurring starts): every change that spends more
on the wide stages buys fewer rounds at a fixed budget.

Past 5060, which this trial did not play: a trajectory can first stand at stage 1 in round WIDEN + 1 = 5
(`Standing::after`), so a game that gets 4 rounds or fewer at level 3, as production's games there mostly do, plays the
same rounds under V2 or V3 as under master, gaining nothing and losing nothing.  A game that gets 5 or more loses rounds
after its 4th, as here; how many was not measured.  V1 widens from round 3, so it would change most games there.

## Caveats

* Six seeds for V0 and V3, three for V1 and V2; a play's outcome turns on its seed (5060: 5 of 6 for both builds), and
  no difference here is near significance.
* The controls test little: 30 of their 39 plays at seeds 31-33 hold opt(n) at the start in every build, and the
  others reach it in rounds 1 to 6, before or at the first wide round.  "No control missed" says only that these
  changes do not break the easy games.
* With no stop on growth and the proven lines of n − 1 to n − 8, V0 reaches 49% of these plays; the rehearsals' plays
  and chains' plays of the same games from opt(n − 1) reached 34% (76 of 223, the study's starts.csv).  The study chose the 13 because they failed,
  and its first passes stopped on growth, so part of the gap is the stop and part is the choice.  The stop
  (`STOP_QUIET`, or a stop that waits for rounds at stage 2) is not tested here.
* One build commit each; the seconds are of a machine shared with production.

## Recommendation

Keep master's TILT, WIDEN and UNIT_STEPS.  None of V1, V2 or V3 reaches more of the hard games at level 3, each costs
a fifth of the rounds, and V3 costs 6% more work and time.  The next levers are elsewhere: the stop on growth, which
ended most of the rehearsals' failing first-pass plays before the wide stages and which this test turned off; and
4134 and 3968, which no setting of the rounds moves (4134 is 1 short in all 18 plays), where a look at the stuck set
against the optimum would say what a neighborhood would have to hold.

## Files

* run.sh: the plays; chain.log: what each play printed.
* plays/V/gN-sS.jsonl and .log: each play's line and stdout.
* score.py → score-out.txt (all seeds), score-31-33.txt, score-34-36.txt.
* rounds.py [VARIANT] → rounds-out.txt (V3), rounds-v1-out.txt, rounds-v2-out.txt.
* taxman-v0 to taxman-v3: the builds.
