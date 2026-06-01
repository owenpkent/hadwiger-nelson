r"""e3q: S_k-BLOCK-DIAGONALIZED ORDER-2 measurable moment SDP (Shot A, Part 1 step 2).

The payoff rung. L41 showed the naive order-2 SDP (e3n) is correct but does not
scale: its PSD block has side |B| ~ 1+nk+binom(n,2)k^2 (X_23 -> ~4141), out of reach.
L46 built and validated the order-1 block-diagonalization. This file ports the SAME
S_k color-symmetry reduction to ORDER 2, where it stops being a mere speedup and
becomes the thing that makes the order-2 frontier (k=4 retest >=5; k=5 open >=6)
runnable at X_23 scale.

WHY ORDER-2 NEEDS A REAL SYMMETRY-ADAPTED BASIS (not the order-1 shortcut). The
order-2 moment matrix, symmetrized over S_k (lossless, L44), is S_k-INVARIANT, so it
block-diagonalizes. But unlike order-1 (whose only nontrivial block was the n x n
standard block), the order-2 representation contains S_k-irreps with MULTIPLICITY > 1
(verified: the eigenspaces of a generic invariant matrix have the irrep dimensions
1,2,3,... but several copies each). Naively grouping eigenvectors of one invariant
matrix does NOT block-diagonalize a general invariant M (the copies of one irrep
couple). The correct construction (Murota-Kanno-Kojima-Kojima randomized block-
diagonalization of a matrix *-algebra; equivalently the de Laat-Vallentin coherent-
configuration reduction) ALIGNS the multiplicity copies:
  1. R  = Reynolds-average of a random symmetric matrix (an element of the commutant).
     Its eigenspaces are the irreducible subspaces (dim = d_lambda each).
  2. R2 = a second random commutant element. Two eigenspaces are copies of the SAME
     irrep iff they have equal dim and V_a^T R2 V_b != 0; this groups eigenspaces into
     irrep components by union-find.
  3. Within a component, the orthogonal part of V_t^T R2 V_ref (an intertwiner, a
     scalar multiple of an orthogonal matrix by Schur) aligns copy t to the reference,
     so that for EVERY invariant M, F_s^T M F_t = c_{st}(M) * I_{d_lambda}.
The reduced PSD is then: for each irrep, the multiplicity x multiplicity matrix
C_lambda = [c_{st}(M)] >= 0. M >= 0 IFF all C_lambda >= 0. (Validated: the
"F_s^T M F_t - c I" residual is ~1e-13; reduced block sizes rhombus 93->17, Moser
321->59.)

CORRECTNESS GATE. A wrong reduction silently FAKES a chi_m bound. So e3q is validated
against the independent naive e3n on small configs (rhombus, Moser, k=4,5, base and
+IEC): the margins must agree and e3q must never exceed e3n (no fake certificate).
Only after that gate passes is the X_23 run meaningful.
"""
from __future__ import annotations

import json
import time
from collections import defaultdict
from itertools import permutations

import cvxpy as cp
import numpy as np
from scipy.special import j0

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config,
    _triangle_vertices_exact, _rhombus_vertices_exact, _moser_vertices_exact,
)
from experiments.fractional.e3n_moment_order2 import (
    _canon, build_order2_relaxation, iec_keys_upto4,
)


def _orbit_rep(key, k):
    """S_k-orbit canonical form of a moment key (frozenset of (vertex,color)):
    relabel colors by order of first appearance (sorted by vertex). Two keys are
    S_k-equivalent iff they share this canonical form. 'one'/'zero' pass through."""
    if key in ("one", "zero"):
        return key
    items = sorted(key)  # by vertex
    remap = {}
    out = []
    for (v, c) in items:
        if c not in remap:
            remap[c] = len(remap)
        out.append((v, remap[c]))
    return frozenset(out)


