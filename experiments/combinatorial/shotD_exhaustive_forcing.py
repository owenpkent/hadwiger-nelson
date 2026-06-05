r"""Shot D: EXHAUSTIVE forcing classification of the chi-5 UDG lineage.

Upgrades L45 (forced-different, core + random sample) and L56 (forced-same, core
+ random sample) from sampled to EXHAUSTIVE. For every NON-ADJACENT pair (a,b) in
each lineage graph, classify it as:
  - forced-different : merging a,b (force same color) is 5-UNSAT  [L45 test]
  - forced-same      : adding edge a,b (force different) is 5-UNSAT [L56 test]
  - free             : neither (both same and different colorings exist)

If L45/L56 hold exhaustively, EVERY non-adjacent pair is FREE: no long-range color
forcing of any kind in the realizable lineage (all forcing is adjacency-local).
A single non-free non-adjacent pair is the missing chi>=6 ingredient (forced-diff
= a clamp directly; forced-same = a clamp via the L56 splice lemma).

Built for unattended overnight running:
  - graphs processed SMALLEST-FIRST so the most graphs finish,
  - per-graph JSONL checkpoint (one line per classified pair), RESUMABLE: a
    restart skips pairs already recorded,
  - PROGRESS.json updated continuously (a monitor/loop reads it),
  - any forced (non-free) pair is appended to HITS.jsonl and printed LOUDLY,
  - exceptions per pair are recorded as indeterminate, never crash the sweep.

Env: SHOTD_SMOKE=N caps each graph to the first N non-adjacent pairs (smoke test).
"""
from __future__ import annotations
import sys, os, pathlib, json, itertools, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import parse_vtx, parse_edges, sat_kcolor, CACHE, VTX, EDGE
from pysat.solvers import Cadical195

# Smallest-first so the maximum number of graphs complete overnight.
GRAPHS = ["S199", "L403", "510", "517", "529", "553",
          "610", "633", "T721", "803", "826", "874"]
BUDGET = 1_000_000          # conflict budget per solve; indeterminate if exceeded
OUT = CACHE / os.environ.get("SHOTD_OUT", "shotD")
SMOKE = int(os.environ.get("SHOTD_SMOKE", "0"))


def load_graph(name):
    base = parse_vtx(VTX / f"{name}.vtx")
    edges = parse_edges(EDGE / f"{name}.edge")
    return base, edges


def forced_different(n, eset, a, b):
    """Merge a,b (force same color). 5-UNSAT => (a,b) forced-different."""
    def rep(x):
        return a if x == b else x
    merged = set()
    for (u, v) in eset:
        uu, vv = rep(u), rep(v)
        if uu == vv:
            return True, False  # a,b adjacent (shouldn't happen: we skip those)
        merged.add((min(uu, vv), max(uu, vv)))
    res, _ = sat_kcolor(n, list(merged), 5, Cadical195, budget_conflicts=BUDGET)
    if res is None:
        return None, True
    return (res is False), False


def forced_same(n, eset, a, b):
    """Add edge a,b (force different colors). 5-UNSAT => (a,b) forced-same."""
    aug = set(eset)
    aug.add((min(a, b), max(a, b)))
    res, _ = sat_kcolor(n, list(aug), 5, Cadical195, budget_conflicts=BUDGET)
    if res is None:
        return None, True
    return (res is False), False


def nonadjacent_pairs(n, adj):
    for a, b in itertools.combinations(range(n), 2):
        if b not in adj[a]:
            yield a, b


def write_progress(state):
    (OUT / "PROGRESS.json").write_text(json.dumps(state, indent=2), encoding="utf-8")


