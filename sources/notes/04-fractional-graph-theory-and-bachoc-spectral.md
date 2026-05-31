# A3 cluster notes: Fractional Graph Theory (Scheinerman-Ullman) + the operator spectral bound (Bachoc-DeCorte-de Oliveira Filho-Vallentin 2014)

SURVEYOR notes for the fractional / spectral architecture (A3, with A2 overlap). Two texts:

1. E.R. Scheinerman, D.H. Ullman, *Fractional Graph Theory* (Wiley 1997). The finite LP-duality foundation.
2. C. Bachoc, P.E.B. DeCorte, F.M. de Oliveira Filho, F. Vallentin, "Spectral bounds for the independence ratio and the chromatic number of an operator," Israel J. Math. (2014), arXiv:1301.1054v2. The infinite-dimensional Hoffman/Lovasz generalization.

Source PDFs: `sources/books/`, `sources/papers/`. Extracted text: `sources/_extracted/`.

---

## Executive summary: what this cluster gives Architecture A3 (and A2)

1. $\chi_f(G)$ is a *real-valued* relaxation of $\chi(G)$ sitting in $\omega(G) \le \chi_f(G) \le \chi(G)$. It is the value of an LP (set-cover over independent sets), so it is computable and bounded by *fractional cliques* via LP duality: $\chi_f(G) = \omega_f(G)$.
2. For the plane the relevant target is $\chi_f(\mathbb{R}^2)$, currently pinned to $3.555 \le \chi_f(\mathbb{R}^2) \le 4.36$ (Scheinerman-Ullman Section 3.6; lower bound shown there at $32/9 \approx 3.556$). This is a continuous quantity: progress does not require an integer $\chi \ge 6$ UDG.
3. The dual lower-bound object is a *fractional clique* (a weighting of vertices so every independent set has weight $\le 1$); its total weight lower-bounds $\chi_f$. This is exactly what a BUILDER can search for on finite UDGs.
4. Bachoc et al. lift Hoffman's spectral chromatic bound $\chi \ge (M-m)/(-m)$ and Lovasz's ratio bound from finite adjacency matrices to *bounded self-adjoint operators* on $L^2(V)$, $V$ a measure space. The plane's unit-distance graph becomes a convolution operator $A_\nu$ whose numerical range is computed by the Fourier transform $\hat\nu$.
5. For $G(\mathbb{R}^n, S^{n-1})$ (Euclidean unit-distance graph) the optimal measure is the rotation-invariant measure on the sphere; $\hat\nu(u) = \Omega_n(\|u\|)$ is a normalized Bessel function and its first minimum (first zero of $J_{n/2}$) gives the bound.
6. This yields a *measurable* chromatic lower bound and an independence-ratio (upper-density) upper bound for $\mathbb{R}^n$, recovering Oliveira-Vallentin. It is an A2 tool (measurable $\chi_m$) computed by A3 machinery (LP/SDP + harmonic analysis).
7. The operator $\vartheta$-number generalizes too (Theorems 2.5-2.7): infinite analogues of $\vartheta$ and $\bar\vartheta$, with the product identity $\theta \cdot \tilde\theta = 1$ for vertex-transitive $G$ with compact transitivity group.
8. Euclidean rigidity enters precisely through $\hat\nu$: the bound depends on the *geometry of the distance set* (Bessel zeros for the sphere). A method using only normed-plane structure would not see this. This is the detector hook (see detector section).
9. The whole pipeline sidesteps THE BOTTLENECK (a $\chi \ge 6$ planar UDG): both $\chi_f(\mathbb{R}^2)$ and $\chi_m(\mathbb{R}^2)$ are real-valued and can be pushed by better independent sets / better measures, independent of integer colorability.
10. Caveat: $\chi_f(\mathbb{R}^2) \le 4.36 < 5$, so $\chi_f$ alone can never prove $\chi(\mathbb{R}^2) \ge 5$; it bounds from below the *gap target*, and the measurable thread ($\chi_m$) is where $\ge 5$ and $\ge 6$ live.

---

## Synthesis: from $\chi_f$ to the operator bound -- the A3 pipeline

### The finite picture (Scheinerman-Ullman)

The unifying object is a hypergraph $H = (S, X)$ with vertex-hyperedge incidence matrix $M$. Four invariants come in two LP-dual pairs (Ch 1, Fig 1.1):

- Covering $k(H) = \min \mathbf{1}^t x$ s.t. $Mx \ge \mathbf{1}$ (integer). Fractional: $k_f(H)$.
- Packing $p(H) = \max \mathbf{1}^t y$ s.t. $M^t y \le \mathbf{1}$. Fractional: $p_f(H)$.
- Transversal $\tau(H) = k(H^*)$, Matching $\mu(H) = p(H^*)$ (dual hypergraph $H^*$ = transpose of $M$).

LP duality collapses the fractional pair: $k_f(H) = p_f(H)$ (Theorem 1.2.1). Two routes to the fractional value agree:
- LP relaxation $k^*$ of the covering IP.
- The $t$-fold limit $k_f(H) = \lim_t k_t(H)/t = \inf_t k_t(H)/t$ (Fekete subadditivity), where a $t$-fold cover hits each vertex $\ge t$ times.

Apply this with $S = V(G)$ and $X = $ independent sets of $G$. Then $k(H) = \chi(G)$ and the fractional covering number is the **fractional chromatic number**:
$$\chi_f(G) = k_f(H) = \lim_{b\to\infty} \frac{\chi_b(G)}{b},$$
where $\chi_b(G)$ is the $b$-fold chromatic number (assign each vertex a $b$-set of colors, adjacent vertices get disjoint sets). The dual is $p_f(H) = \omega_f(G)$, the **fractional clique number**, and duality gives the central identity
$$\chi_f(G) = \omega_f(G), \qquad \omega(G) \le \chi_f(G) \le \chi(G).$$
A *fractional clique* is a weighting $g: V \to [0,1]$ with $\sum_{v \in I} g(v) \le 1$ for every independent set $I$; its weight $\sum_v g(v)$ lower-bounds $\chi_f$. (Equivalently an $a{:}b$-clique, a multiset of size $a$ meeting each independent set in $\le b$ points.)

This is the engine for lower bounds: **to certify $\chi_f(G) \ge r$ it suffices to exhibit one fractional clique of weight $r$.** No coloring, no integer argument. (Scheinerman-Ullman use exactly this for the plane: a $96{:}27$-clique on a 57-vertex UDG, Theorem 3.6.2.)

