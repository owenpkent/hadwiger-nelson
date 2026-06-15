r"""e3s: MATRIX-FREE operator for the S_k-block-diagonalized order-2 measurable SDP.

The correctness-critical first increment of the L70 backend. e3q assembles, per
symmetry block, a DENSE affine map T of shape (mult^2, n_orb) -- ~195 GiB on X_23,
the wall. This module computes the SAME linear map MATRIX-FREE: it never forms T.

The map. Let basis B (|B|=D) index the order-2 moment matrix; M(y) is the D x D
matrix whose (a,b) entry is the moment variable on the merged key of (B_a, B_b):
1 at the constant ('one') positions, y_o at the positions of orbit o, 0 (improper)
elsewhere. For a symmetry block with copy bases F_1..F_mult (each D x d, stacked as
Fstack (mult, D, d)), the reduced PSD block is

    C_block(y) = (1/d) sum_{l=1..d} P_l M(y) P_l^T ,   P_l := Fstack[:, :, l]  (mult x D).

FORWARD  A : y -> {C_block(y)}_blocks. Form M(y) (D x D, ~308 MB at X_23) from the
  orbit incidence, then project each block with d small matmuls. No (mult^2, n_orb)
  array is ever allocated; peak memory is the D x D moment matrix plus the basis
  (the F's total D^2 floats), i.e. O(D^2) ~ hundreds of MB, not O(mult^2 * n_orb)
  ~ hundreds of GiB.

ADJOINT  A^T : {Z_block} -> grad_y, where (A^T Z)_o = sum_block <C_block-coeff_o, Z>.
  By the projection identity <P_l M P_l^T, Z> = <M, P_l^T Z P_l>, assemble
  W = sum_block (1/d) sum_l P_l^T Z_block P_l   (one D x D matrix), then reduce over
  the orbit incidence:  (A^T Z)_o = sum_{(a,b) in orbit_o} W[a,b].

VALIDATION (this file). A matrix-free operator that silently disagrees with the
dense map would fake any downstream certificate, so the gate is strict, on the
small configs where e3q's dense T fits:
  (1) FORWARD matches dense: apply_A(y) == Cconst + (T @ y) per block, random y.
  (2) ADJOINT identity: <apply_A(y) - apply_A(0), Z> == <y, apply_AT(Z)>, random y, Z.
  (3) storage: report the matrix-free O(D^2) footprint vs the dense (mult^2 * n_orb)
      map, and the X_23 projection (~308 MB vs ~195 GiB).
The operator reuses e3q's basis, symmetry-adapted blocks, and orbit canonicalization
verbatim, so a pass here certifies the operator computes exactly e3q's order-2 map.
"""
from __future__ import annotations

import json
import time
from collections import defaultdict

import numpy as np

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config,
    _triangle_vertices_exact, _rhombus_vertices_exact, _moser_vertices_exact,
)
from experiments.fractional.e3n_moment_order2 import _canon
from experiments.fractional.e3q_blockdiag_order2 import (
    _build_basis, _symmetry_adapted_blocks, _orbit_rep, _congruence_rep,
)


def build_operator(X, dc, edges, k, congruence_reduce=False):
    """Shared setup for the matrix-free order-2 operator (identical bookkeeping to
    e3q.build_blockdiag_order2 up to, but not including, the dense T assembly)."""
    n = X.shape[0]
    edges = set((min(a, b), max(a, b)) for (a, b) in edges)
    basis = _build_basis(n, k, edges)
    D = len(basis)

    if congruence_reduce:
        vals = sorted({dc[(i, j)] for i in range(n) for j in range(i + 1, n)},
                      key=lambda e: float(e))
        valpos = {v: idx for idx, v in enumerate(vals)}
        dist_id = {(i, j): valpos[dc[(i, j)]]
                   for i in range(n) for j in range(i + 1, n)}
        keyfn = lambda kk: _congruence_rep(kk, dist_id, k)
    else:
        keyfn = lambda kk: _orbit_rep(kk, k)

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
    one_a = np.array([a for (a, _) in one_positions], dtype=int)
    one_b = np.array([b for (_, b) in one_positions], dtype=int)
    orbit_ab = [(np.array([a for (a, _) in orbit_positions[o]], dtype=int),
                 np.array([b for (_, b) in orbit_positions[o]], dtype=int))
                for o in orbits]

    blocks = _symmetry_adapted_blocks(basis, k)   # list of (F_list, d)
    fblocks = [(np.stack(F_list, axis=0), d) for (F_list, d) in blocks]  # (mult,D,d)

    return {
        "n": n, "k": k, "D": D, "n_orb": len(orbits),
        "one_a": one_a, "one_b": one_b, "orbit_ab": orbit_ab,
        "fblocks": fblocks,
        "block_mults": [F.shape[0] for (F, _) in fblocks],
    }


def _moment_matrix(op, y):
    """M(y): D x D, 1 at constant positions, y_o at orbit-o positions."""
    D = op["D"]
    M = np.zeros((D, D))
    if op["one_a"].size:
        M[op["one_a"], op["one_b"]] = 1.0
    for o, (a_idx, b_idx) in enumerate(op["orbit_ab"]):
        if a_idx.size:
            M[a_idx, b_idx] = y[o]
    return M


def apply_A(op, y):
    """Forward map: y -> list of reduced PSD block matrices C_block(y) (mult x mult).
    Matrix-free: forms M(y) (D x D) and projects; never allocates (mult^2, n_orb)."""
    M = _moment_matrix(op, y)
    out = []
    for (Fstack, d) in op["fblocks"]:
        mult = Fstack.shape[0]
        C = np.zeros((mult, mult))
        for l in range(d):
            Pl = Fstack[:, :, l]          # (mult, D)
            C += Pl @ (M @ Pl.T)          # (mult, mult)
        out.append(C / d)
    return out


