#!/usr/bin/env python3
"""The helpers of run.sh, and the results table of the proofs (README.md says what the experiment is).

    score.py prefix N FILE     write the committed lines of the games 1..N-1 to FILE (the seeded arm's --out)
    score.py spent FILE A [B]  the seconds that the first game of A..B not completed in FILE has had so far
    score.py extract FILE A [B]  print FILE's lines of the games A..B (B = A if not given)
    score.py known A B         print "n score bound" of each game A..B from the best-known file
    score.py budget ARM N      print a job's budget in CPU-hours, its wall seconds on 16 threads, and ok or over
    score.py proven N          print the finished job's file that holds a completed line of game N; fail if none
    score.py table             print the results table of out/*.jsonl, in Markdown

A job's tag is ARM-N: standalone-N and seeded-N prove game N; follow-N goes on from the proven game N, so its file
holds the lines of the games above N.
"""

import csv
import glob
import gzip
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHAIN = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
BEST_KNOWN = "/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl"
GAPS = "/home/brian/taxman_work/lab/work/gapdash/games.csv"
TABLE_END = 5060
THREADS = 16
# A job whose budget passes this many CPU-hours is not started.
MOST_HOURS = 100


def predicted_hours(gap):
    """The CPU-hours that the fit to the chain's 359 exhausted proofs of 4001-5060 gives a parity gap."""
    return math.exp(-56.84 + 7.78 * math.log(gap))


def parsed(path):
    """The parsed lines of a results file; a torn last line is skipped."""
    found = []
    if not os.path.exists(path):
        return found
    with open(path) as f:
        for text in f:
            try:
                found.append(json.loads(text))
            except json.JSONDecodeError:
                continue
    return found


def lines_of(path, n):
    return [line for line in parsed(path) if line.get("n") == n]


def chain_lines(wanted):
    """The committed lines of the games in `wanted`, by n (line n of the file is game n)."""
    found = {}
    if not wanted:
        return found
    top = max(wanted)
    with gzip.open(CHAIN, "rt") as f:
        for number, text in enumerate(f, start=1):
            if number in wanted:
                found[number] = json.loads(text)
            if number >= top:
                break
    return found


def bounds():
    """The parity bound of every game, from the gap dashboard's table."""
    with open(GAPS) as f:
        return {int(row["n"]): int(row["bound"]) for row in csv.DictReader(f)}


def prefix(n, path):
    with gzip.open(CHAIN, "rt") as f, open(path, "w") as out:
        for number, text in enumerate(f, start=1):
            if number >= n:
                break
            out.write(text)


def spent(path, lo, hi):
    """The seconds that the first game of lo..hi with no completed line in the file has had so far (0 if none)."""
    lines = parsed(path)
    done = {line["n"] for line in lines if line["completed"]}
    n = next((n for n in range(lo, hi + 1) if n not in done), None)
    seconds = [line["seconds"]["active_all_runs"] for line in lines if line["n"] == n]
    return int(max(seconds, default=0))


def known(lo, hi):
    """The best-known (score, bound) of each game lo..hi: a game's lines in the file score more, line after line."""
    best = {}
    with open(BEST_KNOWN) as f:
        for text in f:
            head = text[:40]
            at = head.find('"n":')
            if at < 0:
                continue
            n = int(head[at + 4 : head.find(",", at)])
            if not lo <= n <= hi:
                continue
            try:
                line = json.loads(text)
            except json.JSONDecodeError:
                continue
            if line["score"] > best.get(n, (0, 0))[0]:
                best[n] = (line["score"], line["bound"])
    return best


def budget(arm, n):
    """A job's budget in CPU-hours: 3 times the chain's CPU-hours for a game the chain proved, else 3 times the fit's
    prediction at the gap of its best-known line (for a follow-on job, of game n + 1, the first it goes on to)."""
    if arm == "follow":
        n += 1
    if n <= TABLE_END:
        return 3 * chain_lines({n})[n]["seconds"]["cpu_all_runs"] / 3600
    score, bound = known(n, n)[n]
    return 3 * predicted_hours(bound - score)


def read_known(tag):
    path = os.path.join(HERE, "out", f"{tag}.known")
    found = {}
    if os.path.exists(path):
        for text in open(path):
            n, score, bound = map(int, text.split())
            found[n] = (score, bound)
    return found


DURATION = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?(?:([\d.]+)s)?$")


def seconds_of(text):
    """`1h02m03s`, `1m05s` or `12.3s`, as the progress line writes a time, in seconds."""
    match = DURATION.match(text)
    hours, minutes, secs = (float(group) if group else 0.0 for group in match.groups())
    return hours * 3600 + minutes * 60 + secs


