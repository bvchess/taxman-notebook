"""Study B15: the lines of chains that ran with no stop, and a stop rule simulated on them.

A searched game's line records the round, the work and the score of each round that raised its score (`improvements`),
its rounds and its work.  The score after any round is the score of the last improvement up to it.  The work after a
round with no gain is not recorded, and a round's work rises as the game goes on (a trajectory's neighborhoods are
cheap at stage 0, dearer at stage 1, and run to their step limit at stage 2), so a straight line between the rounds whose
work is recorded puts the work of an early round 40% too high at level 2.  The work is taken instead from two sources:

* the work at the end of every other line of the same game that began from the same moves and agrees with it as far as
  it went (the other levels and options of the same study, and E2's levels), which is the work at that round exactly;
* between the rounds whose work is known, in proportion to a model of the cost of a round from the line's
  `stage_rounds`, which puts the work at the real stops of the default arms within 7% on average (the second section
  of b15.py's output).

A rule that asks "is the game done?" after a round is run against these numbers: it ends the rounds at the first round
it says yes, and the line it leaves is the line as it was after that round.

The stop acts on a game's seeded play only (the unseeded play of a game played twice runs to its budget).  A game
played twice whose kept line is the unseeded play has no record of its seeded play's rounds: it is left out of the
simulation, and its seeded play's work stays in the work the savings are shares of.
"""

import bisect
import os
import sys
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
SEARCH = os.path.normpath(os.path.join(HERE, ".."))
B13 = os.path.join(SEARCH, "stopping-and-pushing-by-the-gap-2026-11")
B14 = os.path.join(SEARCH, "tuning-the-unsound-mode-on-a-long-chain-2026-11")
E2 = os.path.join(SEARCH, "the-datasheet-of-the-unsound-mode-2026-11", "runs")
sys.path.insert(0, B13)
from b13lib import games_of, gap_before, opt_scores, parity_bounds  # noqa: E402

LEVEL1_BUDGET = 131_072  # the work from which the stop is asked, whatever the level (`stop_floor` in unsound.rs)
ROUND_WORK = 65_536  # a level's budget is this times 2 to the level
STAGE_COST = (0.15, 0.5, 1.0)  # the cost of a round at stage 0, 1 and 2, relative to stage 2: fitted to the real stops
E2_SEGMENTS = (4561, 4661, 4761, 4861, 4961)
# The six games that start streaks of short games in a run with the stop and in none with no stop (B14).
NAMED = (3332, 3384, 3750, 3774, 3850, 4107)

_GAMES = {}


def games(path, opt):
    """b13lib's games of a file, read once."""
    if path not in _GAMES:
        _GAMES[path] = games_of(path, opt)
    return _GAMES[path]


def model_cumulative(line):
    """The model's cost of rounds 1 to R, summed from round 0.  A trajectory plays its rounds at stage 0, then at
    stage 1, then at stage 2 (`stage_rounds` says how many at each), and a round costs the mean over the trajectories
    of the cost of the stage each is at.  Only the proportions between the rounds of a stretch are used."""
    rows = line["stage_rounds"]
    cum = [0.0]
    for r in range(1, line["rounds"] + 1):
        cost = sum(STAGE_COST[0 if r <= s0 else 1 if r <= s0 + s1 else 2] for s0, s1, _ in rows)
        cum.append(cum[-1] + cost / len(rows))
    return cum


def gains_of(line):
    """The rounds with a gain and the score they reached, from round 0 (a start that is heavier than the first)."""
    return [(i["round"], i["score"]) for i in line["improvements"]]


def below(line):
    """The moves for n − 1 that a game started from, by their score and digest (None if it started from none)."""
    prev = line.get("prev")
    return None if prev is None else (prev["score"], prev["moves_digest"])


