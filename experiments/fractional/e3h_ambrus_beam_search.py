r"""e3h: Beam search over inclusion-exclusion LP configurations to push m_1(R^2).

Architecture 3 / continuous. Continuation of e3g.

Ambrus et al. 2023 found their 23-point configuration giving m_1 <= 0.2470 via
beam search. Their explicit coordinates aren't available to us. e3h reproduces
the beam-search idea using the Polymath 510 vertex set as the candidate pool,
starting from a small seed and greedily growing.

Algorithm:
1. Seed: hexagonal lattice (first 7 vertices of Polymath 510).
2. Candidate pool: remaining 503 vertices of Polymath 510.
3. At each step k:
   a. For each candidate vertex p in pool:
      - Form config' = current_config ∪ {p}.
      - Build IE-LP, solve.
      - Record m_1(config').
   b. Pick the candidate that gives smallest m_1.
   c. Add to current config.
4. Stop after target size (default 23) or when m_1 stops improving by > 1e-4.

Performance considerations:
- Each LP evaluation is O(K) variables where K = number of independent sets
  in the configuration's unit-distance subgraph.
- For 510-vertex pool, ~500 LP solves per step. With LP <= 1s each, ~10 min/step.
- Target 23 points → ~16 steps after the 7-vertex seed → few hours.

Beam width = 1 (greedy) for the initial implementation. Can extend.
"""

from __future__ import annotations

import json
import math
import pathlib
import time

import numpy as np

from experiments.fractional.e3c_ofv_lp_dual import chi_m_integer, CACHE
from experiments.fractional.e3f_polymath510_lp import load_polymath510_vertices
from experiments.fractional.e3g_ambrus_ie_lp import (
    build_ie_lp, unit_distance_subgraph, enumerate_independent_sets
)


def evaluate_config(X: np.ndarray, n_freq: int = 100, indep_max_size: int | None = None) -> dict | None:
    """Build and solve the IE-LP for a configuration X. Return result dict, or None on failure."""
    edges = unit_distance_subgraph(X)
    try:
        indep_sets = enumerate_independent_sets(X.shape[0], edges, max_size=indep_max_size)
        if len(indep_sets) > 200000:
            return None    # too many indep sets, LP would be intractable
        r = build_ie_lp(X, n_freq=n_freq, indep_max_size=indep_max_size)
        if r["m1_bound"] is None or r["m1_bound"] <= 0 or r["m1_bound"] > 1:
            return None    # LP failed
        return r
    except Exception:
        return None


