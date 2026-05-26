r"""e3f: Shot 1 of SOLVING_PROGRAM. Integer chi_m(R^2) >= 5 via LP, using the
Polymath16 510-vertex 5-chromatic UDG as the LP constraint.

Architecture 3 / continuous side. Sits on top of e3e (Moser spindle gave 0.262).

Motivation. The OFV-style LP constraint sum_i f(||v_i||) <= alpha(G) for a
finite UDG G in R^2 drives the LP optimum toward m_1 <= alpha(G)/N(G), where
N is |V(G)| and alpha is the independence number. For a unit-edge triangle
(K_3), alpha/N = 1/3 ~ 0.333. For the Moser spindle (chi=4), alpha/N = 2/7
~ 0.286. For a 5-chromatic UDG (chi=5), alpha/N <= 1/5 = 0.200, which would
push m_1 to ~0.2, giving integer chi_m >= 5 via the bridge inequality
chi_m * m_1 >= 1.

The Polymath16 510-vertex graph (Parts 2019; e1b SAT-verified as
4-uncolorable) is the smallest 5-chromatic UDG in our local sources with
explicit Mathematica-style coordinates in Q(sqrt(3), sqrt(11)).

Method:
1. Parse 510 vertex coordinates from sources/cnp-sat/vtx/510.vtx.
2. Load edge list from sources/cnp-sat/edge/510.edge.
3. Compute alpha(G) via SAT (binary search with cardinality constraint).
4. Sweep over translations of the configuration in R^2.
5. For each translation t, the constraint is sum_{i=1}^{510} f(||v_i + t||) <= alpha,
   contributing 510*z_c to the t=0 LP constraint and alpha*z_c to the objective.
6. Solve LP combining 510-UDG constraints with OFV's 3 triangles.
7. Report m_1 bound. Target: m_1 < 0.2.

The expected ratio alpha/N for the Polymath16 510 graph:
- chi(G) = 5 (verified).
- Fractional chromatic chi_f(G) >= chi(G) = 5 (no, chi_f <= chi); actually
  chi_f(G) <= chi(G) = 5, so by chi_f * alpha >= N: alpha >= N/chi_f >= N/5 = 102.
- Upper bound on alpha: chi(G) >= N/alpha gives alpha >= N/chi >= 102 only
  if chi_f = chi. Tight alpha is in [102, ???]. Likely alpha is close to 102
  (Polymath16 graphs were minimized to be "tight" 5-chromatic).

Once we have the exact alpha, the LP bound prediction is:
- Best case (alpha = 102): m_1 <= 102/510 = 0.2 exactly. Integer chi_m >= 5.
- If alpha = 105 or 110: m_1 ~ 0.206 or 0.215. Real chi_m >= 4.65 or 4.85.
  Integer chi_m still >= 5 if m_1 < 0.2.

A miss would still be informative: the LP framework has finite slack from
the alpha/N ratio, and tight bounds require alpha as close to N/chi as
possible.
"""

from __future__ import annotations

import json
import math
import pathlib
import re
import time

import cvxpy as cp
import numpy as np
import sympy as sp

