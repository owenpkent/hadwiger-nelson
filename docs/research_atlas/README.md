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

> **Reference library.** An annotated catalog of 19 source texts (books + papers) is in
> [`sources/LIBRARY.md`](../../sources/LIBRARY.md), with deep architecture-oriented reading notes
> and a cross-cutting synthesis in [`sources/notes/`](../../sources/notes/README.md). Two
> through-lines from that read: (1) embeddability of a graph as a planar UDG is governed by
> Euclidean dimension $\mathrm{Edim}(G) \leq 2\Delta(G)$, i.e. by max degree not chromatic number,
> the structural reason the $\chi \geq 6$ embeddable-graph bottleneck is hard; (2) the measurable
> bound $\chi_m(\mathbb{R}^2) \geq 5$ is reached both by Falconer 1981 and by the single-class
> density / LP route (Ambrus et al. 2023, $m_1 \leq 0.247 < 1/4$; repo L35/L36), and that density
> route is provably CAPPED at 5 (Croft floor $m_1 \geq 0.229 > 1/5$).

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

## The universal "two 4-chromatic halves + bridges" pattern (LEARNINGS L14-L20)

Reverse-engineering of de Grey 1585 and Polymath 510 (sessions 007-011) identified a universal mechanism behind every published chi >= 5 UDG:

**Every chi >= 5 graph in the published lineage decomposes as two 4-chromatic halves connected by bridge edges.** Removing any single component (either half, or the bridges) drops chi to 4.

| Graph | Half 1 ($\chi=4$) | Half 2 ($\chi=4$) | Bridges | Full ($\chi=5$) |
|---|---:|---:|---:|---:|
| de Grey 1585 | 778v (C_6 core about $v_0=(2,0)$) | 807v (asymmetric) | 155 | 1585v |
| Polymath 510 | 315v (overlap with de Grey under $T=(2,0)$) | 195v (field artifacts) | 833 | 510v |

Findings:

- **Polymath 510 is a translated substructure of de Grey 1585** (L19): 315/510 = 62% of its vertices ARE de Grey vertices under $T = (2, 0)$. Heule/Parts didn't build a new graph; they extracted a subset of de Grey's vertices that fit in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ and added 195 compensatory artifacts.

- **Obstruction is extremely delocalized in de Grey 1585** (L18): every reasonable structural reduction (even keeping 75% of vertices) drops chi to 4.

- **Binding-rotation search exhausted in $\mathbb{Q}(\sqrt 3, \sqrt{11})$** (L14): the Moser spindle admits only 16 single, 62 double, 4 triple binding rotations. Full stacking yields 211v / chi=4. Reaching chi >= 6 likely requires de Grey's full field $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$.

- **Implication for chi >= 6**: the "two halves + bridges" pattern appears to cap at chi = 5. A chi >= 6 UDG likely requires a *qualitatively different* mechanism — e.g., a 3-way coupling that forces each of three colors to be paired with a distinct chi-4 structure. No such construction is known.

This refines L4's "missing 6-chromatic UDG" framing: the missing object is not a refinement of de Grey / Polymath, but a fundamentally different combinatorial idea.

## Four candidate proof architectures

### Architecture 1: Combinatorial / Unit-Distance Graphs

**Goal**: construct a finite UDG in $\mathbb{R}^2$ with chromatic number $\geq 6$ (or $\geq 7$).

**Lineage**: Moser spindle ($\chi = 4$, 1961) $\to$ Golomb graphs $\to$ de Grey ($\chi \geq 5$, 2018, 1581 vertices) $\to$ Polymath16 (Heule 529, Parts 510, Parts 509 in 2020) $\to$ Voronov et al. (2021, Moser-spindle-free at 64513) $\to$ ???.

**Tools**: SAT solvers (cadical, kissat, glucose); structured graph construction in number fields $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ etc.; symmetric / group-theoretic constructions; Heule's clausal-proof-minimization (CPM) and Parts' preserve-a-property minimization.

**Wrong-approach test**: must use the topology / density of $\mathbb{R}$, not just abstract UDG structure (since $\mathbb{Q}^2$ has $\chi = 2$). Every entry in the lineage above realizes essentially-irrational coordinates ($\sqrt{3}, \sqrt{11}$); the detector passes throughout. See [`arch1_sat_lineage.md`](arch1_sat_lineage.md) §5.

**Status**: active. Smallest 5-chromatic UDG record at 509 vertices since 2020 (no shrinking in 5 years). **No 6-chromatic UDG known.** Variant problems ($k$-distance, odd-distance, sphere) admit 6-chromatic constructions; the single-distance plane uniquely resists. See LEARNINGS L1.

**Structural understanding** (sessions 007-011, LEARNINGS L14-L20): every published chi >= 5 UDG in the lineage is an instance of the "two 4-chromatic halves + bridges" coupling construction. The de Grey 2018 breakthrough was not a new combinatorial mechanism; it was a specific instance with 778v + 807v + 155 bridges. Polymath 510 is essentially the same construction translated by $(2, 0)$, restricted to a smaller field, with 315v + 195v + 833 bridges (denser bridges compensate for fewer vertices). The chi >= 6 path likely needs a fundamentally different mechanism than this pattern.

