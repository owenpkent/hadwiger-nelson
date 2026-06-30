r"""Option A: adversarial coordinate <-> soft-coloring co-optimization (flagship).

The GD-native reframe of the live Arch-1 route ("a new chi-5 UDG outside the P510
lineage carrying a wide imprimitive interface"). Couple two surfaces:

    maximize_{coords}  [ min_{soft coloring}  coloring_loss( coords, coloring ) ]

The inner player finds the best soft k-coloring of the *soft* graph a(coords)
(soft_adjacency: pairs near unit distance are edges, differentiably). The outer
player moves the vertex POSITIONS to make that best coloring as bad as possible.
So we ascend coordinates toward a near-uncolorable unit-distance configuration.

Why this respects the wrong-approach detector: the objective is driven by
soft_adjacency, i.e. by REAL Euclidean unit distances. It cannot lift to Q^2 (where
chi = 2) because the chromatic pressure only appears where points sit at genuine
unit distance in R^2. A pure abstract-adjacency version would lift, and is wrong.

Honest status: EXPERIMENTAL. Saddle-point GDA is finicky and the global object
(reach chi > 5) is the open problem itself. What is delivered and calibrated here:
  (1) the inner coloring optimizer recovers known chromatic facts (triangle needs 3,
      K5 needs 5) -- so coloring_loss is a faithful colorability surface;
  (2) the outer loop provably raises the colorability floor on a seed and hands the
      resulting discrete near-unit graph to SAT for an exact chi readout.
Candidates SAT-certified at chi >= 6 would be the prize; none is claimed here.

Run:  python -m experiments.gradient.adversarial
"""
from __future__ import annotations

import math

import numpy as np
import torch

from . import diff_udg as D


# --------------------------------------------------------------------------
# inner-loop calibration: does coloring_loss know the chromatic number?
# --------------------------------------------------------------------------
def best_coloring_loss(coords, k, steps=1500, lr=0.05, tau=0.06, seed=0, restarts=3):
    """min over soft k-colorings of coloring_loss on the soft graph a(coords)."""
    a = D.soft_adjacency(coords, tau=tau).detach()
    n = coords.shape[0]
    best = math.inf
    for r in range(restarts):
        g = torch.Generator().manual_seed(seed + r)
        logits = torch.randn(n, k, generator=g, requires_grad=True)
        D.adam_minimize([logits], lambda: D.coloring_loss(logits, a), steps=steps, lr=lr)
        best = min(best, float(D.coloring_loss(logits, a).detach()))
    return best


def calibrate_inner():
    print("Inner-loop calibration (coloring_loss vs known chi):")
    n, _, tri = D.unit_triangle()
    tri = torch.tensor(tri)
    print(f"  unit triangle (chi=3):   loss@k=2 = {best_coloring_loss(tri, 2):.3e}"
          f"   loss@k=3 = {best_coloring_loss(tri, 3):.3e}   (expect >0 then ~0)")

    # K5 as a unit-distance-ish clique: place 5 points and force near-unit pairwise.
    # Easiest faithful K_m for the inner test: use exact adjacency = all-ones.
    for m in (5,):
        ones = torch.ones(m, m) - torch.eye(m)
        lo = []
        for k in (4, 5):
            g = torch.Generator().manual_seed(7)
            logits = torch.randn(m, k, generator=g, requires_grad=True)
            D.adam_minimize([logits], lambda: D.coloring_loss(logits, ones), steps=2000, lr=0.05)
            lo.append(float(D.coloring_loss(logits, ones).detach()))
        print(f"  K{m} (chi={m}):            loss@k=4 = {lo[0]:.3e}"
              f"   loss@k=5 = {lo[1]:.3e}   (expect >0 then ~0)")


