#!/usr/bin/env python3
"""The push-down below each gain (2026-11): the mini-pass's two arms and the follower's rounds, recomputed.

    nice -n 19 python3 -I analysis.py > out.txt

It reads the lines and logs of the arms and the follower (t/, c/, pd/) and their lists of windows in this folder, and
from the production folder RUN the best-known file (whose records say which file raised each game, `best_known.file`,
and from which score, `best_known.was`) and pass 1's and pass 2's files and logs.  It also writes records.tsv, the
records of the arms' and the follower's files, which is all this entry needs of the best-known file.

A game is *raised* by a set of files when the best-known file has a record of it from one of them; its points are the
score of the last such record less the `was` of the first.  A *streak* is a run of consecutive raised games.  A
thread-hour is a game's seconds times the run's threads, in hours.
"""

import gzip
import json
import re
from collections import Counter, defaultdict, namedtuple
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = Path("/home/brian/taxman_work/lab/work/unsound-run")
PASS1 = ("a-l3.jsonl", "a2-l3.jsonl", "b-l4.jsonl")
PASS2 = ("p2-l3s2.jsonl", "u-l3s2.jsonl")
PASS2_CARRY = "p2-carry.jsonl"
PASS2_LOGS = ("p2-l3s2.log", "p2-l3s2.2.log", "p2-l3s2.3.log", "p2-l3s2.4.log", "u-l3s2.log")
THREADS = {"t": 20, "c": 20, "pd": 8}
BUILD = "f7b134c"  # the commit of the binary of both runs
WINDOW = 8
GAME_LOG = re.compile(r"^n=(\d+) .* ([0-9.]+) s ")
REPAIR_LOG = re.compile(r"^repaired \d+ lines; the repair took ([0-9.]+) s")
ROUND_LOG = re.compile(r"^round (\d+) (\d\d:\d\d:\d\d): (.*)$")

Record = namedtuple("Record", "position n score was file method source began")
Play = namedtuple("Play", "windows games seconds log_seconds repair_seconds work above_bound off_window other_options")


def line_source(d):
    """Where the moves of a line came from, as a pair: the kind (the repair from a line above or below, a trajectory
    from a game above or below, or the start: a prime, a repeat, or a search whose rounds gained nothing) and the
    game it began from."""
    n = d["n"]
    if d.get("repaired"):
        began, kind = d["repaired"]["from"], "repair"
    elif d.get("improvements") and d["trajectories"][d["improvements"][-1]["trajectory"]] != "start":
        began, kind = d["trajectories"][d["improvements"][-1]["trajectory"]], "trajectory"
    else:
        return "the start", ""
    return f"{kind} from {'above' if began > n else 'below'}", began


def load_records():
    """Every record of the best-known file, in file order."""
    records = []
    with open(RUN / "best-known.jsonl") as f:
        for position, text in enumerate(f):
            d = json.loads(text)
            records.append(Record(position, d["n"], d["score"], d["best_known"]["was"], d["best_known"]["file"],
                                  d["method"], *line_source(d)))
    return records


def streaks(games):
    """The runs of consecutive games among `games`, lowest first."""
    runs = []
    for n in sorted(games):
        if runs and runs[-1][-1] == n - 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    return runs


def spans(words):
    return [tuple(map(int, word.split("-"))) for word in words]


def window_list(arm):
    """The windows of the mini-pass's arm `t` or `c`, as (lo, hi)."""
    for text in (HERE / "windows.txt").read_text().splitlines():
        name, *words = text.split()
        if name == arm:
            return spans(words)
    raise ValueError(arm)


def follower_rounds():
    """The follower's rounds: {round: (time it began, [(lo, hi), ...])}."""
    rounds = {}
    for text in (HERE / "follower.log").read_text().splitlines():
        if match := ROUND_LOG.match(text):
            rounds[int(match[1])] = (match[2], spans(match[3].split()))
    return rounds


def minipass_hours():
    """The hours from the choice of the windows to the end of each arm, from minipass.log."""
    stamps = {}
    for text in (HERE / "minipass.log").read_text().splitlines():
        if match := re.match(r"^(windows chosen|[tc] done) (\d\d):(\d\d):(\d\d)$", text):
            stamps[match[1]] = int(match[2]) * 3600 + int(match[3]) * 60 + int(match[4])
    return {arm: (stamps[f"{arm} done"] - stamps["windows chosen"]) / 3600 for arm in ("t", "c")}


