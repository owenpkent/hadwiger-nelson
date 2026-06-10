r"""Independent 4-pattern verification of one E1 alternator (no shared logic).

Builds M^3(C5) fresh, picks the first reported alternator (e1=(0,15),e2=(9,26)),
and checks all four eq/neq patterns explicitly via add-edge / merge encodings,
confirming: both-different UNSAT, both-same UNSAT, only-e1-same SAT, only-e2-same
SAT. That is the definition of an equality-alternator, verified without reusing
e9's contraction helper.
"""
from __future__ import annotations
import sys, pathlib
import networkx as nx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import sat_kcolor
from pysat.solvers import Cadical195


def myciel():
    g = nx.cycle_graph(5)
    for _ in range(3):
        g = nx.mycielskian(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    return g.number_of_nodes(), [(idx[u], idx[v]) for u, v in g.edges()]


def sat_with(n, edges, k, add=(), merge=()):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in merge:
        parent[find(a)] = find(b)
    es = set()
    for u, v in edges:
        uu, vv = find(u), find(v)
        if uu == vv:
            return False
        es.add((min(uu, vv), max(uu, vv)))
    for u, v in add:
        uu, vv = find(u), find(v)
        if uu == vv:
            return False
        es.add((min(uu, vv), max(uu, vv)))
    res, _ = sat_kcolor(n, list(es), k, Cadical195)
    return res


def main():
    n, edges = myciel()
    e1, e2 = (0, 15), (9, 26)
    base = [e for e in edges if tuple(sorted(e)) not in {e1, e2}]  # K - e1 - e2
    # patterns on K-e1-e2:
    both_diff = sat_with(n, base, 5, add=[e1, e2])            # == K, expect UNSAT
    both_same = sat_with(n, base, 5, merge=[e1, e2])          # expect UNSAT
    only_e1 = sat_with(n, base, 5, merge=[e1], add=[e2])      # == K-e1, expect SAT
    only_e2 = sat_with(n, base, 5, merge=[e2], add=[e1])      # == K-e2, expect SAT
    print(f"e1={e1} e2={e2}")
    print(f"  both-different (=K): {both_diff}  (expect False)")
    print(f"  both-same          : {both_same}  (expect False)")
    print(f"  only-e1-same (=K-e1): {only_e1}  (expect True)")
    print(f"  only-e2-same (=K-e2): {only_e2}  (expect True)")
    ok = (both_diff is False and both_same is False
          and only_e1 is True and only_e2 is True)
    print(f"VERIFIED EQUALITY-ALTERNATOR: {ok}")


if __name__ == "__main__":
    main()
