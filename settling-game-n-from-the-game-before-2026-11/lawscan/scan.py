"""Fit "delta(n) = k * P1" by cofactor on the proven searched games, then flag the games past 5060 whose best-known
increments disagree with a law that holds at 95% or more of its proven games.

delta(n) = score(n - 1) + n - score(n); P is the largest prime factor of n, P1 the prime below P, the cofactor n / P.
Reads ../searched.csv (proven searched games, 2..5060) and the current best-known file."""
import collections
import csv
import json
import sys

BEST_KNOWN = '/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl'


def largest_prime(n):
    p, m, last = 2, n, 1
    while p * p <= m:
        while m % p == 0:
            m //= p
            last = p
        p += 1
    return m if m > 1 else last


def prev_prime(p):
    q = p - 1
    while any(q % k == 0 for k in range(2, int(q ** 0.5) + 1)):
        q -= 1
    return q


def main():
    proven = collections.defaultdict(list)
    for row in csv.DictReader(open('../searched.csv')):
        n, delta = int(row['n']), int(row['delta'])
        P = largest_prime(n)
        if P < 50:
            continue
        proven[n // P].append((n, delta, prev_prime(P)))
    laws = {}
    print('cofactor  games  best k  holds   (delta = k * P1 on the proven searched games, P >= 50)')
    for c in sorted(proven):
        games = proven[c]
        ks = collections.Counter(d / p1 for _, d, p1 in games if d % p1 == 0)
        if not ks:
            continue
        k, hits = ks.most_common(1)[0]
        share = hits / len(games)
        if len(games) >= 10:
            print(f'{c:8}  {len(games):5}  {k:6g}  {hits:5} ({100 * share:.0f}%)')
        if len(games) >= 10 and share >= 0.95:
            laws[c] = k
    best = {}
    for line in open(BEST_KNOWN):
        if line.strip():
            d = json.loads(line)
            best[d['n']] = max(best.get(d['n'], 0), d['score'])
    print('\nlaws used (95% or more of 10 or more proven games):', laws)
    flags = []
    covered = collections.Counter()
    for n in range(5062, 10001):
        P = largest_prime(n)
        c = n // P
        if c not in laws or P < 50:
            continue
        delta = best[n - 1] + n - best[n]
        law = int(laws[c] * prev_prime(P))
        covered[c] += 1
        if delta not in (0, law):
            flags.append((n, c, delta, law))
    print('games past 5060 covered:', dict(covered))
    for n, c, delta, law in flags:
        side = f'n - 1 = {n - 1} short by {law - delta}' if delta < law else f'n = {n} short by {delta - law}'
        print(f'{n} = {c} * {n // c}: delta {delta}, law {law}: {side}, if the law holds')
    print(f'{len(flags)} flags')


main()
