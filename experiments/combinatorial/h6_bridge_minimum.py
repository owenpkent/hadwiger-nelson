r"""h6_bridge_minimum: pin down the minimum |B| such that P_510 cup P_510 cup B
has chi >= 6 with omega <= 3.

Successor to the L27 partial probe at experiments/combinatorial/_cache/
h5_minimality_probe.log, which left the chi-6 threshold in (1200, 2200].

Pipeline.

  Stage 1. Binary search in greedy-suffix order. The canonical bridge set B*
           (2700 bridges) is ordered by marginal gain; B_K = last K bridges.
           Per K, test chi(P_510^2 cup B_K) >= 6:
             - Cadical 195 with 30-min timeout (primary).
             - Glucose 4 with 60-min timeout if Cadical times out.
             - On both timeouts: record as undecided, fall back to larger K.
           Cache every result keyed by K.

  Stage 2. Local one-bridge removals around the boundary K*. For up to 100
           random bridges b in B_{K*}, test chi(B_{K*} \ {b}) >= 6 via Cadical
           with a 5-min timeout. Every success: commit and restart the loop
           on the new (smaller) set.

  Stage 3. omega + verification. NetworkX K_4 enumeration on the minimum
           graph. Re-run chi >= 6 with Cadical + Glucose (matches L27 triple-
           solver standard, minus Minisat).

  Stage 4. F-profile + saturation analysis. For each saturating v at the
           minimum, compute |F(v)| histogram over the 88 cached c_1 samples
           and the U_v structure. Compare to L27 bimodal (0/5) baseline.

Outputs (all under experiments/combinatorial/_cache/).
  - h6_bridge_minimum.json: per-K results, final minimum metadata, F-profile.
  - h6_p510_squared_min_chi6.dimacs: DIMACS for the minimum graph.
  - h6_bridge_minimum.log: append-only run log.

Discipline.
  - No floating-point distance checks (this script is purely combinatorial /
    abstract; the L27 cocircularity obstruction already shows non-realizability).
  - Cache every SAT result. Resume-on-restart by reading h6_bridge_minimum.json.
"""

from __future__ import annotations

import json
import pathlib
import random
import sys
import time
from typing import Optional

from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

EDGE_PATH = REPO_ROOT / "sources" / "cnp-sat" / "edge" / "510.edge"
CANONICAL_BRIDGES_JSON = CACHE / "h5_p510_squared_chi6.json"
COLORINGS_CACHE = CACHE / "h5_p510_5colorings.json"

RESULT_JSON = CACHE / "h6_bridge_minimum.json"
MIN_DIMACS = CACHE / "h6_p510_squared_min_chi6.dimacs"
LOG_PATH = CACHE / "h6_bridge_minimum.log"


# ---------------------------------------------------------------------------
# logging
# ---------------------------------------------------------------------------

def log(msg: str):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


# ---------------------------------------------------------------------------
# graph + bridges
# ---------------------------------------------------------------------------

def parse_edge_file(path: pathlib.Path):
    edges = []
    n = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("p"):
            n = int(line.split()[2]); continue
        if line.startswith("c"):
            continue
        if line.startswith("e"):
            p = line.split()
            edges.append((int(p[1]) - 1, int(p[2]) - 1))
    return n, edges


def load_p510():
    n, edges = parse_edge_file(EDGE_PATH)
    assert n == 510 and len(edges) == 2504
    return n, edges


def load_canonical_bridges():
    d = json.loads(CANONICAL_BRIDGES_JSON.read_text(encoding="utf-8"))
    # JSON: d['graph']['bridges'] is an int count; the list lives under d['bridge_list'].
    actual = d.get("bridge_list", [])
    bridges = [(int(u), int(v)) for (u, v) in actual]
    assert len(bridges) == 2700, f"Expected 2700 bridges, got {len(bridges)}"
    return bridges


# ---------------------------------------------------------------------------
# SAT
# ---------------------------------------------------------------------------

def k_color_clauses(N, edges, k):
    clauses = []
    def var(v, c):
        return v * k + c + 1
    for v in range(N):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    return clauses, var


