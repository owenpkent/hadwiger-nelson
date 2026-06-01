r"""e3p: S_k-BLOCK-DIAGONALIZED order-1 measurable moment relaxation (Shot A, Part 1).

This is the cheap, fully cross-checkable increment of the Shot A symmetry-reduction
program (SHOTA_SYMMETRY_REDUCTION_PLAN.md). L44 proved + validated that restricting
the multi-class moment relaxation to the S_k color-symmetric subspace is lossless.
Here we EXPLOIT that symmetry to shrink the PSD cone, then verify the shrunk SDP
reproduces e3m's margins exactly. Proving the basis change on order-1 (where an
independent full-size reference, e3m, exists) is the prerequisite to porting it to
order-2, where the same reduction is what brings X_23 (|B|~4141) into solver range.

THE REDUCTION (order-1, derived in the plan, verified numerically). On the symmetric
subspace the singleton moments are fixed (y_i(c) = 1/k) and the pairwise moments
collapse to two values per pair: the SAME-color density p_ij = y_ij(c,c) and the
DIFFERENT-color density q_ij = y_ij(c,c'), c != c', tied by the marginal
p_ij + (k-1) q_ij = 1/k. The order-1 Lasserre matrix M (size 1+nk) then block-
diagonalizes under the S_k action on colors (trivial (+) standard isotypics):
  - the TRIVIAL block (size 1+n) has only constant entries (1, 1/sqrt k, 1/k); it is
    rank-1 and marginally PSD for ALL feasible points, hence VACUOUS (no constraint);
  - the STANDARD block is an n x n matrix S with S[i,i] = 1/k and
    S[i,j] = p_ij - q_ij, and M >= 0 IFF S >= 0.
So the whole order-1 PSD reduces to a single n x n PSD, INDEPENDENT OF k. (For k=5
that is a 5x smaller side than the full 1+nk matrix; the win compounds at order 2.)

Bochner block (unchanged, shared across colors by symmetry): one measure nu >= 0 with
f(0) = sum nu = 1/k, f(1) = 0, and on each NON-edge pair the same-color density is the
radial autocorrelation p_ij = sum_s nu_s J_0(2 pi ||x_i-x_j|| s) (+ Phase-1 slack).
On EDGE pairs p_ij = 0 (no monochromatic edge), contributing the constant
s_ij = -q_ij = -1/(k(k-1)) to S.

IEC under symmetrization. For |I| <= 2 both Formulation 1 and Formulation 2 collapse
to "congruent pairs have equal same-color density": p_ij = p_{i'j'} whenever the
pairs (i,j) and (i',j') are congruent (equal canonical squared distance). That is the
only IEC content order-1 can carry (it is inert at small scale, L43; included for
parity with e3m and for the order-2 port).
"""
from __future__ import annotations

import json
import time
from itertools import combinations

import cvxpy as cp
import numpy as np
from scipy.special import j0

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config,
    _triangle_vertices_exact, _rhombus_vertices_exact, _moser_vertices_exact,
)
from experiments.fractional.e3m_moment_backend import (
    build_moment_relaxation, iec_keys_degree2, _ambrus_x23_vertices_exact,
)


