# Retrodiction 2050: chi(R^2) is not absolute (Architecture 4 metatheorem)

**Mode**: BUILDER retrodiction exercise. NOT a proof. NOT a claim that any
sub-step is currently provable. Every link is tethered to a 2026 obstruction in
the state-of-play brief and is phrased so a 2026 researcher can ask "is THIS
attackable now?"

**Steered terminal form (given)**: in 2050 the Hadwiger-Nelson problem is
resolved by a metatheorem. The value of chi(R^2) depends on the choice /
measurability axioms. Under ZF + DC + (every set of reals Lebesgue measurable)
one value; under full AC another. The 2050 "solution" is a forcing / inner-model
proof that the question is not absolute.

---

## 0. The single hard constraint the retrodiction must respect

de Grey 2018 exhibits a FINITE 5-chromatic unit-distance graph. A finite point
set is Borel (discrete, hence every subset Borel and Lebesgue measurable in the
ambient R^2). Therefore chi >= 5 lifts through the ENTIRE definability hierarchy:

    chi(R^2) >= 5,  chi_B(R^2) >= 5,  chi_m(R^2) >= 5    in EVERY model of ZF+DC.

Consequence that pins the whole retrodiction: **independence cannot live at the
5 threshold.** The lower edge is nailed down by a finite, absolute witness. The
metatheorem must therefore separate the ZFC value from the Solovay value strictly
ABOVE 5. The only room is

    Solovay model (ZF+DC+LM):  chi(R^2) = 6
    ZFC (full AC):             chi(R^2) = 7

or the analogous split at {5,6}. The retrodiction below argues the {6,7} split is
the structurally forced one, because the upper bound 7 (Isbell) is an explicit AC
construction (a choice of which of finitely many hexagon-classes each boundary
point gets) and the measurable upper bound is the real bottleneck.

