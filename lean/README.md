# Lean 4 / Mathlib substrate

Formal verification skeleton for Hadwiger-Nelson results.

## Status

Skeleton landed 2026-05-25. Mirrors the zeta-function repo's Phase 1 substrate (Lean 4.13.0 + Mathlib v4.13.0).

Files:
- `lean-toolchain`, `lakefile.lean` Mathlib v4.13.0 pin
- `HadwigerNelson.lean` library root, imports all submodules
- `HadwigerNelson/Basic.lean` `unitDistanceGraph`, `planeUnitDistanceGraph`, `chromaticNumberOfPlane`, statements of `DeGreyLowerBound` and `IsbellUpperBound`
- `HadwigerNelson/MoserSpindle.lean` stub for HN-2; placeholder `moserSpindle` graph
- `HadwigerNelson/Controls.lean` Q^2, L^infty, R^1 wrong-approach controls

Not yet built. Requires `elan` to be installed; see Bootstrap below.

## Planned targets

| ID | Statement | Mathlib bridge | Difficulty |
|----|-----------|----------------|------------|
| HN-1 | Definition: `UnitDistanceGraph` in a metric space | `MetricSpace`, `SimpleGraph` | easy |
| HN-2 | Moser spindle is a UDG with $\chi = 4$ | needs explicit 7-vertex graph + brute-force 4-coloring + non-3-colorability | medium |
| HN-3 | Hexagonal tiling gives $\chi(\mathbb{R}^2) \leq 7$ | needs measure-theoretic tiling + coloring | hard |
| HN-4 | Statement of de Grey's $\chi(\mathbb{R}^2) \geq 5$ | needs encoding of the 1581-vertex graph + SAT certificate | very hard |
| HN-5 | $\chi(\mathbb{Q}^2) = 2$ (Woodall) | direct, but needs the parity argument | medium |
| HN-6 | $\chi(L^\infty\text{-UDG on } \mathbb{R}^2) = 4$ | direct construction | medium |

## Bootstrap

The lakefile and skeleton are committed. To build for the first time:

```powershell
# Install elan (one-time, Windows):
#   https://github.com/leanprover/elan/blob/master/README.md#windows
# Then:
cd lean
lake update    # fetches Mathlib v4.13.0 + transitive deps (slow, ~10 min)
lake build     # compiles HadwigerNelson against Mathlib
```

The first `lake build` after `lake update` downloads Mathlib's prebuilt cache (`lake exe cache get`) if available; otherwise it compiles Mathlib from source (hours). Use the cache when possible.

The current Lean files compile only after `lake build` has finished. Until then, IDE features (lake-server) will show import errors.
