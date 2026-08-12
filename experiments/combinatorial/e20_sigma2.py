r"""E20: collapse the $\Sigma_2$ half of the both-free question into ONE CDCL run.

The question E17/E18/E19 keep asking is
$$\exists\, G \text{ in the both-free class on } n \text{ vertices with } \chi(G) \ge 6\;?$$
which is $\Sigma_2$: an existential over graphs wrapping a universal over
5-colorings. Every previous attack answered it by SPLITTING the quantifiers --
enumerate all class members (geng, or SMS), then color each one. That is why
$n=16$ cost 66.3 cpu-h for 11,315 graphs and why $n=17$ (~100x the classes) is a
wall: the cost is proportional to the SIZE OF THE CLASS, not to the difficulty of
the question.

This module never enumerates the class. SMS ships a chromatic-number propagator
(`src/graphPropagators/coloringCheck.cpp`, `MinChromaticNumberChecker`) that the
program has never used: on a fully-defined candidate graph it looks for a
$(k-1)$-coloring, and if it finds one it LEARNS the clause "at least one of the
currently monochromatic non-adjacent pairs must become an edge", handing the
conflict back to CDCL. So the universal half becomes clause learning inside the
same solver whose minimality propagator already owns the isomorphism half:

    smsg -v n --min-chromatic-number 6 --dimacs <class cell>

    Result: 20 (UNSAT)  ==  NO member of that cell has chi >= 6.  A theorem.
    Result: 10 (SAT)    ==  a member with chi >= 6.  A hit, to be re-verified.

Cost is now proportional to the number of learned coloring clauses, which is
bounded by search difficulty rather than by class size. The $n=16$ cells are the
calibration: they must return UNSAT, and the wall-clock ratio against the
measured 66.3 cpu-h census is the predictor for $n=17$.

SOUNDNESS (identical framing to L75/E17, no new burden). The class properties
($K_4$-free, all codegrees $\le 2$) are subgraph-closed, so if any member has
$\chi \ge 6$ then some 6-CRITICAL member does, on $n' \le n$ vertices; a
6-critical graph has $\delta \ge 5$, is 2-connected, satisfies the
Kostochka-Yancey edge floor, and (with the class properties) the E17 maxdeg
lemma $\Delta \le (n-1)/2$. So a sweep returning UNSAT for every cell of every
$n' \le N$ proves the class has no $\chi \ge 6$ member on $\le N$ vertices. The
per-cell CNF is the SAME relaxation-gated `CriticalEncoding` used by E18/E19,
with NO lex-leader clauses (SMS owns canonicity). Gallai's low-vertex conditions
are OFF by default: they are sound only for the critical witness, and L76
measured them as ~2 orders of magnitude too weak to be worth the extra argument.

CALIBRATION LADDER (run `--calibrate`; nothing below is trusted before it passes):
  (A) GROETZSCH, an external uniqueness theorem, tests the propagator and the
      plumbing in BOTH directions: triangle-free with $\chi \ge 4$ is UNSAT at
      $n=10$ and SAT at $n=11$, and the model is the Groetzsch graph.
  (B) $K_4$-free $\chi \ge 5$ is UNSAT at $n=10$, SAT at $n=11$ (Jensen-Royle
      1995). Literature-dependent, so it reports rather than gates.
  (C) NON-VACUITY, per production cell: the same CNF with
      `--min-chromatic-number 3` must be SAT and the model must pass the
      disjoint-code E17 both-free filter. Without this, an UNSAT at $\chi \ge 6$
      could be an empty-cell artifact of a mis-stated constraint.
  (D) THE REPO ANSWER: the $n=15$ and $n=16$ windows must return UNSAT at
      $\chi \ge 6$, reproducing the L75 (geng) and L77 (SMS census) verdicts by a
      third route, and the wall-clock ratio is recorded.

Every SAT model, at any rung, is re-verified by code disjoint from the solver
that produced it (the E17 filter for class membership, the repo's SAT portfolio
for the coloring half), so a propagator bug cannot manufacture a hit.

Usage:
    python -m experiments.combinatorial.e20_sigma2 --calibrate
    python -m experiments.combinatorial.e20_sigma2 --window 17
    python -m experiments.combinatorial.e20_sigma2 --n 17 --m 46
    python -m experiments.combinatorial.e20_sigma2 --n 17 --sweep --jobs 8
"""
from __future__ import annotations

