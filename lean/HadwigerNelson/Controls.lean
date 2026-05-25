/-
Wrong-approach detector controls.

These are the three reference graphs whose chromatic numbers are *known* and
small. Any proof method that purports to give `χ(ℝ²) ≥ 5` and would also give
the same lower bound for one of these controls is structurally wrong.

  - `chromaticNumberOfQ2 = 2` (Woodall 1973): the rational plane has χ = 2.
  - `chromaticNumberOfLInfPlane = 4` (Chilakamarri): ℝ² with the L^∞ norm has χ = 4.
  - `chromaticNumberOfR1 = 2` (trivial): the real line has χ = 2.

Statements only; proofs are VERIFIER targets HN-5 (Q²) and HN-6 (L^∞).
-/

import HadwigerNelson.Basic

namespace HadwigerNelson

open SimpleGraph

/-! ### Control 1: the rational plane, χ(ℚ²) = 2 (Woodall 1973). -/

/-- The rational plane `ℚ²` as a subset of `ℝ²` via the canonical inclusion. -/
abbrev RationalPlane : Type := ℚ × ℚ

instance : PseudoMetricSpace RationalPlane := by
  -- Inherits from the inclusion `ℚ² ↪ ℝ²`. Standard; left as a TODO bridge.
  exact inferInstanceAs (PseudoMetricSpace (ℚ × ℚ))

/-- The unit-distance graph on `ℚ²`. -/
def Q2UnitDistanceGraph : SimpleGraph RationalPlane :=
  unitDistanceGraph RationalPlane

/-- Woodall 1973: `χ(ℚ²) = 2`. The standard proof colors by parity of the
    numerator of the squared distance to the origin, after clearing denominators.
    VERIFIER target HN-5. -/
def Q2IsTwoChromatic : Prop :=
  Q2UnitDistanceGraph.chromaticNumber = 2

/-! ### Control 2: ℝ² with the L^∞ norm, χ = 4 (Chilakamarri). -/

/-- ℝ² as a metric space using the L^∞ (Chebyshev / sup) norm. We index this
    via a type synonym to disambiguate from the Euclidean instance. -/
def LInfPlane : Type := Fin 2 → ℝ

instance : PseudoMetricSpace LInfPlane :=
  PiLp.pseudoMetricSpace ⊤ (fun _ : Fin 2 => ℝ)

/-- The unit-distance graph on ℝ² under the L^∞ norm. -/
def LInfUnitDistanceGraph : SimpleGraph LInfPlane :=
  unitDistanceGraph LInfPlane

/-- Chilakamarri: `χ(ℝ², L^∞) = 4`. The standard proof uses a unit-square
    tiling with a 4-coloring (mod 2 on x and y, with offsets).
    VERIFIER target HN-6. -/
def LInfIsFourChromatic : Prop :=
  LInfUnitDistanceGraph.chromaticNumber = 4

/-! ### Control 3: the real line, χ(ℝ) = 2 (trivial). -/

/-- The unit-distance graph on `ℝ`: edges between reals exactly one apart. -/
def R1UnitDistanceGraph : SimpleGraph ℝ :=
  unitDistanceGraph ℝ

/-- `χ(ℝ) = 2`. Trivial: color by `⌊x⌋ mod 2`.
    Optional VERIFIER target (low difficulty). -/
def R1IsTwoChromatic : Prop :=
  R1UnitDistanceGraph.chromaticNumber = 2

/-! ### The wrong-approach gate.

    A proposed method that claims `χ(ℝ²) ≥ 5` must NOT also entail
    `χ(ℚ²) ≥ 3` or `χ(ℝ², L^∞) ≥ 5`. These are negative reference points,
    not proof targets; they exist to be checked by ADVERSARY against any
    candidate construction. -/

end HadwigerNelson
