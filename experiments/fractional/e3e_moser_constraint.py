r"""e3e: OFV-style LP with Moser-spindle inequality on top of OFV triangles.

Architecture 3 / continuous side. Sits on top of e3c and e3d.

Motivation. e3d showed the unit-edge equilateral triangle constraint is
saturating: wide enumeration over (a, b) on a 0.1 grid yields 1409 candidate
triples but the LP optimum stays at $m_1 \leq 0.2682$ vs OFV's 0.2684.
Closing the gap to KMOR 2015's 0.2588 or Ambrus 2023's 0.2470 requires
*larger* finite UDG configurations as the source of inequalities.

The natural next configuration is the Moser spindle: 7 vertices, 11
unit-distance edges, $\chi = 4$, $\alpha = 2$. The OFV-style constraint
generalizes from a unit-edge triangle ($\alpha = 1$, $N = 3$, giving
$\sum f(\|v_i\|) \leq 1$) to any finite UDG $G$ with independence number
$\alpha(G)$:

  $\sum_{i=1}^{N} f(\|v_i\|) \leq \alpha(G)$

(A measurable distance-1-avoiding set $A$ contains at most $\alpha(G)$ of
any translate of $G$, since the configuration must be independent in $A$'s
unit-distance subgraph.)

For the Moser spindle: $\sum_{i=1}^{7} f(\|v_i\|) \leq 2$. The dual
multiplier $z_M \geq 0$ contributes $2 z_M$ to the objective and $7 z_M$
to the $t = 0$ constraint, with the $t > 0$ constraint adding
$z_M \cdot \sum_i \Omega_n(t \|v_i\|)$.

We sweep over translations of the Moser spindle (each translation gives a
different set of radii $\|v_i\|$ and hence a different constraint). Combined
with OFV's 3 triangle triples, this yields a richer LP.

Coordinates. The Moser spindle vertices (from
[experiments/_shared/unit_distance_graph.py](../_shared/unit_distance_graph.py))
live in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$. We use float coordinates here.
"""

from __future__ import annotations

import json
import math
import pathlib
import time

import cvxpy as cp
import numpy as np

from experiments.fractional.e3c_ofv_lp_dual import (
    omega_n, chi_m_integer, CACHE, OFV_N2_TRIPLES_SQUARED,
)


def moser_spindle_vertices() -> np.ndarray:
    """Moser spindle vertices in R^2 as a (7, 2) float array.

    Construction: two rhombi of unit edges (each with one unit short diagonal),
    sharing vertex A, with the second rhombus rotated by angle theta = arccos(5/6)
    so the outer tips D and D' lie at unit distance.
    """
    sqrt3 = math.sqrt(3.0)
    A = (0.0, 0.0)
    B = (1.0, 0.0)
    C = (0.5, sqrt3 / 2.0)
    D = (1.5, sqrt3 / 2.0)
    cos_t = 5.0 / 6.0
    sin_t = math.sqrt(11.0) / 6.0    # sqrt(1 - 25/36) = sqrt(11)/6

    def rot(p):
        return (cos_t * p[0] - sin_t * p[1], sin_t * p[0] + cos_t * p[1])

    Bp = rot(B)
    Cp = rot(C)
    Dp = rot(D)
    return np.array([A, B, C, D, Bp, Cp, Dp])


def verify_moser_spindle_edges(V: np.ndarray, tol: float = 1e-9) -> tuple[int, list]:
    """Sanity-check: count unit-distance edges among the 7 vertices, return list."""
    edges = []
    n = V.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            d = float(np.linalg.norm(V[i] - V[j]))
            if abs(d - 1.0) < tol:
                edges.append((i, j))
    return len(edges), edges


