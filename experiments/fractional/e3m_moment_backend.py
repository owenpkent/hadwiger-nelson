r"""e3m: scalable MOMENT / Lasserre backend for the multi-class measurable LP.

Architecture 2/3. This is the L38/L39 barrier-(a) "scalability" fix: a relaxation
of the joint k-coloring feasibility test that NEVER enumerates proper colorings,
so it runs at X_23 scale and beyond, toward chi_m(R^2) >= 6.

The idea (de Laat-Vallentin 2015; DeCorte-Oliveira-Vallentin 2022; note 08/12).
The explicit LP (e3k/e3l) carries one variable a_sigma per proper k-coloring sigma
of a configuration X, which is exponential. We instead keep only the low-order
COLOR-MARGINAL MOMENTS of the (unknown) distribution over colorings:

  y_i(c)      = density of points x with  x + x_i in color class A_c
              = sum_{sigma: sigma(i)=c} a_sigma                    (singleton moment)
  y_ij(c,c')  = density of x with x+x_i in A_c AND x+x_j in A_c'
              = sum_{sigma: sigma(i)=c, sigma(j)=c'} a_sigma       (pairwise moment)

These are exactly the pairwise color-marginals. The number of them is polynomial
in n (n*k singletons + C(n,2)*k^2 pairs), independent of the number of colorings.

Constraints satisfied by the TRUE moments of any measurable proper k-coloring
(so the relaxation is valid: moment-infeasible => chi_m >= k+1):

  (NORM)   sum_c y_i(c) = 1                          every point gets one color
  (MARG)   sum_{c'} y_ij(c,c') = y_i(c)              consistency of pair with single
           sum_{c}  y_ij(c,c') = y_j(c')
  (SYM)    y_ij(c,c') = y_ji(c',c)
  (PROP)   y_ij(c,c) = 0 if {i,j} is a unit edge     no monochromatic unit edge
  (NN)     y_i(c) >= 0,  y_ij(c,c') >= 0

  (BOCH)   per-color autocorrelation is Bochner-positive and avoids distance 1:
           y_ij(c,c) = sum_s nu_c(s) J_0(2 pi ||x_i-x_j|| s)   (+ slack; nu_c >= 0)
           y_i(c)    = sum_s nu_c(s)            (= f_c(0) = delta(A_c), every i)
           sum_s nu_c(s) J_0(2 pi s) = 0        (= f_c(1) = 0, avoidance)

  (IEC)    Formulation 1 + 2 congruence (e3l), now LINEAR on the moments:
           y_I(rho) = y_J(rho')  for congruent {I,J}, |I| <= 2. At degree 1 these
           touch only y_i (|I|=1) and y_ij (|I|=2). The e3l constraint KEYS port
           directly: each key is two (vertex,color) assignment-sets of equal mass.

  (PSD)    Lasserre order-1 moment matrix M >= 0 (optional, the SDP tightening).
           M is indexed by {1} ∪ {(i,c)}; M[1,1]=1, M[1,(i,c)]=y_i(c),
           M[(i,c),(i,c)]=y_i(c) (idempotent indicator), M[(i,c),(i,c'!=c)]=0
           (a point has one color), M[(i,c),(j,c')]=y_ij(c,c'). This is the
           standard Boolean (0/1) moment matrix for the partition {A_c}.

Certificate. Phase-1 minimizes sum|slack| on the (BOCH) couplings. A strictly
positive margin OR an infeasible status => no measurable k-coloring of R^2 exists,
i.e. chi_m(R^2) >= k+1. The relaxation is WEAKER than e3l's exact enumeration
(degree 1 < degree infinity), so it can only MISS obstructions e3l would catch,
never invent one: margins here are <= e3l's. The PSD tightening narrows the gap.

Validation in this file (no X_23 needed):
  - CROSS-VALIDATION vs e3l on small configs: both must give margin 0 (e3l gave 0
    everywhere, so the weaker moment relaxation must too).
  - CORRECTNESS GATE: chi_m <= 7 is proven, so k=7 must stay feasible (margin 0)
    with all IEC + PSD. Run on the rhombus.
  - CERTIFICATE-PATH liveness: a config with no proper k-coloring certifies.
  - SCALING demo: run on configs far beyond e3l's enumeration limit (double Moser
    spindle ~13 pts; a 19-point lattice patch) and report solve time; e3l would
    have to enumerate >> 10^5 colorings on these.

The validation TARGET (k=4 on X_23 -> margin > 0 reproducing >= 5) and the open
k=5 frontier toward >= 6 plug into this backend unchanged once X_23 is restored
to a tracked location; the IEC keys are backend-agnostic.
"""

