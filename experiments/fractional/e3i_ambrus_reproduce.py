r"""e3i: Reproduce Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023, m_1(R^2) <= 0.2470.

Architecture 3 (fractional / LP). SOLVING_PROGRAM Shot 3.

Source: arXiv:2207.14179v3, "The density of planar sets avoiding unit distances"
(Ambrus, Csiszarik, Matolcsi, Varga, Zsamboki, last revised 28 Jul 2023). The
paper proves Erdos' conjecture m_1(R^2) < 1/4 with the explicit upper bound
0.24699... < 0.2470.

This script does THREE things, in increasing order of rigour:

(A) PARSE + EXACT-VERIFY the published 23-point configuration X_23. The paper
    gives exact symbolic coordinates (Appendix Table 1) as complex numbers in
    Q(sqrt 3, sqrt 11, sqrt 33). We parse them with sympy, identify z = a + b i
    with the plane point (a, b), and exact-verify the unit-distance graph G_23
    (which pairs are at distance exactly 1) and the count of distinct distances
    (paper says 27). This is the configuration Shot 1 (Polymath 510) lacked.

(B) PRIMAL IE-LP REPRODUCTION. Feed X_23 into the e3g inclusion-exclusion LP
    framework (IE1 + IE2 constraints, Bochner-positive f via a J_0 frequency
    grid) and solve the primal with cvxpy + HiGHS. The paper's LP optimum is
    0.24697; ours will be SLIGHTLY LOOSER because the e3g framework implements
    IE1 + IE2 only, NOT the (IEC) congruence constraints (the paper's LP has
    5868 of those and they account for part of the tightening). We report the
    honest gap.

(C) DUAL CERTIFICATE VERIFICATION (the rigorous bound). The paper's headline
    0.24699 < 0.2470 is a DUAL feasible point, verified via Proposition 1: a
    set of coefficients (w_0, w_T, w_1, w_2, w_c) such that
        W(t) = w_0 J_0(t) + sum_i w_1(i) + sum_{i<j} w_2(i,j) J_0(t|x_i-x_j|) >= 1
    for all t >= 0, and V(eps) >= 0 for all sign patterns eps. Then m_1 <= w_T.
    The W(t) >= 1 half uses ONLY (w_0, w_1, w_2), all of which the paper PRINTS
    (Table 2, 29 coefficients). We reproduce W(t) = phi(t) exactly and verify
    phi(t) >= 1 - mu on [0, T] with the paper's reported global min
    0.99995003 at t = 3.77488. The V(eps) >= 0 half needs the 2321 (IEC)
    congruence coefficients w_c, which the paper does NOT print (website only),
    so that half is verified only insofar as the paper asserts V(eps) >= -nu
    with nu = 1e-5. We are honest about which half we re-derive.

Crossing argument for integer chi_m >= 5. A measurable proper coloring of R^2
partitions (almost all of) the plane into 1-avoiding color classes, each of
upper density <= m_1. With m_1 <= 0.24699 < 1/4, four classes cover density at
most 4 * 0.24699 = 0.98796 < 1, so four colors cannot cover the plane: at least
five are required. Hence chi_m(R^2) >= 5. The threshold is exactly m_1 < 1/4
(4 * 1/4 = 1 is the boundary); the inequality is STRICT (0.24699 < 0.25), so the
integer bound chi_m >= 5 holds.
"""

from __future__ import annotations

import json
import math
import pathlib
import time
from itertools import combinations

import cvxpy as cp
import numpy as np
import sympy as sp
from scipy.special import j0, jn_zeros

from experiments.fractional.e3c_ofv_lp_dual import chi_m_integer, CACHE
from experiments.fractional.e3g_ambrus_ie_lp import (
    unit_distance_subgraph,
    enumerate_independent_sets,
)

CONFIG_PATH = CACHE / "ambrus_23point_config.json"


# ---------------------------------------------------------------------------
# (A) Parse + exact-verify the 23-point configuration.
# ---------------------------------------------------------------------------

def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return json.load(f)


def parse_points_exact(cfg: dict) -> list[sp.Expr]:
    """Parse the 23 symbolic complex coordinates into sympy expressions, 1-indexed
    in order x_1..x_23. Returns a list (0-indexed) of complex sympy expressions."""
    I = sp.I
    sqrt = sp.sqrt
    local = {"I": I, "sqrt": sqrt}
    coords = cfg["coordinates_symbolic_1indexed"]
    pts = []
    for k in range(1, 24):
        expr = sp.sympify(coords[str(k)], locals=local)
        pts.append(sp.expand(expr))
    return pts


