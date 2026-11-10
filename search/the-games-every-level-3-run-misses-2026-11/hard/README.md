# M2: what makes a game hard for the unsound search

Study of 2026-11-09 (Pacific): analysis scripts over lines that exist, no solver run, no code change.

**Answer.**  A game is hard when its optimum is far from the optimum of the game below.  At the 13 recurring starts
the proven set gives up 7 to 15 of what survives of n − 1's proven set, against a median of 1 at matched controls.
The share of plays that miss a game rises from none below 5 such drops to a quarter at 13 or more.  Nothing that a
line shows without the optimum foretells it.

## Data

* **The proven table**, results/optimal.jsonl.gz: opt(n) and one optimal set a game.
* **The rehearsals** over 3001-5060 at level 3, read at 13:11: rehearsal passes 1-4 (seeds 1-4), rehearsal2 and
  rehearsal3 passes 1-3 (seeds 101-103, 201-203); their passes 4 were still running.  Only pass 1 stops on growth.
* **The 19 chains** of B14 and B17: seed 1 at levels 1-4 with the stop and the push varied.  rehearsal:p1's lines
  equal b14:l3's, b17:q3's and b17:q3-h's at every game, so the chains are not independent of it.
* **E5**, the notebook entry "How the optimal game changes with n": its board.py computes exact survivors, and its
  steps.json holds the proven step of every searched game.

## Method

In a run, a game is *short* below opt(n), and a *start* when short though the moves for n − 1 it started from score
opt(n − 1).  A run's *pool* is its searched games below their ceiling that started from opt(n − 1), about 700.  A game
is *recurring* when it starts a streak in 2 of the 3 first passes, or in 3 passes of any seeds.  Its *controls* are
the 3 nearest games in its thousand, with a cofactor within a factor of 1.5, that every run searched from opt(n − 1)
and none left short.  The *proven step* compares what survives in n of n − 1's proven set, surv(S), with n's proven
set, and its *drops* are what the optimum gives up.  A neighborhood can hold the optimum only if it frees every drop
of its incumbent; that chance is exact for the uniform draw and sampled for the tilted one.  Every line plays the same
U\*, so the promotions differ where the moves do.

## 1. Recurrence

The first passes started 12, 15 and 10 streaks.  Each shuffle redraws every run's starts from its own pool, keeping
its count; no shuffle of 20,000 reached any observed count:

| games | observed | shuffled: mean (max) | stratified by thousand and cofactor quartile |
|---|---|---|---|
| starting in 2+ first passes | 11 | 0.63 (6) | 1.11 (6) |
| in all 3 | 4 | 0.00 (1) | 0.01 (2) |
| starting in 3+ of all 10 passes | 10 | 0.06 (2) | 0.19 (4) |

The 13 recurring games (recurrence.csv has every game):

| n | factors | first passes (of 3) | later passes (of 7) | chains short | most short | drops |
|---|---|---|---|---|---|---|
| 3192 | 2³·3·7·19 | 3 | 0 | 7 of 7 | 26 | 15 |
| 3311 | 7·11·43 | 3 | 4 | 7 of 7 | 40 | 13 |
| 3332 | 2²·7²·17 | 2 | 0 | 3 of 7 | 34 | 11 |
| 3384 | 2³·3²·47 | 2 | 0 | 5 of 7 | 47 | 7 |
| 3549 | 3·7·13² | 1 | 2 | 4 of 7 | 10 | 10 |
| 3565 | 5·23·31 | 2 | 1 | 7 of 7 | 65 | 14 |
| 3723 | 3·17·73 | 3 | 0 | 7 of 7 | 3 | 8 |
| 3844 | 2²·31² | 2 | 4 of 6 | 3 of 7 | 12 | 10 |
| 3968 | 2⁷·31 | 2 | 4 | 7 of 7 | 3 | 13 |
| 4107 | 3·37² | 2 | 0 | 10 of 12 | 28 | 10 |
| 4134 | 2·3·13·53 | 3 | 7 | 12 of 12 | 1 | 13 |
| 4225 | 5²·13² | 2 | 2 | 12 of 12 | 4 | 13 |
| 5060 | 2²·5·11·23 | 1 | 6 | 9 of 12 | 45 | 10 |

What seed 1 misses, every level and setting of seed 1 misses, so the chains add no independent evidence.

## 2. What differs: the size of the proven step

Every play of these games started from n − 1's proven set itself.  So n − 1 is optimal, but at the recurring starts
the optimum of n is far from what survives of it (starts.csv):

| median | recurring (13) | controls (39) | recurring higher in the matched pairs |
|---|---|---|---|
| drops of the proven step | 11 | 1 | 37 of 39 |
| its additions | 11 | 2 | 37 of 39 |
| points surv(S) falls short | 879 | 61 | 26 of 39 |
| chance a round at stage 0 (70-90% fixed) frees every drop | 1.1 × 10⁻³ | 1 | 1 of 39 |
| at stage 2 (40-60% fixed) | 0.67 | 1 | 1 of 39 |
| ceiling gap | 639 | 1,096 | 17 of 39 |
| cofactor | 124 | 132 | 21 of 39 |

Over all 726 searched games below their ceiling (bigsteps.csv, from the seed itself):

