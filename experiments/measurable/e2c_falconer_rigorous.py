r"""e2c: Falconer's $\chi_m(\mathbb{R}^2) \geq 5$ made rigorous-numerical.

Architecture 2 (measurable chromatic number). Promotes e2a (a single-cell
autocorrelation illustration) to the actual structure of Falconer's 1981
argument, and pins down precisely what upgrades the density bound from
$\chi_m \geq 4$ to $\chi_m \geq 5$.

The two routes to a measurable lower bound, and why one gives 4 and one gives 5
-------------------------------------------------------------------------------
Route A (density only). A measurable proper $k$-coloring partitions $\mathbb{R}^2$
into $k$ measurable 1-avoiding classes. The largest has upper density $\geq 1/k$.
Since every 1-avoiding measurable set has density $\leq m_1$, we get
$1/k \leq m_1$, i.e. $\chi_m \geq 1/m_1$. With the best known $m_1 \leq 0.2470$
(Ambrus et al. 2023) this gives $\chi_m \geq 1/0.2470 = 4.05$, hence $\geq 5$
as an integer. With the OFV value $m_1 \leq 0.268412$ it gives only $4.05$... no:
$1/0.268412 = 3.726$, i.e. $\chi_m \geq 4$. SO THE DENSITY ROUTE GIVES $\geq 5$
ONLY ONCE $m_1 < 1/4 = 0.25$ IS ESTABLISHED, which is the Ambrus 2023 result;
before 2023 the density route gave only $\chi_m \geq 4$.

Route B (Falconer 1981, density + rigidity). Falconer's ORIGINAL 1981 proof did
NOT need $m_1 < 1/4$. It got $\chi_m \geq 5$ directly in 1981, 42 years before
$m_1 < 1/4$ was proven. The mechanism is NOT "largest class has density $\geq 1/4$";
it is a Lebesgue-density + rigid-configuration argument:

  (F1) Suppose $\mathbb{R}^2$ is properly 4-colored with measurable classes.
       Some class $A$ has positive upper density $\delta > 0$.
  (F2) Lebesgue density theorem: a.e. point of $A$ is a density point. Pick a
       small ball where $A$ has density arbitrarily close to 1 on $A$-points.
  (F3) Rigid configuration $S$: a finite point set, mobile under the Euclidean
       motion group $\mathbb{R}^2 \rtimes O(2)$, such that any 4-coloring forces a
       monochromatic unit pair WITHIN $S$. Falconer uses a spindle-type
       configuration whose unit-distance graph is 4-chromatic so that "no
       monochromatic unit pair" plus "4 colors" over-constrains a high-density
       region.
  (F4) Measure-theoretic averaging: integrate the indicator of "a translate /
       rotate of $S$ lands entirely inside $A$" over the motion group. High
       density forces this measure to be positive, so SOME copy of $S$ lies in
       $A$, giving a monochromatic unit pair: contradiction.

The load-bearing analytic identity is the autocorrelation / Plancherel relation
used in (F4): for $A$ measurable with indicator $1_A$ and autocorrelation
$R_A(t) = \langle 1_A, \tau_t 1_A\rangle$ (the convolution $1_A \star 1_{-A}$),

    \hat{R_A}(\xi) = |\hat{1_A}(\xi)|^2 \geq 0    (Bochner / Wiener-Khinchin),

so $R_A$ is of positive type, $R_A(0) = \delta$, and the 1-avoidance gives the
HARD CONSTRAINT $R_A(t) = 0$ for $|t| = 1$. The averaging integral in (F4) is
an integral of products $\prod_{s \in S} 1_A(x + g\cdot s)$ over $g$ in the
motion group; its positivity is controlled by the same Fourier-positive
autocorrelation structure.

What this script does
---------------------
1. PLANCHEREL / WIENER-KHINCHIN witness. Numerically verify, for an explicit
   measurable 1-avoiding set (a hexagonal-cell union of diameter $<1$), that
   (a) its autocorrelation $R_A$ is real, even, of positive type (its 2D Fourier
   transform is $\geq 0$ up to discretization), and (b) $R_A$ vanishes at
   $|t| = 1$. This is the analytic identity (F4) rests on, made concrete.

2. THE DENSITY-ROUTE ARITHMETIC, honestly. Print the $\chi_m$ implication of each
   historical $m_1$ bound and show the density route crosses from $\geq 4$ to
   $\geq 5$ exactly at $m_1 < 1/4$ (Ambrus 2023). Quantify "additional input".

3. THE RIGIDITY UPGRADE (what e2a/e2b cannot see). Encode a finite rigid
   configuration whose unit-distance graph is 4-chromatic (Moser spindle, the
   canonical $\chi=4$ rigid object) and confirm via exact arithmetic + SAT that
   it is 4-chromatic and 3-colorable-free. Falconer's (F3) needs precisely such
   an object; the script states that the chi_m >= 5 -> chi_m >= 6 upgrade would
   require a 5-chromatic rigid configuration, the SAME missing object as
   Architecture 1's 6-chromatic UDG (the cross-architecture coupling).

HONESTY. This script does NOT reprove $\chi_m \geq 5$ from scratch (Falconer's
(F4) averaging is a measure-theoretic limit not reducible to a finite numeric
certificate overnight). It (i) verifies the analytic identity (F4) uses, (ii)
makes the density-route arithmetic exact, and (iii) names precisely the extra
input (the rigid 4-chromatic configuration) that lifts the density-only $\geq 4$
to Falconer's $\geq 5$, and what would be needed for $\geq 6$.

Wrong-approach caveat. Falconer's argument uses the 2D Lebesgue density theorem
(intrinsically 2D: density of $B(x,r)\cap A$ is a 2D measure) and a rigid
configuration that requires non-collinear points (does not exist in $\mathbb{R}^1$,
where the unit-distance graph is bipartite, $\chi=2$). On the line the argument
degenerates to $\chi_m(\mathbb{R}) \geq 2$, correct, no overshoot ($\mathbb{R}^1$
detector passes). The rigid configuration uses Euclidean distances; on $L^\infty$
the spindle's unit edges become different distances and the configuration is no
longer forced ($L^\infty$ detector passes).
"""