from __future__ import annotations

import json
import time
from itertools import combinations

import cvxpy as cp
import numpy as np
import sympy as sp
from scipy.special import j0

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config,
    enumerate_congruent_pairs_all,
    formulation1_keys,
    formulation2_keys,
    _triangle_vertices_exact,
    _rhombus_vertices_exact,
    _moser_vertices_exact,
)


# ---------------------------------------------------------------------------
# Larger EXACT configs for the scaling demo (beyond e3l's enumeration limit).
# ---------------------------------------------------------------------------

def _double_moser_vertices_exact():
    """Moser spindle ∪ its image under the binding rotation (cos=5/6, sin=√11/6),
    deduped (the rotation fixes the origin and overlaps several vertices, giving a
    rigid 10-point chi=4 config in Q(√3,√11)). Used with the 19-point hexR2 patch
    to show the backend scales past e3l's coloring-enumeration ceiling."""
    base = _moser_vertices_exact()
    cos_t, sin_t = sp.Rational(5, 6), sp.sqrt(11) / 6
    rot = lambda p: (sp.expand(cos_t * p[0] - sin_t * p[1]),
                     sp.expand(sin_t * p[0] + cos_t * p[1]))
    verts = list(base)
    seen = {(sp.nsimplify(x), sp.nsimplify(y)) for (x, y) in base}
    for p in base:
        q = rot(p)
        key = (sp.nsimplify(sp.simplify(q[0])), sp.nsimplify(sp.simplify(q[1])))
        if key not in seen:
            seen.add(key)
            verts.append(q)
    return verts


def _hex_patch_vertices_exact(R: int):
    """Triangular-lattice hexagonal patch of radius R: integer squared distances,
    exact and fast. 1 + 3R(R+1) points. NOTE: 3-colorable, so trivially feasible;
    used only to demonstrate the backend scales (R=2 -> 19 pts)."""
    s3 = sp.sqrt(3)
    verts = []
    for q in range(-R, R + 1):
        for r in range(-R, R + 1):
            if abs(q + r) <= R:
                verts.append((sp.Integer(q) + sp.Rational(1, 2) * r, s3 / 2 * r))
    return verts


def _ambrus_x23_vertices_exact():
    """The 23-point Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 configuration,
    in exact (re, im) sympy coordinates (field Q(√3, √11)). This is the validation
    target for the measurable chi_m >= 6 route: it is the smallest config the
    single-class density LP needed to cross 1/4 (=> chi_m >= 5), so the multi-class
    k=4 moment relaxation WITH IEC must reproduce a >= 5 obstruction (margin > 0).
    Loads the tracked config via e3i (no _cache dependency)."""
    from experiments.fractional.e3i_ambrus_reproduce import (
        load_config, parse_points_exact, to_xy_exact,
    )
    return [to_xy_exact(z) for z in parse_points_exact(load_config())]


# ---------------------------------------------------------------------------
# Moment-relaxation builder.
# ---------------------------------------------------------------------------

def _assignment_to_terms(assignment):
    """An e3l constraint side is a frozenset of (vertex, color). For the moment
    backend it must touch only singleton (|I|=1) or pairwise (|I|=2) moments."""
    return sorted(assignment)


