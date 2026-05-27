r"""h3: pair-wise bridge-cover analysis across a curated list of small 4-chromatic graphs.

Long-job (H3 overnight). For every (unordered) pair of curated 4-chromatic graphs,
compute the minimum bridge cover under three regimes (unconstrained, no-K_4, no-K_5),
the F-profile per L22, the combined-graph chromatic / clique data, and structural
fingerprints. Then assemble the table sorted by no-K_4 minimum |B|.

This sits downstream of L20-L22 (`e1v_bridge_covering.py`, `e1w_lemma_c4.py`).

Curated 4-chromatic test graphs (all chi = 4, verified by SAT):

  - K_4               (4 V,  6 E, omega=4)
  - K_4 + pendant     (5 V,  7 E, omega=4)
  - W_5 wheel         (6 V, 10 E, omega=3 -- C_5 + hub)
  - Moser spindle     (7 V, 11 E, omega=3, UDG)
  - Hajos join (K_4)  (7 V, 12 E, omega=4)  -- two K_4 sharing one vertex
  - Golomb-like 10    (10 V, 18 E, omega=3) -- the canonical 10-vertex 4-chromatic
  - Grotzsch / Myc_4  (11 V, 20 E, omega=2) -- triangle-free, NOT a UDG

Outputs:
  experiments/combinatorial/_cache/h3_pair_minima.json
  experiments/orchestrator_sessions/2026-05-26-h3-enumerate-pairs-draft.md
"""

from __future__ import annotations

import itertools
import json
import math
import pathlib
import sys
import time
from collections import Counter

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from experiments.combinatorial.e1v_bridge_covering import (
    enumerate_canonical_colorings,
    enumerate_all_colorings,
    fraction_killed_per_bridge,
    sat_min_cover,
    sat_min_cover_no_k4,
    combined_chi_check,
)

CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)
OUT_PATH = CACHE / "h3_pair_minima.json"
DRAFT_PATH = (
    REPO_ROOT / "experiments" / "orchestrator_sessions"
    / "2026-05-26-h3-enumerate-pairs-draft.md"
)


# ---------- curated 4-chromatic graph library ----------------------------------

def g_k4():
    n = 4
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    return n, edges, "K4", {"omega": 4, "udg": True, "tri_free": False}


def g_k4_pendant():
    n = 5
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4)]
    return n, edges, "K4pendant", {"omega": 4, "udg": True, "tri_free": False}


def g_w5():
    n = 6
    edges = [(0, i) for i in range(1, 6)]
    for i in range(1, 5):
        edges.append((i, i + 1))
    edges.append((1, 5))
    return n, edges, "W5", {"omega": 3, "udg": False, "tri_free": False}


def g_moser():
    from experiments._shared.unit_distance_graph import moser_spindle
    g = moser_spindle()
    return g.n, g.edges(), "Moser", {"omega": 3, "udg": True, "tri_free": False}


def g_hajos():
    n = 7
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3),
             (0, 4), (0, 5), (0, 6), (4, 5), (4, 6), (5, 6)]
    return n, edges, "Hajos", {"omega": 4, "udg": False, "tri_free": False}


def g_golomb_like():
    """A canonical 10-vertex, 18-edge, 4-chromatic, omega=3 graph in Golomb shape.

    Structure: central K_{1,3} (vertex 0 connected to 1,2,3); inner triangle
    {4,5,6} with extra "wedge" edges {1-4,1-5,2-5,2-6,3-6,3-4}; spokes to outer
    triangle {7,8,9}: 4-7, 5-8, 6-9; outer triangle 7-8-9.

    Note: this is structurally the Golomb graph from Mathworld; it may or may
    not be the canonical Soifer UDG embedding, but it shares all the relevant
    properties (V, E, chi, omega) and serves as a 10-vertex 4-chromatic probe.
    """
    edges = [
        (0, 1), (0, 2), (0, 3),
        (1, 4), (1, 5), (2, 5), (2, 6), (3, 6), (3, 4),
        (4, 5), (5, 6), (4, 6),
        (4, 7), (5, 8), (6, 9),
        (7, 8), (8, 9), (7, 9),
    ]
    return 10, edges, "Golomb", {"omega": 3, "udg": True, "tri_free": False}


