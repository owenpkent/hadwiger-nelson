# sources/ — Library and reading notes

Annotated catalog of the reference library for the Hadwiger-Nelson program.
Last updated 2026-05-30.

> **Deep reading notes** from a full read of every text live in
> [`notes/`](notes/README.md) (one file per text/cluster, architecture-oriented, with
> theorem statements and page references). This LIBRARY file is the catalog; `notes/` is
> the content. The cross-cutting synthesis (why the $\chi \ge 6$ bottleneck is structural)
> is in [`notes/README.md`](notes/README.md).

This file covers two kinds of material:

1. **Texts** (`books/`, `papers/`): 19 human-readable references added 2026-05-30. First
   wave (11): 8 from Owen's drop + 3 fetched from arXiv (Exoo-Ismailescu, Voronov et al.,
   Bachoc et al.). Second wave (7): the Oliveira-Vallentin SDP / distance-avoiding-set
   lineage (5 items, entries #12-16), the Knuth Dancing Links pre-fascicle (#17), and a
   Hamming-cube distance-graph paper (#18). Third wave (1): the KMOR primary source (#19),
   which corrected a material numerical error in note 08. Notes below are deep: per-text
   bibliographic data, which of the four proof architectures it serves, the specific
   chapters/sections worth reading, and how each connects to the project's current bottleneck.
2. **Machine data** (repo root of `sources/` + `cnp-sat/`): the de Grey / Heule /
   Polymath16 graph files (`.dimacs`, `.vtx`, `.edge`, `.cnf`). These are
   referenced directly by `experiments/` scripts and Lean plans, so they are
   **left in place** (do not move them; paths are hard-coded). See the inventory
   at the bottom.

The four architectures (from `CLAUDE.md`):
- **A1** Combinatorial / unit-distance graphs (SAT-driven)
- **A2** Measurable / spectral (Falconer, Fourier autocorrelation)
- **A3** Fractional / Lovász ϑ
- **A4** Set-theoretic / axiomatic (Shelah-Soifer, Borel χ)

**The current bottleneck** (from project memory, 2026-05-28/29): all three active
architectures bottom out at one missing object, *a χ ≥ 6 unit-distance graph that
embeds in the plane*. Reading notes flag which texts bear on that object directly.

---

## Reading priority at a glance

| # | Text | Arch | Priority | Why |
|---|------|------|----------|-----|
| 1 | Soifer, *Mathematical Coloring Book* | A1/A2/A4 | **read first** | The single canonical HN reference; covers all four architectures. Chs 13-15 are the embedding machinery for the bottleneck. |
| 2 | de Grey 2018 paper | A1 | **read first** | The χ ≥ 5 construction you are extending; you have the graph (`degrey_1585.dimacs`) but this is the assembly logic. |
| 3 | Heule 2019, Trimming Graphs | A1 | **read first** | How a χ ≥ 6 claim is made SAT-verifiable; the 553→529 reduction pipeline. |
| 4 | Knuth TAOCP V4F6, Satisfiability | A1 | high | The SAT encodings/CDCL tricks that make these instances tractable. |
| 5 | Scheinerman-Ullman, *Fractional Graph Theory* | A3 | high | χ_f via LP duality; Ch 3 is the core of the fractional thread. |
| 6 | Stein-Shakarchi, *Fourier Analysis* | A2 | medium | Analytic foundation for autocorrelation / Fourier lower bounds. |
| 7 | Kechris, *Classical Descriptive Set Theory* | A4 | medium | Foundation for Borel chromatic number refinements. |
| 8 | Knuth TAOCP V3, Sorting & Searching | (general) | reference | Data-structures/algorithms backstop; not HN-specific. |
| 9 | Exoo-Ismailescu 2018, χ≥5 new proof | A1 | high | Independent, more geometric χ≥5 route; second assembly logic vs de Grey. |
| 10 | Voronov-Neopryatnaya-Dergachev 2022, embedded 5-chromatic UDGs | A1 | **bottleneck** | Algorithms to embed high-χ UDGs in the plane from a 4-chromatic subgraph; no Moser-spindle base. |
| 11 | Bachoc-DeCorte-Oliveira-Vallentin 2014, spectral bounds for an operator | A2/A3 | high | Hoffman/SDP bounds for the ℝ² operator; bridges Fourier (#6) and χ_f (#5). |

---

## books/

### 1. Soifer-2009-Mathematical-Coloring-Book.pdf
**Alexander Soifer, *The Mathematical Coloring Book: Mathematics of Coloring and the
Colorful Life of its Creators*, Springer, 2009.** ~600 pp. Forewords by Grünbaum,
Johnson, Rousseau.

The indispensable HN reference. Most-cited name across `docs/` (100+ hits) for good
reason: it is the only place that treats the chromatic-number-of-the-plane problem
across history, combinatorics, measure theory, *and* the axiom-of-choice phenomenon
in one volume. Part survey, part primary-source history (Soifer interviewed the
principals).

**Chapter map (page numbers are the book's printed pages):**

Part II — Colored Plane (the HN core):
- **Ch 2** Chromatic Number of the Plane: The Problem (p13) — the statement, 4 ≤ χ ≤ 7.
- **Ch 3** Historical Essay (p21) — Nelson, Isbell, Erdős; provenance of the bounds.
- **Ch 4** Polychromatic Number, Results Near the Lower Bound (p32) — Moser spindle etc.
- **Ch 5** *De Bruijn-Erdős Reduction to Finite Sets* (p39) — **A1 foundation.** The
  compactness theorem that licenses the entire finite-UDG program: χ(ℝ²) = the sup of
  χ over finite unit-distance subgraphs. This is *why* a finite χ ≥ 6 graph would settle
  χ(ℝ²) ≥ 6. (Note: this uses choice; cf. Ch 46 / A4.)
- **Ch 6-7** 6-colorings near the upper bound (p43, p50) — Stechkin, tilings, the
  continuum of 6-colorings. Bears on whether 6 colors can ever suffice.
- **Ch 8** Special Circumstances (p57).
- **Ch 9** *Measurable Chromatic Number of the Plane* (p60) — **A2 foundation.** §9.2
  lower bound for χ_m, §9.3 **Falconer** (χ_m ≥ 5). This is the textbook entry point for
  the measurable thread; pairs with the L35/L36 LP work in `experiments/measurable/`.
- **Ch 10** Coloring in Space (p67) — higher-dimensional analogs.
- **Ch 11** *Rational Coloring* (p72) — **wrong-approach detector.** Woodall's χ(ℚ²) = 2.
  Read this to keep the A1 control object honest: any combinatorial argument that would
  also work over ℚ² is structurally wrong (`experiments/_shared/wrong_approach_detectors.py`).

Part III — Coloring Graphs (the embedding machinery — **most relevant to the bottleneck**):
- **Ch 12** Chromatic Number of a Graph (p79); §12.2 chromatic number and girth (p82) —
  high-girth high-χ graphs, relevant to whether a χ ≥ 6 UDG can avoid small structure.
- **Ch 13** *Dimension of a Graph* (p88); §13.2 **Euclidean Dimension of a Graph** (p93) —
  the formal notion of "embeds in the plane as a unit-distance graph."
- **Ch 14** ***Embedding 4-Chromatic Graphs in the Plane*** (p99) — **directly the
  bottleneck machinery.** O'Donnell's embedding constructions (§14.7), attaching k-cycles
  to foundation sets, removing coincidences (§14.6). This is the technology for turning an
  abstract graph into a *realizable* unit-distance graph. If we have an abstract χ ≥ 6
  graph, this chapter is the playbook for embedding it; if we cannot embed, this chapter
  explains the obstruction.
- **Ch 15** *Embedding World Records* (p110) — smallest known 4-chromatic UDGs by vertex
  count and girth (56-, 47-, 45-, 40-, 23-vertex graphs). Calibration targets for our own
  small-graph search.
- **Ch 16** Edge Chromatic Number (p127); **Ch 17** Thomassen's 7-Color Theorem (p140).

Part IV (Maps), Part V (Erdős, **Ch 26 de Bruijn-Erdős history**, p236), Parts VI-VII
(Ramsey theory) — context, less load-bearing for us.

Part VIII — Euclidean Ramsey Theory (p485): Ch 40-42, monochromatic polygons, Gallai.
Part IX — **Colored Integers in Service of Chromatic Number of the Plane** (p519):
Ch 43-45, O'Donnell's theorem (a 4-chromatic UDG of arbitrarily large girth), built from
arithmetic-progression Ramsey results. Relevant if we pursue girth-based lower bounds.

Part X — Predicting the Future:
- **Ch 46** *What If We Had No Choice?* (p535) — **A4 foundation.** §46.2 axiom of choice
  and relatives, §46.6 **Shelah-Soifer class of graphs**, §46.7 **a unit-distance
  Shelah-Soifer graph** (p549) whose chromatic number depends on the choice axioms. This
  is the textbook source for the axiomatic architecture and the ZF+DC vs ZFC distinction.
- **Ch 47** Conditional vs unconditional CNP theorems (p553); **Ch 48** foundations.

Bibliography 800+ items (p569), name + subject indexes.

---

### 2. Knuth-TAOCP-Vol4-Fascicle6-Satisfiability.pdf
**Donald E. Knuth, *The Art of Computer Programming, Volume 4, Fascicle 6:
Satisfiability*, Addison-Wesley, 2015.** (ISBN 978-0-13-439760-3.) This is **§7.2.2.2**
of TAOCP, ~310 pp.

**A1 engine-room reference.** The de Grey / Polymath16 / Heule lineage decides
k-colorability of finite UDGs with SAT solvers; this fascicle is the authoritative
treatment of the solver technology and, crucially, the *encodings*. Read for:
- CNF encoding of graph coloring (one-hot color variables + edge clauses + symmetry
  breaking) — exactly the encoding in `experiments/combinatorial/`.
- CDCL (conflict-driven clause learning), the algorithm behind cadical/kissat/cryptominisat.
- Certificates of unsatisfiability and **clausal (DRAT) proofs** — the bridge to Heule's
  paper (#3) and to a *verifiable* χ ≥ 6 claim.
- Symmetry breaking, autarkies, Tseitin transforms, and the encoding choices that decide
  whether a ~500-2000 vertex instance is seconds or intractable.
- Knuth's own SAT solver implementations and the exercises (with answers) are a practical
  cookbook.

When the combinatorial thread stalls on solver performance, the fix is usually an encoding
trick documented here.

---

### 3. Scheinerman-Ullman-Fractional-Graph-Theory.pdf
**Edward R. Scheinerman & Daniel H. Ullman, *Fractional Graph Theory: A Rational Approach
to the Theory of Graphs*, Wiley 1997 / free author PDF (©2008).** Foreword by Claude Berge.
Freely redistributable (the copyright page grants copy/print rights).

**A3 core reference.** The clean, self-contained treatment of LP-relaxed graph invariants.
For us:
- **Ch 1** General Theory — the hypergraph-covering / LP-duality framework that every
  "fractional X" specializes. Sets up the primal-dual pattern (χ_f as a covering LP, its
  dual a packing LP) that the fractional thread and the Lovász-ϑ work both use.
- **Ch 3** *Fractional Chromatic Number* — **the chapter.** χ_f(G) = min fractional
  coloring = max fractional clique (by LP duality); χ_f ≤ χ; relation to independence
  ratio. This is the rigorous backbone for `experiments/fractional/`. The plane's
  fractional chromatic number χ_f(ℝ²) is a real-valued lower-bound target (known ≥ ~4.36,
  via measurable-set / density arguments) that does not require an integer χ ≥ 6 graph,
  so A3 is the architecture that can make *continuous* progress while A1 is stuck.
- **Ch 4** Fractional Edge Coloring; **Ch 6** Fractional Isomorphism — peripheral.

Ties to the wrong-approach detector: χ_f(ℚ²) and the measurable density ratio are the
control quantities; an LP bound that ignores Euclidean rigidity will not separate ℝ² from
the ℓ^∞ plane (χ = 4).

---

### 4. Stein-Shakarchi-2003-Fourier-Analysis.pdf
**Elias M. Stein & Rami Shakarchi, *Fourier Analysis: An Introduction* (Princeton Lectures
in Analysis, Vol. I), Princeton Univ. Press, 2003.**

**A2 analytic foundation.** Not HN-specific; it supplies the harmonic-analysis machinery
the measurable/spectral thread leans on:
- Fourier series and the Fourier transform on ℝ and ℝ^d.
- **Poisson summation** and convolution — the tools behind autocorrelation/Fourier lower
  bounds on χ_m (the Bukh / Ambrus-Matolcsi line that our L35/L36 LP work reproduces).
- Positive-definite functions and the spectrum of convolution operators (entry point to
  the Bachoc-DeCorte-Oliveira-Vallentin SDP bounds — *that* paper is a gap, see below).

This is Volume I (foundations). The heavier real/functional analysis is in Stein-Shakarchi
Vols III-IV, which we do **not** have; for measure-theoretic χ_m arguments at full strength
(Lebesgue density, measurable selectors) Vol III (*Real Analysis*) would be the next add.

---

### 5. Kechris-1995-Classical-Descriptive-Set-Theory.pdf
**Alexander S. Kechris, *Classical Descriptive Set Theory*, Springer GTM 156, 1995.**

**A4 foundation.** The standard graduate text on Polish spaces and the Borel/projective
hierarchies. Relevant to the *Borel chromatic number* refinement of the axiomatic
architecture: instead of asking for an arbitrary (choice-dependent) coloring, ask for a
*Borel-measurable* coloring of the plane, where χ_Borel(ℝ²) is well-defined without the
Shelah-Soifer pathology.
- Polish spaces, Borel sets, the Borel hierarchy — Chs I-II.
- Analytic / coanalytic sets, projective hierarchy — Chs III-IV.
- The infrastructure for *descriptive combinatorics* (Borel graph colorings).

Caveat: the canonical reference for **Borel chromatic numbers** specifically is
Kechris-Solecki-Todorcevic, "Borel chromatic numbers," *Adv. Math.* 1999 — a paper we do
**not** have (see gaps). Kechris's book is the prerequisite, not the result.

---

### 6. Knuth-TAOCP-Vol3-Sorting-and-Searching.pdf
**Donald E. Knuth, *The Art of Computer Programming, Volume 3: Sorting and Searching*,
2nd ed., Addison-Wesley.**

General CS reference, **not HN-specific.** Useful as a backstop for the data-structure and
algorithm questions that come up implementing graph search (hashing/coincidence detection
when embedding vertices in number fields, sorting edge lists, etc.). Lowest priority of the
set for the mathematics; keep for implementation craft. (Note: my original suggestion was
Vol 4 Fascicle 6 for SAT — that arrived too, as #2. This Vol 3 is a bonus, not a substitute.)

---

## papers/

### 7. deGrey-2018-Chromatic-Number-Plane-At-Least-5_arXiv-1804.02385v3.pdf
**Aubrey D.N.J. de Grey, "The chromatic number of the plane is at least 5,"
arXiv:1804.02385 (2018).** Geombinatorics 28 (2018).

**A1, read first.** The breakthrough: a finite unit-distance graph (1581 vertices in the
published construction) that is not 4-colorable, hence χ(ℝ²) ≥ 5. We hold the *graph*
(`degrey_1585.dimacs`, `degrey_1585_vertices.sage`) but this paper is the *construction
logic*: the hexagonal "H" of 7-vertex pieces, the spindle-of-spindles assembly, the role of
the √3 / √11 coordinates, and the argument that 4-coloring forces a contradiction. To extend
toward χ ≥ 6 you must understand *why* this works at 5, which is here, not in the DIMACS.

### 8. Heule-2019-Trimming-Graphs-Clausal-Proof-Optimization_arXiv-1907.00929v2.pdf
**Marijn J.H. Heule, "Trimming Graphs Using Clausal Proof Optimization," arXiv:1907.00929
(2019).** CP 2019.

**A1, read first.** The verification/minimization methodology. Heule reduces the smallest
known χ = 5 unit-distance graph from **553 vertices / 2720 edges to 529 / 2670** by
exploiting the link between proof size and unsatisfiable-core size: postpone clause deletion
to compute a small unsat core. Two things for us: (a) this is *how a χ ≥ 6 claim becomes
checkable* (a trimmed DRAT proof a third party can verify, as was done for de Grey); (b) the
529-vertex graph is in our data as `cnp-sat/edge/529.edge` / `sources/cnp-sat/vtx/529.vtx`.
Pairs with Knuth V4F6 (#4) on the solver side and with the Polymath16 reduction lineage.

### 9. ExooIsmailescu-2018-Chromatic-Number-Plane-At-Least-5-New-Proof_arXiv-1805.00157.pdf
**Geoffrey Exoo & Dan Ismailescu, "The chromatic number of the plane is at least 5 — a new
proof," arXiv:1805.00157 (2018); Discrete Comput. Geom. 2020.** (Added 2026-05-30.)

**A1.** An *independent, more geometric* route to χ ≥ 5, found in parallel with de Grey.
Different graph family ("Exoo-Ismailescu graphs"), different uncolorability argument. Value
for us: a second assembly logic to compare against de Grey's — where the two constructions
agree on *what forces* 5 colors is a hint about what would force 6. Smaller/cleaner than the
1581-vertex graph in places.

### 10. Voronov-Neopryatnaya-Dergachev-2022-Constructing-5-Chromatic-Unit-Distance-Graphs-Embedded-in-Plane-and-Spheres_arXiv-2106.11824.pdf
**V.A. Voronov, A.M. Neopryatnaya, E.A. Dergachev, "Constructing 5-chromatic unit distance
graphs embedded in the Euclidean plane and two-dimensional spheres," arXiv:2106.11824 (v4,
2022); Discrete Math. 2022.** (Added 2026-05-30.)

**A1 — most directly on the bottleneck.** Develops *algorithms* for finding unit-distance
graphs with χ > 4 that are **embedded in the plane** (and on 2-spheres), built from a given
4-chromatic UDG subgraph. Constructs a series of 5-chromatic UDGs on 64513 vertices in the
plane that, notably, **do not use the Moser spindle as the base element** — i.e. a fresh
embedding strategy, not the standard spindle-of-spindles. This is the closest thing in the
library to a constructive recipe for "take an abstract high-χ graph and realize it as a
planar unit-distance graph," which is exactly the operation the χ ≥ 6 bottleneck needs.
Pairs with Soifer Chs 13-15 (the theory of that same embedding operation). The Polymath16
lineage's most useful *embedding-focused* publication, standing in for the (never cleanly
arXiv'd) Polymath16 paper.

### 11. Bachoc-DeCorte-Oliveira-Vallentin-2014-Spectral-Bounds-Independence-Ratio-Chromatic-Number-Operator_arXiv-1301.1054.pdf
**C. Bachoc, E. DeCorte, F.M. de Oliveira Filho, F. Vallentin, "Spectral bounds for the
independence ratio and the chromatic number of an operator," arXiv:1301.1054 (2013); Israel
J. Math. 202 (2014) 227-254.** (Added 2026-05-30.)

**A2/A3 — the research-strength roadmap for the spectral/fractional thread.** Defines the
independence ratio and chromatic number of a bounded self-adjoint operator on an L²-space
and proves Hoffman-type spectral bounds via the numerical range. This is the framework that
turns "lower-bound χ_m(ℝ²)" into a harmonic-analysis + convex-optimization problem (the
Lovász-ϑ / SDP analog for the infinite geometric graph on ℝ²). It is the conceptual bridge
between Stein-Shakarchi (#6, the Fourier machinery) and Scheinerman-Ullman (#5, the LP-duality
view of χ_f), at the level the L35/L36 LP work in `experiments/measurable/` and
`experiments/fractional/` is reaching toward. Read for the operator-theoretic generalization
of the Hoffman bound and its specialization to Euclidean-space and sphere graphs.

---

## Second wave (added 2026-05-30): the SDP / distance-avoiding-set lineage

These five (#12-16) are the Oliveira-Vallentin school of SDP + harmonic-analysis bounds for
geometric distance graphs. They were the prior top library gap. Deep joint notes:
[`notes/08-sdp-harmonic-analysis-oliveira-vallentin.md`](notes/08-sdp-harmonic-analysis-oliveira-vallentin.md)
(corrected against the KMOR primary, #19 / [`notes/11`](notes/11-keleti-matolcsi-oliveira-ruzsa-avoiding-sets.md)).
Headline result of the cluster: these methods give the EXACT completely-positive
characterization of the avoiding-set density $m_1(\mathbb{R}^n)$ and a convergent hierarchy.
The planar density bounds, in order: 2-point LP $0.2683$; KMOR 2016 $m_1 \le 0.258795$ (just
short, $\chi_m \ge 4$); and **Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 $m_1 \le 0.246894 <
1/4$, giving $\chi_m(\mathbb{R}^2) \ge 5$** by the $1/m_1$ density bound (reproduced and
self-certified in-repo, LEARNINGS L35/L36). So the density route DOES reach $\chi_m \ge 5$.
$\chi_m \ge 5$ is ALSO Falconer 1981 (separate). The route is then CAPPED: $\chi_m \ge 6$ is
**unreachable** by single-class density (Croft's explicit density-0.22936 avoiding set forces
$1/m_1 \le 4.36 < 5$). A2/A3.

### 12. DeCorte-Oliveira-Vallentin-2022-Complete-Positivity-and-Distance-Avoiding-Sets_MathProg.pdf
**E. DeCorte, F.M. de Oliveira Filho, F. Vallentin, "Complete positivity and distance-avoiding
sets," Math. Programming 191 (2022) 487-558** (accepted 2020). **The central paper.** Introduces
the cone of completely positive functions and uses it to characterize the maximum density
$m_1(\mathbb{R}^n)$ of a distance-avoiding set *exactly* as a convex optimization problem, with
a convergent Lasserre-type hierarchy $\vartheta' = \mathrm{las}_1 \ge \mathrm{las}_2 \to \alpha$.
This is the research-strength version of the repo's L35/L36 LP crossing.

### 13. Oliveira-2016-Semidefinite-Programming-Upper-Bounds-for-Packing-Problems_survey.pdf
**F.M. de Oliveira Filho, "Semidefinite programming upper bounds for packing problems" (2016
lecture-notes/survey).** The unifying framework: how SDP/theta bounds packing densities and,
by duality, independence ratios and chromatic numbers on $\mathbb{R}^n$ and $S^{n-1}$. Best
single entry point to the method.

### 14. Vallentin-2008-Lecture-Notes-Semidefinite-Programs-and-Harmonic-Analysis_arXiv-0809.2017.pdf
**F. Vallentin, "Lecture notes: semidefinite programs and harmonic analysis," arXiv:0809.2017
(2008).** Pedagogical derivation of the theta number for distance graphs via positive
Hilbert-Schmidt kernels and the reduction (under rotation invariance) to Bessel / Gegenbauer
problems. The "how the machinery works" reference.

### 15. Vallentin-2014-Spectral-Bounds-and-SDP-Hierarchies-for-Geometric-Packing_slides.pdf
**F. Vallentin, Simons Institute slides (2014).** High-level roadmap of spectral bounds and SDP
hierarchies for geometric packing; image-heavy (sparse extractable text). Orientation, not detail.

### 16. Briet-Oliveira-Vallentin-2010-PSD-Grothendieck-Problem-with-Rank-Constraint_arXiv-0910.5765.pdf
**J. Briet, F.M. de Oliveira Filho, F. Vallentin, "The positive semidefinite Grothendieck problem
with rank constraint," arXiv:0910.5765 (2010).** The SDP-rounding / relaxation toolkit (rank-
constrained PSD optimization). More tangential to HN: relevant to the rounding side of the SDP
hierarchy, not a direct chromatic bound.

---

## Second wave: A1 search and adjacent

### 17. Knuth-TAOCP-Vol4-PreFascicle5C-Dancing-Links.pdf
**Donald E. Knuth, TAOCP Vol 4, Pre-Fascicle 5C: "Dancing Links" (2019 draft, 276 pp).**
**A1, alternative search engine.** Algorithm X + the dancing-links data structure for exact
cover, and exact-cover-with-colors (XCC) onto which graph coloring maps. Notes:
[`notes/09-knuth-dancing-links.md`](notes/09-knuth-dancing-links.md). Verdict: strong for
*enumerating* colorings and witness extraction, but it proves non-colorability only by
exhaustive search with **no compact certificate** (unlike SAT + DRAT), so for the χ ≥ 6 UNSAT
certification the SAT toolchain (notes 06) stays primary; DLX is a complementary cross-check.

### 18. Balogh-Chen-Li-2026-Forbidding-Exactly-One-Hamming-Distance_arXiv-2604.05607.pdf
**J. Balogh, C. Chen, B. Li, "Forbidding exactly one Hamming distance," arXiv:2604.05607 (2026).**
**Adjacent / tangential.** $s$-independence numbers of the Boolean-cube Hamming-distance graph
$H_r(n)$ via sunflower-free / Frankl-Wilson extremal methods. Notes:
[`notes/10-balogh-chen-li-hamming-distance.md`](notes/10-balogh-chen-li-hamming-distance.md).
No direct $\chi(\mathbb{R}^2)$ bound; value is methodological (A3 independence-ratio methods),
with the caveat that cube methods use only translation invariance (no $O(2)$), so a naive
Euclidean transfer would fail the wrong-approach detector.

---

## Third wave (added 2026-05-30): the KMOR primary source

### 19. Keleti-Matolcsi-Oliveira-Ruzsa-2016-Better-Bounds-for-Planar-Sets-Avoiding-Unit-Distances_arXiv-1501.00168.pdf
**T. Keleti, M. Matolcsi, F.M. de Oliveira Filho, I.Z. Ruzsa, "Better bounds for planar sets
avoiding unit distances," Discrete Comput. Geom. 55 (2016) 642-661** (arXiv:1501.00168). **A2/A3.**
The primary source for the planar avoiding-set density $m_1(\mathbb{R}^2)$, repeatedly cited by
the SDP cluster (#12-16). Notes:
[`notes/11-keleti-matolcsi-oliveira-ruzsa-avoiding-sets.md`](notes/11-keleti-matolcsi-oliveira-ruzsa-avoiding-sets.md).
Reading it **corrected a material number error** in note 08: KMOR's proven UPPER bound is
$m_1(\mathbb{R}^2) \le 0.258795$ (Thm 3.1, via Moser-spindle subgraph + 6-point
inclusion-exclusion constraints on the Oliveira-Vallentin LP), giving $\chi_m(\mathbb{R}^2) \ge 4$
(just short of $1/4$). The figure $0.229$ ($= 0.22936$) that note 08 had used is Croft's LOWER
bound (an explicit construction). Note: the density route's actual crossing into
$\chi_m(\mathbb{R}^2) \ge 5$ came LATER, with Ambrus et al. 2023 ($m_1 \le 0.246894 < 1/4$, repo
L35/L36); KMOR 2016 was the just-short predecessor. KMOR also proves the block-structure result
(block-structured avoiding sets have density $< 1/(2n)$).

---

## Machine data inventory (left in place — paths are referenced by code)

Referenced by `experiments/combinatorial/*.py`, `experiments/fractional/e3f_*.py`,
`experiments/LEARNINGS.md`, several `orchestrator_sessions/*.md`, and `lean/SHOT4_PLAN.md`.
**Do not move or rename these.**

Top level of `sources/`:
- `degrey_1585.dimacs`, `degrey_1585_sat.dimacs` — de Grey graph as CNF / SAT instance.
- `degrey_1585_vertices.sage` — exact symbolic vertex coordinates (Sage).
- `heule_826.{vtx,edge}`, `heule_874.{vtx,edge}` — Heule intermediate graphs.
- `polymath16_387.vtx`, `polymath16_525e2605.vtx`, `polymath16_799.vtx` — Polymath16 graphs.

`sources/cnp-sat/` (the Polymath16 SAT toolchain, vertex/edge/CNF families):
- `edge/`, `vtx/` — graph families at 510, 517, 529, 553, 610, 633, 803, 826, 874 vertices
  (plus `L403`, `S199`, `T721`, `G2167` variants). These are the reduced χ = 5 graphs.
- `cnf/` — DIMACS CNF (`*-4.cnf`) and symmetry-broken (`*-4-sbp.cnf`) k=4 colorability
  instances. UNSAT on these = χ ≥ 5.
- `check/` — `check_dist_one.py` (verifies edges are exactly unit distance), `run.sh`,
  `.singular` files (exact-arithmetic distance checks via Singular).
- `color.c` — coloring driver.

---

## Gaps — texts we still do NOT have (candidate next adds)

Mapped to architecture and to the bottleneck. (Exoo-Ismailescu, Voronov et al., and
Bachoc et al. were on this list and have since been acquired — now #9, #10, #11 above.)

- **Polymath16 paper (D.H.J. Polymath, Geombinatorics) / wiki** (A1) — there is **no clean
  standalone arXiv PDF**; the project's writeup went to Geombinatorics and the working record
  lives on Dustin Mixon's blog (dustingmixon.wordpress.com, "Polymath16" threads 1-18, the
  18th posted 2026-01-17 with a new conjecture). Voronov et al. (#10) is the best embedding-
  focused stand-in we have. If we want the reduction narrative (1581 → ~510), it must be
  scraped from the blog threads / wiki rather than downloaded as a paper.
- **Falconer, "The realization of distances in measurable subsets covering ℝⁿ,"
  J. Combin. Theory A (1981)** (A2) — the original χ_m ≥ 5 source (we have Soifer's
  secondary account in Ch 9, not the paper). Not on arXiv (pre-arXiv era); would need a
  journal/library copy.
- **Kechris-Solecki-Todorcevic, "Borel chromatic numbers," Adv. Math. (1999)** (A4) — the
  actual Borel-χ result for which Kechris's book (#5) is the prerequisite. Not on arXiv.
- **Brass, Moser, Pach, *Research Problems in Discrete Geometry* (Springer, 2005)** —
  problem-list context situating HN among neighbors.
- **Graham, Rothschild, Spencer, *Ramsey Theory*** — the Euclidean-Ramsey backbone (Soifer
  Parts VI-VIII cover much of this secondarily).

---

## Note on git / repo size

These PDFs total ~107 MB (Kechris 33 MB and Knuth V3 48 MB dominate). They are currently
**untracked**. Recommendation: add `sources/books/` and `sources/papers/` (or `*.pdf`) to
`.gitignore` rather than committing copyrighted texts and bloating the repo. The machine
data (`.dimacs/.vtx/.edge/.cnf`) is small and already tracked; keep tracking it. Decide
before the next `git add -A`.
