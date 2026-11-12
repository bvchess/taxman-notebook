#!/home/brian/taxman_work/lab/work/stats-venv/bin/python
"""The sampling test's numbers: the detection chance d, the sample's raises, and the estimate past 5060.

    cd /home/brian/taxman_work/lab/work/sampling && nice -n 19 ../stats-venv/bin/python -I analyze.py > analyze-out.txt

Reads calib/roots.csv, calib/jobs.csv and calib/plays/ (the calibration), sample-order.csv, sample.tsv and gains.tsv
(the sample), frame/targets.csv, the ledgers of the plays made before the sample (rootfirst/ledger.tsv, the first
LEDGER2_ROWS rows of rootfirst/ledger2.tsv, hammer/ledger.tsv), the root-first pilot's streaks
(gapdash/model/v3c/streaks.csv) and the survivor test's plays (in the notebook).  Writes nothing but its report.
README.md says what each number is and what it assumes.
"""

import collections
import csv
import json
import math
import os

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = "/home/brian/taxman_work/lab/work"
SURVIVORS = ("/home/brian/taxman_work/research/solver/notebook/search/the-games-every-level-3-run-misses-2026-11/"
             "survivors")
LEDGER2_ROWS = 2121           # ledger2.tsv's rows when the frame was read (07:19 on 2026-11-11)
B = 20000                     # Monte Carlo draws
CONF = 0.95
LEVELS = (2, 3, 4)
rng = np.random.default_rng(20261111)
# the pilot's finds that v3c merges into the unit of another find (gapdash/model/v3c/fit3-out.txt, "units with
# merged finds"): a unit is one streak, its games those of raised.csv whose first_root is the unit or a merged find
MERGED = {7956: (7959,), 7992: (8004, 8024), 8694: (8695, 8696, 8701), 8736: (8740, 8750), 9075: (9126,),
          9261: (9303,)}


def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def read_tsv(path):
    with open(path) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def last_line(path, n):
    found = []
    if os.path.exists(path):
        with open(path) as f:
            for t in f:
                if t.strip():
                    try:
                        d = json.loads(t)
                    except json.JSONDecodeError:
                        continue
                    if d["n"] == n:
                        found.append(d)
    return found[-1] if found else None


def cp_interval(k, n, conf=CONF):
    a = (1 - conf) / 2
    lo = 0.0 if k == 0 else stats.beta.ppf(a, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a, k + 1, n - k)
    return lo, hi


# -- the calibration ------------------------------------------------------------------------------------------------

def calibration():
    opt = {(r["state"], int(r["n"])): int(r["opt"]) for r in read_csv(os.path.join(HERE, "calib", "roots.csv"))}
    plays = []
    for j in read_csv(os.path.join(HERE, "calib", "jobs.csv")):
        n, level, seed = int(j["n"]), int(j["level"]), int(j["seed"])
        line = last_line(os.path.join(HERE, "calib", "plays", f"{j['state']}-g{n}-l{level}-s{seed}.jsonl"), n)
        if line is None:
            continue
        known = line.get("known_before") or 0
        plays.append({"kind": j["kind"], "state": j["state"], "n": n, "level": level, "seed": seed,
                      "raised": line["score"] > known, "reached": line["score"] >= opt[(j["state"], n)],
                      "gain": line["score"] - known, "seconds": line.get("seconds") or 0})
    return plays


def by_instance(plays, kind, level):
    """{(state, n): (raised, plays)} for one kind and level."""
    out = collections.OrderedDict()
    for p in sorted(plays, key=lambda p: (p["n"], p["state"])):
        if p["kind"] == kind and p["level"] == level:
            k, m = out.get((p["state"], p["n"]), (0, 0))
            out[(p["state"], p["n"])] = (k + p["raised"], m + 1)
    return out


