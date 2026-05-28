r"""h6_mixed_cocirc: ADVERSARY cocircularity sieve for an h6_mixed_halves chi>=6 graph.

For each H_2 vertex v with a large bridge-source set U_v subseteq V(H_1), UDG
realizability requires U_v to lie on a common circle of unit radius centered at
phi(v) in R^2. We test cocircularity of U_v using the H_1-side exact
coordinates at 30-digit mpmath precision.

For tag 510x553 the source half H_1 = 510, whose coordinates are cached in
h5_p510_coords.pkl. For other H_1 tags we parse sources/cnp-sat/vtx/<tag>.vtx.

Usage: python h6_mixed_cocirc.py --tag 510x553
"""

from __future__ import annotations

import argparse
import json
import pathlib
import pickle
import sys
from collections import defaultdict

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
VTX_DIR = REPO_ROOT / "sources" / "cnp-sat" / "vtx"


def parse_vtx(path, sympy):
    """Parse a Mathematica-style .vtx file: lines like {x, y} with Sqrt[...]."""
    coords = []
    txt = path.read_text(encoding="utf-8")
    for line in txt.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        inner = line.strip("{}").strip()
        # split on the top-level comma
        depth = 0
        comma = -1
        for i, ch in enumerate(inner):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
            elif ch == "," and depth == 0:
                comma = i
                break
        xs = inner[:comma].strip()
        ys = inner[comma + 1:].strip()

        def conv(s):
            s = s.replace("Sqrt[", "sqrt(").replace("]", ")")
            return sympy.sympify(s, locals={"sqrt": sympy.sqrt})

        coords.append((conv(xs), conv(ys)))
    return coords


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    h1_tag = args.tag.split("x")[0]

    import mpmath
    import sympy
    mpmath.mp.dps = 30

    g = json.loads((CACHE / f"h6mix_{args.tag}_graph.json").read_text())
    B = [tuple(x) for x in g["B"]]
    N1 = g["N1"]

    # Load H_1 coordinates.
    if h1_tag == "510" and (CACHE / "h5_p510_coords.pkl").exists():
        coords_sym = pickle.load(open(CACHE / "h5_p510_coords.pkl", "rb"))
        print("Loaded H_1=510 coords from h5_p510_coords.pkl", flush=True)
    else:
        coords_sym = parse_vtx(VTX_DIR / f"{h1_tag}.vtx", sympy)
        print(f"Parsed H_1={h1_tag} coords from {h1_tag}.vtx", flush=True)
    assert len(coords_sym) >= N1, f"coords {len(coords_sym)} < N1 {N1}"
    coords_num = [(mpmath.mpf(str(sympy.N(x, 30))), mpmath.mpf(str(sympy.N(y, 30))))
                  for (x, y) in coords_sym[:N1]]

    bridges_into = defaultdict(set)
    for (u, v) in B:
        bridges_into[v].add(u)

    def circle(p1, p2, p3):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3
        a = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2
        if abs(a) < mpmath.mpf("1e-25"):
            return None
        b = ((x1**2 + y1**2) * (y3 - y2) + (x2**2 + y2**2) * (y1 - y3)
             + (x3**2 + y3**2) * (y2 - y1))
        c = ((x1**2 + y1**2) * (x2 - x3) + (x2**2 + y2**2) * (x3 - x1)
             + (x3**2 + y3**2) * (x1 - x2))
        cx = -b / (2 * a); cy = -c / (2 * a)
        r = mpmath.sqrt((cx - x1)**2 + (cy - y1)**2)
        return cx, cy, r

    def check(U, eps=mpmath.mpf("1e-20")):
        U = list(U)
        if len(U) < 3:
            return True, None
        res = circle(coords_num[U[0]], coords_num[U[1]], coords_num[U[2]])
        if res is None:
            return None, None
        cx, cy, r = res
        dev = max(abs(mpmath.sqrt((coords_num[u][0] - cx)**2
                                  + (coords_num[u][1] - cy)**2) - r) for u in U)
        return dev < eps, (cx, cy, r, dev)

    sat_v = sorted([v for v in bridges_into if len(bridges_into[v]) >= 5])
    print(f"h6 mixed cocircularity sieve [{args.tag}]", flush=True)
    print(f"  saturating v (|U_v|>=5): {len(sat_v)}", flush=True)

    results = []
    cocirc = 0
    unit = 0
    degenerate = 0
    for v in sat_v:
        U = sorted(bridges_into[v])
        ok, info = check(U)
        if info is None:
            degenerate += 1
            results.append({"v": v, "U_size": len(U), "status": "degenerate"})
            continue
        cx, cy, r, dev = info
        ud = bool(ok) and abs(r - 1) < mpmath.mpf("1e-5")
        if ok:
            cocirc += 1
        if ud:
            unit += 1
        results.append({"v": v, "U_size": len(U), "cocircular": bool(ok),
                        "circle_radius": float(r), "max_deviation": float(dev),
                        "unit_distance_compat": ud})

    n = len(sat_v)
    print(f"  cocircular U_v: {cocirc}/{n}", flush=True)
    print(f"  cocircular AND unit-radius: {unit}/{n}", flush=True)
    print(f"  degenerate (collinear triple): {degenerate}/{n}", flush=True)
    if unit == 0:
        verdict = "NOT UDG-realizable"
        print("  ==> NOT UDG-realizable (no saturating v has cocircular unit-radius U_v)",
              flush=True)
    elif unit < n:
        verdict = f"Partial: {unit}/{n} unit-compatible"
        print(f"  ==> {verdict}; still infeasible as a whole", flush=True)
    else:
        verdict = "Possibly UDG-realizable"
        print("  ==> all saturating v UDG-compatible; realizability plausible", flush=True)

    out = {"experiment": "h6_mixed_cocirc", "tag": args.tag,
           "n_saturating": n, "n_cocircular": cocirc,
           "n_unit_distance_compatible": unit, "n_degenerate": degenerate,
           "verdict": verdict, "per_v": results}
    (CACHE / f"h6mix_{args.tag}_cocirc.json").write_text(json.dumps(out, indent=2, default=str))
    print(f"Saved h6mix_{args.tag}_cocirc.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
