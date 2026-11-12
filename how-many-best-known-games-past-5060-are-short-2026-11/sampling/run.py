#!/usr/bin/env python3
"""The sampling test's plays: the calibration on the rehearsal states and the sample of the targets past 5060.

    cd /home/brian/taxman_work/lab/work/sampling && nohup python3 -I run.py > run.log 2>&1 &

Six lanes of 12 threads (72 in all), each play at idle priority (chrt -i 0 nice -n 19).  Lanes 0 and 1 take the
calibration's jobs first and lanes 2 to 5 the sample's; a lane whose queue is empty takes the other's.

* **Calibration** (calib/jobs.csv, made below): one game of a rehearsal state at one level and seed, played alone into
  a fresh copy of that state's best-known file (calib/states/, made by calib/make_states.py), never the production
  file: `solve n-n --unsound --stop-growth off --known-to 3000 --best-known COPY --threads 12 --effort L --seed S`.
  The copy is deleted after the play; the play's line is calib/plays/STATE-gN-lL-sS.jsonl.  A play whose file has a
  line of its game is done; one without is played again from scratch.
* **The sample** (sample-order.csv, made by draw.py): one level-4 play of each target on seed 71, which no play past
  5060 has used, into the shared best-known file, in the order's sequence; no new sample play starts after STOP_AT,
  a clock time fixed before the run began, so the plays reached are a stratified random sample whatever they find.
  Each play is recorded in rootfirst/ledger2.tsv as succession/lawscan/play.sh records it (game, level, seed, known
  score, new score, time), and in sample.tsv here.  A target with a ledger2 row for level 4 and seed 71 is not played
  again; a play whose file lacks its game's line is run again with the same command, which goes on where it stopped.
* **A gain** (the play's score above its known score) is pushed down as rootfirst/pushdown-watch.sh does (the 8 games
  below at level 3 on seed 41, and on down while the lowest game of a window is raised) and carried up as
  rootfirst/run.sh's carry does (windows of 20 at level 3 on seed 71 while the top game of a window rises), all into
  the shared best-known file, with their files in plays/ here (belowN-s41, upN-s71-FROM).  gains.tsv records each.
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime

WORK = "/home/brian/taxman_work/lab/work"
HERE = os.path.dirname(os.path.abspath(__file__))
TAXMAN = os.path.join(WORK, "unsound-run", "taxman-aeffc29")
BK = os.path.join(WORK, "unsound-run", "best-known.jsonl")
LEDGER = os.path.join(WORK, "rootfirst", "ledger2.tsv")
IDLE = ["chrt", "-i", "0", "nice", "-n", "19"]
THREADS = 12
LANES = 6
CALIB_LANES = (0, 1)
LEVEL, SEED = 4, 71
STOP_AT = datetime(2026, 11, 11, 11, 30)  # local (Pacific) time: no sample play starts after it
CAL_SEEDS3 = (71, 72, 73, 74, 75, 76)     # the roots of the states after pass 3, at levels 4, 3 and 2
CAL_SEEDS = (71, 72, 73, 74)              # the roots after pass 2 and the followers after pass 3, at level 4

lock = threading.Lock()


def now():
    return datetime.now().strftime("%H:%M:%S")


def say(text):
    with lock:
        print(f"{now()} {text}", flush=True)


def lines_of(path):
    out = []
    if os.path.exists(path):
        with open(path) as f:
            for t in f:
                if t.strip():
                    try:
                        out.append(json.loads(t))
                    except json.JSONDecodeError:
                        pass  # a torn last line of a stopped run
    return out


def last_line(path, n):
    found = [d for d in lines_of(path) if d["n"] == n]
    return found[-1] if found else None


def raised_in(path):
    """{n: (known_before, score)} of the games of a run file that its run raised, the last line of each game."""
    seen = {}
    for d in lines_of(path):
        seen[d["n"]] = (d.get("known_before") or 0, d["score"])
    return {n: ks for n, ks in seen.items() if ks[1] > ks[0]}


def solve(lo, hi, level, seed, out, extra):
    cmd = IDLE + [TAXMAN, "solve", f"{lo}-{hi}", "--unsound", "--stop-growth", "off", *extra, "--threads",
                  str(THREADS), "--effort", str(level), "--seed", str(seed), "--out", out]
    with open(out[:-len(".jsonl")] + ".log", "a") as log:
        return subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).returncode


# -- the calibration ------------------------------------------------------------------------------------------------

def calib_jobs():
    path = os.path.join(HERE, "calib", "jobs.csv")
    if not os.path.exists(path):
        with open(os.path.join(HERE, "calib", "roots.csv")) as f:
            rows = list(csv.DictReader(f))
        roots3 = [(r["state"], int(r["n"])) for r in rows if r["root"] == "yes" and r["state"].endswith("P3")]
        roots2 = [(r["state"], int(r["n"])) for r in rows if r["root"] == "yes" and r["state"].endswith("P2")]
        followers = [(r["state"], int(r["n"])) for r in rows if r["root"] == "no" and r["state"].endswith("P3")
                     and r["method"] == "search" and r["at_ceiling"] == "False"]
        jobs = [("root3", s, n, 4, k) for s, n in roots3 for k in CAL_SEEDS3]
        jobs += [("root3", s, n, 3, k) for s, n in roots3 for k in CAL_SEEDS3]
        jobs += [("root2", s, n, 4, k) for s, n in roots2 for k in CAL_SEEDS]
        jobs += [("follower3", s, n, 4, k) for s, n in followers for k in CAL_SEEDS]
        jobs += [("root3", s, n, 2, k) for s, n in roots3 for k in CAL_SEEDS3]
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["kind", "state", "n", "level", "seed"])
            w.writerows(jobs)
    with open(path) as f:
        return [(r["kind"], r["state"], int(r["n"]), int(r["level"]), int(r["seed"])) for r in csv.DictReader(f)]


def calib_play(job):
    kind, state, n, level, seed = job
    name = f"{state}-g{n}-l{level}-s{seed}"
    out = os.path.join(HERE, "calib", "plays", name + ".jsonl")
    if last_line(out, n) is None:
        for stale in (out, out[:-len(".jsonl")] + ".log"):
            if os.path.exists(stale):
                os.remove(stale)
        copy = os.path.join(HERE, "calib", "tmp", name + ".jsonl")
        shutil.copyfile(os.path.join(HERE, "calib", "states", state + ".jsonl"), copy)
        began = time.time()
        code = solve(n, n, level, seed, out, ["--known-to", "3000", "--best-known", copy])
        os.remove(copy)
        line = last_line(out, n)
        if code != 0 or line is None:
            say(f"calibration {name} failed (exit {code}), see {out[:-6]}.log")
            return
        say(f"calibration {name}: {line.get('known_before')} -> {line['score']} ({time.time() - began:.0f} s)")


# -- the sample -----------------------------------------------------------------------------------------------------

def ledger_row(n):
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            for t in f:
                p = t.rstrip("\n").split("\t")
                if len(p) >= 5 and p[0] == str(n) and p[1] == str(LEVEL) and p[2] == str(SEED):
                    return p
    return None


def append(path, text):
    with lock:
        with open(path, "a") as f:
            f.write(text)


def pushdown(n):
    """The 8 games below n at level 3 on seed 41, and on down while the lowest game of a window is raised."""
    top, windows = n, []
    while top > 5069:
        out = os.path.join(HERE, "plays", f"below{top}-s41.jsonl")
        if last_line(out, top - 1) is None:
            if solve(top - 8, top - 1, 3, 41, out, ["--best-known", BK]) != 0:
                say(f"push-down below {top} failed")
                break
        up = raised_in(out)
        windows.append((top, up))
        say(f"below {top}: " + (", ".join(f"{m} +{s - k}" for m, (k, s) in sorted(up.items())) or "nothing raised"))
        if top - 8 not in up:
            break
        top -= 8
    return windows


def carry(n):
    """The games above n in windows of 20 at level 3 on seed 71, while the top game of a window rises."""
    frm, windows = n + 1, []
    while frm <= 10000:
        top = min(frm + 19, 10000)
        out = os.path.join(HERE, "plays", f"up{n}-s{SEED}-{frm}.jsonl")
        if last_line(out, top) is None:
            if solve(frm, top, 3, SEED, out, ["--best-known", BK]) != 0:
                say(f"carry of {n} at {frm}-{top} failed")
                break
        line = last_line(out, top)
        up = raised_in(out)
        windows.append((frm, up))
        say(f"carry of {n}: {frm}-{top}, top game {line.get('known_before')} -> {line['score']}")
        if not line["score"] > (line.get("known_before") or 0):
            break
        frm = top + 1
    return windows


def sample_play(row):
    order, n = int(row["order"]), int(row["n"])
    out = os.path.join(HERE, "plays", f"g{n}-l{LEVEL}-s{SEED}.jsonl")
    began = time.time()
    if ledger_row(n) is None:
        if last_line(out, n) is None:
            code = solve(n, n, LEVEL, SEED, out, ["--best-known", BK])
            if code != 0 or last_line(out, n) is None:
                say(f"sample play of {n} failed (exit {code}); the lane stops")
                return False
        line = last_line(out, n)
        append(LEDGER, f"{n}\t{LEVEL}\t{SEED}\t{line.get('known_before') or 0}\t{line['score']}\t{now()}\n")
    line = last_line(out, n)
    if line is None:
        say(f"sample play of {n} is in ledger2 but has no file here; left out")
        return True
    known, score = line.get("known_before") or 0, line["score"]
    seconds = sum(d.get("seconds") or 0 for d in lines_of(out))
    say(f"sample {order}: {n} {known} -> {score} ({time.time() - began:.0f} s)")
    if score > known:
        own = raised_in(out)
        below = pushdown(n)
        above = carry(n)
        games = dict(own)
        for _, up in below + above:
            games.update(up)
        points = sum(s - k for k, s in games.values())
        append(os.path.join(HERE, "gains.tsv"),
               f"{order}\t{n}\t{score - known}\t{min(games)}\t{max(games)}\t{len(games)}\t{points}\t"
               f"{len(below)}\t{len(above)}\t{' '.join(str(m) for m in sorted(games))}\t{now()}\n")
        say(f"gain at {n}: streak {min(games)}-{max(games)}, {len(games)} games raised, {points} points")
    # written last, so that a run stopped in a gain's push-down or carry goes on with it when started again
    append(os.path.join(HERE, "sample.tsv"), f"{order}\t{n}\t{row['stratum']}\t{row['best_known']}\t{known}\t"
                                              f"{score}\t{score - known}\t{seconds:.1f}\t{now()}\n")
    return True


# -- the lanes ------------------------------------------------------------------------------------------------------

def main():
    with open(os.path.join(HERE, "sample-order.csv")) as f:
        order = list(csv.DictReader(f))
    heads = {"sample.tsv": "order\tn\tstratum\tframe_best_known\tknown_before\tscore\tgain\tseconds\ttime\n",
             "gains.tsv": "order\tn\tgain\tlo\thi\tgames_raised\tpoints\tbelow_windows\tabove_windows\tgames\ttime\n"}
    for name, head in heads.items():
        if not os.path.exists(os.path.join(HERE, name)):
            append(os.path.join(HERE, name), head)
    with open(os.path.join(HERE, "sample.tsv")) as f:
        done = {int(t.split("\t")[1]) for t in f if t[:1].isdigit()}
    sample_q = [r for r in order if int(r["n"]) not in done]
    calib_q = [j for j in calib_jobs()
               if last_line(os.path.join(HERE, "calib", "plays", f"{j[1]}-g{j[2]}-l{j[3]}-s{j[4]}.jsonl"), j[2])
               is None]
    say(f"start: {len(calib_q)} calibration plays to go, {len(done)} sample plays done, stop at {STOP_AT}")

    def take(queue):
        with lock:
            return queue.pop(0) if queue else None

    def lane(i):
        prefer = ("calib", "sample") if i in CALIB_LANES else ("sample", "calib")
        stopped = False
        while True:
            job = None
            for q in prefer:
                if q == "calib":
                    job = take(calib_q)
                    if job:
                        calib_play(job)
                        break
                elif not stopped and datetime.now() < STOP_AT:
                    job = take(sample_q)
                    if job:
                        if not sample_play(job):
                            stopped = True
                        break
            if job is None:
                say(f"lane {i} done")
                return

    threads = [threading.Thread(target=lane, args=(i,)) for i in range(LANES)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    say("all lanes done")


if __name__ == "__main__":
    sys.exit(main())
