r"""Batched, GPU-parameterized differentiable UDG primitives.

WHY this exists. The CPU core (`diff_udg.py`) runs one configuration at a time in
float64. Gradient descent on chi(R^2) is a LOCAL, ONE-SIDED search: a single run
from one seed reaches a single local optimum (the documented honest negative:
one adversarial GDA run reaches only chi=3). The way to make GD productive as a
CANDIDATE GENERATOR is massive multi-start: run thousands of independent
optimizations in parallel and keep the rare good tail. That is a batch dimension,
and a batch dimension is what a GPU is for.

DISCIPLINE. This module changes NOTHING about the governing constraint. GD still
never proves chi >= 6. Everything here PROPOSES float configurations; the exact
chromatic number of any survivor is decided by the SAT firewall
(`adversarial.sat_chi`, `f1pt_lib.sat_kcolor`), never by a loss value. The
coordinate-grounded terms (edge_residual, nonedge_margin, soft_adjacency) keep the
objective anchored in genuine Euclidean unit distances, so it cannot lift to Q^2
(where chi=2) -- the wrong-approach detector that a pure abstract-adjacency
soft-coloring objective would fail.

PRECISION. Search runs in float32 on the GPU (the RTX 5090 has ~1/64 FP64 rate, so
float32 is ~tens of x faster and is fine for PROPOSING candidates). Any survivor is
re-refined in float64 on the CPU before its edges are read off and handed to SAT.
Never read a hard geometric claim off a float32 GPU tensor.

Shapes: coordinates are (B, n, 2). The abstract graph (edge_index, nonedge_index)
is SHARED across the batch -- B different embeddings of the SAME graph -- so edge
tensors are (E, 2) long and broadcast over the batch. Per-batch losses are returned
as (B,) vectors; because the B optimizations are independent, `loss.sum().backward()`
produces the correct per-batch gradients with no cross-talk.
"""
from __future__ import annotations

import torch


def pick_device(prefer_gpu: bool = True) -> torch.device:
    """The compute device: cuda if available and preferred, else cpu."""
    if prefer_gpu and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


# --------------------------------------------------------------------------
# geometry (batched)
# --------------------------------------------------------------------------
def batched_pdist2(coords: torch.Tensor) -> torch.Tensor:
    """(B, n, 2) coords -> (B, n, n) squared Euclidean distances."""
    diff = coords[:, :, None, :] - coords[:, None, :, :]
    return (diff * diff).sum(-1)


def _gather_pairs(coords: torch.Tensor, index: torch.Tensor) -> torch.Tensor:
    """coords (B, n, 2), index (E, 2) long -> (B, E) squared distances of the pairs."""
    i, j = index[:, 0], index[:, 1]
    pi = coords[:, i, :]            # (B, E, 2)
    pj = coords[:, j, :]            # (B, E, 2)
    return ((pi - pj) ** 2).sum(-1)  # (B, E)


