r"""E18 Stage 3: exhaustive SAT enumeration of a both-free cell, as the
INDEPENDENT SECOND ENUMERATOR that L75's caveat (i) asks for.

L75 closes with: "enumeration completeness at $n = 15,16$ rests on geng plus the
verified prune lemmas, no independent second enumerator". Stage 1 showed SAT can
settle EMPTINESS independently; this stage asks for more: enumerate the whole
cell with CDCL + blocking clauses, canonicalise, and compare the resulting set of
isomorphism classes against geng's, graph for graph.

Method: solve, canonicalise the model, block that exact edge assignment, repeat
until UNSAT (cell exhausted) or the model budget runs out. Symmetry breaking
(lex-leader under adjacent transpositions) is sound -- the lex-least labelling of
each isomorphism class survives -- so no class can be lost; it only reduces how
many labelled copies of each class have to be blocked one at a time. Isomorph
rejection is done outside the solver with a Weisfeiler-Lehman hash for bucketing
plus an exact isomorphism test inside each bucket.

The honest cost model this measures: the models-per-class ratio. Enumeration by
blocking is only competitive with canonical augmentation if that ratio stays
small; measuring it is the point of running this at $n = 15$, where geng's answer
(11 classes) is known and the comparison is exact.

Usage:
    python -m experiments.combinatorial.e18_enumerate --n 15 --budget 200000
    python -m experiments.combinatorial.e18_enumerate --n 15 --gallai --compare <g6>
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

import networkx as nx                                       # noqa: E402
from pysat.solvers import Cadical195                        # noqa: E402

from e17_bothfree_filter import graph6_to_adj               # noqa: E402
from e18_gallai import (CriticalEncoding, ky_floor,         # noqa: E402
                        codegree_ceiling)
from e18_sat_class import adj_from_edges                    # noqa: E402


def to_nx(n, edges):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    return g


def gallai_ok(n, edges, low_deg=5):
    """Independent (non-CNF) check of the two Gallai conditions used in the
    encoding, for cross-checking geng's output."""
    g = to_nx(n, edges)
    low = [v for v in g if g.degree(v) == low_deg]
    h = g.subgraph(low)
    for cyc in nx.simple_cycles(h, length_bound=4):
        if len(cyc) == 4:
            return False
    for v in h:
        nb = list(h.neighbors(v))
        sub = h.subgraph(nb)
        if sub.number_of_nodes() and max((d for _, d in sub.degree()), default=0) > 1:
            return False
    return True


class Canon:
    """WL-hash buckets plus exact isomorphism inside a bucket."""

    def __init__(self):
        self.buckets = {}
        self.count = 0

    def add(self, g):
        h = nx.weisfeiler_lehman_graph_hash(g, iterations=4)
        for other in self.buckets.setdefault(h, []):
            if nx.is_isomorphic(g, other):
                return False
        self.buckets[h].append(g)
        self.count += 1
        return True

    def graphs(self):
        for bucket in self.buckets.values():
            yield from bucket


def split_assumptions(enc, n, spec):
    """`spec` is "t:idx": pin the first t vertex pairs in lex order to the bits of
    idx. Every model has definite values on those pairs, so the 2^t branches
    partition the model space exactly -- a sound way to spread one cell over
    cores. Classes straddling branches are merged by the isomorph rejection that
    runs after the branches are collected."""
    t, idx = [int(x) for x in spec.split(":")]
    # Take the LAST t pairs, not the first. The lex-leader symmetry break already
    # pins the low-index rows hard (a split on the first pairs is degenerate: at
    # n=15,m=41 every surviving model landed in a single branch), whereas pairs
    # among the highest-indexed vertices are still free.
    pairs = list(itertools.combinations(range(n), 2))[-t:]
    return [enc.var(i, j) if (idx >> b) & 1 else -enc.var(i, j)
            for b, (i, j) in enumerate(pairs)]


