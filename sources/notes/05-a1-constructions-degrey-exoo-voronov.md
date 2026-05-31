# A1 Constructions: de Grey 2018, Exoo-Ismailescu 2018, Voronov-Neopryatnaya-Dergachev 2022

Architecture 1 (combinatorial / unit-distance graph) core construction papers. These are the three
that establish or re-derive $\chi(\mathbb{R}^2) \geq 5$ via finite UDGs, plus the generalization to
spheres. Reading notes by SURVEYOR; structural focus, mechanism-of-forcing focus, with a
sustained eye on the project bottleneck: what would have to change to force $\chi \geq 6$.

Source files (extracted text):
- `sources/_extracted/deGrey-2018-Chromatic-Number-Plane-At-Least-5_arXiv-1804.02385v3.txt`
- `sources/_extracted/ExooIsmailescu-2018-Chromatic-Number-Plane-At-Least-5-New-Proof_arXiv-1805.00157.txt`
- `sources/_extracted/Voronov-Neopryatnaya-Dergachev-2022-Constructing-5-Chromatic-Unit-Distance-Graphs-Embedded-in-Plane-and-Spheres_arXiv-2106.11824.txt`

---

## Executive summary (10 lines)

1. All three proofs prove $\chi(\mathbb{R}^2) \geq 5$ by exhibiting a finite UDG with no proper 4-coloring; de Bruijn-Erdos then lifts to the plane.
2. The shared engine is a forced monochromatic equilateral triangle of edge length $\sqrt{3}$ (de Grey, Voronov) or $1/\sqrt{3}$ (Exoo-Ismailescu): a "monochromatic triple" that no 4-coloring can avoid everywhere, yet a second gadget forbids locally.
3. de Grey: 7-vertex hexagon-plus-center graph $H$ has exactly 4 essentially-distinct 4-colorings (2 with a monochromatic triple, 2 without); a 121-vertex assembly $L$ (52 copies of $H$) forces one copy of $H$ to contain a mono triple; a 1345-vertex spindle-dense graph $M$ forbids it. Union $N$ = 20425 vertices; shrunk to 1581 (SAT-confirmable).
4. The Euclidean rigidity is the $\sqrt{3}$ distance (long diagonal of a unit rhombus / second-neighbor in the hexagon) coupled with the Moser-spindle constraint that two $\sqrt{3}$-pairs cannot both be monochromatic. This is exactly what fails over $\mathbb{Q}^2$.
5. Exoo-Ismailescu: three-assertion pipeline. (a) some $\sqrt{11/3}$-pair is monochromatic (79-vtx graph), (b) a monochromatic $\sqrt{11/3}$-pair forces a monochromatic $1/\sqrt{3}$-equilateral triangle (49-vtx graph), (c) such a triangle is impossible (627-vtx graph). Coordinate ring $\mathbb{Q}(\sqrt{3},\sqrt{11},\sqrt{247})$.
6. Voronov et al.: an ALGORITHM (generalizing Heule) that builds an embedded high-$\chi$ UDG from any minimally rigid 4-vertex-critical base $L$ via a finitely generated rotation group plus a Minkowski-sum-and-clip vertex set, then a single binding rotation $\psi$. Produces a 64513-vertex planar 5-chromatic graph from base $L_{10,2}$, with NO Moser spindle inside.
7. Voronov also builds 5-chromatic UDGs on spheres ($S^2(r_1)$, 372 vertices, icosahedron-based; $S^2(r_2)$, 972 vertices, great-icosahedron-based), proving $\chi(S^2(r))$ is non-monotonic.
8. SAT/computer role: de Grey used custom DFS for the 20425 graph, SAT for the 1581 shrink; Exoo-Ismailescu use Sage enumeration + a forced-color DFS; Voronov uses CDCL SAT (Glucose, Kissat) at every step.
9. Bottleneck reality check: every attempt to push $\chi \geq 6$ has died on the cost of the "blocker" gadget growing super-linearly while the forced-triple density stays fixed. Voronov tried $H_{12,1} \circ H_{9,1} \circ H_{9,1}$ (29k-54k vertices) and Kissat could not even decide 5-colorability in 1 CPU-month.
10. The deepest structural fact (Voronov, conclusion): the embedded 5-chromatic graphs exist only at isolated curvature values, and the only known continuous-radius high-degree sphere UDGs are bipartite, so the "lots of forced triples" mechanism does not obviously scale to a 6-forcing object.

---

## Top actionable takeaways for reaching $\chi \geq 6$

These are the levers the three papers expose, ranked by how directly they bear on the missing object (a finite $\chi \geq 6$ UDG embeddable in $\mathbb{R}^2$).

1. **The two-gadget pattern is the whole game.** Every $\chi \geq 5$ proof is: gadget A forces SOME local monochromatic configuration $C$ (a $\sqrt{3}$-triple, or a $1/\sqrt{3}$-triangle) in every 4-coloring; gadget B forbids $C$ locally. For $\chi \geq 6$ you need the analog where A forces $C$ in every 5-coloring and B forbids $C$ in every 5-coloring. The first half (force a mono config in every 5-coloring) is the part nobody has built. de Grey's $L$ forces a mono triple in every 4-coloring because $H$ has only 4 essentially-distinct 4-colorings; the 5-coloring analog of $H$ has many more colorings and no clean "two have a triple, two do not" dichotomy. THIS is where to spend effort: find a small graph whose 5-colorings split cleanly into "contains forced config" vs "does not", with the no-config class killable by rotation.

