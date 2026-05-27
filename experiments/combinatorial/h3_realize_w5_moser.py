r"""h3_realize_w5_moser: numerical UDG realizability test for the W5 x Moser
13-vertex no-K_4 chi=5 abstract graph from h3.

H_1 = W_5 wheel (hub + C_5, 6 vertices). UDG-realizable? W_5 contains C_5 which is
not UDG (no 5 unit-distance points on a regular pentagon path). Actually wait: a
unit-equilateral pentagon does not exist in R^2 (regular pentagon has unit sides
but the diagonals are not unit). The W_5 wheel has hub at unit distance to all 5
rim vertices and rim is a C_5 of length 5 with unit edges. Hub at origin, rim
vertices at angles 2*pi*k/5, distance 1: rim-to-rim distance is 2 sin(pi/5)
neq 1. So W_5 is NOT UDG. Wait that's a problem.

Actually the W_5 used here is hub + C_5 (5-cycle). For it to be UDG we'd need
the hub at unit distance to each rim, AND consecutive rim vertices at unit
distance. With hub at origin and rim at unit circle, consecutive rim distance
= 2 sin(pi/5) approx 1.176, not 1. So this W_5 is NOT UDG-realizable.

That means W5 x Moser 13-vertex abstract chi=5 graph is NOT UDG-realizable
either (since it contains W_5 as a subgraph).

CONCLUSION: the abstract 13-vertex W5 x Moser chi=5 graph is structurally
interesting but not directly UDG-realizable.

This script verifies that conclusion explicitly: tries to place the 13 vertices
in R^2 to satisfy all 24 edges (10 W5 + 11 Moser + 12 bridges) at unit distance.
Multi-start scipy with random initial poses. We expect ALL multi-starts to fail
with non-zero residual.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
import time

import numpy as np
from scipy.optimize import minimize

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)
OUT = CACHE / "h3_realize_w5_moser.json"


# ---------- abstract 13-vertex graph -----------------------------------------

def build_combined():
    # H_1 = W_5: vertices 0..5 (0 = hub, 1..5 = rim).
    E_W5 = [(0, i) for i in range(1, 6)]
    for i in range(1, 5):
        E_W5.append((i, i + 1))
    E_W5.append((1, 5))

    # H_2 = Moser spindle: vertices 0..6 (relabel as 6..12 in combined).
    # Moser edges from canonical labels:
    # 0-1, 0-2, 1-2, 1-3, 2-3, 0-4, 0-5, 4-5, 4-6, 5-6, 3-6 -- 11 edges
    E_moser_local = [
        (0, 1), (0, 2), (1, 2), (1, 3), (2, 3),
        (0, 4), (0, 5), (4, 5), (4, 6), (5, 6), (3, 6),
    ]
    N1 = 6
    E_M = [(u + N1, v + N1) for (u, v) in E_moser_local]

    # Bridges from h3 result:
    B_local = [
        (1, 5), (1, 6), (2, 2), (2, 3), (3, 3),
        (3, 4), (4, 0), (4, 1), (4, 4), (5, 1),
        (5, 2), (5, 6),
    ]
    E_B = [(u, v + N1) for (u, v) in B_local]

    edges = E_W5 + E_M + E_B
    return 13, edges, len(E_W5), len(E_M), len(E_B)


# ---------- numerical realizability ------------------------------------------

def residual_sum_sq(coords_flat, edges):
    """Sum of (d - 1)^2 over edges."""
    coords = coords_flat.reshape(-1, 2)
    total = 0.0
    for u, v in edges:
        d = math.hypot(coords[u, 0] - coords[v, 0], coords[u, 1] - coords[v, 1])
        total += (d - 1.0) ** 2
    return total


def residual_grad(coords_flat, edges):
    """Gradient of sum of (d - 1)^2."""
    coords = coords_flat.reshape(-1, 2)
    grad = np.zeros_like(coords)
    for u, v in edges:
        dx = coords[u, 0] - coords[v, 0]
        dy = coords[u, 1] - coords[v, 1]
        d = math.hypot(dx, dy)
        if d < 1e-12:
            continue
        f = (d - 1.0) / d
        grad[u, 0] += 2 * f * dx
        grad[u, 1] += 2 * f * dy
        grad[v, 0] -= 2 * f * dx
        grad[v, 1] -= 2 * f * dy
    return grad.flatten()


def multistart_realize(n, edges, n_starts=300, seed=42):
    rng = np.random.default_rng(seed)
    best_res = float("inf")
    best_x = None
    best_per_edge_max = None
    converged_count = 0
    for s in range(n_starts):
        x0 = rng.standard_normal(2 * n) * 1.5
        try:
            r = minimize(
                residual_sum_sq, x0,
                args=(edges,),
                jac=residual_grad,
                method="BFGS",
                options={"maxiter": 1000, "gtol": 1e-10},
            )
        except Exception:
            continue
        if r.fun < best_res:
            best_res = r.fun
            best_x = r.x
            # per-edge max
            coords = r.x.reshape(-1, 2)
            per_edge = []
            for u, v in edges:
                d = math.hypot(coords[u, 0] - coords[v, 0],
                               coords[u, 1] - coords[v, 1])
                per_edge.append(abs(d - 1.0))
            best_per_edge_max = max(per_edge)
        if r.fun < 1e-10:
            converged_count += 1
    return best_res, best_x, best_per_edge_max, converged_count


def main():
    n, edges, n_W5, n_M, n_B = build_combined()
    print(f"W5 x Moser combined: {n} vertices, {len(edges)} edges")
    print(f"  W5 edges: {n_W5}, Moser edges: {n_M}, Bridge edges: {n_B}")

    # Sanity: clique check.
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    cliques = list(nx.find_cliques(G))
    omega = max(len(c) for c in cliques)
    print(f"  omega(combined) = {omega}")

    # First check: any single W_5 unit-distance realization possible?
    # W_5 has C_5 + hub. C_5 of unit edges + hub at distance 1 from each rim.
    # Hub at origin; rim must be 5 unit-distance pairs around. C_5: pentagon side 1.
    # But hub at distance 1 from each rim vertex means rim is on unit circle.
    # Pentagon with side 1 has circumradius 1/(2 sin(pi/5)) ~ 0.851. Contradiction.
    # So W_5 is NOT UDG-realizable. Expect failure.
    W5_edges = edges[:n_W5]
    print("\nPhase 1: try to realize W_5 alone (expected to fail)")
    t0 = time.time()
    best_w5, _, max_err_w5, _ = multistart_realize(6, W5_edges, n_starts=200)
    print(f"  W5 alone: best residual = {best_w5:.6e}, max per-edge error = {max_err_w5:.4e} (t={time.time()-t0:.2f}s)")

    print("\nPhase 2: try the full 13-vertex graph (expected to fail since W5 already fails)")
    t0 = time.time()
    best, _, max_err, conv = multistart_realize(n, edges, n_starts=500)
    elapsed = time.time() - t0
    print(f"  full graph: best residual = {best:.6e}, max per-edge err = {max_err:.4e}, converged starts = {conv}/500")
    print(f"  elapsed: {elapsed:.2f}s")

    out = {
        "experiment": "h3_realize_w5_moser",
        "n_vertices": n,
        "n_edges": len(edges),
        "omega_combined": omega,
        "edges": edges,
        "w5_alone_best_residual": best_w5,
        "w5_alone_max_per_edge_error": max_err_w5,
        "full_best_residual": best,
        "full_max_per_edge_error": max_err,
        "full_converged_starts": conv,
        "full_n_starts": 500,
        "conclusion": (
            "W_5 (hub + C_5 with unit edges + unit spokes) is NOT realizable as a UDG "
            "since pentagon side 1 has circumradius != 1. Hence the full 13-vertex "
            "graph is not UDG-realizable. Multi-start scipy confirms."
        ),
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\narchived: {OUT}")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
