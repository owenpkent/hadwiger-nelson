r"""Validation gate for the batched GPU core (smoke_test discipline).

A new solver / encoding is not trusted until it reproduces a known baseline. This
gate asserts the batched GPU primitives reproduce the same answers the calibrated
CPU core (diff_udg) is checked against:

  realizer   : Moser spindle and a triangular-lattice patch come back as LEGAL UDGs;
               K4 (needs R^3) fails to realize.
  oracle     : unit-triangle soft coloring_loss@k=2 ~ 1/3, @k=3 ~ 0;
               K5 loss@k=4 ~ 0.1, @k=5 ~ 0.

Non-zero exit == a baseline broke; do not run the campaigns on a broken core.
Run: python -m experiments.gradient.gpu.validate
"""
from __future__ import annotations

import sys

import torch

from experiments.gradient import diff_udg as du
from experiments.gradient.gpu import batched_core as bc
from experiments.gradient.gpu import search as S


def _check(name, cond, detail):
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}: {detail}")
    return cond


def _complete_graph(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def main():
    device = bc.pick_device()
    print(f"device: {device}  torch {torch.__version__}  "
          f"cuda={torch.cuda.is_available()}")
    ok = True

    # ---- realizer baselines -------------------------------------------------
    print("\nrealizer (multi-start, B=768):")
    n_m, edges_m, _ = du.moser_spindle()
    r = S.multistart_realize(n_m, edges_m, B=768, device=device, steps=1500,
                             seed=1)
    ok &= _check("moser_spindle legal",
                 r["legal_udg"],
                 f"max_edge_err={r['refined_max_edge_error']:.2e} "
                 f"gap={r['refined_min_nonedge_gap']:.3f}")

    # rings=1: the 7-vertex hex patch (center + 6 neighbors), easily realizable
    # from scratch. (Larger rigid lattices need structured inits, not pure random
    # multistart -- handled in the campaign, not gated here.)
    n_t, edges_t, _ = du.triangular_lattice_patch(rings=1)
    r = S.multistart_realize(n_t, edges_t, B=1536, device=device, steps=2200,
                             seed=2)
    ok &= _check("triangular_patch(rings=1) legal",
                 r["legal_udg"],
                 f"n={n_t} max_edge_err={r['refined_max_edge_error']:.2e} "
                 f"gap={r['refined_min_nonedge_gap']:.3f}")

    # K4 needs R^3: must NOT realize legally in the plane
    r = S.multistart_realize(4, _complete_graph(4), B=768, device=device,
                             steps=1500, seed=3)
    ok &= _check("K4 refuses to realize (correct)",
                 not r["legal_udg"],
                 f"max_edge_err={r['refined_max_edge_error']:.2e} "
                 f"(large == correct)")

    # ---- coloring oracle baselines -----------------------------------------
    print("\ncoloring oracle (soft, restarts=384):")
    tri = S.hard_adjacency(3, [(0, 1), (1, 2), (0, 2)], device=device)
    l2 = S.soft_chi_oracle(tri, 2, restarts=384, steps=1500, device=device, seed=4)
    l3 = S.soft_chi_oracle(tri, 3, restarts=384, steps=1500, device=device, seed=5)
    ok &= _check("triangle loss@k=2 ~ 0.333", abs(l2 - 1 / 3) < 0.02,
                 f"{l2:.4f} (expect 0.333)")
    ok &= _check("triangle loss@k=3 ~ 0", l3 < 1e-2, f"{l3:.4f} (expect ~0)")

    k5 = S.hard_adjacency(5, _complete_graph(5), device=device)
    l4 = S.soft_chi_oracle(k5, 4, restarts=384, steps=1500, device=device, seed=6)
    l5 = S.soft_chi_oracle(k5, 5, restarts=384, steps=1500, device=device, seed=7)
    ok &= _check("K5 loss@k=4 ~ 0.1", abs(l4 - 0.1) < 0.02, f"{l4:.4f} (expect 0.1)")
    ok &= _check("K5 loss@k=5 ~ 0", l5 < 1e-2, f"{l5:.4f} (expect ~0)")

    print("\n" + ("ALL BASELINES PASS" if ok else "BASELINE FAILURE"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
