r"""E23: the minimum order of a $K_4$-free $6$-chromatic graph.

A question with no unit-distance content, run on the same machinery, for two
reasons. It is a standing question of its own (the $\chi \ge 5$ analogue is
Jensen-Royle 1995: the answer is $11$), so a bound here is citable outside this
program. And it is the natural control for L78: the both-free class dies at
$n = 17$ in under an hour, and E20's ablation showed that removing the codegree
bound (keeping $K_4$-freeness) left the same cell UNDECIDED after 900 seconds. So
this experiment measures how much of L78's speed came from the UDG-specific
constraint rather than from the $\Sigma_2$ collapse itself.

THE QUESTION. Let $f(k)$ be the least $n$ admitting a $K_4$-free graph with
$\chi \ge k$. Then $f(4) = 11$ (Groetzsch, unique by Chvatal) restricted to
triangle-free, $f(5) = 11$ (Jensen-Royle), and $f(6)$ is what this asks. An upper
bound is immediate: the Mycielskian tower gives a triangle-free (hence $K_4$-free)
$6$-chromatic graph on $47$ vertices, so $f(6) \le 47$.

THE ENCODING, and why it is NOT the E20 cell CNF. Dropping $K_{2,3}$-freeness
also drops two things E20 relied on:

  * the codegree edge ceiling, so the upper end of the edge window becomes
    Turan's bound $\lfloor n^2/3 \rfloor$ for $K_4$-free graphs;
  * the E17 maximum-degree lemma $\Delta \le (n-1)/2$, whose proof used
    $K_{2,3}$-freeness. NO degree cap is imposed here.

What survives is the criticality reduction, which never used the class: a
$\chi \ge 6$ graph contains a $6$-critical subgraph, which is $K_4$-free if the
host is, has $\delta \ge 5$, is connected, and meets the Kostochka-Yancey floor
$m \ge \lceil (28n-18)/10 \rceil$. So UNSAT for every edge count at order $n$
proves $f(6) > n$.

CALIBRATION is already done and lives in E20's ladder: the same encoder and solver
return UNSAT at $n = 10$ and SAT at $n = 11$ for $\chi \ge 5$ with $K_4$
forbidden, reproducing Jensen-Royle, and at $k = 6$ they return UNSAT at $n = 7$
and SAT at $n = 8$ with $K_6$ forbidden, returning $C_5 + K_3$. `--calibrate` here
re-runs the $\chi \ge 5$ pair through THIS module's encoder, so the reduction
stack (delta, KY floor, Turan ceiling) is exercised end to end against a published
answer before any new claim is made.

Certification: see L80. An UNSAT here is not a propositional refutation of the
cell formula (which is satisfiable), so it carries the same epistemic status as
L78's, no better and no worse.

Usage:
    python -m experiments.combinatorial.e23_k4free_chi6 --calibrate
    python -m experiments.combinatorial.e23_k4free_chi6 --n 12
    python -m experiments.combinatorial.e23_k4free_chi6 --climb 12 --timeout 3600
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import itertools
import json
import math
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                        # noqa: E402

from e18_gallai import CriticalEncoding, ky_floor            # noqa: E402
from e20_sigma2 import (run_smsg, verify_model, _write_dimacs,  # noqa: E402
                        _assert_edge_order, set_parallelism,
                        SAT, UNSAT, UNKNOWN)

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e23"


def turan_ceiling(n):
    """Max edges of a K4-free graph on n vertices (Turan, r=3)."""
    return (n * n) // 3


def ky_floor_k(n, k):
    """Kostochka-Yancey: a k-critical graph has
    $m \\ge \\frac{(k+1)(k-2)n - k(k-3)}{2(k-1)}$.
    At $k=6$ this is $(28n-18)/10$, the floor `e18_gallai.ky_floor` hard-codes,
    which is asserted below rather than assumed."""
    return math.ceil(((k + 1) * (k - 2) * n - k * (k - 3)) / (2 * (k - 1)))


assert all(ky_floor_k(n, 6) == ky_floor(n) for n in range(7, 40)), \
    "general KY floor disagrees with the k=6 floor E18 uses"


def window(n, k=6):
    """The edge window. An EMPTY window is a real answer (no k-critical graph of
    that order can exist), but it must never be reported as a checked one: the
    first version of this function had a wrong k=5 floor, which made n=10 come
    back UNSAT with zero cells and pass the calibration vacuously."""
    lo, hi = ky_floor_k(n, k), turan_ceiling(n)
    return lo, hi


def build_cnf(n, m, path, k=6, split=None):
    """K4-free, delta >= k-1, edge count exactly m. No degree cap, no codegree."""
    enc = CriticalEncoding(n, k=k, k4free=True, codeg2=False,
                           gallai_cyc=False, gallai_loc=False,
                           min_edges=m, max_edges=m, maxdeg=None,
                           symbreak=False, symbreak_all=False)
    _assert_edge_order(enc, n)
    units = []
    if split:
        t, idx = [int(x) for x in split.split(":")]
        pairs = list(itertools.combinations(range(n), 2))
        for b, (i, j) in enumerate(pairs[-t:]):
            units.append(enc.var(i, j) if (idx >> b) & 1 else -enc.var(i, j))
    return _write_dimacs(enc.cnf, path, units)


def decide(n, m, k=6, timeout=None, split=None, quiet=False, resume=True):
    CACHE.mkdir(parents=True, exist_ok=True)
    tag = f"n{n}_m{m}_chi{k}" + (f"_s{split.replace(':', '_')}" if split else "")
    done = CACHE / f"{tag}.json"
    if resume and done.exists():
        c = json.loads(done.read_text())
        if c.get("result") in (SAT, UNSAT):
            return c
    cnf = CACHE / f"{tag}.cnf"
    nv, ncl = build_cnf(n, m, cnf, k=k, split=split)
    r = run_smsg(n, cnf, k, connected=True, timeout=timeout,
                 log=CACHE / f"{tag}.log")
    out = {"n": n, "m": m, "chi": k, "split": split, "vars": nv, "clauses": ncl,
           "result": r["result"], "elapsed_s": r["elapsed_s"]}
    if r["result"] == SAT and r["models"]:
        v = verify_model(n, r["models"][-1], k, m=m, class_member=False)
        v["k4_free_check"] = v["k4_free"]
        out["witness"] = v
        out["edges"] = r["models"][-1]
    done.write_text(json.dumps(out, indent=2))
    if not quiet:
        print(f"  n={n} m={m} chi>={k}: {r['result']} ({r['elapsed_s']}s)", flush=True)
    return out


def decide_order(n, k=6, jobs=7, timeout=None):
    """Is there a K4-free chi>=k graph on exactly n vertices? SAT in any cell wins."""
    lo, hi = window(n, k)
    cells = list(range(lo, hi + 1))
    print(f"n={n}: edge window [{lo}, {hi}] ({len(cells)} cells), "
          f"KY floor to Turan ceiling", flush=True)
    if not cells:
        print(f"  n={n}: NONE, vacuously (the KY floor exceeds the Turan "
              f"ceiling, so no K4-free k-critical graph of this order exists)",
              flush=True)
        return {"n": n, "chi": k, "window": [lo, hi], "verdict": UNSAT,
                "vacuous": True, "wall_s": 0.0, "cpu_s": 0.0,
                "unknown_cells": [], "witness": None, "per_cell": {}}
    t0 = time.time()
    with futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        res = list(ex.map(lambda m: decide(n, m, k, timeout, quiet=True), cells))
    hits = [r for r in res if r["result"] == SAT]
    unk = [r["m"] for r in res if r["result"] == UNKNOWN]
    for r in res:
        mark = {SAT: "  <-- WITNESS", UNSAT: "", UNKNOWN: "  (timeout)"}[r["result"]]
        print(f"    m={r['m']}: {r['result']} ({r['elapsed_s']}s){mark}", flush=True)
    verdict = (SAT if hits else UNKNOWN if unk else UNSAT)
    summary = {"n": n, "chi": k, "window": [lo, hi], "verdict": verdict,
               "wall_s": round(time.time() - t0, 1),
               "cpu_s": round(sum(r["elapsed_s"] for r in res), 1),
               "unknown_cells": unk,
               "witness": (hits[0].get("witness") if hits else None),
               "per_cell": {str(r["m"]): [r["result"], r["elapsed_s"]] for r in res}}
    (CACHE / f"order_n{n}_chi{k}.json").write_text(json.dumps(summary, indent=2))
    if verdict == SAT:
        w = hits[0]["witness"]
        print(f"  n={n}: EXISTS. K4-free chi>={k} graph found, "
              f"independently verified chi>={k}: {w['chi_ge']}, "
              f"K4-free: {w['k4_free']}, g6={w['g6']}", flush=True)
    elif verdict == UNSAT:
        print(f"  n={n}: NONE. No K4-free chi>={k} graph on {n} vertices "
              f"[{summary['cpu_s']}s cpu]", flush=True)
    else:
        print(f"  n={n}: UNDECIDED, cells {unk} timed out", flush=True)
    return summary


def calibrate(jobs=7, timeout=600):
    """Reproduce Jensen-Royle f(5)=11 through THIS module's encoder."""
    print("E23 calibration: f(5) = 11 (Jensen-Royle 1995), via this encoder",
          flush=True)
    ok = True
    for n, want in ((10, UNSAT), (11, SAT)):
        s = decide_order(n, k=5, jobs=jobs, timeout=timeout)
        good = s["verdict"] == want
        ok &= good
        print(f"  [{'ok' if good else 'FAIL'}] n={n} -> {s['verdict']} "
              f"(want {want})", flush=True)
    print(f"calibration: {'PASS' if ok else 'FAILURE'}", flush=True)
    return ok


