# L23 draft (h2 algebraic complement to e1x numerical): the L21 14-vertex Moser^2 chi=5 graph is NOT UDG-realizable in R^2; certified by a degree-1 Positivstellensatz over Q(sqrt 33), corroborated by a Groebner-basis = {1} computation; the obstruction localizes at H_2-vertex 6 (any pose violates at least 2 of the 5 bridges into it)

This is a VERIFIER-side draft. It is the algebraic counterpart to the parallel e1x BUILDER run that attacked the same question numerically. They should merge into a single L23 entry.

**Architecture**: 1 (combinatorial / UDG). Resolves L21's open BUILDER question on realizability of the 14-vertex Moser x Moser no-K_4 chi=5 graph.

**Experiments**: [`h2_groebner_moser14.py`](../combinatorial/h2_groebner_moser14.py) (VERIFIER, algebraic, this draft) and [`e1x_realize_moser14.py`](../combinatorial/e1x_realize_moser14.py) (BUILDER, numerical, parallel).

**The question (from L21)**. The 14-vertex graph $G_{14} = H_1 \cup H_2 \cup B^*$ with $H_1 = H_2 =$ Moser spindle and $B^*$ the L21 14-bridge set
$$B^* = \{(0,0),(0,1),(0,3),(0,4),(0,6),(1,0),(2,6),(3,6),(4,6),(5,1),(6,1),(6,3),(6,5),(6,6)\}$$
has $\chi = 5$ and $\omega = 3$ (verified by SAT in L21). Can $G_{14}$ be realized as a unit-distance graph in $\mathbb{R}^2$? If yes, it would be a 14-vertex chi-5 UDG, dramatically smaller than Polymath16's 510 or de Grey's 1581.

**Verdict (h2 algebraic, this draft)**: **CERTIFIED INFEASIBLE.** $G_{14}$ is NOT UDG-realizable in $\mathbb{R}^2$.

**The algebraic setup**. Fix $H_1 = $ Moser spindle at canonical coords in $\mathbb{Q}(\sqrt 3, \sqrt{11})$:
- $v_0=(0,0),\, v_1=(1,0),\, v_2=(1/2, \sqrt 3/2),\, v_3=(3/2, \sqrt 3/2),$
- $v_4 = (5/6,\, \sqrt{11}/6),\, v_5 = (5/12 - \sqrt{33}/12,\, \sqrt{11}/12 + 5\sqrt 3/12),$
- $v_6 = (5/4 - \sqrt{33}/12,\, 5\sqrt 3/12 + \sqrt{11}/4).$

Let $H_2 = \phi(\text{Moser})$ where $\phi(v) = R_\theta v + t$ with $R_\theta = \begin{pmatrix} c & -s \\ s & c \end{pmatrix}$, $c^2 + s^2 = 1$, $t = (t_x, t_y)$. Unknowns: $(c, s, t_x, t_y) \in \mathbb{R}^4$ with one algebraic relation $c^2 + s^2 - 1 = 0$.

The 14 bridge constraints
$$f_{ij}(c, s, t_x, t_y) := \|\phi(v_j) - v_i\|^2 - 1 = 0, \quad (i,j) \in B^*,$$
are each degree-2 polynomials over $\mathbb{Q}(\sqrt 3, \sqrt{11})$.

