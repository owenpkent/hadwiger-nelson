r"""E3: Z6 necklace closure of P510 (L58 born-realized chi>=6 probe).

The phase-gadget dichotomy (L58), rational-angle branch: a closed rotation
necklace of a chi-5 UDG is a finite UDG BY CONSTRUCTION (no W3 step). Build the
exact union of rho^j(P510), j=0..5, rho = rotation by 60 deg about the origin
(cos=1/2, sin=sqrt3/2, both in P510's field Q(sqrt3,sqrt11), so the union is
exactly unit-distance), with ALL cross-band unit edges, dedup coincident
vertices exactly, then ONE 5-SAT call.

Expected: SAT (5-colorable). SAT stages the resonance census (which angles /
centers stack the most cross pairs, per L58). A (dual-solver-confirmed) UNSAT
is a finite chi>=6 UDG outright. Reuses h7b's exact cross_unit machinery, which
already verified the 2- and 3-copy 60-degree unions are cross-rich and 5-SAT.
"""
from __future__ import annotations
import sys, pathlib, json, time
import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from h7b_orbit_coupling import parse_vtx, parse_edges, rot, cross_unit, _numlist
from f1pt_lib import sat_kcolor, has_k4, VTX, EDGE, CACHE
from pysat.solvers import Cadical195, Glucose42

OUT = CACHE / "e10_necklace"
OUT.mkdir(parents=True, exist_ok=True)
N_COPIES = 6
COS, SIN = sp.Rational(1, 2), sp.sqrt(3) / 2   # 60-degree rotation, in-field


def canon(p):
    """Exact canonical key for a coordinate (dedup coincident orbit vertices)."""
    return (sp.nsimplify(sp.simplify(p[0])), sp.nsimplify(sp.simplify(p[1])))


def main():
    t0 = time.time()
    base = parse_vtx(VTX / "510.vtx")
    base_edges = parse_edges(EDGE / "510.edge")
    print(f"P510: {len(base)} vtx, {len(base_edges)} edges", flush=True)

    # Build the 6 rotated copies (exact).
    copies = []
    c, s = sp.Integer(1), sp.Integer(0)
    for j in range(N_COPIES):
        copies.append([rot(p, c, s) for p in base])
        c, s = sp.simplify(COS * c - SIN * s), sp.simplify(SIN * c + COS * s)

    # Global exact dedup: map (copy, local idx) -> global id.
    gid = {}
    coords = []
    loc2g = [[None] * len(base) for _ in range(N_COPIES)]
    for j in range(N_COPIES):
        for i, p in enumerate(copies[j]):
            key = canon(p)
            if key not in gid:
                gid[key] = len(coords)
                coords.append(p)
            loc2g[j][i] = gid[key]
    n = len(coords)
    print(f"union: {n} distinct vertices ({N_COPIES * len(base) - n} coincidences) "
          f"({time.time() - t0:.0f}s)", flush=True)

    # Edges: within-copy (P510's own edges, mapped per copy) + cross-copy unit pairs.
    edge_set = set()
    for j in range(N_COPIES):
        for (u, v) in base_edges:
            a, b = loc2g[j][u], loc2g[j][v]
            if a != b:
                edge_set.add((min(a, b), max(a, b)))
    nums = [_numlist(copies[j]) for j in range(N_COPIES)]
    for j1 in range(N_COPIES):
        for j2 in range(j1 + 1, N_COPIES):
            cu = cross_unit(copies[j1], copies[j2], same=False,
                            n1=nums[j1], n2=nums[j2])
            for (i1, i2) in cu:
                a, b = loc2g[j1][i1], loc2g[j2][i2]
                if a != b:
                    edge_set.add((min(a, b), max(a, b)))
            print(f"  cross ({j1},{j2}): {len(cu)} unit pairs", flush=True)
    edges = sorted(edge_set)
    print(f"union: {len(edges)} edges, K4-free={not has_k4(n, edges)} "
          f"({time.time() - t0:.0f}s)", flush=True)

    # One 5-SAT call (uncapped); dual-solver confirm on UNSAT.
    res, dt = sat_kcolor(n, edges, 5, Cadical195)
    verdict = "5-colorable (SAT)" if res else "5-UNSAT => chi>=6"
    print(f"cadical 5-SAT: {res} ({dt:.1f}s) -> {verdict}", flush=True)
    confirm = None
    if res is False:
        print("!!! UNSAT: dual-solver confirming with Glucose42 ...", flush=True)
        confirm, dt2 = sat_kcolor(n, edges, 5, Glucose42)
        print(f"glucose confirm: {confirm} ({dt2:.1f}s)", flush=True)

    result = {"experiment": "e10_necklace_z6", "copies": N_COPIES, "angle": "60deg",
              "n": n, "edges": len(edges), "k4_free": not has_k4(n, edges),
              "five_colorable": bool(res), "glucose_confirm": confirm,
              "secs": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    print("DONE", json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
