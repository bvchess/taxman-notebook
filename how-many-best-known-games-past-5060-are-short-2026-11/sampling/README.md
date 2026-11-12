# The sampling test: how many best-known games past 5060 are short

Started 2026-11-11 07:20 (Pacific time).

**Question.**  How many of the 4,940 best-known games past 5060 are short (below opt(n)), measured without the
statistical model, with an interval?

**Why it can be measured this way.**  A game past 5060 whose best-known score a proved rule determines from game n − 1
(the prime formula, the repeat lemma, the half lemma, the ceiling, the 8p and 12p theorems, the semiprime formula) is
optimal if game n − 1 is, so a short streak can start only at a game no rule covers: a *target*
(`../audit/targets.csv`, 1,559 of the 4,940).  A target that one more play raises was short.  So the share of targets
that one fresh play raises, divided by the chance d that one fresh play raises a root, estimates the roots, and the
streak lengths turn roots into short games.

## Design

### 1. Detection: d, calibrated on the rehearsals

The rehearsals ran the procedure on the proven games 3001-5060 as if unknown (`../rehearsal`, `../rehearsal2`,
`../rehearsal3`: level 3, pass 1 with the default stop, passes 2 to 4 with no stop, the descent).  Each rehearsal's
best-known file is append-only and each line names its pass, so `calib/make_states.py` rebuilds the state after pass 2
and after pass 3 (`calib/states/RrPk.jsonl`; each agrees with the rehearsal's own `scores-k.json` at all 2,060 games)
and lists the short games of each (`calib/roots.csv`).

| state | roots (short games whose game below is not short) | streaks |
|---|---|---|
| R1 after pass 3 | 3844, 4134 | 3844-3847, 4134-4139 |
| R2 after pass 3 | 3549, 4134, 4225, 5060 | 3549-3551, 4134-4139, 4225-4231, 5060 |
| R3 after pass 3 | 3311, 4134 | 3311, 4134-4139 |
| after pass 2 | R1: 3565, 3844, 3968, 4134; R2: 3311, 3549, 3844, 4134, 4225, 5060; R3: 3311, 3840, 3848, 4134 | |

Each calibration play is one game of one state, played alone into a fresh copy of the state's best-known file (never
the production file), with the production play's flags and `--known-to 3000`:

    chrt -i 0 nice -n 19 ../unsound-run/taxman-aeffc29 solve N-N --unsound --stop-growth off --known-to 3000 \
        --best-known COPY --threads 12 --effort L --seed S --out calib/plays/STATE-gN-lL-sS.jsonl

A play *raises* its game when its score is above the copy's best-known score of it (`known_before`).  The plays
(`calib/jobs.csv`, 228):

* the 8 roots after pass 3 at levels 4, 3 and 2, seeds 71-76 (144 plays);
* the 14 roots after pass 2 at level 4, seeds 71-74 (56), to see how d moves from pass 2 to pass 3;
* the 7 followers after pass 3 that are searched games below their ceiling, as targets are (4136 and 4137 in each
  state, 4230 in R2), at level 4, seeds 71-74 (28), to see whether a target inside a streak yields as a root does.

Seeds 71-76 are used by no play of the rehearsals (1-4, 101-104, 201-204), the survivor test (31-33) or B24 (31-36).

**How comparable the rehearsal roots are to the targets past 5060, and what the calibration does about each gap.**

* *Same procedure, same build.*  Production's passes past 5060 are the same level-3 passes with the descent and the
  push-down, and the pilot's plays are the same single-game level-4 plays (build aeffc29; rehearsal 1 ran bd6381b,
  whose solver code is aeffc29's).  The roots of both are searched games below their ceiling that no rule covers.
* *Larger games.*  A level's budget is fixed (level L stops at 2^L × 65,536 work) while a game's promotion
  candidates grow about as n (median 940 at 3001-4000, 2,578 at 9001-10000), so a level-4 play at 9,000 searches each
  candidate about as long as a level-3 play at 4,500.  The calibration plays the roots at levels 2, 3 and 4, and a
  target of game n is given, for each root i, the chance at the level 4 − log2(n / n_i), interpolated between the
  levels played and clamped to 2..4 (*size-matched*).  This assumes the chance depends on the work per promotion
  candidate, which is what the pilot's level choice and the model's falling find chance with n suggest.
