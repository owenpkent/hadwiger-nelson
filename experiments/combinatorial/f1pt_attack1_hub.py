r"""F1 pressure-test, Attack 1: coordinate-first CONCENTRATED hub gadget.

The L34/F1 negative is specific to RIGID whole-graph orbits (which spread
bridges). The task's sharp objection: concentration at a single hub is
geometrically FREE -- any points on v's unit circle are unit-distance from v.

So we build hubs BY CONSTRUCTION:
  - Take H_1 = P_510 (chi 5) with its exact coords fixed.
  - A "hub" h is a NEW vertex placed in the plane. We then choose 5 bridge
    partners in H_1 to bridge into h. For the bridge edges (partner, h) to be
    unit distances, h must lie at the common intersection... no: h must be at
    distance 1 from EACH partner, i.e. the 5 partners must be cocircular at
    radius 1 with center h. We CANNOT choose 5 arbitrary partners and a center;
    cocircularity-at-unit-radius is the constraint.

  The free move the task highlights: forget about reusing P_510 partners.
  Instead place the hub h anywhere, then place 5 BRAND-NEW vertices on h's unit
  circle (trivially cocircular at radius 1). Those 5 new vertices are the bridge
  sources. For them to FORCE |F(h)| = 5 (the L22/L24 obstruction), they must be
  rainbow-forced: every proper 5-coloring of the structure must color them with
  5 DISTINCT colors. New free-floating vertices are NOT forced to anything; they
  must be wired into a chi-5-rigid sub-structure to be rainbow-forced. THAT
  wiring is itself a UDG and re-imposes unit-distance constraints among the 5
  sources and the rest. This script tests whether the wiring + cocircularity can
  coexist.

Concretely we test the SIMPLEST possible chi-6 mechanism and probe its
realizability obstruction precisely:

  GADGET G(h): a hub h plus a "rainbow generator" R that forces 5 distinct
  colors on a designated 5-set S, with S placed cocircularly at unit radius
  around h. If a single G(h) plus copies tile to chi>=6 AND realizes, that's a
  break. We test realizability of the rainbow generator under the cocircularity
  constraint on S.
"""
from __future__ import annotations
import sys, pathlib, json, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
from f1pt_lib import (load_p510, exact_dist2, sat_kcolor, has_k4, CACHE)
from pysat.solvers import Cadical195, Glucose4


def rainbow_forced_5set_exists(n, edges, k=5):
    """Does there exist a 5-set S such that EVERY proper k-coloring assigns S
    five DISTINCT colors? Equivalently S is a 'rainbow-forced' independent-ish
    set. We test via SAT: is it possible to k-color with two vertices of S equal?
    If for SOME pair in S a monochromatic assignment is satisfiable, S is NOT
    rainbow-forced. A rainbow-forced S needs: for all i<j in S, the graph + edge
    (s_i,s_j) is still k-colorable is FALSE... no. Rainbow-forced means: adding
    'merge s_i,s_j' (force equal) makes it UNSAT for every pair. We test that.
    """
    # This is expensive in general; provided as a checker, not enumerator.
    raise NotImplementedError


def analyze_rainbow_in_p510():
    """KEY QUESTION: does P_510 contain ANY 5 vertices that are (a) cocircular at
    unit radius AND (b) rainbow-forced (every proper 5-coloring gives them 5
    distinct colors)?

    (a) Max cocircular-unit subset of P_510 is 36 (Attack 3A), and it is exactly
        the unit-circle neighborhood of a vertex w (w's 36 neighbors). So the
        candidate cocircular 5-sets are 5-subsets of some vertex w's neighbor set.
    (b) Rainbow-forced: under a proper 5-coloring, can 5 mutual-... they all lie
        on w's circle and are all adjacent to w, but are they adjacent to EACH
        OTHER? If they pairwise are NOT edges, a 5-coloring can repeat colors
        among them => NOT rainbow forced. To be rainbow forced they'd need to be
        a K_5 (forces 5 distinct) but omega(P_510)=3, so NO 5-clique exists.

    This is the crux. We verify omega(P_510) <= 3 and that the cocircular 36-set
    (a vertex's neighborhood) has small internal clique number.
    """
    base, edges = load_p510()
    n = len(base)
    eset = set((min(u,v),max(u,v)) for (u,v) in edges)
    from collections import defaultdict
    adj = defaultdict(set)
    for (u,v) in eset:
        adj[u].add(v); adj[v].add(u)

    # omega check (bounded)
    k4 = has_k4(n, eset)
    print(f"P_510 has_K4: {k4}")

    # The max cocircular-unit set = neighborhood of vertex 0 (36 pts). Internal
    # edges among those 36 (they all lie on vertex 0's unit circle).
    members = json.loads((CACHE / "f1pt_attack3_cocirc.json").read_text())["best_members"]
    members = set(members)
    internal = [(u,v) for (u,v) in eset if u in members and v in members]
    print(f"Cocircular 36-set internal edges: {len(internal)}")
    # max clique within the 36-set
    from f1pt_lib import max_clique_size
    sub_idx = sorted(members)
    remap = {v:i for i,v in enumerate(sub_idx)}
    sub_edges = [(remap[u],remap[v]) for (u,v) in internal]
    w = max_clique_size(len(sub_idx), sub_edges, cap=5)
    print(f"Max clique within cocircular 36-set: {w}")

    # Rainbow-forcing requires either a K_5 among the cocircular 5 sources (omega>=5,
    # impossible since omega=3) OR a list-coloring obstruction that FORCES 5 distinct
    # colors on the 5 sources via the SURROUNDING graph. Test: take the 5 highest-degree
    # cocircular points; is there a proper 5-coloring of P_510 making two of them equal?
    cocirc_list = sorted(members, key=lambda v: -len(adj[v]))
    test5 = cocirc_list[:5]
    print(f"Testing cocircular 5-set S={test5} for rainbow-forcing under 5-coloring...")
    forced = True
    for (a,b) in itertools.combinations(test5, 2):
        # force a,b same color: merge by adding clause structure. Easiest: add
        # constraint c(a)=c(b) via extra clauses (a==b iff for each color, x_a,c <-> x_b,c)
        # Instead use SAT with merged variable: build edges with a identified to b.
        merged_edges = []
        def rep(x): return a if x==b else x
        for (u,v) in eset:
            uu,vv = rep(u), rep(v)
            if uu!=vv:
                merged_edges.append((min(uu,vv),max(uu,vv)))
        merged_edges = list(set(merged_edges))
        # vertices: same n, b now isolated/unused but harmless
        res,_ = sat_kcolor(n, merged_edges, 5, Cadical195)
        if res is True:
            forced = False
            print(f"  pair ({a},{b}) CAN be monochromatic in a proper 5-coloring => S NOT rainbow-forced")
            break
    if forced:
        print(f"  S IS rainbow-forced (no pair can be monochromatic)")
    return {"has_k4": k4, "cocirc_internal_edges": len(internal),
            "cocirc_max_clique": w, "test5": test5, "rainbow_forced": forced}


if __name__ == "__main__":
    out = analyze_rainbow_in_p510()
    (CACHE / "f1pt_attack1_hub.json").write_text(json.dumps(out, indent=2))
    print("saved", CACHE / "f1pt_attack1_hub.json")
