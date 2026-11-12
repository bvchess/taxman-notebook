#!/usr/bin/env python3
"""E14 extended, the seal (loops study, Sections 10.4 part 3, 11.2 item 3 and 14).

Part A, the sealing lemma at the clean 16P games: on board n - 1 of 1168, 2224, 2768, 3184, 4432 (and 2512, clean to
depth 2 only), take the heaviest set independent at both parities nearest the committed set (E5's paritydump.jsonl,
variant near_game; the variant plain as a second heaviest set) and, for every number y of the board outside it and
outside the window (columns 0 to 3), its circuit at each parity: the members whose parity vectors sum to y's.  Report
the circuits through a ladder cell, (8, 1), (6, 1), (6, 2), (4, 2), (4, 3), and at 2512 those through any cell of
column 3.

Part B, the seal per hub at 5061: on boards 5060 and 5061, for the hubs 8, 12, 16, 18, 20, 27, 29, 30, 32 (the
study's seven and E10's 8 and 20), the holder of the hub in peel's payment scheme of the recorded set (the committed
set of 5060, the best-known set of 5061), the hub's cells that every heaviest set holds (paritydump-5061.jsonl,
variant forced: a cell some heaviest set holds and some avoids is free), and the circuits of the region's cells
outside the heaviest set nearest the recorded one that pass through a hub cell outside the region.  Two regions: the
study's (the columns of 151, 157, 163, 241, 251) and E10's (149, 151, 157, 163, 241, 251, 421, 631).

A hub cell of h is h·p with p a prime above h's largest prime: h is one of its maximal factors.  Parity vectors as in
docs/theory/parity-bound.md (W1).  Run as `nice -n 19 python3 -I e14/seal.py` from the loops folder."""
import json
import sys

sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops")
sys.path.insert(0, "/home/brian/taxman_work/lab/work/loops/study")
import predict, patterns  # noqa: E402

# study/hubs.py runs its own report over sys.argv when imported; it is imported for its function scheme alone.
ARGS, sys.argv = sys.argv, sys.argv[:1]
import hubs  # noqa: E402
sys.argv = ARGS

common, MF = predict.common, predict.MF
HERE = "/home/brian/taxman_work/lab/work/loops"
HUBS = [8, 12, 16, 18, 20, 27, 29, 30, 32]
REGIONS = {"study": [151, 157, 163, 241, 251], "E10": [149, 151, 157, 163, 241, 251, 421, 631]}


def lpf(x):
    return common.factor(x)[-1]


def omega(x):
    return len(common.factor(x))


