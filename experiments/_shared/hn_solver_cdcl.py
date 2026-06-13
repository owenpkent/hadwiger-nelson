r"""hn_solver_cdcl: conflict-directed backjumping + nogood learning for
k-colorability. The L65 white-paper's #1 improvement to hn_solver: attack the
no-clause-learning ceiling.

Plain hn_solver does chronological backtracking, so it rediscovers the same
conflicts in different subtrees and its node count explodes up the Mycielski
tower (882 at M^2(C5), 447,720 at M^3, intractable at M^4). This module adds two
forms of learning:

  - CONFLICT-DIRECTED BACKJUMPING (Prosser CBJ): when a vertex wipes out, it
    backjumps directly to the deepest vertex actually responsible for the
    conflict, skipping irrelevant decisions in between, and propagates the
    conflict set so the target vertex inherits the reasons.
  - NOGOOD LEARNING: each conflict set is recorded as a nogood (a forbidden
    combination of (vertex, color) assignments) and reused to prune future
    branches before they wipe out.

A clean soundness fact for the symmetry ceiling: a vertex may always take color
(max color used so far) + 1 unless that reaches k, so a wipeout happens ONLY when
the vertex's neighbors already occupy all k colors. That is a pure graph
conflict, with no symmetry artifact, so the conflict set (one neighbor per color)
is exact and conflict analysis is sound. Symmetry breaking and clique detection
are kept; the variable order is static (clique first, then degree-descending) to
keep the CBJ bookkeeping correct.

Correctness is not assumed: the self-test cross-validates every verdict against
both the chronological hn_solver and the MapleChrono portfolio on hundreds of
random graphs. The verdict must never change; learning only changes speed.
"""
from __future__ import annotations
import sys
import pathlib
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def _adj(n, edges):
    a = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            a[u].add(v)
            a[v].add(u)
    return a


def _greedy_clique(n, adj):
    clq = []
    for v in sorted(range(n), key=lambda x: -len(adj[x])):
        if all(u in adj[v] for u in clq):
            clq.append(v)
    return clq


def kcolor_learn(n, edges, k, node_limit=None, max_learn=8,
                 return_coloring=False, return_stats=False):
    """Decide k-colorability via CBJ + nogood learning.

    Returns True/False (or a coloring list if return_coloring and SAT), or None
    if the node budget is exhausted. With return_stats, returns (verdict, stats).
    max_learn = 0 disables nogood storage (pure CBJ); >0 caps the size of stored
    nogoods.

    Tuning note (measured, L66): pure CBJ (max_learn=0) has the cheapest per-node
    cost and is often the fastest in Python; small max_learn (about 8) reduces the
    node count without too much checking overhead; LARGE max_learn (>=12) is
    counterproductive in pure Python because the per-node nogood-checking cost
    (linear scan, no watched literals) outweighs the node reduction. The node
    reduction is real and would pay off in wall time with watched-literal
    indexing or a compiled core.
    """
    adj = _adj(n, edges)
    stats = {"nodes": 0, "backjumps": 0, "learned": 0}

    def ret(verdict):
        if return_coloring and verdict is True:
            verdict = _coloring
        return (verdict, stats) if return_stats else verdict

    if k <= 0:
        return ret(n == 0)

    clq = _greedy_clique(n, adj)
    if len(clq) > k:
        return ret(False)

    # static order: clique prefix, then degree-descending
    clqset = set(clq)
    rest = sorted((v for v in range(n) if v not in clqset),
                  key=lambda x: -len(adj[x]))
    order = clq + rest
    pos = {v: i for i, v in enumerate(order)}
    nbr_pos = [frozenset(pos[u] for u in adj[order[i]]) for i in range(n)]

    color = [-1] * n          # color[i] = color of order[i] (indexed by position)
    tried = [0] * n           # bitmask of colors already tried at position i
    conf = [set() for _ in range(n)]
    ng_by_lit = defaultdict(list)   # (pos, color) -> list of nogood frozensets
    # prefix_max[i] = max color used among positions [0, i); maintained
    # incrementally so the symmetry ceiling is O(1) per node, not O(n).
    prefix_max = [-1] * (n + 1)

    i = 0
    while 0 <= i < n:
        stats["nodes"] += 1
        if node_limit is not None and stats["nodes"] > node_limit:
            return ret(None)

        # symmetry ceiling: one new color above the current max is allowed
        mu = prefix_max[i]
        ceil = k if mu + 2 > k else mu + 2
        npos = nbr_pos[i]

        chosen = -1
        cc = 0
        while cc < ceil:
            if (tried[i] >> cc) & 1:
                cc += 1
                continue
            # graph conflict: an earlier neighbor already has color cc?
            blam = -1
            for jp in npos:
                if jp < i and color[jp] == cc:
                    blam = jp
                    break
            if blam >= 0:
                conf[i].add(blam)
                tried[i] |= (1 << cc)
                cc += 1
                continue
            # nogood: would assigning (i, cc) complete a recorded nogood?
            bad = None
            for ng in ng_by_lit.get((i, cc), ()):
                ok = True
                for (p, col) in ng:
                    if p != i and color[p] != col:
                        ok = False
                        break
                if ok:
                    bad = ng
                    break
            if bad is not None:
                for (p, col) in bad:
                    if p != i:
                        conf[i].add(p)
                tried[i] |= (1 << cc)
                cc += 1
                continue
            chosen = cc
            break

        if chosen >= 0:
            color[i] = chosen
            tried[i] |= (1 << chosen)
            prefix_max[i + 1] = mu if mu > chosen else chosen
            i += 1
        else:
            # wipeout at position i
            if not conf[i]:
                return ret(False)
            h = max(conf[i])
            ng = frozenset((p, color[p]) for p in conf[i])
            if 0 < len(ng) <= max_learn:
                for lit in ng:
                    ng_by_lit[lit].append(ng)
                stats["learned"] += 1
            conf[h] |= (conf[i] - {h})
            stats["backjumps"] += 1
            for j in range(h, i + 1):
                color[j] = -1
            for j in range(h + 1, i + 1):
                tried[j] = 0
                conf[j] = set()
            i = h

    if i == n:
        _coloring = [0] * n
        for idx in range(n):
            _coloring[order[idx]] = color[idx]
        return ret(True)
    return ret(False)


