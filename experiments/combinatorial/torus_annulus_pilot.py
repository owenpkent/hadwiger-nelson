r"""BUILDER pilot: torus annulus-width scaling for k-colorings (upper-bound inversion).

Question. All human 6-coloring attempts are map-type (polygonal tiles) and those
need 7 colors (Voronov; repo kill-list). If chi(R^2) = 6, the 6-coloring is
non-map. This pilot measures WHERE 6-colorability dies as a function of the
forbidden-annulus width on exact-arithmetic torus discretizations.

Setup. Torus Z_n x Z_n with n = 3q (3x3 units, q cells per unit; 3 units is
enough that unit-scale distances do not wrap: 1 + w < 3/2). Forbid same color
on cell pairs whose squared torus distance D (integer!) satisfies
ceil((q-h)^2) <= D <= floor((q+h)^2), i.e. annulus half-width w = h/q around
distance 1. All thresholds are exact integers via Fraction; no floating point.

Predictions (pre-registered):
  P1 (Q^2 detector, visible in-experiment): at h = 0 the constraint graph is the
     exact rational-distance graph; chi is tiny (2-3, wrap triangles give 3).
     The climb to 5-7 happens ONLY as the annulus (topology of R) turns on.
  P2: k=7 is SAT up to a PLATEAU h* ~ 0.13 q (hex coloring capacity
     (1+w)/(1-w) < sqrt(7)/2), i.e. h* grows linearly with q.
  P3: k=6 is SAT only for h below a CELL-SCALE cutoff: h*_6(q) < sqrt(2) cells
     for every q (h >= sqrt(2) cells would give a genuine map-type 6-coloring
     of the plane, contradicting Voronov). If h*_6(q) stays bounded (in cells)
     while h*_7(q) grows linearly: the 6-vs-7 gap is exactly the map/non-map
     transition, and the witness colorings at the 6-threshold are the place to
     look for non-map structure (dust vs islands; component stats below).

A SAT result at k=6 with h >= 1.5 cells would be a candidate periodic
quasi-coloring of the plane and would demand immediate adversarial scrutiny.
"""
from __future__ import annotations
import sys, pathlib, json, time
from fractions import Fraction
from math import ceil, floor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import sat_kcolor
from pysat.solvers import Cadical195

CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
CACHE.mkdir(exist_ok=True)
OUT = CACHE / "torus_annulus_pilot.json"

BUDGET = 600_000  # conflicts per solve; None result = UNKNOWN

M_UNITS = 3
QS = [8, 12]
KS = [5, 6, 7]
HS = [Fraction(0), Fraction(1, 2), Fraction(1), Fraction(3, 2),
      Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2), Fraction(4)]


def window(q: int, h: Fraction):
    lo = (Fraction(q) - h) ** 2
    hi = (Fraction(q) + h) ** 2
    A = ceil(lo)  # Fraction supports __ceil__
    B = floor(hi)
    return A, B


def annulus_offsets(n: int, A: int, B: int):
    offs = []
    for a in range(n):
        da = min(a, n - a)
        for b in range(n):
            db = min(b, n - b)
            D = da * da + db * db
            if A <= D <= B:
                offs.append((a, b))
    return offs


def torus_edges(n: int, A: int, B: int):
    offs = annulus_offsets(n, A, B)
    edges = set()
    for i in range(n):
        for j in range(n):
            v = i * n + j
            for (a, b) in offs:
                u = ((i + a) % n) * n + (j + b) % n
                if u > v:
                    edges.add((v, u))
    return sorted(edges)


def component_stats(n: int, coloring, k: int):
    """4-adjacency connected components per color class: island vs dust probe."""
    stats = []
    for c in range(k):
        cells = set(v for v in range(n * n) if coloring[v] == c)
        seen, comps = set(), []
        for s in cells:
            if s in seen:
                continue
            stack, comp = [s], 0
            seen.add(s)
            while stack:
                v = stack.pop()
                comp += 1
                i, j = divmod(v, n)
                for (di, dj) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    u = ((i + di) % n) * n + (j + dj) % n
                    if u in cells and u not in seen:
                        seen.add(u)
                        stack.append(u)
            comps.append(comp)
        comps.sort(reverse=True)
        stats.append({"n_cells": len(cells), "n_components": len(comps),
                      "largest": comps[0] if comps else 0})
    return stats


def main():
    results = []
    for q in QS:
        n = M_UNITS * q
        for k in KS:
            prev_unsat = False
            for h in HS:
                if prev_unsat:
                    break
                A, B = window(q, h)
                edges = torus_edges(n, A, B)
                res, dt, model = sat_kcolor(n * n, edges, k, Cadical195,
                                            budget_conflicts=BUDGET, return_model=True)
                status = {True: "SAT", False: "UNSAT", None: "UNKNOWN"}[res]
                row = {"q": q, "n": n, "k": k, "h": str(h), "w": str(h / q),
                       "window": [A, B], "n_edges": len(edges),
                       "status": status, "time_s": round(dt, 1)}
                if res is True and model is not None:
                    row["component_stats"] = component_stats(n, model, k)
                    wf = CACHE / f"torus_annulus_witness_q{q}_k{k}_h{h.numerator}_{h.denominator}.json"
                    wf.write_text(json.dumps({"n": n, "k": k, "coloring": model}))
                results.append(row)
                print(f"q={q:2d} k={k} h={str(h):>4s} window=[{A},{B}] "
                      f"edges={len(edges):6d} -> {status:7s} ({dt:.1f}s)", flush=True)
                if res is False:
                    prev_unsat = True
        OUT.write_text(json.dumps(results, indent=1))
    print("saved", OUT)


if __name__ == "__main__":
    main()