def window_stem(directory, lo, hi, round_=None):
    return f"r{round_}-w{lo}-{hi}" if directory == "pd" else f"w{lo}-{hi}"


def as_run(d, threads):
    """Whether a line was made with the options of the mini-pass and the follower: level 3, no stop, seed 3, the 8 games
    above, `threads` threads, on a clean build of master f7b134c."""
    return (d["effort"], d["seed"], d["above"], d["stop_growth"], d["threads"], d["build"]["dirty"]) == \
        (3, 3, 8, None, threads, False) and d["build"]["commit"].startswith(BUILD)


def play_of(directory, stems):
    """The games that the windows of `directory` named by `stems` played, from their lines and logs."""
    seconds = log_seconds = repair_seconds = work = above_bound = off_window = other_options = games = 0
    for stem in stems:
        lo, hi = spans([stem.split("-w")[-1] if directory == "pd" else stem[1:]])[0]
        with gzip.open(HERE / directory / f"{stem}.jsonl.gz", "rt") as f:
            lines = [json.loads(text) for text in f]
        plays = [d for d in lines if not d.get("repaired")]
        if {d["n"] for d in lines} != set(range(lo, hi + 1)) or len(plays) != hi - lo + 1:
            off_window += 1
        games += len(plays)
        seconds += sum(d["seconds"] for d in plays)
        work += sum(d["work"] for d in plays)
        above_bound += sum(d["score"] > d["bound"] for d in lines)
        other_options += sum(not as_run(d, THREADS[directory]) for d in lines)
        for text in (HERE / directory / f"{stem}.log").read_text().splitlines():
            if match := GAME_LOG.match(text):
                log_seconds += float(match[2])
            elif match := REPAIR_LOG.match(text):
                repair_seconds += float(match[1])
    return Play(len(stems), games, seconds, log_seconds, repair_seconds, work, above_bound, off_window, other_options)


def raised_by(records, files):
    """The games raised by `files`: n -> (first record, last record)."""
    first, last = {}, {}
    for r in records:
        if r.file in files:
            first.setdefault(r.n, r)
            last[r.n] = r
    return {n: (first[n], last[n]) for n in first}


def points_of(raised, games=None):
    return sum(last.score - first.was for n, (first, last) in raised.items() if games is None or n in games)


def fisher(a, b, c, d):
    """The two-sided p of Fisher's exact test of the table [[a, b], [c, d]]."""
    row, other, col, total = a + b, c + d, a + c, a + b + c + d

    def p(x):
        return comb(row, x) * comb(other, col - x) / comb(total, col)

    return sum(p(x) for x in range(max(0, col - other), min(row, col) + 1) if p(x) <= p(a) * (1 + 1e-9))


def show(header, rows):
    """Print a table whose first column is left-aligned and the others right-aligned."""
    cells = [header] + [[str(c) for c in row] for row in rows]
    widths = [max(len(row[i]) for row in cells) for i in range(len(header))]
    for row in cells:
        print("  ".join(c.ljust(w) if i == 0 else c.rjust(w) for i, (c, w) in enumerate(zip(row, widths))).rstrip())
    print()


def check_records(records, by_n, files, name):
    """The records of `files` chain: each says it replaced the score the record before it left, and no other file's
    record of the game lies between the first and the last of them."""
    broken = interlopers = 0
    for n in {r.n for r in records if r.file in files}:
        mine = [r for r in by_n[n] if r.file in files]
        for r in mine:
            before = [q for q in by_n[n] if q.position < r.position]
            broken += before[-1].score != r.was
        interlopers += any(mine[0].position < q.position < mine[-1].position and q.file not in files for q in by_n[n])
    print(f"{name}: records whose `was` is not the score before them {broken}; games with another file's record "
          f"between theirs {interlopers}")


