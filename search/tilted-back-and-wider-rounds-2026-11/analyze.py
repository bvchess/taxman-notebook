#!/usr/bin/env python3
"""Race E3b of the unsound mode: checks the lines of the arms and prints the entry's numbers.

    nice -n 19 python3 -I analyze.py [DIR [P1_DIR [E3A_DIR]]] > out.txt

DIR (default: the folder of this script) holds arm-a.jsonl, arm-t.jsonl, arm-k.jsonl, arm-w.jsonl, arm-tkw.jsonl,
arm-tk.jsonl and arm-tkw16.jsonl (Part 1: the 63 games of games.txt, each arm), and part2-a.jsonl and
part2-WINNER.jsonl (Part 2: the games of games-part2.txt, the default and the arm that won Part 1).  P1_DIR (default:
the sibling entry `the-unsound-mode-on-the-hard-games-2026-11`) holds seed-1.jsonl, and E3A_DIR (default: the sibling
entry `larger-neighborhoods-and-a-second-base-2026-11`) the lines of its arm A, for the checks.  The script changes
nothing, except that it writes the chart, race.svg, beside itself; everything it prints is a number of the entry.
"""

import glob
import importlib.util
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta

ARMS = ["A", "T", "K", "W", "TKW", "TK", "TKW16"]
OPTIONS = {  # the options of each arm as its lines record them: tilt, back, widen
    "A": (False, 0, None), "T": (True, 0, None), "K": (False, 8, None), "W": (False, 0, 4),
    "TKW": (True, 8, 4), "TK": (True, 8, None), "TKW16": (True, 8, 16),
}
FLAGS = {
    "A": "none", "T": "--tilt", "K": "--back 8", "W": "--widen 4", "TKW": "--tilt --back 8 --widen 4",
    "TK": "--tilt --back 8", "TKW16": "--tilt --back 8 --widen 16",
}
COMMIT = "cd3c3ac"
PROVER_ENDED = datetime(2026, 11, 7, 0, 21, 24)  # Pacific time: 08:21:24Z in the prover's log, "ended: complete"
EFFORT = 7
ROUND_WORK = 65_536
LEVELS = [(e, ROUND_WORK * 2 ** (e - 1)) for e in range(1, EFFORT + 1)]  # (effort, budget in work)
BUDGET = LEVELS[-1][1]
SEED = 1
THREADS = 4
FIX = [0.7, 0.9]
NEIGHBORHOOD_WORK = 32  # the work a neighborhood costs beside its steps
WORK_BUDGETS = (10_000, 30_000, 100_000, 300_000, 1_000_000, 4_000_000)
TIMES = (10, 30, 100, 300, 600)  # seconds of wall time on 4 threads
WINNER_BUDGET = 1_000_000  # the winner reaches the most games within this work
BANDS = [(3441, 3800), (3801, 4200), (4201, 4600), (4601, 5060)]
MIN_ROUND_TIME = 3.0  # a line's cost is measured when its rounds took this many seconds at least
SEARCHED, SEARCHED_WITH_START_OPTIMAL = 568, 317  # P1's counts: games of 3441-5060 of method search, start optimal
HARD = SEARCHED - SEARCHED_WITH_START_OPTIMAL  # 251
BAND_ALL = (BANDS[0][0], BANDS[-1][1])
# chart: the colors are slots of the validated categorical palette; the default is the neutral ink
COLOR = {"A": "#1f2328", "T": "#2a78d6", "K": "#eb6834", "W": "#1baf7a", "TKW": "#6250d6", "TK": "#e87ba4",
         "TKW16": "#eda100"}
DASH = {"A": "", "T": "", "K": "7 4", "W": "1.5 4", "TKW": "", "TK": "9 4 2 4", "TKW16": "3 3"}
X_MIN, X_MAX = 1_000, 4_400_000
P1_ENTRY = "the-unsound-mode-on-the-hard-games-2026-11"
E3A_ENTRY = "larger-neighborhoods-and-a-second-base-2026-11"


def median(values):
    return statistics.median(values) if values else None