**This immediately resolves "which bound is the bottleneck in this world": the
UPPER bound is, specifically the MEASURABLE upper bound chi_m <= 6.** The lower
bound chi >= 6 must ALSO be established (it is the harder half of the {6,7}
split's bottom edge), but it is established once and absolutely, by a finite
witness; the genuinely model-dependent content is the gap between a measurable
6-coloring (exists in Solovay) and the non-existence of any measurable
6-coloring + existence of an AC 7-coloring-but-not-6 (ZFC).

---

## 1. The retrodicted terminal theorem (2050)

> **Metatheorem (HN-Independence, 2050).** Working over ZF + DC:
> 1. There is a finite unit-distance graph in R^2 with chi >= 6 (absolute,
>    Borel, holds in every model). Hence chi(R^2) >= 6 in every model.
> 2. In the Solovay model (ZF + DC + "every set of reals is Lebesgue
>    measurable"), the plane admits a measurable proper 6-coloring; hence
>    chi(R^2) = chi_m(R^2) = 6 there.
> 3. In ZFC, every proper 6-coloring of R^2 has a non-measurable color class,
>    AND there is an AC-driven proper 7-coloring but no proper 6-coloring at all;
>    hence chi(R^2) = 7 in ZFC.
> 4. Therefore "chi(R^2) = 6" is independent of ZFC: it holds in ZF+DC+LM and
>    fails in ZFC. Equivalently, chi(R^2) is not absolute between the Solovay
>    model and V=L.

The exact value is the PAIR (6 under measurability, 7 under choice). "chi(R^2)"
as a single integer does not exist; the function symbol is model-dependent.

---

## 2. The linchpin object (the single hardest missing thing)

Everything funnels into one construction, the **measurable tiling pair**:

> **A measurable proper 6-coloring of R^2 (a partition into 6 Lebesgue-measurable
> sets, none containing two points at distance exactly 1), TOGETHER with a proof
> that no such 6-coloring is destroyed by adding "every set measurable" but every
> AC-free 6-coloring is.** Concretely: a measurable 6-coloring template T whose
> existence is EQUIVALENT, over ZF+DC, to "every set of reals is measurable."

This is the object that does not exist in 2026 and gates the whole world. It is a
strict strengthening of two separately-open 2026 targets fused into one:

- (a) the measurable UPPER bound chi_m(R^2) <= 6 (today only chi_m <= 7 is known,
  via Isbell, and even that uses AC at the tile boundaries);
- (b) the equivalence "T exists  <=>  LM", which is the genuinely set-theoretic
  half and is what makes the value MOVE between models rather than just being
  unknown.

In 2026 language: the linchpin is **a Steinhaus-rigid measurable 6-tiling of the
plane whose boundary combinatorics encode a non-trivial Sigma^1_2 well-ordering
obstruction.** The tiling's color classes must have positive density everywhere
(so Steinhaus' difference-set theorem applies and forbids a 6th-color escape
under LM in the wrong regime) while admitting an AC refinement to 7 classes that
breaks the density.

---

## 3. The backward chain, 2050 -> 2026, with the 2026 obstruction each link is tethered to

Read bottom-up to go forwards; the table is ordered as the retrodiction
DISCOVERS them (latest first), then re-emitted earliest-first in the structured
output.

### Link E (2046-2050): the forcing/inner-model separation.
The final step packages (lower-bound absolute 6) + (Solovay 6-coloring) +
(ZFC anti-6 + 7-coloring) into "chi(R^2) is not absolute." The descriptive-set-
theoretic engine: a **Marks-style measurable-combinatorics determinacy argument**
showing the property "R^2 has a measurable proper 6-coloring" is invariant under
the Levy collapse that builds the Solovay model, but its negation is forced by a
Sigma^1_2 well-order in V=L. Tether: the 2026 obstruction is that Shelah-Soifer
independence is VACUOUS post-de-Grey because it was pinned at the 4-vs-5
threshold; this link RE-ANCHORS the conditional at the 6-vs-7 threshold (exactly
the dossier's open problem E4.4, "if all finite UDGs have chi <= 6 then chi=6 in
ZFC and >= ... in LM" re-tuned upward). Attackable-now sub-step: state and try to
prove the post-de-Grey conditional at the {5,6} threshold first (cheaper, may be
the actual split).

### Link D (2042-2046): the Solovay-side measurable 6-coloring.
Construct, IN the Solovay model, a measurable proper 6-coloring. This is where
"measurable upper bound is the bottleneck" bites: today even chi_m <= 6 is open
(only <= 7 known). The retrodicted construction is an **autocorrelation-feasible
6-tiling** produced by closing the Falconer/Fourier program from the UPPER side:
the de Laat-Vallentin / DeCorte-Oliveira-Vallentin SDP, run to optimality with
the custom sparse conic backend (L48-L50 blocker resolved), yields not just a
lower bound on m_1 but a DUAL feasible measure that is the indicator-system of an
explicit measurable 6-coloring. Tether: the 2026 blocker is precisely the
"custom sparse conic backend (de Laat-Vallentin)" named in L48-L50; the order-2
SDP at X_23 scale (48342 moment vars, 171 GiB dense map) must be solved sparsely.
Attackable-now sub-step: build the sparse backend and push order-2 on X_23 to a
DUAL certificate, not just a primal bound.

### Link C (2038-2042): the absolute lower bound chi >= 6.
A finite chi >= 6 unit-distance graph in R^2. This is THE named 2026 blocker
(brief section b). The retrodicted resolution is the **realizable color-clamp**
of L51-L53 (Theorem R): a K4-free 6-critical graph H with a LOW-DEGREE split
vertex w such that H - w realizes in the plane with one 3-subset of N(w) at
circumradius exactly 1. Tether: W3 realizability, the cocircularity equation on a
flexing H - w, is the precise 2026 residual. Attackable-now sub-step: find a
small (<= 14-vertex, so Groebner-decidable) K4-free 6-critical graph with a
degree-5 split vertex and decide the single circumradius equation by exact
elimination (the brief's `h2_groebner_moser14.py` route).

### Link B (2032-2038): the rigidity-matroid flexibility theorem.
Link C needs a general reason that SOME H - w has the required 1-parameter flex
meeting the cocircularity locus. The retrodicted enabler is a **rigidity-theoretic
genericity theorem**: for a suitable family of 6-critical graphs, the cocircularity
constraint variety meets the realization variety transversally, so a realizable
clamp exists. Tether: the 2026 obstruction is that "codim counts equations not
solvability" (L53 caveat (d)); a generically minimally-rigid H - w has zero flex,
so the theorem must identify a non-rigid sub-family. Attackable-now sub-step:
compute the rigidity matroid of the Schrijver graph SG(14,5) minus a vertex (the
L52-named candidate, triangle-free chi=6 vertex-critical, bounded degree) and
check whether its flex space is non-trivial.

### Link A (2026-2032): the post-de-Grey conditional + the measurable-upper-bound
program restart. Two parallel 2026-era stretches, both already half-named:
- (A1) re-tune Shelah-Soifer to the current threshold: replace "all finite UDGs
  4-colorable" (dead) with the live "all finite UDGs <= k-colorable" for k in
  {5,6}. Tether: dossier E4.4, explicitly flagged open. This is the seed of Link E.
- (A2) flip the measurable program from LOWER bounds (m_1 <= 0.247, capped at 5
  by the Croft floor) to UPPER bounds (measurable 6-coloring existence). Tether:
  the density route is "provably capped at 5" (brief d), so the m_1 lower-bound
  ladder is a dead end for >= 6; the live direction is the dual/primal-feasible
  COLORING, which is Link D's seed.

---

## 4. Which 2026 technique gets stretched furthest

**The de Laat-Vallentin sparse conic / autocorrelation SDP machinery (Arch 2/3),
run in REVERSE.** In 2026 it produces lower bounds on chi_m via lower bounds on
m_1 (the Ambrus X_23 line). The retrodiction stretches it to produce, from the
DUAL side, an explicit measurable 6-COLORING in the Solovay model (Link D) and
its non-existence under AC-refinement (the boundary that breaks density). That is
a 180-degree repurposing of the exact same SDP whose sparse backend is the
L48-L50 blocker. Second-most-stretched: the L53 cocircularity/rigidity reframing,
pushed from "non-impossibility" to an actual transversality theorem (Link B).

## 5. Which bound is the real bottleneck (explicit)

The **upper bound, specifically the measurable upper bound chi_m(R^2) <= 6**, is
the bottleneck in this world. Reasons:
1. The lower edge (chi >= 5) is absolute and DONE (de Grey). chi >= 6 is also a
   finite-witness absolute statement (Link C); hard, but a SINGLE object, and
   once found it never moves between models.
2. The model-DEPENDENCE lives entirely in the upper structure: "is there a
   measurable 6-coloring?" is the question whose answer flips between Solovay
   (yes, value 6) and ZFC (no, value 7). That is a chi_m <= 6 existence question,
   i.e. an upper-bound question.
3. 2026 evidence: Falconer chi_m >= 5 has been frozen 45 years; the density route
   is capped at 5; ALL recent motion on the upper side (Mundinger ML six-coloring
   continuum, Isbell 7) is about COLORINGS, i.e. upper bounds. The upper bound is
   where the live machinery and the model-dependence both sit.

---

## 6. Wrong-approach-detector self-assessment (honest)

- **Q^2 (chi = 2, Woodall).** PASS. The whole metatheorem rides on a Hamel-basis /
  Levy-collapse mechanism that DEGENERATES on Q^2 (the field is Q, the Hamel basis
  is {1}, no measurability obstruction). The measurable 6-coloring of Link D uses
  the topology and POSITIVE DENSITY of R, absent on the measure-zero Q^2. Arch 4
  gets the partial Q^2 exemption anyway, but this construction passes outright.
- **L^infty (chi = 4, Chilakamarri).** PASS, and this is the load-bearing check.
  The ABSOLUTE lower bound chi >= 6 (Link C) is built from a Euclidean color-clamp
  whose realizability is a cocircularity (unit-CIRCLE) condition specific to the
  Euclidean norm; in L^infty the "unit circle" is a square and the cocircularity
  variety is different (Link C would not produce a 6-chromatic graph there, as it
  should not, since chi(L^infty)=4). The Solovay 6-coloring (Link D) uses the
  Fourier/autocorrelation kernel of the Euclidean group O(2), again norm-specific.
  The Alon-Bucic-Sauermann 2023 sharpening (almost all norms give chi=4) is
  RESPECTED: the construction invokes Euclidean rigidity (equilateral triangles in
  the clamp, the J_0 Bessel kernel) at every Euclidean step.
- **R^1 (chi = 2).** PASS. The O(2) rotation group is essential to the
  measurable-coloring kernel (Link D's Bochner/J_0 ingredient) and to the clamp's
  cocircularity (Link C). Strip rotations and both collapse; the argument cannot
  constrain chi(R^1). NOTE the one subtlety: the Shelah-Soifer MECHANISM (Link A1)
  is demonstrated on R^1 in the 2003 original (a line distance graph with
  axiom-dependent chi). That is the mechanism's NATIVE habitat, not an overshoot;
  the metatheorem's chi=6/7 split is firmly 2-dimensional (needs the clamp and the
  O(2) kernel), so it does not transport an integer-gap to R^1.

**Self-detector verdict**: an argument that proved this WITHOUT invoking Euclidean
rigidity at Links B/C/D would be structurally wrong (it would over-prove on
L^infty). The retrodiction is built so the Euclidean content is concentrated
exactly where the value 6 vs 7 is decided.

---

## 7. Verification targets (for VERIFIER) and adversarial tests (for ADVERSARY)

**VERIFIER targets (formal / computational):**
1. (Absoluteness floor) Formalize: a finite UDG with chi >= k has chi_m >= k and
   chi_B >= k in every model of ZF+DC. (Mathlib: finite => Borel => measurable.)
   This is the rigorous backbone of section 0 and is provable NOW.
2. (Woodall control) chi(Q^2) = 2, to certify the Q^2 detector pass (dossier E4.2,
   Lean target HN-5).
3. (Hierarchy) chi(R^2) <= chi_B(R^2) <= chi_m(R^2) as a Lean lemma schema, with
   the absoluteness floor making all three >= 5.
4. (Link C decidability) given a concrete small K4-free 6-critical graph with a
   degree-5 split vertex, run exact elimination on the single circumradius
   equation; report SAT/UNSAT of realizability. Decidable in principle NOW for
   <= 14 vertices.

**ADVERSARY tests (try to break the world):**
1. **Rigidity-kills-independence (the strongest adversary).** Argue that the
   unit-distance graph is TOO RIGID for the value to move: that any measurable
   6-coloring in Solovay descends to a (possibly non-measurable) 6-coloring in
   ZFC, collapsing the {6,7} split to a single value 6 in both models. If R^2 is
   not absolute-sensitive, the whole metatheorem is empty. This is the dossier's
   named adversary (section 4.2 / 8 of arch4).
2. **Lower-bound-already-7 (collapses to no independence).** If a finite chi >= 7
   UDG exists (not ruled out in 2026), then chi=7 is absolute and there is NO
   split; the world is false. Adversary should check whether de Grey's 2026
   conjecture (omega <= 3 caps construction at 5) instead forces chi=5 absolutely,
   which would ALSO kill this world (no room above 5). Either extreme kills it.
3. **Solovay-coloring-nonexistence.** Attack Link D: argue no measurable
   6-coloring exists even under LM (i.e. chi_m >= 7 absolutely), e.g. by a
   Falconer-style density argument pushed to 6. This would make the value 7 in
   both models (absolute), again no independence.
4. **Detector overshoot.** Re-run the L^infty detector on the actual Link C/D
   constructions: if either yields chi >= 6 under the sup-norm, it is wrong.

The world survives only if EXACTLY: a finite chi>=6 UDG exists, no finite chi>=7
UDG exists, a measurable 6-coloring exists under LM, and no measurable 6-coloring
exists under AC. The four adversary tests probe each of these four load-bearing
facts.
