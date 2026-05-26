# Architecture 2 dossier: measurable / spectral lower bounds on $\chi_m(\mathbb{R}^2)$, 1981 to present

**Sub-corpus**: lower-bound work on the *measurable* chromatic number $\chi_m(\mathbb{R}^2)$ of the unit-distance graph on the Euclidean plane, from Falconer's 1981 paper through autocorrelation, density-of-$1$-avoiding-set, Fourier / LP and SDP, and spectral (generalized Lovász $\vartheta$) work to the present.

**Scope**: lower-bound side of $\chi_m$ only. Combinatorial / SAT work belongs to Architecture 1 (see `arch1_sat_lineage.md`). Set-theoretic / Borel-chromatic work belongs to Architecture 4. Cross-architecture results (e.g., density-avoiding-set bounds that are *fractional* in spirit) are cited where they touch the measurable lineage. Hyperbolic-plane and higher-dimensional results are cited because their methods are the load-bearing technology for any future $\chi_m(\mathbb{R}^2) \geq 6$ attempt.

**Methodology caveat**: several primary PDFs (Falconer 1981 J.C.T.A., Bachoc-Nebe-Oliveira Filho-Vallentin slides, Steinhardt unpublished notes) returned binary-only on WebFetch. Where I have not read the primary text I have flagged claims as "secondary source" and given the chain of citation. The Falconer chapter in Soifer's *Mathematical Coloring Book* (Chapter 9, "Measurable Chromatic Number of the Plane", Springer 2009) is the canonical re-exposition; I cite it for proof-structure claims I cannot verify against the 1981 J.C.T.A. text directly.

**Headline correction up front**: a careful reading of the literature finds that **$\chi_m(\mathbb{R}^2) \geq 5$ (Falconer 1981) remains the best known measurable lower bound for the Euclidean plane**. The widely-cited "$\chi_m \geq 6$" results are: (a) the *hyperbolic* plane $\mathbb{H}^2(d)$ for large $d$ (DeCorte-Golubev 2018), and (b) restricted-region variants on $\mathbb{R}^2$ where color classes are convex tiles of bounded-away-from-zero area (Coulson; Townsend; Woodall). The project atlas claim "$\chi_m \geq 6$ in recent work" applies to those restricted settings, not to the canonical $\chi_m(\mathbb{R}^2)$. See section 4 and the discrepancy log.

---

## 1. Definitional crispness

Let $G = G_{\mathbb{R}^2}$ be the unit-distance graph on $\mathbb{R}^2$: vertex set $\mathbb{R}^2$, edges between points at Euclidean distance exactly $1$.

**$\chi(\mathbb{R}^2)$ (chromatic number)**: smallest $k$ such that there is a function $c: \mathbb{R}^2 \to \{1, \ldots, k\}$ with $c(x) \neq c(y)$ whenever $\|x - y\| = 1$. No measurability assumption on $c$. Existence of $c$ for finite $k$ requires either the axiom of choice or the de Bruijn-Erdős compactness theorem (which itself needs the ultrafilter lemma / weak choice).

**$\chi_m(\mathbb{R}^2)$ (measurable chromatic number)**: smallest $k$ such that there is a coloring $c: \mathbb{R}^2 \to \{1, \ldots, k\}$ with $c(x) \neq c(y)$ whenever $\|x-y\| = 1$ *and* each color class $c^{-1}(i)$ is **Lebesgue measurable**. Introduced by Falconer (1981, J. Combin. Theory A 31, 184-189). The measurability requirement is on the preimage of each color, not on $c$ as a map.

**$\chi_B(\mathbb{R}^2)$ (Borel chromatic number)**: smallest $k$ such that the color classes are *Borel*. Borel sets are strictly contained in Lebesgue-measurable sets, so $\chi_B \geq \chi_m$. The Borel notion is the natural one for descriptive set theory (color classes have a definable structure, not just a measurable one).

**Hierarchy**:

$$
\chi(\mathbb{R}^2) \;\leq\; \chi_m(\mathbb{R}^2) \;\leq\; \chi_B(\mathbb{R}^2).
$$