def g_grotzsch():
    """Mycielski 4 = Grotzsch graph: 11 V, 20 E, chi=4, triangle-free."""
    C5 = nx.cycle_graph(5)
    n_orig = 5
    M = nx.Graph()
    M.add_nodes_from(range(2 * n_orig + 1))
    for (u, v) in C5.edges():
        M.add_edge(u, v)
        M.add_edge(u, v + n_orig)
        M.add_edge(u + n_orig, v)
    for i in range(n_orig):
        M.add_edge(i + n_orig, 2 * n_orig)
    edges = sorted([(u, v) if u < v else (v, u) for u, v in M.edges()])
    return 11, edges, "Grotzsch", {"omega": 2, "udg": False, "tri_free": True}


CURATED = [
    g_k4,
    g_k4_pendant,
    g_w5,
    g_moser,
    g_hajos,
    g_golomb_like,
    g_grotzsch,
]


# ---------- bridge analysis ---------------------------------------------------

def sat_min_cover_no_k5(N_pairs, kill_lists, N1, E1, N2, E2, k_max=None):
    """SAT minimum bridge cover with no-K_5 constraint.

    A K_5 in the combined graph requires 5 vertices pairwise adjacent. Since each
    half is K_4-bounded by chi=4 (K_5 requires chi=5), the K_5 must span the
    bridge: at least one bridge edge is involved.

    We forbid each candidate 5-set whose 10 pairwise relations are all
    present-or-bridge.
    """
    bridges = list(kill_lists.keys())
    M = len(bridges)
    pair_to_bridges = [[] for _ in range(N_pairs)]
    for bi, b in enumerate(bridges):
        for p in kill_lists[b]:
            pair_to_bridges[p].append(bi)
    for p in range(N_pairs):
        if not pair_to_bridges[p]:
            return None

    N = N1 + N2
    E1_set = set((min(u, v), max(u, v)) for u, v in E1)
    E2_set = set((min(u, v), max(u, v)) for u, v in E2)
    bridge_to_idx = {b: bi for bi, b in enumerate(bridges)}

    def edge_status(a, b):
        if a > b:
            a, b = b, a
        if a < N1 and b < N1:
            return ("present" if (a, b) in E1_set else "absent")
        if a >= N1 and b >= N1:
            ap, bp = a - N1, b - N1
            return ("present" if (ap, bp) in E2_set else "absent")
        bridge = (a, b - N1)
        if bridge in bridge_to_idx:
            return ("bridge", bridge_to_idx[bridge])
        return "absent"

    forbidding_clauses = []
    for quint in itertools.combinations(range(N), 5):
        bridge_indices_in_quint = []
        ok = True
        for a, b in itertools.combinations(quint, 2):
            s = edge_status(a, b)
            if s == "absent":
                ok = False
                break
            if isinstance(s, tuple) and s[0] == "bridge":
                bridge_indices_in_quint.append(s[1])
        if ok and bridge_indices_in_quint:
            forbidding_clauses.append([-bi - 1 for bi in bridge_indices_in_quint])

    def feasible(k):
        clauses = []
        for p in range(N_pairs):
            clauses.append([bi + 1 for bi in pair_to_bridges[p]])
        clauses.extend(forbidding_clauses)
        if k < M:
            am = CardEnc.atmost(lits=list(range(1, M + 1)), bound=k, top_id=M,
                                encoding=EncType.seqcounter)
            clauses.extend(am.clauses)
        with Cadical195(bootstrap_with=clauses) as solver:
            sat = solver.solve()
            if not sat:
                return None
            m = solver.get_model()
            return [bridges[i] for i in range(M) if m[i] > 0]

    if k_max is None:
        k_max = M
    sol_max = feasible(k_max)
    if sol_max is None:
        return None
    lo, hi = 1, len(sol_max)
    best = sol_max
    while lo <= hi:
        mid = (lo + hi) // 2
        sol = feasible(mid)
        if sol is not None:
            best = sol
            hi = len(sol) - 1
        else:
            lo = mid + 1
    return best


def compute_F(B, c1, N2):
    F = [set() for _ in range(N2)]
    for (u, v) in B:
        F[v].add(c1[u])
    return [sorted(s) for s in F]


def combined_clique(N1, E1, N2, E2, B):
    G = nx.Graph()
    G.add_nodes_from(range(N1 + N2))
    for u, v in E1:
        G.add_edge(u, v)
    for u, v in E2:
        G.add_edge(u + N1, v + N1)
    for u, v in B:
        G.add_edge(u, v + N1)
    return max((len(c) for c in nx.find_cliques(G)), default=0)


