r"""E27: which DIRECTIONS carry the 5-chromaticity of de Grey's graph?

L83 measured the lineage's vector system: 78 distinct unit vectors across 23 angle
residues mod $60^\circ$, and killed the idea of finding such graphs by growing
balls (radius 8, so $\sim3.5\times10^{17}$ points against 1,585 actually used).
The constructions are sparse hand-assembly. So the question that matters becomes
structural: WHICH parts of the vector system are load-bearing?

THE EXPERIMENT. Group the 7,909 edges by the direction they use. Delete one
direction class at a time and ask whether $\chi \ge 5$ survives. A class whose
deletion drops the graph to 4-colorable is ESSENTIAL; one whose deletion changes
nothing is redundant scaffolding. The profile of essential classes is the binding
skeleton, and it is exactly what a NEW construction in a different field would
have to reproduce.

WHAT L18 PREDICTS, and why measuring it is still worth doing. L18 records that de
Grey's obstruction is "extremely delocalized: every reasonable structural
reduction drops chi to 4". If that is right, most or all classes are essential and
this experiment returns a uniform answer. That is a measurement rather than a
disappointment: "all 23 residue classes are individually essential" is a much
stronger and more quotable statement than "reductions tend to fail", and it tells
a would-be constructor that there is no small skeleton to copy.

Posed as an ASSAY experiment because it is genuinely an existence question per
unit: does a 5-chromatic obstruction still EXIST after deleting this class?

  control   deleting NOTHING must leave chi >= 5 (this is L3, the graph is
            5-chromatic). A pipeline that fails here is broken before it starts.
  ladder    both directions: deleting nothing -> YES; deleting EVERY edge -> NO
            (the empty graph is 1-colorable), so a tool that always answers YES
            cannot pass.
  probe     non-vacuity: the class must actually contain edges. Deleting an empty
            class trivially leaves chi >= 5, and counting that as "redundant"
            would be an artifact of a mis-grouped direction rather than a fact.
  verify    a surviving obstruction (YES) is re-verified by a second, independent
            solver configuration before it is believed.

Usage:
    python -m experiments.combinatorial.e27_direction_ablation --by residue
    python -m experiments.combinatorial.e27_direction_ablation --by vector
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import mpmath as mp                                            # noqa: E402
from assay.core import Experiment, Verdict, run, YES, NO       # noqa: E402

from e26_generator_census import (parse_sage_vertices, load_edges_dimacs,  # noqa: E402
                                  SOURCES)
from experiments._shared.portfolio_sat import solve_color      # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e27"


def load():
    pts = parse_sage_vertices(SOURCES / "degrey_1585_vertices.sage")
    edges = load_edges_dimacs(SOURCES / "degrey_1585.dimacs")
    return pts, edges


def classify(pts, edges, by="residue"):
    """Map each edge to its direction class."""
    groups = collections.defaultdict(list)
    for (i, j) in edges:
        dx = pts[i][0] - pts[j][0]
        dy = pts[i][1] - pts[j][1]
        if dy < 0 or (abs(dy) < mp.mpf("1e-25") and dx < 0):
            dx, dy = -dx, -dy
        if by == "vector":
            key = (mp.nstr(dx, 12), mp.nstr(dy, 12))
        else:
            ang = math.degrees(math.atan2(float(dy), float(dx))) % 60.0
            key = round(ang, 6)
            if abs(key - 60.0) < 1e-6 or abs(key) < 1e-6:
                key = 0.0
        groups[key].append((i, j))
    return groups


def chi_ge5(n, edges, symbreak=True):
    """True iff the graph is NOT 4-colorable."""
    if not edges:
        return False
    return not solve_color(n, list(edges), 4, symbreak=symbreak)["result"]


def build(by="residue") -> Experiment:
    pts, edges = load()
    n = len(pts)
    groups = classify(pts, edges, by=by)
    keys = sorted(groups, key=lambda k: -len(groups[k]))
    print(f"de Grey 1585: {len(edges)} edges in {len(groups)} {by} classes "
          f"(largest {len(groups[keys[0]])} edges, smallest "
          f"{len(groups[keys[-1]])})", flush=True)

    exp = Experiment(
        name=f"direction-ablation-{by}",
        question=("After deleting this direction class, does a 5-chromatic "
                  "obstruction still exist in de Grey's graph?"),
        scope=("Structural anatomy of ONE realized graph. It does not move any "
               "bound, and says nothing about whether a different construction "
               "could use fewer directions."),
    )

    @exp.control(name="intact_graph_is_5_chromatic",
                 note="L3: de Grey 1585 is UNSAT at k=4")
    def intact():
        return YES if chi_ge5(n, edges) else NO

    @exp.calibration(expect=NO, external=True, name="empty_graph_is_not",
                     note="deleting every edge must destroy the obstruction")
    def empty():
        return YES if chi_ge5(n, []) else NO

    @exp.calibration(expect=YES, external=True, name="intact_graph_rung",
                     note="the same known answer, as the YES direction")
    def intact_rung():
        return YES if chi_ge5(n, edges) else NO

    @exp.units
    def units():
        return keys

    @exp.work
    def work(key):
        kept = [e for k, g in groups.items() if k != key for e in g]
        survives = chi_ge5(n, kept)
        return Verdict(YES if survives else NO, key,
                       detail={"deleted_edges": len(groups[key]),
                               "kept_edges": len(kept)})

    @exp.probe
    def nonvacuous(key):
        return len(groups[key]) > 0

    @exp.verify
    def reverify(key, detail):
        """A surviving obstruction re-checked without symmetry breaking, so the
        confirmation does not share the search's configuration."""
        kept = [e for k, g in groups.items() if k != key for e in g]
        return chi_ge5(n, kept, symbreak=False)

    return exp


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--by", default="residue", choices=["residue", "vector"])
    args = ap.parse_args()
    mp.mp.dps = 40
    CACHE.mkdir(parents=True, exist_ok=True)
    exp = build(args.by)
    out = run(exp, ledger_path=CACHE / f"ablation_{args.by}.json",
              stop_on_hit=False)      # every class is interesting, not just one

    ess = [r for r in out["results"] if r["verdict"] == NO]
    red = [r for r in out["results"] if r["verdict"] == YES]
    print(f"\n{len(ess)} ESSENTIAL classes (deletion kills chi>=5), "
          f"{len(red)} redundant", flush=True)
    if red:
        print("  redundant classes (obstruction survives without them):", flush=True)
        for r in red[:10]:
            print(f"    {r['unit']}: {r['detail'].get('deleted_edges')} edges",
                  flush=True)
    summary = {"by": args.by, "essential": len(ess), "redundant": len(red),
               "results": out["results"]}
    (CACHE / f"summary_{args.by}.json").write_text(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