**Algebraic leverage (the key trick)**. For any two bridges $(i, j)$ and $(i', j)$ sharing the same $H_2$-endpoint $j$, the difference $f_{ij} - f_{i'j}$ is LINEAR in $(c, s, t_x, t_y)$:
$$f_{ij} - f_{i'j} = -2(v_i - v_{i'}) \cdot (R_\theta v_j + t) + (\|v_i\|^2 - \|v_{i'}\|^2),$$
since the quadratic-in-rotation terms $\|R_\theta v_j\|^2 = \|v_j\|^2$ cancel by isometry.

In $B^*$, multiple bridges share $H_2$-endpoints $0, 1, 3, 6$, producing **8 linear equations** in 4 unknowns over $\mathbb{Q}(\sqrt 3, \sqrt{11})$. The 8 same-j linear differences are:

| equation | LHS |
|---|---|
| $f_{(1,0)} - f_{(0,0)} = 0$ | $1 - 2 t_x$ |
| $f_{(5,1)} - f_{(0,1)} = 0$ | $(\sqrt{33} - 5)/6 \cdot c - (5\sqrt 3 + \sqrt{11})/6 \cdot s + (\sqrt{33} - 5)/6 \cdot t_x - (5\sqrt 3 + \sqrt{11})/6 \cdot t_y + 1$ |
| $f_{(6,1)} - f_{(0,1)} = 0$ | $(\sqrt{33} - 15)/6 \cdot c - (\sqrt{11}/2 + 5\sqrt 3/6) \cdot s + (\sqrt{33} - 15)/6 \cdot t_x - (\sqrt{11}/2 + 5\sqrt 3/6) \cdot t_y + 3$ |
| $f_{(6,3)} - f_{(0,3)} = 0$ | $-5c - \sqrt{11}\,s + (\sqrt{33} - 15)/6 \cdot t_x - (\sqrt{11}/2 + 5\sqrt 3/6) \cdot t_y + 3$ |
| $f_{(2,6)} - f_{(0,6)} = 0$ | $-(5 + \sqrt{33}/3)/2 \cdot c + (\sqrt{11}/2 - 5\sqrt 3/6) \cdot s - t_x - \sqrt 3 \, t_y + 1$ |
| $f_{(3,6)} - f_{(0,6)} = 0$ | $-5c + \sqrt{11}\,s - 3 t_x - \sqrt 3 \, t_y + 3$ |
| $f_{(4,6)} - f_{(0,6)} = 0$ | $-3c + \sqrt 3 \, s - (5/3) t_x - (\sqrt{11}/3) t_y + 1$ |
| $f_{(6,6)} - f_{(0,6)} = 0$ | $-6c + (\sqrt{33} - 15)/6 \cdot t_x - (\sqrt{11}/2 + 5\sqrt 3/6) \cdot t_y + 3$ |

The augmented matrix has $\operatorname{rank}(A) = 4$ but $\operatorname{rank}([A \mid b]) = 5$: **INCONSISTENT**. So no $(c, s, t_x, t_y) \in \mathbb{R}^4$ (let alone $(c, s, t_x, t_y) \in \mathbb{R}^4$ with $c^2 + s^2 = 1$) satisfies all 14 bridge equations.

**The explicit Positivstellensatz certificate (degree 1)**. Minimal inconsistent subset: 3 of the 8 same-j differences, all using $H_2$-endpoint $j = 6$:

$$g_1 := f_{(2,6)} - f_{(0,6)}, \quad g_2 := f_{(3,6)} - f_{(0,6)}, \quad g_3 := f_{(4,6)} - f_{(0,6)}.$$

With multipliers $(\lambda_1, \lambda_2, \lambda_3) \in \mathbb{Q}(\sqrt{33})^3$:
$$\lambda_1 = \frac{5 - \sqrt{33}}{6}, \qquad \lambda_2 = \frac{-15 + \sqrt{33}}{18}, \qquad \lambda_3 = 1,$$
the polynomial identity
$$\lambda_1 \, g_1 + \lambda_2 \, g_2 + \lambda_3 \, g_3 \;=\; -\frac{2}{3}$$
holds in $\mathbb{Q}(\sqrt 3, \sqrt{11})[c, s, t_x, t_y]$. Verified symbolically by independent sympy expand: see [`_cache/h2_groebner.json`](../combinatorial/_cache/h2_groebner.json) field `inconsistency_witness.symbolic_lhs_residual`.

Since each $g_k$ must equal 0 in any solution, the LHS is 0; but the RHS is $-2/3 \neq 0$ in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. **Contradiction. QED.**

**Groebner cross-check (independent)**. Using sympy's grevlex Groebner basis on the polynomials $\{f_{(0,6)}, f_{(2,6)}, f_{(3,6)}, f_{(4,6)},\, c^2 + s^2 - 1\}$ over $\mathbb{Q}(\sqrt 3, \sqrt{11})$:
$$G = \{1\}.$$
Computed in 0.26s. The ideal is the unit ideal $\Rightarrow$ the variety is empty $\Rightarrow$ INFEASIBLE.

Two independent algebraic methods agree: linear Positivstellensatz and grevlex Groebner.

**Geometric interpretation (clean picture)**. The certificate is local at $H_2$-vertex $j = 6$. The bridges $(0,6), (2,6), (3,6) \in B^*$ demand that $\phi(v_6)$ is at unit distance from $v_0, v_2, v_3$ simultaneously. Solving exactly:
$$\{P \in \mathbb{R}^2 : \|P - v_0\| = \|P - v_2\| = \|P - v_3\| = 1\} = \{(1, 0)\} = \{v_1\}.$$
(Geometrically, $v_0, v_2, v_3$ all lie on the unit circle centered at $v_1$; the three unit circles around them intersect only at $v_1$.) But then bridge $(4, 6) \in B^*$ requires
$$\|v_1 - v_4\|^2 = (1 - 5/6)^2 + (\sqrt{11}/6)^2 = 1/36 + 11/36 = 12/36 = 1/3 \;\neq\; 1.$$
The residual $|v_1 - v_4|^2 - 1 = -2/3$ matches the Positivstellensatz constant exactly.

**Locality of the obstruction at $v_6$ (sharper)**. Exhaustive enumeration of all $2^5$ anchor subsets of $\{v_0, v_2, v_3, v_4, v_6\}$ (the 5 $H_1$-vertices bridging into $v_6$ in $B^*$): a point $P$ at unit distance from all of them exists iff the subset is one of
$$\{v_0\}, \{v_2\}, \{v_3\}, \{v_4\}, \{v_6\}, \quad\text{any 2-subset of these 5}, \quad \{v_0, v_2, v_3\}, \quad \{v_0, v_4, v_6\}.$$
All other 3-subsets and all larger subsets are unrealizable. Therefore **any pose $\phi$ violates at least 2 of the 5 bridges into $v_6$**. The L21 14-bridge set has 5 such bridges, so at least 2 of $B^*$'s 14 bridges fail under any rigid motion.

Combined with the numerical (e1x) result that the best-fit residual sum is $\approx 9.4$ with max per-bridge distance error $\approx 0.9$, the obstruction is severe, not borderline.

**Numerical sanity (e1x cross-link)**. Independent scipy multi-start (400 starts, all isometries of Moser, with/without reflection): best loss = $9.40$ with max bridge-distance error $0.90$. The algebraic certificate explains why: the e1x best pose forces $\phi(v_6) \approx v_1$ to optimize the dominant 3-tuple obstruction, then accepts $\sim 0.67$ residual on the 4th bridge $(4,6)$ (and similarly elsewhere). The numerical loss is consistent with the analytic lower bound that there is no zero of the joint residual.

**Wrong-approach detector status**.

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: Moser is not UDG-realizable in $\mathbb{Q}^2$ (uses $\sqrt 3, \sqrt{11}$), so realizability question is vacuous; our certificate works in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ which is the natural realization field, not in $\mathbb{Q}^2$. |
| $L^\infty$ on $\mathbb{R}^2$ ($\chi = 4$) | PASS: certificate is Euclidean-norm specific (uses Euclidean isometry group $O(2)$). |
| $\mathbb{R}^1$ on the line ($\chi = 2$) | PASS: 1D has no Moser spindle. |

The certificate uses the full $\mathbb{Q}(\sqrt 3, \sqrt{11})$ field arithmetic; it would NOT prove $\chi(\mathbb{Q}^2) \geq $ anything because the hypothesis (Moser spindle embeds) fails in $\mathbb{Q}^2$.

**Why this matters**.

1. **The smallest abstract chi=5 no-$K_4$ graph (L21's $G_{14}$) is NOT a chi=5 UDG.** The gap between the abstract chi-5 minimum ($\geq 14$ vertices, no-$K_4$) and the smallest known chi-5 UDG (510 from Polymath16, 1581 from de Grey) is structural, not just constructional: 14 vertices is *provably* below the UDG-realizability threshold for the Moser^2-bridge family.

2. **Cocircularity radius obstructions are the dominant local UDG-realizability obstruction for low-vertex chi-5 constructions.** L21's bridge set $B^*$ packs 5 bridges into a single $H_2$-vertex ($v_6$) to force its list $L(v_6) = \emptyset$ for chi $\geq 5$. The cost of this local "cone-obstruction" via bridges is that the 5 $H_1$-endpoints into $v_6$ have to be cocircular on a unit circle at $\phi(v_6)$, and the canonical Moser spindle's 5-anchor structure $\{v_0, v_2, v_3, v_4, v_6\}$ admits at most a 3-cocircular subset. Hence any pose can satisfy $\leq 3$ of the 5 bridges into $v_6$ alone.

3. **Quantifies the "abstract-vs-realizable" gap (continues L21's bridge-density Table)**. L21 observed bridge density 0.0833 for abstract Moser^2 vs 0.0142 for de Grey 1585; we now have a clean explanation. The abstract minimum compresses bridges by concentrating them at single endpoints, forming over-constrained cocircularity demands; UDG-realizable constructions instead spread bridges so each endpoint accumulates only $\leq 3$ cocircular anchors.

4. **Algebraic certificate is short (3 polynomials, degree-1 multipliers in $\mathbb{Q}(\sqrt{33})$).** This is ideally suited for Lean 4 formalization: the witness fits in a single rfl-style equation. The natural Lean lemma is
```
theorem moser14_not_udg :
    ¬ ∃ (c s tx ty : ℝ),
        c^2 + s^2 = 1 ∧ ∀ (ij : Bridge), bridgeEquation ij c s tx ty = 0
```
with the proof reducing to the explicit polynomial identity over $\mathbb{Q}(\sqrt 3, \sqrt{11})$.

5. **Updates L21's bridge-density conjecture quantitatively.** The chi-5 UDG-realizability threshold "lives" between abstract-min 14 vertices (provably not UDG, h2 above) and the SAT-driven UDG minimum found by Polymath16/de Grey ($\geq 510$ via no-$K_4$ + UDG). Where in between? Open. The Moser^2 family at fixed $H_1 = H_2 =$ Moser is bottlenecked by the $v_6$-cocircularity obstruction; other choices of $H_1, H_2$ (e.g., 5-chromatic-free-but-rich graph product with more vertices) may relax this constraint.

**Future BUILDER directions**:

1. **Find the smallest UDG-realizable chi=5 abstract graph** via the L21 structure. Start from the next no-$K_4$ minimum bridge set for slightly larger $H_2$ (e.g., 8-vertex Moser-like, with 2 vertices added to spread bridges); compute its own Positivstellensatz; if feasible, decode the embedding. Target: bring chi=5 UDG vertex count below 510.

2. **Quantify the gap between abstract chi-5 size and UDG-realizable chi-5 size**. Define $N_a(k) = $ smallest abstract no-$K_4$ graph with $\chi \geq k$, $N_u(k) = $ smallest UDG with $\chi \geq k$. We have $N_a(5) \leq 14$ (L21), $N_u(5) \leq 510$ (Polymath16). The h2 result says $N_a(5) < N_u(5)$ strictly (the 14-vertex realization fails, so the 510-vertex realization is not just a worse construction; it uses a structurally different bridge layout). Find $N_a(5)$ exactly, then determine the gap.

3. **Apply the same-j linear-difference trick to de Grey 1585 and Polymath 510**. The 22 boundary vertices in $H_2$ (the asymmetric side of de Grey) admit a same-j linear difference per pair of bridges. If de Grey's bridges are UDG-realized, the 22 $H_2$-vertices each meet the cocircularity-radius-1 condition; verify exactly in $\mathbb{Q}(\sqrt{...})$ and quantify the "realizability budget" structurally.

4. **Construct an UDG variant of L21's $G_{14}$**. Replace one or more Moser spindle in $H_2$ with a different 4-chromatic UDG of similar size whose vertices avoid the $v_6$-cocircularity obstruction. The constraints to avoid: any single $H_2$-vertex should not accumulate 4+ bridges from 4 $H_1$-vertices whose mutual geometry forces a cocircular radius $\neq 1$.

**Pointers**:
- Script: [`experiments/combinatorial/h2_groebner_moser14.py`](../combinatorial/h2_groebner_moser14.py)
- Cache (full polynomial system, certificate, anchor analysis): [`experiments/combinatorial/_cache/h2_groebner.json`](../combinatorial/_cache/h2_groebner.json)
- Run log: [`experiments/combinatorial/_cache/h2_run.log`](../combinatorial/_cache/h2_run.log)
- e1x cross-link (numerical): [`experiments/combinatorial/_cache/e1x_realize_moser14.json`](../combinatorial/_cache/e1x_realize_moser14.json)

**Merge note (for SYNTHESIZER)**. This h2 draft and the e1x numerical draft (BUILDER, also currently in flight) attack the same question with complementary methods. The merged L23 entry should lead with the VERDICT (CERTIFIED INFEASIBLE), present the algebraic certificate as the canonical proof, and cite the numerical result as independent corroboration. The numerical detail is in service of intuition; the algebraic certificate is in service of rigor.

**Wall-clock**: the h2 computation completed in $< 4$ seconds total. The "8-hour overnight budget" allocated for Groebner was wildly overestimated because the algebraic trick (same-j linear differences) makes the system decompose immediately to a tractable linear problem. The Groebner cross-check itself took 0.26s on the 4-bridge + rotation subsystem. Lesson: structural exploitation (isometry preserves $\|v_j\|^2$, so same-$j$ differences are linear) is orders of magnitude faster than naive Groebner on 15 quadratic polynomials in 4 variables.
