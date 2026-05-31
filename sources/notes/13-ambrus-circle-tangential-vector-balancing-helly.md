# 13 - Ambrus circle, tangential: colorful vector balancing and Helly numbers of product sets

## Executive summary (6 lines)

1. Two discrete-geometry papers from the Ambrus orbit, neither about $\chi(\mathbb{R}^2)$ directly.
2. **Ambrus-Bozzai, "Colorful Vector Balancing" (arXiv:2302.10865):** signed/colorful sum bounds $\sqrt{d}$ ($\ell_2$) and $O(\sqrt{d})$ ($\ell_\infty$), proved by a Gaussian-random-walk partial-coloring argument. **Relevance verdict: tangential, weakly methodological.**
3. **Arun, "Further Bounds on the Helly Numbers of Product Sets" (2023):** Helly numbers of exponential lattices $L_2(\alpha)$ and arithmetic-congruence product sets, via empty-polygon counting. **Relevance verdict: tangential / adjacent.**
4. Shared object with the program is essentially zero (no distance graphs, no chromatic number, no Euclidean-norm rigidity used as a coloring obstruction).
5. The genuine link is sociological/methodological: same author (G. Ambrus) and same toolkit (linear dependencies / Shapley-Folkman, lattice-point pigeonhole, LP-vertex arguments) that powers the $m_1(\mathbb{R}^2) < 1/4$ density work (note 11, README).
6. One wrong-approach-detector caution applies to the Helly paper (its product-set / lattice methods would "see" $\mathbb{Q}^2$ and $\mathbb{Z}^2$ identically; never use them as a chromatic obstruction).

---

## Paper 1: Ambrus and Bozzai, "Colorful Vector Balancing" (arXiv:2302.10865 v2, 2024)

### Main results (precise)

Setup (Section 1, Def. 2.1): given vector families $V_1,\dots,V_n \subseteq B_p^d$ (unit ball of $\ell_p$ in $\mathbb{R}^d$) with $0 \in \sum_{i} \mathrm{conv}\,V_i$, select one vector $v_i \in V_i$ per family minimizing $\|\sum_i v_i\|$. This generalizes classical vector balancing (recover it by $V_i = \{\pm v_i\}$) to the "colorful" setting where each family is a color class. The relevant constant is $\mathrm{colvb}(K,L)$ (Section 7).

- **Theorem 1.4 (Euclidean):** with $V_i \subseteq B_2^d$ and $0 \in \sum_i \mathrm{conv}\,V_i$, there is a selection with $\|\sum_i v_i\|_2 \le \sqrt{d}$. This is **sharp** for $n \ge d$ and matches Spencer's classical $\mathrm{vb}(B_2^d) = \sqrt{d}$ (eq. 2).
- **Theorem 1.5 (max norm):** with $V_i \subseteq B_\infty^d$, there is a selection with $\|\sum_i v_i\|_\infty \le C\sqrt{d}$, explicit constant $C = 22$. **Asymptotically sharp**; the point is removing the $\sqrt{\ln d}$ factor that a naive probabilistic argument leaves behind.
- **Theorem 7.1 (soft reduction):** $\mathrm{colvb}(K,L) \le 2\,\mathrm{vb}(K,L)$ for any symmetric convex bodies. This recovers the $O(\sqrt{d})$ rates from the classical constants up to a factor 2, via a binary-expansion / Gram-Schmidt-walk argument attributed to the referee. The paper's own direct proof is preferred because it gives the sharp $\sqrt{d}$ (not just $O(\sqrt d)$) and an $O(d^7 \ln^2 d)$ algorithm (Prop. 6.3).

### Methods

- **Reduction to $\le d$ families (Section 2):** a Shapley-Folkman / "method of linear dependencies" argument (Theorem 2.3, built on LP basic-feasible-solution geometry, Lemma 2.4). Reduces $n$ families to $\le d$ free families with $\le k+d$ fractional coordinates. Corollary 2.5 turns any "vertex approximation" bound into a colorful balancing bound. This is the same linear-dependencies toolkit Barany surveys and that underlies several extremal-geometry arguments.
- **Euclidean case (Section 3):** a clean second-moment / probabilistic argument (Prop. 3.1). Pick $w_i$ randomly from family $i$ matching the convex weights; the expected squared error is $\le k$, so some selection achieves $\sqrt{k}$.
- **Max norm (Sections 4-6):** the crux. A **discrete-time Gaussian random walk** in coefficient space $\Delta_W$ confined to slabs, freezing coordinates as they hit the boundary (Skeleton Approximation Lemma 4.2 / 6.1). This is a partial-coloring method in the lineage of Spencer "six standard deviations", Lovett-Meka, and Bansal's Gaussian-walk discrepancy algorithms. The $\sqrt{\ln d}$ removal is exactly the discrepancy-theory trick.

