r"""E13 (L61 route 1 gate): a nauty-free SOURCE of small triangle-rich K4-free
6-chromatic hosts.

L62 left exactly one live phase-route door: rebuild the equality-alternator on a
small omega=3 (triangle-rich, K4-free) 6-critical host. The 47-vtx M^3(C5) host
is triangle-free (worst UDG substrate, L61 warning) and no enumerator exists on
this machine (no nauty), so this script MANUFACTURES hosts:

  Stage 1  deterministic seeds. M(M(W5)) (27 vtx) and M(M(C5)+K1) (25 vtx).
           Mycielski preserves K4-freeness (a K4-free graph has triangle-free
           neighborhoods, so shadow+triangle cliques cannot form) and adds
           chi+1; W5 / the apex inject triangles. Both seeds are verified from
           scratch (K4-free, 5-UNSAT, 6-SAT, vertex-critical, triangle stats).
  Stage 2  SAT-guided shrink. Delete a vertex (the critical host drops to
           5-colorable), then push back to 5-UNSAT by adding K4-safe blocking
           edges between same-colored non-adjacent pairs of successive SAT
           models; on success extract the vertex-critical core and recurse.
           Multi-restart under a global deadline; stuck sizes histogrammed
           (empirical evidence toward the K4-free 6-chromatic floor, L51's
           [9,48]).
  Stage 3  alternator census on the finalists. For disjoint edge pairs
           (e1,e2) of host K: diff-diff is K itself (auto 5-UNSAT); the filter
           is merge-BOTH 5-UNSAT (1 SAT call); survivors get exact
           non-degeneracy checks (only-e1-same SAT, only-e2-same SAT). Hosts
           here are vertex-critical but not necessarily edge-critical, so
           non-degeneracy is NOT automatic (unlike L60's M^3(C5)); it is
           tested, never assumed.

Products: smallest hosts found (committed in e13_hosts.json), triangle/degree
profiles (UDG-plausibility), alternator counts with samples.
"""
from __future__ import annotations
import sys, pathlib, json, time, random, itertools
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import sat_kcolor, CACHE
from pysat.solvers import Cadical195

OUT = CACHE / "e13_small_hosts"
OUT.mkdir(parents=True, exist_ok=True)
HOSTS_JSON = pathlib.Path(__file__).resolve().parent / "e13_hosts.json"

SEED = 20260611
SHRINK_SECONDS = 240.0          # total wall budget for stage 2
CENSUS_SECONDS = 90.0           # per-host wall budget for stage 3
MAX_BLOCK_EDGES = 130           # blocking-edge budget per vertex-deletion attempt


# ---------- graph primitives (edges = sorted tuples over range(n)) ----------

def norm(edges):
    return sorted(set(tuple(sorted(e)) for e in edges))


