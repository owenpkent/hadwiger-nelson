r"""Campaign beta: GPU multi-start adversarial UDG generator.

The GD-native form of the live Arch-1 route (Option A of the gradient thread),
scaled from one run to tens of thousands of parallel runs on the GPU. The
documented single-run honest negative was: one adversarial GDA from a random seed
builds a real ~46-edge near-unit graph but only reaches chi=3. This campaign asks
the escalated question: does massive multi-start change that, or does GD saturate?

PIPELINE (propose -> legalize -> certify; GD never proves a lower bound):

  1. GPU adversarial GDA (batched). For each sweep config (n, target_degree, tau),
     run B parallel runs of

         max_{coords}  min_{soft k-coloring}  coloring_loss(soft_adj(coords), coloring)

     with a degree-budget term forcing the outer player to actually BUILD a
     near-unit graph and an anti-collapse spread penalty. The objective is driven by
     genuine Euclidean unit distances, so it cannot lift to Q^2 (chi=2). k is fixed
     at 4, so a hard-to-4-color emergent graph is a chi>=5 CANDIDATE.

  2. Cheap ranking. Each run reports the colorability it achieved at k=4 (already
     computed by the inner player). Keep the globally hardest few.

  3. Legalize. Extract the emergent edge set (pairs near unit distance) and re-refine
     it into a LEGAL UDG in float64 (drive edges to exact unit, push non-edges off
     the unit circle). Report the clean-gap so an ambiguous near-unit graph is not
     mistaken for a genuine UDG (the P510-flavored faithfulness trap).

  4. Certify. The exact chromatic number of every legal survivor is decided by SAT
     (adversarial.sat_chi). Only SAT can assert chi >= 5.

Outputs a chi histogram, the hardest legal core found, and dumps any chi>=5 legal
candidate for the forced-pair / lemma_db firewall. Run:
  python -m experiments.gradient.gpu.campaign_beta            (full overnight sweep)
  python -m experiments.gradient.gpu.campaign_beta --quick    (fast smoke test)
"""
from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np
import torch

from experiments.gradient.gpu import batched_core as bc
from experiments.gradient.gpu import search as S

CACHE = os.path.join(os.path.dirname(__file__), "_cache")
os.makedirs(CACHE, exist_ok=True)


# --------------------------------------------------------------------------
# phase 1: batched adversarial GDA
# --------------------------------------------------------------------------
def adversarial_gda(n, target_degree, tau, *, k=4, B=2048, rounds=60,
                    inner_steps=25, outer_steps=8, device=None, seed=0,
                    lr_color=0.08, lr_coord=0.02, w_deg=3.0, w_spread=2.0,
                    w_crisp=1.5, scale=1.6, coords_init=None):
    """B parallel adversarial runs. Returns (coords_cpu (B,n,2) float64,
    hardness (B,) = achieved coloring_loss@k at the inner optimum).

    The outer player is pushed to actually BUILD a dense near-unit graph by three
    coordinate terms: a below-target degree hinge (build AT LEAST target_degree unit
    neighbors), a crispness reward (drive soft-adjacency entries to 0/1 so distances
    are clearly unit or clearly not, not a haze of weak near-adjacencies), and an
    anti-collapse spread penalty. Only then does making it hard to k-color mean
    anything. hardness ~ 0 => the emergent graph is easily k-colorable (chi<=k);
    hardness bounded from 0 => a chi>k CANDIDATE (SAT decides, never this loss).
    """
    device = device or bc.pick_device()
    gen = torch.Generator(device=device).manual_seed(seed)
    if coords_init is not None:
        # seeded start (e.g. the Moser/P510 lineage): use the given (B,n,2) init
        coords = coords_init.to(device=device, dtype=torch.float32).clone()
        coords.requires_grad_(True)
    else:
        coords = bc.random_coords(B, n, device, dtype=torch.float32, scale=scale,
                                  generator=gen)
    logits = torch.randn(B, n, k, device=device, generator=gen).requires_grad_(True)
    opt_color = torch.optim.Adam([logits], lr=lr_color)
    opt_coord = torch.optim.Adam([coords], lr=lr_coord)

    for _ in range(rounds):
        # inner player: best soft k-coloring of the CURRENT soft graph
        with torch.no_grad():
            A_fixed = bc.batched_soft_adjacency(coords, tau=tau)
        for _ in range(inner_steps):
            opt_color.zero_grad(set_to_none=True)
            cl = bc.batched_coloring_loss(logits, A_fixed)
            cl.sum().backward()  # minimize coloring_loss
            opt_color.step()

        # outer player: move coordinates to make that coloring as bad as possible,
        # while BUILDING a dense, crisp UDG and not collapsing.
        for _ in range(outer_steps):
            opt_coord.zero_grad(set_to_none=True)
            A = bc.batched_soft_adjacency(coords, tau=tau)          # (B,n,n)
            cl = bc.batched_coloring_loss(logits.detach(), A)       # (B,)
            deg = A.sum(dim=(1, 2)) / n                             # (B,) mean degree
            deg_short = torch.relu(target_degree - deg)             # only if BELOW target
            crisp = (A * (1.0 - A)).sum(dim=(1, 2)) / (n * (n - 1)) # 0 at crisp 0/1
            spread = bc.batched_spread_penalty(coords, floor=0.5)   # (B,)
            outer = (-cl
                     + w_deg * deg_short ** 2
                     + w_crisp * crisp
                     + w_spread * spread)
            outer.sum().backward()
            opt_coord.step()

    # final hardness: re-solve the inner coloring well on the frozen graph
    with torch.no_grad():
        A_fixed = bc.batched_soft_adjacency(coords, tau=tau)
    logits2 = torch.randn(B, n, k, device=device, generator=gen).requires_grad_(True)
    opt2 = torch.optim.Adam([logits2], lr=lr_color)
    for _ in range(inner_steps * 4):
        opt2.zero_grad(set_to_none=True)
        cl = bc.batched_coloring_loss(logits2, A_fixed)
        cl.sum().backward()
        opt2.step()
    with torch.no_grad():
        hardness = bc.batched_coloring_loss(logits2, A_fixed).detach().to("cpu")
    return coords.detach().to("cpu", torch.float64), hardness


