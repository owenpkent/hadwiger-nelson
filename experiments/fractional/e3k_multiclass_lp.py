r"""e3k: multi-class (joint k-coloring) autocorrelation LP for chi_m(R^2).

Architecture 2/3, the measurable frontier NOT provably capped at 5.

Motivation. The single-class density LP (e3g/e3i/e3j) bounds m_1(R^2), the max
density of ONE 1-avoiding set, giving chi_m >= 1/m_1. That route is provably
capped at chi_m >= 5: Croft's explicit avoiding set has density 0.22936 > 1/5,
so 1/m_1 <= 4.36 < 5 and the single-class bound can never reach 6 (LEARNINGS
L36; sources/notes/08, 11). To go past 5 the argument must use the JOINT
structure of all color classes at once, not one class's density.

The multi-class object. A measurable proper k-coloring partitions R^2 into k
sets A_1, ..., A_k, each 1-avoiding (each autocorrelation f_c vanishes at
distance 1), disjoint, covering. Fix a finite configuration X = {x_0, ..., x_{n-1}}
with unit-distance graph G(X). Translating the coloring over R^2 induces a
probability distribution over the local color-patterns sigma: X -> {1..k} that
the configuration sees. Because A_c is 1-avoiding, a pattern sigma can only occur
if it is a PROPER coloring of G(X) (unit-distance config points get distinct
colors). So:

  a_sigma := density of points x such that x + x_i lies in color sigma(i) for all i

is supported on proper k-colorings sigma of G(X), with a_sigma >= 0 and
sum_sigma a_sigma = 1. The per-color autocorrelation is the pair-marginal

  f_c(x_i - x_j) = density of x with x+x_i, x+x_j both in A_c
                 = sum_{sigma: sigma(i)=sigma(j)=c} a_sigma.

By Bochner (rotation-averaged), f_c is positive-definite:
  f_c(r) = integral_0^infty J_0(2 pi r s) d nu_c(s),  nu_c >= 0,
with f_c(0) = delta(A_c) = sum_j nu_c(s_j) and f_c(1) = 0 (avoidance).

The LP. Variables a_sigma >= 0 (proper k-colorings) and nu_{c,j} >= 0 (Bochner
mass per color c, frequency s_j). Constraints:
  (N)  sum_sigma a_sigma = 1
  (D)  for each color c:  sum_{sigma: sigma(x_0)=c} a_sigma = sum_j nu_{c,j}      (= f_c(0))
  (P)  for each color c and non-edge pair (i,j):
         sum_{sigma: sigma(i)=sigma(j)=c} a_sigma = sum_j nu_{c,j} J_0(2 pi ||x_i-x_j|| s_j)
  (A)  for each color c:  sum_j nu_{c,j} J_0(2 pi s_j) = 0                        (f_c(1) = 0)

If this system is INFEASIBLE for k colors on some configuration X, then no
measurable k-coloring of R^2 exists, i.e. chi_m(R^2) >= k+1.

Robust detection. Pure LP feasibility is brittle numerically, so we run a
Phase-1: put a free slack s_{c,(i,j)} on each (P) coupling and minimize
sum |s|. The minimum is 0 iff the coloring-marginals are realizable by
Bochner-positive autocorrelations. A strictly positive minimum is a quantitative
infeasibility margin (=> chi_m >= k+1).

Validation target. k=4 on a configuration rich enough to force chi_m >= 5
(the Ambrus 23-point config) should be INFEASIBLE (margin > 0), reproducing the
known bound from the joint angle. k=4 on a too-small config (Moser spindle)
should be FEASIBLE (margin 0). k=5 on any config is the open frontier toward
chi_m >= 6.

Scaling note. This proof-of-concept enumerates proper k-colorings explicitly,
which is fine for small configs but explodes for the 23-point config. The
principled scalable version is a Lasserre / moment relaxation over pairwise
color-marginals (de Laat-Vallentin 2015, in sources/), which avoids enumeration;
that is the next step if the enumeration barrier blocks validation.
"""

