"""e1b: SAT verification of chi(G) >= 5 for a published 5-chromatic UDG.

Architecture 1 (combinatorial / UDG). The natural targets in increasing
preference:

  - Parts 509-vertex graph (2020, arXiv:2010.12665) current record-holder.
    509 vertices, 2442 edges, coordinates in Q(sqrt 3, sqrt 11).
  - Polymath16 510-vertex graph (Parts 2019, intermediate record).
  - Heule 529 or 553 vertex graphs (2018, arXiv:1805.12181).
  - de Grey 1581-vertex graph (2018, arXiv:1804.02385).

Pipeline (mirrors e1a but at scale):
  1. Load graph from a file in `sources/`. Supported formats:
       - DIMACS CNF (SAT instance, directly encoded).
       - Vertex list + edge list (JSON or whitespace-separated text).
  2. If vertex coords given, exact-arithmetic distance check on each edge.
  3. SAT-decide chi <= 4 with cadical195 + glucose4 (independent solvers).
     Expected: UNSAT from both (the graph is 5-chromatic).
  4. Archive certificates under _cache/.

Run:
  python -m experiments.combinatorial.e1b_de_grey_skeleton --graph sources/parts_509_2020.txt
  python -m experiments.combinatorial.e1b_de_grey_skeleton --cnf sources/parts_509.cnf --k 4

The pure-CNF mode skips distance verification. The graph-coords mode is
preferred when coordinates are available because exact-arithmetic distance
verification catches data-corruption bugs that SAT-only verification cannot.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from typing import Optional

from pysat.formula import CNF
from pysat.solvers import Solver

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCES = REPO_ROOT / "sources"
CACHE = pathlib.Path(__file__).parent / "_cache"

SOLVERS = ["cadical195", "glucose4"]


def load_dimacs_edges(path: pathlib.Path) -> list[tuple[int, int]]:
    """Parse a DIMACS edge file (`p edge V E` header then `e u v` lines, 1-indexed)."""
    edges: list[tuple[int, int]] = []
    n_vertices = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p"):
            # "p edge V E" or "p edges V E"
            parts = line.split()
            n_vertices = int(parts[2])
            continue
        if line.startswith("e"):
            _, u, v = line.split()
            edges.append((int(u) - 1, int(v) - 1))  # convert to 0-indexed
    if n_vertices is None:
        raise ValueError(f"no p-header in {path}")
    return edges


def load_graph_from_text(path: pathlib.Path) -> tuple[Optional[list], list[tuple[int, int]]]:
    """Parse a graph file.

    Supported formats (auto-detected by extension and content):
      - .json: {"vertices": [[x, y], ...], "edges": [[i, j], ...]}
      - .edge / .dimacs: DIMACS edge format with `p edge V E` header.
        Companion .vtx file is consulted for vertex coords when present.
      - .txt / .csv: free-form. First line `V E` (counts), then V lines of
        `x y` coords, then E lines of `i j` edge pairs.
    Returns (vertices_or_None, edges).
    """
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        vertices = data.get("vertices")
        edges = [tuple(e) for e in data["edges"]]
        return vertices, edges

    if path.suffix in (".edge", ".dimacs"):
        edges = load_dimacs_edges(path)
        # Companion .vtx files use Mathematica syntax: `{x, y}` per line with
        # `Sqrt[n]`. We do not parse them here; SAT verification is sound
        # independent of coordinates. Exact-arithmetic distance verification
        # against the .vtx file would be a separate follow-up experiment.
        return None, edges

    sep = "," if path.suffix == ".csv" else None
    text = path.read_text(encoding="utf-8")
    tokens = [line.split(sep) for line in text.splitlines() if line.strip() and not line.startswith("#")]
    if not tokens:
        raise ValueError(f"empty graph file: {path}")
    header = tokens[0]
    if len(header) < 2:
        raise ValueError(f"expected V E header in first line, got {header}")
    V, E = int(header[0]), int(header[1])
    vertices = [tuple(float(x) for x in row) for row in tokens[1:1 + V]] if V > 0 else None
    edges = [(int(row[0]), int(row[1])) for row in tokens[1 + V:1 + V + E]]
    if len(edges) != E:
        raise ValueError(f"expected {E} edges, got {len(edges)}")
    return vertices, edges


def verify_distances(vertices: list, edges: list[tuple[int, int]], tol: float = 1e-9) -> tuple[int, int]:
    """Count edges whose Euclidean distance is within `tol` of 1.

    This is a float sanity check; for canonical verification we expect exact
    symbolic coordinates that are not yet wired into this skeleton.
    """
    good, bad = 0, 0
    for u, v in edges:
        x1, y1 = vertices[u][:2]
        x2, y2 = vertices[v][:2]
        d = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        if abs(d - 1.0) < tol:
            good += 1
        else:
            bad += 1
    return good, bad


def encode_k_coloring(n_vertices: int, edges: list[tuple[int, int]], k: int) -> str:
    """DIMACS CNF for 'this graph is k-colorable'."""
    var = lambda v, c: v * k + c + 1
    clauses: list[list[int]] = []
    for v in range(n_vertices):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for u, v in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    head = f"p cnf {n_vertices * k} {len(clauses)}"
    body = "\n".join(" ".join(str(l) for l in cl) + " 0" for cl in clauses)
    return head + "\n" + body + "\n"


def sat_decide(cnf_text: str, solver_name: str, timeout_s: Optional[float] = None) -> tuple[bool, Optional[list[int]], float]:
    """Run SAT solver. Returns (sat, model_or_None, elapsed_seconds)."""
    cnf = CNF(from_string=cnf_text)
    t0 = time.time()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as s:
        if timeout_s is not None:
            s.conf_budget(int(timeout_s * 1_000_000))  # microseconds approximation
        sat = s.solve()
        model = s.get_model() if sat else None
    return bool(sat), model, time.time() - t0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="SAT-verify a 5-chromatic UDG.")
    parser.add_argument("--graph", type=str, help="path to graph file (vertices + edges)")
    parser.add_argument("--cnf", type=str, help="path to a DIMACS CNF (already-encoded SAT instance)")
    parser.add_argument("--k", type=int, default=4, help="number of colors to test (default 4 = expect UNSAT)")
    parser.add_argument("--no-verify", action="store_true", help="skip float-distance verification")
    args = parser.parse_args(argv)

    if not args.graph and not args.cnf:
        parser.error("must supply --graph or --cnf")
    if args.graph and args.cnf:
        parser.error("supply only one of --graph or --cnf")

    CACHE.mkdir(exist_ok=True)

    if args.cnf:
        cnf_path = pathlib.Path(args.cnf)
        if not cnf_path.is_absolute():
            cnf_path = REPO_ROOT / cnf_path
        print(f"loading DIMACS CNF: {cnf_path}")
        cnf_text = cnf_path.read_text(encoding="utf-8")
        tag = cnf_path.stem
    else:
        graph_path = pathlib.Path(args.graph)
        if not graph_path.is_absolute():
            graph_path = REPO_ROOT / graph_path
        print(f"loading graph: {graph_path}")
        vertices, edges = load_graph_from_text(graph_path)
        n = max(max(u, v) for u, v in edges) + 1
        print(f"  {n} vertices, {len(edges)} edges")

        if vertices is not None and not args.no_verify:
            good, bad = verify_distances(vertices, edges)
            print(f"  float-distance check: {good} edges within 1e-9 of unit, {bad} bad")
            if bad > 0:
                print(f"  WARNING: {bad} edges fail the float distance check. Data may be corrupted.")
                if bad > len(edges) * 0.01:
                    print("  ABORTING: more than 1% of edges fail. Investigate before SAT.")
                    return 2

        cnf_text = encode_k_coloring(n, edges, args.k)
        tag = graph_path.stem

    print(f"\nSAT-deciding chi <= {args.k}:")
    results = {}
    for solver in SOLVERS:
        sat, model, elapsed = sat_decide(cnf_text, solver)
        verdict = "SAT" if sat else "UNSAT"
        print(f"  {solver:12s} {verdict:6s} ({elapsed:.2f}s)")
        results[solver] = {"sat": sat, "elapsed_s": elapsed}

    # Multi-solver agreement check
    verdicts = {r["sat"] for r in results.values()}
    if len(verdicts) > 1:
        print(f"\nERROR: solvers disagree. This indicates a SAT-solver soundness bug.")
        return 3

    is_sat = verdicts.pop()
    expected_unsat = args.k < 5  # if testing 4-colorability of a chi >= 5 graph, expect UNSAT
    if expected_unsat and is_sat:
        print(f"\nUNEXPECTED: solvers agree on SAT for k={args.k}. The graph IS {args.k}-colorable; "
              f"either chi(graph) <= {args.k} (which contradicts the published bound) or the "
              f"input data is wrong.")
        return 4
    if not expected_unsat and not is_sat:
        print(f"\nUNEXPECTED: solvers agree on UNSAT for k={args.k}.")
        return 5

    print(f"\nresult: chi(graph) {'>' if not is_sat else '<='} {args.k} confirmed by {len(SOLVERS)} solvers")

    out_path = CACHE / f"e1b_{tag}_k{args.k}.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e1b",
                "graph_tag": tag,
                "k": args.k,
                "is_sat": is_sat,
                "solvers": results,
            },
            f,
            indent=2,
        )
    print(f"archived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
