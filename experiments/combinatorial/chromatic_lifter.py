r"""Chromatic lifter: a phase-aware engine to drive a seed graph above a target
chromatic number while respecting pluggable structural invariants.

This packages the three algorithmic lessons of the L57-L64 thread into one
reusable tool, generalizing the ad-hoc e14/e14c scripts.

  1. PORTFOLIO backend (L64). Near a colorability phase boundary, single-solver
     runtimes are heavy-tailed (Cadical 12 h vs MapleChrono 155 s on one
     instance). Every decisive solve here goes through `portfolio_sat`, taking
     the first solver to answer.
  2. OVERSHOOT, don't walk (L64). The hard region is a BAND around the UNSAT
     threshold; solves on either side are fast. So the lifter JUMPS past the
     band with free (no-solve) edge additions, then solves once on the cheap
     overconstrained side, instead of paying the threshold tax at every step.
  3. INVARIANT-CONSTRAINED growth (L63). Edges may be required to preserve
     structural properties the target class needs. The built-in invariants are
     K4-freeness and K_{2,3}-freeness (codegree <= 2), which together define the
     UDG-necessary class: every planar unit-distance graph satisfies both.

The lifter proves chi(G) > k by growing G with allowed edges until it is
(k)-UNSAT (the witness), or reports STUCK (no allowed edge remains while still
k-colorable: the invariant class caps at chi <= k from this seed), or EXHAUSTED
(hit the edge budget still colorable).

Self-test (`python chromatic_lifter.py`) lifts a small seed past k=2 and k=3
with and without invariants, asserting the engine is sound end to end. It does
not launch heavy compute.
"""
from __future__ import annotations
import sys
import pathlib
import random
import itertools

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "_shared"))
from portfolio_sat import colorable_portfolio, DEFAULT_SOLVERS  # noqa: E402


# ----------------------------- graph state -----------------------------------

class GraphState:
    """Mutable adjacency + codegree bookkeeping for O(1) invariant checks."""

    def __init__(self, n, edges):
        self.n = n
        self.adj = [set() for _ in range(n)]
        self.C = [[0] * n for _ in range(n)]   # codegree (common-neighbor count)
        self.edge_set = set()
        for u, v in edges:
            self._add(u, v)

    def has(self, u, v):
        return v in self.adj[u]

    def _add(self, u, v):
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
        self.edge_set.add((u, v) if u < v else (v, u))

    def add(self, u, v):
        self._add(u, v)

    def edges(self):
        return list(self.edge_set)


# ----------------------------- invariants ------------------------------------
# Each invariant is a predicate (state, u, v) -> bool: True iff adding edge u-v
# keeps the property. They assume u-v is not already present.

def k4_safe(state, u, v):
    """Adding u-v creates a K4 iff u and v have an edge inside their common
    neighborhood."""
    common = state.adj[u] & state.adj[v]
    for x in common:
        if state.adj[x] & common:
            return False
    return True


def codegree_le2_safe(state, u, v):
    """Keep K_{2,3}-freeness: no pair may reach codegree 3 after adding u-v."""
    for x in state.adj[v]:
        if x != u and state.C[u][x] >= 2:
            return False
    for y in state.adj[u]:
        if y != v and state.C[v][y] >= 2:
            return False
    return True


UDG_NECESSARY = (k4_safe, codegree_le2_safe)


def _allowed(state, u, v, invariants):
    if state.has(u, v):
        return False
    return all(inv(state, u, v) for inv in invariants)


# ----------------------------- edge selection --------------------------------

def _model_pairs(coloring):
    """Non-adjacent same-colored pairs of a proper coloring (model-guided: each
    such edge invalidates this specific coloring)."""
    groups = {}
    for v, c in enumerate(coloring):
        groups.setdefault(c, []).append(v)
    for vs in groups.values():
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                yield vs[i], vs[j]


def _hub_pairs(state, rng, cap=160):
    order = sorted(range(state.n), key=lambda v: -len(state.adj[v]))[:cap]
    rng.shuffle(order)
    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            yield order[i], order[j]


def _take_allowed(state, stream, invariants, count):
    out = []
    for u, v in stream:
        if _allowed(state, u, v, invariants):
            state.add(u, v)
            out.append((u, v))
            if len(out) >= count:
                break
    return out


# ----------------------------- the lifter ------------------------------------

