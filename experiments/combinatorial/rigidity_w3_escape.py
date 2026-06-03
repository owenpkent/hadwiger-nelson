"""Rigidity / realizability analysis of the W3 wall and its escape routes.

BUILDER (rigidity/realizability lens). Attacks W3: when is an abstract no-K4
chi=6 graph unit-distance realizable in R^2?

Core reframing (made precise here):

  The W3 obstruction is a COUPLED RIGIDITY equation count. With two rigid halves
  H1 (pinned) and H2 (rigid body, 3-DOF pose), each realized bridge edge is ONE
  analytic equation |u - w(p)|^2 = 1 in the 3 pose unknowns p = (tx, ty, theta).
  m bridges => m equations in 3 unknowns => generically empty for m >= 4. The
  L42 abstract chi-6 graphs need m ~ 2000 bridges: over-determined by ~1997.

  ESCAPE (the balanced DOF design): give H2 internal flexibility f by hanging the
  bridge-attachment vertices on flexible unit-distance appendages (one DOF each).
  Then pose-space dim = 3 + f. With b boundary vertices each on its own 1-DOF
  appendage, DOF = 3 + b and bridges = b: UNDER-determined by 3. A generic
  realization exists (a 3-parameter family), NOT a measure-zero coincidence.

  THE IRREDUCIBLE OBJECT (where the difficulty actually lives, not hidden in
  machinery): an appendage that is GEOMETRICALLY FLEXIBLE (its terminal-pair
  distance varies along a 1-parameter flex, so the bridge distance is tunable)
  yet COLOR-RIGID (its two terminals are forced to differ, or one terminal's
  color is clamped, in every proper 5-coloring). A unit path absorbs the color
  constraint (flexible but not color-rigid). A rhombus flexes but does not clamp.
  Whether ANY flexible UDG color-clamps its flexing terminals is OPEN and is the
  single kill-test for the entire program.

This module records the DOF accounting and the gadget tests as reproducible code
for VERIFIER / ADVERSARY.
"""

from __future__ import annotations

import json
import os

from pysat.formula import CNF
from pysat.solvers import Cadical195


def _kcol(n, edges, k, eqs=None):
    """k-colorability with optional equality/inequality terminal constraints.

    eqs: list of (u, v, same) where same=True forces c(u)==c(v).
    Returns True iff a proper k-coloring satisfying the constraints exists.
    """
    cnf = CNF()
    var = lambda v, c: v * k + c + 1
    for v in range(n):
        cnf.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            cnf.append([-var(u, c), -var(v, c)])
    for (u, v, same) in (eqs or []):
        if same:
            for c in range(k):
                cnf.append([-var(u, c), var(v, c)])
                cnf.append([var(u, c), -var(v, c)])
    s = Cadical195(bootstrap_with=cnf)
    r = s.solve()
    s.delete()
    return bool(r)


def color_clamps(n, edges, k, s, t):
    """Does the gadget force c(s) != c(t) in every proper k-coloring?

    True iff: the gadget is k-colorable AND forcing c(s)==c(t) is infeasible.
    This is the 'color-rigidity' property of a candidate appendage.
    """
    if not _kcol(n, edges, k):
        return None  # gadget not even k-colorable; ill-posed as an appendage
    same_feasible = _kcol(n, edges, k, eqs=[(s, t, True)])
    return not same_feasible


def appendage_dof_balance(b, appendage_internal_dof=1):
    """Balanced-design DOF accounting.

    b boundary vertices, each on its own appendage of internal DOF d.
    pose DOF = 3; total = 3 + b*d; bridge equations = b.
    Returns over-determination = bridges - total_dof (negative => realizable).
    """
    total = 3 + b * appendage_internal_dof
    return {"b": b, "bridges": b, "total_dof": total,
            "over_determination": b - total}


def run():
    results = {}

    # 1. The smallest flexible UDG (rhombus C4) does NOT color-clamp its
    #    opposite (flexing) terminals.
    c4 = [(0, 1), (1, 2), (2, 3), (3, 0)]
    results["rhombus_C4"] = {
        "flexible": True,  # 1 internal DOF; opposite-vertex distance varies
        "clamps_opposite_at_k5": color_clamps(4, c4, 5, 0, 2),  # expect False
    }

    # 2. The unit 3-path (a flexible linkage) does NOT force terminal colors.
    p3 = [(0, 1), (1, 2), (2, 3)]
    results["unit_path_3"] = {
        "flexible": True,  # 1 internal DOF when both ends pinned; reach (0,3)
        "clamps_ends_at_k5": color_clamps(4, p3, 5, 0, 3),  # expect False
    }

    # 3. The K4-fan (a rigid 'color clamp'): one vertex forced to the 5th color.
    #    This forces SAME color between two such vertices, NOT different.
    #    Recorded as the structural reason different-color forcing is the hard part.
    a = [1, 2, 3, 4]
    k4 = [(a[i], a[j]) for i in range(4) for j in range(i + 1, 4)]
    fan = k4 + [(0, x) for x in a]  # vertex 0 sees all of K4
    results["k4_fan"] = {
        "vertex0_5colorable": _kcol(5, fan, 5),
        "note": "vertex 0 forced to the complementary 5th color; SAME-color clamp",
    }

    # 4. Balanced DOF table.
    results["dof_balance"] = {
        str(b): appendage_dof_balance(b) for b in [3, 10, 100, 2000]
    }

    out = os.path.join(os.path.dirname(__file__), "_cache",
                       "rigidity_w3_escape.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    run()