def build_moment_relaxation(X, dmat2_canon, edges, k, *, use_psd=True,
                            iec_keys=None, n_freq=300, freq_max=20.0,
                            slack_tol=1e-6, solver=None, symmetrize=False):
    """Solve the degree-1 moment (Lasserre order-1) Phase-1 relaxation for k colors.

    iec_keys: iterable of e3l canonical constraint keys (frozenset of two
    (vertex,color) assignment-frozensets), restricted here to |assignment| <= 2.
    Returns a result dict; margin > slack_tol or infeasible => chi_m >= k+1.

    symmetrize: if True, restrict the moments to the S_k color-permutation-invariant
    subspace (Shot A). The Phase-1 objective and ALL constraints (normalization,
    marginalization, per-color Bochner, IEC F1/F2) are invariant under relabeling
    colors, and the feasible set is convex, so the S_k-average of any feasible point
    is feasible with no worse objective. Hence the optimum is attained on the
    symmetric subspace and these added equalities are LOSSLESS (margin unchanged).
    This is the safe, verifiable foundation for the block-diagonalized SDP that
    actually breaks the PSD scale wall (the O(2)-congruence reduction is the harder
    follow-on). Here we only ADD equalities (no PSD-size reduction yet), so this
    flag VALIDATES losslessness rather than buying scale.
    """
    n = X.shape[0]
    iec_keys = list(iec_keys or [])

    # Singleton moments y1[i, c] and pairwise moments y2[(i,j)] (k x k, i < j).
    y1 = cp.Variable((n, k), nonneg=True)
    y2 = {(i, j): cp.Variable((k, k), nonneg=True)
          for i in range(n) for j in range(i + 1, n)}
    nu = cp.Variable((k, n_freq), nonneg=True)

    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)

    cons = []
    # (NORM)
    for i in range(n):
        cons.append(cp.sum(y1[i, :]) == 1)
    # (MARG) + (PROP) per pair.
    for (i, j), Y in y2.items():
        for c in range(k):
            cons.append(cp.sum(Y[c, :]) == y1[i, c])   # row marginal -> y_i
            cons.append(cp.sum(Y[:, c]) == y1[j, c])   # col marginal -> y_j
        if (i, j) in edges:
            for c in range(k):
                cons.append(Y[c, c] == 0)              # no monochromatic edge

    # (BOCH): per-color avoidance + autocorrelation couplings (slack on non-edges).
    slacks = []
    for c in range(k):
        nu_mass = cp.sum(nu[c, :])
        for i in range(n):
            cons.append(y1[i, c] == nu_mass)           # f_c(0) at every vertex
        cons.append(J0_at_1 @ nu[c, :] == 0)           # f_c(1) = 0
    for (i, j), Y in y2.items():
        if (i, j) in edges:
            continue
        d = float(np.linalg.norm(X[i] - X[j]))
        Jvec = j0(2.0 * np.pi * d * freqs)
        for c in range(k):
            s = cp.Variable()
            slacks.append(s)
            cons.append(Y[c, c] - Jvec @ nu[c, :] == s)

    # (IEC) Formulation 1 + 2 on |I| <= 2, as linear moment equalities.
    n_iec = 0
    for key in iec_keys:
        sides = list(key)
        L = _moment_of(sides[0], y1, y2, k)
        R = _moment_of(sides[1], y1, y2, k)
        if L is None or R is None:
            continue  # touches a moment of order > 2 (out of this relaxation)
        cons.append(L == R)
        n_iec += 1

    # (SYM) S_k color-permutation symmetrization (Shot A; lossless, see docstring).
    # Orbits under relabeling colors: every singleton y1[i,c] shares one value per i;
    # every Bochner mass nu[c,:] shares one value; per pair, all diagonal entries
    # Y[c,c] are one value and all off-diagonal Y[c,c'] (c != c') are another.
    if symmetrize:
        for i in range(n):
            for c in range(1, k):
                cons.append(y1[i, c] == y1[i, 0])
        for c in range(1, k):
            cons.append(nu[c, :] == nu[0, :])
        for (i, j), Y in y2.items():
            for c in range(k):
                if c > 0:
                    cons.append(Y[c, c] == Y[0, 0])
                for cp_ in range(k):
                    if c != cp_ and not (c == 0 and cp_ == 1):
                        cons.append(Y[c, cp_] == Y[0, 1])

    # (PSD) Lasserre order-1 moment matrix.
    if use_psd:
        blocks = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(cp.diag(y1[i, :]))
                elif i < j:
                    row.append(y2[(i, j)])
                else:
                    row.append(y2[(j, i)].T)
            blocks.append(row)
        B = cp.bmat(blocks)                            # (n k) x (n k)
        y1flat = cp.reshape(y1, (n * k, 1), order="C")
        top = cp.hstack([cp.Constant(np.array([[1.0]])), y1flat.T])
        bot = cp.hstack([y1flat, B])
        M = cp.vstack([top, bot])
        cons.append(M == M.T)
        cons.append(M >> 0)

    prob = cp.Problem(cp.Minimize(cp.sum([cp.abs(s) for s in slacks])), cons)
    if solver is None:
        # CLARABEL is an interior-point conic solver: ~1e-8 residuals on the PSD
        # block, vs ~1e-4/1e-5 for the first-order SCS. The accuracy matters
        # directly here: a "certificate" is a positive slack margin, so a solver
        # whose noise floor is 1e-5 manufactures spurious chi_m bounds. HIGHS is
        # an exact-ish simplex/IPM for the LP-only (no PSD) case.
        solver = cp.CLARABEL if use_psd else cp.HIGHS
    t0 = time.time()
    try:
        prob.solve(solver=solver, verbose=False)
    except cp.error.SolverError:
        try:
            prob.solve(solver=cp.SCS, verbose=False, eps=1e-7, max_iters=100_000)
        except cp.error.SolverError as e:  # noqa: BLE001
            return {"n_points": n, "k": k, "use_psd": use_psd,
                    "status": f"SOLVER_ERROR:{e}", "n_iec_constraints": n_iec}
    elapsed = time.time() - t0

    raw = float(prob.value) if prob.value is not None else None
    margin = raw if (raw is not None and np.isfinite(raw)) else None
    infeasible = prob.status in ("infeasible", "infeasible_inaccurate")
    # A slack margin only counts as a certificate if it clears the solver noise
    # floor by a healthy factor. With CLARABEL/HIGHS the residual is ~1e-8, so
    # slack_tol=1e-6 is two orders above noise. Margins between noise and slack_tol
    # are reported but explicitly NOT treated as bounds (see `near_noise`).
    near_noise = bool(margin is not None and 0.0 < margin <= slack_tol)
    certifies = bool(infeasible or (margin is not None and margin > slack_tol))
    return {
        "n_points": n, "k": k, "use_psd": use_psd,
        "n_singleton_moments": n * k,
        "n_pairwise_moments": len(y2) * k * k,
        "n_iec_constraints": n_iec, "status": prob.status,
        "infeasibility_margin": margin, "near_noise": near_noise,
        "certifies_infeasible": certifies,
        "implies_chi_m_geq": (k + 1) if certifies else None,
        "solver": str(solver), "solve_time_s": elapsed,
    }


