r"""Shot A, first increment: VALIDATE that S_k color-permutation symmetrization of
the multi-class measurable moment relaxation is LOSSLESS.

Why this is the right first step. L41 showed the order-2 moment SDP is correct but
does not scale: the PSD block (size 1 + nk + ...) is the cost, and X_23 (n=23) is out
of naive reach. The principled fix is to block-diagonalize the moment matrix by its
symmetry. The moment problem has a FREE symmetry that is always present and costs
nothing to exploit: the symmetric group S_k permuting the k color labels. The whole
Phase-1 (objective sum|slack|, normalization, marginalization, per-color Bochner,
IEC Formulation 1/2) is S_k-invariant, and the feasible set is convex, so averaging
any feasible point over S_k gives a symmetric feasible point with no worse objective.
Therefore the optimum lives on the S_k-invariant subspace: symmetrizing is LOSSLESS.

This script proves that computationally on the validated small configs by adding the
S_k orbit-equality constraints (e3m `symmetrize=True`) and checking the infeasibility
margin is UNCHANGED (to solver tolerance) versus the unsymmetrized backend, for LP
and PSD, base and +IEC. A match confirms the symmetrization is sound (it neither
loosens nor, crucially, FAKES a certificate by tightening). That soundness is the
foundation the block-diagonalized SDP (the actual scale win) is built on; the
block-diagonalization and the harder O(2)-congruence reduction are the follow-on.

NOTE: this flag only ADDS equalities; it does not yet shrink the PSD matrix, so it
buys no scale by itself. Its job is to de-risk the reduction program by validating
the lossless-symmetry claim against trusted results before the solver is rewritten.
"""
from __future__ import annotations

import json

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3l_multiclass_iec import (
    _triangle_vertices_exact, _rhombus_vertices_exact, _moser_vertices_exact,
)
from experiments.fractional.e3m_moment_backend import (
    build_exact_config, iec_keys_degree2, build_moment_relaxation,
)

TOL = 1e-6  # margins agree if both <= TOL (feasible) or |diff| <= TOL.

CONFIGS = [
    ("triangle", _triangle_vertices_exact),
    ("rhombus", _rhombus_vertices_exact),
    ("moser7", _moser_vertices_exact),
]


def _agree(a, b):
    if a is None or b is None:
        return a is None and b is None
    if a <= TOL and b <= TOL:
        return True
    return abs(a - b) <= TOL


def run(name, fn, k):
    X, dc, edges = build_exact_config(fn())
    _, _, f12 = iec_keys_degree2(X, dc, edges, k)
    rows = []
    ok = True
    for label, psd, keys in (("LP base", False, set()),
                             ("LP +IEC", False, f12),
                             ("PSD base", True, set()),
                             ("PSD +IEC", True, f12)):
        r0 = build_moment_relaxation(X, dc, edges, k, use_psd=psd, iec_keys=keys,
                                     symmetrize=False)
        r1 = build_moment_relaxation(X, dc, edges, k, use_psd=psd, iec_keys=keys,
                                     symmetrize=True)
        m0, m1 = r0.get("infeasibility_margin"), r1.get("infeasibility_margin")
        agree = _agree(m0, m1)
        # The symmetrized margin must NEVER exceed the unsymmetrized by more than
        # tolerance: a strictly larger symmetric margin would be a FAKE certificate.
        no_fake = (m1 is None) or (m0 is None) or (m1 <= m0 + TOL)
        ok = ok and agree and no_fake
        rows.append({"variant": label, "k": k, "margin_plain": m0,
                     "margin_symmetrized": m1, "agree": agree, "no_fake_cert": no_fake})
        ms0 = "None" if m0 is None else f"{m0:.2e}"
        ms1 = "None" if m1 is None else f"{m1:.2e}"
        flag = "OK " if (agree and no_fake) else "!! "
        print(f"  [{name} k={k}] {label:9s}: plain={ms0:>9s} sym={ms1:>9s} "
              f"{flag}({'lossless' if agree else 'MISMATCH'}"
              f"{'' if no_fake else ', FAKE-CERT RISK'})")
    return ok, rows


def main():
    print("Shot A: validate S_k color-symmetrization is LOSSLESS (foundation for the")
    print("        block-diagonalized order-2 SDP that breaks the X_23 scale wall).")
    print("=" * 78)
    all_ok = True
    out = {"experiment": "shotA_symmetry_validation", "tol": TOL, "configs": {}}
    for name, fn in CONFIGS:
        for k in (4, 5):
            ok, rows = run(name, fn, k)
            all_ok = all_ok and ok
            out["configs"][f"{name}_k{k}"] = {"lossless_and_sound": ok, "rows": rows}
    out["all_lossless_and_sound"] = all_ok
    CACHE.mkdir(exist_ok=True)
    path = CACHE / "shotA_symmetry_validation.json"
    with path.open("w") as f:
        json.dump(out, f, indent=2)
    print("\n" + "=" * 78)
    print(f"S_k SYMMETRIZATION LOSSLESS + SOUND on all small configs: "
          f"{'PASS' if all_ok else 'FAIL'}")
    print("Meaning: the optimum lives on the color-symmetric subspace, and the added")
    print("equalities neither loosen nor fake a certificate. This validates the")
    print("foundation for the block-diagonalized SDP (the actual scale win, follow-on).")
    print(f"archived: {path}")
    return all_ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
