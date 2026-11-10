# The games every level-3 run misses (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-09.  Concluded 2026-11-09.

**Question.**  Some proven games start a streak of short games in most level-3 unsound runs, whatever the seed.  Why,
and does more search (levels 4 to 6) or a change of the search's built-in constants reach opt(n) at them?

**Answer.**  At the 13 games that recur, the proven set of n gives up 7 to 15 of the promotions that survive of the
proven set of n − 1, where their controls give up a median of 1, and nothing computable without the proven set foretells
it.  Played alone from the proven line of n − 1, level 5 reaches opt(n) in as many of 18 plays as level 6 does (11) at
half the seconds, and level 4 in fewer (8).  Widening sooner, tilting more and a larger step limit at the wide stages
reach no more than master at level 3 (38 of 78 plays with master, 37 with the larger step limit, over six seeds), and
each leaves a game 18 to 27% fewer rounds at the same budget.  Game 4134 is 1 short in every play of every build and
level, and 3968 is 3 short in 17 of its 18 plays at level 3.  Master's constants stay, and levels 4 and 6 are not run.

## Method

*The words.*  A game is *short* in a run when its score is below opt(n), and a *streak* is a run of consecutive short
games.  A game is a *start* when it is short though the moves for n − 1 that it started from score opt(n − 1), so a
streak begins at a start (the [rehearsal](../the-rehearsal-on-the-known-range-2026-11/README.md) calls it a root).  A
game is *recurring* when it starts a streak in 2 of the 3 first passes of the rehearsals, or in 3 passes of any seeds.
Its *controls* are the 3 nearest games in its thousand, with a cofactor within a factor of 1.5, that every run searched
from moves at opt(n − 1) and none left short.  The words of the proven step are those of [how the optimal game changes
with n](../how-the-optimal-game-changes-with-n-2026-11/README.md) (E5): surv(S) is what survives in game n of the
proven set of n − 1, the *drops* are the promotions of surv(S) that the proven set of n lacks, and the *additions* are
the proven set's that surv(S) lacks.  A neighborhood can hold the proven set only if it frees every drop of its
incumbent.

