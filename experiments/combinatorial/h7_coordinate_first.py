r"""h7: Coordinate-first realizable chi-6 coupling (Shot 2, novel thrust).

ORCHESTRATOR session 2026-05-29. Directly responsive to the cocircularity
barrier (L23/L27/L28/L29): every ABSTRACT chi-6 coupling fails UDG-realizability
because its bridge edges are not genuine unit distances in any plane embedding.

The reframe. Instead of building an abstract coupling and failing to embed it,
build the coupling COORDINATE-FIRST so realizability holds by construction:

  1. Load the EXACT plane coordinates of a chi-5 UDG (Polymath/Parts 510,
     sources/cnp-sat/vtx/510.vtx, coordinates in Q(sqrt 3, sqrt 11)).
  2. Create a second copy: a rotated and/or translated image of P_510 in an
     enlarged algebraic field K. The rotation/translation is chosen so that
     it maps K^2 -> K^2 (exact arithmetic preserved).
  3. The ONLY allowed bridges are GENUINE unit-distance pairs (u, v) with
     u in copy 1, v in copy 2 and exact distance^2 = 1 in K.
  4. SAT-check whether copy1 + copy2 + (all genuine unit-distance bridges)
     forces chi >= 6.

If a realizable union forces chi >= 6: a verified chi-6 UDG = the prize.

If the realizable bridge set is too SPARSE to force chi >= 6 (the likely
outcome), that is itself a sharp structural finding: it explains WHY the
abstract |B| ~ 2000 construction is non-realizable. Realizability (which caps
the bridge count at the number of true unit-distance cross-pairs) and
chi-6-forcing (which the abstract work shows needs hundreds-to-thousands of
bridges) are in direct tension.

Discipline (non-negotiable, per ORCHESTRATOR spec):
- EXACT arithmetic for every coordinate and distance (sympy over K).
- Every bridge is verified distance^2 == 1 exactly before use.
- chi >= 6 claim requires dual-solver UNSAT + omega <= 3 + the union being
  realizable BY CONSTRUCTION (each copy is a real UDG; bridges are real unit
  distances; so the whole union is a real UDG with no cocircularity issue).
- SAT budget discipline: persist the graph BEFORE any expensive SAT.
- Wrong-approach detectors run on the mechanism.

Translations/rotations that keep Q(sqrt 3, sqrt 11) closed:
- Pure translation by t in (Q(sqrt 3, sqrt 11))^2: trivially closed.
- Rotation by a Moser-type angle (cos = 5/6, sin = sqrt(11)/6): closed in
  Q(sqrt 3, sqrt 11) since both copy coords already contain sqrt 11.
- Rotation by 60 degrees (cos = 1/2, sin = sqrt 3 / 2): closed.
To genuinely ENLARGE the field we also try a rotation introducing sqrt 5 or
sqrt 7 (de Grey's full field Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11)).
"""

from __future__ import annotations

import json
import pathlib
import time

import sympy as sp
from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
VTX = REPO_ROOT / "sources" / "cnp-sat" / "vtx"
EDGE = REPO_ROOT / "sources" / "cnp-sat" / "edge"


def parse_vtx(path: pathlib.Path):
    """Parse a Mathematica-format .vtx file to exact sympy coordinate pairs."""
    out = []
    for line in path.read_text().strip().splitlines():
        line = line.strip().strip("{}")
        a, b = [p.strip() for p in line.split(",")]
        def cv(s):
            return sp.sympify(s.replace("Sqrt[", "sqrt(").replace("]", ")"))
        out.append((cv(a), cv(b)))
    return out


def parse_edges(path: pathlib.Path):
    out = []
    for line in path.read_text().strip().splitlines():
        if line.startswith("e "):
            _, a, b = line.split()
            out.append((int(a) - 1, int(b) - 1))  # to 0-indexed
    return out


def rot_apply(p, cos_t, sin_t):
    return (cos_t * p[0] - sin_t * p[1], sin_t * p[0] + cos_t * p[1])


def translate(p, t):
    return (p[0] + t[0], p[1] + t[1])


def build_copy(base, cos_t, sin_t, t):
    """Return rotated-then-translated exact copy of base coordinate list."""
    return [translate(rot_apply(p, cos_t, sin_t), t) for p in base]


