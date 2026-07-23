r"""E17: nauty-powered exhaustive search of the "both-free class" for a
chi >= 6 member (K4-free AND K_{2,3}-free, the UDG-necessary class of L63).

This is the door L69 left open ("sourcing a sparse 6-critical graph outside the
Mycielski family needs nauty"): enumerate ALL candidate 6-critical members per
order n and chi-filter them. Frame (sanity-checked in e17_window_table.py):

  - Any chi >= 6 member of the class contains a 6-critical subgraph that is
    itself in the class (both properties are subgraph-closed), so a per-n sweep
    over 6-critical CANDIDATES is exhaustive for the class up to order N.
  - 6-critical candidates at order n: 2-connected (Dirac; geng -C), min degree
    >= 5 (geng -d5), max degree <= (n-1)/2 (codegree + mindeg argument, see
    maxdeg_cap), m in [Kostochka-Yancey floor, codegree ceiling] (edge window).
  - Folkman floor (Lathrop-Radziszowski 2011): K4-free chi >= 6 needs n >= 16.

Pipeline per (n, res/mod) cell:
  geng_hn -C -d5 -D# -q n mine:maxe res/mod    (custom PRUNE build, e17_prune.c:
    incremental K4/K_{2,3} rejection + cherry-budget prune, also as PREPRUNE)
    -> stream graph6 -> INDEPENDENT Python re-verification of both-freeness
       (e17_bothfree_filter.py, disjoint code from the C plugin; any
        disagreement is a hard error)
    -> chi filter: DSATUR 5-coloring (fast path, discards ~all)
       -> residue: in-process pysat Cadical195 5-colorability decision
       -> any UNSAT-at-5 survivor is a HIT: confirmed by the independent
          multi-solver portfolio (_shared/portfolio_sat, symbreak encoding),
          saved immediately as JSON, and the run stops-the-world.

Feasibility discipline: run --count-only first; do not launch a cell whose
both-free-pruned output count exceeds ~1e9. Checkpointing per (n, mod) under
_cache/e17/ so interrupted runs resume by res part.

CLI (always via the project venv):
  .venv/bin/python experiments/combinatorial/e17_nauty_host_search.py --count-only 16 17 18
  .venv/bin/python ... --calibrate            # gates b + c (see e17_results.md)
  .venv/bin/python ... --run 16 --mod 16 --jobs 16
  .venv/bin/python ... --run 17 --mod 64 --jobs 16
"""
from __future__ import annotations
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from e17_window_table import window                      # noqa: E402
from e17_bothfree_filter import (graph6_to_adj,          # noqa: E402
                                 is_k4_free, is_k23_free)
from experiments._shared.portfolio_sat import (          # noqa: E402
    build_color_cnf, colorable_portfolio)

GENG_HN = os.path.expanduser("~/.local/bin/geng_hn")
CACHE = HERE / "_cache" / "e17"
RESULTS_MD = HERE / "e17_results.md"
COUNT_WALL = 1_000_000_000     # do not launch a cell above this both-free count


# ---------------------------------------------------------------- geng driving

def maxdeg_cap(n):
    """Sound max-degree cap for the target class. In a K_{2,3}-free graph
    (codegree <= 2) with min degree >= 5, for any vertex a the length-2 walks
    from a satisfy sum_{w in N(a)} (deg w - 1) <= 2(n-1) (each endpoint x != a
    is reached via at most codeg(a,x) <= 2 midpoints), so 4 deg(a) <= 2(n-1),
    i.e. deg(a) <= (n-1)/2. Passing this to geng as -D shrinks the tree
    massively without excluding any target graph."""
    return (n - 1) // 2


def geng_args(n, mine, maxe, res=None, mod=None, count_only=False):
    # -C (biconnected) is sound: 6-critical graphs are 2-connected (Dirac),
    # and the exhaustive claim only needs the 6-critical members per n.
    a = [GENG_HN, "-C", "-d5", f"-D{maxdeg_cap(n)}", str(n), f"{mine}:{maxe}"]
    if count_only:
        a.insert(1, "-u")
    else:
        a.insert(1, "-q")
    if mod is not None:
        a.append(f"{res}/{mod}")
    return a


_ZLINE = re.compile(r">Z\s+([\d,]+)\s+graphs generated")


