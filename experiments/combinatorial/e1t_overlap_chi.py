r"""e1t: Chi of the Polymath/de-Grey vertex overlap.

Architecture 1, Shot 2. Continues L19.

L19 showed that 315/510 = 62% of Polymath 510 vertices match de Grey 1585
vertices under translation T = (2, 0). The remaining 195 are "field-reduction
artifacts" added by Heule/Parts when reformulating in Q(sqrt 3, sqrt 11)
instead of de Grey's Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11).

Question: is the chi >= 5 property carried by the overlap, the artifacts,
or both?

This experiment:
(1) Identify the 315-vertex overlap set in Polymath 510.
(2) Test chi(overlap_subgraph_in_Polymath).
(3) Test chi(overlap_subgraph_in_de_Grey) -- the same vertices, but with
    de Grey's unit-edge set (might differ).
(4) Test chi(Polymath 510 minus overlap = the 195 artifacts).

If any subgraph has chi >= 5, we've identified a smaller 5-chromatic UDG
than Parts 509.
"""

from __future__ import annotations

import json
import pathlib
import re
import time

import mpmath as mp
import sympy as sp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"

mp.mp.dps = 80


def mathematica_to_sympy(text):
    text = re.sub(r"Sqrt\[([^\]]+)\]", r"sqrt(\1)", text)
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        text = "(" + text[1:-1] + ")"
    return text


def parse_polymath_vtx(path):
    verts = []
    sympy_ctx = {"sqrt": sp.sqrt}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        t = sp.sympify(mathematica_to_sympy(line), locals=sympy_ctx, rational=True)
        verts.append((t[0], t[1]))
    return verts


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


def vertices_to_numeric(verts_sym, dps=80):
    out = []
    with mp.workdps(dps):
        for (x, y) in verts_sym:
            xn = mp.mpf(str(sp.N(x, dps)))
            yn = mp.mpf(str(sp.N(y, dps)))
            out.append((xn, yn))
    return out


