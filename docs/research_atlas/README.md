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
| $\chi_B(\mathbb{R}^2)$ | **Borel** chromatic number: color classes Borel | open; sits between $\chi_m$ and $\chi$ |
| $\chi(\mathbb{R}^2)$ in ZF + DC | without full Choice | **Shelah-Soifer**: can differ from ZFC value |
| $\chi_m(\mathbb{H}^2(d))$ | measurable, hyperbolic plane, edge distance $d$ | $\geq 6$ for $d \geq 12$ (DeCorte-Golubev 2018). *Does not transfer to $\mathbb{R}^2$* |
| $\chi$ for convex-tile colorings | color classes are convex polygons of bounded area | $\geq 6$ (Coulson 2002, Townsend-Woodall). Strictly stronger restriction than Lebesgue-measurable |

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

### Architecture 3: Fractional / Lovász $\vartheta$ / spectral

**Goal**: bound $\chi_f(\mathbb{R}^2)$ and the Lovász theta function on (graph powers of) the unit-distance graph, then transfer to $\chi$.

**Lineage**: Cranston-Rabern, Larman-Rogers, work on Cayley graphs of $\mathbb{R}^d$.

**Tools**: linear programming for fractional chromatic; semidefinite programming for Lovász $\vartheta$; spectral analysis of Cayley-graph-like operators on $\mathbb{R}^2$ (Bochner integrals over the rotation group).

**Wrong-approach test**: must distinguish the Euclidean inner product from generic norms (otherwise applies to $L^\infty$ where $\chi = 4$).

**Status**: exploratory. $\chi_f < \chi$ in general, so this gives lower bounds but not equality.

### Architecture 4: Set-theoretic / axiomatic

**Goal**: clarify the dependence of $\chi(\mathbb{R}^2)$ on the axiom system; refine the Borel chromatic number.

**Lineage**: Shelah-Soifer (the chromatic number depends on choice); descriptive set theory (Borel chromatic for graphs on Polish spaces).

**Tools**: forcing; descriptive set theory; effective measure theory.

**Status**: structural. Unlikely to close the gap directly but reframes what "the" chromatic number means.

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
