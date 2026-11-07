#!/usr/bin/env python3
"""The statistics of the prover's run of 2 to 2530 that the entry quotes, from the committed file.

    python3 -I run_stats.py solver/noframe/data/exact_parity_2_2530.jsonl

Prints the totals, the cost by band of 100 in n (as a Markdown table), the dearest games, the shares of the dearest, the
time of a node by the threads a game ran on, and the games of 1301-2175 beside the cloud run of 2026-10 when the two
files of that run are given after it:  ... FILE OLD_2_1300 OLD_1301_2175  (`git show` of the retired files at the
commit before the one that records this run).
"""

import json
import statistics
import sys
from collections import Counter

BAND = 100


def lines(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def hours(thread_seconds):
    """Thread-hours as the tables print them."""
    if thread_seconds < 18:
        return "< 0.01"
    return f"{thread_seconds / 3600:,.2f}" if thread_seconds < 36000 else f"{thread_seconds / 3600:,.1f}"


def totals(rows, searched):
    nodes = sum(r["nodes"] for r in searched)
    seconds = sum(r["ts"] for r in searched)
    print(f"{len(rows)} lines, {len(searched)} searches, {nodes:,} nodes, {seconds / 3600:,.1f} thread-hours, "
          f"{1000 * seconds / nodes:.2f} ms a node")
    skipped = [r for r in rows if r["search"] != "proven"]
    print(f"the {len(skipped)} games with no search took {sum(r['secs'] for r in skipped):.0f} s in all "
          f"(longest {max(r['secs'] for r in skipped):.2f} s)")
    for lo, hi in [(2, 1300), (1301, 2175), (2176, 2530)]:
        part = [r for r in searched if lo <= r["n"] <= hi]
        games = [r for r in rows if lo <= r["n"] <= hi]
        kinds = Counter("search" if r["search"] == "proven" else r["relation"] for r in games)
        print(f"{lo}-{hi}: {len(games)} games {dict(kinds)}; searches {len(part)}, "
              f"{sum(r['nodes'] for r in part):,} nodes, {sum(r['ts'] for r in part) / 3600:.2f} thread-hours")
    threads = Counter(r["threads"] for r in searched)
    print(f"{sum(v for k, v in threads.items() if k > 1)} searches ran on more than one thread, "
          f"at most {max(threads)}")


def by_band(searched):
    print("\n| n | searches | the root's parity gap (mean) | median nodes | most nodes | nodes | thread-hours "
          "| ms a node |")
    print("|---|---|---|---|---|---|---|---|")
    for lo in range(0, 2600, BAND):
        part = [r for r in searched if lo <= r["n"] < lo + BAND]
        if not part:
            continue
        top = max(part, key=lambda r: r["nodes"])
        nodes = sum(r["nodes"] for r in part)
        seconds = sum(r["ts"] for r in part)
        gap = statistics.mean(r["gap"] for r in part)
        print(f"| {max(lo, 2)}–{min(lo + BAND - 1, 2530)} | {len(part)} | {gap:.0f} | "
              f"{statistics.median(r['nodes'] for r in part):,.0f} | {top['nodes']:,} ({top['n']}) | {nodes:,} | "
              f"{hours(seconds)} | {1000 * seconds / nodes:.2f} |")


def dearest(searched):
    total = sum(r["ts"] for r in searched)
    ranked = sorted(searched, key=lambda r: -r["ts"])
    print("\n| n | root gap | nodes | thread-hours | wall hours | threads | ms a node |")
    print("|---|---|---|---|---|---|---|")
    for r in ranked[:12]:
        print(f"| {r['n']} | {r['gap']:,} | {r['nodes']:,} | {r['ts'] / 3600:,.1f} | {r['secs'] / 3600:.1f} | "
              f"{r['threads']} | {1000 * r['ts'] / r['nodes']:.2f} |")
    for k in (1, 5, 10, 50):
        print(f"the {k} dearest: {100 * sum(r['ts'] for r in ranked[:k]) / total:.1f}% of the thread-hours")
    print(f"games past 2175: {100 * sum(r['ts'] for r in searched if r['n'] > 2175) / total:.1f}%; "
          f"2300-2399: {100 * sum(r['ts'] for r in searched if 2300 <= r['n'] < 2400) / total:.1f}%")
    for name, count in [("a million nodes", 1e6), ("ten million", 1e7), ("a hundred million", 1e8)]:
        print(f">= {name}: {sum(1 for r in searched if r['nodes'] >= count)}")
    for name, count in [("a thread-hour", 3600), ("ten", 36000), ("a hundred", 360000)]:
        print(f">= {name}: {sum(1 for r in searched if r['ts'] >= count)}")


def node_time_by_threads(searched):
    print("\nms a node by the threads of a game")
    classes = [("1 thread", 1, 1), ("2-8", 2, 8), ("9-87", 9, 87), ("88", 88, 88)]
    for lo, hi in [(900, 1999), (2000, 2199), (2200, 2530)]:
        for name, a, b in classes:
            part = [r for r in searched if lo <= r["n"] <= hi and a <= r["threads"] <= b]
            if part:
                nodes = sum(r["nodes"] for r in part)
                seconds = sum(r["ts"] for r in part)
                print(f"  {lo}-{hi}, {name}: {len(part)} games, {nodes / 1e6:.2f}M nodes, {seconds / 3600:.1f} "
                      f"thread-hours, {1000 * seconds / nodes:.2f} ms a node")


def beside_the_cloud_run(new, old_files):
    old = {}
    for path in old_files:
        old.update({r["n"]: r for r in lines(path)})
    for lo, hi in [(2, 1300), (1301, 2175)]:
        before = [n for n in range(lo, hi + 1) if old[n]["search"] == "proven"]
        now = [n for n in range(lo, hi + 1) if new[n]["search"] == "proven"]
        both = [n for n in now if old[n]["search"] == "proven"]
        only = [n for n in before if new[n]["search"] != "proven"]

        def spent(file, ns):
            seconds = sum(file[n].get("thread_secs", file[n]["secs"]) for n in ns)
            return sum(file[n]["nodes"] for n in ns), seconds / 3600

        print(f"\n{lo}-{hi}: old run {len(before)} searches, {spent(old, before)[0]:,} nodes, "
              f"{spent(old, before)[1]:.1f} thread-hours; this run {len(now)}, {spent(new, now)[0]:,} nodes, "
              f"{spent(new, now)[1]:.2f} thread-hours")
        print(f"  searched by both: {len(both)}, old {spent(old, both)[0]:,} nodes, new {spent(new, both)[0]:,}; "
              f"searched by the old only: {len(only)}, {spent(old, only)[0]:,} nodes, {spent(old, only)[1]:.1f} "
              f"thread-hours, now {Counter(new[n]['relation'] for n in only)}")


def main():
    rows = lines(sys.argv[1])
    for r in rows:
        r["ts"] = r["thread_secs"]
        r["gap"] = r["parity_bound"] - r["score"]
    searched = [r for r in rows if r["search"] == "proven"]
    totals(rows, searched)
    by_band(searched)
    dearest(searched)
    node_time_by_threads(searched)
    if len(sys.argv) > 2:
        beside_the_cloud_run({r["n"]: r for r in rows}, sys.argv[2:])


if __name__ == "__main__":
    main()