from __future__ import annotations

import json
import math
import pathlib
import time
from itertools import combinations

import cvxpy as cp
import numpy as np
from scipy.special import j0

from experiments.fractional.e3c_ofv_lp_dual import chi_m_integer, CACHE
from experiments.fractional.e3e_moser_constraint import moser_spindle_vertices
from experiments.fractional.e3g_ambrus_ie_lp import unit_distance_subgraph


def enumerate_proper_colorings(
    n: int, edges: set[tuple[int, int]], k: int, cap: int = 300_000
) -> tuple[list[tuple[int, ...]] | None, int]:
    """Backtracking enumeration of proper k-colorings of the graph (vertices 0..n-1).

    Returns (list_of_colorings, count). If the count would exceed `cap`, returns
    (None, cap+1) to signal the enumeration is intractable for this approach.
    Color symmetry is NOT quotiented (the LP needs the full set), but vertex 0 is
    pinned to color 0 to remove the trivial k-fold relabeling overcount; the LP's
    per-color constraints are written symmetrically so pinning v0 is valid only if
    we also allow all colors on v0. We therefore do NOT pin, and rely on `cap`.
    """
    adj = [set() for _ in range(n)]
    for (i, j) in edges:
        adj[i].add(j)
        adj[j].add(i)

    colorings: list[tuple[int, ...]] = []
    coloring = [-1] * n

    def backtrack(v: int) -> bool:
        if len(colorings) > cap:
            return False
        if v == n:
            colorings.append(tuple(coloring))
            return True
        for col in range(k):
            if all(coloring[u] != col for u in adj[v] if u < v):
                coloring[v] = col
                if not backtrack(v + 1):
                    coloring[v] = -1
                    return False
                coloring[v] = -1
        return True

    ok = backtrack(0)
    if not ok or len(colorings) > cap:
        return None, len(colorings)
    return colorings, len(colorings)


def build_multiclass_lp(
    X: np.ndarray,
    k: int,
    n_freq: int = 200,
    freq_max: float = 5.0,
    coloring_cap: int = 300_000,
) -> dict:
    """Build and solve the multi-class Phase-1 LP for k colors on configuration X.

    Returns a dict with the infeasibility margin (min sum|slack|): 0.0 means a
    measurable k-coloring of the local patterns is consistent (no obstruction
    found); > 0 (strictly) means chi_m(R^2) >= k+1 from this configuration.
    """
    n = X.shape[0]
    edges = unit_distance_subgraph(X)

    colorings, count = enumerate_proper_colorings(n, edges, k, cap=coloring_cap)
    if colorings is None:
        return {
            "n_points": n,
            "n_edges": len(edges),
            "k": k,
            "status": "ENUMERATION_INTRACTABLE",
            "proper_colorings_lower_bound": count,
            "note": "proper k-coloring count exceeds cap; need Lasserre marginal relaxation",
        }
    M = len(colorings)
    col_arr = np.array(colorings, dtype=np.int8)  # (M, n)

    # Non-edge pairs and their distances.
    pair_dist: dict[tuple[int, int], float] = {}
    for (i, j) in combinations(range(n), 2):
        if (i, j) in edges:
            continue
        pair_dist[(i, j)] = float(np.linalg.norm(X[i] - X[j]))

    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)
    J0_pair = {p: j0(2.0 * np.pi * d * freqs) for p, d in pair_dist.items()}

    a = cp.Variable(M, nonneg=True)
    nu = cp.Variable((k, n_freq), nonneg=True)

    cons = [cp.sum(a) == 1]

    # (D) delta_c = f_c(0): color-c marginal at vertex 0 equals Bochner mass.
    for c in range(k):
        mask0 = (col_arr[:, 0] == c)
        cons.append(cp.sum(a[np.where(mask0)[0]]) == cp.sum(nu[c, :]))

    # (A) f_c(1) = 0.
    for c in range(k):
        cons.append(J0_at_1 @ nu[c, :] == 0)

    # (P) pair-marginal couplings, with a free slack per (color, pair).
    slacks = []
    for c in range(k):
        for (i, j), Jvec in J0_pair.items():
            same = (col_arr[:, i] == c) & (col_arr[:, j] == c)
            idx = np.where(same)[0]
            lhs = cp.sum(a[idx]) if idx.size else cp.Constant(0.0)
            rhs = Jvec @ nu[c, :]
            s = cp.Variable()
            slacks.append(s)
            cons.append(lhs - rhs == s)

    obj = cp.Minimize(cp.sum([cp.abs(s) for s in slacks]))
    prob = cp.Problem(obj, cons)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0

    margin = float(prob.value) if prob.value is not None else None
    return {
        "n_points": n,
        "n_edges": len(edges),
        "k": k,
        "proper_colorings": M,
        "n_nonedge_pairs": len(pair_dist),
        "n_freq": n_freq,
        "status": prob.status,
        "infeasibility_margin": margin,
        "implies_chi_m_geq": (k + 1) if (margin is not None and margin > 1e-7) else None,
        "solve_time_s": elapsed,
    }


