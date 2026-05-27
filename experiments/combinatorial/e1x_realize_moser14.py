r"""e1x: UDG realizability of the 14-vertex Moser x Moser no-K_4 chi=5 graph.

Architecture 1, BUILDER pass on L21's open realizability question.

The graph (from L21) is:
  H_1 = Moser spindle (canonical coordinates in Q(sqrt 3, sqrt 11))
  H_2 = Moser spindle (a SECOND copy, placed at unknown rigid-motion pose)
  B^* = 14 cross-edges between H_1 and H_2:
       {(0,0),(0,1),(0,3),(0,4),(0,6),(1,0),(2,6),(3,6),(4,6),
        (5,1),(6,1),(6,3),(6,5),(6,6)}

Question: does there exist a rigid motion phi: R^2 -> R^2 (rotation by theta +
translation (t_x, t_y), with optional reflection) such that H_2 = phi(Moser
spindle) and all 14 bridges in B^* are simultaneously unit-distance edges?
The pose has 3 (or 4 with reflection) real DoF; 14 equations. Generically
overdetermined.

Method:
  1. Set up the 14 bridge constraints as polynomial equations in (c, s, tx, ty)
     with c^2 + s^2 = 1 over Q(sqrt 3, sqrt 11) (and a reflection sign).
  2. Numerical feasibility: multi-start scipy.optimize on the squared-residual
     sum. Report global min and per-bridge gap.
  3. Maximum realizable subset: greedy / SAT-style search for the largest
     B' subset of B^* that IS realizable. Quantifies the "realizability cost".
  4. Search across automorphisms of the Moser spindle (relabelings of H_2),
     since the L21 bridge set is index-based and a different labeling might
     align bridges more favorably.

Caches:
  experiments/combinatorial/_cache/e1x_realize_moser14.json
"""

from __future__ import annotations

import itertools
import json
import math
import pathlib
import time

import numpy as np
import sympy as sp
from scipy.optimize import minimize

from experiments._shared.unit_distance_graph import moser_spindle


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

# L21 bridge set: first index = H_1 vertex, second index = H_2 vertex.
BRIDGES = [
    (0, 0), (0, 1), (0, 3), (0, 4), (0, 6),
    (1, 0),
    (2, 6), (3, 6), (4, 6),
    (5, 1),
    (6, 1), (6, 3), (6, 5), (6, 6),
]


def moser_coords_numpy():
    """Numerical (high-precision) Moser spindle coordinates as a (7, 2) ndarray."""
    g = moser_spindle()
    coords = []
    for v in g.vertices:
        x = float(sp.N(v[0], 50))
        y = float(sp.N(v[1], 50))
        coords.append([x, y])
    arr = np.array(coords, dtype=np.float64)
    return arr, g


def moser_automorphisms(g):
    """Return list of permutations of vertices that are graph automorphisms
    AND realized by an isometry (Euclidean rigid motion or reflection) of the
    canonical embedding. We brute-force: enumerate all isometries that map the
    7-vertex set to itself.

    For the Moser spindle the automorphism group is Z_2 x Z_2 (size 4):
    identity, the swap of the two rhombi (across the central axis), and
    reflection along the central axis. Empirically we find all of them by
    checking which permutations of 0..6 preserve all edges and pairwise
    distances. We return the full automorphism list (as tuples).
    """
    coords = np.array([[float(sp.N(p[0], 50)), float(sp.N(p[1], 50))] for p in g.vertices])
    edges = set(tuple(sorted(e)) for e in g.edges())

    # All combinatorial automorphisms first: bijections preserving edges.
    aut = []
    for perm in itertools.permutations(range(7)):
        good = True
        for (u, v) in edges:
            pu, pv = perm[u], perm[v]
            if tuple(sorted((pu, pv))) not in edges:
                good = False
                break
        if not good:
            continue
        # Also require it to be realized by isometry, i.e. all pairwise
        # distances preserved. (For UDGs this is automatic if edges
        # preserved AND graph reconstructs metric, but Moser is so small
        # we double-check.)
        ok = True
        for i in range(7):
            for j in range(i + 1, 7):
                d_orig = np.linalg.norm(coords[i] - coords[j])
                d_perm = np.linalg.norm(coords[perm[i]] - coords[perm[j]])
                if abs(d_orig - d_perm) > 1e-9:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            aut.append(perm)
    return aut


