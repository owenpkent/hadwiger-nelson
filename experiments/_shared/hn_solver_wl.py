r"""hn_solver_wl: watched-literal nogood propagation for k-colorability.

The L66 white-paper's #1 lever, implemented and tuned for PyPy. hn_solver_cdcl
proved that conflict-directed backjumping plus nogood learning REDUCES the search
tree sharply (6.3x fewer nodes on M^3(C5) at max_learn=8), but its wall-time
benefit was eaten by the nogood check: a linear scan of every nogood indexed at
the current (vertex, color), re-run at every node.

This module removes the scan. It keeps the EXACT search skeleton of
hn_solver_cdcl (static clique-first / degree-descending order, the procedural
symmetry ceiling, conflict-set analysis, backjump to the deepest blamer) and
changes one thing: learned nogoods live in a two-watched-literal index, so the
per-node nogood cost drops from "scan all nogoods at (i, c)" to "touch only the
two watched literals of a nogood when a decision falsifies one of them."

Representation matters as much as the algorithm here. Everything is an integer:
a (vertex-position, color) pair is the single literal id  L = p * k + c , so the
watch index is a flat list-of-lists  watch[L] , the forbidden-color reason is a
flat list  reason[L] , and the per-vertex forbidden set is a bitmask. There are
no dict or tuple lookups on the hot path, which is what lets PyPy's JIT compile
the propagation loop to tight machine code (a dict-of-tuples version ran no
faster than the linear scan it replaced).

The literal view. A nogood is a set of literals (p, c) that cannot all hold at
once. A literal is SAT when color[p] == c. A nogood becomes UNIT when all but one
of its literals are SAT; the lone non-SAT literal must then be forbidden. Because
a vertex is only ever assigned by a DECISION (never force-assigned out of static
order), a decision that would complete a nogood was already blocked by that
nogood's unit propagation, so conflicts surface only at decision positions, as in
hn_solver_cdcl.

Soundness on backtrack: watches need no undo (un-assigning a vertex only makes
literals less-SAT, so a watched non-SAT literal stays non-SAT). Only the domain
forbiddings a nogood IMPLIED are undone, via a level-stamped trail; each
forbidding is stamped at the frontier level that triggered it (its deepest
reason), so it is removed exactly when that reason is un-assigned, never later.
Learned nogoods are redundant (implied by the graph and the ceiling), so the base
correctness rests on the graph constraints plus the exhaustive symmetry-broken
search; learning only changes speed. Size-1 learned nogoods are global units,
applied as permanent forbiddings.

Correctness is not assumed. The self-test cross-validates every verdict against
hn_solver (chronological), hn_solver_cdcl, AND the MapleChrono portfolio on
hundreds of random graphs, checks witness validity, and tracks node counts up the
Mycielski tower.
"""
from __future__ import annotations
import sys
import pathlib

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