def adj_from(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def cycle(k):
    return k, [(i, (i + 1) % k) for i in range(k)]


def apex(n, edges):
    return n + 1, norm(list(edges) + [(i, n) for i in range(n)])


def mycielski(n, edges):
    """Originals 0..n-1, shadows n..2n-1 (shadow of i = n+i), z = 2n."""
    out = list(edges)
    for u, v in edges:
        out.append((n + u, v))
        out.append((n + v, u))
    for i in range(n):
        out.append((n + i, 2 * n))
    return 2 * n + 1, norm(out)


def delete_vertex(n, edges, v):
    remap = lambda w: w if w < v else w - 1
    return n - 1, norm((remap(u), remap(w)) for u, w in edges if v not in (u, w))


def merge_vertices(n, edges, pairs):
    """Identify b->a for each (a,b); drop self-loops; compact labels."""
    m = list(range(n))
    for a, b in pairs:
        m[b] = a
    gone = sorted(b for _, b in pairs)
    shift = lambda w: w - sum(1 for g in gone if g < w)
    out = set()
    for u, v in edges:
        a, b = m[u], m[v]
        if a != b:
            out.add(tuple(sorted((shift(a), shift(b)))))
    return n - len(pairs), sorted(out)


def k4_free(n, edges):
    adj = adj_from(n, edges)
    for u, v in edges:
        common = adj[u] & adj[v]
        for x in common:
            if adj[x] & common:
                return False
    return True


def safe_to_add(adj, u, v):
    """Adding (u,v) creates a K4 iff their common neighborhood contains an edge."""
    common = adj[u] & adj[v]
    for x in common:
        if adj[x] & common:
            return False
    return True


def triangle_stats(n, edges):
    adj = adj_from(n, edges)
    tri = 0
    covered = set()
    for u, v in edges:
        c = adj[u] & adj[v]
        tri += len(c)
        if c:
            covered.update((u, v))
            covered.update(c)
    return tri // 3, len(covered)


def degree_stats(n, edges):
    adj = adj_from(n, edges)
    degs = sorted(len(a) for a in adj)
    return degs[0], degs[-1], round(2 * len(edges) / n, 2)


def five(n, edges, model=False, budget=None):
    return sat_kcolor(n, edges, 5, Cadical195,
                      budget_conflicts=budget, return_model=model)


# ---------- stage 1: seeds + verification ----------

def build_seeds():
    w5 = apex(*cycle(5))                       # 6 vtx, chi 4
    grotzsch = mycielski(*cycle(5))            # 11 vtx, chi 4, triangle-free
    seeds = {
        "M2_W5": mycielski(*mycielski(*w5)),               # 27 vtx
        "M_grotzsch_apex": mycielski(*apex(*grotzsch)),    # 25 vtx
    }
    return seeds


def verify_host(name, n, edges, check_critical=True):
    res5, t5 = five(n, edges)
    res6, t6 = sat_kcolor(n, edges, 6, Cadical195)
    crit = None
    if check_critical:
        crit = True
        for v in range(n):
            r, _ = five(*delete_vertex(n, edges, v))
            if r is not True:
                crit = False
                break
    tri, cov = triangle_stats(n, edges)
    dmin, dmax, davg = degree_stats(n, edges)
    info = {
        "name": name, "n": n, "m": len(edges),
        "k4_free": k4_free(n, edges),
        "chi6": (res5 is False) and (res6 is True),
        "vertex_critical": crit,
        "triangles": tri, "tri_covered_vertices": cov,
        "deg_min": dmin, "deg_max": dmax, "deg_avg": davg,
        "ky_bound_2.8n-1.8": round(2.8 * n - 1.8, 1),
    }
    print(f"  [{name}] n={n} m={len(edges)} K4free={info['k4_free']} "
          f"chi6={info['chi6']} crit={crit} tri={tri} cov={cov}/{n} "
          f"deg=[{dmin},{dmax}] avg={davg}")
    return info


# ---------- stage 2: shrink ----------

def critical_core(n, edges, rng):
    changed = True
    while changed:
        changed = False
        for v in rng.sample(range(n), n):
            nn, ee = delete_vertex(n, edges, v)
            r, _ = five(nn, ee)
            if r is False:
                n, edges = nn, ee
                changed = True
                break
    return n, edges


def block_to_unsat(n, edges, rng, max_add=MAX_BLOCK_EDGES):
    """Add K4-safe edges between same-colored non-adjacent pairs until 5-UNSAT.
    Returns the new edge list on success, None if stuck or budget exhausted."""
    E = set(edges)
    adj = adj_from(n, edges)
    for _ in range(max_add + 1):
        r, _, model = five(n, sorted(E), model=True)
        if r is False:
            return sorted(E)
        groups = {}
        for v, c in enumerate(model):
            groups.setdefault(c, []).append(v)
        cands = []
        for vs in groups.values():
            for u, v in itertools.combinations(vs, 2):
                if v not in adj[u] and safe_to_add(adj, u, v):
                    cands.append((u, v))
        if not cands:
            return None
        u, v = rng.choice(cands)
        E.add((u, v))
        adj[u].add(v)
        adj[v].add(u)
    return None


def shrink_run(n, edges, rng, deadline):
    """One descent: repeatedly (delete vertex -> re-force -> core) until stuck."""
    n, edges = critical_core(n, edges, rng)
    while time.time() < deadline:
        success = False
        for v in rng.sample(range(n), n):
            if time.time() > deadline:
                break
            nn, ee = delete_vertex(n, edges, v)
            E2 = block_to_unsat(nn, ee, rng)
            if E2 is not None and k4_free(nn, E2):
                n, edges = critical_core(nn, E2, rng)
                success = True
                break
        if not success:
            break
    return n, edges


def shrink_stage(seeds_verified, budget_s):
    rng = random.Random(SEED)
    t_end = time.time() + budget_s
    best = {}      # n -> (name, edges)
    stuck_sizes = Counter()
    starts = [(name, n, edges) for name, (n, edges) in seeds_verified.items()]
    run_idx = 0
    while time.time() < t_end - 5:
        name, n0, e0 = starts[run_idx % len(starts)]
        run_idx += 1
        sub = random.Random(rng.randrange(10 ** 9))
        per_run_deadline = min(t_end, time.time() + budget_s / 6)
        nf, ef = shrink_run(n0, e0, sub, per_run_deadline)
        stuck_sizes[nf] += 1
        if nf not in best:
            best[nf] = (f"shrunk_{nf}_from_{name}", ef)
        print(f"  restart {run_idx} from {name}: stuck at n={nf} "
              f"(t={time.time() % 1e5:.0f})")
    return best, dict(stuck_sizes)


# ---------- stage 3: alternator census ----------

def alternator_census(n, edges, budget_s):
    """K 6-chromatic. Disjoint edge pairs (e1,e2): filter merge-both 5-UNSAT,
    then exact non-degeneracy. Returns counts + samples."""
    E = list(edges)
    t_end = time.time() + budget_s
    pairs_checked = 0
    survivors = []
    alternators = []
    timeout = False
    for i, j in itertools.combinations(range(len(E)), 2):
        if time.time() > t_end:
            timeout = True
            break
        e1, e2 = E[i], E[j]
        if set(e1) & set(e2):
            continue
        pairs_checked += 1
        G = [e for e in E if e not in (e1, e2)]
        nm, em = merge_vertices(n, G, [e1, e2])
        r, _ = five(nm, em)
        if r is not False:
            continue
        survivors.append((e1, e2))
        # only-e1-same: merge e1 in G + e2 ; only-e2-same symmetric
        n1, ee1 = merge_vertices(n, G + [e2], [e1])
        r1, _ = five(n1, ee1)
        n2, ee2 = merge_vertices(n, G + [e1], [e2])
        r2, _ = five(n2, ee2)
        if r1 is True and r2 is True:
            alternators.append((e1, e2))
    return {
        "pairs_checked": pairs_checked,
        "merge_both_unsat": len(survivors),
        "alternators": len(alternators),
        "sample_alternators": alternators[:5],
        "timeout": timeout,
    }


# ---------- main ----------

def main():
    t0 = time.time()
    print("== stage 1: deterministic seeds ==")
    seeds = build_seeds()
    seed_info = {}
    seeds_ok = {}
    for name, (n, edges) in seeds.items():
        info = verify_host(name, n, edges)
        seed_info[name] = info
        if info["k4_free"] and info["chi6"]:
            seeds_ok[name] = (n, edges)
    if not seeds_ok:
        print("NO valid seeds; abort.")
        return

    print("== stage 2: SAT-guided shrink ==")
    best, stuck_hist = shrink_stage(seeds_ok, SHRINK_SECONDS)
    print(f"  stuck-size histogram: {stuck_hist}")

    print("== stage 3: verify finalists + alternator census ==")
    finalists = sorted(best.items())[:2]   # up to 2 smallest distinct sizes
    results = []
    for nf, (name, ef) in finalists:
        info = verify_host(name, nf, ef)
        census = alternator_census(nf, ef, CENSUS_SECONDS)
        info["census"] = census
        info["edges"] = ef
        results.append(info)
        print(f"  [{name}] pairs={census['pairs_checked']} "
              f"merge_both_unsat={census['merge_both_unsat']} "
              f"ALTERNATORS={census['alternators']} timeout={census['timeout']}")

    payload = {
        "seed": SEED,
        "seeds": seed_info,
        "stuck_histogram": stuck_hist,
        "finalists": results,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (OUT / "RESULT.json").write_text(json.dumps(payload, indent=1))
    HOSTS_JSON.write_text(json.dumps(
        {"comment": "E13 small K4-free 6-chromatic hosts (vertex-critical cores)",
         "hosts": results}, indent=1))
    print(f"done in {payload['elapsed_s']} s; results in {OUT / 'RESULT.json'}")


if __name__ == "__main__":
    main()
