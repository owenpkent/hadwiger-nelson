r"""E29: ITERATED assembly on the new core, which is how the lineage was built.

E28 applied one rotation to the 56-vertex core in $\mathbb{Q}(\sqrt3,\sqrt{35})$:
7 of 8 rotors bound a copy to the motif, and $\chi$ stayed 4. That is a calibrated
negative (the same procedure reassembles the Moser spindle from two rhombi), but
it tested the weakest possible version of the move. The real constructions
ITERATE: de Grey's graph uses 78 unit vectors across 23 rotor residues (L83), and
Moser's spindle is only the first step of the same idea.

So this module does the honest version. Start from the motif, repeatedly add a
rotated copy chosen to maximise binding, and colour after each step, stopping the
moment $\chi \ge 5$ appears or the union stops growing usefully.

WHAT WOULD MAKE THIS SUCCEED OR FAIL INFORMATIVELY.

  * $\chi \ge 5$ at any depth is the object the program wants: a 5-chromatic
    unit-distance graph outside the P510 lineage's field, built on a motif that
    provably contains neither the Moser spindle nor Golomb (L82).
  * $\chi = 4$ at every depth, with binding present throughout, says the new
    core's rigidity is not of the kind that compounds. That is a real structural
    statement about why the lineage's field is special, and it is exactly what
    L57's forcing-sterility would predict if the property is field-wide rather
    than construction-specific.
  * Growth with NO new binding says the field is too poor in rotors, which is a
    statement about $\mathbb{Q}(\sqrt3,\sqrt{35})$ rather than about the motif.

The three outcomes are distinguishable, which is the point of running it.

GUARDS. Every union is re-checked as a LEGAL unit-distance graph in exact field
arithmetic (each claimed edge at distance exactly 1), duplicate points are
counted rather than silently merged, and $\chi$ is computed by the repo's SAT
portfolio. Calibration is inherited from E28 and re-run here: the identity rotor
must not inflate $\chi$, and the Moser rotor on a rhombus must reassemble the
spindle at $\chi=4$ with real binding edges.

Budgeted for overnight: a hard cap on union size and on depth, so it cannot
diverge the way the n=18 blind split did. Every step is written to disk as it
lands, so a kill costs one step.

Usage:
    python -m experiments.combinatorial.e29_iterated_assembly --depth 6
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import networkx as nx                                          # noqa: E402

from e24_ring_census import (Fld, rotate, chromatic_number)    # noqa: E402
from e28_spindle_new_core import (sqrt35_core, candidate_rotors,  # noqa: E402
                                  legal_udg, calibrate)

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e29"


def grow(f, pts, rotors, max_depth, max_points, log=print):
    """Greedy iterated assembly: at each step add the rotated copy that binds most.

    Greedy rather than exhaustive because the space of rotor sequences is huge and
    the binding count is the only signal available before colouring. The greedy
    choice is recorded so a later run can branch differently from any step.
    """
    current = list(pts)
    history = []
    for depth in range(1, max_depth + 1):
        best = None
        for idx, rot in enumerate(rotors):
            cand = current + [rotate(f, v, rot) for v in pts]
            if len(cand) > max_points:
                continue
            g, dup = legal_udg(f, cand)
            n0 = len(current)
            cross = sum(1 for u, v in g.edges() if (u < n0) != (v < n0))
            if best is None or cross > best["binding"]:
                best = {"rotor": idx, "binding": cross, "points": cand,
                        "graph": g, "duplicates": dup}
        if best is None:
            log(f"  depth {depth}: no rotor fits under the {max_points}-point cap")
            break
        g = best["graph"]
        chi = chromatic_number(g, hi=6) if g.number_of_edges() else 1
        step = {"depth": depth, "rotor": best["rotor"],
                "points": len(best["points"]), "edges": g.number_of_edges(),
                "binding_edges": best["binding"], "duplicate_points": best["duplicates"],
                "chi": chi}
        history.append(step)
        log(f"  depth {depth}: rotor {best['rotor']}, {step['points']} pts, "
            f"{step['edges']} edges, {step['binding_edges']} binding, chi = {chi}"
            f"{'   *** chi >= 5 ***' if chi and chi >= 5 else ''}")
        (CACHE / "assembly.json").write_text(json.dumps(history, indent=2))
        if chi and chi >= 5:
            return history, g, best["points"]
        if best["binding"] == 0:
            log(f"  depth {depth}: the added copy binds nothing; the field is out "
                f"of useful rotors for this motif")
            break
        current = best["points"]
    return history, None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depth", type=int, default=6)
    ap.add_argument("--max-points", type=int, default=900)
    ap.add_argument("--rotors", type=int, default=12)
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)

    if not calibrate():
        print("assembly procedure not calibrated; refusing to report", flush=True)
        return 1

    print("\nE29: iterated assembly in Q(sqrt3,sqrt35)", flush=True)
    t0 = time.time()
    f, pts, g0 = sqrt35_core()
    print(f"  motif: {len(pts)} points, {g0.number_of_edges()} edges, "
          f"chi = {chromatic_number(g0)}", flush=True)
    rotors = candidate_rotors(f, 35, limit=args.rotors)
    print(f"  {len(rotors)} candidate rotors, depth cap {args.depth}, "
          f"point cap {args.max_points}", flush=True)

    history, hit, hitpts = grow(f, pts, rotors, args.depth, args.max_points)
    elapsed = round(time.time() - t0, 1)

    if hit is not None:
        g6 = nx.to_graph6_bytes(nx.convert_node_labels_to_integers(hit),
                                header=False).decode().strip()
        out = {"result": "HIT", "chi": history[-1]["chi"], "history": history,
               "g6": g6, "elapsed_s": elapsed}
        print(f"\n*** chi >= 5 unit-distance graph assembled in "
              f"Q(sqrt3,sqrt35) at depth {history[-1]['depth']} ***", flush=True)
    else:
        best = max((h["chi"] or 0) for h in history) if history else 0
        out = {"result": "NO_HIT", "best_chi": best, "history": history,
               "elapsed_s": elapsed}
        print(f"\n  no chi>=5 in {len(history)} steps; best chi = {best} "
              f"[{elapsed}s]", flush=True)
    (CACHE / "result.json").write_text(json.dumps(out, indent=2))
    return 2 if hit is not None else 0


if __name__ == "__main__":
    sys.exit(main())
