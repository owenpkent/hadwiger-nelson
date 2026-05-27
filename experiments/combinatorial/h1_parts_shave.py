r"""h1_parts_shave: Greedy vertex elimination on Polymath 510 (Parts 509 lineage).

Architecture 1, overnight long-job H1.

Goal. Attempt to shave Polymath 510 (510 vertices, 2504 edges, chi >= 5) below
510 via SAT-driven greedy vertex elimination, with pair / triple elimination
once single elimination plateaus.

Findings from initial probe.
  Polymath 510 is VERTEX-CRITICAL: all 510 single-vertex removals drop chi to 4
  (verified via Cadical, ~99s wall time for the full sweep). So Phase 1 (single
  vertex elimination) cannot reduce |V|.

  Strategy below focuses on Phase 2 (pair elimination, with checkpointing) and
  Phase 3 (triple elimination on remaining low-degree candidates), since pair
  attempts are fast (UNSAT is rare, mean SAT-call time ~0.15s).

Method.
  Phase 1. Verify single-vertex criticality and cache the result.
  Phase 2. Enumerate non-adjacent pairs (u, v) in ascending degree-sum order;
           attempt removal of each. If chi(G - {u,v}) >= 5 (k=4 UNSAT), commit
           and restart Phase 2 from scratch (in case removing the pair opened
           up more pairs). Otherwise restore.
  Phase 3. After Phase 2 saturates, try triples in ascending degree-sum order.

Checkpointing.
  After each successful removal: write _cache/h1_parts_state.json AND
  _cache/h1_parts_minimize_<N>.json.

Output.
  Logs to _cache/h1_parts_shave.log.
  Summary at _cache/h1_parts_shave_summary.json.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys
import time

from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
EDGE_PATH = REPO_ROOT / "sources" / "cnp-sat" / "edge" / "510.edge"
OVERLAP_CACHE = CACHE / "e1t_overlap_chi.json"

STATE_PATH = CACHE / "h1_parts_state.json"
SINGLES_CACHE = CACHE / "h1_parts_singles.json"
PAIRS_PROGRESS = CACHE / "h1_parts_pairs_progress.json"
LOG_PATH = CACHE / "h1_parts_shave.log"
CHECKPOINT_EVERY = 500  # save pair-progress every N pairs


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


def edges_among(edges, V_set):
    return [(u, v) for (u, v) in edges if u in V_set and v in V_set]


def sat_k_color(active_list, edges_full, k):
    """SAT check whether the subgraph on `active_list` is k-colorable.

    Returns (sat: bool, elapsed_s: float).
    """
    N = len(active_list)
    if N == 0:
        return True, 0.0
    idx = {v: i for i, v in enumerate(active_list)}
    active_set = set(active_list)

    def var(v_local, c):
        return v_local * k + c + 1

    clauses = []
    for i in range(N):
        clauses.append([var(i, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(i, c1), -var(i, c2)])
    for (u, v) in edges_full:
        if u in active_set and v in active_set:
            for c in range(k):
                clauses.append([-var(idx[u], c), -var(idx[v], c)])
    t0 = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
    return sat, time.time() - t0


def log(msg):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def save_checkpoint(active, history, phase, elapsed, sat_calls, sat_total_t,
                    fname=None):
    out = {
        "experiment": "h1_parts_shave",
        "starting_n": 510,
        "starting_edges": 2504,
        "current_n": len(active),
        "active_vertices": sorted(active),
        "history": history,
        "phase": phase,
        "elapsed_sec": round(elapsed, 2),
        "sat_calls": sat_calls,
        "sat_total_sec": round(sat_total_t, 2),
    }
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w") as f:
        json.dump(out, f, indent=2)
    if fname:
        with (CACHE / fname).open("w") as f:
            json.dump(out, f, indent=2)


def main():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log("=" * 60)
    log("h1_parts_shave starting")
    log("=" * 60)

    edges = parse_edge_file(EDGE_PATH)
    n_init = 510
    log(f"Loaded Polymath 510: {n_init} vertices, {len(edges)} edges")

    adj = [set() for _ in range(n_init)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Bridge incident classification
    bridge_incident = set()
    try:
        if OVERLAP_CACHE.exists():
            ov = json.loads(OVERLAP_CACHE.read_text())
            overlap_idx = set(ov["overlap_poly_indices"])
            for (u, v) in edges:
                if (u in overlap_idx) != (v in overlap_idx):
                    bridge_incident.add(u)
                    bridge_incident.add(v)
            log(f"Bridge-incident vertices (L20 classification): {len(bridge_incident)}")
    except Exception as e:
        log(f"Could not load overlap classification: {e}")

    # Resume support.
    history = []
    t_start = time.time()
    sat_calls = 0
    sat_total_t = 0.0
    phase = "phase1_singles"

    if STATE_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text())
            active = set(state["active_vertices"])
            history = state.get("history", [])
            sat_calls = state.get("sat_calls", 0)
            sat_total_t = state.get("sat_total_sec", 0.0)
            phase = state.get("phase", "phase1_singles")
            log(f"Resumed from checkpoint: |V|={len(active)}, phase={phase}, history={len(history)}")
        except Exception as e:
            log(f"Failed to load state: {e}; starting fresh")
            active = set(range(n_init))
    else:
        active = set(range(n_init))

    # ========================== PHASE 1: SINGLES ==========================
    # Test every single-vertex removal once. Polymath 510 is known critical,
    # but we re-verify and cache, since after pair removals there might be
    # newly removable singles.

    def phase1_singles(max_time, skip_if_cached=True):
        nonlocal active, sat_calls, sat_total_t, history
        # Optimization: if a previous run cached the singles result for the
        # current active set size, skip.
        if skip_if_cached and SINGLES_CACHE.exists():
            try:
                cache = json.loads(SINGLES_CACHE.read_text())
                if cache.get("n_active") == len(active) and cache.get("removable") == []:
                    log(f"Phase 1: SKIPPED (cached: |V|={len(active)}, all single removals fail)")
                    return False
            except Exception:
                pass
        log(f"Phase 1: single-vertex elimination on |V|={len(active)}")
        t_phase = time.time()
        removable = []

        # Order by ascending degree-in-active.
        deg = {v: len(adj[v] & active) for v in active}
        order = sorted(active, key=lambda v: (deg[v], v in bridge_incident, v))
        n_checked = 0
        any_removed = False

        for v in order:
            if (time.time() - t_start) > max_time:
                log("  time budget exceeded mid-Phase 1")
                return any_removed
            if v not in active:
                continue
            trial = active - {v}
            alist = sorted(trial)
            sat4, t4 = sat_k_color(alist, edges, 4)
            sat_calls += 1
            sat_total_t += t4
            n_checked += 1
            if sat4 is False:
                # chi(G - v) >= 5: commit removal
                active = trial
                removable.append(v)
                any_removed = True
                history.append({"phase": "single", "removed": v, "n_after": len(active), "t_sat": round(t4, 3)})
                log(f"  REMOVED v={v} (deg={deg[v]}, bridge={v in bridge_incident}); |V|={len(active)}, t={t4:.2f}s")
                save_checkpoint(active, history, phase, time.time() - t_start, sat_calls, sat_total_t,
                                fname=f"h1_parts_minimize_{len(active)}.json")
            if n_checked % 100 == 0:
                log(f"    [singles {n_checked}/{len(order)}] removable_so_far={len(removable)}, |V|={len(active)}, sat_t_avg={sat_total_t / max(1, sat_calls):.3f}s")
        log(f"  Phase 1 done in {time.time() - t_phase:.1f}s, removable={len(removable)}")
        # Cache the single-vertex results for the active graph
        try:
            with SINGLES_CACHE.open("w") as f:
                json.dump({"n_active": len(active), "removable": removable, "checked": n_checked, "phase_time": time.time() - t_phase}, f, indent=2)
        except Exception:
            pass
        return any_removed

    # ========================== PHASE 2: PAIRS ==========================

    def phase2_pairs(max_time):
        """Pair elimination. Returns True if any pair was removed."""
        nonlocal active, sat_calls, sat_total_t, history
        t_phase = time.time()
        log(f"Phase 2: pair elimination on |V|={len(active)}")

        deg = {v: len(adj[v] & active) for v in active}
        active_list = sorted(active)
        # All non-adjacent pairs, sorted by ascending sum of degrees.
        pairs = []
        for i, u in enumerate(active_list):
            for v in active_list[i + 1:]:
                if v in adj[u]:
                    continue
                pairs.append((deg[u] + deg[v], u, v))
        pairs.sort(key=lambda x: x[0])
        log(f"  {len(pairs)} non-adjacent pairs to try")

        # Resume support: if pairs progress cache matches the active set, skip
        # to the recorded index.
        start_idx = 0
        if PAIRS_PROGRESS.exists():
            try:
                pp = json.loads(PAIRS_PROGRESS.read_text())
                if pp.get("active_sig") == sorted(active):
                    start_idx = pp.get("next_idx", 0)
                    log(f"  Resuming Phase 2 from pair index {start_idx} (of {len(pairs)})")
            except Exception as e:
                log(f"  Could not load pair-progress: {e}")

        any_removed = False
        n_checked = start_idx
        for idx in range(start_idx, len(pairs)):
            _s, u, v = pairs[idx]
            if (time.time() - t_start) > max_time:
                log("  Phase 2 time budget exceeded")
                # Save progress
                with PAIRS_PROGRESS.open("w") as f:
                    json.dump({"active_sig": sorted(active), "next_idx": idx, "n_pairs": len(pairs)}, f)
                break
            if u not in active or v not in active:
                continue
            trial = active - {u, v}
            alist = sorted(trial)
            sat4, t4 = sat_k_color(alist, edges, 4)
            sat_calls += 1
            sat_total_t += t4
            n_checked += 1
            if sat4 is False:
                active = trial
                any_removed = True
                history.append({"phase": "pair", "removed": [u, v], "n_after": len(active), "t_sat": round(t4, 3)})
                log(f"  REMOVED PAIR (u={u}, v={v}); |V|={len(active)}, t={t4:.2f}s")
                save_checkpoint(active, history, phase, time.time() - t_start, sat_calls, sat_total_t,
                                fname=f"h1_parts_minimize_{len(active)}.json")
                # Clear pair-progress; structure changed.
                if PAIRS_PROGRESS.exists():
                    PAIRS_PROGRESS.unlink()
                # Return to allow Phase 1 to re-run.
                return True
            if n_checked % 1000 == 0:
                elapsed_phase = time.time() - t_phase
                rate = max(1, (n_checked - start_idx)) / max(0.001, elapsed_phase)
                remaining = len(pairs) - n_checked
                eta = remaining / max(0.001, rate)
                log(f"    [pairs {n_checked}/{len(pairs)}] |V|={len(active)}, avg_t={sat_total_t/max(1,sat_calls):.3f}s, ETA={eta:.0f}s")
            if n_checked % CHECKPOINT_EVERY == 0:
                with PAIRS_PROGRESS.open("w") as f:
                    json.dump({"active_sig": sorted(active), "next_idx": idx + 1, "n_pairs": len(pairs)}, f)
        # Phase exhausted (no more pairs)
        if n_checked >= len(pairs) - 1:
            # Mark pairs as fully exhausted: write a sentinel
            with PAIRS_PROGRESS.open("w") as f:
                json.dump({"active_sig": sorted(active), "next_idx": len(pairs), "n_pairs": len(pairs), "exhausted": True}, f)
        log(f"  Phase 2 done; pairs tried={n_checked}, any_removed={any_removed}, time={time.time() - t_phase:.1f}s")
        return any_removed

    # ========================== PHASE 3: TRIPLES ==========================

    def phase3_triples(max_time, low_deg_window=80, max_triples=100000):
        """Triple elimination on low-degree vertices only (combinatorial blowup
        prevents full enumeration)."""
        nonlocal active, sat_calls, sat_total_t, history
        t_phase = time.time()
        deg = {v: len(adj[v] & active) for v in active}
        low_deg_v = sorted(active, key=lambda v: (deg[v], v))[:low_deg_window]
        log(f"Phase 3: triples among {len(low_deg_v)} low-degree vertices (max {max_triples})")
        any_removed = False
        triples_tried = 0
        for u, v, w in itertools.combinations(low_deg_v, 3):
            if (time.time() - t_start) > max_time:
                log("  Phase 3 time budget exceeded")
                break
            if triples_tried >= max_triples:
                break
            if u not in active or v not in active or w not in active:
                continue
            trial = active - {u, v, w}
            alist = sorted(trial)
            sat4, t4 = sat_k_color(alist, edges, 4)
            sat_calls += 1
            sat_total_t += t4
            triples_tried += 1
            if sat4 is False:
                active = trial
                any_removed = True
                history.append({"phase": "triple", "removed": [u, v, w], "n_after": len(active), "t_sat": round(t4, 3)})
                log(f"  REMOVED TRIPLE (u={u}, v={v}, w={w}); |V|={len(active)}, t={t4:.2f}s")
                save_checkpoint(active, history, phase, time.time() - t_start, sat_calls, sat_total_t,
                                fname=f"h1_parts_minimize_{len(active)}.json")
                return True
            if triples_tried % 1000 == 0:
                elapsed_phase = time.time() - t_phase
                rate = triples_tried / max(0.001, elapsed_phase)
                log(f"    [triples {triples_tried}/{max_triples}] avg_t={sat_total_t/max(1,sat_calls):.3f}s, rate={rate:.1f}/s")
        log(f"  Phase 3 done; tried={triples_tried}, any_removed={any_removed}, time={time.time() - t_phase:.1f}s")
        return any_removed

    # Main loop: phase 1 -> phase 2 -> phase 1 -> ... -> phase 3 -> ...
    MAX_TIME = 6.5 * 3600  # 6.5h main budget; phase 3 stops at 7h
    PHASE3_MAX_TIME = 7.0 * 3600
    iteration = 0

    while True:
        iteration += 1
        elapsed = time.time() - t_start
        log(f"=== Iteration {iteration}, elapsed={elapsed:.0f}s, |V|={len(active)} ===")

        if elapsed > MAX_TIME:
            log("Main time budget exceeded")
            break

        phase = "phase1_singles"
        if phase1_singles(MAX_TIME):
            # singles removed, continue
            save_checkpoint(active, history, phase, time.time() - t_start, sat_calls, sat_total_t)
            continue

        elapsed = time.time() - t_start
        if elapsed > MAX_TIME:
            log("Main time budget exceeded after Phase 1")
            break

        phase = "phase2_pairs"
        if phase2_pairs(MAX_TIME):
            # pair removed; restart from Phase 1
            save_checkpoint(active, history, phase, time.time() - t_start, sat_calls, sat_total_t)
            continue
        # If neither singles nor pairs removed something, attempt Phase 3
        elapsed = time.time() - t_start
        if elapsed > PHASE3_MAX_TIME:
            log("Phase 3 budget exhausted before starting")
            break

        phase = "phase3_triples"
        if phase3_triples(PHASE3_MAX_TIME):
            save_checkpoint(active, history, phase, time.time() - t_start, sat_calls, sat_total_t)
            continue

        log("No removal in singles, pairs, or triples; minimization saturated")
        break

    # Final output.
    elapsed_total = time.time() - t_start
    final_edges = edges_among(edges, active)
    log("=" * 60)
    log(f"FINAL |V|={len(active)} (from 510, removed {510 - len(active)})")
    log(f"FINAL |E|={len(final_edges)} (from 2504, removed {2504 - len(final_edges)})")
    log(f"Total SAT calls: {sat_calls}")
    log(f"Total SAT solver time: {sat_total_t:.1f}s")
    log(f"Total wall time: {elapsed_total:.1f}s")

    save_checkpoint(active, history, "final", elapsed_total, sat_calls, sat_total_t,
                    fname=f"h1_parts_minimize_{len(active)}_final.json")

    summary = {
        "experiment": "h1_parts_shave",
        "starting_n": n_init,
        "final_n": len(active),
        "starting_edges": 2504,
        "final_edges": len(final_edges),
        "removed_vertices": sorted(set(range(n_init)) - active),
        "history": history,
        "sat_calls": sat_calls,
        "sat_solver_time_sec": round(sat_total_t, 2),
        "wall_time_sec": round(elapsed_total, 2),
        "iterations": iteration,
    }
    with (CACHE / "h1_parts_shave_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
    log(f"Summary written: {CACHE / 'h1_parts_shave_summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
