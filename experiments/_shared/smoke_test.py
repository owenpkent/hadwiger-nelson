"""Smoke test for shared infrastructure.

Run with: python -m experiments._shared.smoke_test
"""

from __future__ import annotations

import sympy as sp

from .unit_distance_graph import UnitDistanceGraph, moser_spindle, euclidean_sq
from .wrong_approach_detectors import (
    rational_unit_distance_sample,
    linf_unit_grid,
    r1_unit_chain,
)


def test_moser_has_seven_vertices():
    g = moser_spindle()
    assert g.n == 7, f"Moser spindle should have 7 vertices, got {g.n}"
    print(f"  [ok] Moser spindle has {g.n} vertices")


def test_moser_edge_count():
    g = moser_spindle()
    edges = g.edges()
    # Moser spindle has 11 unit-distance edges.
    assert len(edges) == 11, f"Moser spindle should have 11 edges, got {len(edges)}"
    print(f"  [ok] Moser spindle has {len(edges)} edges")


def test_q2_control_is_finite_sample():
    g = rational_unit_distance_sample()
    assert g.n > 0
    print(f"  [ok] Q^2 control has {g.n} vertices")


def test_linf_grid_constructs():
    g = linf_unit_grid(size=3)
    assert g.n == 16, f"4x4 L^infty grid has 16 vertices, got {g.n}"
    print(f"  [ok] L^infty grid (size=3) has {g.n} vertices")


def test_r1_chain():
    g = r1_unit_chain(n=5)
    assert g.n == 6
    edges = g.edges()
    # Consecutive integers are at distance 1, so n edges total.
    assert len(edges) == 5, f"R^1 chain n=5 should have 5 edges, got {len(edges)}"
    print(f"  [ok] R^1 chain has {g.n} vertices and {len(edges)} edges")


def test_simple_triangle_is_3_chromatic():
    """Equilateral triangle with side 1 has chi = 3."""
    sqrt3 = sp.sqrt(3)
    verts = [(sp.Integer(0), sp.Integer(0)),
             (sp.Integer(1), sp.Integer(0)),
             (sp.Rational(1, 2), sqrt3 / 2)]
    g = UnitDistanceGraph(vertices=verts, label="K3 unit triangle")
    edges = g.edges()
    assert len(edges) == 3, f"K3 should have 3 edges, got {len(edges)}"
    print(f"  [ok] equilateral triangle has {len(edges)} edges (K3)")


def main():
    tests = [
        test_moser_has_seven_vertices,
        test_moser_edge_count,
        test_q2_control_is_finite_sample,
        test_linf_grid_constructs,
        test_r1_chain,
        test_simple_triangle_is_3_chromatic,
    ]
    print("running smoke tests")
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