* *More search before the test.*  The rehearsal roots have had three passes.  The targets have had passes 1 and 2,
  pass 3 up to 8660, the push-downs, and 0 to 6 dedicated level-3 to level-5 plays (the pilot, the hammer).  A root that
  survived m plays is more likely a hard one.  For a target with prior plays at levels l_1..l_m since its last raise,
  the roots are weighed by the product of their chances to have survived those plays, (1 − d_i) for each (*after prior
  plays*).  Above 8660 the targets had only two passes, which makes the after-pass-3 mix harder than theirs: the
  calibration errs low on d there, so high on the count.
* *Few roots.*  8 instances on 6 games, 3 of them 4134, which no play of any level has reached.  The intervals
  resample the instances, so the mix of easy and hard roots is part of the interval.

The survivor test (notebook, the-games-every-level-3-run-misses-2026-11) played the same 6 games at level 4 from the
proven line of n − 1 with no best-known file, and 8 of 18 reached opt(n).  Its plays had no lines above the game and
counted only plays that reached opt(n), so it is a check on the calibration, not pooled with it unless the two agree.

### 2. The sample past 5060

* **Frame**: `frame/targets.csv`, a copy of `../audit/targets.csv` as written at 07:20 (the best-known file and
  ledger2.tsv read at 07:19): 1,559 targets.  sha256 def5669a....
