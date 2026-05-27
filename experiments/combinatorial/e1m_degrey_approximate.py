r"""e1m: Approximate symmetry analysis of de Grey 1585.

Architecture 1, Shot 2. Companion to e1l.

e1l established that de Grey 1585 has ZERO exact rotational symmetries about
any of 9 tested pivots. This is consistent with the Polymath/Heule lineage
(L15): all public chi >= 5 UDGs in the Hadwiger-Nelson literature appear to
have lost their rotational symmetry through SAT-minimization (or were
originally constructed without it).

This experiment looks for *approximate* rotational symmetries about each
pivot: for each candidate rotation R, count |{v in V : R(v) in V}| and
report top-coverage rotations.

If de Grey has approximate symmetry, we'll see it. If not, the structural
conclusion is firm: the public lineage is fully asymmetric.
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


def parse_sage_vertex_file(path):
    text = path.read_text(encoding="utf-8")
    sympy_ctx = {"sqrt": sp.sqrt}
    parsed = sp.sympify(text, locals=sympy_ctx, rational=True)
    return [(row[0], row[1]) for row in parsed]


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


def find_high_coverage_rotations(verts_num, pivot, lookup, min_coverage_frac=0.3, max_per_class=100):
    n = len(verts_num)
    dist_classes = {}
    for i in range(n):
        dx = verts_num[i][0] - pivot[0]
        dy = verts_num[i][1] - pivot[1]
        r2 = dx*dx + dy*dy
        if r2 < mp.mpf("1e-50"):
            continue
        key = mp.nstr(r2, 18)
        dist_classes.setdefault(key, []).append(i)

    # Sort distance classes by size descending; large classes have more potential rotations.
    sorted_classes = sorted(dist_classes.items(), key=lambda kv: -len(kv[1]))
    print(f"    {len(dist_classes)} distance classes from pivot")
    print(f"    largest class sizes: {[len(c[1]) for c in sorted_classes[:5]]}")

    threshold = int(min_coverage_frac * n)
    results = []
    seen_keys = set()
    for class_key, class_verts in sorted_classes:
        if len(class_verts) < 2:
            continue
        # Cap pairs per class.
        anchor_idx = class_verts[0]
        ax = verts_num[anchor_idx][0] - pivot[0]
        ay = verts_num[anchor_idx][1] - pivot[1]
        r2 = ax*ax + ay*ay
        targets = class_verts[:max_per_class]
        for target_idx in targets:
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
                    "ct": ct, "st": st,
                    "anchor": anchor_idx, "target": target_idx,
                    "coverage": cov,
                })
    results.sort(key=lambda r: -r["coverage"])
    return results


def main():
    print("e1m: approximate symmetry analysis of de Grey 1585")
    print("=" * 78)

    sage_path = REPO_ROOT / "sources" / "degrey_1585_vertices.sage"
    print(f"  parsing {sage_path.relative_to(REPO_ROOT)} ...")
    verts_sym = parse_sage_vertex_file(sage_path)
    n = len(verts_sym)
    print(f"    {n} vertices")

    verts_num = vertices_to_numeric(verts_sym, dps=50)
    lookup = build_vertex_lookup(verts_num)

    pivots_to_try = [
        ("origin", (mp.mpf(0), mp.mpf(0))),
        ("v_0=(2,0)", verts_num[0]),
        ("v_2=(7/3,0)", verts_num[2]),
        ("(1,0)", (mp.mpf(1), mp.mpf(0))),
        ("midpt v_0 v_2", ((verts_num[0][0] + verts_num[2][0]) / 2,
                            (verts_num[0][1] + verts_num[2][1]) / 2)),
        ("centroid", (sum(v[0] for v in verts_num) / mp.mpf(n),
                       sum(v[1] for v in verts_num) / mp.mpf(n))),
    ]

    print(f"  reporting rotations with coverage >= {int(0.3 * n)} ({30}%)")
    print()

    all_results = {}
    for (name, pivot) in pivots_to_try:
        print(f"  Pivot '{name}' = ({mp.nstr(pivot[0], 5)}, {mp.nstr(pivot[1], 5)}):")
        t0 = time.time()
        rots = find_high_coverage_rotations(verts_num, pivot, lookup, min_coverage_frac=0.3, max_per_class=200)
        all_results[name] = rots
        dt = time.time() - t0
        print(f"    {len(rots)} high-coverage rotations in {dt:.1f}s")
        for r in rots[:8]:
            theta = mp.acos(min(max(r["ct"], mp.mpf(-1)), mp.mpf(1)))
            if r["st"] < 0:
                theta = 2 * mp.pi - theta
            theta_f = float(theta)
            deg = theta_f / (2 * 3.141592653589793) * 360.0
            print(f"      theta={theta_f:8.5f} rad ({deg:7.3f} deg)  "
                  f"v_{r['anchor']} -> v_{r['target']}  coverage = {r['coverage']}/{n} ({r['coverage']/n:.2%})")
        print()

    out = {
        "experiment": "e1m_degrey_approximate",
        "n_vertices": n,
        "results": {
            name: [
                {"ct": mp.nstr(r["ct"], 30), "st": mp.nstr(r["st"], 30),
                 "anchor": r["anchor"], "target": r["target"],
                 "coverage": r["coverage"]}
                for r in rots[:30]
            ]
            for name, rots in all_results.items()
        },
    }
    out_path = CACHE / "e1m_degrey_approximate.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
