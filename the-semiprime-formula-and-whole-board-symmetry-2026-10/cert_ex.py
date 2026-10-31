"""The exhaustive solver of heuristics/evaluation/certify.py on the games named on the command line: the best score and
every optimal set.  It reads the heuristics of a checkout of the main repository at commit 2896cdd: the folder named by
TAXMAN_REPO, or the current folder.
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.environ.get('TAXMAN_REPO', '.'), 'heuristics'))
from core import divisor_lists
from evaluation.certify import Exact
for n in map(int, sys.argv[1:]):
    t = time.time()
    ex = Exact(n, divisor_lists(n), time.monotonic() + 3000)
    pot = ex.normalize(sum(1 << c for c in range(1, n + 1)))
    best = ex.best(pot)
    sets = ex.optimal_pick_sets(pot, cap=1000)
    print(n, best, [sorted(s) for s in sets], round(time.time() - t, 1), flush=True)