def residual_per_bridge(pose, h1_coords, h2_coords, bridges, reflect=False):
    """Compute per-bridge squared distance error.

    pose: (tx, ty, theta).
    h1_coords: (7, 2) for H_1 vertices.
    h2_coords: (7, 2) raw H_2 vertices (will be transformed by phi).
    bridges: list of (i, j).
    reflect: if True, multiply x-coord of H_2 by -1 first (a mirror reflection).

    Returns (residuals, dists) where residuals[k] = (||phi(v_j) - v_i||^2 - 1)
    and dists[k] = ||phi(v_j) - v_i||.
    """
    tx, ty, theta = pose
    c, s = np.cos(theta), np.sin(theta)
    R = np.array([[c, -s], [s, c]])
    if reflect:
        ref = np.diag([-1.0, 1.0])
        h2_transformed = (ref @ h2_coords.T).T
    else:
        h2_transformed = h2_coords
    h2_phi = h2_transformed @ R.T + np.array([tx, ty])  # (7, 2)
    residuals = []
    dists = []
    for (i, j) in bridges:
        d = h2_phi[j] - h1_coords[i]
        d2 = float(d[0] ** 2 + d[1] ** 2)
        residuals.append(d2 - 1.0)
        dists.append(math.sqrt(max(d2, 0.0)))
    return np.array(residuals), np.array(dists)


def total_residual(pose, h1_coords, h2_coords, bridges, reflect=False):
    """Sum of squared residuals across all bridges."""
    r, _ = residual_per_bridge(pose, h1_coords, h2_coords, bridges, reflect=reflect)
    return float(np.sum(r * r))


def total_residual_grad(pose, h1_coords, h2_coords, bridges, reflect=False):
    """Analytic gradient of total_residual wrt (tx, ty, theta).

    For each bridge (i,j):
      let q = phi(v_j) = R_theta * (refl(v_j)) + t.
      f_k = ||q - p_i||^2 - 1 = (q-p_i).(q-p_i) - 1
      L = sum_k f_k^2
      dL/dtx = sum_k 2 f_k * 2 (q_x - p_ix)
      dL/dty = sum_k 2 f_k * 2 (q_y - p_iy)
      dL/dtheta = sum_k 2 f_k * 2 (q - p_i) . dq/dtheta
        where dq/dtheta = R'_theta * v_j_ref.
    """
    tx, ty, theta = pose
    c, s = np.cos(theta), np.sin(theta)
    R = np.array([[c, -s], [s, c]])
    dR = np.array([[-s, -c], [c, -s]])
    if reflect:
        ref = np.diag([-1.0, 1.0])
        h2_t = (ref @ h2_coords.T).T
    else:
        h2_t = h2_coords
    h2_phi = h2_t @ R.T + np.array([tx, ty])
    h2_dphi_dtheta = h2_t @ dR.T

    g_tx = 0.0
    g_ty = 0.0
    g_th = 0.0
    for (i, j) in bridges:
        d = h2_phi[j] - h1_coords[i]
        f_k = float(d[0] ** 2 + d[1] ** 2 - 1.0)
        g_tx += 4.0 * f_k * d[0]
        g_ty += 4.0 * f_k * d[1]
        dq = h2_dphi_dtheta[j]
        g_th += 4.0 * f_k * (d[0] * dq[0] + d[1] * dq[1])
    return np.array([g_tx, g_ty, g_th])