def beam_search_greedy(
    pool: np.ndarray,
    seed_indices: list[int],
    target_size: int = 23,
    n_freq: int = 100,
    indep_max_size: int = 8,
    early_stop_eps: float = 1e-4,
    verbose: bool = True,
    save_per_step_path: pathlib.Path | None = None,
    resume_from_path: pathlib.Path | None = None,
) -> dict:
    """Greedy beam-search over candidate point pool.

    pool: (M, 2) array of candidate points.
    seed_indices: starting subset of pool indices.

    Returns dict with progression of m_1 bounds and final config indices.
    """
    config_indices = list(seed_indices)
    M = pool.shape[0]
    history = []

    # Resume from saved state if available.
    if resume_from_path is not None and resume_from_path.exists():
        with resume_from_path.open() as f:
            saved = json.load(f)
        config_indices = list(saved["config_indices"])
        history = list(saved["history"])
        if verbose:
            print(f"Resumed from {resume_from_path}: |X|={len(config_indices)}, "
                  f"m_1={history[-1]['m1_bound']:.6f}", flush=True)

    def save_state(prev_m1):
        if save_per_step_path is None:
            return
        save_per_step_path.parent.mkdir(parents=True, exist_ok=True)
        with save_per_step_path.open("w") as f:
            json.dump({
                "experiment": "e3h_ambrus_beam_search",
                "pool": "polymath_510_vertices",
                "seed_indices": list(seed_indices),
                "config_indices": list(config_indices),
                "history": history,
                "current_m1": prev_m1,
            }, f, indent=2)

    # Evaluate seed.
    X = pool[config_indices]
    r0 = evaluate_config(X, n_freq=n_freq, indep_max_size=indep_max_size)
    if r0 is None:
        print(f"Seed LP failed.")
        return {"history": [], "config_indices": config_indices, "final_m1": None}
    history.append({
        "step": 0,
        "config_size": len(config_indices),
        "m1_bound": r0["m1_bound"],
        "added_idx": None,
        "edges": r0["n_edges"],
        "indep_sets": r0["n_independent_sets"],
    })
    if verbose:
        print(f"Step 0: seed |X|={len(config_indices)}, edges={r0['n_edges']}, "
              f"indep={r0['n_independent_sets']}, m_1 <= {r0['m1_bound']:.6f}", flush=True)

    prev_m1 = r0["m1_bound"]
    save_state(prev_m1)

    while len(config_indices) < target_size:
        step = len(history)
        best_m1 = prev_m1
        best_idx = None
        best_r = None
        eval_count = 0
        candidate_indices = [i for i in range(M) if i not in config_indices]
        t_step_start = time.time()
        for c in candidate_indices:
            X_try = pool[config_indices + [c]]
            r = evaluate_config(X_try, n_freq=n_freq, indep_max_size=indep_max_size)
            if r is None:
                continue
            eval_count += 1
            if r["m1_bound"] < best_m1 - early_stop_eps:
                best_m1 = r["m1_bound"]
                best_idx = c
                best_r = r
        t_step = time.time() - t_step_start

        if best_idx is None:
            if verbose:
                print(f"Step {step}: no candidate improves m_1 beyond {prev_m1:.6f}. Stopping.")
            break

        config_indices.append(best_idx)
        prev_m1 = best_m1
        history.append({
            "step": step,
            "config_size": len(config_indices),
            "m1_bound": best_m1,
            "added_idx": best_idx,
            "edges": best_r["n_edges"],
            "indep_sets": best_r["n_independent_sets"],
            "eval_count": eval_count,
            "step_time_s": t_step,
        })
        if verbose:
            print(f"Step {step}: |X|={len(config_indices)}, added idx={best_idx}, "
                  f"edges={best_r['n_edges']}, "
                  f"indep={best_r['n_independent_sets']}, m_1 <= {best_m1:.6f}  "
                  f"(eval {eval_count}/{len(candidate_indices)}, {t_step:.1f}s)", flush=True)
        save_state(prev_m1)

    return {
        "history": history,
        "config_indices": config_indices,
        "final_m1": prev_m1,
        "target_size": target_size,
    }


def main():
    print("e3h: beam search over IE-LP configurations to push m_1(R^2) <= 0.2470")
    print("=" * 78)

    # Load Polymath 510 as candidate pool.
    pool = load_polymath510_vertices()
    print(f"Candidate pool: Polymath 510 vertices, shape {pool.shape}")

    # Seed: first 7 vertices (hexagonal lattice). Tested in e3g, m_1 <= 0.2799.
    seed_indices = list(range(7))
    print(f"Seed: hex lattice (indices {seed_indices})")
    print()

    state_path = CACHE / "e3h_state.json"
    result = beam_search_greedy(
        pool=pool,
        seed_indices=seed_indices,
        target_size=20,
        n_freq=100,
        indep_max_size=8,
        early_stop_eps=1e-5,
        verbose=True,
        save_per_step_path=state_path,
        resume_from_path=state_path,
    )

    print()
    print("=" * 78)
    print("Beam search complete.")
    print("=" * 78)
    print(f"Final config size: {len(result['config_indices'])}")
    print(f"Final m_1 bound:   {result['final_m1']:.6f}")
    print(f"Final chi_m >=:    {1/result['final_m1']:.4f}")
    print(f"Integer chi_m >=:  {chi_m_integer(result['final_m1'])}")
    print()
    print("Progression:")
    for h in result["history"]:
        print(f"  step {h['step']:3d}: size={h['config_size']:2d}, "
              f"m_1 <= {h['m1_bound']:.6f}, added idx={h.get('added_idx')}")
    print()
    print(f"For comparison:")
    print(f"  e3e (OFV + Moser at translations): m_1 <= 0.2619")
    print(f"  Ambrus et al. 2023 published:      m_1 <= 0.2470")

    # Save.
    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3h_ambrus_beam_search.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e3h_ambrus_beam_search",
                "pool": "polymath_510_vertices",
                "seed_indices": seed_indices,
                "final_config_indices": result["config_indices"],
                "final_m1": result["final_m1"],
                "history": result["history"],
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