PROGRESS = re.compile(r"n=(\d+) active (\S+) waited \S+ cpu \S+ nodes (\d+) .*? best (\d+)")


def progress(log, n):
    """The (active seconds, promotion sum) of each progress line of game n in a log."""
    points = []
    if not os.path.exists(log):
        return points
    with open(log) as f:
        for text in f:
            match = PROGRESS.search(text)
            if match and int(match.group(1)) == n:
                points.append((seconds_of(match.group(2)), int(match.group(4))))
    return points


def hours(seconds):
    return f"{seconds / 3600:.2f}"


def millions(nodes):
    return f"{nodes / 1e6:.1f}M"


def jobs():
    """Every finished job of out/: (arm, n, its lines, its log)."""
    found = []
    for path in sorted(glob.glob(os.path.join(HERE, "out", "*.jsonl"))):
        tag = os.path.basename(path)[: -len(".jsonl")]
        arm, n = tag.rsplit("-", 1)
        if os.path.exists(os.path.join(HERE, "out", f"{tag}.done")):
            found.append((arm, int(n), parsed(path), os.path.join(HERE, "log", f"{tag}.log")))
    return found


def jobs_with_paths():
    """Every finished job of out/: (arm, n, its lines, its file)."""
    return [(arm, n, lines, os.path.join(HERE, "out", f"{arm}-{n}.jsonl")) for arm, n, lines, _ in jobs()]


def score_of(line):
    """The score of a completed line, or the best so far of an unfinished one."""
    return line["score"] if line["completed"] else line["best_so_far"]


def last_line(lines, n):
    mine = [line for line in lines if line["n"] == n]
    return mine[-1] if mine else None


def search_columns(line, points):
    """CPU-hours, wall hours, nodes, the start (the first progress line's promotion sum, after a minute) and the
    active minutes of the first progress line at the run's final best."""
    seconds = line["seconds"]
    best = score_of(line) - line["in_the_bag"] if line["in_the_bag"] is not None else None
    start = points[0][1] if points else None
    at = next((t for t, s in points if best is not None and s >= best), None)
    return seconds["cpu_all_runs"], seconds["active_all_runs"], line["nodes"], start, best, at


def minutes(at):
    return "-" if at is None else f"{at / 60:.0f} min"


def phase1_row(arm, n, line, points, c, bound):
    cpu, active, nodes, start, best, at = search_columns(line, points)
    opt = c["score"]
    gap = bound - opt
    if line["completed"]:
        assert line["score"] == opt, f"{arm} {n}: {line['score']} is not opt(n) {opt}"
        outcome = f"proved, {line['proof']}, = opt(n)"
    else:
        outcome = f"stopped at the cap, best {score_of(line) - opt:+d} from opt(n)"
    more = "" if line["completed"] else "+"
    c_cpu, c_nodes = c["seconds"]["cpu_all_runs"], c["nodes"]
    start_gap = "-" if start is None else f"{start - (opt - line['in_the_bag'])}"
    fit = predicted_hours(gap)
    return (
        f"| {n} | {gap} | {fit:.1f} | {arm} | {hours(c_cpu)} | {millions(c_nodes)} | {3 * c_cpu / 3600:.1f} "
        f"| {hours(cpu)} | {hours(active)} | {millions(nodes)} | {cpu / c_cpu:.2f}{more} | {nodes / c_nodes:.2f}{more} "
        f"| {cpu / 3600 / fit:.2f}{more} | {start_gap} | {minutes(at)} | {outcome} |"
    )


def phase2_row(arm, n, line, points, bk):
    cpu, active, nodes, start, best, at = search_columns(line, points)
    score, bound = bk
    gap = bound - score
    if line["completed"]:
        diff = line["score"] - score
        outcome = "proved at the best-known score" if diff == 0 else f"proved, a gain of {diff:+d}"
    else:
        fit = predicted_hours(gap)
        why = "at its budget" if cpu / 3600 >= 0.95 * 3 * fit else "by a signal before its budget"
        outcome = f"stopped {why}, best so far {score_of(line) - score:+d} from best-known"
    more = "" if line["completed"] else "+"
    start_gap = "-" if start is None else f"{start - (score - line['in_the_bag'])}"
    fit = predicted_hours(gap)
    return (
        f"| {n} | {score} | {gap} | {fit:.1f} | {3 * fit:.1f} | {score_of(line)} | {hours(cpu)} | {hours(active)} "
        f"| {millions(nodes)} | {cpu / 3600 / fit:.2f}{more} | {start_gap} | {minutes(at)} | {outcome} |"
    )