def _congruence_rep(key, dist_id, k):
    """O(2)+S_k congruence-canonical form of a moment key. The O(2)-averaged moment
    of a colored sub-configuration depends only on its CONGRUENCE type (the IEC
    principle, note 12), so congruent colored vertex-subsets share a variable. The
    canonical form jointly minimizes, over all point permutations, the pair
    (distance-class submatrix, first-appearance color partition). 'one'/'zero' pass
    through. dist_id maps each unordered vertex pair to its distance-class integer."""
    if key in ("one", "zero"):
        return key
    items = sorted(key)
    verts = [v for (v, _) in items]
    cols = [c for (_, c) in items]
    m = len(verts)
    best = None
    for perm in permutations(range(m)):
        dpart = []
        for a in range(m):
            for b in range(a + 1, m):
                va, vb = verts[perm[a]], verts[perm[b]]
                dpart.append(dist_id[(min(va, vb), max(va, vb))])
        remap = {}
        cpart = []
        for a in range(m):
            c = cols[perm[a]]
            if c not in remap:
                remap[c] = len(remap)
            cpart.append(remap[c])
        cand = (tuple(dpart), tuple(cpart))
        if best is None or cand < best:
            best = cand
    return best


def _build_basis(n, k, edges):
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
    return basis


def _symmetry_adapted_blocks(basis, k, seed=1):
    """Murota-style symmetry-adapted basis for the S_k color action on `basis`.
    Returns a list of irrep blocks; each block is (F_list, d) where F_list is the
    list of aligned orthonormal D x d copy-bases and d is the irrep dimension."""
    D = len(basis)
    bindex = {b: a for a, b in enumerate(basis)}
    G = [np.array([bindex[frozenset((v, perm[c]) for (v, c) in b)] for b in basis])
         for perm in permutations(range(k))]

    def reynolds(Araw):
        R = np.zeros((D, D))
        for arr in G:
            R[np.ix_(arr, arr)] += Araw
        return (R + R.T) / (2 * len(G))

    rng = np.random.default_rng(seed)
    R = reynolds(_sym(rng.standard_normal((D, D))))
    R2 = reynolds(_sym(rng.standard_normal((D, D))))
    w, V = np.linalg.eigh(R)
    o = np.argsort(w)
    w, V = w[o], V[:, o]
    esp = []
    s = 0
    for i in range(1, D + 1):
        if i == D or abs(w[i] - w[s]) > 1e-6:
            esp.append((s, i))
            s = i
    Vs = [V[:, a:b] for (a, b) in esp]
    dims = [b - a for (a, b) in esp]
    spans = list(esp)

    # Precompute Z = V^T R2 V ONCE (two D x D matmuls). Every intertwiner block
    # V_a^T R2 V_b is then the slice Z[a-rows, b-cols] -- O(D^2) total instead of the
    # O(m^2 D^2) of forming each product separately (which does not scale past n~7).
    Z = V.T @ (R2 @ V)

    m = len(esp)
    parent = list(range(m))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a in range(m):
        ra0, ra1 = spans[a]
        for b in range(a + 1, m):
            if dims[a] != dims[b]:
                continue
            rb0, rb1 = spans[b]
            if np.linalg.norm(Z[ra0:ra1, rb0:rb1]) > 1e-6:
                parent[find(a)] = find(b)

    comps = defaultdict(list)
    for a in range(m):
        comps[find(a)].append(a)

    blocks = []
    for members in comps.values():
        d = dims[members[0]]
        ref = members[0]
        r0, r1 = spans[ref]
        F_list = [Vs[ref]]
        for t in members[1:]:
            t0, t1 = spans[t]
            O = Z[t0:t1, r0:r1]             # intertwiner ref -> t (slice of Z)
            U, _, Wt = np.linalg.svd(O)
            F_list.append(Vs[t] @ (U @ Wt))  # orthogonal aligner
        blocks.append((F_list, d))
    return blocks


def _sym(A):
    return A + A.T


