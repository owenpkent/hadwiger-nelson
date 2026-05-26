"""e3a: Lovász $\\vartheta$ on the Polymath16 510-vertex 5-chromatic UDG.

Architecture 3 baseline. Computes a numerical bound that crosses
Architectures 1 and 2:

    chi(G) >= chi_f(G) >= n / theta(G)

where `theta(G)` is the Lovász theta number, `n` is the vertex count,
and the chain is by Lovász's sandwich theorem.

For the Polymath16 510-vertex graph with `chi(G) = 5` (proved by SAT in
e1b), we have `alpha(G) <= n / chi = 510 / 5 = 102`, hence `theta(G) >=
102`. If we compute `theta(G) <= 102 + epsilon`, we have a tight bound.

The Lovász theta SDP (matrix form):

    theta(G) = max  <X, J>
    s.t.            X >> 0  (positive semidefinite)
                    trace(X) = 1
                    X[i, j] = 0  for all edges {i, j} in E(G)

This bounds the independence number above: `alpha(G) <= theta(G)`. For
sparse G (the UDG has 2504 edges on 510 vertices, far less than the
130,305 possible), this SDP has few equality constraints and is
tractable with cvxpy + SCS.

Cross-architecture significance: theta sits between alpha and
chi(complement), and is the same SDP object whose continuous-infinite
version Bachoc-Nebe-Oliveira Filho-Vallentin (2009, arXiv:0801.1059)
applied to bound chi_m(R^n).

Solver: cvxpy + SCS. Expect a few minutes on a 510x510 SDP.
"""

from __future__ import annotations

import json
import pathlib
import time

import cvxpy as cp
import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = pathlib.Path(__file__).parent / "_cache"
GRAPH_PATH = REPO_ROOT / "sources" / "cnp-sat" / "edge" / "510.edge"


def load_dimacs_edges(path: pathlib.Path) -> list[tuple[int, int]]:
    """Parse DIMACS `p edge V E` + `e u v` lines (1-indexed), return 0-indexed pairs."""
    edges = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("e"):
            _, u, v = line.split()
            edges.append((int(u) - 1, int(v) - 1))
    return edges


def lovasz_theta(n: int, edges: list[tuple[int, int]], verbose: bool = True) -> tuple[float, float]:
    """Lovász theta SDP. Returns (theta, solve_time_seconds).

    Variables: symmetric X in R^{n x n}.
    Maximize sum of all entries (which equals <X, J>).
    Subject to: X is PSD, trace(X) = 1, X[i,j] = 0 for each edge (i,j).
    """
    X = cp.Variable((n, n), symmetric=True)
    constraints = [X >> 0, cp.trace(X) == 1]
    # Vectorize edge constraints
    edge_rows = np.array([u for u, _ in edges])
    edge_cols = np.array([v for _, v in edges])
    constraints.append(X[edge_rows, edge_cols] == 0)
    objective = cp.Maximize(cp.sum(X))
    problem = cp.Problem(objective, constraints)
    t0 = time.time()
    problem.solve(solver=cp.SCS, verbose=verbose)
    elapsed = time.time() - t0
    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"SDP did not solve: status={problem.status}")
    if problem.status == "optimal_inaccurate":
        print(f"WARNING: SDP status is optimal_inaccurate; treat result as approximate")
    return float(problem.value), elapsed


def main():
    edges = load_dimacs_edges(GRAPH_PATH)
    n = max(max(u, v) for u, v in edges) + 1
    print(f"Polymath16 510-vertex graph: n={n}, |E|={len(edges)}")
    print(f"chi(G) = 5 (proved by SAT in e1b); independence number alpha(G) >= 102")

    print(f"\nSolving Lovász theta SDP with cvxpy + SCS...")
    theta, elapsed = lovasz_theta(n, edges, verbose=False)
    print(f"\ntheta(G) = {theta:.6f}  ({elapsed:.1f} s)")

    chi_lower = n / theta
    print(f"\nDerived bounds:")
    print(f"  alpha(G) <= theta(G) = {theta:.4f}")
    print(f"  chi_f(G) >= n / theta(G) = {n} / {theta:.4f} = {chi_lower:.6f}")
    print(f"  Therefore chi(G) >= ceil({chi_lower:.4f}) = {int(np.ceil(chi_lower))}")

    # Comparison to known bounds
    print(f"\nComparison:")
    print(f"  Known: chi(G) = 5 (SAT)")
    print(f"  Theta-derived lower bound on chi: {int(np.ceil(chi_lower))}")
    if int(np.ceil(chi_lower)) >= 5:
        print(f"  Result: theta tightly recovers chi >= 5")
    else:
        print(f"  Result: theta is loose by {5 - int(np.ceil(chi_lower))} integer units")

    # Cross-architecture: theta also relates to chi_f(R^2)
    # The Matolcsi-Ruzsa-Varga-Zsamboki (2023) bound chi_f(R^2) >= 4 used a 27-vertex graph.
    # Our 510-vertex bound below recovers chi_f(this 510-vertex finite graph) >= chi_lower.
    print(f"\nCross-architecture note: this is chi_f(this finite UDG), not chi_f(R^2). "
          f"The fractional chi of R^2 is at least chi_f(any finite UDG embedded in R^2), "
          f"so our chi_lower = {chi_lower:.4f} also lower-bounds chi_f(R^2).")

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3a_lovasz_theta_polymath16_510.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e3a_lovasz_theta_polymath16_510",
                "graph": "polymath16_510",
                "n_vertices": n,
                "n_edges": len(edges),
                "theta": theta,
                "alpha_upper_bound": theta,
                "chi_f_lower_bound": chi_lower,
                "chi_integer_lower_bound": int(np.ceil(chi_lower)),
                "chi_known": 5,
                "solve_time_s": elapsed,
                "solver": "cvxpy + SCS",
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
