"""e2a: Falconer autocorrelation baseline.

Architecture 2 (measurable chromatic number). A pedagogical numerical
illustration of the Falconer 1981 obstruction.

Background. A *measurable* color class `A ⊂ ℝ²` of a measurable coloring
must avoid unit distance: no two points of `A` lie at distance exactly 1.
The autocorrelation

    R_A(t) = lim_{R→∞} (1 / Vol(B_R)) ∫_{B_R} 1_A(x) 1_A(x + t) dx

vanishes for all `t` with `|t| = 1`. Falconer's chi_m ≥ 5 proof combines
the vanishing on the unit circle with Plancherel and the translation
invariance of Lebesgue measure on ℝ² to derive a 4-coloring obstruction.

This script does NOT prove chi_m ≥ 5. It illustrates one component: it
computes the discrete autocorrelation of the indicator function of a
single hexagonal cell of diameter slightly less than 1 (an obvious
distance-1-avoiding set) on a finite [0, L]² grid, then reports the
autocorrelation values at offset distances near 1.

Expectation: the autocorrelation is positive for small offsets (within
the cell), drops to 0 once the offset exceeds the cell diameter, and is
exactly 0 at `|t| = 1`.

For an actual chi_m ≥ 5 numerical check, see e2b (TODO; will compute the
Plancherel side of Falconer's argument).
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

import numpy as np

CACHE = pathlib.Path(__file__).parent / "_cache"


@dataclass
class GridConfig:
    """Finite [-L, L]² grid at resolution `n_per_side` per axis."""
    L: float = 2.0
    n_per_side: int = 256

    @property
    def dx(self) -> float:
        return 2 * self.L / self.n_per_side

    @property
    def coords(self) -> np.ndarray:
        return np.linspace(-self.L, self.L, self.n_per_side, endpoint=False)


def hexagon_indicator(grid: GridConfig, diameter: float, center=(0.0, 0.0)) -> np.ndarray:
    """Indicator function of a regular hexagon (pointy-top, axis-aligned).

    `diameter` is the long diagonal (vertex-to-opposite-vertex), so the
    circumradius is `diameter / 2`. The hexagonal coloring construction
    uses hexagons with diameter slightly less than 1 so no two interior
    points are at distance exactly 1.

    Constraints (pointy-top, vertex at (0, R)):
      - |x| ≤ r  (between the left and right vertical edges, inradius r)
      - |x| + √3 |y| ≤ √3 R  (between the four slanted edges)
    """
    R = diameter / 2  # circumradius
    r = R * np.sqrt(3) / 2  # inradius
    coords = grid.coords
    X, Y = np.meshgrid(coords - center[0], coords - center[1], indexing="ij")
    abs_x = np.abs(X)
    abs_y = np.abs(Y)
    inside = (abs_x <= r) & (abs_x + np.sqrt(3) * abs_y <= np.sqrt(3) * R)
    return inside.astype(np.float64)


def autocorrelation_fft(indicator: np.ndarray) -> np.ndarray:
    """Discrete 2D autocorrelation R(t) = ∫ f(x) f(x+t) dx via FFT.

    Returns the un-normalized autocorrelation; divide by indicator.sum()
    to get the conditional density. The result is `fftshift`-ed so the
    origin t=0 sits at the center of the array.
    """
    F = np.fft.fft2(indicator)
    R = np.fft.ifft2(F * np.conj(F)).real
    return np.fft.fftshift(R)


def query_autocorrelation_at_offsets(
    R: np.ndarray, grid: GridConfig, offsets: list[tuple[float, float]]
) -> list[float]:
    """Sample the autocorrelation at given (tx, ty) offsets via nearest-neighbor."""
    n = grid.n_per_side
    center = n // 2
    samples = []
    for tx, ty in offsets:
        ix = center + int(round(tx / grid.dx))
        iy = center + int(round(ty / grid.dx))
        if 0 <= ix < n and 0 <= iy < n:
            samples.append(float(R[ix, iy]))
        else:
            samples.append(float("nan"))
    return samples


def main():
    grid = GridConfig(L=2.0, n_per_side=512)
    diameter = 0.95  # < 1, so the hexagon avoids unit distance internally

    print(f"Grid: [-{grid.L}, {grid.L}]^2 at resolution {grid.n_per_side}^2 "
          f"(dx = {grid.dx:.5f})")
    print(f"Hexagon diameter: {diameter}")

    indicator = hexagon_indicator(grid, diameter)
    print(f"Hexagon area (grid count): {indicator.sum():.0f} cells, "
          f"{indicator.sum() * grid.dx**2:.4f} area units (expected "
          f"{1.5 * np.sqrt(3) * (diameter/2)**2:.4f})")

    R = autocorrelation_fft(indicator)
    R_normalized = R / indicator.sum()  # condition on hexagon area

    # Sample autocorrelation at a variety of offsets.
    angles = np.linspace(0, np.pi / 2, 6)
    sample_offsets = []
    sample_labels = []
    for r_offset in [0.0, diameter / 4, diameter / 2, diameter * 0.95, 1.0, 1.2]:
        sample_offsets.append((r_offset, 0.0))
        sample_labels.append(f"|t|={r_offset:.3f}")
    samples = query_autocorrelation_at_offsets(R_normalized, grid, sample_offsets)

    print("\nNormalized autocorrelation along the x-axis:")
    for label, val in zip(sample_labels, samples):
        marker = "  <- inside hex" if val > 0.01 else ("  <- outside hex" if val < 0.01 else "")
        print(f"  {label}: {val:.6f}{marker}")

    # The key Falconer-relevant value: autocorrelation at |t|=1.
    samples_at_unit = []
    for angle in np.linspace(0, 2 * np.pi, 16, endpoint=False):
        samples_at_unit.append(query_autocorrelation_at_offsets(
            R_normalized, grid, [(np.cos(angle), np.sin(angle))]
        )[0])

    print(f"\nAutocorrelation on the unit circle (|t|=1), 16 sample angles:")
    print(f"  min = {min(samples_at_unit):.6f}")
    print(f"  max = {max(samples_at_unit):.6f}")
    print(f"  mean = {np.mean(samples_at_unit):.6f}")
    print(f"  Expected: identically 0 (the hexagon avoids unit distance internally)")

    CACHE.mkdir(exist_ok=True)
    out_path = CACHE / "e2a_falconer_hexagon.json"
    with out_path.open("w") as f:
        json.dump(
            {
                "experiment": "e2a_falconer_autocorrelation",
                "grid_L": grid.L,
                "grid_n_per_side": grid.n_per_side,
                "grid_dx": grid.dx,
                "hexagon_diameter": diameter,
                "samples_axis": list(zip(sample_labels, samples)),
                "samples_unit_circle": samples_at_unit,
                "unit_circle_min": float(min(samples_at_unit)),
                "unit_circle_max": float(max(samples_at_unit)),
                "unit_circle_mean": float(np.mean(samples_at_unit)),
            },
            f,
            indent=2,
        )
    print(f"\narchived: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