def optimize_pose(h1_coords, h2_coords, bridges, reflect=False, n_starts=400, seed=0):
    """Multi-start L-BFGS-B optimization on (tx, ty, theta).

    Returns (best_pose, best_loss, best_per_bridge_dist, all_finals).
    """
    rng = np.random.default_rng(seed)
    best_loss = np.inf
    best_pose = None
    best_dists = None
    all_finals = []
    # Bounds: tx, ty in [-3, 3] (Moser is roughly diameter 2.something);
    # theta in [-pi, pi]. Larger than needed but the gradient pulls it in.
    for k in range(n_starts):
        tx0 = rng.uniform(-3.0, 3.0)
        ty0 = rng.uniform(-3.0, 3.0)
        th0 = rng.uniform(-math.pi, math.pi)
        pose0 = np.array([tx0, ty0, th0])
        res = minimize(
            total_residual, pose0,
            args=(h1_coords, h2_coords, bridges, reflect),
            jac=total_residual_grad,
            method="L-BFGS-B",
            options={"maxiter": 500, "ftol": 1e-18, "gtol": 1e-14},
        )
        all_finals.append({"loss": float(res.fun), "pose": res.x.tolist()})
        if res.fun < best_loss:
            best_loss = float(res.fun)
            best_pose = res.x.copy()
            _, best_dists = residual_per_bridge(best_pose, h1_coords, h2_coords, bridges, reflect=reflect)
    return best_pose, best_loss, best_dists, all_finals


def is_subset_realizable(h1_coords, h2_coords, sub_bridges, reflect=False,
                         n_starts=80, tol=1e-7, seed=0):
    """Check if a given subset of bridges can be simultaneously realized.

    Returns (realizable, pose, max_err).
    """
    if len(sub_bridges) == 0:
        return True, np.zeros(3), 0.0
    p, loss, dists, _ = optimize_pose(
        h1_coords, h2_coords, sub_bridges, reflect=reflect,
        n_starts=n_starts, seed=seed,
    )
    max_err = float(np.max(np.abs(dists - 1.0)))
    return max_err < tol, p, max_err


def maximum_realizable_subset(h1_coords, h2_coords, bridges, reflect=False,
                              n_starts=200, tol=1e-7, seed=0,
                              enumerate_up_to=8):
    """Find the maximum subset B' of bridges that IS simultaneously realizable.

    Subset realizability is downward-closed: if pose phi realizes set S, it
    realizes every subset of S. So the maximum realizable size is the largest
    k such that some k-subset is realizable. Brute-force enumeration from
    enumerate_up_to down to greedy+1 suffices.

    For |B| = 14, the safety net is C(14, 8) = 3003 subsets. If size 8 is
    exhaustively unrealizable, sizes 9..14 are all unrealizable by monotonicity.

    Returns (subset, pose, max_err).
    """
    # Phase (a): drop-worst
    current = list(bridges)
    pose, loss, dists, _ = optimize_pose(
        h1_coords, h2_coords, current, reflect=reflect,
        n_starts=n_starts, seed=seed,
    )
    while True:
        r, dists = residual_per_bridge(pose, h1_coords, h2_coords, current, reflect=reflect)
        max_err = float(np.max(np.abs(dists - 1.0)))
        if max_err < tol:
            break
        worst_idx = int(np.argmax(np.abs(dists - 1.0)))
        current = current[:worst_idx] + current[worst_idx + 1:]
        if not current:
            break
        pose, loss, dists, _ = optimize_pose(
            h1_coords, h2_coords, current, reflect=reflect,
            n_starts=50, seed=seed + 1,
        )
    greedy_size = len(current)
    greedy_subset = list(current)
    greedy_pose = pose
    greedy_err = max_err if current else 0.0

    # Phase (b): exhaustive search for larger subsets, sizes greedy_size+1 .. enumerate_up_to
    best_subset = greedy_subset
    best_pose = greedy_pose
    best_err = greedy_err

    for target_size in range(min(enumerate_up_to, len(bridges)), greedy_size, -1):
        # Iterate over all subsets of size target_size, ordered by total "promise" score.
        # We use the per-bridge errors from the full-B fit (heuristically, smaller errors
        # are more compatible). But for honesty we just try all subsets.
        found = False
        n_subs = math.comb(len(bridges), target_size)
        print(f"    enumerating C({len(bridges)}, {target_size}) = {n_subs} subsets ...")
        # Try with low n_starts first; only escalate if borderline.
        ns = 40
        for sub in itertools.combinations(bridges, target_size):
            ok, p, err = is_subset_realizable(
                h1_coords, h2_coords, list(sub), reflect=reflect,
                n_starts=ns, tol=tol, seed=seed + 7,
            )
            if ok:
                # Confirm with more starts to avoid local-min false positive.
                ok2, p2, err2 = is_subset_realizable(
                    h1_coords, h2_coords, list(sub), reflect=reflect,
                    n_starts=200, tol=tol, seed=seed + 17,
                )
                if ok2:
                    best_subset = list(sub)
                    best_pose = p2
                    best_err = err2
                    found = True
                    break
        if found:
            print(f"    FOUND a realizable subset of size {target_size}")
            return best_subset, best_pose, best_err
    return best_subset, best_pose, best_err


