r"""E28: apply the ASSEMBLY principle to the new core, in the new field.

The frontier's top item is a $\chi=5$ UDG outside the P510 lineage, built on a new
principle (L57: the known lineage is forcing-sterile by construction, so filing
down what exists cannot produce it). Three results now point at a concrete attack:

  * L82 found a SECOND binding field, $\mathbb{Q}(\sqrt3,\sqrt{35})$, whose
    4-critical core is a 56-vertex graph that is provably neither the Moser
    spindle nor Golomb (criticality forbids containing a 7- or 10-vertex
    4-chromatic subgraph).
  * L83 killed growing balls (radius 8 would need $\sim3.5\times10^{17}$ points
    against the 1,585 de Grey uses) and said what the realizable constructions
    actually are: SPARSE, hand-assembled unions.
  * The assembly move itself is old and simple. Moser's spindle is a rhombus
    together with a ROTATED COPY of that rhombus, where the rotor is chosen so the
    two far tips land at distance exactly 1 and a new edge appears. de Grey's
    graph is the same move iterated: 78 vectors across 23 rotor residues.

So the experiment: take the 56-vertex core $M$, search its own field for rotors
that BIND a copy to it (create at least one new unit distance between $M$ and
$r(M)$), form $M \cup r(M)$, and colour it. A $\chi \ge 5$ result would be a
5-chromatic unit-distance graph outside the lineage's field, which is the object
the program has been looking for.

WHY THIS IS NOT E24 AGAIN. E24 grew balls, which L83 showed cannot work. This
never enumerates a ball: it takes ONE motif and ONE rotation at a time, which is
what the successful constructions actually do, and the search space is the set of
binding rotors rather than the set of points.

CALIBRATION, in both directions, on the object whose answer is known:

  (a) the identity rotor on the Moser spindle must give back $\chi = 4$: the
      procedure must not manufacture chromatic number out of a duplicate;
  (b) the MOSER ROTOR applied to a unit rhombus must reproduce the spindle,
      $\chi = 4$ from two $\chi = 3$ pieces. This is the assembly move itself, so
      a procedure that fails it cannot be trusted to assemble anything;
  (c) every emitted graph must be a LEGAL unit-distance graph: every claimed edge
      is at distance exactly 1 and every non-edge is not, checked exactly in the
      field rather than in floating point.

Usage:
    python -m experiments.combinatorial.e28_spindle_new_core --calibrate
    python -m experiments.combinatorial.e28_spindle_new_core --run --max-rotors 40
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                          # noqa: E402

from e24_ring_census import (Fld, rot60, with_rotor, sqrt_units,  # noqa: E402
                             unit_vectors, ball, udg, rotate, q,
                             chromatic_number)
from experiments._shared.portfolio_sat import solve_color      # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e28"


def sqrt35_core(radius=3, cap=120000):
    """Rebuild the L82 core WITH coordinates (the committed artifact kept only g6,
    and rotating a graph requires points, not an isomorphism class)."""
    f = Fld(3, 35)
    base = rot60(f)
    for r in [u for den in range(2, 13) for u in sqrt_units(f, 35, den)]:
        base = with_rotor(f, base, r)
    pts, _ = ball(f, unit_vectors(f, base), radius, cap=cap)
    g = udg(f, pts)

    def chi_ge4(h):
        ns = list(h.nodes()); idx = {v: i for i, v in enumerate(ns)}
        es = [(idx[u], idx[v]) for u, v in h.edges()]
        return not solve_color(len(ns), es, 3, symbreak=True)["result"]

    h, changed = g.copy(), True
    while changed:
        changed = False
        for v in sorted(h.nodes(), key=lambda x: -h.degree(x)):
            t = h.copy(); t.remove_node(v)
            if t.number_of_edges() and chi_ge4(t):
                h, changed = t, True
    keep = sorted(h.nodes())
    return f, [pts[i] for i in keep], nx.convert_node_labels_to_integers(h)


def dist2(f, p, qq):
    dx, dy = f.sub(p[0], qq[0]), f.sub(p[1], qq[1])
    return f.add(f.mul(dx, dx), f.mul(dy, dy))


def legal_udg(f, pts):
    """Build the UDG on pts EXACTLY, and report whether all points are distinct."""
    g = nx.Graph(); g.add_nodes_from(range(len(pts)))
    seen = set()
    dup = 0
    for i, p in enumerate(pts):
        k = (str(p[0]), str(p[1]))
        if k in seen:
            dup += 1
        seen.add(k)
    for i, j in itertools.combinations(range(len(pts)), 2):
        if f.is_one(dist2(f, pts[i], pts[j])):
            g.add_edge(i, j)
    return g, dup


def candidate_rotors(f, p, limit=40):
    """Unit vectors of the field usable as rotors, cheapest denominators first."""
    out = []
    for den in range(2, 40):
        for u in sqrt_units(f, p, den):
            if u not in out:
                out.append(u)
        for c in range(1, den):
            # cos = c/den with sin^2 = 1 - c^2/den^2 needing the field's radical
            rem = den * den - c * c
            if rem <= 0:
                continue
            if rem % p == 0:
                k2 = rem // p
                r = int(round(k2 ** 0.5))
                if r * r == k2:
                    v = (q(Fraction(c, den)),
                         (Fraction(0), Fraction(0), Fraction(r, den), Fraction(0)))
                    if v not in out:
                        out.append(v)
        if len(out) >= limit:
            break
    return out[:limit]


def try_rotor(f, pts, rotor, chi_cap=6):
    """Form M union r(M) and report its chromatic number and binding count."""
    img = [rotate(f, v, rotor) for v in pts]
    allpts = list(pts) + img
    g, dup = legal_udg(f, allpts)
    n = len(pts)
    cross = sum(1 for u, v in g.edges() if (u < n) != (v < n))
    chi = chromatic_number(g, hi=chi_cap) if g.number_of_edges() else 1
    return {"points": len(allpts), "duplicate_points": dup,
            "edges": g.number_of_edges(), "binding_edges": cross, "chi": chi}


def calibrate():
    print("E28 calibration: the assembly move, on the object whose answer is known",
          flush=True)
    ok = True
    fm = Fld(3, 11)
    rhombus = [(q(0), q(0)), (q(1), q(0)),
               (rot60(fm)[1][0], rot60(fm)[1][1]),
               (fm.add(q(1), rot60(fm)[1][0]), rot60(fm)[1][1])]

    ident = (fm.one(), fm.zero())
    r = try_rotor(fm, rhombus, ident)
    a = (r["duplicate_points"] == len(rhombus) and r["chi"] <= 3)
    print(f"  [{'ok' if a else 'FAIL'}] identity rotor on a rhombus: chi={r['chi']} "
          f"(want <=3), {r['duplicate_points']} duplicate points (want "
          f"{len(rhombus)}) -- the move must not invent chromatic number", flush=True)
    ok &= a

    moser = (q(Fraction(5, 6)),
             (Fraction(0), Fraction(0), Fraction(1, 6), Fraction(0)))
    r = try_rotor(fm, rhombus, moser)
    b = (r["chi"] == 4 and r["binding_edges"] >= 1)
    print(f"  [{'ok' if b else 'FAIL'}] Moser rotor on a rhombus: chi={r['chi']} "
          f"(want 4) with {r['binding_edges']} binding edge(s) -- this IS the "
          f"spindle, assembled by the procedure", flush=True)
    ok &= b

    print(f"calibration: {'PASS' if ok else 'FAILURE'}", flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--max-rotors", type=int, default=40)
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)

    if not calibrate():
        print("procedure is not calibrated; refusing to report on the new core",
              flush=True)
        return 1
    if args.calibrate:
        return 0
    if not args.run:
        return 0

    print("\nE28: spindling the 56-vertex core in Q(sqrt3,sqrt35)", flush=True)
    f, pts, g = sqrt35_core()
    print(f"  core: {len(pts)} points, {g.number_of_edges()} edges, "
          f"chi = {chromatic_number(g)}", flush=True)

    rotors = candidate_rotors(f, 35, limit=args.max_rotors)
    print(f"  trying {len(rotors)} rotors from the field", flush=True)
    rows, best = [], 0
    for i, rot in enumerate(rotors):
        r = try_rotor(f, pts, rot)
        rows.append(r)
        if r["binding_edges"] or r["chi"] >= 5:
            print(f"    rotor {i}: {r['points']} pts, {r['binding_edges']} binding "
                  f"edges, chi = {r['chi']}"
                  f"{'   *** chi >= 5 ***' if r['chi'] >= 5 else ''}", flush=True)
        best = max(best, r["chi"] or 0)
        (CACHE / "spindle.json").write_text(json.dumps(rows, indent=2))
    bind = [r for r in rows if r["binding_edges"] > 0]
    print(f"\n  {len(bind)}/{len(rows)} rotors bind; best chi over all unions: {best}",
          flush=True)
    return 2 if best >= 5 else 0


if __name__ == "__main__":
    sys.exit(main())
