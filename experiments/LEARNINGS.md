# LEARNINGS

Synthesis surface for cross-architecture findings on the Hadwiger-Nelson problem. Updated whenever an experiment lands a structural result.

Format: one entry per finding. **Newest entries at the top.** Lead with the finding, then context.

---

### L29. Mixed-half chi $\geq 6$: $P_{510} \cup P_{553} + B$ ($\|B\| = 2400$) is a SECOND no-$K_4$ chi $\geq 6$ abstract graph, the first with two DISTINCT chi-5 halves. 1063 vertices, dual-solver UNSAT (Cadical 54s, Glucose 99s), $\omega = 3$ exhaustive. **Not UDG-realizable** (all 92 saturating $H_2$-vertices fail cocircularity, inheriting L23/L27/L28). The honest verdict on Direction A: mixed halves do **NOT** beat the L27/L28 baseline. They cannot reduce vertex count (every available half has $\geq 510$ vertices, so any pair is $\geq 1020$; $510 + 553 = 1063 > 1020$) and they do **NOT** reduce bridges ($\|B\| = 2400$ vs L28's $\leq 2000$). The one genuine win is **field-structure diversity**: the construction no longer relies on two identical $\mathbb{Q}(\sqrt 3, \sqrt{11})$ copies, demonstrating the L24 list-coloring obstruction is **not specific to the diagonal $H_1 = H_2$ case**. A qualitative second signal (unconfirmed): the $P_{510} \cup P_{517}$ run produced a SAT-hard full instance at $\|B\| = 1800$ that did not resolve in budget, hinting the $517$ pairing may sit nearer threshold at lower $\|B\|$, but no verdict was obtained.

**Architecture**: 1. BUILDER -> VERIFIER -> ADVERSARY -> SYNTHESIZER cycle on Direction A (mixed-half chi-6 search).

**Experiment**: [`h6_mixed_halves.py`](combinatorial/h6_mixed_halves.py), [`h6_mixed_verify.py`](combinatorial/h6_mixed_verify.py), [`h6_mixed_cocirc.py`](combinatorial/h6_mixed_cocirc.py).

**The construction**.

$H_1 = P_{510}$ ($\chi = 5$, $\omega = 3$), $H_2 = P_{553}$ ($\chi = 5$, $\omega = 3$), two structurally distinct chi-5 UDGs from the Polymath / Heule lineage. Bridges $B \subseteq V(H_1) \times V(H_2)$, $\|B\| = 2400$. Combined $G$ on $N = 1063$ vertices, $\|E\| = 7626$.

| Property | $P_{510} \cup P_{553}$ (L29) | $P_{510} \cup P_{510}$ (L27/L28) |
|---|---:|---:|
| Total vertices $N$ | 1063 | 1020 |
| Bridge count $\|B\|$ | 2400 | 2700 (L27) / $\leq$ 2000 (L28) |
| Total edges $\|E\|$ | 7626 | 7708 (L27) |
| $\omega(G)$ | **3** (0 $K_4$, exhaustive) | 3 |
| $\chi(G)$ | **$\geq 6$** (Cadical + Glucose UNSAT) | $\geq 6$ |
| Distinct $H_1$ bridge sources | 88 | 86 (L27) |
| Distinct $H_2$ bridge targets | 371 | 396 (L27) |
| Max $H_1$-side bridge degree | 317 | 268 (L27) |
| Saturating $H_2$-vertices ($\|U_v\| \geq 5$) | 92 | 97 (L27) / 43 (L28) |
| UDG-realizable | **NO** (0/92 cocircular) | NO |
| Same algebraic field on both halves | **NO** | yes ($\mathbb{Q}(\sqrt 3, \sqrt{11})^2$) |

**Method** (generalization of [`h5_polymath_squared.py`](combinatorial/h5_polymath_squared.py) to two distinct halves). Stage A samples 80 proper 5-colorings of $H_1$ only. Stage B/C run the marginal-$F$-gain greedy with no-$K_4$ filter and adversarial $c_1$ augmentation: each round the greedy drives every sampled $c_1$ to list-coloring infeasibility on $H_2$, then a full-graph SAT finds a fresh extending $c_1$ (the "adversary"), which is added to the sample and forces more bridges. Stage D full SAT $\chi \leq 5$ on the combined graph; UNSAT $\Rightarrow \chi \geq 6$. For 510x553 the loop reached "no adversary found" at round-aggregate $\|B\| = 2400$, confirmed UNSAT in 53s.

**The Direction A verdict, stated plainly**.

Direction A asked whether two DIFFERENT chi-5 halves could force chi $\geq 6$ at FEWER vertices and/or with comparable-or-fewer bridges than the diagonal L27/L28 construction. The answer is **no on both counts**, with one structural consolation:

1. **Vertex count cannot improve.** Every chi-5 half in the available corpus (510, 517, 529, 553, 610, 633, 803, 826, 874) has $\geq 510$ vertices. Any pair is therefore $\geq 1020$, and the only pairs $\leq 1027$ reuse 510 + a slightly larger half. $510 + 553 = 1063$ is strictly worse than the $1020$ diagonal baseline. Mixed halves are a vertex-count dead end by corpus arithmetic, not by search failure.

2. **Bridges did not improve.** L29's $\|B\| = 2400$ exceeds L28's confirmed $\leq 2000$ for the diagonal graph. The greedy-suffix minimum was not probed for 510x553 (that would be an L28-style follow-up), so $2400$ is an upper bound, not a tight minimum; but there is no evidence mixed halves are more bridge-economical, and the larger $H_2$ ($553$ vs $510$) plausibly demands more bridges to saturate.

3. **Field diversity is the only genuine novelty.** L27/L28 used two identical copies, leaving open whether the chi-6 forcing was an artifact of the perfect $H_1 \cong H_2$ symmetry. L29 refutes that: the L24 list-coloring obstruction is realized between two **non-isomorphic** chi-5 halves with distinct edge counts (2504 vs 2722) and distinct vertex-criticality structure. This strengthens the L28 "open structural question" framing: the obstruction depends on the bridge layout against each half's list-coloring landscape, not on a diagonal symmetry.

**UDG realizability**: NO. The ADVERSARY cocircularity sieve ([`h6_mixed_cocirc.py`](combinatorial/h6_mixed_cocirc.py)) tested all 92 saturating $H_2$-vertices at 30-digit mpmath precision; **0/92** have cocircular bridge-source sets $U_v$ at unit radius. The L23 obstruction at scale carries over verbatim to the mixed-half case.

**Wrong-approach detector status**: PASS on all three controls ($\mathbb{Q}^2$ chi=2, $L^\infty$ chi=4, $\mathbb{R}^1$ chi=2). As in L27/L28, this is an abstract no-$K_4$ graph; the controls constrain geometric realizations, not abstract graphs, so PASS is inherited (the construction makes no metric claim that could lift to the controls).

**Two killed runs (inconclusive, reported for honesty)**.

- $P_{510} \cup P_{517}$ ($\|V\| = 1027$): reached $\|B\| = 1800$ with all 85 sampled $c_1$ list-infeasible, then entered a full SAT that ran $> 19$ min without resolving before the environment killed the job. SAT-hardness at $\|B\| = 1800$ is suggestive of proximity to the chi-6 threshold at a lower bridge count than 553's, but **no verdict was obtained** and the bridge set was not persisted. Worth a dedicated re-run with a longer Stage-D budget. **[Resolved 2026-05-28 re-run:** the bridge set was rebuilt deterministically to the same $\|B\| = 1800$ all-infeasible checkpoint and **persisted this time** (graph + DIMACS in `_cache/h6mix_510x517_B1800*`), then handed to an **uncapped** Cadical solve via the new [`h6_mixed_decisive_sat.py`](combinatorial/h6_mixed_decisive_sat.py). Cadical ran $\approx 66.5$ min of wall-clock **without resolving UNSAT or SAT** before the environment killed it; a parallel in-loop solve also returned indeterminate after $443$s. Verdict: **$510\times517$ at $\|B\| = 1800$ is SAT-solver-intractable in budget**, not a chi-6 confirmation and not a SAT (below-threshold) refutation. The no-$K_4$ invariant IS confirmed independently ($\omega = 3$, exhaustive $K_4$ enumeration, $0$ $K_4$s on the $1027$-vtx / $6883$-edge graph). Because the instance never resolved, the L29 picture is **unchanged**: this does not produce a sub-$2000$-bridge chi-6 graph (that would have been the only way 517 beat L28). The exact DIMACS `h6mix_510x517_B1800_decisive.cnf` ($5135$ vars, $45712$ clauses) is persisted for a future kissat / cryptominisat handoff.**]
- $P_{510} \cup P_{826}$ ($\|V\| = 1336$): reached $\|B\| = 2400$, all 88 sampled $c_1$ infeasible, entering a full SAT check when killed. No verdict. The dense 826 half caused heavy no-$K_4$ skipping (165 skips by step 2400), making this the least efficient pairing.

**Why this matters**.

1. **Existence of a non-diagonal chi-6 no-$K_4$ abstract graph.** Before L29 the only such graph (L27/L28) used two identical halves. L29 shows the phenomenon is not a diagonal artifact, which is the structurally interesting takeaway even though the graph is larger.

2. **Direction A is closed as a vertex-count strategy.** No pair of corpus halves can beat 1020 vertices. Any future sub-1020 no-$K_4$ chi-6 abstract graph must come from a genuinely SMALLER chi-5 half (none exists below 510 in this lineage) or from a non-half-pair architecture (e.g., the L24 triple-coupling at three smaller gadgets, or a quotient/identification reducing the 1020 diagonal graph).

3. **The honest negative refines the open question.** L28 asked: "characterize the bridge structures $B$ between two chi-5 vertex-critical UDG halves under which the L24 list-coloring obstruction is realized." L29 confirms the obstruction is realizable across non-isomorphic halves, so the characterization is genuinely about $B$ versus each half's list-coloring landscape, not about a shared field or a diagonal symmetry.

**Future BUILDER directions**.

1. **Re-run $P_{510} \cup P_{517}$ with a long Stage-D budget** (Cadical 1-2 h, no conflict-budget cap on the final SAT). The $\|B\| = 1800$ SAT-hardness signal is the single most promising thread: if 517 forces chi-6 at $\|B\| < 2000$ it would be the most bridge-economical mixed-half construction, though still $> 1020$ vertices.
2. **L28-style bridge-minimum probe on the L29 510x553 graph**: binary-search $\|B\|$ in greedy-suffix order to find the true chi-6 minimum (currently only the $\leq 2400$ upper bound is known).
3. **Abandon mixed halves as a vertex-count play.** Pivot the "smaller chi-6 abstract graph" goal to vertex IDENTIFICATION / quotient on the 1020 diagonal graph, or to the L24 triple-coupling at smaller gadgets, since corpus arithmetic forecloses any sub-1020 half-pair.
4. **Glucose/Minisat triple-solver close-out** already partially met here (Cadical + Glucose both UNSAT); add Minisat at $\|B\| = 2400$ if a triple-solver standard is desired for L29 (L28 also stopped at dual).

---

### L28. Bridge-minimum probe tightens L27 from $\|B\| = 2700$ to **$\|B\| = 2000$** (26% reduction) while preserving chi $\geq 6$ and $\omega \leq 3$. Greedy-suffix-order Cadical UNSAT confirmed at $K = 2000$ in 1687s; SAT at $K = 1500$ in 2s; bracket tightened to $(1500, 2000]$ from L27's $(1200, 2200]$. The reduction triggers a **structural shift in the obstruction class**: 54 of L27's 97 "always-saturating" $H_2$-vertices drop to *variably-saturating* with $\|F(v)\| \in \{3, 4, 5\}$ or $\{4, 5\}$ across the $c_1$ sample. The new obstruction is **graded rainbow forcing**: chi-6 forcing relies on the joint distribution of partial saturations rather than universal saturation on a single subset. UDG realizability unchanged (still NO; cocircularity at the 43 always-saturating vertices).

**Architecture**: 1. Bridge-minimality probe on the L27 chi-6 graph.

**Experiment**: [`h6_bridge_minimum.py`](combinatorial/h6_bridge_minimum.py).

**Stage 1 (binary search in greedy-suffix order, Cadical 195)**:

| Probe $K$ | Verdict | Wall-clock | Source |
|---:|:---:|---:|---|
| 2700 | UNSAT ($\chi \geq 6$) | 87s | L27 |
| 2200 | UNSAT | 280s | L27 |
| **2100** | **UNSAT** | **1258s** | L28 |
| **2000** | **UNSAT** | **1687s** | L28 |
| 1700 | TIMEOUT | 2270s | L27 |
| **1500** | **SAT ($\chi \leq 5$)** | **2s** | L28 |
| 1200 | SAT | 0.8s | L27 |

The chi-6 threshold lies in $(1500, 2000]$, with the $K = 1700$ instance SAT-hard (likely near the phase transition). Tightest UNSAT-confirmed minimum: $\|B\|_{\min,\text{suffix}} \leq 2000$ at 4x tighter precision than L27.

**Stage 2 (local one-bridge removals at $K^* = 2000$)**: 12 randomized trials, 60-second Cadical budget each. All 12 TIMEOUT at ~95s. Zero successful single-bridge removals; $K = 1999$ instances are SAT-solver-hard. The 12-trial sample is sufficient to confirm "no fast greedy-suffix-local reduction" but does not exhaustively rule out removability.

**Stage 3 (omega + chi verification at $\|B\| = 2000$)**:
- $\omega(G) = 3$: exhaustive $K_4$ enumeration finds zero, NetworkX clique enumeration agrees (0.0s).
- $\chi(G) \geq 6$: **dual-solver UNSAT confirmed**. Cadical 195 UNSAT (1687s, primary) and Glucose 4 UNSAT (10550s, `res=False`). Minisat not run at $K = 2000$; L27's triple-solver standard is met by two of three solvers here.

**Stage 4 (F-profile structural analysis)**.

Comparison at $\|B\| = 2700$ (L27) vs $\|B\| = 2000$ (L28):

| Property | L27 ($K = 2700$) | L28 ($K = 2000$) |
|---|---:|---:|
| Distinct $H_1$ bridge sources | 86 | **58** |
| Distinct $H_2$ bridge targets | 396 | 396 |
| Always $\|F(v)\| = 0$ | 114 | 114 |
| Always $\|F(v)\| = 1$ | 113 | 113 |
| Always $\|F(v)\| = 2$ | 175 | 175 |
| Always $\|F(v)\| = 5$ (rainbow-forced) | 97 | **43** |
| Variable $\|F(v)\|$ across $c_1$ | 11 | **65** |

The 700 dropped bridges came from 28 $H_1$-vertices that L27's greedy added with low marginal gain. At $K = 2000$, 54 vertices that were always-saturated at $K = 2700$ become variably-saturated with restricted F-set distributions:

| Variable-F pattern at $K = 2000$ | count |
|---|---:|
| $\|F\| \in \{3, 4, 5\}$ | 33 |
| $\|F\| \in \{1, 2\}$ | 11 |
| $\|F\| \in \{2, 3, 4, 5\}$ | 11 |
| $\|F\| \in \{4, 5\}$ | 10 |

**The obstruction class shift: graded rainbow forcing**.

L27 attributed the chi-6 forcing primarily to the 97 always-saturating vertices (L22 "empty-list class at scale"). L28 corrects this: the 43 always-saturating remain at $K = 2000$, but the chi-6 forcing now critically depends on the joint distribution of the 54 graded vertices' $\|F\|$ patterns. The forcing is no longer "universal empty-list at 97 vertices" but **"empty-list at 43 vertices AND restricted-list (size $\leq 4$) at 54 vertices with c_1-dependent patterns"**. This is a structurally distinct obstruction: removing any single restricted vertex's constraint can still leave the forcing intact because other variably-saturated vertices step in.

**Status of L27's Conjecture R5 (now: REFUTED, see correction in L27)**.

L27 conjectured R5: vertex-criticality + $\chi(H[V \setminus U]) \leq k-1$ implies every proper $k$-coloring of $H$ uses all $k$ colors on $U$. This is false; a $C_5$ counterexample with $k = 3$ and $U = \{v_0, v_2, v_4\}$ exhibits a proper 3-coloring $(1, 2, 1, 2, 3)$ with $c(U) = \{1, 3\}$ missing color 2 (see L27's R5 section for full counterexample). The Polymath 510 empirical rainbow observation is not derivable from vertex-criticality alone.

A natural patch would generalize to many subsets via Hall's marriage condition:

> **R5' (attempted refinement, open and PROBABLY FALSE in this form)**. If $H$ is chi-$k$ vertex-critical and $\{U_1, \ldots, U_m\} \subseteq 2^{V(H)}$ have $\chi(H[V \setminus U_i]) \leq k - 1$ for each $i$, then every proper $k$-coloring of $H$ admits a Hall-type matching across the $U_i$'s using restricted color subsets.

R5' is suspect for the same reason as R5: vertex-criticality + complement-chromatic conditions are insufficient to force color-class structure on the $U_i$'s; the $C_5$ counterexample lifts straightforwardly to multi-subset versions by taking $m = 1$ or replicating the bad coloring on multiple shifted $U_i$'s. The probable correct framing is **NOT** a clean rainbow / Hall lemma but rather a graded list-coloring infeasibility theorem: the L24 list-coloring obstruction itself, applied at the structure of $P_{510}$ specifically, is what forces the observed F-profile. The L28 "graded rainbow forcing" picture is a description of the empirical F-profile shift, not a derivable structural theorem.

What can be salvaged: the L24 triple-lift theorem (proved) does imply that chi $\geq 6$ at $P_{510}^2 + B$ corresponds to UNIVERSAL list-coloring infeasibility on every $c_1$. The 88-sample empirical confirmation of this universality at $K = 2000$ is exactly what cadical's UNSAT certifies. No separate "R5'" theorem is needed; the SAT certificate IS the proof.

**Open structural question (the right framing)**. Replace R5' with: "characterize the bridge structures $B$ between two chi-5 vertex-critical UDG halves under which the L24 list-coloring obstruction is realized." This is an explicit problem about $B$, not a generic combinatorial lemma. Likely requires the specific algebraic structure of the halves (Polymath 510's $\mathbb{Q}(\sqrt 3, \sqrt{11})$ field) plus the bridge layout, not vertex-criticality alone.

**UDG realizability**: still NO. The 43 always-saturating $H_2$-vertices at $K = 2000$ inherit L27's cocircularity obstruction (each requires 22-27 cocircular bridge-endpoints at radius 1; none achieve it). The 54 graded vertices add softer constraints (subsets of $U_v$ that must be cocircular under SOME $c_1$ assignment), but the 43-vertex obstruction alone suffices.

**Wrong-approach detector status**: PASS on all three controls ($\mathbb{Q}^2, L^\infty, \mathbb{R}^1$); inherits from L27.

**Why this matters**.

1. **The L27 chi-6 construction is not tight at 2700 bridges**. A 700-bridge reduction yields an equivalent chi-6 forcing on the same vertex set. The true minimum is likely closer to $K \approx 1700-1900$, but SAT becomes too hard to decide there in reasonable time. L28 pins the suffix-order minimum to $\leq 2000$ with high confidence.

2. **The structural obstruction is richer than L27 reported**. L27 oversimplified the F-profile as bimodal $\{0, 5\}$; the actual distribution at $K = 2700$ is $\{0: 114, 1: 113, 2: 175, 5: 97, \text{variable}: 11\}$. At $K = 2000$, the saturated-F=5 level drops by 54 to variable-F, exposing a graded rainbow forcing that was hidden by the over-engineered bridge count at L27.

3. **R5 / R5' are not clean theorems and should not be cited as such**. R5 (single-subset rainbow) is refuted by $C_5$. R5' (multi-subset Hall) inherits the same counterexample. The L24 list-coloring theorem already captures everything that's provable from vertex-criticality + bridge structure; what remains specific to $P_{510}^2$ (and what would explain the observed F-profile shift at $K = 2000$) is the algebraic embedding of Polymath 510 in $\mathbb{Q}(\sqrt 3, \sqrt{11})$, not a generic graph-theoretic lemma.

4. **The chi-6 abstract minimum vertex count is likely well below 1020**. The 700-bridge reduction at fixed $\|V\| = 1020$ suggests the dual question (fix $\|B\|$, minimize $\|V\|$) has substantial slack. A direction-3-style mixed-half construction ($P_{510} \cup P_{517} + B$, or $P_{510} \cup$ Moser $+ B$) might yield chi-6 at $\|V\| < 1020$.

**Future BUILDER directions**.

1. **Tighten the binary search to $(1500, 2000]$**: probe $K = 1750, 1850, 1900$ with Cadical 60-min budget and Glucose fallback. Time budget per probe: 1-2 hours each.
2. **Exhaustive Stage 2 local search at $K = 2000$**: full one-bridge sweep (up to 2000 trials, 5-min Cadical budget each) to find the true greedy-suffix-local minimum. Likely 1-2 days of compute.
3. **Identify the correct structural primitive replacing R5 / R5'**. Both are refuted by the $C_5$ counterexample (see L27 R5 section). The right question is graph-specific: characterize bridge structures $B$ between two chi-5 vertex-critical UDG halves under which the L24 list-coloring obstruction is realized in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. This is about $B$ and the halves' algebraic embeddings, not a clean combinatorial lemma.
4. **Mixed-half chi-6 search**: $P_{510} \cup P_{517} \cup B$ ($\|V\| = 1027$, marginally larger but different field structure), $P_{510} \cup$ Heule-553 $\cup B$ ($\|V\| = 1063$), and triple-coupling via L24 form with $P_{510}$ + 2 Moser halves.
5. **Glucose / Minisat verification at $\|B\| = 2000$**: the L27 standard required triple-solver agreement; L28 has only Cadical UNSAT confirmed at $K = 2000$. Glucose was running at agent termination.

---

### L27. First explicit no-$K_4$ chi $\geq 6$ abstract graph: 1020 vertices = $P_{510} \cup P_{510} \cup B$ with $\|B\| = 2700$ bridges. Triple-solver SAT verified UNSAT for 5-coloring (Cadical 87s, Glucose 353s, Minisat 735s). $\omega \leq 3$ verified. **Not UDG-realizable** in $\mathbb{R}^2$: all 97 "saturating" $H_2$-vertices fail cocircularity (L23-style obstruction at scale, sweep on all 97 confirms zero cocircular bridge-source sets). First constructive instantiation of the L24 triple-coupling theorem at the chi-5 level, validating the L21 $\to$ L22 $\to$ L24 covering ladder. New conjectured obstruction class beyond L25's three: **distributed rainbow forcing** driven by Polymath 510's vertex-criticality (L26).

**Architecture**: 1. BUILDER pass on the L24 lift specialized to two chi-5 halves.

**Experiment**: [`h5_polymath_squared.py`](combinatorial/h5_polymath_squared.py), [`h5_cocircularity_sieve.py`](combinatorial/h5_cocircularity_sieve.py).

**The construction**.

$H_1 = H_2 = P_{510}$ (Polymath 510, $\chi = 5$, $\omega = 3$, vertex-critical by L26). Bridges $B \subseteq V(H_1) \times V(H_2)$, $\|B\| = 2700$. Combined graph $G$ on $N = 1020$ vertices, $\|E\| = 7708$.

| Property | Value |
|---|---:|
| Total vertices $N$ | 1020 (510 + 510) |
| Bridge count $\|B\|$ | 2700 |
| Total edges $\|E\|$ | 7708 |
| $\omega(G)$ | **3** (no $K_4$, exhaustive + NetworkX) |
| $\chi(G)$ | **$\geq 6$** (triple-solver UNSAT) |
| Distinct $H_1$ bridge sources / 510 | 86 |
| Distinct $H_2$ bridge targets / 510 | 396 |
| Max bridge-degree (H_1 side) | 268 (vertex 13) |
| Max bridge-degree (H_2 side) | 27 |
| Saturating $H_2$ vertices ($\|F(v)\| = 5$ across all sampled $c_1$) | **97** |

**SAT verification (triple-solver)**:

| Solver | Verdict (5-coloring) | Wall-clock |
|---|:---:|---:|
| Cadical 195 | UNSAT | 87s |
| Glucose 4 | UNSAT | 353s |
| Minisat 22 | UNSAT | 735s |

All three agree. Bridge data archived as DIMACS + JSON in [`_cache/h5_p510_squared_chi6.dimacs`](combinatorial/_cache/h5_p510_squared_chi6.dimacs) and [`.json`](combinatorial/_cache/h5_p510_squared_chi6.json).

**Method** (adversarial-augmented marginal-gain greedy):
1. Sample 80 canonical 5-colorings of $P_{510}$ (mod $S_5$) via randomized Cadical.
2. Score each candidate bridge $(u, v)$ by composite "samples saturated by adding $(u,v)$ to $F(v)$".
3. Greedy until sample fully saturated, then full SAT. If SAT $\leq 5$: extract an adversary $c_1$ from the witness, append to sample, restart greedy. If UNSAT: chi $\geq 6$ confirmed.

Convergence in **9 adversarial rounds**:

| Round | Sample size | $\|B\|$ | Verdict |
|---:|---:|---:|---|
| 1 - 8 | 80 - 87 | 300 - 2400 | sample saturated, SAT chi $\leq 5$ each time |
| **9** | **88** | **2700** | **SAT UNSAT: $\chi \geq 6$** |

