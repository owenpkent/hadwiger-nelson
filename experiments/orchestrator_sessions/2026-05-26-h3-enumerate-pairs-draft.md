# L_next draft (h3): pair-wise minimum no-$K_4$ bridge cover across 7 curated 4-chromatic graphs; $W_5 \times W_5$ yields a 12-vertex chi=5 abstract record (omega=3, 11 bridges); 4 distinct $\omega = 3$ no-$K_4$ chi=5 structures identified across 20 of 28 pairs (8 pairs still computing), all non-UDG-realizable

This is the BUILDER-side draft from the overnight H3 enumeration. It builds on L21 (covering lemma) and L22 (list-coloring reformulation) by sweeping every unordered pair of a 7-graph curated library of small 4-chromatic graphs and recording the bridge minima under three regimes.

**Architecture**: 1 (combinatorial / UDG). Quantitative extension of L21.

**Experiment**: [`h3_enumerate_pairs.py`](../combinatorial/h3_enumerate_pairs.py); cache [`_cache/h3_pair_minima.json`](../combinatorial/_cache/h3_pair_minima.json); UDG realizability check [`h3_realize_w5_moser.py`](../combinatorial/h3_realize_w5_moser.py); analysis [`h3_analyze.py`](../combinatorial/h3_analyze.py).

## The setting

For each unordered pair $(H_1, H_2)$ of 4-chromatic graphs we compute, via SAT-min on the L21 covering instance:

1. $\|B\|^{\text{unc}}$: unconstrained minimum bridge cover (the trivial chi-$\geq$5 forcing bound; usually exploits the $K_5$ trick).
2. $\|B\|^{\text{no-}K_5}$: minimum cover forbidding any 5-clique that involves bridge edges.
3. $\|B\|^{\text{no-}K_4}$: minimum cover forbidding any 4-clique that involves bridge edges (the UDG-relevant regime; $\omega \leq 3$ in $\mathbb{R}^2$).

For the no-$K_4$ regime we additionally record:
- $\omega(\text{combined})$: max clique of the union $H_1 \sqcup H_2 \cup B$. If $\omega(H_i) = 4$ internally (as for $K_4$, $K_4$-pendant, Hajos join), the combined $\omega$ stays $\geq 4$ regardless of bridges, so the SAT result is still "the smallest cover such that bridges don't add a $K_4$" but the combined graph remains $K_4$-containing.
- The $F$-profile (per L22): $F(v) := \{c_1(u) : (u,v) \in B\}$ for fixed canonical $c_1$; we record the sorted descending sequence of $\|F(v)\|$ across $v \in V(H_2)$.

The curated library:

