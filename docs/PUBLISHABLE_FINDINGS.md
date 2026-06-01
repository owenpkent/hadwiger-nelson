# Publishable Findings Assessment

Honest assessment of what this project has produced that could become a publication,
and what each candidate would need first. Written 2026-06-01.

**Read this first.** The headline is a negative: **nothing here moves the known
bounds.** $\chi(\mathbb{R}^2) \in [5,7]$ and $\chi_m(\mathbb{R}^2) \in [5,7]$ are
unchanged. There is no 6-chromatic unit-distance graph, no $\chi_m \geq 6$, no
improved upper bound, no resolution of any case of the problem. So there is no
"major theorem" result. Everything below is in the tier of structural/experimental
notes, a method-in-progress, or verification work.

**Provenance caveat.** Most of the findings below were produced by earlier agent
sessions (LEARNINGS L1-L34). They have NOT all been independently re-verified in
the current session; only the measurable-LP thread (e3l-e3n, L39-L41) was re-run
and checked here. Treat every claim as "candidate, pending independent
verification and a prior-art check" until that work is done. The plane-chromatic
community (Soifer, de Grey, Heule, the Polymath16 participants, Oliveira-Vallentin,
Ambrus-Matolcsi) is small and sophisticated; several observations below may be
known to them. None should be claimed as novel without a literature check.

---

## Tier 1: plausibly publishable as a focused note

### F1. A structural explanation of why $\chi \geq 6$ has resisted post-2018 SAT search

**The claim.** The reason no 6-chromatic unit-distance graph has emerged from the
de Grey / Polymath16 / Heule lineage despite eight years of search is a specific
geometric obstruction, not merely insufficient compute.

**The evidence (LEARNINGS L23, L24, L27-L30, L34).**
- *Abstract chi-6 couplings exist.* Coupling two $\chi$-5 halves (Polymath-510) by a
  no-$K_4$ bridge set forces $\chi \geq 6$: an explicit **1019-vertex** no-$K_4$
  graph, dual-solver UNSAT-confirmed, is the current abstract record (L30). The
  governing theorem (a triple-coupling lift, $\chi \geq 6$ iff a residual
  list-coloring is universally infeasible) is machine-checked in Lean
  (`lean/HadwigerNelson/L24TripleCoupling.lean`, no `sorry`).
- *But they are never unit-distance realizable.* Each saturating vertex requires
  22-27 bridge endpoints to lie exactly on a unit circle; the geometry forbids the
  cocircularity (L23, L27-L29, the "cocircularity sieve").
- *The sharpened barrier (L34).* Realizability forces an EVEN, low-concentration
  bridge layout (a 60-degree orbit of Polymath-510 has 13,757 genuine
  unit-distance bridges, max bridge-degree 36, all 510 vertices touched, and is
  5-colorable in 0.06s). The chi-6 list-coloring obstruction instead needs
  CONCENTRATION (L27: max source-degree 268 on hub vertices). So the embeddable
  bridge supply is the wrong SHAPE for chi-6 forcing, not merely the wrong COUNT.

**Why it could be a paper.** It is a concrete, non-obvious, computationally
supported explanation of a real phenomenon (the post-de-Grey wall). It reframes the
search for a chi-6 UDG as a precise geometric question (realize a concentrated
bridge layout on cocircular point sets in an algebraic field).

**What it is NOT yet.** Heuristic and experimental, not a theorem. There is no proof
that "no chi-6 UDG of this coupled form exists"; the evidence is a finite battery of
failed realizations and 5-colorable witnesses. To be publishable it needs (a) a
crisp, falsifiable statement of the obstruction, (b) either a proof for a restricted
class or an honest framing as an experimental finding, (c) a check that the
"two halves + bridges" framing is exhaustive for the lineage.

**Venue.** Geombinatorics or an experimental-mathematics venue; arXiv note.

**Confidence the core observation survives scrutiny.** Moderate. The 5-colorability
of large realizable bridge families is solver-verified and robust; the
"concentration vs. spread" framing is the part most likely to need sharpening or to
turn out partially known.

### F2. Structural anatomy of the de Grey / Polymath / Heule $\chi \geq 5$ lineage

**The claim (LEARNINGS L15-L20).**
- No non-identity exact rotational symmetry survives SAT minimization (Polymath-510,
  Heule-826, de Grey-1585 all checked).
- The $\chi \geq 5$ obstruction is extremely DELOCALIZED: every reasonable
  structural reduction (cores, halves, bridge-touched subgraphs, up to 75% of the
  original) drops $\chi$ to 4 (L18).
- **Polymath-510 is de Grey-1585 translated and field-reduced**: 315/510 = 62% of
  Polymath vertices coincide with de Grey vertices under $T = (2,0)$ (L19). The
  Heule/Parts minimization reformulated de Grey rather than constructing a new graph.
- Every $\chi \geq 5$ graph in the lineage is "two $\chi$-4 halves + bridge edges"
  (L20).

**What it would need.** Independent recomputation of the 62% overlap and the
reductions; a prior-art check against the Polymath16 project pages and Soifer's book
(the participants documented their constructions thoroughly, so some of this may be
known); rigorous statements. Lower novelty than F1 and higher folklore risk.

**Venue.** Same as F1; possibly folded into F1 as the "background structure" section.

---

## Tier 2: a novel method, but no result yet

### F3. A multi-class measurable moment relaxation as the un-capped route to $\chi_m \geq 6$

