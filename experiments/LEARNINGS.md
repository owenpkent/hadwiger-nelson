# LEARNINGS

Synthesis surface for cross-architecture findings on the Hadwiger-Nelson problem. Updated whenever an experiment lands a structural result.

Format: one entry per finding. Lead with the finding, then context.

---

### L1. 6-chromaticity is "easy" in HN-adjacent variant problems but uniquely resists in the single-distance plane

**Architecture**: 1 (combinatorial / UDG), with cross-references to Architectures 2-3.

**Source**: SURVEYOR session 001, dossier [`docs/research_atlas/arch1_sat_lineage.md`](../docs/research_atlas/arch1_sat_lineage.md) §3.

**Finding**: A 6-chromatic two-distance graph in $\mathbb{R}^2$ exists at **16 vertices** (Parts 2020, [arXiv:2010.12656](https://arxiv.org/abs/2010.12656)). A 6-chromatic finite odd-distance graph in $\mathbb{R}^2$ exists explicitly (Parts 2022, [arXiv:2206.12632](https://arxiv.org/abs/2206.12632)). Six-coloring constructions on the off-diagonal continuum side have been extended (Mundinger-Pokutta et al., [arXiv:2404.05509](https://arxiv.org/abs/2404.05509), [arXiv:2501.18527](https://arxiv.org/abs/2501.18527)). By contrast, **no 6-chromatic single-distance UDG in $\mathbb{R}^2$ is known after 8 years of post-de-Grey SAT search**, and the smallest 5-chromatic single-distance UDG has been stuck at 509 vertices (Parts 2020) for 5 years.

**Why it matters**: the obstruction to $\chi(\mathbb{R}^2) \geq 6$ is not branching factor or SAT-solver strength. Both have been adequate to settle adjacent 6-chromatic questions with very small graphs. The obstruction is **structural rigidity of the unit-distance constraint inside $\mathbb{Q}(\sqrt{3}, \sqrt{11})$**: every closed-under-rotation ring extension $\mathbb{Z}[\omega_1, \omega_3, \omega_4, \zeta]$ tried by Polymath16 admits a homomorphic 5-coloring, and no $\zeta$ has been found that refuses one.

**Architectural implication**: the productive next experiment in Architecture 1 may be a **field-theoretic search** (which closed-under-rotation rings refuse 5-colorings?) rather than a *vertex-count search* (smaller and smaller 5-chromatic UDGs). The latter is hitting a structural floor; the former is unexplored.

**Wrong-approach status**: passes the $\mathbb{Q}^2$ detector. The finding only sharpens: $\mathbb{Q}^2$ admits $\chi = 2$; once you enlarge by $\sqrt{3}, \sqrt{11}$ you can force $\chi \geq 5$; the question is which further enlargement (if any) forces $\chi \geq 6$. The detector says the rigidity is field-theoretic, not topological-abstract.

**Cross-links**: Parts 2022 (odd-distance) sits adjacent to Architecture 2 (Davies et al. 2024 showed the odd-distance graph on $\mathbb{R}^2$ has infinite chromatic number, so the structural-overshoot test fails to engage). Mundinger-Pokutta et al. are methodologically adjacent to Architecture 3 (continuum / fractional / spectral methods extended by neural-network search of color classes).

---

### L2. The Moser spindle is structurally inessential to $\chi \geq 5$

**Architecture**: 1.

**Source**: Voronov, Neopryatnaya, Dergachev 2021, [arXiv:2106.11824](https://arxiv.org/abs/2106.11824). Summarized in [`docs/research_atlas/arch1_sat_lineage.md`](../docs/research_atlas/arch1_sat_lineage.md) §1.3.

**Finding**: There is a 64513-vertex 5-chromatic UDG in $\mathbb{R}^2$ that **does not contain the Moser spindle as a subgraph**. Every prior $\chi \geq 5$ UDG (de Grey 1581, Heule 553/529, Parts 525/517/510/509) used the Moser spindle as a load-bearing 4-chromatic motif; this construction shows that motif is not logically necessary.

**Why it matters**: opens a structurally new vertex-count question. The smallest *Moser-spindle-free* 5-chromatic UDG is unknown (the Voronov record at 64513 is far from optimal). This is a concrete BUILDER target with no published competitor since 2021.

**Wrong-approach status**: passes the $\mathbb{Q}^2$ detector (irrational coordinates in the rotation structure). Detector engagement noted as "likely passes pending full-PDF read" in the SURVEYOR dossier.

---

### L3. Multi-solver SAT agreement reproduces $\chi \geq 5$ at 510, 517, 553, 826 vertices

**Architecture**: 1 (combinatorial / UDG).

**Experiment(s)**: [`e1b_de_grey_skeleton.py`](combinatorial/e1b_de_grey_skeleton.py).

**Source data**: the [marijnheule/CNP-SAT](https://github.com/marijnheule/CNP-SAT) GitHub repository (Polymath16 / Heule lineage, fetched in session 003) and Polymath16 Dropbox links (de Grey 1585).

**Finding**: cadical195 and glucose4 both return UNSAT on the 4-coloring SAT instance for each of:

| Graph | Source | Vertices | Edges | cadical195 | glucose4 |
|-------|--------|---------:|------:|-----------:|---------:|
| Polymath16 G11 | Parts 2019 | 510 | 2504 | 78 s | 111 s |
| Heule G10 (SBP) | Heule 2019 | 517 | 2579 | 3 s | 3 s |
| Heule G8 | Heule 2018 | 529 | 2670 | 82 s | 119 s |
| Heule G7 (SBP) | Heule 2018 | 553 | 2722 | 2 s | 2 s |
| Heule intermediate | Heule 2018 | 826 | 4273 | 279 s | 805 s |
| **de Grey original** | de Grey 2018 | 1585 | 7909 | **5531 s** | **6456 s** |

Symmetry-breaking predicates (the `-sbp` variants) give 10-100× speedup. The 510 case is run without SBP (no pre-built CNF was provided in the repo) and still finishes in ~2 minutes.

**Why it matters**: two independent solver families agree on UNSAT for each graph. A SAT-solver soundness bug would need to corrupt both cadical (CDCL with chronological backtracking) and glucose (LBD-based CDCL with restart heuristic) in the same direction. Per the verifier discipline this is the strongest non-formal evidence available. Combined with formal verification of the Moser spindle in `lean/HadwigerNelson/`, the project now has end-to-end coverage of $\chi(\mathbb{R}^2) \geq 4$ formally and $\chi(\mathbb{R}^2) \geq 5$ via multi-solver SAT.

**Wrong-approach status**: all four graphs have coordinates in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ (verified algebraically by the Singular scripts in `sources/cnp-sat/check/`). The $\mathbb{Q}^2$ detector therefore passes uniformly across the lineage.

**Next**: de Grey 1585 is mid-run; pending. Future BUILDER experiments should focus on either (a) the field-theoretic search direction in L1, or (b) closing the gap to Parts 509 (not publicly available; would need to reproduce the minimization pipeline from the paper).

---

### L4. Architectures 1 and 2 share a single missing object: a 6-chromatic finite UDG

**Architecture**: 1 + 2 (cross-architectural coupling).

**Source**: SURVEYOR session 003, dossier [`docs/research_atlas/arch2_measurable_lineage.md`](../docs/research_atlas/arch2_measurable_lineage.md) §3 + §4 + §7 (discrepancy log item 5). Atlas correction also landed.

**Headline correction**: there is **no published improvement to $\chi_m(\mathbb{R}^2) \geq 5$ since Falconer 1981** (45 years). The widely-cited "$\chi_m \geq 6$" results are from (a) the hyperbolic plane $\mathbb{H}^2(d)$ for $d \geq 12$ (DeCorte-Golubev 2018, [arXiv:1708.01081](https://arxiv.org/abs/1708.01081)), or (b) restricted-region variants where color classes are convex tiles of bounded-away-from-zero area (Coulson 2002, Townsend-Woodall). Neither implies a measurable lower bound on canonical $\mathbb{R}^2$. The atlas's previous "$\chi_m \geq 6$" claim was a misattribution and has been corrected.

**Structural finding**: Falconer's $\chi_m \geq 5$ proof works in four steps: (1) assume a measurable 4-coloring, (2) Lebesgue density theorem extracts a high-density local region in one color class, (3) inscribe a rigid finite *Moser-spindle-like* configuration $S$ in the high-density region, (4) measure-theoretic intersection forces a monochromatic unit pair, contradiction. The load-bearing object in Step 3 is a *rigid finite Euclidean configuration that is at least 5-chromatic as a UDG in $\mathbb{R}^2$*.

To push the same machinery to $\chi_m \geq 6$, Step 3 would need a *6-chromatic finite UDG in $\mathbb{R}^2$*. **But no such object is known** (see L1, L2): Architecture 1 has been searching since de Grey 2018, and the Polymath16 / Heule / Parts lineage has only ever produced 5-chromatic UDGs. The current record (Parts 2020, 509 vertices) is 5-chromatic, and 6-chromaticity has resisted every search.

**The coupling**: the obstruction to $\chi_m \geq 6$ in Architecture 2 is at the lemma level **the same** as the obstruction to $\chi \geq 6$ in Architecture 1. Both architectures need the same missing finite combinatorial object. The measure-theoretic machinery does *not* substitute for the combinatorial search: it consumes a finite UDG and amplifies it via density. The amplification works at chromatic level 5 because de Grey's proof works at chromatic level 5; it would work at chromatic level 6 if and only if Architecture 1 first produces the requisite UDG.

**Implications**:

- The four architectures are not as independent as the project framing suggests. The strongest known cross-coupling is Arch 1 ⟷ Arch 2 via the missing 6-chromatic UDG.
- The "$\chi_m = \chi$" question is not just a coincidence-of-bounds: it is a structural prediction. If Arch 1 finds a 6-chromatic UDG, Falconer's machine immediately bumps Arch 2 to $\chi_m \geq 6$. If Arch 1 never finds one (because $\chi(\mathbb{R}^2) = 5$ is the true value), Arch 2 also stays at 5.
- The independent route to $\chi_m \geq 6$ would be via density: $m_1(\mathbb{R}^2) < 1/5 = 0.200$. Current best is $0.2470$ (Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023, [arXiv:2207.14179](https://arxiv.org/abs/2207.14179)). The gap from $0.247$ to $0.200$ is substantial; no published method approaches it.

**Wrong-approach status**: all measurable methods examined (Falconer 1981, OFV 2010, BNOFV 2009, Ambrus et al. 2023, DeCorte-Golubev 2018) engage with the 2D rotation group and Euclidean rigidity; none over-applies to $\mathbb{R}^1$. The cross-coupling is not a wrong-approach signal, it is a real mathematical constraint.

**Architectural implication for the project**: Architecture 2 cannot be advanced independently of Architecture 1. Investment in BUILDER work on $\chi_m \geq 6$ should either (a) explicitly contribute to the 6-chromatic UDG search (which is Arch 1 work in disguise), or (b) attack the $m_1$ density bound directly via E2.1/E2.2 in the surveyor's experimental menu. The OFV LP at $n = 2$ has reportedly been computed and gives only $\chi_m \geq 5$; whether a higher-order Lasserre / SOS hierarchy could break the barrier is open.

---

### L5. Vanilla Lovász $\vartheta$ on the de Grey lineage UDGs is structurally loose

**Architecture**: 3 (fractional / spectral), with cross-references to 1 and 2.

**Experiment**: [`e3a_lovasz_theta_polymath16_510.py`](fractional/e3a_lovasz_theta_polymath16_510.py).

**Finding**: the Lovász theta number of the Polymath16 510-vertex 5-chromatic UDG is

$$
\vartheta(G) = 170.235 \pm 10^{-3}\quad (\text{cvxpy} + \text{SCS}, \approx 11 \text{ min on a single SDP})
$$

giving the chromatic lower bound $\chi(G) \geq \lceil n/\vartheta \rceil = \lceil 510/170.235 \rceil = 3$. The known value is $\chi(G) = 5$ (e1b). The Lovász bound is **loose by 2 integer units**.

**Why it matters**: this calibrates expectations for Architecture 3 SDP work on Hadwiger-Nelson. Vanilla $\vartheta$ on a single large UDG does not recover the chromatic number for HN-style graphs. The independence number satisfies $\alpha(G) \leq \vartheta(G) = 170$, but the actual $\alpha(G)$ for this graph is probably $\leq 102$ (otherwise $\chi \leq n/\alpha < 5$ contradicts e1b). The **integrality gap** $\vartheta - \alpha \approx 68$ vertices is substantial: $\vartheta$ overestimates $\alpha$ by ~$67\%$.

**Cross-architectural implication**: the Matolcsi-Ruzsa-Varga-Zsámboki 2023 result $\chi_f(\mathbb{R}^2) \geq 4$ ([arXiv:2311.10069](https://arxiv.org/abs/2311.10069)) uses a 27-vertex graph and a finer LP framework, not vanilla $\vartheta$. The OFV / BNOFV LP / SDP family imposes rotation-invariance constraints on the Fourier multiplier, vastly reducing the search space and tightening the bound. *Vanilla theta on a fixed UDG is the wrong relaxation for HN; the right SDP is structurally constrained.*

**Implication for Architecture 3 work**: BUILDER attention should focus on the rotation-symmetric LP / SDP framework (OFV 2010, BNOFV 2009, MRVZ 2023) rather than on vanilla $\vartheta$ on larger and larger graphs. The path to $\chi_f \geq 4$ on $\mathbb{R}^2$ is through structured relaxations, not graph size.

**Wrong-approach status**: vanilla $\vartheta$ passes the $L^\infty$ detector (it's a graph invariant, not norm-specific), but it fails to *engage* with the Euclidean rotation-invariance of $\mathbb{R}^2$ that the OFV / BNOFV framework exploits. This is consistent with the looseness: theta cannot see structural information that the OFV LP cannot avoid using.

---

### L6. The rotation-invariant Bessel-LP cleanly beats vanilla Lovász $\vartheta$ on its own SDP playing field

**Architecture**: 3 (fractional / spectral, continuous side).

**Experiment**: [`e3b_ofv_bessel_lp.py`](fractional/e3b_ofv_bessel_lp.py).

**Finding**: a basic discretized Bessel-LP, parametrizing positive-type radial functions as $F(r) = \sum_k c_k J_0(2\pi r s_k)$ with $c_k \geq 0$ at $N = 2000$ frequencies, solves in **30 milliseconds** via HiGHS and gives the bound

$$
m_1(\mathbb{R}^2) \leq -F(1) / (F(0) - F(1)) \leq 0.402749 / 1.402749 \approx 0.287, \quad \therefore \chi_m(\mathbb{R}^2) \geq 4.
$$

The LP places all weight at the single frequency $s \approx 0.6087$, which corresponds to the first negative minimum of $J_0$ at $2\pi s \approx 3.83$ where $J_0 \approx -0.403$.

**Direct comparison to vanilla Lovász $\vartheta$ on the 510-vertex Polymath16 graph (L5)**:

| Method | Wall clock | Result | Integer bound |
|--------|-----------:|--------|--------------:|
| Vanilla $\vartheta$ via SDP on 510-vertex UDG | 644 s | $\vartheta = 170.24$, $n/\vartheta = 2.996$ | $\chi \geq 3$ |
| Rotation-invariant Bessel-LP on $\mathbb{R}^2$ | 0.03 s | $m_1 \leq 0.287$, $1/m_1 = 3.48$ | $\chi_m \geq 4$ |

The continuous rotation-invariant LP is $\approx 2 \times 10^4 \times$ faster *and* gives a strictly tighter integer bound on a stronger object ($\chi_m \geq \chi$). This is the empirical realization of L5's prediction: encoding rotation symmetry in the optimization is structurally the right move for HN.

**Why so much tighter**. The Lovász $\vartheta$ on a fixed graph $G$ optimizes over a $510 \times 510$ symmetric PSD matrix ($\sim 130\text{k}$ degrees of freedom) and sees only the edge structure. The Bessel-LP optimizes over a *1D radial profile* of the Fourier multiplier ($N$ real coefficients $c_k$) and sees the full continuous structure of $\mathbb{R}^2$, including the unit sphere as a single algebraic object rather than 2504 separate edges. The constraint set is vastly smaller in the right way: it forces the optimum to *only* consider $O(2)$-equivariant solutions.

**Distance to published**: OFV 2010 achieves $m_1 \leq 0.2688$ (so $\chi_m \geq 3.72$), and Ambrus et al. 2023 achieves $m_1 \leq 0.2470$ (so $\chi_m \geq 4.05$, integer 5). Our $0.287$ is loose by 0.02 vs OFV and 0.04 vs AC-MV-Z. Tightening would require a richer basis (Schwartz / Wiener-Hopf-style as in OFV) or higher-order correlations (DeCorte-OFV 2018). The single-frequency LP is the natural "first lesson" baseline.

**Implication**: future BUILDER work on $\chi_m$ / $\chi_f$ improvements should target the OFV / BNOFV / AC-MV-Z framework, not vanilla $\vartheta$ on bigger graphs. The 27-vertex MRVZ 2023 result $\chi_f \geq 4$ used exactly this principle: small graph, rotation-symmetric LP, tight bound.

**Wrong-approach status**: the Bessel-LP uses Bessel functions of order 0 (specific to $d=2$). In $d=1$, the analogous basis would be cosines $\cos(2\pi r s)$ (order $-1/2$), and the LP would recover the trivial $m_1(\mathbb{R}) \leq 1/2$, $\chi_m(\mathbb{R}) \geq 2$. The $\mathbb{R}^1$ detector passes. In $L^\infty$, the rotation-invariance assumption fails (the unit sphere is a square, not a circle), so the basis would need to be different; the method correctly does not transfer naively.

---

### L7. Architecture 1's 2018 breakthrough erased Architecture 4's main 2003 result about $\chi(\mathbb{R}^2)$

**Architecture**: 4 (set-theoretic / axiomatic), with cross-references to 1.

**Source**: SURVEYOR session, dossier [`docs/research_atlas/arch4_set_theoretic_lineage.md`](../docs/research_atlas/arch4_set_theoretic_lineage.md) §1.

**Headline correction**: the widely-cited "Shelah-Soifer: $\chi(\mathbb{R}^2)$ depends on choice axioms" is **not a theorem about $\chi(\mathbb{R}^2)$ at the current bound threshold**. It is a *conditional* theorem:

> **If** every finite unit-distance graph in $\mathbb{R}^2$ has $\chi \leq 4$, **then** $\chi(\mathbb{R}^2) = 4$ in ZFC and $\chi(\mathbb{R}^2) \geq 5$ in ZF + DC + LM.

**De Grey 2018 falsified the hypothesis** by exhibiting a 5-chromatic finite UDG (1581 vertices, since shrunk to 509 by Parts). The conditional is now vacuous as a statement about $\chi(\mathbb{R}^2)$. The Shelah-Soifer phenomenon (axiom-dependent chromatic numbers for unit-distance-*type* graphs) **survives** for artificial distance graphs (Shelah-Soifer 2003b for $\mathbb{R}^2$, Payne 2009 for UDG-subgraphs), but the specific punchline about the actual Hadwiger-Nelson graph $G_{\mathbb{R}^2}$ has not been re-established. Whether $\chi(G_{\mathbb{R}^2})$ itself depends on AC is **open**.

**Cross-architectural symmetry with L4**:

- **L4**: Architectures 1 and 2 share a missing object (a 6-chromatic finite UDG). Arch 2's $\chi_m \geq 6$ barrier *is* Arch 1's $\chi \geq 6$ barrier amplified by Falconer's machine.
- **L7**: Architecture 1's *2018 success* (the existence of a 5-chromatic finite UDG) *erased* Architecture 4's main 2003 statement about $\chi(\mathbb{R}^2)$.

The two architectures are coupled to Arch 1 in opposite directions: L4 says Arch 2 *waits for* an Arch 1 breakthrough; L7 says Arch 4's specific result *was already invalidated* by Arch 1's previous breakthrough. In both cases the combinatorial object (a finite $\chi \geq k$ UDG) is the load-bearing structure.

**The obvious replacement, unstarted**: the natural 2026 conditional would be

> **If** every finite unit-distance graph in $\mathbb{R}^2$ has $\chi \leq 5$, **then** $\chi(\mathbb{R}^2) = 5$ in ZFC and $\chi(\mathbb{R}^2) \geq ?$ in ZF + DC + LM.

The consequent on the LM side would presumably be $\chi(\mathbb{R}^2) \geq 6$ in ZF + DC + LM via Falconer-style machinery, but only if a measurable-coloring obstruction analogous to the 2003 one can be re-derived at the current bound. Nobody has published this. It is a concrete BUILDER target.

**Implication for the project**: Architecture 4 currently has no statement specifically about $\chi(\mathbb{R}^2)$ that is non-trivial post-2018. The architecture remains valuable for (a) the $\chi \leq \chi_B \leq \chi_m$ definability hierarchy, (b) the Borel chromatic question, and (c) the meta-mathematical framing of "which $\chi$ is the right one." But it does not currently engage with the bound-improvement question.

**Wrong-approach status**: Architecture 4 methods (Hamel basis under AC, Steinhaus under LM) are sensitive to which axiom system is in force. The $\mathbb{Q}^2$ detector applies in a refined way: $\chi(\mathbb{Q}^2) = 2$ in ZFC (Woodall, constructive); the same is true in ZF + DC + LM since the 2-coloring is explicit and measurable. So the Shelah-Soifer mechanism does not engage on $\mathbb{Q}^2$ controls. This is consistent with the architecture being orthogonal to the rationality test.

---

(no further entries yet; this is a young repository.)
