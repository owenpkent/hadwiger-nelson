# Architecture 1 dossier: SAT-driven combinatorial lower bounds on $\chi(\mathbb{R}^2)$, 2018 to present

**Sub-corpus**: finite unit-distance graph (UDG) constructions in $\mathbb{R}^2$ whose non-$k$-colorability is certified by SAT, from de Grey 2018 to the present.

**Scope**: lower-bound side of Hadwiger-Nelson, Architecture 1 only. Measurable / Falconer ($\chi_m$) work, fractional / Lovász $\vartheta$ work, and Borel chromatic work belong to Architectures 2, 3, and 4 and appear only when they touch the SAT lineage. The fractional bound $\chi_f(\mathbb{R}^2) \geq 4$ of Matolcsi-Ruzsa-Varga-Zsamboki (2023) is noted as a cross-reference, not analyzed here.

**Methodology caveat**: the de Grey paper PDF and several MathWorld pages returned 403 / binary-only on direct fetch. Where I have not read primary text I have flagged claims as "abstract only" or "secondary source". Citations are arXiv IDs unless otherwise noted.

---

## 1. Chronology

### 1.1 The 2018 breakthrough

**[2018, April] A. D. N. J. de Grey, *The chromatic number of the plane is at least 5*, arXiv:1804.02385; Geombinatorics 28 (2018).**
The first finite UDG in $\mathbb{R}^2$ with $\chi \geq 5$. The published graph has 1581 vertices. The construction proceeds by three named building blocks. $H$ is the 7-point hexagonal lattice neighborhood (the 7 points of the triangular lattice of norm at most 1). $L$ is built from 4 rotated copies of $H$ and forces certain monochromatic configurations; with one choice $L$ has 121 vertices and yields a human-readable argument. $M$ is built from many aligned copies of the Moser spindle (1345 vertices); the full 1581-vertex graph combines $M$ with the constraint structure that $L$ imposes. SAT verification (cadical / Glucose) confirms non-$4$-colorability. Coordinates live in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ (the Moser spindle field), enlarged as needed by additional rotations. *Construction details summarized from Mixon's Polymath16 thread #1 (dustingmixon.wordpress.com, 2018-04-14) and the de Grey arXiv abstract; the full PDF was not directly readable in this session.*

