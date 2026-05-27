/-
L21 covering lemma (formal statement and proof).

For two graphs `H_1, H_2` on disjoint vertex sets and a bridge set
`B subseteq V_1 x V_2`, the combined graph `bridgeGraph H_1 H_2 B` is
4-colorable iff there exist proper 4-colorings `c_1, c_2` of `H_1, H_2`
that AVOID every bridge constraint, i.e., `c_1(u) != c_2(v)` for every
`(u, v) in B`.

The covering lemma is the contrapositive: the combined graph is NOT
4-colorable iff for every pair `(c_1, c_2)` of proper 4-colorings, SOME
bridge `(u, v) in B` has `c_1(u) = c_2(v)`.

See LEARNINGS.md L21 for the experimental context and L22 for the
list-coloring reformulation. This file states the 4-colorable form
because that is the immediate predicate; the chi >= 5 lower bound is then
`Colorable G 4 -> False` (equivalently, `chromaticNumber G >= 5`).

This statement is fully proved (no `sorry`). The proof is short because
the construction of a combined coloring from `(c_1, c_2)` is precisely
`Sum.elim` of color functions, and the verification of properness on the
three edge cases (H_1 edges, H_2 edges, bridge edges) is a direct
case split on `Sum.inl` / `Sum.inr`.
-/

import HadwigerNelson.Bridges

namespace HadwigerNelson

open SimpleGraph

universe u v

variable {V₁ : Type u} {V₂ : Type v}

/-! ### Building a combined coloring from two half-colorings. -/

/-- Given proper 4-colorings `c_1, c_2` of `H_1, H_2` that disagree at every
    bridge (`c_1(u) ≠ c_2(v)` for `(u,v) ∈ B`), `Sum.elim c_1 c_2` is a
    proper 4-coloring of the combined `bridgeGraph H_1 H_2 B`. -/
def combinedColoring {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)}
    (c₁ : H₁.Coloring (Fin 4)) (c₂ : H₂.Coloring (Fin 4))
    (hB : ∀ p ∈ B, c₁ p.1 ≠ c₂ p.2) :
    (bridgeGraph H₁ H₂ B).Coloring (Fin 4) :=
  Coloring.mk (Sum.elim c₁ c₂) (by
    intro x y hxy
    match x, y with
    | Sum.inl a, Sum.inl b =>
        simp only [Sum.elim_inl]
        exact c₁.valid (by simpa using hxy)
    | Sum.inr a, Sum.inr b =>
        simp only [Sum.elim_inr]
        exact c₂.valid (by simpa using hxy)
    | Sum.inl a, Sum.inr b =>
        simp only [Sum.elim_inl, Sum.elim_inr]
        exact hB (a, b) (by simpa using hxy)
    | Sum.inr a, Sum.inl b =>
        simp only [Sum.elim_inl, Sum.elim_inr]
        have h := hB (b, a) (by simpa using hxy)
        exact h.symm)

/-! ### Splitting a combined coloring into two half-colorings. -/

/-- The left restriction of a coloring of `bridgeGraph H_1 H_2 B`: a proper
    coloring of `H_1`. -/
def leftRestrict {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)} (c : (bridgeGraph H₁ H₂ B).Coloring (Fin 4)) :
    H₁.Coloring (Fin 4) :=
  Coloring.mk (fun a => c (Sum.inl a)) (by
    intro a b hab
    exact c.valid (by simp [hab]))

/-- The right restriction of a coloring of `bridgeGraph H_1 H_2 B`: a proper
    coloring of `H_2`. -/
def rightRestrict {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)} (c : (bridgeGraph H₁ H₂ B).Coloring (Fin 4)) :
    H₂.Coloring (Fin 4) :=
  Coloring.mk (fun a => c (Sum.inr a)) (by
    intro a b hab
    exact c.valid (by simp [hab]))

/-- The bridge non-collision property is preserved when splitting a
    combined coloring: for any bridge `(u, v) ∈ B`, the left restriction
    at `u` differs from the right restriction at `v`. -/
lemma bridge_noncollision {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)} (c : (bridgeGraph H₁ H₂ B).Coloring (Fin 4)) :
    ∀ p ∈ B, leftRestrict c p.1 ≠ rightRestrict c p.2 := by
  rintro ⟨u, v⟩ huv
  show c (Sum.inl u) ≠ c (Sum.inr v)
  apply c.valid
  simp [huv]

/-! ### The L21 covering lemma. -/

/-- **L21 covering lemma (4-colorability characterization)**.
    The combined graph is 4-colorable iff there exists a pair of proper
    4-colorings of the halves that disagree at every bridge. -/
theorem bridgeGraph_colorable_four_iff (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) :
    (bridgeGraph H₁ H₂ B).Colorable 4 ↔
      ∃ (c₁ : H₁.Coloring (Fin 4)) (c₂ : H₂.Coloring (Fin 4)),
        ∀ p ∈ B, c₁ p.1 ≠ c₂ p.2 := by
  constructor
  · rintro ⟨c⟩
    exact ⟨leftRestrict c, rightRestrict c, bridge_noncollision c⟩
  · rintro ⟨c₁, c₂, hB⟩
    exact ⟨combinedColoring c₁ c₂ hB⟩

/-- **L21 covering lemma (the chi >= 5 form)**. The combined graph fails
    to be 4-colorable (so its chromatic number is at least 5) iff for
    every pair of proper 4-colorings of the halves, SOME bridge collides:
    `c_1(u) = c_2(v)` for some `(u, v) in B`. -/
theorem bridgeGraph_not_colorable_four_iff (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) :
    ¬ (bridgeGraph H₁ H₂ B).Colorable 4 ↔
      ∀ (c₁ : H₁.Coloring (Fin 4)) (c₂ : H₂.Coloring (Fin 4)),
        ∃ p ∈ B, c₁ p.1 = c₂ p.2 := by
  rw [bridgeGraph_colorable_four_iff]
  push_neg
  rfl

/-- **L21 covering lemma, chi >= 5 conclusion**. If every coloring pair
    is hit by some bridge, the chromatic number of the combined graph is
    strictly greater than 4. -/
theorem bridgeGraph_five_chromatic_of_covering
    (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂) (B : Set (V₁ × V₂))
    (hcov : ∀ (c₁ : H₁.Coloring (Fin 4)) (c₂ : H₂.Coloring (Fin 4)),
        ∃ p ∈ B, c₁ p.1 = c₂ p.2) :
    ¬ (bridgeGraph H₁ H₂ B).Colorable 4 :=
  (bridgeGraph_not_colorable_four_iff H₁ H₂ B).mpr hcov

end HadwigerNelson
