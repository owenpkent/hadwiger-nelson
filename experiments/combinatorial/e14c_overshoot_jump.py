r"""E14c: aggressive-jump overshoot. Skip the threshold instead of walking it.

E14b's walker added a few model-guided edges then solved EVERY step. Near the
SAT/UNSAT boundary each solve costs hours (the 524-edge solve ran 2 h of CPU),
because the hard region is a narrow band AROUND the threshold. Solves on either
side -- comfortably colorable, or comfortably overconstrained -- are fast.

E14c exploits that: JUMP past the band with free (no-solve) blind safe edges,
then solve once.
  - add blind K4-safe + codegree-safe edges (codegree-2 preferred: each closes
    two triangles, the densest local constraint and the UDG-flavored substrate)
    until the edge count hits the next target or no safe edge remains (STUCK);
  - solve once with MapleChrono (budgeted):
      UNSAT  -> SUCCESS: a 6-chromatic graph in the UDG-necessary class.
                Cross-check with Glucose42, persist witness + DIMACS.
      SAT    -> we under-shot; the model is FAST here (past the band), so use it
                to place a few sharp model-guided edges, raise the target, repeat.
      INDET  -> raise budget, raise target, repeat.
  - STUCK with no safe candidate is the structural negative: the class itself
    caps below 6 from this seed (the UDG analog of chi(Q^2)=2).

The witness need not be minimal: a later shrink pass removes vertices/edges with
UNSAT re-checks that are CHEAP on the overconstrained side. Resumes from
STATE_B.json (524 edges); writes STATE_C.json.
"""
from __future__ import annotations
import sys, pathlib, json, time, random
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from e14_udg_class_host import (build_clauses, adj_sets, codegree_matrix,
                                k4_safe, codeg_safe, apply_edge)
from e14b_overshoot import budgeted_solve, safe_batch, model_pairs, all_pairs
from f1pt_lib import parse_vtx, parse_edges, VTX, EDGE, CACHE
from pysat.solvers import MapleChrono, Glucose42

OUT = CACHE / "e14_udg_class"
STATE_B = OUT / "STATE.json"          # fallback seed (470)
STATE_B2 = OUT / "STATE_B.json"       # preferred seed (524)
STATE_C = OUT / "STATE_C.json"

SEED = 20260612
JUMP = 150                 # blind edges per overshoot round: clear the hard band
                           # in one leap (it is WIDE: a +70 jump from 524 still
                           # sat inside it after 5 min of solving).
MODEL_SHARP = 25           # model-guided edges added when a round comes back SAT
MAX_TOTAL = 3500
# Probe CHEAP, jump FAR: a small budget returns fast; SAT or indeterminate both
# trigger another big jump (free). Only a decisive UNSAT (fast once well past the
# band) ends it. Large budgets are the LAST resort, used only deep in the search.
BUDGETS = [1_500_000, 5_000_000, 20_000_000]


def blind_fill(n, adj, C, A, target, rng):
    """Add safe edges (codegree-2 first) until edge-count reaches target or
    no safe candidate remains. Degree-biased candidate stream for locality."""
    added_here = []
    degs = np.argsort([-len(a) for a in adj])
    hubs = [int(x) for x in degs[:160]]
    while True:
        cur = int(A.sum()) // 2
        if cur >= target:
            return added_here, "target"
        # candidate stream: hub x hub, then hub x any (lazy)
        stream = ((u, v) for ui, u in enumerate(hubs) for v in hubs[ui + 1:])
        batch = safe_batch(n, adj, C, A, stream, rng, batch=min(JUMP, target - cur))
        if not batch:
            # widen to all pairs touching a hub before declaring stuck
            stream = ((u, v) for u in hubs for v in range(n) if u != v)
            batch = safe_batch(n, adj, C, A, stream, rng,
                               batch=min(JUMP, target - cur))
        if not batch:
            return added_here, "stuck"
        added_here.extend(batch)


