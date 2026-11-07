#!/usr/bin/env python3
"""Part 3 of study B10: chains of the unsound mode with and without the repair, against the built-in table.

    python3 -I part3.py FILE...

For each file of unsound lines (one chain each), the last line of each game is the game's.  Prints the share of games
at opt(n), as played (the first line of each game) and as the file ends (its last line), and the runs of short games:
where each run is first short, for how many games, by how much at the first, and what ended it (the next game, its
method, and `prev.short_by` if it proves the line before short; "end" if the chain ends inside it).  Then the seconds:
those of the games (their lines' `seconds`), per 100 games, and those of the repairs (`repaired.seconds`).
"""

import gzip
import json
import sys

RESULTS = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"


def runs_of(games, opt):
    """The runs of short games of `games` (n -> line), in order: (first, count, short at the first, what ended it)."""
    runs, current = [], None
    ns = sorted(games)
    for n in ns:
        short = opt[n] - games[n]["score"]
        if short > 0:
            if current is None:
                current = [n, 0, short]
            current[1] += 1
        elif current is not None:
            d = games[n]
            ended = f"{n} {d['method']}" + (f" short_by {d['prev']['short_by']}" if d["prev"] and d["prev"]["short_by"] else "")
            runs.append((*current, ended))
            current = None
    if current is not None:
        runs.append((*current, "end"))
    return runs


def main():
    opt = {}
    with gzip.open(RESULTS, "rt") as f:
        for text in f:
            d = json.loads(text)
            if d["n"] >= 4000:
                opt[d["n"]] = d["score"]
    for path in sys.argv[1:]:
        first, last, repairs = {}, {}, []
        with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
            for text in f:
                d = json.loads(text)
                first.setdefault(d["n"], d)
                last[d["n"]] = d
                if d.get("repaired"):
                    repairs.append(d)
        games = len(first)
        seconds = sum(d["seconds"] for d in first.values())
        work = sum(d["work"] for d in first.values())
        repair_seconds = sum(d["repaired"]["seconds"] for d in repairs)
        print(f"{path}: {games} games {min(first)}-{max(first)}; {len(repairs)} repairs, {repair_seconds:.2f} s in them")
        print(f"  games' seconds {seconds:.0f}, {100 * seconds / games:.0f} a 100 games; work {work}")
        # Past the table there is no opt(n) to hold the lines to.
        known = all(n in opt for n in first)
        if known:
            at_first = sum(opt[n] == d["score"] for n, d in first.items())
            at_last = sum(opt[n] == d["score"] for n, d in last.items())
            print(f"  at opt(n): played {at_first} ({100 * at_first / games:.1f}%), "
                  f"final {at_last} ({100 * at_last / games:.1f}%)")
            for label, lines in (("played", first), ("final", last)):
                runs = runs_of(lines, opt)
                text = ", ".join(f"{n} ({count}, {short}; {ended})" for n, count, short, ended in runs)
                print(f"  runs {label}: {sum(r[1] for r in runs)} short: {text}")
        for d in repairs:
            r = d["repaired"]
            short = f" (opt - {opt[d['n']] - d['score']})" if known else ""
            print(f"    repaired {d['n']} {d['method']} from {r['from']}: {r['was']} -> {d['score']}{short}, "
                  f"{r['seconds']:.3f} s")


if __name__ == "__main__":
    main()
