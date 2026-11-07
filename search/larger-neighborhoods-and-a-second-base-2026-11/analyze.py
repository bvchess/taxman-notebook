#!/usr/bin/env python3
"""Race E3a of the unsound mode: checks the lines of the four arms and prints the entry's numbers.

    nice -n 19 python3 -I analyze.py [DIR [P1_DIR]] > out.txt

DIR (default: the folder of this script) holds arm-a.jsonl (arm A on the 7 games that pilot P1's seed 1 missed),
arm-b.jsonl, arm-c.jsonl and arm-d.jsonl (the 63 games each), arm-a9-check.jsonl (2 games of P1 played again) and
the games' file.  P1_DIR (default: the sibling entry `the-unsound-mode-on-the-hard-games-2026-11`) holds seed-1.jsonl,
whose lines are arm A's on the other 56 games.  The script changes nothing, except that it writes the chart,
race.svg, beside itself; everything it prints is a number of the entry.
"""

import importlib.util
import json
import os
import statistics
import sys

ARMS = "ABCD"
LABEL = {
    "A": "A: default, effort 11",
    "B": "B: --fix 0.5,0.7, effort 9",
    "C": "C: --fix 0.4,0.6, effort 7",
    "D": "D: --survivors, effort 11",
}
SHORT = {"A": "default", "B": "fix 0.5,0.7", "C": "fix 0.4,0.6", "D": "survivors"}
# arm: (effort, fix, survivors) as the lines of the arm record them
SETTING = {"A": (11, [0.7, 0.9], False), "B": (9, [0.5, 0.7], False), "C": (7, [0.4, 0.6], False),
           "D": (11, [0.7, 0.9], True)}
COLOR = {"A": "#2a78d6", "B": "#eb6834", "C": "#6250d6", "D": "#eda100"}  # slots 1, 2, 7 and 4 of the validated palette
DASH = {"A": "", "B": "7 4", "C": "1.5 4", "D": "9 4 2 4"}
COMMIT = "fa05cac"
P1_COMMIT = "e37d6a1"
P1_EFFORT = 9
SEED = 1
THREADS = 4
NEIGHBORHOODS = 64  # a round's neighborhoods
UNIT_LIMIT = 1024  # the steps allowed a neighborhood
BANDS = [(3441, 3800), (3801, 4200), (4201, 4600), (4601, 5060)]  # P1's stretches of n
TIMES = (10, 30, 100, 300, 500)  # seconds of wall time
STEP_BUDGETS = (10_000, 30_000, 100_000, 300_000, 1_000_000, 3_000_000)  # steps of the rounds
HANDOVERS = (10, 30, 100)  # seconds the first arm plays before the second takes over, in the combined runs
SLOW = 16  # the default reached a game after this many rounds: a slow game
MIN_ROUND_TIME = 3.0  # the cost of a round is measured on lines whose rounds took this many seconds at least
COMBINATIONS = (("A", "B"), ("A", "C"), ("D", "B"), ("D", "C"))  # first arm, then second
X_MIN, X_MAX = 2.0, 1000.0  # the chart's axis, in seconds
IGNORED = {"seconds", "start_seconds", "build", "threads", "fix", "survivors", "trajectories"}  # the check of arm A
IGNORED_IMPROVEMENT = {"seconds", "trajectory"}


def median(values):
    return statistics.median(values) if values else None


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "-"


def fmt(x, digits=1):
    return "-" if x is None else f"{x:.{digits}f}" if isinstance(x, float) else str(x)


def read_lines(path):
    """The lines of a file by n, in file order."""
    lines = {}
    with open(path) as f:
        for text in f:
            if text.strip():
                line = json.loads(text)
                lines[line["n"]] = line
    return lines


def record(line):
    """What the race needs of a line: the game's result, its cost, and the time and steps at which it reached the
    known score (the line ends there, so its steps are the steps to it)."""
    stop = line["stop_at_known"]
    reach = stop["round"]
    rec = {
        "n": line["n"], "known": stop["known"], "start": line["start"], "bag": line["in_the_bag"],
        "reach": reach, "short": stop["known"] - line["score"], "start_short": stop["known"] - line["start"],
        "rounds": line["rounds"], "steps": line["steps"], "seconds": line["seconds"],
        "start_seconds": line["start_seconds"], "improvements": line["improvements"],
        "trajectories": line.get("trajectories"), "line": line,
    }
    if reach is not None:
        rec["t_reach"] = line["start_seconds"] if reach == 0 else line["improvements"][-1]["seconds"]
    return rec