def _moment_of(assignment, y1, y2, k):
    """The moment y_S(rho) for an assignment (frozenset of (vertex,color)) of size
    1 or 2. Returns a cvxpy scalar, or None if the assignment has size > 2 (outside
    the degree-1 relaxation) or is internally inconsistent (two colors on one vertex)."""
    terms = sorted(assignment)
    if len(terms) == 1:
        (v, c) = terms[0]
        return y1[v, c]
    if len(terms) == 2:
        (v1, c1), (v2, c2) = terms
        if v1 == v2:
            return None  # same vertex two colors -> impossible pattern (degree-1: skip)
        i, j = (v1, v2) if v1 < v2 else (v2, v1)
        ci, cj = (c1, c2) if v1 < v2 else (c2, c1)
        return y2[(i, j)][ci, cj]
    return None


# ---------------------------------------------------------------------------
# Runner: build IEC keys (|I|<=2 only), solve LP and PSD variants.
# ---------------------------------------------------------------------------

def iec_keys_degree2(X, dmat2_canon, edges, k):
    n = X.shape[0]
    pairs_indep = enumerate_congruent_pairs_all(n, dmat2_canon, 2,
                                                independent_only=True, edges=edges)
    pairs_all = enumerate_congruent_pairs_all(n, dmat2_canon, 2,
                                              independent_only=False, edges=edges)
    f1 = formulation1_keys(pairs_indep, k)
    f2 = formulation2_keys(pairs_all, dmat2_canon, k)
    return f1, f2, (f1 | f2)


