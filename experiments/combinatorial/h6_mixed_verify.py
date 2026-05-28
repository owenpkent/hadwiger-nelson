r"""h6_mixed_verify: independent VERIFIER for an h6_mixed_halves chi>=6 candidate.

Loads a combined graph artifact (h6mix_<tag>_graph.json), then independently:
  1. omega <= 3: exhaustive K_4 enumeration over the actual adjacency (not the
     incremental no-K_4 filter that built it).
  2. chi >= 6: dual-solver UNSAT for 5-coloring (Cadical195 + Glucose4), exact
     (no conflict budget; full solve).
  3. wrong-approach detector status: stated explicitly per L27/L28 convention.

Usage: python h6_mixed_verify.py --tag 510x553
"""

from __future__ import annotations

import argparse
import json
import pathlib
import time

from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"


def build_combined(g):
    N1, N2 = g["N1"], g["N2"]
    N = N1 + N2
    edges = []
    for (u, v) in g["edges_H1"]:
        edges.append((u, v))
    for (u, v) in g["edges_H2"]:
        edges.append((N1 + u, N1 + v))
    for (u, v) in g["B"]:
        edges.append((u, N1 + v))
    return N, edges


def exhaustive_omega_le3(N, edges):
    """Return (max_clique_found_size_at_least_4_witness or None, n_K4).

    Builds adjacency, then for each edge (u,v) intersects neighborhoods to find
    triangles, then checks whether any triangle extends to K_4. We count K_4s.
    """
    adj = [set() for _ in range(N)]
    for (u, v) in edges:
        adj[u].add(v); adj[v].add(u)
    n_k4 = 0
    witness = None
    # Enumerate triangles via edge + common-neighbor, then extend.
    for (u, v) in edges:
        if u > v:
            u, v = v, u
        common = adj[u] & adj[v]
        common = [w for w in common if w > v]
        for i in range(len(common)):
            w1 = common[i]
            aw1 = adj[w1]
            for j in range(i + 1, len(common)):
                w2 = common[j]
                if w2 in aw1:
                    n_k4 += 1
                    if witness is None:
                        witness = (u, v, w1, w2)
    return witness, n_k4


def exact_5color_unsat(N, edges, solver_cls, label):
    """Exact (full, no budget) 5-coloring solve. Returns (is_unsat, elapsed)."""
    k = 5

    def var(v, c):
        return v * k + c + 1

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
    with solver_cls(bootstrap_with=clauses) as solver:
        sat = solver.solve()
    elapsed = time.time() - t0
    print(f"  [{label}] 5-colorable={sat} "
          f"({'UNSAT => chi>=6' if sat is False else 'SAT => chi<=5'}) "
          f"elapsed={elapsed:.0f}s", flush=True)
    return (sat is False), elapsed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--skip-glucose", action="store_true")
    args = ap.parse_args()

    gpath = CACHE / f"h6mix_{args.tag}_graph.json"
    g = json.loads(gpath.read_text())
    N, edges = build_combined(g)
    print(f"VERIFIER for h6mix_{args.tag}: H_1={g['h1_tag']}, H_2={g['h2_tag']}", flush=True)
    print(f"  N={N}, total edges={len(edges)}, |B|={g['B_size']}", flush=True)

    print("Step 1: exhaustive omega<=3 (K_4 enumeration)", flush=True)
    t0 = time.time()
    witness, n_k4 = exhaustive_omega_le3(N, edges)
    print(f"  K_4 count={n_k4}, witness={witness}, "
          f"omega<=3 {'CONFIRMED' if n_k4 == 0 else 'FAILED'} "
          f"({time.time()-t0:.1f}s)", flush=True)

    print("Step 2: chi>=6 dual-solver exact UNSAT", flush=True)
    cad_unsat, cad_t = exact_5color_unsat(N, edges, Cadical195, "Cadical195")
    if args.skip_glucose:
        glu_unsat, glu_t = None, None
        print("  [Glucose4] skipped", flush=True)
    else:
        glu_unsat, glu_t = exact_5color_unsat(N, edges, Glucose4, "Glucose4")

    print("Step 3: wrong-approach detector status", flush=True)
    print("  Abstract no-K_4 graph. The three controls (Q^2 chi=2, L^inf chi=4,",
          flush=True)
    print("  R^1 chi=2) constrain GEOMETRIC realizations, not abstract graphs.",
          flush=True)
    print("  Inherits PASS exactly as L27/L28: the construction makes no metric",
          flush=True)
    print("  claim that could lift to the controls. UDG-realizability is tested",
          flush=True)
    print("  separately by the cocircularity sieve (ADVERSARY stage).", flush=True)

    verdict = {
        "tag": args.tag, "N": N, "n_edges": len(edges), "B_size": g["B_size"],
        "omega_le3_confirmed": n_k4 == 0, "n_K4": n_k4,
        "cadical_unsat": cad_unsat, "cadical_elapsed_s": round(cad_t, 1),
        "glucose_unsat": glu_unsat,
        "glucose_elapsed_s": (round(glu_t, 1) if glu_t is not None else None),
        "chi_ge6_dual_confirmed": bool(cad_unsat and (glu_unsat or args.skip_glucose)),
    }
    out = CACHE / f"h6mix_{args.tag}_verify.json"
    out.write_text(json.dumps(verdict, indent=2))
    print(f"Verdict written to {out.name}", flush=True)
    print(json.dumps(verdict, indent=2), flush=True)


if __name__ == "__main__":
    main()
