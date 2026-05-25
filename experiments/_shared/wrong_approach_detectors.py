"""Wrong-approach detectors for the Hadwiger-Nelson chromatic number problem.

Analog of the Davenport-Heilbronn discipline from the zeta-function repo.

Three control objects whose chromatic numbers are *known* and *different* from
chi(R^2). Any candidate proof of chi(R^2) >= 5 should structurally fail on the
detector appropriate to its architecture.

Controls:
  - Q^2: rational plane has chi = 2 (Woodall 1973). Catches Architecture 1
    methods that don't use the topology / density of R.
  - L^infty unit-distance graph on R^2: chi = 4 (Chilakamarri). Catches
    Architecture 3 methods that don't use Euclidean rigidity.
  - R^1 line: chi = 2 trivially. Catches Architecture 2 methods that don't
    use the 2D rotation group.

A candidate-method M is a function that takes a UnitDistanceGraph and returns
either (a) a lower-bound certificate for chi (a number) or (b) None.
The detector check runs M on each control and confirms M does NOT produce a
lower bound stronger than the known value for that control.
"""

from __future__ import annotations

from typing import Callable, Optional

import sympy as sp

from .unit_distance_graph import UnitDistanceGraph, euclidean_sq, linf


# ---------- Q^2 detector ----------

def rational_unit_distance_sample(num_points: int = 50, denom_bound: int = 10) -> UnitDistanceGraph:
    """A finite sample of Q^2 used as a probe. Vertices with rational coordinates
    and bounded denominator; expected chromatic number is 2 (any finite subset
    of the Q^2-UDG is 2-colorable since the full Q^2-UDG is bipartite).
    """
    verts = []
    # Include the standard 2-colorable witnesses: rational points where unit
    # distance edges exist. Examples: (0,0), (1,0), (3/5, 4/5), (4/5, 3/5).
    for p, q in [(0, 1), (1, 1), (3, 5), (4, 5), (5, 13), (12, 13), (8, 17), (15, 17)]:
        verts.append((sp.Rational(p, q), sp.Rational(0)))
        verts.append((sp.Rational(0), sp.Rational(p, q)))
    # Add some derived edges via Pythagorean triples.
    for a, b, c in [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]:
        verts.append((sp.Rational(a, c), sp.Rational(b, c)))
        verts.append((sp.Rational(b, c), sp.Rational(a, c)))
    seen = set()
    uniq = []
    for v in verts:
        key = (str(v[0]), str(v[1]))
        if key not in seen:
            seen.add(key)
            uniq.append(v)
    return UnitDistanceGraph(
        vertices=uniq,
        distance_sq=euclidean_sq,
        target=sp.Integer(1),
        label="Q^2 control (rational sample)",
    )


# ---------- L^infty detector ----------

def linf_unit_grid(size: int = 5) -> UnitDistanceGraph:
    """Integer grid [0,size] x [0,size] with L^infty unit-distance edges.
    Expected chi = 4.
    """
    verts = [(sp.Integer(i), sp.Integer(j)) for i in range(size + 1) for j in range(size + 1)]
    return UnitDistanceGraph(
        vertices=verts,
        distance_sq=lambda p, q: sp.Max(sp.Abs(p[0] - q[0]), sp.Abs(p[1] - q[1])),
        target=sp.Integer(1),
        label="L^infty control (king-grid)",
    )


# ---------- R^1 detector ----------

def r1_unit_chain(n: int = 6) -> UnitDistanceGraph:
    """Integer points 0..n on R^1 with unit-distance edges. Expected chi = 2."""
    verts = [(sp.Integer(i),) for i in range(n + 1)]
    return UnitDistanceGraph(
        vertices=verts,
        distance_sq=lambda p, q: (p[0] - q[0]) ** 2,
        target=sp.Integer(1),
        label="R^1 control",
    )


# ---------- detector runner ----------

KNOWN_CHI = {
    "Q^2 control (rational sample)": 2,
    "L^infty control (king-grid)": 4,
    "R^1 control": 2,
}


def run_detector(method: Callable[[UnitDistanceGraph], Optional[int]], label: str = "") -> dict:
    """Run a candidate lower-bound method on all controls.

    Returns a dict with per-control results. A method passes if its reported
    lower bound on each control is <= KNOWN_CHI[control].
    """
    results = {"label": label, "controls": []}
    for control in [
        rational_unit_distance_sample(),
        linf_unit_grid(size=4),
        r1_unit_chain(n=6),
    ]:
        known = KNOWN_CHI[control.label]
        try:
            bound = method(control)
        except Exception as e:
            bound = f"error: {e}"
        passed = isinstance(bound, int) and bound <= known
        results["controls"].append({
            "control": control.label,
            "known_chi": known,
            "method_bound": bound,
            "passed": passed,
        })
    results["overall"] = all(c["passed"] for c in results["controls"])
    return results
