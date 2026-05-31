# Soifer, "The Mathematical Coloring Book" (2009) - Research Notes

Source: `sources/_extracted/Soifer-2009-Mathematical-Coloring-Book.txt` (PDF at `sources/books/Soifer-2009-Mathematical-Coloring-Book.pdf`). Full sequential read plus targeted Grep. Page numbers are the book's internal page numbers; line numbers refer to the extracted text where load-bearing.

## Executive summary (what the book gives each architecture, and the bottleneck)

1. This is the single most HN-central book in the corpus: it is the definitive history and exposition of the chromatic number of the plane (CNP), $4 \le \chi(\mathbb{R}^2) \le 7$ as of 2009 (de Grey's $\ge 5$ came in 2018, after the book).
2. A1 (combinatorial/UDG): gives the full landmark inventory (Moser spindle, Golomb graph), the de Bruijn-Erdos finite reduction that licenses the whole SAT program, and Part III + Ch 43-45, the O'Donnell embedding machinery for turning abstract 4-chromatic graphs into unit-distance graphs. This is exactly the bottleneck tooling.
3. A2 (measurable/spectral): Ch 9 gives Falconer's $\chi_m(\mathbb{R}^2) \ge 5$ with a full hand-written-for-the-book proof; the autocorrelation/Fourier route is not in this book (it is Bukh / de Grey-era), but the measure-theoretic density machinery here is the conceptual ancestor.
4. A3 (fractional/Lovasz theta): essentially absent. No $\chi_f$ or theta-function treatment. The book predates the spectral-bound literature being central. Closest content is the polychromatic number $\chi_p$ (Ch 4, 6) and dimension/Euclidean dimension (Ch 13).
5. A4 (set-theoretic/axiomatic): Ch 46-48 are the primary source for the Shelah-Soifer phenomenon, including the explicit unit-distance Shelah-Soifer graph (Payne), and the Conditional CNP Theorem ($\chi_{ZFC}=4$ vs $\chi_{ZFS^+}\ge 5$). This is the canonical A4 reference.
6. The bottleneck (a $\chi \ge 6$ UDG that embeds in $\mathbb{R}^2$): the book makes the structure of the obstruction painfully explicit. We can build 5-chromatic ABSTRACT graphs trivially (attach spindles/Grotzsch to foundation sets), but they are too rigid to embed. O'Donnell's machinery embeds only 4-chromatic graphs.
7. Detector relevance: the book itself supplies the Woodall $\chi(\mathbb{Q}^2)=2$ detector (Ch 11) and uses it as a structural control. Almost all CNP lower-bound arguments here rely on Euclidean rigidity (equilateral triangles, regular pentagons, the $\sqrt 3$ "double triangle"); the rational-coloring chapter shows precisely why they fail over $\mathbb{Q}^2$.
8. Key open problems the book frames for us: smallest $k$-point set of chromatic number $k$ for $k=5,6,7$ (Open Problem 5.4); is there a 5-chromatic UDG in the plane (the recurring refrain); the 6-realizable set $X_6$ ($1 \in X_6 \Rightarrow \chi \le 6$; $1 \notin X_6 \Rightarrow \chi=7$, Ch 7).
9. The book's editorial bet: Soifer conjectures $\chi(\mathbb{R}^2) = 4$ or $7$, and if forced, $7$ (Ch 47). Erdos bet $\ge 5$ (since confirmed by de Grey).
10. Most of the long biographical material (Parts VI-VIII, van der Waerden, Schur, Ramsey) is historical, but the embedded theorems (Schur, van der Waerden, Gallai, Hales-Jewett) feed directly into O'Donnell's arbitrary-girth construction in Part IX.

## Top actionable takeaways for the project

1. The bottleneck is structurally explained, not just asserted (Ch 12-15, Ch 43-45): O'Donnell's cycle-attachment + continuity-argument embedding works because it only ever needs to embed 4-chromatic graphs. A 5-chromatic abstract graph built by attaching spindles to a foundation set "may be too rigid to have an Euclidean embedding in the plane" (p. 97, lines 4552-4555). Any BUILDER attempt at a $\chi\ge6$ embeddable graph must overcome rigidity, not just chromatic number.
2. The Euclidean-dimension concept (Ch 13) is the precise invariant the project should track: $\chi(G)=\chi(V)$ holds exactly when $G$ is EUCLIDEANLY embedded (adjacency iff distance 1), not merely 1-embedded. `EdimG <= 2*chi(G)` (Problem 13.18) and `EdimG <= 2*Delta(G)` (Lovasz-Saks-Schrijver, Problem 13.23). The latter ties embeddability to max degree, not chromatic number, which is exactly why high-chromatic + low-degree (flexible) graphs are the embeddable ones.
3. The continuity argument (Tool 14.1) is the reusable embedding primitive: attach a path with a free starting angle, find a "too short" and a "too long" configuration, invoke the intermediate value theorem to get "just right." This is implementable and is how every world-record graph was embedded. A VERIFIER could re-derive the world-record coordinates from this.
4. Detector confirmation: Woodall $\chi(\mathbb{Q}^2)=2$ (Result 11.2, line 3678) with full proof; Benda-Perles $\chi(\mathbb{Q}^3)=2$, $\chi(\mathbb{Q}^4)=4$; Mann/Cibulka $\chi(\mathbb{Q}^5)\ge 8$, $\chi(\mathbb{Q}^7)\ge 15$. The jump $4 \to \ge 8$ at $\mathbb{Q}^4 \to \mathbb{Q}^5$ is a sharp structural signal. Any combinatorial lower-bound argument that would also run over $\mathbb{Q}^2$ is wrong.
5. de Bruijn-Erdos compactness (Ch 5 statement, Ch 26 proof) is the theorem that licenses the entire A1/SAT program, and it ASSUMES the Axiom of Choice (footnotes at lines 2329, 3654, 9503). Part X shows this assumption is load-bearing: without AC the reduction to finite subsets can fail. Flag for A4: the SAT program's validity is conditional on AC.
6. World-record smallest 4-chromatic UDGs (Ch 15): girth 4 -> 23 vertices (Hochberg-O'Donnell "Fish"); girth 5 -> 45 vertices (Hochberg-O'Donnell "Star"). These are the floors; the open problem is whether 23 is optimal. BUILDER baselines.
7. Falconer $\chi_m \ge 5$ (Ch 9, Theorem 9.1) is given with a complete proof keyed to a "double equilateral triangle" of side 1 with $|xw|=\sqrt 3$ and the number-theoretic fact that $\arcsin(1/(2\sqrt3))$ is an irrational multiple of $\pi$ (via $\mathbb{Q}(\sqrt{-11})$ unique factorization, Tool 9.9). This is the measurable-architecture cornerstone and is Euclidean-rigidity-dependent.
8. The Shelah-Soifer unit-distance graph (Payne, Example 46.27, lines 22100+) is a UDG on $\mathbb{R}^2$ with $\chi_{ZFC}=2$ but $\chi_{ZFS}\ge 3$. It is built by tiling $\mathbb{R}^2$ with translated copies of the Woodall $\mathbb{Q}^2$ graph. This is the concrete A4 object and it sits INSIDE the unit-distance plane, making the "CNP itself may be axiom-dependent" worry concrete.
9. Conditional CNP Theorem (47.1): IF every finite UDG has $\chi \le 4$, THEN $\chi_{ZFC}(\mathbb{R}^2)=4$ but $\chi_{ZFS^+}(\mathbb{R}^2)\ge 5$. Unconditional (47.2): $\chi_{ZFS^+}(\mathbb{R}^2)\ge 5$ always (from Falconer + Solovay measurability). de Grey 2018 has since shown the hypothesis of 47.1 is false, but 47.2 stands and is a clean A4 result.
10. The 6-coloring continuum (Ch 7) and the 6-realizable set $X_6$ reduce the upper-bound question to: is $1 \in X_6$? If yes, $\chi \le 6$; if no, $\chi=7$. This is an alternate attack route on the UPPER bound (currently 7) that the project has not exploited.

---

## Part II: Colored Plane

### Chapter 2: Chromatic Number of the Plane: The Problem (pp. 13-20, lines 1271-1546)

Definitions. CNP: smallest number of colors to color $\mathbb{R}^2$ so no two points at distance 1 share a color, denoted $\chi$. "Realizes distance $d$": a monochromatic set contains a segment of length $d$.

Theorems / constructions (all elementary, all Euclidean-rigidity-based):
- Problem 2.1 (Adam and Eve): $\chi \ge 3$ via a unit equilateral triangle (pigeonhole on 3 vertices, 2 colors).
- Problem 2.2: $\chi \ge 4$ via the Moser spindle (7 vertices, all edges length 1; any 3 points contain a unit pair, so at most 2 of 7 can share a color). Second version (Hadwiger 1961): a unit rhombus $ABA'C$ with $A,A'$ forced same color, rotate to sweep a monochromatic circle of radius $|AA'|=\sqrt3$ containing a unit chord. THIRD route: the Golomb graph (10 vertices: regular hexagon + center + outer triangle, side 1, collapsed from a 3D toothpick model), discovered by Golomb 1960-1965.
- Problem 2.3: $\chi \le 9$ via 3x3 unit-square tiling.
- Problem 2.4: $\chi \le 7$ via regular hexagons of diameter $<1$, 7-color "flower" (Isbell/Hadwiger). Szekely's square-based 7-coloring (Problem 2.5) avoids hexagons.

Key reusable observation (line 1349-1353): in a spindle forbidding distance 1, at most 2 of the 7 vertices share a color (used again in Ch 4 and Ch 40 for the polychromatic lower bound).

Bearing: A1 foundations. Every lower-bound gadget here uses equilateral triangles / the specific value $\sqrt3$. DETECTOR: all of these would collapse over $\mathbb{Q}^2$ (no unit equilateral triangle exists in $\mathbb{Q}^2$), which is exactly why $\chi(\mathbb{Q}^2)=2$ and these are legitimately Euclidean.

### Chapter 3: Historical Essay (pp. 21-31, lines 1548-1990)

History: problem created by Edward Nelson (autumn 1950, age 18/19, $\chi\ge4$); upper bound $\chi\le7$ by John Isbell (1950). Propagated via Isbell -> Klee -> Hadwiger; Leo Moser -> Erdos and Gardner (first print: Gardner, Scientific American, Oct 1960). NOT Hadwiger's or Gardner's problem despite frequent miscredit. Erdos bet $\chi\ge5$.

Bearing: provenance; no new math. Conjecture 3.5: the bounds $4\le\chi\le7$.

### Chapter 4: Polychromatic Number, Lower Bound (pp. 32-38, lines 2000-2298)

Definitions. Polychromatic number $\chi_p$ (Erdos): smallest number of colors to color $\mathbb{R}^2$ so that NO color realizes ALL distances (each color $i$ forbids SOME distance $d_i$, possibly distinct). $\chi_p \le \chi \le 7$.

Theorems:
- Raiskii's Theorem 4.2: $4 \le \chi_p$.
- Merkov's proof (the clean one, lines 2069-2104): place three Moser spindles $S_r, S_w, S_b$ sharing origin $O$, with edge lengths $r, w, b$ (the three forbidden distances). 18 vectors -> map $M: \mathbb{R}^{18} \to \mathbb{R}^2$. The "at most 2/7 of a spindle is one color" observation forces each color to occupy at most $2/7$ of a structured point set $W$ ($7^3$ points). Since $3 \times 2/7 < 1$, contradiction.
- $\chi_r = \max_S \chi(G_S(\mathbb{R}^2))$ over $r$-element forbidden-distance sets $S$. Erdos Conjecture 4.3: does $\chi_r$ grow polynomially? Open Problem 4.4: find the $S$-chromatic number for given $S$ (for $|S|=1$ this IS CNP).

Bearing: A1/A3 boundary (chromatic numbers of distance graphs with multiple forbidden distances). The $2/7$ density bound is a fractional-flavored argument (proto-A3). DETECTOR: spindle-based, so Euclidean.

### Chapter 5: De Bruijn-Erdos Reduction to Finite Sets (pp. 39-42, lines 2300-2452)

THE compactness statement (proof deferred to Ch 26):

> De Bruijn-Erdos Compactness Theorem 5.1 (1951): The chromatic number of the plane equals the maximum chromatic number of its finite subsets. [Footnote line 2329: "The axiom of choice is assumed in this result."] [Footnote line 2330-2331: "Or so we all thought until recently... see Part X."]

General form (Ch 26): an infinite graph $G$ is $k$-colorable iff every finite subgraph is. This LICENSES the entire A1/SAT program: CNP is a question about finite plane sets.

Related finite problems:
- $\eta_k$ = smallest number of points in a plane set of chromatic number $k$. $\eta_3=3$ (triangle), $\eta_4=7$ (spindle, Moser-Moser).
- Open Problem 5.4 (Klee-Wagon): find $\eta_5, \eta_6, \eta_7$. Only meaningful if $\chi>4$; suggests building new "spindles." DIRECTLY relevant to the bottleneck.
- $\eta_3 = 5$ for triangle-free sets (regular unit pentagon, Problem 5.5).
- Erdos's \$25 Problem 5.6/5.7: do triangle-free (or arbitrarily-large-girth) unit-distance sets have $\chi\le 3$? Answered NO by Wormald (girth-5, $\chi=4$, 6448 points) and decisively by O'Donnell.
- O'Donnell's Theorem 5.9: there exist 4-chromatic UDGs of arbitrary finite girth. (Proof split across Ch 14 and Ch 45.)

Bearing: A1 (the licensing theorem) and A4 (AC dependence flagged twice). The repeated "build a 5-chromatic UDG" refrain (Hochberg vs O'Donnell rivalry, lines 2418-2451) is the bottleneck stated historically.

### Chapter 6: Polychromatic Number, Upper Bound (pp. 43-49, lines 2454-2649)

- Stechkin's 6-coloring (Problem 6.1): $\chi_p \le 6$. Parallelogram unit of 4 regular hexagons + 8 triangles, colors 1-4 hexagons, 5-6 triangles by orientation. Type $(1,1,1,1,1/2,1/2)$ after rescaling.
- Coloring TYPE (Definition 6.2): an $n$-coloring is of type $(d_1,\dots,d_n)$ if color $i$ forbids distance $d_i$. A 6-coloring of type $(1,1,1,1,1,1)$ would be the prize.
- Soifer's 6-coloring (Problem 6.4): type $(1,1,1,1,1,1/\sqrt5)$ via squares + non-regular octagons.
- Almost-chromatic number $\chi_a$ (Definition 6.5): $4 \le \chi_a \le 6$. Open Problem 6.6: find $\chi_a$.

Bearing: upper-bound / polychromatic. The "type" language sets up Ch 7's reduction of the upper bound to a single membership question.

### Chapter 7: Continuum of 6-Colorings (pp. 50-56, lines 2651-2962)

- Hoffman-Soifer (Problem 7.1): type $(1,1,1,1,1,\sqrt2-1)$.
- 6-realizable set $X_6$ (Open Problem 7.2): all $\alpha>0$ with a 6-coloring of type $(1,1,1,1,1,\alpha)$.
- Theorem 7.3: $[\sqrt2-1, 1/\sqrt5] \subseteq X_6$ (a full continuum), via a one-parameter family of square+octagon tilings; reduces to a degree-6 polynomial that factors cleanly.
- CRITICAL remark (lines 2931-2938): if $1 \notin X_6$ then $\chi=7$; if $1 \in X_6$ then $\chi \le 6$.

Bearing: a concrete, computational route to deciding the UPPER bound. The project has not pursued $X_6$. Possible A1/A3 hybrid target: certify $1 \notin X_6$ would give $\chi=7$ outright.

### Chapter 8: CNP in Special Circumstances (pp. 57-59, lines 3045-3056)

Corollaries of the Townsend-Woodall theorem (Ch 24):
- Map-colored plane (Result 8.1): $\chi$ under map-type coloring is 6 or 7.
- Closed-set coloring (Result 8.2, Woodall): $\chi$ with closed monochromatic sets is 6 or 7. Proof via Tool 8.3 (a bounded closed set forbidding $d$ forbids a neighborhood $[d-\epsilon,d+\epsilon]$) and a square-lattice refinement.
- Open-set coloring (Result 8.4, Brown-Dunfield-Perry): 6 or 7.

Bearing: shows that if color classes are topologically nice (closed/open/map-like), the lower bound jumps from 4 to 6. This is a regularity-assumption analog of the measurable case (A2). DETECTOR: these are topological/Euclidean arguments.

### Chapter 9: Measurable Chromatic Number (pp. 60-66, lines 3058-3390)

THE A2 cornerstone. Full proof hand-written for the book by Falconer.

> Falconer's Theorem 9.1: If $\mathbb{R}^2 = \bigcup_{i=1}^4 A_i$ is a covering by four disjoint MEASURABLE sets, one $A_i$ realizes distance 1. Equivalently $\chi_m(\mathbb{R}^2) \in \{5,6,7\}$.

Proof machinery (Tools 9.3-9.9):
- Lebesgue Density Theorem; $\tilde A = \{x: D(A,x)=1\}$, density boundary $\partial A$ (measure 0).
- Tool 9.6: there is $x$ in the "boundary set" $M$ with both circles $C(x,1)$ and $C(x,\sqrt3)$ meeting $M$ in length 0.
- Tool 9.7: the "double equilateral triangle" (rhombus of two unit equilateral triangles, $|xw|=\sqrt3$) forces, in almost all orientations, that the far vertex $w$ lands in one of two specific color classes. Hence $C(x,\sqrt3)$ is almost entirely covered by $\tilde A_1 \cup \tilde A_2$.
- Tool 9.8: on a circle of radius $r>1/2$, if two measurable sets cover it and $\phi=2\arcsin(1/2r)$ is an irrational multiple of $\pi$, one of them realizes distance 1.
- Tool 9.9 (number theory): $(1-i\sqrt{11})^{2m} \ne (-12)^m$, because $\mathbb{Q}(\sqrt{-11})$ is Euclidean (unique factorization). This shows $\arcsin(1/(2\sqrt3))$ is an irrational multiple of $\pi$, closing the proof at $r=\sqrt3$.

Bearing: A2 PRIMARY SOURCE. The proof is deeply Euclidean (relies on the exact $\sqrt3$ geometry and on $\mathbb{Q}(\sqrt{-11})$). DETECTOR note: A2 is partly exempt from the $\mathbb{Q}^2$ control (measure-zero on rationals is legitimate), and indeed this proof uses measure positivity that vacuously fails on $\mathbb{Q}^2$. This is the ancestor of the modern $\chi_m \ge 6$ Fourier/autocorrelation work (NOT in this book).

### Chapter 10: Coloring in Space (pp. 67-71, lines 3454-3654)

Higher-dimensional bounds (A1/A2 context):
- Raiskii lower bound: $n+2 \le \chi(\mathbb{R}^n)$. So $\chi(\mathbb{R}^3) \ge 5$.
- Nechushtan 2000: $\chi(\mathbb{R}^3) \ge 6$.
- Coulson: $\chi(\mathbb{R}^3) \le 15$ (face-centered-cubic lattice). Soifer Conjecture 10.4: $\chi(\mathbb{R}^3)=15$.
- Cantwell: $\chi(\mathbb{R}^4)\ge 7$, $\chi(\mathbb{R}^5)\ge 9$. Cibulka: $\chi(\mathbb{R}^6)\ge 11$.
- Frankl-Wilson (1981): $(1+o(1))1.2^n \le \chi(\mathbb{R}^n)$ (exponential lower bound). Larman-Rogers (1972): $\chi(\mathbb{R}^n) \le (3+o(1))^n$. Raigorodskii: $(1.239\ldots+o(1))^n$.
- Erdos Conjecture 10.7: $\chi(\mathbb{R}^n) \to \infty$ exponentially (settled by Frankl-Wilson + Larman-Rogers).

Bearing: the Frankl-Wilson method (forbidden-intersection / linear algebra bound) is a genuine A3-adjacent technique and is the asymptotic engine; worth noting the project's A3 thread could mine it.

### Chapter 11: Rational Coloring (pp. 72-76, lines 3656-3848) - DETECTOR CHAPTER

> Chromatic Number of $\mathbb{Q}^2$, Result 11.2 (Woodall 1973): $\chi(\mathbb{Q}^2) = 2$.

Proof (lines 3680-3743): partition $\mathbb{Q}^2$ by the equivalence "both coordinate differences have ODD denominators in lowest terms." If two rational points are at distance 1, then $(a/b)^2+(c/d)^2=1 \Rightarrow a^2d^2+b^2c^2=b^2d^2$, forcing $b,d$ both ODD, so the two points lie in the SAME class. Each class is a translate of the class of the origin; 2-color that class by parities of numerators ($o/o, e/o$ patterns). No two same-colored points are at distance 1.

Extensions:
- Benda-Perles: $\chi(\mathbb{Q}^3)=2$, $\chi(\mathbb{Q}^4)=4$. Open: $\chi(\mathbb{Q}^n)$ general, and algebraic extensions $\chi(\mathbb{Q}^2(\sqrt2))$.
- Mann: $\chi(\mathbb{Q}^5)\ge 7$, $\chi(\mathbb{Q}^6)\ge 10$, $\chi(\mathbb{Q}^7)\ge 13$, $\chi(\mathbb{Q}^8)\ge 16$.
- Cibulka: $\chi(\mathbb{Q}^5)\ge 8$, $\chi(\mathbb{Q}^7)\ge 15$.
- Open Problem 11.1: find a COUNTABLE $C \subset \mathbb{R}$ with $\chi(C^2)=\chi(\mathbb{R}^2)$. ($\mathbb{Q}$ fails.)

Bearing: THE structural control object for A1/A3. $\chi(\mathbb{Q}^2)=2$, $\chi(\mathbb{Q}^3)=2$, $\chi(\mathbb{Q}^4)=4$, then a JUMP to $\ge 8$ at $\mathbb{Q}^5$. The key mechanism: distance-1 pairs in $\mathbb{Q}^2$ are forced into a single "odd-denominator" coset where the geometry is 2-colorable. Any A1 lower-bound proof that does not break this odd-denominator structure (i.e., does not use a genuinely irrational/topological feature of $\mathbb{R}$) would also color $\mathbb{Q}^2$ with 2 colors and is therefore structurally wrong. The Payne graph (Ch 46) tiles $\mathbb{R}^2$ by translated $\mathbb{Q}^2$ copies precisely to exploit this.

---

## Part III: Coloring Graphs (the bottleneck machinery)

### Chapter 12: Chromatic Number of a Graph (pp. 79-87, lines 3853-4186)

Basics: $\chi(G)$, $\chi(C_n)=2/3$ (even/odd), bipartite iff no odd cycle, $\chi(K_n)=n$, $\chi(G)\le\Delta(G)+1$, Brooks $\chi(G)\le\Delta(G)$ (non-complete, $\Delta>2$).

Chromatic number and GIRTH (12.2), central to the bottleneck:
- Descartes' Construction 12.10 (Tutte, 1954): for any $n$, an $n$-chromatic graph $G_n$ of girth 6, by recursive cycle-attachment to foundation sets (the "$G_{k+1}$ from $G_k$" inductive attach).
- Problem 12.8: attach a 3-cycle to each 3-subset of a 7-point foundation set -> 112-vertex 4-chromatic graph. (Pigeonhole: 3 of 7 monochromatic forces a 2-colored triangle.)
- Problem 12.9: same with a Moser spindle and 25-point foundation -> 5-chromatic graph on 3,364,925 vertices. (Trivially 5-chromatic abstractly, BUT triangle-rich and rigid; almost certainly NOT embeddable.)
- Mycielski Construction 12.11: triangle-free $n$-chromatic graphs. Mycielski-Grotzsch graph = unique smallest triangle-free 4-chromatic graph (11 vertices).
- Erdos Theorem 12.12 (1959, probabilistic; Lovasz 1968 constructive): $n$-chromatic graphs of girth $m$ exist for all $m,n$.

Wormald's application (12.3): the Descartes/Wormald graph $G_{13,5\text{-cycle},\binom{13}{5}}$ = 6448 vertices, 4-chromatic, girth 5, and Wormald EMBEDDED it in $\mathbb{R}^2$ (the hard part). Open Problem 12.15: smallest 4-chromatic UDG with no 3- or 4-cycles.

Bearing: A1 bottleneck. The chapter makes explicit the two-part recipe (build abstract high-chromatic graph cheaply; embed it expensively) and that the SECOND step is the wall. The 5-chromatic abstract graph is trivial; embedding it is the unsolved problem.

### Chapter 13: Dimension and Euclidean Dimension of a Graph (pp. 88-98, lines 4188-4580) - DEFINE PRECISELY

- Dimension $\dim G$ (Erdos-Harary-Tutte 1965): min $n$ such that $G$ 1-EMBEDS in $\mathbb{R}^n$ (every edge a unit segment; non-edges UNRESTRICTED). E.g. $\dim K_n = n-1$; $\dim K_{m,n}=4$ for $m,n\ge3$ (Lenz: two orthogonal circles of radius $1/\sqrt2$ in $\mathbb{R}^4$). $\dim G \le 2\chi(G)$ (Problem 13.10).
- Euclidean dimension $\mathrm{Edim}\,G$ (Soifer; = Erdos-Simonovits "faithful dimension," 1980): min $n$ such that $G$ has a EUCLIDEAN embedding in $\mathbb{R}^n$, meaning adjacency iff distance exactly 1 (non-edges must NOT be at distance 1). 

CRITICAL identity (lines 4438-4442, Problem 13.13): for a EUCLIDEAN embedding, $\chi(G) = \chi(V)$ where $V$ is the embedded vertex set. This is the bridge from abstract graph chromatic number to plane-set chromatic number. 1-embedding does NOT give this (C4 1-embeds as both a square, $\chi=2$, and a $\pi/3$ rhombus, $\chi=3$).

Bounds: $\dim G \le \mathrm{Edim}\,G \le 2\chi(G)$ (Problem 13.18); $\mathrm{Edim}\,G \le 2\Delta(G)+1$ (Erdos-Simonovits) improved to $\mathrm{Edim}\,G \le 2\Delta(G)$ (Lovasz-Saks-Schrijver, Problem 13.23, still best known). $\mathrm{Edim}$ is NOT subgraph-monotone ($W_6'$, the 6-wheel minus a spoke, has $\mathrm{Edim}=3$ while $W_6$ has $\mathrm{Edim}=2$ - rigidity forces a phantom unit distance). $\mathrm{Edim}\,G - \dim G$ can be arbitrarily large (Problem 13.21).

End of chapter (lines 4548-4580): the explicit program statement: "If you believe $\chi\ge5$, create a 5-chromatic graph $G$ and Euclideanly embed it." Notes that spindle-based 5-chromatic graphs are too rigid; Grotzsch-based ones (34-billion-vertex) are triangle-free but the Grotzsch graph itself does not Euclidean-embed. Suggests starting from the FLEXIBLE Wormald graph and attaching.

Bearing: A1 bottleneck, the key INVARIANT. $\mathrm{Edim} \le 2\Delta$ says embeddability is governed by max degree, not chromatic number; the embeddable graphs are the flexible (low-degree, triangle-free) ones, and these are hard to push past $\chi=4$. This is the precise reason the bottleneck exists.

### Chapter 14: Embedding 4-Chromatic Graphs in the Plane (pp. 99-109, lines 4582-5222) - MAXIMAL DETAIL, THE BOTTLENECK TOOL CHEST

O'Donnell's embedding machinery. Two-part recipe (lines 4592-4597): (1) graph-theoretic - show $\chi(G)=4$, no short cycles; (2) geometric - embed with adjacency iff distance 1.

Core notions:
- Attachment: a $k$-vertex graph $G$ is "attached" to a vertex set $V^*$ (the "shadow"/foundation) via a matching of new unit edges. Foundation vertices are a large independent set.
- Continuity Argument 14.1 (THE primitive, lines 4651-4686): fix shadow points; let $u_1$ slide on a unit circle and define $u_i$ inductively at distance 1 from $u_{i-1}$ and its shadow point. If some position gives the closing distance $<1$ ("too short") and another gives $>1$ ("too long"), by continuity (IVT) there is a "just right" position closing the cycle exactly. This attaches a $k$-cycle to the foundation set.
- Four foundation regions: $\delta$-balls around $C_1=(0,0)$, $C_2=(0,0.9)$, $C_3=(0.9,0.9)$, $C_4=(0.9,0)$. A cycle CANNOT attach if all its foundation vertices are in ONE $\delta$-ball; it CAN if they are spread across $\ge 2$ balls. Type $(a_1,a_2,a_3,a_4)_\delta$ = $a_i$ vertices in the ball around $C_i$.

Attachment tools (the constructive core):
- Tool 14.2/14.3: attach a 3-cycle to 3 foundation points (at centers, then anywhere in $\delta$-balls of type $(1,1,1,0)_\delta$). Explicit coordinates in the Appendix (lines 5078-5222): "too short" / "too long" / "just right" triangle points $T_i$ and spoke points $S_i$ to 5 decimals.
- Tool 14.4: attach any odd $k$-cycle to type $(a_1,a_2,a_3,0)_\delta$ by inductively inserting a "detour" (build a 5-cycle $u_1, z, u_1, u_2, u_3$ from a 3-cycle, etc.; $z$ just needs to be $<2$ from $u_1$).
- Tool 14.5: type $(a_1,a_2,a_3,1)_\delta$ (one vertex in the 4th ball) by replacing $u_1$ with a path $u_1,u_4,u_{1a}$.
- Tools 14.6/14.7: types $(a_1,a_2,0,0)_\delta$ and $(a_1,0,a_3,0)_\delta$ (only TWO balls used) by treating one ball as two overlapping balls.
- Removing Coincidences (14.6, Tools 14.8): if two vertices coincide, perturb a foundation vertex (within its $\delta$-ball) so one cycle moves and the other does not, strictly reducing the coincidence count without introducing new ones (two cases: vertices on different cycles / same cycle).

Immediate payoff (14.7): embed the Wormald 6448-vertex graph by placing 4 foundation vertices in each of $C_1,C_2,C_3$ + 1 in $C_4$, attaching all 5-cycles, removing coincidences. Likewise the 352,735-vertex girth-6 Blanche Descartes graph (6 vertices per ball + 1).

Bearing: A1 BOTTLENECK MACHINERY. This is the complete, implementable toolkit for turning a 4-chromatic abstract graph into a UDG. CRITICAL LIMITATION for the project: every tool here embeds graphs whose chromatic-increasing gadget is an ODD CYCLE attached to a foundation independent set. The construction's chromatic ceiling is 4 because the recipe is "3 colors for foundation forces a monochromatic foundation subset, the attached odd cycle then needs a 4th color." To get $\chi\ge5$ you need a gadget that forces a 5th color on the FOUNDATION itself, which is precisely what is missing. The continuity argument should transfer to higher-chromatic gadgets in principle; the open question is whether a $\ge5$-forcing gadget can be made flexible (low-degree, $\mathrm{Edim}=2$) enough to embed.

### Chapter 15: Embedding World Records (pp. 110-126, lines 5224-5670) - LIST RECORDS

Smallest 4-chromatic UDGs found via Ch 14 machinery, all published in Geombinatorics:

GIRTH 4 (Table 15.1, line 5614):
| Vertices | Author | Date |
|----------|--------|------|
| 6448 | Wormald | 1979 |
| 56 | O'Donnell | Jul 1994 |
| 47 | Chilakamarri ("Moth") | Jan 1995 |
| 46 | Hochberg | 1995 (unpublished) |
| 40 | O'Donnell ("Pentagonal") | Jul 1995 |
| 23 | Hochberg-O'Donnell ("Fish") | Apr 1996 |

GIRTH 5 (Table 15.2, line 5651):
| Vertices | Author | Date |
|----------|--------|------|
| 6448 | Wormald | 1979 |
| 45 | Hochberg-O'Donnell ("Star") | Apr 1996 |

Construction notes:
- 56-vertex (15.1): start from $H$ = Mycielskian of $C_{10}$ (= subgraph of the 5-cube projected along a diagonal, vertices = 5th roots of unity, so it is ALREADY a UDG and FLEXIBLE), attach seven 5-cycles. O'Donnell's closing remark (line 5377): triangle-free graphs "seem to be flexible... perhaps flexibility will prove useful in a construction of a 5-chromatic graph in the plane!"
- 40-vertex (15.3): start from a modified 15-vertex Mycielski-Grotzsch (central vertex split into 5), attach five 5-cycles.
- 23-vertex Fish (15.4): GENERALIZED attachment - a cycle need not have all vertices attached, and a foundation vertex may receive more than one cycle vertex. Uses the square $\{w,x,y,z\}$ (one of $\{w,y\},\{x,z\}$ monochromatic in any 3-coloring) + partial 5-cycle attachments. The 23-vertex Fish satisfies all Grotzsch conditions PLUS being a UDG.
- 45-vertex Star (15.5): Petersen graph (UDG-embeddable per EHT 1965) + 7-cycles attached to the 5 rotations of a 4-vertex independent set.

Open Problems 15.4/15.5: smallest 4-chromatic UDG of girth 4 (is 23 optimal?) and girth 5.

Bearing: A1 BUILDER baselines. These give the floor for 4-chromatic UDGs. The recurring theme that "triangle-free = flexible = embeddable" but stuck at $\chi=4$ is the crux of the $\chi\ge6$ bottleneck. Note: NONE of these is $\ge5$-chromatic; the world records are all girth/size records for the $\chi=4$ class.

### Chapter 17: Thomassen's 7-Color Theorem (pp. 140-144, lines 6190-6343)

> Thomassen's 7-Color Theorem 17.1: A connected graph $G$ on a surface $S$ with (i) every non-contractible simple closed curve has diameter $\ge2$, (ii) simple closed curves of diameter $<2$ enclose area $\le k$, (iii) $\mathrm{diam}(S)\ge 12k+30$, requires $\ge 7$ colors for any "nice" coloring (color classes = unions of regions pairwise $>1$ apart).

Proof engine: Tool 17.2 (a connected, locally finite, locally Hamiltonian graph with $\ge13$ vertices has a vertex of degree $\ge6$), applied to the map graph $\Gamma(G,S)$ via a 2-separator / crucial-edge reduction. All three hypotheses shown essential (cylinders / small sphere counterexamples).

Bearing: this is a 7-color LOWER bound under a "nice" (separated, map-like) coloring regularity condition, analogous to Townsend-Woodall. Confirms that regularity assumptions push the lower bound to 6 or 7. A1/topological; not directly a UDG result, but relevant to the upper-bound debate.

---

## Part IV/V (selected)

### Chapter 24: Townsend-Woodall's 5-Color Theorem (pp. 209-224, lines 8500-8700+)

> Townsend-Woodall 5-Color Theorem 24.1: Every 5-colored PLANAR MAP contains two points of the same color at unit distance. Equivalently (24.1'): the chromatic number of the plane under MAP-TYPE coloring is 6 or 7.

History: Woodall 1973 claimed it, Townsend (1979) found the error + counterexample to a sub-claim + a correct (harder) topological proof. Proof (written by Townsend for this book) uses point-set topology: monochrome units, "subtends at unit distance," unit annuli, planar maps as (regions, frontiers). 

Bearing: same family as Ch 8 and Ch 17 - map/closed-set regularity forces lower bound to 6. Relevant to upper-bound architecture. DETECTOR: Euclidean (unit circles, unit annuli).

### Chapter 26: De Bruijn-Erdos Theorem and Its History (pp. 236-241, lines 9460-9583) - PROOF

> De Bruijn-Erdos Compactness Theorem 26.1 (1951): An infinite graph $G$ is $k$-colorable iff every finite subgraph is $k$-colorable. [Footnote line 9503: "This theorem requires the Axiom of Choice or equivalent."]

Proof (Karabash, via Zorn's Lemma): Let $S$ = all super-graphs of $G$ (added edges only) such that every finite subgraph is $k$-colorable, ordered by edge inclusion. Every chain has an upper bound (its union), so Zorn gives a maximal $M$. Non-adjacency in $M$ is an equivalence relation (else an edge could be added), so the complement $M'$ is a disjoint union of complete graphs; there are $\le k$ of them (else a $K_{k+1}$ finite subgraph would not be $k$-colorable). Color each clique a distinct color. $G \subseteq M$ inherits the $k$-coloring.

Generalizes to HYPERGRAPHS (Theorem 26.4): $\chi(H)$ = max over finite subhypergraphs (same proof). This is what O'Donnell exploits in Part IX.

Bearing: A1 (licenses SAT) AND A4 (AC-dependence, the hinge of Part X). The hypergraph version is the engine for the arbitrary-girth construction.

### Embedded Ramsey theorems (Parts VI-VIII, brief)

- Schur's Theorem 32.1: for any $n$ there is $S(n)$ such that any $n$-coloring of $\{1,\dots,S(n)\}$ has monochromatic $a+b=c$. (Bound $S(m): N>m!e$ suffices, Thm 34.1.)
- Van der Waerden's Theorem 33.1 (= Baudet-Schur-vdW, 1927): for any $k,l$ there is $W(k,l)$ such that any $k$-coloring of $\{1,\dots,W(k,l)\}$ has a monochromatic $l$-term arithmetic progression. (Used directly in Ch 43.)
- Generalized Schur 35.1: monochromatic $l$-term AP together with its common difference.
- Gallai's Theorem 42.1/42.2 (Gallai-Witt, pub. Rado): any finite coloring of $\mathbb{Z}^n$ (or $\mathbb{R}^n$) contains a monochromatic homothetic copy of any finite configuration $A$. (Used to force monochromatic polygons.)
- Hales-Jewett Theorem 42.8: for any finite alphabet $A$ and $k$, large enough $n$ makes every $k$-coloring of $A^n$ contain a monochromatic combinatorial line. Implies Gallai (Connection 42.9).

Euclidean Ramsey (Part VIII, Ch 40-41): monochromatic polygons in 2-colored plane (Garsia/Cohen via vdW: any 2-colored plane has a monochromatic square; any finite point set up to scaling). Ramsey sets (Erdos \$500 Problem 41.17: characterize which sets are Ramsey).

Bearing: feeds Part IX. Not CNP lower bounds themselves, but the combinatorial fuel for O'Donnell's girth control.

---

## Part IX: Colored Integers in Service of CNP (pp. 521-531, lines 20760-21274)

How O'Donnell builds 4-chromatic UDGs of ARBITRARY girth (solving Erdos's \$25 Problem 5.6/5.7).

Notation: $G_{n,k\text{-cycle},S}$ = foundation set $\{1,\dots,n\}$ with a $k$-cycle attached to each set in a family $S$ of subsets (here, arithmetic progressions). (Problem-12.8 graph = $G_{7,3\text{-cycle},\binom{[7]}{3}}$; Wormald = $G_{13,5\text{-cycle},\binom{[13]}{5}}$.)

Chapter 43 (girth 9, via van der Waerden): attach $k$-cycles only to APs whose common differences come from a sparse set $D$ (Eq 43.2-43.3) chosen so distinct-difference APs overlap in $\le1$ point and same-difference APs are disjoint.
- Theorem 43.2: $\chi(G_{n,k\text{-cycle},S})=4$ for some $n$, BY van der Waerden (a long monochromatic AP forces a monochromatic foundation set with an attached odd cycle -> needs a 4th color).
- Theorem 43.3: girth $\ge\min(9,k)$ for odd $k\ge9$.

Chapter 44 (girth 12, via Bergelson-Leibman + Mordell-Faltings): make common differences $m'$-th powers, so AP-intersection equations become $ax^{m'}+by^{m'}+cz^{m'}=0$ with no nontrivial primitive solutions (Mordell-Faltings Corollary 44.2, Tool 44.3, Corollary 44.5). Gives girth $\ge12$ (Theorem 44.6), $\chi=4$ via Bergelson-Leibman polynomial vdW (Theorem 44.7). Embedding (44.8) reuses Ch 14 tools.

Chapter 45 (arbitrary girth, the clean solution, via Erdos-Hajnal hypergraphs):
- Theorem 45.1 (Erdos-Hajnal 1966): for all $k,g,l\ge2$ there exist $k$-uniform, girth $g$, $l$-chromatic HYPERGRAPHS.
- O'Donnell's idea: attach $k$-cycles to the HYPEREDGES of a $k$-uniform, girth $g$, 4-chromatic hypergraph $H$ (instead of to APs). $G_{n,k\text{-cycle},H}$.
- Theorem 45.2: $\chi=4$ (since $H$ 4-chromatic, any 3-coloring of foundation has a monochromatic hyperedge = monochromatic attached cycle's shadow).
- Theorem 45.3: girth $=k$ (choose $g\ge k/3$).
- O'Donnell's Theorem 45.4: for any $k\ge3$ there is a girth-$k$, 4-chromatic UNIT DISTANCE graph. Embed via Ch 14 (place color-$i$ foundation vertices in ball $C_i$, $i=1,2,3$; vertex $n'$ in $C_4$; attach all cycles; remove coincidences).

CRITICAL repeated observation (lines 21156-21159, 20961-20963): "the only reasonable candidate for embedding in the plane as unit distance graphs seem to be the 4-colorable graphs." The method generalizes to $l$-chromatic abstract graphs, but only the $l=4$ case is known to embed.

Bearing: A1 BOTTLENECK, the deepest statement of it. O'Donnell unified Ramsey theory and CNP, but the unification produces ARBITRARILY HIGH GIRTH at $\chi=4$, never $\chi=5$. The girth lever and the chromatic lever appear decoupled in the embeddable regime. For the project: a $\chi\ge6$ embeddable graph would need to break the "$\chi=4$ embeds, $\chi\ge5$ does not" pattern that O'Donnell's entire program reinforces.

---

## Part X: Predicting the Future (A4 PRIMARY SOURCE)

### Chapter 46: What If We Had No Choice? (pp. 535-552, lines 21283-22186)

Setup: de Bruijn-Erdos needs AC. Soifer-Shelah ask: in a choiceless set theory, does CNP change?

Axiom systems: ZF, ZFC, ZF+DC (dependent choice), and the Solovay system ZFS = ZF+DC+LM (LM = "all sets of reals Lebesgue measurable"), ZFS$^+$ = same but Solovay's consistency needs an inaccessible cardinal.
- Solovay's Theorem 46.1: ZFS$^+$ is consistent (relative to an inaccessible). In ZFS every set is measurable, so the usual Lebesgue theory survives.

Chromatic CARDINALITY set (Definition 46.1): without AC the chromatic number may not be a single number; $\chi_A(G)$ = set of minimal coloring cardinalities under axiom system $A$.

THE EXAMPLES (Shelah-Soifer class):
- Example 46.2 (on the line $\mathbb{R}$): edges $\{(s,t): s-t-\sqrt2 \in \mathbb{Q}\}$. Result 46.3: $\chi_{ZFC}=2$ (via an AC-chosen transversal of the equivalence $s\sim t \Leftrightarrow s-t \in \mathbb{Q}+\mathbb{Z}\sqrt2$), but $\chi_{ZFS}>\aleph_0$ (Tool 46.4: any measurable independent set in $[0,1)$ is null, via a translate-overlap density argument).
- Examples in the plane (46.5, 46.7): difference graphs with $\sqrt2$-shifts, $\chi_{ZFC}=4$ or $2$, $\chi_{ZFS}>\aleph_0$.
- Examples in space (46.9-46.13): $\chi_{ZFC}=2,\,2n,$ or any value in between; $\chi_{ZFS}>\aleph_0$.
- Karabash-Soifer (46.15-46.26): the Shelah-Soifer CLASS $S$ = graphs with $\chi_{ZFS}\cap\chi_{ZFC}=\emptyset$. Theorem 46.18: if 0 is a limit point of the distance set $D$, then $\chi_{ZFS}(G^n_D)>\aleph_0$ (via Steinhaus's Lemma). The class $S$ is "as big as" its complement (Theorem 46.22).

THE UNIT-DISTANCE SHELAH-SOIFER GRAPH (46.7, Payne 2007, lines 22079-22186):
- Example 46.27: vertex set $\mathbb{R}^2$; edges $\{(p_1,p_2): p_1-p_2\in\mathbb{Q}^2,\ |p_1-p_2|=1\}$. I.e. tile $\mathbb{R}^2$ by translated copies of the Woodall $\mathbb{Q}^2$ unit-distance graph.
- Claim 1: $\chi_{ZFC}(G)=2$ (each tile $\cong \mathbb{Q}^2$ graph, $\chi=2$ by Woodall; AC chooses an origin per tile).
- Claim 2: $3 \le \chi_{ZFS}(G) \le 7$. Proof (Tools 46.28/46.29): any positive-measure set contains the endpoints of a length-3 path in $G$ (using rational points dense on the unit circle to find a short rational horizontal displacement realizable by a 3-path), ruling out 2-coloring of any measurable color class.

Bearing: A4 CORNERSTONE. This is a UNIT-DISTANCE graph living in the actual Euclidean plane whose chromatic number is genuinely axiom-dependent ($2$ vs $\ge3$). It is the concrete object behind "CNP itself might be axiom-dependent." DETECTOR note: this is built FROM the $\mathbb{Q}^2$ detector graph; it shows the detector and the axiomatic phenomenon are intertwined. For the project's A4 thread, this is THE example to formalize/study.

### Chapter 47: A Glimpse into the Future (pp. 553-556, lines 22188-22317)

- Conditional CNP Theorem 47.1 (Shelah-Soifer): IF every finite unit-distance plane graph has $\chi\le4$, THEN $\chi_{ZFC}(\mathbb{R}^2)=4$ (by de Bruijn-Erdos) AND $\chi_{ZFS^+}(\mathbb{R}^2)\ge5$ (by Falconer 9.1 + Solovay measurability + a null-set-preserving bijection $I\to I^2$). [de Grey 2018 has since FALSIFIED the hypothesis: a finite UDG with $\chi=5$ exists. So 47.1's antecedent is now known false, but the theorem's STRUCTURE - that the answer can depend on axioms - remains the point.]
- Unconditional CNP Theorem 47.2: $\chi_{ZFS^+}(\mathbb{R}^2)\ge5$ (always, from Falconer). This is just the measurable bound restated in the choiceless setting.
- Pritikin: any unit-distance 7-chromatic graph has $\ge6198$ vertices.
- Soifer's Conjectures: $\chi(\mathbb{R}^2)=4$ or $7$ (47.3); if one value, $7$ (47.4); $\chi(\mathbb{R}^3)=15$ (47.5); $\chi(\mathbb{R}^n)=2^{n+1}-1$ (47.6).

Bearing: A4 + the project's framing. 47.2 is a clean unconditional result we can cite. The conjecture $\chi=4$ or $7$ is now partly refuted ($\ge5$ kills 4), so Soifer's fallback $\chi=7$ is the live high-end conjecture.

### Chapter 48: Imagining the Real, Realizing the Imaginary (pp. 557-563, lines 22319-22420)

Philosophical/foundational: surveys of Godel, Cohen, Shelah, Solovay views on AC and "truth." Solovay and Shelah both hold AC is "true" (so ZFS$^+$ is "false" but useful as an explication of "constructive"). No new CNP math.

Bearing: A4 context only. Useful framing: the working mathematician's ZFC is a CHOICE, and the CNP value may be an artifact of it.

---

## Discrepancy log (vs project atlas / current state)

1. Era gap: the book (2009) predates de Grey 2018 ($\chi\ge5$ via a 1581-vertex UDG) and Polymath16 (~510 vertices). The book's $4\le\chi\le7$ and Soifer's "$\chi=4$ or $7$" conjecture are now superseded on the low end ($\chi\ge5$). The book's Conditional CNP Theorem 47.1 has had its hypothesis ("every finite UDG is 4-colorable") refuted by de Grey. NOT a contradiction - just chronology. The project's landmark list (de Grey, Polymath16) correctly post-dates this book.
2. A2 $\chi_m\ge6$: the project's CLAUDE.md notes "$\chi_m\ge6$ in recent work" and the repo has L35/L36 work reproducing Ambrus 2023 integer $\chi_m\ge5$. The book only has Falconer $\chi_m\ge5$ (Ch 9). The Fourier/autocorrelation route to $\chi_m\ge6$ is entirely absent here; this book is the $\chi_m\ge5$ ancestor only. No conflict.
3. The book attributes the measurable $\ge5$ bound purely to Falconer's density/double-triangle method. The repo's A2 thread reaches $\chi_m\ge5$ by LP / IEC-congruence (Ambrus). These are DIFFERENT proofs of the same bound; flag that the book's Falconer proof is geometric-rigidity-based while the repo's is linear-programming-based. Not a disagreement, but a methodological fork worth noting for the SYNTHESIZER.
4. Detector consistency: the book independently confirms all three structural facts implicitly used by the project. $\chi(\mathbb{Q}^2)=2$ (Woodall, Ch 11) MATCHES the CLAUDE.md detector. The book does NOT discuss the $L^\infty$ plane ($\chi=4$, Chilakamarri) detector despite citing Chilakamarri's UDG work (Ch 15); flag that the $L^\infty$ detector is from a Chilakamarri paper NOT covered in this book.
5. AC-dependence of de Bruijn-Erdos: the book is emphatic (three footnotes + all of Part X) that the finite reduction needs AC, and that CNP might be axiom-dependent. The project's A1 SAT program implicitly assumes the reduction is valid (ZFC). This is consistent but the project should explicitly note (per Part X) that A1's lower bounds are ZFC results; an A4 caveat. The repo's MEMORY notes the three architectures "bottom out at one missing object (a $\chi$-6 embeddable UDG)" - the book reinforces this exactly and adds the A4 caveat that even the existence of such an object is what de Bruijn-Erdos (hence AC) would translate into $\chi(\mathbb{R}^2)\ge6$.
6. No A3 content: the project's fractional/Lovasz-theta architecture has essentially NO ancestor in this book. The closest is the $2/7$ density argument (Ch 4) and Frankl-Wilson (Ch 10). Flag: if the SYNTHESIZER expects this book to inform A3, it will not; A3 sources are elsewhere (Bachoc-DeCorte-Oliveira-Vallentin etc.).

---

## What this enables / what remains open

ENABLES (downstream agents):
- BUILDER: a complete, implementable embedding toolkit (Ch 14 continuity argument + cycle attachment + coincidence removal, with worked coordinates in the Appendix at lines 5078-5222). The world-record graphs (Ch 15: 23-vertex Fish girth 4, 45-vertex Star girth 5) are reproducible baselines. The recipe "$G_{n,k\text{-cycle},H}$ for a 4-chromatic hypergraph $H$" (Ch 45) is the general construction engine.
- BUILDER: the precise invariant to optimize is Euclidean dimension $\mathrm{Edim}$ (Ch 13), with $\mathrm{Edim}\le 2\Delta(G)$. To embed in the plane, target $\Delta$ small and triangle-free (flexible). The open challenge: a $\ge5$-color-FORCING gadget that stays flexible.
- ADVERSARY: the $\mathbb{Q}^2$ detector is fully proved here (Ch 11) with the odd-denominator mechanism; use it to reject any combinatorial lower-bound argument that does not break the odd-denominator coset structure. The $\chi(\mathbb{Q}^4)=4 \to \chi(\mathbb{Q}^5)\ge8$ jump is a finer detector.
- ADVERSARY / A4: the unit-distance Shelah-Soifer graph (Payne, Ch 46) is a concrete UDG with axiom-dependent $\chi$; any claimed UNCONDITIONAL CNP result must be checked against the ZFC-vs-ZFS distinction.
- SYNTHESIZER: Falconer $\chi_m\ge5$ (Ch 9) and the Conditional/Unconditional CNP Theorems (Ch 47) are the A2/A4 anchors to integrate; the unconditional $\chi_{ZFS^+}(\mathbb{R}^2)\ge5$ is citable.

REMAINS OPEN (the bottleneck, as the book frames it):
- A $\chi\ge5$ (let alone $\ge6$) unit-distance graph in the plane. The book documents 25 years of effort that produced only $\chi=4$ UDGs of ever-smaller size and ever-higher girth, never $\chi\ge5$. (de Grey later cracked $\chi=5$ with 1581 vertices, NOT via the O'Donnell flexible-embedding route but via a rigid spindle-based construction - the OPPOSITE of the "flexibility" heuristic O'Donnell hoped for; this is a key post-book lesson worth flagging to the SYNTHESIZER: rigidity, not flexibility, delivered $\chi=5$.)
- $\eta_5,\eta_6,\eta_7$ (smallest $k$-point sets of chromatic number $k$), Open Problem 5.4. The bottleneck is $\eta_6$: a $\ge6$-chromatic point set is exactly a $\ge6$-chromatic embeddable UDG.
- Whether $1 \in X_6$ (Ch 7): decides the UPPER bound (6 vs 7). Unexplored by the project; a computational target.
- Whether $\chi(\mathbb{R}^n)$ is defined "in the absolute" (in ZF), Open AC Problem 46.14: the A4 frontier.
