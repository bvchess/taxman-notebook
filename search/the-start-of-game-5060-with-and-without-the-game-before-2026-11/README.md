# The start of game 5060, with and without the game before (2026-11)

Part of the [lab notebook](../../README.md).

Started 2026-11-04.  Concluded 2026-11-04.

**Question.**  How close to its best does the search of game 5060 start from the game of 5059, and how close from its
own start, with no seed?  The website's figure of what is left to choose in game 5060 gives the answer a row of its
own.

**Answer.**  From the game of 5059 the search starts at a promotion sum of 570,285, 45 below the best, 570,330.  On its
own it starts at 569,735, 595 below.  The search of 5060 was not run to the end either way: what the 550 points save in
nodes is not measured here.  At game 3020 a start 236 below opt(n) made the proof 7.5 times as long, and one 400 below
16.6 times ([the dear games](../the-dear-games-the-problem-or-the-chains-path-2026-10/README.md#4-what-a-start-below-optn-costs)).

## Method

The frame solver of commit [9015f79](https://github.com/bvchess/taxman/commit/9015f793) (`cargo build --release` in
`solver/frame`; its solver and results are those of every later commit to the website's of 2026-11-04), on the
laptop, one thread, each run stopped by `--node-limit 1` after its first unit:

* with the game before: `taxman solve 5060 --threads 1 --node-limit 1 --use-prev --force-search --out q.jsonl`, which
  takes the game of 5059 from the committed chain as its seed and the ceiling from its score;
* on its own: `taxman solve 5060 --threads 1 --node-limit 1 --out s.jsonl`, with no game before it, so no seed and no
  ceiling.

Each line's `best` is its search's incumbent after 1,023 nodes.  On two threads (1,429 and 1,419 nodes) the incumbents
are the same, so they are the starts themselves.  The best, 570,330, is the committed score of 5060, 8,053,621, less its
`in_the_bag`, 7,483,291.  The start with the game before took 7.3 s of setup and search, the start on its own 24.1 s.

## Results

| start | promotion sum | below the best |
|---|---|---|
| from the game of 5059 | 570,285 | 45 |
| on its own | 569,735 | 595 |
| the best | 570,330 | 0 |

The chain's own search of 5060 took 3.2 billion nodes from the first start.  The ceiling, 571,806, is 1,476 above the
best, so it did not end that search, and the near-repeat cut cut no node of it (`stats.near_repeat_cut` 0).
