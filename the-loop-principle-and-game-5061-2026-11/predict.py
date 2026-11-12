#!/usr/bin/env python3
"""Predictors of the shortfall delta(n) from n's prime-shifted neighbors, one line a searched game.

    nice -n 19 python3 -I predict.py            # writes predict.jsonl as it goes, resumes where it stopped

Searched games: those of 2..5060 that settle.csv (../succession) calls searched, and those of 5061..10000 that the
best-known file calls searched by the same rule (not prime, below the ceiling best-known(n - 1) + n, method of the top
line not repeat); load_rows() then drops the eleven of them whose root problem repeats the game before's (kind repeat
in past5060.csv), whose top line is a later search.  S is the optimal set of n - 1 (committed moves to 5060, the best-known moves past it, highest score per n, the
last if tied); delta = score(n - 1) + n - score(n); delta_pb = n - (PB(n) - PB(n - 1)), PB from the gap dashboard.

Words (README of this folder and brief.md, section 2):
  prev(p)   the prime just below the prime p; 2 has none and is never shifted.
  Sh(m)     the shifts of m: every number made from m by replacing some of its odd prime factors, counted with
            multiplicity, by prev(p).  Sh(m) holds m.
  C(n)      the cluster of n: Sh(n) and Sh(f) for every maximal factor f of n, less n itself.
  shadow    odd n: every prime of n replaced by prev(p) (the smallest member of Sh(n)).
  half      even n with largest prime P > 2: n/2 with P replaced by prev(P).
  shift     shadow for odd n, half for even n.
  boxmove   the smallest member of C(n) that is a move of S.
  boxpeel   the smallest y in C(n) and S with S - y + n playable on board n (peel); a game, so delta <= boxpeel.
  xmin      the single-loss rule: the smallest move y of S with S - y + n playable (0 if S + n is); delta <= xmin.
            Only members of the residual R of S + n, and moves of S that are maximal factors of members of R, can
            be that y (a move outside both leaves the cores of R intact), so only those are tried.
"""

import csv
import json
import os
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/succession")
import common  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "predict.jsonl")
BEST = "/home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl"
SETTLE = "/home/brian/taxman_work/lab/work/succession/settle.csv"
PAST = "/home/brian/taxman_work/lab/work/succession/past5060.csv"
TOP = 10000
spf = common.sieve_spf(TOP + 100)
MF = [set()] * 2 + [common.maximal_factors(x, spf) for x in range(2, TOP + 101)]


def mf_cached(x, _spf=None):
    return MF[x]


# common.playable and common.residual call common.maximal_factors; give them the table.
common.maximal_factors = mf_cached


def is_prime(x):
    return x > 1 and spf[x] == x


def prev_prime(p):
    if p <= 2:
        return None
    q = p - 1
    while not is_prime(q):
        q -= 1
    return q


def shifts(m):
    """Sh(m): m with any of its odd prime factors (with multiplicity) replaced by the prime just below."""
    out = {1}
    for p in common.factor(m):
        q = prev_prime(p) if p > 2 else None
        out = {a * p for a in out} | ({a * q for a in out} if q else set())
    return out


def cluster(n):
    c = set(shifts(n))
    for f in MF[n]:
        if f > 1:
            c |= shifts(f)
    c.discard(n)
    return {y for y in c if y >= 2}


def shadow(n):
    if n % 2 == 0:
        return None
    out = 1
    for p in common.factor(n):
        out *= prev_prime(p)
    return out


def half(n):
    if n % 2:
        return None
    P = common.factor(n)[-1]
    if P == 2:
        return None
    return n // 2 // P * prev_prime(P)


def single_loss(S, n):
    """(xmin, boxpeel inputs): the smallest move y of S with S - y + n playable, by the residual argument."""
    T = S | {n}
    if common.playable(T, n, spf):
        return 0
    R = common.residual(T, spf)
    cand = set(R) - {n}
    for z in R:
        cand |= MF[z] & S
    for y in sorted(cand):
        if common.playable(T - {y}, n, spf):
            return y
    return None


def load_best():
    best = {}
    with open(BEST) as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            n = r["n"]
            if n not in best or r["score"] >= best[n]["score"]:
                best[n] = {"score": r["score"], "moves": r["moves"], "method": r["method"]}
    return best


def load_rows():
    """predict.jsonl, less the games past 5060 that repeat the root problem of the game before (kind repeat in
    past5060.csv: R6 settles them given U), which predict.py keeps when a later search line scores higher than the
    repeat's line."""
    past = {int(r["n"]): r["kind"] for r in csv.DictReader(open(PAST))}
    rows = [json.loads(t) for t in open(OUT) if t.strip()]
    return [r for r in rows if r["range"] == "chain" or past[r["n"]] != "repeat"]


def main():
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            done = {json.loads(t)["n"] for t in f if t.strip()}
    res = common.results()
    best = load_best()
    gc = common.games_csv()
    settle = {int(r["n"]): r for r in csv.DictReader(open(SETTLE))}
    past = {int(r["n"]): r for r in csv.DictReader(open(PAST))}
    games = {}
    for n in range(1, 5061):
        games[n] = {"score": res[n]["score"], "moves": res[n]["moves"]}
    for n in range(5061, TOP + 1):
        games[n] = best[n]
    todo = []
    for n in range(2, TOP + 1):
        if n <= 5060:
            if settle[n]["outcome"] != "searched":
                continue
            step = settle[n]["step"]
            cpu = float(settle[n]["cpu"])
        else:
            if is_prime(n) or games[n]["score"] == games[n - 1]["score"] + n or games[n]["method"] == "repeat":
                continue
            step = past[n]["step"]
            cpu = None
        todo.append((n, step, cpu))
    print(f"searched games: {sum(n <= 5060 for n, _, _ in todo)} of 2..5060, {sum(n > 5060 for n, _, _ in todo)} of "
          f"5061..{TOP}; already done {len(done)}", flush=True)
    with open(OUT, "a") as out:
        for n, step, cpu in todo:
            if n in done:
                continue
            S = set(games[n - 1]["moves"])
            Sn = set(games[n]["moves"])
            assert sum(S) == games[n - 1]["score"] and sum(Sn) == games[n]["score"], n
            delta = games[n - 1]["score"] + n - games[n]["score"]
            C = cluster(n)
            inS = sorted(C & S)
            boxpeel = None
            for y in inS:
                if common.playable((S | {n}) - {y}, n, spf):
                    boxpeel = y
                    break
            f = common.factor(n)
            P = f[-1]
            row = {
                "n": n, "range": "chain" if n <= 5060 else "past", "step": step, "layer": len(f),
                "cofactor": n // P, "P": P, "P1": prev_prime(P), "cpu": cpu, "delta": delta,
                "delta_pb": n - (gc[n]["bound"] - gc[n - 1]["bound"]),
                "shadow": shadow(n), "half": half(n), "boxmove": inS[0] if inS else None, "boxpeel": boxpeel,
                "xmin": single_loss(S, n), "cluster_in_S": inS,
                "delta_in_cluster": delta in C,
                "dropped": sorted(S - Sn), "added": sorted(Sn - S - {n}),
            }
            out.write(json.dumps(row) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
