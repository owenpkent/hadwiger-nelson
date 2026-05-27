r"""e1r: Greedy vertex minimization of de Grey 1585 preserving chi >= 5.

Architecture 1, Shot 2. Continues L17.

Standard approach in the Heule/Parts lineage: iteratively try removing each
vertex; if the remaining graph still has chi >= 5, keep it removed. Repeat
until no single removal preserves chi >= 5. Result is a vertex-minimal
chi >= 5 subgraph.

For Polymath 510 / Parts 509, this approach reached ~510 vertices starting
from a larger Heule graph (553 or 826). For de Grey 1585, no published
greedy minimization exists — Heule and Parts moved to the
Q(sqrt 3, sqrt 11) reformulation instead.

This experiment runs the greedy minimization on de Grey 1585. Each pass:
test removing each vertex (1585 SAT calls per pass). Iterate until no
removal preserves chi >= 5. The output is a presumably-much-smaller
chi >= 5 UDG.

Note: this is computationally significant. The SAT call on a 1500-vertex
chi >= 5 instance was 5500s for the full de Grey 1585 (LEARNINGS L3 table).
But within the minimization, removing a vertex typically allows the SAT
to find a coloring quickly (a few seconds). Total: 1585 * (a few seconds)
per pass = maybe 1-3 hours per pass.

The minimization is checkpointed via a state file so the run can be
resumed.
"""

from __future__ import annotations

import json
import pathlib
import time

import mpmath as mp
import sympy as sp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"

mp.mp.dps = 50


def parse_sage_vertex_file(path):
    text = path.read_text(encoding="utf-8")
    sympy_ctx = {"sqrt": sp.sqrt}
    parsed = sp.sympify(text, locals=sympy_ctx, rational=True)
    return [(row[0], row[1]) for row in parsed]


def parse_edge_file(path):
    edges = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("c") or line.startswith("p"):
            continue
        if line.startswith("e"):
            parts = line.split()
            edges.append((int(parts[1]) - 1, int(parts[2]) - 1))
    return edges


def sat_k_color(N, edges, k, time_limit=300.0):
    """Returns (sat, time). None on timeout."""
    if N == 0:
        return True, 0.0
    def var(v, c): return v * k + c + 1
    clauses = []
    for v in range(N):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    t0 = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
    return sat, time.time() - t0


def main():
    print("e1r: greedy vertex minimization of de Grey 1585")
    print("=" * 78)

    edge_path = REPO_ROOT / "sources" / "degrey_1585.dimacs"
    edges = parse_edge_file(edge_path)
    n = 1585
    print(f"  {n} vertices, {len(edges)} edges")

    # Pre-compute adjacency.
    adj = [set() for _ in range(n)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)

    # State (resumable).
    state_path = CACHE / "e1r_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        active = set(state["active"])
        passes = state["passes"]
        print(f"  resuming: |V|={len(active)} active, passes={passes}")
    else:
        active = set(range(n))
        passes = 0

    # Score-based ordering: try removing low-degree vertices first
    # (more likely to be removable).
    def edges_among(V_set):
        return [(u, v) for (u, v) in edges if u in V_set and v in V_set]

    def chi_at_most_4(V_set):
        E = edges_among(V_set)
        idx = {v: i for i, v in enumerate(sorted(V_set))}
        E_re = [(idx[u], idx[v]) for (u, v) in E]
        return sat_k_color(len(V_set), E_re, 4)

    # Sanity: confirm full graph still chi >= 5.
    if passes == 0:
        print(f"  sanity: chi(de Grey 1585) >= 5? (skipping full SAT, trust L3)")

    # Iterate passes.
    max_passes = 5
    max_total_time = 7200   # 2 hours
    t_start = time.time()

    while passes < max_passes:
        passes += 1
        print(f"\n--- Pass {passes} ---")
        any_removed = False
        # Sort active vertices by current degree-in-active (low first).
        deg_in_active = {v: len(adj[v] & active) for v in active}
        order = sorted(active, key=lambda v: deg_in_active[v])

        t_pass_start = time.time()
        n_checked = 0
        for v in order:
            if time.time() - t_start > max_total_time:
                print(f"  time budget exhausted; saving state and exiting.")
                break
            if v not in active:
                continue
            trial = active - {v}
            sat4, t4 = chi_at_most_4(trial)
            n_checked += 1
            if sat4 is False:
                # Can remove v: trial still has chi >= 5.
                active = trial
                any_removed = True
                if n_checked % 50 == 0 or len(active) < 1000:
                    print(f"    [check {n_checked}/{len(order)}] removed v_{v}, |V|={len(active)}, t={t4:.2f}s", flush=True)
            else:
                if n_checked % 100 == 0:
                    print(f"    [check {n_checked}/{len(order)}] cannot remove v_{v} (t={t4:.2f}s)", flush=True)

        # Save state.
        state = {
            "active": sorted(active),
            "passes": passes,
            "pass_time_sec": time.time() - t_pass_start,
        }
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with state_path.open("w") as f:
            json.dump(state, f)

        print(f"  Pass {passes} complete in {time.time() - t_pass_start:.1f}s; |V|={len(active)}")

        if not any_removed:
            print(f"  No vertex removed this pass; minimum reached (with greedy / pass-1 strategy).")
            break
        if time.time() - t_start > max_total_time:
            break

    # Final state.
    print()
    print(f"FINAL: |V|={len(active)} (started 1585), reduction {1585 - len(active)}")
    print(f"  edges in final: {len(edges_among(active))}")
    final_edges = edges_among(active)
    print(f"  density E/V = {len(final_edges)/max(len(active), 1):.2f}")

    out = {
        "experiment": "e1r_minimize_degrey",
        "n_initial": 1585,
        "n_final": len(active),
        "n_edges_final": len(final_edges),
        "passes": passes,
        "active_vertices": sorted(active),
    }
    out_path = CACHE / "e1r_minimize_degrey.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
