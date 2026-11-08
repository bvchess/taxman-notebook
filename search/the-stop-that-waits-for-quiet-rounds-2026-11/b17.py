#!/usr/bin/env python3
"""Study B17: the stop that waits for 4 quiet rounds (`--stop-quiet 4`, master 9477c8b), measured in the mode.

    python3 -I b17.py [--runs DIR] > out.txt

The five arms are the files DIR/ARM.jsonl (or .jsonl.gz) and logs DIR/ARM.log that run_jobs.py wrote (DIR defaults to
runs/ beside this script).  Each arm is compared with the arms of B14 (`tuning-the-unsound-mode-on-a-long-chain-2026-11`)
that ran the same games with `--stop-quiet 0`, the rule before 9477c8b.  The script reads B14's `b14.py` for the arms'
measures and streaks.  A game's line is the last line the file has for it, its *played* line the first.  Prints:

1. the checks of every line of the five arms;
2. a family at a time (an arm and its comparisons): the games at opt(n), the points short, the work (of both plays of a
   game played twice, and of the seeded plays alone, which the stop acts on) and the seconds per 100 games, the share
   of games stopped and pushed, on the whole range and on each half;
3. the pairs by B14's rule with the work in place of the seconds (X is better when it has more games at opt(n) for at
   most 10% more work, or the same games and points short for less work), and where the lines first differ;
4. the streaks of short games: the games that start one in some arm, the growth there, and the streaks that the change
   ended or began;
5. the seven games that B15 named: the points short, whether the stop ended the rounds, and the rounds;
6. every game where an arm scores less than its comparison, with the points;
7. the levels: the games at opt(n) against the work.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEARCH = os.path.normpath(os.path.join(HERE, ".."))
B14 = os.path.join(SEARCH, "tuning-the-unsound-mode-on-a-long-chain-2026-11")
sys.path.insert(0, B14)
import b14  # noqa: E402

COMMIT = "9477c8b"
SEED, THREADS = 1, 8
MARGIN = 1.10  # B14's rule: at most 10% more

# The five arms: (first game, last game, level, --stop-growth, --stop-quiet, --push-growth); None is `off`.
ARMS = {
    "q2-h": (3001, 4000, 2, 25, 4, 25),
    "q2": (4001, 5060, 2, 25, 4, 25),
    "q3-h": (3001, 4000, 3, 25, 4, 25),
    "off3-h": (3001, 4000, 3, None, 4, 25),
    "q3": (4001, 5060, 3, 25, 4, 25),
}
# B14's arms that serve as comparisons: the folder of B14 that holds each.
COMPARISONS = {
    "h-choice-l2": "part2", "h-choice-l3": "part2", "h-control-l2": "part2",
    "l1": "part1", "l2-push25": "part1", "l3": "part1", "l4": "part1",
}
# A family: its games, its arms (the first is the arm of this study) and the pairs (X, Y) compared by the rule.
FAMILIES = [
    ("Level 2 on 3001-4000", (3001, 4000), ["q2-h", "h-choice-l2", "h-control-l2"],
     [("q2-h", "h-choice-l2"), ("q2-h", "h-control-l2")]),
    ("Level 2 on 4001-5060", (4001, 5060), ["q2", "l2-push25"], [("q2", "l2-push25")]),
    ("Level 3 on 3001-4000", (3001, 4000), ["q3-h", "h-choice-l3", "off3-h"],
     [("q3-h", "h-choice-l3"), ("off3-h", "q3-h"), ("off3-h", "h-choice-l3")]),
    ("Level 3 on 4001-5060", (4001, 5060), ["q3", "l3"], [("q3", "l3")]),
]
# The levels, by range: every arm that ran the range at a level with its own rule for the stop.
LEVEL_ROWS = {
    (3001, 4000): ["h-choice-l2", "q2-h", "h-choice-l3", "q3-h", "off3-h"],
    (4001, 5060): ["l1", "l2-push25", "q2", "l3", "q3", "l4"],
}
LEVEL_STEPS = [("q2-h", "q3-h"), ("h-choice-l2", "h-choice-l3"), ("q2", "q3"), ("l2-push25", "l3")]
# The seven games of B15 and what its simulation expected of the 4 quiet rounds.
SEVEN = {3332: "opt(n)", 3384: "lost", 3750: "opt(n)", 3774: "opt(n)", 3850: "opt(n)", 3576: "opt(n)", 4107: "lost"}


def load(name, runs, opt, bounds):
    """An arm of this study (in `runs`) or of B14."""
    folder = runs if name in ARMS else os.path.join(B14, COMPARISONS[name])
    return b14.Arm(folder, name, opt, bounds)


def quiet_of(arm):
    """The --stop-quiet of an arm: its lines', and 0 for a build before the option."""
    return arm.lines[0].get("stop_quiet", 0)


