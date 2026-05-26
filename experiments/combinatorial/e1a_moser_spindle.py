"""e1a: SAT verification that chi(Moser spindle) = 4.

Architecture 1 (combinatorial / UDG) baseline.

Two SAT decisions:
  - k = 3: expected UNSAT (the spindle is not 3-colorable)
  - k = 4: expected SAT with witness coloring

Multi-solver discipline: both decisions are run with cadical195 (CaDiCaL CDCL,
v1.9.5) and glucose4 (Glucose lineage with LBD), and the results must agree.
Two different solver families catch single-solver soundness bugs. Kissat is
intentionally not used here: its pysat binding segfaults on Windows when given
CNF via `bootstrap_with`. This sets the template for e1b (de Grey 1581-vertex)
and e1c (Polymath16) where multi-solver agreement is the only verification
short of a Lean DRAT-checker.

Artifacts archived under _cache/ (gitignored):
  - e1a_moser_spindle.json: solver agreement + witness colorings
  - e1a_moser_k3.cnf: DIMACS for the 3-coloring decision (UNSAT)
  - e1a_moser_k4.cnf: DIMACS for the 4-coloring decision (SAT)
"""

from __future__ import annotations

import json
import pathlib

from pysat.formula import CNF
from pysat.solvers import Solver

from experiments._shared.unit_distance_graph import moser_spindle


SOLVERS = ["cadical195", "glucose4"]
CACHE = pathlib.Path(__file__).parent / "_cache"


def solve_k_coloring(graph, k: int, solver_name: str):
    """Try to k-color `graph` with `solver_name`. Returns (sat, coloring or None)."""
    cnf = CNF(from_string=graph.to_dimacs(k))
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as s:
        if not s.solve():
            return False, None
        model = s.get_model()
        coloring = [-1] * graph.n
        for v in range(graph.n):
            for c in range(k):
                if model[v * k + c] > 0:
                    coloring[v] = c
                    break
        return True, coloring


def verify_coloring(graph, coloring) -> bool:
    """Confirm no unit-distance edge is monochromatic."""
    for u, v in graph.edges():
        if coloring[u] == coloring[v]:
            return False
    return True


def main():
    g = moser_spindle()
    edges = g.edges()
    print(f"Moser spindle: {g.n} vertices, {len(edges)} edges")

    CACHE.mkdir(exist_ok=True)
    results = {}

    # Phase 1: k = 3 must be UNSAT for every solver.
    print("\nphase 1: chi(Moser) <= 3?")
    for solver in SOLVERS:
        sat, coloring = solve_k_coloring(g, 3, solver)
        verdict = "SAT (UNEXPECTED)" if sat else "UNSAT"
        print(f"  {solver:10s} {verdict}")
        if sat:
            raise RuntimeError(
                f"{solver} found a 3-coloring of the Moser spindle; "
                f"this is a solver bug or a graph-construction bug. Coloring: {coloring}"
            )
        results[f"k3_{solver}"] = {"sat": False}

    # Phase 2: k = 4 must be SAT with a valid witness from every solver.
    print("\nphase 2: chi(Moser) <= 4?")
    witnesses = {}
    for solver in SOLVERS:
        sat, coloring = solve_k_coloring(g, 4, solver)
        verdict = "SAT" if sat else "UNSAT (UNEXPECTED)"
        print(f"  {solver:10s} {verdict}   coloring={coloring}")
        if not sat:
            raise RuntimeError(f"{solver} failed to find a 4-coloring of the Moser spindle")
        if not verify_coloring(g, coloring):
            raise RuntimeError(f"{solver} returned a coloring with a monochromatic edge: {coloring}")
        witnesses[solver] = coloring
        results[f"k4_{solver}"] = {"sat": True, "coloring": coloring}

    print(f"\nresult: chi(Moser spindle) = 4 confirmed by {len(SOLVERS)} independent solvers")

    # Archive.
    out_path = CACHE / "e1a_moser_spindle.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e1a_moser_spindle",
                "graph": "moser_spindle",
                "n_vertices": g.n,
                "n_edges": len(edges),
                "edges": edges,
                "chi": 4,
                "solvers": SOLVERS,
                "k3_unanimous_unsat": all(not results[f"k3_{s}"]["sat"] for s in SOLVERS),
                "k4_witnesses": witnesses,
            },
            f,
            indent=2,
        )
    (CACHE / "e1a_moser_k3.cnf").write_text(g.to_dimacs(3))
    (CACHE / "e1a_moser_k4.cnf").write_text(g.to_dimacs(4))
    print(f"archived: {out_path}")
    print(f"archived: {CACHE / 'e1a_moser_k3.cnf'} ({len(g.to_dimacs(3))} bytes)")
    print(f"archived: {CACHE / 'e1a_moser_k4.cnf'} ({len(g.to_dimacs(4))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
