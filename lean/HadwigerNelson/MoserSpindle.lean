/-
The Moser spindle (1961): a 7-vertex unit-distance graph with χ = 4.

VERIFIER target HN-2: prove `(moserSpindle).chromaticNumber = 4`.

The seven vertices live in `ℚ(√3, √11)`, but for the Lean formalization we
work with explicit real (or `EuclideanSpace`) coordinates and verify edge
distances directly. The graph is small enough that the chromatic number can
be settled by:

  - exhibiting an explicit 4-coloring (gives `≤ 4`);
  - exhibiting an odd cycle / triangle structure forcing non-3-colorability
    (gives `≥ 4`). Specifically, the spindle contains two K₄-free rhombi
    glued at a vertex with the property that any 3-coloring forces a
    monochromatic edge at the gluing point.

The proof is mostly mechanical once the seven vertices are pinned down and
the eleven edges are computed by hand or by sympy and transferred here.
-/

import HadwigerNelson.Basic

namespace HadwigerNelson

open SimpleGraph

/-! ### The seven Moser spindle vertices.

    Standard construction: two unit rhombi `ABCD` and `AEFG` sharing vertex
    `A`, then `B` and `G` (the far vertices) brought to exact distance 1 by
    rotating one rhombus by the angle `arccos(5/6)`. The resulting seven
    points have pairwise distances either 1 or in the algebraic-irrational
    range `(0, 2)` with eleven unit-distance pairs.

    Coordinates worked out in `experiments/_shared/unit_distance_graph.py`
    (function `moser_spindle`). The Lean version below mirrors those exact
    symbolic values; the `Real` cast loses no information for distance
    comparisons after squaring. -/

-- TODO HN-2.1: define the seven vertices as `EuclideanPlane`-valued constants
-- using exact algebraic coordinates (Real.sqrt 3, Real.sqrt 11). Verify
-- distance-squared equalities by `field_simp` + `Real.sq_sqrt`.
-- TODO HN-2.2: define `moserSpindle : SimpleGraph (Fin 7)` as the abstract
-- 11-edge graph, with a homomorphism into `planeUnitDistanceGraph`.
-- TODO HN-2.3: prove `(moserSpindle).chromaticNumber = 4` by exhibiting a
-- 4-coloring (`decide` after `Fintype` instances) and ruling out 3-coloring
-- via `Decidable` on `SimpleGraph.Colorable 3`.

/-- Placeholder: the abstract Moser spindle as an unlabeled graph on `Fin 7`.

    Currently the empty graph on 7 vertices (`⊥` in the SimpleGraph lattice).
    VERIFIER target HN-2 fills this in with the actual 11-edge structure. -/
def moserSpindle : SimpleGraph (Fin 7) := (⊥ : SimpleGraph (Fin 7))

/-- Placeholder statement: the Moser spindle is 4-chromatic. -/
def MoserSpindleIsFourChromatic : Prop :=
  moserSpindle.chromaticNumber = 4

end HadwigerNelson
