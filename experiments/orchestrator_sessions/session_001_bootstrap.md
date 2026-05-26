# Session 001: Bootstrap

**Date**: 2026-05-25
**Mode**: foundational scaffolding (pre-research)
**Architecture focus**: cross-cutting (substrate work)

## Goal

Stand up the repository: docs, four-architecture experiment scaffold, shared infrastructure (UDG + wrong-approach detectors), Lean substrate, six-agent role specs. Get to a state where research-level work in any of the four architectures can begin without further setup.

## What landed

### Repository scaffold (commit df91e44)

- `CLAUDE.md`, `README.md`, `TODO.md`, `requirements.txt`, `.gitignore`
- `docs/00_intuitive/what_is_the_problem.md` accessible exposition
- `docs/research_atlas/README.md` master research map
- `experiments/PROOF_ARCHITECTURES_PLAN.md`, `experiments/LEARNINGS.md`
- `experiments/_shared/`: `UnitDistanceGraph` (exact symbolic coords, SAT colorability), `wrong_approach_detectors.py` (Q², L^∞, R¹ controls), `smoke_test.py`
- Six agent specs under `.claude/agents/`: surveyor, builder, verifier, adversary, synthesizer, orchestrator. Adapted from the zeta repo's role specs; not copied verbatim, because zeta-specific structure (17-constraint framework, Davenport-Heilbronn detector, Phase 0-6) does not transfer cleanly to HN.

### Docs (commit prior to 3b82e91)

- `docs/01_undergraduate/moser_spindle.md` rigorous proof of χ ≥ 4 via the 7-vertex 11-edge construction with rotation angle arccos(5/6). Includes explicit 4-coloring and wrong-approach check.
- `docs/01_undergraduate/hexagonal_upper_bound.md` rigorous proof of χ ≤ 7 via the Eisenstein-lattice-mod-(2+ω) coloring of regular hexagons. Includes the R(√21 − 2) > 1 derivation.

### Lean substrate (commit 3b82e91, builds clean)

- `lakefile.lean`, `lean-toolchain` pinned to Lean v4.13.0 + Mathlib v4.13.0
- `lake-manifest.json` checked in (dependency lock)
- `HadwigerNelson.Basic`: `unitDistanceGraph` over `PseudoMetricSpace`, `unitDistanceGraph_adj` simp lemma proved, `planeUnitDistanceGraph`, `chromaticNumberOfPlane`, statements `DeGreyLowerBound` and `IsbellUpperBound`
- `HadwigerNelson.MoserSpindle`: HN-2 stub (`moserSpindle := ⊥` placeholder)
- `HadwigerNelson.Controls`: Q², L^∞, R¹ wrong-approach controls. Each defined directly via `SimpleGraph.fromRel` on an explicit edge predicate, avoiding the `PseudoMetricSpace` instance hunt on non-Euclidean structures. The Q² predicate stays in ℚ.
- Build: 1859/1859 modules, including all four `HadwigerNelson` modules.

### Smoke test

`python -m experiments._shared.smoke_test` passes 6/6:
- Moser spindle: 7 vertices, 11 edges in exact arithmetic
- Q² control sample: 23 vertices
- L^∞ grid (size 3): 16 vertices
- R¹ chain (n=5): 6 vertices, 5 edges
- Equilateral unit triangle K₃: 3 edges

## Verified state

- Python pipeline: sympy exact arithmetic confirms the Moser spindle's edge count and the equilateral triangle K₃. SAT solver (`python-sat` with cadical) installed; the e1a experiment will be the first end-to-end SAT decision.
- Lean pipeline: substrate compiles. The substrate has no proved theorems yet beyond the trivial `unitDistanceGraph_adj` simp lemma. All chromatic-number claims are statements (Props), not proofs.

## Pending

- e1a Moser spindle SAT: verify χ(Moser) = 4 via multi-solver SAT, archive certificate. Sets the DIMACS encoding template for e1b/e1c.
- e1b de Grey skeleton: import the 1581-vertex graph, SAT-verify χ ≥ 5.
- HN-2 Lean: replace `moserSpindle = ⊥` with the explicit 11-edge graph; prove `chromaticNumber = 4` by `decide` after `Fintype` instances on `Fin 7 → Fin 4` colorings.
- HN-5 Lean (Woodall): Q² parity argument is tractable since the predicate is decidable over ℚ.
- Architecture surveys: nothing surveyed yet; the atlas is a sketch, not a deep dive.

## Recommended next actions

1. **e1a Moser spindle SAT** (Architecture 1, ~50 lines Python). Highest information-per-line: confirms the SAT pipeline works end-to-end and produces a witness/certificate that can later be ported to Lean as HN-2's evidence. Bottom-up before top-down.
2. **HN-2 Lean** (Architecture 1 / formal). Builds on e1a but more involved: define the abstract `moserSpindle : SimpleGraph (Fin 7)` with the 11-edge structure, prove `chromaticNumber = 4` via `decide`. Bridge to `planeUnitDistanceGraph` via an injective graph homomorphism (needs the explicit 7 plane coordinates and distance-equality lemmas).
3. **HN-5 Lean** (Architecture 1 wrong-approach control). The Woodall parity argument: any unit-distance edge in ℚ² must have specific 2-adic structure, force-2-coloring. Predicate is decidable so a clean proof should be possible.

## Falsifiability triggers (none yet)

No research direction has accumulated enough sessions to hit a falsifiability trigger.

## Compute budget

Session 001 cost: one human-session of scaffolding. No SAT compute spent. Mathlib oleans downloaded (~1 GB cache, already on disk from prior work).
