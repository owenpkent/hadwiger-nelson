# Stein & Shakarchi, *Fourier Analysis: An Introduction* (Princeton Lectures in Analysis I, 2003)

Source: `sources/books/Stein-Shakarchi-2003-Fourier-Analysis.pdf`
Extracted text: `sources/_extracted/Stein-Shakarchi-2003-Fourier-Analysis.txt`
Role in project: foundations for **Architecture A2 (measurable / spectral)**, the route to lower bounds on $\chi_m(\mathbb{R}^2)$ via harmonic analysis.

**This is Volume I (foundations).** It develops Fourier analysis on $S^1$, $\mathbb{R}$, $\mathbb{R}^d$, and finite abelian groups, but stays inside the Schwartz space $\mathcal{S}$ and functions of moderate decrease. It does NOT prove Bochner's theorem, the Plancherel theorem in the $L^2$ / Lebesgue setting, distribution theory, or measure-theoretic harmonic analysis. The authors say so explicitly: the general theory "must necessarily be based on Lebesgue integration" and "will be treated in Book III" (Ch 5, intro, around line 7426). So this book gives the *clean Schwartz-space prototypes* of every identity A2 needs; the research-strength versions (tempered distributions, the Fourier transform of the surface measure on $S^1$ as a measure, the SDP / Bochner positivity) live in Vol III and in Bachoc-DeCorte-Oliveira-Vallentin.

---

## Executive summary: what this gives Architecture A2 (10 lines)

1. **Fourier transform on $\mathbb{R}^d$**, definition + inversion + Plancherel, all proved cleanly on $\mathcal{S}(\mathbb{R}^d)$ (Ch 6, Thm 2.4). This is the ambient transform for the plane.
2. **Convolution theorem** $\widehat{f * g} = \hat f \hat g$ on $\mathbb{R}^d$ (Ch 6, Step 4). The autocorrelation $f * \tilde f$ has Fourier transform $|\hat f|^2 \geq 0$, the seed of all positivity arguments.
3. **Radial $\Rightarrow$ radial**: $\hat f$ of a radial function is radial (Ch 6, Cor 2.3), via rotation-invariance $\hat f(R\xi)=\hat f(\xi)$ (Prop 2.1 (vi)). **This is exactly where $O(2)$ enters.**
4. **The $d=2$ Hankel formula** $F_0(\rho) = 2\pi \int_0^\infty J_0(2\pi r\rho)\, f_0(r)\, r\, dr$ (Ch 6, eq (11)): the FT of a radial function on the plane is a Bessel-$J_0$ transform. $J_0$'s zeros are the spectral data A2 exploits.
5. **Bessel function** $J_0$ defined as a Fourier coefficient of $e^{i\rho\sin\theta}$ (Ch 6, sec 4), so its appearance is forced by averaging $e^{2\pi i x\cdot\xi}$ over the unit circle $S^1$.
6. **Poisson summation formula** $\sum f(n) = \sum \hat f(n)$ on $\mathcal{S}(\mathbb{R})$ (Ch 5, Thm 3.1), the lattice / periodization tool behind density-on-a-lattice and LP-duality arguments.
7. **Parseval / Plancherel on $S^1$** (Ch 3, Thm 1.3) and on $\mathbb{R}$ (Ch 5, Thm 1.12): the $L^2$ isometries that turn "no two points at unit distance" into a constraint on $\hat f$ supported off the unit-circle frequencies.
8. **Finite abelian group Fourier analysis** (Ch 7): the exact discrete analogue used when A2 discretizes the plane to a finite Cayley-type graph and runs an LP / SDP (mirrors the L35/L36 measurable experiments).
9. **Gaussian is its own transform** and **good kernels / approximate identities** (Ch 5-6): the mollification that lets you pass between the rigorous-but-restrictive $\mathcal{S}$ statements and the indicator functions of measurable colorings.
10. **What is NOT here**: Bochner's theorem on positive-definite functions, the FT of singular measures (the unit-circle measure $\sigma_{S^1}$ as a tempered distribution), and $L^2$ Plancherel without smoothness. A2's full bound needs those from Vol III / BDOV.

---

## The Fourier route to $\chi_m(\mathbb{R}^2) \geq k$

