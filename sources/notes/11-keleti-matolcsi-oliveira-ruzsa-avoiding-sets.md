# KMOR 2016: "Better bounds for planar sets avoiding unit distances" -- structured notes

SURVEYOR notes on Keleti, Matolcsi, de Oliveira Filho, Ruzsa, "Better bounds for planar sets avoiding unit distances," arXiv:1501.00168v2 (26 Oct 2015), published Discrete Comput. Geom. 55 (2016) 642-661. Architecture A2 (measurable / spectral) primary, A3 (fractional / Lovasz $\vartheta$, via the LP relaxation) shared. This is the SOURCE paper for the planar avoiding-set density bound that the project cites elsewhere; accuracy of the exact constants is the point of this note.

Source PDF: `sources/papers/Keleti-Matolcsi-Oliveira-Ruzsa-2016-Better-Bounds-for-Planar-Sets-Avoiding-Unit-Distances_arXiv-1501.00168.pdf`. Extracted text: `sources/_extracted/Keleti-Matolcsi-Oliveira-Ruzsa-2016-Better-Bounds-for-Planar-Sets-Avoiding-Unit-Distances_arXiv-1501.00168.txt`.

> **CONTEXT BANNER (post-KMOR development; reconciled with repo LEARNINGS L35/L36).** This paper
> (2016) gives $m_1(\mathbb{R}^2) \le 0.258795$, which is JUST SHORT of $1/4$, so KMOR alone yields
> only $\chi_m(\mathbb{R}^2) \ge 4$. That is correct and is the point of this note. BUT the density
> route did not stop here: **Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023** (arXiv:2207.14179)
> pushed the same LP/point-set approach below $1/4$ ($m_1 \le 0.246894$) using inclusion-exclusion
> CONGRUENCE constraints, thereby reaching $\chi_m(\mathbb{R}^2) \ge 5$ BY DENSITY. The repo
> reproduces and self-certifies this (LEARNINGS L35/L36, `experiments/fractional/e3i`,`e3j`). So the
> phrase below "$\chi_m \ge 5$ is Falconer, not density" should read: $\chi_m \ge 5$ is reached by
> BOTH Falconer 1981 (separate measurable argument) AND the density route via Ambrus 2023 (not KMOR,
> which fell short). The discrepancy this note flags in note 08 (the "$0.229$ upper bound" error) was
> real and is fixed; but note 08's conclusion that the density route reaches $\chi_m \ge 5$ was
> ultimately correct, via Ambrus 2023 rather than the $0.229$ figure. The $\ge 6$ ceiling stands.

---

## Executive summary (the exact constants)

