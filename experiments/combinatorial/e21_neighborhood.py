r"""E21: the local geometry the class was throwing away.

Every pipeline in this program (E17 enumeration, E18/E19 census, E20 decision)
searches the same class: $K_4$-free AND $K_{2,3}$-free. Both are UDG-necessary,
and the second is the codegree wall of L63. But unit-distance geometry says
strictly more about what a NEIGHBORHOOD can look like, and none of it is being
used.

THE ARGUMENT. In a unit-distance graph, $N(v)$ lies on the unit circle centered
at $v$. Two points on that circle are at distance exactly $1$ iff they subtend
exactly $60^\circ$ (chord $2\sin(\Delta\theta/2) = 1$). So write each neighbor as
an angle; edges inside $G[N(v)]$ join angles differing by exactly $60^\circ$.
Three consequences, in increasing strength:

  (N1) Every vertex of $G[N(v)]$ has degree $\le 2$ (only $\theta \pm 60$).
  (N2) A cycle in $G[N(v)]$ is a closed walk of $\pm 60^\circ$ steps, so its
       length $\ell$ satisfies $60(2k - \ell) \equiv 0 \pmod{360}$ for some $k$.
       For odd $\ell$ this is impossible, so NO ODD CYCLE lives inside a
       neighborhood; for $\ell = 4$ it forces a repeated angle. The only cycle
       that survives is $C_6$ (six steps of $+60$).
  (N3) All angles in one component of $G[N(v)]$ are congruent mod $60^\circ$, and
       there are only six residues, so EVERY COMPONENT OF $G[N(v)]$ HAS AT MOST
       SIX VERTICES, and is a path on $\le 6$ vertices or exactly $C_6$.

WHAT IS ACTUALLY NEW. Much of the above is already implied by codegree $\le 2$,
and saying so precisely is the point of this module:

  * (N1) is implied: a vertex $u \in N(v)$ with three neighbors in $N(v)$ gives
    $u$ and $v$ three common neighbors.
  * no $C_3$ in $N(v)$ is exactly $K_4$-freeness; implied.
  * no $C_4$ in $N(v)$ is implied: opposite vertices $a, c$ of that $C_4$ have
    common neighbors $b$, $d$ AND $v$, so codegree $3$.
  * **no $C_5$ in $N(v)$ is NOT implied** -- opposite pairs on a $C_5$ have only
    two common neighbors, so codegree $\le 2$ permits it. This is exactly
    $W_5$-freeness ($W_5 = C_5 + \text{hub}$), and L25 already records that $W_5$
    is not a UDG (regular pentagon of side $1$ has circumradius $\ne 1$). The
    fact was known here; it was never made a constraint on the search.
  * **no $C_7$ (and no longer odd cycle) in $N(v)$ is NOT implied**, same reason.
  * **(N3), the six-vertex component bound, is NOT implied.**

So the class every previous experiment searched is strictly weaker than the
geometry allows, and the gap starts at $W_5$.

THE FALSIFIER, RUN FIRST. The argument above is either right about every
unit-distance graph or it is worthless. `--verify-known` tests it against the
realizable lineage: it loads the known $\chi = 5$ UDGs and checks, for every
vertex of every graph, that $G[N(v)]$ obeys (N1), (N2), (N3). One violation in a
graph with a known embedding refutes the reasoning outright, and no amount of
downstream UNSAT would mean anything. This runs before any constraint is added.

Usage:
    python -m experiments.combinatorial.e21_neighborhood --verify-known
    python -m experiments.combinatorial.e21_neighborhood --independence   # is W5-freeness new?
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                        # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCES = REPO / "sources"
CACHE = HERE / "_cache" / "e21"


# ------------------------------------------------------------------- loading

def load_edge_dimacs(path):
    g = nx.Graph()
    for line in pathlib.Path(path).read_text().splitlines():
        f = line.split()
        if not f:
            continue
        if f[0] == "p":
            g.add_nodes_from(range(1, int(f[2]) + 1))
        elif f[0] == "e":
            g.add_edge(int(f[1]), int(f[2]))
    return g


def known_udgs():
    """Every known chi=5 UDG in sources/ that ships an edge list."""
    out = {}
    for p in sorted(SOURCES.glob("*.edge")):
        out[p.stem] = load_edge_dimacs(p)
    for p in sorted(SOURCES.glob("*.dimacs")):
        if "_sat" in p.stem:            # CNF, not a graph
            continue
        out[p.stem] = load_edge_dimacs(p)
    return out


# --------------------------------------------------- the structural predicate

def neighborhood_report(g):
    """Check (N1), (N2), (N3) on every neighborhood. Returns the worst findings."""
    worst = {"max_nbr_degree": 0, "max_component": 0, "odd_cycles": [],
             "cycles_not_c6": [], "components_over_6": []}
    for v in g.nodes():
        h = g.subgraph(list(g.neighbors(v)))
        if h.number_of_nodes() == 0:
            continue
        worst["max_nbr_degree"] = max(worst["max_nbr_degree"],
                                      max((d for _, d in h.degree()), default=0))
        for comp in nx.connected_components(h):
            worst["max_component"] = max(worst["max_component"], len(comp))
            if len(comp) > 6:
                worst["components_over_6"].append((v, sorted(comp)[:8]))
        for cyc in nx.cycle_basis(h):
            if len(cyc) % 2 == 1:
                worst["odd_cycles"].append((v, cyc))
            if len(cyc) != 6:
                worst["cycles_not_c6"].append((v, len(cyc)))
    return worst


def has_w5(g):
    """A W5 is a C5 inside some neighborhood. Returns a witness or None."""
    for v in g.nodes():
        h = g.subgraph(list(g.neighbors(v)))
        for cyc in nx.simple_cycles(h, length_bound=5) if hasattr(
                nx, "simple_cycles") else []:
            if len(cyc) == 5:
                return (v, cyc)
    return None


def verify_known():
    graphs = known_udgs()
    if not graphs:
        print("no graph files found in sources/", flush=True)
        return False
    ok = True
    print("E21 falsifier: the neighborhood claims, tested on graphs with known "
          "unit-distance embeddings", flush=True)
    for name, g in sorted(graphs.items()):
        r = neighborhood_report(g)
        bad = (r["max_nbr_degree"] > 2 or r["max_component"] > 6
               or r["odd_cycles"] or r["cycles_not_c6"])
        ok &= not bad
        print(f"  [{'ok' if not bad else 'VIOLATION'}] {name}: "
              f"n={g.number_of_nodes()} m={g.number_of_edges()}; "
              f"max degree inside a neighborhood {r['max_nbr_degree']} (claim <=2); "
              f"largest neighborhood component {r['max_component']} (claim <=6); "
              f"odd cycles in a neighborhood {len(r['odd_cycles'])} (claim 0); "
              f"non-C6 cycles {len(r['cycles_not_c6'])} (claim 0)", flush=True)
        if bad:
            print(f"      witness: {r['components_over_6'][:1]} "
                  f"{r['odd_cycles'][:1]} {r['cycles_not_c6'][:1]}", flush=True)
    print(f"falsifier: {'claims SURVIVE on every known UDG' if ok else 'REFUTED'}",
          flush=True)
    return ok


def independence():
    """Show W5-freeness is not implied by K4-free + codegree<=2, by exhibiting a
    graph in the current class that the refined class excludes."""
    w5 = nx.wheel_graph(6)                       # hub + C5
    codeg = max(len(set(w5[u]) & set(w5[v]))
                for u, v in itertools.combinations(w5.nodes(), 2))
    k4 = any(len(c) >= 4 for c in nx.find_cliques(w5))
    print("E21 independence check, on W5 itself:", flush=True)
    print(f"  K4-free: {not k4} (the current class allows it)", flush=True)
    print(f"  max codegree: {codeg} (<=2 required; the current class allows it)",
          flush=True)
    print(f"  in the CURRENT class: {not k4 and codeg <= 2}", flush=True)
    print(f"  is a UDG: False (L25: side-1 regular pentagon has circumradius "
          f"{1 / (2 * 0.5877852522924731):.4f} != 1)", flush=True)
    verdict = (not k4) and codeg <= 2
    print(f"  => W5-freeness is {'NEW content' if verdict else 'already implied'}",
          flush=True)
    return verdict


# ------------------------------------------------------- the refined encoding

def w5_clauses(enc, n):
    """Forbid a C5 inside any neighborhood, by brute force over (hub, 5-cycle).

    Kept for reference and for the encoding comparison: it is correct but costs
    n * C(n-1,5) * 12 clauses of width 10 (576,576 of them at n=16), and measured
    SLOWER than the unrefined class. Use `bipartite_neighborhood_clauses`.
    """
    out = []
    for v in range(n):
        others = [u for u in range(n) if u != v]
        for S in itertools.combinations(others, 5):
            spokes = [-enc.var(v, u) for u in S]
            a = S[0]
            for rest in itertools.permutations(S[1:]):
                if rest[0] > rest[-1]:           # each cycle once, not twice
                    continue
                cyc = (a,) + rest
                rim = [-enc.var(cyc[i], cyc[(i + 1) % 5]) for i in range(5)]
                out.append(spokes + rim)
    return out


def bipartite_neighborhood_clauses(enc, n):
    """Every neighborhood is bipartite: no ODD cycle inside any $G[N(v)]$.

    Strictly stronger than W5-freeness (it kills $C_5$, $C_7$, $C_9$, ... at
    once) and vastly cheaper, because bipartiteness is witnessed rather than
    enumerated: introduce one side-variable $b_{v,u}$ per ordered pair and demand
    that adjacent neighbors of $v$ take opposite sides. Cost is
    $2n\\binom{n-1}{2}$ clauses of width 5, so $4{,}080$ at $n = 17$ against the
    $891{,}072$ the brute-force W5 encoding would need.

    Soundness: in a UDG the angles within one component of $G[N(v)]$ differ by
    multiples of $60^\\circ$, and an odd closed walk of $\\pm 60^\\circ$ steps
    cannot return to its start, so a valid assignment of $b$ exists for every
    unit-distance graph. The auxiliary variables are existentially quantified and
    sit above the edge variables, so SMS's minimality propagator (which permutes
    only edge variables) is unaffected.
    """
    out = []
    for v in range(n):
        b = {u: enc.pool.id(("nbside", v, u)) for u in range(n) if u != v}
        for u, w in itertools.combinations([x for x in range(n) if x != v], 2):
            gate = [-enc.var(v, u), -enc.var(v, w), -enc.var(u, w)]
            out.append(gate + [b[u], b[w]])        # not both on the same side
            out.append(gate + [-b[u], -b[w]])
    return out


def build_refined_cnf(n, m, path, split=None):
    """The both-free cell CNF plus W5-freeness."""
    from e18_gallai import CriticalEncoding
    from e20_sigma2 import _assert_edge_order, _write_dimacs

    enc = CriticalEncoding(n, k=6, k4free=True, codeg2=True,
                           gallai_cyc=False, gallai_loc=False,
                           min_edges=m, max_edges=m, maxdeg=(n - 1) // 2,
                           symbreak=False, symbreak_all=False)
    _assert_edge_order(enc, n)
    base = len(enc.cnf.clauses)
    for cl in bipartite_neighborhood_clauses(enc, n):
        enc.cnf.append(cl)
    units = []
    if split:
        t, idx = [int(x) for x in split.split(":")]
        pairs = list(itertools.combinations(range(n), 2))
        for b, (i, j) in enumerate(pairs[-t:]):
            units.append(enc.var(i, j) if (idx >> b) & 1 else -enc.var(i, j))
    nv, ncl = _write_dimacs(enc.cnf, path, units)
    return nv, ncl, len(enc.cnf.clauses) - base


def decide_refined(n, m, chi=6, timeout=None, quiet=False):
    """Decide one cell of the REFINED class, then verify any model twice over."""
    from e20_sigma2 import run_smsg, verify_model, SAT, UNSAT

    CACHE.mkdir(parents=True, exist_ok=True)
    tag = f"refined_n{n}_m{m}_chi{chi}"
    cnf = CACHE / f"{tag}.cnf"
    nv, ncl, added = build_refined_cnf(n, m, cnf)
    r = run_smsg(n, cnf, chi, connected=True, timeout=timeout,
                 log=CACHE / f"{tag}.log")
    out = {"n": n, "m": m, "chi": chi, "class": "refined (both-free + W5-free)",
           "vars": nv, "clauses": ncl, "refinement_clauses": added,
           "result": r["result"], "elapsed_s": r["elapsed_s"]}
    if r["result"] == SAT and r["models"]:
        v = verify_model(n, r["models"][-1], chi, m=m)
        g = nx.Graph(r["models"][-1])
        v["w5_free"] = has_w5(g) is None
        out["hit"] = v
    (CACHE / f"{tag}.json").write_text(json.dumps(out, indent=2))
    if not quiet:
        print(f"  n={n} m={m}: {r['result']} [{r['elapsed_s']}s, {ncl} clauses "
              f"({added} of them the refinement)]", flush=True)
    return out


def sweep_refined(n, chi=6, timeout=None, jobs=None):
    from e18_gallai import ky_floor, codegree_ceiling
    from e20_sigma2 import SAT, UNSAT
    import concurrent.futures as futures
    import time as _time

    cells = list(range(ky_floor(n), codegree_ceiling(n) + 1))
    jobs = jobs or min(len(cells), 7)
    print(f"E21 refined class, n={n}: cells m={cells[0]}..{cells[-1]}, {jobs} jobs",
          flush=True)
    t0 = _time.time()
    with futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        res = list(ex.map(lambda m: decide_refined(n, m, chi, timeout), cells))
    hits = [r for r in res if r["result"] == SAT]
    unk = [r["m"] for r in res if r["result"] not in (SAT, UNSAT)]
    summary = {"n": n, "chi": chi, "class": "refined", "cells": cells,
               "wall_s": round(_time.time() - t0, 1),
               "cpu_s": round(sum(r["elapsed_s"] for r in res), 1),
               "per_cell": {str(r["m"]): [r["result"], r["elapsed_s"]] for r in res},
               "hits": len(hits), "unknown": unk}
    if not hits and not unk:
        summary["verdict"] = (f"no chi>={chi} member of the refined UDG-necessary "
                              f"class on {n} vertices")
    (CACHE / f"sweep_refined_n{n}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2), flush=True)
    return 2 if hits else (1 if unk else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify-known", action="store_true")
    ap.add_argument("--independence", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--m", type=int)
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--timeout", type=int, default=None)
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if args.independence:
        return 0 if independence() else 1
    if args.verify_known:
        return 0 if verify_known() else 1
    if args.sweep:
        assert args.n, "--sweep needs --n"
        return sweep_refined(args.n, timeout=args.timeout, jobs=args.jobs)
    if args.n and args.m:
        from e20_sigma2 import SAT, UNSAT
        r = decide_refined(args.n, args.m, timeout=args.timeout)
        return {UNSAT: 0, SAT: 2}.get(r["result"], 1)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