Key finite facts that transfer:
- Vertex-transitive $G$: $\chi_f(G) = \nu(G)/\alpha(G) = |V|/\alpha$ (Prop 1.3.4 / 3.1.1). The "size over independence number" formula.
- $\chi_f$ is the asymptotic chromatic number under the disjunctive product: $\chi_f(G) = \lim_n \sqrt[n]{\chi(G^n)}$ (Cor 3.4.3), and $\chi_f$ is multiplicative on this product (Cor 3.4.2).
- Lovasz $\vartheta$ wedges in for the *dual* (clique) side: $\omega(G) \le \omega_\infty(G) \le \omega_f(G) = \chi_f(G) = \chi_\infty(G) \le \chi(G)$, with the Shannon-capacity gap $\omega_\infty(C_5) = \sqrt5 < \omega_f(C_5) = 5/2$ showing the *packing* asymptotics need not equal the fractional value (Section 3.5). $\vartheta$ is the computable real number sandwiched: $\alpha \le \vartheta(\bar G) \le \chi_f \le \chi$.

### The bridge: LP duality becomes operator/SDP duality

Bachoc et al. recast the finite Hoffman/Lovasz story in operator language so it survives the passage to an uncountable vertex set. The dictionary:

| Finite (Scheinerman-Ullman / Lovasz) | Operator (Bachoc et al.) |
|---|---|
| adjacency matrix $A \in \mathbb{R}^{V\times V}$ | bounded self-adjoint $A: L^2(V) \to L^2(V)$ |
| $I$ independent: $\sum A(v,w)f(v)f(w)=0$ on $I$ (eq. 3) | $I$ independent: $(Af,f)=0$ for $f$ supported on $I$ (Def 2.1) |
| $\alpha(G)/\|V\|$ | independence ratio $\alpha(A) = \sup\{\mu(I): I \text{ indep}\}$, $\mu$ a probability measure |
| smallest/largest eigenvalue $m(A), M(A)$ | endpoints of numerical range $W(A)=\{(Af,f): \|f\|=1\}$ |
| Hoffman: $\chi \ge (M-m)/(-m)$ | Thm 2.3: $\chi(A) \ge (M(A)-m(A))/(-m(A))$ |
| Lovasz ratio: $\alpha/n \le -m/(M-m)$ | Thm 2.2: $\alpha(A) \le -m(A)/(R-m(A))$ (with $\varepsilon$ slack) |
| $\vartheta(G)$ SDP (eq. 4) and its dual | Thm 2.5 / 2.6: $\inf_\lambda\{\lambda: \lambda I + Z - J \succeq 0\}$ and $\sup\{((D_a+K)\mathbf 1,\mathbf 1)\}$ |
| $\vartheta(G)\vartheta(\bar G) \ge |V|$ (= for vertex-transitive) | Thm 2.7: $\theta \cdot \tilde\theta \ge 1$ (= for compact transitivity group) |
| $\chi \ge \chi_f \ge \vartheta$ | Thm 2.4: $\chi^*(A) \ge ((A\mathbf 1,\mathbf 1) - m)/(-m)$ |