def build_LP(
    triples: list[tuple[float, float, float]],
    moser_centers: list[tuple[float, float]],
    n: int = 2,
    t_max: float = 50.0,
    n_grid: int = 20000,
) -> dict:
    """LP with OFV triangle inequalities plus Moser-spindle inequalities at
    multiple translations.

    Each `triples` entry adds one z_c >= 0 multiplier (triangle, alpha=1, N=3).
    Each `moser_centers` entry adds one z_M >= 0 multiplier (Moser, alpha=2, N=7),
    where the center is the offset (cx, cy); the Moser vertices are translated
    by -center so the resulting radii are ||v_i - center||.
    """
    t_grid = np.linspace(t_max / n_grid, t_max, n_grid)
    omega_t = omega_n(t_grid, n)
    n_plus_1 = n + 1    # 3 for triangles
    moser_N = 7
    moser_alpha = 2

    # Build per-constraint coefficient arrays.
    triple_omega = []    # one per triple: sum_i Omega(t * sqrt(squared))
    for (a, b, c) in triples:
        rs = [math.sqrt(a), math.sqrt(b), math.sqrt(c)]
        triple_omega.append(sum(omega_n(t_grid * r, n) for r in rs))

    V = moser_spindle_vertices()
    moser_omega = []
    moser_radii = []
    for (cx, cy) in moser_centers:
        rs = [float(np.linalg.norm(V[i] - np.array([cx, cy]))) for i in range(moser_N)]
        moser_radii.append(rs)
        moser_omega.append(sum(omega_n(t_grid * r, n) for r in rs))

    K_t = len(triples)
    K_m = len(moser_centers)
    z0 = cp.Variable()
    z1 = cp.Variable()
    zc_t = cp.Variable(K_t, nonneg=True) if K_t > 0 else None
    zc_m = cp.Variable(K_m, nonneg=True) if K_m > 0 else None

    # t > 0 constraint and t = 0 constraint.
    grid_expr = z0 + z1 * omega_t
    t0_expr = z0 + z1
    objective = z0
    if K_t > 0:
        T = np.stack(triple_omega)   # (K_t, n_grid)
        grid_expr = grid_expr + zc_t @ T
        t0_expr = t0_expr + n_plus_1 * cp.sum(zc_t)    # each triangle has N=3 at t=0
        objective = objective + cp.sum(zc_t)            # each triangle has alpha=1
    if K_m > 0:
        M = np.stack(moser_omega)    # (K_m, n_grid)
        grid_expr = grid_expr + zc_m @ M
        t0_expr = t0_expr + moser_N * cp.sum(zc_m)      # each Moser has N=7 at t=0
        objective = objective + moser_alpha * cp.sum(zc_m)    # each Moser has alpha=2

    constraints = [grid_expr >= 0, t0_expr >= 1]
    prob = cp.Problem(cp.Minimize(objective), constraints)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0

    result = {
        "status": prob.status,
        "z0": float(z0.value),
        "z1": float(z1.value),
        "m1_bound": float(prob.value),
        "solve_time_s": elapsed,
        "K_t": K_t,
        "K_m": K_m,
    }
    if K_t > 0:
        active_t = [(triples[k], float(zc_t.value[k])) for k in range(K_t)
                    if zc_t.value[k] > 1e-6]
        result["active_triangles"] = active_t
    if K_m > 0:
        active_m = [(moser_centers[k], moser_radii[k], float(zc_m.value[k]))
                    for k in range(K_m) if zc_m.value[k] > 1e-6]
        result["active_moser"] = active_m
    return result


