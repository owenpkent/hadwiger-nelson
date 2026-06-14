r"""E15: the minimum order of a 6-chromatic graph in the UDG-necessary class.

The paper's "target object" is a 6-chromatic graph that is simultaneously
K4-free and K_{2,3}-free (the two LOCAL obstructions every planar unit-distance
graph must satisfy). Membership is necessary, not sufficient, for UDG
realizability, but the smallest such ABSTRACT graph is itself an open quantity:
the minimum order of a {K4, K_{2,3}}-free 6-chromatic graph is, as far as we
know, not recorded anywhere. (The K4-free-only minimum is the Folkman number 16;
adding K_{2,3}-freeness can only raise it. The codegree ceiling vs the
Kostochka-Yancey floor leaves the window open from n=13, and the Ramsey(4,4)
density argument pushes the plausible start to n approx 26.)

Method. For each order n we grow from the empty graph by adding edges that are
BOTH K4-safe and codegree-safe (codegree <= 2 keeps K_{2,3}-freeness), using the
chromatic_lifter machinery, until the graph is 5-UNSAT (a 6-chromatic in-class
witness) or no safe edge remains (greedy STUCK). Several random restarts per n.

The colorability decisions are made by OUR from-scratch solver (hn_solver), which
runs in-process (no SAT subprocess spawn) and is fast at this scale; this both
speeds the sweep and dogfoods the novel solver. Every witness is then
INDEPENDENTLY confirmed three ways: (1) explicit K4-free + K_{2,3}-free check,
(2) hn_solver says 5-UNSAT and 6-SAT, (3) the portfolio SAT backend agrees.

Honesty: a STUCK result at order n is NOT a proof that no in-class 6-chromatic
graph exists at n; greedy growth can paint itself into a corner. Positive
witnesses are rigorous; the smallest n with a witness is an UPPER BOUND on the
true minimum order.
"""
from __future__ import annotations
import sys
import pathlib
import json
import time
import random

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "_shared"))

from chromatic_lifter import (GraphState, UDG_NECESSARY, _model_pairs,  # noqa: E402
                              _hub_pairs, _take_allowed)
import hn_solver  # noqa: E402
from portfolio_sat import colorable_portfolio, solve_color  # noqa: E402  (L68)
from f1pt_lib import CACHE  # noqa: E402

OUT = CACHE / "e15_min_inclass_chi6"
OUT.mkdir(parents=True, exist_ok=True)

N_LO = 17
N_HI = 64
RESTARTS = 16
JUMP = 4            # small, deliberate growth: solves are instant at this scale
MODEL_SHARP = 2
EDGE_BUDGET = lambda n: n * n     # generous; codegree cap stops growth first
WALL_S = 900.0


def k4_free(state):
    for u in range(state.n):
        for v in state.adj[u]:
            if v > u:
                common = state.adj[u] & state.adj[v]
                for x in common:
                    if state.adj[x] & common:
                        return False
    return True


def k23_free(state):
    for u in range(state.n):
        for v in range(u + 1, state.n):
            if state.C[u][v] >= 3:
                return False
    return True


def grow_once(n, rng):
    """One restart: grow empty graph to 5-UNSAT (success) or STUCK, in-class."""
    state = GraphState(n, [])
    added = 0
    budget = EDGE_BUDGET(n)
    while added < budget:
        col = hn_solver.kcolor(n, state.edges(), 5, return_coloring=True)
        if col is False:
            return "success", state
        batch = _take_allowed(state, _model_pairs(col), UDG_NECESSARY, MODEL_SHARP)
        batch += _take_allowed(state, _hub_pairs(state, rng), UDG_NECESSARY,
                               JUMP - len(batch))
        if not batch:
            return "stuck", state
        added += len(batch)
    return "exhausted", state


def codeg_ceiling(n):
    return int(n * (1 + (8 * n - 7) ** 0.5) / 4)


def chromatic_at(state):
    """Smallest k in {2,3,4,5} that colors the (stuck) graph, else >=6."""
    for k in (2, 3, 4, 5):
        if hn_solver.kcolor(state.n, state.edges(), k):
            return k
    return 6


def confirm(state):
    """Triple confirmation of an in-class 6-chromatic witness, with a DRAT
    certificate of the 5-UNSAT (L68). The portfolio cross-checks use the
    symmetry-broken encoding (symbreak=True), the only one that decides in-class
    5-UNSAT at lineage scale tractably; the 5-UNSAT run emits a machine-checkable
    DRAT proof for a certificate-grade record of the target object."""
    edges = state.edges()
    n = state.n
    cert5 = solve_color(n, edges, 5, symbreak=True,
                        proof_path=str(OUT / "witness_5unsat.drat"))
    checks = {
        "k4_free": k4_free(state),
        "k23_free": k23_free(state),
        "hn_5_unsat": hn_solver.kcolor(n, edges, 5) is False,
        "hn_6_sat": hn_solver.kcolor(n, edges, 6) is True,
        "portfolio_5_unsat": cert5["result"] is False,
        "portfolio_6_sat": colorable_portfolio(n, edges, 6, symbreak=True)["result"] is True,
    }
    return all(checks.values()), checks, cert5


def main():
    t0 = time.time()
    results = []
    best = None
    for n in range(N_LO, N_HI + 1):
        if time.time() - t0 > WALL_S:
            print(f"wall budget hit at n={n}", flush=True)
            break
        outcome = {"n": n, "restarts": 0, "success": False}
        for r in range(RESTARTS):
            rng = random.Random(1000 * n + r)
            status, state = grow_once(n, rng)
            outcome["restarts"] = r + 1
            if status == "success":
                ok, checks, cert5 = confirm(state)
                outcome["success"] = ok
                outcome["m"] = len(state.edges())
                outcome["checks"] = checks
                if ok:
                    outcome["witness_edges"] = state.edges()
                    outcome["drat_proof"] = cert5["proof_path"]
                    outcome["drat_lines"] = cert5["proof_lines"]
                    print(f"n={n}: IN-CLASS 6-CHROMATIC WITNESS, m={outcome['m']}, "
                          f"restart {r}, confirmed={ok}, "
                          f"DRAT 5-UNSAT proof {cert5['proof_lines']} lines", flush=True)
                    if best is None:
                        best = {"n": n, "m": outcome["m"],
                                "edges": state.edges(),
                                "drat_proof": cert5["proof_path"]}
                        (OUT / "WITNESS_min.json").write_text(json.dumps(best, indent=1))
                else:
                    print(f"n={n}: success but confirm FAILED {checks}", flush=True)
                break
        if not outcome["success"]:
            print(f"n={n}: no in-class witness in {RESTARTS} restarts "
                  f"(greedy stuck/exhausted)", flush=True)
        results.append(outcome)
        if best is not None:
            break   # smallest n found; stop the sweep

    payload = {
        "range": [N_LO, N_HI], "restarts": RESTARTS,
        "min_order_found": best["n"] if best else None,
        "min_witness_m": best["m"] if best else None,
        "per_n": results, "elapsed_s": round(time.time() - t0, 1),
    }
    (OUT / "SUMMARY.json").write_text(json.dumps(payload, indent=1))
    if best:
        print(f"\nMIN IN-CLASS 6-CHROMATIC ORDER (upper bound): n={best['n']}, "
              f"m={best['m']}")
    else:
        print(f"\nno in-class 6-chromatic witness found in [{N_LO},{N_HI}] "
              f"by greedy ({RESTARTS} restarts each)")
    print(f"done in {payload['elapsed_s']} s")


if __name__ == "__main__":
    main()
