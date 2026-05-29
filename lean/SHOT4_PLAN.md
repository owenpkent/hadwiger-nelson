# Shot 4: Lean formalization of chi(R^2) >= 5 (de Grey 2018) -- scoping

Status: GROUNDWORK landed (2026-05-29). The reusable logical skeleton is
proved and compiles green (zero `sorry`, no new axioms). The two genuinely
hard pieces (the SAT certificate and the 500+-point embedding) are scoped
below with effort estimates and a milestone breakdown.

## What is already done (Deliverable 1)

`lean/HadwigerNelson/DeGreyLowerBound.lean` proves the BRIDGE THEOREM: the
general composition step that converts a non-4-colorable plane-realized graph
into the lower bound `5 <= chi(R^2)`. It is the chi >= 5 analog of
`MoserBridge.four_le_chromaticNumberOfPlane`.

Reduction achieved (the key theorem):

```
theorem five_le_chromaticNumberOfPlane_of_hom {V : Type u}
    {G : SimpleGraph V} (phi : G →g planeUnitDistanceGraph)
    (h4 : ¬ G.Colorable 4) :
    5 ≤ chromaticNumberOfPlane
```

and the coordinate-packaged convenience corollary

```
theorem five_le_chromaticNumberOfPlane_of_coords {V : Type u}
    (G : SimpleGraph V) (coords : V → EuclideanPlane)
    (hdist : ∀ {a b : V}, G.Adj a b → dist (coords a) (coords b) = 1)
    (h4 : ¬ G.Colorable 4) :
    5 ≤ chromaticNumberOfPlane
```

So `chi(R^2) >= 5` is now reduced to supplying, for some concrete finite
graph `G`:

1. `coords : V -> R^2` with a proof that every edge has Euclidean distance 1
   (the EMBEDDING piece), and
2. `¬ G.Colorable 4` (the SAT-CERTIFICATE piece).

Mathlib lemmas used: `Coloring.comp` (a `Coloring` is a hom into the complete
graph, so `c.comp phi` pulls back), `chromaticNumber_le_iff_colorable`, and
`Order.add_one_le_of_lt` for the `ENat` step `4 < x -> 5 <= x`.

Everything below is what remains.

## Piece A: the non-4-colorability SAT certificate

### Why native_decide cannot do it

`¬ G.Colorable 4` unfolds to: no function `V -> Fin 4` is a proper coloring.
For the Moser spindle (`Fin 7`) we discharged the analogous `¬ Colorable 3`
by `native_decide` over `3^7 = 2187` functions. That is trivial.

For the smallest known 5-chromatic UDG the search space is `4^N` with
`N >= 509`:

- Polymath 510:  `4^510  ~ 10^307`
- Heule G7 553:  `4^553  ~ 10^333`

`native_decide` would enumerate (a smartened version of) this space in
compiled code. Even with the standard "fix vertex 0, propagate" pruning the
decision is a genuine SAT instance: the published CNFs have ~2000 variables
and ~14000 clauses (`sources/cnp-sat/cnf/517-4.cnf` is `p cnf 2068 13935`).
Brute force is hopeless and `native_decide` has no clause-learning, so it
is not a path. (It would also move the entire decision into the trusted
compiled-code oracle, which is exactly the soundness surface we want to
shrink, not grow.)

### The LRAT/DRAT-checker route (the real path)

The de Grey / Heule pipeline proves `¬ 4-colorable` by running a CDCL solver
(cadical/kissat) on the CNF and emitting a DRAT (or the more checkable LRAT)
UNSAT certificate. A *verified* checker re-derives the empty clause from the
certificate by unit propagation, and if the checker itself is proved correct
in Lean, the kernel accepts `UNSAT` without trusting the solver.

What exists as of 2026-05:

- **LeanSAT / `lean-sat` (the bv_decide backend).** Lean core now ships a
  verified LRAT checker used by the `bv_decide` tactic (originally for
  bitvector goals). It parses an LRAT proof and checks it against a CNF, with
  a Lean-level soundness theorem: if the checker accepts, the CNF is
  unsatisfiable. This is the most mature, in-toolchain option and is the
  recommended target. The work is to (i) emit our coloring CNF in the exact
  variable convention `bv_decide`'s checker expects, (ii) produce an LRAT
  proof (cadical `--lrat=true`, or drat-trim / `lrat-check` to elaborate a
  DRAT into LRAT), and (iii) bridge the checker's `Unsatisfiable cnf`
  conclusion to our `¬ G.Colorable 4`.