1. UPPER bound on $m_1(\mathbb{R}^2)$ (the headline result, Theorem 3.1): $m_1(\mathbb{R}^2) \le 0.258795$. Method: a strengthening of the Oliveira-Vallentin LP / harmonic-analysis bound, using three Moser-spindle subgraph constraints plus five 6-point inclusion-exclusion configurations; the radial symbol is the Bessel function $\Omega_2(t) = J_0(t)$.
2. This upper bound yields $\chi_m(\mathbb{R}^2) \ge \lceil 1/0.258795 \rceil = \lceil 3.864\ldots \rceil = 4$. By itself the KMOR upper bound does NOT reach $\chi_m \ge 5$. (Falconer's $\chi_m(\mathbb{R}^2) \ge 5$ is independent; see caveat below.)
3. LOWER bound on $m_1(\mathbb{R}^2)$ (cited, not original here): Croft's tortoise construction gives $m_1(\mathbb{R}^2) \ge 0.22936$ (optimized at hexagon-height parameter $x = 0.96553\ldots$). The plain disk-on-hexagonal-lattice construction gives the weaker $\pi/(8\sqrt{3}) = 0.2267\ldots$.
4. Implied ceiling for the density method: $1/m_1(\mathbb{R}^2) \le 1/0.22936 = 4.3600\ldots$. Forcing 5 colors to be insufficient (i.e. $\chi_m \ge 6$) requires $m_1 < 1/5 = 0.2$; but the Croft floor $m_1 \ge 0.22936 > 1/5$ refutes that, so $1/m_1 \le 4.36 < 5$ and the single-class density method CANNOT reach $\chi_m \ge 6$. It caps at $\chi_m \ge 5$. Reaching the cap needs $m_1 < 1/4$, which KMOR's $0.2588$ does NOT achieve but Ambrus et al. 2023 ($m_1 \le 0.2469$, repo L35/L36) does. (Threshold note: $\chi_m \ge k+1$ needs $m_1 < 1/k$; so $\ge 5$ needs $< 1/4$, $\ge 6$ needs $< 1/5$. The relevant floor comparison for the $\ge 6$ obstruction is $1/5$, not $1/6$.)
5. The block-structure theorem (Theorem 2.1 / 2.2): any 1-avoiding set in $\mathbb{R}^n$ ($n \ge 2$) with block structure has density $\le 1/2n - \varepsilon_n$ for some $\varepsilon_n > 0$. For $n = 2$ this proves the Erdos conjecture $m_1(\mathbb{R}^2) < 1/4$ FOR THE SPECIAL CASE of block-structured sets. The general (non-block) Erdos conjecture remains open.
6. General $n$: the paper records the asymptotic upper bounds $m_1(\mathbb{R}^n) \le (1+o(1)) 1.207^{-n}$ (Frankl-Wilson) and the weaker $1.1654^{-n}$ (Oliveira-Vallentin), with the best known $1.268^{-n}$ due to Bachoc-Passuello-Thiery; KMOR's own new numbers are planar only.
7. Detector status: PASS, A2-exempt on $\mathbb{Q}^2$ (measure zero). Euclidean rotational rigidity enters precisely through the radialization over $O(2)$ and the Bessel $J_0$ symbol (Theorem 3.1 machinery). The block-structure argument (Theorem 2.2) uses Brunn-Minkowski, the isodiametric inequality, and a ball-packing-density bound $\Delta_n < 1$, all genuinely Euclidean-metric.
8. CRITICAL DISCREPANCY with note 08: note 08 repeatedly attributes "$m_1(\mathbb{R}^2) \le 0.229$" to THIS paper. That is wrong. $0.229$ ($= 0.22936$) is the Croft LOWER bound (a construction floor) that this paper CITES; the paper's own UPPER bound is $0.258795$. Note 08's "$\chi_m \ge 5$ via KMOR's $m_1 \le 0.229$" is a conflation. See the discrepancy log below; this needs reconciling across the repo.

---

## 1. The two main theorems, stated precisely

### Theorem 2.1 / 2.2 (block structure)

Definition (block structure, paper Sect 1, eq. before Theorem 2.1): a set $A = \bigcup_{i=0}^\infty A_i$ has block structure if $\|x-y\| < 1$ whenever $x, y$ are in the same block $A_i$, and $\|x-y\| > 1$ whenever $x, y$ are in distinct blocks. Such a set is automatically 1-avoiding. The paper notes (Sect 2) that ALL known high-density 1-avoiding constructions (disks on the hexagonal lattice, Croft's tortoises) are block-structured.

Theorem 2.1: Let $n \ge 2$ and let $A \subseteq \mathbb{R}^n$ be a 1-avoiding set having block structure. Then $\delta(A) \le 1/2n - \varepsilon_n$ for some $\varepsilon_n > 0$.

Theorem 2.2 (the slightly stronger statement actually proved): Let $n \ge 2$ and let $A_1, A_2, \ldots \subseteq \mathbb{R}^n$ be sets of diameter at most 1 such that the distance between any two of them is at least 1. Then the upper density of $A = \bigcup_i A_i$ is at most $1/2n - \varepsilon_n$ for some $\varepsilon_n > 0$.

Consequence for $n = 2$: block-structured 1-avoiding sets have density $\le 1/4 - \varepsilon_2 < 1/4$. This proves the Erdos conjecture $m_1(\mathbb{R}^2) < 1/4$ RESTRICTED to block-structured sets. For $n \ge 3$ it is a special case of the Larman-Rogers-Moser conjecture (volume of a closed 1-avoiding set inside a unit ball is $< 1/2n$ of the ball).

Important: the $\varepsilon_n$ is NOT made explicit. Theorem 2.2 is qualitative (a strict-inequality / stability result), not a numerical improvement. It does NOT give a number better than $1/4$ for $m_1(\mathbb{R}^2)$; it gives strictness ($< 1/4$) for the block-structured subclass only. The quantitative planar number comes entirely from Theorem 3.1.

### Theorem 3.1 (the numerical upper bound)

Theorem 3.1: $m_1(\mathbb{R}^2) \le 0.258795$.

This is the headline number. It is proved by the LP / harmonic-analysis method of Sect 3 (details in Sect 4 below). It improves the previous best upper bounds in this lineage:
- Equilateral triangle (averaging): $m_1(\mathbb{R}^2) \le 1/3 = 0.333\ldots$
- Moser spindle (averaging, $\alpha(G)/|V| = 2/7$): $m_1(\mathbb{R}^2) \le 2/7 = 0.2857\ldots$ (best from a single finite subgraph).
- Szekely 1984: $m_1(\mathbb{R}^2) \lesssim 0.279$.
- Oliveira-Vallentin 2010 (LP + harmonic analysis, equilateral triangles): $m_1(\mathbb{R}^2) \le 0.268$ (paper writes $\approx 0.268$).
- KMOR 2016 (this paper): $m_1(\mathbb{R}^2) \le 0.258795$.

The paper notes (Sect 3.2, end) that with more constraints they could push slightly lower but never below $\approx 0.257$, "which is probably the limit of this method."

---

## 2. The block-structure proof (Theorem 2.2), method detail

The argument is metric-geometric, NOT Fourier-analytic. Structure (paper Sect 2):

Step 0 (reduction): diameter $\le 1$ and pairwise distance $\ge 1$ are preserved under closure, so assume the $A_i$ are closed (hence measurable). This reduction works ONLY under block structure; in the general case there exists a non-measurable 1-avoiding set of full outer measure, which is why the general Erdos conjecture is hard.

Step 1 (the easy $\le 1/2n$, no $\varepsilon$): set $C_i = A_i + B_{1/2}$ (Minkowski sum with the open radius-$1/2$ ball). Block structure forces the $C_i$ pairwise disjoint. Brunn-Minkowski gives $\lambda(C_i)^{1/n} \ge \lambda(A_i)^{1/n} + \lambda(B_{1/2})^{1/n}$; the isodiametric inequality gives $\lambda(A_i) \le \lambda(B_{1/2})$ (since $\mathrm{diam}\, A_i \le 1$). Combining (eq. 1):
$$\frac{\lambda(A_i)^{1/n}}{\lambda(C_i)^{1/n}} \le \frac{1}{1 + (\lambda(B_{1/2})/\lambda(A_i))^{1/n}} \le \frac{1}{1+1} = \frac{1}{2}.$$
Since the $C_i$ are disjoint and $A_i \subseteq C_i$, raising to the $n$-th power gives $\delta(A) \le 1/2^n$. (Note: the abstract and Theorems say $1/2n$, but the displayed bound from this chain is $1/2^n$. For $n = 2$ both equal $1/4$, so the planar Erdos statement is unaffected. This $1/2n$ vs $1/2^n$ is the paper's own notation; the Larman-Rogers-Moser conjecture they reference is stated as "$< 1/2n$" in the introduction but the proof delivers $1/2^n$. For $n=2$ they coincide; for $n \ge 3$ read the proof's $1/2^n$. Flag for VERIFIER if the $n \ge 3$ statement is ever used quantitatively.)

Step 2 (the $-\varepsilon_n$ via stability): the plan (paper p. 4-5): if $\delta(A)$ is close to $1/2n$ then for most $i$ the isodiametric inequality is nearly tight and $\mathrm{diam}\, A_i \approx 1$. A stability theorem (Maggi-Ponsiglione-Pratelli, Lemma 2.3, quantitative isodiametric stability via the isoperimetric inequality) then forces each such $A_i$ to be close to a ball of radius $1/2$, so most $C_i = A_i + B_{1/2}$ are close to UNIT balls. But the density of any unit-ball packing is bounded away from 1 by $\Delta_n < 1$ (true for all $n \ge 2$, exact value unknown in general). Since $A$ occupies at most a $1/2n$ fraction of $\bigcup_i C_i$ and the $C_i$ pack at density $\le \Delta_n < 1$, the density of $A$ is bounded away from $1/2n$. Corollary 2.4 packages the stability estimate into an increasing function $\beta_n(\rho) \to 0$. The final constant choice (paper p. 7) picks $\alpha, \rho, \varepsilon_n$ so that $\Delta_n ((1+\beta(\rho))/(1-\beta(\rho)))^n + \alpha + 2n\varepsilon_n < 1$.

Step 3 (a 1-avoiding set WITHOUT block structure, paper p. 7-8): scaled integer lattice $(c\mathbb{Z})^2$ with $c = 2\sqrt{2} - 2$, open disks of radius $r = (3 - 2\sqrt{2})/2$ at each lattice point. Adjacent-lattice-point disks have all inter-point distances $< 1$; non-adjacent ones have distances $> 1$; but the disk-pair relation is not transitive, so this is 1-avoiding WITHOUT block structure. Density $\delta = r^2 \pi / c^2 \approx 0.0337$. Purpose: shows Theorem 2.2 genuinely needs the block hypothesis, and that not every positive-density 1-avoiding set can be massaged into a block-structured one of equal-or-greater density.

The paper's honest caveat (end of Sect 2): they could NOT prove that a maximum-density 1-avoiding set must be block-structured, so Theorem 2.2 does not settle the full Erdos conjecture.

---

## 3. The upper-bound proof (Theorem 3.1), method detail

This is the harmonic-analysis / LP route, a strengthening of Oliveira-Vallentin 2010. Cross-reference: this is exactly the lineage of note 08 (DeCorte-Oliveira-Vallentin and the SDP hierarchy); KMOR is the concrete planar computation.

### 3a. Setup: autocorrelation, restrict to periodic sets

For a measurable periodic 1-avoiding set $A$ with periodicity lattice $L$, the autocorrelation function is $f(x) = \delta(A \cap (A - x)) = \langle 1_A, 1_{A-x} \rangle$. Computing $m_1(\mathbb{R}^n)$ is equivalent to maximizing $f(0) = \delta(A)$ over autocorrelation functions of 1-avoiding sets. One may restrict to periodic sets (their densities approach $m_1$). The difficulty: no characterization of which $f$ are autocorrelation functions, so one relaxes to functions satisfying only NECESSARY constraints, yielding an upper bound.

### 3b. The constraints (Lemma 3.2)

For $f$ the autocorrelation function of a measurable periodic 1-avoiding set:
1. $f(x) = 0$ if $\|x\| = 1$ (the FORBIDDEN-DISTANCE constraint; this is where "avoiding distance 1" enters). Proof: $A \cap (A-x) = \emptyset$ when $\|x\| = 1$.
2. For any finite subgraph $G = (V,E)$ of the unit-distance graph: $\sum_{x \in V} f(x) \le f(0)\,\alpha(G)$. (Observed by Oliveira-Vallentin for cliques; KMOR use it for Moser spindles.) Proof: any point lies in at most $\alpha(G)$ of the translates $A - x$, $x \in V$.
3. For any finite point set $C \subseteq \mathbb{R}^n$ (inclusion-exclusion, used by Szekely): $\sum_{\{x,y\} \in \binom{C}{2}} f(x-y) \ge |C| f(0) - 1$.

Remark 3.3: constraints (2) and (3) are both consequences of the self-consistency of higher-order correlation functions $F_k$. Remark 3.4: a Kai Lai Chung / Szekely-Wormald generalization of (3) exists but gave NO numerical improvement in 2D when implemented.

### 3c. Fourier positivity and radialization (where Euclidean structure enters)

Parametrize $f$ via its Fourier series over the dual lattice $2\pi L^*$. By Parseval (eq. 20), $f(x) = \sum_{u \in 2\pi L^*} |\hat{1}_A(u)|^2 e^{iu \cdot x}$, so the Fourier coefficients $\hat f(u) = |\hat{1}_A(u)|^2 \ge 0$: $f$ is POSITIVE DEFINITE. This is the extra constraint that the LP exploits.

Radialization (eq. 21): average $f$ over the orthogonal group $O(\mathbb{R}^n)$ (equivalently over the sphere $S^{n-1}$): $\mathring f(x) = \int_{O(\mathbb{R}^n)} f(Tx)\, d\mu(T)$. This produces a RADIAL function. The constraints of Lemma 3.2 are rotation-invariant (as families over all graphs / all point sets), so $\mathring f$ inherits them. Schoenberg's formula (eq. before 22): define $\Omega_n$ by $\Omega_n(\|x\|) = \frac{1}{\omega(S^{n-1})} \int_{S^{n-1}} e^{ix \cdot \xi}\, d\omega(\xi)$, giving
$$\Omega_n(t) = \Gamma\!\left(\tfrac{n}{2}\right) \left(\tfrac{2}{t}\right)^{(n-2)/2} J_{(n-2)/2}(t), \quad \Omega_n(0) = 1,$$
where $J_\alpha$ is the Bessel function of the first kind. THE PLANAR SPECIALIZATION: for $n = 2$, $\Omega_2(t) = J_0(t)$, the Bessel function of order 0. This $J_0$ is the operative object for the entire planar bound.

The radialized autocorrelation is $\mathring f(x) = \sum_{t \ge 0} \kappa(t)\, \Omega_n(t\|x\|)$ (eq. 22), where $\kappa(t)$ is the sum of $\hat f(u)$ over $\|u\| = t$, with $\kappa(t) \ge 0$, $\sum_t \kappa(t) = \delta$, and $\kappa(0) = \delta^2$.

### 3d. The LP and the witness function (Proposition 3.5)

Constraints in terms of $\kappa$ (eqs. 23-24):
- $\sum_t \kappa(t) = \delta$;
- $\sum_t \kappa(t) \Omega_n(t) = 0$ (the forbidden distance 1);
- $\sum_t \kappa(t) \sum_{x \in V(G)} \Omega_n(t\|x\|) \le \delta\, \alpha(G)$ for all graphs $G$;
- $\sum_t \kappa(t) \sum_{\{x,y\}} \Omega_n(t\|x-y\|) \ge \delta |C| - 1$ for all finite $C$;
- $\kappa(0) = \delta^2$, $\kappa(t) \ge 0$.

Proposition 3.5 (the dual / witness form): given finite collections $S$ of subgraphs and $C$ of point sets and nonnegative multipliers $v_0, v_1, w_G, z_C$, form the witness
$$W(t) = v_0 + v_1 \Omega_n(t) + \sum_{G \in S} w_G \sum_{x \in V(G)} \Omega_n(t\|x\|) - \sum_{C \in \mathcal C} z_C \sum_{\{x,y\}} \Omega_n(t\|x-y\|).$$
If $W(0) \ge 1$ and $W(t) \ge 0$ for all $t > 0$, then $m_1(\mathbb{R}^n) \le \delta$ where $\delta$ solves the quadratic (eq. 26)
$$\delta^2 = \delta\Big(v_0 + \sum_{G} w_G \alpha(G) - \sum_C z_C |C|\Big) + \sum_C z_C.$$
Proof: $\delta^2 = \kappa(0) \le \sum_t \kappa(t) W(t)$, then substitute the constraints.

### 3e. The actual planar computation (Sect 3.1-3.2)

Experimental pipeline:
- $S = \mathcal C = \emptyset$ gives $W(t) = v_0 + v_1 \Omega_2(t)$, best bound $\approx 0.287$ (slightly worse than Moser's $2/7$).
- Oliveira-Vallentin: $\mathcal C = \emptyset$, $S$ = a few equilateral triangles, gives $\approx 0.268$.
- KMOR step 1: $\mathcal C = \emptyset$, $S$ = congruent copies of the MOSER SPINDLE placed as $(t,0) + R(\theta)G$ over a discretized grid ($\varepsilon = 0.1$, $-4 \le t \le 4$, $0 \le \theta \le 2\pi$). Solving the discretized LP (eq. 30) with $L = 200$, $\varepsilon = 0.01$, $\delta = 0.26305$ gives $\sup \tilde\kappa(0) \approx 0.26305$, a bound $\lesssim 0.26305$. Only THREE spindles end up active.
- KMOR step 2: add inclusion-exclusion constraints from 6-point sets $C$ ($N = 6$ was the only size that helped), found by numerical nonlinear optimization to minimize the LHS of constraint (3). Iterate. Limit reached.

Final certificate (Sect 3.2): $S$ = three Moser spindles $G_1, G_2, G_3$ at $(t,\theta) = (0.4, 5.4), (0.6, 5.4), (0.8, 5.4)$. $\mathcal C$ = five 6-point configurations $C_1, \ldots, C_5$ (Table 1; each contains the origin). Explicit multipliers (eq. 32): $v_0 = 2.3022\ldots$, $v_1 = 27.2729\ldots$, $w_1 = 0.2022$, $w_2 = 0.4312$, $w_3 = 1.3855$, $z_1 = 0.2863$, $z_2 = 0.7909$, $z_3 = 0.9616$, $z_4 = 0.2772$, $z_5 = 0.5312$.

Verification (the rigor part, Sect 3.2): with $\Omega_2 = J_0$, define $\varphi(t) = v_0 + v_1 J_0(t) + \sum_i w_i \sum_x J_0(t\|x\|) - \sum_i z_i \sum_{\{x,y\}} J_0(t\|x-y\|)$. Need $\varphi(0) \ge 1$ and $\varphi(t) \ge 0$ for $t > 0$.
- Tail: $J_0(t) \to 0$ as $t \to \infty$, so $\varphi(t) \to v_0 > 0$. Quantitatively, using $dJ_0/dt = -J_1(t)$ and that the local extrema of $J_0$ (at zeros of $J_1$) decrease in absolute value, the oscillating part has absolute value $\le v_0 - 0.05 \approx 2.2522$ for $t \ge 779.8998\ldots$ (the 248th positive zero of $J_1$). So $\varphi(t) \ge 0$ for $t \ge L = 780$.
- Interior $[0, L]$: sample. Using $|J_1(t)| \le 1/\sqrt 2$ gives $|\varphi'(t)| \le 75.9547$, so a grid of spacing $\varepsilon/76$ controls the minimum to additive error $\varepsilon$. With $\varepsilon = 10^{-4}$ the minimum of $\varphi$ on $[0,L]$ is $\ge -0.00011$. Adding $0.00011$ to $v_0$ restores nonnegativity.
- Solving the quadratic (eq. 26) with the adjusted constants yields $\delta \le 0.258795$.

The verification was implemented as a short Sage script shipped with the arXiv version; Bessel values are computed numerically (not rational arithmetic), but the code is simple enough to inspect. A fully rigorous rational-arithmetic check is noted as possible but not done.

---

## 4. The lower bound on $m_1(\mathbb{R}^2)$ (cited constructions, Sect 1)

The paper does NOT improve the lower bound; it cites the known constructions to frame the gap:

- Disk-on-hexagonal-lattice: hexagonal lattice with minimal vectors of length 2, open disk of radius $1/2$ at each point. 1-avoiding, density $\pi/(8\sqrt 3) = 0.2267\ldots$.
- Croft 1967 (the "tortoise," paper Sect 1 and Figure 1): shrink the hexagonal lattice to minimal-vector length $1 + x$ ($x < 1$), place at each lattice point the intersection of an open disk of radius $1/2$ with an open regular hexagon of height $x$. The disk keeps intra-block distances $< 1$; the hexagon keeps inter-block distances $> 1$. Optimizing at $x = 0.96553\ldots$ gives density $m_1(\mathbb{R}^2) \ge 0.22936$.

So the best LOWER bound stated is $m_1(\mathbb{R}^2) \ge 0.22936$ (Croft). This is a block-structured construction (consistent with Theorem 2.2's "$< 1/4$" for block-structured sets, since $0.22936 < 0.25$).

### Implied ceiling for the density method

$$m_1(\mathbb{R}^2) \ge 0.22936 \implies \frac{1}{m_1(\mathbb{R}^2)} \le \frac{1}{0.22936} = 4.3600\ldots.$$
Because $\chi_m(\mathbb{R}^2) \ge 1/m_1(\mathbb{R}^2)$ is a LOWER bound (you cannot turn a lower bound on $m_1$ into a lower bound on $\chi_m$), the right reading is: the BEST a single-class density argument could ever prove is $\chi_m \ge \lceil 1/m_1 \rceil$, and the TRUE $m_1$ is pinned in $[0.22936, 0.258795]$. Even at the optimistic end $m_1 = 0.22936$, $\lceil 1/0.22936 \rceil = \lceil 4.36 \rceil = 5$. To reach $\chi_m \ge 6$ one needs $m_1 < 1/5 = 0.2$ (so that $1/m_1 > 5$), which is REFUTED by the Croft construction ($0.22936 > 0.2$). Therefore:

CONCLUSION: $\chi_m(\mathbb{R}^2) \ge 6$ is UNREACHABLE by any single-class avoiding-set density bound. The density method caps at $\chi_m \ge 5$. This is a hard floor coming from an explicit construction, not a "not yet computed" gap.

Subtlety worth stating exactly: KMOR's own UPPER bound $0.258795$ gives only $\lceil 1/0.258795 \rceil = \lceil 3.864 \rceil = 4$. To get $\chi_m \ge 5$ from a density bound you need $m_1 < 1/5 = 0.2$, and to even hit the Erdos-conjectured regime you need $m_1 < 1/4 = 0.25$. KMOR push BELOW $1/4$ (good for Erdos's conjectured value, $0.258795 > 0.25$ actually does NOT cross $1/4$). Recheck: $0.258795 > 0.25$, so KMOR's upper bound does NOT prove the Erdos conjecture $m_1 < 1/4$ either (except for the block-structured subclass via Theorem 2.2). The Erdos conjecture $m_1(\mathbb{R}^2) < 1/4$ remains OPEN in general after this paper. KMOR narrow the window to $[0.22936, 0.258795]$ and prove the block-structured case of $< 1/4$.

---

## 5. General $n \ge 2$ and asymptotics (Sect 1)

The paper records (does not reprove) the asymptotic upper bounds:
- Frankl-Wilson 1981 (exponential-chromatic subgraphs + averaging): $m_1(\mathbb{R}^n) \le (1+o(1))\, 1.207^{-n}$.
- Oliveira-Vallentin 2010 (their harmonic-analysis method): $m_1(\mathbb{R}^n) \le (1+o(1))\, 1.1654^{-n}$ (weaker than Frankl-Wilson).
- Bachoc-Passuello-Thiery 2015 (combination of both, plus numerics for $4 \le n \le 24$): the best known asymptotic $m_1(\mathbb{R}^n) \le (1+o(1))\, 1.268^{-n}$.

KMOR explicitly state their results do NOT overlap with Bachoc-Passuello-Thiery: BPT do asymptotics and $n \ge 4$ numerics; KMOR's new numbers are the planar $0.258795$ (Theorem 3.1) and the qualitative block-structure $1/2n - \varepsilon_n$ (Theorem 2.2, all $n \ge 2$).

---

## 6. Mapping to the four architectures

- A2 (measurable / spectral): PRIMARY. Theorem 3.1 is a measurable upper bound on $m_1(\mathbb{R}^2)$, i.e. a lower bound on $\chi_m$. The autocorrelation / Fourier-positivity / Bessel-$J_0$ machinery is the Falconer-Oliveira-Vallentin measurable lineage. Theorem 2.2 (block structure) is also a measurable-density statement.
- A3 (fractional / Lovasz $\vartheta$): SHARED. The LP (eq. 30) and witness Proposition 3.5 are the dual-feasible-function ($\vartheta'$-style) relaxation; the Moser-spindle and inclusion-exclusion constraints are the same objects that DOV 2022 (note 08) reinterpret as BQP facets. The reciprocal $1/m_1 \approx 4.36$ is the same number as the $\chi_f$ ceiling noted elsewhere.
- A1 (combinatorial / UDG): SEED. The Moser spindle (a finite UDG, $\chi = 4$, $\alpha/|V| = 2/7$) is the constraint source for the planar LP. A1 BUILDER output feeds the A2/A3 LP. KMOR do not produce a $\chi \ge 6$ graph.
- A4 (axiomatic): CONTACT via measurability only. The bound is on the MEASURABLE $\chi_m$; the gap to the ZFC integer $\chi$ is the Shelah-Soifer territory, untouched here.

---

## 7. Wrong-approach-detector check

Detectors: $\chi(\mathbb{Q}^2) = 2$ (Woodall), $\chi(\ell^\infty\text{-plane}) = 4$ (Chilakamarri), $\chi(\mathbb{R}^1) = 2$. A2 is partly exempt from $\mathbb{Q}^2$ (measure zero).

- $\mathbb{Q}^2$: PASS (A2-exempt). Both theorems are Lebesgue-density statements; a 1-avoiding subset of $\mathbb{Q}^2$ has measure 0, so the method says nothing false about $\mathbb{Q}^2$ and does not pretend $\chi(\mathbb{Q}^2) > 2$. Legitimately blind to the rationals.
- $\ell^\infty$-plane: PASS. The upper-bound method radializes over $O(2)$ and uses the Bessel symbol $\Omega_2 = J_0$ (Schoenberg's formula for the EUCLIDEAN sphere). For an $\ell^\infty$ ball the invariant group is the dihedral group (finite), the $O(2)$-radialization step does not apply, and the symbol is a different Fourier transform. The block-structure proof uses Brunn-Minkowski + the isodiametric inequality + Euclidean ball-packing density $\Delta_n$, all metric-specific. The method genuinely depends on which unit ball; it would not give $4$ for the $\ell^\infty$ plane by the same route. Detector hook for ADVERSARY: any claimed bound that does not change when circle $\to$ square is suspect.
- $\mathbb{R}^1$: PASS. For $n = 1$ the Schoenberg symbol degenerates ($\Omega_1(t) = \cos t$, no decay), the radialization over $O(1) = \{\pm 1\}$ is trivial, and the set $\bigcup_k (2k, 2k+1)$ has density $1/2$ avoiding distance 1, consistent with $\chi_m(\mathbb{R}^1) = 2$. The Bessel decay that makes the tail argument (Sect 3.2) work needs $n \ge 2$. The method correctly refuses to over-constrain the line.

Verdict: detector-clean. Euclidean rotational rigidity enters at the radialization-over-$O(2)$ / Bessel-$J_0$ step (Theorem 3.1) and at the Brunn-Minkowski / isodiametric / packing-density step (Theorem 2.2). The "block structure" combinatorial argument is a separate metric-geometric tool, not Fourier.

---

## 8. Discrepancy log (vs note 08 and the project atlas)

CRITICAL DISCREPANCY (numerical, needs reconciling across the repo):

- Note 08 (`sources/notes/08-sdp-harmonic-analysis-oliveira-vallentin.md`) states in at least four places that KMOR 2016 proves "$m_1(\mathbb{R}^2) \le 0.229$" and that this yields $\chi_m(\mathbb{R}^2) \ge 5$. Specifically: note 08 line 24 ("$m_1(\mathbb{R}^2)\le 0.229$ (Keleti-Matolcsi-Oliveira-Ruzsa 2016)"), line 41 ("Keleti-Matolcsi-Oliveira-Ruzsa 2016, DOV ref [22]): $m_1(\mathbb{R}^2)\le 0.229$, hence $\chi_m(\mathbb{R}^2)\ge\lceil1/0.229\rceil=5$"), line 67, line 218-219, line 227 ("THE source of $m_1(\mathbb{R}^2)\le0.229$").
- THE PAPER ACTUALLY PROVES $m_1(\mathbb{R}^2) \le 0.258795$ (Theorem 3.1, abstract, and Sect 3.2 conclusion). It does NOT prove $\le 0.229$.
- The number $0.229$ ($= 0.22936$) in this paper is the CROFT LOWER bound (an explicit construction floor, Sect 1), the OPPOSITE direction. Note 08 has swapped the lower bound for the upper bound.
- Consequence for note 08's logic: $\lceil 1/0.258795 \rceil = 4$, NOT $5$. So KMOR's upper bound does NOT by itself give $\chi_m(\mathbb{R}^2) \ge 5$. The classical $\chi_m(\mathbb{R}^2) \ge 5$ is FALCONER 1981 (a different, earlier, measure-theoretic argument, not a density-of-avoiding-set bound). Note 08's repeated claim "the SDP/density route crosses $\chi_m \ge 5$ via KMOR's $m_1 \le 0.229$" is FALSE as stated: neither KMOR's $0.258795$ nor the Croft floor $0.22936$ gives $\chi_m \ge 5$ ($\lceil 1/0.22936 \rceil = \lceil 4.36 \rceil = 5$ only if you (illegitimately) treat the lower bound on $m_1$ as if it were an upper bound; you cannot, since $\chi_m \ge 1/m_1$ needs an UPPER bound on $m_1$).
- WHAT IS TRUE: the density method has UPPER bound $m_1(\mathbb{R}^2) \le 0.258795$ (KMOR) $\Rightarrow \chi_m \ge 4$. To get $\chi_m \ge 5$ from density alone needs $m_1 < 0.2$, which NO current bound achieves (best is $0.258795$). So $\chi_m(\mathbb{R}^2) \ge 5$ does NOT come from the density method at all; it comes from Falconer 1981 (and is reconfirmed by de Grey's integer $\chi \ge 5$). The DOV 2022 framework (note 08) sharpens $\chi_m$ in dimensions $n \ge 3$, but in 2D the density method is STUCK at $\chi_m \ge 4$.
- This INVERTS one of note 08's headline conclusions. Note 08 line 44 says "$1/m_1(\mathbb{R}^2)\approx 4.36$" and "the BQP/Lasserre constraints buy the extra push ... to the integer crossing $\ge5$" -- but $4.36$ is the reciprocal of the LOWER bound $0.22936$, i.e. it is the optimistic CEILING on what density could ever prove IF $m_1$ equaled its lower bound, not an achieved upper-bound-derived value. The achieved upper bound $0.258795$ gives reciprocal $3.864$, i.e. $\chi_m \ge 4$. Note 08 conflates "the best lower bound on $m_1$" (a construction, $0.22936$) with "the best proven upper bound on $m_1$" (KMOR, $0.258795$) and treats $1/(\text{lower bound}) = 4.36$ as if it certified $\chi_m \ge 5$.

The correct picture, stated cleanly:
- $m_1(\mathbb{R}^2) \in [0.22936, 0.258795]$ (Croft lower, KMOR upper).
- The density method proves $\chi_m(\mathbb{R}^2) \ge \lceil 1/0.258795 \rceil = 4$.
- $\chi_m(\mathbb{R}^2) \ge 5$ is Falconer 1981, NOT a density bound.
- $\chi_m(\mathbb{R}^2) \ge 6$ is unreachable by single-class density because the Croft construction gives $m_1 \ge 0.22936 > 1/5$, so $1/m_1 \le 4.36 < 5$ regardless of how the upper bound improves (forcing 5 colors insufficient would need $m_1 < 1/5$).

The "$\ge 6$ unreachable" conclusion of note 08 is CORRECT (and is the genuinely useful negative result). The "$\ge 5$ via KMOR density" claim is WRONG; $\ge 5$ is Falconer. Flag for SYNTHESIZER and VERIFIER: correct note 08's attribution and the four lines citing "$m_1 \le 0.229$."

Other notes:
- No contradiction with the landmarks: $4 \le \chi(\mathbb{R}^2) \le 7$, Moser spindle $\chi = 4$, Falconer $\chi_m \ge 5$, Woodall (measure-zero exemption) all consistent.
- The paper itself states $4 \le \chi(\mathbb{R}^2) \le 7$ (it predates de Grey 2018, so it does NOT know $\chi \ge 5$). Anyone citing KMOR for the integer lower bound should note it is pre-de-Grey.
- The $1/2n$ vs $1/2^n$ notation point (Sect 2 above): for $n = 2$ harmless; for $n \ge 3$ the proof delivers $1/2^n$, the introduction writes $1/2n$. Flag if the $n \ge 3$ block bound is ever used numerically.

---

## 9. References to follow up

Cited by KMOR, central to A2/A3 (read status):
- F.M. de Oliveira Filho, F. Vallentin, "Fourier analysis, LP, and densities of distance-avoiding sets in $\mathbb{R}^n$," JEMS 12 (2010) 1417-1428. The parent method; the $\approx 0.268$ planar 2-point bound. Skimmed via note 08; pull for the exact triangle-constraint computation.
- L.A. Szekely, "Measurable chromatic number of geometric graphs ...," Combinatorica 4 (1984) 213-218. The $\approx 0.279$ bound and inclusion-exclusion constraint (3). NOT read.
- C. Bachoc, A. Passuello, A. Thiery, "The density of sets avoiding distance 1 in Euclidean space," Discrete Comput. Geom. 53 (2015) 783-808. The $1.268^{-n}$ asymptotic and $4 \le n \le 24$ numerics. NOT read.
- K.J. Falconer, "The realization of distances in measurable subsets covering $\mathbb{R}^n$," JCTA 31 (1981) 184-189. THE actual source of $\chi_m(\mathbb{R}^2) \ge 5$ (which note 08 mis-attributes to KMOR). NOT read; HIGH PRIORITY to settle the discrepancy.
- F. Maggi, M. Ponsiglione, A. Pratelli, "Quantitative stability in the isodiametric inequality ...," Trans. AMS 366 (2014) 1141-1160. The stability theorem (Lemma 2.3) behind Theorem 2.2. NOT read.
- H.T. Croft, "Incidence incidents," Eureka 30 (1967) 22-26. The tortoise construction, $m_1 \ge 0.22936$. NOT read (primary source for the lower bound).
- P. Frankl, R.M. Wilson, "Intersection theorems with geometric consequences," Combinatorica 1 (1981) 357-368. The $1.207^{-n}$ asymptotic. NOT read.
- D.G. Larman, C.A. Rogers, "The realization of distances within sets in Euclidean space," Mathematika 19 (1972) 1-24. The Larman-Rogers-Moser conjecture. NOT read.
- L.A. Szekely, N.C. Wormald, "Bounds on the measurable chromatic number of $\mathbb{R}^n$," Discrete Math. 75 (1989) 343-372. The Kai Lai Chung generalization (Remark 3.4). NOT read.

Forward (citing KMOR): DeCorte-Oliveira-Vallentin 2022 (note 08, ref [22], reinterprets KMOR's constraints as BQP facets); any post-2016 planar SDP (none crosses $\chi_m \ge 6$, per the floor).

---

## 10. What this enables / what remains open

ENABLES:
- BUILDER: KMOR Sect 3.2 gives an EXPLICIT, checkable certificate (three Moser spindles at $(0.4,5.4),(0.6,5.4),(0.8,5.4)$; five 6-point sets in Table 1; multipliers in eq. 32). A BUILDER can reproduce $m_1(\mathbb{R}^2) \le 0.258795$ by evaluating $\varphi(t) = v_0 + v_1 J_0(t) + \ldots$ and confirming $\varphi \ge 0$ on $[0, 780]$ (grid $\varepsilon/76$) plus the tail argument (248th zero of $J_1$ at $779.8998$). The Sage script ships with arXiv:1501.00168v2.
- VERIFIER: confirm the exact constants. The repo's L35/L36 LP crossing should be checked against $0.258795$ (upper) and $0.22936$ (lower), NOT against a spurious "$0.229$ upper bound."
- ADVERSARY: confirm the $\chi_m \ge 6$ floor (Croft $0.22936 > 1/5$, so $1/m_1 < 5$). Apply the $\ell^\infty$ / $\mathbb{R}^1$ detector hooks (the bound must move when the ball changes; it must degenerate for $n = 1$).
- SYNTHESIZER: CORRECT the note-08 attribution. The truth: KMOR upper bound is $0.258795$ ($\Rightarrow \chi_m \ge 4$); the Croft lower bound is $0.22936$; $\chi_m(\mathbb{R}^2) \ge 5$ is FALCONER 1981, not a density bound; $\chi_m(\mathbb{R}^2) \ge 6$ is provably out of reach for single-class density.

OPEN / LIMITATIONS:
- The Erdos conjecture $m_1(\mathbb{R}^2) < 1/4$ is OPEN in general (KMOR's upper bound $0.258795 > 1/4$; they prove $< 1/4$ only for block-structured sets, Theorem 2.2).
- The density method in 2D is STUCK at $\chi_m \ge 4$ (best upper bound $0.258795$, reciprocal $3.864$). To reach $\chi_m \ge 5$ via density would need $m_1 < 0.2$, well below the current best $0.258795$ and below the conjectured Erdos value if that value is near the Croft floor $0.22936$. So density may NEVER prove $\chi_m \ge 5$; Falconer's separate argument is what gives $\ge 5$.
- $\chi_m(\mathbb{R}^2) \ge 6$ unreachable by single-class density (Croft floor). A multi-class / multi-distance measurable obstruction would be needed; KMOR do not provide one.
- The block-structure theorem is qualitative ($\varepsilon_n$ not explicit) and conditional on block structure; reducing a general 1-avoiding set to block structure is the unproved missing step toward the full Erdos conjecture.