def label(arm):
    return f"{arm.label}, quiet {quiet_of(arm)}"


def check(arm, opt, bounds):
    """Every line of an arm of this study: unsound, the build, the options, the bound, no score above it or above
    opt(n), prev.source, and the growth.  Returns the number of lines and the problems."""
    first, last, level, stop, quiet, push = ARMS[arm.name]
    problems = []
    for line in arm.lines:
        n = line["n"]
        where = f"n={n}"
        if not line.get("unsound"):
            problems.append(f"{where}: not unsound")
        if line["build"]["commit"][:7] != COMMIT or line["build"]["dirty"]:
            problems.append(f"{where}: build {line['build']}")
        if not first <= n <= last:
            problems.append(f"{where}: outside {first}-{last}")
        for key, want in (("effort", level), ("seed", SEED), ("threads", THREADS), ("stop_growth", stop),
                          ("stop_quiet", quiet), ("push_growth", push), ("unseeded_every", 0),
                          ("unseeded_effort", None), ("from_known", False), ("stop_at_known", None),
                          ("repair", True)):
            if line[key] != want:
                problems.append(f"{where}: {key} {line[key]}, not {want}")
        if line["bound"] != bounds[n]:
            problems.append(f"{where}: bound {line['bound']}, the parity bound {bounds[n]}")
        if line["score"] > bounds[n] or line["score"] > opt[n]:
            problems.append(f"{where}: score {line['score']} above the bound {bounds[n]} or opt {opt[n]}")
        other = line.get("other")
        if other is not None and (other["score"] > opt[n] or other["score"] > bounds[n]):
            problems.append(f"{where}: the other play scores {other['score']}, above opt {opt[n]} or the bound")
        prev = line.get("prev")
        if line["unseeded"]:
            if prev is not None:
                problems.append(f"{where}: an unseeded line with prev {prev['source']}")
        elif prev is None:
            problems.append(f"{where}: a seeded line with no prev")
        elif prev["source"] != ("table" if n == first else "run"):
            problems.append(f"{where}: prev.source {prev['source']}, not {'table' if n == first else 'run'}")
    for n, game in arm.games.items():
        recorded = game.played.get("growth")
        wanted = b14.growth_of(game, game.played["score"], bounds)
        if recorded is not None and not game.played["unseeded"] and recorded != wanted:
            problems.append(f"n={n}: growth {recorded}, the gaps say {wanted}")
    missing = [n for n in range(first, last + 1) if n not in arm.games]
    if missing:
        problems.append(f"{len(missing)} games missing, {missing[0]} to {missing[-1]}")
    return len(arm.lines), problems


def spans(lo, hi):
    return b14.halves(lo, hi)


def seeded_work(arm, lo, hi):
    """The work of the seeded plays of the games lo to hi, which the stop acts on and the push does not add to."""
    return sum(arm.games[n].seeded()[1] for n in range(lo, hi + 1) if n in arm.games)


def show_family(title, lo, hi, arms, opt):
    """The measures of the arms of a family on the whole range and each half."""
    print(f"\n### {title}\n")
    for a, b in spans(lo, hi):
        print(f"\nGames {a}-{b}:\n")
        print("| arm | settings | at opt(n) | points short | M work / 100 games | M seeded work / 100 games "
              "| s / 100 games | stopped | pushed |")
        print("|---|---|---|---|---|---|---|---|---|")
        for arm in arms:
            m = b14.measures(arm, a, b, opt)
            if not m["games"]:
                continue
            print(f"| {arm.name} | {label(arm)} | {m['at']} of {m['games']} | {m['points']} | "
                  f"{b14.per100(m, 'work') / 1e6:.1f} | {seeded_work(arm, a, b) * 100 / m['games'] / 1e6:.1f} | "
                  f"{b14.per100(m, 'seconds'):,.0f} | "
                  f"{m['stopped']} ({100 * m['stopped'] / m['games']:.1f}%) | "
                  f"{m['pushed']} ({100 * m['pushed'] / m['games']:.1f}%) |")
    print("\nThe command's wall time per 100 games:\n")
    for arm in arms:
        games = len(arm.games)
        print(f"* {arm.name}: {games} games, " + (f"{arm.wall * 100 / games:,.0f} s" if arm.wall else "?"))


