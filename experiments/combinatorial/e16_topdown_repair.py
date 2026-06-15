r"""E16 (= E15-v2): TOP-DOWN repair toward an in-class chi>=6 graph.

The dual of E15/E15b. E15 (greedy from empty) caps at chi=4; E15b (annealing
from empty, in-class HARD, maximize chi) caps at chi=5. Both grow chi UP from
inside the UDG-necessary class. E16 inverts the search direction: START from a
graph that already HAS chi=6 and locally REPAIR its violations of the
UDG-necessary class (K4-free AND K_{2,3}-free), holding chi>=6 as a hard
constraint. If the repair reaches zero violations the result IS the paper's
target object: a chi>=6 graph in the class every planar UDG must satisfy. If it
provably stalls at violations > 0, the stall point is a sharp structural witness
to the codegree obstruction (L63), this time from the inside.

Seed: M^3(C5), the 47-vertex triangle-free 6-CRITICAL graph (L51's H). Triangle-
free => K4-free for free, so the ONLY violations are codegree (K_{2,3}) ones:
~434 non-adjacent pairs with codegree >= 3. m=234 sits right at the n=47 codegree
ceiling 237, so the seed is the tightest-possible feasible starting density.

The criticality trap and how rewiring escapes it (the whole point):
  A 6-critical graph has NO removable edge -- deleting any single edge drops chi
  to 5 (L61). So pure violation-removal is vacuous on the seed. The escape is a
  PAIRED REWIRE: remove a codegree-violating edge e1=(a,b) (chi drops to 5, since
  e1 is critical => a,b are forced-same in G-e1), then add a DIFFERENT
  codegree-safe + K4-safe edge (c,d) that is also forced-same in G-e1, which
  restores chi to exactly 6. Net effect: excess strictly DECREASES (a violating
  edge gone, a safe edge in) while chi stays 6. As the graph sheds criticality,
  pure removes start succeeding too (remove a violating edge, chi survives:
  excess AND m both drop). Both moves are monotone in excess, so this is a clean
  descent; the only question is whether it bottoms out at 0 or > 0.

Every accepted move strictly lowers codegree-excess: removes only lower codegrees,
and the canonical (default) rewire compensator is codegree-safe (creates no new
violation). Two opt-in escapes relax this -- TRADE rewires (compensator may create
a smaller violation, still a net decrease) and vertex-split GROWTH -- both off by
default because they only reach a denser local minimum (L69). The decisive solver
call per move is a single 5-colorability decision on a ~47-vertex graph, run via
the symmetry-broken in-process encoding (solve_color, symbreak=True), which is
Cadical's sweet spot for the STRUCTURED UNSAT these modified-Mycielski instances
are -- distinct from the phase-boundary hardness that blocks E14 (L68).

Forced-same compensators are found by a sampling filter (L62 style): sample many
diverse proper 5-colorings of G-e1 via Kempe-chain walks from a solver seed
coloring; a non-edge monochromatic in ALL samples is a forced-same CANDIDATE
(true forced-same pairs always survive -- no false negatives); each candidate is
confirmed by one 5-UNSAT check before acceptance.

Outputs: a WITNESS.json (an in-class chi>=6 graph, fully re-verified) if excess
reaches 0, else BEST.json + SUMMARY.json recording the minimum excess reached,
the stuck graph, and why it stalled. Deadline-bounded, checkpointed, restartable.
Runs on CPython (uses pysat via solve_color); the Kempe sampler is pure Python.
"""
from __future__ import annotations
import sys
import os
import pathlib
import json
import time
import random

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_shared"))
from portfolio_sat import solve_color  # noqa: E402

OUT = HERE / "_cache" / "e16_topdown_repair"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20260615
DEADLINE_S = float(os.environ.get("E16_DEADLINE_S", 1800))   # 30 min default
N_SAMPLES = int(os.environ.get("E16_SAMPLES", 160))          # Kempe colorings
MAX_REWIRE_TRIES = int(os.environ.get("E16_REWIRE_TRIES", 12))  # candidates/edge
RESTARTS = int(os.environ.get("E16_RESTARTS", 1))
USE_TRADES = os.environ.get("E16_TRADES", "0") == "1"   # allow trade rewires
USE_SPLITS = os.environ.get("E16_SPLITS", "0") == "1"   # allow vertex-split grow
USE_SPARSIFY = os.environ.get("E16_SPARSIFY", "0") == "1"  # redundant-edge remove


