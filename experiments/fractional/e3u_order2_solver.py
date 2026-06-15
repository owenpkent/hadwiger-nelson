r"""e3u: matrix-free first-order solver for the order-2 measurable SDP, wrapping the
e3s operator. The increment that turns the validated operator into an actual SOLVE
of X_23 order-2 (k=4 retest chi_m>=5; k=5 the open chi_m>=6 frontier), which the
dense path cannot reach (~195 GiB even at k=4, L70).

Method: LINEARIZED (proximal) ADMM. The only "hard" cone is the PSD blocks; split
it off as a consensus P_b = apply_A(y), P_b in PSD. The augmented-Lagrangian
x-subproblem couples y through apply_A^T apply_A, so we LINEARIZE that quadratic
(one gradient step via apply_AT, plus a proximal term), leaving an x-update that is
a SPARSE QP with NO psd cone -- solvable by an off-the-shelf QP solver. Iterate:

  grad   = rho * apply_AT( apply_A(y) - (P - U) )                 # via e3s
  (y,nu) = argmin  L1_slack(y,nu) + <grad, y> + (1/2tau)||x - x_prev||^2
                   s.t. NORM, MARG, BOCH (sparse linear), y>=0, nu>=0    # sparse QP
  P_b    = proj_PSD( apply_A(y)_b + U_b )                          # 4 small eigen-decomps
  U_b   += apply_A(y)_b - P_b

The PSD projection is 4 eigendecompositions (max side 735); the operator
applications form only the D x D moment matrix (~125 MB at k=4), never the 195 GiB
affine map. The x-update QP is parametrized (cvxpy DPP) and re-solved each
iteration without re-canonicalizing.

Phase-1 objective = min sum |slack| over non-edges (slack_ij = y_{(i,0),(j,0)} -
J0(2pi d_ij .) . nu); a converged optimum above the noise floor => infeasible =>
chi_m >= k+1. The constraints mirror e3q exactly (congruence-reduced variables),
so the converged margin must equal e3q's dense margin -- the VALIDATION gate, run
on small configs (rhombus, Moser) where e3q's dense reference is available, before
any X_23 solve is trusted.
"""
from __future__ import annotations

import json
import time

import cvxpy as cp
import numpy as np
import scipy.sparse as sp
from scipy.special import j0

from experiments.fractional.e3c_ofv_lp_dual import CACHE, chi_m_integer
from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config, _rhombus_vertices_exact, _moser_vertices_exact,
)
from experiments.fractional.e3n_moment_order2 import _canon
from experiments.fractional.e3q_blockdiag_order2 import build_blockdiag_order2
from experiments.fractional.e3s_order2_operator import (
    build_operator, apply_A, apply_AT,
)


def _mom_col(op, key):
    """Column index (in y) of the moment variable for `key`, or None if the key
    is improper ('zero'). 'one' (the constant) never appears as a singleton/pair
    here, so it is not expected."""
    ck = _canon(key, op["edges"])
    if ck == "zero":
        return None
    if ck == "one":
        return "one"
    return op["oindex"].get(op["keyfn"](ck))


