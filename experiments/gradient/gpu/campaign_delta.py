r"""Campaign delta: fixed-skeleton + candidate-edge growth (the L73/L74 lever).

Beta and gamma showed a global soft-adjacency objective DILUTES a hard core into
3-colorable lattice as it densifies (L74): it cannot add a hardening unit edge to a
chi>=4 core without dissolving the core. This campaign builds the one edge model L74
names as the open lever: optimize over a FIXED edge set (the rigid hard core, held at
unit distance) plus an explicit CANDIDATE-NEW-EDGE mechanism.

The mechanism, which is exactly de Grey's construction principle:
  - Pin a rigid chi>=4 core (the Moser spindle: 7 vtx, 11 edges = 2n-3, isostatic, so
    its SHAPE is fixed once its edges are at unit -- it cannot dissolve to a lattice).
  - Attach m FREE new vertices (no fixed edges, free to roam).
  - Pull each new vertex to UNIT distance from vertices it currently SHARES A COLOR with
    (adding a same-color unit edge forces a recolor: the differentiable proxy for "this
    new edge hardens the graph"). The inner colorer re-solves each round; the outer
    player moves the free vertices to manufacture same-color unit edges.
  - The core edges are held at unit throughout, so the emergent graph is core + whatever
    hardening edges the new vertices formed. Every unit pair is an intended edge (the
    core's, or an accepted candidate), so there is no faithfulness trap: the graph is a
    legal UDG by construction, anchored by an undissolvable chi>=4 core.

Then SAT decides the exact chi of what grew. GD still proves nothing: it PROPOSES a
grown UDG; a chi>=5 result is only real once SAT confirms it and the forced-pair /
lemma_db firewall accepts it. Run:
  python -m experiments.gradient.gpu.campaign_delta [--quick]
"""
from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np
import torch

from experiments.gradient import diff_udg as du
from experiments.gradient.adversarial import sat_chi
from experiments.gradient.gpu import batched_core as bc
from experiments.gradient.gpu import campaign_beta as beta

CACHE = os.path.join(os.path.dirname(__file__), "_cache")
os.makedirs(CACHE, exist_ok=True)


def moser_base():
    n, edges, coords = du.moser_spindle()
    return n, edges, np.asarray(coords, dtype=np.float64)


# --------------------------------------------------------------------------
# the growth optimizer (batched)
# --------------------------------------------------------------------------
def grow(base_n, base_edges, base_coords, *, m, B=2048, device=None, rounds=100,
         inner_steps=25, outer_steps=8, tau=0.07, sigma=0.10, seed=0,
         w_fix=20.0, w_cand=1.0, w_spread=3.0, lr_color=0.08, lr_coord=0.02,
         core_jitter=0.01, new_scale=1.2, k=4):
    """Grow a fixed rigid core by m free vertices that seek same-color unit edges.

    Returns (coords_cpu (B, base_n+m, 2) float64, core_residual (B,) = how well the
    core edges stayed at unit; small => the core held).
    """
    device = device or bc.pick_device()
    n = base_n + m
    gen = torch.Generator(device=device).manual_seed(seed)

    core = torch.tensor(base_coords, dtype=torch.float32, device=device)
    coords = torch.empty(B, n, 2, device=device)
    coords[:, :base_n] = core[None] + core_jitter * torch.randn(B, base_n, 2,
                                                                device=device, generator=gen)
    coords[:, base_n:] = new_scale * torch.randn(B, m, 2, device=device, generator=gen)
    coords.requires_grad_(True)

    fixed_idx = bc.edges_to_index(base_edges, device)
    # candidate pairs: every pair that touches at least one NEW vertex
    cand = [(i, j) for i in range(n) for j in range(i + 1, n) if j >= base_n]
    cand_idx = bc.edges_to_index(cand, device)

    logits = torch.randn(B, n, k, device=device, generator=gen).requires_grad_(True)
    opt_color = torch.optim.Adam([logits], lr=lr_color)
    opt_coord = torch.optim.Adam([coords], lr=lr_coord)

    ci_i, ci_j = cand_idx[:, 0], cand_idx[:, 1]

    for _ in range(rounds):
        with torch.no_grad():
            A_fixed = bc.batched_soft_adjacency(coords, tau=tau)
        for _ in range(inner_steps):
            opt_color.zero_grad(set_to_none=True)
            bc.batched_coloring_loss(logits, A_fixed).sum().backward()
            opt_color.step()

        with torch.no_grad():
            p = torch.softmax(logits, dim=2)                 # (B,n,k)
        for _ in range(outer_steps):
            opt_coord.zero_grad(set_to_none=True)
            core_res = bc.batched_edge_residual(coords, fixed_idx)          # (B,)
            # same-color weight on each candidate pair (detached colorer)
            pi = p[:, ci_i, :]; pj = p[:, ci_j, :]
            samecolor = (pi * pj).sum(-1)                                   # (B, |cand|)
            d_cand = torch.sqrt(((coords[:, ci_i, :] - coords[:, ci_j, :]) ** 2)
                                .sum(-1) + 1e-9)                            # (B, |cand|)
            attract = torch.exp(-((d_cand - 1.0) ** 2) / (2 * sigma * sigma))
            harden = (samecolor * attract).mean(dim=1)                      # (B,) maximize
            spread = bc.batched_spread_penalty(coords, floor=0.5)           # (B,)
            outer = w_fix * core_res - w_cand * harden + w_spread * spread
            outer.sum().backward()
            opt_coord.step()

    with torch.no_grad():
        core_res = bc.batched_edge_residual(coords, fixed_idx).detach().to("cpu")
    return coords.detach().to("cpu", torch.float64), core_res