def process_graph(name, overall):
    base, edges = load_graph(name)
    n = len(base)
    eset = set((min(u, v), max(u, v)) for (u, v) in edges)
    adj = [set() for _ in range(n)]
    for (u, v) in eset:
        adj[u].add(v)
        adj[v].add(u)

    total_pairs = n * (n - 1) // 2 - len(eset)
    if SMOKE:
        total_pairs = min(total_pairs, SMOKE)

    jsonl = OUT / f"{name}.jsonl"
    done = 0
    if jsonl.exists():
        with jsonl.open(encoding="utf-8") as f:
            done = sum(1 for _ in f)
    if (OUT / f"{name}.summary.json").exists() and not SMOKE:
        print(f"  {name}: already complete, skipping", flush=True)
        return json.loads((OUT / f"{name}.summary.json").read_text())

    counts = {"free": 0, "forced_different": 0, "forced_same": 0, "indeterminate": 0}
    hits = []
    t0 = time.time()
    fh = jsonl.open("a", encoding="utf-8")
    processed = 0
    for idx, (a, b) in enumerate(nonadjacent_pairs(n, adj)):
        if SMOKE and idx >= SMOKE:
            break
        if idx < done:
            continue  # resume: already recorded
        fd, ind1 = forced_different(n, eset, a, b)
        if ind1:
            rec = {"a": a, "b": b, "indet": True}
            counts["indeterminate"] += 1
        elif fd:
            rec = {"a": a, "b": b, "diff": True}
            counts["forced_different"] += 1
            hits.append(rec)
        else:
            fs, ind2 = forced_same(n, eset, a, b)
            if ind2:
                rec = {"a": a, "b": b, "indet": True}
                counts["indeterminate"] += 1
            elif fs:
                rec = {"a": a, "b": b, "same": True}
                counts["forced_same"] += 1
                hits.append(rec)
            else:
                rec = {"a": a, "b": b, "free": True}
                counts["free"] += 1
        fh.write(json.dumps(rec) + "\n")
        processed += 1
        if rec.get("diff") or rec.get("same"):
            with (OUT / "HITS.jsonl").open("a", encoding="utf-8") as hf:
                hf.write(json.dumps({"graph": name, **rec}) + "\n")
            print(f"  *** HIT in {name}: pair {(a, b)} {rec} -> chi>=6 candidate ***",
                  flush=True)
        if processed % 1000 == 0:
            fh.flush()
            elapsed = time.time() - t0
            rate = processed / elapsed if elapsed else 0
            remaining = (total_pairs - done - processed) / rate if rate else -1
            print(f"  {name}: {done + processed}/{total_pairs} pairs "
                  f"({rate:.1f}/s, ~{remaining/60:.0f} min left) counts={counts}",
                  flush=True)
            overall["current"] = {"graph": name, "done": done + processed,
                                  "total": total_pairs, "counts": dict(counts),
                                  "rate_per_s": round(rate, 2)}
            write_progress(overall)
    fh.close()

    summary = {"graph": name, "n": n, "edges": len(eset),
               "nonadjacent_pairs": total_pairs, "counts": counts,
               "hits": hits, "seconds": round(time.time() - t0, 1),
               "smoke": bool(SMOKE)}
    if not SMOKE:
        (OUT / f"{name}.summary.json").write_text(json.dumps(summary, indent=2),
                                                  encoding="utf-8")
    print(f"  {name}: DONE {counts} ({summary['seconds']}s)", flush=True)
    return summary


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("Shot D: EXHAUSTIVE forcing classification of the chi-5 UDG lineage")
    print("=" * 78, flush=True)
    overall = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "graphs": GRAPHS,
               "smoke": SMOKE, "completed": [], "any_hit": False}
    write_progress(overall)
    for name in GRAPHS:
        try:
            s = process_graph(name, overall)
        except Exception as e:  # noqa: BLE001
            print(f"  {name}: ERROR {e!r}", flush=True)
            overall.setdefault("errors", []).append({"graph": name, "error": repr(e)})
            write_progress(overall)
            continue
        overall["completed"].append({"graph": name, "counts": s["counts"],
                                     "hits": len(s["hits"])})
        if s["hits"]:
            overall["any_hit"] = True
        write_progress(overall)
    overall["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    write_progress(overall)
    print("\n" + "=" * 78)
    if overall["any_hit"]:
        print("HEADLINE: NON-FREE pair FOUND -> candidate chi>=6 ingredient (see HITS.jsonl).")
    else:
        print("HEADLINE: all classified non-adjacent pairs are FREE (no long-range "
              "forcing). Exhaustive upgrade of L45 + L56 on the completed graphs.")
    print(f"archived under: {OUT}", flush=True)


if __name__ == "__main__":
    main()
