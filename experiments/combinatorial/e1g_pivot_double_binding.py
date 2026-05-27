r"""e1g: Double-binding search with variable rotation pivot.

Architecture 1, Shot 2. Sharpening of e1f.

e1f found 6 double-binding rotations of Moser about the origin, ALL DEGENERATE
(second constraint satisfied by vertex coincidence, zero cross edges). The
algebra of Q(sqrt 3, sqrt 11) over the Moser spindle is too rigid to support
non-degenerate double bindings about a fixed pivot.

This experiment varies the pivot point. For pivot v_k (any Moser vertex) and
rotation R_{v_k, theta}, the constraint |R_{v_k, theta}(p) - q| = 1 becomes
|v_k + R_theta(p - v_k) - q| = 1, equivalent to
|R_theta(p - v_k) - (q - v_k)| = 1, i.e., a linear equation in (cos t, sin t):
   <p - v_k, q - v_k> cos t + det[p - v_k | q - v_k] sin t = (|p-v_k|^2 + |q-v_k|^2 - 1) / 2.

For each pivot v_k, enumerate single binding constraints, then solve all pairs
for double bindings, then test M union R_{v_k, theta}(M) for chi.
"""

from __future__ import annotations

import json
import pathlib
import time

import mpmath as mp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

mp.mp.dps = 80


def moser_vertices_numeric():
    sqrt3 = mp.sqrt(3)
    sqrt11 = mp.sqrt(11)
    cos_t = mp.mpf(5) / mp.mpf(6)
    sin_t = sqrt11 / mp.mpf(6)
    A = (mp.mpf(0), mp.mpf(0))
    B = (mp.mpf(1), mp.mpf(0))
    C = (mp.mpf(1) / mp.mpf(2), sqrt3 / mp.mpf(2))
    D = (mp.mpf(3) / mp.mpf(2), sqrt3 / mp.mpf(2))
    rot = lambda p: (cos_t * p[0] - sin_t * p[1], sin_t * p[0] + cos_t * p[1])
    return [A, B, C, D, rot(B), rot(C), rot(D)]


def linear_constraint(p, q, pivot):
    """For rotation about pivot, return (a, b, c) such that |R_t(p) - q| = 1
       <=> a cos t + b sin t = c. Returns None if degenerate (p == pivot)."""
    px = p[0] - pivot[0]
    py = p[1] - pivot[1]
    qx = q[0] - pivot[0]
    qy = q[1] - pivot[1]
    p2 = px*px + py*py
    if p2 < mp.mpf("1e-60"):
        return None
    q2 = qx*qx + qy*qy
    a = px*qx + py*qy
    b = px*qy - py*qx
    c = (p2 + q2 - 1) / 2
    return a, b, c


