r"""Benchmark suite for hn_solver, the from-scratch k-colorability solver.

Goal: surface HONESTLY where hn_solver wins and where it breaks, against the
MapleChrono CDCL backend, on instances chosen to exercise its structural
features and its missing ones.

Each instance is benched at its two hardest k values: k = chi - 1 (UNSAT) and
k = chi (SAT). For every (instance, k) we record:
  - the verdict from hn_solver (SAT / UNSAT / BUDGET if the node limit is hit)
    and the number of search-tree nodes it expanded,
  - the verdict and wall time from MapleChrono (in-process pysat),
  - hn_solver wall time,
  - AGREEMENT (a disagreement would be a correctness bug; the bench doubles as a
    cross-validation).

Instance families:
  - complete graphs K6,K7,K8: clique-seeding should make these trivial,
  - a 7-vertex unit-distance graph (Moser spindle): small, has triangles,
  - Mycielskians M(C5)=Grotzsch, M^2(C5), M^3(C5): TRIANGLE-FREE (max clique 2),
    so clique-seeding gives nothing; the symmetry breaking is the only aid, and
    these are the stress test,
  - random G(n,p) at growing n: the scaling curve,
  - a lineage graph P510: the scale at which a pure-Python tree search must lose
    to a learning CDCL solver.

Writes a markdown results table to hn_solver_bench_results.md.
"""
from __future__ import annotations
import sys
import pathlib
import time
import random

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hn_solver  # noqa: E402
from portfolio_sat import build_color_cnf  # noqa: E402
from pysat.solvers import MapleChrono  # noqa: E402

REPO = HERE.parent.parent
VTX = REPO / "sources" / "cnp-sat" / "vtx"
EDGE = REPO / "sources" / "cnp-sat" / "edge"
OUT = HERE / "hn_solver_bench_results.md"

NODE_LIMIT = 1_500_000
MAPLE_CONF_BUDGET = 200_000_000   # keep the bench from hanging on a hard UNSAT


# --------------------------- instance builders -------------------------------

def complete(nv):
    return nv, [(u, v) for u in range(nv) for v in range(u + 1, nv)]


def moser_spindle():
    # A standard 7-vertex unit-distance graph with chi = 4 (two rhombi).
    e = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3),
         (0, 4), (0, 5), (4, 5), (4, 6), (5, 6), (3, 6)]
    return 7, e


def cycle(k):
    return k, [(i, (i + 1) % k) for i in range(k)]


def mycielski(n, edges):
    out = list(edges)
    for u, v in edges:
        out.append((n + u, v))
        out.append((n + v, u))
    for i in range(n):
        out.append((n + i, 2 * n))
    return 2 * n + 1, out


def myc_tower(levels):
    n, e = cycle(5)
    for _ in range(levels):
        n, e = mycielski(n, e)
    return n, e


def rand(nv, p, seed):
    rng = random.Random(seed)
    return nv, [(u, v) for u in range(nv) for v in range(u + 1, nv)
                if rng.random() < p]


def lineage(name):
    sys.path.insert(0, str(REPO / "experiments" / "combinatorial"))
    from f1pt_lib import parse_vtx, parse_edges, VTX as _VTX, EDGE as _EDGE
    nv = len(parse_vtx(_VTX / f"{name}.vtx"))
    edges = [tuple(e) for e in parse_edges(_EDGE / f"{name}.edge")]
    return nv, edges


# --------------------------- timing helpers ----------------------------------

def maple_solve(n, edges, k):
    cl, _ = build_color_cnf(n, edges, k)
    t0 = time.perf_counter()
    s = MapleChrono(bootstrap_with=cl)
    try:
        s.conf_budget(MAPLE_CONF_BUDGET)
        r = s.solve_limited()   # None if the conflict budget is exhausted
    finally:
        s.delete()
    return r, time.perf_counter() - t0


def hn_solve(n, edges, k):
    t0 = time.perf_counter()
    verdict, nodes = hn_solver.solve_counting_nodes(n, edges, k,
                                                    node_limit=NODE_LIMIT)
    return verdict, nodes, time.perf_counter() - t0


# --------------------------- bench driver ------------------------------------

def chromatic_via_maple(n, edges, kmax=12):
    for k in range(1, kmax + 1):
        r, _ = maple_solve(n, edges, k)
        if r:
            return k
    return None


