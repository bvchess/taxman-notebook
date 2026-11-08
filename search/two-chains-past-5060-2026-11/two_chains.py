#!/usr/bin/env python3
"""Two chains past 5060: chain A (level 3, the stop on growth) against chain B (level 4, no stop), 2026-11-07/08.

Reads the lines of both chains (runs/), the timing check (timing/), the lines of B14 and E2 and the parity bound from
the notebook, and results/optimal.jsonl.gz of the main repository.  Prints, in this order:

  checks     every line of both chains against the options of its run;
  timing     the timing check before the run;
  part 1     per segment of 250 games over the games both chains have, who scores more, and the time;
  part 2     each streak start where the chains differ and its cause as the lines show it, and the games where A
             scores more;
  part 3     how late the gains come: the searched games whose last gain needs more work than a level's budget;
  part 4     the growth of the gap to the parity bound, proven games against the lines past 5060.

A game's line is the last line the file has for it, so a line that the repair wrote again counts.  A game is
*searched* when its method is `search`.  A game's *gap* is its bound (the parity bound) less its score, and its
*growth* the gap less the gap of the game below.  A *streak* is a run of consecutive games where the chains score
differently, and its *start* the first of them.

Usage: nice -n 19 python3 -I two_chains.py [--results PATH] > out.txt
"""

import argparse
import gzip
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SEARCH = os.path.dirname(HERE)
A_FILE = HERE + '/runs/a-l3.jsonl.gz'
B_FILE = HERE + '/runs/b-l4.to-7039.jsonl.gz'
TIMING = HERE + '/timing/'
PARITY = SEARCH + '/the-parity-bound-against-the-frame-bound-2026-10/parity_2_8191.jsonl.gz'
B14 = SEARCH + '/tuning-the-unsound-mode-on-a-long-chain-2026-11/'
E2 = SEARCH + '/the-datasheet-of-the-unsound-mode-2026-11/runs/'
RESULTS = HERE + '/../../../../results/optimal.jsonl.gz'

FIRST = 5061  # the first game past the proven ones
LAST_PROVEN = 5060
LAST_A, LAST_B = 8191, 7039
SEGMENT = 250
TOL = 25  # the stop's and the push's band
BELOW = 8  # the games below a game whose lines seed it (--back 8)


def budget(level):
    return (1 << level) * 65536


def read(path):
    with (gzip.open(path, 'rt') if path.endswith('.gz') else open(path)) as f:
        for line in f:
            yield json.loads(line)


def last_lines(*paths):
    games = {}
    for path in paths:
        for x in read(path):
            games[x['n']] = x
    return games


def show(header, rows):
    """Print a table: the first column left, the others right."""
    cells = [[str(c) for c in header]] + [[str(c) for c in row] for row in rows]
    widths = [max(len(row[i]) for row in cells) for i in range(len(header))]
    for row in cells:
        print('  '.join(c.ljust(w) if i == 0 else c.rjust(w) for i, (c, w) in enumerate(zip(row, widths))))
    print()


def pct(part, whole):
    return '%.1f' % (100 * part / whole) if whole else '-'


def share(part, whole):
    return '%d (%s%%)' % (part, pct(part, whole))


def segments(lo, hi, size=SEGMENT):
    return [(s, min(s + size - 1, hi)) for s in range(lo, hi + 1, size)]


def last_gain(x):
    """The round and the work of the last improvement a line's own play made (None if it made none)."""
    imp = x['improvements']
    return (imp[-1]['round'], imp[-1]['work']) if imp else None


def total_work(x):
    return x['work'] + (x['other']['work'] if x['other'] else 0)


# ---------------------------------------------------------------------------------------------------------------------
# The checks


