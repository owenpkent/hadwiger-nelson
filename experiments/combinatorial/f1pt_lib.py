r"""F1 pressure-test shared library.

Reusable P_510 loader (exact Q(sqrt3,sqrt11,sqrt5) coords), exact unit-distance
machinery, SAT k-coloring, and cocircularity tools. Standalone (caches absent in
clean clone), reconstructs everything from sources/cnp-sat/{vtx,edge}/510.*.
"""
from __future__ import annotations

import pathlib
import time

import sympy as sp

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
VTX = REPO_ROOT / "sources" / "cnp-sat" / "vtx"
EDGE = REPO_ROOT / "sources" / "cnp-sat" / "edge"


def parse_vtx(path: pathlib.Path):
    out = []
    for line in path.read_text().strip().splitlines():
        line = line.strip().strip("{}")
        a, b = [p.strip() for p in line.split(",")]
        def cv(s):
            return sp.sympify(s.replace("Sqrt[", "sqrt(").replace("]", ")"))
        out.append((cv(a), cv(b)))
    return out


def parse_edges(path: pathlib.Path):
    out = []
    for line in path.read_text().strip().splitlines():
        if line.startswith("e "):
            _, a, b = line.split()
            out.append((int(a) - 1, int(b) - 1))
    return out


def load_p510():
    base = parse_vtx(VTX / "510.vtx")
    edges = parse_edges(EDGE / "510.edge")
    return base, edges


def num_coords(coords, dps=40):
    import mpmath as mp
    mp.mp.dps = dps
    out = []
    for x, y in coords:
        out.append((mp.mpf(str(sp.N(x, dps))), mp.mpf(str(sp.N(y, dps)))))
    return out


def exact_dist2(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return sp.simplify(dx * dx + dy * dy)


def rot_apply(p, cos_t, sin_t):
    return (cos_t * p[0] - sin_t * p[1], sin_t * p[0] + cos_t * p[1])


def translate(p, t):
    return (p[0] + t[0], p[1] + t[1])


def build_copy(base, cos_t, sin_t, t):
    return [translate(rot_apply(p, cos_t, sin_t), t) for p in base]


def has_k4(n, edge_set):
    adj = [set() for _ in range(n)]
    for (u, v) in edge_set:
        adj[u].add(v)
        adj[v].add(u)
    for a in range(n):
        Na = adj[a]
        for b in Na:
            if b <= a:
                continue
            common_ab = Na & adj[b]
            for c in common_ab:
                if c <= b:
                    continue
                if adj[c] & common_ab:
                    for d in (adj[c] & common_ab):
                        if d > c:
                            return True
    return False


def max_clique_size(n, edge_set, cap=5):
    """Return min(clique number, cap+1-ish indicator). Cheap bounded check."""
    adj = [set() for _ in range(n)]
    for (u, v) in edge_set:
        adj[u].add(v)
        adj[v].add(u)
    best = 1 if n > 0 else 0
    # greedy bounded Bron-Kerbosch with pivot, capped
    import sys
    sys.setrecursionlimit(100000)
    found = [best]

    def expand(R, P):
        if not P:
            if R > found[0]:
                found[0] = R
            return
        if R >= cap + 1:
            found[0] = max(found[0], R)
            return
        Plist = list(P)
        for v in Plist:
            expand(R + 1, P & adj[v])
            P = P - {v}

    expand(0, set(range(n)))
    return found[0]


def sat_kcolor(n, edges, k, solver_cls, budget_conflicts=None, return_model=False):
    def var(v, c):
        return v * k + c + 1
    clauses = []
    for v in range(n):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    t0 = time.time()
    model = None
    s = solver_cls(bootstrap_with=clauses)
    try:
        if budget_conflicts is not None:
            s.conf_budget(budget_conflicts)
            res = s.solve_limited()
        else:
            res = s.solve()
        if res is True and return_model:
            m = s.get_model()
            mset = set(x for x in m if x > 0)
            coloring = []
            for v in range(n):
                cv = None
                for c in range(k):
                    if var(v, c) in mset:
                        cv = c
                        break
                coloring.append(cv)
            model = coloring
    finally:
        s.delete()
    dt = time.time() - t0
    if return_model:
        return res, dt, model
    return res, dt
