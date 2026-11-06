#!/usr/bin/env python3
"""Experiment E0 of the unsound mode: where each searched game's best score came from, and how much work it took.

Reads the result lines and the profiles of the run of 2026-11-01 (read-only), writes games.json (one record per game
of method search or start) and prints the numbers of the entry's tables.

    nice -n 19 python3 -I collect.py [DATA_DIR] [OUT_DIR]

A profile is streamed line by line; its `node` lines (the bulk of it) are skipped, the `steps` lines (which carry the
search's own clock, `active`) and the `open` lines (the incumbent at each checkpoint) are read from their first bytes.
"""
import bisect
import json
import os
import re
import statistics
import sys
from multiprocessing import Pool

DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/taxman_work/chain2-data")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
PROCESSES = 4

STEPS = re.compile(rb'"seq":(\d+),"nodes":(\d+),"counted":\d+,"active":([0-9.]+)')
OPEN = re.compile(rb'"seq":(\d+),"nodes":(\d+),"incumbent":(\d+)')
NODE0 = re.compile(rb'"bound":(-?\d+),"need":(-?\d+),"gap":(-?\d+)')

STRETCHES = [(1, 1000), (1001, 2000), (2001, 3000), (3001, 4000), (4001, 4400), (4401, 4800), (4801, 5060)]


def read_profile(path):
    """The start's incumbent, the root's bound, the checkpoints (active, nodes, incumbent) and the end."""
    start = root = end = None
    clock = {}
    opens = []
    with open(path, "rb") as f:
        for line in f:
            if line.startswith(b'{"kind":"node"'):
                if root is None and line.startswith(b'{"kind":"node","id":0,'):
                    m = NODE0.search(line)
                    root = {"bound": int(m.group(1)), "need": int(m.group(2)), "gap": int(m.group(3))}
                continue
            if line.startswith(b'{"kind":"steps"'):
                m = STEPS.search(line[:200])
                clock[int(m.group(1))] = (float(m.group(3)), int(m.group(2)))
            elif line.startswith(b'{"kind":"open"'):
                m = OPEN.search(line[:200])
                seq = int(m.group(1))
                active, nodes = clock.get(seq, (None, int(m.group(2))))
                opens.append((active, nodes, int(m.group(3))))
            elif line.startswith(b'{"kind":"start"'):
                start = json.loads(line)
            elif line.startswith(b'{"kind":"end"'):
                end = json.loads(line)
    return start, root, opens, end, clock


def active_at_nodes(clock, nodes):
    """The search's own clock when it had taken `nodes` steps, interpolated between its `steps` lines (None if there
    are none)."""
    pts = sorted((n, a) for a, n in clock.values())
    if not pts:
        return None
    xs = [p[0] for p in pts]
    i = bisect.bisect_left(xs, nodes)
    if i == 0:
        return pts[0][1] * nodes / pts[0][0] if pts[0][0] else 0.0
    if i >= len(pts):
        return pts[-1][1]
    (n0, a0), (n1, a1) = pts[i - 1], pts[i]
    return a0 + (a1 - a0) * (nodes - n0) / (n1 - n0) if n1 > n0 else a1


def analyze(args):
    r, path = args
    n = r["n"]
    opt = r["score"] - r["in_the_bag"]
    eng = r.get("engine") or {}
    fin = eng.get("finder")
    g = {
        "n": n, "method": r["method"], "proof": r["proof"], "opt": opt, "cap": r["setup"]["cap"],
        "greedy": r["setup"]["greedy_sum"], "nodes": r["nodes"], "active": r["seconds"]["active_all_runs"],
        "cpu": r["seconds"]["cpu_all_runs"], "finder": fin,
    }
    if path is None:
        # A start that met the ceiling needed no search: its game is the start's.
        g.update(start=opt, bound=None, root_gap=None, start_met_bound=None, source="start", t_lo=0.0, t_hi=0.0,
                 nodes_at_opt=0, improvements=[])
        return g
    start, root, opens, end, clock = read_profile(path)
    s = start["incumbent"]
    g.update(start=s, bound=root["bound"], root_gap=root["gap"], start_met_bound=s >= root["bound"])
    g["end_active"] = end["active"] if end else None
    # Increases of the incumbent between the checkpoints: (own clock of the checkpoint, nodes, incumbent).
    imp = []
    last = s
    for a, nd, inc in opens:
        if inc > last:
            imp.append((a, nd, inc))
            last = inc
    g["improvements"] = imp
    g["finder_started_at"] = active_at_nodes(clock, fin["at_nodes"]) if fin else None
    if s >= opt:
        g.update(source="start", t_lo=0.0, t_hi=0.0, nodes_at_opt=0)
    elif fin and fin["from"] >= opt:
        g.update(source="tree_before_finder", t_lo=None, t_hi=g["finder_started_at"], nodes_at_opt=fin["at_nodes"])
    elif fin and fin["best"] >= opt:
        # The finder's own clock (found) counts from its start; the search's own clock at its start is interpolated.
        t0 = g["finder_started_at"] or 0.0
        g.update(source="finder", t_lo=t0, t_hi=t0 + fin["found_seconds"], nodes_at_opt=None)
    else:
        # The tree search: between the last checkpoint below the optimum and the first at or above it.
        below = [(a, nd) for a, nd, inc in [(0.0, 0, s)] + opens if inc < opt]
        above = [(a, nd) for a, nd, inc in opens if inc >= opt]
        lo = below[-1][0] if below else 0.0
        hi, nd = above[0] if above else (g["end_active"], r["nodes"])
        g.update(source="tree", t_lo=lo, t_hi=hi, nodes_at_opt=nd)
    return g


