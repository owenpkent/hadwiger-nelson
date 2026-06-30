r"""Option A seeded from P510 (instead of a random point cloud).

The flagship adversary's random-seed run (adversarial.py) only ever reaches chi=3:
a random cloud has no chromatic structure, so the inner colorer always wins. The
right starting basin is a KNOWN hard chi=5 unit-distance graph. P510 (Polymath/Parts,
510 vertices, exact coords in Q(sqrt3, sqrt11, sqrt5)) is exactly that: chi(P510)=5,
i.e. it is 5-colorable but NOT 4-colorable. We seed the adversary at P510's true
coordinates and let it deform the positions to try to make the best 5-coloring bad --
i.e. to push the configuration toward needing a 6th color, staying inside the realizable
(unit-distance) world the whole time.

Honest expectation: this is the open problem, so the likely outcome is that P510 stays
5-colorable under local coordinate moves (an informative negative that localizes where,
if anywhere, chromatic pressure concentrates). A SAT-confirmed 5-UNSAT deformation would
be the prize and is checked for explicitly (budgeted).

Run:  python -m experiments.gradient.adversarial_p510
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import sympy as sp

from . import diff_udg as D
from .adversarial import run_adversary, discrete_graph

COMB = pathlib.Path(__file__).resolve().parents[1] / "combinatorial"
sys.path.insert(0, str(COMB))


def load_p510_coords():
    """Exact P510 coords -> float (n,2), plus the true edge list."""
    from f1pt_lib import load_p510  # noqa: E402
    base, edges = load_p510()
    coords = np.array([[float(sp.N(x, 30)), float(sp.N(y, 30))] for (x, y) in base])
    return coords, [tuple(e) for e in edges]


def sat_5col(n, edges, budget_conflicts=2_000_000):
    """Is the extracted graph 5-colorable? UNSAT => chi>=6 (the prize). Budgeted."""
    try:
        from f1pt_lib import sat_kcolor
        from pysat.solvers import Cadical195
    except ImportError:
        return None
    res, dt = sat_kcolor(n, edges, 5, Cadical195, budget_conflicts=budget_conflicts)
    return res, dt  # res True=5-colorable, False=5-UNSAT(chi>=6), None=budget hit


def main():
    print("Option A seeded from P510  (deform a real chi=5 UDG toward chi>=6)\n")
    coords0, true_edges = load_p510_coords()
    n = len(coords0)
    print(f"  loaded P510: {n} vertices, {len(true_edges)} unit edges (chi=5)")

    # Choose tau so the soft graph FAITHFULLY recovers the true unit edges. P510 is
    # dense and has many non-edge pairs near (but not at) unit distance, so a loose tau
    # thickens the graph and inflates its chromatic demand artificially. Tighten until
    # the soft edge count tracks the true 2504; report the trade (small tau = faithful
    # but weaker gradient signal for new edges to form).
    print("  tau sweep (faithfulness of the soft graph vs the true unit edges):")
    tau, best_gap = 0.05, None
    for tcand in (0.05, 0.03, 0.02, 0.012):
        _, se = discrete_graph(coords0, thr=0.5, tau=tcand)
        gap = abs(len(se) - len(true_edges))
        print(f"    tau={tcand:<5}  soft edges = {len(se):5d}  (gap to true {gap})")
        if best_gap is None or gap < best_gap:
            tau, best_gap = tcand, gap
    print(f"  using tau = {tau} (closest to the true edge count)\n")

    # adversary: ascend coordinates against the best soft 5-coloring.
    print("  running adversary (k=5, deforming positions)...")
    coords, hist, final = run_adversary(
        coords0, k=5, tau=tau, outer_steps=200, inner_steps=30,
        lr_coords=0.004, lr_logits=0.08, lam_spread=0.3, lam_edge=0.2,
        target_deg=float(2 * len(true_edges) / n), seed=0, log_every=50)
    print(f"\n  colorability_loss: start {hist[0]:.4e}  ->  end {final:.4e}")

    n2, edges2 = discrete_graph(coords, thr=0.5, tau=tau)
    print(f"  extracted deformed graph: {n2} vtx, {len(edges2)} near-unit edges")
    sat = sat_5col(n2, edges2)
    if sat is None:
        print("  (pysat unavailable; install python-sat for the chi check.)")
    else:
        res, dt = sat
        if res is True:
            verdict = "5-colorable (chi<=5, still not the prize)"
        elif res is False:
            verdict = "5-UNSAT  ->  chi>=6  ***VERIFY THIS***"
        else:
            verdict = "budget hit (inconclusive)"
        print(f"  SAT 5-colorability of the deformed graph [{dt:.1f}s]: {verdict}")
    print("\n  Note: chromatic pressure that survives here, localized to a small vertex")
    print("  set, is the seed for a hand-built clamp; a true 5-UNSAT deformation is the")
    print("  prize and must be re-confirmed exactly (unit distances + dual UNSAT).")


if __name__ == "__main__":
    main()
