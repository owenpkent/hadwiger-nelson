# Recent advances briefing: Hadwiger-Nelson, 2024-2026

**Date**: 2026-05-26
**Author**: SURVEYOR agent
**Scope**: post-Polymath16 (rough window 2023-2026) literature on $\chi(\mathbb{R}^2)$ and adjacent chromatic-geometry questions.

## Caveats up front

- The atlas already covers Falconer 1981, OFV 2010, BNOV 2009, KMOR 2015, AMV 2022, ACMVZ 2023, MRVZ 2023, Voronov-Neopryatnaya-Dergachev 2021, Parts 2020 (509), Heule 2018 (529), Mundinger-Pokutta-Spiegel-Zimmer 2024 (deep-annealing six-colorings), Davies 2022 (odd-distance, GAFA 2024), Parts 2022 (6-chromatic odd-distance plane graph, 6-chromatic two-distance plane graph), Voronov 2023 (interval of forbidden distances, $\chi \geq 7$ for $[1-\varepsilon, 1+\varepsilon]$), and Vallentin-Weissbach-Zimmermann 2024 (4-dim lattices). What follows is the genuinely new material **on top of** the existing arch1 and arch2 dossiers.
- Several searches returned only papers already in the atlas; I record below those for which the search confirmed no new development.
- I read abstracts and intros. I have not deep-read any of the new papers. Claims at the lemma / proof level are flagged as such.

## The five most significant 2024-2026 papers

### 1. Sokolov-Voronov 2025, "On the chromatic number of the plane for map-type colorings", [arXiv:2502.01958](https://arxiv.org/abs/2502.01958).

Shows $\chi \geq 7$ for map-type colorings of $\mathbb{R}^2$ where region boundaries are not unit-circle arcs and exactly three boundaries meet at each vertex. Strengthens Woodall 1973 / Townsend 1981 (which had $\geq 6$). Corollary: $\chi \geq 7$ for proper colorings by arbitrary polygonal regions. Method: techniques developed for Voronov 2023's $[1-\varepsilon, 1+\varepsilon]$ interval-of-forbidden-distances result.

**Architecture mapping**: this is a restricted-model strengthening, structurally between Architecture 1 (combinatorial / finite UDG) and Architecture 2 (measurable with regularity). It does *not* imply $\chi_m(\mathbb{R}^2) \geq 7$ or $\chi(\mathbb{R}^2) \geq 7$ because a measurable color class need not be a polygonal region (it can be highly irregular). Note this is the same conflation flagged in [arch2 dossier section 4](arch2_measurable_lineage.md): "$\chi \geq 6$ in recent work" referred to restricted-model results, not measurable.

**Detector check**: passes by design ($\mathbb{Q}^2$ has no polygonal $\chi \geq 7$ regions because the unit-distance graph itself is bipartite; $L^\infty$ would need to be checked).

### 2. Ágoston 2024-2025, "A lower bound on the number of colours needed to nicely colour a sphere", [arXiv:2404.14398](https://arxiv.org/abs/2404.14398).

Shows the chromatic number of any sphere of sufficiently large radius is at least 8 under "nice" coloring restrictions (precise definition in the paper; not deep-read here). Improves Thomassen's lower bound of 7 for manifolds. Original conference version at CCCG 2020; arXiv submitted April 2024, revised April 2025.

**Architecture mapping**: Architecture 1 variant. The result lives on $S^2$, not $\mathbb{R}^2$; it is structurally similar to the sphere-coloring constructions of Voronov-Neopryatnaya-Dergachev 2021. Whether the 8-coloring obstruction transfers to $\mathbb{R}^2$ via radius $r \to \infty$ is the natural question; the answer depends on the precise definition of "nicely". Atlas already lists $\chi(S^2_r) \geq 5$ from VND 2021; the Ágoston result moves this to $\geq 8$ in the restricted-coloring model.

### 3. Parts 2026, "The chromatic number of $\mathbb{R}^8$ is at least 25", [arXiv:2603.14581](https://arxiv.org/abs/2603.14581).

