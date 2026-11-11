#!/usr/bin/env python3
"""E5, templates as local losses (layer 4), for the study in study-report-1.md Section 5.

    nice -n 19 python3 -I -B e5.py [--light] N [N ...]   # a report a board in out/boardN.md and out/boardN.json, and on
                                                         # stdout; --light skips the mixed-core count and the search
                                                         # for the outside numbers a repair needs
    nice -n 19 python3 -I -B e5.py --summary             # one table of the instances of every board in out/

For each board n it takes the parity bound's heaviest set H (parity.py) and the recorded optimal set S* (the "moves" of
results/optimal.jsonl.gz) and, in layer 4 of H's own instance (cores.py's definitions):

1. extracts minimal cores whose members are all *fiber* members (largest prime above B = 23): the template cores.  Cores
   with a smooth member (largest prime up to 23) are the layer's smooth knot, counted but not listed;
2. groups the template cores into *instances*: cores that share a fiber prime are one instance;
3. takes an instance's *territory* to be the fibers of its primes (every number up to n/2 whose largest prime is one of
   them) and its hubs (the cofactors x/P, all below n/P), and lists what S* drops (in H, not in S*) and adds (in S*, not
   in H) there, with the loss: the weight of H less the weight of S* on the territory;
4. tests the repair: H with only the instance's territory differences swapped to S*'s (a "local repair") must break
   every template core of the instance and create no residual in any layer that H does not already have; it searches
   all subsets of the territory differences for the cheapest such local repair;
5. classifies every difference between H and S* (numbers up to n/2; the sources agree) by the largest prime of the
   number: template fiber, other residual fiber, smooth (up to 23), unrelated fiber, and hub.
"""

import json
import os
import random
import sys
from itertools import combinations

