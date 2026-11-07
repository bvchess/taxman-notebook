#!/usr/bin/env python3
"""The swaps that the unsound pilot's stuck games and short starts needed, and which neighborhoods contain them (4-5).

    nice -n 19 python3 -I swaps.py P1_ENTRY > swaps-out.txt

A swap takes an incumbent X, a promotion set of game n, to the recorded optimal set O: it frees the drops D = X - O and
promotes the additions A = O - X.  A neighborhood of the large neighborhood search fixes part of X and leaves the rest
and every other candidate free, so it holds O exactly when it frees every member of D; the chance that a neighborhood
rule frees D is computed here without the solver.  The incumbents are:

* the stuck sets: the final promotions of the pilot's lines (P1_ENTRY/seed-1.jsonl, seed-2.jsonl) that never held
  the known score, one per distinct set;
* the starts: the promotions of the start of each game of the pilot whose start fell short, from starts.jsonl
  (run_starts.py), which the pilot's lines do not record;
* the survivors: what survives in game n of the moves of game n - j, j = 1 to 8, computed here (board.Game.survivors).

The region of a candidate y outside X is what y's addition puts in conflict: the strict region is X's promotions in
the residual of U* + X + {y}, the cores y makes; the wide region adds X's promotions that are maximal factors of the
residual's members, whose release as factors could pay for them.  The region of A is the same with all of A added.

The rules: the mode's random share (the fixed share drawn from LO-HI, then that many promotions fixed at random); a
window of the K incumbent promotions nearest in size to one drawn at random; a fixed band of sizes; and a grown group
of at most K promotions, the region of one candidate drawn at random, then the regions of candidates whose regions
hold a member of the group drawn at random, while they fit (grow).  The group's chance is estimated from GROW_DRAWS
draws of random.Random(1).  candidates.json keeps the candidates of each game, made on the first run.
"""
import json
import os
import random
import statistics
import sys
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from board import Game, Position, Tables, load_results, seed_of  # noqa: E402  (board.py sits beside this script)

ROUND = 64
SHARES = {'default 0.7-0.9': (0.7, 0.9), '0.5-0.7': (0.5, 0.7), '0.4-0.6': (0.4, 0.6)}
SIZES = (20, 40, 60, 80, 100)
BANDS = (0.38, 0.40, 0.42, 0.45)
GROW_DRAWS = 1000
GROW_FAILS = 20
SEEDS_BACK = 8


def p_share(x_size, d_size, lo, hi, points=401):
    """The chance that the mode's random share frees all d_size drops of an incumbent of x_size promotions."""
    total = 0.0
    for i in range(points):
        share = lo + (hi - lo) * i / (points - 1)
        fixed = round(x_size * share)
        total += comb(x_size - d_size, fixed) / comb(x_size, fixed) if fixed <= x_size - d_size else 0.0
    return total / points


def p_random(x_size, d_size, k):
    """The chance that k promotions freed at random hold all d_size drops."""
    return comb(x_size - d_size, k - d_size) / comb(x_size, k) if k >= d_size else 0.0


