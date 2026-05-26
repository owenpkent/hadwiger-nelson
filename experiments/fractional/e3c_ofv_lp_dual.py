r"""e3c: OFV LP for $m_1(\mathbb{R}^2)$ in the correct dual form, with simplex strengthening.

Architecture 3 / continuous side. Reproduces the published OFV 2010 bound
$m_1(\mathbb{R}^2) \leq 0.268412$, improving the basic 0.2873 of e3b.

Setup follows Oliveira Filho-Vallentin 2010 (arXiv:0808.1822), Theorem 1.1
plus the simplex strengthening of section 3.1.

Theorem 1.1 (one forbidden distance $d_1 = 1$, dimension $n$):
Let $A \subseteq \mathbb{R}^n$ be measurable, avoiding distance $1$. If
$z_0, z_1 \in \mathbb{R}$ satisfy

  $z_0 + z_1 \geq 1$
  $z_0 + z_1 \Omega_n(t) \geq 0$ for all $t \geq 0$

then the upper density of $A$ is at most $z_0$. Here
$\Omega_n(t) = \Gamma(n/2) (2/t)^{(n-2)/2} J_{(n-2)/2}(t)$, with
$\Omega_2(t) = J_0(t)$.

Analytic optimum of the basic LP at $n = 2$: $z_0 = J_0(j_{1,1}) / (J_0(j_{1,1}) - 1)$
where $j_{1,1} \approx 3.8317$ is the first positive zero of $J_1$ and equivalently
the location of the absolute minimum of $J_0$, $J_0(j_{1,1}) \approx -0.4028$.
So $z_0^{\rm basic} = 0.4028 / 1.4028 \approx 0.2873$. This matches e3b.

Strengthened LP (Section 3.1). A regular simplex with edge length $1$ in $\mathbb{R}^n$
has $n+1$ vertices; if centered at the origin each vertex lies at distance
$\sqrt{1/2 - 1/(2n+2)}$ from the origin. Since $A$ avoids distance $1$, it
contains at most one vertex of any unit-edge simplex, which gives the extra
inequality

  $(n+1) f(\sqrt{1/2 - 1/(2n+2)}) \leq 1$

on the radial autocorrelation $f$ of $1_A$. This dualizes into the LP

  $\min z_0 + z_c$
  s.t. $z_c \geq 0$
       $z_0 + z_1 + (n+1) z_c \geq 1$
       $z_0 + z_1 \Omega_n(t) + (n+1) z_c \Omega_n(t \sqrt{1/2 - 1/(2n+2)}) \geq 0$ for all $t \geq 0$

with the bound becoming $m_1(\mathbb{R}^n) \leq z_0 + z_c$.

At $n = 2$ the simplex is an equilateral triangle, $(n+1) = 3$, and the
center-to-vertex radius is $\sqrt{1/2 - 1/6} = 1/\sqrt{3}$. The published
bound is $m_1(\mathbb{R}^2) \leq 0.268412$ (OFV Table 3.1).

Cross-architecture. $\chi_m(\mathbb{R}^2) \geq 1/m_1$, so 0.2688 gives
integer bound $\chi_m \geq 4$ (real-valued $\geq 3.724$). To reach
$\chi_m \geq 5$ via this route requires $m_1 < 1/5 = 0.2000$, which no
published method has reached. KMOR 2015 gets 0.2588 (adds more inequalities),
Ambrus et al. 2023 gets 0.2470 (23-point configuration + beam search).

Solver: cvxpy + HiGHS (LP, 3 variables + ~10k discretized t-constraints, fast).

Wrong-approach detector. The OFV LP is dimension-aware via $\Omega_n$; the
optimal $z_0$ depends on which Bessel function is used. At $n = 1$,
$\Omega_1(t) = \cos(t)$, and the basic LP gives $z_0 = \cos(\pi)/(\cos(\pi)-1) = -1/-2 = 1/2$,
i.e., $m_1(\mathbb{R}) \leq 1/2$, hence $\chi_m(\mathbb{R}) \geq 2$.
This is correct (the optimal coloring is alternating half-open intervals
of length $1/2$). The detector engages.
"""

from __future__ import annotations

import json
import pathlib
import time

import cvxpy as cp
import numpy as np
from scipy.special import j0, jv, jn_zeros, gamma

CACHE = pathlib.Path(__file__).parent / "_cache"


def chi_m_integer(m1_bound: float, tol: float = 1e-6) -> int:
    """Integer lower bound on chi_m from m_1 upper bound, tolerance-aware.

    chi_m >= 1/m_1 ceil-style, but the LP returns m_1 with solver tolerance
    around 1e-9, so 1/m_1 may sit microscopically above an integer (e.g.,
    2.0000000002 from a m_1 == 0.5 problem). Snap to the integer when within
    `tol` of it before applying ceil.
    """
    inv = 1.0 / m1_bound
    rounded = round(inv)
    if abs(inv - rounded) <= tol:
        return int(rounded)
    return int(np.ceil(inv))


