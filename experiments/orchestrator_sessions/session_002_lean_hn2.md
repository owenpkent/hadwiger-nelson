# Session 002: HN-2 from spindle to plane in Lean

**Date**: 2026-05-25 (same day as session 001)
**Mode**: depth-first on one architectural target
**Architecture focus**: Architecture 1 (combinatorial / UDG) + formal verification

## Goal

Carry the Moser-spindle lower bound `chi(R^2) >= 4` from informal mathematics through to a Lean-kernel-verified theorem. Validate that the Lean substrate landed in session 001 can produce substantive proofs.

## What landed

### e1a Moser spindle SAT (commit ed28362)

`experiments/combinatorial/e1a_moser_spindle.py`. Two independent solvers (cadical195, glucose4) agree:
- k=3 UNSAT (Moser is not 3-colorable)
- k=4 SAT, witness colorings `[0,1,2,0,1,2,3]` (cadical195) and `[3,2,0,1,2,1,0]` (glucose4)

Solver-name gotcha documented: pysat in this install requires versioned names (`cadical195`, not bare `cadical`); kissat404's Windows binding segfaults via `bootstrap_with`.

### Surveyor integration (commit da27e71)

3300-word dossier `docs/research_atlas/arch1_sat_lineage.md` covering the de Grey 2018 to Mundinger 2025 lineage. Triggered:
- Atlas README corrections (509 vertices not "~510", Voronov 2021 added)
- LEARNINGS L1: 6-chromaticity is "easy" in HN-adjacent variants (2-distance 16-vertex Parts, finite odd-distance Parts) but uniquely resists in single-distance UDGs since 2018. Obstruction is structural rigidity inside `Q(sqrt 3, sqrt 11)`, not solver power.
- LEARNINGS L2: Moser spindle is structurally inessential (Voronov 64513-vertex spindle-free 5-chromatic UDG).

### HN-2 in Lean (commits a94b7bb, 80081c3, 7892185)

Full Moser chain, kernel-verified:

**MoserSpindle.lean**:
- `moserSpindleAdjBool`: pattern-matched Bool table for 11 unit edges across `Fin 7`. Adjacency table form makes `Symmetric` and `Irreflexive` decide via `fin_cases + decide`.
- HN-2a `moserSpindle_colorable_four`: from the e1a SAT witness `[0,1,2,0,1,2,3]`. Validity by `decide` per edge.
- HN-2b `moserSpindle_not_colorable_three`: `native_decide` over the `3^7 = 2187` candidate functions. Kernel `decide` blew the recursion stack at 2187 cases; native compilation runs in seconds.
- HN-2c `moserSpindle_chromaticNumber = 4`: glued via `Nat.sInf_upward_closed_eq_succ_iff` applied with `k = 3`. `Colorable.mono` provides the upward-closure of the Colorable set; HN-2a and HN-2b are exactly the two clauses of the iff.

**MoserBridge.lean** (HN-2d):
- `moserVertex : Fin 7 -> EuclideanPlane`: explicit coordinates with `Real.sqrt 3`, `Real.sqrt 11`, `Real.sqrt 33`. Rotation angle arccos(5/6) -> `(cos theta, sin theta) = (5/6, sqrt 11 / 6)`.
- Eleven `dist_moserVertex_i_j` lemmas, one per edge. Custom `moser_edge` tactic macro: unfold coords, substitute `sqrt 33 = sqrt 3 * sqrt 11` where present, close with `nlinarith` using `(sqrt 3)^2 = 3`, `(sqrt 11)^2 = 11`, and `sq_nonneg` hints.
- `moserToPlane : moserSpindle ->g planeUnitDistanceGraph`: dispatcher uses `fin_cases` on the 49 (a,b) pairs; 27 non-edges closed by `absurd hab (by decide)`, 22 edge orderings dispatched to one of the 11 cached lemmas (with `dist_comm` for the reverse direction). Required `maxHeartbeats 1000000` because the `first |` combinator has quadratic elaboration cost.
- `four_le_chromaticNumberOfPlane`: `SimpleGraph.chromaticNumber_le_of_forall_imp` + HN-2c.

## Verified state at end of session

The end-to-end statement is a Lean theorem:

```lean
theorem four_le_chromaticNumberOfPlane : 4 <= chromaticNumberOfPlane
```

Two independent computational pipelines now agree on `chi(Moser) = 4`:
1. Python (multi-solver SAT in e1a)
2. Lean kernel + native_decide (HN-2a + HN-2b)

Plus a third path from finite to plane: the Lean bridge in HN-2d.

## Pending

- **HN-3** Isbell hexagonal upper bound `chi <= 7`. Open. Hard: needs measure-theoretic tiling formalized.
- **HN-4** de Grey / Parts lower bound `chi >= 5`. Major project requiring graph data + DRAT-checker-in-Lean OR a Lean-native enumerative proof. E1b in Python (multi-solver SAT on the Parts 509 graph) is the natural Python-side preparation.
- **HN-5** Woodall `chi(Q^2) = 2`. Needs Pythagorean-triple parity argument, not brute force.
- **HN-6** Chilakamarri `chi(L^inf-plane) = 4`. Direct construction via square tiling.
- **Variants sub-dossier** (odd-distance, two-distance, sphere). Pending SURVEYOR session.
- **Field-theoretic search** (LEARNINGS L1). Novel BUILDER direction; needs design work.

## Lessons logged for future sessions

- For decide-style proofs on Fin types, watch for the kernel-vs-native distinction: 2187 candidates is comfortably native but stops kernel.
- Mathlib's `chromaticNumber` is `ℕ∞` (ENat); proving `= k` goes via `Colorable.chromaticNumber_eq_sInf` plus `Nat.sInf_upward_closed_eq_succ_iff` for upward-closed sets like `{n | Colorable n}`.
- For graph-hom Adj-preservation proofs with many cases, dispatch via cached `dist_X_Y` lemmas using `fin_cases + first | exact ...` is the cleanest; just raise `maxHeartbeats` to ~1M to absorb the combinator's quadratic cost.
- `EuclideanSpace.dist_eq` plus `Fin.sum_univ_two` plus `Real.dist_eq` plus `sq_abs` plus `Real.sqrt_eq_one` is the canonical chain for `dist x y = 1` proofs in `EuclideanSpace R (Fin 2)`.
