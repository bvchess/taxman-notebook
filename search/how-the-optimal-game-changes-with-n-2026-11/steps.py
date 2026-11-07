#!/usr/bin/env python3
"""How the recorded optimal promotion set of game n differs from what game n can take from game n - 1 (the entry's
sections 1 to 4).

    nice -n 19 python3 -I steps.py > steps-out.txt

For each game n of results/optimal.jsonl.gz, the seed is the moves of n - 1 that are factors of n (at most n/2): what
a search of n is seeded with, before setup drops what is not a candidate.  The step's drops D are the members of the
seed that the promotions of n lack, its additions A the promotions of n the seed lacks.  The script prints:

1. the sizes of D and A by method and by stretch of n;
2. where the changed promotions lie: their size against n, their layer (which fixes their frame) against the layer
   where n arrives, their relation to n's prime factors;
3. whether the members of D and A at one step are related to each other more often than random sets of the same sizes
   are, for several relations, and whether D lies in the cores that A creates (the frame model, exactly);
4. whether the changes of the games before predict D, and whether an earlier game than n - 1 is closer to n's set.

It writes steps.json, the drops and additions of every searched game.  The random sets take D' from the seed and A' from
the numbers up to n/2 outside the seed that some game within 100 of n promotes, drawn by random.Random(1).
"""
import json
import os
import random
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from board import Tables, frame_graph_by_layer, load_results, seed_of  # noqa: E402  (board.py sits beside this script)

STRETCHES = [(2, 1000), (1001, 2000), (2001, 3000), (3001, 4000), (4001, 5060)]
HARD = (3441, 5060)
POOL_WINDOW = 100
DRAWS = 20


def quantile(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))]


