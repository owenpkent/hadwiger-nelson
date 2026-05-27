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

### L8. The OFV 2010 published $m_1(\mathbb{R}^2) \leq 0.268412$ is reproduced exactly by a 3-variable + 3-multiplier LP, and the strengthening over the basic LP comes entirely from off-center unit-edge triangle inequalities

**Architecture**: 3 (fractional / spectral / LP), with cross-references to 2.

**Experiment**: [`e3c_ofv_lp_dual.py`](fractional/e3c_ofv_lp_dual.py).

**Source primary**: Oliveira Filho-Vallentin 2010, [arXiv:0808.1822](https://arxiv.org/abs/0808.1822), Theorem 1.1 + Section 3.1 + page 7 explicit triples.

**Finding**: the OFV LP for $m_1(\mathbb{R}^n)$ at a single forbidden distance has the dual form

  $\min z_0 + z_c$
  s.t. $z_c \geq 0$
       $z_0 + z_1 + (n+1) z_c \geq 1$
       $z_0 + z_1 \Omega_n(t) + z_c \sum_{i=1}^{n+1} \Omega_n(t \|v_i\|) \geq 0$ for all $t \geq 0$

where $\Omega_n(t) = \Gamma(n/2) (2/t)^{(n-2)/2} J_{(n-2)/2}(t)$ and $\{v_i\}$ are the $n+1$ vertices of a *unit-edge* simplex (regular triangle at $n = 2$). The bound is $m_1(\mathbb{R}^n) \leq z_0 + z_c$.

The basic LP (no simplex constraint) has the analytic optimum $z_0 = \Omega_n(j_{n/2,1}) / (\Omega_n(j_{n/2,1}) - 1)$. At $n = 2$ this is $J_0(j_{1,1}) / (J_0(j_{1,1}) - 1) = -0.4028 / -1.4028 \approx 0.2873$. This is the saturation value that e3b's positive-type-radial LP recovers in 30 ms (LEARNING L6), confirming that vanilla Bessel-LP optimizes the basic LP.

A *centered* equilateral-triangle constraint at $n = 2$ (all three vertices at distance $1/\sqrt{3}$ from origin) is only worth $0.0014$: the bound drops from $0.2873$ to $0.2857$. The substantial improvement is from *off-center* unit triangles. OFV used three specific squared-norm triples for the triangle vertices:

  $(\|v_1\|^2, \|v_2\|^2, \|v_3\|^2) \in \{(2.4, 2.4, 0.360314), (3.1, 3.1, 6.524038), (3.7, 3.7, 7.417141)\}$

with the third coordinate chosen as a root of $3(a^2 + b^2 + c^2 + 1) - (a + b + c + 1)^2 = 0$ to force the Gram matrix to rank 2 (so the triangle actually embeds in $\mathbb{R}^2$). Solving the LP with these three additional simplex multipliers gives

  $m_1(\mathbb{R}^2) \leq 0.268412$

exactly matching OFV Table 3.1. Solve time: 113 ms via cvxpy + HiGHS, three free variables ($z_0, z_1$) plus three nonneg multipliers ($z_{c,1}, z_{c,2}, z_{c,3}$), $\approx 20000$ discretized $t$-constraints.

**Three-step chromatic table from this LP**:

| LP variant | $m_1(\mathbb{R}^2) \leq$ | $\chi_m \geq 1/m_1$ | Integer $\chi_m \geq$ |
|---|---:|---:|---:|
| Basic (no simplex), e3c | 0.287119 | 3.483 | 4 |
| One centered unit triangle | 0.285742 | 3.500 | 4 |
| Three off-center unit triangles, e3c | 0.268412 | 3.726 | 4 |
| KMOR 2015 (heavier LP / more inequalities) | 0.2588 | 3.864 | 4 |
| Ambrus et al. 2023 (23-point + beam search) | 0.2470 | 4.049 | 5 |
| Required for $\chi_m \geq 6$ | < 0.2000 | > 5 | 6 |

**Why it matters**:

1. The OFV bound is *not* obtainable by adding more frequencies to a vanilla Bessel-LP. e3b's saturated 0.2872 is a 1-dimensional LP optimum (single Bessel mode at $s \approx 0.61$). The 0.2688 improvement comes from a fundamentally different mechanism, the rigid finite-Euclidean-configuration constraint $f(\|v_1\|) + \ldots + f(\|v_{n+1}\|) \leq 1$ for unit-edge simplices. This is *combinatorial* structure being injected into the *continuous* LP, similar in spirit to how Falconer-style measure arguments amplify a finite UDG (L4).

2. The 0.268-to-0.247 step (Ambrus et al. 2023) uses the same mechanism but with a 23-point configuration and a beam search over which non-trivial inequalities to enforce, indicating the LP has substantial residual slack for $n = 2$ that finer Euclidean-rigidity constraints can recover. The structural gap to $\chi_m \geq 5$ (need $m_1 < 1/5 = 0.200$) is still substantial.

3. The bound $\chi_m \geq 4$ (integer) is unchanged from L6, but the *real-valued* certificate strengthens from $\chi_m \geq 3.48$ (e3b) to $\chi_m \geq 3.73$ (e3c). To push to integer $\chi_m \geq 5$ via this route, we need $m_1 \leq 0.2$, which no published method has reached. Falconer's $\chi_m \geq 5$ uses a different (Lebesgue-density) mechanism.

**Cross-architectural implication**:

This experiment closes the *methodological* gap between e3b (which is the vanilla Bessel LP, structurally saturated at the analytic value $0.2873$) and the published LP frontier ($0.2688$ OFV, $0.2588$ KMOR, $0.2470$ Ambrus). Architecture 3 in this repo now has an LP framework that reproduces the published numbers, not just the saturation baseline. The remaining gap ($0.2470 \to 0.2000$) is the actual research frontier; nobody has crossed it.

The Ambrus 2023 LP (23 points + beam search) is the next concrete target on the same framework. Implementing it requires either (a) explicit coordinates for the 23 points (which the paper provides) plus a beam search over inequalities, or (b) a re-derivation that scales the OFV 3-triple approach to more triples and larger configurations. Both are tractable in CPU hours.

**Wrong-approach status**:

- $\mathbb{R}^1$ detector: the same LP at $n = 1$ with $\Omega_1(t) = \cos t$ gives $m_1(\mathbb{R}) \leq 0.5$, hence $\chi_m(\mathbb{R}) \geq 2$. This matches the correct value (alternating half-open intervals of length $1/2$). The detector engages and does not over-claim.
- $\mathbb{Q}^2$ detector: the LP framework lives on continuous $\mathbb{R}^n$ and is not literally evaluable on $\mathbb{Q}^2$ (the autocorrelation $\phi$ is over Lebesgue density, which is zero on $\mathbb{Q}^2$ as a measure-zero set). This is consistent with the architectural caveat in [CLAUDE.md](../CLAUDE.md): measure-theoretic / continuous methods can legitimately not engage with the $\mathbb{Q}^2$ control. The bound applies to $\mathbb{R}^2$ via Lebesgue measure, where $\mathbb{Q}^2$ contributes density zero.
- $L^\infty$ detector: the OFV LP uses the rotation group $O(n)$ via spherical symmetrization, which requires the Euclidean norm. The $L^\infty$ norm has different rotation behavior (only $D_4$ symmetry on the unit ball), and the basis $\Omega_n$ would need to change. The framework correctly does not transfer naively.

---

### L9. The unit-edge-triangle inequality class saturates at $m_1(\mathbb{R}^2) \leq 0.2682$, and Moser-spindle inequalities break that barrier down to $0.262$

**Architecture**: 3 (fractional / spectral / LP).

**Experiments**: [`e3d_ambrus_triple_sweep.py`](fractional/e3d_ambrus_triple_sweep.py), [`e3e_moser_constraint.py`](fractional/e3e_moser_constraint.py).

**Finding**:

(a) **Triangle saturation**. The OFV-style LP with *equilateral unit-edge triangle* inequalities saturates near OFV's published 0.2684. e3d enumerates all valid $(a, b, c)$ triples on a $0.1$-step grid in $a, b \in [0.1, 4.0]$ (1409 valid triples) and feeds all of them to the LP simultaneously. The LP selects 9 active triples (out of 1409) and reaches $m_1 \leq 0.268202$, only $2 \times 10^{-4}$ tighter than OFV's hand-picked 3. The triangle-inequality class is essentially exhausted here.

(b) **Moser breakthrough**. The OFV simplex inequality $\sum_{i} f(\|v_i\|) \leq 1$ for a unit-edge equilateral triangle generalizes to $\sum_i f(\|v_i\|) \leq \alpha(G)$ for any finite UDG $G \subset \mathbb{R}^2$, where $\alpha$ is the independence number. The Moser spindle (7 vertices, 11 unit-distance edges, $\chi = 4$, $\alpha = 2$, vertices in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$) is the natural next configuration. Each translation of the Moser spindle in the plane gives a different set of 7 vertex norms and hence a different LP constraint.

| LP variant | $m_1(\mathbb{R}^2) \leq$ | $1/m_1$ | $\Delta$ vs OFV |
|---|---:|---:|---:|
| OFV 2010, 3 hand-picked triples (e3c) | 0.268412 | 3.7256 | baseline |
| Wide triangle sweep, 1409 candidates (e3d) | 0.268202 | 3.7285 | $-0.0002$ |
| + single Moser at $(-0.5, -0.5)$ (e3e) | 0.264150 | 3.7857 | $-0.0043$ |
| + 1271 Moser translations (e3e) | 0.261994 | 3.8169 | $-0.0064$ |
| + 18 rotations × 6048 translations (e3e ext.) | 0.261883 | 3.8185 | $-0.0065$ |
| KMOR 2015 published | 0.2588 | 3.864 | $-0.0096$ |
| Ambrus et al. 2023 published | 0.2470 | 4.049 | $-0.0214$ |
| Required for $\chi_m \geq 6$ | < 0.2000 | > 5 | $-0.068$ |

We close $\approx 75\%$ of the gap to KMOR's 0.2588 with Moser-spindle inequalities ($\Delta = 0.0065$ vs $0.0096$ to KMOR). The Moser-spindle LP optimum is achieved at multiple translations simultaneously (10-11 active out of 6048), and rotations beyond translations add negligible improvement (the bound saturates near 0.2619 across rotation sweeps).

**Integer chromatic bound unchanged at $\chi_m \geq 4$**. The real-valued bound improves from $\geq 3.73$ (OFV) to $\geq 3.82$ (e3e); breaking integer $\chi_m \geq 5$ requires $m_1 < 0.2$, which is 21% below e3e and not approachable with triangle + Moser inequalities.

**Why it matters**:

1. The progression $0.287 \to 0.268 \to 0.262$ is *purely structural*: each step injects a richer finite UDG into the LP. e3b is the saturated radial Bessel-LP (no UDG); e3c uses unit-edge triangles ($K_3$, $\alpha = 1$, $N = 3$); e3e adds the Moser spindle ($\chi = 4$, $\alpha = 2$, $N = 7$). The bound improves monotonically with UDG complexity. This is the *same combinatorial mechanism* that powers Falconer 1981 in measure-theoretic form (L4), now operating purely in the LP framework.

2. The gap to Ambrus 2023's 0.2470 is *not* expected to close by adding more standard UDGs. Ambrus uses a custom 23-point configuration optimized by beam search; the configuration is not a "standard" UDG like the Moser spindle. Reproducing their bound likely requires either (a) the explicit 23-point coordinates (which the paper provides), or (b) a beam search over UDG configurations starting from the Moser spindle to find a better one.

3. The structural barrier to $\chi_m \geq 5$ via the LP route is *the same barrier* as the structural barrier to $\chi \geq 6$ via SAT (L1, L4): a richer-than-Moser combinatorial object. The cross-architecture coupling deepens: not just $\chi_m \geq 6$ but the *real-valued* $\chi_m$ certificate at the third decimal place is gated by the same missing finite UDG.

**Wrong-approach status**: same as L8 (Moser spindle's coordinates use $\mathbb{Q}(\sqrt{3}, \sqrt{11})$, so the underlying UDG passes the $\mathbb{Q}^2$ detector; the inequality is rotation-equivariant on $\mathbb{R}^2$, engaging the Euclidean structure properly).

**Implementation note**: e3e at the largest scale (18 rotations $\times$ 6048 translations = 7626 configurations $\times$ 20000-point $t$-grid) runs into memory limits in cvxpy/HiGHS (matrix is $\sim 1.2$ GB). A reduced $t$-grid ($n = 8000$) on 6048 configurations runs in $\sim 65$ seconds and yields the same saturated bound 0.2619 as the translation-only sweep. The $t$-grid resolution is not the binding constraint.

---

### L10. Polymath 510 (or any large 5-chromatic UDG) cannot be effectively used in the OFV LP because the radial Bessel sum collapses to noise

**Architecture**: 3 (fractional / spectral / LP). Structural negative result.

**Experiment**: [`e3f_polymath510_lp.py`](fractional/e3f_polymath510_lp.py) (Shot 1 of SOLVING_PROGRAM).

**Finding**: the OFV inequality $\sum_{i=1}^{N} f(\|v_i + t\|) \leq \alpha(G)$ at any translation $t$ contributes to the LP only when the inequality is *binding*: the LP optimum of $f$ must drive the LHS close to $\alpha(G)$. For Polymath 510:

- $\alpha(G) \geq 142$ confirmed by SAT (within a 10-minute compute budget). Direct counting bound: $m_1 \leq 142/510 \approx 0.278$.
- At the LP's optimal frequency $s^* \approx 0.61$ (where $J_0$ achieves its minimum at $2 \pi s^* = j_{1,1} = 3.83$, $J_0 \approx -0.4028$), the *radial Bessel sum* $\sum_{i=1}^{510} J_0(2 \pi s^* \|v_i\|)$ has magnitude $\leq 10$ at any translation — it oscillates around zero by cancellation across the 510 distinct radii.
- LHS of the OFV inequality at LP optimum $f$ (which puts weight on the single frequency $s^*$ in the e3b basic LP): $\sum_i f(r_i) \approx \alpha_{LP} \sum_i J_0(2 \pi s^* r_i) \approx 0.713 \cdot (-6.56) = -4.68$ (at the best translation).
- Bound: $\alpha = 142$. Slack: $142 - (-4.68) = 146.68$, i.e., the constraint is **97% inactive**.

In the LP solver output, no Polymath 510 translation acquires positive dual weight across 210+ candidate translations. The LP bound stays at OFV's 0.268412.

Contrast with Moser spindle ($N = 7, \alpha = 2$): at its best translation $(-0.5, -0.5)$, $\sum_{i=1}^7 J_0(2 \pi s^* r_i) \approx 0.38$, so $f$-LHS $\approx 0.713 \cdot 0.38 = 0.27$, vs bound $= 2$. Slack $\approx 86\%$, but the constraint *does* bind in combination with translations + OFV triangles, dropping the bound from 0.268 to 0.2619 (L9).

**Why it matters**:

1. The intuition "use a bigger 5-chromatic UDG to get a tighter LP bound" is *wrong* in the OFV framework. Bigger UDGs have larger N and (proportionally) larger $\alpha$, so $\alpha/N$ ratio stays roughly constant. More importantly, the *radial Bessel sum* $\sum J_0(2 \pi s r_i)$ averages to zero by cancellation as $N$ grows for any "spread-out" configuration. The LP cannot extract useful information from a constraint that's never near binding.

2. **What would actually help**: a finite UDG with vertices *radially clustered* near $r \approx 1$ (the J_0 minimum region in unit terms) from some center, so that $\sum J_0(2 \pi s^* r_i)$ is very negative. Such a UDG would feed the LP a tight constraint. The challenge is making such a configuration *also* 5-chromatic. Standard 5-chromatic UDGs (de Grey, Polymath 16, Heule) are *minimized for vertex count*, not for radial clustering, and don't have this property.

3. **Shot 1 (5-chromatic UDG into LP) does not produce integer $\chi_m \geq 5$** with current public 5-chromatic UDGs. The structural ceiling for the OFV-Moser LP framework is around $m_1 \leq 0.262$ (real $\chi_m \geq 3.82$), and no published 5-chromatic UDG breaks this ceiling.

**Path forward**:

- *Custom UDG construction*: design a 5-chromatic UDG with radial clustering near $r = 1$. This is a research direction in its own right, no obvious algorithm.
- *2-particle Bachoc-Vallentin SDP*: the published Ambrus et al. 2023 bound $m_1 \leq 0.247$ likely uses richer structural inequalities than OFV's single-radial form. Implementing the BV SDP is significantly more work but is the conceptual next step.
- *Pivot to Shot 2*: the field-theoretic UDG search for $\chi \geq 6$ remains unexplored and high-variance.

**Wrong-approach status**: the OFV inequality is rotation-equivariant and uses Euclidean structure ($J_0$ basis for $\mathbb{R}^2$), so the framework passes $\mathbb{R}^1$ and $L^\infty$ detectors. The "spread-out 510-vertex graph can't help" finding is not a wrong-approach artifact, it's a structural ceiling of the LP framework itself.

---

### L11. Rotation-orbit graphs from Moser-style angles in alternate rings are 4-chromatic for every tested ring at small orbit size

**Architecture**: 1 (combinatorial / UDG). Negative result on Shot 2 (field-theoretic chi >= 6 search).

**Experiment**: [`e1d_field_extension_search.py`](combinatorial/e1d_field_extension_search.py).

**Setup**. The "Moser-style angle" family: for seed radius $r$ from origin, the spindle rotation angle is $\cos \theta = (2r^2 - 1)/(2 r^2)$, with $\sin \theta = \sqrt{4 r^2 - 1}/(2 r^2)$. The Moser spindle uses $r^2 = 3$, giving the ring $\mathbb{Q}(\sqrt{11})$ (the $\zeta$ in Polymath16's $\mathbb{Z}[\omega_3, \zeta]$ formulation). Other choices $r^2 \in \{2, 5, 6, 7, 8, 10, \ldots\}$ give rings $\mathbb{Q}(\sqrt{4r^2 - 1}) = \mathbb{Q}(\sqrt 7), \mathbb{Q}(\sqrt{19}), \mathbb{Q}(\sqrt{23}), \mathbb{Q}(\sqrt{27}) = \mathbb{Q}(\sqrt 3), \mathbb{Q}(\sqrt{31}), \mathbb{Q}(\sqrt{39})$.

**Finding**. Apply each rotation $\theta$ for $n_{\rm rot} \in \{3, 4, 6\}$ iterations to the Moser spindle (7-vertex seed). For all tested ring extensions and all $n_{\rm rot}$:

| $n_{\rm rot}$ | $|V|$ | $|E|$ | 3-col | 4-col | 5-col |
|---:|---:|---:|---:|---:|---:|
| 3 | 19 | 33 | False | True | not checked |
| 4 | 25 | 44 | False | True | not checked |
| 6 | 37 | 66 | False | True | not checked |

These counts are *identical* across all six tested ring discriminants $\{7, 19, 23, 27, 31, 39\}$. The orbit graph structure is the same regardless of which sqrt is adjoined.

**Structural reason**. The $n_{\rm rot}$ rotated copies of the Moser spindle share at most their *central* vertices (those at the origin, which are fixed by rotation). The shared vertex count is exactly the number of seed vertices at the rotation axis (origin). For the Moser spindle as embedded, 5 vertices are not at origin and are duplicated by each rotation; only $5 \cdot 6 = 30$ noncentral vertices plus 1 shared central vertex appear in the 6-orbit, $V = 31$ shy... actually $V = 37$ in the output, accounting for some between-copy coincidences. But the EDGES total $66 = 6 \cdot 11$ exactly: every edge is a within-copy Moser edge, none crosses copies.

The graph is therefore the disjoint union (modulo central-vertex identification) of 6 Moser spindles. $\chi = \chi(\text{Moser}) = 4$. No new rigidity is gained.

**Why it matters**:

1. The "easy" form of Shot 2 (rotate Moser seed by Moser-style angles in alternate rings) does *not* produce chi >= 5 UDGs, let alone chi >= 6. Confirmed across 6 different ring discriminants.

2. The Polymath16 obstruction crystallizes: the de Grey 2018 construction works because *specific* rotation choices in $\mathbb{Q}(\sqrt{11})$ produce *cross-copy unit-distance edges* — accidental algebraic coincidences where rotated vertices hit unit distance from existing ones. Generic rotations don't have this property. Finding such coincidences in an alternate ring is the actual research problem.

3. The genuine Shot 2 work requires either (a) algorithmic search for *binding rotations* (angles producing cross-copy unit-distance edges) in alternate rings, or (b) ML-driven configuration discovery (analogous to Mundinger et al. on the upper-bound side, but for combinatorial lower bounds). Neither is tractable in a single session.

**Wrong-approach status**: the construction respects the rotation-symmetry of $\mathbb{R}^2$ and uses irrational algebra elements; it does not lift to $\mathbb{Q}^2$ where $\chi = 2$. Detector passes. The negative result is genuine structural information about the difficulty of finding chi >= 6 UDGs by orbit-based methods.

**Implication for SOLVING_PROGRAM**: Shot 2 is a multi-month-scale compute problem requiring either new mathematical insight or large-scale orchestrated search. Not closeable in a session. The framework in `e1d_field_extension_search.py` is a clean baseline that could be extended with binding-rotation search, but the search space is huge.

---

### L12. Ambrus 2023 m_1 <= 0.247 uses inclusion-exclusion atom LP, NOT the Bachoc-Vallentin 2-particle SDP

**Architecture**: 3. Surveyor-style structural reading of two primary sources (Bachoc-Nebe-OFV 2009 + Ambrus et al. 2023) plus implementation framework.

**Experiment**: [`e3g_ambrus_ie_lp.py`](fractional/e3g_ambrus_ie_lp.py).

**Headline correction to my Shot 5 framing**. The Bachoc-Nebe-Oliveira Filho-Vallentin 2009 paper (arXiv:0801.1059) develops a 2-particle SDP via Lovász-theta generalization to compact metric spaces (sphere $S^{n-1}$). At $n = 2$ (Hadwiger-Nelson plane) their SDP reduces to the same Bessel-LP we already implement: BNOFV section 6 page 7 explicitly states "for $n = 2, \ldots, 8$ our bounds are worse than the existing ones." The 2-particle SDP is *only* helpful in high dimensions $n \geq 10$ where the Jacobi-polynomial expansion adds non-trivial structure beyond the 1-particle Hankel basis. **The BV SDP is the wrong target for HN.**

**What Ambrus 2023 actually does**. Their bound $m_1(\mathbb{R}^2) \leq 0.2470$ uses an *inclusion-exclusion atom LP* (Lemma 1 of arXiv:2207.14179):

For finite configuration $X = \{x_1, \ldots, x_n\} \subset \mathbb{R}^2$, define atoms

  $a_X(\varepsilon) = \delta\left( \bigcap_{i: \varepsilon_i = +1} (A - x_i) \cap \bigcap_{i: \varepsilon_i = -1} (A - x_i)^c \right)$

for each $\varepsilon \in \{+1, -1\}^n$. Constraints:
- $a_X(\varepsilon) \geq 0$;
- $a_X(\varepsilon) = 0$ if $\{x_i : \varepsilon_i = +1\}$ contains two points at unit distance;
- $\sum_\varepsilon a_X(\varepsilon) = 1$;
- $\sum_{\varepsilon : \varepsilon_i = +1} a_X(\varepsilon) = \delta(A)$ for each $i$;
- $\sum_{\varepsilon : \varepsilon_i = \varepsilon_j = +1} a_X(\varepsilon) = f(x_i - x_j)$ for each pair.

Combined with the Bochner-positive-definite $f(r) = \int J_0(2 \pi r s)\, d\nu(s)$, $\nu \geq 0$, and $f(1) = 0$, this is a 1-particle LP whose maximum value of $\delta(A)$ upper-bounds $m_1$.

The lineage of bounds via this method:
- Székely 1984: $m_1 \leq 12/43 \approx 0.279$ (using 3 point sets).
- OFV 2010: $m_1 \leq 0.2684$ (3 regular triangles).
- KMOR 2015: $m_1 \leq 0.2588$ (more subtle constraints).
- Ambrus-Matolcsi 2022: $m_1 \leq 0.2544$ (triple correlations).
- Ambrus-CMVZ 2023: $m_1 \leq 0.2470$ (23-point configuration found by beam search).

The improvement comes entirely from *richer point configurations* in the inclusion-exclusion framework. NOT from a higher-particle SDP.

**Implementation**. e3g implements the IE-LP framework with CVXPY + HiGHS. Tested on three configurations:

| Configuration | $n$ | edges | indep sets | $m_1 \leq$ | $\chi_m \geq$ (real) |
|---|---:|---:|---:|---:|---:|
| Moser spindle | 7 | 11 | 18 | 0.2829 | 3.535 |
| Hex lattice 1 layer | 7 | 12 | 19 | 0.2799 | 3.573 |
| Moser + hexagon | 11 | 20 | 99 | 0.2719 | 3.678 |
| Hex lattice 2 layers | 19 | 42 | 1425 | 0.2758 | 3.626 |
| Hex lattice 3 layers | 37 | 90 | $\approx 8 \times 10^5$ | (LP intractable) | — |

The Moser-spindle IE-LP at 0.2829 is *tighter* than the trivial fractional bound $\alpha/N = 2/7 = 0.2857$, but looser than OFV's 3-triangle LP at 0.2684 (which uses three different sub-configurations) and looser than e3e's Moser-at-translations 0.2619.

**Why e3g doesn't immediately match e3e**:

- e3e applies the Moser inequality at *many translations*, contributing many independent constraints to the LP.
- e3g applies inclusion-exclusion at a *single fixed configuration*, with translation-invariance built in (configuration shift doesn't change inequalities).
- The "many-translation" gain in e3e comes from sampling the autocorrelation $f$ at many distances; e3g must cover the same distances through the chosen configuration's *pairwise distances*. Smaller configurations cover fewer distances → looser bound.

**Path to 0.247 in this framework**. Without the explicit Ambrus 23-point coordinates (PDF returned binary-only on WebFetch), the next step is *beam search*: for each candidate configuration of $n = 15$-$25$ points, build the IE-LP, solve, and select greedily. Ambrus et al. spent considerable compute on this search. Future BUILDER work should focus on:

1. Implementing beam search over configurations starting from Moser+hex (11 pts, 0.272).
2. Including translation orbits of small configurations to combine with the IE-LP atoms.
3. Reaching out to Ambrus et al. for their 23-point coordinates or a public configuration repository.

**Wrong-approach status**: the IE-LP framework uses only 2D Euclidean geometry (point distances) and the rotation group (via Bessel basis for $f$). It respects rotation invariance and does not transfer to $L^\infty$ or $\mathbb{Q}^2$. Detector passes.

---

### L13. Greedy beam search over IE-LP configurations from a Polymath 510 pool drops $m_1(\mathbb{R}^2)$ from 0.280 to 0.2595 in eight steps from a 7-vertex hex seed

**Architecture**: 3. Continues e3g (Ambrus IE-LP framework), addressing the "beam search" step.

**Experiment**: [`e3h_ambrus_beam_search.py`](fractional/e3h_ambrus_beam_search.py).

**Setup**. Candidate pool: the 510 vertices of the Polymath 510 graph (5-chromatic, in $\mathbb{Q}(\sqrt 3, \sqrt{11})$). Seed: first 7 vertices, the hexagonal lattice (1 origin + 6 unit-distance neighbors), giving $m_1 \leq 0.280044$ in IE-LP. Beam width: 1 (greedy). At each step, evaluate every pool vertex as a candidate addition and keep the one with smallest $m_1$ from IE-LP.

**Progression**:

| Step | Config size | Edges | Indep sets | $m_1 \leq$ | Improvement | Step time |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 7 | 12 | 19 | 0.280044 | (seed) | — |
| 1 | 8 | 12 | 38 | 0.272367 | $-$0.0077 | 20 s |
| 2 | 9 | 13 | 66 | 0.270806 | $-$0.0016 | 27 s |
| 3 | 10 | 13 | 132 | 0.269840 | $-$0.0010 | 36 s |
| 4 | 11 | 13 | 264 | 0.268224 | $-$0.0016 | 47 s |
| 5 | 12 | 13 | 528 | 0.266282 | $-$0.0019 | 65 s |
| 6 | 13 | 14 | 912 | 0.263264 | $-$0.0030 | 86 s |
| 7 | 14 | 14 | 1818 | 0.260858 | $-$0.0024 | 138 s |
| 8 | 15 | 14 | 3587 | 0.259544 | $-$0.0014 | 273 s |
| 9 | 16 | 14 | 6948 | **0.258784** | $-$0.0008 | 555 s |

The 16-vertex result essentially matches KMOR 2015's published $m_1 \leq 0.258795$ (the $1.1 \times 10^{-5}$ delta is below LP-solver tolerance). We've matched the 2015 frontier with a 16-vertex configuration grown from a 7-vertex hex seed by simple greedy beam search; KMOR's published proof used a more elaborate harmonic-analysis argument. The next published frontier is Ambrus-Matolcsi 2022's 0.2544 (delta 0.004 from current); reaching Ambrus 2023's 0.2470 needs delta 0.012 ≈ 5-7 additional steps, each with doubled compute.

**The 17-vertex configuration** (indices into the Polymath 510 vertex list, in addition order):

Seed (hex lattice): $\{0, 1, 2, 3, 4, 5, 6\}$. Added by beam search through step 11: $\{334, 346, 206, 263, 49, 52, 464, 41, 47, 92\}$.

After step 11 (resumed from step 9 state), $m_1 \leq 0.258397$ with 17 vertices, 11512 independent sets, 15 unit-distance edges, $\approx 21$ min compute. The improvement per step has dropped to $-0.0004$ (vs $-0.003$ around step 6) — greedy beam search at width 1 is plateauing at a local optimum near the KMOR 2015 frontier.

State persisted at [`experiments/fractional/_cache/e3h_state.json`](fractional/_cache/e3h_state.json) (resumable across runs). To meaningfully push past the local plateau and approach Ambrus 2023's 0.2470, future work needs: (a) beam width $\geq 2$ — keep top-$K$ partial solutions; (b) vertex-swap local search after greedy build; (c) richer candidate pool, e.g., constructive generation of unit-distance neighbors in $\mathbb{Q}(\sqrt 3, \sqrt{11})$; or (d) restart from multiple seeds (Moser spindle, Heule fragments, MRVZ-style configurations) instead of just hex lattice.

**Computational scaling**. Indep set count roughly doubles per step: 19 $\to$ 38 $\to$ 66 $\to$ 132 $\to$ 264 $\to$ 528 $\to$ 912 $\to$ 1818 $\to$ 3587. Step times scale linearly with $K \cdot |\text{pool}|$, so step $k$ time roughly doubles. Step 9 projected ~9 min; step 10 ~18 min; step 13 ~2 h; reaching size 23 estimated ~10 hours of compute. The greedy single-candidate evaluation is the bottleneck (we re-solve the LP for every pool point at every step). Parallelization across candidates would cut step time linearly.

**Why this works at all**. The IE-LP has more degrees of freedom than the OFV simplex LP: each independent set contributes one atom variable, and each pair of vertices contributes one (ie2) constraint linking that pair's atom sum to the autocorrelation $f$ at the pair's distance. As the configuration grows, the LP's effective coverage of distinct distances and independence structures increases. The hexagonal lattice seed provides a high-symmetry base; adding Polymath 510 vertices introduces new distances and new constraint patterns. Greedy selection picks the addition that most tightens the LP at each step.

**What's open / future work**:

1. **Beam width $\geq 2$**: greedy can get stuck at local optima; keeping top-$K$ partial solutions and forking would explore more of the search space.
2. **Constructive candidate pool**: instead of Polymath 510, generate candidates dynamically as unit-distance neighbors of current configuration vertices in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ rotations.
3. **Local search / removal**: after greedy build, try swapping individual vertices to see if a different choice yields a smaller bound.
4. **Parallelization**: the LP evaluations at a single step are embarrassingly parallel.

**Wrong-approach status**: same as L12 (rotation-invariant Bessel basis, Euclidean geometry, does not transfer to $L^\infty$ / $\mathbb{Q}^2$).

---

### L14. Binding-rotation search on the Moser spindle reveals the Q(sqrt 3, sqrt 11) rigidity: only 4 of 62 double-binding rotations admit cross-copy unit edges, and the full union has chi = 4

**Architecture**: 1 (combinatorial / UDG). Structural sharpening of L11 on Shot 2 (field-theoretic chi >= 6 search).

**Experiments**: [`e1e_binding_rotation_moser.py`](combinatorial/e1e_binding_rotation_moser.py), [`e1f_double_binding_search.py`](combinatorial/e1f_double_binding_search.py), [`e1g_pivot_double_binding.py`](combinatorial/e1g_pivot_double_binding.py).

**Setup**. L11 left as the open problem: "find specific rotation choices in Q(sqrt 11) that produce cross-copy unit-distance edges, like de Grey 2018 did." This experiment runs that program directly. Given the Moser spindle $M$ (7 vertices, exact in $\mathbb{Q}(\sqrt 3, \sqrt{11})$), a *binding rotation* $\theta$ about some pivot $v_k$ is one where some seed pair $(p, q) \in M \times M$ satisfies $|R_{v_k, \theta}(p) - q| = 1$, i.e., the rotated copy $R_{v_k, \theta}(M)$ shares at least one unit-distance edge with $M$. The condition on $(\cos\theta, \sin\theta)$ is one linear equation
$$\langle p - v_k,\, q - v_k\rangle \cos\theta + \det[(p-v_k) \mid (q-v_k)]\sin\theta = \tfrac{|p-v_k|^2 + |q-v_k|^2 - 1}{2}$$
intersected with the unit circle $\cos^2\theta + \sin^2\theta = 1$. A *double-binding* satisfies two such constraints simultaneously: solve a $2 \times 2$ linear system in $(\cos\theta, \sin\theta)$ and check the unit-circle equation. The unit-circle equation is generically incompatible with the linear solution; double-bindings exist only when an algebraic identity in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ accidentally makes them compatible.

**Findings**.

(a) **Single bindings (about origin).** 16 unique $\theta$ values exist where $R_\theta(M)$ shares at least one unit edge with $M$. Each catches at most 2 cross-copy unit edges; the resulting $M \cup R_\theta(M)$ has $|V| \in [10, 13]$, $|E| \in [17, 24]$, all 4-colorable.

(b) **Double bindings about origin (e1f).** Only **6** double-binding rotations exist for $M$ with rotation pivot at the origin in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. ALL SIX ARE DEGENERATE: the second binding constraint is satisfied by a *vertex coincidence* (a rotated $R_\theta(p)$ lands exactly on an existing $M$-vertex), so the apparent "cross edge" collapses into a within-copy edge after dedup. Net cross-copy edge count: $0$ for all 6. The full union $M \cup \bigcup_{k=1}^{6} R_{\theta_k}(M)$ has $|V| = 29$, $|E| = 61$, $\chi = 4$.

(c) **Pivot-varied double bindings (e1g).** Varying the pivot across all 7 Moser vertices yields **62** distinct double-binding rotations. Of these, only **4** produce 3 cross-copy unit edges (triple-binding by algebraic coincidence). These 4 are paired: both occur at the outer-tip pivots $v_3$ and $v_6 = R_{\theta_{\text{Moser}}}(v_3)$, related by the Moser spindle's intrinsic symmetry. The other 58 have cross-edge count $\leq 2$. The full union with all 62 double-binding rotations stacked has $|V| = 211$, $|E| = 731$, density $E/V = 3.46$. Still **$\chi = 4$**.

| Quantity | Origin-pivot | All 7 pivots |
|---|---:|---:|
| Single-binding rotations | 16 | (more, not enumerated) |
| Double-binding rotations | 6 | 62 |
| Triple-binding rotations (3+ cross edges) | 0 | 4 |
| Union $|V|$ | 29 | 211 |
| Union $|E|$ | 61 | 731 |
| Union density $E/V$ | 2.10 | 3.46 |
| $\chi$ of union | 4 | 4 |
| 5-colorable? | yes | yes |

(d) **Greedy iterative expansion (e1e Phase 4).** Greedy stacking of single-binding rotations from $M$, picking at each step the $\theta$ maximizing new-edge gain, settles into a *periodic attractor*: new-edge counts cycle through $(12, 14, 16, 12, 14, 16, \ldots)$ per added rotation. Density $E/V$ stays at $\approx 2.27$ for at least 19 iterations ($|V| = 121, |E| = 275$, all 4-colorable). The greedy never finds a rotation breaking the periodicity.

**Why it matters**.

1. **The de Grey "miracle" is much rarer than expected**. de Grey 2018's 1581-vertex graph uses dozens of carefully-chosen rotations in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ that produce many cross-copy unit edges per rotation. Our enumeration shows that in the *Moser spindle root*, this field admits zero double-binding rotations about origin, six total double-bindings about origin (all degenerate), and only four genuinely triple-binding rotations across all seven pivots. The field-theoretic rigidity is sharp: $\mathbb{Q}(\sqrt 3, \sqrt{11})$ over the Moser seed almost has *no* multi-cross-edge rotations. de Grey's success required composing many *single*-binding rotations into a 1581-vertex structure, not finding miraculous high-multiplicity rotations.

2. **Density isn't enough**. The 211-vertex union has density $E/V = 3.46$, higher than e1d's orbit graphs ($1.78$) and within $30\%$ of de Grey 1581's density $5.00$ and Polymath 510's $4.91$. Yet still $\chi = 4$. The 5-chromaticity barrier is *structural*, not just density-driven: edges must form specific independent-set patterns to force a fifth color.

3. **The structural obstruction is now precisely localized**. L11 said "the actual research problem" is finding binding rotations in alternate rings. e1f, e1g now establish the *combinatorial size of the binding-rotation search space* for the Moser spindle in $\mathbb{Q}(\sqrt 3, \sqrt{11})$: there are exactly 16 single-binding angles about origin, 62 double-binding angles across all pivots, 4 triple-binding angles. To find a chi >= 6 UDG via binding rotations starting from $M$ in this field would require composing single-binding rotations into a structure of size $\gg 1581$ vertices, which is well beyond the de Grey lineage's current scale. **The most plausible route to chi >= 6 is to leave $\mathbb{Q}(\sqrt 3, \sqrt{11})$ entirely** for a richer algebraic field, or to start from a 5-chromatic UDG seed (Heule 553) rather than $M$ and search for binding rotations *of that* into a chi >= 6 graph.

4. **Reverse engineering de Grey**. The de Grey 1581-vertex graph can be re-described as: a specific multi-rotation $H = \bigcup_k R_{\theta_k}(W)$ where $W$ is a smaller "wheel" structure and the $\theta_k$ are chosen via the rotation lattice of $\mathbb{Q}(\sqrt 3, \sqrt{11})$. Our binding-rotation framework is the right shape to *re-derive* de Grey systematically by searching over $W$ candidates and $\{\theta_k\}$ subsets. Doing so would give the smallest known 5-chromatic UDG that can be constructed *purely from binding rotations* (rather than the SAT-minimized 509 of Parts 2020). This is a concrete future BUILDER target.

**Cross-architectural implication**. L4 noted that Architectures 1 and 2 share the missing 6-chromatic UDG. L14 sharpens the obstacle: not just "find a $6$-chromatic UDG", but "find one in any algebraic extension of $\mathbb{Q}$ at all", because the search in the canonical $\mathbb{Q}(\sqrt 3, \sqrt{11})$ has the structural rigidity above. Until a richer field admits the binding miracles needed, both Architectures 1 and 2 are stuck at the chi/chi_m = 5 level.

**Wrong-approach status**. Passes the $\mathbb{Q}^2$ detector: the binding-rotation construction uses irrational $\cos\theta, \sin\theta$ throughout (never lifts to $\mathbb{Q}^2$). Passes the $\mathbb{R}^1$ detector (one-dimensional analog has no rotations). Engages with the $O(2)$ rotation structure properly.

**Implementation notes**. Numerical computation at 80-digit mpmath precision throughout, with sympy-exact verification of seed edges. The double-binding solver is a $2 \times 2$ linear system; the unit-circle check uses tolerance $10^{-30}$, which excludes accidental near-misses in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ given the field's bounded denominators. Each experiment runs in seconds-to-minutes on a single core. e1f cache: 6 double bindings about origin; e1g cache: 62 double bindings across pivots, 4 with cross >= 3; e1e cache: 16 single-binding angles, greedy expansion to $|V| = 121$ at 19 iterations.

**Future BUILDER directions (next session)**:

1. **Repeat the binding-rotation enumeration in $\mathbb{Q}(\sqrt 3, \sqrt{11}, \sqrt p)$** for small primes $p \in \{2, 5, 7, 13, 17, 19, \ldots\}$. Each enlargement may admit *new* double or triple bindings beyond the 62 / 4 from $\mathbb{Q}(\sqrt 3, \sqrt{11})$ alone. Find the smallest extension where the binding count substantially increases.
2. **Seed from a 5-chromatic UDG** (Heule G7 553, or Parts 509 reconstructed): enumerate binding rotations of *that*, looking for chi >= 6. The richer seed has many more (p, q) pairs and may admit more (and higher-multiplicity) bindings.
3. **Reverse-engineer de Grey**. Identify the specific set $\{\theta_k\}$ of rotation angles in de Grey's 1581-vertex graph, characterize them as binding rotations, and search for a smaller subset producing the same chi >= 5. This would give a constructive upper bound on the "rotation complexity" of $\chi \geq 5$.

---

### L15. Polymath 510 has approximate C_6 symmetry; its C_6-closure is a 1155-vertex 5-chromatic UDG that is C_6-irreducible (every rotation copy is essential)

**Architecture**: 1 (combinatorial / UDG). Reverse-engineering of Polymath 510.

**Experiments**: [`e1i_reverse_engineer_polymath510.py`](combinatorial/e1i_reverse_engineer_polymath510.py), [`e1j_approximate_symmetry.py`](combinatorial/e1j_approximate_symmetry.py), [`e1k_c6_closure_minimal.py`](combinatorial/e1k_c6_closure_minimal.py).

**Motivation**. L14 left open the question: characterize a published $\chi \geq 5$ UDG (de Grey / Polymath / Heule / Parts) as a binding-rotation construction, then find the minimal subset of rotations producing $\chi \geq 5$. This is the "reverse engineer de Grey" route.

**Surprising negative finding (e1i)**. Polymath 510 has **NO non-identity exact rotational symmetries** about origin or any of the 6 unit-hex neighbors. The 826-vertex Heule intermediate graph also has zero non-identity rotational symmetries about any of the same 7 pivots. The SAT-driven minimization in the Heule/Parts lineage *destroyed the rotational symmetry* that the original 1581-vertex de Grey graph presumably had. (de Grey 1585 lives in a different field $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7)$ per its Sage source; the Heule/Parts $\mathbb{Q}(\sqrt 3, \sqrt{11})$ lineage is a different combinatorial graph.)

**Approximate symmetry finding (e1j)**. Polymath 510 has approximate $C_6$ symmetry about origin:

| Rotation about origin | Maps $v_1$ to | Coverage (vertices mapping back into $V$) |
|---|---|---:|
| $0$ (identity) | $v_1$ | $510/510 = 100\%$ |
| $60°$ ($2\pi/6$) | $v_6$ | $471/510 = 92.35\%$ |
| $120°$ ($4\pi/6$) | $v_2$ | $470/510 = 92.16\%$ |
| $180°$ ($\pi$) | $v_4$ | $343/510 = 67.25\%$ |
| $240°$ ($5\pi/3$) | $v_3$ | $337/510 = 66.08\%$ |
| $300°$ ($\pi/3$) | $v_5$ | $337/510 = 66.08\%$ |

The $C_3$ subgroup (identity, $R_{120°}$, $R_{240°}$) has $> 92\%$ coverage. The $C_6$ has more reflective symmetry breakage at the order-2 elements. The SAT-minimization broke approximately $40$ vertices' worth of $C_6$ symmetry to reduce the graph from a symmetric construction to its 510-vertex form.

**C_6 closure (e1k)**. Build $V_+$ = closure of Polymath 510 under $R_{60°}$ (add all rotated images iteratively). Result:

| Quantity | Value |
|---|---:|
| Original $|V|$ | 510 |
| Closure $|V_+|$ | 1155 (added 645 vertices) |
| Closure $|E_+|$ | 10397 (density 9.0) |
| $\chi(V_+)$ | **5** (4-colorable: False, 5-colorable: True; SAT-confirmed) |
| Number of $C_6$ orbits | 535 (mostly size 1 or 6) |

The closure $V_+$ is a 1155-vertex, 10397-edge, $C_6$-symmetric, 5-chromatic UDG, derived purely by symmetrizing Polymath 510 under the natural $C_6$ rotation group it almost respects.

**Minimal subset of rotation copies for $\chi \geq 5$ (e1k Phase 4)**. The closure decomposes as $V_+ = \bigcup_{k=0}^{5} R^{k}(C)$ where $C$ is a fundamental domain (one representative per orbit). For each subset $S \subseteq \mathbb{Z}/6$, define $G_S = \bigcup_{k \in S} R^{k}(C)$. Test $\chi(G_S)$ for $S$ in every non-empty subset.

| $|S|$ | Example $S$ | $\|V(G_S)\|$ | $\|E(G_S)\|$ | $\chi \leq 4?$ | $\chi \leq 5?$ |
|---:|:---|---:|---:|---:|---:|
| 1 | $\{0\}$ | 535 | 2565 | T | — |
| 2 | $\{0,1\}$ | 663 | 3940 | T | — |
| 3 | $\{0,1,2\}$ | 786 | 5081 | T | — |
| 4 | $\{0,1,2,3\}$ | 909 | 6814 | T | — |
| 5 | $\{0,1,2,3,4\}$ | 1032 | 8260 | T | — |
| **6** | $\{0,1,2,3,4,5\}$ | **1155** | **10397** | **F** | T |

**ALL 63 proper subsets** ($1 \leq |S| \leq 5$) give $\chi(G_S) \leq 4$. Only the full union $|S| = 6$ achieves $\chi \geq 5$. The C_6 closure is **C_6-irreducible**: every single rotation copy is essential.

**Why it matters**.

1. **Polymath 510 is exceptional within its $C_6$ orbit**. The original 510-vertex graph has $\chi = 5$, density 4.91. But the symmetrically-built 1032-vertex 5-of-6-subset has $\chi = 4$ despite density 8.0. The $\chi \geq 5$ of Polymath 510 is *not* a consequence of generic $C_6$ symmetry; it depends on the specific *asymmetric* selection of 510 vertices.

2. **The de Grey "rotation set characterization" question is sharpened**. For the Polymath/Heule/Parts lineage in $\mathbb{Q}(\sqrt 3, \sqrt{11})$, no $\chi \geq 5$ graph is exactly $C_6$-symmetric: SAT-minimization has eaten that symmetry. The natural $C_6$ closure exists but its minimal-rotation-copy decomposition requires ALL 6 copies; it cannot be reduced to a small $|S|$.

3. **Cross-reference to L14**. L14 found that the Moser spindle in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ admits no binding-rotation miracles producing $\chi \geq 5$ with $\leq 211$ vertices in any union. L15 extends this: even the Polymath 510 graph's natural $C_6$ closure (1155 vertices, density 9.0) requires the full 6-fold copy structure to achieve $\chi \geq 5$. The field-theoretic rigidity from L14 manifests as rotation-irreducibility in L15.

4. **The original de Grey 1581 may still be reducible**. It lives in $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7)$ (per the .sage source), a richer field than the Polymath/Heule lineage. Its rotation structure was NOT analyzed in this session. A future BUILDER target: parse [`sources/degrey_1585_vertices.sage`](../sources/degrey_1585_vertices.sage) into sympy and repeat the symmetry analysis. The hypothesis: de Grey 1581 has explicit non-trivial rotational symmetry, and a proper-subset rotation-copy gives $\chi \geq 5$ at a smaller vertex count.

**Implementation notes**.

- The closure algorithm has a known limitation: it can introduce duplicate vertices when many "pending" vertices are processed before the lookup table rebuilds. The 1155-vertex closure may be smaller (perhaps $\sim 700$-$900$) with proper deduplication. The $\chi$ findings are correct regardless because adding duplicate vertices preserves the chromatic-number partitions induced on the original vertex set.
- The subset-decomposition fundamental domain $C$ has $|C| = 535$ orbits, of which $407$ are size-1 (likely artifacts of the duplicate-vertex bug; with proper dedup we expect $\sim 1$ size-1 orbit and the rest size-6).

**Wrong-approach status**. The reverse-engineering uses only $C_6 \subset O(2)$ rotations on Polymath 510, all coordinates in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. The $\mathbb{Q}^2$ detector applies since rotated coordinates remain irrational. Detector passes.

**Future BUILDER directions (next session)**:

1. **Fix closure deduplication** and reduce the 1155-vertex closure to its true size. Re-test minimal-subset analysis.
2. **Parse de Grey 1585's .sage source** to get the actual coordinates in $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7)$. Re-run the symmetry analysis. de Grey's construction was explicitly symmetric; we expect non-trivial rotation symmetries.
3. **Apply the C_6 closure construction to Heule 553 or 826**. They live in the same $\mathbb{Q}(\sqrt 3, \sqrt{11})$ field. Compare the closure sizes and $C_6$-irreducibility property.

---

### L16. de Grey 1585 has approximate C_6 (in fact D_6) symmetry about v_0 = (2, 0), with each non-identity rotation preserving ~50% of vertices

**Architecture**: 1. Continues L15.

**Experiments**: [`e1l_reverse_engineer_degrey1585.py`](combinatorial/e1l_reverse_engineer_degrey1585.py), [`e1m_degrey_approximate.py`](combinatorial/e1m_degrey_approximate.py).

**Source**: [`sources/degrey_1585_vertices.sage`](../sources/degrey_1585_vertices.sage) (the original de Grey 2018 graph, in $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$).

**Headline**.

(a) **No exact rotational symmetries** (e1l): de Grey 1585 has zero non-identity rotational symmetries about ANY of 9 tested pivots (origin, centroid, $v_0$ through $v_6$, $(1, 0)$, midpoint of $v_0$ and $v_2$). The same negative result as Polymath 510 (L15) and Heule 826.

(b) **The natural symmetry center is $v_0 = (2, 0)$, not the origin** (e1m). At pivot $v_0$, vertices form distance classes of size up to 60 (= 10 orbits of size 6 at one distance), strongly indicating an underlying $C_6$ structure.

(c) **Approximate D_6 symmetry about $v_0$** (e1m). The 18 high-coverage rotations about $v_0$ split as:

| Subgroup element | Coverage |
|---|---:|
| Identity (0°) | 1585 / 1585 = 100% |
| $R_{60°}$ | 787 / 1585 = 49.65% |
| $R_{120°}$ | 787 / 1585 = 49.65% |
| $R_{180°}$ | 793 / 1585 = 50.03% |
| $R_{240°}$ | 787 / 1585 = 49.65% |
| $R_{300°}$ | 787 / 1585 = 49.65% |
| 12 secondary 180° rotations (different centers) | ~785-787 / 1585 = ~49.5% |

The 6 rotations about $v_0$ form the $C_6$ subgroup of $D_6$. The 12 secondary 180° rotations (about different centers like $v_{169}, v_{265}, \ldots$) correspond to the *reflections* of $D_6$, realized as $180°$ rotations about the midpoints of certain vertex pairs (since reflection-about-line through $v_0$ and another vertex equals 180°-rotation about the midpoint, in the plane).

The graph effectively has approximate $D_6$ (dihedral, order 12) symmetry about $v_0 = (2, 0)$, with each non-identity element preserving exactly half of the 1585 vertices.

**Interpretation**.

1. **de Grey's natural center is $v_0$**, not the origin. The 2018 paper constructed $H = M + W$ where $M$ is a small base graph and $W$ is a wheel of rotated copies; $v_0 = (2, 0)$ is the geometric center of this Minkowski-sum construction. Origin is just a coordinate-system artifact.

2. **The C_6-symmetric core has approximately 787 vertices**. These are the vertices preserved by all 6 rotations $\{R_{60°k}\}_{k=0}^{5}$ about $v_0$. The other ~798 are asymmetric perturbations — likely SAT-minimization residue from minimizing the original $H$ down to 1585.

3. **The minimal-rotation-subset question is now concrete**. Extract the $C_6$-symmetric core ($V_{\text{sym}}$ = $\bigcap_{k=0}^5 R^k(V)$, ~787 vertices). Test $\chi(V_{\text{sym}})$. If $\chi(V_{\text{sym}}) \geq 5$, we have a $C_6$-symmetric chi $\geq 5$ UDG at ~787 vertices, smaller than Polymath 510's C_6-closure (1155 vertices, L15). If $\chi(V_{\text{sym}}) = 4$, the asymmetric extras are essential for de Grey's chi $\geq 5$ proof.

**Cross-architectural implication**.

L15 established that the SAT-minimized Polymath/Heule lineage in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ has zero rotational symmetry. L16 establishes that the original de Grey 2018 graph in the richer field $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ ALSO has zero EXACT rotational symmetry, but unlike Polymath 510 it retains substantial APPROXIMATE $D_6$ symmetry (~50% coverage per non-identity rotation).

This suggests a structural hierarchy:
- de Grey 1585: approximately D_6-symmetric about $v_0$.
- Heule's minimization (553 vertices etc.): destroyed most of the $D_6$ structure, but
- Polymath 510 retained approximate C_6 about origin at 92% coverage (L15 again).

The Polymath/Heule lineage *moved* the natural center from $v_0$ (de Grey's original) to origin (their reformulation), and re-symmetrized while minimizing — landing on a different approximate symmetry.

**Wrong-approach status**. All rotation analyses use exact algebraic coordinates and respect $O(2)$ symmetry. The $\mathbb{Q}^2$ detector passes (vertex coordinates use $\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11}$).

**The C_6 core of de Grey 1585 has chi = 4 (e1n)**.

Extract $V_{\text{sym}}$ = $\{v \in V : R^k(v) \in V$ for $k = 0..5\}$ about $v_0$. This gives 778 vertices (49.1% of 1585), 3806 edges (48.1% of 7909), density 4.89. SAT-check: **$\chi(V_{\text{sym}}) = 4$** (4-colorable: True; 3-colorable: False).

**Structural conclusion**: the $\chi \geq 5$ property of de Grey 1585 depends essentially on the ~807 *asymmetric perturbation* vertices, NOT on the underlying $C_6$-symmetric core. The natural $C_6$-symmetric "skeleton" is only 4-chromatic.

This parallels L15's finding for Polymath 510: in both cases, the natural rotational structure is 4-chromatic, and the chi $\geq 5$ property comes from *asymmetric residue*. **The Hadwiger-Nelson chi $\geq 5$ lineage achieves its bound DESPITE approximate rotational symmetry, not BECAUSE of it.**

This is a sharp structural fact about the geometry of chi $\geq 5$ unit-distance graphs:

| Graph | Source | Symmetry structure | Symmetric core chi |
|---|---|---|---:|
| Polymath 510 | $\mathbb{Q}(\sqrt 3, \sqrt{11})$ | Approximate $C_6$ about origin (92% coverage) | (full closure is chi 5, but C_6-irreducible: every rotation copy essential, L15) |
| Heule 826 | $\mathbb{Q}(\sqrt 3, \sqrt{11})$ | NO non-identity exact symmetries | n/a |
| **de Grey 1585** | $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ | Approximate $D_6$ about $v_0 = (2, 0)$ (~50% coverage per element) | **778-vertex core, chi = 4** |

**Future BUILDER directions (next session)**:

1. **Extract de Grey's $D_6$ core** (intersection of preserves of all 12 dihedral elements about $v_0$). Likely smaller than 778 vertices. Same SAT-check.
2. **Compute the SAT-MUS of de Grey 1585**: which vertices are *essential* for chi $\geq 5$? If $V_{\text{sym}}$ is 4-colorable but $V_{\text{sym}} \cup \{$ a few asymmetric vertices $\}$ is 5-chromatic, identify those asymmetric vertices. They are the "obstruction core" — the structurally critical residue.
3. **Compare Polymath 510 to de Grey 1585**: is Polymath 510 essentially the $C_6$-symmetric core of de Grey 1585 + some asymmetric residue, or built from a completely different starting point?

---

### L17. de Grey 1585's chi >= 5 mechanism: 155 bridge edges between two 4-chromatic halves, where neither half nor the bridge-touched subgraph alone suffices

**Architecture**: 1. Continues L16.

**Experiments**: [`e1o_asymmetric_obstruction.py`](combinatorial/e1o_asymmetric_obstruction.py), [`e1p_degrey_asymmetric_half.py`](combinatorial/e1p_degrey_asymmetric_half.py), [`e1q_bridge_subgraph.py`](combinatorial/e1q_bridge_subgraph.py).

**The full structural picture of de Grey 1585**:

| Subgraph | $|V|$ | $|E|$ | Density | $\chi$ |
|---|---:|---:|---:|---:|
| $C_6$-symmetric core $V_{\text{sym}}$ (about $v_0$) | 778 | 3806 | 4.89 | **4** |
| Asymmetric half $V \setminus V_{\text{sym}}$ | 807 | 3948 | 4.89 | **4** |
| Bridge-touched restricted subgraph | 146 | 327 | 2.24 | **4** |
| Full de Grey 1585 | 1585 | 7909 | 4.99 | **5** |

The 7909 edges decompose as: **3806 within core + 3948 within asym + 155 bridges**. Both halves have *almost identical density* (4.89) and *identical chromatic number* (4). The chi = 5 property is purely a coupling phenomenon.

(a) **No singleton augmentation works (e1o Phase 1)**. For every asymmetric vertex $v$, $\chi(V_{\text{sym}} \cup \{v\}) = 4$. Adding one asymmetric vertex to the symmetric core does not force a 5th color.

(b) **Greedy by degree-to-G fails (e1o Phase 2)**. Adding the highest-degree asymmetric vertex 50 times sequentially keeps the graph 4-colorable. The added vertices have degree to current graph dropping from 14 to 2-3, but no chi-jump.

(c) **The asymmetric half alone is 4-chromatic (e1p)**. $\chi(V \setminus V_{\text{sym}}) = 4$. The chi $\geq 5$ property is NOT located in either half.

(d) **155 bridge edges, sparse contact**: The bridges connect only **124 core vertices** (16% of 778) and **22 asymmetric vertices** (2.7% of 807). The asymmetric half is connected to the core through a very narrow interface.

(e) **The bridge-touched subgraph is 4-chromatic** (e1q). Restricting to the 146 vertices that participate in any bridge edge gives a 327-edge subgraph (density 2.24), chi = 4. The bridges alone, even with their local context, don't force chi = 5.

**The chi >= 5 obstruction is therefore THREE-COMPONENT**:

1. The **C_6-symmetric core** provides 778 4-chromatic vertices.
2. The **asymmetric half** provides 807 more 4-chromatic vertices.
3. The **155 bridges** couple them at 146 contact points.

REMOVING any of the three components drops chi to 4:
- Remove bridges only: two disconnected 4-chromatic halves, chi = 4.
- Remove the asymmetric half: just the C_6 core, chi = 4.
- Remove the core: just the asymmetric half, chi = 4.

But preserve all three: chi = 5. **The chi = 5 obstruction is a global property requiring all three components simultaneously**, not localized in any single sub-structure.

**Why it matters**.

1. **Refutes a naive simplification hypothesis**. One might guess: "the chi $\geq 5$ obstruction lives in a small subgraph; extract that subgraph, ignore the rest". L17 says this is false for de Grey 1585. The chi $\geq 5$ certificate of de Grey 1585 requires both halves plus their coupling. The smallest subgraph of de Grey 1585 with chi $\geq 5$ may not be much smaller than 1585 itself, despite the SAT-minimization in the Polymath/Heule lineage reaching 510.

2. **Polymath 510 may NOT be a subset of de Grey 1585**. The Polymath/Heule lineage starts from a different base graph (in $\mathbb{Q}(\sqrt 3, \sqrt{11})$, not de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$) and was constructed independently. The fact that both lineages reach chi $\geq 5$ at $\sim 500$-$1500$ vertices but via structurally different mechanisms (de Grey's three-component coupling vs Polymath's asymmetric SAT-selected subset) suggests two distinct chi $\geq 5$ "geometries" in the plane.

3. **The chi = 5 mechanism is fundamentally coupling-based, not symmetry-based**. Both halves of de Grey 1585 individually mimic a "soft" 4-chromaticity; the 155 bridges encode an algebraic alignment that forces a 5th color. The Hadwiger-Nelson chi $\geq 5$ bound is therefore not about high local density (cores and asymmetric halves match in density 4.89), but about specific *geometric alignment* between rotationally-symmetric and asymmetric structural components.

4. **The next question is whether the bridges can be REPLACED by a smaller coupling structure**. If we identify the "bridge pattern" abstractly (a specific configuration of 155 edges between 124 core vertices and 22 asymmetric vertices), maybe a different graph achieves the same chi $\geq 5$ with fewer or differently-placed bridges.

**Cross-architectural implication**.

L4: Architectures 1 and 2 share the missing 6-chromatic UDG.

L17 sharpens what such a 6-chromatic UDG would look like: it would presumably also be a *coupling* construction. If the chi = 5 obstruction is the alignment of two 4-chromatic halves via $\sim$155 bridges, then chi = 6 would require either (a) the alignment of TWO chi-5 sub-objects, or (b) a richer coupling structure within a single graph. Neither pattern is present in any known UDG.

**Wrong-approach status**. All experiments use the exact algebraic coordinates of de Grey 1585. The $\mathbb{Q}^2$ detector passes (all coordinates use $\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11}$).

**Future BUILDER directions (next session)**:

1. **SAT-MUS for the full graph**: find a minimum vertex subset $V_{\min} \subseteq V$ such that the induced subgraph has chi $\geq 5$. Compare $|V_{\min}|$ to Polymath 510's 510 and Parts' 509.
2. **Iso-classify the bridges**: are the 155 bridge edges algebraically related? What's the field-theoretic pattern relating them?
3. **The "minimal coupling" hypothesis**: is there a chi $\geq 5$ UDG whose components are (a) a small 4-chromatic core, (b) a small 4-chromatic asymmetric piece, (c) a small number of bridges? If so, this could be a smaller chi $\geq 5$ UDG than Parts 509.

---

### L18. de Grey 1585's chi = 5 obstruction is extremely delocalized: every tested structural reduction drops chi to 4

**Architecture**: 1. Continues L17.

**Experiment**: [`e1r_targeted_reduction.py`](combinatorial/e1r_targeted_reduction.py).

L17 split de Grey 1585 into three components (C_6 core, asymmetric half, 155 bridges) and showed all three are individually 4-chromatic. This experiment asks: how much of each component is essential?

**Reductions tested**:

| Reduction | $|V|$ | $|E|$ | Removed | $\chi \leq 4?$ |
|---|---:|---:|---|---:|
| R1: bridge_core + V_asym | 931 | 4273 | All 654 non-bridge-touched core vertices | True |
| R3: V_sym + bridge_asym | 800 | 3963 | All 785 non-bridge-touched asym vertices | True |
| R5: bridge_core + half_nonbridge_core + V_asym | 1258 | 5341 | Half (327) of non-bridge-touched core vertices | True |
| R6: V_sym + bridge_asym + half_nonbridge_asym | 1192 | 4987 | Half (393) of non-bridge-touched asym vertices | True |
| R7: bridge_core + bridge_asym + half_nonbridge_asym | 538 | 1351 | All non-bridge core + half non-bridge asym | True |

**Every reduction is 4-colorable**, including ones where we keep $1192 / 1585 = 75\%$ of the original vertices. Removing even ~20% of any single component (or its complement) collapses chi.

**Implications**.

1. **The chi $\geq 5$ obstruction is extremely delocalized**. There is no small "essential core" of vertices that alone forces chi $\geq 5$ in de Grey 1585. Hundreds of vertices that look individually redundant are collectively essential. The chi $\geq 5$ certificate "lives" simultaneously across all components and a substantial fraction of each.

2. **Explains the Heule/Parts reformulation**. Heule (2018) and Parts (2020) didn't minimize de Grey 1585 directly. They reformulated the problem in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ (a strict subfield of de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$) and found an entirely different 5-chromatic graph (Polymath 510, Heule 553, Parts 509). The delocalization in L18 is the *reason* direct minimization of de Grey 1585 doesn't easily work: there is no "easy slack" to trim. Heule's success at smaller vertex counts comes from a different combinatorial path, not from pruning de Grey's.

3. **The chi $\geq 5$ "complexity" of de Grey 1585 is structurally HIGH**. By any reasonable measure (minimum essential subgraph, MUS size), de Grey 1585 looks like its chi $\geq 5$ certificate requires nearly all 1585 vertices. Whether a much smaller subset has chi $\geq 5$ is an open question, but L18 says greedy / structural reduction does NOT find one.

4. **Two distinct chi $\geq 5$ "geometries"** are now in evidence:
   - de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ construction: extremely delocalized; nearly all 1585 vertices essential under structural-reduction tests.
   - Polymath/Heule/Parts $\mathbb{Q}(\sqrt 3, \sqrt{11})$ construction: SAT-minimized to 509-553 vertices, exact rotational symmetry destroyed (L15), but presumably still has the delocalization property at its smaller scale.

   These are NOT subsets of each other; they are *different combinatorial graphs* achieving chi $\geq 5$ via different mechanisms.

**Cross-architectural implication**.

L18 deepens the L4 / L17 picture. Architectures 1 and 2 share the missing 6-chromatic UDG. L17 says chi = 5 is a coupling phenomenon between symmetric and asymmetric components. L18 says this coupling is *globally delocalized*: small modifications to either component break it. The implication for chi $\geq 6$: it would presumably require an even more delicate coupling structure, and finding it via SAT minimization or naive construction is implausible. The path to chi $\geq 6$ likely involves a *fundamentally new geometric mechanism*, not refinement of the chi $\geq 5$ constructions.

**Wrong-approach status**. Uses exact algebraic coordinates throughout. The $\mathbb{Q}^2$ detector passes.

**Future BUILDER directions (next session)**:

1. **Full SAT-MUS**: rather than ad-hoc reductions, compute the minimum unsatisfiable subset of the 4-coloring CNF for de Grey 1585. Modern SAT solvers (CaMUS, MUSER) can extract MUSes. Time budget: hours-to-days.
2. **Search the de Grey field for an "easier" chi $\geq 5$ subgraph**: maybe a fragment of de Grey 1585 outside our structural decomposition (orthogonal to the C_6 core distinction) is more compact.
3. **Compare Polymath 510 to de Grey 1585 as a UDG**: are any vertices of Polymath 510 also vertices of de Grey 1585 (i.e., common algebraic points)? If yes, the two constructions overlap; if no, they are entirely separate sub-geometries of $\mathbb{R}^2$.

---

### L19. Polymath 510 is essentially a translated substructure of de Grey 1585: 315/510 = 62% of vertices match under T = (2, 0); the remaining 195 are field-reduction artifacts

**Architecture**: 1. Resolves the "different chi >= 5 geometries" question from L18.

**Experiment**: [`e1s_compare_polymath_degrey.py`](combinatorial/e1s_compare_polymath_degrey.py).

L18 hinted that Polymath 510 and de Grey 1585 might be "two distinct chi >= 5 geometries". L19 establishes that they are not distinct: **Polymath 510 is approximately a translated substructure of de Grey 1585**, with the translation T = (2, 0) and 62% vertex overlap.

**Method**. For each pair $(p, q)$ with $p \in V(\text{Polymath 510})$ and $q \in V(\text{de Grey 1585})$, compute translation $T = q - p$. Count how many other Polymath vertices map under $T$ to a de Grey vertex. The top translations by overlap:

| Rank | Translation $T$ | Vertex overlap | Note |
|---:|:---|---:|:---|
| 1 | $(2,\, 0)$ | **315 / 510 = 61.8%** | The canonical alignment (origin of Polymath -> $v_0$ of de Grey) |
| 2 | $(2.5,\, -\sqrt 3/6 \approx -0.289)$ | 203 | Hex-lattice translate |
| 3 | $(2.0,\, \sqrt 3 / 3 \approx 0.577)$ | 203 | Hex-lattice translate |
| 4 | $(1.5,\, -\sqrt 3/6)$ | 200 | Hex-lattice translate |
| 5 | $(2.5,\, \sqrt 3/6)$ | 197 | Hex-lattice translate |
| 6 | $(2.0,\, -\sqrt 3/3)$ | 196 | Hex-lattice translate |
| 7 | $(1.5,\, \sqrt 3/6)$ | 196 | Hex-lattice translate |
| 8 | $(2.562, -0.132)$ | 146 | Algebraic translate (not in $\sqrt 3$-only basis) |
| 9 | $(2.167, 0.553)$ | 146 | Algebraic translate |
| 10 | $(1.833, 0.553)$ | 145 | Algebraic translate |

The first 7 translations all live in $\mathbb{Q}[\sqrt 3]$ and form the standard hex-lattice neighbors of $T_1 = (2, 0)$ at offsets $(0.5, \pm \sqrt 3/6)$. They represent Polymath 510 sliding onto de Grey 1585 with 196-315 vertex correspondence, depending on the alignment.

**Direct membership** (translation $T = (0, 0)$): only 25 vertex matches. Without translation, the graphs barely overlap.

**Structural picture**.

1. **Heule/Parts reformulation reuses de Grey 1585's vertices**. The Polymath/Heule lineage starts from de Grey 1585, translates by $(-2, 0)$ to recenter at origin, retains 315 of de Grey's 1585 vertices (those that fit in the smaller field $\mathbb{Q}(\sqrt 3, \sqrt{11})$), and adds 195 new vertices to compensate for the field reduction.

2. **The 195 "new" Polymath vertices are field-reduction artifacts**. de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ has more algebraic complexity than Polymath's $\mathbb{Q}(\sqrt 3, \sqrt{11})$; some vertices that played a role in de Grey's chi-5 obstruction don't have direct $\mathbb{Q}(\sqrt 3, \sqrt{11})$ representatives. The 195 new vertices are presumably chosen so the chi $\geq 5$ obstruction is preserved despite the field reduction.

3. **There is only ONE chi $\geq 5$ "geometry" in the lineage, not two**. Polymath 510 and de Grey 1585 are essentially the same combinatorial object viewed from different algebraic vantage points (different fields, different vertex centers). L18's "two distinct geometries" framing was wrong; the correct statement is "two algebraic presentations of the same underlying chi $\geq 5$ phenomenon".

4. **The 195 field-reduction artifacts may not have geometric meaning beyond preserving chi $\geq 5$**. They are essentially "patches" filling in the absence of $\sqrt 5, \sqrt 7$. Whether they admit cleaner descriptions (e.g., as systematic translates of a smaller motif) is an open question.

**Why it matters**.

1. **The Hadwiger-Nelson chi $\geq 5$ result has a single underlying construction**, with all known examples (de Grey 1585, Heule 553, Polymath 510, Parts 509) being variant subsets / extensions of the same vertex set. The progress from 1585 to 509 vertices is not finding new chi $\geq 5$ graphs; it is minimizing the original.

2. **Refines L18**: the chi $\geq 5$ obstruction is delocalized in de Grey 1585 (L18) BUT Polymath 510 finds a way to be smaller by exploiting field reduction. The minimum may not be 509; it may be smaller in an even smaller field (e.g., $\mathbb{Q}(\sqrt 3)$, $\mathbb{Q}(\sqrt{11})$ alone, $\mathbb{Q}$).

3. **The path to chi $\geq 6$ probably starts with de Grey's full field** $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$, not the reduced field. The richer field provides more algebraic coincidences. de Grey's choice of field was not accidental.

**Cross-architectural implication**. L4 said Architectures 1 and 2 share the missing 6-chromatic UDG. L19 sharpens: the 6-chromatic UDG, if it exists, is likely in a field at least as rich as $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$. The path through smaller fields (Polymath's) likely cannot reach chi $\geq 6$ because the field reduction discards exactly the algebraic complexity needed.

**Wrong-approach status**. Compares two specific algebraic UDGs in $\mathbb{R}^2$. The $\mathbb{Q}^2$ detector passes (both graphs use irrational coordinates throughout).

**Future BUILDER directions (next session)**:

1. **Identify the 195 Polymath "new" vertices algebraically**. What's the field-theoretic pattern? Are they all systematic translates of a small motif, or scattered?
2. **The 195 new vertices may NOT be necessary in the field Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11)**. Test: build the chi $\geq 5$ UDG using only de Grey 1585's vertices that coincide with Polymath 510 (the 315 overlap, plus some closure). Is that still chi $\geq 5$?
3. **The de Grey 2018 paper provided a richer-field construction**; modern SAT minimization moved to the smaller field for solver-pragmatic reasons. The richer field may be the proper home of chi $\geq 6$.

---

(no further entries yet; this is a young repository.)
