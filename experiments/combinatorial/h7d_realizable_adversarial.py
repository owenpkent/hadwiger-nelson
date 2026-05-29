r"""h7d: Can an ADVERSARIAL SUBSET of REALIZABLE bridges force chi >= 6?

The decisive test of the coordinate-first thrust. h7 showed the FULL realizable
bridge set (every genuine unit-distance cross-pair) of P_510 vs rotated/
translated P_510 is 5-colorable in all configs, even at 4378 bridges. h7d asks
the sharper question: the abstract chi-6 construction (L27, |B|=2700) forces
UNSAT by ADVERSARIALLY choosing which bridges to add. What if we run that same
adversarial selection, but restrict the candidate pool to ONLY the realizable
unit-distance cross-pairs?

If an adversarial subset of realizable bridges forces chi >= 6: a REALIZABLE
chi-6 UDG = the prize (every chosen bridge is a genuine unit distance, both
halves are real plane embeddings, so the union is a real UDG).

If no adversarial subset of the realizable pool can force chi >= 6 (the likely
outcome): this is the sharp structural finding. It proves realizability and
chi-6-forcing are in TENSION not just at the full-bridge level but at the
level of EVERY achievable bridge subset. It would explain definitively WHY
the abstract |B|~2000 construction is non-realizable: the abstract construction
NEEDS bridges that are not unit distances in any embedding.

Mechanism: greedy adversarial augmentation restricted to the realizable pool R.
  - Sample proper 5-colorings c1 of H1.
  - Maintain bridge set B subset of R. For each c1, B induces lists on H2.
  - Greedily add the realizable bridge from R that most increases saturation
    across the c1 sample.
  - When the sample is saturated, full-SAT the union; if SAT, extract an
    adversary c1 and continue; if UNSAT, chi >= 6 with realizable bridges.
  - If R is exhausted (all of R added) and the union is still SAT, the
    realizable pool is PROVABLY insufficient for chi-6 (definitive negative).

Discipline: exact (bridges already exact-verified in h7), persist, dual-solver,
budget.
"""

from __future__ import annotations

import json
import pathlib
import random
import time

from pysat.solvers import Cadical195, Glucose4

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"
EDGE = REPO_ROOT / "sources" / "cnp-sat" / "edge"


def parse_edges(path):
    out = []
    for line in path.read_text().strip().splitlines():
        if line.startswith("e "):
            _, a, b = line.split()
            out.append((int(a) - 1, int(b) - 1))
    return out


def sat_color(N, edges, k, solver_cls, budget=None, want_model=False):
    var = lambda v, c: v * k + c + 1
    clauses = []
    for v in range(N):
        clauses.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        for c in range(k):
            clauses.append([-var(u, c), -var(v, c)])
    t0 = time.time()
    with solver_cls(bootstrap_with=clauses) as s:
        if budget:
            s.conf_budget(budget)
            res = s.solve_limited()
        else:
            res = s.solve()
        model = s.get_model() if (res and want_model) else None
    coloring = None
    if model and want_model:
        pos = set(x for x in model if x > 0)
        coloring = [None] * N
        for v in range(N):
            for c in range(k):
                if var(v, c) in pos:
                    coloring[v] = c
                    break
    return res, coloring, time.time() - t0


def sample_colorings(n, eb, count, seed):
    """Sample distinct proper 5-colorings of H1 (P_510) via randomized SAT."""
    rng = random.Random(seed)
    cols = []
    seen = set()
    for attempt in range(count * 4):
        if len(cols) >= count:
            break
        # randomize by adding a random unit-clause seed assignment then solving
        var = lambda v, c: v * 5 + c + 1
        clauses = []
        for v in range(n):
            clauses.append([var(v, c) for c in range(5)])
            for c1 in range(5):
                for c2 in range(c1 + 1, 5):
                    clauses.append([-var(v, c1), -var(v, c2)])
        for (u, v) in eb:
            for c in range(5):
                clauses.append([-var(u, c), -var(v, c)])
        with Cadical195(bootstrap_with=clauses) as s:
            # random phase via random assumptions on a few vertices
            assumptions = []
            for v in rng.sample(range(n), 8):
                assumptions.append(var(v, rng.randrange(5)))
            res = s.solve(assumptions=assumptions)
            if not res:
                continue
            m = s.get_model()
        col = tuple(next(c for c in range(5) if m[v * 5 + c] > 0) for v in range(n))
        if col not in seen:
            seen.add(col)
            cols.append(col)
    return cols


