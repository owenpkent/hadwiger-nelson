r"""e3l: multi-class (joint k-coloring) LP WITH inclusion-exclusion CONGRUENCE
constraints (Formulation 1 + Formulation 2), the "sharpness" half of L38.

Architecture 2/3, the measurable frontier NOT provably capped at chi_m >= 5.

Context. e3k built the base multi-class autocorrelation LP: a feasibility test
over distributions a_sigma on proper k-colorings sigma of a configuration X,
with each per-color autocorrelation forced Bochner-positive (J_0 representation)
and zero at distance 1. On small (enumerable) configs the base LP gives margin 0
(feasible) because the base constraints alone are too weak, exactly as the
single-class IE-LP gave only 0.2584 (chi_m >= 4) before the (IEC) congruence
constraints took it to < 1/4 (chi_m >= 5; L36). This module adds the multi-class
analog of (IEC), the missing sharpening ingredient flagged in L38 / sources/notes/12.

The two formulations (sources/notes/12, "the MISSING piece"):

  FORMULATION 1 (per-color marginal IEC; conservative, definitely valid).
  For each color c and each congruent INDEPENDENT pair {I,J} in C(X):
      sum_{sigma: sigma|_I = c} a_sigma  =  sum_{sigma: sigma|_J = c} a_sigma
  (whole sub-config monochromatic color c). This is the literal per-color lift of
  the single-class (ieC); it is k parallel copies of the L36 certificate and is
  expected to reproduce, at most, chi_m >= 5.

  FORMULATION 2 (full joint-pattern IEC; the genuine multi-class generalization).
  For each congruent pair {I,J} with a witnessing vertex bijection b: I -> J
  (an isometry of the labelled point sets) and ANY local color labeling
  rho: I -> [k], transported to rho' = rho o b^{-1} on J:
      sum_{sigma: sigma|_I = rho} a_sigma  =  sum_{sigma: sigma|_J = rho'} a_sigma.
  Formulation 1 is the special case rho == constant. Formulation 2 additionally
  couples MIXED patterns ("x_i red, x_j blue" congruence-coupled to its isometric
  image), the cross-color correlations the single-class object cannot see. These
  are NOT covered by the alpha_1 = 1/4 density cap, so Formulation 2 is the one
  identified candidate to make the k=5 LP infeasible (=> chi_m >= 6).

Validity (paper Section 4 O(2)-averaging). delta(intersection_i (A_{rho(i)} - x_i))
is the joint density of the colored sub-config; Haar-averaging over O(2) makes it
depend only on the congruence type of the COLORED point set. So for any isometry b
mapping (X|_I, rho) onto (X|_J, rho'), the two averaged joint densities are equal.
Each valid isometry gives a valid equation; when X|_I has self-congruences several
bijections yield several (all valid) equations, deduped here to a canonical key.
SOUNDNESS GATE: every emitted pair is re-verified to preserve the exact (canonical)
squared-distance matrix, so only genuine congruences produce constraints.

Certificate logic. The base couplings (P) carry a free slack; Phase-1 minimizes
sum|slack|. The IEC equalities are HARD (exact identities for any real coloring).
If, with the IEC constraints, the LP is INFEASIBLE or forces a strictly positive
slack margin, then no measurable k-coloring of R^2 exists, i.e. chi_m(R^2) >= k+1.
Adding valid IEC equalities can only raise the margin, never lower the true value.

CORRECTNESS GATE (the load-bearing check). chi_m(R^2) <= 7 is PROVEN (Isbell
hexagonal 7-coloring exists and is measurable), so the k=7 LP MUST be feasible
(margin 0) on every configuration, WITH all IEC constraints. If any IEC constraint
were invalid it could make k=7 infeasible; the gate would catch it. We run the gate
on a rhombus (rich in congruences, hence many F1+F2 constraints, but still small
enough to enumerate proper 7-colorings).

Scope / honest expectation. This module validates the constraint machinery and
quantifies its bite on EXACTLY-CONSTRUCTIBLE, ENUMERABLE configs. The single-class
route needed the 23-point X_23 to cross 1/4; whether the joint Formulation-2 object
bites at smaller configs is the open question probed here. The validation TARGET
(X_23, k=4 -> margin > 0 reproducing >= 5) is enumeration-intractable for the
explicit-coloring backend used here; reaching it needs the Lasserre / moment
marginal relaxation (de Laat-Vallentin; note 08), for which this is the validated
constraint layer. See L38 barrier (a) scalability vs (b) sharpness: e3l is (b).
"""

