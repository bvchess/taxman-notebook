#!/usr/bin/env python3
"""Does every best-known game past 5060 have the most moves possible?

nu(n) is the matching number of the maximal factor graph of the board 1..n: each number x in 2..n is joined to its
maximal factors x/p, for the primes p dividing x (the maximal factor of a prime is 1, so 1 is a vertex).  The most moves
of a game of n is at most nu(n), and a legal game with nu(n) moves is a longest game
(docs/theory/uniqueness-and-longest-games.md, lemma Q3).

Steps:
  1. nu(n) for n = 2..10000, one augmenting-path search per new vertex (the new vertex n has only its maximal factors
     as neighbors, so nu(n) - nu(n-1) is 0 or 1).
  2. Checks: nu(21) = 9, nu(51) = 23, nu(833) = 363, nu(n) against the prover's `nu` field in
     solver/noframe/data/moves_2_1300.jsonl and the notebook's moves_1301_4949.jsonl, and the move count of every
     proven game 836..5060 of results/optimal.jsonl.gz against nu(n).
  3. For n = 5061..10000 the best-known line of unsound-run/best-known.jsonl with the highest score (the last one if
     tied), its moves against nu(n); the games that are short, with what rootfirst/ledger2.tsv says of them.

Run:  nice -n 19 python3 -I short.py       (writes nu.csv, short.csv and prints the report; reads only)
"""

import csv
import gzip
import json
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path

TOP = 10000
FIRST_UNPROVEN = 5061
WORK = Path("/home/brian/taxman_work")
OPTIMAL = WORK / "research/results/optimal.jsonl.gz"
PROVER_DATA = [
    WORK / "research/solver/noframe/data/moves_2_1300.jsonl",
    WORK / "research/solver/notebook/how-far-an-optimal-game-falls-short-of-a-longest-one-2026-10/moves_1301_4949.jsonl",
]
BEST_KNOWN = WORK / "lab/work/unsound-run/best-known.jsonl"
LEDGER = WORK / "lab/work/rootfirst/ledger2.tsv"
OUT = Path(__file__).resolve().parent
NONE = 0  # no vertex is 0, so 0 marks an unmatched vertex