def main():
    print("h7d: adversarial subset of REALIZABLE bridges -> chi >= 6?")
    print("=" * 70)

    eb = parse_edges(EDGE / "510.edge")
    n = 510

    # Load the realizable bridge pools from h7. Use the densest configs.
    pools = {}
    for tag in ["rot60_t0", "rot60_t1", "trans_1_Integer", "rotMoser_t0"]:
        # filenames were sanitized; match by glob
        for p in CACHE.glob(f"h7_{tag}*_graph.json"):
            d = json.load(open(p))
            pools[tag] = d["bridges"]
            break
    for tag, br in pools.items():
        print(f"  pool {tag}: {len(br)} realizable bridges")

    # Sample colorings of P_510 once (shared).
    print("\nsampling 40 proper 5-colorings of P_510 ...")
    t0 = time.time()
    colorings = sample_colorings(n, eb, 40, seed=20260529)
    print(f"  got {len(colorings)} distinct colorings ({time.time()-t0:.1f}s)")

    internal = list(eb) + [(u + n, v + n) for (u, v) in eb]

    results = []
    for tag, pool in pools.items():
        print(f"\n--- adversarial greedy on realizable pool {tag} ({len(pool)} bridges) ---")
        # Adversarial selection: score each candidate realizable bridge (u,v) by
        # how many sampled colorings it "constrains" the target v in. The score
        # for bridge (u, v) under coloring c1 is: it forbids color c1[u] at v.
        # A target v is "saturated" under c1 if its forbidden-color set = all 5.
        # We greedily add bridges to maximize total saturations across the sample.
        B = []
        pool_remaining = [tuple(p) for p in pool]
        round_no = 0
        sample = list(colorings)
        verdict = None
        max_rounds = 12
        while round_no < max_rounds:
            round_no += 1
            # forbidden[ (v) ] under each c1 in sample
            # build current forbidden sets
            def forbidden_sets(Bcur):
                # for each sampled c1, dict v -> set of forbidden colors at v
                fs = []
                for c1 in sample:
                    fmap = {}
                    for (u, v) in Bcur:
                        fmap.setdefault(v, set()).add(c1[u])
                    fs.append(fmap)
                return fs
            # greedily add bridges from pool until every sampled c1 has some v with |forbidden|=5
            added_this_round = 0
            while pool_remaining:
                fs = forbidden_sets(B)
                # is every c1 saturated (some v fully forbidden)?
                unsat_c1 = [k for k, fmap in enumerate(fs)
                            if not any(len(s) >= 5 for s in fmap.values())]
                if not unsat_c1:
                    break
                # score candidates by marginal saturation gain on unsat_c1
                best, best_gain = None, -1
                for (u, v) in pool_remaining[:4000]:  # cap scan for speed
                    gain = 0
                    for k in unsat_c1:
                        cur = fs[k].get(v, set())
                        if c_needed := (sample[k][u] not in cur):
                            # marginal: brings v closer to saturation
                            if len(cur) == 4:
                                gain += 3   # would saturate v
                            else:
                                gain += 1
                    if gain > best_gain:
                        best_gain, best = gain, (u, v)
                if best is None or best_gain <= 0:
                    break
                B.append(best)
                pool_remaining.remove(best)
                added_this_round += 1
                if added_this_round > 3000:
                    break
            # full SAT on union with current B
            edges = internal + [(u, v + n) for (u, v) in B]
            res, _, tt = sat_color(2 * n, edges, 5, Cadical195, budget=2_000_000)
            print(f"  round {round_no}: |B|={len(B)}, pool_left={len(pool_remaining)}, SAT={res} ({tt:.1f}s)")
            if res is False:
                # chi >= 6 candidate! dual-confirm
                resb, _, _ = sat_color(2 * n, edges, 5, Glucose4, budget=20_000_000)
                verdict = f"UNSAT cadical chi>=6 CANDIDATE at |B|={len(B)}; glucose={'UNSAT' if resb is False else resb}"
                print(f"  *** {verdict} ***")
                gpath = CACHE / f"h7d_{tag}_chi6candidate.json"
                json.dump({"tag": tag, "B": B, "N": 2 * n}, open(gpath, "w"))
                break
            elif res is None:
                verdict = f"SAT-intractable in budget at |B|={len(B)}"
                print(f"  {verdict}")
                break
            else:
                # SAT: extract adversary c1 and add to sample
                res2, col2, _ = sat_color(2 * n, edges, 5, Cadical195, budget=2_000_000, want_model=True)
                if col2:
                    adv = tuple(col2[:n])
                    if adv not in sample:
                        sample.append(adv)
                if not pool_remaining:
                    verdict = f"POOL EXHAUSTED: all {len(B)} realizable bridges added, union still 5-colorable -> realizable pool INSUFFICIENT for chi-6"
                    print(f"  {verdict}")
                    break
        if verdict is None:
            verdict = f"max rounds reached; |B|={len(B)}, still 5-colorable"
        results.append({"tag": tag, "pool_size": len(pool), "final_B": len(B),
                        "rounds": round_no, "verdict": verdict})

    out = CACHE / "h7d_realizable_adversarial.json"
    json.dump({"experiment": "h7d_realizable_adversarial", "results": results}, open(out, "w"), indent=2)
    print(f"\narchived: {out}")
    print("\nSUMMARY")
    for r in results:
        print(f"  {r['tag']:<18} pool={r['pool_size']:>5} finalB={r['final_B']:>5}  {r['verdict']}")


if __name__ == "__main__":
    raise SystemExit(main())
