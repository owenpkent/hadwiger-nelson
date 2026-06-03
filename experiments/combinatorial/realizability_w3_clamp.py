r"""W3 attack: is the abstract color-clamp (L51) unit-distance realizable in R^2?

L51 built an explicit 48-vertex triangle-free chi-5 graph G with a non-adjacent
forced-different pair (s,t) at k=5 (the abstract L45 ingredient). The remaining and
ONLY obstruction to chi(R^2) >= 6 by coupling is W3: can such a clamp be drawn with
every edge at distance exactly 1?

This probe answers it for the specific Mycielski-tower clamp and isolates WHERE the
obstruction lives, so the refined target is precise.

Method (calibrated, so a negative is meaningful rather than solver fatigue):
  realizability = does the edge-residual system r_e(p) = |p_i - p_j|^2 - 1 = 0 have a
  real solution? Probe by multi-start Levenberg-Marquardt (scipy least_squares) on the
  2n coordinates; success := max edge-length error < 1e-5. We CALIBRATE on graphs of
  known status at the same scale:
    - Moser spindle (7 v): realizable -> solver MUST reach ~0.
    - a triangular-lattice patch (~50 v): realizable -> solver MUST reach ~0
      (shows the solver scales to clamp size; a clamp failure is then structural).
  then run the clamp. We also report the rigidity over-determination |E|-(2|V|-3),
  the degree sequence, and (for the clamp) which edges retain the largest residual
  (localizing the obstruction to the high-degree apex).

Honest scope: numerical non-realizability is strong EVIDENCE, not a proof (a missed
basin is possible); the over-determination count and the apex-degree argument are the
structural backbone. Exact (Groebner) realizability is feasible only at ~14 vertices
(cf. h2_groebner_moser14.py), too small for the 48-vertex clamp.
"""
from __future__ import annotations

import json
import math
import os
import sys
import pathlib

import numpy as np
import networkx as nx
from scipy.optimize import least_squares

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from f1pt_lib import parse_vtx, parse_edges, VTX, EDGE  # noqa: E402

CACHE = os.path.join(os.path.dirname(__file__), "_cache")
RNG = np.random.default_rng(20260602)


# ---------- test graphs ----------

def load_clamp():
    d = json.load(open(os.path.join(CACHE, "lrf_abstract_clamp.json")))
    m = d["minimized"]
    return m["n"], [tuple(e) for e in m["edge_list"]], (m["s"], m["t"])


def moser_spindle_graph():
    """Abstract Moser spindle (7 v, 11 e): realizable by construction."""
    edges = [(0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4),
             (1, 5), (3, 5), (2, 6), (4, 6), (5, 6)]
    return 7, edges


def triangular_lattice_patch(rings=4):
    """A hex patch of the unit triangular lattice; realizable by construction.
    Returns (n, edges) with ~50 vertices for rings=4."""
    pts = []
    a = (1.0, 0.0)
    b = (0.5, math.sqrt(3) / 2)
    seen = {}
    for i in range(-rings, rings + 1):
        for j in range(-rings, rings + 1):
            x = i * a[0] + j * b[0]
            y = i * a[1] + j * b[1]
            if x * x + y * y <= (rings + 0.1) ** 2:
                seen[(i, j)] = (x, y)
    idx = {k: n for n, k in enumerate(seen)}
    pts = [seen[k] for k in seen]
    edges = []
    coords = list(seen.keys())
    cset = set(coords)
    for (i, j) in coords:
        for (di, dj) in [(1, 0), (0, 1), (1, -1)]:
            if (i + di, j + dj) in cset:
                edges.append((idx[(i, j)], idx[(i + di, j + dj)]))
    return len(pts), edges, pts  # pts = the true realization (unit edges)


# ---------- realizability solver ----------

def residuals(flat, n, edges):
    p = flat.reshape(n, 2)
    r = np.empty(len(edges))
    for k, (i, j) in enumerate(edges):
        d = p[i] - p[j]
        r[k] = d[0] * d[0] + d[1] * d[1] - 1.0
    return r


def _make_graph(n, edges):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    return G


def _scale_to_unit(p, edges):
    lens = [math.hypot(*(p[i] - p[j])) for (i, j) in edges]
    med = float(np.median(lens))
    return p / med if med > 1e-9 else p