def quantiles(xs):
    if not xs:
        return None
    xs = sorted(xs)
    return (statistics.median(xs), xs[min(len(xs) - 1, int(0.9 * len(xs)))], xs[-1])


def fmt(q, p=1):
    return "-" if q is None else "/".join(f"{x:.{p}f}" for x in q)


def stretch_of(n):
    for lo, hi in STRETCHES:
        if lo <= n <= hi:
            return (lo, hi)


def main():
    recs = {}
    with open(os.path.join(DATA, "results/strict.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            recs[r["n"]] = r
    assert len(recs) == 5060 and all(r["completed"] for r in recs.values())
    jobs = []
    for n in sorted(recs):
        r = recs[n]
        if r["method"] in ("search", "start"):
            p = os.path.join(DATA, "profile", f"n{n:04d}.profile.jsonl")
            jobs.append((r, p if os.path.exists(p) else None))
    with Pool(PROCESSES) as pool:
        games = pool.map(analyze, jobs, chunksize=8)
    with open(os.path.join(OUT, "games.json"), "w") as f:
        json.dump(games, f, separators=(",", ":"))

    print("== methods by stretch (count; share taking the game before = prime+repeat+start)")
    for lo, hi in STRETCHES:
        ns = [n for n in recs if lo <= n <= hi]
        c = {}
        for n in ns:
            c[recs[n]["method"]] = c.get(recs[n]["method"], 0) + 1
        take = c.get("prime", 0) + c.get("repeat", 0) + c.get("start", 0)
        print(f"{lo}-{hi}: {len(ns)} games " + " ".join(f"{k}={c.get(k, 0)}" for k in
              ("trivial", "prime", "repeat", "start", "search")) + f"  from-game-before {100 * take / len(ns):.1f}%")
    c = {}
    for r in recs.values():
        c[r["method"]] = c.get(r["method"], 0) + 1
    print("all:", c)

    searched = [g for g in games if g["method"] == "search"]
    print(f"\n== searched games: {len(searched)}; with profile {sum(1 for g in searched if g['bound'] is not None)}")
    print("stretch | searched | start optimal | start met root bound | opt = root bound | opt = cap | "
          "finder: n, share, found s med/p90/max | tree: n, share, t_hi s med/p90/max | "
          "shortfall (where short) n, med/p90/max | shortfall rel med/max")
    for lo, hi in STRETCHES + [(1, 5060)]:
        sel = [g for g in searched if lo <= g["n"] <= hi]
        if not sel:
            continue
        k = len(sel)
        pct = lambda x: f"{100 * x / k:.1f}%"
        s_opt = [g for g in sel if g["source"] == "start"]
        met = [g for g in sel if g["start_met_bound"]]
        eqb = [g for g in sel if g["opt"] >= g["bound"]]
        eqc = [g for g in sel if g["opt"] >= g["cap"]]
        fi = [g for g in sel if g["source"] == "finder"]
        tr = [g for g in sel if g["source"] == "tree"]
        tb = [g for g in sel if g["source"] == "tree_before_finder"]
        short = [g for g in sel if g["start"] < g["opt"]]
        sf = [g["opt"] - g["start"] for g in short]
        sr = [(g["opt"] - g["start"]) / g["opt"] for g in short]
        print(f"{lo}-{hi} | {k} | {len(s_opt)} {pct(len(s_opt))} | {len(met)} {pct(len(met))} | {len(eqb)} {pct(len(eqb))} | "
              f"{len(eqc)} {pct(len(eqc))} | {len(fi)} {pct(len(fi))} {fmt(quantiles([g['finder']['found_seconds'] for g in fi]))} | "
              f"{len(tr)}+{len(tb)} {pct(len(tr) + len(tb))} {fmt(quantiles([g['t_hi'] for g in tr]))} | "
              f"{len(short)} {fmt(quantiles(sf), 0)} | {fmt(quantiles(sr), 5)}")

    print("\n== work: own time of searched games (hours), time to the optimum (upper bound) and the rest")
    for lo, hi in STRETCHES + [(1, 5060)]:
        sel = [g for g in searched if lo <= g["n"] <= hi]
        tot = sum(g["active"] for g in sel) / 3600
        hold = sum(min(g["t_hi"] if g["t_hi"] is not None else g["active"], g["active"]) for g in sel) / 3600
        nofin = [g for g in sel if g["finder"] is None]
        print(f"{lo}-{hi}: active {tot:.2f} h; optimum held by (upper bound) {hold:.3f} h = {100 * hold / tot:.2f}%; "
              f"games without finder {len(nofin)} ({sum(g['active'] for g in nofin) / 3600:.2f} h); "
              f"median active {statistics.median(g['active'] for g in sel):.3f} s")

    print("\n== games whose start fell short: n, opt, start, shortfall, root bound, source, finder found, "
          "t range, active")
    short = sorted((g for g in searched if g["start"] < g["opt"]), key=lambda g: -g["opt"] + g["start"])
    for g in short[:25]:
        print(g["n"], g["opt"], g["start"], g["opt"] - g["start"], g["bound"], g["source"],
              g["finder"] and round(g["finder"]["found_seconds"], 1), g["t_lo"], g["t_hi"], round(g["active"], 1))
    print("\nsources of the optimum, all searched:",
          {s: sum(1 for g in searched if g["source"] == s) for s in
           ("start", "finder", "tree", "tree_before_finder")})
    fin_late = [g for g in searched if g["finder"] is None]
    print("searched games with no finder (search ended before 1,000,000 steps):", len(fin_late),
          "of which start short:", sum(1 for g in fin_late if g["start"] < g["opt"]))
    big = [g for g in searched if g["finder"] and g["finder"]["seconds"] < 899 and g["start"] < g["opt"]]
    print("finder ended before its 900 s budget while start short:", len(big))
    bg = [g["bound"] - g["opt"] for g in searched if g["bound"] is not None]
    print("root bound minus optimum (searched): quantiles med/p90/max", fmt(quantiles(bg), 0))
    gaps = [(g["bound"] - g["opt"]) / g["opt"] for g in searched if g["bound"] is not None and g["n"] >= 1000]
    print("relative root gap n>=1000 med/p90/max", fmt(quantiles(gaps), 5))
    bs = [g["bound"] - g["start"] for g in searched if g["bound"] is not None]
    print("root bound minus start: med/p90/max", fmt(quantiles(bs), 0))
    ms = [g for g in games if g["method"] == "start"]
    print("method start:", len(ms), "median active s", statistics.median(g["active"] for g in ms),
          "greedy<opt:", sum(1 for g in ms if g["greedy"] < g["opt"]))
    sel = searched
    print("greedy vs start vs opt (searched): greedy==opt", sum(1 for g in sel if g["greedy"] >= g["opt"]),
          "start>greedy", sum(1 for g in sel if g["start"] > g["greedy"]),
          "start==greedy", sum(1 for g in sel if g["start"] == g["greedy"]))
    for lo, hi in STRETCHES:
        sel2 = [g for g in searched + ms if lo <= g["n"] <= hi and g["greedy"] is not None]
        print(f"{lo}-{hi} greedy already optimal {sum(1 for g in sel2 if g['greedy'] >= g['opt'])}/{len(sel2)}")

    extras(searched)
    setup_cost(recs)


def extras(searched):
    """How early the optimum was held, and how far the data pins it."""
    print("\n== share of searched games holding the optimum by T own seconds (upper bound t_hi), by stretch")
    marks = (0, 1, 10, 60, 300, 900, 3600)
    print("stretch | n | " + " | ".join(f"<={m}s" for m in marks))
    for lo, hi in STRETCHES + [(1, 5060)]:
        sel = [g for g in searched if lo <= g["n"] <= hi]
        row = []
        for m in marks:
            k = sum(1 for g in sel if (g["t_hi"] if g["t_hi"] is not None else 0.0) <= m)
            row.append(f"{100 * k / len(sel):.1f}%")
        print(f"{lo}-{hi} | {len(sel)} | " + " | ".join(row))
    print("\n== games whose start fell short, by how the optimum was found, by stretch")
    print("stretch | short | no finder (tree) | finder started, tree before it | finder found | finder started, tree found")
    for lo, hi in STRETCHES + [(1, 5060)]:
        sh = [g for g in searched if lo <= g["n"] <= hi and g["start"] < g["opt"]]
        nofin = [g for g in sh if g["finder"] is None]
        tb = [g for g in sh if g["source"] == "tree_before_finder"]
        fi = [g for g in sh if g["source"] == "finder"]
        tr = [g for g in sh if g["source"] == "tree" and g["finder"] is not None]
        print(f"{lo}-{hi} | {len(sh)} | {len(nofin)} | {len(tb)} | {len(fi)} | {len(tr)}")
    tree = [g for g in searched if g["source"] == "tree"]
    pinned = [g for g in tree if g["improvements"] and g["improvements"][-1][0] is not None]
    print("\ntree-found games:", len(tree), "of which a checkpoint line saw the optimum:",
          sum(1 for g in tree if any(i[2] >= g["opt"] for i in g["improvements"])),
          "(the others: only the end of the search is known)")
    print("tree-found, t_hi seconds quantiles med/p90/max:", fmt(quantiles([g["t_hi"] for g in tree])),
          " share of their active time (med):",
          f"{statistics.median(g['t_hi'] / g['active'] for g in tree if g['active'] > 0):.3f}")
    # Finder-found games where a checkpoint line already showed the optimum before the finder's find.
    clash = [g for g in searched if g["source"] == "finder" and any(
        i[2] >= g["opt"] and i[0] is not None and i[0] < g["t_lo"] + g["finder"]["found_seconds"] - 1e-9
        for i in g["improvements"])]
    print("finder-found games where a checkpoint line showed the optimum before the finder's time:", len(clash))
    fin = [g for g in searched if g["source"] == "finder"]
    print("finder-found: improved count quantiles med/p90/max", fmt(quantiles([g["finder"]["improved"] for g in fin])),
          " finder start (own clock) med/p90/max", fmt(quantiles([g["finder_started_at"] for g in fin])),
          " game's active med/p90/max", fmt(quantiles([g["active"] for g in fin])))
    sf = [g for g in searched if g["finder"]]
    print("games with a finder:", len(sf), "ran full 900 s:", sum(1 for g in sf if g["finder"]["seconds"] >= 899),
          "found something better than its start:", sum(1 for g in sf if g["finder"]["best"] > g["finder"]["from"]),
          "finder best < opt (ended short of it):", sum(1 for g in sf if g["finder"]["best"] < g["opt"]),
          "of these start < opt:", sum(1 for g in sf if g["finder"]["best"] < g["opt"] and g["start"] < g["opt"]))
    # Finder where the start was already optimal: it never had a chance to show anything.
    print("games with a finder whose start was optimal:", sum(1 for g in sf if g["start"] >= g["opt"]))
    # Time the tail takes: active after the optimum is held, in hours, by source.
    for s in ("start", "finder", "tree", "tree_before_finder"):
        sel = [g for g in searched if g["source"] == s]
        print(s, len(sel), "games; active h", round(sum(g["active"] for g in sel) / 3600, 2),
              "; held by (upper bound) h", round(sum(g["t_hi"] or 0 for g in sel) / 3600, 3))
    # The hardest: games over an hour.
    big = sorted((g for g in searched if g["active"] > 3600), key=lambda g: g["n"])
    print("\ngames over 1 h active:", len(big), "start optimal:", sum(1 for g in big if g["start"] >= g["opt"]),
          "active h:", round(sum(g["active"] for g in big) / 3600, 1))
    for g in big:
        if g["start"] < g["opt"]:
            print("  short:", g["n"], g["opt"] - g["start"], g["source"], round(g["t_hi"], 1), round(g["active"] / 3600, 2))
    # The root gap against the shortfall: could the bound say the start is near-optimal?
    print("\nroot bound minus start in start-optimal games, med/p90:",
          fmt(quantiles([g["bound"] - g["start"] for g in searched if g["start"] >= g["opt"]]), 0))
    print("root bound minus start in short-start games, med/p90:",
          fmt(quantiles([g["bound"] - g["start"] for g in searched if g["start"] < g["opt"]]), 0))




def setup_cost(recs):
    """What a game that takes its moves from the game before costs: its own active seconds, by method and stretch."""
    print("\n== active seconds of a game by method and stretch (median / p90 / max)")
    for method in ("trivial", "prime", "repeat", "start"):
        for lo, hi in STRETCHES:
            xs = [r["seconds"]["active_all_runs"] for n, r in recs.items() if r["method"] == method and lo <= n <= hi]
            if xs:
                print(f"{method} {lo}-{hi}: {len(xs)} games {fmt(quantiles(xs), 3)}; total {sum(xs):.1f} s")
    tot = sum(r["seconds"]["active_all_runs"] for r in recs.values())
    for method in ("trivial", "prime", "repeat", "start", "search"):
        xs = [r["seconds"]["active_all_runs"] for r in recs.values() if r["method"] == method]
        print(f"{method}: {len(xs)} games, {sum(xs) / 3600:.3f} h = {100 * sum(xs) / tot:.2f}% of {tot / 3600:.2f} h")


if __name__ == "__main__":
    main()