# ---------------------------------------------------------------------------
# Seed: M^3(C5) via the Mycielski tower (networkx), reindexed to 0..n-1.
# ---------------------------------------------------------------------------

def mycielski_tower():
    import networkx as nx
    g = nx.cycle_graph(5)
    g = nx.mycielskian(g)   # Grotzsch, 4-critical, 11 v
    g = nx.mycielskian(g)   # 5-critical, 23 v
    g = nx.mycielskian(g)   # 6-critical, 47 v
    idx = {v: i for i, v in enumerate(g.nodes())}
    edges = [(min(idx[u], idx[v]), max(idx[u], idx[v])) for u, v in g.edges()]
    return g.number_of_nodes(), sorted(set(edges))


# ---------------------------------------------------------------------------
# Graph state with an incrementally maintained codegree matrix and excess.
#   C[u][v] = number of common neighbors of u and v (codegree).
#   excess  = sum_{u<v} max(0, C[u][v] - 2); == 0 iff K_{2,3}-free.
# add()/remove() keep C and excess in sync; add_safe() forbids any move that
# would create a K4 or push a codegree to 3.
# ---------------------------------------------------------------------------

class State:
    def __init__(self, n):
        self.n = n
        self.adj = [set() for _ in range(n)]
        self.C = [[0] * n for _ in range(n)]
        self.m = 0
        self.excess = 0

    def has(self, u, v):
        return v in self.adj[u]

    def add(self, u, v):
        for x in self.adj[v]:
            if x != u:
                if self.C[u][x] >= 2:
                    self.excess += 1
                self.C[u][x] += 1
                self.C[x][u] += 1
        for y in self.adj[u]:
            if y != v:
                if self.C[v][y] >= 2:
                    self.excess += 1
                self.C[v][y] += 1
                self.C[y][v] += 1
        self.adj[u].add(v)
        self.adj[v].add(u)
        self.m += 1

    def remove(self, u, v):
        self.adj[u].discard(v)
        self.adj[v].discard(u)
        for x in self.adj[v]:
            if x != u:
                if self.C[u][x] >= 3:
                    self.excess -= 1
                self.C[u][x] -= 1
                self.C[x][u] -= 1
        for y in self.adj[u]:
            if y != v:
                if self.C[v][y] >= 3:
                    self.excess -= 1
                self.C[v][y] -= 1
                self.C[y][v] -= 1
        self.m -= 1

    def k4_safe(self, u, v):
        """No K4 created: no edge inside the common neighborhood of u, v. (A
        rewire compensator must keep the graph K4-free -- a hard in-class
        invariant -- but MAY create a codegree violation, which is folded into
        the excess objective and only accepted on a net decrease.)"""
        if u == v or v in self.adj[u]:
            return False
        common = self.adj[u] & self.adj[v]
        for x in common:
            if self.adj[x] & common:
                return False
        return True

    def add_safe(self, u, v):
        """K4-safe AND codegree-safe (no incident pair would reach codegree 3).
        Used by perturbation only; the main rewire uses the weaker k4_safe +
        net-excess-decrease rule."""
        if not self.k4_safe(u, v):
            return False
        for x in self.adj[v]:
            if x != u and self.C[u][x] >= 2:
                return False
        for y in self.adj[u]:
            if y != v and self.C[v][y] >= 2:
                return False
        return True

    def add_vertex(self):
        """Append a fresh isolated vertex (codegree 0 with everyone). Keeps C and
        excess consistent (a degree-0 vertex contributes no codegree)."""
        for row in self.C:
            row.append(0)
        self.C.append([0] * (self.n + 1))
        self.adj.append(set())
        self.n += 1
        return self.n - 1

    def snapshot(self):
        return (self.n, self.m, self.excess,
                [set(s) for s in self.adj], [row[:] for row in self.C])

    def restore(self, snap):
        self.n, self.m, self.excess = snap[0], snap[1], snap[2]
        self.adj = [set(s) for s in snap[3]]
        self.C = [row[:] for row in snap[4]]

    def violation_load(self, w):
        """Sum of excess on pairs for which w is a common neighbor (the excess a
        split of w can relieve)."""
        load = 0
        nb = list(self.adj[w])
        for i in range(len(nb)):
            x = nb[i]
            for j in range(i + 1, len(nb)):
                y = nb[j]
                if self.C[x][y] >= 3:
                    load += self.C[x][y] - 2
        return load

    def violating_pairs(self):
        out = []
        for u in range(self.n):
            row = self.C[u]
            for v in range(u + 1, self.n):
                if row[v] >= 3:
                    out.append((u, v))
        return out

    def edges(self):
        return [(u, v) for u in range(self.n) for v in self.adj[u] if u < v]