def circumcircle(p1, p2, p3):
    """Return (center, radius) of the circle through p1, p2, p3 in R^2,
    or (None, None) if collinear."""
    ax, ay = p1
    bx, by = p2
    cx, cy = p3
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-14:
        return None, None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay)
          + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx)
          + (cx * cx + cy * cy) * (bx - ax)) / d
    r = math.sqrt((ax - ux) ** 2 + (ay - uy) ** 2)
    return (ux, uy), r


def cocircularity_obstruction(coords, idxs, tol=1e-9):
    """For a set of points indexed by idxs in coords, check if they are
    cocircular AND if the common radius equals 1.

    Returns dict {cocircular, on_unit_circle, common_radius, n_points}.

    Interpretation: if a single H_2 vertex must be at unit distance from
    several H_1 points (via bridges into it), those H_1 points (in the
    canonical H_1 frame, up to rigid motion) must all lie on a circle of
    radius 1 around the prospective H_2 vertex position. Two facts:
      (a) they must be cocircular (sit on a common circle), and
      (b) that circle must have radius 1.

    Returns the structural diagnostic without optimization.
    """
    pts = [coords[i] for i in idxs]
    n = len(idxs)
    if n < 3:
        # 1 or 2 points: no obstruction.
        return {"cocircular": True, "on_unit_circle": True,
                "common_radius": None, "n_points": n}
    centers_radii = []
    for trio in itertools.combinations(range(n), 3):
        c, r = circumcircle(pts[trio[0]], pts[trio[1]], pts[trio[2]])
        if c is not None:
            centers_radii.append((c, r))
    if not centers_radii:
        return {"cocircular": False, "on_unit_circle": False,
                "common_radius": None, "n_points": n, "collinear": True}
    radii = [r for _, r in centers_radii]
    centers = [c for c, _ in centers_radii]
    max_r, min_r = max(radii), min(radii)
    if len(centers) >= 2:
        max_center_diff = max(
            math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)
            for c1, c2 in itertools.combinations(centers, 2)
        )
    else:
        max_center_diff = 0.0
    cocircular = (max_r - min_r) < tol and max_center_diff < tol
    on_unit_circle = abs(max_r - 1.0) < tol if cocircular else False
    return {"cocircular": cocircular, "on_unit_circle": on_unit_circle,
            "common_radius": max_r if cocircular else None,
            "radius_range": [min_r, max_r], "n_points": n}


