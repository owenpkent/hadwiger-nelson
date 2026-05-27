/-
Bridge graphs: two disjoint subgraphs connected by a bridge set.

This file sets up the "two halves plus bridges" construction that pervades
the chi >= 5 lineage in the Hadwiger-Nelson program (de Grey 1585, Polymath
510, the abstract Moser x Moser 14-bridge graph). See LEARNINGS.md entry L20
for the structural ubiquity of this pattern and L21 / L22 for the covering
lemma and list-coloring reformulation.

We model two graphs `H_1 : SimpleGraph V_1` and `H_2 : SimpleGraph V_2` on
DISJOINT vertex sets via the disjoint-union type `V_1 + V_2 : Type`. The
bridge set is `B : Set (V_1 x V_2)`. The combined graph is
`bridgeGraph H_1 H_2 B : SimpleGraph (V_1 + V_2)`.

Disjointness is enforced at the type level by `Sum.inl_ne_inr` rather than
by tracking a disjointness hypothesis. This is cleaner: no boundary
conditions to maintain, no chance of accidental vertex collision.

The two L21 / L22 theorems are proved in:
  - `HadwigerNelson.L21CoveringLemma`: chi(G) >= 5 iff every coloring pair
    is hit by some bridge.
  - `HadwigerNelson.L22ListColoring`: the same condition, restated as
    list-uncolorability of H_2 from lists L(v) = [4] \ F(v).
-/

import HadwigerNelson.Basic

namespace HadwigerNelson

open SimpleGraph

universe u v

variable {V₁ : Type u} {V₂ : Type v}

/-! ### Lifting `H_1` and `H_2` to the sum type. -/

/-- Lift `H_1 : SimpleGraph V_1` to `SimpleGraph (V_1 + V_2)`: an edge
    `inl a -- inl b` exactly when `H_1.Adj a b`; no edges involving `inr`. -/
def liftLeft (H₁ : SimpleGraph V₁) : SimpleGraph (V₁ ⊕ V₂) where
  Adj x y := match x, y with
    | Sum.inl a, Sum.inl b => H₁.Adj a b
    | _, _ => False
  symm := by
    rintro (a | a) (b | b) h <;> simp_all [H₁.adj_comm]
  loopless := by
    rintro (a | a) h <;> simp_all [H₁.loopless]

@[simp]
lemma liftLeft_adj_inl_inl (H₁ : SimpleGraph V₁) (a b : V₁) :
    (liftLeft (V₂ := V₂) H₁).Adj (Sum.inl a) (Sum.inl b) ↔ H₁.Adj a b := Iff.rfl

@[simp]
lemma liftLeft_adj_inl_inr (H₁ : SimpleGraph V₁) (a : V₁) (b : V₂) :
    ¬ (liftLeft (V₂ := V₂) H₁).Adj (Sum.inl a) (Sum.inr b) := by
  intro h; exact h

@[simp]
lemma liftLeft_adj_inr_inl (H₁ : SimpleGraph V₁) (a : V₂) (b : V₁) :
    ¬ (liftLeft (V₂ := V₂) H₁).Adj (Sum.inr a) (Sum.inl b) := by
  intro h; exact h

@[simp]
lemma liftLeft_adj_inr_inr (H₁ : SimpleGraph V₁) (a b : V₂) :
    ¬ (liftLeft (V₂ := V₂) H₁).Adj (Sum.inr a) (Sum.inr b) := by
  intro h; exact h

/-- Lift `H_2 : SimpleGraph V_2` to `SimpleGraph (V_1 + V_2)` symmetrically. -/
def liftRight (H₂ : SimpleGraph V₂) : SimpleGraph (V₁ ⊕ V₂) where
  Adj x y := match x, y with
    | Sum.inr a, Sum.inr b => H₂.Adj a b
    | _, _ => False
  symm := by
    rintro (a | a) (b | b) h <;> simp_all [H₂.adj_comm]
  loopless := by
    rintro (a | a) h <;> simp_all [H₂.loopless]

@[simp]
lemma liftRight_adj_inr_inr (H₂ : SimpleGraph V₂) (a b : V₂) :
    (liftRight (V₁ := V₁) H₂).Adj (Sum.inr a) (Sum.inr b) ↔ H₂.Adj a b := Iff.rfl

