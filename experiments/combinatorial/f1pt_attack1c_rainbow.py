r"""F1 pressure-test, Attack 1c: try to BREAK F1 by rainbow-forcing 5 cocircular
points in a genuine unit-distance graph.

Reduced lemma (L): F1's geometric core is exactly:
  Can 5 points cocircular at radius 1 be RAINBOW-FORCED in a UDG (every proper
  5-coloring assigns them 5 distinct colors)?

If YES + the forcing structure realizes, the hub on that circle has |F(hub)|=5
under every coloring -> the L22/L24 chi-6 obstruction is realizable -> potential
chi-6 UDG (a BREAK of F1). If NO, we pin the obstruction.

Attack strategy: take the densest available cocircular-at-unit structure that EXISTS
as a UDG and is rich enough to rainbow-force. We use the hub's own unit circle and
populate it AND its exterior with Moser-spindle / triangular-lattice unit-distance
structure to attempt rainbow forcing of a chosen cocircular 5-set, all in
Q(sqrt3) (the hexagonal/triangular lattice field, exact).

We build the triangular lattice patch (all unit distances exact in Q(sqrt3)),
identify a maximal cocircular-at-unit subset, and SAT-test rainbow-forcing of
its 5-subsets. The triangular lattice is the natural habitat: it has unit
distances in abundance and contains hexagons (cocircular-at-unit 6-sets).
"""
from __future__ import annotations
import sys, pathlib, json, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
import mpmath as mp
from f1pt_lib import exact_dist2, sat_kcolor, has_k4, CACHE
from pysat.solvers import Cadical195

mp.mp.dps = 40


def tri_lattice(R):
    """Triangular lattice points within radius R (exact, Q(sqrt3)). Unit nearest-neighbor."""
    s3 = sp.sqrt(3)
    pts = []
    rng = range(-R-1, R+2)
    for a in rng:
        for b in rng:
            x = sp.Integer(a) + sp.Rational(1, 2) * b
            y = s3 / 2 * b
            # numeric radius filter
            if float(sp.N(x*x + y*y)) <= (R + 0.01)**2:
                pts.append((sp.nsimplify(x), sp.nsimplify(y)))
    return pts


def unit_edges(pts):
    n = len(pts)
    # numeric prefilter
    npts = [(float(sp.N(x)), float(sp.N(y))) for (x, y) in pts]
    edges = []
    for i in range(n):
        xi, yi = npts[i]
        for j in range(i+1, n):
            xj, yj = npts[j]
            d2 = (xi-xj)**2 + (yi-yj)**2
            if abs(d2 - 1.0) < 1e-9:
                if exact_dist2(pts[i], pts[j]) == 1:
                    edges.append((i, j))
    return edges


def cocircular_unit_sets(pts):
    """For each lattice point c, the set of OTHER points at exact unit distance
    (its unit-circle neighborhood = a cocircular-at-unit set). Return centers
    with >=5 neighbors."""
    npts = [(float(sp.N(x)), float(sp.N(y))) for (x, y) in pts]
    from collections import defaultdict
    nbr = defaultdict(list)
    n = len(pts)
    for i in range(n):
        xi, yi = npts[i]
        for j in range(n):
            if i == j:
                continue
            xj, yj = npts[j]
            if abs((xi-xj)**2 + (yi-yj)**2 - 1.0) < 1e-9:
                if exact_dist2(pts[i], pts[j]) == 1:
                    nbr[i].append(j)
    return {c: sorted(s) for c, s in nbr.items() if len(s) >= 5}


def rainbow_forced(n, edges, S, k=5):
    """Is S (a set of vertices) rainbow-forced: every proper k-coloring gives S
    |S| distinct colors? Equivalently no proper k-coloring makes any two in S
    equal. Test all pairs: merge and check UNSAT."""
    eset = set((min(u,v),max(u,v)) for (u,v) in edges)
    for (a, b) in itertools.combinations(sorted(S), 2):
        def rep(x): return a if x == b else x
        merged = set()
        for (u, v) in eset:
            uu, vv = rep(u), rep(v)
            if uu != vv:
                merged.add((min(uu,vv), max(uu,vv)))
        res, _ = sat_kcolor(n, list(merged), k, Cadical195)
        if res is True:
            return False, (a, b)
    return True, None


def main():
    out = {}
    for R in (3, 4):
        pts = tri_lattice(R)
        edges = unit_edges(pts)
        n = len(pts)
        cocirc = cocircular_unit_sets(pts)
        print(f"R={R}: {n} lattice pts, {len(edges)} unit edges, "
              f"{len(cocirc)} centers with >=5 cocircular-unit neighbors")
        # chi of the lattice patch (should be 3, triangular lattice is 3-chromatic)
        # find a center with a big cocircular set and test rainbow-forcing of 5-subsets
        best_center = max(cocirc, key=lambda c: len(cocirc[c])) if cocirc else None
        rec = {"R": R, "n": n, "edges": len(edges),
               "n_centers_ge5": len(cocirc)}
        if best_center is not None:
            U = cocirc[best_center]
            rec["best_center"] = best_center
            rec["cocirc_set_size"] = len(U)
            # try several 5-subsets; report if ANY is rainbow-forced
            found_forced = False
            tried = 0
            for S in itertools.combinations(U, 5):
                tried += 1
                if tried > 30:
                    break
                forced, witness = rainbow_forced(n, edges, S, k=5)
                if forced:
                    found_forced = True
                    rec["rainbow_forced_5set"] = list(S)
                    break
            rec["any_5subset_rainbow_forced"] = found_forced
            rec["subsets_tried"] = tried
            print(f"  best cocircular set size {len(U)} at center {best_center}; "
                  f"rainbow-forced 5-subset found: {found_forced}")
        out[f"R{R}"] = rec

    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "f1pt_attack1c_rainbow.json").write_text(json.dumps(out, indent=2, default=str))
    print("saved", CACHE / "f1pt_attack1c_rainbow.json")

if __name__ == "__main__":
    main()
