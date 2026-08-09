r"""Merge the E18 n=16 SAT enumeration into one isomorph-free class list.

The cell was enumerated as several independent jobs: one per edge count m, and
for the dominant cell m=43 an additional 8-way branch split on the three
highest-indexed vertex pairs. Branches partition the MODEL space, not the
isomorphism-class space, so the same class can be found in several branches and
the union has to be deduplicated by isomorphism before it means anything.

Completeness bookkeeping is explicit: a cell counts as covered only if its job
reported EXHAUSTED, and for m=43 only if every one of its 8 branches did. The
output records which cells are complete, so a partial run can never be read as a
finished census.

Usage: python -m experiments.combinatorial.e18_merge
"""
from __future__ import annotations

import argparse
import glob
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                   # noqa: E402

from e17_bothfree_filter import graph6_to_adj           # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e18"


def g6_to_graph(g6):
    n, adj = graph6_to_adj(g6)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((i, j) for i, j in itertools.combinations(range(n), 2)
                     if (adj[i] >> j) & 1)
    return g


def dedupe(g6s):
    buckets, out = {}, []
    for s in g6s:
        g = g6_to_graph(s)
        h = nx.weisfeiler_lehman_graph_hash(g, iterations=4)
        if any(nx.is_isomorphic(g, o) for o in buckets.setdefault(h, [])):
            continue
        buckets[h].append(g)
        out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(CACHE / "n16_sat_classes.g6"))
    args = ap.parse_args()

    per_cell, raw, incomplete = {}, [], []
    for p in sorted(glob.glob(str(CACHE / "enum_n16_m*.json"))):
        name = pathlib.Path(p).stem
        d = json.loads(pathlib.Path(p).read_text())
        per_cell[name] = {"classes": d.get("classes"), "models": d.get("models"),
                          "exhausted": d.get("exhausted")}
        if not d.get("exhausted"):
            incomplete.append(name)
        raw.extend(d.get("g6", []))

    # A cell counts as covered if EITHER its single unsplit job exhausted OR all 8
    # of its branches did. Both m=43 and m=44 were branch-split mid-run, and their
    # unsplit jobs were retired once the branches overtook them, so neither writes
    # a JSON; coverage has to be judged per m rather than per file.
    coverage = {}
    for m in (43, 44, 45, 46, 47, 48):
        single = per_cell.get(f"enum_n16_m{m}", {}).get("exhausted", False)
        branches = [per_cell[k]["exhausted"] for k in per_cell
                    if k.startswith(f"enum_n16_m{m}_s")]
        coverage[m] = (single or (len(branches) == 8 and all(branches)),
                       single, sum(1 for b in branches if b), len(branches))
    m43_ok = coverage[43][0]
    others_ok = all(coverage[m][0] for m in (44, 45, 46, 47, 48))

    print(f"raw graphs from {len(per_cell)} jobs: {len(raw)}")
    classes = dedupe(raw)
    print(f"after isomorph dedupe: {len(classes)} classes")
    for k in sorted(per_cell):
        c = per_cell[k]
        print(f"  {k:24s} classes={c['classes']:>6} models={c['models']:>8} "
              f"exhausted={c['exhausted']}")

    complete = m43_ok and others_ok
    print()
    for m in (43, 44, 45, 46, 47, 48):
        ok, single, done, total = coverage[m]
        # `total` counts branch JSONs WRITTEN so far, so report against the 8
        # branches a split cell actually has; otherwise "2/2" reads as complete.
        how = f"unsplit={single}" if not total else f"branches={done}/8"
        print(f"  m={m}: covered={ok} ({how})")
    print(f"CENSUS COMPLETE: {complete}"
          f"{'' if complete else '  -- partial, do not read as a finished census'}")

    pathlib.Path(args.out).write_text("\n".join(classes) + "\n")
    (CACHE / "n16_merge_summary.json").write_text(json.dumps({
        "raw": len(raw), "classes": len(classes), "complete": complete,
        "m43_covered": m43_ok, "others_covered": others_ok,
        "coverage": {str(m): coverage[m][0] for m in coverage},
        "incomplete_jobs": incomplete, "per_cell": per_cell,
    }, indent=2))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