def build_blockdiag_order2(X, dmat2_canon, edges, k, *, iec_keys=None,
                           congruence_reduce=False,
                           n_freq=300, freq_max=20.0, slack_tol=1e-6, solver=None):
    """S_k-reduced order-2 Phase-1 relaxation. Reproduces e3n margins (symmetrized,
    lossless) with the PSD split into small multiplicity blocks.

    congruence_reduce: if True, ALSO identify O(2)-congruent colored sub-configs as
    one moment variable (Part 2). This is structurally equivalent to imposing the
    Formulation-1/2 IEC up to subset size 4, so iec_keys is then ignored. It reduces
    the moment-VARIABLE count along the vertex axis (S_k only reduces the color axis /
    block sizes), but only as much as the configuration is geometrically degenerate."""
    n = X.shape[0]
    edges = set((min(a, b), max(a, b)) for (a, b) in edges)
    iec_keys = [] if congruence_reduce else list(iec_keys or [])
    basis = _build_basis(n, k, edges)
    D = len(basis)

    if congruence_reduce:
        vals = sorted({dmat2_canon[(i, j)] for i in range(n) for j in range(i + 1, n)},
                      key=lambda e: float(e))
        valpos = {v: idx for idx, v in enumerate(vals)}
        dist_id = {(i, j): valpos[dmat2_canon[(i, j)]]
                   for i in range(n) for j in range(i + 1, n)}
        keyfn = lambda kk: _congruence_rep(kk, dist_id, k)
    else:
        keyfn = lambda kk: _orbit_rep(kk, k)

    # Symmetrized moment variables: one per orbit (S_k) or congruence class (+O(2)) of
    # the non-trivial merged keys. Record incidence positions and the constant ('one').
    orbit_positions = defaultdict(list)
    one_positions = []
    for a in range(D):
        Ba = basis[a]
        for b in range(D):
            key = _canon(Ba | basis[b], edges)
            if key == "zero":
                continue
            if key == "one":
                one_positions.append((a, b))
                continue
            orbit_positions[keyfn(key)].append((a, b))

    orbits = list(orbit_positions)
    oindex = {o: idx for idx, o in enumerate(orbits)}
    y = cp.Variable(len(orbits), nonneg=True)

    def mom(assignset):
        key = _canon(assignset, edges)
        if key == "one":
            return cp.Constant(1.0)
        if key == "zero":
            return cp.Constant(0.0)
        idx = oindex.get(keyfn(key))
        return y[idx] if idx is not None else cp.Constant(0.0)

    # Symmetry-adapted blocks; precompute, per (block, orbit), the small matrix
    # C_orbit[s,t] = (1/d) tr(F_s^T E_orbit F_t), and the constant block.
    blocks = _symmetry_adapted_blocks(basis, k)
    cons = []
    # Precompute position arrays (a-index, b-index) per orbit and for the constant.
    one_a = np.array([a for (a, _) in one_positions], dtype=int)
    one_b = np.array([b for (_, b) in one_positions], dtype=int)
    orbit_ab = [(np.array([a for (a, _) in orbit_positions[o]], dtype=int),
                 np.array([b for (_, b) in orbit_positions[o]], dtype=int))
                for o in orbits]
    n_orb = len(orbits)
    # The affine map T (mult^2 x n_orb) per block is dense. S_k shrinks the BLOCKS
    # but not the moment-VARIABLE count (n_orb), which is vertex-combinatorial; on
    # X_23 order-2 n_orb ~ 98627 and the largest block ~735, so T alone is ~170 GiB
    # (L48). That variable explosion is what the O(2)-congruence reduction (Part 2)
    # collapses. Guard against the OOM so the limit is reported, not crashed into.
    max_mult = max(len(F) for F, _ in blocks)
    gib = max_mult * max_mult * n_orb * 8 / 2**30
    if gib > 8.0:
        return {"n_points": n, "k": k, "basis_size": D, "n_orbit_vars": n_orb,
                "n_blocks": len(blocks), "max_block": max_mult,
                "status": "SKIPPED_AFFINE_MAP_TOO_LARGE",
                "affine_map_gib": round(gib, 1),
                "note": "S_k reduces blocks but not the moment-variable count; "
                        "needs the O(2)-congruence reduction (Part 2) to collapse "
                        f"the {n_orb} moment variables before X_23-scale order-2 runs"}
    for F_list, d in blocks:
        mult = len(F_list)
        Fstack = np.stack(F_list, axis=0)        # (mult, D, d)

        def Cmat(a_idx, b_idx):
            if a_idx.size == 0:
                return np.zeros((mult, mult))
            A = Fstack[:, a_idx, :]              # (mult, P, d)
            B = Fstack[:, b_idx, :]
            return np.einsum('spl,tpl->st', A, B) / d

        # Build the block as a SINGLE affine map vec(C) = Cconst_vec + T @ y, rather
        # than summing n_orb weighted cp.Constant matrices (which made cvxpy's
        # canonicalization blow up at n>=7). T is (mult^2, n_orb).
        Cconst = Cmat(one_a, one_b)
        T = np.zeros((mult * mult, n_orb))
        for oi, (a_idx, b_idx) in enumerate(orbit_ab):
            Co = Cmat(a_idx, b_idx)
            if np.any(np.abs(Co) > 1e-12):
                T[:, oi] = Co.reshape(-1)
        vecC = cp.Constant(Cconst.reshape(-1)) + cp.Constant(T) @ y
        cons.append(cp.reshape(vecC, (mult, mult), order="C") >> 0)

    # (NORM) each point one color.
    for i in range(n):
        cons.append(cp.sum([mom({(i, c)}) for c in range(k)]) == 1)
    # (MARG) singleton <- pair.
    for i in range(n):
        for c in range(k):
            yi = mom({(i, c)})
            for j in range(n):
                if j == i:
                    continue
                cons.append(yi == cp.sum([mom({(i, c), (j, cc)}) for cc in range(k)]))
    # (BOCH) per-color Bochner + slack on non-edges. By symmetry one color suffices.
    nu = cp.Variable(n_freq, nonneg=True)
    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)
    for i in range(n):
        cons.append(mom({(i, 0)}) == cp.sum(nu))
    cons.append(J0_at_1 @ nu == 0)
    slacks = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in edges:
                continue
            dd = float(np.linalg.norm(X[i] - X[j]))
            Jvec = j0(2.0 * np.pi * dd * freqs)
            s = cp.Variable()
            slacks.append(s)
            cons.append(mom({(i, 0), (j, 0)}) - Jvec @ nu == s)

    # (IEC) Formulation 1+2 up to size 4 as moment equalities (on orbit vars).
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
                "basis_size": D, "n_orbit_vars": len(orbits)}
    elapsed = time.time() - t0

    raw = float(prob.value) if prob.value is not None else None
    margin = raw if (raw is not None and np.isfinite(raw)) else None
    infeasible = prob.status in ("infeasible", "infeasible_inaccurate")
    near_noise = bool(margin is not None and 0.0 < margin <= slack_tol)
    certifies = bool(infeasible or (margin is not None and margin > slack_tol))
    return {
        "n_points": n, "k": k, "basis_size": D, "n_orbit_vars": len(orbits),
        "n_blocks": len(blocks), "max_block": max(len(F) for F, _ in blocks),
        "n_iec_constraints": n_iec, "status": prob.status,
        "infeasibility_margin": margin, "near_noise": near_noise,
        "certifies_infeasible": certifies,
        "implies_chi_m_geq": (k + 1) if certifies else None,
        "solve_time_s": elapsed,
    }