def structural_obstruction_analysis(h1_coords, bridges):
    """Symmetric cocircularity check at every bridge-endpoint of both sides.

    For each H_2 vertex j receiving bridges from H_1 vertex set N_2(j), the
    H_1 vertices in N_2(j) (in H_1 frame) must be cocircular at radius 1
    (since they all need to be unit-distance from the SAME H_2 point under
    some rigid motion, equivalent to being on a unit circle).

    Symmetrically for H_1 vertices i sending bridges to N_1(i) in H_2 frame
    (H_2 = same Moser coords, modulo rigid motion).

    Returns dict with per-side analysis.
    """
    from collections import defaultdict
    h1_to_h2 = defaultdict(list)
    h2_to_h1 = defaultdict(list)
    for (i, j) in bridges:
        h1_to_h2[i].append(j)
        h2_to_h1[j].append(i)
    rows = []
    for j, h1s in sorted(h2_to_h1.items()):
        diag = cocircularity_obstruction(h1_coords, sorted(h1s))
        rows.append({"side": "H_2 receives", "vertex": j,
                     "bridge_endpoints": sorted(h1s), **diag})
    for i, h2s in sorted(h1_to_h2.items()):
        # H_2 uses same coords as H_1 up to rigid motion -- check on H_1-relative
        # coords (i.e. the canonical Moser coords are the orbit-representative).
        diag = cocircularity_obstruction(h1_coords, sorted(h2s))
        rows.append({"side": "H_1 sends", "vertex": i,
                     "bridge_endpoints": sorted(h2s), **diag})
    return rows


def analyze_pose(pose, h1_coords, h2_coords, bridges, reflect):
    """Detailed bridge-by-bridge analysis at a given pose."""
    r, dists = residual_per_bridge(pose, h1_coords, h2_coords, bridges, reflect=reflect)
    rows = []
    for k, (i, j) in enumerate(bridges):
        rows.append({
            "bridge": (i, j),
            "dist": float(dists[k]),
            "abs_err": float(abs(dists[k] - 1.0)),
        })
    return rows


