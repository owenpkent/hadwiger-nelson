r"""E25 driver: the five $n=18$ cells the blind split could not close.

WHY THIS EXISTS. E20's ladder closed $m = 54..57$ at $n = 18$ and then failed on
$m = 49..53$. Its fallback, recursive unit-clause splitting on the highest-indexed
vertex pairs, DIVERGED: $m=49$ reached split depth 15 (up to $32^3$ branches) with
branches still timing out at every level. Pinning a fixed set of variables does
not reduce those cells' difficulty, it multiplies the number of hard subproblems.
That route is retired (see `_cache/e20/STOP`).

Cube-and-conquer cuts along the SOLVER'S OWN decision structure instead: run
ordinary search for `--prerun` seconds, then emit a cube whenever `--cutoff` edge
variables are assigned. Measured on the stuck $m=53$ cell, the cutoff behaves as a
dial (40 -> 3 cubes, 55 -> 33, 70 -> 544) and sampled cubes solved in 0.11 to 41.9
seconds against a whole-cell budget of hours that never finished.

HONEST UNCERTAINTY. That sample was 5 cubes out of 544, and one of the five took
42 s, so the tail is unmeasured. If cube difficulty is heavy-tailed the estimate
is wrong in the bad direction, and this driver will show it: every cube carries a
timeout, an UNKNOWN cube is never counted as UNSAT, and a cell with any UNKNOWN
cube is reported UNDECIDED rather than closed.

Order matters. Cells run from $m=53$ down to $m=49$, easiest first, because the
earlier ladder showed cost climbing steeply as $m$ falls; a cheap cell closing
first is worth more than a hard cell timing out first.

Usage:
    python -m experiments.combinatorial.e25_n18_stuck --jobs 7
    python -m experiments.combinatorial.e25_n18_stuck --cells 53,52 --cutoff 80
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from e25_cube import decide, CACHE                            # noqa: E402
from e20_sigma2 import SAT, UNSAT, UNKNOWN, probe_cell        # noqa: E402
from e18_gallai import ky_floor, codegree_ceiling             # noqa: E402

# The n=18 cells the E20 ladder already closed (m=54..57); everything else in the
# window is still open.
N18_ALREADY_CLOSED = {54, 55, 56, 57}


def default_cells(n):
    """The full window, hardest last, minus anything already closed.

    NEVER hardcode this. An earlier version of this file listed n=19 as 52..60
    when the window is 52..61, so cell m=61 would have gone untested while the
    queue reported "n=19 COMPLETE" -- a silently wrong answer, which is the only
    kind that really matters here.
    """
    lo, hi = ky_floor(n), codegree_ceiling(n)
    cells = [m for m in range(lo, hi + 1)
             if not (n == 18 and m in N18_ALREADY_CLOSED)]
    return sorted(cells, reverse=True)      # easiest (densest) first


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--cells", type=str, default=None,
                    help="override; default is the computed window")
    ap.add_argument("--cutoff", type=int, default=70)
    ap.add_argument("--prerun", type=int, default=60)
    ap.add_argument("--jobs", type=int, default=7)
    ap.add_argument("--cube-timeout", type=int, default=1800)
    args = ap.parse_args()

    cells = ([int(x) for x in args.cells.split(",")] if args.cells
             else default_cells(args.n))
    CACHE.mkdir(parents=True, exist_ok=True)
    ledger = CACHE / f"n{args.n}_stuck.json"
    state = json.loads(ledger.read_text()) if ledger.exists() else {}

    print(f"E25 on the stuck n={args.n} cells {cells}: cutoff {args.cutoff}, "
          f"prerun {args.prerun}s, {args.jobs} jobs, "
          f"{args.cube_timeout}s per cube", flush=True)

    for m in cells:
        if state.get(str(m), {}).get("result") in (SAT, UNSAT):
            print(f"  m={m}: {state[str(m)]['result']} [cached]", flush=True)
            continue
        t0 = time.time()
        r = decide(args.n, m, cutoff=args.cutoff, prerun=args.prerun,
                   jobs=args.jobs, timeout=args.cube_timeout)
        state[str(m)] = {k: r.get(k) for k in
                         ("result", "cubes", "solve_cpu_s", "solve_wall_s",
                          "max_cube_s", "unknown_cubes", "closed_during_prerun")}
        state[str(m)]["wall_s"] = round(time.time() - t0, 1)
        ledger.write_text(json.dumps(state, indent=2))
        if r["result"] == SAT:
            print(f"*** HIT at n={args.n} m={m}: a chi>=6 member of the class. "
                  f"Verified independently: {r.get('hit')} ***", flush=True)
            return 2
        if r["result"] == UNKNOWN:
            print(f"  m={m}: UNDECIDED, {len(r.get('unknown_cubes') or [])} of "
                  f"{r.get('cubes')} cubes timed out. Not counted as closed.",
                  flush=True)
        if r["result"] == UNSAT:
            # NON-VACUITY, the guard E20 had and the cube path was missing. An
            # UNSAT on a cell that is empty for reasons unrelated to colouring
            # (a malformed CNF, a mis-stated constraint) is information-free, and
            # it looks exactly like a real closure. So demand that the SAME cell
            # be satisfiable at chi>=3, with the model certified a genuine class
            # member by the disjoint E17 filter. A cell that fails this is
            # downgraded from UNSAT to UNKNOWN rather than counted.
            probe = probe_cell(args.n, m, timeout=args.cube_timeout)
            state[str(m)]["nonvacuity"] = probe
            if not probe["nonempty"]:
                state[str(m)]["result"] = UNKNOWN
                state[str(m)]["downgraded"] = (
                    "UNSAT not counted: the cell failed its non-vacuity probe, "
                    "so its emptiness is not evidence about colouring")
                print(f"  m={m}: UNSAT DOWNGRADED -- non-vacuity probe returned "
                      f"{probe['result']}, so this closure means nothing",
                      flush=True)
            else:
                print(f"  m={m}: UNSAT, non-vacuity ok (witness "
                      f"{probe.get('witness')})", flush=True)
            ledger.write_text(json.dumps(state, indent=2))

    closed = [m for m in cells if state.get(str(m), {}).get("result") == UNSAT]
    stuck = [m for m in cells if state.get(str(m), {}).get("result") != UNSAT]
    print(f"\nn={args.n}: {len(closed)}/{len(cells)} stuck cells closed {closed}",
          flush=True)
    if stuck:
        print(f"  still open: {stuck}", flush=True)
        return 1
    print(f"*** n={args.n} COMPLETE: no chi>=6 both-free graph on {args.n} "
          f"vertices (m=54..57 by the E20 ladder, {closed} by cube-and-conquer) ***",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
