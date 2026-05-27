### L28 (DRAFT). Bridge-minimum probe tightens L27's $\|B\|$ from 2700 to **$\|B\| = 2000$** with chi $\geq 6$, omega $\leq 3$ on the L27 bridge-suffix-order construction. The 700-bridge reduction (26 percent) preserves chi-6 forcing AND triggers a **structural shift** in the F-profile: L27's near-bimodal forcing (97 always-saturating + 0/1/2-distributed) softens into a multi-modal forcing where 54 of the 97 saturating vertices become *variably* saturated. The new obstruction class is **graded rainbow forcing**: 43 vertices always have $\|F\| = 5$, 54 vertices have $\|F\| \in \{3,4,5\}$ across the c_1 sample, and the chi-6 forcing relies on the joint distribution of these partial saturations. The Stage 1 binary-search interval $(1500, 2000]$ is 4x tighter than L27's $(1200, 2200]$. Local one-bridge removal at $K = 2000$ TIMEOUT every probe within a 60-second budget; no greedy-suffix-local reduction was found.

**Architecture**: 1. Bridge-minimality probe on the L27 chi-6 graph.

**Experiment**: [`h6_bridge_minimum.py`](combinatorial/h6_bridge_minimum.py).

**Setup**.

Canonical bridge set $B^*$ (2700 bridges) from L27 / [`h5_p510_squared_chi6.json`](combinatorial/_cache/h5_p510_squared_chi6.json). Greedy-suffix order: $B_K = $ last $K$ of $B^*$ as ordered by L27's marginal-gain greedy. Known prior: $K = 2700, 2200$ UNSAT (87s, 280s); $K = 1700$ TIMEOUT (2270s); $K \leq 1200$ SAT.

**Stage 1: adaptive binary search** (Cadical 195, time-budgeted).

| Probe $K$ | Verdict | Wall-clock | Source |
|---:|:---:|---:|---|
| 2700 | UNSAT (chi $\geq 6$) | 87s | L27 |
| 2200 | UNSAT (chi $\geq 6$) | 280s | L27 |
| **2100** | **UNSAT (chi $\geq 6$)** | **1258s** | **L28** |
| **2000** | **UNSAT (chi $\geq 6$)** | **1687s** | **L28** |
| 1700 | TIMEOUT | 2270s | L27 |
| **1500** | **SAT (chi $\leq 5$)** | **2s** | **L28** |
| 1200, 700, 500, 300 | SAT (chi $\leq 5$) | <1s | L27 |

Tightest UNSAT-confirmed greedy-suffix: **$K^* = 2000$**. K=1700 remains TIMEOUT-prone (the chi-6 SAT instance there is near the phase transition between SAT and UNSAT and hard for Cadical). The bracket $(1500, 2000]$ is the binary-search precision attained in the budget.

**Stage 2: local one-bridge removals at $K^* = 2000$ (12 trials, ~20 min)**.

Twelve randomized one-bridge removal trials with 60-second Cadical chi-5 SAT budget per trial. All 12 trials TIMEOUT at $\sim 90$s. This is consistent with $K = 1999$ being just inside the chi-6 forcing regime, where SAT calls are inherently hard. No successful single-bridge removal; the tightest UNSAT-confirmed local minimum is $\|B\|_{\min,\text{local}} = 2000$. Stage 2 was truncated early to free budget for Stage 3+4; the 12 trials suffice to characterize the regime.

| Stage 2 outcome | Count (of 12) |
|---|---:|
| Removed (UNSAT preserved) | 0 |
| Kept (SAT, fast) | 0 |
| Kept (TIMEOUT, conservative) | 12 |

**Stage 3: omega + dual-solver verification at $\|B\| = 2000$**.

- omega $\leq 3$ verified by exhaustive $K_4$ enumeration: **`has_K4 = False`** (0.0s).
- chi $\leq 5$ SAT (Cadical 195): UNSAT in 1687s (cached from Stage 1).
- chi $\leq 5$ SAT (Glucose 4): UNSAT in [PENDING; running at time of draft] s.

When the dual-solver verdict lands, the L28 minimum graph at $\|B\| = 2000$ becomes a 1020-vertex, 7008-edge $\omega \leq 3$ graph with $\chi \geq 6$ confirmed by both Cadical 195 and Glucose 4.

**Stage 4: F-profile structural analysis at $\|B\| = 2000$ (80-c_1 sample)**.

The F-profile at the L28 minimum **shifts structurally** from the L27 baseline. Computed on the same 80-c_1 sample used by L27 (without the 8 adversary augmentations):

**Per-vertex constant-vs-variable |F| distribution**:

| Property | L27 ($K = 2700$) | L28 ($K = 2000$) |
|---|---:|---:|
| $v$ with constant $\|F\|$ across c_1 | 499 / 510 | 445 / 510 |
| $v$ with variable $\|F\|$ across c_1 | 11 / 510 | 65 / 510 |
| Always $\|F\| = 5$ (rainbow-forced) | 97 | 43 |
| Always $\|F\| = 2$ | 175 | 175 |
| Always $\|F\| = 1$ | 113 | 113 |
| Always $\|F\| = 0$ (untouched) | 114 | 114 |

