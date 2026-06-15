r"""e3r: diagnose the order-2 X_23 blocker before committing to the multi-week
raw-solver backend (the L48/L50 prerequisite for the measurable chi_m >= 6 frontier).

e3q block-diagonalizes the order-2 moment SDP by the S_k color symmetry, shrinking
the PSD BLOCKS (max side ~735 on X_23) but NOT the moment-VARIABLE count n_orb
(~48342 after the O(2)-congruence reduction). It then builds, per block, a DENSE
affine map T of shape (mult^2, n_orb) -- ~210 GiB on X_23 -- and that dense assembly
is the wall (e3q returns SKIPPED_AFFINE_MAP_TOO_LARGE).

Two independent levers could make X_23 order-2 run; this probe measures both, to
decide which build path is warranted:

  (1) EXTRA SYMMETRY. If X_23 has a nontrivial geometric automorphism group
      Aut(X_23) (isometries permuting its 23 points), the order-2 moment matrix is
      ALSO Aut-invariant, so the combined (S_k x Aut) action block-diagonalizes
      FURTHER, shrinking mult below 735. A large Aut could make the existing dense
      code fit with no new solver. Part 1 computes |Aut(X_23)| exactly (isometries =
      automorphisms of the distance-class-labelled complete graph).

  (2) AFFINE-MAP SPARSITY. If the per-block coefficient matrices C_o = F_s^T E_o F_t
      are mostly ZERO, T is sparse and a scipy.sparse assembly (a ~day change) fits
      X_23 without the full raw-solver backend. If C_o is dense (the symmetry-adapted
      basis F mixes the basis, so projecting a sparse orbit indicator E_o yields a
      dense small matrix), sparse-T cannot save it and the raw low-rank/solver path
      (weeks) is genuinely required. Part 2 measures the ACTUAL density of T's
      largest block on runnable configs (Moser n=7, double-Moser n=10) and
      extrapolates the X_23 memory under dense vs sparse assembly.

Output: a clear verdict on the build path (extra symmetry available? sparse-T
sufficient? or raw-solver backend unavoidable?), no bound moved.
"""
from __future__ import annotations

import json
import time
from collections import defaultdict

import numpy as np

from experiments.fractional.e3c_ofv_lp_dual import CACHE
from experiments.fractional.e3l_multiclass_iec import (
    build_exact_config, _moser_vertices_exact,
)
from experiments.fractional.e3m_moment_backend import _double_moser_vertices_exact
from experiments.fractional.e3n_moment_order2 import _canon
from experiments.fractional.e3q_blockdiag_order2 import (
    _build_basis, _symmetry_adapted_blocks, _orbit_rep, _congruence_rep,
)


# ---------------------------------------------------------------------------
# Part 1: geometric automorphism group of X_23 (extra symmetry to exploit?).
# ---------------------------------------------------------------------------

def x23_automorphism_group():
    """|Aut(X_23)| = isometries of the plane permuting the 23 points = automorphisms
    of the complete graph on 23 nodes with each edge labelled by its exact
    squared-distance class. Computed via networkx VF2 with edge-label matching."""
    import networkx as nx
    from networkx.algorithms.isomorphism import GraphMatcher, categorical_edge_match
    from experiments.fractional.e3i_ambrus_reproduce import (
        load_config, parse_points_exact, exact_unit_distance_graph,
    )

    cfg = load_config()
    pts = parse_points_exact(cfg)
    n = len(pts)
    import sympy as sp
    # distance-class id per pair (exact)
    d2 = {}
    distinct = {}
    for i in range(n):
        for j in range(i + 1, n):
            dd = sp.simplify((sp.re(pts[i] - pts[j]))**2 + (sp.im(pts[i] - pts[j]))**2)
            key = sp.srepr(sp.nsimplify(dd))
            if key not in distinct:
                distinct[key] = len(distinct)
            d2[(i, j)] = distinct[key]

    G = nx.complete_graph(n)
    for (i, j), lab in d2.items():
        G[i][j]["d"] = lab

    em = categorical_edge_match("d", -1)
    gm = GraphMatcher(G, G, edge_match=em)
    autos = list(gm.isomorphisms_iter())
    # orbits of the vertex set under Aut
    perms = [tuple(a[v] for v in range(n)) for a in autos]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for p in perms:
        for v in range(n):
            parent[find(v)] = find(p[v])
    orbits = defaultdict(list)
    for v in range(n):
        orbits[find(v)].append(v)
    nontrivial = [p for p in perms if any(p[v] != v for v in range(n))]
    return {
        "n_points": n, "n_distinct_distances": len(distinct),
        "aut_order": len(perms), "n_nontrivial": len(nontrivial),
        "n_vertex_orbits": len(orbits),
        "orbit_sizes": sorted(len(o) for o in orbits.values()),
    }