def cross_unit_bridges(copy1, copy2):
    """Find all (i, j) with copy1[i], copy2[j] at exact distance^2 == 1.

    This is O(N^2) exact-distance checks. With N = 510 that is 260k sympy
    simplifies; we use a numeric prefilter then confirm exactly.
    """
    import mpmath as mp
    mp.mp.dps = 40

    def num(p):
        return (complex(sp.N(p[0], 40)).real, complex(sp.N(p[1], 40)).real)

    n1 = [num(p) for p in copy1]
    n2 = [num(p) for p in copy2]
    candidates = []
    for i, (x1, y1) in enumerate(n1):
        for j, (x2, y2) in enumerate(n2):
            d2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
            if abs(d2 - 1.0) < 1e-9:
                candidates.append((i, j))
    # exact confirm
    confirmed = []
    for (i, j) in candidates:
        dx = copy1[i][0] - copy2[j][0]
        dy = copy1[i][1] - copy2[j][1]
        d2 = sp.simplify(dx * dx + dy * dy)
        if d2 == 1:
            confirmed.append((i, j))
    return confirmed, len(candidates)


def has_k4(n, edge_set):
    """Exhaustive K_4 check via adjacency. Returns True if any K_4 exists."""
    adj = [set() for _ in range(n)]
    for (u, v) in edge_set:
        adj[u].add(v)
        adj[v].add(u)
    for a in range(n):
        Na = adj[a]
        for b in Na:
            if b <= a:
                continue
            common_ab = Na & adj[b]
            for c in common_ab:
                if c <= b:
                    continue
                if adj[c] & common_ab:
                    # any d > c adjacent to a,b,c
                    for d in (adj[c] & common_ab):
                        if d > c:
                            return True
    return False


def sat_kcolor(n, edges, k, solver_cls, budget_conflicts=None):
    def var(v, c):
        return v * k + c + 1
    clauses = []
    for v in range(n):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    t0 = time.time()
    with solver_cls(bootstrap_with=clauses) as s:
        if budget_conflicts is not None:
            s.conf_budget(budget_conflicts)
            res = s.solve_limited()
        else:
            res = s.solve()
    return res, time.time() - t0


def run_one(base, edges_base, cos_t, sin_t, t, tag, do_sat=True):
    n = len(base)
    copy1 = base
    copy2 = build_copy(base, cos_t, sin_t, t)

    bridges, n_numcand = cross_unit_bridges(copy1, copy2)

    # combined graph: copy1 [0..n), copy2 [n..2n)
    edges = list(edges_base) + [(u + n, v + n) for (u, v) in edges_base]
    edges += [(u, v + n) for (u, v) in bridges]
    N = 2 * n

    distinct_sources = len({u for (u, v) in bridges})
    distinct_targets = len({v for (u, v) in bridges})

    result = {
        "tag": tag,
        "N": N,
        "n_bridges": len(bridges),
        "numeric_candidates": n_numcand,
        "distinct_bridge_sources": distinct_sources,
        "distinct_bridge_targets": distinct_targets,
        "n_edges_total": len(edges),
    }

    # persist graph BEFORE SAT (sanitize tag for filesystem)
    safe_tag = "".join(c if c.isalnum() or c in "_-" else "_" for c in tag)
    CACHE.mkdir(parents=True, exist_ok=True)
    gpath = CACHE / f"h7_{safe_tag}_graph.json"
    with gpath.open("w") as f:
        json.dump({"tag": tag, "N": N, "n": n, "bridges": bridges,
                   "n_edges": len(edges)}, f)
    result["graph_path"] = str(gpath)

    if not do_sat or len(bridges) == 0:
        result["chi_verdict"] = "no bridges; chi = 5 (union of two disjoint chi-5 copies)" if len(bridges) == 0 else "SAT skipped"
        return result, edges, N

    omega_has_k4 = has_k4(N, set((min(a, b), max(a, b)) for (a, b) in edges))
    result["has_K4"] = omega_has_k4

    # SAT 5-colorability with a conflict budget (tractability discipline)
    res5, t5 = sat_kcolor(N, edges, 5, Cadical195, budget_conflicts=2_000_000)
    if res5 is True:
        result["chi_verdict"] = "5-colorable (chi <= 5); realizable bridges do NOT force chi-6"
        result["sat5_cadical"] = "SAT"
        result["sat5_time"] = t5
    elif res5 is False:
        # UNSAT -> chi >= 6 candidate! confirm with second solver.
        res5b, t5b = sat_kcolor(N, edges, 5, Glucose4, budget_conflicts=20_000_000)
        result["chi_verdict"] = "UNSAT cadical (chi >= 6 CANDIDATE)"
        result["sat5_cadical"] = "UNSAT"
        result["sat5_glucose"] = "UNSAT" if res5b is False else ("SAT" if res5b is True else "BUDGET")
        result["sat5_time"] = t5
    else:
        result["chi_verdict"] = "SAT-intractable in budget (2M conflicts)"
        result["sat5_cadical"] = "BUDGET"
        result["sat5_time"] = t5
    return result, edges, N


