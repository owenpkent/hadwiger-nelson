"""Unit-distance graph interface.

A unit-distance graph (UDG) has vertices in a metric space and edges between
pairs of vertices at distance exactly 1. For Hadwiger-Nelson work we keep
vertex coordinates symbolic (typically in a number field over Q) so distance
comparisons are exact.

The chromatic_number_sat method encodes k-colorability as CNF and dispatches
to a SAT solver to either return a witness coloring or a proof of UNSAT.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Optional

import sympy as sp


# Distance functions. Default is the squared Euclidean distance so we avoid
# square roots and stay inside the underlying ring.
def euclidean_sq(p, q):
    return sum((a - b) ** 2 for a, b in zip(p, q))


def linf(p, q):
    diffs = [sp.Abs(a - b) for a, b in zip(p, q)]
    return sp.Max(*diffs) if len(diffs) > 1 else diffs[0]


@dataclass
class UnitDistanceGraph:
    """A finite unit-distance graph with exact symbolic coordinates.

    vertices: iterable of tuples of sympy expressions
    distance_sq: callable (p, q) -> sympy expression (we compare to 1 exactly).
                 The default expects the Euclidean squared distance to equal 1.
                 For non-Euclidean metrics, pass a custom callable whose
                 target value is also given via target.
    target: sympy expression the distance function should equal for an edge.
            Default 1 (so Euclidean squared distance = 1 means distance = 1).
    label: human-readable name.
    """

    vertices: list = field(default_factory=list)
    distance_sq: Callable = euclidean_sq
    target: sp.Expr = sp.Integer(1)
    label: str = ""

    @property
    def n(self) -> int:
        return len(self.vertices)

    def edges(self) -> list[tuple[int, int]]:
        """Return list of (i, j) index pairs with i < j and distance == target."""
        es = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = sp.simplify(self.distance_sq(self.vertices[i], self.vertices[j]))
                if d == self.target:
                    es.append((i, j))
        return es

    def to_dimacs(self, k: int) -> str:
        """CNF for 'this graph is k-colorable'. Variables x_{v,c} = vertex v gets color c."""
        n, edges = self.n, self.edges()
        var = lambda v, c: v * k + c + 1  # 1-indexed, c in 0..k-1
        clauses = []
        for v in range(n):
            clauses.append([var(v, c) for c in range(k)])  # at-least-one
            for c1 in range(k):
                for c2 in range(c1 + 1, k):  # at-most-one
                    clauses.append([-var(v, c1), -var(v, c2)])
        for (u, v) in edges:
            for c in range(k):
                clauses.append([-var(u, c), -var(v, c)])
        head = f"p cnf {n*k} {len(clauses)}"
        body = "\n".join(" ".join(str(l) for l in cl) + " 0" for cl in clauses)
        return head + "\n" + body + "\n"

    def chromatic_number_sat(self, k_max: int = 7):
        """Try k = 1, 2, ... up to k_max. Returns (chi, coloring or None).

        Requires `python-sat`. If unavailable, returns (None, "python-sat not installed").
        """
        try:
            from pysat.formula import CNF
            from pysat.solvers import Solver
        except ImportError:
            return None, "python-sat not installed"
        n = self.n
        for k in range(1, k_max + 1):
            cnf = CNF(from_string=self.to_dimacs(k))
            with Solver(name="cadical", bootstrap_with=cnf.clauses) as s:
                if s.solve():
                    model = s.get_model()
                    coloring = [None] * n
                    for v in range(n):
                        for c in range(k):
                            if model[v * k + c] > 0:
                                coloring[v] = c
                                break
                    return k, coloring
        return None, f"not {k_max}-colorable"


# ---------- canonical small examples ----------

def moser_spindle() -> UnitDistanceGraph:
    """The Moser spindle: 7-vertex UDG with chi = 4.

    Built from two rhombi of unit edges sharing an edge, then connecting tips
    so that the two outer triangles meet at unit distance.
    """
    sqrt3 = sp.sqrt(3)
    # Two unit rhombi each made of two equilateral triangles.
    # Apex shared at origin.
    A = (sp.Integer(0), sp.Integer(0))
    B = (sp.Integer(1), sp.Integer(0))
    C = (sp.Rational(1, 2), sqrt3 / 2)
    D = (sp.Rational(3, 2), sqrt3 / 2)
    # Rotate the second rhombus about A by an angle so its outer tip is at unit
    # distance from B's outer tip. Standard Moser construction uses arccos(5/6).
    theta = sp.acos(sp.Rational(5, 6))
    rot = lambda p: (sp.cos(theta) * p[0] - sp.sin(theta) * p[1],
                     sp.sin(theta) * p[0] + sp.cos(theta) * p[1])
    Bp = rot(B)
    Cp = rot(C)
    Dp = rot(D)
    verts = [A, B, C, D, Bp, Cp, Dp]
    return UnitDistanceGraph(vertices=verts, label="Moser spindle")
