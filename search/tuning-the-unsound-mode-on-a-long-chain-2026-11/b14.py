#!/usr/bin/env python3
"""Study B14: the arms of long chains of the unsound mode, 4001-5060 (Part 1) and 3001-4000 (Part 2).

    python3 -I b14.py DIR ARM... [--range LO-HI] [--levels] [--groups]

Each ARM is a file DIR/ARM.jsonl (or .jsonl.gz) of unsound lines over one range, with its log DIR/ARM.log (run_jobs.py
writes both).  A game's line is its last line in the file (a line the repair wrote again replaces it); its *played*
line is the first.  The range is split into two halves of equal size.  Prints:

1. the checks of every line (build, options, the bound, no score above the bound or opt(n), prev.source, growth);
2. for each arm, on the whole range and on each half: the games at opt(n), the points short, the seconds and the work
   per 100 games, the games stopped by the growth, pushed and played twice;
3. the streaks of short games of each arm, and a table of the games that start one in some arm;
4. the push's cost: the games played twice, those whose seeded play was at opt(n) already, and the seconds of the
   unseeded plays;
5. with --groups, the options' values against each other by the rule of the study (more games at opt(n) for at most
   10% more time, or the same games and points short in less time), on the whole range and on each half;
6. with --levels (Part 1), the levels 1 to 4 against E2's chains of 100 games over 4561-5060, and against B13's chain of
   200 games over 4861-5060.
"""

import argparse
import datetime
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK = os.path.normpath(os.path.join(HERE, "..", ".."))
SEARCH = os.path.join(NOTEBOOK, "search")
B13 = os.path.join(SEARCH, "stopping-and-pushing-by-the-gap-2026-11")
E2 = os.path.join(SEARCH, "the-datasheet-of-the-unsound-mode-2026-11", "runs")
PARITY = os.path.join(SEARCH, "the-parity-bound-against-the-frame-bound-2026-10", "parity_2_8191.jsonl.gz")
sys.path.insert(0, B13)
from b13lib import games_of, gap_before, growth_of, opened, opt_scores, parity_bounds, streaks  # noqa: E402

COMMIT = "ecb4bc4"
PUSH_REFERENCE = 50  # the default T of --push-growth, used to mark the streaks of an arm that has no push


class Arm:
    """One run: its games by n (b13lib.Game), its lines, its log's wall time and the repair's time."""

    def __init__(self, folder, name, opt, bounds):
        self.name = name
        self.path = os.path.join(folder, f"{name}.jsonl")
        self.path = self.path if os.path.exists(self.path) else f"{self.path}.gz"
        self.log = os.path.join(folder, f"{name}.log")
        self.games = games_of(self.path, opt)
        with opened(self.path) as f:
            self.lines = [json.loads(text) for text in f if text.strip()]
        first = self.lines[0]
        self.effort = first["effort"]
        self.stop = first["stop_growth"]
        self.push = first["push_growth"]
        self.every = first["unseeded_every"]
        self.unseeded_effort = first["unseeded_effort"]
        self.lo = min(self.games)
        self.wall, self.repair_seconds = self.read_log()

    def read_log(self):
        """The command's wall time from its log's first stamp to its last, and the repair's seconds it reported."""
        if not os.path.exists(self.log):
            return None, None
        stamps, repair = [], None
        with open(self.log) as f:
            for text in f:
                found = re.match(r"# (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \S+ ", text)
                if found:
                    stamps.append(datetime.datetime.strptime(found.group(1), "%Y-%m-%d %H:%M:%S"))
                found = re.match(r"repaired (\d+) lines; the repair took ([\d.]+) s", text)
                if found:
                    repair = float(found.group(2))
        wall = (stamps[-1] - stamps[0]).total_seconds() if len(stamps) > 1 else None
        return wall, repair

    @property
    def label(self):
        every = f", every {self.every}th twice" if self.every else ""
        unseeded = f", unseeded level {self.unseeded_effort}" if self.unseeded_effort else ""
        return f"level {self.effort}, stop {self.stop if self.stop is not None else 'off'}, " \
               f"push {self.push if self.push is not None else 'off'}{every}{unseeded}"


def unseeded_play(line):
    """(score, work, seconds) of the unseeded play of a game played twice, else None.  The line's seconds are those of
    both plays."""
    other = line.get("other")
    if other is None:
        return None
    if line["unseeded"]:
        return line["score"], line["work"], line["seconds"] - other["seconds"]
    return other["score"], other["work"], other["seconds"]


