# Session 004: HN-2 full Lean, Architectures 2-4 opened, cross-architecture synthesis

**Date**: 2026-05-25 (continuation) through 2026-05-26
**Mode**: depth + breadth combined; all four architectures touched
**Architecture focus**: 1 (HN-2 Lean completion), 2, 3, 4 (opening + integration)

## Goal

Continuation of session 003. After landing multi-solver SAT verification of chi >= 5 at five graphs (and 1585 running in background), broaden from Architecture 1 to the other three architectures while completing the Moser-spindle Lean chain (HN-2c and HN-2d).

## What landed

### Lean HN-2 completion (commits 80081c3, 7892185)

- **HN-2c** `moserSpindle_chromaticNumber = 4`: glued HN-2a (Colorable 4) and HN-2b (not Colorable 3) into the full equality. The Mathlib lemma `Nat.sInf_upward_closed_eq_succ_iff` is exactly the right tool, applied at `k = 3` after using `Colorable.mono` to establish upward-closure of the `{n | Colorable n}` set.

- **HN-2d** `four_le_chromaticNumberOfPlane`: bridge from the abstract `Fin 7` Moser spindle to the Euclidean unit-distance graph. Explicit coordinates with `Real.sqrt 3 / 11 / 33`, eleven distance lemmas via a custom `moser_edge` macro tactic (unfold, substitute `sqrt 33 = sqrt 3 * sqrt 11`, `nlinarith` with square identities), homomorphism dispatch via `fin_cases` over 49 pairs with `maxHeartbeats 1000000` to absorb the `first | ...` combinator's quadratic cost, chromatic transfer via `SimpleGraph.chromaticNumber_le_of_forall_imp`.

The end-to-end Lean theorem `4 ≤ chromaticNumberOfPlane` is now fully kernel-verified.

### Architecture 2: measurable opening (commits 0aa3e05, 868791e)

- `docs/02_graduate/measurable_chromatic_number.md`: graduate-level exposition of chi_m, Falconer's proof, Shelah-Soifer phenomenon (since updated by L7), wrong-approach detectors.
- `experiments/measurable/e2a_falconer_autocorrelation.py`: 512x512 grid, indicator of pointy-top hexagon of diameter 0.95, 2D FFT autocorrelation. Result: autocorrelation identically 0 across 16 angles on the unit circle, illustrating the Falconer building block at scale.
- Surveyor dossier: `docs/research_atlas/arch2_measurable_lineage.md` (3300 words). 12 chronology entries, lemma-level Falconer proof reconstruction, critical examination of chi_m >= 6 claims.

**Major atlas correction**: the widely-cited "chi_m(R^2) >= 6 in recent work" is a misattribution. The Euclidean measurable bound has been chi_m >= 5 since Falconer 1981 (45 years unchanged). The ">= 6" results are from the hyperbolic plane H^2(d) for d >= 12 (DeCorte-Golubev 2018) or restricted-region variants where color classes are convex tiles (Coulson 2002). Neither implies a measurable lower bound on R^2.

### Architecture 3: fractional / Lovász theta opening (commits fecb7f7, e07a720, 284caae)

- `experiments/fractional/e3a_lovasz_theta_polymath16_510.py`: vanilla Lovász theta SDP on the 510-vertex Polymath16 graph. Result: theta = 170.24 (644 s, cvxpy + SCS), giving chi >= 3 only. Loose by 2 integer units vs known chi = 5.

- `experiments/fractional/e3b_ofv_bessel_lp.py`: the "symmetry fix". Discretized OFV-style Bessel-LP for m_1(R^2), parametrizing radially-symmetric positive-type functions as F(r) = sum_k c_k J_0(2 pi r s_k) with c_k >= 0. Result: m_1(R^2) <= 0.287, chi_m >= 4 in 30 milliseconds (cvxpy + HiGHS). The LP places all mass at s ~ 0.6087, the first negative minimum of J_0. **20,000x faster than vanilla theta AND a tighter integer bound on a stronger object.**

### Architecture 4: set-theoretic opening (commits 593af4a, 0b12e19)

- Surveyor dossier: `docs/research_atlas/arch4_set_theoretic_lineage.md` (3400 words). 13 chronology entries, four-way taxonomy of the Shelah-Soifer 2003/2003b/2005/Payne 2009 lineage, hierarchy chi <= chi_B <= chi_m definitions, candidate experiments E4.1-E4.4.

**Second major atlas correction**: the widely-cited "Shelah-Soifer: chi(R^2) depends on choice axioms" is a *conditional* theorem ("if every finite UDG has chi <= 4, then..."). de Grey 2018 falsified the hypothesis by producing a 5-chromatic finite UDG. The conditional is now vacuous as a statement about chi(R^2). The phenomenon survives for artificial distance graphs (Payne 2009) but not for chi(R^2) specifically. Whether chi(R^2) actually depends on AC at the post-2018 threshold is **open** and the obvious replacement conditional ("if all finite UDGs have chi <= 5, then chi >= 6 in ZF + DC + LM") has not been published.

### Cross-architecture synthesis (commit bbcb2d1, updated in 0b12e19)

`docs/03_research/cross_architecture_coupling.md`: integrates LEARNINGS L1-L7 into a single narrative. The headline finding: **three of the four architectures are coupled to Architecture 1 via the same missing combinatorial object (a 6-chromatic finite UDG)**.

- L4: Arch 2 waits for an Arch 1 breakthrough. Falconer's chi_m >= 5 proof amplifies a 5-chromatic UDG; the same machine would amplify a 6-chromatic UDG to chi_m >= 6.
- L6: Arch 3 has the same barrier in continuous form. Pushing m_1 < 1/5 via OFV-style LP would give chi_m >= 6, but the current best (Ambrus et al. 2023) is 0.247.
- L7: Arch 4's main 2003 result was already invalidated by Arch 1's 2018 breakthrough. No current published statement specifically about chi(R^2).