def agreeing_ends(line, others):
    """(rounds, work) at the end of each of `others` (lines of the same n) that began from the same moves as `line` and
    has its gains up to its own end, so that the work it recorded at its end is the work of `line` at that round."""
    mine, found = gains_of(line), {}
    for other in others:
        if other["method"] != "search" or other.get("unseeded") or not 0 < other["rounds"] < line["rounds"]:
            continue
        if other["start"] != line["start"] or below(other) != below(line):
            continue
        if gains_of(other) == [g for g in mine if g[0] <= other["rounds"]]:
            found[other["rounds"]] = other["work"]
    return found


@dataclass(frozen=True)
class Rule:
    """A stop rule, asked after each round r once the work reaches `gate`: end the rounds if the growth is from `lo`
    to `hi`, the last `quiet` rounds raised nothing, and (with `survivor`) no survivor of a game below scores within
    that many points of the start."""

    name: str
    gate: int = LEVEL1_BUDGET
    lo: int = -25
    hi: int = 25
    quiet: int = 0
    survivor: int = None


class Play:
    """One searched game's seeded play (its line is the first for its n), with what a rule is asked about at each
    round.  `others` are lines of the same game in other runs, whose ends give the work at those rounds."""

    def __init__(self, game, bounds, opt, data_set, others=()):
        line = game.played
        self.data_set, self.n, self.line = data_set, line["n"], line
        self.bound = bounds[self.n]
        self.gap_below = gap_before(game, bounds)
        self.rounds, self.work, self.final = line["rounds"], line["work"], line["score"]
        self.budget = line["budget"]
        self.level = (self.budget // ROUND_WORK).bit_length() - 1
        self.opt = opt[self.n]
        gains = dict(gains_of(line))
        self.gain_rounds = sorted(r for r in gains if r > 0)
        anchors = {0: 0, **agreeing_ends(line, others)}
        anchors.update({i["round"]: i["work"] for i in line["improvements"] if i["round"] > 0})
        anchors[self.rounds] = self.work
        self.known = sorted(anchors)
        self._known_work = [anchors[r] for r in self.known]
        score, last, self.score, self.since = gains.get(0, line["start"]), 0, [], []
        for r in range(self.rounds + 1):
            if r in gains and r > 0:
                score, last = gains[r], r
            self.score.append(score)
            self.since.append(r - last)
        # the best survivor of a game below, less the start (E2's lines have none)
        survivors = line.get("survivor_scores")
        self.survivors_near = max(score for _, score in survivors) - line["start"] if survivors else None
        self._model = model_cumulative(line)
        self.work_after = [self._work_at(r) for r in range(self.rounds + 1)]

    def _work_at(self, r):
        """The work after round r: recorded if known, else between the known rounds around it, in proportion to the
        model's cost of the rounds, and below the budget, which every round but the last started under."""
        i = bisect.bisect_left(self.known, r)
        if self.known[i] == r:
            return self._known_work[i]
        (r0, w0), (r1, w1) = (self.known[i - 1], self._known_work[i - 1]), (self.known[i], self._known_work[i])
        cum = self._model
        return min(w0 + (w1 - w0) * (cum[r] - cum[r0]) / (cum[r1] - cum[r0]), self.budget - 1)

    def growth(self, r):
        """The growth of the gap at the score after round r."""
        return self.bound - self.score[r] - self.gap_below

    def last_gain(self):
        return self.gain_rounds[-1] if self.gain_rounds else 0

    def stop(self, rule):
        """The round after which `rule` ends the rounds, or None: it never asks, never says yes, or says it at the
        last round, which changes nothing."""
        if rule.survivor is not None:
            if self.survivors_near is None:
                raise ValueError(f"n={self.n}: the line has no survivor_scores")
            if self.survivors_near >= -rule.survivor:
                return None
        for r in range(1, self.rounds):
            if self.work_after[r] >= rule.gate and rule.lo <= self.growth(r) <= rule.hi and self.since[r] >= rule.quiet:
                return r
        return None

    def result(self, rule):
        """(round, work saved, points lost) of the game under `rule`; round None if the rule never stops it."""
        r = self.stop(rule)
        if r is None:
            return None, 0.0, 0
        return r, self.work - self.work_after[r], self.final - self.score[r]


def line_checks(play):
    """The problems of a play's numbers: the final score is that of the last gain (or the start), the work is not below
    the work of the last gain, and the growth recorded is the growth at the final score."""
    line, problems = play.line, []
    if play.score[-1] != play.final:
        problems.append(f"n={play.n}: score {play.final}, the gains say {play.score[-1]}")
    if line["improvements"] and line["improvements"][-1]["work"] > play.work:
        problems.append(f"n={play.n}: work {play.work} is below the last gain's")
    recorded = line.get("growth")
    if recorded is not None and recorded != play.growth(play.rounds):
        problems.append(f"n={play.n}: growth {recorded}, the gaps say {play.growth(play.rounds)}")
    return problems


@dataclass
class DataSet:
    """The seeded plays of a chain that can be simulated, by n, and the work of all its seeded plays."""

    name: str
    plays: dict
    seeded_work: int  # the seeded plays of every searched game, simulated or not
    all_work: int  # the work of both plays of every game
    others: int  # the games played twice whose kept line is the unseeded play: not simulated
    games: int  # the games of the chain, searched or not


def plays_of(path, name, opt, bounds, lo=None, hi=None, companions=()):
    """The data set of a file of lines over lo to hi; `companions` are other files of lines over the same games."""
    mine = games(path, opt)
    other_games = [games(p, opt) for p in companions if p != path]
    plays, seeded_work, all_work, others, count = {}, 0, 0, 0, 0
    for n in sorted(mine):
        if (lo is not None and n < lo) or (hi is not None and n > hi):
            continue
        count += 1
        line = mine[n].played
        all_work += line["work"] + (line["other"]["work"] if line.get("other") else 0)
        if line["method"] != "search":
            continue
        if line.get("unseeded"):
            others += 1
            seeded_work += line["other"]["work"]
            continue
        seeded_work += line["work"]
        plays[n] = Play(mine[n], bounds, opt, name, [g[n].played for g in other_games if n in g])
    return DataSet(name, plays, seeded_work, all_work, others, count)


def e2_path(old_effort, first):
    return os.path.join(E2, f"e{old_effort}-{first}.jsonl.gz")


def e2_plays(old_effort, opt, bounds, companions=(), other_efforts=True):
    """E2's chains of one old effort (level old effort − 1), 4561-5060, as one data set.  The companions of a
    segment are the files of the other efforts over it (unless `other_efforts` is false) and `companions`."""
    name = f"e{old_effort}"
    parts = []
    for first in E2_SEGMENTS:
        near = [e2_path(effort, first) for effort in range(1, 8) if other_efforts] + list(companions)
        parts.append(plays_of(e2_path(old_effort, first), name, opt, bounds, companions=near))
    plays = {n: p for part in parts for n, p in part.plays.items()}
    return DataSet(name, plays, sum(p.seeded_work for p in parts), sum(p.all_work for p in parts),
                   sum(p.others for p in parts), sum(p.games for p in parts))


@dataclass
class Totals:
    """What a rule does over a data set: the work it saves, and the games and points it loses."""

    games: int
    stopped: int
    saved: float
    seeded_work: int
    lost: int
    new_short: int
    points: int
    lost_ns: tuple

    @property
    def share(self):
        return self.saved / self.seeded_work


def totals(data, rule, sample=None):
    """The rule's totals over the plays of `data` (those of `sample`, a set of n, if given)."""
    stopped = saved = lost = new_short = points = 0
    lost_ns = []
    chosen = [p for n, p in data.plays.items() if sample is None or n in sample]
    for p in chosen:
        r, work, loss = p.result(rule)
        stopped += r is not None
        saved += work
        if loss > 0:
            lost += 1
            points += loss
            lost_ns.append(p.n)
            new_short += p.final == p.opt
    work = data.seeded_work if sample is None else sum(p.work for p in chosen)
    return Totals(len(chosen), stopped, saved, work, lost, new_short, points, tuple(lost_ns))