### Relevance verdict: tangential, weakly methodological

- **Shared objects with HN: none of substance.** No unit-distance graph, no chromatic number, no plane-coloring. "Colorful" here means color = family, a combinatorial bookkeeping device, not a proper coloring of a graph. The Euclidean norm enters only through ball geometry, never through equilateral-triangle / pentagon rigidity, which is what any real HN argument must exploit.
- **Weak methodological transfer to A1/A3.** The Gaussian-random-walk / partial-coloring discrepancy machinery (Sections 4-6) is the same family of tools used in modern SDP-relaxation and discrepancy-driven combinatorics. If a future A3 attack ever phrases a fractional-chromatic or Lovasz-$\vartheta$ rounding problem as "round a fractional coloring to an integer one while controlling a discrepancy functional", this is a textbook reference for how to do the rounding with $\sqrt{d}$-type loss. That is speculative: the program's A3 thread (note 04, note 08) currently uses SDP / autocorrelation bounds, not discrepancy rounding.
- **Ambrus-circle link.** Gergely Ambrus is the lead author of the Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 work that reached $m_1(\mathbb{R}^2) \le 0.246894 < 1/4$, the integer $\chi_m(\mathbb{R}^2) \ge 5$ crossing the repo reproduced in L35/L36 (README, note 11). This paper shares his discrete-geometry / probabilistic-method style and the Shapley-Folkman / linear-dependencies habit, but it is not part of the density line. Treat the connection as authorship-and-toolkit, not content.

### Wrong-approach-detector check

- Largely **not applicable**: the paper proves an existence/optimization theorem, not a chromatic bound, so there is nothing to test against $\chi(\mathbb{Q}^2)=2$, $\chi(L^\infty)=4$, $\chi(\mathbb{R}^1)=2$.
- One caution worth recording: the $\ell_\infty$ result (Theorem 1.5) lives on the **max norm**, exactly the control object where $\chi = 4$. The fact that the balancing constant in $\ell_\infty$ is $O(\sqrt d)$ (same order as Euclidean) is a reminder that max-norm geometry is "soft": it does not single out the Euclidean rigidity. Any HN-style argument that, like this balancing bound, treats $\ell_2$ and $\ell_\infty$ on equal footing is structurally suspect for the chromatic problem.

---

## Paper 2: Arun, "Further Bounds on the Helly Numbers of Product Sets" (PRIMES-USA, Dec 2023)

### Main results (precise)

The Helly number $h(S)$ is the smallest $h$ such that "every $h$-wise intersecting subfamily of convex sets has a common point in $S$" forces a global common point in $S$ (Section 1). By Hoffman's theorem, for discrete $S$, $h(S)$ equals the max size of an **empty** subset (lattice points only at hull vertices). The paper studies product sets $S = A^d$.

- **Theorem 1.7 (exponential lattices, upper bound):** for $L_2(\alpha) = \{\alpha^n : n \in \mathbb{N}_0\}^2$, $\alpha > 1$, $h(L_2(\alpha)) \le 2\lceil \log_\alpha(\tfrac{\alpha}{\alpha-1})\rceil + 3$. Improves the Ambrus-Balko-Frankl-Jung-Naszodi 2023 bound (Theorem 1.6) with a shorter, more geometric empty-polygon argument; recovers exact values $h(L_2(\alpha)) = 5$ for $\alpha \ge 2$ and $= 7$ for $\alpha \in [\varphi, 2)$.
- **Corollary 2.1:** full characterization of maximal empty pentagons for $\alpha \ge 2$.
- **Theorem 1.8 (higher-dim lower bound):** $h(L_d(\alpha)) \ge \binom{k+d-1}{d-1}$ with $k = \lceil\sqrt{1/(\alpha-1)}\rceil$, via an empty polytope on the curve $x_1\cdots x_d = \alpha^k$. Asymptotically $\Omega_d((\alpha-1)^{-(d-1)/2})$, beating the product bound from Prop. 1.5.
- **Section 3:** strengthens Dillon: a 2-syndetic integer set $A$ whose square $A^2$ has an empty polygon with **infinitely many vertices** (Fibonacci/golden-ratio construction).
- **Theorems 1.9-1.11 (arithmetic-congruence sets):** for $A = \{n \equiv 0,1 \bmod k\}$, $h(A\times A) = 8$ for $k=3,4,5,6$ (mod-3 by hand, others by brute-force C++ in the appendix). General bound $h(A^d) \le k^d$ under a residue-count condition (Theorem 1.11), beating Garber in 2D and extending to higher $d$.
- **Section 5:** a Doignon-style variant for a generalized emptiness notion (Theorem 5.1: $\le 2d$ vertices when facets are simplices).

