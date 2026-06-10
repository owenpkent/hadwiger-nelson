r"""E1b: attack the equality-alternator's W3 (realizability) wall.

L60 established the abstract equality-alternator exists (693 in M^3(C5)). For the
L58 phase-gadget route it must be realized as a UDG with two CONGRUENT non-adjacent
interface pairs L, R = tau(L). Three stages:

  Stage 1 (minimize): greedily delete non-terminal vertices/edges from each
    alternator while preserving the alternator property:
      A) diff-diff forbidden : G + e1 + e2 is 5-UNSAT
      B) same-same forbidden : merge(a1,a2) & merge(b1,b2) is 5-UNSAT
      C) non-degenerate       : only-e1-same SAT and only-e2-same SAT
    Report the size distribution and the global minimum-order alternator.

  Stage 2 (congruence filter): for the smallest distinct minimized alternators,
    compute the automorphism group (networkx VF2) and keep those with an
    involution swapping the two pairs {a1,a2} <-> {b1,b2} (a built-in tau).

  Stage 3 (realization): attempt unit-distance realization (L52 embedder) of the
    smallest candidates; flag any of order <= 14 as an exact-Groebner target.

A small pair-swap-symmetric realizable alternator would be the phase route's
analog of a realizable clamp, but width-2 with NO cocircular rainbow, so it
plausibly evades Theorem R's degree-5 obstruction. A clean "all minimized
alternators are large / non-realizable" outcome bounds the route's cost.
"""
from __future__ import annotations
import sys, pathlib, json, itertools, time
import networkx as nx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import sat_kcolor, CACHE
from pysat.solvers import Cadical195

OUT = CACHE / "e11_alternator_w3"
OUT.mkdir(parents=True, exist_ok=True)
BUD = 2_000_000