def build_lookup(verts_num, tol=mp.mpf("1e-30")):
    def quantize(x):
        return mp.nstr(x, 30)
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
    print("e1t: chi of the Polymath/de-Grey vertex overlap")
    print("=" * 78)

    poly_path = REPO_ROOT / "sources" / "cnp-sat" / "vtx" / "510.vtx"
    poly_edge_path = REPO_ROOT / "sources" / "cnp-sat" / "edge" / "510.edge"
    dg_path = REPO_ROOT / "sources" / "degrey_1585_vertices.sage"
    dg_edge_path = REPO_ROOT / "sources" / "degrey_1585.dimacs"

    print("  parsing...")
    poly_sym = parse_polymath_vtx(poly_path)
    poly_num = vertices_to_numeric(poly_sym, dps=80)
    poly_edges = parse_edge_file(poly_edge_path)
    print(f"    Polymath 510: {len(poly_sym)} V, {len(poly_edges)} E")

    dg_sym = parse_sage_vertex_file(dg_path)
    dg_num = vertices_to_numeric(dg_sym, dps=80)
    dg_edges = parse_edge_file(dg_edge_path)
    print(f"    de Grey 1585: {len(dg_sym)} V, {len(dg_edges)} E")

    dg_lookup = build_lookup(dg_num)
    tx = mp.mpf(2)
    ty = mp.mpf(0)
    print()

    # Find Polymath vertices that match de Grey under T = (2, 0).
    print("Phase 1: find the 315 Polymath/de Grey overlap.")
    overlap_poly = []   # indices in Polymath
    overlap_dg = []     # corresponding indices in de Grey
    for i, p in enumerate(poly_num):
        p_t = (p[0] + tx, p[1] + ty)
        j = dg_lookup(p_t)
        if j >= 0:
            overlap_poly.append(i)
            overlap_dg.append(j)
    print(f"    overlap: {len(overlap_poly)} vertex pairs")
    print()

    # --- Phase 2: chi(overlap in Polymath 510) ---
    print("Phase 2: chi(overlap subgraph of Polymath 510).")
    overlap_poly_set = set(overlap_poly)
    overlap_poly_edges = [(u, v) for (u, v) in poly_edges
                          if u in overlap_poly_set and v in overlap_poly_set]
    idx_map = {v: i for i, v in enumerate(overlap_poly)}
    re_edges = [(idx_map[u], idx_map[v]) for (u, v) in overlap_poly_edges]
    print(f"    |V| = {len(overlap_poly)}, |E| = {len(overlap_poly_edges)}, density = {len(overlap_poly_edges)/max(len(overlap_poly),1):.2f}")
    sat4_p, t4_p = sat_k_color(len(overlap_poly), re_edges, 4)
    print(f"    4-colorable: {sat4_p} (t = {t4_p:.1f}s)")
    if sat4_p is False:
        sat5_p, t5_p = sat_k_color(len(overlap_poly), re_edges, 5)
        print(f"    5-colorable: {sat5_p} (t = {t5_p:.1f}s)")
        chi_poly_overlap = "5" if sat5_p is True else ">=6"
    else:
        chi_poly_overlap = "4"
    print(f"    chi = {chi_poly_overlap}")
    print()

    # --- Phase 3: chi(overlap in de Grey 1585) ---
    # Same vertices, but in de Grey's vertex set, with de Grey's edges.
    print("Phase 3: chi(overlap subgraph in de Grey 1585's edges).")
    overlap_dg_set = set(overlap_dg)
    overlap_dg_edges = [(u, v) for (u, v) in dg_edges
                        if u in overlap_dg_set and v in overlap_dg_set]
    dg_idx_map = {v: i for i, v in enumerate(overlap_dg)}
    re_edges_dg = [(dg_idx_map[u], dg_idx_map[v]) for (u, v) in overlap_dg_edges]
    print(f"    |V| = {len(overlap_dg)}, |E| = {len(overlap_dg_edges)}, density = {len(overlap_dg_edges)/max(len(overlap_dg),1):.2f}")
    sat4_d, t4_d = sat_k_color(len(overlap_dg), re_edges_dg, 4)
    print(f"    4-colorable: {sat4_d} (t = {t4_d:.1f}s)")
    if sat4_d is False:
        sat5_d, t5_d = sat_k_color(len(overlap_dg), re_edges_dg, 5)
        print(f"    5-colorable: {sat5_d} (t = {t5_d:.1f}s)")
        chi_dg_overlap = "5" if sat5_d is True else ">=6"
    else:
        chi_dg_overlap = "4"
    print(f"    chi = {chi_dg_overlap}")
    print()

    # --- Phase 4: chi(Polymath 510 minus overlap = 195 artifacts) ---
    print("Phase 4: chi(Polymath 510 minus overlap = the 195 artifacts).")
    artifact_indices = [i for i in range(len(poly_num)) if i not in overlap_poly_set]
    artifact_set = set(artifact_indices)
    artifact_edges = [(u, v) for (u, v) in poly_edges
                      if u in artifact_set and v in artifact_set]
    a_idx_map = {v: i for i, v in enumerate(artifact_indices)}
    re_edges_a = [(a_idx_map[u], a_idx_map[v]) for (u, v) in artifact_edges]
    print(f"    |V| = {len(artifact_indices)}, |E| = {len(artifact_edges)}, density = {len(artifact_edges)/max(len(artifact_indices),1):.2f}")
    sat4_a, t4_a = sat_k_color(len(artifact_indices), re_edges_a, 4)
    print(f"    4-colorable: {sat4_a} (t = {t4_a:.1f}s)")
    if sat4_a is False:
        sat5_a, t5_a = sat_k_color(len(artifact_indices), re_edges_a, 5)
        print(f"    5-colorable: {sat5_a} (t = {t5_a:.1f}s)")
        chi_artifact = "5" if sat5_a is True else ">=6"
    else:
        chi_artifact = "4"
    print(f"    chi = {chi_artifact}")
    print()

    # --- Summary ---
    print("Summary:")
    print(f"  Polymath/de-Grey overlap in Polymath edges: |V|=315, |E|={len(overlap_poly_edges)}, chi={chi_poly_overlap}")
    print(f"  Polymath/de-Grey overlap in de-Grey edges:  |V|=315, |E|={len(overlap_dg_edges)}, chi={chi_dg_overlap}")
    print(f"  Polymath 195 artifacts (without overlap):   |V|=195, |E|={len(artifact_edges)}, chi={chi_artifact}")

    if chi_poly_overlap == "5" or chi_poly_overlap == ">=6":
        print()
        print(f"  *** 315-vertex chi >= 5 UDG found via Polymath/de-Grey overlap! ***")
        print(f"  *** This is smaller than Parts 509 ***")

    out = {
        "experiment": "e1t_overlap_chi",
        "n_overlap": len(overlap_poly),
        "overlap_poly_indices": overlap_poly,
        "overlap_dg_indices": overlap_dg,
        "chi_overlap_in_polymath_edges": chi_poly_overlap,
        "chi_overlap_in_degrey_edges": chi_dg_overlap,
        "chi_artifacts": chi_artifact,
        "n_overlap_edges_poly": len(overlap_poly_edges),
        "n_overlap_edges_dg": len(overlap_dg_edges),
        "n_artifact_edges": len(artifact_edges),
    }
    out_path = CACHE / "e1t_overlap_chi.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