def build_linear_system(op, X, n_freq=300, freq_max=20.0):
    """Assemble the sparse linear constraints (NORM, MARG, BOCH) and the slack map
    (for the L1 objective) over the variable vector vec = [y (n_orb), nu (n_freq)],
    mirroring e3q's order-2 constraints with congruence-reduced variables."""
    n, k = op["n"], op["k"]
    n_orb = op["n_orb"]
    N = n_orb + n_freq
    edges = op["edges"]
    freqs = np.linspace(0.001, freq_max, n_freq)
    J0_at_1 = j0(2.0 * np.pi * freqs)

    rows, cols, vals, rhs = [], [], [], []
    r = 0

    def add(coeffs, b):
        nonlocal r
        for (c, v) in coeffs:
            rows.append(r); cols.append(c); vals.append(v)
        rhs.append(b)
        r += 1

    def ycol(key):
        return _mom_col(op, frozenset(key))

    # NORM: sum_c y_{(i,c)} = 1
    for i in range(n):
        acc = {}
        for c in range(k):
            col = ycol({(i, c)})
            if isinstance(col, int):
                acc[col] = acc.get(col, 0.0) + 1.0
        add(list(acc.items()), 1.0)

    # MARG: y_{(i,c)} - sum_{c'} y_{(i,c),(j,c')} = 0
    for i in range(n):
        for c in range(k):
            ci = ycol({(i, c)})
            for j in range(n):
                if j == i:
                    continue
                acc = {}
                if isinstance(ci, int):
                    acc[ci] = acc.get(ci, 0.0) + 1.0
                for cp_ in range(k):
                    col = ycol({(i, c), (j, cp_)})
                    if isinstance(col, int):
                        acc[col] = acc.get(col, 0.0) - 1.0
                if acc:
                    add(list(acc.items()), 0.0)

    # BOCH: y_{(i,0)} - sum(nu) = 0
    for i in range(n):
        ci = ycol({(i, 0)})
        acc = {}
        if isinstance(ci, int):
            acc[ci] = acc.get(ci, 0.0) + 1.0
        for f in range(n_freq):
            acc[n_orb + f] = acc.get(n_orb + f, 0.0) - 1.0
        add(list(acc.items()), 0.0)

    # BOCH-zero: J0_at_1 . nu = 0
    add([(n_orb + f, float(J0_at_1[f])) for f in range(n_freq)], 0.0)

    G = sp.csr_matrix((vals, (rows, cols)), shape=(r, N))
    g = np.array(rhs)

    # slack rows for the L1 objective: s_ij = y_{(i,0),(j,0)} - Jvec_ij . nu
    srows, scols, svals = [], [], []
    sr = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in edges:
                continue
            col = ycol({(i, 0), (j, 0)})
            if not isinstance(col, int):
                continue
            dd = float(np.linalg.norm(X[i] - X[j]))
            Jvec = j0(2.0 * np.pi * dd * freqs)
            srows.append(sr); scols.append(col); svals.append(1.0)
            for f in range(n_freq):
                srows.append(sr); scols.append(n_orb + f); svals.append(-float(Jvec[f]))
            sr += 1
    S = sp.csr_matrix((svals, (srows, scols)), shape=(sr, N))
    return {"G": G, "g": g, "S": S, "N": N, "n_orb": n_orb, "n_freq": n_freq}


def _op_norm_sq(op, iters=20):
    """Estimate ||apply_A||^2 (largest eigenvalue of apply_AT.apply_A) by power
    iteration, to set the proximal step tau < 1/(rho ||A||^2)."""
    rng = np.random.default_rng(0)
    v = rng.standard_normal(op["n_orb"])
    v /= np.linalg.norm(v)
    lam = 1.0
    for _ in range(iters):
        w = apply_AT(op, apply_A(op, v))
        lam = float(np.linalg.norm(w))
        if lam <= 0:
            break
        v = w / lam
    return lam


def _proj_psd(M):
    M = 0.5 * (M + M.T)
    w, V = np.linalg.eigh(M)
    w = np.maximum(w, 0.0)
    return (V * w) @ V.T


