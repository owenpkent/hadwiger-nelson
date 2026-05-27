r"""e1n: Extract the C_6-symmetric core of de Grey 1585 about v_0, SAT-check chi.

Architecture 1, Shot 2. Continues e1m (L16).

e1m discovered that de Grey 1585 has approximate D_6 symmetry about
v_0 = (2, 0), with each non-identity rotation R_{60°k} preserving exactly
half (~787) of the 1585 vertices.

This experiment extracts the C_6-symmetric core:
  V_sym = {v in V : R^k(v) in V for all k = 0..5}
about pivot v_0. SAT-check chi(V_sym).

If chi(V_sym) >= 5, we have a ~787-vertex C_6-symmetric 5-chromatic UDG,
substantially smaller than the C_6-closure of Polymath 510 (1155 vertices, L15).

If chi(V_sym) = 4, the asymmetric perturbations are essential.
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


def main():
    print("e1n: extract C_6-symmetric core of de Grey 1585 about v_0")
    print("=" * 78)

    sage_path = REPO_ROOT / "sources" / "degrey_1585_vertices.sage"
    edge_path = REPO_ROOT / "sources" / "degrey_1585.dimacs"
    print(f"  loading...")
    verts_sym = parse_sage_vertex_file(sage_path)
    edges = parse_edge_file(edge_path)
    n = len(verts_sym)
    verts_num = vertices_to_numeric(verts_sym, dps=50)
    lookup = build_vertex_lookup(verts_num)
    print(f"    {n} vertices, {len(edges)} edges")

    # v_0 = (2, 0) as the rotation pivot.
    pivot = verts_num[0]
    print(f"  pivot v_0 = ({mp.nstr(pivot[0], 5)}, {mp.nstr(pivot[1], 5)})")

    # C_6 generator: cos(60°) = 1/2, sin(60°) = sqrt(3)/2.
    ct = mp.mpf(1) / mp.mpf(2)
    st = mp.sqrt(mp.mpf(3)) / mp.mpf(2)
    print(f"  R_60° about v_0")
    print()

    # --- Phase 1: identify C_6-symmetric core ---
    print("Phase 1: identify C_6-symmetric core.")
    in_core = [True] * n
    for i in range(n):
        p = verts_num[i]
        # Apply R^k for k = 1..5 and check each image is in V.
        rk = p
        for k in range(5):
            rk = apply_pivot_rotation(rk, pivot, ct, st)
            j = lookup(rk)
            if j < 0:
                in_core[i] = False
                break
    core_indices = [i for i in range(n) if in_core[i]]
    print(f"  C_6-symmetric core: {len(core_indices)} vertices "
          f"(out of {n}, {len(core_indices)/n:.1%})")
    print()

    # --- Phase 2: edges within core ---
    core_set = set(core_indices)
    core_edges = [(u, v) for (u, v) in edges if u in core_set and v in core_set]
    print(f"Phase 2: edges within C_6 core.")
    print(f"  {len(core_edges)} edges (out of {len(edges)} total)")
    print()

    # Reindex.
    idx_map = {v: i for i, v in enumerate(core_indices)}
    core_edges_reidx = [(idx_map[u], idx_map[v]) for (u, v) in core_edges]

    # --- Phase 3: chi of core ---
    print("Phase 3: chi(C_6 core) via SAT.")
    print(f"  testing 4-colorability...")
    sat4, t4 = sat_k_color(len(core_indices), core_edges_reidx, 4)
    print(f"    4-colorable: {sat4} (time {t4:.1f}s)")
    if sat4 is False:
        print(f"  *** C_6 core has chi >= 5 ***")
        sat5, t5 = sat_k_color(len(core_indices), core_edges_reidx, 5)
        print(f"    5-colorable: {sat5} (time {t5:.1f}s)")
        chi = "5" if (sat5 is True and sat4 is False) else (">=6" if sat5 is False else "?")
    else:
        print(f"    chi(C_6 core) <= 4. Symmetric subset alone is NOT 5-chromatic.")
        sat3, t3 = sat_k_color(len(core_indices), core_edges_reidx, 3)
        chi = "4" if sat3 is False else "<=3"
        print(f"    3-colorable: {sat3}")
    print()
    print(f"  CONCLUSION: chi(C_6 core of de Grey 1585) = {chi}")

    out = {
        "experiment": "e1n_degrey_c6_core",
        "n_vertices_total": n,
        "n_edges_total": len(edges),
        "n_core_vertices": len(core_indices),
        "n_core_edges": len(core_edges),
        "core_indices": core_indices,
        "chi": chi,
        "4-colorable": sat4,
        "5-colorable": sat5 if 'sat5' in locals() else None,
        "3-colorable": sat3 if 'sat3' in locals() else None,
    }
    out_path = CACHE / "e1n_degrey_c6_core.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
