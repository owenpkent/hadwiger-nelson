r"""e1k: C_6 closure of Polymath 510, then minimal-subset-of-rotated-copies giving chi >= 5.

Architecture 1, Shot 2. Concrete reverse-engineering of Polymath 510.

e1j showed Polymath 510 has approximate C_6 rotational symmetry about origin:
R_{60°} maps 471/510 (92.35%) of vertices into V. The SAT-minimization broke
~8% of the symmetry by removing redundant vertices.

This experiment:

(1) **C_6 closure**. Add the missing vertices to make R_{60°}-symmetry exact.
    Iterate: while some R_{60°}(v) is not in V, add it to V. Stops when V is
    closed under R_{60°} (and hence under all of C_6). Verify edges.

(2) **Fundamental domain**. Partition V_+ (the closure) into 6-vertex orbits
    under C_6 (some smaller if fixed by sub-rotations). Pick one
    representative per orbit; call this set C. |V_+| = 6 * |C| modulo
    fixed-point orbits.

(3) **Minimal subset of rotated copies**. For each non-empty subset S of
    Z/6 = {0, 1, 2, 3, 4, 5}, build G_S = union_{k in S} R_{60°k}(C).
    SAT-check chi(G_S). Report the smallest S with chi(G_S) >= 5.

Output: the construction "Polymath 510 closed under C_6 admits a (k, |G_S|)-
rotation-decomposition" with k the number of rotated copies needed and
|G_S| the resulting vertex count.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import re
import time

import mpmath as mp
import sympy as sp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

mp.mp.dps = 50


def mathematica_to_sympy(text):
    text = re.sub(r"Sqrt\[([^\]]+)\]", r"sqrt(\1)", text)
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        text = "(" + text[1:-1] + ")"
    return text


def parse_vtx_file(path):
    verts = []
    sympy_ctx = {"sqrt": sp.sqrt}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        s = mathematica_to_sympy(line)
        t = sp.sympify(s, locals=sympy_ctx, rational=True)
        verts.append((t[0], t[1]))
    return verts


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


def find_unit_edges(verts_num, tol=mp.mpf("1e-25")):
    out = []
    one = mp.mpf(1)
    n = len(verts_num)
    for i in range(n):
        for j in range(i + 1, n):
            dx = verts_num[i][0] - verts_num[j][0]
            dy = verts_num[i][1] - verts_num[j][1]
            d2 = dx*dx + dy*dy
            if mp.fabs(d2 - one) < tol:
                out.append((i, j))
    return out


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


def apply_rotation_about_origin(p, ct, st):
    return (ct * p[0] - st * p[1], st * p[0] + ct * p[1])


def main():
    tag = "510"
    print(f"e1k: C_6 closure of Polymath {tag} and minimal-subset analysis")
    print("=" * 78)

    vtx_path = REPO_ROOT / "sources" / "cnp-sat" / "vtx" / f"{tag}.vtx"
    edge_path = REPO_ROOT / "sources" / "cnp-sat" / "edge" / f"{tag}.edge"
    verts_sym = parse_vtx_file(vtx_path)
    edges_dimacs = parse_edge_file(edge_path)
    n0 = len(verts_sym)
    print(f"  loaded {n0} vertices, {len(edges_dimacs)} edges")

    verts_num = vertices_to_numeric(verts_sym, dps=50)

    # Sanity: original chi.
    sat4, t4 = sat_k_color(n0, edges_dimacs, 4)
    print(f"  Polymath 510 chi <= 4: {sat4} (expected False = chi >= 5)")
    print()

    # --- Phase 1: C_6 closure (numeric only; sympy verification deferred) ---
    print("Phase 1: C_6 closure of vertex set (numeric only).")
    ct_60 = mp.mpf(1) / mp.mpf(2)
    st_60 = mp.sqrt(mp.mpf(3)) / mp.mpf(2)

    closure_num = list(verts_num)
    lookup = build_vertex_lookup(closure_num)
    added = 0
    pending = list(range(len(closure_num)))
    iteration = 0
    while pending:
        iteration += 1
        next_pending = []
        for idx in pending:
            p_num = closure_num[idx]
            rk_num = p_num
            for _ in range(5):
                rk_num = apply_rotation_about_origin(rk_num, ct_60, st_60)
                j = lookup(rk_num)
                if j < 0:
                    new_idx = len(closure_num)
                    closure_num.append(rk_num)
                    # Lazy lookup update: add to table inline (avoid full rebuild).
                    next_pending.append(new_idx)
                    added += 1
                    # Tiny lookup update via closure on the table dict isn't
                    # exposed; rebuild lookup periodically.
            # Periodic lookup rebuild.
        # Rebuild lookup once per iteration (cheap).
        lookup = build_vertex_lookup(closure_num)
        pending = next_pending
        print(f"  iter {iteration}: added {added} cumulative; |V|={len(closure_num)}", flush=True)
    n1 = len(closure_num)
    print(f"  added {added} vertices to close under C_6: {n0} -> {n1}")
    print()

    # Recompute edges over closure.
    print(f"Phase 2: edges in C_6 closure (might be slow).")
    t0 = time.time()
    edges_closure = find_unit_edges(closure_num)
    dt = time.time() - t0
    print(f"  {len(edges_closure)} edges in {dt:.1f}s")
    sat4c, t4c = sat_k_color(n1, edges_closure, 4)
    sat5c = None
    t5c = 0.0
    if sat4c is False:
        sat5c, t5c = sat_k_color(n1, edges_closure, 5)
    print(f"  chi(closure): 4-col={sat4c} (expected False), 5-col={sat5c}")
    print()

    # --- Phase 3: fundamental domain under C_6 ---
    print("Phase 3: C_6 orbits.")
    # Build C_6 action as a permutation: rot60[i] = lookup(R_60(v_i)).
    rot60_perm = [-1] * n1
    for i in range(n1):
        p = closure_num[i]
        rp = apply_rotation_about_origin(p, ct_60, st_60)
        j = lookup(rp)
        rot60_perm[i] = j
    # Sanity: rot60_perm should be a permutation (closure under R_60).
    missing = [i for i in range(n1) if rot60_perm[i] < 0]
    print(f"  rot60 missing image count: {len(missing)} (should be 0 if closure complete)")

    # Build orbits by traversing the permutation cycles.
    visited = [False] * n1
    orbits = []
    for i in range(n1):
        if visited[i]:
            continue
        orbit = []
        j = i
        for k in range(7):   # safety: at most 6 rotations bring us back
            if visited[j]:
                break
            orbit.append(j)
            visited[j] = True
            j = rot60_perm[j]
            if j < 0:
                break
        orbits.append(orbit)

    print(f"  # C_6 orbits: {len(orbits)}")
    size_distribution = {}
    for o in orbits:
        size_distribution[len(o)] = size_distribution.get(len(o), 0) + 1
    print(f"  orbit size distribution: {dict(sorted(size_distribution.items()))}")
    # Total vertices accounted: sum sizes
    total_in_orbits = sum(len(o) for o in orbits)
    print(f"  vertices in orbits: {total_in_orbits} (sanity: {n1})")

    # Fundamental domain C: pick one rep per orbit (the lowest-indexed).
    fund_domain = [o[0] for o in orbits]
    print(f"  fundamental domain |C| = {len(fund_domain)}")
    print()

    # --- Phase 4: minimal subset S of Z/6 with chi(union_{k in S} R^k(C)) >= 5 ---
    print("Phase 4: minimal rotation-subset for chi >= 5.")
    print()

    # For each subset of {0, 1, 2, 3, 4, 5}, build G_S = union_{k in S} R^k(C).
    # Vertex inclusion rule depends on orbit size d: orbit[i] (for i in 0..d-1)
    # is included in G_S iff some j in {i, i+d, i+2d, ...} mod 6 is in S.

    def is_included(orbit_size, pos_in_orbit, S_set):
        # Check whether the vertex at position pos_in_orbit in a size-d orbit
        # is reached by some rotation R^k for k in S.
        for k in range(6):
            if k % orbit_size == pos_in_orbit and k in S_set:
                return True
        return False

    print(f"  {'|S|':>3} {'S':>14} {'|V|':>5} {'|E|':>6} {'4-col':>6} {'5-col':>6}")

    subset_results = []
    smallest_chi5 = None
    for size in range(1, 7):
        found_in_size = False
        for S in itertools.combinations(range(6), size):
            S_set = set(S)
            V_S = []
            for o in orbits:
                d = len(o)
                if d == 0:
                    continue
                for pos in range(d):
                    if is_included(d, pos, S_set):
                        V_S.append(o[pos])
            V_S_set = set(V_S)
            E_S = [(u, v) for (u, v) in edges_closure
                   if u in V_S_set and v in V_S_set]
            idx_map = {v: i for i, v in enumerate(V_S)}
            E_S_reidx = [(idx_map[u], idx_map[v]) for (u, v) in E_S]
            sat4S, _ = sat_k_color(len(V_S), E_S_reidx, 4)
            sat5S = None
            if sat4S is False:
                sat5S, _ = sat_k_color(len(V_S), E_S_reidx, 5)
            subset_results.append({
                "S": list(S), "n_vertices": len(V_S), "n_edges": len(E_S),
                "4-colorable": sat4S, "5-colorable": sat5S,
            })
            mark = "!!!" if sat4S is False else ""
            print(f"  {size:3d} {str(S):>14} {len(V_S):5d} {len(E_S):6d} "
                  f"{'F' if sat4S is False else 'T':>6} "
                  f"{('F' if sat5S is False else 'T' if sat5S is True else '-'):>6} {mark}", flush=True)
            if sat4S is False and smallest_chi5 is None:
                smallest_chi5 = {"S": list(S), "n_vertices": len(V_S), "n_edges": len(E_S)}
                found_in_size = True
        if found_in_size:
            print(f"  -- found smallest chi>=5 subset at size {size}; continuing for completeness --")
            print()
            break

    print()
    if smallest_chi5:
        print(f"SMALLEST CHI >= 5 SUBSET: {smallest_chi5['S']}")
        print(f"  |V| = {smallest_chi5['n_vertices']}, |E| = {smallest_chi5['n_edges']}")
    else:
        print("No chi >= 5 subset found at any size (unexpected).")

    out = {
        "experiment": "e1k_c6_closure_minimal",
        "graph_tag": tag,
        "n_original": n0,
        "n_closure": n1,
        "n_added": added,
        "n_edges_closure": len(edges_closure),
        "chi_closure_4col": sat4c,
        "chi_closure_5col": sat5c,
        "n_orbits": len(orbits),
        "orbit_size_distribution": {str(k): v for k, v in size_distribution.items()},
        "subset_results": subset_results,
        "smallest_chi5_subset": smallest_chi5,
    }
    out_path = CACHE / "e1k_c6_closure_minimal.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
