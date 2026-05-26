# Cross-architecture coupling in Hadwiger-Nelson

*Synthesis of LEARNINGS L1-L6, session 003 of the Hadwiger-Nelson research program.*

The project frames the chromatic number of the plane $\chi(\mathbb{R}^2)$ as a problem with four candidate proof architectures: combinatorial (UDG SAT), measurable (Falconer), fractional / spectral (Lovász $\vartheta$ / OFV), and set-theoretic (Shelah-Soifer). This document argues that **the architectures are not independent**: at the level of obstructions, Architecture 1 and Architecture 2 share a single missing object, and Architecture 3 evidence suggests the same is structurally true for $\chi_f$. The four-architecture framing remains useful as an attack surface, but the no-progress-since-2018 facts across the board are a *single* missing object in disguise.

## The empirical core of one day's work

In one focused work day (2026-05-25) the project produced:

1. **Lean kernel theorem `4 ≤ chromaticNumberOfPlane`** ([`lean/HadwigerNelson/MoserBridge.lean`](../../lean/HadwigerNelson/MoserBridge.lean)). Full pipeline: explicit 7-vertex Moser spindle on `Fin 7`, decide-based 4-coloring witness, `native_decide`-based non-3-colorability over $3^7$ candidates, glue via `Nat.sInf_upward_closed_eq_succ_iff` to $\chi = 4$, bridge to Euclidean plane via 11 distance-1 lemmas on coordinates with $\sqrt{3}, \sqrt{11}, \sqrt{33}$ proved by `nlinarith`, transfer to `chromaticNumberOfPlane` via `chromaticNumber_le_of_forall_imp`.

2. **Multi-solver SAT verification of $\chi \geq 5$** at five graphs in the Polymath16 / Heule lineage: 510, 517, 529, 553, 826 vertices. cadical195 and glucose4 agree on UNSAT for 4-coloring in each. (1585 still running.)

3. **Vanilla Lovász $\vartheta(G) = 170.24$ on the 510-vertex graph** gave only $\chi \geq 3$ (loose by 2 integer units, $\chi$ known = 5).

4. **Rotation-invariant Bessel-LP** for $m_1(\mathbb{R}^2)$ gave $m_1 \leq 0.287$, $\chi_m \geq 4$ in 30 milliseconds (cvxpy + HiGHS) — 20,000× faster than vanilla $\vartheta$, with a tighter integer bound on a stronger object.

5. **Two surveyor dossiers** establishing the literature: [arch1 SAT lineage](../research_atlas/arch1_sat_lineage.md) and [arch2 measurable lineage](../research_atlas/arch2_measurable_lineage.md). The arch2 dossier corrected a long-standing atlas misattribution: the widely-cited "$\chi_m(\mathbb{R}^2) \geq 6$" is not on the canonical Euclidean plane; the actual Euclidean bound has been $\chi_m \geq 5$ since Falconer 1981, 45 years unchanged.

## Six structural findings (L1-L6)

The empirical core produces six LEARNINGS that are mutually reinforcing.

**L1**: 6-chromaticity is *easy* in Hadwiger-Nelson-adjacent variant problems. Two-distance graphs in $\mathbb{R}^2$ have 6-chromatic constructions at 16 vertices (Parts 2020). Odd-distance graphs have finite 6-chromatic subgraphs (Parts 2022). Continuum off-diagonal six-colorings have been extended (Mundinger-Pokutta et al. 2024-2025). **But no 6-chromatic single-distance UDG in $\mathbb{R}^2$ is known after 8 years of post-de-Grey search.** The smallest 5-chromatic single-distance UDG has been stuck at 509 vertices (Parts 2020) for 5 years.

**L2**: The Moser spindle is structurally inessential. Voronov-Neopryatnaya-Dergachev 2021 produced a 64513-vertex 5-chromatic UDG with no Moser spindle as a subgraph. The motif used in every other $\chi \geq 5$ construction (de Grey, Heule, Parts) is not logically necessary.

**L3**: At the 510-826 vertex range, multi-solver SAT cleanly reproduces $\chi \geq 5$. Five independent verifications, two solver families (cadical CDCL with chronological backtracking; glucose LBD-based CDCL). The five-graph spread rules out single-solver soundness bugs. Symmetry-breaking predicates give 10-100× speedup.

**L4**: **Architectures 1 and 2 share a single missing object.** Falconer's $\chi_m \geq 5$ proof works by (a) Lebesgue-density extraction from a hypothetical 4-coloring, then (b) inscribing a *rigid finite Moser-spindle-like configuration* in the dense region to force a contradiction. The proof's load-bearing combinatorial object in step (b) is "a finite configuration in $\mathbb{R}^2$ that is at least 5-chromatic as a UDG." Pushing the same machinery to $\chi_m \geq 6$ would require **a 6-chromatic finite UDG in $\mathbb{R}^2$**. The same object Architecture 1 has been searching for since 2018. Both architectures stall at 5 for the same combinatorial reason.

