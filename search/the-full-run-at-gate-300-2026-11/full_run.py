#!/usr/bin/env python3
"""The full run of 2026-11-01 (games 1 to 5060 at a fixed gate of 300) against the October re-run and against the
original file, game by game and by stretch.

Prints the run and its totals, where its hours went, the run against the re-run (games 1 to 4879, one machine) and
against the original file (games 4875 to 5060, the only ones it ran on this machine) by stretch, the dearest games, the
games where the run took longer than the other, and 4983 and 4984, which the gate study left open.

A game's hours are, in each file, the nearest thing it records to the time the game held the chain up:
* the run: `seconds.active_all_runs`, the time the game had at least one worker, from its setup to its line;
* the re-run: `seconds.own`, the time the game was the head of the window (its oldest game) with its search running;
* the original file: `seconds.own` where its line has one (4899 on), else `seconds.search_all_runs`, which also counts
  the time a search was suspended behind older games of the window.
Nodes are the `nodes` of a line, which counts every invocation of a game.

usage: full_run.py
Environment variables (a path ending in .gz is read as gzip):
  NOV1_RESULTS      the run's lines: strict.jsonl of its data folder, or results/optimal.jsonl.gz of the main repository
                    at commit 5bd5d48 (the same lines, byte for byte)
  RERUN_RESULTS     the re-run's lines: strict.jsonl of its data folder (build 3ca11bf, games 1 to 4879 complete)
  ORIGINAL_RESULTS  the original file: what `git show d05191a:results/optimal.jsonl.gz` prints, saved in a file
  NOV1_LOG          the run's logs/chain.log (optional): the solver's own wall time"""
import datetime
import gzip
import json
import os
import re

LAST = 5060
# The stretches of games 1 to 4879 against the re-run, cut at 25 or 50 games where the run's hours turn from fewer than
# the re-run's to more and back.
AGAINST_RERUN = [
    (1, 3075), (3076, 3125), (3126, 3525), (3526, 3625), (3626, 4375), (4376, 4425),
    (4426, 4475), (4476, 4575), (4576, 4675), (4676, 4775), (4776, 4879),
]
# The stretches of games 4875 to 5060 against the original file, one for each policy it searched them with.
# The cut at 5023 is no change of policy: it is where the run's result against the original file turns over.
AGAINST_ORIGINAL = [(4875, 4983), (4984, 4990), (4991, 4992), (4993, 5023), (5024, 5053), (5054, 5060)]
# The five earlier runs of the original file, which ran on other machines (results/runs.md, "The earlier file").
EARLIER_RUNS = [(1, 2175), (2176, 3440), (3441, 3914), (3915, 4547), (4548, 4874)]
# The stretches of the run's hours: the six runs of the original file's history, the last split at 4983.
WHERE_THE_HOURS_WENT = [(1, 2175), (2176, 3440), (3441, 3914), (3915, 4547), (4548, 4874), (4875, 4983), (4984, 5060)]
# A game that took this many hours more in one file than in the other is listed as lost (or won).
LOST_HOURS = 0.1
# A game that took fewer hours than this in both files is left out of the counts of the games the run won and lost.
SMALL_HOURS = 0.01


def read_lines(path):
    """The last completed line of each game in a JSON-lines file, and the number of lines read."""
    last, count = {}, 0
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as lines:
        for text in lines:
            if text.strip():
                line = json.loads(text)
                count += 1
                if line.get("completed"):
                    last[line["n"]] = line
    return last, count


def nov1_hours(line):
    return line["seconds"]["active_all_runs"] / 3600


def rerun_hours(line):
    return line["seconds"]["own"] / 3600


def original_hours(line):
    seconds = line["seconds"]
    return seconds.get("own", seconds["search_all_runs"]) / 3600


def millions(line):
    return line["nodes"] / 1e6


def original_policy(line):
    """The gate policy of a search of the original file, from the lab's key and the options of its line."""
    lab = line.get("lab") or {}
    policy = lab.get("policy") or {}
    trial = (line.get("engine") or {}).get("gate_trial") or {}
    if trial.get("applied"):
        return f"{policy.get('gate') or 1200}, then {trial['chosen']}"
    if lab.get("conflict_branching") == "off":
        return "300, then off"
    if lab.get("conflict_branching") == "on" and lab.get("gate"):
        if policy.get("conflict_branching") == "off":
            return f"off, then {lab['gate']}"
        return f"{policy.get('gate') or 300}, then {lab['gate']}"
    return str(policy.get("gate") or 300)


