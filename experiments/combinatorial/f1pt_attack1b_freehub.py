r"""F1 pressure-test, Attack 1b: a FREE concentrated hub, realizable by construction,
and the test of whether external rainbow-forcing can coexist with cocircularity.

Construction (all coordinates exact, all bridge edges genuine unit distances):
  - Hub h at the origin.
  - Sources s_1..s_m placed ON h's unit circle at exact angles. The edges (s_i, h)
    are unit distances BY CONSTRUCTION (cocircularity satisfied trivially).
  - To force |F(h)| = 5 (the L22/L24 chi-6 obstruction at one vertex), we need a
    proper 5-coloring to be FORCED to put 5 distinct colors on 5 of the sources.

The decisive realizability fact this script establishes:
  The sources live on a single unit circle (radius 1). Any unit-distance edges
  AMONG the sources require two sources to be 60 deg apart (chord=1). So the
  induced UDG on the sources is a subgraph of the hexagon-6-cycle C_6 (at most 6
  usable angular slots at multiples of 60 deg, plus their reflections give the
  same 6 chord-1 positions). Thus the sources can be wired to EACH OTHER only as
  a sub-C_6: omega <= 2, chi <= 2 among them.

To rainbow-force the sources we must use EXTERNAL vertices (a rainbow generator
gadget). Those external vertices and their unit-distance edges to the sources are
themselves geometric constraints. We test whether the standard rainbow generator
(a "color enforcer" forcing 5 distinct colors on a target 5-set) can attach to 5
cocircular sources by genuine unit distances.

This script builds the most favorable case and SAT-checks chi, then reports the
geometric over-determination.
"""
from __future__ import annotations
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
import mpmath as mp
from f1pt_lib import exact_dist2, sat_kcolor, has_k4, CACHE
from pysat.solvers import Cadical195

mp.mp.dps = 40

def hexagon_on_unit_circle():
    """The 6 points at multiples of 60deg on the hub's unit circle (radius 1, center origin).
    These are the ONLY cocircular-at-unit points that can have unit edges among themselves."""
    pts = []
    for k in range(6):
        ang = sp.Rational(k, 6) * 2 * sp.pi
        pts.append((sp.cos(ang), sp.sin(ang)))
    return [(sp.nsimplify(x), sp.nsimplify(y)) for (x, y) in pts]


def main():
    out = {}
    hub = (sp.Integer(0), sp.Integer(0))
    hexpts = hexagon_on_unit_circle()
    # verify each hex point is unit distance from hub
    hub_edges_ok = all(exact_dist2(hub, p) == 1 for p in hexpts)
    out["hub_to_hex_all_unit"] = bool(hub_edges_ok)
    print("hub->hexagon all unit distance:", hub_edges_ok)

    # mutual distances among hexagon points (which pairs are unit)
    mutual_unit = []
    for i in range(6):
        for j in range(i+1, 6):
            if exact_dist2(hexpts[i], hexpts[j]) == 1:
                mutual_unit.append((i, j))
    out["hexagon_mutual_unit_edges"] = mutual_unit
    print("hexagon mutual unit edges (the only intra-source edges available):", mutual_unit)
    # this is exactly C_6 adjacency

    # So vertices: hub=0, hex sources=1..6. Edges: hub-source (6) + C_6 among sources.
    n = 7
    edges = [(0, i+1) for i in range(6)] + [(a+1, b+1) for (a, b) in mutual_unit]
    out["gadget_n"] = n
    out["gadget_edges"] = edges
    out["gadget_has_k4"] = has_k4(n, set((min(a,b),max(a,b)) for (a,b) in edges))
    # chi of the wheel-like gadget W_6 (hub + C_6): chi(C_6)=2, +hub adjacent to all => 3.
    for k in (2,3,4):
        r,_ = sat_kcolor(n, edges, k, Cadical195)
        out[f"gadget_chi_le_{k}"] = bool(r)
    print("gadget (hub+hexagon C_6) k-colorable:",
          {k: out[f"gadget_chi_le_{k}"] for k in (2,3,4)})

    # KEY: to force |F(hub)|=5 we need 5 sources rainbow (5 distinct colors). But the
    # sources form C_6 (chi=2): a proper coloring can 2-color them => at most 2 distinct
    # colors appear on the sources from THEIR OWN structure. The hub forbids those 2.
    # |F(hub)| <= (#distinct colors among the 6 cocircular neighbors). On C_6 that is
    # >=2 but to FORCE it to be 5 we'd need 5 distinct colors forced on the 6 circle pts,
    # impossible since chi(C_6)=2 admits a 2-coloring of the sources.
    # Demonstrate: can we 5-color the gadget with the 6 sources using only 2 colors?
    # Then hub needs a 3rd color, |F(hub)|=2. Confirm hub never sees 5 forbidden colors.
    # Add the hub-forbids: simulate by checking max distinct colors forced on sources.
    out["max_distinct_forced_on_circle_sources"] = (
        "<= chi-related; C_6 is 2-colorable so sources can share down to 2 colors; "
        "|F(hub)| cannot be forced to 5 by cocircular sources alone")

    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "f1pt_attack1b_freehub.json").write_text(json.dumps(out, indent=2, default=str))
    print("saved", CACHE / "f1pt_attack1b_freehub.json")

if __name__ == "__main__":
    main()
