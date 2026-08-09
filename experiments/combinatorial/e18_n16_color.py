r"""Color the SAT-enumerated n=16 cell: the second half of an end-to-end
independent replication of the E17/L75 verdict.

E17's claim at $n=16$ has two halves. The census half ("the window contains
exactly 11,315 both-free graphs") is re-derived by `e18_enumerate`, which finds
them with CDCL + blocking clauses instead of canonical augmentation. This script
does the verdict half: every one of those graphs is 5-colorable, so the class has
no $\chi \ge 6$ member at $n = 16$.

Note honestly what is and is not independent here. The enumeration is independent
of geng. The coloring is *not* independent of E17's coloring in method -- both use
DSATUR first and a SAT portfolio for the residue -- but it is run on a separately
derived graph set, so a graph that E17's enumeration missed and that happened to
be 6-chromatic would show up here.

Any graph that DSATUR cannot 5-color goes to the portfolio, and any graph the
portfolio reports UNSAT at $k=5$ is a HIT: a $K_4$-free, $K_{2,3}$-free graph with
$\chi \ge 6$, which is the object E17 was hunting. Hits are written out
separately and loudly.

Usage: python -m experiments.combinatorial.e18_n16_color
"""
from __future__ import annotations

import argparse
import glob
import itertools
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                       # noqa: E402

from e17_bothfree_filter import (graph6_to_adj,             # noqa: E402
                                 is_k4_free, is_k23_free)
from experiments._shared.portfolio_sat import solve_color   # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e18"


def load_sat_graphs():
    out = []
    for p in sorted(glob.glob(str(CACHE / "enum_n16_m*.json"))):
        d = json.loads(pathlib.Path(p).read_text())
        if not d.get("exhausted"):
            print(f"  WARNING: {pathlib.Path(p).name} hit its budget -- partial cell")
        out.extend(d.get("g6", []))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--g6", default=None, help="a .g6 file instead of the enum JSONs")
    ap.add_argument("--out", default=str(CACHE / "n16_coloring.json"))
    args = ap.parse_args()

    if args.g6:
        g6s = [l.strip() for l in pathlib.Path(args.g6).read_text().split() if l.strip()]
    else:
        g6s = load_sat_graphs()
    print(f"coloring {len(g6s)} graphs from the n=16 cell")

    hist, hits, residue = {}, [], 0
    t0 = time.time()
    for idx, g6 in enumerate(g6s):
        n, adj = graph6_to_adj(g6)
        edges = [(i, j) for i, j in itertools.combinations(range(n), 2)
                 if (adj[i] >> j) & 1]
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)

        # Property re-check with disjoint code: a graph that is not in the class
        # has no business being counted in this verdict.
        degs = [bin(a).count("1") for a in adj]
        if not (is_k4_free(n, adj) and is_k23_free(n, adj)
                and min(degs) >= 5 and max(degs) <= 7):
            print(f"  PROPERTY VIOLATION at {g6}")
            return 2

        greedy = max(nx.coloring.greedy_color(g, strategy="DSATUR").values()) + 1
        if greedy <= 5:
            chi_le5 = True
        else:
            residue += 1
            chi_le5 = bool(solve_color(n, edges, 5, symbreak=True)["result"])
        if not chi_le5:
            hits.append(g6)
            print(f"  *** HIT: {g6} is NOT 5-colorable (chi >= 6) ***")
        key = "chi<=5" if chi_le5 else "chi>=6"
        hist[key] = hist.get(key, 0) + 1
        if (idx + 1) % 2000 == 0:
            print(f"    {idx + 1}/{len(g6s)}  {time.time() - t0:.0f}s  "
                  f"(DSATUR residue so far: {residue})", flush=True)

    elapsed = round(time.time() - t0, 1)
    print(f"\nn=16 cell: {len(g6s)} graphs, {hist}, "
          f"{residue} needed SAT beyond DSATUR, {elapsed}s")
    verdict = "PASS: no chi>=6 member at n=16" if not hits else "HIT FOUND"
    print(f"VERDICT: {verdict}")

    pathlib.Path(args.out).write_text(json.dumps({
        "source": "e18 SAT enumeration of the n=16 window",
        "count": len(g6s), "histogram": hist, "dsatur_residue": residue,
        "hits": hits, "elapsed_s": elapsed, "no_chi6": not hits,
    }, indent=2))
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