def main():
    print("h7: coordinate-first realizable chi-6 coupling")
    print("=" * 70)

    base = parse_vtx(VTX / "510.vtx")
    edges_base = parse_edges(EDGE / "510.edge")
    n = len(base)
    print(f"P_510 loaded: {n} vertices, {len(edges_base)} edges (exact Q(sqrt3,sqrt11))")

    sqrt3 = sp.sqrt(3)
    sqrt11 = sp.sqrt(11)
    sqrt5 = sp.sqrt(5)
    sqrt7 = sp.sqrt(7)

    # A battery of rotation/translation pairs. Each keeps the union a genuine UDG.
    configs = []

    # 1. Pure translations by small lattice vectors in Q(sqrt3,sqrt11).
    for t in [(sp.Integer(1), sp.Integer(0)),
              (sp.Integer(2), sp.Integer(0)),
              (sp.Rational(1, 2), sqrt3 / 2),
              (sp.Integer(1), sqrt3 / 2)]:
        configs.append((sp.Integer(1), sp.Integer(0), t, f"trans_{t[0]}_{sp.srepr(t[1])[:8]}"))

    # 2. Moser-angle rotation about origin, no translation (in-field).
    configs.append((sp.Rational(5, 6), sqrt11 / 6, (sp.Integer(0), sp.Integer(0)), "rotMoser_t0"))
    # 2b. Moser rotation + unit translation.
    configs.append((sp.Rational(5, 6), sqrt11 / 6, (sp.Integer(1), sp.Integer(0)), "rotMoser_t1"))

    # 3. 60-degree rotation (in-field), small translations.
    configs.append((sp.Rational(1, 2), sqrt3 / 2, (sp.Integer(0), sp.Integer(0)), "rot60_t0"))
    configs.append((sp.Rational(1, 2), sqrt3 / 2, (sp.Integer(1), sp.Integer(0)), "rot60_t1"))

    # 4. FIELD ENLARGEMENT: rotation introducing sqrt 7 (cos=3/4? no: use the
    #    e1d family. r^2=2 gives cos=3/4, sin=sqrt7/4 -> Q(sqrt7)). de Grey field.
    configs.append((sp.Rational(3, 4), sqrt7 / 4, (sp.Integer(0), sp.Integer(0)), "rotSqrt7_t0"))
    configs.append((sp.Rational(3, 4), sqrt7 / 4, (sp.Integer(1), sp.Integer(0)), "rotSqrt7_t1"))

    # 5. FIELD ENLARGEMENT: rotation introducing sqrt 19 via r^2 = 5
    #    (cos=9/10, sin=sqrt19/10). A genuinely new ring.
    configs.append((sp.Rational(9, 10), sp.sqrt(19) / 10, (sp.Integer(0), sp.Integer(0)), "rotSqrt19_t0"))

    all_results = []
    for (cos_t, sin_t, t, tag) in configs:
        print(f"\n--- {tag}: cos={cos_t}, sin={sin_t}, t=({t[0]},{t[1]}) ---")
        try:
            res, edges, N = run_one(base, edges_base, cos_t, sin_t, t, tag)
            print(f"  bridges (exact unit dist): {res['n_bridges']} "
                  f"(numeric candidates {res['numeric_candidates']})")
            print(f"  distinct sources/targets: {res['distinct_bridge_sources']}/{res['distinct_bridge_targets']}")
            print(f"  verdict: {res['chi_verdict']}")
            all_results.append(res)
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {str(e)[:200]}")
            all_results.append({"tag": tag, "error": f"{type(e).__name__}: {str(e)[:200]}"})

    out = CACHE / "h7_coordinate_first.json"
    with out.open("w") as f:
        json.dump({"experiment": "h7_coordinate_first", "results": all_results}, f, indent=2)
    print(f"\narchived: {out}")

    # summary
    print("\n" + "=" * 70)
    print("SUMMARY (realizable bridge counts vs chi-6 forcing)")
    print(f"{'config':<22}{'bridges':>9}{'verdict':>40}")
    for r in all_results:
        if "error" in r:
            print(f"{r['tag']:<22}{'ERR':>9}{r['error'][:40]:>40}")
        else:
            print(f"{r['tag']:<22}{r['n_bridges']:>9}  {r['chi_verdict'][:46]}")


if __name__ == "__main__":
    raise SystemExit(main())