def count_cell(n, mine, maxe, res=None, mod=None, timeout=None):
    """geng_hn -u count of both-free connected mindeg-5 graphs in the cell.
    Returns (count, seconds) or (None, seconds) on timeout."""
    t0 = time.time()
    try:
        p = subprocess.run(geng_args(n, mine, maxe, res, mod, count_only=True),
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, time.time() - t0
    m = _ZLINE.search(p.stderr)
    if not m:
        raise RuntimeError(f"no >Z line from geng_hn: {p.stderr[-300:]}")
    return int(m.group(1).replace(",", "")), time.time() - t0


# ---------------------------------------------------------------- chi filter

def dsatur_colors(n, adj, k):
    """DSATUR greedy k-coloring; returns a coloring list or None (heuristic
    failure, NOT evidence of uncolorability)."""
    colors = [-1] * n
    satmask = [0] * n
    degs = [adj[v].bit_count() for v in range(n)]
    full = (1 << k) - 1
    for _ in range(n):
        best, bs, bd = -1, -1, -1
        for v in range(n):
            if colors[v] < 0:
                s = satmask[v].bit_count()
                if s > bs or (s == bs and degs[v] > bd):
                    best, bs, bd = v, s, degs[v]
        avail = ~satmask[best] & full
        if not avail:
            return None
        c = (avail & -avail).bit_length() - 1
        colors[best] = c
        w, u = adj[best], 0
        while w:
            if w & 1:
                satmask[u] |= 1 << c
            w >>= 1
            u += 1
    return colors


def edges_of(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n)
            if (adj[u] >> v) & 1]


def sat5_inprocess(n, edges):
    """In-process Cadical195 5-colorability decision (fast residue path)."""
    from pysat.solvers import Solver
    clauses, _ = build_color_cnf(n, edges, 5)
    with Solver(name="cadical195", bootstrap_with=clauses) as s:
        return s.solve()