from experiments.fractional.e3c_ofv_lp_dual import (
    omega_n, chi_m_integer, CACHE, OFV_N2_TRIPLES_SQUARED,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCES = REPO_ROOT / "sources" / "cnp-sat"
VTX_PATH = SOURCES / "vtx" / "510.vtx"
EDGE_PATH = SOURCES / "edge" / "510.edge"


def parse_mathematica_coord(s: str) -> float:
    """Convert a Mathematica scalar string like '(3 - Sqrt[33])/6' to a Python float.

    Supports unnested Sqrt[X] with X a rational or integer expression. Uses sympy
    to evaluate the resulting expression symbolically, then converts to float.
    """
    s = s.strip()
    # Replace Sqrt[X] with sqrt(X).
    s_py = re.sub(r"Sqrt\[([^\]]+)\]", r"sqrt(\1)", s)
    return float(sp.sympify(s_py))


def load_polymath510_vertices() -> np.ndarray:
    """Load all 510 vertices from sources/cnp-sat/vtx/510.vtx as a (510, 2) float array."""
    verts = []
    with VTX_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            assert line.startswith("{") and line.endswith("}"), f"Unexpected vertex format: {line!r}"
            body = line[1:-1]
            # The two coordinates are separated by a comma, but commas can appear
            # inside Sqrt[a, b] type forms. The Polymath 510 file doesn't have those,
            # but we still split carefully by tracking bracket depth.
            depth = 0
            split_at = None
            for i, ch in enumerate(body):
                if ch in "[(":
                    depth += 1
                elif ch in "])":
                    depth -= 1
                elif ch == "," and depth == 0:
                    split_at = i
                    break
            assert split_at is not None, f"No top-level comma in: {line!r}"
            x_str, y_str = body[:split_at], body[split_at+1:]
            verts.append([parse_mathematica_coord(x_str), parse_mathematica_coord(y_str)])
    V = np.array(verts)
    assert V.shape == (510, 2), f"Expected 510 vertices, got {V.shape}"
    return V


def load_polymath510_edges() -> list[tuple[int, int]]:
    """Load edges from sources/cnp-sat/edge/510.edge in DIMACS format.

    Returns list of (i, j) with i < j, 0-indexed.
    """
    edges = []
    n_expected = None
    e_expected = None
    with EDGE_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                parts = line.split()
                assert parts[0] == "p" and parts[1] == "edge"
                n_expected = int(parts[2])
                e_expected = int(parts[3])
            elif line.startswith("e"):
                parts = line.split()
                i, j = int(parts[1]) - 1, int(parts[2]) - 1
                if i > j:
                    i, j = j, i
                edges.append((i, j))
    assert n_expected == 510, f"Expected 510 vertices in edge file header, got {n_expected}"
    if e_expected is not None:
        assert len(edges) == e_expected, f"Expected {e_expected} edges, got {len(edges)}"
    return edges


def verify_unit_distance_edges(V: np.ndarray, edges: list[tuple[int, int]], tol: float = 1e-6) -> int:
    """Sanity check: count how many declared edges actually have Euclidean distance 1 (float tolerance)."""
    good = 0
    for (i, j) in edges:
        d = float(np.linalg.norm(V[i] - V[j]))
        if abs(d - 1.0) < tol:
            good += 1
    return good


def alpha_via_sat(N: int, edges: list[tuple[int, int]], target: int, cache_path: pathlib.Path | None = None) -> tuple[bool, list[int] | None, float]:
    """Check if alpha(G) >= target via SAT, return (is_sat, independent_set, time).

    Encoding: variables x_1, ..., x_N (vertex is in independent set or not).
    Constraints: x_i + x_j <= 1 for each edge (i, j).
    Cardinality: sum x_i >= target (sequential counter encoding via python-sat).
    """
    from pysat.formula import CNF
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Cadical195

    # Variables 1..N are x_1..x_N. Cardinality encoding adds auxiliary variables.
    top_var = N

    cnf = CNF()
    for (i, j) in edges:
        cnf.append([-(i + 1), -(j + 1)])    # at most one of x_i, x_j

    # sum x_i >= target: equivalent to NOT(sum x_i <= target - 1).
    # CardEnc.atleast handles this directly via sequential counter encoding.
    card = CardEnc.atleast(lits=list(range(1, N + 1)), bound=target, top_id=top_var, encoding=EncType.seqcounter)
    cnf.extend(card.clauses)

    t0 = time.time()
    with Cadical195(bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    elapsed = time.time() - t0

    indep_set = None
    if sat and model is not None:
        indep_set = [i for i in range(N) if (i + 1) in model[:N]]
    return sat, indep_set, elapsed


def compute_alpha(N: int, edges: list[tuple[int, int]], lo: int, hi: int, cache_path: pathlib.Path) -> dict:
    """Compute alpha(G) via binary search SAT.

    Returns dict with 'alpha', 'witness' (max independent set), and timing info.
    """
    if cache_path.exists():
        with cache_path.open() as f:
            cached = json.load(f)
        print(f"  loaded cached alpha = {cached['alpha']} (witness size {len(cached['witness'])})")
        return cached

    print(f"  binary search alpha in [{lo}, {hi}]:")
    best_witness = None
    best_alpha = None
    # First confirm lower bound at lo.
    sat, witness, t = alpha_via_sat(N, edges, lo)
    print(f"    alpha >= {lo}: {sat} ({t:.1f}s)")
    if not sat:
        raise RuntimeError(f"alpha < {lo}, contradicts theory")
    best_alpha = lo
    best_witness = witness

    lo += 1
    while lo <= hi:
        mid = (lo + hi) // 2
        sat, witness, t = alpha_via_sat(N, edges, mid)
        print(f"    alpha >= {mid}: {sat} ({t:.1f}s)")
        if sat:
            best_alpha = mid
            best_witness = witness
            lo = mid + 1
        else:
            hi = mid - 1

    result = {
        "alpha": best_alpha,
        "witness": sorted(best_witness),
        "n_vertices": N,
        "n_edges": len(edges),
    }
    cache_path.parent.mkdir(exist_ok=True)
    with cache_path.open("w") as f:
        json.dump(result, f, indent=2)
    print(f"  alpha(G) = {best_alpha} (witness size = {len(best_witness)})")
    return result


def build_LP_with_udg(
    V: np.ndarray,
    alpha_G: int,
    translations: list[tuple[float, float]],
    ofv_triples: list[tuple[float, float, float]] = OFV_N2_TRIPLES_SQUARED,
    n: int = 2,
    t_max: float = 50.0,
    n_grid: int = 8000,
) -> dict:
    """Build the LP combining OFV triangles + sum f(||v_i + t||) <= alpha for each translation t.

    Variables: z_0 (free), z_1 (free), zc_t[k] >= 0 (triangle k), zc_u[k] >= 0 (UDG translation k).

    LP:
      min z_0 + sum_k_triangle zc_t[k] + sum_k_UDG alpha * zc_u[k]
      s.t. z_0 + z_1 + sum 3 * zc_t[k] + sum N * zc_u[k] >= 1
           z_0 + z_1 Omega_n(t) + sum_k_t zc_t[k] (Omega_n(t r_1k) + Omega_n(t r_2k) + Omega_n(t r_3k))
                                + sum_k_u zc_u[k] (sum_i Omega_n(t ||v_i + offset_k||)) >= 0   for all t > 0
    """
    N = V.shape[0]
    t_grid = np.linspace(t_max / n_grid, t_max, n_grid)
    omega_t = omega_n(t_grid, n)
    n_plus_1 = n + 1

    # Triangle constraints (OFV).
    K_t = len(ofv_triples)
    triple_omega = []
    for (a, b, c) in ofv_triples:
        rs = [math.sqrt(a), math.sqrt(b), math.sqrt(c)]
        triple_omega.append(sum(omega_n(t_grid * r, n) for r in rs))
    T = np.stack(triple_omega) if K_t > 0 else None

    # UDG constraints (Polymath510 translations).
    K_u = len(translations)
    udg_omega = np.zeros((K_u, n_grid))
    for k, (cx, cy) in enumerate(translations):
        # Radii ||v_i + offset|| where offset is the translation point.
        # Equivalently, place the origin at the position -offset:
        # the configuration shifted to put -offset at origin.
        # We just need the N radii.
        diffs = V - np.array([cx, cy])
        radii = np.linalg.norm(diffs, axis=1)
        # sum over i of Omega_n(t * r_i)
        s = np.zeros(n_grid)
        for r in radii:
            s += omega_n(t_grid * r, n)
        udg_omega[k] = s

    z0 = cp.Variable()
    z1 = cp.Variable()
    zc_t = cp.Variable(K_t, nonneg=True) if K_t > 0 else None
    zc_u = cp.Variable(K_u, nonneg=True) if K_u > 0 else None

    grid_expr = z0 + z1 * omega_t
    t0_expr = z0 + z1
    objective = z0
    if K_t > 0:
        grid_expr = grid_expr + zc_t @ T
        t0_expr = t0_expr + n_plus_1 * cp.sum(zc_t)
        objective = objective + cp.sum(zc_t)
    if K_u > 0:
        grid_expr = grid_expr + zc_u @ udg_omega
        t0_expr = t0_expr + N * cp.sum(zc_u)
        objective = objective + alpha_G * cp.sum(zc_u)

    constraints = [grid_expr >= 0, t0_expr >= 1]
    prob = cp.Problem(cp.Minimize(objective), constraints)
    t0 = time.time()
    prob.solve(solver=cp.HIGHS, verbose=False)
    elapsed = time.time() - t0

    out = {
        "status": prob.status,
        "z0": float(z0.value) if z0.value is not None else None,
        "z1": float(z1.value) if z1.value is not None else None,
        "m1_bound": float(prob.value) if prob.value is not None else None,
        "solve_time_s": elapsed,
        "n_vertices": N,
        "alpha_G": alpha_G,
        "ratio_alpha_over_N": alpha_G / N,
        "K_t": K_t,
        "K_u": K_u,
    }
    if K_u > 0 and zc_u.value is not None:
        active = [(translations[k], float(zc_u.value[k])) for k in range(K_u) if zc_u.value[k] > 1e-6]
        out["K_u_active"] = len(active)
        out["active_translations_sample"] = active[:5]
    return out


def main():
    print("e3f: Shot 1 - integer chi_m(R^2) >= 5 via Polymath 510 UDG in OFV LP")
    print("=" * 78)
    print()

    # --- Load graph ---
    print("Loading Polymath16 510-vertex 5-chromatic UDG:")
    V = load_polymath510_vertices()
    edges = load_polymath510_edges()
    n_good = verify_unit_distance_edges(V, edges)
    print(f"  vertices: {V.shape[0]}")
    print(f"  edges:    {len(edges)} (expected 2504); {n_good} verified as unit-distance to float tol")
    if n_good != len(edges):
        print(f"  WARN: {len(edges) - n_good} edges have unit-distance discrepancy at 1e-6 tol")

    # --- Compute alpha(G) ---
    print()
    print("Computing alpha(Polymath510) via SAT binary search:")
    # chi(G) = 5, so alpha >= N/chi = 102. Upper bound: at most N/2 = 255 (vertex bound).
    # Practically alpha is in [102, ~150]. Bracket [102, 200].
    alpha_cache = CACHE / "e3f_polymath510_alpha.json"
    alpha_info = compute_alpha(N=510, edges=edges, lo=102, hi=200, cache_path=alpha_cache)
    alpha_G = alpha_info["alpha"]
    ratio = alpha_G / 510
    print()
    print(f"  alpha(G) = {alpha_G}")
    print(f"  ratio alpha/N = {alpha_G}/510 = {ratio:.6f}")
    print(f"  predicted LP bound:  m_1 ~ {ratio:.4f}")
    print(f"  predicted chi_m:     {1/ratio:.4f}  (int: {int(np.ceil(1/ratio))})")

    # --- LP ---
    print()
    print("Building LP with OFV triangles + single Polymath510 UDG translation at origin:")
    single = build_LP_with_udg(V, alpha_G, translations=[(0.0, 0.0)])
    print(f"  alpha = {alpha_G}, N = 510, ratio = {ratio:.4f}")
    print(f"  m_1 <= {single['m1_bound']:.6f}  chi_m >= {1/single['m1_bound']:.4f}  "
          f"(int: {chi_m_integer(single['m1_bound'])})")
    print(f"  solve {single['solve_time_s']:.1f}s")

    # Sweep translations.
    print()
    print("Sweeping translations:")
    for grid_step in [0.5, 0.25, 0.1]:
        # Translations on a grid covering the configuration's footprint.
        x_min, y_min = V.min(axis=0)
        x_max, y_max = V.max(axis=0)
        pad = 0.5
        cx_vals = np.arange(x_min - pad, x_max + pad + 1e-9, grid_step)
        cy_vals = np.arange(y_min - pad, y_max + pad + 1e-9, grid_step)
        translations = [(float(cx), float(cy)) for cx in cx_vals for cy in cy_vals]
        if len(translations) > 1500:
            print(f"  grid_step={grid_step}: {len(translations)} translations, "
                  f"too many for memory budget; skipping")
            continue
        r = build_LP_with_udg(V, alpha_G, translations=translations)
        nu_active = r.get("K_u_active", 0)
        print(f"  grid_step={grid_step}: {len(translations)} translations, "
              f"m_1 <= {r['m1_bound']:.6f}, chi_m >= {1/r['m1_bound']:.4f} "
              f"(int: {chi_m_integer(r['m1_bound'])}), {nu_active} active, "
              f"{r['solve_time_s']:.1f}s")

    print()
    print("=" * 78)
    print("Summary:")
    print("=" * 78)
    print(f"  alpha(Polymath510) = {alpha_G}, ratio = {alpha_G}/510 = {ratio:.4f}")
    print(f"  e3e Moser-spindle baseline:    m_1 <= 0.2619")
    print(f"  e3f Polymath 510 (single):     m_1 <= {single['m1_bound']:.4f}")
    print(f"  Target for integer chi_m >= 5: m_1 < 0.2000")

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e3f_polymath510_lp.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e3f_polymath510_lp",
                "alpha": alpha_G,
                "ratio_alpha_over_N": ratio,
                "single_translation_result": single,
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