def climb(n_from, n_to=99, k=6, jobs=7, timeout=None):
    """Walk n upward until a witness appears. The first SAT is f(k)."""
    set_parallelism(jobs)
    ladder = {}
    for n in range(n_from, n_to + 1):
        s = decide_order(n, k=k, jobs=jobs, timeout=timeout)
        ladder[n] = {kk: s[kk] for kk in ("verdict", "window", "cpu_s", "wall_s",
                                          "unknown_cells")}
        (CACHE / f"climb_chi{k}.json").write_text(json.dumps(ladder, indent=2))
        if s["verdict"] == SAT:
            print(f"*** f({k}) = {n}: the smallest K4-free {k}-chromatic graph "
                  f"has {n} vertices ***", flush=True)
            return 0
        if s["verdict"] == UNKNOWN:
            print(f"*** WALL at n={n} (cells {s['unknown_cells']}). "
                  f"Established so far: f({k}) > {n - 1}. ***", flush=True)
            return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--m", type=int)
    ap.add_argument("--chi", type=int, default=6)
    ap.add_argument("--climb", type=int, metavar="FROM")
    ap.add_argument("--jobs", type=int, default=7)
    ap.add_argument("--timeout", type=int, default=None)
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    set_parallelism(args.jobs)
    if args.calibrate:
        return 0 if calibrate(jobs=args.jobs, timeout=args.timeout or 600) else 1
    if args.climb:
        return climb(args.climb, k=args.chi, jobs=args.jobs, timeout=args.timeout)
    if args.n and args.m:
        r = decide(args.n, args.m, args.chi, args.timeout)
        return {UNSAT: 0, SAT: 2}.get(r["result"], 1)
    if args.n:
        s = decide_order(args.n, k=args.chi, jobs=args.jobs, timeout=args.timeout)
        return {UNSAT: 0, SAT: 2}.get(s["verdict"], 1)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