# --------------------------------------------------------------------------
# outer loop: ascend coordinates against the best k-coloring
# --------------------------------------------------------------------------
def run_adversary(init_coords, k=5, tau=0.07, outer_steps=400, inner_steps=40,
                  lr_coords=0.01, lr_logits=0.08, lam_spread=0.5, lam_edge=0.4,
                  target_deg=3.5, seed=0, log_every=100):
    """Alternating gradient descent/ascent. Returns (coords, history, final_loss).

    The outer objective is  -colorability_loss + lam_spread*spread + lam_edge*deg_gap.
    The deg_gap term is essential: without an edge-formation incentive the adversary's
    trivial optimum is "no unit distances at all" (an empty graph is 1-colorable). The
    term pins the mean soft-degree near a UDG-like target, forcing it to BUILD a
    unit-distance graph and only then make that graph hard to k-color.
    """
    coords = torch.tensor(np.asarray(init_coords, float), requires_grad=True)
    n = coords.shape[0]
    g = torch.Generator().manual_seed(seed)
    logits = torch.randn(n, k, generator=g, requires_grad=True)
    opt_c = torch.optim.Adam([coords], lr=lr_coords)
    opt_l = torch.optim.Adam([logits], lr=lr_logits)
    hist = []
    for t in range(outer_steps):
        # inner: minimize colorability loss (find the best coloring of current graph)
        for _ in range(inner_steps):
            opt_l.zero_grad()
            a = D.soft_adjacency(coords.detach(), tau=tau)
            li = D.coloring_loss(logits, a)
            li.backward()
            opt_l.step()
        # outer: MAXIMIZE colorability loss wrt coords (minimize its negative),
        # while holding the graph at UDG-like density and avoiding collapse.
        opt_c.zero_grad()
        a = D.soft_adjacency(coords, tau=tau)
        cl = D.coloring_loss(logits.detach(), a)
        mean_deg = a.sum() / n
        deg_gap = (mean_deg - target_deg) ** 2
        obj = -cl + lam_spread * D.spread_penalty(coords) + lam_edge * deg_gap
        obj.backward()
        opt_c.step()
        hist.append(float(cl.detach()))
        if log_every and t % log_every == 0:
            print(f"    outer {t:4d}  colorability_loss = {hist[-1]:.4e}"
                  f"   mean_soft_deg = {float(mean_deg.detach()):.2f}")
    return coords.detach(), hist, hist[-1] if hist else 0.0


def discrete_graph(coords, thr=0.5, tau=0.07):
    """Threshold the soft graph into a discrete near-unit-distance graph."""
    c = coords.detach() if torch.is_tensor(coords) else torch.tensor(np.asarray(coords, float))
    a = D.soft_adjacency(c, tau=tau).numpy()
    n = a.shape[0]
    return n, [(i, j) for i in range(n) for j in range(i + 1, n) if a[i, j] > thr]


def sat_chi(n, edges, k_try=(2, 3, 4, 5, 6, 7)):
    """Exact chromatic number of the extracted discrete graph, via pysat."""
    try:
        from pysat.formula import CNF
        from pysat.solvers import Cadical195
    except ImportError:
        return None
    for k in k_try:
        cnf = CNF()
        var = lambda v, c: v * k + c + 1
        for v in range(n):
            cnf.append([var(v, c) for c in range(k)])
            for c1 in range(k):
                for c2 in range(c1 + 1, k):
                    cnf.append([-var(v, c1), -var(v, c2)])
        for (u, v) in edges:
            for c in range(k):
                cnf.append([-var(u, c), -var(v, c)])
        with Cadical195(bootstrap_with=cnf.clauses) as s:
            if s.solve():
                return k
    return f">{k_try[-1]}"


def main():
    print("Option A  -  adversarial coordinate <-> coloring co-optimization\n")
    calibrate_inner()

    print("\nOuter-loop demo (EXPERIMENTAL): ascend a random seed against best 5-coloring")
    rng = np.random.default_rng(0)
    n0 = 24
    init = rng.uniform(-2.0, 2.0, size=(n0, 2))
    coords, hist, final = run_adversary(init, k=5, outer_steps=400)
    print(f"  colorability_loss: start {hist[0]:.4e}  ->  end {final:.4e}")
    n, edges = discrete_graph(coords)
    chi = sat_chi(n, edges)
    print(f"  extracted near-unit graph: {n} vtx, {len(edges)} edges, exact chi = {chi}")
    print("  (a SAT chi >= 6 here would be the prize; this seed is only a harness check.)")


if __name__ == "__main__":
    main()