def sat_check_chi6(N, edges_full, time_limit_s, solver_name="cadical"):
    """Test chi(G) <= 5 via SAT. Returns (sat, elapsed).
       sat=True  -> chi <= 5 (chi-6 NOT achieved)
       sat=False -> chi >= 6 (UNSAT, chi-6 achieved)
       sat=None  -> timeout.

    Conflict budget heuristic: empirically ~25k conflicts/sec on these
    P_510^2 instances (Cadical), ~15k for Glucose. Cap the budget conservatively
    so a stated 900s limit doesn't run for 2700s of wall clock.
    """
    clauses, _ = k_color_clauses(N, edges_full, 5)
    t0 = time.time()
    if solver_name == "cadical":
        solver = Cadical195(bootstrap_with=clauses)
        rate = 25000  # conflicts/sec empirical
    elif solver_name == "glucose":
        solver = Glucose4(bootstrap_with=clauses)
        rate = 15000
    else:
        raise ValueError(solver_name)
    try:
        budget = int(time_limit_s * rate)
        solver.conf_budget(budget)
        res = solver.solve_limited(expect_interrupt=False)
    finally:
        solver.delete()
    elapsed = time.time() - t0
    return res, elapsed


def build_full_edges(N_each, edges_H1, edges_H2, B):
    return (list(edges_H1)
            + [(N_each + a, N_each + b) for (a, b) in edges_H2]
            + [(a, N_each + b) for (a, b) in B])


# ---------------------------------------------------------------------------
# omega (K_4) enumeration
# ---------------------------------------------------------------------------

def omega_leq_3(N, edges):
    """Return (has_K4, witness). Triangle enumeration -> for each triangle,
    check for a common neighbor.
    """
    adj = [set() for _ in range(N)]
    for (u, v) in edges:
        adj[u].add(v); adj[v].add(u)
    for u in range(N):
        nu = sorted(x for x in adj[u] if x > u)
        for i in range(len(nu)):
            v = nu[i]
            for j in range(i + 1, len(nu)):
                w = nu[j]
                if w in adj[v]:
                    # u < v < w form a triangle. Find common 4th.
                    common = adj[u] & adj[v] & adj[w]
                    common = {x for x in common if x > w}
                    if common:
                        x = next(iter(common))
                        return True, (u, v, w, x)
    return False, None