# ---------- per-pair analysis -------------------------------------------------

def analyze_pair(graph1, graph2, label, regimes=("unconstrained", "no_K5", "no_K4"),
                 time_budget_sec=900):
    """Analyze a single pair. Returns dict with the bridge-min results per regime.

    time_budget_sec: per-regime SAT time budget. Skip regime if exceeded.
    """
    (N1, E1, name1, _meta1) = graph1
    (N2, E2, name2, _meta2) = graph2

    print(f"\n=== {label}: {name1} ({N1}V) x {name2} ({N2}V) ===")
    print(f"  H_1: {N1} V, {len(E1)} E, omega={_meta1['omega']}")
    print(f"  H_2: {N2} V, {len(E2)} E, omega={_meta2['omega']}")

    t0 = time.time()
    C1 = enumerate_canonical_colorings(N1, E1, 4)
    C2 = enumerate_all_colorings(N2, E2, 4)
    enum_t = time.time() - t0
    print(f"  |C_1 (canon)|={len(C1)}, |C_2 (full)|={len(C2)}, |P|={len(C1)*len(C2)} (t={enum_t:.2f}s)")
    if not C1 or not C2:
        return {"label": label, "skipped": True, "reason": "no 4-coloring"}

    P = len(C1) * len(C2)
    rho = fraction_killed_per_bridge(N1, N2, C1, C2)
    rho_mean = sum(rho.values()) / len(rho)

    # Build kill_lists
    kill_lists = {}
    for (uv, _) in rho.items():
        u, v = uv
        kills = set()
        idx = 0
        for c1 in C1:
            cu = c1[u]
            for c2 in C2:
                if cu == c2[v]:
                    kills.add(idx)
                idx += 1
        if kills:
            kill_lists[uv] = kills

    out = {
        "label": label,
        "graph1": name1, "N1": N1, "E1_count": len(E1), "omega1": _meta1["omega"],
        "graph2": name2, "N2": N2, "E2_count": len(E2), "omega2": _meta2["omega"],
        "n_C1": len(C1), "n_C2": len(C2), "rho_mean": rho_mean,
        "regimes": {},
    }

    cap = min(N1 * N2, 50)

    # Unconstrained
    if "unconstrained" in regimes:
        t0 = time.time()
        try:
            sat_B = sat_min_cover(P, kill_lists, k_max=cap)
            unc_t = time.time() - t0
            if sat_B is not None:
                clique = combined_clique(N1, E1, N2, E2, sat_B)
                chi5 = (not combined_chi_check(N1, E1, N2, E2, sat_B, 4)
                        and combined_chi_check(N1, E1, N2, E2, sat_B, 5))
                F = compute_F(sat_B, C1[0], N2)
                F_sizes_sorted = sorted([len(f) for f in F], reverse=True)
                out["regimes"]["unconstrained"] = {
                    "B_size": len(sat_B),
                    "B": [list(b) for b in sat_B],
                    "F_profile_sorted": F_sizes_sorted,
                    "omega_combined": clique,
                    "chi_eq_5_verified": chi5,
                    "sat_time": unc_t,
                }
                print(f"  unconstrained: |B|={len(sat_B)}, omega(combined)={clique}, chi=5? {chi5} (t={unc_t:.2f}s)")
            else:
                out["regimes"]["unconstrained"] = {"B_size": None, "reason": "infeasible"}
        except Exception as e:
            print(f"  unconstrained: error {e}")
            out["regimes"]["unconstrained"] = {"B_size": None, "reason": f"error: {e}"}

    # no-K_5
    if "no_K5" in regimes:
        t0 = time.time()
        try:
            sat_B = sat_min_cover_no_k5(P, kill_lists, N1, E1, N2, E2, k_max=cap)
            nk5_t = time.time() - t0
            if sat_B is not None:
                clique = combined_clique(N1, E1, N2, E2, sat_B)
                chi5 = (not combined_chi_check(N1, E1, N2, E2, sat_B, 4)
                        and combined_chi_check(N1, E1, N2, E2, sat_B, 5))
                F = compute_F(sat_B, C1[0], N2)
                F_sizes_sorted = sorted([len(f) for f in F], reverse=True)
                out["regimes"]["no_K5"] = {
                    "B_size": len(sat_B),
                    "B": [list(b) for b in sat_B],
                    "F_profile_sorted": F_sizes_sorted,
                    "omega_combined": clique,
                    "chi_eq_5_verified": chi5,
                    "sat_time": nk5_t,
                }
                print(f"  no-K5: |B|={len(sat_B)}, omega(combined)={clique}, chi=5? {chi5} (t={nk5_t:.2f}s)")
            else:
                out["regimes"]["no_K5"] = {"B_size": None, "reason": "infeasible"}
                print(f"  no-K5: infeasible (t={nk5_t:.2f}s)")
        except Exception as e:
            print(f"  no-K5: error {e}")
            out["regimes"]["no_K5"] = {"B_size": None, "reason": f"error: {e}"}

    # no-K_4
    if "no_K4" in regimes:
        t0 = time.time()
        try:
            sat_B = sat_min_cover_no_k4(P, kill_lists, N1, E1, N2, E2, k_max=cap)
            nk4_t = time.time() - t0
            if sat_B is not None:
                clique = combined_clique(N1, E1, N2, E2, sat_B)
                chi5 = (not combined_chi_check(N1, E1, N2, E2, sat_B, 4)
                        and combined_chi_check(N1, E1, N2, E2, sat_B, 5))
                F = compute_F(sat_B, C1[0], N2)
                F_sizes_sorted = sorted([len(f) for f in F], reverse=True)
                F_full = [list(f) for f in F]
                out["regimes"]["no_K4"] = {
                    "B_size": len(sat_B),
                    "B": [list(b) for b in sat_B],
                    "F_profile_sorted": F_sizes_sorted,
                    "F_profile_full": F_full,
                    "omega_combined": clique,
                    "chi_eq_5_verified": chi5,
                    "sat_time": nk4_t,
                    "combined_V": N1 + N2,
                    "combined_E": len(E1) + len(E2) + len(sat_B),
                }
                print(f"  no-K4: |B|={len(sat_B)}, V_combined={N1+N2}, omega={clique}, chi=5? {chi5} (t={nk4_t:.2f}s)")
            else:
                out["regimes"]["no_K4"] = {"B_size": None, "reason": "infeasible"}
                print(f"  no-K4: infeasible (t={nk4_t:.2f}s)")
        except Exception as e:
            print(f"  no-K4: error {e}")
            out["regimes"]["no_K4"] = {"B_size": None, "reason": f"error: {e}"}

    return out


