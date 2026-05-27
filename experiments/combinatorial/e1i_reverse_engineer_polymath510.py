r"""e1i: Reverse-engineer Polymath 510 as binding-rotation construction.

Architecture 1, Shot 2. Continues the L14 thread.

Plan.

(1) Parse [sources/cnp-sat/vtx/510.vtx](../../sources/cnp-sat/vtx/510.vtx)
    (Mathematica syntax) to sympy + mpmath high-precision coordinates.
    Parse [sources/cnp-sat/edge/510.edge](../../sources/cnp-sat/edge/510.edge)
    (DIMACS edge format) to edge list.

(2) Find ALL rotational symmetries: rotations R about origin (or any vertex)
    such that R(V) = V. The set of such rotations forms a subgroup of O(2).

(3) Decompose V into rotation orbits under the symmetry group. Identify
    "generating" vertices (orbit representatives).

(4) For each rotation angle theta in the symmetry group, characterize it as
    a binding rotation: which seed-pair (p, q) does it solve?

(5) Greedy minimum-subset search: find the smallest subset S of rotations
    such that union_{R in S} R(seed) is still 5-chromatic.

Output: a description of Polymath 510 as "(seed) rotated by these k angles
about these pivots, then unioned and SAT-verified".
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

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

mp.mp.dps = 80


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def mathematica_to_sympy(text):
    """Convert simple Mathematica expressions to sympy.
    Handles: Sqrt[n] -> sqrt(n), {x, y} -> tuple, basic arithmetic.
    """
    # Replace Sqrt[...] with sqrt(...)
    text = re.sub(r"Sqrt\[([^\]]+)\]", r"sqrt(\1)", text)
    text = text.strip()
    # Curly braces -> parens for tuples
    if text.startswith("{") and text.endswith("}"):
        text = "(" + text[1:-1] + ")"
    return text


def parse_vtx_file(path):
    """Parse a .vtx file with Mathematica syntax. Returns list of sympy
    2-tuples."""
    verts = []
    sympy_ctx = {"sqrt": sp.sqrt}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        s = mathematica_to_sympy(line)
        try:
            t = sp.sympify(s, locals=sympy_ctx, rational=True)
        except Exception as e:
            raise ValueError(f"line {line_no}: {line!r} -> {s!r} parse error: {e}")
        if not isinstance(t, sp.Tuple) and not isinstance(t, tuple):
            # sp.sympify on "(a, b)" produces a Tuple
            t = sp.Tuple(*t)
        verts.append((t[0], t[1]))
    return verts


def parse_edge_file(path):
    """Parse a DIMACS .edge file. Returns list of (u, v) 0-indexed pairs."""
    edges = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("c") or line.startswith("p"):
            continue
        if line.startswith("e"):
            parts = line.split()
            u, v = int(parts[1]) - 1, int(parts[2]) - 1
            edges.append((u, v))
    return edges


def vertices_to_numeric(verts_sym, dps=80):
    """Convert sympy vertices to mpmath 2-tuples at given precision."""
    out = []
    with mp.workdps(dps):
        for (x, y) in verts_sym:
            xn = mp.mpf(str(sp.N(x, dps)))
            yn = mp.mpf(str(sp.N(y, dps)))
            out.append((xn, yn))
    return out


# ---------------------------------------------------------------------------
# Edge-set sanity checks
# ---------------------------------------------------------------------------

def verify_edges_exact(verts_sym, edges):
    """For each edge (u, v), check |v_u - v_v|^2 == 1 symbolically.
    Returns (good_count, bad_list)."""
    good = 0
    bad = []
    for (u, v) in edges:
        dx = verts_sym[u][0] - verts_sym[v][0]
        dy = verts_sym[u][1] - verts_sym[v][1]
        d2 = sp.simplify(dx*dx + dy*dy)
        if d2 == 1:
            good += 1
        else:
            n = float(sp.N(d2, 50))
            if abs(n - 1) < 1e-30:
                d2_simpler = sp.simplify(sp.radsimp(d2 - 1))
                if d2_simpler == 0:
                    good += 1
                    continue
            bad.append((u, v, sp.nsimplify(d2)))
    return good, bad


def find_unit_distances_numeric(verts_num, tol=mp.mpf("1e-30")):
    """For sanity: find all numeric unit-distance pairs."""
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


# ---------------------------------------------------------------------------
# Rotational symmetry search
# ---------------------------------------------------------------------------

def build_vertex_lookup(verts_num, tol=mp.mpf("1e-40")):
    """Return a function lookup(p) -> index in verts_num if any, else -1."""
    # Hash to a quantized key for fast first pass.
    def quantize(x):
        return mp.nstr(x, 30)
    table = {}
    for idx, (x, y) in enumerate(verts_num):
        table.setdefault((quantize(x), quantize(y)), []).append(idx)

    def lookup(p):
        kx = quantize(p[0])
        ky = quantize(p[1])
        # Check exact bucket first
        for idx in table.get((kx, ky), []):
            ux, uy = verts_num[idx]
            if mp.fabs(p[0] - ux) < tol and mp.fabs(p[1] - uy) < tol:
                return idx
        # Fallback: brute scan neighboring quantization buckets (rare)
        return -1
    return lookup


def find_rotation_symmetries(verts_num, pivot, lookup, anchor_indices=None):
    """Find all rotations R about pivot mapping verts_num set to itself.

    Strategy: pick anchor v_a (a single vertex on each orbit suffices). For
    each target v_t at the same distance from pivot, compute the rotation
    sending v_a to v_t and verify R(V) = V.

    To exhaustively discover all rotations: try EACH anchor index in
    anchor_indices (default = small set covering each distance class).
    Dedup by (ct, st).
    """
    n = len(verts_num)
    if anchor_indices is None:
        # Pick anchors at each distance value (one per distance class).
        # Use a coarse quantization on distance.
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

    rotations = []
    seen_keys = set()
    for anchor_idx in anchor_indices:
        ax = verts_num[anchor_idx][0] - pivot[0]
        ay = verts_num[anchor_idx][1] - pivot[1]
        r2 = ax*ax + ay*ay
        if r2 < mp.mpf("1e-50"):
            continue
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
            if mp.fabs(ct*ct + st*st - 1) > mp.mpf("1e-25"):
                continue
            key = (mp.nstr(ct, 25), mp.nstr(st, 25))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            # Apply to all vertices; check that R(V) = V.
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="510",
                        help="graph tag (510, 553, 826, 874, etc.)")
    parser.add_argument("--pivots", default="0,1,2,3,4,5,6",
                        help="comma-separated vertex indices to use as rotation pivots")
    args = parser.parse_args(sys.argv[1:])

    tag = args.graph
    pivot_indices = [int(x) for x in args.pivots.split(",") if x.strip()]

    print(f"e1i: reverse-engineer Polymath/Heule {tag} via rotational symmetry analysis")
    print("=" * 78)

    vtx_path = REPO_ROOT / "sources" / "cnp-sat" / "vtx" / f"{tag}.vtx"
    edge_path = REPO_ROOT / "sources" / "cnp-sat" / "edge" / f"{tag}.edge"

    print(f"  parsing {vtx_path.relative_to(REPO_ROOT)} ...")
    t0 = time.time()
    verts_sym = parse_vtx_file(vtx_path)
    print(f"    {len(verts_sym)} vertices parsed in {time.time() - t0:.1f}s")

    print(f"  parsing {edge_path.relative_to(REPO_ROOT)} ...")
    edges = parse_edge_file(edge_path)
    print(f"    {len(edges)} edges parsed")

    # Skip full exact verification (slow at 510*2504); verify_distances done in e1b.
    # Convert to numeric.
    print(f"  converting to mpmath 80-digit numerics ...")
    t0 = time.time()
    verts_num = vertices_to_numeric(verts_sym, dps=80)
    print(f"    done in {time.time() - t0:.1f}s")

    # Sanity: numeric edge count should equal claimed edge count.
    t0 = time.time()
    num_edges = find_unit_distances_numeric(verts_num)
    print(f"  numeric edge count: {len(num_edges)} (expected {len(edges)})")
    print(f"    in {time.time() - t0:.1f}s")

    lookup = build_vertex_lookup(verts_num)

    # --- Phase 1: rotational symmetries about each pivot ---
    print()
    print(f"Phase 1: rotational symmetries about pivots {pivot_indices}.")
    all_pivot_rots = {}
    for p_idx in pivot_indices:
        if p_idx >= len(verts_num):
            continue
        pivot = verts_num[p_idx]
        t0 = time.time()
        rots = find_rotation_symmetries(verts_num, pivot, lookup)
        all_pivot_rots[p_idx] = rots
        # Non-trivial = not identity.
        non_trivial = [r for r in rots
                       if not (mp.fabs(r["ct"] - 1) < mp.mpf("1e-25")
                               and mp.fabs(r["st"]) < mp.mpf("1e-25"))]
        print(f"  pivot v_{p_idx} = ({mp.nstr(pivot[0], 5)}, {mp.nstr(pivot[1], 5)}): "
              f"{len(rots)} total ({len(non_trivial)} non-identity) in {time.time() - t0:.1f}s")
        if non_trivial:
            for r in non_trivial[:6]:
                ct, st = r["ct"], r["st"]
                theta = mp.acos(min(max(ct, mp.mpf(-1)), mp.mpf(1)))
                if st < 0:
                    theta = 2 * mp.pi - theta
                print(f"    theta={float(theta):8.5f} rad  v_{r['anchor']} -> v_{r['target']}")
            if len(non_trivial) > 6:
                print(f"    ... and {len(non_trivial) - 6} more")
    print()

    # Combine all rotations across pivots.
    total_rots = sum(len(v) for v in all_pivot_rots.values())
    total_nontrivial = sum(
        len([r for r in v
             if not (mp.fabs(r["ct"] - 1) < mp.mpf("1e-25")
                     and mp.fabs(r["st"]) < mp.mpf("1e-25"))])
        for v in all_pivot_rots.values())
    print(f"Total rotations across pivots: {total_rots} ({total_nontrivial} non-identity)")
    print()

    # --- Phase 2: orbit structure if origin has nontrivial rotations ---
    rots_origin = all_pivot_rots.get(0, [])
    if rots_origin and len(rots_origin) > 1:
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
        for r in rots_origin:
            for i, j in enumerate(r["perm"]):
                union(i, j)
        orbits = {}
        for i in range(n):
            orbits.setdefault(find(i), []).append(i)
        orbit_sizes = sorted((len(o) for o in orbits.values()), reverse=True)
        print(f"  # distinct orbits: {len(orbits)}")
        print(f"  orbit size distribution (top 12): {orbit_sizes[:12]}")
        print()
    else:
        orbits = None
        orbit_sizes = None
        print("Phase 2 skipped: no non-trivial rotation about origin.")
        print()

    # --- Save ---
    out = {
        "experiment": "e1i_reverse_engineer",
        "graph_tag": tag,
        "n_vertices": len(verts_sym),
        "n_edges_dimacs": len(edges),
        "n_edges_numeric": len(num_edges),
        "pivot_rotations": {
            str(p_idx): [
                {"ct": mp.nstr(r["ct"], 30), "st": mp.nstr(r["st"], 30),
                 "anchor": r["anchor"], "target": r["target"]}
                for r in rots
            ]
            for p_idx, rots in all_pivot_rots.items()
        },
        "orbit_count": len(orbits) if orbits else None,
        "orbit_size_distribution": orbit_sizes,
    }
    out_path = CACHE / f"e1i_{tag}_symmetry.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
