r"""E13b: edge-minimize E13 hosts toward the UDG-necessary class
(K4-free AND K_{2,3}-free), then re-census alternators.

E13 minimized VERTICES and paid in edge density: the 18-vtx host has m=79,
avg degree 8.8. But a planar UDG has codegree <= 2 everywhere (two unit
circles meet in <= 2 points), i.e. it is K_{2,3}-free, which forces
m <= n(1+sqrt(8n-7))/4 (sub-3n at this scale). Kostochka-Yancey forces any
6-critical host UP to m >= 2.8n - 1.8. So the UDG-plausible window is
edge-critical hosts squeezed between the two bounds, and K_{2,3}-freeness is
the sharp structural test E13 never ran.

Stages:
  1  edge-minimize each E13 finalist to an edge-critical core (delete edges
     while 5-UNSAT survives; prefer deleting edges involved in codegree-3+
     violations, so the descent steers toward K_{2,3}-freeness).
  2  report the squeeze: n, m vs KY floor 2.8n-1.8 vs K_{2,3} ceiling;
     exact codegree histogram; K4 / K_{2,3} flags; triangle profile.
  3  fresh codegree-aware shrink runs from the E13 seeds (blocking edges must
     be K4-safe AND codegree-safe when possible), edge-minimized the same way.
  4  alternator census on every edge-critical core (edge-criticality makes
     non-degeneracy automatic, but it is still checked exactly), plus
     pair-swap involution count on a sample (the L61 congruence advantage).

Decision content: does ANY 6-chromatic K4-free host fit inside the
K_{2,3}-free window at this scale? If yes, those hosts are the first
UDG-plausible alternator carriers. If no, the codegree obstruction is a new
quantitative wall for the phase route at small n.
"""
from __future__ import annotations
import sys, pathlib, json, time, random, itertools
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from e13_small_hosts import (norm, adj_from, cycle, apex, mycielski,
                             delete_vertex, merge_vertices, k4_free,
                             safe_to_add, triangle_stats, degree_stats, five,
                             critical_core, alternator_census, build_seeds)
from f1pt_lib import CACHE

OUT = CACHE / "e13b_edge_minimal"
OUT.mkdir(parents=True, exist_ok=True)
HOSTS_IN = pathlib.Path(__file__).resolve().parent / "e13_hosts.json"
HOSTS_OUT = pathlib.Path(__file__).resolve().parent / "e13b_hosts.json"

SEED = 20260611
FRESH_SHRINK_SECONDS = 150.0
CENSUS_SECONDS = 45.0
MAX_BLOCK_EDGES = 130


# ---------- codegree / K_{2,3} machinery ----------

def codegree_violations(n, edges):
    """Pairs with >= 3 common neighbors (impossible in a planar UDG)."""
    adj = adj_from(n, edges)
    bad = []
    for u, v in itertools.combinations(range(n), 2):
        c = len(adj[u] & adj[v])
        if c >= 3:
            bad.append((u, v, c))
    return bad


def codegree_hist(n, edges):
    adj = adj_from(n, edges)
    h = Counter(len(adj[u] & adj[v]) for u, v in itertools.combinations(range(n), 2))
    return {str(k): v for k, v in sorted(h.items())}


def k23_ceiling(n):
    """Max edges of a K_{2,3}-free graph by the codegree double count:
    sum_v C(d_v,2) <= 2*C(n,2)."""
    d = (1 + (8 * n - 7) ** 0.5) / 2
    return int(n * d / 2)


def codegree_safe(adj, u, v):
    """Adding (u,v): no pair may reach codegree 3. New common-neighbor pairs:
    (u,x) for x in N(v), (v,y) for y in N(u) gain 1; and (u,v) itself is fine."""
    for x in adj[v]:
        if x != u and len(adj[u] & adj[x]) >= 2:
            return False
    for y in adj[u]:
        if y != v and len(adj[v] & adj[y]) >= 2:
            return False
    return True


# ---------- stage 1: edge minimization ----------

def edge_minimize(n, edges, rng):
    """Delete edges while staying 5-UNSAT; violation-involved edges first."""
    E = list(edges)
    changed = True
    while changed:
        changed = False
        bad = codegree_violations(n, E)
        hot = set()
        adj = adj_from(n, E)
        for u, v, _ in bad:
            for x in adj[u] & adj[v]:
                hot.add(tuple(sorted((u, x))))
                hot.add(tuple(sorted((v, x))))
        order = sorted(E, key=lambda e: (e not in hot, rng.random()))
        for e in order:
            E2 = [f for f in E if f != e]
            r, _ = five(n, E2)
            if r is False:
                E = E2
                changed = True
                break
    return norm(E)


# ---------- stage 3 fresh: codegree-aware shrink ----------

def block_to_unsat_aware(n, edges, rng, max_add=MAX_BLOCK_EDGES):
    """Like E13's block loop but PREFERS codegree-safe edges (hard K4 filter,
    soft K_{2,3} filter with fallback)."""
    E = set(edges)
    adj = adj_from(n, edges)
    for _ in range(max_add + 1):
        r, _, model = five(n, sorted(E), model=True)
        if r is False:
            return sorted(E)
        groups = {}
        for v, c in enumerate(model):
            groups.setdefault(c, []).append(v)
        good, fallback = [], []
        for vs in groups.values():
            for u, v in itertools.combinations(vs, 2):
                if v in adj[u] or not safe_to_add(adj, u, v):
                    continue
                (good if codegree_safe(adj, u, v) else fallback).append((u, v))
        pool = good if good else fallback
        if not pool:
            return None
        u, v = rng.choice(pool)
        E.add((u, v))
        adj[u].add(v)
        adj[v].add(u)
    return None