def survivor_test():
    """The survivor test's level-4 plays (from the proven n - 1, no best-known file): {n: (at opt(n), plays)}."""
    out = {}
    path = os.path.join(SURVIVORS, "run.log")
    if not os.path.exists(path):
        return out
    # score.py's table at the end of run.log is the record; read the plays' own files where they are kept
    import glob
    import gzip
    opt = {}
    with gzip.open("/home/brian/taxman_work/research/results/optimal.jsonl.gz", "rt") as f:
        for t in f:
            d = json.loads(t)
            if 3300 <= d["n"] <= 5060:
                opt[d["n"]] = d["score"]
    for p in sorted(glob.glob(os.path.join(SURVIVORS, "g*-l4-s*.jsonl"))):
        n = int(os.path.basename(p)[1:].split("-")[0])
        line = last_line(p, n)
        if line:
            k, m = out.get(n, (0, 0))
            out[n] = (k + (line["score"] >= opt[n]), m + 1)
    return out


# -- the history of each target -------------------------------------------------------------------------------------

def prior_plays():
    """{n: [level, ...]}: the dedicated plays of each game since its last raise by one, before the sample."""
    seq = collections.defaultdict(list)
    for t in open(os.path.join(WORK, "rootfirst", "ledger.tsv")):
        p = t.rstrip("\n").split("\t")
        if len(p) >= 4:
            seq[int(p[0])].append((3, int(p[3]) > int(p[2])))
    for path, limit in ((os.path.join(WORK, "rootfirst", "ledger2.tsv"), LEDGER2_ROWS),
                        (os.path.join(WORK, "hammer", "ledger.tsv"), None)):
        with open(path) as f:
            for i, t in enumerate(f):
                if limit is not None and i >= limit:
                    break
                p = t.rstrip("\n").split("\t")
                if len(p) >= 5:
                    seq[int(p[0])].append((int(p[1]), int(p[4]) > int(p[3])))
    out = {}
    for n, s in seq.items():
        last = max((i for i, (_, up) in enumerate(s) if up), default=-1)
        out[n] = [lv for lv, _ in s[last + 1:]]
    return out


# -- the detection chance of a target -------------------------------------------------------------------------------

def interp(dl, level):
    """d at a (fractional) level from the rates at levels 2, 3 and 4 (array of shape (..., 3)), clamped to 2..4."""
    x = np.clip(level, 2.0, 4.0)
    lo = np.clip(np.floor(x).astype(int), 2, 3)
    w = x - lo
    a = np.take_along_axis(dl, (lo - 2)[..., None], axis=-1)[..., 0]
    b = np.take_along_axis(dl, (lo - 1)[..., None], axis=-1)[..., 0]
    return a * (1 - w) + b * w


def target_detection(d_inst, n_inst, targets, history, size=True, survival=True):
    """A fresh level-4 play's chance to raise a root among the frame's targets, for each draw.

    d_inst: (draws, roots, 3), each root's chance at levels 2, 3, 4; n_inst: the roots' games.  For a target of game
    n with prior plays at levels l_1..l_m since its last raise, root i stands at the equivalent level
    L = 4 - log2(n / n_i) (the same work per promotion candidate; clamped to 2..4), or at 4 without the size match,
    and has survived those plays with chance w_i = the product of (1 - d_i at L + l_j - 4), or 1 without survival.
    Returns (frame, located, by stratum): `frame` is the mean over the targets of sum_i d_i w_i / sum_i w_i (every
    target as likely to hold a root, with the survivors' mix of roots); `located` is sum_t sum_i d_i w_i / sum_t sum_i
    w_i (the roots spread evenly over the targets before their prior plays, and thinned by them)."""
    draws = d_inst.shape[0]
    frame, num, den = np.zeros(draws), np.zeros(draws), np.zeros(draws)
    by = collections.defaultdict(lambda: np.zeros(draws))
    count = collections.Counter()
    for t in targets:
        n = int(t["n"])
        L = 4 - np.log2(n / n_inst) if size else np.full(np.shape(n_inst), 4.0)
        L = np.broadcast_to(L, d_inst.shape[:2])
        d_now = interp(d_inst, L)
        w = np.ones(d_inst.shape[:2])
        if survival:
            for lv in history.get(n, []):
                w = w * (1 - interp(d_inst, L + lv - 4))
        dw, ws = (d_now * w).sum(axis=1), w.sum(axis=1)
        dt = dw / np.maximum(ws, 1e-300)
        frame += dt
        num += dw
        den += ws
        h = min(int(t["plays"]), 3)
        by[h] += dt
        count[h] += 1
    return frame / len(targets), num / den, {h: by[h] / count[h] for h in sorted(by)}


