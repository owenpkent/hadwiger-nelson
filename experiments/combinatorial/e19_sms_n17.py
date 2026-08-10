r"""E19: the $n=17$ door, attacked from the SAT side with SAT modulo symmetries.

L75 measured the geng wall at $n=17$ ($>80$ cpu-days of canonical augmentation on
this host) and L76/L77 built and validated the tool that removes the SAT side's
own wall (the blocking tail): `smsg` emits one model per isomorphism class with
in-solver canonicity checking, at ~230 classes/s on the $n=16$ census. This
module asks whether that rate survives at $n=17$, and if it does, runs the full
window: every emitted graph is colored ON THE FLY (DSATUR, then the SAT
portfolio for the residue), so the theorem-relevant verdict ("does the class
contain a $\chi \ge 6$ member at $n=17$?") accumulates as the enumeration runs.

Design differences from `e18_sms_cell.py`, both forced by scale:

  * STREAMING: nothing per-graph is kept in memory. Accepted graphs append to a
    .g6 stream file; only DSATUR-residue graphs and (loudly) any hits are
    recorded individually. No isomorph dedupe runs inline -- completeness, not
    distinctness, is what the verdict needs, and SMS near-eliminates duplicates
    anyway (exact class counts can be recovered later from the .g6 streams).
  * SPLIT: `--split t:idx` pins the t highest-indexed vertex pairs to the bits
    of idx via unit clauses, partitioning the model space exactly as
    `e18_enumerate` did, in case a cell outgrows one solver after all.

Soundness: the cell CNF is the same relaxation-gated `CriticalEncoding`
(K4-free, codegree <= 2, delta >= 5, maxdeg <= 8, m pinned), no lex-leader
clauses; SMS minimality clauses only exclude non-canonical labellings, so no
isomorphism class is lost. Every emitted graph is re-verified by the
disjoint-code E17 filter before coloring. "Exhausted" = smsg's final result is
UNSAT, not a timeout.

Usage:
    python -m experiments.combinatorial.e19_sms_n17 --m 52
    python -m experiments.combinatorial.e19_sms_n17 --m 46 --split 4:0
    python -m experiments.combinatorial.e19_sms_n17 --window   # print the cells
"""
from __future__ import annotations

import argparse
import ast
import itertools
import json
import os
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                        # noqa: E402

from e17_bothfree_filter import is_k4_free, is_k23_free      # noqa: E402
from e18_gallai import CriticalEncoding, ky_floor, codegree_ceiling  # noqa: E402
from e18_sat_class import adj_from_edges                     # noqa: E402
from e18_enumerate import to_nx                              # noqa: E402
from experiments._shared.portfolio_sat import solve_color    # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e19"

SMSG_DEFAULT = pathlib.Path.home() / ".local" / "src" / "sat-modulo-symmetries" / "build" / "src" / "smsg.exe"
UCRT64_BIN = r"C:\Tools\msys\ucrt64\bin"

N = 17