def rerun_gate_path(line):
    """The gate the re-run's search used: 1200 until its trial (at 50 million steps or more), then the gate it kept."""
    trial = (line.get("engine") or {}).get("gate_trial")
    if trial is None:
        return "1200 throughout" if line["nodes"] else "no search"
    steps = f"{trial['at_nodes'] / 1e6:.0f}M"
    return f"1200, kept at {steps}" if trial["chosen"] == 1200 else f"{trial['chosen']} from {steps}"


def finder_start(line):
    """The incumbent the finder began from and the best it ended with, and the seconds it took to find the best."""
    finder = (line.get("engine") or {}).get("finder") or {}
    return finder.get("from"), finder.get("best"), finder.get("found_seconds", 0)


def total(lines, games, hours):
    """The hours and the millions of nodes of the lines of GAMES."""
    return sum(hours(lines[n]) for n in games), sum(millions(lines[n]) for n in games)


def stamp(text):
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")


def ratio(a, b):
    return f"{a / b:5.2f}" if b else "    -"


def count_by(lines, key):
    counts = {}
    for line in lines:
        counts[line[key]] = counts.get(line[key], 0) + 1
    return counts


def the_run(nov1, nov1_count):
    print("THE RUN")
    assert sorted(nov1) == list(range(1, LAST + 1)) and nov1_count == LAST, "one completed line a game, 1 to 5060"
    lines = [nov1[n] for n in sorted(nov1)]
    builds = sorted({line["build"]["commit"][:7] + (" dirty" if line["build"]["dirty"] else "") for line in lines})
    threads = sorted({line["threads"] for line in lines})
    invocations = sorted({line["invocations"] for line in lines})
    print(f"lines {len(lines)}, builds {builds}, threads {threads}, invocations {invocations}")
    started = min(stamp(line["started"]) for line in lines)
    ended = max(stamp(line["finished"]) for line in lines)
    wall = (ended - started).total_seconds()
    print(f"first game started {started}Z, last finished {ended}Z: {wall:.0f} s = {wall / 3600:.2f} h")
    hours = {key: sum(line["seconds"][key] for line in lines) / 3600
             for key in ("active_all_runs", "waiting_all_runs", "cpu_all_runs")}
    print(f"active {hours['active_all_runs']:.2f} h, waiting {hours['waiting_all_runs']:.2f} h, "
          f"CPU {hours['cpu_all_runs']:.0f} h ({hours['cpu_all_runs'] / (wall / 3600):.1f} threads busy on average)")
    proofs = dict(sorted(count_by(lines, "proof").items()))
    print(f"searched games (nodes > 0) {sum(1 for line in lines if line['nodes'])}, "
          f"nodes {sum(line['nodes'] for line in lines) / 1e9:.2f} G, proofs {proofs}")
    print()
    print("Where the hours went (active hours and their share, CPU hours, nodes in millions, searched games)")
    for first, last in WHERE_THE_HOURS_WENT + [(1, 4874), (4875, LAST)]:
        ns = range(first, last + 1)
        active = sum(nov1_hours(nov1[n]) for n in ns)
        cpu = sum(nov1[n]["seconds"]["cpu_all_runs"] for n in ns) / 3600
        print(f"{first:>5}-{last:<5} {active:8.2f} h {active / hours['active_all_runs']:6.1%} {cpu:9.0f} cpu h "
              f"{sum(millions(nov1[n]) for n in ns):9.0f} M {sum(1 for n in ns if nov1[n]['nodes']):4d}")
    print()


def the_log(path):
    if not path:
        return
    with open(path) as log:
        for text in log:
            found = re.search(r"exited with status (\d+) after (\d+)s", text)
            if found:
                seconds = int(found.group(2))
                print(f"chain.log: the solver exited with status {found.group(1)} after {seconds} s = "
                      f"{seconds / 3600:.2f} h")
    print()


def head_time(nov1):
    """The head time of each game in hours: the time from the finish of the game before it to its own finish (from the
    run's start for game 1).  The games finish in order, so these add up to the run's wall time."""
    before = min(stamp(line["started"]) for line in nov1.values())
    head = {}
    for n in sorted(nov1):
        finished = stamp(nov1[n]["finished"])
        head[n] = (finished - before).total_seconds() / 3600
        before = finished
    return head