This section reconstructs the standard density / autocorrelation argument **from the tools proved in this book**, and marks where each piece is rigorous here versus where it needs the heavier machinery the book defers to Vol III. The full research-strength version (the Lovász-$\vartheta$-style SDP and the Hoffman / ratio bound for the infinite unit-distance graph) is in **Bachoc-De Corte-Oliveira-Vallentin** (a separate text in this library). The job here is to map the *foundations* to that argument.

### Setup

The unit-distance graph $G$ on $\mathbb{R}^2$ has vertex set $\mathbb{R}^2$ and an edge between $x,y$ iff $|x-y|=1$. A **measurable independent set** $A \subseteq \mathbb{R}^2$ is a (Lebesgue) measurable set containing no two points at distance exactly $1$. If $\mathbb{R}^2$ can be colored with $k$ measurable color classes, at least one class has upper density $\geq 1/k$, so an upper bound $\delta^*$ on the density of any measurable independent set forces

$$\chi_m(\mathbb{R}^2) \geq \frac{1}{\delta^*}.$$

The whole A2 program is: make $\delta^*$ small. (Falconer 1981 already gives $\chi_m \geq 5$, i.e. $\delta^* < 1/4$; the L35/L36 repo experiments reproduce an LP crossing $\chi_m \geq 5$; the frontier is $\geq 6$.)

### Step 1: encode "no unit distance" as a Fourier support condition

Let $f = \mathbf{1}_A$ (smoothed by a good kernel $K_\delta$ so that the rigorous $\mathcal{S}$-statements of this book apply; the Gaussian family $K_\delta(x)=\delta^{-d/2}e^{-\pi|x|^2/\delta}$ is the canonical approximate identity, Ch 6 Step 2). The **autocorrelation**

$$g(x) = (f * \tilde f)(x), \qquad \tilde f(x) = \overline{f(-x)},$$

satisfies, by the convolution theorem on $\mathbb{R}^2$ (Ch 6, Step 4: $\widehat{f*g}=\hat f\hat g$),

$$\hat g(\xi) = |\hat f(\xi)|^2 \geq 0.$$

Nonnegativity of $\hat g$ is the only positivity input the book itself supplies; it is the elementary precursor of Bochner's theorem (which the book does *not* prove). The independence condition $A \cap (A+u)=\varnothing$ for all $|u|=1$ says $g(u)=0$ whenever $|u|=1$: the autocorrelation **vanishes on the unit circle**.

### Step 2: average over the unit circle, where $O(2)$ and $J_0$ enter

Integrate the relation $g(u)=0$ against the uniform probability measure $\sigma$ on the unit circle $S^1$. Define the **rotational average** of $g$. Because $\sigma$ is $O(2)$-invariant, its Fourier transform is radial, and on $\mathbb{R}^2$ the FT of a radial object is the Bessel-$J_0$ transform (Ch 6, eq (11)):

$$\hat\sigma(\xi) = \int_{S^1} e^{-2\pi i \xi\cdot\gamma}\, d\sigma(\gamma) = J_0(2\pi|\xi|).$$

This is the exact 2D analogue of Lemma 3.5 (which the book proves for $S^2$: $\frac{1}{4\pi}\int_{S^2}e^{-2\pi i\xi\cdot\gamma}d\sigma = \frac{\sin 2\pi|\xi|}{2\pi|\xi|}$, line 10954). The book *defines* $J_0$ precisely as the angular average $J_0(\rho)=\frac{1}{2\pi}\int_0^{2\pi}e^{i\rho\sin\theta}d\theta$ (Ch 6, sec 4, line 11371), so $J_0$ is **literally the Fourier transform of the unit-vector measure on $S^1$**. The constraint becomes, via Parseval/Plancherel (Ch 5 Thm 1.12, extended to $\mathbb{R}^2$ in Ch 6 Thm 2.4),

$$0 = \int_{S^1} g(u)\, d\sigma(u) = \int_{\mathbb{R}^2} |\hat f(\xi)|^2\, J_0(2\pi|\xi|)\, d\xi.$$