Only Architecture 4's broader descriptive-set-theoretic / Borel chromatic program is structurally independent of the missing UDG, and it has not produced bounds on chi(R^2) specifically.

### de Grey 1585 SAT completion (commit 3b8b652)

Background run from session 003 completed:
- cadical195: 5531 s (~92 min) UNSAT
- glucose4: 6456 s (~108 min) UNSAT

The original de Grey 2018 graph (1585 vertices, 7909 edges) is now multi-solver SAT-verified. This is the historic graph that broke chi >= 4 in 2018. Combined with the previous 5 graphs in the lineage, chi >= 5 is now independently verified on six distinct graphs.

### Formatting fix (commit f472925)

Cleanup pass on `docs/01_undergraduate/hexagonal_upper_bound.md`: single-fraction inradius formula, cleaner derivation chain, L^infty notation consistent with the atlas.

## Verified state at session end

End-to-end Lean theorem:

```lean
theorem four_le_chromaticNumberOfPlane : 4 <= chromaticNumberOfPlane
```

(In `lean/HadwigerNelson/MoserBridge.lean`; the full Moser bridge chain.)

Multi-solver SAT verification of chi(R^2) >= 5 at:

| Graph             | V    | E    | cadical    | glucose    |
|-------------------|-----:|-----:|-----------:|-----------:|
| Polymath16 G11    |  510 | 2504 |     78 s   |    111 s   |
| Heule G10 SBP     |  517 | 2579 |      3 s   |      3 s   |
| Heule G8          |  529 | 2670 |     82 s   |    119 s   |
| Heule G7 SBP      |  553 | 2722 |      2 s   |      2 s   |
| Heule intermediate|  826 | 4273 |    279 s   |    805 s   |
| de Grey 2018      | 1585 | 7909 |   5531 s   |   6456 s   |

Six independent graphs, two solver families (cadical CDCL + glucose LBD-based), full agreement on UNSAT. Strongest single-machine evidence for chi(R^2) >= 5 short of formal verification.

Lovász theta + OFV LP on continuous side gives chi_m >= 4 via two routes (vanilla theta = loose chi >= 3; rotation-invariant Bessel-LP = clean chi_m >= 4 in 30 ms).

## LEARNINGS now in the project

| # | Architecture | Finding | Source |
|---|--------------|---------|--------|
| L1 | 1, cross | 6-chromaticity easy in HN-adjacent variants, uniquely resists in single-distance | Arch 1 dossier |
| L2 | 1 | Moser spindle structurally inessential (Voronov spindle-free 64513-vertex) | Arch 1 dossier |
| L3 | 1 | Multi-solver SAT agreement reproduces chi >= 5 across 6 graphs | e1b experiments |
| L4 | 1+2 | Arch 1 and Arch 2 share a single missing 6-chromatic finite UDG | Arch 2 dossier |
| L5 | 3 | Vanilla Lovász theta on de Grey lineage UDGs is structurally loose | e3a |
| L6 | 3 | Rotation-invariant Bessel-LP wins 20,000x vs vanilla theta with cleaner bound | e3b |
| L7 | 4 (cross to 1) | Arch 1's 2018 breakthrough erased Arch 4's main 2003 result about chi(R^2) | Arch 4 dossier |

## Pending

- **HN-3** Isbell hexagonal upper bound chi <= 7 (Lean). Hard: measure-theoretic tiling.
- **HN-4** de Grey lower bound chi >= 5 (Lean). Major project: needs SAT/DRAT checker in Lean.
- **HN-5** Woodall chi(Q^2) = 2 (Lean). Tractable; Pythagorean-triple parity.
- **HN-6** Chilakamarri chi(L^infty) = 4 (Lean). Direct construction.
- **Field-theoretic search** (L1): which rings Z[zeta] refuse 5-colorings?
- **Reproduce Ambrus et al. m_1 <= 0.2470**: 23-point LP, would give chi_m >= 5 via L6 framework.
- **Higher-order OFV LP hierarchy** (DeCorte-OFV 2018): days of work.
- **Replacement Shelah-Soifer conditional** (L7): "if all finite UDGs have chi <= 5, then chi >= 6 in ZF + DC + LM". Unpublished.
- **Variants sub-dossier** (odd-distance, two-distance, sphere).
- **Architecture 3 standalone dossier** (currently covered partly by Arch 2 dossier and the synthesis).
- **Visualizations** (manim) — entirely unstarted.

## Compute used this session

- Lean: full library build ~1860 modules; HN-2d's macro tactic runs maxHeartbeats 1M.
- Python SAT: ~3.3 hours total wall time across all 6 graphs (mostly de Grey 1585).
- Python SDP: 644 s for vanilla Lovász theta on 510-vertex graph.
- Python LP: 30 ms for OFV Bessel-LP.
- Background agents: 2 SURVEYOR runs (Arch 2, Arch 4), ~7-8 minutes each.

## Lessons for future sessions

- The "obvious" SDP approach (vanilla Lovász theta on bigger graphs) is a dead end for HN. The right SDP is rotation-symmetric.
- Background SAT runs through PowerShell with `run_in_background` capture stdout in a buffer that does not flush until the process exits. Cannot see live progress.
- Multi-solver SAT scaling: SBP variants are 10-100x faster than basic CNF; for big problems (1000+ vertices) the SBP version may be essential.
- Lean `decide` blows the kernel stack at ~2000 cases; switch to `native_decide` for finite brute-force searches.
- The "$\chi_m \geq 6$" and "Shelah-Soifer chi(R^2)" claims in the literature are widely misattributed. Surveyor agents catch these efficiently.