def load(directory, p1_directory):
    """The lines of the four arms by n, and P1's seed-1 lines."""
    p1 = read_lines(os.path.join(p1_directory, "seed-1.jsonl"))
    with open(os.path.join(directory, "games.txt")) as f:
        games = [int(text) for text in f if text.strip()]
    lines = {arm: read_lines(os.path.join(directory, f"arm-{arm.lower()}.jsonl")) for arm in "BCD"}
    a_misses = read_lines(os.path.join(directory, "arm-a.jsonl"))
    lines["A"] = {n: a_misses[n] if n in a_misses else p1[n] for n in games}
    check = read_lines(os.path.join(directory, "arm-a9-check.jsonl"))
    return games, lines, p1, a_misses, check


def check_lines(games, lines, p1, a_misses, check):
    """Section A: the checks of the lines.  Returns the number of failures."""
    print("== A. Checks of the lines ==")
    failures = 0

    def fail(text):
        nonlocal failures
        failures += 1
        print("  FAIL:", text)

    p1_misses = sorted(n for n, line in p1.items() if line["stop_at_known"]["round"] is None)
    print(f"  P1's seed 1 missed {len(p1_misses)} games: {p1_misses}; arm A played {sorted(a_misses)} "
          f"(want the same)")
    if p1_misses != sorted(a_misses):
        fail("arm A's games are not P1's misses")
    for arm in ARMS:
        own = lines[arm] if arm != "A" else a_misses
        missing = [n for n in games if n not in lines[arm]]
        extra = sorted(set(own) - set(games))
        print(f"  arm {arm}: {len(own)} lines of its own, {len(lines[arm])} lines in all; missing {missing}; "
              f"extra {extra}")
        failures += len(missing) + len(extra)
        effort, fix, survivors = SETTING[arm]
        methods, builds, over, wrong = {}, set(), [], []
        for n, line in own.items():
            methods[line["method"]] = methods.get(line["method"], 0) + 1
            builds.add((line["build"]["commit"][:7], line["build"]["dirty"]))
            if line["stop_at_known"]["known"] < line["score"]:
                over.append(n)
            for key, want in (("effort", effort), ("fix", fix), ("survivors", survivors), ("seed", SEED),
                              ("threads", THREADS), ("from_known", True)):
                if line[key] != want:
                    wrong.append((n, key, line[key]))
            if line["prev"]["source"] != "table":
                wrong.append((n, "prev.source", line["prev"]["source"]))
            if line["trajectories"] != (2 if survivors else 1):
                wrong.append((n, "trajectories", line["trajectories"]))
            if not survivors and any(i["trajectory"] != 0 for i in line["improvements"]):
                wrong.append((n, "trajectory of an improvement", "not 0"))
        print(f"    methods {methods} (want only search); builds {sorted(builds)} (want [('{COMMIT}', False)]); "
              f"scores above the table's: {over}; settings that differ from the arm's: {wrong}")
        if set(methods) != {"search"}:
            fail(f"arm {arm}: methods {methods}")
        if builds != {(COMMIT, False)}:
            fail(f"arm {arm}: builds {sorted(builds)}")
        failures += len(over) + len(wrong)
    differ = []
    for n in games:
        keys = {(lines[arm][n]["start"], lines[arm][n]["in_the_bag"], lines[arm][n]["stop_at_known"]["known"],
                 json.dumps(lines[arm][n]["setup"], sort_keys=True), json.dumps(lines[arm][n]["prev"], sort_keys=True))
                for arm in ARMS}
        if len(keys) != 1:
            differ.append(n)
    print(f"  start, in_the_bag, the known score, setup and prev differ between arms (P1's lines included) in "
          f"{len(differ)} games: {differ} (want none)")
    failures += len(differ)
    bad_p1 = [n for n in games if p1[n]["build"]["commit"][:7] != P1_COMMIT or p1[n]["build"]["dirty"]]
    print(f"  P1's lines not of {P1_COMMIT}, clean: {bad_p1}")
    print(f"  arm A, the check of this build against P1's seed-1 lines at effort {P1_EFFORT}: "
          f"games {sorted(check)}")
    for n, line in sorted(check.items()):
        old = p1[n]
        if line["build"]["commit"][:7] != COMMIT or line["build"]["dirty"] or line["effort"] != P1_EFFORT:
            fail(f"check line of {n}: build {line['build']} effort {line['effort']}")
        diffs = [key for key in sorted(set(old) | set(line) - IGNORED)
                 if key not in IGNORED and old.get(key) != line.get(key) and key != "improvements"]
        old_improvements = [{k: v for k, v in r.items() if k not in IGNORED_IMPROVEMENT} for r in old["improvements"]]
        new_improvements = [{k: v for k, v in r.items() if k not in IGNORED_IMPROVEMENT} for r in line["improvements"]]
        if old_improvements != new_improvements:
            diffs.append("improvements")
        new_keys = sorted(set(line) - set(old))
        print(f"    game {n}: rounds {line['rounds']} steps {line['steps']} improvements {len(line['improvements'])} "
              f"in both; keys that differ (not times, threads, build, fix, survivors, trajectories): {diffs} "
              f"(want none); keys only the new build writes: {new_keys}; seconds {old['seconds']:.1f} "
              f"(P1) and {line['seconds']:.1f} (now)")
        failures += len(diffs)
    if len(check) != 2:
        fail("the check wants 2 games")
    return failures