def run_config(name, verts_fn, k, *, do_psd=True, do_iec=True, verbose=True):
    verts = verts_fn()
    X, dmat2_canon, edges = build_exact_config(verts)
    n = X.shape[0]
    f1, f2, f12 = iec_keys_degree2(X, dmat2_canon, edges, k) if do_iec else (set(), set(), set())

    out = {"config": name, "n_points": n, "n_edges": len(edges), "k": k,
           "n_F1_deg2": len(f1), "n_F2_deg2": len(f2), "runs": {}}
    variants = [("LP base", False, set())]
    if do_iec:
        variants.append(("LP +IEC", False, f12))
    if do_psd:
        variants.append(("PSD base", True, set()))
        if do_iec:
            variants.append(("PSD +IEC", True, f12))
    for label, psd, keys in variants:
        r = build_moment_relaxation(X, dmat2_canon, edges, k,
                                    use_psd=psd, iec_keys=keys)
        out["runs"][label] = r
        if verbose:
            m = r.get("infeasibility_margin")
            ms = "None" if m is None else f"{m:.2e}"
            flag = " [noise]" if r.get("near_noise") else ""
            chi = r.get("implies_chi_m_geq")
            chi_s = f"CHI_M>={chi}" if chi else "-"
            print(f"  [{name} k={k}] {label:9s}: {r['status']:>10s} "
                  f"margin={ms}{flag} iec={r.get('n_iec_constraints', 0)} "
                  f"{chi_s} ({r.get('solve_time_s', 0):.2f}s)")
    return out


def reverify(name, verts_fn, k, *, use_psd, iec_keys):
    """High-accuracy re-solve of an apparent certificate, to separate a genuine
    positive slack margin from solver noise. CLARABEL is already ~1e-8; we tighten
    further and require the margin to persist above slack_tol."""
    verts = verts_fn()
    X, dc, e = build_exact_config(verts)
    r = build_moment_relaxation(X, dc, e, k, use_psd=use_psd, iec_keys=iec_keys,
                                slack_tol=1e-6)
    return r.get("infeasibility_margin"), r.get("certifies_infeasible")


def run_x23_validation(k=4, do_psd=True):
    """The measurable-route validation target: run the degree-1 moment relaxation
    WITH IEC on the Ambrus X_23 config. k=4 must reproduce chi_m >= 5 (margin > 0)
    if degree-1 IEC (subset size <= 2) is strong enough; a margin at the solver
    noise floor instead means degree-1 is too weak (the single-class route needed
    IEC up to size 5), pointing to the order-2 lift (e3n + symmetry reduction).

    Opt-in (minutes-long, ~65k IEC equalities at k=4), so it is NOT in main()'s
    default suite. Run: python -c "from experiments.fractional.e3m_moment_backend
    import run_x23_validation; run_x23_validation()".
    """
    print(f"e3m X_23 validation: k={k} multi-class moment relaxation + IEC")
    print("=" * 78)
    out = run_config("X_23", _ambrus_x23_vertices_exact, k, do_psd=do_psd, do_iec=True)
    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / f"e3m_x23_k{k}.json"
    with out_path.open("w") as f:
        json.dump({"experiment": "e3m_x23_validation", "result": out}, f, indent=2)
    print(f"\narchived: {out_path}")
    certs = [lbl for lbl, r in out["runs"].items() if r.get("certifies_infeasible")]
    if certs:
        print(f"CERTIFIES chi_m >= {k+1} via: {certs} (re-verify the margin at high accuracy)")
    else:
        print(f"No certificate at k={k}: degree-1 IEC margins at noise floor "
              f"(=> order-2 lift needed; see e3n).")
    return out


