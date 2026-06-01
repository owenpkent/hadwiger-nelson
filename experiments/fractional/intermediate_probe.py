r"""Intermediate-config probe (L50): does the order-2 measurable SDP ever STRICTLY
beat order-1 on a config small enough to run, before committing to the X_23-scale
sparse solver?

Motivation. L49 showed the two symmetry reductions (S_k blocks, O(2) variables),
though both built and correct, are together insufficient to fit X_23 order-2 into a
dense-assembly solver; the remaining step is a custom sparse conic backend (weeks of
work). Before paying for that, check whether the order-2 lift's extra strength
(larger PSD coupling + IEC up to subset size 4 vs size 2) is observable on ANY
runnable configuration. If order-2 ever certifies an obstruction order-1 misses, that
motivates the solver; if it never does at runnable scale, the X_23 sparse solver is
the only way to find out (no shortcut).

Result (L50): no strict separation. On Moser (n=7) at k=2..5 and double-Moser (n=10)
at k=2, e3p (order-1) and e3q (order-2 + congruence) AGREE everywhere: both certify
the graph-non-k-colorable cases (k < chi), both feasible otherwise. The order-2
advantage only manifests at X_23 scale (the measurable obstruction the single-class
route needed 23 points + IEC size 5 to see). double-Moser k>=3 order-2 exceeds memory
at n=10 (naive-assembly scaling wall).
"""
from __future__ import annotations

import json

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config, _moser_vertices_exact,
)
from experiments.fractional.e3m_moment_backend import _double_moser_vertices_exact
from experiments.fractional.e3p_blockdiag_order1 import build_blockdiag_order1
from experiments.fractional.e3q_blockdiag_order2 import build_blockdiag_order2


def _fmt(m):
    return "None" if m is None else f"{m:.2e}"


def main():
    print("Intermediate probe: order-2 vs order-1 separation on runnable configs")
    print("=" * 78, flush=True)
    configs = [("moser7", _moser_vertices_exact, (2, 3, 4, 5)),
               ("double_moser10", _double_moser_vertices_exact, (2, 3, 4, 5))]
    rows = []
    any_sep = False
    for name, fn, ks in configs:
        X, dc, e = build_exact_config(fn())
        n = X.shape[0]
        for k in ks:
            try:
                r1 = build_blockdiag_order1(X, dc, e, k, use_psd=True,
                                            congruence_iec=True)
                r2 = build_blockdiag_order2(X, dc, e, k, congruence_reduce=True)
            except MemoryError as exc:  # naive-assembly wall (informative)
                print(f"  [{name} n={n} k={k}] order-2 MemoryError: {exc}", flush=True)
                rows.append({"config": name, "n": n, "k": k, "error": "MemoryError"})
                continue
            m1, c1 = r1.get("infeasibility_margin"), r1.get("certifies_infeasible")
            m2, c2 = r2.get("infeasibility_margin"), r2.get("certifies_infeasible")
            if r2.get("status", "").startswith("SKIPPED"):
                print(f"  [{name} n={n} k={k}] order-2 {r2['status']} "
                      f"(affine map {r2.get('affine_map_gib')} GiB)", flush=True)
                rows.append({"config": name, "n": n, "k": k,
                             "o2_status": r2.get("status")})
                continue
            sep = bool(c2 and not c1)
            any_sep = any_sep or sep
            print(f"  [{name} n={n} k={k}] order1: margin={_fmt(m1)} cert={c1} | "
                  f"order2: margin={_fmt(m2)} cert={c2} vars={r2.get('n_orbit_vars')}"
                  f"{'  <<< ORDER-2 STRICTLY STRONGER' if sep else ''}", flush=True)
            rows.append({"config": name, "n": n, "k": k, "o1_margin": m1,
                         "o1_cert": c1, "o2_margin": m2, "o2_cert": c2, "sep": sep})
    print(f"\nANY strict order-2 > order-1 separation: {any_sep}", flush=True)
    print("(No separation => the order-2 advantage only shows at X_23 scale; the "
          "sparse solver is the only way to test it.)")
    CACHE.mkdir(exist_ok=True)
    with (CACHE / "intermediate_probe.json").open("w") as f:
        json.dump({"experiment": "intermediate_probe", "rows": rows,
                   "any_separation": any_sep}, f, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
