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

(no further entries yet; this is a young repository.)