def main():
    print("e1x: UDG realizability of 14-vertex Moser x Moser no-K_4 chi=5 graph")
    print("=" * 78)
    print()
    print(f"|B^*| = {len(BRIDGES)} bridges:")
    print(f"  {BRIDGES}")
    print()

    h1_coords, g = moser_coords_numpy()
    h2_coords_raw = h1_coords.copy()  # H_2 is a second copy of the Moser spindle

    print("Moser spindle canonical coords (numerical):")
    for i, v in enumerate(h1_coords):
        print(f"  v_{i} = ({v[0]:+.6f}, {v[1]:+.6f})")
    print()

    auts = moser_automorphisms(g)
    print(f"Moser spindle has {len(auts)} automorphisms realized by isometry:")
    for k, p in enumerate(auts):
        print(f"  aut_{k}: {p}")
    print()

    # ----- Phase 0: structural cocircularity obstruction -----
    print("Phase 0: structural cocircularity obstruction (no optimization)")
    print("  For each vertex v receiving k bridges, the k endpoints in the other")
    print("  half must be cocircular at radius 1 (in canonical Moser frame).")
    print()
    obs_rows = structural_obstruction_analysis(h1_coords, BRIDGES)
    has_obstruction = False
    obstruction_rows = []
    for row in obs_rows:
        n = row["n_points"]
        if n < 3:
            note = f"only {n} bridge endpoints (no cocircularity required)"
            ok = True
        elif not row["cocircular"]:
            note = (f"NOT cocircular; radius range "
                    f"[{row['radius_range'][0]:.4f}, {row['radius_range'][1]:.4f}]")
            ok = False
        elif not row["on_unit_circle"]:
            note = f"cocircular at radius {row['common_radius']:.6f} != 1"
            ok = False
        else:
            note = "cocircular at radius 1 (compatible)"
            ok = True
        if not ok:
            has_obstruction = True
            obstruction_rows.append(row)
        print(f"  {row['side']:>12s} v_{row['vertex']} via {row['bridge_endpoints']}: {note}")
    print()
    if has_obstruction:
        print("  STRUCTURAL OBSTRUCTION FOUND: at least one bridge endpoint requires")
        print("  cocircular partners at radius 1, but the Moser spindle's vertices")
        print("  don't satisfy this. The 14-vertex graph is NOT UDG-realizable,")
        print("  even before numerical optimization.")
    else:
        print("  No structural obstruction from cocircularity alone; need optimization.")
    print()

    seed = 12345

    # ----- Phase 1: full bridge set with identity labeling, no reflection -----
    print("Phase 1: optimize over (tx, ty, theta) with identity H_2 labeling, no reflection")
    t0 = time.time()
    pose_id, loss_id, dists_id, _ = optimize_pose(
        h1_coords, h2_coords_raw, BRIDGES, reflect=False, n_starts=500, seed=seed
    )
    t_id = time.time() - t0
    max_err_id = float(np.max(np.abs(dists_id - 1.0)))
    print(f"  best total loss = {loss_id:.6e}  (max per-bridge |d - 1| = {max_err_id:.6e}, t={t_id:.2f}s)")
    print(f"  best pose: tx={pose_id[0]:+.6f}, ty={pose_id[1]:+.6f}, theta={pose_id[2]:+.6f} rad")

    # ----- Phase 2: with reflection -----
    print()
    print("Phase 2: optimize with reflection (H_2 chirality flipped)")
    t0 = time.time()
    pose_ref, loss_ref, dists_ref, _ = optimize_pose(
        h1_coords, h2_coords_raw, BRIDGES, reflect=True, n_starts=500, seed=seed + 1
    )
    t_ref = time.time() - t0
    max_err_ref = float(np.max(np.abs(dists_ref - 1.0)))
    print(f"  best total loss = {loss_ref:.6e}  (max per-bridge |d - 1| = {max_err_ref:.6e}, t={t_ref:.2f}s)")
    print(f"  best pose: tx={pose_ref[0]:+.6f}, ty={pose_ref[1]:+.6f}, theta={pose_ref[2]:+.6f} rad")

    # ----- Phase 3: across all automorphism relabelings of H_2 -----
    print()
    print("Phase 3: optimize across all Moser automorphism relabelings of H_2 + both chiralities")
    aut_results = []
    for ai, aut in enumerate(auts):
        # Relabel bridges: bridge (i, j) becomes (i, aut[j]) effectively.
        # Equivalently: leave bridges fixed but relabel H_2 coords by the inverse.
        # We act on H_2 vertices by the permutation: new_coords[k] = old_coords[aut[k]]
        # No: we want bridge (i, j) to mean "i in H_1 connects to v_{aut(j)} in H_2",
        # so we can either relabel bridges or permute coordinates.
        # Permute coordinates: h2_coords_relabeled[k] = h2_coords_raw[aut[k]]
        # Then bridge (i, j) means i in H_1 to h2_coords_relabeled[j] = h2_coords_raw[aut[j]].
        # This is equivalent to using the original bridges with permuted H_2 labels.
        h2_relab = h2_coords_raw[list(aut)]
        for ref_flag in (False, True):
            p, loss, dists, _ = optimize_pose(
                h1_coords, h2_relab, BRIDGES, reflect=ref_flag,
                n_starts=200, seed=seed + 100 * ai + (1 if ref_flag else 0)
            )
            max_err = float(np.max(np.abs(dists - 1.0)))
            aut_results.append({
                "aut_idx": ai,
                "aut": list(aut),
                "reflect": ref_flag,
                "loss": float(loss),
                "max_err": max_err,
                "pose": p.tolist(),
            })
            print(f"  aut_{ai} {aut}, reflect={ref_flag}: loss={loss:.4e}, max|d-1|={max_err:.4e}")

    best_aut = min(aut_results, key=lambda r: r["loss"])
    print()
    print(f"BEST across all automorphisms+chiralities: loss = {best_aut['loss']:.6e}, "
          f"max|d-1| = {best_aut['max_err']:.6e}")
    print(f"  aut = {best_aut['aut']}, reflect = {best_aut['reflect']}")
    print(f"  pose = {best_aut['pose']}")

    # ----- Phase 4: detailed per-bridge analysis at the best pose -----
    best_aut_perm = best_aut["aut"]
    best_pose = np.array(best_aut["pose"])
    h2_best = h2_coords_raw[best_aut_perm]
    bridge_rows = analyze_pose(best_pose, h1_coords, h2_best, BRIDGES, reflect=best_aut["reflect"])

    print()
    print("Per-bridge analysis at best pose:")
    print(f"  {'(i,j)':>8s}  {'dist':>10s}  {'|d-1|':>12s}")
    for row in sorted(bridge_rows, key=lambda r: r["abs_err"]):
        print(f"  {str(row['bridge']):>8s}  {row['dist']:>10.6f}  {row['abs_err']:>12.6e}")

    # ----- Phase 5: maximum realizable subset -----
    print()
    print("Phase 5: maximum realizable subset (iterative drop-worst)")
    h2_best_relab = h2_coords_raw[best_aut_perm]
    max_subset, max_pose, max_err = maximum_realizable_subset(
        h1_coords, h2_best_relab, BRIDGES, reflect=best_aut["reflect"],
        n_starts=300, tol=1e-7, seed=seed + 9999
    )
    print(f"  largest realizable subset: |B'| = {len(max_subset)} of {len(BRIDGES)}")
    print(f"  max |d - 1| = {max_err:.6e}")
    print(f"  realized bridges = {max_subset}")
    obstructions = sorted(set(BRIDGES) - set(max_subset))
    print(f"  obstructing bridges = {obstructions}")

    # ----- Output JSON -----
    output = {
        "experiment": "e1x_realize_moser14",
        "bridges": [list(b) for b in BRIDGES],
        "n_bridges": len(BRIDGES),
        "moser_automorphisms": [list(p) for p in auts],
        "h1_coords_numeric": h1_coords.tolist(),
        "structural_obstructions": obstruction_rows,
        "has_structural_obstruction": has_obstruction,
        "phase1_identity_no_reflect": {
            "best_loss": loss_id,
            "best_max_err": max_err_id,
            "best_pose": pose_id.tolist(),
        },
        "phase2_identity_reflect": {
            "best_loss": loss_ref,
            "best_max_err": max_err_ref,
            "best_pose": pose_ref.tolist(),
        },
        "phase3_all_automorphisms": aut_results,
        "best_overall": {
            "aut": best_aut["aut"],
            "reflect": best_aut["reflect"],
            "loss": best_aut["loss"],
            "max_err": best_aut["max_err"],
            "pose": best_aut["pose"],
            "bridge_distances": bridge_rows,
        },
        "max_realizable_subset": {
            "size": len(max_subset),
            "bridges": [list(b) for b in max_subset],
            "obstructions": [list(b) for b in obstructions],
            "max_err_at_subset": max_err,
            "pose": max_pose.tolist() if max_pose is not None else None,
        },
    }
    out_path = CACHE / "e1x_realize_moser14.json"
    with out_path.open("w") as f:
        json.dump(output, f, indent=2)
    print()
    print(f"archived: {out_path}")

    # ----- Verdict -----
    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    eps = 1e-6
    realizable = best_aut["max_err"] < eps
    print(f"  Realizable as UDG? {'YES' if realizable else 'NO'}")
    if has_obstruction:
        print(f"  Structural cocircularity obstruction: PRESENT")
        for r in obstruction_rows:
            print(f"    -- {r['side']} v_{r['vertex']} via {r['bridge_endpoints']}")
    else:
        print(f"  Structural cocircularity obstruction: ABSENT")
    print(f"  Best numerical max per-bridge |d - 1| (across all auts + chiralities)"
          f" = {best_aut['max_err']:.6e}")
    print(f"  Threshold for realizability: {eps:.0e}")
    if not realizable:
        print(f"  Maximum realizable subset size = {len(max_subset)} / 14")
        print(f"  => the 14-vertex Moser x Moser no-K_4 chi=5 abstract graph is NOT UDG-realizable.")
        print(f"     Max simultaneous unit-distance bridges: |B'| = {len(max_subset)}, with")
        print(f"     {len(obstructions)} obstructions.")


if __name__ == "__main__":
    raise SystemExit(main())