def records(lines):
    return {arm: {n: record(line) for n, line in lines[arm].items()} for arm in ARMS}


def per_game(games, recs):
    """Section 1: one row a game, and the reached games' time and steps."""
    print("\n== 1. Per game ==")
    print("  short0 = the known score less the start's, in points (the start is the same in every arm); an arm's cell "
          "is round/seconds/steps at which it held the known score, or 'no' and the final shortfall, the round of "
          "its last improvement, and the seconds the run took")
    print(f"  {'n':>5} {'short0':>6} | " + " | ".join(f"{arm + ': ' + SHORT[arm]:^28}" for arm in ARMS))
    for n in games:
        cells = []
        for arm in ARMS:
            r = recs[arm][n]
            if r["reach"] is not None:
                cells.append(f"r{r['reach']} {r['t_reach']:.1f}s {r['steps']}st")
            else:
                last = max((i["round"] for i in r["improvements"]), default=0)
                cells.append(f"no -{r['short']} last r{last} {r['seconds']:.0f}s")
        print(f"  {n:>5} {recs['A'][n]['start_short']:>6} | " + " | ".join(f"{c:^28}" for c in cells))
    print()
    hard = [n for n in games if recs["A"][n]["start_short"] > 0]
    print(f"  Of the {len(games)} games, {len(games) - len(hard)} hold the known score at the start and {len(hard)} "
          "are short at the start.")
    for arm in ARMS:
        reached = [n for n in games if recs[arm][n]["reach"] is not None]
        reached_hard = [n for n in hard if recs[arm][n]["reach"] is not None]
        print(f"  arm {arm}: reached {len(reached)} of {len(games)} ({pct(len(reached), len(games))}), "
              f"{len(reached_hard)} of the {len(hard)} short at the start")
        missed = [recs[arm][n] for n in games if recs[arm][n]["reach"] is None]
        if missed:
            print(f"    missed {[r['n'] for r in missed]}; final shortfalls {[r['short'] for r in missed]}; "
                  f"seconds of the runs {[round(r['seconds']) for r in missed]}; rounds {[r['rounds'] for r in missed]}")
    return hard


def share_within(arm_recs, limit, key, spent):
    """How many games reached the known score with `key` (t_reach or steps) at most `limit`, and whether the number is
    exact: it is a lower bound if a game that did not reach it stopped before `limit` was spent."""
    count = sum(1 for r in arm_recs.values() if r["reach"] is not None and reach_cost(r, key) <= limit)
    exact = all(r["reach"] is not None or r[spent] >= limit for r in arm_recs.values())
    return count, exact


def reach_cost(rec, key):
    """The seconds or the steps at which a game reached the known score."""
    return rec["t_reach"] if key == "t_reach" else rec["steps"]


def cell(count, exact, total):
    return f"{count}{'' if exact else '+'} ({100 * count / total:.1f}%)"