def shrink_run_aware(n, edges, rng, deadline):
    n, edges = critical_core(n, edges, rng)
    while time.time() < deadline:
        success = False
        for v in rng.sample(range(n), n):
            if time.time() > deadline:
                break
            nn, ee = delete_vertex(n, edges, v)
            E2 = block_to_unsat_aware(nn, ee, rng)
            if E2 is not None and k4_free(nn, E2):
                n, edges = critical_core(nn, E2, rng)
                success = True
                break
        if not success:
            break
    return n, edges


# ---------- involutions (L61 congruence advantage) ----------

def pair_swap_involutions(n, edges, alts, cap=40):
    """Count alternators (e1,e2) admitting an automorphism swapping them."""
    try:
        import networkx as nx
        from networkx.algorithms.isomorphism import GraphMatcher
    except ImportError:
        return None
    G = nx.Graph(edges)
    G.add_nodes_from(range(n))
    gm = GraphMatcher(G, G)
    autos = []
    for m in gm.isomorphisms_iter():
        autos.append(m)
        if len(autos) >= 50000:
            break
    hits = 0
    for e1, e2 in alts[:cap]:
        s1, s2 = set(e1), set(e2)
        for a in autos:
            if {a[x] for x in s1} == s2 and {a[x] for x in s2} == s1:
                hits += 1
                break
    return {"aut_count": len(autos), "checked": min(len(alts), cap),
            "with_pair_swap": hits}


# ---------- reporting ----------

def profile(name, n, edges):
    r5, _ = five(n, edges)
    tri, cov = triangle_stats(n, edges)
    dmin, dmax, davg = degree_stats(n, edges)
    bad = codegree_violations(n, edges)
    info = {
        "name": name, "n": n, "m": len(edges),
        "chi6_lower_ok": r5 is False,
        "k4_free": k4_free(n, edges),
        "k23_free": len(bad) == 0,
        "codegree_violations": len(bad),
        "codegree_hist": codegree_hist(n, edges),
        "ky_floor": round(2.8 * n - 1.8, 1),
        "k23_ceiling": k23_ceiling(n),
        "triangles": tri, "tri_covered": cov,
        "deg": [dmin, dmax, davg],
    }
    print(f"  [{name}] n={n} m={len(edges)} KYfloor={info['ky_floor']} "
          f"K23ceil={info['k23_ceiling']} K4free={info['k4_free']} "
          f"K23free={info['k23_free']} (viol={len(bad)}) tri={tri} "
          f"deg=[{dmin},{dmax}]")
    return info


def main():
    t0 = time.time()
    rng = random.Random(SEED)
    results = []

    print("== stage 1+2: edge-minimize E13 finalists ==")
    finalists = json.loads(HOSTS_IN.read_text())["hosts"]
    cores = []
    for h in finalists:
        n, E = h["n"], norm(map(tuple, h["edges"]))
        Em = edge_minimize(n, E, rng)
        info = profile(h["name"] + "_emin", n, Em)
        cores.append((info["name"], n, Em, info))

    print("== stage 3: fresh codegree-aware shrink from seeds ==")
    seeds = build_seeds()
    t_end = time.time() + FRESH_SHRINK_SECONDS
    best_aware = {}
    i = 0
    names = list(seeds)
    while time.time() < t_end - 5:
        nm = names[i % len(names)]
        i += 1
        sub = random.Random(rng.randrange(10 ** 9))
        nf, ef = shrink_run_aware(*seeds[nm], sub,
                                  min(t_end, time.time() + FRESH_SHRINK_SECONDS / 5))
        ef = edge_minimize(nf, ef, sub)
        key = (nf, len(ef))
        if key not in best_aware:
            best_aware[key] = ef
            print(f"  aware restart {i} from {nm}: n={nf} m={len(ef)}")
    for (nf, mf), ef in sorted(best_aware.items())[:4]:
        info = profile(f"aware_{nf}_{mf}", nf, ef)
        cores.append((info["name"], nf, ef, info))

    print("== stage 4: alternator census + involutions on edge-critical cores ==")
    seen = set()
    for name, n, E, info in cores[:5]:
        key = (n, len(E))
        if key in seen:
            continue
        seen.add(key)
        census = alternator_census(n, E, CENSUS_SECONDS)
        info["census"] = census
        alts = [tuple(map(tuple, a)) for a in census["sample_alternators"]]
        # re-collect more alternators for the involution sample if any exist
        inv = pair_swap_involutions(n, E, alts) if alts else None
        info["involutions"] = inv
        info["edges"] = E
        results.append(info)
        print(f"  [{name}] pairs={census['pairs_checked']} "
              f"alt={census['alternators']} inv={inv}")

    payload = {"seed": SEED, "results": results,
               "elapsed_s": round(time.time() - t0, 1)}
    (OUT / "RESULT.json").write_text(json.dumps(payload, indent=1))
    HOSTS_OUT.write_text(json.dumps(
        {"comment": "E13b edge-critical K4-free 6-chromatic hosts; "
                    "k23_free=True members are UDG-plausible alternator carriers",
         "hosts": results}, indent=1))
    print(f"done in {payload['elapsed_s']} s")


if __name__ == "__main__":
    main()
