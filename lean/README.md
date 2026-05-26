# Lean 4 / Mathlib substrate

Formal verification skeleton for Hadwiger-Nelson results.

## Status

Skeleton landed and builds end-to-end 2026-05-25 (commit 3b82e91). Mirrors the zeta-function repo's Phase 1 substrate (Lean 4.13.0 + Mathlib v4.13.0).

Files:
- `lean-toolchain`, `lakefile.lean` Mathlib v4.13.0 pin
- `lake-manifest.json` dependency lock (checked in)
- `HadwigerNelson.lean` library root, imports all submodules
- `HadwigerNelson/Basic.lean` `unitDistanceGraph` (over any PseudoMetricSpace), `planeUnitDistanceGraph` (Euclidean), `chromaticNumberOfPlane`, statements of `DeGreyLowerBound` and `IsbellUpperBound`, and a proved `unitDistanceGraph_adj` simp lemma
- `HadwigerNelson/MoserSpindle.lean` HN-2 stub; `moserSpindle = ⊥` placeholder
- `HadwigerNelson/Controls.lean` Q^2, L^infty, R^1 wrong-approach controls; each defined directly via `SimpleGraph.fromRel` on an explicit edge predicate (Q^2 edge predicate stays in ℚ, no `Real.sqrt`)

Build result: `1859/1859` modules including all four `HadwigerNelson` modules.

## Planned targets

| ID | Statement | Mathlib bridge | Difficulty | Status |
|----|-----------|----------------|------------|--------|
| HN-1 | Definition: `unitDistanceGraph` in a pseudo-metric space | `PseudoMetricSpace`, `SimpleGraph.fromRel` | easy | done (Basic.lean) |
| HN-2 | Moser spindle is a UDG with $\chi = 4$ | explicit 7-vertex `Fin 7` graph, decide-based 4-coloring, decide-based non-3-colorability, homomorphism to `planeUnitDistanceGraph` | medium | stub (MoserSpindle.lean) |
| HN-3 | Hexagonal tiling gives $\chi(\mathbb{R}^2) \leq 7$ | measure-theoretic tiling + Eisenstein-lattice coloring | hard | not started |
| HN-4 | de Grey's $\chi(\mathbb{R}^2) \geq 5$ | 1581-vertex graph + verified SAT/DRAT certificate | very hard | not started |
| HN-5 | $\chi(\mathbb{Q}^2) = 2$ (Woodall) | parity argument on numerators after clearing denominators | medium | stub (Controls.lean) |
| HN-6 | $\chi(L^\infty\text{-UDG on } \mathbb{R}^2) = 4$ | direct construction using a unit-square tiling | medium | stub (Controls.lean) |

## Bootstrap

The lakefile, skeleton, and lock file are committed. On a fresh machine:

```powershell
# Install elan (one-time):
#   https://github.com/leanprover/elan/blob/master/README.md#windows
# Then:
cd lean
lake update                # fetches Mathlib v4.13.0 + transitive deps
lake exe cache get         # pulls prebuilt Mathlib oleans (fast, ~1 GB)
lake build                 # compiles HadwigerNelson
```

`lake exe cache get` downloads Mathlib's prebuilt cache (much faster than compiling Mathlib from source). On the current Windows dev box this completed in a few minutes; the cache was healthy and reported "No files to download" since all 5370 oleans were already on disk from prior work.

After this, `lake build` is incremental and rebuilds only the HadwigerNelson modules (~seconds).

## Editing

Open the project root (the `hadwiger-nelson/` directory containing both `lean/` and the Python code) in VS Code with the Lean 4 extension installed. The Lean server picks up `lean/lakefile.lean` automatically and provides goal view, hover types, and tactic suggestions.
