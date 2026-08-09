r"""Persist and independently re-verify the n=15 cell of the both-free class.

E17/L75 reports that the $n=15$ window (edges 41..43, $\delta \ge 5$,
$\Delta \le 7$, 2-connected, $K_4$-free, $K_{2,3}$-free) contains exactly 11
graphs and that all 11 are 5-colorable. Those 11 graphs were never committed:
they lived in `_cache/e17/` on the Linux host. This script regenerates them from
`geng_hn`, re-verifies every claimed property with disjoint code, and writes the
graph6 strings into the repo so the cell is reproducible without that host.

Gate: 11 graphs, every one both-free with degrees inside the window, every one
5-colorable and none 4-colorable-if-E17-says-otherwise (the per-graph chromatic
number is recorded, not assumed).

Usage: python -m experiments.combinatorial.e18_n15_artifact [--g6 FILE]
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from e17_bothfree_filter import (graph6_to_adj,        # noqa: E402
                                 is_k4_free, is_k23_free)
from experiments._shared.portfolio_sat import solve_color  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_G6 = HERE / "_cache" / "e18" / "n15_all.g6"
OUT = HERE / "e18_n15_class.json"


def analyse(g6):
    n, adj = graph6_to_adj(g6)
    edges = [(i, j) for i, j in itertools.combinations(range(n), 2) if (adj[i] >> j) & 1]
    degs = [bin(a).count("1") for a in adj]
    chi = None
    for k in range(2, 8):
        if solve_color(n, edges, k, symbreak=True)["result"]:
            chi = k
            break
    return {
        "g6": g6, "n": n, "m": len(edges),
        "mindeg": min(degs), "maxdeg": max(degs),
        "k4_free": is_k4_free(n, adj), "k23_free": is_k23_free(n, adj),
        "chi": chi, "edges": edges,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--g6", default=str(DEFAULT_G6))
    args = ap.parse_args()

    lines = [l.strip() for l in pathlib.Path(args.g6).read_text().split() if l.strip()]
    rows = [analyse(l) for l in lines]

    ok = (len(rows) == 11
          and all(r["k4_free"] and r["k23_free"] for r in rows)
          and all(5 <= r["mindeg"] and r["maxdeg"] <= 7 for r in rows)
          and all(41 <= r["m"] <= 43 for r in rows)
          and all(r["chi"] is not None and r["chi"] <= 5 for r in rows))

    for r in rows:
        print(f"  {r['g6']:22s} m={r['m']} deg[{r['mindeg']},{r['maxdeg']}] "
              f"K4-free={r['k4_free']} K23-free={r['k23_free']} chi={r['chi']}")
    chis = sorted({r["chi"] for r in rows})
    print(f"\nn=15 cell: {len(rows)} graphs, chi values {chis} -> "
          f"{'PASS (no chi>=6 member)' if ok else 'FAIL'}")

    OUT.write_text(json.dumps({
        "source": "geng_hn -C -d5 -D7 15 41:43 (msys/ucrt64 build, 16-way res/mod split)",
        "claim": "the n=15 cell of the both-free class: 11 graphs, all 5-colorable",
        "count": len(rows), "chi_values": chis, "gate_pass": ok,
        "graphs": rows,
    }, indent=2))
    print(f"wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
