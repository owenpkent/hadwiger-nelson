r"""E18 follow-up: close a both-free cell with SAT MODULO SYMMETRIES (smsg).

Why this exists. The E18 blocking-clause enumerator measured its own wall: it
dies at ~$10^5$ blocking clauses per solver regardless of how the cell is split,
because the lex-leader symmetry break leaves ~250-370 labelled copies of each
isomorphism class to be blocked one at a time. The fix named in
`e18_results.md` is an enumerator that never emits duplicate labellings:
SAT modulo symmetries (Kirchweger-Szeider), which does canonicity checking
INSIDE the CDCL solver via a lazily-refined minimality propagator. This module
drives `smsg` over the exact same class CNF and closes the one outstanding cell
($n=16$, $m=43$).

Soundness structure, and what is reused vs independent:

  * The CNF is built by the SAME `CriticalEncoding` used by `e18_enumerate`
    (K4-free, codegree <= 2, delta >= 5, maxdeg cap, edge count pinned), with NO
    lex-leader symmetry breaking: SMS supplies the symmetry handling. The
    encoding was already relaxation-gated (11/11 known class members accepted).
  * Variable-order compatibility is ASSERTED, not assumed: smsg expects the
    edge variable for pair (i, j), i < j, at DIMACS index 1 + rank of (i, j) in
    lexicographic pair order, which is exactly the order `CriticalEncoding`
    allocates them; the assertion fails loudly if either side ever changes.
  * SMS minimality clauses only ever EXCLUDE non-lex-minimal labellings, so no
    isomorphism class can be lost; with the default cutoff the check is
    incomplete per call and duplicates may be EMITTED, which is harmless here
    because isomorph rejection (WL hash + exact test, same as `e18_enumerate`)
    runs downstream anyway.
  * Every emitted graph is re-verified by the disjoint-code E17 filter, and
    biconnectivity is post-filtered exactly as in `e18_enumerate` (geng ran -C).
  * "Cell exhausted" means smsg terminated with final `Result: 20` (UNSAT after
    the last solution was blocked), not a timeout or budget stop.

Usage:
    python -m experiments.combinatorial.e18_sms_cell --n 15 --m 41
    python -m experiments.combinatorial.e18_sms_cell --n 16 --m 43 --write-enum-json
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

import networkx as nx                                   # noqa: E402

from e17_bothfree_filter import is_k4_free, is_k23_free  # noqa: E402
from e18_gallai import CriticalEncoding                  # noqa: E402
from e18_sat_class import adj_from_edges                 # noqa: E402
from e18_enumerate import Canon, to_nx                   # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e18"

SMSG_DEFAULT = pathlib.Path.home() / ".local" / "src" / "sat-modulo-symmetries" / "build" / "src" / "smsg.exe"
# smsg is a ucrt64 binary; its DLLs must be on PATH when spawned from outside msys.
UCRT64_BIN = r"C:\Tools\msys\ucrt64\bin"


def build_dimacs(n, m, maxdeg, path):
    """The e18 cell CNF (no Gallai, no symmetry breaking), as a DIMACS file whose
    first C(n,2) variables are the edge variables in smsg's expected order."""
    enc = CriticalEncoding(n, k=6, gallai_cyc=False, gallai_loc=False,
                           min_edges=m, max_edges=m, maxdeg=maxdeg,
                           symbreak=False, symbreak_all=False)
    pairs = list(itertools.combinations(range(n), 2))
    for rank, (i, j) in enumerate(pairs):
        assert enc.var(i, j) == rank + 1, (
            f"edge-variable order mismatch at ({i},{j}): got {enc.var(i, j)}, "
            f"smsg expects {rank + 1}")
    with open(path, "w") as f:
        f.write(f"p cnf {enc.cnf.nv} {len(enc.cnf.clauses)}\n")
        for cl in enc.cnf.clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    return enc.cnf.nv, len(enc.cnf.clauses)