def main():
    rng = random.Random(SEED)
    base = parse_vtx(VTX / "510.vtx")
    base_edges = [tuple(e) for e in parse_edges(EDGE / "510.edge")]
    n = len(base)
    # Resume from the deepest checkpoint available: STATE_C (this script's own
    # progress) > STATE_B (524, e14b) > STATE (470, e14).
    seed_state = STATE_C if STATE_C.exists() else (
        STATE_B2 if STATE_B2.exists() else STATE_B)
    added = [tuple(e) for e in json.loads(seed_state.read_text())["added"]]
    print(f"E14c: seed {len(added)} added edges from {seed_state.name}; "
          f"base m={len(base_edges)}", flush=True)

    edges = base_edges + added
    adj = adj_sets(n, edges)
    C = codegree_matrix(n, edges)
    np.fill_diagonal(C, 0)
    A = np.zeros((n, n), dtype=bool)
    for u, v in edges:
        A[u, v] = A[v, u] = True

    cur_added = lambda: int(A.sum()) // 2 - len(base_edges)
    target = len(added) + JUMP
    bi = 0
    rounds = 0
    while cur_added() < MAX_TOTAL:
        rounds += 1
        new, why = blind_fill(n, adj, C, A, len(base_edges) + target, rng)
        added.extend(new)
        edges.extend(new)
        if why == "stuck" and cur_added() < target:
            print(f"STUCK: only {cur_added()} added edges placeable "
                  f"(target {target}); structural cap from this seed", flush=True)
            json.dump({"added": added, "status": "stuck_no_safe_candidate",
                       "n_added": cur_added()}, STATE_C.open("w"))
            return
        b = BUDGETS[min(bi, len(BUDGETS) - 1)]
        json.dump({"added": added, "status": "solving",
                   "n_added": cur_added()}, STATE_C.open("w"))
        print(f"  round {rounds}: {cur_added()} added edges "
              f"(m={len(edges)}); solving (budget {b // 1_000_000}M)...",
              flush=True)
        t0 = time.time()
        res, model = budgeted_solve(n, edges, b, solver_cls=MapleChrono,
                                    model=True)
        dt = time.time() - t0
        if res is False:
            print(f"  *** 5-UNSAT at {cur_added()} added edges ({dt:.0f} s) ***",
                  flush=True)
            print("  cross-checking with Glucose42...", flush=True)
            r2, _ = budgeted_solve(n, edges, 200_000_000, solver_cls=Glucose42)
            cl, _ = build_clauses(n, edges)
            cnf = OUT / f"e14c_p510_plus{cur_added()}_UNSAT_k5.cnf"
            with cnf.open("w") as f:
                f.write(f"c E14c witness: P510 + {cur_added()} safe edges, "
                        f"K4-free + K_2,3-free, 5-UNSAT\n")
                f.write(f"p cnf {n * 5} {len(cl)}\n")
                for c in cl:
                    f.write(" ".join(map(str, c)) + " 0\n")
            json.dump({"added": added, "status": "success_unsat",
                       "n_added": cur_added(), "crosscheck_glucose42": r2,
                       "maple_seconds": round(dt)}, STATE_C.open("w"))
            print(f"  cross-check Glucose42: {r2} "
                  f"(False = confirmed 6-chromatic). DIMACS: {cnf.name}",
                  flush=True)
            return
        if res is True:
            bi = 0
            sharp = safe_batch(n, adj, C, A, model_pairs(model, n), rng,
                               batch=MODEL_SHARP)
            added.extend(sharp)
            edges.extend(sharp)
            target = cur_added() + JUMP
            print(f"  SAT in {dt:.0f} s; +{len(sharp)} sharp model edges; "
                  f"next target {target}", flush=True)
        else:
            bi += 1
            target = cur_added() + JUMP
            print(f"  INDETERMINATE in {dt:.0f} s; escalating budget, "
                  f"next target {target}", flush=True)
    json.dump({"added": added, "status": "max_total_exhausted",
               "n_added": cur_added()}, STATE_C.open("w"))
    print("max total exhausted", flush=True)


if __name__ == "__main__":
    main()
