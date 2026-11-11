## Phase 1: games the chain proved

The gap is the parity bound less opt(n), and `fit` the CPU-hours that the fit to the chain's proofs of
4001-5060 predicts for it; the budget is 3 times the chain's CPU-hours.  CPU and wall are this run's
search (the wall is `active`: the game's seconds with a worker, setup included).  The ratios are this
run's over the chain's; `+` marks a run stopped before it finished, a lower bound.  The start is the first
progress line's promotion sum less opt(n)'s, after a minute; `found` the active time of the first progress
line at the run's final best.

| n | gap | fit CPU-h | arm | chain CPU-h | chain nodes | budget CPU-h | CPU-h | wall h | nodes | CPU ratio | node ratio | CPU / fit | start | found | outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4848 | 1940 | 7.8 | seeded | 3.69 | 18.4M | 11.1 | 3.58 | 0.23 | 21.9M | 0.97 | 1.19 | 0.46 | 0 | 1 min | proved, exhausted, = opt(n) |
| 4848 | 1940 | 7.8 | standalone | 3.69 | 18.4M | 11.1 | 3.42 | 0.22 | 23.1M | 0.93 | 1.25 | 0.44 | 0 | 1 min | proved, exhausted, = opt(n) |
| 4864 | 1944 | 8.0 | seeded | 4.50 | 21.6M | 13.5 | 4.29 | 0.27 | 29.2M | 0.95 | 1.35 | 0.54 | 0 | 1 min | proved, exhausted, = opt(n) |
| 4864 | 1944 | 8.0 | standalone | 4.50 | 21.6M | 13.5 | 4.41 | 0.28 | 29.6M | 0.98 | 1.37 | 0.55 | -44 | 2 min | proved, exhausted, = opt(n) |
| 4865 | 1944 | 8.0 | seeded | 3.90 | 20.0M | 11.7 | 4.15 | 0.26 | 28.2M | 1.06 | 1.41 | 0.52 | 0 | 1 min | proved, exhausted, = opt(n) |
| 4865 | 1944 | 8.0 | standalone | 3.90 | 20.0M | 11.7 | 4.56 | 0.29 | 29.8M | 1.17 | 1.49 | 0.57 | -391 | 15 min | proved, exhausted, = opt(n) |
| 4872 | 1898 | 6.6 | seeded | 3.57 | 17.5M | 10.7 | 3.89 | 0.24 | 25.1M | 1.09 | 1.43 | 0.59 | 0 | 1 min | proved, exhausted, = opt(n) |
| 4872 | 1898 | 6.6 | standalone | 3.57 | 17.5M | 10.7 | 4.12 | 0.26 | 26.2M | 1.15 | 1.49 | 0.62 | -73 | 2 min | proved, exhausted, = opt(n) |
| 5019 | 2272 | 26.8 | seeded | 22.99 | 117.0M | 69.0 | 21.28 | 1.33 | 130.3M | 0.93 | 1.11 | 0.80 | 0 | 1 min | proved, exhausted, = opt(n) |
| 5019 | 2272 | 26.8 | standalone | 22.99 | 117.0M | 69.0 | 23.06 | 1.45 | 135.1M | 1.00 | 1.15 | 0.86 | 0 | 1 min | proved, exhausted, = opt(n) |

## Phase 2: games past 5060

The best-known score is the best-known file's when the run began, and the gap the bound less it.  The
budget is 3 times the fit's CPU-hours, and the ratio the run's CPU-hours over the fit's; the start is
the first progress line's promotion sum less the best-known one.

| n | best-known | gap | fit CPU-h | budget CPU-h | score or best so far | CPU-h | wall h | nodes | CPU / fit | start | found | outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5260 | 8711408 | 2106 | 14.8 | 44.5 | 8711408 | 44.46 | 2.79 | 345.2M | 3.00+ | -544 | 10 min | stopped at its budget, best so far +0 from best-known |
| 5264 | 8722614 | 2090 | 14.0 | 41.9 | 8722614 | 8.88 | 0.56 | 63.5M | 0.64+ | -544 | 14 min | stopped by a signal before its budget, best so far +0 from best-known |
| 5304 | 8862090 | 2093 | 14.1 | 42.4 | 8862090 | 42.38 | 2.65 | 360.7M | 3.00+ | -93 | 3 min | stopped at its budget, best so far +0 from best-known |