def head_against_active(nov1):
    print("HEAD TIME AGAINST ACTIVE TIME of the run, in hours.  The head time of a game is the time from the finish of")
    print("the game before it to its own finish, which is what the re-run's `own` counts when the head searches.")
    head = head_time(nov1)
    print(f"{'games':<11} {'head':>8} {'active':>8} {'active/head':>12}")
    for first, last in AGAINST_RERUN + [(4880, 4983), (4984, 5060), (1, LAST)]:
        ns = range(first, last + 1)
        h = sum(head[n] for n in ns)
        a = sum(nov1_hours(nov1[n]) for n in ns)
        print(f"{first:>5}-{last:<5} {h:8.2f} {a:8.2f} {a / h:12.3f}")
    print()


def against_rerun(nov1, rerun):
    print("THE RUN AGAINST THE RE-RUN (build 3ca11bf, gate 1200 with the trial; hours: active / own; same machine)")
    print(f"{'games':<11} {'run h':>7} {'run M':>7} {'re-run h':>9} {'re-run M':>9} {'hours':>6} {'nodes':>6}  "
          "searched")
    for first, last in AGAINST_RERUN + [(1, 4879)]:
        ns = range(first, last + 1)
        a_hours, a_nodes = total(nov1, ns, nov1_hours)
        b_hours, b_nodes = total(rerun, ns, rerun_hours)
        searched = sum(1 for n in ns if nov1[n]["nodes"])
        print(f"{first:>5}-{last:<5} {a_hours:7.2f} {a_nodes:7.0f} {b_hours:9.2f} {b_nodes:9.0f} "
              f"{ratio(a_hours, b_hours):>6} {ratio(a_nodes, b_nodes):>6}  {searched}")
    print()


def against_earlier_runs(nov1, original):
    print("THE RUN AGAINST THE FIVE EARLIER RUNS OF THE ORIGINAL FILE, in nodes (millions) of the games each searched")
    print("itself (method search); they ran on other machines and builds, without conflict branching, so hours are not")
    print("compared.  The games it took from the bounds store (method known) cost it no search:")
    print(f"{'games':<11} {'searched':>9} {'orig M':>8} {'run M':>7} {'nodes':>6}   {'known':>6} {'run M':>7} "
          f"{'run h':>6}")
    for first, last in EARLIER_RUNS:
        ns = range(first, last + 1)
        searched = [n for n in ns if original[n]["method"] == "search"]
        known = [n for n in ns if original[n]["method"] == "known"]
        a_nodes = sum(millions(original[n]) for n in searched)
        b_nodes = sum(millions(nov1[n]) for n in searched)
        k_hours, k_nodes = total(nov1, known, nov1_hours)
        print(f"{first:>5}-{last:<5} {len(searched):9d} {a_nodes:8.0f} {b_nodes:7.0f} {ratio(b_nodes, a_nodes):>6}   "
              f"{len(known):6d} {k_nodes:7.0f} {k_hours:6.2f}")
    known = [n for n in range(1, LAST + 1) if original[n]["method"] == "known"]
    k_hours, k_nodes = total(nov1, known, nov1_hours)
    print(f"all {len(known)} games taken from the store: {k_nodes:.0f} M nodes and {k_hours:.2f} h in the run")
    print()