def check(arm, opt, bounds, lo):
    """Every line: unsound, the build, the options, the bound, no score above it or above opt(n), prev.source, and the
    growth.  Returns the number of lines and the problems."""
    problems = []
    for line in arm.lines:
        n = line["n"]
        where = f"n={n}"
        if not line.get("unsound"):
            problems.append(f"{where}: not unsound")
        if line["build"]["commit"][:7] != COMMIT or line["build"]["dirty"]:
            problems.append(f"{where}: build {line['build']}")
        # the line of an unseeded play records the level of that play, which --unseeded-effort sets
        effort = arm.unseeded_effort if line["unseeded"] and arm.unseeded_effort else arm.effort
        for key, want in (("effort", effort), ("seed", 1), ("threads", 8), ("stop_growth", arm.stop),
                          ("push_growth", arm.push), ("unseeded_every", arm.every),
                          ("unseeded_effort", arm.unseeded_effort), ("from_known", False), ("stop_at_known", None),
                          ("repair", True)):
            if line[key] != want:
                problems.append(f"{where}: {key} {line[key]}, not {want}")
        if line["bound"] != bounds[n]:
            problems.append(f"{where}: bound {line['bound']}, the parity bound {bounds[n]}")
        if line["score"] > bounds[n] or line["score"] > opt[n]:
            problems.append(f"{where}: score {line['score']} above the bound {bounds[n]} or opt {opt[n]}")
        other = line.get("other")
        if other is not None and other["score"] > opt[n]:
            problems.append(f"{where}: the other play scores {other['score']}, above opt {opt[n]}")
        prev = line.get("prev")
        if prev is not None:
            want = "table" if n == lo else "run"
            if prev["source"] != want:
                problems.append(f"{where}: prev.source {prev['source']}, not {want}")
    for n, game in arm.games.items():
        recorded = game.played.get("growth")
        if recorded is not None and not game.played["unseeded"] and \
                recorded != growth_of(game, game.played["score"], bounds):
            problems.append(f"n={n}: growth {recorded}, the gaps say {growth_of(game, game.played['score'], bounds)}")
    return len(arm.lines), problems


def measures(arm, lo, hi, opt):
    """The numbers of an arm on the games lo to hi that it has."""
    ns = [n for n in range(lo, hi + 1) if n in arm.games]
    played = [arm.games[n].played for n in ns]
    last = [arm.games[n].last for n in ns]
    twice = [p for p in played if p.get("other") is not None]
    return {
        "games": len(ns),
        "at": sum(1 for n, line in zip(ns, last) if line["score"] == opt[n]),
        "points": sum(opt[n] - line["score"] for n, line in zip(ns, last)),
        "seconds": sum(p["seconds"] for p in played),
        "work": sum(p["work"] + (p["other"]["work"] if p.get("other") else 0) for p in played),
        "searched": sum(1 for p in played if p["method"] == "search"),
        "stopped": sum(1 for p in played if p.get("growth_stop")),
        "pushed": sum(1 for p in played if p.get("pushed")),
        "twice": len(twice),
        "repaired": sum(1 for g in (arm.games[n] for n in ns) if g.last.get("repaired") is not None),
    }


def per100(m, key):
    return m[key] * 100 / m["games"]


def halves(lo, hi):
    """The whole range and its two halves."""
    mid = lo + (hi - lo + 1) // 2 - 1
    return [(lo, hi), (lo, mid), (mid + 1, hi)]


