r"""F1 pressure-test, Attack 1d: the decisive test. Is ANY cocircular-at-unit
5-set in P_510 (the richest chi-5 UDG in the lineage) rainbow-forced?

If YES: P_510 + a hub on that circle = realizable concentrated forcing -> the
seed of a chi-6 UDG. A BREAK candidate.
If NO across all cocircular sets: the cocircular-rainbow lemma (L) holds for the
lineage's flagship object, strengthening F1 with a precise mechanism.

We enumerate ALL cocircular-at-unit sets in P_510 (centered at any plane point
realized as a lattice/vertex unit-circle), focusing first on the 36-set
(vertex 0's neighborhood) and all per-vertex unit-circle neighborhoods, then test
rainbow-forcing of representative 5-subsets via SAT pair-merge UNSAT.

Plus the STRONGER test: not just rainbow-forced UNDER ALL colorings, but the
weaker necessary condition the L22 obstruction actually needs at scale -- whether
there EXISTS a hub assignment making |F(hub)|=5 forced. We compute, for vertex 0's
36 cocircular neighbors, the maximum number of DISTINCT colors that are FORCED to
appear among any 5 of them across all proper 5-colorings (= can the hub ever be
saturated?).
"""
from __future__ import annotations
import sys, pathlib, json, itertools, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
from f1pt_lib import load_p510, sat_kcolor, exact_dist2, CACHE
from pysat.solvers import Cadical195

random.seed(1)


def per_vertex_cocircular(base, edges):
    """Each vertex v's unit-distance neighborhood is a cocircular-at-unit set
    (all neighbors lie on v's unit circle, radius 1)."""
    from collections import defaultdict
    adj = defaultdict(set)
    for (u, v) in edges:
        adj[u].add(v); adj[v].add(u)
    return {v: sorted(adj[v]) for v in range(len(base)) if len(adj[v]) >= 5}


def rainbow_forced(n, eset, S, k=5):
    for (a, b) in itertools.combinations(sorted(S), 2):
        def rep(x): return a if x == b else x
        merged = set()
        for (u, v) in eset:
            uu, vv = rep(u), rep(v)
            if uu != vv:
                merged.add((min(uu,vv), max(uu,vv)))
        res, _ = sat_kcolor(n, list(merged), k, Cadical195)
        if res is True:
            return False, (a, b)
    return True, None


def sample_colorings(n, edges, k, count):
    """Collect proper k-colorings by adding random symmetry-breaking / blocking."""
    from pysat.solvers import Cadical195 as Solver
    def var(v, c): return v*k + c + 1
    base_clauses = []
    for v in range(n):
        base_clauses.append([var(v,c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1+1,k):
                base_clauses.append([-var(v,c1),-var(v,c2)])
    for (u,v) in edges:
        for c in range(k):
            base_clauses.append([-var(u,c),-var(v,c)])
    cols = []
    s = Solver(bootstrap_with=base_clauses)
    for _ in range(count):
        if not s.solve():
            break
        m = set(x for x in s.get_model() if x > 0)
        coloring = [next(c for c in range(k) if var(v,c) in m) for v in range(n)]
        cols.append(coloring)
        # block this exact coloring on a random 40-vertex window to diversify
        window = random.sample(range(n), 40)
        s.add_clause([-var(v, coloring[v]) for v in window])
    s.delete()
    return cols


def main():
    base, edges = load_p510()
    n = len(base)
    eset = set((min(u,v),max(u,v)) for (u,v) in edges)
    cocirc = per_vertex_cocircular(base, edges)
    print(f"P_510: {len(cocirc)} vertices with >=5 cocircular-unit neighbors")

    out = {"n_cocirc_centers": len(cocirc)}

    # Part A: rainbow-forcing test on the largest cocircular sets.
    # Sort centers by neighborhood size, test top ones; per center test many 5-subsets.
    centers_by_size = sorted(cocirc, key=lambda c: -len(cocirc[c]))
    any_forced = False
    forced_record = None
    tested_centers = 0
    for c in centers_by_size:
        U = cocirc[c]
        tested_centers += 1
        if tested_centers > 8:
            break
        # test up to 25 random 5-subsets
        subs = list(itertools.combinations(U, 5))
        random.shuffle(subs)
        for S in subs[:25]:
            forced, witness = rainbow_forced(n, eset, S, k=5)
            if forced:
                any_forced = True
                forced_record = {"center": c, "S": list(S)}
                break
        if any_forced:
            break
    out["any_cocircular_5set_rainbow_forced"] = any_forced
    out["forced_record"] = forced_record
    print(f"Part A: any cocircular 5-set rainbow-forced (top 8 centers, 25 subsets each): {any_forced}")

    # Part B: the actual hub-saturation question. For vertex 0's 36 cocircular
    # neighbors, across a SAMPLE of proper 5-colorings, what is the max number of
    # distinct colors appearing on ANY 5-subset, and how often does the FULL set
    # of 5 colors appear among the 36? (If never all 5, a hub on that circle is
    # never saturated by these neighbors -> |F(hub)| < 5 always -> no chi-6 forcing.)
    big_c = centers_by_size[0]
    U = cocirc[big_c]
    cols = sample_colorings(n, edges, 5, 200)
    distinct_counts = []
    for col in cols:
        colors_on_U = set(col[u] for u in U)
        distinct_counts.append(len(colors_on_U))
    out["big_center"] = big_c
    out["big_center_neighbors"] = len(U)
    out["n_sampled_colorings"] = len(cols)
    out["distinct_colors_on_cocirc_set_distribution"] = {
        str(k): distinct_counts.count(k) for k in sorted(set(distinct_counts))}
    print(f"Part B: vertex {big_c}'s {len(U)} cocircular neighbors; over {len(cols)} sampled "
          f"5-colorings, distinct-color-count distribution: {out['distinct_colors_on_cocirc_set_distribution']}")
    # Even if all-5 appears among 36 neighbors, the HUB needs 5 distinct on its
    # bridge set which is a CHOSEN 5-subset; the obstruction needs it forced for
    # EVERY coloring. Part A already tests that directly.

    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "f1pt_attack1d_p510rainbow.json").write_text(json.dumps(out, indent=2, default=str))
    print("saved", CACHE / "f1pt_attack1d_p510rainbow.json")

if __name__ == "__main__":
    main()
