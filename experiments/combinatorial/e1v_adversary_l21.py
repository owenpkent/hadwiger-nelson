"""e1v: ADVERSARY attack on the L20 "two 4-chromatic halves + bridges -> chi >= 5" framework.

Companion to BUILDER's e1v_bridge_covering.py.

We attack six angles. Each is a separate question with a concrete numerical
answer. Together they bound how strong / informative the L20 framework actually
is for building chi >= 6.

Angles:
  (1) Triviality boundary: how many single-bridge configurations between two
      Moser spindles force chi >= 5? (None, as it turns out: Moser has no K_4.)
  (2) Q^2 detector: verify the rational unit-distance graph is 2-chromatic
      (Woodall). Confirms L20 needs irrational coordinates.
  (3) L^infty detector: verify chi(L^infty king grid) = 4 (Chilakamarri).
      Show abstract halves-plus-bridges trivializes via K_5 in non-UDG settings.
  (4) Counterexample search: H1 = H2 = Moser; B = all 49 bridges.
      Compute chi(H1 cup H2 cup B). (Result: chi = 8 = chi(H1) + chi(H2).)
  (5) Color-class collision lower bound: union-bound on bridges needed.
  (6) Three-way coupling (KEY): build H1, H2, H3 = Moser spindles with
      various 3-way bridge configurations. Find that aligned K_{2,2} bridges
      force chi=6 trivially via K_6, refuting L20 implication 5.

Output saved to _cache/e1v_adversary_l21.json. Findings reported in
experiments/orchestrator_sessions/2026-05-26-adversary-l21.md.

Notes:
  - Uses python -u for unbuffered stdout on Windows (otherwise no progress visible).
  - Skips the all-pairs two-bridge exhaustive sweep (was ~1176 SAT calls; too slow
    on Windows). Uses random-sample scans for angle 4 instead.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import random
import sys

import networkx as nx
from pysat.solvers import Solver

# Line-buffered stdout (critical on Windows when running with redirected output).
try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass


CACHE = pathlib.Path(__file__).parent / "_cache"


# ---------- core helpers ----------

def k_color_cnf(G: nx.Graph, k: int):
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    var = lambda v, c: idx[v] * k + c + 1
    clauses = []
    for v in nodes:
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for u, w in G.edges():
        for c in range(k):
            clauses.append([-var(u, c), -var(w, c)])
    return clauses


def is_k_colorable(G: nx.Graph, k: int) -> bool:
    with Solver(name="cadical195", bootstrap_with=k_color_cnf(G, k)) as s:
        return s.solve()


def chi_in_range(G: nx.Graph, lo: int, hi: int):
    for k in range(lo, hi + 1):
        if is_k_colorable(G, k):
            return k
    return None


def moser() -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(range(7))
    G.add_edges_from([
        (0, 1), (0, 2), (1, 2), (1, 3), (2, 3),
        (0, 4), (0, 5), (4, 5), (4, 6), (5, 6),
        (3, 6),
    ])
    return G


def build_3way(B12, B13, B23) -> nx.Graph:
    H = nx.disjoint_union(nx.disjoint_union(moser(), moser()), moser())
    for u, v in B12:
        H.add_edge(u, v + 7)
    for u, v in B13:
        H.add_edge(u, v + 14)
    for u, v in B23:
        H.add_edge(u + 7, v + 14)
    return H


# ---------- angle 1: single-bridge triviality ----------

def angle1():
    print("Angle 1: single-bridge triviality")
    count = 0
    for u in range(7):
        for v in range(7):
            H = nx.disjoint_union(moser(), moser())
            H.add_edge(u, v + 7)
            if not is_k_colorable(H, 4):
                count += 1
    print(f"  single bridges forcing chi>=5: {count}/49")
    # K_4 K_4 single bridge
    H = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    H.add_edge(0, 4)
    K4_K4_single = chi_in_range(H, 4, 6)
    print(f"  K_4-K_4 + 1 bridge chi = {K4_K4_single}")
    # K_4 K_4 4-star
    H = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    for v in range(4):
        H.add_edge(0, v + 4)
    K4_K4_star = chi_in_range(H, 4, 6)
    print(f"  K_4-K_4 + 4-star chi = {K4_K4_star} (trivial K_5 route)")
    return {
        "single_bridge_moser_moser_forces_chi5": count,
        "K4_K4_single_chi": K4_K4_single,
        "K4_K4_star4_chi": K4_K4_star,
    }


# ---------- angle 2: Q^2 detector ----------

def angle2():
    print("\nAngle 2: Q^2 detector (Woodall)")
    from fractions import Fraction
    pts = set()
    for a, b, c in [(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29)]:
        for sx in (-1, 1):
            for sy in (-1, 1):
                pts.add((Fraction(sx*a, c), Fraction(sy*b, c)))
                pts.add((Fraction(sx*b, c), Fraction(sy*a, c)))
    expanded = set(pts)
    for shift in list(pts)[:8]:
        for p in list(pts)[:8]:
            expanded.add((p[0] + shift[0], p[1] + shift[1]))
    pts = list(expanded)
    G = nx.Graph()
    for i in range(len(pts)):
        G.add_node(i)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
            if d == 1:
                G.add_edge(i, j)
    chi_val = chi_in_range(G, 2, 5)
    print(f"  Q^2 sample V={G.number_of_nodes()} E={G.number_of_edges()} chi={chi_val}")
    return {"V": G.number_of_nodes(), "E": G.number_of_edges(), "chi": chi_val}


# ---------- angle 3: L^infty detector ----------

def angle3():
    print("\nAngle 3: L^infty detector (Chilakamarri)")
    G = nx.Graph()
    for i in range(5):
        for j in range(5):
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 5 and 0 <= nj < 5:
                        G.add_edge((i, j), (ni, nj))
    chi_val = chi_in_range(G, 3, 6)
    print(f"  king 5x5 V={G.number_of_nodes()} E={G.number_of_edges()} chi={chi_val}")
    return {"V": G.number_of_nodes(), "E": G.number_of_edges(), "chi": chi_val}


# ---------- angle 4: full bridges ----------

def angle4():
    print("\nAngle 4: all 49 cross-bridges between two Moser spindles")
    H = nx.disjoint_union(moser(), moser())
    for u in range(7):
        for v in range(7):
            H.add_edge(u, v + 7)
    chi_all = chi_in_range(H, 4, 9)
    print(f"  V={H.number_of_nodes()} E={H.number_of_edges()} chi={chi_all}")

    # Boundary scan
    random.seed(0)
    boundary = []
    for size in range(14, 22):
        counts = {4: 0, 5: 0, 6: 0}
        for trial in range(10):
            all_b = [(u, v) for u in range(7) for v in range(7)]
            random.shuffle(all_b)
            H = nx.disjoint_union(moser(), moser())
            for u, v in all_b[:size]:
                H.add_edge(u, v + 7)
            cv = chi_in_range(H, 4, 6)
            counts[cv] = counts.get(cv, 0) + 1
        boundary.append({"size": size, **counts})
        print(f"  |B|={size}: {counts}")
    return {"all_49_chi": chi_all, "boundary_scan": boundary}


# ---------- angle 5: collision bound ----------

def angle5():
    print("\nAngle 5: color-class collision lower bound")
    G = moser()
    k = 4
    nodes = list(G.nodes())
    N = len(nodes)
    var = lambda i, c: i * k + c + 1
    clauses = []
    for i in range(N):
        clauses.append([var(i, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(i, c1), -var(i, c2)])
    for u, w in G.edges():
        for c in range(k):
            clauses.append([-var(u, c), -var(w, c)])
    all_cols = []
    with Solver(name="cadical195", bootstrap_with=clauses) as s:
        while s.solve():
            m = s.get_model()
            col = [None] * N
            for i in range(N):
                for c in range(k):
                    if m[i * k + c] > 0:
                        col[i] = c
                        break
            all_cols.append(tuple(col))
            s.add_clause([-(i * k + col[i] + 1) for i in range(N)])
    canon_set = set()
    canon_cols = []
    for col in all_cols:
        relabel = {}
        nl = 0
        canon = []
        for c in col:
            if c not in relabel:
                relabel[c] = nl
                nl += 1
            canon.append(relabel[c])
        key = tuple(canon)
        if key not in canon_set:
            canon_set.add(key)
            canon_cols.append(canon)
    freq = [[0] * 4 for _ in range(N)]
    for col in all_cols:
        for i in range(N):
            freq[i][col[i]] += 1
    total = len(all_cols)
    f_uv = [[sum(freq[u][c] * freq[v][c] for c in range(4)) / (total * total)
             for v in range(N)] for u in range(N)]
    flat = [f_uv[u][v] for u in range(N) for v in range(N)]
    avg = sum(flat) / len(flat)
    print(f"  total 4-colorings: {len(all_cols)}, canonical: {len(canon_cols)}")
    print(f"  f(u,v) min={min(flat):.4f} avg={avg:.4f} max={max(flat):.4f}")
    print(f"  union-bound lower bound |B| >= {1/avg:.2f}")
    B6 = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
    B6_total = sum(f_uv[u][v] for u, v in B6)
    print(f"  BUILDER's B6 total f = {B6_total:.4f} (looseness factor {B6_total:.2f})")
    return {
        "n_colorings": len(all_cols),
        "n_canonical": len(canon_cols),
        "f_min": min(flat),
        "f_avg": avg,
        "f_max": max(flat),
        "union_bound_LB_B": 1 / avg,
        "B6_total_f": B6_total,
    }


# ---------- angle 6: three-way coupling (KEY) ----------

def angle6():
    print("\nAngle 6: three-way coupling")
    B6 = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
    B_K22 = [(0,0),(0,1),(1,0),(1,1)]
    B_K23_shift = [(0,3),(0,4),(0,5),(1,3),(1,4),(1,5)]

    configs = [
        ("B6 aligned all", B6, B6, B6),
        ("B6/B6/empty", B6, B6, []),
        ("B6 chain", B6, [], B6),
        ("B6 + perm(B6)", B6, B6, [(u, (v + 3) % 7) for u, v in B6]),
        ("K_{2,2} aligned (K_6 trivial)", B_K22, B_K22, B_K22),
        ("K_{2,3} shifted (no K_3)", B_K23_shift, B_K23_shift, B_K23_shift),
        ("B6 minus (0,0)", B6[1:], B6[1:], B6[1:]),
        ("B6 minus (0,2)", [b for b in B6 if b != (0, 2)],
         [b for b in B6 if b != (0, 2)], [b for b in B6 if b != (0, 2)]),
    ]
    results = []
    for label, B12, B13, B23 in configs:
        H = build_3way(B12, B13, B23)
        # Pairwise chi (H1 + H2 + B12)
        Hp = nx.disjoint_union(moser(), moser())
        for u, v in B12:
            Hp.add_edge(u, v + 7)
        chi_p = chi_in_range(Hp, 4, 6)
        chi_3 = chi_in_range(H, 4, 8)
        print(f"  {label}: pairwise={chi_p}, 3-way={chi_3}")
        results.append({
            "label": label,
            "B_sizes": (len(B12), len(B13), len(B23)),
            "pairwise_chi": chi_p,
            "three_way_chi": chi_3,
        })

    # Three K_4s + K_{1,4} stars
    H = nx.disjoint_union(nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4)),
                         nx.complete_graph(4))
    for v in range(4):
        H.add_edge(0, v + 4)
        H.add_edge(0, v + 8)
        H.add_edge(4, v + 8)
    chi_K4_star = chi_in_range(H, 4, 8)
    print(f"  Three K_4 + K_{{1,4}} stars: chi={chi_K4_star}")
    results.append({"label": "Three K_4 + K_{1,4}", "three_way_chi": chi_K4_star})

    # Verify K_6 in the K_{2,2} aligned Moser case
    H = build_3way(B_K22, B_K22, B_K22)
    S = [0, 1, 7, 8, 14, 15]
    K6_edges = sum(1 for i in S for j in S if i < j and H.has_edge(i, j))
    print(f"  Aligned K_{{2,2}} 3-way: K_6 on {S} has {K6_edges}/15 edges (should be 15)")
    return {"configs": results, "K22_aligned_K6_edges": K6_edges}


# ---------- main ----------

def main():
    CACHE.mkdir(exist_ok=True)
    print("=" * 60)
    print("ADVERSARY e1v: attack on L20 'halves + bridges -> chi>=5'")
    print("=" * 60)
    results = {
        "experiment": "e1v_adversary_l21",
        "angle1": angle1(),
        "angle2": angle2(),
        "angle3": angle3(),
        "angle4": angle4(),
        "angle5": angle5(),
        "angle6": angle6(),
    }
    out = CACHE / "e1v_adversary_l21.json"
    with out.open("w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\narchived: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
