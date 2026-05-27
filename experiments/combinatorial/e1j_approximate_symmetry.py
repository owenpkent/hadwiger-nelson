r"""e1j: Approximate-symmetry analysis of Polymath 510 / Heule 826.

Architecture 1, Shot 2. Continues e1i's negative finding.

e1i established that Polymath 510 and Heule 826 have NO non-identity exact
rotational symmetries (the SAT-driven minimization destroyed them). But the
graph may still have *approximate* rotational structure: rotations R such
that R(V) is largely contained in V even if R(V) != V.

This experiment finds rotations with high coverage. For each (u, v) pair at
the same distance from a pivot, compute the rotation R taking u to v, then
count |{w : R(w) in V}|. The top-coverage rotations are the "skeleton" of
the construction.

Method.
1. Group vertices by distance from each pivot (origin and 6 unit-distance
   neighbors).
2. Within each distance class, enumerate (u, v) pairs and compute R.
3. For each R, compute coverage.
4. Report top-coverage rotations across all pivots.
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


def find_high_coverage_rotations(verts_num, pivot, lookup, min_coverage_frac=0.5):
    """For each pair (u, v) at same distance from pivot, compute rotation R
    taking u to v about pivot. Compute coverage = |R(V) cap V|. Return list
    sorted by coverage descending, with only those above min_coverage_frac * N.
    """
    n = len(verts_num)
    # Group vertices by distance class (from pivot).
    dist_classes = {}
    for i in range(n):
        dx = verts_num[i][0] - pivot[0]
        dy = verts_num[i][1] - pivot[1]
        r2 = dx*dx + dy*dy
        if r2 < mp.mpf("1e-50"):
            continue
        key = mp.nstr(r2, 20)
        dist_classes.setdefault(key, []).append(i)

    results = []
    seen_keys = set()
    threshold = int(min_coverage_frac * n)
    for class_key, class_verts in dist_classes.items():
        if len(class_verts) < 2:
            continue
        # Anchor: first vertex in class.
        anchor_idx = class_verts[0]
        ax = verts_num[anchor_idx][0] - pivot[0]
        ay = verts_num[anchor_idx][1] - pivot[1]
        r2 = ax*ax + ay*ay
        for target_idx in class_verts:
            tx = verts_num[target_idx][0] - pivot[0]
            ty = verts_num[target_idx][1] - pivot[1]
            ct = (ax*tx + ay*ty) / r2
            st = (ax*ty - ay*tx) / r2
            if mp.fabs(ct*ct + st*st - 1) > mp.mpf("1e-20"):
                continue
            key = (mp.nstr(ct, 18), mp.nstr(st, 18))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            # Compute coverage.
            cov = 0
            for (x, y) in verts_num:
                dx = x - pivot[0]
                dy = y - pivot[1]
                xr = ct*dx - st*dy + pivot[0]
                yr = st*dx + ct*dy + pivot[1]
                j = lookup((xr, yr))
                if j >= 0:
                    cov += 1
            if cov >= threshold:
                results.append({
                    "ct": ct, "st": st, "anchor": anchor_idx,
                    "target": target_idx, "coverage": cov,
                })
    results.sort(key=lambda r: -r["coverage"])
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="510")
    parser.add_argument("--pivots", default="0,1")
    parser.add_argument("--min-frac", type=float, default=0.5,
                        help="minimum coverage fraction (default 0.5)")
    args = parser.parse_args(sys.argv[1:])

    tag = args.graph
    pivot_indices = [int(x) for x in args.pivots.split(",") if x.strip()]

    print(f"e1j: approximate-symmetry analysis of {tag}")
    print("=" * 78)

    vtx_path = REPO_ROOT / "sources" / "cnp-sat" / "vtx" / f"{tag}.vtx"
    verts_sym = parse_vtx_file(vtx_path)
    n = len(verts_sym)
    print(f"  {n} vertices loaded")

    verts_num = vertices_to_numeric(verts_sym, dps=50)
    lookup = build_vertex_lookup(verts_num)

    threshold = int(args.min_frac * n)
    print(f"  reporting rotations with coverage >= {threshold} ({args.min_frac:.0%})")
    print()

    all_results = {}
    for p_idx in pivot_indices:
        pivot = verts_num[p_idx]
        t0 = time.time()
        rots = find_high_coverage_rotations(verts_num, pivot, lookup, args.min_frac)
        dt = time.time() - t0
        all_results[p_idx] = rots
        print(f"  pivot v_{p_idx} = ({mp.nstr(pivot[0], 5)}, {mp.nstr(pivot[1], 5)}): "
              f"{len(rots)} high-coverage rotations in {dt:.1f}s")
        for r in rots[:10]:
            theta = mp.acos(min(max(r["ct"], mp.mpf(-1)), mp.mpf(1)))
            if r["st"] < 0:
                theta = 2 * mp.pi - theta
            print(f"    theta={float(theta):8.5f} rad  v_{r['anchor']} -> v_{r['target']}  "
                  f"coverage = {r['coverage']}/{n} ({r['coverage']/n:.2%})")
        if len(rots) > 10:
            print(f"    ... and {len(rots) - 10} more")
        print()

    out = {
        "experiment": "e1j_approximate_symmetry",
        "graph_tag": tag,
        "n_vertices": n,
        "min_coverage_frac": args.min_frac,
        "results": {
            str(p_idx): [
                {"ct": mp.nstr(r["ct"], 30), "st": mp.nstr(r["st"], 30),
                 "anchor": r["anchor"], "target": r["target"],
                 "coverage": r["coverage"]}
                for r in rots
            ]
            for p_idx, rots in all_results.items()
        },
    }
    out_path = CACHE / f"e1j_{tag}_approx_symmetry.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