def percentile(values, q):
    """The value of nearest rank at fraction q (q = 0.9: the 90th percentile)."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)] if ordered else None


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "-"


def fmt(x, digits=1):
    return "-" if x is None else f"{x:.{digits}f}" if isinstance(x, float) else str(x)


def read_lines(path):
    """The lines of a file by n, in file order; none if there is no file."""
    lines = {}
    if os.path.exists(path):
        with open(path) as f:
            for text in f:
                if text.strip():
                    line = json.loads(text)
                    lines[line["n"]] = line
    return lines


def read_games(path):
    with open(path) as f:
        return [int(text) for text in f if text.strip()]


def game_starts(directory):
    """When each game began, from the logs: {(part, arm, n): time}, the part being "part1" or "part2"."""
    starts = {}
    for name in sorted(os.listdir(directory)):
        if name.endswith(".log") and name.startswith(("arm-", "part2-")):
            part = "part2" if name.startswith("part2-") else "part1"
            with open(os.path.join(directory, name)) as f:
                for text in f:
                    if text.startswith("# 20") and " arm " in text:
                        words = text.split()
                        starts[(part, words[5], int(words[7].rstrip(":")))] = datetime.strptime(
                            text[2:21], "%Y-%m-%d %H:%M:%S")
    return starts


def annotate(recs, part, starts):
    """Marks the games that began after the prover ended: their seconds are not those of a loaded machine."""
    for arm, arm_recs in recs.items():
        for n, rec in arm_recs.items():
            rec["unloaded"] = starts[(part, arm, n)] >= PROVER_ENDED


def record(line):
    """What the race needs of a line: the game's result, its cost, and the work, steps and seconds at which it held the
    known score (the line ends there, so these are the line's own)."""
    reach = line["stop_at_known"]["round"]
    improvements = line["improvements"]
    rec = {
        "n": line["n"], "known": line["stop_at_known"]["known"], "start": line["start"], "bag": line["in_the_bag"],
        "reach": reach, "short": line["stop_at_known"]["known"] - line["score"],
        "start_short": line["stop_at_known"]["known"] - line["start"], "rounds": line["rounds"],
        "neighborhoods": line["neighborhoods"], "steps": line["steps"], "work": line["work"],
        "seconds": line["seconds"], "start_seconds": line["start_seconds"], "improvements": improvements,
        "trajectories": line["trajectories"], "stage_rounds": line["stage_rounds"], "line": line,
    }
    if reach is not None:
        last = improvements[-1] if improvements else None
        rec["t_reach"] = last["seconds"] if last else line["start_seconds"]
        rec["by"] = last["trajectory"] if last else 0  # the trajectory that made the reaching improvement
        rec["stage"] = last["stage"] if last else 0
    return rec


def records(lines_by_arm):
    return {arm: {n: record(line) for n, line in lines.items()} for arm, lines in lines_by_arm.items()}


def reached(rec, limit=None):
    """Whether the game held the known score, within `limit` work if given."""
    return rec["reach"] is not None and (limit is None or rec["work"] <= limit)


def reach_cost(rec, key):
    """The seconds or the work at which a game reached the known score."""
    return rec["t_reach"] if key == "seconds" else rec["work"]


def share_within(arm_recs, games, limit, key):
    """How many of the games held the known score within `limit` (work or seconds), and whether the number is exact:
    it is a lower bound if a game is missing, or did not reach it and ended its run before `limit`."""
    count, exact = 0, True
    for n in games:
        rec = arm_recs.get(n)
        if rec is None:
            exact = False
        elif reached(rec) and reach_cost(rec, key) <= limit:
            count += 1
        elif not reached(rec) and rec[key] < limit:
            exact = False
    return count, exact


def cell(count, exact, total):
    return f"{count}{'' if exact else '+'} ({100 * count / total:.1f}%)"


def band_of(n):
    return next(b for b in BANDS if b[0] <= n <= b[1])


# ---------------------------------------------------------------------------------------------------------------------
# Checks of the lines


def check_lines(games, lines, p1, e3a_a, part):
    """The checks of the lines of the arms in `lines` on `games`.  Returns the number of failures."""
    print(f"== A. Checks of the lines ({part}) ==")
    failures = 0

    def fail(text):
        nonlocal failures
        failures += 1
        print("  FAIL:", text)

    for arm, arm_lines in lines.items():
        tilt, back, widen = OPTIONS[arm]
        missing = [n for n in games if n not in arm_lines]
        extra = sorted(set(arm_lines) - set(games))
        print(f"  arm {arm} ({FLAGS[arm]}): {len(arm_lines)} lines; missing {missing}; extra {extra}")
        if extra:
            fail(f"arm {arm}: extra games {extra}")
        methods, builds, bad = {}, set(), []
        for n, line in arm_lines.items():
            methods[line["method"]] = methods.get(line["method"], 0) + 1
            builds.add((line["build"]["commit"][:7], line["build"]["dirty"]))
            for key, want in (("effort", EFFORT), ("budget", BUDGET), ("fix", FIX), ("seed", SEED),
                              ("threads", THREADS), ("from_known", True), ("tilt", tilt), ("back", back),
                              ("widen", widen)):
                if line[key] != want:
                    bad.append((n, key, line[key]))
            if line["prev"]["source"] != "table":
                bad.append((n, "prev.source", line["prev"]["source"]))
            if line["stop_at_known"]["known"] < line["score"]:
                bad.append((n, "score above the table's", line["score"]))
            bad += check_one(line, tilt, back, widen)
        print(f"    methods {methods} (want only search); builds {sorted(builds)} (want [('{COMMIT}', False)]); "
              f"deviations from the arm's options and the line's own consistency: {bad} (want none)")
        if set(methods) - {"search"}:
            fail(f"arm {arm}: methods {methods}")
        if builds - {(COMMIT, False)}:
            fail(f"arm {arm}: builds {sorted(builds)}")
        failures += len(bad)
    differ = []
    for n in games:
        keys = {(line[n]["start"], line[n]["in_the_bag"], line[n]["stop_at_known"]["known"],
                 json.dumps(line[n]["setup"], sort_keys=True), json.dumps(line[n]["prev"], sort_keys=True))
                for line in lines.values() if n in line}
        if len(keys) > 1:
            differ.append(n)
    print(f"  start, in_the_bag, the known score, setup and prev differ between arms in {len(differ)} games: {differ} "
          "(want none)")
    failures += len(differ)
    if part == "Part 1":
        against_p1 = [n for n in games if any(n in line and (line[n]["start"] != p1[n]["start"]
                                                             or line[n]["stop_at_known"]["known"]
                                                             != p1[n]["stop_at_known"]["known"]
                                                             or line[n]["in_the_bag"] != p1[n]["in_the_bag"])
                                              for line in lines.values())]
        print(f"  start, in_the_bag or known score unlike P1's seed-1 line in {len(against_p1)} games: {against_p1} "
              "(want none)")
        failures += len(against_p1)
        failures += check_against_e3a(games, lines.get("A", {}), e3a_a)
    return failures


def runs(directory):
    """Section 0: when each run played (the first game's start to the last game's end, Pacific time), from its log."""
    print("== 0. The runs, from the logs (a game starts at the log's time and ends that many seconds later) ==")
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".log") or not name.startswith(("arm-", "part2-")):
            continue
        starts, ends, seconds, games, lost, late = [], [], 0.0, 0, 0.0, 0
        with open(os.path.join(directory, name)) as f:
            for text in f:
                if text.startswith("# 20"):
                    starts.append(datetime.strptime(text[2:21], "%Y-%m-%d %H:%M:%S"))
                elif text.startswith("# game") and " exit " in text:
                    took = float(text.split(" after ")[1].split(" s")[0])
                    ends.append(starts[-1] + timedelta(seconds=took))
                    if " exit 0 " in text:
                        seconds += took
                        games += 1
                        late += starts[-1] >= PROVER_ENDED
                    else:
                        lost += took  # a game that a stop signal ended, which no line records
        if starts and ends:
            print(f"  {name}: {starts[0]:%Y-%m-%d %H:%M} to {max(ends):%H:%M}, {games} games recorded, "
                  f"{seconds / 3600:.2f} h of 4 threads; {late} began after the prover ended "
                  f"({PROVER_ENDED:%m-%d %H:%M:%S})"
                  + (f"; a game ended by SIGTERM after {lost:.0f} s, not recorded" if lost else ""))