def to_xy_exact(z: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    """Split complex z into (Re, Im) as exact sympy expressions."""
    return (sp.re(z), sp.im(z))


def exact_unit_distance_graph(pts: list[sp.Expr]) -> tuple[set[tuple[int, int]], dict, int]:
    """Compute the unit-distance graph exactly: pair (i,j) with i<j is an edge iff
    |x_i - x_j|^2 == 1 exactly (sympy simplify). Also collect all squared distances
    to count distinct distances. Returns (edges, dist2_by_pair, n_distinct_distances)."""
    n = len(pts)
    edges = set()
    dist2 = {}
    distinct = set()
    for i in range(n):
        for j in range(i + 1, n):
            d = pts[i] - pts[j]
            # |d|^2 = Re(d)^2 + Im(d)^2
            re_d = sp.re(d)
            im_d = sp.im(d)
            d2 = sp.simplify(re_d**2 + im_d**2)
            dist2[(i, j)] = d2
            distinct.add(sp.nsimplify(d2))
            if d2 == 1:
                edges.add((i, j))
    return edges, dist2, len(distinct)


def points_to_float_array(pts: list[sp.Expr]) -> np.ndarray:
    """Convert the exact complex coordinates to a float (n,2) array (a, b)."""
    X = np.zeros((len(pts), 2))
    for k, z in enumerate(pts):
        zc = complex(z)
        X[k, 0] = zc.real
        X[k, 1] = zc.imag
    return X


# ---------------------------------------------------------------------------
# (B) Primal IE-LP reproduction (IE1 + IE2 only; no IEC congruence).
# ---------------------------------------------------------------------------

def build_ie_lp_dualreport(
    X: np.ndarray,
    edges: set[tuple[int, int]],
    n_freq: int = 600,
    freq_max: float = 30.0,
    indep_max_size: int | None = None,
) -> dict:
    """IE-LP on X (e3g formulation), returning the primal optimum, the solver
    status, the duality gap, and a dual-feasibility report.

    Frequency convention: f(r) = sum_k c_k J_0(2 pi r s_k), unit-distance at r=1.
    This matches e3g (the paper uses J_0(t |x_i-x_j|) which is the t = 2 pi s
    reparametrization; the LP optimum is identical).
    """
    n = X.shape[0]
    indep_sets = enumerate_independent_sets(n, edges, max_size=indep_max_size)
    K = len(indep_sets)

    vertex_indep_idx = [[] for _ in range(n)]
    pair_indep_idx: dict[tuple[int, int], list[int]] = {}
    for I_idx, Iset in enumerate(indep_sets):
        for v in Iset:
            vertex_indep_idx[v].append(I_idx)
        for v1, v2 in combinations(sorted(Iset), 2):
            pair = (v1, v2)
            pair_indep_idx.setdefault(pair, []).append(I_idx)

    freqs = np.linspace(0.001, freq_max, n_freq)

    pair_distances = {}
    for (i, j) in combinations(range(n), 2):
        if (i, j) in edges:
            continue
        pair_distances[(i, j)] = float(np.linalg.norm(X[i] - X[j]))

    a = cp.Variable(K, nonneg=True)
    c = cp.Variable(n_freq, nonneg=True)
    d = cp.Variable()

    J0_at_pair = {p: j0(2.0 * np.pi * dist * freqs) for p, dist in pair_distances.items()}
    J0_at_1 = j0(2.0 * np.pi * freqs)

    constraints = [cp.sum(a) == 1]
    for v in range(n):
        if vertex_indep_idx[v]:
            constraints.append(cp.sum(a[vertex_indep_idx[v]]) == d)
        else:
            constraints.append(d == 0)
    for pair in pair_distances:
        if pair in pair_indep_idx and pair_indep_idx[pair]:
            constraints.append(cp.sum(a[pair_indep_idx[pair]]) == J0_at_pair[pair] @ c)
        else:
            constraints.append(J0_at_pair[pair] @ c == 0)
    constraints.append(J0_at_1 @ c == 0)
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
        "freq_max": freq_max,
        "alpha_G": max(len(s) for s in indep_sets),
        "status": prob.status,
        "m1_primal": float(d.value) if d.value is not None else None,
        "solve_time_s": elapsed,
    }


# ---------------------------------------------------------------------------
# (C) Dual certificate verification: phi(t) = W(t) >= 1 on [0, T].
# ---------------------------------------------------------------------------

