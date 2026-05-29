r"""h6_direction_b_single: decisive long-budget single-vertex deletion test.

The fast probe showed single non-bridge deletions are SAT-intractable at a 4M
conflict budget (~395s each return indeterminate). To distinguish "1020 is
deletion-rigid (deletion provably breaks chi-6)" from "merely unverifiable in
budget", run ONE single-vertex deletion at a very generous budget on the
lowest-degree H2 non-bridge vertex (the best removal candidate). Also try the
lowest-degree H1 non-bridge vertex. Definitive UNSAT => a 1019-vertex chi-6
record; definitive SAT => that vertex is essential; BUDGET => still intractable.
"""
from __future__ import annotations
import json, pathlib, sys, time
from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "combinatorial"))
from h6_bridge_minimum import (load_p510, load_canonical_bridges,
                               k_color_clauses, build_full_edges, omega_leq_3)

CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
LOG = CACHE / "h6_direction_b_single.log"
OUT = CACHE / "h6_direction_b_single.json"
N_EACH = 510
BIG_BUDGET = 120_000_000   # ~ very generous; well past the 4M that timed out


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


def main():
    log("=" * 70); log("Direction B SINGLE-vertex decisive test")
    n, eH = load_p510()
    B = load_canonical_bridges()[-2000:]
    full = build_full_edges(N_EACH, eH, eH, B)
    Nfull = 2 * N_EACH
    deg = {v: 0 for v in range(Nfull)}
    for (u, v) in full:
        deg[u] += 1; deg[v] += 1
    h1_src = {a for (a, b) in B}
    h2_tgt = {N_EACH + b for (a, b) in B}
    h2_nb = [v for v in range(N_EACH, 2 * N_EACH) if v not in h2_tgt]
    h1_nb = [v for v in range(N_EACH) if v not in h1_src]
    # best removal candidates = lowest degree
    cand_h2 = min(h2_nb, key=lambda v: deg[v])
    cand_h1 = min(h1_nb, key=lambda v: deg[v])
    log(f"lowest-degree H2 non-bridge vtx {cand_h2} deg={deg[cand_h2]}")
    log(f"lowest-degree H1 non-bridge vtx {cand_h1} deg={deg[cand_h1]}")

    results = {}
    for label, cand in [("H2", cand_h2), ("H1", cand_h1)]:
        active = set(range(Nfull)) - {cand}
        r, el = sat5(active, full, BIG_BUDGET, "cadical")
        v = {True: "SAT(chi<=5, vtx essential)",
             False: "UNSAT(chi>=6 SURVIVES, 1019-vtx record!)",
             None: "BUDGET(intractable)"}[r]
        log(f"delete {label} vtx {cand}: {v} [{el:.1f}s]")
        results[label] = {"vtx": cand, "deg": deg[cand], "verdict": v,
                          "elapsed_s": el}
        OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
        if r is False:
            # genuine record: confirm omega + glucose
            n2, e2 = induced(active, full)
            hasK4, _ = omega_leq_3(n2, e2)
            rg, eg = sat5(active, full, BIG_BUDGET, "glucose")
            log(f"  RECORD omega{'>3!!' if hasK4 else '<=3'}; "
                f"Glucose {{True:'SAT',False:'UNSAT',None:'BUDGET'}}[{rg}] [{eg:.1f}s]")
            results[label]["omega_leq_3"] = not hasK4
            results[label]["glucose"] = str(rg)
            gpath = CACHE / f"h6_dirB_1019_del{label}_graph.json"
            gpath.write_text(json.dumps({"N": n2, "edges": e2,
                "deleted_global_vtx": cand}), encoding="utf-8")
            results[label]["graph_path"] = str(gpath)
            OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    log("SINGLE test done.")


if __name__ == "__main__":
    main()