def check_one(line, tilt, back, widen):
    """The consistency of one line with itself and its arm's options; a list of the deviations."""
    n, bad = line["n"], []
    trajectories = line["trajectories"]
    if trajectories[0] != "start" or len(set(trajectories)) != len(trajectories) or len(trajectories) > back + 1:
        bad.append((n, "trajectories", trajectories))
    elif trajectories[1:] != sorted(trajectories[1:], reverse=True) or any(not n - back <= m < n
                                                                           for m in trajectories[1:]):
        bad.append((n, "trajectories not distinct earlier games within back", trajectories))
    if back == 0 and trajectories != ["start"]:
        bad.append((n, "trajectories without back", trajectories))
    stage_rounds = line["stage_rounds"]
    if len(stage_rounds) != len(trajectories) or any(sum(s) != line["rounds"] for s in stage_rounds):
        bad.append((n, "stage_rounds", stage_rounds))
    if widen is None and any(s[1] or s[2] for s in stage_rounds):
        bad.append((n, "stage_rounds beyond stage 0 without widen", stage_rounds))
    if line["work"] != line["steps"] + NEIGHBORHOOD_WORK * line["neighborhoods"]:
        bad.append((n, "work is not steps + 32 per neighborhood", line["work"]))
    for imp in line["improvements"]:
        if not 0 <= imp["trajectory"] < len(trajectories) or not 0 <= imp["stage"] <= 2:
            bad.append((n, "improvement", imp))
        if widen is None and imp["stage"] != 0:
            bad.append((n, "improvement beyond stage 0 without widen", imp))
        if imp["round"] == 0 and (imp["work"] != 0 or imp["trajectory"] == 0):
            bad.append((n, "improvement of round 0", imp))
    scores = [line["start"]] + [imp["score"] for imp in line["improvements"]]
    if scores != sorted(set(scores)) or scores[-1] != line["score"]:
        bad.append((n, "scores do not rise to the line's", scores))
    reach = line["stop_at_known"]["round"]
    last = line["improvements"][-1] if line["improvements"] else None
    if reach is not None:
        if line["score"] != line["stop_at_known"]["known"]:
            bad.append((n, "reached, but the score is not the known one", line["score"]))
        if last is None and (line["start"] != line["stop_at_known"]["known"] or line["rounds"] != 0):
            bad.append((n, "reached at the start, but the start is short or rounds were run", line["rounds"]))
        if last is not None and (last["round"] != reach or last["work"] != line["work"]
                                 or last["steps"] != line["steps"] or last["neighborhoods"] != line["neighborhoods"]
                                 or last["score"] != line["score"] or line["rounds"] != max(reach, 0)):
            bad.append((n, "the reaching improvement is not the line's end", last))
    elif line["work"] < line["budget"] or line["score"] >= line["stop_at_known"]["known"]:
        bad.append((n, "not reached, but the run did not use its budget", line["work"]))
    return bad


def check_against_e3a(games, a_lines, e3a_a):
    """Arm A on this build against the lines of E3a's arm A (the default; fa05cac): the improvements agree as far as
    both lines' rounds go.  Returns the number of games that differ."""
    differ, compared = [], 0
    for n in games:
        if n not in a_lines or n not in e3a_a:
            continue
        new, old = a_lines[n], e3a_a[n]
        limit = min(new["rounds"], old["rounds"])
        new_i = [(i["round"], i["score"]) for i in new["improvements"] if i["round"] <= limit]
        old_i = [(i["round"], i["score"]) for i in old["improvements"] if i["round"] <= limit]
        compared += 1
        if new_i != old_i or new["start"] != old["start"]:
            differ.append(n)
    print(f"  arm A against E3a's arm A (build fa05cac; the improvements as far as both lines' rounds go): {compared} "
          f"games compared, {len(differ)} differ: {differ} (want none)")
    return len(differ)


# ---------------------------------------------------------------------------------------------------------------------
# Part 1 and Part 2: the race


def label(rec, index=None):
    """A short name of where an improvement came from: S the start's trajectory, or the offset back to the game whose
    survivors it began from (-8 for n - 8)."""
    origin_of = rec["trajectories"][rec["by"] if index is None else index]
    return "S" if origin_of == "start" else f"-{rec['n'] - origin_of}"


def per_game(games, recs, arms):
    """Section 1: one row a game; the reaching work, seconds and round, the trajectory and stage; the misses."""
    print("\n== 1. Per game ==")
    print("  short0 = the known score less the start's, in points (the same in every arm).  An arm's cell is "
          "round/work/seconds at which it held the known score and the trajectory (S: the start's; -j: began from the "
          "survivors of n - j) and stage that made it, or 'no' and the final shortfall and the round of its last "
          "improvement")
    print(f"  {'n':>5} {'short0':>6} | " + " | ".join(f"{arm:^22}" for arm in arms))
    for n in games:
        cells = []
        for arm in arms:
            rec = recs[arm].get(n)
            if rec is None:
                cells.append("(not run)")
            elif reached(rec):
                cells.append(f"r{rec['reach']} {rec['work']}w {rec['t_reach']:.0f}s {label(rec)}/{rec['stage']}"
                             if rec["improvements"] else "at the start")
            else:
                last = max((i["round"] for i in rec["improvements"]), default=0)
                cells.append(f"no -{rec['short']} last r{last}")
        first = next((recs[arm][n] for arm in arms if n in recs[arm]), None)
        print(f"  {n:>5} {first['start_short'] if first else '?':>6} | " + " | ".join(f"{c:^22}" for c in cells))
    hard = [n for n in games if any(n in recs[arm] and recs[arm][n]["start_short"] > 0 for arm in arms)]
    print(f"\n  Of the {len(games)} games, {len(games) - len(hard)} hold the known score at the start and {len(hard)} "
          "are short at the start.")
    for arm in arms:
        done = [n for n in games if n in recs[arm]]
        got = [n for n in done if reached(recs[arm][n])]
        got_hard = [n for n in got if n in hard]
        print(f"  arm {arm}: {len(done)} games run; reached {len(got)} ({pct(len(got), len(games))}), "
              f"{len(got_hard)} of the {len(hard)} short at the start")
        missed = [recs[arm][n] for n in done if not reached(recs[arm][n])]
        if missed:
            print(f"    missed {[r['n'] for r in missed]}; final shortfalls {[r['short'] for r in missed]}; "
                  f"seconds of the runs {[round(r['seconds']) for r in missed]}")
    print("\n  The improvements of each game short at the start, per arm, as round:trajectory+stage (S: the start's, "
          "-j: the survivors of n - j):")
    for n in hard:
        parts = []
        for arm in arms:
            rec = recs[arm].get(n)
            if rec is not None:
                parts.append(f"{arm}[" + " ".join(f"{i['round']}:{label(rec, i['trajectory'])}/{i['stage']}"
                                                  for i in rec["improvements"]) + "]")
        print(f"    {n}: " + " ".join(parts))
    return hard


def winner_key(arm_recs, games):
    """The Part 2 rule's ranking: the most games at the known score within WINNER_BUDGET work, ties broken by the work
    summed over the games to reach it (a game not reached counts as the budget)."""
    count = sum(1 for n in games if n in arm_recs and reached(arm_recs[n], WINNER_BUDGET))
    spent = sum(arm_recs[n]["work"] if reached(arm_recs[n]) else BUDGET for n in games if n in arm_recs)
    return -count, spent


