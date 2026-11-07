#!/usr/bin/env python3
"""Race R1 of the unsound mode: checks the lines of the six arms and prints the entry's numbers.

    nice -n 19 python3 -I analyze.py [RESULTS [E3B_DIR]] > out.txt

RESULTS (default: results/optimal.jsonl.gz of the main repository, three levels above this notebook's `search/`
folder when the notebook is checked out at solver/notebook/) is the built-in table's source, read with gzip.  E3B_DIR
(default: the sibling entry `tilted-back-and-wider-rounds-2026-11`) holds the lines of E3b's arms A, K (63 games) and
TKW (which is `--tilt 100` here); the folder of this script holds R1's lines (k0-5.jsonl: arm K on the other 188
games; k25w4-0-5.jsonl, k50w4-0-5.jsonl and k50-0-5.jsonl) and their logs, and games-all.txt.  The script changes
nothing, except that it writes the chart, share.svg, beside itself; everything it prints is a number of the entry.
Functions that E3b's analyze.py already has (a line's record, the checks of its consistency, the sign test, the cost
and time models) are used from there.
"""

import glob
import gzip
import importlib.util
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta

E3B_ENTRY = "tilted-back-and-wider-rounds-2026-11"
ARMS = ("A", "K", "K100W4", "K25W4", "K50W4", "K50")
OPTIONS = {  # the options of each arm as its lines record them: tilt percent, back, widen
    "A": (0, 0, None), "K": (0, 8, None), "K100W4": (100, 8, 4), "K25W4": (25, 8, 4), "K50W4": (50, 8, 4),
    "K50": (50, 8, None),
}
FLAGS = {
    "A": "none", "K": "--back 8", "K100W4": "--back 8 --tilt 100 --widen 4", "K25W4": "--back 8 --tilt 25 --widen 4",
    "K50W4": "--back 8 --tilt 50 --widen 4", "K50": "--back 8 --tilt 50",
}
OLD_COMMIT, NEW_COMMIT = "cd3c3ac", "8dc6500"  # E3b's build (and K's 188 games), and the build of --tilt P
EFFORT, SEED, THREADS, FIX = 7, 1, 4, [0.7, 0.9]
ROUND_WORK = 65_536
LEVELS = [(0, 0)] + [(e, ROUND_WORK * 2 ** (e - 1)) for e in range(1, EFFORT + 1)]  # (effort, budget in work)
BUDGET = LEVELS[-1][1]
WORK_BUDGETS = (10_000, 30_000, 100_000, 300_000, 1_000_000, 4_000_000)  # E3b's
SIGN_LEVELS = (1, 3, 5, 7)
STRETCHES = ((3441, 4000), (4001, 4560), (4561, 5060))
SEARCHED, SEARCHED_WITH_START_OPTIMAL = 568, 317  # P1's counts: games of 3441-5060 of method search, start optimal
MIN_ROUND_TIME = 3.0  # a line's cost is measured when its rounds took this many seconds at least
# the chart: the colors are slots of the validated categorical palette (blue, orange, violet, magenta: adjacent pairs
# pass the validator, in this order); the default is the ink and the arm with no tilt a neutral gray
COLOR = {"A": "#1f2328", "K": "#7d8590", "K100W4": "#6250d6", "K25W4": "#2a78d6", "K50W4": "#eb6834",
         "K50": "#e87ba4"}
DASH = {"A": "", "K": "7 4", "K100W4": "3 3", "K25W4": "", "K50W4": "", "K50": "9 4 2 4"}
MARKER = {"A": "circle", "K": "square", "K100W4": "down", "K25W4": "up", "K50W4": "diamond", "K50": "ring"}
X_MIN, X_MAX = 3_000, 4_800_000