def follow_row(n, line, points, bk):
    cpu, active, nodes, _, _, at = search_columns(line, points)
    score, _ = bk
    if line["completed"]:
        diff = line["score"] - score
        outcome = f"proved, {line['proof']}" + ("" if diff == 0 else f", a gain of {diff:+d}")
    else:
        outcome = f"stopped at the cap, best so far {score_of(line) - score:+d} from best-known"
    same = line.get("same_search")
    of = f" of {same['n']}" if same else ""
    return (
        f"| {n} | {line['method']}{of} | {score} | {score_of(line)} | {hours(cpu)} | {hours(active)} "
        f"| {millions(nodes)} | {outcome} |"
    )


def table():
    found = jobs()
    games = {n for arm, n, _, _ in found if arm != "follow"}
    chain = chain_lines({n for n in games if n <= TABLE_END})
    bound = bounds()
    rows1, rows2, rows3 = [], [], []
    for arm, n, lines, log in sorted(found, key=lambda r: (r[1], r[0])):
        if arm == "follow":
            bk = read_known(f"{arm}-{n}")
            for line in sorted(lines, key=lambda line: line["n"]):
                rows3.append(follow_row(line["n"], line, progress(log, line["n"]), bk[line["n"]]))
            continue
        line = last_line(lines, n)
        if n <= TABLE_END:
            rows1.append(phase1_row(arm, n, line, progress(log, n), chain[n], bound[n]))
        else:
            rows2.append(phase2_row(arm, n, line, progress(log, n), read_known(f"{arm}-{n}")[n]))
    print("## Phase 1: games the chain proved\n")
    print("The gap is the parity bound less opt(n), and `fit` the CPU-hours that the fit to the chain's proofs of")
    print("4001-5060 predicts for it; the budget is 3 times the chain's CPU-hours.  CPU and wall are this run's")
    print("search (the wall is `active`: the game's seconds with a worker, setup included).  The ratios are this")
    print("run's over the chain's; `+` marks a run stopped before it finished, a lower bound.  The start is the first")
    print("progress line's promotion sum less opt(n)'s, after a minute; `found` the active time of the first progress")
    print("line at the run's final best.\n")
    print("| n | gap | fit CPU-h | arm | chain CPU-h | chain nodes | budget CPU-h | CPU-h | wall h | nodes | CPU ratio "
          "| node ratio | CPU / fit | start | found | outcome |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    print("\n".join(rows1))
    if rows2:
        print("\n## Phase 2: games past 5060\n")
        print("The best-known score is the best-known file's when the run began, and the gap the bound less it.  The")
        print("budget is 3 times the fit's CPU-hours, and the ratio the run's CPU-hours over the fit's; the start is")
        print("the first progress line's promotion sum less the best-known one.\n")
        print("| n | best-known | gap | fit CPU-h | budget CPU-h | score or best so far | CPU-h | wall h | nodes "
              "| CPU / fit | start | found | outcome |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        print("\n".join(rows2))
    if rows3:
        print("\n## The games above a proven game\n")
        print("A range run from the proven game's line, with every tactic at its default (the ceiling, the prime")
        print("formula, the repeats and the near-repeat cut).\n")
        print("| n | method | best-known | score or best so far | CPU-h | wall h | nodes | outcome |")
        print("|---|---|---|---|---|---|---|---|")
        print("\n".join(rows3))


def main(argv):
    command = argv[1]
    if command == "prefix":
        prefix(int(argv[2]), argv[3])
    elif command == "spent":
        lo = int(argv[3])
        print(spent(argv[2], lo, int(argv[4]) if len(argv) > 4 else lo))
    elif command == "extract":
        lo = int(argv[3])
        hi = int(argv[4]) if len(argv) > 4 else lo
        with open(argv[2]) as f:
            for text in f:
                try:
                    if lo <= json.loads(text).get("n") <= hi:
                        sys.stdout.write(text)
                except json.JSONDecodeError:
                    pass
    elif command == "known":
        for n, (score, bound) in sorted(known(int(argv[2]), int(argv[3])).items()):
            print(n, score, bound)
    elif command == "proven":
        # The job file that holds a completed line of game N; fails if none does.
        n = int(argv[2])
        holders = [path for arm, _, lines, path in jobs_with_paths() if any(
            line["n"] == n and line["completed"] for line in lines)]
        if not holders:
            sys.exit(1)
        print(holders[0])
    elif command == "budget":
        # The budget in CPU-hours, the wall seconds it gives 16 threads, and whether it is within the most a job may
        # have.
        hours_of = budget(argv[2], int(argv[3]))
        verdict = "ok" if hours_of <= MOST_HOURS else "over"
        print(f"{hours_of:.1f} {math.ceil(hours_of * 3600 / THREADS)} {verdict}")
    elif command == "table":
        table()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