**[2018, April] Polymath16 launches.** Proposed by Gil Kalai, Jordan Ellenberg, Noam Elkies, and Terence Tao on the polymathprojects.org blog (2018-04-10) and hosted on Dustin Mixon's *Short, Fat Matrices* blog. Goal: shrink de Grey's graph and explore $\chi \geq 6$. Runs through seventeen threads, April 2018 to February 2021. ([dustingmixon.wordpress.com](https://dustingmixon.wordpress.com/category/polymath/), [polymathprojects.org](https://polymathprojects.org/2018/04/10/polymath-proposal-finding-simpler-unit-distance-graphs-of-chromatic-number-5/))

**[2018, May] M. J. H. Heule, *Computing small unit-distance graphs with chromatic number 5*, arXiv:1805.12181.**
Heule applies clausal-proof minimization (CPM): take a SAT proof that $G$ is not $4$-colorable, extract a small unsatisfiable core, then geometrically realize the corresponding subgraph back in $\mathbb{R}^2$. This produces several 553-vertex 5-chromatic UDGs. Iterating CPM with symmetry-aware vertex selection then yields a 529-vertex graph (paper reports 529 vertices, 2630 edges). Validation in seconds with `cadical`; finding the graph took roughly $10^5$ CPU-hours.

**[2018, May] G. Exoo and D. Ismailescu, *The chromatic number of the plane is at least 5: a new proof*, arXiv:1805.00157.**
Independent construction containing the Moser spindle as a subgraph. The arXiv abstract is brief and does not commit to a vertex count comparable to de Grey's; I have not read the full PDF in this session. Filed here as an independent confirmation rather than a competitive size record.

### 1.2 The Polymath16 shrinking phase (2018-2020)

**[2019, August] J. Parts, 510-vertex UDG.** First publicly announced by Parts on the Polymath16 13th thread (dustingmixon.wordpress.com, 2019-07-08). A vertex selection / pruning algorithm different from Heule's CPM, iterating on Heule's 529-vertex graph. 510 vertices, 2508 edges. Held the record for about a year.

**[2019] Intermediate Heule / Parts records (525, 517, 529).** From the Polymath16 13th-thread summary: Heule 529 (2630 edges), Parts 525 (2605 edges, 428 Moser spindles), Heule 517 (2579 edges, with 120-degree rotational symmetry), Parts 510 (2508 edges). The Heule 517 result imports symmetry-breaking ideas from arXiv:1907.00929.

**[2020] J. Parts, *Graph minimization, focusing on the example of 5-chromatic unit-distance graphs in the plane*, arXiv:2010.12665; Geombinatorics 29/4 (2020), 137-166.**
Introduces a "preserve-a-property" minimization framework: rather than minimizing arbitrary subgraph properties, the algorithm preserves a checkable property (here, non-$4$-colorability via SAT) and iteratively deletes vertices. Output: **509 vertices, 2442 edges**. This is the current record (see section 2).

**[2020] J. Parts, *The chromatic number of the plane is at least 5: a human-verifiable proof*, arXiv:2010.12661.**
Restructures the de Grey argument so that the unsatisfiability core can be checked by hand rather than by SAT. The graph used is larger than 509 vertices (the abstract emphasizes verifiability, not minimality). Important as a structural counter-narrative: it shows SAT was a convenience, not a logical necessity, for the $\chi \geq 5$ proof.

### 1.3 Polymath16 closes; sphere and variant work (2021-2022)

**[2021, February] Polymath16 declares victory.** Mixon, *Polymath16, seventeenth thread: Declaring victory* (dustingmixon.wordpress.com, 2021-02-01). After roughly 1000 days, the project finalizes a D.H.J. Polymath paper for *Geombinatorics*. Records at closure: smallest 5-chromatic UDG = 509 vertices (Parts), no 6-chromatic UDG, fractional chromatic lower bound around $3.98$.

**[2021, June] V. Voronov, A. Neopryatnaya, E. Dergachev, *Constructing 5-chromatic unit distance graphs embedded in the Euclidean plane and two-dimensional spheres*, arXiv:2106.11824; *Discrete Math.* (2022).**
Two structural innovations. First, 5-chromatic UDGs in $\mathbb{R}^2$ on 64513 vertices that **do not contain a Moser spindle as a subgraph**. This is the first such example: every prior $\chi \geq 5$ UDG (de Grey, Heule, Parts) used spindles as the load-bearing 4-chromatic motif. Second, 5-chromatic graphs of 372 and 972 vertices realized on $S^2$ (the unit sphere): the 372-vertex graph sits on the circumsphere of a regular icosahedron with unit edges; the 972-vertex one on the great icosahedron. These give $\chi(S^2_r) \geq 5$ for the corresponding radii. The 64513-vertex plane graph is structurally different from the Parts / Heule lineage and is not currently competitive on vertex count.

**[2022] J. Parts, *A 6-chromatic odd-distance graph in the plane*, arXiv:2206.12632; Geombinatorics 31/3 (2022), 124-137.**
Builds a finite subgraph of the **odd-distance graph** (vertices = $\mathbb{R}^2$, edges = pairs at odd-integer distance) with chromatic number 6. The odd-distance graph is *not* the unit-distance graph; whether the construction transfers to UDGs is open. Parts proposes it as a stepping stone toward a 6-chromatic UDG, motivated by Heule's earlier suggestion that the odd-distance setting is "easier" because there is no unit-rigidity constraint to enforce. *Important structural note (Davies and others 2024, *Odd distances in colourings of the plane*, arXiv:2209.15598 + GAFA 2024): the odd-distance graph itself has no finite chromatic number, so finite 6-chromatic subgraphs of it exist trivially in some sense; Parts' contribution is the small explicit construction.*

**[2022] J. Parts, *A small 6-chromatic two-distance graph in the plane*, arXiv:2010.12656.**
A 16-vertex graph in $\mathbb{R}^2$ with two forbidden distances ($1$ and some $d$) that is 6-chromatic. This is for the two-distance variant, not the single-distance Hadwiger-Nelson problem, but shows that 6-chromaticity in $\mathbb{R}^2$ is reachable in adjacent problems with very small graphs. Confirms the Mundinger-Pokutta et al. and "two forbidden distances" literature.

### 1.4 Variant problems and indirect approaches (2023-2025)

**[2023] M. Matolcsi, I. Z. Ruzsa, D. Varga, P. Zsamboki, *The fractional chromatic number of the plane is at least 4*, arXiv:2311.10069.**
$\chi_f(\mathbb{R}^2) \geq 4$, improved from Cranston-Rabern's $76/21 \approx 3.619$ (arXiv:1501.01647). Uses a 27-vertex finite UDG and the amenability of the Euclidean group. Architecture 3, not Architecture 1, but uses a small finite UDG and is the most recent SAT-adjacent finite-graph lower bound. Listed for cross-architecture coherence.

**[2024] K. Mundinger, S. Pokutta, C. Spiegel, M. Zimmer, *Extending the continuum of six-colorings*, arXiv:2404.05509; Geombinatorics Quarterly (2024).**
**Upper-bound side** (off-diagonal variant): extends the interval of distances $d$ for which a six-coloring of $\mathbb{R}^2$ forbidding distance 1 in five colors and distance $d$ in the sixth exists, to $0.354 \leq d \leq 0.657$. First 30-year improvement on this variant. Discovered via gradient-based optimization with neural-network approximators of color classes. Listed because it is an ML-driven feasibility computation, methodologically adjacent to SAT-driven lower-bound work.

**[2025] K. Mundinger, M. Zimmer, A. Kiem, C. Spiegel, S. Pokutta, *Neural discovery in mathematics: do machines dream of colored planes?*, arXiv:2501.18527.**
Successor to the 2024 paper. Reformulates plane-coloring feasibility problems as differentiable losses and searches with neural networks. Two new six-colorings of $\mathbb{R}^2$ (off-diagonal variant). Methodologically interesting as the first time a non-SAT computational paradigm has produced new HN-related constructions; for Architecture 1, the relevant signal is that neural search may complement SAT for the upper-bound side, with no comparable result yet on the lower-bound side.

---

## 2. Smallest known $\chi \geq 5$ UDG today

**Jaan Parts (2020), 509 vertices, 2442 edges, coordinates in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$, certified by SAT.** ([arXiv:2010.12665](https://arxiv.org/abs/2010.12665); Geombinatorics 29/4 (2020), 137-166.) Contains the Moser spindle and Heule spindle as subgraphs.

This has been the record since 2020. No further shrinking has been published as of this survey (current date: 2026-05-25). The Voronov-Neopryatnaya-Dergachev 64513-vertex graph (2021) is structurally distinct in that it is Moser-spindle-free, but is much larger.

---

## 3. What has been tried toward $\chi \geq 6$ in $\mathbb{R}^2$

**No 6-chromatic UDG in $\mathbb{R}^2$ is known.** The Polymath16 wiki ([michaelnielsen.org/polymath](https://michaelnielsen.org/polymath/index.php?title=Hadwiger-Nelson_problem)) explicitly lists "Find a 6-chromatic unit-distance graph in the plane" as Goal 3, unsolved.

Documented attempts and obstructions:

1. **Direct SAT scaling.** Naive extension of the de Grey / Heule pipeline to $\chi \geq 6$ requires graphs large enough to fail $5$-coloring. Polymath16 third thread (Mixon, 2018-05-01) discusses this. The combinatorial branch space is roughly $5^V$ per assignment vs $4^V$ for $\chi \geq 5$, and the structural lemmas that drove the de Grey argument (e.g., the $H$-blocks forcing monochromatic triples in any $4$-coloring) have no obvious 5-coloring analog.

2. **Algebraic ring enlargements.** Several Polymath16 threads discuss embedding the search in $\mathbb{Z}[\omega_1, \omega_3, \omega_4, \zeta]$ for various $\zeta$ and asking whether this ring admits a homomorphic 5-coloring. Each extension that has been computed admits a 5-coloring. No $\zeta$ has been found that blocks all 5-colorings.

3. **Odd-distance proxy (Parts 2022, arXiv:2206.12632).** Heule proposed: construct a 6-chromatic *odd-distance* graph first because the constraint "distance is an odd integer" is more flexible than "distance equals 1". Parts succeeded for odd-distance, but the construction has not been transported back to unit-distance. The transport step is the hard one and remains open.

4. **Two-distance / off-diagonal variants.** 6-chromatic graphs exist with as few as 16 vertices for two-distance (Parts, arXiv:2010.12656) and there are 6-chromatic constructions for the two-distance plane (1 and $d$) for various $d$. These do not give $\chi(\mathbb{R}^2) \geq 6$ since they use a second forbidden distance, but they suggest that the obstruction to 6-chromatic single-distance graphs is specific to the rigidity of the unit-distance graph, not to 6-chromaticity per se.

5. **Sphere transport (Voronov-Neopryatnaya-Dergachev).** 5-chromatic on $S^2$ has been done; 6-chromatic on $S^2$ would not directly imply $\chi(\mathbb{R}^2) \geq 6$ (the sphere and plane have different rigidity), but would be progress on a related structure. Not yet achieved.

6. **Neural / ML methods (Mundinger-Pokutta lineage, 2024-2025).** So far applied only to the upper-bound side. No published attempt at neural-network search for 6-chromatic UDGs as of the 2501.18527 preprint.

**Rumor / unverified flag**: discussion threads (Mixon's blog, dustingmixon comments) periodically mention private experiments with $> 100{,}000$-vertex candidate graphs. None has resulted in a published $\chi \geq 6$ result. I have no evidence of an unpublished construction; treat any rumor as unverified.

---

## 4. Open computational questions (concrete, tractable-looking SAT instances)

Drawn from Polymath16 wiki goals and the literature:

1. **Sub-509-vertex 5-chromatic UDG.** Iterate Parts' "preserve-a-property" minimization with newer SAT solvers (kissat 3.x) and better unsat-core extraction. No published attempt since 2020.

2. **Moser-spindle-free 5-chromatic UDG with $V < 64513$.** Voronov-Neopryatnaya-Dergachev's graph is huge; the natural question is the minimum vertex count for a *Moser-spindle-free* 5-chromatic UDG. Open both for the plane and for $S^2$.

3. **Triangle-free 5-chromatic UDG.** Exoo-Ismailescu's 17-vertex triangle-free 4-chromatic UDG is small; lifting to triangle-free 5-chromatic in fewer than 509 vertices is plausible because the geometry is less rigid. Listed in the Polymath16 wiki and in the Springer 2024 volume *The New Mathematical Coloring Book* (chapter on triangle-free constructions).

4. **6-chromatic UDG with $V \leq 10000$.** No published systematic search. The branching factor argument suggests this is at the edge of tractability for current SAT solvers if a good seed structure is found.

5. **Lifting odd-distance Parts graph to UDG.** Parts' 2022 odd-distance 6-chromatic graph is concrete; the question is whether some scaling / rotation realizes it as a unit-distance graph in $\mathbb{R}^2$, possibly in a larger number field.

6. **5-chromatic on $S^2$ at radii other than the icosahedral ones.** Voronov-Neopryatnaya-Dergachev cover two specific radii; the full set of radii admitting small 5-chromatic UDGs on $S^2$ is open.

---

## 5. Wrong-approach-detector check

The Architecture 1 detector is $\mathbb{Q}^2$ (Woodall 1973: $\chi(\mathbb{Q}^2) = 2$). A combinatorial argument that gives $\chi(\mathbb{R}^2) \geq 5$ must use the topology / density of $\mathbb{R}$, otherwise it would also apply to $\mathbb{Q}^2$ and be false.

Method-by-method:

- **de Grey 2018, Heule 2018, Parts 2020 (509 vertices).** All use coordinates in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ (and rotations enlarging the field). **This field is not a subfield of $\mathbb{Q}$.** $\sqrt{3}$ and $\sqrt{11}$ are irrational. The vertex set realizes specific irrational distances; the unit-distance edges between vertices at distance exactly $1$ depend on the field being closed under the requisite rotations, which $\mathbb{Q}^2$ is not. **Detector passes**: the construction does not lift to $\mathbb{Q}^2$ because the rotated copies of the Moser spindle that force non-$4$-colorability require $\sqrt{3}$ in the coordinates.

- **Parts 2020 (human-verifiable proof, arXiv:2010.12661).** Same field requirement. **Detector passes.**

- **Voronov-Neopryatnaya-Dergachev 2021.** The 64513-vertex plane graph does not use the Moser spindle but does use a different rotation structure with irrational coordinates. From the abstract, the construction uses algorithms in the algebraic-number-field setting. **Detector likely passes**, but I have not read the full PDF and cannot verify the exact field; flagged for follow-up.

- **Parts 2022 odd-distance graph.** Uses the odd-distance relation, not unit-distance, so the $\mathbb{Q}^2$ detector does not apply in the standard form. The relevant detector here would be the odd-distance graph on $\mathbb{Q}^2$, which (per Davies et al. 2024, arXiv:2209.15598) has chromatic number $\aleph_0$ (countably infinite) for both $\mathbb{Q}^2$ and $\mathbb{R}^2$, so the structural-overshoot test is trivial. **Detector does not engage**; this is a feature of the problem, not a flaw.

- **Mundinger-Pokutta et al. 2024-2025 (six-colorings, off-diagonal).** Constructive upper-bound side; gives explicit measurable color classes. The detector for upper bounds is the $L^\infty$ plane ($\chi = 4$, Chilakamarri). Any upper-bound construction in $L^2$ that uses only norm-blind geometric structure should fail to give the $\chi(L^\infty) \leq 4$ bound. The Mundinger-Pokutta constructions explicitly use Euclidean disks / hexagons, not norm-blind cells. **Detector passes** for the upper-bound side.

**Result of detector pass**: no method in the 2018-present SAT-driven lineage overshoots to $\mathbb{Q}^2$. The lineage is structurally sound. The number field $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ is the load-bearing topological ingredient.

---

## 6. Discrepancy log

Items where my findings disagree with or refine the project's atlas:

1. **Atlas says "Polymath16 reduced the size to $\sim 510$ vertices".** The current published record is **509 vertices** (Parts 2020, arXiv:2010.12665). The 510-vertex Parts graph (Aug 2019) was the *intermediate* record. Suggest updating `docs/research_atlas/README.md` line 23 to "Polymath16 reduced the size of certified $5$-chromatic UDGs to 509 vertices (Parts 2020)".

2. **Atlas does not mention Voronov-Neopryatnaya-Dergachev (2021).** This is the first $\chi \geq 5$ UDG without a Moser spindle and the first 5-chromatic UDG on $S^2$. Structurally important; should be added to landmarks.

3. **Atlas treats SAT as the *only* certification path.** Parts 2020 (arXiv:2010.12661) gives a human-verifiable proof of $\chi(\mathbb{R}^2) \geq 5$. SAT is therefore convenient but not necessary. Worth noting in the Architecture 1 description.

4. **Atlas does not flag the odd-distance / two-distance variants.** Parts 2022 (odd-distance, 6-chromatic) and Parts 2020 (two-distance, 6-chromatic, 16 vertices) are useful proxies and live structurally adjacent to Architecture 1. The 6-chromaticity is *achievable* in these variants and provides a sanity check on what computational machinery can do; the gap to single-distance 6-chromatic is therefore structural, not computational-power-limited.

5. **Heule "529" vs "Heule 553".** Sources vary: arXiv:1805.12181 abstract reports 553; later announcements report 529 from continued CPM. Both are by Heule, in May-July 2018. The atlas should not pick a single number without noting the progression 1581 to 553 to 529 to 525 to 517 to 510 to 509.

---

## 7. What this enables / what remains open

**Enables (downstream agents)**:

- **BUILDER**: the 509-vertex Parts graph (arXiv:2010.12665) is the natural seed for sub-509 minimization experiments. The Heule clausal-proof-minimization pipeline (arXiv:1805.12181) and Parts' preserve-a-property minimization are both publicly described; an implementation in `experiments/combinatorial/` should reproduce 509 vertices as a baseline and then attempt further reduction with newer SAT solvers (kissat 3.x). The Voronov-Neopryatnaya-Dergachev graph (arXiv:2106.11824) is the natural seed for Moser-spindle-free 5-chromatic searches.

- **VERIFIER**: any candidate $\chi \geq 6$ UDG should be checked against (a) the SAT certificate (unsat proof in DRAT format), (b) the $\mathbb{Q}^2$ detector (the graph's edges must depend essentially on irrational coordinates), and (c) the $L^\infty$ detector for upper-bound proofs.

- **ADVERSARY**: the gap between single-distance and two-distance 6-chromatic graphs (one is open, the other has a 16-vertex example) is the most promising point of attack. Why does adding one extra forbidden distance collapse the difficulty from "totally open" to "16 vertices"?

- **SYNTHESIZER**: integrate the discrepancy log into `docs/research_atlas/README.md` and update LEARNINGS.md with the Moser-spindle question (see below).

**Remains open**:

- $\chi(\mathbb{R}^2) \in \{5, 6, 7\}$, no progress on narrowing since 2018.
- No 6-chromatic UDG known. The structural barrier appears to be that 5-coloring of UDGs in $\mathbb{Q}(\sqrt{3}, \sqrt{11})^2$-realizable graphs is "easy enough" that all currently constructible candidates admit a 5-coloring.
- Whether the 509-vertex bound on smallest 5-chromatic UDG is tight is open. The lower bound on 5-chromatic UDG size is roughly 17 (the Exoo-Ismailescu 4-chromatic triangle-free graph) times a constant, but no good explicit lower bound is known.
- Whether neural / ML methods can produce 5-chromatic UDGs competitive with SAT (i.e., $< 509$ vertices) is untested as of 2025. Mundinger-Pokutta-style differentiable loss reformulations have only been deployed for upper-bound coloring constructions.

**Flag for follow-up SURVEYOR sessions**:

- (a) The Polymath16 D.H.J. Polymath paper (Geombinatorics 2021): I located announcements but not the published PDF. A targeted SURVEYOR session to extract its formal statements would be valuable.
- (b) Variant problems sub-dossier: odd-distance, two-distance, and sphere problems collectively form a "Hadwiger-Nelson environment" worth its own dossier.
- (c) Number-field landscape: a precise inventory of which $\mathbb{Q}(\alpha)$ admit / refuse 5-colorings would clarify the field-theoretic obstruction in section 3, point 2.

---

## References (verified by direct fetch or quoted from secondary)

| Tag | Reference | Verified |
|-----|-----------|----------|
| de Grey 2018 | arXiv:1804.02385; Geombinatorics 28 (2018) | abstract + secondary |
| Polymath16 launch | polymathprojects.org 2018-04-10 | fetched |
| Heule 2018 | arXiv:1805.12181 | abstract |
| Exoo-Ismailescu 2018 | arXiv:1805.00157 | abstract |
| Parts 2020 minimization | arXiv:2010.12665; Geombinatorics 29/4 (2020), 137-166 | abstract |
| Parts 2020 human-verifiable | arXiv:2010.12661 | abstract |
| Polymath16 13th thread | dustingmixon.wordpress.com 2019-07-08 | fetched |
| Polymath16 16th thread | dustingmixon.wordpress.com 2020-05-11 | fetched |
| Polymath16 17th thread | dustingmixon.wordpress.com 2021-02-01 | fetched |
| Polymath16 wiki | michaelnielsen.org/polymath | fetched |
| Voronov-Neopryatnaya-Dergachev 2021 | arXiv:2106.11824; *Discrete Math.* (2022) | abstract |
| Parts 2022 odd-distance | arXiv:2206.12632; Geombinatorics 31/3 (2022) | abstract |
| Parts 2020 two-distance | arXiv:2010.12656 | abstract |
| Matolcsi-Ruzsa-Varga-Zsamboki 2023 | arXiv:2311.10069 | abstract |
| Davies et al. 2024 odd-distance | arXiv:2209.15598; GAFA 2024 | secondary |
| Mundinger-Pokutta et al. 2024 | arXiv:2404.05509; Geombinatorics Quarterly 2024 | abstract + blog |
| Mundinger et al. 2025 | arXiv:2501.18527 | abstract |
| Globus-Parshall 2019 | arXiv:1905.07829 | abstract |
| Oostema-Martins-Heule (unit-distance strips) | LPAR-23 (Heule's CMU page) | secondary |
| Soifer 2024 (chapter, "Can we reach chromatic 5 without Moser spindles?") | *The New Mathematical Coloring Book*, Springer 2024 | secondary |

Items marked "abstract" mean only the arXiv abstract was read; full-PDF verification is a follow-up task.