def load_module(path):
    """A module of another entry, by its path (E3b's analyze.py)."""
    sys.dont_write_bytecode = True  # leave no __pycache__ in the other entry's folder
    spec = importlib.util.spec_from_file_location("e3b_analyze", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tilt_percent(value):
    """The tilt of a line as a percent: E3b's build wrote true or false, the build of --tilt P writes the percent."""
    return 100 if value is True else 0 if value is False else value


def p_text(p):
    """A p-value of the sign test as the entry prints it."""
    return "-" if p is None else "<0.001" if p < 0.001 else f"{p:.3f}"


def spans(here, e3b):
    """The files of each arm: [(path, build commit its lines should record)]."""
    def own(pattern, commit):
        return [(p, commit) for p in sorted(glob.glob(os.path.join(here, pattern)))]

    def old(pattern):
        return [(p, OLD_COMMIT) for p in sorted(glob.glob(os.path.join(e3b, pattern)))]

    return {
        "A": old("arm-a.jsonl") + old("part2-a.jsonl") + old("part2-a-tail*.jsonl"),
        "K": old("arm-k.jsonl") + own("k[0-5].jsonl", OLD_COMMIT),
        "K100W4": old("arm-tkw.jsonl") + old("part2-tkw.jsonl"),
        "K25W4": own("k25w4-[0-5].jsonl", NEW_COMMIT),
        "K50W4": own("k50w4-[0-5].jsonl", NEW_COMMIT),
        "K50": own("k50-[0-5].jsonl", NEW_COMMIT),
    }


def read_arm(files):
    """The lines of an arm by n, each with its file and the commit it should record; and the games found twice."""
    lines, twice = {}, []
    for path, commit in files:
        with open(path) as f:
            for text in f:
                if text.strip():
                    line = json.loads(text)
                    if line["n"] in lines:
                        twice.append(line["n"])
                    lines[line["n"]] = (line, path, commit)
    return lines, twice


def read_table(path, games):
    """The built-in table's scores of the games, from the committed results file."""
    table = {}
    with gzip.open(path, "rt") as f:
        for text in f:
            if '"n":' in text[:40]:
                line = json.loads(text)
                if line["n"] in games:
                    table[line["n"]] = line["score"]
    return table


# ---------------------------------------------------------------------------------------------------------------------
# The runs and the checks of the lines


def runs(here):
    """Section 0: when each of R1's runs played, from its log; the most games at once."""
    print("== 0. The runs, from the logs (a game starts at the log's time and ends that many seconds later) ==")
    intervals = {}
    for name in sorted(os.listdir(here)):
        if not name.endswith(".log"):
            continue
        starts, ends, hours, games, problems = [], [], 0.0, 0, 0
        with open(os.path.join(here, name)) as f:
            for text in f:
                if text.startswith("# 20"):
                    starts.append(datetime.strptime(text[2:21], "%Y-%m-%d %H:%M:%S"))
                elif text.startswith("# game") and " exit " in text:
                    took = float(text.split(" after ")[1].split(" s")[0])
                    ends.append(starts[-1] + timedelta(seconds=took))
                    if " exit 0 " in text:
                        hours += took / 3600
                        games += 1
                    else:
                        problems += 1
                elif text.startswith("# done"):
                    done = text.strip()
        # a log's time has a resolution of a second: a game ends no later than the next one of its log starts
        intervals[name] = [(a, min(b, starts[i + 1]) if i + 1 < len(starts) else b)
                           for i, (a, b) in enumerate(zip(starts, ends))]
        print(f"  {name}: {starts[0]:%Y-%m-%d %H:%M:%S} to {max(ends):%H:%M:%S}, {games} games, {hours:.2f} h of "
              f"{THREADS} threads, games with a nonzero exit {problems}; {done}")
    for label, prefix in (("K's six runs", ("k0", "k1", "k2", "k3", "k4", "k5")), ("K25W4, K50W4 and K50", None)):
        names = [n for n in intervals if (n[:-4] in prefix if prefix else n.startswith(("k25", "k50")))]
        events = sorted([(a, 1) for n in names for a, _ in intervals[n]]
                        + [(b, -1) for n in names for _, b in intervals[n]], key=lambda x: (x[0], x[1]))
        live = peak = 0
        for _, step in events:
            live += step
            peak = max(peak, live)
        first = min(s for n in names for s, _ in intervals[n])
        last = max(e for n in names for _, e in intervals[n])
        print(f"  {label}: {first:%H:%M:%S} to {last:%H:%M:%S}, at most {peak} games at once "
              f"({peak * THREADS} threads)")


def check_lines(arms_lines, table, games, e3b):
    """Section A: the checks of the lines.  Returns the number of failures."""
    print("== A. Checks of the lines ==")
    failures = 0

    def fail(text):
        nonlocal failures
        failures += 1
        print("  FAIL:", text)

    for arm in ARMS:
        tilt, back, widen = OPTIONS[arm]
        lines = arms_lines[arm]
        missing = [n for n in games if n not in lines]
        extra = sorted(set(lines) - set(games))
        methods, builds, bad = {}, {}, []
        for n, (line, name, commit) in lines.items():
            methods[line["method"]] = methods.get(line["method"], 0) + 1
            builds[(line["build"]["commit"][:7], line["build"]["dirty"])] = builds.get(
                (line["build"]["commit"][:7], line["build"]["dirty"]), 0) + 1
            if line["build"]["commit"][:7] != commit or line["build"]["dirty"]:
                bad.append((n, "build", line["build"]))
            for key, want in (("effort", EFFORT), ("budget", BUDGET), ("fix", FIX), ("seed", SEED),
                              ("threads", THREADS), ("from_known", True), ("back", back), ("widen", widen)):
                if line[key] != want:
                    bad.append((n, key, line[key]))
            if tilt_percent(line["tilt"]) != tilt:
                bad.append((n, "tilt", line["tilt"]))
            if line["prev"]["source"] != "table":
                bad.append((n, "prev.source", line["prev"]["source"]))
            if n in table and (line["score"] > table[n] or line["stop_at_known"]["known"] != table[n]):
                bad.append((n, "score above the table's, or the known score is not the table's", line["score"]))
            bad += e3b.check_one(line, tilt, back, widen)
        print(f"  arm {arm} ({FLAGS[arm]}): {len(lines)} lines; missing {missing}; extra {extra}; methods {methods}; "
              f"builds {builds}; deviations {bad}")
        if missing or extra or set(methods) != {"search"} or bad:
            fail(f"arm {arm}")
    differ = []
    for n in games:
        keys = {(lines[n][0]["start"], lines[n][0]["in_the_bag"], lines[n][0]["stop_at_known"]["known"],
                 json.dumps(lines[n][0]["setup"], sort_keys=True), json.dumps(lines[n][0]["prev"], sort_keys=True))
                for lines in arms_lines.values() if n in lines}
        if len(keys) > 1:
            differ.append(n)
    print(f"  start, in_the_bag, the known score, setup and prev differ between arms in {len(differ)} games: "
          f"{differ} (want none)")
    if differ:
        fail("the arms differ in a game's start")
    print(f"  the table (results/optimal.jsonl.gz) has {len(table)} of the {len(games)} games")
    if len(table) != len(games):
        fail("table")
    return failures


def check_files(here, arms_files, twice):
    """The files against their logs: the lines of each R1 file are the games of its log, every command exited 0 and
    every run says it is done.  Also the games found in two files of an arm."""
    failures = 0
    for arm, files in arms_files.items():
        if twice[arm]:
            print(f"  FAIL: arm {arm}: games in two lines: {twice[arm]}")
            failures += 1
    for arm, files in arms_files.items():
        for path, commit in files:
            if os.path.dirname(path) != here.rstrip("/"):
                continue  # E3b's files were checked in its entry
            log = path[:-len(".jsonl")] + ".log"
            with open(path) as f:
                count = sum(1 for text in f if text.strip())
            with open(log) as f:
                text = f.read()
            ok = text.count(" exit 0 after ") == count and text.count(" exit ") == count and \
                text.rstrip().endswith("# done: stopping=False, failures=[]")
            if not ok:
                print(f"  FAIL: {os.path.basename(path)}: {count} lines, the log does not agree")
                failures += 1
    print(f"  files against their logs: {failures} disagreements (want none)")
    return failures


# ---------------------------------------------------------------------------------------------------------------------
# The shares


def count_within(recs, games, limit, e3b):
    return sum(1 for n in games if e3b.reached(recs[n], limit))


def levels_table(recs, games, e3b, title):
    """The games at the known score within each level's budget of work, one row an arm."""
    print(f"\n  {title} ({len(games)} games): games at the known score within the budget of each effort level "
          "(a lower bound by up to one round's work)")
    print(f"  {'arm':>7} | " + " | ".join(f"{'E' + str(e):>11}" for e, _ in LEVELS))
    for arm in ARMS:
        counts = [count_within(recs[arm], games, b, e3b) for _, b in LEVELS]
        print(f"  {arm:>7} | " + " | ".join(f"{c:>4} {100 * c / len(games):5.1f}" for c in counts))


def annotate(recs, arms_lines, e3b, e3b_dir):
    """Marks the lines of E3b's runs that began after its prover ended, as E3b does: their seconds are not those of the
    loaded machine of the others, and the cost leaves them out.  R1's lines were all run beside other work, and stay."""
    starts = e3b.game_starts(e3b_dir)
    names = {"A": "A", "K": "K", "K100W4": "TKW"}  # the arm's name in E3b's logs
    with open(os.path.join(e3b_dir, "games.txt")) as f:
        part1 = {int(text) for text in f if text.strip()}
    marked = {}
    for arm, name in names.items():
        for n, (line, file, _) in arms_lines[arm].items():
            if file.startswith(e3b_dir):
                key = ("part1" if n in part1 else "part2", name, n)
                recs[arm][n]["unloaded"] = starts[key] >= e3b.PROVER_ENDED
                marked[arm] = marked.get(arm, 0) + recs[arm][n]["unloaded"]
    print(f"  lines of E3b's runs that began after its prover ended, left out of the cost: {marked}")


def in_run(rec, budget):
    """Whether a run at a level, whose rounds go on until their work reaches `budget`, holds the known score: the
    line gives the work at the end of the reaching round, and the run takes that round if the work before it was
    below the budget.  The work before it is estimated, by spreading the work since the last earlier improvement over
    the rounds in between: an estimate, which `reached` bounds from below (the lines hold no work by round)."""
    if rec["reach"] is None:
        return False
    if rec["work"] == 0 or rec["reach"] == 0:
        return True
    improvements = rec["improvements"]
    earlier_round, earlier_work = (improvements[-2]["round"], improvements[-2]["work"]) if len(improvements) > 1 \
        else (0, 0)
    before = rec["work"] - (rec["work"] - earlier_work) / (rec["reach"] - earlier_round)
    return before < budget


def shares(recs, games, e3b):
    """Section 1 to 4: the shares by level, by work, the misses, the work summed, the stretches."""
    total = len(games)
    print("\n== 1. The share at the known score at each level of effort ==")
    print(f"  Effort E is a budget of {ROUND_WORK:,} x 2^(E-1) work (E0: none: a game whose start, or a trajectory's "
          "start, holds the known score).  Counts, then percent of the games.")
    levels_table(recs, games, e3b, "All")
    print("\n  Percent only, for the entry:")
    print(f"  {'arm':>7} | " + " ".join(f"{'E' + str(e):>5}" for e, _ in LEVELS) + " | mean E1-E7")
    shares_by_arm = {}
    for arm in ARMS:
        counts = [count_within(recs[arm], games, b, e3b) for _, b in LEVELS]
        shares_by_arm[arm] = [100 * c / total for c in counts]
        print(f"  {arm:>7} | " + " ".join(f"{s:5.1f}" for s in shares_by_arm[arm])
              + f" | {statistics.mean(shares_by_arm[arm][1:]):5.1f}")
    print("\n  Points below the best arm at the level (regret), and their sum over E1-E7:")
    for arm in ARMS:
        regret = [max(shares_by_arm[a][i] for a in ARMS) - shares_by_arm[arm][i] for i in range(len(LEVELS))]
        print(f"  {arm:>7} | " + " ".join(f"{r:5.1f}" for r in regret) + f" | sum {sum(regret[1:]):5.1f}, largest "
              f"{max(regret[1:]):.1f}")
    print("\n  The count at each level if the run's last round is counted as the level runs it (the work before the "
          "reaching round is estimated; the lower bound above counts the games whose reaching round ended within "
          "the budget): lower bound / estimate")
    print(f"  {'arm':>7} | " + " | ".join(f"{'E' + str(e):>9}" for e, _ in LEVELS[1:]))
    for arm in ARMS:
        cells = [f"{count_within(recs[arm], games, b, e3b)}/{sum(1 for n in games if in_run(recs[arm][n], b))}"
                 for _, b in LEVELS[1:]]
        print(f"  {arm:>7} | " + " | ".join(f"{c:>9}" for c in cells))
    print("\n  The same, the estimate in percent, E1 to E7 and the mean:")
    for arm in ARMS:
        estimate = [100 * sum(1 for n in games if in_run(recs[arm][n], b)) / total for _, b in LEVELS[1:]]
        print(f"  {arm:>7} | " + " ".join(f"{e:5.1f}" for e in estimate) + f" | {statistics.mean(estimate):5.1f}")
    print(f"\n  The estimate for the {SEARCHED} searched games of 3441-5060 (P1's rule: "
          f"({SEARCHED_WITH_START_OPTIMAL} + the hard games reached) / {SEARCHED}; all 251 hard games run):")
    print(f"  {'arm':>7} | " + " ".join(f"{'E' + str(e):>5}" for e, _ in LEVELS))
    for arm in ARMS:
        counts = [count_within(recs[arm], games, b, e3b) for _, b in LEVELS]
        print(f"  {arm:>7} | " + " ".join(f"{100 * (SEARCHED_WITH_START_OPTIMAL + c) / SEARCHED:5.1f}"
                                          for c in counts))

    print("\n== 2. The share within a budget of work (E3b's budgets) ==")
    print(f"  {'arm':>7} | " + " | ".join(f"{w:>10,}" for w in WORK_BUDGETS) + f" | {'at effort 7':>11}")
    for arm in ARMS:
        counts = [count_within(recs[arm], games, w, e3b) for w in WORK_BUDGETS]
        run = sum(1 for n in games if e3b.reached(recs[arm][n]))
        print(f"  {arm:>7} | " + " | ".join(f"{c:>4} {100 * c / total:5.1f}" for c in counts)
              + f" | {run:>4} {100 * run / total:5.1f}")

    print("\n== 3. The games each arm misses (final shortfall in points), and the work summed to the known score "
          f"(a game not reached counts as the budget, {BUDGET:,}) ==")
    for arm in ARMS:
        missed = [n for n in games if not e3b.reached(recs[arm][n])]
        spent = sum(recs[arm][n]["work"] if e3b.reached(recs[arm][n]) else BUDGET for n in games)
        works = [recs[arm][n]["work"] for n in games if e3b.reached(recs[arm][n]) and recs[arm][n]["work"]]
        print(f"  {arm:>7}: misses {len(missed)}: " + ", ".join(f"{n} (-{recs[arm][n]['short']})" for n in missed))
        print(f"  {'':>7}  work summed {spent:,}; median work of the {len(works)} games it reaches after the start "
              f"{statistics.median(works):,.0f}")

    print("\n== 4. The share by stretch of n (percent, and games) ==")
    for low, high in STRETCHES:
        part = [n for n in games if low <= n <= high]
        print(f"  {low}-{high}: {len(part)} games")
        print(f"  {'arm':>7} | " + " ".join(f"{'E' + str(e):>11}" for e, _ in LEVELS))
        for arm in ARMS:
            counts = [count_within(recs[arm], part, b, e3b) for _, b in LEVELS]
            print(f"  {arm:>7} | " + " ".join(f"{100 * c / len(part):5.1f}{c:>4} " for c in counts))


def compare(recs, games, first, second, test, e3b):
    """The games the first arm holds at each level that the second does not, and the reverse, by `test(rec, budget)`:
    [(effort, gained, lost, p)]."""
    cells = []
    for effort, budget in LEVELS[1:]:
        ahead = [test(recs[first][n], budget) for n in games]
        behind = [test(recs[second][n], budget) for n in games]
        gained = [n for n, a, b in zip(games, ahead, behind) if a and not b]
        lost = [n for n, a, b in zip(games, ahead, behind) if b and not a]
        cells.append((effort, gained, lost, e3b.sign_test(len(gained), len(lost))))
    return cells


def pairs(recs, games, e3b):
    """Section 6: game by game, the games one arm reaches and another does not, at each level, with the lower bound
    of the level's share (`reached`) and with the estimate that counts the round that crosses the budget (`in_run`)."""
    print("\n== 6. Game by game: gained / lost (games the first arm holds within the level's budget that the second "
          "does not / the reverse), and the two-sided sign test p ==")
    pairings = (("K25W4", "K"), ("K25W4", "K100W4"), ("K50W4", "K"), ("K50W4", "K100W4"), ("K25W4", "K50W4"),
                ("K50W4", "K50"), ("K25W4", "K50"), ("K100W4", "K50W4"), ("K50", "K"), ("K", "A"), ("K25W4", "A"),
                ("K50W4", "A"))
    listed = (("K25W4", "K50W4"), ("K25W4", "K"), ("K50W4", "K"), ("K25W4", "K100W4"), ("K50W4", "K100W4"),
              ("K50W4", "K50"))
    for first, second in pairings:
        low = compare(recs, games, first, second, e3b.reached, e3b)
        est = compare(recs, games, first, second, in_run, e3b)
        print(f"  {first} against {second}:")
        print("    lower bound  " + " | ".join(f"E{e}: +{len(g)}/-{len(l)} p={p_text(p)}" for e, g, l, p in low))
        print("    with the round that crosses the budget (estimate)  " + " | ".join(
            f"E{e}: +{len(g)}/-{len(l)} p={p_text(p)}" for e, g, l, p in est))
        if (first, second) in listed:
            for effort, gained, lost, p in low:
                if effort in SIGN_LEVELS:
                    print(f"      E{effort}: gained {gained}; lost {lost}; paired s.e. of the difference "
                          f"{100 * math.sqrt(len(gained) + len(lost)) / len(games):.2f} points")


def unreached(recs, games, e3b):
    """Section 7: the games no arm reaches, and the games each arm reaches alone or misses alone."""
    print("\n== 7. The games no arm reaches, and how far short each arm ends (points; start: the start's "
          "shortfall) ==")
    none = [n for n in games if all(not e3b.reached(recs[a][n]) for a in ARMS)]
    print(f"  no arm reaches {len(none)} games: {none}")
    print(f"  {'n':>5} {'start':>6} | " + " | ".join(f"{arm:>7}" for arm in ARMS) + " | best")
    for n in none:
        shorts = [recs[a][n]["short"] for a in ARMS]
        print(f"  {n:>5} {recs['A'][n]['start_short']:>6} | " + " | ".join(f"{s:>7}" for s in shorts)
              + f" | {min(shorts)}")
    tilt_arms = [a for a in ARMS if OPTIONS[a][0]]
    print(f"\n  The games that some arm misses and another reaches (cell: work at which it reached, in thousands, "
          "or -shortfall):")
    some = [n for n in games if any(not e3b.reached(recs[a][n]) for a in ARMS) and n not in none]
    print(f"  {'n':>5} {'start':>6} | " + " | ".join(f"{arm:>8}" for arm in ARMS))
    for n in some:
        cells = []
        for a in ARMS:
            r = recs[a][n]
            cells.append(f"{r['work'] / 1000:.0f}k" if e3b.reached(r) else f"-{r['short']}")
        print(f"  {n:>5} {recs['A'][n]['start_short']:>6} | " + " | ".join(f"{c:>8}" for c in cells))
    print("\n  Games the default reaches at effort 7 that another arm does not, and the reverse:")
    for arm in ARMS[1:]:
        lost = [n for n in games if e3b.reached(recs["A"][n]) and not e3b.reached(recs[arm][n])]
        gained = [n for n in games if e3b.reached(recs[arm][n]) and not e3b.reached(recs["A"][n])]
        print(f"    {arm:>7}: loses {len(lost)} {lost}; gains {len(gained)}")
    for arm in ARMS:
        others = [a for a in ARMS if a != arm]
        only = [n for n in games if e3b.reached(recs[arm][n]) and all(not e3b.reached(recs[a][n]) for a in others)]
        print(f"  reached by {arm} alone: {only}")
        alone_missing = [n for n in games if not e3b.reached(recs[arm][n])
                         and all(e3b.reached(recs[a][n]) for a in others)]
        print(f"  missed by {arm} alone: {alone_missing}")
    print(f"\n  Tilting arms ({tilt_arms}) at effort 7: games missed by each, and the union of what they miss")
    for a in tilt_arms:
        print(f"    {a}: {[n for n in games if not e3b.reached(recs[a][n])]}")
    print(f"    reached by at least one of the four tilting arms: "
          f"{sum(1 for n in games if any(e3b.reached(recs[a][n]) for a in tilt_arms))} of {len(games)}; by one of the "
          f"six: {sum(1 for n in games if any(e3b.reached(recs[a][n]) for a in ARMS))}")


# ---------------------------------------------------------------------------------------------------------------------
# The cost


def cost(recs, games, e3b):
    """Section 5: seconds per 10^6 work and steps per neighborhood, by arm; the rounds a budget buys."""
    print("\n== 5. Cost ==")
    print(f"  Lines whose rounds took at least {MIN_ROUND_TIME:.0f} s (the rounds' wall time on {THREADS} threads, at "
          "nice 19).  Seconds are not exact (the machine was loaded, differently in each run); steps and work are.")
    print(f"  {'arm':>7} {'lines':>5} | {'s per 10^6 work':>24} | {'steps per neighborhood':>24} | "
          f"{'work per round (K)':>20}")

    def span(values, digits):
        return f"{statistics.median(values):.{digits}f} ({min(values):.{digits}f}-{max(values):.{digits}f})"

    for arm in ARMS:
        measured = [recs[arm][n] for n in games if e3b.measurable(recs[arm][n])]
        spw = [1e6 * e3b.used(r)[0] / e3b.used(r)[1] for r in measured]
        spn = [r["steps"] / r["neighborhoods"] for r in measured]
        wpr = [r["work"] / r["rounds"] / 1000 for r in measured]
        print(f"  {arm:>7} {len(measured):>5} | {span(spw, 1):>24} | {span(spn, 0):>24} | {span(wpr, 1):>20}")
    print("\n  By stretch of n, the median seconds per 10^6 work (lines):")
    for low, high in STRETCHES:
        cells = []
        for arm in ARMS:
            vals = [1e6 * e3b.used(recs[arm][n])[0] / e3b.used(recs[arm][n])[1] for n in games
                    if low <= n <= high and e3b.measurable(recs[arm][n])]
            cells.append(f"{arm} {statistics.median(vals):.1f} ({len(vals)})" if vals else f"{arm} -")
        print(f"    {low}-{high}: " + "; ".join(cells))
    print("\n  Steps per neighborhood over all the rounds of the arm's lines (pooled steps / pooled neighborhoods), "
          "and the median of a game's, over the lines with a round:")
    for arm in ARMS:
        own = [recs[arm][n] for n in games if recs[arm][n]["rounds"] >= 1]
        pooled = sum(r["steps"] for r in own) / sum(r["neighborhoods"] for r in own)
        median = statistics.median([r["steps"] / r["neighborhoods"] for r in own])
        print(f"    {arm:>7}: {len(own)} lines with a round; pooled {pooled:.1f}, median {median:.1f}")
    print("\n  Steps per neighborhood against K's, game by game over the games with a round in both (median, "
          "min-max); exact, as steps do not depend on the machine:")
    for arm in ARMS:
        if arm == "K":
            continue
        both = [n for n in games if recs[arm][n]["rounds"] >= 1 and recs["K"][n]["rounds"] >= 1]
        ratios = [(recs[arm][n]["steps"] / recs[arm][n]["neighborhoods"])
                  / (recs["K"][n]["steps"] / recs["K"][n]["neighborhoods"]) for n in both]
        print(f"    {arm:>7}: {len(both)} games; x{span(ratios, 2)}")
    print("\n  Rounds of the games not reached (they used the whole budget of effort 7): number, median, min-max")
    for arm in ARMS:
        missed = [recs[arm][n]["rounds"] for n in games if not e3b.reached(recs[arm][n])]
        print(f"    {arm:>7}: {len(missed)} games; rounds " + (span(missed, 0) if missed else "-"))
    print("\n  The three arms that ran together on the same games (K25W4, K50W4, K50), game by game over the games "
          "measurable in all three: ratios of seconds per work and of steps per neighborhood (median, min-max)")
    trio = ("K25W4", "K50W4", "K50")
    both = [n for n in games if all(e3b.measurable(recs[a][n]) for a in trio)]
    for a, b in (("K50W4", "K25W4"), ("K50", "K50W4"), ("K50", "K25W4")):
        spw = [(e3b.used(recs[a][n])[0] / e3b.used(recs[a][n])[1]) / (e3b.used(recs[b][n])[0] / e3b.used(recs[b][n])[1])
               for n in both]
        spn = [(recs[a][n]["steps"] / recs[a][n]["neighborhoods"]) / (recs[b][n]["steps"] / recs[b][n]["neighborhoods"])
               for n in both]
        print(f"    {a} / {b}: {len(both)} games; seconds per work x{span(spw, 2)}; steps per neighborhood "
              f"x{span(spn, 2)}")
    print("\n  Total seconds of the lines (the games' whole runs, 4 threads) and the seconds in the games missed:")
    for arm in ARMS:
        own = [recs[arm][n] for n in games]
        total = sum(r["seconds"] for r in own)
        missed = [r for r in own if not e3b.reached(r)]
        lost = sum(r["seconds"] for r in missed)
        start = statistics.median([r["start_seconds"] for r in own])
        print(f"    {arm:>7}: {total:.0f} s ({total / 3600:.2f} h) over {len(own)} lines; {lost:.0f} s in the "
              f"{len(missed)} missed; the start takes a median {start:.1f} s")


def times(recs, games, e3b):
    """Section 8: the time of a full run at each level (E3b's model), from each arm's own lines."""
    print("\n== 8. The time of a full run of each level, E3b's model: the start's seconds plus the stretch's median "
          "seconds per work (the arm's own lines) times the budget; median / 90th percentile ==")
    rate = {arm: e3b.rates(recs[arm], games) for arm in ARMS}
    print(f"  {'effort':>6} {'work':>10} | " + " | ".join(f"{arm:>11}" for arm in ARMS))
    for effort, budget in LEVELS[1:]:
        cells = []
        for arm in ARMS:
            t = [e3b.time_full(recs[arm][n], budget, rate[arm]) for n in games]
            cells.append(f"{statistics.median(t):.0f} / {e3b.percentile(t, 0.9):.0f}")
        print(f"  {effort:>6} {budget:>10,} | " + " | ".join(f"{c:>11}" for c in cells))
    print("  rates (seconds per 10^6 work, all stretches): " + ", ".join(
        f"{arm} {rate[arm][(3441, 5060)]:.1f}" for arm in ARMS))


# ---------------------------------------------------------------------------------------------------------------------
# The chart


def marker_svg(kind, x, y, color, size=4.5):
    """A marker at (x, y): a 2px ring of the surface around it, so that markers stay legible where they overlap."""
    ring = 'stroke="#ffffff" stroke-width="2"'
    if kind == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size}" fill="{color}" {ring}/>'
    if kind == "ring":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size}" fill="#ffffff" stroke="{color}" stroke-width="2"/>'
    if kind == "square":
        return (f'<rect x="{x - size:.1f}" y="{y - size:.1f}" width="{2 * size}" height="{2 * size}" fill="{color}" '
                f'{ring}/>')
    points = {"up": [(0, -1.25), (1.1, 0.8), (-1.1, 0.8)], "down": [(0, 1.25), (1.1, -0.8), (-1.1, -0.8)],
              "diamond": [(0, -1.3), (1.3, 0), (0, 1.3), (-1.3, 0)]}[kind]
    path = " ".join(f"{x + dx * size:.1f},{y + dy * size:.1f}" for dx, dy in points)
    return f'<polygon points="{path}" fill="{color}" {ring} stroke-linejoin="round"/>'