def streak_table(raised, by_n, labels, own, title):
    """One row a streak of `raised`: its games, points, the root's source, and who raised the game above it, if the
    records of that game that came before the streak's say so."""
    rows, joins, roots = [], Counter(), Counter()
    for run in streaks(raised):
        lo, hi = run[0], run[-1]
        began = min(raised[n][0].position for n in run)
        above = next((labels[q.file] for q in by_n.get(hi + 1, []) if q.position < began and q.file in labels
                      and labels[q.file] != own), "no one")
        root = raised[lo][1]
        joins[above] += 1
        roots[root.source] += 1
        rows.append((f"{lo}-{hi}", len(run), points_of(raised, run), f"{root.source} {root.began}".strip(), above))
    print(title)
    show(("streak", "games", "points", "root's line came from", "game above raised by"), rows)
    print("game above raised by:", dict(joins))
    print("root's line came from:", dict(roots))
    print()
    return joins, roots


def arms(records, by_n, labels):
    """The mini-pass's table: judge.py's figures for arms t and c, recomputed."""
    print("== The mini-pass: arms t and c ==\n")
    columns, tables, summary = {}, {}, []
    wall = minipass_hours()
    for arm in ("t", "c"):
        windows = window_list(arm)
        stems = [window_stem(arm, lo, hi) for lo, hi in windows]
        play = play_of(arm, stems)
        raised = raised_by(records, {f"{stem}.jsonl" for stem in stems})
        runs = streaks(raised)
        hours = play.seconds * THREADS[arm] / 3600
        log_hours = play.log_seconds * THREADS[arm] / 3600
        with_gain = sum(any(lo <= n <= hi for n in raised) for lo, hi in windows)
        breakthroughs = [lo + WINDOW * k for lo, hi in windows for k in range(1, (hi - lo + 1) // WINDOW + 1)]
        columns[arm] = dict(
            windows=len(windows), games=play.games, breakthroughs=len(breakthroughs) if arm == "t" else "",
            threads=THREADS[arm], seconds=f"{play.seconds:.0f}", thread_hours=f"{hours:.1f}",
            thread_hours_from_logs=f"{log_hours:.1f}", repair_seconds=f"{play.repair_seconds:.0f}",
            wall_clock_hours=f"{wall[arm]:.2f}", thread_hours_held=f"{wall[arm] * THREADS[arm]:.1f}",
            work_M=f"{play.work / 1e6:.1f}", raised=len(raised), per_100=f"{100 * len(raised) / play.games:.1f}",
            streaks=len(runs), points=points_of(raised), windows_with_a_raise=with_gain,
            lines_above_the_bound=play.above_bound, windows_off=play.off_window,
            lines_with_other_options=play.other_options,
        )
        tables[arm] = (raised, windows, breakthroughs)
        summary.append((f"arm {arm}", play.games, hours, len(raised), len(runs), points_of(raised)))
        check_records(records, by_n, {f"{stem}.jsonl" for stem in stems}, f"arm {arm}")
    print()
    names = list(columns["t"])
    show(("", "arm t", "arm c"), [(name.replace("_", " "), columns["t"][name], columns["c"][name]) for name in names])
    t_with, c_with = columns["t"]["windows_with_a_raise"], columns["c"]["windows_with_a_raise"]
    t_n, c_n = columns["t"]["windows"], columns["c"]["windows"]
    print(f"windows with a raise: t {t_with} of {t_n}, c {c_with} of {c_n}; Fisher's exact test, two-sided "
          f"p = {fisher(t_with, t_n - t_with, c_with, c_n - c_with):.4f}\n")

    raised, windows, breakthroughs = tables["t"]
    roots = {int(word) for word in (HERE / "handled.init").read_text().split()}
    print(f"breakthroughs of pass 2 (the game above each block of {WINDOW} games of the windows): "
          f"{' '.join(map(str, breakthroughs))}")
    print(f"handled.init holds {len(roots)} roots, the game above each window; the breakthroughs it lacks: "
          f"{sorted(set(breakthroughs) - roots)}; the roots it has that are no breakthrough: "
          f"{sorted(roots - set(breakthroughs))}")
    began = min(first.position for first, last in raised.values())
    pass2 = [n for n in breakthroughs if any(q.file == PASS2[0] and q.position < began for q in by_n[n])]
    below = [n for n in pass2 if any(q.file == PASS2[0] and q.position < began for q in by_n[n - 1])]
    print(f"breakthroughs that pass 2's lower lane had raised before the first record of arm t: {len(pass2)} of "
          f"{len(breakthroughs)}; of them with the game below raised by it too {len(below)}\n")
    streak_table(raised, by_n, labels, "arm t", "Arm t's streaks")
    streak_table(tables["c"][0], by_n, labels, "arm c", "Arm c's streaks")
    return summary


def follower(records, by_n, labels):
    """The follower's rounds, from its log, its windows' lines and logs, and the best-known records."""
    print("== The follower ==\n")
    rounds = follower_rounds()
    handled = [line.split() for line in (HERE / "handled.txt").read_text().splitlines()]
    init = (HERE / "handled.init").read_text().split()
    print(f"handled.txt's first line is handled.init's: {handled[0] == init}; its lines after it hold "
          f"{[len(line) for line in handled[1:]]} roots, one a round\n")
    rows, every = [], set()
    totals = Counter()
    for k, (began, windows) in rounds.items():
        stems = [window_stem("pd", lo, hi, k) for lo, hi in windows]
        files = {f"{stem}.jsonl" for stem in stems}
        play = play_of("pd", stems)
        raised = raised_by(records, files)
        runs = streaks(raised)
        hours = play.seconds * THREADS["pd"] / 3600
        bottom = sum(lo in raised for lo, hi in windows)
        rows.append((k, began, len(handled[k]), len(windows), play.games, len(raised), len(runs), points_of(raised),
                     f"{hours:.1f}", f"{len(runs) / hours:.2f}", f"{play.log_seconds * THREADS['pd'] / 3600:.1f}",
                     f"{play.work / 1e6:.1f}", bottom))
        totals.update(windows=len(windows), games=play.games, raised=len(raised), points=points_of(raised),
                      seconds=play.seconds, log_seconds=play.log_seconds, repair=play.repair_seconds, work=play.work,
                      off=play.off_window, bound=play.above_bound, roots=len(handled[k]), other=play.other_options)
        every |= files
        check_records(records, by_n, files, f"round {k}")
    round_streaks = sum(row[6] for row in rows)
    union = raised_by(records, every)
    runs = streaks(union)
    hours = totals["seconds"] * THREADS["pd"] / 3600
    distinct = len({n for began, windows in rounds.values() for lo, hi in windows for n in range(lo, hi + 1)})
    rows.append(("all", "", totals["roots"], totals["windows"], totals["games"], len(union), len(runs),
                 points_of(union), f"{hours:.1f}", f"{len(runs) / hours:.2f}",
                 f"{totals['log_seconds'] * THREADS['pd'] / 3600:.1f}", f"{totals['work'] / 1e6:.1f}", ""))
    print()
    show(("round", "began", "roots", "windows", "games played", "games raised", "streaks", "points", "thread-hours",
          "streaks per thread-hour", "from the logs", "M work", "windows raising their bottom game"), rows)
    print(f"round by round, games raised add to {totals['raised']} (there are {len(union)} different ones), points to "
          f"{totals['points']} and streaks to {round_streaks} (the rounds extend each other's streaks); the follower's "
          f"files hold {sum(r.file in every for r in records)} best-known records")
    print(f"windows whose lines do not match their games {totals['off']}; lines above the bound {totals['bound']}; "
          f"lines made with other options than level 3, seed 3, 8 above, no stop, 8 threads, a clean {BUILD} "
          f"{totals['other']}; the repair walks took {totals['repair']:.0f} s in all (one thread; not in the "
          f"thread-hours); {distinct} different games played\n")
    check_records(records, by_n, every, "the follower")
    print()
    streak_table(union, by_n, labels, "the follower", "The follower's streaks")
    return [("the follower", totals["games"], hours, len(union), len(runs), points_of(union))]


def pass_two(records):
    """Pass 2 against pass 1, from their files: games raised, streaks, points, thread-hours."""
    print("== Pass 2, for scale ==\n")
    best = {"pass 1": {}, "pass 2": {}}
    plays = seconds = thread_seconds = work = log_seconds = 0
    threads, options, ranges = Counter(), Counter(), {}
    for name, files in (("pass 1", PASS1), ("pass 2", PASS2)):
        for file in files:
            with open(RUN / file) as f:
                for text in f:
                    d = json.loads(text)
                    best[name][d["n"]] = max(best[name].get(d["n"], 0), d["score"])
                    if name == "pass 2" and not d.get("repaired"):
                        plays += 1
                        seconds += d["seconds"]
                        thread_seconds += d["seconds"] * d["threads"]
                        work += d["work"]
                        threads[d["threads"]] += 1
                        options[(file, d["effort"], d["seed"], d["above"], d["stop_growth"],
                                 d["build"]["commit"][:7])] += 1
                        lo, hi = ranges.get(file, (d["n"], d["n"]))
                        ranges[file] = (min(lo, d["n"]), max(hi, d["n"]))
    for name in PASS2_LOGS:
        for text in (RUN / name).read_text().splitlines():
            if match := GAME_LOG.match(text):
                log_seconds += float(match[2])
    raised = {n: s - best["pass 1"][n] for n, s in best["pass 2"].items() if s > best["pass 1"].get(n, 0)}
    runs = streaks(raised)
    hours = thread_seconds / 3600
    print(f"pass 2's files {PASS2} against pass 1's {PASS1}: {len(best['pass 2'])} games in pass 2 "
          f"({min(best['pass 2'])}-{max(best['pass 2'])}), {len(best['pass 1'])} in pass 1; games of pass 2 not in "
          f"pass 1: {len(set(best['pass 2']) - set(best['pass 1']))}")
    print(f"plays {plays}; threads of the plays {dict(threads)}; the plays' seconds {seconds:.0f} s (the logs' "
          f"{log_seconds:.0f} s) and times their threads {hours:.1f} thread-hours; work {work / 1e6:.1f} M")
    print(f"games played by each file: {ranges}")
    print("plays by (file, level, seed, --above, stop on growth, commit of the build):")
    for key, count in sorted(options.items()):
        print(f"  {key}: {count}")
    recorded = raised_by(records, set(PASS2))
    carry = raised_by(records, {PASS2_CARRY})
    print(f"raised over pass 1: {len(raised)} games in {len(runs)} streaks, {sum(raised.values())} points; by the "
          f"best-known file's records of these two files: {len(recorded)} games in {len(streaks(recorded))} streaks, "
          f"{points_of(recorded)} points; the carry {PASS2_CARRY} (left out) raised {len(carry)}\n")
    return [("pass 2", plays, hours, len(raised), len(runs), sum(raised.values()))]


def main():
    records = load_records()
    by_n = defaultdict(list)
    for r in records:
        by_n[r.n].append(r)
    labels = {}
    for r in records:
        if r.file in PASS2 or r.file == PASS2_CARRY:
            labels[r.file] = "pass 2"
        elif r.file[0] == "w":
            labels[r.file] = "arm t" if (HERE / "t" / f"{r.file}.gz").exists() else "arm c"
        elif r.file[0] == "r":
            labels[r.file] = "the follower"
    ours = [r for r in records if r.file in labels and labels[r.file] != "pass 2"]
    print(f"best-known file: {len(ours)} records from the arms' and the follower's files, the last at position "
          f"{max(r.position for r in ours)} (pass 3 goes on appending to the file, so its length grows)\n")
    with open(HERE / "records.tsv", "w") as f:
        f.write("position\tn\tscore\twas\tfile\tmethod\tline came from\tbegan from game\n")
        for r in ours:
            f.write("\t".join(map(str, (r.position, r.n, r.score, r.was, r.file, r.method, r.source, r.began))) + "\n")
    summary = arms(records, by_n, labels) + follower(records, by_n, labels) + pass_two(records)
    print("== New streaks per thread-hour ==\n")
    show(("", "games played", "thread-hours", "games raised", "per 100 played", "streaks", "streaks per thread-hour",
          "points", "points per thread-hour"),
         [(name, played, f"{hours:.1f}", raised, f"{100 * raised / played:.1f}", runs, f"{runs / hours:.2f}", points,
           f"{points / hours:.0f}") for name, played, hours, raised, runs, points in summary])


if __name__ == "__main__":
    main()