# --------------------------------------------------------------------------
# phase 3+4: legalize an emergent topology, then SAT its exact chi
# --------------------------------------------------------------------------
def extract_edges(coords_np, tol=0.04):
    """Pairs within tol of unit distance = candidate edges. Also returns the
    ambiguity band count: non-edges whose distance is within [tol, 3*tol] of 1
    (a large band means the emergent graph is NOT a clean UDG)."""
    n = len(coords_np)
    edges, band = [], 0
    for i in range(n):
        for j in range(i + 1, n):
            d = math.hypot(*(coords_np[i] - coords_np[j]))
            off = abs(d - 1.0)
            if off < tol:
                edges.append((i, j))
            elif off < 3 * tol:
                band += 1
    return edges, band


def legalize_and_certify(coords_np, device, *, tol=0.04, k_cap=7):
    """Extract the emergent graph, re-refine it into a legal UDG, and SAT its chi.

    Returns a dict verdict. `legal` means every edge is at unit distance and no
    non-edge is within delta/2 of it; `chi` is the SAT-exact chromatic number of the
    (legalized) discrete graph. A near-unit config whose extracted graph cannot be
    legalized is reported with legal=False and its ambiguity band, an honest negative.
    """
    from experiments.gradient.adversarial import sat_chi
    n = len(coords_np)
    edges, band = extract_edges(coords_np, tol=tol)
    if len(edges) < n:  # too sparse to be interesting
        return {"n": n, "num_edges": len(edges), "band": band, "legal": False,
                "chi": None, "note": "too_sparse"}
    # re-refine THIS fixed topology into a legal UDG (reuses the alpha machinery)
    r = S.multistart_realize(n, edges, B=256, device=device, steps=800,
                             refine_steps=3000, delta=0.05, seed=0)
    legal = r["legal_udg"]
    # SAT the exact chi of the legalized graph (or the raw extracted graph if the
    # legalization moved points: re-extract from the refined coords for consistency)
    ref_coords = np.asarray(r["coords"])
    ref_edges, ref_band = extract_edges(ref_coords, tol=0.02) if legal else (edges, band)
    chi = sat_chi(n, ref_edges, k_try=tuple(range(2, k_cap + 1)))
    return {"n": n, "num_edges": len(ref_edges), "band": ref_band if legal else band,
            "legal": bool(legal),
            "max_edge_error": r["refined_max_edge_error"],
            "min_nonedge_gap": r["refined_min_nonedge_gap"],
            "chi": chi, "coords": ref_coords.tolist()}


