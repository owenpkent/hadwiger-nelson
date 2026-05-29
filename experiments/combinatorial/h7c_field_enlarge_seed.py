r"""h7c: Field-enlargement binding-rotation search on a chi-5 seed (Shot 2c).

The SAT-minimized Polymath field Q(sqrt 3, sqrt 11) is provably insufficient
(L11/L14: binding-rotation enumeration there plateaus at chi=4 / density 3.46).
This thrust enlarges the field: take a chi-5 SEED (Heule 553 or Parts 510,
exact coords in Q(sqrt 3, sqrt 11)) and form closed-under-rotation extensions
in the enlarged field K, then SAT-check each candidate for a 5-coloring REFUSAL.

A 5-coloring REFUSAL (UNSAT) on a verified UDG = a chi-6 UDG = the prize.

Method (coordinate-grounded, realizable by construction).
  1. Load the chi-5 seed S (exact coords).
  2. For each binding angle theta that maps a seed vertex to unit distance from
     another (the e1e mechanism), in an enlarged field (sqrt 7 / sqrt 19),
     form S' = R_theta(S). The union S cup S' is a genuine plane UDG; its only
     cross edges are exact unit distances (no cocircularity obstruction).
  3. SAT-check chi(S cup S') >= 6.

This differs from h7/h7b in that the SECOND copy's rotation angle is chosen to
be a BINDING angle (genuinely introducing a new field element), maximizing the
field-theoretic novelty rather than using an in-field 60-deg/Moser rotation.

Discipline: exact arithmetic, persist before SAT, dual-solver on UNSAT,
budget the SAT, run detectors.
"""

from __future__ import annotations

import json
import pathlib
import time

import numpy as np
import sympy as sp
from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
VTX = REPO_ROOT / "sources" / "cnp-sat" / "vtx"
EDGE = REPO_ROOT / "sources" / "cnp-sat" / "edge"


def parse_vtx(path):
    out = []
    for line in path.read_text().strip().splitlines():
        line = line.strip().strip("{}")
        a, b = [p.strip() for p in line.split(",")]
        cv = lambda s: sp.sympify(s.replace("Sqrt[", "sqrt(").replace("]", ")"))
        out.append((cv(a), cv(b)))
    return out


def parse_edges(path):
    out = []
    for line in path.read_text().strip().splitlines():
        if line.startswith("e "):
            _, a, b = line.split()
            out.append((int(a) - 1, int(b) - 1))
    return out


def numlist(coords):
    return [(float(sp.N(p[0], 30)), float(sp.N(p[1], 30))) for p in coords]


def cross_unit(c1, c2, n1, n2):
    a = np.array(n1); b = np.array(n2)
    diff = a[:, None, :] - b[None, :, :]
    d2 = (diff ** 2).sum(axis=2)
    ii, jj = np.where(np.abs(d2 - 1.0) < 1e-9)
    conf = []
    for i, j in zip(ii, jj):
        i, j = int(i), int(j)
        dx = c1[i][0] - c2[j][0]; dy = c1[i][1] - c2[j][1]
        if sp.simplify(dx * dx + dy * dy) == 1:
            conf.append((i, j))
    return conf


def has_k4(n, edge_set):
    adj = [set() for _ in range(n)]
    for (u, v) in edge_set:
        adj[u].add(v); adj[v].add(u)
    for a in range(n):
        for b in adj[a]:
            if b <= a:
                continue
            common = adj[a] & adj[b]
            for c in common:
                if c <= b:
                    continue
                if any(d > c for d in (adj[c] & common)):
                    return True
    return False


def sat5(n, edges, solver_cls, budget):
    var = lambda v, c: v * 5 + c + 1
    clauses = []
    for v in range(n):
        clauses.append([var(v, c) for c in range(5)])
        for c1 in range(5):
            for c2 in range(c1 + 1, 5):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(5):
            clauses.append([-var(u, c), -var(v, c)])
    t0 = time.time()
    with solver_cls(bootstrap_with=clauses) as s:
        if budget:
            s.conf_budget(budget)
            res = s.solve_limited()
        else:
            res = s.solve()
    return res, time.time() - t0


