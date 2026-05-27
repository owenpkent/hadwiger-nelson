r"""e1s: Compare Polymath 510 and de Grey 1585 as point sets.

Architecture 1, Shot 2. Continues L17/L18.

L17/L18 hinted at two distinct chi >= 5 "geometries":
- Polymath 510 in Q(sqrt 3, sqrt 11)
- de Grey 1585 in Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11) (strictly larger field)

Question: do they share vertices? Specifically:
(a) Is V(Polymath 510) a subset of V(de Grey 1585) directly?
(b) Is there a translation T such that T(V(Polymath)) intersects V(de Grey)
    in many vertices?

Since Polymath 510 has its "natural center" at origin (per L15) and de Grey
1585 has its natural center at v_0 = (2, 0) (per L16), the natural
translation to test is T = (2, 0). i.e., does V(Polymath 510) + (2, 0)
intersect V(de Grey 1585)?

If overlap is large: the two chi >= 5 graphs are related; Polymath 510 might
be (approximately) a sub-structure of de Grey 1585.
If overlap is small/none: they are truly different geometries in different
fields.
"""

from __future__ import annotations

import json
import pathlib
import re
import time

import mpmath as mp
import sympy as sp

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = REPO_ROOT / "experiments" / "combinatorial" / "_cache"

mp.mp.dps = 80


def mathematica_to_sympy(text):
    text = re.sub(r"Sqrt\[([^\]]+)\]", r"sqrt(\1)", text)
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        text = "(" + text[1:-1] + ")"
    return text


def parse_polymath_vtx(path):
    verts = []
    sympy_ctx = {"sqrt": sp.sqrt}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        t = sp.sympify(mathematica_to_sympy(line), locals=sympy_ctx, rational=True)
        verts.append((t[0], t[1]))
    return verts


def parse_sage_vertex_file(path):
    text = path.read_text(encoding="utf-8")
    sympy_ctx = {"sqrt": sp.sqrt}
    parsed = sp.sympify(text, locals=sympy_ctx, rational=True)
    return [(row[0], row[1]) for row in parsed]


def vertices_to_numeric(verts_sym, dps=80):
    out = []
    with mp.workdps(dps):
        for (x, y) in verts_sym:
            xn = mp.mpf(str(sp.N(x, dps)))
            yn = mp.mpf(str(sp.N(y, dps)))
            out.append((xn, yn))
    return out


def build_lookup(verts_num, tol=mp.mpf("1e-30")):
    def quantize(x):
        return mp.nstr(x, 30)
    table = {}
    for idx, (x, y) in enumerate(verts_num):
        table.setdefault((quantize(x), quantize(y)), []).append(idx)

    def lookup(p):
        kx = quantize(p[0])
        ky = quantize(p[1])
        for idx in table.get((kx, ky), []):
            ux, uy = verts_num[idx]
            if mp.fabs(p[0] - ux) < tol and mp.fabs(p[1] - uy) < tol:
                return idx
        # Try nearby quantization buckets (rare; only needed near quantization
        # boundaries).
        return -1
    return lookup