def race(games, recs, arms, hard):
    """Section 2: the share at the known score at equal work and at equal wall time; the winner."""
    total = len(games)
    print(f"\n== 2. The race at equal work: games of {total} at the known score within W work (the start's work is 0; "
          "every non-reached run used its whole budget, so every cell is exact unless marked +) ==")
    print(f"  {'':>8} | " + " | ".join(f"{w:>10,}".rjust(12) for w in WORK_BUDGETS) + f" | {'in the run':>12}")
    for arm in arms:
        cells = [cell(*share_within(recs[arm], games, w, "work"), total) for w in WORK_BUDGETS]
        run = sum(1 for n in games if n in recs[arm] and reached(recs[arm][n]))
        print(f"  {arm:>8} | " + " | ".join(f"{c:>12}" for c in cells) + f" | {run:>12}")
    print(f"\n  The same for the {len(hard)} games short at the start:")
    for arm in arms:
        cells = [cell(*share_within(recs[arm], hard, w, "work"), len(hard)) for w in WORK_BUDGETS]
        print(f"  {arm:>8} | " + " | ".join(f"{c:>12}" for c in cells))
    print(f"\n== 2b. The race at equal wall time: games of {total} at the known score within T seconds on {THREADS} "
          "threads (the start's time counted); '+' marks a lower bound (a game not reached ended its run before T, or "
          "was not run) ==")
    print(f"  {'':>8} | " + " | ".join(f"{t:>3} s".rjust(12) for t in TIMES))
    for arm in arms:
        cells = [cell(*share_within(recs[arm], games, t, "seconds"), total) for t in TIMES]
        print(f"  {arm:>8} | " + " | ".join(f"{c:>12}" for c in cells))
    print("  the seconds the runs of the games each arm did not reach took:")
    for arm in arms:
        ends = sorted(round(r["seconds"]) for r in recs[arm].values() if not reached(r))
        print(f"    arm {arm}: {ends}")
    print(f"\n  The ranking of the Part 2 rule (the most games within {WINNER_BUDGET:,} work, then the least work "
          f"summed, a game not reached counting as the budget {BUDGET:,}):")
    ranked = sorted(arms, key=lambda arm: winner_key(recs[arm], games))
    for arm in ranked:
        count, spent = winner_key(recs[arm], games)
        print(f"    {arm:>6}: {-count} games, work summed {spent:,}; games run {len(recs[arm])} of {total}")
    return ranked


def versus_default(games, recs, arms):
    """The games each arm gains or loses against the default at several budgets of work."""
    print("\n== 2c. Each arm against the default, game by game: gained / lost (games it holds within W work that the "
          "default does not / the reverse) ==")
    print(f"  {'':>8} | " + " | ".join(f"{w:>10,}".rjust(12) for w in WORK_BUDGETS))
    for arm in arms:
        if arm == "A":
            continue
        cells, tests = [], []
        for w in WORK_BUDGETS:
            gained = sum(1 for n in games if n in recs[arm] and reached(recs[arm][n], w)
                         and not reached(recs["A"][n], w))
            lost = sum(1 for n in games if n in recs[arm] and not reached(recs[arm][n], w)
                       and reached(recs["A"][n], w))
            cells.append(f"+{gained} / -{lost}")
            tests.append(sign_test(gained, lost))
        print(f"  {arm:>8} | " + " | ".join(f"{c:>12}" for c in cells))
        print(f"  {'p':>8} | " + " | ".join(
            "           -" if p is None else "     <0.0001" if p < 0.0001 else f"{p:>12.4f}" for p in tests))
    print("  p = the two-sided sign test (exact binomial) of the gained against the lost games")


def sign_test(gained, lost):
    """The two-sided p of the sign test: the chance of a split at least as uneven as gained / lost if each game that
    one of the two arms holds and the other does not were equally likely to be either's; None if there are none."""
    total = gained + lost
    if total == 0:
        return None
    tail = sum(math.comb(total, k) for k in range(min(gained, lost) + 1)) / 2 ** total
    return min(1.0, 2 * tail)


def stuck(games, recs, arms):
    """The games each arm did not reach: the start's shortfall, the final shortfall, the rounds, the last improvement,
    and where the default stands."""
    print("\n== 3b. The games each arm did not reach ==")
    print("  short0 / final = the known score less the start's / the final score, in points; last = the round, "
          "trajectory (S: the start's; -j: the survivors of n - j) and stage of the last improvement; the default's "
          "result, round and work, or its final shortfall")
    for arm in arms:
        for n in games:
            rec = recs[arm].get(n)
            if rec is None or reached(rec):
                continue
            last = rec["improvements"][-1] if rec["improvements"] else None
            where = (f"round {last['round']}, {label(rec, last['trajectory'])}, stage {last['stage']}" if last
                     else "none")
            default = recs["A"].get(n) if "A" in recs else None
            by_default = ("" if default is None or arm == "A" else
                          f"; the default: r{default['reach']}, {default['work']} work" if reached(default)
                          else f"; the default: short {default['short']}")
            print(f"  arm {arm:>5} {n}: short0 {rec['start_short']}, final {rec['short']}, rounds {rec['rounds']}, "
                  f"work {rec['work']}, last improvement: {where}, trajectories {len(rec['trajectories'])}, "
                  f"rounds at stages 0/1/2 {[sum(s[k] for s in rec['stage_rounds']) for k in range(3)]}{by_default}")


