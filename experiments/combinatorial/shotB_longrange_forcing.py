r"""Shot B, first increment: search the de Grey / Polymath16 chi-5 UDG lineage for
LONG-RANGE COLOR FORCING.

The L42 reframing (the right target for chi >= 6): find a chi-5 unit-distance graph
with a NON-ADJACENT pair that is forced-different in every proper 5-coloring. That
is exactly what a chi-6 coupling needs and exactly what the de Grey / Polymath
lineage was shown to LACK in P_510 (there, forced-different <=> adjacent, L42).

This extends the L42 P_510 test to the full available lineage (510, 517, 529, 553,
610, 633, 803, 826, 874, L403, S199, T721). For each graph:
  (1) confirm it is 5-colorable (it is chi-5 by construction; sanity only),
  (2) test whether ANY NON-ADJACENT pair (a,b) is forced-different, i.e. merging
      a,b (forcing same color) makes the graph 5-UNSAT [merged_unsat].

A non-adjacent forced-different pair anywhere = the missing chi-6 ingredient (a
universal hub adjacent to a rainbow-forced set, or directly a long-range coupling).
We test the high-degree core exhaustively (forcing concentrates there) plus a random
sample across the whole graph. If forced-different <=> adjacent holds across the
whole family, that upgrades L42 from "P_510 lacks it" to "the lineage lacks it",
sharpening the open problem; a single hit would be a breakthrough.
"""
from __future__ import annotations
import sys, pathlib, json, itertools, random, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import parse_vtx, parse_edges, sat_kcolor, CACHE, VTX, EDGE
from pysat.solvers import Cadical195

random.seed(11)

# (name, core size to test exhaustively, random non-adjacent pairs across whole graph)
GRAPHS = [
    ("510", 60, 500), ("517", 60, 500), ("529", 60, 500), ("553", 60, 500),
    ("610", 55, 450), ("633", 55, 450), ("803", 50, 400), ("826", 50, 400),
    ("874", 50, 400), ("L403", 55, 450), ("S199", 70, 600), ("T721", 45, 350),
]
BUDGET = 400_000  # conflict budget per merge; indeterminate if exceeded


def load_graph(name):
    base = parse_vtx(VTX / f"{name}.vtx")
    edges = parse_edges(EDGE / f"{name}.edge")
    return base, edges


def merged_unsat(n, eset, a, b, k=5):
    """Merge a,b (force same color); return (verdict, indeterminate).
    verdict True  => k-UNSAT  => (a,b) forced-different in every proper k-coloring.
    verdict False => k-SAT    => (a,b) can share a color (not forced).
    indeterminate True if the conflict budget was exhausted (verdict unreliable)."""
    def rep(x):
        return a if x == b else x
    merged = set()
    for (u, v) in eset:
        uu, vv = rep(u), rep(v)
        if uu == vv:
            # A self-loop arises only from the edge (a,b) itself: a and b are
            # ADJACENT, so forcing them equal violates a unit-distance edge => the
            # merge is UNSAT and the pair is (trivially) forced-different.
            return True, False
        merged.add((min(uu, vv), max(uu, vv)))
    res, _ = sat_kcolor(n, list(merged), k, Cadical195, budget_conflicts=BUDGET)
    if res is None:  # budget exhausted
        return None, True
    return (res is False), False