**Wrong-approach detector check.** This is the rotational/2D structure the A2 detector demands. The measure $\sigma$ lives on the *circle* of unit vectors $S^1\subset\mathbb{R}^2$; its transform $J_0$ is genuinely 2-dimensional. On $\mathbb{R}^1$ the unit "sphere" $S^0=\{+1,-1\}$ gives instead $\hat\sigma_{1D}(\xi)=\cos(2\pi\xi)$ (the $d=1$ formula, Ch 6 eq (9): $F_0(\rho)=2\int_0^\infty\cos(2\pi\rho r)f_0(r)dr$), whose first zero / oscillation pattern allows density $1/2$ and forces only $\chi_m(\mathbb{R})=2$. An argument that used only 1D translation (the $\cos$ structure) and never the circular average $J_0$ would constrain $\chi(\mathbb{R}^1)=2$ and is therefore structurally wrong for the plane. The bound MUST go through $J_0$, i.e. through the full $S^1$ measure. **This is the load-bearing $O(2)$ step.** Flagged and satisfied.

### Step 3: the LP / ratio (Hoffman-type) bound

Now choose a test function. The Turing / Delsarte LP setup: pick $h$ with $\hat h \geq 0$, $\hat h$ supported so that the autocorrelation constraint $\int |\hat f|^2 J_0(2\pi|\xi|)\,d\xi=0$ can be combined with $\hat g(0)=\|f\|_1^2 = (\mathrm{density})^2\cdot\mathrm{vol}$ and $g(0)=\|f\|_2^2=\mathrm{density}\cdot\mathrm{vol}$ to bound the density. Concretely one seeks coefficients turning the problem into:

> maximize the density $\delta$ subject to $\hat g(\xi)\geq 0$ everywhere, $g\equiv 0$ on $\{|u|=1\}$, $g(0)=\delta$, $\int g = \delta^2$ (up to normalization).

The spectral content is the **eigenvalue / Hoffman ratio bound** for the (infinite) unit-distance graph: if $m$ is the minimum and $M$ the maximum of the "spectrum" of the convolution operator $f\mapsto f*\sigma_{S^1}$ (whose symbol is exactly $J_0(2\pi|\xi|)$ by Step 2), then the independence-set density is bounded by the Hoffman-style ratio

$$\delta^* \leq \frac{-m}{M-m},$$

where $m=\min_\xi J_0(2\pi|\xi|)\approx -0.4028$ (the first, deepest minimum of $J_0$, attained at the first zero region of $J_1$) and $M=J_0(0)=1$. This gives the cruder $\delta^* \leq 0.4028/1.4028 \approx 0.287$, hence $\chi_m\geq 1/0.287 \approx 3.5$, i.e. $\geq 4$. The sharper Falconer / LP refinements push $\delta^*<1/4$ ($\chi_m\geq 5$). **Why $J_0$'s zeros matter**: the operator $f*\sigma_{S^1}$ acts on the frequency $\xi$ by multiplication by $J_0(2\pi|\xi|)$; its negative eigenvalues sit at the frequencies where $J_0<0$ (between its zeros $j_{0,1}\approx 2.405$, $j_{0,2}\approx 5.520$, ...), and the most negative value $m$ controls the ratio bound. Smaller (more negative) accessible $m$, or a cleverer multi-distance / SDP test, lowers $\delta^*$ and raises $\chi_m$.

### Where this book stops, and what BDOV adds

- **This book** rigorously gives: the transform, inversion, Plancherel, convolution theorem on $\mathbb{R}^2$; the radial$\to J_0$ Hankel formula; $\hat\sigma=J_0$ in spirit (proved for $S^2$, stated method works for $S^1$); Poisson summation for lattice versions; and $\hat g=|\hat f|^2\geq 0$.
- **This book does NOT give**: Bochner's theorem (positive-definite $\Leftrightarrow$ nonnegative-measure transform), the FT of $\sigma_{S^1}$ as a genuine tempered distribution/measure (only the smooth-function prototype), or the $L^2$ Plancherel for indicators without mollification. Those are Vol III.
- **BDOV (Bachoc-De Corte-Oliveira-Vallentin)** supplies: the measure-theoretic / SDP formulation, the Lovász-$\vartheta'$ bound for $\mathbb{R}^n$ unit-distance graphs, the multi-distance LP that beats the single-$J_0$ ratio bound, and the rigorous treatment of the surface measure. The notes here are the *foundations* those papers assume.

