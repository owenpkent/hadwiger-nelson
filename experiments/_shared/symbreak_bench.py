r"""Validate and benchmark the symmetry-broken CNF export.

Part 1 (correctness): the symmetry-broken encoding must be EQUISATISFIABLE with
the naive one-hot encoding on every instance. We check verdict agreement on many
random graphs across several k, plus witness validity (a model of the
symmetry-broken CNF decodes to a proper coloring).

Part 2 (the point): head-to-head wall-clock on the structured instances that are
the program's walls -- the Mycielski tower and a lineage graph -- comparing the
same CDCL solver (Cadical195) on the naive vs the symmetry-broken encoding.
"""
from __future__ import annotations
import sys
import time
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from portfolio_sat import build_color_cnf, build_color_cnf_symbreak  # noqa: E402


def _solve(clauses, name="Cadical195", want_model=False, time_limit=None):
    from pysat.solvers import Cadical195, Glucose42, MapleChrono  # noqa: F401
    cls = {"Cadical195": Cadical195, "Glucose42": Glucose42,
           "MapleChrono": MapleChrono}[name]
    s = cls(bootstrap_with=clauses)
    try:
        t = time.perf_counter()
        if time_limit is not None:
            # conf budget as a rough wall bound; Cadical ~1e6 conf/s here
            s.conf_budget(int(time_limit * 2_000_000))
            r = s.solve_limited()
        else:
            r = s.solve()
        dt = time.perf_counter() - t
        model = s.get_model() if (r and want_model) else None
        return r, dt, model
    finally:
        s.delete()


def cycle(m):
    return m, [(j, (j + 1) % m) for j in range(m)]


def myc(n, e):
    out = list(e)
    for u, v in e:
        out += [(n + u, v), (n + v, u)]
    for j in range(n):
        out.append((n + j, 2 * n))
    return 2 * n + 1, out


def myc_tower(levels):
    n, e = cycle(5)
    for _ in range(levels):
        n, e = myc(n, e)
    return n, e


def part1_correctness(trials=400):
    print("[1] equisatisfiability: symmetry-broken vs naive one-hot")
    rng = random.Random(2027)
    disagree = 0
    bad_witness = 0
    for t in range(trials):
        n = rng.randint(4, 16)
        p = rng.uniform(0.2, 0.7)
        edges = [(u, v) for u in range(n) for v in range(u + 1, n)
                 if rng.random() < p]
        for k in (2, 3, 4, 5):
            naive, _ = build_color_cnf(n, edges, k)
            sb, var = build_color_cnf_symbreak(n, edges, k)
            rn, _, _ = _solve(naive)
            rs, _, model = _solve(sb, want_model=True)
            if bool(rn) != bool(rs):
                disagree += 1
                print(f"   DISAGREE n={n} k={k} naive={rn} sb={rs} edges={edges}")
            if rs and model:
                mset = set(x for x in model if x > 0)
                col = [next((c for c in range(k) if var(v, c) in mset), -1)
                       for v in range(n)]
                if any(col[u] == col[v] for u, v in edges) or -1 in col:
                    bad_witness += 1
                    print(f"   BAD WITNESS n={n} k={k} col={col}")
    print(f"    {trials} graphs x 4 k: {disagree} disagreements, "
          f"{bad_witness} bad witnesses")
    assert disagree == 0 and bad_witness == 0
    print("    PASS")


def part2_walls(naive_budget_s=120):
    r"""Head-to-head on the program's standing walls. The symmetry-broken solve
    runs FIRST and UNBOUNDED (it is the point); the naive baseline is run second
    with a conflict budget (~naive_budget_s seconds) so a wall instance reports
    BUDGET instead of hanging.

    Measured (Cadical195, single isolated run, this machine, 2026-06-14):
      M^3(C5) k=5 UNSAT : naive  7.0s -> symbroken 0.05s  (~146x)
      M^4(C5) k=6 UNSAT : naive  BUDGET (wall) -> symbroken 21.9s  (newly tractable)
      P510    k=4 UNSAT : naive  BUDGET (wall) -> symbroken 1.66s  (newly tractable)
      P510    k=5 SAT   : symbroken instant
    Run the laggard baselines yourself if you want fresh naive numbers; they are
    omitted from a quick run because they only confirm the wall.
    """
    print(f"\n[2] head-to-head on the walls (Cadical195; symmetry-broken first, "
          f"naive capped at ~{naive_budget_s}s)")
    instances = [
        ("M^3(C5) 47v", myc_tower(3), 5),
        ("M^4(C5) 95v", myc_tower(4), 6),
    ]
    try:
        sys.path.insert(0, str(HERE.parent / "combinatorial"))
        from f1pt_lib import parse_vtx, parse_edges, VTX as _VTX, EDGE as _EDGE
        nv = len(parse_vtx(_VTX / "510.vtx"))
        edges = [tuple(e) for e in parse_edges(_EDGE / "510.edge")]
        instances.append(("P510 510v", (nv, edges), 4))
    except Exception as ex:
        print(f"    (lineage P510 unavailable: {ex})")

    budget = naive_budget_s * 1_250_000   # Cadical ~1.25M conf/s here
    print(f"    {'instance':14s} {'k':>2s} {'symbrk':>8s} {'symbrk t':>10s} "
          f"{'naive':>8s} {'naive t':>10s}")
    for label, (n, edges), k in instances:
        sb, _ = build_color_cnf_symbreak(n, edges, k)
        rs, ts, _ = _solve(sb)                       # unbounded: the point
        vs = {True: "SAT", False: "UNSAT", None: "?"}[rs]
        naive, _ = build_color_cnf(n, edges, k)
        rn, tn, _ = _solve(naive, time_limit=naive_budget_s)
        vn = {True: "SAT", False: "UNSAT", None: "BUDGET"}[rn]
        if rn is not None and bool(rn) != bool(rs):
            vn += "!MISMATCH"
        print(f"    {label:14s} {k:>2d} {vs:>8s} {ts:>9.2f}s {vn:>8s} "
              f"{tn:>9.2f}s", flush=True)


if __name__ == "__main__":
    part1_correctness()
    part2_walls()
