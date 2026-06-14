r"""E14b (v2): model-guided overshoot past the SAT boundary, all calls bounded.

E14 grew P510 inside the UDG-necessary class (K4-free + K_{2,3}-free hard
invariants) to 470 added edges, then stalled: its pool sampler needed cheap
SAT models, and at the boundary Cadical took 12+ h on an instance MapleChrono
decides in 155 s (portfolio lesson). The v1 overshoot still bootstrapped a
coloring pool (too expensive here: one solve costs minutes, a pool needs
dozens, and relaxation-filtering decays like mono_rate^k).

v2 drops the pool. The loop is three-way and every solver call is budgeted:

  budgeted MapleChrono solve on current G
    UNSAT          -> SUCCESS: a 6-chromatic graph in the UDG-necessary class
                      (cross-checked with a second budgeted solver).
    SAT (model)    -> add a batch of 6 safe blocking edges chosen INSIDE the
                      model's color classes (each provably kills this model),
                      preferring pairs with 2 common neighbors (closes two
                      triangles: strongest local constraint, triangle-rich =
                      the UDG-flavored substrate L61/L63 want).
    indeterminate  -> add a blind batch of safe high-codegree pairs, escalate
                      the budget and continue (overconstraining makes the
                      next UNSAT attempt cheaper: the overshoot principle).

  STUCK (no safe candidate) is the structural negative: the class itself
  resists 6-chromaticity from this seed.

Resumes from STATE_B.json if present, else from E14's STATE.json (470 edges).
Shrink (vertex/edge minimization on the overconstrained side, where UNSAT
checks are cheap) is a follow-up step reusing E14 machinery with Maple.
"""
from __future__ import annotations
import sys, pathlib, json, time, random
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from e14_udg_class_host import (build_clauses, adj_sets, codegree_matrix,
                                k4_safe, codeg_safe, apply_edge)
from f1pt_lib import parse_vtx, parse_edges, VTX, EDGE, CACHE
from pysat.solvers import MapleChrono, Glucose42
from portfolio_sat import build_color_cnf_symbreak, solve_color  # L68

OUT = CACHE / "e14_udg_class"
STATE_A = OUT / "STATE.json"
STATE_B = OUT / "STATE_B.json"

SEED = 20260612
MAX_ADDS_TOTAL = 2000
BATCH = 15
BUDGETS = [3_000_000, 12_000_000, 50_000_000]


def budgeted_solve(n, edges, budget, solver_cls=MapleChrono, model=False,
                   symbreak=True):
    # L68: the in-class decisive solve runs on the symmetry-broken encoding so the
    # near-boundary 5-UNSAT proof (the ~2 CPU-hour cost) is cheap; var(v,c) is the
    # same v*5+c+1, so model decoding is unchanged. A canonical model still yields
    # valid same-color overshoot pairs.
    cl, var = (build_color_cnf_symbreak(n, edges, 5) if symbreak
               else build_clauses(n, edges))
    s = solver_cls(bootstrap_with=cl)
    try:
        s.conf_budget(budget)
        res = s.solve_limited()
        out = None
        if res and model:
            mset = set(x for x in s.get_model() if x > 0)
            out = [next(c for c in range(5) if var(v, c) in mset)
                   for v in range(n)]
        return res, out
    finally:
        s.delete()


def safe_batch(n, adj, C, A, pairs_iter, rng, batch=BATCH):
    """Greedy: take up to `batch` safe pairs, preferring codegree 2 then 1."""
    buckets = {2: [], 1: [], 0: []}
    for u, v in pairs_iter:
        if not A[u, v]:
            buckets[min(2, int(C[u, v]))].append((u, v))
    out = []
    for key in (2, 1, 0):
        rng.shuffle(buckets[key])
        for u, v in buckets[key]:
            if A[u, v]:
                continue
            if k4_safe(adj, u, v) and codeg_safe(adj, C, u, v):
                apply_edge(adj, C, u, v)
                A[u, v] = A[v, u] = True
                out.append((u, v))
                if len(out) >= batch:
                    return out
    return out


def model_pairs(model, n):
    groups = {}
    for v, c in enumerate(model):
        groups.setdefault(c, []).append(v)
    for vs in groups.values():
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                yield (vs[i], vs[j])


def all_pairs(n, degs_order):
    for i in range(len(degs_order)):
        for j in range(i + 1, len(degs_order)):
            yield (int(degs_order[i]), int(degs_order[j]))


def main():
    rng = random.Random(SEED)
    base = parse_vtx(VTX / "510.vtx")
    base_edges = [tuple(e) for e in parse_edges(EDGE / "510.edge")]
    n = len(base)
    if STATE_B.exists() and "added" in json.loads(STATE_B.read_text()):
        added = [tuple(e) for e in json.loads(STATE_B.read_text())["added"]]
        src = "STATE_B"
    else:
        added = [tuple(e) for e in json.loads(STATE_A.read_text())["added"]]
        src = "STATE_A"
    print(f"E14b v2: resuming from {len(added)} added edges ({src})", flush=True)

    edges = base_edges + added
    adj = adj_sets(n, edges)
    C = codegree_matrix(n, edges)
    np.fill_diagonal(C, 0)
    A = np.zeros((n, n), dtype=bool)
    for u, v in edges:
        A[u, v] = A[v, u] = True

    bi = 0
    while len(added) < MAX_ADDS_TOTAL:
        b = BUDGETS[min(bi, len(BUDGETS) - 1)]
        t0 = time.time()
        res, model = budgeted_solve(n, edges, b, model=True)
        dt = time.time() - t0
        if res is False:
            print(f"SUCCESS: 5-UNSAT at {len(added)} added edges ({dt:.0f} s); "
                  f"cross-checking with Glucose42...", flush=True)
            r2, _ = budgeted_solve(n, edges, 100_000_000, solver_cls=Glucose42)
            # L68: emit a DRAT certificate of the symmetry-broken 5-UNSAT, the
            # in-class chi>=6 target object, for a certificate-grade record.
            cert = solve_color(n, edges, 5, symbreak=True,
                               proof_path=str(OUT / "e14b_witness_5unsat.drat"))
            json.dump({"added": added, "status": "success_unsat",
                       "crosscheck_glucose42": r2,
                       "drat_proof": cert["proof_path"],
                       "drat_lines": cert["proof_lines"]}, STATE_B.open("w"))
            print(f"cross-check: {r2} (False=confirmed UNSAT); "
                  f"DRAT proof: {cert['proof_lines']} lines -> "
                  f"{cert['proof_path']}", flush=True)
            return
        if res is True:
            bi = 0
            batch = safe_batch(n, adj, C, A, model_pairs(model, n), rng)
            kind = "model"
        else:
            bi += 1
            degs = np.argsort([-len(a) for a in adj])
            batch = safe_batch(n, adj, C, A, all_pairs(n, degs[:120]), rng)
            kind = f"blind(bi={bi})"
        if not batch:
            print(f"STUCK: no safe {kind} candidates at {len(added)} edges",
                  flush=True)
            json.dump({"added": added, "status": f"stuck_{kind}"},
                      STATE_B.open("w"))
            return
        added.extend(batch)
        edges.extend(batch)
        json.dump({"added": added, "status": "growing"}, STATE_B.open("w"))
        print(f"  {len(added)} edges (+{len(batch)} {kind}); solve {res} "
              f"in {dt:.0f} s (budget {b // 1_000_000}M)", flush=True)
    json.dump({"added": added, "status": "max_adds_exhausted"},
              STATE_B.open("w"))
    print("max adds exhausted", flush=True)


if __name__ == "__main__":
    main()
