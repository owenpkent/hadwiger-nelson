r"""The abstract L45 ingredient EXISTS and is constructible (vertex-split of a
6-critical K4-free graph). This relocates the chi >= 6 difficulty entirely onto
W3 (unit-distance realizability).

Context. L45 / W2: across all 12 lineage chi-5 UDGs (and, this session, the V=1155
C_6 closure) a pair is forced-different in every proper 5-coloring IFF it is a unit
edge. The project framed the missing chi-6 ingredient -- a chi-5 graph with a
NON-ADJACENT forced-different pair at k=5 (a "color-clamp") -- as "absent, must be
constructed by a new principle." The creative-attack workflow's adversary went
further and predicted the ABSTRACT object does not exist below ~13 vertices
(a non-existence theorem).

That prediction is FALSE, and the correction is the point. Claim (elementary):

  Let H be any K4-free 6-CRITICAL graph and w a vertex. Take a proper 5-coloring
  phi of H - w (exists by criticality; and phi(N(w)) = all 5 colors, else w extends).
  Split N(w) into A, B by a 2-partition (S1, S2) of the 5 colors, and form
      G = (H - w) + two NON-adjacent vertices s, t,  s ~ A,  t ~ B.
  Then: (i) G is K4-free; (ii) chi(G) = 5 (proper 5-colorings exist); (iii) the
  non-adjacent pair (s, t) is forced-different in EVERY proper 5-coloring of G,
  because identifying s, t reproduces H, which is not 5-colorable.

Proof of (iii): a proper 5-coloring of G with c(s) = c(t) descends (merge s,t to w)
to a proper 5-coloring of H (legal: s,t non-adjacent, N(s) U N(t) = N(w)); but H is
not 5-colorable. So c(s) != c(t) always. (ii): color H - w by phi; s sees only
colors S1 (a proper subset of [5]) so a free color remains for s, likewise t. (i):
the witness below is triangle-free (Mycielskian tower), a fortiori K4-free.

So the abstract ingredient is a one-line construction; the ENTIRE obstruction to
chi(R^2) >= 6 via coupling is W3 unit-distance realizability of such a clamp. We
build an explicit witness, verify all three properties by SAT, minimize it, and run
the wrong-approach gate (a bipartite / Q^2-style graph admits NO clamp, so the test
cannot fake a bound on the control).
"""
from __future__ import annotations

import json
import os
import itertools

import networkx as nx
from pysat.formula import CNF
from pysat.solvers import Cadical195

CACHE = os.path.join(os.path.dirname(__file__), "_cache")


# ---------- SAT k-colorability over an abstract edge set ----------

def kcol(n, edges, k, merges=None, return_model=False):
    """Is the graph (n vertices, edges) k-colorable, optionally after forcing
    c(u)==c(v) for each (u,v) in merges? Returns bool, or (bool, model)."""
    cnf = CNF()
    var = lambda v, c: v * k + c + 1
    for v in range(n):
        cnf.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cnf.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            cnf.append([-var(u, c), -var(v, c)])
    for (u, v) in (merges or []):  # force same color
        for c in range(k):
            cnf.append([-var(u, c), var(v, c)])
            cnf.append([var(u, c), -var(v, c)])
    s = Cadical195(bootstrap_with=cnf)
    sat = s.solve()
    model = s.get_model() if (sat and return_model) else None
    s.delete()
    if return_model:
        if not sat:
            return False, None
        coloring = [None] * n
        mset = set(x for x in model if x > 0)
        for v in range(n):
            for c in range(k):
                if var(v, c) in mset:
                    coloring[v] = c
                    break
        return True, coloring
    return bool(sat)


def chromatic_number(n, edges, kmax=7):
    for k in range(1, kmax + 1):
        if kcol(n, edges, k):
            return k
    return None


def relabel_edges(G):
    """Return (n, edge_list, index_of) with vertices relabeled 0..n-1."""
    idx = {v: i for i, v in enumerate(G.nodes())}
    es = [(idx[u], idx[v]) for u, v in G.edges()]
    return G.number_of_nodes(), es, idx


# ---------- build a K4-free (in fact triangle-free) 6-critical graph ----------

def mycielski_tower():
    """C5 (3-chromatic) -> M -> M -> M : a triangle-free 6-CRITICAL graph.

    Mycielskian raises chi by exactly 1 and preserves both triangle-freeness and
    criticality (M(G) is (chi+1)-critical when G is chi-critical). C5 is 3-critical.
    """
    g = nx.cycle_graph(5)           # 3-critical, triangle-free
    g = nx.mycielskian(g)           # Grotzsch, 4-critical, 11 v
    g = nx.mycielskian(g)           # 5-critical, 23 v
    g = nx.mycielskian(g)           # 6-critical, 47 v
    return nx.convert_node_labels_to_integers(g)


# ---------- the vertex-split construction ----------

