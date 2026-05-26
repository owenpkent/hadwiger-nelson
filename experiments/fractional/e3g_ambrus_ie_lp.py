r"""e3g: Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023 inclusion-exclusion LP for m_1(R^2).

Architecture 3 / continuous side. Implements the "common generalization" of
the fractional-chromatic and harmonic-analysis approaches (Ambrus et al. 2023,
arXiv:2207.14179). NOT a 2-particle SDP (Bachoc-Nebe-OFV 2009 explicitly
says their SDP at n=2 is no better than the OFV 1-particle LP); it is a
refined 1-particle LP with inclusion-exclusion atom constraints from a finite
configuration.

The LP (Lemma 1 of Ambrus 2023). Let A be a periodic, measurable, 1-avoiding
set in R^2 with autocorrelation f(x) = delta(A intersect (A - x)). Let
X = {x_1, ..., x_n} be a finite configuration. For each sign pattern
eps in {+1, -1}^n, define the atom

  a_X(eps) = delta( intersection_{i: eps_i=1} (A - x_i) intersect
                    intersection_{i: eps_i=-1} (A - x_i)^c )

Properties:
  (ieP) a_X(eps) >= 0
  (ieI) a_X(eps) = 0 if {x_i : eps_i = +1} contains two points at distance 1
  (ieT) sum_{eps} a_X(eps) = 1
  (ie1) sum_{eps: eps_i = +1} a_X(eps) = delta(A) for each i
  (ie2) sum_{eps: eps_i = eps_j = +1} a_X(eps) = f(x_i - x_j) for each pair (i, j)

Combined with the harmonic-analysis constraint that f is positive-definite
(Bochner: f(r) = integral J_0(2 pi r s) d nu(s) with nu >= 0), and that
f(1) = 0 (avoidance), we get a single LP whose maximum value of delta(A)
upper-bounds m_1(R^2).

In primal form:

  max d
  s.t.
    a_I >= 0 for each I in IndependentSets(G(X))    (one variable per indep set)
    c_k >= 0 for each frequency s_k
    sum a_I = 1                                      (ieT, normalized)
    sum_{I containing v_i} a_I = d for each vertex v_i  (ie1)
    sum_{I containing pair (v_i, v_j)} a_I = sum_k c_k J_0(2 pi ||x_i - x_j|| s_k)
                                                     (ie2, pair v_i,v_j non-edge)
    sum_k c_k = d                                    (f(0) = d)
    sum_k c_k J_0(2 pi s_k) = 0                      (f(1) = 0)

  Output: m_1(R^2) <= d_opt.

For the Moser spindle (n=7, alpha=2): trivially d_opt <= 2/7 ~= 0.286 by the
fractional-chromatic argument (m_1 <= alpha(G)/|G|), and the LP should not be
worse. For richer configurations Ambrus et al. push down to 0.2470 with a
23-point configuration found by beam search.

We start with sanity checks (Moser, then small extensions) and build the
framework for trying larger configurations.
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

from experiments.fractional.e3c_ofv_lp_dual import omega_n, chi_m_integer, CACHE
from experiments.fractional.e3e_moser_constraint import moser_spindle_vertices


def unit_distance_subgraph(X: np.ndarray, tol: float = 1e-9) -> set[tuple[int, int]]:
    """Compute set of unit-distance edges (i, j) with i < j in the point set X."""
    edges = set()
    n = X.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if abs(float(np.linalg.norm(X[i] - X[j])) - 1.0) < tol:
                edges.add((i, j))
    return edges


def enumerate_independent_sets(n: int, edges: set[tuple[int, int]], max_size: int | None = None) -> list[frozenset[int]]:
    """Enumerate all independent subsets of the graph (n vertices, given edges).

    Optimization: use a recursive enumeration that prunes by checking edges.
    """
    adj = [set() for _ in range(n)]
    for (i, j) in edges:
        adj[i].add(j)
        adj[j].add(i)

    indep_sets = [frozenset()]    # always include empty set

    def extend(current: frozenset, next_v: int):
        if max_size is not None and len(current) >= max_size:
            return
        for v in range(next_v, n):
            if not (current & adj[v]):
                new = current | {v}
                indep_sets.append(new)
                extend(new, v + 1)

    extend(frozenset(), 0)
    return indep_sets


def build_ie_lp(
    X: np.ndarray,
    n_freq: int = 200,
    freq_max: float = 5.0,
    indep_max_size: int | None = None,
) -> dict:
    """Build and solve the inclusion-exclusion LP for a given point set X.

    Returns dict with optimal m_1 bound, LP details, etc.
    """
    n = X.shape[0]
    edges = unit_distance_subgraph(X)
    indep_sets = enumerate_independent_sets(n, edges, max_size=indep_max_size)
    K = len(indep_sets)

    # Map vertex -> list of indep-set indices containing it.
    vertex_indep_idx = [[] for _ in range(n)]
    pair_indep_idx: dict[tuple[int, int], list[int]] = {}
    for I_idx, I in enumerate(indep_sets):
        for v in I:
            vertex_indep_idx[v].append(I_idx)
        for v1, v2 in combinations(sorted(I), 2):
            pair = (v1, v2) if v1 < v2 else (v2, v1)
            pair_indep_idx.setdefault(pair, []).append(I_idx)

    # Frequency grid for Bessel decomposition.
    freqs = np.linspace(0.001, freq_max, n_freq)
    # J_0(2 pi r s_k) for various r values:
    # we need r = 1 (avoidance), r = 0 (auto: J_0(0) = 1), r = ||x_i - x_j|| for each non-edge pair.

    # Collect distinct non-edge distances appearing in pairs.
    pair_distances = {}    # (i, j) -> ||x_i - x_j||
    for (i, j) in combinations(range(n), 2):
        if (i, j) in edges:
            continue
        d = float(np.linalg.norm(X[i] - X[j]))
        pair_distances[(i, j)] = d

    # CVXPY variables.
    a = cp.Variable(K, nonneg=True)
    c = cp.Variable(n_freq, nonneg=True)
    d = cp.Variable()    # d = delta(A), what we maximize

    # Precompute Bessel evaluations.
    J0_at_pair = {}    # pair -> vector of length n_freq with J_0(2 pi d_pair s_k)
    for pair, dist in pair_distances.items():
        J0_at_pair[pair] = j0(2.0 * np.pi * dist * freqs)
    J0_at_1 = j0(2.0 * np.pi * 1.0 * freqs)
    # J_0(0) = 1 implicitly (we use this via the c sum = d constraint).

    constraints = []
    # (ieT): sum a = 1
    constraints.append(cp.sum(a) == 1)
    # (ie1): sum a over indep sets containing v_i = d
    for v in range(n):
        if vertex_indep_idx[v]:
            constraints.append(cp.sum(a[vertex_indep_idx[v]]) == d)
        else:
            # vertex appears in no indep set (impossible for indep singleton always exists)
            constraints.append(d == 0)
    # (ie2): sum a over indep sets containing pair (v_i, v_j) = Bessel sum at d_ij
    for pair, dist in pair_distances.items():
        if pair in pair_indep_idx and pair_indep_idx[pair]:
            constraints.append(cp.sum(a[pair_indep_idx[pair]]) == J0_at_pair[pair] @ c)
        else:
            # Pair never appears in any independent set => left side is 0
            constraints.append(J0_at_pair[pair] @ c == 0)
    # f(1) = 0:
    constraints.append(J0_at_1 @ c == 0)
    # f(0) = sum c = d:
    constraints.append(cp.sum(c) == d)

    prob = cp.Problem(cp.Maximize(d), constraints)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0

    return {
        "n_points": n,
        "n_edges": len(edges),
        "n_independent_sets": K,
        "n_freq": n_freq,
        "max_indep_size": max(len(I) for I in indep_sets),
        "alpha_G": max(len(I) for I in indep_sets),
        "status": prob.status,
        "m1_bound": float(d.value) if d.value is not None else None,
        "solve_time_s": elapsed,
    }


def test_moser_spindle():
    """Sanity check: IE-LP on Moser spindle should give m_1 <= 2/7 = 0.2857
    (the fractional chromatic bound), and might be tighter via positivity of f."""
    V = moser_spindle_vertices()
    r = build_ie_lp(V)
    print(f"\nMoser spindle (n=7):")
    print(f"  unit-distance edges: {r['n_edges']}")
    print(f"  independent sets: {r['n_independent_sets']}  (alpha={r['alpha_G']})")
    print(f"  m_1 bound:   {r['m1_bound']:.6f}  (vs trivial 2/7 = {2/7:.6f})")
    print(f"  chi_m:       {1/r['m1_bound']:.4f}  (int {chi_m_integer(r['m1_bound'])})")
    print(f"  solve time:  {r['solve_time_s']*1000:.0f} ms")
    return r


def test_moser_with_offset():
    """Try Moser spindle translated to put a vertex closer to the LP-binding shell."""
    V = moser_spindle_vertices()
    # Translate so the centroid is at origin (each vertex r_i smaller).
    V_centered = V - V.mean(axis=0)
    r = build_ie_lp(V_centered)
    print(f"\nMoser spindle (centroid at origin):")
    print(f"  m_1 bound:   {r['m1_bound']:.6f}")
    print(f"  chi_m:       {1/r['m1_bound']:.4f}")
    return r


def test_extended_configurations():
    """Try a few small extended configurations: Moser + extra points."""
    V_moser = moser_spindle_vertices()
    results = []

    # Moser + central origin (already has (0,0) at A).
    # Moser + reflection of D and D' across origin?
    # For exploration, try Moser + symmetric copies.
    sqrt3 = math.sqrt(3.0)

    # Configuration: 7-point Moser + 6 hexagonal lattice points at unit distance.
    hexagon = np.array([
        [1.0, 0.0],
        [0.5, sqrt3 / 2],
        [-0.5, sqrt3 / 2],
        [-1.0, 0.0],
        [-0.5, -sqrt3 / 2],
        [0.5, -sqrt3 / 2],
    ])
    V_hex = np.vstack([V_moser, hexagon])
    # Dedup
    V_hex_uniq = []
    seen = set()
    for p in V_hex:
        k = (round(float(p[0]), 8), round(float(p[1]), 8))
        if k not in seen:
            seen.add(k)
            V_hex_uniq.append(p)
    V_hex_uniq = np.array(V_hex_uniq)
    print(f"\nMoser + hexagon ({V_hex_uniq.shape[0]} points after dedup):")
    if V_hex_uniq.shape[0] <= 20:
        r = build_ie_lp(V_hex_uniq)
        print(f"  edges: {r['n_edges']}")
        print(f"  independent sets: {r['n_independent_sets']}  (alpha={r['alpha_G']})")
        print(f"  m_1 bound: {r['m1_bound']:.6f}")
        print(f"  chi_m: {1/r['m1_bound']:.4f}  (int {chi_m_integer(r['m1_bound'])})")
        print(f"  solve time: {r['solve_time_s']*1000:.0f} ms")
        results.append(("moser + hexagon", r))

    return results


def main():
    print("e3g: Ambrus-style inclusion-exclusion LP for m_1(R^2)")
    print("=" * 78)
    moser_result = test_moser_spindle()
    moser_centered = test_moser_with_offset()
    extended_results = test_extended_configurations()

    print()
    print("=" * 78)
    print("Summary:")
    print("=" * 78)
    print(f"  e3e (OFV + Moser at translations): m_1 <= 0.2619")
    print(f"  e3g IE-LP on Moser (this expt):    m_1 <= {moser_result['m1_bound']:.4f}")
    if extended_results:
        for name, r in extended_results:
            print(f"  e3g IE-LP {name}:               m_1 <= {r['m1_bound']:.4f}")
    print(f"  Ambrus et al. 2023 published:      m_1 <= 0.2470")

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3g_ambrus_ie_lp.json"
    with out_path.open("w") as f:
        json.dump({
            "experiment": "e3g_ambrus_ie_lp",
            "moser_result": moser_result,
            "moser_centered": moser_centered,
            "extended_results": [{"name": name, "result": r} for name, r in extended_results],
        }, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