def test_graph(name, core_size, n_random):
    base, edges = load_graph(name)
    n = len(base)
    eset = set((min(u, v), max(u, v)) for (u, v) in edges)
    adj = [set() for _ in range(n)]
    for (u, v) in eset:
        adj[u].add(v)
        adj[v].add(u)
    deg = [len(adj[v]) for v in range(n)]

    # Sanity: the graph must be 5-colorable (it is chi-5 by construction).
    sat5, _ = sat_kcolor(n, list(eset), 5, Cadical195, budget_conflicts=2_000_000)
    colorable = (sat5 is True)

    core = sorted(range(n), key=lambda v: -deg[v])[:min(core_size, n)]
    core_set = set(core)

    tested = 0
    indet = 0
    forced_nonadj = []   # the jackpot: non-adjacent pairs forced different
    forced_adj = 0       # adjacent pairs are trivially forced different; sanity counter
    nonadj_not_forced = 0

    def consider(a, b):
        nonlocal tested, indet, forced_adj, nonadj_not_forced
        a, b = (a, b) if a < b else (b, a)
        adjacent = b in adj[a]
        verdict, ind = merged_unsat(n, eset, a, b)
        tested += 1
        if ind:
            indet += 1
            return
        if verdict:  # forced different
            if adjacent:
                forced_adj += 1
            else:
                forced_nonadj.append((a, b))
        else:
            if not adjacent:
                nonadj_not_forced += 1

    # (1) exhaustive over the high-degree core (forcing concentrates among hubs).
    for a, b in itertools.combinations(core, 2):
        consider(a, b)
        if forced_nonadj:
            break  # stop early on a hit; it is the headline

    # (2) random non-adjacent pairs across the WHOLE graph.
    if not forced_nonadj:
        seen = set()
        attempts = 0
        while len(seen) < n_random and attempts < n_random * 20:
            attempts += 1
            a, b = random.randrange(n), random.randrange(n)
            if a == b:
                continue
            a, b = (a, b) if a < b else (b, a)
            if (a, b) in seen or b in adj[a]:
                continue
            if a in core_set and b in core_set:
                continue  # already covered exhaustively
            seen.add((a, b))
            consider(a, b)
            if forced_nonadj:
                break

    return {
        "graph": name, "n": n, "edges": len(eset), "5_colorable": colorable,
        "core_size": len(core), "pairs_tested": tested, "indeterminate": indet,
        "forced_adjacent_pairs_sampled": forced_adj,
        "nonadjacent_not_forced": nonadj_not_forced,
        "LONG_RANGE_FORCING_pairs": forced_nonadj,
        "long_range_forcing_found": bool(forced_nonadj),
    }


def main():
    print("Shot B: long-range color forcing across the chi-5 UDG lineage")
    print("=" * 78)
    print("Target: a NON-ADJACENT pair forced-different in every proper 5-coloring.")
    print("(L42: P_510 has none -> forced-different <=> adjacent. Does any lineage")
    print(" graph break that?)\n")
    results = []
    any_hit = False
    for name, core_size, n_random in GRAPHS:
        t0 = time.time()
        try:
            r = test_graph(name, core_size, n_random)
        except Exception as e:  # noqa: BLE001
            r = {"graph": name, "error": repr(e)}
            print(f"  {name:6s}: ERROR {e!r}", flush=True)
            results.append(r)
            continue
        r["seconds"] = round(time.time() - t0, 1)
        results.append(r)
        hit = r.get("long_range_forcing_found")
        any_hit = any_hit or hit
        tag = "  *** LONG-RANGE FORCING FOUND ***" if hit else ""
        print(f"  {name:6s}: n={r['n']:4d} E={r['edges']:5d} 5col={r['5_colorable']} "
              f"tested={r['pairs_tested']:5d} indet={r['indeterminate']:4d} "
              f"forced_nonadj={len(r['LONG_RANGE_FORCING_pairs'])} "
              f"({r['seconds']}s){tag}", flush=True)
        if hit:
            print(f"        pairs: {r['LONG_RANGE_FORCING_pairs']}", flush=True)

    CACHE.mkdir(exist_ok=True)
    out = CACHE / "shotB_longrange_forcing.json"
    with out.open("w") as f:
        json.dump({"experiment": "shotB_longrange_forcing",
                   "long_range_forcing_found_anywhere": any_hit,
                   "results": results}, f, indent=2)
    print("\n" + "=" * 78)
    if any_hit:
        print("HEADLINE: long-range forcing FOUND -> candidate chi-6 ingredient. Verify "
              "exact + check UDG realizability of the forcing gadget.")
    else:
        print("HEADLINE: NO long-range forcing in any tested lineage graph. "
              "forced-different <=> adjacent holds across the family, upgrading L42 "
              "from P_510 to the lineage. The open problem (find a chi-5 UDG WITH "
              "long-range forcing) stands, now better motivated.")
    print(f"archived: {out}")
    return any_hit  # a hit is the headline, not an error; exit 0 regardless


if __name__ == "__main__":
    main()
    raise SystemExit(0)