---

## Chapter-level notes

### Ch 1. The Genesis of Fourier Analysis
Vibrating string and heat equation derivations; separation of variables; steady-state heat in the disc. Motivational; no A2 tool, but the heat-kernel theme recurs (and Gaussians = heat kernels are the A2 mollifier).

### Ch 2. Basic Properties of Fourier Series
Definitions of Fourier coefficients $a_n=\frac{1}{2\pi}\int f e^{-in\theta}$; **convolutions on $S^1$** and the convolution-multiplies-coefficients identity; **good kernels / approximate identities** (sec 4); Cesaro / Fejer and Abel summability; Poisson kernel on the disc. The good-kernel machinery is the prototype of the mollification A2 uses to legalize indicator functions.

### Ch 3. Convergence of Fourier Series
Inner-product / Hilbert-space framing on $S^1$. **Parseval's identity** (Thm 1.3 (ii), line 4574): for integrable $f\sim\sum a_n e^{in\theta}$,
$$\sum_{n=-\infty}^{\infty}|a_n|^2 = \frac{1}{2\pi}\int_0^{2\pi}|f(\theta)|^2\,d\theta.$$
Bessel's inequality $\sum|a_n|^2\leq\|f\|^2$ for any orthonormal family (line 4588). Bilinear Parseval (Lemma 1.5, line 4623): $\frac{1}{2\pi}\int F\overline G = \sum a_n\overline{b_n}$. Riemann-Lebesgue lemma. *A2 use*: the $L^2$ isometry; the discrete model for the finite-graph LP.

### Ch 4. Some Applications of Fourier Series
Isoperimetric inequality; Weyl equidistribution; a continuous nowhere-differentiable function; heat equation on the circle. Brief; equidistribution is conceptually adjacent to density arguments but not directly used.

### Ch 5. The Fourier Transform on $\mathbb{R}$
- **Definition** (eq (3), line 7367): $\hat f(\xi)=\int_{-\infty}^\infty f(x)e^{-2\pi i x\xi}dx$.
- **Schwartz space** $\mathcal{S}(\mathbb{R})$: smooth, rapidly decreasing; FT maps $\mathcal{S}\to\mathcal{S}$.
- **Fourier inversion** (eq (4)): $f(x)=\int \hat f(\xi)e^{2\pi i x\xi}d\xi$ for $f\in\mathcal{S}$.
- **Convolution** (Prop 1.11, line 8068): $f*g\in\mathcal{S}$, commutative, and $\widehat{f*g}(\xi)=\hat f(\xi)\hat g(\xi)$.
- **Plancherel** (Thm 1.12, line 8145): for $f\in\mathcal{S}(\mathbb{R})$, $\|\hat f\| = \|f\|$ in $L^2$. Extends to moderate-decrease $f$ with $\hat f$ also of moderate decrease (sec 1.7).
- **Heat / steady-state heat** applications; Gaussian $\widehat{e^{-\pi x^2}}=e^{-\pi\xi^2}$.
- **Poisson summation formula** (Thm 3.1, line 8748): for $f\in\mathcal{S}(\mathbb{R})$,
  $$\sum_{n\in\mathbb{Z}}f(x+n)=\sum_{n\in\mathbb{Z}}\hat f(n)e^{2\pi i n x},\quad\text{in particular}\quad\sum_n f(n)=\sum_n\hat f(n).$$
  Hypotheses: $f\in\mathcal{S}$; extends to $f,\hat f$ both of moderate decrease (line 8808). Applications: theta-function functional equation $s^{-1/2}\vartheta(1/s)=\vartheta(s)$ (Thm 3.2), heat kernel on circle = periodization of heat kernel on $\mathbb{R}$ (Thm 3.3), Poisson kernel relation (Thm 3.5).
- **Heisenberg uncertainty** (Thm 4.1, line 8991): $(\int x^2|\psi|^2)(\int\xi^2|\hat\psi|^2)\geq\frac{1}{16\pi^2}$ for normalized $\psi\in\mathcal{S}$.