# ---------------------------------------------------------------------------
# Part 2: density of the per-block order-2 affine map T on runnable configs.
# ---------------------------------------------------------------------------

def affine_map_density(X, dc, edges, k, congruence_reduce, largest_only=True):
    """Replicate e3q's per-block affine-map construction far enough to MEASURE T's
    density (no solve). Returns the orbit-variable count, block sizes, and -- for the
    largest block (which dominates the memory) -- the dense element count vs the
    actual nonzero count."""
    n = X.shape[0]
    edges = set((min(a, b), max(a, b)) for (a, b) in edges)
    basis = _build_basis(n, k, edges)
    D = len(basis)

    if congruence_reduce:
        vals = sorted({dc[(i, j)] for i in range(n) for j in range(i + 1, n)},
                      key=lambda e: float(e))
        valpos = {v: idx for idx, v in enumerate(vals)}
        dist_id = {(i, j): valpos[dc[(i, j)]]
                   for i in range(n) for j in range(i + 1, n)}
        keyfn = lambda kk: _congruence_rep(kk, dist_id, k)
    else:
        keyfn = lambda kk: _orbit_rep(kk, k)

    orbit_positions = defaultdict(list)
    for a in range(D):
        Ba = basis[a]
        for b in range(D):
            key = _canon(Ba | basis[b], edges)
            if key in ("zero", "one"):
                continue
            orbit_positions[keyfn(key)].append((a, b))
    orbits = list(orbit_positions)
    n_orb = len(orbits)
    orbit_ab = [(np.array([a for (a, _) in orbit_positions[o]], dtype=int),
                 np.array([b for (_, b) in orbit_positions[o]], dtype=int))
                for o in orbits]

    blocks = _symmetry_adapted_blocks(basis, k)
    block_mults = sorted((len(F) for F, _ in blocks), reverse=True)

    # Measure T density on the largest block(s).
    targets = [max(range(len(blocks)), key=lambda i: len(blocks[i][0]))] if largest_only \
        else list(range(len(blocks)))
    per_block = []
    for bi in targets:
        F_list, d = blocks[bi]
        mult = len(F_list)
        Fstack = np.stack(F_list, axis=0)        # (mult, D, d)
        nnz = 0
        dense = mult * mult * n_orb
        for (a_idx, b_idx) in orbit_ab:
            if a_idx.size == 0:
                continue
            A = Fstack[:, a_idx, :]
            B = Fstack[:, b_idx, :]
            Co = np.einsum('spl,tpl->st', A, B) / d
            nnz += int(np.count_nonzero(np.abs(Co) > 1e-12))
        per_block.append({"block_mult": mult, "irrep_dim": d,
                          "dense_entries": dense, "nnz": nnz,
                          "density": (nnz / dense) if dense else 0.0})

    total_dense_all_blocks = sum(m * m for m in block_mults) * n_orb
    return {
        "n": n, "k": k, "congruence_reduce": congruence_reduce,
        "basis_size": D, "n_orbit_vars": n_orb,
        "n_blocks": len(blocks), "max_block_mult": block_mults[0],
        "block_mults_top5": block_mults[:5],
        "total_dense_T_entries_all_blocks": total_dense_all_blocks,
        "total_dense_T_GiB": round(total_dense_all_blocks * 8 / 2**30, 3),
        "largest_block_density": per_block,
    }