def main():
    print("h7c: field-enlargement binding-rotation on chi-5 seed (553)")
    print("=" * 70)
    base = parse_vtx(VTX / "553.vtx")
    eb = parse_edges(EDGE / "553.edge")
    n = len(base)
    nb = numlist(base)
    print(f"Heule 553: {n} vtx, {len(eb)} edges")

    sqrt3 = sp.sqrt(3); sqrt11 = sp.sqrt(11); sqrt7 = sp.sqrt(7); sqrt19 = sp.sqrt(19)

    # Field-enlarging rotation angles from the e1d family (cos=(2r^2-1)/2r^2):
    #   r^2=2 -> cos 3/4, sin sqrt7/4   (introduces sqrt 7)
    #   r^2=5 -> cos 9/10, sin sqrt19/10 (introduces sqrt 19)
    #   r^2=6 -> cos 11/12, sin sqrt23/12 (introduces sqrt 23)
    # Also a composite: Moser angle applied twice is in-field; instead use sqrt7.
    angles = [
        ("rotSqrt7", sp.Rational(3, 4), sqrt7 / 4),
        ("rotSqrt19", sp.Rational(9, 10), sqrt19 / 10),
        ("rotSqrt23", sp.Rational(11, 12), sp.sqrt(23) / 12),
        ("rotSqrt15", sp.Rational(7, 8), sp.sqrt(15) / 8),
    ]

    results = []
    for (tag, c, s) in angles:
        print(f"\n--- {tag}: cos={c}, sin={s} ---")
        copy2 = [(c * x - s * y, s * x + c * y) for (x, y) in base]
        n2 = numlist(copy2)
        br = cross_unit(base, copy2, nb, n2)
        edges = list(eb) + [(u + n, v + n) for (u, v) in eb] + [(u, v + n) for (u, v) in br]
        N = 2 * n
        print(f"  realizable bridges: {len(br)}")
        CACHE.mkdir(parents=True, exist_ok=True)
        gpath = CACHE / f"h7c_553_{tag}_graph.json"
        with gpath.open("w") as f:
            json.dump({"tag": tag, "N": N, "n": n, "bridges": br, "n_edges": len(edges)}, f)
        if len(br) == 0:
            print("  no realizable bridges; union is two disjoint chi-5 copies (chi=5). skip SAT.")
            results.append({"tag": tag, "N": N, "n_bridges": 0, "verdict": "no bridges"})
            continue
        es = set((min(a, b), max(a, b)) for (a, b) in edges)
        k4 = has_k4(N, es)
        res, tt = sat5(N, edges, Cadical195, budget=2_000_000)
        if res is True:
            verdict = "5-colorable (chi <= 5)"
        elif res is False:
            resb, _ = sat5(N, edges, Glucose4, budget=20_000_000)
            gv = "UNSAT" if resb is False else ("SAT" if resb is True else "BUDGET")
            verdict = f"UNSAT cadical (chi >= 6 CANDIDATE); glucose={gv}"
        else:
            verdict = "SAT-intractable in budget (2M conflicts)"
        print(f"  K4={k4}; 5-color SAT: {verdict} ({tt:.1f}s)")
        results.append({"tag": tag, "N": N, "n_bridges": len(br), "has_K4": k4,
                        "verdict": verdict, "sat_time": tt, "graph_path": str(gpath)})

    out = CACHE / "h7c_field_enlarge_seed.json"
    with out.open("w") as f:
        json.dump({"experiment": "h7c_field_enlarge_seed", "results": results}, f, indent=2)
    print(f"\narchived: {out}")
    print("\nSUMMARY")
    for r in results:
        print(f"  {r['tag']:<14} N={r.get('N')} bridges={r.get('n_bridges'):>4}  {r.get('verdict')}")


if __name__ == "__main__":
    raise SystemExit(main())
