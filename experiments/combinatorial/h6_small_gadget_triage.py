r"""h6_small_gadget_triage: chi + omega of the sub-510 corpus gadgets.

Direction B sub-direction 3: triple-coupling can only beat 1020 vertices if a
chi-5 no-K_4 gadget with < 340 vertices exists (3 x 340 = 1020). The corpus has
three graphs smaller than the 510-lineage halves that have not been characterized
in this context: S199 (199 vtx), L403 (403 vtx), T721 (721 vtx).

For each: chi = smallest k with k-coloring SAT, and omega via exhaustive K_4/K_5.
The decisive question: is any chi-5, no-K_4 gadget < 340 vertices?
"""

from __future__ import annotations

import pathlib
import sys
import time

from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "combinatorial"))
from h6_bridge_minimum import k_color_clauses, omega_leq_3  # noqa: E402

EDGE_DIR = REPO_ROOT / "sources" / "cnp-sat" / "edge"


def parse_edge(path):
    n = None
    edges = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("p"):
            n = int(line.split()[2])
        elif line.startswith("e"):
            p = line.split()
            edges.append((int(p[1]) - 1, int(p[2]) - 1))
    return n, edges


def k_colorable(n, edges, k, budget_s=120):
    clauses, _ = k_color_clauses(n, edges, k)
    s = Cadical195(bootstrap_with=clauses)
    try:
        s.conf_budget(int(budget_s * 25000))
        res = s.solve_limited(expect_interrupt=False)
    finally:
        s.delete()
    return res


def has_K(n, edges, ksize):
    """Exhaustive clique-of-size-ksize search (ksize in {4,5})."""
    adj = [set() for _ in range(n)]
    for (u, v) in edges:
        adj[u].add(v); adj[v].add(u)
    if ksize == 4:
        hasK4, wit = omega_leq_3(n, edges)
        return hasK4
    # ksize == 5: extend K_4 witnesses; cheap brute over triangles+2
    for u in range(n):
        nu = sorted(x for x in adj[u] if x > u)
        for i in range(len(nu)):
            v = nu[i]
            for j in range(i + 1, len(nu)):
                w = nu[j]
                if w not in adj[v]:
                    continue
                common = sorted(x for x in (adj[u] & adj[v] & adj[w]) if x > w)
                for a_i in range(len(common)):
                    x = common[a_i]
                    for b_i in range(a_i + 1, len(common)):
                        y = common[b_i]
                        if y in adj[x]:
                            return True
    return False


def chi_via_sat(n, edges):
    """Smallest k (2..7) with k-coloring SAT. Returns (chi, timings)."""
    timings = {}
    for k in range(2, 8):
        t0 = time.time()
        res = k_colorable(n, edges, k)
        timings[k] = (res, time.time() - t0)
        if res is True:
            return k, timings
        if res is None:
            return None, timings
    return None, timings


def main():
    for name in ["S199", "L403", "T721"]:
        path = EDGE_DIR / f"{name}.edge"
        n, edges = parse_edge(path)
        print(f"\n=== {name}: {n} vertices, {len(edges)} edges ===", flush=True)
        t0 = time.time()
        k4 = has_K(n, edges, 4)
        print(f"  K_4 present: {k4}  (omega {'>= 4' if k4 else '<= 3'})  "
              f"[{time.time()-t0:.1f}s]", flush=True)
        if k4:
            k5 = has_K(n, edges, 5)
            print(f"  K_5 present: {k5}", flush=True)
        chi, timings = chi_via_sat(n, edges)
        for k, (res, el) in timings.items():
            v = {True: "SAT", False: "UNSAT", None: "BUDGET"}[res]
            print(f"  {k}-color: {v} [{el:.2f}s]", flush=True)
        print(f"  chi = {chi}", flush=True)
        verdict = ("CANDIDATE (chi-5 no-K_4 < 340)"
                   if (chi == 5 and not k4 and n < 340)
                   else "not a sub-340 chi-5 no-K_4 gadget")
        print(f"  >>> {verdict}", flush=True)


if __name__ == "__main__":
    main()