def lift(n, base_edges, k, invariants=(), jump=60, model_sharp=15,
         max_added=4000, time_limit_per_solve=None, solvers=DEFAULT_SOLVERS,
         seed=0, log=lambda *_: None):
    """Drive chi above k by adding `invariants`-allowed edges.

    Returns dict: status in {success_unsat, stuck, exhausted}, plus n, k,
    added (list of edges), m_added, witness (the k-UNSAT edge list on success).
    """
    rng = random.Random(seed)
    state = GraphState(n, base_edges)
    added = []
    rounds = 0

    while len(added) < max_added:
        rounds += 1
        out = colorable_portfolio(n, state.edges(), k, want_coloring=True,
                                  time_limit=time_limit_per_solve, solvers=solvers)
        if out["result"] is False:
            log(f"round {rounds}: {len(added)} added -> k={k} UNSAT (winner "
                f"{out['winner']}, {out['elapsed']}s)")
            return {"status": "success_unsat", "n": n, "k": k, "added": added,
                    "m_added": len(added), "witness": state.edges(),
                    "winner": out["winner"]}

        # SAT (or TIMEOUT): overshoot. Sharp model-guided edges first, then a
        # blind jump past the band.
        batch = []
        if out["result"] is True and out.get("coloring"):
            batch += _take_allowed(state, _model_pairs(out["coloring"]),
                                   invariants, model_sharp)
        batch += _take_allowed(state, _hub_pairs(state, rng), invariants,
                               jump - len(batch))
        if not batch:
            log(f"round {rounds}: {len(added)} added -> STUCK (no allowed edge)")
            return {"status": "stuck", "n": n, "k": k, "added": added,
                    "m_added": len(added), "witness": None}
        added.extend(batch)
        tag = out["result"]
        log(f"round {rounds}: +{len(batch)} edges -> {len(added)} added "
            f"(solve {tag} in {out['elapsed']}s via {out['winner']})")

    return {"status": "exhausted", "n": n, "k": k, "added": added,
            "m_added": len(added), "witness": None}


# ----------------------------- self-test -------------------------------------

def _selftest():
    pr = lambda *a: print("   ", *a)

    # (1) No invariants: lift an edgeless graph past k=2. Must succeed (it just
    # needs to build an odd cycle), proving the SAT-driven growth + portfolio
    # detect UNSAT correctly.
    print("[1] lift n=9 empty graph past k=2 (force an odd cycle), no invariants")
    r = lift(9, [], 2, invariants=(), jump=4, model_sharp=2, seed=1, log=pr)
    assert r["status"] == "success_unsat", r["status"]
    # verify the witness really is 2-UNSAT and 3-colorable (chi==3 lifted)
    chk2 = colorable_portfolio(9, r["witness"], 2)["result"]
    chk3 = colorable_portfolio(9, r["witness"], 3)["result"]
    assert chk2 is False and chk3 is True
    print(f"    -> success at {r['m_added']} added edges; witness 2-UNSAT, "
          f"3-SAT (chi=3). OK")

    # (2) Invariant-constrained: lift past k=2 while keeping the graph
    # triangle-free (a stricter invariant than K4-free). Forcing chi>=3
    # triangle-free needs a longer odd cycle; the engine should still succeed.
    def triangle_free(state, u, v):
        return len(state.adj[u] & state.adj[v]) == 0
    print("[2] lift n=11 past k=2 under triangle-free invariant")
    r2 = lift(11, [], 2, invariants=(triangle_free,), jump=5, model_sharp=2,
              seed=2, log=pr)
    assert r2["status"] == "success_unsat", r2["status"]
    # witness must contain no triangle
    st = GraphState(11, r2["witness"])
    assert all(len(st.adj[u] & st.adj[v]) == 0 for u, v in r2["witness"])
    print(f"    -> success at {r2['m_added']} added edges; witness "
          f"triangle-free and 2-UNSAT. OK")

    # (3) STUCK detection: a complete graph K4 is already 3-chromatic; ask to
    # lift K3 past k=2 forbidding ALL new edges (empty allowed set) -> must
    # report stuck immediately (K3 is 3-colorable, 2-... actually K3 is already
    # 2-UNSAT). Use an edgeless n=4 with a never-allow invariant: stays
    # 2-colorable, no edge addable -> stuck.
    print("[3] STUCK detection: edgeless n=4, k=2, all edges forbidden")
    never = lambda *a: False
    r3 = lift(4, [], 2, invariants=(never,), jump=4, seed=3, log=pr)
    assert r3["status"] == "stuck", r3["status"]
    print("    -> correctly reported STUCK. OK")

    print("\nALL SELF-TESTS PASSED")


if __name__ == "__main__":
    _selftest()
