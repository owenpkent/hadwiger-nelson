# Verification

What the Lean artifact under `lean/` actually establishes, what it trusts, and
how to check it independently. Machine-readable summary in the repo-root
`formalization.yaml`.

## Trust base is not uniform

Four of the five headline results use only Lean's three standard axioms. One
does not.

| Result | ID | Axioms |
|---|---|---|
| `four_le_chromaticNumberOfPlane` | HN-2d | standard three **plus `Lean.ofReduceBool`** |
| `bridgeGraph_five_chromatic_of_covering` | HN-L21 | standard three |
| `L21_iff_L22` | HN-L22 | standard three |
| `tripleGraph_six_chromatic_of_universal_residual_uncolorable` | HN-L24 | standard three |
| `five_le_chromaticNumberOfPlane_of_hom` | HN-4 | standard three |

The `chi >= 4` result is the one with the larger base. The chain is
`four_le_chromaticNumberOfPlane` -> `moserSpindle_chromaticNumber` ->
`moserSpindle_not_colorable_three`, and the last is proved by `native_decide`
at `HadwigerNelson/MoserSpindle.lean:76`, which trusts the compiled decision
procedure as a separate oracle rather than the kernel.

This is disclosed in the file's own docstring and the README's axiom claim is
correctly scoped to `DeGreyLowerBound.lean`, so nothing here is misstated. The
point is that the difference should be visible without reading the source.

**Worth closing.** The search is `Fin 7 -> Fin 3`, only 2187 candidates. The
docstring says kernel `decide` blows the stack, which is a statement about the
`Decidable` instance's reduction behaviour rather than about the problem size.
A `Finset.univ.filter` formulation, or `List.all` over an explicit enumeration
with `decide` on the resulting boolean, would very likely fit the kernel and
bring HN-2d down to the standard three. Until then, `chi >= 4` is Lean-verified
in a weaker sense than the reductions around it.

## What is proved, and what is not

`chi(R^2) >= 4` is unconditional. Everything else is a reduction.

In particular HN-4 is **not** a proof of `chi >= 5`. It says: given a graph with
a homomorphism into `planeUnitDistanceGraph` that is not 4-colorable, you get
`chi(R^2) >= 5`. No such graph is supplied. The two missing pieces, an
LRAT-checked non-4-colorability certificate and a >500-point embedding, are
scoped in `SHOT4_PLAN.md`.

Similarly HN-L24 lifts to `chi >= 6` conditionally on a list-uncolorability
hypothesis that no concrete instance discharges.

## Statement provenance

Every definition here is this project's own, including `planeUnitDistanceGraph`.
That is the weakest link in any formalization: a proof of the wrong statement
verifies just as cleanly as a proof of the right one.

Google DeepMind's Formal Conjectures carries a third-party statement,
`FormalConjectures/Wikipedia/HadwigerNelson.lean`, plus supporting
`UnitDistancePlaneGraph.lean`. It has not been diffed against this project's
definitions. Doing that diff, and where possible restating results against the
upstream definitions, would buy the independence guarantee that self-authored
statements cannot. It is the single highest-value verification task outstanding.

## Reproducing

The toolchain is pinned to `leanprover/lean4:v4.13.0` with mathlib at
`v4.13.0` (`d7317655e2826dc1f1de9a0c138db2775c4bb841`). Neither `.lake` nor a
green build exists on the current machine; the `1864/1864` figure in
`lean/README.md` is a historical note from a Windows box, dated 2026-05-25.

```sh
cd lean
lake exe cache get
lake build
```

Then confirm the trust base directly, which is the check that matters:

```lean
#print axioms HadwigerNelson.four_le_chromaticNumberOfPlane
#print axioms HadwigerNelson.five_le_chromaticNumberOfPlane_of_hom
```

## Independent checking

Once a result is complete enough to publish, it can be checked the way an
outside party would: a challenge file stating the theorem, a solution module
that never imports it, and Comparator plus an external kernel. The harness is
installed at `~/.local/share/lean-verify/` and the workflow is captured in the
`lean-verify` skill.

Note that a Comparator run would currently **reject** HN-2d against the usual
`permitted_axioms` list, since `Lean.ofReduceBool` is not among the standard
three. That is the tooling correctly reporting the situation above.
