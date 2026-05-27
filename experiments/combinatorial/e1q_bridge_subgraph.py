r"""e1q: Bridge-subgraph analysis of de Grey 1585.

Architecture 1, Shot 2. Continues e1p (L16/L17).

Structural picture so far:
- C_6 core V_sym: 778 vertices, 3806 internal edges, chi = 4 (e1n).
- Asymmetric half V \ V_sym: 807 vertices, 3948 internal edges, chi = 4 (e1p).
- Full de Grey 1585: 1585 vertices, 7909 edges, chi = 5.
- Difference: 7909 - 3806 - 3948 = 155 "bridge edges" between core and asymmetric.

These 155 bridge edges are the locus of the chi >= 5 obstruction. The two
halves can each be 4-colored independently; chi jumps to 5 only when bridges
are added.

This experiment:
(1) Identify the bridge edges and the endpoint vertices in each half.
(2) Restrict to vertices touched by bridge edges. Add within-half edges among
    these vertices. SAT-check chi of this restricted graph.
(3) The minimum bridge configuration: smallest subgraph using only bridge
    edges (+ necessary internal edges) that's still chi >= 5.

Output: a chi >= 5 UDG smaller than de Grey 1585 by removing "irrelevant"
vertices (those not touched by any bridge edge).
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
    print("e1q: bridge-subgraph analysis of de Grey 1585")
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

    core_set = set(i for i in range(n) if in_core[i])
    asym_set = set(i for i in range(n) if not in_core[i])
    print(f"  C_6 core: {len(core_set)} vertices; asymmetric half: {len(asym_set)}")

    # Classify edges.
    bridge_edges = []
    core_edges = []
    asym_edges = []
    for (u, v) in edges:
        u_in_core = u in core_set
        v_in_core = v in core_set
        if u_in_core and v_in_core:
            core_edges.append((u, v))
        elif u in asym_set and v in asym_set:
            asym_edges.append((u, v))
        else:
            bridge_edges.append((u, v))
    print(f"  edges within core: {len(core_edges)}")
    print(f"  edges within asym: {len(asym_edges)}")
    print(f"  bridge edges (core-asym): {len(bridge_edges)}")
    print()

    # --- Phase 1: vertices touched by bridge edges ---
    bridge_core = set()  # core vertices with a bridge edge
    bridge_asym = set()  # asym vertices with a bridge edge
    for (u, v) in bridge_edges:
        if u in core_set:
            bridge_core.add(u)
            bridge_asym.add(v)
        else:
            bridge_core.add(v)
            bridge_asym.add(u)
    print(f"Phase 1: bridge-touched vertices.")
    print(f"  core vertices with bridge edges: {len(bridge_core)} (of 778)")
    print(f"  asym vertices with bridge edges: {len(bridge_asym)} (of 807)")
    print()

    # --- Phase 2: restricted subgraph on bridge-touched vertices ---
    print("Phase 2: subgraph restricted to bridge-touched vertices.")
    V_R = sorted(bridge_core | bridge_asym)
    V_R_set = set(V_R)
    E_R = [(u, v) for (u, v) in edges if u in V_R_set and v in V_R_set]
    print(f"  |V_R| = {len(V_R)}, |E_R| = {len(E_R)}")
    idx_map = {v: i for i, v in enumerate(V_R)}
    E_R_reidx = [(idx_map[u], idx_map[v]) for (u, v) in E_R]
    sat4, t4 = sat_k_color(len(V_R), E_R_reidx, 4)
    print(f"    4-colorable: {sat4} (t={t4:.1f}s)")
    if sat4 is False:
        sat5, t5 = sat_k_color(len(V_R), E_R_reidx, 5)
        print(f"    5-colorable: {sat5} (t={t5:.1f}s)")
        print(f"  *** Restricted subgraph (|V|={len(V_R)}) has chi >= 5 ***")
    print()

    # --- Phase 3: vertex minimization within the bridge subgraph ---
    if sat4 is False:
        print("Phase 3: greedy vertex removal from bridge subgraph.")
        # Try removing each vertex; if chi remains >= 5, remove permanently.
        current_V = list(V_R)
        current_E = list(E_R)
        removed = []
        passes = 0
        while True:
            passes += 1
            any_removed = False
            for v in list(current_V):
                trial_V = [u for u in current_V if u != v]
                trial_set = set(trial_V)
                trial_E = [(a, b) for (a, b) in current_E if a in trial_set and b in trial_set]
                idx_map_t = {u: i for i, u in enumerate(trial_V)}
                trial_E_reidx = [(idx_map_t[a], idx_map_t[b]) for (a, b) in trial_E]
                sat4_t, _ = sat_k_color(len(trial_V), trial_E_reidx, 4)
                if sat4_t is False:
                    # Can remove v while keeping chi >= 5.
                    current_V = trial_V
                    current_E = trial_E
                    removed.append(v)
                    any_removed = True
            print(f"  pass {passes}: removed {len(removed)} cumulative, |V|={len(current_V)}, |E|={len(current_E)}", flush=True)
            if not any_removed:
                break
            if passes >= 3:   # cap passes for time budget
                break

        sat4_f, _ = sat_k_color(len(current_V), [(((dict((u, i) for i, u in enumerate(current_V)))[a]), ((dict((u, i) for i, u in enumerate(current_V)))[b])) for (a, b) in current_E], 4)
        print()
        print(f"  After greedy minimization: |V|={len(current_V)}, |E|={len(current_E)}, chi <= 4: {sat4_f}")
        if sat4_f is False:
            print(f"  *** Reduced chi >= 5 UDG: {len(current_V)} vertices ***")
    print()

    out = {
        "experiment": "e1q_bridge_subgraph",
        "n_core_edges": len(core_edges),
        "n_asym_edges": len(asym_edges),
        "n_bridge_edges": len(bridge_edges),
        "n_bridge_core_vertices": len(bridge_core),
        "n_bridge_asym_vertices": len(bridge_asym),
        "restricted_V": len(V_R),
        "restricted_E": len(E_R),
        "restricted_chi4": sat4,
        "restricted_chi5": sat5 if 'sat5' in locals() else None,
        "reduced_V": len(current_V) if 'current_V' in locals() else None,
        "reduced_E": len(current_E) if 'current_E' in locals() else None,
    }
    out_path = CACHE / "e1q_bridge_subgraph.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
