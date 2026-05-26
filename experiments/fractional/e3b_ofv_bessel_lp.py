"""e3b: Oliveira Filho-Vallentin LP for $m_1(\\mathbb{R}^2)$ via Bessel decomposition.

Architecture 3 / continuous side. Replaces the loose vanilla Lovász
theta (e3a, $\\vartheta = 170$, gave $\\chi \\geq 3$ on a 5-chromatic UDG)
with the rotation-invariant LP framework that the OFV / BNOFV / MRVZ
lineage uses.

Math. A radially-symmetric positive-type function on $\\mathbb{R}^2$
has a Hankel decomposition:

    F(r) = \\int_0^\\infty J_0(2 \\pi r s) d\\nu(s)

with $\\nu$ a non-negative measure on $[0, \\infty)$.

For any measurable set $A \\subset \\mathbb{R}^2$ avoiding distance 1, the
upper density satisfies

    \\mu(A) \\leq F(0) / (F(0) - F(1))

provided $F(r) \\geq 0$ for all $r \\geq 0$ and $F(1) \\leq 0$.

The LP: discretize $\\nu$ at $N$ frequencies, parameterize
$F(r) = \\sum_k c_k J_0(2\\pi r s_k)$ with $c_k \\geq 0$. Normalize
$F(0) = 1$ (i.e., $\\sum c_k = 1$). Minimize $F(1)$. Enforce
$F(r) \\geq 0$ on a fine evaluation grid as a finite approximation of
the infinite positivity constraint.

The resulting bound: $m_1(\\mathbb{R}^2) \\leq 1 / (1 - F(1)_{\\min})$.

Published OFV (arXiv:0808.1822, 2010): $m_1(\\mathbb{R}^2) \\leq 0.2688$
with a more elaborate basis. Our simple Bessel-LP should land in the
$\\sim 0.3$ ballpark; matching 0.2688 would require careful choice of
frequencies and possibly Schwartz / Wiener-Hopf refinements.

Cross-architecture: $\\chi_m(\\mathbb{R}^2) \\geq 1/m_1$, so $m_1 \\leq 0.247$
(Ambrus et al. 2023) gives $\\chi_m \\geq 5$ (recovering Falconer). To
push to $\\chi_m \\geq 6$ would require $m_1 \\leq 0.200$, which no
published method has reached (LEARNINGS L4).

Solver: cvxpy + ECOS or SCS.
"""

from __future__ import annotations

import json
import pathlib
import time

import cvxpy as cp
import numpy as np
from scipy.special import j0

CACHE = pathlib.Path(__file__).parent / "_cache"


def build_bessel_LP(
    frequencies: np.ndarray,
    target_radius: float = 1.0,
) -> tuple[cp.Problem, cp.Variable]:
    """Build the OFV-style Bessel-LP.

    Variables: c_k >= 0 for each frequency s_k.
    The parameterization F(r) = sum_k c_k J_0(2*pi*r*s_k) with c_k >= 0
    already enforces 'positive type' (F is the Hankel transform of a
    non-negative measure on [0, infty)). No pointwise positivity on F
    is required by the OFV theorem.

    Normalize F(0) = 1 via sum_k c_k = 1 (since J_0(0) = 1).
    Minimize F(target_radius) = sum_k c_k J_0(2*pi*target_radius*s_k).
    """
    # Target row: J_0(2*pi*target_radius*s_k)
    b_target = j0(2.0 * np.pi * target_radius * frequencies)

    c = cp.Variable(len(frequencies), nonneg=True)
    constraints = [
        cp.sum(c) == 1,        # F(0) = 1 (normalization)
    ]
    objective = cp.Minimize(b_target @ c)
    return cp.Problem(objective, constraints), c


