#!/usr/bin/env python3
"""Study H1 of the unsound mode, the heuristics: plays the repository's heuristic strategies on a range of games and
writes a line a game, with the score, the seconds and the moves.

    python3 h1_heuristics.py moniot --bin PLAYTAXMAN --strategy NAME --lo A --hi B --out FILE [--every K]
    python3 h1_heuristics.py baseline --bin PLAYTAXMAN --out FILE
    python3 h1_heuristics.py python --heuristics DIR --strategy NAME --lo A --hi B --out FILE [--every K] [--workers W]
        [--skip GLOB ...] [--order descending|spread] [--claims DIR] [--deadline EPOCH]
    python3 h1_heuristics.py chain --heuristics DIR --lo A --hi B --out FILE [--every K] [--reanchor-solvent]
        [--bundle-limit L] [--optimal PATH] [--max-seconds S]

`moniot` plays each game with a fresh process of moniot/'s program, built from moniot/Makefile, and times the process
(the seconds of its wall clock, and the CPU seconds of the process).  `baseline` times the process on game 2, which
plays one move, to show what a process costs besides its game.  `python` plays the games of one of the strategies of
heuristics/strategies/ that need no game before them (maxturn, onetax, cascade, solvent, solvent_b), `--workers`
games at a time, each game on one thread, and times the call of the strategy alone, with the tables of divisors that
the strategies share built before (a worker builds them once).  `--skip` names files (a glob each, gzipped or not)
whose games the run does not play again.  `--order spread` plays the games of the range in the order of the van der
Corput sequence of their places (the first, the middle, the quarters, ...), so that at any time the games done are
spread over the range, and the first half of the order is every second game.  `--claims` names a folder in which a
worker claims a game by creating a file with its number before it plays it, so that several runs, started at
different times, play the games of one range between them without playing one twice.  `--deadline` is a time (seconds
since the epoch) after which the workers start no game.  `chain` plays the continuation chain as the README of
heuristics/ describes: one game after another, each from the game before, the first from the moves for A - 1 of
the proven results (`--optimal`).  With `--every K` it plays the games A, A + K, ..., and `chain` refuses it, since a
chain is the games in a row.

`--heuristics` is a copy of heuristics/ (the script writes no file there, but a copy keeps the repository clean of
bytecode).  Each file is JSON lines, one a game:

    {"strategy", "n", "score", "seconds", "cpu", "load", "threads": 1, "moves"}

`seconds` is the wall time of the game and `cpu` the CPU time of the process (of the worker, for python), `load` the
one-minute load average at the game's start, and `moves` the moves of a legal game of that score for the strategies
that give moves (null for the Python onetax and maxturn, which return a score).  `--max-seconds` ends a chain before
the game that would start once the seconds of its games, those of earlier runs of the same file included, reach S.
The chain's moves are an order that the chain's own `derive_order` gives for the set it ends with, which the script
computes after the game's seconds are taken.  A file that has some games is continued: the games it has are not
played again.  SIGINT and SIGTERM end the run between games.
"""

import argparse
import glob
import gzip
import json
import multiprocessing
import os
import resource
import signal
import statistics
import subprocess
import sys
import time
from pathlib import Path

PYTHON_STRATEGIES = ("maxturn", "onetax", "cascade", "solvent", "solvent_b")
MONIOT_STRATEGIES = ("OneTax", "GreedyOneTax", "PureOneTax", "MaxTurn+", "MaxTurn", "OddsEvens", "MaxPick")
BASELINE_RUNS = 50
STOP = False


def on_signal(_signum, _frame):
    """Ends the run after the game in play."""
    global STOP
    STOP = True


def load():
    """The one-minute load average."""
    with open("/proc/loadavg") as f:
        return float(f.read().split()[0])


def games_done(path):
    """The n of the lines a file has."""
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return {json.loads(line)["n"] for line in f if line.strip()}


def games_of(args, done):
    """The games of the range to play: every `--every`th from lo, minus the games already in the file."""
    return [n for n in range(args.lo, args.hi + 1, args.every) if n not in done]