def run_moser(k: int) -> dict:
    V = moser_spindle_vertices()
    r = build_multiclass_lp(V, k=k)
    print(f"\nMoser spindle, k={k}:")
    print(f"  proper {k}-colorings: {r.get('proper_colorings')}  edges={r['n_edges']}")
    print(f"  status: {r['status']}  margin: {r.get('infeasibility_margin')}")
    print(f"  implies chi_m >= {r.get('implies_chi_m_geq')}  ({r.get('solve_time_s', 0)*1000:.0f} ms)")
    return r


def run_ambrus(k: int, coloring_cap: int = 300_000) -> dict:
    """Load the Ambrus 23-point config (floats) and run the multi-class LP."""
    try:
        from experiments.fractional.e3i_ambrus_reproduce import (
            load_config, parse_points_exact, points_to_float_array,
        )
        cfg = load_config()
        pts = parse_points_exact(cfg)
        X = points_to_float_array(pts)
    except Exception as e:  # noqa: BLE001
        return {"status": "CONFIG_LOAD_FAILED", "error": repr(e), "k": k}
    r = build_multiclass_lp(X, k=k, coloring_cap=coloring_cap)
    print(f"\nAmbrus X_23, k={k}:")
    print(f"  status: {r['status']}")
    if r["status"] == "ENUMERATION_INTRACTABLE":
        print(f"  proper {k}-colorings exceed cap ({r['proper_colorings_lower_bound']}+).")
        print(f"  => need the Lasserre marginal relaxation (de Laat-Vallentin); see docstring.")
    else:
        print(f"  proper {k}-colorings: {r.get('proper_colorings')}")
        print(f"  margin: {r.get('infeasibility_margin')}  implies chi_m >= {r.get('implies_chi_m_geq')}")
    return r


def main():
    print("e3k: multi-class (joint k-coloring) autocorrelation LP for chi_m(R^2)")
    print("=" * 78)
    print("Sanity (Moser spindle, too small to force >=5): expect margin 0 (feasible).")
    moser4 = run_moser(4)
    moser5 = run_moser(5)
    print("\nValidation attempt (Ambrus X_23 forces chi_m >= 5):")
    print("  k=4 SHOULD be infeasible (margin > 0) if the machinery + config suffice.")
    ambrus4 = run_ambrus(4)
    ambrus5 = run_ambrus(5)

    CACHE.mkdir(exist_ok=True)
    out = CACHE / "e3k_multiclass_lp.json"
    with out.open("w") as f:
        json.dump(
            {
                "experiment": "e3k_multiclass_lp",
                "moser_k4": moser4,
                "moser_k5": moser5,
                "ambrus_k4": ambrus4,
                "ambrus_k5": ambrus5,
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out}")


if __name__ == "__main__":
    raise SystemExit(main())
