# Ambrus, Csiszarik, Matolcsi, Varga, Zsamboki (2023): The Density of Planar Sets Avoiding Unit Distances

Source: `sources/papers/Ambrus-...-2207.14179.pdf`, extracted text at `sources/_extracted/Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki-2023-Density-of-Planar-Sets-Avoiding-Unit-Distances_arXiv-2207.14179.txt`. arXiv:2207.14179v3 [math.MG], 28 Jul 2023. Architecture 2/3 (measurable / fractional-spectral).

## Executive summary (8 lines)

1. Main theorem (Thm 1): every Lebesgue measurable, 1-avoiding planar set has upper density at most $0.2470$; the numerical LP optimum is $0.24697$ and the rigorous dual-certified bound is $0.24699\ldots < 0.2470$. This proves Erdos's conjecture $m_1(\mathbb{R}^2) < 1/4$.
2. Consequence: $\chi_m(\mathbb{R}^2) \geq 1/m_1(\mathbb{R}^2) > 4$, hence $\chi_m(\mathbb{R}^2) \geq 5$ as an integer (an alternative to Falconer 1981). Four colors cover at most $0.988$ of the plane.
3. Method: a common generalization of (a) the fractional-chromatic-number route and (b) the autocorrelation harmonic-analysis LP route. The unifier is the full inclusion-exclusion (IE) formula on a point configuration $X$, with no loss.
4. The key new ingredient over 2015/2022 work is the inclusion-exclusion CONGRUENCE constraints (ieC / IEC): O(2)-averaging the IE identity over congruent sub-configurations of $X$ couples atom densities of isometric index sets.
5. Atoms $a_X(\varepsilon)$ are densities of Venn-diagram cells of $\{A - x_i\}$; non-independent atoms vanish; the LP variables are independent atoms plus Fourier frequency masses $\kappa(t)$.
6. The winning configuration is $X_{23}$: 23 points, found by beam search seeded at the Moser spindle, living in the Moser-spindle ring (field $\mathbb{Q}(\sqrt{3}, \sqrt{11})$); 27 distinct pairwise distances.
7. LP size: 13552 atom variables, 12000 Fourier variables (25552 total), 6099 equality constraints (23 IE1, 206 IE2, 5868 IEC), solved by Mosek/Gurobi in under 30 s.
8. Repo reproduction L35/L36 (`experiments/fractional/e3i`, `e3j`): self-certified $m_1 \leq 0.246894$, dual-certified $0.246997$; $X_{23}$ has 47 unit edges and 27 distinct distances. Constants cross-checked below; no discrepancy.

---

## Template for the multi-class IEC (for e3k)

This is the load-bearing section for the active experiment `experiments/fractional/e3k_multiclass_lp.py` (LEARNINGS L38). The single-class LP is provably capped at $\chi_m \geq 5$ (Croft floor $m_1 \geq 0.22936 > 1/5$). The route to $\geq 6$ is the JOINT k-coloring LP, and that LP currently lacks the congruence constraints that drove the single-class 2015->2023 crossing. Below is the precise generalization.

### What the single-class IEC is (precise, see the detailed notes for full derivation)

For a config $X = \{x_1, \ldots, x_n\}$, an atom is indexed by a sign vector $\varepsilon \in \{\pm 1\}^n$, where $\varepsilon_i = 1$ means "in $A - x_i$" and $-1$ means "in the complement". $a_X(\varepsilon) = \delta\big(\bigcap_i (A - x_i)^{\varepsilon_i}\big)$ is the density of that Venn cell. For an index set $I \subset [n]$, $\sigma(n; I) = \{\varepsilon : \varepsilon|_I = 1\}$, and by inclusion-exclusion $\delta(\bigcap_{i \in I}(A - x_i)) = \sum_{\varepsilon \in \sigma(n;I)} a_X(\varepsilon)$. After O(2)-averaging (replace $a_X$ by $\mathring a_X$), for every congruent pair $\{I, J\} \in C(X)$ (i.e. $X|_I \cong X|_J$ as point sets, related by an isometry):

$$\sum_{\varepsilon \in \sigma(n;I)} \mathring a_X(\varepsilon) = \sum_{\varepsilon \in \sigma(n;J)} \mathring a_X(\varepsilon). \quad \text{(ieC / IEC)}$$