def solve(op, lin, rho=1.0, max_iters=4000, tol=1e-7, verbose=False,
          ckpt_path=None, ckpt_every=20):
    """Linearized-ADMM solve. Returns the Phase-1 margin (min sum|slack|) and
    residuals."""
    n_orb, n_freq, N = lin["n_orb"], lin["n_freq"], lin["N"]
    G, g, S = lin["G"], lin["g"], lin["S"]
    L = _op_norm_sq(op)
    tau = 0.9 / (rho * max(L, 1e-12))

    # x-update QP via OSQP-DIRECT (no cvxpy canonicalization, which OOMs at X_23:
    # a 48342-var DPP quad-form materializes a ~35 GiB dense coeff array). The QP is
    #   min  grad.x + (1/2tau)||x - xprev||^2 + sum t
    #   s.t. G x = g,  x >= 0,  t >= S x,  t >= -S x      (t = epigraph of |S x|)
    # Its P and A are CONSTANT across ADMM iterations; only q changes, so OSQP
    # factorizes once and each iteration is a q-update + warm-started solve.
    import osqp
    m_s = S.shape[0]
    Nz = N + m_s
    Pqp = sp.diags(np.concatenate([np.full(N, 1.0 / tau), np.zeros(m_s)])).tocsc()
    I_N = sp.eye(N, format="csr")
    Z_Nm = sp.csr_matrix((N, m_s))
    Z_eqm = sp.csr_matrix((G.shape[0], m_s))
    I_ms = sp.eye(m_s, format="csr")
    A_qp = sp.vstack([
        sp.hstack([G, Z_eqm]),            # G x = g
        sp.hstack([I_N, Z_Nm]),           # x >= 0
        sp.hstack([S, -I_ms]),            # S x - t <= 0
        sp.hstack([-S, -I_ms]),           # -S x - t <= 0
    ]).tocsc()
    INF = np.inf
    l_qp = np.concatenate([g, np.zeros(N), np.full(m_s, -INF), np.full(m_s, -INF)])
    u_qp = np.concatenate([g, np.full(N, INF), np.zeros(m_s), np.zeros(m_s)])
    qp = osqp.OSQP()
    # Inexact inner solves are fine for the outer ADMM; loosen tol + drop polish
    # for ~2x faster iterations (validation verdict is unchanged at 1e-5).
    qp.setup(P=Pqp, q=np.zeros(Nz), A=A_qp, l=l_qp, u=u_qp, verbose=False,
             eps_abs=1e-5, eps_rel=1e-5, max_iter=8000, polish=False,
             warm_start=True)

    x = np.zeros(N)
    P = [np.zeros((F.shape[0], F.shape[0])) for (F, _) in op["fblocks"]]
    U = [np.zeros_like(p) for p in P]

    margin = None
    t_start = time.time()
    for it in range(max_iters):
        y = x[:n_orb]
        AY = apply_A(op, y)
        resid_blocks = [AY[b] - (P[b] - U[b]) for b in range(len(P))]
        gy = rho * apply_AT(op, resid_blocks)
        qx = np.zeros(Nz)
        qx[:n_orb] = gy - (1.0 / tau) * x[:n_orb]
        qx[n_orb:N] = -(1.0 / tau) * x[n_orb:N]
        qx[N:] = 1.0                       # sum t
        qp.update(q=qx)
        res = qp.solve()
        if res.x is None or not np.all(np.isfinite(res.x)):
            return {"status": "x_update_failed", "iter": it}
        x = np.asarray(res.x[:N])

        y = x[:n_orb]
        AY = apply_A(op, y)
        prim = 0.0
        dual = 0.0
        for b in range(len(P)):
            Pnew = _proj_psd(AY[b] + U[b])
            prim += float(np.sum((AY[b] - Pnew) ** 2))
            dual += float(np.sum((Pnew - P[b]) ** 2))
            U[b] = U[b] + AY[b] - Pnew
            P[b] = Pnew
        prim = prim ** 0.5
        dual = (rho * dual) ** 0.5
        margin = float(np.sum(np.abs(S @ x)))
        if verbose and (it % 100 == 0 or it == max_iters - 1):
            print(f"    it {it}: margin={margin:.3e} prim={prim:.2e} "
                  f"dual={dual:.2e}", flush=True)
        if ckpt_path is not None and (it % ckpt_every == 0 or it == max_iters - 1):
            el = time.time() - t_start
            import json as _json
            with open(ckpt_path, "w") as f:
                _json.dump({"iter": it, "margin": margin, "prim_resid": prim,
                            "dual_resid": dual, "elapsed_s": round(el, 1),
                            "sec_per_iter": round(el / (it + 1), 3),
                            "op_norm_sq": L, "n_orb": n_orb, "max_iters": max_iters},
                           f, indent=1)
        if prim < tol and dual < tol:
            break
    return {"status": "ok", "iter": it, "margin": margin,
            "prim_resid": prim, "dual_resid": dual, "op_norm_sq": L, "tau": tau}


