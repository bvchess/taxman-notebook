#!/usr/bin/env python3
"""Part 2 of study B13: chains of the unsound mode, each arm against the first.

    python3 -I part2.py DIR ARM... [--games LO-HI]

Each ARM is a file DIR/ARM.jsonl (or .jsonl.gz) of unsound lines over one range, with its log DIR/ARM.log (run_jobs.py
writes both), the first arm the one the others are set against (master).  A game's line is its last line in the file.
With `--games`, only the games LO to HI count (but for the wall time, which is the command's).  Prints, for each arm:

* the games at opt(n) where the committed results have it, the streaks of short games (the game each starts at, its
  length, how short its first game is), and the points short in all;
* the sum of the scores, less the first arm's;
* the games played twice, and those of them by the push, the unseeded plays kept, and the games whose rounds the stop
  on growth ended;
* the work (of both plays) and the seconds per 100 games: the seconds of the games' lines, and the wall time of the
  command from its log;
* the games whose score is lower than the first arm's, and those higher;

and checks every line: its `bound` is the parity bound of n (b13lib.PARITY), no score is above it or above opt(n),
and the growth it records is its gap less the gap of the line below as the run had it.
"""

import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b13lib import games_of, opened, opt_scores, parity_bounds, growth_of, streaks  # noqa: E402


def wall_seconds(log):
    """The wall time of the command of a log of run_jobs.py: from its first stamp to its exit, else to the log's last
    write; None without a log."""
    if not os.path.exists(log):
        return None
    stamps = []
    with open(log) as f:
        for text in f:
            found = re.match(r"# (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \S+ ", text)
            if found:
                stamps.append(datetime.datetime.strptime(found.group(1), "%Y-%m-%d %H:%M:%S"))
    if not stamps:
        return None
    end = stamps[-1] if len(stamps) > 1 else datetime.datetime.fromtimestamp(os.path.getmtime(log))
    return (end - stamps[0]).total_seconds()


def check(path, opt, bounds):
    """Every line of the file: its bound is the parity bound, no score is above it or above opt(n), and its growth is
    its gap less the gap of the line below (both plays of a game played twice are checked through the kept line)."""
    problems, lines, unbounded = [], 0, 0
    with opened(path) as f:
        for text in f:
            if not text.strip():
                continue
            line, lines = json.loads(text), lines + 1
            n = line["n"]
            if "bound" not in line:
                unbounded += 1
            elif line["bound"] != bounds[n]:
                problems.append(f"n={n}: bound {line['bound']}, the parity bound {bounds[n]}")
            if line["score"] > bounds[n] or (n in opt and line["score"] > opt[n]):
                problems.append(f"n={n}: score {line['score']} above the bound or opt(n)")
    if unbounded:
        problems.append(f"{unbounded} lines record no bound (a build before it)")
    for n, game in games_of(path, opt).items():
        recorded = game.played.get("growth")
        if recorded is not None and recorded != growth_of(game, game.played["score"], bounds):
            problems.append(f"n={n}: growth {recorded}, the gaps say {growth_of(game, game.played['score'], bounds)}")
    return lines, problems


def summary(path, log, opt, bounds, base, span):
    games = {n: g for n, g in games_of(path, opt).items() if span is None or span[0] <= n <= span[1]}
    ns = sorted(games)
    last = {n: g.last for n, g in games.items()}
    known = [n for n in ns if n in opt]
    short = {n: opt[n] - last[n]["score"] for n in known}
    played = {n: g.played for n, g in games.items()}
    twice = [n for n in ns if played[n].get("other") is not None]
    pushed = [n for n in twice if played[n].get("pushed")]
    kept = [n for n in twice if played[n]["unseeded"]]
    stopped = [n for n in ns if played[n].get("growth_stop")]
    work = sum(p["work"] + (p["other"]["work"] if p.get("other") else 0) for p in played.values())
    seconds = sum(p["seconds"] for p in played.values())
    wall = wall_seconds(log)
    per100 = 100 / len(ns)
    lines, problems = check(path, opt, bounds)
    out = [f"{os.path.basename(path)}: games {ns[0]}-{ns[-1]} ({len(ns)}), {lines} lines"]
    if known:
        at = sum(1 for n in known if short[n] == 0)
        out.append(f"  at opt(n): {at} of {len(known)}; points short: {sum(short.values())}")
        out.append("  streaks: " + (", ".join(f"{f} ({k} games, {s} short)" for f, k, s in streaks(known, short))
                                    or "none"))
    total = sum(last[n]["score"] for n in ns)
    if base is not None:
        out.append(f"  points: {total - sum(base[n]['score'] for n in ns):+} on the first arm")
        lower = [f"{n} ({last[n]['score'] - base[n]['score']})" for n in ns if last[n]["score"] < base[n]["score"]]
        higher = [f"{n} (+{last[n]['score'] - base[n]['score']})" for n in ns if last[n]["score"] > base[n]["score"]]
        out.append(f"  lower than the first arm: {len(lower)} {' '.join(lower)}")
        out.append(f"  higher than the first arm: {len(higher)} {' '.join(higher)}")
    out.append(f"  played twice: {len(twice)}, by the push {len(pushed)} {pushed}; the unseeded play kept: "
               f"{len(kept)} {kept}")
    out.append(f"  rounds ended by the stop on growth: {len(stopped)}")
    wall_text = f"{wall * per100:,.0f}" if wall is not None else "?"
    out.append(f"  per 100 games: {work * per100 / 1e6:.1f} million work, {seconds * per100:,.0f} s of games, "
               f"{wall_text} s of wall time")
    out.append(f"  checks: {'every line passes' if not problems else '; '.join(problems[:10])}")
    return "\n".join(out), last


def main():
    args, span = sys.argv[1:], None
    if "--games" in args:
        at = args.index("--games")
        span = tuple(map(int, args[at + 1].split("-")))
        args = args[:at] + args[at + 2:]
    folder, arms = args[0], args[1:]
    opt, bounds = opt_scores(), parity_bounds()
    base = None
    for arm in arms:
        path = os.path.join(folder, f"{arm}.jsonl")
        path = path if os.path.exists(path) else f"{path}.gz"
        text, last = summary(path, os.path.join(folder, f"{arm}.log"), opt, bounds, base, span)
        print(text)
        base = base if base is not None else last


if __name__ == "__main__":
    main()
