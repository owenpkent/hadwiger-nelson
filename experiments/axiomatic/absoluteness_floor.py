"""Absoluteness floor for the 2050-independence retrodiction (Architecture 4).

The retrodicted world is: chi(R^2) = 6 under ZF+DC+LM and = 7 under ZFC, so
"chi(R^2)=6" is independent of ZFC. The ONE rigorous, currently-provable backbone
of that world is the *absoluteness floor*:

    A finite unit-distance graph G in R^2 with chi(G) >= k is a Borel object
    (finite => discrete => every subset Borel and Lebesgue measurable in R^2).
    Therefore chi_m(R^2) >= chi_B(R^2) >= chi(R^2) >= k in EVERY model of ZF+DC.
    The lower edge does NOT move between models.

This is why the independence in the retrodiction CANNOT sit at the 5 threshold
(de Grey's finite 5-chromatic UDG nails chi >= 5 absolutely) and must sit strictly
above 5, at the {6,7} split. This script certifies the floor for a concrete finite
UDG using exact arithmetic (sympy, no floating point) for the distances and two
independent SAT solvers for the chromatic lower bound, then states the lift.

It does NOT prove anything model-dependent (that is the speculative part of the
retrodiction). It certifies the absolute backbone that any such world must respect.
"""

from __future__ import annotations

import json
import pathlib

import sympy as sp
from pysat.formula import CNF
from pysat.solvers import Solver

from experiments._shared.unit_distance_graph import moser_spindle

SOLVERS = ["cadical195", "glucose4"]
CACHE = pathlib.Path(__file__).parent / "_cache"


def exact_edges_are_unit(graph) -> tuple[bool, int]:
    """Verify every edge has distance EXACTLY 1 in exact (sympy) arithmetic.

    Returns (all_unit, n_edges). No floating point: distances are simplified
    symbolically and compared to 1.
    """
    verts = graph.vertices
    n_ok = 0
    edges = graph.edges()
    for u, v in edges:
        d2 = sp.simplify(graph.distance_sq(verts[u], verts[v]))
        if sp.simplify(d2 - graph.target) != 0:
            return False, len(edges)
        n_ok += 1
    return n_ok == len(edges), len(edges)


def solve_k_coloring(graph, k: int, solver_name: str):
    cnf = CNF(from_string=graph.to_dimacs(k))
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as s:
        sat = s.solve()
        return sat


def certify_floor(graph, name: str, k_lower: int) -> dict:
    """Certify chi(graph) >= k_lower absolutely.

    k_lower is the largest k for which the (k_lower-1)-coloring is UNSAT.
    For the Moser spindle, chi = 4, so the 3-coloring is UNSAT => chi >= 4.
    """
    all_unit, n_edges = exact_edges_are_unit(graph)

    # chi >= k_lower  iff  (k_lower - 1)-coloring is UNSAT.
    unsat_results = {}
    for solver in SOLVERS:
        unsat_results[solver] = not solve_k_coloring(graph, k_lower - 1, solver)
    chi_ge = all(unsat_results.values())

    # sanity: k_lower-coloring should be SAT (so the bound is tight at this witness).
    sat_results = {}
    for solver in SOLVERS:
        sat_results[solver] = solve_k_coloring(graph, k_lower, solver)
    colorable_at_k = all(sat_results.values())

    return {
        "graph": name,
        "n_vertices": graph.n,
        "n_edges": n_edges,
        "all_edges_unit_exact": all_unit,
        "k_lower": k_lower,
        "unsat_at_k_minus_1": unsat_results,
        "chi_ge_k_lower_absolute": chi_ge and all_unit,
        "sat_at_k_lower": sat_results,
        "colorable_at_k_lower": colorable_at_k,
        # The lift: a finite chi>=k UDG is Borel, so the bound holds in every model.
        "lifts_to": {
            "chi_R2_ge": k_lower if (chi_ge and all_unit) else None,
            "chi_B_R2_ge": k_lower if (chi_ge and all_unit) else None,
            "chi_m_R2_ge": k_lower if (chi_ge and all_unit) else None,
            "model_dependent": False,
            "reason": (
                "finite point set is Borel and Lebesgue measurable in R^2; "
                "chi <= chi_B <= chi_m and a finite chi>=k witness is absolute"
            ),
        },
    }


def main() -> None:
    CACHE.mkdir(exist_ok=True)
    spindle = moser_spindle()
    # Moser spindle: chi = 4, so 3-coloring UNSAT => chi >= 4 absolutely.
    result = certify_floor(spindle, "moser_spindle", k_lower=4)

    summary = {
        "purpose": (
            "Absoluteness floor for the 2050 chi(R^2) independence retrodiction. "
            "Certifies that a finite chi>=k UDG forces chi/chi_B/chi_m(R^2) >= k "
            "in every model of ZF+DC (the lower edge does not move). The Moser "
            "spindle stands in for de Grey's finite 5-chromatic UDG; the same lift "
            "applies verbatim to k=5 (de Grey) and, in the retrodicted world, k=6 "
            "(the missing realizable color-clamp of L51-L53)."
        ),
        "spindle_floor": result,
        "consequence_for_retrodiction": (
            "Because chi>=5 is absolute (de Grey, finite Borel witness), the "
            "ZFC-vs-Solovay independence cannot live at the 5 threshold. It is "
            "forced to the {6,7} split: chi=6 under ZF+DC+LM, chi=7 under ZFC. "
            "The model-dependent content is therefore an UPPER-bound question "
            "(does a measurable 6-coloring exist?), not a lower-bound question."
        ),
    }

    out = CACHE / "absoluteness_floor.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Absoluteness floor certificate")
    print(f"  graph: {result['graph']}  (n={result['n_vertices']}, "
          f"m={result['n_edges']})")
    print(f"  all edges exactly unit (sympy): {result['all_edges_unit_exact']}")
    print(f"  {result['k_lower']-1}-coloring UNSAT (both solvers): "
          f"{result['unsat_at_k_minus_1']}")
    print(f"  chi >= {result['k_lower']} ABSOLUTE: "
          f"{result['chi_ge_k_lower_absolute']}")
    print(f"  lifts to chi_m(R^2) >= {result['lifts_to']['chi_m_R2_ge']} "
          f"in every model (model_dependent="
          f"{result['lifts_to']['model_dependent']})")
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