def who_reaches(games, recs, arms, misses, name):
    """Section 3: which arm reaches which of the games the default (or P1's seed 1) missed; what an arm loses."""
    print(f"\n== 3. Which arm reaches which of {name} ==")
    print(f"  {'n':>5} {'short0':>6} | " + " | ".join(f"{arm:^24}" for arm in arms))
    for n in misses:
        cells = []
        for arm in arms:
            r = recs[arm].get(n)
            if r is None:
                cells.append("(not run)")
            elif reached(r):
                cells.append(f"r{r['reach']} {r['work']}w {r['t_reach']:.0f}s {label(r)}/{r['stage']}")
            else:
                last = max((i["round"] for i in r["improvements"]), default=0)
                cells.append(f"no -{r['short']} last r{last}")
        print(f"  {n:>5} {recs['A'][n]['start_short']:>6} | " + " | ".join(f"{c:^24}" for c in cells))
    for arm in arms:
        got = [n for n in misses if n in recs[arm] and reached(recs[arm][n])]
        print(f"  arm {arm} reaches {len(got)} of the {len(misses)}: {got}")
    by_a = [n for n in games if reached(recs["A"][n])]
    print("\n  Games the default reaches that another arm does not (within its run):")
    for arm in arms:
        if arm != "A":
            lost = [n for n in by_a if n in recs[arm] and not reached(recs[arm][n])]
            print(f"    arm {arm} loses {len(lost)}: {lost}")
    print("  Games another arm reaches that the default does not:")
    for arm in arms:
        if arm != "A":
            gained = [n for n in games if n in recs[arm] and reached(recs[arm][n]) and not reached(recs["A"][n])]
            print(f"    arm {arm} gains {len(gained)}: {gained}")
    print("  Games no arm reaches:", [n for n in games if all(n in recs[a] and not reached(recs[a][n]) for a in arms)])
    print("\n  The work to the known score on the games short at the start that the default and the arm both reach "
          "(median of the arm's work over the default's, and of the seconds; games where the arm needs less work):")
    for arm in arms:
        if arm == "A":
            continue
        both = [n for n in games if n in recs[arm] and reached(recs[arm][n]) and reached(recs["A"][n])
                and recs["A"][n]["start_short"] > 0]
        if both:
            rw = [recs[arm][n]["work"] / recs["A"][n]["work"] for n in both if recs["A"][n]["work"]]
            rt = [recs[arm][n]["t_reach"] / recs["A"][n]["t_reach"] for n in both]
            print(f"    {arm}: {len(both)} games; work ratio median {median(rw):.2f} "
                  f"({sum(1 for x in rw if x < 1)} less); seconds ratio median {median(rt):.2f} "
                  f"({sum(1 for x in rt if x < 1)} less)")


# ---------------------------------------------------------------------------------------------------------------------
# Part 1: cost, trajectories


def used(rec):
    """The seconds, work, steps and neighborhoods of a line's rounds (to the known score if it reached it)."""
    end = rec["t_reach"] if reached(rec) else rec["seconds"]
    return end - rec["start_seconds"], rec["work"], rec["steps"], rec["neighborhoods"]


def measurable(rec):
    """Whether a line's cost can be measured: its rounds took long enough for the fixed cost of a line (about 0.1 s) to
    weigh little, and the prover was running beside it, as it was beside every line of Part 1."""
    return rec["rounds"] >= 1 and used(rec)[0] >= MIN_ROUND_TIME and not rec.get("unloaded")


def costs(games, recs, arms):
    """Section 4: seconds per work and per step, steps per neighborhood, by arm and stretch of n."""
    print("\n== 4. Cost: seconds per 10^6 work, ms per step, steps per neighborhood, by arm and stretch of n ==")
    print(f"  Over the lines whose rounds took at least {MIN_ROUND_TIME:.0f} s.  Seconds are the rounds' wall time on "
          f"{THREADS} threads at nice 19, the prover at idle priority on the same cores.  med (min-max).")
    print(f"  {'arm':>6} {'band':>11} {'lines':>5} | {'s/10^6 work':>22} | {'ms/step':>20} | {'steps/nb':>20}")
    for arm in arms:
        for band in BANDS + [BAND_ALL]:
            spw, sps, spn = [], [], []
            for n in games:
                r = recs[arm].get(n)
                if r is None or not band[0] <= n <= band[1] or not measurable(r):
                    continue
                seconds, work, steps, nbs = used(r)
                spw.append(1e6 * seconds / work)
                sps.append(1000 * seconds / steps)
                spn.append(steps / nbs)
            if not spw:
                print(f"  {arm:>6} {band[0]:>5}-{band[1]:<5} {0:>5} | (no line with rounds of that length)")
                continue

            def span(values, digits):
                return f"{median(values):.{digits}f} ({min(values):.{digits}f}-{max(values):.{digits}f})"

            print(f"  {arm:>6} {band[0]:>5}-{band[1]:<5} {len(spw):>5} | {span(spw, 2):>22} | {span(sps, 3):>20} | "
                  f"{span(spn, 0):>20}")
    print("\n  The cost of the arm against the default's, game by game, over the games whose rounds are long enough "
          "in both (median, min-max): seconds per work, seconds per step and steps per neighborhood as ratios:")
    for arm in arms:
        if arm == "A" or "A" not in recs:
            continue
        both = [n for n in games if n in recs[arm] and measurable(recs[arm][n]) and measurable(recs["A"][n])]
        if not both:
            continue
        ratios = {"s/work": [], "s/step": [], "steps/nb": []}
        for n in both:
            (sa, wa, ta, na), (sb, wb, tb, nb) = used(recs["A"][n]), used(recs[arm][n])
            ratios["s/work"].append((sb / wb) / (sa / wa))
            ratios["s/step"].append((sb / tb) / (sa / ta))
            ratios["steps/nb"].append((tb / nb) / (ta / na))
        print(f"    {arm:>6}: {len(both):>2} games; " + "; ".join(
            f"{k} x{median(v):.2f} ({min(v):.2f}-{max(v):.2f})" for k, v in ratios.items()))
    print("\n  Total seconds of the lines (the games' whole runs):")
    for arm in arms:
        own = [recs[arm][n] for n in games if n in recs[arm]]
        total = sum(r["seconds"] for r in own)
        missed = sum(r["seconds"] for r in own if not reached(r))
        print(f"    arm {arm}: {total:.0f} s over {len(own)} lines ({total / 3600:.2f} h of {THREADS} threads), "
              f"{missed:.0f} s in the {sum(1 for r in own if not reached(r))} games it missed; the start takes a "
              f"median {median([r['start_seconds'] for r in own]):.1f} s")