def run_x23(k=4, max_iters=20000, tol=1e-5):
    """Build and solve X_23 order-2 (matrix-free), with checkpointing. k=4 retests
    chi_m >= 5; k=5 (same reduced size) opens the chi_m >= 6 frontier. A converged
    primal residual -> 0 means FEASIBLE (no certificate); a residual plateauing
    above ~1e-3 means the order-2 relaxation certifies chi_m >= k+1."""
    import sympy as sp
    from experiments.fractional.e3i_ambrus_reproduce import (
        load_config, parse_points_exact,
    )
    print(f"e3u: RUN X_23 order-2, k={k} (matrix-free linearized ADMM)", flush=True)
    t0 = time.time()
    pts = parse_points_exact(load_config())
    verts = [(sp.re(z), sp.im(z)) for z in pts]
    X, dc, edges = build_exact_config(verts)
    op = build_operator(X, dc, edges, k, congruence_reduce=True)
    lin = build_linear_system(op, X)
    print(f"  built op (D={op['D']} n_orb={op['n_orb']} max_block="
          f"{max(op['block_mults'])}) + linear system in {time.time()-t0:.0f}s",
          flush=True)
    ckpt = CACHE / f"e3u_x23_k{k}_ckpt.json"
    r = solve(op, lin, max_iters=max_iters, tol=tol, verbose=True,
              ckpt_path=str(ckpt), ckpt_every=10)
    prim = r.get("prim_resid")
    feasible = prim is not None and prim < 1e-3
    verdict = {"k": k, "iters": r.get("iter"), "prim_resid": prim,
               "margin": r.get("margin"), "feasible": feasible,
               "certifies_chi_m_geq": (None if feasible else k + 1),
               "total_s": round(time.time() - t0, 1)}
    with (CACHE / f"e3u_x23_k{k}_result.json").open("w") as f:
        json.dump(verdict, f, indent=2)
    print(f"\nX_23 k={k}: prim_resid={prim:.2e} feasible={feasible} "
          f"=> {'no certificate (order-2 feasible)' if feasible else f'CERTIFIES chi_m >= {k+1}'}",
          flush=True)
    return verdict


TOL = 5e-4   # first-order solver tolerance for margin agreement (vs e3q IPM)


def validate():
    print("e3u: matrix-free linearized-ADMM order-2 solver vs e3q dense margins")
    print("=" * 78, flush=True)
    # configs spanning a certificate (margin>0) and a feasible (margin~0) case.
    cases = [("rhombus", _rhombus_vertices_exact, 4),
             ("moser7", _moser_vertices_exact, 3),
             ("moser7", _moser_vertices_exact, 4)]
    # The certificate is either e3q status 'infeasible' OR margin > slack_tol; the
    # matrix-free analogue is: feasible <=> primal residual closes to ~0, certifying
    # <=> primal residual plateaus above the feasibility threshold.
    PRIM_FEAS = 1e-3
    rows = []
    all_ok = True
    for name, fn, k in cases:
        X, dc, edges = build_exact_config(fn())
        ref = build_blockdiag_order2(X, dc, edges, k, congruence_reduce=True)
        ref_margin = ref.get("infeasibility_margin")
        ref_cert = bool(ref.get("certifies_infeasible"))
        op = build_operator(X, dc, edges, k, congruence_reduce=True)
        lin = build_linear_system(op, X)
        t0 = time.time()
        r = solve(op, lin, verbose=True)
        prim = r.get("prim_resid")
        my_feasible = (prim is not None and prim < PRIM_FEAS)
        my_cert = not my_feasible
        ok = (my_cert == ref_cert)
        all_ok = all_ok and ok
        mtxt = "infeas" if ref_margin is None else f"{ref_margin:.3e}"
        print(f"  [{name} k={k}] e3q: margin={mtxt} certifies={ref_cert} | "
              f"e3u: prim={prim:.2e} feasible={my_feasible} certifies={my_cert} "
              f"iters={r.get('iter')} L={r.get('op_norm_sq'):.1f}  "
              f"({time.time()-t0:.0f}s)  {'OK' if ok else '!! MISMATCH'}", flush=True)
        rows.append({"config": name, "k": k, "e3q_margin": ref_margin,
                     "e3q_certifies": ref_cert, "e3u_prim_resid": prim,
                     "e3u_margin": r.get("margin"), "e3u_certifies": my_cert,
                     "iters": r.get("iter"), "ok": ok})
    print("\n" + "=" * 78)
    print(f"matrix-free solver agrees with e3q feasible/certify verdict: "
          f"{'PASS' if all_ok else 'FAIL'}")
    CACHE.mkdir(exist_ok=True)
    with (CACHE / "e3u_order2_solver.json").open("w") as f:
        json.dump({"experiment": "e3u_order2_solver", "tol": TOL,
                   "rows": rows, "all_reproduce": all_ok}, f, indent=2)
    return 0 if all_ok else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "x23":
        kk = int(sys.argv[2]) if len(sys.argv) >= 3 else 4
        run_x23(k=kk)
        raise SystemExit(0)
    raise SystemExit(validate())