- **Heule's `cake_lpr` (verified in CakeML/HOL).** Industrial-strength LRAT
  checker with an end-to-end correctness proof, used to certify the original
  de Grey result and the Pythagorean-triples / Schur-number proofs. It is NOT
  Lean, so it would be an *external* trusted step unless re-ported; useful as
  an independent cross-check of the certificate but not a Lean kernel proof.

- **A minimal hand-rolled LRAT checker in Lean.** ~500-1500 lines: parse
  LRAT, maintain a clause database, replay RUP/RAT steps, prove the
  unit-propagation soundness lemma. Feasible but redundant given LeanSAT.

Recommended: target the in-toolchain LeanSAT LRAT checker. The toolchain here
is Lean 4.13.0 + Mathlib v4.13.0; confirm the LRAT-checker module is present
at that version (it landed in `Std`/`Lean` around late 2024) or bump the pin.

### Bridging the checker output to `¬ G.Colorable 4`

The checker proves `Unsatisfiable phi` for a propositional CNF `phi`. We need
`¬ G.Colorable 4`. The connecting lemma chain:

1. Define the coloring CNF `phi_G` with boolean variables `x_{v,c}` for
   `v : V`, `c : Fin 4`, and clauses: at-least-one `(x_{v,0} ∨ ... ∨ x_{v,3})`
   per vertex; edge clauses `(¬x_{u,c} ∨ ¬x_{v,c})` per edge `(u,v)` and color
   `c`. (At-most-one per vertex is implied by 4 colors + edges, or add it.)
2. Prove `G.Colorable 4 ↔ Satisfiable phi_G` (a proper coloring is a
   satisfying assignment and vice versa). This is a finite, structural lemma
   provable once, generically, for any finite graph with a decidable
   adjacency. ~100-200 lines.
3. Then `Unsatisfiable phi_G` (from the checker) gives `¬ Satisfiable phi_G`,
   hence `¬ G.Colorable 4`, which feeds `five_le_chromaticNumberOfPlane_of_hom`.

The CNF emitted by the checker must be the SAME `phi_G` (same variable
numbering) that step 2 reasons about; getting this reflection-faithful is the
fiddly part. The published `sources/cnp-sat/cnf/553-4.cnf` uses the
`x_{v,c} = 4*(v-1)+c` convention; either match it or regenerate from the edge
list inside Lean so the convention is definitionally ours.

## Piece B: the embedding (G ->g planeUnitDistanceGraph)

`five_le_chromaticNumberOfPlane_of_coords` needs `coords : V -> R^2` and a
proof that every edge maps to a unit-distance pair. `MoserBridge` did this for
7 points / 11 edges: each edge is one `nlinarith` after substituting the
square identities `(sqrt 3)^2 = 3`, `(sqrt 11)^2 = 11`, and `sqrt 33 =
sqrt 3 * sqrt 11`.

For a 5-chromatic UDG the data is in `sources/cnp-sat/vtx/` and `edge/`:

- Smallest with a full certificate set (vtx + edge + cnf) here: **517**
  (`517.vtx`, `517.edge`, `cnf/517-4.cnf` = `p cnf 2068 13935`). 510 has
  vtx+edge but no CNF in this tree; 553 (Heule G7) is the canonical Heule
  benchmark and the one his `cake_lpr` certificate targets.
- Field: the coordinates live in `Q(sqrt 3, sqrt 5, sqrt 11)` (see the
  Singular check `sources/cnp-sat/check/553.singular`: ring vars `r3 = 1/sqrt3,
  s3, s5, s11` with the ideal `s3*r3-1, s11^2-11, s5^2-5, s3^2-3`).
- Edges: ~2500 (517 has 2504; 553 has ~2722).

Effort estimate for the embedding:

- The 2500 per-edge unit-distance proofs CANNOT be hand-written. They must be
  generated. The good news: the distance-squared of each edge is a polynomial
  in `sqrt 3, sqrt 5, sqrt 11` that equals 1, and the Heule/Ritirc Singular
  scripts already PROVE this by Groebner-basis ideal membership over exactly
  that field. So the math is certified externally; the task is to reproduce it
  inside the Lean kernel.
- In Lean, each edge reduces (after `EuclideanSpace.dist_eq`, `Fin.sum_univ_two`,
  `sq_abs`) to a polynomial identity in `s3, s5, s11` modulo the ideal
  `{s3^2=3, s5^2=5, s11^2=11}`. `nlinarith`/`polyrith` with the three square
  hints should close each one, but 2500 invocations is heavy and `polyrith`
  is slow/network-dependent. Better: write a `decide`-style normal form, or a
  custom tactic that rewrites all squares and calls `ring_nf` + `linear_combination`
  with precomputed coefficients exported from Singular.
