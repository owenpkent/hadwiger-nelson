r"""E12 (L61 route 2): born-realized joint-pattern alternator sweep on the lineage.

L57 tested SINGLE pairs (G+e and G/e never 5-UNSAT: no local forcing). The
equality-alternator is a PAIR-OF-PAIRS property L57 never tested. A born-realized
alternator in a chi-5 UDG G is two disjoint non-adjacent pairs (e1,e2) with:
  - diff-diff forbidden : G + e1 + e2 is 5-UNSAT   (the first TWO-edge forcing)
  - same-same forbidden : merge(e1) & merge(e2) is 5-UNSAT
  - non-degenerate      : only-e1-same SAT and only-e2-same SAT
Found inside a realizable UDG => NO W3 step. Even a diff-diff hit alone is the
first nonlocal forcing in the lineage, overturning "all forcing is local".

Tractable design: brute pairs-of-pairs on 510 vtx is too slow, so SAMPLE many
diverse proper 5-colorings (random vertex-fix assumptions), then a pair-of-pairs
is a diff-diff CANDIDATE only if NO sampled coloring has both pairs bichromatic.
Survivors (rare) are SAT-confirmed. The high-degree core is swept (forcing
concentrates among hubs, per L42/L45).
"""
from __future__ import annotations
import sys, pathlib, json, itertools, time, random
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import parse_vtx, parse_edges, sat_kcolor, CACHE, VTX, EDGE
from pysat.solvers import Cadical195

OUT = CACHE / "e12_born_alternator"
OUT.mkdir(parents=True, exist_ok=True)
GRAPHS = ["510", "517", "529", "553", "610", "633", "803", "826", "874"]
CORE = 60          # sweep pairs among the top-CORE highest-degree vertices
N_SAMPLES = 500    # diverse 5-colorings for the cheap filter
BUD = 2_000_000


def build_cnf(n, edges, k=5):
    var = lambda v, c: v * k + c + 1
    cl = []
    for v in range(n):
        cl.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cl.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            cl.append([-var(u, c), -var(v, c)])
    return cl, var