def verdict(x, y):
    """Whether X's measures are better than Y's by the rule of B14 with the work in place of the seconds."""
    more = x["work"] / y["work"]
    if x["at"] > y["at"] and more <= MARGIN:
        return "better"
    if y["at"] > x["at"] and 1 / more <= MARGIN:
        return "worse"
    if x["at"] == y["at"] and x["points"] == y["points"]:
        return "better" if more < 1 else "worse" if more > 1 else "same"
    if x["at"] == y["at"] and x["points"] < y["points"] and more <= 1:
        return "better"
    if x["at"] == y["at"] and x["points"] > y["points"] and more >= 1:
        return "worse"
    return "neither"


def first_difference(x, y, lo, hi):
    """The first game whose played line differs between two arms in its score or rounds, and how many differ."""
    differ = [n for n in range(lo, hi + 1) if n in x.games and n in y.games and (
        x.games[n].played["score"] != y.games[n].played["score"] or
        x.games[n].played["rounds"] != y.games[n].played["rounds"])]
    return (differ[0] if differ else None), len(differ)


def show_pair(x, y, lo, hi, opt):
    """X against Y by the rule, on the whole range and on each half."""
    print(f"\n**{x.name} against {y.name}** (the rule with work; the seconds beside it)\n")
    print("| games | X at opt(n) less Y's | Y's points short less X's | work X / Y | seeded work X / Y "
          "| seconds X / Y | X is |")
    print("|---|---|---|---|---|---|---|")
    common, kinds = min(max(x.games), max(y.games), hi), []
    for a, b in spans(lo, hi):
        b = min(b, common)
        mx, my = b14.measures(x, a, b, opt), b14.measures(y, a, b, opt)
        if not mx["games"]:
            continue
        kind = verdict(mx, my)
        kinds.append(kind)
        print(f"| {a}-{b} | {mx['at'] - my['at']:+d} | {my['points'] - mx['points']:+d} | "
              f"{mx['work'] / my['work']:.3f} | {seeded_work(x, a, b) / seeded_work(y, a, b):.3f} | "
              f"{mx['seconds'] / my['seconds']:.3f} | **{kind}** |")
    agree = "agree" if len(set(kinds)) == 1 else "the halves disagree" if len(kinds) == 3 and kinds[1] != kinds[2] \
        else "the whole range differs from the halves"
    first, count = first_difference(x, y, lo, hi)
    print(f"\nThe whole range and the halves {agree}.  The played lines differ in score or rounds in {count} games, "
          f"the first {first}.")


def streak_cell(arm, found, n, opt):
    """What an arm has at game n: the length of the streak it starts there (p: pushed, s: the stop ended the rounds)
    and the growth of the seeded play, `tail of F` inside a streak that starts at F, `-` at opt(n)."""
    if n not in arm.games:
        return "?"
    s = found.get(n)
    if s is not None:
        return f"{s['length']}{'p' if s['pushed'] else ''}{'s' if s['stopped'] else ''} ({s['growth']:+d})"
    if arm.games[n].last["score"] == opt[n]:
        return "-"
    for first, t in found.items():
        if first < n < first + t["length"]:
            return f"tail of {first}"
    return "short"