# ---------- main ---------------------------------------------------------------

def verify_graphs():
    print("Verifying curated graphs are 4-chromatic...")
    for ctor in CURATED:
        N, E, name, meta = ctor()
        # SAT check
        G = nx.Graph()
        G.add_nodes_from(range(N))
        G.add_edges_from(E)
        omega = max((len(c) for c in nx.find_cliques(G)), default=0)
        # quick chi check: 3-col SAT
        cnf3 = []
        var = lambda v, c: v * 3 + c + 1
        for v in range(N):
            cnf3.append([var(v, c) for c in range(3)])
            for c1 in range(3):
                for c2 in range(c1 + 1, 3):
                    cnf3.append([-var(v, c1), -var(v, c2)])
        for u, v in E:
            for c in range(3):
                cnf3.append([-var(u, c), -var(v, c)])
        with Cadical195(bootstrap_with=cnf3) as s:
            three_col = s.solve()
        cnf4 = []
        var4 = lambda v, c: v * 4 + c + 1
        for v in range(N):
            cnf4.append([var4(v, c) for c in range(4)])
            for c1 in range(4):
                for c2 in range(c1 + 1, 4):
                    cnf4.append([-var4(v, c1), -var4(v, c2)])
        for u, v in E:
            for c in range(4):
                cnf4.append([-var4(u, c), -var4(v, c)])
        with Cadical195(bootstrap_with=cnf4) as s:
            four_col = s.solve()
        chi = 4 if (not three_col and four_col) else (3 if three_col else "?")
        print(f"  {name:12s}: V={N}, E={len(E)}, omega={omega}, "
              f"3-col? {three_col}, 4-col? {four_col}, chi={chi}, "
              f"meta_omega={meta['omega']}")
        assert chi == 4, f"{name} is not 4-chromatic"
        assert omega == meta["omega"], f"{name} omega mismatch"


