r"""e1p: Check chi of the asymmetric half of de Grey 1585.

Architecture 1, Shot 2. Continues e1n (L16).

e1n showed: C_6-symmetric core V_sym about v_0 = (2, 0) has 778 vertices,
chi = 4.

The complement V \ V_sym (asymmetric vertices, 807 of them) is the
"perturbation half" — vertices not preserved by all 6 rotations.

Question: is chi(V \ V_sym) >= 5 on its own? If yes, then the chi >= 5
property of de Grey 1585 is entirely in the asymmetric half (the symmetric
core is "extra"). If no, then chi >= 5 emerges from the INTERACTION between
the two halves.

This test takes one SAT call.
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
    print("e1p: chi of asymmetric half of de Grey 1585")
    print("=" * 78)

    sage_path = REPO_ROOT / "sources" / "degrey_1585_vertices.sage"
    edge_path = REPO_ROOT / "sources" / "degrey_1585.dimacs"
    verts_sym = parse_sage_vertex_file(sage_path)
    edges = parse_edge_file(edge_path)
    n = len(verts_sym)
    verts_num = vertices_to_numeric(verts_sym, dps=50)
    lookup = build_vertex_lookup(verts_num)
    print(f"  {n} vertices, {len(edges)} edges")

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

    asym = [i for i in range(n) if not in_core[i]]
    core = [i for i in range(n) if in_core[i]]
    print(f"  C_6 core: {len(core)} vertices; asymmetric half: {len(asym)} vertices")

    asym_set = set(asym)
    asym_edges = [(u, v) for (u, v) in edges if u in asym_set and v in asym_set]
    idx_map = {v: i for i, v in enumerate(asym)}
    asym_edges_reidx = [(idx_map[u], idx_map[v]) for (u, v) in asym_edges]
    print(f"  asymmetric half: |V|={len(asym)}, |E|={len(asym_edges)}, density={len(asym_edges)/len(asym):.2f}")
    print()

    print(f"  Testing chi(asymmetric half):")
    sat3, t3 = sat_k_color(len(asym), asym_edges_reidx, 3)
    print(f"    3-colorable: {sat3} (t={t3:.1f}s)")
    sat4, t4 = sat_k_color(len(asym), asym_edges_reidx, 4)
    print(f"    4-colorable: {sat4} (t={t4:.1f}s)")
    sat5 = None
    t5 = 0.0
    if sat4 is False:
        sat5, t5 = sat_k_color(len(asym), asym_edges_reidx, 5)
        print(f"    5-colorable: {sat5} (t={t5:.1f}s)")

    if sat4 is False:
        chi = "5" if sat5 is True else ">=6"
        print(f"\n  CHI(asymmetric half) = {chi}")
        print(f"  IMPORTANT: the asymmetric half alone is at least 5-chromatic.")
        print(f"  This is a {len(asym)}-vertex 5-chromatic UDG.")
        if len(asym) < 1585:
            print(f"  Smaller than de Grey 1585 (saves {1585 - len(asym)} vertices).")
    elif sat3 is False:
        chi = "4"
        print(f"\n  CHI(asymmetric half) = 4. chi >= 5 emerges from core+asym interaction.")
    else:
        chi = "<=3"
        print(f"\n  CHI(asymmetric half) <= 3.")

    out = {
        "experiment": "e1p_degrey_asymmetric_half",
        "n_asymmetric": len(asym),
        "n_edges_asymmetric": len(asym_edges),
        "chi": chi,
        "3-colorable": sat3,
        "4-colorable": sat4,
        "5-colorable": sat5,
    }
    out_path = CACHE / "e1p_degrey_asymmetric_half.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
