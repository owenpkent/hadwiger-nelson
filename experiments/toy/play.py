"""The toy demo: grade the reference and two bad candidates over the full battery.

Run: python -m experiments.toy.play
"""

from __future__ import annotations

from experiments.toy import (
    grade,
    sat_lower_bound,
    clique_lower_bound,
    max_degree_plus_one,
)


def main() -> int:
    print("HN toy sandbox: grading chi-lower-bound techniques against a known-chi battery\n")

    print("1) REFERENCE: exact chi by SAT (the known-correct toy technique)")
    ref = grade(sat_lower_bound, "sat_lower_bound (reference)")
    print(ref.report())
    print()

    print("2) BAD: max-clique omega (valid but too weak; omega<=3 in the UDG regime)")
    clq = grade(clique_lower_bound, "clique_lower_bound")
    print(clq.report())
    print()

    print("3) BAD: max-degree+1 (an upper bound abused as a lower bound; control-blind)")
    deg = grade(max_degree_plus_one, "max_degree_plus_one")
    print(deg.report())
    print()

    ok = ref.all_green and not clq.all_green and not deg.all_green
    print(f"demo verdict: reference green, both bad candidates caught -> {'PASS' if ok else 'FAIL'}")
    print("\ncaveat: a green scorecard means the technique is sound and control-clean on")
    print("FINITE graphs. It does NOT mean it lifts to R^2: the W3 realizability wall is")
    print("not in the toy. The delta between green-here and a planar UDG is the compass.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
