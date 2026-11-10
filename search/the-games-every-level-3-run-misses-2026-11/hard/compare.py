#!/usr/bin/env python3
"""The recurring starts against the optimum and against matched controls: starts.csv (a row a game) and
starts_by_run.csv (a row for each run that searched the game from moves for n - 1 at opt(n - 1)).

    cd /home/brian/taxman_work/lab/work/gapdash/hard && OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
        nice -n 19 /home/brian/taxman_work/lab/work/stats-venv/bin/python3 -I -B compare.py

The stats venv's Python (numpy, for the tilted draw), about 30 minutes, and longer on a first run, which computes the
candidates of each game studied and saves them in candidates.json (read after).  Reads plays.csv.gz (extract.py),
recurrence.csv (recurrence.py), the proven table, and board.py of the notebook entry "How the optimal game changes
with n" (E5), the frame model in Python: its exact test of a promotion set, its candidates and its survivors.  -B, and
sys.dont_write_bytecode below, keep Python from writing into the notebook's folder.

Words, as E5 has them.  T is the proven set of game n, O a run's line's set, S the line of n - 1 that the line started
from, and surv(S) what survives of its seed in game n (of its moves up to n/2, the candidates of n that can still be
promoted, from the largest down), from which a trajectory begins; the survivors' sums match the lines'
survivor_scores, which the script checks.  A *swap* from a set X to T has the drops X - T and the additions T - X.  A
neighborhood that frees every drop of X holds T, since it leaves every other candidate free; p_free is the chance that
one neighborhood of X does, at each stage of the widening (70-90%, 50-70%, 40-60% of X's promotions fixed), for the
uniform draw (exact) and for the tilted one (finder.rs's weighted draw without replacement, by the weights of its
TILT, sampled).  A round of 64 neighborhoods from one incumbent tilts a quarter of them.  Freeing every drop is
necessary, not sufficient: the neighborhood's search of at most 1,024 steps must also find T.

Controls: for each recurring start, the 3 games nearest in n among the searched games below their ceiling, in the same
thousand (3001-4000 or 4001-5060), with a cofactor within a factor of 1.5 of its own, that every run searched from
moves for n - 1 at opt(n - 1) and none left short; no game is a control twice.
"""

import csv
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True  # board.py lives in the notebook, which this study only reads
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves this folder off the path
from common import (E5, HERE, HI, LO, cofactor, factor, ints, kind, layer, load_opt, load_parity,  # noqa: E402
                    promotions_of, read_plays, read_recurrence, seed_of, started_from)
sys.path.insert(0, E5)
from board import Game, Tables  # noqa: E402

CANDIDATES = os.path.join(HERE, "candidates.json")
STAGES = [(0.7, 0.9), (0.5, 0.7), (0.4, 0.6)]  # finder.rs LADDER
TILT = [487, 470, 348, 241, 153, 112, 76, 45, 28, 33]  # finder.rs TILT
CONTROLS_EACH = 3
COFACTOR_RATIO = 1.5
SHARES = 101  # points of the grid over a stage's range of shares
TILT_DRAWS, CHUNK = 200000, 10000  # samples of the tilted draw, and how many at a time
SEED = 20261109