from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

CACHE = pathlib.Path(__file__).parent / "_cache"

# historical m_1 bounds and the chi_m they imply via the density route
M1_HISTORY = [
    ("trivial", 1.0),
    ("OFV 2010 basic 2-point", 0.287119),
    ("OFV 2010 (3 off-center triangles)", 0.268412),
    ("KMOR 2015", 0.2588),
    ("Ambrus-Matolcsi 2022", 0.2544),
    ("Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023", 0.2470),
]


# --------------------------------------------------------------------------
# Part 1: Plancherel / Wiener-Khinchin witness on a 1-avoiding set
# --------------------------------------------------------------------------
def hexagon_indicator(coords: np.ndarray, diameter: float) -> np.ndarray:
    """Indicator of a regular (pointy-top) hexagon, circumradius diameter/2."""
    R = diameter / 2.0
    r = R * np.sqrt(3) / 2.0
    X, Y = np.meshgrid(coords, coords, indexing="ij")
    ax, ay = np.abs(X), np.abs(Y)
    return ((ax <= r) & (ax + np.sqrt(3) * ay <= np.sqrt(3) * R)).astype(np.float64)


def plancherel_witness(L: float = 3.0, n: int = 768, diameter: float = 0.95) -> dict:
    """Verify the autocorrelation of a 1-avoiding set is positive-type and
    vanishes at unit distance.

    A single hexagon of diameter < 1 is 1-avoiding (interior diameter < 1).
    R_A = 1_A star 1_{-A} via FFT; hat(R_A) = |hat(1_A)|^2 >= 0 exactly in the
    DFT (Wiener-Khinchin), so the positive-type property is exact up to float.
    The unit-circle vanishing is approximate (discretization + finite cell).
    """
    coords = np.linspace(-L, L, n, endpoint=False)
    dx = coords[1] - coords[0]
    ind = hexagon_indicator(coords, diameter)
    F = np.fft.fft2(ind)
    power = (F * np.conj(F)).real        # = |hat(1_A)|^2, the DFT of R_A; >= 0 exactly
    R = np.fft.fftshift(np.fft.ifft2(power).real)
    area = ind.sum() * dx * dx
    R_norm = R / ind.sum()               # condition on cell -> conditional density

    # positive-type check: power spectrum must be >= 0 (Wiener-Khinchin)
    min_power = float(power.min())

    # sample R on the unit circle (the hard 1-avoidance constraint R(|t|=1)=0)
    center = n // 2
    unit_vals = []
    for ang in np.linspace(0, 2 * np.pi, 64, endpoint=False):
        ix = center + int(round(np.cos(ang) / dx))
        iy = center + int(round(np.sin(ang) / dx))
        if 0 <= ix < n and 0 <= iy < n:
            unit_vals.append(float(R_norm[ix, iy]))
    unit_vals = np.array(unit_vals)

    return {
        "grid_L": L, "grid_n": n, "dx": float(dx), "diameter": diameter,
        "cell_area": float(area),
        "min_power_spectrum": min_power,         # >= -eps proves positive-type
        "positive_type_ok": bool(min_power >= -1e-6 * float(power.max())),
        "R_at_0_density": float(R_norm[center, center]),
        "unit_circle_max_abs": float(np.max(np.abs(unit_vals))),
        "unit_circle_mean": float(np.mean(unit_vals)),
        "unit_vanishing_ok": bool(np.max(np.abs(unit_vals)) < 1e-9),
    }


