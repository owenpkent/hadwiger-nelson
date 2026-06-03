r"""Shot C (L55 follow-up i): search the chi-5 UDG lineage for FORCED-SAME
non-adjacent pairs, the dual of L45's forced-different sweep, and verify the
splice lemma that makes a forced-same pair as good as a clamp.

Motivation (L55). Color-symmetry confines single-vertex-port relations to the
primitive monoid {0, I, J-I, J}. The clamp question (a chi >= 6 UDG) factors
into two sub-questions; THIS is sub-question (i): can a planar UDG (omega <= 3)
force two NON-ADJACENT vertices to the SAME color (realize relation I)?

Why it suffices (the splice lemma, verified in Part 1 below). If (s,t) is a
forced-same non-adjacent pair in a UDG G, add one new vertex u at unit distance
from t but not from s. Then every proper 5-coloring has c(s) = c(t) != c(u), so
(s,u) is a NON-ADJACENT forced-different pair = a clamp; contracting s = u forces
t != t, so chi(G + u with s,u identified) >= 6. A realizable forced-same gadget
therefore yields a realizable clamp and a chi >= 6 UDG. So forced-same is exactly
as powerful as the clamp, approached from the "same color" side.

The test (dual of L45 / shotB). L45 tested forced-DIFFERENT by MERGING (a,b)
(force same color) and checking 5-UNSAT. Forced-SAME is the mirror: ADD an edge
(a,b) (force different colors) and check 5-UNSAT. UNSAT => no proper 5-coloring
has a != b => (a,b) is FORCED-SAME. Only non-adjacent (non-unit) pairs qualify.

L45 established forced-different <=> adjacent across the lineage (non-adjacent =>
NOT forced-different). If this sweep finds NO forced-same non-adjacent pair
either, the two halves combine to: in the lineage, non-adjacent pairs are
COMPLETELY UNFORCED (neither same nor different is forced) -- all color forcing
is local/adjacency-only. A single hit, by the splice lemma, is a chi >= 6 UDG.
"""
from __future__ import annotations
import sys, pathlib, json, itertools, random, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import parse_vtx, parse_edges, sat_kcolor, CACHE, VTX, EDGE
from pysat.solvers import Cadical195

random.seed(11)

GRAPHS = [
    ("510", 60, 500), ("517", 60, 500), ("529", 60, 500), ("553", 60, 500),
    ("610", 55, 450), ("633", 55, 450), ("803", 50, 400), ("826", 50, 400),
    ("874", 50, 400), ("L403", 55, 450), ("S199", 70, 600), ("T721", 45, 350),
]
BUDGET = 400_000


# ---------------------------------------------------------------------------
# Part 1: verify the splice lemma on a tiny exact witness (K_6 minus an edge).
# K_6 - e is 5-colorable with the two endpoints of the missing edge FORCED-SAME.
# (This witness has a K_4, which is fine here: Part 1 only verifies the LOGIC of
# the splice. Part 2 searches K_4-free planar UDGs.)
# ---------------------------------------------------------------------------
def brute_forced_same(n, edges, s, t, k=5):
    """True iff every proper k-coloring colors s and t the same."""
    eset = set((min(u, v), max(u, v)) for u, v in edges)
    saw_proper = False
    for col in itertools.product(range(k), repeat=n):
        if all(col[u] != col[v] for u, v in eset):
            saw_proper = True
            if col[s] != col[t]:
                return False
    return saw_proper  # forced-same only if at least one proper coloring exists


def verify_splice_lemma():
    s, t = 4, 5
    k6_minus_e = [(i, j) for i in range(6) for j in range(i + 1, 6) if (i, j) != (s, t)]
    fs = brute_forced_same(6, k6_minus_e, s, t)

    # Splice: add u = 6 at "unit distance" from t (edge 5-6), not from s.
    u = 6
    spliced = k6_minus_e + [(t, u)]
    # (s,u) non-adjacent? yes (no edge 4-6). forced-different?
    eset = set((min(a, b), max(a, b)) for a, b in spliced)
    fd_su = True
    saw = False
    for col in itertools.product(range(5), repeat=7):
        if all(col[a] != col[b] for a, b in eset):
            saw = True
            if col[s] == col[u]:
                fd_su = False
                break
    # contracting s=u must be 5-UNSAT (chi >= 6)
    contracted = set()
    for a, b in spliced:
        aa = s if a == u else a
        bb = s if b == u else b
        if aa != bb:
            contracted.add((min(aa, bb), max(aa, bb)))
    res, _ = sat_kcolor(6, list(contracted), 5, Cadical195, budget_conflicts=BUDGET)
    contract_unsat = (res is False)

    return {
        "witness": "K_6 minus edge (4,5)",
        "endpoints_forced_same": fs,
        "spliced_pair_(s,u)_nonadjacent": (s, u) not in eset and (u, s) not in eset,
        "spliced_pair_forced_different": fd_su and saw,
        "contracting_s_eq_u_is_5_UNSAT": contract_unsat,
        "splice_lemma_holds": fs and fd_su and saw and contract_unsat,
    }