def append(path, line):
    """Writes one line of a file and flushes it, so that a stop leaves the file whole."""
    with open(path, "a") as f:
        f.write(json.dumps(line, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------------------------------------------------------------
# moniot/


def play_moniot(binary, strategy, n):
    """One game with one process: the line of the game, with its wall seconds and the CPU seconds of the process."""
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.perf_counter()
    out = subprocess.run([binary, "-h", strategy, "-p", "CSV", "-s", "-m"], input=f"{n}\n", capture_output=True,
                         text=True, check=True).stdout
    seconds = time.perf_counter() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    fields = out.strip().splitlines()[-1].split(",")
    if int(fields[0]) != n:
        raise RuntimeError(f"{strategy} {n}: the program played game {fields[0]}")
    cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    return {"strategy": strategy, "n": n, "score": int(fields[1]), "seconds": seconds, "cpu": cpu, "load": load(),
            "threads": 1, "moves": [int(x) for x in fields[2:]]}


def moniot(args):
    """Plays the games of the range with one of moniot/'s strategies."""
    done = games_done(args.out)
    for n in games_of(args, done):
        if STOP:
            break
        append(args.out, play_moniot(args.bin, args.strategy, n))


def baseline(args):
    """Times each strategy's process on game 2, BASELINE_RUNS times, and writes the medians."""
    result = {}
    for strategy in MONIOT_STRATEGIES:
        runs = [play_moniot(args.bin, strategy, 2) for _ in range(BASELINE_RUNS)]
        result[strategy] = {"seconds": statistics.median(r["seconds"] for r in runs),
                            "cpu": statistics.median(r["cpu"] for r in runs), "runs": BASELINE_RUNS}
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1)


# ---------------------------------------------------------------------------------------------------------------------
# heuristics/


def import_heuristics(directory):
    """Puts a copy of heuristics/ on the path, without bytecode, and returns the modules the strategies need."""
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.abspath(directory))
    sys.setrecursionlimit(100_000)


WORKER = {}