def check_chain(name, raw, games, parity, level, stop, last):
    """Check every line of a chain against the options its run was given, and print the counts."""
    bad = {}

    def fail(key):
        bad[key] = bad.get(key, 0) + 1

    growth_checked = 0
    for x in raw:
        n = x['n']
        if not (x['unsound'] and x['build']['commit'].startswith('ecb4bc4') and not x['build']['dirty']):
            fail('unsound or build')
        if (x['effort'], x['budget']) != (level, budget(level)):
            fail('level')
        if (x['seed'], x['threads'], x['push_growth'], x['unseeded_every'], x['stop_growth']) != (1, 44, TOL, 0, stop):
            fail('options')
        if x['bound'] != parity[n] or x['score'] > x['bound']:
            fail('bound')
        if x['prev'] and x['prev']['source'] != ('table' if n == FIRST else 'run'):
            fail('prev source')
        if x['prev'] and x['growth'] is not None:
            growth_checked += 1
            if x['growth'] != (x['bound'] - x['score']) - (parity[n - 1] - x['prev']['score']):
                fail('growth')
    repaired = sum(1 for x in raw if x['repaired'])
    stopped, pushed = (sum(1 for x in games.values() if x[key]) for key in ('growth_stop', 'pushed'))
    print('%s: %d lines, %d games %d-%d, %d lines written again by the repair; stopped %d, pushed %d' % (
        name, len(raw), len(games), min(games), max(games), repaired, stopped, pushed))
    print('   contiguous: %s; lines = games + repaired lines: %s; growth checked on %d lines (those with a prev)' % (
        sorted(games) == list(range(FIRST, last + 1)), len(raw) == len(games) + repaired, growth_checked))
    print('   checks failed: %s' % (bad or 'none'))


def part_checks(raw_a, raw_b, a, b, parity):
    print('== Checks\n')
    check_chain('A', raw_a, a, parity, 3, TOL, LAST_A)
    check_chain('B', raw_b, b, parity, 4, None, LAST_B)
    common = sorted(set(a) & set(b))
    print('common games %d-%d: %d; methods differ on %d games\n' % (
        common[0], common[-1], len(common), sum(1 for n in common if a[n]['method'] != b[n]['method'])))


# ---------------------------------------------------------------------------------------------------------------------
# The timing check


def part_timing(a, b):
    print('== The timing check before the run (unseeded level 3, one game each, --threads 29, nice 19)\n')
    rows = []
    for n in (6000, 7000, 8000):
        text = open(TIMING + 'u3-%d.time' % n).read()
        wall = re.search(r'Elapsed .*: (\d+):([\d.]+)', text)
        user = float(re.search(r'User time \(seconds\): ([\d.]+)', text).group(1))
        cpu = int(re.search(r'Percent of CPU this job got: (\d+)%', text).group(1))
        x = next(read(TIMING + 'u3-%d.jsonl.gz' % n))
        row = [n, int(wall.group(1)) * 60 + float(wall.group(2)), user, cpu, x['rounds'], x['work'], x['score']]
        for chain in (a, b):
            if n in chain:
                lo = FIRST + (n - FIRST) // SEGMENT * SEGMENT
                searched = [chain[m]['seconds'] for m in range(lo, min(lo + SEGMENT, max(chain) + 1))
                            if chain[m]['method'] == 'search' and chain[m]['rounds']]
                row += [chain[n]['score'] - x['score'], '%.1f' % chain[n]['seconds'],
                        '%.1f' % statistics.mean(searched)]
            else:
                row += ['-', '-', '-']
        rows.append(row)
    show(['n', 'wall s', 'user s', 'CPU %', 'rounds', 'work', 'score',
          'A-score', 'A s (game)', 'A s (searched, segment)', 'B-score', 'B s (game)', 'B s (searched, segment)'], rows)
    print('A-score and B-score: the chain\'s line less the unseeded game\'s score.  The seconds of the chains are on\n'
          '44 threads beside the other chain, the timing check\'s on 29 threads before the chains started.  The\n'
          'segment is the 250 games of part 1 that hold n; its seconds are the mean of its searched games that ran\n'
          'rounds.\n')


# ---------------------------------------------------------------------------------------------------------------------
# Part 1: the games where one chain scores more


def runs_of(diff):
    """The maximal runs of consecutive games with a nonzero difference, as (first, last)."""
    runs, n = [], min(diff)
    while n <= max(diff):
        if diff.get(n):
            m = n
            while diff.get(m + 1):
                m += 1
            runs.append((n, m))
            n = m + 1
        else:
            n += 1
    return runs


