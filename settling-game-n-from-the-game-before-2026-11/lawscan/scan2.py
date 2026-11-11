"""Flag games past 5060 whose best-known increments disagree with the exchange law (delta(n) = the shadow of n at an
exchange step, ../past5060.csv's step) or with the weaker cofactor laws (40P: 18 P1, 49P: 25 P1, 87-92% of proven)."""
import csv
import json

BEST_KNOWN = '/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl'


def factor(n):
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def prev_prime(p):
    q = p - 1
    while any(q % k == 0 for k in range(2, int(q ** 0.5) + 1)):
        q -= 1
    return q


best = {}
for line in open(BEST_KNOWN):
    if line.strip():
        d = json.loads(line)
        best[d['n']] = max(best.get(d['n'], 0), d['score'])
steps = {int(r['n']): r['step'] for r in csv.DictReader(open('../past5060.csv'))}
exch = flags = 0
for n in range(5062, 10001):
    delta = best[n - 1] + n - best[n]
    fs = factor(n)
    if steps.get(n) == 'exchange':
        exch += 1
        shadow = 1
        for p in fs:
            shadow *= prev_prime(p) if p > 2 else 1
        if delta != shadow:
            flags += 1
            print(f'exchange {n} = {"*".join(map(str, fs))}: delta {delta}, shadow {shadow}')
    P = max(fs)
    c = n // P
    if P >= 50 and c in (40, 49):
        law = {40: 18, 49: 25}[c] * prev_prime(P)
        if delta not in (0, law):
            flags += 1
            side = f'{n - 1} short by {law - delta}' if delta < law else f'{n} short by {delta - law}'
            print(f'{c}P {n}: delta {delta}, law {law}: {side} if the law holds')
print(f'{exch} exchange steps past 5060; {flags} flags')