def init_worker(heuristics, top):
    """Builds a worker's tables of divisors for the games up to `top`, and ignores the signals the parent handles."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    import_heuristics(heuristics)
    from core import divisor_lists, maximal_factor_lists
    from strategies.cascade import cascade
    from strategies.maxturn import max_turn
    from strategies.onetax import one_tax
    from strategies.solvent import solvent
    from strategies.solvent_b import solvent_b
    WORKER["divs"] = divisor_lists(top)
    WORKER["mf"] = maximal_factor_lists(top)
    WORKER["play"] = {
        "maxturn": lambda n: max_turn(n, WORKER["divs"]),
        "onetax": lambda n: one_tax(n, WORKER["divs"]),
        "cascade": lambda n: cascade(n, WORKER["divs"]),
        "solvent": lambda n: solvent(n, WORKER["mf"]),
        "solvent_b": lambda n: solvent_b(n, WORKER["mf"]),
    }


def play_python(job):
    """One game of a Python strategy, timed: the line of the game; None if the deadline has passed or another run has
    claimed the game."""
    strategy, n, claims, deadline = job
    if deadline is not None and time.time() > deadline:
        return None
    if claims is not None:
        try:
            os.close(os.open(os.path.join(claims, str(n)), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except FileExistsError:
            return None
    started_load = load()
    cpu = time.process_time()
    started = time.perf_counter()
    result = WORKER["play"][strategy](n)
    seconds = time.perf_counter() - started
    cpu = time.process_time() - cpu
    if isinstance(result, int):
        score, moves = result, None
    else:
        score, moves = sum(result), list(result)
    return {"strategy": strategy, "n": n, "score": score, "seconds": seconds, "cpu": cpu, "load": started_load,
            "threads": 1, "moves": moves}


def python(args):
    """Plays the games of the range with one strategy of heuristics/strategies/, `--workers` games at a time."""
    done = games_done(args.out)
    for pattern in args.skip:
        for path in glob.glob(pattern):
            opener = gzip.open if path.endswith(".gz") else open
            with opener(path, "rt") as f:
                done |= {json.loads(line)["n"] for line in f if line.strip()}
    games = games_of(args, set())
    if args.order == "spread":
        bits = max(1, (len(games) - 1).bit_length())
        games = [games[i] for i in sorted(range(len(games)), key=lambda i: int(format(i, f"0{bits}b")[::-1], 2))]
    else:
        # Games from the top down, so that the long ones start first and the workers end together.
        games = sorted(games, reverse=True)
    jobs = [(args.strategy, n, args.claims, args.deadline) for n in games if n not in done]
    if not jobs:
        return
    with multiprocessing.Pool(args.workers, init_worker, (args.heuristics, args.hi)) as pool:
        for line in pool.imap_unordered(play_python, jobs):
            if line is None:
                continue
            append(args.out, line)
            if STOP:
                pool.terminate()
                break


def legal_order(modules, n, moves_set, mf):
    """A legal order of a playable set, by the chain's own method: the set added largest first to the evaluator, then
    `derive_order` from its matching."""
    evaluator = modules["SetEval"](n, mf)
    for c in sorted(moves_set, reverse=True):
        if not evaluator.playable_add(c):
            raise RuntimeError(f"game {n}: {c} of the set does not add")
    return modules["derive_order"](n, evaluator.S, evaluator.match)


def chain(args):
    """Plays the continuation chain game by game, each from the game before; the first from the proven moves."""
    if args.every != 1:
        raise SystemExit("a chain is the games in a row: --every must be 1")
    import_heuristics(args.heuristics)
    from core import maximal_factor_lists, smallest_prime_factors
    from evaluation.verify import load_optimal
    from strategies import continuation
    from strategies.seteval import SetEval
    modules = {"SetEval": SetEval, "derive_order": continuation.derive_order}
    optimal = load_optimal(Path(args.optimal), args.hi)
    spf = smallest_prime_factors(args.hi)
    mf = maximal_factor_lists(args.hi)
    previous = None
    if os.path.exists(args.out):
        with open(args.out) as f:
            lines = [json.loads(line) for line in f if line.strip()]
        if lines:
            if [d["n"] for d in lines] != list(range(args.lo, args.lo + len(lines))):
                raise SystemExit(f"{args.out} does not hold the games from {args.lo} in a row")
            previous = {"n": lines[-1]["n"], "score": lines[-1]["score"], "_set": lines[-1]["moves"]}
    spent = sum(d["seconds"] for d in lines) if previous is not None else 0.0
    for n in range(args.lo if previous is None else previous["n"] + 1, args.hi + 1):
        if STOP or (args.max_seconds is not None and spent >= args.max_seconds):
            break
        started_load = load()
        cpu = time.process_time()
        started = time.perf_counter()
        record = continuation.run(n, n, previous is None, args.bundle_limit, args.reanchor_solvent, optimal, spf, mf,
                                  initial_records=None if previous is None else [previous])[-1]
        seconds = time.perf_counter() - started
        cpu = time.process_time() - cpu
        moves = legal_order(modules, n, set(record["_set"]), mf)
        if sum(moves) != record["score"]:
            raise RuntimeError(f"game {n}: the moves score {sum(moves)}, the chain {record['score']}")
        spent += seconds
        append(args.out, {"strategy": "chain", "n": n, "score": record["score"], "seconds": seconds, "cpu": cpu,
                          "load": started_load, "threads": 1, "source": record["source"], "tier": record["tier"],
                          "flips": record["flips"], "certificate": record["certificate"], "moves": moves})
        previous = record


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("moniot", "baseline", "python", "chain"))
    parser.add_argument("--bin", help="moniot/'s program")
    parser.add_argument("--heuristics", help="a copy of heuristics/")
    parser.add_argument("--strategy", help="the strategy's name")
    parser.add_argument("--lo", type=int)
    parser.add_argument("--hi", type=int)
    parser.add_argument("--every", type=int, default=1, help="play every Kth game from lo")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--skip", nargs="*", default=[], help="files (globs) whose games are not played again")
    parser.add_argument("--order", choices=("descending", "spread"), default="descending")
    parser.add_argument("--claims", help="a folder in which a worker claims a game before it plays it")
    parser.add_argument("--deadline", type=float, help="seconds since the epoch after which no game starts")
    parser.add_argument("--reanchor-solvent", action="store_true")
    parser.add_argument("--bundle-limit", type=int, default=2000)
    parser.add_argument("--optimal", help="results/optimal.jsonl.gz")
    parser.add_argument("--max-seconds", type=float, help="the seconds of games after which a chain starts no more")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)
    {"moniot": moniot, "baseline": baseline, "python": python, "chain": chain}[args.mode](args)


if __name__ == "__main__":
    main()