def part1(a, b, common, diff):
    print('== Part 1: A (level 3, stop) against B (level 4, no stop) on %d-%d, %d games\n' % (
        common[0], common[-1], len(common)))
    starts = runs_of(diff)
    ranges = segments(common[0], common[-1]) + [(common[0], common[-1])]
    rows = []
    for lo, hi in ranges:
        seg = [n for n in common if lo <= n <= hi]
        bh = [n for n in seg if diff[n] > 0]
        ah = [n for n in seg if diff[n] < 0]
        st = [s for s, _ in starts if lo <= s <= hi]
        rows.append(['%d-%d' % (lo, hi), len(seg), len(bh), pct(len(bh), len(seg)), len(ah), pct(len(ah), len(seg)),
                     sum(1 for s in st if diff[s] > 0), sum(1 for s in st if diff[s] < 0),
                     sum(diff[n] for n in bh), sum(-diff[n] for n in ah)])
    show(['segment', 'games', 'B>A', '%', 'A>B', '%', 'starts B>A', 'starts A>B', 'points B>A', 'points A>B'], rows)
    print('A streak start is the first game of a run of games where the chains differ; a start is B>A or A>B by the\n'
          'sign of the difference at its first game.  Points: the sum of the differences over the games.\n')

    rows = []
    for lo, hi in ranges:
        seg = [n for n in common if lo <= n <= hi]
        srch = [n for n in seg if a[n]['method'] == 'search']
        sa, sb = sum(a[n]['seconds'] for n in seg), sum(b[n]['seconds'] for n in seg)
        stopped = sum(1 for n in seg if a[n]['growth_stop'])
        pa, pb = sum(1 for n in seg if a[n]['pushed']), sum(1 for n in seg if b[n]['pushed'])
        rows.append(['%d-%d' % (lo, hi), len(srch), '%.1f' % (sa / len(seg)), '%.1f' % (sb / len(seg)),
                     '%.2f' % (sb / sa), '%.3f' % (sum(total_work(a[n]) for n in seg) / len(seg) / 1e6),
                     '%.3f' % (sum(total_work(b[n]) for n in seg) / len(seg) / 1e6),
                     share(stopped, len(srch)), share(pa, len(srch)), share(pb, len(srch)),
                     '%.1f' % (sum(a[n]['seconds'] for n in srch) / len(srch)),
                     '%.1f' % (sum(b[n]['seconds'] for n in srch) / len(srch))])
    show(['segment', 'searched', 'A s/game', 'B s/game', 'B/A', 'A M work/game', 'B M work/game', 'A stopped',
          'A pushed', 'B pushed', 'A s/searched', 'B s/searched'], rows)
    print('Percentages of stopped and pushed games are of the searched games.  Work includes the unseeded play of a\n'
          'pushed game.')
    print('A: %d games, %.2f hours of game seconds (%.2f on %d-%d); B on %d-%d: %.2f hours.\n' % (
        len(a), sum(x['seconds'] for x in a.values()) / 3600, sum(a[n]['seconds'] for n in common) / 3600,
        common[0], common[-1], common[0], common[-1], sum(x['seconds'] for x in b.values()) / 3600))
    only_a = range(LAST_B + 1, LAST_A + 1)
    print('Games %d-%d that only A played: %d, A stopped %d, pushed %d, %.1f s/game\n' % (
        only_a[0], only_a[-1], len(only_a), sum(1 for n in only_a if a[n]['growth_stop']),
        sum(1 for n in only_a if a[n]['pushed']), sum(a[n]['seconds'] for n in only_a) / len(only_a)))


# ---------------------------------------------------------------------------------------------------------------------
# Part 2: the streak starts and their causes


def play(x, unseeded):
    """The seeded (unseeded False) or the unseeded play of a line: rounds, work, whether the stop ended it, last gain.

    The line is the play it came from; `other` has the rounds and the work of the other play, and no more."""
    if x['unseeded'] == unseeded:
        return {'rounds': x['rounds'], 'work': x['work'], 'stopped': bool(x['growth_stop']), 'gain': last_gain(x)}
    if x['other'] is None:
        return None
    return {'rounds': x['other']['rounds'], 'work': x['other']['work'], 'stopped': False, 'gain': None}


def cause(x, y, high, level_low):
    """Why the chain whose line is `high` ('A' or 'B') scores more at a streak start, as the lines show it.

    The play that wrote the higher line made its last gain in some round.  If the lower chain's same play ran that
    round, it missed the gain; if not, its rounds ended by the stop or at the budget of its level."""
    h, l = (x, y) if high == 'A' else (y, x)
    hp, lp = play(h, h['unseeded']), play(l, h['unseeded'])
    if lp is None:
        return 'the other did not play it', lp
    if hp['gain'] is None:
        return 'start', lp
    if hp['gain'][0] <= lp['rounds']:
        return 'missed', lp
    if lp['stopped']:
        return 'stop', lp
    return ('budget' if lp['work'] >= budget(level_low) else 'ended otherwise'), lp