| drops | games | recurring | short in no run | plays that missed, all passes |
|---|---|---|---|---|
| 0-4 | 573 | 0 | 547 | 0 of 5,678 |
| 5-6 | 59 | 0 | 57 | 1 of 588 (0.2%) |
| 7-9 | 51 | 2 | 39 | 11 of 503 (2.2%) |
| 10-12 | 27 | 5 | 17 | 21 of 243 (8.6%) |
| 13+ | 16 | 6 | 4 | 36 of 148 (24%) |

Among the 153 games of 5 or more drops, the recurring ones have more (a median of 11 against 7 for those no run
missed, AUC 0.90) and are less smooth, not more (cofactor 124 against 198).

* **The stuck line stays near surv(S).**  In 12 of the 13 games the first failing first pass ends within 5 drops of
  it, in 9 without a gain over the start.  In 8 games every failing play ends at the same set.
* **The drops are small promotions**, a median 0.35 n, which the tilt favors: a tilted neighborhood frees a stuck
  swap a median 50 times as often as a uniform one at stage 2.
* **Pass 1 stops before the wide stages.**  The stop on growth ended 16 of the 27 failing first-pass plays, and 14
  of the 27 gave the start's trajectory no round at stage 2.  The expected number of a play's neighborhoods that freed its swap has a median
  of 0.24.
* **A hard core runs its budget and still misses.**  3549, 3844, 3968, 4134 and 4225 grew their gap by more than 25,
  so pass 1 played them twice, to the budget, through stage 2; they make 19 of the 30 later-pass starts.  At 4134 the
  rehearsals' plays should have freed the swap about 7 times and found nothing: there, freeing is not finding.
* **What reached the optimum.**  In the later passes, 43 of 58 plays did through a trajectory from a line above, in
  a median of 1 round; in the first passes and chains, 18 did from the start or a line below, after 8 to 10 rounds.
  But what survives of the lines above is 9 to 13 drops from the optimum at 7 of the 13 games.

## 3. A property computable without the optimum: none

pattern.py tests 25 features of the lines of n and below it on each first pass: the AUC of recurring against clean
games, a threshold chosen on three blocks of 515 games and applied to the fourth, the top tenth by the other blocks'
cut, and the matched pairs.  Selected rows, summed over the passes (34 recurring starts, 1,885 clean games):

| feature | AUC | held out: caught, clean flagged, share flagged | top tenth: caught |
|---|---|---|---|
| cofactor (log) | 0.67 | 29, 975, 54% | 3 |
| largest prime (log), lower | 0.68 | 28, 946, 52% | 4 |
| ceiling gap, lower | 0.64 | 18, 856, 45% | 12 |
| gains in the rounds | 0.60 | 13, 392, 22% | 9 |
| the line's own step (drops) | 0.67 | 11, 394, 23% | 10 |
| the proven step (uses the optimum) | 0.99 | 31, 88, 8% | 34 |

The strongest, a small ceiling gap and the line's own step, catch 10 to 12 of the 34 in the top tenth (chance 3.4).
The 34 are 13 games counted in each pass, so that is about 4 games, within chance for the strongest of 25 features,
and the matched pairs show neither.

Nor can the proven step be foreseen.  A logistic regression on 16 features of number theory and setup
(stepsize.py), fitted on 1,434 searched games of 1001-5060 with blocks of 500 held out, scores an AUC of 0.78 for a
step of 7+ drops, but its top tenth of each first pass holds 4 of the 34 recurring starts (chance 3.4).  The line's
own step equals the proven one where the line is right (Spearman 0.96) and is small where it is stuck.

## 4. Past 5060

No property held up, so none was applied and the production best-known file was not read.

## 5. For the search

A recurring start needs a swap of 7 to 15 promotions in one step.  A search reaches it by freeing the whole swap in
one neighborhood and finding the gain inside, or by starting from a line that holds it.

1. **Give a stalled game rounds at the wide stages, tilted.**  From surv(S) a round frees the swap with a median
   chance of 10⁻³ at stage 0 and 0.67 at stage 2.  The stop cannot see these games, whose gap grows only by their
   shortfall, so pass 1 ends most of them first.  A game that stalls below its run's ceiling could widen after 1 or 2
   quiet rounds rather than 4, or stop only after a few rounds at stage 2, and the wide stages could tilt more than a
   quarter of their neighborhoods.  A race would have to measure the cost over all stalled games.
2. **Test a larger step limit for the wide neighborhoods** on 3549, 3844, 3968, 4134 and 4225, which ran their budget
   through stage 2 pass after pass and stayed short.
3. **Keep the lines above at work**, as the descent and the later passes do past 5060, knowing that they miss the
   games whose lines above are as far from the optimum.
4. **Not more seeds or levels of the same rounds.**  Seed 1 at levels 1 to 4 misses the same games, and 4134 failed in
   all 10 passes and all 12 chains.

## Caveats

* One optimal set a game: another could be closer (E5 found that rare).
* Freeing every drop is necessary, not sufficient.  The counts of freeing neighborhoods assume the widening's ladder
  after the last gain; the tilted chances are sampled, 0 meaning below 5 × 10⁻⁶.
* 13 recurring starts.  The later passes have lines above that a first pass lacks, but none above 5060.

## Files

Run in order at nice 19; each header gives its command and interpreter.  extract.py → plays.csv.gz; recurrence.py →
recurrence.csv; compare.py (stats venv) → starts.csv, starts_by_run.csv, candidates.json; pattern.py →
features.csv; bigsteps.py (stats venv) → bigsteps.csv; stepsize.py (stats venv).  common.py holds the shared
definitions, and the *-out.txt files what each printed.