def against_original(nov1, original):
    print("THE RUN AGAINST THE ORIGINAL FILE, games 4875 to 5060, its sixth run, on this machine")
    print("(hours: active / own, else search_all_runs; policy: the gate and what changed it)")
    print(f"{'games':<11} {'policy':<16} {'run h':>7} {'run M':>7} {'orig h':>8} {'orig M':>8} "
          f"{'hours':>6} {'nodes':>6}")
    for first, last in AGAINST_ORIGINAL + [(4984, 5060), (4875, 5060)]:
        ns = range(first, last + 1)
        labels = sorted({original_policy(original[n]) for n in ns if original[n]["nodes"]})
        label = labels[0] if len(labels) == 1 else "all"
        assert len(labels) == 1 or (first, last) in [(4875, 5060), (4984, 5060), (5054, 5060)], labels
        a_hours, a_nodes = total(nov1, ns, nov1_hours)
        b_hours, b_nodes = total(original, ns, original_hours)
        print(f"{first:>5}-{last:<5} {label:<16} {a_hours:7.2f} {a_nodes:7.0f} {b_hours:8.2f} {b_nodes:8.0f} "
              f"{ratio(a_hours, b_hours):>6} {ratio(a_nodes, b_nodes):>6}")
    print("The tactics of the two files are the same from 4984 on.  Before it the original lacked carried_nogoods and")
    print("warm_start (to 4983), price_reuse (to 4959) and near_repeat (to 4913), and lacked conflict_look to 4913 and")
    print("had it off in some games to 4947.")
    ns = range(4875, LAST + 1)
    own = [n for n in ns if "own" in original[n]["seconds"]]
    other = [n for n in ns if "own" not in original[n]["seconds"]]
    by_search = sum(original[n]["seconds"]["search_all_runs"] for n in ns) / 3600
    print(f"The original's hours of 4875-5060 by `own` for {len(own)} games ({own[0]}-{own[-1]}) and `search_all_runs` "
          f"for {len(other)} ({other[0]}-{other[-1]}): {total(original, ns, original_hours)[0]:.2f} h;")
    print(f"by `search_all_runs` for all of them: {by_search:.2f} h;  by `search` of the last invocation: "
          f"{sum(original[n]['seconds']['search'] for n in ns) / 3600:.2f} h")
    for first, last in [(4984, 5022), (5024, 5060)]:
        both = [n for n in range(first, last + 1) if original[n]["nodes"] and nov1[n]["nodes"]]
        ratios = [nov1[n]["nodes"] / original[n]["nodes"] for n in both]
        in_all = sum(nov1[n]["nodes"] for n in both) / sum(original[n]["nodes"] for n in both)
        a_hours, _ = total(nov1, range(first, last + 1), nov1_hours)
        b_hours, _ = total(original, range(first, last + 1), original_hours)
        print(f"games {first}-{last}: {len(both)} searched by both, the run's nodes over the original's "
              f"{min(ratios):.2f} to {max(ratios):.2f}, {in_all:.2f} in all; hours {a_hours:.2f} against "
              f"{b_hours:.2f}, {ratio(a_hours, b_hours).strip()}; builds of the original "
              f"{sorted({original[n]['build']['commit'][:7] for n in both})}")
    tenth = [n for n in ns if original[n]["nodes"] and nov1[n]["nodes"] < original[n]["nodes"] / 10]
    print("games whose nodes in the run are under a tenth of the original's: "
          + ", ".join(f"{n} ({nov1[n]['nodes']} against {original[n]['nodes']})" for n in tenth))
    print()


def dearest(nov1, rerun, original, count=12):
    print(f"THE {count} DEAREST GAMES OF THE RUN (active hours; CPU hours; nodes in millions)")
    print(f"{'game':<5} {'run h':>6} {'cpu h':>7} {'run M':>7} {'share':>6} {'cum.':>6}  "
          "other run: policy, hours, M nodes")
    everything = sum(nov1_hours(line) for line in nov1.values())
    cumulative = 0
    for n in sorted(nov1, key=lambda n: -nov1_hours(nov1[n]))[:count]:
        line = nov1[n]
        other = ""
        if n >= 4875:
            other = f"original ({original_policy(original[n])}): {original_hours(original[n]):.2f} h, " \
                    f"{millions(original[n]):.0f} M"
        if n in rerun:
            other = f"re-run ({rerun_gate_path(rerun[n])}): {rerun_hours(rerun[n]):.2f} h, {millions(rerun[n]):.0f} M"
        cumulative += nov1_hours(line)
        print(f"{n:<5} {nov1_hours(line):6.2f} {line['seconds']['cpu_all_runs'] / 3600:7.0f} {millions(line):7.0f} "
              f"{nov1_hours(line) / everything:6.1%} {cumulative / everything:6.1%}  {other}")
    print()