def played_at(chain, n):
    """The game whose play made the line of n: n itself, or, for a line the repair raised, the game above it."""
    while chain[n]['repaired']:
        n = chain[n]['repaired']['from']
    return n


def same_seeds(x, y):
    """Whether the seeded plays of two lines of a game began from the same seeds: the line below, the trajectories
    and the scores of the survivors.  None if either line is the unseeded play's, which does not record them."""
    if x['unseeded'] or y['unseeded'] or not x['prev'] or not y['prev']:
        return None
    return all(x['prev']['moves_digest'] == y['prev']['moves_digest'] and x[key] == y[key]
               for key in ('trajectories', 'survivor_scores'))


def word(flag):
    return '-' if flag is None else ('yes' if flag else 'no')


def describe(x):
    """A line's start, score and play, and the score of the other play of a game played twice."""
    kind = lambda unseeded: 'unseeded' if unseeded else 'seeded'
    other = ''
    if x['other']:
        other = '; the %s play %d in %d rounds' % (kind(x['other']['unseeded']), x['other']['score'],
                                                   x['other']['rounds'])
    return 'line below %s, start %s, score %d (%s play, %d rounds%s)' % (
        x['prev']['score'] if x['prev'] else '-', x['start'], x['score'], kind(x['unseeded']), x['rounds'], other)


