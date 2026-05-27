r"""e1r: Targeted reductions of de Grey 1585 based on L17 structure.

Architecture 1, Shot 2.

L17 identified three components:
  - C_6 core V_sym (778v, chi 4).
  - Asymmetric half V_asym (807v, chi 4).
  - 155 bridges between them; 124 core vertices and 22 asym vertices touched.

This experiment tests targeted reductions: which subgraphs of de Grey 1585
still have chi >= 5?

Reductions to try:
  (R1) bridge_core (124) + V_asym (807) = 931 vertices.
       Drop the 654 non-bridge-touched core vertices.
  (R2) bridge_core (124) + bridge_asym (22) + remaining_asym (785) = 931.
       (Same as R1 with different decomposition.)
  (R3) V_sym (778) + bridge_asym (22) = 800 vertices.
       Drop the 785 non-bridge-touched asym vertices.
  (R4) bridge_core (124) + bridge_asym (22) = 146 vertices (already tested in
       e1q, chi = 4, no good).
  (R5) bridge_core (124) + V_asym (807) + the 124 bridge_core's neighbors
       in V_sym = 778 (full core) — same as full graph.

For each reduction, run a single SAT call to test chi <= 4.
"""

from __future__ import annotations

import json
import pathlib
import time

import mpmath as mp
import sympy as sp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"

mp.mp.dps = 50


def parse_sage_vertex_file(path):
    text = path.read_text(encoding="utf-8")
    sympy_ctx = {"sqrt": sp.sqrt}
    parsed = sp.sympify(text, locals=sympy_ctx, rational=True)
    return [(row[0], row[1]) for row in parsed]


def parse_edge_file(path):
    edges = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("c") or line.startswith("p"):
            continue
        if line.startswith("e"):
            parts = line.split()
            edges.append((int(parts[1]) - 1, int(parts[2]) - 1))
    return edges


def vertices_to_numeric(verts_sym, dps=50):
    out = []
    with mp.workdps(dps):
        for (x, y) in verts_sym:
            xn = mp.mpf(str(sp.N(x, dps)))
            yn = mp.mpf(str(sp.N(y, dps)))
            out.append((xn, yn))
    return out


def build_vertex_lookup(verts_num, tol=mp.mpf("1e-30")):
    def quantize(x):
        return mp.nstr(x, 20)
    table = {}
    for idx, (x, y) in enumerate(verts_num):
        table.setdefault((quantize(x), quantize(y)), []).append(idx)

    def lookup(p):
        kx = quantize(p[0])
        ky = quantize(p[1])
        for idx in table.get((kx, ky), []):
            ux, uy = verts_num[idx]
            if mp.fabs(p[0] - ux) < tol and mp.fabs(p[1] - uy) < tol:
                return idx
        return -1
    return lookup


def apply_pivot_rotation(p, pivot, ct, st):
    dx = p[0] - pivot[0]
    dy = p[1] - pivot[1]
    return (ct*dx - st*dy + pivot[0], st*dx + ct*dy + pivot[1])


def sat_k_color(N, edges, k):
    if N == 0:
        return True, 0.0
    def var(v, c): return v * k + c + 1
    clauses = []
    for v in range(N):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    t0 = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
    return sat, time.time() - t0


def test_subgraph(V_subset, edges, label):
    V_set = set(V_subset)
    E = [(u, v) for (u, v) in edges if u in V_set and v in V_set]
    idx_map = {v: i for i, v in enumerate(sorted(V_subset))}
    E_re = [(idx_map[u], idx_map[v]) for (u, v) in E]
    print(f"  Reduction {label}: |V| = {len(V_subset)}, |E| = {len(E)}", flush=True)
    sat4, t4 = sat_k_color(len(V_subset), E_re, 4)
    print(f"    4-colorable: {sat4} (t = {t4:.1f}s)", flush=True)
    if sat4 is False:
        sat5, t5 = sat_k_color(len(V_subset), E_re, 5)
        print(f"    5-colorable: {sat5} (t = {t5:.1f}s)", flush=True)
        if sat5 is True:
            chi = "5"
        else:
            chi = ">=6"
        print(f"    *** {label} has chi = {chi} ***", flush=True)
        return {"label": label, "n_vertices": len(V_subset), "n_edges": len(E), "chi": chi}
    else:
        return {"label": label, "n_vertices": len(V_subset), "n_edges": len(E), "chi": "<=4"}


