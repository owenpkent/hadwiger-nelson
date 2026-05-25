# Lean 4 / Mathlib substrate

Formal verification skeleton for Hadwiger-Nelson results.

## Status

Not initialized. The zeta-function repo's `lean/` directory has a working Phase 1 substrate (Lean 4.13.0 + Mathlib v4.13.0) that can be cloned as a starting point.

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

When ready:

```powershell
cd lean
elan default leanprover/lean4:v4.13.0
lake init HadwigerNelson
lake update
lake build
```

Mirror the zeta-function repo's lakefile and Mathlib pin.
