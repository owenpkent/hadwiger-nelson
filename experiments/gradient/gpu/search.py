r"""Reusable GPU search routines built on batched_core.

Two primitives the campaigns and the validation gate share:

  multistart_realize   -- Option B at scale: B parallel embeddings of ONE abstract
                          graph; return the best legal-UDG realization (float64 CPU
                          refined). A host that realizes legally is a live chi>=6
                          candidate; the L63 hosts must all fail here.

  soft_chi_oracle      -- heuristic colorability witness: best soft coloring_loss@k
                          over `restarts` parallel random inits. A large residual at
                          k is only a SIGNAL that chi>k; the SAT firewall decides.

Neither certifies a lower bound. Both PROPOSE; SAT disposes.
"""
from __future__ import annotations

import math

import numpy as np
import torch

from experiments.gradient.gpu import batched_core as bc


# --------------------------------------------------------------------------
# Option B: multi-start legal-UDG realizer
# --------------------------------------------------------------------------
def multistart_realize(n, edges, *, B=1024, device=None, steps=1500, lr=0.02,
                       delta=0.05, margin_weight=1.0, scale=1.5, seed=0,
                       refine_steps=4000):
    """Realize the abstract graph (n, edges) as a legal UDG via B parallel starts.

    GPU float32 search minimizes edge_residual + margin_weight * nonedge_margin over
    B random embeddings; the best is re-refined in float64 on CPU and its true edge
    error / non-edge gap are measured exactly. Returns a dict verdict.

    LEGAL means: every intended edge is at unit distance (max_edge_err small) AND no
    non-edge sits on the unit circle (min_nonedge_gap healthy). Edge residual alone is
    not enough -- that is the whole point of the non-edge margin term.
    """
    device = device or bc.pick_device()
    gen = torch.Generator(device=device).manual_seed(seed)

    edge_index = bc.edges_to_index(edges, device)
    nonedge_index = bc.nonedges_index(n, edges, device)
    coords = bc.random_coords(B, n, device, dtype=torch.float32, scale=scale,
                              generator=gen)

    def loss_vec():
        er = bc.batched_edge_residual(coords, edge_index)
        nm = bc.batched_nonedge_margin(coords, nonedge_index, delta=delta)
        return er + margin_weight * nm

    bc.batched_adam([coords], loss_vec, steps=steps, lr=lr)

    # take the top-K starts by a legality-aware score, refine each in float64, keep
    # the most legal (a single "best by float32 score" can be deceptive: low edge
    # residual but an accidental near-unit non-edge).
    topk = min(8, B)
    with torch.no_grad():
        er = bc.batched_edge_residual(coords, edge_index)
        nm = bc.batched_nonedge_margin(coords, nonedge_index, delta=delta)
        score = er + margin_weight * nm
        idx = torch.argsort(score)[:topk].tolist()

    best = None
    for bi in idx:
        c0 = coords[bi].detach().to("cpu", torch.float64).clone()
        refined = _cpu_refine(c0, edges, n, delta=delta,
                              margin_weight=margin_weight, steps=refine_steps, lr=lr)
        me = _max_edge_error(refined, edges)
        gp = _min_nonedge_gap(refined, n, edges)
        cand = (me, -gp, refined, bi)
        if best is None or cand[:2] < best[:2]:
            best = cand
    max_err, neg_gap, refined, best_bi = best
    gap = -neg_gap
    legal = (max_err < 1e-6) and (gap > delta * 0.5)
    best = best_bi
    return {
        "n": n, "num_edges": len(edges), "B": B,
        "best_batch_edge_residual": float(er[best].item()),
        "best_batch_nonedge_margin": float(nm[best].item()),
        "refined_max_edge_error": max_err,
        "refined_min_nonedge_gap": gap,
        "legal_udg": bool(legal),
        "coords": refined.numpy(),
    }


def _cpu_refine(coords0, edges, n, *, delta, margin_weight, steps, lr):
    """float64 CPU polish of one embedding using the diff_udg terms."""
    from experiments.gradient import diff_udg as du
    c = coords0.clone().to(torch.float64).requires_grad_(True)
    ei = du.edges_to_index(edges) if edges else torch.zeros((0, 2), dtype=torch.long)
    nei = du.nonedges_index(n, edges)

    def loss():
        er = du.edge_residual_loss(c, ei)
        nm = du.nonedge_margin_loss(c, nei, delta=delta)
        return er + margin_weight * nm

    du.adam_minimize([c], loss, steps=steps, lr=lr)
    # LBFGS polish: rigid unit-distance realizations converge quadratically here,
    # driving a genuine realization to machine precision. A graph that is NOT
    # realizable in the plane (e.g. K4) stays stuck with a large residual -- which
    # is exactly the legality signal we want.
    opt = torch.optim.LBFGS([c], lr=1.0, max_iter=250, history_size=50,
                            tolerance_grad=1e-18, tolerance_change=1e-20,
                            line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        val = loss()
        val.backward()
        return val

    try:
        opt.step(closure)
    except Exception:
        pass
    return c.detach()


def _max_edge_error(coords_t, edges):
    p = coords_t.numpy() if hasattr(coords_t, "numpy") else np.asarray(coords_t)
    if not edges:
        return 0.0
    return max(abs(math.hypot(*(p[i] - p[j])) - 1.0) for (i, j) in edges)


def _min_nonedge_gap(coords_t, n, edges):
    p = coords_t.numpy() if hasattr(coords_t, "numpy") else np.asarray(coords_t)
    es = {(min(i, j), max(i, j)) for (i, j) in edges}
    gaps = [abs(math.hypot(*(p[i] - p[j])) - 1.0)
            for i in range(n) for j in range(i + 1, n) if (i, j) not in es]
    return min(gaps) if gaps else float("inf")


# --------------------------------------------------------------------------
# heuristic colorability oracle (soft, GPU, multi-restart)
# --------------------------------------------------------------------------
def soft_chi_oracle(adjacency, k, *, restarts=256, steps=1200, lr=0.05, device=None,
                    seed=0):
    """Best soft coloring_loss@k over `restarts` parallel random colorings.

    adjacency: (n, n) nonneg tensor or ndarray. Returns the minimum achievable
    coloring loss at k colors (float). ~0 => a proper k-coloring was found (chi<=k);
    a residual bounded away from 0 across many restarts SIGNALS chi>k -- confirm with
    SAT, never conclude here.
    """
    device = device or bc.pick_device()
    if isinstance(adjacency, torch.Tensor):
        A = adjacency.to(device=device, dtype=torch.float32)
    else:
        A = torch.as_tensor(np.asarray(adjacency), dtype=torch.float32, device=device)
    n = A.shape[0]
    Ab = A[None].expand(restarts, n, n).contiguous()
    gen = torch.Generator(device=device).manual_seed(seed)
    logits = torch.randn(restarts, n, k, device=device, generator=gen).requires_grad_(True)

    def loss_vec():
        return bc.batched_coloring_loss(logits, Ab)

    final = bc.batched_adam([logits], loss_vec, steps=steps, lr=lr)
    return float(final.min().item())


def hard_adjacency(n, edges, device=None):
    """0/1 adjacency (n, n) from an edge list, for the oracle's calibration."""
    device = device or bc.pick_device()
    A = torch.zeros(n, n, device=device)
    for (i, j) in edges:
        A[i, j] = 1.0
        A[j, i] = 1.0
    return A