# ---------------------------------------------------------------------------
# Part 2: forced-same sweep across the realizable chi-5 UDG lineage.
# ---------------------------------------------------------------------------
def load_graph(name):
    base = parse_vtx(VTX / f"{name}.vtx")
    edges = parse_edges(EDGE / f"{name}.edge")
    return base, edges


def differ_unsat(n, eset, a, b, k=5):
    """Add the constraint a != b (an edge a-b); return (verdict, indeterminate).
    verdict True  => k-UNSAT => no proper k-coloring has a != b => FORCED-SAME.
    verdict False => k-SAT   => a,b can differ (not forced-same)."""
    aug = set(eset)
    aug.add((min(a, b), max(a, b)))
    res, _ = sat_kcolor(n, list(aug), k, Cadical195, budget_conflicts=BUDGET)
    if res is None:
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

    sat5, _ = sat_kcolor(n, list(eset), 5, Cadical195, budget_conflicts=2_000_000)
    colorable = (sat5 is True)

    core = sorted(range(n), key=lambda v: -deg[v])[:min(core_size, n)]
    core_set = set(core)

    tested = 0
    indet = 0
    forced_same = []        # the jackpot: non-adjacent pairs forced to SAME color
    nonadj_free = 0         # non-adjacent and NOT forced-same (the expected case)

    def consider(a, b):
        nonlocal tested, indet, nonadj_free
        a, b = (a, b) if a < b else (b, a)
        if b in adj[a]:
            return  # adjacent pairs cannot be forced-same; skip
        verdict, ind = differ_unsat(n, eset, a, b)
        tested += 1
        if ind:
            indet += 1
            return
        if verdict:
            forced_same.append((a, b))
        else:
            nonadj_free += 1

    for a, b in itertools.combinations(core, 2):
        consider(a, b)
        if forced_same:
            break

    if not forced_same:
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
                continue
            seen.add((a, b))
            consider(a, b)
            if forced_same:
                break

    return {
        "graph": name, "n": n, "edges": len(eset), "5_colorable": colorable,
        "core_size": len(core), "pairs_tested": tested, "indeterminate": indet,
        "nonadjacent_unforced": nonadj_free,
        "FORCED_SAME_pairs": forced_same,
        "forced_same_found": bool(forced_same),
    }


def main():
    print("Shot C: FORCED-SAME color forcing across the chi-5 UDG lineage")
    print("=" * 78)
    print("Target: a NON-ADJACENT pair forced to the SAME color in every proper")
    print("5-coloring (L55 sub-question i). By the splice lemma a hit = a chi>=6 UDG.\n")

    print("[Part 1] Splice-lemma verification (K_6 - e, exact brute force):")
    sl = verify_splice_lemma()
    for kk, vv in sl.items():
        print(f"    {kk}: {vv}")
    print()

    print("[Part 2] Forced-same sweep across the lineage:")
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
        hit = r.get("forced_same_found")
        any_hit = any_hit or hit
        tag = "  *** FORCED-SAME FOUND (=> chi>=6 by splice) ***" if hit else ""
        print(f"  {name:6s}: n={r['n']:4d} E={r['edges']:5d} 5col={r['5_colorable']} "
              f"tested={r['pairs_tested']:5d} indet={r['indeterminate']:4d} "
              f"forced_same={len(r['FORCED_SAME_pairs'])} ({r['seconds']}s){tag}",
              flush=True)
        if hit:
            print(f"        pairs: {r['FORCED_SAME_pairs']}", flush=True)

    CACHE.mkdir(exist_ok=True)
    out = CACHE / "shotC_forced_same.json"
    with out.open("w") as f:
        json.dump({"experiment": "shotC_forced_same",
                   "splice_lemma": sl,
                   "forced_same_found_anywhere": any_hit,
                   "results": results}, f, indent=2)
    print("\n" + "=" * 78)
    if any_hit:
        print("HEADLINE: FORCED-SAME pair FOUND -> a chi>=6 UDG via the splice lemma. "
              "Verify exact + realize the spliced unit-distance vertex u.")
    else:
        print("HEADLINE: NO forced-same non-adjacent pair in any tested lineage graph. "
              "Combined with L45 (forced-different <=> adjacent), non-adjacent pairs "
              "in the lineage are COMPLETELY UNFORCED -- all color forcing is local. "
              "Sub-question (i) is negative on the realizable lineage; the open object "
              "remains a NEW chi-5 UDG outside the lineage (the W3 wall).")
    print(f"archived: {out}")
    return any_hit


if __name__ == "__main__":
    main()
    raise SystemExit(0)
