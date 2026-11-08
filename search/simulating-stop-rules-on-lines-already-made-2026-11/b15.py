#!/usr/bin/env python3
"""Study B15: stop rules simulated on the lines of chains that ran with no stop.

    python3 -I b15.py > out.txt

Prints, in order:

1. the data sets (B14's chains with no stop at level 2, E2's chains at levels 3 to 6) and the checks of their lines;
2. the estimate of the work after a round, against the real stops of the default arms (B14's l2, l3 and l4,
   h-default-l2);
3. the rules: per data set, the share of the seeded plays' work they save and the games and points they lose;
4. the six games that start streaks in B14, per rule, and every game that the default rule loses;
5. what the rounds after the gate gain, the survivors' scores as a signal, and the estimate of the work against its
   alternatives.

The simulation is in b15lib.py.
"""

import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b15lib as lib  # noqa: E402

ANY = 10**9  # a growth bound that never binds
OPT = lib.opt_scores()
P1 = [os.path.join(lib.B14, "part1", f"{arm}.jsonl.gz") for arm in
      ("l1", "l2", "l2-push25", "l2-push100", "l2-stop50", "l2-stopoff", "l2-control", "l2-unseeded1", "l3", "l4")]
P2 = [os.path.join(lib.B14, "part2", f"{arm}.jsonl.gz") for arm in
      ("h-choice-l2", "h-choice-l3", "h-control-l2", "h-default-l2")]
STOPOFF, CONTROL, L2, L3, L4 = P1[5], P1[6], P1[1], P1[8], P1[9]
H_CONTROL, H_DEFAULT = P2[2], P2[3]
DEFAULT = lib.Rule("default")
RULES = [
    ("default", DEFAULT, "the band of ±25, asked from 131,072 work (the mode's)"),
    ("k1", lib.Rule("k1", quiet=1), "and the last round raised nothing"),
    ("k2", lib.Rule("k2", quiet=2), "and the last 2 rounds raised nothing"),
    ("k3", lib.Rule("k3", quiet=3), "and the last 3 rounds raised nothing"),
    ("k4", lib.Rule("k4", quiet=4), "and the last 4 rounds raised nothing"),
    ("k6", lib.Rule("k6", quiet=6), "and the last 6 rounds raised nothing"),
    ("gate 196,608", lib.Rule("g", gate=196_608), "the default, asked from 196,608 work"),
    ("gate 262,144", lib.Rule("g", gate=262_144), "the default, asked from level 2's budget"),
    ("±10", lib.Rule("b10", lo=-10, hi=10), "the band of ±10"),
    ("-10..25, k4", lib.Rule("b", lo=-10, hi=25, quiet=4), "growth from −10 to 25, and k4"),
    ("≤ 25, k2", lib.Rule("o2", lo=-ANY, hi=25, quiet=2), "growth up to 25 (no lower limit), and k2"),
    ("≤ 25, k4", lib.Rule("o4", lo=-ANY, hi=25, quiet=4), "growth up to 25 (no lower limit), and k4"),
    ("survivor 200", lib.Rule("s", survivor=200), "the default, unless a survivor scores within 200 of the start"),
]


def load(opt, bounds):
    """The data sets: B14's chains with no stop at level 2, and E2's chains at levels 3 to 6 (old efforts 4 to 7)."""
    sets = {
        "stopoff": lib.plays_of(STOPOFF, "stopoff", opt, bounds, 4001, 5060, companions=P1),
        "control": lib.plays_of(CONTROL, "control", opt, bounds, 4001, 5060, companions=P1),
        "h-control": lib.plays_of(H_CONTROL, "h-control", opt, bounds, 3001, 4000, companions=P2),
    }
    for old in (4, 5, 6, 7):
        sets[f"level {old - 1}"] = lib.e2_plays(old, opt, bounds, companions=P1)
    return sets


