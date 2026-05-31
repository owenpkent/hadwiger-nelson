# Balogh, Chen, Li (2026): Forbidding Exactly One Hamming Distance

arXiv:2604.05607v1 [math.CO], 7 Apr 2026. Extracted text read in full (~10pp incl. appendix).

## Executive summary (6 lines)

1. The paper studies the $r$-distance graph $H_r(n)$ on $\{0,1\}^n$ (adjacency iff Hamming distance is exactly $r$), the discrete analog of the Euclidean unit-distance graph, and determines the $s$-independence number $\alpha_s(H_r(n))$ to order of magnitude for fixed $s \geq 2$ and even $r = 2t$.
2. Main result (Thm 1.4): $\alpha_s(H_{2t}(n)) = \Theta(2^n / n^t)$, with the constant pinned down for $r=2$ (Thm 1.5: $\limsup \alpha_s(H_2(n))/(2^n/n) = s-1$).
3. Method: upper bound by reduction to sunflower-free / forbidden-intersection extremal set systems (Furedi, Frankl-Furedi, Frankl-Wilson); lower bound by algebraic codes (BCH, constant-weight / Graham-Sloane) plus a random-translate first-moment argument.
4. Architecture fit: this is squarely A3-family (independence-ratio / extremal / Delsarte-LP-adjacent), with the explicit Lovasz-theta lineage noted in the intro via Castro-Silva et al.
5. Relevance verdict: TANGENTIAL to $\chi(\mathbb{R}^2)$. No direct bound; the cube is a finite, bipartite-when-$r$-odd, translation-invariant object with no $O(2)$ rotation group and trivially rational coordinates. Value is purely methodological.
6. Transferable ideas: the layer-transfer (Bassalygo) reduction, the "$s-1$ random translates" union construction for $\alpha_s$ from $\alpha$, and the sunflower-Turan packaging of $K_s$-free sets. These are A3 toolbox items, not Euclidean bounds.

## What the paper actually proves (lemma level)

### Setup and conventions
- $H_r(n)$: $V = \{0,1\}^n$, $E = \{\{x,y\} : d_H(x,y) = r\}$. $H_1(n)$ is the ordinary Hamming graph (lines 23-33).
- For odd $r$, $H_r(n)$ is bipartite (parity of weight), so $\alpha_3 = 2^n$ trivially; hence the paper restricts to even $r = 2t$ (lines 34-36). This is the discrete shadow of the fact that bipartiteness kills the question, the opposite of the Euclidean situation where odd-cycle obstructions drive $\chi \geq 3$.
- $\alpha_s(G)$ = max size of a vertex set spanning no $K_s$ (the "$s$-independence" / $K_s$-free number). $\alpha_2 = \alpha$ is the ordinary independence number (lines 66-73). For $s = 3$ this is the "triangle-free subset" question of Castro-Silva-de Oliveira Filho-Slot-Vallentin and Mukkamala (lines 37-39, 51-54).
- $L_k = \{x : |x| = k\}$, the $k$-th layer; $L_k^r$ is the induced subgraph (lines 191-195).

### Prior art the paper improves on
- Mukkamala [27]: $\alpha_3(H_r(n)) = \Omega(2^n/n^{3r/4})$ (probabilistic) and $O(2^n/n)$ (lines 51-54). The new $\Theta(2^n/n^t)$ closes the gap for fixed $r$, large $n$.
- Bassalygo-Cohen-Zemor [4,9] (Thm 1.3): the ordinary independence number $\alpha(H_{2t}(n)) = \Theta(2^n/n^t)$, constant depending on $r$ (lines 74-81). The new work shows the $K_s$-free relaxation does not change the order of magnitude, only the constant.