def myciel():
    g = nx.cycle_graph(5)
    for _ in range(3):
        g = nx.mycielskian(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    return g.number_of_nodes(), [(idx[u], idx[v]) for u, v in g.edges()]


def _sat(n, edges, k, add=(), merge=()):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in merge:
        parent[find(a)] = find(b)
    es = set()
    for u, v in list(edges) + list(add):
        uu, vv = find(u), find(v)
        if uu == vv:
            return False
        es.add((min(uu, vv), max(uu, vv)))
    res, _ = sat_kcolor(n, list(es), k, Cadical195, budget_conflicts=BUD)
    return res


def alt_ok(n, edges, e1, e2):
    """edges already excludes e1,e2 (the gadget G = K - e1 - e2)."""
    a1, a2 = e1; b1, b2 = e2
    A = _sat(n, edges, 5, add=[e1, e2]) is False              # diff-diff forbidden
    if not A:
        return False
    B = _sat(n, edges, 5, merge=[e1, e2]) is False            # same-same forbidden
    if not B:
        return False
    C1 = _sat(n, edges, 5, merge=[e1], add=[e2]) is True       # only-e1-same
    C2 = _sat(n, edges, 5, merge=[e2], add=[e1]) is True       # only-e2-same
    return C1 and C2


def find_alternators(n, eset):
    pairs = []
    m = len(eset)
    for i in range(m):
        a1, a2 = eset[i]
        for j in range(i + 1, m):
            b1, b2 = eset[j]
            if len({a1, a2, b1, b2}) == 4:
                pairs.append((eset[i], eset[j]))
    hits = []
    for (e1, e2) in pairs:
        base = [e for e in eset if e != tuple(sorted(e1)) and e != tuple(sorted(e2))]
        # base excludes e1,e2; both-same test only:
        if _sat(n, base, 5, merge=[e1, e2]) is False:
            hits.append((e1, e2))
    return hits


def minimize(n, eset, e1, e2):
    """Delete non-terminal vertices preserving alt_ok. Returns (n', edges', e1', e2')."""
    term = set(e1) | set(e2)
    alive = set(range(n))
    cur = [e for e in eset if e != tuple(sorted(e1)) and e != tuple(sorted(e2))]
    changed = True
    while changed:
        changed = False
        for v in sorted(alive):
            if v in term:
                continue
            keep = sorted(alive - {v})
            remap = {old: i for i, old in enumerate(keep)}
            te = [(remap[a], remap[b]) for (a, b) in cur if a in remap and b in remap]
            ne1 = (remap[e1[0]], remap[e1[1]]); ne2 = (remap[e2[0]], remap[e2[1]])
            if alt_ok(len(keep), te, ne1, ne2):
                alive.discard(v); cur = te
                # remap cur back to original labels for next iteration
                inv = {i: old for old, i in remap.items()}
                cur = [(inv[a], inv[b]) for (a, b) in cur]
                changed = True
    keep = sorted(alive)
    remap = {old: i for i, old in enumerate(keep)}
    fe = sorted({(min(remap[a], remap[b]), max(remap[a], remap[b]))
                 for (a, b) in cur if a in remap and b in remap})
    return len(keep), fe, (remap[e1[0]], remap[e1[1]]), (remap[e2[0]], remap[e2[1]])


def pair_swap_autos(n, edges, e1, e2):
    """Count automorphisms phi with phi({a1,a2}) = {b1,b2} (and vice versa)."""
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    P1, P2 = frozenset(e1), frozenset(e2)
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    swaps, total = 0, 0
    for phi in gm.isomorphisms_iter():
        total += 1
        if total > 200000:
            break
        im1 = frozenset({phi[e1[0]], phi[e1[1]]})
        im2 = frozenset({phi[e2[0]], phi[e2[1]]})
        if im1 == P2 and im2 == P1:
            swaps += 1
    return swaps, total


def main():
    t0 = time.time()
    n, edges = myciel()
    eset = [tuple(sorted((u, v))) for u, v in edges]
    print(f"M^3(C5): n={n}, edges={len(eset)}", flush=True)

    print("stage 1: finding alternators ...", flush=True)
    alts = find_alternators(n, eset)
    print(f"  {len(alts)} alternators ({time.time()-t0:.0f}s)", flush=True)

    print("stage 1: minimizing ...", flush=True)
    minimized = []
    seen = {}
    for k, (e1, e2) in enumerate(alts):
        mn, me, me1, me2 = minimize(n, eset, e1, e2)
        key = (mn, tuple(me))
        if key not in seen:
            seen[key] = {"n": mn, "edges": me, "e1": list(me1), "e2": list(me2)}
        minimized.append(mn)
        if k % 50 == 0:
            sizes = sorted(set(minimized))
            print(f"  {k}/{len(alts)} min-so-far={min(minimized)} "
                  f"distinct={len(seen)} ({time.time()-t0:.0f}s)", flush=True)
            (OUT / "progress.json").write_text(json.dumps(
                {"done": k, "total": len(alts), "min": min(minimized),
                 "distinct": len(seen), "size_hist": {str(s): minimized.count(s) for s in sizes}}))
    minsize = min(minimized)
    distinct = sorted(seen.values(), key=lambda d: (d["n"], len(d["edges"])))
    print(f"stage 1 DONE: min order={minsize}, {len(distinct)} distinct minimized "
          f"({time.time()-t0:.0f}s)", flush=True)
    hist = {str(s): minimized.count(s) for s in sorted(set(minimized))}
    print(f"  size histogram: {hist}", flush=True)

    print("stage 2: pair-swap automorphisms on smallest distinct ...", flush=True)
    smallest = [d for d in distinct if d["n"] <= minsize + 2][:12]
    for d in smallest:
        sw, tot = pair_swap_autos(d["n"], d["edges"], tuple(d["e1"]), tuple(d["e2"]))
        d["pair_swap_autos"] = sw
        d["aut_total_seen"] = tot
        print(f"  n={d['n']} m={len(d['edges'])} pair-swap-autos={sw} (of {tot})", flush=True)

    result = {"experiment": "e11_alternator_w3", "host": "M^3(C5)",
              "n_alternators": len(alts), "min_order": minsize,
              "size_histogram": hist, "n_distinct_minimized": len(distinct),
              "smallest": smallest, "secs": round(time.time()-t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    # persist the full distinct set for a possible stage-3 realization pass
    (OUT / "distinct_minimized.json").write_text(json.dumps(distinct))
    print("DONE", json.dumps({k: v for k, v in result.items()
                              if k not in ("smallest",)}, indent=2), flush=True)
    print("smallest candidates:", json.dumps(smallest, indent=2), flush=True)


if __name__ == "__main__":
    main()