def chart(recs, games, e3b, path):
    """The chart: the share of the games at the known score against the work (a log axis), a step line an arm, a marker
    at the budget of each effort level.  The default and the three arms with the highest mean share over the levels
    are labeled at the right; the legend names all six."""
    width, height, left, right, top, bottom = 940, 660, 64, 150, 196, 70
    plot_w, plot_h = width - left - right, height - top - bottom
    total = len(games)
    y_min, y_max = 0.3, 1.0
    levels = [(e, b) for e, b in LEVELS if e >= 1]

    def px(work):
        span = math.log10(X_MAX) - math.log10(X_MIN)
        return left + plot_w * (math.log10(max(work, X_MIN)) - math.log10(X_MIN)) / span

    def py(share):
        return top + plot_h * (1 - (share - y_min) / (y_max - y_min))

    mean_share = {arm: statistics.mean([count_within(recs[arm], games, b, e3b) / total for _, b in levels])
                  for arm in ARMS}
    best = sorted((a for a in ARMS if a != "A"), key=lambda a: -mean_share[a])[:3]
    labeled = ["A"] + best
    ink, muted, grid = "#1f2328", "#59636e", "#d1d9e0"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, '
           f'sans-serif" role="img" aria-labelledby="title desc">',
           '<title id="title">Race R1: the 251 hard games at the known score against the work</title>',
           '<desc id="desc">The share of the 251 hard games of 3441-5060 at the known score within W work, one step '
           'line an arm, with a marker at the budget of each effort level; the tables of the entry give the '
           'numbers.</desc>',
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
           f'<clipPath id="plot"><rect x="{left}" y="{top - 4}" width="{plot_w + 6}" height="{plot_h + 8}"/>'
           '</clipPath>',
           f'<text x="{left}" y="26" font-size="16" font-weight="600" fill="{ink}">Race R1: the 251 hard games at the '
           f'known score against the work</text>',
           f'<text x="{left}" y="44" font-size="12" fill="{muted}">Share of the games at the known score within W '
           f'work (steps and 32 for each neighborhood); the axis starts at 30%.</text>',
           f'<text x="{left}" y="60" font-size="12" fill="{muted}">A marker is the share at the budget of an effort '
           f'level: E1 is 65,536 work, and each level is twice the one below.</text>',
           f'<text x="{left}" y="76" font-size="12" fill="{muted}">Seeded from the proven game of n - 1; one seed, '
           f'4 threads.</text>',
           f'<text x="{left}" y="92" font-size="12" fill="{muted}">Labeled at the right: the default and the three '
           f'arms with the highest mean share over E1 to E7.</text>']
    for work, text in ((10_000, "10k"), (30_000, "30k")):
        x = px(work)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + plot_h}" stroke="{grid}"/>')
        out.append(f'<text x="{x:.1f}" y="{top + plot_h + 32}" font-size="12" fill="{muted}" text-anchor="middle">'
                   f'{text}</text>')
    for effort, budget in levels:
        x = px(budget)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + plot_h}" stroke="{grid}"/>')
        out.append(f'<text x="{x:.1f}" y="{top + plot_h + 16}" font-size="12" fill="{ink}" text-anchor="middle">'
                   f'E{effort}</text>')
        label = f"{budget / 1000:.1f}k" if budget < 100_000 else f"{budget / 1000:.0f}k" if budget < 1e6 \
            else f"{budget / 1e6:.2f}M"
        out.append(f'<text x="{x:.1f}" y="{top + plot_h + 32}" font-size="12" fill="{muted}" text-anchor="middle">'
                   f'{label}</text>')
    for share in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        y = py(share)
        out.append(f'<line x1="{left}" x2="{left + plot_w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{grid}"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" font-size="12" fill="{muted}" text-anchor="end">'
                   f'{round(100 * share)}%</text>')
    out.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 14}" font-size="12" fill="{muted}" '
               f'text-anchor="middle">work (log axis); effort level above it</text>')
    ends = {}
    for arm in ARMS:
        works = sorted(recs[arm][n]["work"] for n in games if e3b.reached(recs[arm][n]))
        points = [(X_MIN, sum(1 for w in works if w <= X_MIN))]
        for i, w in enumerate(works):
            if w > X_MIN:
                points += [(w, points[-1][1]), (w, i + 1)]
        points.append((BUDGET, len(works)))
        path_d = " ".join(f"{px(w):.1f},{py(c / total):.1f}" for w, c in points)
        dash = f' stroke-dasharray="{DASH[arm]}"' if DASH[arm] else ""
        out.append(f'<polyline points="{path_d}" fill="none" stroke="{COLOR[arm]}" stroke-width="2"{dash} '
                   f'stroke-linecap="round" stroke-linejoin="round" clip-path="url(#plot)"/>')
        ends[arm] = len(works)
    for arm in ARMS:
        for _, budget in levels:
            out.append(marker_svg(MARKER[arm], px(budget), py(count_within(recs[arm], games, budget, e3b) / total),
                                  COLOR[arm]))
    wanted = sorted((py(ends[arm] / total), arm) for arm in labeled)
    placed, previous = {}, -1e9
    for y, arm in wanted:
        y = max(y, previous + 16)
        placed[arm] = y
        previous = y
    for arm in labeled:
        x = left + plot_w + 12
        out.append(f'<line x1="{px(BUDGET) + 6:.1f}" x2="{x - 3:.1f}" y1="{py(ends[arm] / total):.1f}" '
                   f'y2="{placed[arm]:.1f}" stroke="{COLOR[arm]}" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{placed[arm] + 4:.1f}" font-size="12" fill="{ink}">{arm} '
                   f'{100 * ends[arm] / total:.1f}%</text>')
    for i, arm in enumerate(ARMS):  # the legend, two columns of three
        x, y = left + (i // 3) * 400, 118 + (i % 3) * 18
        dash = f' stroke-dasharray="{DASH[arm]}"' if DASH[arm] else ""
        out.append(f'<line x1="{x}" x2="{x + 34}" y1="{y}" y2="{y}" stroke="{COLOR[arm]}" stroke-width="2"{dash} '
                   f'stroke-linecap="round"/>')
        out.append(marker_svg(MARKER[arm], x + 17, y, COLOR[arm]))
        out.append(f'<text x="{x + 44}" y="{y + 4}" font-size="12" fill="{ink}">{arm}: {FLAGS[arm]}</text>')
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    gaps = [b - a for a, b in zip(sorted(placed.values()), sorted(placed.values())[1:])]
    print(f"\n  chart written: {os.path.basename(path)}; games at the known score at the end of each line {ends}; "
          f"labeled {labeled} (the mean share over E1-E7: "
          + ", ".join(f"{a} {100 * mean_share[a]:.1f}" for a in ARMS)
          + f"); gaps between the labels' lines {[round(g, 1) for g in gaps]} px (want 16 or more)")


# ---------------------------------------------------------------------------------------------------------------------


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    results = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "..", "..", "..", "results",
                                                                 "optimal.jsonl.gz")
    e3b_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", E3B_ENTRY)
    e3b = load_module(os.path.join(e3b_dir, "analyze.py"))
    with open(os.path.join(here, "games-all.txt")) as f:
        games = [int(text) for text in f if text.strip()]
    print(f"Race R1: {len(games)} hard games, n {games[0]} to {games[-1]}; arms {list(ARMS)}\n")
    runs(here)
    print()
    files = spans(here, e3b_dir)
    arms_lines, twice = {}, {}
    for arm in ARMS:
        arms_lines[arm], twice[arm] = read_arm(files[arm])
    table = read_table(results, set(games))
    failures = check_lines(arms_lines, table, games, e3b)
    failures += check_files(here, files, twice)
    recs = {arm: {n: e3b.record(line) for n, (line, _, _) in arms_lines[arm].items()} for arm in ARMS}
    ok = all(all(n in recs[arm] for n in games) for arm in ARMS)
    if not ok:
        print("\nchecks failed: incomplete arms; stopping")
        return
    print("\n== 0b. E3b's lines ==")
    annotate(recs, arms_lines, e3b, e3b_dir)
    shares(recs, games, e3b)
    cost(recs, games, e3b)
    pairs(recs, games, e3b)
    unreached(recs, games, e3b)
    times(recs, games, e3b)
    chart(recs, games, e3b, os.path.join(here, "share.svg"))
    print(f"\nchecks failed: {failures}")


if __name__ == "__main__":
    main()
