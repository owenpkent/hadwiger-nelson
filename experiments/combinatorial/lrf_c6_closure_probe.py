r"""Long-range-forcing probe on the C_6 closure of Polymath-510 (V=1155).

The lens observation (F1 / L42 / L45): no SAT-MINIMIZED lineage graph has a
non-adjacent forced-different pair (forced-different <=> adjacent). The e1k C_6
closure (V=1155, E=10397, chi=5: 4-col UNSAT, 5-col SAT) was built but NEVER tested
for long-range forcing. SAT-minimization destroys exact rotational symmetry (W5);
the closure RESTORES it. A C_6-symmetric chi-5 graph constrains its color classes
under R_60, which is a different regime from the asymmetric minimized graphs.

This probe reconstructs the closure (numeric, dps=50, matching e1k) and runs the
merge-SAT forced-different test on STRUCTURED candidate pairs first:
  (a) antipodal pairs {v, R_180(v)} for high-degree v (the C_6 symmetry's order-2
      element; a 5-coloring's class structure interacts with the central symmetry),
  (b) same-orbit pairs {v, R_60^k(v)} (color-class-correlated by symmetry),
  (c) a high-degree-core exhaustive sweep (forcing concentrates among hubs, L42),
  (d) random non-adjacent pairs across the whole closure.

A single non-adjacent forced-different pair here = the missing chi-6 ingredient
present in a SYMMETRIC, NON-minimal, exactly-realizable UDG. That would refute the
implicit "symmetric closures also lack it" extrapolation and hand the chi-6 program
a concrete forcing gadget to amplify. A clean negative is also valuable: it would
say the closure's symmetry does NOT manufacture long-range forcing, narrowing the
search.
"""
from __future__ import annotations
import sys, pathlib, json, itertools, random, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mpmath as mp
import sympy as sp
from f1pt_lib import parse_vtx, parse_edges, sat_kcolor, CACHE, VTX, EDGE
from pysat.solvers import Cadical195

random.seed(11)
mp.mp.dps = 50
BUDGET = 600_000


def num(verts_sym, dps=50):
    out = []
    for (x, y) in verts_sym:
        out.append((mp.mpf(str(sp.N(x, dps))), mp.mpf(str(sp.N(y, dps)))))
    return out


def rot(p, ct, st):
    return (ct * p[0] - st * p[1], st * p[0] + ct * p[1])


def build_lookup(verts):
    def q(x):
        return mp.nstr(x, 20)
    table = {}
    for i, (x, y) in enumerate(verts):
        table.setdefault((q(x), q(y)), []).append(i)

    def look(p, tol=mp.mpf("1e-28")):
        for i in table.get((q(p[0]), q(p[1])), []):
            ux, uy = verts[i]
            if mp.fabs(p[0] - ux) < tol and mp.fabs(p[1] - uy) < tol:
                return i
        return -1
    return look


def c6_closure(verts):
    ct = mp.mpf(1) / 2
    st = mp.sqrt(mp.mpf(3)) / 2
    closure = list(verts)
    look = build_lookup(closure)
    pending = list(range(len(closure)))
    while pending:
        nxt = []
        for idx in pending:
            p = closure[idx]
            for _ in range(5):
                p = rot(p, ct, st)
                if look(p) < 0:
                    closure.append(p)
                    nxt.append(len(closure) - 1)
        look = build_lookup(closure)
        pending = nxt
    return closure, ct, st


def unit_edges(verts, tol=mp.mpf("1e-22")):
    out = []
    one = mp.mpf(1)
    n = len(verts)
    for i in range(n):
        xi, yi = verts[i]
        for j in range(i + 1, n):
            dx = xi - verts[j][0]
            dy = yi - verts[j][1]
            if mp.fabs(dx * dx + dy * dy - one) < tol:
                out.append((i, j))
    return out


def merged_unsat(n, eset, a, b, adj, k=5):
    if b in adj[a]:
        return True, False  # adjacent: trivially forced
    def rep(x):
        return a if x == b else x
    merged = set()
    for (u, v) in eset:
        uu, vv = rep(u), rep(v)
        if uu == vv:
            return True, False
        merged.add((min(uu, vv), max(uu, vv)))
    res, _ = sat_kcolor(n, list(merged), k, Cadical195, budget_conflicts=BUDGET)
    if res is None:
        return None, True
    return (res is False), False