def apply_AT(op, Zlist):
    """Adjoint map: list of dual block matrices Z_block -> grad over the n_orb
    moment variables. Matrix-free: forms one D x D intermediate W and reduces over
    the orbit incidence."""
    D = op["D"]
    W = np.zeros((D, D))
    for (Fstack, d), Z in zip(op["fblocks"], Zlist):
        for l in range(d):
            Pl = Fstack[:, :, l]          # (mult, D)
            W += (Pl.T @ (Z @ Pl)) / d    # (D, D)
    g = np.empty(op["n_orb"])
    for o, (a_idx, b_idx) in enumerate(op["orbit_ab"]):
        g[o] = float(W[a_idx, b_idx].sum()) if a_idx.size else 0.0
    return g


def _dense_reference(op):
    """Build e3q's dense per-block (Cconst, T) ONLY for validation on small configs
    (T is mult^2 x n_orb). Returns list of (Cconst (mult,mult), T (mult^2,n_orb))."""
    ref = []
    n_orb = op["n_orb"]
    for (Fstack, d) in op["fblocks"]:
        mult = Fstack.shape[0]

        def Cmat(a_idx, b_idx):
            if a_idx.size == 0:
                return np.zeros((mult, mult))
            A = Fstack[:, a_idx, :]
            B = Fstack[:, b_idx, :]
            return np.einsum('spl,tpl->st', A, B) / d

        Cconst = Cmat(op["one_a"], op["one_b"])
        T = np.zeros((mult * mult, n_orb))
        for oi, (a_idx, b_idx) in enumerate(op["orbit_ab"]):
            Co = Cmat(a_idx, b_idx)
            T[:, oi] = Co.reshape(-1)
        ref.append((Cconst, T))
    return ref


def validate():
    print("e3s: matrix-free order-2 operator vs e3q dense map (must reproduce)")
    print("=" * 78, flush=True)
    rng = np.random.default_rng(0)
    configs = [("triangle", _triangle_vertices_exact, 4),
               ("rhombus", _rhombus_vertices_exact, 4),
               ("moser7", _moser_vertices_exact, 5)]
    rows = []
    all_ok = True
    for name, fn, k in configs:
        X, dc, edges = build_exact_config(fn())
        for cong in (False, True):
            op = build_operator(X, dc, edges, k, congruence_reduce=cong)
            ref = _dense_reference(op)
            n_orb = op["n_orb"]
            y = rng.standard_normal(n_orb)

            # (1) forward matches dense
            fwd = apply_A(op, y)
            fwd_err = 0.0
            for (Cb, (Cconst, T)) in zip(fwd, ref):
                mult = Cb.shape[0]
                dense = Cconst + (T @ y).reshape(mult, mult)
                fwd_err = max(fwd_err, float(np.max(np.abs(Cb - dense))))

            # (2) adjoint identity: <A y - A 0, Z> == <y, A^T Z>
            Z = [rng.standard_normal((F.shape[0], F.shape[0])) for (F, _) in op["fblocks"]]
            Z = [0.5 * (z + z.T) for z in Z]            # symmetric duals
            A0 = apply_A(op, np.zeros(n_orb))
            lhs = sum(float(np.sum((cb - c0) * z))
                      for cb, c0, z in zip(fwd, A0, Z))
            g = apply_AT(op, Z)
            rhs = float(np.dot(y, g))
            adj_err = abs(lhs - rhs)

            # (3) storage footprint
            dense_T_entries = sum(m * m for m in op["block_mults"]) * n_orb
            mf_entries = op["D"] ** 2 + sum(F.size for (F, _) in op["fblocks"])
            ok = fwd_err < 1e-9 and adj_err < 1e-7
            all_ok = all_ok and ok
            tag = "cong" if cong else "S_k "
            print(f"  [{name} k={k} {tag}] D={op['D']:4d} n_orb={n_orb:5d} "
                  f"max_block={max(op['block_mults']):3d} | fwd_err={fwd_err:.1e} "
                  f"adj_err={adj_err:.1e} | denseT={dense_T_entries*8/2**20:.1f}MB "
                  f"mf={mf_entries*8/2**20:.1f}MB  {'OK' if ok else '!! FAIL'}",
                  flush=True)
            rows.append({"config": name, "k": k, "congruence": cong,
                         "D": op["D"], "n_orb": n_orb,
                         "max_block": max(op["block_mults"]),
                         "fwd_err": fwd_err, "adj_err": adj_err,
                         "dense_T_MB": dense_T_entries * 8 / 2**20,
                         "matrix_free_MB": mf_entries * 8 / 2**20, "ok": ok})

    # X_23 projection (known scale: D~6206, n_orb~48342 cong, max_block~735).
    D23, NORB23, MB23 = 6206, 48342, 735
    dense23 = MB23 ** 2 * NORB23 * 8 / 2**30
    mf23 = D23 ** 2 * 8 / 2**30
    print("\n" + "=" * 78)
    print(f"X_23 projection: dense largest-block map ~{dense23:.0f} GiB  vs  "
          f"matrix-free moment matrix ~{mf23*1024:.0f} MB (+ basis ~{mf23*1024:.0f} MB).")
    print(f"matrix-free operator reproduces e3q dense map: {'PASS' if all_ok else 'FAIL'}")

    CACHE.mkdir(exist_ok=True)
    with (CACHE / "e3s_order2_operator.json").open("w") as f:
        json.dump({"experiment": "e3s_order2_operator", "rows": rows,
                   "all_reproduce": all_ok,
                   "x23_dense_largest_block_GiB": dense23,
                   "x23_matrix_free_MB": mf23 * 1024}, f, indent=2)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(validate())