*A2 use*: Plancherel and the convolution theorem are the $\mathbb{R}$-prototypes; Poisson summation is the lattice tool for periodized colorings and for LP-duality bounds on lattice sub-graphs.

### Ch 6. The Fourier Transform on $\mathbb{R}^d$ (the core A2 chapter)
- **Definition**: $\hat f(\xi)=\int_{\mathbb{R}^d}f(x)e^{-2\pi i x\cdot\xi}dx$ (line 10380); inner product replaces the scalar product.
- **Properties** (Prop 2.1, line 10388): translation/modulation/dilation/differentiation rules, and crucially **(vi)** $f(Rx)\to\hat f(R\xi)$ for any rotation $R$, proved via $|\det R|=1$ and $R^{-1}y\cdot\xi = y\cdot R\xi$ (line 10402). **This is the $O(2)$-equivariance of the FT.**
- **Radial functions** (line 10428): $f$ radial $\Leftrightarrow$ $f(Rx)=f(x)$ for all rotations. **Cor 2.3**: the FT of a radial function is radial (line 10440), directly from (vi).
- **Inversion + Plancherel on $\mathbb{R}^d$** (Thm 2.4, line 10450): $f(x)=\int\hat f(\xi)e^{2\pi i x\cdot\xi}d\xi$ and $\int|\hat f|^2=\int|f|^2$. Proof via Gaussian good kernels $K_\delta(x)=\delta^{-d/2}e^{-\pi|x|^2/\delta}$ (Steps 1-2), multiplication formula (Step 3), convolution theorem $\widehat{f*g}=\hat f\hat g$ (Step 4, line 10550).
- **Surface measure FT** (Lemma 3.5, line 10954): $\frac{1}{4\pi}\int_{S^2}e^{-2\pi i\xi\cdot\gamma}d\sigma(\gamma)=\frac{\sin 2\pi|\xi|}{2\pi|\xi|}$. The 3D instance of "FT of the unit-sphere measure"; the same averaging-over-the-sphere method gives the 2D ($J_0$) case.
- **Radial symmetry and Bessel functions** (sec 4, line 11306):
  - $d=1$: $F_0(\rho)=2\int_0^\infty\cos(2\pi\rho r)f_0(r)dr$ (eq (9)).
  - $d=3$: $F_0(\rho)=2\rho^{-1}\int_0^\infty\sin(2\pi\rho r)f_0(r)r\,dr$ (eq (10)).
  - **$d=2$ (the plane): $F_0(\rho)=2\pi\int_0^\infty J_0(2\pi r\rho)f_0(r)r\,dr$** (eq (11), line 11391). This is the **Hankel transform of order 0**; it is the radial-profile relation A2 lives on.
  - **Bessel function** $J_n(\rho)=\frac{1}{2\pi}\int_0^{2\pi}e^{i\rho\sin\theta}e^{-in\theta}d\theta$ (line 11371), so $e^{i\rho\sin\theta}=\sum_n J_n(\rho)e^{in\theta}$. General $d$: order $d/2-1$; even $d$ uses integer-order Bessel (Problem 2).
- **Radon / X-ray transform** (sec 5): tomography. Not A2-central.

*A2 use*: this entire chapter. The $d=2$ Hankel/$J_0$ formula plus rotation-equivariance plus Plancherel-on-$\mathbb{R}^2$ are precisely the foundations of the autocorrelation/density bound reconstructed above.

### Ch 7. Finite Fourier Analysis
Fourier analysis on $\mathbb{Z}(N)$ (Fourier inversion + Parseval-Plancherel on $\mathbb{Z}(N)$, sec 1.2); the FFT; characters of finite abelian groups, orthogonality relations, completeness, and the **finite Parseval-Plancherel formula** (sec 2.5, line 13466). *A2 use*: the exact discrete model for when the plane (or a lattice quotient) is replaced by a finite Cayley graph and the density bound becomes a finite LP / SDP. This is the mathematics underneath the repo's L35/L36 `experiments/measurable/` LP that crosses $\chi_m\geq 5$: a finite-group Fourier diagonalization of the (circulant) constraint matrix.

