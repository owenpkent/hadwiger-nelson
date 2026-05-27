/-
L22 list-coloring reformulation of the L21 covering lemma.

For `H_1, H_2` on disjoint vertex sets and a bridge set `B`, fix a proper
4-coloring `c_1` of `H_1`. For each `v in V(H_2)` define the FORBIDDEN
color set `F(v) = {c_1(u) : (u, v) in B}` and the LIST `L(v) = Fin 4 \ F(v)`.

The list-coloring reformulation:

  Colorable(bridgeGraph H_1 H_2 B, 4)
  iff
  exists c_1 : H_1.Coloring (Fin 4),
    H_2 admits a list-coloring from L_{c_1}.

Equivalently (contrapositive):

  not Colorable(bridgeGraph, 4)
  iff
  forall c_1 : H_1.Coloring (Fin 4),
    H_2 admits no list-coloring from L_{c_1}.

This file:
  1. defines `ListColorable` (the existence of a proper coloring with
     `c v in L v` for all `v`).
  2. defines `forbiddenColors c_1 B v = F(v)` and
     `allowedColors c_1 B v = L(v)`.
  3. proves the iff above, using `bridgeGraph_colorable_four_iff` from
     L21 plus a small bookkeeping lemma equating the "no-collision"
     existential with `ListColorable`.