* **Strata** by the dedicated plays a target has had (targets.csv's `plays`): 0 (503), 1 (546), 2 (82), 3 or more
  (428).  The sample is drawn from all targets, stratified with proportional allocation: `draw.py` (seed 20261111)
  puts each stratum in a random order and interleaves the strata so that the first k targets hold each stratum in
  proportion to its size, for every k (`sample-order.csv`).  A target played three times is less likely to yield to one
  more play; the strata keep the sample's mix of histories equal to the frame's, and the detection chance of each
  target is adjusted for its own history (above), so the estimate neither leans on the unplayed targets nor ignores
  the played ones.
* **The play**: one level-4 play of each target on seed 71, which no play past 5060 has used (production has used
  seeds 1-6, 41-44 and 51-56), into the shared best-known file, exactly the command of
  `../succession/lawscan/play.sh`, at idle priority on 12 threads, recorded in `../rootfirst/ledger2.tsv` as play.sh
  records it, and in `sample.tsv` here.
* **Stopping**: the run plays the order from the top and starts no sample play after 11:30, a time fixed before it
  began, so the plays reached are a stratified random sample whatever they find.
* **A gain** is pushed down (the 8 games below at level 3 on seed 41, and on down while the lowest game of a window
  is raised, as `../rootfirst/pushdown-watch.sh` does) and carried up (windows of 20 at level 3 on seed 71 while the
  top game of a window rises, as `../rootfirst/run.sh`'s carry does), into the shared file, with their files in
  `plays/` here; `gains.tsv` records the streak each one raised.

**The size of the sample.**  With none of n sampled targets raised, the exact (hypergeometric) 95% upper bound on the
number of targets one play would raise is (draw.py):

| sample | 100 | 200 | 300 | 400 | 600 | 800 | 1,000 | 1,559 |
|---|---|---|---|---|---|---|---|---|
| hours on 6 lanes of 12 threads | 0.9 | 1.9 | 2.9 | 3.9 | 5.8 | 7.7 | 9.6 | 14.9 |
| raisable targets, none raised | 44 | 21 | 13 | 10 | 6 | 4 | 2 | 0 |
| the same, one raised | 70 | 34 | 22 | 16 | 10 | 7 | 5 | 1 |

The roots are that bound divided by d, so at d near 0.3 a sample of 300 bounds them near 45, of 600 near 20.  Halving
the bound costs about twice the plays.  A few hours give a sample of 300-400.

### 3. The estimate

* Roots ≈ (k / n) × T / d, with k the sample's raised targets, n its size, T = 1,559, and d the mean over the frame's
  targets of each target's detection chance (size-matched, after its prior plays).
* Short games ≈ roots × streak length, the lengths drawn from the root-first pilot's 30 streaks past 5060
  (`../gapdash/model/v3c/streaks.csv`, the units of v3c, mean 15.8 games) and this sample's own; the rehearsals'
  streaks (mean 4.25 games) are a second reading.
* **Interval (Monte Carlo)**: each draw resamples the 8 roots with replacement and draws each one's chance at each
  level from its Jeffreys posterior (Beta(k + 1/2, m − k + 1/2)), which gives d; then draws the roots from their
  posterior under a flat prior on 0..T, with a sampled root raised with chance (n / T) × d (binomial, which ignores
  that the sample is drawn without replacement and so widens the interval); then draws that many streak lengths.  The
  95% upper bound is the 95th percentile of the draws.  A second reading (Bonferroni): the exact hypergeometric 97.5%
  upper bound on the raisable targets, divided by the 2.5% quantile of d.

## Commands

    cd /home/brian/taxman_work/lab/work/sampling/calib && nice -n 19 python3 -I make_states.py
    cd /home/brian/taxman_work/lab/work/sampling && nice -n 19 python3 -I draw.py
    cd /home/brian/taxman_work/lab/work/sampling && nice -n 19 python3 -I run.py >> run.log 2>&1   # resumable
    cd /home/brian/taxman_work/lab/work/sampling && nice -n 19 ../stats-venv/bin/python -I analyze.py > analyze-out.txt

`run.py` runs six lanes of 12 threads: lanes 0 and 1 take the calibration first, lanes 2-5 the sample; a lane whose
queue is empty takes the other's.  A calibration play whose file has its game's line is done (one without is played
again from a fresh copy); a sample target with a ledger2 row for level 4 and seed 71 is not played again, and one whose
file lacks its line is run again with the same command, which goes on where it stopped; `sample.tsv` is written after
a gain's push-down and carry, so a stopped run goes on with them.

## Files

* `frame/targets.csv`: the frame.  `sample-order.csv`: the order of the plays.
* `calib/make_states.py`, `calib/states/`, `calib/roots.csv`, `calib/jobs.csv`, `calib/plays/`: the calibration.
* `run.py`, `run.log`: the plays.  `sample.tsv`: one row a sample play (order, n, stratum, the frame's best-known
  score, the known score when the play began, its score, gain, seconds, time).  `gains.tsv`: one row a gain (the games
  raised by the play, its descent, its push-down and its carry).  `plays/`: the sample's run files.
* `analyze.py`, `analyze-out.txt`: the numbers below.

## Results

The run went from 07:27 to 11:33 on 2026-11-11: 228 calibration plays (43 thread-hours) and 262 sample plays (208
thread-hours, 238 s a play), on a machine shared with other experiments (load 80 to 112).  `analyze-out.txt` has
every number below.

### d, the detection chance

Fresh plays of the rehearsal states' roots (raised / plays; each instance one root in one state):

| roots | level 4 | level 3 | level 2 |
|---|---|---|---|
| after pass 3: 8 instances on 6 games | 17/48 = 0.35 (exact 95% 0.22-0.51) | 12/48 = 0.25 | 8/48 = 0.17 |
| the same without 4134's 3 instances | 17/30 = 0.57 | 12/30 = 0.40 | 8/30 = 0.27 |
| after pass 2: 14 instances | 29/56 = 0.52 | | |
| followers after pass 3 (4136, 4137, 4230) | 3/28 = 0.11 | | |

* By root at level 4: 3844 6/6, 5060 4/6, 3311 3/6, 3549 3/6, 4225 1/6, 4134 0/18.  Every raise reached opt(n) at
  level 4.  The roots after pass 2 yield more (0.52) than those after pass 3 (0.35): the passes leave the hard ones.
* The survivor test's level-4 plays from the proven line of n − 1 reached opt(n) in 8 of 18, 0.44 a game against 0.47
  a game here, but not game by game (3844: 0/3 there, 6/6 here; the lines above it differ), so they are not pooled.
* Followers yield at rho = 0.30 times a root's rate (95% 0.15-1.00): only 4136, which is short by 31 more than the
  game below it, ever rose; 4137 and 4230, short by exactly what the game below them is, never did.
* For the targets past 5060, the mean over the frame of one play's chance (95% interval of the Monte Carlo draws):
  level 4 as played 0.354 (0.23-0.65); size-matched 0.262 (0.16-0.55); size-matched and after each target's prior
  plays 0.157 (0.13-0.39), or 0.177 (0.14-0.46) with the roots thinned by those plays.  By plays so far (0, 1, 2, 3+)
  the last is 0.27, 0.15, 0.09 and 0.05: a root that survived three plays is most likely of 4134's kind.

### The sample

262 of the 1,559 targets (85 of 503 never played, 92 of 546 played once, 13 of 82 twice, 72 of 428 three or more
times).  One raised: **5796** (stratum 3+, three earlier level-4 plays on seeds 41-43), +54, a root (the 8 games below
it rose not at all), whose carry raised 5797-5807: a streak of 12 games and 1,627 points (`gains.tsv`).  No other
target rose, and none had been raised by another play before its own.

### The estimate

A streak with k_s targets is raised by the sample with expected count f d D_s, f = 262 / 1,559 = 0.168, D_s =
1 + (k_s − 1) rho.  The detection mass M = Σ D_s is Gamma(k + 1, rate f d) under a flat prior; streaks and games are M
times the streaks and games per unit of D of a pool of streaks: the 31 found past 5060 by single-game plays (the
pilot's 30 units, their games and targets from `../gapdash/model/v3c/raised.csv`, and 5796's), each weighed by 1 / D_s
since a single-game play finds a streak in proportion to D_s; or the rehearsals' 8 streaks after pass 3, which are
every streak of their states.

The reading fixed before the last plays came in: d size-matched and after prior plays, every target alike; rho as
measured; the found streaks.

| reading | streaks | 95% upper | short games | 90% upper | 95% upper |
|---|---|---|---|---|---|
| **the reading above** | **25** | **81** | **193** | **459** | **573** |
| the same, roots thinned by the plays | 22 | 73 | 172 | 412 | 521 |
| the same, the rehearsals' streaks | 30 | 97 | 127 | 323 | 405 |
| the same, rho = 1 (followers yield as roots do) | 19 | 68 | 107 | 300 | 376 |
| the same, rho = 0 (only roots yield; the brief's roots × streak length) | 38 | 130 | 592 | 1,690 | 2,161 |
| d size-matched, no history | 15 | 60 | 116 | 333 | 425 |
| d level 4 as played | 11 | 45 | 86 | 257 | 317 |

* **Stratified**, each stratum's raises over its own d: the one raise, in the 3+ stratum where d = 0.049, stands for a
  detection mass of 122 and 622 games, and the strata with no raise give 0.  The two strata of targets played at most
  once (1,049) have 0 raises in 177 plays: their 95% upper bound is 508 games.
* **Bonferroni**: at most 30 raisable targets in the frame (exact, 97.5%) and d ≥ 0.137 (97.5%) give M ≤ 219.
* The model v3c's claim, for comparison: 88 short games (22-260).

### The claim

With 95% confidence at most about 570 of the 4,940 best-known games past 5060 are short (at least 88% at opt(n)), and
the estimate is about 190 (96%), in about 25 streaks.  It assumes:

1. Every short game past 5060 lies in a streak that starts at a target (proved: the rules settle the other games from
   the game below; L4 and N7b rest on statement U, and J3, L2 and L4 on the finite part of the square theorem).
2. The sample is a stratified random sample of the targets (by design; the stop was a clock time).
3. A root past 5060 yields to one fresh level-4 play as the rehearsals' 8 roots after pass 3 do at the level with the
   same work per promotion candidate, thinned for the target's earlier plays.  This carries over the rehearsals' mix,
   in which 3 of 8 instances (1 of 6 games, 4134) yield to no play: roots of that kind are counted only through that
   share, and no sampling at level 4 sees them.
4. A target inside a streak yields at 0.30 times a root's rate (3 games).
5. The streaks are like the 31 found past 5060.
6. The roots are spread over the strata like the targets; read stratum by stratum, the one find makes it about 620.

### What would tighten it

* **More plays per target.**  The bound scales as 1 / (f d): one more level-4 play of every target (about 17 hours on
  72 threads at today's load) gives f = 1 and would put the 95% bound near 150 games if it raised nothing new.
* **A larger d.**  A level scaled to the game's size would recover the size match's loss (0.35 against 0.26); a level-5
  play would raise it further (not measured here).  The heavily played targets, where d is 0.05, need several seeds or
  a higher level to be seen at all.
* **More roots in the calibration.**  The share of roots no play reaches (4134) sets the history adjustment; two or
  three more rehearsal replicates (about 280 thread-hours each), or rehearsals of 2001-3000, would measure it on more
  than one game.  rho rests on 3 games.
