#!/usr/bin/env python3
"""Self-test of audit.py: plants defects in copies of best-known lines and checks that the audit finds each one.

    nice -n 19 python3 -I selftest.py        # about three minutes; writes no file

A game with one move left out is still a legal game, a few points lower, so a damaged line is a best-known score that
is short by a known amount.  Each defect below is planted in a game where one relation of README.md applies, and the
test passes when the audit lists the game under that relation with the right game short.
"""

import array
import collections
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit  # noqa: E402


def first(pred, start, stop=audit.TOP):
    return next(n for n in range(start, stop + 1) if pred(n))


def main():
    audit.init_tables(audit.TOP)
    lines, meta = audit.load_best_known(audit.BEST)
    chain, beyond = audit.load_chain(), audit.load_beyond()
    gc = audit.common.games_csv()
    omega, is_prime = audit.OMEGA, audit.is_prime
    digest_of = {ln.n: ln.digest for ln in lines if ln.digest}
    digest_games = collections.Counter(digest_of.values())

    def step(n):
        return gc[n]["ustar"] - gc[n - 1]["ustar"]

    def damage(n, drops=1, first_move=False):
        """Replace the lines of game n by its best line less its smallest promotions (or its first move)."""
        best = max((ln for ln in lines if ln.n == n), key=lambda ln: ln.score)
        moves = list(best.moves)
        gone = [moves[0]] if first_move else sorted(x for x in moves if x <= n // 2)[:drops]
        for x in gone:
            moves.remove(x)
        lines[:] = [ln for ln in lines if ln.n != n] + [
            audit.Line(n, best.score - sum(gone), array.array("H", moves), best.method, best.digest, best.bag)]

    games = {
        "prime": first(is_prime, 7001),
        "odd semiprime": first(lambda n: n % 2 and omega[n] == 2 and not is_prime(n), 8001),
        "half-out": first(lambda n: n % 2 == 0 and step(n) == n and not is_prime(n - 1), 8501),
        "8P": first(lambda n: n % 8 == 0 and is_prime(n // 8), 8100),
        "12P": first(lambda n: n % 12 == 0 and is_prime(n // 12), 9000),
        "9P": first(lambda n: n % 9 == 0 and is_prime(n // 9), 7000),
        "exchange": first(lambda n: n % 2 and omega[n] == 3 and 0 < step(n) < n, 8201),
        "16P clean": first(lambda n: n % 16 == 0 and is_prime(n // 16) and audit.clean_depth(n) >= 3, 8000),
        "repeat group": first(lambda n: digest_games[digest_of.get(n)] > 1 and n % 2 and not is_prime(n)
                              and omega[n] > 2, 9001),
    }
    # (name, game damaged, kind of damage, [(game of the row, relation, game it says is short)])
    plan = [
        ("N5, N3, S1 at a prime", games["prime"], {},
         [(games["prime"], r, games["prime"]) for r in ("N5", "N3", "S1")]),
        ("J3 at an odd semiprime", games["odd semiprime"], {},
         [(games["odd semiprime"], "J3", games["odd semiprime"])]),
        ("N6, N7a, N7b at a half-out game", games["half-out"], {},
         [(games["half-out"], r, games["half-out"]) for r in ("N6", "N7a", "N7b")]),
        ("L2, short n - 1 of 8P", games["8P"] - 1, {}, [(games["8P"], "L2", games["8P"] - 1)]),
        ("L4, short n - 1 of 12P", games["12P"] - 1, {}, [(games["12P"], "L4", games["12P"] - 1)]),
        ("COF9 at 9P", games["9P"], {}, [(games["9P"], "COF9", games["9P"])]),
        ("EXL at a layer-3 exchange", games["exchange"], {}, [(games["exchange"], "EXL", games["exchange"])]),
        ("FAM16 at 16P", games["16P clean"], {}, [(games["16P clean"], "FAM16", games["16P clean"])]),
        ("R6 in a repeat group", games["repeat group"], {}, [(games["repeat group"], "R6", games["repeat group"])]),
        ("PROJ, 100 promotions off 7500", 7500, {"drops": 100}, [(7500, "PROJ", 7500)]),
        ("STRUCT, q(n) not played at 7600", 7600, {"first_move": True}, [(7600, "STRUCT", 7600)]),
    ]
    for _, game, how, _ in plan:
        damage(game, **how)
    result = audit.run(lines, meta, chain, beyond)
    rows = {(r["n"], r["relation"], r["short_game"]) for r in result.rows}
    failed = 0
    for name, game, _, expect in plan:
        missing = [e for e in expect if e not in rows]
        failed += bool(missing)
        print(f"{'FAIL' if missing else 'pass'}  {name} (game {game})" + (f"  not found: {missing}" if missing else ""))
    print(f"{len(plan) - failed} of {len(plan)} planted defects found; the audit lists {len(result.rows)} rows in all; "
          f"games it built and replayed above a damaged score: {len(result.constructions)}; "
          f"bounds whose game did not replay: {result.unverified}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