**L5**: Vanilla Lovász $\vartheta$ on the 510-vertex Polymath16 graph gives $\vartheta = 170.24$ in 644 seconds, yielding only $\chi(G) \geq 3$. Loose by 2 integer units. The bare graph SDP doesn't see the rotation symmetry of $\mathbb{R}^2$. Integrality gap of ~68 vertices.

**L6**: The rotation-invariant Bessel-LP for $m_1(\mathbb{R}^2)$ gives $m_1 \leq 0.287$ in 30 milliseconds. The LP places all weight at the single frequency $s \approx 0.6087$ where $J_0(2\pi s)$ hits its first negative minimum $\approx -0.403$. **$2 \times 10^4$ times faster than vanilla $\vartheta$ AND a strictly tighter integer bound on a stronger object** ($\chi_m \geq 4$ vs $\chi \geq 3$).

## The unified picture

The six findings tell a single story.

**$\chi(\mathbb{R}^2)$ has been stuck at the interval $[5, 7]$ since 1950, with $\chi \geq 5$ established in 2018.** Every method that has tried to push the lower bound up to 6 has stalled. The four architectures look like four independent attacks: SAT-driven combinatorial graphs (Arch 1), measure-theoretic with rotation invariance (Arch 2), spectral / fractional via LP / SDP (Arch 3), set-theoretic (Arch 4, unstarted in this project).

**But they're not independent**. L4 shows that Architectures 1 and 2 are *coupled at the obstruction level*: Falconer's machine consumes a finite $\chi \geq 5$ UDG and produces $\chi_m \geq 5$. To produce $\chi_m \geq 6$, the same machine would need a finite $\chi \geq 6$ UDG, which doesn't exist (Arch 1). So Arch 2's barrier *is* Arch 1's barrier with a measure-theoretic amplifier.

**Architecture 3 (L5, L6) confirms this is not coincidence.** The vanilla Lovász $\vartheta$ on any of the Polymath16 graphs gives only $\chi \geq 3$ — the SDP relaxation is too coarse to see the rotation structure that makes Falconer's proof work. The rotation-invariant LP cleanly gives $\chi_m \geq 4$, matching OFV's published integer bound, but to push to $\chi_m \geq 5$ requires $m_1 < 0.20$, which Ambrus et al. 2023 approaches but doesn't reach (best $0.2470$). The continuous side is *also* stuck at the same place: $\chi_m \geq 5$ from Falconer, no improvement to 6 without either a finite 6-chromatic UDG or $m_1 < 0.20$.

**The single missing object**: a 6-chromatic finite UDG in $\mathbb{R}^2$. If found, Architecture 1 gets $\chi \geq 6$ immediately and Architecture 2 gets $\chi_m \geq 6$ via Falconer's machine. If never found (because $\chi(\mathbb{R}^2) = 5$), all architectures stay at 5.

**The alternate path**: a density bound $m_1(\mathbb{R}^2) < 0.20$ would force $\chi_m \geq 6$ without needing a finite UDG, via the OFV $\chi_m \geq 1/m_1$ bridge. Current best is $0.2470$ (Ambrus et al. 2023), 0.047 from sufficiency. Each refinement of the LP (OFV $\to$ Keleti $\to$ Ambrus) has shaved ~0.01 off $m_1$ over 15 years. Reaching $0.20$ within the same framework would require another half-decade of improvements at the current pace.

## What this implies for the program

**For BUILDER**: stop looking at the four architectures as independent attack surfaces. The interesting BUILDER directions are:
- Architecture 1: the **field-theoretic search** (L1) — which closed-under-rotation rings $\mathbb{Z}[\zeta]$ refuse 5-colorings? Every published $\chi \geq 5$ UDG lives in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$; what does $\mathbb{Q}(\sqrt{3}, \sqrt{11}, \zeta)$ look like for various $\zeta$? Novel.
- Architecture 2/3 boundary: tighten the OFV / BNOFV / AC-MV-Z LP framework toward $m_1 < 0.20$. Hard but well-defined; published work approaches it asymptotically.
- Architecture 1 / 2 coupling: any 6-chromatic UDG (Arch 1) immediately gives $\chi_m \geq 6$ (Arch 2). This means resources are best concentrated, not parallelized across architectures.

**For VERIFIER**: any claimed $\chi(\mathbb{R}^2) \geq 6$ result must implicitly construct (or imply the existence of) a 6-chromatic finite UDG. Check against the L1 / L4 coupling. Any claimed $\chi_m \geq 6$ result without a corresponding UDG construction must either (a) push $m_1 < 0.20$ through a density argument, or (b) use a completely new structural ingredient. (a) is implausible without orders-of-magnitude LP improvement; (b) would be a breakthrough deserving the most adversarial scrutiny.