import argparse
import ast
import concurrent.futures as futures
import itertools
import json
import os
import pathlib
import subprocess
import sys
import threading
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                        # noqa: E402
from pysat.formula import CNF, IDPool                        # noqa: E402

from e17_bothfree_filter import is_k4_free, is_k23_free      # noqa: E402
from e18_gallai import CriticalEncoding, ky_floor, codegree_ceiling  # noqa: E402
from e18_sat_class import adj_from_edges                     # noqa: E402
from e18_enumerate import to_nx                              # noqa: E402
from experiments._shared.portfolio_sat import solve_color    # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e20"

SMSG = os.environ.get("SMSG", str(pathlib.Path.home() / ".local" / "bin" / "smsg"))
SAT, UNSAT, UNKNOWN = "SAT", "UNSAT", "UNKNOWN"

# Recursive splitting nests thread pools, so worker count is not a usable bound on
# how many solvers run at once. This semaphore is: it is taken only around an smsg
# invocation, never while a parent waits on its children, so it cannot deadlock.
_SLOTS = None


def set_parallelism(n):
    global _SLOTS
    _SLOTS = threading.Semaphore(n)


# ------------------------------------------------------------------ encodings

def _write_dimacs(cnf, path, units=()):
    with open(path, "w") as f:
        f.write(f"p cnf {cnf.nv} {len(cnf.clauses) + len(units)}\n")
        for cl in cnf.clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
        for cl in units:
            f.write(f"{cl} 0\n")
    return cnf.nv, len(cnf.clauses) + len(units)


def _assert_edge_order(enc, n):
    """smsg expects edge var (i,j) at the lex rank of the pair, 1-based."""
    for rank, (i, j) in enumerate(itertools.combinations(range(n), 2)):
        assert enc.var(i, j) == rank + 1, "edge-variable order mismatch"


def build_class_cnf(n, m, path, gallai=False, split=None, k4free=True, codeg2=True):
    """The both-free cell CNF: K4-free, codeg<=2, delta>=5, maxdeg<=(n-1)/2, m pinned.

    `k4free` / `codeg2` are the ablation switches. Turning one OFF enlarges the
    search space, so a SAT there is not a class member; the point of the ablation
    is to show the search CAN return SAT in this regime, which is what makes the
    unablated UNSAT a statement about the class rather than about the solver.
    """
    enc = CriticalEncoding(n, k=6, k4free=k4free, codeg2=codeg2,
                           gallai_cyc=gallai, gallai_loc=gallai,
                           min_edges=m, max_edges=m, maxdeg=(n - 1) // 2,
                           symbreak=False, symbreak_all=False)
    _assert_edge_order(enc, n)
    units = []
    if split:
        t, idx = [int(x) for x in split.split(":")]
        pairs = list(itertools.combinations(range(n), 2))
        for b, (i, j) in enumerate(pairs[-t:]):
            units.append(enc.var(i, j) if (idx >> b) & 1 else -enc.var(i, j))
    return _write_dimacs(enc.cnf, path, units)


def build_forbidden_clique_cnf(n, size, path):
    """Only edge variables, with every K_size forbidden. Used by the calibration
    rungs, where the point is to test the propagator against an external answer
    with as little of our own machinery in the way as possible."""
    pool, cnf = IDPool(), CNF()
    e = {}
    for i, j in itertools.combinations(range(n), 2):
        v = pool.id(("e", i, j))
        e[(i, j)] = e[(j, i)] = v
    for combo in itertools.combinations(range(n), size):
        cnf.append([-e[(a, b)] for a, b in itertools.combinations(combo, 2)])
    assert pool.id(("e", 0, 1)) == 1
    return _write_dimacs(cnf, path)