def main():
    print("e3e: OFV LP with Moser-spindle inequality (N=7, alpha=2)")
    print("Built atop OFV 2010 (3 triangles giving 0.268412).\n")

    V = moser_spindle_vertices()
    n_edges, edges = verify_moser_spindle_edges(V)
    print(f"Moser spindle vertices verified: {V.shape[0]} vertices, {n_edges} unit-distance edges")
    print(f"  expected 11; got {n_edges}.  edges: {edges[:11]}\n")
    assert n_edges == 11, f"Moser spindle: expected 11 unit-distance edges, got {n_edges}"

    # Baseline: OFV 3 triples only.
    baseline = build_LP(triples=OFV_N2_TRIPLES_SQUARED, moser_centers=[])
    print(f"Baseline (OFV 3 triangles):  m_1 <= {baseline['m1_bound']:.6f}  "
          f"chi_m >= {chi_m_integer(baseline['m1_bound'])}")

    # Single Moser at centroid.
    centroid = tuple(V.mean(axis=0))
    print(f"\nMoser spindle centroid: ({centroid[0]:.4f}, {centroid[1]:.4f})")

    # Try a sweep over Moser centers.
    print(f"\nSweep of Moser-center positions:")
    print(f"  {'center':>22}  {'m_1':>10}  {'chi_m':>8}  {'active_M':>9}  {'active_T':>9}")
    print(f"  {'-'*22}  {'-'*10}  {'-'*8}  {'-'*9}  {'-'*9}")

    # Grid of centers near origin and the Moser body.
    candidates = []
    candidates.append(centroid)                    # geometric centroid
    candidates.append((0.0, 0.0))                  # vertex A
    candidates.append(tuple(V[0]))                 # vertex A (same as above; keep)
    candidates.append(tuple(V[3]))                 # vertex D
    candidates.append(tuple(V[6]))                 # vertex D'
    # Add a small grid of off-vertex centers.
    for cx in np.linspace(-0.5, 2.0, 11):
        for cy in np.linspace(-0.5, 1.5, 9):
            candidates.append((float(cx), float(cy)))

    best = baseline.copy()
    best["center"] = None
    for c in candidates:
        r = build_LP(triples=OFV_N2_TRIPLES_SQUARED, moser_centers=[c])
        nm_active = len(r.get("active_moser", []))
        nt_active = len(r.get("active_triangles", []))
        if r["m1_bound"] < best["m1_bound"] - 1e-9:
            best = r.copy()
            best["center"] = c
            print(f"  ({c[0]:+.3f}, {c[1]:+.3f})  {r['m1_bound']:10.6f}  "
                  f"{1/r['m1_bound']:8.4f}  {nm_active:9d}  {nt_active:9d}   <-- improved")
        # else: not printed (would clutter)

    print()
    if best["center"] is not None:
        print(f"Best single Moser center: ({best['center'][0]:+.4f}, {best['center'][1]:+.4f})")
        print(f"  m_1 = {best['m1_bound']:.6f}  vs baseline 0.268412")
    else:
        print("No Moser center improved over baseline.")

    # Try combining best center with a few neighbors.
    if best["center"] is not None:
        print(f"\nCombining the best Moser center with neighboring offsets...")
        centers_combo = [best["center"]]
        cx0, cy0 = best["center"]
        for dx in [-0.2, -0.1, 0.0, 0.1, 0.2]:
            for dy in [-0.2, -0.1, 0.0, 0.1, 0.2]:
                if dx == 0 and dy == 0:
                    continue
                centers_combo.append((cx0 + dx, cy0 + dy))
        combo = build_LP(triples=OFV_N2_TRIPLES_SQUARED, moser_centers=centers_combo)
        n_active = len(combo.get("active_moser", []))
        print(f"  {len(centers_combo)} centers (best + 24 neighbors): "
              f"m_1 = {combo['m1_bound']:.6f}, {n_active} active")

        # Sweep wider, denser.
        print(f"\nDense sweep around best center (0.05 grid, radius 0.5):")
        centers_dense = []
        for cx in np.arange(cx0 - 0.5, cx0 + 0.5 + 1e-9, 0.05):
            for cy in np.arange(cy0 - 0.5, cy0 + 0.5 + 1e-9, 0.05):
                centers_dense.append((float(cx), float(cy)))
        dense = build_LP(triples=OFV_N2_TRIPLES_SQUARED, moser_centers=centers_dense)
        n_active_d = len(dense.get("active_moser", []))
        print(f"  {len(centers_dense)} centers: m_1 = {dense['m1_bound']:.6f}, "
              f"{n_active_d} active")

        # Sweep wider region.
        print(f"\nWide sweep (0.1 grid, broad region):")
        centers_wide = []
        for cx in np.arange(-1.0, 3.0 + 1e-9, 0.1):
            for cy in np.arange(-1.0, 2.0 + 1e-9, 0.1):
                centers_wide.append((float(cx), float(cy)))
        wide = build_LP(triples=OFV_N2_TRIPLES_SQUARED, moser_centers=centers_wide)
        n_active_w = len(wide.get("active_moser", []))
        print(f"  {len(centers_wide)} centers: m_1 = {wide['m1_bound']:.6f}, "
              f"{n_active_w} active")

    print()
    print("=" * 78)
    print("Summary:")
    print("=" * 78)
    print(f"  OFV 2010 (3 triangles):       m_1 <= 0.2684  chi_m >= 4   (real >= 3.73)")
    if best["center"] is not None:
        print(f"  e3e (+best Moser):            m_1 <= {best['m1_bound']:.4f}  chi_m >= "
              f"{chi_m_integer(best['m1_bound'])}   (real >= {1/best['m1_bound']:.2f})")
    print(f"  KMOR 2015:                    m_1 <= 0.2588  chi_m >= 4   (real >= 3.86)")
    print(f"  Ambrus et al. 2023:           m_1 <= 0.2470  chi_m >= 5   (real >= 4.05)")

    # Save.
    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3e_moser_constraint.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e3e_moser_constraint",
                "moser_vertices": V.tolist(),
                "moser_n_edges": n_edges,
                "baseline_3_triangles_m1": baseline["m1_bound"],
                "best_single_moser_center": best.get("center"),
                "best_single_moser_m1_bound": best["m1_bound"],
                "best_single_moser_chi_m_integer": chi_m_integer(best["m1_bound"]),
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