def save_provisional_hit(n, line, adj):
    """A graph survived DSATUR + in-process Cadical as 5-UNSAT. Persist it
    IMMEDIATELY (crash-safe), marked provisional. The multi-solver portfolio
    confirmation runs in the MAIN process (finalize_hit): portfolio_solve
    spawns processes, which a daemonic Pool worker is not allowed to do."""
    edges = edges_of(n, adj)
    out = {
        "experiment": "e17_nauty_host_search",
        "claim": "K4-free K_{2,3}-free graph, 5-UNSAT per in-process "
                 "Cadical195 (PROVISIONAL, portfolio confirmation pending)",
        "n": n, "m": len(edges),
        "graph6": line,
        "edges": edges,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    import hashlib
    tag = hashlib.md5(line.encode()).hexdigest()[:8]   # deterministic name
    path = HERE / f"e17_hit_n{n}_{tag}.json"
    path.write_text(json.dumps(out, indent=1))
    return path


def finalize_hit(path):
    """Main-process confirmation of a provisional hit with the independent
    multi-solver portfolio (symbreak encoding). Returns True iff the hit
    stands (5-UNSAT confirmed)."""
    d = json.loads(pathlib.Path(path).read_text())
    n, edges = d["n"], [tuple(e) for e in d["edges"]]
    conf = colorable_portfolio(n, edges, 5, symbreak=True)
    six = colorable_portfolio(n, edges, 6, want_coloring=True, symbreak=True)
    d["portfolio_5colorable"] = conf["result"]
    d["portfolio_5_solver"] = conf.get("winner")
    d["portfolio_6colorable"] = six["result"]
    d["coloring6"] = six.get("coloring")
    d["claim"] = ("K4-free K_{2,3}-free graph with chi >= 6 (CANDIDATE, "
                  "portfolio-confirmed 5-UNSAT)" if not conf["result"] else
                  "SOLVER DISAGREEMENT: cadical 5-UNSAT vs portfolio 5-SAT")
    pathlib.Path(path).write_text(json.dumps(d, indent=1))
    return not conf["result"]


# ---------------------------------------------------------------- cell worker

def process_cell(task):
    """Worker: run one geng_hn (n, mine, maxe, res/mod) part and chi-filter the
    stream. Returns a stats dict; stats['hit'] is a path string on a hit."""
    n, mine, maxe, res, mod = task
    t0 = time.time()
    stats = {"n": n, "res": res, "mod": mod, "generated": 0,
             "recheck_fail": 0, "dsatur_colored": 0, "sat_colored": 0,
             "sat_residue_g6": [], "hit": None}
    p = subprocess.Popen(geng_args(n, mine, maxe, res, mod),
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                         text=True, bufsize=1 << 16)
    try:
        for line in p.stdout:
            line = line.strip()
            if not line:
                continue
            stats["generated"] += 1
            gn, adj = graph6_to_adj(line)
            assert gn == n
            # independent double-check layer (disjoint from the C plugin)
            if not (is_k4_free(n, adj) and is_k23_free(n, adj)):
                stats["recheck_fail"] += 1
                raise RuntimeError(
                    f"PLUGIN BUG: geng_hn emitted non-both-free graph {line}")
            if dsatur_colors(n, adj, 5) is not None:
                stats["dsatur_colored"] += 1
                continue
            if sat5_inprocess(n, edges_of(n, adj)):
                stats["sat_colored"] += 1
                # persist the DSATUR-resistant graph itself, not just the
                # count, so the residue set is re-checkable without
                # re-enumerating the part (VERIFIER finding, 2026-07-23)
                stats["sat_residue_g6"].append(line)
                continue
            # 5-UNSAT survivor: persist immediately, stop this part;
            # the caller portfolio-confirms in the main process.
            stats["hit"] = str(save_provisional_hit(n, line, adj))
            p.terminate()
            break
    finally:
        p.stdout.close()
        p.wait()
    stats["secs"] = round(time.time() - t0, 2)
    return stats


# ---------------------------------------------------------------- orchestration

def append_results(text):
    with open(RESULTS_MD, "a") as f:
        f.write(text.rstrip() + "\n")


def checkpoint_path(n, mod):
    return CACHE / f"checkpoint_n{n}_mod{mod}.json"


def run_order(n, mod, jobs):
    w = window(n)
    if w is None:
        print(f"n={n}: window EMPTY, nothing to run")
        return
    mine, maxe = w
    CACHE.mkdir(parents=True, exist_ok=True)
    ckpath = checkpoint_path(n, mod)
    ck = json.loads(ckpath.read_text()) if ckpath.exists() else \
        {"n": n, "mod": mod, "window": [mine, maxe], "done": {}}
    todo = [r for r in range(mod) if str(r) not in ck["done"]]
    print(f"n={n} window {mine}..{maxe} mod={mod}: "
          f"{len(todo)} parts to run ({mod - len(todo)} done)")
    if not todo:
        summarize_order(n, mod, ck)
        return
    import multiprocessing as mp
    t0 = time.time()
    hit = None
    with mp.Pool(processes=jobs) as pool:
        for stats in pool.imap_unordered(
                process_cell, [(n, mine, maxe, r, mod) for r in todo]):
            ck["done"][str(stats["res"])] = stats
            ckpath.write_text(json.dumps(ck))
            print(f"  part {stats['res']}/{mod}: gen={stats['generated']} "
                  f"dsatur={stats['dsatur_colored']} sat={stats['sat_colored']} "
                  f"({stats['secs']}s)", flush=True)
            if stats["hit"]:
                hit = stats["hit"]
                pool.terminate()
                break
    if hit:
        stands = finalize_hit(hit)
        append_results(
            f"- **{'HIT' if stands else 'SOLVER DISAGREEMENT'} at n={n}**: "
            f"`{hit}` (STOP-THE-WORLD, {time.strftime('%Y-%m-%d %H:%M')})")
        print(f"{'HIT (portfolio-confirmed)' if stands else 'DISAGREEMENT'}: "
              f"{hit}")
        sys.exit(17)
    if len(ck["done"]) == mod:
        summarize_order(n, mod, ck, wall=time.time() - t0)


def summarize_order(n, mod, ck, wall=None):
    tot = {k: sum(d[k] for d in ck["done"].values())
           for k in ("generated", "dsatur_colored", "sat_colored")}
    secs = sum(d["secs"] for d in ck["done"].values())
    mine, maxe = ck["window"]
    line = (f"| {n} | {mine}..{maxe} | {tot['generated']} | "
            f"{tot['dsatur_colored']} | {tot['sat_colored']} | 0 | "
            f"{secs:.0f}s cpu | complete |")
    append_results(line)
    print(f"n={n} COMPLETE: {tot['generated']} both-free graphs, "
          f"{tot['dsatur_colored']} DSATUR-5-colored, "
          f"{tot['sat_colored']} SAT-5-colored, 0 hits "
          f"({secs:.0f}s cpu{f', {wall:.0f}s wall' if wall else ''})")


def count_only(orders, timeout, per_m=False):
    print(f"{'n':>3} {'window':>8} {'both-free count':>16} {'secs':>8}")
    for n in orders:
        w = window(n)
        if w is None:
            print(f"{n:>3} {'EMPTY':>8} {'-':>16} {'-':>8}")
            continue
        mine, maxe = w
        if per_m:
            for m in range(mine, maxe + 1):
                c, s = count_cell(n, m, m, timeout=timeout)
                cs = "TIMEOUT" if c is None else str(c)
                print(f"{n:>3} {f'{m}:{m}':>8} {cs:>16} {s:>8.1f}")
        c, s = count_cell(n, mine, maxe, timeout=timeout)
        cs = "TIMEOUT" if c is None else str(c)
        print(f"{n:>3} {f'{mine}:{maxe}':>8} {cs:>16} {s:>8.1f}", flush=True)
        if c is not None and c > COUNT_WALL:
            print(f"    n={n} exceeds the {COUNT_WALL:.0e} wall: DO NOT LAUNCH")


# ---------------------------------------------------------------- calibration

def calibrate():
    ok = True
    # Gate (b): n=16 m=48 forces srg(16,6,2,2); K4-free => Shrikhande; chi=4.
    # (m=48 forces 6-regular with every codegree exactly 2: cherries
    #  sum C(d,2) >= 240 by convexity with equality iff 6-regular, and the
    #  K_{2,3} bound caps cherries at 240.)
    print("gate (b): n=16 m=48 extremal cell (parallel split) ...")
    jobs = os.cpu_count()

    def cell_args(r):
        # -D6 is sound HERE: m=48 at n=16 forces 6-regularity (cherry
        # convexity), unlike the general window which needs -D7.
        return [GENG_HN, "-C", "-d5", "-D6", "-q", "16", "48:48",
                f"{r}/{jobs}"]
    procs = [subprocess.Popen(cell_args(r), stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, text=True)
             for r in range(jobs)]
    lines = []
    for p in procs:
        out, _ = p.communicate()
        lines += [l for l in out.split() if l.strip()]
    print(f"  geng_hn -C -d5 -D6 16 48:48 emitted {len(lines)} graph(s)")
    if len(lines) != 1:
        print("  FAIL: expected exactly 1 (the Shrikhande graph)")
        return False
    n, adj = graph6_to_adj(lines[0])
    degs = sorted(a.bit_count() for a in adj)
    reg6 = degs == [6] * 16
    codegs = sorted((adj[u] & adj[v]).bit_count()
                    for u in range(16) for v in range(u + 1, 16))
    srg = reg6 and codegs == [2] * 120
    print(f"  6-regular: {reg6}; all 120 codegrees == 2 (srg(16,6,2,2)): {srg}")
    # explicit Shrikhande: Cayley graph on Z4 x Z4, S = {+-(1,0),+-(0,1),+-(1,1)}
    import networkx as nx
    S = {(1, 0), (3, 0), (0, 1), (0, 3), (1, 1), (3, 3)}
    G = nx.Graph()
    for a in range(4):
        for b in range(4):
            for (da, db) in S:
                G.add_edge((a, b), ((a + da) % 4, (b + db) % 4))
    H = nx.Graph()
    H.add_nodes_from(range(16))
    H.add_edges_from(edges_of(16, adj))
    iso = nx.is_isomorphic(G, H)
    print(f"  isomorphic to Shrikhande (Cayley Z4xZ4 construction): {iso}")
    e = edges_of(16, adj)
    chi3 = colorable_portfolio(16, e, 3, symbreak=True)["result"]
    chi4 = colorable_portfolio(16, e, 4, symbreak=True)["result"]
    print(f"  3-colorable: {chi3} (want False); 4-colorable: {chi4} "
          f"(want True) => chi = 4, correctly REJECTED as a chi>=6 candidate")
    ok &= srg and iso and (not chi3) and chi4
    # Gate (c): Folkman floor, n < 16 cells must have 0 hits.
    print("gate (c): n=13,14,15 full windows, expect 0 hits ...")
    import multiprocessing as mp
    for n in (13, 14, 15):
        w = window(n)
        mod = jobs if n == 15 else None      # n=15's tree needs the split
        tasks = [(n, w[0], w[1], r, mod) for r in range(mod)] if mod \
            else [(n, w[0], w[1], None, None)]
        if mod:
            with mp.Pool(processes=jobs) as pool:
                parts = list(pool.imap_unordered(process_cell, tasks))
        else:
            parts = [process_cell(tasks[0])]
        gen = sum(p["generated"] for p in parts)
        dsa = sum(p["dsatur_colored"] for p in parts)
        sat = sum(p["sat_colored"] for p in parts)
        secs = max(p["secs"] for p in parts)
        hit = next((p["hit"] for p in parts if p["hit"]), None)
        print(f"  n={n} window {w[0]}..{w[1]}: generated={gen} "
              f"dsatur={dsa} sat={sat} "
              f"hits={'1 (FAIL)' if hit else 0} ({secs}s wall)")
        ok &= hit is None
    print(f"calibration: {'ALL GATES PASS' if ok else 'FAILURE'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count-only", nargs="+", type=int, metavar="N")
    ap.add_argument("--per-m", action="store_true",
                    help="with --count-only, also count each edge cell")
    ap.add_argument("--count-timeout", type=float, default=None)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--run", type=int, metavar="N")
    ap.add_argument("--mod", type=int, default=16)
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    args = ap.parse_args()
    if args.calibrate:
        sys.exit(0 if calibrate() else 1)
    if args.count_only:
        count_only(args.count_only, args.count_timeout, per_m=args.per_m)
        return
    if args.run:
        run_order(args.run, args.mod, args.jobs)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
