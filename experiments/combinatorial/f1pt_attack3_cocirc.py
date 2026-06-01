r"""F1 pressure-test, Attack 3 part A: maximum cocircular-at-radius-1 subset of P_510.

This quantifies the RIGID-orbit concentration ceiling. In a whole-graph rigid
orbit, H_1's coords are fixed P_510. A hub v in H_2 receiving k bridges from
U_v subset V(H_1) requires U_v to lie on a unit circle (cocircular at radius 1).
So the maximum bridge-degree any single hub can have, using P_510's fixed points
as bridge sources, is the maximum number of P_510 points on a common unit circle.

We compute this with float prefilter + exact sympy confirmation of the witness.
"""
from __future__ import annotations
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from f1pt_lib import load_p510, num_coords, CACHE

def main():
    base, edges = load_p510()
    nc = num_coords(base, dps=30)
    P = np.array([[float(x), float(y)] for (x, y) in nc])
    n = len(P)

    # Enumerate candidate unit-circle centers from every close pair (d<2).
    # Each such pair lies on exactly 2 unit circles; collect their centers.
    centers = []
    src_pairs = []
    for i in range(n):
        di = P - P[i]
        d2 = (di[:, 0]**2 + di[:, 1]**2)
        for j in range(i+1, n):
            dd2 = d2[j]
            if dd2 >= 4.0 or dd2 <= 1e-18:
                continue
            d = np.sqrt(dd2)
            mid = (P[i] + P[j]) / 2.0
            h = np.sqrt(max(0.0, 1.0 - dd2/4.0))
            perp = np.array([-(P[j,1]-P[i,1]), (P[j,0]-P[i,0])]) / d
            centers.append(mid + h*perp)
            centers.append(mid - h*perp)
    centers = np.array(centers)
    print(f"candidate centers: {len(centers)}")

    # For each center, count P_510 points at distance ~1 (vectorized).
    best = 0
    best_center = None
    best_members = None
    # batch to control memory
    B = 4000
    for s in range(0, len(centers), B):
        chunk = centers[s:s+B]
        # dist from each center to each point
        # shape (chunk, n)
        diff = chunk[:, None, :] - P[None, :, :]
        dist = np.sqrt((diff**2).sum(axis=2))
        onunit = np.abs(dist - 1.0) < 1e-7
        counts = onunit.sum(axis=1)
        mi = counts.argmax()
        if counts[mi] > best:
            best = int(counts[mi])
            best_center = chunk[mi].tolist()
            best_members = np.where(onunit[mi])[0].tolist()
    print(f"MAX P_510 points on a common unit circle (float, 1e-7): {best}")
    print(f"  center ~ {best_center}")
    print(f"  members ({len(best_members)}): {best_members}")

    # Histogram of how many circles achieve high counts
    out = {
        "max_cocircular_unit_subset": best,
        "best_center_float": best_center,
        "best_members": best_members,
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "f1pt_attack3_cocirc.json").write_text(json.dumps(out, indent=2))
    print("saved", CACHE / "f1pt_attack3_cocirc.json")

if __name__ == "__main__":
    main()