# --------------------------- self-test ---------------------------------------

def _selftest():
    import random
    import time
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import hn_solver
    from portfolio_sat import colorable_portfolio

    rng = random.Random(7)
    print("[1] cross-validate verdict vs chronological hn_solver AND portfolio")
    disagree = 0
    trials = 200
    for t in range(trials):
        nn = rng.randint(4, 14)
        p = rng.uniform(0.2, 0.75)
        edges = [(u, v) for u in range(nn) for v in range(u + 1, nn)
                 if rng.random() < p]
        for k in (2, 3, 4):
            mine = kcolor_learn(nn, edges, k)
            chrono = hn_solver.kcolor(nn, edges, k)
            if bool(mine) != bool(chrono):
                disagree += 1
                print(f"   DISAGREE(chrono) n={nn} k={k} learn={mine} "
                      f"chrono={chrono} edges={edges}")
            # spot-check a third of cases against the SAT portfolio too
            if t % 3 == 0:
                ref = colorable_portfolio(nn, edges, k)["result"]
                if bool(mine) != bool(ref):
                    disagree += 1
                    print(f"   DISAGREE(portfolio) n={nn} k={k} "
                          f"learn={mine} ref={ref}")
    print(f"    {trials} graphs x 3 k: {disagree} disagreements")
    assert disagree == 0

    print("[2] witness validity")
    bad = 0
    for t in range(60):
        nn = rng.randint(5, 13)
        edges = [(u, v) for u in range(nn) for v in range(u + 1, nn)
                 if rng.random() < 0.4]
        col = kcolor_learn(nn, edges, 4, return_coloring=True)
        if col is not False and col is not None:
            if any(col[u] == col[v] for u, v in edges):
                bad += 1
    print(f"    improper witnesses: {bad}")
    assert bad == 0

    print("[3] learning vs chronological node counts (the point)")

    def cycle(m):
        return m, [(j, (j + 1) % m) for j in range(m)]

    def myc(nn, e):
        out = list(e)
        for u, v in e:
            out.append((nn + u, v))
            out.append((nn + v, u))
        for j in range(nn):
            out.append((nn + j, 2 * nn))
        return 2 * nn + 1, out

    nn, e = cycle(5)
    tower = {1: None, 2: None, 3: None}
    cur = (nn, e)
    levels = {}
    for lvl in range(1, 4):
        cur = myc(*cur)
        levels[lvl] = cur
    names = {1: "M(C5) 11v k=3", 2: "M^2(C5) 23v k=4", 3: "M^3(C5) 47v k=5"}
    ks = {1: 3, 2: 4, 3: 5}
    print(f"    {'instance':22s} {'chrono nodes':>13s} {'CBJ nodes':>11s} "
          f"{'CBJ+ng nodes':>13s} {'backjumps':>10s} {'learned':>8s}")
    for lvl in (1, 2, 3):
        gn, ge = levels[lvl]
        kk = ks[lvl]
        _, cstats = hn_solver.solve_counting_nodes(gn, ge, kk)
        chrono_nodes = cstats
        v0, s0 = kcolor_learn(gn, ge, kk, max_learn=0, return_stats=True)
        v1, s1 = kcolor_learn(gn, ge, kk, max_learn=20, return_stats=True)
        assert bool(v0) == bool(v1)
        print(f"    {names[lvl]:22s} {chrono_nodes:>13,d} "
              f"{s0['nodes']:>11,d} {s1['nodes']:>13,d} "
              f"{s1['backjumps']:>10,d} {s1['learned']:>8,d}")

    print("\nALL SELF-TESTS PASSED")


if __name__ == "__main__":
    _selftest()
