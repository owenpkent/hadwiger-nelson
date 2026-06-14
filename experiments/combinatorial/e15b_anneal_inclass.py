r"""E15b: simulated-annealing search for a SMALL graph in the UDG-necessary class
(K4-free AND K_{2,3}-free) with chromatic number >= 6 -- the paper's "target
object."

E15 showed GREEDY in-class growth from empty caps at chi=4 (it gets STUCK: no
codegree-safe edge addable while still 5-colorable). The fix is a real LOCAL
SEARCH that can both ADD and REMOVE edges, escaping the greedy trap by rewiring.

Design (pure Python, runs under PyPy at ~5x; imports only hn_solver):
  - State: a graph kept K4-free AND K_{2,3}-free as a HARD invariant. Adds are
    checked (k4_safe + codeg_safe); removes are always safe (cannot create K4 or
    K_{2,3}).
  - Objective (lexicographic, minimized): (capped 5-coloring PATTERN count,
    -edges). The pattern count is hn_solver's count_patterns, the unique
    capability that makes this search possible: it reaches 0 exactly when the
    graph is 5-UNSAT, i.e. chi >= 6 = WITNESS. When the count is saturated at the
    cap (very colorable, flat region), the -edges tiebreak supplies a gradient
    (prefer denser), and moves are biased toward adds to climb out of the flat
    region toward chi >= 6.
  - Metropolis acceptance with a cooling schedule; many restarts; an n sweep.
  - Any chi >= 6 witness is verified (K4-free, K_{2,3}-free, 5-UNSAT, 6-SAT) with
    hn_solver and saved; a portfolio cross-check is a CPython post-step.

Checkpointed and deadline-bounded for unattended overnight runs. A positive
result is a new object; a strong negative ("best reached chi=5 in-class at n=X
over N restarts") sharpens the paper's target-object discussion.
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
import hn_solver  # noqa: E402  (pure Python, PyPy-safe)

OUT = HERE / "_cache" / "e15b_anneal"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20260613
N_RANGE = list(range(26, 41))     # both-free window opens ~26 (Folkman-floor density)
CAP = 80                          # pattern-count cap (cheaper; the near-goal
                                  # gradient below it is what matters)
RESTART_STEPS = 5000              # annealing steps per restart
T0 = 6.0
COOL = 0.9985
DEADLINE_S = float(os.environ.get("E15B_DEADLINE_S", 28800))   # 8 h default


# ---------------- both-free graph state (self-contained, no pysat) -----------

class State:
    def __init__(self, n):
        self.n = n
        self.adj = [set() for _ in range(n)]
        self.C = [[0] * n for _ in range(n)]
        self.m = 0

    def has(self, u, v):
        return v in self.adj[u]

    def add(self, u, v):
        for x in self.adj[v]:
            if x != u:
                self.C[u][x] += 1
                self.C[x][u] += 1
        for y in self.adj[u]:
            if y != v:
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
                self.C[u][x] -= 1
                self.C[x][u] -= 1
        for y in self.adj[u]:
            if y != v:
                self.C[v][y] -= 1
                self.C[y][v] -= 1
        self.m -= 1

    def add_safe(self, u, v):
        """K4-safe (no edge inside common neighborhood) AND codegree-safe (no
        pair reaches codegree 3)."""
        if v in self.adj[u]:
            return False
        common = self.adj[u] & self.adj[v]
        for x in common:           # K4: an edge within the common neighborhood
            if self.adj[x] & common:
                return False
        for x in self.adj[v]:      # codegree: u-x would reach 3
            if x != u and self.C[u][x] >= 2:
                return False
        for y in self.adj[u]:
            if y != v and self.C[v][y] >= 2:
                return False
        return True

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
    for u in range(st.n):
        for v in range(u + 1, st.n):
            if st.C[u][v] >= 3:
                return False
    return True


# ---------------- objective + annealing --------------------------------------

def capped_count(st):
    return hn_solver.count_patterns(st.n, st.edges(), 5, cap=CAP)


def score_scalar(cnt, m):
    # lexicographic (cnt, -m) flattened: fewer colorings dominates, then denser
    return cnt * 100000 - m


def random_safe_add(st, rng, tries=60):
    for _ in range(tries):
        u = rng.randrange(st.n)
        v = rng.randrange(st.n)
        if u != v and st.add_safe(u, v):
            return (min(u, v), max(u, v))
    # fall back to a scan from a random offset: find a safe add if one exists
    off = rng.randrange(st.n)
    for du in range(st.n):
        u = (off + du) % st.n
        for v in range(u + 1, st.n):
            if st.add_safe(u, v):
                return (u, v)
    return None


def chromatic_of(st, kmax=6):
    """Smallest k in 2..kmax that colors st; kmax+ if none (i.e. chi > kmax)."""
    edges = st.edges()
    for k in range(2, kmax + 1):
        if hn_solver.kcolor(st.n, edges, k):
            return k
    return kmax + 1


def anneal_restart(n, rng, deadline, best_holder):
    st = State(n)
    # seed: a few random safe edges to start non-empty
    for _ in range(n):
        e = random_safe_add(st, rng)
        if e:
            st.add(*e)
    cnt = capped_count(st)
    cur = score_scalar(cnt, st.m)
    T = T0
    for step in range(RESTART_STEPS):
        if time.time() > deadline:
            break
        # bias toward adds when saturated at the cap (flat region) to densify
        add_bias = 0.8 if cnt >= CAP else 0.5
        do_add = rng.random() < add_bias
        move = None
        if do_add:
            e = random_safe_add(st, rng)
            if e:
                st.add(*e)
                move = ("add", e)
        if move is None and st.m > 0:
            e = rng.choice(st.edges())
            st.remove(*e)
            move = ("remove", e)
        if move is None:
            continue
        ncnt = capped_count(st)
        new = score_scalar(ncnt, st.m)
        if new <= cur or rng.random() < pow(2.718281828, -(new - cur) / max(T, 1e-6)):
            cur, cnt = new, ncnt
            if ncnt < best_holder["cnt"] or (ncnt == best_holder["cnt"] and st.m > best_holder["m"]):
                best_holder["cnt"] = ncnt
                best_holder["m"] = st.m
                best_holder["n"] = n
                best_holder["edges"] = st.edges()
            if ncnt == 0:
                return st          # chi >= 6 candidate
        else:
            # undo
            kind, e = move
            if kind == "add":
                st.remove(*e)
            else:
                st.add(*e)
            cnt = capped_count(st) if False else cnt   # cnt unchanged on undo
        T *= COOL
    return None


def verify_witness(st):
    edges = st.edges()
    checks = {
        "k4_free": k4_free(st),
        "k23_free": k23_free(st),
        "hn_5_unsat": hn_solver.kcolor(st.n, edges, 5) is False,
        "hn_6_sat": hn_solver.kcolor(st.n, edges, 6) is True,
    }
    return all(checks.values()), checks


def main():
    rng = random.Random(SEED)
    deadline = time.time() + DEADLINE_S
    best = {n: {"cnt": 10 ** 9, "m": 0, "n": n, "edges": []} for n in N_RANGE}
    restarts = {n: 0 for n in N_RANGE}
    witness = None
    rounds = 0
    print(f"E15b annealing: n in {N_RANGE[0]}..{N_RANGE[-1]}, cap={CAP}, "
          f"deadline {DEADLINE_S/3600:.1f}h", flush=True)
    while time.time() < deadline and witness is None:
        rounds += 1
        for n in N_RANGE:
            if time.time() > deadline:
                break
            restarts[n] += 1
            st = anneal_restart(n, rng, deadline, best[n])
            if st is not None:
                ok, checks = verify_witness(st)
                if ok:
                    witness = {"n": st.n, "m": st.m, "edges": st.edges(),
                               "checks": checks}
                    (OUT / "WITNESS.json").write_text(json.dumps(witness, indent=1))
                    print(f"*** WITNESS n={st.n} m={st.m} -- in-class chi>=6! "
                          f"checks={checks}", flush=True)
                    break
                else:
                    print(f"  n={n}: count hit 0 but verify failed {checks}",
                          flush=True)
        # track the chromatic number of the best graph found per n (the
        # informative quantity: does any in-class graph reach chi >= 6?)
        for n in N_RANGE:
            if best[n]["edges"]:
                stb = State(n)
                for (u, v) in best[n]["edges"]:
                    stb.add(u, v)
                best[n]["chi"] = chromatic_of(stb)
            else:
                best[n]["chi"] = 0
        summary = {
            "rounds": rounds, "restarts": restarts,
            "best_per_n": {n: {"cnt": best[n]["cnt"], "m": best[n]["m"],
                               "chi": best[n].get("chi", 0)} for n in N_RANGE},
            "max_chi_seen": max((best[n].get("chi", 0) for n in N_RANGE), default=0),
            "witness": witness is not None,
            "elapsed_s": round(time.time() - time_start, 1),
        }
        (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1))
        (OUT / "BEST.json").write_text(json.dumps(
            {n: {"cnt": best[n]["cnt"], "m": best[n]["m"],
                 "chi": best[n].get("chi", 0), "edges": best[n]["edges"]}
             for n in N_RANGE}, indent=1))
        bestline = " ".join(f"{n}:chi{best[n].get('chi',0)}/m{best[n]['m']}/c{best[n]['cnt']}"
                            for n in N_RANGE)
        print(f"round {rounds} (t={time.time()-time_start:.0f}s) "
              f"max_chi={summary['max_chi_seen']} | {bestline}", flush=True)

    if witness:
        print(f"\nFOUND in-class chi>=6 witness: n={witness['n']} m={witness['m']}",
              flush=True)
    else:
        bn = min(N_RANGE, key=lambda n: best[n]["cnt"])
        print(f"\nno witness in {DEADLINE_S/3600:.1f}h; closest: n={bn} "
              f"min pattern-count={best[bn]['cnt']} (0 would be chi>=6)", flush=True)
    print(f"done; {sum(restarts.values())} restarts total", flush=True)


time_start = time.time()
if __name__ == "__main__":
    main()