def part2(a, b, diff):
    runs = runs_of(diff)
    print('== Part 2: the %d streak starts\n' % len(runs))
    rows, by_cause = [], {}
    for s, e in runs:
        high = 'B' if diff[s] > 0 else 'A'
        chain = b if high == 'B' else a
        t = played_at(chain, s)  # the cause is read at the game that played the gain
        h = chain[t]
        c, lp = cause(a[t], b[t], high, 3 if high == 'B' else 4)
        alike = all(diff.get(m, 0) == 0 for m in range(s - BELOW, s))
        seeds = same_seeds(a[t], b[t])
        points = sum(abs(diff[m]) for m in range(s, e + 1))
        by_cause.setdefault(c, []).append((s, t, abs(diff[s]), e - s + 1, points, h['unseeded'], alike, seeds))
        rows.append([s, high, '%+d' % diff[s], e - s + 1, points, t if t != s else '-',
                     'unseeded' if h['unseeded'] else 'seeded', lp['rounds'], lp['work'],
                     'stop' if lp['stopped'] else '-', 'pushed' if h['pushed'] else '-',
                     '%d, %d' % last_gain(h) if last_gain(h) else '-', word(alike), word(seeds), c])
    show(['start', 'higher', 'diff (B-A)', 'games', 'points', 'played at', "higher's play", 'lower rounds',
          'lower work', 'lower stop', 'higher pushed', "higher's last gain (round, work)", '8 below alike',
          'same seeds', 'cause'], rows)
    print('The lower chain\'s rounds and work are those of its play of the same kind as the play that wrote the\n'
          'higher chain\'s line.  Points: the sum of |B - A| over the streak.  8 below alike: the chains scored the\n'
          'same on the 8 games below the start.  Same seeds: the seeded plays began from the same line below,\n'
          'trajectories and survivor scores (- for a line that is the unseeded play\'s).  Played at: for a line the\n'
          'repair raised, the game above it whose play made the gain, where the cause is read.\n')
    for c, items in by_cause.items():
        print('%-8s %2d starts: %3d points at the starts, %3d games and %4d points in their streaks; in the unseeded '
              'play of a pushed game %d; 8 below alike in %d; same seeds in %d, different in %d' % (
                  c, len(items), sum(i[2] for i in items), sum(i[3] for i in items), sum(i[4] for i in items),
                  sum(1 for i in items if i[5]), sum(1 for i in items if i[6]),
                  sum(1 for i in items if i[7]), sum(1 for i in items if i[7] is False)))
        print('         ' + ' '.join(str(i[0]) for i in items))
    print()
    stops = [i[1] for i in by_cause.get('stop', [])]
    quiet = [n for n in stops if a[n]['rounds'] - (last_gain(a[n]) or (0,))[0] >= 4]
    print('Of the %d starts the stop made, the last 4 rounds before the stop (the start is round 0) raised nothing in '
          '%d: %s' % (len(stops), len(quiet), ' '.join(map(str, quiet))))
    print('A\'s rounds at the stop: %s' % ' '.join('%d:%d' % (n, a[n]['rounds']) for n in stops))
    for s, e in runs:
        if played_at(b, s) != s:
            print('The repair raised B\'s line of %d from game %d: A scored %d, B before the repair %d, B after %d' % (
                s, b[s]['repaired']['from'], a[s]['score'], b[s]['repaired']['was'], b[s]['score']))
    lows = [(s, a[s]) for s, _ in runs if diff[s] > 0]
    print('Starts where A scores less: %d, of which A\'s game was pushed %d (%s), stopped %d\n' % (
        len(lows), sum(1 for _, x in lows if x['pushed']), ' '.join(str(s) for s, x in lows if x['pushed']),
        sum(1 for _, x in lows if x['growth_stop'])))

    print('Episodes where A scores more (maximal runs of games with A > B, inside a streak or at its start):\n')
    rows, firsts = [], []
    games = sorted(diff)
    n = games[0]
    while n <= games[-1]:
        if diff[n] < 0:
            m = n
            while diff.get(m + 1, 0) < 0:
                m += 1
            x, y = a[n], b[n]
            c, lp = cause(x, y, 'A', 4)
            rows.append([n, m, m - n + 1, sum(-diff[k] for k in range(n, m + 1)), '%+d' % diff.get(n - 1, 0),
                         '%+d' % diff[n], '%d, %d' % last_gain(x) if last_gain(x) else '-', x['rounds'], y['rounds'],
                         'unseeded' if y['unseeded'] else 'seeded',
                         word(all(diff.get(k, 0) == 0 for k in range(n - BELOW, n))), word(same_seeds(x, y)), c])
            firsts.append(n)
            n = m + 1
        else:
            n += 1
    show(['first', 'last', 'games', 'points', 'B-A below', 'B-A at first', "A's last gain (round, work)", 'A rounds',
          'B rounds', "B's play", '8 below alike', 'same seeds', 'cause'], rows)
    print('An episode begins at a game below which B led, or had led within 8 games, and where A gained more.  The\n'
          'cause is read as for the other starts, with A the higher chain and B the lower; B\'s play is the kind that\n'
          'wrote B\'s line.  The first game of each, as the lines record it:\n')
    for n in firsts:
        print('%d  A: %s' % (n, describe(a[n])))
        print('%s  B: %s' % (' ' * len(str(n)), describe(b[n])))
    print()

    # The rounds of A are the first rounds of B when the seeds are the same.
    same, bad, others = 0, [], 0
    for n in sorted(set(a) & set(b)):
        x, y = a[n], b[n]
        if x['method'] != 'search' or y['method'] != 'search':
            continue
        if not same_seeds(x, y):
            others += same_seeds(x, y) is False
            continue
        same += 1
        ia = [(i['round'], i['work'], i['score']) for i in x['improvements']]
        ib = [(i['round'], i['work'], i['score']) for i in y['improvements'] if i['round'] <= x['rounds']]
        if ia != ib:
            bad.append(n)
    print('Seeded plays of searched games with the same seeds in both chains: %d.  B\'s improvements in the rounds '
          'A ran differ from A\'s in %d: %s.  With different seeds: %d games\n' % (
              same, len(bad), ' '.join(map(str, bad)), others))
    print('Games in the %d runs: %d (B>A %d, A>B %d)\n' % (len(runs), sum(1 for n in diff if diff[n]),
                                                           sum(1 for n in diff if diff[n] > 0),
                                                           sum(1 for n in diff if diff[n] < 0)))


# ---------------------------------------------------------------------------------------------------------------------
# Part 3: how late the gains come


