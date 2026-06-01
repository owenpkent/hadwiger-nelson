r"""F1 pressure-test, Attack 3: DOF / counting analysis of the re-embedding question.

The sharp rigorous question (task attack 3): take the abstract chi-6 graph's
saturating hubs v and their required bridge-source sets U_v. Instead of testing
cocircularity in INHERITED coords (L23/L27, which fails), try to RE-EMBED: solve
for plane coordinates making each U_v cocircular at unit radius SIMULTANEOUSLY.
Is the system over-determined? DOF vs constraints.

This script does the counting for the GENERAL re-embedding problem and validates
it on small explicit obstruction graphs (Moser x Moser from L23, where the abstract
chi-5 (not 6) graph already fails to embed -- the cleanest decisive small case).

DOF accounting for re-embedding a graph G=(V,E) as a UDG in the plane:
  - Variables: 2|V| coordinates, minus 3 for the global rigid motion (translation
    + rotation) gauge freedom = 2|V| - 3 effective DOF.
  - Constraints: one equation per edge ( dist^2 = 1 ), so |E| equations.
  - Generic rigidity / realizability heuristic: a UDG embedding generically exists
    (with finitely many solutions) when 2|V| - 3 >= |E|, i.e. |E| <= 2|V| - 3.
    When |E| > 2|V| - 3 the system is OVER-determined and a UDG embedding exists
    only on a measure-zero (non-generic) coincidence variety.

The chi-6 abstract graphs (L27/L28) have |E| >> 2|V|: they are massively
over-determined. We quantify the over-determination for the L27/L28 family and
for the minimal L23 Moser x Moser graph.
"""
from __future__ import annotations
import sys, pathlib, json, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
from f1pt_lib import load_p510, sat_kcolor, CACHE
from pysat.solvers import Cadical195


def moser_spindle():
    """7-vertex Moser spindle, exact coords in Q(sqrt3, sqrt11), 11 edges."""
    s3 = sp.sqrt(3)
    A = (sp.Integer(0), sp.Integer(0))
    B = (sp.Integer(1), sp.Integer(0))
    C = (sp.Rational(1,2), s3/2)
    D = (sp.Rational(3,2), s3/2)
    # rotate the rhombus A,B,C,D by angle with cos=5/6,sin=sqrt11/6 about A
    c, s = sp.Rational(5,6), sp.sqrt(11)/6
    def rot(p): return (c*p[0]-s*p[1], s*p[0]+c*p[1])
    E2 = rot(B); F2 = rot(C); G2 = rot(D)
    pts = [A,B,C,D,E2,F2,G2]
    # edges: unit-distance pairs
    edges=[]
    for i in range(7):
        for j in range(i+1,7):
            dx=pts[i][0]-pts[j][0]; dy=pts[i][1]-pts[j][1]
            if sp.simplify(dx*dx+dy*dy)==1: edges.append((i,j))
    return pts, edges


def dof_report(name, nV, nE):
    eff = 2*nV - 3
    over = nE - eff
    return {"graph": name, "V": nV, "E": nE,
            "effective_DOF": eff, "edge_constraints": nE,
            "overdetermination": over,
            "generically_realizable": over <= 0}


def main():
    out = {"note": "DOF heuristic: UDG embedding generic iff |E| <= 2|V|-3"}
    rows = []

    # Moser spindle (sanity: known realizable)
    mpts, medges = moser_spindle()
    rows.append(dof_report("Moser spindle", 7, len(medges)))

    # L23 Moser x Moser + 14 bridges (abstract chi=5, NOT realizable)
    # 2 mosers (7+7=14 V, 11+11=22 E) + 14 bridges = 36 E
    rows.append(dof_report("L23 MoserxMoser+14B (abstract chi5)", 14, 22+14))

    # L27 chi-6: P_510 U P_510 + 2700 bridges
    base, edges = load_p510()
    nE_p510 = len(edges)
    rows.append(dof_report("L27 P510^2 + 2700B (abstract chi6)", 1020, 2*nE_p510+2700))
    # L28 with 2000 bridges
    rows.append(dof_report("L28 P510^2 + 2000B (abstract chi6)", 1020, 2*nE_p510+2000))

    # SINGLE-HUB sub-question: a hub v + 5 cocircular sources that are rainbow-forced.
    # The minimal rainbow-FORCING structure on 5 vertices forcing 5 distinct colors,
    # IF it were a UDG, plus the 5 cocircularity constraints on v's circle.
    # Cocircularity of k sources on v's circle = k unit-distance edges (source,v): k edges.
    # Plus the rainbow-forcing subgraph edges. For the 5 sources to be rainbow-forced
    # they need to live in a chi-5 structure. The smallest chi-5 UDG is P_510 (510 V).
    # So a single realizable saturated hub costs >= 510 + 1 vertices and inherits all
    # 2504 + (cocircularity edges) constraints. Per-hub it is already P_510-scale.
    rows.append({"graph": "single realizable saturated hub (lower bound)",
                 "note": "needs a chi-5 rainbow generator (smallest known = P_510, 510V) "
                         "PLUS 5 sources cocircular at unit radius on the hub circle. "
                         "The 5 cocircular sources must each be a graph vertex at mutual "
                         "distances allowing chi-5 rainbow-forcing AND all at distance 1 "
                         "from the hub. The hub-circle constraint pins all 5 to one circle "
                         "(2 DOF for the circle center), removing freedom needed to embed "
                         "the chi-5 generator."})

    out["rows"] = rows
    for r in rows:
        if "overdetermination" in r:
            print(f"{r['graph']:<45} V={r['V']:>5} E={r['E']:>6} "
                  f"2V-3={r['effective_DOF']:>5} over={r['overdetermination']:>6} "
                  f"{'REALIZABLE-generic' if r['generically_realizable'] else 'OVER-DETERMINED'}")
        else:
            print(f"{r['graph']}: {r.get('note','')[:80]}")

    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "f1pt_attack3_dof.json").write_text(json.dumps(out, indent=2, default=str))
    print("saved", CACHE / "f1pt_attack3_dof.json")

if __name__ == "__main__":
    main()
