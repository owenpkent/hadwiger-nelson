/-
Foundational definitions for the HadwigerNelson project.

This module sets up the unit-distance graph on a (pseudo-)metric space and the
chromatic number of the Euclidean plane.

Status note (Phase 1 substrate, 2026-05-25 onwards):

  The unit-distance graph is built directly via `SimpleGraph.fromRel` on the
  predicate `dist x y = 1`. The chromatic number is taken from Mathlib's
  `SimpleGraph.chromaticNumber : ℕ∞`. The Hadwiger-Nelson problem is then the
  statement `chromaticNumber (unitDistanceGraph (EuclideanSpace ℝ (Fin 2)))`,
  with the known bounds `5 ≤ χ ≤ 7` to be wired up as VERIFIER targets HN-2..4
  reduce to it.
-/

import Mathlib.Combinatorics.SimpleGraph.Basic
import Mathlib.Combinatorics.SimpleGraph.Coloring
import Mathlib.Analysis.InnerProductSpace.EuclideanDist
import Mathlib.Topology.MetricSpace.Basic

namespace HadwigerNelson

open SimpleGraph

/-! ### The unit-distance graph on a metric space. -/

/-- The unit-distance graph on a pseudo-metric space: vertices are points of
    the space, with an edge between `x` and `y` iff `dist x y = 1`. -/
def unitDistanceGraph (α : Type*) [PseudoMetricSpace α] : SimpleGraph α :=
  SimpleGraph.fromRel (fun x y => dist x y = 1)

@[simp]
lemma unitDistanceGraph_adj {α : Type*} [PseudoMetricSpace α] {x y : α} :
    (unitDistanceGraph α).Adj x y ↔ x ≠ y ∧ dist x y = 1 := by
  unfold unitDistanceGraph
  rw [SimpleGraph.fromRel_adj]
  constructor
  · rintro ⟨hne, h | h⟩
    · exact ⟨hne, h⟩
    · exact ⟨hne, by rwa [dist_comm] at h⟩
  · rintro ⟨hne, h⟩
    exact ⟨hne, Or.inl h⟩

/-! ### The Euclidean plane and the Hadwiger-Nelson chromatic number. -/

/-- The Euclidean plane `ℝ²` as a metric space. We use Mathlib's
    `EuclideanSpace ℝ (Fin 2)` to get the standard Euclidean norm. -/
abbrev EuclideanPlane : Type := EuclideanSpace ℝ (Fin 2)

/-- The unit-distance graph on the Euclidean plane.
    Marked `noncomputable` because `dist` on `EuclideanSpace ℝ` involves `Real.sqrt`. -/
noncomputable def planeUnitDistanceGraph : SimpleGraph EuclideanPlane :=
  unitDistanceGraph EuclideanPlane

/-- The chromatic number of the plane, χ(ℝ²). The Hadwiger-Nelson problem
    asks for its exact value; current bounds are `5 ≤ χ(ℝ²) ≤ 7`. -/
noncomputable def chromaticNumberOfPlane : ℕ∞ :=
  planeUnitDistanceGraph.chromaticNumber

/-! ### Known bounds (statements; proofs are VERIFIER targets). -/

/-- The de Grey 2018 lower bound: `χ(ℝ²) ≥ 5`. Reduces to the
    non-4-colorability of a specific 1581-vertex UDG, verified via SAT.
    VERIFIER target HN-4. -/
def DeGreyLowerBound : Prop := 5 ≤ chromaticNumberOfPlane

/-- The Isbell hexagonal upper bound: `χ(ℝ²) ≤ 7`. Reduces to a 7-coloring
    of `ℝ²` via slightly-undersized regular hexagons.
    VERIFIER target HN-3. -/
def IsbellUpperBound : Prop := chromaticNumberOfPlane ≤ 7

/-- The combined classical bounds. -/
def HadwigerNelsonBounds : Prop :=
  5 ≤ chromaticNumberOfPlane ∧ chromaticNumberOfPlane ≤ 7

end HadwigerNelson