def late_gains(label, games, lo, hi):
    """A table row: the searched games of lo..hi whose last gain needs more work than level 2's and 3's budgets."""
    seg = [games[n] for n in range(lo, hi + 1) if n in games and games[n]['method'] == 'search'
           and not games[n].get('at_ceiling')]
    last = [max([i['work'] for i in x['improvements']] or [0]) for x in seg]
    gained = [w for w in last if w > 0]
    late = [sum(w > budget(level) for w in last) for level in (2, 3)]
    rounds = [x['rounds'] for x in seg if x['rounds']]
    return [label, '%d-%d' % (lo, hi), len(seg), len(gained), share(late[0], len(seg)), share(late[1], len(seg)),
            pct(late[1], len(gained)), '%g' % statistics.median(rounds), '%.0f' % statistics.median(
                x['work'] / x['rounds'] for x in seg if x['rounds']),
            '%g' % statistics.median(x['improvements'][-1]['round'] for x in seg if x['improvements'])]


LATE_HEADER = ['chain', 'games', 'searched', 'gained', 'last gain > level 2 budget', 'last gain > level 3 budget',
               '% of gained > L3', 'median rounds', 'median work/round', 'median round of last gain']


def part3(a, b):
    print('== Part 3: the searched games (not stopped at the ceiling) whose last gain needs more work than level 2\'s '
          '(%d) and level 3\'s (%d) budget\n' % (budget(2), budget(3)))
    sets = {'E2 level 4, no stop': last_lines(*[E2 + 'e5-%d.jsonl.gz' % lo for lo in (4561, 4661, 4761, 4861, 4961)]),
            'E2 level 3, no stop': last_lines(*[E2 + 'e4-%d.jsonl.gz' % lo for lo in (4561, 4661, 4761, 4861, 4961)]),
            'B14 level 4, stop': last_lines(B14 + 'part1/l4.jsonl.gz'),
            'B14 level 3, stop': last_lines(B14 + 'part1/l3.jsonl.gz'),
            'B level 4, no stop': b, 'A level 3, stop': a}
    for name, games in sets.items():
        print('%-20s games %d-%d, budgets %s, stop_growth %s' % (
            name, min(games), max(games), sorted({x['budget'] for x in games.values()}),
            sorted({str(x.get('stop_growth')) for x in games.values()})))
    print()
    print('Level 4 chains, by segment of 250 games (B14 from 4061 so that the segments of 4561-5060 are E2\'s):\n')
    rows = []
    for name, lo, hi in (('B14 level 4, stop', 4061, 5060), ('E2 level 4, no stop', 4561, 5060),
                         ('B level 4, no stop', FIRST, LAST_B)):
        step = SEGMENT
        for s in range(lo, hi + 1, step):
            rows.append(late_gains(name, sets[name], s, min(s + step - 1, hi)))
    show(LATE_HEADER, rows)
    print('Level 4 chains on the same games and in total:\n')
    rows = [late_gains(name, sets[name], lo, hi) for name, lo, hi in (
        ('B14 level 4, stop', 4561, 5060), ('E2 level 4, no stop', 4561, 5060), ('B level 4, no stop', FIRST, LAST_B),
        ('B level 4, no stop', FIRST, 6060), ('B level 4, no stop', 6061, LAST_B))]
    show(LATE_HEADER, rows)
    print('Level 3 chains: a gain recorded above level 3\'s budget can only be that of the round that reaches it, the\n'
          'last one, so their share above level 3\'s budget is the share that level 4 chains have with no more work.\n')
    rows = [late_gains(name, sets[name], lo, hi) for name, lo, hi in (
        ('B14 level 3, stop', 4561, 5060), ('E2 level 3, no stop', 4561, 5060), ('A level 3, stop', FIRST, LAST_B),
        ('A level 3, stop', FIRST, 6060), ('A level 3, stop', 6061, LAST_B))]
    show(LATE_HEADER, rows)
    rows = [late_gains('A level 3, stop', a, lo, hi) for lo, hi in segments(FIRST, LAST_B)]
    show(LATE_HEADER, rows)
    print('B searched lines raised by the repair (their improvements are those of the play, not of the repair): %d\n'
          % sum(1 for x in b.values() if x['repaired'] and x['method'] == 'search'))
    l3, l4 = sets['B14 level 3, stop'], sets['B14 level 4, stop']
    print('B14 level 3 against level 4 on %d-%d: scores differ on %d games, moves on %d; points short of the better: '
          '%d and %d\n' % (min(l3), max(l3), sum(1 for n in l3 if l3[n]['score'] != l4[n]['score']),
                           sum(1 for n in l3 if l3[n]['moves'] != l4[n]['moves']),
                           sum(max(l3[n]['score'], l4[n]['score']) - l3[n]['score'] for n in l3),
                           sum(max(l3[n]['score'], l4[n]['score']) - l4[n]['score'] for n in l3)))


