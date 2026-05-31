# A2/A3 cluster notes: the SDP + harmonic-analysis lineage for distance-avoiding sets (Oliveira-Vallentin school)

> **CORRECTION (2026-05-30, two rounds; this is the settled version, reconciled with the repo's own
> LEARNINGS L35/L36). See [`11-keleti-matolcsi-oliveira-ruzsa-avoiding-sets.md`](11-keleti-matolcsi-oliveira-ruzsa-avoiding-sets.md)
> and `experiments/LEARNINGS.md` L35/L36.**
>
> The original draft cited a wrong number: it wrote "$m_1(\mathbb{R}^2) \le 0.229$" for KMOR 2016.
> That is wrong. $0.229$ ($= 0.22936$) is **Croft's LOWER bound** (a construction). KMOR 2016's
> proven **upper** bound is $m_1(\mathbb{R}^2) \le 0.258795$, which alone gives only $\chi_m \ge 4$.
>
> BUT the density route does NOT stop at KMOR. **Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023**
> (arXiv:2207.14179) proved $m_1(\mathbb{R}^2) \le 0.246894 < 1/4$ via inclusion-exclusion CONGRUENCE
> (IEC) constraints on a 23-point configuration. Since $m_1 < 1/4$ strictly, four 1-avoiding color
> classes cover density $\le 4 \times 0.2469 < 1$, so **the single-class density / LP route DOES reach
> $\chi_m(\mathbb{R}^2) \ge 5$.** This is reproduced and self-certified IN THIS REPO (LEARNINGS L35,
> L36; `experiments/fractional/e3i`, `e3j`). The 2015 KMOR $\to$ 2023 Ambrus improvement is exactly
> the IEC constraints (L36 isolates this: KMOR-frontier $0.2584$ without them, $0.2469$ with them).
>
> So the corrected ledger:
> - Density route reaches $\chi_m(\mathbb{R}^2) \ge 5$ (Ambrus 2023, $m_1 \le 0.2469 < 1/4$; repo L35/L36). KMOR 2016 ($0.2588$) was the just-short predecessor ($\chi_m \ge 4$).
> - $\chi_m(\mathbb{R}^2) \ge 5$ is ALSO Falconer 1981, by a separate (earlier, pre-density-bound) measurable argument.
> - $\chi_m(\mathbb{R}^2) \ge 6$ is UNREACHABLE by single-class density: Croft's floor $m_1 \ge 0.22936 > 1/5 = 0.2$ forces $1/m_1 \le 4.36 < 5$, so the route caps at $\ge 5$ (conjectured true value $m_1 = 1/4$). This negative result stands.
> - DOV 2022's real contribution: the EXACT completely-positive characterization and the convergent Lasserre hierarchy.
>
> Wherever the body below says "$m_1 \le 0.229 \Rightarrow \chi_m \ge 5$ (KMOR)", the conclusion
> ($\chi_m \ge 5$ by density) is RIGHT but the number/citation is wrong: it is $m_1 \le 0.2469$
> (Ambrus 2023), not $0.229$ (KMOR). An intermediate edit pass that concluded "density only reaches 4"
> was itself wrong (it stopped at KMOR and missed Ambrus 2023 / the repo's L36); ignore any such phrasing.

SURVEYOR notes for the semidefinite-programming / harmonic-analysis route to the measurable chromatic number $\chi_m(\mathbb{R}^2)$ and the density of distance-avoiding sets. This cluster extends Architecture A2 (measurable / spectral) and A3 (fractional / Lovasz $\vartheta$), and it is the lineage the project previously flagged as a GAP: it is the research-strength machinery that actually pushes $\chi_m$ and the avoiding-set density $m_1$ toward sharp values.

This note EXTENDS `sources/notes/04-fractional-graph-theory-and-bachoc-spectral.md` (Bachoc-DeCorte-Oliveira-Vallentin 2014, the operator spectral bound). Do not re-read 04 here; this note assumes it. The relation in one line: note 04 is the 2-point (single-operator) Hoffman/Lovasz bound; this note is the conic-cone characterization (DeCorte-Oliveira-Vallentin 2022) plus the SDP-hierarchy refinements (Boolean-quadratic / Lasserre) that close the gap between the 2-point bound and the true parameter.

Five texts:

1. E. DeCorte, F.M. de Oliveira Filho, F. Vallentin, "Complete positivity and distance-avoiding sets," Math. Program. Ser. A 191 (2022) 487-558. THE central paper. (72pp.)
2. F.M. de Oliveira Filho, "Semidefinite programming upper bounds for packing problems," lecture notes (2016). The unifying framework: Delsarte / Cohn-Elkies / Lovasz $\vartheta$ are one object.
3. F. Vallentin, "Lecture notes: semidefinite programs and harmonic analysis," arXiv:0809.2017 (2008). Pedagogical: $\vartheta$ for distance graphs, positive Hilbert-Schmidt kernels, Peter-Weyl, Bochner.
4. F. Vallentin, "Spectral bounds and SDP hierarchies for geometric packing," slides (Simons Institute, 2014). The roadmap: 2-point to $t$-point Lasserre, the $n=2$ Bessel reduction.
5. J. Briet, F.M. de Oliveira Filho, F. Vallentin, "The PSD Grothendieck problem with rank constraint," arXiv:0910.5765 (2010). The SDP-rounding toolkit (tangential).

Source PDFs: `sources/papers/`. Extracted text: `sources/_extracted/`.

---

## Executive summary: what this cluster gives A2/A3 (and how it fills the prior gap)

1. The operative quantity is $m_1(\mathbb{R}^n)$ = max density of a Lebesgue-measurable set in $\mathbb{R}^n$ avoiding distance 1. The bridge to coloring is $m_1(\mathbb{R}^n)\,\chi_m(\mathbb{R}^n)\ge 1$, so $\chi_m(\mathbb{R}^n)\ge\lceil 1/m_1\rceil$. These methods compute UPPER bounds on $m_1$, hence LOWER bounds on $\chi_m$.
2. DeCorte-Oliveira-Vallentin 2022 (DOV) prove the EXACT characterization (Thm 1.1 / Thm 5.1): replacing the cone of positive-type functions by the cone of COMPLETELY POSITIVE functions makes the convex program equal $m_1(\mathbb{R}^n)$ (and $m_0(S^{n-1})$) exactly, not just an upper bound. This is the infinite-dimensional analogue of "$\alpha(G)=\vartheta(G,\mathrm{CP})$" (Motzkin-Straus / de Klerk-Pasechnik).
3. The gap this fills: note 04's bound is the 2-point ($\vartheta'$, single convolution operator) bound. DOV give the complete cone of constraints (completely-positive functions) and a concrete, finite, computable family (Boolean-quadratic-polytope / subgraph constraints) that systematically strengthens it toward the TRUE value of $m_1$. The SAME point-set / inclusion-exclusion idea, pushed to congruence constraints on a 23-point configuration by Ambrus et al. 2023, is what finally drives $m_1(\mathbb{R}^2)$ below $1/4$ and crosses $\chi_m(\mathbb{R}^2) \ge 5$ (see item 4). On SPHERES the analogous bounds cross higher integers, the cluster's live frontier.
4. [SETTLED, reconciled with repo L35/L36] Planar density upper bounds, in order: 2-point LP $0.2683$ (Oliveira-Vallentin 2010); KMOR 2016 Thm 3.1 $m_1 \le 0.258795$ (Moser-spindle subgraph + 6-point inclusion-exclusion, DOV reinterpret as BQP facets) which gives only $\chi_m \ge 4$ (just short, $0.2588 > 1/4$); and Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 $m_1 \le 0.246894 < 1/4$ (inclusion-exclusion CONGRUENCE constraints), which gives $\chi_m(\mathbb{R}^2) \ge 5$. So the single-class density route DOES reach 5; the repo reproduces and self-certifies the 2023 bound (LEARNINGS L35, L36). The figure $0.229$ ($=0.22936$) that appears below is Croft's LOWER bound (a construction floor), not an upper bound. DOV 2022's Table 2 improves $n=3,\dots,8$ but not $n=2$; the planar crossing is Ambrus 2023, not DOV.
5. The harmonic-analysis mechanism: rotation ($O(n)$) invariance lets one radialize the optimization variable. A radial positive-type function is, by Schoenberg/Bochner, a nonnegative-measure mixture of the Bessel symbol $\Omega_n(t\|x\|)$, where $\Omega_n(t)=\Gamma(n/2)(2/t)^{(n-2)/2}J_{(n-2)/2}(t)$. For $n=2$ the operative object is $\Omega_2(t)=J_0(t)$, the Bessel function of order 0. The forbidden-distance constraint $f(x)=0$ at $\|x\|=1$ becomes $\int_0^\infty\Omega_n(t)\,d\alpha(t)=0$, an LP/SDP in the measure $\alpha$ on $[0,\infty)$.
6. The SDP HIERARCHY (Vallentin 2014 slides; DOV Sects 7-10): the 2-point bound is the first level $\mathrm{las}_1=\vartheta'$. Adding constraints from finitely many points (the BQP$(U)$ / Lasserre $t$-point cone) gives $\mathrm{las}_1\ge\mathrm{las}_2\ge\dots\to\alpha$, a convergent hierarchy. Each level is a finite SDP. Computationally feasible levels are $t=2$ plus a handful of $k$-point ($k\le7$) facet constraints.
7. DOV Sect 10 proves the hierarchy CONVERGES to $m_1$ (recovering Bukh's computability of $m_1(\mathbb{R}^n)$ to any precision) and reproduces Bukh's asymptotic $m_{d_1,\dots,d_N}(\mathbb{R}^n)\to m_1(\mathbb{R}^n)^N$ as the distances space out. This is a theoretical, not yet practical, route to arbitrary precision.
8. Oliveira 2016 is the unification: Delsarte's LP bound for binary codes, Delsarte-Goethals-Seidel for spherical codes, and Cohn-Elkies for sphere packing are all the dual $\vartheta'$ specialized via Krawtchouk (Hamming), Jacobi/Gegenbauer (sphere), Bessel (Euclidean) harmonics. Same skeleton; the harmonics differ by the symmetry group.
9. Vallentin 2008 supplies the functional-analytic foundation that note 04 used: positive Hilbert-Schmidt kernels, Mercer spectral decomposition, Peter-Weyl decomposition $C(V)=\bigoplus H_k$, Bochner block-diagonalization of invariant kernels. This is why the infinite SDP reduces to a small block SDP.
10. Detector status: the bound enters Euclidean structure through the rotation-invariant optimal measure and the Bessel symbol; it correctly gives $\chi_m(\mathbb{R}^1)=2$ (degenerate Bessel), depends on the norm/dimension (so it sees $\ell^2$ vs $\ell^\infty$), and is legitimately blind to $\mathbb{Q}^2$ (measure zero, the A2 exemption). Detector-clean. The standing caution: this is a MEASURABLE bound, so it caps out at whatever $1/m_1$ is; it cannot by itself reach the non-measurable integer $\chi(\mathbb{R}^2)$.

---

## The SDP route to $\chi_m(\mathbb{R}^2)$: state of the art and the path to $\ge 6$

### (a) Best current bound and the obstacle to pushing higher

State of the art, two dimensions:

- 2-point / single-operator (LP, note 04 / Oliveira-Vallentin 2010): $m_1(\mathbb{R}^2)\le 0.2683$, giving $\chi_m(\mathbb{R}^2)\ge\lceil1/0.2683\rceil=4$. This is the weak Bessel bound.
- KMOR 2016 (Thm 3.1, DOV ref [22]): $m_1(\mathbb{R}^2)\le 0.258795$, hence $\chi_m(\mathbb{R}^2)\ge\lceil1/0.258795\rceil = 4$. Moser-spindle subgraph + 6-point inclusion-exclusion inequalities, which DOV (Sect 7) reinterpret as BQP$(U)$ facets. This was JUST SHORT of $1/4$, so it gave only $\chi_m \ge 4$.
- Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 (arXiv:2207.14179): $m_1(\mathbb{R}^2)\le 0.246894 < 1/4$, hence $\chi_m(\mathbb{R}^2) \ge 5$. The new ingredient over KMOR is inclusion-exclusion CONGRUENCE (IEC) constraints on a 23-point configuration $X_{23}$ (averaging atom densities over $O(2)$-congruent sub-configurations). REPRODUCED AND SELF-CERTIFIED in this repo (LEARNINGS L35, L36; `experiments/fractional/e3i`, `e3j`): the repo's own primal+dual LP gives $m_1 \le 0.246894$, and L36 isolates the 2015$\to$2023 gain as exactly the IEC constraints (KMOR-frontier $0.2584$ without them). This is the planar density crossing into $\chi_m \ge 5$.
- DOV 2022 Table 2 improves $m_1(\mathbb{R}^n)$ for $n=3,\dots,8$ ($n=4$: $\chi_m\,10\to11$; $n=5$: $15\to17$; $n=6$: $21\to23$). DOV do NOT report a new $n=2$ row. Their 2D contribution is conceptual (the complete-positivity EXACTNESS theorem + BQP facet theory that explains why the point-set constraints work).

The obstacle to $\chi_m(\mathbb{R}^2)\ge6$ [SETTLED]. Reaching $\ge6$ by this route would require $m_1(\mathbb{R}^2) < 1/5 = 0.2$. The best LOWER bound (Croft-type avoiding set, density $0.22936$, note 04 Sect 3.6 / note 11) is a hard floor ABOVE $1/5$: no upper-bound improvement can push $m_1$ below $0.22936$, so $1/m_1$ can never exceed $4.36 < 5$. Therefore the single-class density route caps at $\chi_m \ge 5$ (already attained, Ambrus 2023) and CANNOT reach $\ge 6$. (The conjectured true value is $m_1(\mathbb{R}^2) = 1/4$; Ambrus et al. also report a record fractional $\chi_{gf} = 3.9954$, never $>4$, consistent with the conjecture $\chi_f(\mathbb{R}^2)=4$.) Reaching $\chi_m \ge 6$ needs a fundamentally different obstruction (multi-distance / multi-color LP, or a Fourier argument on a partition rather than one class), or the Arch-1 rigid 5-chromatic object (repo L33/L36).

Relation to note 04's wall [SETTLED]. The number $4.36 = 1/0.22936$ is the reciprocal of the avoiding-set density LOWER bound, i.e. the optimistic CEILING on what single-class density can ever prove. Since $4.36 \in (4,5)$, the integer it certifies is $\chi_m \ge 5$ (any proven $m_1 < 1/4$ suffices, and Ambrus 2023's $0.2469$ achieves it). It cannot certify $6$ ($4.36 < 5$). So:

