r"""E18: a SAT decision procedure for EXISTENCE in the both-free class, built to
be independent of nauty/geng.

Why this exists. L75 (E17) closed the both-free class ($K_4$-free AND
$K_{2,3}$-free, the UDG-necessary class) for $n \le 16$ by exhaustive canonical
augmentation, and carries an explicit caveat: "enumeration completeness at
$n = 15,16$ rests on geng plus the verified prune lemmas, no independent second
enumerator". This module attacks the half of that caveat which is attackable.

The scoping fact, stated up front because it decides what SAT can and cannot do
here:

  * "the class is EMPTY at order $n$" is an $\exists$-statement over the
    $\binom{n}{2}$ edge variables, so it is in NP, and a SAT UNSAT answer (with a
    DRAT proof) is a complete and independent proof of it;
  * "every class member at order $n$ is 5-colorable" is $\exists\forall$, i.e.
    $\Sigma_2^p$, and is NOT SAT-encodable. That half stays geng's job.

So this settles the emptiness half by a different technology (CDCL over an edge
incidence encoding) rather than by a second canonical-augmentation program.

The encoding is deliberately a RELAXATION of what E17 enumerated. E17 searched
`geng_hn -C -d5 -D[(n-1)/2]` over the per-$n$ edge window [Kostochka-Yancey floor,
codegree ceiling]. Here the default instance drops connectivity, drops the degree
cap, and drops the edge window, keeping only

    (1) $K_4$-free,
    (2) codegree $\le 2$ (equivalently $K_{2,3}$-subgraph-free),
    (3) $\delta \ge 5$,

all three of which every 6-critical member of the class must satisfy. Dropping
constraints can only make the instance easier to satisfy, so UNSAT on this
relaxation is a strictly stronger statement than emptiness of E17's window, and
in particular it is independent of Kostochka-Yancey: it also covers the edge
counts BELOW the KY floor, which E17 never enumerated.

Soundness contract (see NIGHT_PLAN_2026-08-08.md):

  * `--replay G6` fixes every edge variable to a known graph and re-solves; the
    encoding must accept every genuine class member (this is the relaxation
    check, and it fails loudly if a clause is too strong);
  * every model produced is re-verified by `e17_bothfree_filter.py`, which is
    disjoint code from this encoder;
  * `--no-symbreak` (the default for a claimed UNSAT) uses no symmetry breaking
    at all, so the UNSAT answer needs no soundness argument about the symmetry
    break. `--symbreak` adds lex-leader constraints under adjacent transpositions
    (sound: the lex-least member of each isomorphism orbit satisfies them) and is
    for speed only.

Usage:
    python -m experiments.combinatorial.e18_sat_class --n 13
    python -m experiments.combinatorial.e18_sat_class --n 14 --proof out.drat
    python -m experiments.combinatorial.e18_sat_class --n 15 --model
    python -m experiments.combinatorial.e18_sat_class --sweep 9:15
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from pysat.card import CardEnc, EncType                    # noqa: E402
from pysat.formula import CNF, IDPool                      # noqa: E402
from pysat.solvers import Cadical195, Glucose42, Minisat22  # noqa: E402

from e17_bothfree_filter import (graph6_to_adj,            # noqa: E402
                                 is_k4_free, is_k23_free)

CACHE = pathlib.Path(__file__).resolve().parent / "_cache" / "e18"


class ClassEncoding:
    """CNF for "there is a graph on n vertices that is K4-free, has all codegrees
    <= 2, and has min degree >= mindeg", plus optional degree cap / edge window.

    The edge variable for the pair (i, j), i < j, is `self.e[i][j]`.
    """

    def __init__(self, n, mindeg=5, maxdeg=None, min_edges=None, max_edges=None,
                 symbreak=False, symbreak_all=False):
        self.n = n
        self.mindeg = mindeg
        self.pool = IDPool()
        self.cnf = CNF()
        self.e = {}
        for i, j in itertools.combinations(range(n), 2):
            v = self.pool.id(("e", i, j))
            self.e.setdefault(i, {})[j] = v
            self.e.setdefault(j, {})[i] = v
        self.edge_vars = [self.e[i][j] for i, j in itertools.combinations(range(n), 2)]

        self._k4_free()
        self._codegree_le2()
        self._degrees(mindeg, maxdeg)
        if min_edges is not None or max_edges is not None:
            self._edge_window(min_edges, max_edges)
        if symbreak or symbreak_all:
            self._lex_leader_adjacent(all_pairs=symbreak_all)

    def var(self, i, j):
        return self.e[i][j]

    def _k4_free(self):
        """No 4-set spans all 6 edges."""
        for quad in itertools.combinations(range(self.n), 4):
            self.cnf.append([-self.var(a, b) for a, b in itertools.combinations(quad, 2)])

    def _codegree_le2(self):
        """No two vertices share three common neighbours (= no K_{2,3} subgraph).

        This is the Euclidean content of the class: two distinct unit circles meet
        in at most two points, so a unit-distance graph in R^2 has codegree <= 2.
        """
        verts = range(self.n)
        for a, b in itertools.combinations(verts, 2):
            rest = [c for c in verts if c != a and c != b]
            for c, d, f in itertools.combinations(rest, 3):
                self.cnf.append([-self.var(a, c), -self.var(a, d), -self.var(a, f),
                                 -self.var(b, c), -self.var(b, d), -self.var(b, f)])

    def _card(self, lits, bound, kind):
        enc = (CardEnc.atleast if kind == "atleast" else CardEnc.atmost)(
            lits=lits, bound=bound, vpool=self.pool, encoding=EncType.seqcounter)
        self.cnf.extend(enc.clauses)

    def _degrees(self, mindeg, maxdeg):
        for v in range(self.n):
            inc = [self.e[v][u] for u in range(self.n) if u != v]
            if mindeg:
                self._card(inc, mindeg, "atleast")
            if maxdeg is not None:
                self._card(inc, maxdeg, "atmost")

    def _edge_window(self, lo, hi):
        if lo is not None:
            self._card(self.edge_vars, lo, "atleast")
        if hi is not None:
            self._card(self.edge_vars, hi, "atmost")

    def _lex_leader_adjacent(self, all_pairs=False):
        """Sound (speed-only) symmetry break: for a transposition (p, q), require
        row p to be lex <= row q on the coordinates the swap moves. The lex-least
        labelling of any isomorphism class satisfies every such constraint, so no
        class is lost and UNSAT is preserved.

        `all_pairs` ranges over every p < q rather than only adjacent ones. Both
        are sound; the full version leaves far fewer labelled copies of each class
        for an enumeration to have to block one at a time, which is the dominant
        cost in `e18_enumerate`.
        """
        n = self.n
        pairs = (itertools.combinations(range(n), 2) if all_pairs
                 else ((p, p + 1) for p in range(n - 1)))
        for p, q in pairs:
            others = [u for u in range(n) if u not in (p, q)]
            # Lexicographic comparison of (row_p) vs (row_q) restricted to
            # `others`, implemented with the standard chain of "equal so far" vars.
            prev_eq = None
            for idx, u in enumerate(others):
                a, b = self.e[p][u], self.e[q][u]
                if prev_eq is None:
                    self.cnf.append([-a, b])          # a <= b
                    eq = self.pool.id(("eq", p, q, idx))
                    self.cnf.append([-eq, -a, b])
                    self.cnf.append([-eq, a, -b])
                    self.cnf.append([eq, a, b])
                    self.cnf.append([eq, -a, -b])
                else:
                    self.cnf.append([-prev_eq, -a, b])
                    eq = self.pool.id(("eq", p, q, idx))
                    self.cnf.append([-eq, prev_eq])
                    self.cnf.append([-eq, -a, b])
                    self.cnf.append([-eq, a, -b])
                    self.cnf.append([eq, -prev_eq, a, b])
                    self.cnf.append([eq, -prev_eq, -a, -b])
                prev_eq = eq

    def model_to_edges(self, model):
        pos = {abs(l) for l in model if l > 0}
        return [(i, j) for i, j in itertools.combinations(range(self.n), 2)
                if self.var(i, j) in pos]

    def assumptions_for(self, adj):
        """Assumption literals pinning every edge variable to a given graph."""
        out = []
        for i, j in itertools.combinations(range(self.n), 2):
            v = self.var(i, j)
            out.append(v if (adj[i] >> j) & 1 else -v)
        return out


def adj_from_edges(n, edges):
    adj = [0] * n
    for i, j in edges:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return adj


def verify_model_independently(n, edges, mindeg):
    """Re-check a SAT model with the disjoint-code E17 filter."""
    adj = adj_from_edges(n, edges)
    degs = [bin(a).count("1") for a in adj]
    return {
        "k4_free": is_k4_free(n, adj),
        "k23_free": is_k23_free(n, adj),
        "mindeg_ok": min(degs) >= mindeg,
        "mindeg": min(degs),
        "maxdeg": max(degs),
        "edges": len(edges),
    }


def decide(n, mindeg=5, maxdeg=None, min_edges=None, max_edges=None,
           symbreak=False, proof=None, want_model=False, solver="Cadical195"):
    t0 = time.time()
    enc = ClassEncoding(n, mindeg, maxdeg, min_edges, max_edges, symbreak)
    build = time.time() - t0

    cls = {"Cadical195": Cadical195, "Glucose42": Glucose42, "Minisat22": Minisat22}[solver]
    kwargs = {"bootstrap_with": enc.cnf.clauses}
    if proof and solver == "Cadical195":
        kwargs["with_proof"] = True
    t1 = time.time()
    with cls(**kwargs) as s:
        sat = s.solve()
        model = s.get_model() if (sat and want_model) else None
        prooflines = s.get_proof() if (proof and not sat and solver == "Cadical195") else None
    elapsed = time.time() - t1

    out = {
        "n": n, "mindeg": mindeg, "maxdeg": maxdeg,
        "min_edges": min_edges, "max_edges": max_edges,
        "symbreak": symbreak, "solver": solver,
        "sat": bool(sat),
        "n_vars": enc.cnf.nv, "n_clauses": len(enc.cnf.clauses),
        "build_s": round(build, 2), "solve_s": round(elapsed, 2),
    }
    if model is not None:
        edges = enc.model_to_edges(model)
        out["model_edges"] = edges
        out["independent_check"] = verify_model_independently(n, edges, mindeg)
    if prooflines is not None:
        pathlib.Path(proof).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(proof).write_text("\n".join(prooflines) + "\n")
        out["proof_path"] = str(proof)
        out["proof_lines"] = len(prooflines)
    return out


def replay(g6, mindeg=5):
    """Relaxation gate: a known class member must SATISFY the encoding."""
    n, adj = graph6_to_adj(g6.strip())
    enc = ClassEncoding(n, mindeg=mindeg)
    with Cadical195(bootstrap_with=enc.cnf.clauses) as s:
        ok = s.solve(assumptions=enc.assumptions_for(adj))
    degs = [bin(a).count("1") for a in adj]
    return {
        "g6": g6.strip(), "n": n, "accepted": bool(ok),
        "mindeg": min(degs), "maxdeg": max(degs),
        "edges": sum(degs) // 2,
        "truly_in_class": is_k4_free(n, adj) and is_k23_free(n, adj) and min(degs) >= mindeg,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int)
    ap.add_argument("--sweep", type=str, help="a:b, decide every n in [a,b]")
    ap.add_argument("--mindeg", type=int, default=5)
    ap.add_argument("--maxdeg", type=int, default=None)
    ap.add_argument("--min-edges", type=int, default=None)
    ap.add_argument("--max-edges", type=int, default=None)
    ap.add_argument("--symbreak", action="store_true")
    ap.add_argument("--model", action="store_true")
    ap.add_argument("--proof", type=str, default=None)
    ap.add_argument("--solver", default="Cadical195")
    ap.add_argument("--replay", type=str, help="graph6 string or path to a .g6 file")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    if args.replay:
        p = pathlib.Path(args.replay)
        lines = p.read_text().split() if p.exists() else [args.replay]
        results = [replay(l, args.mindeg) for l in lines if l.strip()]
        bad = [r for r in results if r["truly_in_class"] and not r["accepted"]]
        for r in results:
            print(f"  n={r['n']:2d} m={r['edges']:3d} deg[{r['mindeg']},{r['maxdeg']}] "
                  f"in-class={r['truly_in_class']} accepted={r['accepted']}")
        print(f"\nreplay gate: {len(results) - len(bad)}/{len(results)} accepted; "
              f"{'PASS' if not bad else 'FAIL (encoding is not a relaxation)'}")
        return 1 if bad else 0

    ns = ([args.n] if args.n else
          list(range(*[int(x) for x in args.sweep.split(":")])) if args.sweep else [])
    if args.sweep:
        a, b = [int(x) for x in args.sweep.split(":")]
        ns = list(range(a, b + 1))

    results = []
    for n in ns:
        r = decide(n, args.mindeg, args.maxdeg, args.min_edges, args.max_edges,
                   args.symbreak, args.proof, args.model or True, args.solver)
        results.append(r)
        verdict = "SAT (class nonempty)" if r["sat"] else "UNSAT (class EMPTY)"
        print(f"n={n:2d}  {verdict:22s}  vars={r['n_vars']:6d} clauses={r['n_clauses']:7d} "
              f"solve={r['solve_s']:8.2f}s", flush=True)
        if r.get("independent_check"):
            c = r["independent_check"]
            print(f"        independent filter: K4-free={c['k4_free']} "
                  f"K23-free={c['k23_free']} deg[{c['mindeg']},{c['maxdeg']}] m={c['edges']}")
    if args.out:
        pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.out).write_text(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
