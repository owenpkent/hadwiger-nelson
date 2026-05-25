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

Aubrey de Grey constructed a finite unit-distance graph on $1581$ vertices that is not $4$-colorable. Marijn Heule independently verified the construction with a SAT proof. Polymath16 reduced the size of certified $5$-chromatic UDGs to $\sim 510$ vertices.

This replaced the long-standing $\chi \geq 4$ bound from the Moser spindle (1961).

### Upper bound: $\chi \leq 7$ (Isbell, ~1950)

Tile the plane with regular hexagons of diameter slightly less than $1$ (e.g., diameter $\tfrac{7}{8}$). Color the hexagons with $7$ colors in a repeating $7$-color pattern such that any two hexagons sharing the same color are at distance more than $1$ apart. The standard construction uses cells with centers on a hexagonal lattice scaled so that any two same-colored cells are far enough apart.

Refinement: with diameter exactly $1$ and boundary handling, this gives $\chi \leq 7$.

## Variants and refinements

| Variant | Definition | Status |
|---------|------------|--------|
| $\chi(\mathbb{R}^2)$ | full chromatic number, AC available | $5 \leq \chi \leq 7$ |
| $\chi_m(\mathbb{R}^2)$ | **measurable** chromatic number: color classes must be Lebesgue-measurable | $5 \leq \chi_m$; recent: $\chi_m \geq 6$ |
| $\chi_f(\mathbb{R}^2)$ | **fractional** chromatic number | $\chi_f \geq 3.6\ldots$ (Cranston-Rabern) |
| $\chi_B(\mathbb{R}^2)$ | **Borel** chromatic number: color classes Borel | open; sits between $\chi_m$ and $\chi$ |
| $\chi(\mathbb{R}^2)$ in ZF + DC | without full Choice | **Shelah-Soifer**: can differ from ZFC value |

## Four candidate proof architectures

### Architecture 1: Combinatorial / Unit-Distance Graphs

**Goal**: construct a finite UDG in $\mathbb{R}^2$ with chromatic number $\geq 6$ (or $\geq 7$).

**Lineage**: Moser spindle ($\chi = 4$, 1961) $\to$ Golomb graphs $\to$ de Grey ($\chi \geq 5$, 2018) $\to$ Polymath16 (smaller) $\to$ ???.

**Tools**: SAT solvers (cadical, kissat); structured graph construction in number fields $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ etc.; symmetric / group-theoretic constructions.

**Wrong-approach test**: must use the topology / density of $\mathbb{R}$, not just abstract UDG structure (since $\mathbb{Q}^2$ has $\chi = 2$). Constructions that live in a fixed number field $K$ must produce a graph that is *not* $4$-colorable but might be $4$-colorable in some sub-rational structure if extended back; the topology of $\mathbb{R}$ enters through the unbounded supply of algebraic distances.

**Status**: active worldwide. Smallest known $5$-chromatic UDG keeps shrinking. No known $6$-chromatic UDG.

### Architecture 2: Measurable / spectral

**Goal**: prove lower bounds on $\chi_m(\mathbb{R}^2)$, then either (a) prove $\chi_m = \chi$ under reasonable axioms, or (b) push $\chi_m \geq 6$ or $\geq 7$.

**Lineage**: Falconer 1981 ($\chi_m \geq 5$) $\to$ Bukh, Soifer expositions $\to$ Fourier / autocorrelation bounds $\to$ recent $\chi_m \geq 6$ refinements.

**Tools**: Lebesgue measure on $\mathbb{R}^2$; autocorrelation of indicator functions of color classes; Fourier transform on $\mathbb{R}^2$ and the rotation group $O(2)$; harmonic analysis on the Heisenberg group has been explored.

**Wrong-approach test**: must use the 2D rotation group, not just dimension; must not reduce to $\mathbb{R}^1$ (where $\chi = 2$ trivially). Measure-zero issues mean this architecture is exempt from the $\mathbb{Q}^2$ test.

**Status**: active. $\chi_m \geq 6$ is recent; the gap to $\chi(\mathbb{R}^2)$ remains.

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
