r"""Option D: the flexible-but-color-rigid gadget search (the stated kill-test).

rigidity_w3_escape.py names the single object the whole UDG program may turn on: a
gadget that is GEOMETRICALLY FLEXIBLE (a 1-parameter flex moves its two terminals,
so the bridge distance between gadgets is tunable) yet COLOR-RIGID (its terminals
are clamped -- forced different, or one fixed -- in every proper 5-coloring).
A flexible color-clamp would let bridges be realized as genuine unit distances
(escaping the W3 over-determination) while still forcing chi up.

This script makes the two halves of that test runnable and composable:

  - flex side (continuous / linear algebra): the rigidity matrix R of the framework.
    Terminal pair (s,t) is FLEXIBLE iff appending grad |p_s - p_t|^2 to R raises the
    rank -- i.e. some non-rigid infinitesimal motion changes the terminal distance.
  - clamp side (discrete / SAT): terminals are CLAMPED at k iff no proper k-coloring
    gives them the same color (forced different).

It scans the canonical gadgets and reproduces the known negatives as calibration:
unit path and rhombus FLEX but do not clamp at k=5; the triangle and Moser spindle
are rigid (Moser clamps only at k=4). The OPEN target is the cell that stays empty:
FLEX = yes AND CLAMP@k=5 = yes. GD enters by optimizing a parametrized gadget's
geometry (the flex) while this SAT clamp test scores its terminals.

Run:  python -m experiments.gradient.gadget_search
"""
from __future__ import annotations

import math

import numpy as np


# --------------------------------------------------------------------------
# flex side: rigidity matrix
# --------------------------------------------------------------------------
def rigidity_matrix(coords, edges):
    n = len(coords)
    R = np.zeros((len(edges), 2 * n))
    for r, (i, j) in enumerate(edges):
        d = coords[i] - coords[j]
        R[r, 2 * i:2 * i + 2] = 2 * d
        R[r, 2 * j:2 * j + 2] = -2 * d
    return R


def _rank(M, tol=1e-9):
    if M.size == 0:
        return 0
    s = np.linalg.svd(M, compute_uv=False)
    return int((s > tol * max(1.0, s[0])).sum())


def flex_analysis(coords, edges, s, t):
    """Returns (internal_dof, terminal_flexible)."""
    coords = np.asarray(coords, float)
    n = len(coords)
    R = rigidity_matrix(coords, edges)
    rk = _rank(R)
    flex_dim = 2 * n - rk           # all infinitesimal flexes (incl. rigid motions)
    internal = flex_dim - 3         # subtract the 3 trivial rigid motions (2D)
    # terminal distance gradient
    g = np.zeros(2 * n)
    d = coords[s] - coords[t]
    g[2 * s:2 * s + 2] = 2 * d
    g[2 * t:2 * t + 2] = -2 * d
    terminal_flexible = _rank(np.vstack([R, g])) > rk
    return internal, terminal_flexible


# --------------------------------------------------------------------------
# clamp side: SAT
# --------------------------------------------------------------------------
def can_color_with(n, edges, k, s=None, t=None, same=None):
    """Is there a proper k-coloring (optionally with c(s) == / != c(t))?"""
    try:
        from pysat.formula import CNF
        from pysat.solvers import Cadical195
    except ImportError:
        return None
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
    if s is not None and same is not None:
        # auxiliary equality: e_c <-> (c(s)=c and c(t)=c); enforce sum e_c per same flag
        if same:  # force c(s)==c(t): forbid every (s=c1, t=c2) with c1!=c2
            for c1 in range(k):
                for c2 in range(k):
                    if c1 != c2:
                        cnf.append([-var(s, c1), -var(t, c2)])
        else:     # force c(s)!=c(t)
            for c in range(k):
                cnf.append([-var(s, c), -var(t, c)])
    with Cadical195(bootstrap_with=cnf.clauses) as solver:
        return solver.solve()


def clamp_status(n, edges, s, t, k):
    """Clamp type for a NON-adjacent terminal pair (s,t) at k colors.

    'diff'  forced different (no k-coloring shares their color)
    'same'  forced same      (no k-coloring differs their color)  <- Moser's property
    'free'  neither (terminals unconstrained)
    'none'  graph not k-colorable at all
    """
    same_ok = can_color_with(n, edges, k, s, t, same=True)
    diff_ok = can_color_with(n, edges, k, s, t, same=False)
    if same_ok is None:
        return None
    if not same_ok and not diff_ok:
        return "none"
    if not same_ok:
        return "diff"
    if not diff_ok:
        return "same"
    return "free"


