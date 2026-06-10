r"""E1: abstract Equality-Alternator existence (L58 phase-gadget route gate).

The phase-gadget dichotomy (L58) needs an interface gadget whose 5-colorings
carry a Z/p phase. The minimal target (p=2) is the EQUALITY-ALTERNATOR: a graph
with two non-adjacent pairs (a1,a2),(b1,b2) such that EVERY proper 5-coloring
satisfies exactly one of c(a1)=c(a2) and c(b1)=c(b2). No single pair is forced,
so it is provably invisible to L45/L56/L57.

Construction insight (adversary result_14, corrected): take K = M^3(C5), the
47-vertex triangle-free 6-CRITICAL graph (L51's H). For a 6-critical graph,
removing an edge e=(u,v) forces u,v to the SAME color in every proper 5-coloring
(else that coloring would 5-color K, impossible). So in K - e1 - e2:
  - both-different (a1!=a2 AND b1!=b2) is ALWAYS infeasible: such a coloring
    properly colors K itself (both removed edges satisfied), but chi(K)=6.
  - only-e1-same and only-e2-same are ALWAYS feasible (they are just K-e1, K-e2,
    each 5-colorable by criticality).
  - both-same (a1=a2 AND b1=b2) is the ONLY question. If it is 5-UNSAT, then
    every coloring has exactly one pair same: an alternator. SELF-CERTIFYING.

So the gate is: over independent edge pairs (e1,e2) of M^3(C5) (4 distinct
endpoints), contract a1=a2 and b1=b2 in K-e1-e2 and 5-SAT. Any UNSAT is an
abstract Z/2 alternator and the first object for the phase-gadget route.
A clean negative bounds the minimal alternator below M^3(C5)'s edge structure
and redirects to wider interfaces / different 6-critical hosts.
"""
from __future__ import annotations
import sys, pathlib, json, itertools, time
import networkx as nx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import sat_kcolor, CACHE
from pysat.solvers import Cadical195

OUT = CACHE / "e9_alternator"
OUT.mkdir(parents=True, exist_ok=True)


def mycielski_tower():
    """C5 -> M -> M -> M: triangle-free 6-critical, 47 vertices (L51's H)."""
    g = nx.cycle_graph(5)
    g = nx.mycielskian(g)   # Grotzsch, 4-critical, 11 v
    g = nx.mycielskian(g)   # 5-critical, 23 v
    g = nx.mycielskian(g)   # 6-critical, 47 v
    idx = {v: i for i, v in enumerate(g.nodes())}
    edges = [(idx[u], idx[v]) for u, v in g.edges()]
    n = g.number_of_nodes()
    return n, edges


def color_after_contractions(n, edges, drop, merges):
    """5-SAT of (edges minus `drop`) with each pair in `merges` contracted.
    Returns True/False/None (None = budget exceeded)."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b) in merges:
        parent[find(a)] = find(b)
    dropset = {(min(u, v), max(u, v)) for (u, v) in drop}
    merged = set()
    for (u, v) in edges:
        if (min(u, v), max(u, v)) in dropset:
            continue
        uu, vv = find(u), find(v)
        if uu == vv:
            return False  # a surviving edge collapsed onto itself => self-loop => 5-UNSAT
        merged.add((min(uu, vv), max(uu, vv)))
    res, _ = sat_kcolor(n, list(merged), 5, Cadical195, budget_conflicts=2_000_000)
    return res


def main():
    n, edges = mycielski_tower()
    eset = [(min(u, v), max(u, v)) for (u, v) in edges]
    print(f"M^3(C5): n={n}, edges={len(eset)}", flush=True)

    # Sanity controls (self-certifying logic, but verify the host).
    res_k, _ = sat_kcolor(n, eset, 5, Cadical195, budget_conflicts=2_000_000)
    res_k6, _ = sat_kcolor(n, eset, 6, Cadical195, budget_conflicts=2_000_000)
    print(f"control: chi(K) 5-SAT={res_k} (expect False), 6-SAT={res_k6} (expect True)", flush=True)
    assert res_k is False and res_k6 is True, "host is not 6-chromatic; abort"

    # Independent edge pairs: 4 distinct endpoints, and the two 'same' pairs
    # (a1,a2),(b1,b2) must be NON-ADJACENT in K (else 'same' is trivially UNSAT
    # and uninteresting). a1,a2 ARE adjacent in K (they form edge e1); we contract
    # them, which is fine. Non-adjacency we need is between the merge reps, handled
    # by the contraction logic. Independence = e1,e2 share no vertex.
    pairs = []
    m = len(eset)
    for i in range(m):
        a1, a2 = eset[i]
        for j in range(i + 1, m):
            b1, b2 = eset[j]
            if len({a1, a2, b1, b2}) == 4:
                pairs.append((i, j))
    print(f"independent edge pairs: {len(pairs)}", flush=True)

    hits = []
    t0 = time.time()
    ck = OUT / "progress.json"
    for idx, (i, j) in enumerate(pairs):
        e1, e2 = eset[i], eset[j]
        res = color_after_contractions(n, eset, drop=[e1, e2],
                                       merges=[(e1[0], e1[1]), (e2[0], e2[1])])
        if res is False:
            hits.append({"e1": e1, "e2": e2})
            print(f"!!! ALTERNATOR: e1={e1} e2={e2} (both-same 5-UNSAT)", flush=True)
        elif res is None:
            print(f"  indeterminate e1={e1} e2={e2}", flush=True)
        if idx % 500 == 0:
            ck.write_text(json.dumps({"done": idx, "total": len(pairs),
                                      "hits": len(hits), "secs": round(time.time() - t0, 1)}))
            print(f"{idx}/{len(pairs)} hits={len(hits)} ({time.time() - t0:.0f}s)", flush=True)

    result = {"host": "M^3(C5)", "n": n, "edges": len(eset),
              "pairs_tested": len(pairs), "alternators": len(hits),
              "hits": hits[:50], "secs": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    print("DONE", json.dumps({k: v for k, v in result.items() if k != "hits"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