### Upper bound machinery (Section 4)
- **Lemma 2.5 (Bassalygo layer-transfer).** $\alpha_s(H_{2t}(n)) \leq \frac{2^n}{\binom{n}{k}} \cdot \alpha_s(L_k) = \frac{2^n}{\binom{n}{k}} \cdot m_s(n,k,k-t)$ (lines 196-246). Proof is a clean double-count / averaging over translates $v \in \{0,1\}^n$: every pair $(x,y) \in F \times \binom{[n]}{k}$ is hit by a unique translate, so some translate sees a $\geq |F|\binom{n}{k}/2^n$ fraction landing in one layer, and translation preserves $d_H$ hence $K_s$-freeness. This is the key reduction from cube to a single layer.
- On a layer, a $K_s$-free set is exactly a $k$-uniform family with no $s$ sets pairwise intersecting in $k-t$ (since $d_H(1_A,1_B) = 2(k - |A\cap B|)$, line 89-97), i.e. $m_s(n,k,\ell)$ with $\ell = k-t$.
- **Lemma 2.3 + Theorem 2.2 (sunflower Turan).** $m_s(n,k,\ell) \leq \mathrm{ex}(n, S^{(k)}_\ell(s)) = O(n^{\max\{\ell, k-\ell-1\}})$ (Furedi [20], Frankl-Furedi [18,17]; lines 146-179). A set of $s$ sets pairwise intersecting in exactly $\ell$ with the right structure is a sunflower with $s$ petals and kernel size $\ell$; forbidding $K_s$ forbids the sunflower, so the Turan number caps $m_s$.
- **Thm 1.4 upper bound (lines 350-385):** take $k = 2t-1$, $\ell = t-1$. Then $m_s(n,2t-1,t-1) = O(n^{t-1})$ and $\binom{n}{2t-1} = \Theta(n^{2t-1})$, giving $\alpha_s \leq 2^n \cdot O(n^{t-1})/\Theta(n^{2t-1}) = O(2^n/n^t)$.
- **Thm 1.5 ($r=2$) sharp constant (lines 387-400):** $t=1$, $k=1$, $m_s(n,1,0) = s-1$ (you cannot have $s$ singletons pairwise intersecting in $0$ elements... actually $s-1$ singletons is the max $K_s$-free family of points). Gives $\alpha_s(H_2(n)) \leq (s-1)2^n/n$.
- **Thm 1.7 (explicit constants via Frankl-Wilson):** for $t+i$ a prime power, $\alpha(H_{2t}(n)) \leq \big(\frac{(2t-1+i)!}{(t-1+i)!} + o(1)\big) 2^n/n^t$, using Frankl-Wilson Thm 2.4 with $q = t+i$ on the layer $k = 2t-1+i$ (lines 137-143, 401-422). This beats the constant-free Thm 1.3.

### Lower bound machinery (Section 3 + Appendix)
- **Lemma 3.3 (random-translate union, the reusable gadget).** For any Hamming-distance graph $G$ (adjacency depends only on $d_H \in D$) and any independent set $I$, $\alpha_s(G) \geq (s-1)|I|(1 - \frac{s-2}{2}\frac{|I|}{2^n})$; in particular $\alpha_s \geq (s-1+o(1))\alpha(G)$ when $\alpha(G) = o(2^n)$ (lines 275-339). Proof: take $S = I \cup (I+u_1) \cup \cdots \cup (I+u_{s-2})$ for random $u_j$. Translation invariance over $(\mathbb{Z}/2)^n$ makes each translate independent, so a union of $s-1$ independent sets is $K_s$-free; first-moment / inclusion-exclusion controls overlaps ($\mathbb{E}|I+u_i \cap I+u_j| = |I|^2/2^n$). This is how you boost $\alpha$ to $\alpha_s$ "for free" up to the factor $s-1$.
- **Independent-set source 1 (BCH black box):** there is an independent set of size $(1+o(1))2^n/n^t$ in $H_{2t}(n)$ (lines 342-344, ref [26]). Plug into Lemma 3.3.
- **Independent-set source 2 (constant-weight / coloring, Appendix Prop 5.1):** an explicit BCH-style $\mathbb{F}_2$-linear map $\Phi(x) = (S_1(x), S_3(x), \ldots, S_{2t-1}(x))$ into $\mathbb{F}_{2^m}^t$ whose fibers $C_b$ are independent sets, giving a proper coloring $\chi(H_{2t}(n)) \leq N^t = 2^{\lceil \log_2 n\rceil t}$ (lines 514-653). The fiber-is-independent claim (Claim 5.2) is a Vandermonde / power-sum argument: if $x,x'$ share a fiber, $y = x \oplus x'$ has $S_\ell(y) = 0$ for all $\ell \in [2t]$ (using $S_{2j} = S_j^2$ in char 2), forcing weight $\geq 2t+1$ by nonsingular Vandermonde. When $n$ is a power of $2$ (or one less) the color classes are equal-sized.
- **Graham-Sloane Thm 2.6 + prime gaps (Thm 2.7, Baker-Harman-Pintz).** $\chi(L_k) \leq n^t$ for $n$ prime, extended to all large $n$ by the prime in $[n, n+n^{0.525}]$ gap result (lines 247-264, Cor 3.1). Then Lemma 3.2 partitions layers into $t+1$ classes with no cross-edges to get $\chi(H_{2t}(n)) \leq (t+1)\max_k \chi(L_k)$.
- **Thm 1.6 lower bounds:** (i) $\alpha_s \geq (\frac{s-1}{t+1}+o(1))2^n/n^t$ by taking the $s-1$ largest color classes of a $(t+1+o(1))n^t$-coloring (color classes are independent, union of $s-1$ of them is $K_s$-free); (ii) sharper $(s-1+o(1))2^n/n^t$ along subsequences via the equal-size BCH coloring (lines 124-134, 340-347).

