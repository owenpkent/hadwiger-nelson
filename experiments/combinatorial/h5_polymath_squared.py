r"""h5_polymath_squared: Search for a chi >= 6 UDG candidate via P510 x P510 + bridges.

Architecture 1, long-job H5. BUILDER pass on the L24 triple-coupling theorem
specialized to two chi-5 halves at the 5-color level (the natural recursive next
rung on the L21/L22 covering ladder).

Goal. Find a no-K_4 bridge set B subseteq V(P_510) x V(P_510) between two
disjoint copies of Polymath 510 such that chi(P_510 cup P_510 cup B) >= 6.
If found and UDG-realizable, this is a CHI-6 UDG record (an open problem
since the Hadwiger-Nelson lower bound passed 5 in 2018).

Structural framing (L24 lift at the chi-5 level).
  Let H_1 = H_2 = P_510. For bridge set B subseteq V(H_1) x V(H_2), define
    F(v) := {c_1(u) : (u,v) in B} subseteq [5],   v in V(H_2),
    L(v) := [5] \ F(v).
  Then:
    chi(H_1 cup H_2 cup B) >= 6
      iff
    for every proper 5-coloring c_1 of H_1, H_2 is not list-5-colorable from L.

  Since chi(H_2) = 5, the residual is feasible when L(v) = [5] everywhere; the
  bridges must shrink L enough to break list-extensibility universally.

Constraints.
  1. no-K_4: omega(H_1 cup H_2 cup B) <= 3. Both halves have omega = 3
     internally; bridges must avoid creating K_4 cross-cliques.
  2. chi >= 6 forcing: validated by SAT on the full combined graph (N = 1020).

Method (multi-stage, budgeted).
  Stage A. Load P_510 vertices and edges. Sample 50-200 random proper
           5-colorings via diverse SAT seeds + clause shuffling. Canonicalize
           mod S_5. Cache.
  Stage B. For each candidate bridge (u, v) in V(H_1) x V(H_2):
             - compute the "kill vector": for each cached c_1, the color
               c_1(u) added to F(v).
             - score: diversity of colors added to L(v) across the c_1 sample.
           Apply no-K_4 filter.
  Stage C. Greedy + local-search bridge cover. Start with B = []. Add the
           highest-scoring bridge that doesn't create K_4 and increases the
           # of c_1's with list-uncolorable residual. SAT-check chi periodically.
  Stage D. SAT verification on the full combined graph (1020 vertices) using
           cadical with aggressive time-outs.

Output.
  - _cache/h5_p510_5colorings.json: sampled proper 5-colorings.
  - _cache/h5_bridge_scores.json: bridge candidates + diversity scores.
  - _cache/h5_search_log.json: search history.
  - _cache/h5_summary.json: final verdict + best B tested.

Aggressive time-outs: no single SAT verification exceeds 30 min. The script
checkpoints between stages so resumption is possible.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import random
import sys
import time
from typing import Optional

from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

EDGE_PATH = REPO_ROOT / "sources" / "cnp-sat" / "edge" / "510.edge"

COLORINGS_CACHE = CACHE / "h5_p510_5colorings.json"
SCORES_CACHE = CACHE / "h5_bridge_scores.json"
SEARCH_LOG = CACHE / "h5_search_log.json"
SUMMARY_PATH = CACHE / "h5_summary.json"
LOG_PATH = CACHE / "h5_polymath_squared.log"


# =========================================================================
# Logging
# =========================================================================

def log(msg: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


# =========================================================================
# Load P_510
# =========================================================================

def parse_edge_file(path: pathlib.Path):
    edges = []
    n = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("p"):
            parts = line.split()
            n = int(parts[2])
            continue
        if line.startswith("c"):
            continue
        if line.startswith("e"):
            parts = line.split()
            edges.append((int(parts[1]) - 1, int(parts[2]) - 1))
    return n, edges


def load_p510():
    n, edges = parse_edge_file(EDGE_PATH)
    assert n == 510, f"Expected 510 vertices, got {n}"
    assert len(edges) == 2504, f"Expected 2504 edges, got {len(edges)}"
    return n, edges


# =========================================================================
# SAT machinery (k-coloring)
# =========================================================================

def k_color_clauses(N, edges, k, vertex_perm=None, color_perm=None, shuffle_rng=None):
    """Generate CNF for the k-coloring problem on graph (N, edges).

    Returns (clauses, var_of) where var_of(v, c) -> variable id (1-indexed).

    vertex_perm, color_perm let us inject randomness by remapping internal
    variable order. shuffle_rng additionally shuffles clause order.
    """
    if vertex_perm is None:
        vertex_perm = list(range(N))
    if color_perm is None:
        color_perm = list(range(k))

    def var(v, c):
        return vertex_perm[v] * k + color_perm[c] + 1

    clauses = []
    # At least one color per vertex.
    for v in range(N):
        clauses.append([var(v, c) for c in range(k)])
        # At most one color per vertex.
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    # No two adjacent vertices share a color.
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])

    if shuffle_rng is not None:
        # Shuffle clauses (within reason) to perturb the solver's search.
        shuffle_rng.shuffle(clauses)

    return clauses, var


def sat_k_color(N, edges, k, time_limit=None, vertex_perm=None,
                color_perm=None, shuffle_rng=None, return_model=False):
    """SAT check whether graph (N, edges) is k-colorable.

    Returns (sat, coloring_or_None, elapsed_s).
    """
    clauses, var = k_color_clauses(N, edges, k,
                                    vertex_perm=vertex_perm,
                                    color_perm=color_perm,
                                    shuffle_rng=shuffle_rng)
    t0 = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        if time_limit is not None:
            # Cadical supports conflict budget rather than wall clock.
            # Convert: assume ~10000 conflicts/sec heuristically.
            solver.conf_budget(int(time_limit * 50000))
            sat = solver.solve_limited(expect_interrupt=False)
        else:
            sat = solver.solve()
        elapsed = time.time() - t0
        if sat and return_model:
            model = solver.get_model()
            # Decode coloring.
            coloring = [None] * N
            for v in range(N):
                for c in range(k):
                    lit = var(v, c)
                    if model[lit - 1] > 0:
                        coloring[v] = c
                        break
            return sat, coloring, elapsed
        return sat, None, elapsed


# =========================================================================
# Stage A: sample diverse 5-colorings of P_510
# =========================================================================

def canonicalize_coloring(coloring, k):
    """Canonicalize a k-coloring mod S_k: relabel colors in order of first
    appearance so the first vertex gets color 0, etc.
    """
    remap = {}
    next_color = 0
    out = []
    for c in coloring:
        if c not in remap:
            remap[c] = next_color
            next_color += 1
        out.append(remap[c])
    return tuple(out)


def sample_5colorings(N, edges, target_count=80, seed=20260527,
                      time_limit=1800):
    """Sample distinct proper 5-colorings of P_510 via SAT with randomized
    variable order + clause shuffling. Canonicalize mod S_5 before dedup.

    Returns list of canonical tuples.
    """
    rng = random.Random(seed)
    seen = set()  # canonical coloring tuples
    colorings = []  # raw colorings (preserving variety in original form)
    t_start = time.time()
    n_attempts = 0
    n_distinct = 0
    n_consecutive_dups = 0

    log(f"Stage A: sampling {target_count} distinct canonical 5-colorings of P_510")

    while n_distinct < target_count:
        elapsed = time.time() - t_start
        if elapsed > time_limit:
            log(f"  time limit hit at {n_distinct} colorings after {elapsed:.0f}s")
            break
        n_attempts += 1

        # Randomize variable order + color order + clause shuffle.
        vertex_perm = list(range(N))
        rng.shuffle(vertex_perm)
        color_perm = list(range(5))
        rng.shuffle(color_perm)
        shuffle_rng = random.Random(rng.randint(0, 10**9))

        sat, coloring, t_sat = sat_k_color(
            N, edges, 5, vertex_perm=vertex_perm, color_perm=color_perm,
            shuffle_rng=shuffle_rng, return_model=True,
        )
        if not sat:
            log(f"  ERROR: P_510 5-coloring SAT returned UNSAT (should be SAT)")
            break

        canonical = canonicalize_coloring(coloring, 5)
        if canonical in seen:
            n_consecutive_dups += 1
            if n_consecutive_dups >= 25:
                log(f"  early stop: 25 consecutive duplicates "
                    f"(SAT solver returning similar models). Final count: {n_distinct}")
                break
            continue

        seen.add(canonical)
        colorings.append(list(canonical))
        n_distinct += 1
        n_consecutive_dups = 0
        if n_distinct % 10 == 0:
            log(f"  sampled {n_distinct}/{target_count} distinct (attempts={n_attempts}, "
                f"t_sat_last={t_sat:.2f}s, total_elapsed={elapsed:.0f}s)")

    log(f"Stage A complete: {len(colorings)} distinct canonical 5-colorings, "
        f"elapsed={time.time()-t_start:.0f}s, attempts={n_attempts}")
    return colorings


# =========================================================================
# Stage B: bridge scoring (kill vectors + diversity)
# =========================================================================

def build_color_table(colorings):
    """Convert list-of-colorings into a numpy-friendly nested structure:
    C[s][v] = color of vertex v under sample s.

    Returns list of lists.
    """
    return [list(c) for c in colorings]


def score_bridges(N, colorings, top_k=8000):
    """Precompute per-vertex u-profile across the c_1 sample.

    Returns (u_color_table, u_entropy) where:
      u_color_table[u] = list of colors [c_1(u) for c_1 in colorings],
                        length = len(colorings).
      u_entropy[u]    = Shannon entropy of u's color distribution.

    The actual bridge ranking is done DYNAMICALLY in Stage C (greedy needs
    marginal F(v) growth at each step, not a static (u, v) score), but we
    pre-rank u's by entropy so the greedy can iterate u in priority order.
    """
    log(f"Stage B: precomputing u-profile for {N} vertices across "
        f"{len(colorings)} colorings")
    t0 = time.time()
    C = colorings
    S = len(C)

    u_color_table = [[c1[u] for c1 in C] for u in range(N)]

    import math
    def entropy(profile):
        total = sum(profile)
        if total == 0:
            return 0
        h = 0
        for n in profile:
            if n == 0:
                continue
            p = n / total
            h -= p * math.log2(p)
        return h

    u_profile = [[0] * 5 for _ in range(N)]
    for u in range(N):
        for s in range(S):
            u_profile[u][u_color_table[u][s]] += 1
    u_entropy = [entropy(u_profile[u]) for u in range(N)]

    log(f"  u_entropy range: [{min(u_entropy):.3f}, {max(u_entropy):.3f}], "
        f"mean={sum(u_entropy)/N:.3f}")
    log(f"  high-entropy (>2.0) u count: {sum(1 for e in u_entropy if e > 2.0)}")
    log(f"  full-entropy (=log2(5)~2.32) u count: "
        f"{sum(1 for e in u_entropy if e > 2.30)}")

    log(f"Stage B complete (elapsed {time.time()-t0:.1f}s)")

    # Return per-u data; Stage C ranks bridges dynamically.
    return u_color_table, u_entropy


# =========================================================================
# no-K_4 check
# =========================================================================

def compute_adj(N1, N2, edges_H1, edges_H2, B):
    """Combined adjacency on N1+N2 vertices.

    H_1 vertices: 0..N1-1. H_2 vertices: N1..N1+N2-1.
    """
    N = N1 + N2
    adj = [set() for _ in range(N)]
    for (u, v) in edges_H1:
        adj[u].add(v); adj[v].add(u)
    for (u, v) in edges_H2:
        adj[N1 + u].add(N1 + v)
        adj[N1 + v].add(N1 + u)
    for (u, v) in B:
        adj[u].add(N1 + v)
        adj[N1 + v].add(u)
    return adj


def adj_add_bridge(adj, u, v_global):
    adj[u].add(v_global)
    adj[v_global].add(u)


def adj_remove_bridge(adj, u, v_global):
    adj[u].discard(v_global)
    adj[v_global].discard(u)


def creates_K4(adj, u, v_global):
    """Check if adding the edge (u, v_global) would create a K_4. The edge
    is NOT yet in adj.

    A K_4 containing the new edge requires two vertices w_1, w_2 such that:
      w_1, w_2 are both adjacent to both u and v_global, AND
      w_1 is adjacent to w_2.
    """
    common = adj[u] & adj[v_global]
    if len(common) < 2:
        return False
    common = sorted(common)
    for i in range(len(common)):
        c1 = common[i]
        adj_c1 = adj[c1]
        for j in range(i + 1, len(common)):
            c2 = common[j]
            if c2 in adj_c1:
                return True
    return False


# =========================================================================
# Residual list-coloring check (for H_2 = P_510 with list L)
# =========================================================================

def list_color_feasible(N, edges, L, time_limit=60):
    """Check whether H_2 (graph (N, edges)) is list-colorable from lists L.

    L is a list of N lists, each a subset of [5]. Returns True/False (None
    on timeout).
    """
    # Encode: x_{v, c} for c in L[v]. Constraints:
    #   each vertex: at least one color from its list.
    #   each vertex: at most one color (pairwise).
    #   each edge (u, v): no shared color.
    # Empty list at any v ==> infeasible.
    for v in range(N):
        if not L[v]:
            return False

    var_map = {}
    next_var = 1
    for v in range(N):
        for c in L[v]:
            var_map[(v, c)] = next_var
            next_var += 1

    clauses = []
    for v in range(N):
        lits = [var_map[(v, c)] for c in L[v]]
        clauses.append(lits)
        for i in range(len(L[v])):
            for j in range(i + 1, len(L[v])):
                clauses.append([-var_map[(v, L[v][i])], -var_map[(v, L[v][j])]])
    for (u, v) in edges:
        common = set(L[u]) & set(L[v])
        for c in common:
            clauses.append([-var_map[(u, c)], -var_map[(v, c)]])

    with Cadical195(bootstrap_with=clauses) as solver:
        if time_limit is not None:
            solver.conf_budget(int(time_limit * 50000))
            res = solver.solve_limited(expect_interrupt=False)
        else:
            res = solver.solve()
        if res is None:
            return None
        return bool(res)


def compute_L_from_B(B, c1, N2):
    """Given bridge set B and c_1 (a coloring of H_1), compute L[v] for
    each v in V(H_2).
    """
    F = [set() for _ in range(N2)]
    for (u, v) in B:
        F[v].add(c1[u])
    return [sorted(set(range(5)) - f) for f in F]


def count_infeasible_c1(B, colorings, N2, edges_H2, time_limit_per=30):
    """For a bridge set B, count how many c_1 samples produce list-infeasible
    residual.

    Returns (n_infeasible, n_feasible, n_timeout).
    """
    n_inf = 0
    n_feas = 0
    n_to = 0
    for c1 in colorings:
        L = compute_L_from_B(B, c1, N2)
        # Fast empty-list check.
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
# Stage C: greedy bridge cover
# =========================================================================

def greedy_bridge_cover(N1, edges_H1, N2, edges_H2, colorings,
                        u_color_table, u_entropy,
                        max_bridges=2000, no_k4=True, time_limit=10800,
                        sat_check_every=50, sat_time_limit=600,
                        candidate_pool_size=200,
                        initial_B=None):
    """Marginal-gain greedy: at each step pick the bridge (u, v) maximizing
    the increase in sum_{s} |F[s][v]| (subject to no-K_4 and not already in B).

    To keep cost manageable, we maintain a candidate pool of "promising" u's
    (sorted by entropy desc, top `candidate_pool_size`) and a target pool of
    "underserved" v's (those with smallest current max_F(v) across samples).

    Returns (best_B, history, verdict).
    """
    log(f"Stage C: marginal-gain greedy (max={max_bridges} bridges, "
        f"sat_check_every={sat_check_every}, candidate_pool={candidate_pool_size})")
    t_start = time.time()

    S = len(colorings)
    # Per-sample F[v]: F_state[s][v] is a bitmask in [0, 32), bit c -> c is in F.
    F_state = [[0] * N2 for _ in range(S)]

    # Track popcount(F[s][v]) for each (s, v).
    F_size = [[0] * N2 for _ in range(S)]

    # Per-bridge usage set so we don't double-add.
    used = set()

    # Adjacency for K_4 detection.
    adj = compute_adj(N1, N2, edges_H1, edges_H2, [])

    # Bridge candidate pool: top-entropy u's.
    u_ranked = sorted(range(N1), key=lambda u: -u_entropy[u])
    u_pool = u_ranked[:candidate_pool_size]

    # Bitmask of color c_1(u) under sample s for u in u_pool.
    # Precompute: for each u in u_pool, kill_mask[u][s] = 1 << c_1(u).
    kill_mask = {}
    for u in u_pool:
        kill_mask[u] = [1 << u_color_table[u][s] for s in range(S)]
    # Also for u's in initial_B that may not be in u_pool.
    if initial_B:
        for (u, v) in initial_B:
            if u not in kill_mask:
                kill_mask[u] = [1 << u_color_table[u][s] for s in range(S)]

    B = []
    history = []
    n_attempted = 0
    n_skipped_k4 = 0
    n_added = 0

    # Re-apply initial_B to F_state and adj.
    if initial_B:
        for (u, v) in initial_B:
            v_global = N1 + v
            adj_add_bridge(adj, u, v_global)
            B.append((u, v))
            used.add((u, v))
            n_added += 1
            for s in range(S):
                km_s = kill_mask[u][s]
                if not (F_state[s][v] & km_s):
                    F_state[s][v] |= km_s
                    F_size[s][v] += 1
        log(f"  re-applied initial_B: |B|={len(B)}")

    # Track "v score" = sum_{s} F_size[s][v] (current). Bridges into v with the
    # largest unmet potential are preferred.
    # Marginal gain of (u, v): for sample s, gain += 1 iff kill_mask[u][s] bit
    # NOT already in F_state[s][v]. So gain_uv = sum_{s} (1 if kill_mask[u][s]
    # & F_state[s][v] == 0 else 0).
    #
    # For tractability: we iterate (u, v) lexicographically through (u_pool, V_H2),
    # compute gain_uv quickly, and pick argmax. With u_pool=200 and N2=510 that's
    # ~102k (u,v) per step, each O(S) bitmask ops. With S=60 that's ~6M ops per
    # step. Adding 2500 bridges => 15B ops, way too slow.
    #
    # Optimization: We pre-compute a quick "potential bridge" list: only consider
    # (u, v) where F_size[s][v] < 5 for SOME s (otherwise the bridge can't help).
    # We also lazily evaluate gains: only top-K by previous step's gain are
    # re-evaluated each step.

    # Initialize candidate list with all (u, v) for u in u_pool, v in V_H2.
    # That's |u_pool| * N2 = 200 * 510 = 102k candidates.
    candidates = []  # list of (u, v)
    for u in u_pool:
        for v in range(N2):
            candidates.append((u, v))

    log(f"  candidate (u, v) pool size: {len(candidates)}")
    log(f"  initial: |B|=0, all samples have F empty everywhere")

    last_sample_chi6_check_step = 0

    # Concentration strategy: we want to SATURATE F(v) = [5] for some specific
    # target v across all samples. So we pick a small set of "target v's" and
    # concentrate bridges into them.
    #
    # Heuristic: identify ~20 target v's (e.g., low-degree v's in H_2 to keep
    # K_4 risk low, or random) and add bridges (u, v) where u varies across
    # high-entropy candidates and v is in the target set.
    #
    # Score formula:
    #   priority(u, v) = (gain * 1000)
    #                  + (10 if v in target_set else 0)
    #                  + (100 if any sample reaches F_size = 5 after this bridge else 0)
    #                  + (1 if v_progress[v] near max - F_size still under 5)

    # Target v selection: 20 v's with the lowest H_2 degree (to keep K_4 unlikely).
    deg_H2 = [0] * N2
    for (u, vv) in edges_H2:
        deg_H2[u] += 1
        deg_H2[vv] += 1
    target_v = sorted(range(N2), key=lambda v: deg_H2[v])[:30]
    target_set = set(target_v)
    log(f"  target v set (low-degree): {target_v[:10]}... (min_deg={deg_H2[target_v[0]]}, "
        f"max in target={deg_H2[target_v[-1]]})")

    while n_added < max_bridges:
        if time.time() - t_start > time_limit:
            log("  time limit reached")
            break

        # Compute v_progress (current saturation level).
        v_progress = [sum(F_size[s][v] for s in range(S)) for v in range(N2)]

        # Pick a candidate maximizing the composite score.
        # Inline-optimized inner loop (Python bytecode hot path).
        best_score = -1
        best_uv = None
        best_gain = 0
        # Per-u kill_masks pre-extracted for speed.
        # Cache F_state and F_size accessors.
        for (u, v) in candidates:
            if (u, v) in used:
                continue
            km = kill_mask[u]
            gain = 0
            sat_sam = 0
            sub_sat = 0
            for s in range(S):
                Fsv = F_state[s][v]
                kms = km[s]
                if not (Fsv & kms):
                    gain += 1
                    new_sz = F_size[s][v] + 1
                    if new_sz == 5:
                        sat_sam += 1
                    elif new_sz == 4:
                        sub_sat += 1
            if gain == 0:
                continue
            in_target = 500 if v in target_set else 0
            score = (sat_sam * 100000
                     + sub_sat * 1000
                     + in_target
                     + gain * 10
                     + v_progress[v])
            if score > best_score:
                best_score = score
                best_uv = (u, v)
                best_gain = gain

        if best_uv is None or best_gain <= 0:
            log(f"  no positive-gain candidate; stopping greedy")
            break

        u, v = best_uv

        # no-K_4 check
        v_global = N1 + v
        if no_k4 and creates_K4(adj, u, v_global):
            n_skipped_k4 += 1
            # Mark this (u, v) so we don't try it again.
            used.add((u, v))
            n_attempted += 1
            continue

        # Add the bridge.
        adj_add_bridge(adj, u, v_global)
        used.add((u, v))
        B.append((u, v))
        # Update F_state and F_size.
        for s in range(S):
            km_s = kill_mask[u][s]
            if not (F_state[s][v] & km_s):
                F_state[s][v] |= km_s
                F_size[s][v] += 1
        n_added += 1
        n_attempted += 1

        emptylist_infeasible_count = sum(
            1 for s in range(S) if any(F_size[s][vv] == 5 for vv in range(N2))
        )

        history.append({
            "step": n_added,
            "added": [u, v],
            "gain": best_gain,
            "emptylist_infeasible_count": emptylist_infeasible_count,
            "n_skipped_k4": n_skipped_k4,
        })

        if n_added % 25 == 0:
            elapsed = time.time() - t_start
            log(f"  step {n_added}: |B|={len(B)}, last_gain={best_gain}, "
                f"emptylist={emptylist_infeasible_count}/{S}, "
                f"skipped_K4={n_skipped_k4}, attempted={n_attempted}, "
                f"elapsed={elapsed:.0f}s ({n_added/(elapsed+0.001):.2f}/s)")

        # SAT check periodically.
        if n_added % sat_check_every == 0:
            if emptylist_infeasible_count == S:
                # All samples have empty list at some v: strong signal.
                n_inf, n_feas, n_to = count_infeasible_c1(
                    B, colorings, N2, edges_H2, time_limit_per=20,
                )
                log(f"  step {n_added}: residual-infeas={n_inf}, "
                    f"feas={n_feas}, to={n_to} (of {S})")
                if n_feas == 0:
                    log(f"  SAMPLE-level all-infeasible at |B|={len(B)}; "
                        f"calling full SAT.")
                    edges_full = (list(edges_H1)
                                  + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                                  + [(a, N1 + b) for (a, b) in B])
                    sat, _, t_sat = sat_k_color(N1 + N2, edges_full, 5,
                                                 time_limit=sat_time_limit)
                    log(f"  full SAT 5-coloring: sat={sat}, t={t_sat:.0f}s")
                    if sat is False:
                        log(f"  !!! CHI >= 6 CONFIRMED at |B|={len(B)}")
                        return B, history, "chi_geq_6"
                    elif sat is True:
                        log(f"  chi <= 5 still (sample incomplete); "
                            f"bailing round to add adversary")
                        return B, history, "sample_incomplete"
                    else:
                        log(f"  SAT timeout; continuing greedy")
                last_sample_chi6_check_step = n_added

    log(f"Stage C done: |B|={len(B)}, attempted={n_attempted}, "
        f"skipped_K4={n_skipped_k4}, time={time.time()-t_start:.0f}s")
    return B, history, "exhausted"


# =========================================================================
# Adversarial c_1 augmentation: find a c_1 that list-extends despite B
# =========================================================================

def find_adversary_c1(N1, edges_H1, N2, edges_H2, B, time_limit=300):
    """Find a proper 5-coloring c_1 of H_1 such that the residual list-coloring
    on H_2 with L(v) = [5] \\ {c_1(u) : (u,v) in B} IS feasible.

    Equivalently: a 5-coloring c of the combined graph G = H_1 cup H_2 cup B,
    restricted to H_1. If such c exists, c_1 = c|_{H_1} is a c_1 with a
    list-extending witness c_2 = c|_{H_2}.

    Returns c_1 (a coloring of H_1) or None.
    """
    edges_full = (list(edges_H1)
                  + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                  + [(a, N1 + b) for (a, b) in B])
    sat, coloring, elapsed = sat_k_color(
        N1 + N2, edges_full, 5, time_limit=time_limit, return_model=True,
    )
    if sat:
        c1 = list(coloring[:N1])
        # Canonicalize.
        return canonicalize_coloring(c1, 5)
    return None


def greedy_with_adversarial_aug(N1, edges_H1, N2, edges_H2, colorings,
                                u_color_table, u_entropy,
                                max_bridges=3000, no_k4=True,
                                time_limit=14400,
                                sat_check_every=100, sat_time_limit=600,
                                candidate_pool_size=150,
                                max_adversary_rounds=20):
    """Iterated greedy: between greedy rounds, augment the c_1 sample with an
    adversary coloring (one that list-extends despite current B).

    Returns (B, history, verdict, final_colorings).
    """
    log(f"Stage C+: iterated greedy with adversarial augmentation")
    log(f"  initial sample size: {len(colorings)}, max_adversary_rounds: "
        f"{max_adversary_rounds}")
    t_start = time.time()

    colorings = list(colorings)  # mutable copy
    aggregated_B = []
    history_all = []
    aug_round = 0
    n_consecutive_duplicates = 0

    while aug_round < max_adversary_rounds:
        aug_round += 1
        log(f"=== Adversary round {aug_round}/{max_adversary_rounds}, "
            f"sample size now {len(colorings)} ===")

        # Recompute u_color_table to include new colorings.
        # u_color_table[u] = [c_1(u) for c_1 in colorings]
        new_u_color_table = [[c1[u] for c1 in colorings] for u in range(N1)]
        import math
        def entropy(profile):
            total = sum(profile)
            if total == 0:
                return 0
            h = 0
            for n in profile:
                if n == 0:
                    continue
                p = n / total
                h -= p * math.log2(p)
            return h
        u_profile = [[0] * 5 for _ in range(N1)]
        S = len(colorings)
        for u in range(N1):
            for s in range(S):
                u_profile[u][new_u_color_table[u][s]] += 1
        new_u_entropy = [entropy(u_profile[u]) for u in range(N1)]

        elapsed_so_far = time.time() - t_start
        remaining_budget = time_limit - elapsed_so_far
        if remaining_budget < 60:
            log(f"  global budget exhausted")
            break
        # Per-round time budget: aggressive cap, prevents single round dominating.
        per_round_budget = min(remaining_budget * 0.4, 600)  # 10 min max/round

        # Run greedy starting from current aggregated_B (continue building).
        # Allow up to max_bridges total. If aggregated_B already at max, bump
        # by 50% per round to give room.
        round_max = max(max_bridges, len(aggregated_B) + 200)
        B_round, hist_round, verdict_round = greedy_bridge_cover(
            N1, edges_H1, N2, edges_H2, colorings,
            new_u_color_table, new_u_entropy,
            max_bridges=round_max,
            no_k4=no_k4,
            time_limit=per_round_budget,
            sat_check_every=sat_check_every,
            sat_time_limit=sat_time_limit,
            candidate_pool_size=candidate_pool_size,
            initial_B=aggregated_B,
        )
        aggregated_B = B_round
        for h in hist_round:
            h["aug_round"] = aug_round
            history_all.append(h)

        log(f"  round {aug_round} verdict: {verdict_round}, |B|={len(aggregated_B)}")

        if verdict_round == "chi_geq_6":
            log(f"  !!! CHI >= 6 confirmed at round {aug_round}, |B|={len(aggregated_B)}")
            return aggregated_B, history_all, "chi_geq_6", colorings

        # verdict_round in {"exhausted", "sample_incomplete", "time_limit"} all
        # mean: try adversarial augmentation.

        # Run adversary search: find c_1 that list-extends.
        log(f"  searching for adversary c_1 (with |B|={len(aggregated_B)})...")
        t_adv = time.time()
        adv_c1 = find_adversary_c1(
            N1, edges_H1, N2, edges_H2, aggregated_B,
            time_limit=min(300, remaining_budget - 30),
        )
        log(f"  adversary search: {'FOUND' if adv_c1 else 'NOT FOUND'} in {time.time()-t_adv:.0f}s")

        if adv_c1 is None:
            # No adversary => chi >= 6 should be confirmed.
            log(f"  no adversary found - confirming chi >= 6 via full SAT")
            sat, _, t_s = sat_k_color(
                N1 + N2,
                list(edges_H1) + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                + [(a, N1 + b) for (a, b) in aggregated_B],
                5, time_limit=min(900, remaining_budget),
            )
            if sat is False:
                log(f"  !!! CHI >= 6 CONFIRMED")
                return aggregated_B, history_all, "chi_geq_6", colorings
            elif sat is True:
                log(f"  SAT solver inconsistency - sat=True but no adversary?")
                # Just continue or stop.
                return aggregated_B, history_all, "inconsistent", colorings
            else:
                log(f"  SAT timeout; treating as inconclusive")
                return aggregated_B, history_all, "sat_timeout", colorings

        # Check if adv_c1 is already in colorings (canonical dedup).
        adv_c1 = list(adv_c1)
        if any(list(c) == adv_c1 for c in colorings):
            n_consecutive_duplicates += 1
            log(f"  adversary duplicate (#{n_consecutive_duplicates}); "
                f"retry with random clause shuffling")
            if n_consecutive_duplicates >= 5:
                log(f"  too many consecutive duplicates; stopping")
                return aggregated_B, history_all, "adversary_duplicate", colorings
            # Try forcing diversity: random search with seeded shuffling.
            edges_full = (list(edges_H1)
                          + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                          + [(a, N1 + b) for (a, b) in aggregated_B])
            for retry in range(5):
                vp = list(range(N1 + N2))
                rng = random.Random(20260527 + aug_round * 100 + retry)
                rng.shuffle(vp)
                cp = list(range(5))
                rng.shuffle(cp)
                sh_rng = random.Random(rng.randint(0, 10**9))
                sat, model, t_s = sat_k_color(
                    N1 + N2, edges_full, 5, return_model=True,
                    vertex_perm=vp, color_perm=cp, shuffle_rng=sh_rng,
                    time_limit=120,
                )
                if sat and model:
                    cand = canonicalize_coloring(list(model[:N1]), 5)
                    cand = list(cand)
                    if not any(list(c) == cand for c in colorings):
                        adv_c1 = cand
                        log(f"  found fresh adversary via shuffled SAT")
                        break
            else:
                log(f"  failed to find fresh adversary even with shuffling")
                continue
            n_consecutive_duplicates = 0

        colorings.append(adv_c1)
        log(f"  added adversary c_1 to sample (new size: {len(colorings)})")
        n_consecutive_duplicates = 0

    log(f"Max adversary rounds reached")
    return aggregated_B, history_all, "max_rounds", colorings


# =========================================================================
# Stage D: full SAT verification
# =========================================================================

def full_sat_verification(N1, edges_H1, N2, edges_H2, B, time_limit=1800):
    """SAT-check chi(G) <= 5 on the full combined graph.

    Returns (chi_5_sat, elapsed).
    """
    log(f"Stage D: full SAT chi<=5 on N={N1+N2}, |E|={len(edges_H1)+len(edges_H2)+len(B)}")
    edges_full = (list(edges_H1)
                  + [(N1 + a, N1 + b) for (a, b) in edges_H2]
                  + [(a, N1 + b) for (a, b) in B])
    sat, _, elapsed = sat_k_color(N1 + N2, edges_full, 5, time_limit=time_limit)
    if sat is None:
        log(f"  SAT timeout after {elapsed:.0f}s")
    else:
        log(f"  SAT chi<=5 result: {sat} ({'SAT (chi <= 5)' if sat else 'UNSAT (chi >= 6 !!!)'}) "
            f"elapsed={elapsed:.0f}s")
    return sat, elapsed


# =========================================================================
# Main
# =========================================================================

def main():
    log("=" * 76)
    log("h5_polymath_squared: chi>=6 UDG candidate search via P_510 x P_510 + bridges")
    log("=" * 76)

    # ----- Load -----
    N, edges = load_p510()
    N1 = N; edges_H1 = list(edges)
    N2 = N; edges_H2 = list(edges)
    log(f"Loaded P_510: |V|={N}, |E|={len(edges)}")

    # ----- Stage A: sample 5-colorings -----
    if COLORINGS_CACHE.exists():
        cached = json.loads(COLORINGS_CACHE.read_text())
        colorings = cached["colorings"]
        log(f"Stage A: loaded {len(colorings)} cached 5-colorings")
    else:
        colorings = sample_5colorings(N, edges, target_count=80, seed=20260527,
                                      time_limit=600)
        COLORINGS_CACHE.write_text(json.dumps({
            "n_vertices": N,
            "n_edges": len(edges),
            "n_colorings": len(colorings),
            "canonicalized": "S_5_first_appearance",
            "colorings": colorings,
        }, indent=1))
        log(f"  cached {len(colorings)} colorings to {COLORINGS_CACHE.name}")

    if len(colorings) < 5:
        log("Too few colorings sampled; aborting")
        return 1

    # ----- Stage B: precompute u-color table + u-entropy -----
    if SCORES_CACHE.exists():
        cached = json.loads(SCORES_CACHE.read_text())
        u_color_table = cached["u_color_table"]
        u_entropy = cached["u_entropy"]
        log(f"Stage B: loaded cached u_color_table and u_entropy")
    else:
        u_color_table, u_entropy = score_bridges(N, colorings)
        SCORES_CACHE.write_text(json.dumps({
            "u_color_table": u_color_table,
            "u_entropy": u_entropy,
        }, indent=1))
        log(f"  cached u_color_table + u_entropy to {SCORES_CACHE.name}")

    # ----- Stage C: greedy build with adversarial c_1 augmentation -----
    # Strategy: greedy saturates the sample, then we find a c_1 that
    # list-extends despite B (an "adversary" coloring), add it to the sample,
    # and continue.
    # Tight per-round limits: max_bridges total cap 4000, per-round time 600s,
    # 30 adversary rounds. Total budget ~3h.
    best_B, history, verdict_C, colorings_final = greedy_with_adversarial_aug(
        N1, edges_H1, N2, edges_H2, colorings,
        u_color_table, u_entropy,
        max_bridges=4000, no_k4=True, time_limit=11000,
        sat_check_every=300, sat_time_limit=600,
        candidate_pool_size=120,
        max_adversary_rounds=30,
    )
    log(f"Stage C final: |B|={len(best_B)}, |colorings|={len(colorings_final)}, "
        f"verdict={verdict_C}")
    colorings = colorings_final

    log(f"Stage C verdict: {verdict_C}, final |B|={len(best_B)}")

    # ----- Stage D: full SAT verification on best B -----
    if verdict_C == "chi_geq_6":
        log("Stage D: confirming chi >= 6 via full SAT")
        sat, elapsed = full_sat_verification(N1, edges_H1, N2, edges_H2, best_B,
                                              time_limit=1800)
        final_verdict = "CHI_6_CONFIRMED" if sat is False else \
                        "CHI_5_DESPITE_LIST_INFEAS" if sat is True else \
                        "SAT_TIMEOUT"
    else:
        # Just do a sanity full SAT chi<=5 on the final B (should be SAT).
        log("Stage D: sanity chi<=5 SAT on final B")
        if len(best_B) > 0:
            sat, elapsed = full_sat_verification(N1, edges_H1, N2, edges_H2, best_B,
                                                  time_limit=900)
            final_verdict = "NO_CHI_6_FOUND_SAT_HOLDS" if sat is True else \
                            "UNEXPECTED_UNSAT" if sat is False else \
                            "SAT_TIMEOUT"
        else:
            sat, elapsed = (True, 0.0)
            final_verdict = "NO_BRIDGES_ADDED"

    # ----- F-profile analysis on final B (structural takeaway) -----
    log("F-profile evolution analysis on final B")
    F_profiles = []
    if best_B:
        for c1 in colorings[:10]:  # first 10 samples
            F = [set() for _ in range(N2)]
            for (u, v) in best_B:
                F[v].add(c1[u])
            sizes = sorted([len(f) for f in F], reverse=True)
            F_profiles.append({
                "max_F": sizes[0],
                "min_L": 5 - sizes[0],
                "n_F_eq_5": sum(1 for s in sizes if s == 5),
                "n_F_eq_4": sum(1 for s in sizes if s == 4),
                "n_F_geq_3": sum(1 for s in sizes if s >= 3),
                "n_F_eq_0": sum(1 for s in sizes if s == 0),
            })

    # Count residual infeasibility across the sample for the final B.
    if best_B and len(best_B) <= 5000:
        log("Counting residual list-coloring infeasibility on final B (full sample)")
        # Quick empty-list filter first (cheap).
        n_empty_list = 0
        for c1 in colorings:
            F = [set() for _ in range(N2)]
            for (u, v) in best_B:
                F[v].add(c1[u])
            if any(len(f) == 5 for f in F):
                n_empty_list += 1
        log(f"  empty-list infeasibility on sample: {n_empty_list}/{len(colorings)}")
    else:
        n_empty_list = 0

    # ----- Summary -----
    summary = {
        "experiment": "h5_polymath_squared",
        "halves": "P_510 x P_510",
        "n_vertices_each": N,
        "n_edges_each": len(edges),
        "n_total_vertices": 2 * N,
        "n_colorings_sampled": len(colorings),
        "best_B_size": len(best_B),
        "best_B": best_B,
        "verdict_stage_C": verdict_C,
        "verdict_final": final_verdict,
        "sat_check_result": sat,
        "sat_check_elapsed_s": round(elapsed, 1),
        "n_empty_list_on_sample": n_empty_list,
        "F_profiles_first10": F_profiles,
        "history_length": len(history),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, default=str))
    log(f"Summary written to {SUMMARY_PATH.name}")

    # Save full history separately (larger).
    SEARCH_LOG.write_text(json.dumps({
        "history": history,
    }, indent=1))

    log("=" * 76)
    log(f"FINAL VERDICT: {final_verdict}")
    log(f"  |B| tested: {len(best_B)}")
    log(f"  no-K_4: yes (filter applied)")
    log(f"  empty-list infeasibility (sample): {n_empty_list}/{len(colorings)}")
    log("=" * 76)

    return 0


if __name__ == "__main__":
    sys.exit(main())