### Ch 8. Dirichlet's Theorem
Primes in arithmetic progressions via characters mod $q$ and $L$-functions. Number-theoretic; no A2 tool. (Of tangential interest: the character / $L$-function machinery is the spiritual cousin of the zeta repo's wrong-approach-detector framing, but it is not used here.)

---

## Discrepancy log

No direct conflicts with the atlas. Two clarifications to flag for SYNTHESIZER:

1. **Positive-definiteness / Bochner.** The CLAUDE framing says the A2 "spectral/SDP bound rests on Bochner-type positive-definiteness." **Bochner's theorem is NOT in this volume.** The book supplies only the elementary nonnegativity $\widehat{f*\tilde f}=|\hat f|^2\geq 0$. Any atlas citation that points to Stein-Shakarchi Vol I for "positive-definite functions / Bochner" should be redirected to Vol III or to a dedicated harmonic-analysis source (Rudin, *Fourier Analysis on Groups*) or to BDOV. Flagged, not resolved.

2. **The $\hat\sigma_{S^1}=J_0$ identity** is presented here only as the radial Hankel formula (eq (11)) and via the $S^2$ surface-measure lemma (Lemma 3.5), not as a standalone "Fourier transform of the unit-circle measure" theorem. The clean measure-valued statement (and its decay $J_0(r)\sim\sqrt{2/\pi r}\cos(\cdot)$) is assumed by A2 but must be cited from elsewhere. Noted so downstream agents do not over-claim what Vol I proves.

---

## References to follow up

Cited / adjacent (for the A2 chain), in this library unless noted:
- **Bachoc, De Corte, Oliveira, Vallentin** (separate text in this library): the research-strength SDP / $\vartheta'$ bound for $\mathbb{R}^n$ unit-distance graphs; the multi-distance LP; rigorous surface-measure treatment. **The direct sequel to these notes.**
- **Stein-Shakarchi Vol III, *Real Analysis*** (NOT in library): $L^2$ Plancherel, tempered distributions, FT of measures, the rigorous home of Step 1's mollification removal.
- **Falconer 1981**: $\chi_m(\mathbb{R}^2)\geq 5$; the prototype density bound this Fourier route reproduces and sharpens.
- **Soifer 2009, *Mathematical Coloring Book*** (in library): historical/structural context for $\chi_m$ vs $\chi$.
- **Rudin, *Fourier Analysis on Groups*** (NOT in library): canonical source for Bochner's theorem and positive-definite functions, the gap flagged above.
- Internal: `experiments/measurable/` (L35/L36 LP), `experiments/_shared/wrong_approach_detectors.py` (the $\mathbb{R}^1$ / $J_0$ control checked in Step 2).

---

## What this enables / what remains open

**Enables (for BUILDER / ADVERSARY / SYNTHESIZER):**
- A rigorous, citeable foundation for every analytic step in the autocorrelation/density bound on $\chi_m(\mathbb{R}^2)$: transform, inversion, Plancherel, convolution theorem on $\mathbb{R}^2$, and the radial-to-$J_0$ Hankel formula. BUILDER can write the single-distance ratio bound ($\delta^*\leq -m/(M-m)$ with $m=\min J_0$) with confidence in the foundations.
- A precise statement of where $O(2)$ / 2D structure enters (Step 2, via $\hat\sigma_{S^1}=J_0$), satisfying the A2 wrong-approach detector. ADVERSARY should check any proposed A2 bound actually routes through $J_0$ and not merely 1D $\cos$ structure.
- The finite-group Fourier dictionary (Ch 7) underwriting the repo's finite-LP $\chi_m\geq 5$ crossing.

**Remains open / not in this book (hand to Vol III + BDOV):**
- Bochner's theorem and the positive-definite-function / SDP formulation: NOT here. Needed for the Lovász-$\vartheta$ upgrade that could push $\chi_m\geq 6$.
- The FT of singular measures (the unit-circle measure as a tempered distribution); the rigorous removal of the Schwartz-space mollification on indicators.
- The multi-distance / multi-frequency LP that beats the single-$J_0$ ratio bound: this is the live continuous-progress frontier for A2 while A1 is stuck on the missing $\chi\geq 6$ embeddable UDG. The analytic tools to *sharpen* the bound (better test functions, more circle-measure constraints) are foundationally supported here; the optimization is BDOV/experiment territory.