def _init_layouts(n, edges, n_random):
    """Graph-structure-aware initializations (NOT just random): Kamada-Kawai
    (shortest-path-distance embedding, close to the metric a UDG wants) and spring,
    plus random restarts as backup. Scaled so the median edge length is 1."""
    G = _make_graph(n, edges)
    outs = []
    try:
        kk = nx.kamada_kawai_layout(G)
        outs.append(("kk", np.array([kk[i] for i in range(n)], float)))
    except Exception:  # noqa: BLE001
        pass
    for seed in range(3):
        sp = nx.spring_layout(G, seed=seed, iterations=300, dim=2)
        outs.append((f"spring{seed}", np.array([sp[i] for i in range(n)], float)))
    for _ in range(n_random):
        outs.append(("rand", RNG.uniform(-math.sqrt(n), math.sqrt(n), size=(n, 2))))
    return [(name, _scale_to_unit(p, edges)) for name, p in outs]


def try_realize(n, edges, starts=40, true_coords=None):
    """Multi-init Levenberg/trust-region refine. If true_coords is given, also seed
    from a noisy copy of the true layout (a LOCAL-basin calibration: a correct solver
    must refine a perturbed true realization back to ~0)."""
    best = math.inf
    best_p = None
    inits = _init_layouts(n, edges, starts)
    if true_coords is not None:
        tc = np.array(true_coords, float)
        for sig in (0.02, 0.1, 0.25):
            inits.append((f"true+{sig}", tc + RNG.normal(0, sig, size=tc.shape)))
    for _name, p0 in inits:
        sol = least_squares(residuals, p0.ravel(), args=(n, edges),
                            method="trf", max_nfev=6000)
        p = sol.x.reshape(n, 2)
        errs = [abs(math.hypot(*(p[i] - p[j])) - 1.0) for (i, j) in edges]
        m = max(errs)
        if m < best:
            best, best_p = m, p
        if best < 1e-7:
            break
    return best, best_p


def edge_error_profile(p, edges, top=8):
    errs = [(abs(math.hypot(*(p[i] - p[j])) - 1.0), i, j) for (i, j) in edges]
    errs.sort(reverse=True)
    return errs[:top]


def degree_stats(n, edges):
    deg = [0] * n
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    return {"n": n, "edges": len(edges), "max_deg": max(deg),
            "min_deg": min(deg), "avg_deg": round(2 * len(edges) / n, 2),
            "over_determination": len(edges) - (2 * n - 3),
            "argmax_deg": int(np.argmax(deg))}