def trajectories(games, recs, arms):
    """The trajectories a game had, and the share of the rounds at each stage of --widen."""
    print("\n== 4b. Trajectories and stages ==")
    for arm in arms:
        back = OPTIONS[arm][1]
        widen = OPTIONS[arm][2]
        own = [recs[arm][n] for n in games if n in recs[arm]]
        if back:
            counts = [len(r["trajectories"]) for r in own]
            print(f"  arm {arm}: trajectories a game: mean {statistics.mean(counts):.2f}, median {median(counts)}, "
                  f"range {min(counts)}-{max(counts)}; games by count: "
                  f"{ {c: counts.count(c) for c in sorted(set(counts))} }")
        if widen:
            totals = [0, 0, 0]
            for r in own:
                for stages in r["stage_rounds"]:
                    for s in range(3):
                        totals[s] += stages[s]
            whole = sum(totals)
            print(f"  arm {arm}: the rounds of all trajectories at stages 0/1/2 (0.7,0.9 / 0.5,0.7 / 0.4,0.6): "
                  f"{totals} of {whole}: " + " / ".join(pct(t, whole) for t in totals)
                  + f"; games with a trajectory at stage 1 or 2 at the end: "
                  f"{sum(1 for r in own if any(s[1] or s[2] for s in r['stage_rounds']))} of {len(own)}")
            hard_own = [r for r in own if not reached(r)]
            missed_totals = [sum(s[k] for r in hard_own for s in r["stage_rounds"]) for k in range(3)]
            if hard_own:
                print(f"    in the {len(hard_own)} games not reached: {missed_totals} of {sum(missed_totals)}: "
                      + " / ".join(pct(t, sum(missed_totals)) for t in missed_totals))
        improvement_stages = [0, 0, 0]
        improvement_trajectories = {}
        for r in own:
            for imp in r["improvements"]:
                improvement_stages[imp["stage"]] += 1
                key = label(r, imp["trajectory"])
                improvement_trajectories[key] = improvement_trajectories.get(key, 0) + 1
        print(f"  arm {arm}: improvements by stage {improvement_stages}; by trajectory (S: the start's, -j: the "
              f"survivors of n - j): {dict(sorted(improvement_trajectories.items()))}")


def from_the_games_before(games, recs, arms):
    """Section 5: how often the trajectory that reached the known score began from n - j."""
    print("\n== 5. The trajectories from the games before ==")
    for arm in arms:
        if not OPTIONS[arm][1]:
            continue
        own = [recs[arm][n] for n in games if n in recs[arm]]
        short = [r for r in own if r["start_short"] > 0]
        got = [r for r in short if reached(r)]
        by_j = {}
        for r in got:
            by_j.setdefault(label(r), []).append(r["n"])
        existed = {}
        for r in short:
            for m in r["trajectories"][1:]:
                existed[r["n"] - m] = existed.get(r["n"] - m, 0) + 1
        at_round_0 = [r["n"] for r in got if r["reach"] == 0]
        print(f"  arm {arm}: of the {len(short)} games short at the start, {len(got)} were reached; the reaching "
              f"improvement came from the trajectory (S: the start's; -j: began from the survivors of n - j): "
              + "; ".join(f"{k}: {len(v)}" for k, v in sorted(by_j.items())))
        print("    games short at the start that had a trajectory from n - j (distinct from the others), by j: "
              + ", ".join(f"{j}: {existed.get(j, 0)}" for j in range(1, OPTIONS[arm][1] + 1)) + f" of {len(short)}")
        print(f"    reached before any round (an improvement of round 0 held the known score): {at_round_0}")
        round0 = [r["n"] for r in short if r["improvements"] and r["improvements"][0]["round"] == 0]
        print(f"    games short at the start whose first improvement is of round 0 (a trajectory from a game before "
              f"started heavier): {len(round0)} {round0}")
        if 4232 in recs[arm]:
            r = recs[arm][4232]
            end = f"reached at round {r['reach']}, work {r['work']}" if reached(r) else "not reached"
            steps = [(i["round"], label(r, i["trajectory"]), i["stage"], i["score"]) for i in r["improvements"]]
            print(f"    4232: trajectories {r['trajectories']}; improvements (round, trajectory, stage, score) "
                  f"{steps}; {end}")


# ---------------------------------------------------------------------------------------------------------------------
# The effort levels


def rates(recs, games):
    """The median seconds per work of an arm's measurable lines in each stretch of n (and of all), for the time of a
    full run of a budget."""
    out = {}
    for band in BANDS + [BAND_ALL]:
        values = [1e6 * used(r)[0] / used(r)[1] for n, r in recs.items() if band[0] <= n <= band[1] and measurable(r)
                  and used(r)[1]]
        out[band] = median(values)
    overall = out[BAND_ALL]
    return {band: overall if value is None else value for band, value in out.items()}


def time_to_known(rec, budget):
    """The wall time of a run at a budget of work that ends at the known score: the time to it, or the time the run
    takes to spend the budget (interpolated linearly in work between the start and the line's end)."""
    if reached(rec, budget):
        return rec["t_reach"]
    seconds, work, _, _ = used(rec)
    return rec["start_seconds"] + seconds * min(1.0, budget / work) if work else rec["start_seconds"]


def time_full(rec, budget, rate):
    """The wall time of a run of the whole budget: the start and the stretch's median rate of seconds per work."""
    return rec["start_seconds"] + rate[band_of(rec["n"])] * budget / 1e6


def levels(recs, games, name):
    """The share at the known score at each level of effort, and the median and 90th percentile time of a game."""
    rate = rates(recs, games)
    print(f"\n== 6. The levels of effort: {name} ({len(games)} games) ==")
    print("  share = games at the known score within the level's budget of work (a lower bound by up to one round's "
          "work: the round that crosses the budget also runs).  'stop' time = the wall time of a run that ends at the "
          "known score (what the lines measure); 'full' time = the start's seconds plus the stretch's median seconds "
          "per work times the budget (a run with no known score spends the whole budget).")
    print(f"  {'effort':>6} {'budget':>10} | {'at the known score':>20} | {'stop median':>11} {'p90':>7} | "
          f"{'full median':>11} {'p90':>7}")
    for effort, budget in LEVELS:
        got = sum(1 for n in games if n in recs and reached(recs[n], budget))
        stop = [time_to_known(recs[n], budget) for n in games if n in recs]
        full = [time_full(recs[n], budget, rate) for n in games if n in recs]
        print(f"  {effort:>6} {budget:>10,} | {cell(got, True, len(games)):>20} | {median(stop):>11.1f} "
              f"{percentile(stop, 0.9):>7.1f} | {median(full):>11.1f} {percentile(full, 0.9):>7.1f}")
    print(f"  rates (seconds per 10^6 work) by stretch: "
          + ", ".join(f"{b[0]}-{b[1]}: {fmt(v, 2)}" for b, v in rate.items()))
    return rate


