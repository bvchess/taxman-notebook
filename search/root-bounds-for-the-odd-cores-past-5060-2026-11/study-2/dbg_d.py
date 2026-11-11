import sys, json
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore/study-2")
from lib import Board
from split import Split, SMOOTH
from mi import max_weight_common
from exp_d import hubs_paid_in_peel
n = 1000
b = Board(n); line = b.opt_line(); s = set(line["moves"]); sp = Split(b)
half = n // 2
s_sm = sorted(x for x in s if x <= half and b.lp[x] <= SMOOTH)
s_fb = sorted(x for x in s if x <= half and b.lp[x] > SMOOTH)
print("S* smooth promotions", sum(s_sm), len(s_sm), "fiber", sum(s_fb), len(s_fb), "layers2?", [x for x in s if x <= half and b.om[x] < 3])
xstar = hubs_paid_in_peel(b, s)
xs = {h for h in xstar if b.lp[h] <= SMOOTH and h <= half}
print("X* smooth hubs", sorted(xs), "nonsmooth", sorted(xstar - xs))
ok, k, lists = sp.smooth_playable(s_sm, xs)
print("S* smooth config playable with X* deleted:", ok, k)
base = sp.base_vectors(sp.smooth_sources, xs)
try:
    ch, v = max_weight_common({x: sp.smooth_elems[x] for x in sp.smooth_elems if x not in xs}, base[0], base[1], picks=s_sm)
    print("smooth MI with S* picked:", v, "chosen", len(ch))
except ValueError as e:
    print("smooth picks dependent:", e)
base = sp.base_vectors(sp.fiber_sources, [h for h in sp.hubs if h not in xs])
try:
    ch, v = max_weight_common(dict(sp.fiber_elems), base[0], base[1], picks=s_fb)
    print("fiber MI with S* picked:", v, "chosen", len(ch))
except ValueError as e:
    print("fiber picks dependent:", e)
# which candidates of S* are missing from the element sets?
print("missing smooth", [x for x in s_sm if x not in sp.smooth_elems], "missing fiber", [x for x in s_fb if x not in sp.fiber_elems])
