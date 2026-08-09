r"""Compare the two independent enumerations of the n=16 both-free cell.

Side A: `geng_hn` (canonical augmentation), the E17/L75 method, rerun here on a
different OS and compiler.
Side B: `e18_enumerate` (CDCL + blocking clauses + external isomorph rejection),
a different algorithm and a different code base.

The comparison is class-by-class, not just count-by-count: both sides are bucketed
by Weisfeiler-Lehman hash and matched exactly inside each bucket, so a coincidence
of totals cannot pass. Any graph present on one side and absent on the other is
reported explicitly -- that asymmetry is exactly what L75's caveat (i) is about.

Usage: python -m experiments.combinatorial.e18_n16_compare
"""
from __future__ import annotations

import glob
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                   # noqa: E402

from e17_bothfree_filter import (graph6_to_adj,         # noqa: E402
                                 is_k4_free, is_k23_free)

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e18"


def load_g6_file(path):
    out = []
    for line in pathlib.Path(path).read_text().split():
        line = line.strip()
        if line:
            out.append(line)
    return out


def g6_to_graph(g6):
    n, adj = graph6_to_adj(g6)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((i, j) for i, j in itertools.combinations(range(n), 2)
                     if (adj[i] >> j) & 1)
    return g


def bucket(graphs):
    b = {}
    for g6, g in graphs:
        b.setdefault(nx.weisfeiler_lehman_graph_hash(g, iterations=4), []).append((g6, g))
    return b


def match(a_bucket, b_bucket):
    """Return (matched, only_a, only_b) counting isomorphism classes."""
    matched, only_a, only_b = 0, [], []
    for h, items in a_bucket.items():
        others = b_bucket.get(h, [])
        used = set()
        for g6, g in items:
            hit = None
            for idx, (_, g2) in enumerate(others):
                if idx not in used and nx.is_isomorphic(g, g2):
                    hit = idx
                    break
            if hit is None:
                only_a.append(g6)
            else:
                used.add(hit)
                matched += 1
        for idx, (g62, _) in enumerate(others):
            if idx not in used:
                only_b.append(g62)
    for h, items in b_bucket.items():
        if h not in a_bucket:
            only_b.extend(g6 for g6, _ in items)
    return matched, only_a, only_b


def main():
    geng_path = CACHE / "n16_geng_all.g6"
    if not geng_path.exists():
        parts = sorted(glob.glob(str(CACHE / "n16_geng_*.g6")))
        text = "\n".join(pathlib.Path(p).read_text().strip() for p in parts if
                         pathlib.Path(p).read_text().strip())
        geng_path.write_text(text + "\n")

    geng_g6 = load_g6_file(geng_path)

    # Prefer the deduplicated class list from e18_merge. The raw per-job output
    # is NOT isomorph-free: branches partition the model space, so the same class
    # legitimately appears in several branch files, and comparing raw output
    # would report those duplicates as spurious "only in SAT" entries.
    merged = CACHE / "n16_sat_classes.g6"
    if merged.exists():
        sat_g6 = load_g6_file(merged)
        summary = CACHE / "n16_merge_summary.json"
        if summary.exists():
            s = json.loads(summary.read_text())
            if not s.get("complete"):
                print("  NOTE: the SAT census is PARTIAL (not every cell has been "
                      "proved exhausted); missing classes are expected as 'only in geng'")
    else:
        sat_g6 = []
        for p in sorted(glob.glob(str(CACHE / "enum_n16_m*.json"))):
            d = json.loads(pathlib.Path(p).read_text())
            if not d.get("exhausted"):
                print(f"  WARNING: {pathlib.Path(p).name} did not exhaust its cell "
                      f"({d['models']} models, budget hit) -- comparison is partial")
            sat_g6.extend(d.get("g6", []))

    print(f"geng side: {len(geng_g6)} graphs")
    print(f"SAT  side: {len(sat_g6)} graphs")

    geng_graphs = [(s, g6_to_graph(s)) for s in geng_g6]
    sat_graphs = [(s, g6_to_graph(s)) for s in sat_g6]

    # Independent property re-check of both sides (disjoint code from either
    # enumerator): every graph must actually be in the class.
    bad = []
    for tag, coll in (("geng", geng_g6), ("sat", sat_g6)):
        for s in coll:
            n, adj = graph6_to_adj(s)
            degs = [bin(a).count("1") for a in adj]
            if not (is_k4_free(n, adj) and is_k23_free(n, adj)
                    and min(degs) >= 5 and max(degs) <= 7 and 43 <= sum(degs) // 2 <= 48):
                bad.append((tag, s))
    print(f"property re-check: {len(bad)} violations "
          f"{'(clean)' if not bad else bad[:5]}")

    matched, only_geng, only_sat = match(bucket(geng_graphs), bucket(sat_graphs))
    print(f"\nmatched classes : {matched}")
    print(f"only in geng    : {len(only_geng)}")
    print(f"only in SAT     : {len(only_sat)}")
    # Distinguish the two ways this can fail to be a clean AGREE. A class the SAT
    # side produced that geng does not have, or a property violation, is a real
    # CONTRADICTION between the two methods. A class geng has that the SAT side
    # lacks, while the SAT census is still partial, is merely missing coverage --
    # it says nothing against either method.
    contradiction = bool(only_sat) or bool(bad)
    agree = not only_geng and not contradiction
    if agree:
        verdict = "AGREE (independent enumerations identical)"
    elif contradiction:
        verdict = "DISAGREE (contradiction: SAT produced a class geng does not have)"
    else:
        verdict = (f"CONSISTENT, PARTIAL: no contradictions, but {len(only_geng)} "
                   f"geng classes are not yet covered by the SAT side")
    print(f"\nVERDICT: {verdict}")

    (CACHE / "n16_compare.json").write_text(json.dumps({
        "geng_count": len(geng_g6), "sat_count": len(sat_g6),
        "matched": matched, "only_geng": only_geng[:200],
        "only_sat": only_sat[:200], "property_violations": len(bad),
        "agree": agree,
    }, indent=2))
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main())