# (label, (n, edges), explicit_ks_or_None). If ks is None, auto-detect chi and
# use {chi-1, chi}. Lineage uses an explicit k to avoid a slow UNSAT probe.
def suite():
    items = [
        ("K6", complete(6), None),
        ("K7", complete(7), None),
        ("K8", complete(8), None),
        ("Moser spindle (7v)", moser_spindle(), None),
        ("Grotzsch M(C5) 11v (tri-free)", myc_tower(1), None),
        ("M^2(C5) 23v (tri-free)", myc_tower(2), None),
        ("M^3(C5) 47v (tri-free)", myc_tower(3), None),
        ("M^4(C5) 95v (tri-free)", myc_tower(4), [7]),
        ("rand G(15,0.5)", rand(15, 0.5, 1), None),
        ("rand G(25,0.4)", rand(25, 0.4, 2), None),
        ("rand G(40,0.3)", rand(40, 0.3, 3), None),
        ("rand G(60,0.25)", rand(60, 0.25, 4), None),
        ("lineage P510 (k=5 SAT)", lineage("510"), [5]),
    ]
    return items


def fmt_t(t):
    return f"{t * 1000:.1f} ms" if t < 1 else f"{t:.2f} s"


def main():
    rows = []
    disagreements = 0
    print(f"{'instance':32s} {'k':>2s} {'hn':>8s} {'nodes':>11s} "
          f"{'hn_t':>9s} {'maple':>6s} {'maple_t':>9s} {'agree':>6s}", flush=True)
    for label, (n, edges), ks in suite():
        if ks is None:
            chi = chromatic_via_maple(n, edges)
            ks = [k for k in (chi - 1, chi) if k >= 1]
            chi_str = str(chi)
        else:
            chi_str = "?"
        for k in ks:
            hv, nodes, ht = hn_solve(n, edges, k)
            mv, mt = maple_solve(n, edges, k)
            hn_s = {True: "SAT", False: "UNSAT", None: "BUDGET"}[hv]
            mp_s = {True: "SAT", False: "UNSAT", None: "?"}[mv]
            agree = (hv is None) or (mv is None) or (bool(hv) == bool(mv))
            if not agree:
                disagreements += 1
            speed = ""
            if hv is not None and ht > 0 and mt > 0:
                ratio = ht / mt
                speed = f"hn {1 / ratio:.1f}x" if ratio < 1 else f"maple {ratio:.0f}x"
            rows.append((label, n, len(edges), chi_str, k, hn_s, nodes, ht,
                         mp_s, mt, agree, speed))
            print(f"{label:32s} {k:>2d} {hn_s:>8s} {nodes:>11,d} "
                  f"{fmt_t(ht):>9s} {mp_s:>6s} {fmt_t(mt):>9s} "
                  f"{'OK' if agree else 'MISMATCH':>6s}", flush=True)

    # markdown
    lines = ["# hn_solver benchmark results", "",
             f"Node budget: {NODE_LIMIT:,}. MapleChrono in-process (pysat). "
             "BUDGET = hn_solver hit the node limit. Times are wall-clock; "
             "MapleChrono is a compiled C CDCL solver, hn_solver is pure Python.",
             "",
             "| instance | n | m | chi | k | hn | nodes | hn time | maple | "
             "maple time | agree | winner |",
             "|---|--:|--:|:--:|--:|:--:|--:|--:|:--:|--:|:--:|:--:|"]
    for (label, n, m, chi, k, hn_s, nodes, ht, mp_s, mt, agree, speed) in rows:
        lines.append(f"| {label} | {n} | {m} | {chi} | {k} | {hn_s} | "
                     f"{nodes:,} | {fmt_t(ht)} | {mp_s} | {fmt_t(mt)} | "
                     f"{'OK' if agree else '**MISMATCH**'} | {speed} |")
    hn_wins = sum(1 for r in rows if r[10] and r[5] != "BUDGET"
                  and r[7] < r[9])
    budgets = sum(1 for r in rows if r[5] == "BUDGET")
    lines += ["",
              f"Total instances/k: {len(rows)}. Correctness disagreements: "
              f"{disagreements}. hn_solver hit the node budget on {budgets}. "
              f"hn_solver faster on {hn_wins}/{len(rows)}.", ""]
    OUT.write_text("\n".join(lines))
    print(f"\ndisagreements: {disagreements}  budgets: {budgets}  "
          f"hn_faster: {hn_wins}/{len(rows)}")
    print(f"markdown -> {OUT}")


if __name__ == "__main__":
    main()