Strictness of any of these inclusions is open. Under AC, $\chi(\mathbb{R}^2)$ is well-defined and is between $5$ and $7$; without AC, $\chi$ can be infinite (Shelah-Soifer phenomenon) while $\chi_m$ stays bounded if a measurable choice can be made. The Shelah-Soifer 2003 example (a graph with $\chi = 2$ in ZFC but $\chi = \aleph_0$ in ZF + LM) shows the gap between $\chi$ and $\chi_m$ is not a technicality but a foundational object. ([Shelah-Soifer 2003, JCT-A 103](https://shelah.logic.at/files/95439/E33.pdf))

**Why measurability matters technically**: a measurable color class $A \subset \mathbb{R}^2$ has a density profile. If $\mu(A \cap [-R, R]^2) / (2R)^2 \to \delta$ as $R \to \infty$ along a Følner sequence, then $\delta$ is well-defined for measurable sets and is the object the Falconer / Croft / Oliveira Filho-Vallentin / Ambrus-Matolcsi lineage studies. The classical $\chi$ has no such structure; AC-witnesses to a coloring need not have any density behavior.

---

## 2. Chronology

| Year | Reference | Headline | Method |
|------|-----------|----------|--------|
| 1981 | Falconer, *J. Combin. Theory A* 31, 184-189 | $\chi_m(\mathbb{R}^2) \geq 5$ | autocorrelation / density of 1-avoiding sets |
| 1989 | Székely-Wormald, *Discrete Math.* | bounds on $\chi_m(\mathbb{R}^n)$ for $n \geq 2$ | combinatorial / density |
| 2002 | Coulson, *Discrete Math.* (tile-coloring) | $\geq 6$ for *convex-tile* colorings | combinatorial / topological |
| 2003 | Shelah-Soifer, *JCT-A* 103 | $\chi$ depends on choice axioms | descriptive set theory |
| 2009 | Bachoc-Nebe-Oliveira Filho-Vallentin, *GAFA* (arXiv:0801.1059) | new $\chi_m(\mathbb{R}^n)$ bounds, $n = 10$ to $24$ | generalized Lovász $\vartheta$ / SDP / Jacobi polynomials |
| 2010 | Oliveira Filho-Vallentin, *J. Eur. Math. Soc.* 12 (arXiv:0808.1822) | $m_1(\mathbb{R}^n)$ upper bounds, $n = 2$ to $24$; $\chi_m(\mathbb{R}^n) \geq 1/m_1$ | Fourier analysis + linear programming |
| 2015 | Keleti-Matolcsi-Oliveira Filho-Ruzsa, *DCG* (arXiv:1501.00168) | $m_1(\mathbb{R}^2) \leq 0.258795$ | LP + harmonic analysis |
| 2018 | Bukh, *DCG* (preceded by Steinhardt's spectral note) | density / measurable coloring of odd-distance graph | spectral / autocorrelation |
| 2018 | DeCorte-Golubev, *DCG* (arXiv:1708.01081) | $\chi_m(\mathbb{H}^2(d)) \geq 6$ for $d$ large (e.g., $d \geq 12$) | spectral / Lovász $\vartheta$ on noncompact group |
| 2018 | DeCorte-Oliveira Filho-Vallentin (density estimates via higher-order correlations, arXiv:1809.05453) | refined $m_1(\mathbb{R}^n)$ bounds | $k$-point correlation LP hierarchy |
| 2023 | Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki, *Math. Programming* (arXiv:2207.14179) | $m_1(\mathbb{R}^2) < 1/4$ (specifically $\leq 0.2470$), settling Erdős's conjecture | LP + beam-search 23-point configuration |
| 2024 | Ruhland (arXiv:2408.10076) | no improvement to *lower* bound on $m_1(\mathbb{R}^2)$ | analytic + LP, negative result |

Notes:
- Falconer 1981 J.C.T.A. (volume 31, pp. 184-189) is the canonical reference. The exposition in Soifer, *The Mathematical Coloring Book* (Springer 2009), Chapter 9 ("Measurable Chromatic Number of the Plane"), contains a clarified re-proof written by Falconer specifically for the book.
- The Bachoc et al. 2009 paper's bounds are tight in dimensions $10$ to $24$ but do not improve $\chi_m(\mathbb{R}^2)$ beyond $5$: the SDP bound at $n = 2$ degenerates / gives only $\chi_m \geq 5$. ([arXiv:0801.1059](https://arxiv.org/abs/0801.1059); slides at [Fields Institute](https://www.fields.utoronto.ca/talk-media/1/85/89/slides.pdf))
- "$m_1(\mathbb{R}^2)$" denotes the supremum of upper densities of measurable subsets of $\mathbb{R}^2$ avoiding distance $1$. The relation $\chi_m(\mathbb{R}^d) \cdot m_1(\mathbb{R}^d) \geq 1$ is the structural bridge: if a $k$-coloring exists, the largest color class has density $\geq 1/k$ and avoids distance $1$, so $m_1 \geq 1/k$, equivalently $\chi_m \geq 1/m_1$. Therefore $m_1(\mathbb{R}^2) \leq 0.2470$ would give $\chi_m(\mathbb{R}^2) \geq 1/0.2470 > 4.05$, so $\geq 5$, recovering Falconer's bound by a different route.
- **No $\chi_m(\mathbb{R}^2) \geq 6$ has been published as of May 2026.** To force $\chi_m \geq 6$ via the $m_1$ bridge one would need $m_1(\mathbb{R}^2) < 1/5 = 0.2000$, a substantial drop from the current 0.247. This is consistent with section 4.

---

## 3. Falconer's proof of $\chi_m(\mathbb{R}^2) \geq 5$ at the lemma level

The proof in Falconer (1981) is *not* the autocorrelation / Fourier argument that the Bachoc / Oliveira Filho-Vallentin lineage later developed; that lineage *reproves* Falconer's bound by density-of-1-avoiding-set arguments. Falconer's original argument is geometric-measure-theoretic and relies on a Lebesgue-density / category-style argument.

Falconer's structure (as re-exposed in *Mathematical Coloring Book*, Ch. 9, written by Falconer for Soifer):

**Step 1: structure of measurable color classes.** Suppose for contradiction $\mathbb{R}^2$ is properly $4$-colored with measurable color classes $A_1, A_2, A_3, A_4$. At least one $A_i$ has positive upper density; call it $A$.

**Step 2: Lebesgue density lemma applied to $A$.** Almost every point of $A$ is a Lebesgue density point of $A$. By a covering argument, there is a small ball $B(x_0, \varepsilon)$ in which $A$ has Lebesgue density arbitrarily close to $1$ at every point of $A \cap B(x_0, \varepsilon)$.

**Step 3: realize a forbidden configuration in the high-density set.** Falconer constructs a small finite configuration $S \subset \mathbb{R}^2$ (a generalization of the Moser spindle / triangular point configurations) such that any $4$-coloring of $S$ forces a unit-distance monochromatic pair. The configuration is mobile under rotation and translation. Because $A$ has high density in $B(x_0, \varepsilon)$, the measure of rotations / translations that place a copy of $S$ inside the high-density region of $A$ is positive.

**Step 4: contradiction by intersection of mobile configurations.** A measure-theoretic intersection argument shows that some translate / rotate of $S$ must have all its points in $A$ simultaneously, producing the forbidden monochromatic unit pair.

The load-bearing technical ingredient is the **Lebesgue density theorem applied to the color classes**, combined with a **rigid finite configuration that is $\chi \geq 5$ as an abstract graph in $\mathbb{R}^2$**. Falconer's clever step is that he does not need the configuration to be a UDG (in the de Grey 2018 sense, where every edge is a unit distance); he needs a finite Moser-spindle-like graph that, *combined with the density*, forces a contradiction. This is why his 1981 argument got $\chi_m \geq 5$ thirty-seven years before de Grey 2018 got $\chi \geq 5$ for the un-measurable problem.

**Mechanism summary**: Falconer extracts a *local* density-$1$ region from a hypothetical $4$-coloring and uses the rigidity of small Euclidean configurations to force a monochromatic unit pair *within* that region. The density theorem replaces the SAT-driven combinatorial search of Architecture 1.

**Obstruction to extending to $\chi_m \geq 6$**: Step 3 needs a *rigid finite configuration that is at least $5$-chromatic as a unit-distance graph in the plane*. As of 2026, no such configuration is known: the unit-distance subgraph of any finite set in $\mathbb{R}^2$ has $\chi \leq 5$ in all explored cases (no $\chi \geq 6$ UDG known; see Architecture 1 dossier section 3). Falconer's machine therefore stalls at $\chi_m \geq 5$ for the same combinatorial reason that Architecture 1 stalls at $\chi \geq 5$: the missing object is a $6$-chromatic finite UDG, and the measure-theoretic argument cannot manufacture one. This is the cross-architecture coupling worth flagging for LEARNINGS.

---

## 4. The "$\chi_m \geq 6$" claim and what it actually says

The user's prompt suggested $\chi_m(\mathbb{R}^2) \geq 6$ has been proved recently. Careful checking of the literature finds this is a conflation of three distinct results:

1. **DeCorte-Golubev 2018, $\chi_m(\mathbb{H}^2(d)) \geq 6$ for $d$ large enough.** The hyperbolic plane, edge distance $d$. Method: spectral / Lovász $\vartheta$ for a noncompact Cayley-graph-like setting on $\mathrm{PSL}_2(\mathbb{R})$. The result has $d \geq 12$ sufficiency (per the abstract). It does *not* transfer to $\mathbb{R}^2$ because the hyperbolic plane has exponential volume growth and the spectral bounds exploit this. The Euclidean plane has polynomial growth and a different spectral obstruction landscape. ([arXiv:1708.01081](https://arxiv.org/abs/1708.01081); *DCG* 2019)

2. **Coulson 2002 (and earlier Woodall-Townsend lineage): $\chi \geq 6$ for *convex-tile* colorings of $\mathbb{R}^2$.** If color classes are required to be unions of convex polygons of area $\geq \varepsilon$ for some $\varepsilon > 0$, then at least $6$ colors are needed. This is much more restrictive than Lebesgue-measurable. ([Coulson, *Discrete Math.* 2002](https://www.semanticscholar.org/paper/On-the-chromatic-number-of-plane-tilings-Coulson/df4462f7611c43548ed9e36c4dc11b1cfd08cffe); cited in Polymath16 wiki and Soifer's *Mathematical Coloring Book*.)

3. **Tile-based / map-type colorings: $\chi \geq 6$ in the Woodall-Townsend chain.** Townsend 1981 and Woodall 1973 prove tile-based colorings cannot achieve $5$. The 2025 paper "On the chromatic number of the plane for map-type colorings" ([arXiv:2502.01958](https://arxiv.org/abs/2502.01958)) extends this kind of result.

**None of (1), (2), (3) imply $\chi_m(\mathbb{R}^2) \geq 6$.** The measurable category is strictly broader than convex-tile or map-type; a measurable color class can be highly fractal, non-tiling, and density-irregular at the macro scale while still being measurable. The Coulson / Townsend chain operates in a strictly stronger model. The DeCorte-Golubev result lives on a different manifold.

**Best known measurable lower bound on $\mathbb{R}^2$ as of 2026-05**: $\chi_m(\mathbb{R}^2) \geq 5$ (Falconer 1981), reconfirmed by the Oliveira Filho-Vallentin LP bound, by the Keleti-Matolcsi-Oliveira Filho-Ruzsa 2015 density bound (which gives $\chi_m \geq 4$ directly via $m_1 \leq 0.2588$; combined with Falconer reaches $5$), and by Ambrus et al. 2023 $m_1 \leq 0.2470$ (which gives $\chi_m \geq 1/0.2470 \approx 4.05$, so $\geq 5$).

**Room left between bound and conjecture**: assuming $\chi(\mathbb{R}^2) \in \{5, 6, 7\}$ and $\chi_m \geq \chi$, the room for improvement on $\chi_m$ is "prove $\chi_m \geq 6$ or $\chi_m \geq 7$" with no consensus on which is correct. If $\chi_m = \chi$, then closing the $\chi_m$ side also closes $\chi$. There is no published evidence that $\chi_m > \chi$.

---

## 5. What is tractable computationally

The measurable lineage is dominated by **continuous optimization** (LP, SDP, harmonic analysis) rather than the discrete SAT machinery of Architecture 1. Concrete experiments for this project:

### E2.1: reproduce the Oliveira Filho-Vallentin LP bound for $m_1(\mathbb{R}^2)$

**Scope**: implement the LP from arXiv:0808.1822, §3-4, for $n = 2$ on a discretized grid. Solve via `scipy.optimize.linprog` or `cvxpy`. Target output: $m_1(\mathbb{R}^2) \leq 0.2688$ (the OFV bound) as a sanity check on the implementation. Then push to dim $n = 2,3,4$ to verify the $m_1(\mathbb{R}^n) \to 0$ exponential decay.

**Why tractable**: the LP is finite-dimensional after truncation of the Fourier basis; truncation parameter $N \sim 30$ is enough for the 0.27-range bound. Should run in minutes.

**Output**: certificate of $m_1$ bound, plus the optimal Fourier multipliers as data for E2.4.

### E2.2: reproduce Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki $m_1 < 1/4$ at the small-configuration level

**Scope**: take the 23-point configuration from arXiv:2207.14179 (the paper provides explicit coordinates). For each point, write the linear constraint $f(x) + f(x + v_i) \leq 1$ where $\{v_i\}$ are the configuration's unit-distance edges. Solve the LP; verify the bound $\leq 0.2470$. Then iterate the beam search to see whether a $24$- or $25$-point configuration gives a tighter bound; targeted at $0.24$ as a stretch goal.

**Why tractable**: the LP is small (a few hundred variables after Fourier truncation). The beam search is the expensive part; one or two iterations on top of the published 23-point config is feasible in CPU-hours, not CPU-days.

**Pitfall**: the AC-MV-Z paper's beam search ran for months. Replicating the search at scale is not tractable; replicating the *verification* of the published certificate is.

### E2.3: spectral / Lovász $\vartheta$ on a finite UDG approximation

**Scope**: take the 509-vertex Parts graph (the smallest known 5-chromatic UDG, Architecture 1 dossier section 2) and compute its Lovász $\vartheta$ number numerically using `cvxpy` + an SDP solver (Mosek, SCS, or CSDP). Compare to its chromatic number $\chi = 5$ and fractional chromatic $\chi_f \geq 4$ (from Matolcsi-Ruzsa-Varga-Zsámboki, arXiv:2311.10069). Theoretical relations: $\vartheta(\overline{G}) \leq \chi_f(G) \leq \chi(G)$. Verify the chain.

**Why tractable**: $\vartheta$ on a 509-vertex graph is a $509 \times 509$ SDP, well within the reach of `cvxpy` + SCS on a laptop (memory dominates; expect ~5 minutes).

**Output**: the empirical $\vartheta$ for the Parts graph, plus the dual SDP witness, which is a labeled-orthonormal-representation in $\mathbb{R}^{509}$. This is a finite proxy for the infinite SDP of Bachoc-Nebe-Oliveira Filho-Vallentin.

### E2.4: discretized Falconer density argument

**Scope**: pick a discretized torus $T_N = (\mathbb{Z}/N\mathbb{Z})^2$ with $N = 1000$ scaled so that the unit distance corresponds to ~30 lattice steps. Search by simulated annealing for measurable colorings of $T_N$ with 4 colors that avoid the unit-distance edges. Falconer's argument predicts the largest such "color class" has density $\leq m_1 \approx 0.247$. Verify empirically that no $4$-coloring exists with all classes of density $\geq 0.25$.

**Why tractable**: discretized search on a $10^6$-cell torus is GPU-friendly. The discretization introduces lattice-rigidity effects (the discrete unit-distance graph is not isometric to the continuous one), so the result is illustrative, not a proof.

**Output**: an empirical map of "how close to $1/k$ can a $k$-color density classification on $T_N$ get without a unit-distance edge". This visualizes the density bound Falconer's proof relies on.

### E2.5 (stretch): SDP for $\chi_m$ on a sphere

**Scope**: implement the Bachoc-Nebe-Oliveira Filho-Vallentin SDP for $\chi_m(S^{n-1})$ at $n = 3, 4, 5$ using Jacobi polynomials. Target reproducing the published bound at $n = 3$ ($\chi_m(S^2) \geq 4$ on the unit sphere) as a baseline. This is the natural sphere counterpart to E2.3 and tests the orthogonal-polynomial reduction.

**Why ambitious**: the SDP is infinite-dimensional pre-truncation; the truncation level for $n = 3$ is degree $\sim 30$ Jacobi polynomials. Implementation is several days of work.

---

## 6. Wrong-approach-detector check

The Architecture 2 detectors are: (a) the $\mathbb{R}^1$ trivial control ($\chi(\mathbb{R}) = \chi_m(\mathbb{R}) = 2$; any method blind to the 2D rotation group $O(2)$ would also constrain $\mathbb{R}^1$, where the bound is $2$ and cannot be improved); (b) the $L^\infty$-norm plane ($\chi(L^\infty) = 4$, Chilakamarri; any method that uses only norm-blind structure should fail on $L^\infty$); (c) the $\mathbb{Q}^2$ detector is partly exempt because measure-zero, but the *measurable* analog on $\mathbb{Q}^2$ is degenerate (rationals have Lebesgue measure zero, so measurable colorings of $\mathbb{R}^2$ restricted to $\mathbb{Q}^2$ are not meaningful; the project atlas correctly flags this).

Method-by-method:

- **Falconer 1981 (autocorrelation / density + rigid configuration)**. Uses (i) Lebesgue density (a 2D fact in essential way: density at a point in $\mathbb{R}^2$ is a 2D measure of $B(x, r) \cap A$, not a 1D measure), and (ii) a rigid Euclidean configuration $S$ that exists in $\mathbb{R}^2$ but not in $\mathbb{R}^1$ (it requires non-collinear points). **$\mathbb{R}^1$ detector passes**: the method does not apply on $\mathbb{R}^1$ because no rigid 4-chromatic UDG configuration exists in dimension 1 (in $\mathbb{R}^1$, the unit-distance graph is bipartite). The 2D rotation group enters via the mobility of $S$ under $O(2)$. **$L^\infty$ detector passes**: the Lebesgue-density argument is norm-agnostic but the configuration $S$ uses Euclidean rigidity (specific Euclidean distances $1, \sqrt{3}$, etc.); on $L^\infty$, the corresponding configuration has different unit-distance edges. **Pass.**

- **Oliveira Filho-Vallentin 2010 (Fourier + LP)**. The LP is over functions $f: \mathbb{R}^2 \to \mathbb{R}$ satisfying $f(x) + f(x+v) \leq 1$ for $\|v\| = 1$. The Fourier transform is on $\mathbb{R}^2$ as a 2D group with rotation invariance built in (the optimal $f$ is rotation-invariant by symmetry of the constraint). **$\mathbb{R}^1$ detector**: in dimension 1 the same LP gives $m_1(\mathbb{R}) \leq 1/2$ (the $\sin / \cos$ structure of 1D Fourier), recovering $\chi_m(\mathbb{R}) \geq 2$ correctly. The method gives the *right* answer on $\mathbb{R}^1$ rather than overshooting. **Pass.** **$L^\infty$ detector**: the LP is identical, but the unit-distance edge set in $L^\infty$ is different (a sphere in $L^\infty$ is an $\ell^\infty$ unit cube boundary, very different from the Euclidean circle). Running the same LP on $L^\infty$ would give a different bound and would recover $\chi_m(L^\infty) \geq 4$ correctly (Chilakamarri shows this). **Pass.**

- **Bachoc-Nebe-Oliveira Filho-Vallentin 2009 (Lovász $\vartheta$ on $S^{n-1}$, then transfer to $\mathbb{R}^n$)**. The SDP uses spherical harmonics on $S^{n-1}$, which are intrinsically 2D for $n = 3$ and higher. **$\mathbb{R}^1$ detector**: on $\mathbb{R}^1$, the sphere $S^0$ is two points, the harmonic-analysis machinery degenerates trivially, and the bound becomes $\chi_m \geq 2$, recovering the right answer. **Pass.** **$L^\infty$ detector**: the Jacobi-polynomial structure is Euclidean; on $L^\infty$ the analogous spherical harmonics on the $L^\infty$ ball boundary do not exist in the standard form, so the method does not transfer. **Pass.**

- **Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023 ($m_1 < 1/4$)**. The 23-point configuration includes points at Euclidean distances $1$, $\sqrt{3}$, $\sqrt{7/3}$, etc. (Moser-spindle-style with refinements). **$\mathbb{R}^1$ detector**: the configuration is intrinsically 2D (non-collinear), so the LP would degenerate to the trivial $m_1(\mathbb{R}) \leq 1/2$ bound. **Pass.** **$L^\infty$ detector**: the configuration's edges become different distances in $L^\infty$, breaking the LP constraints' structure. The Euclidean specificity is essential. **Pass.**

- **DeCorte-Golubev 2018 (hyperbolic plane $\chi_m \geq 6$)**. Uses Plancherel / harmonic analysis on the noncompact symmetric space $\mathrm{PSL}_2(\mathbb{R}) / \mathrm{SO}(2)$. The exponential volume growth of $\mathbb{H}^2$ is the load-bearing fact. **$\mathbb{R}^1$ detector**: not applicable, the method is intrinsically 2D. **$L^\infty$ detector**: not applicable, this is a curved-space method. **$\mathbb{R}^2$ analog**: this is the question, see section 4. The method does not directly transfer to $\mathbb{R}^2$ because $\mathbb{R}^2$ has polynomial volume growth, so the spectral gap behaves differently.

**Result of detector pass**: every method in the measurable lineage engages with the 2D rotation group and with Euclidean rigidity (the configuration $S$ in Falconer, the Jacobi polynomials in BNOFV, the LP constraints' $\|v\| = 1$ in OFV). No method overshoots to $\mathbb{R}^1$. The lineage is structurally sound. The cross-architecture coupling is that all current methods *also* stall at $\chi_m \geq 5$ for the same combinatorial reason Architecture 1 stalls at $\chi \geq 5$: no $6$-chromatic UDG in $\mathbb{R}^2$ is known, and the measurable arguments inherit this barrier.

---

## 7. Discrepancy log

Items where my findings refine or correct the project's atlas:

1. **Atlas (`README.md` line 44, line 75) says "$\chi_m \geq 6$ in recent work" without citation.** Best read of the literature is that this is a **misattribution**: $\chi_m(\mathbb{R}^2) \geq 5$ (Falconer 1981) is still the state of the art; the $\geq 6$ results live in the hyperbolic plane (DeCorte-Golubev 2018) and in restricted-region (convex-tile) variants (Coulson 2002). Suggest updating the atlas variants table to "**$\chi_m \geq 5$ (Falconer 1981)**; no improvement on the Euclidean plane as of 2026" and adding the hyperbolic and tile-coloring results as separate rows.

2. **Atlas does not mention $m_1(\mathbb{R}^2)$.** The density-of-1-avoiding-set quantity is the central technical object of the modern measurable lineage. Suggest adding to the variants table: "$m_1(\mathbb{R}^2) \leq 0.2470$ (Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023); $\chi_m \geq 1/m_1 \geq 5$".

3. **Atlas does not mention the Lovász-$\vartheta$ / Bachoc-Nebe-Oliveira Filho-Vallentin SDP framework.** This is the load-bearing technology of *spectral* methods on $\chi_m$, and it lives at the Arch 2 / Arch 3 boundary (the SDP is the same object whose LP relaxation gives $\chi_f$). Suggest a footnote in Architecture 2 acknowledging the BNOFV framework, with a cross-reference to the (future) Architecture 3 dossier.

4. **Atlas line 44 says "$\chi_f \geq 3.6\ldots$ (Cranston-Rabern)".** Superseded: Matolcsi-Ruzsa-Varga-Zsámboki 2023 (arXiv:2311.10069) proved $\chi_f(\mathbb{R}^2) \geq 4$. Same group as the AC-MV-Z $m_1 < 1/4$ paper. This is an Architecture 3 update but worth noting here because the fractional and measurable lineages converge in the OFV LP framework.

5. **Cross-coupling with Architecture 1**: the obstruction to extending Falconer's $\chi_m \geq 5$ to $\chi_m \geq 6$ is, at the lemma level, **the same** as the obstruction to Architecture 1 extending de Grey's $\chi \geq 5$ to $\chi \geq 6$. Both require a finite $6$-chromatic configuration in $\mathbb{R}^2$ (rigid for Falconer; UDG for de Grey). This coupling should be noted in LEARNINGS as a cross-architectural fact.

---

## 8. What this enables / what remains open

**Enables (downstream agents)**:

- **BUILDER**: the highest-value experiment is **E2.3 (Lovász $\vartheta$ on the 509-vertex Parts graph)**. It is implementable in a day with `cvxpy` + SCS, gives a concrete numerical bound that is comparable across architectures (Arch 1, 2, 3), and produces a labeled-orthonormal-representation that is a finite analog of the BNOFV infinite SDP witness. **E2.2 (verify the AC-MV-Z 23-point LP)** is the next-most valuable, both because it is a tractable certificate-verification task and because the 23-point configuration is the right starting point for further beam search.

- **VERIFIER**: any claimed $\chi_m(\mathbb{R}^2) \geq 6$ result should be checked against (a) the $m_1(\mathbb{R}^2)$ bridge: does it imply $m_1 < 1/5$, contradicting current $m_1$ lower-bound experiments? (b) the $\mathbb{R}^1$ detector: does the proof degenerate trivially on the line? (c) the cross-architecture coupling: does it implicitly construct a 6-chromatic finite UDG in $\mathbb{R}^2$? If so, that is an Architecture 1 breakthrough independently and should be checked by SAT.

- **ADVERSARY**: the most promising point of attack is the **gap between Falconer-style and Architecture-1-style arguments**. The fact that both stall at $5$ for the same combinatorial reason (no $6$-chromatic UDG in $\mathbb{R}^2$) suggests either (a) the actual value is $\chi(\mathbb{R}^2) = \chi_m(\mathbb{R}^2) = 5$, in which case both architectures are at the natural bound, or (b) there is a $6$-chromatic UDG hiding in some number field not yet explored. The adversarial question: are there choice-axiom-dependent reasons why $\chi$ and $\chi_m$ would differ in the plane? Shelah-Soifer says they *can* differ in artificial graphs; does the $\mathbb{R}^2$ structure permit such a difference?

- **SYNTHESIZER**: integrate items 1, 2, 4 of the discrepancy log into `docs/research_atlas/README.md`. Add a LEARNINGS entry on the cross-architectural coupling (point 5 of discrepancy log).

**Remains open**:

- $\chi_m(\mathbb{R}^2) = 5, 6,$ or $7$? No published improvement on $\chi_m \geq 5$ since Falconer 1981.
- $\chi_m(\mathbb{R}^2) = \chi(\mathbb{R}^2)$? No published example of a strict inequality on the plane.
- Can the BNOFV SDP / OFV LP framework be sharpened at $n = 2$ to give $\chi_m \geq 6$? The SDP at $n = 2$ has been computed and gives only $\chi_m \geq 5$ (per BNOFV slides at Fields Institute); whether a higher-order SDP hierarchy (Lasserre / sums-of-squares) could break the barrier is open.
- Can higher-order correlation methods (DeCorte-Oliveira Filho-Vallentin 2018, arXiv:1809.05453) push $m_1(\mathbb{R}^2)$ below $1/5$? This would force $\chi_m \geq 6$ via the bridge. Current value $0.247$ is far from $0.200$.
- Does $\chi_B(\mathbb{R}^2) > \chi_m(\mathbb{R}^2)$? Open. Descriptive-set-theoretic methods (Architecture 4) might separate them.

**Flag for follow-up SURVEYOR sessions**:

- (a) **Falconer 1981 primary text**: PDF was not directly readable; a careful re-exposition of the original proof from the J.C.T.A. text (not just the Soifer book chapter) would confirm the four-step structure in section 3.
- (b) **Bachoc-Nebe-Oliveira Filho-Vallentin slides + GAFA paper full text**: their explicit bounds at $n = 2$ are quoted as "only $5$" in secondary literature; the primary numerical values and degeneracy mechanism need verification.
- (c) **Architecture 3 dossier**: the fractional / Lovász-$\vartheta$ side overlaps Architecture 2 here in the OFV / BNOFV framework. A unified Arch 2 / Arch 3 dossier on "linear programming and SDP bounds for $\chi_m, \chi_f$ on $\mathbb{R}^2$" would consolidate.
- (d) **Whether DeCorte-Golubev's hyperbolic method has any Euclidean analog**: the noncompact-symmetric-space machinery is potentially transferable to $\mathbb{R}^2$ as a Cayley graph of the Euclidean motion group $\mathbb{R}^2 \rtimes O(2)$. Has this been attempted? Worth a focused search.

---

## References (verified by direct fetch or quoted from secondary)

| Tag | Reference | Verified |
|-----|-----------|----------|
| Falconer 1981 | K.J. Falconer, *The realization of distances in measurable subsets covering $\mathbb{R}^n$*, J. Combin. Theory A 31 (1981), 184-189 | secondary (Soifer Ch. 9; Polymath16 wiki) |
| Soifer 2009 | A. Soifer, *The Mathematical Coloring Book*, Springer 2009, Ch. 9 "Measurable Chromatic Number of the Plane" | secondary, summary fetched |
| Shelah-Soifer 2003 | S. Shelah, A. Soifer, *Axiom of choice and chromatic number of the plane*, JCT-A 103 | abstract + Shelah preprint fetched |
| Bachoc-Nebe-Oliveira Filho-Vallentin 2009 | C. Bachoc, G. Nebe, F.M. de Oliveira Filho, F. Vallentin, *Lower bounds for measurable chromatic numbers*, GAFA / arXiv:0801.1059 | abstract + slides fetched |
| Oliveira Filho-Vallentin 2010 | F.M. de Oliveira Filho, F. Vallentin, *Fourier analysis, linear programming, and densities of distance avoiding sets in $\mathbb{R}^n$*, JEMS 12 / arXiv:0808.1822 | abstract |
| Keleti-Matolcsi-Oliveira Filho-Ruzsa 2015 | T. Keleti, M. Matolcsi, F.M. de Oliveira Filho, I.Z. Ruzsa, *Better bounds for planar sets avoiding unit distances*, DCG / arXiv:1501.00168 | abstract |
| DeCorte-Golubev 2018 | E. DeCorte, K. Golubev, *Lower bounds for the measurable chromatic number of the hyperbolic plane*, DCG / arXiv:1708.01081 | abstract fetched |
| DeCorte-Oliveira Filho-Vallentin 2018 | E. DeCorte, F.M. de Oliveira Filho, F. Vallentin, *Density estimates of 1-avoiding sets via higher order correlations*, arXiv:1809.05453 | abstract |
| Ambrus et al. 2023 | G. Ambrus, A. Csiszárik, M. Matolcsi, D. Varga, P. Zsámboki, *The density of planar sets avoiding unit distances*, Math. Programming / arXiv:2207.14179 | abstract + Rényi AI blog fetched |
| Matolcsi-Ruzsa-Varga-Zsámboki 2023 | M. Matolcsi, I.Z. Ruzsa, D. Varga, P. Zsámboki, *The fractional chromatic number of the plane is at least 4*, arXiv:2311.10069 | abstract (cross-ref Arch 3) |
| Ruhland 2024 | H. Ruhland, *No new lower bound for the density of planar sets avoiding unit distances*, arXiv:2408.10076 | summary fetched |
| Steinhardt (odd-distance) | J. Steinhardt, *On coloring the odd-distance graph*, unpublished notes, Stanford CS | binary PDF, secondary only |
| Coulson 2002 | D. Coulson, *On the chromatic number of plane tilings*, Discrete Math. | secondary (Polymath16 wiki, Soifer) |
| Polymath16 wiki | michaelnielsen.org/polymath, Hadwiger-Nelson | fetched |
| Geometry Junkyard | ics.uci.edu/~eppstein/junkyard/plane-color.html | redirect / not fetched |
| Map-type colorings 2025 | arXiv:2502.01958, *On the chromatic number of the plane for map-type colorings* | abstract |

Items marked "secondary" mean the primary text was not directly readable; reliance is on the Soifer book chapter, Polymath16 wiki, the Rényi AI blog post, or arXiv abstracts.