@[simp]
lemma liftRight_adj_inl_inl (H₂ : SimpleGraph V₂) (a b : V₁) :
    ¬ (liftRight (V₁ := V₁) H₂).Adj (Sum.inl a) (Sum.inl b) := by
  intro h; exact h

@[simp]
lemma liftRight_adj_inl_inr (H₂ : SimpleGraph V₂) (a : V₁) (b : V₂) :
    ¬ (liftRight (V₁ := V₁) H₂).Adj (Sum.inl a) (Sum.inr b) := by
  intro h; exact h

@[simp]
lemma liftRight_adj_inr_inl (H₂ : SimpleGraph V₂) (a : V₂) (b : V₁) :
    ¬ (liftRight (V₁ := V₁) H₂).Adj (Sum.inr a) (Sum.inl b) := by
  intro h; exact h

/-! ### The bridge graph itself.

    The bridge set is `B : Set (V_1 x V_2)`. The bridge graph has an edge
    `inl u -- inr v` exactly when `(u, v) in B`. It is automatically
    irreflexive and symmetric because `inl ≠ inr`. -/

/-- The graph on `V_1 + V_2` whose edges are exactly the bridges in `B`,
    from `inl u` to `inr v` for each `(u, v) in B`. -/
def bridgeSetGraph (B : Set (V₁ × V₂)) : SimpleGraph (V₁ ⊕ V₂) where
  Adj x y := match x, y with
    | Sum.inl u, Sum.inr v => (u, v) ∈ B
    | Sum.inr v, Sum.inl u => (u, v) ∈ B
    | _, _ => False
  symm := by
    rintro (a | a) (b | b) h <;> simp_all
  loopless := by
    rintro (a | a) h <;> simp_all

@[simp]
lemma bridgeSetGraph_adj_inl_inr (B : Set (V₁ × V₂)) (u : V₁) (v : V₂) :
    (bridgeSetGraph B).Adj (Sum.inl u) (Sum.inr v) ↔ (u, v) ∈ B := Iff.rfl

@[simp]
lemma bridgeSetGraph_adj_inr_inl (B : Set (V₁ × V₂)) (v : V₂) (u : V₁) :
    (bridgeSetGraph B).Adj (Sum.inr v) (Sum.inl u) ↔ (u, v) ∈ B := Iff.rfl

@[simp]
lemma bridgeSetGraph_adj_inl_inl (B : Set (V₁ × V₂)) (u u' : V₁) :
    ¬ (bridgeSetGraph B).Adj (Sum.inl u) (Sum.inl u') := by
  intro h; exact h

@[simp]
lemma bridgeSetGraph_adj_inr_inr (B : Set (V₁ × V₂)) (v v' : V₂) :
    ¬ (bridgeSetGraph B).Adj (Sum.inr v) (Sum.inr v') := by
  intro h; exact h

/-! ### The combined "two halves plus bridges" graph. -/

/-- The combined graph: `H_1` on the left, `H_2` on the right, plus
    bridges from `B`. This is the central construction of L21 / L22. -/
def bridgeGraph (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) : SimpleGraph (V₁ ⊕ V₂) :=
  liftLeft H₁ ⊔ liftRight H₂ ⊔ bridgeSetGraph B

@[simp]
lemma bridgeGraph_adj_inl_inl (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) (a b : V₁) :
    (bridgeGraph H₁ H₂ B).Adj (Sum.inl a) (Sum.inl b) ↔ H₁.Adj a b := by
  unfold bridgeGraph
  simp

@[simp]
lemma bridgeGraph_adj_inr_inr (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) (a b : V₂) :
    (bridgeGraph H₁ H₂ B).Adj (Sum.inr a) (Sum.inr b) ↔ H₂.Adj a b := by
  unfold bridgeGraph
  simp

@[simp]
lemma bridgeGraph_adj_inl_inr (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) (u : V₁) (v : V₂) :
    (bridgeGraph H₁ H₂ B).Adj (Sum.inl u) (Sum.inr v) ↔ (u, v) ∈ B := by
  unfold bridgeGraph
  simp

@[simp]
lemma bridgeGraph_adj_inr_inl (H₁ : SimpleGraph V₁) (H₂ : SimpleGraph V₂)
    (B : Set (V₁ × V₂)) (v : V₂) (u : V₁) :
    (bridgeGraph H₁ H₂ B).Adj (Sum.inr v) (Sum.inl u) ↔ (u, v) ∈ B := by
  unfold bridgeGraph
  simp

end HadwigerNelson