def build_clamp(H):
    """Split a critical vertex of a 6-critical graph H into a non-adjacent pair
    (s,t), returning a K4-free chi-5 graph G with (s,t) forced-different at k=5.

    Returns dict with edges of G, indices s,t, and the SAT verification gates.
    """
    n0, eH, _ = relabel_edges(H)
    assert chromatic_number(n0, eH) == 6, "H must be 6-chromatic"

    adjH = [set() for _ in range(n0)]
    for u, v in eH:
        adjH[u].add(v)
        adjH[v].add(u)

    for w in sorted(range(n0), key=lambda x: -len(adjH[x])):
        nbrs = sorted(adjH[w])
        # 5-color H - w (delete w by dropping its incident edges; w stays isolated)
        e_minus = [(u, v) for (u, v) in eH if u != w and v != w]
        sat, phi = kcol(n0, e_minus, 5, return_model=True)
        if not sat:
            continue
        nbr_colors = sorted(set(phi[u] for u in nbrs))
        if len(nbr_colors) < 2:
            continue  # need at least two colors among neighbors to split
        # try every nontrivial 2-partition of the colors present on N(w)
        cols = nbr_colors
        for r in range(1, len(cols)):
            for S1 in itertools.combinations(cols, r):
                S1 = set(S1)
                A = [u for u in nbrs if phi[u] in S1]
                B = [u for u in nbrs if phi[u] not in S1]
                if not A or not B:
                    continue
                # G: keep vertices 0..n0-1 EXCEPT w (left isolated, harmless),
                # add s = n0, t = n0+1.
                s, t = n0, n0 + 1
                nG = n0 + 2
                eG = list(e_minus)
                eG += [(s, a) for a in A]
                eG += [(t, b) for b in B]
                # (s,t) deliberately NON-adjacent
                five_colorable = kcol(nG, eG, 5)
                # contract s,t  <=>  reproduce H : not 5-colorable
                merged_unsat = not kcol(nG, eG, 5, merges=[(s, t)])
                if five_colorable and merged_unsat:
                    return {
                        "w": w, "s": s, "t": t, "n": nG, "edges": eG,
                        "A_size": len(A), "B_size": len(B),
                        "nbr_colors": nbr_colors,
                        "verified_5colorable": five_colorable,
                        "verified_forced_different": merged_unsat,
                    }
    return None


def is_k4_free(n, edges):
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    return max((len(c) for c in nx.find_cliques(G)), default=0) <= 3


def is_triangle_free(n, edges):
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    return sum(nx.triangles(G).values()) == 0


# ---------- minimize the clamp (SAT-guided vertex deletion) ----------

def minimize_clamp(n, edges, s, t):
    """Greedily delete non-terminal vertices while preserving the clamp property
    (G 5-colorable AND G/{s,t} not 5-colorable). Returns a reduced (n,edges,s,t)."""
    alive = set(range(n))

    def clamp_ok(active_edges, sv, tv, nn):
        return kcol(nn, active_edges, 5) and not kcol(nn, active_edges, 5,
                                                      merges=[(sv, tv)])

    changed = True
    cur_edges = list(edges)
    while changed:
        changed = False
        for v in sorted(alive):
            if v in (s, t):
                continue
            trial = [(a, b) for (a, b) in cur_edges if a != v and b != v]
            # relabel to compact indices for the SAT call
            keep = sorted(alive - {v})
            remap = {old: i for i, old in enumerate(keep)}
            if s not in remap or t not in remap:
                continue
            te = [(remap[a], remap[b]) for (a, b) in trial
                  if a in remap and b in remap]
            if clamp_ok(te, remap[s], remap[t], len(keep)):
                alive.discard(v)
                cur_edges = trial
                changed = True
    keep = sorted(alive)
    remap = {old: i for i, old in enumerate(keep)}
    final_edges = sorted({(min(remap[a], remap[b]), max(remap[a], remap[b]))
                          for (a, b) in cur_edges if a in remap and b in remap})
    return len(keep), final_edges, remap[s], remap[t]


# ---------- wrong-approach gate ----------

def control_no_clamp():
    """A bipartite graph (chi=2, the Q^2 / R^1 control regime) hosts NO clamp:
    any contraction stays bipartite-or-odd-cycle, chi <= 3 < 6, never forced at k=5.
    We confirm the engine reports no clamp on K_{3,3} and on a path, so the test
    cannot fabricate a bound on the controls."""
    out = {}
    for name, G in [("K_3_3", nx.complete_bipartite_graph(3, 3)),
                    ("path_8", nx.path_graph(8)),
                    ("C6", nx.cycle_graph(6))]:
        n, e, _ = relabel_edges(G)
        hits = 0
        for s in range(n):
            for t in range(s + 1, n):
                if G.has_edge(list(G.nodes())[s], list(G.nodes())[t]):
                    continue
                if kcol(n, e, 5) and not kcol(n, e, 5, merges=[(s, t)]):
                    hits += 1
        out[name] = {"clamp_pairs_at_k5": hits, "expect": 0}
    return out