def main():
    print("e1r: targeted reductions of de Grey 1585")
    print("=" * 78)

    sage_path = REPO_ROOT / "sources" / "degrey_1585_vertices.sage"
    edge_path = REPO_ROOT / "sources" / "degrey_1585.dimacs"
    verts_sym = parse_sage_vertex_file(sage_path)
    edges = parse_edge_file(edge_path)
    n = len(verts_sym)
    verts_num = vertices_to_numeric(verts_sym, dps=50)
    lookup = build_vertex_lookup(verts_num)
    print(f"  {n} vertices, {len(edges)} edges")

    # Compute C_6 core.
    pivot = verts_num[0]
    ct = mp.mpf(1) / mp.mpf(2)
    st = mp.sqrt(mp.mpf(3)) / mp.mpf(2)
    in_core = [True] * n
    for i in range(n):
        p = verts_num[i]
        rk = p
        for k in range(5):
            rk = apply_pivot_rotation(rk, pivot, ct, st)
            j = lookup(rk)
            if j < 0:
                in_core[i] = False
                break
    core = set(i for i in range(n) if in_core[i])
    asym = set(i for i in range(n) if not in_core[i])
    print(f"  C_6 core: {len(core)}; asymmetric: {len(asym)}")

    # Bridges.
    bridge_core = set()
    bridge_asym = set()
    for (u, v) in edges:
        if u in core and v in asym:
            bridge_core.add(u)
            bridge_asym.add(v)
        elif v in core and u in asym:
            bridge_core.add(v)
            bridge_asym.add(u)
    print(f"  bridge-touched: {len(bridge_core)} core + {len(bridge_asym)} asym")
    print()

    # --- Run reductions ---
    print("Testing reductions:")
    print()
    results = []

    # R1: bridge_core + full asym = 124 + 807 = 931.
    R1 = bridge_core | asym
    results.append(test_subgraph(R1, edges, "R1 = bridge_core + V_asym"))

    # R3: full core + bridge_asym = 778 + 22 = 800.
    R3 = core | bridge_asym
    results.append(test_subgraph(R3, edges, "R3 = V_sym + bridge_asym"))

    # R5: drop a fraction of the non-bridge-touched core (keep half of them).
    #   bridge_core (124) + half non-bridge-touched core + V_asym
    nonbridge_core = sorted(core - bridge_core)
    # Take first half.
    half_nonbridge = set(nonbridge_core[:len(nonbridge_core) // 2])
    R5 = bridge_core | half_nonbridge | asym
    results.append(test_subgraph(R5, edges, "R5 = bridge_core + half_nonbridge_core + V_asym"))

    # R6: V_sym + half non-bridge-touched asym
    nonbridge_asym = sorted(asym - bridge_asym)
    half_nonbridge_asym = set(nonbridge_asym[:len(nonbridge_asym) // 2])
    R6 = core | bridge_asym | half_nonbridge_asym
    results.append(test_subgraph(R6, edges, "R6 = V_sym + bridge_asym + half_nonbridge_asym"))

    # R7: bridge_core + bridge_asym + half non-bridge-touched asym
    R7 = bridge_core | bridge_asym | half_nonbridge_asym
    results.append(test_subgraph(R7, edges, "R7 = bridge_core + bridge_asym + half_nonbridge_asym"))

    print()
    print("Summary:")
    for r in results:
        print(f"  {r['label']:50s} |V|={r['n_vertices']:4d}  |E|={r['n_edges']:5d}  chi={r['chi']}")

    out = {
        "experiment": "e1r_targeted_reduction",
        "results": results,
    }
    out_path = CACHE / "e1r_targeted_reduction.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