def show_measures(arms, opt, spans):
    for lo, hi in spans:
        print(f"\n### Games {lo}-{hi}\n")
        print("| arm | settings | games at opt(n) | points short | s / 100 games | M work / 100 games "
              "| searched | stopped | pushed | played twice | lines repaired |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for arm in arms:
            m = measures(arm, lo, hi, opt)
            if not m["games"]:
                continue
            print(f"| {arm.name} | {arm.label} | {m['at']} of {m['games']} | {m['points']} | "
                  f"{per100(m, 'seconds'):,.0f} | {per100(m, 'work') / 1e6:.1f} | {m['searched']} | "
                  f"{m['stopped']} ({100 * m['stopped'] / m['games']:.1f}%) | "
                  f"{m['pushed']} ({100 * m['pushed'] / m['games']:.1f}%) | {m['twice']} | {m['repaired']} |")
    print("\nWall time of the command per 100 games, and the repair's time reported:\n")
    for arm in arms:
        games = measures(arm, min(arm.games), max(arm.games), opt)["games"]
        wall = f"{arm.wall * 100 / games:,.0f} s" if arm.wall else "?"
        repair = f"{arm.repair_seconds:.1f} s" if arm.repair_seconds is not None else "none reported"
        print(f"* {arm.name}: {games} games, wall {wall} per 100 games, the repair's walks {repair}")


def seeded_growth(game, bounds):
    """The growth of the gap of the seeded play of a game, the play the push judges."""
    return growth_of(game, game.seeded()[0], bounds)


def push_threshold(arm):
    return arm.push if arm.push is not None else PUSH_REFERENCE


def arm_streaks(arm, opt, bounds, lo, hi):
    """The streaks of short games of an arm, each a dict, in order."""
    ns = [n for n in range(lo, hi + 1) if n in arm.games]
    short = {n: opt[n] - arm.games[n].last["score"] for n in ns}
    found = []
    for first, length, size in streaks(ns, short):
        game = arm.games[first]
        play = unseeded_play(game.played)
        end = first + length
        if end > hi or end not in arm.games:
            ended = "the end of the range"
        elif arm.games[end].last.get("repaired") is not None:
            ended = f"the repair's walk, from {arm.games[end].last['repaired']['from']}"
        else:
            ended = f"{end} reached opt(n) ({arm.games[end].played['method']})"
        growth = seeded_growth(game, bounds)
        found.append({
            "first": first, "length": length, "short": size, "points": sum(short[n] for n in range(first, end)),
            "method": game.played["method"], "growth": growth, "flagged": growth > push_threshold(arm),
            "pushed": bool(game.played.get("pushed")), "twice": play is not None,
            "stopped": bool(game.played.get("growth_stop")),
            "unseeded_short": None if play is None else opt[first] - play[0], "ended": ended,
        })
    return found


def show_streaks(arms, opt, bounds, lo, hi):
    print(f"\n### Streaks of short games, {lo}-{hi}\n")
    for arm in arms:
        found = arm_streaks(arm, opt, bounds, lo, hi)
        mark = f"push {arm.push}" if arm.push is not None else f"no push (marked against T = {PUSH_REFERENCE})"
        print(f"\n**{arm.name}** ({mark}): {len(found)} streaks\n")
        if not found:
            continue
        print("| first game | games | points short at the first | points short in all | method | growth of the "
              "seeded play | flagged by the push | played twice | unseeded play | rounds ended by the stop | "
              "ended by |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for s in found:
            unseeded = "-" if s["unseeded_short"] is None else \
                ("at opt(n)" if s["unseeded_short"] == 0 else f"{s['unseeded_short']} short")
            twice = "no" if not s["twice"] else ("by the push" if s["pushed"] else "for its n")
            print(f"| {s['first']}{'' if s['flagged'] else ' *'} | {s['length']} | {s['short']} | {s['points']} | "
                  f"{s['method']} | {s['growth']} | {'yes' if s['flagged'] else 'no'} | {twice} | {unseeded} | "
                  f"{'yes' if s['stopped'] else 'no'} | {s['ended']} |")
    print("\n`*` marks a streak that starts at a game whose seeded play's growth the push does not flag.")
    print(f"\n### Games that start a streak in some arm, {lo}-{hi}\n")
    names = [arm.name for arm in arms]
    table = {}
    for arm in arms:
        for s in arm_streaks(arm, opt, bounds, lo, hi):
            table.setdefault(s["first"], {})[arm.name] = s
    print("| first game | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    for first in sorted(table):
        cells = []
        for name in names:
            s = table[first].get(name)
            if s is None:
                cells.append("-")
            else:
                by_push, for_n = "p" if s["pushed"] else "", "t" if s["twice"] and not s["pushed"] else ""
                cells.append(f"{s['length']}{by_push}{for_n}")
        print(f"| {first} | " + " | ".join(cells) + " |")
    print("\nA cell is the streak's length in games, with `p` if the push played its first game twice and `t` if "
          "the schedule did; `-` means no streak starts there.")
    everywhere = [first for first in sorted(table) if len(table[first]) == len(names)]
    print(f"\nStarts in all {len(names)} arms: {everywhere}")
    print("\nThe short games of each arm: those that start a streak, those handed on to a game by the game before "
          "(the tail), the points short at the starts and in the tails, and the streaks that a restart from a "
          "proven game every 100 games (from the first game of the range, and from E2's 4561 if the range holds it) "
          "would have cut:\n")
    schemes = [("from the range's first game", lo)] + ([("from 4561", 4561)] if lo < 4561 <= hi else [])
    for arm in arms:
        found = arm_streaks(arm, opt, bounds, lo, hi)
        short = sum(s["length"] for s in found)
        starts = sum(s["short"] for s in found)
        cut = []
        for label, first_game in schemes:
            boundaries = range(first_game + 100, hi + 1, 100)
            cut.append(f"{label}: " + (", ".join(f"{s['first']} (+{s['length']})" for s in found if any(
                s["first"] < b < s["first"] + s["length"] for b in boundaries)) or "none"))
        total = sum(s["points"] for s in found)
        stopped = [s["first"] for s in found if s["stopped"]]
        unflagged = [s["first"] for s in found if not s["flagged"]]
        print(f"* {arm.name}: {short} short games, {len(found)} start streaks and {short - len(found)} are handed on; "
              f"{starts} points short at the starts and {total - starts} in the tails; {len(unflagged)} starts not "
              f"flagged by the push; {len(stopped)} starts at a game whose rounds the stop ended; cut by a restart: "
              f"{'; '.join(cut)}")


def show_repairs(arms, opt):
    """The lines the repair raised: the game, the game whose line gave the moves, the points gained, and whether the
    game above it ended short."""
    print("\n### Lines the repair raised\n")
    for arm in arms:
        found = []
        for n in sorted(arm.games):
            game = arm.games[n]
            if game.last.get("repaired") is None:
                continue
            above = arm.games.get(n + 1)
            above_short = "" if above is None else f", the game above {opt[n + 1] - above.last['score']} short"
            found.append(f"{n} (from {game.last['repaired']['from']}, +{game.last['score'] - game.played['score']}"
                         f"{above_short})")
        print(f"* {arm.name}: {len(found)}" + (": " + ", ".join(found) if found else ""))


def show_push(arms, opt, bounds, lo, hi):
    print(f"\n### The games played twice, {lo}-{hi}\n")
    print("| arm | pushed | seeded play at opt(n) already | unseeded play better | of those, reached opt(n) | "
          "points gained | no gain, seeded short | played twice for n | of those, unseeded better | "
          "unseeded plays' s | their share of the arm's s | their M work |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    gains = {}
    for arm in arms:
        rows = {"push": [], "every": []}
        total = 0.0
        for n in range(lo, hi + 1):
            if n not in arm.games:
                continue
            p = arm.games[n].played
            total += p["seconds"]
            play = unseeded_play(p)
            if play is not None:
                rows["push" if p.get("pushed") else "every"].append((n, arm.games[n].seeded()[0], *play))
        pushed, every = rows["push"], rows["every"]
        wasted = [r for r in pushed if r[1] == opt[r[0]]]
        better = [r for r in pushed if r[2] > r[1]]
        reached = [r for r in better if r[2] == opt[r[0]]]
        none = [r for r in pushed if r[1] < opt[r[0]] and r[2] <= r[1]]
        every_better = [r for r in every if r[2] > r[1]]
        seconds = sum(r[4] for r in pushed + every)
        work = sum(r[3] for r in pushed + every)
        print(f"| {arm.name} | {len(pushed)} | {len(wasted)} | {len(better)} | {len(reached)} | "
              f"{sum(r[2] - r[1] for r in better)} | {len(none)} | {len(every)} | {len(every_better)} | "
              f"{seconds:,.0f} | {100 * seconds / total:.1f}% | {work / 1e6:.1f} |")
        gains[arm.name] = [f"{r[0]} ({opt[r[0]] - r[1]} to {opt[r[0]] - r[2]} short)" for r in better + every_better]
    print("\nThe games whose unseeded play scored more than the seeded one (the points short of each play):\n")
    for name, found in gains.items():
        print(f"* {name}: {', '.join(found) or 'none'}")


def time_of(m):
    return m["seconds"]


def verdict(x, y):
    """Whether X's measures are better than Y's by the study's rule, worse, or neither."""
    more_time = time_of(x) / time_of(y)
    if x["at"] > y["at"] and more_time <= 1.10:
        return "better"
    if y["at"] > x["at"] and time_of(y) / time_of(x) <= 1.10:
        return "worse"
    if x["at"] == y["at"] and x["points"] == y["points"]:
        return "better" if time_of(x) < time_of(y) else "worse" if time_of(x) > time_of(y) else "same"
    if x["at"] == y["at"] and x["points"] < y["points"] and time_of(x) <= time_of(y):
        return "better"
    if x["at"] == y["at"] and x["points"] > y["points"] and time_of(x) >= time_of(y):
        return "worse"
    return "neither"


def show_group(title, arms, opt, lo, hi):
    """Each pair of the arms by the rule, on the whole range and on each half."""
    print(f"\n**{title}**\n")
    heads = " | ".join(f"{a}-{b}: games, points, time X/Y, X is" for a, b in halves(lo, hi))
    print(f"| X | Y | {heads} | agree |")
    print("|---|---|" + "---|" * 4)
    for i, x in enumerate(arms):
        for y in arms[i + 1:]:
            cells, kinds = [], []
            common = min(max(x.games), max(y.games), hi)  # an arm that was stopped early is compared on its games
            for a, b in halves(lo, hi):
                b = min(b, common)
                mx, my = measures(x, a, b, opt), measures(y, a, b, opt)
                if not mx["games"]:
                    cells.append("no games")
                    continue
                kind = verdict(mx, my)
                kinds.append(kind)
                upto = f" (to {b})" if b == common < hi else ""
                cells.append(f"{mx['at'] - my['at']:+d}, {my['points'] - mx['points']:+d} less short, "
                             f"{time_of(mx) / time_of(my):.2f}, **{kind}**{upto}")
            if len(kinds) == 3:
                agree = "yes" if len(set(kinds)) == 1 else "the halves disagree" if kinds[1] != kinds[2] else "no"
            else:
                agree = "?"
            print(f"| {x.name} | {y.name} | " + " | ".join(cells) + f" | {agree} |")


def show_groups(by_name, opt, lo, hi):
    groups = [
        ("The push's T (level 2)", ["l2-push25", "l2", "l2-push100"]),
        ("The stop's T (level 2)", ["l2", "l2-stop50", "l2-stopoff"]),
        ("The level of the unseeded play (level 2)", ["l2", "l2-unseeded1"]),
        ("The control against the defaults (level 2)", ["l2", "l2-control"]),
        ("The choice against the control (level 2)", ["l2-push25", "l2-control"]),
        ("The levels with the defaults", ["l1", "l2", "l3", "l4"]),
        ("The levels with the choice, on the held-out stretch", ["h-choice-l2", "h-choice-l3"]),
        ("The held-out stretch: the choice against the control (level 2)", ["h-choice-l2", "h-control-l2"]),
        ("The held-out stretch: the choice against the defaults (level 2)", ["h-choice-l2", "h-default-l2"]),
        ("The held-out stretch: the defaults against the control (level 2)", ["h-default-l2", "h-control-l2"]),
    ]
    print("\n### The options against each other, by the rule of the study\n")
    print("`X is better` means X has more games at opt(n) for at most 10% more of the game seconds, or the same games "
          "and points short in fewer seconds (or fewer points short, no more time).  The cells give X's games at "
          "opt(n) less Y's, Y's points short less X's, and X's seconds over Y's.")
    for title, names in groups:
        arms = [by_name[name] for name in names if name in by_name]
        if len(arms) == len(names):
            show_group(title, arms, opt, lo, hi)


def segment_games(level_file, opt):
    """The games of E2's chains of one level (its files `e{level_file}-{first}.jsonl.gz`), by n."""
    games = {}
    for first in (4561, 4661, 4761, 4861, 4961):
        games.update(games_of(os.path.join(E2, f"e{level_file}-{first}.jsonl.gz"), opt))
    return games


class Loaded:
    """A set of games with the interface that `measures` needs (a stand-in for an Arm)."""

    def __init__(self, games):
        self.games = games


def show_levels(by_name, opt, bounds, lo, hi):
    print("\n### The levels against E2's chains of 100 games and B13's chain of 200\n")
    print("E2's chains (old efforts 2 to 5 are levels 1 to 4) ran on 4 threads of a busy machine, with the options "
          "of this build but no stop, no push and no repair; B13's, level 3 with the defaults, 4861-5060 from the "
          "table's 4860, on 8 threads with up to 48 threads busy.\n")
    b13 = Loaded(games_of(os.path.join(B13, "chains", "f", "band0-4861.jsonl.gz"), opt))
    print("| level | range | E2: at opt(n) | E2: points short | E2: s / 100 games (4 threads) | "
          "this chain: at opt(n) | points short | s / 100 games (8 threads) | M work / 100, E2 | M work / 100, chain |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    spans = ((4561, 5060), (4561, 4660), (4661, 4760), (4761, 4860), (4861, 4960), (4961, 5060), (4861, 5060))
    for level in (1, 2, 3, 4):
        arm = by_name.get(f"l{level}")
        if arm is None:
            continue
        e2 = Loaded(segment_games(level + 1, opt))
        for a, b in spans:
            if b > max(arm.games):
                continue
            me, mc = measures(e2, a, b, opt), measures(arm, a, b, opt)
            print(f"| {level} | {a}-{b} | {me['at']} of {me['games']} | {me['points']} | "
                  f"{per100(me, 'seconds'):,.0f} | {mc['at']} of {mc['games']} | {mc['points']} | "
                  f"{per100(mc, 'seconds'):,.0f} | {per100(me, 'work') / 1e6:.1f} | {per100(mc, 'work') / 1e6:.1f} |")
    mb = measures(b13, 4861, 5060, opt)
    print(f"\nB13, level 3, defaults, 4861-5060 from the table's 4860: {mb['at']} of {mb['games']} at opt(n), "
          f"{mb['points']} points short, {per100(mb, 'seconds'):,.0f} s and {per100(mb, 'work') / 1e6:.1f} M work "
          f"per 100 games.")
    arm = by_name.get("l3")
    if arm is not None and max(arm.games) >= 5060:
        differ = [n for n in range(4861, 5061) if arm.games[n].last["score"] != b13.games[n].last["score"]]
        print(f"Level 3 here against B13's lines of 4861-5060: {len(differ)} games with another score {differ}.")
    print("\nHours per 100 games over 4561-5060 (game seconds), E2's chain alone-estimates on 4 and 8 threads from its "
          "README (levels 1 to 4): 4 threads 0.15, 0.24, 0.42, 0.77; 8 threads 0.09, 0.14, 0.25, 0.46.")


def show_games(arms, opt, bounds, first, last):
    """The games first to last of each arm, one line a game: the points short of the line as played and as it ends,
    the method, the growth recorded and of the seeded play, whether it was pushed, the points short of the other play,
    whether the stop ended the rounds, the rounds, the seconds and the game whose line repaired it."""
    print(f"\n### Games {first}-{last}, one line a game\n")
    for arm in arms:
        print(f"\n**{arm.name}**\n")
        print("| n | short as played | short at the end | method | growth | growth of the seeded play | pushed | "
              "unseeded line kept | the other play short | stopped | rounds | s | repaired from |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for n in range(first, last + 1):
            game = arm.games[n]
            p, end = game.played, game.last
            other = p.get("other")
            repaired = "" if end.get("repaired") is None else end["repaired"]["from"]
            print(f"| {n} | {opt[n] - p['score']} | {opt[n] - end['score']} | {p['method']} | {p['growth']} | "
                  f"{seeded_growth(game, bounds)} | {'yes' if p['pushed'] else 'no'} | "
                  f"{'yes' if p['unseeded'] else 'no'} | {'-' if other is None else opt[n] - other['score']} | "
                  f"{'yes' if p['growth_stop'] else 'no'} | {p['rounds']} | {p['seconds']:.1f} | {repaired} |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument("arms", nargs="+")
    parser.add_argument("--range", default="4001-5060")
    parser.add_argument("--levels", action="store_true")
    parser.add_argument("--groups", action="store_true")
    parser.add_argument("--games", help="LO-HI: print these games of each arm, one line a game, and nothing else")
    args = parser.parse_args()
    lo, hi = map(int, args.range.split("-"))
    opt, bounds = opt_scores(), parity_bounds(PARITY)
    arms = [Arm(args.folder, name, opt, bounds) for name in args.arms]
    by_name = {arm.name: arm for arm in arms}
    if args.games:
        show_games(arms, opt, bounds, *map(int, args.games.split("-")))
        return
    print(f"## Study B14: {args.folder}, games {lo}-{hi}\n")
    print("### Checks\n")
    for arm in arms:
        lines, problems = check(arm, opt, bounds, lo)
        first = arm.games[min(arm.games)].played
        print(f"* {arm.name}: games {min(arm.games)}-{max(arm.games)} ({len(arm.games)}), {lines} lines, "
              f"{'every line passes' if not problems else str(len(problems)) + ' problems: ' + '; '.join(problems[:8])}"
              f"; first game's prev.source {first['prev']['source']}")
    show_measures(arms, opt, halves(lo, hi))
    show_streaks(arms, opt, bounds, lo, hi)
    show_push(arms, opt, bounds, lo, hi)
    show_repairs(arms, opt)
    if args.groups:
        show_groups(by_name, opt, lo, hi)
    if args.levels:
        show_levels(by_name, opt, bounds, lo, hi)


if __name__ == "__main__":
    main()