See LEARNINGS.md L22 for the experimental motivation and the explicit
counter-example showing C4 (L21's original conjecture) is strictly
stronger than the list-coloring condition.
-/

import HadwigerNelson.L21CoveringLemma
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Basic

namespace HadwigerNelson

open SimpleGraph

universe u v

variable {V₁ : Type u} {V₂ : Type v}

/-! ### List-coloring predicate.

    A `ListColorable G L` instance is a witness: there exists a proper
    coloring of `G` whose value at every vertex `v` is in `L v`. This
    is the existential version; `IsListColorable` packages the witness
    inside the proposition. -/

/-- A proper coloring `c` of `G` with `c v ∈ L v` for every `v`. -/
structure ListColoring (G : SimpleGraph V₂) (L : V₂ → Set (Fin 4)) where
  toColoring : G.Coloring (Fin 4)
  mem_list : ∀ v, toColoring v ∈ L v

/-- `G` is list-colorable from `L` if a `ListColoring` exists. -/
def ListColorable (G : SimpleGraph V₂) (L : V₂ → Set (Fin 4)) : Prop :=
  Nonempty (ListColoring G L)

/-! ### The forbidden / allowed color sets `F(v)` and `L(v)`. -/

/-- Forbidden colors at `v ∈ V(H_2)`: the set of `c_1`-colors of
    `H_1`-endpoints of bridges into `v`. -/
def forbiddenColors {H₁ : SimpleGraph V₁} (c₁ : H₁.Coloring (Fin 4))
    (B : Set (V₁ × V₂)) (v : V₂) : Set (Fin 4) :=
  {x | ∃ u : V₁, (u, v) ∈ B ∧ c₁ u = x}

/-- Allowed colors at `v ∈ V(H_2)`: the complement of `forbiddenColors`. -/
def allowedColors {H₁ : SimpleGraph V₁} (c₁ : H₁.Coloring (Fin 4))
    (B : Set (V₁ × V₂)) (v : V₂) : Set (Fin 4) :=
  (forbiddenColors c₁ B v)ᶜ

@[simp]
lemma mem_allowedColors {H₁ : SimpleGraph V₁} (c₁ : H₁.Coloring (Fin 4))
    (B : Set (V₁ × V₂)) (v : V₂) (x : Fin 4) :
    x ∈ allowedColors c₁ B v ↔ ∀ u : V₁, (u, v) ∈ B → c₁ u ≠ x := by
  unfold allowedColors forbiddenColors
  simp only [Set.mem_compl_iff, Set.mem_setOf_eq, not_exists, not_and]

/-! ### Bridge-disagreement <-> list-coloring (the bookkeeping lemma).

    Given a fixed `c_1`, a coloring `c_2` of `H_2` satisfies the L21
    bridge non-collision condition iff `c_2 v ∈ L(v)` for every `v`.
    This is purely set-theoretic. -/

lemma noncollision_iff_list_membership {H₁ : SimpleGraph V₁}
    {H₂ : SimpleGraph V₂} (c₁ : H₁.Coloring (Fin 4))
    (c₂ : H₂.Coloring (Fin 4)) (B : Set (V₁ × V₂)) :
    (∀ p ∈ B, c₁ p.1 ≠ c₂ p.2) ↔ ∀ v, c₂ v ∈ allowedColors c₁ B v := by
  constructor
  · intro h v
    rw [mem_allowedColors]
    intro u hub hcol
    exact h (u, v) hub hcol
  · intro h ⟨u, v⟩ hub
    have := (mem_allowedColors c₁ B v (c₂ v)).mp (h v)
    exact this u hub

/-! ### The L22 list-coloring theorem (chi <= 4 form). -/

/-- **L22 list-coloring theorem (chi <= 4 form)**.

    The combined graph `bridgeGraph H_1 H_2 B` is 4-colorable iff there
    exists a proper 4-coloring `c_1` of `H_1` for which `H_2` admits a
    list-coloring from `L_{c_1}` (the lists `[4] \ F(v)`).

    This is the EXACT reformulation of L21 in list-coloring language. -/
theorem bridgeGraph_colorable_four_iff_list (H₁ : SimpleGraph V₁)
    (H₂ : SimpleGraph V₂) (B : Set (V₁ × V₂)) :
    (bridgeGraph H₁ H₂ B).Colorable 4 ↔
      ∃ c₁ : H₁.Coloring (Fin 4),
        ListColorable H₂ (allowedColors c₁ B) := by
  rw [bridgeGraph_colorable_four_iff]
  constructor
  · rintro ⟨c₁, c₂, hB⟩
    refine ⟨c₁, ?_⟩
    exact ⟨c₂, (noncollision_iff_list_membership c₁ c₂ B).mp hB⟩
  · rintro ⟨c₁, ⟨c₂, hmem⟩⟩
    refine ⟨c₁, c₂, ?_⟩
    exact (noncollision_iff_list_membership c₁ c₂ B).mpr hmem

/-- **L22 list-coloring theorem (chi >= 5 form)**.

    The combined graph fails to be 4-colorable (so `chi >= 5`) iff for
    every proper 4-coloring `c_1` of `H_1`, `H_2` is NOT list-colorable
    from `L_{c_1}`. -/
theorem bridgeGraph_not_colorable_four_iff_list (H₁ : SimpleGraph V₁)
    (H₂ : SimpleGraph V₂) (B : Set (V₁ × V₂)) :
    ¬ (bridgeGraph H₁ H₂ B).Colorable 4 ↔
      ∀ c₁ : H₁.Coloring (Fin 4),
        ¬ ListColorable H₂ (allowedColors c₁ B) := by
  rw [bridgeGraph_colorable_four_iff_list]
  push_neg
  rfl

/-- **L22 list-coloring corollary: a single bad `c_1` is enough for chi >= 5.**

    If there is some `c_1` such that `H_2` has no list-coloring from
    `L_{c_1}`, AND this holds for every `c_1` (the universal condition
    of L22), then the combined graph has `chi >= 5`. -/
theorem bridgeGraph_five_chromatic_of_universal_list_uncolorable
    (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂) (B : Set (V₁ × V₂))
    (huniv : ∀ c₁ : H₁.Coloring (Fin 4),
        ¬ ListColorable H₂ (allowedColors c₁ B)) :
    ¬ (bridgeGraph H₁ H₂ B).Colorable 4 :=
  (bridgeGraph_not_colorable_four_iff_list H₁ H₂ B).mpr huniv

/-! ### Connection between L21 and L22.

    The two theorems are EXACTLY equivalent. The list-coloring form is
    just `noncollision_iff_list_membership` applied inside the existential
    of L21. We package this as a convenience lemma. -/

/-- L21 and L22 are equivalent: the L21 covering condition (every coloring
    pair is hit by some bridge) is the same as the L22 universal-list-
    uncolorable condition. -/
theorem L21_iff_L22 (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) :
    (∀ (c₁ : H₁.Coloring (Fin 4)) (c₂ : H₂.Coloring (Fin 4)),
        ∃ p ∈ B, c₁ p.1 = c₂ p.2) ↔
    (∀ c₁ : H₁.Coloring (Fin 4),
        ¬ ListColorable H₂ (allowedColors c₁ B)) := by
  rw [← bridgeGraph_not_colorable_four_iff,
      bridgeGraph_not_colorable_four_iff_list]

end HadwigerNelson