def levels_summary(recs_by_arm, games, arms, name):
    """The share at each level of effort, and the median and 90th percentile time of a full run, one column an arm."""
    print(f"\n== 6b. The levels of effort, all arms: {name} ({len(games)} games) ==")
    print(f"  Games at the known score within the budget of work of each effort level:")
    print(f"  {'effort':>6} {'budget':>10} | " + " | ".join(f"{arm:>12}" for arm in arms))
    for effort, budget in LEVELS:
        cells = [cell(sum(1 for n in games if n in recs_by_arm[arm] and reached(recs_by_arm[arm][n], budget)), True,
                      len(games)) for arm in arms]
        print(f"  {effort:>6} {budget:>10,} | " + " | ".join(f"{c:>12}" for c in cells))
    rate = {arm: rates(recs_by_arm[arm], games) for arm in arms}
    for kind, fn in (("full run (the start and the stretch's median seconds per work times the budget)",
                      lambda arm, rec, budget: time_full(rec, budget, rate[arm])),
                     ("run that stops at the known score", lambda arm, rec, budget: time_to_known(rec, budget))):
        print(f"\n  Median / 90th percentile seconds of a game, {kind}:")
        print(f"  {'effort':>6} {'budget':>10} | " + " | ".join(f"{arm:>12}" for arm in arms))
        for effort, budget in LEVELS:
            cells = []
            for arm in arms:
                times = [fn(arm, recs_by_arm[arm][n], budget) for n in games if n in recs_by_arm[arm]]
                cells.append(f"{median(times):.0f} / {percentile(times, 0.9):.0f}")
            print(f"  {effort:>6} {budget:>10,} | " + " | ".join(f"{c:>12}" for c in cells))


def estimate(recs, games, p1_module, name):
    """The share of the 568 searched games of 3441-5060 held at each level of effort, by P1's rule: the games whose
    start held the best score in the run of 2026-11-01 are taken as holding it, and the share of the hard games run
    stands for the others ((317 + 251 x the share) / 568), with the exact interval of the share carried through unless
    all 251 hard games were run."""
    print(f"\n== 7. Estimate for the {SEARCHED} searched games of 3441-5060 ({name}; P1's rule: "
          f"({SEARCHED_WITH_START_OPTIMAL} + {HARD} x the share of the hard games) / {SEARCHED}) ==")
    print(f"  {'effort':>6} {'budget':>10} | {'hard games':>16} | {'568 games':>10} {'90% interval':>14}")
    for effort, budget in LEVELS:
        got = sum(1 for n in games if n in recs and reached(recs[n], budget))
        low, high = p1_module.clopper_pearson(got, len(games))
        est = lambda s: 100 * (SEARCHED_WITH_START_OPTIMAL + HARD * s) / SEARCHED
        span = "(all hard games run)" if len(games) == HARD else f"{est(low):>7.1f}-{est(high):.1f}%"
        print(f"  {effort:>6} {budget:>10,} | {cell(got, True, len(games)):>16} | "
              f"{est(got / len(games)):>9.1f}% {span}")


# ---------------------------------------------------------------------------------------------------------------------
# The chart


def curve(arm_recs, games):
    """The step function of the chart: the work at which each game was reached."""
    return sorted(arm_recs[n]["work"] for n in games if n in arm_recs and reached(arm_recs[n]))


def chart(games, recs, arms, ranked, path):
    """The chart: the share of the games at the known score against the work, a log axis, one line an arm.  The best
    three arms of the ranking and the default are labeled at the right; the legend names all."""
    width, height, left, right, top, bottom = 900, 620, 64, 190, 172, 56
    plot_w, plot_h = width - left - right, height - top - bottom
    total = len(games)
    y_min, y_max = 0.3, 1.0

    def px(work):
        span = math.log10(X_MAX) - math.log10(X_MIN)
        return left + plot_w * (math.log10(max(work, X_MIN)) - math.log10(X_MIN)) / span

    def py(share):
        return top + plot_h * (1 - (share - y_min) / (y_max - y_min))

    ink, muted, grid = "#1f2328", "#59636e", "#d1d9e0"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, '
           f'sans-serif" role="img" aria-labelledby="title desc">',
           '<title id="title">Race E3b: the 63 hard games at the known score against the work</title>',
           '<desc id="desc">The share of the 63 games at the known score within W work, one line an arm; the table '
           'of the entry gives the numbers.</desc>',
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
           f'<clipPath id="plot"><rect x="{left}" y="{top - 4}" width="{plot_w}" height="{plot_h + 8}"/></clipPath>',
           f'<text x="{left}" y="26" font-size="16" font-weight="600" fill="{ink}">Race E3b: the 63 hard games at the '
           f'known score against the work</text>',
           f'<text x="{left}" y="46" font-size="12" fill="{muted}">Share of the 63 games at the known score within W '
           f'work (steps and 32 for each neighborhood), seeded from the proven game of n - 1; the axis starts at '
           f'30%.</text>',
           f'<text x="{left}" y="62" font-size="12" fill="{muted}">Effort 7 is a budget of 4,194,304 work; each '
           f'effort level below it is half the work of the next.  One seed, 4 threads.</text>']
    for work, text in ((1_000, "1k"), (10_000, "10k"), (30_000, "30k"), (100_000, "100k"), (300_000, "300k"),
                       (1_000_000, "1M"), (4_000_000, "4M")):
        x = px(work)
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + plot_h}" stroke="{grid}"/>')
        out.append(f'<text x="{x:.1f}" y="{top + plot_h + 18}" font-size="12" fill="{muted}" text-anchor="middle">'
                   f'{text}</text>')
    for share in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        y = py(share)
        out.append(f'<line x1="{left}" x2="{left + plot_w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{grid}"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" font-size="12" fill="{muted}" text-anchor="end">'
                   f'{round(100 * share)}%</text>')
    out.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 14}" font-size="12" fill="{muted}" '
               f'text-anchor="middle">work (log axis)</text>')
    ends = {}
    for arm in arms:
        works = curve(recs[arm], games)
        points = [(X_MIN, sum(1 for w in works if w <= X_MIN))]
        for i, w in enumerate(works):
            if w > X_MIN:
                points += [(w, points[-1][1]), (w, i + 1)]
        points.append((X_MAX, len(works)))
        path_d = " ".join(f"{px(w):.1f},{py(c / total):.1f}" for w, c in points)
        dash = f' stroke-dasharray="{DASH[arm]}"' if DASH[arm] else ""
        out.append(f'<polyline points="{path_d}" fill="none" stroke="{COLOR[arm]}" stroke-width="2.5"{dash} '
                   f'stroke-linecap="round" stroke-linejoin="round" clip-path="url(#plot)"/>')
        ends[arm] = len(works)
    labeled = [arm for arm in dict.fromkeys(ranked[:3] + ["A"]) if arm in ends]
    wanted = sorted((py(ends[arm] / total), arm) for arm in labeled)
    placed, previous = {}, -1e9
    for y, arm in wanted:
        y = max(y, previous + 17)
        placed[arm] = y
        previous = y
    for arm in labeled:
        x = left + plot_w + 10
        out.append(f'<line x1="{left + plot_w:.1f}" x2="{x - 3:.1f}" y1="{py(ends[arm] / total):.1f}" '
                   f'y2="{placed[arm]:.1f}" stroke="{COLOR[arm]}" stroke-width="1"/>')
        out.append(f'<text x="{x:.1f}" y="{placed[arm] + 4:.1f}" font-size="12" fill="{ink}">{arm}: {ends[arm]}</text>')
    for i, arm in enumerate(arms):  # the legend, two arms a row
        x, y = left + (i % 2) * 330, 86 + (i // 2) * 18
        dash = f' stroke-dasharray="{DASH[arm]}"' if DASH[arm] else ""
        out.append(f'<line x1="{x}" x2="{x + 30}" y1="{y}" y2="{y}" stroke="{COLOR[arm]}" stroke-width="2.5"{dash} '
                   f'stroke-linecap="round"/>')
        out.append(f'<text x="{x + 38}" y="{y + 4}" font-size="12" fill="{ink}">{arm}: {FLAGS[arm]}</text>')
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"\n  chart written: {path} (games at the known score at the end of each line: {ends}; labeled {labeled})")