**For ADVERSARY**: the strongest attack on a claimed breakthrough is L4. If a paper claims $\chi_m \geq 6$ and does not produce a 6-chromatic UDG, ask: does the proof reduce to $m_1 < 0.20$? If not, what new structural ingredient enters?

**For SYNTHESIZER**: this coupling story should be the headline of the project as it matures. The four-architecture map is a useful research tool, but the no-progress-since-2018 pattern across architectures is best understood as a single combinatorial barrier, not four independent ones.

**Update (L7, Architecture 4)**: the coupling extends to Arch 4 as well, but inverted. Where L4 says Arch 2 *waits for* an Arch 1 breakthrough (a 6-chromatic UDG would unlock $\chi_m \geq 6$), L7 says Arch 4's main 2003 result *was already invalidated* by Arch 1's 2018 breakthrough. The Shelah-Soifer "$\chi(\mathbb{R}^2)$ depends on choice axioms" claim is *conditional* on all finite UDGs being 4-colorable; de Grey 2018 produced a 5-chromatic UDG and made the conditional vacuous. So three of the four architectures are now coupled to Arch 1 by the same combinatorial object: Arch 2 needs a $\chi \geq 6$ UDG to advance (L4), Arch 3 needs a $\chi_f \geq 6$ argument via $m_1 < 1/5$ density bounds (the same barrier in continuous form, L6), and Arch 4 lost its specific result to Arch 1 already (L7). Only Architecture 4's broader descriptive-set-theoretic / Borel-chromatic program is structurally independent of the missing UDG, and that program has not produced bounds on $\chi(\mathbb{R}^2)$ specifically.

**For ORCHESTRATOR**: the architecture portfolio (40% Arch 1, 25% Arch 2, 15% Arch 3, 10% Arch 4, 10% cross-cutting) should be revisited in light of L4. If Arch 1 and Arch 2 share an obstruction, parallel investment in both gives diminishing returns. Concentrating on Arch 1 (the source of the missing object) or on Arch 3's symmetry-fixed LP (the only independent route) may be more efficient. Arch 4 remains valuable for the structural / axiomatic framing but is unlikely to close the bound gap directly.

## What this does *not* claim

- We have not proved $\chi(\mathbb{R}^2) = 5$. The value is in $\{5, 6, 7\}$, and the coupling argument is consistent with all three.
- We have not improved any published bound. The Lean substrate is a re-verification at $\chi \geq 4$; the SAT verifications are reproductions of existing literature; the Bessel-LP $0.287$ is looser than OFV's $0.2688$.
- We have not found a 6-chromatic UDG. The coupling argument shows what *would* unlock $\chi \geq 6$ in both architectures, not how to find it.
- We have not addressed Architecture 4 (set-theoretic) in this synthesis. The Shelah-Soifer / Borel chromatic landscape is conceptually adjacent but does not engage with the missing-UDG barrier the same way.

## Open frontier as of 2026-05-25

| Question | Status | Path |
|----------|--------|------|
| $\chi(\mathbb{R}^2) \geq 6$? | open | find a 6-chromatic finite UDG (Arch 1) |
| $\chi_m(\mathbb{R}^2) \geq 6$? | open, same obstruction | either (a) Arch 1 finds the UDG above, or (b) push $m_1 < 0.20$ |
| $\chi(\mathbb{R}^2) = \chi_m(\mathbb{R}^2)$? | open; no published example of inequality on the plane | a structural theorem on the gap |
| $\chi_B(\mathbb{R}^2)$ between $\chi_m$ and $\chi$? | open; Arch 4 territory | descriptive set theory; not yet started |
| Field-theoretic search for $\chi \geq 6$ rings? | proposed in L1, not started | novel BUILDER direction |
| Reproduce Ambrus et al. $m_1 \leq 0.2470$? | published 2023, not yet replicated locally | requires their 23-point configuration + LP setup |
| Higher-order OFV LP hierarchy (DeCorte-OFV 2018) | published, not implemented | $\sim$ days of work |

## References

- **LEARNINGS source**: [`experiments/LEARNINGS.md`](../../experiments/LEARNINGS.md) entries L1 through L6.
- **Architecture 1 dossier**: [`docs/research_atlas/arch1_sat_lineage.md`](../research_atlas/arch1_sat_lineage.md).
- **Architecture 2 dossier**: [`docs/research_atlas/arch2_measurable_lineage.md`](../research_atlas/arch2_measurable_lineage.md).
- **Architecture 4 dossier**: [`docs/research_atlas/arch4_set_theoretic_lineage.md`](../research_atlas/arch4_set_theoretic_lineage.md).
- **Session records**: [`experiments/orchestrator_sessions/`](../../experiments/orchestrator_sessions/).
- **Verified Lean theorem**: `HadwigerNelson.four_le_chromaticNumberOfPlane` in [`lean/HadwigerNelson/MoserBridge.lean`](../../lean/HadwigerNelson/MoserBridge.lean).