CONCLUSION (state of the art) [SETTLED, repo-reconciled]: the single-class density / LP route gives $\chi_m(\mathbb{R}^2)\ge 5$ (Ambrus 2023, $m_1 \le 0.2469 < 1/4$; reproduced repo L35/L36), and it CANNOT reach $\ge6$ (Croft floor $0.22936 > 1/5$). KMOR 2016 ($0.2588$) was the just-short predecessor ($\ge 4$). $\chi_m(\mathbb{R}^2) \ge 5$ is ALSO Falconer 1981 by a separate earlier measurable argument. The $\ge6$ frontier needs a multi-class / multi-distance refinement (DOV Sect 10 supports it in principle) for which no $\mathbb{R}^2$ computation yet crosses 6.

### (b) How this complements (does not replace) the A1 search for a $\chi\ge6$ embeddable graph

These are orthogonal attacks on different numbers:

- A1 targets the ORDINARY (non-measurable, integer) $\chi(\mathbb{R}^2)$ via finite unit-distance graphs and SAT. The open bottleneck is a $\chi\ge6$ UDG that embeds in the plane.
- This cluster targets the MEASURABLE $\chi_m(\mathbb{R}^2)$ via a global density/Fourier argument. It never builds a graph; it certifies a dual SDP feasible solution (a positive-type function with a sign condition).