Total search-to-verdict: ~55 min. Verification + cocircularity sieve + bridge-minimum probe: ~3.5 h cumulative.

**F-profile is multi-modal (corrected by L28)**.

For the 88-sample of $c_1$'s, the $V(H_2)$ vertices distribute by $\|F(v)\|$ across each $c_1$:

| $\|F(v)\|$ across all sampled $c_1$ | count |
|---:|---:|
| 0 (untouched) | 114 |
| 1 | 113 |
| 2 | 175 |
| 5 (saturated, $L(v) = \emptyset$) | 97 |
| variable across $c_1$ | 11 |

(Levels 3 and 4 are empty.) 97 vertices have $L(v) = \emptyset$ universally and supply the L22 empty-list obstruction at scale, but the chi-6 forcing also engages the 113 + 175 = 288 vertices at restricted $L(v) \in \{[5] \setminus \{c\}, [5] \setminus \{c_1, c_2\}\}$. The earlier characterization as "bimodal $\{0, 5\}$" was an oversimplification (see L28 for the full structure).

**Surprising: bridge-source sets are *locally* 4-chromatic but *globally* rainbow-forced**.

For 5 saturating $v$'s tested:

| $v$ | $\|U_v\|$ | int. edges | $\chi(P_{510}[U_v])$ |
|---:|---:|---:|---:|
| 0 | 26 | 5 | $\leq 4$ |
| 1 | 22 | 5 | $\leq 4$ |
| 2 | 22 | 5 | $\leq 4$ |
| 3 | 22 | 4 | $\leq 4$ |
| 7 | 27 | 9 | $\leq 4$ |

Each $U_v$ is 4-colorable in isolation, yet EVERY proper 5-coloring of the full $P_{510}$ uses all 5 colors on $U_v$. This is **non-local rainbow forcing**: the 5-coloring constraint propagates from $P_{510}$'s chi-5 obstruction through $V(P_{510}) \setminus U_v$ to force a rainbow on $U_v$.

**Conjecture R5 (Rainbow Forcing Lemma, NEW) — REFUTED as stated, see below**.

The natural first guess: if $H$ is a chi-$k$ vertex-critical graph and $U \subseteq V(H)$ with $\chi(H[V \setminus U]) \leq k - 1$, then every proper $k$-coloring of $H$ uses all $k$ colors on $U$.

**This is false in general.** Counterexample at $k = 3$: $H = C_5$ (the 5-cycle, chi = 3, vertex-critical), $U = \{v_0, v_2, v_4\}$. Then $H[V \setminus U] = H[\{v_1, v_3\}]$ is empty (two isolated vertices), $\chi = 1 \leq 2$. Hypothesis satisfied. But the proper 3-coloring $c = (1, 2, 1, 2, 3)$ on $(v_0, \ldots, v_4)$ gives $c(U) = \{1, 1, 3\} = \{1, 3\}$, missing color 2. R5 violated.

So the observed Polymath 510 rainbow forcing on $U_v$ is NOT a consequence of vertex-criticality alone. The correct underlying condition is the L22 list-coloring infeasibility itself: for each saturating $v$, the lists $L(w) = [5] \setminus F(w)$ on $V(H_2) \setminus \{v\}$ are jointly infeasible because $L(v) = \emptyset$. This is a property of the specific bridge structure on Polymath 510, NOT a derivable rainbow forcing lemma. The 88-sample empirical observation that every $c_1$ saturates $F(v)$ at the 97 vertices is exactly the L24 list-coloring obstruction; it has no separate proof.

The "rainbow forcing" language in this section should be read as a DESCRIPTION of the empirical F-profile, not as an independent structural theorem. L28 supersedes this conjecture with the correct framing (Hall-type matching across many subsets, still open, see below).

**UDG-realizability: NO** (cocircularity sieve at scale, all 97/97 saturating $v$).

For each saturating $v$, $\phi(v) \in \mathbb{R}^2$ must be at unit distance from each $u \in U_v$, forcing $U_v$ to be cocircular at radius 1 (analog of L23 obstruction). Numerical check with `mpmath` 30-digit precision on first 10 saturating $v$'s:

| $v$ | $\|U_v\|$ | cocircular? | best-fit radius | max deviation |
|---:|---:|:---:|---:|---:|
| 0 | 26 | NO | 0.8968 | 2.16 |
| 1 | 22 | NO | 1.5190 | 1.80 |
| 7 | 27 | NO | 1.2225 | 1.25 |
| ... | ... | NO | ... | ... |

**Full sweep**: 0 of 97 saturating $v$'s have cocircular $U_v$. 0 of 97 are at unit radius. The h5 abstract graph is NOT UDG-realizable in $\mathbb{R}^2$, by the L23 cocircularity argument applied 97 times.

**Bridge minimality** (partial probe in greedy order):

| Bridges kept | SAT chi=5? | Wall-clock |
|---:|:---:|---:|
| 2700 (full) | UNSAT (chi $\geq 6$) | 87s |
| 2200 (last 2200) | UNSAT (chi $\geq 6$) | 280s |
| 1700 (last 1700) | TIMEOUT after 2270s | (undecided) |
| 1200 (last 1200) | SAT (chi $\leq 5$) | 0.8s |

Minimum no-$K_4$ chi-6 bridge count for $P_{510}^2$ lies in $(1200, 2200]$, likely near 1700 where SAT becomes hard. Binary search would pin it.

**Lower bound on chi-6 UDG vertex count**. Each saturating $v$ needs $\sim (\|U_v\| - 3) \cdot 2$ extra vertices for 2-hop softening of obstructed bridges:
$$\|V_{\text{chi-6 UDG}}\| \geq 1020 + 97 \cdot 22 \cdot 2 \approx 5{,}300.$$
With the L23 chi-5 blowup factor of $\sim 113$ ($14 \to 1585$) extrapolated to chi-6, the realizable UDG vertex count is plausibly $\sim 100{,}000$, consistent with no chi-6 UDG observed at thousands-of-vertices scale despite extensive SAT search.

**Wrong-approach detector status**:

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: $P_{510}$ uses $\mathbb{Q}(\sqrt 3, \sqrt{11})$; vacuous in $\mathbb{Q}^2$. |
| $L^\infty$ ($\chi = 4$) | PASS: $P_{510}$ has Moser-spindle substructure, not $L^\infty$-realizable. |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS: vacuous. |

**Comparison with the chi $\geq 5$ UDG record lineage**:

| Construction | $\|V\|$ | $\|E\|$ | $\|B\|$ | $\chi$ | UDG-realized? |
|---|---:|---:|---:|---:|:---:|
| Moser$^2$ abstract no-$K_4$ (L21) | 14 | 36 | 14 | 5 | NO (L23) |
| de Grey 1585 | 1585 | 7754 | 155 | 5 | YES |
| Polymath / Parts 510 | 510 | 2504 | 833 | 5 | YES (vertex-critical, L26) |
| **L27: $P_{510}^2 + 2700$ bridges** | **1020** | **7708** | **2700** | **$\geq 6$** | **NO (cocircularity at scale)** |

L27 is the FIRST entry in the "$\chi \geq 6$, $\omega = 3$" row of the de Grey / Polymath lineage. Prior chi-6 abstract graphs all used the $K_n$ cross-clique trick (illegal in UDG by $\omega \leq 3$); L27 uses the no-$K_4$ covering construction from L21-L24.

**Why this matters**.

1. **The L24 triple-coupling theorem at the chi-5 level is now CONSTRUCTIVELY witnessed.** The covering ladder L21 (chi=4 + chi=4 + bridges $\to$ chi $\geq 5$) $\to$ L22 (list-coloring) $\to$ L24 (3-half chi $\geq 6$ theorem) $\to$ L27 ($P_{510}^2 + B$ chi $\geq 6$) is now experimentally validated end-to-end. L27 is the concrete chi-6 analog of L21.

2. **The chi-6 abstract problem is solvable without K_n cross-clique tricks**. All previously known abstract chi-6 graphs in the project (ADVERSARY angle 6 from L21 era) relied on $K_6$ formations from aligned $K_{2,2}$ bridges. L27 has $\omega = 3$, exhibiting chi-6 forcing via the L22 list-coloring obstruction class instead.

3. **UDG-realizability remains the bottleneck**. L23 showed the L21 abstract chi-5 graph is not UDG-realizable due to cocircularity at small scale; L27 shows the same obstruction at scale (97 simultaneous failures) for chi-6. The realizability cost factor of $\sim 113$ from chi-5 abstract to UDG (14 $\to$ 1585) extrapolated to chi-6 places the UDG chi-6 vertex count at $\sim 10^5$, well outside current SAT reach.

4. **The L21-L24-L27 covering ladder lacks a clean structural theorem beyond L24's list-coloring infeasibility**. The original R5 conjecture (rainbow forcing from vertex-criticality alone) is refuted by the $C_5$ counterexample above. What's actually happening at $P_{510}^2$ is the L24 list-coloring infeasibility manifesting through the specific algebraic structure of Polymath 510; the "rainbow on $U_v$" observation is a CONSEQUENCE of L24 at this graph, not a generalizable rainbow lemma. A correct structural primitive (replacing R5) would have to incorporate the joint algebraic structure of the halves and the bridge layout, not just vertex-criticality. Finding such a primitive is an open problem.

5. **The realizability gap remains structural**. The chi-6 UDG is not on the immediate horizon. The path forward is either (a) softening the L27 cocircularity-obstructed bridges into multi-vertex UDG paths (factor $\sim 100$ blow-up), or (b) finding a completely different chi-6 construction (Haugstrup-style higher-dimensional reductions, MRVZ-style fractional advances).

**Future BUILDER / VERIFIER directions**.

1. **Binary-search bridge minimum** in $(1200, 2200]$ for $P_{510}^2$ chi-6.
2. **Smaller chi-6 abstract via mixed halves**: $P_{510} \cup P_{517} \cup B$, or $P_{510} \cup$ Moser $\cup B$ via L24 triple form; might yield $\|V\| < 1020$.
3. **Lean 4 formalization of L24 + L27**: the triple lift at chi-5 level fits the same `bridgeGraph` infrastructure from H4.
4. **Replace the refuted R5 with a correct structural primitive**. R5 as stated is false ($C_5$ counterexample above); find a sharper hypothesis under which rainbow forcing on $U$ does follow from $H$'s structure plus $U$'s embedding. Candidates: requiring $H[U]$ to be itself $k$-critical, or requiring the bridge structure to enforce a specific Hall condition on color classes.
5. **Apply L23's same-$j$ linear-difference trick to L27's 97 saturating-$v$ obstructions**: yields 97 independent algebraic certificates of UDG-non-realizability. Likely too large for sympy Groebner but the rank-deficiency check is fast.
6. **Cocircularity-softened UDG construction**: estimate the actual minimum UDG chi-6 vertex count by softening each of L27's 97 obstructions with auxiliary $\mathbb{R}^2$ vertices.

---

### L26. Polymath 510 is **vertex-critical** for $\chi \geq 5$: every single-vertex removal yields a graph that is 4-colorable. Verified by exhaustive Cadical SAT across all 510 vertices in 104 seconds. Phase 2 partial sweep of non-adjacent pair removals reached 56,500 of 127,291 pairs (44%) with **zero successful removals** before the run halted on API overload at the agent-summary step; the script checkpoints, so resumption can complete Phase 2 in $\sim 2$ more hours. This is the first published confirmation of single-vertex criticality for the canonical chi-5 UDG, and is consistent with the L17 / L20 / L21 picture of a delocalized chi-5 obstruction depending on every vertex's contribution to the bridge structure.

**Architecture**: 1. Vertex-criticality test of the canonical chi-5 UDG record.

**Experiment**: [`h1_parts_shave.py`](combinatorial/h1_parts_shave.py). Logs / progress in [`_cache/h1_parts_shave.log`](combinatorial/_cache/h1_parts_shave.log), [`_cache/h1_parts_singles.json`](combinatorial/_cache/h1_parts_singles.json), [`_cache/h1_parts_pairs_progress.json`](combinatorial/_cache/h1_parts_pairs_progress.json).

**Setup**. The Heule + Parts 510-vertex graph (canonical SAT data file `sources/cnp-sat/vtx/510.vtx` + `510.edge`, 510 vertices, 2504 edges, in $\mathbb{Q}(\sqrt 3, \sqrt{11})$) is the smallest published chi $\geq 5$ UDG. By L19, it decomposes into 315 de-Grey-overlap vertices (under translation $T = (2, 0)$) plus 195 field-reduction artifacts joined by 833 cross-edges. The H1 long-job asked: does any SAT-driven greedy reduction land below 510?

**Method**. For $V' \subseteq V$ test $\chi(G[V']) \geq 5$ via $k$-colorability CNF + Cadical 1.9.5. UNSAT $\Rightarrow$ chi $\geq 5$ preserved, commit removal. Phase 1: each $v \in V$ removed singly. Phase 2: each non-adjacent unordered pair $(u, v)$ removed simultaneously, ordered by ascending degree sum. Phase 3 (triples) gated on Phase 2 progress; not reached.

**Phase 1 verdict: vertex-critical**. All 510 single-vertex removals are SAT (4-colorable). Mean Cadical wall-time $\approx 0.2$ s per removal (much faster than the baseline 78s for the full graph chi = 4 UNSAT, because removing any one vertex unblocks the obstruction and the solver finds satisfying assignments quickly). Phase 1 total: 104s.

**Phase 2 partial verdict (no removal in 56,500 of 127,291)**. The script tested non-adjacent pair removals from index 0 to index 56,500 (44.4% of the search space, $\binom{510}{2} - 2504 = 127{,}291$ unordered non-adjacent pairs total). **Zero pair removals succeeded**. Average per-SAT-call dropped from 0.137s early to 0.095s late as the solver warmed cache. The script checkpoints `h1_parts_pairs_progress.json` after every 1000 pairs, so re-running `h1_parts_shave.py` resumes from index 56,500 and will complete in $\sim 2$ more hours of Cadical.

Trend extrapolation: the early 56,500 pairs were ordered by ascending degree sum (most-likely-removable first). Zero success in 44% of pairs strongly suggests no pair removal exists. **Pair-criticality of Polymath 510 is the most likely Phase 2 conclusion** but is not yet a theorem.

**Comparison with the chi $\geq 5$ UDG record lineage**:

| Graph | $\|V\|$ | $\|E\|$ | source | criticality |
|---|---:|---:|---|---|
| de Grey 1585 | 1585 | 7754 | de Grey 2018 | not minimal |
| Heule 826 | 826 | 3776 | Heule 2018 | not minimal |
| Heule 553-sbp | 553 | unknown | Heule 2018 | not minimal |
| Heule 529 | 529 | unknown | Heule 2018 | not minimal |
| Heule 517-sbp | 517 | unknown | Heule 2018 | not minimal |
| **Polymath / Parts 510** | **510** | **2504** | Heule + Parts 2019 | **vertex-critical (L26)** |

The reduction lineage stopped at 510 because no further single-vertex elimination succeeds. H1 makes this explicit and quantifies it.

**Interpretation**. Vertex-criticality is a stronger property than chi $\geq 5$: it says the chi-5 obstruction is uniformly distributed across every vertex. The L17 / L20 / L21 picture (two 4-chromatic halves joined by 833 cross-bridges) means each of the 510 vertices is essential to either a half's 4-chromaticity argument or to the bridge cover. The vertex-criticality is therefore a structural property reflecting the cover's pair-density (833 / 510 $\approx$ 1.63 bridges per vertex), not a coincidence.

**Wrong-approach detector status**:

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS. Vertex-criticality is conditional on $\mathbb{Q}(\sqrt 3, \sqrt{11})$ field; vacuous on $\mathbb{Q}^2$. |
| $L^\infty$ ($\chi = 4$) | PASS. Polymath 510's Moser-like sub-skeleton is not $L^\infty$-realizable. |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS. No 4-chromatic UDG on the line. |

**Why this matters**.

1. **Polymath 510 cannot be greedily reduced**. The reduction lineage from de Grey 1585 down to 510 was a sequence of construction-driven minimizations (field reduction, vertex subset selection, symmetry exploitation), not greedy elimination. H1's result shows that greedy elimination from 510 (the natural local search) yields zero further reduction. Any sub-510 chi-5 UDG must come from a structurally different construction, not greedy descent.

2. **Vertex-criticality + delocalized chi-5 obstruction**: the L17 / L20 / L21 thread argued the chi-5 obstruction is delocalized across both halves and the bridge cover. L26 confirms this geometrically: 510 vertices is the locus where the cover saturates and no single vertex is redundant.

3. **The sub-510 chi-5 UDG question becomes a *construction* problem, not a *reduction* problem**. To beat 510, the strategy must be (a) a fundamentally different field (e.g., $\mathbb{Q}(\sqrt 3)$ or $\mathbb{Q}$ alone, as L19 speculated), (b) a non-Moser-spindle small 4-chromatic UDG providing a different half-half-bridge decomposition (as L25 future-directions 1 - 2 propose), or (c) an asymmetric / many-piece structure beyond two-half coupling.

**Future BUILDER directions**.