Two technical moves make the lift work:
1. **The $\varepsilon$ in the Hoffman proof.** Finite proof projects onto color-class representatives; infinite proof projects $L^2(V) = \bigoplus_i L^2(C_i)$ and chooses $f$ with $(Af,f) \ge M(A) - \varepsilon$, then lets $\varepsilon \to 0$. The trace-zero argument on the compressed operator $B = PA$ is otherwise identical (the authors note it is "very close" to Bollobas's proof, "we only had to include the epsilon").
2. **Symmetrization.** For a vertex-transitive $G$ with compact transitivity group $T$ (Haar measure $\nu$), $R_T(A)f(x) = \int_T (Af^T)^{T^{-1}}(x)\,d\nu(T)$ averages an operator into one having $\mathbf 1_V$ as eigenfunction while preserving "respects $G$" and positivity. This is the infinite analogue of replacing an optimal solution by its group-average (Prop 1.3.4 above), and it is what forces $\inf$ in (5) and $\sup$ in (6) to coincide with the operator $\vartheta$ and to satisfy the product identity.

The phrase "operator $A$ **respects** $G$" (measurable independent sets of $G$ are independent for $A$) is the load-bearing definition: any such $A$ gives $\alpha(G) \le \alpha(A)$ and $\chi(A) \le \chi_m(G)$, so *every* respecting operator yields a valid bound, and one optimizes over them.

### The geometry: convolution operators and Fourier on $\mathbb{R}^n$

For $G(\mathbb{R}^n, N)$ (vertices $\mathbb{R}^n$, adjacency iff $x-y \in N$, $N$ bounded, centrally symmetric, $0 \notin \overline N$), take a centrally symmetric signed measure $\nu$ supported on $N$ and the convolution operator
$$(A_\nu f)(x) = (f * \nu)(x) = \int_{\mathbb{R}^n} f(x-y)\, d\nu(y).$$
- Central symmetry $\Rightarrow A_\nu$ self-adjoint.
- Every measurable independent set of $G$ is independent for $A_\nu$ (because $x \in I, y \in N \Rightarrow x-y \notin I$), so $A_\nu$ respects $G$.
- Plancherel diagonalizes it: $(A_\nu f, f) = (\hat\nu \hat f, \hat f)$, so $A_\nu$ is multiplication by $\hat\nu(u) = \int e^{-2\pi i x\cdot u}\,d\nu(x)$. Hence
$$m(A_\nu) = \inf_u \hat\nu(u), \qquad M(A_\nu) = \sup_u \hat\nu(u).$$

Plugging into Hoffman (Thm 2.3) gives the master inequality (eq. 10):
$$\chi_m(G(\mathbb{R}^n, N)) \ \ge\ \frac{\sup_u \hat\nu(u) - \inf_u \hat\nu(u)}{-\inf_u \hat\nu(u)},$$
optimized over admissible $\nu$. The dual density statement (eq. 11), via a ball-truncation limit $A_\nu^r$ on $L^2(B_r)$ and $\limsup_r \alpha(A_\nu^r) \ge \alpha(G)$, gives the **upper density** (independence ratio) bound:
$$\alpha(G(\mathbb{R}^n, N)) \ \le\ \frac{-\inf_u \hat\nu(u)}{\hat\nu(0) - \inf_u \hat\nu(u)}.$$

**Unit-distance specialization** ($N = S^{n-1}$): $O(n)$ acts transitively, the optimal $\nu$ is the rotation-invariant probability measure $\omega$, and
$$\hat\omega(u) = \Omega_n(\|u\|), \qquad \Omega_n(t) = \Gamma\!\left(\tfrac n2\right)\left(\tfrac 2t\right)^{(n-2)/2} J_{(n-2)/2}(t),$$
a normalized Bessel function with $\Omega_n(0)=1$. The global minimum of $\Omega_n$ sits at $t = j_{n/2,1}$, the first positive zero of $J_{n/2}$. Therefore
$$\chi_m(G(\mathbb{R}^n, S^{n-1})) \ \ge\ \frac{\Omega_n(j_{n/2,1}) - 1}{\Omega_n(j_{n/2,1})}, \qquad \alpha(G(\mathbb{R}^n, S^{n-1})) \ \le\ \frac{\Omega_n(j_{n/2,1})}{\Omega_n(j_{n/2,1}) - 1}.$$
This recovers Oliveira-Vallentin (2010), Section 3. The two bounds multiply to 1 (Thm 2.7).

For the **sphere** $G(S^{n-1}, D)$ the same template runs with spherical harmonics replacing Fourier modes: the operators $A_t$ have eigenvalues $\lambda_k(t) = P_k^{(\alpha,\alpha)}(t)$ (Jacobi polynomials, $\alpha = (n-3)/2$) by Funk-Hecke. For a single inner product $D = \{t\}$ no optimization is needed:
$$\alpha(G(S^{n-1},\{t\})) \le \frac{-\inf_k \lambda_k(t)}{1 - \inf_k \lambda_k(t)}, \qquad \chi_m(G(S^{n-1},\{t\})) \ge \frac{1 - \inf_k \lambda_k(t)}{-\inf_k \lambda_k(t)},$$
tight in many cases (e.g. $n=3$, $t=-1/3$, originally Lovasz 1983 by topology).

### What this offers the project

- A **continuous lower-bound dial** for the plane that does not pass through integer colorability: improve the certified fractional clique (finite side) or improve the spectral/measure choice (infinite side).
- A clean **A3 -> A2 bridge**: the operator chromatic bound is literally a lower bound on $\chi_m(\mathbb{R}^2)$, the measurable chromatic number, so an A3 computation feeds the A2 ledger directly.
- A **dual SDP** (operator $\vartheta$) that, for the Euclidean unit-distance graph, reduces to a one-variable optimization over a Bessel transform: this is what made the LP-bound program of Oliveira-Vallentin and the de Grey-era density bounds tractable.
- It **circumvents THE BOTTLENECK**: the missing object for A1 (a $\chi \ge 6$ planar UDG) is irrelevant here; the obstruction is instead the *gap* between the fractional/measurable bound and the integer chromatic number.

---

## Text 1: Scheinerman-Ullman, *Fractional Graph Theory* -- structured notes

### Chapter 1: General Theory (Hypergraphs) -- MAX DEPTH

The whole book is built on one LP-duality template applied to a hypergraph $H = (S,X)$ with incidence matrix $M$.

- **Covering** $k(H)$: fewest hyperedges covering all vertices. IP: $\min \mathbf 1^t x$ s.t. $Mx \ge \mathbf 1$, $x \in \{0,1\}$.
- **Packing** $p(H)$: most vertices, no two in a common hyperedge. IP: $\max \mathbf 1^t y$ s.t. $M^t y \le \mathbf 1$. (For a graph this is $\alpha$.)
- Prop 1.1.1: $p(H) \le k(H)$ (weak duality at IP level).
- Graph instances: $\chi(G) = k(H)$ with $X$ = independent sets; $\mu(G) = p(\text{dual})$.

**Fractional via two routes (Section 1.2), shown equal (Thm 1.2.1):**
- LP relaxation: $k^*(H) = \min \mathbf 1^t x$ s.t. $Mx \ge \mathbf 1$, $x \ge 0$; $p^*(H) = \max \mathbf 1^t y$ s.t. $M^t y \le \mathbf 1$, $y \ge 0$. LP duality: $k^* = p^*$.
- $t$-fold / asymptotic: $t$-fold cover hits each vertex $\ge t$ times; $k_t$ subadditive in $t$; Fekete gives $k_f(H) = \lim_t k_t/t = \inf_t k_t/t \le k(H)$. Dually $p_t$ superadditive, $p_f = \lim p_t/t \ge p(H)$.
- **Theorem 1.2.1**: $k^* = k_f = p^* = p_f$. All four "fractional" notions coincide.

**Consequences (Section 1.3):**
- Cor 1.3.1: $k_f(H) \in \mathbb{Q}$ (LP with integer data).
- Cor 1.3.2: $\exists s$ with $k_f = k_s/s$ (the inf is attained, infinitely often).
- Prop 1.3.4 (**transitivity formula**): vertex-transitive $H$, $e = \max_X |X|$, then $k_f(H) = |S|/e$. Proof: uniform weight $1/e$ is optimal by group-averaging.

**Game-theoretic value (Section 1.4):** the hypergraph incidence game (vertex player picks $s$, hyperedge player picks $X$, payoff $1$ if $s \in X$) has value $1/k_f(H)$ (Thm 1.4.1). This is the minimax / LP-duality reading.

**Two dualities (Section 1.5):** (a) LP/IP duality (covering vs packing); (b) hypergraph duality $H \to H^*$ (transpose $M$), giving transversal $\tau(H) = k(H^*)$ and matching $\mu(H) = p(H^*)$, hence $\tau_f = \mu_f$. Fig 1.1 summarizes all four.

**Asymptotic invariants (Section 1.6, used again in 3.5):** hypergraph product $H \times K$ (Cartesian product of vertex sets, products of hyperedges). $k_f$ is multiplicative: $k_f(H\times K) = k_f(H)k_f(K)$ (Thm 1.6.1). Asymptotic covering $k_\infty(H) = \inf_n \sqrt[n]{k(H^n)}$. **Thm 1.6.2: $k_\infty = k_f$** (two proofs: random cover, and greedy cover via Lemma 1.6.4 $k(H) \le (1+\log m)k_f(H)$). In contrast $p_\infty$ (asymptotic packing) need NOT equal $p_f$ and need not be rational: for $C_5$, $p_f = k_f = 5/2$ but $p_\infty = $ Shannon capacity $= \sqrt5$ (Lovasz). This asymmetry is the source of the $\vartheta$ story.

### Chapter 2: Fractional Matching (brief)

Fractional matching $\mu_f(G) = \sup \sum_e f(e)$, $f: E \to [0,1]$, $\sum_{e \ni v} f(e) \le 1$. Dual: fractional transversal. Konig-Egervary: bipartite $\Rightarrow \mu = \mu_f$ (Thm 2.1.3), proved via total unimodularity of the incidence matrix (Lemma 2.1.4). Half-integrality: $2\mu_f(G) \in \mathbb{Z}$, achieved with $f(e) \in \{0, 1/2, 1\}$ (Thm 2.1.5) -- sharply unlike $\chi_f$, whose values are dense in $[2,\infty) \cap \mathbb{Q}$. Section 2.x also sets up the vertex-independent-set hypergraph used to define $\chi_f$ in Ch 3.

### Chapter 3: Fractional Coloring -- MAX DEPTH

**Definition.** $H$ = vertex-independent-set hypergraph; $\chi_f(G) = k_f(H) = \lim_b \chi_b(G)/b$. Rational (Cor 1.3.1), $\chi_f = \chi_b/b$ for some $b$. If $G$ has an edge then $\chi_f \ge 2$.

**Duality and bounds:**
- Prop 3.1.1: $\chi_f(G) \ge \nu(G)/\alpha(G)$, equality if vertex-transitive. (From Prop 1.3.4.)
- Dual: $p_f(H) = \omega_f(G)$, the **fractional clique number**; $\chi_f(G) = \omega_f(G)$ (LP duality).
- $\omega(G) \le \chi_f(G) \le \chi(G)$. Fractional perfection is trivial: $\chi_f(H) = \omega_f(H)$ for *all* induced $H$.
- Prop 3.1.2: $\chi_f(C_{2m+1}) = 2 + 1/m$.

**Homomorphisms and Kneser graphs (Section 3.2):**
- $K_{a:b}$ = Kneser graph ($b$-subsets of $[a]$, adjacent iff disjoint). $G$ has an $a{:}b$-coloring iff $\exists$ homomorphism $G \to K_{a:b}$ (Prop 3.2.1).
- **Homomorphism monotonicity (the "no-homomorphism" inequality, stated here via composition):** if $G \to H$ then any $c{:}d$-coloring of $H$ pulls back to $G$; hence $\chi_f(G) \le \chi_f(H)$ whenever there is a homomorphism $G \to H$ (Props 3.2.5, used to prove EKR and Stahl). Concretely: $K_{a:b} \to K_{c:d}$ exists iff $c/d \ge a/b$ on the Kneser scale.
- Erdos-Ko-Rado: $\alpha(K_{a:b}) = \binom{a-1}{b-1}$ for $a>2b$ (Thm 3.2.3), equivalent to **$\chi_f(K_{a:b}) = a/b$ (Prop 3.2.4)**. Also the circular graph $G_{a,b}$ has $\chi_f = a/b$ (Prop 3.2.2): all rationals $\ge 2$ are achieved.
- Integer Kneser: $\chi(K_{a:b}) = a - 2b + 2$ (Lovasz, Thm 3.2.6); $\chi_m(K_{a:b}) = a - 2b + 2m$ for $1 \le m \le b$ (Stahl, Thm 3.2.8). The gap $\chi - \chi_f$ can be arbitrarily large (Example 3.3.1: $K_{nb:b}$ has $\omega = \chi_f = n$ but $\chi = (n-2)b+2$).

**Duality gap and Mycielskian (Section 3.3):** $\chi_f$ lives in $[\omega, \chi]$, both endpoints achievable. Mycielski $Y(G)$: $\omega(Y(G)) = \omega(G)$, $\chi(Y(G)) = \chi(G)+1$, but **$\chi_f(Y(G)) = \chi_f(G) + 1/\chi_f(G)$** (Thm 3.3.4). Iterating from $K_2$: $\chi_f \sim \sqrt{2n}$ while $\chi = n+1$. Also shows the denominator of $\chi_f$ can be exponential in $|V|$ (obstacle to fast computation).

**Products and asymptotics (Sections 3.4-3.5):** disjunctive product $G * H$; $\chi_f(G*H) = \chi_f(G)\chi_f(H)$ (Cor 3.4.2); $\chi_f(G) = \lim_n \sqrt[n]{\chi(G^n)} = \chi_\infty(G)$ (Cor 3.4.3). Full chain:
$$\omega(G) \le \omega_\infty(G) \le \omega_f(G) = \chi_f(G) = \chi_\infty(G) \le \chi(G),$$
all inequalities can be strict. **Shannon capacity** $\Theta(C_5) = \omega_\infty(C_5) = \sqrt5$ (Thm 3.5.3) via Lovasz's orthonormal-representation invariant $\eta$ (the umbrella construction), $\omega_\infty \le \eta$, $\eta(C_5) = \sqrt5$. This $\eta$ is (a form of) Lovasz $\vartheta$ -- the precise object Bachoc et al. generalize.

**Section 3.6: THE FRACTIONAL CHROMATIC NUMBER OF THE PLANE (central for the project).**
- Upper bound **$\chi_f(\mathbb{R}^2) \le 4.36$** (Thm 3.6.1). Method: a periodic independent set $S$ of density $d = 0.229365$ (Croft 1967 / Hochberg-O'Donnell 1993: open convex tile $A$ = disk of diameter 1 with 6 symmetric circular segments removed, perimeter half arc / half segment, framed in a hexagon, tiled). A density-$d$ independent set yields $\chi_f \le 1/d = 4.35987$ via a translate-coloring argument (color classes are $n^2$ translates of $S$; each point gets $\approx n^2 d$ colors).
- Lower bound **$\chi_f(\mathbb{R}^2) \ge 32/9 \approx 3.556$** (Thm 3.6.2). Method: a 57-vertex, 198-edge unit graph $G$ (core of 12 vertices + 15 Moser-spindle "gadgets" in 3 rotated families) with a $96{:}27$-fractional clique, certifying $\chi_f(G) \ge 96/27 = 32/9$. Graph due to D. Fisher and D. Ullman. The spindle alone gives $\chi_f \ge 7/2$.
- The headline interval $3.555 \le \chi_f(\mathbb{R}^2) \le 4.36$ is the section's summary (lower bound rounded from $32/9$). Notes: larger Fisher-Ullman graphs plausibly push toward $\chi_f(\mathbb{R}^2) \ge 4$, but the sup of $\chi_f$ over finite subgraphs *might not equal* $\chi_f(\mathbb{R}^2)$ (Exercises 23-24, Leader/Levin counterexamples for general infinite graphs).
- **Exercise 19 (detector-relevant): $\mathbb{Q}^2$ (rational unit-distance graph) is bipartite** -- Woodall's $\chi(\mathbb{Q}^2)=2$ appears here directly.

> **VERIFIED AUDIT (2026-05-30), prompted by the note-08 / KMOR $m_1$-direction error.** The
> $\chi_f(\mathbb{R}^2) \le 4.36$ claim was checked against the SU source text (Thm 3.6.1, extracted
> lines 2768-2895) and is CORRECT, including the $d = 0.229365$ density and the $1/d = 4.35987$
> arithmetic. Crucially the DIRECTION here is the OPPOSITE of the $\chi_m$ density bound and is used
> correctly, so this is NOT the note-08 error: for $\chi_f$, a measurable independent set of density
> $d$ gives a fractional coloring of cost $1/d$, so $\chi_f \le 1/d$; a LARGER $d$ (denser explicit
> construction) gives a SMALLER, better UPPER bound. Using the construction value $d = 0.229365$ (a
> LOWER-bound witness on $m_1$) to upper-bound $\chi_f$ is valid. (Contrast $\chi_m \ge 1/m_1$, which
> needs an UPPER bound on $m_1$; there, using $0.229$ as if it bounded $m_1$ above was the note-08
> error.) Sanity check: $\mathbb{R}^1$ has $m_1 = 1/2$, giving $\chi_f(\mathbb{R}^1) \le 2$, correct.
> TWO updates to flag: (i) the LOWER bound $32/9 \approx 3.556$ is the 2011 textbook value; the field
> has since improved it, and the repo's own LEARNINGS L36 records a record fractional
> $\chi_{gf} = 3.9954$ (Ambrus et al.), with the conjecture $\chi_f(\mathbb{R}^2) = 4$ (and $m_1 = 1/4$).
> So treat $3.9954 \le \chi_f(\mathbb{R}^2) \le 4.36$ as the current interval, conjecturally $= 4$.
> (ii) The vertex-transitive identity $\chi_f = 1/m_1$ that holds for finite graphs need NOT pin the
> infinite plane (line above, Leader/Levin); the proven $m_1 \le 0.2469$ does not force $\chi_f \ge 4.05$,
> precisely because the finite-subgraph sup may be $< 1/m_1$. Both bounds in this interval are sound.

**Section 3.7-3.9:** Fractional Erdos-Faber-Lovasz (Kahn-Seymour, Thm 3.7.2: $\chi_f = n$, the integer version still open). Fractional list-chromatic equals fractional chromatic (Thm 3.8.1, no gap). Complexity: deciding $\chi_f(G) \le r$ is NP-complete for every real $r > 2$ (Thm 3.9.2, Grotschel-Lovasz-Schrijver) even though LPs solve in poly time -- the LP has exponentially many independent-set variables.

### Chapter 4: Fractional Edge Coloring (brief)

$\chi'_f(G) = \chi_f(L(G)) = k_f(\text{edge-matching hypergraph})$. Vizing: $\Delta \le \chi' \le \Delta+1$ (Thm 4.1.1); class one/two distinction NP-hard. Goldberg-Seymour-type results: $\chi'_f$ has a clean min-max (fractional edge coloring = max edge weighting with no matching exceeding 1). Not central to A3 for the plane.

### Chapter 5: Fractional Arboricity / Matroid Methods (brief)

Arboricity $\Upsilon$ = min forests covering $E$; fractional version via the cycle matroid. Nash-Williams formula and its fractional refinement. Matroid structure makes these the best-behaved fractional invariants. Tangential to HN.

### Chapter 6: Fractional Isomorphism (brief)

$G \cong_f H$ iff $\exists$ doubly stochastic $S$ with $AS = SB$ ($A,B$ adjacency matrices). Weaker than isomorphism (example: a planar graph fractionally iso to a non-planar one). Invariants preserved: $|V|$, $|E|$, degree sequence, largest eigenvalue (Props 6.1.2-6.1.4, 6.2.6, 6.5.2). Regular graphs of the same degree/order are all fractionally isomorphic. Characterized by equitable-partition / iterated-degree refinement. Not a lower-bound tool for HN but conceptually the "linear relaxation of permutation."

### Chapter 7: Fractional Odds and Ends (brief)

Fractional genus, crossing number ($x_f = x$, Thm 7.1.4), thickness, cycle double covers, domination ($\gamma_f$ can be any rational $\ge 1$, Thm 7.4.1), Ramsey-type. Survey-flavored.

---

## Text 2: Bachoc-DeCorte-de Oliveira Filho-Vallentin (2014) -- detailed reconstruction

21 pages. MSC 47B25 (operator theory), 05C50 (graph spectra). Goal: extend Hoffman's spectral chromatic bound and Lovasz's ratio bound from finite adjacency matrices to bounded self-adjoint operators on $L^2$, providing a framework where infinite packing/coloring problems are attacked with harmonic analysis + convex optimization.

### Section 1: Introduction / finite background

- Hoffman (eq. 1): $\chi(G) \ge (M(A) - m(A))/(-m(A))$, $A$ = adjacency matrix, $m,M$ extreme eigenvalues. The proof works for any symmetric matrix supported on $E(G)$; maximizing over such matrices yields $\vartheta(\bar G)$.
- Lovasz ratio bound (eq. 2): regular $G$ on $n$ vertices, $\alpha(G)/n \le -m(A)/(M(A)-m(A))$.
- $\vartheta$ SDP (eq. 4): $\max \sum_{v,w} K(v,w)$ s.t. $\sum_v K(v,v)=1$, $K(v,w)=0$ on edges, $K \succeq 0$. Sandwich $\alpha(G) \le \vartheta(\bar G) \le \chi(G)$, and $\chi(G) \ge \chi_f(G) \ge \vartheta(\bar G)$. Schrijver's $\vartheta'$ (add $K \ge 0$ entrywise) = Galtman's best spectral bound over nonnegative weighted adjacency matrices (Perron-Frobenius). Prior infinite-graph $\vartheta$: Bachoc-Nebe-Oliveira-Vallentin (2009) for compact metric spaces.

### Section 2: Spectral bounds for bounded self-adjoint operators (the core theory)

**Setup (2.2):** $L^2(V)$ over a measure space $(V, \Sigma, \mu)$, complex-valued; $A$ bounded self-adjoint; numerical range $W(A) = \{(Af,f): \|f\|=1\}$ is a real interval $[m(A), M(A)] \subseteq [-\|A\|, \|A\|]$. Endpoints may or may not be attained.

**Independence (2.3, Def 2.1):** measurable $I \subseteq V$ is *independent for $A$* if $(Af,f) = 0$ for every $f$ vanishing a.e. outside $I$. Nullsets are always independent (so independence is defined up to nullsets). With $\mu$ a probability measure, independence ratio $\alpha(A) = \sup\{\mu(I): I \text{ independent}\}$; for a finite graph this is $\alpha(G)/|V|$.

**Theorem 2.2 (operator Lovasz ratio bound, with slack).** $(V,\mu)$ probability space, $A \ne 0$ bounded self-adjoint. Fix $R$, set $\varepsilon = \|A\mathbf 1_V - R\mathbf 1_V\|$. If a positive-measure independent $I$ exists and $R - m(A) - \varepsilon > 0$, then
$$\alpha(A) \le \frac{-m(A) + 2\varepsilon}{R - m(A) - \varepsilon}.$$
Proof: decompose $\mathbf 1_I = \beta\mathbf 1_V + g$ ($g \perp \mathbf 1_V$), note $\mu(I) = \beta = \beta^2 + \|g\|^2$, expand $0 = (A\mathbf 1_I, \mathbf 1_I)$, bound with Cauchy-Schwarz and $\eta = A\mathbf 1_V - R\mathbf 1_V$. When $A$ is a regular finite graph and $R = M(A)$ (so $\mathbf 1_V$ is the top eigenvector, $\varepsilon=0$), recovers eq. 2. The hypothesis $\mu(I)>0$ is essential (counterexample given).

**Theorem 2.3 (operator Hoffman chromatic bound).** $A \ne 0$ bounded self-adjoint, $\chi(A) < \infty$:
$$\chi(A) \ge \frac{M(A) - m(A)}{-m(A)}.$$
Here $\chi(A)$ = fewest independent sets partitioning $V$. Proof: partition $L^2(V) = \bigoplus_i L^2(C_i)$; pick $f$ with $(Af,f) \ge M(A)-\varepsilon$, decompose over color classes, form $B = PA$ on the $k$-dim span $U$; $W(B) \subseteq [m,M]$, $\lambda_1(B) \ge M-\varepsilon$, $\operatorname{tr} B = \sum_i (Af_i,f_i) = 0$ (each $f_i$ in an independent class), so $M - \varepsilon + (k-1)m \le 0$; let $\varepsilon \to 0$. Corollary of the proof: $A \ne 0$ with finite $\chi(A) \Rightarrow m(A) < 0 < M(A)$.

**Theorem 2.4 (operator fractional chromatic bound).** $(V,\mu)$ probability space, $A \ne 0$, $\chi^*(A) < \infty$:
$$\chi^*(A) \ge \frac{(A\mathbf 1_V, \mathbf 1_V) - m(A)}{-m(A)},$$
where $\chi^*(A)$ = inf of $\sum \lambda_i$ over fractional colorings $\sum_i \lambda_i \mathbf 1_{C_i} = \mathbf 1_V$ with $C_i$ independent. Proof mirrors Schrijver's sandwich-theorem proof.

**Subsection 2.6 (relation to $\vartheta$).** Definitions: $A \succeq 0$ positive; $J f = (f, \mathbf 1_V)\mathbf 1_V$; "$A$ respects $G$" = measurable independent sets of measurable graph $G$ are independent for $A$, giving $\alpha(G) \le \alpha(A)$, $\chi(A) \le \chi_m(G)$. Master bounds over respecting operators:
$$\alpha(G) \le \inf_A \frac{-m(A)}{M_1(A)-m(A)} \quad (\text{eq. 5}), \qquad \chi_m(G) \ge \sup_A \frac{M(A)-m(A)}{-m(A)} \quad (\text{eq. 6}).$$
Vertex-transitivity here means a topological transitivity group $T$ acting continuously and transitively by measure-preserving automorphisms.

**Theorem 2.5 (operator $\vartheta$, primal/dual side for $\alpha$).** The inf in (5) is $\ge$
$$\inf_\lambda \{\lambda : \lambda I + Z - J \succeq 0,\ Z \text{ bounded self-adjoint, respects } G\},$$
with equality when $G$ is vertex-transitive with compact transitivity group and the value is $<1$. For finite $G$ this is exactly the dual SDP to (4), i.e. $\vartheta(G)$. Proof uses the symmetrization $R_T$.

**Theorem 2.6 ($\vartheta$ for the chromatic side).** The sup in (6) is $\le$
$$\sup \{((D_a + K)\mathbf 1_V, \mathbf 1_V) : D_a + K \succeq 0,\ a \in L^\infty,\ \textstyle\int a\,d\mu = 1,\ K \text{ bounded self-adjoint, respects } G\},$$
($D_a$ = multiplication by $a$), with equality for vertex-transitive $G$ with compact transitivity group and value $>1$. For finite $G$ this is $\vartheta(\bar G)$.

**Theorem 2.7 (product identity).** With $\theta$ = value of (7) and $\tilde\theta$ = value of (8): $\theta \cdot \tilde\theta \ge 1$, equality for compact transitivity group. (Infinite analogue of $\vartheta(G)\vartheta(\bar G) \ge |V|$.)

### Section 3: Graphs on Euclidean space

$G(\mathbb{R}^n, N)$ as above. Convolution operator $A_\nu$ (eq. 9), self-adjoint by central symmetry, respects $G$, bounded by Minkowski. Fourier diagonalization: $m(A_\nu) = \inf_u \hat\nu(u)$, $M(A_\nu) = \sup_u \hat\nu(u)$. Master chromatic bound eq. 10 and, via ball truncation $A_\nu^r$ on $L^2(B_r)$, the upper-density bound eq. 11 (limits $m(A_\nu^r) \to m(A_\nu)$, $R(r) \to \hat\nu(0)$, $\varepsilon(r) \to 0$ proved explicitly using the diameter-$D$ support of $\nu$).

- **3.3 Odd-distance graph $G(\mathbb{R}^2, \bigcup_k (2k+1)S^1)$.** Rosenfeld's question (finite $\chi$?). Integer $\chi \ge 5$ (Ardal-Manuch-Rosenfeld-Shelah-Stacho). Furstenberg-Katznelson-Weiss $\Rightarrow$ $\chi_m = \infty$. Steinhardt's measure $\nu = \frac{\beta-1}{\beta}\sum_k \beta^{-k}\omega_{2k+1}$ makes $\inf_u \hat\nu(u) \to 0$, $\sup \to 1$ as $\beta \to 1$, $N \to \infty$, so eq. 10 forces $\chi_m \to \infty$. Kolountzakis's variant handles non-polytopal norm balls via decay of $\hat\nu$.
- **3.4 Unit-distance graph $G(\mathbb{R}^n, S^{n-1})$.** $O(n)$ transitive, optimal $\nu = \omega$ (rotation-invariant), $\hat\omega(u) = \Omega_n(\|u\|)$ a normalized Bessel; min at first zero $j_{n/2,1}$ of $J_{n/2}$. Bounds as in the synthesis section. Recovers Oliveira-Vallentin (2010, Sec 3). For $\mathbb{R}^2$ this is the spectral/measurable bound on $\chi_m(\mathbb{R}^2)$ (numerically $\approx 1+\text{(Bessel ratio)}$, the well-known weak measurable bound; the strong $\chi_m \ge 5,6$ results come from multi-distance / multi-measure refinements built on this same operator framework).

### Section 4: Graphs on the unit sphere

$G(S^{n-1}, D)$, $D \subseteq [-1,1]$, $1 \notin \overline D$, adjacency iff $x\cdot y \in D$. Compact non-abelian $O(n)$ transitivity (vs locally-compact abelian $\mathbb{R}^n$ in Sec 3). Operators $A_t$ have spherical harmonics as eigenfunctions (Funk-Hecke), eigenvalues $\lambda_k(t) = P_k^{(\alpha,\alpha)}(t)$, $\alpha=(n-3)/2$ (Jacobi polynomials); decay $O(k^{-1/2-(n-3)/2})$ so $A_t$ compact for $n \ge 3$. $A_\nu = \int A_t\,d\nu$, $m(A_\nu) = \inf_k \int \lambda_k\,d\nu$, $M = \sup_k$. Single inner product $D=\{t\}$: closed-form bounds (multiply to 1), tight in many cases; $n=3, t=-1/3$ recovers Lovasz (1983). Extends to compact rank-one symmetric spaces (Oliveira-Vallentin).

---

## Mapping to the four architectures

- **A3 (fractional / spectral): primary home.** Scheinerman-Ullman Ch 1+3 supplies the finite LP-duality skeleton ($\chi_f = \omega_f$, fractional cliques, $\vartheta$ sandwich) and the concrete plane bounds $32/9 \le \chi_f(\mathbb{R}^2) \le 4.36$. Bachoc et al. supplies the infinite operator/SDP generalization and the Fourier/Bessel computation. The operator $\vartheta$ (Thms 2.5-2.7) is the A3 SDP for $\mathbb{R}^2$.
- **A2 (measurable / spectral): direct overlap.** Bachoc's eq. 6 and eq. 10 are lower bounds on $\chi_m(G)$, the *measurable* chromatic number. The convolution-operator method is exactly the Falconer/autocorrelation lineage in operator form, so Bachoc is an A2 instrument computed by A3 means. Steinhardt's $\chi_m(\text{odd-distance}) = \infty$ result lives here too.
- **A1 (combinatorial / UDG): consumer, not producer.** A3 fractional cliques are searched on finite UDGs (the Fisher-Ullman 57-vertex graph). A1's BUILDERs supply candidate UDGs; A3 reads off $\chi_f$ certificates. Crucially A3 does not need the $\chi \ge 6$ UDG.
- **A4 (axiomatic): contact only via inheritance.** $\chi_f$ of infinite graphs uses choice-style compactness subtleties (Erdos-de Bruijn fails for $\chi_f$, Exercises 23-24); the sup-over-finite-subgraphs caveat for $\chi_f(\mathbb{R}^2)$ is a measurability/limit issue, not a full A4 phenomenon.

---

## Wrong-approach-detector check

Detectors: $\chi(\mathbb{Q}^2)=2$ (Woodall), $\chi(\ell^\infty\text{-plane})=4$ (Chilakamarri), $\chi(\mathbb{R}^1)=2$.

- **$\mathbb{Q}^2$ control.** Scheinerman-Ullman state $\mathbb{Q}^2$ is *bipartite* (Exercise 19), so $\chi_f(\mathbb{Q}^2)=\chi(\mathbb{Q}^2)=2$. The plane lower bound $\chi_f(\mathbb{R}^2) \ge 32/9$ is proved with a *specific finite UDG using $\sqrt3$ coordinates* (Moser spindles): it does NOT lift to $\mathbb{Q}^2$, because that graph does not embed in $\mathbb{Q}^2$ (the spindle needs irrational coordinates). PASS: the fractional-clique certificate is geometry-specific. A purely combinatorial fractional-clique argument that used only abstract graph structure available over $\mathbb{Q}^2$ would wrongly imply $\chi_f(\mathbb{Q}^2) > 2$; flag any such.
- **$\ell^\infty$-plane control.** Bachoc's bound depends on $N$ only through $\hat\nu$. For the Euclidean unit-distance graph the bound is driven by Bessel zeros (rotation invariance of $S^{n-1}$). For a polytopal norm ball (e.g. $\ell^\infty$), $\hat\nu$ decays differently / the optimal invariant measure is different; Kolountzakis (cited 3.3) treats *non-polytopal* balls precisely because the method's strength depends on the ball geometry. So the spectral bound genuinely uses Euclidean rotational rigidity. PASS, with a caveat: a careless application that fixes $\hat\nu$ without reference to the actual norm would not separate $\ell^\infty$ from $\ell^2$ -- flag any operator bound that ignores which $N$/norm it is built on. The detector hook is "does the bound move when you change the unit ball from a circle to a square?"
- **$\mathbb{R}^1$ control.** On $\mathbb{R}^1$, $N = \{-1, +1\}$, $\hat\nu(u) = \cos(2\pi u)$, $\inf = -1$, $\sup = 1$, so eq. 10 gives $\chi_m \ge (1-(-1))/(-(-1)) = 2$ -- exactly correct, not an over-claim. The rotation group $O(1) = \{\pm 1\}$ is essentially trivial; the method correctly returns 2. PASS: the method is *not* blind to $O(n)$; the $O(n)$-invariant optimal measure is where Euclidean structure enters, and degenerating to $n=1$ recovers the trivial answer rather than a false bound.

Verdict: the cluster is detector-clean. The one standing caution is that $\chi_f$ and the linear (single-distance) operator bound are *weak*: $\chi_f(\mathbb{R}^2) \le 4.36$ and the single-distance $\chi_m(\mathbb{R}^2)$ Bessel bound is also $< 5$. Neither, alone, can reach $\ge 5$. The strong measurable results ($\chi_m \ge 5$, recent $\ge 6$) require multi-distance / multi-measure SDP refinements layered on this framework, where the choice of distance set re-engages Euclidean rigidity more sharply.

---

## Discrepancy log (vs project atlas)

- **No contradictions found** with the project's known landmarks. The texts corroborate: Woodall $\chi(\mathbb{Q}^2)=2$ (SU Ex 19, as bipartiteness), $4 \le \chi(\mathbb{R}^2) \le 7$ (SU Sec 3.6), Moser spindle $\chi=4$ (SU Fig 3.7, called "the spindle"), 7-coloring upper bound (SU Fig 3.6).
- **Numerical note to flag for VERIFIER.** The atlas/CLAUDE.md lists $\chi_f(\mathbb{R}^2)$ targets loosely; SU pin them to $32/9 = 3.5\overline{5} \le \chi_f(\mathbb{R}^2) \le 1/0.229365 = 4.35987$. The section headline says "$3.555$" which is $32/9$ rounded down; the proof value is $32/9 \approx 3.5556$. Use $32/9$ as the certified figure.
- **Date/edition note.** SU is 1997; later work (Polymath16-era density bounds, de Grey 2018) postdates it, so SU's "no improvement in 40 years" framing and "$\chi_f(\mathbb{R}^2) \ge 4$ plausible" remark predate modern fractional/measurable improvements. The current best $\chi_f(\mathbb{R}^2)$ lower bound is higher than $32/9$ in the post-2018 literature; SU should be read as the foundational, not the current, figure. Flag for SYNTHESIZER to cross-check against the atlas's current-best table.
- **Bachoc vs project A2 ledger.** Bachoc's single-distance Euclidean bound is the *weak* measurable bound; the project's $\chi_m(\mathbb{R}^2) \ge 5$ (Falconer) and recent $\ge 6$ are stronger and come from refinements. No conflict, but the project should not cite Bachoc Sec 3.4 as the source of $\chi_m \ge 5$; it is the framework, Oliveira-Vallentin/Falconer give the sharp numbers.

---

## References to follow up

Cited by these texts, worth pulling for the A3/A2 thread:
- F.M. de Oliveira Filho, F. Vallentin, "Fourier analysis, LP, and densities of distance-avoiding sets in $\mathbb{R}^n$," JEMS 12 (2010), arXiv:0808.1822. *The sharp Euclidean density/measurable bounds; the practical engine.*
- C. Bachoc, G. Nebe, F.M. de Oliveira Filho, F. Vallentin, "Lower bounds for measurable chromatic numbers," GAFA 19 (2009), arXiv:0801.1059. *The compact-space $\vartheta$ that Sec 4 generalizes.*
- L. Lovasz, "On the Shannon capacity of a graph," IEEE IT 25 (1979). *$\vartheta$, the orthonormal-representation bound.*
- A.J. Hoffman, "On eigenvalues and colorings of graphs" (1970). *The original spectral $\chi$ bound.*
- J. Steinhardt, "On coloring the odd-distance graph," EJC 16 (2009), arXiv:0908.1452.
- M.N. Kolountzakis, "Distance sets corresponding to convex bodies," GAFA 14 (2004), arXiv:math/0303212. *Norm-ball geometry dependence -- detector-relevant.*
- A. Schrijver, "A comparison of the Delsarte and Lovasz bounds" (1979) and *Combinatorial Optimization* (2003), Thm 67.1. *$\vartheta'$ and the sandwich proof Bachoc 2.4 follows.*
- Larsen, Propp, Ullman (Mycielskian $\chi_f$ formula, SU Thm 3.3.4); Kahn-Seymour (fractional EFL).
- Croft (1967) / Hochberg-O'Donnell (1993): the density-0.229365 plane independent set.

Citing these texts (forward references to chase): Polymath16 papers; de Grey 2018; DeCorte-Golubev / DeCorte-Pikhurko measurable-$\chi$ work; recent fractional-chromatic-of-the-plane lower bounds post-2018.

---

## What this enables / what remains open

**Enables (for BUILDER / ADVERSARY / SYNTHESIZER):**
- BUILDER: search finite UDGs for high-weight *fractional cliques* (the $96{:}27$-clique pattern) to push $\chi_f(\mathbb{R}^2)$ lower bounds, and set up the operator $\vartheta$ SDP (Bachoc Thm 2.6 / eq. 10) with multi-distance measures $\nu$ on $\mathbb{R}^2$ to push the *measurable* $\chi_m(\mathbb{R}^2)$ lower bound. Both are LP/SDP-shaped, cvxpy-friendly, and need no $\chi \ge 6$ graph.
- The exact computable target: optimize $\frac{\sup_u \hat\nu(u) - \inf_u \hat\nu(u)}{-\inf_u \hat\nu(u)}$ over centrally-symmetric measures $\nu$ supported on a chosen finite distance set in $\mathbb{R}^2$. This is the concrete A2/A3 numerical experiment.
- ADVERSARY: test any proposed fractional/spectral argument against the three detectors using the hooks above (does it survive $\mathbb{Q}^2$ bipartiteness? does the bound move when the unit ball changes? does $n=1$ give 2, not more?).

**Open / limitations:**
- $\chi_f(\mathbb{R}^2) \le 4.36 < 5$: the fractional relaxation provably cannot reach the integer lower bound $\ge 5$. $\chi_f$ measures the LP-relaxation gap target, not $\chi$ itself.
- Single-distance Euclidean spectral bound is weak ($<5$). Reaching $\chi_m \ge 5$ (let alone $\ge 6$) needs multi-distance / multi-measure SDP refinements; the operator framework supports them but the sharp numerics are in Oliveira-Vallentin and successors, not in these two texts.
- The sup of $\chi_f$ over finite UDG subgraphs may not equal $\chi_f(\mathbb{R}^2)$ (SU Exercises 23-24): a genuine gap between the finite-graph LP program and the true continuous value. VERIFIER should not assume finite-subgraph $\chi_f$ sup $= \chi_f(\mathbb{R}^2)$.
- The integer bottleneck ($\chi \ge 6$ planar UDG) is untouched by A3; A3's contribution is orthogonal continuous progress on $\chi_f$ and $\chi_m$, plus the SDP machinery that may eventually corner $\chi_m \ge 6$ without ever exhibiting an integer-$\chi$-6 graph.
