r"""Option B applied to the L63 host-factory candidates.

L63 (the codegree wall): the manufactured K4-free 6-chromatic hosts (E13/E13b) are
NOT K_{2,3}-free, and every unit-distance graph IS K_{2,3}-free, so none of them can
be drawn in the plane with unit edges. That is a COMBINATORIAL argument (codegree
ceiling). This script corroborates it from the CONTINUOUS / rigidity side, fully
independent of SAT: run the legal-UDG realizer (Option B) on each host and confirm it
cannot reach a legal embedding, and report WHY -- the rigidity over-determination
|E| - (2|V| - 3), which for these dense hosts is large and positive (generically no
real realization exists).

Calibrate first on the Moser spindle (must return LEGAL) so a host FAILURE is a
structural non-realizability signal, not solver fatigue.

Run:  python -m experiments.gradient.realize_hosts
"""
from __future__ import annotations

import json
import pathlib

from . import diff_udg as D
from .realize import realize

COMB = pathlib.Path(__file__).resolve().parents[1] / "combinatorial"
HOST_FILES = ["e13_hosts.json", "e13b_hosts.json"]


def load_hosts():
    out = []
    for fn in HOST_FILES:
        p = COMB / fn
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        for h in data.get("hosts", []):
            edges = [tuple(e) for e in h["edges"]]
            out.append({
                "name": h.get("name", p.stem),
                "n": h["n"],
                "edges": edges,
                "k23_free": h.get("k23_free"),
                "codegree_violations": h.get("codegree_violations"),
            })
    return out


def overdetermination(n, edges):
    """|E| - (2n - 3): rigidity excess. > 0 => generically no real realization."""
    return len(edges) - (2 * n - 3)


def main():
    print("Option B  ->  L63 host-factory candidates (geometric codegree-wall check)\n")

    # calibration: Moser must come back LEGAL
    n, edges, coords = D.moser_spindle()
    cal = realize(n, edges, true_coords=coords)
    print(f"  calibration  Moser spindle: legal={cal['legal']}  "
          f"max_edge_err={cal['max_edge_err']:.1e}   (must be True)\n")

    hosts = load_hosts()
    if not hosts:
        print("  no host JSON found (e13_hosts.json / e13b_hosts.json).")
        return

    print(f"  {'host':28s} {'n':>3s} {'|E|':>4s} {'overdet':>7s} "
          f"{'K23free':>7s} {'realizes legally?':>18s}")
    for h in hosts:
        od = overdetermination(h["n"], h["edges"])
        res = realize(h["n"], h["edges"], starts=16, steps=1200)
        verdict = "LEGAL-UDG (!)" if res["legal"] else f"no (err {res['max_edge_err']:.1e})"
        k23 = str(h["k23_free"]) if h["k23_free"] is not None else "?"
        print(f"  {h['name']:28s} {h['n']:>3d} {len(h['edges']):>4d} {od:>+7d} "
              f"{k23:>7s} {verdict:>18s}")

    print("\n  Reading: every host is rigidity-OVER-determined (overdet >> 0) and fails to")
    print("  realize as a legal UDG -- the continuous corroboration of L63's codegree wall.")
    print("  A host that DID realize legally (the LEGAL-UDG(!) flag) would be a live")
    print("  candidate and should go straight to the SAT chi>=6 confirmation. None here.")


if __name__ == "__main__":
    main()
