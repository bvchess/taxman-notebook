#!/usr/bin/env python3
"""The rehearsal states after passes 2 and 3, and their roots.

    cd /home/brian/taxman_work/lab/work/sampling/calib && nice -n 19 python3 -I make_states.py

A rehearsal's best-known file (lab/work/rehearsal{,2,3}/best-known.jsonl) is append-only and each line names the pass
file it came from (best_known.file, p1.jsonl to p4.jsonl), so the state after pass k is the file's lines from p1 to pk,
in order.  This writes states/RrPk.jsonl for r = 1, 2, 3 and k = 2, 3, checks each state's scores against the
rehearsal's own scores-k.json (written by its score.py after pass k), and writes roots.csv: every game of 3001-5060
short in a state (best-known score below opt(n) of results/optimal.jsonl.gz), with its streak, whether it is the root
of its streak (short while n - 1 is not), and the line's method and at_ceiling.  The source files are only read.
"""

import csv
import gzip
import json
import os

WORK = "/home/brian/taxman_work/lab/work"
TABLE = "/home/brian/taxman_work/research/results/optimal.jsonl.gz"
REHEARSALS = {1: "rehearsal", 2: "rehearsal2", 3: "rehearsal3"}
PASSES = (2, 3)
LO, HI = 3001, 5060
HERE = os.path.dirname(os.path.abspath(__file__))


def opt_table():
    opt = {}
    with gzip.open(TABLE, "rt") as f:
        for text in f:
            line = json.loads(text)
            if LO - 1 <= line["n"] <= HI:
                opt[line["n"]] = line["score"]
    return opt


def main():
    opt = opt_table()
    rows = []
    for r, folder in REHEARSALS.items():
        src = os.path.join(WORK, folder, "best-known.jsonl")
        with open(src) as f:
            texts = [t for t in f if t.strip()]
        for k in PASSES:
            keep = {f"p{j}.jsonl" for j in range(1, k + 1)}
            state = [t for t in texts if json.loads(t)["best_known"]["file"] in keep]
            out = os.path.join(HERE, "states", f"R{r}P{k}.jsonl")
            with open(out, "w") as f:
                f.writelines(state)
            best, last = {}, {}
            for t in state:
                line = json.loads(t)
                best[line["n"]] = max(best.get(line["n"], 0), line["score"])
                last[line["n"]] = line
            with open(os.path.join(WORK, folder, f"scores-{k}.json")) as f:
                theirs = {int(n): s for n, s in json.load(f)["scores"].items()}
            differ = [n for n in range(LO, HI + 1) if best.get(n) != theirs.get(n)]
            short = [n for n in range(LO, HI + 1) if best[n] < opt[n]]
            print(f"R{r}P{k}: {len(state)} lines, games {len(best)}, against scores-{k}.json: {len(differ)} differ "
                  f"{differ[:5]}; short {len(short)}")
            shortset = set(short)
            for n in short:
                root = n - 1 not in shortset
                lo = n
                while lo - 1 in shortset:
                    lo -= 1
                hi = n
                while hi + 1 in shortset:
                    hi += 1
                line = last[n]
                rows.append({"state": f"R{r}P{k}", "n": n, "streak": f"{lo}-{hi}", "root": "yes" if root else "no",
                             "short_by": opt[n] - best[n], "method": line.get("method"),
                             "at_ceiling": line.get("at_ceiling"), "known": best[n], "opt": opt[n]})
    with open(os.path.join(HERE, "roots.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
