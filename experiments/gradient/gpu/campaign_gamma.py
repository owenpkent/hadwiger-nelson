r"""Campaign gamma: beta seeded from the chi>=4 lineage (Moser / P510).

Campaign beta (random-init adversarial GDA) produced a monolithic chi=3 distribution
across ~221k runs: GD builds triangular-lattice-like graphs and never even reaches
chi=4 (L74). Two readings are possible, and this campaign separates them:

  (i)  the generator CANNOT represent chi>=4 in its verify pipeline (an artifact), or
  (ii) random init never REACHES chi>=4 structure, which is geometrically isolated.

If (ii) is the truth, then SEEDING from a known chi>=4/chi>=5 configuration should let
the pipeline hold that value. Three experiments:

  E1 representation. Take the true Moser spindle (chi=4) and P510 (chi=5) embeddings,
     extract their unit-distance edges, and SAT the chi. If beta's extract+SAT path
     recovers 4 and 5, reading (i) is dead: the pipeline represents chi>=4 fine.

  E2 preservation under pressure. Seed the adversarial GDA AT the Moser spindle
     (B jittered copies) and run the full outer pressure. Does the evolved config stay
     chi=4, or does the density/colorability pressure relax it back to chi=3? Either
     answer is informative: preservation => the chi=3 monolith is a reachability wall;
     relaxation => the objective actively destroys chi=4 rigidity (a stronger negative).

  E3 scaffold growth. Seed a Moser core (7 vtx, chi=4) plus (n-7) free vertices and run
     multi-start adversarial GDA: can the adversary GROW a genuine chi=4 core into
     chi>=5? Harvest the densest/hardest, legalize, and SAT. Any legal chi>=5 is a
     candidate for the forced-pair / lemma_db firewall.

Discipline unchanged: every chi is SAT-decided; nothing here claims a lower bound.
Run: python -m experiments.gradient.gpu.campaign_gamma [--quick]
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


# --------------------------------------------------------------------------
# seeds from the lineage
# --------------------------------------------------------------------------
def moser_coords():
    _, _, coords = du.moser_spindle()
    return np.asarray(coords, dtype=np.float64)


def p510_coords():
    """Float coords of the P510 chi=5 UDG (from the exact symbolic vertices)."""
    from experiments.combinatorial.f1pt_lib import load_p510, num_coords
    base, _ = load_p510()
    fl = num_coords(base, dps=30)
    return np.array([[float(x), float(y)] for (x, y) in fl], dtype=np.float64)


def tile_seed(coords_np, B, jitter, device, gen):
    """(n,2) -> (B,n,2) jittered copies on device (float32)."""
    n = len(coords_np)
    base = torch.tensor(coords_np, dtype=torch.float32, device=device)
    out = base[None].expand(B, n, 2).clone()
    out = out + jitter * torch.randn(B, n, 2, device=device, generator=gen)
    return out


def scaffold_seed(core_np, n, B, jitter, device, gen, free_scale=1.2):
    """(B,n,2): first len(core) = jittered core (Moser), rest = random near it."""
    c = len(core_np)
    assert n >= c
    core = torch.tensor(core_np, dtype=torch.float32, device=device)
    out = torch.empty(B, n, 2, device=device)
    out[:, :c] = core[None] + jitter * torch.randn(B, c, 2, device=device, generator=gen)
    out[:, c:] = free_scale * torch.randn(B, n - c, 2, device=device, generator=gen)
    return out


# --------------------------------------------------------------------------
# certify a config AS-IS (no re-realization) -- "what did this become?"
# --------------------------------------------------------------------------
def certify_in_place(coords_np, tol=0.04, k_cap=7):
    """Extract the unit-distance graph from THESE coords and SAT its chi. Also
    reports the clean-gap (legality of the given embedding). No re-realization: this
    measures what the evolved configuration actually is."""
    n = len(coords_np)
    edges, band = beta.extract_edges(coords_np, tol=tol)
    if not edges:
        return {"n": n, "num_edges": 0, "band": band, "gap": None, "chi": None}
    # min non-edge gap (are these coords a clean UDG of the extracted graph?)
    es = {(min(i, j), max(i, j)) for (i, j) in edges}
    gaps = [abs(math.hypot(*(coords_np[i] - coords_np[j])) - 1.0)
            for i in range(n) for j in range(i + 1, n) if (i, j) not in es]
    gap = min(gaps) if gaps else float("inf")
    chi = sat_chi(n, edges, k_try=tuple(range(2, k_cap + 1)))
    return {"n": n, "num_edges": len(edges), "band": band, "gap": gap, "chi": chi}


# --------------------------------------------------------------------------
# experiments
# --------------------------------------------------------------------------
def e1_representation(device):
    print("\n=== E1: representation (does the pipeline recover chi=4 / chi=5?) ===")
    out = {}
    for name, cnp, want in [("moser", moser_coords(), 4),
                            ("p510", p510_coords(), 5)]:
        # tighter tol for the exact Moser; looser for float P510
        tol = 1e-4 if name == "moser" else 0.02
        v = certify_in_place(cnp, tol=tol, k_cap=7)
        ok = (v["chi"] == want)
        print(f"  {name}: extracted |E|={v['num_edges']} chi={v['chi']} "
              f"(expect {want}) {'OK' if ok else 'MISMATCH'}")
        out[name] = {**v, "expected": want, "ok": ok}
    return out


def e2_preservation(device, *, B, rounds, tau, jitter=0.01, seeds=(0,)):
    print("\n=== E2: Moser preservation under adversarial pressure ===")
    mc = moser_coords()
    results = []
    for s in seeds:
        gen = torch.Generator(device=device).manual_seed(7000 + s)
        seed_coords = tile_seed(mc, B, jitter, device, gen)
        coords, hardness = beta.adversarial_gda(
            7, target_degree=4, tau=tau, B=B, rounds=rounds, device=device,
            seed=7000 + s, coords_init=seed_coords)
        chis = {}
        gaps = []
        for i in range(len(coords)):
            v = certify_in_place(coords[i].numpy(), tol=0.04)
            key = str(v["chi"])
            chis[key] = chis.get(key, 0) + 1
            if v["gap"] is not None and math.isfinite(v["gap"]):
                gaps.append(v["gap"])
        # baseline: the untouched jittered seeds, before any pressure
        base_chi = {}
        sc = seed_coords.detach().to("cpu", torch.float64)
        for i in range(min(B, 256)):
            v = certify_in_place(sc[i].numpy(), tol=0.04)
            base_chi[str(v["chi"])] = base_chi.get(str(v["chi"]), 0) + 1
        print(f"  seed {s}: pre-pressure chi {base_chi} -> post-pressure chi {chis}")
        results.append({"seed": s, "pre": base_chi, "post": chis,
                        "median_gap": float(np.median(gaps)) if gaps else None})
    return results


def e3_scaffold(device, *, ns, B, rounds, taus, degs, top_m, jitter=0.02):
    print("\n=== E3: Moser-core scaffold growth (can chi=4 grow to chi>=5?) ===")
    mc = moser_coords()
    pool = []  # (density, hardness, coords_np, cfg)
    per_cfg = []
    ci = 0
    for n in ns:
        for deg in degs:
            for tau in taus:
                gen = torch.Generator(device=device).manual_seed(8000 + ci)
                seed_coords = scaffold_seed(mc, n, B, jitter, device, gen)
                coords, hardness = beta.adversarial_gda(
                    n, target_degree=deg, tau=tau, B=B, rounds=rounds,
                    device=device, seed=8000 + ci, coords_init=seed_coords)
                h = hardness.numpy()
                dens = np.array([len(beta.extract_edges(coords[i].numpy(), tol=0.04)[0])
                                 for i in range(len(coords))])
                keep = set(np.argsort(-dens)[:6].tolist()) | set(np.where(h > 0.03)[0].tolist())
                for idx in keep:
                    pool.append((int(dens[idx]), float(h[idx]),
                                 coords[idx].numpy(), (n, deg, tau)))
                per_cfg.append({"n": n, "deg": deg, "tau": tau,
                                "crisp_edges_max": int(dens.max()),
                                "hardness_max": float(h.max())})
                print(f"  n={n} deg={deg} tau={tau}: crisp|E| max={dens.max()} "
                      f"hardness max={h.max():.4f}")
                ci += 1

    pool.sort(key=lambda t: (-t[0], -t[1]))
    survivors = pool[:top_m]
    verified = []
    chi_hist = {}
    best_chi = 0
    print(f"\n  verifying {len(survivors)} densest scaffold survivors (legalize + SAT)...")
    for rank, (dens, hard, cnp, cfg) in enumerate(survivors):
        try:
            v = beta.legalize_and_certify(cnp, device, k_cap=7)
        except Exception as e:
            verified.append({"rank": rank, "error": repr(e), "config": cfg})
            continue
        v["rank"] = rank; v["gda_hardness"] = hard; v["config"] = cfg
        verified.append(v)
        chi = v.get("chi")
        chi_hist[str(chi)] = chi_hist.get(str(chi), 0) + 1
        if v.get("legal") and isinstance(chi, int):
            if chi > best_chi:
                best_chi = chi
            if chi >= 5:
                _flag(v, rank)
        print(f"    rank {rank:3d} n={v.get('n')} |E|={v.get('num_edges')} "
              f"legal={v.get('legal')} chi={chi} (hardness={hard:.3f})")
    print(f"\n  scaffold chi histogram: {chi_hist}  best legal chi: {best_chi}")
    return {"per_cfg": per_cfg, "verified": verified, "chi_hist": chi_hist,
            "best_legal_chi": best_chi}


def _flag(v, rank):
    path = os.path.join(CACHE, f"gamma_candidate_chi{v['chi']}_rank{rank}.json")
    with open(path, "w") as f:
        json.dump(v, f, indent=2)
    print("\n" + "*" * 70)
    print(f"*** SCAFFOLD GREW A LEGAL chi={v['chi']} >= 5 UDG "
          f"(n={v['n']}, |E|={v['num_edges']}) -> {path}")
    print("*** ROUTE TO SAT forced-pair test / lemma_db before trusting.")
    print("*" * 70 + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    device = bc.pick_device()
    print(f"device: {device}  torch {torch.__version__}  cuda={torch.cuda.is_available()}")

    out = {}
    out["e1"] = e1_representation(device)
    if args.quick:
        out["e2"] = e2_preservation(device, B=256, rounds=40, tau=0.06, seeds=(0,))
        out["e3"] = e3_scaffold(device, ns=[10], B=512, rounds=50, taus=[0.06],
                                degs=[4], top_m=12)
        path = os.path.join(CACHE, "gamma_quick.json")
    else:
        out["e2"] = e2_preservation(device, B=2048, rounds=80, tau=0.06,
                                    seeds=(0, 1, 2))
        out["e3"] = e3_scaffold(device, ns=[10, 12, 15, 18], B=4096, rounds=100,
                                taus=[0.05, 0.08, 0.12], degs=[4, 5], top_m=96)
        path = os.path.join(CACHE, "gamma_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nresults -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
