r"""E14 (L63 redirect): generate a 6-chromatic graph INSIDE the UDG-necessary
class (K4-free AND K_{2,3}-free), seeded from a real UDG.

L63's codegree wall: every manufactured K4-free 6-critical host violates the
UDG codegree bound (<= 2 common neighbors per pair, since two unit circles
meet in <= 2 points). E13's mistake was building ABOVE the class and cutting
down. E14 never leaves the class:

  seed     P510 (real UDG: chi-5, K4-free, K_{2,3}-free automatically;
           both verified at load).
  grow     add blocking edges, each REQUIRED to be K4-safe and codegree-safe
           (hard invariants). Edge choice is greedy-informed: maintain a pool
           of diverse proper 5-colorings (e12-style sampling); add the safe
           non-adjacent pair monochromatic in the MOST pool colorings (kills
           the most colorings per unit of codegree budget). Pool filtered
           after each add; refilled by SAT; refill UNSAT = SUCCESS (chi >= 6).
           No safe candidate = STUCK (a structural finding: the class resists
           6-chromaticity from this seed).
  shrink   batch ddmin vertex deletion preserving 5-UNSAT (deletions preserve
           both freenesses), then per-vertex pass to vertex-criticality, then
           edge minimization (added/abstract edges first, original unit edges
           last, provenance tracked).

Checkpointed and resumable (STATE.json); decision content: does the
UDG-necessary class admit 6-chromatic members at reachable n, at what density
(m/n vs the K_{2,3} ceiling n(1+sqrt(8n-7))/4), and with how many abstract
(non-unit) edges?
"""
from __future__ import annotations
import sys, pathlib, json, time, random, itertools
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import parse_vtx, parse_edges, CACHE, VTX, EDGE
from pysat.solvers import Cadical195

OUT = CACHE / "e14_udg_class"
OUT.mkdir(parents=True, exist_ok=True)
STATE_F = OUT / "STATE.json"

GRAPH = "510"
SEED = 20260611
POOL_TARGET = 80           # diverse 5-colorings kept for edge scoring
POOL_MIN = 24              # refill threshold
MAX_ADDS = 2000
REFILL_BUDGET = 2_000_000  # conflicts before escalating to a decisive solve
SHRINK_WALL_S = float(__import__("os").environ.get("E14_SHRINK_S", 9000))
TOPK = 4000                # safety-check at most this many top-scored pairs/add


# ---------- SAT ----------

def build_clauses(n, edges, k=5):
    var = lambda v, c: v * k + c + 1
    cl = []
    for v in range(n):
        cl.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cl.append([-var(v, c1), -var(v, c2)])
    for u, v in edges:
        for c in range(k):
            cl.append([-var(u, c), -var(v, c)])
    return cl, var


def solve5(n, edges, budget=None, model=False):
    cl, var = build_clauses(n, edges)
    s = Cadical195(bootstrap_with=cl)
    try:
        if budget:
            s.conf_budget(budget)
            res = s.solve_limited()
        else:
            res = s.solve()
        out = None
        if res and model:
            mset = set(x for x in s.get_model() if x > 0)
            out = np.array([next(c for c in range(5) if var(v, c) in mset)
                            for v in range(n)], dtype=np.int8)
        return res, out
    finally:
        s.delete()


def sample_pool(n, edges, want, rng, fix=5, budget=50_000):
    """Diverse colorings via SMALL random assumption sets, conflict-budgeted.
    Near the SAT boundary large random fixings become hard conditional-UNSAT
    proofs (the E14 run-killer); small budgeted ones stay cheap, falling back
    to a plain decisive solve when the assumptions are contradictory."""
    cl, var = build_clauses(n, edges)
    s = Cadical195(bootstrap_with=cl)
    rows = []
    try:
        for _ in range(want):
            fixed = rng.sample(range(n), fix)
            s.conf_budget(budget)
            res = s.solve_limited(
                assumptions=[var(v, rng.randrange(5)) for v in fixed])
            if res is not True:
                if s.solve() is False:
                    return None    # UNSAT: chi >= 6 reached
            m = set(x for x in s.get_model() if x > 0)
            rows.append([next(c for c in range(5) if var(v, c) in m)
                         for v in range(n)])
    finally:
        s.delete()
    return np.array(rows, dtype=np.int8)