**The setup (LEARNINGS L37-L41; experiments e3k-e3n).** Single-class avoiding-set
density is PROVABLY capped at $\chi_m \geq 5$: Croft's construction gives
$m_1(\mathbb{R}^2) \geq 0.22936 > 1/5$, so $1/m_1 \leq 4.36$ and no improvement to
the density upper bound can reach 6. To pass 5 the argument must use the JOINT
structure of all color classes.

**What was built.** A Lasserre / moment hierarchy over the pairwise (and, at order
2, up to size-4) COLOR-MARGINALS of the distribution over proper $k$-colorings of a
configuration, with each per-color autocorrelation forced Bochner-positive and
vanishing at distance 1, AND a multi-class analog of the Ambrus 2023
inclusion-exclusion CONGRUENCE constraints. The key new ingredient is
**Formulation 2** (cross-color congruence: "red-next-to-blue" patterns coupled to
their isometric images), which is NOT covered by the $\alpha_1 = 1/4$ density cap.
The stack: e3k (formulation) $\to$ e3l (IEC sharpness, validated) $\to$ e3m
(degree-1 scalable backend, validated) $\to$ e3n (order-2, correct but
naive-unscalable).

**Honest status.** It has NOT produced a bound. It is a validated engine and a
well-posed program. Two reasons it is not yet a paper:
1. It has not bitten: on every enumerable / tractable configuration the margin is 0
   (no obstruction detected). The validation target (reproduce $\chi_m \geq 5$ on
   the Ambrus 23-point config) is out of reach because the explicit backend cannot
   enumerate it and the naive order-2 SDP does not scale (L41: even $n=4$ takes
   $\sim 13$ s; $X_{23}$ needs the $O(2)$/congruence symmetry reduction of
   de Laat-Vallentin / DeCorte-Oliveira-Vallentin).
2. Novelty over the existing moment-hierarchy literature (de Laat-Vallentin 2015;
   DeCorte-Oliveira-Vallentin 2022) for measurable colorings must be pinned down.
   The JOINT-coloring / cross-color-IEC framing may be new relative to their
   single-set independence-number machinery, but this needs to be established.

**What it would need to be publishable.** Either (a) the symmetry-reduced order-2
SDP plus a restored $X_{23}$, run to actually produce $\chi_m \geq 5$ from the joint
angle (a methods result), and then $k=5$ as the open $\geq 6$ frontier; or (b) a
careful theoretical demonstration that Formulation 2 is strictly stronger than the
single-class cap, independent of a numerical bound.

**Venue (if it produces a bound).** A discrete-geometry / optimization venue
(Discrete & Computational Geometry, Mathematical Programming, Experimental Math).

---

## Tier 3: verification value, not novel mathematics

### F4. Self-certified reproduction of Ambrus 2023, $\chi_m(\mathbb{R}^2) \geq 5$
The repo reproduces $m_1(\mathbb{R}^2) \leq 0.246894 < 1/4$ using its OWN dual
certificate (the IEC congruence family re-derived in-repo), independent of the
paper's website-only dual coefficients (L35/L36). Useful verification; not new
mathematics. NOTE: the 23-point input is currently gitignored and absent from a
clean clone, so this is not reproducible from scratch here (a reproducibility debt,
not a result).

### F5. Independent SAT re-verification of the lineage
cadical + glucose agree on UNSAT (non-4-colorability) for the de Grey 1585 and the
510/517/529/553/826 Polymath/Heule variants. Confirms the state of the art; not
novel.

### F6. Lean $\chi \geq 5$ bridge theorem
A machine-checked (no `sorry`) reduction: a graph hom into the plane unit-distance
graph plus non-4-colorability yields $5 \leq \chi(\mathbb{R}^2)$
(`lean/HadwigerNelson/DeGreyLowerBound.lean`). This is groundwork. A FINISHED
kernel-verified $\chi(\mathbb{R}^2) \geq 5$ (adding an LRAT-checked certificate and
a $\sim 2500$-edge exact embedding) WOULD be publishable (CPP / ITP), and would be
the first formal verification of the bound. It is not done.

---

## The bottom line and the recommended path

The single most write-up-worthy item is **F1**: the cocircularity / wrong-shape-bridge
explanation of the $\chi \geq 6$ barrier. It is concrete, non-obvious, and explains a
real phenomenon, and it is the closest to a self-contained story.

Before any of this is publishable, three things are owed:
1. **Independent re-verification** of the earlier-session computations (only e3l-e3n
   were re-run this session).
2. **A literature / prior-art check** against Polymath16, Soifer, Ambrus-Matolcsi,
   and Oliveira-Vallentin, to confirm novelty.
3. **Rigor**: converting heuristic observations (especially the F1 "concentration"
   barrier) into falsifiable statements, and either proving a restricted case or
   framing honestly as experimental.

**Recommended next step.** Pressure-test F1: actively try to BREAK the cocircularity
claim (search for a realizable concentrated bridge layout in an enlarged field),
delimit exactly what is rigorous vs. heuristic, and check it against the literature.
That is the fastest way to learn whether F1 is a real paper or a known/false lead.

---

## Verification debt ledger

| Finding | Re-verified this session? | Prior-art checked? | Rigorous statement? |
|---|---|---|---|
| F1 cocircularity barrier | No | No | No (heuristic) |
| F2 lineage anatomy | No | No | Partial |
| F3 multi-class moment LP | Yes (e3l-e3n) | No | Valid relaxation, no bound |
| F4 Ambrus reproduction | No (input missing) | N/A (reproduction) | Yes |
| F5 SAT re-verification | No | N/A | Yes |
| F6 Lean bridge theorem | No | N/A | Yes (but incomplete goal) |