def lost_to_the_rerun(nov1, rerun):
    games = range(1, 4880)
    print(f"GAMES 1-4879 WHERE THE RUN TOOK {LOST_HOURS} H OR MORE LONGER THAN THE RE-RUN")
    print(f"{'game':<5} {'run h':>6} {'run M':>6} {'re-run h':>9} {'re-run M':>9} {'hours':>6} {'nodes':>6}  "
          "re-run's gate")
    lost = [n for n in games if nov1_hours(nov1[n]) - rerun_hours(rerun[n]) >= LOST_HOURS]
    for n in lost:
        a, b = nov1[n], rerun[n]
        print(f"{n:<5} {nov1_hours(a):6.2f} {millions(a):6.0f} {rerun_hours(b):9.2f} {millions(b):9.0f} "
              f"{ratio(nov1_hours(a), rerun_hours(b)):>6} {ratio(millions(a), millions(b)):>6}  {rerun_gate_path(b)}")
    excess = sum(nov1_hours(nov1[n]) - rerun_hours(rerun[n]) for n in lost)
    same = sum(1 for n in lost if finder_start(nov1[n])[:2] == finder_start(rerun[n])[:2])
    print(f"{len(lost)} games, {excess:.2f} h longer in all; the finder began at the same incumbent and ended at the "
          f"same best in {same} of them")
    print()
    big = [n for n in games if max(nov1_hours(nov1[n]), rerun_hours(rerun[n])) >= SMALL_HOURS]
    longer = [n for n in big if nov1_hours(nov1[n]) > rerun_hours(rerun[n])]
    gain = sum(rerun_hours(rerun[n]) - nov1_hours(nov1[n]) for n in big if n not in longer)
    loss = sum(nov1_hours(nov1[n]) - rerun_hours(rerun[n]) for n in longer)
    best = sum(min(nov1_hours(nov1[n]), rerun_hours(rerun[n])) for n in games)
    print(f"Of the {len(big)} games of 1-4879 that took {SMALL_HOURS} h or more in either file, the run took longer on "
          f"{len(longer)}, {loss:.2f} h longer in all,")
    print(f"and less time on {len(big) - len(longer)}, {gain:.2f} h less in all.  Taking the faster of the two files "
          f"in each game would give {best:.2f} h against the run's {sum(nov1_hours(nov1[n]) for n in games):.2f} h")
    print("(a bound that no policy reaches: the choice is made after the fact, and the files differ by chance too).")
    print()
    print(f"THE RUN AGAINST THE RE-RUN BY THE GATE THE RE-RUN'S TRIAL KEPT (games that took {SMALL_HOURS} h or more in")
    print("either file; 'none': no trial ran, since the search ended before 50 million steps)")
    print(f"{'kept':<8} {'games':>6} {'run h':>7} {'re-run h':>9} {'hours':>6} {'run M':>7} {'re-run M':>9} "
          f"{'nodes':>6} {'run longer':>11}")
    groups = {}
    for n in big:
        trial = (rerun[n].get("engine") or {}).get("gate_trial")
        groups.setdefault(str(trial["chosen"]) if trial else "none", []).append(n)
    rows = [(key, groups[key]) for key in ("none", "600", "800", "1000", "1200") if key in groups]
    rows.append(("800-1200", groups.get("800", []) + groups.get("1000", []) + groups.get("1200", [])))
    for key, ns in rows:
        a_hours, a_nodes = total(nov1, ns, nov1_hours)
        b_hours, b_nodes = total(rerun, ns, rerun_hours)
        slower = sum(1 for n in ns if nov1_hours(nov1[n]) > rerun_hours(rerun[n]))
        print(f"{key:<8} {len(ns):6d} {a_hours:7.2f} {b_hours:9.2f} {ratio(a_hours, b_hours):>6} {a_nodes:7.0f} "
              f"{b_nodes:9.0f} {ratio(a_nodes, b_nodes):>6} {slower:11d}")
    print()