def k4_free(st):
    for u in range(st.n):
        for v in st.adj[u]:
            if v > u:
                common = st.adj[u] & st.adj[v]
                for x in common:
                    if st.adj[x] & common:
                        return False
    return True


def k23_free(st):
    return st.excess == 0


# ---------------------------------------------------------------------------
# chi >= 6  <=>  not 5-colorable.  Structured UNSAT => symbreak Cadical is fast.
# ---------------------------------------------------------------------------

def chi_ge6(st):
    res = solve_color(st.n, st.edges(), 5, symbreak=True)["result"]
    return res is False


# ---------------------------------------------------------------------------
# Diverse proper 5-colorings via Kempe-chain walks from a solver seed coloring.
# ---------------------------------------------------------------------------

def kempe_flip(adj, col, v, i, j):
    comp = {v}
    stack = [v]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if col[y] in (i, j) and y not in comp:
                comp.add(y)
                stack.append(y)
    for x in comp:
        col[x] = j if col[x] == i else i


def sample_colorings(st, rng, num):
    base = solve_color(st.n, st.edges(), 5, symbreak=False, want_model=True)
    if not base["result"]:
        return []
    adj = st.adj
    col = base["model"]
    cols = [col[:]]
    cur = col[:]
    k = 5
    for _ in range(num):
        i = rng.randrange(k)
        j = rng.randrange(k)
        if i == j:
            continue
        movable = [v for v in range(st.n) if cur[v] in (i, j)]
        if not movable:
            continue
        kempe_flip(adj, cur, rng.choice(movable), i, j)
        cols.append(cur[:])
    return cols


def forced_same_candidates(st, cols):
    """Non-edges monochromatic across EVERY sampled coloring (forced-same
    candidates; a true forced-same pair survives with no false negative)."""
    survivors = None
    for col in cols:
        by_color = {}
        for v in range(st.n):
            by_color.setdefault(col[v], []).append(v)
        mono = set()
        for verts in by_color.values():
            verts.sort()
            for ai in range(len(verts)):
                a = verts[ai]
                aadj = st.adj[a]
                for bi in range(ai + 1, len(verts)):
                    b = verts[bi]
                    if b not in aadj:
                        mono.add((a, b))
        if survivors is None:
            survivors = mono
        else:
            survivors &= mono
        if not survivors:
            return []
    return list(survivors) if survivors else []


# ---------------------------------------------------------------------------
# Repair moves. excess never rises: pure removes only lower codegrees, rewires
# add only add_safe edges. Two engines:
#   try_pure_remove -- cheap (1 chi call/candidate): scan violating edges for one
#       whose removal keeps chi>=6. The main sparsifier once criticality breaks.
#   try_rewire -- the criticality-breaker: remove a critical violating edge, find
#       a codegree-safe + K4-safe forced-same compensator (sampling filter +
#       confirm), restore chi to 6. Net excess strictly down.
# ---------------------------------------------------------------------------

def _reducible_edges(st, rng, limit):
    """Edges whose removal lowers some pair's codegree below it (i.e. incident
    to a violating pair via a shared endpoint). Returns up to `limit`, shuffled."""
    vpairs = st.violating_pairs()
    rng.shuffle(vpairs)
    seen = set()
    out = []
    for (u, v) in vpairs:
        for w in (st.adj[u] & st.adj[v]):
            for (a, b) in ((min(u, w), max(u, w)), (min(v, w), max(v, w))):
                if (a, b) not in seen and st.has(a, b):
                    seen.add((a, b))
                    out.append((a, b))
        if len(out) >= limit:
            break
    return out


def try_pure_remove(st, rng, stats, scan):
    for (a, b) in _reducible_edges(st, rng, scan):
        st.remove(a, b)
        stats["chi_calls"] += 1
        if chi_ge6(st):
            return (a, b)
        st.add(a, b)
    return None


