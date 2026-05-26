/-
HN-2d: bridge the abstract Moser spindle `Fin 7` graph to the Euclidean unit-
distance graph on the plane.

The abstract Moser spindle has chromatic number 4 (`moserSpindle_chromaticNumber`).
This file constructs a graph homomorphism
`moserSpindle →g planeUnitDistanceGraph` which transfers the lower bound:
`4 ≤ chromaticNumberOfPlane`.

Vertex coordinates (standard Moser construction, rotation angle arccos(5/6)):
  0 = A  = (0, 0)
  1 = B  = (1, 0)
  2 = C  = (1/2, √3/2)
  3 = D  = (3/2, √3/2)
  4 = B' = (5/6, √11/6)
  5 = C' = ((5 − √33)/12, (√11 + 5√3)/12)
  6 = D' = ((15 − √33)/12, (3√11 + 5√3)/12)

For all 11 unit edges in `moserSpindle`, the corresponding Euclidean distance
equals 1. The proofs split into:
  - rational-only edges (AB, CD): trivial.
  - single-sqrt edges (AC, BC, BD, AB', C'D'): one `Real.sq_sqrt` application.
  - cross-sqrt edges with √33 cancellation (AC', B'C', B'D', DD'): require the
    identity √33 = √3·√11 to make the cross terms cancel in the algebra.
-/

import HadwigerNelson.Basic
import HadwigerNelson.MoserSpindle

namespace HadwigerNelson

open Real

/-- The seven Moser spindle vertices as points in the Euclidean plane.
    Coordinates use `Real.sqrt 3`, `Real.sqrt 11`, `Real.sqrt 33`. -/
noncomputable def moserVertex : Fin 7 → EuclideanPlane
  | 0 => ![0, 0]
  | 1 => ![1, 0]
  | 2 => ![1 / 2, sqrt 3 / 2]
  | 3 => ![3 / 2, sqrt 3 / 2]
  | 4 => ![5 / 6, sqrt 11 / 6]
  | 5 => ![(5 - sqrt 33) / 12, (sqrt 11 + 5 * sqrt 3) / 12]
  | 6 => ![(15 - sqrt 33) / 12, (3 * sqrt 11 + 5 * sqrt 3) / 12]

/-! ### Auxiliary lemmas for unwrapping `EuclideanPlane` distance to plane algebra. -/

private lemma sqrt_three_sq : sqrt 3 ^ 2 = 3 := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 3)
private lemma sqrt_eleven_sq : sqrt 11 ^ 2 = 11 := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 11)
private lemma sqrt_thirtythree_eq : sqrt 33 = sqrt 3 * sqrt 11 := by
  rw [show (33 : ℝ) = 3 * 11 from by norm_num]
  exact Real.sqrt_mul (by norm_num : (0:ℝ) ≤ 3) _

/-- Boilerplate-eliminator: `dist x y = 1` for `EuclideanPlane` reduces to
    `(x 0 - y 0)² + (x 1 - y 1)² = 1`. -/
private lemma plane_dist_eq_one_of_sq_eq_one {x y : EuclideanPlane}
    (h : (x 0 - y 0) ^ 2 + (x 1 - y 1) ^ 2 = 1) : dist x y = 1 := by
  rw [EuclideanSpace.dist_eq, Fin.sum_univ_two, Real.dist_eq, Real.dist_eq, sq_abs, sq_abs, h]
  exact Real.sqrt_one

/-! ### The 11 unit-distance edges.

    Each proof unfolds `moserVertex` to expose explicit coordinates, then
    substitutes `√33 = √3 · √11` (where present), then closes via `nlinarith`
    with the square identities `(√3)² = 3` and `(√11)² = 11`. -/

/-- Common tactic: unfold `moserVertex`, expose coordinates, replace `√33`,
    and close the polynomial equation with `nlinarith` and the square
    identities. The `sq_nonneg` hints help `nlinarith` see the cross-term
    cancellations involving `√3 · √11`. -/
local syntax "moser_edge" : tactic
macro_rules
  | `(tactic| moser_edge) =>
    `(tactic|(
        apply plane_dist_eq_one_of_sq_eq_one
        simp only [moserVertex, Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons]
        try rw [sqrt_thirtythree_eq]
        have h3 := sqrt_three_sq
        have h11 := sqrt_eleven_sq
        nlinarith [h3, h11, sq_nonneg (sqrt 3 + sqrt 11), sq_nonneg (sqrt 3 - sqrt 11),
                   sq_nonneg (sqrt 3 * sqrt 11), Real.sqrt_nonneg 3, Real.sqrt_nonneg 11]))

lemma dist_moserVertex_0_1 : dist (moserVertex 0) (moserVertex 1) = 1 := by moser_edge

lemma dist_moserVertex_0_2 : dist (moserVertex 0) (moserVertex 2) = 1 := by moser_edge

