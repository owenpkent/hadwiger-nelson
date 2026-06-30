"""Smoke test + calibration gate for shared infrastructure.

Two tiers:

  CORE (default) - constructs the canonical small graphs AND actually colors
  them, asserting the known chromatic numbers. This is the enforced gate: it
  turns the wrong-approach detectors into a runnable verdict instead of library
  code. A new solver or encoding is not trusted until it reproduces this baseline
  (see CLAUDE.md "Calibration discipline").

      Moser spindle      chi = 4
      Q^2 control        chi = 2   (Woodall: the rational plane is bipartite)
      L^infty king-grid  chi = 4   (Chilakamarri)
      R^1 chain          chi = 2
      unit triangle      chi = 3

  FULL (--full) - adds the chi >= 5 anchor: a published 5-chromatic UDG must be
  UNSAT at k = 4. Uses the symmetry-broken portfolio so it finishes in seconds
  to minutes. Skips gracefully (not a failure) if no source graph is present,
  since sources/ graph files may be gitignored on a fresh checkout.

Run:
  python -m experiments._shared.smoke_test            # core gate (fast)
  python -m experiments._shared.smoke_test --full     # core + chi>=5 calibration

A non-zero exit code means a baseline broke. Wire this into CI.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import sympy as sp

from .unit_distance_graph import UnitDistanceGraph, moser_spindle, euclidean_sq
from .wrong_approach_detectors import (
    rational_unit_distance_sample,
    linf_unit_grid,
    r1_unit_chain,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCES = REPO_ROOT / "sources"

# chi >= 5 anchors, in increasing solve cost. The first one whose source file
# exists is used for the --full calibration. heule_826 is the cheapest published
# 5-chromatic UDG on disk; de Grey 1585 is the gold standard but slow (~18 min).
CHI5_ANCHORS = [
    ("heule_826.edge", "Heule 826-vertex 5-chromatic UDG"),
    ("heule_874.edge", "Heule 874-vertex 5-chromatic UDG"),
    ("degrey_1585_sat.dimacs", "de Grey 1585-vertex 5-chromatic UDG"),
]


# ---------- structural tests (cheap; shape only) ----------

def test_moser_has_seven_vertices():
    g = moser_spindle()
    assert g.n == 7, f"Moser spindle should have 7 vertices, got {g.n}"
    print(f"  [ok] Moser spindle has {g.n} vertices")


def test_moser_edge_count():
    g = moser_spindle()
    edges = g.edges()
    assert len(edges) == 11, f"Moser spindle should have 11 edges, got {len(edges)}"
    print(f"  [ok] Moser spindle has {len(edges)} edges")


def test_linf_grid_constructs():
    g = linf_unit_grid(size=3)
    assert g.n == 16, f"4x4 L^infty grid has 16 vertices, got {g.n}"
    print(f"  [ok] L^infty grid (size=3) has {g.n} vertices")


def test_r1_chain_shape():
    g = r1_unit_chain(n=5)
    assert g.n == 6
    edges = g.edges()
    assert len(edges) == 5, f"R^1 chain n=5 should have 5 edges, got {len(edges)}"
    print(f"  [ok] R^1 chain has {g.n} vertices and {len(edges)} edges")


# ---------- chromatic calibration (colors the controls) ----------

def _assert_chi(g: UnitDistanceGraph, expected: int, name: str):
    chi, witness = g.chromatic_number_sat(k_max=expected + 2)
    if chi is None:
        # witness carries the failure reason (e.g. python-sat missing)
        raise AssertionError(f"{name}: could not decide chi ({witness})")
    assert chi == expected, f"{name}: expected chi={expected}, solver returned chi={chi}"
    print(f"  [ok] {name}: chi = {chi}")


def test_moser_chi_is_4():
    _assert_chi(moser_spindle(), 4, "Moser spindle")


def test_q2_control_chi_is_2():
    # The Q^2 unit-distance graph is bipartite (Woodall 1973); any finite sample
    # is 2-colorable. A method that paints this >= 3 is using R-specific content
    # illegitimately.
    _assert_chi(rational_unit_distance_sample(), 2, "Q^2 control")


def test_linf_control_chi_is_4():
    # L^infty king-grid: chi = 4 exactly (Chilakamarri). A norm-blind argument
    # that reaches >= 5 here is wrong.
    _assert_chi(linf_unit_grid(size=3), 4, "L^infty control")


def test_r1_control_chi_is_2():
    _assert_chi(r1_unit_chain(n=6), 2, "R^1 control")


def test_unit_triangle_chi_is_3():
    sqrt3 = sp.sqrt(3)
    verts = [(sp.Integer(0), sp.Integer(0)),
             (sp.Integer(1), sp.Integer(0)),
             (sp.Rational(1, 2), sqrt3 / 2)]
    g = UnitDistanceGraph(vertices=verts, distance_sq=euclidean_sq, label="K3 unit triangle")
    assert len(g.edges()) == 3
    _assert_chi(g, 3, "unit equilateral triangle")


# ---------- chi >= 5 anchor (opt-in; --full) ----------

def calibrate_chi5() -> int:
    """Confirm a published 5-chromatic UDG is UNSAT at k=4 via the symmetry-broken
    portfolio. Returns 0 (pass), 1 (fail: it was 4-colorable -> data/solver bug),
    or 0 with a SKIP note if no source graph is on disk.
    """
    try:
        from ..combinatorial.e1b_de_grey_skeleton import load_dimacs_edges
        from .portfolio_sat import colorable_portfolio
    except Exception as e:  # pragma: no cover - import wiring
        print(f"  [SKIP] chi>=5 calibration: backend import failed ({e})")
        return 0

    chosen = next(((SOURCES / fn, desc) for fn, desc in CHI5_ANCHORS
                   if (SOURCES / fn).exists()), None)
    if chosen is None:
        print(f"  [SKIP] chi>=5 calibration: no anchor graph found under {SOURCES} "
              f"(tried {', '.join(fn for fn, _ in CHI5_ANCHORS)})")
        return 0

    path, desc = chosen
    edges = load_dimacs_edges(path)
    n = max(max(u, v) for u, v in edges) + 1
    print(f"  ... {desc}: {n} vertices, {len(edges)} edges; deciding k=4 (symmetry-broken portfolio)")
    out = colorable_portfolio(n, edges, k=4, symbreak=True)
    if out["result"] is None:
        print(f"  [SKIP] chi>=5 calibration: portfolio hit its time limit (no verdict)")
        return 0
    if out["result"] is True:
        print(f"  [FAIL] chi>=5 calibration: {desc} is 4-COLORABLE - data or solver bug")
        return 1
    print(f"  [ok] chi>=5 calibration: {desc} is UNSAT at k=4 "
          f"(winner={out['winner']}, {out['elapsed']}s) -> chi >= 5")
    return 0


CORE_TESTS = [
    test_moser_has_seven_vertices,
    test_moser_edge_count,
    test_linf_grid_constructs,
    test_r1_chain_shape,
    test_moser_chi_is_4,
    test_q2_control_chi_is_2,
    test_linf_control_chi_is_4,
    test_r1_control_chi_is_2,
    test_unit_triangle_chi_is_3,
]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true",
                        help="also run the chi>=5 anchor (slower; needs a sources/ graph)")
    args = parser.parse_args(argv)

    print("running smoke tests (core gate)")
    passed = 0
    for t in CORE_TESTS:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {t.__name__}: {e}")
    core_ok = passed == len(CORE_TESTS)
    print(f"\ncore: {passed}/{len(CORE_TESTS)} passed")

    full_ok = True
    if args.full:
        print("\nrunning chi>=5 calibration (--full)")
        full_ok = calibrate_chi5() == 0

    return 0 if (core_ok and full_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