def race(games, recs):
    """Section 2: the share at the known score at equal time and at equal steps; the chart."""
    total = len(games)
    print(f"\n== 2. The race at equal time: games of {total} at the known score within T seconds of wall time on "
          f"{THREADS} threads (the start's time counted) ==")
    print("  '+' marks a lower bound: some game the arm did not reach ended its run before T")
    print(f"  {'':>14} | " + " | ".join(f"{t:>3} s".rjust(12) for t in TIMES))
    for arm in ARMS:
        cells = [cell(*share_within(recs[arm], t, "t_reach", "seconds"), total) for t in TIMES]
        print(f"  {'arm ' + arm + ' ' + SHORT[arm]:>14} | " + " | ".join(f"{c:>12}" for c in cells))
    print("  the seconds at which the runs of the arm that missed ended (each one's own budget):")
    for arm in ARMS:
        ends = sorted(round(r["seconds"]) for r in recs[arm].values() if r["reach"] is None)
        print(f"    arm {arm}: {ends}")
    print("\n  Of the same table, the games short at the start only "
          f"({sum(1 for n in games if recs['A'][n]['start_short'] > 0)} games) at the known score within T seconds:")
    hard = {arm: {n: r for n, r in recs[arm].items() if r["start_short"] > 0} for arm in ARMS}
    for arm in ARMS:
        cells = [cell(*share_within(hard[arm], t, "t_reach", "seconds"), len(hard[arm])) for t in TIMES]
        print(f"  {'arm ' + arm + ' ' + SHORT[arm]:>14} | " + " | ".join(f"{c:>12}" for c in cells))

    print(f"\n== 2b. The race at equal steps: games of {total} at the known score within S steps of the rounds "
          "(the start's steps, the same in every arm, not counted) ==")
    print(f"  {'':>14} | " + " | ".join(f"{s:>9,}".rjust(12) for s in STEP_BUDGETS))
    for arm in ARMS:
        cells = [cell(*share_within(recs[arm], s, "steps", "steps"), total) for s in STEP_BUDGETS]
        print(f"  {'arm ' + arm + ' ' + SHORT[arm]:>14} | " + " | ".join(f"{c:>12}" for c in cells))
    print("  the steps at which the runs of the arm that missed ended:")
    for arm in ARMS:
        ends = sorted(r["steps"] for r in recs[arm].values() if r["reach"] is None)
        print(f"    arm {arm}: {ends}")


def estimate(games, recs, p1):
    """Section 2c: the estimate for the 568 searched games of 3441-5060, by P1's rule: the games whose start held the
    best score in the run of 2026-11-01 are taken as holding it, and the sample's share stands for the others."""
    total = len(games)
    hard = p1.SEARCHED - p1.SEARCHED_WITH_START_OPTIMAL

    def est(share):
        return 100 * (p1.SEARCHED_WITH_START_OPTIMAL + hard * share) / p1.SEARCHED

    print(f"\n== 2c. Estimate for all {p1.SEARCHED} searched games of 3441-5060 (P1's rule: ({p1.SEARCHED_WITH_START_OPTIMAL} "
          f"+ {hard} x the sample's share) / {p1.SEARCHED}; the 90% interval is the exact binomial interval of the "
          "sample's share) ==")
    print("  '+' marks a lower bound.  'own budget' is the whole run of the arm, whatever its seconds.")
    print(f"  {'':>16} | " + " | ".join(f"{t:>3} s".rjust(8) for t in TIMES) + f" | {'own budget':>10} {'k/63':>5} "
          f"{'90% interval':>16}")
    for arm in ARMS:
        cells = []
        for t in TIMES:
            count, exact = share_within(recs[arm], t, "t_reach", "seconds")
            cells.append(f"{est(count / total):.1f}%{'' if exact else '+'}")
        k = sum(1 for r in recs[arm].values() if r["reach"] is not None)
        low, high = p1.clopper_pearson(k, total)
        print(f"  {'arm ' + arm + ' ' + SHORT[arm]:>16} | " + " | ".join(f"{c:>8}" for c in cells)
              + f" | {est(k / total):>9.1f}% {k:>5} {est(low):>7.1f}-{est(high):.1f}%")


def curve(arm_recs):
    """The step function of the chart: (seconds, games at the known score) at each game's time, and the seconds
    until which it is exact (a game that did not reach it ended its run then)."""
    times = sorted(r["t_reach"] for r in arm_recs.values() if r["reach"] is not None)
    exact_until = min((r["seconds"] for r in arm_recs.values() if r["reach"] is None), default=float("inf"))
    return times, exact_until


def x_of(seconds, left, width):
    import math
    return left + width * (math.log10(seconds) - math.log10(X_MIN)) / (math.log10(X_MAX) - math.log10(X_MIN))


