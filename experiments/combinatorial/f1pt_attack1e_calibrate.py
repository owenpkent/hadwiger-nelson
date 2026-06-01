r"""F1 pressure-test, Attack 1e: calibrate the rainbow-forcing question and run the
sharpest non-rigid break attempt.

Two questions:
 (Q1) Does P_510 contain ANY rainbow-forced 5-set at all (cocircular or not)? If
      even the unconstrained version is rare/absent, cocircularity is not the only
      barrier. If unconstrained rainbow-forced 5-sets exist but no COCIRCULAR one,
      cocircularity is precisely the obstruction.
 (Q2) The single-hub chi-6 gadget: hub v + 5 sources that are (a) cocircular at unit
      radius (so realizable into v) AND (b) rainbow-forced. We attempt to BUILD this
      with v adjacent to all 5 sources (the realized bridges) plus the 5 sources
      forced rainbow by an attached chi-5 generator. The local chi must be >=6.

For (Q1) we search: a 5-set S is rainbow-forced iff for every pair in S, merging
them keeps the graph 5-UNSAT. We test high-degree / mutually-distant 5-sets and the
known critical structure.

For the sharpest break: a hub v adjacent to 5 rainbow-forced vertices has chi(local)
>= 6 ONLY IF those 5 are FORCED to 5 distinct colors AND v adjacent to all. But if
the 5 are rainbow-forced in the GENERATOR (without v), then adding v adjacent to all
5 makes v need a 6th color: chi >= 6. So a single rainbow-forced 5-set + a universal
hub IS a chi-6 graph. The ONLY missing ingredient for realizability is that the 5
rainbow-forced sources be COCIRCULAR AT UNIT RADIUS (so the hub realizes). That is
EXACTLY lemma (L). We test it head-on.
"""
from __future__ import annotations
import sys, pathlib, json, itertools, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import load_p510, sat_kcolor, CACHE
from pysat.solvers import Cadical195

random.seed(7)


def merged_unsat(n, eset, a, b, k=5):
    """Merge a,b (force same color); return True if resulting graph is k-UNSAT."""
    def rep(x): return a if x == b else x
    merged = set()
    for (u, v) in eset:
        uu, vv = rep(u), rep(v)
        if uu != vv:
            merged.add((min(uu,vv), max(uu,vv)))
    res, _ = sat_kcolor(n, list(merged), k, Cadical195)
    return res is False


def is_rainbow_forced(n, eset, S, k=5):
    for (a, b) in itertools.combinations(sorted(S), 2):
        if not merged_unsat(n, eset, a, b, k):
            return False
    return True


def main():
    base, edges = load_p510()
    n = len(base)
    eset = set((min(u,v),max(u,v)) for (u,v) in edges)
    from collections import defaultdict
    adj = defaultdict(set)
    for (u,v) in eset:
        adj[u].add(v); adj[v].add(u)

    out = {}

    # Q1: find ANY rainbow-forced 5-set. Strategy: rainbow-forcing of a pair requires
    # merging them to be UNSAT. First find all "rigid pairs" (a,b) whose merge is UNSAT
    # (these are pairs forced to differ in every 5-coloring). A rainbow-forced 5-set is a
    # 5-clique in the "forced-different" graph D. Build D over a sampled vertex subset.
    # (Full D is 510x510/2 ~ 130k merges; sample to keep tractable but representative.)
    verts = list(range(n))
    # Use a moderate subset: top-degree vertices and their neighborhoods (most constrained)
    cand = sorted(verts, key=lambda v: -len(adj[v]))[:40]
    print(f"Building forced-different graph D on {len(cand)} high-degree vertices...")
    D = defaultdict(set)
    pairs = list(itertools.combinations(cand, 2))
    for idx, (a, b) in enumerate(pairs):
        if (min(a,b),max(a,b)) in eset:
            D[a].add(b); D[b].add(a)  # adjacent => trivially forced different
            continue
        if merged_unsat(n, eset, a, b, 5):
            D[a].add(b); D[b].add(a)
    total_forced = sum(len(s) for s in D.values())//2
    print(f"forced-different pairs among {len(cand)} verts: {total_forced} of {len(pairs)}")
    out["forced_diff_subset_size"] = len(cand)
    out["forced_diff_pairs"] = total_forced
    out["forced_diff_total_pairs"] = len(pairs)

    # A rainbow-forced 5-set = 5-clique in D. Search for one.
    def find_clique5():
        cverts = list(D.keys())
        for combo in itertools.combinations(cverts, 5):
            ok = all((y in D[x]) for x, y in itertools.combinations(combo, 2))
            if ok:
                return combo
        return None
    clique = find_clique5()
    out["rainbow_forced_5set_exists_in_subset"] = clique is not None
    out["rainbow_forced_5set"] = list(clique) if clique else None
    print(f"Q1: rainbow-forced 5-set (5-clique in D) in high-degree subset: {clique}")

    if clique:
        # verify and check cocircularity: are these 5 cocircular at unit radius?
        # A 5-set is cocircular at unit radius iff there is a common point at dist 1 from
        # all 5, i.e. a common unit-distance vertex OR plane point. Check if they share a
        # common P_510 neighbor (a vertex adjacent to all 5 = a realizable hub already in graph!)
        common_nbr = set.intersection(*[adj[v] for v in clique])
        out["rainbow5_common_p510_neighbor"] = sorted(common_nbr)
        print(f"   common P_510 neighbor of the rainbow-forced 5-set: {sorted(common_nbr)}")
        if common_nbr:
            print("   !!! A common neighbor h would be a REALIZED hub adjacent to a rainbow-")
            print("       forced 5-set => chi(local) >= 6 => potential BREAK. Verify chi.")
            h = min(common_nbr)
            sub = set(clique) | {h}
            # local subgraph chi
            subverts = sorted(sub)
            remap = {v:i for i,v in enumerate(subverts)}
            subE = [(remap[u],remap[v]) for (u,v) in eset if u in sub and v in sub]
            for k in range(3,7):
                r,_ = sat_kcolor(len(subverts), subE, k, Cadical195)
                print(f"     local chi <= {k}: {'yes' if r else 'NO'}")
                if r:
                    out["hub_plus_rainbow5_local_chi"] = k
                    break

    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "f1pt_attack1e_calibrate.json").write_text(json.dumps(out, indent=2, default=str))
    print("saved", CACHE / "f1pt_attack1e_calibrate.json")

if __name__ == "__main__":
    main()