## Architecture mapping

- **A3 (fractional / Lovasz theta / independence ratio): primary fit.** The whole paper is about independence-type numbers of a distance graph, the Delsarte-LP / theta-body framework is explicitly the motivating context (Castro-Silva et al. [7], Lovasz [25], Grotschel-Lovasz-Schrijver [22], lines 55-60, 98-99). The $\alpha_s$ generalization of $\alpha$ parallels the project's interest in fractional and $K_s$-free relaxations.
- **A2 (measurable / spectral): adjacent.** The Delsarte LP / association-scheme angle (lines 98-99) is the discrete analog of the Fourier / autocorrelation bounds used for $\chi_m(\mathbb{R}^2)$ (Falconer, the cube's eigenvalue bounds are the Krawtchouk-polynomial analog of the plane's Bessel-function autocorrelation). The intro even names "minima of Krawtchouk and Hahn polynomials" (line 38). But this paper does NOT execute a spectral/Fourier argument; it routes around it via sunflower-Turan and codes.
- **A1 (combinatorial UDG): no fit.** No geometric realization, no rigidity, no equilateral-triangle / pentagon structure. The cube graph is vertex-transitive and translation-invariant in a way the Euclidean UDG is not.
- **A4 (axiomatic): no fit.** Finite graphs throughout; no choice / measurability subtleties.

## Wrong-approach detector check

The three HN control objects are $\mathbb{Q}^2$ ($\chi=2$), $L^\infty$ on $\mathbb{R}^2$ ($\chi=4$), $\mathbb{R}^1$ ($\chi=2$). This paper does not target $\chi(\mathbb{R}^2)$, so the detectors do not apply as a falsification test of a Euclidean claim. The honest statement: the methods here are intrinsically discrete and do not "engage" any of the three controls, because the controls are continuous-geometry probes and the cube is a finite combinatorial object.

Two structural cautions for anyone tempted to port these methods to the plane:
- **Translation invariance is load-bearing.** Lemma 3.3 and the layer-transfer (Lemma 2.5) both lean on the abelian group action of $(\mathbb{Z}/2)^n$ on the vertex set, with the uniform counting measure. The Euclidean plane has $\mathbb{R}^2$ translations too, so this part could analogize. But the cube has NO continuous rotation group, so any argument that secretly only uses translations would also apply to $\mathbb{Q}^2$ and to $\mathbb{R}^1$, and would therefore be detector-failing if it claimed a Euclidean lower bound. The cube methods give independence numbers, not chromatic lower bounds for the plane, so they do not actually trip the detector; but a naive transfer would.
- **Bipartite-when-odd.** The cube's $r$-odd bipartiteness (line 35) has no Euclidean counterpart; the Euclidean unit-distance graph is famously full of odd cycles (Moser spindle). So the "even $r$" restriction is a cube-specific phenomenon, not transferable.

## Transferable techniques (methodological cross-pollination)