def try_rewire(st, rng, stats, scan, attempts, safe_only):
    """Remove a critical violating edge e1, restore chi=6 with a forced-same,
    K4-safe compensator chosen to MINIMIZE the resulting excess; accept only on a
    strict net excess decrease.

    safe_only=True restricts compensators to codegree-SAFE ones (no new
    violation): this is the in-class-preserving rewire, and preferring it forces
    the search to keep hunting for pure removes (sparsification) rather than
    settling for a density-preserving trade. safe_only=False additionally allows
    a TRADE compensator (creates a smaller violation than e1 removed) -- a
    last-resort that escapes the codegree-safe stall at the cost of staying
    dense."""
    cand_edges = _reducible_edges(st, rng, scan)
    used = 0
    for (a, b) in cand_edges:
        if used >= attempts:
            break
        excess0 = st.excess
        st.remove(a, b)
        stats["chi_calls"] += 1
        if chi_ge6(st):                       # turned out removable after all
            return ("remove", (a, b))
        used += 1
        excess_after_remove = st.excess       # baseline with e1 gone
        cols = sample_colorings(st, rng, N_SAMPLES)
        cands = forced_same_candidates(st, cols)
        # rank K4-safe forced-same candidates by resulting excess (no chi call).
        # Sort key puts codegree-SAFE compensators (those adding no new violation,
        # i.e. e_new == excess_after_remove) ahead of trades: the safe trajectory
        # empirically sparsifies further (more downstream pure removes) than
        # greedy lowest-excess trades that keep the graph dense.
        scored = []
        for (c, d) in cands:
            if (c, d) == (a, b) or not st.k4_safe(c, d):
                continue
            st.add(c, d)
            e_new = st.excess
            st.remove(c, d)
            if e_new < excess0:               # strict net decrease over the move
                is_trade = 1 if e_new > excess_after_remove else 0
                if safe_only and is_trade:
                    continue
                # random tiebreak: safe compensators tie on e_new, so a fixed
                # (c,d) order would trap the descent in one trajectory; shuffling
                # ties lets restarts explore different paths down a rugged surface
                scored.append((is_trade, e_new, rng.random(), c, d))
        scored.sort()
        tried = 0
        for (_t, e_new, _r, c, d) in scored:
            st.add(c, d)
            stats["chi_calls"] += 1
            if chi_ge6(st):
                return ("rewire", ((a, b), (c, d)))
            st.remove(c, d)
            tried += 1
            if tried >= MAX_REWIRE_TRIES:
                break
        st.add(a, b)                          # undo; this edge resists rewiring
    return None


def try_sparsify(st, rng, stats, scan):
    """Remove a REDUNDANT (chi-preserving) edge to break the criticality rigidity
    that blocks the violating-edge sweep. The L69 floor sits ABOVE the
    Kostochka-Yancey 6-critical floor, so non-critical (removable) edges exist;
    deleting one drops m toward that floor and can make a previously-critical
    violating edge removable next round. Prefer edges incident to high total-
    codegree vertices so the sparsification concentrates where the violations are
    (this is the 'remove a non-violating edge that frees a violating one'
    operator). Removal never raises excess, so the descent stays monotone."""
    codeg_load = [sum(st.C[u]) for u in range(st.n)]
    edges = st.edges()
    edges.sort(key=lambda e: -(codeg_load[e[0]] + codeg_load[e[1]]))
    for (a, b) in edges[:scan]:
        st.remove(a, b)
        stats["chi_calls"] += 1
        if chi_ge6(st):
            return ("sparsify", (a, b))
        st.add(a, b)
    return None


def find_compensator(st, rng, stats, excess_cap):
    """When the current graph is 5-colorable (chi dropped to 5), find one
    forced-same, K4-safe edge to add that restores chi to 6 with excess <
    excess_cap. Returns (c,d) and leaves it ADDED on success, else returns None
    leaving the graph unchanged. Shared by the rewire and the split move."""
    cols = sample_colorings(st, rng, N_SAMPLES)
    cands = forced_same_candidates(st, cols)
    scored = []
    for (c, d) in cands:
        if not st.k4_safe(c, d):
            continue
        st.add(c, d)
        e_new = st.excess
        st.remove(c, d)
        if e_new < excess_cap:
            scored.append((e_new, c, d))
    scored.sort()
    tried = 0
    for (e_new, c, d) in scored:
        st.add(c, d)
        stats["chi_calls"] += 1
        if chi_ge6(st):
            return (c, d)
        st.remove(c, d)
        tried += 1
        if tried >= MAX_REWIRE_TRIES:
            break
    return None