def main():
    print("e3r: order-2 X_23 blocker diagnosis (extra symmetry? sparse-T enough?)")
    print("=" * 78, flush=True)

    print("\n[Part 1] Geometric automorphism group of X_23 ...", flush=True)
    t0 = time.time()
    aut = x23_automorphism_group()
    print(f"  |Aut(X_23)| = {aut['aut_order']}  (nontrivial: {aut['n_nontrivial']}); "
          f"vertex orbits: {aut['n_vertex_orbits']} sizes {aut['orbit_sizes']}; "
          f"distinct sq-dists {aut['n_distinct_distances']}  ({time.time()-t0:.1f}s)",
          flush=True)
    if aut["aut_order"] > 1:
        print(f"  => EXTRA SYMMETRY available: the order-2 SDP can be quotiented by "
              f"(S_k x Aut), shrinking blocks ~{aut['aut_order']}x.", flush=True)
    else:
        print("  => X_23 is asymmetric (Aut trivial): no extra geometric symmetry; "
              "the block size is fixed by S_k alone.", flush=True)

    print("\n[Part 2] Order-2 affine-map density on runnable configs "
          "(largest block) ...", flush=True)
    rows = []
    probes = [("moser7", _moser_vertices_exact, 5),
              ("double_moser10", _double_moser_vertices_exact, 4)]
    for name, fn, k in probes:
        X, dc, edges = build_exact_config(fn())
        for cong in (False, True):
            t0 = time.time()
            r = affine_map_density(X, dc, edges, k, congruence_reduce=cong)
            lb = r["largest_block_density"][0]
            tag = "cong" if cong else "S_k "
            print(f"  [{name} k={k} {tag}] n_orb={r['n_orbit_vars']:6d}  "
                  f"max_block={r['max_block_mult']:3d}  largest-block T density="
                  f"{lb['density']*100:.1f}%  ({lb['nnz']}/{lb['dense_entries']})  "
                  f"total dense T={r['total_dense_T_GiB']} GiB  ({time.time()-t0:.1f}s)",
                  flush=True)
            r["config"] = name
            rows.append(r)

    # Verdict: extrapolate the largest-block density to X_23 (max_block ~735,
    # n_orb ~48342 congruence-reduced) under dense vs sparse assembly.
    X23_MAX_BLOCK = 735
    X23_N_ORB_CONG = 48342
    dense_x23 = X23_MAX_BLOCK ** 2 * X23_N_ORB_CONG * 8 / 2**30
    cong_densities = [r["largest_block_density"][0]["density"] for r in rows
                      if r["congruence_reduce"]]
    dmax = max(cong_densities) if cong_densities else 1.0
    sparse_x23 = dense_x23 * dmax * 1.5   # CSC overhead ~1.5x (values + indices)
    print("\n" + "=" * 78)
    print("VERDICT (X_23 order-2, largest block, congruence-reduced):")
    print(f"  dense affine map (largest block): ~{dense_x23:.0f} GiB (the wall)")
    print(f"  measured largest-block density (congruence): max {dmax*100:.1f}%")
    print(f"  => sparse-T (scipy.sparse) largest block: ~{sparse_x23:.1f} GiB")
    if sparse_x23 < 16:
        print("  PATH: a scipy.sparse affine-map assembly likely FITS -- try that "
              "before the raw-solver backend.")
    else:
        print("  PATH: sparse-T does NOT fit either; the raw low-rank/solver backend "
              "(de Laat-Vallentin) is genuinely required, unless Part-1 symmetry "
              "shrinks the block first.")

    CACHE.mkdir(exist_ok=True)
    out = {"experiment": "e3r_order2_sparsity_probe", "x23_aut": aut,
           "density_rows": rows,
           "verdict": {"x23_dense_GiB": dense_x23,
                       "max_cong_density": dmax,
                       "x23_sparse_GiB_est": sparse_x23,
                       "sparse_fits": bool(sparse_x23 < 16)}}
    with (CACHE / "e3r_order2_sparsity_probe.json").open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\narchived: {CACHE / 'e3r_order2_sparsity_probe.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
