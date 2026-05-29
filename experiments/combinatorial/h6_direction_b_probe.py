r"""h6_direction_b_probe: Direction B reduction of the 1020-vertex chi-6 graph.

Goal: find a no-K_4 (omega <= 3) abstract graph with chi >= 6 on FEWER than
1020 vertices, by REDUCING the L27/L28 diagonal construction
  G = P_510 cup P_510 + B   (B = last 2000 bridges in greedy-suffix order, L28).

Three probes, run in order of expected value:

  Probe A (essentiality map + bulk deletion). Classify vertices as
    bridge-source (H1), bridge-target (H2), or non-bridge-incident. Then
    delete all non-bridge-incident vertices (H1-only, H2-only, both) and
    SAT-check whether chi >= 6 survives. If it survives -> immediate sub-1020
    record. If not -> bisect to bound how many are removable.

  Probe B (greedy vertex deletion). From the smallest chi-6-preserving graph
    found in A, greedily delete further vertices (non-bridge first, then low
    bridge-degree), committing only deletions that keep chi >= 6 (Cadical
    UNSAT within conflict budget) and omega <= 3.

  Probe C (dual-solver close-out). For the final minimum, dual-confirm chi >= 6
    with Cadical AND Glucose, exhaustive omega <= 3, persist graph, run
    wrong-approach detectors.

Discipline (L29 lesson): PERSIST every reduced graph BEFORE expensive SAT.
Cadical has only a conflict-budget proxy, no wall-clock timeout; budget calls.
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
    load_p510,
    load_canonical_bridges,
    k_color_clauses,
    build_full_edges,
    omega_leq_3,
)

CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

ESSMAP_JSON = CACHE / "h6_direction_b_essmap.json"
MIN_JSON = CACHE / "h6_direction_b_min.json"
LOG_PATH = CACHE / "h6_direction_b_probe.log"

N_EACH = 510


def log(msg: str):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def sat_chi6(N_active, edges, time_limit_s, solver_name="cadical"):
    """chi(G) <= 5 SAT test on an arbitrary vertex set (vertices 0..maxidx).
    Returns (res, elapsed). res True=SAT(chi<=5), False=UNSAT(chi>=6), None=budget.
    We encode over the FULL index range 0..N_active-1 where N_active = max index
    + 1; isolated / deleted indices just get a free color, harmless for UNSAT.
    """
    clauses, _ = k_color_clauses(N_active, edges, 5)
    t0 = time.time()
    if solver_name == "cadical":
        solver = Cadical195(bootstrap_with=clauses)
        rate = 25000
    elif solver_name == "glucose":
        solver = Glucose4(bootstrap_with=clauses)
        rate = 15000
    else:
        raise ValueError(solver_name)
    try:
        solver.conf_budget(int(time_limit_s * rate))
        res = solver.solve_limited(expect_interrupt=False)
    finally:
        solver.delete()
    return res, time.time() - t0


def induced_on(keep_set, edges):
    """Restrict edges to those with both endpoints in keep_set."""
    ks = keep_set
    return [(u, v) for (u, v) in edges if u in ks and v in ks]


def remap(keep_sorted, edges):
    """Relabel a vertex subset to 0..len-1, returning (n, edges_remapped, idmap)."""
    idmap = {v: i for i, v in enumerate(keep_sorted)}
    e2 = [(idmap[u], idmap[v]) for (u, v) in edges]
    return len(keep_sorted), e2, idmap


def main():
    log("=" * 70)
    log("Direction B probe start")

    n, edges_H1 = load_p510()
    assert n == N_EACH
    edges_H2 = edges_H1  # diagonal: identical halves
    bridges_2700 = load_canonical_bridges()
    # L28: last 2000 bridges in greedy-suffix order preserve chi >= 6.
    B = bridges_2700[-2000:]
    log(f"P_510 loaded: {n} vtx, {len(edges_H1)} edges/half; B_2000 = {len(B)} bridges")

    full_edges = build_full_edges(N_EACH, edges_H1, edges_H2, B)
    N_full = 2 * N_EACH
    log(f"Full graph: N={N_full}, |E|={len(full_edges)}")

    # ---- Probe A: essentiality classification ----
    h1_sources = sorted({a for (a, b) in B})            # within-half H1 indices
    h2_targets = sorted({N_EACH + b for (a, b) in B})   # global H2 indices
    h1_nonbridge = [v for v in range(N_EACH) if v not in set(h1_sources)]
    h2_nonbridge = [v for v in range(N_EACH, 2 * N_EACH)
                    if v not in set(h2_targets)]

    log(f"H1 bridge sources: {len(h1_sources)}  |  H1 non-bridge: {len(h1_nonbridge)}")
    log(f"H2 bridge targets: {len(h2_targets)}  |  H2 non-bridge: {len(h2_nonbridge)}")

    essmap = {
        "experiment": "h6_direction_b",
        "bridge_set": "B_2000 (last 2000 of canonical 2700, greedy-suffix)",
        "N_full": N_full,
        "edges_full": len(full_edges),
        "h1_bridge_sources": len(h1_sources),
        "h1_nonbridge": len(h1_nonbridge),
        "h2_bridge_targets": len(h2_targets),
        "h2_nonbridge": len(h2_nonbridge),
        "h1_source_list": h1_sources,
        "h2_target_list": h2_targets,
    }
    ESSMAP_JSON.write_text(json.dumps(essmap, indent=2), encoding="utf-8")
    log(f"Essentiality map persisted: {ESSMAP_JSON}")

    # Baseline sanity: full graph must be UNSAT (chi >= 6) at modest budget.
    res, el = sat_chi6(N_full, full_edges, 600, "cadical")
    verdict = {True: "SAT(chi<=5)", False: "UNSAT(chi>=6)", None: "BUDGET"}[res]
    log(f"BASELINE B_2000 full: {verdict} in {el:.1f}s")
    if res is not False:
        log("WARNING: baseline did not confirm chi>=6 in budget; results below are vs an unconfirmed baseline.")

    # ---- Probe A bulk deletions ----
    def trial(name, delete_set, budget_s):
        keep = sorted(set(range(N_full)) - set(delete_set))
        e_ind = induced_on(set(keep), full_edges)
        # persist BEFORE expensive SAT (L29 lesson)
        nn, e2, idmap = remap(keep, e_ind)
        graph_path = CACHE / f"h6_dirB_{name}_graph.json"
        graph_path.write_text(json.dumps({
            "name": name, "N": nn, "edges": e2,
            "deleted_count": len(delete_set),
            "kept_global_indices": keep,
        }), encoding="utf-8")
        # omega check (deletion cannot create K_4, but verify)
        hasK4, wit = omega_leq_3(nn, e2)
        r, e = sat_chi6(nn, e2, budget_s, "cadical")
        v = {True: "SAT(chi<=5)", False: "UNSAT(chi>=6)", None: "BUDGET"}[r]
        log(f"TRIAL {name}: |V|={nn} (deleted {len(delete_set)}) "
            f"omega{'>3!!' if hasK4 else '<=3'} -> {v} in {e:.1f}s  [{graph_path.name}]")
        return {"name": name, "N": nn, "deleted": len(delete_set),
                "omega_leq_3": not hasK4, "verdict": v, "elapsed_s": e,
                "graph_path": str(graph_path)}

    results = []
    results.append(trial("del_h1nonbridge", h1_nonbridge, 600))
    results.append(trial("del_h2nonbridge", h2_nonbridge, 600))
    results.append(trial("del_both_nonbridge", h1_nonbridge + h2_nonbridge, 900))

    out = {"essmap": essmap, "probe_A_trials": results}
    MIN_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    log(f"Probe A results persisted: {MIN_JSON}")
    log("Probe A done. Inspect verdicts above to decide Probe B.")


if __name__ == "__main__":
    main()