def build_dimacs(m, path, split=None):
    maxdeg = (N - 1) // 2
    enc = CriticalEncoding(N, k=6, gallai_cyc=False, gallai_loc=False,
                           min_edges=m, max_edges=m, maxdeg=maxdeg,
                           symbreak=False, symbreak_all=False)
    pairs = list(itertools.combinations(range(N), 2))
    for rank, (i, j) in enumerate(pairs):
        assert enc.var(i, j) == rank + 1, "edge-variable order mismatch"
    units = []
    if split:
        t, idx = [int(x) for x in split.split(":")]
        for b, (i, j) in enumerate(pairs[-t:]):
            units.append([enc.var(i, j) if (idx >> b) & 1 else -enc.var(i, j)])
    with open(path, "w") as f:
        f.write(f"p cnf {enc.cnf.nv} {len(enc.cnf.clauses) + len(units)}\n")
        for cl in enc.cnf.clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
        for cl in units:
            f.write(f"{cl[0]} 0\n")
    return enc.cnf.nv, len(enc.cnf.clauses) + len(units)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--m", type=int)
    ap.add_argument("--split", type=str, default=None, help="t:idx")
    ap.add_argument("--smsg", default=str(SMSG_DEFAULT))
    ap.add_argument("--cutoff", type=int, default=None)
    ap.add_argument("--timeout", type=int, default=None, help="seconds for smsg")
    ap.add_argument("--window", action="store_true", help="print the cell window and exit")
    ap.add_argument("--report-every", type=int, default=5000)
    args = ap.parse_args()

    lo, hi = ky_floor(N), codegree_ceiling(N)
    if args.window or args.m is None:
        print(f"n={N}: KY floor m>={lo}, codegree ceiling m<={hi}, "
              f"maxdeg<={(N - 1) // 2}; cells: {list(range(lo, hi + 1))}")
        if args.window:
            return 0
        return 1
    m = args.m
    assert lo <= m <= hi, f"m={m} outside window [{lo},{hi}]"

    CACHE.mkdir(parents=True, exist_ok=True)
    tag = f"n{N}_m{m}" + (f"_s{args.split.replace(':', '_')}" if args.split else "")
    dimacs = CACHE / f"sms_{tag}.cnf"
    g6_stream = CACHE / f"sms_{tag}.g6"
    residue_path = CACHE / f"sms_{tag}_residue.jsonl"
    hits_path = CACHE / f"sms_{tag}_HITS.jsonl"
    summary_path = CACHE / f"sms_{tag}.json"

    nv, ncl = build_dimacs(m, dimacs, args.split)
    print(f"n={N} m={m} split={args.split}: CNF vars={nv} clauses={ncl}", flush=True)

    env = dict(os.environ)
    if os.name == "nt":
        env["PATH"] = UCRT64_BIN + os.pathsep + env.get("PATH", "")
    cmd = [str(args.smsg), "-v", str(N), "--all-graphs", "--dimacs", str(dimacs)]
    if args.cutoff is not None:
        cmd += ["--cutoff", str(args.cutoff)]
    if args.timeout:
        cmd += ["--timeout", str(args.timeout)]

    t0 = time.time()
    models = bad = non_biconn = dsatur_ok = sat_ok = hits = 0
    exhausted = False
    tail = []
    with open(g6_stream, "w") as g6f, open(residue_path, "w") as resf, \
         open(hits_path, "w") as hitf, subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, env=env, bufsize=1) as p:
        for line in p.stdout:
            s = line.strip()
            if not (s.startswith("[") and s.endswith("]")):
                tail.append(s)
                if s.startswith("Result:"):
                    exhausted = (s.split()[-1] == "20")
                continue
            edges = ast.literal_eval(s) if s != "[]" else []
            models += 1
            adj = adj_from_edges(N, edges)
            degs = [bin(a).count("1") for a in adj]
            if not (is_k4_free(N, adj) and is_k23_free(N, adj)
                    and min(degs) >= 5 and max(degs) <= (N - 1) // 2
                    and len(edges) == m):
                bad += 1
                continue
            g = to_nx(N, edges)
            if not nx.is_biconnected(g):
                non_biconn += 1
                continue
            g6 = nx.to_graph6_bytes(g, header=False).decode().strip()
            g6f.write(g6 + "\n")
            k = max(nx.coloring.greedy_color(g, strategy="DSATUR").values()) + 1
            if k <= 5:
                dsatur_ok += 1
            else:
                res = solve_color(N, edges, 5, symbreak=True)["result"]
                if res:
                    sat_ok += 1
                    resf.write(json.dumps({"g6": g6, "dsatur": k, "chi_le5": True}) + "\n")
                    resf.flush()
                else:
                    hits += 1
                    hitf.write(json.dumps({"g6": g6, "dsatur": k,
                                           "result": res}) + "\n")
                    hitf.flush()
                    print(f"  *** HIT: chi>=6 candidate (result={res}), g6={g6} ***",
                          flush=True)
            if args.report_every and models % args.report_every == 0:
                el = time.time() - t0
                print(f"    {models} models, {dsatur_ok}+{sat_ok} colored, "
                      f"{hits} hits, {el:.0f}s ({models / el:.0f}/s)", flush=True)

    out = {
        "n": N, "m": m, "split": args.split, "method": "sms",
        "cmd": " ".join(cmd), "models": models, "property_violations": bad,
        "non_biconnected_dropped": non_biconn, "dsatur_ok": dsatur_ok,
        "sat_ok": sat_ok, "hits": hits, "exhausted": exhausted,
        "elapsed_s": round(time.time() - t0, 1),
        "smsg_tail": [t for t in tail if t][-12:],
    }
    summary_path.write_text(json.dumps(out, indent=2))
    status = "EXHAUSTED" if exhausted else "PARTIAL (timeout/stop)"
    print(f"n={N} m={m} split={args.split}: {models} models "
          f"({bad} violations, {non_biconn} non-biconnected), "
          f"{dsatur_ok} DSATUR + {sat_ok} SAT 5-colorable, {hits} HITS "
          f"[{status}] {out['elapsed_s']}s", flush=True)
    return 0 if (exhausted and hits == 0 and bad == 0) else (2 if hits else 1)


if __name__ == "__main__":
    sys.exit(main())