def omega_n(t: np.ndarray, n: int) -> np.ndarray:
    """Spherical-average function $\\Omega_n(t)$ from OFV (eq. 1).

    $\\Omega_n(t) = \\Gamma(n/2) (2/t)^{(n-2)/2} J_{(n-2)/2}(t)$ for $t > 0$,
    with $\\Omega_n(0) = 1$.

    For $n = 1$: $\\Omega_1(t) = \\cos(t)$ (using $J_{-1/2}(t) = \\sqrt{2/(\\pi t)} \\cos t$).
    For $n = 2$: $\\Omega_2(t) = J_0(t)$.
    For $n = 3$: $\\Omega_3(t) = \\sin(t)/t$.
    """
    t = np.atleast_1d(np.asarray(t, dtype=float))
    out = np.empty_like(t)
    zero_mask = t == 0.0
    out[zero_mask] = 1.0
    nz = ~zero_mask
    tnz = t[nz]
    nu = (n - 2) / 2.0
    if n == 2:
        out[nz] = j0(tnz)
    elif n == 1:
        out[nz] = np.cos(tnz)
    elif n == 3:
        out[nz] = np.sin(tnz) / tnz
    else:
        out[nz] = gamma(n / 2.0) * (2.0 / tnz) ** nu * jv(nu, tnz)
    return out


def solve_basic_LP(n: int, t_max: float = 50.0, n_grid: int = 20000) -> dict:
    """Basic OFV LP (Theorem 1.1, no simplex).

    min z_0
    s.t. z_0 + z_1 >= 1
         z_0 + z_1 * Omega_n(t) >= 0 for all t in (0, t_max] (discretized)
         (z_0, z_1 free)

    Returns m_1 bound and dual variables.
    """
    t_grid = np.linspace(t_max / n_grid, t_max, n_grid)
    omega_vals = omega_n(t_grid, n)

    z0 = cp.Variable()
    z1 = cp.Variable()
    constraints = [
        z0 + z1 >= 1,
        z0 + z1 * omega_vals >= 0,    # vectorized: 1 constraint per t-grid pt
    ]
    prob = cp.Problem(cp.Minimize(z0), constraints)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0
    return {
        "name": f"basic_LP_n{n}",
        "n": n,
        "status": prob.status,
        "z0": float(z0.value),
        "z1": float(z1.value),
        "m1_bound": float(z0.value),
        "solve_time_s": elapsed,
        "t_max": t_max,
        "n_grid": n_grid,
    }


def solve_simplex_LP(n: int, t_max: float = 50.0, n_grid: int = 20000) -> dict:
    """OFV LP with regular-simplex strengthening (Section 3.1).

    min z_0 + z_c
    s.t. z_c >= 0
         z_0 + z_1 + (n+1) z_c >= 1
         z_0 + z_1 Omega_n(t) + (n+1) z_c Omega_n(t * sqrt(1/2 - 1/(2n+2))) >= 0
              for all t in (0, t_max]
         (z_0, z_1 free; z_c >= 0)

    Returns m_1 bound = z_0 + z_c and dual variables.
    """
    t_grid = np.linspace(t_max / n_grid, t_max, n_grid)
    omega_vals = omega_n(t_grid, n)

    r_simplex = np.sqrt(0.5 - 1.0 / (2 * n + 2))    # 1/sqrt(3) for n = 2
    omega_simplex_vals = omega_n(t_grid * r_simplex, n)
    n_plus_1 = n + 1

    z0 = cp.Variable()
    z1 = cp.Variable()
    zc = cp.Variable(nonneg=True)
    constraints = [
        z0 + z1 + n_plus_1 * zc >= 1,
        z0 + z1 * omega_vals + n_plus_1 * zc * omega_simplex_vals >= 0,
    ]
    prob = cp.Problem(cp.Minimize(z0 + zc), constraints)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0
    return {
        "name": f"simplex_LP_n{n}",
        "n": n,
        "status": prob.status,
        "z0": float(z0.value),
        "z1": float(z1.value),
        "zc": float(zc.value),
        "r_simplex": float(r_simplex),
        "m1_bound": float(z0.value + zc.value),
        "solve_time_s": elapsed,
        "t_max": t_max,
        "n_grid": n_grid,
    }


# OFV 2010 page 7: three off-center triples (||v_1||^2, ||v_2||^2, ||v_3||^2)
# for the unit-edge equilateral triangle in R^2. The third coordinate is the
# root of 3(a^2 + b^2 + c^2 + 1) - (a+b+c+1)^2 = 0 that makes the Gram matrix
# of (v_1, v_2, v_3) singular (rank 2, so the triangle fits in the plane).
OFV_N2_TRIPLES_SQUARED = [
    (2.4, 2.4, 0.360314),
    (3.1, 3.1, 6.524038),
    (3.7, 3.7, 7.417141),
]