def build_blockdiag_order1(X, dmat2_canon, edges, k, *, use_psd=True,
                           congruence_iec=False, n_freq=300, freq_max=20.0,
                           slack_tol=1e-6, solver=None):
    """S_k-reduced order-1 Phase-1 relaxation. Returns a result dict; margin >
    slack_tol or infeasible => chi_m >= k+1. Designed to reproduce e3m's
    build_moment_relaxation margins (with symmetrize=True, which is lossless)."""
    n = X.shape[0]
    edges = set((min(a, b), max(a, b)) for (a, b) in edges)

    pairs = list(combinations(range(n), 2))
    dist = {(i, j): float(np.linalg.norm(X[i] - X[j])) for (i, j) in pairs}

    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)

    nu = cp.Variable(n_freq, nonneg=True)
    # same-color density per NON-edge pair (edges are fixed to 0).
    p = {(i, j): cp.Variable(nonneg=True) for (i, j) in pairs if (i, j) not in edges}

    cons = [cp.sum(nu) == 1.0 / k, J0_at_1 @ nu == 0]

    # Bochner couplings on non-edges, with a free Phase-1 slack each.
    slacks = []
    for (i, j), var in p.items():
        Jvec = j0(2.0 * np.pi * dist[(i, j)] * freqs)
        s = cp.Variable()
        slacks.append(s)
        cons.append(var - Jvec @ nu == s)
        cons.append(var <= 1.0 / k)              # q_ij >= 0

    # IEC (symmetrized): congruent pairs share the same same-color density.
    n_iec = 0
    if congruence_iec:
        by_d2: dict = {}
        for (i, j) in p:                          # only non-edge pairs are free
            key = dmat2_canon[(i, j)]
            by_d2.setdefault(key, []).append((i, j))
        for key, group in by_d2.items():
            for a in range(1, len(group)):
                cons.append(p[group[a]] == p[group[0]])
                n_iec += 1

    # The n x n standard block S: S[i,i] = 1/k, S[i,j] = p_ij - q_ij.
    # q_ij = (1/k - p_ij)/(k-1); on edges p_ij = 0 so q_ij = 1/(k(k-1)).
    if use_psd:
        rows = []
        edge_q = 1.0 / (k * (k - 1))
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(cp.Constant(1.0 / k))
                else:
                    a, b = (i, j) if i < j else (j, i)
                    if (a, b) in edges:
                        row.append(cp.Constant(-edge_q))
                    else:
                        pij = p[(a, b)]
                        qij = (cp.Constant(1.0 / k) - pij) / (k - 1)
                        row.append(pij - qij)
            rows.append(cp.hstack(row))
        S = cp.vstack(rows)
        cons.append(S == S.T)
        cons.append(S >> 0)

    prob = cp.Problem(cp.Minimize(cp.sum([cp.abs(s) for s in slacks])), cons)
    if solver is None:
        solver = cp.CLARABEL if use_psd else cp.HIGHS
    t0 = time.time()
    try:
        prob.solve(solver=solver, verbose=False)
    except cp.error.SolverError:
        prob.solve(solver=cp.SCS, verbose=False, eps=1e-7, max_iters=100_000)
    elapsed = time.time() - t0

    raw = float(prob.value) if prob.value is not None else None
    margin = raw if (raw is not None and np.isfinite(raw)) else None
    infeasible = prob.status in ("infeasible", "infeasible_inaccurate")
    near_noise = bool(margin is not None and 0.0 < margin <= slack_tol)
    certifies = bool(infeasible or (margin is not None and margin > slack_tol))
    return {
        "n_points": n, "k": k, "use_psd": use_psd, "psd_side": n,
        "n_free_pairs": len(p), "n_iec_constraints": n_iec,
        "status": prob.status, "infeasibility_margin": margin,
        "near_noise": near_noise, "certifies_infeasible": certifies,
        "implies_chi_m_geq": (k + 1) if certifies else None,
        "solve_time_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Validation: reproduce e3m (full-size) margins on small configs.
# ---------------------------------------------------------------------------

TOL = 1e-6


def _agree(a, b):
    if a is None or b is None:
        return a is None and b is None
    if a <= TOL and b <= TOL:
        return True
    return abs(a - b) <= TOL


def validate():
    print("e3p: S_k-block-diagonalized order-1 vs full-size e3m (must reproduce margins)")
    print("=" * 78)
    configs = [("triangle", _triangle_vertices_exact),
               ("rhombus", _rhombus_vertices_exact),
               ("moser7", _moser_vertices_exact)]
    out = {"experiment": "e3p_blockdiag_order1", "tol": TOL, "rows": []}
    all_ok = True
    for name, fn in configs:
        X, dc, edges = build_exact_config(fn())
        for k in (4, 5):
            _, _, f12 = iec_keys_degree2(X, dc, edges, k)
            for label, psd, iec in (("LP base", False, False),
                                    ("LP +IEC", False, True),
                                    ("PSD base", True, False),
                                    ("PSD +IEC", True, True)):
                # e3m reference (symmetrize=True; lossless per L44).
                ref = build_moment_relaxation(
                    X, dc, edges, k, use_psd=psd, symmetrize=True,
                    iec_keys=(f12 if iec else set()))
                red = build_blockdiag_order1(
                    X, dc, edges, k, use_psd=psd, congruence_iec=iec)
                mr, md = ref.get("infeasibility_margin"), red.get("infeasibility_margin")
                ok = _agree(mr, md)
                # Soundness: the reduced SDP must not FAKE a certificate vs e3m.
                no_fake = (md is None) or (mr is None) or (md <= mr + TOL)
                ok = ok and no_fake
                all_ok = all_ok and ok
                side = red.get("psd_side") if psd else "-"
                fullside = (1 + X.shape[0] * k) if psd else "-"
                print(f"  [{name} k={k}] {label:9s}: e3m={_fmt(mr)} e3p={_fmt(md)} "
                      f"PSD side {fullside}->{side}  {'OK' if ok else '!! MISMATCH'}")
                out["rows"].append({"config": name, "k": k, "variant": label,
                                    "e3m_margin": mr, "e3p_margin": md,
                                    "full_psd_side": fullside, "reduced_psd_side": side,
                                    "ok": ok})
    out["all_reproduce"] = all_ok
    CACHE.mkdir(exist_ok=True)
    with (CACHE / "e3p_blockdiag_order1.json").open("w") as f:
        json.dump(out, f, indent=2)
    print("\n" + "=" * 78)
    print(f"BLOCK-DIAGONALIZED order-1 reproduces e3m on all small configs: "
          f"{'PASS' if all_ok else 'FAIL'}")
    print("=> the S_k symmetry-adapted basis is correct; ready to port to order-2.")
    return all_ok


def _fmt(m):
    return "None" if m is None else f"{m:.2e}"


def main():
    ok = validate()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