TOL = 1e-6


def _agree(a, b):
    if a is None or b is None:
        return a is None and b is None
    if a <= TOL and b <= TOL:
        return True
    return abs(a - b) <= TOL


def validate():
    print("e3q: S_k-block-diagonalized ORDER-2 vs naive e3n (must reproduce margins)",
          flush=True)
    print("=" * 78, flush=True)
    # Rhombus is the decisive correctness gate: small enough that the naive e3n
    # reference is cheap, and the reduction is fully exercised (PSD 93 -> small blocks).
    # Triangle is added as a second independent check. (Moser/X_23 are scaling
    # follow-ons: the precompute needs the orbit einsum tiled before they are cheap.)
    configs = [("triangle", _triangle_vertices_exact),
               ("rhombus", _rhombus_vertices_exact)]
    out = {"experiment": "e3q_blockdiag_order2", "tol": TOL, "rows": []}
    all_ok = True
    for name, fn in configs:
        X, dc, edges = build_exact_config(fn())
        for k in (4, 5):
            keys = iec_keys_upto4(X, dc, edges, k, max_size=3)
            for label, iec in (("base", set()), ("+IEC", keys)):
                ref = build_order2_relaxation(X, dc, edges, k, iec_keys=iec,
                                              max_basis=5000)
                red = build_blockdiag_order2(X, dc, edges, k, iec_keys=iec)
                mr = ref.get("infeasibility_margin")
                md = red.get("infeasibility_margin")
                ok = _agree(mr, md) and ((md is None) or (mr is None) or md <= mr + TOL)
                all_ok = all_ok and ok
                print(f"  [{name} k={k}] {label:5s}: e3n={_f(mr)} e3q={_f(md)} "
                      f"|B|={ref.get('basis_size')}->blocks {red.get('n_blocks')} "
                      f"(max {red.get('max_block')})  e3n {ref.get('solve_time_s',0):.1f}s "
                      f"e3q {red.get('solve_time_s',0):.1f}s  {'OK' if ok else '!! MISMATCH'}",
                      flush=True)
                out["rows"].append({"config": name, "k": k, "variant": label,
                                    "e3n_margin": mr, "e3q_margin": md,
                                    "basis": ref.get("basis_size"),
                                    "max_block": red.get("max_block"), "ok": ok})
    out["all_reproduce"] = all_ok
    CACHE.mkdir(exist_ok=True)
    with (CACHE / "e3q_blockdiag_order2.json").open("w") as f:
        json.dump(out, f, indent=2)
    print("\n" + "=" * 78)
    print(f"BLOCK-DIAGONALIZED order-2 reproduces e3n on small configs: "
          f"{'PASS' if all_ok else 'FAIL'}")
    return all_ok


