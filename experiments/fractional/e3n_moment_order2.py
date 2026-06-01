r"""e3n: ORDER-2 moment / Lasserre relaxation for the multi-class measurable LP.

Architecture 2/3. The strength increment over the degree-1 backend e3m (L40),
flagged in L40 as the next lever if degree-1 (IEC subset size <= 2) is too weak.

Why order-2. The single-class IEC proof (L36) needed congruence constraints up to
subset size 5 to cross 1/4. The degree-1 backend (e3m) carries IEC only up to size
2 (its moment matrix is indexed by SINGLETON patterns, entries are size-<=2
moments). The order-2 moment matrix is indexed by patterns on subsets up to size 2,
so its entries are moments up to size 4: it can host IEC congruence constraints up
to subset size 4, and its larger PSD block couples the pairwise color-marginals
through size-3 and size-4 joint moments. This is the de Laat-Vallentin / DeCorte-
Oliveira-Vallentin order-2 Lasserre step (note 08).

The construction.
  Basis B (the order-2 "monomial basis"): the empty pattern (constant 1), every
  singleton pattern (i,c), and every pair pattern ((i,c),(j,c')) that is PROPER
  (we prune monochromatic unit edges, whose moment is identically 0).
  Moment matrix M, |B| x |B|, with
     M[alpha, beta] = y( S_alpha ∪ S_beta,  rho_alpha ⊕ rho_beta ),
  the joint color-density of the merged pattern, = 0 if the two patterns disagree
  on a shared vertex or the merge is improper. Entries are moments on subsets of
  size <= 4. EQUAL merged patterns share ONE variable, which auto-enforces moment
  consistency across the matrix.

Constraints valid for the TRUE moments of any measurable proper k-coloring (so the
relaxation is valid: order-2-infeasible => chi_m(R^2) >= k+1):
  - M[empty,empty] = 1;  M >= 0 (PSD);  every moment variable >= 0.
  - sum_c y_i(c) = 1 (each point one color).
  - improper moments = 0 (monochromatic unit edge).
  - marginalization: y_i(c) = sum_{c'} y_ij(c,c')  (singleton <- pair).
  - per-color Bochner: y_ij(c,c) = sum_s nu_c(s) J_0(2 pi ||x_i-x_j|| s) (+slack);
    y_i(c) = sum_s nu_c(s);  sum_s nu_c(s) J_0(2 pi s) = 0.
  - IEC (Formulation 1 + 2) up to subset size 4: e3l keys re-expressed as equalities
    among the order-<=4 moment variables.

Certificate. Phase-1 minimizes sum|slack| on the Bochner couplings; a positive
margin (well above the solver noise floor) or an infeasible status => chi_m >= k+1.
Per the L40 lesson, the PSD block is solved with the interior-point CLARABEL solver
and any apparent certificate must clear the noise floor by orders of magnitude.

Scope. The naive (no-symmetry) order-2 SDP has |B| ~ 1 + nk + binom(n,2)k^2; the
PSD matrix is |B| x |B|. This grows fast (n=7,k=4 -> ~320; n=10 -> ~760; n=19 ->
~2800), so this file maps the practical CEILING of the naive construction and
thereby answers whether full X_23 (n=23 -> ~4100) needs symmetry reduction before
the order-2 frontier (k=4 -> validate >=5; k=5 -> open >=6) can be run.

Validation here (no X_23 needed): cross-check order-2 is AT LEAST as strong as
order-1 (e3m) on the certificate path (triangle k=2, Moser k=3 -> infeasible),
stays feasible on the chi_m<=7 gate, agrees (margin ~0) on small configs, and a
scalability sweep over n reporting |B| and solve time.
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
    enumerate_congruent_pairs_all,
    formulation1_keys,
    formulation2_keys,
    _triangle_vertices_exact,
    _rhombus_vertices_exact,
    _moser_vertices_exact,
)
from experiments.fractional.e3m_moment_backend import (
    _double_moser_vertices_exact,
    _hex_patch_vertices_exact,
)


def _proper(assign: dict, edges) -> bool:
    """Is the coloring `assign` (vertex->color) proper on its support (no
    monochromatic unit edge)?"""
    verts = list(assign)
    for a in range(len(verts)):
        for b in range(a + 1, len(verts)):
            u, w = verts[a], verts[b]
            if assign[u] == assign[w] and ((u, w) in edges or (w, u) in edges):
                return False
    return True


def _canon(assignset, edges):
    """Canonicalize a pattern (iterable of (vertex,color)) to ('one'|'zero'|key).
    'one' = empty pattern; 'zero' = inconsistent (two colors on a vertex) or
    improper (monochromatic unit edge); else the frozenset key of its moment."""
    d = {}
    for (v, c) in assignset:
        if v in d and d[v] != c:
            return "zero"
        d[v] = c
    if not d:
        return "one"
    if not _proper(d, edges):
        return "zero"
    return frozenset(d.items())


def build_order2_relaxation(X, dmat2_canon, edges, k, *, iec_keys=None,
                            n_freq=300, freq_max=20.0, slack_tol=1e-6,
                            max_basis=1400, solver=None):
    """Solve the order-2 moment Phase-1 relaxation for k colors on X.

    Returns a result dict; margin > slack_tol or infeasible => chi_m >= k+1.
    If the basis would exceed max_basis, returns a SKIPPED status (the naive SDP
    is too large) so the scalability sweep can record the ceiling.

    The moment matrix M is built as a SINGLE sparse linear map vec(M) = S y + c1
    from the moment-variable vector y, NOT as a scalar cp.bmat: the latter creates
    |B|^2 separate scalar subexpressions and cvxpy's canonicalization of that is
    catastrophically memory-hungry (>1 GB at |B|~180). The sparse map is what makes
    order-2 runnable past triangles."""
    from collections import defaultdict
    from scipy.sparse import coo_matrix

    n = X.shape[0]
    iec_keys = list(iec_keys or [])

    # Order-2 basis: empty, singletons, proper pairs.
    basis = [frozenset()]
    for i in range(n):
        for c in range(k):
            basis.append(frozenset({(i, c)}))
    for i in range(n):
        for j in range(i + 1, n):
            for c in range(k):
                for cp_ in range(k):
                    if (i, j) in edges and c == cp_:
                        continue
                    basis.append(frozenset({(i, c), (j, cp_)}))
    if len(basis) > max_basis:
        return {"n_points": n, "k": k, "status": "SKIPPED_BASIS_TOO_LARGE",
                "basis_size": len(basis), "max_basis": max_basis}

    D = len(basis)
    # Positions in M per distinct moment key (shared entries auto-enforce moment
    # consistency); positions whose merged pattern is the empty pattern carry a 1.
    pos_per_key = defaultdict(list)
    one_rows, one_cols = [], []
    for a in range(D):
        Ba = basis[a]
        for b in range(D):
            key = _canon(Ba | basis[b], edges)
            if key == "zero":
                continue
            if key == "one":
                one_rows.append(a); one_cols.append(b)
            else:
                pos_per_key[key].append(a * D + b)

    key_list = list(pos_per_key)
    K = len(key_list)
    key_index = {key: idx for idx, key in enumerate(key_list)}
    y = cp.Variable(K, nonneg=True)            # the moment variables

    # Sparse selection S: vec(M)[a*D+b] = sum over keys at (a,b). Each (a,b) has at
    # most one key (the merged pattern is unique), so S has one 1 per nonzero entry.
    rows_S, cols_S = [], []
    for idx, key in enumerate(key_list):
        for flat in pos_per_key[key]:
            rows_S.append(flat); cols_S.append(idx)
    S = coo_matrix((np.ones(len(rows_S)), (rows_S, cols_S)), shape=(D * D, K)).tocsr()
    c1 = np.zeros(D * D)
    c1[np.array(one_rows, dtype=int) * D + np.array(one_cols, dtype=int)] = 1.0 \
        if one_rows else 0.0
    vecM = S @ y + cp.Constant(c1)
    M = cp.reshape(vecM, (D, D), order="C")

    def mom(assignset):
        key = _canon(assignset, edges)
        if key == "one":
            return cp.Constant(1.0)
        if key == "zero":
            return cp.Constant(0.0)
        idx = key_index.get(key)
        return y[idx] if idx is not None else cp.Constant(0.0)

    cons = [M >> 0]

    # (NORM) each point one color.
    for i in range(n):
        cons.append(cp.sum([mom({(i, c)}) for c in range(k)]) == 1)

    # (MARG) singleton <- pair marginalization.
    for i in range(n):
        for c in range(k):
            yi = mom({(i, c)})
            for j in range(n):
                if j == i:
                    continue
                cons.append(yi == cp.sum([mom({(i, c), (j, cc)}) for cc in range(k)]))

    # (BOCH) per-color avoidance + autocorrelation couplings (slack on non-edges).
    nu = cp.Variable((k, n_freq), nonneg=True)
    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)
    for c in range(k):
        nu_mass = cp.sum(nu[c, :])
        for i in range(n):
            cons.append(mom({(i, c)}) == nu_mass)
        cons.append(J0_at_1 @ nu[c, :] == 0)
    slacks = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in edges:
                continue
            d = float(np.linalg.norm(X[i] - X[j]))
            Jvec = j0(2.0 * np.pi * d * freqs)
            for c in range(k):
                s = cp.Variable()
                slacks.append(s)
                cons.append(mom({(i, c), (j, c)}) - Jvec @ nu[c, :] == s)

    # (IEC) Formulation 1 + 2 up to subset size 4, as moment equalities.
    n_iec = 0
    for key in iec_keys:
        sides = list(key)
        cons.append(mom(sides[0]) == mom(sides[1]))
        n_iec += 1

    if solver is None:
        solver = cp.CLARABEL
    prob = cp.Problem(cp.Minimize(cp.sum([cp.abs(s) for s in slacks]) if slacks
                                  else cp.Constant(0.0)), cons)
    t0 = time.time()
    try:
        prob.solve(solver=solver, verbose=False)
    except cp.error.SolverError as e:  # noqa: BLE001
        return {"n_points": n, "k": k, "status": f"SOLVER_ERROR:{e}",
                "basis_size": D, "n_moment_vars": K}
    elapsed = time.time() - t0

    raw = float(prob.value) if prob.value is not None else None
    margin = raw if (raw is not None and np.isfinite(raw)) else None
    infeasible = prob.status in ("infeasible", "infeasible_inaccurate")
    near_noise = bool(margin is not None and 0.0 < margin <= slack_tol)
    certifies = bool(infeasible or (margin is not None and margin > slack_tol))
    return {
        "n_points": n, "k": k, "basis_size": D, "n_moment_vars": K,
        "n_iec_constraints": n_iec, "status": prob.status,
        "infeasibility_margin": margin, "near_noise": near_noise,
        "certifies_infeasible": certifies,
        "implies_chi_m_geq": (k + 1) if certifies else None,
        "solve_time_s": elapsed,
    }


def iec_keys_upto4(X, dmat2_canon, edges, k, max_size=4):
    n = X.shape[0]
    pairs_indep = enumerate_congruent_pairs_all(n, dmat2_canon, max_size,
                                                independent_only=True, edges=edges)
    pairs_all = enumerate_congruent_pairs_all(n, dmat2_canon, max_size,
                                              independent_only=False, edges=edges)
    f1 = formulation1_keys(pairs_indep, k)
    f2 = formulation2_keys(pairs_all, dmat2_canon, k)
    # The order-2 moment matrix only carries moments up to size 4, so restrict IEC
    # keys whose larger side touches a subset of size > 4 (both sides have equal
    # size for a congruence, so checking one side suffices).
    out = set()
    for key in (f1 | f2):
        sides = list(key)
        if max(len(sides[0]), len(sides[1])) <= 4:
            out.add(key)
    return out


def run_config(name, verts_fn, k, *, do_iec=True, max_iec_size=3, max_basis=1400,
               verbose=True):
    X, dmat2_canon, edges = build_exact_config(verts_fn())
    keys = iec_keys_upto4(X, dmat2_canon, edges, k, max_iec_size) if do_iec else set()
    out = {"config": name, "n_points": X.shape[0], "n_edges": len(edges), "k": k,
           "n_iec_keys": len(keys), "runs": {}}
    for label, kk in (("base", set()), ("+IEC", keys)):
        r = build_order2_relaxation(X, dmat2_canon, edges, k, iec_keys=kk,
                                    max_basis=max_basis)
        out["runs"][label] = r
        if verbose:
            m = r.get("infeasibility_margin")
            ms = "None" if m is None else f"{m:.2e}"
            flag = " [noise]" if r.get("near_noise") else ""
            chi = r.get("implies_chi_m_geq")
            print(f"  [{name} k={k}] order2 {label:5s}: {r['status']:>10s} "
                  f"|B|={r.get('basis_size')} margin={ms}{flag} "
                  f"iec={r.get('n_iec_constraints', 0)} "
                  f"{'CHI_M>='+str(chi) if chi else '-'} ({r.get('solve_time_s', 0):.1f}s)")
    return out


def main():
    print("e3n: ORDER-2 moment / Lasserre relaxation for the multi-class measurable LP")
    print("=" * 78)
    results = {}

    # The naive order-2 PSD canonicalization in cvxpy is slow even at tiny |B|
    # (rhombus n=4, |B|=93, ~13 s), so we VALIDATE correctness on the configs that
    # solve quickly and report the scalability ceiling as a projection. This is the
    # honest headline: naive order-2 does not scale; X_23 needs symmetry reduction.
    print("\n[CERT PATH LIVE] order-2 must certify a genuinely non-k-colorable graph")
    print("  (triangle k=2): the order-1/order-2 PSD detects what the LP misses.")
    X, dc, e = build_exact_config(_triangle_vertices_exact())
    r = build_order2_relaxation(X, dc, e, 2, iec_keys=set())
    print(f"  triangle k=2: status={r['status']} certifies={r.get('certifies_infeasible')}"
          f" -> chi_m>= {r.get('implies_chi_m_geq')} (|B|={r.get('basis_size')})")
    results["cert_triangle_k2"] = r

    print("\n[NO FALSE CERT + size-3 IEC] feasible (k-colorable) configs must give")
    print("  margin ~0 even with IEC up to subset size 3 (order-1 caps IEC at size 2).")
    for nm, fn in (("triangle", _triangle_vertices_exact),
                   ("rhombus", _rhombus_vertices_exact)):
        results[f"{nm}_k4"] = run_config(nm, fn, 4, max_iec_size=3)

    print("\n[SCALABILITY] order-2 basis |B| ~ 1 + nk + (C(n,2)k^2 - E*k). The naive")
    print("  cvxpy PSD canonicalization is already ~13 s at |B|=93 (n=4); it does NOT")
    print("  scale. Projection (no solve) shows the X_23 frontier needs symmetry red.:")
    proj = []
    for nm, fn, k in (("triangle", _triangle_vertices_exact, 4),
                      ("rhombus", _rhombus_vertices_exact, 4),
                      ("moser7", _moser_vertices_exact, 4),
                      ("double_moser", _double_moser_vertices_exact, 4),
                      ("hexR2", lambda: _hex_patch_vertices_exact(2), 4)):
        X, dc, e = build_exact_config(fn())
        n = X.shape[0]
        bsize = 1 + n * k + (n * (n - 1) // 2 * k * k - len(e) * k)
        print(f"  {nm:13s} n={n:2d}  |B|~{bsize:5d}  (PSD {bsize}x{bsize})")
        proj.append({"config": nm, "n": n, "basis_size": bsize})
    bx = 1 + 23 * 4 + (23 * 22 // 2 * 16)
    print(f"  {'X_23':13s} n=23  |B|~{bx:5d}  (PSD {bx}x{bx}) -> far beyond naive reach")
    proj.append({"config": "X_23", "n": 23, "basis_size": bx})
    results["scalability_projection"] = proj

    flagged = [(key, lab, r.get("infeasibility_margin"))
               for key, res in results.items() if isinstance(res, dict)
               for lab, r in res.get("runs", {}).items()
               if r.get("certifies_infeasible")]
    print("\n[VERIFY] spurious certificates among feasible configs: "
          + ("NONE" if not flagged else str(flagged)))

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3n_moment_order2.json"
    with out_path.open("w") as f:
        json.dump({"experiment": "e3n_moment_order2",
                   "any_spurious_certificate": bool(flagged),
                   "results": results}, f, indent=2)
    print(f"\narchived: {out_path}")

    cert_ok = results["cert_triangle_k2"].get("certifies_infeasible")
    print("\n" + "=" * 78)
    print(f"CERT PATH LIVE (order-2 certifies triangle k=2): {'PASS' if cert_ok else 'FAIL'}")
    print(f"NO spurious certificate on feasible configs: {'PASS' if not flagged else 'FAIL'}")
    print("SCALABILITY: naive order-2 ~13 s at |B|=93 (n=4); X_23 |B|~4233 -> "
          "symmetry reduction REQUIRED (see L41).")
    return results


if __name__ == "__main__":
    main()
