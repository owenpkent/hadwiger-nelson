/-
L24 triple-coupling lift (formal statement and proof).

LEARNINGS.md L24 states the recursive lift of the L22 pair list-coloring
theorem to three halves. Let `H_1, H_2, H_3` be graphs on disjoint vertex
sets, `B_12, B_13, B_23` the pairwise bridge sets, and

    G = H_1 ∪ H_2 ∪ H_3 ∪ B_12 ∪ B_13 ∪ B_23.

Then `chi(G) >= 6` iff for every proper 5-coloring `c_1` of `H_1`, the
residual list-coloring on `H_2 ∪ H_3 ∪ B_23` with lists
`L_2(v) = [5] \ {c_1(u) : (u,v) in B_12}` and
`L_3(w) = [5] \ {c_1(u) : (u,w) in B_13}` is infeasible.

The clean formalization observes that `G` is a NESTED bridge graph:

    G = bridgeGraph H_1 (bridgeGraph H_2 H_3 B_23) B_1,

where the right half is itself the pair graph `H_2 ∪ H_3 ∪ B_23` on
`V_2 + V_3`, and `B_1 ⊆ V_1 × (V_2 + V_3)` carries `B_12` into the
`inl` summand and `B_13` into the `inr` summand. So L24 is precisely the
L22 list-coloring reformulation applied ONCE, at the 5-color level, to
the pair `(H_1, H_2 ∪ H_3 ∪ B_23)`.

Because the L21 covering lemma and the L22 list-coloring reformulation are
purely structural (the proofs never use the number `4`), this file reproves
them GENERICALLY over an arbitrary color type `α` inside the
`HadwigerNelson.Triple` namespace, then specializes to `α = Fin 5`. The
`Fin 4` versions in `L21CoveringLemma` / `L22ListColoring` are the
documented chi >= 5 instances of the same generic facts.

The residual `bridgeGraph H_2 H_3 B_23` and the explicit lists `L_2, L_3`
are recovered by `mem_allowedColors_lift_inl` / `mem_allowedColors_lift_inr`,
matching the LEARNINGS L24 statement on the nose.

This file has no `sorry`.
-/

import HadwigerNelson.Bridges
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Basic

namespace HadwigerNelson.Triple

open SimpleGraph HadwigerNelson

universe u v w

variable {V₁ : Type u} {V₂ : Type v} {V₃ : Type w} {α : Type*}

/-! ### Generic covering lemma (L21 over an arbitrary color type).

    Identical in content to `HadwigerNelson.bridgeGraph_colorable_four_iff`,
    but with `Fin 4` replaced by any color type `α`. The proofs mirror the
    `Fin 4` versions exactly; nothing here uses the cardinality of the
    color set. -/

/-- Glue two proper `α`-colorings of the halves that disagree at every
    bridge into a proper `α`-coloring of `bridgeGraph H₁ H₂ B`. -/
def combinedColoring {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)}
    (c₁ : H₁.Coloring α) (c₂ : H₂.Coloring α)
    (hB : ∀ p ∈ B, c₁ p.1 ≠ c₂ p.2) :
    (bridgeGraph H₁ H₂ B).Coloring α :=
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

/-- Left restriction of a coloring of `bridgeGraph H₁ H₂ B` to `H₁`. -/
def leftRestrict {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)} (c : (bridgeGraph H₁ H₂ B).Coloring α) :
    H₁.Coloring α :=
  Coloring.mk (fun a => c (Sum.inl a)) (by
    intro a b hab
    exact c.valid (by simp [hab]))

/-- Right restriction of a coloring of `bridgeGraph H₁ H₂ B` to `H₂`. -/
def rightRestrict {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)} (c : (bridgeGraph H₁ H₂ B).Coloring α) :
    H₂.Coloring α :=
  Coloring.mk (fun a => c (Sum.inr a)) (by
    intro a b hab
    exact c.valid (by simp [hab]))

/-- Splitting preserves bridge non-collision. -/
lemma bridge_noncollision {H₁ : SimpleGraph V₁} {H₂ : SimpleGraph V₂}
    {B : Set (V₁ × V₂)} (c : (bridgeGraph H₁ H₂ B).Coloring α) :
    ∀ p ∈ B, (leftRestrict c) p.1 ≠ (rightRestrict c) p.2 := by
  rintro ⟨u, v⟩ huv
  show c (Sum.inl u) ≠ c (Sum.inr v)
  apply c.valid
  simp [huv]

/-- **Generic covering lemma**. `bridgeGraph H₁ H₂ B` is `α`-colorable iff
    there is a pair of proper `α`-colorings of the halves that disagree at
    every bridge. -/
theorem bridgeGraph_coloring_nonempty_iff (H₁ : SimpleGraph V₁)
    (H₂ : SimpleGraph V₂) (B : Set (V₁ × V₂)) :
    Nonempty ((bridgeGraph H₁ H₂ B).Coloring α) ↔
      ∃ (c₁ : H₁.Coloring α) (c₂ : H₂.Coloring α),
        ∀ p ∈ B, c₁ p.1 ≠ c₂ p.2 := by
  constructor
  · rintro ⟨c⟩
    exact ⟨leftRestrict c, rightRestrict c, bridge_noncollision c⟩
  · rintro ⟨c₁, c₂, hB⟩
    exact ⟨combinedColoring c₁ c₂ hB⟩