They complement in three ways. First, $\chi(\mathbb{R}^2)\ge\chi_m(\mathbb{R}^2)$ always, so any measurable lower bound is also a lower bound on $\chi$. If the SDP route ever crossed $\chi_m\ge6$ it would settle $\chi(\mathbb{R}^2)\ge6$ WITHOUT a graph. Second, the BQP/subgraph constraints are SEEDED by finite graphs (the Moser spindle, regular simplices, the 600-cell on spheres): A1's BUILDER output (good rigid finite UDGs) is exactly the constraint source for the A2/A3 SDP. Third [SETTLED]: there are now THREE lower bounds of 5 by disjoint methods, de Grey 2018 (integer $\chi\ge5$, combinatorial), Falconer 1981 (measurable $\chi_m\ge5$), and the density/LP route (Ambrus 2023, $m_1<1/4$, reproduced repo L35/L36). The density route's $\chi_m\ge5$ is the project's L35/L36 result.

What this route does NOT do [SETTLED]: it does not produce a $\chi\ge6$ embeddable graph, and (per (a)) it cannot reach $\chi_m\ge6$ by single-class density (Croft floor $> 1/5$). It DOES reach $\chi_m\ge5$ (Ambrus 2023). So it is a parallel ledger that has reached 5 and is capped there; it is not a substitute for the A1 bottleneck at 6. Its distinctive deliverables: the EXACT completely-positive characterization, the convergent hierarchy, the high-dimensional ($n \ge 3$, sphere) bounds, and the proof that the density engine cannot reach 6 in 2D.

### (c) What a BUILDER / VERIFIER could compute now

Concrete, runnable computations, in increasing order of effort:

1. REPRODUCE the 2-point bound (LP, half a page of cvxpy / scipy). Variable: a finite measure $\alpha$ on a grid of $[0,T]$. Objective: maximize $\alpha([0,\infty))$ (the primal density proxy) or solve the dual (39)/(46) of DOV. Constraints: $\int\Omega_2(t)\,d\alpha(t)=0$ (forbidden distance 1, with $\Omega_2=J_0$), plus the PSD $2\times2$ block from DOV (38). Expected: $m_1(\mathbb{R}^2)\le0.268$, $\chi_m\ge4$. This validates the pipeline and matches Oliveira-Vallentin 2010. The repo's L35/L36 LP crossing is essentially this with a coarse discretization; this gives the analytic-quality version.

2. ADD point-set constraints to cross $1/4$ (the repo has DONE this; this item is now calibration, not frontier). KMOR's Moser-spindle BQP facet gives $m_1 \le 0.2588$ ($\chi_m \ge 4$, just short). To CROSS $1/4$ you need Ambrus 2023's inclusion-exclusion CONGRUENCE (IEC) constraints on the 23-point $X_{23}$, which the repo already implements and self-certifies ($m_1 \le 0.246894 < 1/4$, $\chi_m \ge 5$; `experiments/fractional/e3i`, `e3j`, LEARNINGS L35/L36). Anyone reproducing from scratch: take $U = X_{23}$ (exact coords in $\mathbb{Q}(\sqrt3,\sqrt{11})$ in `_cache/ambrus_23point_config.json`), enumerate $O(2)$-congruent subset pairs, add the IEC equalities, solve. The KMOR-only ($0.2588$) and Ambrus-IEC ($0.2469$) values bracket exactly where the congruence constraints bite.

3. VERIFY a dual certificate rigorously. The repo already does this for the Ambrus bound (L36: cvxpy/HiGHS primal + its own dual, gap $\sim 10^{-16}$, plus an independent SCS re-solve and exact sympy edge verification). The general recipe (DOV Sect 9.3 / KMOR): solve the discretized SDP in high precision, perturb the floating dual to a rational feasible point, bound the quality loss via eigenvalue estimates. A VERIFIER can re-run the repo's `e3j` self-certification or the DOV checker.

4. EXPLORE the $\ge6$ frontier (research-grade, the route is provably capped at 5 in 2D). The single-class density bound cannot reach 6 (Croft floor $> 1/5$). The many-distance LP (DOV (45)/(46), $m_{d_1,\dots,d_m}\to m_1^m$ by Bukh) constrains a multi-distance graph, not $\chi_m(\mathbb{R}^2)$ directly. The genuinely open computation is a MULTI-CLASS measurable LP (partition $\mathbb{R}^2$ into $k$ color classes, bound the joint autocorrelation), not yet formalized as a finite SDP in these texts. Flag for ADVERSARY: confirm no single-class density bound can give $\chi_m(\mathbb{R}^2)\ge6$ (it cannot: the density-$0.22936$ Croft tile forces $1/m_1 \le 4.36 < 5$).

Choice of basis matters (Vallentin 2014 slides): use the normalized Gegenbauer/Bessel basis $|\mu_k^{-1}|L_k^{n/2-1}(2\pi t)$, NOT monomials, or the SDP conditions blow up even at low degree. For $n=2$ the relevant transform is the Hankel/Bessel-$J_0$ transform.

---

## Text 1: DeCorte-Oliveira-Vallentin 2022, "Complete positivity and distance-avoiding sets" -- structured notes

### Sect 1: the two problems and the main theorem

Two prototypical parameters:
- (P1) $m_0(S^{n-1})$: max surface measure of a subset of $S^{n-1}$ with no orthogonal pairs (Witsenhausen). Kalai's double-cap conjecture says two antipodal $\pi/4$-caps are optimal; open for all $n\ge2$.
- (P2) $m_1(\mathbb{R}^n)$: max density of a 1-avoiding set. Erdos conjectured $m_1(\mathbb{R}^2)<1/4$ (open). L. Moser's conjecture $m_1(\mathbb{R}^n)\le1/2^n$ was disproved [34]; the truth resembles Kalai's double-cap behavior.