Validity: $\delta(\bigcap_{i\in I}(A - x_i))$ depends only on the congruence class of $X|_I$ (translation invariance of density plus the O(2) average over the fixed set $A$). So congruent index sets have equal "intersection density", and that equality is exactly the difference of two atom-sums.

### The multi-class object (matches e3k's current skeleton)

A measurable proper $k$-coloring partitions $\mathbb{R}^2$ into 1-avoiding classes $A_1, \ldots, A_k$. Fix $X$. The translation-induced local pattern is a map $\sigma: [n] \to [k]$ (which color each $x + x_i$ lands in). Define the pattern density

$$a_\sigma = \delta\big(\{x : x + x_i \in A_{\sigma(i)} \text{ for all } i \in [n]\}\big).$$

$a_\sigma = 0$ unless $\sigma$ is a proper coloring of $G(X)$ (unit-distance pairs need distinct colors). Constraints already in e3k: $\sum_\sigma a_\sigma = 1$ (N); per-color $f_c(0) = \sum_{\sigma:\sigma(x_1)=c} a_\sigma$ (D); per-color pair-marginal $f_c(x_i - x_j) = \sum_{\sigma:\sigma(i)=\sigma(j)=c} a_\sigma$ coupled to a per-color Bochner expansion (P); per-color $f_c(1) = 0$ (A).

### The MISSING piece: multi-class IEC, two equivalent formulations

The multi-class generalization of the IE atoms is a JOINT Venn diagram. Instead of $\varepsilon \in \{\pm1\}^n$ (in/out of one set), the atom index is the full color pattern $\sigma \in [k]^n$, and $a_\sigma$ is exactly the joint-occupancy density above. The single-class atom $a_X(\varepsilon)$ is recovered for color $c$ by marginalizing: $a^{(c)}_X(\varepsilon) = \sum_{\sigma} [\sigma(i) = c \iff \varepsilon_i = 1]\, a_\sigma$. So the multi-class LP already carries strictly more information than $k$ separate single-class LPs; the IEC is what activates it.

There are two ways to add IEC, and BUILDER should implement BOTH (they are not equivalent in strength):

FORMULATION 1 (per-color marginal IEC; the conservative, definitely-valid one). For each color $c \in [k]$ and each congruent pair $\{I, J\} \in C(X)$, impose

$$\sum_{\sigma: \sigma|_I = c} a_\sigma = \sum_{\sigma: \sigma|_J = c} a_\sigma \qquad \text{for every } \{I,J\} \in C(X),\ c \in [k],$$

where $\sigma|_I = c$ means $\sigma(i) = c$ for all $i \in I$ (the whole sub-config $X|_I$ is monochromatic color $c$). Justification: $\sum_{\sigma:\sigma|_I=c} a_\sigma = \delta(\bigcap_{i\in I}(A_c - x_i))$ is the single-class intersection density for class $A_c$, and the single-class IEC argument applies verbatim to each $A_c$ (each is a fixed measurable set, O(2)-average over the same Haar measure). This is the literal per-color lift of (ieC). It is exactly the constraint family whose single-class analog took the LP from $0.2584$ (no IEC) to $< 1/4$ (with IEC) in L36. CONCRETE COUNT: for $X_{23}$, the single-class had 5868 IEC constraints, so the per-color version contributes up to $5868 \times k$ constraints (most prunable: only patterns that are monochromatic-feasible on $X|_I$, i.e. $X|_I$ independent, contribute a nonzero side).

FORMULATION 2 (full joint-pattern IEC; stronger, the genuine multi-class generalization). The single-class IE identity says intersection densities depend only on the congruence class of the index set. The multi-class analog: for any COLORED sub-configuration, the density depends only on the congruence class of the colored point set. Precisely, for a congruent pair $\{I, J\}$ with witnessing isometry $\varphi$ ($X|_J = \varphi(\tau(X|_I))$) and a fixed local color assignment $\rho: I \to [k]$ transported to $\rho': J \to [k]$ along $\varphi$ (so $\rho'(\varphi(\tau(x_i))) = \rho(x_i)$), impose