def kcolor_wl(n, edges, k, node_limit=None, max_learn=64,
              return_coloring=False, return_stats=False):
    """Decide k-colorability via CBJ + watched-literal nogood propagation.

    Returns True/False (or a coloring list if return_coloring and SAT), or None
    if the node budget is exhausted. With return_stats, returns (verdict, stats).

    max_learn caps the SIZE of a stored nogood (0 disables learning, leaving pure
    CBJ). The O(1)-amortized check makes a much larger max_learn affordable than
    in hn_solver_cdcl, so the default is raised accordingly.
    """
    adj = _adj(n, edges)
    stats = {"nodes": 0, "backjumps": 0, "learned": 0, "props": 0}

    def ret(verdict):
        if return_coloring and verdict is True:
            verdict = _coloring
        return (verdict, stats) if return_stats else verdict

    if k <= 0:
        return ret(n == 0)

    clq = _greedy_clique(n, adj)
    if len(clq) > k:
        return ret(False)

    clqset = set(clq)
    rest = sorted((v for v in range(n) if v not in clqset),
                  key=lambda x: -len(adj[x]))
    order = clq + rest
    pos = {v: i for i, v in enumerate(order)}
    nbr_pos = [tuple(sorted(pos[u] for u in adj[order[i]])) for i in range(n)]

    color = [-1] * n            # color[i] = color at position i, or -1
    tried = [0] * n             # bitmask of colors already tried at position i
    conf = [set() for _ in range(n)]
    prefix_max = [-1] * (n + 1)

    # --- watched-literal nogood store (learned nogoods of size >= 2) ----------
    # literal id  L = p * k + c .  color of position p is SAT for L iff color[p]==c
    NL = n * k
    cl_lits = []                # gid -> list of int literals
    cl_w = []                   # gid -> [idx0, idx1] watched positions in cl_lits
    watch = [[] for _ in range(NL)]   # L -> list of gid watching literal L
    forbid = [0] * n            # temporary nogood-forbidden color mask per pos
    pforbid = [0] * n           # permanent (size-1 nogood) forbidden mask
    reason = [-1] * NL          # reason[L] = gid that forbade L (temporary), else -1
    fb_lit = []                 # forbidding trail: literal
    fb_lvl = []                 # forbidding trail: level (frontier when forbidden)

    def _undo_forbids(level):
        while fb_lvl and fb_lvl[-1] >= level:
            L = fb_lit.pop()
            fb_lvl.pop()
            forbid[L // k] &= ~(1 << (L % k))
            reason[L] = -1

    def _do_forbid(L, gid, level):
        p = L // k
        c = L % k
        if (forbid[p] >> c) & 1 or (pforbid[p] >> c) & 1:
            return
        forbid[p] |= (1 << c)
        reason[L] = gid
        fb_lit.append(L)
        fb_lvl.append(level)
        stats["props"] += 1

    def _propagate(dlit, level):
        wl = watch[dlit]
        if not wl:
            return
        keep = []
        for gid in wl:
            lits = cl_lits[gid]
            w = cl_w[gid]
            w0 = w[0]
            w1 = w[1]
            if lits[w0] == dlit:
                wi, other = 0, w1
            elif lits[w1] == dlit:
                wi, other = 1, w0
            else:
                continue                 # stale watch entry, drop it
            rep = -1
            for r in range(len(lits)):
                if r == w0 or r == w1:
                    continue
                L = lits[r]
                if color[L // k] != L % k:    # non-SAT: a valid watch
                    rep = r
                    break
            if rep >= 0:
                w[wi] = rep
                watch[lits[rep]].append(gid)
            else:
                keep.append(gid)
                oL = lits[other]
                if color[oL // k] == -1:
                    _do_forbid(oL, gid, level)
                # color[oL//k]==oL%k: all SAT, redundant nogood violated, the
                #   decision search hits the equivalent graph conflict anyway.
                # else: contra, clause satisfied.
        watch[dlit] = keep

    def _learn(ng_lits, h):
        # ng_lits: literals sorted ascending (== sorted by position, since
        # position dominates color in L = p*k + c); the asserting literal (max
        # position == h) is last. After backjump h is cleared, so the asserting
        # literal is the lone non-SAT one: forbid it at level h.
        if len(ng_lits) == 1:
            L = ng_lits[0]
            pforbid[L // k] |= (1 << (L % k))     # global unit: permanent
            stats["learned"] += 1
            return
        gid = len(cl_lits)
        cl_lits.append(ng_lits)
        ai = len(ng_lits) - 1                      # asserting literal index
        si = len(ng_lits) - 2                      # second-highest position
        cl_w.append([ai, si])
        watch[ng_lits[ai]].append(gid)
        watch[ng_lits[si]].append(gid)
        _do_forbid(ng_lits[ai], gid, h)
        stats["learned"] += 1

    # --- main search ---------------------------------------------------------
    i = 0
    while 0 <= i < n:
        stats["nodes"] += 1
        if node_limit is not None and stats["nodes"] > node_limit:
            return ret(None)

        mu = prefix_max[i]
        ceil = k if mu + 2 > k else mu + 2
        npos = nbr_pos[i]
        blocked = forbid[i] | pforbid[i]
        base = i * k

        chosen = -1
        cc = 0
        while cc < ceil:
            if (tried[i] >> cc) & 1:
                cc += 1
                continue
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
            if (blocked >> cc) & 1:
                gid = reason[base + cc]
                if gid >= 0:                  # temporary nogood: blame members
                    for L in cl_lits[gid]:
                        p = L // k
                        if p != i:
                            conf[i].add(p)
                # permanent (size-1) nogood adds no blamer (global fact)
                tried[i] |= (1 << cc)
                cc += 1
                continue
            chosen = cc
            break

        if chosen >= 0:
            color[i] = chosen
            tried[i] |= (1 << chosen)
            prefix_max[i + 1] = mu if mu > chosen else chosen
            _propagate(base + chosen, i)
            i += 1
        else:
            if not conf[i]:
                return ret(False)
            h = max(conf[i])
            ng = sorted(p * k + color[p] for p in conf[i])
            _undo_forbids(h)
            conf[h] |= (conf[i] - {h})
            stats["backjumps"] += 1
            for j in range(h, i + 1):
                color[j] = -1
            for j in range(h + 1, i + 1):
                tried[j] = 0
                conf[j] = set()
            i = h
            if max_learn > 0 and 1 <= len(ng) <= max_learn:
                _learn(ng, h)

    if i == n:
        _coloring = [0] * n
        for idx in range(n):
            _coloring[order[idx]] = color[idx]
        return ret(True)
    return ret(False)


# --------------------------- self-test ---------------------------------------

def _selftest():
    import random
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import hn_solver
    import hn_solver_cdcl
    from portfolio_sat import colorable_portfolio

    rng_ = random.Random(11)
    print("[1] cross-validate verdict vs hn_solver, hn_solver_cdcl, portfolio")
    disagree = 0
    trials = 300
    for t in range(trials):
        nn = rng_.randint(4, 15)
        p = rng_.uniform(0.2, 0.75)
        edges = [(u, v) for u in range(nn) for v in range(u + 1, nn)
                 if rng_.random() < p]
        for k in (2, 3, 4, 5):
            mine = bool(kcolor_wl(nn, edges, k))
            chrono = bool(hn_solver.kcolor(nn, edges, k))
            cbj = bool(hn_solver_cdcl.kcolor_learn(nn, edges, k))
            if mine != chrono or mine != cbj:
                disagree += 1
                print(f"   DISAGREE n={nn} k={k} wl={mine} chrono={chrono} "
                      f"cbj={cbj} edges={edges}")
            if t % 4 == 0:
                ref = colorable_portfolio(nn, edges, k)["result"]
                if mine != ref:
                    disagree += 1
                    print(f"   DISAGREE(portfolio) n={nn} k={k} wl={mine} "
                          f"ref={ref}")
    print(f"    {trials} graphs x 4 k: {disagree} disagreements")
    assert disagree == 0

    print("[2] witness validity")
    bad = 0
    for t in range(80):
        nn = rng_.randint(5, 14)
        edges = [(u, v) for u in range(nn) for v in range(u + 1, nn)
                 if rng_.random() < 0.4]
        col = kcolor_wl(nn, edges, 4, return_coloring=True)
        if col is not False and col is not None:
            if any(col[u] == col[v] for u, v in edges):
                bad += 1
    print(f"    improper witnesses: {bad}")
    assert bad == 0

    print("[3] node counts vs hn_solver_cdcl up the Mycielski tower")

    def cycle(m):
        return m, [(j, (j + 1) % m) for j in range(m)]

    def myc(nn, e):
        out = list(e)
        for u, v in e:
            out += [(nn + u, v), (nn + v, u)]
        for j in range(nn):
            out.append((nn + j, 2 * nn))
        return 2 * nn + 1, out

    cur = cycle(5)
    levels = {}
    for lvl in range(1, 4):
        cur = myc(*cur)
        levels[lvl] = cur
    names = {1: "M(C5) 11v k=3", 2: "M^2(C5) 23v k=4", 3: "M^3(C5) 47v k=5"}
    ks = {1: 3, 2: 4, 3: 5}
    print(f"    {'instance':22s} {'cbj ml=8':>10s} {'wl ml=8':>10s} "
          f"{'wl ml=64':>10s} {'verdict':>8s}")
    for lvl in (1, 2, 3):
        gn, ge = levels[lvl]
        kk = ks[lvl]
        vc, sc = hn_solver_cdcl.kcolor_learn(gn, ge, kk, max_learn=8,
                                             return_stats=True)
        v8, s8 = kcolor_wl(gn, ge, kk, max_learn=8, return_stats=True)
        v64, s64 = kcolor_wl(gn, ge, kk, max_learn=64, return_stats=True)
        assert bool(vc) == bool(v8) == bool(v64)
        print(f"    {names[lvl]:22s} {sc['nodes']:>10,d} {s8['nodes']:>10,d} "
              f"{s64['nodes']:>10,d} {str(bool(v8)):>8s}")

    print("\nALL SELF-TESTS PASSED")


if __name__ == "__main__":
    _selftest()