def show_streaks(title, lo, hi, arms, pairs, opt, bounds):
    """The games that start a streak in some arm of the family, and the streaks that each pair ended or began."""
    print(f"\n### Streaks of short games: {title}\n")
    found = {arm.name: {s["first"]: s for s in b14.arm_streaks(arm, opt, bounds, lo, hi)} for arm in arms}
    for arm in arms:
        short = sum(s["length"] for s in found[arm.name].values())
        print(f"* {arm.name}: {len(found[arm.name])} streaks, {short} short games, "
              f"{short - len(found[arm.name])} handed on")
    starts = sorted({first for per in found.values() for first in per})
    print("\n| first game | " + " | ".join(arm.name for arm in arms) + " |")
    print("|---|" + "---|" * len(arms))
    for first in starts:
        print(f"| {first} | " + " | ".join(streak_cell(arm, found[arm.name], first, opt) for arm in arms) + " |")
    print("\nA cell is the length of the streak that starts at the game, with `p` if the push played the game twice "
          "and `s` if the stop ended its rounds, and the growth of the seeded play in parentheses; `tail of F` is a "
          "short game inside a streak from F, `-` a game at opt(n).")
    by_name = {arm.name: arm for arm in arms}
    for x_name, y_name in pairs:
        x, y = by_name[x_name], by_name[y_name]
        ended = [f"{f} ({found[y_name][f]['length']} games)" for f in sorted(found[y_name]) if f not in found[x_name]]
        began = [f"{f} ({found[x_name][f]['length']} games)" for f in sorted(found[x_name]) if f not in found[y_name]]
        changed = [f"{f} ({found[y_name][f]['length']} to {found[x_name][f]['length']} games)"
                   for f in sorted(found[x_name]) if f in found[y_name]
                   and found[x_name][f]["length"] != found[y_name][f]["length"]]
        print(f"\n{x.name} against {y.name}:\n")
        print(f"* ended (a start of {y.name} that {x.name} does not start): {', '.join(ended) or 'none'}")
        print(f"* began (a start of {x.name} that {y.name} does not start): {', '.join(began) or 'none'}")
        print(f"* the same start, another length: {', '.join(changed) or 'none'}")


def show_seven(arms, opt):
    """The seven games of B15: points short as the game ended, whether the stop ended its rounds, the rounds."""
    print("\n### The seven games\n")
    print("A cell: the points short at the end of the run (and as played, if the repair changed it), `stopped` if the "
          "stop ended the rounds or `ran`, the rounds, `pushed` if the push played the game twice.  B15 expected "
          "the 4 quiet rounds to leave the game at the value in the second column.\n")
    for games in ([n for n in SEVEN if n < 4001], [n for n in SEVEN if n >= 4001]):
        here = [arm for arm in arms if any(n in arm.games for n in games)]
        print("| game | B15 expected | " + " | ".join(arm.name for arm in here) + " |")
        print("|---|---|" + "---|" * len(here))
        for n in games:
            cells = []
            for arm in here:
                if n not in arm.games:
                    cells.append("-")
                    continue
                played, last = arm.games[n].played, arm.games[n].last
                short, short_played = opt[n] - last["score"], opt[n] - played["score"]
                cells.append(f"{short}{'' if short == short_played else f' (played {short_played})'}; "
                             f"{'stopped' if played['growth_stop'] else 'ran'} {played['rounds']}"
                             f"{'; pushed' if played['pushed'] else ''}")
            print(f"| {n} | {SEVEN[n]} | " + " | ".join(cells) + " |")
        print()


def role(found, n):
    """What the streaks of an arm (a dict by first game) say of game n."""
    for first, s in found.items():
        if first <= n < first + s["length"]:
            return "a streak start" if n == first else f"in the tail of {first}"
    return "alone"


def show_less(pairs_by_family, by_name, opt, bounds):
    """Every game where X scores less than Y, with the points, and the number where it scores more."""
    print("\n### The games where an arm scores less than its comparison\n")
    for title, lo, hi, pairs in pairs_by_family:
        for x_name, y_name in pairs:
            x, y = by_name[x_name], by_name[y_name]
            common = min(max(x.games), max(y.games), hi)
            ns = [n for n in range(lo, common + 1) if n in x.games and n in y.games]
            less = [n for n in ns if x.games[n].last["score"] < y.games[n].last["score"]]
            more = [n for n in ns if x.games[n].last["score"] > y.games[n].last["score"]]
            found = {s["first"]: s for s in b14.arm_streaks(x, opt, bounds, lo, hi)}
            lost = sum(y.games[n].last["score"] - x.games[n].last["score"] for n in less)
            won = sum(x.games[n].last["score"] - y.games[n].last["score"] for n in more)
            print(f"\n**{x_name} against {y_name}** ({title}): {len(less)} games lower by {lost} points in all, "
                  f"{len(more)} games higher by {won}\n")
            if less:
                print("| game | points lower | X short | Y short | X's stop ended the rounds | the game in X is |")
                print("|---|---|---|---|---|---|")
            for n in less:
                print(f"| {n} | {y.games[n].last['score'] - x.games[n].last['score']} | "
                      f"{opt[n] - x.games[n].last['score']} | {opt[n] - y.games[n].last['score']} | "
                      f"{'yes' if x.games[n].played['growth_stop'] else 'no'} | {role(found, n)} |")
            if more:
                print("\nHigher: " + ", ".join(f"{n} (+{x.games[n].last['score'] - y.games[n].last['score']})"
                                               for n in more))