/-! ### Generic list-coloring reformulation (L22 over an arbitrary color
    type). -/

/-- A proper `α`-coloring `c` of `G` with `c v ∈ L v` for every `v`. -/
structure ListColoring (G : SimpleGraph V₂) (L : V₂ → Set α) where
  toColoring : G.Coloring α
  mem_list : ∀ v, toColoring v ∈ L v

/-- `G` is list-colorable from `L` if a `ListColoring` exists. -/
def ListColorable (G : SimpleGraph V₂) (L : V₂ → Set α) : Prop :=
  Nonempty (ListColoring G L)

/-- Forbidden colors at `v ∈ V(H₂)` under a fixed `c₁`. -/
def forbiddenColors {H₁ : SimpleGraph V₁} (c₁ : H₁.Coloring α)
    (B : Set (V₁ × V₂)) (v : V₂) : Set α :=
  {x | ∃ u : V₁, (u, v) ∈ B ∧ c₁ u = x}

/-- Allowed colors at `v`: complement of the forbidden set. -/
def allowedColors {H₁ : SimpleGraph V₁} (c₁ : H₁.Coloring α)
    (B : Set (V₁ × V₂)) (v : V₂) : Set α :=
  (forbiddenColors c₁ B v)ᶜ

@[simp]
lemma mem_allowedColors {H₁ : SimpleGraph V₁} (c₁ : H₁.Coloring α)
    (B : Set (V₁ × V₂)) (v : V₂) (x : α) :
    x ∈ allowedColors c₁ B v ↔ ∀ u : V₁, (u, v) ∈ B → c₁ u ≠ x := by
  unfold allowedColors forbiddenColors
  simp only [Set.mem_compl_iff, Set.mem_setOf_eq, not_exists, not_and]

lemma noncollision_iff_list_membership {H₁ : SimpleGraph V₁}
    {H₂ : SimpleGraph V₂} (c₁ : H₁.Coloring α)
    (c₂ : H₂.Coloring α) (B : Set (V₁ × V₂)) :
    (∀ p ∈ B, c₁ p.1 ≠ c₂ p.2) ↔ ∀ v, c₂ v ∈ allowedColors c₁ B v := by
  constructor
  · intro h v
    rw [mem_allowedColors]
    intro u hub hcol
    exact h (u, v) hub hcol
  · intro h ⟨u, v⟩ hub
    have := (mem_allowedColors c₁ B v (c₂ v)).mp (h v)
    exact this u hub

/-- **Generic list-coloring reformulation**. `bridgeGraph H₁ H₂ B` is
    `α`-colorable iff some `c₁` makes `H₂` list-colorable from `L_{c₁}`. -/
theorem coloring_nonempty_iff_list (H₁ : SimpleGraph V₁)
    (H₂ : SimpleGraph V₂) (B : Set (V₁ × V₂)) :
    Nonempty ((bridgeGraph H₁ H₂ B).Coloring α) ↔
      ∃ c₁ : H₁.Coloring α, ListColorable H₂ (allowedColors c₁ B) := by
  rw [bridgeGraph_coloring_nonempty_iff]
  constructor
  · rintro ⟨c₁, c₂, hB⟩
    exact ⟨c₁, ⟨c₂, (noncollision_iff_list_membership c₁ c₂ B).mp hB⟩⟩
  · rintro ⟨c₁, ⟨c₂, hmem⟩⟩
    exact ⟨c₁, c₂, (noncollision_iff_list_membership c₁ c₂ B).mpr hmem⟩

/-- **Generic list-coloring reformulation (the lower-bound form)**.
    `bridgeGraph H₁ H₂ B` is NOT `α`-colorable iff for every `c₁`, `H₂` is
    not list-colorable from `L_{c₁}`. -/
theorem not_coloring_nonempty_iff_list (H₁ : SimpleGraph V₁)
    (H₂ : SimpleGraph V₂) (B : Set (V₁ × V₂)) :
    ¬ Nonempty ((bridgeGraph H₁ H₂ B).Coloring α) ↔
      ∀ c₁ : H₁.Coloring α, ¬ ListColorable H₂ (allowedColors c₁ B) := by
  rw [coloring_nonempty_iff_list]
  push_neg
  rfl

/-! ### The triple graph as a nested bridge graph. -/

/-- Carry the two `H₁`-incident bridge sets into a single bridge set over
    `V₁ × (V₂ + V₃)`: `B₁₂` lands in the `inl` summand, `B₁₃` in the `inr`
    summand. -/
def liftTripleBridges (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃)) :
    Set (V₁ × (V₂ ⊕ V₃)) :=
  fun p => Sum.elim (fun v => (p.1, v) ∈ B₁₂) (fun w => (p.1, w) ∈ B₁₃) p.2

