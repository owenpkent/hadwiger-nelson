r"""Vertex-criticality scan of the chi-5 lineage (L58 Essential-Pair follow-up).

Essential-Pair Lemma (L58): a forced non-adjacent pair (s,t) in a 5-chromatic G
requires chi(G-s) >= 5 AND chi(G-t) >= 5. So vertex-critical chi-5 graphs host
no forced pairs of any kind, and only chi-redundant vertices (chi(G-v) = 5) can
be clamp endpoints.

This scan decides, for each of the 9 chi-5 lineage graphs (P510 already proven
vertex-critical in L26; rechecked here as a control), whether ANY vertex is
chi-redundant: for every v, SAT-test 4-colorability of G - v.
  SAT   => chi(G-v) <= 4 => v is critical-at (deleting it loses 5-chromaticity)
  UNSAT => chi(G-v)  = 5 => v is REDUNDANT (a potential clamp endpoint)

Zero redundant vertices across the nine => L57's exhaustive freeness was
predetermined by the lineage's minimization toward criticality. Any redundant
vertex localizes where forcing could have lived (L57 already says it didn't).

Checkpointed per graph under _cache/critscan/; resumable.
"""
from __future__ import annotations
import sys, pathlib, json, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import parse_vtx, parse_edges, sat_kcolor, CACHE, VTX, EDGE
from pysat.solvers import Cadical195

GRAPHS = ["510", "517", "529", "553", "610", "633", "803", "826", "874"]
BUDGET = 1_000_000
OUT = CACHE / "critscan"
OUT.mkdir(parents=True, exist_ok=True)


def scan(name):
    base = parse_vtx(VTX / f"{name}.vtx")
    edges = parse_edges(EDGE / f"{name}.edge")
    n = len(base)
    eset = set((min(u, v), max(u, v)) for (u, v) in edges)
    ck = OUT / f"{name}.json"
    done = json.loads(ck.read_text()) if ck.exists() else {}
    t0 = time.time()
    for v in range(n):
        key = str(v)
        if key in done:
            continue
        # deleting v = dropping its edges; the leftover isolated vertex is
        # colorable with any color, so it cannot affect satisfiability
        sub = [(u, w) for (u, w) in eset if u != v and w != v]
        res, _ = sat_kcolor(n, sub, 4, Cadical195, budget_conflicts=BUDGET)
        done[key] = "critical" if res is True else ("REDUNDANT" if res is False else "indeterminate")
        if done[key] != "critical":
            print(f"!!! {name} v={v}: {done[key]}", flush=True)
        if v % 50 == 0:
            ck.write_text(json.dumps(done))
            print(f"{name}: {v + 1}/{n} ({time.time() - t0:.0f}s)", flush=True)
    ck.write_text(json.dumps(done))
    red = [int(k) for k, s in done.items() if s == "REDUNDANT"]
    ind = [int(k) for k, s in done.items() if s == "indeterminate"]
    return {"n": n, "redundant": sorted(red), "indeterminate": sorted(ind),
            "vertex_critical": not red and not ind, "secs": round(time.time() - t0, 1)}


def main():
    summary = {}
    for name in GRAPHS:
        print(f"=== {name} ===", flush=True)
        summary[name] = scan(name)
        print(f"{name}: {summary[name]}", flush=True)
        (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2))
    print("DONE", json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