def show_levels(by_name, opt):
    """Games at opt(n) against the work, for each range, and the step from one level to the next."""
    print("\n### The levels\n")
    for (lo, hi), names in LEVEL_ROWS.items():
        print(f"\nGames {lo}-{hi}:\n")
        print("| arm | settings | at opt(n) | points short | M work / 100 games | s / 100 games | M work per game at opt(n) |")
        print("|---|---|---|---|---|---|---|")
        for name in names:
            if name not in by_name:
                continue
            m = b14.measures(by_name[name], lo, hi, opt)
            print(f"| {name} | {label(by_name[name])} | {m['at']} of {m['games']} | {m['points']} | "
                  f"{b14.per100(m, 'work') / 1e6:.1f} | {b14.per100(m, 'seconds'):,.0f} | "
                  f"{m['work'] / m['at'] / 1e6:.3f} |")
    print("\nThe step from level 2 to level 3 (the same options but for the level):\n")
    print("| from | to | games | extra games at opt(n) | points short removed | work to / from | extra M work per extra game "
          "| seconds to / from |")
    print("|---|---|---|---|---|---|---|---|")
    for lower, upper in LEVEL_STEPS:
        if lower not in by_name or upper not in by_name:
            continue
        x, y = by_name[lower], by_name[upper]
        lo, hi = min(min(x.games), min(y.games)), min(max(x.games), max(y.games))
        mx, my = b14.measures(x, lo, hi, opt), b14.measures(y, lo, hi, opt)
        extra = my["at"] - mx["at"]
        per_game = f"{(my['work'] - mx['work']) / extra / 1e6:.1f}" if extra > 0 else "-"
        print(f"| {lower} | {upper} | {lo}-{hi} | {extra:+d} | {mx['points'] - my['points']:+d} | "
              f"{my['work'] / mx['work']:.3f} | {per_game} | {my['seconds'] / mx['seconds']:.3f} |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", default=os.path.join(HERE, "runs"), help="the folder of the five arms' files")
    args = parser.parse_args()
    opt, bounds = b14.opt_scores(), b14.parity_bounds(b14.PARITY)
    names = list(ARMS) + list(COMPARISONS)
    by_name = {}
    for name in names:
        try:
            by_name[name] = load(name, args.runs, opt, bounds)
        except FileNotFoundError:
            print(f"(no file for {name})")
    print(f"## Study B17: the arms in {os.path.relpath(args.runs, HERE)}\n")
    print("### Checks\n")
    for name in ARMS:
        if name not in by_name:
            continue
        arm = by_name[name]
        lines, problems = check(arm, opt, bounds)
        print(f"* {name}: games {min(arm.games)}-{max(arm.games)} ({len(arm.games)}), {lines} lines, "
              f"{'every line passes' if not problems else str(len(problems)) + ' problems: ' + '; '.join(problems[:8])}"
              f"; first game's prev.source {arm.games[min(arm.games)].played['prev']['source']}")
    pairs_by_family = []
    for title, (lo, hi), arm_names, pairs in FAMILIES:
        arms = [by_name[name] for name in arm_names if name in by_name]
        if len(arms) < len(arm_names):
            continue
        show_family(title, lo, hi, arms, opt)
        print(f"\n### The rule, with work: {title}")
        for x_name, y_name in pairs:
            show_pair(by_name[x_name], by_name[y_name], lo, hi, opt)
        show_streaks(title, lo, hi, arms, pairs, opt, bounds)
        pairs_by_family.append((title, lo, hi, pairs))
    show_seven([by_name[name] for name in by_name], opt)
    show_less(pairs_by_family, by_name, opt, bounds)
    show_levels(by_name, opt)


if __name__ == "__main__":
    main()