### Methods

Pure **combinatorial / extremal lattice geometry**: empty-polygon vertex counting, pigeonhole on residues modulo $m$ (the centroid / midpoint argument in Theorem 1.9), Binet's formula for the Fibonacci construction, and small brute-force search. No probabilistic method, no analysis. Self-contained and elementary.

### Relevance verdict: tangential / adjacent

- **Shared objects with HN: none.** Helly numbers measure intersection patterns of convex sets, not chromatic numbers. The "product set $A^d$" and "empty polygon" objects have no unit-distance-graph content. The pigeonhole-on-residues technique (Theorem 1.9) is the closest thing to an HN-flavored argument, and it is the same generic mod-$m$ pigeonhole that appears everywhere in lattice combinatorics; it carries no Euclidean-distance information.
- **Ambrus-circle link is one step removed.** The paper builds on Ambrus-Balko-Frankl-Jung-Naszodi 2023 (a different Ambrus paper, on Helly numbers of exponential lattices), and Arun is mentored by Travis Dillon. So this is "Ambrus circle" only via a cited Ambrus paper, not via the density/$m_1$ line. No methodological pipe into A1-A4.
- **Why it is in the corpus at all:** likely collected because it cites an Ambrus paper and lives in the same discrete-geometry community. The honest assessment is that it is adjacent literature with no transferable technique for $\chi(\mathbb{R}^2)$.

### Wrong-approach-detector check (and a real caution)

- The empty-polygon and product-set methods are **lattice-intrinsic**: they operate on $\mathbb{Z}^d$, exponential lattices, and congruence sets, and they would behave the same on $\mathbb{Q}^2$ as on any other countable affine-rational structure. They never use the metric/topology of $\mathbb{R}$ that separates $\chi(\mathbb{R}^2)=5$ from $\chi(\mathbb{Q}^2)=2$.
- **Caution flag:** any temptation to import "empty-set / Helly-number counting on a lattice" as a chromatic obstruction would fail the $\mathbb{Q}^2$ detector immediately. These are convex-intersection invariants, blind to the unit-distance relation. There is no danger of a naive lift here because no one would plausibly try it, but record it: lattice-pigeonhole arguments are exactly the kind of "combinatorial method that lifts to $\mathbb{Q}^2$" the project warns against.

---

## What this enables / what remains open

- **For BUILDER:** nothing direct. No construction, UDG, or coloring to lift. The only conceivable use is filed under "future A3 rounding": if a fractional-to-integer chromatic rounding is ever framed as a discrepancy problem, Ambrus-Bozzai Sections 4-6 (Gaussian random walk, partial coloring, $\sqrt{\ln d}$ removal) is the reference for the rounding loss. Speculative, low priority.
- **For ADVERSARY:** use Paper 1's $\ell_2$/$\ell_\infty$ symmetry as a sanity reminder: a balancing-style bound that does not distinguish the Euclidean from the max norm cannot, by itself, certify anything specific to $\chi(\mathbb{R}^2)$ as opposed to $\chi(L^\infty)=4$. Use Paper 2's lattice-intrinsic methods as a clean example of a "$\mathbb{Q}^2$-blind" technique to flag if it ever resurfaces.
- **For SYNTHESIZER:** record both as **tangential** in the atlas literature ledger. The load-bearing fact is the authorship link: G. Ambrus's density work (note 11, L35/L36) is the real HN contribution; these two are his (and his community's) adjacent output, not part of the chromatic line. No discrepancy with existing analyses.
- **Discrepancy log:** none. Neither paper makes a claim that touches the program's bounds, so there is nothing to disagree with. The only correction to prior framing is to be precise that "the Ambrus circle" spans at least three distinct lines (density/$m_1$, vector balancing, Helly numbers), and only the first feeds $\chi_m(\mathbb{R}^2)$.

### Honest caveats

- I read both extracted texts in full (Ambrus-Bozzai: history, the reduction lemma, both vertex-approximation propositions, the Gaussian-walk proof, the Section 7 reduction; Arun: all theorems, proofs, and appendix code).
- I did **not** read the cited primaries (Spencer 1981/1985, Lovett-Meka, Bansal-Dadush-Garg-Lovett, Ambrus-Balko-Frankl-Jung-Naszodi 2023, Dillon 2021). Claims about those are taken from the two papers' own statements, not independently verified.
- I am confident on the relevance verdicts; the "weak A3 methodological transfer" for Paper 1 is a judgment call, deliberately filed as speculative.