*The rounds.*  A level L runs rounds until their work reaches 2^L × 65,536, so level 3 has 524,288 and level 5
2,097,152 ([the level of
effort](https://github.com/bvchess/taxman/blob/aeffc29/solver/docs/unsound/play.md#the-level-of-effort)).  A trajectory
of incumbents has a *stage* that sets the share of the incumbent's promotions its neighborhoods fix: 0.7 to 0.9 at stage
0, and 0.5 to 0.7 at stage 1 and 0.4 to 0.6 at stage 2, the *wide stages*.  It moves one stage down after each
`WIDEN` = 4 rounds with no growth, and returns to stage 0 when its incumbent grows.  `TILT` = 25 percent of its
neighborhoods free the small promotions more often, and a neighborhood searches up to `UNIT_STEPS` = 1,024 steps
([the options that shape the
rounds](https://github.com/bvchess/taxman/blob/aeffc29/solver/docs/unsound/play.md#the-options-that-shape-the-rounds)).

*The three studies.*  All three concern the recurring games and ran on 2026-11-09 (Pacific time).

1. **The study of the hard games** ([hard/](hard/)) is scripts over lines that exist, with no solver run.  It read at
   13:11 the 10 passes of the rehearsals of 3001-5060 at level 3: the rehearsal's passes 1 to 4 (seeds 1 to 4) and the
   passes 1 to 3 of two replicates of it with the seeds 100 + k and 200 + k for pass k (their passes 4 were still
   running).  Only pass 1 stops on growth.  The rehearsal ran the build
   [bd6381b](https://github.com/bvchess/taxman/commit/bd6381b) and the replicates the build
   [aeffc29](https://github.com/bvchess/taxman/commit/aeffc29).  It also read the 19 chains of
   [B14](../tuning-the-unsound-mode-on-a-long-chain-2026-11/README.md) and
   [B17](../the-stop-that-waits-for-quiet-rounds-2026-11/README.md) (seed 1, levels 1 to 4, the stop and the push
   varied; the lines of the rehearsal's pass 1 equal those of three of them at every game, so the chains are not
   independent of it), the proven table, and the proven step of every searched game from E5's steps.json.
2. **The survivor test** ([survivors/](survivors/), [run.sh](survivors/run.sh)) played 6 of the 13 games alone (3311,
   3549, 3844, 4134, 4225 and 5060) at levels 4, 5 and 6 with seeds 31, 32 and 33: `--known-to N-1 --best-known off
   --stop-growth off --threads 12` for game N, so each game starts from the proven lines of N − 1 and below it and
   nothing else.  54 plays by the build aeffc29, from 14:32 to 16:46.
3. **B24** ([b24/](b24/)) played the 13 games and their 13 controls alone at level 3 with `--known-to N-1`, no
   best-known file and no stop on growth, by four builds on 8 threads, one play at a time, from 14:32 to 18:40.  V0 is
   the build aeffc29 (production's; its tree is that of master ba59242, but for a doc), and each of V1, V2 and V3 is
   master's tree with one change at the wide stages.  Seeds 31 to 33 for all four builds on all 26 games, then seeds 34
   to 36 for V0 and V3 on the 13 recurring games, and for V1 on 3844.

Both of the last two studies leave the push at its default: a game whose gap grew by more than 25 is played twice, the
second time unseeded, and its work and seconds are both plays'.  They overlapped in time on one machine shared with
production, so their seconds compare within a study only.

## Results

### The recurring games

The first passes started 12, 15 and 10 streaks.  The shuffle redraws each run's starts from its own pool (the searched
games below their ceiling that started from opt(n − 1), about 700), keeping the run's count; no shuffle of 20,000
reached an observed count:

| games | observed | shuffled: mean (max) | stratified by thousand and cofactor quartile |
|---|---|---|---|
| starting in 2 or more first passes | 11 | 0.63 (6) | 1.11 (6) |
| in all 3 | 4 | 0.00 (1) | 0.01 (2) |
| starting in 3 or more of all 10 passes | 10 | 0.06 (2) | 0.19 (4) |

The 13 recurring games ([recurrence.csv](hard/recurrence.csv) has every game; 3844 was in the pool of 6 of the 7 later
passes, the others in all 7):

| n | factors | first passes (of 3) | later passes (of 7) | chains short (of 7 or 12) | most short | drops |
|---|---|---|---|---|---|---|
| 3192 | 2³·3·7·19 | 3 | 0 | 7 | 26 | 15 |
| 3311 | 7·11·43 | 3 | 4 | 7 | 40 | 13 |
| 3332 | 2²·7²·17 | 2 | 0 | 3 | 34 | 11 |
| 3384 | 2³·3²·47 | 2 | 0 | 5 | 47 | 7 |
| 3549 | 3·7·13² | 1 | 2 | 4 | 10 | 10 |
| 3565 | 5·23·31 | 2 | 1 | 7 | 65 | 14 |
| 3723 | 3·17·73 | 3 | 0 | 7 | 3 | 8 |
| 3844 | 2²·31² | 2 | 4 | 3 | 12 | 10 |
| 3968 | 2⁷·31 | 2 | 4 | 7 | 3 | 13 |
| 4107 | 3·37² | 2 | 0 | 10 | 28 | 10 |
| 4134 | 2·3·13·53 | 3 | 7 | 12 | 1 | 13 |
| 4225 | 5²·13² | 2 | 2 | 12 | 4 | 13 |
| 5060 | 2²·5·11·23 | 1 | 6 | 9 | 45 | 10 |

What seed 1 misses, every level and setting of seed 1 misses, so the 19 chains add no independent evidence.

### The size of the proven step

Every recurring game has a proven step of 7 or more drops, and the controls have a median of 1
([starts.csv](hard/starts.csv), medians over the 13 and their 39 controls):

| median | recurring (13) | controls (39) | recurring higher in the matched pairs |
|---|---|---|---|
| drops of the proven step | 11 | 1 | 37 of 39 |
| its additions | 11 | 2 | 37 of 39 |
| points surv(S) falls short | 879 | 61 | 26 of 39 |
| chance a round at stage 0 frees every drop | 1.1 × 10⁻³ | 1 | 1 of 39 |
| the same at stage 2 | 0.67 | 1 | 1 of 39 |
| ceiling gap | 639 | 1,096 | 17 of 39 |
| cofactor | 124 | 132 | 21 of 39 |

Over all 726 searched games of 3001-5060 below their ceiling ([bigsteps.csv](hard/bigsteps.csv)), the share of plays
that miss a game rises with the drops from none to a quarter:

| drops | games | recurring | short in no run | plays that missed, all passes |
|---|---|---|---|---|
| 0-4 | 573 | 0 | 547 | 0 of 5,678 |
| 5-6 | 59 | 0 | 57 | 1 of 588 (0.2%) |
| 7-9 | 51 | 2 | 39 | 11 of 503 (2.2%) |
| 10-12 | 27 | 5 | 17 | 21 of 243 (8.6%) |
| 13 or more | 16 | 6 | 4 | 36 of 148 (24%) |

Among the 153 games of 5 or more drops, the recurring ones have more (a median of 11 against 7 for those no run
missed, AUC 0.90) and a lower cofactor (124 against 198).

* **The stuck line stays near surv(S).**  At 12 of the 13 games the first failing first pass ends within 5 drops of it,
  and at 9 without a gain over the start.  At 8 games every failing play ends at the same set.
* **The drops are small promotions**, a median 0.35 n, which the tilt favors: a tilted neighborhood frees a stuck swap
  a median 50 times as often as a uniform one at stage 2 (82 times at stage 1).
* **Pass 1 stops before the wide stages.**  The stop on growth ended 16 of the 27 failing first-pass plays, and 14 of
  the 27 gave the start's trajectory no round at stage 2.  The expected number of a play's neighborhoods that freed its
  swap has a median of 0.24, against 0.61 in the later passes.
* **A hard core runs its budget and still misses.**  3549, 3844, 3968, 4134 and 4225 grew their gap by more than 25,
  so pass 1 played them twice, to the budget, through stage 2; they make 19 of the 30 later-pass starts.
* **What reached opt(n).**  In the later passes, 43 of the 58 plays that did came through a trajectory from a line
  above, in a median of 1 round; in the first passes and chains, 18 came from the start or a line below, after 8 to 10
  rounds.  But what survives of the lines above is 9 to 13 drops from the proven set at 7 of the 13 games.

### Nothing computable without the proven set foretells it

[pattern.py](hard/pattern.py) tests 25 features of the lines of n and below it on each first pass: the AUC of recurring
against clean games (searched below the ceiling from opt(n − 1) in every run and short in none), a threshold chosen on
three blocks of 515 games and applied to the fourth, the top tenth by the other blocks' cut, and the matched pairs.
Selected rows, summed over the three first passes (34 recurring starts, 1,885 clean games):

| feature | AUC | held out: caught, clean flagged, share flagged | top tenth: caught |
|---|---|---|---|
| cofactor (log) | 0.67 | 29, 975, 54% | 3 |
| largest prime (log), lower | 0.68 | 28, 946, 52% | 4 |
| ceiling gap, lower | 0.64 | 18, 856, 45% | 12 |
| gains in the rounds | 0.60 | 13, 392, 22% | 9 |
| the line's own step (drops) | 0.67 | 11, 394, 23% | 10 |
| the proven step (uses the proven set) | 0.99 | 31, 88, 8% | 34 |

The strongest, a small ceiling gap and the line's own step, catch 10 to 12 of the 34 in the top tenth (3.4 by chance).
The 34 are 13 games counted in each pass, so that is about 4 games, within chance for the strongest of 25 features,
and the matched pairs show neither.

Nor can the proven step be foreseen.  A logistic regression on 16 features of number theory and setup
([stepsize.py](hard/stepsize.py)), fitted on 1,434 searched games of 1001-5060 with blocks of 500 held out, scores an
AUC of 0.78 for a step of 7 or more drops, but its top tenth of each first pass holds 4 of the 34 recurring starts
(3.4 by chance).  The line's own step equals the proven one where the line is right (Spearman 0.96) and is small where
it is stuck.  No property held up, so none was applied past 5060, and the production best-known file was not read.

### More effort: levels 4, 5 and 6

Played alone from the proven line of n − 1 with no stop, level 5 reaches opt(n) in as many plays as level 6, for half
the seconds ([run.log](survivors/run.log) ends with the table of score.py; the cost is [cost.txt](survivors/cost.txt)):

| game | level 4: plays at opt(n) of 3 | level 5 | level 6 |
|---|---|---|---|
| 3311 | 2 (40 short) | 2 (40) | 2 (40) |
| 3549 | 3 | 3 | 3 |
| 3844 | 0 (1, 1, 12) | 2 (1) | 2 (1) |
| 4134 | 0 (1, 1, 1) | 0 (1, 1, 1) | 0 (1, 1, 1) |
| 4225 | 1 (4, 4) | 2 (4) | 2 (4) |
| 5060 | 2 (45) | 2 (45) | 2 (14) |
| all, of 18 plays | 8 | 11 | 11 |
| points short | 110 | 93 | 62 |
| work, millions | 32.8 | 64.4 | 127.2 |
| seconds | 1,142 | 2,329 | 4,569 |

* **Level 5 gains three plays over level 4** (3844 seeds 32 and 33, 4225 seed 31), and level 6 gains none over level 5.
  Every play at opt(n) at one level is at opt(n) at the levels above it.
* **Level 6 shortens one play.**  5060 at seed 32 is 45 short at levels 4 and 5 and 14 short at level 6.
* **The seed decides more than the level**: seed 33 stays 40 short at 3311 and 4 short at 4225 at all three levels, and
  seed 32 stays short at 5060 (45, 45 and 14 points).
* **Level 5 takes 2.04 times level 4's seconds and level 6 4.00 times**, and the work doubles with each level (32.8,
  64.4 and 127.2 M).  The chains' levels 1 to 4 missed the same games from their own lines with the stop on; this test
  plays from the proven line with no stop.

### Three changes to the rounds (B24)

The hard-games study suggested giving a stalled game rounds at the wide stages, tilted, and a larger step limit there.
B24 tried three such changes, each master's tree with one change ([the patches](b24/)):

| variant | change | why this value |
|---|---|---|
| V0 | none (aeffc29) | |
| V1 | `unsound::WIDEN` 4 → 2 | [The race](../tilted-back-and-wider-rounds-2026-11/README.md) chose 4 over 16 (same reach, less work); 2 never raced.  With 2 a stalled trajectory reaches stage 2 at round 5, not 9. |
| V2 | `finder::WIDE_TILT` = 75: at stages 1 and 2, 75 percent of the neighborhoods tilt, at stage 0 still 25 | At stage 2 a tilted neighborhood frees a stuck swap a median 50 times as often as a uniform one; a quarter stays uniform for drops that are not small. |
| V3 | `finder::WIDE_UNIT_STEPS` = 4,096: at stages 1 and 2 a neighborhood takes up to 4,096 steps, at stage 0 still 1,024 | At 0.4 to 0.6 fixed a uniform round takes about 70,000 steps, so the limit of 1,024 binds there.  The level's budget is unchanged. |

The 13 controls are 3213, 3321, 3328, 3392, 3553, 3542, 3735, 3828, 3944, 4100, 4130, 4224 and 5054, the nearest of each
game's three in starts.csv.  The builds are release builds without LTO, built at -j 4.

| variant | recurring at opt(n), seeds 31-33: plays, games | seeds 34-36 | seeds 31-36: plays, games | controls missed (31-33) | work M, recurring / controls (31-33) | seconds, recurring / controls (31-33) | seeded rounds against V0 |
|---|---|---|---|---|---|---|---|
| V0 | 19/39, 9/13 | 19/39, 9/13 | 38/78, 11/13 | 0/39 | 30.6 / 25.5 | 1,567 / 1,285 | |
| V1 | 17/39, 8/13 | | | 0/39 | 30.4 / 25.5 | 1,512 / 1,167 | −27% / −21% |
| V2 | 15/39, 8/13 | | | 0/39 | 31.2 / 26.1 | 1,507 / 1,307 | −19% / −17% |
| V3 | 21/39, 11/13 | 16/39, 8/13 | 37/78, 12/13 | 0/39 | 32.3 / 27.0 | 1,648 / 1,381 | −18% / −18% |

The last column compares the plays of the same game and seed, recurring / controls.  Over six seeds V3 costs 6.0% more
work and 6.4% more seconds than V0 on the recurring games (64.5 against 60.9 M, 3,146 against 2,958 s), and 6.0% and
7.5% on the controls: the round that crosses the budget is larger.

Plays at opt(n) of 6 seeds (V1 and V2: of 3), by game:

| game | 3192 | 3311 | 3332 | 3384 | 3549 | 3565 | 3723 | 3844 | 3968 | 4107 | 4134 | 4225 | 5060 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V0 | 1 | 1 | 6 | 6 | 3 | 4 | 2 | 1 | 0 | 6 | 0 | 3 | 5 |
| V3 | 2 | 1 | 6 | 5 | 1 | 2 | 2 | 1 | 1 | 6 | 0 | 5 | 5 |
| V1 (31-33) | 0 | 1 | 3 | 3 | 0 | 1 | 0 | 2 | 0 | 3 | 0 | 2 | 2 |
| V2 (31-33) | 1 | 1 | 3 | 3 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | 1 | 2 |

* **No variant reaches more plays than V0.**  Over six seeds V0 and V3 are level (38 and 37 of 78); over seeds 31-33 V0
  leads V1 and V2 (19 against 17 and 15) and V3 leads V0 (21 against 19), then trails it at seeds 34-36 (16 against
  19).  V3 reaches 12 of the 13 games at some seed and V0 11, the difference being 3968, which V3 reaches once.  No
  difference is near significance.
* **Each change cuts the rounds.**  At level 3's budget V3's seeded plays of the recurring games get a median of 11
  rounds against V0's 13.5 (940 against 1,150 in all, fewer in 76 of the 78 pairs of the same game and seed), and the
  controls 11 against 14.  The median work of a round rises from 40.9k to 52.7k.  The rounds of V0 and V3 are the same
  until a trajectory first stands at a wide stage, so the whole cut falls after the 4th round.  V1 and V2 cut them as
  much or more, so every change that spends more on the wide stages buys fewer rounds at a fixed budget.
* **The pairs that split** (same game and seed, one build at opt(n); [rounds-out.txt](b24/rounds-out.txt) and the
  other two files of rounds.py).  V3 against V0: V0 alone 8, V3 alone 7 (sign test p = 1), and 7 of V0's 8 reached
  opt(n) in a round past the last round of V3's same play.  Of V3's 7, 5 came at a wide stage and 2 at stage 0 after a
  history that the wide rounds changed (3968 seed 31 in the unseeded play, 5060 seed 32).  V1 against V0 at seeds
  31-33: V0 alone 5, V1 alone 3 (3844 seeds 32 and 33, 4225 seed 33), and each of V0's 5 came past V1's last round.
  V2 against V0: V0 alone 5, V2 alone 1 (3192 seed 32), and 4 of V0's 5 came past V2's last round.
* **3844 is the one game where a variant led and V0 reached nothing** (seeds 31-33).  V1 also played it at seeds 34 to
  36: over the six seeds V1 reaches it 3 times (seeds 32, 33 and 35), V0 and V3 once each (seed 36); in pairs V1 alone
  3, V0 alone 1 (p = 0.63).  V1 loses at 3549 and 3723 (0 of 3 each, V0 2 of 3).
* **No build missed a control**, but 10 of the 13 controls hold opt(n) at the start (30 of the 39 plays in every
  build), and in the other 9 plays the builds reach it within the first 7 rounds.  The test says only that these
  changes do not break the easy games.

### The two that nothing reaches

* **4134 is 1 short in every play of every build and level** here: 18 plays at level 3 and 9 at levels 4 to 6.  It
  failed in all 10 passes and all 12 chains.  A round from surv(S) frees all 13 drops with chance 0.56 at stage 2, and
  the rehearsals' failing plays should have freed the swap about 7 times in all (6.8 expected neighborhoods over 10
  plays) and found nothing: there, freeing the swap is not finding the gain inside it.
* **3968 is 3 short in 17 of its 18 plays at level 3**, and reached once (V3, seed 31, in the unseeded play).  A round
  from surv(S) frees all 13 of its drops with chance 3 × 10⁻⁷ at stage 0 and 0.19 at stage 2, the lowest of the 13
  games at both stages (the median at stage 2 is 0.67), and the rehearsals' 6 failing plays should have freed it 2.6
  times in all.

## Limits

* **13 recurring games, one proven set each.**  Another optimal set of a game could be closer to the line (E5 found
  that rare).  Freeing every drop is necessary, not sufficient.  The counts of neighborhoods that free a swap assume the
  widening's ladder after the last gain, and the tilted chances are sampled, a chance of 0 meaning below 5 × 10⁻⁶.
* **The survivor test played 6 of the 13 games** at 3 seeds each, with no stop on growth.  3968 was not among them.
* **B24 has six seeds for V0 and V3 and three for V1 and V2**, and a play's outcome turns on its seed (5060 reaches
  opt(n) in 5 of 6 plays of both builds).  No build was tried with its budget raised to give it master's rounds, so
  the loss of rounds is the cause the data point to, not one that a run isolated.
* **The plays have no stop on growth and the proven lines.**  V0 reaches 49% of these plays, and the rehearsals' and
  chains' plays of the same games from opt(n − 1) reached 34% (76 of 223).  The study chose the 13 because they failed,
  and its first passes stopped on growth, so part of the gap is the stop and part the choice.  The stop, or a stop that
  waits for rounds at stage 2, is not tested here.
* **Nothing was played past 5060**, where no game is proven.  A trajectory can first stand at stage 1 in round
  `WIDEN` + 1 = 5, so a game that gets 4 rounds or fewer at level 3, as production's games there mostly do, plays the
  same rounds under V2 or V3 as under master; a game that gets 5 or more loses rounds after its 4th, and how many was
  not measured.  V1 widens from round 3 and would change most games.
* **One build commit each**, and the seconds are those of a machine shared with production.

## Decision

Keep master's `TILT` (25 percent), `WIDEN` (4 rounds) and `UNIT_STEPS` (1,024 steps).  None of V1, V2 and V3 reaches
more of the hard games at level 3, each leaves a game 18 to 27% fewer rounds at the same budget, and V3 costs 6% more
work and time.  Levels 4 and 6 are not run.  Level 4 reaches fewer of the survivors' plays than level 5 (8 against 11 of
18), and level 6 reaches the same 11 at twice level 5's seconds; production runs level 5 only.

The studies point to other levers:

* **The stop on growth**, which ended most of the rehearsals' failing first-pass plays before the wide stages and which
  B24 turned off.
* **4134 and 3968**, which no setting of the rounds moves: a look at their stuck sets against their proven sets would
  say what a neighborhood would have to hold.
* **The lines above**, as the descent and the later passes use them, which brought 43 of the 58 later-pass plays that
  reached opt(n) there, and miss the games whose lines above are as far from it.

What would reopen it:

* a variant played at a budget that leaves it master's number of rounds, or a stop that ends a stalled game's rounds
  only after rounds at stage 2, which separates the width from the loss of rounds;
* a game past 5060, or a streak in the production passes, that level 6 or a wider setting shortens and level 5 with
  master's constants leaves short;
* a neighborhood that holds the swaps of 4134 and 3968.

## Files

The studies ran in the scratch folder `lab/work/`, in the folders `gapdash/hard/`, `survivors/` and `b24/`, and each
keeps its folder here.  No binary is kept: the builds taxman-v0 to taxman-v3 (86 MB each) are not here, and the patches
are the record of V1 to V3.

* [hard/](hard/): the study of the hard games.
  * [README.md](hard/README.md): the study's own notes, written the day it ran.  This entry is the record and takes its
    numbers from them and the outputs below.
  * Run in order at nice 19; the header of each script gives its command and interpreter.  [extract.py](hard/extract.py)
    makes [plays.csv.gz](hard/plays.csv.gz) from the lines of every run (the rehearsals' and chains' lines are not
    kept here).  [recurrence.py](hard/recurrence.py) makes [recurrence.csv](hard/recurrence.csv).
    [compare.py](hard/compare.py) (the stats venv) makes [starts.csv](hard/starts.csv),
    [starts_by_run.csv](hard/starts_by_run.csv) and [candidates.json](hard/candidates.json).
    [pattern.py](hard/pattern.py) makes [features.csv](hard/features.csv).  [bigsteps.py](hard/bigsteps.py) (the stats
    venv) makes [bigsteps.csv](hard/bigsteps.csv).  [stepsize.py](hard/stepsize.py) (the stats venv) prints its tests.
    [common.py](hard/common.py) holds the shared definitions and is not run.
  * The outputs, what each script printed: [extract-out.txt](hard/extract-out.txt),
    [recurrence-out.txt](hard/recurrence-out.txt), [compare-out.txt](hard/compare-out.txt) with
    [compare-err.txt](hard/compare-err.txt) (its standard error), [pattern-out.txt](hard/pattern-out.txt),
    [bigsteps-out.txt](hard/bigsteps-out.txt) and [stepsize-out.txt](hard/stepsize-out.txt).
* [survivors/](survivors/): the survivor test.
  * [run.sh](survivors/run.sh) plays the 54 plays, one at a time, with `TAXMAN` the release build of aeffc29 in the
    scratch folder (`../unsound-run/taxman-aeffc29`), and ends by running score.py.  [run.log](survivors/run.log) is
    its output, with the table of score.py at the end.
  * [score.py](survivors/score.py) (`nice -n 19 python3 -I score.py` in the folder): each play against opt(n) of
    `results/optimal.jsonl.gz`, and for each game and level the seeds at opt(n).
  * [cost.py](survivors/cost.py) (`nice -n 19 python3 -I cost.py > cost.txt` in the folder) and
    [cost.txt](survivors/cost.txt): the plays at opt(n), the points short, and the work, rounds and seconds of each
    level.  It was written for this entry.
  * `gG-lL-sS.jsonl` and `.log`: the line and the standard output of the play of game G at level L and seed S.
* [b24/](b24/): the three changes to the search.
  * [README.md](b24/README.md): the trial's own notes, written the day it ran, as for hard/.
  * [run.sh](b24/run.sh) (`./run.sh VARIANT GAMES SEEDS`, GAMES `rec`, `ctl`, `all` or a list, beside the builds
    taxman-v0 to taxman-v3): `all` with seeds 31, 32 and 33 for each of v0 to v3, then `rec` with seeds 34 to 36 for v0
    and v3 and `3844` with seeds 34 to 36 for v1; a play whose line exists is skipped, so it resumes.
    [chain.log](b24/chain.log) is what each play printed, in order, with the times.
  * [plays/](b24/plays/): `plays/VARIANT/gN-sS.jsonl` and `.log`, the line and standard output of each of 393 plays.
  * [score.py](b24/score.py) (`python3 -I score.py [SEEDS]`) makes [score-out.txt](b24/score-out.txt) (all seeds),
    [score-31-33.txt](b24/score-31-33.txt) (`31,32,33`) and [score-34-36.txt](b24/score-34-36.txt) (`34,35,36`).
  * [rounds.py](b24/rounds.py) (`python3 -I rounds.py [VARIANT]`) makes [rounds-out.txt](b24/rounds-out.txt) (V3, the
    default), [rounds-v1-out.txt](b24/rounds-v1-out.txt) (`v1`) and [rounds-v2-out.txt](b24/rounds-v2-out.txt) (`v2`).
  * [v1-widen-2.patch](b24/v1-widen-2.patch), [v2-wide-tilt-75.patch](b24/v2-wide-tilt-75.patch) and
    [v3-wide-unit-steps-4096.patch](b24/v3-wide-unit-steps-4096.patch): each variant's change against master's commit
    ba59242 (`git diff ba59242 COMMIT` with COMMIT 90fe578, 9defb6e and 4a90337; `git apply` them to master).  V1
    changes `solver/frame/src/solver/unsound.rs`, V2 and V3 `solver/frame/src/search/finder.rs`.

## Commits

* [aeffc29](https://github.com/bvchess/taxman/commit/aeffc29) (main repository): the build of the survivor test's 54
  plays, of B24's V0 (117 plays) and of the rehearsal's two replicates; the lines of the first two name it as a clean
  build.  Master's next commit, ba59242, differs from it in a doc only.  The studies changed no code of master.
* [bd6381b](https://github.com/bvchess/taxman/commit/bd6381b): the build of the rehearsal's four passes.
* 90fe578 (V1), 9defb6e (V2) and 4a90337 (V3) (2026-11-09): the three variants, on the branch `b24-hard-search` of the
  main repository, each against ba59242; the lines of their plays name them as clean builds.  They were never merged
  and their branch is deleted, so `git show` may not find them.  The commits are stacked (V2 on V1, V3 on V2) although
  each one's tree is master's with its own change, so `git show` of V2 or V3 would show more than that change; the
  patches are the record.
* The commit that adds this entry and its row in [the register's file of the unsound
  mode](../../register/unsound-mode.md).