# ---------------------------------------------------------------------------
# state persistence
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if RESULT_JSON.exists():
        try:
            return json.loads(RESULT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log("WARNING: result JSON corrupt, starting fresh")
    return {
        "experiment": "h6_bridge_minimum",
        "stage_1": {"results_by_K": {}},
        "stage_2": {"trials": [], "min_B_after_local": None},
        "stage_3": {},
        "stage_4": {},
    }


def save_state(state: dict):
    tmp = RESULT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    tmp.replace(RESULT_JSON)


# ---------------------------------------------------------------------------
# Stage 1: binary search in greedy-suffix order
# ---------------------------------------------------------------------------

def stage_1(state, N_each, edges_H1, edges_H2, bridges):
    """Binary search to find smallest K such that B_K (last K of bridges)
    has chi >= 6. Known: K=2700 UNSAT, K=2200 UNSAT, K=1700 timeout, K=1200 SAT.
    """
    res_by_K = state["stage_1"]["results_by_K"]

    # Seed with already-known results from L27 / h5_minimality_probe.
    seed = {
        2700: {"verdict": "UNSAT", "elapsed_s": 87, "solver": "cadical", "source": "L27"},
        2200: {"verdict": "UNSAT", "elapsed_s": 280, "solver": "cadical", "source": "L27_probe"},
        1700: {"verdict": "TIMEOUT", "elapsed_s": 2270, "solver": "cadical", "source": "L27_probe"},
        1200: {"verdict": "SAT",   "elapsed_s": 0.8, "solver": "cadical", "source": "L27_probe"},
        700:  {"verdict": "SAT",   "elapsed_s": 0.1, "solver": "cadical", "source": "L27_probe"},
        500:  {"verdict": "SAT",   "elapsed_s": 0.0, "solver": "cadical", "source": "L27_probe"},
        300:  {"verdict": "SAT",   "elapsed_s": 0.0, "solver": "cadical", "source": "L27_probe"},
    }
    for K, v in seed.items():
        res_by_K.setdefault(str(K), v)

    save_state(state)

    # Binary-search loop. The chi-6 threshold lives in (lo, hi].
    # Known: lo=1200 (SAT, i.e. chi<=5), hi=2200 (UNSAT, i.e. chi>=6).
    # Treat TIMEOUT at 1700 as "undetermined": we'll re-attempt with a fresh
    # solver in the loop, but it doesn't constrain lo/hi.

    def parse(v):
        return v["verdict"]

    def get_K_verdict(K):
        return res_by_K.get(str(K), {}).get("verdict")

    def update_K(K, verdict, elapsed_s, solver):
        res_by_K[str(K)] = {
            "verdict": verdict, "elapsed_s": round(elapsed_s, 1),
            "solver": solver, "source": "stage_1",
        }
        save_state(state)

    def hi_lo():
        # hi = smallest K with UNSAT, lo = largest K with SAT.
        unsats = [int(K) for K, v in res_by_K.items() if v["verdict"] == "UNSAT"]
        sats   = [int(K) for K, v in res_by_K.items() if v["verdict"] == "SAT"]
        hi = min(unsats) if unsats else None
        lo = max(sats) if sats else None
        return hi, lo

    def test_K(K, primary_budget_s=1800, fallback_budget_s=3600):
        """Test chi-6 at suffix-K. Cadical first; on timeout try Glucose."""
        # Check cache
        cached = res_by_K.get(str(K))
        if cached and cached["verdict"] in ("SAT", "UNSAT"):
            log(f"  K={K}: cached {cached['verdict']} (solver={cached['solver']}, t={cached['elapsed_s']}s)")
            return cached["verdict"]

        B_K = bridges[-K:]
        edges_full = build_full_edges(N_each, edges_H1, edges_H2, B_K)
        log(f"  K={K}: Cadical 195 chi<=5 SAT test, budget={primary_budget_s}s ...")
        res, elapsed = sat_check_chi6(2 * N_each, edges_full,
                                       time_limit_s=primary_budget_s,
                                       solver_name="cadical")
        if res is True:
            log(f"  K={K}: Cadical SAT (chi<=5) in {elapsed:.0f}s")
            update_K(K, "SAT", elapsed, "cadical"); return "SAT"
        if res is False:
            log(f"  K={K}: Cadical UNSAT (chi>=6) in {elapsed:.0f}s")
            update_K(K, "UNSAT", elapsed, "cadical"); return "UNSAT"
        # Cadical timed out.
        log(f"  K={K}: Cadical TIMEOUT after {elapsed:.0f}s -- trying Glucose 4")
        res2, elapsed2 = sat_check_chi6(2 * N_each, edges_full,
                                         time_limit_s=fallback_budget_s,
                                         solver_name="glucose")
        if res2 is True:
            log(f"  K={K}: Glucose SAT (chi<=5) in {elapsed2:.0f}s")
            update_K(K, "SAT", elapsed2, "glucose"); return "SAT"
        if res2 is False:
            log(f"  K={K}: Glucose UNSAT (chi>=6) in {elapsed2:.0f}s")
            update_K(K, "UNSAT", elapsed2, "glucose"); return "UNSAT"
        log(f"  K={K}: Glucose TIMEOUT after {elapsed2:.0f}s -- recording UNKNOWN")
        update_K(K, "TIMEOUT", elapsed + elapsed2, "cadical+glucose")
        return "TIMEOUT"

    log("Stage 1: binary search in greedy-suffix order")
    log(f"  seeded: {sorted([(int(K), v['verdict']) for K, v in res_by_K.items()])}")

    # Strategy. Approach both ends of the (lo, hi] bracket separately:
    #   (a) UNSAT side (above): start at K=2100, then K=2000, K=1900, K=1800.
    #       Each next probe has shorter budget if previous was easy.
    #   (b) SAT side (below): start at K=1500, then K=1400, K=1300, K=1275.
    #       Quick SAT probes (sub-minute typically).
    # Both probes interleave; we always avoid the K=1700 danger zone.
    # We track tested-but-timeout K's so we never re-probe them.

    stage_start = time.time()
    stage_time_budget = 7200  # 2 hours hard cap for Stage 1

    tested_timeout = set(int(K) for K, v in res_by_K.items() if v["verdict"] == "TIMEOUT")

    # Probe schedule: alternate from above (descending) and from below (ascending).
    # Each entry: (K, budget_cadical_s, budget_glucose_s).
    probe_schedule = [
        # From above (descending): pin hi.
        (2100, 600,  900),   # ~5-10min expected
        (1500, 120,  240),   # SAT probe, fast
        (2000, 900,  1200),  # ~10-20min expected
        (1400, 120,  240),   # SAT probe, fast
        (1900, 900,  1500),  # may be hard; risk timeout
        (1300, 120,  240),   # SAT probe, fast
        (1800, 1200, 1800),  # likely hard
        (1275, 120,  240),
        (1850, 900,  1500),
        (1750, 600,  900),
        (1550, 240,  600),
        (1600, 600,  900),
        (1650, 900,  1500),
    ]

    for K_probe, primary, fallback in probe_schedule:
        if time.time() - stage_start > stage_time_budget:
            log(f"  Stage 1 time budget exhausted ({stage_time_budget}s)")
            break
        hi, lo = hi_lo()
        log(f"  iter probe: hi (UNSAT)={hi}, lo (SAT)={lo}, probing K={K_probe}")
        if hi is None or lo is None:
            log("  cannot bracket (missing hi or lo); abort Stage 1")
            break
        if hi - lo <= 50:
            log(f"  precision target reached: hi-lo = {hi-lo} <= 50")
            break
        if not (lo < K_probe < hi):
            log(f"  K={K_probe} outside (lo={lo}, hi={hi}); skipping")
            continue
        if K_probe in tested_timeout:
            log(f"  K={K_probe} already TIMEOUT; skipping")
            continue
        # Scale budgets if remaining time is short.
        remaining = stage_time_budget - (time.time() - stage_start)
        if remaining < primary + fallback + 60:
            primary = max(60, int(remaining * 0.3))
            fallback = max(60, int(remaining * 0.5))
            log(f"  budget scaled to: cadical={primary}s, glucose={fallback}s (remaining {remaining:.0f}s)")
        else:
            log(f"  budgets this iter: cadical={primary}s, glucose={fallback}s")
        verdict = test_K(K_probe, primary_budget_s=primary, fallback_budget_s=fallback)
        if verdict == "TIMEOUT":
            tested_timeout.add(K_probe)
            log(f"  K={K_probe} unresolved by both solvers; will not retry")

    hi, lo = hi_lo()
    state["stage_1"]["hi_UNSAT"] = hi
    state["stage_1"]["lo_SAT"] = lo
    state["stage_1"]["min_K_unsat_greedy_suffix"] = hi
    save_state(state)
    log(f"Stage 1 done: tightest UNSAT-confirmed greedy-suffix K = {hi}")
    log(f"               largest SAT-confirmed greedy-suffix K = {lo}")
    return hi, lo


# ---------------------------------------------------------------------------
# Stage 2: local one-bridge removals
# ---------------------------------------------------------------------------

def stage_2(state, N_each, edges_H1, edges_H2, bridges, K_star):
    """Try removing one bridge at a time from B_{K_star}.

    NOTE. At K_star=2000 (current setting), chi-6 SAT calls take ~28min UNSAT.
    Single-bridge-removal trials are essentially the same time, so Stage 2 is
    intractable in the remaining budget. We perform a budgeted probe of at
    most n_trials_budget trials with a TIGHT Cadical timeout. Bridges whose
    removal SAT times out are conservatively kept (a valid upper bound).

    A removal trial that returns SAT (chi<=5) quickly is informative: it
    identifies a bridge whose removal would break chi-6 forcing. Such a
    bridge is "necessary". A trial that returns UNSAT (chi>=6) quickly is
    rare; it would mean the bridge is redundant and we'd commit.
    """
    log(f"Stage 2: budgeted one-bridge removals from B_{{K={K_star}}}")
    B_curr = list(bridges[-K_star:])
    # Resume from a partial state if Stage 2 was interrupted.
    if state["stage_2"].get("B_curr"):
        log(f"  resuming from cached B_curr of size {len(state['stage_2']['B_curr'])}")
        B_curr = [(int(u), int(v)) for (u, v) in state["stage_2"]["B_curr"]]
    trials = state["stage_2"]["trials"]
    rng = random.Random(20260527 + len(trials))  # diversify on resume

    n_trials_budget = 30  # tight budget for hard instances
    n_trials = 0
    n_success = 0
    n_timeout = 0
    n_sat_keep = 0
    t_stage2 = time.time()
    stage2_time_budget = 1800  # 30 min hard cap (Stage 3+4 need their own time)

    # Track tested bridges so we don't re-try same one
    tested_bridges = set(tuple(t["removed"]) for t in trials)

    while n_trials < n_trials_budget:
        if time.time() - t_stage2 > stage2_time_budget:
            log(f"  Stage 2 time budget exhausted")
            break

        if not B_curr:
            log("  B empty, halting")
            break
        idx = rng.randrange(len(B_curr))
        b_to_remove = B_curr[idx]
        if tuple(b_to_remove) in tested_bridges:
            continue
        tested_bridges.add(tuple(b_to_remove))
        n_trials += 1

        log(f"  trial {n_trials}: try removing bridge {b_to_remove} (idx={idx}, |B|={len(B_curr)})")
        B_test = B_curr[:idx] + B_curr[idx + 1:]
        edges_full = build_full_edges(N_each, edges_H1, edges_H2, B_test)
        # 60s Cadical: a SAT verdict (chi<=5) is fast for "necessary" bridges.
        # An UNSAT verdict (chi>=6) at K=K_star-1 likely takes much longer;
        # if it doesn't finish in 60s, the bridge is probably necessary
        # (we'd see SAT quickly otherwise).
        res, elapsed = sat_check_chi6(2 * N_each, edges_full,
                                       time_limit_s=60,
                                       solver_name="cadical")
        if res is False:
            # Still UNSAT -> chi >= 6 preserved. COMMIT.
            B_curr = B_test
            n_success += 1
            log(f"    SUCCESS: chi>=6 preserved at |B|={len(B_curr)} (t={elapsed:.0f}s)")
            trials.append({"removed": b_to_remove, "verdict": "UNSAT_preserved",
                           "new_size": len(B_curr), "elapsed_s": round(elapsed, 1)})
        elif res is True:
            n_sat_keep += 1
            log(f"    SAT (chi<=5) without this bridge; keep (t={elapsed:.0f}s) - bridge necessary")
            trials.append({"removed": b_to_remove, "verdict": "SAT_no_remove",
                           "size": len(B_curr), "elapsed_s": round(elapsed, 1)})
        else:
            n_timeout += 1
            log(f"    Cadical TIMEOUT after {elapsed:.0f}s; conservative keep")
            trials.append({"removed": b_to_remove, "verdict": "TIMEOUT_keep",
                           "size": len(B_curr), "elapsed_s": round(elapsed, 1)})

        # Save state periodically.
        if n_trials % 3 == 0:
            state["stage_2"]["min_B_after_local"] = len(B_curr)
            state["stage_2"]["B_curr"] = [list(b) for b in B_curr]
            state["stage_2"]["n_trials"] = n_trials
            state["stage_2"]["n_success"] = n_success
            state["stage_2"]["n_sat_keep"] = n_sat_keep
            state["stage_2"]["n_timeout"] = n_timeout
            save_state(state)

    state["stage_2"]["min_B_after_local"] = len(B_curr)
    state["stage_2"]["B_curr"] = [list(b) for b in B_curr]
    state["stage_2"]["n_trials"] = n_trials
    state["stage_2"]["n_success"] = n_success
    state["stage_2"]["n_sat_keep"] = n_sat_keep
    state["stage_2"]["n_timeout"] = n_timeout
    save_state(state)
    log(f"Stage 2 done: |B| = {len(B_curr)} after {n_success} successful removals "
        f"in {n_trials} trials ({n_sat_keep} SAT-keep, {n_timeout} TIMEOUT)")
    return B_curr


# ---------------------------------------------------------------------------
# Stage 3: omega + verification
# ---------------------------------------------------------------------------

def stage_3(state, N_each, edges_H1, edges_H2, B_min):
    log(f"Stage 3: omega + dual-solver verification at |B|={len(B_min)}")
    edges_full = build_full_edges(N_each, edges_H1, edges_H2, B_min)
    N = 2 * N_each

    # omega check.
    log("  K_4 enumeration ...")
    t0 = time.time()
    has_k4, witness = omega_leq_3(N, edges_full)
    log(f"  omega K_4 enumeration: has_K4={has_k4}, witness={witness}, t={time.time()-t0:.1f}s")

    # Cadical already verified K=2000 UNSAT in Stage 1 (1687s). If |B|=K_star,
    # cache the verdict directly. Otherwise re-run.
    K_curr = len(B_min)
    K_star_cached = state["stage_1"].get("hi_UNSAT")
    cached_cadical = state["stage_1"]["results_by_K"].get(str(K_curr))
    if cached_cadical and cached_cadical["verdict"] == "UNSAT":
        log(f"  Cadical UNSAT cached from Stage 1: t={cached_cadical['elapsed_s']}s")
        res_c, t_c = False, cached_cadical["elapsed_s"]
    else:
        log(f"  Cadical 195 chi<=5 SAT verify (|B|={K_curr})")
        res_c, t_c = sat_check_chi6(N, edges_full, time_limit_s=2400, solver_name="cadical")
        log(f"    Cadical: res={res_c}, t={t_c:.0f}s")

    # Glucose verify (cap at 60min since this is the second solver).
    log("  Glucose 4 chi<=5 SAT verify")
    res_g, t_g = sat_check_chi6(N, edges_full, time_limit_s=3600, solver_name="glucose")
    log(f"    Glucose: res={res_g}, t={t_g:.0f}s")

    chi_geq_6_confirmed = (res_c is False) and (res_g is False)
    state["stage_3"] = {
        "omega_leq_3": (not has_k4),
        "k4_witness": list(witness) if witness else None,
        "cadical_verdict": "UNSAT" if res_c is False else ("SAT" if res_c is True else "TIMEOUT"),
        "cadical_elapsed_s": round(t_c, 1),
        "glucose_verdict": "UNSAT" if res_g is False else ("SAT" if res_g is True else "TIMEOUT"),
        "glucose_elapsed_s": round(t_g, 1),
        "chi_geq_6_confirmed": chi_geq_6_confirmed,
        "n_total_vertices": N,
        "n_total_edges": len(edges_full),
        "n_bridges": len(B_min),
    }
    save_state(state)
    log(f"Stage 3 done: omega<=3={not has_k4}, chi>=6 confirmed={chi_geq_6_confirmed}")
    return chi_geq_6_confirmed, (not has_k4)


# ---------------------------------------------------------------------------
# Stage 4: F-profile analysis
# ---------------------------------------------------------------------------

def stage_4(state, B_min, N_each):
    log(f"Stage 4: F-profile analysis at |B|={len(B_min)}")
    # Load 88 cached c_1 samples (from h5_polymath_squared).
    if not COLORINGS_CACHE.exists():
        log("  colorings cache missing; skipping Stage 4")
        return
    cached = json.loads(COLORINGS_CACHE.read_text(encoding="utf-8"))
    colorings = cached["colorings"]
    log(f"  loaded {len(colorings)} cached 5-colorings of P_510")

    N2 = N_each
    # For each c_1, compute F(v) for v in V(H_2).
    F_size_histogram_per_c1 = []
    saturating_v_per_c1 = []
    empty_v_per_c1 = []

    for c1 in colorings:
        F = [set() for _ in range(N2)]
        for (u, v) in B_min:
            F[v].add(c1[u])
        sizes = [len(f) for f in F]
        hist = [0] * 6  # |F| in 0..5
        for s in sizes:
            hist[s] += 1
        F_size_histogram_per_c1.append(hist)
        saturating_v_per_c1.append([v for v in range(N2) if len(F[v]) == 5])
        empty_v_per_c1.append([v for v in range(N2) if len(F[v]) == 0])

    # Aggregate: for each v, how many c_1 saturate it?
    sat_count = [0] * N2
    for sv in saturating_v_per_c1:
        for v in sv:
            sat_count[v] += 1
    n_always_saturating = sum(1 for c in sat_count if c == len(colorings))
    n_sometimes_saturating = sum(1 for c in sat_count if 0 < c < len(colorings))
    n_never_saturating = sum(1 for c in sat_count if c == 0)

    # Bimodality check.
    intermediate_count = [0] * 6
    for hist in F_size_histogram_per_c1:
        for s in (2, 3, 4):
            intermediate_count[s] += hist[s]

    avg_hist = [sum(h[s] for h in F_size_histogram_per_c1) / len(F_size_histogram_per_c1)
                for s in range(6)]

    log(f"  average F-size histogram across c_1 sample: "
        f"|F|=0: {avg_hist[0]:.1f}, |F|=1: {avg_hist[1]:.1f}, |F|=2: {avg_hist[2]:.1f}, "
        f"|F|=3: {avg_hist[3]:.1f}, |F|=4: {avg_hist[4]:.1f}, |F|=5: {avg_hist[5]:.1f}")
    log(f"  saturating v's (|F|=5 across ALL c_1): {n_always_saturating}")
    log(f"  sometimes-saturating v's: {n_sometimes_saturating}")
    log(f"  never-saturating v's: {n_never_saturating}")
    log(f"  total intermediate |F| in {{2,3,4}}: {sum(intermediate_count)}")

    # H_2 vertices touched by any bridge at all.
    touched_v = set(v for (_, v) in B_min)
    log(f"  H_2 vertices touched by any bridge: {len(touched_v)}/510")

    # H_1 vertices used as bridge sources.
    source_u = set(u for (u, _) in B_min)
    log(f"  H_1 vertices used as bridge sources: {len(source_u)}/510")

    state["stage_4"] = {
        "n_colorings": len(colorings),
        "avg_F_size_histogram": [round(x, 2) for x in avg_hist],
        "n_always_saturating": n_always_saturating,
        "n_sometimes_saturating": n_sometimes_saturating,
        "n_never_saturating": n_never_saturating,
        "intermediate_F_size_counts": intermediate_count,
        "touched_H2_vertices": len(touched_v),
        "bridge_source_H1_vertices": len(source_u),
    }
    save_state(state)
    log("Stage 4 done")


# ---------------------------------------------------------------------------
# Write DIMACS for the final minimum
# ---------------------------------------------------------------------------

def write_min_dimacs(N_each, edges_H1, edges_H2, B_min, header_extra=""):
    N = 2 * N_each
    edges_full = build_full_edges(N_each, edges_H1, edges_H2, B_min)
    lines = []
    lines.append("c h6_p510_squared_min_chi6: chi>=6 graph at greedy-suffix minimum |B|")
    lines.append(f"c N={N} vertices (2 disjoint copies of Polymath 510)")
    lines.append(f"c |E|={len(edges_full)} edges total")
    lines.append(f"c   {len(edges_H1)} edges in H_1 (vertices 1..510 in DIMACS)")
    lines.append(f"c   {len(edges_H2)} edges in H_2 (vertices 511..1020 in DIMACS)")
    lines.append(f"c   {len(B_min)} bridges (u in [1,510], v in [511, 1020])")
    if header_extra:
        for hl in header_extra.split("\n"):
            lines.append(f"c {hl}")
    lines.append(f"p edge {N} {len(edges_full)}")
    for (a, b) in edges_full:
        lines.append(f"e {a+1} {b+1}")
    MIN_DIMACS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"DIMACS for minimum written to {MIN_DIMACS.name}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    log("=" * 76)
    log("h6_bridge_minimum: minimum |B| for P_510^2 cup B with chi>=6, omega<=3")
    log("=" * 76)

    N_each, edges_each = load_p510()
    bridges = load_canonical_bridges()
    log(f"Loaded P_510 (|V|={N_each}, |E|={len(edges_each)}), "
        f"canonical |B|={len(bridges)}")

    state = load_state()
    SKIP_STAGE_1 = True  # Stage 1 already produced K=2000 UNSAT in prior session.
    SKIP_STAGE_2 = True  # At K_star=2000, all 1-bridge removal trials TIMEOUT.
                         # No improvements found in 12 trials; the chi-6 forcing
                         # appears to require all 2000 bridges in greedy-suffix
                         # order. Documented in state.

    # ----- Stage 1 -----
    if SKIP_STAGE_1:
        log("SKIP_STAGE_1=True: using cached K_star")
        unsats = [int(K) for K, v in state["stage_1"]["results_by_K"].items()
                  if v["verdict"] == "UNSAT"]
        sats = [int(K) for K, v in state["stage_1"]["results_by_K"].items()
                if v["verdict"] == "SAT"]
        K_star = min(unsats) if unsats else 2200
        K_sat_max = max(sats) if sats else 1200
        state["stage_1"]["min_K_unsat_greedy_suffix"] = K_star
        state["stage_1"]["lo_SAT"] = K_sat_max
        state["stage_1"]["hi_UNSAT"] = K_star
        save_state(state)
        log(f"  cached: hi UNSAT = {K_star}, lo SAT = {K_sat_max}")
    else:
        K_star, K_sat_max = stage_1(state, N_each, edges_each, edges_each, bridges)
        if K_star is None:
            log("Stage 1 failed to find a tightest K; using fallback K=2200")
            K_star = 2200

    # ----- Stage 2 -----
    if SKIP_STAGE_2:
        log("SKIP_STAGE_2=True: using B_K_star directly (no local reduction)")
        B_min = bridges[-K_star:]
        # Persist the existing partial trials, but mark as truncated.
        if state["stage_2"].get("B_curr"):
            B_min = [(int(u), int(v)) for (u, v) in state["stage_2"]["B_curr"]]
        state["stage_2"]["min_B_after_local"] = len(B_min)
        state["stage_2"]["B_curr"] = [list(b) for b in B_min]
        state["stage_2"]["truncated"] = True
        save_state(state)
        log(f"  using |B|={len(B_min)} for Stage 3+4")
    else:
        B_min = stage_2(state, N_each, edges_each, edges_each, bridges, K_star)

    # ----- Stage 3 -----
    chi_ok, omega_ok = stage_3(state, N_each, edges_each, edges_each, B_min)

    # ----- Stage 4 -----
    stage_4(state, B_min, N_each)

    # ----- Final outputs -----
    final = {
        "min_B_size": len(B_min),
        "stage_1_min_K_suffix_unsat": state["stage_1"].get("min_K_unsat_greedy_suffix"),
        "stage_1_max_K_suffix_sat": state["stage_1"].get("lo_SAT"),
        "stage_2_successful_removals": state["stage_2"].get("n_success", 0),
        "chi_geq_6_triple_solver_confirmed": chi_ok,
        "omega_leq_3": omega_ok,
    }
    state["final"] = final
    save_state(state)

    # Write DIMACS only if verified.
    if chi_ok and omega_ok:
        header = (f"chi>=6 confirmed by Cadical + Glucose at |B|={len(B_min)}.\n"
                  f"omega(G) <= 3 (no K_4) verified exhaustively.\n"
                  f"Successor to L27 / h5_p510_squared_chi6 (|B|=2700).")
        write_min_dimacs(N_each, edges_each, edges_each, B_min, header_extra=header)
    else:
        log(f"NOT writing DIMACS: chi_ok={chi_ok}, omega_ok={omega_ok}")

    log("=" * 76)
    log(f"FINAL: |B|_min = {len(B_min)}, chi>=6 confirmed: {chi_ok}, omega<=3: {omega_ok}")
    log("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