# --------------------------------------------------------------------------
# certify a grown config: core held? what chi?
# --------------------------------------------------------------------------
def certify_growth(coords_np, base_n, base_edges, *, tol=0.05, k_cap=7):
    """Extract the emergent unit-distance graph and SAT its chi. Also checks the core
    edges survived (core_ok) and reports how many hardening edges were added."""
    n = len(coords_np)
    core_max_err = max(abs(math.hypot(*(coords_np[i] - coords_np[j])) - 1.0)
                       for (i, j) in base_edges)
    edges, band = beta.extract_edges(coords_np, tol=tol)
    eset = {(min(i, j), max(i, j)) for (i, j) in edges}
    core_present = all((min(i, j), max(i, j)) in eset for (i, j) in base_edges)
    added = [e for e in edges if e not in {(min(i, j), max(i, j)) for (i, j) in base_edges}]
    involves_new = sum(1 for (i, j) in added if j >= base_n or i >= base_n)
    chi = sat_chi(n, edges, k_try=tuple(range(2, k_cap + 1)))
    return {"n": n, "num_edges": len(edges), "core_max_err": core_max_err,
            "core_ok": bool(core_present and core_max_err < tol),
            "added_edges": len(added), "added_touching_new": involves_new,
            "band": band, "chi": chi}


def run(device, *, ms, B, rounds, top_m, k=4, quick_label="delta"):
    base_n, base_edges, base_coords = moser_base()
    print(f"base: Moser spindle n={base_n} |E|={len(base_edges)} (rigid core, chi=4)")
    pool = []   # (added_touching_new, harden_hint, coords_np, m)
    for mi, m in enumerate(ms):
        coords, core_res = grow(base_n, base_edges, base_coords, m=m, B=B,
                                device=device, rounds=rounds, seed=100 + mi, k=k)
        cr = core_res.numpy()
        # rank by number of candidate edges formed touching new vertices, among the
        # runs whose core actually held
        held = np.where(cr < 0.02)[0]
        scored = []
        for idx in held:
            e, _ = beta.extract_edges(coords[idx].numpy(), tol=0.05)
            eset = {(min(a, b), max(a, b)) for (a, b) in e}
            base_set = {(min(a, b), max(a, b)) for (a, b) in base_edges}
            add_new = sum(1 for (a, b) in (eset - base_set) if b >= base_n or a >= base_n)
            scored.append((add_new, idx))
        scored.sort(reverse=True)
        for add_new, idx in scored[:max(top_m // len(ms), 4)]:
            pool.append((add_new, coords[idx].numpy(), m))
        best_add = scored[0][0] if scored else 0
        print(f"  m={m}: {len(held)}/{B} runs held the core; "
              f"best added-new-edges among held = {best_add}")

    pool.sort(key=lambda t: -t[0])
    survivors = pool[:top_m]
    verified, chi_hist, best_legal_chi = [], {}, 0
    print(f"\nverifying {len(survivors)} grown survivors (core-check + SAT)...")
    for rank, (add_new, cnp, m) in enumerate(survivors):
        v = certify_growth(cnp, base_n, base_edges, k_cap=7)
        v["rank"] = rank; v["m"] = m
        verified.append(v)
        chi = v["chi"]
        chi_hist[str(chi)] = chi_hist.get(str(chi), 0) + 1
        if v["core_ok"] and isinstance(chi, int):
            best_legal_chi = max(best_legal_chi, chi)
            if chi >= 5:
                _flag(v, cnp, rank)
        print(f"  rank {rank:3d} m={m} n={v['n']} |E|={v['num_edges']} "
              f"core_ok={v['core_ok']} added(new)={v['added_touching_new']} chi={chi}")

    out = {"chi_hist": chi_hist, "best_legal_chi": best_legal_chi,
           "verified": verified}
    print(f"\ndelta chi histogram: {chi_hist}  best core-legal chi: {best_legal_chi}")
    return out


def _flag(v, coords_np, rank):
    path = os.path.join(CACHE, f"delta_candidate_chi{v['chi']}_rank{rank}.json")
    with open(path, "w") as f:
        json.dump({**v, "coords": coords_np.tolist()}, f, indent=2)
    print("\n" + "*" * 70)
    print(f"*** DELTA GREW A LEGAL chi={v['chi']} >= 5 UDG from the Moser core "
          f"(n={v['n']}, |E|={v['num_edges']}, +{v['added_touching_new']} new edges)")
    print(f"*** -> {path}  ROUTE TO SAT forced-pair test / lemma_db.")
    print("*" * 70 + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    device = bc.pick_device()
    print(f"device: {device}  torch {torch.__version__}  cuda={torch.cuda.is_available()}")
    if args.quick:
        out = run(device, ms=[2, 4], B=512, rounds=60, top_m=12)
        path = os.path.join(CACHE, "delta_quick.json")
    else:
        out = run(device, ms=[2, 3, 4, 5, 6, 8, 10, 12], B=4096, rounds=140, top_m=96)
        path = os.path.join(CACHE, "delta_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nresults -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
