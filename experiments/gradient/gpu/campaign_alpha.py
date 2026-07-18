r"""Campaign alpha: GPU realizer sweep over the program's chi>=6 host candidates.

Governing fact (L63, the codegree wall): every host graph swept here is
rigidity-over-determined, |E| >> 2n - 3, so a legal Euclidean unit-distance
realization is not expected. The sweep is a NEGATIVE-RESULT confirmation at
GPU scale, run over multiple random seeds so a null result is not an artifact
of one unlucky init. If any host DOES realize legally, that is a live
chi>=6 CANDIDATE and must be flagged loudly and routed to the SAT firewall
(this script never certifies chi; it only proposes coordinates).

Sources swept:
  1. experiments/combinatorial/e15b_chi5_n29.json  -- a verified chi=5, n=29
     graph. If it realizes exactly, that is simply a re-realization of a
     known chi=5 UDG (not a new bound), but it is the highest-value graph in
     the sweep because it is a REAL chi=5 witness, so it gets the largest
     per-seed budget.
  2. experiments/combinatorial/e13_hosts.json      -- 'hosts' list, each host
     dict carries its own edge list (verified by inspection; not regenerated
     from e13_small_hosts.py).
  3. experiments/combinatorial/e13b_hosts.json     -- same shape, same
     verification.

Run: python -m experiments.gradient.gpu.campaign_alpha [--quick]
"""
from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from experiments.gradient.gpu import batched_core as bc
from experiments.gradient.gpu import search as S

REPO_ROOT = Path(__file__).resolve().parents[3]
COMB_DIR = REPO_ROOT / "experiments" / "combinatorial"
CACHE_DIR = Path(__file__).resolve().parent / "_cache"
RESULTS_PATH = CACHE_DIR / "alpha_results.json"

E15B_PATH = COMB_DIR / "e15b_chi5_n29.json"
E13_PATH = COMB_DIR / "e13_hosts.json"
E13B_PATH = COMB_DIR / "e13b_hosts.json"


def over_determination(n, edges):
    """Rigidity over-determination: |E| - (2n - 3). Positive => generically
    over-constrained for a planar unit-distance realization (the codegree
    wall's rigidity signature)."""
    return len(edges) - (2 * n - 3)


def load_graphs(quick: bool):
    """Return a list of (name, n, edges, seeds) tuples to sweep.

    Each host's edges are read verbatim from its own JSON record; nothing is
    fabricated. e13 / e13b hosts that lack an explicit edge list would be
    SKIPPED (with a note in the results) rather than reconstructed here --
    but as verified by direct inspection, every host in e13_hosts.json and
    e13b_hosts.json already carries its own 'edges' field, so no host is
    skipped in the current data.
    """
    graphs = []
    skipped = []

    # 1. the n=29 chi=5 prize graph -- biggest budget, most seeds.
    with open(E15B_PATH) as f:
        d = json.load(f)
    n29_seeds = [0] if quick else [0, 1, 2, 3, 4, 5, 6, 7]
    graphs.append(("e15b_chi5_n29", d["n"], [tuple(e) for e in d["edges"]], n29_seeds))

    if quick:
        return graphs, skipped

    # 2 & 3. e13 / e13b hosts.
    for path, tag in ((E13_PATH, "e13"), (E13B_PATH, "e13b")):
        with open(path) as f:
            d = json.load(f)
        hosts = d["hosts"] if isinstance(d, dict) else d
        for h in hosts:
            name = f"{tag}_{h.get('name', 'unnamed')}"
            if "edges" in h and h["edges"]:
                edges = [tuple(e) for e in h["edges"]]
                graphs.append((name, h["n"], edges, [0, 1, 2, 3]))
            else:
                skipped.append({
                    "name": name,
                    "reason": ("no explicit 'edges' field serialized in "
                               f"{path.name}; not regenerated from "
                               "e13_small_hosts.py per task scope"),
                })

    return graphs, skipped


