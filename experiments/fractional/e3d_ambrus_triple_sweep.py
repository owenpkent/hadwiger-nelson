r"""e3d: extend OFV multi-simplex LP via wide enumeration of valid triples.

Architecture 3 / continuous side. Sits on top of e3c
(OFV 2010 multi-simplex LP, $m_1(\mathbb{R}^2) \leq 0.268412$ with 3 hand-picked triples).

Strategy. OFV section 3.1 chose three (a, b, c) triples by enumerating
$a, b \in \{0, 0.1, \ldots, 4.0\}$ and selecting the 3 that best improved
the LP. Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023
([arXiv:2207.14179](https://arxiv.org/abs/2207.14179)) extended this idea to a
23-point configuration plus a beam search, reaching $m_1 \leq 0.2470$ (which
would give integer $\chi_m \geq 5$).

This experiment is an honest middle ground. Rather than implementing the
specific 23-point Ambrus configuration, we (a) reproduce OFV's enumeration
at a fine grid, (b) feed *all* valid triples into a single LP as candidate
constraints (with $z_{c,k} \geq 0$ multipliers, letting the LP zero out
the useless ones), and (c) report how the bound improves as we sweep grid
density. The bound we obtain is a lower bound on what's achievable; the
gap to $0.2470$ is the "non-triple structure" Ambrus exploit.

Triple geometry. For $(\|v_1\|^2, \|v_2\|^2, \|v_3\|^2) = (a, b, c)$ to be a
unit-edge equilateral triangle in $\mathbb{R}^2$, the Gram matrix

  $G = \begin{pmatrix} a & (a+b-1)/2 & (a+c-1)/2 \\ (a+b-1)/2 & b & (b+c-1)/2 \\ (a+c-1)/2 & (b+c-1)/2 & c \end{pmatrix}$

must be positive-semidefinite of rank $\leq 2$. The rank condition gives

  $c^2 - (a+b+1) c + (a^2 + b^2 + 1 - ab - a - b) = 0$

(OFV's $3(a^2 + b^2 + c^2 + 1) - (a + b + c + 1)^2 = 0$ rearranged), and the
PSD condition gives $4 a b \geq (a + b - 1)^2$ plus $c \geq 0$.

Solver: cvxpy + HiGHS. With $\sim 10^3$ candidate triples and $\sim 10^4$
discretized $t$-constraints, solve time is seconds.
"""

from __future__ import annotations

import json
import math
import pathlib
import time

import cvxpy as cp
import numpy as np

# Import shared utilities from e3c.
from experiments.fractional.e3c_ofv_lp_dual import (
    omega_n, chi_m_integer, CACHE, OFV_N2_TRIPLES_SQUARED
)


def enumerate_triples(
    a_grid: np.ndarray,
    b_grid: np.ndarray,
    c_max: float = 10.0,
    tol: float = 1e-9,
) -> list[tuple[float, float, float]]:
    """Enumerate valid (a, b, c) triples with c a root of the Gram-rank
    polynomial.

    Constraints:
      4 a b >= (a + b - 1)^2     (principal 2x2 minor PSD)
      c >= 0, c <= c_max
      c^2 - (a+b+1) c + (a^2 + b^2 + 1 - a b - a - b) = 0
    """
    triples = []
    seen = set()
    for a in a_grid:
        for b in b_grid:
            if 4 * a * b + tol < (a + b - 1) ** 2:
                continue
            p = -(a + b + 1)
            q = a * a + b * b + 1 - a * b - a - b
            disc = p * p - 4 * q
            if disc < -tol:
                continue
            disc = max(disc, 0.0)
            sq = math.sqrt(disc)
            for c in ((-p - sq) / 2, (-p + sq) / 2):
                if c < -tol or c > c_max:
                    continue
                c = max(c, 0.0)
                # Canonicalize (a, b, c) as sorted, dedup.
                key = tuple(sorted((round(a, 6), round(b, 6), round(c, 6))))
                if key in seen:
                    continue
                seen.add(key)
                triples.append((float(a), float(b), float(c)))
    return triples


def solve_LP_with_candidate_triples(
    triples: list[tuple[float, float, float]],
    n: int = 2,
    t_max: float = 50.0,
    n_grid: int = 20000,
    verbose: bool = False,
) -> dict:
    """LP with multiple simplex inequalities. Each triple gives one z_c >= 0
    multiplier; the LP zeros out useless ones automatically.

    See e3c.solve_multi_simplex_LP. This is the same LP, just with potentially
    much larger K.
    """
    t_grid = np.linspace(t_max / n_grid, t_max, n_grid)
    omega_t = omega_n(t_grid, n)

    K = len(triples)
    z0 = cp.Variable()
    z1 = cp.Variable()
    zc = cp.Variable(K, nonneg=True)
    n_plus_1 = n + 1

    # For each triple compute the sum Omega_n(t r_1) + Omega_n(t r_2) + Omega_n(t r_3).
    triple_omega = np.zeros((K, n_grid))
    for k, (a, b, c) in enumerate(triples):
        rs = [math.sqrt(a), math.sqrt(b), math.sqrt(c)]
        triple_omega[k] = sum(omega_n(t_grid * r, n) for r in rs)

    # Vectorized constraint.
    grid_expr = z0 + z1 * omega_t + zc @ triple_omega
    constraints = [
        grid_expr >= 0,
        z0 + z1 + n_plus_1 * cp.sum(zc) >= 1,
    ]
    prob = cp.Problem(cp.Minimize(z0 + cp.sum(zc)), constraints)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=verbose)
    elapsed = time.time() - t0

    active_idx = [k for k, v in enumerate(zc.value) if v > 1e-6]
    return {
        "K": K,
        "K_active": len(active_idx),
        "status": prob.status,
        "z0": float(z0.value),
        "z1": float(z1.value),
        "m1_bound": float(z0.value + sum(zc.value)),
        "solve_time_s": elapsed,
        "active_triples": [triples[k] for k in active_idx],
        "active_weights": [float(zc.value[k]) for k in active_idx],
    }