def main():
    # Frequency grid: dense around the first negative trough of J_0.
    # J_0(t) has its first negative minimum at t ~ 3.83, value ~ -0.403.
    # So 2*pi*s = 3.83 gives s ~ 0.61. Sample densely around s ~ 0.6.
    N_freq = 2000
    freq = np.linspace(0.001, 5.0, N_freq)

    print(f"OFV Bessel-LP for m_1(R^2)")
    print(f"  frequencies: {N_freq} linearly spaced in [{freq[0]:.3f}, {freq[-1]:.1f}]")
    print(f"  no pointwise positivity constraints (positive-type via c_k >= 0)")
    print(f"  target: minimize F(1)")

    problem, c = build_bessel_LP(freq, target_radius=1.0)

    # Try solvers in order: HiGHS (best for LP), then SCS.
    solver_used = None
    elapsed = 0
    for solver in [cp.HIGHS, cp.SCS]:
        try:
            print(f"\nSolving via cvxpy + {solver}...")
            t0 = time.time()
            problem.solve(solver=solver, verbose=False)
            elapsed = time.time() - t0
            print(f"status: {problem.status}, elapsed {elapsed:.2f} s")
            if problem.status in ("optimal", "optimal_inaccurate"):
                solver_used = solver
                break
        except Exception as e:
            print(f"  {solver} failed: {e}")
            continue
    if solver_used is None:
        raise RuntimeError("no solver succeeded")

    F_at_1 = problem.value
    print(f"\nF(1)_min = {F_at_1:.6f}")

    if F_at_1 >= 0:
        print(f"WARNING: F(1) >= 0; this basis cannot produce a useful bound. "
              f"Increase N_freq or expand the frequency range.")
        m1_bound = 1.0
    else:
        # OFV bound: m_1(R^d) <= -F(1) / (F(0) - F(1)) when F is of positive type,
        # F(0) = 1 (normalized), F(1) < 0.
        m1_bound = -F_at_1 / (1.0 - F_at_1)
        print(f"m_1(R^2) <= -F(1) / (F(0) - F(1)) = {-F_at_1:.6f} / {1 - F_at_1:.6f} = {m1_bound:.6f}")

    chi_m_bound = 1.0 / m1_bound
    print(f"chi_m(R^2) >= 1 / m_1 = {chi_m_bound:.6f}")
    print(f"           Therefore chi_m >= {int(np.ceil(chi_m_bound))}")

    print(f"\nFor comparison:")
    print(f"  Trivial:               m_1 <= 1.0,    chi_m >= 1")
    print(f"  Falconer 1981:         m_1 <= ?,      chi_m >= 5")
    print(f"  OFV 2010 published:    m_1 <= 0.2688, chi_m >= 3.72 (so >= 4)")
    print(f"  Ambrus et al. 2023:    m_1 <= 0.2470, chi_m >= 4.05 (so >= 5)")
    print(f"  Required for chi_m>=6: m_1 <  0.2000")

    # Diagnose: where is the LP's mass concentrated?
    c_val = c.value
    significant_idx = np.where(c_val > 1e-4)[0]
    print(f"\nLP mass placement (frequencies with c_k > 1e-4):")
    for i in significant_idx[:10]:
        print(f"  freq {freq[i]:7.4f}: c = {c_val[i]:.6f}, J_0(2 pi * freq) at r=1: {j0(2 * np.pi * freq[i]):.6f}")
    if len(significant_idx) > 10:
        print(f"  ... ({len(significant_idx)} significant frequencies total)")

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3b_ofv_bessel_lp.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e3b_ofv_bessel_lp",
                "n_frequencies": N_freq,
                "freq_min": float(freq[0]),
                "freq_max": float(freq[-1]),
                "F_at_1": float(F_at_1),
                "m1_upper_bound": float(m1_bound),
                "chi_m_lower_bound": float(chi_m_bound),
                "chi_m_integer_bound": int(np.ceil(chi_m_bound)),
                "solve_time_s": elapsed,
                "solver_status": problem.status,
                "significant_frequencies": [float(freq[i]) for i in significant_idx],
                "significant_weights": [float(c_val[i]) for i in significant_idx],
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