def sweep_one(name, n, edges, seeds, *, B, steps, refine_steps, delta=0.05):
    """Run multistart_realize over `seeds`, keep the best (smallest max edge
    error) result. Returns a result dict augmented with rigidity stats."""
    over = over_determination(n, edges)
    device = bc.pick_device()

    best = None
    per_seed = []
    for sd in seeds:
        r = S.multistart_realize(n, edges, B=B, device=device, steps=steps,
                                 refine_steps=refine_steps, delta=delta, seed=sd)
        per_seed.append({
            "seed": sd,
            "refined_max_edge_error": r["refined_max_edge_error"],
            "refined_min_nonedge_gap": r["refined_min_nonedge_gap"],
            "legal_udg": r["legal_udg"],
        })
        if best is None or r["refined_max_edge_error"] < best["refined_max_edge_error"]:
            best = r

    return {
        "name": name,
        "n": n,
        "num_edges": len(edges),
        "over_determination": over,
        "seeds_tried": list(seeds),
        "per_seed": per_seed,
        "best_max_edge_error": best["refined_max_edge_error"],
        "best_min_nonedge_gap": best["refined_min_nonedge_gap"],
        "legal_udg": best["legal_udg"],
        "best_coords": best["coords"].tolist(),
        "best_seed_B": B,
    }


def checkpoint(results, skipped):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"results": results, "skipped_hosts": skipped}
    with open(RESULTS_PATH, "w") as f:
        json.dump(payload, f, indent=1)


def dump_candidate(name, coords):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"alpha_candidate_{name}.json"
    with open(path, "w") as f:
        json.dump({"name": name, "coords": coords}, f, indent=1)
    return path


def main():
    ap = argparse.ArgumentParser(description="GPU realizer sweep over chi>=6 host candidates.")
    ap.add_argument("--quick", action="store_true",
                    help="fast smoke test: n=29 graph only, tiny budget, seed 0 only")
    args = ap.parse_args()

    device = bc.pick_device()
    print(f"campaign_alpha: device={device} quick={args.quick}")

    if args.quick:
        B, steps, refine_steps = 512, 600, 1500
    else:
        B, steps, refine_steps = 4096, 2500, 5000

    graphs, skipped = load_graphs(args.quick)

    if skipped:
        print("\nSKIPPED hosts (no serialized edge list):")
        for s in skipped:
            print(f"  - {s['name']}: {s['reason']}")

    results = {}
    summary_rows = []

    for name, n, edges, seeds in graphs:
        # the n=29 prize graph gets its full multi-seed budget even in --quick
        # it would just be seeds=[0]; other graphs already carry their own seed list.
        run_B, run_steps, run_refine = B, steps, refine_steps
        print(f"\n=== {name}: n={n} |E|={len(edges)} seeds={seeds} "
              f"B={run_B} steps={run_steps} refine={run_refine} ===")
        try:
            res = sweep_one(name, n, edges, seeds, B=run_B, steps=run_steps,
                            refine_steps=run_refine)
        except Exception as exc:
            print(f"  ERROR sweeping {name}: {exc}")
            traceback.print_exc()
            results[name] = {
                "name": name, "n": n, "num_edges": len(edges),
                "over_determination": over_determination(n, edges),
                "error": str(exc),
            }
            checkpoint(results, skipped)
            continue

        results[name] = res
        checkpoint(results, skipped)

        print(f"  over={res['over_determination']}  "
              f"best_max_edge_err={res['best_max_edge_error']:.3e}  "
              f"best_gap={res['best_min_nonedge_gap']:.3f}  "
              f"legal={res['legal_udg']}")

        if res["legal_udg"]:
            path = dump_candidate(name, res["best_coords"])
            print("\n" + "*" * 78)
            print(f"*** LEGAL UDG REALIZED: {name} -- LIVE chi>=6 CANDIDATE, "
                  f"ROUTE TO SAT ***")
            print(f"*** coords dumped to {path} ***")
            print("*" * 78 + "\n")

        summary_rows.append((
            name, res["n"], res["num_edges"], res["over_determination"],
            res["best_max_edge_error"], res["best_min_nonedge_gap"],
            res["legal_udg"],
        ))

    print("\n" + "=" * 100)
    print(f"{'name':<32}{'n':>4}{'|E|':>6}{'over':>6}"
          f"{'best_max_edge_err':>20}{'best_gap':>12}{'legal':>8}")
    print("-" * 100)
    for name, n, m, over, err, gap, legal in summary_rows:
        print(f"{name:<32}{n:>4}{m:>6}{over:>6}{err:>20.3e}{gap:>12.4f}{str(legal):>8}")
    print("=" * 100)

    if skipped:
        print("\nskipped hosts:")
        for s in skipped:
            print(f"  - {s['name']}: {s['reason']}")

    any_legal = any(row[-1] for row in summary_rows)
    print(f"\nresults checkpointed to {RESULTS_PATH}")
    print("ANY LEGAL UDG FOUND: " + ("YES -- SEE BANNER ABOVE" if any_legal else "no (expected)"))


if __name__ == "__main__":
    main()