**Deep dive**: [`arch1_sat_lineage.md`](arch1_sat_lineage.md).

### Architecture 2: Measurable / spectral

**Goal**: prove lower bounds on $\chi_m(\mathbb{R}^2)$, then either (a) prove $\chi_m = \chi$ under reasonable axioms, or (b) push $\chi_m \geq 6$ or $\geq 7$.

**Lineage**: Falconer 1981 ($\chi_m \geq 5$) $\to$ Bukh, Soifer expositions $\to$ Fourier / autocorrelation $\to$ Oliveira Filho-Vallentin LP bounds on $m_1(\mathbb{R}^2)$ $\to$ Bachoc-Nebe-Oliveira Filho-Vallentin generalized Lovász $\vartheta$ SDP $\to$ Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023 ($m_1 < 1/4$).

**Tools**: Lebesgue density theorem on color classes; autocorrelation of indicator functions; Fourier transform on $\mathbb{R}^2$ and the rotation group $O(2)$; generalized Lovász $\vartheta$ SDP via Jacobi polynomials; LP bounds on $m_1(\mathbb{R}^2)$ via the OFV / AC-MV-Z chain.

**Wrong-approach test**: must use the 2D rotation group, not just dimension; must not reduce to $\mathbb{R}^1$ (where $\chi = 2$ trivially). Measure-zero issues mean this architecture is exempt from the $\mathbb{Q}^2$ test.

**Status**: $\chi_m(\mathbb{R}^2) \geq 5$ since Falconer 1981, **no improvement in 45 years**. The widely-cited "$\chi_m \geq 6$" results live in the hyperbolic plane or in restricted-region variants, not in the canonical $\mathbb{R}^2$. **Cross-architecture coupling** (see LEARNINGS L4): the obstruction to pushing Falconer's $\chi_m \geq 5$ to $\chi_m \geq 6$ is at the lemma level the same as the obstruction to $\chi \geq 6$ in Architecture 1, namely the missing 6-chromatic finite UDG.

**Deep dive**: [`arch2_measurable_lineage.md`](arch2_measurable_lineage.md) (chronology, Falconer proof, $\chi_m \geq 6$ misattribution audit). Spectral / SDP companion: [`arch2_measurable.md`](arch2_measurable.md) (the $k$-point SDP hierarchy, OFV 2-point and DMOV 3-point, project experiments e2a/e2b/e2c with certificates, sharpened $\chi_m \geq 6$-is-open verdict; LEARNINGS L31-L33).

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

## 2024-2026 update

Survey [`2026-05-26-recent-advances-briefing.md`](2026-05-26-recent-advances-briefing.md) covers post-Polymath16 literature. Headlines:

- **$\chi(\mathbb{R}^2)$ unchanged**: Parts 509 (2020) still the smallest known 5-chromatic UDG. No 6-chromatic UDG announced. $\chi_m(\mathbb{R}^2) \geq 5$ (Falconer 1981) still the measurable lower bound. $\chi_f(\mathbb{R}^2) \geq 4$ (Matolcsi-Ruzsa-Varga-Zsámboki 2023) still the fractional lower bound.
- **Higher dimensions are moving**: Parts pushed $\chi(\mathbb{R}^6) \geq 14$, $\chi(\mathbb{R}^7) \geq 17$, $\chi(\mathbb{R}^8) \geq 25$ in 2025-2026 via $E_n$-lattice constructions ([arXiv:2603.14581](https://arxiv.org/abs/2603.14581)). Asger Haugstrup constructed **triangle-free 6-chromatic UDGs in $\mathbb{R}^4$** using 600-cells and 120-cells.
- **de Grey's 2026 conjecture**: for all $d \geq 2$ and $3 \leq n \leq d+2$, there exists a $(d+n-1)$-chromatic unit-distance graph in $\mathbb{R}^d$ that does not contain any $n$-simplex. For $d = 2$ the conjecture caps at $\chi = 5$ (since UDGs in $\mathbb{R}^2$ have $\omega \leq 3$, ruling out $n \geq 5$). **If de Grey's conjecture is tight, $\chi(\mathbb{R}^2) = 5$**. Posted on [Polymath16 thread 18](https://dustingmixon.wordpress.com/2026/01/17/polymath16-eighteenth-thread-back-with-a-new-conjecture/) (2026-01-17). Structural complement to LEARNINGS L21's $K_{n+1}$-trick ladder.
- **Map-type / interval-of-distances variants** (Voronov 2023, Sokolov-Voronov 2025, [arXiv:2502.01958](https://arxiv.org/abs/2502.01958)): for proper colorings whose regions are polygonal (or whose forbidden distance is the interval $[1-\varepsilon, 1+\varepsilon]$), $\chi \geq 7$. These results do *not* imply $\chi_m \geq 7$; restricted-model colorings are strictly stronger than Lebesgue-measurable.
- **Two-distance variant**: 6-chromatic 2-distance graph for $d = 2 + 6\sqrt 2$ and $d = 3$ ([Amer. Math. Monthly 2025](https://www.tandfonline.com/doi/abs/10.1080/00029890.2025.2559554)).
- **Wrong-approach detector sharpening** (Alon-Bucić-Sauermann 2023, revised 2024, [arXiv:2302.09058](https://arxiv.org/abs/2302.09058)): for *almost all* norms on $\mathbb{R}^2$ (Baire category), the unit-distance graph has $\chi = 4$. The Euclidean norm is non-generic. Any Architecture 3 method that does not exploit Euclidean-specific structure is structurally wrong.
- **ML / neural**: Mundinger-Pokutta-Spiegel-Zimmer 2024 ([arXiv:2404.05509](https://arxiv.org/abs/2404.05509)) and 2025 ([arXiv:2501.18527](https://arxiv.org/abs/2501.18527)) used deep-annealing neural-network search to extend the continuum of six-colorings of $\mathbb{R}^2$ to $0.354 \leq d \leq 0.657$ (first 30-year improvement on this variant). **Upper-bound side only**; no ML / RL on the lower-bound side yet.

Per-architecture status, intersection with LEARNINGS L20-L22, and three concrete next-experiment ideas in the briefing.

## Open frontiers

- Is $\chi(\mathbb{R}^2) = 5, 6,$ or $7$?
- Can a small ($\leq 1000$ vertex) $6$-chromatic UDG exist?
- Does $\chi_m = \chi$ under MA or some choice-weakening axiom?
- Can the Lovász $\vartheta$ on Cayley graphs of $\mathbb{R}^2$ be computed analytically?
- Is there a "natural" proof method that distinguishes the $\chi \leq 7$ bound from the $\chi \geq 5$ bound asymptotically?
- Is de Grey's 2026 conjecture (for all $d \geq 2$ and $3 \leq n \leq d+2$, there exists a $(d+n-1)$-chromatic $n$-simplex-free UDG in $\mathbb{R}^d$) true? If yes and tight, $\chi(\mathbb{R}^2) = 5$.

## References

- A.D.N.J. de Grey, *The chromatic number of the plane is at least 5*, Geombinatorics 28 (2018).
- A. Soifer, *The Mathematical Coloring Book*, Springer (2009). Definitive reference.
- K.J. Falconer, *The realization of distances in measurable subsets covering $\mathbb{R}^n$*, J. Combin. Theory A 31 (1981).
- L.A. Székely, *Erdős on unit distances and the Szemerédi-Trotter theorems*, Paul Erdős and his Mathematics II, 2002.
- Polymath16, *Hadwiger-Nelson problem*, online project (2018).
- D.R. Woodall, *Distances realized by sets covering the plane*, J. Combin. Theory A 14 (1973). The $\mathbb{Q}^2$ result.
- S. Shelah and A. Soifer, *Axiom of choice and chromatic number of the plane*, J. Combin. Theory A 103 (2003).

### 2024-2026 additions

- G. Sokolov and V. Voronov, *On the chromatic number of the plane for map-type colorings*, [arXiv:2502.01958](https://arxiv.org/abs/2502.01958) (2025).
- V. Voronov, *The chromatic number of the plane with an interval of forbidden distances is at least 7*, [arXiv:2304.10163](https://arxiv.org/abs/2304.10163) (2023).
- J. Parts, *The chromatic number of $\mathbb{R}^8$ is at least 25*, [arXiv:2603.14581](https://arxiv.org/abs/2603.14581) (2026).
- P. Ágoston, *A lower bound on the number of colours needed to nicely colour a sphere*, [arXiv:2404.14398](https://arxiv.org/abs/2404.14398) (2024-2025).
- N. Alon, M. Bucić, L. Sauermann, *Unit and distinct distances in typical norms*, [arXiv:2302.09058](https://arxiv.org/abs/2302.09058) (2023, rev 2024). Almost-all norms on $\mathbb{R}^2$ give $\chi = 4$; sharpens the wrong-approach detector.
- K. Mundinger, M. Zimmer, A. Kiem, C. Spiegel, S. Pokutta, *Neural discovery in mathematics: do machines dream of colored planes?*, [arXiv:2501.18527](https://arxiv.org/abs/2501.18527) (2025).
- K. Mundinger, S. Pokutta, C. Spiegel, M. Zimmer, *Extending the continuum of six-colorings*, [arXiv:2404.05509](https://arxiv.org/abs/2404.05509); Geombinatorics Quarterly (2024).
- F. Vallentin, S. Weißbach, M. C. Zimmermann, *The chromatic number of 4-dimensional lattices*, [arXiv:2407.03513](https://arxiv.org/abs/2407.03513) (2024).
- G. Exoo, D. Ismailescu, *A 5-chromatic same-distance graph in the hyperbolic plane*, [arXiv:2303.06801](https://arxiv.org/abs/2303.06801) (2023).
- Polymath16, *Eighteenth thread: Back with a new conjecture!*, [Short, Fat Matrices blog](https://dustingmixon.wordpress.com/2026/01/17/polymath16-eighteenth-thread-back-with-a-new-conjecture/) (2026-01-17). Includes Haugstrup's triangle-free 6-chromatic UDGs in $\mathbb{R}^4$ and de Grey's structural conjecture.