def tilt_weight(x, n):
    return TILT[min(max(0, 40 * x - 10 * n) // n, len(TILT) - 1)]


def kept_of(size, share):
    return int(math.floor(size * share + 0.5))


def p_uniform(size, d, fix):
    """The chance that a uniform neighborhood of a set of `size` promotions frees `d` given ones."""
    total = 0.0
    for i in range(SHARES):
        kept = kept_of(size, fix[0] + (fix[1] - fix[0]) * i / (SHARES - 1))
        p = 1.0
        for j in range(d):
            p *= max(0, size - kept - j) / (size - j)
        total += p
    return total / SHARES


def p_tilted(members, drops, n, fix, rng):
    """The chance that a tilted neighborhood of `members` frees every one of `drops`: the draw of finder.rs's
    tilted_freed, a weighted draw without replacement, which is that of the keys u^(1/w) (the largest are freed),
    sampled TILT_DRAWS times; 0 means below about 1 / TILT_DRAWS."""
    xs = sorted(members)
    w = np.array([tilt_weight(x, n) for x in xs], dtype=float)
    is_drop = np.array([x in drops for x in xs])
    size, hits = len(xs), 0
    for _ in range(TILT_DRAWS // CHUNK):
        shares = rng.uniform(fix[0], fix[1], CHUNK)
        freed = size - np.floor(size * shares + 0.5).astype(int)
        keys = rng.random((CHUNK, size)) ** (1 / w)
        cut = np.sort(keys, axis=1)[np.arange(CHUNK), size - freed]  # the smallest key freed
        hits += int(np.count_nonzero(keys[:, is_drop].min(axis=1) >= cut))
    return hits / TILT_DRAWS


_FREE = {}


def p_free(members, target, n, rng):
    """For each stage: the chance that a uniform and a tilted neighborhood of `members` frees every drop toward
    `target`, and that a round of 64 from it (a quarter tilted) does at least once."""
    drops = frozenset(members - target)
    key = (n, frozenset(members), drops)
    if key not in _FREE:
        out = []
        for fix in STAGES:
            if drops:
                pu, pt = p_uniform(len(members), len(drops), fix), p_tilted(members, drops, n, fix, rng)
            else:
                pu = pt = 1.0
            out.append((pu, pt, 1 - (1 - pu) ** 48 * (1 - pt) ** 16))
        _FREE[key] = out
    return _FREE[key]


def expected_freeing(pf, impr, stage_rounds, rounds, ntraj):
    """The expected number of the line's neighborhoods that freed every drop of its final set O, counting those of the
    trajectory that held O from the round after O was found: with no gain, the first trajectory, whose incumbent was
    the start, O, in all its rounds (stage_rounds); else the last gain's trajectory, which after it spends 4 rounds at
    stage 0, 4 at stage 1 and the rest at stage 2 (the widening of 4).  A round gives a trajectory 64 / ntraj
    neighborhoods, a quarter of them tilted."""
    if pf is None or not stage_rounds:
        return ""
    if impr:
        after = rounds - impr[-1][0]
        by_stage = [min(after, 4), min(max(after - 4, 0), 4), max(after - 8, 0)]
    else:
        by_stage = stage_rounds[0]
    return sum(r * 64 / ntraj * (0.75 * pf[s][0] + 0.25 * pf[s][1]) for s, r in enumerate(by_stage))


def size_median(xs, n):
    xs = sorted(x / n for x in xs)
    return round(xs[len(xs) // 2], 3) if xs else ""


def run_kind(run):
    if run.startswith("rehearsal"):
        return "first pass" if run.endswith(":p1") else "later pass"
    return "chain"


def median(xs):
    xs = sorted(xs)
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2 if xs else float("nan")


def tallies(by_run, summary):
    """The counts the README quotes: the failing plays of the recurring starts, by kind of run; how the plays that
    reached the optimum got there; and the canonical plays."""
    rec_plays = [r for r in by_run if r["role"] == "recurring"]
    print("failing plays of the recurring starts: kind | plays | ended by the stop | no round at stage 2 in the first "
          "trajectory | expected neighborhoods freeing the swap, median and sum")
    for k in ("first pass", "later pass", "chain"):
        g = [r for r in rec_plays if r["outcome"] == "short" and run_kind(r["run"]) == k]
        s2 = [int(r["stage_rounds"].split()[0].split(".")[2]) for r in g if r["stage_rounds"]]
        e = [float(r["expected_freeing_neighborhoods"]) for r in g if r["expected_freeing_neighborhoods"]]
        print(f"  {k} | {len(g)} | {sum(int(r['growth_stop']) for r in g)} | {sum(x == 0 for x in s2)} | "
              f"{median(e):.2f}, {sum(e):.1f}")
    fails = [r for r in rec_plays if r["outcome"] == "short"]
    for s in (1, 2):
        ratio = [float(r[f"pO_tilted_s{s}"]) / float(r[f"pO_uniform_s{s}"]) for r in fails
                 if r[f"pO_uniform_s{s}"] and float(r[f"pO_uniform_s{s}"]) > 0 and float(r[f"pO_tilted_s{s}"]) > 0]
        print(f"  tilted over uniform chance of freeing the stuck swap at stage {s}: median {median(ratio):.0f} "
              f"({min(ratio):.1f}-{max(ratio):.0f}) over {len(ratio)} plays")
    print("plays of the recurring starts that reached opt(n): kind | from the start | from a line below | from a line "
          "above | at stage 2 | median round of the last gain")
    for k in ("first pass", "later pass", "chain"):
        g = [r for r in rec_plays if r["outcome"] == "opt" and run_kind(r["run"]) == k]
        src = [("start" if r["last_impr_traj"] in ("start", "") else "own" if int(r["last_impr_traj"]) == r["n"] else
                "above" if int(r["last_impr_traj"]) > r["n"] else "below") for r in g]
        last_round = median([r["last_impr_round"] for r in g if r["last_impr_round"] != ""])
        print(f"  {k} | {src.count('start')} | {src.count('below')} | {src.count('above')}"
              f"{' (and ' + str(src.count('own')) + ' from its own line)' if 'own' in src else ''} | "
              f"{sum(r['last_impr_stage'] == 2 for r in g)} | {last_round:g}")
    print("expected neighborhoods that freed the stuck swap, summed over the failing plays of the rehearsals (a seed "
          "each; the chains repeat seed 1's draws), and the plays that reached opt(n):")
    for n in sorted({r["n"] for r in rec_plays}):
        g = [r for r in rec_plays if r["n"] == n and r["run"].startswith("rehearsal")]
        e = [float(r["expected_freeing_neighborhoods"]) for r in g
             if r["outcome"] == "short" and r["expected_freeing_neighborhoods"]]
        print(f"  {n}: {sum(e):.1f} over {len(e)} failing plays; reached in {sum(r['outcome'] == 'opt' for r in g)}")
    canon = [s for s in summary if s["role"] == "recurring"]
    print(f"canonical failing plays: {len(canon)}; within 5 drops of surv(S): "
          f"{sum(int(s['O_vs_survS_drops']) <= 5 for s in canon)}; no gain over the start: "
          f"{sum(s['start_vs_line'] == 0 for s in canon)}; one stuck set over all failing plays: "
          f"{sum(s['distinct_stuck_sets'] == 1 for s in canon)}")


def choose_controls(rec, plays, opt, recurring):
    """For each recurring start, CONTROLS_EACH games matched by thousand, cofactor and n."""
    def clean(n):
        r = rec[n]
        if r["kind"] != "below":
            return False
        runs = [run for run in plays if n in plays[run]]
        return (all(plays[run][n]["method"] == "search" for run in runs)
                and r["p1_short"] + r["pk_short"] + r["chains_short"] == 0
                and r["p1_pool"] == r["p1_runs"] and r["pk_pool"] == r["pk_runs"]
                and r["chains_pool"] == r["chains_runs"])
    clean_games = [n for n in range(LO, HI + 1) if clean(n)]
    used, out = set(), {}
    for g in recurring:
        near = [n for n in clean_games if n not in used and (n > 4000) == (g > 4000)
                and abs(math.log(cofactor(n) / cofactor(g))) <= math.log(COFACTOR_RATIO)]
        near.sort(key=lambda n: (abs(n - g), n))
        out[g] = near[:CONTROLS_EACH]
        used.update(out[g])
    return out, len(clean_games)


def main():
    rng = np.random.default_rng(SEED)
    rec = read_recurrence()
    plays = read_plays()
    recurring = [n for n in range(LO, HI + 1) if rec[n]["recurring"]]
    opt0 = load_opt(LO - 1, HI, promotions=False)
    controls, n_clean = choose_controls(rec, plays, opt0, recurring)
    games = recurring + [c for g in recurring for c in controls[g]]
    opt = load_opt(LO - 1, HI, moves=set(games))
    par = load_parity(LO - 1, HI)
    tables = Tables(HI + 1)
    cands = {}
    if os.path.exists(CANDIDATES):
        with open(CANDIDATES) as f:
            cands = {int(k): v for k, v in json.load(f).items()}
    boards = {}
    for n in games:
        boards[n] = Game(tables, n, opt[n]["moves"], cands.get(n))
        if n not in cands:
            cands[n] = sorted(boards[n].candidates)
            with open(CANDIDATES, "w") as f:
                json.dump({str(k): v for k, v in sorted(cands.items())}, f)
        assert len(boards[n].candidates) == opt[n]["setup"]["candidates"], n
        assert boards[n].promotable(opt[n]["promotions"]), n
    print(f"{len(recurring)} recurring starts; {n_clean} clean games, of which the controls: "
          f"{ {g: controls[g] for g in recurring} }")

    by_run = []
    for n in games:
        role = "recurring" if n in recurring else "control"
        T = opt[n]["promotions"]
        To = opt[n - 1]["promotions"]
        b = boards[n]
        surv_To = b.survivors(To | ({n // 2} if opt[n - 1]["half_up"] else set()))
        for run in plays:
            row = plays[run].get(n)
            if row is None:
                continue
            S_row = started_from(plays, run, n)
            if S_row is None or int(S_row["score"]) != opt[n - 1]["score"]:
                continue  # not searched from moves for n - 1 at opt(n - 1)
            if row["method"] != "search":
                continue
            O = promotions_of(row, opt)
            S = promotions_of(S_row, opt)
            sv = b.survivors(seed_of(S_row, opt))
            assert b.promotable(O), (run, n)
            surv_line = dict((int(a), int(s)) for a, s in (t.split(":") for t in row["surv"].split()))
            if n - 1 in surv_line:
                assert surv_line[n - 1] == opt[n]["in_the_bag"] + sum(sv), (run, n)
            pf_O = p_free(O, T, n, rng) if O != T else None
            pf_S = p_free(sv, T, n, rng)
            # what survives in n of the run's lines of n + 1 ... n + 8: the trajectories from above that a later pass
            # or the descent gives the game
            above = []
            for j in range(1, 9):
                up = plays[run].get(n + j)
                if up is not None and O != T:
                    sj = b.survivors(promotions_of(up, opt))
                    above.append((len(sj - T), j, len(T - sj), sum(T) - sum(sj),
                                  int(int(up["score"]) == opt[n + j]["score"])))
            best_above = min(above) if above else None
            first_opt_above = next((a[1] for a in sorted(above, key=lambda a: a[1]) if a[4]), "")
            impr = [tuple(int(v) for v in t.split(".")) for t in row["impr"].split()]
            traj = row["traj"].split()
            stage_rounds = [ints(s.replace(".", " ")) for s in row["stage_rounds"].split()]
            ntraj = max(1, len(traj))
            e_free = expected_freeing(pf_O, impr, stage_rounds, int(row["rounds"]), ntraj)
            by_run.append({
                "role": role, "n": n, "run": run, "seed": row["seed"], "outcome": "short" if O != T and
                int(row["score"]) < opt[n]["score"] else "opt",
                "short_by": opt[n]["score"] - int(row["score"]), "same_set_as_proven": int(O == T),
                "S_is_proven": int(S == To), "S_run": S_row["run"],
                "promos": len(O), "proven_promos": len(T),
                "O_drops": len(O - T), "O_adds": len(T - O), "O_drops_sum": sum(O - T), "O_adds_sum": sum(T - O),
                "O_drops_size": size_median(O - T, n), "O_adds_size": size_median(T - O, n),
                "O_drops_list": " ".join(map(str, sorted(O - T))), "O_adds_list": " ".join(map(str, sorted(T - O))),
                "survS_drops": len(sv - T), "survS_adds": len(T - sv), "survS_short": sum(T) - sum(sv),
                "survS_drops_size": size_median(sv - T, n),
                "O_vs_survS_drops": len(sv - O), "O_vs_survS_adds": len(O - sv),
                "surv_proven_drops": len(surv_To - T), "surv_proven_adds": len(T - surv_To),
                "above_first_at_opt": first_opt_above,
                "above_best_j": best_above[1] if best_above else "",
                "above_best_drops": best_above[0] if best_above else "",
                "above_best_adds": best_above[2] if best_above else "",
                "above_best_short": best_above[3] if best_above else "",
                **{f"pO_round_s{s}": f"{pf_O[s][2]:.3g}" if pf_O else "" for s in range(3)},
                **{f"pO_uniform_s{s}": f"{pf_O[s][0]:.3g}" if pf_O else "" for s in range(3)},
                **{f"pO_tilted_s{s}": f"{pf_O[s][1]:.3g}" if pf_O else "" for s in range(3)},
                **{f"pS_round_s{s}": f"{pf_S[s][2]:.3g}" for s in range(3)},
                "expected_freeing_neighborhoods": f"{e_free:.3g}" if e_free != "" else "",
                "start": row["start"], "start_vs_line": int(row["score"]) - int(row["start"]) if row["start"] else "",
                "surv_back": surv_line.get(n - 1, ""), "traj": row["traj"], "rounds": row["rounds"],
                "stage_rounds": row["stage_rounds"], "work": row["work"], "n_impr": len(impr),
                "impr": row["impr"], "last_impr_round": impr[-1][0] if impr else "",
                "last_impr_traj": traj[impr[-1][1]] if impr else "", "last_impr_stage": impr[-1][2] if impr else "",
                "growth": row["growth"], "growth_stop": row["growth_stop"], "pushed": row["pushed"],
                "other_score": row["other_score"], "descent_root": row["descent_root"],
                "repaired_from": row["repaired_from"],
            })
        print(f"  {n} ({role}): {sum(1 for r in by_run if r['n'] == n)} plays", file=sys.stderr)

    fields = list(by_run[0])
    with open(os.path.join(HERE, "starts_by_run.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(by_run)

    # one row a game, from one play: a recurring start's first failure in a rehearsal's first pass (else its first
    # failure), a control's play in rehearsal:p1
    summary = []
    for n in games:
        plays_n = [r for r in by_run if r["n"] == n]
        fails = [r for r in plays_n if r["outcome"] == "short"]
        first_passes = [r for r in (fails or plays_n) if r["run"].endswith(":p1") and r["run"].startswith("rehearsal")]
        canon = (first_passes or fails or plays_n)[0]
        stuck_sets = {(r["O_drops_list"], r["O_adds_list"]) for r in fails}
        ok = [r for r in plays_n if r["outcome"] == "opt"]
        r0 = rec[n]
        setup, setup_b = opt[n]["setup"], opt[n - 1]["setup"]
        ust = par[n][0] - par[n - 1][0]
        summary.append({
            "role": canon["role"], "n": n,
            "matched_to": "" if n in recurring else next(g for g in recurring if n in controls[g]),
            "factors": "*".join(map(str, factor(n))), "cofactor": cofactor(n), "layer": layer(n),
            "n_minus_1": f"{'prime' if layer(n - 1) == 1 else kind(n - 1, opt)}",
            "c": n + opt[n - 1]["score"] - opt[n]["score"],
            "p1_starts": r0["p1_starts"], "pk_starts": r0["pk_starts"], "pk_runs": r0["pk_runs"],
            "chains_starts": r0["chains_starts"], "chains_runs": r0["chains_runs"],
            "plays_from_opt": len(plays_n), "plays_short": len(fails), "distinct_stuck_sets": len(stuck_sets),
            "plays_at_opt_with_proven_set": sum(r["same_set_as_proven"] for r in ok),
            "successes_last_traj": " ".join(f"{r['run']}:{r['last_impr_traj'] or 'none'}@{r['last_impr_stage']}"
                                            for r in ok if n in recurring),
            "canonical_run": canon["run"], "short_by": canon["short_by"],
            **{k: canon[k] for k in ("promos", "O_drops", "O_adds", "O_drops_sum", "O_adds_sum", "O_drops_size",
                                     "O_adds_size", "survS_drops", "survS_adds", "survS_short", "survS_drops_size",
                                     "O_vs_survS_drops", "O_vs_survS_adds", "S_is_proven", "surv_proven_drops",
                                     "surv_proven_adds", "above_first_at_opt", "above_best_j", "above_best_drops",
                                     "above_best_short", "pO_round_s0", "pO_round_s1", "pO_round_s2", "pS_round_s0",
                                     "pS_round_s1", "pS_round_s2", "expected_freeing_neighborhoods", "start_vs_line",
                                     "traj", "rounds", "stage_rounds", "n_impr", "last_impr_round",
                                     "last_impr_traj", "last_impr_stage", "growth", "pushed")},
            "frames": setup.get("frames"), "cands": setup.get("candidates"), "d_cands": setup.get("candidates", 0) -
            (setup_b.get("candidates") or par[n - 1][2]), "max_total": setup.get("max_total"),
            "slack": setup.get("max_total", 0) - len(opt[n]["promotions"]),
            "cap_less_greedy": setup.get("cap", 0) - setup.get("greedy_sum", 0),
            "ustar_step_less_n": ust - n,
            "O_drops_list": canon["O_drops_list"], "O_adds_list": canon["O_adds_list"],
        })
    with open(os.path.join(HERE, "starts.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)

    tallies(by_run, summary)
    print("medians, recurring starts against controls:")
    for k in ("survS_drops", "survS_adds", "survS_short", "survS_drops_size", "pS_round_s0", "pS_round_s1",
              "pS_round_s2", "c", "cofactor", "layer", "promos", "rounds", "n_impr", "start_vs_line"):
        med = {role: median([float(s[k]) for s in summary if s["role"] == role and s[k] != ""])
               for role in ("recurring", "control")}
        pairs = [(s, next(t for t in summary if t["n"] == s["matched_to"])) for s in summary if s["role"] == "control"]
        pairs = [(s, t) for s, t in pairs if s[k] != "" and t[k] != ""]
        higher = sum((float(t[k]) > float(s[k])) + 0.5 * (float(t[k]) == float(s[k])) for s, t in pairs)
        print(f"  {k}: {med['recurring']:g} against {med['control']:g}; the recurring start above its control in "
              f"{higher:g} of {len(pairs)} pairs")
    keys = ["n", "role", "matched_to", "cofactor", "c", "short_by", "promos", "O_drops", "survS_drops",
            "surv_proven_drops", "survS_drops_size", "pS_round_s0", "pS_round_s2", "pO_round_s2",
            "expected_freeing_neighborhoods", "n_impr", "plays_short", "plays_from_opt", "distinct_stuck_sets"]
    print("\t".join(keys))
    for s in summary:
        print("\t".join(str(s[k]) for k in keys))


if __name__ == "__main__":
    main()