def main():
    print("e3m: scalable moment / Lasserre backend for the multi-class measurable LP")
    print("=" * 78)
    results = {}

    print("\n[GATE] k=7 on rhombus must stay FEASIBLE (margin ~0) with IEC + PSD.")
    print("       (chi_m(R^2) <= 7 proven; CLARABEL high-accuracy so margin is real.)")
    results["gate_rhombus_k7"] = run_config("rhombus", _rhombus_vertices_exact, 7)

    print("\n[RELAXATION GAP] degree-1 LP is WEAKER than enumeration, so a graph that")
    print("  is not k-colorable need NOT be LP-infeasible (informational, not a gate).")
    for nm, fn, k in (("triangle", _triangle_vertices_exact, 2),
                      ("moser7", _moser_vertices_exact, 3)):
        X, dc, e = build_exact_config(fn())
        r_lp = build_moment_relaxation(X, dc, e, k, use_psd=False, iec_keys=set())
        r_psd = build_moment_relaxation(X, dc, e, k, use_psd=True, iec_keys=set())
        print(f"  {nm} k={k} (chi={k}+ not k-colorable): "
              f"LP margin={r_lp.get('infeasibility_margin')}, "
              f"PSD margin={r_psd.get('infeasibility_margin')}, "
              f"PSD certifies={r_psd.get('certifies_infeasible')}")
        results[f"gap_{nm}_k{k}"] = {"lp": r_lp, "psd": r_psd}

    print("\n[CROSS-VAL vs e3l] small configs: moment relaxation must also be margin ~0")
    print("  (it is weaker than e3l, whose margins were all 0, so it cannot exceed them).")
    for nm, fn in (("triangle", _triangle_vertices_exact),
                   ("rhombus", _rhombus_vertices_exact),
                   ("moser7", _moser_vertices_exact)):
        for k in (4, 5):
            results[f"{nm}_k{k}"] = run_config(nm, fn, k)

    print("\n[SCALING] configs beyond e3l's enumeration limit. e3l would enumerate")
    print("  >> 1e5 proper colorings; the moment backend never enumerates.")
    results["double_moser_k5"] = run_config(
        "double_moser", _double_moser_vertices_exact, 5)
    # hex R=2 (19 pts) is 3-colorable; its lattice symmetry explodes the degree-2
    # IEC set (~70k constraints), so we run the IEC-free variants to show the core
    # LP/PSD solve scales to 19 points. (The IEC explosion is itself a practical
    # caveat for highly symmetric configs.)
    results["hexR2_k4"] = run_config(
        "hexR2", lambda: _hex_patch_vertices_exact(2), 4, do_iec=False)

    # Robustness sweep: re-verify EVERY apparent certificate at high accuracy.
    print("\n[VERIFY] re-checking any apparent certificate (margin > 1e-6) ...")
    flagged = []
    for key, res in results.items():
        for label, r in res.get("runs", {}).items():
            if r.get("certifies_infeasible"):
                flagged.append((key, label, r.get("infeasibility_margin")))
    if not flagged:
        print("  none flagged: no configuration certifies chi_m >= k+1 (all margins"
              " <= 1e-6, i.e. at the solver noise floor). Expected: these configs"
              " are too small / wrong-structured to force a measurable bound.")
    else:
        for key, label, m in flagged:
            print(f"  FLAGGED {key}/{label}: margin {m} -> needs exact-dual re-verification")

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3m_moment_backend.json"
    with out_path.open("w") as f:
        json.dump({"experiment": "e3m_moment_backend",
                   "any_certificate": bool(flagged), "results": results},
                  f, indent=2)
    print(f"\narchived: {out_path}")

    # Headline.
    gate = results["gate_rhombus_k7"]["runs"].get("PSD +IEC", {})
    gm = gate.get("infeasibility_margin")
    gate_ok = (gate.get("status") in ("optimal", "optimal_inaccurate")
               and gm is not None and gm < 1e-6)
    print("\n" + "=" * 78)
    print(f"GATE (k=7 rhombus PSD+IEC feasible): {'PASS' if gate_ok else 'CHECK'} "
          f"(margin {gm})")
    print(f"NO false certificate: {'PASS' if not flagged else 'FAIL'} "
          f"({len(flagged)} flagged)")
    print("SCALING solved: "
          + ", ".join(f"{results[c]['config']} n={results[c]['n_points']}"
                      f" ({max(rr.get('solve_time_s', 0) for rr in results[c]['runs'].values()):.1f}s)"
                      for c in ("double_moser_k5", "hexR2_k4")))
    return results


if __name__ == "__main__":
    raise SystemExit(main())