$$\sum_{\sigma: \sigma|_I = \rho} a_\sigma = \sum_{\sigma: \sigma|_J = \rho'} a_\sigma.$$

Justification: $\sum_{\sigma:\sigma|_I = \rho} a_\sigma = \delta(\bigcap_{i\in I}(A_{\rho(i)} - x_i))$ is the joint density of the colored sub-config; O(2)-averaging the fixed coloring over the orthogonal group makes it depend only on the congruence type of the colored point set, AND on the multiset of color labels carried by congruent points. Validity caveat for BUILDER: this requires that the isometry $\varphi$ is a SYMMETRY of the colored pattern, i.e. it maps the labeling $\rho$ to a labeling $\rho'$ consistently. The correct enumeration is over pairs $(\{I,J\}, \rho)$ where $\rho$ is any coloring of $X|_I$ (proper or not, since complement/other-color cells are allowed) and $\rho'$ is its $\varphi$-transport. Formulation 1 is the special case $\rho \equiv c$ (constant). Formulation 2 also includes mixed patterns like "$x_i$ red, $x_j$ blue" being congruence-coupled, which Formulation 1 cannot express.

### Why Formulation 2 is the real prize, and the subtlety

The single-class IEC only ever sees one set $A$, so its only congruence statement is "monochromatic intersection densities match". The multi-class problem has cross-color structure (a red point next to a blue point), and the chromatic obstruction past 5 is expected to live in the cross-color correlations, not the per-color ones. Formulation 1 alone will likely reproduce $\chi_m \geq 5$ (it is $k$ parallel copies of the L36 certificate) but is unlikely to reach $\geq 6$. Formulation 2 is the one that could bite at $k = 5$. SUBTLETY to flag for VERIFIER: O(2)-averaging a colored configuration is only valid if the same Haar-random isometry is applied to the WHOLE plane (all colors rotate together). This is exactly the averaging heuristic in the paper (Section 4 Remark: tile into $Q \times Q$ squares, apply an independent random O(2) element per square). It holds for any fixed partition $\{A_c\}$, so Formulation 2 is valid. The one thing to check is the transport map $\rho \mapsto \rho'$: when $X|_I$ has nontrivial self-congruences, the same atom-sum can be written multiple ways; dedupe to avoid redundant (and over-tight) constraints.

### Concrete implementation checklist for e3k

1. Replace the per-color marginal variables with the joint pattern variables $a_\sigma$ over proper colorings $\sigma$ of $G(X)$ (e3k already enumerates these).
2. Enumerate $C(X)$: all unordered pairs $\{I, J\}$ of index subsets with $X|_I \cong X|_J$. Reuse the single-class enumerator from `e3j_iec_selfcertify.py` (it already builds $C(X)$ for $X_{23}$). Restrict to $|I| \leq 5$ initially (L36 found size $\leq 5$ already saturates the single-class $X_{23}$ LP).
3. Add Formulation 1 constraints first (cheap, definitely valid, sanity check: k=4 on $X_{23}$ should be infeasible reproducing $\geq 5$).
4. Add Formulation 2 constraints for $|I| = 2$ and $|I| = 3$ (pairs and triangles) with all color labelings $\rho$. This is where new strength enters.
5. Keep the Bochner per-color positive-definite constraints (P)/(A): they are the analog of (IE2)+(C0) tying color marginals to a valid radial autocorrelation. The IEC constraints are PURELY on the $a_\sigma$ variables (they never touch $\kappa$/$\nu$), so they slot in independently of the Fourier block.
6. Scaling: the proper-coloring enumeration over $k^n$ explodes. The principled replacement is the de Laat-Vallentin / DeCorte-Oliveira-Vallentin moment hierarchy over pairwise color marginals; the IEC constraints become linear constraints on the degree-$|I|$ moments. See note 08.

---

## Detailed structured notes

### 1. Setup and main result (Section 1)

- $m_1(\mathbb{R}^d) = \sup\{\delta(A) : A \subset \mathbb{R}^d$ 1-avoiding, measurable$\}$ (eq. 1). Connection: $\chi_m(\mathbb{R}^d) \geq 1/m_1(\mathbb{R}^d)$.
- Lower bounds on $m_1(\mathbb{R}^2)$: hexagonal discs of radius $1/2$ give $\pi/(8\sqrt3) \approx 0.2267$; Croft's tortoise (disc of radius $1/2$ intersected with a hexagon of height $x = 0.96553$, on a hex lattice with basis length $1+x$) gives $m_1 \geq 0.22936$. No better construction known.
- Upper-bound history: $\alpha(M_7)/|M_7| = 2/7 \approx 0.2857$ (Moser spindle independence ratio); Szekely 1984 $12/43 \approx 0.2791$; de Oliveira-Vallentin 2010 $0.2684$ (three regular triangles); Keleti-Matolcsi-Oliveira-Ruzsa 2016 $0.2588$; Ambrus-Matolcsi 2022 $0.2544$ (triple correlations); Bellitto-Pecher-Sedillot 2018 $0.2565$ via $\chi_f(G) \geq 3.8991$ on 607 vertices; Parts 2022 (unpublished) $\chi_f \geq 3.9898$ on 1057 vertices. This paper: $0.2470$.
- Theorem 1: any Lebesgue measurable 1-avoiding planar set has upper density $\leq 0.2470$.

### 2. Inclusion-exclusion constraints (Section 2, Lemma 1) -- ties to repo e3g

Notation: $[n] = \{1,\ldots,n\}$; $\sigma(n) = \{\pm1\}^n$; $I(\varepsilon) = \{i : \varepsilon_i = 1\}$; $\sigma(n; I) = \{\varepsilon : \varepsilon|_I = 1\}$. For $Y \subset \mathbb{R}^2$, $Y^1 = Y$, $Y^{-1} = Y^c$. For $X = \{x_1,\ldots,x_n\}$ and $\varepsilon \in \sigma(n)$:

$$a_X(\varepsilon) = \delta\Big(\bigcap_{i=1}^n (A - x_i)^{\varepsilon_i}\Big) \quad \text{(eq. 5)}.$$

Atoms are Venn-diagram cells of $\{A - x_i\}$. IE identity (eq. 6): for nonempty $I$, $\delta(\bigcap_{i\in I}(A-x_i)) = \sum_{\varepsilon \in \sigma(n;I)} a_X(\varepsilon)$. Non-independent atoms vanish: $a_X(\varepsilon) = 0$ if $I_X(\varepsilon)$ contains a unit-distance pair.

Lemma 1 (inclusion-exclusion constraints) on $\{a_X(\varepsilon)\}$:
- (ieP) $a_X(\varepsilon) \geq 0$.
- (ieI) $a_X(\varepsilon) = 0$ if $I_X(\varepsilon)$ contains two points at unit distance.
- (ieT) $\sum_{\varepsilon} a_X(\varepsilon) = 1$ (total density of plane is 1).
- (ie1) $\sum_{\varepsilon \in \sigma(n;i)} a_X(\varepsilon) = f(0) = \delta(A)$ for every $i$.
- (ie2) $\sum_{\varepsilon \in \sigma(n;i,j)} a_X(\varepsilon) = f(x_i - x_j)$ for every pair $\{i,j\}$.

Here $f(x) = \delta(A \cap (A - x))$ is the autocorrelation, $f(0) = \delta(A)$, and $f(x) = 0$ for unit vectors $x$ (eq. 3). Dividing by $\delta(A)$ ($\tilde a_X(\varepsilon) = a_X(\varepsilon)/\delta(A)$) gives a lower bound on $1/\delta(A)$ via the LP (7): minimize $\sum_\varepsilon \tilde a_X(\varepsilon)$ subject to (ieP), (ieI), and $\sum_{\varepsilon \in \sigma(n;i)} \tilde a_X(\varepsilon) = 1$. This is the repo's `e3g_ambrus_ie_lp.py` core.

### 3. Fractional chromatic number (Section 3, Lemma 2, Corollaries 1-2)

- Definition 1: $\chi_f(G) = \min \sum_S \gamma(S)$ over independent-set weights with $\sum_{S \ni x} \gamma(S) \geq 1$ per vertex. $\chi_f(M_7) = 7/2$.
- Lemma 2: equality $\sum_{S \ni x}\gamma(S) = 1$ may be required without changing $\chi_f$.
- Corollary 1: the LP (7) equals $\chi_f(G)$ via $\tilde a_X(\varepsilon) = \gamma(I_X(\varepsilon))$. So $1/\delta(A) \geq \chi_f(G)$, $m_1(\mathbb{R}^2) \leq 1/\chi_f(G) \leq 1/\chi_f(\mathbb{R}^2)$.
- Definition 2: geometric fractional chromatic number $\chi_{gf}(G)$ adds the congruence constraint $\sum_{S \subset T}\gamma(T) = \sum_{S'\subset T'}\gamma(T')$ for congruent $\{S,S'\} \in C(X)$. $\chi_{gf}(G) \geq \chi_f(G)$.
- Corollary 2: $1/\delta(A) \geq \chi_{gf}(G)$, so $m_1 \leq 1/\chi_{gf}(\mathbb{R}^2)$.
- Remark: $\alpha_1(\mathbb{R}^2) = \inf_G \alpha(G)/|G|$ (non-measurable independence ratio) equals $1/\chi_f(\mathbb{R}^2)$; conjecture $\chi_f(\mathbb{R}^2) = \chi_{gf}(\mathbb{R}^2) = 4$ (record so far $\chi_{gf}(G) = 3.9954$), which would give $\alpha_1 = 1/4$ and $m_1 \leq 0.247$ simultaneously. THIS IS THE CEILING: the IEC-LP route bottoms out at $1/4$ (L36 caveat). It cannot give $m_1 < 1/5$, so cannot reach $\chi_m \geq 6$.

### 4. Averaging (Section 4) -- the IEC derivation

Lemma 1 holds for every isometric image $\phi(X)$. Average over O(2) with Haar measure $\mu$:

$$\mathring a_X(\varepsilon) = \int_{O(2)} \delta\Big(\bigcap_i (A - \phi(x_i))^{\varepsilon_i}\Big) d\mu(\phi), \qquad \mathring f(x) = \int_{O(2)} \delta(A \cap (A - \phi(x))) d\mu(\phi).$$

$\mathring f$ is radial (eq. 13: $\mathring f(x) = \frac{1}{2\pi}\int_{S^1} f(\xi|x|) d\omega(\xi)$). $C(X) = \{\{I,J\} : I \neq J, X|_I \cong X|_J\}$ is the set of congruent index-set pairs. Averaging eq. 6 gives:

$$\text{(ieC)} \quad \sum_{\varepsilon \in \sigma(n;I)} \mathring a_X(\varepsilon) = \sum_{\varepsilon \in \sigma(n;J)} \mathring a_X(\varepsilon) \quad \text{for every } \{I,J\} \in C(X).$$

Why valid: $X|_J = \phi(\tau(X|_I))$ for some O(2) element $\phi$ and translation $\tau$; $a_X(\varepsilon) = a_{\tau(X)}(\varepsilon)$ by translation invariance of density; averaging eq. 6 over $\phi$ couples the two sides. The Section 4 Remark gives the heuristic (tile into $Q\times Q$ squares, paste an independent Haar-random rotation of $A$ into each, delete unit-width boundary strips): the result has density close to $\delta(A)$ and density correlations effectively O(2)-invariant, so averaging costs nothing in the density estimate (no rigorous proof given; not needed).

### 5. Fourier tools (Section 5) -- Bochner / Bessel

Assume $A$ periodic w.r.t. lattice $L$. Fourier-expand $f$ on $L^2(\mathbb{R}^2/L)$: $\hat f(u) = |\hat{1_A}(u)|^2 \geq 0$ (eq. 14, positive definiteness). After O(2)-averaging,

$$\mathring f(x) = \sum_{u \in 2\pi L^*} \hat f(u)\, \Omega_2(|u||x|), \qquad \Omega_2(|x|) = \frac{1}{2\pi}\int_{S^1} e^{ix\cdot\xi} d\omega(\xi).$$

Schoenberg 1938: $\Omega_2(t) = J_0(t)$, the Bessel function of the first kind, order 0. Grouping by frequency length, $\kappa(t) = \sum_{|u|=t} \hat f(u)$, so $\mathring f(x) = \sum_{t\geq0} \kappa(t) J_0(t|x|)$ (eq. 16) and $\delta(A) = \mathring f(0) = \sum_t \kappa(t)$ (eq. 17). This is the Bochner positive-definite representation: $f(r) = \int J_0(2\pi r s)\,d\nu(s)$ with $\nu \geq 0$, $f(1) = 0$. Repo e3g encodes this as the $\kappa(t) \geq 0$ block plus the $f(1)=0$ constraint.

### 6. Linear programming format (Section 6) -- the full (LP)

Variables: $\{\kappa(t) : t \geq 0\}$ (Fourier masses) and $\{\mathring a_X(\varepsilon)\}$ (independent atoms only). Maximize $\sum_t \kappa(t)$ subject to:
- (CP) $\kappa(t) \geq 0$.
- (IEP) $\mathring a_X(\varepsilon) \geq 0$.
- (C0) $\sum_t \kappa(t) J_0(t) = 0$ (i.e. $\mathring f(1) = 0$, avoidance).
- (IET) $\sum_\varepsilon \mathring a_X(\varepsilon) = 1$.
- (IE1) $\sum_t \kappa(t) - \sum_{\varepsilon\in\sigma(n;i)} \mathring a_X(\varepsilon) = 0$ for each $i$.
- (IE2) $\sum_t \kappa(t) J_0(t|x_i-x_j|) - \sum_{\varepsilon\in\sigma(n;i,j)} \mathring a_X(\varepsilon) = 0$ for each pair.
- (IEC) $\sum_{\varepsilon\in\sigma(n;I)}\mathring a_X(\varepsilon) - \sum_{\varepsilon\in\sigma(n;J)}\mathring a_X(\varepsilon) = 0$ for each $\{I,J\}\in C(X)$.

Remarks: listing congruence constraints for 1- and 2-element vertex sets lets (IE1) be imposed for $i=1$ only and (IE2) once per distinct distance. (IEP)+(C0)+(IE2) force non-independent atoms to 0, so only independent atoms are variables. Applying Lemma 1 to several point sets is dominated by applying it to their union, so one set $X$ suffices. The (LP) constraints induce Szekely 1984, KeMOR 2016, AmM 2022 as special cases. Illustration: Szekely's three graphs embed in a 7-point $X$; solving (LP) on it gives $0.2771 < 12/43$.

### 7. Proposition 1 (dual certificate / weak duality) -- ties to repo L35

Dual variables: $w_0$, $w_T$, $\{w_1(i)\}$, $\{w_2(i,j)\}$, $\{w_c(I,J) : \{I,J\}\in C(X)\}$. Define

$$W(t) = w_0 \Omega_2(t) + \sum_{i} w_1(i) + \sum_{\{i,j\}} w_2(i,j)\,\Omega_2(t|x_i-x_j|),$$

and

$$V(\varepsilon) = w_T - \sum_{i:\varepsilon_i=1} w_1(i) - \sum_{\{i,j\}:\varepsilon_i=\varepsilon_j=1} w_2(i,j) + \sum_{\{I,J\}\in C(X):\varepsilon\in\sigma(n;I)} w_c(I,J) - \sum_{\{I,J\}\in C(X):\varepsilon\in\sigma(n;J)} w_c(I,J).$$

If $W(t) \geq 1$ for all $t \geq 0$ and $V(\varepsilon) \geq 0$ for all $\varepsilon \in \sigma(n)$, then $m_1(\mathbb{R}^2) \leq w_T$. Proof is weak LP duality: $\delta(A) = \sum_t \kappa(t) \leq \sum_t \kappa(t) W(t)$, expand using (C0)/(IE1)/(IE2) so the $w_0$ term vanishes and the $w_1,w_2$ terms become atom-sums, then the IEC telescopes the $w_c$ terms to $0$, leaving $\leq w_T \sum_\varepsilon \mathring a_X(\varepsilon) = w_T$. Only independent atoms need checking for $V(\varepsilon) \geq 0$.

### 8. Breaking 1/4 (Section 7): discretization and beam search

- Discretize $\kappa$: $t_i = i\varepsilon_0$, $\varepsilon_0 = 0.05$, $t_{\max} = 600$ (so 12000 Fourier grid points), $\kappa(t) = 0$ elsewhere.
- Search: configs of cardinality $\leq 24$. Seed $X_0 = $ Moser spindle $M_7$ (for parallelism). Each new point is at distance exactly 1 from $\geq 2$ existing points (to create unit edges and congruent pairs) and at distance $\geq 0.1$ from all existing points (error control, $d_{\min} \geq 0.1$). Score = (LP) optimum. Beam search, beam width 100. Ran 1 week on 128 CPUs, created/solved 186472 LPs, produced a 24-point set; one point was useless and removed, yielding $X_{23}$.

### 9. The configuration $X_{23}$ (Appendix, Section 9)

- 23 points, exact symbolic coordinates in Table 1, complex form $x = a + bi$. $x_1 = 0$, $x_2 = 1$, $x_3 = 1/2 + \sqrt3 i/2$, $x_4 = 3/2 + \sqrt3 i/2$, $x_5 = 5/6 + \sqrt{11}i/6$, etc. Field $\mathbb{Q}(\sqrt3, \sqrt{11})$ (the Moser-spindle ring; the de Grey / Polymath16 ring). Reverse-engineered from numerics using parallelograms (type 1), unit triangles (type 2), and quadratic two-circle intersections (type 3); for $X_{23}$ only type-1 steps plus a single type-2 step were needed.
- $G_{23}$: most vertices degree $\geq 3$, all degree $\geq 2$. Only 27 distinct pairwise distances (this drives the large $|C(X)|$).
- LP size for $X_{23}$: 13552 atom variables, 12000 Fourier variables (25552 total), 6099 equality constraints = 23 (IE1) + 206 (IE2) + 5868 (IEC). Mosek/Gurobi, $< 30$ s.
- Numerical (LP) optimum: $0.24697$.

### 10. Verification (Section 8) -- the rigorous bound

Dual solution: 2350 nonzero coefficients, of which 2321 are $w_c(I,J)$ (at the project website [Web], `bit.ly/unit-distances`, NOT printed in the paper). The 29 non-$w_c$ coefficients are in Table 2. Notably $w_1(i) = 0$ except $w_1(1) = 1.059383649998022$.
- $V(\varepsilon) \geq -\nu$ with $\nu = 10^{-5}$ (high-precision check over all independent atoms); set $\tilde w_T = w_T + \nu$ to restore $V \geq 0$.
- $W(t) \geq 1$ via $\varphi(t) = w_0 J_0(t) + \sum_i w_1(i) + \sum_{i,j} w_2(i,j) J_0(t|x_i-x_j|)$. As $t\to\infty$, $J_0\to0$ so $\varphi(t) \to w_1(1) = 1.0594$. Tail bound (eq. 23) using decreasing $|J_0|$ extrema at zeros of $J_1$: with $\sum|w_2| + |w_0| \approx 1.93062 < 2$ (eq. 24) and $d_{\min} \geq 0.1$, $T = 10000$, largest $J_1$-zero $\leq 1000$ is $s_0 = 999.81148$, gives $\varphi(t) > w_1(1) - 2|J_0(s_0)| = 1.00892 > 1$ for $t > T$. On $[0,T]$, interval arithmetic ($|J_0'| = |J_1| < 1$) gives $\varphi(t) > 1 - \mu$ with $\mu = 0.00006$; global min $0.99995003$ at $t = 3.77488$.
- Divide all $w$ by $(1-\mu)$: final bound $m_1(\mathbb{R}^2) \leq (w_T + \nu)/(1-\mu) = 0.24699\ldots < 0.2470$.

---

## Cross-check against repo L35/L36

| Quantity | Paper | Repo (L35/L36) | Status |
|---|---|---|---|
| (LP) numerical optimum | $0.24697$ | $0.246894$ self-certified (L36), $0.246997$ dual-certified (L35) | Consistent. L36's $0.246894 \leq 0.24697$: the repo's size-$\leq 5$ IEC subset already saturates $X_{23}$, the paper's 5868 include size-$\geq 6$ classes the optimum no longer needs. No discrepancy. |
| Rigorous bound | $(w_T+\nu)/(1-\mu) = 0.24699$ | L35 $0.246997$, L36 $\nu$-free $0.246894$ | Consistent. L35's $0.246997$ matches paper's $0.24699$ to printed digits. |
| Global min of $\varphi(t)$ | $0.99995003$ at $t=3.77488$ | $0.99995003$ at $t=3.7749$ (L35) | Exact match to all printed digits. |
| $\nu, \mu$ | $\nu=10^{-5}$, $\mu=6\times10^{-5}$ | same (L35) | Match. |
| $w_1(1)$ | $1.059383649998022$ | (used in L35 dual re-derivation) | Match. |
| $|w_0| + \sum|w_2|$ | $\approx 1.93062 < 2$ | -- | Paper-internal. |
| $X_{23}$ distinct distances | 27 | 27 (L37 ledger) | Match. |
| $X_{23}$ unit edges | not stated in paper text (degree info only) | 47 (repo extraction) | Repo datum, not contradicted by paper. |
| Field | Moser-spindle ring $\mathbb{Q}(\sqrt3,\sqrt{11})$ | $\mathbb{Q}(\sqrt3,\sqrt{11})$ | Match. |
| LP constraint count | 23 IE1 + 206 IE2 + 5868 IEC = 6099 | (e3j builds $C(X)$) | Match. |

No discrepancies. The repo's self-certified $0.246894$ is slightly TIGHTER than the paper's published $0.24697$ because the repo computes its own dual (no reliance on the website-only 2321 $w_c$) and the size-$\leq 5$ IEC subset already saturates the optimum. This is logged honestly in L36 and is not a contradiction.

---

## Wrong-approach detector check

- $\mathbb{Q}^2$ ($\chi = 2$): Architecture 2 is partly exempt (measure zero on rationals is legitimate). The method here is genuinely measure-theoretic (densities, Lebesgue measure, Bochner), so it does not falsely "lift" to $\mathbb{Q}^2$. PASS (with the standard A2 exemption).
- $L^\infty$ on $\mathbb{R}^2$ ($\chi = 4$): the method DOES use Euclidean rigidity. The Bochner representation uses $J_0$ (the $O(2)$-radial kernel specific to the Euclidean norm), and the configuration $X_{23}$ uses Euclidean unit distances and equilateral-triangle / Moser-spindle structure. A pure $L^\infty$ normed plane has a different (non-rotation-invariant) unit ball and would not support the $J_0$ averaging. PASS: the method engages Euclidean-specific structure.
- $\mathbb{R}^1$ ($\chi = 2$): the $O(2)$ averaging (eq. 12-13) is the crux and is meaningless on the line (no rotation group). The radialization $\mathring f$ and the $J_0$ kernel are 2D-specific. A version blind to $O(2)$ would over-constrain $\mathbb{R}^1$; this method is explicitly $O(2)$-driven. PASS.

The method engages all three control objects correctly. The IEC constraints are the part most at risk of a wrong "lift": they are valid precisely because of the $O(2)$ average over the Euclidean isometry group (Section 4), which is what distinguishes $\mathbb{R}^2$ from $\mathbb{Q}^2$ (no dense rotation orbits) and from $\mathbb{R}^1$ (no $O(2)$).

---

## What this enables / what remains open

ENABLES:
- The single-class IEC construction is now extracted in full precision (Sections 2, 4, 6, 7 above), giving BUILDER the exact template to add congruence constraints to the multi-class LP e3k.
- Two concrete formulations of the multi-class IEC (per-color marginal, and full joint-pattern) with validity arguments and an implementation checklist. Formulation 2 ($|I| = 2, 3$ colored congruence) is the candidate that could push past $\chi_m \geq 5$.
- Cross-checked constants confirm the repo's L35/L36 are faithful; the repo's self-certified $0.246894$ is sound and slightly tighter than the published $0.24697$.

REMAINS OPEN (for BUILDER / ADVERSARY):
- Whether the full joint-pattern IEC (Formulation 2) makes the $k=5$ multi-class LP infeasible (would give $\chi_m \geq 6$). The single-class route is provably capped at $\geq 5$ (paper's own $\alpha_1 = 1/4$ conjecture, L36 ceiling), but the JOINT route is NOT covered by that cap because it uses cross-color correlations the single-class object cannot see.
- VERIFIER must check the transport map $\rho \mapsto \rho'$ dedup when $X|_I$ has self-congruences, to avoid over-tight (invalid) constraints in Formulation 2.
- Scaling: explicit proper-coloring enumeration explodes past ~11 points (L38 barrier a); the moment/Lasserre relaxation (note 08, de Laat-Vallentin, DeCorte-Oliveira-Vallentin 2022) is the principled replacement and would let $X_{23}$-scale configs be used.
- ADVERSARY angle: confirm whether Formulation 1 alone is provably just $k$ parallel L36 certificates (hence capped at 5). If so, only Formulation 2 carries new information, and the cross-color congruence pairs are where any $\geq 6$ obstruction must surface.

Follow-up references to read (cited here, relevant to e3k):
- DeCorte, de Oliveira Filho, Vallentin 2022 (Math. Programming 191): complete-positivity characterization, the exact frame for the IEC truncation (already in `sources/`, note 08).
- Ambrus-Matolcsi 2022 (DCG 67): triple correlations, the immediate predecessor (note relevant).
- Keleti-Matolcsi-de Oliveira Filho-Ruzsa 2016 (DCG 55): Remark 3.3 first suggested the full IE formula (note 11).
- Bellitto-Pecher-Sedillot 2021 (DMTCS 23): $\chi_f \geq 3.8991$ on 607 vertices, the fractional-route comparison.