def main():
    print("e3d: enrich OFV multi-simplex LP via wide triple enumeration")
    print("(extending OFV 2010 page 7 search; targeting Ambrus 2023 = 0.247)\n")

    # Baseline: OFV's 3 hand-picked triples.
    print("=" * 78)
    print("Baseline (OFV 2010 hand-picked 3 triples):")
    print("=" * 78)
    baseline = solve_LP_with_candidate_triples(OFV_N2_TRIPLES_SQUARED)
    print(f"  m_1     <= {baseline['m1_bound']:.6f}  (published OFV: 0.268412)")
    print(f"  chi_m   >= {1/baseline['m1_bound']:.4f}  (int: {chi_m_integer(baseline['m1_bound'])})")
    print(f"  solve   {baseline['solve_time_s']*1000:.0f} ms\n")

    # Sweep: enumerate triples on increasingly fine grids.
    print("=" * 78)
    print("Wide enumeration (grid_step is increment in a and b over [0.1, 4.0]):")
    print("=" * 78)
    print(f"  {'step':>6}  {'#triples':>9}  {'m_1 bound':>12}  {'chi_m':>8}  "
          f"{'K_active':>8}  {'t(s)':>6}")
    print(f"  {'-'*6}  {'-'*9}  {'-'*12}  {'-'*8}  {'-'*8}  {'-'*6}")

    best = baseline
    best_step = None
    for step in [0.4, 0.2, 0.1, 0.05]:
        grid = np.arange(0.1, 4.0 + 1e-9, step)
        triples = enumerate_triples(grid, grid, c_max=15.0)
        # Always include OFV's 3 to guarantee no regression from baseline.
        all_triples = list({tuple(sorted(t)) for t in triples + OFV_N2_TRIPLES_SQUARED})
        all_triples = [tuple(t) for t in all_triples]
        if len(all_triples) > 2500:
            print(f"  {step:6.2f}  {len(all_triples):9d}  "
                  f"(skipped, too many; LP would be slow)")
            continue
        r = solve_LP_with_candidate_triples(all_triples)
        print(f"  {step:6.2f}  {len(all_triples):9d}  {r['m1_bound']:12.6f}  "
              f"{1/r['m1_bound']:8.4f}  {r['K_active']:8d}  {r['solve_time_s']:6.2f}")
        if r["m1_bound"] < best["m1_bound"]:
            best = r
            best_step = step

    print()
    print("=" * 78)
    print("Best bound from wide enumeration:")
    print("=" * 78)
    print(f"  grid step:      {best_step}")
    print(f"  total triples:  {best['K']}")
    print(f"  active triples: {best['K_active']}  (LP zeroed out the rest)")
    print(f"  m_1 bound:      {best['m1_bound']:.6f}")
    print(f"  chi_m bound:    {1/best['m1_bound']:.6f}  (int: {chi_m_integer(best['m1_bound'])})")
    print()
    print(f"  Active triples and weights:")
    for trip, w in zip(best.get("active_triples", []), best.get("active_weights", [])):
        rs = [math.sqrt(x) for x in trip]
        print(f"    (a, b, c) = ({trip[0]:.4f}, {trip[1]:.4f}, {trip[2]:.4f})  "
              f"radii = ({rs[0]:.4f}, {rs[1]:.4f}, {rs[2]:.4f})  z_c = {w:.6f}")

    print()
    print("=" * 78)
    print("Summary:")
    print("=" * 78)
    print(f"  OFV 2010 published 3 triples:  m_1 <= 0.2684  chi_m >= 4   (real >= 3.73)")
    print(f"  e3d wide enumeration:          m_1 <= {best['m1_bound']:.4f}  chi_m >= "
          f"{chi_m_integer(best['m1_bound'])}   (real >= {1/best['m1_bound']:.2f})")
    print(f"  KMOR 2015 published:           m_1 <= 0.2588  chi_m >= 4   (real >= 3.86)")
    print(f"  Ambrus et al. 2023 published:  m_1 <= 0.2470  chi_m >= 5   (real >= 4.05)")

    # Save.
    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3d_ambrus_triple_sweep.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e3d_ambrus_triple_sweep",
                "baseline_OFV_3_triples": {
                    k: v for k, v in baseline.items()
                    if k not in ("active_triples", "active_weights")
                },
                "best_step": best_step,
                "best": {
                    "K": best["K"],
                    "K_active": best["K_active"],
                    "m1_bound": best["m1_bound"],
                    "chi_m_real": 1 / best["m1_bound"],
                    "chi_m_integer": chi_m_integer(best["m1_bound"]),
                    "active_triples": best.get("active_triples", []),
                    "active_weights": best.get("active_weights", []),
                },
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
