r"""e1o: Identify the asymmetric obstruction in de Grey 1585.

Architecture 1, Shot 2. Continues e1n (L16).

e1n established that the C_6-symmetric core V_sym of de Grey 1585 (778
vertices about v_0 = (2, 0)) has chi = 4. The chi >= 5 property must
come from the ~807 asymmetric "perturbation" vertices V \ V_sym.

This experiment asks: what is the minimum subset S of asymmetric vertices
such that chi(V_sym union S) >= 5? Such an S is the "asymmetric obstruction
core" of de Grey 1585 — the structurally critical residue that the
C_6 symmetric core lacks.

Method.
(1) Singleton test: for each asymmetric vertex v, test chi(V_sym union {v}) >= 5.
(2) If no singleton works, do greedy: at each step, add the asymmetric vertex
    whose addition reduces the most "slack" toward chi 5. Repeat until 5-chromatic.

For singleton: ~807 SAT calls on ~780-vertex graphs. ~5-10 minutes total.
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
    print("e1o: identify asymmetric obstruction core in de Grey 1585")
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

    # Recover the C_6 core (same as e1n).
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
    core = [i for i in range(n) if in_core[i]]
    asym = [i for i in range(n) if not in_core[i]]
    print(f"  C_6 core: {len(core)} vertices; asymmetric: {len(asym)}")
    print()

    # Pre-compute edges by endpoint for fast subset edges.
    incident = [[] for _ in range(n)]
    edges_set = set()
    for (u, v) in edges:
        a, b = (u, v) if u < v else (v, u)
        edges_set.add((a, b))
        incident[u].append(v)
        incident[v].append(u)

    def induced_edges(V_subset):
        S = set(V_subset)
        E = []
        for v in V_subset:
            for u in incident[v]:
                if u in S and u > v:
                    E.append((v, u))
                elif u in S and u < v:
                    pass   # handled by the u-side
        return E

    # Sanity: chi(core) should be 4.
    core_edges = induced_edges(core)
    print(f"  sanity: |E(core)| = {len(core_edges)} (expected 3806)")
    sat4_core, t4_core = sat_k_color(len(core), [(core.index(u), core.index(v)) for (u, v) in core_edges], 4)
    print(f"  sanity: chi(core) 4-col = {sat4_core} (expected True)")
    print()

    # --- Phase 1: singleton augmentation test ---
    print(f"Phase 1: singleton augmentation. Test chi(core u {{v}}) for each asymmetric v.")
    print()
    core_idx_map = {v: i for i, v in enumerate(core)}

    base_N = len(core)
    successful_singletons = []
    t_phase1_start = time.time()
    for ki, vidx in enumerate(asym):
        V_aug = core + [vidx]
        idx_map = dict(core_idx_map)
        idx_map[vidx] = base_N
        # Build edges for augmented.
        E_aug = list(core_edges)
        for u in incident[vidx]:
            if u in core_idx_map:
                E_aug.append((u, vidx) if u < vidx else (vidx, u))
        E_aug_reidx = [(idx_map[u], idx_map[v]) for (u, v) in E_aug]
        sat4, t4 = sat_k_color(len(V_aug), E_aug_reidx, 4)
        if sat4 is False:
            successful_singletons.append({"vertex": vidx, "n_new_edges": len(E_aug) - len(core_edges)})
            print(f"  [SINGLETON {len(successful_singletons)}] v_{vidx} forces chi>=5! "
                  f"(new edges: {len(E_aug) - len(core_edges)}, t={t4:.2f}s)")
        if (ki + 1) % 100 == 0:
            print(f"    progress: {ki+1}/{len(asym)}, found {len(successful_singletons)} so far, "
                  f"elapsed {time.time() - t_phase1_start:.1f}s", flush=True)

    print()
    print(f"  Phase 1 complete in {time.time() - t_phase1_start:.1f}s")
    print(f"  Singletons forcing chi>=5: {len(successful_singletons)} out of {len(asym)} asymmetric vertices")
    if successful_singletons:
        print(f"  Smallest augmented size: |V| = {len(core) + 1} = {len(core)} (core) + 1 asymmetric")

    # --- Phase 2: greedy multi-step augmentation ---
    # Strategy: at each step, add the asymmetric vertex with maximum degree to
    # the CURRENT graph (most-constrained candidate). SAT-check chi. Repeat
    # until chi >= 5 or no asymmetric vertex remains.
    print()
    print("Phase 2: greedy multi-step augmentation by degree to current G.")
    print()

    G = list(core)
    G_set = set(G)
    G_edges = list(core_edges)
    G_idx_map = dict(core_idx_map)
    remaining = list(asym)
    added_seq = []
    max_steps = 50

    print(f"  {'step':>4} {'|V|':>5} {'|E|':>5} {'added':>6} {'deg':>4} {'4-col':>6} {'5-col':>6} {'time':>7}")

    for step in range(1, max_steps + 1):
        # Compute degree-to-G for each remaining asymmetric vertex.
        best = None
        best_deg = -1
        for v in remaining:
            deg = sum(1 for u in incident[v] if u in G_set)
            if deg > best_deg:
                best_deg = deg
                best = v
        if best is None or best_deg == 0:
            print(f"  step {step}: no remaining asymmetric vertex has edges to G; stopping.")
            break

        # Add best.
        added_seq.append(best)
        new_idx = len(G)
        G.append(best)
        G_set.add(best)
        G_idx_map[best] = new_idx
        remaining.remove(best)
        for u in incident[best]:
            if u in G_set and u != best:
                G_edges.append((u, best) if u < best else (best, u))

        # SAT-check chi.
        E_reidx = [(G_idx_map[u], G_idx_map[v]) for (u, v) in G_edges]
        sat4, t4 = sat_k_color(len(G), E_reidx, 4)
        sat5 = None
        t5 = 0.0
        if sat4 is False:
            sat5, t5 = sat_k_color(len(G), E_reidx, 5)
        mark = "!!!" if sat4 is False else ""
        print(f"  {step:4d} {len(G):5d} {len(G_edges):5d} v_{best:5d} {best_deg:4d} "
              f"{'F' if sat4 is False else 'T':>6} "
              f"{('F' if sat5 is False else 'T' if sat5 is True else '-'):>6} "
              f"{(t4 + t5):7.2f}s {mark}", flush=True)

        if sat4 is False:
            print()
            print(f"  FOUND chi >= 5 augmentation at step {step}!")
            print(f"  |V| = {len(G)} = {len(core)} (core) + {step} asymmetric")
            print(f"  added asymmetric vertices: {added_seq}")
            break

    out = {
        "experiment": "e1o_asymmetric_obstruction",
        "n_core": len(core),
        "n_asymmetric": len(asym),
        "n_singletons_forcing_chi5": len(successful_singletons),
        "singletons": successful_singletons,
        "core_vertices": core,
        "asym_vertices": asym,
        "phase2_added_sequence": added_seq,
        "phase2_final_V": len(G),
        "phase2_final_E": len(G_edges),
        "phase2_chi5_step": step if sat4 is False else None,
    }
    out_path = CACHE / "e1o_asymmetric_obstruction.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
