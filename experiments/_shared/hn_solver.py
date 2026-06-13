r"""hn_solver: a from-scratch k-colorability solver specialized for the
Hadwiger-Nelson program.

This is NOT a competitor to MapleChrono / Cadical on raw speed (a black-box CDCL
solver will win on large instances). Its value is structural: it is built on the
program's own findings and natively exposes structure that a SAT encoding hides.

Design (all implemented from scratch, no SAT backend):
  - COLOR-CLASS SYMMETRY BREAKING. A vertex may introduce color c only if
    c <= 1 + (max color used so far). This collapses the k! color-permutation
    symmetry that a one-hot SAT encoding carries, and makes the search count
    coloring PATTERNS (orbits under color permutation), which is the object the
    "deep liquidity" findings (L57/L62) actually care about.
  - CLIQUE SEEDING. A greedy maximal clique is colored 1..omega up front (forced
    distinct), pinning the symmetry-broken frame and giving an immediate
    omega > k UNSAT certificate.
  - FORWARD CHECKING + MRV. Branch on the uncolored vertex with the fewest
    available colors (minimum remaining values), max-degree tiebreak; detect
    domain wipeout early.
  - COUNTING MODE. count_patterns(n, edges, k, cap) returns the number of proper
    k-colorings up to color permutation, bounded by cap. SAT solvers do not give
    this; it is a direct measure of coloring-space liquidity.

Correctness is established in the self-test by cross-validating every decision
against the portfolio SAT backend on many random graphs, and by cross-validating
the counter against brute force on tiny graphs.
"""
from __future__ import annotations
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


# --------------------------- graph helpers -----------------------------------

def _adj(n, edges):
    a = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            a[u].add(v)
            a[v].add(u)
    return a


def greedy_clique(n, adj):
    """A maximal clique by greedy max-degree extension (cheap, not maximum)."""
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    clique = []
    for v in order:
        if all(u in adj[v] for u in clique):
            clique.append(v)
    return clique


# --------------------------- core search -------------------------------------

class _Search:
    def __init__(self, n, adj, k):
        self.n = n
        self.adj = adj
        self.k = k
        self.color = [-1] * n

    def _neighbor_colors(self, v):
        m = 0
        for u in self.adj[v]:
            c = self.color[u]
            if c >= 0:
                m |= (1 << c)
        return m

    def _pick(self):
        """MRV: uncolored vertex with fewest available colors (within the
        current symmetry ceiling), max-degree tiebreak. Returns (v, avail_mask,
        ceil) or None if all colored. Returns ('DEADEND',) on a wipeout."""
        best = None
        max_used = max(self.color) if any(c >= 0 for c in self.color) else -1
        ceil = min(self.k, max_used + 2)   # colors 0..ceil-1 are placeable
        full = (1 << ceil) - 1
        for v in range(self.n):
            if self.color[v] >= 0:
                continue
            avail = full & ~self._neighbor_colors(v)
            cnt = bin(avail).count("1")
            if cnt == 0:
                return ("DEADEND",)
            deg = len(self.adj[v])
            key = (cnt, -deg)
            if best is None or key < best[0]:
                best = (key, v, avail)
        if best is None:
            return None
        return (best[1], best[2])

    def find_one(self):
        pick = self._pick()
        if pick is None:
            return True
        if pick[0] == "DEADEND":
            return False
        v, avail = pick
        c = 0
        while avail:
            if avail & 1:
                self.color[v] = c
                if self.find_one():
                    return True
                self.color[v] = -1
            avail >>= 1
            c += 1
        return False

    def count(self, cap):
        pick = self._pick()
        if pick is None:
            return 1
        if pick[0] == "DEADEND":
            return 0
        v, avail = pick
        total = 0
        c = 0
        while avail:
            if avail & 1:
                self.color[v] = c
                total += self.count(cap)
                self.color[v] = -1
                if total >= cap:
                    return total
            avail >>= 1
            c += 1
        return total


