#!/usr/bin/env python3
"""Extract, once, every run's line of every game of 3001-5060 into plays.csv.gz, with its promotions as differences
from the proven set.

    cd /home/brian/taxman_work/lab/work/gapdash/hard && nice -n 19 python3 -I extract.py

Plain Python 3, standard library only.  Reads the runs that common.runs() names: the 19 chains of B14 and B17, and
each rehearsal's passes that its run.log says have ended (a pass still running is left out).  Prints the time of the
read and each run's count of lines.

One row a run and a game: the run's line of the game (its highest score, the first such line on a tie), with
first_score (its first line's, the game as played in order) and last_score (its last line's).  The promotions are
written as `extra` (the line's promotions that the proven set lacks) and `missing` (the proven set's that the line
lacks), so a line at opt(n) with the proven set has both empty.  The search keys: `impr`, one "round.trajectory.stage.
score" per improvement; `traj`, the trajectories' sources; `surv`, "game:score" of each survivor.
"""

import csv
import gzip
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves this folder off the path
from common import HI, LO, PLAYS, lines, load_opt, runs  # noqa: E402

FIELDS = ["run", "family", "pass", "n", "nlines", "score", "first_score", "last_score", "method", "seed", "effort",
          "stop_growth", "at_ceiling", "ceiling", "prev_score", "prev_source", "unseeded", "pushed", "other_score",
          "growth", "growth_stop", "rounds", "work", "start", "ntraj", "traj", "surv", "n_impr", "impr", "stage_rounds",
          "repaired_from", "descent_root", "known_before", "in_the_bag", "bound", "npromo", "frames", "cands",
          "max_total", "greedy_sum", "digest", "extra", "missing"]


def blank(v):
    return "" if v is None else v


def record(x, opt):
    n = x["n"]
    prev = x.get("prev") or {}
    other = x.get("other") or {}
    setup = x.get("setup") or {}
    promos = set(x.get("promotions") or [])
    proven = opt[n]["promotions"]
    impr = x.get("improvements") or []
    return {
        "n": n, "score": x["score"], "method": x["method"], "seed": x.get("seed"), "effort": x.get("effort"),
        "stop_growth": blank(x.get("stop_growth")), "at_ceiling": int(bool(x.get("at_ceiling"))),
        "ceiling": blank(x.get("ceiling")), "prev_score": blank(prev.get("score")),
        "prev_source": blank(prev.get("source")), "unseeded": int(bool(x.get("unseeded"))),
        "pushed": int(bool(x.get("pushed"))), "other_score": blank(other.get("score")),
        "growth": blank(x.get("growth")), "growth_stop": int(bool(x.get("growth_stop"))),
        "rounds": x.get("rounds") or 0, "work": x.get("work") or 0, "start": blank(x.get("start")),
        "ntraj": len(x.get("trajectories") or []),
        "traj": " ".join(str(t) for t in (x.get("trajectories") or [])),
        "surv": " ".join(f"{m}:{s}" for m, s in (x.get("survivor_scores") or [])),
        "n_impr": len(impr),
        "impr": " ".join(f"{i['round']}.{i['trajectory']}.{i['stage']}.{i['score']}" for i in impr),
        "stage_rounds": " ".join(".".join(str(r) for r in s) for s in (x.get("stage_rounds") or [])),
        "repaired_from": blank((x.get("repaired") or {}).get("from")),
        "descent_root": blank((x.get("descent") or {}).get("root")),
        "known_before": blank(x.get("known_before")),
        "in_the_bag": blank(x.get("in_the_bag")), "bound": blank(x.get("bound")), "npromo": len(promos),
        "frames": blank(setup.get("frames")), "cands": blank(setup.get("candidates")),
        "max_total": blank(setup.get("max_total")), "greedy_sum": blank(setup.get("greedy_sum")),
        "digest": blank(setup.get("digest")),
        "extra": " ".join(str(p) for p in sorted(promos - proven)),
        "missing": " ".join(str(p) for p in sorted(proven - promos)),
    }


def main():
    print("read at", time.strftime("%Y-%m-%d %H:%M %Z"), file=sys.stderr)
    opt = load_opt(LO - 1, HI)
    with gzip.open(PLAYS, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for run, family, k, path in runs():
            best, first, last, count = {}, {}, {}, {}
            for x in lines(path):
                n = x["n"]
                if not LO <= n <= HI:
                    continue
                count[n] = count.get(n, 0) + 1
                first.setdefault(n, x["score"])
                last[n] = x["score"]
                if n not in best or x["score"] > best[n]["score"]:
                    best[n] = record(x, opt)
            for n in sorted(best):
                w.writerow({"run": run, "family": family, "pass": k, "nlines": count[n], "first_score": first[n],
                            "last_score": last[n], **best[n]})
            print(f"{run}: {os.path.basename(path)}, {sum(count.values())} lines, {len(best)} games, "
                  f"{sum(1 for n in best if last[n] < best[n]['score'])} with a last line below the best",
                  file=sys.stderr)


if __name__ == "__main__":
    main()