2. **Spindle density is a proxy for $\sqrt{3}$-pair uniformity, not for color count.** de Grey's $M$ works because high spindle density forces $\sqrt{3}$-apart monochromatic pairs to distribute uniformly, so a high-density local triple is a contradiction. Spindles constrain 4-colorings (a spindle is 4-chromatic). For 5 colors you need a 5-chromatic rigid base playing the spindle's role. de Grey explicitly flags this: spindles give "two $\sqrt{3}$-pairs that cannot both be monochromatic." A 5-color analog needs a small 5-chromatic rigid gadget giving "k forbidden-monochromatic configs that cannot all be avoided." No such small gadget is known (the smallest 5-chromatic UDG is ~509 vertices, Parts).

3. **Voronov's algorithm is the most directly scalable lever, and it is in-repo-reproducible.** Their construction takes ANY minimally rigid 4-vertex-critical base $L$ with a finite-order generator $\phi_0$, builds $M_s$ = clipped Minkowski powers of the unit-circle generator set, then unions with one rotated copy $\psi M_s$. The exact same pipeline with a 5-chromatic rigid base $L'$ (if one is found small enough) would be the natural route to a 6-chromatic graph. The bottleneck is purely (a) finding a small 5-chromatic rigid base and (b) SAT cost of deciding 5-colorability of the resulting ~$10^4$-$10^5$ vertex union. They explicitly note (b) is the wall: deciding 5-colorability of the 64513 graph is "surprisingly difficult," and for $s > 3$ may be "practically unsolvable using pure SAT."

4. **Coordinate-ring discipline is a live wrong-approach detector.** de Grey lives in $\mathbb{Q}(\sqrt{3},\sqrt{5},\sqrt{7},\sqrt{11})$; Exoo-Ismailescu in $\mathbb{Q}(\sqrt{3},\sqrt{11},\sqrt{247})$; Voronov's spindle-based series in $\mathbb{Q}(i,\sqrt{3},\sqrt{5},\sqrt{11})$; Voronov's $L_{10,2}$ series in $\mathbb{Q}(i,\sqrt{2},\sqrt{3},\sqrt{5})$ (NO $\sqrt{11}$, hence provably no Moser spindle). The $\sqrt{3}$ is universal: it is the rigidity that makes the equilateral-triangle forcing work and the thing that vanishes over $\mathbb{Q}^2$. Any candidate $\chi \geq 6$ construction that does not use $\sqrt{3}$-type irrationalities to build rigid triangles is suspect.

5. **Connect to the repo reverse-engineering scripts.** `experiments/combinatorial/e1l_reverse_engineer_degrey1585.py` parses `sources/degrey_1585_vertices.sage` and looks for rotational symmetries about origin / vertex pivots / centroid; `e1i_reverse_engineer_polymath510.py` does the same for Polymath/Heule 510. The lesson those scripts encode (per their docstrings): SAT-minimization DESTROYS the rotational symmetry that made the original construction legible (Polymath 510 has lost its symmetry; de Grey 1585 should retain some). For $\chi \geq 6$ work, build from the SYMMETRIC originals (de Grey's $L$/$M$ recipe, Voronov's rotation-group recipe), not from the minimized SAT outputs, because the symmetric versions expose the forcing mechanism. The repo should add an `e1?` script that runs Voronov's $M_s$-and-$\psi$ pipeline with a parameterizable base $L$, so a 5-chromatic base can be dropped in when found.

6. **Non-monotonicity of $\chi(S^2(r))$ is a generator of new gadgets.** Voronov's sphere results (Corollary 1) show curvature is a free parameter that changes which 4-chromatic rigid graphs embed. The icosahedron graph $H_{12,1}$ has a UNIQUE 4-coloring up to symmetry (Ballard) and $\alpha = 3$ with every independent triple an equilateral triangle. That uniqueness is a far stronger forcing than de Grey's $H$ (which has 4 colorings). A spherical or hyperbolic base with a unique or near-unique 5-coloring would be the cleanest possible gadget A. This is an underexplored direction with no obvious obstruction yet recorded.

---

## Cross-comparison

### Where all three agree on what forces 5

The common skeleton is identical and worth stating sharply:

> In any proper 4-coloring of the plane, there is a forced **monochromatic equilateral triangle** at a specific Euclidean scale, but a finite gadget makes that triangle locally impossible.

- de Grey and Voronov use the **$\sqrt{3}$-triple**: three vertices of a regular hexagon of side 1 that are pairwise $\sqrt{3}$ apart and form an equilateral triangle of side $\sqrt{3}$. The hexagon-plus-center graph $H$ (de Grey) / the icosahedron triple (Voronov) is the carrier.
- Exoo-Ismailescu use the **$1/\sqrt{3}$-triangle**: an equilateral triangle of side $1/\sqrt{3}$, reached via a $\sqrt{11/3}$ monochromatic pair.

In all cases the rigidity that does the work is that $\sqrt{3}$ is the distance between two vertices of a unit rhombus along the long diagonal (equivalently the Moser spindle is built from two unit rhombi sharing the $\sqrt{3}$ apex spread, and $\sqrt{11}$ appears as the cross-distance in the spindle). The number-field signature $\sqrt{3}$ everywhere, $\sqrt{11}$ wherever a Moser spindle is present is the structural fingerprint.