def hub_of(z):
    """The hubs h of HUBS for which z is a hub cell h·p, p a prime above h's largest prime."""
    return [h for h in HUBS if z % h == 0 and predict.is_prime(z // h) and z // h > lpf(h)]


class Circuits:
    """The fundamental circuits of numbers outside an independent set `members` of board m, at one parity."""

    def __init__(self, m, members, parity):
        self.m, self.parity = m, parity
        self.members = sorted(members)
        self.basis = {}  # pivot bit -> (vector, combination of member indices as a bit mask)
        for i, s in enumerate(self.members):
            v = self.vec(s)
            if v is None:
                continue
            c = 1 << i
            while v:
                p = v.bit_length() - 1
                if p not in self.basis:
                    self.basis[p] = (v, c)
                    break
                bv, bc = self.basis[p]
                v ^= bv
                c ^= bc
            else:
                raise ValueError(f"board {m}: the set is dependent at parity {parity}")

    def vec(self, s):
        if (omega(s) - self.parity) % 2:
            return sum(1 << f for f in MF[s])
        return (1 << s) if 2 * s <= self.m else None

    def of(self, y):
        """The members whose vectors sum to y's, or None (y's vector is independent of theirs, or has an extra
        coordinate)."""
        v = self.vec(y)
        if v is None:
            return None
        c = 0
        while v:
            p = v.bit_length() - 1
            if p not in self.basis:
                return None
            bv, bc = self.basis[p]
            v ^= bv
            c ^= bc
        return [s for i, s in enumerate(self.members) if c >> i & 1]


def sets_of(path):
    out = {}
    for line in open(path):
        d = json.loads(line)
        if d.get("variant") in ("near_game", "plain"):
            out[(d["n"], d["m"], d["variant"])] = d["set"]
    return out


def part_a():
    sets = sets_of(f"{HERE}/e5/paritydump.jsonl")
    print("== Part A: circuits of the numbers outside the window and outside a heaviest set of n - 1")
    print("   (heavy: at least the lightest ladder cell 4·P3; light: the rest, the hubs and other small numbers, whose unit")
    print("   vectors the ladder cells span as they span every hub they list)")
    for n in (1168, 2224, 2768, 3184, 4432, 2512):
        m = n - 1
        P = lpf(n)
        pj = patterns.primes_around(P)
        window = {pj[j] for j in range(4)}
        ladder = {8 * pj[1]: "(8,1)", 6 * pj[1]: "(6,1)", 6 * pj[2]: "(6,2)", 4 * pj[2]: "(4,2)", 4 * pj[3]: "(4,3)"}
        lightest = min(ladder)
        print(f"-- {n} = 16·{P}, clean depth {patterns.clean_depth(n)}, columns 0..3 = {[pj[j] for j in range(4)]}; "
              f"near_game and plain sets equal: {sets[(n, m, 'near_game')] == sets[(n, m, 'plain')]}")
        for variant in ("near_game", "plain"):
            members = set(sets[(n, m, variant)])
            inside = {c: lab for c, lab in ladder.items() if c in members}
            outside = [y for y in range(2, m + 1) if y not in members and lpf(y) not in window]
            counted = {"heavy": 0, "light": 0}
            through = {"heavy": [], "light": []}
            column3 = {"heavy": {}, "light": {}}
            for parity in (0, 1):
                circ = Circuits(m, members, parity)
                for y in outside:
                    c = circ.of(y)
                    if c is None:
                        continue
                    kind = "heavy" if y >= lightest else "light"
                    counted[kind] += 1
                    hit = [ladder[s] for s in c if s in ladder]
                    if hit:
                        through[kind].append((y, parity, hit, len(c)))
                    rows3 = tuple(sorted(s // pj[3] for s in c if lpf(s) == pj[3]))
                    if rows3:
                        column3[kind].setdefault(rows3, []).append(f"{y}@{parity}({len(c)})")
            print(f"   {variant}: ladder cells in the set {sorted(inside.values())}; {len(outside)} numbers outside")
            for kind in ("heavy", "light"):
                print(f"      {kind}: {counted[kind]} circuits; through a ladder cell {len(through[kind])}; through column 3 "
                      f"{sum(len(v) for v in column3[kind].values())}")
                if kind == "heavy":
                    for y, parity, hit, size in through[kind][:12]:
                        print(f"         {y} = {cellname(y, pj)} parity {parity}: ladder {hit}, {size} members")
                for r3, ys in sorted(column3[kind].items()):
                    print(f"         column-3 rows {list(r3)}: {len(ys)} circuits, e.g. {ys[:6]}")
            if variant == "near_game" and sets[(n, m, "near_game")] == sets[(n, m, "plain")]:
                break


def part_a_freed():
    """Part A2: which numbers outside the window the cascade frees.  I1 is the heaviest set of n - 1 nearest the
    committed set, I2 the heaviest set of n nearest I1 (the parity bound's own change, E5's near_prev).  A number y
    outside the window and outside both sets is freed at a parity when it has a circuit in I1 and none in I2."""
    lines = [json.loads(t) for t in open(f"{HERE}/e5/paritydump.jsonl")]
    sets = {(d["n"], d["m"], d["variant"]): d["set"] for d in lines if "set" in d}
    print("\n== Part A2: numbers outside the window that the cascade frees (a circuit in I(n - 1), none in I(n))")
    for n in (1168, 2224, 2768, 3184, 4432, 2512):
        m = n - 1
        pj = patterns.primes_around(lpf(n))
        window = {pj[j] for j in range(4)}
        i1, i2 = set(sets[(n, m, "near_game")]), set(sets[(n, n, "near_prev")])
        moved_in = sorted(y for y in i2 - i1 if lpf(y) not in window)
        moved_out = sorted(y for y in i1 - i2 if lpf(y) not in window)
        outside = [y for y in range(2, m + 1) if y not in i1 and y not in i2 and lpf(y) not in window]
        freed = []
        for parity in (0, 1):
            c1, c2 = Circuits(m, i1, parity), Circuits(n, i2, parity)
            for y in outside:
                before = c1.of(y)
                if before is not None and c2.of(y) is None:
                    through = sorted({cellname(s, pj) for s in before if lpf(s) in window})
                    freed.append((y, parity, len(before), through))
        print(f"-- {n}: the parity change outside the window: in {moved_in}, out {moved_out}; "
              f"{len(outside)} numbers outside both sets; freed at a parity: {len(freed)}")
        for y, parity, size, through in freed[:12]:
            print(f"      {y} = {cellname(y, pj)} at parity {parity}: its circuit in I(n - 1), {size} members, met the "
                  f"window at {through}")


def sets_of_key(sets, n, m, variant):
    return sets[(n, m, variant)]


def cellname(y, pj):
    lab = patterns.label(y, pj)
    return f"({lab[0]},{lab[1]})" if lab else str(y)


def part_b():
    path = f"{HERE}/e14/paritydump-5061.jsonl"
    lines = [json.loads(t) for t in open(path)]
    near = {d["m"]: d["set"] for d in lines if d.get("variant") == "near_game"}
    forced = {}
    for d in lines:
        if d.get("variant") == "forced":
            forced[d["m"]] = {x: (hold, avoid) for x, hold, avoid in d["can_hold_can_avoid"]}
    res = common.results()
    best = predict.load_best()
    recorded = {5060: set(res[5060]["moves"]), 5061: set(best[5061]["moves"])}
    print("\n== Part B: the hubs at 5061 (boards 5060 and 5061)")
    for m in (5060, 5061):
        S = recorded[m]
        pay = hubs.scheme(S, m)
        holder = {f: x for x, f in pay.items()}
        members = set(near[m])
        fm = forced[m]
        print(f"-- board {m}: recorded set {'committed (proven)' if m == 5060 else 'best-known'}, "
              f"{len(S)} moves; heaviest set nearest it, {len(members)} members")
        circ = {parity: Circuits(m, members, parity) for parity in (0, 1)}
        crossings = {name: {} for name in REGIONS}
        for name, cols in REGIONS.items():
            for y in range(2, m + 1):
                if y in members or lpf(y) not in cols:
                    continue
                for parity in (0, 1):
                    c = circ[parity].of(y)
                    if c is None:
                        continue
                    for s in c:
                        if lpf(s) in cols:
                            continue
                        for h in hub_of(s):
                            crossings[name].setdefault(h, set()).add((y, parity, s))
        for h in HUBS:
            cells = sorted((h * p for p in range(lpf(h) + 1, m // h + 1) if predict.is_prime(p)), reverse=True)
            g = holder.get(h)
            g_text = f"{g} = {h}·{g // h}" if g and g % h == 0 else (str(g) if g else ("a move" if h in S else "none"))
            in_s = [c for c in cells if c in S]
            heavier = [c for c in in_s if g is not None and c > g]
            always = [c for c in cells if c in fm and not fm[c][1]]
            never_count = sum(1 for c in cells if c in fm and not fm[c][0])
            free = [c for c in cells if c in fm and fm[c][0] and fm[c][1]]
            in_set = [c for c in cells if c in members]
            print(f"   hub {h}: game holder {g_text}; hub cells in the recorded set {len(in_s)}, heavier than the "
                  f"holder {heavier[:6]}")
            print(f"      parity: cells in every heaviest set {always[:8]}{' ...' if len(always) > 8 else ''} "
                  f"({len(always)}), free {free[:8]} ({len(free)}), in none {never_count}; in the nearest set "
                  f"{in_set[:6]} ({len(in_set)})")
            for name in REGIONS:
                cross = crossings[name].get(h, set())
                far = sorted({s for _, _, s in cross}, reverse=True)
                ys = sorted({y for y, _, _ in cross})
                print(f"      {name} region: circuits of {len(ys)} region cells pass through far cells of hub {h}"
                      f"{': ' + str(far[:6]) + ', e.g. from ' + str(ys[:6]) if cross else ''}")


def part_b_freed():
    """Part B2: at 5060 -> 5061, the parity change outside each region and the numbers outside it that the change
    frees (a circuit in I(5060), the heaviest set nearest the committed set, and none in I(5061), the heaviest set of
    5061 nearest it); and the hub cells where the recorded sets and those heaviest sets differ."""
    lines = [json.loads(t) for t in open(f"{HERE}/e14/paritydump-5061.jsonl")]
    sets = {(d["m"], d["variant"]): d["set"] for d in lines if "set" in d}
    i1, i2 = set(sets[(5060, "near_game")]), set(sets[(5061, "near_prev")])
    res = common.results()
    best = predict.load_best()
    recorded = {5060: set(res[5060]["moves"]), 5061: set(best[5061]["moves"])}
    print("\n== Part B2: 5060 -> 5061, the parity change and what it frees outside each region")
    for name, cols in REGIONS.items():
        moved_in = sorted(y for y in i2 - i1 if lpf(y) not in cols)
        moved_out = sorted(y for y in i1 - i2 if lpf(y) not in cols)
        outside = [y for y in range(2, 5061) if y not in i1 and y not in i2 and lpf(y) not in cols]
        freed = []
        for parity in (0, 1):
            c1, c2 = Circuits(5060, i1, parity), Circuits(5061, i2, parity)
            for y in outside:
                before = c1.of(y)
                if before is not None and c2.of(y) is None:
                    freed.append((y, parity, len(before), sorted(s for s in before if lpf(s) in cols)))
        print(f"-- {name} region {cols}: the parity change outside it: in {moved_in}, out {moved_out}; "
              f"{len(outside)} numbers outside both sets and the region; freed at a parity: {len(freed)}")
        for y, parity, size, inside in freed[:10]:
            print(f"      {y} = {common.factor(y)} at parity {parity}: circuit of {size} in I(5060), region cells in it "
                  f"{inside[:8]}")
    print("   hub cells where the recorded set and the nearest heaviest set differ (recorded only | parity only):")
    for m, nearest in ((5060, i1), (5061, i2)):
        S = recorded[m]
        for h in HUBS:
            cells = {h * p for p in range(lpf(h) + 1, m // h + 1) if predict.is_prime(p)}
            rec_only = sorted(c for c in cells if c in S and c not in nearest)
            par_only = sorted(c for c in cells if c in nearest and c not in S)
            if rec_only or par_only:
                print(f"      board {m}, hub {h}: {rec_only} | {par_only}")


if __name__ == "__main__":
    part_a()
    part_a_freed()
    if "--a-only" not in ARGS:
        part_b()
        part_b_freed()