lemma dist_moserVertex_1_2 : dist (moserVertex 1) (moserVertex 2) = 1 := by moser_edge

lemma dist_moserVertex_1_3 : dist (moserVertex 1) (moserVertex 3) = 1 := by moser_edge

lemma dist_moserVertex_2_3 : dist (moserVertex 2) (moserVertex 3) = 1 := by moser_edge

lemma dist_moserVertex_0_4 : dist (moserVertex 0) (moserVertex 4) = 1 := by moser_edge

lemma dist_moserVertex_4_5 : dist (moserVertex 4) (moserVertex 5) = 1 := by moser_edge

lemma dist_moserVertex_4_6 : dist (moserVertex 4) (moserVertex 6) = 1 := by moser_edge

lemma dist_moserVertex_5_6 : dist (moserVertex 5) (moserVertex 6) = 1 := by moser_edge

lemma dist_moserVertex_0_5 : dist (moserVertex 0) (moserVertex 5) = 1 := by moser_edge

lemma dist_moserVertex_3_6 : dist (moserVertex 3) (moserVertex 6) = 1 := by moser_edge

/-! ### The graph homomorphism `moserSpindle →g planeUnitDistanceGraph`.

    The vertex map is `moserVertex`. The adjacency-preservation proof
    enumerates the 49 (a, b) pairs via `fin_cases`. For non-edges, `hab` is
    `false = true` and the case is refuted by `decide`. For each of the 22
    edge orderings, dispatch to one of the 11 named distance lemmas (with
    `dist_comm` for the reverse direction). All heavy `nlinarith` work
    already happened in those lemmas, so this dispatcher only does cheap
    term-level applications. -/

set_option maxHeartbeats 1000000 in
private lemma dist_of_moserAdj {a b : Fin 7} (hab : moserSpindle.Adj a b) :
    dist (moserVertex a) (moserVertex b) = 1 := by
  fin_cases a <;> fin_cases b <;>
    first
    | exact absurd hab (by decide)
    | exact dist_moserVertex_0_1
    | (rw [dist_comm]; exact dist_moserVertex_0_1)
    | exact dist_moserVertex_0_2
    | (rw [dist_comm]; exact dist_moserVertex_0_2)
    | exact dist_moserVertex_1_2
    | (rw [dist_comm]; exact dist_moserVertex_1_2)
    | exact dist_moserVertex_1_3
    | (rw [dist_comm]; exact dist_moserVertex_1_3)
    | exact dist_moserVertex_2_3
    | (rw [dist_comm]; exact dist_moserVertex_2_3)
    | exact dist_moserVertex_0_4
    | (rw [dist_comm]; exact dist_moserVertex_0_4)
    | exact dist_moserVertex_0_5
    | (rw [dist_comm]; exact dist_moserVertex_0_5)
    | exact dist_moserVertex_4_5
    | (rw [dist_comm]; exact dist_moserVertex_4_5)
    | exact dist_moserVertex_4_6
    | (rw [dist_comm]; exact dist_moserVertex_4_6)
    | exact dist_moserVertex_5_6
    | (rw [dist_comm]; exact dist_moserVertex_5_6)
    | exact dist_moserVertex_3_6
    | (rw [dist_comm]; exact dist_moserVertex_3_6)

/-- The graph homomorphism from the abstract Moser spindle to the Euclidean
    plane's unit-distance graph. -/
noncomputable def moserToPlane : moserSpindle →g planeUnitDistanceGraph where
  toFun := moserVertex
  map_rel' {a b} hab := by
    have hd : dist (moserVertex a) (moserVertex b) = 1 := dist_of_moserAdj hab
    refine ⟨?_, Or.inl hd⟩
    intro heq
    rw [heq, dist_self] at hd
    norm_num at hd

/-! ### Transfer the chromatic-number lower bound to the plane. -/

/-- If the plane unit-distance graph is `n`-colorable, so is the Moser spindle.
    Proof: pull back the coloring along the homomorphism `moserToPlane`. -/
private lemma moserSpindle_colorable_of_plane_colorable {n : ℕ}
    (h : planeUnitDistanceGraph.Colorable n) : moserSpindle.Colorable n :=
  ⟨h.some.comp moserToPlane⟩

/-- **HN-2d** (Moser bridge corollary): the chromatic number of the plane is
    at least 4. This is the Moser-spindle lower bound transferred via the
    homomorphism `moserToPlane`. -/
theorem four_le_chromaticNumberOfPlane : 4 ≤ chromaticNumberOfPlane := by
  have h_transfer : moserSpindle.chromaticNumber ≤ planeUnitDistanceGraph.chromaticNumber :=
    SimpleGraph.chromaticNumber_le_of_forall_imp
      (fun _ => moserSpindle_colorable_of_plane_colorable)
  rw [moserSpindle_chromaticNumber] at h_transfer
  exact h_transfer

end HadwigerNelson
