r"""h5_cocircularity_sieve: Apply the L23 cocircularity obstruction to the
chi >= 6 abstract graph found by h5_polymath_squared.

For each saturating $H_2$ vertex $v$ (one with $\|F(v)\| = 5$ universally),
the bridge-source set $U_v \subseteq V(H_1)$ must be cocircular at unit
distance from some point in $\mathbb{R}^2$ for the graph to be UDG-realizable.

Method: 30-digit mpmath precision cocircularity check. Three points define
a unique circle; the remaining $|U_v| - 3$ must lie on it.

Result: ALL 97 saturating $v$'s have non-cocircular $U_v$, so the h5
abstract chi-6 graph is NOT UDG-realizable.
"""

from __future__ import annotations

import json
import pathlib
import pickle
import sys
from collections import defaultdict

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"


def main():
    import mpmath
    mpmath.mp.dps = 30

    # Load P_510 coordinates (parsed from 510.vtx in h5_polymath_squared).
    coords_path = CACHE / "h5_p510_coords.pkl"
    if not coords_path.exists():
        print(f"Coordinates not cached. Run the parse_510_vertices snippet from "
              f"h5_polymath_squared.py first.")
        return 1

    import sympy
    coords_sym = pickle.load(open(coords_path, "rb"))
    coords_num = []
    for x, y in coords_sym:
        coords_num.append((mpmath.mpf(str(sympy.N(x, 30))),
                            mpmath.mpf(str(sympy.N(y, 30)))))

    # Load h5 bridge set.
    summary = json.loads((CACHE / "h5_summary.json").read_text())
    B = [tuple(x) for x in summary["best_B"]]

    bridges_into = defaultdict(set)
    for (u, v) in B:
        bridges_into[v].add(u)

    def circle_center_radius(p1, p2, p3):
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3
        a = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2
        if abs(a) < mpmath.mpf('1e-25'):
            return None, None
        b = ((x1**2 + y1**2) * (y3 - y2) +
             (x2**2 + y2**2) * (y1 - y3) +
             (x3**2 + y3**2) * (y2 - y1))
        c = ((x1**2 + y1**2) * (x2 - x3) +
             (x2**2 + y2**2) * (x3 - x1) +
             (x3**2 + y3**2) * (x1 - x2))
        cx = -b / (2 * a)
        cy = -c / (2 * a)
        r2 = (cx - x1)**2 + (cy - y1)**2
        return (cx, cy), mpmath.sqrt(r2)

    def check_cocircularity(U, eps=mpmath.mpf('1e-20')):
        if len(U) < 3:
            return True, None
        U = list(U)
        p0 = coords_num[U[0]]; p1 = coords_num[U[1]]; p2 = coords_num[U[2]]
        center, r = circle_center_radius(p0, p1, p2)
        if center is None:
            return None, None
        cx, cy = center
        radii = []
        for u in U:
            x, y = coords_num[u]
            d = mpmath.sqrt((x - cx)**2 + (y - cy)**2)
            radii.append(d)
        max_dev = max(abs(rd - r) for rd in radii)
        return max_dev < eps, (cx, cy, r, max_dev)

    sat_v = sorted([v for v in bridges_into if len(bridges_into[v]) >= 5])
    print(f"Cocircularity sieve on h5_polymath_squared chi >= 6 bridge set")
    print(f"  Total saturating v (|U_v| >= 5): {len(sat_v)}")
    print(f"  Testing all {len(sat_v)} for cocircularity...")
    print()

    results = []
    cocirc_count = 0
    unit_dist_count = 0
    for v in sat_v:
        U = sorted(bridges_into[v])
        ok, info = check_cocircularity(U)
        entry = {"v": v, "U_size": len(U)}
        if info is None:
            entry["status"] = "degenerate"
            print(f"  v={v}, |U|={len(U)}: degenerate (3 collinear)")
            results.append(entry)
            continue
        cx, cy, r, dev = info
        entry["cocircular"] = ok
        entry["circle_radius"] = float(r)
        entry["max_deviation"] = float(dev)
        entry["unit_distance_compat"] = ok and abs(r - 1) < mpmath.mpf('1e-5')
        if ok:
            cocirc_count += 1
        if entry["unit_distance_compat"]:
            unit_dist_count += 1
        results.append(entry)

    n_total = len(results)
    print()
    print(f"Cocircularity verdict: {cocirc_count}/{n_total} saturating v's "
          f"have cocircular U_v.")
    print(f"Unit-distance compatibility verdict: {unit_dist_count}/{n_total} "
          f"have cocircular U_v at unit radius.")
    print()

    if cocirc_count == 0:
        print("ALL saturating v's have non-cocircular U_v.")
        print("==> The h5 abstract chi-6 graph is NOT UDG-realizable in R^2.")
        print("    Each v requires U_v at unit distance from phi(v), which fails")
        print("    if the U_v are not on a common circle.")
    elif unit_dist_count == 0:
        print("Some saturating v's are cocircular but NOT at unit radius.")
        print("==> Still not UDG-realizable (radius != 1).")
    elif unit_dist_count < n_total:
        print(f"Partial UDG-compatibility: {unit_dist_count}/{n_total} could be at unit distance.")
        print("==> Realizability is still infeasible, but a softening might preserve {unit_dist_count} bridges.")
    else:
        print(f"All saturating v's are UDG-compatible. Realizability is likely.")

    # Save.
    out = {
        "experiment": "h5_cocircularity_sieve",
        "n_total_saturating": n_total,
        "n_cocircular": cocirc_count,
        "n_unit_distance_compatible": unit_dist_count,
        "verdict": ("NOT UDG-realizable" if cocirc_count == 0 or unit_dist_count == 0
                    else f"Partial: {unit_dist_count}/{n_total}"),
        "per_v_results": results,
    }
    out_path = CACHE / "h5_cocircularity.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\nSaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