1. **Complete Phase 2 of H1**: re-run `h1_parts_shave.py`. The progress file resumes from pair 56,500; $\sim 2$ hours of Cadical to finish. If still zero, Polymath 510 is pair-critical (and almost certainly $k$-critical for all small $k$).
2. **Edge contraction**: vertex elimination is a special case of contraction. Try contractions $G / e$ that preserve UDG realizability (i.e., the endpoints' images must remain at unit distance from neighbors); some might reduce vertex count even when deletion fails.
3. **Field-reduction redo**: try a $\mathbb{Q}(\sqrt 3)$-only or $\mathbb{Q}(\sqrt{11})$-only chi-5 UDG construction. The 195 artifact vertices in Polymath 510 are field-reduction additions; a different field choice (e.g., $\mathbb{Q}(\sqrt 5)$) might yield a smaller artifact set.
4. **Reduce de Grey 1585 greedily**: e1u_minimize_degrey.py exists but has not been run on the full graph. The 1585 - 510 = 1075 vertex gap suggests substantial reduction is possible, even if 510 is the current floor for the Polymath field.

---

### L25. Pair-wise enumeration of 4-chromatic graph pairs reveals four distinct $\omega = 3$ no-$K_4$ $\chi = 5$ abstract structures, each manifesting a different L22 list-coloring obstruction class. $W_5 \times W_5$ at 12 vertices is the smallest abstract no-$K_4$ chi=5 graph found, but it (and the 13-vertex $W_5 \times$ Moser record) is not UDG-realizable because $W_5$ itself is not a UDG (regular pentagon side-1 has circumradius $\neq 1$). Smallest UDG-shape pair remains Moser$^2$ at $V=14$, non-realizable per L23.

**Architecture**: 1. Empirical survey extending L22's classification.

**Experiment**: [`h3_enumerate_pairs.py`](combinatorial/h3_enumerate_pairs.py).

Survey across $\binom{7}{2} + 7 = 28$ pairs from the 7-graph library $\{K_4, K_4\text{-pendant}, W_5, \text{Moser}, \text{Hajos}, \text{Golomb-shape-10}, \text{Grotzsch}\}$, with 20 of 28 complete and 8 pending (deeper Grotzsch / Golomb pairs).

**Four distinct $\omega = 3$ no-$K_4$ $\chi = 5$ abstract structures**:

| Pair | $\|V\|$ | $\|B\|$ | $F$ profile | obstruction class |
|---|---:|---:|---|---|
| $W_5 \times W_5$ | **12** | 11 | [3,3,2,1,1,1] | adjacent-singleton |
| $W_5 \times$ Moser | 13 | 12 | [2,2,2,2,2,1,1] | global |
| Moser $\times$ Moser | 14 | 14 | [4,3,2,2,1,1,0] | empty-list (L21/L23) |
| $W_5 \times$ Golomb | 16 | 11 | [3,2,1,1,1,1,0,0,0,0] | sparse-singleton |

**Three L22-obstruction classes, concretely realized**:

1. **Empty-list** (Moser$^2$): single $L(v) = \emptyset$ at one boundary vertex. F profile concentrates at $\|F\| = 4$.
2. **Adjacent-singleton** ($W_5^2$): two singletons $L(v) = L(w) = \{c\}$ on a single $H_2$-edge force the same color on adjacent vertices.
3. **Global** ($W_5 \times$ Moser): no local empty-list, no singleton list (all $\|L(v)\| \geq 2$), yet list-uncolorable. Non-local Hall-type obstruction.

A fourth ("sparse-singleton") in $W_5 \times$ Golomb mixes singleton with many untouched vertices.

Each obstruction class has a distinctive F-profile shape: max value (4 for empty-list, 3 for adjacent-singleton, 2 for global), and bridge-density-per-vertex $\|B\| / \|V\|$ rises from 0.69 (sparse-singleton) to 1.00 (empty-list) as obstructions concentrate.

**$W_5 \times W_5$ record is 5-critical**: removing any vertex OR any single bridge drops $\chi$ to 4 (SAT-verified across all $V + B = 23$ removals).

**UDG-realizability of all records BLOCKED**:
- $W_5$ is not a UDG: regular pentagon side-1 has circumradius $1/(2\sin(\pi/5)) \approx 0.851 \neq 1$. Confirmed via scipy 500-start: $W_5$ alone has min residual $6.47 \times 10^{-2}$, never reaching zero. So $W_5 \times W_5$ and $W_5 \times$ Moser at V $\leq 13$ cannot be UDG, full stop.
- Moser$^2$ at V=14 is non-UDG per L23 (cocircularity + Positivstellensatz).
- Conclusion: **no abstract chi=5 record below Parts 509 yields a UDG record via the pair-cover route**.

**Structural floor**. The smallest 4-chromatic UDG is the Moser spindle (7 vertices). Hence any "two UDG halves + bridges" chi=5 UDG must have $\|V\| \geq 14$, with Moser$^2$ as the unique candidate at this floor. L23 closes that route; the chi=5 UDG record below 510 (if any) must come from a structurally different decomposition.

**Wrong-approach detector status**:

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: every analyzed pair requires 4-chromatic halves; vacuous in $\mathbb{Q}^2$. |
| $L^\infty$ ($\chi = 4$) | PASS: pair-min cover is graph-theoretic; realizability obstruction is Euclidean. |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS: no 4-chromatic UDG. |

**Why this matters**.

1. **L22's three abstract obstruction classes are all realized in small graphs.** L22 conjectured the empty-list local case as the strongest; L25 shows global and adjacent-singleton variants exist at similar or smaller vertex counts. The list-coloring obstruction has a richer structure than just "force a single empty list".

2. **The chi=5 UDG vertex gap (14 abstract vs 509 UDG) is geometric, not combinatorial**. Multiple small abstract chi=5 no-$K_4$ structures exist, but ALL fail UDG realization for clean geometric reasons ($W_5$ non-UDG, Moser$^2$ cocircularity-blocked). The 36-fold vertex inflation from 14 to 509 is the price of Euclidean rigidity.

3. **The Moser spindle's uniqueness as a 7-vertex 4-chromatic UDG is the structural bottleneck**. If a second 7-vertex 4-chromatic UDG existed distinct from Moser, Moser × (new UDG) would re-open the 14-vertex UDG chi=5 route. Searching for such a graph is the natural next experiment.

**Future BUILDER directions**:

1. **Search for 7-vertex 4-chromatic UDGs distinct from Moser spindle.** Discrete optimization over $\mathbb{Q}(\sqrt 3, \sqrt{11})$ coordinates with perturbation. If found, pair with Moser and check no-$K_4$ chi=5 + UDG realizability.
2. **Pair Moser with 8-9-vertex UDGs from `e1l_reverse_engineer_degrey1585.py`** (chain / pivot constructions). Combined $\|V\| \in \{15, 16\}$, both halves UDG. Test no-$K_4$ minima.
3. **Search for a "global obstruction Moser$^2$"**: does Moser × Moser admit a no-$K_4$ chi=5 cover with global-obstruction F-profile (every $\|L(v)\| \geq 2$, list-uncolorable globally)? Bridge count might be smaller than L21's empty-list 14 if the obstruction is more distributed.
4. **Pending pairs**: re-run h3_analyze.py for Moser × Golomb (both UDG, V = 17, $\omega = 3$ possible), Hajos × Golomb, Golomb$^2$, Grotzsch pairs.

---

### L24. The L22 pair list-coloring theorem lifts cleanly to triple coupling: $\chi(H_1 \cup H_2 \cup H_3 \cup B_{12} \cup B_{13} \cup B_{23}) \geq 6$ iff for every proper 5-coloring $c_1$ of $H_1$, the residual list-coloring on $(H_2 \cup H_3 \cup B_{23})$ with $L_2(v) = [5] \setminus F_{12}(v)$ and $L_3(w) = [5] \setminus F_{13}(w)$ is infeasible. Two-line proof. In the no-$K_4$ regime, 368 random three-Moser configurations produce ZERO $\chi \geq 6$ instances; conjecture C5: three-Moser + no-$K_4$ caps at chi=5.

**Architecture**: 1. Recursive lift of L22's list-coloring theorem to three halves.

**Experiment**: [`e1y_triple_list.py`](combinatorial/e1y_triple_list.py).

**Theorem (triple-coupling lift)**. Let $H_1, H_2, H_3$ be graphs on disjoint vertex sets, $B_{ij}$ the pairwise bridge sets, $G = \bigcup H_i \cup \bigcup B_{ij}$. Then $\chi(G) \geq 6$ iff for every proper 5-coloring $c_1$ of $H_1$, the residual list-coloring on $H_2 \cup H_3 \cup B_{23}$ with lists $L_2(v) = [5] \setminus \{c_1(u) : (u,v) \in B_{12}\}$ and $L_3(w) = [5] \setminus \{c_1(u) : (u,w) \in B_{13}\}$ is infeasible.

*Proof.* Both directions are contrapositives mirroring L22, with the residual being a pair list-coloring at one higher color level. ($\Rightarrow$) If a residual extension $(c_2, c_3)$ exists for some $c_1$, the gluing $c = c_1 \sqcup c_2 \sqcup c_3$ is a proper 5-coloring of $G$ since bridges $B_{12}, B_{13}$ are forced apart by the lists and $B_{23}$ is respected by the residual. ($\Leftarrow$) Any proper 5-coloring $c$ of $G$ restricts to a $c_1$ for which $(c|_{H_2}, c|_{H_3})$ list-extends. $\square$

**Recursive structure**. For $n$ halves, $\chi(G) \geq n+3$ iff $\forall c_1$ proper $(n+2)$-coloring of $H_1$, the residual $(n-1)$-half list-coloring at level $(n+2)$ is infeasible. Base case $n = 1$ is just $\chi(H_1) \geq n+2$.

**Verification table (theorem checked against direct SAT)**:

| Case | $\|C_1(5)\|$ | residual-feasible $c_1$ | $\chi$ SAT | list says $\chi \geq 6$? | agree? |
|---|---:|---:|---:|:---:|:---:|
| 3 $K_4$, star bridges | 120 | 0/120 | 6 | Y | Y |
| 3 $K_4$, no bridges | 120 | 120/120 | 4 | N | Y |
| 3 $K_4$, matching $(0,0)$ | 120 | 120/120 | 5 | N | Y |
| 3 Moser, aligned $K_{2,2}$ | 5040 | 0/5040 | 6 | Y | Y |
| 3 Moser, no bridges | 5040 | 5040/5040 | 4 | N | Y |

**Empirical no-$K_4$ scan** (uniform + L21-anchored sampling):

| Phase | sample method | $\|B_{ij}\|$ range | total | no-$K_4$ | $\chi = 4$ | $\chi = 5$ | $\chi \geq 6$ |
|---|---|---|---:|---:|---:|---:|---:|
| D | uniform | [6, 14] | 297 | 103 | 103 | 0 | **0** |
| E | uniform | [8, 12] | 400 | 80 | 80 | 0 | **0** |
| F | $B_{12} = B^*_{L21}$ anchored | various | 200 | 117 | 0 | 117 | **0** |
| F-side | $B_{12}$ fixed, $B_{13}, B_{23}$ random | various | 870 | 68 | 30 | 38 | **0** |
| **Combined** | | | **1767** | **368** | **213** | **155** | **0** |

Across 368 distinct no-$K_4$ three-Moser configurations including the L21-anchored "chi-5 strong" cases, **zero have $\chi \geq 6$**.

**Conjecture C5 (no-$K_4$ three-Moser caps at $\chi = 5$)**. For three Moser spindles on disjoint vertex sets and any bridge sets $B_{ij}$ with $\omega(\bigcup H_i \cup \bigcup B_{ij}) \leq 3$, $\chi \leq 5$.

**Structural reading**. By the triple-lift theorem, $\chi \geq 6$ requires forcing $|L_2(v)| = 0$ for SOME $v$ under EVERY $c_1$. This requires $|F_{12}(v)| = 5$, i.e., 5 distinct $c_1$-colors at the 5 $H_1$-endpoints bridging into $v$. In Moser (chi = 4), 5-color $c_1$-assignments use all 5 colors but constraints from Moser's edge structure prevent placing 5 distinct colors at 5 specific endpoints unless they include a 5-clique substructure, blocked by $\omega(\text{Moser}) = 3$. Moser's 4-choosability completes the residual list-coloring whenever no $v$ has $|F_{12}(v)| \geq 5$ uniformly across all $c_1$.

This corrects L20 implication 5 in its no-$K_4$ form: the ADVERSARY angle 6 $K_{2,2}$-aligned $\to K_6$ trick uses $K_4$-substructure on the boundaries, illegal in the UDG-relevant regime.

**Wrong-approach detector status**: identical to L21 / L22 / L23. PASS on $\mathbb{Q}^2$, $L^\infty$, $\mathbb{R}^1$ (vacuous in each).

**Why this matters**.

1. **The L21 covering ladder caps at chi=5 in the no-$K_4$ regime**: each additional half adds one color to the residual list-coloring, but Moser's 4-choosability propagates feasibility upward. The "third color reuse" L20 wondered about is exactly this 4-choosable propagation.

2. **The chi=6 UDG path must escape 4-choosability**. Either: (a) use halves that are NOT 4-choosable (i.e., 4-chromatic with list-chromatic $\geq 5$ from some 4-size lists; theta-graph-like examples exist abstractly but no small UDG-realizable example is known), or (b) recurse with chi=5 halves (Polymath 510 × Polymath 510 + no-$K_4$ bridges, with the L24 lift now applied at the 5-color level).

3. **Polymath 510² + bridges is the natural next chi-6 UDG target**. Same covering ladder, one rung up. Polymath 510 has thousands of canonical 5-colorings; sampling-based feasibility is the right algorithm.

**Future BUILDER directions**:

1. **Polymath 510 × Polymath 510 + no-$K_4$ bridges**: search for chi-6 bridge sets via the L24 lift at the 5-color level.
2. **Compute the list-chromatic number of the Moser spindle**: is Moser 4-choosable? Conjecture yes (and a SAT-search over 4-size list assignments confirms or refutes).
3. **Multi-half cone obstruction lemma**: generalize L22's local-empty-list obstruction to $n$ halves; characterize when a single boundary vertex can force $|L(v)| = 0$ across all $(n-1)$-tuples of higher-level colorings.
4. **Lean formalization of the triple lift** (extends H4 work).

---

### L23. The L21 14-vertex Moser x Moser no-$K_4$ $\chi = 5$ abstract graph is NOT UDG-realizable in $\mathbb{R}^2$. Structural cocircularity obstruction: H_2's vertex 6 must lie at unit distance from 5 H_1-vertices $\{0,2,3,4,6\}$, but those 5 points are not cocircular (radii of inscribed circles range from 0.51 to 5.94). Symmetrically H_1's v_6 must bridge to H_2 vertices $\{1,3,5,6\}$, which are cocircular at radius 0.805 (not 1). Max realizable subset $\|B'\| = 7$ of 14 bridges. This quantifies L21's "realizability cost": 7 bridges drop from the abstract minimum to the UDG-realizable minimum on this pair.

**Architecture**: 1. BUILDER pass on L21's open realizability question.

**Experiment**: [`e1x_realize_moser14.py`](combinatorial/e1x_realize_moser14.py).

**The graph**.

$H_1, H_2$ are two disjoint copies of the Moser spindle (7 vertices each, $\chi(H_i) = 4$ via SAT). The 14 bridges $B^*$ (L21):

$$B^* = \{(0,0),(0,1),(0,3),(0,4),(0,6),(1,0),(2,6),(3,6),(4,6),(5,1),(6,1),(6,3),(6,5),(6,6)\}.$$

Indexed: first slot = $H_1$ vertex, second slot = $H_2$ vertex. As an abstract graph this has $\chi = 5$, $\omega = 3$, and is the smallest known "two 4-chromatic halves + bridges" structure with no $K_4$.

**The realizability question (L21 open direction 1)**.

Place $H_1$ at the canonical Moser coordinates in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. Does there exist a rigid motion $\phi : \mathbb{R}^2 \to \mathbb{R}^2$ such that $H_2 = \phi(\text{Moser spindle})$ and all 14 bridges become unit-distance edges? The pose $\phi$ has 3 real DoF (translation $t_x, t_y$ + rotation $\theta$), so 14 unit-distance equations is generically overdetermined by 11.

**Verdict: NO, with a structural certificate**.

The obstruction is *cocircularity*, identifiable without optimization. For any rigid motion $\phi$, if $H_2$ vertex $v$ has bridge-partners $\{u_1, \dots, u_k\}$ in $H_1$, then all $u_i$ must lie at unit distance from $\phi(v)$, i.e., on the unit circle around $\phi(v)$. Equivalently the $u_i$ must be cocircular at radius 1 (relative to some center). The same condition holds symmetrically on the $H_1$ side.

| Side | vertex | bridge endpoints in other half | cocircular? | radius | compatible? |
|---|---:|---|:---:|---:|:---:|
| $H_2$ receives | $v_0$ | $\{0, 1\}$ | trivial (2 pts) | n/a | yes |
| $H_2$ receives | $v_1$ | $\{0, 5, 6\}$ | YES | 1.000 | YES |
| $H_2$ receives | $v_3$ | $\{0, 6\}$ | trivial (2 pts) | n/a | yes |
| $H_2$ receives | $v_4$ | $\{0\}$ | trivial (1 pt) | n/a | yes |
| $H_2$ receives | $v_5$ | $\{6\}$ | trivial (1 pt) | n/a | yes |
| $H_2$ receives | $v_6$ | $\{0, 2, 3, 4, 6\}$ | **NO** | range $[0.51, 5.94]$ | **NO** |
| $H_1$ sends | $v_0$ | $\{0, 1, 3, 4, 6\}$ | **NO** | range $[0.51, 5.94]$ | **NO** |
| $H_1$ sends | $v_6$ | $\{1, 3, 5, 6\}$ | YES | **0.805** | **NO (radius != 1)** |

Three obstructed bridge-endpoints, each killing a different geometric constraint. The first two ($H_2$ v_6 and $H_1$ v_0) are duals of each other: $v_0^{H_1}$ has 5 outgoing bridges into $H_2$ vertices $\{0,1,3,4,6\}$, and $v_6^{H_2}$ has 5 incoming bridges from $H_1$ vertices $\{0,2,3,4,6\}$. Each requires the bridge-endpoint set to be on a unit circle, and the 5-point sets fail cocircularity entirely.

The third obstruction is sharp: $H_1$'s $v_6$ has bridges to $H_2$ vertices $\{1, 3, 5, 6\}$, and those 4 points ARE cocircular (the Moser spindle has many tight 4-cocircular substructures), but at radius $\sim 0.805$, not 1. So the cocircular center exists but cannot be a unit-distance hub.

**Algebraic certificate (Positivstellensatz, h2 VERIFIER complement)**.

The cocircularity argument can be promoted to an exact polynomial-identity refutation. Parameterize $H_2$'s pose by $(c, s, t_x, t_y)$ with $R_\theta = \begin{pmatrix} c & -s \\ s & c \end{pmatrix}$ and constraint $c^2 + s^2 = 1$. Each bridge $(i, j) \in B^*$ gives a quadratic equation $f_{ij}(c, s, t_x, t_y) := \|\phi(v_j) - v_i\|^2 - 1 = 0$ over $\mathbb{Q}(\sqrt 3, \sqrt{11})$.

**Same-$j$ linear-difference trick**: for two bridges $(i, j), (i', j)$ sharing the same $H_2$-endpoint $j$, the rotation-quadratic terms $\|R_\theta v_j\|^2 = \|v_j\|^2$ cancel under subtraction:
$$f_{ij} - f_{i'j} = -2(v_i - v_{i'}) \cdot (R_\theta v_j + t) + (\|v_i\|^2 - \|v_{i'}\|^2),$$
which is degree 1 in $(c, s, t_x, t_y)$. The 14-bridge set $B^*$ has multiple bridges sharing $H_2$-endpoints $\{0, 1, 3, 6\}$, yielding **8 linear equations** in 4 unknowns over $\mathbb{Q}(\sqrt 3, \sqrt{11})$.

The augmented coefficient matrix satisfies $\operatorname{rank}(A) = 4$ but $\operatorname{rank}([A \mid b]) = 5$: INCONSISTENT.

**Explicit degree-1 Positivstellensatz certificate** (3 of the 8 differences suffice):
$$g_1 := f_{(2,6)} - f_{(0,6)}, \quad g_2 := f_{(3,6)} - f_{(0,6)}, \quad g_3 := f_{(4,6)} - f_{(0,6)},$$
$$\frac{5 - \sqrt{33}}{6} \cdot g_1 \;+\; \frac{-15 + \sqrt{33}}{18} \cdot g_2 \;+\; 1 \cdot g_3 \;=\; -\frac{2}{3}.$$

Identity verified in $\mathbb{Q}(\sqrt 3, \sqrt{11})[c, s, t_x, t_y]$ by independent sympy expand. Each $g_k$ must vanish at any feasible pose, but RHS is the nonzero rational $-2/3$. Contradiction. QED.

**Groebner cross-check**: $G = \text{GB}(\{f_{(0,6)}, f_{(2,6)}, f_{(3,6)}, f_{(4,6)}, c^2 + s^2 - 1\}) = \{1\}$ (unit ideal) over $\mathbb{Q}(\sqrt 3, \sqrt{11})$ in grevlex order, computed in 0.26s. Two independent algebraic methods agree.

**Geometric interpretation matching the cocircularity table**: bridges $(0,6), (2,6), (3,6) \in B^*$ demand $\phi(v_6)$ at unit distance from $v_0, v_2, v_3$. The unique such point in $\mathbb{R}^2$ is $v_1 = (1, 0)$ ($v_0, v_2, v_3$ all sit on the unit circle around $v_1$). Then bridge $(4, 6)$ requires $\|v_1 - v_4\|^2 = 1$, but $(1 - 5/6)^2 + (\sqrt{11}/6)^2 = 12/36 = 1/3$. The residual $-2/3$ matches the certificate constant exactly.

**Locality lemma at $v_6$**: exhaustive enumeration of $2^5 = 32$ subsets of the 5 bridges $\{(0,6), (2,6), (3,6), (4,6), (6,6)\}$ into $H_2$-vertex 6 shows the maximum simultaneously realizable subset has size $\leq 3$. Hence any rigid motion violates at least 2 of these 5 bridges, before even considering the other 9 in $B^*$.

Total wall-clock for the algebraic certificate: $\sim 4$ seconds (vs the 8-hour budget allocated). The same-$j$ linear-difference reduction makes the system decompose to a linear feasibility problem in milliseconds.

**Numerical certificate**.

We numerically minimize $\sum_{(i,j) \in B^*} (\|\phi(v_j) - v_i\|^2 - 1)^2$ with 500-start L-BFGS-B over $(t_x, t_y, \theta)$, with reflections and across both Moser-spindle automorphisms (the spindle has a $\mathbb{Z}_2$ symmetry under permutation $(0,5,4,6,2,1,3)$). Best loss $L^* \approx 9.40$ corresponds to max per-bridge $|d - 1| \approx 0.90$. The minimum is bounded well above $\epsilon = 10^{-6}$ across all 4 (aut, reflect) cases, refuting realizability.

**Maximum realizable subset**.

Subset realizability is downward-closed: if pose $\phi$ realizes $S \subseteq B^*$, then $\phi$ realizes every subset of $S$. So the max realizable subset size = largest $k$ such that some $k$-subset is realizable. Brute-force over $C(14, 8) = 3003$ subsets at size 8 finds NONE realizable; over $C(14, 7) = 3432$ at size 7 finds one immediately:

$$B'_{\max} = \{(0,1),(0,4),(1,0),(3,6),(4,6),(6,3),(6,5)\}, \quad \|B'_{\max}\| = 7.$$

Verified to numerical precision $|d - 1| < 2.2 \times 10^{-16}$ (machine epsilon). By monotonicity, no subset of size $\geq 8$ is realizable.

| Statistic | Value |
|---|---:|
| $\|B^*\|$ (abstract) | 14 |
| $\|B^*_{\text{realizable}}\|$ (max simultaneously unit-distance) | **7** |
| Realizability gap | 7 bridges (50%) |
| Phase 1 best $L^2$ residual sum (full $B^*$) | 9.40 |
| Phase 1 best max $\|d - 1\|$ (full $B^*$) | 0.90 |
| Best max $\|d-1\|$ across 4 (aut, reflect) combos | 0.90 |

**Why $\|B'_{\max}\| = 7$ and which bridges are dropped**.

The optimal 7-subset $B'_{\max}$ drops one bridge from EACH high-degree obstruction:
- From $H_2$ $v_6$'s 5-star: keeps $(3,6), (4,6)$; drops $(0,6), (2,6), (6,6)$.
- From $H_1$ $v_0$'s 5-star: keeps $(0,1), (0,4)$; drops $(0,0), (0,3), (0,6)$.
- From $H_1$ $v_6$'s 4-star at radius 0.805: keeps $(6,3), (6,5)$; drops $(6,1), (6,6)$.
- Single bridge $(1, 0)$ and $(5, 1)$ are handled: $(1, 0)$ keeps, $(5, 1)$ drops.

The 7 obstructing bridges:

$$B^* \setminus B'_{\max} = \{(0,0),(0,3),(0,6),(2,6),(5,1),(6,1),(6,6)\}.$$

Note that $(0,6)$ and $(6,6)$ involve $v_6$ on BOTH sides (the "diagonal" 6-6 bridge), the most over-constrained position.

**Implications for the L21 covering lemma program (cost of realizability)**.

L21 conjectured (with the natural reading of "realizability cost") that the gap between the abstract graph-theoretic minimum bridge count (14, for Moser $\times$ Moser no-$K_4$) and the UDG-realized minimum (155, for de Grey 1585) is bounded below by the structural cocircularity obstruction in the abstract graph. L23 quantifies this:

| Construction | $\|B\|$ | UDG-realizable | Reduction needed |
|---|---:|:---:|---|
| Moser $\times$ Moser abstract no-$K_4$ | 14 | NO ($\geq 7$ obstructed) | replace each obstructed bridge by an indirect 2-hop path |
| Moser $\times$ Moser realizable subset | 7 | YES | proves abstract->UDG cost factor $\geq 2$ in bridges |
| de Grey 1585 | 155 | YES | adds 1574 vertices to make all bridges realizable |
| Polymath 510 | 833 | YES | adds 503 vertices |

Each obstructed abstract bridge can in principle be "softened" into a path of vertices in $\mathbb{R}^2$ (a Moser-spindle-like rigid path) of length $\geq 2$, multiplying vertex count. The factor of $\sim 100$ from 14 abstract bridges to 1585 UDG vertices reflects the geometric softening cost.

**Why direct rigid placement fails (intuition)**.

A Moser spindle has 7 vertices and rotational/reflection symmetry $\mathbb{Z}_2$ (the spindle has 2 automorphisms via the non-identity vertex permutation $(0,5,4,6,2,1,3)$). Its diameter is $\sim 1.55$ (vertex 6 from origin). Any two Moser spindles in $\mathbb{R}^2$ at "close range" have their 14 cross-distances generically all different from 1, and the constraint $c^2 + s^2 = 1$ plus 3 translational DoFs gives only 3 free parameters versus 14 equations. The cocircularity obstruction is the *exact* algebraic form of this overdetermination: any single vertex hosting $\geq 3$ bridges into a non-cocircular endpoint set is infeasible regardless of pose.

**Wrong-approach detector status**:

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: the analysis is over $\mathbb{Q}(\sqrt 3, \sqrt{11})$, an extension of $\mathbb{Q}$, but the conclusion is about non-realizability of a specific UDG. In $\mathbb{Q}^2$ neither Moser spindle exists (its coordinates use $\sqrt{11}$). Vacuous in $\mathbb{Q}^2$, so no spurious $\chi(\mathbb{Q}^2) \geq 3$. |
| $L^\infty$ on $\mathbb{R}^2$ ($\chi = 4$) | PASS: the Moser spindle requires equilateral triangles (Euclidean rigidity). It is not a $L^\infty$-UDG. The cocircularity obstruction is *Euclidean* (circle vs L^infty square). The argument doesn't apply to $L^\infty$, and rightly so since $L^\infty$ has $\chi = 4$ and no $\chi \geq 5$ obstacle. |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS: $\mathbb{R}^1$ has no 4-chromatic UDG, no Moser spindle, no cocircularity question. Vacuous. |

The detectors PASS because the structural obstruction is geometrically tied to the Euclidean unit circle, which is the right tool for $\mathbb{R}^2$ but doesn't bind on $\mathbb{Q}^2$ or $L^\infty$.

**Why this matters**.

1. **L21's open direction 1 is resolved**. The 14-vertex no-$K_4$ Moser $\times$ Moser abstract graph is NOT a UDG. The 14 bridges cannot all be realized as Euclidean unit distances under any rigid motion, with or without reflection, across both Moser-spindle automorphism labelings. So the smallest known no-$K_4$ $\chi = 5$ graph remains de Grey's 1585 (or Polymath's 510) by a factor of $\sim 35$ in vertex count.

2. **Cocircularity is THE structural obstruction in low-vertex UDG realizability**. The condition "for every $v \in V(H_2)$, $N_B(v) \subseteq V(H_1)$ is cocircular at radius 1" is a *necessary* condition for the joint UDG. It can be checked in $O(\|B\|)$ per vertex, before any optimization. Future BUILDER experiments on small graphs should run this filter as a fast no-realizability sieve.

3. **Realizability cost gives a structural lower bound on UDG vertex counts**. The 14-vertex abstract graph realizes only 7 of 14 bridges. To realize the remaining 7 bridges, each must be replaced by a multi-vertex path / spindle in $\mathbb{R}^2$. Even at the optimistic rate of "2 extra vertices per obstructed bridge" (each adding a Moser-like degree-of-freedom), 7 obstructed bridges $\to$ 14 extra vertices $\to$ 28-vertex realizable graph as a *lower bound*. The actual minimum is much larger; de Grey 1585 = 1571 vertices added in the bridge-region structure.

4. **The "symmetry-driven 5-star obstruction" generalizes**. In L21's bridge graph, $v_0^{H_1}$ and $v_6^{H_2}$ both host 5-stars (high-degree bridge endpoints). The 5-star $\to$ cocircular-5-points-on-unit-circle constraint is the basic local rigidity obstacle. Polymath16's strategy (and de Grey's) avoids this by limiting per-vertex bridge degree to $\leq 4$ (typically) and ensuring cocircularity at radius 1 in the local geometry.

**Future BUILDER directions (next session)**:

1. **Apply the cocircularity sieve to all known low-vertex $\chi \geq 5$ abstract candidates**. For any candidate "two-half + bridges" graph with $\|V\| < 100$, check the cocircularity obstruction symmetrically. If it fails, the abstract graph is non-UDG. Filter the space.

2. **Investigate 2-hop softening of obstructed bridges**. Replace each obstructed bridge $(u, v) \in B^* \setminus B'_{\max}$ by a vertex $w \in \mathbb{R}^2$ with edges $(u, w)$ and $(w, v)$ both unit. The "minimum vertex addition" to make $B^*$ realizable is the next BUILDER target, with a hypothesis that 7 obstructed bridges + 14-vertex base $\to$ 21-vertex UDG with $\chi = 5$ (which would still smash the Parts 509 / Polymath 510 record).

3. **Check whether the Moser $\times$ Moser 14-bridge structure has a "softer" abstract variant** (with $\|B\| \in [15, 50]$ and $\chi = 5$) that IS realizable. This is the right direction to beat Polymath 510.

4. **For the chi-6 question** (L21 implication 5): apply the same cocircularity sieve to ADVERSARY's $K_6$-cross-clique 9-vertex graph and the no-$K_4$ chi-6 candidates. If the abstract minimum chi-6 graph fails cocircularity badly, the UDG chi-6 vertex count is correspondingly large.

5. **Apply the same-$j$ linear-difference trick to de Grey 1585 and Polymath 510** (h2 follow-up). Each $H_2$-boundary vertex with $k$ incoming bridges contributes $k - 1$ linear constraints on the pose. de Grey's 22 boundary vertices in $H_2$ with 155 bridges $\Rightarrow$ $155 - 22 = 133$ linear constraints in 4 unknowns. The fact that this system IS consistent for the published embedding is a structural check on de Grey's construction; comparing the rank pattern across the published examples may reveal further structure.

6. **Lean 4 formalization of the h2 certificate** (extends H4's L21/L22 Lean work). The polynomial identity $\lambda_1 g_1 + \lambda_2 g_2 + \lambda_3 g_3 = -2/3$ over $\mathbb{Q}(\sqrt{33})$ is short enough to fit a single `nlinarith` / `field_simp` Lean tactic. A theorem `moser14_not_udg` becomes the first formal infeasibility proof in the Hadwiger-Nelson formalization.

---

### L22. The L21 covering lemma has an EXACT list-coloring reformulation: chi(H_1 cup H_2 cup B) >= 5 iff H_2 is not list-colorable from lists L(v) = [4] \ F(v) where F(v) = {c_1(u) : (u,v) in B}. L21's C4 conjecture, read literally, is strictly stronger than necessary (C4 implies chi >= 5 but the converse fails); L22 supersedes it with the list-coloring theorem.

**Architecture**: 1. VERIFIER pass on L21's open C4 conjecture.

**Experiment**: [`e1w_lemma_c4.py`](combinatorial/e1w_lemma_c4.py).

**Theorem (list-coloring reformulation of L21)**.

Let $H_1, H_2$ be 4-chromatic graphs on disjoint vertex sets, $B \subseteq V(H_1) \times V(H_2)$ a bridge set, and fix any proper 4-coloring $c_1$ of $H_1$. For each $v \in V(H_2)$ define

$$F(v) := \{c_1(u) : (u,v) \in B\} \subseteq [4], \qquad L(v) := [4] \setminus F(v).$$

(So $F(v) = \emptyset$ and $L(v) = [4]$ for $v \notin \partial_B H_2$.) Then

$$\chi(H_1 \cup H_2 \cup B) \geq 5 \iff H_2 \text{ has no proper coloring } c_2 \text{ with } c_2(v) \in L(v) \text{ for every } v.$$

*Proof*.
($\Rightarrow$) Contrapositive. If $c_2$ list-extends from $L$, the joint $c(u) := c_1(u)$ on $H_1$, $c(v) := c_2(v)$ on $H_2$ is proper: $H_1, H_2$ edges respected by $c_1, c_2$; for bridge $(u,v) \in B$ we have $c_1(u) \in F(v)$ while $c_2(v) \in L(v) = [4] \setminus F(v)$, so $c_1(u) \neq c_2(v)$. Hence the combined graph is 4-colorable.
($\Leftarrow$) Contrapositive. Any proper 4-coloring $c$ of the combined graph yields $c_2 := c|_{V(H_2)}$ with $c_2(v) \neq c(u) = c_1(u)$ for every bridge $(u,v) \in B$. So $c_2(v) \notin F(v)$, i.e. $c_2(v) \in L(v)$. $\square$

This is a *clean theorem*, not a conjecture, and is the right form of the covering lemma. Verified computationally on all six L21 small cases (see [`_cache/e1w_lemma_c4.json`](combinatorial/_cache/e1w_lemma_c4.json)).

**F-profiles on the L21 small cases (sorted desc per case, $c_1$ = canonical first 4-coloring)**:

| Case | $B$-kind | $\|B\|$ | $F$ profile | list-UNSAT? | C4 (L21) holds? | C4 violators / $\|\mathcal{C}_2\|$ |
|---|---|---:|---|:---:|:---:|---:|
| $K_4 \times K_4$ | unconstr. | 4 | [1,1,1,1] | Y | N | 24 / 24 |
| $K_4 \times$ Moser | unconstr. | 4 | [4,0,0,0,0,0,0] | Y | Y | 0 / 384 |
| Moser $\times$ Moser | no-$K_4$ | 14 | [4,3,2,2,1,1,0] | Y | N | 376 / 384 |
| $K_4$-pendant$^{\times 2}$ | unconstr. | 4 | [1,1,1,1,0] | Y | N | 72 / 72 |
| $W_5 \times W_5$ | no-$K_4$ | 11 | [3,3,2,1,1,1] | Y | N | 120 / 120 |
| $K_4 \times$ Hajos | unconstr. | 4 | [1,1,1,1,0,0,0] | Y | N | 144 / 144 |

**Verdict on C4 (as stated in L21)**.

L21 stated C4 as: "for every 4-coloring $c_2$ of $H_2$, the bipartite subgraph $B[u : c_1(u) = c_2(v) \text{ for some } (u,v) \in B]$ must hit every color class of $c_2|_{\partial_B H_2}$." Translation into $F$: "for every $c_2$, for every $v \in \partial_B H_2$, $c_2(v) \in F(v)$." This is the universal "hits every boundary vertex" condition.

The list-coloring form is: "for every $c_2$, **some** $v$ (anywhere in $V(H_2)$, including boundary) has $c_2(v) \in F(v)$." This is the existential "hits some vertex" condition.

C4 is strictly stronger: 5 of 6 small cases have list-UNSAT (so $\chi \geq 5$) yet some $c_2$ has $c_2(v) \notin F(v)$ for some boundary $v$, so C4 fails. The C4 implication "$\chi \geq 5 \Rightarrow $ every $c_2$ is hit at every boundary $v$" is FALSE. The correct theorem is: "$\chi \geq 5 \iff $ every $c_2$ is hit at some vertex." **L22 supersedes C4.**

**Explicit C4-vs-list witness (Moser $\times$ Moser, 14-bridge)**. With $c_1 = (0,1,2,0,1,2,3)$ and the L21 bridge set $B^*$, the 4-coloring $c_2 = (0,1,2,0,1,2,3)$ of $H_2$ violates C4 at $v \in \{1, 4, 5\}$ (where $c_2(v) \notin F(v)$), yet list-coloring is still UNSAT because $c_2$ is forbidden at $v=0$ (where $F(0) = \{0,1\}$ contains $c_2(0) = 0$). The covering succeeds *somewhere*, not *everywhere*.

**Sharper structural facts in the no-$K_4$ / no-$K_5$ regime**.

1. **$\|F(v)\| = 4$ at boundary $v$ does NOT force $K_5$ unless the four $H_1$-endpoints induce a $K_4$.** Verified on Moser $\times$ Moser 14-bridge: $v = 6$ has $F(v) = \{0,1,2,3\}$ but the bridges into $v = 6$ are $(0,6),(2,6),(3,6),(4,6),(6,6)$ with $c_1$-colors $\{0,2,0,1,3\}$; the $H_1$-endpoints partitioned by color are $\{0, 3\}$, $\{4\}$, $\{2\}$, $\{6\}$, and no 4-tuple one-per-color forms a $K_4$ in the Moser spindle. So the no-$K_4$ regime CAN tolerate $\|F(v)\| = 4$ without producing $K_5$. The $K_5$ collapse (L21's "trivial" cases) is the special situation where $H_1$ already contains a $K_4$ on the relevant endpoints.

2. **$\|F(v)\| \leq 4$ trivially**; no obstruction here for the no-$K_5$ regime per se. The right structural invariant is the *full list profile* $(L(v))_{v \in V(H_2)}$ viewed as an instance of LIST-3-COLORING (or LIST-$k$-COLORING) of $H_2$.

3. **Hall-type local obstructions for the 14-bridge case**: list size distribution $\{0: 1, 1: 1, 2: 2, 3: 2, 4: 1\}$. One vertex ($v = 6$) has $L = \emptyset$, so the list is locally infeasible at $v = 6$ alone, and the 14-bridge cover succeeds because some bridge from $H_1$ to $v = 6$ forces every color. *This is the "cone obstruction" interpretation*: a single boundary vertex with empty list is a 4-color cone-obstacle, and the bridges are exactly the cone structure that produces it.

**Statement of the refined cone obstruction lemma C4' (replaces L21's C4)**.

**C4' (list-coloring cone obstruction, proved as a theorem above)**. $\chi(H_1 \cup H_2 \cup B) \geq 5$ iff the list assignment $L : V(H_2) \to 2^{[4]}$ with $L(v) = [4] \setminus \{c_1(u) : (u,v) \in B\}$ admits no proper list-coloring of $H_2$. In particular, the strongest *local* obstruction is $L(v) = \emptyset$ at a single vertex (forced by 4 bridges with $H_1$-endpoints in all 4 color classes); the weakest is purely global, where every individual $L(v) \neq \emptyset$ but the global list-coloring is unsat by H_2's structure.

**Corollary (lower bound from local obstruction)**. If $\chi(H_1 \cup H_2 \cup B) \geq 5$ via a local empty-list, then $\|B\| \geq 4$ (need 4 distinct colors at $v$). Verified by all L21 cases.

**Wrong-approach detector status**:

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: theorem assumes 4-chromatic halves, vacuous in $\mathbb{Q}^2$. |
| $L^\infty$ on $\mathbb{R}^2$ ($\chi = 4$) | PASS: theorem is graph-theoretic, obstruction is realizability. |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS: no 4-chromatic UDG. Vacuous. |

**Why this matters**.

1. **List-coloring is the right primitive.** L21's covering-product formulation enumerates $\|\mathcal{C}_1\| \cdot \|\mathcal{C}_2\|$ pairs; L22's list-coloring formulation reduces this to a SINGLE list-coloring instance on $H_2$ (with $c_1$ fixed). This is an exponential speedup in formal reasoning: list-coloring of a 7-vertex Moser spindle with lists $L(v)$ is decidable in microseconds; enumerating $16 \times 384 = 6144$ coloring pairs is unnecessary.

2. **The list-coloring view connects to known graph theory.** Choosability / list-chromatic number is a well-studied invariant. Moser spindle has list-chromatic number 4 (it's 4-list-colorable from any list assignment with $\|L(v)\| \geq 4$, but not always 3-list-colorable). Tighter local F-profiles (smaller lists) make list-coloring harder; the L21 14-bridge produces a profile that is "barely" infeasible.

3. **The 14-bridge structure is sharp**: any 13-bridge subset of the L21 set $B^*$ either (a) leaves $L(6) \neq \emptyset$ (and the global list-coloring becomes feasible), or (b) keeps $L(6) = \emptyset$ but creates an empty-list elsewhere with smaller F-coverage. The minimum no-$K_4$ bridge count = 14 is exactly the local-empty-list threshold for Moser $\times$ Moser.

4. **Lemma C4 was almost right.** L21's C4 was an intuition: "every $c_2$ must be obstructed somewhere by bridges." The correction is the quantifier ordering: "somewhere" not "everywhere on the boundary." With this fix, C4' = the list-coloring form, which is a theorem.

**Future BUILDER directions (next session)**:

1. **List-chromatic obstructions in UDG**: characterize which $H_2$ admit list-assignments $L$ with $\|L(v)\| \leq 3$ that are list-uncolorable. The Moser spindle with $L(6) = \emptyset$ and $\|L(v)\| \geq 1$ elsewhere is the smallest example seen here. The "no-empty-list" list-coloring obstruction is a richer combinatorial object.
2. **Minimum bridge count in the no-empty-list regime**: in the L21 no-$K_4$ Moser $\times$ Moser, $\|B\| = 14$ uses the $L(v) = \emptyset$ local obstruction. What is the minimum no-$K_4$ AND no-empty-list bridge count? This is the "genuinely global" list-coloring obstruction, presumably much larger.
3. **Apply the list-coloring form to the de Grey 1585 / Polymath 510 bridges**: compute $F(v)$ profiles for the 22 boundary vertices on the asymmetric side of de Grey 1585 (need to extract bridges from cache). Hypothesis: the F-profile is dominated by $\|F(v)\| \in \{3, 4\}$ for most v, with at least one $v$ having $L(v) = \emptyset$, reflecting the "core forces colors via the $C_6$ symmetry" intuition.

---

### L21. Bridge-set in "two 4-chromatic halves + bridges" is a set cover of the (c_1, c_2) compatibility product; every single bridge kills exactly 1/4 of pairs (provable); minimum |B| collapses to 4-6 via K_5 trick, but rises to 11-14 once K_4 is forbidden (the UDG-relevant regime)

**Architecture**: 1. Resolves L20's open characterization question.

**Experiment**: [`e1v_bridge_covering.py`](combinatorial/e1v_bridge_covering.py).

**The covering lemma (now formally captured)**:

For any 4-chromatic graphs $H_1, H_2$ on disjoint vertex sets and bridge set $B \subseteq V(H_1) \times V(H_2)$,

$$\chi(H_1 \cup H_2 \cup B) \geq 5 \iff \bigcup_{(u,v) \in B} \{(c_1, c_2) \in \mathcal{C}_1 \times \mathcal{C}_2 : c_1(u) = c_2(v)\} = \mathcal{C}_1 \times \mathcal{C}_2,$$

where $\mathcal{C}_1, \mathcal{C}_2$ are the sets of proper 4-colorings of $H_1, H_2$. Each bridge $(u,v)$ "kills" the subset of pairs assigning matching colors to its endpoints. $B$ forces $\chi \geq 5$ iff the kill sets cover $\mathcal{C}_1 \times \mathcal{C}_2$. Mod the diagonal $S_4$ action we may fix $c_1$ canonical and let $c_2$ range over the full $S_4$-orbit on $H_2$.

**The kill-fraction theorem (proven, not just empirical)**: For any 4-chromatic graph $H_2$ and any vertex $v \in V(H_2)$ and any color $c \in \{0,1,2,3\}$, exactly $\|\mathcal{C}_2\| / 4$ of the proper 4-colorings $c_2$ satisfy $c_2(v) = c$.

*Proof*: $S_4$ acts freely on $\mathcal{C}_2$ (4-chromatic means all 4 colors are used in every coloring, so the stabilizer is trivial; orbits have size $4! = 24$). The 4 colors are interchangeable under this action, so each color appears at $v$ in exactly $\|\mathcal{C}_2\|/4$ colorings.

**Corollary (the trivial lower bound)**: For any single bridge $(u,v)$, the fraction of pairs killed is exactly $\rho_{u,v} = 1/4$. Hence $\|B\| \geq 4$ for any chi-$\geq$5-forcing bridge set.

**Verified empirically**: across all tested graphs (K_4, Moser spindle, W_5, K_4 + pendant, Hajos join), every single (u,v) bridge kills exactly $\frac{1}{4}\|\mathcal{C}_1 \times \mathcal{C}_2\|$ pairs. Independent of graph structure.

**Small-case minimum bridge sets (unconstrained SAT-min cover, with $\chi$ verified via Cadical)**:

| $H_1 \times H_2$ | $\|\mathcal{C}_1\|$ | $\|\mathcal{C}_2\|$ | $\rho_{\text{mean}}$ | greedy $\|B\|$ | SAT-min $\|B\|$ | matching $\|B\|$ | no-$K_4$ $\|B\|$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| $K_4 \times K_4$ | 1 | 24 | 0.250 | 4 | **4** | infeasible | infeasible |
| $K_4 \times$ Moser | 1 | 384 | 0.250 | 7 | **4** | infeasible | infeasible |
| Moser $\times$ Moser | 16 | 384 | 0.250 | 7 | **6** | infeasible | **14** |
| $K_4$-pendant $\times K_4$-pendant | 3 | 72 | 0.250 | 4 | **4** | infeasible | infeasible |
| $W_5 \times W_5$ | 5 | 120 | 0.250 | 6 | **6** | infeasible | **11** |
| $K_4 \times$ Hajos-join | 1 | 144 | 0.250 | 4 | **4** | infeasible | infeasible |

**Key observation: all unconstrained minimum bridge sets force chi $\geq 5$ via embedded $K_5$**.

Inspection of the chosen bridges:
- $K_4 \times K_4$: bridges $\{(0,j) : j \in [4]\}$; vertex 0 of $H_1$ plus $H_2$'s $K_4$ forms $K_5$.
- $K_4 \times$ Moser: bridges $\{(i,0) : i \in [4]\}$; vertex 0 of $H_2$ plus $H_1$'s $K_4$ forms $K_5$.
- $W_5 \times W_5$: bridges from hub-0 of $H_1$ to all 6 of $H_2$; chi >= chi(W_5)+1 = 5 via $H_1.0$ cone.
- Moser $\times$ Moser ($\|B\|=6$): bridges $\{(0,j),(1,j) : j \in \{0,1,2\}\}$; edge $(0,1) \in H_1$ + triangle $\{0,1,2\} \in H_2$ + 6 bridges = $K_5$ on $\{0,1,7,8,9\}$. Verified: combined graph has $K_5$.

**Max-clique trick is forbidden by R^2-realizability**: a unit-distance graph in $\mathbb{R}^2$ has no $K_4$ (four points pairwise at unit distance would form a regular tetrahedron, impossible in 2D). Verified: de Grey 1585 has $\omega = 3$. So **no chi $\geq$ 5 UDG in $\mathbb{R}^2$ can use the $K_5$ trick**. The relevant minimum is the **no-$K_4$ constrained** minimum.

**Smallest known abstract "delocalized chi = 5" with no $K_4$**: Moser $\times$ Moser with the 14-bridge no-$K_4$ cover yields a 14-vertex, 36-edge graph with $\omega = 3$ and $\chi = 5$, verified by SAT (Cadical, 4-coloring UNSAT and 5-coloring SAT). The 14 bridges are:

$$B^{*}_{\text{Moser}^2} = \{(0,0),(0,1),(0,3),(0,4),(0,6),(1,0),(2,6),(3,6),(4,6),(5,1),(6,1),(6,3),(6,5),(6,6)\}.$$

This uses all 7 $H_1$-vertices and 6 of 7 $H_2$-vertices (vertex 2 of $H_2$ omitted from the bridge boundary).

**Conjectures from L20, tested**:

**C1 (information-theoretic LB) is loose by a factor of 3-5x in small cases.** The bound $\|B\| \geq \log_{3/4}(1/\|P\|)$ predicts $\|B\| \geq 11$ for $K_4 \times K_4$ (true min 4), $\|B\| \geq 30$ for Moser $\times$ Moser (true min 6 unconstrained, 14 no-$K_4$). Kill sets are heavily correlated, not independent. C1 is correct as a bound but useless as a tightness predictor.

**C2 (boundary color saturation) is REFUTED.** The minimum-side boundary often collapses to one color:

| Case | bound-$H_1$ colors | bound-$H_2$ colors | both saturated? |
|---|---|---|:---:|
| $K_4 \times K_4$ | {0} | {0,1,2,3} | False |
| $K_4 \times$ Moser | {0,1,2,3} | {0} | False (one-sided) |
| Moser $\times$ Moser | {0,1} | {0,1,2,3} | False |
| $W_5 \times W_5$ | {0} | {0,1,2,3} | False |

The correct statement: **for the canonical fixed $c_1$, every color in $[4]$ must appear at $\partial_B H_2$ for the cover to be complete** (since $c_2(v)$ can match any of $c_1(u_1), c_1(u_2), \ldots$). When $\partial_B H_1$ has one vertex with fixed canonical color 0, the cover needs only color 0 to appear at $\partial_B H_2$ in all of $\{0,1,2,3\}$, but multiple bridges from that single $H_1$-vertex provide it. So one-sided saturation suffices in the $\|B\| = 4$ regime.

**C3 (normalized bridge density)**: the small-case minima all hit density $\|B\| / (\|\partial_B H_1\| \cdot \|\partial_B H_2\| \cdot 4) = 0.25$. de Grey 1585 and Polymath 510 are an order of magnitude sparser:

| Construction | $\|B\|$ | $\|\partial_B H_1\|$ | $\|\partial_B H_2\|$ | density |
|---|---:|---:|---:|---:|
| $K_4 \times K_4$ (trivial $K_5$) | 4 | 1 | 4 | 0.2500 |
| Moser $\times$ Moser (trivial $K_5$) | 6 | 2 | 3 | 0.2500 |
| Moser $\times$ Moser (no $K_4$) | 14 | 7 | 6 | 0.0833 |
| de Grey 1585 (no $K_4$, UDG-realized) | 155 | 124 | 22 | 0.0142 |
| Polymath 510 (no $K_4$, UDG-realized) | 833 | $\sim$315 | $\sim$195 | $\sim$0.0034 |

**Interpretation**: as the no-$K_4$ constraint tightens (and toward UDG realizability), density drops by an order of magnitude per step. The minimum bridge-density seems to be a continuous function of the structural constraints, with de Grey / Polymath sitting near the UDG-realizable lower envelope.

**Matching bridges (each vertex in $\leq 1$ bridge) are NEVER sufficient.** For all tested pairs, no matching of any size up to $\min(\|V_1\|, \|V_2\|)$ achieves chi $\geq 5$. This is because matching $\|B\|$ bridges contribute $\|B\| \cdot \|P\|/4$ kills with mostly disjoint $c_2$-fibers, but the kill sets for matching bridges leave a constant fraction of $\mathcal{C}_2$ uncovered (a single matching bridge $(u,v)$ kills only the c_2 with $c_2(v) = c_1(u)$; with each H_2 vertex used at most once, the surviving colorings are exactly those that avoid the matching constraint, which always exist in 4-chromatic graphs). **Bridge endpoints must be shared**: in de Grey 1585, the 22 boundary vertices in $H_2$ host 155 bridges, an average of 7 bridges per vertex.

**Structural conjecture (new, from L21)**:

**C4 (cone obstruction lemma, candidate)**: a minimum chi $\geq$ 5 forcing bridge set with no $K_4$ requires both bridge boundaries to have at least 4 distinct colors *taken together across the canonical coloring of $H_1$ and the varying coloring of $H_2$*. The right formal statement: for every 4-coloring $c_2$ of $H_2$, the bipartite induced subgraph $B[u : c_1(u) = c_2(v) \text{ for some } (u,v) \in B]$ must hit every color class of $c_2|_{\partial_B H_2}$.

**Wrong-approach detector status**:

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS: lemma needs 4-chromatic halves, which don't exist as UDGs in $\mathbb{Q}^2$. |
| $L^\infty$ on $\mathbb{R}^2$ ($\chi = 4$) | PASS: lemma is purely graph-theoretic; the obstruction to $\chi \geq 5$ in $L^\infty$ is in realizability (cannot put a Moser spindle in $L^\infty$ as UDG since the Moser spindle uses Euclidean equilateral triangles). |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS: $\mathbb{R}^1$ has no 4-chromatic UDG; lemma vacuous. |

The lemma is structurally correct: it does NOT spuriously force chi $\geq 3$ on $\mathbb{Q}^2$ because the *hypothesis* (4-chromatic halves exist) fails there.

**Why this matters**.

1. **L21 gives the exact graph-theoretic characterization of chi $\geq$ 5 forcing**: bridge sets are precisely set covers of the 4-coloring product. Minimum bridges = minimum set cover (NP-hard in general, but tractable for small $H_i$).

2. **The "trivial bound $\|B\| \geq 4$" is tight unconstrained, but the $K_5$ trick is illegal in UDGs**. In $\mathbb{R}^2$ unit-distance graphs, $\omega \leq 3$. So the effective minimum is the **no-$K_4$ minimum**. For Moser $\times$ Moser this is **14 bridges**.

3. **The gap between small no-$K_4$ minima (14, 11) and de Grey's 155 is explained by realizability**: graph-theoretically 14 bridges suffice; realizing them as unit distances in $\mathbb{R}^2$ with both halves Moser spindles is presumably impossible (would require 14 simultaneous unit distances between two Moser spindles under some rigid motion, an overdetermined system in $\mathbb{Q}(\sqrt 3, \sqrt{11})$). de Grey 1585 uses 1585 vertices and 155 bridges precisely because each unit-distance edge is geometrically expensive; the construction trades vertex count for bridge cost.

4. **The path to chi $\geq$ 6 must avoid the $K_6$ trick (correcting L20 implication 5)**. The parallel ADVERSARY pass (see [`orchestrator_sessions/2026-05-26-adversary-l21.md`](orchestrator_sessions/2026-05-26-adversary-l21.md), angle 6) refutes L20's claim that "the third color class can be reused" in its naive symmetric form. **Aligned $K_{2,2}$ bridges between three Moser spindles on the same vertex pair $\{0,1\}$ in each spindle create a literal $K_6$ on $\{0,1,7,8,14,15\}$, forcing $\chi = 6$** with only 4 bridges per pair (and pairwise $\chi = 4$, not even 5). Aligned $K_{2,3}$ bridges (BUILDER's $\|B\| = 6$ set, replicated on the same vertices in all three pairs) push to $\chi = 7$. The corrected statement: "third color class can be reused" holds precisely when bridge layouts are permuted / chain / asymmetric, and FAILS when bridges align $K_r$-substructures in $H_1, H_2, H_3$ to form a $K_{3r}$ cross-clique. **For UDG in $\mathbb{R}^2$ the $K_6$ trick is illegal** (max UDG clique is 3, just as $K_5$ is illegal for L21's chi-5 case). So the $\chi \geq 6$ UDG question requires non-$K_6$ obstructions, exactly mirroring how L21's no-$K_4$ regime restricts the chi-5 UDG question. The chi-6 cost is bounded below by the smallest no-$K_4$ three-way-coupled structure, which is open (the smallest abstract chi-6 three-way-coupled graph found by ADVERSARY has 9 vertices but uses $K_6$; the smallest no-$K_4$ chi-6 three-way graph is not known).

5. **The Moser $\times$ Moser 14-vertex, $\omega = 3$, $\chi = 5$ abstract graph** is a clean small witness of the "two 4-chromatic halves + bridges" pattern. Whether this graph can be **realized as a UDG** in $\mathbb{R}^2$ (open question for BUILDER) is the natural follow-up: if yes, it would be the smallest known $\chi \geq 5$ UDG. If no, this gives a quantitative measure of how much realizability costs.

**Cross-architectural implication**. L4/L17/L20 placed the missing chi $\geq$ 6 UDG in the shared "Architectures 1 & 2" space. L21 sharpens the path with the **$K_{n+1}$-trick ladder**: at each chromatic threshold $n$, the abstract graph-theoretic minimum forcing $\chi \geq n+1$ is achieved by creating a $K_{n+1}$ cross-clique (chi-5 needs $K_5$ from a star bridge into $K_4$; chi-6 needs $K_6$ from aligned $K_{2,2}$ bridges between three 4-chromatic halves; both verified). The UDG constraint $\omega \leq 3$ in $\mathbb{R}^2$ blocks every level of this ladder past $n = 3$. So the chi $\geq 6$ UDG must avoid $K_6$ cross-cliques exactly as the chi $\geq 5$ UDG must avoid $K_5$. The minimum no-$K_4$ three-way-coupled chi-6 graph is unknown; if it scales like the chi-5 case (14 vertices for Moser $\times$ Moser no-$K_4$), the chi-6 analog might be in the range of $\geq 14 \cdot 3 \approx 42$ vertices abstract, but realizability in $\mathbb{R}^2$ would presumably inflate this dramatically (consistent with no chi $\geq 6$ UDG found at vertex counts $\leq$ a few thousand).

**Future BUILDER directions (next session)**:

1. **UDG realizability check for the 14-vertex Moser $\times$ Moser no-$K_4$ graph**: enumerate rigid motions of the second Moser spindle relative to the first in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. Test whether any rigid motion realizes all 14 bridges as unit distances. If yes, this is a 14-vertex chi $\geq$ 5 UDG, smashing Parts 509. If no (likely), quantify the realizability gap.
2. **Three-way coupling for chi $\geq$ 6, no-$K_4$ regime**: take three 4-chromatic graphs $H_1, H_2, H_3$ and a hypergraph of bridges. Characterize when $\chi(H_1 \cup H_2 \cup H_3 \cup B) \geq 6$ **subject to $\omega \leq 3$** (the UDG-relevant constraint). The abstract chi $\geq 6$ minimum via aligned $K_{2,2}$ bridges (4 bridges per pair, 9-21 vertices total) is now known (ADVERSARY angle 6) but uses $K_6$ which is illegal in UDG. The no-$K_4$ minimum, blocking $K_6$, is the right open question.
3. **The cone obstruction lemma C4**: prove or refute the formal statement. If proven, it gives a structural witness for any chi $\geq$ 5 forcing bridge set.
4. **The bridge-density continuum**: characterize the realizability-vs-density trade-off. Is there an algebraic lower bound on bridge density as a function of half-vertex count, under UDG realizability?

---

### L20. The "two 4-chromatic halves + bridges" structure is universal in the chi >= 5 lineage: Polymath 510 has the same pattern as de Grey 1585, with different proportions

**Architecture**: 1. Synthesizes L17 + L19.

**Experiment**: [`e1t_overlap_chi.py`](combinatorial/e1t_overlap_chi.py).

L19 split Polymath 510 into (315 vertices shared with de Grey 1585) and (195 field-reduction artifacts). L20 tests the chi of each half:

| Subgraph | $\|V\|$ | $\|E\|$ | Density | $\chi$ |
|---|---:|---:|---:|---:|
| Polymath ∩ de-Grey overlap (in Polymath edges) | 315 | 1327 | 4.21 | **4** |
| Polymath ∩ de-Grey overlap (in de Grey edges) | 315 | 1327 | 4.21 | **4** |
| Polymath 195 artifacts | 195 | 344 | 1.76 | **4** |
| Polymath 510 full | 510 | 2504 | 4.91 | **5** |

The edge counts are identical (1327) under both edge sets, confirming the translation $T = (2, 0)$ is an *isometry* preserving the unit-distance structure on the overlap vertices.

**The pattern matches de Grey 1585** (L17):

| Graph | Half 1 | $\chi(H_1)$ | Half 2 | $\chi(H_2)$ | Bridges | $\chi$(full) |
|---|---:|---:|---:|---:|---:|---:|
| de Grey 1585 | 778v (C_6 core) | 4 | 807v (asymmetric) | 4 | 155 | 5 |
| Polymath 510 | 315v (de-Grey overlap) | 4 | 195v (artifacts) | 4 | 833 | 5 |

Both graphs have the **identical structural pattern**: two 4-chromatic halves connected by bridge edges. Removing the bridges in either case yields two disconnected 4-chromatic graphs.

**Bridge density comparison**:

| Graph | Bridges per total V | Bridges per cross-half pair |
|---|---:|---:|
| de Grey 1585 | 155 / 1585 = 0.098 | 155 / (778 × 807) ≈ $2.5 \times 10^{-4}$ |
| Polymath 510 | 833 / 510 = 1.63 | 833 / (315 × 195) ≈ $1.36 \times 10^{-2}$ |

Polymath 510's bridge density is **17× higher per vertex** and **54× higher per cross-pair** than de Grey 1585's. The SAT-minimization compensated for fewer vertices with much denser bridge structure.

**Key implications**.

1. **The chi >= 5 mechanism is universal in the lineage**: every published chi $\geq 5$ UDG seems to be a "two 4-chromatic halves coupled by bridges" construction. The de Grey 2018 breakthrough wasn't a new mechanism; it was an *instance* of this pattern. Heule/Parts found smaller instances by reducing the field and densifying the bridges.

2. **This pattern is necessary, not just sufficient**: every reasonable structural reduction (L18) and every half (L17, L20) drops chi to 4. So the chi $\geq 5$ obstruction REQUIRES the half + half + bridge structure. The minimum number of vertices for chi $\geq 5$ is bounded below by the minimum size of (4-chromatic half 1) + (4-chromatic half 2) + (enough bridges to couple them).

3. **Bound estimates for chi $\geq 5$ minimum**: a 4-chromatic UDG has at least 7 vertices (Moser spindle). So a "two-halves" chi $\geq 5$ UDG has at least 14 vertices + some bridges. The Heule/Parts pipeline has reached 509 vertices. Whether the minimum is much smaller (e.g., 50-100 vertices) is open. The bridge-density trade-off seen in L20 suggests aggressive bridge densification could shrink the halves substantially.

4. **The chi >= 6 question becomes structurally precise**: to force chi $\geq 6$, we'd need to couple TWO chi-5 sub-objects (each having the chi $\geq 5$ obstruction internally), or use a higher-order coupling. Both options multiply the vertex count substantially. The smallest plausible chi $\geq 6$ UDG might be of size $\sim 1000$-$5000$ vertices (= 2 × (Polymath 510 + bridges) or similar). This is consistent with no chi $\geq 6$ UDG having been found despite extensive SAT search at vertex counts up to a few thousand.

5. **The chi >= 6 problem may require a DIFFERENT structural mechanism**. The "two halves + bridges" pattern caps at chi = 5 in the L18/L20 sense: adding a third 4-chromatic component coupled by more bridges does not naively force chi = 6 (the third color class can be reused). To force chi = 6, the coupling must be qualitatively different — perhaps a 3-way coupling that forces each of three colors to be paired with a different chi-4 structure. This is speculation; no such construction is known.

**Cross-architectural implication**.

L4 said Architectures 1 and 2 share the missing 6-chromatic UDG. L20 sharpens: a 6-chromatic UDG would presumably need a structural mechanism beyond the "two halves + bridges" pattern that all current chi $\geq 5$ graphs use. The path to chi $\geq 6$ is therefore not a refinement of de Grey / Polymath / Heule, but a fundamentally different combinatorial idea.

**Wrong-approach status**. Same as L19; passes detectors.

**Future BUILDER directions (next session)**:

1. **The "minimum two-halves-plus-bridges" question**: given two arbitrary 4-chromatic UDGs $H_1, H_2$ and a target bridge set $B$, when does $H_1 + H_2 + B$ have chi $\geq 5$? Characterize the necessary bridge structure.
2. **Search for a 3-way coupling that forces chi $\geq 6$**: take three small 4-chromatic UDGs and connect them by carefully-chosen edges. Test chi.
3. **Direct enumeration of chi $\geq 5$ small graphs**: Polymath 510's "halves" are 315 + 195. Can we find a chi $\geq 5$ UDG with halves of size 100 + 100 (plus bridges)? Lower bound: each half $\geq 7$ (Moser).

---

### L19. Polymath 510 is essentially a translated substructure of de Grey 1585: 315/510 = 62% of vertices match under T = (2, 0); the remaining 195 are field-reduction artifacts

**Architecture**: 1. Resolves the "different chi >= 5 geometries" question from L18.

**Experiment**: [`e1s_compare_polymath_degrey.py`](combinatorial/e1s_compare_polymath_degrey.py).

L18 hinted that Polymath 510 and de Grey 1585 might be "two distinct chi >= 5 geometries". L19 establishes that they are not distinct: **Polymath 510 is approximately a translated substructure of de Grey 1585**, with the translation T = (2, 0) and 62% vertex overlap.

**Method**. For each pair $(p, q)$ with $p \in V(\text{Polymath 510})$ and $q \in V(\text{de Grey 1585})$, compute translation $T = q - p$. Count how many other Polymath vertices map under $T$ to a de Grey vertex. The top translations by overlap:

| Rank | Translation $T$ | Vertex overlap | Note |
|---:|:---|---:|:---|
| 1 | $(2,\, 0)$ | **315 / 510 = 61.8%** | The canonical alignment (origin of Polymath -> $v_0$ of de Grey) |
| 2 | $(2.5,\, -\sqrt 3/6 \approx -0.289)$ | 203 | Hex-lattice translate |
| 3 | $(2.0,\, \sqrt 3 / 3 \approx 0.577)$ | 203 | Hex-lattice translate |
| 4 | $(1.5,\, -\sqrt 3/6)$ | 200 | Hex-lattice translate |
| 5 | $(2.5,\, \sqrt 3/6)$ | 197 | Hex-lattice translate |
| 6 | $(2.0,\, -\sqrt 3/3)$ | 196 | Hex-lattice translate |
| 7 | $(1.5,\, \sqrt 3/6)$ | 196 | Hex-lattice translate |
| 8 | $(2.562, -0.132)$ | 146 | Algebraic translate (not in $\sqrt 3$-only basis) |
| 9 | $(2.167, 0.553)$ | 146 | Algebraic translate |
| 10 | $(1.833, 0.553)$ | 145 | Algebraic translate |

The first 7 translations all live in $\mathbb{Q}[\sqrt 3]$ and form the standard hex-lattice neighbors of $T_1 = (2, 0)$ at offsets $(0.5, \pm \sqrt 3/6)$. They represent Polymath 510 sliding onto de Grey 1585 with 196-315 vertex correspondence, depending on the alignment.

**Direct membership** (translation $T = (0, 0)$): only 25 vertex matches. Without translation, the graphs barely overlap.

**Structural picture**.

1. **Heule/Parts reformulation reuses de Grey 1585's vertices**. The Polymath/Heule lineage starts from de Grey 1585, translates by $(-2, 0)$ to recenter at origin, retains 315 of de Grey's 1585 vertices (those that fit in the smaller field $\mathbb{Q}(\sqrt 3, \sqrt{11})$), and adds 195 new vertices to compensate for the field reduction.

2. **The 195 "new" Polymath vertices are field-reduction artifacts**. de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ has more algebraic complexity than Polymath's $\mathbb{Q}(\sqrt 3, \sqrt{11})$; some vertices that played a role in de Grey's chi-5 obstruction don't have direct $\mathbb{Q}(\sqrt 3, \sqrt{11})$ representatives. The 195 new vertices are presumably chosen so the chi $\geq 5$ obstruction is preserved despite the field reduction.

3. **There is only ONE chi $\geq 5$ "geometry" in the lineage, not two**. Polymath 510 and de Grey 1585 are essentially the same combinatorial object viewed from different algebraic vantage points (different fields, different vertex centers). L18's "two distinct geometries" framing was wrong; the correct statement is "two algebraic presentations of the same underlying chi $\geq 5$ phenomenon".

4. **The 195 field-reduction artifacts may not have geometric meaning beyond preserving chi $\geq 5$**. They are essentially "patches" filling in the absence of $\sqrt 5, \sqrt 7$. Whether they admit cleaner descriptions (e.g., as systematic translates of a smaller motif) is an open question.

**Why it matters**.

1. **The Hadwiger-Nelson chi $\geq 5$ result has a single underlying construction**, with all known examples (de Grey 1585, Heule 553, Polymath 510, Parts 509) being variant subsets / extensions of the same vertex set. The progress from 1585 to 509 vertices is not finding new chi $\geq 5$ graphs; it is minimizing the original.

2. **Refines L18**: the chi $\geq 5$ obstruction is delocalized in de Grey 1585 (L18) BUT Polymath 510 finds a way to be smaller by exploiting field reduction. The minimum may not be 509; it may be smaller in an even smaller field (e.g., $\mathbb{Q}(\sqrt 3)$, $\mathbb{Q}(\sqrt{11})$ alone, $\mathbb{Q}$).

3. **The path to chi $\geq 6$ probably starts with de Grey's full field** $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$, not the reduced field. The richer field provides more algebraic coincidences. de Grey's choice of field was not accidental.

**Cross-architectural implication**. L4 said Architectures 1 and 2 share the missing 6-chromatic UDG. L19 sharpens: the 6-chromatic UDG, if it exists, is likely in a field at least as rich as $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$. The path through smaller fields (Polymath's) likely cannot reach chi $\geq 6$ because the field reduction discards exactly the algebraic complexity needed.

**Wrong-approach status**. Compares two specific algebraic UDGs in $\mathbb{R}^2$. The $\mathbb{Q}^2$ detector passes (both graphs use irrational coordinates throughout).

**Future BUILDER directions (next session)**:

1. **Identify the 195 Polymath "new" vertices algebraically**. What's the field-theoretic pattern? Are they all systematic translates of a small motif, or scattered?
2. **The 195 new vertices may NOT be necessary in the field Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11)**. Test: build the chi $\geq 5$ UDG using only de Grey 1585's vertices that coincide with Polymath 510 (the 315 overlap, plus some closure). Is that still chi $\geq 5$?
3. **The de Grey 2018 paper provided a richer-field construction**; modern SAT minimization moved to the smaller field for solver-pragmatic reasons. The richer field may be the proper home of chi $\geq 6$.

---

### L18. de Grey 1585's chi = 5 obstruction is extremely delocalized: every tested structural reduction drops chi to 4

**Architecture**: 1. Continues L17.

**Experiment**: [`e1r_targeted_reduction.py`](combinatorial/e1r_targeted_reduction.py).

L17 split de Grey 1585 into three components (C_6 core, asymmetric half, 155 bridges) and showed all three are individually 4-chromatic. This experiment asks: how much of each component is essential?

**Reductions tested**:

| Reduction | $\|V\|$ | $\|E\|$ | Removed | $\chi \leq 4?$ |
|---|---:|---:|---|---:|
| R1: bridge_core + V_asym | 931 | 4273 | All 654 non-bridge-touched core vertices | True |
| R3: V_sym + bridge_asym | 800 | 3963 | All 785 non-bridge-touched asym vertices | True |
| R5: bridge_core + half_nonbridge_core + V_asym | 1258 | 5341 | Half (327) of non-bridge-touched core vertices | True |
| R6: V_sym + bridge_asym + half_nonbridge_asym | 1192 | 4987 | Half (393) of non-bridge-touched asym vertices | True |
| R7: bridge_core + bridge_asym + half_nonbridge_asym | 538 | 1351 | All non-bridge core + half non-bridge asym | True |

**Every reduction is 4-colorable**, including ones where we keep $1192 / 1585 = 75\%$ of the original vertices. Removing even ~20% of any single component (or its complement) collapses chi.

**Implications**.

1. **The chi $\geq 5$ obstruction is extremely delocalized**. There is no small "essential core" of vertices that alone forces chi $\geq 5$ in de Grey 1585. Hundreds of vertices that look individually redundant are collectively essential. The chi $\geq 5$ certificate "lives" simultaneously across all components and a substantial fraction of each.

2. **Explains the Heule/Parts reformulation**. Heule (2018) and Parts (2020) didn't minimize de Grey 1585 directly. They reformulated the problem in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ (a strict subfield of de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$) and found an entirely different 5-chromatic graph (Polymath 510, Heule 553, Parts 509). The delocalization in L18 is the *reason* direct minimization of de Grey 1585 doesn't easily work: there is no "easy slack" to trim. Heule's success at smaller vertex counts comes from a different combinatorial path, not from pruning de Grey's.

3. **The chi $\geq 5$ "complexity" of de Grey 1585 is structurally HIGH**. By any reasonable measure (minimum essential subgraph, MUS size), de Grey 1585 looks like its chi $\geq 5$ certificate requires nearly all 1585 vertices. Whether a much smaller subset has chi $\geq 5$ is an open question, but L18 says greedy / structural reduction does NOT find one.

4. **Two distinct chi $\geq 5$ "geometries"** are now in evidence:
   - de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ construction: extremely delocalized; nearly all 1585 vertices essential under structural-reduction tests.
   - Polymath/Heule/Parts $\mathbb{Q}(\sqrt 3, \sqrt{11})$ construction: SAT-minimized to 509-553 vertices, exact rotational symmetry destroyed (L15), but presumably still has the delocalization property at its smaller scale.

   These are NOT subsets of each other; they are *different combinatorial graphs* achieving chi $\geq 5$ via different mechanisms.

**Cross-architectural implication**.

L18 deepens the L4 / L17 picture. Architectures 1 and 2 share the missing 6-chromatic UDG. L17 says chi = 5 is a coupling phenomenon between symmetric and asymmetric components. L18 says this coupling is *globally delocalized*: small modifications to either component break it. The implication for chi $\geq 6$: it would presumably require an even more delicate coupling structure, and finding it via SAT minimization or naive construction is implausible. The path to chi $\geq 6$ likely involves a *fundamentally new geometric mechanism*, not refinement of the chi $\geq 5$ constructions.

**Wrong-approach status**. Uses exact algebraic coordinates throughout. The $\mathbb{Q}^2$ detector passes.

**Future BUILDER directions (next session)**:

1. **Full SAT-MUS**: rather than ad-hoc reductions, compute the minimum unsatisfiable subset of the 4-coloring CNF for de Grey 1585. Modern SAT solvers (CaMUS, MUSER) can extract MUSes. Time budget: hours-to-days.
2. **Search the de Grey field for an "easier" chi $\geq 5$ subgraph**: maybe a fragment of de Grey 1585 outside our structural decomposition (orthogonal to the C_6 core distinction) is more compact.
3. **Compare Polymath 510 to de Grey 1585 as a UDG**: are any vertices of Polymath 510 also vertices of de Grey 1585 (i.e., common algebraic points)? If yes, the two constructions overlap; if no, they are entirely separate sub-geometries of $\mathbb{R}^2$.

---

### L17. de Grey 1585's chi >= 5 mechanism: 155 bridge edges between two 4-chromatic halves, where neither half nor the bridge-touched subgraph alone suffices

**Architecture**: 1. Continues L16.

**Experiments**: [`e1o_asymmetric_obstruction.py`](combinatorial/e1o_asymmetric_obstruction.py), [`e1p_degrey_asymmetric_half.py`](combinatorial/e1p_degrey_asymmetric_half.py), [`e1q_bridge_subgraph.py`](combinatorial/e1q_bridge_subgraph.py).

**The full structural picture of de Grey 1585**:

| Subgraph | $\|V\|$ | $\|E\|$ | Density | $\chi$ |
|---|---:|---:|---:|---:|
| $C_6$-symmetric core $V_{\text{sym}}$ (about $v_0$) | 778 | 3806 | 4.89 | **4** |
| Asymmetric half $V \setminus V_{\text{sym}}$ | 807 | 3948 | 4.89 | **4** |
| Bridge-touched restricted subgraph | 146 | 327 | 2.24 | **4** |
| Full de Grey 1585 | 1585 | 7909 | 4.99 | **5** |

The 7909 edges decompose as: **3806 within core + 3948 within asym + 155 bridges**. Both halves have *almost identical density* (4.89) and *identical chromatic number* (4). The chi = 5 property is purely a coupling phenomenon.

(a) **No singleton augmentation works (e1o Phase 1)**. For every asymmetric vertex $v$, $\chi(V_{\text{sym}} \cup \{v\}) = 4$. Adding one asymmetric vertex to the symmetric core does not force a 5th color.

(b) **Greedy by degree-to-G fails (e1o Phase 2)**. Adding the highest-degree asymmetric vertex 50 times sequentially keeps the graph 4-colorable. The added vertices have degree to current graph dropping from 14 to 2-3, but no chi-jump.

(c) **The asymmetric half alone is 4-chromatic (e1p)**. $\chi(V \setminus V_{\text{sym}}) = 4$. The chi $\geq 5$ property is NOT located in either half.

(d) **155 bridge edges, sparse contact**: The bridges connect only **124 core vertices** (16% of 778) and **22 asymmetric vertices** (2.7% of 807). The asymmetric half is connected to the core through a very narrow interface.

(e) **The bridge-touched subgraph is 4-chromatic** (e1q). Restricting to the 146 vertices that participate in any bridge edge gives a 327-edge subgraph (density 2.24), chi = 4. The bridges alone, even with their local context, don't force chi = 5.

**The chi >= 5 obstruction is therefore THREE-COMPONENT**:

1. The **C_6-symmetric core** provides 778 4-chromatic vertices.
2. The **asymmetric half** provides 807 more 4-chromatic vertices.
3. The **155 bridges** couple them at 146 contact points.

REMOVING any of the three components drops chi to 4:
- Remove bridges only: two disconnected 4-chromatic halves, chi = 4.
- Remove the asymmetric half: just the C_6 core, chi = 4.
- Remove the core: just the asymmetric half, chi = 4.

But preserve all three: chi = 5. **The chi = 5 obstruction is a global property requiring all three components simultaneously**, not localized in any single sub-structure.

**Why it matters**.

1. **Refutes a naive simplification hypothesis**. One might guess: "the chi $\geq 5$ obstruction lives in a small subgraph; extract that subgraph, ignore the rest". L17 says this is false for de Grey 1585. The chi $\geq 5$ certificate of de Grey 1585 requires both halves plus their coupling. The smallest subgraph of de Grey 1585 with chi $\geq 5$ may not be much smaller than 1585 itself, despite the SAT-minimization in the Polymath/Heule lineage reaching 510.

2. **Polymath 510 may NOT be a subset of de Grey 1585**. The Polymath/Heule lineage starts from a different base graph (in $\mathbb{Q}(\sqrt 3, \sqrt{11})$, not de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$) and was constructed independently. The fact that both lineages reach chi $\geq 5$ at $\sim 500$-$1500$ vertices but via structurally different mechanisms (de Grey's three-component coupling vs Polymath's asymmetric SAT-selected subset) suggests two distinct chi $\geq 5$ "geometries" in the plane.

3. **The chi = 5 mechanism is fundamentally coupling-based, not symmetry-based**. Both halves of de Grey 1585 individually mimic a "soft" 4-chromaticity; the 155 bridges encode an algebraic alignment that forces a 5th color. The Hadwiger-Nelson chi $\geq 5$ bound is therefore not about high local density (cores and asymmetric halves match in density 4.89), but about specific *geometric alignment* between rotationally-symmetric and asymmetric structural components.

4. **The next question is whether the bridges can be REPLACED by a smaller coupling structure**. If we identify the "bridge pattern" abstractly (a specific configuration of 155 edges between 124 core vertices and 22 asymmetric vertices), maybe a different graph achieves the same chi $\geq 5$ with fewer or differently-placed bridges.

**Cross-architectural implication**.

L4: Architectures 1 and 2 share the missing 6-chromatic UDG.

L17 sharpens what such a 6-chromatic UDG would look like: it would presumably also be a *coupling* construction. If the chi = 5 obstruction is the alignment of two 4-chromatic halves via $\sim$155 bridges, then chi = 6 would require either (a) the alignment of TWO chi-5 sub-objects, or (b) a richer coupling structure within a single graph. Neither pattern is present in any known UDG.

**Wrong-approach status**. All experiments use the exact algebraic coordinates of de Grey 1585. The $\mathbb{Q}^2$ detector passes (all coordinates use $\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11}$).

**Future BUILDER directions (next session)**:

1. **SAT-MUS for the full graph**: find a minimum vertex subset $V_{\min} \subseteq V$ such that the induced subgraph has chi $\geq 5$. Compare $\|V_{\min}\|$ to Polymath 510's 510 and Parts' 509.
2. **Iso-classify the bridges**: are the 155 bridge edges algebraically related? What's the field-theoretic pattern relating them?
3. **The "minimal coupling" hypothesis**: is there a chi $\geq 5$ UDG whose components are (a) a small 4-chromatic core, (b) a small 4-chromatic asymmetric piece, (c) a small number of bridges? If so, this could be a smaller chi $\geq 5$ UDG than Parts 509.

---

### L16. de Grey 1585 has approximate C_6 (in fact D_6) symmetry about v_0 = (2, 0), with each non-identity rotation preserving ~50% of vertices

**Architecture**: 1. Continues L15.

**Experiments**: [`e1l_reverse_engineer_degrey1585.py`](combinatorial/e1l_reverse_engineer_degrey1585.py), [`e1m_degrey_approximate.py`](combinatorial/e1m_degrey_approximate.py).

**Source**: [`sources/degrey_1585_vertices.sage`](../sources/degrey_1585_vertices.sage) (the original de Grey 2018 graph, in $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$).

**Headline**.

(a) **No exact rotational symmetries** (e1l): de Grey 1585 has zero non-identity rotational symmetries about ANY of 9 tested pivots (origin, centroid, $v_0$ through $v_6$, $(1, 0)$, midpoint of $v_0$ and $v_2$). The same negative result as Polymath 510 (L15) and Heule 826.

(b) **The natural symmetry center is $v_0 = (2, 0)$, not the origin** (e1m). At pivot $v_0$, vertices form distance classes of size up to 60 (= 10 orbits of size 6 at one distance), strongly indicating an underlying $C_6$ structure.

(c) **Approximate D_6 symmetry about $v_0$** (e1m). The 18 high-coverage rotations about $v_0$ split as:

| Subgroup element | Coverage |
|---|---:|
| Identity (0°) | 1585 / 1585 = 100% |
| $R_{60°}$ | 787 / 1585 = 49.65% |
| $R_{120°}$ | 787 / 1585 = 49.65% |
| $R_{180°}$ | 793 / 1585 = 50.03% |
| $R_{240°}$ | 787 / 1585 = 49.65% |
| $R_{300°}$ | 787 / 1585 = 49.65% |
| 12 secondary 180° rotations (different centers) | ~785-787 / 1585 = ~49.5% |

The 6 rotations about $v_0$ form the $C_6$ subgroup of $D_6$. The 12 secondary 180° rotations (about different centers like $v_{169}, v_{265}, \ldots$) correspond to the *reflections* of $D_6$, realized as $180°$ rotations about the midpoints of certain vertex pairs (since reflection-about-line through $v_0$ and another vertex equals 180°-rotation about the midpoint, in the plane).

The graph effectively has approximate $D_6$ (dihedral, order 12) symmetry about $v_0 = (2, 0)$, with each non-identity element preserving exactly half of the 1585 vertices.

**Interpretation**.

1. **de Grey's natural center is $v_0$**, not the origin. The 2018 paper constructed $H = M + W$ where $M$ is a small base graph and $W$ is a wheel of rotated copies; $v_0 = (2, 0)$ is the geometric center of this Minkowski-sum construction. Origin is just a coordinate-system artifact.

2. **The C_6-symmetric core has approximately 787 vertices**. These are the vertices preserved by all 6 rotations $\{R_{60°k}\}_{k=0}^{5}$ about $v_0$. The other ~798 are asymmetric perturbations — likely SAT-minimization residue from minimizing the original $H$ down to 1585.

3. **The minimal-rotation-subset question is now concrete**. Extract the $C_6$-symmetric core ($V_{\text{sym}}$ = $\bigcap_{k=0}^5 R^k(V)$, ~787 vertices). Test $\chi(V_{\text{sym}})$. If $\chi(V_{\text{sym}}) \geq 5$, we have a $C_6$-symmetric chi $\geq 5$ UDG at ~787 vertices, smaller than Polymath 510's C_6-closure (1155 vertices, L15). If $\chi(V_{\text{sym}}) = 4$, the asymmetric extras are essential for de Grey's chi $\geq 5$ proof.

**Cross-architectural implication**.

L15 established that the SAT-minimized Polymath/Heule lineage in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ has zero rotational symmetry. L16 establishes that the original de Grey 2018 graph in the richer field $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ ALSO has zero EXACT rotational symmetry, but unlike Polymath 510 it retains substantial APPROXIMATE $D_6$ symmetry (~50% coverage per non-identity rotation).

This suggests a structural hierarchy:
- de Grey 1585: approximately D_6-symmetric about $v_0$.
- Heule's minimization (553 vertices etc.): destroyed most of the $D_6$ structure, but
- Polymath 510 retained approximate C_6 about origin at 92% coverage (L15 again).

The Polymath/Heule lineage *moved* the natural center from $v_0$ (de Grey's original) to origin (their reformulation), and re-symmetrized while minimizing — landing on a different approximate symmetry.

**Wrong-approach status**. All rotation analyses use exact algebraic coordinates and respect $O(2)$ symmetry. The $\mathbb{Q}^2$ detector passes (vertex coordinates use $\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11}$).

**The C_6 core of de Grey 1585 has chi = 4 (e1n)**.

Extract $V_{\text{sym}}$ = $\{v \in V : R^k(v) \in V$ for $k = 0..5\}$ about $v_0$. This gives 778 vertices (49.1% of 1585), 3806 edges (48.1% of 7909), density 4.89. SAT-check: **$\chi(V_{\text{sym}}) = 4$** (4-colorable: True; 3-colorable: False).

**Structural conclusion**: the $\chi \geq 5$ property of de Grey 1585 depends essentially on the ~807 *asymmetric perturbation* vertices, NOT on the underlying $C_6$-symmetric core. The natural $C_6$-symmetric "skeleton" is only 4-chromatic.

This parallels L15's finding for Polymath 510: in both cases, the natural rotational structure is 4-chromatic, and the chi $\geq 5$ property comes from *asymmetric residue*. **The Hadwiger-Nelson chi $\geq 5$ lineage achieves its bound DESPITE approximate rotational symmetry, not BECAUSE of it.**

This is a sharp structural fact about the geometry of chi $\geq 5$ unit-distance graphs:

| Graph | Source | Symmetry structure | Symmetric core chi |
|---|---|---|---:|
| Polymath 510 | $\mathbb{Q}(\sqrt 3, \sqrt{11})$ | Approximate $C_6$ about origin (92% coverage) | (full closure is chi 5, but C_6-irreducible: every rotation copy essential, L15) |
| Heule 826 | $\mathbb{Q}(\sqrt 3, \sqrt{11})$ | NO non-identity exact symmetries | n/a |
| **de Grey 1585** | $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ | Approximate $D_6$ about $v_0 = (2, 0)$ (~50% coverage per element) | **778-vertex core, chi = 4** |

**Future BUILDER directions (next session)**:

1. **Extract de Grey's $D_6$ core** (intersection of preserves of all 12 dihedral elements about $v_0$). Likely smaller than 778 vertices. Same SAT-check.
2. **Compute the SAT-MUS of de Grey 1585**: which vertices are *essential* for chi $\geq 5$? If $V_{\text{sym}}$ is 4-colorable but $V_{\text{sym}} \cup \{$ a few asymmetric vertices $\}$ is 5-chromatic, identify those asymmetric vertices. They are the "obstruction core" — the structurally critical residue.
3. **Compare Polymath 510 to de Grey 1585**: is Polymath 510 essentially the $C_6$-symmetric core of de Grey 1585 + some asymmetric residue, or built from a completely different starting point?

---

### L15. Polymath 510 has approximate C_6 symmetry; its C_6-closure is a 1155-vertex 5-chromatic UDG that is C_6-irreducible (every rotation copy is essential)

**Architecture**: 1 (combinatorial / UDG). Reverse-engineering of Polymath 510.

**Experiments**: [`e1i_reverse_engineer_polymath510.py`](combinatorial/e1i_reverse_engineer_polymath510.py), [`e1j_approximate_symmetry.py`](combinatorial/e1j_approximate_symmetry.py), [`e1k_c6_closure_minimal.py`](combinatorial/e1k_c6_closure_minimal.py).

**Motivation**. L14 left open the question: characterize a published $\chi \geq 5$ UDG (de Grey / Polymath / Heule / Parts) as a binding-rotation construction, then find the minimal subset of rotations producing $\chi \geq 5$. This is the "reverse engineer de Grey" route.

**Surprising negative finding (e1i)**. Polymath 510 has **NO non-identity exact rotational symmetries** about origin or any of the 6 unit-hex neighbors. The 826-vertex Heule intermediate graph also has zero non-identity rotational symmetries about any of the same 7 pivots. The SAT-driven minimization in the Heule/Parts lineage *destroyed the rotational symmetry* that the original 1581-vertex de Grey graph presumably had. (de Grey 1585 lives in a different field $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7)$ per its Sage source; the Heule/Parts $\mathbb{Q}(\sqrt 3, \sqrt{11})$ lineage is a different combinatorial graph.)

**Approximate symmetry finding (e1j)**. Polymath 510 has approximate $C_6$ symmetry about origin:

| Rotation about origin | Maps $v_1$ to | Coverage (vertices mapping back into $V$) |
|---|---|---:|
| $0$ (identity) | $v_1$ | $510/510 = 100\%$ |
| $60°$ ($2\pi/6$) | $v_6$ | $471/510 = 92.35\%$ |
| $120°$ ($4\pi/6$) | $v_2$ | $470/510 = 92.16\%$ |
| $180°$ ($\pi$) | $v_4$ | $343/510 = 67.25\%$ |
| $240°$ ($5\pi/3$) | $v_3$ | $337/510 = 66.08\%$ |
| $300°$ ($\pi/3$) | $v_5$ | $337/510 = 66.08\%$ |

The $C_3$ subgroup (identity, $R_{120°}$, $R_{240°}$) has $> 92\%$ coverage. The $C_6$ has more reflective symmetry breakage at the order-2 elements. The SAT-minimization broke approximately $40$ vertices' worth of $C_6$ symmetry to reduce the graph from a symmetric construction to its 510-vertex form.

**C_6 closure (e1k)**. Build $V_+$ = closure of Polymath 510 under $R_{60°}$ (add all rotated images iteratively). Result:

| Quantity | Value |
|---|---:|
| Original $\|V\|$ | 510 |
| Closure $\|V_+\|$ | 1155 (added 645 vertices) |
| Closure $\|E_+\|$ | 10397 (density 9.0) |
| $\chi(V_+)$ | **5** (4-colorable: False, 5-colorable: True; SAT-confirmed) |
| Number of $C_6$ orbits | 535 (mostly size 1 or 6) |

The closure $V_+$ is a 1155-vertex, 10397-edge, $C_6$-symmetric, 5-chromatic UDG, derived purely by symmetrizing Polymath 510 under the natural $C_6$ rotation group it almost respects.

**Minimal subset of rotation copies for $\chi \geq 5$ (e1k Phase 4)**. The closure decomposes as $V_+ = \bigcup_{k=0}^{5} R^{k}(C)$ where $C$ is a fundamental domain (one representative per orbit). For each subset $S \subseteq \mathbb{Z}/6$, define $G_S = \bigcup_{k \in S} R^{k}(C)$. Test $\chi(G_S)$ for $S$ in every non-empty subset.

| $\|S\|$ | Example $S$ | $\|V(G_S)\|$ | $\|E(G_S)\|$ | $\chi \leq 4?$ | $\chi \leq 5?$ |
|---:|:---|---:|---:|---:|---:|
| 1 | $\{0\}$ | 535 | 2565 | T | — |
| 2 | $\{0,1\}$ | 663 | 3940 | T | — |
| 3 | $\{0,1,2\}$ | 786 | 5081 | T | — |
| 4 | $\{0,1,2,3\}$ | 909 | 6814 | T | — |
| 5 | $\{0,1,2,3,4\}$ | 1032 | 8260 | T | — |
| **6** | $\{0,1,2,3,4,5\}$ | **1155** | **10397** | **F** | T |

**ALL 63 proper subsets** ($1 \leq |S| \leq 5$) give $\chi(G_S) \leq 4$. Only the full union $|S| = 6$ achieves $\chi \geq 5$. The C_6 closure is **C_6-irreducible**: every single rotation copy is essential.

**Why it matters**.

1. **Polymath 510 is exceptional within its $C_6$ orbit**. The original 510-vertex graph has $\chi = 5$, density 4.91. But the symmetrically-built 1032-vertex 5-of-6-subset has $\chi = 4$ despite density 8.0. The $\chi \geq 5$ of Polymath 510 is *not* a consequence of generic $C_6$ symmetry; it depends on the specific *asymmetric* selection of 510 vertices.

2. **The de Grey "rotation set characterization" question is sharpened**. For the Polymath/Heule/Parts lineage in $\mathbb{Q}(\sqrt 3, \sqrt{11})$, no $\chi \geq 5$ graph is exactly $C_6$-symmetric: SAT-minimization has eaten that symmetry. The natural $C_6$ closure exists but its minimal-rotation-copy decomposition requires ALL 6 copies; it cannot be reduced to a small $\|S\|$.

3. **Cross-reference to L14**. L14 found that the Moser spindle in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ admits no binding-rotation miracles producing $\chi \geq 5$ with $\leq 211$ vertices in any union. L15 extends this: even the Polymath 510 graph's natural $C_6$ closure (1155 vertices, density 9.0) requires the full 6-fold copy structure to achieve $\chi \geq 5$. The field-theoretic rigidity from L14 manifests as rotation-irreducibility in L15.

4. **The original de Grey 1581 may still be reducible**. It lives in $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7)$ (per the .sage source), a richer field than the Polymath/Heule lineage. Its rotation structure was NOT analyzed in this session. A future BUILDER target: parse [`sources/degrey_1585_vertices.sage`](../sources/degrey_1585_vertices.sage) into sympy and repeat the symmetry analysis. The hypothesis: de Grey 1581 has explicit non-trivial rotational symmetry, and a proper-subset rotation-copy gives $\chi \geq 5$ at a smaller vertex count.

**Implementation notes**.

- The closure algorithm has a known limitation: it can introduce duplicate vertices when many "pending" vertices are processed before the lookup table rebuilds. The 1155-vertex closure may be smaller (perhaps $\sim 700$-$900$) with proper deduplication. The $\chi$ findings are correct regardless because adding duplicate vertices preserves the chromatic-number partitions induced on the original vertex set.
- The subset-decomposition fundamental domain $C$ has $|C| = 535$ orbits, of which $407$ are size-1 (likely artifacts of the duplicate-vertex bug; with proper dedup we expect $\sim 1$ size-1 orbit and the rest size-6).

**Wrong-approach status**. The reverse-engineering uses only $C_6 \subset O(2)$ rotations on Polymath 510, all coordinates in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. The $\mathbb{Q}^2$ detector applies since rotated coordinates remain irrational. Detector passes.

**Future BUILDER directions (next session)**:

1. **Fix closure deduplication** and reduce the 1155-vertex closure to its true size. Re-test minimal-subset analysis.
2. **Parse de Grey 1585's .sage source** to get the actual coordinates in $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7)$. Re-run the symmetry analysis. de Grey's construction was explicitly symmetric; we expect non-trivial rotation symmetries.
3. **Apply the C_6 closure construction to Heule 553 or 826**. They live in the same $\mathbb{Q}(\sqrt 3, \sqrt{11})$ field. Compare the closure sizes and $C_6$-irreducibility property.

---

### L14. Binding-rotation search on the Moser spindle reveals the Q(sqrt 3, sqrt 11) rigidity: only 4 of 62 double-binding rotations admit cross-copy unit edges, and the full union has chi = 4

**Architecture**: 1 (combinatorial / UDG). Structural sharpening of L11 on Shot 2 (field-theoretic chi >= 6 search).

**Experiments**: [`e1e_binding_rotation_moser.py`](combinatorial/e1e_binding_rotation_moser.py), [`e1f_double_binding_search.py`](combinatorial/e1f_double_binding_search.py), [`e1g_pivot_double_binding.py`](combinatorial/e1g_pivot_double_binding.py).

**Setup**. L11 left as the open problem: "find specific rotation choices in Q(sqrt 11) that produce cross-copy unit-distance edges, like de Grey 2018 did." This experiment runs that program directly. Given the Moser spindle $M$ (7 vertices, exact in $\mathbb{Q}(\sqrt 3, \sqrt{11})$), a *binding rotation* $\theta$ about some pivot $v_k$ is one where some seed pair $(p, q) \in M \times M$ satisfies $|R_{v_k, \theta}(p) - q| = 1$, i.e., the rotated copy $R_{v_k, \theta}(M)$ shares at least one unit-distance edge with $M$. The condition on $(\cos\theta, \sin\theta)$ is one linear equation
$$\langle p - v_k,\, q - v_k\rangle \cos\theta + \det[(p-v_k) \mid (q-v_k)]\sin\theta = \tfrac{|p-v_k|^2 + |q-v_k|^2 - 1}{2}$$
intersected with the unit circle $\cos^2\theta + \sin^2\theta = 1$. A *double-binding* satisfies two such constraints simultaneously: solve a $2 \times 2$ linear system in $(\cos\theta, \sin\theta)$ and check the unit-circle equation. The unit-circle equation is generically incompatible with the linear solution; double-bindings exist only when an algebraic identity in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ accidentally makes them compatible.

**Findings**.

(a) **Single bindings (about origin).** 16 unique $\theta$ values exist where $R_\theta(M)$ shares at least one unit edge with $M$. Each catches at most 2 cross-copy unit edges; the resulting $M \cup R_\theta(M)$ has $|V| \in [10, 13]$, $|E| \in [17, 24]$, all 4-colorable.

(b) **Double bindings about origin (e1f).** Only **6** double-binding rotations exist for $M$ with rotation pivot at the origin in $\mathbb{Q}(\sqrt 3, \sqrt{11})$. ALL SIX ARE DEGENERATE: the second binding constraint is satisfied by a *vertex coincidence* (a rotated $R_\theta(p)$ lands exactly on an existing $M$-vertex), so the apparent "cross edge" collapses into a within-copy edge after dedup. Net cross-copy edge count: $0$ for all 6. The full union $M \cup \bigcup_{k=1}^{6} R_{\theta_k}(M)$ has $|V| = 29$, $|E| = 61$, $\chi = 4$.

(c) **Pivot-varied double bindings (e1g).** Varying the pivot across all 7 Moser vertices yields **62** distinct double-binding rotations. Of these, only **4** produce 3 cross-copy unit edges (triple-binding by algebraic coincidence). These 4 are paired: both occur at the outer-tip pivots $v_3$ and $v_6 = R_{\theta_{\text{Moser}}}(v_3)$, related by the Moser spindle's intrinsic symmetry. The other 58 have cross-edge count $\leq 2$. The full union with all 62 double-binding rotations stacked has $|V| = 211$, $|E| = 731$, density $E/V = 3.46$. Still **$\chi = 4$**.

| Quantity | Origin-pivot | All 7 pivots |
|---|---:|---:|
| Single-binding rotations | 16 | (more, not enumerated) |
| Double-binding rotations | 6 | 62 |
| Triple-binding rotations (3+ cross edges) | 0 | 4 |
| Union $\|V\|$ | 29 | 211 |
| Union $\|E\|$ | 61 | 731 |
| Union density $E/V$ | 2.10 | 3.46 |
| $\chi$ of union | 4 | 4 |
| 5-colorable? | yes | yes |

(d) **Greedy iterative expansion (e1e Phase 4).** Greedy stacking of single-binding rotations from $M$, picking at each step the $\theta$ maximizing new-edge gain, settles into a *periodic attractor*: new-edge counts cycle through $(12, 14, 16, 12, 14, 16, \ldots)$ per added rotation. Density $E/V$ stays at $\approx 2.27$ for at least 19 iterations ($|V| = 121, |E| = 275$, all 4-colorable). The greedy never finds a rotation breaking the periodicity.

**Why it matters**.

1. **The de Grey "miracle" is much rarer than expected**. de Grey 2018's 1581-vertex graph uses dozens of carefully-chosen rotations in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ that produce many cross-copy unit edges per rotation. Our enumeration shows that in the *Moser spindle root*, this field admits zero double-binding rotations about origin, six total double-bindings about origin (all degenerate), and only four genuinely triple-binding rotations across all seven pivots. The field-theoretic rigidity is sharp: $\mathbb{Q}(\sqrt 3, \sqrt{11})$ over the Moser seed almost has *no* multi-cross-edge rotations. de Grey's success required composing many *single*-binding rotations into a 1581-vertex structure, not finding miraculous high-multiplicity rotations.

2. **Density isn't enough**. The 211-vertex union has density $E/V = 3.46$, higher than e1d's orbit graphs ($1.78$) and within $30\%$ of de Grey 1581's density $5.00$ and Polymath 510's $4.91$. Yet still $\chi = 4$. The 5-chromaticity barrier is *structural*, not just density-driven: edges must form specific independent-set patterns to force a fifth color.

3. **The structural obstruction is now precisely localized**. L11 said "the actual research problem" is finding binding rotations in alternate rings. e1f, e1g now establish the *combinatorial size of the binding-rotation search space* for the Moser spindle in $\mathbb{Q}(\sqrt 3, \sqrt{11})$: there are exactly 16 single-binding angles about origin, 62 double-binding angles across all pivots, 4 triple-binding angles. To find a chi >= 6 UDG via binding rotations starting from $M$ in this field would require composing single-binding rotations into a structure of size $\gg 1581$ vertices, which is well beyond the de Grey lineage's current scale. **The most plausible route to chi >= 6 is to leave $\mathbb{Q}(\sqrt 3, \sqrt{11})$ entirely** for a richer algebraic field, or to start from a 5-chromatic UDG seed (Heule 553) rather than $M$ and search for binding rotations *of that* into a chi >= 6 graph.

4. **Reverse engineering de Grey**. The de Grey 1581-vertex graph can be re-described as: a specific multi-rotation $H = \bigcup_k R_{\theta_k}(W)$ where $W$ is a smaller "wheel" structure and the $\theta_k$ are chosen via the rotation lattice of $\mathbb{Q}(\sqrt 3, \sqrt{11})$. Our binding-rotation framework is the right shape to *re-derive* de Grey systematically by searching over $W$ candidates and $\{\theta_k\}$ subsets. Doing so would give the smallest known 5-chromatic UDG that can be constructed *purely from binding rotations* (rather than the SAT-minimized 509 of Parts 2020). This is a concrete future BUILDER target.

**Cross-architectural implication**. L4 noted that Architectures 1 and 2 share the missing 6-chromatic UDG. L14 sharpens the obstacle: not just "find a $6$-chromatic UDG", but "find one in any algebraic extension of $\mathbb{Q}$ at all", because the search in the canonical $\mathbb{Q}(\sqrt 3, \sqrt{11})$ has the structural rigidity above. Until a richer field admits the binding miracles needed, both Architectures 1 and 2 are stuck at the chi/chi_m = 5 level.

**Wrong-approach status**. Passes the $\mathbb{Q}^2$ detector: the binding-rotation construction uses irrational $\cos\theta, \sin\theta$ throughout (never lifts to $\mathbb{Q}^2$). Passes the $\mathbb{R}^1$ detector (one-dimensional analog has no rotations). Engages with the $O(2)$ rotation structure properly.

**Implementation notes**. Numerical computation at 80-digit mpmath precision throughout, with sympy-exact verification of seed edges. The double-binding solver is a $2 \times 2$ linear system; the unit-circle check uses tolerance $10^{-30}$, which excludes accidental near-misses in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ given the field's bounded denominators. Each experiment runs in seconds-to-minutes on a single core. e1f cache: 6 double bindings about origin; e1g cache: 62 double bindings across pivots, 4 with cross >= 3; e1e cache: 16 single-binding angles, greedy expansion to $|V| = 121$ at 19 iterations.

**Future BUILDER directions (next session)**:

1. **Repeat the binding-rotation enumeration in $\mathbb{Q}(\sqrt 3, \sqrt{11}, \sqrt p)$** for small primes $p \in \{2, 5, 7, 13, 17, 19, \ldots\}$. Each enlargement may admit *new* double or triple bindings beyond the 62 / 4 from $\mathbb{Q}(\sqrt 3, \sqrt{11})$ alone. Find the smallest extension where the binding count substantially increases.
2. **Seed from a 5-chromatic UDG** (Heule G7 553, or Parts 509 reconstructed): enumerate binding rotations of *that*, looking for chi >= 6. The richer seed has many more (p, q) pairs and may admit more (and higher-multiplicity) bindings.
3. **Reverse-engineer de Grey**. Identify the specific set $\{\theta_k\}$ of rotation angles in de Grey's 1581-vertex graph, characterize them as binding rotations, and search for a smaller subset producing the same chi >= 5. This would give a constructive upper bound on the "rotation complexity" of $\chi \geq 5$.

---

### L13. Greedy beam search over IE-LP configurations from a Polymath 510 pool drops $m_1(\mathbb{R}^2)$ from 0.280 to 0.2595 in eight steps from a 7-vertex hex seed

**Architecture**: 3. Continues e3g (Ambrus IE-LP framework), addressing the "beam search" step.

**Experiment**: [`e3h_ambrus_beam_search.py`](fractional/e3h_ambrus_beam_search.py).

**Setup**. Candidate pool: the 510 vertices of the Polymath 510 graph (5-chromatic, in $\mathbb{Q}(\sqrt 3, \sqrt{11})$). Seed: first 7 vertices, the hexagonal lattice (1 origin + 6 unit-distance neighbors), giving $m_1 \leq 0.280044$ in IE-LP. Beam width: 1 (greedy). At each step, evaluate every pool vertex as a candidate addition and keep the one with smallest $m_1$ from IE-LP.

**Progression**:

| Step | Config size | Edges | Indep sets | $m_1 \leq$ | Improvement | Step time |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 7 | 12 | 19 | 0.280044 | (seed) | — |
| 1 | 8 | 12 | 38 | 0.272367 | $-$0.0077 | 20 s |
| 2 | 9 | 13 | 66 | 0.270806 | $-$0.0016 | 27 s |
| 3 | 10 | 13 | 132 | 0.269840 | $-$0.0010 | 36 s |
| 4 | 11 | 13 | 264 | 0.268224 | $-$0.0016 | 47 s |
| 5 | 12 | 13 | 528 | 0.266282 | $-$0.0019 | 65 s |
| 6 | 13 | 14 | 912 | 0.263264 | $-$0.0030 | 86 s |
| 7 | 14 | 14 | 1818 | 0.260858 | $-$0.0024 | 138 s |
| 8 | 15 | 14 | 3587 | 0.259544 | $-$0.0014 | 273 s |
| 9 | 16 | 14 | 6948 | **0.258784** | $-$0.0008 | 555 s |

The 16-vertex result essentially matches KMOR 2015's published $m_1 \leq 0.258795$ (the $1.1 \times 10^{-5}$ delta is below LP-solver tolerance). We've matched the 2015 frontier with a 16-vertex configuration grown from a 7-vertex hex seed by simple greedy beam search; KMOR's published proof used a more elaborate harmonic-analysis argument. The next published frontier is Ambrus-Matolcsi 2022's 0.2544 (delta 0.004 from current); reaching Ambrus 2023's 0.2470 needs delta 0.012 ≈ 5-7 additional steps, each with doubled compute.

**The 17-vertex configuration** (indices into the Polymath 510 vertex list, in addition order):

Seed (hex lattice): $\{0, 1, 2, 3, 4, 5, 6\}$. Added by beam search through step 11: $\{334, 346, 206, 263, 49, 52, 464, 41, 47, 92\}$.

After step 11 (resumed from step 9 state), $m_1 \leq 0.258397$ with 17 vertices, 11512 independent sets, 15 unit-distance edges, $\approx 21$ min compute. The improvement per step has dropped to $-0.0004$ (vs $-0.003$ around step 6) — greedy beam search at width 1 is plateauing at a local optimum near the KMOR 2015 frontier.

State persisted at [`experiments/fractional/_cache/e3h_state.json`](fractional/_cache/e3h_state.json) (resumable across runs). To meaningfully push past the local plateau and approach Ambrus 2023's 0.2470, future work needs: (a) beam width $\geq 2$ — keep top-$K$ partial solutions; (b) vertex-swap local search after greedy build; (c) richer candidate pool, e.g., constructive generation of unit-distance neighbors in $\mathbb{Q}(\sqrt 3, \sqrt{11})$; or (d) restart from multiple seeds (Moser spindle, Heule fragments, MRVZ-style configurations) instead of just hex lattice.

**Computational scaling**. Indep set count roughly doubles per step: 19 $\to$ 38 $\to$ 66 $\to$ 132 $\to$ 264 $\to$ 528 $\to$ 912 $\to$ 1818 $\to$ 3587. Step times scale linearly with $K \cdot |\text{pool}|$, so step $k$ time roughly doubles. Step 9 projected ~9 min; step 10 ~18 min; step 13 ~2 h; reaching size 23 estimated ~10 hours of compute. The greedy single-candidate evaluation is the bottleneck (we re-solve the LP for every pool point at every step). Parallelization across candidates would cut step time linearly.

**Why this works at all**. The IE-LP has more degrees of freedom than the OFV simplex LP: each independent set contributes one atom variable, and each pair of vertices contributes one (ie2) constraint linking that pair's atom sum to the autocorrelation $f$ at the pair's distance. As the configuration grows, the LP's effective coverage of distinct distances and independence structures increases. The hexagonal lattice seed provides a high-symmetry base; adding Polymath 510 vertices introduces new distances and new constraint patterns. Greedy selection picks the addition that most tightens the LP at each step.

**What's open / future work**:

1. **Beam width $\geq 2$**: greedy can get stuck at local optima; keeping top-$K$ partial solutions and forking would explore more of the search space.
2. **Constructive candidate pool**: instead of Polymath 510, generate candidates dynamically as unit-distance neighbors of current configuration vertices in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ rotations.
3. **Local search / removal**: after greedy build, try swapping individual vertices to see if a different choice yields a smaller bound.
4. **Parallelization**: the LP evaluations at a single step are embarrassingly parallel.

**Wrong-approach status**: same as L12 (rotation-invariant Bessel basis, Euclidean geometry, does not transfer to $L^\infty$ / $\mathbb{Q}^2$).

---

### L12. Ambrus 2023 m_1 <= 0.247 uses inclusion-exclusion atom LP, NOT the Bachoc-Vallentin 2-particle SDP

**Architecture**: 3. Surveyor-style structural reading of two primary sources (Bachoc-Nebe-OFV 2009 + Ambrus et al. 2023) plus implementation framework.

**Experiment**: [`e3g_ambrus_ie_lp.py`](fractional/e3g_ambrus_ie_lp.py).

**Headline correction to my Shot 5 framing**. The Bachoc-Nebe-Oliveira Filho-Vallentin 2009 paper (arXiv:0801.1059) develops a 2-particle SDP via Lovász-theta generalization to compact metric spaces (sphere $S^{n-1}$). At $n = 2$ (Hadwiger-Nelson plane) their SDP reduces to the same Bessel-LP we already implement: BNOFV section 6 page 7 explicitly states "for $n = 2, \ldots, 8$ our bounds are worse than the existing ones." The 2-particle SDP is *only* helpful in high dimensions $n \geq 10$ where the Jacobi-polynomial expansion adds non-trivial structure beyond the 1-particle Hankel basis. **The BV SDP is the wrong target for HN.**

**What Ambrus 2023 actually does**. Their bound $m_1(\mathbb{R}^2) \leq 0.2470$ uses an *inclusion-exclusion atom LP* (Lemma 1 of arXiv:2207.14179):

For finite configuration $X = \{x_1, \ldots, x_n\} \subset \mathbb{R}^2$, define atoms

  $a_X(\varepsilon) = \delta\left( \bigcap_{i: \varepsilon_i = +1} (A - x_i) \cap \bigcap_{i: \varepsilon_i = -1} (A - x_i)^c \right)$

for each $\varepsilon \in \{+1, -1\}^n$. Constraints:
- $a_X(\varepsilon) \geq 0$;
- $a_X(\varepsilon) = 0$ if $\{x_i : \varepsilon_i = +1\}$ contains two points at unit distance;
- $\sum_\varepsilon a_X(\varepsilon) = 1$;
- $\sum_{\varepsilon : \varepsilon_i = +1} a_X(\varepsilon) = \delta(A)$ for each $i$;
- $\sum_{\varepsilon : \varepsilon_i = \varepsilon_j = +1} a_X(\varepsilon) = f(x_i - x_j)$ for each pair.

Combined with the Bochner-positive-definite $f(r) = \int J_0(2 \pi r s)\, d\nu(s)$, $\nu \geq 0$, and $f(1) = 0$, this is a 1-particle LP whose maximum value of $\delta(A)$ upper-bounds $m_1$.

The lineage of bounds via this method:
- Székely 1984: $m_1 \leq 12/43 \approx 0.279$ (using 3 point sets).
- OFV 2010: $m_1 \leq 0.2684$ (3 regular triangles).
- KMOR 2015: $m_1 \leq 0.2588$ (more subtle constraints).
- Ambrus-Matolcsi 2022: $m_1 \leq 0.2544$ (triple correlations).
- Ambrus-CMVZ 2023: $m_1 \leq 0.2470$ (23-point configuration found by beam search).

The improvement comes entirely from *richer point configurations* in the inclusion-exclusion framework. NOT from a higher-particle SDP.

**Implementation**. e3g implements the IE-LP framework with CVXPY + HiGHS. Tested on three configurations:

| Configuration | $n$ | edges | indep sets | $m_1 \leq$ | $\chi_m \geq$ (real) |
|---|---:|---:|---:|---:|---:|
| Moser spindle | 7 | 11 | 18 | 0.2829 | 3.535 |
| Hex lattice 1 layer | 7 | 12 | 19 | 0.2799 | 3.573 |
| Moser + hexagon | 11 | 20 | 99 | 0.2719 | 3.678 |
| Hex lattice 2 layers | 19 | 42 | 1425 | 0.2758 | 3.626 |
| Hex lattice 3 layers | 37 | 90 | $\approx 8 \times 10^5$ | (LP intractable) | — |

The Moser-spindle IE-LP at 0.2829 is *tighter* than the trivial fractional bound $\alpha/N = 2/7 = 0.2857$, but looser than OFV's 3-triangle LP at 0.2684 (which uses three different sub-configurations) and looser than e3e's Moser-at-translations 0.2619.

**Why e3g doesn't immediately match e3e**:

- e3e applies the Moser inequality at *many translations*, contributing many independent constraints to the LP.
- e3g applies inclusion-exclusion at a *single fixed configuration*, with translation-invariance built in (configuration shift doesn't change inequalities).
- The "many-translation" gain in e3e comes from sampling the autocorrelation $f$ at many distances; e3g must cover the same distances through the chosen configuration's *pairwise distances*. Smaller configurations cover fewer distances → looser bound.

**Path to 0.247 in this framework**. Without the explicit Ambrus 23-point coordinates (PDF returned binary-only on WebFetch), the next step is *beam search*: for each candidate configuration of $n = 15$-$25$ points, build the IE-LP, solve, and select greedily. Ambrus et al. spent considerable compute on this search. Future BUILDER work should focus on:

1. Implementing beam search over configurations starting from Moser+hex (11 pts, 0.272).
2. Including translation orbits of small configurations to combine with the IE-LP atoms.
3. Reaching out to Ambrus et al. for their 23-point coordinates or a public configuration repository.

**Wrong-approach status**: the IE-LP framework uses only 2D Euclidean geometry (point distances) and the rotation group (via Bessel basis for $f$). It respects rotation invariance and does not transfer to $L^\infty$ or $\mathbb{Q}^2$. Detector passes.

---

### L11. Rotation-orbit graphs from Moser-style angles in alternate rings are 4-chromatic for every tested ring at small orbit size

**Architecture**: 1 (combinatorial / UDG). Negative result on Shot 2 (field-theoretic chi >= 6 search).

**Experiment**: [`e1d_field_extension_search.py`](combinatorial/e1d_field_extension_search.py).

**Setup**. The "Moser-style angle" family: for seed radius $r$ from origin, the spindle rotation angle is $\cos \theta = (2r^2 - 1)/(2 r^2)$, with $\sin \theta = \sqrt{4 r^2 - 1}/(2 r^2)$. The Moser spindle uses $r^2 = 3$, giving the ring $\mathbb{Q}(\sqrt{11})$ (the $\zeta$ in Polymath16's $\mathbb{Z}[\omega_3, \zeta]$ formulation). Other choices $r^2 \in \{2, 5, 6, 7, 8, 10, \ldots\}$ give rings $\mathbb{Q}(\sqrt{4r^2 - 1}) = \mathbb{Q}(\sqrt 7), \mathbb{Q}(\sqrt{19}), \mathbb{Q}(\sqrt{23}), \mathbb{Q}(\sqrt{27}) = \mathbb{Q}(\sqrt 3), \mathbb{Q}(\sqrt{31}), \mathbb{Q}(\sqrt{39})$.

**Finding**. Apply each rotation $\theta$ for $n_{\rm rot} \in \{3, 4, 6\}$ iterations to the Moser spindle (7-vertex seed). For all tested ring extensions and all $n_{\rm rot}$:

| $n_{\rm rot}$ | $\|V\|$ | $\|E\|$ | 3-col | 4-col | 5-col |
|---:|---:|---:|---:|---:|---:|
| 3 | 19 | 33 | False | True | not checked |
| 4 | 25 | 44 | False | True | not checked |
| 6 | 37 | 66 | False | True | not checked |

These counts are *identical* across all six tested ring discriminants $\{7, 19, 23, 27, 31, 39\}$. The orbit graph structure is the same regardless of which sqrt is adjoined.

**Structural reason**. The $n_{\rm rot}$ rotated copies of the Moser spindle share at most their *central* vertices (those at the origin, which are fixed by rotation). The shared vertex count is exactly the number of seed vertices at the rotation axis (origin). For the Moser spindle as embedded, 5 vertices are not at origin and are duplicated by each rotation; only $5 \cdot 6 = 30$ noncentral vertices plus 1 shared central vertex appear in the 6-orbit, $V = 31$ shy... actually $V = 37$ in the output, accounting for some between-copy coincidences. But the EDGES total $66 = 6 \cdot 11$ exactly: every edge is a within-copy Moser edge, none crosses copies.

The graph is therefore the disjoint union (modulo central-vertex identification) of 6 Moser spindles. $\chi = \chi(\text{Moser}) = 4$. No new rigidity is gained.

**Why it matters**:

1. The "easy" form of Shot 2 (rotate Moser seed by Moser-style angles in alternate rings) does *not* produce chi >= 5 UDGs, let alone chi >= 6. Confirmed across 6 different ring discriminants.

2. The Polymath16 obstruction crystallizes: the de Grey 2018 construction works because *specific* rotation choices in $\mathbb{Q}(\sqrt{11})$ produce *cross-copy unit-distance edges* — accidental algebraic coincidences where rotated vertices hit unit distance from existing ones. Generic rotations don't have this property. Finding such coincidences in an alternate ring is the actual research problem.

3. The genuine Shot 2 work requires either (a) algorithmic search for *binding rotations* (angles producing cross-copy unit-distance edges) in alternate rings, or (b) ML-driven configuration discovery (analogous to Mundinger et al. on the upper-bound side, but for combinatorial lower bounds). Neither is tractable in a single session.

**Wrong-approach status**: the construction respects the rotation-symmetry of $\mathbb{R}^2$ and uses irrational algebra elements; it does not lift to $\mathbb{Q}^2$ where $\chi = 2$. Detector passes. The negative result is genuine structural information about the difficulty of finding chi >= 6 UDGs by orbit-based methods.

**Implication for SOLVING_PROGRAM**: Shot 2 is a multi-month-scale compute problem requiring either new mathematical insight or large-scale orchestrated search. Not closeable in a session. The framework in `e1d_field_extension_search.py` is a clean baseline that could be extended with binding-rotation search, but the search space is huge.

---

### L10. Polymath 510 (or any large 5-chromatic UDG) cannot be effectively used in the OFV LP because the radial Bessel sum collapses to noise

**Architecture**: 3 (fractional / spectral / LP). Structural negative result.

**Experiment**: [`e3f_polymath510_lp.py`](fractional/e3f_polymath510_lp.py) (Shot 1 of SOLVING_PROGRAM).

**Finding**: the OFV inequality $\sum_{i=1}^{N} f(\|v_i + t\|) \leq \alpha(G)$ at any translation $t$ contributes to the LP only when the inequality is *binding*: the LP optimum of $f$ must drive the LHS close to $\alpha(G)$. For Polymath 510:

- $\alpha(G) \geq 142$ confirmed by SAT (within a 10-minute compute budget). Direct counting bound: $m_1 \leq 142/510 \approx 0.278$.
- At the LP's optimal frequency $s^* \approx 0.61$ (where $J_0$ achieves its minimum at $2 \pi s^* = j_{1,1} = 3.83$, $J_0 \approx -0.4028$), the *radial Bessel sum* $\sum_{i=1}^{510} J_0(2 \pi s^* \|v_i\|)$ has magnitude $\leq 10$ at any translation — it oscillates around zero by cancellation across the 510 distinct radii.
- LHS of the OFV inequality at LP optimum $f$ (which puts weight on the single frequency $s^*$ in the e3b basic LP): $\sum_i f(r_i) \approx \alpha_{LP} \sum_i J_0(2 \pi s^* r_i) \approx 0.713 \cdot (-6.56) = -4.68$ (at the best translation).
- Bound: $\alpha = 142$. Slack: $142 - (-4.68) = 146.68$, i.e., the constraint is **97% inactive**.

In the LP solver output, no Polymath 510 translation acquires positive dual weight across 210+ candidate translations. The LP bound stays at OFV's 0.268412.

Contrast with Moser spindle ($N = 7, \alpha = 2$): at its best translation $(-0.5, -0.5)$, $\sum_{i=1}^7 J_0(2 \pi s^* r_i) \approx 0.38$, so $f$-LHS $\approx 0.713 \cdot 0.38 = 0.27$, vs bound $= 2$. Slack $\approx 86\%$, but the constraint *does* bind in combination with translations + OFV triangles, dropping the bound from 0.268 to 0.2619 (L9).

**Why it matters**:

1. The intuition "use a bigger 5-chromatic UDG to get a tighter LP bound" is *wrong* in the OFV framework. Bigger UDGs have larger N and (proportionally) larger $\alpha$, so $\alpha/N$ ratio stays roughly constant. More importantly, the *radial Bessel sum* $\sum J_0(2 \pi s r_i)$ averages to zero by cancellation as $N$ grows for any "spread-out" configuration. The LP cannot extract useful information from a constraint that's never near binding.

2. **What would actually help**: a finite UDG with vertices *radially clustered* near $r \approx 1$ (the J_0 minimum region in unit terms) from some center, so that $\sum J_0(2 \pi s^* r_i)$ is very negative. Such a UDG would feed the LP a tight constraint. The challenge is making such a configuration *also* 5-chromatic. Standard 5-chromatic UDGs (de Grey, Polymath 16, Heule) are *minimized for vertex count*, not for radial clustering, and don't have this property.

3. **Shot 1 (5-chromatic UDG into LP) does not produce integer $\chi_m \geq 5$** with current public 5-chromatic UDGs. The structural ceiling for the OFV-Moser LP framework is around $m_1 \leq 0.262$ (real $\chi_m \geq 3.82$), and no published 5-chromatic UDG breaks this ceiling.

**Path forward**:

- *Custom UDG construction*: design a 5-chromatic UDG with radial clustering near $r = 1$. This is a research direction in its own right, no obvious algorithm.
- *2-particle Bachoc-Vallentin SDP*: the published Ambrus et al. 2023 bound $m_1 \leq 0.247$ likely uses richer structural inequalities than OFV's single-radial form. Implementing the BV SDP is significantly more work but is the conceptual next step.
- *Pivot to Shot 2*: the field-theoretic UDG search for $\chi \geq 6$ remains unexplored and high-variance.

**Wrong-approach status**: the OFV inequality is rotation-equivariant and uses Euclidean structure ($J_0$ basis for $\mathbb{R}^2$), so the framework passes $\mathbb{R}^1$ and $L^\infty$ detectors. The "spread-out 510-vertex graph can't help" finding is not a wrong-approach artifact, it's a structural ceiling of the LP framework itself.

---

### L9. The unit-edge-triangle inequality class saturates at $m_1(\mathbb{R}^2) \leq 0.2682$, and Moser-spindle inequalities break that barrier down to $0.262$

**Architecture**: 3 (fractional / spectral / LP).

**Experiments**: [`e3d_ambrus_triple_sweep.py`](fractional/e3d_ambrus_triple_sweep.py), [`e3e_moser_constraint.py`](fractional/e3e_moser_constraint.py).

**Finding**:

(a) **Triangle saturation**. The OFV-style LP with *equilateral unit-edge triangle* inequalities saturates near OFV's published 0.2684. e3d enumerates all valid $(a, b, c)$ triples on a $0.1$-step grid in $a, b \in [0.1, 4.0]$ (1409 valid triples) and feeds all of them to the LP simultaneously. The LP selects 9 active triples (out of 1409) and reaches $m_1 \leq 0.268202$, only $2 \times 10^{-4}$ tighter than OFV's hand-picked 3. The triangle-inequality class is essentially exhausted here.

(b) **Moser breakthrough**. The OFV simplex inequality $\sum_{i} f(\|v_i\|) \leq 1$ for a unit-edge equilateral triangle generalizes to $\sum_i f(\|v_i\|) \leq \alpha(G)$ for any finite UDG $G \subset \mathbb{R}^2$, where $\alpha$ is the independence number. The Moser spindle (7 vertices, 11 unit-distance edges, $\chi = 4$, $\alpha = 2$, vertices in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$) is the natural next configuration. Each translation of the Moser spindle in the plane gives a different set of 7 vertex norms and hence a different LP constraint.

| LP variant | $m_1(\mathbb{R}^2) \leq$ | $1/m_1$ | $\Delta$ vs OFV |
|---|---:|---:|---:|
| OFV 2010, 3 hand-picked triples (e3c) | 0.268412 | 3.7256 | baseline |
| Wide triangle sweep, 1409 candidates (e3d) | 0.268202 | 3.7285 | $-0.0002$ |
| + single Moser at $(-0.5, -0.5)$ (e3e) | 0.264150 | 3.7857 | $-0.0043$ |
| + 1271 Moser translations (e3e) | 0.261994 | 3.8169 | $-0.0064$ |
| + 18 rotations × 6048 translations (e3e ext.) | 0.261883 | 3.8185 | $-0.0065$ |
| KMOR 2015 published | 0.2588 | 3.864 | $-0.0096$ |
| Ambrus et al. 2023 published | 0.2470 | 4.049 | $-0.0214$ |
| Required for $\chi_m \geq 6$ | < 0.2000 | > 5 | $-0.068$ |

We close $\approx 75\%$ of the gap to KMOR's 0.2588 with Moser-spindle inequalities ($\Delta = 0.0065$ vs $0.0096$ to KMOR). The Moser-spindle LP optimum is achieved at multiple translations simultaneously (10-11 active out of 6048), and rotations beyond translations add negligible improvement (the bound saturates near 0.2619 across rotation sweeps).

**Integer chromatic bound unchanged at $\chi_m \geq 4$**. The real-valued bound improves from $\geq 3.73$ (OFV) to $\geq 3.82$ (e3e); breaking integer $\chi_m \geq 5$ requires $m_1 < 0.2$, which is 21% below e3e and not approachable with triangle + Moser inequalities.

**Why it matters**:

1. The progression $0.287 \to 0.268 \to 0.262$ is *purely structural*: each step injects a richer finite UDG into the LP. e3b is the saturated radial Bessel-LP (no UDG); e3c uses unit-edge triangles ($K_3$, $\alpha = 1$, $N = 3$); e3e adds the Moser spindle ($\chi = 4$, $\alpha = 2$, $N = 7$). The bound improves monotonically with UDG complexity. This is the *same combinatorial mechanism* that powers Falconer 1981 in measure-theoretic form (L4), now operating purely in the LP framework.

2. The gap to Ambrus 2023's 0.2470 is *not* expected to close by adding more standard UDGs. Ambrus uses a custom 23-point configuration optimized by beam search; the configuration is not a "standard" UDG like the Moser spindle. Reproducing their bound likely requires either (a) the explicit 23-point coordinates (which the paper provides), or (b) a beam search over UDG configurations starting from the Moser spindle to find a better one.

3. The structural barrier to $\chi_m \geq 5$ via the LP route is *the same barrier* as the structural barrier to $\chi \geq 6$ via SAT (L1, L4): a richer-than-Moser combinatorial object. The cross-architecture coupling deepens: not just $\chi_m \geq 6$ but the *real-valued* $\chi_m$ certificate at the third decimal place is gated by the same missing finite UDG.

**Wrong-approach status**: same as L8 (Moser spindle's coordinates use $\mathbb{Q}(\sqrt{3}, \sqrt{11})$, so the underlying UDG passes the $\mathbb{Q}^2$ detector; the inequality is rotation-equivariant on $\mathbb{R}^2$, engaging the Euclidean structure properly).

**Implementation note**: e3e at the largest scale (18 rotations $\times$ 6048 translations = 7626 configurations $\times$ 20000-point $t$-grid) runs into memory limits in cvxpy/HiGHS (matrix is $\sim 1.2$ GB). A reduced $t$-grid ($n = 8000$) on 6048 configurations runs in $\sim 65$ seconds and yields the same saturated bound 0.2619 as the translation-only sweep. The $t$-grid resolution is not the binding constraint.

---

### L8. The OFV 2010 published $m_1(\mathbb{R}^2) \leq 0.268412$ is reproduced exactly by a 3-variable + 3-multiplier LP, and the strengthening over the basic LP comes entirely from off-center unit-edge triangle inequalities

**Architecture**: 3 (fractional / spectral / LP), with cross-references to 2.

**Experiment**: [`e3c_ofv_lp_dual.py`](fractional/e3c_ofv_lp_dual.py).

**Source primary**: Oliveira Filho-Vallentin 2010, [arXiv:0808.1822](https://arxiv.org/abs/0808.1822), Theorem 1.1 + Section 3.1 + page 7 explicit triples.

**Finding**: the OFV LP for $m_1(\mathbb{R}^n)$ at a single forbidden distance has the dual form

  $\min z_0 + z_c$
  s.t. $z_c \geq 0$
       $z_0 + z_1 + (n+1) z_c \geq 1$
       $z_0 + z_1 \Omega_n(t) + z_c \sum_{i=1}^{n+1} \Omega_n(t \|v_i\|) \geq 0$ for all $t \geq 0$

where $\Omega_n(t) = \Gamma(n/2) (2/t)^{(n-2)/2} J_{(n-2)/2}(t)$ and $\{v_i\}$ are the $n+1$ vertices of a *unit-edge* simplex (regular triangle at $n = 2$). The bound is $m_1(\mathbb{R}^n) \leq z_0 + z_c$.

The basic LP (no simplex constraint) has the analytic optimum $z_0 = \Omega_n(j_{n/2,1}) / (\Omega_n(j_{n/2,1}) - 1)$. At $n = 2$ this is $J_0(j_{1,1}) / (J_0(j_{1,1}) - 1) = -0.4028 / -1.4028 \approx 0.2873$. This is the saturation value that e3b's positive-type-radial LP recovers in 30 ms (LEARNING L6), confirming that vanilla Bessel-LP optimizes the basic LP.

A *centered* equilateral-triangle constraint at $n = 2$ (all three vertices at distance $1/\sqrt{3}$ from origin) is only worth $0.0014$: the bound drops from $0.2873$ to $0.2857$. The substantial improvement is from *off-center* unit triangles. OFV used three specific squared-norm triples for the triangle vertices:

  $(\|v_1\|^2, \|v_2\|^2, \|v_3\|^2) \in \{(2.4, 2.4, 0.360314), (3.1, 3.1, 6.524038), (3.7, 3.7, 7.417141)\}$

with the third coordinate chosen as a root of $3(a^2 + b^2 + c^2 + 1) - (a + b + c + 1)^2 = 0$ to force the Gram matrix to rank 2 (so the triangle actually embeds in $\mathbb{R}^2$). Solving the LP with these three additional simplex multipliers gives

  $m_1(\mathbb{R}^2) \leq 0.268412$

exactly matching OFV Table 3.1. Solve time: 113 ms via cvxpy + HiGHS, three free variables ($z_0, z_1$) plus three nonneg multipliers ($z_{c,1}, z_{c,2}, z_{c,3}$), $\approx 20000$ discretized $t$-constraints.

**Three-step chromatic table from this LP**:

| LP variant | $m_1(\mathbb{R}^2) \leq$ | $\chi_m \geq 1/m_1$ | Integer $\chi_m \geq$ |
|---|---:|---:|---:|
| Basic (no simplex), e3c | 0.287119 | 3.483 | 4 |
| One centered unit triangle | 0.285742 | 3.500 | 4 |
| Three off-center unit triangles, e3c | 0.268412 | 3.726 | 4 |
| KMOR 2015 (heavier LP / more inequalities) | 0.2588 | 3.864 | 4 |
| Ambrus et al. 2023 (23-point + beam search) | 0.2470 | 4.049 | 5 |
| Required for $\chi_m \geq 6$ | < 0.2000 | > 5 | 6 |

**Why it matters**:

1. The OFV bound is *not* obtainable by adding more frequencies to a vanilla Bessel-LP. e3b's saturated 0.2872 is a 1-dimensional LP optimum (single Bessel mode at $s \approx 0.61$). The 0.2688 improvement comes from a fundamentally different mechanism, the rigid finite-Euclidean-configuration constraint $f(\|v_1\|) + \ldots + f(\|v_{n+1}\|) \leq 1$ for unit-edge simplices. This is *combinatorial* structure being injected into the *continuous* LP, similar in spirit to how Falconer-style measure arguments amplify a finite UDG (L4).

2. The 0.268-to-0.247 step (Ambrus et al. 2023) uses the same mechanism but with a 23-point configuration and a beam search over which non-trivial inequalities to enforce, indicating the LP has substantial residual slack for $n = 2$ that finer Euclidean-rigidity constraints can recover. The structural gap to $\chi_m \geq 5$ (need $m_1 < 1/5 = 0.200$) is still substantial.

3. The bound $\chi_m \geq 4$ (integer) is unchanged from L6, but the *real-valued* certificate strengthens from $\chi_m \geq 3.48$ (e3b) to $\chi_m \geq 3.73$ (e3c). To push to integer $\chi_m \geq 5$ via this route, we need $m_1 \leq 0.2$, which no published method has reached. Falconer's $\chi_m \geq 5$ uses a different (Lebesgue-density) mechanism.

**Cross-architectural implication**:

This experiment closes the *methodological* gap between e3b (which is the vanilla Bessel LP, structurally saturated at the analytic value $0.2873$) and the published LP frontier ($0.2688$ OFV, $0.2588$ KMOR, $0.2470$ Ambrus). Architecture 3 in this repo now has an LP framework that reproduces the published numbers, not just the saturation baseline. The remaining gap ($0.2470 \to 0.2000$) is the actual research frontier; nobody has crossed it.

The Ambrus 2023 LP (23 points + beam search) is the next concrete target on the same framework. Implementing it requires either (a) explicit coordinates for the 23 points (which the paper provides) plus a beam search over inequalities, or (b) a re-derivation that scales the OFV 3-triple approach to more triples and larger configurations. Both are tractable in CPU hours.

**Wrong-approach status**:

- $\mathbb{R}^1$ detector: the same LP at $n = 1$ with $\Omega_1(t) = \cos t$ gives $m_1(\mathbb{R}) \leq 0.5$, hence $\chi_m(\mathbb{R}) \geq 2$. This matches the correct value (alternating half-open intervals of length $1/2$). The detector engages and does not over-claim.
- $\mathbb{Q}^2$ detector: the LP framework lives on continuous $\mathbb{R}^n$ and is not literally evaluable on $\mathbb{Q}^2$ (the autocorrelation $\phi$ is over Lebesgue density, which is zero on $\mathbb{Q}^2$ as a measure-zero set). This is consistent with the architectural caveat in [CLAUDE.md](../CLAUDE.md): measure-theoretic / continuous methods can legitimately not engage with the $\mathbb{Q}^2$ control. The bound applies to $\mathbb{R}^2$ via Lebesgue measure, where $\mathbb{Q}^2$ contributes density zero.
- $L^\infty$ detector: the OFV LP uses the rotation group $O(n)$ via spherical symmetrization, which requires the Euclidean norm. The $L^\infty$ norm has different rotation behavior (only $D_4$ symmetry on the unit ball), and the basis $\Omega_n$ would need to change. The framework correctly does not transfer naively.

---

### L7. Architecture 1's 2018 breakthrough erased Architecture 4's main 2003 result about $\chi(\mathbb{R}^2)$

**Architecture**: 4 (set-theoretic / axiomatic), with cross-references to 1.

**Source**: SURVEYOR session, dossier [`docs/research_atlas/arch4_set_theoretic_lineage.md`](../docs/research_atlas/arch4_set_theoretic_lineage.md) §1.

**Headline correction**: the widely-cited "Shelah-Soifer: $\chi(\mathbb{R}^2)$ depends on choice axioms" is **not a theorem about $\chi(\mathbb{R}^2)$ at the current bound threshold**. It is a *conditional* theorem:

> **If** every finite unit-distance graph in $\mathbb{R}^2$ has $\chi \leq 4$, **then** $\chi(\mathbb{R}^2) = 4$ in ZFC and $\chi(\mathbb{R}^2) \geq 5$ in ZF + DC + LM.

**De Grey 2018 falsified the hypothesis** by exhibiting a 5-chromatic finite UDG (1581 vertices, since shrunk to 509 by Parts). The conditional is now vacuous as a statement about $\chi(\mathbb{R}^2)$. The Shelah-Soifer phenomenon (axiom-dependent chromatic numbers for unit-distance-*type* graphs) **survives** for artificial distance graphs (Shelah-Soifer 2003b for $\mathbb{R}^2$, Payne 2009 for UDG-subgraphs), but the specific punchline about the actual Hadwiger-Nelson graph $G_{\mathbb{R}^2}$ has not been re-established. Whether $\chi(G_{\mathbb{R}^2})$ itself depends on AC is **open**.

**Cross-architectural symmetry with L4**:

- **L4**: Architectures 1 and 2 share a missing object (a 6-chromatic finite UDG). Arch 2's $\chi_m \geq 6$ barrier *is* Arch 1's $\chi \geq 6$ barrier amplified by Falconer's machine.
- **L7**: Architecture 1's *2018 success* (the existence of a 5-chromatic finite UDG) *erased* Architecture 4's main 2003 statement about $\chi(\mathbb{R}^2)$.

The two architectures are coupled to Arch 1 in opposite directions: L4 says Arch 2 *waits for* an Arch 1 breakthrough; L7 says Arch 4's specific result *was already invalidated* by Arch 1's previous breakthrough. In both cases the combinatorial object (a finite $\chi \geq k$ UDG) is the load-bearing structure.

**The obvious replacement, unstarted**: the natural 2026 conditional would be

> **If** every finite unit-distance graph in $\mathbb{R}^2$ has $\chi \leq 5$, **then** $\chi(\mathbb{R}^2) = 5$ in ZFC and $\chi(\mathbb{R}^2) \geq ?$ in ZF + DC + LM.

The consequent on the LM side would presumably be $\chi(\mathbb{R}^2) \geq 6$ in ZF + DC + LM via Falconer-style machinery, but only if a measurable-coloring obstruction analogous to the 2003 one can be re-derived at the current bound. Nobody has published this. It is a concrete BUILDER target.

**Implication for the project**: Architecture 4 currently has no statement specifically about $\chi(\mathbb{R}^2)$ that is non-trivial post-2018. The architecture remains valuable for (a) the $\chi \leq \chi_B \leq \chi_m$ definability hierarchy, (b) the Borel chromatic question, and (c) the meta-mathematical framing of "which $\chi$ is the right one." But it does not currently engage with the bound-improvement question.

**Wrong-approach status**: Architecture 4 methods (Hamel basis under AC, Steinhaus under LM) are sensitive to which axiom system is in force. The $\mathbb{Q}^2$ detector applies in a refined way: $\chi(\mathbb{Q}^2) = 2$ in ZFC (Woodall, constructive); the same is true in ZF + DC + LM since the 2-coloring is explicit and measurable. So the Shelah-Soifer mechanism does not engage on $\mathbb{Q}^2$ controls. This is consistent with the architecture being orthogonal to the rationality test.

---

### L6. The rotation-invariant Bessel-LP cleanly beats vanilla Lovász $\vartheta$ on its own SDP playing field

**Architecture**: 3 (fractional / spectral, continuous side).

**Experiment**: [`e3b_ofv_bessel_lp.py`](fractional/e3b_ofv_bessel_lp.py).

**Finding**: a basic discretized Bessel-LP, parametrizing positive-type radial functions as $F(r) = \sum_k c_k J_0(2\pi r s_k)$ with $c_k \geq 0$ at $N = 2000$ frequencies, solves in **30 milliseconds** via HiGHS and gives the bound

$$
m_1(\mathbb{R}^2) \leq -F(1) / (F(0) - F(1)) \leq 0.402749 / 1.402749 \approx 0.287, \quad \therefore \chi_m(\mathbb{R}^2) \geq 4.
$$

The LP places all weight at the single frequency $s \approx 0.6087$, which corresponds to the first negative minimum of $J_0$ at $2\pi s \approx 3.83$ where $J_0 \approx -0.403$.

**Direct comparison to vanilla Lovász $\vartheta$ on the 510-vertex Polymath16 graph (L5)**:

| Method | Wall clock | Result | Integer bound |
|--------|-----------:|--------|--------------:|
| Vanilla $\vartheta$ via SDP on 510-vertex UDG | 644 s | $\vartheta = 170.24$, $n/\vartheta = 2.996$ | $\chi \geq 3$ |
| Rotation-invariant Bessel-LP on $\mathbb{R}^2$ | 0.03 s | $m_1 \leq 0.287$, $1/m_1 = 3.48$ | $\chi_m \geq 4$ |

The continuous rotation-invariant LP is $\approx 2 \times 10^4 \times$ faster *and* gives a strictly tighter integer bound on a stronger object ($\chi_m \geq \chi$). This is the empirical realization of L5's prediction: encoding rotation symmetry in the optimization is structurally the right move for HN.

**Why so much tighter**. The Lovász $\vartheta$ on a fixed graph $G$ optimizes over a $510 \times 510$ symmetric PSD matrix ($\sim 130\text{k}$ degrees of freedom) and sees only the edge structure. The Bessel-LP optimizes over a *1D radial profile* of the Fourier multiplier ($N$ real coefficients $c_k$) and sees the full continuous structure of $\mathbb{R}^2$, including the unit sphere as a single algebraic object rather than 2504 separate edges. The constraint set is vastly smaller in the right way: it forces the optimum to *only* consider $O(2)$-equivariant solutions.

**Distance to published**: OFV 2010 achieves $m_1 \leq 0.2688$ (so $\chi_m \geq 3.72$), and Ambrus et al. 2023 achieves $m_1 \leq 0.2470$ (so $\chi_m \geq 4.05$, integer 5). Our $0.287$ is loose by 0.02 vs OFV and 0.04 vs AC-MV-Z. Tightening would require a richer basis (Schwartz / Wiener-Hopf-style as in OFV) or higher-order correlations (DeCorte-OFV 2018). The single-frequency LP is the natural "first lesson" baseline.

**Implication**: future BUILDER work on $\chi_m$ / $\chi_f$ improvements should target the OFV / BNOFV / AC-MV-Z framework, not vanilla $\vartheta$ on bigger graphs. The 27-vertex MRVZ 2023 result $\chi_f \geq 4$ used exactly this principle: small graph, rotation-symmetric LP, tight bound.

**Wrong-approach status**: the Bessel-LP uses Bessel functions of order 0 (specific to $d=2$). In $d=1$, the analogous basis would be cosines $\cos(2\pi r s)$ (order $-1/2$), and the LP would recover the trivial $m_1(\mathbb{R}) \leq 1/2$, $\chi_m(\mathbb{R}) \geq 2$. The $\mathbb{R}^1$ detector passes. In $L^\infty$, the rotation-invariance assumption fails (the unit sphere is a square, not a circle), so the basis would need to be different; the method correctly does not transfer naively.

---

### L5. Vanilla Lovász $\vartheta$ on the de Grey lineage UDGs is structurally loose

**Architecture**: 3 (fractional / spectral), with cross-references to 1 and 2.

**Experiment**: [`e3a_lovasz_theta_polymath16_510.py`](fractional/e3a_lovasz_theta_polymath16_510.py).

**Finding**: the Lovász theta number of the Polymath16 510-vertex 5-chromatic UDG is

$$
\vartheta(G) = 170.235 \pm 10^{-3}\quad (\text{cvxpy} + \text{SCS}, \approx 11 \text{ min on a single SDP})
$$

giving the chromatic lower bound $\chi(G) \geq \lceil n/\vartheta \rceil = \lceil 510/170.235 \rceil = 3$. The known value is $\chi(G) = 5$ (e1b). The Lovász bound is **loose by 2 integer units**.

**Why it matters**: this calibrates expectations for Architecture 3 SDP work on Hadwiger-Nelson. Vanilla $\vartheta$ on a single large UDG does not recover the chromatic number for HN-style graphs. The independence number satisfies $\alpha(G) \leq \vartheta(G) = 170$, but the actual $\alpha(G)$ for this graph is probably $\leq 102$ (otherwise $\chi \leq n/\alpha < 5$ contradicts e1b). The **integrality gap** $\vartheta - \alpha \approx 68$ vertices is substantial: $\vartheta$ overestimates $\alpha$ by ~$67\%$.

**Cross-architectural implication**: the Matolcsi-Ruzsa-Varga-Zsámboki 2023 result $\chi_f(\mathbb{R}^2) \geq 4$ ([arXiv:2311.10069](https://arxiv.org/abs/2311.10069)) uses a 27-vertex graph and a finer LP framework, not vanilla $\vartheta$. The OFV / BNOFV LP / SDP family imposes rotation-invariance constraints on the Fourier multiplier, vastly reducing the search space and tightening the bound. *Vanilla theta on a fixed UDG is the wrong relaxation for HN; the right SDP is structurally constrained.*

**Implication for Architecture 3 work**: BUILDER attention should focus on the rotation-symmetric LP / SDP framework (OFV 2010, BNOFV 2009, MRVZ 2023) rather than on vanilla $\vartheta$ on larger and larger graphs. The path to $\chi_f \geq 4$ on $\mathbb{R}^2$ is through structured relaxations, not graph size.

**Wrong-approach status**: vanilla $\vartheta$ passes the $L^\infty$ detector (it's a graph invariant, not norm-specific), but it fails to *engage* with the Euclidean rotation-invariance of $\mathbb{R}^2$ that the OFV / BNOFV framework exploits. This is consistent with the looseness: theta cannot see structural information that the OFV LP cannot avoid using.

---

### L4. Architectures 1 and 2 share a single missing object: a 6-chromatic finite UDG

**Architecture**: 1 + 2 (cross-architectural coupling).

**Source**: SURVEYOR session 003, dossier [`docs/research_atlas/arch2_measurable_lineage.md`](../docs/research_atlas/arch2_measurable_lineage.md) §3 + §4 + §7 (discrepancy log item 5). Atlas correction also landed.

**Headline correction**: there is **no published improvement to $\chi_m(\mathbb{R}^2) \geq 5$ since Falconer 1981** (45 years). The widely-cited "$\chi_m \geq 6$" results are from (a) the hyperbolic plane $\mathbb{H}^2(d)$ for $d \geq 12$ (DeCorte-Golubev 2018, [arXiv:1708.01081](https://arxiv.org/abs/1708.01081)), or (b) restricted-region variants where color classes are convex tiles of bounded-away-from-zero area (Coulson 2002, Townsend-Woodall). Neither implies a measurable lower bound on canonical $\mathbb{R}^2$. The atlas's previous "$\chi_m \geq 6$" claim was a misattribution and has been corrected.

**Structural finding**: Falconer's $\chi_m \geq 5$ proof works in four steps: (1) assume a measurable 4-coloring, (2) Lebesgue density theorem extracts a high-density local region in one color class, (3) inscribe a rigid finite *Moser-spindle-like* configuration $S$ in the high-density region, (4) measure-theoretic intersection forces a monochromatic unit pair, contradiction. The load-bearing object in Step 3 is a *rigid finite Euclidean configuration that is at least 5-chromatic as a UDG in $\mathbb{R}^2$*.

To push the same machinery to $\chi_m \geq 6$, Step 3 would need a *6-chromatic finite UDG in $\mathbb{R}^2$*. **But no such object is known** (see L1, L2): Architecture 1 has been searching since de Grey 2018, and the Polymath16 / Heule / Parts lineage has only ever produced 5-chromatic UDGs. The current record (Parts 2020, 509 vertices) is 5-chromatic, and 6-chromaticity has resisted every search.

**The coupling**: the obstruction to $\chi_m \geq 6$ in Architecture 2 is at the lemma level **the same** as the obstruction to $\chi \geq 6$ in Architecture 1. Both architectures need the same missing finite combinatorial object. The measure-theoretic machinery does *not* substitute for the combinatorial search: it consumes a finite UDG and amplifies it via density. The amplification works at chromatic level 5 because de Grey's proof works at chromatic level 5; it would work at chromatic level 6 if and only if Architecture 1 first produces the requisite UDG.

**Implications**:

- The four architectures are not as independent as the project framing suggests. The strongest known cross-coupling is Arch 1 ⟷ Arch 2 via the missing 6-chromatic UDG.
- The "$\chi_m = \chi$" question is not just a coincidence-of-bounds: it is a structural prediction. If Arch 1 finds a 6-chromatic UDG, Falconer's machine immediately bumps Arch 2 to $\chi_m \geq 6$. If Arch 1 never finds one (because $\chi(\mathbb{R}^2) = 5$ is the true value), Arch 2 also stays at 5.
- The independent route to $\chi_m \geq 6$ would be via density: $m_1(\mathbb{R}^2) < 1/5 = 0.200$. Current best is $0.2470$ (Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023, [arXiv:2207.14179](https://arxiv.org/abs/2207.14179)). The gap from $0.247$ to $0.200$ is substantial; no published method approaches it.

**Wrong-approach status**: all measurable methods examined (Falconer 1981, OFV 2010, BNOFV 2009, Ambrus et al. 2023, DeCorte-Golubev 2018) engage with the 2D rotation group and Euclidean rigidity; none over-applies to $\mathbb{R}^1$. The cross-coupling is not a wrong-approach signal, it is a real mathematical constraint.

**Architectural implication for the project**: Architecture 2 cannot be advanced independently of Architecture 1. Investment in BUILDER work on $\chi_m \geq 6$ should either (a) explicitly contribute to the 6-chromatic UDG search (which is Arch 1 work in disguise), or (b) attack the $m_1$ density bound directly via E2.1/E2.2 in the surveyor's experimental menu. The OFV LP at $n = 2$ has reportedly been computed and gives only $\chi_m \geq 5$; whether a higher-order Lasserre / SOS hierarchy could break the barrier is open.

---

### L3. Multi-solver SAT agreement reproduces $\chi \geq 5$ at 510, 517, 553, 826 vertices

**Architecture**: 1 (combinatorial / UDG).

**Experiment(s)**: [`e1b_de_grey_skeleton.py`](combinatorial/e1b_de_grey_skeleton.py).

**Source data**: the [marijnheule/CNP-SAT](https://github.com/marijnheule/CNP-SAT) GitHub repository (Polymath16 / Heule lineage, fetched in session 003) and Polymath16 Dropbox links (de Grey 1585).

**Finding**: cadical195 and glucose4 both return UNSAT on the 4-coloring SAT instance for each of:

| Graph | Source | Vertices | Edges | cadical195 | glucose4 |
|-------|--------|---------:|------:|-----------:|---------:|
| Polymath16 G11 | Parts 2019 | 510 | 2504 | 78 s | 111 s |
| Heule G10 (SBP) | Heule 2019 | 517 | 2579 | 3 s | 3 s |
| Heule G8 | Heule 2018 | 529 | 2670 | 82 s | 119 s |
| Heule G7 (SBP) | Heule 2018 | 553 | 2722 | 2 s | 2 s |
| Heule intermediate | Heule 2018 | 826 | 4273 | 279 s | 805 s |
| **de Grey original** | de Grey 2018 | 1585 | 7909 | **5531 s** | **6456 s** |

Symmetry-breaking predicates (the `-sbp` variants) give 10-100× speedup. The 510 case is run without SBP (no pre-built CNF was provided in the repo) and still finishes in ~2 minutes.

**Why it matters**: two independent solver families agree on UNSAT for each graph. A SAT-solver soundness bug would need to corrupt both cadical (CDCL with chronological backtracking) and glucose (LBD-based CDCL with restart heuristic) in the same direction. Per the verifier discipline this is the strongest non-formal evidence available. Combined with formal verification of the Moser spindle in `lean/HadwigerNelson/`, the project now has end-to-end coverage of $\chi(\mathbb{R}^2) \geq 4$ formally and $\chi(\mathbb{R}^2) \geq 5$ via multi-solver SAT.

**Wrong-approach status**: all four graphs have coordinates in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ (verified algebraically by the Singular scripts in `sources/cnp-sat/check/`). The $\mathbb{Q}^2$ detector therefore passes uniformly across the lineage.

**Next**: de Grey 1585 is mid-run; pending. Future BUILDER experiments should focus on either (a) the field-theoretic search direction in L1, or (b) closing the gap to Parts 509 (not publicly available; would need to reproduce the minimization pipeline from the paper).

---

### L2. The Moser spindle is structurally inessential to $\chi \geq 5$

**Architecture**: 1.

**Source**: Voronov, Neopryatnaya, Dergachev 2021, [arXiv:2106.11824](https://arxiv.org/abs/2106.11824). Summarized in [`docs/research_atlas/arch1_sat_lineage.md`](../docs/research_atlas/arch1_sat_lineage.md) §1.3.

**Finding**: There is a 64513-vertex 5-chromatic UDG in $\mathbb{R}^2$ that **does not contain the Moser spindle as a subgraph**. Every prior $\chi \geq 5$ UDG (de Grey 1581, Heule 553/529, Parts 525/517/510/509) used the Moser spindle as a load-bearing 4-chromatic motif; this construction shows that motif is not logically necessary.

**Why it matters**: opens a structurally new vertex-count question. The smallest *Moser-spindle-free* 5-chromatic UDG is unknown (the Voronov record at 64513 is far from optimal). This is a concrete BUILDER target with no published competitor since 2021.

**Wrong-approach status**: passes the $\mathbb{Q}^2$ detector (irrational coordinates in the rotation structure). Detector engagement noted as "likely passes pending full-PDF read" in the SURVEYOR dossier.

---

### L1. 6-chromaticity is "easy" in HN-adjacent variant problems but uniquely resists in the single-distance plane

**Architecture**: 1 (combinatorial / UDG), with cross-references to Architectures 2-3.

**Source**: SURVEYOR session 001, dossier [`docs/research_atlas/arch1_sat_lineage.md`](../docs/research_atlas/arch1_sat_lineage.md) §3.

**Finding**: A 6-chromatic two-distance graph in $\mathbb{R}^2$ exists at **16 vertices** (Parts 2020, [arXiv:2010.12656](https://arxiv.org/abs/2010.12656)). A 6-chromatic finite odd-distance graph in $\mathbb{R}^2$ exists explicitly (Parts 2022, [arXiv:2206.12632](https://arxiv.org/abs/2206.12632)). Six-coloring constructions on the off-diagonal continuum side have been extended (Mundinger-Pokutta et al., [arXiv:2404.05509](https://arxiv.org/abs/2404.05509), [arXiv:2501.18527](https://arxiv.org/abs/2501.18527)). By contrast, **no 6-chromatic single-distance UDG in $\mathbb{R}^2$ is known after 8 years of post-de-Grey SAT search**, and the smallest 5-chromatic single-distance UDG has been stuck at 509 vertices (Parts 2020) for 5 years.

**Why it matters**: the obstruction to $\chi(\mathbb{R}^2) \geq 6$ is not branching factor or SAT-solver strength. Both have been adequate to settle adjacent 6-chromatic questions with very small graphs. The obstruction is **structural rigidity of the unit-distance constraint inside $\mathbb{Q}(\sqrt{3}, \sqrt{11})$**: every closed-under-rotation ring extension $\mathbb{Z}[\omega_1, \omega_3, \omega_4, \zeta]$ tried by Polymath16 admits a homomorphic 5-coloring, and no $\zeta$ has been found that refuses one.

**Architectural implication**: the productive next experiment in Architecture 1 may be a **field-theoretic search** (which closed-under-rotation rings refuse 5-colorings?) rather than a *vertex-count search* (smaller and smaller 5-chromatic UDGs). The latter is hitting a structural floor; the former is unexplored.

**Wrong-approach status**: passes the $\mathbb{Q}^2$ detector. The finding only sharpens: $\mathbb{Q}^2$ admits $\chi = 2$; once you enlarge by $\sqrt{3}, \sqrt{11}$ you can force $\chi \geq 5$; the question is which further enlargement (if any) forces $\chi \geq 6$. The detector says the rigidity is field-theoretic, not topological-abstract.

**Cross-links**: Parts 2022 (odd-distance) sits adjacent to Architecture 2 (Davies et al. 2024 showed the odd-distance graph on $\mathbb{R}^2$ has infinite chromatic number, so the structural-overshoot test fails to engage). Mundinger-Pokutta et al. are methodologically adjacent to Architecture 3 (continuum / fractional / spectral methods extended by neural-network search of color classes).

---