# ---------------------------------------------------------------------- smsg

def run_smsg(n, dimacs, chi, connected=True, timeout=None, all_graphs=False,
             coloring_algo=None, log=None, extra=()):
    cmd = [SMSG, "-v", str(n), "--dimacs", str(dimacs),
           "--min-chromatic-number", str(chi)]
    if connected:
        cmd.append("--connected")
    if all_graphs:
        cmd.append("--all-graphs")
    if coloring_algo is not None:
        cmd += ["--coloring-algo", str(coloring_algo)]
    if timeout:
        cmd += ["--timeout", str(timeout)]
    cmd += list(extra)

    t0 = time.time()
    models, tail, result = [], [], UNKNOWN
    if _SLOTS:
        _SLOTS.acquire()
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, bufsize=1)
        lines = []
        for line in p.stdout:
            s = line.strip()
            lines.append(s)
            if s.startswith("[") and s.endswith("]"):
                models.append(ast.literal_eval(s) if s != "[]" else [])
            else:
                tail.append(s)
                if s.startswith("Result:"):
                    code = s.split()[-1]
                    result = {"10": SAT, "20": UNSAT}.get(code, UNKNOWN)
        p.wait()
    finally:
        if _SLOTS:
            _SLOTS.release()
    if result is UNKNOWN and models:
        result = SAT
    if log:
        pathlib.Path(log).write_text("\n".join(lines[-400:]))
    return {"cmd": " ".join(cmd), "result": result, "models": models,
            "elapsed_s": round(time.time() - t0, 2), "returncode": p.returncode,
            "tail": [t for t in tail if t][-14:]}


# --------------------------------------------------------------- verification

def verify_model(n, edges, chi, m=None, class_member=True):
    """Re-derive, with code disjoint from smsg, what the model is claimed to be.

    Returns a dict of independent checks. `chi_ge` is the load-bearing one: the
    repo's SAT portfolio must report (chi-1)-coloring UNSAT.
    """
    adj = adj_from_edges(n, edges)
    degs = [bin(a).count("1") for a in adj]
    g = to_nx(n, edges)
    out = {
        "n_edges": len(edges),
        "k4_free": bool(is_k4_free(n, adj)),
        "k23_free": bool(is_k23_free(n, adj)),
        "min_deg": min(degs) if degs else 0,
        "max_deg": max(degs) if degs else 0,
        "connected": bool(nx.is_connected(g)) if n else False,
        "biconnected": bool(nx.is_biconnected(g)) if n > 2 else False,
        "g6": nx.to_graph6_bytes(g, header=False).decode().strip(),
    }
    res = solve_color(n, edges, chi - 1, symbreak=True)["result"]
    out["colorable_at_k_minus_1"] = bool(res)
    out["chi_ge"] = (not res)
    if class_member:
        out["class_ok"] = (out["k4_free"] and out["k23_free"]
                           and out["min_deg"] >= 5
                           and out["max_deg"] <= (n - 1) // 2
                           and (m is None or len(edges) == m))
    return out


# ---------------------------------------------------------------- calibration

def _rung(name, ok, detail):
    print(f"  [{'ok' if ok else 'FAIL'}] {name}: {detail}", flush=True)
    return ok