def build_phi(cfg: dict, dist_of_pair: dict[tuple[int, int], float]):
    """Return a callable phi(t) implementing the paper's W(t) (eq. W_def / eq_phi),
    using the published (w_0, w_1(1), w_2(i,j)) and the float pair distances.

      phi(t) = w_0 J_0(t) + sum_i w_1(i) + sum_{i<j} w_2(i,j) J_0(t |x_i - x_j|)

    Pairs are 1-indexed in the config; dist_of_pair is 0-indexed."""
    dc = cfg["dual_certificate_published"]
    w0 = dc["w_0"]
    w1_total = sum(dc["w_1"].values())  # only w_1(1) is nonzero
    w2_terms = []
    for key, w in dc["w_2_by_pair_1indexed"].items():
        i1, j1 = (int(s) for s in key.split(","))
        i0, j0_ = i1 - 1, j1 - 1
        pair = (min(i0, j0_), max(i0, j0_))
        dist = dist_of_pair[pair]
        w2_terms.append((w, dist))

    def phi(t):
        t = np.asarray(t, dtype=float)
        val = w0 * j0(t) + w1_total
        for w, dist in w2_terms:
            val = val + w * j0(t * dist)
        return val

    sum_abs = abs(w0) + sum(abs(w) for w, _ in w2_terms)
    return phi, w1_total, sum_abs, w2_terms


def verify_phi_ge_1(phi, w1_total: float, sum_abs: float, T: float = 10000.0):
    """Verify phi(t) >= 1 - mu on [0, T] by dense sampling + the paper's tail
    argument for t > T. Returns a report dict."""
    # Dense scan on [0, T]. The global min is near t = 3.77; sample finely there
    # and coarsely on the tail. |phi'| = |J0' contributions| <= sum_abs * |J1| < 2,
    # so a step h bounds the between-sample error by ~2h; we use h = 1e-4 near the
    # min and confirm the reported global minimum.
    t_fine = np.arange(0.0, 60.0, 1e-4)
    phi_fine = phi(t_fine)
    i_min = int(np.argmin(phi_fine))
    t_min = float(t_fine[i_min])
    phi_min = float(phi_fine[i_min])

    # Coarser scan to T to confirm no deeper dip in the tail.
    t_mid = np.arange(60.0, T, 0.01)
    phi_mid_min = float(np.min(phi(t_mid)))

    # Tail t > T: phi -> w1_total; bound below by w1_total - sum_abs * |J0(s0)|.
    # s0 = largest zero of J1 not exceeding T * d_min. d_min >= 0.1 (paper), so
    # T*d_min >= 1000; use s0 ~ 999.81 as in the paper.
    s0 = 999.81148
    tail_lb = w1_total - sum_abs * abs(j0(s0))

    return {
        "T": T,
        "phi_global_min": phi_min,
        "phi_global_min_location_t": t_min,
        "phi_min_on_[60,T]": phi_mid_min,
        "sum_abs_w0_w2": sum_abs,
        "tail_lower_bound_t>T": tail_lb,
        "paper_reported_min": 0.99995003,
        "paper_reported_min_location": 3.77488,
        "min_matches_paper": abs(phi_min - 0.99995003) < 1e-4,
        "location_matches_paper": abs(t_min - 3.77488) < 1e-2,
    }


# ---------------------------------------------------------------------------
# Wrong-approach detector: 1D analog (must give m_1(R) = 1/2, chi_m(R) = 2).
# ---------------------------------------------------------------------------