# ---------------------------------------------------------------------------------------------------------------------
# Part 4: the parity bound


def tails(label, ns, g):
    """A row of the tails of the growth g over the games ns, per 100: in points, and as a share of n."""
    gs = [g(n) for n in ns]
    rel = [abs(g(n)) / n for n in ns]
    per100 = lambda hits: '%.1f' % (100 * sum(1 for h in hits if h) / len(gs))
    return [label, len(gs)] + [per100([abs(v) > t for v in gs]) for t in (100, 200, 400)] + \
        [per100([v > t for v in rel]) for t in (0.02, 0.04, 0.08)] + [min(gs), max(gs), '%.3f' % max(rel)]


TAIL_HEADER = ['games', 'searched', '|g|>100', '>200', '>400', '|g|/n>.02', '>.04', '>.08', 'min g', 'max g',
               'max |g|/n']


def part4(a, b, opt, parity, proven_method):
    print('== Part 4: the growth of the gap to the parity bound\n')
    series = {'A': {n: x['score'] for n, x in a.items()},
              'B': {n: x['score'] for n, x in b.items()}}
    series['the better of A and B'] = {n: max(a[n]['score'], b[n]['score']) if n in b else a[n]['score'] for n in a}
    method = {n: x['method'] for n, x in a.items()}
    method.update(proven_method)

    def growth_of(score):
        full = dict(opt)
        full.update(score)
        return lambda n: (parity[n] - full[n]) - (parity[n - 1] - full[n - 1])

    better = series['the better of A and B']
    g_better, g_opt = growth_of(better), growth_of({})
    searched = lambda lo, hi: [n for n in range(lo, hi + 1) if method.get(n) == 'search']

    rows = [tails('proven %d-%d' % (lo, hi), searched(lo, hi), g_opt) for lo, hi in
            ((3001, 4000), (4001, LAST_PROVEN), (3001, LAST_PROVEN))]
    for lo, hi in ((5061, 6060), (6061, 7060), (7061, 8191), (5061, 8191)):
        rows.append(tails('better of A and B %d-%d' % (lo, hi), searched(lo, hi), g_better))
    print('The tails of the growth, per 100 searched games.  Proven: opt(n) (results/optimal.jsonl.gz), the searched\n'
          'games of 3001-5060, the games whose method B14\'s lines give.  Past 5060: the better of the two chains\'\n'
          'scores, and A\'s alone from 7040 on (B stopped at 7039).\n')
    show(TAIL_HEADER, rows)

    proven_ns, past = searched(3001, 5060), searched(FIRST, LAST_A)
    top = max(g_opt(n) for n in proven_ns)
    top_rel = max(g_opt(n) / n for n in proven_ns)
    above = sorted((n for n in past if g_better(n) > top), key=lambda n: -g_better(n))
    above_rel = [n for n in past if g_better(n) / n > top_rel]
    top_all = max(g_opt(n) for n in range(1001, LAST_PROVEN + 1))
    print('Largest growth of a proven searched game, 3001-5060: %d (n = %d), as a share of n %.4f; of any proven game '
          '1001-5060: %d' % (top, max(proven_ns, key=g_opt), top_rel, top_all))
    print('Searched games past 5060 above %d points: %d of %d; above %.4f of n: %d (%s)' % (
        top, len(above), len(past), top_rel, len(above_rel), ' '.join(map(str, above_rel))))
    for n in above:
        nxt = [(m, g_better(m)) for m in range(n + 1, min(n + 61, LAST_A + 1)) if g_better(m) < -g_better(n) / 2][:1]
        print('   %d  growth %+5d  (%.4f of n)  A %d  B %s  next drop of half as much within 60 games: %s' % (
            n, g_better(n), g_better(n) / n, a[n]['score'], b[n]['score'] if n in b else '-', nxt or 'none'))
    print()

    # The quantiles of |growth| by window of 500 games from 1001 on, over the games whose growth is not 0.
    windows = [(lo, lo + 499) for lo in range(1001, 4501, 500)] + [(4501, LAST_PROVEN)] + \
              [(lo, lo + 499) for lo in range(FIRST, 7561, 500)] + [(7561, LAST_A)]
    rows = []
    for lo, hi in windows:
        g = g_opt if hi <= LAST_PROVEN else g_better
        absg = [abs(g(n)) for n in range(lo, hi + 1) if g(n)]
        rel = [abs(g(n)) / n for n in range(lo, hi + 1) if g(n)]
        qa, qr = statistics.quantiles(absg, n=100), statistics.quantiles(rel, n=100)
        rows.append(['%d-%d' % (lo, hi), 'proven' if hi <= LAST_PROVEN else ('A, B' if hi <= 7060 else 'A'),
                     hi - lo + 1, len(absg), '%.0f' % qa[49], '%.0f' % qa[89], '%.0f' % qa[98], max(absg),
                     '%.4f' % qr[49], '%.4f' % qr[89], '%.4f' % qr[98], '%.4f' % max(rel)])
    print('Quantiles of |growth| by window of 500 games (the last window of each part is longer), over the games '
          'whose growth is not 0.\n')
    show(['window', 'scores', 'games', 'growth != 0', 'p50', 'p90', 'p99', 'max', 'p50/n', 'p90/n', 'p99/n', 'max/n'],
         rows)
    print('Proven games of 3001-5060 with a growth that is not 0 and a method that is not search: %d of %d\n' % (
        sum(1 for n in range(3001, LAST_PROVEN + 1) if g_opt(n) and method.get(n) != 'search'),
        sum(1 for n in range(3001, LAST_PROVEN + 1) if g_opt(n))))

    # The sensitivity: A, B and the better of the two on the games all three have.
    ns_all = searched(FIRST, LAST_B)
    rows, below, g_of = [], {}, {}
    for name, score in series.items():
        g_of[name] = growth_of({n: score[n] for n in range(FIRST, LAST_B + 1)})
        rows.append(tails(name, ns_all, g_of[name]))
        below[name] = [n for n in range(FIRST, LAST_B + 1) if score[n] < better[n]]
    print('Sensitivity on %d-%d: the tails for A, B and the better of the two.\n' % (FIRST, LAST_B))
    show(['scores'] + TAIL_HEADER[1:], rows)
    for name in ('A', 'B'):
        print('%s is below the better of A and B on %d games (%d points)' % (
            name, len(below[name]), sum(better[n] - series[name][n] for n in below[name])))
    print()
    g_a = g_of['A']
    starts_a = [s for s, _ in runs_of({n: b[n]['score'] - a[n]['score'] for n in range(FIRST, LAST_B + 1)})
                if b[s]['score'] > a[s]['score']]
    print('Of the %d games where A is below B, A\'s growth is above +%d on %d, and above +%d (the proven games\' '
          'largest) on %d' % (len(below['A']), TOL, sum(1 for n in below['A'] if g_a(n) > TOL), top,
                              sum(1 for n in below['A'] if g_a(n) > top)))
    print('At the %d streak starts where A scores less, A\'s growth: median %+d, minimum %+d, maximum %+d; above +%d '
          'on %d; the median of A\'s growth over all searched games %+d\n' % (
              len(starts_a), statistics.median(g_a(s) for s in starts_a), min(g_a(s) for s in starts_a),
              max(g_a(s) for s in starts_a), TOL, sum(1 for s in starts_a if g_a(s) > TOL),
              statistics.median(g_a(n) for n in ns_all)))


# ---------------------------------------------------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--results', default=RESULTS, help='results/optimal.jsonl.gz of the main repository')
    args = parser.parse_args()

    raw_a, raw_b = list(read(A_FILE)), list(read(B_FILE))
    a, b = {x['n']: x for x in raw_a}, {x['n']: x for x in raw_b}
    parity = {x['n']: x['parity'] for x in read(PARITY)}
    opt = {x['n']: x['score'] for x in read(args.results)}
    common = sorted(set(a) & set(b))
    diff = {n: b[n]['score'] - a[n]['score'] for n in common}
    proven_method = {}
    for path in (B14 + 'part2/h-choice-l3.jsonl.gz', B14 + 'part1/l3.jsonl.gz'):
        proven_method.update({n: x['method'] for n, x in last_lines(path).items()})

    part_checks(raw_a, raw_b, a, b, parity)
    part_timing(a, b)
    part1(a, b, common, diff)
    part2(a, b, diff)
    part3(a, b)
    part4(a, b, opt, parity, proven_method)


if __name__ == '__main__':
    main()