def lost_to_the_original(nov1, original):
    games = range(4875, LAST + 1)
    print(f"GAMES 4875-5060 WHERE THE RUN TOOK {LOST_HOURS} H OR MORE LONGER THAN THE ORIGINAL FILE")
    print(f"{'game':<5} {'run h':>6} {'run M':>6} {'orig h':>7} {'orig M':>7} {'hours':>6} {'nodes':>6}  "
          "original's gate; finder (from, best, seconds to the best), run | original; invocations, run | original")
    lost = [n for n in games if nov1_hours(nov1[n]) - original_hours(original[n]) >= LOST_HOURS]
    for n in lost:
        a, b = nov1[n], original[n]
        finders = [", ".join(f"{value:.0f}" for value in finder_start(line)) for line in (a, b)]
        print(f"{n:<5} {nov1_hours(a):6.2f} {millions(a):6.0f} {original_hours(b):7.2f} {millions(b):7.0f} "
              f"{ratio(nov1_hours(a), original_hours(b)):>6} {ratio(millions(a), millions(b)):>6}  "
              f"{original_policy(b)}; {finders[0]} | {finders[1]}; {a['invocations']} | {b['invocations']}")
    excess = sum(nov1_hours(nov1[n]) - original_hours(original[n]) for n in lost)
    every = sum(max(0, nov1_hours(nov1[n]) - original_hours(original[n])) for n in games)
    print(f"{len(lost)} games: {lost}, {excess:.2f} h longer in all ({every:.2f} h over every game that took longer)")
    won = [n for n in games if original_hours(original[n]) - nov1_hours(nov1[n]) >= LOST_HOURS]
    saved = sum(original_hours(original[n]) - nov1_hours(nov1[n]) for n in won)
    print(f"and it took {LOST_HOURS} h or more less on {len(won)} games, {saved:.2f} h less in all, among them:")
    for n in [4983, 4984, 5049, 5052, 5054, 5056, 5060]:
        print(f"  {n:<5} {nov1_hours(nov1[n]):6.2f} h {millions(nov1[n]):6.0f} M | "
              f"{original_hours(original[n]):6.2f} h {millions(original[n]):6.0f} M  original's gate "
              f"{original_policy(original[n])}")
    print()


def left_open(nov1, original):
    print("THE GAMES THE GATE STUDY LEFT OPEN (4983 and 4984 whole at a gate of 300)")
    for n in (4983, 4984):
        a, b = nov1[n], original[n]
        cpu = a["seconds"]["cpu_all_runs"] / 3600
        print(f"{n}: run {nov1_hours(a):.2f} h, {millions(a):.0f} M nodes, CPU {cpu:.0f} h, build "
              f"{a['build']['commit'][:7]}, started {a['started']}, finished {a['finished']}")
        print(f"      original: {original_hours(b):.2f} h by own, {millions(b):.0f} M nodes, build "
              f"{b['build']['commit'][:7]}, invocations {b['invocations']}, policy {original_policy(b)}, "
              f"tactics {b['tactics']}; the search of its last invocation took {b['seconds']['search'] / 3600:.2f} h")
        per_node = (nov1_hours(a) / millions(a)) / (original_hours(b) / millions(b))
        print(f"      ratio of the run to the original: hours {ratio(nov1_hours(a), original_hours(b)).strip()}, "
              f"nodes {ratio(millions(a), millions(b)).strip()}, hours a node {per_node:.2f}; "
              f"hours a billion nodes {1000 * nov1_hours(a) / millions(a):.2f} and "
              f"{1000 * original_hours(b) / millions(b):.2f}")
    print()


def scores(nov1, rerun, original):
    differ_original = [n for n in nov1 if nov1[n]["score"] != original[n]["score"]]
    differ_rerun = [n for n in rerun if nov1[n]["score"] != rerun[n]["score"]]
    print(f"SCORES: the run and the original file differ in {len(differ_original)} games, the run and the re-run in "
          f"{len(differ_rerun)} of {len(rerun)}")


def main():
    nov1, nov1_count = read_lines(os.environ["NOV1_RESULTS"])
    rerun, _ = read_lines(os.environ["RERUN_RESULTS"])
    original, _ = read_lines(os.environ["ORIGINAL_RESULTS"])
    assert sorted(rerun) == list(range(1, 4880)), "the re-run's complete games are 1 to 4879"
    assert sorted(original) == list(range(1, LAST + 1)), "the original file has games 1 to 5060"
    the_run(nov1, nov1_count)
    the_log(os.environ.get("NOV1_LOG"))
    head_against_active(nov1)
    against_rerun(nov1, rerun)
    against_earlier_runs(nov1, original)
    against_original(nov1, original)
    dearest(nov1, rerun, original)
    lost_to_the_rerun(nov1, rerun)
    lost_to_the_original(nov1, original)
    left_open(nov1, original)
    scores(nov1, rerun, original)


if __name__ == "__main__":
    main()