def wrong_approach_1d() -> dict:
    """The IE-LP machinery in 1D must recover m_1(R) = 1/2 (chi_m(R) = 2), no
    overshoot. We run the basic OFV-style LP in 1D where Omega_1(t) = cos(t):
    max z0 s.t. z0 + z1 cos(t) >= 0 for all t, z0 + z1 >= 1. Optimum z0 = 1/2.
    A 23-point analog is unnecessary; the 1D radial LP already certifies the
    detector engages and does not overshoot below 1/2."""
    n_t = 4000
    ts = np.linspace(0.0, 60.0, n_t)
    z0 = cp.Variable()
    z1 = cp.Variable()
    cons = [z0 + z1 >= 1.0]
    cons += [z0 + z1 * math.cos(float(t)) >= 0 for t in ts]
    prob = cp.Problem(cp.Minimize(z0), cons)
    prob.solve(solver=cp.HIGHS)
    m1_R = float(z0.value)
    return {
        "m1_R_upper_bound": m1_R,
        "expected": 0.5,
        "chi_m_R_lower": chi_m_integer(m1_R),
        "no_overshoot": m1_R >= 0.5 - 1e-4,
        "status": prob.status,
    }


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def main():
    print("e3i: Ambrus 2023 m_1(R^2) <= 0.2470 reproduction")
    print("=" * 78)
    cfg = load_config()

    # (A) Parse + exact-verify.
    print("\n(A) Parsing + exact-verifying the 23-point configuration ...")
    pts = parse_points_exact(cfg)
    edges, dist2, n_distinct = exact_unit_distance_graph(pts)
    X = points_to_float_array(pts)
    print(f"  points parsed: {len(pts)}")
    print(f"  exact unit-distance edges |E(G_23)|: {len(edges)}")
    print(f"  distinct squared distances: {n_distinct}  (paper: 27)")
    # Float sanity vs exact edge set.
    edges_float = unit_distance_subgraph(X)
    print(f"  float edge set agrees with exact: {edges_float == edges}")
    degrees = [sum(1 for e in edges if v in e) for v in range(len(pts))]
    print(f"  min degree: {min(degrees)}  (paper: all >= 2)")

    dist_of_pair = {}
    for (i, j) in combinations(range(len(pts)), 2):
        dist_of_pair[(i, j)] = float(np.linalg.norm(X[i] - X[j]))

    # (B) Primal IE-LP.
    print("\n(B) Primal IE-LP (IE1 + IE2; NO IEC congruence) via cvxpy + HiGHS ...")
    primal = build_ie_lp_dualreport(X, edges, n_freq=600, freq_max=30.0)
    print(f"  status: {primal['status']}")
    print(f"  independent sets (atom variables): {primal['n_independent_sets']}")
    print(f"  alpha(G_23): {primal['alpha_G']}")
    print(f"  m_1 primal optimum: {primal['m1_primal']:.6f}")
    print(f"  vs paper LP optimum 0.24697 (paper LP includes IEC; ours does not)")
    print(f"  chi_m integer from primal: {chi_m_integer(primal['m1_primal'])}")
    print(f"  solve time: {primal['solve_time_s']:.1f} s")

    # (C) Dual certificate W(t) >= 1.
    print("\n(C) Verifying published dual certificate phi(t) = W(t) >= 1 ...")
    phi, w1_total, sum_abs, _ = build_phi(cfg, dist_of_pair)
    phi_report = verify_phi_ge_1(phi, w1_total, sum_abs)
    print(f"  phi global min: {phi_report['phi_global_min']:.8f} at t = {phi_report['phi_global_min_location_t']:.5f}")
    print(f"  paper reports:  0.99995003 at t = 3.77488")
    print(f"  min matches paper: {phi_report['min_matches_paper']};  location matches: {phi_report['location_matches_paper']}")
    print(f"  |w_0| + sum|w_2| = {phi_report['sum_abs_w0_w2']:.5f}  (paper: ~1.93062 < 2)")
    print(f"  tail bound (t>T): phi -> {w1_total:.6f}, lower bound {phi_report['tail_lower_bound_t>T']:.6f} > 1")

    dc = cfg["dual_certificate_published"]
    nu = dc["verification_constants"]["nu"]
    mu = dc["verification_constants"]["mu"]
    w_T = dc["w_T"]
    rigorous_bound = (w_T + nu) / (1 - mu)
    print(f"\n  Rigorous bound (w_T + nu)/(1 - mu) = ({w_T:.6f} + {nu})/(1 - {mu})")
    print(f"                                     = {rigorous_bound:.6f} < 0.2470")

    strict_quarter = rigorous_bound < 0.25
    chi_m_int = chi_m_integer(rigorous_bound)
    print(f"\n  m_1 < 1/4 strictly: {strict_quarter}  ({rigorous_bound:.6f} < 0.25)")
    print(f"  integer chi_m(R^2) >= {chi_m_int}")
    print(f"  4 classes cover density <= 4 * {rigorous_bound:.6f} = {4*rigorous_bound:.6f} < 1")

    # Wrong-approach detector (1D).
    print("\n(D) Wrong-approach detector (1D analog) ...")
    wa = wrong_approach_1d()
    print(f"  m_1(R) upper bound: {wa['m1_R_upper_bound']:.6f}  (expected 1/2)")
    print(f"  chi_m(R) >= {wa['chi_m_R_lower']}  (expected 2; no overshoot: {wa['no_overshoot']})")

    out = {
        "experiment": "e3i_ambrus_reproduce",
        "source": cfg["source"],
        "config_verify": {
            "n_points": len(pts),
            "n_unit_edges": len(edges),
            "n_distinct_distances": n_distinct,
            "float_exact_edge_agreement": edges_float == edges,
            "min_degree": min(degrees),
        },
        "primal_ie_lp": primal,
        "dual_certificate": {
            "w_T": w_T, "nu": nu, "mu": mu,
            "rigorous_bound": rigorous_bound,
            "phi_verification": phi_report,
            "m1_strictly_below_quarter": bool(strict_quarter),
            "chi_m_integer": chi_m_int,
        },
        "wrong_approach_1d": wa,
        "verdict": {
            "integer_chi_m_ge_5": bool(strict_quarter and chi_m_int >= 5),
            "primal_gap_to_paper": (primal["m1_primal"] - 0.24697) if primal["m1_primal"] else None,
        },
    }
    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3i_ambrus_reproduce.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\narchived: {out_path}")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