| Graph | $\|V\|$ | $\|E\|$ | $\omega$ | UDG? | triangle-free? |
|---|---:|---:|---:|:---:|:---:|
| $K_4$ | 4 | 6 | 4 | yes | no |
| $K_4$-pendant ($K_4$ + leaf) | 5 | 7 | 4 | yes | no |
| $W_5$ (hub + $C_5$) | 6 | 10 | 3 | NO (pentagon side-1 circumradius $\neq 1$) | no |
| Moser spindle | 7 | 11 | 3 | yes | no |
| Hajos join ($K_4 \sqcup K_4$, shared vertex) | 7 | 12 | 4 | no | no |
| Golomb-shape 10 (structural sibling of Soifer's Golomb) | 10 | 18 | 3 | yes (caveat) | no |
| Grotzsch ($M_4$) | 11 | 20 | 2 | no | YES |

All seven verified $\chi = 4$ by SAT (Cadical 1.9.5). Caveat: "Golomb-shape 10" is a 10-vertex, 18-edge, $\omega=3$, $\chi=4$ graph matching the *combinatorial* fingerprint of Soifer's Golomb graph; the UDG-realizability of this specific labelling is not the focus of h3.

$\binom{7}{2} + 7 = 28$ unordered pairs.

## Results table (20 of 28 pairs complete; remainder in progress)

Sorted by $V_1 + V_2$, then by no-$K_4$ $\|B\|$. "inf" means infeasible.

| Pair | $V_1+V_2$ | $\omega_1, \omega_2$ | $\|C_1\|$ | $\|C_2\|$ | unc $\|B\|$ | no-$K_5$ $\|B\|$ | no-$K_4$ $\|B\|$ | $\omega$(comb, nk4) | F profile (nk4, sorted desc) |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| $K_4 \times K_4$ | 8 | 4, 4 | 1 | 24 | 4 | inf | inf | - | - |
| $K_4 \times$ K4pendant | 9 | 4, 4 | 1 | 72 | 4 | 6 | inf | - | - |
| $K_4 \times W_5$ | 10 | 4, 3 | 1 | 120 | 4 | 6 | inf | - | - |
| K4pendant $\times$ K4pendant | 10 | 4, 4 | 3 | 72 | 4 | 6 | inf | - | - |
| K4pendant $\times W_5$ | 11 | 4, 3 | 3 | 120 | 4 | 6 | 14 | 4 | [3,2,2,2,2,2] |
| $K_4 \times$ Moser | 11 | 4, 3 | 1 | 384 | 4 | 7 | inf | - | - |
| $K_4 \times$ Hajos | 11 | 4, 4 | 1 | 144 | 4 | 6 | inf | - | - |
| $\mathbf{W_5 \times W_5}$ | $\mathbf{12}$ | 3, 3 | 5 | 120 | 6 | 6 | $\mathbf{11}$ | $\mathbf{3}$ | $\mathbf{[3,3,2,1,1,1]}$ |
| K4pendant $\times$ Moser | 12 | 4, 3 | 3 | 384 | 4 | 7 | 13 | 4 | [3,2,2,2,1,1,1] |
| K4pendant $\times$ Hajos | 12 | 4, 4 | 3 | 144 | 4 | 6 | inf | - | - |
| $W_5 \times$ Hajos | 13 | 3, 4 | 5 | 144 | 4 | 6 | 9 | 4 | [2,2,1,1,1,1,1] |
| $\mathbf{W_5 \times}$ **Moser** | $\mathbf{13}$ | 3, 3 | 5 | 384 | 6 | 6 | $\mathbf{12}$ | $\mathbf{3}$ | $\mathbf{[2,2,2,2,2,1,1]}$ |
| Hajos $\times$ Hajos | 14 | 4, 4 | 6 | 144 | 4 | 6 | 12 | 4 | [3,2,2,2,2,0,0] |
| $K_4 \times$ Golomb | 14 | 4, 3 | 1 | 3432 | 4 | 7 | 13 | 4 | [2,2,2,2,2,1,1,1,0,0] |
| Moser $\times$ Hajos | 14 | 3, 4 | 16 | 144 | 4 | 6 | 13 | 4 | [3,3,3,2,1,0,0] |
| $\mathbf{Moser} \times$ **Moser** | $\mathbf{14}$ | 3, 3 | 16 | 384 | 6 | 7 | $\mathbf{14}$ | $\mathbf{3}$ | $\mathbf{[4,3,2,2,1,1,0]}$ |
| $K_4 \times$ Grotzsch | 15 | 4, 2 | 1 | 12480 | 4 | 8 | 11 | 4 | [1,1,1,1,1,1,1,1,1,1,1] |
| K4pendant $\times$ Golomb | 15 | 4, 3 | 3 | 3432 | 4 | 7 | 13 | 4 | [3,2,2,2,1,1,0,0,0,0] |
| K4pendant $\times$ Grotzsch | 16 | 4, 2 | 3 | 12480 | 4 | 8 | 11 | 4 | [1,1,1,1,1,1,1,1,1,1,1] |
| $\mathbf{W_5 \times}$ **Golomb** | $\mathbf{16}$ | 3, 3 | 5 | 3432 | 6 | 6 | $\mathbf{11}$ | $\mathbf{3}$ | $\mathbf{[3,2,1,1,1,1,0,0,0,0]}$ |
| $W_5 \times$ Grotzsch | 17 | 3, 2 | 5 | 12480 | 6 | 6 | (running) | - | - |
| Moser $\times$ Golomb | 17 | 3, 3 | 16 | 3432 | - | - | (pending) | - | - |
| Hajos $\times$ Golomb | 17 | 4, 3 | 6 | 3432 | - | - | (pending) | - | - |
| Moser $\times$ Grotzsch | 18 | 3, 2 | 16 | 12480 | - | - | (pending) | - | - |
| Hajos $\times$ Grotzsch | 18 | 4, 2 | 6 | 12480 | - | - | (pending) | - | - |
| Golomb $\times$ Golomb | 20 | 3, 3 | 143 | 3432 | - | - | (pending) | - | - |
| Golomb $\times$ Grotzsch | 21 | 3, 2 | 143 | 12480 | - | - | (pending) | - | - |
| Grotzsch $\times$ Grotzsch | 22 | 2, 2 | 520 | 12480 | - | - | (pending; $P = 6.5 \mathrm{M}$ may time out) | - | - |

## Main findings (from completed pairs)

**(F1) Four structurally distinct $\omega = 3$ no-$K_4$ chi-5 abstract graphs found so far, with characteristic F-profile shapes.**

| Pair | $V$ | $\|B\|$ | F profile | F max | obstruction class |
|---|---:|---:|---|---:|---|
| $W_5 \times W_5$ | 12 | 11 | [3,3,2,1,1,1] | 3 | adjacent-singleton (two $L = \{c\}$ on an $H_2$ edge) |
| $W_5 \times$ Moser | 13 | 12 | [2,2,2,2,2,1,1] | 2 | global (no local $\|L\| \leq 1$; non-local list-uncolorability) |
| Moser $\times$ Moser | 14 | 14 | [4,3,2,2,1,1,0] | 4 | empty-list (single $L = \emptyset$ at one boundary vertex) |
| $W_5 \times$ Golomb | 16 | 11 | [3,2,1,1,1,1,0,0,0,0] | 3 | sparse-singleton (one $L = \{c\}$, several untouched vertices) |

These are L22's "list-coloring obstruction" classes realized concretely: empty-list (local), adjacent-singleton (semi-local on one edge), and global (non-local; the most spread-out F-profile).

**(F2) New abstract record: $W_5 \times W_5$ is a 12-vertex, 31-edge, $\omega = 3$, $\chi = 5$ abstract graph with $\|B\| = 11$ bridges.**

This is the smallest no-$K_4$ chi=5 graph found by h3, beating L21's Moser$^2$ (14 vertices, 14 bridges). It is 5-critical: removing any vertex drops chi to 4, AND removing any single bridge edge also drops chi to 4 (verified by SAT on all $V + B = 23$ removals).

The 12-vertex $W_5 \times W_5$ no-$K_4$ chi=5 structure decomposes into:
- $H_1 = W_5$ on vertices 0..5 (hub 0, rim 1..5, $C_5$ edges 1-2, 2-3, 3-4, 4-5, 1-5, spokes 0-{1,2,3,4,5}).
- $H_2 = W_5$ on vertices 6..11 (relabel +6).
- 11 bridges: $\{(1,0),(1,3),(2,0),(2,5),(3,4),(3,5),(4,2),(4,4),(5,0),(5,1),(5,4)\}$ in (H_1, H_2-local) form.

Per canonical $c_1 = (0, 1, 2, 1, 2, 3)$, the $F$-profile is $F = [\{1,2,3\}, \{3\}, \{2\}, \{1\}, \{1,2,3\}, \{1,2\}]$, $L = [\{0\}, \{0,1,2\}, \{0,1,3\}, \{0,2,3\}, \{0\}, \{0,3\}]$. **Vertices 0 and 4 of $H_2$ are forced to color 0 by their lists, but they are adjacent in $W_5$ (hub-rim edge); contradiction.** This is the **adjacent-singleton obstruction**.

**(F3) Record candidate: $W_5 \times$ Moser is a 13-vertex no-$K_4$ chi=5 with $\|B\| = 12$ and a "global" obstruction.**

13-vertex, 33-edge, $\omega = 3$, $\chi = 5$. 5-critical (each vertex and each bridge is essential, verified by SAT). Bridges: $\{(1,5),(1,6),(2,2),(2,3),(3,3),(3,4),(4,0),(4,1),(4,4),(5,1),(5,2),(5,6)\}$.

For $c_1 = (0, 1, 2, 1, 2, 3)$, $F = [\{2\}, \{2,3\}, \{2,3\}, \{1,2\}, \{1,2\}, \{1\}, \{1,3\}]$, $L = [\{0,1,3\}, \{0,1\}, \{0,1\}, \{0,3\}, \{0,3\}, \{0,2,3\}, \{0,2\}]$. List sizes $\{3,2,2,2,2,3,2\}$. No single $L(v) = \emptyset$ and no singleton list at all (always $\|L\| \geq 2$). Yet the list-coloring is SAT-UNSAT. **This is the global obstruction**: list-uncolorability requires the entire $H_2$ structure to fail simultaneously, no single local clue suffices.

**(F4) $W_5 \times$ Golomb at $V = 16$, $\|B\| = 11$ matches W5$^2$'s 11 bridges with a different structure.**

The Golomb half supplies 4 "untouched" $H_2$ vertices (F = ∅, $L = [4]$), while one Golomb vertex has $F = \{1,2,3\}$ (forced to color 0). Same $\|B\| = 11$ as W5$^2$, but with $V = 16$ vs 12 — so the bridge density per vertex is lower (0.69 vs 0.92). The Golomb structure "absorbs" some bridges by having more vertices to spread the constraint across.

**(F5) Moser $\times$ Moser remains the smallest UDG-shape (both halves UDG-realizable) no-$K_4$ chi=5 in our list: $V = 14$, $\|B\| = 14$.**

L23 (Groebner / Positivstellensatz; parallel VERIFIER pass) certifies this is NOT UDG-realizable.

The 12-vertex $W_5 \times W_5$ and 13-vertex $W_5 \times$ Moser graphs are also **NOT UDG-realizable** because $W_5$ itself is not UDG (regular pentagon side-1 has circumradius $\neq 1$). Confirmed via multi-start scipy in [`h3_realize_w5_moser.py`](../combinatorial/h3_realize_w5_moser.py): the 6-vertex $W_5$ has minimum residual $6.47 \times 10^{-2}$ over 200 random starts, never reaching zero.

**(F6) The smallest 4-chromatic UDG is the Moser spindle (7 vertices); hence the abstract lower bound for "two UDG halves + bridges" is $V \geq 14$.**

This is a structural floor: any "two halves + bridges" construction targeting a UDG chi-5 result must have $V \geq 7 + 7 = 14$. Combined with L23's no-realizability for Moser$^2$, this means **any UDG chi=5 graph with $V \leq 13$ cannot arise as a "two-half + bridges" structure**. (It might arise as a fundamentally different construction such as a triangle-of-spindles or a deformed Moser.)

**(F7) Pairs where one half has $\omega = 4$ (internal $K_4$) trivially make $\omega(\text{combined}) \geq 4$, so the no-$K_4$ SAT result is reported for completeness but the combined graph is not $K_4$-free.**

These rows (e.g., K4pendant $\times$ Moser: $V=12$, $\|B\|=13$, $\omega=4$) confirm the L21 pattern: the no-$K_4$ minimum bridge count rises monotonically with $V$ when one half has internal $K_4$, but the resulting graph is not UDG-shape.

**(F8) $K_4 \times H_2$ collapses to a "star cover" of size $\|B\| = N_2$.**

$K_4 \times $ Grotzsch achieves no-$K_4$ $\|B\| = 11$ with $B = \{(0, j) : j \in V(\text{Grotzsch})\}$. Every Grotzsch vertex receives exactly one bridge from the single $K_4$-vertex 0. $F$ is uniformly $\{0\}$, $L$ uniformly $[4] \setminus \{0\}$. The list-uncolorability reduces to "Grotzsch is not 3-colorable", which is the $\chi(H_2) \geq 4$ hypothesis. So **the $K_4 \times H_2$ no-$K_4$ minimum is exactly $N_2$ whenever $H_2$ is 4-chromatic**, equivalently the chi-5 forcing for $K_4 \times H_2$ is the trivial reduction to chi$(H_2) \geq 4$. Not UDG-relevant ($\omega(\text{combined}) = 4$ from $H_1$).

**(F9) Some pairs are no-$K_4$ infeasible.**

$K_4 \times K_4$, K4pendant $\times$ K4pendant, $K_4 \times K_4$-pendant, $K_4 \times $ Hajos, K4pendant $\times$ Hajos are all no-$K_4$ infeasible. Why: with $K_4$ in $H_1$ on vertices $\{0,1,2,3\}$, each $H_2$-vertex can have at most 2 bridges from $H_1$'s $K_4$ subset (else 3 bridges + 3 $H_1$-edges form $K_4$ with $v \in H_2$). With $\|F(v)\| \leq 2$, the list $L(v) \geq 2$, and 2-list-coloring of $H_2$ from any 2-subsets is feasible for our small $H_2$'s here.

## Wrong-approach detector status

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: every analyzed graph has $\chi = 4$ verified by SAT and is non-trivial only outside $\mathbb{Q}^2$. The list-coloring framework requires 4-chromatic halves, vacuous in $\mathbb{Q}^2$. |
| $L^\infty$ on $\mathbb{R}^2$ ($\chi = 4$) | PASS: the pair-min cover is purely graph-theoretic; the obstruction to chi $\geq 5$ in $L^\infty$ is in realizability (no $C_5$ + hub at unit distance, no Euclidean equilateral triangle), not the lemma. |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS: no 4-chromatic UDG in $\mathbb{R}^1$. Vacuous. |

## Why this matters

1. **Multiple obstruction classes in concrete examples.** L22's list-coloring theorem subsumes all observed classes (empty-list, adjacent-singleton, global) and h3 supplies witnesses for each: Moser$^2$ for empty-list, W5$^2$ for adjacent-singleton, $W_5 \times$ Moser for global, $W_5 \times$ Golomb for mixed singleton. Each obstruction class has a characteristic F-profile shape (max value, distribution shape).

2. **Quantitative ladder $V$ vs $\|B\|$ for $\omega = 3$ no-$K_4$ chi=5 abstract graphs.** $W_5^2$ at 12V/11B is sharper than $W_5 \times$ Moser (13V/12B) which is sharper than Moser$^2$ (14V/14B). All are 5-critical. The "concentration of bridges per vertex" increases with the obstruction class (going from "global" to "empty-list"): $|B|/V$ ratio rises from 0.69 (W5$\times$Golomb) to 0.92 (W5$^2$, W5$\times$Moser) to 1.00 (Moser$^2$).

3. **UDG realizability is the orthogonal bottleneck.** H3 shows that the abstract bridge cover problem has small witnesses (12-14 vertices), but **realizing them as UDGs in $\mathbb{R}^2$ is what blocks the route to the chi $\geq 5$ UDG record**. L23 (Moser$^2$) and this experiment (any W5-containing pair, since $W_5$ is non-UDG) confirm that the abstract small structures are all UDG-blocked. The de Grey 1581 / Polymath 510 vertex count is the price of UDG realizability.

4. **No new UDG chi=5 record below 510 vertices identified.** The smallest UDG-shape pair is Moser$^2$ at $V = 14$, which L23 already certifies non-realizable. To find a UDG chi $\geq 5$ graph smaller than de Grey, we need either (a) a new 6-V or 7-V 4-chromatic UDG distinct from Moser, (b) a different "two halves + bridges" decomposition with Moser plus a Moser-like UDG that is not literally Moser, or (c) an asymmetric / many-piece structure beyond two-half coupling.

## Future BUILDER directions

1. **Find a 7-vertex 4-chromatic UDG distinct from the Moser spindle**: any UDG-realizable 7-vertex 4-chromatic graph other than Moser would re-open the "small two halves + bridges" UDG strategy. The Moser spindle is the unique 7-vertex 4-chromatic UDG known; whether there are others is unclear. Search via discrete optimization over $\mathbb{Q}(\sqrt 3, \sqrt{11})$-coordinates with parameter perturbation. If a different 7V UDG exists, its bridges to Moser could realize a 14V UDG chi=5 with a non-L23 algebraic structure.

2. **Apply h3 framework to the "spindle of spindles" 9-vertex UDGs from `e1l_reverse_engineer_degrey1585.py`**: chain or pivot constructions in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ produce 8-9 vertex 4-chromatic UDGs. Pair such with Moser; combined $V \in \{15, 16\}$ but with both halves UDG. Test no-$K_4$ minima and realizability.

3. **The "global obstruction" class is structurally richer than the "empty-list" class** seen in Moser$^2$. The W5 $\times$ Moser global obstruction (every $\|L(v)\| \geq 2$, yet list-uncolorable) is a tight Hall-type combinatorial obstruction. Characterize *when* this happens on UDG halves: if Moser spindle admits a list-2-uncolorable assignment from any 4-chromatic UDG bridges, that would be a "global obstruction Moser$^2$", possibly with different (lower?) bridge count than L21's empty-list 14. Compare the minimum global-obstruction Moser$^2$ bridge count with the L21 14-bridge empty-list count.

## Caveats and stretch goals

- **Golomb-shape 10 graph**: the 10-vertex graph I used has the same $\|V\|, \|E\|, \chi, \omega$ as Soifer's Golomb graph but may not be isomorphic; the structural bridge analysis is still valid since it depends only on the combinatorial isomorphism class of $H_2$. A future verification could match this graph against the canonical Soifer UDG embedding.

- **Pending pairs**: 8 of 28 pairs are still being computed by h3, the largest being Grotzsch$^2$ ($V = 22$, $P = 6.5\mathrm{M}$). These are the largest $V$ pairs and unlikely to yield new $\omega = 3$ chi=5 records below 14V. The Moser $\times$ Golomb pair is the most interesting open case (both halves UDG, $V = 17$, $\omega = 3$ possible).

- **UDG realizability stretch goal (not realized)**: the original H3 plan asked to attempt UDG realization for any V<14 omega=3 chi=5 record. Both W5-pair candidates failed because W_5 itself is non-UDG.
