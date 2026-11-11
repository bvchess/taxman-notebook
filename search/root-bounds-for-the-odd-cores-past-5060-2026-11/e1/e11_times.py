#!/usr/bin/env python3
"""E11's times, read off the progress lines of a PB_sh run (logs/hubs-N-23.log, 2 s apart on 16 threads): when its
open bound first passes PB_s (the E1 value), and the share its bound has reached at 2 × E1's wall time and at the
point of equal CPU, 2 × E1's thread-seconds (E1 ran on 4 threads, so 0.5 × E1's wall time on 16).

    python3 -I e11_times.py N [N ...]
"""

import json
import re
import sys

E1 = "/home/brian/taxman_work/lab/work/oddcore/e1/results.jsonl"
HUBS = "/home/brian/taxman_work/lab/work/oddcore/e1/hubs.jsonl"
LINE = re.compile(r"\[([\d.]+) s\] processed (\d+) open (\d+) best (\d+) upper (\d+)")


def main():
    e1 = {}
    for raw in open(E1):
        d = json.loads(raw)
        if d["B"] == 23 and d["finished"]:
            e1[d["n"]] = d
    for n in map(int, sys.argv[1:]):
        d = e1[n]
        pb, gap, pbs, t1, threads = d["PB"], d["gap"], d["PB_s"], d["seconds"], d["threads"]
        rows = [tuple(map(float, m.groups())) for m in map(LINE.match, open(f"logs/hubs-{n}-23.log")) if m]
        share = lambda upper: 100 * (pb - upper) / gap

        def at(t):
            seen = [r for r in rows if r[0] <= t]
            return f"{share(seen[-1][4]):.1f}% at {seen[-1][0]:.1f} s" if seen else f"before the first line ({rows[0][0]} s)"

        passed = next((r for r in rows if r[4] <= pbs), None)
        out = {
            "n": n,
            "PB_s share": f"{share(pbs):.1f}%",
            "E1 wall s (threads)": f"{t1} ({threads})",
            "passes PB_s at": f"{passed[0]:.1f} s, {int(passed[1])} nodes" if passed else "not in the log",
            "share at 2 x E1 wall": at(2 * t1),
            "share at 2 x E1 thread-s": at(2 * t1 * threads / 16),
            "last line": f"{share(rows[-1][4]):.1f}% at {rows[-1][0]:.1f} s, {int(rows[-1][1])} nodes",
        }
        for raw in open(HUBS):
            h = json.loads(raw)
            if h["n"] == n and h["threads"] == 16:
                up = h["PB_s"] if h["finished"] else h["PB_s_upper"]
                out["PB_sh"] = f"{'' if h['finished'] else '<= '}{up:,}, share {'' if h['finished'] else '>= '}" + \
                    f"{share(up):.1f}%, {h['processed']:,} nodes, {h['seconds']:.0f} s, finished {h['finished']}"
        print(json.dumps(out))


if __name__ == "__main__":
    main()