def _seed_clique(s):
    """Color a greedy clique 1..omega; return False if omega > k (UNSAT)."""
    clq = greedy_clique(s.n, s.adj)
    if len(clq) > s.k:
        return False
    for i, v in enumerate(clq):
        s.color[v] = i
    return True


def kcolor(n, edges, k, return_coloring=False):
    """Decide k-colorability from scratch. Returns a coloring list if
    return_coloring and SAT, else True/False."""
    adj = _adj(n, edges)
    s = _Search(n, adj, k)
    if not _seed_clique(s):
        return False
    ok = s.find_one()
    if not ok:
        return False
    return list(s.color) if return_coloring else True


def count_patterns(n, edges, k, cap=10 ** 9):
    """Number of proper k-colorings up to color permutation (coloring patterns),
    bounded by cap. Symmetry breaking makes each orbit counted once."""
    adj = _adj(n, edges)
    s = _Search(n, adj, k)
    # NOTE: clique-seeding fixes a canonical frame, which is compatible with the
    # symmetry-broken count (it pins the same orbit representative choice).
    if not _seed_clique(s):
        return 0
    return s.count(cap)


# --------------------------- self-test ---------------------------------------

def _brute_patterns(n, edges, k):
    """Reference: count proper k-colorings up to color permutation by brute
    force over canonical (symmetry-broken) assignments. Tiny n only."""
    adj = _adj(n, edges)
    cnt = 0

    def rec(v, maxc):
        nonlocal cnt
        if v == n:
            cnt += 1
            return
        used = {None}
        ceil = min(k, maxc + 2)
        for c in range(ceil):
            if all(adj_c != c for adj_c in (col[u] for u in adj[v] if u < v)):
                col[v] = c
                rec(v + 1, max(maxc, c))
                col[v] = -1
    col = [-1] * n
    rec(0, -1)
    return cnt


def _selftest():
    import random
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from portfolio_sat import colorable_portfolio

    rng = random.Random(2026)
    print("[1] cross-validate decision vs portfolio on random graphs")
    disagree = 0
    trials = 60
    for t in range(trials):
        n = rng.randint(5, 13)
        p = rng.uniform(0.25, 0.7)
        edges = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if rng.random() < p]
        for k in (3, 4):
            mine = kcolor(n, edges, k)
            ref = colorable_portfolio(n, edges, k)["result"]
            if mine != ref:
                disagree += 1
                print(f"   DISAGREE n={n} k={k} mine={mine} ref={ref} edges={edges}")
    print(f"    {trials} graphs x 2 k-values: {disagree} disagreements")
    assert disagree == 0

    print("[2] witness validity (returned colorings are proper)")
    bad = 0
    for t in range(40):
        n = rng.randint(5, 12)
        edges = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if rng.random() < 0.4]
        col = kcolor(n, edges, 4, return_coloring=True)
        if col is not False:
            if any(col[u] == col[v] for u, v in edges):
                bad += 1
    print(f"    improper witnesses: {bad}")
    assert bad == 0

    print("[3] cross-validate pattern counter vs brute force (tiny n)")
    mismatch = 0
    for t in range(30):
        n = rng.randint(3, 7)
        edges = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if rng.random() < 0.5]
        for k in (3, 4):
            mine = count_patterns(n, edges, k)
            ref = _brute_patterns(n, edges, k)
            if mine != ref:
                mismatch += 1
                print(f"   COUNT MISMATCH n={n} k={k} mine={mine} ref={ref}")
    print(f"    pattern-count mismatches: {mismatch}")
    assert mismatch == 0

    print("[4] known value: C5 proper 3-coloring patterns")
    c5 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    pat = count_patterns(5, c5, 3)
    # total proper 3-colorings of C5 = 30; up to color permutation:
    print(f"    C5 3-coloring patterns = {pat} (brute = {_brute_patterns(5, c5, 3)})")
    assert pat == _brute_patterns(5, c5, 3)

    print("\nALL SELF-TESTS PASSED")


if __name__ == "__main__":
    _selftest()