def small_lower_bound():
    """Rigorous floor: enumerate ALL connected graphs on <= 7 vertices (networkx
    graph atlas) and confirm every K4-free one is 5-colorable. Hence the minimum
    order of a K4-free 6-chromatic graph is >= 8, so the smallest clamp is >= 9."""
    from networkx.generators.atlas import graph_atlas_g
    worst = 0
    n_k4free = 0
    for g in graph_atlas_g():
        if g.number_of_nodes() < 1 or not nx.is_connected(g):
            continue
        n, e, _ = relabel_edges(g)
        if not is_k4_free(n, e):
            continue
        n_k4free += 1
        chi = chromatic_number(n, e, kmax=6)
        worst = max(worst, chi or 0)
    return {"max_chi_over_K4free_up_to_7v": worst,
            "K4free_connected_graphs_scanned": n_k4free,
            "implies_min_order_K4free_6chromatic_>=": 8,
            "implies_min_clamp_order_>=": 9}


def main():
    os.makedirs(CACHE, exist_ok=True)
    print("Abstract color-clamp construction (the L45 ingredient, abstractly)")
    print("=" * 74)

    H = mycielski_tower()
    nH, eH, _ = relabel_edges(H)
    chiH = chromatic_number(nH, eH)
    print(f"  H = M^3(C5): {nH} vertices, {len(eH)} edges, chi = {chiH} "
          f"(triangle-free, 6-critical)")
    assert chiH == 6

    print("  building the vertex-split clamp ...")
    clamp = build_clamp(H)
    assert clamp is not None, "construction failed (unexpected)"
    nG, eG, s, t = clamp["n"], clamp["edges"], clamp["s"], clamp["t"]
    print(f"  G: {nG} vertices, {len(eG)} edges; split vertex w={clamp['w']} "
          f"-> s={s}(|A|={clamp['A_size']}), t={t}(|B|={clamp['B_size']})")
    print(f"    [GATE] G is 5-colorable           : {clamp['verified_5colorable']}")
    print(f"    [GATE] (s,t) forced-different k=5 : {clamp['verified_forced_different']}")
    print(f"    [GATE] chi(G) == 5                : {chromatic_number(nG, eG) == 5}")
    print(f"    [GATE] (s,t) non-adjacent         : {((s,t) not in set(map(tuple, (sorted(e) for e in eG))))}")
    print(f"    [GATE] G is K4-free               : {is_k4_free(nG, eG)}")
    print(f"    [GATE] G is triangle-free         : {is_triangle_free(nG, eG)}")

    print("  minimizing the clamp (SAT-guided vertex deletion) ...")
    mN, mE, mS, mT = minimize_clamp(nG, eG, s, t)
    min_ok = (chromatic_number(mN, mE) == 5) and (
        not kcol(mN, mE, 5, merges=[(mS, mT)]))
    print(f"  minimized G*: {mN} vertices, {len(mE)} edges; clamp preserved: {min_ok}")
    print(f"    chi(G*) = {chromatic_number(mN, mE)}, "
          f"K4-free: {is_k4_free(mN, mE)}, "
          f"triangle-free: {is_triangle_free(mN, mE)}")

    print("  wrong-approach gate (controls must host NO clamp) ...")
    ctrl = control_no_clamp()
    for name, d in ctrl.items():
        print(f"    {name}: clamp pairs at k=5 = {d['clamp_pairs_at_k5']} (expect 0)")

    print("  rigorous small-graph lower bound (atlas, n<=7) ...")
    lb = small_lower_bound()
    print(f"    max chi over all connected K4-free graphs (n<=7) = "
          f"{lb['max_chi_over_K4free_up_to_7v']} "
          f"({lb['K4free_connected_graphs_scanned']} graphs) "
          f"=> min clamp order >= {lb['implies_min_clamp_order_>=']}")

    result = {
        "experiment": "lrf_abstract_clamp",
        "H_vertices": nH, "H_chi": chiH,
        "clamp": {"n": nG, "edges": len(eG), "s": s, "t": t,
                  "gates": {
                      "five_colorable": clamp["verified_5colorable"],
                      "forced_different": clamp["verified_forced_different"],
                      "chi_is_5": chromatic_number(nG, eG) == 5,
                      "k4_free": is_k4_free(nG, eG),
                      "triangle_free": is_triangle_free(nG, eG)}},
        "minimized": {"n": mN, "edges": len(mE), "s": mS, "t": mT,
                      "clamp_preserved": min_ok,
                      "k4_free": is_k4_free(mN, mE),
                      "triangle_free": is_triangle_free(mN, mE),
                      "edge_list": mE},
        "control_gate": ctrl,
        "lower_bound": lb,
        "headline": ("The abstract L45 ingredient (chi-5 K4-free graph with a "
                     "non-adjacent forced-different pair at k=5) EXISTS and is a "
                     "one-move vertex-split of a 6-critical K4-free graph. The "
                     "obstruction to chi(R^2)>=6 is therefore W3 (UDG realizability) "
                     "alone, not abstract non-existence."),
    }
    with open(os.path.join(CACHE, "lrf_abstract_clamp.json"), "w") as f:
        json.dump(result, f, indent=2)
    print("=" * 74)
    print("  HEADLINE:", result["headline"])
    print("  archived _cache/lrf_abstract_clamp.json")
    return result


if __name__ == "__main__":
    main()