def p_window(x, d, k):
    """The chance that the k promotions nearest in rank to a random one hold every drop."""
    s = sorted(x)
    pos = {v: i for i, v in enumerate(s)}
    lo, hi = min(pos[v] for v in d), max(pos[v] for v in d)
    hits = 0
    for r in range(len(s)):
        a = max(0, min(r - k // 2, len(s) - k))
        hits += a <= lo and hi <= a + k - 1
    return hits / len(s)


def regions(tables, game, x):
    """For each candidate y outside x, the cores y makes: x's promotions in the residual of U* + x + {y} (the strict
    region), and those with x's promotions that are maximal factors of the residual's members added (the wide region,
    the promotions whose release as factors could pay for a member of a core).  Only nonempty regions are kept."""
    pos = Position(tables, game.ustar | x)
    strict, wide = {}, {}
    for y in sorted(game.candidates - x):
        r = pos.residual_after(add=(y,))
        s = r & x
        w = set(s)
        for m in r:
            w.update(f for f in tables.mf[m] if f in x)
        if s:
            strict[y] = frozenset(s)
        if w:
            wide[y] = frozenset(w)
    return strict, wide


def inverse(reg):
    """For each promotion, the candidates whose cores hold it."""
    out = {}
    for y in sorted(reg):
        for m in reg[y]:
            out.setdefault(m, []).append(y)
    return out


def grow(reg, inv, first, k, rng):
    """A grown group of at most k promotions: the region of a candidate drawn from `first` (those whose region fits),
    then, again and again, the region of a candidate whose region holds a member of the group drawn at random, added
    where it brings something and still fits, until GROW_FAILS draws in a row add nothing."""
    members = sorted(reg[rng.choice(first)])
    group = set(members)
    fails = 0
    while fails < GROW_FAILS:
        y = rng.choice(inv[rng.choice(members)])
        new = reg[y] - group
        if new and len(group) + len(new) <= k:
            group |= new
            members += sorted(new)
            fails = 0
        else:
            fails += 1
    return group


def band(x, n, top):
    """The incumbent's promotions from n/4 up to top * n."""
    return {m for m in x if 4 * m > n and m <= top * n}


def related_groups(t, xs):
    """The number of groups of xs under 'same largest prime or same cofactor', and under 'a shared prime >= 5'."""
    def count(rel):
        xs_l = list(xs)
        parent = list(range(len(xs_l)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(len(xs_l)):
            for j in range(i + 1, len(xs_l)):
                if rel(xs_l[i], xs_l[j]):
                    parent[find(i)] = find(j)
        return len({find(i) for i in range(len(xs_l))})
    lp = t.largest_prime
    rook = count(lambda a, b: lp(a) == lp(b) or a // lp(a) == b // lp(b))
    p5 = count(lambda a, b: any(p >= 5 for p in set(t.primes_of[a]) & set(t.primes_of[b])))
    return rook, p5


def load_candidates(tables, games, ns):
    """The game of each n of ns, with the candidates candidates.json keeps, or computed and then kept there."""
    path = os.path.join(HERE, 'candidates.json')
    known = {}
    if os.path.exists(path):
        with open(path) as f:
            known = {int(k): frozenset(v) for k, v in json.load(f).items()}
    out = {}
    for n in ns:
        g = Game(tables, n, games[n]['moves'], known.get(n))
        known[n] = g.candidates
        assert len(g.candidates) == games[n]['candidates'], n
        out[n] = g
    with open(path, 'w') as f:
        json.dump({str(n): sorted(c) for n, c in sorted(known.items())}, f, separators=(',', ':'))
    return out


def main():
    p1 = sys.argv[1]
    games = load_results()
    t = Tables(max(games))

    lines = {1: {}, 2: {}}
    for s in (1, 2):
        with open(f'{p1}/seed-{s}.jsonl') as f:
            for line in f:
                rec = json.loads(line)
                lines[s][rec['n']] = rec
    starts = {}
    with open(os.path.join(HERE, 'starts.jsonl')) as f:
        for line in f:
            rec = json.loads(line)
            starts[rec['n']] = rec
    short = sorted(n for n, rec in lines[1].items() if rec['stop_at_known']['round'] != 0)
    assert sorted(starts) == short, 'starts.jsonl must hold every short start of the pilot'
    for n in short:
        assert starts[n]['start'] == lines[1][n]['start'] == lines[2][n]['start'], n
        assert starts[n]['score'] == starts[n]['start'] and starts[n]['rounds'] == 0, n
    print(f'{len(short)} short starts; every start of starts.jsonl scores what both seeds of the pilot started at')

    cases = []
    seen = set()
    for s in (1, 2):
        for n, rec in sorted(lines[s].items()):
            if rec['stop_at_known']['round'] is None:
                x = frozenset(rec['promotions'])
                if (n, x) not in seen:
                    seen.add((n, x))
                    cases.append(('stuck', f'{n} (seed {s})', n, x, rec['moves']))
    for n in short:
        cases.append(('start', str(n), n, frozenset(starts[n]['promotions']), starts[n]['moves']))

    gm = load_candidates(t, games, sorted({c[2] for c in cases}))
    print(f'{len(gm)} boards: the candidates of board.py number what setup counts on each')
    print(f'the seed from n - 1 is all candidates on {sum(seed_of(games, n) <= g.candidates for n, g in gm.items())} '
          f'of them')
    for _, _, n, x, moves in cases:
        assert gm[n].promotable(x), n
        assert frozenset(m for m in moves if 2 * m > n) == gm[n].ustar, n
    print('every incumbent is a promotion set of its game, by the test of board.py, and its line plays U*\n')

    rng = random.Random(1)
    results = []
    for kind, label, n, x, _ in cases:
        o = games[n]['promotions']
        d, a = x - o, o - x
        strict, wide = regions(t, gm[n], x)
        res = t.residual(gm[n].ustar | x | a)
        core = res & x
        core_wide = core | {f for m in res for f in t.mf[m] if f in x}
        rook, p5 = related_groups(t, d | a)
        row = dict(kind=kind, label=label, n=n, x=len(x), d=len(d), a=len(a), gain=sum(a) - sum(d), rook=rook, p5=p5,
                   core=len(core), core_has=d <= core, core_wide=len(core_wide), core_wide_has=d <= core_wide)
        for name, (lo, hi) in SHARES.items():
            row[name] = p_share(len(x), len(d), lo, hi)
        for k in SIZES:
            row[f'rand{k}'] = p_random(len(x), len(d), k)
            row[f'win{k}'] = p_window(x, d, k)
        for rname, reg in (('strict', strict), ('wide', wide)):
            inv = inverse(reg)
            for k in SIZES:
                hits, sizes, chance = 0, [], 0.0
                first = [y for y in sorted(reg) if len(reg[y]) <= k]
                for _ in range(GROW_DRAWS if first else 0):
                    g = grow(reg, inv, first, k, rng)
                    hits += d <= g
                    sizes.append(len(g))
                    chance += p_random(len(x), len(d), len(g))
                draws = max(1, len(sizes))
                row[f'{rname}{k}'] = hits / draws
                row[f'{rname}size{k}'] = statistics.mean(sizes) if sizes else 0
                row[f'{rname}rand{k}'] = chance / draws
        for top in BANDS:
            b = band(x, n, top)
            row[f'band{top}'] = (len(b), d <= b)
        if kind == 'start':
            row['p1'] = (lines[1][n]['stop_at_known']['round'], lines[2][n]['stop_at_known']['round'])
        results.append(row)
        print(f'{kind} {label} done', file=sys.stderr, flush=True)

    print('# The swaps\n')
    print('| incumbent | n | promotions | D | A | gain | groups: rook, shared prime >= 5 | strict region of A: '
          'promotions, holds D | wide region of A |')
    print('|---|---|---|---|---|---|---|---|---|')
    for r in results:
        print(f"| {r['kind']} | {r['label']} | {r['x']} | {r['d']} | {r['a']} | {r['gain']} | {r['rook']}, {r['p5']} | "
              f"{r['core']}, {'yes' if r['core_has'] else 'no'} | {r['core_wide']}, "
              f"{'yes' if r['core_wide_has'] else 'no'} |")
    for kind in ('stuck', 'start'):
        rs = [r for r in results if r['kind'] == kind]
        ds = [r['d'] for r in rs]
        print(f"\n{kind}: {len(rs)} incumbents; |D| median {statistics.median(ds):g}, range {min(ds)}-{max(ds)}; "
              f"|D| = |A| in {sum(r['d'] == r['a'] for r in rs)}; gain median "
              f"{statistics.median(r['gain'] for r in rs):g}; one rook group in {sum(r['rook'] == 1 for r in rs)}, "
              f"one shared-prime group in {sum(r['p5'] == 1 for r in rs)}; D within the strict region of A in "
              f"{sum(r['core_has'] for r in rs)}, which holds a median {statistics.median(r['core'] for r in rs):g} "
              f"promotions ({statistics.median(r['core'] / r['x'] for r in rs):.2f} of X); within the wide one in "
              f"{sum(r['core_wide_has'] for r in rs)}, a median {statistics.median(r['core_wide'] for r in rs):g} "
              f"({statistics.median(r['core_wide'] / r['x'] for r in rs):.2f})")

    print('\n# The chance that one neighborhood frees every drop\n')
    print('The mode\'s random share, and the chance of at least one in a round of 64:\n')
    print('| incumbent | n | D | ' + ' | '.join(f'{k}: one, round' for k in SHARES) + ' |')
    print('|---|---|---|' + '---|' * len(SHARES))
    for r in results:
        cells = [f'{r[k]:.1e}, {1 - (1 - r[k]) ** ROUND:.3f}' for k in SHARES]
        print(f"| {r['kind']} | {r['label']} | {r['d']} | " + ' | '.join(cells) + ' |')
    print('\nThe default share against the pilot: the starts the pilot\'s seeds brought to the known score at round 1')
    rs = [r for r in results if r['kind'] == 'start']
    for lo, hi in [(0.5, 1.01), (0.05, 0.5), (0.0, 0.05)]:
        sel = [r for r in rs if lo <= 1 - (1 - r['default 0.7-0.9']) ** ROUND < hi]
        r1 = sum(r['p1'][0] == 1 for r in sel)
        r2 = sum(r['p1'][1] == 1 for r in sel)
        exp = sum(1 - (1 - r['default 0.7-0.9']) ** ROUND for r in sel)
        print(f'    predicted chance in [{lo}, {min(hi, 1)}): {len(sel)} starts, expected {exp:.1f} at round 1; '
              f'seed 1 reached {r1}, seed 2 {r2}')
    print('\nStructured rules against random ones of the same size: the chance for one neighborhood of at most K freed '
          'promotions: K at random, the window of K, and the groups grown from the strict and the wide regions, '
          'with their mean size in brackets\n')
    print('| incumbent | n | D | ' + ' | '.join(f'K {k}: random, window, strict [size], wide [size]' for k in SIZES)
          + ' |')
    print('|---|---|---|' + '---|' * len(SIZES))
    for r in results:
        cells = [f"{r[f'rand{k}']:.0e}, {r[f'win{k}']:.2f}, {r[f'strict{k}']:.3f} [{r[f'strictsize{k}']:.0f}], "
                 f"{r[f'wide{k}']:.3f} [{r[f'widesize{k}']:.0f}]" for k in SIZES]
        print(f"| {r['kind']} | {r['label']} | {r['d']} | " + ' | '.join(cells) + ' |')
    print('\nA fixed band, the promotions from n/4 up to b n: its size, and whether it holds D\n')
    print('| incumbent | n | D | ' + ' | '.join(f'b {b}' for b in BANDS) + ' |')
    print('|---|---|---|' + '---|' * len(BANDS))
    for r in results:
        cells = [f"{r[f'band{b}'][0]}, {'yes' if r[f'band{b}'][1] else 'no'}" for b in BANDS]
        print(f"| {r['kind']} | {r['label']} | {r['d']} | " + ' | '.join(cells) + ' |')
    for kind in ('stuck', 'start'):
        sel = [r for r in results if r['kind'] == kind]
        cells = [f"b {b}: holds D in {sum(r[f'band{b}'][1] for r in sel)}, size median "
                 f"{statistics.median(r[f'band{b}'][0] for r in sel):g} ({statistics.median(r[f'band{b}'][0] / r['x'] for r in sel):.2f})"
                 for b in BANDS]
        print(f'    {kind} ({len(sel)}): ' + '; '.join(cells))
    for kind in ('stuck', 'start'):
        sel = [r for r in results if r['kind'] == kind]
        print(f'\n{kind}, means over {len(sel)} incumbents:')
        for k in SIZES:
            cells = [f"random {statistics.mean(r[f'rand{k}'] for r in sel):.2e}",
                     f"window {statistics.mean(r[f'win{k}'] for r in sel):.3f} (> 0 in "
                     f"{sum(r[f'win{k}'] > 0 for r in sel)})"]
            for rname in ('strict', 'wide'):
                cells.append(f"{rname} {statistics.mean(r[f'{rname}{k}'] for r in sel):.3f} (> 0 in "
                             f"{sum(r[f'{rname}{k}'] > 0 for r in sel)}; size "
                             f"{statistics.mean(r[f'{rname}size{k}'] for r in sel):.0f}; random at its sizes "
                             f"{statistics.mean(r[f'{rname}rand{k}'] for r in sel):.2e})")
            print(f'    K {k}: ' + '; '.join(cells))

    print('\n# The survivors of the games before as starts\n')
    print('What survives in game n of the moves of n - j: its drops against opt(n), its shortfall, and the chance '
          'that a round of the default share from it holds opt(n); the start for comparison.\n')
    print('| n | start: D, short, round | ' + ' | '.join(f'n - {j}' for j in range(1, SEEDS_BACK + 1)) + ' | best |')
    print('|---|---|' + '---|' * SEEDS_BACK + '---|')
    cache = {}
    summary = []
    for n in short:
        o = games[n]['promotions']
        st = frozenset(starts[n]['promotions'])
        d0 = len(st - o)
        p0 = 1 - (1 - p_share(len(st), d0, 0.7, 0.9)) ** ROUND
        cells = []
        best = (p0, 'start')
        for j in range(1, SEEDS_BACK + 1):
            seed = seed_of(games, n, j)
            key = (n, seed)
            if key not in cache:
                cache[key] = gm[n].survivors(seed)
            sv = cache[key]
            dj = len(sv - o)
            pj = 1 - (1 - p_share(len(sv), dj, 0.7, 0.9)) ** ROUND
            cells.append(f'{dj}, {sum(o) - sum(sv)}, {pj:.2f}')
            if pj > best[0] + 1e-12:
                best = (pj, f'n - {j}')
        summary.append((n, p0, best))
        print(f'| {n} | {d0}, {sum(o) - sum(st)}, {p0:.2f} | ' + ' | '.join(cells) + f' | {best[1]} {best[0]:.2f} |')
    fewer = equal = more = 0
    d_start, d_surv, short_surv = [], [], []
    for n in short:
        o = games[n]['promotions']
        st = frozenset(starts[n]['promotions'])
        sv = cache[(n, seed_of(games, n, 1))]
        a, b = len(st - o), len(sv - o)
        fewer += b < a
        equal += b == a
        more += b > a
        d_start.append(a)
        d_surv.append(b)
        short_surv.append(sum(o) - sum(sv))
    print(f'\nThe survivors of n - 1 against the start: fewer drops in {fewer}, as many in {equal}, more in {more} of '
          f'{len(short)}; drops a median {statistics.median(d_surv):g} against {statistics.median(d_start):g}; the '
          f'survivors fall short by a median {statistics.median(short_surv):g} (range {min(short_surv)}-'
          f'{max(short_surv)})')
    better = [s for s in summary if s[2][1] != 'start']
    print(f'\nThe survivors of some n - j (j <= {SEEDS_BACK}) give a better chance in round 1 than the start in '
          f'{len(better)} of {len(summary)} short starts; expected games at opt(n) after one round from the start '
          f'{sum(s[1] for s in summary):.1f}, from the best of the start and the {SEEDS_BACK} survivors '
          f'{sum(s[2][0] for s in summary):.1f}')
    both_missed = sorted({c[2] for c in cases if c[0] == 'stuck'} - {3600, 4416})
    print('A round of 64 from the start and from each distinct set among the survivors of n - 1 .. n - J (a set that '
          'equals the start or an earlier survivor gets no round of its own):')
    for jmax in (1, 2, 4, 8):
        tot, rounds, missed = 0.0, [], []
        for n, _, _ in summary:
            o = games[n]['promotions']
            incumbents = [frozenset(starts[n]['promotions'])]
            for j in range(1, jmax + 1):
                sv = cache[(n, seed_of(games, n, j))]
                if sv not in incumbents:
                    incumbents.append(sv)
            miss = 1.0
            for x in incumbents:
                miss *= (1 - p_share(len(x), len(x - o), 0.7, 0.9)) ** ROUND
            tot += 1 - miss
            rounds.append(len(incumbents))
            if n in both_missed:
                missed.append(f'{n} {1 - miss:.2f}')
        print(f'    J = {jmax}: expected {tot:.1f} of {len(summary)} at opt(n), in a mean {statistics.mean(rounds):.1f} '
              f'rounds (at most {max(rounds)}); the games both seeds missed: {", ".join(missed)}')


if __name__ == '__main__':
    main()