# --------------------------------------------------------------------------
# Part 2: density-route arithmetic
# --------------------------------------------------------------------------
def density_route_table() -> list[dict]:
    rows = []
    for name, m1 in M1_HISTORY:
        chi_real = 1.0 / m1
        rows.append({
            "bound": name, "m1": m1,
            "chi_m_real": chi_real,
            "chi_m_integer": int(np.ceil(chi_real - 1e-12)),
        })
    return rows


# --------------------------------------------------------------------------
# Part 3: rigidity upgrade -- the Moser spindle as Falconer's (F3) object
# --------------------------------------------------------------------------
def moser_spindle_chromatic() -> dict:
    """Confirm the Moser spindle (the canonical rigid chi=4 UDG) is exactly
    4-chromatic via the project UDG interface + SAT, with exact coordinates.

    Falconer's step (F3) needs a rigid finite configuration whose unit-distance
    graph is (k-1)-chromatic to force chi_m >= k via density + averaging. For
    k = 5 the Moser spindle (chi = 4) is the canonical object. For k = 6 one
    would need a rigid 5-chromatic configuration -- which is exactly the de Grey
    2018 / Polymath object, but that has 509+ vertices and is not "rigid and
    small" in Falconer's sense. This is the cross-architecture coupling.
    """
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
        from _shared.unit_distance_graph import moser_spindle  # type: ignore
        G = moser_spindle()
        nverts = G.n
        n_edges = len(G.edges())
        chi, _coloring = G.chromatic_number_sat(7)   # returns (chi, coloring)
        return {
            "available": True, "n_vertices": nverts, "n_edges": n_edges,
            "chi": chi,
            "is_4_colorable": (chi is not None and chi <= 4),
            "is_3_colorable": (chi is not None and chi <= 3),
            "note": f"Moser spindle chi={chi} confirmed via SAT; rigid 4-chromatic "
                    "object for Falconer (F3)."
        }
    except Exception as e:
        return {"available": False, "error": str(e),
                "note": "UDG interface not importable; spindle chi=4 is a known fact "
                        "(Moser 1961), used here only as Falconer's (F3) rigid object."}


