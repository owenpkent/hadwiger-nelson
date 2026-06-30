"""Smoke test for the toy sandbox.

Verifies (a) the battery's answer key matches SAT, (b) the reference candidate
scores all green, (c) each demonstration bad candidate is caught.

Run: python -m experiments.toy.test_toy
"""

from __future__ import annotations

from experiments.toy import (
    FULL_BATTERY,
    chi_via_sat,
    grade,
    sat_lower_bound,
    clique_lower_bound,
    max_degree_plus_one,
)


def test_answer_key_matches_sat():
    for inst in FULL_BATTERY:
        chi = chi_via_sat(inst.n, inst.edges)
        assert chi == inst.known_chi, f"{inst.name}: known_chi={inst.known_chi} but SAT says {chi}"
        print(f"  [ok] {inst.name}: chi = {chi}")


def test_reference_all_green():
    sc = grade(sat_lower_bound, "reference")
    assert sc.all_green, f"reference candidate should be all green:\n{sc.report()}"
    print("  [ok] reference (sat_lower_bound) is ALL GREEN")


def test_clique_fails_reproduces():
    sc = grade(clique_lower_bound, "clique")
    assert not sc.reproduces_target, "clique bound should fail reproduces_target (omega<6 on M^3(C5))"
    assert sc.control_immune, "clique bound (omega) should still be control-immune"
    print("  [ok] clique_lower_bound caught: fails reproduces_target, stays control-immune")


def test_degree_fails_control():
    sc = grade(max_degree_plus_one, "deg+1")
    assert not sc.control_immune, "max-degree+1 should fail control_immune (over-claims on L^infty)"
    print("  [ok] max_degree_plus_one caught: fails control_immune")


def main() -> int:
    tests = [
        test_answer_key_matches_sat,
        test_reference_all_green,
        test_clique_fails_reproduces,
        test_degree_fails_control,
    ]
    print("running toy smoke tests")
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