def chart(games, recs, path):
    """The chart: the share of the games at the known score against the seconds, a log axis, one line an arm."""
    width, height, left, right, top, bottom = 900, 540, 64, 200, 124, 56
    plot_w, plot_h = width - left - right, height - top - bottom
    total = len(games)
    y_min, y_max = 0.3, 1.0

    def px(seconds):
        return x_of(seconds, left, plot_w)

    def py(share):
        return top + plot_h * (1 - (share - y_min) / (y_max - y_min))

    ink, muted, grid = "#1f2328", "#59636e", "#d1d9e0"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, '
           f'sans-serif">', f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
           f'<clipPath id="plot"><rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}"/></clipPath>',
           f'<text x="{left}" y="26" font-size="16" font-weight="600" fill="{ink}">Race E3a: the 63 hard games at the '
           f'known score against the time (4 threads)</text>',
           f'<text x="{left}" y="46" font-size="12" fill="{muted}">Share of the 63 games at the known score by '
           f'seconds of wall time, the start counted; the axis starts at 30%.</text>',
           f'<text x="{left}" y="62" font-size="12" fill="{muted}">A thin line is a lower bound: a game the arm had '
           f'not reached ended its run before that time.</text>']
    for t in (3, 10, 30, 100, 300, 500, 1000):
        x = px(t)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + plot_h}" stroke="{grid}"/>')
        out.append(f'<text x="{x:.1f}" y="{top + plot_h + 18}" font-size="12" fill="{muted}" text-anchor="middle">'
                   f'{t}</text>')
    for s in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        y = py(s)
        out.append(f'<line x1="{left}" x2="{left + plot_w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{grid}"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" font-size="12" fill="{muted}" text-anchor="end">'
                   f'{round(100 * s)}%</text>')
    out.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 14}" font-size="12" fill="{muted}" '
               f'text-anchor="middle">seconds of wall time (log axis)</text>')
    ends = {}
    for arm in ARMS:
        times, exact_until = curve(recs[arm])
        last = times[-1]
        stop = X_MAX
        points = [(X_MIN, sum(1 for t in times if t <= X_MIN))]
        for i, t in enumerate(times):
            points.append((t, i))
            points.append((t, i + 1))
        points.append((stop, len(times)))
        solid = [(t, c) for t, c in points if t <= exact_until]
        solid.append((min(exact_until, stop), sum(1 for t in times if t <= exact_until)))
        rest = [(max(t, exact_until), c) for t, c in points if t >= exact_until]
        rest.insert(0, (exact_until, sum(1 for t in times if t <= exact_until)))

        def path_of(pts):
            return " ".join(f"{px(max(t, X_MIN)):.1f},{py(c / total):.1f}" for t, c in pts)

        dash = f' stroke-dasharray="{DASH[arm]}"' if DASH[arm] else ""
        if exact_until < X_MAX and rest:
            out.append(f'<polyline points="{path_of(rest)}" fill="none" stroke="{COLOR[arm]}" stroke-width="1.2" '
                       f'opacity="0.55"{dash} stroke-linecap="round" clip-path="url(#plot)"/>')
        out.append(f'<polyline points="{path_of(solid)}" fill="none" stroke="{COLOR[arm]}" stroke-width="2.5"'
                   f'{dash} stroke-linecap="round" stroke-linejoin="round" clip-path="url(#plot)"/>')
        ends[arm] = (len(times), last)
    # direct labels at the right edge, spread to be at least 17 px apart
    wanted = sorted(((py(ends[arm][0] / total), arm) for arm in ARMS))
    placed, previous = {}, -1e9
    for y, arm in wanted:
        y = max(y, previous + 17)
        placed[arm] = y
        previous = y
    for arm in ARMS:
        x = left + plot_w + 10
        out.append(f'<line x1="{left + plot_w:.1f}" x2="{x - 3:.1f}" y1="{py(ends[arm][0] / total):.1f}" '
                   f'y2="{placed[arm]:.1f}" stroke="{COLOR[arm]}" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{placed[arm] + 4:.1f}" font-size="12" fill="{ink}">{arm} {SHORT[arm]}: '
                   f'{ends[arm][0]}</text>')
    # the legend, two arms a row
    for i, arm in enumerate(ARMS):
        x, y = left + (i % 2) * 300, 86 + (i // 2) * 18
        dash = f' stroke-dasharray="{DASH[arm]}"' if DASH[arm] else ""
        out.append(f'<line x1="{x}" x2="{x + 30}" y1="{y}" y2="{y}" stroke="{COLOR[arm]}" stroke-width="2.5"{dash} '
                   f'stroke-linecap="round"/>')
        out.append(f'<text x="{x + 38}" y="{y + 4}" font-size="12" fill="{ink}">{LABEL[arm]}</text>')
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"\n  chart written: {path} (end of each line, games at the known score: "
          f"{ {arm: ends[arm][0] for arm in ARMS} })")


