r"""h6_mixed_decisive_sat: decoupled, UNCAPPED decisive 5-coloring SAT on a
persisted h6_mixed_halves checkpoint graph.

Why this exists. The in-loop Stage-D SAT inside h6_mixed_halves.py uses a
conflict-budget proxy (sat_time_limit * 50000 conflicts) that can either return
None (budget exhausted, looks like a hang) or run a very long time. The L29
510x517 run was KILLED mid-SAT at |B| = 1800 with no verdict and no persisted
bridge set. This driver decouples the decisive solve from the fragile
greedy/adversary loop: it loads the checkpointed combined graph and runs a
single TRUE (uncapped, no conflict budget) Cadical solve, writing the DIMACS
first so a future session can hand the exact instance to kissat / cryptominisat
if Cadical itself proves intractable in budget.

On UNSAT (chi >= 6): re-confirm with Glucose4 per the L27/L28 dual-solver
standard.

Usage:
  python h6_mixed_decisive_sat.py --tag 510x517
  python h6_mixed_decisive_sat.py --tag 510x517 --skip-glucose   (Cadical only)

The Cadical solve is uncapped; this script is meant to be run in the background
and left to complete (potentially hours). It checkpoints nothing further: the
graph and DIMACS are the durable artifacts.
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
    edges = []
    for (u, v) in g["edges_H1"]:
        edges.append((u, v))
    for (u, v) in g["edges_H2"]:
        edges.append((N1 + u, N1 + v))
    for (u, v) in g["B"]:
        edges.append((u, N1 + v))
    return N1 + N2, edges


def k_color_clauses(N, edges, k=5):
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
    return clauses


def write_dimacs(path, n_vars, clauses):
    with path.open("w", encoding="utf-8") as f:
        f.write(f"p cnf {n_vars} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")


def solve_uncapped(clauses, solver_cls, label):
    t0 = time.time()
    with solver_cls(bootstrap_with=clauses) as solver:
        sat = solver.solve()  # NO conf_budget: a true, complete solve
    elapsed = time.time() - t0
    verdict = ("UNSAT => chi>=6" if sat is False
               else "SAT => chi<=5" if sat is True else "INDETERMINATE")
    print(f"  [{label}] 5-colorable={sat} ({verdict}) elapsed={elapsed:.1f}s",
          flush=True)
    return sat, elapsed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--skip-glucose", action="store_true")
    args = ap.parse_args()

    gpath = CACHE / f"h6mix_{args.tag}_graph.json"
    g = json.loads(gpath.read_text())
    N, edges = build_combined(g)
    print(f"DECISIVE SAT for h6mix_{args.tag}: N={N}, |E|={len(edges)}, "
          f"|B|={g['B_size']}", flush=True)

    k = 5
    n_vars = N * k
    clauses = k_color_clauses(N, edges, k)
    dimacs = CACHE / f"h6mix_{args.tag}_decisive.cnf"
    write_dimacs(dimacs, n_vars, clauses)
    print(f"  wrote DIMACS ({n_vars} vars, {len(clauses)} clauses) to "
          f"{dimacs.name}", flush=True)

    print("Cadical195 uncapped solve (this may take a long time)...", flush=True)
    cad_sat, cad_t = solve_uncapped(clauses, Cadical195, "Cadical195")

    glu_sat, glu_t = None, None
    if cad_sat is False and not args.skip_glucose:
        print("Cadical UNSAT; re-confirming with Glucose4 (dual-solver standard)...",
              flush=True)
        glu_sat, glu_t = solve_uncapped(clauses, Glucose4, "Glucose4")

    if cad_sat is False:
        verdict = "CHI_6_CONFIRMED"
    elif cad_sat is True:
        verdict = "CHI_LE_5_below_threshold"
    else:
        verdict = "SAT_INTRACTABLE_IN_BUDGET"

    out = {
        "tag": args.tag, "N": N, "n_edges": len(edges), "B_size": g["B_size"],
        "n_colorings_at_checkpoint": g.get("n_colorings_at_checkpoint"),
        "cadical_sat": cad_sat, "cadical_elapsed_s": round(cad_t, 1),
        "glucose_sat": glu_sat,
        "glucose_elapsed_s": (round(glu_t, 1) if glu_t is not None else None),
        "verdict": verdict,
        "dimacs": dimacs.name,
    }
    opath = CACHE / f"h6mix_{args.tag}_decisive.json"
    opath.write_text(json.dumps(out, indent=2))
    print(f"\nVERDICT: {verdict}  (|B|={g['B_size']})", flush=True)
    print(f"written to {opath.name}", flush=True)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