1. **The $s-1$ random-translate boost (Lemma 3.3).** Generic for any vertex-transitive distance graph: $\alpha_s \geq (s-1+o(1))\alpha$ when $\alpha = o(|V|)$. The Euclidean unit-distance graph on a torus / lattice quotient is translation-invariant; if the project ever studies $K_s$-free (rather than independent) subsets of finite UDGs (e.g. for fractional-coloring LPs that forbid small cliques), this gadget transfers verbatim. Relevant to A3 fractional-relaxation experiments.
2. **Layer-transfer / averaging reduction (Lemma 2.5).** The "average over translates, land in one slice" move is a standard density-increment that has analogs in measurable colorings of $\mathbb{R}^2$ (averaging a coloring over translations to get a periodic/measurable one). Conceptually adjacent to A2 density arguments, though the slicing-by-Hamming-weight is cube-specific.
3. **Sunflower-Turan packaging of $K_s$-free.** Recognizing that "$s$ pairwise-equal-intersection sets" = sunflower, hence cliques in a distance graph are controlled by sunflower Turan numbers (Lemma 2.3). Tangential to Euclidean work, but if A3 ever encodes the plane's clique structure via set systems (it does not currently), this is the relevant extremal-set-theory hook.
4. **Frankl-Wilson modular intersection bound (Thm 2.4).** This is the same Frankl-Wilson theorem that underlies the Frankl-Wilson / Raigorodskii lower bounds for $\chi(\mathbb{R}^n)$ in HIGH dimension (exponential lower bounds via $\{0,1\}^n$ embeddings). That high-dimensional HN lineage IS a genuine connection: the same modular-intersection / forbidden-intersection technology that powers Thm 1.7 here is what gives the best known $\chi(\mathbb{R}^n) \geq (1.239\ldots)^n$ type bounds. See follow-ups below. This is the strongest real bridge in the paper, but it lives in $\mathbb{R}^n$ for large $n$, not $\mathbb{R}^2$.

## Discrepancy log

No direct conflict with the atlas; the paper is off-axis from $\chi(\mathbb{R}^2)$. One nuance worth flagging to SYNTHESIZER: the project's A3 framing emphasizes Lovasz $\vartheta$ / spectral bounds. This paper deliberately AVOIDS the SDP/theta route (which Castro-Silva et al. used) in favor of sunflower-Turan and codes, and gets the sharp order of magnitude that the theta-body relaxation did not pin down. Methodological takeaway: for distance graphs, extremal-set-system bounds can beat SDP relaxations on the constant/order. If the atlas claims theta is the strongest general tool for distance-graph independence numbers, that should be softened.

## What this enables / what remains open

Enables:
- For BUILDER: the random-translate union (Lemma 3.3) is a ready-made gadget if any A3 experiment wants $K_s$-free subsets of a finite, translation-invariant UDG-like graph. Cite lines 275-339.
- For ADVERSARY: a clean "detector" talking point. Any proposed Euclidean lower-bound argument whose only group input is translation (no rotation, no rigidity) is suspect, because the cube admits strong independence-number results from translation alone yet has $\chi$ growing only polynomially (poly in $n$, i.e. $\sim n^t$ colors for $2^n$ vertices), with no plane-style $\chi \geq 5$ rigidity.
- For SYNTHESIZER: a pointer to the Frankl-Wilson high-dimensional HN connection ($\chi(\mathbb{R}^n)$ exponential lower bounds) as the one place this set-system technology genuinely touches Hadwiger-Nelson.

Open / follow-up to read (cited here, NOT yet read by me):
- Mukkamala, "Triangle-free subsets of the Hypercube", arXiv:2506.18782 [27]: the immediate predecessor with the $\alpha_3$ bounds; would clarify the $s=3$ baseline.
- Castro-Silva, de Oliveira Filho, Slot, Vallentin, "A recursive theta body for hypergraphs", Combinatorica 43.5 (2023) [7]: the SDP/theta source and where Question 1.1 originates; directly A3-relevant and worth a separate dossier on whether the recursive theta body transfers to Euclidean UDGs.
- Bohman, Michelen, Mubayi, "The largest $K_r$-free set of vertices in a random graph", arXiv:2603.16454 [5]: the random-graph $\alpha_s$ analog; methodological only.
- Frankl-Wilson, Combinatorica 1.4 (1981) [19]: the modular intersection theorem; the genuine bridge to $\chi(\mathbb{R}^n)$ lower bounds. Highest-priority follow-up for any A3 high-dimensional thread.
- Linz, "Set systems containing no singleton intersection and the Delsarte number", arXiv:2604.00418 [24]: connects forbidden-intersection set systems to the Delsarte LP number; the most A2/A3-bridging citation.

Honest limitation of these notes: I read the extracted text in full but did not consult any of the cited references; all attributions above are as stated in the paper. The Frankl-Wilson / $\chi(\mathbb{R}^n)$ connection is my own contextual annotation, not claimed by the authors, and should be verified before relying on it.