def who_reaches(games, recs):
    """Section 3: which arm reaches which game."""
    print("\n== 3. Which arm reaches which of the hard games ==")
    misses = sorted(n for n in games if recs["A"][n]["reach"] is None or recs["A"][n]["reach"] > 256)
    print("  P1's seed-1 misses (the default at effort 9), with the arms' results (round/seconds/steps, or the final "
          "shortfall and the last improvement's round):")
    print(f"  {'n':>5} {'short0':>6} | " + " | ".join(f"{arm + ': ' + SHORT[arm]:^28}" for arm in ARMS))
    for n in misses:
        cells = []
        for arm in ARMS:
            r = recs[arm][n]
            last = max((i["round"] for i in r["improvements"]), default=0)
            cells.append(f"r{r['reach']} {r['t_reach']:.0f}s {r['steps']}st" if r["reach"] is not None
                         else f"no -{r['short']} last r{last} {r['seconds']:.0f}s")
        print(f"  {n:>5} {recs['A'][n]['start_short']:>6} | " + " | ".join(f"{c:^28}" for c in cells))
    for arm in ARMS:
        reached = [n for n in misses if recs[arm][n]["reach"] is not None]
        print(f"  arm {arm} reaches {len(reached)} of the {len(misses)}: {reached}")
    reached_by_a = [n for n in games if recs["A"][n]["reach"] is not None]
    print("\n  Games the default reaches (within its effort) that another arm does not:")
    for arm in "BCD":
        lost = [n for n in reached_by_a if recs[arm][n]["reach"] is None]
        print(f"    arm {arm} loses {len(lost)}: {lost}")
    print("  Games another arm reaches that the default does not:")
    for arm in "BCD":
        gained = [n for n in games if recs[arm][n]["reach"] is not None and recs["A"][n]["reach"] is None]
        print(f"    arm {arm} gains {len(gained)}: {gained}")
    print("  Games no arm reaches:", [n for n in games if all(recs[a][n]["reach"] is None for a in ARMS)])
    print("  Games the default reaches within 256 rounds (P1's budget) and arm B or C does not:")
    for arm in "BC":
        lost = [n for n in games if recs["A"][n]["reach"] is not None and recs["A"][n]["reach"] <= 256
                and recs[arm][n]["reach"] is None]
        print(f"    arm {arm}: {lost}")
    print("\n  The time to the known score, on the games two arms both reach and that are short at the start "
          "(median of the ratio of the second arm's seconds to the first's, and of the steps):")
    for first, second in (("A", "B"), ("A", "C"), ("A", "D"), ("B", "C")):
        both = [n for n in games if recs[first][n]["reach"] and recs[second][n]["reach"]]
        both = [n for n in both if recs[first][n]["start_short"] > 0]
        ratios_t = [recs[second][n]["t_reach"] / recs[first][n]["t_reach"] for n in both]
        ratios_s = [recs[second][n]["steps"] / recs[first][n]["steps"] for n in both]
        faster = sum(1 for x in ratios_t if x < 1)
        rounds_f, rounds_s = [recs[first][n]["reach"] for n in both], [recs[second][n]["reach"] for n in both]
        print(f"    {second} against {first}: {len(both)} games; seconds ratio median {median(ratios_t):.2f} "
              f"({faster} games faster); steps ratio median {median(ratios_s):.2f}; rounds median {median(rounds_s)} "
              f"against {median(rounds_f)}")
    slow = [n for n in games if recs["A"][n]["reach"] is not None and recs["A"][n]["reach"] > SLOW]
    print(f"\n  The games the default reached after round {SLOW} (slow), with each arm's round and seconds "
          "(the default's rounds are cheap, the larger neighborhoods' dear):")
    for n in slow:
        cells = [f"r{recs[arm][n]['reach']} {recs[arm][n]['t_reach']:.0f}s" if recs[arm][n]["reach"] is not None
                 else f"no -{recs[arm][n]['short']}" for arm in ARMS]
        print(f"    {n}: " + " | ".join(f"{arm} {c}" for arm, c in zip(ARMS, cells)))
    print("\n  The rounds an arm needed to reach the games short at the start, sorted:")
    for arm in ARMS:
        rounds = sorted(r["reach"] for r in recs[arm].values() if r["reach"] and r["start_short"] > 0)
        print(f"    arm {arm}: {len(rounds)} games: {rounds}")