def enumerate_cell(n, gallai=False, budget=200000, require_2conn=True,
                   report_every=20000, m=None, split=None, symbreak_all=False):
    """Enumerate the cell. With `m` set, the edge count is pinned exactly, which
    buys two things: the cells split across cores, and the blocking clause may
    name only the POSITIVE edges. The latter is sound precisely because m is
    fixed -- a distinct graph on the same number of edges cannot contain this
    one's edge set -- and it shortens each blocking clause from C(n,2) to m."""
    lo = hi = m
    if m is None:
        lo, hi = ky_floor(n), codegree_ceiling(n)
    enc = CriticalEncoding(
        n, k=6, gallai_cyc=gallai, gallai_loc=gallai,
        min_edges=lo, max_edges=hi,
        maxdeg=(n - 1) // 2, symbreak=not symbreak_all, symbreak_all=symbreak_all)
    canon = Canon()
    models = 0
    exhausted = False
    t0 = time.time()
    with Cadical195(bootstrap_with=enc.cnf.clauses) as s:
        assume = split_assumptions(enc, n, split) if split else []
        while models < budget:
            if not s.solve(assumptions=assume):
                exhausted = True
                break
            model = s.get_model()
            edges = enc.model_to_edges(model)
            models += 1
            g = to_nx(n, edges)
            if (not require_2conn) or nx.is_biconnected(g):
                canon.add(g)
            if m is None:
                present = set(edges)
                s.add_clause([-enc.var(i, j) if (i, j) in present else enc.var(i, j)
                              for i, j in itertools.combinations(range(n), 2)])
            else:
                s.add_clause([-enc.var(i, j) for i, j in edges])
            if report_every and models % report_every == 0:
                print(f"    {models} models, {canon.count} classes, "
                      f"{time.time() - t0:.0f}s", flush=True)
    return {
        "n": n, "m": m, "split": split, "gallai": gallai, "require_2conn": require_2conn,
        "models": models, "classes": canon.count, "exhausted": exhausted,
        "g6": [nx.to_graph6_bytes(g, header=False).decode().strip()
               for g in canon.graphs()],
        "elapsed_s": round(time.time() - t0, 1),
        "models_per_class": round(models / canon.count, 1) if canon.count else None,
        "_canon": canon,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--gallai", action="store_true")
    ap.add_argument("--budget", type=int, default=200000)
    ap.add_argument("--m", type=int, default=None,
                    help="pin the edge count (splits the cell across cores)")
    ap.add_argument("--split", type=str, default=None,
                    help="t:idx, pin the first t vertex pairs to the bits of idx")
    ap.add_argument("--symbreak-all", action="store_true",
                    help="lex constraints over ALL transpositions, not just adjacent")
    ap.add_argument("--no-2conn", action="store_true")
    ap.add_argument("--compare", type=str, help="a .g6 file of geng's answer")
    ap.add_argument("--out", type=str)
    args = ap.parse_args()

    r = enumerate_cell(args.n, gallai=args.gallai, budget=args.budget,
                       require_2conn=not args.no_2conn, m=args.m, split=args.split,
                       symbreak_all=args.symbreak_all)
    canon = r.pop("_canon")
    status = "EXHAUSTED (cell complete)" if r["exhausted"] else "BUDGET HIT (partial)"
    print(f"n={args.n} m={args.m} split={args.split} gallai={args.gallai}: {r['models']} models -> "
          f"{r['classes']} classes  [{status}]  {r['elapsed_s']}s "
          f"(models/class = {r['models_per_class']})")

    if args.compare:
        lines = [l.strip() for l in pathlib.Path(args.compare).read_text().split()
                 if l.strip()]
        ref = []
        for l in lines:
            nn, adj = graph6_to_adj(l)
            edges = [(i, j) for i, j in itertools.combinations(range(nn), 2)
                     if (adj[i] >> j) & 1]
            g = to_nx(nn, edges)
            if (not args.gallai) or gallai_ok(nn, edges):
                ref.append(g)
        mine = list(canon.graphs())
        matched = 0
        for g in ref:
            if any(nx.is_isomorphic(g, h) for h in mine):
                matched += 1
        agree = (matched == len(ref) == len(mine))
        print(f"compare vs geng: geng={len(ref)} classes (after gallai filter="
              f"{args.gallai}), SAT={len(mine)}, matched={matched} -> "
              f"{'AGREE' if agree else 'DISAGREE'}")
        r["compare"] = {"geng_classes": len(ref), "sat_classes": len(mine),
                        "matched": matched, "agree": agree}

    if args.out:
        pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.out).write_text(json.dumps(r, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