def sample_colorings(n, edges, n_samples, k=5, fix_frac=18):
    """Diverse proper k-colorings via random per-vertex color assumptions."""
    cl, var = build_cnf(n, edges, k)
    rng = random.Random(12345)
    cols = []
    s = Cadical195(bootstrap_with=cl)
    try:
        for _ in range(n_samples):
            fixed = rng.sample(range(n), max(1, n // fix_frac))
            assumptions = [var(v, rng.randrange(k)) for v in fixed]
            if s.solve(assumptions=assumptions):
                m = set(x for x in s.get_model() if x > 0)
            elif s.solve():  # fall back to any coloring if the random fix was UNSAT
                m = set(x for x in s.get_model() if x > 0)
            else:
                continue
            row = np.empty(n, dtype=np.int8)
            for v in range(n):
                for c in range(k):
                    if var(v, c) in m:
                        row[v] = c
                        break
            cols.append(row)
    finally:
        s.delete()
    return np.array(cols)  # (n_samples, n)


def sweep_graph(GRAPH):
    t0 = time.time()
    base = parse_vtx(VTX / f"{GRAPH}.vtx")
    edges = parse_edges(EDGE / f"{GRAPH}.edge")
    n = len(base)
    eset = set((min(u, v), max(u, v)) for (u, v) in edges)
    adj = [set() for _ in range(n)]
    for (u, v) in eset:
        adj[u].add(v); adj[v].add(u)
    deg = sorted(range(n), key=lambda v: -len(adj[v]))
    core = deg[:CORE]
    print(f"{GRAPH}: n={n}, edges={len(eset)}; core={CORE} (deg "
          f"{len(adj[core[0]])}..{len(adj[core[-1]])})", flush=True)

    C = sample_colorings(n, list(eset), N_SAMPLES)
    print(f"sampled {len(C)} proper 5-colorings ({time.time()-t0:.0f}s)", flush=True)

    # Non-adjacent core pairs and their per-sample "monochromatic" bit vectors.
    pairs = [(a, b) for a, b in itertools.combinations(core, 2) if b not in adj[a]]
    mono = {}   # pair -> bool vector over samples (True = same color)
    for (a, b) in pairs:
        mono[(a, b)] = (C[:, a] == C[:, b])
    # marginal mono rate (diagnostic: L57 predicts ~1/5, deep liquidity)
    rates = {p: float(v.mean()) for p, v in mono.items()}
    rmin, rmax = min(rates.values()), max(rates.values())
    print(f"{len(pairs)} non-adj core pairs; mono-rate in [{rmin:.3f},{rmax:.3f}] "
          f"(L57 liquidity ~0.2)", flush=True)

    # diff-diff candidates: NO sampled coloring has both pairs bichromatic,
    # i.e. (mono[e1] OR mono[e2]) is all True over samples.
    cand = []
    plist = pairs
    for i in range(len(plist)):
        m1 = mono[plist[i]]
        for j in range(i + 1, len(plist)):
            e1, e2 = plist[i], plist[j]
            if len({e1[0], e1[1], e2[0], e2[1]}) < 4:
                continue
            if np.all(m1 | mono[e2]):    # never both bichromatic in the sample
                cand.append((e1, e2))
    print(f"{len(cand)} diff-diff candidates survive the sampling filter "
          f"({time.time()-t0:.0f}s)", flush=True)

    # SAT-confirm survivors.
    def sat_mod(add=(), merge=()):
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        for a, b in merge:
            parent[find(a)] = find(b)
        es = set()
        for u, v in list(eset) + list(add):
            uu, vv = find(u), find(v)
            if uu == vv:
                return False
            es.add((min(uu, vv), max(uu, vv)))
        res, _ = sat_kcolor(n, list(es), 5, Cadical195, budget_conflicts=BUD)
        return res

    hits = []
    for k, (e1, e2) in enumerate(cand):
        diff_diff = sat_mod(add=[e1, e2])             # expect False if real
        if diff_diff is not False:
            continue
        same_same = sat_mod(merge=[e1, e2])
        only_e1 = sat_mod(merge=[e1], add=[e2])
        only_e2 = sat_mod(merge=[e2], add=[e1])
        rec = {"e1": list(e1), "e2": list(e2),
               "diff_diff_UNSAT": diff_diff is False,
               "same_same_UNSAT": same_same is False,
               "only_e1_SAT": only_e1 is True, "only_e2_SAT": only_e2 is True,
               "full_alternator": (same_same is False and only_e1 is True and only_e2 is True)}
        hits.append(rec)
        tag = "FULL ALTERNATOR" if rec["full_alternator"] else "two-edge forcing (diff-diff)"
        print(f"!!! {tag}: e1={e1} e2={e2} same_same_UNSAT={rec['same_same_UNSAT']}", flush=True)

    result = {"experiment": "e12_born_alternator", "graph": GRAPH, "n": n,
              "core": CORE, "samples": len(C), "candidates": len(cand),
              "confirmed_diff_diff": len(hits),
              "full_alternators": sum(h["full_alternator"] for h in hits),
              "hits": hits[:100], "secs": round(time.time()-t0, 1)}
    (OUT / f"{GRAPH}.json").write_text(json.dumps(result, indent=2))
    print(f"  {GRAPH} DONE: candidates={len(cand)} diff_diff={len(hits)} "
          f"full={result['full_alternators']} ({result['secs']}s)", flush=True)
    return result


def main():
    summary = {}
    for g in GRAPHS:
        r = sweep_graph(g)
        summary[g] = {k: r[k] for k in ("n", "core", "samples", "candidates",
                                        "confirmed_diff_diff", "full_alternators")}
        (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2))
    tot_c = sum(s["candidates"] for s in summary.values())
    tot_h = sum(s["confirmed_diff_diff"] for s in summary.values())
    print(f"\nLINEAGE SUMMARY: {len(GRAPHS)} graphs, {tot_c} sampling candidates, "
          f"{tot_h} confirmed diff-diff, "
          f"{sum(s['full_alternators'] for s in summary.values())} full alternators", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