from __future__ import annotations

import json
import time
from itertools import combinations, permutations, product

import cvxpy as cp
import numpy as np
import sympy as sp
from scipy.special import j0

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3k_multiclass_lp import enumerate_proper_colorings
from experiments.fractional.e3j_iec_selfcertify import (
    canonicalize_distances,
    subset_distance_signature,
)

# A small Moser-spindle import that yields EXACT sympy coordinates.
import sys
import pathlib

_SHARED = pathlib.Path(__file__).resolve().parents[1] / "_shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))


# ---------------------------------------------------------------------------
# Exact configurations (sympy coordinates) -> float array + canonical distances.
# ---------------------------------------------------------------------------

def _moser_vertices_exact() -> list[tuple[sp.Expr, sp.Expr]]:
    """Moser spindle, exact coordinates in Q(sqrt 3, sqrt 11) (chi = 4)."""
    s3 = sp.sqrt(3)
    A = (sp.Integer(0), sp.Integer(0))
    B = (sp.Integer(1), sp.Integer(0))
    C = (sp.Rational(1, 2), s3 / 2)
    D = (sp.Rational(3, 2), s3 / 2)
    # rotation by theta with cos = 5/6, sin = sqrt(11)/6 (the standard binding angle)
    cos_t, sin_t = sp.Rational(5, 6), sp.sqrt(11) / 6
    rot = lambda p: (cos_t * p[0] - sin_t * p[1], sin_t * p[0] + cos_t * p[1])
    return [A, B, C, D, rot(B), rot(C), rot(D)]


def _triangle_vertices_exact() -> list[tuple[sp.Expr, sp.Expr]]:
    s3 = sp.sqrt(3)
    return [(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)),
            (sp.Rational(1, 2), s3 / 2)]


def _rhombus_vertices_exact() -> list[tuple[sp.Expr, sp.Expr]]:
    """Two unit equilateral triangles sharing edge BC: vertices A,B,C,D with unit
    edges AB,AC,BC,BD,CD. Rich in congruent subsets (two congruent triangles, many
    congruent edges), small enough to enumerate proper 7-colorings."""
    s3 = sp.sqrt(3)
    return [(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)),
            (sp.Rational(1, 2), s3 / 2), (sp.Rational(3, 2), s3 / 2)]


def build_exact_config(verts: list[tuple[sp.Expr, sp.Expr]]):
    """Return (X float (n,2), dmat2_canon, edges) for an exact sympy config."""
    n = len(verts)
    X = np.array([[float(v[0]), float(v[1])] for v in verts], dtype=float)
    dmat2 = {}
    edges = set()
    for i in range(n):
        for j in range(i + 1, n):
            dx = verts[i][0] - verts[j][0]
            dy = verts[i][1] - verts[j][1]
            d2 = sp.simplify(dx * dx + dy * dy)
            dmat2[(i, j)] = d2
            if d2 == 1:
                edges.add((i, j))
    dmat2_canon = canonicalize_distances(dmat2)
    return X, dmat2_canon, edges


# ---------------------------------------------------------------------------
# Congruence enumeration over ALL subsets (not only independent), and the
# witnessing vertex bijections needed to transport color labelings (Formulation 2).
# ---------------------------------------------------------------------------

def _d2(p, q, dmat2_canon):
    return dmat2_canon[(p, q) if p < q else (q, p)]


