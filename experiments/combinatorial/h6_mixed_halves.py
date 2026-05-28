r"""h6_mixed_halves: chi >= 6 search via two DISTINCT chi-5 halves H_1 != H_2 + bridges.

Architecture 1, Direction A (mixed-half chi-6 search). Generalization of
h5_polymath_squared.py from H_1 = H_2 = P_510 to two genuinely distinct
chi-5 UDG halves loaded from separate .edge files.

Motivation (L28 future direction 4). The L27/L28 result G = P_510 cup P_510 + B
(1020 vtx, |B| in (1500, 2000]) uses two IDENTICAL halves. Direction A asks
whether two DIFFERENT chi-5 halves H_1, H_2 joined by a no-K_4 bridge set B
can force chi >= 6 with:
  (a) fewer total vertices than 1020, and/or
  (b) a different algebraic field structure than P_510^2, and/or
  (c) comparable-or-fewer bridges.
Since every available half has >= 510 vertices, raw vertex count cannot beat
1020 for any PAIR; the honest win here is field-structure diversity and/or
bridge economy, NOT a smaller graph. We report this plainly.

Structural framing (carries over verbatim from L24/L27).
  For halves H_1, H_2 (both chi = 5, omega = 3) and bridge set
  B subseteq V(H_1) x V(H_2), define for each v in V(H_2):
    F(v) := {c_1(u) : (u, v) in B} subseteq [5],
    L(v) := [5] \ F(v).
  Then chi(H_1 cup H_2 cup B) >= 6
       iff for EVERY proper 5-coloring c_1 of H_1, H_2 is not
       list-5-colorable from L.

Usage:
  python h6_mixed_halves.py --h1 510 --h2 517
  python h6_mixed_halves.py --h1 510 --h2 553
  python h6_mixed_halves.py --h1 510 --h2 826

Stages (budgeted, checkpointed):
  A. Sample N_SAMPLES proper 5-colorings of H_1 only (H_2 is never sampled).
  B. Precompute u-color table + entropy over the c_1 sample for H_1 vertices.
  C. Iterated greedy + adversarial augmentation bridge cover with no-K_4.
  D. Full SAT chi <= 5 on the combined graph; UNSAT => chi >= 6.

Outputs (per-pair, suffixed by the pair tag e.g. _510x517):
  _cache/h6mix_<tag>_h1_5colorings.json
  _cache/h6mix_<tag>_summary.json
  _cache/h6mix_<tag>_search_log.json
  _cache/h6mix_<tag>.log
  _cache/h6mix_<tag>_graph.json   (full combined graph if chi >= 6 found)
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
import sys
import time

from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)
EDGE_DIR = REPO_ROOT / "sources" / "cnp-sat" / "edge"

# Set per-run in main() once the pair tag is known.
_LOG_PATH = None


def log(msg: str):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    if _LOG_PATH is not None:
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    print(line, flush=True)


# =========================================================================
# Load a half from an .edge file
# =========================================================================

def parse_edge_file(path: pathlib.Path):
    edges = []
    n = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("p"):
            n = int(line.split()[2])
        elif line.startswith("e"):
            parts = line.split()
            edges.append((int(parts[1]) - 1, int(parts[2]) - 1))
    return n, edges


def load_half(tag: str):
    path = EDGE_DIR / f"{tag}.edge"
    if not path.exists():
        raise FileNotFoundError(f"No edge file for half '{tag}': {path}")
    n, edges = parse_edge_file(path)
    return n, edges


# =========================================================================
# SAT machinery (k-coloring)
# =========================================================================

def k_color_clauses(N, edges, k, vertex_perm=None, color_perm=None, shuffle_rng=None):
    if vertex_perm is None:
        vertex_perm = list(range(N))
    if color_perm is None:
        color_perm = list(range(k))

    def var(v, c):
        return vertex_perm[v] * k + color_perm[c] + 1

    clauses = []
    for v in range(N):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])

    if shuffle_rng is not None:
        shuffle_rng.shuffle(clauses)
    return clauses, var


def sat_k_color(N, edges, k, time_limit=None, vertex_perm=None,
                color_perm=None, shuffle_rng=None, return_model=False):
    clauses, var = k_color_clauses(N, edges, k, vertex_perm=vertex_perm,
                                   color_perm=color_perm, shuffle_rng=shuffle_rng)
    t0 = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        if time_limit is not None:
            solver.conf_budget(int(time_limit * 50000))
            sat = solver.solve_limited(expect_interrupt=False)
        else:
            sat = solver.solve()
        elapsed = time.time() - t0
        if sat and return_model:
            model = solver.get_model()
            coloring = [None] * N
            for v in range(N):
                for c in range(k):
                    if model[var(v, c) - 1] > 0:
                        coloring[v] = c
                        break
            return sat, coloring, elapsed
        return sat, None, elapsed


# =========================================================================
# Stage A: sample diverse 5-colorings of H_1
# =========================================================================

def canonicalize_coloring(coloring, k):
    remap = {}
    nxt = 0
    out = []
    for c in coloring:
        if c not in remap:
            remap[c] = nxt
            nxt += 1
        out.append(remap[c])
    return tuple(out)


def sample_5colorings(N, edges, target_count=80, seed=20260528, time_limit=600):
    rng = random.Random(seed)
    seen = set()
    colorings = []
    t_start = time.time()
    n_attempts = 0
    n_distinct = 0
    n_consec_dups = 0
    log(f"Stage A: sampling {target_count} distinct canonical 5-colorings of H_1 (N={N})")
    while n_distinct < target_count:
        if time.time() - t_start > time_limit:
            log(f"  time limit hit at {n_distinct} colorings")
            break
        n_attempts += 1
        vp = list(range(N)); rng.shuffle(vp)
        cp = list(range(5)); rng.shuffle(cp)
        sh = random.Random(rng.randint(0, 10**9))
        sat, coloring, t_sat = sat_k_color(N, edges, 5, vertex_perm=vp,
                                           color_perm=cp, shuffle_rng=sh,
                                           return_model=True)
        if not sat:
            log("  ERROR: H_1 5-coloring returned UNSAT (half should be chi=5, SAT for k=5)")
            break
        canon = canonicalize_coloring(coloring, 5)
        if canon in seen:
            n_consec_dups += 1
            if n_consec_dups >= 30:
                log(f"  early stop: 30 consecutive duplicates, final count {n_distinct}")
                break
            continue
        seen.add(canon)
        colorings.append(list(canon))
        n_distinct += 1
        n_consec_dups = 0
        if n_distinct % 10 == 0:
            log(f"  sampled {n_distinct}/{target_count} (attempts={n_attempts}, "
                f"t_sat_last={t_sat:.2f}s)")
    log(f"Stage A complete: {len(colorings)} distinct colorings, "
        f"elapsed={time.time()-t_start:.0f}s")
    return colorings


# =========================================================================
# Stage B: u-color table + entropy over H_1
# =========================================================================

def entropy(profile):
    total = sum(profile)
    if total == 0:
        return 0.0
    h = 0.0
    for n in profile:
        if n:
            p = n / total
            h -= p * math.log2(p)
    return h


def build_u_profile(N1, colorings):
    S = len(colorings)
    u_color_table = [[c1[u] for c1 in colorings] for u in range(N1)]
    u_profile = [[0] * 5 for _ in range(N1)]
    for u in range(N1):
        for s in range(S):
            u_profile[u][u_color_table[u][s]] += 1
    u_entropy = [entropy(u_profile[u]) for u in range(N1)]
    log(f"Stage B: u_entropy range [{min(u_entropy):.3f}, {max(u_entropy):.3f}], "
        f"high-entropy(>2.0) count={sum(1 for e in u_entropy if e > 2.0)}")
    return u_color_table, u_entropy


# =========================================================================
# no-K_4 machinery
# =========================================================================

def compute_adj(N1, N2, edges_H1, edges_H2, B):
    N = N1 + N2
    adj = [set() for _ in range(N)]
    for (u, v) in edges_H1:
        adj[u].add(v); adj[v].add(u)
    for (u, v) in edges_H2:
        adj[N1 + u].add(N1 + v); adj[N1 + v].add(N1 + u)
    for (u, v) in B:
        adj[u].add(N1 + v); adj[N1 + v].add(u)
    return adj


def adj_add_bridge(adj, u, v_global):
    adj[u].add(v_global); adj[v_global].add(u)


def creates_K4(adj, u, v_global):
    common = adj[u] & adj[v_global]
    if len(common) < 2:
        return False
    common = sorted(common)
    for i in range(len(common)):
        adj_c1 = adj[common[i]]
        for j in range(i + 1, len(common)):
            if common[j] in adj_c1:
                return True
    return False


# =========================================================================
# Residual list-coloring feasibility on H_2
# =========================================================================

def list_color_feasible(N, edges, L, time_limit=30):
    for v in range(N):
        if not L[v]:
            return False
    var_map = {}
    nv = 1
    for v in range(N):
        for c in L[v]:
            var_map[(v, c)] = nv
            nv += 1
    clauses = []
    for v in range(N):
        lits = [var_map[(v, c)] for c in L[v]]
        clauses.append(lits)
        for i in range(len(L[v])):
            for j in range(i + 1, len(L[v])):
                clauses.append([-var_map[(v, L[v][i])], -var_map[(v, L[v][j])]])
    for (u, v) in edges:
        for c in set(L[u]) & set(L[v]):
            clauses.append([-var_map[(u, c)], -var_map[(v, c)]])
    with Cadical195(bootstrap_with=clauses) as solver:
        if time_limit is not None:
            solver.conf_budget(int(time_limit * 50000))
            res = solver.solve_limited(expect_interrupt=False)
        else:
            res = solver.solve()
        return None if res is None else bool(res)


def compute_L_from_B(B, c1, N2):
    F = [set() for _ in range(N2)]
    for (u, v) in B:
        F[v].add(c1[u])
    return [sorted(set(range(5)) - f) for f in F]


def count_infeasible_c1(B, colorings, N2, edges_H2, time_limit_per=20):
    n_inf = n_feas = n_to = 0
    for c1 in colorings:
        L = compute_L_from_B(B, c1, N2)
        if any(not l for l in L):
            n_inf += 1
            continue
        res = list_color_feasible(N2, edges_H2, L, time_limit=time_limit_per)
        if res is None:
            n_to += 1
        elif not res:
            n_inf += 1
        else:
            n_feas += 1
    return n_inf, n_feas, n_to


# =========================================================================
# Stage C: greedy bridge cover (marginal F-gain, no-K_4) -- two distinct halves
# =========================================================================

def greedy_bridge_cover(N1, edges_H1, N2, edges_H2, colorings,
                        u_color_table, u_entropy,
                        max_bridges=2000, no_k4=True, time_limit=10800,
                        sat_check_every=300, sat_time_limit=600,
                        candidate_pool_size=120, initial_B=None):
    log(f"Stage C: greedy (max={max_bridges}, pool={candidate_pool_size})")
    t_start = time.time()
    S = len(colorings)
    F_state = [[0] * N2 for _ in range(S)]
    F_size = [[0] * N2 for _ in range(S)]
    used = set()
    adj = compute_adj(N1, N2, edges_H1, edges_H2, [])

    u_ranked = sorted(range(N1), key=lambda u: -u_entropy[u])
    u_pool = u_ranked[:candidate_pool_size]
    kill_mask = {}
    for u in u_pool:
        kill_mask[u] = [1 << u_color_table[u][s] for s in range(S)]
    if initial_B:
        for (u, v) in initial_B:
            if u not in kill_mask:
                kill_mask[u] = [1 << u_color_table[u][s] for s in range(S)]

    B = []
    history = []
    n_skipped_k4 = 0
    n_added = 0

    if initial_B:
        for (u, v) in initial_B:
            vg = N1 + v
            adj_add_bridge(adj, u, vg)
            B.append((u, v)); used.add((u, v)); n_added += 1
            for s in range(S):
                kms = kill_mask[u][s]
                if not (F_state[s][v] & kms):
                    F_state[s][v] |= kms
                    F_size[s][v] += 1
        log(f"  re-applied initial_B: |B|={len(B)}")

    candidates = [(u, v) for u in u_pool for v in range(N2)]
    log(f"  candidate (u,v) pool size: {len(candidates)}")

    deg_H2 = [0] * N2
    for (a, b) in edges_H2:
        deg_H2[a] += 1; deg_H2[b] += 1
    target_set = set(sorted(range(N2), key=lambda v: deg_H2[v])[:30])

    while n_added < max_bridges:
        if time.time() - t_start > time_limit:
            log("  time limit reached")
            break
        v_progress = [sum(F_size[s][v] for s in range(S)) for v in range(N2)]
        best_score = -1
        best_uv = None
        best_gain = 0
        for (u, v) in candidates:
            if (u, v) in used:
                continue
            km = kill_mask[u]
            gain = 0; sat_sam = 0; sub_sat = 0
            for s in range(S):
                kms = km[s]
                if not (F_state[s][v] & kms):
                    gain += 1
                    nsz = F_size[s][v] + 1
                    if nsz == 5:
                        sat_sam += 1
                    elif nsz == 4:
                        sub_sat += 1
            if gain == 0:
                continue
            score = (sat_sam * 100000 + sub_sat * 1000
                     + (500 if v in target_set else 0)
                     + gain * 10 + v_progress[v])
            if score > best_score:
                best_score = score; best_uv = (u, v); best_gain = gain
        if best_uv is None or best_gain <= 0:
            log("  no positive-gain candidate; stopping greedy")
            break
        u, v = best_uv
        vg = N1 + v
        if no_k4 and creates_K4(adj, u, vg):
            n_skipped_k4 += 1
            used.add((u, v))
            continue
        adj_add_bridge(adj, u, vg)
        used.add((u, v)); B.append((u, v))
        for s in range(S):
            kms = kill_mask[u][s]
            if not (F_state[s][v] & kms):
                F_state[s][v] |= kms
                F_size[s][v] += 1
        n_added += 1
        empty_inf = sum(1 for s in range(S) if any(F_size[s][vv] == 5 for vv in range(N2)))
        history.append({"step": n_added, "added": [u, v], "gain": best_gain,
                        "emptylist_infeasible_count": empty_inf,
                        "n_skipped_k4": n_skipped_k4})
        if n_added % 50 == 0:
            el = time.time() - t_start
            log(f"  step {n_added}: |B|={len(B)}, last_gain={best_gain}, "
                f"emptylist={empty_inf}/{S}, skippedK4={n_skipped_k4}, "
                f"elapsed={el:.0f}s ({n_added/(el+0.001):.2f}/s)")
        if n_added % sat_check_every == 0 and empty_inf == S:
            n_inf, n_feas, n_to = count_infeasible_c1(B, colorings, N2, edges_H2,
                                                      time_limit_per=20)
            log(f"  step {n_added}: residual infeas={n_inf}, feas={n_feas}, to={n_to}/{S}")
            if n_feas == 0:
                log(f"  SAMPLE-level all-infeasible at |B|={len(B)}; full SAT check.")
                edges_full = (list(edges_H1)
                              + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                              + [(a, N1 + b) for (a, b) in B])
                sat, _, t_sat = sat_k_color(N1 + N2, edges_full, 5, time_limit=sat_time_limit)
                log(f"  full SAT 5-coloring: sat={sat}, t={t_sat:.0f}s")
                if sat is False:
                    log(f"  !!! CHI >= 6 CONFIRMED at |B|={len(B)}")
                    return B, history, "chi_geq_6"
                elif sat is True:
                    return B, history, "sample_incomplete"
    log(f"Stage C done: |B|={len(B)}, skippedK4={n_skipped_k4}, "
        f"time={time.time()-t_start:.0f}s")
    return B, history, "exhausted"


# =========================================================================
# Adversarial augmentation
# =========================================================================

def find_adversary_c1(N1, edges_H1, N2, edges_H2, B, time_limit=300):
    edges_full = (list(edges_H1)
                  + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                  + [(a, N1 + b) for (a, b) in B])
    sat, coloring, _ = sat_k_color(N1 + N2, edges_full, 5,
                                   time_limit=time_limit, return_model=True)
    if sat:
        return canonicalize_coloring(list(coloring[:N1]), 5)
    return None


def greedy_with_adversarial_aug(N1, edges_H1, N2, edges_H2, colorings,
                                u_color_table, u_entropy,
                                max_bridges=4000, no_k4=True, time_limit=11000,
                                sat_check_every=300, sat_time_limit=600,
                                candidate_pool_size=120, max_adversary_rounds=30):
    log("Stage C+: iterated greedy with adversarial augmentation")
    t_start = time.time()
    colorings = list(colorings)
    aggregated_B = []
    history_all = []
    aug_round = 0
    n_consec_dup = 0

    while aug_round < max_adversary_rounds:
        aug_round += 1
        log(f"=== Adversary round {aug_round}/{max_adversary_rounds}, "
            f"sample size {len(colorings)} ===")
        new_u_color_table = [[c1[u] for c1 in colorings] for u in range(N1)]
        S = len(colorings)
        u_profile = [[0] * 5 for _ in range(N1)]
        for u in range(N1):
            for s in range(S):
                u_profile[u][new_u_color_table[u][s]] += 1
        new_u_entropy = [entropy(u_profile[u]) for u in range(N1)]

        elapsed_so_far = time.time() - t_start
        remaining = time_limit - elapsed_so_far
        if remaining < 60:
            log("  global budget exhausted")
            break
        per_round = min(remaining * 0.4, 600)
        round_max = max(max_bridges, len(aggregated_B) + 200)
        B_round, hist_round, verdict_round = greedy_bridge_cover(
            N1, edges_H1, N2, edges_H2, colorings,
            new_u_color_table, new_u_entropy, max_bridges=round_max,
            no_k4=no_k4, time_limit=per_round, sat_check_every=sat_check_every,
            sat_time_limit=sat_time_limit, candidate_pool_size=candidate_pool_size,
            initial_B=aggregated_B)
        aggregated_B = B_round
        for h in hist_round:
            h["aug_round"] = aug_round
            history_all.append(h)
        log(f"  round {aug_round} verdict: {verdict_round}, |B|={len(aggregated_B)}")
        if verdict_round == "chi_geq_6":
            return aggregated_B, history_all, "chi_geq_6", colorings

        log(f"  searching for adversary c_1 (|B|={len(aggregated_B)})...")
        t_adv = time.time()
        adv_c1 = find_adversary_c1(N1, edges_H1, N2, edges_H2, aggregated_B,
                                   time_limit=min(300, remaining - 30))
        log(f"  adversary: {'FOUND' if adv_c1 else 'NOT FOUND'} in {time.time()-t_adv:.0f}s")
        if adv_c1 is None:
            log("  no adversary found - confirming chi >= 6 via full SAT")
            sat, _, _ = sat_k_color(
                N1 + N2,
                list(edges_H1) + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                + [(a, N1 + b) for (a, b) in aggregated_B],
                5, time_limit=min(900, remaining))
            if sat is False:
                return aggregated_B, history_all, "chi_geq_6", colorings
            elif sat is True:
                return aggregated_B, history_all, "inconsistent", colorings
            else:
                return aggregated_B, history_all, "sat_timeout", colorings
        adv_c1 = list(adv_c1)
        if any(list(c) == adv_c1 for c in colorings):
            n_consec_dup += 1
            log(f"  adversary duplicate (#{n_consec_dup})")
            if n_consec_dup >= 5:
                return aggregated_B, history_all, "adversary_duplicate", colorings
            edges_full = (list(edges_H1)
                          + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                          + [(a, N1 + b) for (a, b) in aggregated_B])
            found = False
            for retry in range(5):
                vp = list(range(N1 + N2))
                rng = random.Random(20260528 + aug_round * 100 + retry)
                rng.shuffle(vp)
                cp = list(range(5)); rng.shuffle(cp)
                sh = random.Random(rng.randint(0, 10**9))
                sat, model, _ = sat_k_color(N1 + N2, edges_full, 5, return_model=True,
                                            vertex_perm=vp, color_perm=cp,
                                            shuffle_rng=sh, time_limit=120)
                if sat and model:
                    cand = list(canonicalize_coloring(list(model[:N1]), 5))
                    if not any(list(c) == cand for c in colorings):
                        adv_c1 = cand; found = True
                        log("  found fresh adversary via shuffled SAT")
                        break
            if not found:
                log("  failed to find fresh adversary even with shuffling")
                continue
            n_consec_dup = 0
        colorings.append(adv_c1)
        log(f"  added adversary c_1 (new sample size {len(colorings)})")
        n_consec_dup = 0

    log("Max adversary rounds reached")
    return aggregated_B, history_all, "max_rounds", colorings


# =========================================================================
# Stage D + main
# =========================================================================

def full_sat_verification(N1, edges_H1, N2, edges_H2, B, time_limit=1800):
    log(f"Stage D: full SAT chi<=5 on N={N1+N2}, "
        f"|E|={len(edges_H1)+len(edges_H2)+len(B)}")
    edges_full = (list(edges_H1)
                  + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                  + [(a, N1 + b) for (a, b) in B])
    sat, _, elapsed = sat_k_color(N1 + N2, edges_full, 5, time_limit=time_limit)
    log(f"  SAT chi<=5: {sat} "
        f"({'SAT (chi<=5)' if sat else 'UNSAT (chi>=6 !!!)' if sat is False else 'timeout'}) "
        f"elapsed={elapsed:.0f}s")
    return sat, elapsed


def main():
    global _LOG_PATH
    ap = argparse.ArgumentParser()
    ap.add_argument("--h1", required=True, help="tag of first half (e.g. 510)")
    ap.add_argument("--h2", required=True, help="tag of second half (e.g. 517)")
    ap.add_argument("--samples", type=int, default=80)
    ap.add_argument("--sample-time", type=int, default=600)
    ap.add_argument("--time-limit", type=int, default=11000)
    ap.add_argument("--max-bridges", type=int, default=4000)
    ap.add_argument("--adversary-rounds", type=int, default=30)
    args = ap.parse_args()

    tag = f"{args.h1}x{args.h2}"
    _LOG_PATH = CACHE / f"h6mix_{tag}.log"
    colorings_cache = CACHE / f"h6mix_{tag}_h1_5colorings.json"
    summary_path = CACHE / f"h6mix_{tag}_summary.json"
    search_log = CACHE / f"h6mix_{tag}_search_log.json"
    graph_path = CACHE / f"h6mix_{tag}_graph.json"

    log("=" * 76)
    log(f"h6_mixed_halves: chi>=6 search, H_1={args.h1}, H_2={args.h2}")
    log("=" * 76)

    N1, edges_H1 = load_half(args.h1)
    N2, edges_H2 = load_half(args.h2)
    log(f"Loaded H_1={args.h1}: |V|={N1}, |E|={len(edges_H1)}")
    log(f"Loaded H_2={args.h2}: |V|={N2}, |E|={len(edges_H2)}")
    log(f"Combined |V|={N1+N2} (baseline L27/L28: 1020)")

    # Stage A
    if colorings_cache.exists():
        colorings = json.loads(colorings_cache.read_text())["colorings"]
        log(f"Stage A: loaded {len(colorings)} cached colorings")
    else:
        colorings = sample_5colorings(N1, edges_H1, target_count=args.samples,
                                      seed=20260528, time_limit=args.sample_time)
        colorings_cache.write_text(json.dumps({
            "h1_tag": args.h1, "n_vertices": N1, "n_edges": len(edges_H1),
            "n_colorings": len(colorings),
            "canonicalized": "S_5_first_appearance",
            "colorings": colorings}, indent=1))
        log(f"  cached {len(colorings)} colorings")
    if len(colorings) < 5:
        log("Too few colorings; aborting")
        return 1

    # Stage B
    u_color_table, u_entropy = build_u_profile(N1, colorings)

    # Stage C
    best_B, history, verdict_C, colorings_final = greedy_with_adversarial_aug(
        N1, edges_H1, N2, edges_H2, colorings, u_color_table, u_entropy,
        max_bridges=args.max_bridges, no_k4=True, time_limit=args.time_limit,
        sat_check_every=300, sat_time_limit=600, candidate_pool_size=120,
        max_adversary_rounds=args.adversary_rounds)
    colorings = colorings_final
    log(f"Stage C verdict: {verdict_C}, final |B|={len(best_B)}, "
        f"|colorings|={len(colorings)}")

    # Stage D
    if verdict_C == "chi_geq_6":
        sat, elapsed = full_sat_verification(N1, edges_H1, N2, edges_H2, best_B,
                                             time_limit=1800)
        final_verdict = ("CHI_6_CONFIRMED" if sat is False
                         else "CHI_5_DESPITE_LIST_INFEAS" if sat is True
                         else "SAT_TIMEOUT")
        if sat is False:
            # Persist the full combined graph for VERIFIER/ADVERSARY.
            graph_path.write_text(json.dumps({
                "h1_tag": args.h1, "h2_tag": args.h2,
                "N1": N1, "N2": N2, "N_total": N1 + N2,
                "edges_H1": edges_H1, "edges_H2": edges_H2,
                "B": best_B, "B_size": len(best_B)}, indent=1))
            log(f"  combined chi>=6 graph written to {graph_path.name}")
    else:
        if best_B:
            sat, elapsed = full_sat_verification(N1, edges_H1, N2, edges_H2, best_B,
                                                 time_limit=900)
            final_verdict = ("NO_CHI_6_FOUND_SAT_HOLDS" if sat is True
                             else "UNEXPECTED_UNSAT" if sat is False
                             else "SAT_TIMEOUT")
        else:
            sat, elapsed = True, 0.0
            final_verdict = "NO_BRIDGES_ADDED"

    # empty-list infeasibility tally on final sample
    n_empty_list = 0
    if best_B:
        for c1 in colorings:
            F = [set() for _ in range(N2)]
            for (u, v) in best_B:
                F[v].add(c1[u])
            if any(len(f) == 5 for f in F):
                n_empty_list += 1

    summary = {
        "experiment": "h6_mixed_halves",
        "h1_tag": args.h1, "h2_tag": args.h2,
        "N1": N1, "N2": N2, "N_total": N1 + N2,
        "n_edges_H1": len(edges_H1), "n_edges_H2": len(edges_H2),
        "baseline_L27_vertices": 1020,
        "baseline_L28_bridges_upper": 2000,
        "n_colorings_final": len(colorings),
        "best_B_size": len(best_B),
        "verdict_stage_C": verdict_C,
        "verdict_final": final_verdict,
        "sat_check_result": sat,
        "sat_check_elapsed_s": round(elapsed, 1),
        "n_empty_list_on_sample": n_empty_list,
        "history_length": len(history),
        "best_B": best_B,
    }
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    search_log.write_text(json.dumps({"history": history}, indent=1))
    log("=" * 76)
    log(f"FINAL VERDICT [{tag}]: {final_verdict}  |B|={len(best_B)}  "
        f"empty-list {n_empty_list}/{len(colorings)}")
    log("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