def _f(m):
    return "None" if m is None else f"{m:.2e}"


def validate_congruence():
    """Gate Part 2: e3q with congruence_reduce=True (O(2) variable identification)
    must reproduce e3n WITH the size-<=4 IEC, since identifying congruent variables
    is structurally the same as imposing the IEC equalities. Also reports the
    variable collapse (S_k orbits -> congruence classes)."""
    print("\ne3q Part 2: congruence reduction vs e3n+IEC (must match) + var collapse")
    print("=" * 78, flush=True)
    configs = [("triangle", _triangle_vertices_exact), ("rhombus", _rhombus_vertices_exact)]
    all_ok = True
    rows = []
    for name, fn in configs:
        X, dc, edges = build_exact_config(fn())
        for k in (4, 5):
            keys = iec_keys_upto4(X, dc, edges, k, max_size=4)
            ref = build_order2_relaxation(X, dc, edges, k, iec_keys=keys, max_basis=5000)
            sk = build_blockdiag_order2(X, dc, edges, k, congruence_reduce=False,
                                        iec_keys=set())
            cg = build_blockdiag_order2(X, dc, edges, k, congruence_reduce=True)
            mr, mc = ref.get("infeasibility_margin"), cg.get("infeasibility_margin")
            ok = _agree(mr, mc) and ((mc is None) or (mr is None) or mc <= mr + TOL)
            all_ok = all_ok and ok
            print(f"  [{name} k={k}] e3n+IEC={_f(mr)} e3q+cong={_f(mc)}  vars "
                  f"S_k={sk.get('n_orbit_vars')}->cong={cg.get('n_orbit_vars')}  "
                  f"{'OK' if ok else '!! MISMATCH'}", flush=True)
            rows.append({"config": name, "k": k, "e3n_iec_margin": mr,
                         "cong_margin": mc, "sk_vars": sk.get("n_orbit_vars"),
                         "cong_vars": cg.get("n_orbit_vars"), "ok": ok})
    print(f"\nCONGRUENCE reduction reproduces e3n+IEC: {'PASS' if all_ok else 'FAIL'}",
          flush=True)
    CACHE.mkdir(exist_ok=True)
    with (CACHE / "e3q_congruence_validation.json").open("w") as f:
        json.dump({"experiment": "e3q_congruence_validation", "rows": rows,
                   "all_reproduce": all_ok}, f, indent=2)
    return all_ok


def main():
    ok1 = validate()
    ok2 = validate_congruence()
    return 0 if (ok1 and ok2) else 1


if __name__ == "__main__":
    raise SystemExit(main())
