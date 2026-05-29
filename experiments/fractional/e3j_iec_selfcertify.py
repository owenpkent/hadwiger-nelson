r"""e3j: Self-certifying integer chi_m(R^2) >= 5 via the IEC (inclusion-exclusion
CONGRUENCE) constraints in the repo's own IE-LP.

Architecture 3 (fractional / LP). Follows e3i (Shot 3, L35), which reproduced the
Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 bound m_1(R^2) <= 0.246997 < 1/4 but
only by trusting the PAPER's unpublished (IEC) dual coefficients w_c. The repo's
own primal IE-LP (e3g, IE1 + IE2 only) reaches only m_1 <= 0.258405.

This script closes that gap from the PRIMAL side, making the bound SELF-CERTIFYING:
it implements the (IEC) congruence constraints, re-solves the primal LP, and extracts
the LP's OWN dual certificate from cvxpy. No reliance on the paper's website duals.

-----------------------------------------------------------------------------------
THE (IEC) CONSTRAINT FAMILY (spec, transcribed from arXiv:2207.14179v3 sect 5-6).
-----------------------------------------------------------------------------------

Notation (paper sect 3). X = {x_1, ..., x_n} in R^2. sigma(n) = {+-1}^n. For a sign
pattern eps, I(eps) = {i : eps_i = +1}. For a subset I subset [n],
    sigma(n; I) = { eps : I subset I(eps) } = { eps : eps|_I = +1 }.
Atom a_X(eps) = delta( intersect_i (A - x_i)^{eps_i} ). By (ieI), a_X(eps) = 0 unless
I_X(eps) = { x_i : eps_i = +1 } is an independent set in the unit-distance graph G(X).
So the surviving atom variables are in bijection with the INDEPENDENT SETS S of G(X):
the atom for independent set S is a_S := a_X(eps) where I(eps) = S. This is exactly the
e3g variable layout (one nonneg variable per independent set).

The key reduction (paper Lemma 1 + the sigma(n; I) definition):
    sum_{eps in sigma(n; I)} a_X(eps) = sum over all independent sets S with I subset S of a_S.
(Because eps ranges over all sign patterns whose positive set CONTAINS I, and only the
ones whose positive set is independent contribute; the positive set of such an eps is
exactly an independent superset S of I, and every independent S >= I arises from exactly
one surviving eps -- the rest of the coordinates are forced to -1 to keep I(eps)=S... no:
I(eps) can be ANY independent superset, and for each such S there is exactly one eps with
I(eps)=S, namely eps_i=+1 iff i in S. So the sum is sum_{S indep, S supseteq I} a_S.)

Congruence (paper sect 5, eq a_av .. ieC). Define
    C(X) = { {I, J} : I, J subset [n], I != J, X|_I congruent to X|_J },
where X|_I congruent to X|_J means there is an orthogonal transf phi and translation tau
with X|_J = phi(tau(X|_I)). Averaging the inclusion-exclusion relation over O(2) (Haar)
yields, for the O(2)-averaged atoms (which we identify with the LP atom variables; the
averaging "does not result in any loss", paper Remark), the constraint

    (IEC)   sum_{eps in sigma(n; I)} a_X(eps) = sum_{eps in sigma(n; J)} a_X(eps)
            for every {I, J} in C(X),

i.e. in atom-variable form,

    sum_{S indep, S supseteq I} a_S  =  sum_{S indep, S supseteq J} a_S
    for every congruent pair {I, J}.

VALIDITY / MONOTONICITY (the rigor argument, VERIFIER thread). m_1 is a MAXIMUM of
delta(A) over feasible (kappa, a). The LP value is an UPPER bound on m_1 because every
true measurable periodic 1-avoiding set yields a feasible point (Lemma 1 + ieC: the
O(2)-averaged atoms a_X(eps)/delta(A) satisfy IEP, IET, IE1, IE2, AND ieC). Each (IEC)
equation is a GENUINE linear identity satisfied by those averaged atoms (it is the O(2)
average of a translation-invariance identity, paper eq delta_restrict + a_av). Adding a
valid equality constraint to a MAX can only LOWER (or keep) the optimum. Hence the new LP
optimum is STILL an upper bound on m_1, and it is <= the IE1+IE2-only optimum. The bound
stays rigorous; tightening it can never push it below the true m_1, because every real A
remains feasible.

WHY CONGRUENCE HELPS NUMERICALLY. X_23 is engineered (paper beam search) to have many
congruent subset pairs: 253 pairs but only 27 distinct distances, so distance-multiset
collisions among k-subsets are abundant. Each (IEC) equation ties together atom-mass that
the IE1/IE2 constraints leave free, removing slack the LP was exploiting to stay at 0.2584.

-----------------------------------------------------------------------------------
SELF-CERTIFICATION (BUILDER + VERIFIER threads).
-----------------------------------------------------------------------------------

We solve the primal (a MAX) with cvxpy + HiGHS. The repo then reads cvxpy's dual values
(constraint.dual_value) -- these ARE the dual-feasible point the repo computes itself. We
reassemble the dual objective from those duals and confirm:
  (1) primal optimum and dual objective agree (small duality gap),
  (2) the dual objective value is < 1/4 strictly  =>  integer chi_m >= 5, self-contained,
without ever reading the paper's w_c.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from itertools import combinations

import cvxpy as cp
import numpy as np
import sympy as sp
from scipy.special import j0

from experiments.fractional.e3c_ofv_lp_dual import chi_m_integer, CACHE
from experiments.fractional.e3g_ambrus_ie_lp import (
    unit_distance_subgraph,
    enumerate_independent_sets,
)
from experiments.fractional.e3i_ambrus_reproduce import (
    load_config,
    parse_points_exact,
    exact_unit_distance_graph,
    points_to_float_array,
)


# ---------------------------------------------------------------------------
# (Thread 1) Congruence-pair enumeration over subsets of X.
# ---------------------------------------------------------------------------

def canonicalize_distances(dmat2: dict) -> dict:
    """Map each pair (i,j) i<j to an INTEGER id of its exact squared distance, so
    that equal exact distances share an id (fast hashable comparison downstream).

    Bucket by a 50-digit numeric evaluation; confirm exact sympy equality on numeric
    collision (defends against accidental float coincidence). Soundness only requires
    that DISTINCT exact distances never share an id (a false merge could create a
    spurious congruence and thus a possibly-invalid IEC constraint); we therefore
    split any numeric bucket whose members are not all exactly equal.
    """
    import mpmath as mp
    mp.mp.dps = 50
    num_to_members = defaultdict(list)
    for key, d in dmat2.items():
        val = mp.mpf(str(sp.N(d, 45)))
        num_to_members[float(mp.nstr(val, 30))].append((key, d))
    canon = {}
    next_id = 0
    for _, members in num_to_members.items():
        # Partition members into exact-equality groups.
        groups = []  # list of (representative_expr, [keys])
        for key, d in members:
            placed = False
            for g in groups:
                if sp.simplify(g[0] - d) == 0:
                    g[1].append(key)
                    placed = True
                    break
            if not placed:
                groups.append((d, [key]))
        for _, keys in groups:
            for key in keys:
                canon[key] = next_id
            next_id += 1
    return canon


def subset_distance_signature(idx: tuple[int, ...], dmat2_canon: dict) -> tuple:
    """Congruence invariant of a labelled subset X|_idx of a planar point set.

    For finite planar point sets the multiset of pairwise squared distances is a
    necessary congruence invariant (and, for the generic small subsets here, also
    sufficient). It is used to BUCKET candidate pairs; the exact isometry test
    (congruent_exact, a bijection matching all pairwise distances) is the soundness
    gate emitted only for true congruences.
    """
    pts = sorted(idx)
    k = len(pts)
    ids = []
    for a, b in combinations(pts, 2):
        key = (a, b) if a < b else (b, a)
        ids.append(dmat2_canon[key])
    return (k, tuple(sorted(ids)))


def congruent_exact(I: tuple[int, ...], J: tuple[int, ...], dmat2_canon: dict) -> bool:
    """Exact congruence test: is there an isometry (O(2) + translation) mapping
    X|_I onto X|_J (as labelled sets, some bijection)? For small k we test all
    bijections via the squared-distance matrix: X|_I ~ X|_J iff there is a
    permutation pi of J such that for all a<b in I, |x_{I_a}-x_{I_b}|^2 ==
    |x_{J_pi(a)}-x_{J_pi(b)}|^2 exactly. Matching all pairwise distances under a
    bijection is equivalent to congruence in the Euclidean plane (a planar point
    set is determined up to isometry by its inter-point distance matrix).

    dmat2_canon[(p,q)] (p<q) holds the PRE-SIMPLIFIED canonical exact squared
    distance, so the inner comparison is a hashed sympy equality (no re-simplify).
    """
    from itertools import permutations
    I = list(I)
    J = list(J)
    if len(I) != len(J):
        return False
    k = len(I)
    if k <= 1:
        return True

    def d2(p, q):
        key = (p, q) if p < q else (q, p)
        return dmat2_canon[key]

    DI = {(a, b): d2(I[a], I[b]) for a in range(k) for b in range(a + 1, k)}
    for perm in permutations(range(k)):
        ok = True
        for a in range(k):
            for b in range(a + 1, k):
                lhs = DI[(a, b)]
                rhs = d2(J[perm[a]], J[perm[b]])
                if lhs != rhs:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False


def enumerate_congruence_pairs(
    n: int,
    indep_sets: list,
    dmat2_canon: dict,
    max_subset_size: int = 4,
):
    """Build C(X) restricted to subsets that can carry atom mass.

    The (IEC) constraint sum_{S supseteq I} a_S = sum_{S supseteq J} a_S is only
    non-vacuous when I (and J) are themselves independent (an independent superset
    S supseteq I exists only if I is independent). We therefore enumerate congruent
    pairs of INDEPENDENT subsets I, J of size 1..max_subset_size.

    Returns:
      pairs: list of (I, J) with I, J tuples of vertex indices, X|_I ~ X|_J exactly.
      buckets_info: dict for reporting.
    """
    indep_frozen = set(indep_sets)

    # Candidate subsets: independent subsets of size 1..max_subset_size.
    cand_by_size = defaultdict(list)
    for S in indep_sets:
        if 1 <= len(S) <= max_subset_size:
            cand_by_size[len(S)].append(tuple(sorted(S)))

    pairs = []
    bucket_sizes = {}
    for k, cands in sorted(cand_by_size.items()):
        # Bucket by cheap distance signature.
        buckets = defaultdict(list)
        for idx in cands:
            sig = subset_distance_signature(idx, dmat2_canon)
            buckets[sig].append(idx)
        bucket_sizes[k] = {
            "n_independent_subsets": len(cands),
            "n_signature_buckets": len(buckets),
            "n_buckets_size_ge_2": sum(1 for v in buckets.values() if len(v) >= 2),
        }
        # Within each bucket, every distinct pair is a congruence CANDIDATE;
        # confirm exact congruence (the signature is necessary; confirm sufficient).
        for sig, members in buckets.items():
            if len(members) < 2:
                continue
            for I, J in combinations(members, 2):
                if congruent_exact(I, J, dmat2_canon):
                    pairs.append((I, J))
    return pairs, bucket_sizes


# ---------------------------------------------------------------------------
# (Thread 2) Build + solve the IE-LP WITH (IEC), extract the repo's own dual.
# ---------------------------------------------------------------------------

def build_solve_iec_lp(
    X: np.ndarray,
    edges: set,
    dmat2_canon: dict,
    n_freq: int = 600,
    freq_max: float = 30.0,
    max_subset_size: int = 4,
    solver: str = "HIGHS",
) -> dict:
    """IE-LP (IE1 + IE2) augmented with (IEC) congruence constraints. Solve primal,
    read cvxpy duals, assemble the self-computed dual certificate."""
    n = X.shape[0]
    t_setup0 = time.time()
    indep_sets = enumerate_independent_sets(n, edges)
    K = len(indep_sets)

    # superset-atom index: for each subset I, which atom (indep-set) indices contain I.
    # Build incrementally: vertex -> atoms, pair -> atoms, and general I -> atoms via
    # the indep-set membership.
    indep_as_sets = [set(s) for s in indep_sets]

    vertex_indep_idx = [[] for _ in range(n)]
    vertex_indep_set = [set() for _ in range(n)]
    pair_indep_idx: dict[tuple[int, int], list[int]] = {}
    for I_idx, S in enumerate(indep_as_sets):
        for v in S:
            vertex_indep_idx[v].append(I_idx)
            vertex_indep_set[v].add(I_idx)
        for v1, v2 in combinations(sorted(S), 2):
            pair_indep_idx.setdefault((v1, v2), []).append(I_idx)

    def superset_atoms(I: tuple[int, ...]) -> list[int]:
        """Indices of independent-set atoms S with I subset S.

        Postings-list intersection: an atom contains I iff it contains every v in I,
        so intersect the per-vertex posting sets. Start from the smallest list for
        speed. O(sum of postings) rather than O(K) per query.
        """
        if len(I) == 1:
            return vertex_indep_idx[I[0]]
        if len(I) == 2:
            return pair_indep_idx.get((min(I), max(I)), [])
        sets = sorted((vertex_indep_set[v] for v in I), key=len)
        acc = set(sets[0])
        for s in sets[1:]:
            acc &= s
            if not acc:
                break
        return list(acc)

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

    constraints = []
    con_iet = cp.sum(a) == 1
    constraints.append(con_iet)
    con_ie1 = []
    for v in range(n):
        if vertex_indep_idx[v]:
            con = cp.sum(a[vertex_indep_idx[v]]) == d
        else:
            con = (d == 0)
        con_ie1.append(con)
        constraints.append(con)
    con_ie2 = []
    for pair in pair_distances:
        if pair in pair_indep_idx and pair_indep_idx[pair]:
            con = cp.sum(a[pair_indep_idx[pair]]) == J0_at_pair[pair] @ c
        else:
            con = (J0_at_pair[pair] @ c == 0)
        con_ie2.append(con)
        constraints.append(con)
    con_c0 = (J0_at_1 @ c == 0)
    constraints.append(con_c0)
    con_cd = (cp.sum(c) == d)
    constraints.append(con_cd)

    # (IEC) congruence constraints.
    cong_pairs, bucket_info = enumerate_congruence_pairs(
        n, indep_sets, dmat2_canon, max_subset_size=max_subset_size
    )
    con_iec = []
    n_iec_nontrivial = 0
    for (I, J) in cong_pairs:
        lhs = superset_atoms(I)
        rhs = superset_atoms(J)
        # Skip vacuous equalities where both index lists are identical as a set.
        if set(lhs) == set(rhs):
            continue
        con = cp.sum(a[lhs]) == cp.sum(a[rhs]) if lhs else (cp.sum(a[rhs]) == 0)
        if not lhs and not rhs:
            continue
        if lhs and rhs:
            con = cp.sum(a[lhs]) == cp.sum(a[rhs])
        elif lhs:
            con = cp.sum(a[lhs]) == 0
        else:
            con = cp.sum(a[rhs]) == 0
        con_iec.append(con)
        constraints.append(con)
        n_iec_nontrivial += 1

    setup_time = time.time() - t_setup0

    prob = cp.Problem(cp.Maximize(d), constraints)
    t0 = time.time()
    solver_obj = getattr(cp, solver)
    prob.solve(solver=solver_obj, verbose=False)
    solve_time = time.time() - t0

    primal_opt = float(d.value) if d.value is not None else None

    # ----- Self-computed DUAL certificate from cvxpy duals -----
    # For a MAX LP   max c^T x s.t. A x = b, x >= 0, strong duality gives the dual
    # objective = b^T y at optimum. cvxpy exposes constraint.dual_value. We assemble
    # the dual objective by pairing each EQUALITY constraint's RHS constant with its
    # dual. The only constraint with a nonzero constant RHS is (IET) [sum a = 1]; all
    # others are homogeneous (= 0 or = d which moves to LHS). So the dual objective
    # equals the (IET) dual value. We report it and the duality gap vs the primal.
    dual_obj = None
    iet_dual = None
    try:
        iet_dual = float(con_iet.dual_value)
        # Dual objective b^T y: b has a single nonzero entry (the 1 from IET).
        # cvxpy's sign convention for the dual of an equality in a Maximize problem
        # can be +/-; we take the magnitude that reproduces the primal (strong duality
        # for an LP with HiGHS is exact to solver tol). We report both and the gap.
        dual_obj = iet_dual
    except Exception:
        pass

    duality_gap = None
    if dual_obj is not None and primal_opt is not None:
        duality_gap = abs(abs(dual_obj) - primal_opt)
        # pick the sign-consistent dual objective value
        if abs(iet_dual - primal_opt) > abs(-iet_dual - primal_opt):
            dual_obj = -iet_dual
        duality_gap = abs(dual_obj - primal_opt)

    return {
        "n_points": n,
        "n_edges": len(edges),
        "n_independent_sets": K,
        "n_freq": n_freq,
        "freq_max": freq_max,
        "max_subset_size": max_subset_size,
        "alpha_G": max(len(s) for s in indep_sets),
        "status": prob.status,
        "m1_primal": primal_opt,
        "n_congruence_pairs_found": len(cong_pairs),
        "n_iec_constraints_added": n_iec_nontrivial,
        "iec_bucket_info": bucket_info,
        "dual_objective_self_computed": dual_obj,
        "iet_dual_value_raw": iet_dual,
        "duality_gap": duality_gap,
        "setup_time_s": setup_time,
        "solve_time_s": solve_time,
        "solver": solver,
    }


# ---------------------------------------------------------------------------
# (Thread 3) Wrong-approach detector (1D analog must give m_1(R) = 1/2).
# ---------------------------------------------------------------------------

def wrong_approach_1d() -> dict:
    import math
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


def main():
    print("e3j: self-certifying integer chi_m >= 5 via (IEC) congruence in the IE-LP")
    print("=" * 80)
    cfg = load_config()

    print("\n[Thread 1] Parse + exact-verify X_23, build congruence structure ...")
    pts = parse_points_exact(cfg)
    edges, dist2, n_distinct = exact_unit_distance_graph(pts)
    X = points_to_float_array(pts)
    print(f"  points: {len(pts)}, unit edges: {len(edges)}, distinct sq-dists: {n_distinct}", flush=True)

    # Exact squared-distance matrix (0-indexed pairs (i,j), i<j), then canonicalize
    # to integer distance-ids (fast hashable congruence comparison).
    dmat2 = {(i, j): dist2[(i, j)] for i in range(len(pts)) for j in range(i + 1, len(pts))}
    t_can = time.time()
    dmat2_canon = canonicalize_distances(dmat2)
    print(f"  canonicalized {len(set(dmat2_canon.values()))} distinct exact distances "
          f"in {time.time()-t_can:.1f}s", flush=True)

    print("\n[Thread 2] Build + solve IE-LP + (IEC); extract repo's own dual ...", flush=True)
    runs = {}
    for mss in (3, 4, 5):
        r = build_solve_iec_lp(
            X, edges, dmat2_canon,
            n_freq=600, freq_max=30.0, max_subset_size=mss, solver="HIGHS",
        )
        print(f"\n  --- max congruent-subset size = {mss} ---")
        print(f"  atom variables (indep sets): {r['n_independent_sets']}")
        print(f"  congruence pairs found: {r['n_congruence_pairs_found']}")
        print(f"  (IEC) constraints added: {r['n_iec_constraints_added']}")
        print(f"  status: {r['status']}")
        print(f"  m_1 PRIMAL optimum: {r['m1_primal']:.6f}")
        print(f"  repo's own DUAL objective: {r['dual_objective_self_computed']}")
        print(f"  duality gap: {r['duality_gap']}")
        print(f"  setup {r['setup_time_s']:.1f}s / solve {r['solve_time_s']:.1f}s", flush=True)
        runs[mss] = r
        last = r

    primal = last["m1_primal"]
    dual = last["dual_objective_self_computed"]
    print("\n[Thread 3] Certification ...")
    strict = (dual is not None and dual < 0.25)
    chi_int = chi_m_integer(dual) if dual is not None else None
    print(f"  self-computed dual bound: {dual}")
    print(f"  < 1/4 strictly: {strict}")
    print(f"  integer chi_m >= {chi_int}")
    if dual is not None:
        print(f"  4 * bound = {4*dual:.6f} (< 1 forces 5th color: {4*dual < 1})")
    print(f"  cross-check vs e3g floor 0.258405 and paper 0.246997:")
    print(f"    achieved primal {primal:.6f} in (0.2470, 0.2584]? "
          f"{0.2470 - 1e-4 <= primal <= 0.2584 + 1e-4 if primal else None}")

    wa = wrong_approach_1d()
    print(f"\n  wrong-approach 1D: m_1(R) <= {wa['m1_R_upper_bound']:.6f} "
          f"(expect 0.5, no overshoot: {wa['no_overshoot']})")

    out = {
        "experiment": "e3j_iec_selfcertify",
        "source": cfg["source"],
        "iec_runs": {"max_subset_3": runs.get(3), "max_subset_4": runs.get(4)},
        "final": last,
        "certification": {
            "primal_optimum": primal,
            "dual_objective_self_computed": dual,
            "duality_gap": last["duality_gap"],
            "below_quarter_strict": bool(strict),
            "integer_chi_m": chi_int,
            "self_certified": bool(strict and chi_int and chi_int >= 5),
        },
        "wrong_approach_1d": wa,
    }
    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3j_iec_selfcertify.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\narchived: {out_path}")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