Improves the lower bound on $\chi(\mathbb{R}^8)$ from 19 to 25. Short paper (11 KB), suggests a focused E8-lattice-based construction. Abstract-only at this read. The Polymath16 18th thread (Jan 2026, see [dustingmixon.wordpress.com](https://dustingmixon.wordpress.com/2026/01/17/polymath16-eighteenth-thread-back-with-a-new-conjecture/)) also credits Parts with $\chi(\mathbb{R}^6) \geq 14$ and $\chi(\mathbb{R}^7) \geq 17$ using $E_6$ and $E_7$ lattices respectively.

**Architecture mapping**: Architecture 1 in higher dimensions. **Cross-pollination potential**: the $E_n$-lattice family has algebraic structure not available in $\mathbb{R}^2$, but the *technique* (lattice vector enumeration, Voronoi cell analysis, SAT-driven non-$k$-colorability of the resulting finite graph) is the same as the de Grey / Parts plane lineage. The dimension-8 bound has now grown to 25, vs the plane's stuck-at-5: this gap is itself a signal about the relative tractability of high-dimensional vs low-dimensional cases.

### 4. Polymath16 18th thread (Jan 2026): de Grey's new conjecture and Haugstrup's 6-chromatic triangle-free UDGs in $\mathbb{R}^4$.

Posted at [dustingmixon.wordpress.com](https://dustingmixon.wordpress.com/2026/01/17/polymath16-eighteenth-thread-back-with-a-new-conjecture/) on 2026-01-17. de Grey conjectures: **for all $d \geq 2$ and $3 \leq n \leq d+2$, there exists a $(d+n-1)$-chromatic unit-distance graph in $\mathbb{R}^d$ that does not contain any $n$-simplex.**

For $d = 2$: $n = 3$ gives 4-chromatic triangle-free UDGs (Erdős, by probabilistic argument); $n = 4$ gives a 5-chromatic $K_4$-free UDG (vacuous since UDGs in $\mathbb{R}^2$ contain no $K_4$, so de Grey's 1581 / Parts 509 satisfy this); $n = 5$ would give 6-chromatic UDGs in $\mathbb{R}^2$, which is the missing object.

For $d = 4$: Asger Haugstrup constructed **triangle-free 6-chromatic UDGs in $\mathbb{R}^4$ using 600-cells and 120-cells with novel radius combinations**. This is genuinely new content. The atlas does not currently cover the higher-dimensional triangle-free chromatic frontier.

**Architecture mapping**: Architecture 1, dimension lifted. The conjecture is structural: it pulls the missing-$K_{n+1}$ obstruction (LEARNINGS L21's "$K_{n+1}$-trick ladder") into the framing.

**Cross-pollination with L21**: L21 noted that the $K_{n+1}$-trick is illegal in $\mathbb{R}^2$ UDGs because $\omega \leq 3$. de Grey's conjecture says one can compensate by raising the dimension. If true for $d = 4, n = 4$ (Haugstrup's setting), this gives a roadmap: each dimension allows one more chromatic step than the previous. For $\mathbb{R}^2$, only $n = 3, 4$ are accessible, capping chromatic number at $d + n - 1 = 5$. de Grey's conjecture, **if it correctly characterizes the structural limit**, would explain why the plane is stuck at 5.

### 5. The American Mathematical Monthly 2025, "On the chromatic number of the plane with two forbidden distances", [Vol 132 No 10](https://www.tandfonline.com/doi/abs/10.1080/00029890.2025.2559554) (paywalled abstract).

Constructs a 6-chromatic 2-distance graph in $\mathbb{R}^2$ for $d = 2 + 6\sqrt{2}$ and $d = 3$, raising the lower bound for the chromatic number of the plane with two forbidden distances $\{1, d\}$ to 6 for these values. Continues the lineage of Exoo-Ismailescu 2018 and Parts 2010.12656.

**Architecture mapping**: Architecture 1 variant. Two-distance graph: edges = pairs at distance 1 OR $d$. Note the cross-pollination potential with the "two halves + bridges" L20 framing: a two-distance graph can be seen as the union of two unit-distance graphs (one at scale 1, one at scale $d$). The 6-chromatic obstruction in the two-distance setting is a candidate "intermediate" object between 5-chromatic single-distance and 6-chromatic single-distance.

## Honorable mentions / lesser results

- **Alon-Bucić-Sauermann 2023 (revised Nov 2024), [arXiv:2302.09058](https://arxiv.org/abs/2302.09058), "Unit and distinct distances in typical norms".** Proves that for almost all norms on $\mathbb{R}^2$ (in the Baire category sense), the unit-distance graph has chromatic number exactly 4. **This is a wrong-approach detector update**: it sharpens the project's existing $L^\infty$ detector. The detector regime "abstract normed plane, no Euclidean rigidity" gives $\chi = 4$ for typical norms; the Euclidean norm is non-generic in this measure. Any Architecture 3 method that does not exploit Euclidean-specific structure is structurally wrong (atlas already noted this; the Alon-Bucić-Sauermann result makes it quantitative for all generic norms, not just $L^\infty$).

- **Mundinger-Zimmer-Kiem-Spiegel-Pokutta 2025, [arXiv:2501.18527](https://arxiv.org/abs/2501.18527), "Neural discovery in mathematics: do machines dream of colored planes?"** Successor to the 2024 deep-annealing paper. New six-colorings of $\mathbb{R}^2$ (off-diagonal / two-distance variant). Already covered in [arch1 dossier section 1.4](arch1_sat_lineage.md).

- **Davies 2024, [arXiv:2209.15598](https://arxiv.org/abs/2209.15598), "Odd distances in colourings of the plane" (GAFA 2024).** Every finite coloring of $\mathbb{R}^2$ has a monochromatic odd-distance pair. The odd-distance graph has no finite chromatic number. Already covered in [arch1 dossier section 1.3](arch1_sat_lineage.md).

- **Vallentin-Weissbach-Zimmermann 2024, [arXiv:2407.03513](https://arxiv.org/abs/2407.03513), "The chromatic number of 4-dimensional lattices".** Voronoi graphs of lattice parallelohedra. SAT-driven, but for Cayley graphs, not for unit-distance.

- **Exoo-Ismailescu 2023, [arXiv:2303.06801](https://arxiv.org/abs/2303.06801), "A 5-chromatic same-distance graph in the hyperbolic plane".** Hyperbolic-plane variant, distance $\approx 1.375$. Architecture 2 / 3 adjacent.

- **Elphick-Tang-Zhang 2025, [arXiv:2504.01295](https://arxiv.org/abs/2504.01295), "A spectral lower bound on chromatic numbers using p-energy".** Pure spectral graph theory, no direct geometric application. Listed because Architecture 3 / Lovász $\vartheta$ adjacencies might exploit it; current paper does not.

- **Geometric graphs with exponential chromatic number and arbitrary girth, [arXiv:2312.06898](https://arxiv.org/abs/2312.06898).** Unit-distance graphs in $\mathbb{R}^d$ with $\chi \geq (1.074 + o(1))^d$ and arbitrarily large girth. Architecture 1 in high dimension. Confirms the picture in (3): dimension makes chromatic obstructions much easier than in the plane.

## Negative findings (no new progress in 2024-2026)

- **No new $\chi(\mathbb{R}^2)$ bound.** Parts 509 / 2020 remains the smallest known 5-chromatic UDG. No 6-chromatic UDG in $\mathbb{R}^2$ has been announced.
- **No new $\chi_m(\mathbb{R}^2)$ bound.** Falconer 1981's $\chi_m \geq 5$ still the best. Ruhland 2024 ([arXiv:2408.10076](https://arxiv.org/abs/2408.10076), already in arch2) explicitly proved no improvement to the *lower* bound on $m_1$, sharpening the obstruction picture.
- **No new $\chi_f(\mathbb{R}^2)$ bound.** Matolcsi-Ruzsa-Varga-Zsámboki 2023's $\chi_f \geq 4$ (on a 27-vertex graph, via amenability of $\mathrm{Isom}(\mathbb{R}^2)$) is the current frontier. No 2024-2026 improvement found.
- **No new Borel chromatic bound.** Search for "Borel chromatic plane unit distance 2024" returned the 2024 [Borel polychromatic grids](https://arxiv.org/abs/2508.18559) paper, which is a different problem (grids, not unit-distance in the plane).
- **No published Lean / formal proof of $\chi \geq 5$.** Search returned general Lean activity, nothing specific to Hadwiger-Nelson.
- **No ML / RL paper attempting $\chi \geq 6$ in $\mathbb{R}^2$.** The Mundinger-Pokutta line is on the upper-bound (six-coloring) side. Neural approaches for the lower bound remain unexplored.

## Per-architecture status

### Architecture 1 (combinatorial / SAT / UDG)
- $\mathbb{R}^2$: **stuck**. Parts 509 since 2020. No 6-chromatic UDG.
- $\mathbb{R}^3$: stuck. Nechushtan-style $\chi \geq 6$, $\chi \leq 15$.
- $\mathbb{R}^d, d \geq 4$: **moving**. Parts pushed $\chi(\mathbb{R}^6) \geq 14$, $\chi(\mathbb{R}^7) \geq 17$, $\chi(\mathbb{R}^8) \geq 25$ in 2025-2026. Haugstrup constructed triangle-free 6-chromatic UDGs in $\mathbb{R}^4$.
- **Conjectural roadmap**: de Grey's 18th-thread conjecture (Jan 2026) explicitly ties the dimension-vs-chromatic-step structure.
- **Status on project's L20-L22 frontier**: the K_{n+1}-trick ladder of L21 has a new structural complement (de Grey's conjecture). Pursuing $\mathbb{R}^2$ chi=6 still requires a non-$K_6$ mechanism in the dimension-2 case; raising the dimension is the obvious workaround, but yields no information about the plane.

### Architecture 2 (measurable / spectral)
- **Stuck**. $\chi_m(\mathbb{R}^2) \geq 5$ since 1981. $m_1(\mathbb{R}^2) \leq 0.247$ since Ambrus et al. 2023, no improvement. Ruhland 2024 negative result on lower bound for $m_1$.
- The Bochner-Riesz / Fourier-analytic angle: a search returned no 2024-2026 paper applying Bochner-Riesz multipliers to the unit-distance equation. Open.
- **Status on project's L20-L22 frontier**: the L4 / arch2 dossier sec 5 coupling (Falconer's machine needs a 6-chromatic UDG to push to $\chi_m \geq 6$) is unchanged.

### Architecture 3 (fractional / Lovász $\vartheta$)
- $\chi_f(\mathbb{R}^2) \geq 4$ since MRVZ 2023 (27-vertex graph + amenability). No 2024-2026 improvement.
- **Cross-pollination potential**: the MRVZ "geometric fractional chromatic number" $\chi_{gf}$ is the natural fractional analog of the project's L20 "two halves + bridges" framing. If the 27-vertex graph in MRVZ decomposes as two 3.5-chromatic halves coupled by bridges, the framing transfers.
- **Status on project's L20-L22 frontier**: project's IE-LP / beam-search work (LEARNINGS L13, $m_1 \leq 0.2584$) is methodologically descended from Ambrus 2022, KMOR 2015; no new 2024-2026 SDP / LP work to incorporate.

### Architecture 4 (set-theoretic / axiomatic)
- **No new development.** Shelah-Soifer 2003 remains canonical; de Grey 2018 made the conditional theorem vacuous (LEARNINGS L7). Borel chromatic number of the unit-distance graph on $\mathbb{R}^2$ has no published bound stronger than $\chi_B \geq 5$ (which follows from $\chi \geq 5$ via the trivial $\chi_B \geq \chi$ inequality).
- **Status on project's L20-L22 frontier**: orthogonal. L20-L22 are combinatorial / structural; Architecture 4 is meta-mathematical.

### Cross-architecture: ML / search heuristics
- Active on the upper-bound side (Mundinger-Pokutta-Spiegel-Zimmer 2024 / 2025). **No published ML / RL work on the lower-bound side for $\mathbb{R}^2$.**
- For Architecture 1 in higher dimensions, Parts and Haugstrup are using hand-crafted lattice-based constructions, not learned ones.

## Intersection with L20-L22 (current project frontier)

The atlas's current internal frontier is the "two 4-chromatic halves + bridges" framing (L17-L20), the $K_{n+1}$-trick ladder (L21), and the list-coloring reformulation (L22). What does the survey tell us?

1. **de Grey's January 2026 conjecture is the structural complement of L21.** L21 said: in $\mathbb{R}^2$, the $K_{n+1}$-trick is illegal for $n \geq 3$ because UDGs have $\omega \leq 3$, so the chi-5 step can be done graph-theoretically (Moser×Moser, 14 vertices) but no chi-6 step exists. de Grey's conjecture proposes the structural workaround: **raise the dimension**. For $d = 2$, the conjecture's accessible cases ($n = 3, 4$) cap at $d + n - 1 = 5$. The plane is "stuck" because of an algebraic-topological constraint at $d = 2$, not because of insufficient search effort. *If the conjecture is true and tight, $\chi(\mathbb{R}^2) = 5$.*

2. **Haugstrup's triangle-free 6-chromatic UDG in $\mathbb{R}^4$ is the smallest known structurally novel chi-6 UDG in any dimension since 2018.** This is the kind of explicit construction the L20 "two halves + bridges" framing should be tested against. If Haugstrup's graph decomposes as two 5-chromatic halves coupled by bridges (a 3-way coupling in L20's sense), the framing extends to chi-6. If not, the framing was specific to the chi-5 step.

3. **The list-coloring view (L22) generalizes immediately to dimension lift.** L22 reformulated chi >= 5 forcing as a list-coloring instance on $H_2$. The same reformulation applies to chi >= 6 in any dimension: $\chi(H_1 \cup H_2 \cup H_3 \cup B) \geq 6$ iff a 2-step list-coloring deduction fails. For Haugstrup's $\mathbb{R}^4$ construction, computing the F-profiles on the boundary vertices would test whether the structural mechanism is the same as in $\mathbb{R}^2$.

4. **MRVZ 2023's 27-vertex graph in $\mathbb{R}^2$ is a candidate test object for L20.** It has $\chi_f \geq 4$ but $\chi = 4$ (presumably). Does it decompose as two halves of $\chi_f \approx 2$ each, coupled by bridges? If yes, the fractional analog of the L20 mechanism is alive in Architecture 3.

## Three concrete next-experiment ideas

### E-A: Decomposition analysis of Haugstrup's $\mathbb{R}^4$ 6-chromatic triangle-free UDG (L20 test in higher dimension)

**Goal**: test whether the "two 4-chromatic halves + bridges" pattern of L17-L20 generalizes to "two 5-chromatic halves + bridges" or "three 4-chromatic components + 3-way bridges" in the $\mathbb{R}^4$ chi-6 construction.

**Method**: extract Haugstrup's graph from Polymath16 thread 18 / a personal-communication request to Asger Haugstrup. Compute connected components after removing candidate bridge edges. For each candidate decomposition, verify chi of each component via SAT. Compute F-profiles per L22.

**Why now**: this is the first published chi-6 triangle-free UDG in any dimension since 2018; the L20-L22 framing was developed against $\mathbb{R}^2$ chi-5 examples; this is the natural test.

**Architecture**: 1. Cross-dimension transfer.

### E-B: Apply MRVZ 2023's geometric-fractional-chromatic machinery to the Moser×Moser 14-vertex L21 abstract graph

**Goal**: compute $\chi_{gf}$ of the L21 14-vertex no-$K_4$ abstract graph (the smallest known chi >= 5 with $\omega \leq 3$). If $\chi_{gf} = 5$ (matching the integer $\chi$), the MRVZ amenability technique transfers; if $\chi_{gf} < 5$, the geometric / amenability obstruction is the binding constraint.

**Method**: implement MRVZ's $\chi_{gf}$ formulation (LP on Haar-measure-weighted indicator functions over $\mathrm{Isom}(\mathbb{R}^2)$). Apply to the L21 14-vertex graph. Compare to the integer chi = 5.

**Why now**: MRVZ 2023 is the most recent Architecture 3 advance and uses the same finite-graph backbone as the project's L21 work; the cross-architecture coupling (L4, L9-L10) predicts that bounds transfer.

**Architecture**: 3. Cross-architecture coupling with Architecture 1.

### E-C: Bochner-Riesz / multiplier-theoretic re-attack on Falconer 1981

**Goal**: revisit Falconer's $\chi_m \geq 5$ argument with modern Bochner-Riesz multiplier technology. The Falconer step-3 (rigid finite configuration realized in a high-density region) admits a Fourier-analytic rephrasing: the convolution of an indicator function with itself near the unit-distance level set has structure that Bochner-Riesz multipliers can sharpen.

**Method**: literature pull on Bochner-Riesz $\to$ unit-distance configurations (2022-2026). Implement Falconer step 3 with a Bochner-Riesz convolution. Test whether stepping from $\chi \geq 5$ to $\chi \geq 6$ requires a 6-chromatic configuration or admits a *measurable-only* obstruction (multiplier of a different type).

**Why now**: arch2 dossier sec 5 notes Bochner-Riesz is unattempted; the recent ACMVZ 2023 success at sharpening $m_1$ via inclusion-exclusion atoms suggests harmonic-analytic LP techniques have more room to run.

**Architecture**: 2. Pure Architecture 2 strategy that does not require a new finite UDG.

## What this enables / what remains open

**Enabled**:
- A concrete test (E-A) of whether L20-L22's structural pattern generalizes to chi-6 in higher dimensions.
- A concrete cross-architecture test (E-B) of whether the integer-vs-fractional chromatic gap is the binding constraint.
- A revisit (E-C) of the only Architecture 2 lemma with growth potential.

**Open**:
- Is $\chi(\mathbb{R}^2) \in \{5, 6, 7\}$? Nothing in 2024-2026 closes this.
- Is de Grey's January 2026 conjecture true? If yes, $\chi(\mathbb{R}^2) = 5$.
- Does Haugstrup's $\mathbb{R}^4$ construction project down to a $\mathbb{R}^2$ chi-6 UDG? Unlikely (projection-of-unit-distance-graph is not unit-distance), but the structural lessons transfer.
- Is there a fundamentally different proof method (Architecture 5: something other than the four established) that has not been considered? Not visible in 2024-2026 literature.
