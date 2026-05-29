/-
HN-4 (groundwork): the de Grey chi >= 5 BRIDGE THEOREM.

This file proves the general composition step that turns a non-4-colorable
finite unit-distance graph into the lower bound `5 <= chi(R^2)`. It is the
chi >= 5 analog of `MoserBridge.four_le_chromaticNumberOfPlane` (chi >= 4).

The logical skeleton has three independent pieces, each a small, reusable
lemma:

  1. `Colorable.of_hom` (local): a graph homomorphism `phi : G ->g H` pulls
     back colorings. If `H.Colorable n` then `G.Colorable n`. (Mathlib's
     `Coloring` is itself a hom into the complete graph, so the witness is
     `c.some.comp phi`, exactly as in `MoserBridge`.)

  2. `five_le_chromaticNumber_of_not_colorable_four` (local): from
     `not H.Colorable 4` to `5 <= H.chromaticNumber`, via the Mathlib
     equivalence `chromaticNumber_le_iff_colorable` and `ENat` arithmetic.

  3. `five_le_chromaticNumberOfPlane_of_hom`: compose (1) with `H =
     planeUnitDistanceGraph` and the plane chromaticNumber definition.

The convenience corollary `five_le_chromaticNumberOfPlane_of_coords` packages
the realization data the way `MoserBridge` does: an explicit coordinate map
`coords : V -> EuclideanPlane` plus a proof that adjacent vertices map to
points at Euclidean distance 1. A future session supplies a concrete
5-chromatic UDG by giving `coords`, the unit-distance proofs, and a
`not G.Colorable 4` certificate. See `lean/SHOT4_PLAN.md` for the remaining
(very hard) SAT-certificate piece.

NO `sorry`, NO `admit`, no new axioms beyond Mathlib's.
-/

import HadwigerNelson.Basic

namespace HadwigerNelson

open SimpleGraph

universe u v

/-! ### Piece 1: homomorphism pullback of colorings. -/

/-- A graph homomorphism `phi : G ->g H` pulls back `n`-colorings: if `H` is
    `n`-colorable then so is `G`. The witness is the composite hom
    `c.comp phi : G ->g completeGraph (Fin n)`, i.e. `Coloring` is a hom into
    the complete graph. This mirrors the `h.some.comp moserToPlane` step in
    `MoserBridge`. -/
theorem Colorable.of_hom {V : Type u} {W : Type v}
    {G : SimpleGraph V} {H : SimpleGraph W} (phi : G →g H) {n : ℕ}
    (hH : H.Colorable n) : G.Colorable n :=
  ⟨hH.some.comp phi⟩

/-! ### Piece 2: not-4-colorable forces chromaticNumber at least 5. -/

/-- For any simple graph `H`, if `H` is not 4-colorable then its chromatic
    number is at least 5. Proof: `chromaticNumber_le_iff_colorable` turns
    `not H.Colorable 4` into `not (H.chromaticNumber <= 4)`, i.e.
    `4 < H.chromaticNumber`; in `ENat` that is `5 <= H.chromaticNumber`. -/
theorem five_le_chromaticNumber_of_not_colorable_four
    {W : Type v} (H : SimpleGraph W) (h4 : ¬ H.Colorable 4) :
    5 ≤ H.chromaticNumber := by
  have hlt : (4 : ℕ∞) < H.chromaticNumber := by
    rw [← not_le]
    intro hle
    exact h4 (chromaticNumber_le_iff_colorable.mp hle)
  -- In `ℕ∞`, `4 < x` is equivalent to `5 ≤ x` (`4 + 1 ≤ x`).
  have : (4 : ℕ∞) + 1 ≤ H.chromaticNumber := Order.add_one_le_of_lt hlt
  simpa using this

/-! ### Piece 3: the plane bridge theorem. -/

/-- **HN-4 bridge theorem (general form).**

    If a simple graph `G` admits a graph homomorphism into the plane
    unit-distance graph (i.e. `G` is realized by unit-distance-respecting
    plane coordinates) AND `G` is not 4-colorable, then the chromatic number
    of the plane is at least 5.

    Composition: the hom pulls `planeUnitDistanceGraph.Colorable 4` back to
    `G.Colorable 4` (`Colorable.of_hom`); contrapositive gives
    `not planeUnitDistanceGraph.Colorable 4`; then
    `five_le_chromaticNumber_of_not_colorable_four` concludes. -/
theorem five_le_chromaticNumberOfPlane_of_hom {V : Type u}
    {G : SimpleGraph V} (phi : G →g planeUnitDistanceGraph)
    (h4 : ¬ G.Colorable 4) :
    5 ≤ chromaticNumberOfPlane := by
  have hplane : ¬ planeUnitDistanceGraph.Colorable 4 := fun hc =>
    h4 (Colorable.of_hom phi hc)
  exact five_le_chromaticNumber_of_not_colorable_four planeUnitDistanceGraph hplane

/-! ### Convenience corollary: realization by explicit coordinates.

    This packages the realization data exactly as `MoserBridge` produces it:
    a coordinate map `coords : V -> EuclideanPlane` together with a proof that
    every `G`-edge maps to a pair of points at Euclidean distance 1. From this
    the homomorphism into `planeUnitDistanceGraph` is reconstructed (the
    `x ≠ y` side condition follows because distance 1 forces distinctness, via
    `dist_self`). A future session plugging in a concrete 5-chromatic UDG only
    needs to supply `coords`, the per-edge distance proofs, and a
    `not G.Colorable 4` certificate. -/
theorem five_le_chromaticNumberOfPlane_of_coords {V : Type u}
    (G : SimpleGraph V) (coords : V → EuclideanPlane)
    (hdist : ∀ {a b : V}, G.Adj a b → dist (coords a) (coords b) = 1)
    (h4 : ¬ G.Colorable 4) :
    5 ≤ chromaticNumberOfPlane := by
  let phi : G →g planeUnitDistanceGraph :=
    { toFun := coords
      map_rel' := by
        intro a b hab
        have hd : dist (coords a) (coords b) = 1 := hdist hab
        have hne : coords a ≠ coords b := by
          intro heq
          rw [heq, dist_self] at hd
          norm_num at hd
        show (unitDistanceGraph EuclideanPlane).Adj (coords a) (coords b)
        exact (unitDistanceGraph_adj).mpr ⟨hne, hd⟩ }
  exact five_le_chromaticNumberOfPlane_of_hom phi h4

/-! ### The named target.

    `DeGreyLowerBound` (the proposition `5 <= chromaticNumberOfPlane`, defined
    in `Basic.lean`) is now reduced to a single hypothesis: the existence of a
    non-4-colorable finite UDG realized in the plane. The hard remaining work
    is supplying that hypothesis with a kernel-checkable certificate; see
    `lean/SHOT4_PLAN.md`. -/

/-- The de Grey lower bound `5 <= chi(R^2)` holds GIVEN a plane-realized graph
    that is not 4-colorable. This is the precise reduction the SAT-certificate
    piece must discharge. -/
theorem deGreyLowerBound_of_realized_not_four_colorable {V : Type u}
    {G : SimpleGraph V} (phi : G →g planeUnitDistanceGraph)
    (h4 : ¬ G.Colorable 4) :
    DeGreyLowerBound :=
  five_le_chromaticNumberOfPlane_of_hom phi h4

end HadwigerNelson