@[simp]
lemma mem_liftTripleBridges_inl (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃))
    (u : V₁) (v : V₂) :
    (u, Sum.inl v) ∈ liftTripleBridges B₁₂ B₁₃ ↔ (u, v) ∈ B₁₂ := Iff.rfl

@[simp]
lemma mem_liftTripleBridges_inr (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃))
    (u : V₁) (w : V₃) :
    (u, Sum.inr w) ∈ liftTripleBridges B₁₂ B₁₃ ↔ (u, w) ∈ B₁₃ := Iff.rfl

/-- The combined three-halves graph `H₁ ∪ H₂ ∪ H₃ ∪ B₁₂ ∪ B₁₃ ∪ B₂₃` on
    `V₁ + (V₂ + V₃)`, realized as a nested bridge graph. -/
def tripleGraph (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (H₃ : SimpleGraph V₃) (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃))
    (B₂₃ : Set (V₂ × V₃)) : SimpleGraph (V₁ ⊕ (V₂ ⊕ V₃)) :=
  bridgeGraph H₁ (bridgeGraph H₂ H₃ B₂₃) (liftTripleBridges B₁₂ B₁₃)

/-! ### The lists `L_2` and `L_3` are exactly recovered.

    On the `inl` summand the allowed-color set is `[5] \ F₁₂(v)`; on the
    `inr` summand it is `[5] \ F₁₃(w)`. This matches the LEARNINGS L24
    statement verbatim. -/

@[simp]
lemma mem_allowedColors_lift_inl {H₁ : SimpleGraph V₁}
    (c₁ : H₁.Coloring α) (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃))
    (v : V₂) (x : α) :
    x ∈ allowedColors c₁ (liftTripleBridges B₁₂ B₁₃) (Sum.inl v) ↔
      ∀ u : V₁, (u, v) ∈ B₁₂ → c₁ u ≠ x := by
  rw [mem_allowedColors]
  constructor
  · intro h u hub; exact h u (by simpa using hub)
  · intro h u hub; exact h u (by simpa using hub)

@[simp]
lemma mem_allowedColors_lift_inr {H₁ : SimpleGraph V₁}
    (c₁ : H₁.Coloring α) (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃))
    (w : V₃) (x : α) :
    x ∈ allowedColors c₁ (liftTripleBridges B₁₂ B₁₃) (Sum.inr w) ↔
      ∀ u : V₁, (u, w) ∈ B₁₃ → c₁ u ≠ x := by
  rw [mem_allowedColors]
  constructor
  · intro h u hub; exact h u (by simpa using hub)
  · intro h u hub; exact h u (by simpa using hub)

/-! ### The L24 triple-coupling theorem. -/

/-- **L24 triple-coupling lift (the chi >= 6 characterization)**.

    The three-halves graph fails to be 5-colorable (so `chi >= 6`) iff for
    every proper 5-coloring `c₁` of `H₁`, the residual pair graph
    `H₂ ∪ H₃ ∪ B₂₃` is NOT list-colorable from the lists
    `L₂(v) = [5] \ F₁₂(v)` and `L₃(w) = [5] \ F₁₃(w)`.

    The residual lists are `allowedColors c₁ (liftTripleBridges B₁₂ B₁₃)`,
    which `mem_allowedColors_lift_inl/inr` identify with `L₂` and `L₃`. -/
theorem tripleGraph_not_colorable_five_iff_list
    (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂) (H₃ : SimpleGraph V₃)
    (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃)) (B₂₃ : Set (V₂ × V₃)) :
    ¬ (tripleGraph H₁ H₂ H₃ B₁₂ B₁₃ B₂₃).Colorable 5 ↔
      ∀ c₁ : H₁.Coloring (Fin 5),
        ¬ ListColorable (bridgeGraph H₂ H₃ B₂₃)
            (allowedColors c₁ (liftTripleBridges B₁₂ B₁₃)) :=
  not_coloring_nonempty_iff_list (α := Fin 5) H₁ (bridgeGraph H₂ H₃ B₂₃)
    (liftTripleBridges B₁₂ B₁₃)

/-- **L24 triple-coupling lift (the chi >= 6 sufficient condition)**.

    If for every proper 5-coloring `c₁` of `H₁` the residual pair graph is
    not list-colorable, then the three-halves graph has chromatic number at
    least 6. -/
theorem tripleGraph_six_chromatic_of_universal_residual_uncolorable
    (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂) (H₃ : SimpleGraph V₃)
    (B₁₂ : Set (V₁ × V₂)) (B₁₃ : Set (V₁ × V₃)) (B₂₃ : Set (V₂ × V₃))
    (huniv : ∀ c₁ : H₁.Coloring (Fin 5),
        ¬ ListColorable (bridgeGraph H₂ H₃ B₂₃)
            (allowedColors c₁ (liftTripleBridges B₁₂ B₁₃))) :
    ¬ (tripleGraph H₁ H₂ H₃ B₁₂ B₁₃ B₂₃).Colorable 5 :=
  (tripleGraph_not_colorable_five_iff_list H₁ H₂ H₃ B₁₂ B₁₃ B₂₃).mpr huniv

end HadwigerNelson.Triple