def main():
    print("e1s: compare Polymath 510 and de Grey 1585 as point sets")
    print("=" * 78)

    poly_path = REPO_ROOT / "sources" / "cnp-sat" / "vtx" / "510.vtx"
    dg_path = REPO_ROOT / "sources" / "degrey_1585_vertices.sage"

    print("  parsing Polymath 510...")
    poly_sym = parse_polymath_vtx(poly_path)
    poly_num = vertices_to_numeric(poly_sym, dps=80)
    print(f"    {len(poly_sym)} vertices")

    print("  parsing de Grey 1585...")
    dg_sym = parse_sage_vertex_file(dg_path)
    dg_num = vertices_to_numeric(dg_sym, dps=80)
    print(f"    {len(dg_sym)} vertices")

    dg_lookup = build_lookup(dg_num)
    print()

    # --- Phase 1: direct membership ---
    print("Phase 1: V(Polymath 510) subset of V(de Grey 1585) directly?")
    direct_hits = []
    for i, p in enumerate(poly_num):
        j = dg_lookup(p)
        if j >= 0:
            direct_hits.append((i, j))
    print(f"  direct vertex matches: {len(direct_hits)} / {len(poly_num)}")
    if direct_hits[:5]:
        for i, j in direct_hits[:5]:
            x, y = poly_num[i]
            print(f"    Polymath v_{i} = ({mp.nstr(x, 5)}, {mp.nstr(y, 5)}) = de Grey v_{j}")
    print()

    # --- Phase 2: translation by (2, 0) ---
    print("Phase 2: V(Polymath 510) + (2, 0) subset of V(de Grey 1585)?")
    tx = mp.mpf(2)
    ty = mp.mpf(0)
    trans_hits = []
    for i, p in enumerate(poly_num):
        p_t = (p[0] + tx, p[1] + ty)
        j = dg_lookup(p_t)
        if j >= 0:
            trans_hits.append((i, j))
    print(f"  T=(2,0) vertex matches: {len(trans_hits)} / {len(poly_num)}")
    if trans_hits[:5]:
        for i, j in trans_hits[:5]:
            x, y = poly_num[i]
            print(f"    Polymath v_{i} = ({mp.nstr(x, 5)}, {mp.nstr(y, 5)}) -> de Grey v_{j}")
    print()

    # --- Phase 3: systematic search for translation candidates ---
    # For each pair (p in Polymath, q in de Grey), the translation T = q - p maps
    # p to q. Compute how many other Polymath vertices match a de Grey vertex
    # under this same T. The best T gives max overlap.
    print("Phase 3: search for best translation T mapping Polymath -> de Grey.")
    print("  (For each (p, q) pair, count overlaps; report top candidates.)")

    # To keep this tractable, only consider Polymath's first 20 vertices as
    # potential p's (and try mapping each to every de Grey vertex).
    top_candidates = []
    t_start = time.time()
    poly_subset_for_T = poly_num[:30]
    for pi, p in enumerate(poly_subset_for_T):
        for qj, q in enumerate(dg_num):
            T = (q[0] - p[0], q[1] - p[1])
            count = 0
            for p2 in poly_num:
                p2_t = (p2[0] + T[0], p2[1] + T[1])
                if dg_lookup(p2_t) >= 0:
                    count += 1
            if count > 1:
                top_candidates.append({
                    "T": (mp.nstr(T[0], 12), mp.nstr(T[1], 12)),
                    "overlap": count, "p_idx": pi, "q_idx": qj,
                })
        if (pi + 1) % 10 == 0:
            print(f"    p={pi+1}/{len(poly_subset_for_T)} done, elapsed {time.time() - t_start:.1f}s", flush=True)
    top_candidates.sort(key=lambda r: -r["overlap"])
    print(f"  total candidate T's with overlap > 1: {len(top_candidates)}")
    seen_T = set()
    print("  top 10 unique translations by overlap:")
    shown = 0
    for c in top_candidates:
        if c["T"] in seen_T:
            continue
        seen_T.add(c["T"])
        print(f"    T = ({c['T'][0]}, {c['T'][1]}): overlap = {c['overlap']} (from p_{c['p_idx']} -> q_{c['q_idx']})")
        shown += 1
        if shown >= 10:
            break
    print()

    out = {
        "experiment": "e1s_compare_polymath_degrey",
        "poly_n": len(poly_num),
        "dg_n": len(dg_num),
        "direct_hits": len(direct_hits),
        "T_2_0_hits": len(trans_hits),
        "best_T_overlap": top_candidates[0] if top_candidates else None,
        "all_unique_T_top10": list(seen_T)[:10],
    }
    out_path = CACHE / "e1s_compare_polymath_degrey.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"archived: {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