# ---------- invariants ----------

def adj_sets(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def codegree_matrix(n, edges):
    A = np.zeros((n, n), dtype=np.int16)
    for u, v in edges:
        A[u, v] = A[v, u] = 1
    return A @ A


def verify_class(n, edges, where):
    adj = adj_sets(n, edges)
    for u, v in edges:
        common = adj[u] & adj[v]
        for x in common:
            if adj[x] & common:
                raise AssertionError(f"K4 at {where}: {u},{v},{x}")
    C = codegree_matrix(n, edges)
    np.fill_diagonal(C, 0)
    mx = C.max()
    if mx > 2:
        raise AssertionError(f"codegree {mx} > 2 at {where}")
    return True


def k4_safe(adj, u, v):
    common = adj[u] & adj[v]
    for x in common:
        if adj[x] & common:
            return False
    return True


def codeg_safe(adj, C, u, v):
    for x in adj[v]:
        if x != u and C[u, x] >= 2:
            return False
    for y in adj[u]:
        if y != v and C[v, y] >= 2:
            return False
    return True


def apply_edge(adj, C, u, v):
    for x in adj[v]:
        if x != u:
            C[u, x] += 1
            C[x, u] += 1
    for y in adj[u]:
        if y != v:
            C[v, y] += 1
            C[y, v] += 1
    adj[u].add(v)
    adj[v].add(u)


# ---------- phase A: grow ----------

def mono_counts(pool):
    s, n = pool.shape
    M = np.zeros((n, n), dtype=np.float32)
    for c in range(5):
        B = (pool == c).astype(np.float32)
        M += B.T @ B
    return M


def grow(n, base_edges, state, rng):
    added = [tuple(e) for e in state.get("added", [])]
    edges = base_edges + added
    adj = adj_sets(n, edges)
    C = codegree_matrix(n, edges)
    np.fill_diagonal(C, 0)
    A = np.zeros((n, n), dtype=bool)
    for u, v in edges:
        A[u, v] = A[v, u] = True

    pool = sample_pool(n, edges, POOL_TARGET, rng)
    if pool is None:
        return added, "already_unsat"
    t_last = time.time()
    while len(added) < MAX_ADDS:
        M = mono_counts(pool)
        M[A] = -1
        np.fill_diagonal(M, -1)
        iu = np.triu_indices(n, 1)
        scores = M[iu]
        order = np.argsort(scores)[::-1][:TOPK]
        pick = None
        for idx in order:
            if scores[idx] < 0:
                break
            u, v = int(iu[0][idx]), int(iu[1][idx])
            if k4_safe(adj, u, v) and codeg_safe(adj, C, u, v):
                pick = (u, v)
                break
        if pick is None:
            return added, "stuck_no_safe_candidate"
        u, v = pick
        apply_edge(adj, C, u, v)
        A[u, v] = A[v, u] = True
        added.append((u, v))
        edges.append((u, v))
        pool = pool[pool[:, u] != pool[:, v]]
        if len(added) % 25 == 0 or time.time() - t_last > 60:
            state["added"] = added
            STATE_F.write_text(json.dumps(state))
            t_last = time.time()
            print(f"  grow: {len(added)} added, pool={len(pool)}, "
                  f"last mono={int(scores[idx])}/{POOL_TARGET}", flush=True)
        if len(pool) < POOL_MIN:
            res, _ = solve5(n, edges, budget=REFILL_BUDGET)
            if res is None:
                print("  refill indeterminate; decisive solve...", flush=True)
                res, _ = solve5(n, edges)
            if res is False:
                return added, "success_unsat"
            fresh = sample_pool(n, edges, POOL_TARGET, rng)
            if fresh is None:
                return added, "success_unsat"
            pool = fresh
    return added, "max_adds_exhausted"


# ---------- phase B: shrink ----------

def relabel(active, edges):
    idx = {v: i for i, v in enumerate(active)}
    return len(active), [(idx[u], idx[v]) for u, v in edges
                         if u in idx and v in idx]


def shrink(n, base_edges, added, state, rng, wall_s):
    """active: original labels kept. All edges (base+added) filtered to active.
    Batch ddmin then per-vertex pass, preserving 5-UNSAT."""
    active = state.get("active") or list(range(n))
    all_edges = base_edges + [tuple(e) for e in added]
    t_end = time.time() + wall_s

    def is_unsat(act):
        nn, ee = relabel(act, all_edges)
        r, _ = solve5(nn, ee)
        return r is False

    batch = max(1, len(active) // 4)
    while batch >= 1 and time.time() < t_end:
        progress = False
        order = rng.sample(active, len(active))
        i = 0
        while i < len(order) and time.time() < t_end:
            cand = [v for v in order[i:i + batch] if v in active]
            i += batch
            if not cand:
                continue
            trial = [v for v in active if v not in set(cand)]
            if trial and is_unsat(trial):
                active = trial
                progress = True
                state["active"] = active
                STATE_F.write_text(json.dumps(state))
                print(f"  shrink: -{len(cand)} -> n={len(active)} "
                      f"(batch={batch})", flush=True)
        if not progress:
            batch //= 2
    state["active"] = active
    STATE_F.write_text(json.dumps(state))

    # edge minimization: added edges first (abstract liabilities), then base
    nn, _ = relabel(active, all_edges)
    act_set = set(active)
    kept_added = [e for e in added if e[0] in act_set and e[1] in act_set]
    kept_base = [e for e in base_edges if e[0] in act_set and e[1] in act_set]
    changed = True
    while changed and time.time() < t_end:
        changed = False
        for src, lst in (("added", kept_added), ("base", kept_base)):
            for e in list(lst):
                if time.time() > t_end:
                    break
                trial = [x for x in kept_added if x != e] if src == "added" \
                    else kept_added
                trialb = kept_base if src == "added" \
                    else [x for x in kept_base if x != e]
                nn2, ee2 = relabel(active, trialb + trial)
                r, _ = solve5(nn2, ee2)
                if r is False:
                    lst.remove(e)
                    changed = True
                    print(f"  emin: dropped {src} edge {e}", flush=True)
                    break
            if changed:
                break
    state["final"] = {"active": active,
                      "added": kept_added, "base": kept_base}
    STATE_F.write_text(json.dumps(state))
    return active, kept_base, kept_added


# ---------- main ----------

def main():
    rng = random.Random(SEED)
    base = parse_vtx(VTX / f"{GRAPH}.vtx")
    base_edges = [tuple(e) for e in parse_edges(EDGE / f"{GRAPH}.edge")]
    n = len(base)
    print(f"P{GRAPH}: n={n} m={len(base_edges)}", flush=True)
    verify_class(n, base_edges, "seed")
    print("seed verified: K4-free AND K_{2,3}-free", flush=True)

    state = json.loads(STATE_F.read_text()) if STATE_F.exists() else {}
    if "grow_status" not in state:
        t0 = time.time()
        added, status = grow(n, base_edges, state, rng)
        state.update({"added": added, "grow_status": status,
                      "grow_s": round(time.time() - t0, 1)})
        STATE_F.write_text(json.dumps(state))
    print(f"grow: {state['grow_status']} with {len(state['added'])} edges "
          f"({state.get('grow_s', '?')} s)", flush=True)
    if not str(state["grow_status"]).startswith("success"):
        print("no 6-chromatic graph reached; stopping (structural finding).",
              flush=True)
        return

    t0 = time.time()
    active, kb, ka = shrink(n, base_edges, state["added"], state, rng,
                            SHRINK_WALL_S)
    nn, ee = relabel(active, kb + ka)
    r, _ = solve5(nn, ee)
    verify_class(nn, ee, "final")
    ceil = int(nn * (1 + (8 * nn - 7) ** 0.5) / 4)
    summary = {
        "n": nn, "m": len(ee), "m_base_unit": len(kb), "m_added_abstract": len(ka),
        "five_unsat": r is False, "ky_floor": round(2.8 * nn - 1.8, 1),
        "k23_ceiling": ceil, "shrink_s": round(time.time() - t0, 1),
    }
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