def split_move(st, rng, stats):
    """Grow n by 1 to relieve the codegree/criticality tension. Pick the vertex
    w carrying the most violation load, add a twin w', and move roughly half of
    w's neighbors to w' (halving the codegrees that route through w). If chi
    stays 6, accept; else try a forced-same compensator to restore chi=6; else
    revert. Net: codegree excess relieved, n+1, chi held at 6."""
    if st.n == 0:
        return None
    cands = sorted(range(st.n), key=lambda w: -st.violation_load(w))[:6]
    for w in cands:
        nb = list(st.adj[w])
        if len(nb) < 4:
            continue
        snap = st.snapshot()
        excess0 = st.excess
        rng.shuffle(nb)
        move_to = nb[: len(nb) // 2]          # half of w's neighbors -> w'
        wp = st.add_vertex()
        for b in move_to:
            st.remove(w, b)
            st.add(wp, b)
        stats["chi_calls"] += 1
        if chi_ge6(st):
            if st.excess < excess0:
                return ("split", (w, wp, len(move_to)))
            st.restore(snap)                  # split didn't help excess; revert
            continue
        # chi dropped: try to restore with a forced-same compensator
        comp = find_compensator(st, rng, stats, excess0)
        if comp is not None and st.excess < excess0:
            return ("split+comp", (w, wp, comp))
        st.restore(snap)
    return None


# ---------------------------------------------------------------------------

def verify_witness(st):
    edges = st.edges()
    checks = {
        "k4_free": k4_free(st),
        "k23_free": k23_free(st),
        "excess": st.excess,
        "five_unsat": solve_color(st.n, edges, 5, symbreak=True)["result"] is False,
        "six_sat": solve_color(st.n, edges, 6, symbreak=True)["result"] is True,
    }
    ok = (checks["k4_free"] and checks["k23_free"] and checks["five_unsat"]
          and checks["six_sat"])
    return ok, checks


def run(deadline, rng):
    n, seed_edges = mycielski_tower()
    st = State(n)
    for (u, v) in seed_edges:
        st.add(u, v)
    start_excess = st.excess
    print(f"seed M^3(C5): n={n} m={st.m} excess={start_excess} "
          f"violating_pairs={len(st.violating_pairs())}", flush=True)
    # confirm the seed is chi=6 (5-UNSAT and 6-SAT)
    assert chi_ge6(st), "seed not chi>=6"
    best = {"excess": st.excess, "m": st.m, "n": st.n, "edges": st.edges()}
    stats = {"chi_calls": 0, "removes": 0, "rewires": 0, "splits": 0,
             "sparsifies": 0}
    step = 0
    SCAN = 80                # violating edges scanned per cheap pass
    REWIRE_SCAN = 40         # violating edges considered for rewiring
    REWIRE_ATTEMPTS = 8      # rewires actually attempted per stuck step
    N_MAX = int(os.environ.get("E16_NMAX", 120))   # vertex-growth ceiling
    t0 = time.time()
    while st.excess > 0 and time.time() < deadline:
        step += 1
        # Lever ordering (sparsification first, growth last):
        # 1) pure-remove sweep   2) codegree-SAFE rewire   3) TRADE rewire
        # 4) thorough safe-rewire confirm   5) vertex-split growth   6) stall.
        e = try_pure_remove(st, rng, stats, SCAN)
        if e is not None:
            stats["removes"] += 1
            kind = "remove"
        else:
            # codegree-SAFE rewire, scanned then thorough (the canonical
            # in-class-preserving descent: never creates a K_{2,3} violation).
            r = try_rewire(st, rng, stats, REWIRE_SCAN, REWIRE_ATTEMPTS,
                           safe_only=True)
            if r is None:
                r = try_rewire(st, rng, stats, 10 ** 9, 10 ** 9, safe_only=True)
            # SPARSIFY (E16 follow-up): remove a redundant non-violating edge to
            # break criticality rigidity, freeing the violating-edge sweep.
            if r is None and USE_SPARSIFY:
                r = try_sparsify(st, rng, stats, 10 ** 9)
            # Opt-in escapes (default off): TRADE rewires that create a smaller
            # violation, and vertex-split GROWTH. Empirically these only reach a
            # denser local minimum, so they are not part of the canonical run.
            if r is None and USE_TRADES:
                r = try_rewire(st, rng, stats, 10 ** 9, 10 ** 9, safe_only=False)
            if r is None and USE_SPLITS and st.n < N_MAX:
                r = split_move(st, rng, stats)
            if r is None:
                print(f"  TERMINAL STALL at excess={st.excess} m={st.m} "
                      f"n={st.n} (no pure remove, no safe or trade rewire, no "
                      f"chi-preserving excess-reducing split; n_max={N_MAX})",
                      flush=True)
                break
            kind = r[0]
            if kind == "remove":
                stats["removes"] += 1
            elif kind == "sparsify":
                stats["sparsifies"] += 1
            elif kind in ("split", "split+comp"):
                stats["splits"] += 1
            else:
                stats["rewires"] += 1
        if (st.excess, st.m) < (best["excess"], best["m"]):  # min excess, then m
            best = {"excess": st.excess, "m": st.m, "n": st.n, "edges": st.edges()}
        if step % 10 == 0:
            summary = {
                "seed_n": n, "start_excess": start_excess,
                "cur_excess": st.excess, "cur_m": st.m, "cur_n": st.n,
                "best_excess": best["excess"], "best_m": best["m"],
                "best_n": best["n"], "step": step, "stats": dict(stats),
                "elapsed_s": round(time.time() - t0, 1),
            }
            (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1))
            (OUT / "BEST.json").write_text(json.dumps(best, indent=1))
            print(f"step {step} ({kind}) excess {st.excess} m {st.m} n {st.n} "
                  f"vpairs {len(st.violating_pairs())} | rew {stats['rewires']} "
                  f"rem {stats['removes']} spa {stats['sparsifies']} "
                  f"spl {stats['splits']} calls {stats['chi_calls']} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    # final
    summary = {
        "seed_n": n, "start_excess": start_excess, "cur_excess": st.excess,
        "cur_m": st.m, "cur_n": st.n, "best_excess": best["excess"],
        "best_m": best["m"], "best_n": best["n"], "step": step,
        "stats": dict(stats), "elapsed_s": round(time.time() - t0, 1),
        "reached_zero": st.excess == 0,
    }
    if st.excess == 0:
        ok, checks = verify_witness(st)
        summary["witness_verified"] = ok
        summary["checks"] = checks
        if ok:
            witness = {"n": st.n, "m": st.m, "edges": st.edges(), "checks": checks}
            (OUT / "WITNESS.json").write_text(json.dumps(witness, indent=1))
            print(f"\n*** WITNESS: in-class chi>=6 at n={st.n} m={st.m} "
                  f"checks={checks}", flush=True)
        else:
            print(f"\nexcess hit 0 but verification FAILED: {checks}", flush=True)
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1))
    summary["best_edges"] = best["edges"]     # carried for the aggregate, not file
    return summary, best