def survivors_arm(games, recs):
    """The trajectories of arm D."""
    print("\n== 3b. Arm D: which trajectory made the improvements ==")
    counts = {0: 0, 1: 0}
    first_only, final = [], {0: [], 1: []}
    by_game = {}
    for n in games:
        r = recs["D"][n]
        made = [i["trajectory"] for i in r["improvements"]]
        for t in made:
            counts[t] += 1
        by_game[n] = made
        if r["reach"] is not None and made:
            final[made[-1]].append(n)
    print(f"  improvements by trajectory (0: the start's, 1: the survivors'): {counts}")
    print(f"  games whose reaching improvement came from trajectory 0: {len(final[0])}, from trajectory 1: "
          f"{len(final[1])}: {final[1]}")
    only1 = [n for n, made in by_game.items() if made and set(made) == {1}]
    both = [n for n, made in by_game.items() if set(made) == {0, 1}]
    print(f"  games improved only by trajectory 1: {len(only1)} {only1}; by both: {len(both)}")
    for n in games:
        r = recs["D"][n]
        if r["reach"] is None:
            print(f"    missed {n}: improvements by trajectory {by_game[n]}, final short {r['short']}, "
                  f"start short {r['start_short']}")
    # the survivors' own incumbent is not in the lines; its first improvement to the game's set shows when it passed
    print("  the trajectory of each improvement, in order, per game with improvements (0: the start's, 1: the "
          "survivors'):")
    for n in games:
        if by_game[n]:
            reached = recs["D"][n]["reach"]
            print(f"    {n}: {','.join(str(t) for t in by_game[n])}" + (f" (reached at round {reached})" if reached else
                  " (missed)"))


def rounds_seconds(rec):
    """The seconds a line spent in its rounds: up to the round that reached the known score for a line that stopped
    there (so that the replay and the write after the last round do not count), else over the whole run."""
    return (rec["t_reach"] if rec["reach"] is not None else rec["seconds"]) - rec["start_seconds"]


def measurable(rec):
    """Whether a line's rounds took long enough for the fixed cost of a line (about 0.1 s) to weigh little."""
    return rec["rounds"] >= 1 and rounds_seconds(rec) >= MIN_ROUND_TIME


def round_cost(rec):
    """The seconds a round took in a line."""
    return rounds_seconds(rec) / rec["rounds"]


def costs(games, recs):
    """Section 4: the cost of a round and of a neighborhood by arm and stretch of n."""
    print("\n== 4. Cost: seconds per round, steps per neighborhood by arm and stretch of n ==")
    print(f"  Over the lines whose rounds took at least {MIN_ROUND_TIME:.0f} s, so that the fixed cost of a line weighs "
          f"little.  Seconds per round = (seconds up to the last round - start_seconds) / rounds; {THREADS} threads at "
          "nice 19 on a loaded machine; arm A is P1's seed-1 lines and the 7 long ones.  ms/step = thread-milliseconds "
          f"of a step = seconds per round x threads / {NEIGHBORHOODS} / steps per neighborhood.")
    print(f"  {'arm':>3} {'band':>11} {'lines':>5} | {'s/round med':>11} {'min':>6} {'max':>7} | "
          f"{'steps/nb med':>12} {'min':>7} {'max':>7} | {'ms/step med':>11} | {'start s med':>11}")
    whole = (BANDS[0][0], BANDS[-1][1])
    for arm in ARMS:
        for band in BANDS + [whole]:
            spr, spn, mss, starts = [], [], [], []
            for n in games:
                r = recs[arm][n]
                if not band[0] <= n <= band[1]:
                    continue
                starts.append(r["start_seconds"])
                if measurable(r):
                    spr.append(round_cost(r))
                    spn.append(r["steps"] / (r["rounds"] * NEIGHBORHOODS))
                    mss.append(1000 * spr[-1] * THREADS / NEIGHBORHOODS / spn[-1])
            if not spr:
                print(f"  {arm:>3} {band[0]:>5}-{band[1]:<5} {0:>5} | (no line with the rounds of that length)")
                continue
            print(f"  {arm:>3} {band[0]:>5}-{band[1]:<5} {len(spr):>5} | {median(spr):>11.3f} {min(spr):>6.3f} "
                  f"{max(spr):>7.3f} | {median(spn):>12.1f} {min(spn):>7.1f} {max(spn):>7.1f} | "
                  f"{median(mss):>11.2f} | {median(starts):>11.2f}")
    print("\n  The cost of the arm against the default's, game by game, over the games whose rounds are long enough in both "
          "(median, with the lowest and highest):")
    for arm in "BCD":
        both = [n for n in games if measurable(recs[arm][n]) and measurable(recs["A"][n])]
        ts = [round_cost(recs[arm][n]) / round_cost(recs["A"][n]) for n in both]
        ss = [(recs[arm][n]["steps"] / recs[arm][n]["rounds"]) / (recs["A"][n]["steps"] / recs["A"][n]["rounds"])
              for n in both]
        print(f"    arm {arm}: {len(both)} games; seconds per round x{median(ts):.2f} ({min(ts):.2f} to "
              f"{max(ts):.2f}); steps per round x{median(ss):.2f} ({min(ss):.2f} to {max(ss):.2f})")
    print("\n  Total seconds of the arms' lines:")
    for arm in ARMS:
        own = [recs[arm][n] for n in games]
        total = sum(r["seconds"] for r in own)
        missed = sum(r["seconds"] for r in own if r["reach"] is None)
        print(f"    arm {arm}: {total:.0f} s over {len(own)} lines ({total / 3600:.2f} h of {THREADS} threads), "
              f"{missed:.0f} s of them in the {sum(1 for r in own if r['reach'] is None)} games it missed")


