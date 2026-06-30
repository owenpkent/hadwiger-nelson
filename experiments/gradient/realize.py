r"""Option B: the LEGAL-UDG realizer (patched).

The legacy realizer (combinatorial/realizability_w3_clamp.py) minimizes only the
edge residual r_e = |p_i - p_j|^2 - 1. A zero of that is NOT enough: the embedding
is a legal UDG of the intended abstract graph only if every NON-edge also stays off
the unit circle. Otherwise the drawing has extra unit-distance edges and is a
different graph (which can change chi).

This script minimizes  edge_residual + w * nonedge_margin  with torch+Adam, multi-
start (Kamada-Kawai / spring / random), and reports BOTH numbers:
  - max edge error   (should be ~0)
  - min non-edge gap  | distance - 1 |  (should be >= delta => legal)

Calibration (so a NEGATIVE is structural, not solver fatigue): Moser spindle and a
triangular-lattice patch are realizable BY CONSTRUCTION and must come back legal.

Run:  python -m experiments.gradient.realize
"""
from __future__ import annotations

import math

import networkx as nx
import numpy as np
import torch

from . import diff_udg as D


def _init_layouts(n, edges, n_random=8, seed=0):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    rng = np.random.default_rng(seed)
    outs = []
    try:
        kk = nx.kamada_kawai_layout(G)
        outs.append(np.array([kk[i] for i in range(n)], float))
    except Exception:  # noqa: BLE001
        pass
    for s in range(3):
        sp = nx.spring_layout(G, seed=s, iterations=300)
        outs.append(np.array([sp[i] for i in range(n)], float))
    for _ in range(n_random):
        outs.append(rng.uniform(-math.sqrt(n), math.sqrt(n), size=(n, 2)))
    # scale each so the median edge length is 1
    scaled = []
    for p in outs:
        lens = [math.hypot(*(p[i] - p[j])) for (i, j) in edges] or [1.0]
        med = float(np.median(lens))
        scaled.append(p / med if med > 1e-9 else p)
    return scaled


def realize(n, edges, true_coords=None, delta=0.05, w_margin=1.0,
            starts=12, steps=1500, lr=0.03, seed=0):
    """Search for a legal UDG realization. Returns dict with best metrics."""
    ei = D.edges_to_index(edges)
    nei = D.nonedges_index(n, edges)
    inits = _init_layouts(n, edges, n_random=starts, seed=seed)
    if true_coords is not None:
        rng = np.random.default_rng(seed + 1)
        tc = np.array(true_coords, float)
        for sig in (0.05, 0.15, 0.3):
            inits.append(tc + rng.normal(0, sig, size=tc.shape))

    best = None
    for p0 in inits:
        coords = torch.tensor(p0, requires_grad=True)

        def loss_fn():
            return D.edge_residual_loss(coords, ei) + w_margin * D.nonedge_margin_loss(coords, nei, delta)

        D.adam_minimize([coords], loss_fn, steps=steps, lr=lr)
        err = D.max_edge_error(coords, edges)
        gap = D.min_nonedge_gap(coords, n, edges)
        legal = (err < 1e-4) and (gap >= delta - 1e-6)
        cand = {"max_edge_err": err, "min_nonedge_gap": gap, "legal": legal,
                "coords": coords.detach().numpy().copy()}
        # rank: legal first, then by edge error
        key = (not legal, err)
        if best is None or key < (not best["legal"], best["max_edge_err"]):
            best = cand
        if legal and err < 1e-6:
            break
    return best


def _report(name, res):
    flag = "LEGAL-UDG" if res["legal"] else "not legal"
    print(f"  {name:24s}  max_edge_err={res['max_edge_err']:.2e}  "
          f"min_nonedge_gap={res['min_nonedge_gap']:.3f}  -> {flag}")


def main():
    print("Option B  -  legal-UDG realizer (edge residual + non-edge margin)\n")
    print("Calibration (must come back LEGAL):")
    for name, (n, edges, coords) in [
        ("Moser spindle", D.moser_spindle()),
        ("triangular patch", D.triangular_lattice_patch(rings=3)),
    ]:
        res = realize(n, edges, true_coords=coords)
        _report(name, res)

    # Contrast: K4 is NOT a unit-distance graph in R^2 (needs R^3). The realizer
    # should fail to make it legal -- a one-sided negative the legacy residual-only
    # objective can also catch, shown here for completeness.
    print("\nContrast (should FAIL to realize in R^2):")
    n, edges = 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    _report("K4 (needs R^3)", realize(n, edges, starts=20, steps=1500))


if __name__ == "__main__":
    main()
