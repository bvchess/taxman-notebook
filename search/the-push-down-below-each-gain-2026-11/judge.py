#!/usr/bin/env python3
"""Judge the mini-pass: arm t (below pass 2's breakthroughs) against arm c (random windows)."""
import glob
import json
import os
import sys

RUN = "/home/brian/taxman_work/lab/work/unsound-run"
THREADS = 20


def windows(arm):
    out = []
    for path in sorted(glob.glob(f"{RUN}/mini/{arm}/w*.jsonl")):
        lo, hi = map(int, os.path.basename(path)[1:-6].split("-"))
        out.append((lo, hi, path))
    return out


def main():
    bk_lines = [json.loads(t) for t in open(f"{RUN}/best-known.jsonl")]
    for arm in ("t", "c"):
        ws = windows(arm)
        names = {os.path.basename(p) for _, _, p in ws}
        raised = {}  # n -> (gain over was, line)
        for d in bk_lines:
            bk = d.get("best_known") or {}
            if bk.get("file") in names:
                was = bk.get("was")
                first = raised.get(d["n"], (None, None, was))[2]
                raised[d["n"]] = (d["score"] - first, d, first)
        seconds = work = games = 0
        bad = 0
        for lo, hi, path in ws:
            lines = [json.loads(t) for t in open(path)]
            ns = {d["n"] for d in lines}
            if ns != set(range(lo, hi + 1)):
                print(arm, path, "games", sorted(ns)[:3], "not", lo, hi)
            for d in lines:
                if d.get("repaired") is None:
                    seconds += d["seconds"]
                    work += d["work"]
                    games += 1
                if d["score"] > d["bound"]:
                    bad += 1
        roots = [n for n in sorted(raised) if n - 1 not in raised]
        gains = sorted(g for g, _, _ in raised.values())
        th = seconds * THREADS / 3600
        print(f"arm {arm}: {len(ws)} windows, {games} games, {seconds:.0f} s, {th:.1f} thread-hours, work {work/1e6:.1f} M, "
              f"lines above the bound {bad}")
        print(f"  raised {len(raised)} games in {len(roots)} streaks, {sum(gains)} points, median {gains[len(gains)//2] if gains else 0}"
              f"; {len(roots)/th:.2f} streaks and {len(raised)/th:.2f} games per thread-hour")
        for lo, hi, path in ws:
            r = [n for n in raised if lo <= n <= hi]
            if not r:
                continue
            desc = []
            for n in sorted(r):
                g, d, _ = raised[n]
                src = ""
                if d.get("repaired"):
                    src = f"R{d['repaired']['from'] - n:+d}"
                elif d.get("improvements"):
                    t = d["improvements"][-1]["trajectory"]
                    k = d["trajectories"][t]
                    src = "start" if k == "start" else f"T{k - n:+d}"
                else:
                    src = "C" if d.get("at_ceiling") else "P"
                desc.append(f"{n}:+{g}({src})")
            print(f"  w{lo}-{hi} top+1={hi+1}: " + " ".join(desc))


if __name__ == "__main__":
    main()
