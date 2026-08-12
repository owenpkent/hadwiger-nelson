r"""E26: what vector system does the realizable lineage actually use?

L82 left the ring census (E24) blocked on a precise sub-problem. Its $\chi\ge5$
negatives are uninformative because the machinery could not find a $\chi=5$ graph
even in the field where de Grey's provably lives, so "no field reached $\chi\ge5$"
was a statement about the generator set rather than about the fields. This module
answers the sub-problem directly, from the data: it reads the coordinates of the
realized graphs and extracts the unit vectors they actually use.

WHAT THE DATA ALREADY SAYS. `sources/degrey_1585_vertices.sage` mentions
$\sqrt3$ 7,678 times, $\sqrt5$ 4,008 times, $\sqrt7$ 2,868 times and $\sqrt{11}$
2,760 times. So the de Grey graph lives in $\mathbb{Q}(\sqrt3,\sqrt5,\sqrt7,\sqrt{11})$,
degree 16 over $\mathbb{Q}$, and NOT in the degree-4 field
$\mathbb{Q}(\sqrt3,\sqrt{11})$ that `CLAUDE.md` records for it. That single fact
explains the L82 calibration failure completely: E24 was searching balls inside a
degree-4 subfield of the degree-16 field where the target lives, so no ball it
could build was ever going to contain the graph.

THE MEASUREMENT. For each realized graph: take every edge, form the coordinate
difference, confirm it is a unit vector, and collect the distinct ones. That set
is the vector system the construction really uses. Then ask the structural
question E24 needs answered: is it the orbit of a small generating set under the
sixth roots of unity, and how many rotors does it take?

CALIBRATION, because an extractor is a tool like any other. The same procedure is
run first on the MOSER SPINDLE, whose vector system is known by construction: the
sixth roots of unity together with one rotor at $\arccos(5/6)$, so a correct
extractor must return exactly those and no others. An extractor that cannot
recover a known 7-vertex answer says nothing about a 1585-vertex one.

SHAPE NOTE. This is a MEASUREMENT, not an existence question, so it is not an
`assay.Experiment`: forcing "what is the generator set?" into a YES/NO verdict
would be dishonest framing. The calibration discipline still applies and is
implemented here directly, which is the point of the discipline being a practice
rather than only a library.

Usage:
    python -m experiments.combinatorial.e26_generator_census --calibrate
    python -m experiments.combinatorial.e26_generator_census --graph degrey
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import mpmath as mp                                            # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCES = REPO / "sources"
CACHE = HERE / "_cache" / "e26"

TOL = mp.mpf("1e-20")
DEDUP = 14          # decimal places used to identify equal vectors


def parse_sage_vertices(path):
    """Read a .sage list of [x, y] with sqrt() terms into high-precision floats.

    Deliberately arithmetic-only parsing (no sympy): the file is a list of linear
    combinations of square roots with rational coefficients, and evaluating them
    numerically at 50 digits is both faster and enough for identifying vectors.
    """
    text = pathlib.Path(path).read_text()
    rows = re.findall(r"\[([^\[\]]+)\]", text)
    out = []
    for row in rows:
        parts = _split_top(row)
        if len(parts) != 2:
            continue
        out.append((_ev(parts[0]), _ev(parts[1])))
    return out


def _split_top(row):
    depth, cur, parts = 0, "", []
    for ch in row:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def _ev(expr):
    e = expr.strip()
    e = re.sub(r"sqrt\((\d+)\)", r"mp.sqrt(\1)", e)
    e = re.sub(r"(?<![\w.])(\d+)/(\d+)", r"(mp.mpf(\1)/\2)", e)
    return eval(e, {"mp": mp, "__builtins__": {}})


def load_edges_dimacs(path):
    edges = []
    for line in pathlib.Path(path).read_text().splitlines():
        f = line.split()
        if f and f[0] == "e":
            edges.append((int(f[1]) - 1, int(f[2]) - 1))
    return edges


def moser_spindle():
    """The calibration graph, built from its definition rather than a file."""
    r3 = mp.sqrt(3)
    # Rhombus of unit edges: O, A, B, C with the standard spindle coordinates.
    pts = [(mp.mpf(0), mp.mpf(0))]
    for ang in (mp.mpf(0), mp.pi / 3):
        pts.append((mp.cos(ang), mp.sin(ang)))
    pts.append((mp.cos(mp.pi / 6) * r3 / r3 + mp.mpf("0.5"), mp.sin(mp.pi / 3)))
    # Simpler and exact: build the spindle by two rhombi related by the rotation
    # with cos t = 5/6, which is the construction, so the extractor sees exactly
    # the vectors the construction uses.
    t = mp.acos(mp.mpf(5) / 6)
    base = [(mp.mpf(0), mp.mpf(0)), (mp.mpf(1), mp.mpf(0)),
            (mp.cos(mp.pi / 3), mp.sin(mp.pi / 3)),
            (mp.mpf(1) + mp.cos(mp.pi / 3), mp.sin(mp.pi / 3))]
    rot = [(mp.cos(t) * x - mp.sin(t) * y, mp.sin(t) * x + mp.cos(t) * y)
           for (x, y) in base]
    pts = base + rot[1:]
    edges = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = mp.sqrt((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2)
            if abs(d - 1) < mp.mpf("1e-30"):
                edges.append((i, j))
    return pts, edges


def unit_vectors(pts, edges):
    """The distinct edge-difference vectors, negation-collapsed, with counts."""
    seen = collections.Counter()
    bad = 0
    for i, j in edges:
        dx = pts[i][0] - pts[j][0]
        dy = pts[i][1] - pts[j][1]
        norm = mp.sqrt(dx * dx + dy * dy)
        if abs(norm - 1) > mp.mpf("1e-12"):
            bad += 1
            continue
        # Collapse v and -v: keep the representative in the upper half plane.
        if dy < 0 or (abs(dy) < mp.mpf("1e-25") and dx < 0):
            dx, dy = -dx, -dy
        key = (mp.nstr(dx, DEDUP), mp.nstr(dy, DEDUP))
        seen[key] += 1
    return seen, bad


def angle_structure(vectors):
    """Angles mod 60 degrees. A vector system that is the orbit of a few rotors
    under the sixth roots of unity shows up as a small number of residues."""
    residues = collections.Counter()
    for (sx, sy) in vectors:
        ang = math.degrees(math.atan2(float(sy), float(sx))) % 60.0
        r = round(ang, 6)
        # 60 and 0 are the SAME residue. Rounding after the modulo can land a
        # direction on 60.0, which the calibration caught as a spurious fourth
        # residue for the Moser spindle, whose construction admits exactly three.
        if abs(r - 60.0) < 1e-6 or abs(r) < 1e-6:
            r = 0.0
        residues[r] += 1
    return residues


def report(label, pts, edges, expect_vectors=None):
    vecs, bad = unit_vectors(pts, edges)
    res = angle_structure(vecs.keys())
    print(f"  {label}: {len(pts)} vertices, {len(edges)} edges, "
          f"{len(vecs)} distinct unit vectors (up to sign), "
          f"{bad} edges NOT of unit length", flush=True)
    print(f"    angle residues mod 60 deg: {len(res)} distinct "
          f"-> {sorted(res)[:8]}{' ...' if len(res) > 8 else ''}", flush=True)
    ok = True
    if expect_vectors is not None:
        ok = (len(vecs) == expect_vectors and bad == 0)
        print(f"    [{'ok' if ok else 'FAIL'}] expected {expect_vectors} "
              f"distinct unit vectors, got {len(vecs)}", flush=True)
    return {"label": label, "vertices": len(pts), "edges": len(edges),
            "distinct_unit_vectors": len(vecs), "non_unit_edges": bad,
            "angle_residues_mod60": len(res),
            "residues": sorted(float(r) for r in res)[:24], "ok": ok}


def calibrate():
    """The extractor must recover a known vector system before it is believed.

    The Moser spindle is built from the hexagonal directions plus ONE rotor at
    arccos(5/6), so its edges use the sixth roots of unity and their images under
    that rotor: 3 residues mod 60 degrees at most (0, the rotor angle, and its
    negative folded back).
    """
    print("E26 calibration: recover the Moser spindle's known vector system",
          flush=True)
    pts, edges = moser_spindle()
    r = report("moser_spindle", pts, edges)
    # The spindle has 11 edges; two rhombi share directions, so the distinct
    # vector count must be small and the residues must be few.
    ok = (len(edges) == 11 and r["angle_residues_mod60"] <= 3
          and r["non_unit_edges"] == 0)
    print(f"    [{'ok' if ok else 'FAIL'}] 11 edges, <=3 angle residues, "
          f"0 non-unit edges", flush=True)
    print(f"calibration: {'PASS' if ok else 'FAILURE'}", flush=True)
    return ok, r


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--graph", default=None, choices=["degrey"])
    ap.add_argument("--dps", type=int, default=50)
    args = ap.parse_args()
    mp.mp.dps = args.dps
    CACHE.mkdir(parents=True, exist_ok=True)

    ok, cal = calibrate()
    out = {"calibration": cal, "calibration_passed": ok}
    if not ok:
        print("extractor is not calibrated; refusing to report on the lineage",
              flush=True)
        (CACHE / "census.json").write_text(json.dumps(out, indent=2))
        return 1
    if args.calibrate:
        (CACHE / "census.json").write_text(json.dumps(out, indent=2))
        return 0

    if args.graph == "degrey":
        print("\nE26: the de Grey 1585 vector system", flush=True)
        pts = parse_sage_vertices(SOURCES / "degrey_1585_vertices.sage")
        edges = load_edges_dimacs(SOURCES / "degrey_1585.dimacs")
        out["degrey"] = report("degrey_1585", pts, edges)
    (CACHE / "census.json").write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