def build_graph(top):
    """factors[x]: the maximal factors x/p of x, ascending order of p; composites[x]: the numbers x*p <= top with x as
    a maximal factor, ascending.  The board 1..m restricts the graph to the vertices <= m."""
    spf = list(range(top + 1))
    for p in range(2, int(top**0.5) + 1):
        if spf[p] == p:
            for multiple in range(p * p, top + 1, p):
                if spf[multiple] == multiple:
                    spf[multiple] = p
    factors = [[] for _ in range(top + 1)]
    composites = [[] for _ in range(top + 1)]
    for m in range(2, top + 1):
        x, primes = m, []
        while x > 1:
            p = spf[x]
            primes.append(p)
            while x % p == 0:
                x //= p
        for p in primes:
            factors[m].append(m // p)
            composites[m // p].append(m)  # m ascends, so each composites list stays sorted
    return factors, composites


def matching_numbers(top):
    """nu[m] for m = 0..top: the matching number of the maximal factor graph of the board 1..m, by Kuhn's search from
    each new vertex m over the vertices <= m (Berge: the matching grows exactly when an augmenting path starts at m)."""
    factors, composites = build_graph(top)
    mate = [NONE] * (top + 1)
    seen = [0] * (top + 1)  # seen[v] == m marks v visited in the search of m
    nu = [0, 0]
    for m in range(2, top + 1):
        nu.append(nu[-1] + augment(m, factors, composites, mate, seen))
    return nu


def augment(root, factors, composites, mate, seen):
    """True, with the matching augmented, if an alternating path from the new vertex `root` reaches a free vertex.
    Iterative depth-first search (the paths are too long for the recursion limit); `limit` is root, the board's top."""
    limit = root

    def neighbors(u):
        return iter(factors[u] + composites[u][: bisect_right(composites[u], limit)])

    stack_u = [root]  # the vertices on the path, on one side of the bipartition
    stack_v = []  # stack_v[i] is the neighbor of stack_u[i] that the path took, on the other side
    stack_it = [neighbors(root)]
    while stack_u:
        for v in stack_it[-1]:
            if seen[v] == root:
                continue
            seen[v] = root
            w = mate[v]
            stack_v.append(v)
            if w == NONE:
                for u, v_taken in zip(stack_u, stack_v):
                    mate[u] = v_taken
                    mate[v_taken] = u
                return True
            stack_u.append(w)
            stack_it.append(neighbors(w))
            break
        else:
            stack_u.pop()
            stack_it.pop()
            if stack_v:
                stack_v.pop()
    return False


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {name} {detail}".rstrip())
    return ok


def check_nu(nu):
    print("checks of nu")
    check("nu(21) = 9", nu[21] == 9, f"(got {nu[21]})")
    check("nu(51) = 23", nu[51] == 23, f"(got {nu[51]})")
    check("nu(833) = 363", nu[833] == 363, f"(got {nu[833]})")
    for path in PROVER_DATA:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        wrong = [(row["n"], nu[row["n"]], row["nu"]) for row in rows if nu[row["n"]] != row["nu"]]
        check(f"nu against the prover's nu in {path.name}", not wrong, f"({len(rows)} games, differing: {wrong[:5]})")


def check_proven(nu):
    """The moves of the proven optimal games 836..5060 of results/optimal.jsonl.gz against nu(n)."""
    print("checks of the proven games")
    games = {}
    with gzip.open(OPTIMAL, "rt") as lines:
        for line in lines:
            record = json.loads(line)
            games.setdefault(record["n"], record)
    assert sorted(games) == list(range(1, len(games) + 1)), "the committed chain has a gap"
    top = max(games)
    short = [(n, nu[n], games[n]["moves"]) for n in range(2, top + 1) if len(games[n]["moves"]) != nu[n]]
    in_range = [item for item in short if item[0] >= 836]
    check(f"every proven game 836..{top} has nu(n) moves", not in_range, f"(differing: {in_range})")
    print(f"  games 2..835 whose recorded moves differ from nu(n): {[item[0] for item in short if item[0] < 836]}")
    return top


def best_known_lines():
    """The line of the highest score of each n, the last one if tied; the most moves of any line of n; the lines of n."""
    best, most_moves, lines_of = {}, defaultdict(int), defaultdict(int)
    with open(BEST_KNOWN) as lines:
        for line in lines:
            record = json.loads(line)
            n = record["n"]
            if n not in best or record["score"] >= best[n]["score"]:
                best[n] = record
            most_moves[n] = max(most_moves[n], len(record["moves"]))
            lines_of[n] += 1
    return best, most_moves, lines_of


def ledger():
    """For each game of rootfirst/ledger2.tsv: its rows (game, level, seed, known, new, time)."""
    rows = defaultdict(list)
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            game, level, seed, known, new, clock = line.split("\t")
            rows[int(game)].append((int(level), int(seed), int(known), int(new), clock))
    return rows


def main():
    nu = matching_numbers(TOP)
    check_nu(nu)
    top = check_proven(nu)
    assert top == FIRST_UNPROVEN - 1, f"the committed chain ends at {top}, not {FIRST_UNPROVEN - 1}"

    best, most_moves, lines_of = best_known_lines()
    rootfirst = ledger()
    assert sorted(best) == list(range(FIRST_UNPROVEN, TOP + 1)), "best-known.jsonl misses a game"
    with open(OUT / "nu.csv", "w", newline="") as handle:
        out = csv.writer(handle)
        out.writerow(["n", "nu", "moves", "score", "short_by"])
        rows = []
        for n in range(FIRST_UNPROVEN, TOP + 1):
            moves = best[n]["moves"]
            row = (n, nu[n], len(moves), best[n]["score"], nu[n] - len(moves))
            rows.append(row)
            out.writerow(row)

    print(f"best-known games {FIRST_UNPROVEN}..{TOP}: {len(rows)}")
    bad = [n for n in best if len(set(best[n]["moves"])) != len(best[n]["moves"]) or not all(
        2 <= c <= n for c in best[n]["moves"])]
    check("every best-known line has distinct moves in 2..n", not bad, f"(bad: {bad[:5]})")
    over = [row for row in rows if row[4] < 0]
    check("no best-known line has more than nu(n) moves", not over, f"(over: {over[:10]})")
    short = [row for row in rows if row[4] > 0]
    print(f"  best-known games with fewer than nu(n) moves: {len(short)}")
    print("  shortfalls:", dict(sorted({s: sum(1 for r in short if r[4] == s) for s in {r[4] for r in short}}.items())))
    with open(OUT / "short.csv", "w", newline="") as handle:
        out = csv.writer(handle)
        out.writerow(["n", "nu", "moves", "score", "short_by", "lines", "most_moves_of_any_line", "rootfirst_rows",
                      "rootfirst_levels", "rootfirst_improved"])
        for n, nu_n, moves, score, short_by in short:
            plays = rootfirst.get(n, [])
            out.writerow([n, nu_n, moves, score, short_by, lines_of[n], most_moves[n], len(plays),
                          "/".join(str(level) for level in sorted({p[0] for p in plays})),
                          sum(1 for p in plays if p[3] > p[2])])
    played = [row for row in short if row[0] in rootfirst]
    print(f"  of them played by the root-first search (in ledger2.tsv): {len(played)}")
    print("n, nu, moves, score, short_by, rootfirst rows (level seed known new)")
    for n, nu_n, moves, score, short_by in short:
        plays = [f"{p[0]}/{p[1]}/{p[2]}/{p[3]}" for p in rootfirst.get(n, [])]
        print(f"  {n} {nu_n} {moves} {score} {short_by}  {' '.join(plays) if plays else '-'}")


if __name__ == "__main__":
    main()