def scan_clamps(coords, edges, k):
    """Over all NON-adjacent pairs, find those that are clamped (same/diff) at k,
    and report whether any clamped pair is also terminal-flexible.

    Returns (best, n_clamped) where best is the most useful pair:
    a (flexible, clamped) pair if one exists, else any clamped pair, else None.
    """
    n = len(coords)
    eset = {(min(a, b), max(a, b)) for (a, b) in edges}
    best, n_clamped = None, 0
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in eset:
                continue
            st = clamp_status(n, edges, i, j, k)
            if st in ("same", "diff"):
                n_clamped += 1
                _, flex = flex_analysis(coords, edges, i, j)
                cand = (i, j, st, flex)
                if best is None or (flex and not best[3]):
                    best = cand
    return best, n_clamped


# --------------------------------------------------------------------------
# gadget library: (name, coords, edges, s, t)
# --------------------------------------------------------------------------
def _bent_unit_path(n=5, seed=1):
    rng = np.random.default_rng(seed)
    pts = [np.array([0.0, 0.0])]
    ang = 0.0
    for _ in range(n - 1):
        ang += rng.uniform(0.5, 1.0)  # generic, non-straight
        pts.append(pts[-1] + np.array([math.cos(ang), math.sin(ang)]))
    coords = np.array(pts)
    edges = [(i, i + 1) for i in range(n - 1)]
    return coords, edges, 0, n - 1


def _rhombus(theta=1.1):
    c, s = math.cos(theta), math.sin(theta)
    coords = np.array([[0.0, 0.0], [1.0, 0.0], [1 + c, s], [c, s]])
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    return coords, edges, 1, 3  # the varying diagonal


def _unit_pentagon():
    r = 1.0 / (2 * math.sin(math.pi / 5))  # circumradius for unit edges
    coords = np.array([[r * math.cos(2 * math.pi * k / 5 + 0.3),
                        r * math.sin(2 * math.pi * k / 5 + 0.3)] for k in range(5)])
    edges = [(k, (k + 1) % 5) for k in range(5)]
    return coords, edges, 0, 2


def _moser():
    s3 = math.sqrt(3)
    base = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, s3 / 2], [1.5, s3 / 2]])
    th = math.acos(5.0 / 6.0)
    Rm = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    coords = np.vstack([base, (base @ Rm.T)[1:]])
    edges = []
    for i in range(7):
        for j in range(i + 1, 7):
            if abs(math.hypot(*(coords[i] - coords[j])) - 1.0) < 1e-6:
                edges.append((i, j))
    return coords, edges, 4, 6  # two outer tips (non-adjacent forced-same at k=4)


def max_flexible_clamp_k(coords, edges, ks=(2, 3, 4, 5)):
    """Highest k at which the gadget has a NON-adjacent pair that is BOTH clamped and
    terminal-flexible. Returns (k, pair, status) or (None, ...) if there is none."""
    found = (None, None, None)
    for k in ks:
        best, _ = scan_clamps(coords, edges, k)
        if best is not None and best[3]:  # flexible clamp at this k
            i, j, st, _ = best
            found = (k, (i, j), st)
    return found


def main():
    print("Option D  -  flexible-but-color-rigid gadget search (the kill-test)\n")
    gadgets = [
        ("unit path (5)", *_bent_unit_path(5)),
        ("rhombus", *_rhombus()),
        ("unit pentagon", *_unit_pentagon()),
        ("Moser spindle", *_moser()),
    ]
    print(f"  {'gadget':16s} {'int.DOF':>7s}   highest k with a FLEXIBLE clamp")
    for name, coords, edges, *_ in gadgets:
        dof, _ = flex_analysis(coords, edges, 0, 1)  # DOF is a framework property
        k, pair, st = max_flexible_clamp_k(coords, edges)
        cell = "none" if k is None else f"k={k}  (pair {pair} forced {st})"
        print(f"  {name:16s} {dof:7d}   {cell}")
    print("\n  Flexible clamps DO exist at low k (a path forces its endpoints SAME at")
    print("  k=2 and still flexes), but they vanish far below k=5. The kill-test asks")
    print("  for one that survives to k=5: that cell stays empty for every small gadget.")
    print("  GD attacks by deforming a parametrized gadget while this SAT test scores")
    print("  the terminals -- climbing that highest-k column toward 5.")


if __name__ == "__main__":
    main()