def draw_instances(inst, draws):
    """Resample the roots (with replacement) and draw each one's rate at each level from its Jeffreys posterior."""
    keys = list(inst)
    pick = rng.integers(0, len(keys), size=(draws, len(keys)))
    d = np.zeros((draws, len(keys), 3))
    for li, level in enumerate(LEVELS):
        k = np.array([inst[key][level][0] for key in keys], dtype=float)
        m = np.array([inst[key][level][1] for key in keys], dtype=float)
        d[:, :, li] = rng.beta(k[pick] + 0.5, m[pick] - k[pick] + 0.5)
    # a play at a higher level runs the rounds of the lower ones first, so a root's chance does not fall with level
    d = np.maximum.accumulate(d, axis=2)
    n_inst = np.array([key[1] for key in keys], dtype=float)
    return d, n_inst[pick]


def point_instances(inst):
    keys = list(inst)
    d = np.array([[[inst[key][lv][0] / inst[key][lv][1] for lv in LEVELS] for key in keys]])
    return np.maximum.accumulate(d, axis=2), np.array([key[1] for key in keys], dtype=float)


def main():
    plays = calibration()
    print("CALIBRATION: fresh plays of the rehearsals' roots (and followers), each into its own copy of the state")
    print(f"  {len(plays)} plays done of {len(read_csv(os.path.join(HERE, 'calib', 'jobs.csv')))}")
    for kind in ("root3", "root2", "follower3"):
        for level in (4, 3, 2):
            inst = by_instance(plays, kind, level)
            if not inst:
                continue
            k = sum(a for a, _ in inst.values())
            m = sum(b for _, b in inst.values())
            mean = np.mean([a / b for a, b in inst.values()])
            lo, hi = cp_interval(k, m)
            reached = sum(p["reached"] for p in plays if p["kind"] == kind and p["level"] == level)
            secs = np.mean([p["seconds"] for p in plays if p["kind"] == kind and p["level"] == level])
            print(f"  {kind:9} level {level}: raised {k} of {m} plays ({k / m:.2f}; exact 95% {lo:.2f}-{hi:.2f}, "
                  f"plays pooled), mean over {len(inst)} instances {mean:.2f}; reached opt(n) {reached}; "
                  f"{secs:.0f} s a play")
            print("      " + ", ".join(f"{s}:{n} {a}/{b}" for (s, n), (a, b) in inst.items()))
    surv = survivor_test()
    if surv:
        print("  the survivor test, level 4 from the proven n - 1 with no best-known file (at opt(n) / plays): "
              + ", ".join(f"{n} {a}/{b}" for n, (a, b) in sorted(surv.items())))

    # the roots after pass 3 with all three levels
    inst = {}
    for level in LEVELS:
        for key, val in by_instance(plays, "root3", level).items():
            inst.setdefault(key, {})[level] = val
    inst = {key: v for key, v in inst.items() if all(lv in v for lv in LEVELS)}
    if not inst:
        print("no root has plays at all three levels yet")
        return
    print(f"\n  roots after pass 3 with plays at levels 2, 3 and 4: {len(inst)}")

    targets = read_csv(os.path.join(HERE, "frame", "targets.csv"))
    T = len(targets)
    history = prior_plays()
    m_count = collections.Counter(min(len(history.get(int(t["n"]), [])), 3) for t in targets)
    print(f"  the frame's targets by dedicated plays since their last raise (0, 1, 2, 3+): "
          f"{[m_count[i] for i in range(4)]}")

    dP, nP = point_instances(inst)
    dB, nB = draw_instances(inst, B)
    variants = (("level 4 as played", False, False), ("size-matched", True, False),
                ("size-matched, after prior plays", True, True))
    dbar = {}
    print("\nDETECTION d: one fresh level-4 play's chance to raise a root among the frame's targets (point; 95% interval "
          "of the draws)")
    for name, size, surv_on in variants:
        p_f, p_l, p_by = target_detection(dP, nP, targets, history, size, surv_on)
        b_f, b_l, b_by = target_detection(dB, nB, targets, history, size, surv_on)
        dby = (p_by, b_by)  # by stratum, for the stratified reading (the last variant: after prior plays)
        readings = [("", p_f, b_f)] if not surv_on else [(", every target alike", p_f, b_f),
                                                          (", roots thinned by the plays", p_l, b_l)]
        for tag, pt, bd in readings:
            dbar[name + tag] = (pt[0], bd)
            lo, hi = np.quantile(bd, [0.025, 0.975])
            print(f"  {name + tag}: {pt[0]:.3f} ({lo:.3f}-{hi:.3f})")
        print("      by plays so far 0/1/2/3+: " + ", ".join(f"{p_by[h][0]:.3f}" for h in sorted(p_by)))

    # -- the sample
    sample = [r for r in read_tsv(os.path.join(HERE, "sample.tsv"))] if os.path.exists(
        os.path.join(HERE, "sample.tsv")) else []
    gains = read_tsv(os.path.join(HERE, "gains.tsv")) if os.path.exists(os.path.join(HERE, "gains.tsv")) else []
    n_s = len(sample)
    raised = [r for r in sample if int(r["score"]) > int(r["known_before"])]
    before = [r for r in sample if int(r["known_before"]) > int(r["frame_best_known"])]
    print(f"\nSAMPLE: {n_s} of {T} targets played (seed 71, level 4); raised {len(raised)}; "
          f"raised since the frame by another play before their own: {len(before)}")
    by_h = collections.Counter(r["stratum"] for r in sample)
    up_h = collections.Counter(r["stratum"] for r in raised)
    T_h = collections.Counter(str(min(int(t["plays"]), 3)) for t in targets)
    for h in sorted(T_h):
        print(f"  stratum {h} (plays so far {h if h != '3' else '3+'}): {by_h[h]} of {T_h[h]} played, {up_h[h]} raised")
    if n_s:
        print(f"  seconds a play: mean {np.mean([float(r['seconds']) for r in sample]):.0f}")
    for g in gains:
        print(f"  gain at {g['n']}: +{g['gain']}; raised {g['games_raised']} games {g['lo']}-{g['hi']}, "
              f"{g['points']} points ({g['below_windows']} windows below, {g['above_windows']} above)")
    k = len(raised)

    # -- streaks: games L and targets k_s of each (a target is a game no proved rule settles from the one below)
    tset = {int(t["n"]) for t in targets}
    unit_of = {m: u for u, ms in MERGED.items() for m in ms}
    raised_by = collections.defaultdict(set)
    for r in read_csv(os.path.join(WORK, "gapdash", "model", "v3c", "raised.csv")):
        root = int(r["first_root"])
        raised_by[unit_of.get(root, root)].add(int(r["n"]))
    pilot = [(len(g), max(1, len(g & tset))) for g in raised_by.values()]
    rehearsal = collections.defaultdict(lambda: [0, 0])
    for r in read_csv(os.path.join(HERE, "calib", "roots.csv")):
        if r["state"].endswith("P3"):
            key = (r["state"], r["streak"])
            rehearsal[key][0] += 1
            rehearsal[key][1] += r["root"] == "yes" or (r["method"] == "search" and r["at_ceiling"] == "False")
    rehearsal = [tuple(v) for v in rehearsal.values()]
    for g in gains:
        games = {int(m) for m in g["games"].split()}
        pilot.append((len(games), max(1, len(games & tset))))
    for name, pool in (("the pilot's units past 5060 and this sample's gains", pilot),
                       ("the rehearsals' streaks after pass 3", rehearsal)):
        L = np.array([a for a, _ in pool])
        K = np.array([b for _, b in pool])
        print(f"\nSTREAKS, {name}: {len(pool)}; games mean {L.mean():.2f} (median {np.median(L):.0f}, largest "
              f"{L.max()}); targets in a streak mean {K.mean():.2f}; games per target {L.sum() / K.sum():.2f}")

    # -- how a target inside a streak yields, against a root (level 4, pooled over instances)
    fol = by_instance(plays, "follower3", 4)
    r4 = by_instance(plays, "root3", 4)
    if fol:
        keys = list(fol)
        kf = np.array([fol[x][0] for x in keys], dtype=float)
        mf = np.array([fol[x][1] for x in keys], dtype=float)
        pick = rng.integers(0, len(keys), size=(B, len(keys)))
        d_fol = rng.beta(kf[pick] + 0.5, mf[pick] - kf[pick] + 0.5).mean(axis=1)
        rho = np.minimum(d_fol / np.maximum(dB[:, :, 2].mean(axis=1), 1e-9), 1.0)
        rho_pt = min((kf / mf).mean() / np.mean([a / b for a, b in r4.values()]), 1.0)
    else:
        rho, rho_pt = np.zeros(B), 0.0
    print(f"\nFOLLOWERS: a target inside a streak yields at rho = {rho_pt:.2f} times a root's rate (95% "
          f"{np.quantile(rho, 0.025):.2f}-{np.quantile(rho, 0.975):.2f}, capped at 1)")

    # -- the estimate
    print(f"\nESTIMATE (T = {T} targets, sample n = {n_s}, raised k = {k}, f = n / T = {n_s / max(T, 1):.3f})")
    if n_s == 0:
        return
    f = n_s / T
    print("  A streak with k_s targets is raised by the sample with expected count f d D_s, D_s = 1 + (k_s - 1) rho.  "
          "The detection mass M = sum_s D_s is Gamma(k + 1) with rate f d (flat prior, Poisson counts).  Streaks and "
          "games are M times the pool's streaks and games per unit of D: for a pool of streaks that were found by "
          "single-game plays (found with chance proportional to D_s) the means of 1 / D_s and L_s / D_s; for the "
          "rehearsals' streaks, which are all the streaks of their states, n / sum D_s and sum L_s / sum D_s.")
    found_pool = pilot
    rows = []
    for dname, (d_pt, d_draws) in dbar.items():
        for pname, pool, biased in (("found streaks (pilot and sample)", found_pool, True),
                                    ("rehearsal streaks", rehearsal, False)):
            for rname, rr, r_pt in (("rho measured", rho, rho_pt), ("rho = 0", np.zeros(B), 0.0),
                                    ("rho = 1", np.ones(B), 1.0)):
                S, G = streaks_and_games(k, f, d_draws, rr, pool, biased)
                S0, G0 = point_estimate(k, f, d_pt, r_pt, pool, biased)
                rows.append((dname, pname, rname, S0, np.quantile(S, CONF), G0, np.quantile(G, 0.90),
                             np.quantile(G, CONF)))
    print(f"  {'d':45} {'streak pool':34} {'rho':12} {'streaks':>8} {'95% up':>7} {'games':>7} {'90% up':>7} "
          f"{'95% up':>7}")
    for r in rows:
        print(f"  {r[0]:45} {r[1]:34} {r[2]:12} {r[3]:8.1f} {r[4]:7.1f} {r[5]:7.0f} {r[6]:7.0f} {r[7]:7.0f}")
    # the stratified reading: each stratum's raises over its own d (after prior plays, every target alike)
    p_by, b_by = dby
    L = np.array([a for a, _ in found_pool], dtype=float)
    K = np.array([b for _, b in found_pool], dtype=float)
    per_s, per_g = pool_ratios(L, K, rho_pt, True)
    pick = rng.integers(0, len(found_pool), size=(B, len(found_pool)))
    bs, bg = pool_ratios(L[pick], K[pick], rho[:, None], True)
    M_pt, M_low = 0.0, np.zeros(B)
    print("  Stratified reading (d after prior plays, every target alike; found streaks; rho measured):")
    for h in sorted(T_h):
        hh = int(h)
        f_h = by_h[h] / T_h[h]
        if by_h[h] == 0:
            continue
        m_pt = up_h[h] / (f_h * p_by[hh][0])
        M_pt += m_pt
        draws = rng.gamma(up_h[h] + 1, 1.0 / (f_h * b_by[hh]))
        if hh <= 1:
            M_low = M_low + draws
        print(f"    stratum {h}: k {up_h[h]} of {by_h[h]}, d {p_by[hh][0]:.3f}: detection mass {m_pt:.1f}, games "
              f"{m_pt * per_g:.0f}; 95% upper on its games with a flat prior "
              f"{np.quantile(draws * bg, CONF):.0f}")
    print(f"    all strata: games {M_pt * per_g:.0f} (streaks {M_pt * per_s:.1f}); strata 0 and 1 together (1,049 "
          f"targets with at most one earlier play): 95% upper on their games {np.quantile(M_low * bg, CONF):.0f}")
    r_up = r_upper(T, n_s, k, 0.975)
    d_lo = np.quantile(dbar["size-matched, after prior plays, roots thinned by the plays"][1], 0.025)
    print(f"  Bonferroni: raised targets in the frame <= {r_up} (hypergeometric, 97.5%), d >= {d_lo:.3f} (97.5%): "
          f"detection mass M <= {r_up / d_lo:.0f}")