Prior bounds (the cone of POSITIVE-type functions):
- Bachoc-Nebe-Oliveira-Vallentin 2009: problem (1), an upper bound for $m_0(S^{n-1})$, the spherical analogue of Delsarte.
- Oliveira-Vallentin 2010: problem (2), an upper bound for $m_1(\mathbb{R}^n)$, the Euclidean analogue of Cohn-Elkies. Variable: continuous $f:\mathbb{R}^n\to\mathbb{R}$ of positive type with $f(0)=1$, $f(x)=0$ at $\|x\|=1$; objective the mean value $M(f)$. By Bochner this is an infinite LP.

The central result (Thm 1.1): require $f$ to be of COMPLETELY POSITIVE type (for every finite $U$, the matrix $(f(x-y))_{x,y\in U}$ is completely positive, i.e. a conic sum of rank-1 nonnegative matrices) and the optimal value becomes EXACTLY $m_1(\mathbb{R}^n)$ (resp. $m_0(S^{n-1})$). Significance: (i) it gives a COMPLETE source of strengthening constraints (every finite-$U$ complete-positivity / copositivity inequality is valid and they suffice); (ii) the exact convex characterization yields analytic results (Bukh's many-distance asymptotic and the Turing-computability of $m_1$).

The general engine (Thm 5.1): for a locally independent topological graph $G$ on a compact space, with an inner-regular Borel measure, $\vartheta(G,\mathrm{CP}(V))=\alpha_\omega(G)$, the measurable independence number. Infinite analogue of "$\alpha(G)=\vartheta(G,\mathrm{CP})$" (Motzkin-Straus, de Klerk-Pasechnik).

### Sect 2: locally independent graphs

The right infinite setting. A $D$-distance graph $G(V,D)$ has $x\sim y$ iff $d(x,y)\in D$; independent sets are $D$-avoiding sets. Four regimes by (compactness of $V$) x ($0$ isolated from $D$ or not): kissing ($S^{n-1}$, $D=(0,\pi/3)$, finite $\alpha$); Witsenhausen ($S^{n-1}$, $D=\{\pi/2\}$, positive-measure independent sets, $\alpha_\omega=m_0$); sphere packing ($\mathbb{R}^n$, $D=(0,1)$, discrete); 1-avoiding ($\mathbb{R}^n$, $D=\{1\}$, the unit-distance graph, $\alpha_{\bar\delta}=m_1$).

Def 2.1: $G$ is locally independent if every compact independent set sits inside an OPEN independent set. Thm 2.2: $V$ metrizable + $E$ closed $\Rightarrow$ locally independent. This is the topological hypothesis that makes Urysohn's lemma (hence the feasible-kernel construction) work. The 1-avoiding and Witsenhausen graphs qualify (0 isolated from $D$).

### Sect 3: the conic program for the independence number

The finite template (3): $\max\langle J,A\rangle$ s.t. $\mathrm{tr}\,A=1$, $A(x,y)=0$ on edges, $A\in K(V)$. With $K=\mathrm{PSD}$ this is Lovasz $\vartheta$; with $K=\mathrm{PSD}\cap\mathrm{NN}$ it is Schrijver $\vartheta'$; with $K=\mathrm{CP}$ (completely positive) it equals $\alpha(G)$ exactly. Chain (4): $\vartheta\ge\vartheta'\ge\vartheta(\cdot,\mathrm{CP})=\alpha$. The last equality is the Motzkin-Straus fact (de Klerk-Pasechnik), proved in one paragraph: a CP feasible $A=\sum\alpha_if_i\otimes f_i^*$ has some $f_1$ whose support is independent and $\langle J,A\rangle\le|{\rm supp}\,f_1|\le\alpha$.

Infinite extension (6): replace trace by integral over the diagonal (Mercer makes them equal for positive kernels); $C(V)=\mathrm{cl\,cone}\{f\otimes f^*:f\in L^2(V),f\ge0\}$ is the cone of completely positive KERNELS. Thm 3.1: locally independent $G$ on compact Hausdorff $V$, inner-regular $\omega$, $0<\alpha_\omega<\infty$ $\Rightarrow\vartheta(G,C(V))\ge\alpha_\omega$. Proof via Urysohn (build a continuous $f$ that is 1 on a near-optimal compact independent set, 0 outside an open independent neighborhood; then $A=\|f\|^{-2}f\otimes f^*$ is CP-feasible).

### Sect 4: the completely positive and copositive cones on compact spaces

The dual cone is $C^*(V)$, the COPOSITIVE kernels: $\langle Z,f\otimes f^*\rangle\ge0$ for all $f\ge0$. Bipolar theorem: $(C^*)^*=C$. Thm 4.1: $C$ and $C^*$ are closed under (i) restriction to positive-measure subsets and (ii) Hadamard product with $g\otimes g^*$, $g\ge0$. Sect 4.1 develops the averaging operation $A*P$ over an $\omega$-partition $P$ (a step-kernel / graph-limit construction); Thm 4.2: averaging preserves both $C$ and $C^*$. This is the technical machinery for the Choquet decomposition used in Sect 5.

### Sect 5: when is the CP formulation exact

Thm 5.1 (the heart). Reverse inequality $\vartheta(G,C(V))\le\alpha_\omega(G)$ under extra hypotheses (vertex-transitive under a compact group with right-invariant metric, plus regularity). Proof sketch: an optimal CP kernel $A$ is, by Choquet's theorem, a "continuous convex combination" $\int f\otimes f^*\,d\nu(f\otimes f^*)$ of rank-1 nonnegative kernels. The constraints force, for $\nu$-almost every $f$, that the set of DENSITY POINTS of $\mathrm{supp}\,f$ is independent (the measure-zero non-density-point set is what one removes; Lemma 5.6 does the density-point argument with the $2/3$-density / Lebesgue-density estimate). Then one such support gives a measurable independent set of measure $\ge\langle J,A\rangle$. Corollary: when the optimum is attained, $\alpha_\omega$ is ATTAINED by a measurable set (reproves DeCorte-Pikhurko for $G(S^{n-1},\{\theta\})$, $n\ge3$).

### Sect 6: distance graphs on Euclidean space (THE Bessel reduction)

Extends Thm 5.1 to $\mathbb{R}^n$ via tori. Upper density $\bar\delta(X)$ and independence density $\alpha_{\bar\delta}(G(\mathbb{R}^n,D))=m_1$-type parameter. Sect 6.1: periodic sets = independent sets on the torus $\mathbb{R}^n/L\mathbb{Z}^n$; Lemma 6.1 (the torus graph is locally independent for $L>2\sup D$) and Lemma 6.2 ($\limsup_L\alpha_{\rm vol}(G(\mathbb{R}^n/L\mathbb{Z}^n,D))/{\rm vol}=\alpha_{\bar\delta}(G(\mathbb{R}^n,D))$, periodic densities approximate the true density). Sect 6.2: harmonic analysis on $\mathbb{R}^n$, positive-type via Bochner ($\hat f\ge0$).

### Sects 7-9: the computable strengthenings (where the numbers come from)

- Sect 7: the BOOLEAN-QUADRATIC cone BQC$(V)$ and polytope BQP$(V)=\mathrm{conv}\{f\otimes f^*:f:V\to\{0,1\}\}$. Adding BQP$(U)$-constraints for finite $U$ strengthens $\vartheta(G,\mathrm{PSD})$. Thm 7.4: a new class of facets $Q_G$ of BQC, indexed by connected $\alpha$-critical graphs $G$ (generalizing Padberg's clique facets). KMOR's inclusion-exclusion inequalities are exactly such facets; this is why the Moser-spindle constraint works.
- Sect 8: better $m_0(S^{n-1})$ bounds. Table 1: $n=3$, $0.30153$ (improving Zhao's $0.308$); $n=4,\dots,8$ improving Witsenhausen's $1/n$. Lower bounds from two opposite caps.
- Sect 9: better $m_1(\mathbb{R}^n)$ bounds, $n=3,\dots,8$ (Table 2). Sect 9.1 (RADIAL functions): $O(n)$-invariance lets one radialize; Schoenberg's formula gives $f(x)=\int_0^\infty\Omega_n(t\|x\|)\,d\alpha(t)$ with $\Omega_n(t)=\Gamma(n/2)(2/t)^{(n-2)/2}J_{(n-2)/2}(t)$, $\Omega_n(0)=1$ (eq. 37). Sect 9.2: the primal SDP (38) in the measure $\alpha$ (constraint $\int\Omega_n\,d\alpha=0$ is the forbidden-distance-1 condition) and its dual (39). Sect 9.3: discretize $t$, solve, then verify by perturbation to a rational feasible solution (KMOR recipe).

Table 2 numbers (previous $\to$ new): $\bar\alpha_\delta$ upper bounds $n{=}3$: $0.1645\to0.1533$ ($\chi_m\,7\to7$); $n{=}4$: $0.1001\to0.0986$ ($10\to11$, 600-cell); $n{=}5$: $0.0678\to0.0624$ ($15\to17$, 600-cell); $n{=}6$: $0.0478\to0.0450$ ($21\to23$, 600-cell); $n{=}7$: $0.0277\to0.0261$ ($37\to39$, $E_8$ kissing); $n{=}8$: $0.0196\to0.0191$ ($52\to53$, $E_8$ + 8-simplex). NO new $n=2$ row: planar $m_1\le0.258795$ stands at KMOR 2016 (Thm 3.1).

### Sect 10: many distances and computability

Thick constraints (Lemma 10.1): $C(\mathbb{R}^n)$ characterized by $\sum_{x,y\in U}Z(x,y)\int_{B(x,\delta)}\int_{B(y,\delta)}f\ge0$ for all finite $U$, copositive $Z$, $\delta\le m(U)/2$. Lemma 10.2: the radialized $r(t)$ vanishes at infinity and is nonnegative for large $t$ (Riemann-Lebesgue + Bessel decay; FALSE for $n=1$, which is the detector signal). A countable family of thick constraints over rational point sets gives a sequence of primal LPs (45) whose optima DECREASE to $m_1(\mathbb{R}^n)$ (recovers Bukh's algorithm and the asymptotic $m_{d_1,\dots,d_N}\to m_1^N$). This is the convergence guarantee: the hierarchy is COMPLETE, so $m_1$ is computable to any precision in principle.

---

## Text 2: Oliveira 2016, "SDP upper bounds for packing problems" -- structured notes

The unifying lecture notes. Thesis: Delsarte (binary codes), Delsarte-Goethals-Seidel (spherical codes), Cohn-Elkies (sphere packing) are ONE bound, the dual Schrijver $\vartheta'$, specialized through different harmonics.

- Sect 3-5: packing $\leftrightarrow$ independence number of a packing graph; $\vartheta'$ via SDP (3) and its dual (4); $\alpha\le\vartheta'$.
- Sect 6: Hamming cube. Symmetrize over $\mathrm{Iso}(H_n)$; invariant PSD kernels are $\sum_k f_k K_k^n(|x-y|)$ with $f_k\ge0$ (Krawtchouk polynomials, Thm 3). The SDP collapses to Delsarte's LP (6).
- Sect 7: the infinite-graph $\vartheta'$ (7) via positive continuous kernels and Bochner's finite-PSD characterization. Any feasible dual gives $\alpha\le\lambda$.
- Sect 8: sphere $A(n,\theta)$. Symmetrize over $O(n)$; Schoenberg (Thm 5): invariant positive kernels are $\sum_k f_kP_k^n(x\cdot y)$, $f_k\ge0$, $P_k^n$ Jacobi/Gegenbauer ($\alpha=\beta=(n-3)/2$). LP (10). Example: $\tau_3\le13$ at degree 13.
- Sects 9-10: compactification of $\mathbb{R}^n$ via periodic packings + tori; the Cohn-Elkies bound (15) recovered as $\vartheta'$ on the torus (Thm 6). The forbidden region is now NONCOMPACT, so sampling/LP is replaced by sum-of-squares.
- Sects 11-13: SOS = PSD (Thm 7); how to turn the infinite LP into a finite SDP via SOS multipliers; applied to spherical codes (Sect 12) and sphere packing (Sect 13).

Relevance to HN: the EXACT same skeleton runs for $G(\mathbb{R}^n,\{1\})$ (the unit-distance graph) with the Bessel symbol $\Omega_n$ in place of Cohn-Elkies's role; the forbidden set $\{1\}$ (measure zero) instead of $(0,1)$. This is the bridge between the sphere-packing LP and the distance-avoiding LP. The note is the cleanest single source for "why $\vartheta'$, Delsarte, Cohn-Elkies, and the $m_1$ bound are the same object."

---

## Text 3: Vallentin 2008, "Semidefinite programs and harmonic analysis" -- structured notes

Pedagogical foundation (the functional analysis note 04 and DOV assume).

- Sect 2.1-2.2: distance graphs $G(V,I)$; finite graphs are distance graphs (shortest-path metric); Lovasz $\vartheta$ in both primal (2) and dual (3) form; Schrijver $\vartheta'$ by sign-strengthening.
- Sect 2.3: POSITIVE HILBERT-SCHMIDT KERNELS. A symmetric continuous $K$ is positive iff every finite extracted matrix is PSD. Mercer spectral decomposition $K=\sum_k\lambda_k e_k\otimes e_k$ (nonneg eigenvalues, only accumulation point 0, finite multiplicities). This is the infinite-PSD object.
- Sect 2.4: $\vartheta$ for infinite graphs (6), via the dual form; Thm 2.7 ($\vartheta\ge\alpha$) by the test-function argument (any feasible kernel bounds any stable set). $\vartheta\ge\vartheta'\ge\alpha$.
- Sect 2.5: SYMMETRY. Group-average a feasible kernel over $\mathrm{Aut}(V)$ via the invariant (Haar) integral; for $SO(2)$ it is $\frac1{2\pi}\int_0^{2\pi}d\theta$. The optimum is unchanged by restricting to invariant kernels. THIS is the move that makes the infinite SDP tractable.
- Sect 3: HARMONIC ANALYSIS. Peter-Weyl (Thm 3.5): $C(V)=\bigoplus_k H_k$, each $H_k$ a finite-dim isotypic block. Bochner (Thm 3.6): every $\mathrm{Aut}(V)$-invariant positive kernel is $K(x,y)=\sum_k\langle F_k,Z_k(x,y)\rangle$ with $F_k$ PSD of size $m_k\times m_k$. So optimizing over invariant kernels = optimizing over small PSD blocks $F_k$ = a BLOCK-DIAGONAL SDP. This is the entire "exploit symmetry" engine.
- Sect 4: Boolean harmonics ($H_k$ = span of weight-$k$ characters, Krawtchouk; multiplicity 1, so blocks are scalars $\Rightarrow$ Delsarte LP).
- Sect 5: Spherical harmonics ($H_k$ = degree-$k$ harmonic polynomials, dimension $\binom{n+k-1}{k}-\binom{n+k-3}{k-2}$; addition formula gives the Gegenbauer/Jacobi zonal kernel $\Rightarrow$ Delsarte-Goethals-Seidel LP). The Euclidean case ($\mathbb{R}^n\rtimes SO(n)$) is the noncompact analogue, where the irreducibles are indexed by $a>0$ and the zonal function is the Bessel symbol $J_{s-r}(2\pi a\rho)$ (this is spelled out in the Vallentin 2014 slides below).

Takeaway: Vallentin 2008 is the "how the block reduction works" reference; for $\mathbb{R}^2$ the block index is the continuous radial frequency $a$ and the basis matrices involve $J_0$ (and higher $J_k$ for the off-diagonal angular modes).

---

## Text 4: Vallentin 2014 slides, "Spectral bounds and SDP hierarchies for geometric packing" -- roadmap

High-level structure (sparse, image-heavy; extracted skeleton):

- Frame: independent sets in CAYLEY graphs $\mathrm{Cayley}(G,\Sigma)$ over a group $G$ with connection set $\Sigma$. Three instances: $\mathbb{F}_2^n$ (Hamming, error-correcting codes, finite); $SO(n)$ (spherical codes, compact); $SO(n)\ltimes\mathbb{R}^n$ (body packing, locally compact). The unit-distance graph is the locally-compact Euclidean instance.
- Hilbert's 18th problem (densest packing) as the motivating target, "solve by computer using an SOS proof system." de Laat-Oliveira-Vallentin 2012 sphere-packing upper bounds table ($n=4,\dots,9$, e.g. $n=4$: new $0.130587$ vs Cohn-Elkies $0.13126$).
- The LASSERRE HIERARCHY: $\alpha(G)=\max\sum_v x_v$ over a polynomial-optimization formulation; the $t$-th step $\mathrm{las}_t(G)$ uses a moment matrix $M_t(y)$ indexed by independent sets of size $\le t$; $\vartheta'=\mathrm{las}_1\ge\mathrm{las}_2\ge\dots\ge\mathrm{las}_\alpha=\alpha$. The $n$-point bound uses $y_{I\cup J}$ with $|I\cup J|\le n$. Generalized to TOPOLOGICAL packing graphs (de Laat-Vallentin): primal over Borel measures $\lambda$ on $I_{2t}$, dual over copositive kernels $K$.
- 2-point (spectral) bound for Cayley graphs: $\mathrm{las}_1=\inf\{f(e):f$ positive type, $f(x)\le0$ for $x\notin\Sigma\}$, parametrized via Gelfand-Raikov (positive-type functions = matrix coefficients of unitary reps) and the Plancherel/Fourier transform $\hat f(\pi)$ over $\hat G$.
- THE $n=2$ EUCLIDEAN SPECIALIZATION (the operative slide). The relevant irreducible reps of $\mathbb{R}^2\rtimes SO(2)$ are indexed by $a>0$ acting on $L^2(S^1)$; in polar coordinates $x=\rho(\cos\theta,\sin\theta)$, $A=$ rotation by $\alpha$,
  $$f(\rho,\theta,\alpha)=\int_0^\infty\sum_{r,s\in\mathbb{Z}}\hat f(a)_{r,s}\,i^{s-r}e^{-i(s\alpha+(r-s)\theta)}J_{s-r}(2\pi a\rho)\,a\,da.$$
  Setting $\hat f(a)_{r,s}=\sum_{k=0}^d f_{r,s;k}a^{2k}e^{-\pi a^2}$ and requiring $e^{\pi a^2}\sum\hat f(a)_{r,s}y_ry_s$ to be a sum of squares forces $f$ positive type, turning the infinite SDP into a finite SOS-SDP. The diagonal $r=s$ angular mode carries $J_0$; this is the Bessel object for the plane.
- Rigorous computation notes: use the Gegenbauer/Bessel basis $|\mu_k^{-1}|L_k^{n/2-1}(2\pi t)$ (monomials fail), SDPA-GMP at 256 bits, degree up to $d\approx51$, perturb to rational, bound quality loss by eigenvalue/condition-number estimates, custom C++ SOS-SDP library. Tetrahedra still open (needs more automation of the harmonic-analysis side).

Use for the project: this is the explicit recipe for the $n=2$ SOS-SDP, including the exact Bessel expansion and the numerical hygiene. A BUILDER setting up the planar bound should follow this basis/precision guidance.

---

## Text 5: Briet-Oliveira-Vallentin 2010, "PSD Grothendieck problem with rank constraint" -- structured notes (tangential)

Main object: $\mathrm{SDP}_n(A)=\max\sum_{ij}A_{ij}x_i\cdot x_j$ over $x_i\in S^{n-1}$ (rank-$n$ constrained PSD Grothendieck). $n=1$ is classical Grothendieck / MAX CUT.

Main theorem (Thm 1): a randomized polynomial-time algorithm achieves the ratio
$$\gamma(n)=\frac2n\left(\frac{\Gamma((n+1)/2)}{\Gamma(n/2)}\right)^2=1-\Theta(1/n),$$
with $\gamma(1)=2/\pi$, $\gamma(2)=\pi/4$, $\gamma(3)=8/(3\pi)$; optimal under the unique games conjecture (Thm 3). Thm 2 sharpens the classical $2/\pi$ Grothendieck constant to $2/(\pi\gamma(m))$.

Mechanism (Sect 2): solve the relaxation $\mathrm{SDP}_\infty$ (vectors in $S^\infty$), then ROUND by a Gaussian random projection $x_i=Xu_i/\|Xu_i\|$ with $X_{ij}\sim N(0,1)$ (Goemans-Williamson for $n=1$); the analysis uses the WISHART distribution and FUNCTIONS OF POSITIVE TYPE on $S^{m-1}$ (Schoenberg).

Relevance to HN (honest assessment: tangential). This is the ROUNDING / relaxation-quality side of the SDP toolkit, not a distance-avoiding-set bound. Two connection points: (i) it is the same Schoenberg positive-type-on-spheres machinery used in Vallentin 2008 Sect 5 and DOV Sect 8, so it shares the harmonic-analysis vocabulary; (ii) it quantifies how much is lost in passing from an infinite-dimensional SDP relaxation ($S^\infty$) to a finite-rank ($S^{n-1}$) feasible solution, which is conceptually the gap between the SDP bound and a realizable geometric configuration. It does NOT directly give a $\chi_m$ or $m_1$ bound, and a BUILDER would not run it to attack HN. Included for completeness of the cluster's toolkit; the load-bearing texts are 1-4.

---

## Mapping to the four architectures

- A2 (measurable / spectral): PRIMARY HOME. The whole cluster computes upper bounds on $m_1(\mathbb{R}^n)$ and $m_0(S^{n-1})$, hence lower bounds on the MEASURABLE chromatic number $\chi_m$. DOV Sect 9 explicitly states "$\alpha_{\bar\delta}\,\chi_m\ge1$" and reads off $\chi_m$ lower bounds. This is the Falconer/autocorrelation lineage in its sharpest conic form.
- A3 (fractional / Lovasz $\vartheta$): SHARED HOME. The conic program (3)/(6) IS the Lovasz $\vartheta$ family; the CP cone is the exact ($\alpha$) end, PSD is the loose ($\vartheta$) end, $\vartheta'$ and BQP/Lasserre sit between. The Vallentin 2014 Lasserre hierarchy is pure A3. The reciprocal $1/m_1$ coincides numerically with the $\chi_f$ ceiling $\approx4.36$ from note 04, so the A3 fractional and the A2 single-class measurable relaxations bottom out at the SAME number.
- A1 (combinatorial / UDG): CONSUMER and SEED. Finite UDGs (Moser spindle, simplices, 600-cell, $E_8$ kissing) are the SOURCE of the BQP/subgraph constraints that strengthen the SDP. A1 BUILDER output feeds A2/A3 SDP input. A1's integer $\chi$ is a DIFFERENT (larger) number; this cluster cannot produce a $\chi\ge6$ embeddable graph.
- A4 (axiomatic): CONTACT via measurability only. Everything here is about the MEASURABLE chromatic number; the Shelah-Soifer / AC dependence is exactly the gap between $\chi_m$ (what these methods bound) and $\chi$ (what de Grey bounds). The cluster does not engage A4 directly but defines one side of the $\chi$-vs-$\chi_m$ question.

---

## Wrong-approach-detector check

Detectors: $\chi(\mathbb{Q}^2)=2$ (Woodall), $\chi(\ell^\infty$-plane$)=4$ (Chilakamarri), $\chi(\mathbb{R}^1)=2$. Recall A2 is partly exempt from the $\mathbb{Q}^2$ control (measure zero is legitimate).

- $\mathbb{Q}^2$ control. The bound is a DENSITY/measure statement: a 1-avoiding set in $\mathbb{Q}^2$ has Lebesgue measure 0 in $\mathbb{R}^2$, so the method says nothing false about $\mathbb{Q}^2$ and correctly does not imply $\chi(\mathbb{Q}^2)>2$. The A2 exemption applies: the method is allowed to be (and is) blind to the rationals. PASS (exempt).
- $\ell^\infty$-plane control. The bound depends on the unit ball through the optimal $O(n)$-invariant measure and the symbol $\hat\nu$. For the Euclidean ball this is the Bessel $\Omega_n$ (DOV eq. 37); for a polytopal ($\ell^\infty$) ball the invariant group is finite (dihedral) not $O(2)$, the radialization step (DOV Sect 9.1) does not apply, and the symbol is a different (faster/anisotropically decaying) Fourier transform. The Vallentin 2014 "$K^\circ-AK^\circ$ is an open 10-gon" slide and DOV Lemma 10.2 (which is FALSE for $n=1$ and uses Bessel decay specific to the Euclidean sphere) show the method genuinely uses Euclidean rotational rigidity. PASS. Detector hook for ADVERSARY: does the proposed bound CHANGE when the unit ball goes from circle to square? If a claimed SDP bound is stated without reference to which symbol $\hat\nu$ / which harmonics, it is suspect.
- $\mathbb{R}^1$ control. DOV Lemma 10.2 explicitly notes its nonnegativity-at-infinity conclusion is FALSE for $n=1$ (Bessel $\Omega_n$ vanishes at infinity only for $n\ge2$; the odd-interval set $\bigcup_k(2k,2k+1)$ has density $1/2$ and avoids odd distances). So the method correctly REFUSES to give a nontrivial $\mathbb{R}^1$ bound and returns $\chi_m(\mathbb{R}^1)=2$ (degenerate symbol $\cos(2\pi u)$, see note 04). The method is NOT blind to $O(n)$; the $O(n)$-invariant measure is precisely where dimension enters. PASS.

Verdict: detector-clean, same as note 04, with sharper evidence (DOV's explicit "false for $n=1$" remarks and the $\ell^\infty$ polytope slide). Standing caution [SETTLED]: this is a MEASURABLE single-class bound. The best proven planar upper bound $m_1 \le 0.246894 < 1/4$ (Ambrus 2023, repo L35/L36) gives $\chi_m(\mathbb{R}^2) \ge 5$; KMOR 2016's $0.2588$ was the just-short predecessor ($\ge 4$). $\chi_m \ge 6$ is unreachable by single-class density: the explicit Croft tile has density $0.22936 > 1/5$, so $m_1 \ge 0.22936$ and $1/m_1 \le 4.36 < 5$.

---

## Discrepancy log (vs project atlas and note 04)

- NO contradictions with project landmarks. The cluster corroborates $4\le\chi(\mathbb{R}^2)\le7$, the Moser spindle, Woodall (via measure-zero exemption). Note: de Grey 2018 is $\chi \ge 5$ (ordinary, not measurable); the measurable $\chi_m \ge 5$ is the older Falconer 1981 result. Since $\chi \ge \chi_m$, neither implies the other directly.
- [SETTLED] Re note 04's claim. Note 04 says the single-distance (2-point) Euclidean bound is "weak ($<5$)". That is RIGHT for the bare 2-point bound ($0.268$, $\chi_m \ge 4$) and for KMOR's point-set bound ($0.2588$, $\chi_m \ge 4$). But the POINT-SET method does cross $1/4$ once the IEC congruence constraints are added (Ambrus 2023, $m_1 \le 0.2469$, $\chi_m \ge 5$; repo L35/L36). So the density route DOES reach 5, just not at the 2-point level. $\chi_m(\mathbb{R}^2) \ge 5$ is independently Falconer 1981. Flag for SYNTHESIZER: the density-route $\chi_m \ge 5$ citation is Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 (= repo L35/L36), not KMOR 2016 (which fell short) and not the $0.229$ figure (Croft lower bound).
- $\chi_m(\mathbb{R}^2)\ge6$ status. The project's MEMORY notes "all 3 active architectures bottom out at one missing object: a $\chi$-6 UDG that embeds in the plane." This cluster corroborates a SEPARATE finding (already in repo L36): the MEASURABLE $\chi_m(\mathbb{R}^2)\ge6$ is blocked by the avoiding-set density floor. The floor argument: an explicit density-$0.22936$ 1-avoiding set (Croft) $\Rightarrow m_1\ge0.22936 > 1/5 \Rightarrow 1/m_1\le4.36 < 5 \Rightarrow$ the density method caps at $\chi_m \ge 5$ and cannot give 6. So $\chi_m\ge6$ via single-class density is provably out of reach, NOT merely "not yet computed."
- Numerical note [SETTLED]. DOV Table 2 is $n=3,\dots,8$ only; there is no DOV improvement to $m_1(\mathbb{R}^2)$. The best planar UPPER bound is Ambrus 2023: $m_1(\mathbb{R}^2)\le 0.246894 < 1/4$ (repo L35/L36); KMOR 2016's $0.258795$ was the prior frontier. The DOV planar contribution is the EXACTNESS theorem and facet theory, not a number. The $0.229$ figure is Croft's LOWER bound.

---

## References to follow up

Cited by these texts, central to the A2/A3 thread (read status noted):

- T. Keleti, M. Matolcsi, F.M. de Oliveira Filho, I.Z. Ruzsa, "Better bounds for planar sets avoiding unit distances," Discrete Comput. Geom. 55 (2016) 642-661. NOW READ, see note 11. Proves the UPPER bound $m_1(\mathbb{R}^2)\le 0.258795$ (Thm 3.1), giving $\chi_m \ge 4$ (just short of $1/4$). The $0.229$ figure these notes pointed to is Croft's LOWER bound, cited by KMOR.
- M. Ambrus, A. Csiszarik, M. Matolcsi, D. Varga, P. Zsamboki, "The density of planar sets avoiding unit distances" (arXiv:2207.14179, 2023). THE planar crossing: $m_1(\mathbb{R}^2) \le 0.246894 < 1/4 \Rightarrow \chi_m(\mathbb{R}^2) \ge 5$, via IEC congruence constraints on a 23-point config. NOT in this `sources/` library as a PDF, but PRESENT and worked in the repo: `experiments/fractional/_cache/main_final_version.tex`, reproduced + self-certified in LEARNINGS L35/L36 (`e3i`, `e3j`). The single most relevant A2/A3 paper for the planar bound; consider adding the PDF to `sources/papers/`.
- F.M. de Oliveira Filho, F. Vallentin, "Fourier analysis, LP, and densities of distance-avoiding sets in $\mathbb{R}^n$," JEMS 12 (2010) arXiv:0808.1822. The 2-point Euclidean bound (DOV ref [36]). Skimmed via DOV/note 04; pull for the exact $0.268$ planar 2-point value.
- B. Bukh, "Measurable sets with excluded distances," GAFA 18 (2008). The many-distance asymptotic and computability of $m_1$ (DOV ref [6]). NOT read; relevant to DOV Sect 10.
- C. Bachoc, A. Passuello, A. Thiery, "The density of sets avoiding distance 1 in Euclidean space," Discrete Comput. Geom. (2015) (DOV ref [2]). The $n=4,\dots,24$ subgraph-constraint bounds. NOT read.
- E. DeCorte, O. Pikhurko, "Spherical sets avoiding a prescribed set of angles" (DOV ref [9]). The attainment result reproved in DOV Sect 5. NOT read.
- M. de Laat, F. Vallentin, "A semidefinite programming hierarchy for packing problems in discrete geometry," Math. Program. (2015). The topological-packing Lasserre hierarchy (Vallentin 2014 slides). NOT read; the rigorous version of the slide roadmap.
- H. Cohn, N. Elkies, "New upper bounds on sphere packings I," Ann. Math. 157 (2003). The Euclidean LP bound (Oliveira 2016 Sect 10). Skimmed via survey.
- Schoenberg (positive type on spheres), Bochner (positive type on $\mathbb{R}^n$ / groups), Peter-Weyl, Mercer: the harmonic-analysis backbone, in Vallentin 2008 and Stein-Shakarchi (note 03).

Forward (citing these): the DeCorte-Pikhurko and DeCorte-Golubev measurable-$\chi$ line; any post-2022 SDP that improves $n=2$ (none known to cross $\chi_m\ge6$); Polymath16 (uses A1, but cross-references the density bounds).

---

## What this enables / what remains open

ENABLES (for BUILDER / VERIFIER / ADVERSARY / SYNTHESIZER):

- BUILDER [SETTLED]: the $\chi_m \ge 5$ density crossing is already DONE in-repo (L35/L36, Ambrus 2023 reproduction, self-certified $m_1 \le 0.246894 < 1/4$). Remaining build work is not "reach 5" but: (a) clean analytic-quality reproduction of the 2-point bound ($0.268$) and the KMOR point-set bound ($0.2588$) as calibration; (b) the genuinely open multi-class / many-distance LP toward the $\ge 6$ question (provably blocked for single-class). Basis: Gegenbauer/Bessel $|\mu_k^{-1}|L_k^{0}(2\pi t)$, NOT monomials (Vallentin 2014 numerical guidance).
- VERIFIER: re-run the repo's `e3j` self-certification (its own primal+dual, gap $\sim 10^{-16}$) confirming $m_1(\mathbb{R}^2)\le 0.246894$, or the DOV/KMOR dual-certificate checker (rational perturbation + eigenvalue bound). Confirm the $\chi_m\ge6$ FLOOR argument (Croft density-$0.22936$ tile $\Rightarrow m_1 \ge 0.22936 > 1/5 \Rightarrow 1/m_1 \le 4.36 < 5 \Rightarrow$ density cannot reach 6).
- ADVERSARY: apply the detector hooks. Any claimed measurable/spectral bound must (i) be blind to $\mathbb{Q}^2$ legitimately (measure zero), (ii) MOVE when the unit ball changes circle$\to$square (else it does not use Euclidean rigidity), (iii) return $\chi_m(\mathbb{R}^1)=2$ (Bessel degenerates, DOV Lemma 10.2 "false for $n=1$"). Also: reject any single-class density argument claiming $\chi_m(\mathbb{R}^2)\ge6$ (provably blocked by the $0.22936 > 1/5$ floor); accept $\chi_m \ge 5$ only with $m_1 < 1/4$ STRICTLY (Ambrus 2023 has it; KMOR's $0.2588$ does not).
- SYNTHESIZER [SETTLED]: A2's single-class density engine (2-point Bessel note 04; point-set / IEC-strengthened, this note + repo L35/L36) reaches $\chi_m(\mathbb{R}^2) \ge 5$ (Ambrus 2023, $m_1 \le 0.2469 < 1/4$) and is CAPPED there (Croft floor $> 1/5$). $\chi_m(\mathbb{R}^2)\ge5$ is independently Falconer 1981. The $\chi_m(\mathbb{R}^2)\ge6$ frontier is blocked for the density engine and is a SEPARATE negative result, distinct from the A1 "$\chi$-6 embeddable graph" bottleneck.

OPEN / LIMITATIONS:

- $\chi_m(\mathbb{R}^2)\ge6$ is UNREACHABLE by single-class avoiding-set density: $m_1(\mathbb{R}^2)\ge0.22936>1/5$ from an explicit construction (Croft), so $1/m_1\le4.36 < 5$, and the density method $\chi_m \ge 1/m_1$ caps at $\chi_m \ge 5$ (attained: Ambrus 2023, $m_1 \le 0.2469 < 1/4$, repo L35/L36). A genuinely new measurable obstruction (multi-class partition Fourier bound) would be needed for 6; the DOV framework supports the many-distance LP but no $\mathbb{R}^2$ computation crosses it.
- The complete-positivity characterization (DOV Thm 1.1) is EXACT but the CP/copositive cone is computationally intractable in general (copositivity is co-NP-hard). The practical hierarchy (BQP$(U)$ facets up to $|U|\approx7$) is a finite truncation; convergence to $m_1$ (DOV Sect 10) is guaranteed in the limit but the rate is unknown and the constraints get rapidly harder.
- The integer bottleneck ($\chi\ge6$ embeddable UDG) is UNTOUCHED. This cluster bounds $\chi_m$, and $\chi\ge\chi_m$, so a future $\chi_m\ge6$ would settle $\chi\ge6$, but per the floor that route is blocked in 2D. The cluster's live contribution is: sharper $\chi_m$ bounds in dimensions $n\ge3$ (Table 2), the exact convex characterization, and the seeding relationship (A1 graphs feed A2/A3 SDP constraints).