The forcing logic is always a **counting/pigeonhole on a small graph with few 4-colorings**:
- de Grey: $H$ has exactly 4 essentially-distinct 4-colorings, cleanly split 2-2 by "has a monochromatic triple."
- Exoo-Ismailescu: $G_{49}$ has exactly 18694 proper 4-colorings up to permutation, only 44 with no monochromatic $1/\sqrt{3}$-triangle, and in ALL 44 the marked pair $P,Q$ gets different colors.
- Voronov (sphere): $H_{12,1}$ has a UNIQUE 4-coloring up to symmetry. The plane construction inherits de Grey's $H$-logic implicitly through the spindle/base subgraph.

### Where they differ

| Aspect | de Grey 2018 | Exoo-Ismailescu 2018 | Voronov et al. 2022 |
|---|---|---|---|
| Forced config | mono $\sqrt{3}$-triple in hexagon $H$ | mono $1/\sqrt{3}$-equilateral triangle | inherits de Grey-style triple via base |
| Pipeline length | 2 gadgets ($L$ forces, $M$ forbids) | 3 gadgets ($G_{79}$, $G_{49}$, $G_{627}$) | 1 algorithm, parameterized by base $L$ |
| Base 4-chromatic element | Moser spindle (dense) | Moser spindle + Golomb-ish triangles | minimally rigid 4-vertex-critical graph (e.g. $L_{10,2}$, $L_{9,1}$); deliberately NOT the spindle for the plane $L_{10,2}$ series |
| Smallest graph | 1581 vertices (shrunk from 20425) | 5782+ vertices (3-step, less economical; not minimized) | 64513 (plane); 372 / 972 (spheres) |
| Coordinate ring | $\mathbb{Q}(\sqrt{3},\sqrt{5},\sqrt{7},\sqrt{11})$ | $\mathbb{Q}(\sqrt{3},\sqrt{11},\sqrt{247})$ | $\mathbb{Q}(i,\sqrt{2},\sqrt{3},\sqrt{5})$ for $L_{10,2}$ series (no $\sqrt{11}$); $\mathbb{Q}(i,\sqrt{3},\sqrt{5},\sqrt{11})$ for spindle series |
| Computer role | custom DFS (forced-propagation), then SAT for shrunk graph | Sage enumeration + circumcenter-adding DFS | CDCL SAT (Glucose/Kissat) at every decision |
| New contribution | first proof; the $H$/$L$/$M$ economy | independent proof; explicit number field; the assertion-chain | algorithmic generation; spheres; spindle-free plane graphs |

Key methodological divergence: de Grey and Exoo-Ismailescu hand-craft the assembling rotations (de Grey's $2\arcsin(1/4)$, $2\arcsin(1/8)$; Exoo's $\arccos(119/128)$). Voronov AUTOMATES the search over the binding rotation $\psi$ and over the base graph, turning the construction into a parameterized algorithm.

### What would have to change to force $\chi \geq 6$ (reasoned assessment)

The papers themselves are explicit that pushing to 6 has not worked, and they hint at why. Synthesizing:

