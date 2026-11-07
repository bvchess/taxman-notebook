"""Shared helpers of the study: opt(n) from the committed results, and the lines of a file of unsound lines."""
import gzip
import json

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"


def opt_scores(path=RESULTS):
    """opt(n) for every n of the committed results."""
    scores = {}
    with gzip.open(path, "rt") as f:
        for text in f:
            line = json.loads(text)
            scores[line["n"]] = line["score"]
    return scores


def last_lines(path):
    """The last line of each game of a file of unsound lines (gzipped or not)."""
    opener = gzip.open if path.endswith(".gz") else open
    games = {}
    with opener(path, "rt") as f:
        for text in f:
            if text.strip():
                line = json.loads(text)
                games[line["n"]] = line
    return games
