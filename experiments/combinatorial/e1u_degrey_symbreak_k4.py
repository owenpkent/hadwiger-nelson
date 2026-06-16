"""e1u: persist a symmetry-broken de Grey 1585 k=4 UNSAT certificate + timing.

Closes the C3-paper gap (adversary A1): the paper's flagship "de Grey 1585 k=4
UNSAT in 19.5 min" had no backing artifact, while the only persisted de Grey k=4
cache (e1b) recorded the NAIVE encoding at ~92 min (CaDiCaL). This script runs the
same decision under the color-permutation symmetry break (the encoding the C3
paper is about) and writes the measured time, so the headline number is backed by
a real cached run on this machine.

Loads the edge graph `sources/degrey_1585.dimacs`, runs
`solve_color(symbreak=True, solver="Cadical195")` at k=4 (expect UNSAT =>
chi(deGrey) >= 5 => chi(R^2) >= 5), and archives the timing under _cache/.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "_shared"))

from portfolio_sat import solve_color  # noqa: E402

GRAPH = REPO_ROOT / "sources" / "degrey_1585.dimacs"
CACHE = pathlib.Path(__file__).parent / "_cache"
OUT = CACHE / "e1u_degrey_1585_symbreak_k4.json"


def load_edges(path: pathlib.Path) -> tuple[int, list[tuple[int, int]]]:
    n = None
    edges: list[tuple[int, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p"):
            n = int(line.split()[2])
            continue
        if line.startswith("e"):
            _, u, v = line.split()
            edges.append((int(u) - 1, int(v) - 1))  # 0-indexed
    if n is None:
        raise ValueError(f"no p-header in {path}")
    return n, edges


def main() -> int:
    CACHE.mkdir(exist_ok=True)
    n, edges = load_edges(GRAPH)
    print(f"de Grey: {n} vertices, {len(edges)} edges", flush=True)
    print("solving k=4 with symmetry break (Cadical195), unbounded ...", flush=True)
    t0 = time.time()
    res = solve_color(n, edges, 4, symbreak=True, solver="Cadical195")
    wall = time.time() - t0

    record = {
        "experiment": "e1u",
        "graph": "degrey_1585",
        "k": 4,
        "encoding": res["encoding"],
        "solver": "Cadical195",
        "result_sat": res["result"],          # expect False (UNSAT)
        "is_unsat": res["result"] is False,
        "elapsed_s": round(res["elapsed"], 2),
        "elapsed_min": round(res["elapsed"] / 60.0, 2),
        "wall_s": round(wall, 2),
        "clique_size": len(res["clique"]),
        "n_vertices": n,
        "n_edges": len(edges),
        "naive_reference_s": 5531.07,         # e1b cadical195 naive, for contrast
    }
    with OUT.open("w") as f:
        json.dump(record, f, indent=2)
    verdict = {False: "UNSAT (chi>=5)", True: "SAT", None: "BUDGET"}[res["result"]]
    print(f"verdict: {verdict} in {record['elapsed_min']} min "
          f"(symbreak); naive ref ~92.2 min", flush=True)
    print(f"archived: {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