sys.dont_write_bytecode = True
sys.path.insert(0, "/home/brian/taxman_work/lab/work/oddcore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cores as C  # noqa: E402
import fetch  # noqa: E402
import parity as P  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LAYER = 4
SMOOTH = 23  # members whose largest prime is above this are fiber members
BASES = {  # the base cofactors of the templates of brief.md Section 2.4 (T11 also with the cofactor 8 of its variants)
    "T11": {8, 12, 18, 20, 27, 30},
    "T14": {45, 50, 63, 70, 75, 98, 105},
    "T23": {28, 30, 42, 45, 50, 52, 63, 70, 75, 78},
}
MIXED_ORDERS = 200  # random orders on the whole residual, to count its mixed cores
EXHAUSTIVE = 12  # all subsets of the territory differences up to this many, else none


class Board:
    """H, S* and the arithmetic of one board."""

    def __init__(self, n):
        self.n = n
        d = fetch.load_board(n)
        self.d = d
        self.om, self.mf = P.omega_and_mf(n)
        self.h = set(d["greedy_basis"]) | set(d["heaviest_low"])
        self.s = set(d["moves"])
        self.half = n // 2
        assert not {x for x in self.h ^ self.s if x > self.half}, "H and S* hold different sources"

    def gpf(self, x):
        return x // self.mf[x][0]

    def layer_residual(self, h, k):
        """The residual of layer k's own instance of h (cores.py's dismantling)."""
        layer = [x for x in h if self.om[x] == k]
        lists = {x: {f for f in self.mf[x] if f not in h} for x in layer}
        return C.residual(layer, lists)

    def residuals(self, h, layers):
        return {k: self.layer_residual(h, k) for k in layers}

    def fmt(self, x):
        p = self.gpf(x)
        return f"{x // p}x{p}" if p > SMOOTH else str(x)


def template_cores(b, h4, lists, rng, patience=150, cap=2000):
    """The fiber-only residual of layer 4 and the distinct minimal cores sampled in it by random deletion orders."""
    fibers = [x for x in h4 if b.gpf(x) > SMOOTH]
    rf = C.residual(fibers, lists)
    found, stale, tried = {}, 0, 0
    members = sorted(rf)
    while rf and stale < patience and tried < cap:
        order = members[:]
        rng.shuffle(order)
        c = frozenset(C.minimal_core(set(rf), lists, order))
        tried += 1
        if c in found:
            found[c] += 1
            stale += 1
        else:
            found[c] = 1
            stale = 0
    return rf, found, tried


def group_by_prime(b, cores):
    """Instances: the cores that share a fiber prime, merged."""
    groups = []  # [set of primes, list of cores]
    for c in sorted(cores, key=lambda c: (len(c), sorted(c))):
        primes = {b.gpf(x) for x in c}
        hit = [g for g in groups if g[0] & primes]
        merged = [primes, [c]]
        for g in hit:
            merged[0] |= g[0]
            merged[1] += g[1]
            groups.remove(g)
        groups.append(merged)
    return sorted(groups, key=lambda g: min(g[0]))


def pattern(b, members):
    """The base pattern: for each largest prime, the sorted cofactors of the members."""
    out = {}
    for x in members:
        out.setdefault(b.gpf(x), []).append(x // b.gpf(x))
    return {p: sorted(v) for p, v in sorted(out.items())}


def template_name(pat):
    union = {m for v in pat.values() for m in v}
    for name in ("T11", "T14", "T23"):
        if union <= BASES[name]:
            return name
    return "other"


def territory_test(b, inst):
    """A predicate for the territory of an instance: its fibers up to n/2, and its hubs."""
    primes = inst["primes"]
    hub_max = b.n // min(primes)

    def where(x):
        if b.gpf(x) in primes:
            return "fiber"
        if x <= hub_max:
            return "hub"
        return None

    return where


class Checker:
    """Tests whether a swap of H toward S* is *clean* for a set of instances.

    The swap removes its drops from H and puts its adds in.  It is clean when, for every instance named, the
    fiber-only instance of the instance's primes in layer 4 (the template and its twins, nothing smooth) has no
    residual,
    so every template core is broken, and no layer has a residual member that H's does not have.
    """

    def __init__(self, b, instances):
        self.b = b
        self.primes = {inst["id"]: set(inst["primes"]) for inst in instances}
        self.layers = sorted({b.om[x] for x in b.h if b.om[x] >= 3})
        self._base = {}

    def base(self, k):
        if k not in self._base:
            self._base[k] = self.b.layer_residual(self.b.h, k)
        return self._base[k]

    def swap(self, items):
        h2 = set(self.b.h)
        for kind, x in items:
            if kind == "drop":
                h2.discard(x)
            else:
                h2.add(x)
        return h2

    def check(self, items, ids, layers=None):
        """(clean, template cores broken for every id, new residual by layer, residual members gone by layer)."""
        b = self.b
        h2 = self.swap(items)
        broken = True
        for i in ids:
            lists = {x: {f for f in b.mf[x] if f not in h2} for x in h2
                     if b.om[x] == LAYER and b.gpf(x) in self.primes[i]}
            if C.residual(list(lists), lists):
                broken = False
        new, gone = {}, {}
        for k in layers or self.layers:
            r = b.layer_residual(h2, k)
            if r - self.base(k):
                new[k] = sorted(r - self.base(k))
            if self.base(k) - r:
                gone[k] = len(self.base(k) - r)
        return broken and not new, broken, new, gone

    def touched(self, items):
        return sorted({self.b.om[x] + e for _, x in items for e in (0, 1)})

    def cheapest_subset(self, items, ids):
        """The subsets of the items (when there are at most EXHAUSTIVE) that are clean: the smallest, the cheapest."""
        if len(items) > EXHAUSTIVE:
            return None
        layers = self.touched(items)
        clean = []
        for size in range(1, len(items) + 1):
            for subset in combinations(items, size):
                if self.check(subset, ids, layers)[0]:
                    loss = sum(x for k, x in subset if k == "drop") - sum(x for k, x in subset if k == "add")
                    clean.append((loss, size, subset))
        out = {"clean_count": len(clean), "subsets": 2 ** len(items) - 1}
        if clean:
            smallest = min(c[1] for c in clean)
            loss, size, subset = min(clean, key=lambda c: (c[0], c[1]))
            out["cheapest"] = {"loss": loss, "items": [list(i) for i in subset]}
            out["smallest_size"] = smallest
            out["smallest"] = [{"loss": c[0], "items": [list(i) for i in c[2]]} for c in clean if c[1] == smallest][:6]
        return out

    def needed_outside(self, inside, outside, ids):
        """A minimal set of the outside differences that must come with the inside ones to make the swap clean.

        Starts from all the outside differences (S* itself, which is playable, so clean) and drops each in turn if the
        swap stays clean, passing over the set again until no difference can go (cleanness is not monotone, so one pass
        is not enough), in ascending and in descending order of number; returns the shorter result.
        """
        best = None
        for order in (sorted(outside, key=lambda i: i[1]), sorted(outside, key=lambda i: -i[1])):
            cur = list(outside)
            changed = True
            while changed:
                changed = False
                for it in order:
                    if it in cur:
                        trial = [z for z in cur if z != it]
                        if self.check(inside + trial, ids)[0]:
                            cur = trial
                            changed = True
            if best is None or len(cur) < len(best):
                best = cur
        return best


def analyze(n, light=False):
    b = Board(n)
    h, s = b.h, b.s
    rng = random.Random(1)
    h4 = [x for x in h if b.om[x] == LAYER]
    lists = {x: {f for f in b.mf[x] if f not in h} for x in h4}
    r4 = C.residual(h4, lists)
    rf, found, tried = template_cores(b, h4, lists, rng)
    # mixed (smooth-knot) cores are sampled on the whole residual, only to count them
    mixed = {}
    members = sorted(r4)
    for _ in range(0 if light else MIXED_ORDERS):
        order = members[:]
        rng.shuffle(order)
        c = frozenset(C.minimal_core(set(r4), lists, order))
        if any(b.gpf(x) <= SMOOTH for x in c):
            mixed[c] = 1
    smooth_in_residual = sorted(x for x in r4 if b.gpf(x) <= SMOOTH)

    groups = group_by_prime(b, list(found))
    instances = []
    for i, (primes, cores) in enumerate(groups, start=1):
        union = set().union(*cores)
        pat = pattern(b, union)
        hangers = sorted(x for x in rf if x not in union and b.gpf(x) in primes)
        instances.append({"id": i, "primes": sorted(primes), "cores": cores, "members": sorted(union),
                          "pattern": pat, "template": template_name(pat), "hangers": hangers})
    template_primes = {p for inst in instances for p in inst["primes"]}
    r4_primes = {b.gpf(x) for x in r4}
    only_h = sorted(x for x in h - s)
    only_s = sorted(x for x in s - h)

    def classify(x):
        q = b.gpf(x)
        for inst in instances:
            if territory_test(b, inst)(x) == "fiber":
                return f"template {inst['id']}"
        for inst in instances:
            if territory_test(b, inst)(x) == "hub":
                return "hub"
        if q <= SMOOTH:
            return "smooth"
        if q in r4_primes:
            return "other residual fiber"
        return "unrelated fiber"

    diffs = [(x, "drop") for x in only_h] + [(x, "add") for x in only_s]
    cls = {x: classify(x) for x, _ in diffs}

    chk = Checker(b, instances)
    all_items = [("drop", x) for x in only_h] + [("add", x) for x in only_s]
    assert chk.check(all_items, [inst["id"] for inst in instances])[0], "S* is not clean: the checker is wrong"
    ref = P.layer_residual(sorted(h), b.n, b.om, b.mf)  # parity.py's residual of every layer, as a check of ours
    for k in chk.layers:
        assert chk.base(k) == set(ref.get(k, {"members": []})["members"]), f"residual of layer {k} differs"
    for inst in instances:
        where = territory_test(b, inst)
        drops = [x for x in only_h if where(x)]
        adds = [x for x in only_s if where(x)]
        inst["drops"], inst["adds"] = drops, adds
        inst["loss"] = sum(drops) - sum(adds)
        inst["by_prime"] = {}
        for p in inst["primes"]:
            dp = [x // p for x in drops if b.gpf(x) == p]
            ap = [x // p for x in adds if b.gpf(x) == p]
            inst["by_prime"][p] = {"drop": dp, "add": ap, "c": sum(dp) - sum(ap)}
        inst["nonsource_members"] = [x for x in inst["members"] if x <= b.half]
        inside = [("drop", x) for x in drops] + [("add", x) for x in adds]
        ids = [inst["id"]]
        clean, broken, new, gone = chk.check(inside, ids)
        inst["alone"] = {"clean": clean, "broken": broken, "new": {k: [b.fmt(x) for x in v] for k, v in new.items()},
                         "gone": gone}
        inst["subsets"] = chk.cheapest_subset(inside, ids)
        if clean or light:
            inst["needs"] = []
        else:
            outside = [i for i in all_items if i not in inside]
            inst["needs"] = [list(i) for i in chk.needed_outside(inside, outside, ids)]
    # all the templates together
    inside = [i for i in all_items if cls[i[1]].startswith("template")]
    ids = [inst["id"] for inst in instances]
    clean, broken, new, gone = chk.check(inside, ids)
    joint = {"clean": clean, "broken": broken, "new": {k: [b.fmt(x) for x in v] for k, v in new.items()},
             "gone": gone, "loss": sum(x for k, x in inside if k == "drop") - sum(x for k, x in inside if k == "add")}
    joint["needs"] = [] if clean or light else [list(i) for i in chk.needed_outside(
        inside, [i for i in all_items if i not in inside], ids)]
    return b, {"n": n, "gap": b.d["gap"], "bound": b.d["bound"], "opt": b.d["opt"], "tried": tried,
               "r4": sorted(r4), "rf": sorted(rf), "smooth_in_residual": smooth_in_residual,
               "found": [(sorted(c), k) for c, k in found.items()], "mixed": len(mixed), "light": light,
               "mixed_sizes": sorted(len(c) for c in mixed), "instances": instances, "only_h": only_h,
               "only_s": only_s, "cls": cls, "template_primes": sorted(template_primes), "joint": joint,
               "layer_of": {x: b.om[x] for x in only_h + only_s}}


def items_text(b, items, cls=None):
    """Swap items as text: 'drop 45x29, add 42x29' (with the class of each number when cls is given)."""
    return ", ".join(f"{k} {b.fmt(x)}" + (f" ({cls[x]})" if cls else "") for k, x in items)


def render(b, r):
    n = r["n"]
    om = b.om
    out = []
    w = out.append
    w(f"## n = {n}: PB {r['bound']}, opt {r['opt']}, gap {r['gap']}")
    w("")
    w(f"H has {len(b.d['greedy_basis'])} sources and {len(b.d['heaviest_low'])} numbers up to n/2; S* differs from H "
      f"in {len(r['only_h'])} numbers (H only) and {len(r['only_s'])} (S* only), all up to n/2.  Layer 4's residual "
      f"has {len(r['r4'])} members; {len(r['rf'])} of them survive peeling the fiber members alone, "
      f"{len(r['smooth_in_residual'])} are smooth (largest prime up to {SMOOTH}).")
    w("")
    w(f"### Template cores (minimal cores of fiber members only; {len(r['found'])} distinct in {r['tried']} orders)")
    w("")
    w("| core | size | primes | base pattern (largest prime: cofactors) |")
    w("|---|---|---|---|")
    for i, (c, k) in enumerate(sorted(r["found"], key=lambda e: (len(e[0]), e[0])), start=1):
        pat = pattern(b, c)
        w(f"| c{i} | {len(c)} | {', '.join(map(str, pat))} | "
          + "; ".join(f"{p}: {','.join(map(str, v))}" for p, v in pat.items()) + " |")
    w("")
    w(f"Mixed cores (with a smooth member): {r['mixed']} distinct sampled"
      + (f", sizes {min(r['mixed_sizes'])}-{max(r['mixed_sizes'])}" if r["mixed"] else "") + ".")
    w("")
    w("### Instances")
    w("")
    w("| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | "
      "cheapest clean subset of it | outside numbers it needs |")
    w("|---|---|---|---|---|---|---|---|---|")
    for inst in r["instances"]:
        sub = inst["subsets"]
        if sub is None:
            cheap = "not searched"
        elif "cheapest" in sub:
            cheap = f"loss {sub['cheapest']['loss']}: " + items_text(b, sub["cheapest"]["items"])
        else:
            cheap = "none"
        needs = items_text(b, inst["needs"], r["cls"]) if inst["needs"] else "none"
        w(f"| I{inst['id']} | {inst['template']} | {', '.join(map(str, inst['primes']))} | {len(inst['cores'])} "
          f"| {len(inst['members'])} ({len(inst['nonsource_members'])}) | {inst['loss']} "
          f"| {'yes' if inst['alone']['clean'] else 'no'} | {cheap} | {needs} |")
    w("")
    for inst in r["instances"]:
        w(f"#### I{inst['id']} ({inst['template']}) on {', '.join(map(str, inst['primes']))}")
        w("")
        w("Pattern: " + "; ".join(f"{p}: {','.join(map(str, v))}" for p, v in inst["pattern"].items())
          + ".  Hangers: " + (", ".join(b.fmt(x) for x in inst["hangers"]) or "none") + ".")
        w("")
        w("| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] "
          "| c = Σdrop − Σadd |")
        w("|---|---|---|---|")
        for p in inst["primes"]:
            bp = inst["by_prime"][p]
            memset = set(inst["members"])
            dr = ", ".join(f"{k}{'*' if k * p in memset else ''} [L{om[k * p]}]" for k in bp["drop"]) or "-"
            ad = ", ".join(f"{k}{'*' if k * p in memset else ''} [L{om[k * p]}]" for k in bp["add"]) or "-"
            w(f"| {p} | {dr} | {ad} | {bp['c']} |")
        hubs = [x for x in r["only_h"] + r["only_s"] if territory_test(b, inst)(x) == "hub"]
        w("")
        w(f"(* = a member of one of the instance's template cores.)  Loss = Σ c·P = "
          + " + ".join(f"{inst['by_prime'][p]['c']}x{p}" for p in inst["primes"]) + f" = {inst['loss']}.  "
          f"Hubs changed: {hubs or 'none'}.")
        al = inst["alone"]
        w(f"S* swap on the territory alone: template cores broken = {al['broken']}, new residual "
          f"{al['new'] or 'none'}, residual members gone {al['gone'] or 'none'}.  "
          + ("Clean." if al["clean"] else "Not clean: it needs "
             + (items_text(b, inst["needs"], r["cls"]) if inst["needs"] else "?") + " as well."))
        sub = inst["subsets"]
        if sub:
            line = f"Subsets of the territory differences: {sub['clean_count']} clean of {sub['subsets']}."
            if "smallest" in sub:
                eg = "; ".join(f"{items_text(b, s['items'])} (loss {s['loss']})" for s in sub["smallest"][:3])
                line += f"  Smallest clean ones have {sub['smallest_size']} numbers: {eg}."
            w(line)
        w("")
    j = r["joint"]
    w(f"#### All templates together: loss {j['loss']}; template cores broken = {j['broken']}, new residual "
      f"{j['new'] or 'none'}; " + ("clean." if j["clean"] else "not clean, it needs "
                                   + (items_text(b, j["needs"], r["cls"]) if j["needs"] else "?") + " as well."))
    w("")
    w("### Differences by class (numbers up to n/2)")
    w("")
    cls = r["cls"]
    names = sorted(set(cls.values()), key=lambda c: (c.startswith("template") is False, c))
    w("| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |")
    w("|---|---|---|---|---|")
    tot = 0
    for c in names:
        dh = [x for x in r["only_h"] if cls[x] == c]
        ds = [x for x in r["only_s"] if cls[x] == c]
        layers = sorted({om[x] for x in dh + ds})
        loss = sum(dh) - sum(ds)
        tot += loss
        w(f"| {c} | {len(dh)}, {sum(dh)} | {len(ds)}, {sum(ds)} | {loss} | {','.join('L%d' % k for k in layers)} |")
    w(f"| total | {len(r['only_h'])}, {sum(r['only_h'])} | {len(r['only_s'])}, {sum(r['only_s'])} "
      f"| {tot} | gap {r['gap']} |")
    w("")
    l4 = [x for x in r["only_h"] + r["only_s"] if om[x] == LAYER]
    inside = [x for x in l4 if cls[x].startswith("template")]
    w(f"Layer-4 differences: {len(l4)}, of which {len(inside)} inside a template's fibers "
      f"({len(l4) - len(inside)} outside: "
      + ", ".join(f"{b.fmt(x)} ({cls[x]})" for x in sorted(l4) if x not in inside) + ").")
    w("")
    return "\n".join(out)


def signature(inst):
    """The swap of an instance as text, by prime: the cofactors dropped (-) and added (+)."""
    parts = []
    for p in inst["primes"]:
        bp = inst["by_prime"][str(p)]
        if bp["drop"] or bp["add"]:
            parts.append(f"{p}: " + " ".join([f"-{k}" for k in bp["drop"]] + [f"+{k}" for k in bp["add"]]))
    return "; ".join(parts) or "-"


def summary():
    """The instances of every board in out/ in one table by template, and one line a board."""
    rows, boards = [], []
    for name in os.listdir(f"{HERE}/out"):
        if name.startswith("board") and name.endswith(".json"):
            with open(f"{HERE}/out/{name}") as f:
                r = json.load(f)
            boards.append(r)
            for inst in r["instances"]:
                rows.append((inst["template"], r["n"], r, inst))
    rows.sort(key=lambda x: (x[0], x[1]))
    boards.sort(key=lambda r: r["n"])
    out = ["| template | n | primes | territory loss | swap in the territory (cofactors by prime) | "
           "T14 rule 3Σ(primes but the largest) | swap alone clean | cheapest clean subset | outside numbers needed |",
           "|---|---|---|---|---|---|---|---|---|"]
    for name, n, r, inst in rows:
        primes = inst["primes"]
        rule = 3 * sum(primes[:-1]) if name == "T14" else ""
        sub = inst["subsets"]
        cheap = "-" if not sub else (str(sub["cheapest"]["loss"]) if "cheapest" in sub else "none")
        needs = "(not run)" if r["light"] and not inst["alone"]["clean"] else len(inst["needs"])
        out.append(f"| {name} | {n} | {', '.join(map(str, primes))} | {inst['loss']} | {signature(inst)} | {rule} "
                   f"| {'yes' if inst['alone']['clean'] else 'no'} | {cheap} | {needs} |")
    out += ["", "| n | gap | instances | swap alone clean | Σ territory loss | layer-4 differences "
            "| inside templates |",
            "|---|---|---|---|---|---|---|"]
    for r in boards:
        l4 = [x for x in r["only_h"] + r["only_s"] if r["layer_of"][str(x)] == LAYER]
        inside = [x for x in l4 if r["cls"][str(x)].startswith("template")]
        insts = r["instances"]
        out.append(f"| {r['n']} | {r['gap']} | {len(insts)} | {sum(i['alone']['clean'] for i in insts)} "
                   f"| {sum(i['loss'] for i in insts)} | {len(l4)} | {len(inside)} |")
    text = "\n".join(out)
    with open(f"{HERE}/out/summary.md", "w") as f:
        f.write(text + "\n")
    print(text)


def main():
    os.makedirs(f"{HERE}/out", exist_ok=True)
    args = sys.argv[1:]
    if args == ["--summary"]:
        summary()
        return
    light = "--light" in args
    for arg in [a for a in args if a != "--light"]:
        b, r = analyze(int(arg), light)
        text = render(b, r)
        print(text, flush=True)
        with open(f"{HERE}/out/board{arg}.md", "w") as f:
            f.write(text + "\n")
        slim = dict(r)
        slim["found"] = [[c, k] for c, k in r["found"]]
        for inst in slim["instances"]:
            inst["cores"] = [sorted(c) for c in inst["cores"]]
        with open(f"{HERE}/out/board{arg}.json", "w") as f:
            json.dump(slim, f)


if __name__ == "__main__":
    main()
