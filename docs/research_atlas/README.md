# Hadwiger-Nelson Research Atlas

Master research map for the chromatic number of the plane.

## The problem

Let $G_{\mathbb{R}^2}$ be the graph on vertex set $\mathbb{R}^2$ with edges between points at Euclidean distance exactly $1$. The **chromatic number of the plane** is

$$
\chi(\mathbb{R}^2) := \chi(G_{\mathbb{R}^2}).
$$

Hadwiger (1945) and Nelson (1950, communicated through Gardner and Isbell) posed the question. Current bounds:

$$
5 \leq \chi(\mathbb{R}^2) \leq 7.
$$

## Known bounds

### Lower bound: $\chi \geq 5$ (de Grey, 2018)

Aubrey de Grey constructed a finite unit-distance graph on $1581$ vertices that is not $4$-colorable. Marijn Heule independently verified the construction with a SAT proof. The Polymath16 project then iteratively shrank the graph: 553 (Heule, 2018), 529 (Heule, 2018), 525 (Parts, 2019), 517 (Heule, 2019, with $120^\circ$ rotational symmetry), 510 (Parts, 2019), to the current record of **509 vertices, 2442 edges** by Parts (2020, [arXiv:2010.12665](https://arxiv.org/abs/2010.12665)). Coordinates throughout this lineage live in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$.

Parts also published a **human-verifiable** proof of $\chi \geq 5$ ([arXiv:2010.12661](https://arxiv.org/abs/2010.12661)) showing that SAT was a convenience, not a logical necessity.

Voronov, Neopryatnaya, and Dergachev (2021, [arXiv:2106.11824](https://arxiv.org/abs/2106.11824)) constructed the first $\chi \geq 5$ UDG with **no Moser spindle as a subgraph** (64513 vertices), and the first 5-chromatic UDGs on $S^2$ (372 and 972 vertices). These show the Moser spindle is structurally inessential to $\chi \geq 5$, even though it appears in every Polymath16 record.

This replaced the long-standing $\chi \geq 4$ bound from the Moser spindle (1961).

Deep dive: [`arch1_sat_lineage.md`](arch1_sat_lineage.md) (Architecture 1 SAT lineage, 2018-present).

### Upper bound: $\chi \leq 7$ (Isbell, ~1950)

Tile the plane with regular hexagons of diameter slightly less than $1$ (e.g., diameter $\tfrac{7}{8}$). Color the hexagons with $7$ colors in a repeating $7$-color pattern such that any two hexagons sharing the same color are at distance more than $1$ apart. The standard construction uses cells with centers on a hexagonal lattice scaled so that any two same-colored cells are far enough apart.

Refinement: with diameter exactly $1$ and boundary handling, this gives $\chi \leq 7$.

## Variants and refinements

| Variant | Definition | Status |
|---------|------------|--------|
| $\chi(\mathbb{R}^2)$ | full chromatic number, AC available | $5 \leq \chi \leq 7$ |
| $\chi_m(\mathbb{R}^2)$ | **measurable** chromatic number: color classes must be Lebesgue-measurable | $5 \leq \chi_m$ (Falconer 1981, **no improvement in 45 years**); see arch2 dossier |
| $m_1(\mathbb{R}^2)$ | density of largest measurable unit-distance-avoiding set; $\chi_m \geq 1/m_1$ | $m_1 \leq 0.2470$ (Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023), settling Erdős's conjecture |
| $\chi_f(\mathbb{R}^2)$ | **fractional** chromatic number | $\chi_f \geq 4$ (Matolcsi-Ruzsa-Varga-Zsámboki 2023, arXiv:2311.10069); previously $\geq 3.6$ (Cranston-Rabern) |
| $\chi_B(\mathbb{R}^2)$ | **Borel** chromatic number: color classes Borel | open; sits between $\chi$ and $\chi_m$; no published bound stronger than $\chi_B \geq 5$ |
| $\chi(\mathbb{R}^2)$ in ZF + DC + LM | without full Choice, with Lebesgue measurability | **open whether it differs from ZFC value**. Shelah-Soifer 2003 proved a *conditional* (if every finite UDG has $\chi \leq 4$ then values differ) which de Grey 2018 made vacuous by exhibiting a 5-chromatic UDG. The phenomenon survives for *artificial* distance graphs (Shelah-Soifer 2003b, Payne 2009) but not for $\chi(\mathbb{R}^2)$ itself. See LEARNINGS L7 |
| $\chi_m(\mathbb{H}^2(d))$ | measurable, hyperbolic plane, edge distance $d$ | $\geq 6$ for $d \geq 12$ (DeCorte-Golubev 2018). *Does not transfer to $\mathbb{R}^2$* |
| $\chi$ for convex-tile colorings | color classes are convex polygons of bounded area | $\geq 6$ (Coulson 2002, Townsend-Woodall). Strictly stronger restriction than Lebesgue-measurable |

## Cross-architecture synthesis

Three of the four architectures are gated by a single missing combinatorial object: **a finite unit-distance graph in $\mathbb{R}^2$ with chromatic number $\geq 6$**.

- Architecture 1: such a graph directly gives $\chi(\mathbb{R}^2) \geq 6$.
- Architecture 2: Falconer's 1981 four-step machine inputs a finite $k$-chromatic UDG and outputs $\chi_m \geq k$. A 6-chromatic UDG $\to$ $\chi_m \geq 6$.
- Architecture 3: the OFV-style LP constraint $\sum f(\|v_i\|) \leq \alpha(G)$ drives $m_1 \to \alpha(G)/N(G) \leq 1/\chi_f(G)$. A graph with $\chi_f(G) \geq 6$ would give integer $\chi_m \geq 6$.

See [`../03_research/cross_architecture_coupling.md`](../03_research/cross_architecture_coupling.md) for the synthesis of LEARNINGS L1-L13. Long-range research program in [`../../experiments/SOLVING_PROGRAM.md`](../../experiments/SOLVING_PROGRAM.md).

## Four candidate proof architectures

### Architecture 1: Combinatorial / Unit-Distance Graphs

**Goal**: construct a finite UDG in $\mathbb{R}^2$ with chromatic number $\geq 6$ (or $\geq 7$).

**Lineage**: Moser spindle ($\chi = 4$, 1961) $\to$ Golomb graphs $\to$ de Grey ($\chi \geq 5$, 2018, 1581 vertices) $\to$ Polymath16 (Heule 529, Parts 510, Parts 509 in 2020) $\to$ Voronov et al. (2021, Moser-spindle-free at 64513) $\to$ ???.

**Tools**: SAT solvers (cadical, kissat, glucose); structured graph construction in number fields $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ etc.; symmetric / group-theoretic constructions; Heule's clausal-proof-minimization (CPM) and Parts' preserve-a-property minimization.

**Wrong-approach test**: must use the topology / density of $\mathbb{R}$, not just abstract UDG structure (since $\mathbb{Q}^2$ has $\chi = 2$). Every entry in the lineage above realizes essentially-irrational coordinates ($\sqrt{3}, \sqrt{11}$); the detector passes throughout. See [`arch1_sat_lineage.md`](arch1_sat_lineage.md) §5.

**Status**: active. Smallest 5-chromatic UDG record at 509 vertices since 2020 (no shrinking in 5 years). **No 6-chromatic UDG known.** Variant problems ($k$-distance, odd-distance, sphere) admit 6-chromatic constructions; the single-distance plane uniquely resists. See LEARNINGS L1.

**Deep dive**: [`arch1_sat_lineage.md`](arch1_sat_lineage.md).

### Architecture 2: Measurable / spectral

**Goal**: prove lower bounds on $\chi_m(\mathbb{R}^2)$, then either (a) prove $\chi_m = \chi$ under reasonable axioms, or (b) push $\chi_m \geq 6$ or $\geq 7$.

**Lineage**: Falconer 1981 ($\chi_m \geq 5$) $\to$ Bukh, Soifer expositions $\to$ Fourier / autocorrelation $\to$ Oliveira Filho-Vallentin LP bounds on $m_1(\mathbb{R}^2)$ $\to$ Bachoc-Nebe-Oliveira Filho-Vallentin generalized Lovász $\vartheta$ SDP $\to$ Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023 ($m_1 < 1/4$).

**Tools**: Lebesgue density theorem on color classes; autocorrelation of indicator functions; Fourier transform on $\mathbb{R}^2$ and the rotation group $O(2)$; generalized Lovász $\vartheta$ SDP via Jacobi polynomials; LP bounds on $m_1(\mathbb{R}^2)$ via the OFV / AC-MV-Z chain.

**Wrong-approach test**: must use the 2D rotation group, not just dimension; must not reduce to $\mathbb{R}^1$ (where $\chi = 2$ trivially). Measure-zero issues mean this architecture is exempt from the $\mathbb{Q}^2$ test.

**Status**: $\chi_m(\mathbb{R}^2) \geq 5$ since Falconer 1981, **no improvement in 45 years**. The widely-cited "$\chi_m \geq 6$" results live in the hyperbolic plane or in restricted-region variants, not in the canonical $\mathbb{R}^2$. **Cross-architecture coupling** (see LEARNINGS L4): the obstruction to pushing Falconer's $\chi_m \geq 5$ to $\chi_m \geq 6$ is at the lemma level the same as the obstruction to $\chi \geq 6$ in Architecture 1, namely the missing 6-chromatic finite UDG.

**Deep dive**: [`arch2_measurable_lineage.md`](arch2_measurable_lineage.md).

### Architecture 3: Fractional / Lovász $\vartheta$ / spectral / LP for $m_1(\mathbb{R}^2)$

**Goal**: bound $m_1(\mathbb{R}^2)$ via continuous LP / SDP, transfer to $\chi_m$ via $\chi_m \geq 1/m_1$; bound $\chi_f(\mathbb{R}^2)$ via finite UDG fractional chromatic.

**Lineage**: Cranston-Rabern $\chi_f \geq 76/21 \approx 3.62$ (arXiv:1501.01647) $\to$ Oliveira Filho-Vallentin 2010 LP $m_1 \leq 0.2688$ (arXiv:0808.1822) $\to$ Bachoc-Nebe-OFV 2009 2-particle SDP (arXiv:0801.1059, not helpful at $n=2$, LEARNINGS L12) $\to$ Keleti-Matolcsi-OFV-Ruzsa 2015 LP $m_1 \leq 0.2588$ (arXiv:1501.00168) $\to$ Bellitto-Pêcher-Sédillot 2018 $\chi_f \geq 3.8991$ on 607 vertices $\to$ Ambrus-Matolcsi 2022 LP $m_1 \leq 0.2544$ $\to$ Matolcsi-Ruzsa-Varga-Zsámboki 2023 $\chi_f \geq 4$ on 27 vertices (arXiv:2311.10069) $\to$ **Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023 $m_1 \leq 0.2470$** via 23-point IE-LP + beam search (arXiv:2207.14179). This last gives integer $\chi_m \geq 5$ via the bridge inequality $\chi_m \geq 1/m_1$.

**Key insight (LEARNINGS L12)**: Ambrus 2023's path to 0.247 is a refined *1-particle* LP with inclusion-exclusion atom constraints from a finite point configuration. NOT a 2-particle SDP. The BV SDP at $n=2$ reduces to the basic Bessel LP.

**Tools**: Bochner-Hankel decomposition of positive-type radial functions on $\mathbb{R}^2$ via Bessel $J_0$; rotation-invariant LP for $m_1(\mathbb{R}^n)$ via $\Omega_n$ functions; OFV-style simplex inequalities (unit-edge equilateral triangles $K_3$); Moser-spindle inequalities ($\alpha(G) = 2$); inclusion-exclusion atom LP from finite point configurations (Ambrus); beam search over configurations.

**Wrong-approach test**: must distinguish the Euclidean inner product from generic norms (otherwise applies to $L^\infty$ where $\chi = 4$); must engage the $O(2)$ rotation group via spherical symmetrization (otherwise reduces to $\mathbb{R}^1$ where the LP gives the correct $m_1 = 1/2$, $\chi_m \geq 2$ — detector check passes for OFV / IE-LP framework).

**Status**: active. Project replication state:
- e3b vanilla Bessel-LP: $m_1 \leq 0.2873$ analytic saturation (L6).
- e3c OFV 2010 dual LP with 3 off-center triangles: $m_1 \leq 0.268412$ exact match (L8).
- e3e Moser-spindle inequality at 6048 translations: $m_1 \leq 0.2619$ (L9).
- e3h greedy beam search over IE-LP, 17-vertex configuration: $m_1 \leq 0.2584$ matching KMOR 2015 (L13).
- Integer $\chi_m \geq 5$ via this route requires $m_1 < 0.2$, current open frontier. Greedy width-1 plateau near 0.258; beam width $\geq 2$, vertex-swap local search, or richer pool needed.

**Cross-architecture coupling** (LEARNINGS L9, L10): the OFV LP constraint $\sum f(\|v_i\|) \leq \alpha(G)$ drives $m_1$ toward $\alpha(G)/N(G)$. For a 6-chromatic finite UDG with $\chi_f(G) = 6$, this gives $m_1 \leq 1/6$, hence integer $\chi_m \geq 6$. Same missing object as Architectures 1 and 2.

### Architecture 4: Set-theoretic / axiomatic

**Goal**: clarify the dependence of $\chi(\mathbb{R}^2)$ on the axiom system; refine the Borel chromatic number.

**Lineage**: de Bruijn-Erdős 1951 (compactness, weak AC) $\to$ Shelah-Soifer 2003 (axiom-dependence for distance graphs on $\mathbb{R}^1$ and $\mathbb{R}^2$; conditional theorem about $\chi(\mathbb{R}^2)$) $\to$ Shelah-Soifer 2005 ($\mathbb{R}^n$ extension) $\to$ Payne 2009 (first UDG-subgraphs with axiom-dependent $\chi$) $\to$ Kechris-Solecki-Todorcevic 1999 / Marks et al. (Borel chromatic framework on Polish spaces).

**Tools**: forcing; descriptive set theory; Hamel-basis constructions; Steinhaus theorem on difference sets; effective measure theory.

**Wrong-approach test**: partly orthogonal (axiom dependence is meta-mathematical). But arguments should still distinguish $\mathbb{R}$ from $\mathbb{Q}$ structurally.

**Status**: conceptually rich but **does not close the $[5, 7]$ gap**. The 2003 Shelah-Soifer conditional theorem about $\chi(\mathbb{R}^2)$ was made vacuous by de Grey 2018: it required all finite UDGs to be 4-colorable, and de Grey produced a 5-chromatic finite UDG. Whether $\chi(G_{\mathbb{R}^2})$ specifically depends on AC remains **open**. See LEARNINGS L7 and the [arch4 dossier](arch4_set_theoretic_lineage.md).

**Deep dive**: [`arch4_set_theoretic_lineage.md`](arch4_set_theoretic_lineage.md).

## Wrong-approach detectors

The Hadwiger-Nelson analog of the zeta-function repo's Davenport-Heilbronn discipline.

| Detector | $\chi$ | Architectures it catches |
|----------|--------|---------------------------|
| $\mathbb{Q}^2$ unit-distance graph | $2$ (Woodall 1973) | 1 (combinatorial) — must use topology of $\mathbb{R}$ |
| $L^\infty$ unit-distance graph on $\mathbb{R}^2$ | $4$ (Chilakamarri) | 3 (fractional / spectral) — must use Euclidean rigidity |
| $\mathbb{R}^1$ (line, distance 1) | $2$ | 2 (measurable) — must use 2D rotation group |
| $\mathbb{Q}^4$ unit-distance graph | $4$ (Benda-Perles) | growth tests for dimension-sensitive methods |

A proposed proof method that gives $\chi(\mathbb{R}^2) \geq 5$ should fail on the detector appropriate to its architecture. If it does not, the method has overshot and is structurally wrong.

## Open frontiers

- Is $\chi(\mathbb{R}^2) = 5, 6,$ or $7$?
- Can a small ($\leq 1000$ vertex) $6$-chromatic UDG exist?
- Does $\chi_m = \chi$ under MA or some choice-weakening axiom?
- Can the Lovász $\vartheta$ on Cayley graphs of $\mathbb{R}^2$ be computed analytically?
- Is there a "natural" proof method that distinguishes the $\chi \leq 7$ bound from the $\chi \geq 5$ bound asymptotically?

## References

- A.D.N.J. de Grey, *The chromatic number of the plane is at least 5*, Geombinatorics 28 (2018).
- A. Soifer, *The Mathematical Coloring Book*, Springer (2009). Definitive reference.
- K.J. Falconer, *The realization of distances in measurable subsets covering $\mathbb{R}^n$*, J. Combin. Theory A 31 (1981).
- L.A. Székely, *Erdős on unit distances and the Szemerédi-Trotter theorems*, Paul Erdős and his Mathematics II, 2002.
- Polymath16, *Hadwiger-Nelson problem*, online project (2018).
- D.R. Woodall, *Distances realized by sets covering the plane*, J. Combin. Theory A 14 (1973). The $\mathbb{Q}^2$ result.
- S. Shelah and A. Soifer, *Axiom of choice and chromatic number of the plane*, J. Combin. Theory A 103 (2003).
