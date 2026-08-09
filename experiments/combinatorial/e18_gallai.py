r"""E18 Stage 2: push 6-CRITICAL structure (Gallai's low-vertex theorem) inside a
SAT encoding of the both-free class, and ask how far up $n$ that kills it.

L75 measured the E17 wall precisely: geng enumeration of the both-free class
saturates at $n = 16$ (66 cpu-h), and $n = 17$ costs $> 80$ cpu-days, so it needs
"either ~100x compute or a qualitatively stronger prune (6-critical / Gallai-tree
structure pushed INSIDE the generator ...)". This module takes the second option,
but puts the structure inside a CDCL search rather than inside geng.

The logic. Any $\chi \ge 6$ member of the class contains a 6-CRITICAL subgraph
which is itself in the class (both class properties are subgraph-closed). So if
for every $n' \le N$ there is no graph on $n'$ vertices satisfying the *necessary
conditions* for being a 6-critical member, then the class has no $\chi \ge 6$
member on $\le N$ vertices. Necessary conditions used here, all of them in NP:

  (C1) $K_4$-free, all codegrees $\le 2$              [class membership]
  (C2) $\delta \ge 5$                                  [6-critical]
  (C3) $m \ge \lceil (28n-18)/10 \rceil$               [Kostochka-Yancey]
  (C4) $\Delta \le (n-1)/2$                            [E17 lemma, from (C1)+(C2)]
  (C5) GALLAI: the subgraph induced by the vertices of degree exactly 5 has every
       block a complete graph or an odd cycle.

(C5) is the new content. Two consequences of it are encoded, both valid only
BECAUSE the class is $K_4$-free (which caps complete blocks at $K_3$):

  (G-cyc) the low subgraph has no $C_4$ (every cycle lies inside one block, and
          $K_1/K_2/K_3$/odd cycles contain no $C_4$);
  (G-loc) for every low vertex $v$, the low subgraph induced on $N(v)$ has max
          degree $\le 1$ (the blocks at $v$ are edge-disjoint and each is $K_2$,
          $K_3$, or an odd cycle, so $v$'s low neighbours pair up at most).

An UNSAT answer is therefore a proof that no 6-critical member exists at that
order. A SAT answer is INCONCLUSIVE (the model meets the necessary conditions but
need not be 6-critical) and its model is emitted as a candidate to $\chi$-test.

Calibration is non-circular by construction: (C5) is instantiated at $k = 4$,
where genuine small $k$-critical graphs exist, and the gate demands that the
encoding ACCEPT them (odd wheel $W_5$, $C_5$, $C_7$, Moser spindle) while
REJECTING a graph whose low subgraph has a $C_4$ and which is not critical (the
cube $Q_3$). If (C5) were mis-stated in the strong direction, the accept half
fails loudly.

Usage:
    python -m experiments.combinatorial.e18_gallai --calibrate
    python -m experiments.combinatorial.e18_gallai --n 15
    python -m experiments.combinatorial.e18_gallai --sweep 13:17 --symbreak
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from pysat.formula import CNF, IDPool                     # noqa: E402
from pysat.solvers import Cadical195                      # noqa: E402

from e17_bothfree_filter import (graph6_to_adj,           # noqa: E402
                                 is_k4_free, is_k23_free)
from e18_sat_class import ClassEncoding, adj_from_edges   # noqa: E402


def ky_floor(n):
    """Kostochka-Yancey: a 6-critical graph has m >= (28n - 18)/10."""
    return math.ceil((28 * n - 18) / 10)


def codegree_ceiling(n):
    """sum_v C(deg v, 2) <= 2*C(n,2) with all codegrees <= 2."""
    return int(n * (1 + math.sqrt(8 * n - 7)) / 4)


class CriticalEncoding(ClassEncoding):
    """The class encoding plus reified degree counters and the Gallai conditions.

    `k` is the criticality target (6 for the real question, 4 for calibration);
    low vertices are those of degree exactly k-1.
    """

    def __init__(self, n, k=6, k4free=True, codeg2=True, gallai_cyc=True,
                 gallai_loc=True, min_edges=None, max_edges=None, maxdeg=None,
                 symbreak=False, symbreak_all=False):
        self.k = k
        self.low_deg = k - 1
        # Build the base class encoding, but suppress its own cardinality-based
        # degree constraints: the reified counter below supplies delta >= k-1 and
        # the low/high indicators from one shared structure.
        self.n = n
        self.pool = IDPool()
        self.cnf = CNF()
        self.e = {}
        for i, j in itertools.combinations(range(n), 2):
            v = self.pool.id(("e", i, j))
            self.e.setdefault(i, {})[j] = v
            self.e.setdefault(j, {})[i] = v
        self.edge_vars = [self.e[i][j] for i, j in itertools.combinations(range(n), 2)]

        if k4free:
            self._k4_free()
        if codeg2:
            self._codegree_le2()

        self.low = {}
        for v in range(n):
            inc = [self.e[v][u] for u in range(n) if u != v]
            ge = self._unary_counter(inc, self.low_deg + 1, tag=("deg", v))
            self.cnf.append([ge[self.low_deg]])               # delta >= k-1
            if maxdeg is not None and maxdeg >= self.low_deg:
                capped = self._unary_counter(inc, maxdeg + 1, tag=("cap", v))
                self.cnf.append([-capped[maxdeg + 1]])        # deg <= maxdeg
            self.low[v] = -ge[self.low_deg + 1]               # deg <= k-1, so == k-1

        if gallai_cyc:
            self._gallai_no_c4()
        if gallai_loc:
            self._gallai_local()
        if min_edges is not None or max_edges is not None:
            self._edge_window(min_edges, max_edges)
        if symbreak or symbreak_all:
            self._lex_leader_adjacent(all_pairs=symbreak_all)

    def _unary_counter(self, lits, kmax, tag):
        """Fully reified sequential counter: returns ge[k] with
        ge[k] <-> (sum(lits) >= k), for k = 0..kmax."""
        m = len(lits)
        TRUE = self.pool.id(("true", tag))
        self.cnf.append([TRUE])
        prev = {0: TRUE}
        for k in range(1, kmax + 1):
            prev[k] = None                                    # sum of 0 lits < k
        for i, x in enumerate(lits, start=1):
            cur = {0: TRUE}
            for k in range(1, kmax + 1):
                s = self.pool.id(("s", tag, i, k))
                p_k, p_km1 = prev[k], prev[k - 1]
                # <- : carry over, or reach k by taking x_i
                if p_k is not None:
                    self.cnf.append([-p_k, s])
                if p_km1 is not None:
                    self.cnf.append([-p_km1, -x, s])
                # -> : if s then (p_k) or (p_{k-1} and x)
                if p_k is None and p_km1 is None:
                    self.cnf.append([-s])
                elif p_k is None:
                    self.cnf.append([-s, p_km1])
                    self.cnf.append([-s, x])
                elif p_km1 is None:
                    self.cnf.append([-s, p_k])
                else:
                    self.cnf.append([-s, p_k, p_km1])
                    self.cnf.append([-s, p_k, x])
                cur[k] = s
            prev = cur
        return prev

    def _gallai_no_c4(self):
        """No 4-cycle among low vertices. Each 4-set carries 3 distinct 4-cycles."""
        for quad in itertools.combinations(range(self.n), 4):
            a, b, c, d = quad
            lows = [-self.low[v] for v in quad]
            for cyc in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
                p, q, r, s = cyc
                self.cnf.append(lows + [-self.var(p, q), -self.var(q, r),
                                        -self.var(r, s), -self.var(s, p)])

    def _gallai_local(self):
        """For a low vertex v, the low subgraph on N(v) has max degree <= 1:
        no low a adjacent to two other low neighbours b, c of v."""
        for v in range(self.n):
            rest = [u for u in range(self.n) if u != v]
            for a in rest:
                for b, c in itertools.combinations([u for u in rest if u != a], 2):
                    self.cnf.append([-self.low[v], -self.low[a], -self.low[b],
                                     -self.low[c],
                                     -self.var(v, a), -self.var(v, b), -self.var(v, c),
                                     -self.var(a, b), -self.var(a, c)])


def decide_critical(n, k=6, use_ky=True, use_maxdeg=True, symbreak=False,
                    gallai=True, budget=None):
    t0 = time.time()
    enc = CriticalEncoding(
        n, k=k,
        gallai_cyc=gallai, gallai_loc=gallai,
        min_edges=ky_floor(n) if use_ky else None,
        max_edges=codegree_ceiling(n) if use_ky else None,
        maxdeg=(n - 1) // 2 if use_maxdeg else None,
        symbreak=symbreak)
    build = time.time() - t0
    t1 = time.time()
    with Cadical195(bootstrap_with=enc.cnf.clauses) as s:
        sat = s.solve()
        model = s.get_model() if sat else None
    out = {
        "n": n, "k": k, "gallai": gallai, "ky": use_ky, "maxdeg_cap": use_maxdeg,
        "symbreak": symbreak, "sat": bool(sat),
        "n_vars": enc.cnf.nv, "n_clauses": len(enc.cnf.clauses),
        "build_s": round(build, 2), "solve_s": round(time.time() - t1, 2),
    }
    if model is not None:
        edges = enc.model_to_edges(model)
        adj = adj_from_edges(n, edges)
        degs = [bin(a).count("1") for a in adj]
        out["candidate"] = {
            "edges": edges, "m": len(edges),
            "mindeg": min(degs), "maxdeg": max(degs),
            "k4_free": is_k4_free(n, adj), "k23_free": is_k23_free(n, adj),
        }
    return out


# ---------------------------------------------------------------- calibration

def _named_graphs():
    """Positive controls (genuinely k-critical) and a negative control."""
    W5 = [(0, i) for i in range(1, 6)] + [(i, i % 5 + 1) for i in range(1, 6)]
    C5 = [(i, (i + 1) % 5) for i in range(5)]
    C7 = [(i, (i + 1) % 7) for i in range(7)]
    # Moser spindle (4-critical, K4-free), standard edge list.
    MOSER = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (0, 4), (0, 5), (4, 5),
             (4, 6), (5, 6), (3, 6)]
    Q3 = []
    for a in range(8):
        for b in range(8):
            if a < b and bin(a ^ b).count("1") == 1:
                Q3.append((a, b))
    return {
        "W5 (odd wheel, 4-critical)":   (6, W5, 4, True),
        "C5 (3-critical)":              (5, C5, 3, True),
        "C7 (3-critical)":              (7, C7, 3, True),
        "Moser spindle (4-critical)":   (7, MOSER, 4, True),
        "Q3 cube (chi=2, low sub has C4)": (8, Q3, 4, False),
    }


def calibrate():
    """The Gallai encoding must accept genuine k-critical graphs and reject the
    negative control. Runs with the class constraints OFF (they are about the
    UDG class, not about criticality) so this tests (C5) alone."""
    rows = []
    for name, (n, edges, k, should_accept) in _named_graphs().items():
        enc = CriticalEncoding(n, k=k, k4free=False, codeg2=False,
                               gallai_cyc=True, gallai_loc=True)
        adj = adj_from_edges(n, edges)
        with Cadical195(bootstrap_with=enc.cnf.clauses) as s:
            accepted = bool(s.solve(assumptions=enc.assumptions_for(adj)))
        ok = accepted == should_accept
        rows.append({"name": name, "n": n, "k": k, "expected": should_accept,
                     "accepted": accepted, "pass": ok})
        print(f"  [{'ok' if ok else 'FAIL'}] {name:34s} k={k} "
              f"expected={'accept' if should_accept else 'reject'} "
              f"got={'accept' if accepted else 'reject'}")
    npass = sum(r["pass"] for r in rows)
    print(f"\ncalibration: {npass}/{len(rows)} "
          f"{'PASS' if npass == len(rows) else 'FAIL'}")
    return rows, npass == len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int)
    ap.add_argument("--sweep", type=str)
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--no-gallai", action="store_true",
                    help="ablation: same instance without the Gallai conditions")
    ap.add_argument("--no-ky", action="store_true")
    ap.add_argument("--symbreak", action="store_true")
    ap.add_argument("--out", type=str)
    args = ap.parse_args()

    if args.calibrate:
        _, ok = calibrate()
        return 0 if ok else 1

    ns = [args.n] if args.n else []
    if args.sweep:
        a, b = [int(x) for x in args.sweep.split(":")]
        ns = list(range(a, b + 1))

    results = []
    for n in ns:
        r = decide_critical(n, k=args.k, use_ky=not args.no_ky,
                            symbreak=args.symbreak, gallai=not args.no_gallai)
        results.append(r)
        verdict = ("SAT: candidate exists (INCONCLUSIVE, chi-test it)" if r["sat"]
                   else "UNSAT: NO 6-critical member at this order")
        print(f"n={n:2d}  {verdict:48s} clauses={r['n_clauses']:9d} "
              f"solve={r['solve_s']:9.2f}s", flush=True)
        if args.out:
            pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(args.out).write_text(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
