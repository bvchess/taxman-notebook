#!/usr/bin/env python3
"""B24's score (2026-11-09): each play plays/VARIANT/gN-sS.jsonl against opt(n) from the proven chain, and for each
variant the recurring starts reached (plays and distinct games), the controls missed, and the cost of each set.

    python3 -I score.py [SEEDS]

SEEDS, such as 31,32,33, limits the summary to those seeds (all by default); the per-game table shows every seed.
A play's work and seconds are both plays' for a game played twice (the line's `work` and `other.work`; `seconds`
counts both).  `to opt` is the work at which the play first scored opt(n), counted from the start of the game.
"""

import collections
import glob
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
REC = [3192, 3311, 3332, 3384, 3549, 3565, 3723, 3844, 3968, 4107, 4134, 4225, 5060]
CTL = [3213, 3321, 3328, 3392, 3553, 3542, 3735, 3828, 3944, 4100, 4130, 4224, 5054]
ORDER = ["v0", "v1", "v2", "v3", "v4"]


def work_to_opt(line, opt):
    """The work from the start of the game at which its kept play first scored `opt`, or None."""
    offset = line["other"]["work"] if line["unseeded"] and line["other"] else 0
    if line["start"] is not None and line["start"] >= opt:
        return offset
    for imp in line["improvements"] or []:
        if imp["score"] >= opt:
            return offset + imp["work"]
    return None


def plays(opt):
    """Every play here: (variant, n, seed) -> what it came to."""
    out = {}
    for path in glob.glob(os.path.join(HERE, "plays", "*", "g*-s*.jsonl")):
        variant = os.path.basename(os.path.dirname(path))
        n, seed = map(int, re.match(r"g(\d+)-s(\d+)\.jsonl", os.path.basename(path)).groups())
        with open(path) as f:
            lines = [json.loads(t) for t in f if t.strip()]
        lines = [x for x in lines if x["n"] == n]
        if not lines:
            continue
        line = lines[-1]
        other = line["other"] or {}
        out[(variant, n, seed)] = {
            "short": opt[n] - line["score"],
            "work": line["work"] + other.get("work", 0),
            "seconds": line["seconds"],
            "pushed": line["pushed"],
            "unseeded": line["unseeded"],
            "rounds": line["rounds"] + other.get("rounds", 0),
            "to_opt": work_to_opt(line, opt[n]),
        }
    return out


def main():
    seeds = {int(s) for s in sys.argv[1].split(",")} if len(sys.argv) > 1 else None
    opt = {x["n"]: x["score"] for x in map(json.loads, gzip.open(RES, "rt"))}
    got = plays(opt)
    variants = sorted({v for v, _, _ in got}, key=lambda v: (ORDER.index(v) if v in ORDER else 99, v))

    print("per game: the shortfall of each seed's play (0 = opt(n)), by variant")
    all_seeds = sorted({s for _, _, s in got})
    print(f"{'set':4} {'n':>5}  " + "  ".join(f"{v:>{4 * len(all_seeds)}}" for v in variants))
    for role, games in (("rec", REC), ("ctl", CTL)):
        for n in games:
            cells = []
            for v in variants:
                cells.append("".join(f"{got[(v, n, s)]['short']:>4}" if (v, n, s) in got else "   ." for s in all_seeds))
            print(f"{role:4} {n:>5}  " + "  ".join(cells))
    print(f"(seeds {', '.join(map(str, all_seeds))})")
    print()

    print("by variant" + (f", seeds {sorted(seeds)}" if seeds else ", all seeds"))
    head = ("variant", "rec plays", "rec games", "ctl missed", "rec work M", "rec s", "ctl work M", "ctl s",
            "ctl to opt M")
    print("  ".join(f"{h:>12}" for h in head))
    for v in variants:
        row = {}
        for role, games in (("rec", REC), ("ctl", CTL)):
            mine = [(n, s, p) for (vv, n, s), p in got.items() if vv == v and n in games and (seeds is None or s in seeds)]
            row[role] = mine
        rec, ctl = row["rec"], row["ctl"]
        rec_reached = sum(p["short"] == 0 for _, _, p in rec)
        rec_games = len({n for n, _, p in rec if p["short"] == 0})
        ctl_missed = [(n, s) for n, s, p in ctl if p["short"] != 0]
        to_opt = [p["to_opt"] for _, _, p in ctl if p["to_opt"] is not None]
        cells = (
            v,
            f"{rec_reached}/{len(rec)}",
            f"{rec_games}/{len({n for n, _, _ in rec})}",
            f"{len(ctl_missed)}/{len(ctl)}",
            f"{sum(p['work'] for _, _, p in rec) / 1e6:.2f}",
            f"{sum(p['seconds'] for _, _, p in rec):.0f}",
            f"{sum(p['work'] for _, _, p in ctl) / 1e6:.2f}",
            f"{sum(p['seconds'] for _, _, p in ctl):.0f}",
            f"{sum(to_opt) / 1e6:.2f}",
        )
        print("  ".join(f"{c:>12}" for c in cells))
        if ctl_missed:
            print(f"{'':12}  controls missed: {ctl_missed}")
    print()
    print("work M: millions of work over the set's plays (both plays of a game played twice); s: wall seconds summed;")
    print("ctl to opt M: the work at which each control's play first scored opt(n), summed over the plays that did")


if __name__ == "__main__":
    main()