def show_data(sets):
    print("## The data sets\n")
    print("| data set | file | level | games | searched, seeded play simulated | unseeded play kept (not simulated) | "
          "seeded plays' work, M | work of both plays, M | problems in the lines |")
    print("|---|---|---|---|---|---|---|---|---|")
    files = {"stopoff": "B14 part1/l2-stopoff", "control": "B14 part1/l2-control",
             "h-control": "B14 part2/h-control-l2"}
    for name, data in sets.items():
        problems = [problem for play in data.plays.values() for problem in lib.line_checks(play)]
        level = {play.level for play in data.plays.values()}
        file = files.get(name) or f"E2 e{int(name.split()[-1]) + 1}-LO"
        print(f"| {name} | {file} | {','.join(map(str, sorted(level)))} "
              f"| {data.games:,} | {len(data.plays)} | {data.others} | {data.seeded_work / 1e6:.1f} | "
              f"{data.all_work / 1e6:.1f} | {len(problems)} |")
        for problem in problems[:5]:
            print(f"  problem: {problem}")
    print()


def real_agreement(label, data, reference):
    """Simulate the default rule on `data`, and compare it with the stops that the arm `reference` made on the games
    that began from the same moves and agree with it as far as it went."""
    ref = lib.games(reference, OPT)
    same = agree = by_one = 0
    real_saved = sim_saved = 0.0
    errors = []
    for n, play in data.plays.items():
        game = ref.get(n)
        if game is None:
            continue
        line = game.played
        mine = [g for g in lib.gains_of(play.line) if g[0] <= line["rounds"]]
        if line["method"] != "search" or line.get("unseeded") or line["start"] != play.line["start"] or \
                lib.below(line) != lib.below(play.line) or lib.gains_of(line) != mine:
            continue
        same += 1
        real = line["rounds"] if line["growth_stop"] else None
        if real is not None:
            errors.append(abs(play.work_after[real] - line["work"]) / line["work"])
        sim = play.stop(DEFAULT)
        real_saved += play.work - line["work"] if real else 0
        sim_saved += play.work - play.work_after[sim] if sim else 0
        agree += real == sim
        by_one += real != sim and real is not None and sim is not None and abs(real - sim) == 1
    return (f"| {label} | {same} | {agree} ({agree / same:.0%}) | {by_one} | {sum(errors) / len(errors):.1%} | "
            f"{real_saved / 1e6:.2f} | {sim_saved / 1e6:.2f} ({sim_saved / real_saved - 1:+.1%}) |")


def show_validation(opt, bounds):
    print("## The estimate of the work after a round, against the real stops\n")
    print("The default rule simulated on a line with no stop, and the stop that the default arm made on the same game "
          "(the same start, the same moves below and the same gains as far as the arm went).  *Model only*: the work "
          "between the rounds whose work the line records is shared out by the model of the cost of a round; "
          "*straight line*: shared out evenly.  "
          "*With the other arms' ends*: the work at the end of every other line of the game that agrees with it "
          "(never the reference arm's) is known too, which is not independent of the arm: its variants (the push, "
          "the stop at 50) stopped many of the same games at the same rounds.\n")
    print("| data set against the arm | games with the same inputs | the stop round agrees | differs by one round | "
          "error of the work at the arm's stop rounds | work saved by the arm's stops, M | "
          "work saved by the simulated stops, M |")
    print("|---|---|---|---|---|---|---|")
    pairs = [("stopoff against l2", STOPOFF, "stopoff", L2, 4001, 5060, P1),
             ("control against l2", CONTROL, "control", L2, 4001, 5060, P1),
             ("h-control against h-default-l2", H_CONTROL, "h-control", H_DEFAULT, 3001, 4000, P2)]
    kept = lib.STAGE_COST
    for mode, known, costs in (("model only", False, kept), ("straight line", False, (1.0, 1.0, 1.0)),
                               ("with the other arms' ends", True, kept)):
        lib.STAGE_COST = costs
        for label, path, name, reference, lo, hi, arms in pairs:
            near = [p for p in arms if p != reference] if known else []
            data = lib.plays_of(path, name, opt, bounds, lo, hi, companions=near)
            print(real_agreement(f"{label}, {mode}", data, reference))
        for old, reference in ((4, L3), (5, L4)):
            near = [p for p in P1 if p != reference] if known else []
            data = lib.e2_plays(old, opt, bounds, companions=near, other_efforts=known)
            print(real_agreement(f"level {old - 1} (E2) against l{old - 1}, {mode}", data, reference))
    lib.STAGE_COST = kept
    print()


def fmt(total):
    return f"{total.share:.1%} | {total.lost} ({total.new_short}) | {total.points}"


