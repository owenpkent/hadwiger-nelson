r"""e3t: actually RUN order-2 on X_23 (the chi_m >= 6 frontier attempt).

Two-pronged, lowest-risk first:
  (1) MEASURE the real X_23 order-2 sizes (D, n_orb after O(2)-congruence, block
      multiplicities) for k=4 (validation: order-2 should retest chi_m >= 5) and,
      if feasible, k=5 (the open chi_m >= 6 frontier). e3r/L50 quoted ~48342 vars /
      block 735 for k=5; the k=4 numbers are unmeasured and smaller.
  (2) If the dense per-block affine map for k=4 fits in memory, solve it DIRECTLY
      (e3q's build_blockdiag_order2 with congruence_reduce=True) and report the
      Phase-1 margin -> a fully end-to-end order-2 confirmation of chi_m >= 5 at
      X_23 scale, validating the whole pipeline. If it does NOT fit, that is the
      signal the matrix-free solver (wrapping e3s) is required even for k=4.

No bound is claimed unless a solve returns a margin above the noise floor.
"""
from __future__ import annotations

import json
import time

import sympy as sp

from experiments.fractional.e3c_ofv_lp_dual import CACHE, chi_m_integer
from experiments.fractional.e3l_multiclass_iec import build_exact_config
from experiments.fractional.e3q_blockdiag_order2 import build_blockdiag_order2
from experiments.fractional.e3s_order2_operator import build_operator
from experiments.fractional.e3i_ambrus_reproduce import (
    load_config, parse_points_exact,
)


def x23_exact_config():
    """X_23 as (X float, dmat2_canon, edges) in the e3l format."""
    pts = parse_points_exact(load_config())
    verts = [(sp.re(z), sp.im(z)) for z in pts]
    return build_exact_config(verts)


def main():
    print("e3t: RUN order-2 on X_23 (measure sizes; solve k=4 directly if it fits)")
    print("=" * 78, flush=True)

    t0 = time.time()
    print("building exact X_23 config (sympy distances) ...", flush=True)
    X, dc, edges = x23_exact_config()
    print(f"  n={X.shape[0]} unit-edges={len(edges)}  ({time.time()-t0:.0f}s)",
          flush=True)

    out = {"experiment": "e3t_x23_order2_run", "sizes": {}, "solves": {}}
    for k in (4, 5):
        t1 = time.time()
        print(f"\n[k={k}] measuring order-2 sizes (congruence-reduced) ...",
              flush=True)
        try:
            op = build_operator(X, dc, edges, k, congruence_reduce=True)
        except MemoryError as e:
            print(f"  build_operator MemoryError: {e}", flush=True)
            out["sizes"][k] = {"error": "MemoryError"}
            continue
        mults = op["block_mults"]
        max_mult = max(mults)
        D, n_orb = op["D"], op["n_orb"]
        # e3q's dense-affine-map guard metric, and the full all-blocks total.
        guard_gib = max_mult ** 2 * n_orb * 8 / 2**30
        total_gib = sum(m * m for m in mults) * n_orb * 8 / 2**30
        print(f"  D={D}  n_orb(cong)={n_orb}  n_blocks={len(mults)}  "
              f"max_block={max_mult}  (build {time.time()-t1:.0f}s)", flush=True)
        print(f"  dense affine map: largest block {guard_gib:.1f} GiB, "
              f"all blocks {total_gib:.1f} GiB", flush=True)
        out["sizes"][k] = {"D": D, "n_orb": n_orb, "n_blocks": len(mults),
                           "max_block": max_mult, "guard_gib": guard_gib,
                           "total_gib": total_gib}

        # Direct dense solve only if the largest-block map is small (e3q guard < 8).
        if guard_gib < 8.0:
            print(f"  -> fits the dense path; solving k={k} directly (CLARABEL) ...",
                  flush=True)
            t2 = time.time()
            r = build_blockdiag_order2(X, dc, edges, k, congruence_reduce=True)
            margin = r.get("infeasibility_margin")
            print(f"     status={r.get('status')}  margin={margin}  "
                  f"certifies_infeasible={r.get('certifies_infeasible')}  "
                  f"=> chi_m >= {r.get('implies_chi_m_geq')}  "
                  f"({time.time()-t2:.0f}s)", flush=True)
            out["solves"][k] = {"status": r.get("status"), "margin": margin,
                                "certifies": r.get("certifies_infeasible"),
                                "implies_chi_m_geq": r.get("implies_chi_m_geq"),
                                "solve_time_s": round(time.time() - t2, 1)}
        else:
            print(f"  -> dense path too large ({guard_gib:.0f} GiB > 8); "
                  f"k={k} requires the matrix-free solver (wrap e3s).", flush=True)
            out["solves"][k] = {"status": "NEEDS_MATRIX_FREE",
                                "guard_gib": guard_gib}

    CACHE.mkdir(exist_ok=True)
    with (CACHE / "e3t_x23_order2_run.json").open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\narchived: {CACHE / 'e3t_x23_order2_run.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