def r_upper(T, n, k, conf):
    """The largest number R of raisable targets in the frame with P(at most k in a sample of n) >= 1 - conf."""
    R = k
    while R + 1 <= T and stats.hypergeom.cdf(k, T, R + 1, n) >= 1 - conf:
        R += 1
    return R


def pool_ratios(L, K, rho, biased):
    """Streaks and games per unit of detection mass D = 1 + (K - 1) rho, for one resample (arrays) of a pool."""
    D = 1 + (K - 1) * rho
    if biased:
        return (1 / D).mean(axis=-1), (L / D).mean(axis=-1)
    return K.shape[-1] / D.sum(axis=-1), L.sum(axis=-1) / D.sum(axis=-1)


def streaks_and_games(k, f, d_draws, rho_draws, pool, biased):
    """For each draw of d and rho, a resample of the pool and M ~ Gamma(k + 1, rate f d): (streaks, games)."""
    L = np.array([a for a, _ in pool], dtype=float)
    K = np.array([b for _, b in pool], dtype=float)
    pick = rng.integers(0, len(pool), size=(len(d_draws), len(pool)))
    per_s, per_g = pool_ratios(L[pick], K[pick], rho_draws[:, None], biased)
    M = rng.gamma(k + 1, 1.0 / np.maximum(f * d_draws, 1e-12))
    return M * per_s, M * per_g


def point_estimate(k, f, d, rho, pool, biased):
    """k / (f d) units of detection mass, times the pool's streaks and games per unit."""
    L = np.array([a for a, _ in pool], dtype=float)
    K = np.array([b for _, b in pool], dtype=float)
    per_s, per_g = pool_ratios(L, K, rho, biased)
    M = k / (f * d)
    return M * per_s, M * per_g


if __name__ == "__main__":
    main()