def run_smsg(smsg, n, dimacs, cutoff, timeout_s, log_path):
    env = dict(os.environ)
    if os.name == "nt":
        env["PATH"] = UCRT64_BIN + os.pathsep + env.get("PATH", "")
    cmd = [str(smsg), "-v", str(n), "--all-graphs", "--dimacs", str(dimacs)]
    if cutoff is not None:
        cmd += ["--cutoff", str(cutoff)]
    if timeout_s:
        cmd += ["--timeout", str(timeout_s)]
    t0 = time.time()
    edges_per_model, exhausted, tail = [], False, []
    with open(log_path, "w") as log, subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, env=env, bufsize=1) as p:
        for line in p.stdout:
            log.write(line)
            s = line.strip()
            if s.startswith("[") and s.endswith("]"):
                edges_per_model.append(ast.literal_eval(s) if s != "[]" else [])
            else:
                tail.append(s)
                if s.startswith("Result:"):
                    exhausted = (s.split()[-1] == "20")
    return {
        "cmd": " ".join(cmd), "returncode": p.returncode,
        "models": edges_per_model, "exhausted": exhausted,
        "elapsed_s": round(time.time() - t0, 1),
        "tail": [t for t in tail if t][-15:],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--maxdeg", type=int, default=None,
                    help="default (n-1)//2, the proved class cap")
    ap.add_argument("--smsg", default=str(SMSG_DEFAULT))
    ap.add_argument("--cutoff", type=int, default=None,
                    help="smsg minimality-check cutoff (0 = complete check)")
    ap.add_argument("--timeout", type=int, default=None, help="seconds")
    ap.add_argument("--write-enum-json", action="store_true",
                    help="on EXHAUSTED, write _cache/e18/enum_n{n}_m{m}.json in "
                         "the e18_merge schema (only for the outstanding cell)")
    args = ap.parse_args()

    n, m = args.n, args.m
    maxdeg = args.maxdeg if args.maxdeg is not None else (n - 1) // 2
    CACHE.mkdir(parents=True, exist_ok=True)
    dimacs = CACHE / f"sms_n{n}_m{m}.cnf"
    log_path = CACHE / f"sms_n{n}_m{m}.log"

    nv, ncl = build_dimacs(n, m, maxdeg, dimacs)
    print(f"n={n} m={m} maxdeg={maxdeg}: CNF vars={nv} clauses={ncl} "
          f"(no symmetry breaking; SMS owns symmetries)", flush=True)

    r = run_smsg(args.smsg, n, dimacs, args.cutoff, args.timeout, log_path)
    print(f"smsg: {len(r['models'])} solutions emitted, "
          f"exhausted={r['exhausted']}, {r['elapsed_s']}s", flush=True)

    canon = Canon()
    bad, non_biconn = [], 0
    for edges in r["models"]:
        adj = adj_from_edges(n, edges)
        degs = [bin(a).count("1") for a in adj]
        if not (is_k4_free(n, adj) and is_k23_free(n, adj)
                and min(degs) >= 5 and max(degs) <= maxdeg and len(edges) == m):
            bad.append(edges)
            continue
        g = to_nx(n, edges)
        if nx.is_biconnected(g):
            canon.add(g)
        else:
            non_biconn += 1

    print(f"independent property re-check: {len(bad)} violations "
          f"{'(clean)' if not bad else '(FAIL)'}")
    print(f"biconnectivity post-filter: {non_biconn} dropped")
    print(f"isomorphism classes: {canon.count}")

    out = {
        "n": n, "m": m, "split": None, "gallai": False, "require_2conn": True,
        "method": "sms", "smsg_cmd": r["cmd"], "cutoff": args.cutoff,
        "models": len(r["models"]), "classes": canon.count,
        "exhausted": r["exhausted"] and not bad,
        "property_violations": len(bad), "non_biconnected_dropped": non_biconn,
        "g6": [nx.to_graph6_bytes(g, header=False).decode().strip()
               for g in canon.graphs()],
        "elapsed_s": r["elapsed_s"],
        "models_per_class": round(len(r["models"]) / canon.count, 1) if canon.count else None,
        "smsg_tail": r["tail"],
    }
    sms_json = CACHE / f"sms_n{n}_m{m}.json"
    sms_json.write_text(json.dumps(out, indent=2))
    print(f"wrote {sms_json}")

    if args.write_enum_json:
        if out["exhausted"]:
            enum_json = CACHE / f"enum_n{n}_m{m}.json"
            enum_json.write_text(json.dumps(out, indent=2))
            print(f"wrote {enum_json} (cell counts as covered for e18_merge)")
        else:
            print("NOT writing enum json: cell not exhausted "
                  "(timeout/violations), do not let merge read it as covered")
    status = "EXHAUSTED (cell complete)" if out["exhausted"] else "PARTIAL"
    print(f"n={n} m={m}: {out['models']} SMS solutions -> {out['classes']} "
          f"classes  [{status}]")
    return 0 if out["exhausted"] else 1


if __name__ == "__main__":
    sys.exit(main())