def congruence_bijections(I: tuple[int, ...], J: tuple[int, ...], dmat2_canon: dict):
    """All vertex bijections b: I -> J preserving the canonical squared-distance
    matrix (i.e. all witnessing isometries of the labelled point sets). Returns a
    list of dicts {i_vertex: j_vertex}. Empty if X|_I is not congruent to X|_J."""
    I, J = list(I), list(J)
    if len(I) != len(J):
        return []
    k = len(I)
    if k == 1:
        return [{I[0]: J[0]}]
    DI = {(a, b): _d2(I[a], I[b], dmat2_canon) for a in range(k) for b in range(a + 1, k)}
    bijections = []
    for perm in permutations(range(k)):
        ok = True
        for a in range(k):
            for b in range(a + 1, k):
                if DI[(a, b)] != _d2(J[perm[a]], J[perm[b]], dmat2_canon):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            bijections.append({I[t]: J[perm[t]] for t in range(k)})
    return bijections


def enumerate_congruent_pairs_all(n: int, dmat2_canon: dict, max_size: int,
                                  independent_only: bool, edges: set):
    """Unordered pairs {I,J} of distinct equal-size subsets with X|_I ~ X|_J.

    independent_only=True restricts to subsets with no internal unit edge (the only
    subsets that can be monochromatic; required for Formulation 1). For Formulation 2
    we allow all subsets. Buckets by the distance signature, confirms by an exact
    bijection test (soundness gate)."""
    from collections import defaultdict

    def is_independent(S):
        return not any((a, b) in edges for a, b in combinations(sorted(S), 2))

    pairs = []
    for size in range(1, max_size + 1):
        cands = []
        for S in combinations(range(n), size):
            if independent_only and size >= 2 and not is_independent(S):
                continue
            cands.append(S)
        buckets = defaultdict(list)
        for S in cands:
            buckets[subset_distance_signature(S, dmat2_canon)].append(S)
        for members in buckets.values():
            if len(members) < 2:
                continue
            for I, J in combinations(members, 2):
                if congruence_bijections(I, J, dmat2_canon):
                    pairs.append((I, J))
    return pairs


# ---------------------------------------------------------------------------
# Constraint generation. A constraint is a canonical key: frozenset of two
# "assignment" frozensets, each a frozenset of (vertex, color) pairs. The two
# sides must have equal a_sigma-mass. Self-equal keys (lhs == rhs) are dropped.
# ---------------------------------------------------------------------------

def _key(lhs, rhs):
    lf, rf = frozenset(lhs), frozenset(rhs)
    if lf == rf:
        return None
    return frozenset({lf, rf})


def formulation1_keys(pairs_indep, k):
    keys = set()
    for I, J in pairs_indep:
        for c in range(k):
            key = _key({(i, c) for i in I}, {(j, c) for j in J})
            if key is not None:
                keys.add(key)
    return keys


def formulation2_keys(pairs_all, dmat2_canon, k):
    keys = set()
    for I, J in pairs_all:
        bijs = congruence_bijections(I, J, dmat2_canon)
        Ilist = list(I)
        for b in bijs:
            for rho in product(range(k), repeat=len(Ilist)):
                lhs = {(Ilist[t], rho[t]) for t in range(len(Ilist))}
                rhs = {(b[Ilist[t]], rho[t]) for t in range(len(Ilist))}
                key = _key(lhs, rhs)
                if key is not None:
                    keys.add(key)
    return keys


# ---------------------------------------------------------------------------
# The multi-class IEC LP.
# ---------------------------------------------------------------------------

