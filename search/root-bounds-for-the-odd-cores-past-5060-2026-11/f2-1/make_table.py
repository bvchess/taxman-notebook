#!/usr/bin/env python3
"""table.md from out/*.json: the split's X-term at each board and at the other peels' X* (item 1), the counts of smooth
configurations near E(empty set) (item 4), and the largest X-term found by the search over hub sets or the hill climb
(item 2).

Usage: python3 -I make_table.py > table.md
"""

import glob
import json
import os

DIR = "/home/brian/taxman_work/lab/work/oddcore/f2-1"

# study-2/exp_d_{1000,1500,2000}.log: E(X*), F(X*), and the X-term less opt.
PYTHON = {1000: (17436, 6821, 89), 1500: (34356, 20909, 178), 2000: (52591, 42306, 12)}


def load():
    """(n, run) -> the run's JSON lines, for out/N_RUN.json: RUN is the peel of an X-term (xstar, xstar_asc,
    xstar_desc), enum (item 4), maxx or localR (item 2)."""
    runs = {}
    for path in glob.glob(os.path.join(DIR, "out", "*.json")):
        name = os.path.basename(path)[:-5]
        n, run = name.split("_", 1)
        lines = [json.loads(t) for t in open(path).read().splitlines() if t.strip()]
        if lines:
            runs[(int(n), run)] = lines
    return runs


def num(v):
    return "—" if v is None else f"{v:,}"


def main():
    runs = load()
    terms = {k: v[0] for k, v in runs.items() if k[1].startswith("xstar")}
    print("## Item 1: the X\\*-term")
    print()
    print("| n | gap | hubs | X\\* | S\\*'s smooth part | E(X\\*) | smooth side | S\\*'s fiber part | F(X\\*) "
          "| fiber side | E + F − opt | share lost | share closed | E nodes | s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (n, peel), d in sorted(terms.items()):
        if peel != "xstar":
            continue
        if d["finished"]:
            e, side, tg = num(d["E"]), num(d["smooth_side"]), num(d["term_gap"])
            lost = f"{100 * d['share_lost']:.1f}%"
            closed = f"{100 * (1 - d['share_lost']):.1f}%"
        else:
            e = f"{num(d['E_lower'])} to {num(d['E_upper'])}"
            side = f"{num(d['E_lower'] - d['S_smooth'])} to {num(d['smooth_side_upper'])}"
            tg = f"{num(d['term_gap_lower'])} to {num(d['term_gap_upper'])}"
            lost = f"{100 * d['share_lost_lower']:.1f}% to {100 * d['share_lost_upper']:.1f}%"
            closed = f"{100 * (1 - d['share_lost_upper']):.1f}% to {100 * (1 - d['share_lost_lower']):.1f}%"
        print(f"| {n} | {num(d['gap'])} | {d['hubs']} | {d['X']} | {num(d['S_smooth'])} | {e} | {side} "
              f"| {num(d['S_fiber'])} | {num(d['F'])} | {num(d['fiber_side'])} | {tg} | {lost} | {closed} "
              f"| {num(d['processed'])} | {d['seconds']:.0f} |")
    print()
    print("Against the Python study (study-2/exp_d_N.log): E(X\\*), F(X\\*), E + F − opt.")
    print()
    print("| n | Python | Rust | agree |")
    print("|---|---|---|---|")
    for n, (e, f, g) in sorted(PYTHON.items()):
        d = terms.get((n, "xstar"))
        if d is None:
            continue
        mine = (d["E"], d["F"], d["term_gap"])
        print(f"| {n} | {e:,}, {f:,}, {g} | {num(mine[0])}, {num(mine[1])}, {num(mine[2])} "
              f"| {'yes' if mine == (e, f, g) else 'no'} |")
    others = [(k, d) for k, d in sorted(terms.items()) if k[1] != "xstar"]
    if others:
        print()
        print("At the X\\* of other peels (the same peel, members and columns scanned in ascending or descending order):")
        print()
        print("| n | peel | X\\* | E(X\\*) | smooth side | F(X\\*) | fiber side | E + F − opt | share lost | E nodes | s |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for (n, peel), d in others:
            if d["finished"]:
                e, side, tg = num(d["E"]), num(d["smooth_side"]), num(d["term_gap"])
                lost = f"{100 * d['share_lost']:.1f}%"
            else:
                e = f"{num(d['E_lower'])} to {num(d['E_upper'])}"
                side = f"{num(d['E_lower'] - d['S_smooth'])} to {num(d['smooth_side_upper'])}"
                tg = f"{num(d['term_gap_lower'])} to {num(d['term_gap_upper'])}"
                lost = f"{100 * d['share_lost_lower']:.1f}% to {100 * d['share_lost_upper']:.1f}%"
            print(f"| {n} | {peel[6:]} | {d['X']} | {e} | {side} | {num(d['F'])} | {num(d['fiber_side'])} | {tg} "
                  f"| {lost} | {num(d['processed'])} | {d['seconds']:.0f} |")

    enums = [(n, v[-1]) for (n, run), v in sorted(runs.items()) if run == "enum"]
    if enums:
        print()
        print("## Item 4: smooth configurations within m of E(X), X empty")
        print()
        print("| n | E(∅) | E nodes | m | configurations | final | enumeration nodes | enumeration s |")
        print("|---|---|---|---|---|---|---|---|")
        for n, d in enums:
            for m, c, fin in zip(d["margins"], d["counts"], d["final"]):
                print(f"| {n} | {num(d['E'])} | {num(d['E_nodes'])} | {m} | {num(c)} | {'yes' if fin else 'no'} "
                      f"| {num(d['processed'])} | {d['enumeration_s']:.0f} |")

    climbs = [(n, run, v[-1]) for (n, run), v in sorted(runs.items()) if run == "maxx" or run.startswith("local")]
    climbs = [(n, run, d) for n, run, d in climbs if "term_gap" in d and "E_runs" in d]
    if climbs:
        print()
        print("## Item 2: the largest X-term against the X\\*-term")
        print()
        print("| n | gap | method | X\\*-term − opt | best found − opt | best − X\\*-term | share of gap | done "
              "| hubs added, removed | E runs | s |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for n, run, d in climbs:
            if run == "maxx":
                method = "search over hub sets"
                best, diff, share, done = d["max_gap"], d["max_minus_term"], d["share_of_gap"], d["finished"]
            else:
                method = f"hill climb, radius {d['radius']}"
                best, diff, share, done = d["best_gap"], d["best_minus_term"], d["share_of_gap"], d["complete"]
            moved = f"{d['best_x_added']}, {d['best_x_removed']}"
            print(f"| {n} | {num(d['gap'])} | {method} | {num(d['term_gap'])} | {num(best)} | {num(diff)} "
                  f"| {100 * share:.1f}% | {'yes' if done else 'no'} | {moved} | {num(d['E_runs'])} "
                  f"| {d['search_s']:.0f} |")


if __name__ == "__main__":
    main()
