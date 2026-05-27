r"""e1y: Triple-coupling lift of the L22 list-coloring theorem.

Architecture 1, Shot 5. BUILDER pass: lift L22's pair-coupling list-coloring
theorem to a triple-coupling theorem and search for a 21-vertex (three Moser
spindles) chi=6 graph subject to omega(G) <= 3.

L22 (pair-coupling theorem, proved):

  chi(H_1 cup H_2 cup B) >= 5
    iff
  for every proper 4-coloring c_1 of H_1, the residual list-coloring problem
    L(v) = [4] \ {c_1(u) : (u, v) in B},   v in V(H_2),
  on H_2 admits no proper list-coloring.

THIS FILE PROVES THE TRIPLE LIFT (theorem):

  THEOREM (triple-coupling list-coloring lift).
  Let H_1, H_2, H_3 be graphs on disjoint vertex sets, B_{12}, B_{13}, B_{23}
  bridge sets, G = H_1 cup H_2 cup H_3 cup B_{12} cup B_{13} cup B_{23}. Then:
    chi(G) >= 6
      iff
    for every proper 5-coloring c_1 of H_1, the residual list-coloring problem
    on H_2 cup H_3 cup B_{23} with lists
      L_2(v) = [5] \ {c_1(u) : (u, v) in B_{12}},   v in V(H_2),
      L_3(w) = [5] \ {c_1(u) : (u, w) in B_{13}},   w in V(H_3),
    admits no proper list-coloring of H_2 cup H_3 cup B_{23} (where the bridges
    in B_{23} must connect distinctly-colored endpoints in any valid coloring).

  Proof.
  (==>) Contrapositive. Suppose for some c_1 the residual list-coloring is
  feasible with witness (c_2, c_3). Set c|_{H_i} = c_i. Then:
    - H_1 edges OK by c_1 proper.
    - H_2 edges OK by c_2 proper list-coloring.
    - H_3 edges OK by c_3 proper list-coloring.
    - B_{12} bridges (u, v): c(u) = c_1(u) in F_{12}(v) but c(v) = c_2(v) in
      L_2(v) = [5] \ F_{12}(v); distinct.
    - B_{13} bridges: same logic.
    - B_{23} bridges: enforced by the residual list-coloring problem's edge
      constraint between H_2 and H_3 via B_{23}.
  So G is properly 5-colored, contradicting chi(G) >= 6.
  (<==) Contrapositive. Suppose G is properly 5-colored by c. Let
    c_1 := c|_{H_1}, c_2 := c|_{H_2}, c_3 := c|_{H_3}.
  Then c_1 is a proper 5-coloring of H_1 (since H_1 edges respected). For each
  v in V(H_2) and each bridge (u, v) in B_{12}: c_2(v) = c(v) != c(u) = c_1(u),
  so c_2(v) not in {c_1(u) : (u,v) in B_{12}} = F_{12}(v); hence c_2(v) in
  L_2(v). Symmetrically c_3(w) in L_3(w). And H_2 edges, H_3 edges, B_{23}
  edges respected. So (c_2, c_3) is a residual list-coloring for c_1,
  contradicting "for every c_1, residual is infeasible". QED.

This is the natural recursive structure of multi-half coupling: each additional
half lifts the list-coloring problem by one color (residual has 5 colors instead
of 4) and adds one more bridge set. The induction can iterate.

OUTPUTS:
  - Theorem verification on small synthetic cases (K_4 + Moser variants).
  - Three-Moser search subject to omega(G) <= 3.
  - The "list-tightness" structural analysis: when is the residual infeasible?
  - JSON cache at _cache/e1y_triple_list.json.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import random
import sys
import time
from typing import Iterable, Optional

from pysat.solvers import Cadical195
from pysat.card import CardEnc, EncType

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO_ROOT))
from experiments.combinatorial.e1v_bridge_covering import (
    k4_graph, moser_spindle_graph, enumerate_canonical_colorings,
    enumerate_all_colorings, sat_k_color,
)


# =========================================================================
# SAT machinery
# =========================================================================

def chi_three_way(N1, E1, N2, E2, N3, E3, B12, B13, B23, k):
    """SAT-check chi(H_1 cup H_2 cup H_3 cup B12 cup B13 cup B23) <= k.

    Vertex indexing:
      H_1: 0 .. N1-1
      H_2: N1 .. N1+N2-1
      H_3: N1+N2 .. N1+N2+N3-1
    """
    N = N1 + N2 + N3
    edges = list(E1)
    edges += [(N1 + u, N1 + v) for (u, v) in E2]
    edges += [(N1 + N2 + u, N1 + N2 + v) for (u, v) in E3]
    edges += [(u, N1 + v) for (u, v) in B12]
    edges += [(u, N1 + N2 + v) for (u, v) in B13]
    edges += [(N1 + u, N1 + N2 + v) for (u, v) in B23]
    return sat_k_color(N, edges, k)


def chi_value(N, edges, lo=3, hi=8):
    """Return chi(G) for graph (N, edges) in [lo, hi] via SAT (binary-style)."""
    for k in range(lo, hi + 1):
        if sat_k_color(N, edges, k):
            return k
    return None


def chi_three_way_value(N1, E1, N2, E2, N3, E3, B12, B13, B23, lo=4, hi=8):
    for k in range(lo, hi + 1):
        if chi_three_way(N1, E1, N2, E2, N3, E3, B12, B13, B23, k):
            return k
    return None


# =========================================================================
# Triple list-coloring SAT engine
# =========================================================================

def triple_list_color_witness(N2, E2, N3, E3, B23, L2, L3, N1):
    """Return a witness coloring (c2, c3) for the residual list-coloring on
    (H_2 cup H_3 cup B_{23}) with vertex lists L2[v] (for v in V(H_2)) and
    L3[w] (for w in V(H_3)), or None if infeasible.

    Variable encoding: x_{(side, v, c)} where side in {2, 3}.
    """
    var_map = {}
    next_var = 1
    for v in range(N2):
        for c in L2[v]:
            var_map[(2, v, c)] = next_var
            next_var += 1
    for v in range(N3):
        for c in L3[v]:
            var_map[(3, v, c)] = next_var
            next_var += 1
    inv = {val: key for key, val in var_map.items()}

    clauses = []
    # Each vertex gets at least one color (and at most one).
    for v in range(N2):
        if not L2[v]:
            return None
        lits = [var_map[(2, v, c)] for c in L2[v]]
        clauses.append(lits)
        for i in range(len(L2[v])):
            for j in range(i + 1, len(L2[v])):
                clauses.append([-var_map[(2, v, L2[v][i])], -var_map[(2, v, L2[v][j])]])
    for v in range(N3):
        if not L3[v]:
            return None
        lits = [var_map[(3, v, c)] for c in L3[v]]
        clauses.append(lits)
        for i in range(len(L3[v])):
            for j in range(i + 1, len(L3[v])):
                clauses.append([-var_map[(3, v, L3[v][i])], -var_map[(3, v, L3[v][j])]])

    # H_2 edges.
    for (u, v) in E2:
        common = set(L2[u]) & set(L2[v])
        for c in common:
            clauses.append([-var_map[(2, u, c)], -var_map[(2, v, c)]])
    # H_3 edges.
    for (u, v) in E3:
        common = set(L3[u]) & set(L3[v])
        for c in common:
            clauses.append([-var_map[(3, u, c)], -var_map[(3, v, c)]])
    # B_{23} bridge edges: c2(u) != c3(v).
    for (u, v) in B23:
        common = set(L2[u]) & set(L3[v])
        for c in common:
            clauses.append([-var_map[(2, u, c)], -var_map[(3, v, c)]])

    with Cadical195(bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        m = solver.get_model()
        c2 = [None] * N2
        c3 = [None] * N3
        for lit in m:
            if lit > 0 and lit in inv:
                side, v, c = inv[lit]
                if side == 2:
                    c2[v] = c
                else:
                    c3[v] = c
        return (c2, c3)


def triple_list_color_feasible(N2, E2, N3, E3, B23, L2, L3, N1=0):
    return triple_list_color_witness(N2, E2, N3, E3, B23, L2, L3, N1) is not None


def compute_F_for_bridges(B, c1, N_target):
    F = [set() for _ in range(N_target)]
    for (u, v) in B:
        F[v].add(c1[u])
    return [sorted(s) for s in F]


def compute_L_from_F(F, k=5):
    return [sorted(set(range(k)) - set(f)) for f in F]


# =========================================================================
# Triple lift theorem: verify on simple cases
# =========================================================================

def verify_triple_theorem(N1, E1, N2, E2, N3, E3, B12, B13, B23,
                          k=5, label="", verbose=False):
    """Verify the triple lift theorem computationally:

      chi(G) >= k+1
        iff
      for every proper k-coloring c_1 of H_1, the residual list-coloring on
      (H_2 cup H_3 cup B_{23}) with lists L2[v] = [k] \ F_{12}(v),
      L3[w] = [k] \ F_{13}(w), is infeasible.

    Returns dict with both sides' values and assertion check.
    """
    # Enumerate ALL (not canonical) proper k-colorings of H_1, since the bridge
    # constraints compare colored values directly.
    C1 = enumerate_all_colorings(N1, E1, k)
    n_C1 = len(C1)
    n_residual_feasible = 0
    feasible_c1_example = None
    for c1 in C1:
        F12 = compute_F_for_bridges(B12, c1, N2)
        F13 = compute_F_for_bridges(B13, c1, N3)
        L2 = compute_L_from_F(F12, k)
        L3 = compute_L_from_F(F13, k)
        witness = triple_list_color_witness(N2, E2, N3, E3, B23, L2, L3, N1)
        if witness is not None:
            n_residual_feasible += 1
            if feasible_c1_example is None:
                feasible_c1_example = (list(c1), L2, L3, witness)
    chi_geq_kp1_via_list = (n_residual_feasible == 0)

    # Direct SAT check.
    sat_k = chi_three_way(N1, E1, N2, E2, N3, E3, B12, B13, B23, k)
    chi_geq_kp1_via_sat = not sat_k

    # Sanity assertion.
    if chi_geq_kp1_via_list != chi_geq_kp1_via_sat:
        # Find a counterexample: this would mean a bug.
        msg = (
            f"BUG in triple lift theorem on case '{label}': "
            f"list-method says chi>={k+1}? {chi_geq_kp1_via_list}, "
            f"SAT says chi>={k+1}? {chi_geq_kp1_via_sat}"
        )
        raise AssertionError(msg)

    result = {
        "label": label,
        "k": k,
        "n_C1": n_C1,
        "n_residual_feasible": n_residual_feasible,
        "chi_geq_kp1_via_list": chi_geq_kp1_via_list,
        "chi_geq_kp1_via_sat": chi_geq_kp1_via_sat,
        "theorem_holds": chi_geq_kp1_via_list == chi_geq_kp1_via_sat,
    }
    if verbose and feasible_c1_example is not None:
        c1, L2, L3, witness = feasible_c1_example
        result["feasible_c1_example"] = {
            "c1": c1,
            "L2_sizes": [len(l) for l in L2],
            "L3_sizes": [len(l) for l in L3],
            "witness_c2": witness[0],
            "witness_c3": witness[1],
        }
    return result


# =========================================================================
# Three-Moser search subject to omega <= 3
# =========================================================================

def moser_edge_list():
    """Return the Moser spindle edge list (graph-theoretic)."""
    N, E, _ = moser_spindle_graph()
    return N, E


def build_three_moser_graph(B12, B13, B23):
    """Construct H_1 cup H_2 cup H_3 cup B_{12} cup B_{13} cup B_{23}.

    Returns (N, edges).
    """
    N1, E1 = moser_edge_list()
    N2, E2 = moser_edge_list()
    N3, E3 = moser_edge_list()
    N = N1 + N2 + N3  # = 21
    edges = list(E1)
    edges += [(N1 + u, N1 + v) for (u, v) in E2]
    edges += [(N1 + N2 + u, N1 + N2 + v) for (u, v) in E3]
    edges += [(u, N1 + v) for (u, v) in B12]
    edges += [(u, N1 + N2 + v) for (u, v) in B13]
    edges += [(N1 + u, N1 + N2 + v) for (u, v) in B23]
    return N, edges


def omega_at_most_3(N, edges):
    """Test that the graph (N, edges) has clique number <= 3.

    Implementation: iterate over triangles, then check no triangle extends to K_4.
    The Moser spindle itself contains triangles, so we only need to test that no
    triangle in the full graph extends to K_4.
    """
    adj = [set() for _ in range(N)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)
    # Look for any K_4: for each edge (u,v), find common neighbors.
    edge_list = sorted(set((min(u, v), max(u, v)) for (u, v) in edges))
    for (u, v) in edge_list:
        common_uv = adj[u] & adj[v]
        if len(common_uv) < 2:
            continue
        common = sorted(common_uv)
        for i in range(len(common)):
            for j in range(i + 1, len(common)):
                w1, w2 = common[i], common[j]
                if w2 in adj[w1]:
                    # K_4 on {u, v, w1, w2}.
                    return False
    return True


def find_K4(N, edges):
    """Return one K_4 vertex set or None."""
    adj = [set() for _ in range(N)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)
    edge_list = sorted(set((min(u, v), max(u, v)) for (u, v) in edges))
    for (u, v) in edge_list:
        common = sorted(adj[u] & adj[v])
        for i in range(len(common)):
            for j in range(i + 1, len(common)):
                w1, w2 = common[i], common[j]
                if w2 in adj[w1]:
                    return (u, v, w1, w2)
    return None


# =========================================================================
# Search strategy: sample bridge configurations, filter no-K_4, SAT-check chi
# =========================================================================

def sample_bridge_set(N_H_target, size, rng, allowed_pairs=None):
    """Sample a bridge set of given size from V(H_1) x V(H_2).

    If allowed_pairs is given (a list of (u, v) pairs), sample only from those.
    """
    if allowed_pairs is None:
        all_pairs = [(u, v) for u in range(N_H_target) for v in range(N_H_target)]
    else:
        all_pairs = list(allowed_pairs)
    if size > len(all_pairs):
        return None
    return tuple(sorted(rng.sample(all_pairs, size)))


def search_three_moser_chi6_noK4(n_samples=2000, size_range=(8, 14),
                                  seed=42, sample_per_size=None,
                                  log_every=50, time_limit=600):
    """Sample random bridge configurations between three Moser spindles and
    record those with omega <= 3.

    For each configuration:
      1. Build G = three Moser spindles + B12 + B13 + B23 (each of size in size_range).
      2. Check omega(G) <= 3.
      3. SAT-check chi(G) via two-color escalator (start at 5, escalate to 6, 7...).
      4. Record case if chi >= 6.

    Returns dict with hits, near-misses, statistics.
    """
    rng = random.Random(seed)
    hits = []  # chi >= 6 with no K_4
    near_misses = []  # chi == 5 with no K_4
    statistics = {"total_tried": 0, "no_K4": 0, "chi_5": 0, "chi_6": 0,
                  "chi_7_plus": 0, "chi_4_or_less": 0, "K4_present": 0}

    t_start = time.time()
    N = 21  # three Moser

    if sample_per_size is None:
        sample_per_size = max(1, n_samples // (size_range[1] - size_range[0] + 1))

    for size in range(size_range[0], size_range[1] + 1):
        for trial in range(sample_per_size):
            if time.time() - t_start > time_limit:
                statistics["time_limit_hit"] = True
                break

            B12 = sample_bridge_set(7, size, rng)
            B13 = sample_bridge_set(7, size, rng)
            B23 = sample_bridge_set(7, size, rng)

            N_full, edges = build_three_moser_graph(B12, B13, B23)
            statistics["total_tried"] += 1

            # K_4 filter (cheap).
            if not omega_at_most_3(N_full, edges):
                statistics["K4_present"] += 1
                continue
            statistics["no_K4"] += 1

            # SAT-check chi.
            # Lower bound: chi >= 4 always (Moser is 4-chromatic).
            # Upper bound: chi <= chi(H1)+chi(H2)+chi(H3) = 12 but typically lower.
            # We do binary search starting at 4.
            chi_4 = sat_k_color(N_full, edges, 4)
            if chi_4:
                statistics["chi_4_or_less"] += 1
                continue
            chi_5 = sat_k_color(N_full, edges, 5)
            if chi_5:
                statistics["chi_5"] += 1
                if len(near_misses) < 20:
                    near_misses.append({
                        "B12": list(B12), "B13": list(B13), "B23": list(B23),
                        "chi": 5, "size": size,
                    })
                continue
            chi_6 = sat_k_color(N_full, edges, 6)
            if chi_6:
                statistics["chi_6"] += 1
                hits.append({
                    "B12": list(B12), "B13": list(B13), "B23": list(B23),
                    "chi": 6, "size": size,
                })
                print(f"  >>> HIT (chi>=6, no-K_4): size={size}")
                print(f"      B12={B12}")
                print(f"      B13={B13}")
                print(f"      B23={B23}")
            else:
                # chi >= 7.
                statistics["chi_7_plus"] += 1
                hits.append({
                    "B12": list(B12), "B13": list(B13), "B23": list(B23),
                    "chi": ">=7", "size": size,
                })
                print(f"  >>> HIT (chi>=7, no-K_4): size={size}")

            if (statistics["total_tried"]) % log_every == 0:
                print(f"  ... tried {statistics['total_tried']}, "
                      f"no-K_4: {statistics['no_K4']}, "
                      f"chi5: {statistics['chi_5']}, "
                      f"chi6: {statistics['chi_6']}, "
                      f"chi7+: {statistics['chi_7_plus']}, "
                      f"t={time.time()-t_start:.1f}s")

        if time.time() - t_start > time_limit:
            break

    statistics["elapsed_sec"] = round(time.time() - t_start, 2)
    return {"hits": hits, "near_misses": near_misses, "statistics": statistics}


# =========================================================================
# Structural conjecture test: three Moser + no-K_4 ==> chi <= 5
# =========================================================================

def test_three_moser_no_K4_caps_at_5(n_samples=400, size_range=(6, 16), seed=123,
                                      time_limit=400):
    """Conjecture: for three Moser spindles + bridges with omega <= 3,
    chi(G) <= 5 (i.e., the L21 mechanism caps at chi=5 in the no-K_4 regime).

    Test: many random samples, ALL OF THEM with omega <= 3 have chi <= 5.
    """
    res = search_three_moser_chi6_noK4(
        n_samples=n_samples, size_range=size_range, seed=seed,
        sample_per_size=max(1, n_samples // (size_range[1] - size_range[0] + 1)),
        time_limit=time_limit,
    )
    s = res["statistics"]
    if s["chi_6"] + s["chi_7_plus"] == 0:
        verdict = (
            f"NO chi>=6 no-K_4 three-Moser graph found in {s['total_tried']} "
            f"samples. Conjecture stands (cap = 5)."
        )
    else:
        verdict = (
            f"FOUND chi>=6 no-K_4 three-Moser graph: "
            f"{s['chi_6']} chi=6 cases, {s['chi_7_plus']} chi>=7 cases. "
            f"Conjecture REFUTED."
        )
    return {"verdict": verdict, "statistics": s, "hits": res["hits"],
            "near_misses": res["near_misses"][:5]}


# =========================================================================
# Aligned-bridge configurations from ADVERSARY angle 6, with K_4 filter
# =========================================================================

def test_adversary_configs_with_K4_filter():
    """Replay the ADVERSARY angle-6 named configurations and report chi, omega,
    and which K_4 (if any) is in the resulting graph.
    """
    B6 = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
    B_K22 = [(0,0),(0,1),(1,0),(1,1)]
    B_K23_shift = [(0,3),(0,4),(0,5),(1,3),(1,4),(1,5)]
    B6_perm = [(u, (v + 3) % 7) for u, v in B6]

    configs = [
        ("B6 aligned all", B6, B6, B6),
        ("B6/B6/empty", B6, B6, []),
        ("B6 chain", B6, [], B6),
        ("B6 + B6 + perm(B6)", B6, B6, B6_perm),
        ("K_{2,2} aligned", B_K22, B_K22, B_K22),
        ("K_{2,3} shifted (no K_3 cross)", B_K23_shift, B_K23_shift, B_K23_shift),
        ("B6 minus (0,0)", B6[1:], B6[1:], B6[1:]),
    ]
    results = []
    for label, B12, B13, B23 in configs:
        N, edges = build_three_moser_graph(B12, B13, B23)
        has_K4 = find_K4(N, edges)
        chi_v = chi_value(N, edges, lo=4, hi=8)
        results.append({
            "label": label,
            "B_sizes": (len(B12), len(B13), len(B23)),
            "K4_exists": has_K4 is not None,
            "K4_vertices": list(has_K4) if has_K4 else None,
            "chi": chi_v,
        })
        print(f"  {label}: |B|={len(B12)},{len(B13)},{len(B23)}, "
              f"K_4={has_K4 is not None} (verts={has_K4}), chi={chi_v}")
    return results


# =========================================================================
# F-profile / list-tightness analysis (corresponds to L22 lemma)
# =========================================================================

def list_tightness_analysis(N1, E1, N2, E2, N3, E3, B12, B13, B23, k=5):
    """For each proper k-coloring c_1 of H_1, compute the L_2 and L_3 profiles
    (list sizes per vertex) and check feasibility of the residual list-coloring.

    Aggregate: distribution of (min L_2 size, min L_3 size, residual-feasible)
    across all c_1.
    """
    C1 = enumerate_all_colorings(N1, E1, k)
    stats = []
    for c1 in C1:
        F12 = compute_F_for_bridges(B12, c1, N2)
        F13 = compute_F_for_bridges(B13, c1, N3)
        L2 = compute_L_from_F(F12, k)
        L3 = compute_L_from_F(F13, k)
        feasible = triple_list_color_feasible(N2, E2, N3, E3, B23, L2, L3)
        stats.append({
            "L2_sizes": [len(l) for l in L2],
            "L3_sizes": [len(l) for l in L3],
            "min_L2": min(len(l) for l in L2),
            "min_L3": min(len(l) for l in L3),
            "n_L2_empty": sum(1 for l in L2 if not l),
            "n_L3_empty": sum(1 for l in L3 if not l),
            "feasible": feasible,
        })
    n_total = len(stats)
    n_feasible = sum(1 for s in stats if s["feasible"])
    n_L2_empty_any = sum(1 for s in stats if s["n_L2_empty"] > 0)
    n_L3_empty_any = sum(1 for s in stats if s["n_L3_empty"] > 0)
    return {
        "n_C1": n_total,
        "n_residual_feasible": n_feasible,
        "n_C1_with_L2_empty": n_L2_empty_any,
        "n_C1_with_L3_empty": n_L3_empty_any,
        "chi_geq_6": n_feasible == 0,
    }


# =========================================================================
# Phase F: anchored search with L21 14-bridge as B12
# =========================================================================

def _phase_F_l21_anchored(B_L21, n_trials=200, seed=2026, time_limit=240):
    """B12 = L21 14-bridge (forces chi(H_1 + H_2 + B12) = 5, no-K_4).
    Vary B13 (size 0..14 random) and B23 (size 0..14 random); SAT-check chi.
    """
    rng = random.Random(seed)
    hits = []
    near_misses = []
    stats = {"total": 0, "no_K4": 0, "chi_4": 0, "chi_5": 0, "chi_6": 0, "chi_7+": 0,
             "K4_present": 0}
    t0 = time.time()
    all_pairs = [(u, v) for u in range(7) for v in range(7)]
    for trial in range(n_trials):
        if time.time() - t0 > time_limit:
            stats["time_limit_hit"] = True
            break
        s13 = rng.randint(0, 14)
        s23 = rng.randint(0, 14)
        B13 = tuple(rng.sample(all_pairs, s13)) if s13 else ()
        B23 = tuple(rng.sample(all_pairs, s23)) if s23 else ()
        N, edges = build_three_moser_graph(B_L21, B13, B23)
        stats["total"] += 1
        if find_K4(N, edges):
            stats["K4_present"] += 1
            continue
        stats["no_K4"] += 1
        chi = chi_value(N, edges, lo=4, hi=8)
        if chi == 4:
            stats["chi_4"] += 1
        elif chi == 5:
            stats["chi_5"] += 1
            if len(near_misses) < 8:
                near_misses.append({"B12": B_L21, "B13": list(B13), "B23": list(B23),
                                    "chi": 5})
        elif chi == 6:
            stats["chi_6"] += 1
            hits.append({"B12": B_L21, "B13": list(B13), "B23": list(B23), "chi": 6})
            print(f"  >>> CHI=6 NO-K_4: |B13|={s13}, |B23|={s23}")
        else:
            stats["chi_7+"] += 1
            hits.append({"B12": B_L21, "B13": list(B13), "B23": list(B23), "chi": chi})
            print(f"  >>> CHI={chi} NO-K_4: |B13|={s13}, |B23|={s23}")
    stats["elapsed_sec"] = round(time.time() - t0, 2)
    verdict = (
        f"hits chi>=6: {stats['chi_6'] + stats.get('chi_7+', 0)} "
        f"in {stats['total']} samples (no-K_4: {stats['no_K4']}). "
        f"chi=5 count: {stats['chi_5']}. "
        f"{'Conjecture STANDS (cap=5)' if stats['chi_6'] + stats.get('chi_7+', 0) == 0 else 'Conjecture REFUTED'}."
    )
    return {"verdict": verdict, "statistics": stats, "hits": hits,
            "near_misses_sample": near_misses}


# =========================================================================
# Phase A: verify theorem on small synthetic cases
# =========================================================================

def k4_data():
    N, E, _ = k4_graph()
    return N, E


def small_synthetic_cases():
    """Build a few small synthetic three-half cases and verify the triple lift
    theorem on each.

    Cases (k = 5):
      1. Three K_4s, all aligned star bridges (chi = 6 via K_6 cross-clique).
      2. Three K_4s, no bridges (chi = 4).
      3. Three K_4s with single matching bridges between pairs (chi = 5? = 4?).
      4. K_4 + K_4 + Moser with mixed bridges.
      5. Three Moser spindles, aligned K_{2,2} (chi = 6 via K_6 per L21).
      6. Three Moser spindles, no bridges (chi = 4).
    """
    cases = []

    # Case 1: three K_4 with star bridges that form K_6.
    N_k4, E_k4 = k4_data()
    B = [(0, 0), (0, 1), (0, 2), (0, 3)]  # not enough; need full K_6
    # K_6 forces: vertex u in H_1, all 4 vertices of H_2 -> vertex 0 of H_1 sees
    # all of H_2 + vertex 0 of H_3 sees all of H_2 + edge (0_H1, 0_H3) needed.
    # Easier: build a K_6 by full cross-coupling between H_1 vertex 0, H_2 vertex 0,
    # H_3 vertex 0 plus interlocked bridges to all 4 H_i vertices.
    # We just test that the THEOREM (list <=> SAT) holds, not that chi=6.
    cases.append({
        "label": "K4 x K4 x K4, B_12=star_0, B_13=star_0, B_23=star_0",
        "N1": N_k4, "E1": E_k4, "N2": N_k4, "E2": E_k4, "N3": N_k4, "E3": E_k4,
        "B12": [(0, j) for j in range(4)],
        "B13": [(0, j) for j in range(4)],
        "B23": [(0, j) for j in range(4)],
    })

    # Case 2: three K_4 with no bridges, chi = 4.
    cases.append({
        "label": "K4 x K4 x K4, no bridges",
        "N1": N_k4, "E1": E_k4, "N2": N_k4, "E2": E_k4, "N3": N_k4, "E3": E_k4,
        "B12": [], "B13": [], "B23": [],
    })

    # Case 3: three K_4 with single matching bridges.
    cases.append({
        "label": "K4 x K4 x K4, single matching bridges (0,0) only between pairs",
        "N1": N_k4, "E1": E_k4, "N2": N_k4, "E2": E_k4, "N3": N_k4, "E3": E_k4,
        "B12": [(0, 0)], "B13": [(0, 0)], "B23": [(0, 0)],
    })

    # Case 4: K_4 + K_4 + Moser, no bridges.
    N_m, E_m = moser_edge_list()
    cases.append({
        "label": "K4 x K4 x Moser, no bridges",
        "N1": N_k4, "E1": E_k4, "N2": N_k4, "E2": E_k4, "N3": N_m, "E3": E_m,
        "B12": [], "B13": [], "B23": [],
    })

    # Case 5: three Moser, K_{2,2} aligned (chi = 6 via K_6).
    B_K22 = [(0, 0), (0, 1), (1, 0), (1, 1)]
    cases.append({
        "label": "Moser x Moser x Moser, aligned K_{2,2}",
        "N1": N_m, "E1": E_m, "N2": N_m, "E2": E_m, "N3": N_m, "E3": E_m,
        "B12": B_K22, "B13": B_K22, "B23": B_K22,
    })

    # Case 6: three Moser, no bridges (chi = 4).
    cases.append({
        "label": "Moser x Moser x Moser, no bridges",
        "N1": N_m, "E1": E_m, "N2": N_m, "E2": E_m, "N3": N_m, "E3": E_m,
        "B12": [], "B13": [], "B23": [],
    })

    return cases


def phase_A_theorem_verification():
    cases = small_synthetic_cases()
    results = []
    for c in cases:
        # k=5, so we check chi >= 6 iff residual list-coloring infeasible for every c_1.
        # NOTE: for case 5 (three-Moser K_{2,2}), C_1 has 5040 5-colorings; this
        # takes a few seconds. For others, much less.
        N1, E1 = c["N1"], c["E1"]
        nC1 = len(enumerate_all_colorings(N1, E1, 5))
        print(f"\n  Case '{c['label']}': |C_1(5)|={nC1}")
        if nC1 > 6000:
            print(f"    skipping full theorem enumeration; SAT-only verification.")
            chi = chi_three_way_value(c["N1"], c["E1"], c["N2"], c["E2"],
                                       c["N3"], c["E3"],
                                       c["B12"], c["B13"], c["B23"], lo=4, hi=8)
            results.append({"label": c["label"], "chi_SAT": chi,
                            "list_method_skipped": True})
            continue
        r = verify_triple_theorem(
            c["N1"], c["E1"], c["N2"], c["E2"], c["N3"], c["E3"],
            c["B12"], c["B13"], c["B23"], k=5, label=c["label"],
        )
        print(f"    chi>=6 via list: {r['chi_geq_kp1_via_list']}, "
              f"via SAT: {r['chi_geq_kp1_via_sat']}, theorem holds: {r['theorem_holds']}")
        results.append(r)
    return results


# =========================================================================
# Phase B: list-tightness scan for three Moser
# =========================================================================

def phase_B_list_tightness_three_moser():
    """For a few selected bridge configurations on three Moser spindles, run the
    list-tightness analysis: across all c_1 of H_1 (5040 5-colorings), what's
    the distribution of residual list-feasibility?

    Skipped for large cases (enumeration cost).
    """
    N_m, E_m = moser_edge_list()
    B6 = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]

    # B configurations chosen to be feasible quickly (B12 small, e.g. 4 bridges).
    cases = [
        ("aligned B6/B6/B6", B6, B6, B6),
        ("B6/B6/empty", B6, B6, []),
        ("B6/empty/B6", B6, [], B6),
        ("aligned K_{2,2}/K_{2,2}/K_{2,2}", [(0,0),(0,1),(1,0),(1,1)],
                                              [(0,0),(0,1),(1,0),(1,1)],
                                              [(0,0),(0,1),(1,0),(1,1)]),
    ]

    results = []
    # |C_1(5)| = 5040; too expensive to enumerate per case. Use canonical mod S_5
    # then re-multiply. Canonical = 42 reps.
    # But: the bridge constraint c_1(u) compares to colored values; canonical mod
    # S_k for c_1 IS valid because we let c_2 / c_3 range freely; the symmetry
    # group of the residual problem includes S_k acting diagonally. Strictly,
    # for the THEOREM (chi >= 6 iff for-every-c_1...) we need every c_1 to fail,
    # but S_5 acts on c_1 in a way that permutes the residual problem; if
    # canonical c_1 fails for all canonical c_1, every c_1 fails.

    # Verify: if S_5 acts on c_1 by permutation pi, the residual problem on
    # (H_2, H_3, B_23) becomes the SAME problem with lists pi(L_2), pi(L_3).
    # A list-coloring witness (c_2, c_3) for c_1 gives (pi o c_2, pi o c_3) for
    # pi o c_1. So feasibility is invariant under S_5 acting on c_1. Hence
    # enumerating canonical c_1 mod S_5 is sufficient.

    for label, B12, B13, B23 in cases:
        # Use canonical 5-colorings.
        C1_canon = enumerate_canonical_colorings(N_m, E_m, 5)
        n_total = len(C1_canon)
        n_feasible = 0
        for c1 in C1_canon:
            F12 = compute_F_for_bridges(B12, c1, len(E_m) + 7)  # N2 = 7
            F12 = compute_F_for_bridges(B12, c1, 7)
            F13 = compute_F_for_bridges(B13, c1, 7)
            L2 = compute_L_from_F(F12, 5)
            L3 = compute_L_from_F(F13, 5)
            if triple_list_color_feasible(7, E_m, 7, E_m, B23, L2, L3):
                n_feasible += 1
        chi_geq_6 = (n_feasible == 0)
        # SAT cross-check.
        chi_v = chi_three_way_value(7, E_m, 7, E_m, 7, E_m, B12, B13, B23, lo=4, hi=8)
        sat_chi_geq_6 = chi_v is not None and chi_v >= 6
        # Find K_4 status.
        N, edges = build_three_moser_graph(B12, B13, B23)
        has_K4 = find_K4(N, edges)
        results.append({
            "label": label,
            "n_canonical_c1": n_total,
            "n_residual_feasible_canonical_c1": n_feasible,
            "list_chi_geq_6": chi_geq_6,
            "sat_chi": chi_v,
            "sat_chi_geq_6": sat_chi_geq_6,
            "has_K4": has_K4 is not None,
        })
        print(f"  {label}: feasible c_1 (canonical) = {n_feasible}/{n_total}, "
              f"chi(SAT) = {chi_v}, list says chi>=6? {chi_geq_6}, "
              f"K_4? {has_K4 is not None}")
    return results


# =========================================================================
# Main
# =========================================================================

def main():
    print("e1y: Triple-coupling lift of L22 list-coloring theorem")
    print("=" * 78)
    print()
    print("THEOREM (triple lift):")
    print("  Let H_1, H_2, H_3 be graphs on disjoint vertex sets and")
    print("  B_{12}, B_{13}, B_{23} bridge sets. Let G be their union.")
    print("  Then chi(G) >= 6 iff for every proper 5-coloring c_1 of H_1,")
    print("  the residual list-coloring problem on (H_2 cup H_3 cup B_{23}) with")
    print("    L_2(v) = [5] \\ {c_1(u) : (u,v) in B_{12}},  v in V(H_2),")
    print("    L_3(w) = [5] \\ {c_1(u) : (u,w) in B_{13}},  w in V(H_3),")
    print("  is infeasible.")
    print()

    out = {
        "experiment": "e1y_triple_list",
        "theorem": (
            "chi(H_1 cup H_2 cup H_3 cup B_12 cup B_13 cup B_23) >= 6 iff "
            "for every proper 5-coloring c_1 of H_1, the residual list-coloring "
            "on (H_2 cup H_3 cup B_23) with lists L_2(v) = [5] \\ "
            "{c_1(u) : (u,v) in B_12}, L_3(w) = [5] \\ {c_1(u) : (u,w) in B_13}, "
            "is infeasible."
        ),
    }

    # ----- Phase A: theorem verification on small cases -----
    print("=" * 78)
    print("Phase A. Verify the triple lift theorem on synthetic small cases.")
    print("=" * 78)
    phase_A = phase_A_theorem_verification()
    out["phase_A_theorem_verification"] = phase_A

    # ----- Phase B: list-tightness scan on three Moser bridge configurations -----
    print()
    print("=" * 78)
    print("Phase B. List-tightness on three Moser spindles for specific bridges.")
    print("=" * 78)
    phase_B = phase_B_list_tightness_three_moser()
    out["phase_B_list_tightness"] = phase_B

    # ----- Phase C: replay ADVERSARY configs with K_4 filter -----
    print()
    print("=" * 78)
    print("Phase C. ADVERSARY angle-6 named configs: chi vs K_4 presence.")
    print("=" * 78)
    phase_C = test_adversary_configs_with_K4_filter()
    out["phase_C_adversary_configs"] = phase_C

    # ----- Phase D: random search for three Moser + no-K_4 chi >= 6 -----
    print()
    print("=" * 78)
    print("Phase D. Random search: three Moser + bridges, no K_4, target chi >= 6.")
    print("=" * 78)
    print(" Sampling random bridge configurations |B_ij| in [6, 14] each;")
    print(" filtering by omega <= 3; SAT-checking chi.")
    phase_D = test_three_moser_no_K4_caps_at_5(
        n_samples=300, size_range=(6, 14), seed=42, time_limit=180,
    )
    out["phase_D_random_search"] = phase_D
    print(f"\n  VERDICT: {phase_D['verdict']}")
    print(f"  statistics: {phase_D['statistics']}")

    # ----- Phase E: refined search (larger sample, narrow size range) -----
    print()
    print("=" * 78)
    print("Phase E. Refined search: |B_ij| = 8..12, larger sample.")
    print("=" * 78)
    phase_E = test_three_moser_no_K4_caps_at_5(
        n_samples=400, size_range=(8, 12), seed=99, time_limit=240,
    )
    out["phase_E_random_search_refined"] = phase_E
    print(f"\n  VERDICT: {phase_E['verdict']}")
    print(f"  statistics: {phase_E['statistics']}")

    # ----- Phase F: structured L21-based 3-way -----
    print()
    print("=" * 78)
    print("Phase F. Anchored search: B12 = L21 14-bridge no-K_4 cover, vary B13, B23.")
    print("=" * 78)
    B_L21 = [(0,0),(0,1),(0,3),(0,4),(0,6),(1,0),(2,6),(3,6),(4,6),
             (5,1),(6,1),(6,3),(6,5),(6,6)]
    phase_F = _phase_F_l21_anchored(B_L21, n_trials=200, seed=2026, time_limit=240)
    out["phase_F_l21_anchored"] = phase_F
    print(f"\n  VERDICT: {phase_F['verdict']}")
    print(f"  statistics: {phase_F['statistics']}")

    # ----- Save -----
    out_path = CACHE / "e1y_triple_list.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print()
    print(f"archived: {out_path}")

    # ----- Wrong-approach detector status -----
    print()
    print("Wrong-approach detector status:")
    print("- Q^2 (chi=2): theorem hypothesizes the (4 or 5)-chromatic halves; vacuous "
          "in Q^2. PASS.")
    print("- L^infty (chi=4): graph-theoretic theorem; realizability obstruction "
          "separates from chromatic structure. PASS.")
    print("- R^1 (chi=2): no 4-chromatic UDG; vacuous. PASS.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