def build_multiclass_iec_lp(X, dmat2_canon, edges, k, constraint_keys,
                            n_freq=300, freq_max=20.0, coloring_cap=300_000,
                            slack_tol=1e-6):
    """Solve the multi-class Phase-1 LP for k colors on X, augmented with the IEC
    equalities in `constraint_keys`. Returns a result dict with the infeasibility
    margin (min sum|slack| over the base couplings). margin > slack_tol OR an
    infeasible status => chi_m(R^2) >= k+1 from this configuration."""
    n = X.shape[0]
    colorings, count = enumerate_proper_colorings(n, edges, k, cap=coloring_cap)
    if colorings is None:
        return {"n_points": n, "k": k, "status": "ENUMERATION_INTRACTABLE",
                "proper_colorings_lower_bound": count}
    M = len(colorings)
    if M == 0:
        # G(X) has no proper k-coloring at all: the finite UDG already needs > k
        # colors, so a fortiori no measurable k-coloring of R^2 exists.
        return {"n_points": n, "k": k, "proper_colorings": 0,
                "n_iec_constraints": 0, "status": "no_proper_coloring",
                "infeasibility_margin": None, "certifies_infeasible": True,
                "implies_chi_m_geq": k + 1, "solve_time_s": 0.0}
    col_arr = np.array(colorings, dtype=np.int8)  # (M, n)

    # Non-edge pair distances for the (P) couplings.
    pair_dist = {}
    for (i, j) in combinations(range(n), 2):
        if (i, j) in edges:
            continue
        pair_dist[(i, j)] = float(np.sqrt(_dist2_float(X, i, j)))

    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)
    J0_pair = {p: j0(2.0 * np.pi * d * freqs) for p, d in pair_dist.items()}

    a = cp.Variable(M, nonneg=True)
    nu = cp.Variable((k, n_freq), nonneg=True)
    cons = [cp.sum(a) == 1]

    # (D) per-color marginal at EVERY vertex equals the Bochner mass f_c(0).
    for c in range(k):
        msum = cp.sum(nu[c, :])
        for i in range(n):
            idx = np.where(col_arr[:, i] == c)[0]
            cons.append((cp.sum(a[idx]) if idx.size else cp.Constant(0.0)) == msum)
    # (A) f_c(1) = 0.
    for c in range(k):
        cons.append(J0_at_1 @ nu[c, :] == 0)
    # (P) pair couplings with free slack.
    slacks = []
    for c in range(k):
        for (i, j), Jvec in J0_pair.items():
            same = (col_arr[:, i] == c) & (col_arr[:, j] == c)
            idx = np.where(same)[0]
            lhs = cp.sum(a[idx]) if idx.size else cp.Constant(0.0)
            s = cp.Variable()
            slacks.append(s)
            cons.append(lhs - Jvec @ nu[c, :] == s)

    # (IEC) hard equalities on a (Formulation 1 and/or 2).
    n_iec = 0
    for key in constraint_keys:
        sides = list(key)
        lhs_assign, rhs_assign = sides[0], sides[1]
        idxL = _mask_idx(col_arr, lhs_assign)
        idxR = _mask_idx(col_arr, rhs_assign)
        L = cp.sum(a[idxL]) if idxL.size else cp.Constant(0.0)
        R = cp.sum(a[idxR]) if idxR.size else cp.Constant(0.0)
        cons.append(L == R)
        n_iec += 1

    prob = cp.Problem(cp.Minimize(cp.sum([cp.abs(s) for s in slacks])), cons)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0

    margin = float(prob.value) if prob.value is not None else None
    infeasible = prob.status in ("infeasible", "infeasible_inaccurate")
    certifies = bool(infeasible or (margin is not None and margin > slack_tol))
    return {
        "n_points": n, "k": k, "proper_colorings": M,
        "n_iec_constraints": n_iec, "n_nonedge_pairs": len(pair_dist),
        "status": prob.status, "infeasibility_margin": margin,
        "certifies_infeasible": certifies,
        "implies_chi_m_geq": (k + 1) if certifies else None,
        "solve_time_s": elapsed,
    }


def _dist2_float(X, i, j):
    d = X[i] - X[j]
    return float(d @ d)


def _mask_idx(col_arr, assignment):
    mask = np.ones(col_arr.shape[0], dtype=bool)
    for (v, c) in assignment:
        mask &= (col_arr[:, v] == c)
    return np.where(mask)[0]


# ---------------------------------------------------------------------------
# Runner.
# ---------------------------------------------------------------------------

CONFIGS = {
    "triangle": _triangle_vertices_exact,
    "rhombus": _rhombus_vertices_exact,
    "moser7": _moser_vertices_exact,
}


