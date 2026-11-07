#!/usr/bin/env python3
"""A tilted share: free each promotion with a probability that follows where the drops of the steps lie (section 6).

    nice -n 19 python3 -I tilt.py P1_ENTRY > tilt-out.txt

The weights are fitted on the searched steps of 1001-3440 (the drops D against the seed from n - 1, section 1) and
tested on data the fit never saw: the steps of 3441-5060, the pilot's stuck sets and its short starts (starts.jsonl).
A promotion x of game n has three features: its size x/n in one of BINS bins from 1/4 to 1/2 (the few below n/4 in the
first), whether it lies in the frame where n arrives (the layer of n at an odd n, of n/2 at an even n), and whether
n's largest prime divides it.  Its
weight is the product, over the features, of the share of the drops with x's value over the share of the seed's
promotions with it.  A neighborhood frees x with probability min(1, q w(x)), q set so that the expected share freed is
the target, and fixes the rest; it holds the optimal set when it frees every drop, with probability the product of
the drops' probabilities.  The uniform share frees every promotion with the same probability, the target.
"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from board import Tables, load_results, seed_of  # noqa: E402  (board.py sits beside this script)

BINS = 10
FIT = (1001, 3440)
TEST = (3441, 5060)
TARGETS = (0.2, 0.3, 0.4, 0.5)
ROUND = 64


def features(t, x, n):
    b = min(BINS - 1, max(0, int((x / n - 0.25) / 0.25 * BINS)))
    arrival = t.omega[x] == (t.omega[n] if n % 2 else t.omega[n // 2])
    big = x % t.largest_prime(n) == 0
    return b, arrival, big


def fit(t, games, lo, hi):
    """The weights of each feature's values: the share of the drops with the value over the share of the seed's."""
    drops = [{}, {}, {}]
    seeds = [{}, {}, {}]
    nd = ns = 0
    for n in range(lo, hi + 1):
        if games[n]['method'] != 'search':
            continue
        seed = seed_of(games, n)
        d = seed - games[n]['promotions']
        for x in seed:
            f = features(t, x, n)
            for i in range(3):
                seeds[i][f[i]] = seeds[i].get(f[i], 0) + 1
                if x in d:
                    drops[i][f[i]] = drops[i].get(f[i], 0) + 1
        nd += len(d)
        ns += len(seed)
    return [{v: (drops[i].get(v, 0) + 1) / (nd + 1) / (c / ns) for v, c in seeds[i].items()} for i in range(3)]


def weight(t, w, x, n):
    f = features(t, x, n)
    out = 1.0
    for i in range(3):
        out *= w[i].get(f[i], 1.0)
    return out


def chance(t, w, x_set, d, n, target, use=(0, 1, 2)):
    """The chance that the tilted share frees every drop, and that the uniform share does, at one expected share."""
    ws = {}
    for x in x_set:
        f = features(t, x, n)
        v = 1.0
        for i in use:
            v *= w[i].get(f[i], 1.0)
        ws[x] = v
    want = target * len(x_set)
    lo, hi = 0.0, 1e6
    for _ in range(100):
        q = (lo + hi) / 2
        if sum(min(1.0, q * v) for v in ws.values()) < want:
            lo = q
        else:
            hi = q
    p = 1.0
    for x in d:
        p *= min(1.0, hi * ws[x])
    return p, target ** len(d)


def main():
    p1 = sys.argv[1]
    games = load_results()
    t = Tables(max(games))
    w = fit(t, games, *FIT)
    print(f'Weights fitted on the searched steps of {FIT[0]}-{FIT[1]}:')
    print('    size x/n from ' + ', '.join(f'{0.25 + 0.025 * b:.3f}: {w[0][b]:.2f}' for b in sorted(w[0])))
    print(f'    in the frame where n arrives: {w[1].get(True, 0):.2f}, not: {w[1].get(False, 0):.2f}')
    print(f"    a multiple of n's largest prime: {w[2].get(True, 0):.2f}, not: {w[2].get(False, 0):.2f}")

    cases = []
    for n in range(TEST[0], TEST[1] + 1):
        if games[n]['method'] != 'search':
            continue
        seed = seed_of(games, n)
        d = seed - games[n]['promotions']
        if len(d) >= 2:
            cases.append(('step', n, seed, d))
    seen = set()
    for s in (1, 2):
        with open(f'{p1}/seed-{s}.jsonl') as f:
            for line in f:
                rec = json.loads(line)
                if rec['stop_at_known']['round'] is None:
                    x = frozenset(rec['promotions'])
                    if (rec['n'], x) not in seen:
                        seen.add((rec['n'], x))
                        cases.append(('stuck', rec['n'], x, x - games[rec['n']]['promotions']))
    with open(os.path.join(HERE, 'starts.jsonl')) as f:
        for line in f:
            rec = json.loads(line)
            x = frozenset(rec['promotions'])
            d = x - games[rec['n']]['promotions']
            cases.append(('start', rec['n'], x, d))

    print('\nThe chance that one neighborhood frees every drop, tilted against uniform at the same expected share '
          '(the geometric mean of their ratio, and the mean chance of each), and the features used:\n')
    print('| incumbents | cases | share | features | tilted, mean | uniform, mean | ratio, geometric mean | '
          'tilted ahead in |')
    print('|---|---|---|---|---|---|---|---|')
    for kind in ('step', 'stuck', 'start'):
        sel = [c for c in cases if c[0] == kind and c[3]]
        for target in TARGETS:
            for use, label in [((0,), 'size'), ((0, 1, 2), 'all three')]:
                tilted, uniform, logs, ahead = [], [], [], 0
                for _, n, x, d in sel:
                    pt, pu = chance(t, w, x, d, n, target, use)
                    tilted.append(pt)
                    uniform.append(pu)
                    logs.append((pt / pu) if pu > 0 else float('inf'))
                    ahead += pt > pu
                gm = statistics.geometric_mean([v for v in logs if v > 0]) if all(v > 0 for v in logs) else 0
                print(f'| {kind} | {len(sel)} | {target} | {label} | {statistics.mean(tilted):.2e} | '
                      f'{statistics.mean(uniform):.2e} | {gm:.1f} | {ahead} |')

    print('\nThe stuck sets one by one, the size alone: the chance for one neighborhood and for a round of 64, at an '
          'expected share of 0.2 and 0.4\n')
    print('| n | D | 0.2: tilted, uniform | round: tilted, uniform | 0.4: tilted, uniform | round: tilted, uniform |')
    print('|---|---|---|---|---|---|')
    for kind, n, x, d in cases:
        if kind != 'stuck':
            continue
        cells = []
        for target in (0.2, 0.4):
            pt, pu = chance(t, w, x, d, n, target, (0,))
            cells.append(f'{pt:.1e}, {pu:.1e} | {1 - (1 - pt) ** ROUND:.3f}, {1 - (1 - pu) ** ROUND:.3f}')
        print(f'| {n} | {len(d)} | ' + ' | '.join(cells) + ' |')

    print('\nGames expected at opt(n) after one round of 64 from the incumbent, the size alone:')
    p1_round = {}
    with open(f'{p1}/seed-1.jsonl') as f1, open(f'{p1}/seed-2.jsonl') as f2:
        for a, b in zip(f1, f2):
            ra, rb = json.loads(a), json.loads(b)
            p1_round[ra['n']] = (ra['stop_at_known']['round'], rb['stop_at_known']['round'])
    for kind in ('stuck', 'start'):
        sel = [c for c in cases if c[0] == kind]
        cells = []
        for target in TARGETS:
            et = eu = 0.0
            for _, n, x, d in sel:
                pt, pu = chance(t, w, x, d, n, target, (0,))
                et += 1 - (1 - pt) ** ROUND
                eu += 1 - (1 - pu) ** ROUND
            cells.append(f'share {target}: tilted {et:.1f}, uniform {eu:.1f}')
        extra = ''
        if kind == 'start':
            extra = (f'; the pilot reached {sum(p1_round[n][0] == 1 for _, n, _, _ in sel)} (seed 1) and '
                     f'{sum(p1_round[n][1] == 1 for _, n, _, _ in sel)} (seed 2) at round 1 with the share 0.1-0.3')
        print(f'    {kind} ({len(sel)}): ' + '; '.join(cells) + extra)


if __name__ == '__main__':
    main()
