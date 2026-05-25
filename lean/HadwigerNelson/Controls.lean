/-
Wrong-approach detector controls.

These are the three reference graphs whose chromatic numbers are *known* and
small. Any proof method that purports to give `χ(ℝ²) ≥ 5` and would also give
the same lower bound for one of these controls is structurally wrong.

  - `chromaticNumberOfQ2 = 2` (Woodall 1973): the rational plane has χ = 2.
  - `chromaticNumberOfLInfPlane = 4` (Chilakamarri): ℝ² with the L^∞ norm has χ = 4.
  - `chromaticNumberOfR1 = 2` (trivial): the real line has χ = 2.

Each unit-distance graph is defined directly via `SimpleGraph.fromRel` on the
appropriate edge predicate, sidestepping the `PseudoMetricSpace` instance on
non-Euclidean / non-Real metric structures. Statements only; proofs are
VERIFIER targets HN-5 (Q²) and HN-6 (L^∞).
-/

import HadwigerNelson.Basic

namespace HadwigerNelson

open SimpleGraph

/-! ### Control 1: the rational plane, χ(ℚ²) = 2 (Woodall 1973).

    Edge: rational points `(a,b)`, `(c,d)` with `(a-c)² + (b-d)² = 1`.
    This is the induced subgraph of the Euclidean unit-distance graph on
    rational coordinates, expressed without referring to `Real.sqrt`. -/

/-- The Q² unit-edge predicate: squared Euclidean distance equals 1. -/
def Q2UnitEdge (p q : ℚ × ℚ) : Prop :=
  (p.1 - q.1)^2 + (p.2 - q.2)^2 = 1

/-- The unit-distance graph on `ℚ²`. -/
def Q2UnitDistanceGraph : SimpleGraph (ℚ × ℚ) :=
  SimpleGraph.fromRel Q2UnitEdge

/-- The chromatic number of the rational plane. -/
noncomputable def chromaticNumberOfQ2 : ℕ∞ :=
  Q2UnitDistanceGraph.chromaticNumber

/-- Woodall 1973: `χ(ℚ²) = 2`. The standard proof colors by parity of the
    numerator of the squared distance to the origin, after clearing denominators.
    VERIFIER target HN-5. -/
def Q2IsTwoChromatic : Prop := chromaticNumberOfQ2 = 2

/-! ### Control 2: ℝ² with the L^∞ norm, χ = 4 (Chilakamarri).

    Edge: real points `(a,b)`, `(c,d)` with `max |a-c| |b-d| = 1`. We work
    with `ℝ × ℝ` and the explicit edge predicate, bypassing the `PiLp ⊤`
    machinery for this phase. -/

/-- The L^∞ unit-edge predicate on ℝ². -/
noncomputable def LInfUnitEdge (p q : ℝ × ℝ) : Prop :=
  max |p.1 - q.1| |p.2 - q.2| = 1

/-- The unit-distance graph on ℝ² under the L^∞ norm. -/
noncomputable def LInfUnitDistanceGraph : SimpleGraph (ℝ × ℝ) :=
  SimpleGraph.fromRel LInfUnitEdge

/-- The chromatic number of the L^∞ plane. -/
noncomputable def chromaticNumberOfLInfPlane : ℕ∞ :=
  LInfUnitDistanceGraph.chromaticNumber

/-- Chilakamarri: `χ(ℝ², L^∞) = 4`. The standard proof uses a unit-square
    tiling with a 4-coloring (mod 2 on x and y, with offsets).
    VERIFIER target HN-6. -/
def LInfIsFourChromatic : Prop := chromaticNumberOfLInfPlane = 4

/-! ### Control 3: the real line, χ(ℝ) = 2 (trivial). -/

/-- The R¹ unit-edge predicate: `|x - y| = 1`. -/
noncomputable def R1UnitEdge (x y : ℝ) : Prop := |x - y| = 1

/-- The unit-distance graph on ℝ. -/
noncomputable def R1UnitDistanceGraph : SimpleGraph ℝ :=
  SimpleGraph.fromRel R1UnitEdge

/-- The chromatic number of the real line. -/
noncomputable def chromaticNumberOfR1 : ℕ∞ :=
  R1UnitDistanceGraph.chromaticNumber

/-- `χ(ℝ) = 2`. Trivial: color by `⌊x⌋ mod 2`.
    Optional VERIFIER target (low difficulty). -/
def R1IsTwoChromatic : Prop := chromaticNumberOfR1 = 2

/-! ### The wrong-approach gate.

    A proposed method that claims `χ(ℝ²) ≥ 5` must NOT also entail
    `χ(ℚ²) ≥ 3` or `χ(ℝ², L^∞) ≥ 5`. These are negative reference points,
    not proof targets; they exist to be checked by ADVERSARY against any
    candidate construction. -/

end HadwigerNelson
