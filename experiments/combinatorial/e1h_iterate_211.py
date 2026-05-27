r"""e1h: Iterate the 211-vertex double-binding union, adding more rotations.

Architecture 1, Shot 2. Final phase of the field-theoretic search.

Background. e1g built G_0 = M union (all 62 double-binding R-copies across all
7 pivots), |V|=211, |E|=731, chi(G_0) = 4. This is the highest-density UDG
reachable by Moser-spindle double-bindings in Q(sqrt 3, sqrt 11).

This experiment: iterate. Find binding rotations theta such that R_theta(M)
shares MANY unit edges with the current G. At each step, add R_theta(M) for
the theta producing the most new edges. SAT-check chi(G) at each step.

If chi(G) >= 5 at any iteration, we've found a smaller-than-Parts-509
5-chromatic UDG via the binding-rotation route. If chi >= 6, the headline result.
"""

from __future__ import annotations

import json
import pathlib
import time

import mpmath as mp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"

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


def build_g0(M):
    """Reproduce the 211-vertex G_0 from e1g."""
    all_double = []
    seen_keys = set()
    n = len(M)
    for pivot_idx, pivot in enumerate(M):
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
                constraints.append((a, b, c))
        for i in range(len(constraints)):
            for j in range(i + 1, len(constraints)):
                a1, b1, c1 = constraints[i]
                a2, b2, c2 = constraints[j]
                sol = solve_2x2(a1, b1, c1, a2, b2, c2)
                if sol is None:
                    continue
                ct, st = sol
                if mp.fabs(ct*ct + st*st - 1) > mp.mpf("1e-30"):
                    continue
                if mp.fabs(ct - 1) < mp.mpf("1e-30") and mp.fabs(st) < mp.mpf("1e-30"):
                    continue
                key = (pivot_idx, mp.nstr(ct, 25), mp.nstr(st, 25))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                all_double.append({"pivot": pivot_idx, "ct": ct, "st": st})

    union = list(M)
    for rec in all_double:
        pivot = M[rec["pivot"]]
        R = apply_pivot_rotation(M, pivot, rec["ct"], rec["st"])
        union.extend(R)
    uniq, _ = dedup_vertices(union)
    return uniq, all_double


def main():
    print("e1h: iterate the 211-vertex G_0 by adding more binding rotations of M")
    print("=" * 78)

    M = moser_vertices_numeric()
    G, base_rots = build_g0(M)
    G_edges = edges_of(G)
    print(f"  G_0: |V|={len(G)}, |E|={len(G_edges)}")
    s4, _ = sat_k_color(len(G), G_edges, 4)
    print(f"  chi(G_0) <= 4: {s4}")
    print()
    if not s4:
        print("UNEXPECTED: G_0 not 4-colorable")
        return 0

    # Iterate: find rotations of M (about any vertex of G) that hit unit distance
    # with multiple G-vertices. Apply the rotation maximizing new-edge gain.
    print("Phase: iterate. Add R_theta(M) about origin (pivot = G[0]) maximizing new edges.")
    print()
    print(f"  {'it':>3} {'newE':>5} {'|V|':>5} {'|E|':>6} {'E/V':>6} {'4-col':>6} {'5-col':>6} {'time':>8}")

    pivot = M[0]  # origin
    seen_global = set()
    max_iter = 40
    iter_records = []

    for it in range(1, max_iter + 1):
        t0 = time.time()
        # Enumerate single-binding rotations: for each pair (v_p in M, v_q in G),
        # find R_theta about pivot such that R_theta(v_p) is at unit-distance from v_q.
        # This is one linear constraint. Each yields ≤2 solutions; collect them.
        cand = []
        for ip in range(len(M)):
            if mp.fabs(M[ip][0] - pivot[0]) < mp.mpf("1e-50") and \
               mp.fabs(M[ip][1] - pivot[1]) < mp.mpf("1e-50"):
                continue
            for iq in range(len(G)):
                px = M[ip][0] - pivot[0]
                py = M[ip][1] - pivot[1]
                qx = G[iq][0] - pivot[0]
                qy = G[iq][1] - pivot[1]
                p2 = px*px + py*py
                q2 = qx*qx + qy*qy
                if p2 < mp.mpf("1e-60"):
                    continue
                a = px*qx + py*qy
                b = px*qy - py*qx
                c = (p2 + q2 - 1) / 2
                norm_sq = a*a + b*b
                if norm_sq < mp.mpf("1e-60"):
                    continue
                discr = norm_sq - c*c
                if discr < mp.mpf("-1e-30"):
                    continue
                if discr < 0:
                    discr = mp.mpf(0)
                sr = mp.sqrt(discr)
                for sign in (mp.mpf(1), mp.mpf(-1)):
                    ct = (a*c + sign*b*sr) / norm_sq
                    st = (b*c - sign*a*sr) / norm_sq
                    if mp.fabs(ct*ct + st*st - 1) > mp.mpf("1e-25"):
                        continue
                    if mp.fabs(ct - 1) < mp.mpf("1e-30") and mp.fabs(st) < mp.mpf("1e-30"):
                        continue
                    key = (mp.nstr(ct, 20), mp.nstr(st, 20))
                    if key in seen_global:
                        continue
                    cand.append({"ct": ct, "st": st, "key": key})

        # Dedup candidates locally.
        seen_local = set()
        cand_dedup = []
        for c in cand:
            if c["key"] in seen_local:
                continue
            seen_local.add(c["key"])
            cand_dedup.append(c)

        # Score each candidate.
        best = None
        for c in cand_dedup:
            R = apply_pivot_rotation(M, pivot, c["ct"], c["st"])
            cand_union = G + R
            uniq_c, _ = dedup_vertices(cand_union)
            cand_edges = edges_of(uniq_c)
            score = len(cand_edges) - len(G_edges)
            if best is None or score > best["score"]:
                best = {**c, "score": score, "uniq_c": uniq_c, "cand_edges": cand_edges}

        if best is None or best["score"] <= 0:
            print(f"  {it:3d}: no candidate adds new edges; stopping at |V|={len(G)}.")
            break

        seen_global.add(best["key"])
        G = best["uniq_c"]
        G_edges = best["cand_edges"]

        s4, _ = sat_k_color(len(G), G_edges, 4)
        s5 = None
        if s4 is False:
            s5, _ = sat_k_color(len(G), G_edges, 5)

        ev = len(G_edges) / max(len(G), 1)
        mark = ""
        if s4 is False:
            mark = "!!! chi>=5"
        if s5 is False:
            mark = "*** CHI>=6 ***"
        print(f"  {it:3d} {best['score']:5d} {len(G):5d} {len(G_edges):6d} {ev:6.3f} "
              f"{'F' if s4 is False else 'T':>6} "
              f"{('F' if s5 is False else 'T' if s5 is True else '-'):>6} "
              f"{(time.time()-t0):8.1f}s {mark}", flush=True)

        iter_records.append({
            "iter": it, "newE": best["score"], "n_vertices": len(G),
            "n_edges": len(G_edges), "E_over_V": float(ev),
            "4-col": s4, "5-col": s5,
        })

        if s5 is False:
            print("\n  chi >= 6 FOUND")
            break

    out = {
        "experiment": "e1h_iterate_211",
        "iterations": iter_records,
    }
    out_path = CACHE / "e1h_iterate_211.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
