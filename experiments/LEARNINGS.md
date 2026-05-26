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

(no further entries yet; this is a young repository.)