def main():
    games = load_results()
    n_max = max(games)
    t = Tables(n_max)
    om, lp = t.omega, t.largest_prime

    def cof(x):
        return x // lp(x)

    steps = {}
    for n in range(3, n_max + 1):
        seed = seed_of(games, n)
        opt = games[n]['promotions']
        steps[n] = (seed, opt, seed - opt, opt - seed)
    searched = [n for n in range(3, n_max + 1) if games[n]['method'] == 'search']

    print('# 1. The sizes of the drops D and the additions A, against the seed from n - 1\n')
    by_method = defaultdict(lambda: [0, 0])
    for n in range(3, n_max + 1):
        _, _, d, a = steps[n]
        by_method[games[n]['method']][0] += 1
        by_method[games[n]['method']][1] += bool(d or a)
    for m, (cnt, changed) in sorted(by_method.items()):
        print(f'method {m:8s}: {cnt:5d} games, {changed:5d} with a change')
    print()
    print('| n | searched | no change | D: median, p90, max | A: median, p90, max | D >= 5 | D >= 10 | promotions, median |')
    print('|---|---|---|---|---|---|---|---|')
    for lo, hi in STRETCHES + [HARD, (2, n_max)]:
        ns = [n for n in searched if lo <= n <= hi]
        ds = [len(steps[n][2]) for n in ns]
        as_ = [len(steps[n][3]) for n in ns]
        none = sum(1 for n in ns if not steps[n][2] and not steps[n][3])
        sizes = [len(steps[n][1]) for n in ns]
        print(f'| {lo}-{hi} | {len(ns)} | {none} | {statistics.median(ds):g}, {quantile(ds, .9)}, {max(ds)} | '
              f'{statistics.median(as_):g}, {quantile(as_, .9)}, {max(as_)} | {sum(d >= 5 for d in ds)} | '
              f'{sum(d >= 10 for d in ds)} | {statistics.median(sizes):g} |')
    net = Counter(len(steps[n][3]) - len(steps[n][2]) for n in searched)
    print(f'\n|A| - |D| over the searched games: {dict(sorted(net.items()))}')
    print(f'a step with D empty and A not: {sum(1 for n in searched if not steps[n][2] and steps[n][3])}; '
          f'with A empty and D not: {sum(1 for n in searched if steps[n][2] and not steps[n][3])}')

    print('\n# 2. Where the changed promotions lie (searched games; "kept" is the seed less D)\n')
    low = sum(1 for n in range(1001, n_max + 1) for x in games[n]['promotions'] if 4 * x <= n)
    total = sum(len(games[n]['promotions']) for n in range(1001, n_max + 1))
    print(f'the promotions of 1001-{n_max} at most n/4: {low} of {total} ({low / total:.4f})\n')
    tests = [
        ('size x/n, quartiles', None),
        ('in the layer of n (odd n) or of n/2 (even n)', lambda x, n: om[x] == (om[n] if n % 2 else om[n // 2])),
        ('a multiple of the largest prime of n', lambda x, n: n % lp(n) == 0 and x % lp(n) == 0),
        ('shares a prime >= 5 with n', lambda x, n: any(p >= 5 and n % p == 0 for p in t.primes_of[x])),
        ('a divisor of n', lambda x, n: n % x == 0),
        ('the cofactor of n/2 (even n)', lambda x, n: n % 2 == 0 and cof(x) == cof(n // 2)),
    ]
    for lo, hi in [(1001, 3440), HARD]:
        for parity, name in [(0, 'even'), (1, 'odd')]:
            ns = [n for n in searched if lo <= n <= hi and n % 2 == parity]
            groups = {'D': [], 'A': [], 'kept': []}
            for n in ns:
                seed, opt, d, a = steps[n]
                groups['D'] += [(x, n) for x in d]
                groups['A'] += [(x, n) for x in a]
                groups['kept'] += [(x, n) for x in seed & opt]
            print(f'{lo}-{hi}, {name} n ({len(ns)} searched games; |D| {len(groups["D"])}, |A| {len(groups["A"])}):')
            for label, f in tests:
                if f is None:
                    cells = []
                    for g, xs in groups.items():
                        r = [x / n for x, n in xs]
                        cells.append(f'{g} {quantile(r, .25):.3f} {quantile(r, .5):.3f} {quantile(r, .75):.3f}')
                    print(f'    {label:46s} ' + ' | '.join(cells))
                else:
                    cells = [f'{g} {sum(f(x, n) for x, n in xs) / max(1, len(xs)):.3f}' for g, xs in groups.items()]
                    print(f'    {label:46s} ' + ' | '.join(cells))

    print('\nThe frame graph by layer: its sources, and the sources of its largest components; and the share of the '
          'recorded promotions in each layer:')
    for n in (3552, 5060):
        comps = frame_graph_by_layer(t, n)
        cells = [f'{k}: {sum(v)} ({", ".join(map(str, v[:3]))}{", ..." if len(v) > 3 else ""})'
                 for k, v in comps.items() if k >= 2]
        print(f'    {n}, sources by layer: ' + '; '.join(cells))
        promos = Counter(om[x] for x in games[n]['promotions'])
        total = sum(promos.values())
        print(f'    {n}, promotions by layer: ' + ', '.join(f'{k}: {v / total:.2f}' for k, v in sorted(promos.items())))

    print('\n# 3. Are the members of D and A at one step related to each other?\n')
    relations = [
        ('one frame (one layer)', lambda x, y: om[x] == om[y]),
        ('same largest prime', lambda x, y: lp(x) == lp(y)),
        ('same cofactor x/P(x)', lambda x, y: cof(x) == cof(y)),
        ('same largest prime or cofactor', lambda x, y: lp(x) == lp(y) or cof(x) == cof(y)),
        ('a shared maximal factor', lambda x, y: bool(set(t.mf[x]) & set(t.mf[y]))),
        ('a shared prime >= 5', lambda x, y: any(p >= 5 for p in set(t.primes_of[x]) & set(t.primes_of[y]))),
        ('a shared prime', lambda x, y: bool(set(t.primes_of[x]) & set(t.primes_of[y]))),
    ]

    def components(xs, rel):
        xs = list(xs)
        parent = list(range(len(xs)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        isolated = 0
        for i in range(len(xs)):
            linked = False
            for j in range(len(xs)):
                if i != j and rel(xs[i], xs[j]):
                    linked = True
                    if j > i:
                        parent[find(i)] = find(j)
            isolated += not linked
        return len({find(i) for i in range(len(xs))}), isolated

    rng = random.Random(1)
    for lo, hi in [(1001, 3440), HARD]:
        ns = [n for n in searched if lo <= n <= hi and len(steps[n][2]) + len(steps[n][3]) >= 2]
        pools = {}
        for n in ns:
            seed = steps[n][0]
            pool = set()
            for m in range(max(2, n - POOL_WINDOW), min(n_max, n + POOL_WINDOW) + 1):
                pool |= {x for x in games[m]['promotions'] if 2 * x <= n}
            pools[n] = sorted(pool - seed)
        draws = {n: [] for n in ns}
        for n in ns:
            seed, _, d, a = steps[n]
            seed_l = sorted(seed)
            for _ in range(DRAWS):
                draws[n].append(set(rng.sample(seed_l, len(d))) | set(rng.sample(pools[n], min(len(a), len(pools[n])))))
        members = sum(len(steps[n][2]) + len(steps[n][3]) for n in ns)
        print(f'{lo}-{hi}: {len(ns)} searched games with |D| + |A| >= 2, {members} changed promotions')
        print('| relation | isolated: observed, random | one group: observed, random |')
        print('|---|---|---|')
        for label, rel in relations:
            iso = one = 0
            riso = rone = 0.0
            for n in ns:
                c, i = components(steps[n][2] | steps[n][3], rel)
                iso += i
                one += c == 1
                for s in draws[n]:
                    rc, ri = components(s, rel)
                    riso += ri / DRAWS
                    rone += (rc == 1) / DRAWS
            print(f'| {label} | {iso / members:.3f}, {riso / members:.3f} | {one / len(ns):.3f}, {rone / len(ns):.3f} |')
        print()

    print('In the frame model: D against the region of A, the seed\'s promotions in the residual of U* + seed + A '
          '(strict), and with the seed\'s promotions that are maximal factors of the residual\'s members (wide); '
          'searched games with |D| >= 2\n')
    print('| n | region | games | D within | region: median promotions, median share of the seed | '
          'chance for a random D, mean |')
    print('|---|---|---|---|---|---|')
    region = {}
    for lo, hi in STRETCHES[1:] + [HARD]:
        ns = [n for n in searched if lo <= n <= hi and len(steps[n][2]) >= 2]
        for kind in (0, 1):
            within = 0
            sizes, shares, chance = [], [], []
            for n in ns:
                if n not in region:
                    seed, opt, d, a = steps[n]
                    ustar = frozenset(m for m in games[n]['moves'] if 2 * m > n)
                    res = t.residual(ustar | seed | a)
                    strict = res & seed
                    region[n] = (strict, strict | {f for m in res for f in t.mf[m] if f in seed})
                seed, _, d, _ = steps[n]
                r = region[n][kind]
                within += d <= r
                sizes.append(len(r))
                shares.append(len(r) / len(seed))
                p = 1.0
                for i in range(len(d)):
                    p *= max(0, len(r) - i) / (len(seed) - i)
                chance.append(p)
            print(f'| {lo}-{hi} | {("strict", "wide")[kind]} | {len(ns)} | {within} ({within / len(ns):.2f}) | '
                  f'{statistics.median(sizes):g}, {statistics.median(shares):.2f} | {statistics.mean(chance):.3f} |')

    print('\n# 4. Do the steps before predict D?\n')
    changed = {n: steps[n][2] | steps[n][3] for n in steps}
    print('| n | k | recall of D | chance | lift | D within | free set: median, p90 |')
    print('|---|---|---|---|---|---|---|')
    for lo, hi in [(1001, 3440), HARD]:
        ns = [n for n in searched if lo <= n <= hi and steps[n][2]]
        for k in [1, 2, 5, 10, 20, 50, 100, 200]:
            rec = tot = full = 0
            exp = 0.0
            sizes = []
            for n in ns:
                seed, _, d, _ = steps[n]
                v = set()
                for m in range(max(3, n - k), n):
                    v |= changed[m]
                vs = v & seed
                rec += len(d & v)
                tot += len(d)
                full += d <= v
                exp += len(d) * len(vs) / len(seed)
                sizes.append(len(vs))
            print(f'| {lo}-{hi} | {k} | {rec / tot:.3f} | {exp / tot:.3f} | {rec / max(exp, 1e-9):.1f} | '
                  f'{full / len(ns):.3f} | {statistics.median(sizes):g}, {quantile(sizes, .9)} |')
    print()
    print('An earlier game than n - 1 as the seed: |opt(n) ^ seed from n - j|, j = 2..20, against j = 1')
    for lo, hi in STRETCHES[1:] + [HARD]:
        ns = [n for n in searched if lo <= n <= hi]
        closer = equal_opt = exact1 = 0
        gains = []
        for n in ns:
            opt = games[n]['promotions']
            dist = [len(opt ^ seed_of(games, n, j)) for j in range(1, 21)]
            if dist[0] == 0:
                exact1 += 1
                continue
            best = min(dist[1:])
            if best < dist[0]:
                closer += 1
                gains.append(dist[0] - best)
            equal_opt += best == 0
        print(f'    {lo}-{hi}: {len(ns)} searched, n - 1 exact {exact1}, an earlier game closer {closer} '
              f'(gain median {statistics.median(gains) if gains else 0:g}), an earlier game exact {equal_opt}')
    print()
    print('The size of D against the form of n (searched games):')
    for lo, hi in [(1001, 3440), HARD]:
        ns = [n for n in searched if lo <= n <= hi]
        forms = {
            'even': [n for n in ns if n % 2 == 0], 'odd': [n for n in ns if n % 2],
            'P(n) <= 50': [n for n in ns if lp(n) <= 50], 'P(n) > 50': [n for n in ns if lp(n) > 50],
            'layer of n <= 3': [n for n in ns if om[n] <= 3], 'layer of n >= 4': [n for n in ns if om[n] >= 4],
        }
        cells = []
        for label, xs in forms.items():
            ds = [len(steps[n][2]) for n in xs]
            cells.append(f'{label}: {len(xs)} games, median {statistics.median(ds):g}, p90 {quantile(ds, .9)}, '
                         f'D >= 5 {sum(d >= 5 for d in ds) / len(ds):.2f}')
        print(f'    {lo}-{hi}: ' + '; '.join(cells))

    out = {str(n): {'drops': sorted(steps[n][2]), 'additions': sorted(steps[n][3]), 'promotions': len(steps[n][1])}
           for n in searched}
    with open(os.path.join(HERE, 'steps.json'), 'w') as f:
        json.dump(out, f, separators=(',', ':'))


if __name__ == '__main__':
    main()
