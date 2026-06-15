r"""Independent verification of the E16 repair-floor graph (FLOOR.json): recompute
codegree excess from scratch, check K4-freeness, and decide chi via the portfolio
(symmetry-broken), separate from the search's own hn_solver path."""
import json
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_shared"))
from portfolio_sat import colorable_portfolio


def main():
    f = json.load(open(HERE / "_cache" / "e16_topdown_repair" / "FLOOR.json"))
    n = f["n"]
    edges = [tuple(e) for e in f["edges"]]
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    C = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            C[u][v] = len(adj[u] & adj[v])
    excess = sum(max(0, C[u][v] - 2) for u in range(n) for v in range(u + 1, n))
    vpairs = sum(1 for u in range(n) for v in range(u + 1, n) if C[u][v] >= 3)
    maxcod = max(C[u][v] for u in range(n) for v in range(u + 1, n))

    k4 = False
    for u in range(n):
        for v in adj[u]:
            if v > u:
                common = adj[u] & adj[v]
                for x in common:
                    if adj[x] & common:
                        k4 = True

    # genuinely independent: the parallel portfolio (Maple + Cadical + Glucose)
    five = colorable_portfolio(n, edges, 5, symbreak=True)["result"]
    six = colorable_portfolio(n, edges, 6, symbreak=True)["result"]

    print("n=%d m=%d reported_excess=%d recomputed_excess=%d"
          % (n, len(edges), f["excess"], excess))
    print("violating_pairs=%d max_codegree=%d" % (vpairs, maxcod))
    print("K4_free=%s  5-colorable=%s (False=>chi>=6)  6-colorable=%s (True=>chi<=6)"
          % (not k4, five, six))
    print("chi==6: %s ; K4-free: %s ; K_{2,3}-free: %s"
          % (five is False and six is True, not k4, excess == 0))


if __name__ == "__main__":
    main()