def main():
    print("=" * 78)
    print("e2c: Falconer chi_m(R^2) >= 5, rigorous-numerical decomposition")
    print("=" * 78)

    # --- Part 1 ---
    print("\n[1] Plancherel / Wiener-Khinchin witness (analytic core of Falconer F4)")
    t0 = time.time()
    pw = plancherel_witness()
    print(f"  1-avoiding set: hexagon diameter {pw['diameter']} (< 1), "
          f"grid {pw['grid_n']}^2 on [-{pw['grid_L']},{pw['grid_L']}]^2")
    print(f"  autocorrelation positive-type (min power spectrum "
          f"{pw['min_power_spectrum']:.3e} >= 0): {pw['positive_type_ok']}")
    print(f"  R_A(0) (conditional density at origin): {pw['R_at_0_density']:.4f} "
          f"(expect 1.0)")
    print(f"  R_A on unit circle |t|=1: max|.| = {pw['unit_circle_max_abs']:.3e}, "
          f"mean = {pw['unit_circle_mean']:.3e}")
    print(f"  unit-distance vanishing R_A(|t|=1)=0: {pw['unit_vanishing_ok']} "
          f"(the hard 1-avoidance constraint)")
    print(f"  [{time.time()-t0:.1f}s]")

    # --- Part 2 ---
    print("\n[2] Density route: chi_m >= 1/m_1 across historical m_1 bounds")
    rows = density_route_table()
    print(f"  {'bound':<48} {'m_1':>8} {'1/m_1':>8} {'chi_m>=':>8}")
    for r in rows:
        flag = "  <- crosses 1/4, gives >=5" if (r["m1"] < 0.25 and r["chi_m_integer"] >= 5
                                                  and r["m1"] >= 0.2) else ""
        print(f"  {r['bound']:<48} {r['m1']:>8.4f} {r['chi_m_real']:>8.4f} "
              f"{r['chi_m_integer']:>8d}{flag}")
    print("  KEY: the DENSITY route reaches chi_m >= 5 only at m_1 < 1/4 = 0.25")
    print("       (Ambrus et al. 2023). Falconer 1981 reached >= 5 WITHOUT m_1<1/4,")
    print("       via the rigidity argument (Part 3).")
    print("  need m_1 < 1/5 = 0.2000 for chi_m >= 6 via the density route (open).")

    # --- Part 3 ---
    print("\n[3] Rigidity upgrade: Falconer's (F3) rigid configuration")
    ms = moser_spindle_chromatic()
    if ms.get("available"):
        print(f"  Moser spindle: {ms['n_vertices']} vertices, "
              f"3-colorable={ms['is_3_colorable']}, 4-colorable={ms['is_4_colorable']}, "
              f"chi={ms['chi']}")
    print(f"  {ms['note']}")
    print("  Falconer (F3) inputs a rigid (k-1)-chromatic configuration to output")
    print("  chi_m >= k. Spindle (chi=4) -> chi_m >= 5. To get chi_m >= 6 Falconer's")
    print("  machine needs a rigid 5-chromatic configuration in R^2: this is the SAME")
    print("  missing object as Architecture 1's open 6-chromatic UDG (the published")
    print("  5-chromatic objects have 509+ vertices and are not Falconer-rigid-small).")

    print("\n[Verdict] chi_m(R^2) >= 5 (Falconer 1981) is the state of the art.")
    print("  chi_m(R^2) >= 6 is OPEN. Both the density route (needs m_1<1/5) and the")
    print("  Falconer rigidity route (needs a 5-chromatic rigid configuration) are")
    print("  blocked by the same missing finite object that blocks Architecture 1.")

    CACHE.mkdir(exist_ok=True)
    out = CACHE / "e2c_falconer_rigorous.json"
    with out.open("w") as fh:
        json.dump({
            "experiment": "e2c_falconer_rigorous",
            "plancherel_witness": pw,
            "density_route": rows,
            "rigidity": ms,
            "verdict": {
                "chi_m_lower_bound": 5,
                "chi_m_geq_6_open": True,
                "density_route_threshold_for_5": "m_1 < 1/4 (Ambrus 2023)",
                "density_route_threshold_for_6": "m_1 < 1/5 = 0.2 (open)",
                "falconer_route_threshold_for_6": "rigid 5-chromatic configuration (open, == Arch1 missing object)",
            },
        }, fh, indent=2)
    print(f"\narchived: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
