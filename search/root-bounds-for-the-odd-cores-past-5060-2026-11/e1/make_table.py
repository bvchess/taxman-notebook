#!/usr/bin/env python3
"""The table of E1 from the runs' lines: one row a board, with the root gap and, for each smoothness bound B run,
PB_s (or the range a stopped run left), the share of the gap it closes, the nodes processed and the time.

    python3 -I make_table.py [--only N,N,...] results.jsonl [more.jsonl ...] > table.md

A later line for the same board and B replaces an earlier one; --only keeps those boards alone.
"""

import json
import sys


def cell(d):
    def pct(v):
        return f"{100 * (d['PB'] - v) / d['gap']:.1f}%" if d["gap"] else "100%"

    if d["finished"]:
        value = f"{d['PB_s']:,}"
        share = pct(d["PB_s"])
    else:
        value = f"≤ {d['PB_s_upper']:,} (stopped)"
        share = f"≥ {pct(d['PB_s_upper'])}"
        if d["PB_s_lower"] > d["known"]:
            share += f", ≤ {pct(d['PB_s_lower'])}"
    return value, share, f"{d['processed']:,}", f"{d['seconds']:.0f}" if d["seconds"] >= 10 else f"{d['seconds']:.1f}"


def main():
    paths = sys.argv[1:]
    only = None
    if paths[:1] == ["--only"]:
        only = {int(x) for x in paths[1].split(",")}
        paths = paths[2:]
    runs = {}
    for path in paths:
        for raw in open(path):
            d = json.loads(raw)
            if only is None or d["n"] in only:
                runs[(d["n"], d["B"])] = d
    bs = sorted({b for _, b in runs}, reverse=True)
    head = ["n", "PB", "score", "gap"]
    for b in bs:
        head += [f"PB_{b}", f"share ({b})", f"nodes ({b})", f"s ({b})"]
    print("| " + " | ".join(head) + " |")
    print("|" + "---|" * len(head))
    for n in sorted({n for n, _ in runs}):
        any_run = next(d for (m, _), d in runs.items() if m == n)
        row = [str(n), f"{any_run['PB']:,}", f"{any_run['known']:,}", f"{any_run['gap']:,}"]
        for b in bs:
            row += list(cell(runs[(n, b)])) if (n, b) in runs else ["", "", "", ""]
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
