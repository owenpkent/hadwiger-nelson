/-
The Moser spindle (1961): a 7-vertex unit-distance graph with χ = 4.

VERIFIER target HN-2: prove `moserSpindle.chromaticNumber = 4`.

Decomposition:
  HN-2a: `moserSpindle.Colorable 4` (upper bound; immediate from a witness coloring).
  HN-2b: `¬ moserSpindle.Colorable 3` (lower bound; harder, needs case analysis
         over 3^7 = 2187 candidate colorings or a structural argument).
  HN-2c: bridge to `planeUnitDistanceGraph` via an injective graph
         homomorphism using the explicit 7 plane coordinates.

This file lands HN-2a. HN-2b and HN-2c are TODO.

Vertex labeling: 0 = A, 1 = B, 2 = C, 3 = D, 4 = B', 5 = C', 6 = D'.
Edges (11 total): the five unit edges of each unit rhombus plus the connecting
edge DD'. See `docs/01_undergraduate/moser_spindle.md` for the geometry.

The 4-coloring witness comes from `experiments/combinatorial/e1a_moser_spindle.py`
(cadical195 returned `[0, 1, 2, 0, 1, 2, 3]`). The e1a experiment also
SAT-verified that no 3-coloring exists; HN-2b is the formal counterpart.
-/

import HadwigerNelson.Basic

namespace HadwigerNelson

open SimpleGraph

/-- Boolean adjacency table for the Moser spindle. All 22 ordered pairs (11
    unordered edges, each direction) are listed explicitly so the function
    reduces to `true`/`false` by pattern matching, giving decidability of
    `moserSpindle.Adj` for free. -/
def moserSpindleAdjBool : Fin 7 → Fin 7 → Bool
  | 0, 1 | 1, 0 | 0, 2 | 2, 0 | 1, 2 | 2, 1 | 1, 3 | 3, 1 | 2, 3 | 3, 2
  | 0, 4 | 4, 0 | 0, 5 | 5, 0 | 4, 5 | 5, 4 | 4, 6 | 6, 4 | 5, 6 | 6, 5
  | 3, 6 | 6, 3 => true
  | _, _ => false

/-- The Moser spindle as an abstract simple graph on `Fin 7`. -/
def moserSpindle : SimpleGraph (Fin 7) where
  Adj i j := moserSpindleAdjBool i j = true
  symm := by
    intro i j h
    fin_cases i <;> fin_cases j <;> revert h <;> decide
  loopless := by
    intro i h
    fin_cases i <;> revert h <;> decide

instance : DecidableRel moserSpindle.Adj := fun i j =>
  inferInstanceAs (Decidable (moserSpindleAdjBool i j = true))

/-- The explicit 4-coloring of the Moser spindle, taken from the e1a SAT witness.
    Cadical195 returned this assignment; the verifier checks every edge is
    bichromatic. -/
def moserSpindle4ColorFn : Fin 7 → Fin 4 :=
  ![0, 1, 2, 0, 1, 2, 3]

/-- The 4-coloring as a `SimpleGraph.Coloring`. The validity proof enumerates
    all adjacent pairs via `decide` after unfolding `fromEdgeSet`. -/
def moserSpindle4Coloring : moserSpindle.Coloring (Fin 4) :=
  Coloring.mk moserSpindle4ColorFn (by decide)

/-- HN-2a: the Moser spindle is 4-colorable. Immediate from the e1a witness. -/
theorem moserSpindle_colorable_four : moserSpindle.Colorable 4 :=
  ⟨moserSpindle4Coloring⟩

/-- HN-2b: the Moser spindle is not 3-colorable. Proof by `native_decide`
    over the $3^7 = 2187$ candidate functions `Fin 7 → Fin 3`. Kernel `decide`
    blows the stack on this many cases; `native_decide` compiles the decision
    procedure to native code and is trusted as a (different) computational
    oracle in the Lean kernel. -/
theorem moserSpindle_not_colorable_three : ¬ moserSpindle.Colorable 3 := by
  rintro ⟨C⟩
  have h : ¬ ∃ f : Fin 7 → Fin 3, ∀ i j, moserSpindle.Adj i j → f i ≠ f j := by
    native_decide
  exact h ⟨C, fun _ _ adj => C.valid adj⟩

/-- HN-2 target: `chi(Moser spindle) = 4`. Combining the two halves into the
    `chromaticNumber = 4` form involves Mathlib's `iInf` / `sInf` plumbing on
    `ℕ∞`; tracked separately. The mathematical content lives in the two
    theorems above. -/
def MoserSpindleIsFourChromatic : Prop :=
  moserSpindle.chromaticNumber = 4

end HadwigerNelson