def show_rules(sets):
    print("## The rules\n")
    print("*Saved* is the share of the seeded plays' work that the rule saves; *lost* the games whose line scores "
          "fewer points than the line with no stop (in parentheses, those that were at opt(n) in it and are short "
          "now), and *points* the points they lose.\n")
    names = ("stopoff", "control", "h-control")
    print("### Level 2\n")
    print("| rule | what it asks | stopoff 4001-5060: saved | lost | points | control 4001-5060: saved | lost | points "
          "| h-control 3001-4000: saved | lost | points |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for name, rule, what in RULES:
        print(f"| {name} | {what} | " + " | ".join(fmt(lib.totals(sets[s], rule)) for s in names) + " |")
    print()
    shares = [lib.totals(sets[s], DEFAULT).saved / sets[s].all_work for s in names]
    print("As a share of the work of both plays of every game, the default rule saves " +
          ", ".join(f"{share:.1%} in {s}" for share, s in zip(shares, names)) + ".\n")
    print("### Levels 3 to 6 (E2, 4561-5060)\n")
    levels = ("level 3", "level 4", "level 5", "level 6")
    print("| rule | " + " | ".join(f"{s}: saved | lost | points" for s in levels) + " |")
    print("|---|" + "---|---|---|" * len(levels))
    for name, rule, what in RULES:
        if rule.survivor is not None:
            continue
        print(f"| {name} | " + " | ".join(fmt(lib.totals(sets[s], rule)) for s in levels) + " |")
    print()
    print("### Level 2, stopoff and h-control together (2,060 games)\n")
    print("| rule | saved | lost (at opt(n) before) | points |")
    print("|---|---|---|---|")
    for name, rule, what in RULES:
        both = [lib.totals(sets[s], rule) for s in ("stopoff", "h-control")]
        saved = sum(t.saved for t in both) / sum(t.seeded_work for t in both)
        print(f"| {name} | {saved:.1%} | {sum(t.lost for t in both)} ({sum(t.new_short for t in both)}) | "
              f"{sum(t.points for t in both)} |")
    print()


def real_stop(path, n):
    """The round at which the default arm's rounds of game n ended by the stop, else None."""
    line = lib.games(path, OPT)[n].played
    return line["rounds"] if line["growth_stop"] else None


def show_lost(sets):
    print("## The games that the default rule loses\n")
    print("*Stop* is the round after which the simulated rule ends the rounds, *arm's stop* the round at which the "
          "default arm ended the game's rounds, if it began from the same moves (else `other`, or `-` if its rounds "
          "were not ended by the stop).\n")
    print("| game | data set | rounds | gains | stop | arm's stop | growth at the stop | growth at the end | "
          "points lost | short of opt(n) with no stop |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name, arm in (("stopoff", L2), ("control", L2), ("h-control", H_DEFAULT)):
        for n, play in sets[name].plays.items():
            stop, _, loss = play.result(DEFAULT)
            if not loss:
                continue
            line = lib.games(arm, OPT)[n].played
            same = lib.below(line) == lib.below(play.line) and line["start"] == play.line["start"] and \
                lib.gains_of(line) == [g for g in lib.gains_of(play.line) if g[0] <= line["rounds"]]
            real = (real_stop(arm, n) or "-") if same else "other"
            print(f"| {n} | {name} | {play.rounds} | {', '.join(map(str, play.gain_rounds))} | {stop} | {real} | "
                  f"{play.growth(stop)} | {play.growth(play.rounds)} | {loss} | {play.opt - play.final} |")
    print()


def show_named(sets):
    print("## The six games\n")
    print("Each cell says whether the rule ends the game's rounds before its last gain (the points it would lose), "
          "or `-` if not.  *Gains* are the rounds with a gain in the line with no stop; *stop* the round at which the "
          "default arm (h-default-l2, or l2 for 4107) really stopped it.\n")
    names = [name for name, _, _ in RULES]
    print("| game | data set | rounds | gains | points the gains add to the start | stop | " + " | ".join(names) + " |")
    print("|---|---|---|---|---|---|" + "---|" * len(names))
    for n in lib.NAMED:
        for set_name, arm in (("stopoff", L2), ("control", L2), ("h-control", H_DEFAULT)):
            play = sets[set_name].plays.get(n)
            if play is None:
                continue
            cells = []
            for name, rule, what in RULES:
                stop = play.stop(rule)
                loss = 0 if stop is None else play.final - play.score[stop]
                cells.append(f"{loss} lost" if loss else "-")
            print(f"| {n} | {set_name} | {play.rounds} | {', '.join(map(str, play.gain_rounds))} | "
                  f"{play.final - play.line['start']} | {real_stop(arm, n)} | " + " | ".join(cells) + " |")
    print()


def show_gaps(sets):
    print("## Where the gains after the gate come from\n")
    print("The rounds with no gain before each gain that comes at or after the gate (131,072 work), counted from the "
          "game's last gain before it, or from the start of the rounds if there is none.\n")
    print("| quiet rounds before the gain | " + " | ".join(["0", "1", "2", "3", "4", "5-6", "7 or more"]) + " |")
    print("|---|" + "---|" * 7)
    for label, names in (("level 2: stopoff and h-control", ("stopoff", "h-control")),
                         ("levels 3 to 6 (E2)", ("level 3", "level 4", "level 5", "level 6"))):
        gaps = Counter()
        for name in names:
            for play in sets[name].plays.values():
                before = 0
                for gain in play.gain_rounds:
                    if play.work_after[gain] >= lib.LEVEL1_BUDGET:
                        gaps[gain - before - 1] += 1
                    before = gain
        long = sum(count for quiet, count in gaps.items() if quiet >= 7)
        buckets = [gaps[0], gaps[1], gaps[2], gaps[3], gaps[4], gaps[5] + gaps[6], long]
        print(f"| {label}: {sum(buckets)} gains | " + " | ".join(map(str, buckets)) + " |")
    print()


def show_survivors(sets):
    print("## The survivors' scores as a signal\n")
    print("Among the games that the default rule stops, those with a survivor of a game below that scores within D "
          "points of the start (a rule that keeps such a game going would not stop them), and among the games that "
          "lose points, the same.\n")
    print("| D | stopped games flagged | of the games that lose points, flagged |")
    print("|---|---|---|")
    rows = []
    for name in ("stopoff", "h-control"):
        for play in sets[name].plays.values():
            stop = play.stop(DEFAULT)
            if stop is None:
                continue
            rows.append((play.survivors_near, play.final > play.score[stop]))
    stopped, lost = len(rows), sum(1 for _, bad in rows if bad)
    for d in (0, 25, 50, 100, 200, 400, 800):
        flagged = [bad for near, bad in rows if near >= -d]
        print(f"| {d} | {len(flagged)} of {stopped} ({len(flagged) / stopped:.0%}) | "
              f"{sum(flagged)} of {lost} ({sum(flagged) / lost:.0%}) |")
    print()


def show_sensitivity(opt, bounds):
    print("## The estimate of the work against its alternatives\n")
    print("The model's cost of a round at stage 0, 1 and 2 (relative to stage 2), changed; (1, 1, 1) is the straight "
          "line between the rounds whose work is known.  The default rule and k4 on the level-2 data sets.\n")
    print("| costs | rule | stopoff: saved | lost | h-control: saved | lost |")
    print("|---|---|---|---|---|---|")
    kept = lib.STAGE_COST
    for costs in (kept, (0.1, 0.63, 1.0), (0.2, 0.4, 1.0), (1.0, 1.0, 1.0)):
        lib.STAGE_COST = costs
        stopoff = lib.plays_of(STOPOFF, "stopoff", opt, bounds, 4001, 5060, companions=P1)
        h_control = lib.plays_of(H_CONTROL, "h-control", opt, bounds, 3001, 4000, companions=P2)
        for name, rule, _ in RULES:
            if name not in ("default", "k4"):
                continue
            a, b = lib.totals(stopoff, rule), lib.totals(h_control, rule)
            print(f"| {costs} | {name} | {a.share:.1%} | {a.lost} ({a.new_short}) | "
                  f"{b.share:.1%} | {b.lost} ({b.new_short}) |")
    lib.STAGE_COST = kept
    print()


def main():
    bounds = lib.parity_bounds()
    sets = load(OPT, bounds)
    show_data(sets)
    show_validation(OPT, bounds)
    show_rules(sets)
    show_named(sets)
    show_lost(sets)
    show_gaps(sets)
    show_survivors(sets)
    show_sensitivity(OPT, bounds)


if __name__ == "__main__":
    main()