- Most robust plan: have Singular (already in the repo's check pipeline) emit,
  for each edge, the `linear_combination` certificate (the ideal-membership
  cofactors), then a code-generated Lean file with one
  `linear_combination ...` per edge. This is mechanical once the cofactor
  export works. Estimate: 1-2 weeks to build the generator + tactic, then the
  generated file may be large (~2500 lemmas) and slow to compile (hours), so
  it likely needs to be split into modules and possibly use `native_decide`
  on a reflected polynomial-equality decision over the number field (cleaner
  but requires formalizing the field `Q(sqrt3,sqrt5,sqrt11)` as a Lean type
  with decidable equality, ~2-3 weeks).
- The `coords` map itself: parse `*.vtx` (Mathematica `{a, b}` with `Sqrt[..]`)
  into Lean `EuclideanPlane` literals. Mechanical, ~1-2 days including a
  generator.

The adjacency-preservation dispatcher (`map_rel'`) that `MoserBridge` wrote by
hand (a 49-way `fin_cases`) does NOT scale to `Fin 517`. Instead prove it
generically: if `coords` is defined by table lookup and `G.Adj` is the
edge-list membership relation, then `G.Adj a b -> dist = 1` follows by
`decide` on which edge plus the corresponding generated distance lemma. This
wants the edge relation to be `DecidableRel` (as `moserSpindle` is) and a
lookup from edge-index to distance-lemma. Plan: index the generated lemmas by
edge and write one `fin_cases`-free dispatcher that does `interval_cases`/
list-membership. ~1 week.

## Milestone breakdown (realistic, ~6 months total)

| # | Milestone | Effort | Risk |
|---|-----------|--------|------|
| M0 | Bridge theorem (`DeGreyLowerBound.lean`) | DONE | none |
| M1 | Generic `G.Colorable 4 ↔ Satisfiable phi_G` reflection lemma, fixing the CNF variable convention | 2-3 wk | med (faithful encoding) |
| M2 | Wire the LeanSAT LRAT checker: confirm it is in the 4.13 toolchain or bump pin; emit LRAT for `553-4.cnf` (cadical `--lrat`), check it accepts | 3-4 wk | med (toolchain availability) |
| M3 | Compose M1+M2 into `¬ moserG553.Colorable 4` as a kernel theorem | 2 wk | low |
| M4 | Number-field substrate: `Q(sqrt3,sqrt5,sqrt11)` coords parser + the per-edge unit-distance generator (Singular cofactor export -> Lean `linear_combination`) | 4-6 wk | high (scale, compile time) |
| M5 | Generic embedding `moserG553 →g planeUnitDistanceGraph` from the generated distance lemmas + a scalable `map_rel'` dispatcher | 3-4 wk | med |
| M6 | Final: `five_le_chromaticNumberOfPlane_of_coords` applied -> `5 <= chi(R^2)`; full `lake build` green, `#print axioms` clean (only Mathlib + the LRAT checker's trust base) | 1 wk | low |
| M7 | Independent VERIFIER re-runs (multi-solver SAT agreement on 553-4.cnf with cadical + kissat; cross-check LRAT with `cake_lpr`) | 1 wk | low |

Total: roughly 5-6 months of focused work, dominated by M4 (the 2500-edge
exact-arithmetic embedding) and M2 (LRAT-checker integration). M1 and the
bridge (M0) are the parts that are cheap and now done.

## Smallest available certificated 5-chromatic UDG (summary)

- **517** is the smallest instance here with vtx + edge + 4-coloring CNF
  (`cnf/517-4.cnf`, 2068 vars / 13935 clauses). Use it if size is the only
  criterion.
- **553 (Heule G7)** is the recommended target: it is the published benchmark
  with an externally verified `cake_lpr` LRAT/DRAT certificate, giving an
  independent cross-check for M7, and its exact-distance proof is already in
  the repo's Singular pipeline (`check/553.singular`, field
  `Q(sqrt3,sqrt5,sqrt11)`).
- **510 (Polymath)** is the smallest known in the literature but lacks a CNF
  in this tree; it is `de Grey 1585 translated and field-restricted`
  (LEARNINGS L19), so it carries no independent certification advantage.

## What this groundwork proves / what remains

Proved (kernel, no new axioms): IF a finite graph is realized in the plane by
unit-distance coordinates AND is not 4-colorable, THEN `5 <= chi(R^2)`. The
chi >= 5 plane lower bound is now a one-line corollary of two finite,
checkable certificates.

Remains: the two certificates themselves (Piece A = LRAT-checked
non-4-colorability; Piece B = 2500-edge exact-arithmetic embedding). Both are
mechanical-but-large; neither is mathematically open. The honest estimate is
5-6 months, with the bulk in the embedding generator and the LRAT-checker
integration.
