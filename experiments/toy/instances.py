"""The toy battery: finite graphs with KNOWN chromatic number.

The Hadwiger-Nelson analog of the zeta repo's function-field toy world. There,
RH is a theorem (Weil) so a proof-move can be graded. Here, the chromatic number
of a finite graph is decidable by SAT, so it is the answer key: a proposed
chi-lower-bound TECHNIQUE can be graded right or wrong, and a control-blind or
circular technique is caught on contact.

The battery splits three ways:
  POSITIVE (known chi >= 6): the technique must reach the target here.
  NEGATIVE (known chi < 6):  the technique must NOT claim >= 6 here (the fakes).
  CONTROL  (the firewall):   the three wrong-approach detectors as gradeable
                             instances (Q^2 chi=2, L^infty chi=4, R^1 chi=2). A
                             technique that over-claims on a control is wrong, the
                             same way a D-H-blind argument is wrong in the zeta toy.

A candidate never sees `known_chi`. It receives only `ToyData` (n, edges), exactly
the abstract-graph information a real lower-bound technique is allowed to use.

The honest caveat (identical in spirit to the zeta toy): the answer key here is
decidable because the graphs are FINITE. The real obstruction, W3 = unit-distance
realizability of a chi>=6 host in R^2, is NOT in the toy. The toy grades the
technique; it cannot grade the lift. The delta between "passes the battery" and
"produces a planar UDG" is the compass, not the proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from experiments._shared.unit_distance_graph import moser_spindle
from experiments._shared.wrong_approach_detectors import (
    rational_unit_distance_sample,
    linf_unit_grid,
    r1_unit_chain,
)


# ---------------------------------------------------------------------------
# Abstract-graph data types.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ToyData:
    """The candidate's view of an instance: the abstract graph only. Deliberately
    excludes known_chi and any embedding, so a technique cannot read the answer."""
    n: int
    edges: tuple   # tuple of (i, j), i < j


@dataclass(frozen=True)
class ToyInstance:
    name: str
    n: int
    edges: tuple
    known_chi: int          # ANSWER KEY, hidden from candidates
    kind: str               # 'abstract' | 'udg' | 'control'
    control: Optional[str] = None   # 'Q2' | 'Linf' | 'R1' for control instances
    note: str = ""

    @property
    def target(self) -> bool:
        """True iff this instance genuinely has chi >= 6."""
        return self.known_chi >= 6

    def to_data(self) -> ToyData:
        return ToyData(n=self.n, edges=self.edges)


# ---------------------------------------------------------------------------
# Graph builders (abstract, on integer vertex labels 0..n-1).
# ---------------------------------------------------------------------------
def complete_graph(n: int) -> tuple:
    return tuple((i, j) for i in range(n) for j in range(i + 1, n))


def cycle(n: int) -> tuple:
    return tuple((i, (i + 1) % n) if i + 1 < n else (0, i) for i in range(n))


def mycielskian(n: int, edges) -> tuple[int, tuple]:
    """Mycielski construction M(G): raises chromatic number by 1, keeps the graph
    triangle-free if G is. Vertices: originals 0..n-1, shadows n..2n-1, apex 2n.
    Edges: original edges; for each original edge (i,j) add shadow-original edges
    (n+i, j) and (i, n+j); apex 2n joined to every shadow."""
    adj = [set() for _ in range(n)]
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)
    out = set()
    for i, j in edges:
        a, b = (i, j) if i < j else (j, i)
        out.add((a, b))
    for i in range(n):
        for j in adj[i]:
            u, v = n + i, j           # shadow of i to original neighbor j
            out.add((u, v) if u < v else (v, u))
    apex = 2 * n
    for i in range(n):
        out.add((n + i, apex))
    return 2 * n + 1, tuple(sorted(out))


def _mycielski_tower(base_n: int, base_edges: tuple, levels: int) -> tuple[int, tuple]:
    n, e = base_n, base_edges
    for _ in range(levels):
        n, e = mycielskian(n, e)
    return n, e


def _from_udg(udg) -> tuple[int, tuple]:
    """Abstract (n, edges) of a UnitDistanceGraph instance."""
    return udg.n, tuple(udg.edges())


# Mycielski tower over C5 (chi 3): M(C5)=Grotzsch chi 4, M^2 chi 5, M^3 chi 6.
# These are triangle-free, so omega = 2: the hardest test of any clique-based bound.
_M2_N, _M2_E = _mycielski_tower(5, cycle(5), 2)   # chi 5, 23 vertices
_M3_N, _M3_E = _mycielski_tower(5, cycle(5), 3)   # chi 6, 47 vertices

_MOSER_N, _MOSER_E = _from_udg(moser_spindle())
_Q2_N, _Q2_E = _from_udg(rational_unit_distance_sample())
_LINF_N, _LINF_E = _from_udg(linf_unit_grid(size=3))
_R1_N, _R1_E = _from_udg(r1_unit_chain(n=6))


# ---------------------------------------------------------------------------
# The batteries.
# ---------------------------------------------------------------------------
POSITIVE_BATTERY = [
    ToyInstance("K6 (chi=6, omega=6)", 6, complete_graph(6), 6, "abstract",
                note="trivial chi>=6; a clique bound gets this for free"),
    ToyInstance("K7 (chi=7)", 7, complete_graph(7), 7, "abstract"),
    ToyInstance("M^3(C5) (chi=6, triangle-free, omega=2)", _M3_N, _M3_E, 6, "abstract",
                note="the hard positive: chi=6 with omega=2, the clamp-route regime"),
]

NEGATIVE_BATTERY = [
    ToyInstance("C5 (chi=3)", 5, cycle(5), 3, "abstract"),
    ToyInstance("Moser spindle (chi=4, UDG)", _MOSER_N, _MOSER_E, 4, "udg"),
    ToyInstance("M^2(C5) (chi=5, triangle-free)", _M2_N, _M2_E, 5, "abstract",
                note="the fake: chi exactly 5; a technique that calls this >=6 is wrong"),
]

CONTROL_BATTERY = [
    ToyInstance("Q^2 control (chi=2)", _Q2_N, _Q2_E, 2, "control", control="Q2",
                note="rational plane is bipartite (Woodall)"),
    ToyInstance("L^infty control (chi=4)", _LINF_N, _LINF_E, 4, "control", control="Linf",
                note="king-grid; chi=4 exactly (Chilakamarri)"),
    ToyInstance("R^1 control (chi=2)", _R1_N, _R1_E, 2, "control", control="R1",
                note="the line; blind to the rotation group O(2)"),
]

FULL_BATTERY = POSITIVE_BATTERY + NEGATIVE_BATTERY + CONTROL_BATTERY


# ---------------------------------------------------------------------------
# The answer key: exact chi by SAT (used to verify the battery and as the
# reference candidate's engine). Finite graphs only; this is the whole point.
# ---------------------------------------------------------------------------
def chi_via_sat(n: int, edges, kmax: int = 8) -> Optional[int]:
    """Exact chromatic number by trying k = 1, 2, ... up to kmax (first SAT wins).
    Returns None if python-sat is unavailable or chi > kmax."""
    try:
        from pysat.formula import CNF
        from pysat.solvers import Solver
    except ImportError:
        return None

    def dimacs(k: int) -> str:
        var = lambda v, c: v * k + c + 1
        clauses = []
        for v in range(n):
            clauses.append([var(v, c) for c in range(k)])
            for c1 in range(k):
                for c2 in range(c1 + 1, k):
                    clauses.append([-var(v, c1), -var(v, c2)])
        for (u, v) in edges:
            for c in range(k):
                clauses.append([-var(u, c), -var(v, c)])
        head = f"p cnf {n * k} {len(clauses)}"
        body = "\n".join(" ".join(str(l) for l in cl) + " 0" for cl in clauses)
        return head + "\n" + body + "\n"

    for k in range(1, kmax + 1):
        cnf = CNF(from_string=dimacs(k))
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as s:
            if s.solve():
                return k
    return None
