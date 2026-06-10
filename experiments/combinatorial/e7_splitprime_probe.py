"""Calibration probe for the split-prime Eisenstein ensemble (BUILDER lens:
random/extremal UDGs outside the de Grey/Polymath lineage).

Object: the unit-distance graph on patches of the localized ring
E_7 = Z[omega, 1/7], omega = e^{i pi/3}. Points at 7-adic level <= 1 are
z = (a + b*omega)/7 with a, b integers; the squared Euclidean norm is
N(a + b*omega)/49 with N(a,b) = a^2 + a*b + b^2 (Loeschian form).
Unit edges = numerator differences of norm exactly 49. There are 18 such
directions: 6 units * {7, pi^2, pibar^2}, pi = 1 + 2*omega (N(pi) = 7).
The pi^2/7 = u_7 directions are the split-prime "foreign spindle" twist
(rotation by arccos(1/7)); they connect the 49 hex-sublattice cosets.

All arithmetic is exact integer arithmetic (no radicals, no floats in the
edge test). This probe measures n, average degree, triangle presence, and
SAT 4/5-colorability of small saturated patches, plus a Gaussian control
Z[i, 1/5] (subset of Q^2, must stay bipartite: chi = 2).
"""

import itertools
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
os.makedirs(CACHE, exist_ok=True)


def eisenstein_patch(level_den, radius_num_sq):
    """Vertices (a, b) = numerators of z = (a + b*omega)/level_den with
    N(a,b) <= radius_num_sq. Returns list of (a, b)."""
    out = []
    # N(a,b) = a^2 + ab + b^2; bound |a|, |b| <= 2*sqrt(R) is safe.
    import math
    m = int(2 * math.isqrt(radius_num_sq) + 2)
    for a in range(-m, m + 1):
        for b in range(-m, m + 1):
            if a * a + a * b + b * b <= radius_num_sq:
                out.append((a, b))
    return out


def eisenstein_edges(verts, unit_norm):
    """Edges = pairs with N(diff) == unit_norm. Exact integers."""
    index = {v: i for i, v in enumerate(verts)}
    # enumerate the difference vectors of norm unit_norm once
    dirs = []
    import math
    m = int(2 * math.isqrt(unit_norm) + 2)
    for a in range(-m, m + 1):
        for b in range(-m, m + 1):
            if a * a + a * b + b * b == unit_norm:
                dirs.append((a, b))
    edges = set()
    for (a, b) in verts:
        i = index[(a, b)]
        for (da, db) in dirs:
            w = (a + da, b + db)
            j = index.get(w)
            if j is not None and j > i:
                edges.add((i, j))
    return sorted(edges), dirs


def gaussian_patch_edges(level_den, radius_num_sq, unit_norm):
    """Control: Z[i, 1/5]-style patch. N(a,b) = a^2 + b^2."""
    import math
    m = int(2 * math.isqrt(radius_num_sq) + 2)
    verts = [(a, b) for a in range(-m, m + 1) for b in range(-m, m + 1)
             if a * a + b * b <= radius_num_sq]
    index = {v: i for i, v in enumerate(verts)}
    dirs = [(a, b) for a in range(-m, m + 1) for b in range(-m, m + 1)
            if a * a + b * b == unit_norm]
    edges = set()
    for (a, b) in verts:
        i = index[(a, b)]
        for (da, db) in dirs:
            j = index.get((a + da, b + db))
            if j is not None and j > i:
                edges.add((i, j))
    return verts, sorted(edges)


def sat_colorable(n, edges, k, conflict_budget=None):
    """k-colorability via python-sat. Returns (status, seconds).
    status in {True, False, None} (None = budget exhausted)."""
    from pysat.solvers import Cadical153
    cnf = []
    var = lambda v, c: v * k + c + 1
    for v in range(n):
        cnf.append([var(v, c) for c in range(k)])
    for (u, v) in edges:
        for c in range(k):
            cnf.append([-var(u, c), -var(v, c)])
    t0 = time.time()
    with Cadical153(bootstrap_with=cnf) as s:
        if conflict_budget:
            s.conf_budget(conflict_budget)
            res = s.solve_limited()
        else:
            res = s.solve()
    return res, time.time() - t0


def bipartite_check(n, edges):
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    return nx.is_bipartite(g)


def main():
    results = {}

    for radius in (2, 3):
        rsq = 49 * radius * radius  # numerator norm bound for |z| <= radius
        verts = eisenstein_patch(7, rsq)
        edges, dirs = eisenstein_edges(verts, 49)
        n, m = len(verts), len(edges)
        avg_deg = 2.0 * m / n
        # triangle presence: any unit equilateral (u, u+d1, u+d2)?
        dirset = set(dirs)
        tri = any(((d1[0] - d2[0], d1[1] - d2[1]) in dirset)
                  for d1, d2 in itertools.combinations(dirs, 2))
        print(f"[E7 level<=1 radius {radius}] n={n} m={m} "
              f"avg_deg={avg_deg:.2f} unit_dirs={len(dirs)} triangles={tri}")
        entry = {"n": n, "m": m, "avg_deg": avg_deg,
                 "unit_dirs": len(dirs), "has_triangle": tri}
        for k in (3, 4, 5):
            res, dt = sat_colorable(n, edges, k, conflict_budget=3_000_000)
            print(f"  {k}-colorable: {res}   ({dt:.1f}s)")
            entry[f"col{k}"] = res
            if res:
                break_at = k
        results[f"E7_r{radius}"] = entry

    # Gaussian control: Z[i, 1/5], level 1, radius 2. Unit norm = 25.
    gverts, gedges = gaussian_patch_edges(5, 25 * 4, 25)
    gn, gm = len(gverts), len(gedges)
    bip = bipartite_check(gn, gedges)
    print(f"[Gaussian control Z[i,1/5] radius 2] n={gn} m={gm} "
          f"avg_deg={2*gm/gn:.2f} bipartite={bip} (must be True; Q^2 has chi=2)")
    results["gaussian_control"] = {"n": gn, "m": gm, "bipartite": bip}

    with open(os.path.join(CACHE, "e7_splitprime_probe.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("cached ->", os.path.join(CACHE, "e7_splitprime_probe.json"))


if __name__ == "__main__":
    main()
