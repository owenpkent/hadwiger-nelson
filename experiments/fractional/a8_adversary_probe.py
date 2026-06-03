r"""ADVERSARY probe for direction A8.

A8 proposes importing the W2 forcing-locality fact (non-edges CAN share a color)
into the measurable order-1/order-2 SDP as linear moment inequalities
    p_ij = y_ij(c,c) >= tau > 0   for non-adjacent pairs (i,j).

Claim under test: this manufactures an order-1/order-2 separation that L50 found
absent. ADVERSARY hypothesis: p_ij is ALREADY a free nonneg variable in e3p with
0 <= p_ij <= 1/k, so the import only RAISES a lower bound that the relaxation is
free to satisfy. Since infeasibility (a chi_m certificate) is detected by an
UPPER obstruction (Bochner autocorrelation can force p_ij small / negative S),
adding a LOWER floor p_ij >= tau can only SHRINK the feasible set -- it can never
turn a feasible (margin-0) instance infeasible in a way that yields a valid bound,
UNLESS the floor itself is a valid consequence of k-colorability. And the floor is
NOT a valid consequence: a particular color class can be empty on a non-edge, so
the true measurable moments need not satisfy p_ij >= tau for any tau > 0.

This probe runs e3p (order-1) on Moser at several k, baseline vs +floor, to show:
  (a) the floor is NOT implied (it changes the solve), AND
  (b) any "certificate" it produces is FAKE (appears at k >= chi too).
Either way A8 does not produce a sound new bound. We report which.
"""
from __future__ import annotations

import numpy as np
import cvxpy as cp
from itertools import combinations
from scipy.special import j0

from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config, _moser_vertices_exact,
)


def moser_floats():
    V = _moser_vertices_exact()
    import sympy as sp
    X = np.array([[float(sp.nsimplify(c)) if not isinstance(c, float) else c
                   for c in v] for v in V], dtype=float)
    # unit edges
    n = len(X)
    edges = set()
    for i, j in combinations(range(n), 2):
        d = np.linalg.norm(X[i] - X[j])
        if abs(d - 1.0) < 1e-9:
            edges.add((i, j))
    return X, edges


def solve_e3p(X, edges, k, floor_tau=0.0, floor_pairs=None, n_freq=200, freq_max=20.0):
    """Order-1 S_k-reduced relaxation (mirrors e3p). Optionally impose
    p_ij >= floor_tau on the given floor_pairs (default: all non-edges)."""
    n = X.shape[0]
    edges = set((min(a, b), max(a, b)) for (a, b) in edges)
    pairs = list(combinations(range(n), 2))
    dist = {(i, j): float(np.linalg.norm(X[i] - X[j])) for (i, j) in pairs}

    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)

    nu = cp.Variable(n_freq, nonneg=True)
    p = {(i, j): cp.Variable(nonneg=True) for (i, j) in pairs if (i, j) not in edges}

    cons = [cp.sum(nu) == 1.0 / k, J0_at_1 @ nu == 0]

    slacks = []
    for (i, j), var in p.items():
        Jvec = j0(2.0 * np.pi * dist[(i, j)] * freqs)
        s = cp.Variable()
        slacks.append(s)
        cons.append(var - Jvec @ nu == s)
        cons.append(var <= 1.0 / k)

    # A8 IMPORT: same-color-density floor on chosen non-edges.
    nonedges = [pr for pr in pairs if pr not in edges]
    if floor_pairs is None:
        floor_pairs = nonedges
    for pr in floor_pairs:
        if pr in p:
            cons.append(p[pr] >= floor_tau)

    # standard n x n PSD block
    rows = []
    edge_q = 1.0 / (k * (k - 1))
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(cp.Constant(1.0 / k))
            else:
                a, b = (i, j) if i < j else (j, i)
                if (a, b) in edges:
                    row.append(cp.Constant(-edge_q))
                else:
                    pij = p[(a, b)]
                    qij = (cp.Constant(1.0 / k) - pij) / (k - 1)
                    row.append(pij - qij)
        rows.append(cp.hstack(row))
    S = cp.vstack(rows)
    cons.append(S == S.T)
    cons.append(S >> 0)

    prob = cp.Problem(cp.Minimize(cp.sum([cp.abs(s) for s in slacks])), cons)
    try:
        prob.solve(solver=cp.CLARABEL, verbose=False)
    except cp.error.SolverError:
        return {"status": "solver_error", "margin": None}
    return {"status": prob.status,
            "margin": float(prob.value) if prob.value is not None else None}


if __name__ == "__main__":
    X, edges = moser_floats()
    print(f"Moser: n={X.shape[0]}, edges={len(edges)}, chi=4")
    print("=" * 70)
    for k in [3, 4, 5]:
        base = solve_e3p(X, edges, k, floor_tau=0.0)
        for tau in [1e-4, 1e-3, 1e-2, 0.02, 0.05]:
            fl = solve_e3p(X, edges, k, floor_tau=tau)
            print(f"k={k} tau={tau:<7} | base: {base['status']:<22} "
                  f"margin={base['margin']!s:<12} || +floor: {fl['status']:<22} "
                  f"margin={fl['margin']!s}")
        print("-" * 70)