def solve_multi_simplex_LP(
    n: int,
    triples_squared: list[tuple[float, float, float]],
    t_max: float = 50.0,
    n_grid: int = 20000,
    include_centered: bool = False,
) -> dict:
    """OFV LP strengthened with multiple unit-edge simplex inequalities.

    For each triple (a_k, b_k, c_k) of squared vertex norms, we add the
    constraint f(sqrt(a_k)) + f(sqrt(b_k)) + f(sqrt(c_k)) <= 1, valid for
    any radial autocorrelation f of a measurable distance-1-avoiding set
    (A contains at most one vertex of any unit-edge equilateral triangle).

    Dual LP:
      min z_0 + sum_k z_{c,k}
      s.t. z_{c,k} >= 0 for each k
           z_0 + z_1 + 3 sum_k z_{c,k} >= 1
           z_0 + z_1 Omega_n(t) + sum_k z_{c,k}
               (Omega_n(t sqrt(a_k)) + Omega_n(t sqrt(b_k)) + Omega_n(t sqrt(c_k))) >= 0
               for all t > 0

    If include_centered = True, also add the centered equilateral-triangle
    constraint with vertices at distance 1/sqrt(3) from origin.
    """
    t_grid = np.linspace(t_max / n_grid, t_max, n_grid)
    omega_vals = omega_n(t_grid, n)

    K = len(triples_squared) + (1 if include_centered else 0)
    z0 = cp.Variable()
    z1 = cp.Variable()
    zc = cp.Variable(K, nonneg=True)
    n_plus_1 = n + 1

    triple_omega_at_grid = []
    triple_vertex_radii = []
    for (a, b, c) in triples_squared:
        rs = [float(np.sqrt(a)), float(np.sqrt(b)), float(np.sqrt(c))]
        triple_vertex_radii.append(rs)
        ovals = sum(omega_n(t_grid * r, n) for r in rs)
        triple_omega_at_grid.append(ovals)
    if include_centered:
        r_c = float(np.sqrt(0.5 - 1.0 / (2 * n + 2)))
        triple_vertex_radii.append([r_c] * n_plus_1)
        triple_omega_at_grid.append(n_plus_1 * omega_n(t_grid * r_c, n))

    grid_expr = z0 + z1 * omega_vals + sum(zc[k] * triple_omega_at_grid[k] for k in range(K))
    constraints = [
        grid_expr >= 0,
        z0 + z1 + n_plus_1 * cp.sum(zc) >= 1,
    ]
    prob = cp.Problem(cp.Minimize(z0 + cp.sum(zc)), constraints)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0
    return {
        "name": f"multi_simplex_LP_n{n}_K{K}",
        "n": n,
        "K": K,
        "include_centered": include_centered,
        "triples_squared": triples_squared,
        "triple_vertex_radii": triple_vertex_radii,
        "status": prob.status,
        "z0": float(z0.value),
        "z1": float(z1.value),
        "zc": [float(v) for v in zc.value],
        "m1_bound": float(z0.value + sum(zc.value)),
        "solve_time_s": elapsed,
        "t_max": t_max,
        "n_grid": n_grid,
    }