def solve_2x2(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1
    if mp.fabs(det) < mp.mpf("1e-60"):
        return None
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return x, y


def apply_pivot_rotation(verts, pivot, ct, st):
    out = []
    for (x, y) in verts:
        dx = x - pivot[0]
        dy = y - pivot[1]
        xr = ct*dx - st*dy + pivot[0]
        yr = st*dx + ct*dy + pivot[1]
        out.append((xr, yr))
    return out


def dedup_vertices(verts, tol=mp.mpf("1e-40")):
    uniq = []
    mapping = []
    for v in verts:
        idx = None
        for j, u in enumerate(uniq):
            if mp.fabs(v[0] - u[0]) < tol and mp.fabs(v[1] - u[1]) < tol:
                idx = j
                break
        if idx is None:
            idx = len(uniq)
            uniq.append(v)
        mapping.append(idx)
    return uniq, mapping


def edges_of(verts, tol=mp.mpf("1e-30")):
    out = []
    one = mp.mpf(1)
    n = len(verts)
    for i in range(n):
        for j in range(i + 1, n):
            dx = verts[i][0] - verts[j][0]
            dy = verts[i][1] - verts[j][1]
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


def cross_edges_count(uniq, edges, mapping, n_seed):
    preimages = [set() for _ in range(len(uniq))]
    for ui, mi in enumerate(mapping):
        preimages[mi].add(ui)
    c = 0
    for (a, b) in edges:
        a_s = any(p < n_seed for p in preimages[a])
        a_r = any(p >= n_seed for p in preimages[a])
        b_s = any(p < n_seed for p in preimages[b])
        b_r = any(p >= n_seed for p in preimages[b])
        a_pure_s = a_s and not a_r
        a_pure_r = a_r and not a_s
        b_pure_s = b_s and not b_r
        b_pure_r = b_r and not b_s
        if (a_pure_s and b_pure_r) or (a_pure_r and b_pure_s):
            c += 1
    return c


def main():
    print("e1g: pivot-varied double-binding rotation search on Moser spindle")
    print("=" * 78)

    M = moser_vertices_numeric()
    n = len(M)
    seed_edges = edges_of(M)
    print(f"  Moser seed: {n} vertices, {len(seed_edges)} edges")
    print()

    all_pivot_results = []
    n_chi5 = 0
    n_chi6 = 0
    n_triple_plus = 0

    # All double-binding rotations found across pivots, deduped.
    all_double = []
    all_double_keys = set()

    for pivot_idx, pivot in enumerate(M):
        # --- Phase per-pivot ---
        print(f"  Pivot v_{pivot_idx} = ({mp.nstr(pivot[0], 4)}, {mp.nstr(pivot[1], 4)})")
        constraints = []
        for i_p in range(n):
            if mp.fabs(M[i_p][0] - pivot[0]) < mp.mpf("1e-50") and \
               mp.fabs(M[i_p][1] - pivot[1]) < mp.mpf("1e-50"):
                continue
            for i_q in range(n):
                if i_q == i_p:
                    continue
                lc = linear_constraint(M[i_p], M[i_q], pivot)
                if lc is None:
                    continue
                a, b, c = lc
                constraints.append({"p": i_p, "q": i_q, "a": a, "b": b, "c": c})

        # Enumerate double-binding rotations.
        per_pivot_doubles = []
        seen_local = set()
        for i in range(len(constraints)):
            for j in range(i + 1, len(constraints)):
                cci = constraints[i]
                ccj = constraints[j]
                sol = solve_2x2(cci["a"], cci["b"], cci["c"],
                                ccj["a"], ccj["b"], ccj["c"])
                if sol is None:
                    continue
                ct, st = sol
                if mp.fabs(ct*ct + st*st - 1) > mp.mpf("1e-30"):
                    continue
                if mp.fabs(ct - 1) < mp.mpf("1e-30") and mp.fabs(st) < mp.mpf("1e-30"):
                    continue
                key = (pivot_idx, mp.nstr(ct, 25), mp.nstr(st, 25))
                if key in seen_local:
                    continue
                seen_local.add(key)
                per_pivot_doubles.append({
                    "pivot": pivot_idx, "ct": ct, "st": st,
                    "constr_i": (cci["p"], cci["q"]),
                    "constr_j": (ccj["p"], ccj["q"]),
                })
                global_key = ("p" + str(pivot_idx), mp.nstr(ct, 20), mp.nstr(st, 20))
                if global_key not in all_double_keys:
                    all_double_keys.add(global_key)
                    all_double.append({
                        "pivot": pivot_idx, "ct": ct, "st": st,
                    })

        print(f"    {len(constraints)} constraints, {len(per_pivot_doubles)} double bindings")

        # Test each.
        pivot_results = []
        for k_idx, rec in enumerate(per_pivot_doubles):
            R = apply_pivot_rotation(M, pivot, rec["ct"], rec["st"])
            union = list(M) + R
            uniq, mapping = dedup_vertices(union)
            edges = edges_of(uniq)
            cross = cross_edges_count(uniq, edges, mapping, n)
            sat4, _ = sat_k_color(len(uniq), edges, 4)
            sat5 = None
            if sat4 is False:
                sat5, _ = sat_k_color(len(uniq), edges, 5)
            pivot_results.append({
                "k": k_idx, "pivot": pivot_idx,
                "constr_i": list(rec["constr_i"]), "constr_j": list(rec["constr_j"]),
                "n_vertices": len(uniq), "n_edges": len(edges),
                "cross_edges": cross,
                "4-colorable": sat4, "5-colorable": sat5,
            })
            if cross >= 3:
                n_triple_plus += 1
            if sat4 is False:
                n_chi5 += 1
            if sat5 is False:
                n_chi6 += 1

        all_pivot_results.extend(pivot_results)

        # Summary line for the pivot.
        if per_pivot_doubles:
            best_cross = max(r["cross_edges"] for r in pivot_results)
            print(f"    best cross-edge count across {len(per_pivot_doubles)} double bindings: {best_cross}")
        print()

    print("=" * 78)
    print(f"Total double bindings across all 7 pivots: {len(all_double)}")
    print(f"  cross_edges >= 3 (triple-plus): {n_triple_plus}")
    print(f"  producing chi >= 5: {n_chi5}")
    print(f"  producing chi >= 6: {n_chi6}")
    print()

    # --- Final union: stack ALL double-binding rotations across all pivots ---
    print("Final: union M with ALL double-binding rotations (all pivots).")
    union_all = list(M)
    for rec in all_double:
        pivot = M[rec["pivot"]]
        R = apply_pivot_rotation(M, pivot, rec["ct"], rec["st"])
        union_all.extend(R)
    uniq_all, mapping_all = dedup_vertices(union_all)
    edges_all = edges_of(uniq_all)
    print(f"  union: |V|={len(uniq_all)}, |E|={len(edges_all)}")
    s3, _ = sat_k_color(len(uniq_all), edges_all, 3)
    s4, _ = sat_k_color(len(uniq_all), edges_all, 4)
    s5 = None
    if s4 is False:
        s5, _ = sat_k_color(len(uniq_all), edges_all, 5)
    s6 = None
    if s5 is False:
        s6, _ = sat_k_color(len(uniq_all), edges_all, 6)
    print(f"  chi: 3-col={s3}, 4-col={s4}, 5-col={s5}, 6-col={s6}")
    print()

    out = {
        "experiment": "e1g_pivot_double_binding",
        "n_double_bindings_total": len(all_double),
        "n_triple_plus": n_triple_plus,
        "n_chi5": n_chi5, "n_chi6": n_chi6,
        "results": all_pivot_results,
        "final_union": {
            "n_vertices": len(uniq_all), "n_edges": len(edges_all),
            "3-col": s3, "4-col": s4, "5-col": s5, "6-col": s6,
        },
    }
    out_path = CACHE / "e1g_pivot_double_binding.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
