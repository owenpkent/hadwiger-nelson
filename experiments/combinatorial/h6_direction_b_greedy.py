r"""h6_direction_b_greedy: greedy vertex deletion to reduce the 1020-vtx chi-6 graph.

Run AFTER h6_direction_b_probe.py. Loads B_2000 full graph, then greedily
deletes vertices (non-bridge-incident first, then ascending bridge-degree),
committing a deletion only if chi >= 6 (Cadical UNSAT within conflict budget)
is preserved. omega <= 3 is automatic under deletion (verified once at the end).

Strategy to amortize the very expensive full-budget SAT calls:
  - Batch-delete: try removing a whole block of candidate vertices at once,
    one SAT call. If UNSAT preserved, commit the whole block. If SAT or budget,
    bisect the block (binary search the largest removable prefix).
  - Order candidates by ascending degree-in-current-graph so the least
    constrained vertices go first.

Each committed state is persisted to h6_direction_b_greedy_min.json BEFORE the
next SAT (L29 lesson: never lose a hard instance).

Budget note: Cadical conf_budget rate is empirically ~12k/s on these instances
(the probe baseline ran 2078s at a nominal 600s/25k cap => ~7.2k eff conf/s).
We set a generous per-call budget and accept BUDGET as "indeterminate -> keep".
"""

from __future__ import annotations

import json
import pathlib
import sys
import time

from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "combinatorial"))
from h6_bridge_minimum import (  # noqa: E402
    load_p510, load_canonical_bridges, k_color_clauses,
    build_full_edges, omega_leq_3,
)

CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
MIN_JSON = CACHE / "h6_direction_b_greedy_min.json"
LOG_PATH = CACHE / "h6_direction_b_greedy.log"
N_EACH = 510

# Per-SAT conflict budget. ~12k eff conf/s; 1800 => ~ up to ~40 min worst case.
PER_CALL_BUDGET_CONF = 22_000_000


def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def chi6_unsat(active_vertices, edges_full, budget_conf, solver="cadical"):
    """chi >= 6 test on induced subgraph. Returns (res, elapsed):
    res False = UNSAT (chi>=6 preserved, GOOD), True = SAT (chi<=5, deletion
    broke it), None = budget exhausted (indeterminate)."""
    aset = set(active_vertices)
    e = [(u, v) for (u, v) in edges_full if u in aset and v in aset]
    idmap = {v: i for i, v in enumerate(sorted(aset))}
    e2 = [(idmap[u], idmap[v]) for (u, v) in e]
    clauses, _ = k_color_clauses(len(aset), e2, 5)
    t0 = time.time()
    S = Cadical195 if solver == "cadical" else Glucose4
    s = S(bootstrap_with=clauses)
    try:
        s.conf_budget(budget_conf)
        res = s.solve_limited(expect_interrupt=False)
    finally:
        s.delete()
    return res, time.time() - t0


def persist(active, edges_full, extra=None):
    aset = set(active)
    e = [(u, v) for (u, v) in edges_full if u in aset and v in aset]
    idmap = {v: i for i, v in enumerate(sorted(aset))}
    e2 = [(idmap[u], idmap[v]) for (u, v) in e]
    d = {"experiment": "h6_direction_b_greedy", "N": len(aset),
         "kept_global_indices": sorted(aset), "edges": e2}
    if extra:
        d.update(extra)
    MIN_JSON.write_text(json.dumps(d), encoding="utf-8")
    return len(aset), len(e2)


def main():
    log("=" * 70)
    log("Direction B greedy deletion start")
    n, eH = load_p510()
    B = load_canonical_bridges()[-2000:]
    full = build_full_edges(N_EACH, eH, eH, B)
    Nfull = 2 * N_EACH

    h1_sources = {a for (a, b) in B}
    h2_targets = {N_EACH + b for (a, b) in B}
    bridge_incident = h1_sources | h2_targets

    active = set(range(Nfull))
    deg = {v: 0 for v in active}
    for (u, v) in full:
        deg[u] += 1; deg[v] += 1

    # Candidate order: non-bridge vertices ascending degree, then bridge vertices
    # ascending bridge-degree. Non-bridge first.
    nonbridge = sorted((v for v in active if v not in bridge_incident),
                       key=lambda v: deg[v])
    log(f"candidates: {len(nonbridge)} non-bridge vertices to attempt (ascending degree)")

    persist(active, full, {"stage": "init"})

    committed = 0
    indeterminate = 0
    # Batch bisection over the non-bridge candidate list.
    queue = list(nonbridge)
    block = 64  # initial batch size
    while queue:
        batch = queue[:block]
        trial_active = active - set(batch)
        persist(trial_active, full, {"stage": "trial", "batch_size": len(batch),
                                     "committed_so_far": committed})
        res, el = chi6_unsat(trial_active, full, PER_CALL_BUDGET_CONF)
        v = {True: "SAT(broke)", False: "UNSAT(ok)", None: "BUDGET"}[res]
        log(f"batch={len(batch)} |V|->{len(trial_active)} : {v} [{el:.1f}s]")
        if res is False:
            active = trial_active
            committed += len(batch)
            queue = queue[block:]
            block = min(block * 2, 128)  # grow on success
            persist(active, full, {"stage": "committed", "committed": committed})
        else:
            if len(batch) == 1:
                # this single vertex is essential (or indeterminate); skip it
                if res is None:
                    indeterminate += 1
                queue = queue[1:]
                block = 64
            else:
                block = max(1, len(batch) // 2)  # bisect

    Nf, Ef = persist(active, full, {"stage": "final"})
    log(f"GREEDY DONE: |V|={Nf}, |E|={Ef}, committed deletions={committed}, "
        f"indeterminate={indeterminate}")

    # final omega + dual-solver chi confirmation
    aset = set(active)
    e = [(u, v) for (u, v) in full if u in aset and v in aset]
    idmap = {v: i for i, v in enumerate(sorted(aset))}
    e2 = [(idmap[u], idmap[v]) for (u, v) in e]
    hasK4, _ = omega_leq_3(len(aset), e2)
    log(f"FINAL omega {'>3 !!' if hasK4 else '<=3'} on {len(aset)} vtx")
    rc, ec = chi6_unsat(active, full, PER_CALL_BUDGET_CONF, "cadical")
    log(f"FINAL Cadical: {{True:'SAT',False:'UNSAT',None:'BUDGET'}}[{rc}] [{ec:.1f}s]")
    rg, eg = chi6_unsat(active, full, PER_CALL_BUDGET_CONF, "glucose")
    log(f"FINAL Glucose: {{True:'SAT',False:'UNSAT',None:'BUDGET'}}[{rg}] [{eg:.1f}s]")
    persist(active, full, {"stage": "final_verified", "omega_leq_3": not hasK4,
                           "cadical": str(rc), "glucose": str(rg),
                           "committed": committed, "indeterminate": indeterminate})


if __name__ == "__main__":
    main()