def combined(games, recs):
    """Section 5: one arm for a while, then another played again from the start (a portfolio of two runs).

    The second run pays its own seconds less its start, which the first run made; the incumbent of the first run is not
    carried on, so this is not a schedule that moves to larger neighborhoods in the middle of a run."""
    print("\n== 5. One arm for H seconds, then another played again from the start ==")
    print("  A game is at the known score within T seconds if the first arm reaches it by H, or H plus the second arm's "
          "seconds (less its start) are at most T.  The incumbent is not carried over: two runs, not one schedule.  "
          "'+' marks a lower bound.")
    total = len(games)
    print(f"  {'':>16} | " + " | ".join(f"{t:>3} s".rjust(12) for t in TIMES))
    for arm in ARMS:
        cells = [cell(*share_within(recs[arm], t, "t_reach", "seconds"), total) for t in TIMES]
        print(f"  {'arm ' + arm + ' alone':>16} | " + " | ".join(f"{c:>12}" for c in cells))
    for first, second in COMBINATIONS:
        for handover in HANDOVERS:
            cells = []
            for t in TIMES:
                count, exact = 0, True
                for n in games:
                    a, o = recs[first][n], recs[second][n]
                    if a["reach"] is not None and a["t_reach"] <= min(handover, t):
                        count += 1
                    elif t > handover:
                        left = t - handover
                        if o["reach"] is not None and o["t_reach"] - o["start_seconds"] <= left:
                            count += 1
                        elif o["reach"] is None and o["seconds"] - o["start_seconds"] < left:
                            exact = False
                cells.append(cell(count, exact, total))
            print(f"  {first + ' ' + str(handover) + ' s, ' + second:>16} | " + " | ".join(f"{c:>12}" for c in cells))
    print("\n  The cost of the plans: the seconds of 4 threads the 63 games take in all (a game's seconds up to the known "
          "score, or its whole run if it is never reached; a combined plan's second run less its start), and the "
          "games reached in the end:")
    print(f"  {'':>16} | {'seconds':>8} {'reached':>8}")
    for arm in ARMS:
        spent = sum(recs[arm][n]["t_reach"] if recs[arm][n]["reach"] is not None else recs[arm][n]["seconds"]
                    for n in games)
        print(f"  {'arm ' + arm + ' alone':>16} | {spent:>8.0f} {sum(1 for n in games if recs[arm][n]['reach'] is not None):>8}")
    for first, second in COMBINATIONS:
        for handover in HANDOVERS:
            spent, reached = 0.0, 0
            for n in games:
                a, o = recs[first][n], recs[second][n]
                if a["reach"] is not None and a["t_reach"] <= handover:
                    spent += a["t_reach"]
                    reached += 1
                else:
                    spent += handover
                    second_cost = o["t_reach"] - o["start_seconds"] if o["reach"] is not None else o["seconds"] - o["start_seconds"]
                    spent += second_cost
                    reached += o["reach"] is not None
            print(f"  {first + ' ' + str(handover) + ' s, ' + second:>16} | {spent:>8.0f} {reached:>8}")


def load_module(path):
    """A module of another entry, by its path (P1's analyze.py, for its interval and its counts of games)."""
    sys.dont_write_bytecode = True  # leave no __pycache__ in the other entry's folder
    spec = importlib.util.spec_from_file_location("p1_analyze", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    directory = sys.argv[1] if len(sys.argv) > 1 else here
    p1_directory = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "the-unsound-mode-on-the-hard-games-2026-11")
    games, lines, p1, a_misses, check = load(directory, p1_directory)
    print(f"{len(games)} games, n {games[0]} to {games[-1]}")
    failures = check_lines(games, lines, p1, a_misses, check)
    recs = records(lines)
    per_game(games, recs)
    race(games, recs)
    estimate(games, recs, load_module(os.path.join(p1_directory, "analyze.py")))
    chart(games, recs, os.path.join(directory, "race.svg"))
    who_reaches(games, recs)
    survivors_arm(games, recs)
    costs(games, recs)
    combined(games, recs)
    print(f"\nchecks failed: {failures}")


if __name__ == "__main__":
    main()