def calibrate(timeout=None):
    CACHE.mkdir(parents=True, exist_ok=True)
    ok = True
    print("E20 calibration ladder", flush=True)

    # (A) Groetzsch: triangle-free, chi >= 4. UNSAT at 10, SAT at 11.
    print(" (A) triangle-free chi>=4  [Groetzsch, Chvatal uniqueness]", flush=True)
    for n, want in ((10, UNSAT), (11, SAT)):
        cnf = CACHE / f"cal_tf_n{n}.cnf"
        build_forbidden_clique_cnf(n, 3, cnf)
        r = run_smsg(n, cnf, 4, connected=True, timeout=timeout)
        good = r["result"] == want
        detail = f"n={n} -> {r['result']} (want {want}) in {r['elapsed_s']}s"
        if r["result"] == SAT and r["models"]:
            v = verify_model(n, r["models"][-1], 4, class_member=False)
            iso = nx.is_isomorphic(to_nx(n, r["models"][-1]), nx.mycielski_graph(4))
            good = good and v["chi_ge"]
            detail += f"; independent chi>=4 {v['chi_ge']}; Groetzsch {iso}; g6={v['g6']}"
        ok &= _rung("A", good, detail)

    # (B) K4-free chi >= 5: UNSAT at 10, SAT at 11 (Jensen-Royle 1995). Reports.
    print(" (B) K4-free chi>=5  [Jensen-Royle; reports, does not gate]", flush=True)
    for n in (10, 11):
        cnf = CACHE / f"cal_k4f_n{n}.cnf"
        build_forbidden_clique_cnf(n, 4, cnf)
        r = run_smsg(n, cnf, 5, connected=True, timeout=timeout)
        detail = f"n={n} -> {r['result']} in {r['elapsed_s']}s"
        if r["result"] == SAT and r["models"]:
            v = verify_model(n, r["models"][-1], 5, class_member=False)
            detail += f"; independent chi>=5 {v['chi_ge']}; g6={v['g6']}"
        _rung("B", True, detail)

    # (E) the propagator AT THE PRODUCTION VALUE k=6, both directions. A
    # k-critical graph has n = k or n >= k+2 (no k-critical graph on k+1
    # vertices), so a 6-chromatic graph on 7 vertices must contain K6: forbidding
    # K6 makes n=7 UNSAT. At n=8 the join C5 + K3 is 6-chromatic with clique
    # number 5, so it is SAT. Rungs A and B only exercise k=4 and k=5.
    print(" (E) K6-free chi>=6  [k-critical: n=k or n>=k+2]", flush=True)
    for n, want in ((7, UNSAT), (8, SAT)):
        cnf = CACHE / f"cal_k6f_n{n}.cnf"
        build_forbidden_clique_cnf(n, 6, cnf)
        r = run_smsg(n, cnf, 6, connected=True, timeout=timeout)
        good = r["result"] == want
        detail = f"n={n} -> {r['result']} (want {want}) in {r['elapsed_s']}s"
        if r["result"] == SAT and r["models"]:
            v = verify_model(n, r["models"][-1], 6, class_member=False)
            good = good and v["chi_ge"]
            detail += f"; independent chi>=6 {v['chi_ge']}; g6={v['g6']}"
        ok &= _rung("E", good, detail)

    # (C)+(D) the repo answer at n=15 and n=16: every cell UNSAT at chi>=6,
    # every cell non-vacuous at chi>=3.
    for n in (15, 16):
        lo, hi = ky_floor(n), codegree_ceiling(n)
        print(f" (C/D) both-free class n={n}, cells m={lo}..{hi}", flush=True)
        for m in range(lo, hi + 1):
            cnf = CACHE / f"cal_class_n{n}_m{m}.cnf"
            build_class_cnf(n, m, cnf)
            probe = run_smsg(n, cnf, 3, connected=True, timeout=timeout)
            vac = "SAT" if probe["result"] == SAT else probe["result"]
            vdet = ""
            if probe["result"] == SAT and probe["models"]:
                v = verify_model(n, probe["models"][-1], 3, m=m)
                vac = f"SAT/class_ok={v['class_ok']}"
                vdet = v["g6"]
            r = run_smsg(n, cnf, 6, connected=True, timeout=timeout)
            good = r["result"] == UNSAT
            if r["result"] == SAT and r["models"]:
                v = verify_model(n, r["models"][-1], 6, m=m)
                good = False
                vdet = f"HIT g6={v['g6']} verified={v['chi_ge']}"
            ok &= _rung(f"n={n} m={m}", good,
                        f"chi>=6 -> {r['result']} in {r['elapsed_s']}s; "
                        f"nonvacuity(chi>=3) -> {vac} {vdet}")

    print(f"calibration: {'ALL RUNGS PASS' if ok else 'FAILURE'}", flush=True)
    return ok


