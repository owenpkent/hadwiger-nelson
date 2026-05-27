r"""e1l: Reverse-engineer de Grey 1585.

Architecture 1, Shot 2. Companion to e1i/e1j/e1k.

e1i established that the Polymath/Heule lineage in Q(sqrt 3, sqrt 11) lost
its rotational symmetry to SAT-minimization. e1k built the C_6 closure of
Polymath 510 and showed it is C_6-irreducible.

This experiment analyzes the ORIGINAL de Grey 1585 graph (the 2018
breakthrough), which lives in Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11) per its
Sage source. de Grey's construction was explicit and presumably symmetric;
we expect non-trivial rotational symmetries.

Plan.
(1) Parse sources/degrey_1585_vertices.sage (Python-ish list of vertices).
(2) Parse sources/degrey_1585.dimacs (edge list).
(3) Convert to mpmath 80-digit numerics.
(4) Find exact rotational symmetries about origin and small pivots.
(5) If symmetries exist, compute orbits and try minimal-subset analysis.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time

import mpmath as mp
import sympy as sp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

mp.mp.dps = 80


def parse_sage_vertex_file(path):
    """Parse a Sage-style nested list of [x, y] vertices using sympy.sympify."""
    text = path.read_text(encoding="utf-8")
    # The whole file is a list of lists. Use sympify with sqrt in scope.
    sympy_ctx = {"sqrt": sp.sqrt}
    parsed = sp.sympify(text, locals=sympy_ctx, rational=True)
    # parsed should be a list of length-2 lists.
    verts = []
    for row in parsed:
        verts.append((row[0], row[1]))
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


def vertices_to_numeric(verts_sym, dps=80):
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


def find_unit_edges_numeric(verts_num, tol=mp.mpf("1e-25")):
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


def find_rotation_symmetries(verts_num, pivot, lookup, max_anchors=None):
    """For each anchor in one-per-distance-class, try rotations to every target
    at same distance. Verify R(V) = V exactly. Returns list of rotation dicts."""
    n = len(verts_num)
    seen_r2 = {}
    for i in range(n):
        dx = verts_num[i][0] - pivot[0]
        dy = verts_num[i][1] - pivot[1]
        r2 = dx*dx + dy*dy
        if r2 < mp.mpf("1e-50"):
            continue
        key = mp.nstr(r2, 25)
        if key not in seen_r2:
            seen_r2[key] = i
    anchor_indices = list(seen_r2.values())
    if max_anchors is not None:
        anchor_indices = anchor_indices[:max_anchors]

    rotations = []
    seen_keys = set()
    for anchor_idx in anchor_indices:
        ax = verts_num[anchor_idx][0] - pivot[0]
        ay = verts_num[anchor_idx][1] - pivot[1]
        r2 = ax*ax + ay*ay
        for target in range(n):
            tx = verts_num[target][0] - pivot[0]
            ty = verts_num[target][1] - pivot[1]
            tr2 = tx*tx + ty*ty
            if mp.fabs(tr2 - r2) > mp.mpf("1e-25"):
                continue
            a_dot_t = ax * tx + ay * ty
            a_cross_t = ax * ty - ay * tx
            ct = a_dot_t / r2
            st = a_cross_t / r2
            if mp.fabs(ct*ct + st*st - 1) > mp.mpf("1e-20"):
                continue
            key = (mp.nstr(ct, 25), mp.nstr(st, 25))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            perm = []
            ok = True
            for (x, y) in verts_num:
                dx = x - pivot[0]
                dy = y - pivot[1]
                xr = ct*dx - st*dy + pivot[0]
                yr = st*dx + ct*dy + pivot[1]
                j = lookup((xr, yr))
                if j < 0:
                    ok = False
                    break
                perm.append(j)
            if ok:
                rotations.append({"ct": ct, "st": st, "perm": perm,
                                  "anchor": anchor_idx, "target": target})
    return rotations


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
    print("e1l: reverse-engineer de Grey 1585")
    print("=" * 78)

    sage_path = REPO_ROOT / "sources" / "degrey_1585_vertices.sage"
    edge_path = REPO_ROOT / "sources" / "degrey_1585.dimacs"

    print(f"  parsing {sage_path.relative_to(REPO_ROOT)} ...")
    t0 = time.time()
    verts_sym = parse_sage_vertex_file(sage_path)
    print(f"    {len(verts_sym)} vertices parsed in {time.time() - t0:.1f}s")

    print(f"  parsing {edge_path.relative_to(REPO_ROOT)} ...")
    edges = parse_edge_file(edge_path)
    print(f"    {len(edges)} edges parsed")

    print(f"  converting to mpmath 80-digit numerics ...")
    t0 = time.time()
    verts_num = vertices_to_numeric(verts_sym, dps=80)
    print(f"    done in {time.time() - t0:.1f}s")

    # Sanity: numeric edge count.
    print(f"  computing numeric edges (sanity)...")
    t0 = time.time()
    num_edges = find_unit_edges_numeric(verts_num)
    print(f"    {len(num_edges)} unit edges in {time.time() - t0:.1f}s (expected {len(edges)})")

    # Print the first few vertices to see what we have.
    print()
    print(f"  first 8 vertex norms (distance from origin):")
    for i in range(min(8, len(verts_num))):
        x, y = verts_num[i]
        r = mp.sqrt(x*x + y*y)
        print(f"    v_{i}: |v| = {mp.nstr(r, 6)}")
    print()

    lookup = build_vertex_lookup(verts_num)

    # --- Phase 1: rotational symmetries about multiple pivots ---
    # de Grey's graph isn't centered at origin (his coords start at (2, 0)).
    # Try multiple pivots: origin, vertices 0-5, and the centroid.
    print("Phase 1: rotational symmetries about various pivots.")

    # Compute centroid (geometric center of all vertices).
    cx = sum(v[0] for v in verts_num) / mp.mpf(len(verts_num))
    cy = sum(v[1] for v in verts_num) / mp.mpf(len(verts_num))
    print(f"  centroid: ({mp.nstr(cx, 6)}, {mp.nstr(cy, 6)})")

    pivots_to_try = [
        ("origin", (mp.mpf(0), mp.mpf(0))),
        ("centroid", (cx, cy)),
        ("v_0", verts_num[0]),
        ("v_1", verts_num[1]),
        ("v_2", verts_num[2]),
        ("v_3", verts_num[3]),
        ("v_6", verts_num[6]),
    ]
    # Also try a "shifted origin" close to v_0 = (2, 0): center might be (1, 0)
    # which is the midpoint of plausible Moser-like base.
    pivots_to_try.append(("(1,0)", (mp.mpf(1), mp.mpf(0))))
    # And a guess: maybe the symmetric center is between v_0=(2,0) and v_2=(7/3,0)
    pivots_to_try.append(("midpt v_0 v_2", ((verts_num[0][0] + verts_num[2][0]) / 2,
                                            (verts_num[0][1] + verts_num[2][1]) / 2)))

    rots_by_pivot = {}
    non_trivial_total = []
    for (name, pivot) in pivots_to_try:
        t0 = time.time()
        rots = find_rotation_symmetries(verts_num, pivot, lookup)
        non_trivial = [r for r in rots
                       if not (mp.fabs(r["ct"] - 1) < mp.mpf("1e-25")
                               and mp.fabs(r["st"]) < mp.mpf("1e-25"))]
        rots_by_pivot[name] = (rots, non_trivial, pivot)
        print(f"  pivot '{name}' = ({mp.nstr(pivot[0], 5)}, {mp.nstr(pivot[1], 5)}): "
              f"{len(rots)} rotations ({len(non_trivial)} non-identity) "
              f"in {time.time() - t0:.1f}s")
        if non_trivial:
            angles_print = []
            for r in non_trivial[:10]:
                ct, st = r["ct"], r["st"]
                theta = mp.acos(min(max(ct, mp.mpf(-1)), mp.mpf(1)))
                if st < 0:
                    theta = 2 * mp.pi - theta
                angles_print.append((float(theta), r["anchor"], r["target"]))
            angles_print.sort()
            for (a, anchor, target) in angles_print:
                print(f"    theta={a:8.5f} rad ({a / (2*mp.pi) * 360:7.3f}°)  v_{anchor} -> v_{target}")
            non_trivial_total.extend(non_trivial)

    rots = rots_by_pivot["origin"][0]
    non_trivial = rots_by_pivot["origin"][1]
    print()

    # --- Phase 2: orbit structure if origin has non-trivial rotations ---
    if non_trivial:
        print("Phase 2: vertex orbits under origin-rotation group.")
        n = len(verts_num)
        orbit_of = list(range(n))
        def find(x):
            while orbit_of[x] != x:
                orbit_of[x] = orbit_of[orbit_of[x]]
                x = orbit_of[x]
            return x
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                orbit_of[ra] = rb
        for r in rots:
            for i, j in enumerate(r["perm"]):
                union(i, j)
        orbits = {}
        for i in range(n):
            orbits.setdefault(find(i), []).append(i)
        orbit_sizes = sorted((len(o) for o in orbits.values()), reverse=True)
        size_dist = {}
        for o in orbits.values():
            size_dist[len(o)] = size_dist.get(len(o), 0) + 1
        print(f"  # distinct orbits: {len(orbits)}")
        print(f"  orbit size distribution: {dict(sorted(size_dist.items()))}")
        print(f"  largest orbit sizes (top 10): {orbit_sizes[:10]}")
        print()

    out = {
        "experiment": "e1l_reverse_engineer_degrey1585",
        "n_vertices": len(verts_sym),
        "n_edges_dimacs": len(edges),
        "n_edges_numeric": len(num_edges),
        "rotations_origin_total": len(rots) if 'rots' in locals() else None,
        "rotations_origin_nontrivial": len(non_trivial) if 'non_trivial' in locals() else None,
        "rotations_origin_angles_deg": [
            {
                "theta_deg": float(mp.acos(min(max(r["ct"], mp.mpf(-1)), mp.mpf(1)))
                                    / (2 * mp.pi) * 360
                                    if r["st"] >= 0
                                    else 360 - mp.acos(min(max(r["ct"], mp.mpf(-1)), mp.mpf(1)))
                                                   / (2 * mp.pi) * 360),
                "anchor": r["anchor"], "target": r["target"],
            }
            for r in (non_trivial[:50] if 'non_trivial' in locals() else [])
        ],
        "orbit_size_distribution": (size_dist if 'size_dist' in locals() else None),
        "orbit_count": (len(orbits) if 'orbits' in locals() else None),
    }
    out_path = CACHE / "e1l_degrey1585_symmetry.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
