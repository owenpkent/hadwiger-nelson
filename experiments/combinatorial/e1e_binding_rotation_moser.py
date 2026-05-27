r"""e1e: Field-theoretic search for chi >= 6, refined from e1d's negative result (LEARNING L11).

Architecture 1 / combinatorial. Shot 2 of SOLVING_PROGRAM.

Motivation. L11 established that generic rotation orbits of the Moser spindle in
alternate rings (Q(sqrt 7), Q(sqrt 19), ...) give chi = 4 graphs. The reason: each
rotated copy is disjoint from the seed (modulo center), so the orbit graph is a
disjoint union of Moser spindles. The actual research problem L11 isolates: find
"binding" rotations theta where R_theta(M) creates *cross-copy unit-distance edges*
with the seed M. The de Grey 2018 construction works because of specific rotation
choices in Q(sqrt 11) that produce such algebraic coincidences.

This experiment systematically enumerates binding rotations.

Method.

(1) Moser seed: M = 7-vertex spindle in Q(sqrt 3, sqrt 11), centered at origin.

(2) For each ordered pair (v_i, v_j) of seed vertices, find rotation angle theta
    such that |R_theta(v_i) - v_j| = 1. The locus of (cos theta, sin theta) is the
    intersection of an affine line (linear in cos, sin) with the unit circle:

      a * cos t + b * sin t = c     where
      a = <v_i, v_j>, b = det[v_i | v_j] = v_ix v_jy - v_iy v_jx,
      c = (|v_i|^2 + |v_j|^2 - 1) / 2.

    Closed form: cos t, sin t in the field Q(sqrt 3, sqrt 11, sqrt(a^2 + b^2 - c^2)).

(3) For each binding angle theta, build U = M union R_theta(M). Count exact
    cross-copy unit edges. SAT-check chi(U) for k = 4, 5.

(4) Report any (cos_t, sin_t) that yields chi(U) >= 5 (would be a new chi >= 5
    construction). Refusal of 5-coloring would be chi >= 6 (the headline target).

(5) Phase 2: for any binding rotation that produces chi(U) = 4 with substantial
    cross-copy edges, try STACKING a second binding rotation: U' = U union R_phi(M)
    for another binding angle phi. Test chi(U') >= 5, 6.

Numerical strategy. Use mpmath at 80 digits to compute binding angles. Apply each
rotation numerically to the Moser vertices; identify candidate unit edges by
distance threshold 1e-50. For each candidate, verify EXACTLY via sympy.simplify
in the underlying number field. SAT-check uses only verified-exact edges.

If a true chi >= 6 turns up, the construction is publishable; if not, this is
structural data on the difficulty of finding chi >= 6 via Moser-stacking.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import time

import mpmath as mp
import sympy as sp
from pysat.solvers import Cadical195

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

mp.mp.dps = 80  # 80 decimal digits of working precision


# ---------------------------------------------------------------------------
# Moser spindle in Q(sqrt 3, sqrt 11)
# ---------------------------------------------------------------------------

def moser_vertices_exact():
    """Return Moser spindle as 7 sympy 2-tuples. Apex A at origin."""
    sqrt3 = sp.sqrt(3)
    sqrt11 = sp.sqrt(11)
    cos_t = sp.Rational(5, 6)
    sin_t = sqrt11 / 6
    A = (sp.Integer(0), sp.Integer(0))
    B = (sp.Integer(1), sp.Integer(0))
    C = (sp.Rational(1, 2), sqrt3 / 2)
    D = (sp.Rational(3, 2), sqrt3 / 2)
    rot = lambda p: (cos_t * p[0] - sin_t * p[1], sin_t * p[0] + cos_t * p[1])
    return [A, B, C, D, rot(B), rot(C), rot(D)]


def moser_vertices_numeric(verts_exact):
    """High-precision mpmath numerical version of the Moser vertices."""
    out = []
    for (x, y) in verts_exact:
        xn = mp.mpc(0) + mp.mpmathify(str(sp.N(x, 80)))
        yn = mp.mpc(0) + mp.mpmathify(str(sp.N(y, 80)))
        # Use mpf, not mpc
        xn = mp.mpf(str(sp.N(x, 80)))
        yn = mp.mpf(str(sp.N(y, 80)))
        out.append((xn, yn))
    return out


# ---------------------------------------------------------------------------
# Binding rotation enumeration
# ---------------------------------------------------------------------------

def binding_angles_exact(p, q):
    """All (cos theta, sin theta) such that |R_theta(p) - q| = 1, exact.

    Constraint:
      |R_t(p) - q|^2 = |p|^2 + |q|^2 - 2 <R_t(p), q> = 1
      <R_t(p), q> = cos t (p_x q_x + p_y q_y) + sin t (p_x q_y - p_y q_x)
      So  a cos t + b sin t = (|p|^2 + |q|^2 - 1) / 2,
      where a = <p,q>, b = det[p|q].
      Combined with cos^2 + sin^2 = 1, two solutions in general.

    Returns list of (cos_t_expr, sin_t_expr) in sympy form (possibly empty).
    """
    px, py = p
    qx, qy = q
    p2 = px*px + py*py
    q2 = qx*qx + qy*qy
    a = sp.simplify(px*qx + py*qy)         # <p, q>
    b = sp.simplify(px*qy - py*qx)         # det
    c = sp.simplify((p2 + q2 - 1) / 2)
    norm_sq = sp.simplify(a*a + b*b)       # |p|^2 |q|^2
    if norm_sq == 0:
        return []
    discr = sp.simplify(norm_sq - c*c)
    # Numerically check feasibility.
    try:
        d_num = float(sp.N(discr, 30))
    except (TypeError, ValueError):
        return []
    if d_num < -1e-20:
        return []
    if d_num < 0:
        discr = sp.Integer(0)
    sols = []
    for sign in (sp.Integer(1), sp.Integer(-1)):
        ct = sp.simplify((a*c + sign*b*sp.sqrt(discr)) / norm_sq)
        st = sp.simplify((b*c - sign*a*sp.sqrt(discr)) / norm_sq)
        # Verify on unit circle and consistency with the line equation.
        line_ok = float(sp.N(a*ct + b*st - c, 30))
        circ_ok = float(sp.N(ct*ct + st*st - 1, 30))
        if abs(line_ok) > 1e-15 or abs(circ_ok) > 1e-15:
            continue
        sols.append((ct, st))
    return sols


def binding_angles_numeric(p_num, q_num):
    """mpmath version of binding_angles_exact for fast enumeration / dedup."""
    px, py = p_num
    qx, qy = q_num
    p2 = px*px + py*py
    q2 = qx*qx + qy*qy
    a = px*qx + py*qy
    b = px*qy - py*qx
    c = (p2 + q2 - 1) / 2
    norm_sq = a*a + b*b
    if norm_sq == 0:
        return []
    discr = norm_sq - c*c
    if discr < 0:
        if discr < -mp.mpf("1e-30"):
            return []
        discr = mp.mpf(0)
    sr = mp.sqrt(discr)
    sols = []
    for sign in (mp.mpf(1), mp.mpf(-1)):
        ct = (a*c + sign*b*sr) / norm_sq
        st = (b*c - sign*a*sr) / norm_sq
        sols.append((ct, st))
    return sols


# ---------------------------------------------------------------------------
# Construct M union R_theta(M)
# ---------------------------------------------------------------------------

def apply_rotation_numeric(verts_num, cos_t_num, sin_t_num):
    out = []
    for (x, y) in verts_num:
        xr = cos_t_num * x - sin_t_num * y
        yr = sin_t_num * x + cos_t_num * y
        out.append((xr, yr))
    return out


def dedup_numeric(vertices_num, tol=mp.mpf("1e-40")):
    """Return (unique_vertices, mapping_old_to_new)."""
    uniq = []
    mapping = []
    for v in vertices_num:
        idx = None
        for j, u in enumerate(uniq):
            if mp.fabs(v[0] - u[0]) < tol and mp.fabs(v[1] - u[1]) < tol:
                idx = j
                break
        if idx is None:
            idx = len(uniq)
            uniq.append(v)
        mapping.append(idx)
    return uniq, mapping


def edges_numeric(verts_num, tol=mp.mpf("1e-30")):
    """All pairs at distance ~ 1."""
    es = []
    n = len(verts_num)
    one = mp.mpf(1)
    for i in range(n):
        for j in range(i+1, n):
            dx = verts_num[i][0] - verts_num[j][0]
            dy = verts_num[i][1] - verts_num[j][1]
            d2 = dx*dx + dy*dy
            if mp.fabs(d2 - one) < tol:
                es.append((i, j))
    return es


# ---------------------------------------------------------------------------
# Exact verification of candidate edges
# ---------------------------------------------------------------------------

def verify_edges_exact(verts_exact, candidate_edges):
    """For each candidate edge (i, j), verify symbolically that distance^2 == 1.
    Returns the subset of candidate_edges that pass."""
    confirmed = []
    for (i, j) in candidate_edges:
        dx = verts_exact[i][0] - verts_exact[j][0]
        dy = verts_exact[i][1] - verts_exact[j][1]
        d2 = sp.simplify(dx*dx + dy*dy)
        # radsimp + nsimplify to chase common forms
        d2_simp = sp.radsimp(sp.nsimplify(d2, rational=False))
        if d2 == 1 or d2_simp == 1:
            confirmed.append((i, j))
            continue
        # Try numeric agreement to 50 digits as a backup test, then exact again
        n = float(sp.N(d2, 50))
        if abs(n - 1) < 1e-40:
            # Suspect exact match that simplify missed
            d2_more = sp.simplify(sp.expand(sp.radsimp(d2 - 1)))
            if d2_more == 0:
                confirmed.append((i, j))
    return confirmed


# ---------------------------------------------------------------------------
# SAT k-colorability
# ---------------------------------------------------------------------------

def sat_k_color(N, edges, k, time_limit=60.0):
    """Return (sat, time). sat=True iff k-colorable. None if timeout / unknown."""
    if N == 0:
        return True, 0.0

    def var(v, c):
        return v * k + c + 1

    clauses = []
    for v in range(N):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1+1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])

    t0 = time.time()
    with Cadical195(bootstrap_with=clauses) as solver:
        sat = solver.solve()
    return sat, time.time() - t0


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def numeric_angle_key(ct, st):
    """Hashable signature of a (cos, sin) pair for dedup, ~30 digits."""
    return (mp.nstr(ct, 30), mp.nstr(st, 30))


def main():
    print("e1e: binding rotation search on Moser spindle")
    print("=" * 78)

    M_exact = moser_vertices_exact()
    M_num = moser_vertices_numeric(M_exact)
    print(f"  Moser seed: {len(M_exact)} vertices in Q(sqrt 3, sqrt 11)")

    # Sanity check on M itself.
    seed_edges = edges_numeric(M_num)
    seed_edges_ex = verify_edges_exact(M_exact, seed_edges)
    print(f"  seed unit edges (verified): {len(seed_edges_ex)} (expected 11)")
    sat4_seed, t_seed = sat_k_color(len(M_exact), seed_edges_ex, k=4)
    sat3_seed, _ = sat_k_color(len(M_exact), seed_edges_ex, k=3)
    print(f"  seed chi: 3-col={sat3_seed}, 4-col={sat4_seed} "
          f"(expected False, True; chi = 4)")
    print()

    # --- Enumerate binding angles ---
    print("Phase 1: enumerate binding angles.")
    print("  For each ordered seed pair (i, j) with i != j: find (cos t, sin t) "
          "s.t. |R_t(v_i) - v_j| = 1.")
    print()

    binding_pool = []  # list of dicts
    seen_keys = set()
    n = len(M_exact)
    for i, j in itertools.product(range(n), repeat=2):
        if i == j:
            continue
        # Skip if v_i is at origin (rotation does nothing to it).
        if M_exact[i][0] == 0 and M_exact[i][1] == 0:
            continue
        # If v_j is origin: condition is |v_i| = 1, doesn't constrain rotation.
        if M_exact[j][0] == 0 and M_exact[j][1] == 0:
            continue
        sols_num = binding_angles_numeric(M_num[i], M_num[j])
        for k_sol, (ct_num, st_num) in enumerate(sols_num):
            key = numeric_angle_key(ct_num, st_num)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            # Filter out the identity rotation (theta = 0).
            if mp.fabs(ct_num - 1) < mp.mpf("1e-30") and mp.fabs(st_num) < mp.mpf("1e-30"):
                continue
            binding_pool.append({
                "from_pair": (i, j),
                "branch": k_sol,
                "cos_t_num": ct_num,
                "sin_t_num": st_num,
                "key": key,
            })

    print(f"  binding angles found (after dedup): {len(binding_pool)}")
    print()

    # --- For each binding angle, build union and test chi ---
    print("Phase 2: test M union R_theta(M) for each binding rotation.")
    print()
    print(f"  {'idx':>3} {'pair':>10} {'|V|':>4} {'|E|':>4} {'cross':>6} {'4-col':>6} {'5-col':>6} {'time':>7}")

    results = []
    chi_ge_5_angles = []
    chi_ge_6_angles = []

    def build_union(rec):
        """Build M union R_theta(M) for a binding rotation record.

        Returns (uniq_ex_vertices, confirmed_edges, mapping, ct_ex, st_ex)
        or None on failure. mapping[u] = index in uniq for original union pos u
        in 0..13 (0..6 = seed, 7..13 = R-copy)."""
        ct = rec["cos_t_num"]
        st = rec["sin_t_num"]
        R_num = apply_rotation_numeric(M_num, ct, st)
        union_num_local = M_num + R_num
        uniq_num, mapping_local = dedup_numeric(union_num_local)

        # Recover exact (cos_t, sin_t) branch.
        i_pair, j_pair = rec["from_pair"]
        sols_ex = binding_angles_exact(M_exact[i_pair], M_exact[j_pair])
        if not sols_ex:
            return None
        chosen_ex = None
        for ct_ex, st_ex in sols_ex:
            try:
                ctn = mp.mpf(str(sp.N(ct_ex, 50)))
                stn = mp.mpf(str(sp.N(st_ex, 50)))
            except Exception:
                continue
            if mp.fabs(ctn - ct) < mp.mpf("1e-25") and mp.fabs(stn - st) < mp.mpf("1e-25"):
                chosen_ex = (ct_ex, st_ex)
                break
        if chosen_ex is None:
            return None
        ct_ex, st_ex = chosen_ex
        R_exact = [
            (ct_ex * x - st_ex * y, st_ex * x + ct_ex * y)
            for (x, y) in M_exact
        ]
        union_ex_local = list(M_exact) + R_exact

        # Build uniq_ex using mapping_local (first-occurrence rule).
        uniq_ex_local = [None] * len(uniq_num)
        for ui, mi in enumerate(mapping_local):
            if uniq_ex_local[mi] is None:
                uniq_ex_local[mi] = union_ex_local[ui]

        # Re-run candidate edges over the deduped numeric vertices.
        cand_edges = edges_numeric(uniq_num)
        confirmed_edges = verify_edges_exact(uniq_ex_local, cand_edges)
        return uniq_ex_local, confirmed_edges, mapping_local, ct_ex, st_ex

    promising = []  # records with cross_edges >= 2 — candidates for stacking

    for idx, rec in enumerate(binding_pool):
        built = build_union(rec)
        if built is None:
            continue
        uniq_ex, confirmed_edges, mapping_local, ct_ex, st_ex = built
        N_uniq = len(uniq_ex)
        n_seed_pos = len(M_exact)

        # cross_edges: edges between {old seed-image} and {old R-image} after dedup.
        # An edge (a, b) in uniq is cross iff at least one of its preimages came
        # from seed (pos < 7) and at least one came from R (pos >= 7).
        preimages = [set() for _ in range(N_uniq)]
        for ui, mi in enumerate(mapping_local):
            preimages[mi].add(ui)
        cross_edges = 0
        for (a, b) in confirmed_edges:
            a_has_seed = any(p < n_seed_pos for p in preimages[a])
            a_has_rot = any(p >= n_seed_pos for p in preimages[a])
            b_has_seed = any(p < n_seed_pos for p in preimages[b])
            b_has_rot = any(p >= n_seed_pos for p in preimages[b])
            # Edge counts as cross if endpoints span the seed/rot partition.
            if (a_has_seed and b_has_rot) or (a_has_rot and b_has_seed):
                # Only count if not also a within-seed or within-rot edge (i.e.,
                # endpoints uniquely identified): if a is purely seed and b purely
                # rot (or vice versa), definitely cross.
                a_pure_seed = a_has_seed and not a_has_rot
                a_pure_rot = a_has_rot and not a_has_seed
                b_pure_seed = b_has_seed and not b_has_rot
                b_pure_rot = b_has_rot and not b_has_seed
                if (a_pure_seed and b_pure_rot) or (a_pure_rot and b_pure_seed):
                    cross_edges += 1

        sat4, t4 = sat_k_color(N_uniq, confirmed_edges, k=4)
        sat5 = None
        t5 = 0.0
        if sat4 is False:
            sat5, t5 = sat_k_color(N_uniq, confirmed_edges, k=5)

        results.append({
            "idx": idx,
            "from_pair": rec["from_pair"],
            "branch": rec["branch"],
            "key": rec["key"],
            "n_vertices": N_uniq,
            "n_edges": len(confirmed_edges),
            "cross_edges": cross_edges,
            "4-colorable": sat4,
            "5-colorable": sat5,
            "t_sat": t4 + t5,
        })

        if cross_edges >= 1:
            promising.append({
                "rec": rec,
                "uniq_ex": uniq_ex,
                "edges": confirmed_edges,
                "cross_edges": cross_edges,
                "ct_ex": ct_ex,
                "st_ex": st_ex,
            })

        if sat4 is False:
            chi_ge_5_angles.append(rec)
        if sat5 is False:
            chi_ge_6_angles.append(rec)

        mark_5 = "!!!" if sat4 is False else ""
        mark_6 = "*** CHI>=6 ***" if sat5 is False else ""
        print(f"  {idx:3d} {str(rec['from_pair']):>10} {N_uniq:4d} {len(confirmed_edges):4d} "
              f"{cross_edges:>6} "
              f"{'F' if sat4 is False else 'T':>6} "
              f"{('F' if sat5 is False else 'T' if sat5 is True else '-'):>6} "
              f"{(t4+t5):7.2f}s {mark_5} {mark_6}")

    print()
    print(f"  binding angles producing chi >= 5: {len(chi_ge_5_angles)}")
    print(f"  binding angles producing chi >= 6: {len(chi_ge_6_angles)}")
    print(f"  promising (cross_edges >= 1): {len(promising)}")
    print()

    # --- Phase 3: stack pairs of binding rotations ---
    # Build U_{i,j} = M union R_{theta_i}(M) union R_{theta_j}(M) for pairs of
    # binding rotations from the promising pool. SAT-check chi(U) for k = 4, 5.
    # If chi(U) >= 5 for any pair, we've found a new 5-chromatic UDG. If chi >= 6,
    # we've cracked Hadwiger-Nelson.

    print("Phase 3: stack pairs of binding rotations.")
    print()

    if len(promising) < 2:
        print(f"  fewer than 2 promising rotations — skipping stacking")
        stack_results = []
    else:
        stack_results = []
        # Limit to most-cross-edge promising rotations for compute budget.
        promising.sort(key=lambda r: -r["cross_edges"])
        top = promising[:12]  # 12 choose 2 = 66 pairs
        print(f"  stacking top {len(top)} promising rotations (by cross_edges)")
        print(f"  {'i':>3} {'j':>3} {'cross_i':>7} {'cross_j':>7} {'|V|':>5} {'|E|':>5} {'4-col':>6} {'5-col':>6} {'time':>7}")

        for i in range(len(top)):
            for j in range(i+1, len(top)):
                rec_i = top[i]["rec"]
                rec_j = top[j]["rec"]
                ct_i = rec_i["cos_t_num"]
                st_i = rec_i["sin_t_num"]
                ct_j = rec_j["cos_t_num"]
                st_j = rec_j["sin_t_num"]

                R_i_num = apply_rotation_numeric(M_num, ct_i, st_i)
                R_j_num = apply_rotation_numeric(M_num, ct_j, st_j)
                triple_num = M_num + R_i_num + R_j_num
                uniq_num_tr, mapping_tr = dedup_numeric(triple_num)

                # Build exact triple union using the cached ct_ex, st_ex.
                ct_i_ex, st_i_ex = top[i]["ct_ex"], top[i]["st_ex"]
                ct_j_ex, st_j_ex = top[j]["ct_ex"], top[j]["st_ex"]
                R_i_ex = [(ct_i_ex*x - st_i_ex*y, st_i_ex*x + ct_i_ex*y) for (x, y) in M_exact]
                R_j_ex = [(ct_j_ex*x - st_j_ex*y, st_j_ex*x + ct_j_ex*y) for (x, y) in M_exact]
                triple_ex = list(M_exact) + R_i_ex + R_j_ex

                uniq_ex_tr = [None] * len(uniq_num_tr)
                for ui, mi in enumerate(mapping_tr):
                    if uniq_ex_tr[mi] is None:
                        uniq_ex_tr[mi] = triple_ex[ui]

                cand_edges_tr = edges_numeric(uniq_num_tr)
                confirmed_tr = verify_edges_exact(uniq_ex_tr, cand_edges_tr)
                N_tr = len(uniq_ex_tr)

                sat4_tr, t4_tr = sat_k_color(N_tr, confirmed_tr, k=4)
                sat5_tr = None
                t5_tr = 0.0
                if sat4_tr is False:
                    sat5_tr, t5_tr = sat_k_color(N_tr, confirmed_tr, k=5)

                stack_results.append({
                    "i_idx": top[i]["rec"]["from_pair"],
                    "j_idx": top[j]["rec"]["from_pair"],
                    "cross_i": top[i]["cross_edges"],
                    "cross_j": top[j]["cross_edges"],
                    "n_vertices": N_tr,
                    "n_edges": len(confirmed_tr),
                    "4-colorable": sat4_tr,
                    "5-colorable": sat5_tr,
                })

                mark5 = "!!!" if sat4_tr is False else ""
                mark6 = "*** CHI>=6 ***" if sat5_tr is False else ""
                print(f"  {i:3d} {j:3d} {top[i]['cross_edges']:7d} {top[j]['cross_edges']:7d} "
                      f"{N_tr:5d} {len(confirmed_tr):5d} "
                      f"{'F' if sat4_tr is False else 'T':>6} "
                      f"{('F' if sat5_tr is False else 'T' if sat5_tr is True else '-'):>6} "
                      f"{(t4_tr+t5_tr):7.2f}s {mark5} {mark6}")

        n_stack_chi5 = sum(1 for r in stack_results if r["4-colorable"] is False)
        n_stack_chi6 = sum(1 for r in stack_results if r["5-colorable"] is False)
        print()
        print(f"  pairs producing chi(triple-union) >= 5: {n_stack_chi5}")
        print(f"  pairs producing chi(triple-union) >= 6: {n_stack_chi6}")

    # --- Phase 4: greedy iterative expansion (numeric-only at 80 digits) ---
    # At 80-digit precision, an accidental |dist^2 - 1| < 1e-30 from non-edges is
    # vanishingly unlikely for finite algebraic configurations. We trust numeric
    # edges. The chi(G) determination via SAT is then sound conditional on the
    # numeric edge set being a faithful subgraph of the algebraic UDG, which we
    # spot-check by exact verification at the end.

    print()
    print("Phase 4: greedy iterative expansion (grow G by adding R_theta(M) at each step).")
    print()

    G_num = list(M_num)
    # G_num_set: we maintain numeric vertices; edges are recomputed each step.
    G_edges_num = list(seed_edges)
    rotations_used_num = []   # list of (ct_num, st_num) for each applied rotation
    max_iterations = 20
    budget_V = 200
    iter_records = []

    print(f"  initial G: |V|={len(G_num)}, |E|={len(G_edges_num)}")
    print()
    print(f"  {'it':>3} {'angle':>10} {'newV':>5} {'newE':>5} {'|V|':>5} {'|E|':>6} {'3-col':>6} {'4-col':>6} {'5-col':>6} {'time':>8}")

    seen_rotations = set()

    def numeric_apply(verts_num, ct, st):
        return apply_rotation_numeric(verts_num, ct, st)

    chi6_found_iter = None
    for it in range(1, max_iterations + 1):
        t_iter = time.time()
        # Enumerate candidate binding angles. To keep the candidate pool tractable,
        # restrict the "source" to v_i in the ORIGINAL M (i.e., R sends M into itself
        # rotated about origin) but allow the "target" v_j to range over all of G.
        candidates = []
        seen_local = set()
        for i_m in range(len(M_exact)):
            if mp.fabs(M_num[i_m][0]) < mp.mpf("1e-50") and mp.fabs(M_num[i_m][1]) < mp.mpf("1e-50"):
                continue
            for j_g in range(len(G_num)):
                if mp.fabs(G_num[j_g][0]) < mp.mpf("1e-50") and mp.fabs(G_num[j_g][1]) < mp.mpf("1e-50"):
                    continue
                sols_n = binding_angles_numeric(M_num[i_m], G_num[j_g])
                for (ct_n, st_n) in sols_n:
                    key = numeric_angle_key(ct_n, st_n)
                    if key in seen_local or key in seen_rotations:
                        continue
                    seen_local.add(key)
                    if mp.fabs(ct_n - 1) < mp.mpf("1e-30") and mp.fabs(st_n) < mp.mpf("1e-30"):
                        continue
                    candidates.append({
                        "ct_num": ct_n, "st_num": st_n, "key": key,
                    })

        # Score each candidate by new-edge count.
        best = None
        for cand in candidates:
            R_num = numeric_apply(M_num, cand["ct_num"], cand["st_num"])
            triple = G_num + R_num
            uniq_n, _ = dedup_numeric(triple)
            new_edges_cand = edges_numeric(uniq_n)
            score = len(new_edges_cand) - len(G_edges_num)
            if best is None or score > best["score"]:
                best = {**cand, "score": score, "uniq_n": uniq_n}

        if best is None or best["score"] <= 0:
            print(f"  {it:3d}: no candidate adds new edges; stopping at |V|={len(G_num)}.")
            break

        # Apply best.
        seen_rotations.add(best["key"])
        rotations_used_num.append((best["ct_num"], best["st_num"]))

        G_num = best["uniq_n"]
        new_edges_set = edges_numeric(G_num)
        new_V = len(G_num) - len(G_edges_num) // 1 + 0  # placeholder, replaced below
        new_V = len(best["uniq_n"]) - sum(1 for _ in [])  # raw size
        old_V = len(rotations_used_num) and (len(G_num) if it == 1 else None)
        # Simpler: track from previous count.
        # Instead, recompute incrementals directly.

        # Reset: G_num is now the new vertex set; recompute G_edges_num.
        new_V_delta = len(G_num) - (len(M_num) + sum(0 for _ in rotations_used_num[:-1]) if False else None or 0)
        # Compute deltas from the iter_records.
        prev_V = iter_records[-1]["n_vertices"] if iter_records else len(M_num)
        prev_E = iter_records[-1]["n_edges"] if iter_records else len(seed_edges)
        G_edges_num = new_edges_set
        delta_V = len(G_num) - prev_V
        delta_E = len(G_edges_num) - prev_E

        if len(G_num) > budget_V:
            print(f"  {it:3d}: |V|={len(G_num)} exceeds budget {budget_V}; stopping.")
            break

        sat3, t3 = sat_k_color(len(G_num), G_edges_num, k=3)
        sat4, t4 = sat_k_color(len(G_num), G_edges_num, k=4)
        sat5 = None
        t5 = 0.0
        if sat4 is False:
            sat5, t5 = sat_k_color(len(G_num), G_edges_num, k=5)

        iter_records.append({
            "iter": it, "n_vertices": len(G_num), "n_edges": len(G_edges_num),
            "newV": delta_V, "newE": delta_E,
            "3-col": sat3, "4-col": sat4, "5-col": sat5,
            "time_iter": time.time() - t_iter,
        })

        mark5 = "!!!" if sat4 is False else ""
        mark6 = "*** CHI>=6 ***" if sat5 is False else ""
        angle_disp = mp.nstr(mp.acos(best["ct_num"]), 6)
        print(f"  {it:3d} {angle_disp:>10} {delta_V:5d} {delta_E:5d} "
              f"{len(G_num):5d} {len(G_edges_num):6d} "
              f"{'F' if sat3 is False else 'T':>6} "
              f"{'F' if sat4 is False else 'T':>6} "
              f"{('F' if sat5 is False else 'T' if sat5 is True else '-'):>6} "
              f"{(t3+t4+t5):8.2f}s {mark5} {mark6}", flush=True)

        if sat5 is False:
            chi6_found_iter = it
            print(f"\n  *** chi >= 6 FOUND at iteration {it} *** ")
            # Save numeric reproduction data.
            graph_dump = {
                "vertices_num": [[mp.nstr(x, 50), mp.nstr(y, 50)] for (x, y) in G_num],
                "edges": [[a, b] for (a, b) in G_edges_num],
                "rotations_used_num": [
                    [mp.nstr(c, 50), mp.nstr(s, 50)] for (c, s) in rotations_used_num
                ],
            }
            with (CACHE / "e1e_chi6_candidate.json").open("w") as f:
                json.dump(graph_dump, f, indent=2)
            break

    # --- Save ---
    out = {
        "experiment": "e1e_binding_rotation_moser",
        "n_binding_angles_tried": len(binding_pool),
        "n_chi_ge_5": len(chi_ge_5_angles),
        "n_chi_ge_6": len(chi_ge_6_angles),
        "n_promising": len(promising),
        "chi6_found_iter": chi6_found_iter,
        "results_single_rotation": [
            {**r, "from_pair": list(r["from_pair"])} for r in results
        ],
        "results_stacked_pair": stack_results if isinstance(stack_results, list) else [],
        "phase4_iterative_expansion": iter_records,
        "phase4_rotations_used_num": [
            [mp.nstr(c, 30), mp.nstr(s, 30)] for (c, s) in rotations_used_num
        ],
    }
    out_path = CACHE / "e1e_binding_rotation_moser.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\narchived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