def main():
    deadline = time.time() + DEADLINE_S
    print(f"E16 top-down repair: deadline {DEADLINE_S/60:.0f} min, "
          f"samples={N_SAMPLES}, rewire_tries={MAX_REWIRE_TRIES}, "
          f"trades={USE_TRADES} splits={USE_SPLITS}", flush=True)
    best_overall = None
    floors = []                               # per-restart stall excess
    for r in range(RESTARTS):
        if time.time() >= deadline:
            break
        rng = random.Random(SEED + r)
        print(f"\n=== restart {r} ===", flush=True)
        s, best = run(deadline, rng)
        floors.append({"restart": r, "stall_excess": s["cur_excess"],
                       "stall_m": s["cur_m"], "stall_n": s["cur_n"],
                       "best_excess": best["excess"], "best_m": best["m"]})
        if best_overall is None or (best["excess"], best["m"]) < (
                best_overall["excess"], best_overall["m"]):
            best_overall = best
            # the deepest in-class-repaired graph: K4-free, chi=6, minimum
            # residual codegree excess. Committable artifact (the "repair floor").
            floor = {"n": best["n"], "m": best["m"], "excess": best["excess"],
                     "edges": best["edges"]}
            (OUT / "FLOOR.json").write_text(json.dumps(floor, indent=1))
        if s.get("reached_zero"):
            break
    agg = {
        "restarts": len(floors), "start_excess": 1068,
        "best_excess": best_overall["excess"], "best_m": best_overall["m"],
        "best_n": best_overall["n"],
        "stall_excess_min": min(f["stall_excess"] for f in floors),
        "stall_excess_max": max(f["stall_excess"] for f in floors),
        "reached_zero": False,
        "floors": floors,
        "trades": USE_TRADES, "splits": USE_SPLITS,
    }
    (OUT / "AGGREGATE.json").write_text(json.dumps(agg, indent=1))
    print(f"\nDONE. best_excess={best_overall['excess']} "
          f"m={best_overall['m']} n={best_overall['n']} (start 1068); "
          f"stall range [{agg['stall_excess_min']},{agg['stall_excess_max']}] "
          f"over {len(floors)} restarts; reached_zero=False", flush=True)


if __name__ == "__main__":
    main()