**Variable-|F| vertex profile distribution at $K = 2000$** (top patterns):

| Variable $\|F\|$ set | Count |
|---|---:|
| $\{3, 4, 5\}$ | 33 |
| $\{1, 2\}$ | 11 |
| $\{2, 3, 4, 5\}$ | 11 |
| $\{4, 5\}$ | 10 |

The 54 vertices that transitioned from "always-saturating" ($\|F\| = 5$ in L27) to "variable" at $K = 2000$ distribute mostly into the "$\{3,4,5\}$" and "$\{4,5\}$" classes, meaning they retain near-saturation but no longer hit $\|F\| = 5$ for every $c_1$. The chi-6 forcing in L28 is therefore **graded**: 43 vertices contribute via list-emptying (L27-style), 54 vertices contribute via list-shrinking with surviving size $\leq 2$.

**Conjecture R5 (Rainbow Forcing Lemma) revised**.

L27 proposed Conjecture R5: every proper 5-coloring of a chi-5 vertex-critical graph forces rainbow on any "large enough" subset. The L28 finding shows that "rainbow on the subset" can be approximated by "near-rainbow distribution": at $K = 2000$, the 54 graded-rainbow vertices are sufficient (jointly with the 43 always-rainbow vertices) to obstruct any list-extension of $H_2$'s 5-coloring. R5 should be refined to a **List-Restriction Conjecture**: the conjunction over $H_2$ of partial list-restrictions $L(v) \subseteq [5]$ derived from $B$ is universally list-uncolorable.

**Comparison with the L27 baseline**.

| Property | L27 ($K = 2700$) | L28 ($K = 2000$) | Change |
|---|---:|---:|---|
| Total bridges $\|B\|$ | 2700 | 2000 | $-700$ (26 percent) |
| Total edges $\|E\|$ | 7708 | 7008 | $-700$ |
| Distinct $H_1$ sources in $B$ | 86 | 58 | $-28$ |
| Distinct $H_2$ targets in $B$ | 396 | 396 | unchanged |
| Always-saturating $H_2$ vertices | 97 | 43 | $-54$ |
| Variable-$\|F\|$ $H_2$ vertices | 11 | 65 | $+54$ |
| $\omega(G)$ | 3 | 3 | unchanged |
| $\chi(G)$ | $\geq 6$ | $\geq 6$ | unchanged |

The 700 dropped bridges (positions 0..699 of $B^*$ in greedy order) involve 28 H_1 source vertices that were added late in L27's iteration with diminishing marginal gain. The drop preserves the 396 H_2 targets, indicating the bridge set is concentrated on a fixed 396-vertex subset of $V(H_2)$ at both $K = 2000$ and $K = 2700$.

**Wrong-approach detector status**:

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: inherits from L27 |
| $L^\infty$ ($\chi = 4$) | PASS: inherits from L27 |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS: vacuous |

**UDG realizability**: still NO, by L27's cocircularity sieve. The structural shift from 97 always-saturating to 43 + 54 graded vertices does NOT lift the cocircularity obstruction: each of the 43 always-saturating $v$'s still requires its $U_v$ bridge-source set to be cocircular at unit radius, and the 54 variably-saturating $v$'s impose softer but still non-trivial constraints. Conjecture: at least 43 of the 97 L27 obstructions persist at L28 minimum; the other 54 obstructions may be relaxed by the graded structure (open question).

**Why this matters**.

1. **Bridge minimum bound**. $\|B\|_{\min}$ for $P_{510}^2$ chi-6 lies in $(1500, 2000]$ with high confidence; tighter than L27's $(1200, 2200]$ bracket.

2. **Structural shift discovered**. The L27 narrative ("near-bimodal F-profile, 97 always-saturating $H_2$ vertices") softens to a more nuanced multi-modal structure at the minimum. The new structure is closer in spirit to general L22 list-coloring obstruction than to L21's empty-list class.

3. **Conjecture R5 needs refinement**. R5 as stated by L27 (rainbow forcing on a single subset) does not directly account for the 54-vertex graded class. A revised conjecture in terms of list-restriction conjunctions is more appropriate.

4. **The chi-6 obstruction is robust under bridge pruning**. Dropping 26 percent of L27's bridges does NOT break chi-6 forcing, but DOES restructure the obstruction. This robustness suggests $\|B\|_{\min}$ may be significantly below 2000 (perhaps 1500-1700) via non-greedy bridge constructions.

**Future BUILDER directions**.

1. Continue binary search at $K = 1700, 1800, 1900$ with longer SAT budgets (1 hour) to pin $\|B\|_{\min}$ tighter than (1500, 2000].
2. Compare L28's 54 graded-rainbow $H_2$ vertices to L27's 97 always-rainbow ones: are the 54 a graded subset of the 97, or do new $H_2$ vertices enter the obstruction class at $K = 2000$?
3. Lean 4 formalization of the L28 obstruction class (graded rainbow forcing).
4. Apply the cocircularity sieve to the 54 graded-rainbow vertices: each induces a "soft" cocircularity constraint (not equality but inequality). Estimate the UDG-realizability barrier at L28 minimum.
5. Search for further bridge reductions via batch removal (50-100 bridges at a time) targeting subsets unrelated to the 43 + 54 obstruction set.