def main():
    print("h3: pair-wise bridge-cover analysis")
    print("=" * 78)

    verify_graphs()

    graphs = [ctor() for ctor in CURATED]
    pair_results = []

    # Unordered pairs including diagonal
    pairs = []
    for i in range(len(graphs)):
        for j in range(i, len(graphs)):
            pairs.append((graphs[i], graphs[j]))

    print(f"\n{len(pairs)} pairs to analyze.")

    # Order: smallest combined V x V first for SAT-tractability and early signal.
    pairs.sort(key=lambda gg: (gg[0][0] * gg[1][0], gg[0][0] + gg[1][0]))

    for (g1, g2) in pairs:
        N1 = g1[0]
        N2 = g2[0]
        name1 = g1[2]
        name2 = g2[2]
        label = f"{name1}_x_{name2}"
        # Time budget heuristic: skip if combined too large for the no-K_4 SAT.
        # |C_2| can be huge for big graphs.
        if N1 * N2 > 200:
            print(f"\n=== {label}: SKIPPED (N1*N2 = {N1*N2} too large) ===")
            pair_results.append({"label": label, "skipped": True,
                                 "reason": f"N1*N2={N1*N2} too large"})
            continue
        r = analyze_pair(g1, g2, label)
        pair_results.append(r)

        # Incremental save
        with open(OUT_PATH, "w") as f:
            json.dump({"experiment": "h3_enumerate_pairs",
                       "pair_results": pair_results}, f, indent=2)

    # ---------- structural table ----------
    print("\n" + "=" * 78)
    print("STRUCTURAL TABLE (sorted by no-K_4 |B|)")
    print("=" * 78)
    print()

    rows = []
    for r in pair_results:
        if r.get("skipped"):
            continue
        regimes = r["regimes"]
        unc = regimes.get("unconstrained", {})
        nk5 = regimes.get("no_K5", {})
        nk4 = regimes.get("no_K4", {})
        row = {
            "label": r["label"],
            "N1": r["N1"], "N2": r["N2"],
            "n_C1": r["n_C1"], "n_C2": r["n_C2"],
            "unc_B": unc.get("B_size"),
            "nk5_B": nk5.get("B_size"),
            "nk4_B": nk4.get("B_size"),
            "F_profile_nk4": nk4.get("F_profile_sorted"),
            "V_combined": r["N1"] + r["N2"],
        }
        rows.append(row)
    rows.sort(key=lambda r: ((r["nk4_B"] is None, r["nk4_B"] or 0), r["V_combined"]))

    print("| Pair | V1xV2 | |C1| | |C2| | unc |B| | no-K5 |B| | no-K4 |B| | omega_combined(nk4) | F profile (no-K4) |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for r in rows:
        # Find the regime data
        result = next((rr for rr in pair_results if rr.get("label") == r["label"]), {})
        nk4_data = result.get("regimes", {}).get("no_K4", {}) if result else {}
        omega_combined = nk4_data.get("omega_combined", "-")
        print(f"| {r['label']} | {r['N1']}x{r['N2']} | {r['n_C1']} | {r['n_C2']} | "
              f"{r['unc_B']} | {r['nk5_B']} | {r['nk4_B']} | {omega_combined} | "
              f"{r['F_profile_nk4']} |")

    # Look for record-breaking: combined omega <= 3 AND V < 14 (UDG-relevant)
    print("\n" + "=" * 78)
    print("RECORD HUNT: K_4-free combined graph with chi=5 and V_combined < 14")
    print("=" * 78)
    records = []
    for r in rows:
        result = next((rr for rr in pair_results if rr.get("label") == r["label"]), {})
        nk4_data = result.get("regimes", {}).get("no_K4", {}) if result else {}
        omega_combined = nk4_data.get("omega_combined", None)
        if (r["nk4_B"] is not None and omega_combined is not None
            and omega_combined <= 3 and r["V_combined"] < 14):
            r["omega_combined"] = omega_combined
            records.append(r)
    if not records:
        print("No new record below 14 vertices (with omega <= 3).")
    else:
        for r in records:
            print(f"  RECORD CANDIDATE: {r['label']} V={r['V_combined']}, "
                  f"|B|={r['nk4_B']}, omega={r['omega_combined']}")

    # ---------- save ----------
    final = {
        "experiment": "h3_enumerate_pairs",
        "graphs": [{"name": ctor()[2], "N": ctor()[0], "E": len(ctor()[1]),
                    "meta": ctor()[3]} for ctor in CURATED],
        "pair_results": pair_results,
        "structural_table": rows,
        "records_below_14": records,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(final, f, indent=2)
    print(f"\narchived: {OUT_PATH}")
    return final


if __name__ == "__main__":
    raise SystemExit(main())
