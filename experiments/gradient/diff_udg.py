r"""Differentiable unit-distance-graph primitives (torch) for HN gradient attacks.

WHY this exists. chi is integer-valued and a coloring is discrete, so there is no
global differentiable objective whose minimum *is* chi(R^2). Gradient descent is a
LOCAL, ONE-SIDED method: it can witness existence (a coloring => k-colorable; an
embedding => realizable) but never non-existence. A chi >= 6 claim still needs a
certificate (SAT UNSAT core, dual SDP). So everything here lives on the
construction/search side. It proposes objects; the SAT lemma_db certifies them.

WRONG-APPROACH-DETECTOR note. A pure soft-coloring objective (coloring_loss with a
fixed adjacency) is blind to the topology of R: it lifts unchanged to Q^2, where
chi = 2 (Woodall). It therefore cannot prove anything R^2-specific on its own. The
coordinate terms (edge_residual_loss, nonedge_margin_loss, soft_adjacency) are what
ground an objective in the Euclidean plane. Any GD attack that claims to bound
chi(R^2) MUST route through real unit distances, not abstract adjacency alone.

All tensors are float64.
"""
from __future__ import annotations

import math

import numpy as np
import torch

torch.set_default_dtype(torch.float64)


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------
def pdist2(coords: torch.Tensor) -> torch.Tensor:
    """(n,2) coords -> (n,n) squared Euclidean distances."""
    diff = coords[:, None, :] - coords[None, :, :]
    return (diff * diff).sum(-1)