**(A) The forced-config gadget must constrain 5-colorings, not 4-colorings.** Every gadget A above is built on a 4-chromatic rigid graph whose 4-colorings are few and structured. The Moser spindle (4-chromatic, 7 vertices) is the smallest such; the analog for 6 is a small 5-chromatic rigid graph. The smallest known 5-chromatic UDG is ~509 vertices (Parts), which is two orders of magnitude larger than the spindle. So gadget A for $\chi \geq 6$ would plausibly be enormous (Voronov's union with a ~509-vertex base under their Minkowski-power scheme would dwarf 64513). No small 5-chromatic rigid base is known, and there may be a real barrier: 5-chromatic UDGs seem to require "irreducible largeness" (the SAT-minimization removes symmetry, suggesting the 5-chromaticity is not concentrated in a small rigid core).

**(B) The blocker gadget grows faster than the forcing density.** de Grey's $M$ (1345 vertices) blocks ONE triple location; $N$ needs 52 of them. For 5 colors, the blocker analog must rule out a forced config under all 5-colorings, which is combinatorially much harder (more colorings to kill). Exoo-Ismailescu's $G_{627}$ already needed 576 added vertices to kill 13357 colorings of $G_{51}$; the 5-color analog would have vastly more colorings to eliminate. The vertex count likely explodes beyond SAT reach.

**(C) SAT decidability is the operational wall, and it is sharp.** Voronov state it plainly (Conclusion): deciding 5-colorability of their 64513-vertex graph is "surprisingly difficult," and for the iterated sphere product $H_{12,1} \circ H_{9,1} \circ H_{9,1}$ (29112-54072 vertices) Kissat could not decide 5-colorability in 1 CPU-month. de Grey's economy (custom DFS exploiting forced propagation) was essential at 20425 vertices; the analog of "fixing 20 colors forces almost all the rest" does not obviously hold at the 5-coloring level because the per-vertex branching is higher (5 colors, not 4).

**(D) Continuous-curvature obstruction (Voronov, Conclusion).** The only known unit-distance graphs on spheres of continuously varying radius with arbitrarily high mean degree are bipartite (Erdos-Hickerson-Pach; Swanepoel-Valtr). High mean degree is what you would want to force many constraints, but bipartiteness kills any high-$\chi$ hope. So the "throw more edges at it" route to a 6-forcing object is structurally blocked on the sphere, and the analogous worry applies to the plane: edge density alone does not raise $\chi$ past what rigidity forces.

**(E) Field-theoretic ceiling.** Madore's result (cited by Exoo-Ismailescu) shows that whether a 5-chromatic UDG exists over $\mathbb{Q}(\sqrt{3},\sqrt{11})$ alone is the best-possible field question. The need for extra irrationalities ($\sqrt{5},\sqrt{7},\sqrt{247}$) to build the assembling rotations suggests that 5-chromaticity already strains the smallest natural field; 6-chromaticity may require still-larger fields, and the rotations needed to bind copies become harder to realize with small-degree algebraic numbers.

**Bottom line for the repo:** the missing object is a finite $\chi \geq 6$ UDG. The three papers collectively say: you need a gadget that forces a monochromatic config in every 5-coloring. The cleanest known forcing mechanisms (de Grey's $H$ with 4 colorings, Voronov's icosahedron with 1 coloring) are 4-coloring phenomena. The single most promising lever is Voronov's parameterized algorithm fed a 5-chromatic rigid base, gated entirely on (i) finding a SMALL 5-chromatic rigid base and (ii) SAT being able to decide 5-colorability of the ~$10^5$-vertex output. Both are open and both look hard. There is no proof of impossibility, only a consistent pattern of cost explosion.

### Connection to repo reverse-engineering scripts

- `e1l_reverse_engineer_degrey1585.py`: parses the 1581-vertex SAT-confirmed graph $G$ (de Grey's step 5 shrink), hunts rotational symmetries about origin / vertices / centroid / $(1,0)$ / midpoints. Relevant because de Grey's $G$ is built by rotating $Y$ (itself a 60-degree-symmetric union $S_a \cup S_b$) by $\pm \arcsin(1/8)$ about $(-2,0)$. The script should recover a residual reflection/rotation structure even after the deletion of $(\pm 1/3, 0)$. This is the symmetric original, so symmetry is expected (unlike Polymath 510).
- `e1i_reverse_engineer_polymath510.py`: per its docstring, established that the Polymath/Heule lineage in $\mathbb{Q}(\sqrt{3},\sqrt{11})$ LOST its rotational symmetry to SAT-minimization. This is the cautionary tale: minimized graphs are illegible. For building toward 6, work from Voronov's rotation-group recipe (Section 5 of their paper), which keeps the symmetry explicit via the generators $\Phi(L) = \{\phi_0, \dots, \phi_p\}$ with $\phi_0^k = 1$.
- Suggested new experiment: implement Voronov's $M_1 = \{0\} \cup \{\phi_0^{\alpha_0}\cdots\phi_p^{\alpha_p}\}$, $M_s = \mathrm{clip}(M_{s-1} + M_1; r_s)$, $W = M_s \cup \psi M_s$ pipeline as a function of base $L$, reproduce the 64513 graph from $L_{10,2}$ with $\phi_0 = (\sqrt6+\sqrt2)/4 + (\sqrt6-\sqrt2)/4 \cdot i$ ($\phi_0^{24}=1$), $\phi_1 = \sqrt6/3 + \sqrt3/3 \cdot i$, $t=1$, then make $L$ swappable for a future 5-chromatic base.

---

## Per-paper detailed notes

### Paper 1: de Grey, "The chromatic number of the plane is at least 5" (arXiv:1804.02385v3, 2018)

**Result.** A family of finite non-4-colorable UDGs in the plane; smallest found = 1581 vertices, hence $\chi(\mathbb{R}^2) \geq 5$.

**Building block $H$ (Section 2).** The 7-vertex, 12-edge UDG = center plus 6 vertices of a regular hexagon of side 1. (Center-to-vertex = 1; adjacent rim vertices = 1; that is 6 + 6 = 12 edges. The three "long diagonals" of the rim are pairs at distance $\sqrt{3}$, NOT edges.) Key fact: $H$ has exactly FOUR essentially-distinct 4-colorings (up to rotation, reflection, color permutation). Two contain a monochromatic triple (three vertices same color, necessarily an equilateral triangle of side $\sqrt{3}$ formed by alternate rim vertices), two do not. This 2-2 dichotomy is the seed of everything.

**The forcing assembly $L$ (Section 3).**
- $J$: 31 vertices, 13 copies of $H$ (one central, six at distance 1 from center, six at distance $\sqrt{3}$). Lemma: the 4-colorings of $J$ in which NO copy of $H$ has a monochromatic triple number exactly six (up to symmetry plus free "black" vertices), and ALL of them have a special property about the "linking vertices" (the six vertices at distance 2 from center). The linking-vertex color pattern is one of three types: (a) all same as center, (b) four consecutive same as center + two a second color, (c) two opposite same as center + four a second color. A "linking diagonal" is a pair of linking vertices in opposite directions.
- $K$: 61 vertices = $J \cup (J$ rotated by $2\arcsin(1/4))$. The rotation puts corresponding linking vertices at distance 1. Lemma: in any 4-coloring of $K$ with no copy of $H$ having a mono triple, BOTH copies of $J$ must use linking-pattern (c), in which every linking diagonal is monochromatic. So all six linking diagonals are monochromatic.
- $L$: 121 vertices = $K \cup (K$ rotated about $A$ by $2\arcsin(1/8))$. The rotation puts $B' $ at distance 1 from $B$. Since $B$ and $B'$ must differ in color, one linking diagonal is non-monochromatic, contradiction with the $K$-lemma. Therefore: **in no 4-coloring of $L$ do all 52 copies of $H$ avoid a monochromatic triple.** $L$ = the forcing gadget A.

**The blocker $M$ (Section 4).** A graph containing a copy of $H$ such that NO 4-coloring of $M$ has that $H$ containing a monochromatic triple. Motivation: a Moser spindle has two $\sqrt{3}$-apart pairs that cannot both be monochromatic, so a spindle-dense graph forces $\sqrt{3}$-monochromatic pairs to spread uniformly; a local mono triple (high local $\sqrt{3}$-density) then contradicts uniformity.
- $T$: 9 vertices = spindle + 2 vertices $P,Q$ forming an equilateral triangle with the spindle tip $X$ and lying on the extension of the base $YZ$.
- $U$: 15 vertices = three spindles with triangular symmetry.
- de Grey found 97-vertex graphs with 78 spindles but they did not enforce enough uniformity even at >1000 vertices.
- Fix: enrich the edge-direction classes. Edges of $V$ (the 30-degree-max graph) lie at angles $i\arcsin(\sqrt{3}/2) + j\arcsin(1/\sqrt{12})$, $i \in 0..5$, $j \in -2..2$. Max vertex degree rises 18 to 30.
- $W$: 301 vertices = all points at distance $\leq \sqrt{3}$ from origin that are sums of two edges of $V$.
- $M$: 1345 vertices = $W$ plus six translates (origin to each vertex of $H$). The custom program found no 4-coloring with central $H$ having a mono triple. So $M$ = blocker gadget B.

**The non-4-colorable graph $N$ (Section 4.2).** Union of 52 copies of $M$, placed so each $H$ in $L$ coincides with a central $H$ of an $M$. After merging coincident vertices: 20425 vertices. Logic: $L$ forces some copy of $H$ to have a mono triple; the $M$ glued there forbids it. Contradiction; $N$ is not 4-colorable.

**Computer role (Section 4.3).** Custom depth-first search in Mathematica 11, exploiting that fixing ~20 colors at branch points forces almost all others via constraint propagation (order vertices by spindle-count, then degree, then unit-triangle count). Ran in minutes on a MacBook Air. The crucial efficiency: only asking 4-colorability (a decision), not chromatic number, and high edge/spindle density makes propagation aggressive.

**Shrinking to 1581 (Section 5).** Delete vertices of subgraphs whose removal preserves the needed property; add single vertices enabling multiple deletions. Record: 1581-vertex graph $G$, built from an explicit 38-point set $S$ (coordinates given in $\mathbb{Q}(\sqrt{3},\sqrt{11},\sqrt{33})$, with $\sqrt{33}=\sqrt{3}\sqrt{11}$), via:
1. $S_a$ = $S$ rotated by multiples of 60 degrees and $y$-negated = 397 vertices.
2. $S_b$ = $S_a$ rotated by $2\arcsin(1/4)$.
3. $Y$ = $S_a \cup S_b$ minus $(\pm 1/3, 0)$.
4. $Y_a, Y_b$ = $Y$ rotated about $(-2,0)$ by $\pi/2 \pm \arcsin(1/8)$.
5. $G = Y_a \cup Y_b$.
$G$ is within reach of standard SAT solvers (independently confirmed $\chi = 5$).

**Euclidean rigidity / wrong-approach check.** The $\sqrt{3}$ distance (hexagon long diagonal = spindle apex spread) is the load-bearing irrationality; $\sqrt{11}$ is the spindle cross-distance. Over $\mathbb{Q}^2$ there are no unit equilateral triangles (no $\sqrt{3}$), the hexagon $H$ does not embed, and the whole forcing collapses; consistent with $\chi(\mathbb{Q}^2)=2$. The assembling rotations $2\arcsin(1/4)$, $2\arcsin(1/8)$ are exactly the irrational rotations that $\mathbb{Q}^2$ cannot support. PASSES the detector (uses Euclidean rigidity that fails on $\mathbb{Q}^2$ and on the $L^\infty$ plane, where regular hexagons of unit side do not have $\sqrt{3}$ diagonals in the same way).

### Paper 2: Exoo-Ismailescu, "A new proof" (arXiv:1805.00157, 2018)

**Result.** Independent proof that any proper 4-coloring of the plane fails; $\chi(\mathbb{R}^2) \geq 5$. Coordinate notation $[a,b,c,d] := (a\sqrt3/36 + b\sqrt{11}/36,\ c/36 + d\sqrt3\sqrt{11}/36)$, integers $a,b,c,d$; almost all vertices in $\mathbb{Q}(\sqrt3,\sqrt{11})^2$.

**Three-assertion architecture (Section 1).**
- (a) Any proper 4-coloring has two points at distance $\sqrt{11/3}$ identically colored.
- (b) A monochromatic $\sqrt{11/3}$-pair forces a monochromatic equilateral triangle of side $1/\sqrt{3}$.
- (c) A monochromatic $1/\sqrt3$-equilateral triangle is impossible under a proper 4-coloring.
Chain: (a) + (b) force a mono $1/\sqrt3$-triangle; (c) forbids it; contradiction.

**Assertion (a), $G_{79}$ (Section 2).** Start with $G_{40}$: 40 points in $\mathbb{Q}(\sqrt3,\sqrt{11})^2$, 82 unit edges, 59 pairs at distance $\sqrt{11/3}$. Crucial property: in any 4-coloring avoiding monochromatic $\sqrt{11/3}$-pairs, vertices $[0,0,0,0]$ and $[0,0,96,0]$ (distance $8/3$) get the same color (Sage-verifiable). Rotate $G_{40}$ about $[0,0,0,0]$ by $\theta = \arccos(119/128) \approx 21.61^\circ$ so the image of $[0,0,96,0]$ lands at distance 1 from the original. $G_{79}$ = union; 165 unit edges, 118 edges of length $\sqrt{11/3}$. Any 4-coloring forces some $\sqrt{11/3}$-edge monochromatic. Because $\sin\theta = 3\sqrt{247}/128$, the points sit in $\mathbb{Q}(\sqrt3,\sqrt{11},\sqrt{247})^2$. (The $\sqrt{247} = \sqrt{13 \cdot 19}$ is the price of the binding rotation.)

**Assertion (b), $G_{49}$ (Section 3).** 49 points in $\mathbb{Q}(\sqrt3,\sqrt{11})^2$, 180 unit edges, containing fixed $P=[0,0,0,0]$, $Q=[0,0,0,12]$ at distance $\sqrt{11/3}$, and 18 equilateral triangles of side $1/\sqrt3$. Enumeration: exactly 18694 proper 4-colorings up to permutation, only 44 with no monochromatic $1/\sqrt3$-triangle, and in all 44 the pair $P,Q$ is bichromatic. So if $P,Q$ are monochromatic, some $1/\sqrt3$-triangle is monochromatic.

**Assertion (c), $G_{627}$ (Section 4).** Start with $G_{51}$: 51 vertices, automorphism group of order 6 (a $2\pi/3$ rotation + a $y$-axis reflection), first three vertices $A,B,C$ forming a $1/\sqrt3$-equilateral triangle. There are 13357 proper 4-colorings of $G_{51}$ with $\chi(A)=\chi(B)=\chi(C)$. Method: for each, repeatedly add the circumcenter of any "rainbow" triple (3 differently-colored vertices) whose circumradius is exactly 1, forcing colors until a unit-distance monochromatic conflict appears. The hardest coloring needed 55 added vertices; a single set of 576 added vertices kills all 13357. Result $G_{627}$ = 51 + 576 = 627 vertices, 2982 unit edges, same order-6 symmetry, not 4-colorable when $A,B,C$ share a color. Verified by a simple forced-color DFS (Algorithm 1): once vertices 1-3 are set and processed in file order, vertices 52-627 are all FORCED. (Appendix gives 109 generating vertices; full set via $2\pi/3$ rotations and reflections across $y=0$ and $\sqrt3 x \pm y = 0$.)

**Assembling a 5-chromatic graph (Section 5).** Start with $G_{79}$; on each of its 118 $\sqrt{11/3}$-edges place a $G_{49}$ ($118 \cdot 49 = 5782$ vertices, with multiplicity); on each forced $1/\sqrt3$-triangle place a $G_{627}$. Order much larger than de Grey's 20425. They note de Grey is more economical (2 steps vs 3). Their graph embeds in $\mathbb{Q}(\sqrt3,\sqrt{11},\sqrt{247})^2$. They cite Heule's 826-vertex graph in $\mathbb{Q}(\sqrt3,\sqrt{11},\sqrt5)^2$ and ask the open field question: is there a 5-chromatic UDG over $\mathbb{Q}(\sqrt3,\sqrt{11})^2$ alone (best possible per Madore)?

**Open questions they raise (Section 5).** Minimum order of a 5-chromatic UDG; smallest subfield requiring 5 colors; **whether these ideas can build a 6-requiring UDG**; whether $\chi_f(\mathbb{R}^2) > 4$ (they note their own 73-vertex graph with $\chi_f = 383/102 \approx 3.755$); higher-dimensional analogs.

**Euclidean rigidity / wrong-approach check.** The triple $\sqrt{11/3}$-pair, $1/\sqrt3$-triangle, unit-distance is pure Euclidean-norm rigidity; $\sqrt3$ and $\sqrt{11}$ are the spindle/rhombus irrationalities, $\sqrt{247}$ the rotation cost. None of these distances are simultaneously realizable on $\mathbb{Q}^2$ (no $1/\sqrt3$-equilateral triangle exists there) and the construction does not survive the $L^\infty$ plane. PASSES the detector.

### Paper 3: Voronov-Neopryatnaya-Dergachev (arXiv:2106.11824v4, 2022, Discrete Mathematics)

**Results.** (i) An algorithm generating embedded high-$\chi$ UDGs from a 4-chromatic base. (ii) A series of 64513-vertex 5-chromatic PLANAR UDGs that do NOT use the Moser spindle. (iii) 5-chromatic UDGs on two spheres: 372 vertices on the icosahedron circumsphere $S^2(r_1)$, $r_1 = \cos(\pi/10) \approx 0.951$; 972 vertices on the great-icosahedron circumsphere $S^2(r_2)$, $r_2 = \cos(3\pi/10) \approx 0.588$. (iv) Corollary: $\chi(S^2(r))$ is NON-MONOTONIC (since $\chi(S^2(\sqrt2/2)) = 4$).

**Heuristic / base selection (Section 2).** Use minimally rigid (Graver-Servatius), 4-vertex-critical UDGs with few vertices as the base. Counts $l'_{4,k}$ of such graphs: $k=7$: 1 (the Moser spindle $L_7$), $k=8$: 1, $k=9$: 6, $k=10$: 60, $k=11$: 241 (OEIS A328061). Chosen bases: $L_{9,1}$ (subgraph of Golomb graph; icosahedron sphere), $L_{10,1}$ (great-icosahedron sphere), $L_{10,2}$ (the new planar construction). The 4-chromatic 17-vertex graph $L_{17}$ from Exoo-Ismailescu is also noted as rigid.

**Distance product (Section 3).** For $G_1, G_2 \subset S^2(r)$, $P(u_1,v_1;u_2,v_2) \subset O(3)$ = the 4 isometries taking edge $\{u_2,v_2\}$ to $\{u_1,v_1\}$. $F(G_1,G_2)$ = union over all edge pairs. $G_1 \circ G_2 = \mathrm{udg}(\bigcup_{f \in F} f(V_2))$. Degree-pruning: to seek $\chi = k$, iteratively discard vertices of degree $< k-1$.

**Sphere construction (Section 4).**
- $H_{12,1}$ = icosahedron UDG (unit edges), on $S^2(r_1)$, $r_1 = \cos(\pi/10) = \sqrt{5+\sqrt5}/(2\sqrt2)$. Proposition 1: $\alpha(H_{12,1}) = 3$, $\chi(H_{12,1}) = 4$, and (Ballard) the proper 4-coloring is UNIQUE up to icosahedral symmetry and color permutation. Every independent triple is an equilateral triangle of side $\tau = (\sqrt5+1)/2$; four such triangles form a regular tetrahedron. Opposite points get different colors.
- Proposition 2: $L_{9,1}$ embeds in $S^2(r_1)$ as a UDG (coords via minimal polynomials, Table 3; an extra unit distance appears beyond the $L_{9,1}$ edges).
- Proposition 3: $\chi(H_{12,1} \circ H_{9,1}) = 5$. Product = 732 vertices, 3390 edges; prune degree $\leq 7$ to get $G_{372}$ (372 vertices, 1710 edges; icosahedron vertices degree 35, plus 120 of degree 9 and 240 of degree 8; 4 symmetry classes). SAT (Minisat / IGraph-M) decides no-4-coloring in <1 sec; minimal-vertex search tree ~$2\times10^5$ nodes. $G_{372}$ is vertex-deletion-robust (stays 5-chromatic deleting any single vertex) but drops to 4 if a whole symmetry class is deleted.
- Proposition 4: $H_{12,2}$ = great icosahedron, $L_{10,1}$ embedded on $S^2(r_2)$, $r_2 = \cos(3\pi/10) = \sqrt{5-\sqrt5}/(2\sqrt2)$. $\chi(H_{12,2} \circ H_{10,1}) = 5$, product 3132 vertices / 10230 edges, pruned to $G_{972}$ (972 vertices, 4110 edges, 8 symmetry classes; coords as degree-8 minimal polynomials, Table 8). SAT decides no-4-coloring in <5 sec.
- Theorem 1: $\chi(S^2(r_1)) \geq 5$, $\chi(S^2(r_2)) \geq 5$. Corollary 1: $\chi(S^2(r))$ non-monotonic.

**Plane construction algorithm (Section 5).** Work in $\mathbb{C}$. For a rigid 4-chromatic base $L$ embedded with an edge from 0 to 1:
- $D(L) = \{u - v : (u,v) \in E(L)\}$, the edge-vector set.
- $g(L) = \langle D(L) \rangle$, the finitely generated group of products of edge vectors and inverses.
- Minimal generators $\Phi(L) = \{\phi_0,\dots,\phi_p\}$ with $\phi_0$ of finite order ($\phi_0^k = 1$); restrict to $L$ admitting such $\phi_0$.
- $M_1(L;t) = \{0\} \cup \{\phi_0^{\alpha_0}\cdots\phi_p^{\alpha_p}\}$ with $0 \leq \alpha_0 \leq k-1$, $-t \leq \alpha_i \leq t$. So $M_1$ has $k$-fold symmetry and lies on the unit circle plus origin.
- $\mathrm{clip}(M;r) = \{z \in M : |z| \leq r\}$; $M_s = \mathrm{clip}(M_{s-1} + M_1; r_s)$ (Minkowski sum then clip). Clipping radii $r_2,\dots,r_s$ minimize low-degree vertices.
- Final: $W = M_s \cup \psi M_s$, where $|\psi| = 1$ is the binding rotation chosen so new edges appear between $M_s \setminus \{0\}$ and $\psi M_s \setminus \{0\}$. Try finitely many $\psi$ (ordered by new-edge count).
- Remark 1: minimal $s$ to contain $L$ is at least the graph radius $r(L)$; prefer small-radius bases ($r(L_7) = r(L_{10,2}) = 2$).
- Remark 2: adding a generator translating one unit-segment endpoint to the other lets you skip Minkowski sums and use a discrete-isometry-group orbit instead (works on sphere/hyperbolic plane too).

**New plane examples (Section 6).**
- Series 1, $L = L_7$ (Moser spindle): $\phi_0 = 1/2 + (\sqrt3/2)i$ ($\phi_0^6 = 1$), $\phi_1 = \sqrt{33}/6 + (\sqrt3/6)i$, $t=2$. $M_1$ = 31 points; $M_3$ = 1939 points. Reproduces Heule's graph (his $\psi^* = 7/8 + (\sqrt{15}/8)i$) plus 4 more 5-chromatic cases (Table 5). All embed in $\mathbb{Q}(i,\sqrt3,\sqrt5,\sqrt{11})$. First 5-chromatic appears 6th in the enumeration, found in <1 min. Final union ~3877 vertices, 26748 common edges.
- Series 2, $L = L_{10,2}$: $\phi_0 = (\sqrt6+\sqrt2)/4 + ((\sqrt6-\sqrt2)/4)i$ ($\phi_0^{24} = 1$), $\phi_1 = \sqrt6/3 + (\sqrt3/3)i$, $t=1$. $M_1$ = 73 points; $M_3$ = 32257 points. Union $\mathrm{udg}(M_3 \cup \psi M_3)$ = 64513 vertices, 542352 common edges; 2731 $\psi$-cases tried, 14 yielded 5-chromatic graphs (Table 6).
- Proposition 5: $\chi(\mathbb{Q}(i,\sqrt2,\sqrt3,\sqrt5)) \geq 5$ (case 10 has $\psi = \phi_0^{-1}(7/8 + (\sqrt{15}/8)i)$, embeds in that field).
- Proposition 6: NONE of the 14 graphs $G_{64513,k}$ contain $L_7$ (Moser spindle), because their field lacks $\sqrt{11}$. Proof: $M_3$ contains at most a 4-vertex diamond $D_4 = K_4 \setminus e$ of any spindle, so a spindle would need its two diamonds split across $M_3$ and $\psi M_3$ sharing one vertex; the values of $\psi$ in Table 6 do not match the required $\phi_0^q \phi_1^p (5/6 \pm (\sqrt{11}/6)i)$. So these are genuinely spindle-free 5-chromatic plane UDGs.

**SAT performance (Section 7).** CDCL solvers (Minisat, Glucose 4, Glucose-syrup, MapleLCMDv3, plingeling, painless-mcomsps, Kissat). Standard CNF coloring encoding (clause that each vertex gets some color; clause forbidding equal colors on adjacent vertices), with symmetry-breaking by fixing colors on a max clique. UNSAT for the 3877-vertex graphs is trivial (~3-7 sec); the hard problems are SAT/UNSAT on the 64513-vertex graphs (Glucose 4 best single-threaded; Glucose-syrup best multithreaded). Table 7 gives timings.

**Conclusion / barriers (Section 8).** The constructions exist only at isolated curvature values. Iterated products like $H_{12,1} \circ H_{9,1} \circ H_{9,1}$ (29112-54072 vertices) are computationally intractable: fixing a 5-coloring of $H_{12,1}$, Kissat cannot decide 5-colorability in 1 CPU-month. For the plane, 5-coloring the 64513 graph is "surprisingly difficult" but trivial if you fix the origin to color 5 and 4-color the rest. For $s > 3$, pure-SAT 5-colorability may be "practically unsolvable." The high-mean-degree continuously-varying-radius sphere UDGs are all bipartite, so they cannot seed a continuously-embeddable high-$\chi$ graph; only finite families at fixed curvature are reachable.

**Euclidean / spherical rigidity / wrong-approach check.** Plane series 2 deliberately AVOIDS $\sqrt{11}$ (no spindle) yet still achieves 5; the rigidity instead comes from $L_{10,2}$'s minimally rigid 4-vertex-critical structure realized in $\mathbb{Q}(i,\sqrt2,\sqrt3,\sqrt5)$. The $\sqrt3$ persists (in $\phi_1 = \sqrt6/3 + (\sqrt3/3)i$ and the generators). This is a useful refinement of the detector: the load-bearing rigidity is "minimally rigid 4-vertex-critical base + finite-order rotation generator," not specifically the spindle. The sphere constructions use icosahedral rigidity (the $\tau$ golden-ratio triangles), which has no $\mathbb{Q}^2$ analog. PASSES the detector. Note the project's $L^\infty$ control is about the plane; the sphere results are a legitimate generalization outside the three standard controls.

---

## What this enables / what remains open

**Enables (for BUILDER / ADVERSARY / SYNTHESIZER):**
- A precise template for the two-gadget forcing pattern (force a mono config in every $k$-coloring; forbid it locally) that any $\chi \geq 6$ attempt must instantiate at $k=5$.
- A reproducible, parameterized generation algorithm (Voronov Section 5) ready to be coded in `experiments/combinatorial/` with the base graph $L$ as a swappable input. Concrete parameters for reproducing the 3877 (spindle) and 64513 ($L_{10,2}$) graphs are recorded above.
- A clear field-theoretic fingerprint to validate or reject candidate constructions: $\sqrt3$ universal, $\sqrt{11}$ iff Moser spindle present, larger fields ($\sqrt5,\sqrt7,\sqrt{247}$) for binding rotations.
- Sphere/curvature as an additional free parameter (non-monotonic $\chi(S^2(r))$), with the icosahedron's UNIQUE 4-coloring as the strongest known forcing gadget, a candidate seed for stronger forcing.

**Remains open (the bottleneck, restated):**
- No small 5-chromatic rigid base is known to play the spindle's role; the smallest 5-chromatic UDG is ~509 vertices and SAT-minimization has stripped its symmetry (per `e1i_reverse_engineer_polymath510.py`).
- The blocker gadget for 5-colorings would have to eliminate far more colorings than the 4-coloring blockers (de Grey's $M$, Exoo's $G_{627}$), and likely explodes past SAT-decidable size.
- Voronov's own iterated products (29k-54k vertices) are already beyond Kissat at 1 CPU-month for the 5-colorability decision; this is the operational wall.
- The continuous-curvature high-degree sphere UDGs are bipartite, blocking the "more edges" route.
- No impossibility proof exists; the pattern is consistent cost explosion, not a theorem.

**Suggested next repo action:** add an experiment implementing Voronov's $M_s$/$\psi$ pipeline parameterized by base $L$, reproduce 64513 from $L_{10,2}$, then enumerate minimally rigid 5-vertex-critical (or smallest known 5-chromatic) bases as drop-in candidates, gated on a fast 5-colorability decision procedure. Cross-reference `e1l_reverse_engineer_degrey1585.py` to keep working from symmetric originals, not minimized SAT outputs.
