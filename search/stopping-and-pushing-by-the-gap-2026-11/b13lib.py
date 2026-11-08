"""Shared helpers of study B13: opt(n), the parity bound, and the games of a file of unsound lines with their growth.

A line's *gap* is its bound less its score, and its *growth* its gap less the gap of the line of n − 1 that the game
started from (the study's question calls it the step).  The bound of n is the parity bound, field `parity` of the
notebook's file of every board 2..8191.
"""

import gzip
import json

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
NOTEBOOK = "/home/brian/taxman_work/research/solver/notebook/search"
PARITY = f"{NOTEBOOK}/the-parity-bound-against-the-frame-bound-2026-10/parity_2_8191.jsonl.gz"
# E2's chains of 100 games (`eE-LO.jsonl.gz`, old effort E, level E − 1) and B11's chains of Part 2.
E2 = f"{NOTEBOOK}/the-datasheet-of-the-unsound-mode-2026-11/runs"
B11 = f"{NOTEBOOK}/unseeded-games-above-a-short-game-2026-11/part2"


def segment_of(path):
    """The first game of the segment of one of E2's chains, from its file's name: `4861` for `e4-4861.jsonl.gz`."""
    return path.rsplit("/", 1)[-1].split("-")[1].split(".")[0]


def opened(path):
    """A text file, gzipped or not."""
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def opt_scores(path=RESULTS):
    """opt(n) for every n of the committed results."""
    with gzip.open(path, "rt") as f:
        return {line["n"]: line["score"] for line in map(json.loads, f)}


def parity_bounds(path=PARITY):
    """The parity bound of every n of 2..8191, and 0 for n = 1."""
    with gzip.open(path, "rt") as f:
        bounds = {line["n"]: line["parity"] for line in map(json.loads, f)}
    bounds[1] = 0
    return bounds


class Game:
    """A game of a file: its line as played (`played`, the first), its last line (`last`, the game's), and the score
    of the line of n − 1 when it was played (`prev_score`: the run's or the file's line, else opt(n − 1))."""

    def __init__(self, played, prev_score):
        self.played = played
        self.last = played
        self.prev_score = prev_score

    @property
    def n(self):
        return self.played["n"]

    def seeded(self):
        """The seeded play's score, work and improvements: the line's, or for a game played twice whose unseeded
        play was kept, its `other` (with no improvements)."""
        line = self.played
        if line.get("unseeded") and line.get("other"):
            other = line["other"]
            return other["score"], other["work"], None
        return line["score"], line["work"], line["improvements"]


def games_of(path, opt):
    """The games of a file of unsound lines, by n, in the order the file wrote them.  The score of n − 1 a game started
    from is the last line of n − 1 written before the game's first line, else opt(n − 1); where the line records
    `prev`, the two agree."""
    games, current = {}, {}
    with opened(path) as f:
        for text in f:
            if not text.strip():
                continue
            line = json.loads(text)
            n = line["n"]
            if line.get("repaired") is None:
                prev_score = current.get(n - 1, opt.get(n - 1))
                if line.get("prev") is not None and line["prev"]["score"] != prev_score:
                    raise SystemExit(f"{path}: n={n}: prev.score {line['prev']['score']}, the file had {prev_score}")
                games[n] = Game(line, prev_score)
            else:
                games[n].last = line
            current[n] = line["score"]
    return games


def gap_before(game, bounds):
    """The gap of the line of n − 1 that the game started from."""
    return bounds[game.n - 1] - game.prev_score


def growth_of(game, score, bounds):
    """The growth of the gap of the game at `score`: its gap there less the gap of the line below."""
    return bounds[game.n] - score - gap_before(game, bounds)


def streaks(ns, short):
    """The stretches of consecutive short games among `ns`: (first, length, shortfall at the first)."""
    found, ordered, i = [], sorted(ns), 0
    while i < len(ordered):
        if short[ordered[i]] == 0:
            i += 1
            continue
        j = i
        while j + 1 < len(ordered) and ordered[j + 1] == ordered[j] + 1 and short[ordered[j + 1]] > 0:
            j += 1
        found.append((ordered[i], j - i + 1, short[ordered[i]]))
        i = j + 1
    return found