def main():
    t_start = time.time()
    print("LRF probe on C_6 closure of Polymath-510")
    print("=" * 70)
    base = parse_vtx(VTX / "510.vtx")
    print(f"  loaded {len(base)} base vertices")
    vb = num(base)
    closure, ct, st = c6_closure(vb)
    n = len(closure)
    print(f"  closure: {n} vertices (expect 1155)")
    eset = set(unit_edges(closure))
    print(f"  edges: {len(eset)} (expect 10397)")

    adj = [set() for _ in range(n)]
    for (u, v) in eset:
        adj[u].add(v); adj[v].add(u)
    deg = [len(adj[v]) for v in range(n)]

    # confirm chi = 5
    s4, _ = sat_kcolor(n, list(eset), 4, Cadical195, budget_conflicts=3_000_000)
    s5, _ = sat_kcolor(n, list(eset), 5, Cadical195, budget_conflicts=3_000_000)
    print(f"  4-col SAT={s4} (expect False), 5-col SAT={s5} (expect True)")

    look = build_lookup(closure)
    # R_180 = R_60^3
    def r180(p):
        for _ in range(3):
            p = rot(p, ct, st)
        return p

    tested = 0; indet = 0
    forced_nonadj = []
    nonadj_not_forced = 0
    log = []

    def consider(a, b, kind):
        nonlocal tested, indet, nonadj_not_forced
        a, b = (a, b) if a < b else (b, a)
        if a == b:
            return
        adjacent = b in adj[a]
        v, ind = merged_unsat(n, eset, a, b, adj)
        tested += 1
        if ind:
            indet += 1
            return
        if v and not adjacent:
            forced_nonadj.append((a, b, kind))
        elif (not v) and (not adjacent):
            nonadj_not_forced += 1

    core = sorted(range(n), key=lambda v: -deg[v])[:50]

    # (a) antipodal pairs for top-degree vertices
    print("\n  (a) antipodal {v, R_180(v)} for top-40 degree vertices")
    for v in core[:40]:
        j = look(r180(closure[v]))
        if j >= 0 and j != v:
            consider(v, j, "antipodal")
        if forced_nonadj:
            break

    # (b) same-orbit pairs {v, R_60^k(v)} for top vertices, k=1,2 (k=3 is antipodal)
    if not forced_nonadj:
        print("  (b) same-orbit {v, R_60^k(v)}, k in {1,2}, top-40")
        for v in core[:40]:
            p = closure[v]
            for kk in (1, 2):
                p = rot(p, ct, st)
                j = look(p)
                if j >= 0 and j != v:
                    consider(v, j, f"orbit_R60^{kk}")
            if forced_nonadj:
                break

    # (c) exhaustive over high-degree core
    if not forced_nonadj:
        print("  (c) exhaustive non-adjacent pairs in top-50 core")
        for a, b in itertools.combinations(core, 2):
            if b not in adj[a]:
                consider(a, b, "core")
            if forced_nonadj:
                break

    # (d) random non-adjacent pairs across whole closure
    if not forced_nonadj:
        print("  (d) 500 random non-adjacent pairs across the closure")
        seen = set(); att = 0
        while len(seen) < 500 and att < 12000:
            att += 1
            a, b = random.randrange(n), random.randrange(n)
            if a == b:
                continue
            a, b = (a, b) if a < b else (b, a)
            if (a, b) in seen or b in adj[a]:
                continue
            seen.add((a, b))
            consider(a, b, "random")
            if forced_nonadj:
                break

    out = {
        "experiment": "lrf_c6_closure_probe",
        "n": n, "edges": len(eset),
        "chi5_confirmed": (s4 is False and s5 is True),
        "pairs_tested": tested, "indeterminate": indet,
        "nonadjacent_not_forced": nonadj_not_forced,
        "LONG_RANGE_FORCING_pairs": forced_nonadj,
        "long_range_forcing_found": bool(forced_nonadj),
        "seconds": round(time.time() - t_start, 1),
    }
    CACHE.mkdir(exist_ok=True)
    with (CACHE / "lrf_c6_closure_probe.json").open("w") as f:
        json.dump(out, f, indent=2)
    print("\n" + "=" * 70)
    print(f"  tested={tested} indet={indet} nonadj_not_forced={nonadj_not_forced}")
    if forced_nonadj:
        print(f"  *** LONG-RANGE FORCING FOUND: {forced_nonadj[:5]} ***")
    else:
        print("  NO long-range forcing in the structured + sampled pairs tested.")
    print(f"  ({out['seconds']}s) archived lrf_c6_closure_probe.json")
    return out


if __name__ == "__main__":
    main()