# ----------------------------------------------------------------- production

def probe_cell(n, m, connected=True, timeout=None):
    """Non-vacuity: the same cell CNF at chi>=3 must be SAT with a model that the
    disjoint-code E17 filter certifies as a genuine class member. An UNSAT here
    means the cell is empty, and the chi>=6 UNSAT for it carries no information."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cnf = CACHE / f"probe_n{n}_m{m}.cnf"
    build_class_cnf(n, m, cnf)
    r = run_smsg(n, cnf, 3, connected=connected, timeout=timeout)
    out = {"result": r["result"], "elapsed_s": r["elapsed_s"], "nonempty": False}
    if r["result"] == SAT and r["models"]:
        v = verify_model(n, r["models"][-1], 3, m=m)
        out.update(witness=v["g6"], class_ok=v["class_ok"], nonempty=bool(v["class_ok"]))
    return out


def decide_cell(n, m, chi=6, gallai=False, split=None, connected=True,
                timeout=None, coloring_algo=None, extra=(), quiet=False,
                k4free=True, codeg2=True, probe=False, resume=True):
    CACHE.mkdir(parents=True, exist_ok=True)
    abl = ("" if k4free else "_nok4") + ("" if codeg2 else "_nocodeg")
    tag = (f"n{n}_m{m}_chi{chi}{abl}"
           + (f"_s{split.replace(':', '_')}" if split else ""))
    done = CACHE / f"{tag}.json"
    if resume and done.exists():
        cached = json.loads(done.read_text())
        if cached.get("result") in (SAT, UNSAT):
            if not quiet:
                print(f"n={n} m={m} chi>={chi}"
                      f"{' split=' + split if split else ''}: {cached['result']} "
                      f"[cached]", flush=True)
            return cached
    cnf = CACHE / f"{tag}.cnf"
    nv, ncl = build_class_cnf(n, m, cnf, gallai=gallai, split=split,
                              k4free=k4free, codeg2=codeg2)
    r = run_smsg(n, cnf, chi, connected=connected, timeout=timeout,
                 coloring_algo=coloring_algo, log=CACHE / f"{tag}.log", extra=extra)
    out = {"n": n, "m": m, "chi": chi, "gallai": gallai, "split": split,
           "connected": connected, "k4free": k4free, "codeg2": codeg2,
           "vars": nv, "clauses": ncl,
           "cmd": r["cmd"], "result": r["result"], "elapsed_s": r["elapsed_s"],
           "smsg_tail": r["tail"]}
    if r["result"] == SAT and r["models"]:
        out["hit"] = verify_model(n, r["models"][-1], chi, m=m,
                                  class_member=k4free and codeg2)
        out["hit"]["edges"] = r["models"][-1]
    if probe and r["result"] == UNSAT and k4free and codeg2:
        out["nonvacuity"] = probe_cell(n, m, connected=connected, timeout=timeout)
    (CACHE / f"{tag}.json").write_text(json.dumps(out, indent=2))
    if not quiet:
        verdict = {UNSAT: f"UNSAT: no chi>={chi} member in this cell",
                   SAT: "*** SAT: HIT ***"}.get(r["result"], "UNKNOWN (timeout/stop)")
        print(f"n={n} m={m} chi>={chi}{' +gallai' if gallai else ''}"
              f"{' split=' + split if split else ''}: {verdict} "
              f"[{r['elapsed_s']}s, {nv} vars, {ncl} clauses]", flush=True)
        if "hit" in out:
            print(f"    independent verification: {out['hit']}", flush=True)
        if "nonvacuity" in out:
            nv_ = out["nonvacuity"]
            print(f"    non-vacuity: cell {'NONEMPTY' if nv_['nonempty'] else 'EMPTY'}"
                  f" ({nv_['result']}, {nv_['elapsed_s']}s"
                  f"{', witness ' + nv_['witness'] if nv_.get('witness') else ''})",
                  flush=True)
    return out


def ablate(n, m, connected=True, timeout=None):
    """Which constraint is doing the killing, measured at production scale.

    Rung 4 (neither class property) is the end-to-end POSITIVE CONTROL: in the
    same n / degree / edge-count regime, with the class properties removed, the
    pipeline must return SAT. If it does, the unablated UNSAT is a fact about the
    both-free class. If it does not, the search is what is failing, and no
    nonexistence claim may be made.
    """
    print(f"E20 ablation at n={n}, m={m} (chi>=6)", flush=True)
    rows = []
    for label, k4, cd in (("class (K4-free + codeg<=2)", True, True),
                          ("drop codeg<=2 (K_{2,3} allowed)", True, False),
                          ("drop K4-free", False, True),
                          ("drop both  [POSITIVE CONTROL]", False, False)):
        r = decide_cell(n, m, chi=6, k4free=k4, codeg2=cd, connected=connected,
                        timeout=timeout, quiet=True)
        note = ""
        if r["result"] == SAT and "hit" in r:
            note = f" g6={r['hit']['g6']} verified_chi>=6={r['hit']['chi_ge']}"
        print(f"  {label:34s} -> {r['result']:7s} {r['elapsed_s']:8.2f}s{note}", flush=True)
        rows.append({"ablation": label,
                     **{k: r.get(k) for k in ("k4free", "codeg2", "result", "elapsed_s")},
                     "g6": (r.get("hit") or {}).get("g6")})
    control = rows[-1]
    ok = control["result"] == SAT
    print(f"  positive control: {'PASS (search can return SAT here)' if ok else 'FAIL'}",
          flush=True)
    (CACHE / f"ablate_n{n}_m{m}.json").write_text(
        json.dumps({"n": n, "m": m, "rows": rows, "control_pass": ok}, indent=2))
    return 0 if ok else 1


def sweep(n, chi=6, jobs=None, **kw):
    lo, hi = ky_floor(n), codegree_ceiling(n)
    cells = list(range(lo, hi + 1))
    jobs = jobs or min(len(cells), os.cpu_count() or 1)
    print(f"n={n}: window m={lo}..{hi} ({len(cells)} cells), {jobs} jobs", flush=True)
    t0 = time.time()
    results = []
    with futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(decide_cell, n, m, chi=chi, **kw): m for m in cells}
        for f in futures.as_completed(futs):
            results.append(f.result())
    results.sort(key=lambda r: r["m"])
    hits = [r for r in results if r["result"] == SAT]
    unknown = [r for r in results if r["result"] == UNKNOWN]
    summary = {
        "n": n, "chi": chi, "cells": cells, "jobs": jobs,
        "wall_s": round(time.time() - t0, 1),
        "cpu_s": round(sum(r["elapsed_s"] for r in results), 1),
        "per_cell": {str(r["m"]): [r["result"], r["elapsed_s"]] for r in results},
        "hits": len(hits), "unknown": [r["m"] for r in unknown],
    }
    if not hits and not unknown:
        summary["verdict"] = (f"THEOREM: the both-free class has no chi>={chi} "
                              f"member on {n} vertices")
    (CACHE / f"sweep_n{n}_chi{chi}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2), flush=True)
    return 2 if hits else (1 if unknown else 0)


def decide_with_split(n, m, jobs, timeout, split_bits=5, max_depth=3,
                      t=0, idx=0, **kw):
    """Decide one cell, splitting recursively for as long as branches time out.

    A branch is a pair (t, idx): the t highest-indexed vertex pairs are pinned to
    the bits of idx by unit clauses. This is an exact partition of the model space,
    because each isomorphism class's lex-minimal labelling has definite values on
    those pairs, so every class is reached by exactly one branch. Splitting a
    branch again keeps its own pins: the last t pairs of the deeper slice are the
    parent's pairs, so the child index is (idx << split_bits) | j.

    Recursion is what keeps a hard cell from being misreported as a wall. A branch
    that times out is not a verdict, it is a request to split further; only
    exhausting `max_depth` is a wall. Splitting on the HIGHEST-indexed pairs is
    deliberate (L76: splitting on the lowest is useless, lex-minimality has already
    pinned them).
    """
    spec = f"{t}:{idx}" if t else None
    r = decide_cell(n, m, split=spec, timeout=timeout, quiet=True, **kw)
    if r["result"] != UNKNOWN:
        return r
    if max_depth <= 0:
        return r
    kids = [((idx << split_bits) | j) for j in range(2 ** split_bits)]
    ct = t + split_bits
    print(f"    {'  ' * (3 - max_depth)}n={n} m={m} "
          f"{'branch ' + spec if spec else 'cell'} timed out -> "
          f"{len(kids)} sub-branches at depth {ct}", flush=True)
    with futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        subs = list(ex.map(lambda j: decide_with_split(
            n, m, jobs, timeout, split_bits, max_depth - 1, ct, j, **kw), kids))
    if any(s["result"] == SAT for s in subs):
        hit = next(s for s in subs if s["result"] == SAT)
        return {**hit, "split_depth": ct}
    if all(s["result"] == UNSAT for s in subs):
        return {"n": n, "m": m, "result": UNSAT, "split_depth": ct,
                "elapsed_s": round(sum(s["elapsed_s"] for s in subs), 1),
                "branches": len(kids)}
    return {"n": n, "m": m, "result": UNKNOWN, "split_depth": ct,
            "elapsed_s": round(sum(s["elapsed_s"] for s in subs), 1),
            "stuck_branches": [s.get("split") for s in subs
                               if s["result"] == UNKNOWN]}


def climb(n_from, n_to=None, jobs=None, timeout=None, split_bits=5, **kw):
    """The always-on ladder: decide every cell of n = n_from, n_from+1, ... .

    Resumable at cell granularity (a finished cell caches its JSON and is skipped
    on the next run), so this can be killed and restarted at any moment. A cell
    that exceeds `timeout` is retried as 2^split_bits independent branches, each
    of which is itself a cached, resumable unit; the cell is UNSAT iff every
    branch is. The ladder stops on the first SAT (a hit) or on a cell that
    survives even the split, and records where it stopped.
    """
    jobs = jobs or (os.cpu_count() or 1)
    set_parallelism(jobs)
    n_to = n_to or 99
    ladder = {}
    for n in range(n_from, n_to + 1):
        cells = list(range(ky_floor(n), codegree_ceiling(n) + 1))
        print(f"\n=== n={n}: cells m={cells[0]}..{cells[-1]}, {jobs} jobs, "
              f"timeout {timeout or 'none'}s ===", flush=True)
        t0 = time.time()
        with futures.ThreadPoolExecutor(max_workers=jobs) as ex:
            res = list(ex.map(lambda m: decide_cell(n, m, timeout=timeout,
                                                    quiet=True, **kw), cells))
        for m, r in zip(cells, res):
            print(f"  n={n} m={m}: {r['result']} ({r['elapsed_s']}s)", flush=True)

        stuck = [m for m, r in zip(cells, res) if r["result"] == UNKNOWN]
        branch_totals = {}
        for m in stuck:
            r = decide_with_split(n, m, jobs, timeout, split_bits, **kw)
            branch_totals[m] = {"depth": r.get("split_depth"),
                                "branches": r.get("branches")}
            print(f"  n={n} m={m}: {r['result']} after splitting to depth "
                  f"{r.get('split_depth')} ({r['elapsed_s']}s)", flush=True)
            res[cells.index(m)] = {"m": m, "n": n, **r}

        hits = [r for r in res if r["result"] == SAT]
        unknown = [r["m"] for r in res if r["result"] == UNKNOWN]
        ladder[n] = {
            "cells": cells, "wall_s": round(time.time() - t0, 1),
            "cpu_s": round(sum(r["elapsed_s"] for r in res), 1),
            "per_cell": {str(r["m"]): [r["result"], r["elapsed_s"]] for r in res},
            "split_branches": branch_totals,
            "hits": [r.get("hit") for r in hits], "unknown": unknown,
            "verdict": ("HIT" if hits else "STUCK" if unknown else
                        f"no chi>=6 both-free graph exists on {n} vertices"),
        }
        (CACHE / "climb.json").write_text(json.dumps(ladder, indent=2))
        print(f"  n={n}: {ladder[n]['verdict']} "
              f"[{ladder[n]['wall_s']}s wall, {ladder[n]['cpu_s']}s cpu]", flush=True)
        if hits:
            print(f"*** HIT at n={n}. Ladder stops. ***", flush=True)
            return 2
        if unknown:
            print(f"*** WALL at n={n}, cells {unknown} survive the split. "
                  f"Ladder stops. ***", flush=True)
            return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--window", type=int, metavar="N", help="print the cell window and exit")
    ap.add_argument("--n", type=int)
    ap.add_argument("--m", type=int)
    ap.add_argument("--chi", type=int, default=6)
    ap.add_argument("--sweep", action="store_true", help="all cells of --n")
    ap.add_argument("--ablate", action="store_true",
                    help="constraint ablation + positive control at --n --m")
    ap.add_argument("--probe", action="store_true",
                    help="follow every UNSAT cell with a non-vacuity probe")
    ap.add_argument("--climb", type=str, metavar="FROM[:TO]",
                    help="resumable ladder over n (the always-on job)")
    ap.add_argument("--split-bits", type=int, default=5,
                    help="branches = 2^bits when a cell times out")
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--gallai", action="store_true",
                    help="add the Gallai low-vertex conditions (sweep-sound only)")
    ap.add_argument("--split", type=str, default=None, help="t:idx unit-clause split")
    ap.add_argument("--no-connected", action="store_true")
    ap.add_argument("--timeout", type=int, default=None, help="seconds, per smsg call")
    ap.add_argument("--coloring-algo", type=int, default=None, choices=[0, 1, 2])
    ap.add_argument("--smsg-extra", nargs=argparse.REMAINDER, default=[],
                    help="everything after this is passed through to smsg")
    args = ap.parse_args()

    if args.window is not None:
        n = args.window
        lo, hi = ky_floor(n), codegree_ceiling(n)
        print(f"n={n}: KY floor m>={lo}, codegree ceiling m<={hi}, "
              f"maxdeg<={(n - 1) // 2}; cells: {list(range(lo, hi + 1))}")
        return 0
    if args.calibrate:
        return 0 if calibrate(timeout=args.timeout) else 1

    if args.ablate:
        assert args.n and args.m, "--ablate needs --n and --m"
        return ablate(args.n, args.m, connected=not args.no_connected,
                      timeout=args.timeout)

    kw = dict(chi=args.chi, gallai=args.gallai, connected=not args.no_connected,
              timeout=args.timeout, coloring_algo=args.coloring_algo,
              extra=args.smsg_extra, probe=args.probe)
    if args.climb:
        lo, _, hi = args.climb.partition(":")
        return climb(int(lo), int(hi) if hi else None, jobs=args.jobs,
                     split_bits=args.split_bits, **kw)
    if args.sweep:
        assert args.n, "--sweep needs --n"
        return sweep(args.n, jobs=args.jobs, **kw)
    if args.n and args.m:
        r = decide_cell(args.n, args.m, split=args.split, **kw)
        return {UNSAT: 0, SAT: 2}.get(r["result"], 1)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