# --------------------------------------------------------------------------
# sweep driver
# --------------------------------------------------------------------------
def run_sweep(configs, *, B, top_m, device, rounds, out_path, verify_cap=7,
              per_config_keep=6, hard_flag=0.02):
    """For each config, build B graphs, keep the densest few (and any anomalously
    hard one), then legalize + SAT their exact chi. Ranking is by achieved crisp
    density, because hardness@k=4 is ~0 for everything GD builds (the finding): the
    dense unit-distance graphs it constructs are lattice-like and easily colorable.
    """
    device = device or bc.pick_device()
    pool = []   # (density, hardness, coords_np, config)
    per_config = []
    for ci, (n, deg, tau) in enumerate(configs):
        coords, hardness = adversarial_gda(n, deg, tau, B=B, rounds=rounds,
                                           device=device, seed=1000 + ci)
        h = hardness.numpy()
        dens = np.array([len(extract_edges(coords[i].numpy(), tol=0.04)[0])
                         for i in range(len(coords))])
        # keep the densest per config, plus any anomalously hard start
        keep = set(np.argsort(-dens)[:per_config_keep].tolist())
        keep |= set(np.where(h > hard_flag)[0].tolist())
        for idx in keep:
            pool.append((int(dens[idx]), float(h[idx]), coords[idx].numpy(),
                         (n, deg, tau)))
        per_config.append({"n": n, "target_degree": deg, "tau": tau,
                           "crisp_edges_max": int(dens.max()),
                           "crisp_edges_median": float(np.median(dens)),
                           "hardness_max": float(h.max())})
        print(f"  config n={n} deg={deg} tau={tau}: crisp|E| "
              f"max={dens.max()} median={np.median(dens):.0f} | "
              f"hardness max={h.max():.4f}")
        _dump(out_path, {"per_config": per_config, "verified": None})

    # verify the densest survivors globally (plus the hard-flagged ones already in)
    pool.sort(key=lambda t: (-t[0], -t[1]))
    survivors = pool[:top_m]
    verified = []
    chi_hist = {}
    best_legal = None
    print(f"\nverifying {len(survivors)} densest survivors (legalize + SAT)...")
    for rank, (dens, hard, cnp, cfg) in enumerate(survivors):
        try:
            v = legalize_and_certify(cnp, device, k_cap=verify_cap)
        except Exception as e:  # keep the sweep alive
            v = {"error": repr(e), "config": cfg}
            verified.append({"rank": rank, "gda_hardness": hard, "config": cfg, **v})
            continue
        v["rank"] = rank
        v["gda_hardness"] = hard
        v["gda_crisp_edges"] = dens
        v["config"] = cfg
        verified.append(v)
        chi = v.get("chi")
        key = str(chi)
        chi_hist[key] = chi_hist.get(key, 0) + 1
        # track the hardest LEGAL core, and flag any legal chi>=5
        if v.get("legal") and isinstance(chi, int):
            if best_legal is None or chi > best_legal.get("chi", 0):
                best_legal = v
            if chi >= 5:
                _flag_candidate(v, rank)
        print(f"  rank {rank:3d} n={v.get('n')} |E|={v.get('num_edges')} "
              f"legal={v.get('legal')} band={v.get('band')} chi={chi} "
              f"(gda_hardness={hard:.3f})")
        _dump(out_path, {"per_config": per_config, "verified": verified,
                         "chi_hist": chi_hist})

    summary = {"per_config": per_config, "verified": verified,
               "chi_hist": chi_hist,
               "best_legal_chi": (best_legal.get("chi") if best_legal else None)}
    _dump(out_path, summary)
    print("\nchi histogram over legal+illegal survivors:", chi_hist)
    if best_legal:
        print(f"hardest LEGAL UDG: n={best_legal['n']} |E|={best_legal['num_edges']} "
              f"chi={best_legal['chi']} gap={best_legal.get('min_nonedge_gap'):.3f}")
    return summary


def _flag_candidate(v, rank):
    path = os.path.join(CACHE, f"beta_candidate_chi{v['chi']}_rank{rank}.json")
    with open(path, "w") as f:
        json.dump(v, f, indent=2)
    print("\n" + "*" * 70)
    print(f"*** LEGAL near-unit graph with chi={v['chi']} >= 5 "
          f"(n={v['n']}, |E|={v['num_edges']}, gap={v.get('min_nonedge_gap'):.3f})")
    print(f"*** CANDIDATE dumped to {path}")
    print(f"*** ROUTE TO SAT forced-pair test / lemma_db firewall before trusting.")
    print("*" * 70 + "\n")


def _dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    device = bc.pick_device()
    print(f"device: {device}  torch {torch.__version__}  cuda={torch.cuda.is_available()}")

    if args.quick:
        configs = [(12, 4, 0.06), (15, 4, 0.06)]
        summary = run_sweep(configs, B=512, top_m=10, device=device, rounds=70,
                            out_path=os.path.join(CACHE, "beta_quick.json"))
    else:
        ns = [9, 12, 15, 18, 21, 24]
        degs = [3, 4, 5]
        taus = [0.05, 0.08, 0.12]
        configs = [(n, d, t) for n in ns for d in degs for t in taus]
        summary = run_sweep(configs, B=4096, top_m=96, device=device, rounds=100,
                            out_path=os.path.join(CACHE, "beta_results.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
