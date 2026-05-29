r"""h6_direction_b_fast: budget-disciplined incremental vertex deletion.

Complements h6_direction_b_probe.py. Uses a TIGHT per-call conflict budget so
no single SAT dominates (the L29 anti-pattern). Semantics:
  - delete a batch, SAT-check chi<=5 with a tight budget.
  - SAT (fast)   -> deletion broke chi-6 -> revert.
  - UNSAT (fast) -> deletion safe -> commit.
  - BUDGET       -> indeterminate; CONSERVATIVELY revert (keep the vertices) so
    we never claim an unverified chi-6 graph. Reverted-on-budget vertices are
    logged as "indeterminate" for a later long-budget pass.

Starts from H2 non-bridge vertices (114, the smaller class) then H1 non-bridge.
Persists the running minimum before each SAT.
"""
from __future__ import annotations
import json, pathlib, sys, time
from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "combinatorial"))
from h6_bridge_minimum import (load_p510, load_canonical_bridges,
                               k_color_clauses, build_full_edges, omega_leq_3)

CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
MIN_JSON = CACHE / "h6_direction_b_fast_min.json"
LOG = CACHE / "h6_direction_b_fast.log"
N_EACH = 510
TIGHT_BUDGET = 4_000_000      # tight: fast SAT/UNSAT, slow ones hit budget
FINAL_BUDGET = 60_000_000     # generous, for the final confirmation only


def log(m):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {m}"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def induced(active, full):
    aset = set(active)
    e = [(u, v) for (u, v) in full if u in aset and v in aset]
    idmap = {v: i for i, v in enumerate(sorted(aset))}
    return len(aset), [(idmap[u], idmap[v]) for (u, v) in e]


def sat5(active, full, budget, solver="cadical"):
    n, e = induced(active, full)
    clauses, _ = k_color_clauses(n, e, 5)
    S = Cadical195 if solver == "cadical" else Glucose4
    s = S(bootstrap_with=clauses)
    t0 = time.time()
    try:
        s.conf_budget(budget)
        r = s.solve_limited(expect_interrupt=False)
    finally:
        s.delete()
    return r, time.time() - t0


def persist(active, full, extra):
    n, e = induced(active, full)
    d = {"experiment": "h6_direction_b_fast", "N": n,
         "kept_global_indices": sorted(set(active)), "edges": e}
    d.update(extra)
    MIN_JSON.write_text(json.dumps(d), encoding="utf-8")
    return n, len(e)


def main():
    log("=" * 70); log("Direction B FAST deletion start")
    n, eH = load_p510()
    B = load_canonical_bridges()[-2000:]
    full = build_full_edges(N_EACH, eH, eH, B)
    Nfull = 2 * N_EACH
    h1_src = {a for (a, b) in B}
    h2_tgt = {N_EACH + b for (a, b) in B}
    h2_nonbridge = [v for v in range(N_EACH, 2 * N_EACH) if v not in h2_tgt]
    h1_nonbridge = [v for v in range(N_EACH) if v not in h1_src]
    log(f"H2 non-bridge: {len(h2_nonbridge)} | H1 non-bridge: {len(h1_nonbridge)}")

    active = set(range(Nfull))
    committed = 0
    indeterminate = []
    persist(active, full, {"stage": "init"})

    # process in batches, bisecting on failure/budget
    def process(cands, label):
        nonlocal active, committed
        queue = list(cands)
        block = 32
        while queue:
            batch = queue[:block]
            trial = active - set(batch)
            persist(trial, full, {"stage": "trial", "label": label,
                                  "committed": committed})
            r, el = sat5(trial, full, TIGHT_BUDGET)
            v = {True: "SAT(broke)", False: "UNSAT(ok)", None: "BUDGET"}[r]
            log(f"[{label}] batch={len(batch)} |V|->{len(trial)}: {v} [{el:.1f}s]")
            if r is False:
                active = trial; committed += len(batch); queue = queue[block:]
                block = min(block * 2, 64)
                persist(active, full, {"stage": "commit", "committed": committed})
            elif len(batch) == 1:
                if r is None:
                    indeterminate.append(batch[0])
                queue = queue[1:]; block = 32
            else:
                block = max(1, len(batch) // 2)

    process(h2_nonbridge, "H2nb")
    process(h1_nonbridge, "H1nb")

    nF, eF = persist(active, full, {"stage": "final", "committed": committed,
                                    "indeterminate": indeterminate})
    log(f"FAST DONE: |V|={nF} |E|={eF} committed={committed} "
        f"indeterminate={len(indeterminate)}")

    if nF < Nfull:
        n2, e2 = induced(active, full)
        hasK4, _ = omega_leq_3(n2, e2)
        log(f"FINAL omega {'>3!!' if hasK4 else '<=3'}")
        rc, ec = sat5(active, full, FINAL_BUDGET, "cadical")
        log(f"FINAL Cadical chi>=6: {{True:'SAT',False:'UNSAT',None:'BUDGET'}}[{rc}] [{ec:.1f}s]")
        rg, eg = sat5(active, full, FINAL_BUDGET, "glucose")
        log(f"FINAL Glucose chi>=6: {{True:'SAT',False:'UNSAT',None:'BUDGET'}}[{rg}] [{eg:.1f}s]")
        persist(active, full, {"stage": "final_verified", "N": nF,
                               "omega_leq_3": not hasK4,
                               "cadical": str(rc), "glucose": str(rg),
                               "committed": committed,
                               "indeterminate": indeterminate})


if __name__ == "__main__":
    main()