# ---------------------------------------------------------------------------------------------------------------------


def load_module(path):
    """A module of another entry, by its path (P1's analyze.py, for its interval)."""
    sys.dont_write_bytecode = True  # leave no __pycache__ in the other entry's folder
    spec = importlib.util.spec_from_file_location("p1_analyze", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    directory = sys.argv[1] if len(sys.argv) > 1 else here
    p1_directory = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", P1_ENTRY)
    e3a_directory = sys.argv[3] if len(sys.argv) > 3 else os.path.join(here, "..", E3A_ENTRY)
    p1_module = load_module(os.path.join(p1_directory, "analyze.py"))
    games = read_games(os.path.join(directory, "games.txt"))
    p1 = read_lines(os.path.join(p1_directory, "seed-1.jsonl"))
    e3a_a = read_lines(os.path.join(e3a_directory, "arm-a.jsonl"))
    e3a_a = {n: e3a_a.get(n, p1[n]) for n in games}  # E3a's arm A: its 7 long lines, else P1's seed-1 lines
    lines = {arm: read_lines(os.path.join(directory, f"arm-{arm.lower()}.jsonl")) for arm in ARMS}
    lines = {arm: arm_lines for arm, arm_lines in lines.items() if arm_lines}
    arms = [arm for arm in ARMS if arm in lines]
    runs(directory)
    print(f"\nPart 1: {len(games)} games, n {games[0]} to {games[-1]}; arms {arms}")
    p1_misses = sorted(n for n, line in p1.items() if line["stop_at_known"]["round"] is None)
    print(f"  P1's seed 1 missed {len(p1_misses)} games: {p1_misses}")
    failures = check_lines(games, lines, p1, e3a_a, "Part 1")
    recs = records(lines)
    starts = game_starts(directory)
    annotate(recs, "part1", starts)
    hard = per_game(games, recs, arms)
    ranked = race(games, recs, arms, hard)
    if "A" in recs:
        versus_default(games, recs, arms)
        who_reaches(games, recs, arms, p1_misses, "P1's seed-1 misses")
        stuck(games, recs, arms)
    costs(games, recs, arms)
    trajectories(games, recs, arms)
    from_the_games_before(games, recs, arms)
    chart(games, recs, arms, [a for a in ranked if a in arms], os.path.join(directory, "race.svg"))
    for arm in arms:
        levels(recs[arm], games, f"arm {arm}, Part 1")
    levels_summary(recs, games, arms, "Part 1")
    for arm in arms:
        estimate(recs[arm], games, p1_module, f"arm {arm}, the 63 games of Part 1")
    winner = ranked[0]
    print(f"\nPart 1 winner by the rule: {winner}")

    # Part 2
    games2_path = os.path.join(directory, "games-part2.txt")
    if os.path.exists(games2_path):
        games2 = read_games(games2_path)
        lines2 = {arm: {} for arm in ("A", winner)}
        for arm, arm_lines in lines2.items():  # the default's lines are in several files: the first run's, then -tail*
            prefix = os.path.join(directory, f"part2-{arm.lower()}")
            for part in [prefix + ".jsonl"] + sorted(glob.glob(prefix + "-tail*.jsonl")):
                arm_lines.update(read_lines(part))
        lines2 = {arm: arm_lines for arm, arm_lines in lines2.items() if arm_lines}
        if lines2:
            arms2 = [arm for arm in ARMS if arm in lines2]
            run_by_all = [n for n in games2 if all(n in arm_lines for arm_lines in lines2.values())]
            if len(run_by_all) != len(games2):
                failures += 1
                print(f"\n  FAIL: Part 2 is incomplete: {len(run_by_all)} of {len(games2)} games are in every arm's "
                      "file; the others are left out below")
                games2 = run_by_all
            print(f"\n\n######## Part 2: {len(games2)} games, n {games2[0]} to {games2[-1]}; arms {arms2}")
            failures += check_lines(games2, lines2, p1, e3a_a, "Part 2")
            recs2 = records(lines2)
            annotate(recs2, "part2", starts)
            hard2 = per_game(games2, recs2, arms2)
            race(games2, recs2, arms2, hard2)
            if "A" in recs2 and len(arms2) > 1:
                versus_default(games2, recs2, arms2)
                misses2 = [n for n in games2 if n in recs2["A"] and not reached(recs2["A"][n])]
                who_reaches(games2, recs2, arms2, misses2, "the games the default missed (Part 2)")
                stuck(games2, recs2, [arm for arm in arms2 if arm != "A"])
            costs(games2, recs2, arms2)
            trajectories(games2, recs2, arms2)
            from_the_games_before(games2, recs2, arms2)
            levels_summary(recs2, games2, arms2, "Part 2")
            pooled_games = games + [n for n in games2 if all(n in recs2[arm] for arm in arms2)]
            pooled ={arm: {**recs[arm], **recs2[arm]} for arm in arms2}
            for arm in arms2:
                levels(pooled[arm], pooled_games, f"arm {arm}, Parts 1 and 2 together")
                estimate(pooled[arm], pooled_games, p1_module, f"arm {arm}, Parts 1 and 2 together")
            levels_summary(pooled, pooled_games, arms2, "Parts 1 and 2 together")
    print(f"\nchecks failed: {failures}")


if __name__ == "__main__":
    main()