def edge_residual_loss(coords: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
    """Mean (|p_i - p_j|^2 - 1)^2 over the edges that SHOULD be unit distance."""
    i, j = edge_index[:, 0], edge_index[:, 1]
    d2 = ((coords[i] - coords[j]) ** 2).sum(-1)
    return ((d2 - 1.0) ** 2).mean()


def nonedge_margin_loss(coords: torch.Tensor, nonedge_index: torch.Tensor,
                        delta: float = 0.05, eps: float = 1e-9) -> torch.Tensor:
    """Hinge keeping NON-edges away from distance 1 by at least delta.

    This is the term the legacy realizer (realizability_w3_clamp.py) omits: it only
    pulls edges to unit length and ignores non-edges that drift onto the unit circle.
    A configuration with a small edge residual but a non-edge at distance 1 is NOT a
    legal UDG of the intended graph (it has an extra unit-distance edge). Penalty is
    relu(delta - | |p_i-p_j| - 1 |)^2.
    """
    if nonedge_index.numel() == 0:
        return coords.new_zeros(())
    i, j = nonedge_index[:, 0], nonedge_index[:, 1]
    d = torch.sqrt(((coords[i] - coords[j]) ** 2).sum(-1) + eps)
    viol = torch.relu(delta - (d - 1.0).abs())
    return (viol ** 2).mean()


def soft_adjacency(coords: torch.Tensor, tau: float = 0.06, eps: float = 1e-9) -> torch.Tensor:
    """Differentiable adjacency: a_ij = exp(-(d_ij - 1)^2 / 2 tau^2), zero diagonal.

    a_ij ~ 1 when (i,j) is at unit distance, ~0 otherwise. This makes the *graph
    structure itself* a smooth function of the coordinates, which is the whole point:
    moving a vertex changes which pairs are edges, differentiably.
    """
    n = coords.shape[0]
    d = torch.sqrt(pdist2(coords) + eps)
    a = torch.exp(-((d - 1.0) ** 2) / (2 * tau * tau))
    a = a - torch.diag(torch.diagonal(a))
    return a


def coloring_loss(logits: torch.Tensor, adjacency: torch.Tensor) -> torch.Tensor:
    """Expected monochromatic-edge weight under a soft coloring.

    logits: (n, k). adjacency: (n, n) nonneg weights. p = softmax(logits); the
    probability endpoints share a color is <p_i, p_j>. Returns the adjacency-weighted
    mean, in [0, 1]. Zero => a proper k-coloring of the (soft) graph exists.
    """
    p = torch.softmax(logits, dim=1)
    same = p @ p.t()
    return (adjacency * same).sum() / (adjacency.sum() + 1e-12)


def spread_penalty(coords: torch.Tensor, eps: float = 1e-9) -> torch.Tensor:
    """Anti-collapse regularizer: penalizes pairs that get much closer than unit.

    The adversarial loop will otherwise cheat by piling vertices on top of each other
    (all distances 0) or scattering them to infinity (all a_ij = 0). This keeps the
    point cloud at a sane scale by pushing very-close pairs apart.
    """
    n = coords.shape[0]
    d2 = pdist2(coords)
    off = d2 + torch.eye(n, dtype=d2.dtype) * 1e6
    close = torch.relu(0.5 - off)  # only pairs closer than ~0.7 contribute
    return close.sum() / (n * (n - 1) + 1)


# --------------------------------------------------------------------------
# optimization helper
# --------------------------------------------------------------------------
def adam_minimize(params, loss_fn, steps=2000, lr=0.02, log_every=0):
    """Run Adam on `params` (list of leaf tensors with requires_grad) minimizing
    loss_fn() -> scalar tensor. Returns the final loss value (float)."""
    opt = torch.optim.Adam(params, lr=lr)
    last = math.inf
    for t in range(steps):
        opt.zero_grad()
        loss = loss_fn()
        loss.backward()
        opt.step()
        last = float(loss.detach())
        if log_every and t % log_every == 0:
            print(f"    step {t:5d}  loss {last:.3e}")
    return last


# --------------------------------------------------------------------------
# abstract-graph <-> tensor helpers
# --------------------------------------------------------------------------
def edges_to_index(edges) -> torch.Tensor:
    return torch.tensor([[i, j] for (i, j) in edges], dtype=torch.long)


def nonedges_index(n, edges) -> torch.Tensor:
    es = {(min(i, j), max(i, j)) for (i, j) in edges}
    out = [[i, j] for i in range(n) for j in range(i + 1, n) if (i, j) not in es]
    return torch.tensor(out, dtype=torch.long) if out else torch.zeros((0, 2), dtype=torch.long)


def max_edge_error(coords: torch.Tensor, edges) -> float:
    p = coords.detach().numpy()
    return max(abs(math.hypot(*(p[i] - p[j])) - 1.0) for (i, j) in edges) if edges else 0.0


def min_nonedge_gap(coords: torch.Tensor, n, edges) -> float:
    """min over non-edges of | distance - 1 |. Large => legal (no accidental edge)."""
    p = coords.detach().numpy()
    es = {(min(i, j), max(i, j)) for (i, j) in edges}
    gaps = [abs(math.hypot(*(p[i] - p[j])) - 1.0)
            for i in range(n) for j in range(i + 1, n) if (i, j) not in es]
    return min(gaps) if gaps else float("inf")


# --------------------------------------------------------------------------
# canonical calibration graphs (abstract edges + a TRUE realization)
# --------------------------------------------------------------------------
def moser_spindle():
    """7-vertex chi=4 UDG. Returns (n, edges, true_coords)."""
    s3 = math.sqrt(3)
    base = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, s3 / 2], [1.5, s3 / 2]])
    th = math.acos(5.0 / 6.0)
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    rot = base @ R.T
    coords = np.vstack([base, rot[1:]])  # A,B,C,D, B',C',D'
    edges = [(0, 1), (0, 2), (1, 2), (0, 3), (2, 3), (1, 4), (0, 5),
             (4, 5), (3, 6), (5, 6), (4, 6)]
    # Recompute edges from the true coords to be safe (unit distances only).
    edges = _unit_edges(coords)
    return 7, edges, coords


def triangular_lattice_patch(rings=3):
    """Hex patch of the unit triangular lattice (chi=3). Returns (n, edges, coords)."""
    a = np.array([1.0, 0.0])
    b = np.array([0.5, math.sqrt(3) / 2])
    seen = {}
    for i in range(-rings, rings + 1):
        for j in range(-rings, rings + 1):
            p = i * a + j * b
            if p @ p <= (rings + 0.1) ** 2:
                seen[(i, j)] = p
    idx = {k: n for n, k in enumerate(seen)}
    coords = np.array([seen[k] for k in seen])
    edges = _unit_edges(coords)
    return len(coords), edges, coords


def _unit_edges(coords, tol=1e-6):
    n = len(coords)
    es = []
    for i in range(n):
        for j in range(i + 1, n):
            d = math.hypot(*(coords[i] - coords[j]))
            if abs(d - 1.0) < tol:
                es.append((i, j))
    return es


def unit_triangle():
    """Equilateral unit triangle (chi=3, not 2-colorable). Returns (n, edges, coords)."""
    coords = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, math.sqrt(3) / 2]])
    return 3, [(0, 1), (1, 2), (0, 2)], coords
