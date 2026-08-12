r"""The both-free $\chi\ge6$ question, expressed as an ASSAY experiment.

This is the port that shows the platform is real rather than a shape. The
mathematics and the solver are unchanged (E20's $\Sigma_2$ decision procedure);
what changes is that the gates are no longer applied by whoever is driving, they
are structural conditions the runner enforces before it will spend any compute.

Reading this file next to `e20_sigma2.py` is the argument for the platform: the
same guards are present in both, but here forgetting one is impossible rather
than merely discouraged. `Experiment.validate()` refuses a ladder with no
expected-YES rung, refuses a missing non-vacuity probe, refuses a missing
independent verifier, and refuses an experiment with no scope statement.

Run:  python -m experiments.assay_bothfree --n 15
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "combinatorial"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path.home() / "dev" / "assay"))

from assay.core import Experiment, Verdict, run, YES, NO, UNKNOWN  # noqa: E402

from e20_sigma2 import (decide_cell, probe_cell, verify_model,      # noqa: E402
                        build_forbidden_clique_cnf, run_smsg, CACHE,
                        SAT, UNSAT)
from e18_gallai import ky_floor, codegree_ceiling                   # noqa: E402
from experiments._shared.wrong_approach_detectors import (          # noqa: E402
    rational_unit_distance_sample)
from experiments._shared.portfolio_sat import solve_color           # noqa: E402

# The solver's vocabulary is SAT/UNSAT; the platform's is YES/NO. YES means the
# object exists, so SAT maps to YES.
FROM_SOLVER = {SAT: YES, UNSAT: NO}


def build(n: int) -> Experiment:
    exp = Experiment(
        name=f"bothfree-chi6-n{n}",
        question=(f"Does the UDG-necessary class (K4-free, codegree <= 2) contain "
                  f"a member with chi >= 6 on {n} vertices?"),
        scope=("Bounds the CLASS, not chi(R^2). W3 (unit-distance realizability) "
               "is untouched, and an UNSAT here is not LRAT-certifiable (L80)."),
    )

    # Invariant 4. Woodall: the unit-distance graph on Q^2 is 2-chromatic. A method
    # that finds 3-chromatic structure there is using something that is not there,
    # and nothing it says about R^2 can be trusted.
    @exp.control(name="Q2_is_2_chromatic",
                 note="Woodall 1973; the wrong-approach detector")
    def q2_control():
        udg = rational_unit_distance_sample(num_points=60, denom_bound=10)
        vs = udg.vertices() if callable(udg.vertices) else udg.vertices
        es = udg.edges() if callable(udg.edges) else udg.edges
        verts = list(vs)
        e = [tuple(pair) for pair in es]      # already index pairs
        two = solve_color(len(verts), e, 2, symbreak=True)["result"]
        # YES = "the control behaves as the theorem says" (2-colorable).
        return YES if two else NO

    # Invariant 1, the NO direction, against an external uniqueness theorem.
    @exp.calibration(expect=NO, external=True, name="triangle_free_chi4_at_n10",
                     note="no triangle-free 4-chromatic graph on 10 vertices")
    def tf10():
        cnf = CACHE / "assay_tf_n10.cnf"
        build_forbidden_clique_cnf(10, 3, cnf)
        return FROM_SOLVER.get(run_smsg(10, cnf, 4)["result"], UNKNOWN)

    # Invariant 1/3, the YES direction. Without this rung a solver that always
    # answered UNSAT would sail through calibration and every nonexistence result
    # in this file would be unfounded.
    @exp.calibration(expect=YES, external=True, name="groetzsch_at_n11",
                     note="Chvatal: the Groetzsch graph is the unique such graph")
    def tf11():
        cnf = CACHE / "assay_tf_n11.cnf"
        build_forbidden_clique_cnf(11, 3, cnf)
        return FROM_SOLVER.get(run_smsg(11, cnf, 4)["result"], UNKNOWN)

    # The production value k=6, both directions. A k-critical graph has n = k or
    # n >= k+2, never k+1, so K6-free chi>=6 is impossible at n=7 and possible at
    # n=8 (C5 + K3).
    @exp.calibration(expect=NO, external=True, name="k6free_chi6_at_n7")
    def k6_7():
        cnf = CACHE / "assay_k6_n7.cnf"
        build_forbidden_clique_cnf(7, 6, cnf)
        return FROM_SOLVER.get(run_smsg(7, cnf, 6)["result"], UNKNOWN)

    @exp.calibration(expect=YES, external=True, name="k6free_chi6_at_n8")
    def k6_8():
        cnf = CACHE / "assay_k6_n8.cnf"
        build_forbidden_clique_cnf(8, 6, cnf)
        return FROM_SOLVER.get(run_smsg(8, cnf, 6)["result"], UNKNOWN)

    @exp.units
    def cells():
        return list(range(ky_floor(n), codegree_ceiling(n) + 1))

    @exp.work
    def decide(m):
        r = decide_cell(n, m, chi=6, quiet=True)
        return Verdict(FROM_SOLVER.get(r["result"], UNKNOWN), m,
                       seconds=r["elapsed_s"],
                       detail={"edges": m, "hit": r.get("hit")})

    @exp.probe
    def nonvacuous(m):
        return probe_cell(n, m)["nonempty"]

    @exp.verify
    def reverify(m, detail):
        hit = detail.get("hit") or {}
        edges = hit.get("edges")
        if not edges:
            return False
        v = verify_model(n, edges, 6, m=m)
        return bool(v["chi_ge"] and v["class_ok"])

    return exp


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=15)
    args = ap.parse_args()
    exp = build(args.n)
    CACHE.mkdir(parents=True, exist_ok=True)
    out = run(exp, ledger_path=CACHE / f"assay_n{args.n}.json")
    print()
    if out["halt"]:
        kind, msg = out["halt"]
        print(f"HALT [{kind}]: {msg}")
        return 2 if kind == "HIT" else 1
    print(f"{out['decided']}/{len(out['results'])} cells decided; "
          f"no chi>=6 member of the class on {args.n} vertices")
    print(f"scope: {exp.scope}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
