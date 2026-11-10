"""Shared definitions of the study of hard games (standard library only): the runs, the proven table, the number theory.

Imported by the scripts of this folder (extract.py, recurrence.py, compare.py, pattern.py, bigsteps.py, stepsize.py);
not run itself.

A *run* is one file of unsound lines over a range of the proven games: a chain of B14 or B17 (seed 1, settings vary),
or one pass of a rehearsal (rehearsal, rehearsal2, rehearsal3: the same procedure, seeds k, 100 + k, 200 + k for pass
k).  A game's line in a run is its line of the highest score there, the first such line on a tie.
"""

import csv
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = "/home/brian/taxman_work/lab/work"
RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
PARITY_NB = "/home/brian/taxman_work/research/solver/notebook/search/the-parity-bound-against-the-frame-bound-2026-10"
PARITY = [f"{PARITY_NB}/parity_2_8191.jsonl.gz", f"{PARITY_NB}/parity_8192_10000.jsonl.gz"]
# E5, the notebook entry "How the optimal game changes with n": board.py (the frame model in Python) and steps.json (the
# drops and additions of the proven step at every searched game of 1-5060)
E5 = "/home/brian/taxman_work/research/solver/notebook/search/how-the-optimal-game-changes-with-n-2026-11"
STEPS = f"{E5}/steps.json"
LO, HI = 3001, 5060
PLAYS = os.path.join(HERE, "plays.csv.gz")
RECURRENCE = os.path.join(HERE, "recurrence.csv")

B14, B17 = f"{LAB}/unsound-b14", f"{LAB}/unsound-b17/runs"
CHAINS = (
    [(f"b14:{a}", "chain4k", f"{B14}/part1/{a}.jsonl") for a in
     ("l1", "l2", "l2-control", "l2-push100", "l2-push25", "l2-stop50", "l2-stopoff", "l2-unseeded1", "l3", "l4")]
    + [(f"b17:{a}", "chain4k", f"{B17}/{a}.jsonl") for a in ("q2", "q3")]
    + [(f"b14:{a}", "chain3k", f"{B14}/part2/{a}.jsonl") for a in
       ("h-choice-l2", "h-choice-l3", "h-control-l2", "h-default-l2")]
    + [(f"b17:{a}", "chain3k", f"{B17}/{a}.jsonl") for a in ("q2-h", "q3-h", "off3-h")]
)
REHEARSALS = ["rehearsal", "rehearsal2", "rehearsal3"]


def passes_done(folder):
    """The passes of a rehearsal folder that have ended: run.log has the score line "pass K: ... of ... games" of
    each, which its run.sh writes once the pass's file is complete."""
    done = []
    with open(os.path.join(folder, "run.log")) as f:
        for text in f:
            m = re.match(r"pass (\d+): \d+ of \d+ games", text)
            if m and int(m.group(1)) not in done and os.path.exists(os.path.join(folder, f"p{m.group(1)}.jsonl")):
                done.append(int(m.group(1)))
    return done


def runs():
    """(run, family, pass, file) of every run: the chains (pass 0), then each rehearsal's ended passes."""
    for run, family, path in CHAINS:
        yield run, family, 0, path
    for name in REHEARSALS:
        folder = os.path.join(LAB, name)
        for k in passes_done(folder):
            yield f"{name}:p{k}", name, k, os.path.join(folder, f"p{k}.jsonl")


def lines(path):
    """The parsed lines of a file of unsound lines; a last line that a writer has not finished is skipped."""
    with open(path) as f:
        for text in f:
            if not text.strip():
                continue
            if not text.endswith("\n"):
                return
            yield json.loads(text)


def load_opt(lo=2, hi=HI, promotions=True, moves=()):
    """n -> the proven line's score, promotions (a frozenset), method, in_the_bag and setup; `half_up`, whether
    (n + 1)/2 is a move of n (a source of U*(n) that is a factor of n + 1); and for the n in `moves` its moves (a
    frozenset)."""
    out = {}
    with gzip.open(RESULTS, "rt") as f:
        for text in f:
            x = json.loads(text)
            n = x["n"]
            if lo <= n <= hi:
                out[n] = {"score": x["score"], "method": x["method"], "in_the_bag": x.get("in_the_bag"),
                          "setup": x.get("setup") or {},
                          "promotions": frozenset(x.get("promotions") or []) if promotions else None,
                          "half_up": n % 2 == 1 and (n + 1) // 2 in x["moves"],
                          "moves": frozenset(x["moves"]) if n in moves else None}
    return out


def load_parity(lo=2, hi=10000):
    """n -> (U* sum, parity bound, candidates, candidates' sum) from the notebook's parity files."""
    out = {}
    for path in PARITY:
        with gzip.open(path, "rt") as f:
            for text in f:
                x = json.loads(text)
                if lo <= x["n"] <= hi:
                    out[x["n"]] = (x["ustar_sum"], x["parity"], x["free"], x["free_sum"])
    return out


def factor(n):
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def cofactor(n):
    """n over its largest prime factor."""
    return n // factor(n)[-1]


def layer(n):
    """The number of prime factors of n, counted with multiplicity."""
    return len(factor(n))


def kind(n, opt):
    """prime; ceiling (opt(n) = n + opt(n - 1)); or below (a game below its ceiling, not a prime)."""
    if layer(n) == 1:
        return "prime"
    return "ceiling" if opt[n]["score"] == n + opt[n - 1]["score"] else "below"


def ints(text):
    """The integers of a space-separated field."""
    return [int(t) for t in text.split()] if text else []


def read_plays():
    """run -> n -> the row of plays.csv.gz (strings as written)."""
    out = {}
    with gzip.open(PLAYS, "rt", newline="") as f:
        for row in csv.DictReader(f):
            out.setdefault(row["run"], {})[int(row["n"])] = row
    return out


def promotions_of(row, opt):
    """The promotions of a run's line, from the proven set of its game and the line's differences from it."""
    n = int(row["n"])
    return (opt[n]["promotions"] - set(ints(row["missing"]))) | set(ints(row["extra"]))


def seed_of(row, opt):
    """The seed that a line of n - 1 gives game n: its moves up to n/2, which are its promotions and, at an even n,
    n/2, a source of n - 1 that every line of n - 1 plays when U*(n - 1) holds it."""
    m = int(row["n"])
    return promotions_of(row, opt) | ({(m + 1) // 2} if opt[m]["half_up"] else set())


def read_recurrence():
    """n -> the row of recurrence.csv, its counts as ints."""
    out = {}
    with open(RECURRENCE, newline="") as f:
        for row in csv.DictReader(f):
            out[int(row["n"])] = {k: (int(v) if re.fullmatch(r"-?\d+", v) else v) for k, v in row.items()}
    return out


def started_from(plays, run, n):
    """The row of the line of n - 1 that a run's line of n started from: the run's own line of n - 1 if it scores what
    the line's `prev` does, else (in a pass after the first) the line of the earliest earlier pass that does; None if
    neither does or the line has no `prev`."""
    row = plays[run][n]
    if row["prev_score"] == "":
        return None
    prev = int(row["prev_score"])
    own = plays[run].get(n - 1)
    if own is not None and int(own["score"]) == prev:
        return own
    family = row["family"]
    for k in range(1, int(row["pass"])):
        other = plays.get(f"{family}:p{k}", {}).get(n - 1)
        if other is not None and int(other["score"]) == prev:
            return other
    return None