def main():
    print("W3: unit-distance realizability of the abstract color-clamp")
    print("=" * 74)

    out = {"experiment": "realizability_w3_clamp", "calibration": {}, "clamp": {}}

    # --- calibration: graphs of known status ---
    # The DECISIVE calibration is global recovery of the lattice from STRUCTURE-based
    # inits (no true coords): if the solver can find a realization from scratch at
    # clamp scale, a clamp failure is meaningful; if not, the clamp test is inconclusive.
    print("Calibration (solver must reach ~0 on realizable graphs, from scratch):")
    nM, eM = moser_spindle_graph()
    bestM, _ = try_realize(nM, eM, starts=30)
    nL, eL, coordsL = triangular_lattice_patch(4)
    bestL_scratch, _ = try_realize(nL, eL, starts=40)          # structure inits only
    bestL_local, _ = try_realize(nL, eL, starts=4, true_coords=coordsL)  # basin check
    for name, n, e, best in [("moser_spindle", nM, eM, bestM),
                             ("tri_lattice(scratch)", nL, eL, bestL_scratch),
                             ("tri_lattice(local)", nL, eL, bestL_local)]:
        st = degree_stats(n, e)
        realized = best < 1e-5
        out["calibration"][name] = {"best_max_edge_err": best, "realized": realized,
                                    **st}
        print(f"  {name:22s}: n={st['n']:3d} E={st['edges']:3d} "
              f"max_deg={st['max_deg']:2d} over_det={st['over_determination']:+4d} "
              f"-> best_err={best:.2e} realized={realized}")
    calib_global_ok = (bestM < 1e-5) and (bestL_scratch < 1e-5)
    calib_local_ok = (bestL_local < 1e-5)
    out["calibration"]["global_recovery_ok"] = bool(calib_global_ok)
    out["calibration"]["local_basin_ok"] = bool(calib_local_ok)
    print(f"  -> from-scratch global recovery calibrated: {calib_global_ok} "
          f"(local-basin convergence works: {calib_local_ok})")

    # --- the clamp ---
    nC, eC, (s, t) = load_clamp()
    stC = degree_stats(nC, eC)
    print("\nThe 48-vertex Mycielski clamp:")
    print(f"  n={stC['n']} E={stC['edges']} max_deg={stC['max_deg']} "
          f"(at vertex {stC['argmax_deg']}) min_deg={stC['min_deg']} "
          f"over_det={stC['over_determination']:+d}")
    best, bp = try_realize(nC, eC, starts=60)
    realized = best < 1e-5
    print(f"  best max edge-length error over 60 starts: {best:.3e} "
          f"-> realizable(numerical): {realized}")
    prof = edge_error_profile(bp, eC, top=8) if bp is not None else []
    print("  largest residual edges (obstruction localization):")
    deg = [0] * nC
    for a, b in eC:
        deg[a] += 1
        deg[b] += 1
    for err, i, j in prof:
        print(f"    edge ({i:2d},{j:2d}) err={err:.3f}  "
              f"deg({i})={deg[i]} deg({j})={deg[j]}")
    out["clamp"] = {"best_max_edge_err": best, "realized_numerical": realized,
                    "top_residual_edges": [[round(e, 4), i, j, deg[i], deg[j]]
                                           for e, i, j in prof], **stC}

    # --- comparison to a realizable lineage graph (P_510) ---
    print("\nComparison: the realizable lineage (Polymath-510) is SPARSE:")
    base = parse_vtx(VTX / "510.vtx")
    edges510 = parse_edges(EDGE / "510.edge")
    st510 = degree_stats(len(base), [tuple(e) for e in edges510])
    out["polymath510"] = st510
    print(f"  P_510: n={st510['n']} E={st510['edges']} max_deg={st510['max_deg']} "
          f"avg_deg={st510['avg_deg']} over_det={st510['over_determination']:+d}")
    print(f"  (realizable, but L45: NO clamp -> forced-different = adjacent)")

    # --- the structural picture, HONESTLY gated on calibration ---
    print("\n" + "=" * 74)
    if realized:
        verdict = "REALIZED -- VERIFY IMMEDIATELY (would supply the chi-6 ingredient)"
    elif calib_global_ok:
        verdict = ("NON-realizable: strong numerical evidence (solver IS calibrated: "
                   "it recovers same-scale realizable graphs from scratch)")
    else:
        verdict = ("INCONCLUSIVE: the from-scratch solver is NOT calibrated (it also "
                   "fails to recover the realizable lattice), so the clamp's failure "
                   "is solver weakness, not proven non-realizability")
    out["verdict"] = verdict
    out["heuristics_invalidated"] = (
        "Both cheap obstruction heuristics are INVALID, shown by the realizable "
        "P_510: over-determination (P_510 +%d > clamp +%d, yet P_510 realizes) and "
        "max-degree (P_510 deg %d > clamp deg %d, yet P_510 realizes) do NOT predict "
        "non-realizability. So W3 cannot be decided by counting; the real obstruction "
        "is the algebraic solvability of the cocircularity system (L42 Lemma L "
        "lineage), not a DOF or degree count."
        % (st510["over_determination"], stC["over_determination"],
           st510["max_deg"], stC["max_deg"]))
    out["refined_target"] = (
        "Refined W3 target: decide realizability of a SMALL clamp exactly (Groebner, "
        "feasible ~<=14 v as in h2_groebner_moser14.py) -- but the min clamp order is "
        ">=9 and likely >14, so first find a small/low-degree clamp (split a small "
        "K4-free 6-critical graph; Schrijver SG(14,5), triangle-free chi=6 vertex-"
        "critical, 196 v, is a bounded-degree candidate). Open: can a realizable "
        "(sparse) graph host a clamp, which the realizable lineage (L45) never does?")
    print("VERDICT:", verdict)
    print("HEURISTICS:", out["heuristics_invalidated"])
    print("NEXT:", out["refined_target"])

    os.makedirs(CACHE, exist_ok=True)
    json.dump(out, open(os.path.join(CACHE, "realizability_w3_clamp.json"), "w"),
              indent=2)
    print("\narchived _cache/realizability_w3_clamp.json")
    return out


if __name__ == "__main__":
    main()