def main():
    print("OFV LP for m_1(R^n), single forbidden distance, dual formulation")
    print("(Oliveira Filho-Vallentin 2010, arXiv:0808.1822)\n")

    # --- n = 2, the Hadwiger-Nelson target dimension ---
    print("=" * 78)
    print("n = 2 (Hadwiger-Nelson plane)")
    print("=" * 78)

    basic_2 = solve_basic_LP(n=2)
    print(f"\nBasic LP (Theorem 1.1, no simplex):")
    print(f"  z_0     = {basic_2['z0']:.6f}")
    print(f"  z_1     = {basic_2['z1']:.6f}")
    print(f"  m_1     <= {basic_2['m1_bound']:.6f}")
    print(f"  chi_m   >= {1/basic_2['m1_bound']:.4f}   (int: {chi_m_integer(basic_2['m1_bound'])})")
    print(f"  status  = {basic_2['status']},  solve {basic_2['solve_time_s']*1000:.1f} ms")
    print(f"  analytic: J_0(j_{{1,1}})/(J_0(j_{{1,1}}) - 1) = {j0(jn_zeros(1,1)[0]):.6f}/"
          f"({j0(jn_zeros(1,1)[0]):.6f} - 1) = {j0(jn_zeros(1,1)[0])/(j0(jn_zeros(1,1)[0])-1):.6f}")

    simplex_2 = solve_simplex_LP(n=2)
    print(f"\nCentered-simplex LP (Section 3.1, centered equilateral-triangle):")
    print(f"  z_0     = {simplex_2['z0']:.6f}")
    print(f"  z_1     = {simplex_2['z1']:.6f}")
    print(f"  z_c     = {simplex_2['zc']:.6f}")
    print(f"  m_1     <= z_0 + z_c = {simplex_2['m1_bound']:.6f}")
    print(f"  chi_m   >= {1/simplex_2['m1_bound']:.4f}   (int: {chi_m_integer(simplex_2['m1_bound'])})")
    print(f"  status  = {simplex_2['status']},  solve {simplex_2['solve_time_s']*1000:.1f} ms")

    # OFV 2010 page 7: the centered triangle gives only 0.287, but three
    # off-center unit-edge triangles (specific squared-norm triples) give 0.268412.
    multi_2 = solve_multi_simplex_LP(
        n=2, triples_squared=OFV_N2_TRIPLES_SQUARED, include_centered=False
    )
    print(f"\nMulti-simplex LP (OFV section 3.1, three off-center unit triangles):")
    print(f"  triples (||v_i||^2): {OFV_N2_TRIPLES_SQUARED}")
    print(f"  z_0     = {multi_2['z0']:.6f}")
    print(f"  z_1     = {multi_2['z1']:.6f}")
    for k, zk in enumerate(multi_2['zc']):
        rs = multi_2['triple_vertex_radii'][k]
        print(f"  z_c[{k}]  = {zk:.6f}   (vertex radii {[round(r,4) for r in rs]})")
    print(f"  m_1     <= z_0 + sum z_c = {multi_2['m1_bound']:.6f}")
    print(f"  chi_m   >= {1/multi_2['m1_bound']:.4f}   (int: {chi_m_integer(multi_2['m1_bound'])})")
    print(f"  status  = {multi_2['status']},  solve {multi_2['solve_time_s']*1000:.1f} ms")
    print(f"  published OFV Table 3.1 (n=2): 0.268412  (gap: {multi_2['m1_bound'] - 0.268412:+.6f})")

    # --- n = 1, wrong-approach detector ---
    print("\n" + "=" * 78)
    print("n = 1 (R^1 wrong-approach detector)")
    print("=" * 78)

    basic_1 = solve_basic_LP(n=1)
    print(f"\nBasic LP at n=1:")
    print(f"  m_1     <= {basic_1['m1_bound']:.6f}")
    print(f"  chi_m   >= {1/basic_1['m1_bound']:.4f}   (int: {chi_m_integer(basic_1['m1_bound'])})")
    print(f"  expected: chi_m(R^1) = 2 (alternating intervals); the LP should not over-claim")

    # --- comparison table ---
    print("\n" + "=" * 78)
    print("Summary, R^2 lineage")
    print("=" * 78)
    print(f"  e3b vanilla Bessel LP:   m_1 <= 0.2873  chi_m >= 4   (saturated basic LP)")
    print(f"  e3c basic dual LP:       m_1 <= {basic_2['m1_bound']:.4f}  chi_m >= "
          f"{chi_m_integer(basic_2['m1_bound'])}   (recovers e3b)")
    print(f"  e3c centered-simplex:    m_1 <= {simplex_2['m1_bound']:.4f}  chi_m >= "
          f"{chi_m_integer(simplex_2['m1_bound'])}   (Section 3.1 with centered triangle only)")
    print(f"  e3c 3-off-center LP:     m_1 <= {multi_2['m1_bound']:.4f}  chi_m >= "
          f"{chi_m_integer(multi_2['m1_bound'])}   (this experiment, OFV 2010 page 7)")
    print(f"  OFV 2010 published:      m_1 <= 0.2688  chi_m >= 4")
    print(f"  KMOR 2015:               m_1 <= 0.2588  chi_m >= 4")
    print(f"  Ambrus et al. 2023:      m_1 <= 0.2470  chi_m >= 5  (still open)")
    print(f"  required for chi_m >= 6: m_1  < 0.2000")

    # --- save ---
    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3c_ofv_lp.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e3c_ofv_lp_dual",
                "results": [basic_2, simplex_2, multi_2, basic_1],
                "headline": {
                    "basic_LP_R2_m1_bound": basic_2["m1_bound"],
                    "centered_simplex_LP_R2_m1_bound": simplex_2["m1_bound"],
                    "multi_simplex_LP_R2_m1_bound": multi_2["m1_bound"],
                    "multi_simplex_LP_R2_chi_m_lower": 1 / multi_2["m1_bound"],
                    "multi_simplex_LP_R2_chi_m_integer": chi_m_integer(multi_2["m1_bound"]),
                    "published_OFV_R2": 0.268412,
                    "match_to_published_abs_err": abs(multi_2["m1_bound"] - 0.268412),
                },
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