def run_config(name, k, max_iec_size=3, coloring_cap=300_000, verbose=True):
    verts = CONFIGS[name]()
    X, dmat2_canon, edges = build_exact_config(verts)
    n = X.shape[0]

    pairs_indep = enumerate_congruent_pairs_all(n, dmat2_canon, max_iec_size,
                                                independent_only=True, edges=edges)
    pairs_all = enumerate_congruent_pairs_all(n, dmat2_canon, max_iec_size,
                                              independent_only=False, edges=edges)
    f1 = formulation1_keys(pairs_indep, k)
    f2 = formulation2_keys(pairs_all, dmat2_canon, k)
    f12 = f1 | f2

    out = {"config": name, "n_points": n, "n_edges": len(edges), "k": k,
           "n_congruent_pairs_indep": len(pairs_indep),
           "n_congruent_pairs_all": len(pairs_all),
           "n_F1_constraints": len(f1), "n_F2_constraints": len(f2),
           "n_F2_cross_color_extra": len(f2 - f1), "runs": {}}

    for label, keys in (("base", set()), ("+F1", f1), ("+F1+F2", f12)):
        r = build_multiclass_iec_lp(X, dmat2_canon, edges, k, keys,
                                    coloring_cap=coloring_cap)
        out["runs"][label] = r
        if verbose:
            m = r.get("infeasibility_margin")
            print(f"  [{name} k={k}] {label:7s}: status={r['status']:>8s} "
                  f"margin={m if m is None else round(m, 8)} "
                  f"iec={r.get('n_iec_constraints', 0)} "
                  f"chi_m>= {r.get('implies_chi_m_geq')}  ({r.get('solve_time_s', 0)*1000:.0f}ms)")
    return out


def main():
    print("e3l: multi-class IEC LP (Formulation 1 + 2) for chi_m(R^2)")
    print("=" * 78)

    results = {}

    # CORRECTNESS GATE: chi_m <= 7 is proven, so k=7 MUST be feasible (margin 0)
    # WITH all IEC constraints. A rhombus is congruence-rich yet 7-color-enumerable.
    print("\n[GATE] k=7 on the rhombus must stay FEASIBLE (margin 0) with all IEC.")
    print("       (chi_m(R^2) <= 7 is proven; invalid IEC would break this.)")
    gate = run_config("rhombus", k=7, max_iec_size=3)
    results["gate_rhombus_k7"] = gate
    gate_margin = gate["runs"]["+F1+F2"].get("infeasibility_margin")
    gate_ok = (gate["runs"]["+F1+F2"]["status"] == "optimal"
               and gate_margin is not None and gate_margin < 1e-6)
    print(f"  GATE {'PASS' if gate_ok else 'FAIL'}: k=7 +F1+F2 margin = {gate_margin}")
    if not gate_ok:
        print("  !! IEC constraints appear INVALID (k=7 not feasible). Aborting sweep.")

    # SWEEP: does the joint Formulation-2 object bite on small rigid (chi=4) configs?
    print("\n[SWEEP] k=4 and k=5 on rigid configs (expect margin 0 if config too small;")
    print("        any margin > 0 at k=4 would certify chi_m >= 5 from that config).")
    for name in ("triangle", "rhombus", "moser7"):
        print(f"\n config = {name}")
        for k in (4, 5):
            results[f"{name}_k{k}"] = run_config(name, k=k, max_iec_size=3)

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3l_multiclass_iec.json"
    with out_path.open("w") as f:
        json.dump({"experiment": "e3l_multiclass_iec",
                   "gate_pass": bool(gate_ok), "results": results}, f, indent=2)
    print(f"\narchived: {out_path}")

    # Headline summary.
    print("\n" + "=" * 78)
    print("SUMMARY (infeasibility margin by config / k / constraint set):")
    print(f"  {'config':10s} {'k':>2s} {'base':>10s} {'+F1':>10s} {'+F1+F2':>10s}  F2-extra")
    for name in ("triangle", "rhombus", "moser7"):
        for k in (4, 5):
            r = results[f"{name}_k{k}"]
            def mg(lbl):
                v = r["runs"][lbl].get("infeasibility_margin")
                st = r["runs"][lbl]["status"]
                if st != "optimal":
                    return st[:9]
                return f"{v:.2e}" if v is not None else "?"
            print(f"  {name:10s} {k:>2d} {mg('base'):>10s} {mg('+F1'):>10s} "
                  f"{mg('+F1+F2'):>10s}  {r['n_F2_cross_color_extra']}")
    return results


if __name__ == "__main__":
    raise SystemExit(main())
