r"""e1f: Double-binding rotation search.

Architecture 1, Shot 2. Sharpening of e1e.

Motivation. e1e (Phase 4) shows the greedy stacking of single-binding rotations
produces a periodic 4-colorable attractor at E/V ~ 2.27, never escaping to
chi >= 5. The structural reason: each single binding angle catches at most 2
cross-copy unit edges (constraint: one linear equation on (cos t, sin t)).

To force chi >= 5 we need rotations theta such that R_theta(M) shares
SEVERAL unit edges with M (or with the current G). Each unit-edge condition is
a linear equation in (cos t, sin t); the joint condition for k simultaneous
cross-copy edges is a system of k linear equations plus cos^2 + sin^2 = 1.

For k = 2: solve 2x2 linear system uniquely, then check the unit-circle
condition. If the unit-circle equation holds, theta is a "double-binding"
rotation: R_theta(M) has TWO cross-copy unit edges with M.

For k = 3: three linear equations are generically overdetermined; solutions
exist only for algebraic coincidences in the underlying field. These are the
"de Grey miracles."

This experiment systematically enumerates all double-binding rotations of the
Moser spindle in Q(sqrt 3, sqrt 11), tests chi(M union R_theta(M)) for each,
and looks for triple-binding rotations as algebraic surprises.

Method. Numeric only at 80 digits. For each unordered pair of constraints
{(p_1, q_1), (p_2, q_2)}: solve the 2x2 system; check unit circle to 1e-50;
if it holds, accept the rotation. Apply, build the union graph, count cross
edges, SAT-check chi.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import time

import mpmath as mp
import sympy as sp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

mp.mp.dps = 80


def moser_vertices_numeric():
    """Numeric Moser spindle (mpmath, 80 digits)."""
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


def linear_constraint(p, q):
    """Return (a, b, c) such that a cos t + b sin t = c is equivalent to
       |R_t(p) - q|^2 = 1 with rotation about the origin.
       a = <p, q>, b = det[p|q] = p_x q_y - p_y q_x, c = (|p|^2 + |q|^2 - 1)/2.
       Returns None if p is at origin (constraint is trivial)."""
    px, py = p
    qx, qy = q
    p2 = px*px + py*py
    if p2 < mp.mpf("1e-60"):
        return None
    q2 = qx*qx + qy*qy
    a = px*qx + py*qy
    b = px*qy - py*qx
    c = (p2 + q2 - 1) / 2
    return a, b, c


def solve_2x2(a1, b1, c1, a2, b2, c2):
    """Solve a1 x + b1 y = c1 ; a2 x + b2 y = c2 uniquely (or None if det=0)."""
    det = a1 * b2 - a2 * b1
    if mp.fabs(det) < mp.mpf("1e-60"):
        return None
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return x, y


def apply_rotation(verts, ct, st):
    return [(ct*x - st*y, st*x + ct*y) for (x, y) in verts]


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


def main():
    print("e1f: double-binding rotation search on Moser spindle")
    print("=" * 78)

    M = moser_vertices_numeric()
    n = len(M)
    print(f"  Moser seed: {n} vertices (numeric, mp.dps=80)")
    seed_edges = edges_of(M)
    print(f"  seed edges: {len(seed_edges)} (expected 11)")
    s3, _ = sat_k_color(n, seed_edges, 3)
    s4, _ = sat_k_color(n, seed_edges, 4)
    print(f"  seed chi: 3-col={s3}, 4-col={s4}")
    print()

    # --- Phase 1: enumerate all single binding constraints (p in M, q in M) ---
    print("Phase 1: enumerate single binding constraints (p in M, q in M).")
    constraints = []  # list of (i_p, i_q, a, b, c)
    for i_p in range(n):
        if M[i_p][0] == 0 and M[i_p][1] == 0:
            continue
        for i_q in range(n):
            if i_q == i_p:
                continue
            lc = linear_constraint(M[i_p], M[i_q])
            if lc is None:
                continue
            a, b, c = lc
            constraints.append({"p": i_p, "q": i_q, "a": a, "b": b, "c": c})
    print(f"  total single binding constraints: {len(constraints)}")
    print()

    # --- Phase 2: enumerate all double-binding rotations (k = 2) ---
    print("Phase 2: enumerate double-binding rotations.")
    double_pool = []
    seen_keys = set()
    for i in range(len(constraints)):
        for j in range(i + 1, len(constraints)):
            cci = constraints[i]
            ccj = constraints[j]
            sol = solve_2x2(cci["a"], cci["b"], cci["c"],
                            ccj["a"], ccj["b"], ccj["c"])
            if sol is None:
                continue
            ct, st = sol
            # Check unit circle.
            if mp.fabs(ct*ct + st*st - 1) > mp.mpf("1e-30"):
                continue
            # Skip identity.
            if mp.fabs(ct - 1) < mp.mpf("1e-30") and mp.fabs(st) < mp.mpf("1e-30"):
                continue
            # Dedup.
            key = (mp.nstr(ct, 25), mp.nstr(st, 25))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            double_pool.append({"ct": ct, "st": st, "constr_i": (cci["p"], cci["q"]),
                                "constr_j": (ccj["p"], ccj["q"]), "key": key})
    print(f"  double-binding rotations found: {len(double_pool)}")
    print()

    # --- Phase 3: for each double-binding rotation, build M U R(M), count cross edges, chi-test ---
    print("Phase 3: test M union R_theta(M) for each double-binding rotation.")
    print(f"  {'idx':>3} {'theta(rad)':>11} {'|V|':>4} {'|E|':>4} {'cross':>6} {'4-col':>6} {'5-col':>6}")
    results = []
    triple_or_more = []
    for idx, rec in enumerate(double_pool):
        ct, st = rec["ct"], rec["st"]
        R = apply_rotation(M, ct, st)
        union = M + R
        uniq, mapping = dedup_vertices(union)
        all_edges = edges_of(uniq)
        # Count cross edges: an edge (a, b) where preimages straddle the seed/R split.
        preimages = [set() for _ in range(len(uniq))]
        for ui, mi in enumerate(mapping):
            preimages[mi].add(ui)
        cross_edges = 0
        for (a, b) in all_edges:
            a_has_s = any(p < n for p in preimages[a])
            a_has_r = any(p >= n for p in preimages[a])
            b_has_s = any(p < n for p in preimages[b])
            b_has_r = any(p >= n for p in preimages[b])
            a_pure_s = a_has_s and not a_has_r
            a_pure_r = a_has_r and not a_has_s
            b_pure_s = b_has_s and not b_has_r
            b_pure_r = b_has_r and not b_has_s
            if (a_pure_s and b_pure_r) or (a_pure_r and b_pure_s):
                cross_edges += 1
        N_u = len(uniq)
        sat4, _ = sat_k_color(N_u, all_edges, 4)
        sat5 = None
        if sat4 is False:
            sat5, _ = sat_k_color(N_u, all_edges, 5)
        theta = mp.acos(ct) if ct <= 1 else mp.mpf(0)
        if st < 0:
            theta = mp.mpf(2) * mp.pi - theta
        results.append({
            "idx": idx, "constr_i": rec["constr_i"], "constr_j": rec["constr_j"],
            "theta": mp.nstr(theta, 12),
            "n_vertices": N_u, "n_edges": len(all_edges),
            "cross_edges": cross_edges,
            "4-colorable": sat4, "5-colorable": sat5,
        })
        if cross_edges >= 3:
            triple_or_more.append(rec)
        mark = ""
        if sat4 is False:
            mark = "!!! chi>=5"
        if sat5 is False:
            mark = "*** CHI>=6 ***"
        print(f"  {idx:3d} {mp.nstr(theta, 8):>11} {N_u:4d} {len(all_edges):4d} "
              f"{cross_edges:>6} "
              f"{'F' if sat4 is False else 'T':>6} "
              f"{('F' if sat5 is False else 'T' if sat5 is True else '-'):>6} {mark}")

    print()
    print(f"  rotations with cross_edges >= 3 (TRIPLE or higher): {len(triple_or_more)}")
    print()

    # --- Phase 4: stack ALL double-binding rotations at once ---
    print("Phase 4: union M with all double-binding rotations simultaneously.")
    union_all = list(M)
    for rec in double_pool:
        R = apply_rotation(M, rec["ct"], rec["st"])
        union_all.extend(R)
    uniq_all, mapping_all = dedup_vertices(union_all)
    all_edges = edges_of(uniq_all)
    print(f"  union: |V|={len(uniq_all)}, |E|={len(all_edges)}")
    s3_u, _ = sat_k_color(len(uniq_all), all_edges, 3)
    s4_u, _ = sat_k_color(len(uniq_all), all_edges, 4)
    s5_u = None
    if s4_u is False:
        s5_u, _ = sat_k_color(len(uniq_all), all_edges, 5)
    s6_u = None
    if s5_u is False:
        s6_u, _ = sat_k_color(len(uniq_all), all_edges, 6)
    print(f"  chi: 3-col={s3_u}, 4-col={s4_u}, 5-col={s5_u}, 6-col={s6_u}")
    union_chi5 = (s4_u is False)
    union_chi6 = (s5_u is False)
    print()

    # --- Save ---
    out = {
        "experiment": "e1f_double_binding_search",
        "n_single_constraints": len(constraints),
        "n_double_binding_rotations": len(double_pool),
        "n_triple_or_more": len(triple_or_more),
        "results": [
            {**r, "constr_i": list(r["constr_i"]), "constr_j": list(r["constr_j"])}
            for r in results
        ],
        "phase4_union": {
            "n_vertices": len(uniq_all), "n_edges": len(all_edges),
            "3-col": s3_u, "4-col": s4_u, "5-col": s5_u, "6-col": s6_u,
        },
        "found_chi_ge_5": any(r["4-colorable"] is False for r in results) or union_chi5,
        "found_chi_ge_6": any(r["5-colorable"] is False for r in results) or union_chi6,
    }
    out_path = CACHE / "e1f_double_binding_search.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
