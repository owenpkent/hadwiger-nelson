r"""h7b: Coordinate-first MULTI-COPY realizable coupling (Shot 2a, 3-way).

Follow-up to h7. h7 found every 2-copy realizable union of P_510 (rotated/
translated, exact unit-distance bridges only) is 5-colorable, EVEN at 4378
realizable bridges (rot60_t0), which exceeds the abstract L27 |B|=2700. So
realizable chi-6 forcing fails not from bridge SCARCITY but from bridge
STRUCTURE: the geometrically-determined cross-pairs respect a 5-coloring.

h7b tests the qualitatively-new 3-way coupling (Shot 2a) coordinate-first:
take copy0 = P_510, copy1 = rot(theta) P_510, copy2 = rot(2 theta) P_510 for
an in-field angle theta. All three copies live in one plane, so EVERY
cross-pair at exact distance 1 (between any two of the three copies) is a
genuine realizable bridge. SAT-check chi >= 6 on the union.

The orbit closes the union under a single rotation, maximizing realizable
cross-structure while staying a real UDG by construction (no cocircularity
obstruction: it IS an embedded plane graph).

Discipline: exact arithmetic, persist before SAT, dual-solver on any UNSAT,
budget the SAT, run detectors on the mechanism.
"""

from __future__ import annotations

import json
import pathlib
import time

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


def rot(p, c, s):
    return (c * p[0] - s * p[1], s * p[0] + c * p[1])


def _numlist(coords):
    return [(float(sp.N(p[0], 30)), float(sp.N(p[1], 30))) for p in coords]


def cross_unit(c1, c2, same, n1=None, n2=None):
    """Exact unit-distance pairs between coordinate lists c1, c2.

    Vectorized numeric prefilter (numpy) then exact sympy confirm. Precomputed
    numeric lists n1, n2 may be passed to avoid recomputation across pairs.
    """
    import numpy as np
    if n1 is None:
        n1 = _numlist(c1)
    if n2 is None:
        n2 = _numlist(c2)
    a = np.array(n1)
    b = np.array(n2)
    # pairwise squared distances via broadcasting
    diff = a[:, None, :] - b[None, :, :]
    d2 = (diff ** 2).sum(axis=2)
    ii, jj = np.where(np.abs(d2 - 1.0) < 1e-9)
    cand = [(int(i), int(j)) for i, j in zip(ii, jj) if (not same) or i < j]
    conf = []
    for (i, j) in cand:
        dx = c1[i][0] - c2[j][0]
        dy = c1[i][1] - c2[j][1]
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
    print("h7b: 3-way coordinate-first realizable coupling (orbit)")
    print("=" * 70)
    base = parse_vtx(VTX / "510.vtx")
    eb = parse_edges(EDGE / "510.edge")
    n = len(base)
    print(f"P_510: {n} vtx, {len(eb)} edges")

    sqrt3 = sp.sqrt(3)
    sqrt11 = sp.sqrt(11)

    # In-field angles that admit a closed/dense orbit. 60-deg gave the densest
    # 2-copy cross-set (4378). Use 60-deg orbit: copies at 0, 60, 120 deg.
    angles = [
        ("rot60_orbit3", sp.Rational(1, 2), sqrt3 / 2),
        ("rotMoser_orbit3", sp.Rational(5, 6), sqrt11 / 6),
    ]

    results = []
    for (tag, c, s) in angles:
        print(f"\n--- {tag}: building 3 copies at 0, theta, 2theta ---")
        copy0 = base
        copy1 = [rot(p, c, s) for p in base]
        # 2 theta via Chebyshev
        c2t = sp.simplify(c * c - s * s)
        s2t = sp.simplify(2 * s * c)
        copy2 = [rot(p, c2t, s2t) for p in base]

        # base internal edges in each copy
        edges = []
        for off in (0, n, 2 * n):
            edges += [(u + off, v + off) for (u, v) in eb]

        # cross bridges (genuine unit distances), all three pairs
        n0, n1_, n2_ = _numlist(copy0), _numlist(copy1), _numlist(copy2)
        b01 = cross_unit(copy0, copy1, same=False, n1=n0, n2=n1_)
        b02 = cross_unit(copy0, copy2, same=False, n1=n0, n2=n2_)
        b12 = cross_unit(copy1, copy2, same=False, n1=n1_, n2=n2_)
        edges += [(u, v + n) for (u, v) in b01]
        edges += [(u, v + 2 * n) for (u, v) in b02]
        edges += [(u + n, v + 2 * n) for (u, v) in b12]
        N = 3 * n
        nb = len(b01) + len(b02) + len(b12)
        print(f"  realizable bridges: 0-1={len(b01)}, 0-2={len(b02)}, 1-2={len(b12)}, total={nb}")

        # persist BEFORE SAT
        CACHE.mkdir(parents=True, exist_ok=True)
        gpath = CACHE / f"h7b_{tag}_graph.json"
        with gpath.open("w") as f:
            json.dump({"tag": tag, "N": N, "n": n,
                       "b01": b01, "b02": b02, "b12": b12,
                       "n_edges": len(edges)}, f)

        es = set((min(a, b), max(a, b)) for (a, b) in edges)
        k4 = has_k4(N, es)
        print(f"  N={N}, edges={len(edges)}, has_K4={k4}")

        res, tt = sat5(N, edges, Cadical195, budget=3_000_000)
        if res is True:
            verdict = "5-colorable (chi <= 5)"
        elif res is False:
            resb, ttb = sat5(N, edges, Glucose4, budget=30_000_000)
            gv = "UNSAT" if resb is False else ("SAT" if resb is True else "BUDGET")
            verdict = f"UNSAT cadical (chi >= 6 CANDIDATE); glucose={gv}"
        else:
            verdict = "SAT-intractable in budget (3M conflicts)"
        print(f"  5-color SAT: {verdict}  ({tt:.1f}s)")
        results.append({"tag": tag, "N": N, "n_bridges": nb,
                        "b01": len(b01), "b02": len(b02), "b12": len(b12),
                        "has_K4": k4, "verdict": verdict, "sat_time": tt,
                        "graph_path": str(gpath)})

    out = CACHE / "h7b_orbit_coupling.json"
    with out.open("w") as f:
        json.dump({"experiment": "h7b_orbit_coupling", "results": results}, f, indent=2)
    print(f"\narchived: {out}")
    print("\nSUMMARY")
    for r in results:
        print(f"  {r['tag']:<20} N={r['N']} bridges={r['n_bridges']:>5} K4={r['has_K4']}  {r['verdict']}")


if __name__ == "__main__":
    raise SystemExit(main())