def batched_edge_residual(coords: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
    """Per-batch mean (|p_i - p_j|^2 - 1)^2 over edges that SHOULD be unit. -> (B,)."""
    if edge_index.numel() == 0:
        return coords.new_zeros(coords.shape[0])
    d2 = _gather_pairs(coords, edge_index)         # (B, E)
    return ((d2 - 1.0) ** 2).mean(dim=1)            # (B,)


def batched_nonedge_margin(coords: torch.Tensor, nonedge_index: torch.Tensor,
                           delta: float = 0.05, eps: float = 1e-9) -> torch.Tensor:
    """Per-batch hinge keeping NON-edges >= delta away from unit distance. -> (B,).

    This is the term the legacy realizer omits (see diff_udg.nonedge_margin_loss):
    a small edge residual with a non-edge sitting at distance 1 is NOT a legal UDG
    of the intended graph -- it has an accidental extra unit edge that can change chi.
    """
    if nonedge_index.numel() == 0:
        return coords.new_zeros(coords.shape[0])
    d = torch.sqrt(_gather_pairs(coords, nonedge_index) + eps)   # (B, E')
    viol = torch.relu(delta - (d - 1.0).abs())
    return (viol ** 2).mean(dim=1)                               # (B,)


def batched_soft_adjacency(coords: torch.Tensor, tau: float = 0.06,
                           eps: float = 1e-9) -> torch.Tensor:
    """Differentiable adjacency a_ij = exp(-(d_ij-1)^2 / 2 tau^2), zero diagonal.

    (B, n, 2) -> (B, n, n). The graph structure as a smooth function of coordinates.
    """
    d = torch.sqrt(batched_pdist2(coords) + eps)                 # (B, n, n)
    a = torch.exp(-((d - 1.0) ** 2) / (2 * tau * tau))
    n = coords.shape[1]
    eye = torch.eye(n, dtype=a.dtype, device=a.device)
    return a * (1.0 - eye)                                        # zero diagonal


def batched_coloring_loss(logits: torch.Tensor, adjacency: torch.Tensor) -> torch.Tensor:
    """Expected monochromatic-edge weight under a soft coloring, per batch. -> (B,).

    logits: (B, n, k). adjacency: (B, n, n) nonneg. p = softmax(logits); the
    probability that endpoints share a color is <p_i, p_j>. Returns adjacency-weighted
    mean in [0, 1]; 0 <=> a proper (soft) k-coloring exists. This is a HEURISTIC
    upper witness only -- it never certifies chi > k; SAT does that.
    """
    p = torch.softmax(logits, dim=2)                             # (B, n, k)
    same = torch.bmm(p, p.transpose(1, 2))                       # (B, n, n)
    num = (adjacency * same).sum(dim=(1, 2))                     # (B,)
    den = adjacency.sum(dim=(1, 2)) + 1e-12
    return num / den


def batched_spread_penalty(coords: torch.Tensor, floor: float = 0.5) -> torch.Tensor:
    """Anti-collapse: penalize pairs closer than sqrt(floor). Per batch. -> (B,).

    Keeps the adversarial outer player from cheating by stacking vertices (all
    distances 0) or scattering them to infinity (all a_ij -> 0).
    """
    B, n, _ = coords.shape
    d2 = batched_pdist2(coords)
    eye = torch.eye(n, dtype=d2.dtype, device=d2.device)[None] * 1e6
    close = torch.relu(floor - (d2 + eye))
    return close.sum(dim=(1, 2)) / (n * (n - 1) + 1)


# --------------------------------------------------------------------------
# batched optimization driver
# --------------------------------------------------------------------------
def batched_adam(params, loss_vec_fn, steps: int = 2000, lr: float = 0.02,
                 log_every: int = 0):
    """Adam on `params` minimizing loss_vec_fn() -> (B,) per-batch losses.

    The B optimizations are independent, so summing the per-batch losses before
    backward gives correct per-batch gradients (no cross-batch coupling). Returns
    the final per-batch loss vector (B,) detached on CPU.
    """
    opt = torch.optim.Adam(params, lr=lr)
    last = None
    for t in range(steps):
        opt.zero_grad(set_to_none=True)
        loss_vec = loss_vec_fn()
        loss_vec.sum().backward()
        opt.step()
        if log_every and (t % log_every == 0 or t == steps - 1):
            with torch.no_grad():
                lv = loss_vec.detach()
                print(f"    step {t:5d}  min {lv.min():.3e}  "
                      f"median {lv.median():.3e}  max {lv.max():.3e}")
        last = loss_vec
    return last.detach().to("cpu")


# --------------------------------------------------------------------------
# abstract graph -> device tensors
# --------------------------------------------------------------------------
def edges_to_index(edges, device, dtype=torch.long) -> torch.Tensor:
    if not edges:
        return torch.zeros((0, 2), dtype=dtype, device=device)
    return torch.tensor([[i, j] for (i, j) in edges], dtype=dtype, device=device)


def nonedges_index(n, edges, device) -> torch.Tensor:
    es = {(min(i, j), max(i, j)) for (i, j) in edges}
    out = [[i, j] for i in range(n) for j in range(i + 1, n) if (i, j) not in es]
    if not out:
        return torch.zeros((0, 2), dtype=torch.long, device=device)
    return torch.tensor(out, dtype=torch.long, device=device)


def random_coords(B: int, n: int, device, dtype=torch.float32, scale: float = 1.5,
                  generator: torch.Generator | None = None) -> torch.Tensor:
    """(B, n, 2) random initial embeddings, requires_grad. Seeds differ per batch."""
    c = torch.randn(B, n, 2, device=device, dtype=dtype, generator=generator) * scale
    c.requires_grad_(True)
    return c
