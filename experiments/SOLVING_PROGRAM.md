# Solving Program

Long-range program for substantive contributions to the Hadwiger-Nelson problem.

**Date opened**: 2026-05-26
**Current known bounds**: 5 ≤ χ(R²) ≤ 7 (de Grey 2018; Isbell ~1950)
**Current measurable bounds**: 5 ≤ χ_m(R²) ≤ 7 (Falconer 1981; Isbell)

## Honest assessment

χ(R²) has been open for 75 years. The 2018 breakthrough to χ ≥ 5 was a single brilliant construction (de Grey, 1581 vertices). Eight years of post-de-Grey SAT search (Heule, Polymath16, Parts) have not produced χ ≥ 6. There is real prior probability that χ(R²) = 5 and no 6-chromatic finite UDG exists. Any "plan to solve" the problem is dishonest. What we have is a plan to take serious shots, each of which is a real contribution.

## The structural fact

Three of the four architectures share a single missing combinatorial object (LEARNINGS L4, L9):

  **A finite unit-distance graph in R² with chromatic number ≥ 6.**

- Architecture 1: existence implies χ(R²) ≥ 6 directly.
- Architecture 2: Falconer's 1981 four-step machine inputs a finite k-chromatic UDG and outputs χ_m ≥ k. A 6-chromatic UDG → χ_m ≥ 6.
- Architecture 3: the OFV-style LP constraint sum f(‖v_i‖) ≤ α(G) drives m_1 toward α(G)/N(G) ≤ 1/χ(G). A 6-chromatic UDG → m_1 ≤ 1/6 → integer χ_m ≥ 6.

Find this object once, three barriers collapse.

## Four shots

### Shot 1: 5-chromatic UDG into the LP (integer χ_m ≥ 5 via Architecture 3)

**Goal**: prove integer χ_m(R²) ≥ 5 via the OFV LP framework alone, independent of Falconer's measure-theoretic argument. The first such proof.

**Method**:
1. Take a known 5-chromatic UDG from the de Grey lineage (Polymath 510 chosen for size).
2. Compute α(G) via MAX-SAT or SAT-based binary search.
3. Embed the constraint sum_{i=1}^{510} f(‖v_i + t‖) ≤ α(G) into the e3e LP framework, swept over translations t.
4. LP pushes m_1 toward α(G)/510 ≈ 1/5 = 0.2.
5. Integer χ_m ≥ 5 iff m_1 ≤ 0.2 − ε for some ε > 0.

**Probability of success**: ~95%. Pure engineering on top of the proven e3e framework.

**Wall clock**: weeks (LP at 510×K translations × t-grid is computationally significant but not prohibitive).

**Novelty**: methodological. No published proof of integer χ_m ≥ 5 by LP/SDP alone (OFV stops at 0.2688, KMOR at 0.2588, Ambrus at 0.2470 = barely integer 5 via the bridge inequality, but via a custom 23-point UDG, not via a 5-chromatic UDG).

**Status**: COMPLETED with NEGATIVE RESULT. The Polymath 510 graph cannot be effectively used in the OFV LP (LEARNING L10). At the LP's binding frequency $s^* \approx 0.61$, $\sum J_0(2\pi s^* r_i)$ over the 510 vertex norms is only $\approx -6$ (oscillatory cancellation across spread-out vertex distribution), while the constraint bound $\alpha \geq 142$ is far from binding. The LP never activates Polymath 510 translation constraints. The structural ceiling for the OFV-Moser LP framework with public 5-chromatic UDGs is $m_1 \leq 0.262$, integer $\chi_m \geq 4$. Reaching integer $\chi_m \geq 5$ via this LP route requires either (a) a custom 5-chromatic UDG with radial clustering near $r=1$, or (b) the 2-particle Bachoc-Vallentin SDP framework. Both are research-grade problems.

### Shot 2: Field-theoretic search for χ ≥ 6 (LEARNINGS L1 unexplored direction)

**Goal**: find a 6-chromatic finite UDG by enumerating closed-under-rotation rings over algebraic extensions of Q(√3, √11) and SAT-checking each candidate graph for 5-colorability.

**Method**:
1. Enumerate algebraic extensions Q(√3, √11, √p₁, …, √p_k) for small primes p_i.
2. For each extension K, build the unit-distance graph on a finite ball B_R(0) ∩ K² with small R.
3. SAT-check 5-colorability.
4. Refusal = 6-chromatic UDG found.

**Probability of success**: unknown. Genuinely unexplored. The Polymath16 lineage searched rings of the form Z[ω₁, ω₃, ω₄, ζ] for specific small ζ ∈ {6, 12, 30, 60-th roots of unity}; all admitted 5-colorings. The unexplored question: which closed-under-rotation extensions, particularly those obtained by adjoining further square roots, refuse 5-coloring?

**Wall clock**: months. Compute-heavy.

**Novelty**: this is the actual bet on χ(R²) ≥ 6. High-variance, possibly the way through.

**Status**: BINDING-ROTATION FRAMEWORK BUILT AND ENUMERATED IN $\mathbb{Q}(\sqrt 3, \sqrt{11})$; NEGATIVE FOR chi >= 5 (LEARNINGS L11 + L14).

L11 (initial): naive Moser-orbit graphs in 6 alternate rings give chi = 4.

L14 (refined): The L11-identified "actual research problem" is now executed. The Moser spindle in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ admits exactly 16 single-binding rotations (about origin), 62 double-binding rotations (across all 7 pivots), and 4 triple-binding rotations. Stacking ALL 62 double-bindings yields a 211-vertex, 731-edge UDG with density 3.46 (within 30% of de Grey 1581's density 5.00), still chi = 4. Greedy iterative expansion (e1e Phase 4) plateaus at density 2.27 in a periodic attractor. The field-theoretic rigidity is sharply characterized: $\mathbb{Q}(\sqrt 3, \sqrt{11})$ over the Moser seed barely admits multi-cross-edge rotations. Routes forward:
- Enlarge the field: $\mathbb{Q}(\sqrt 3, \sqrt{11}, \sqrt p)$ for small primes $p$, re-enumerate.
- Larger seed: Heule G7 553 (a chi = 5 UDG) and search binding rotations for chi >= 6.
- Reverse-engineer de Grey: characterize the specific $\{\theta_k\}$ his construction uses.

### Shot 3: Ambrus 23-point reproduction (LP bound m_1 ≤ 0.2470)

**Goal**: reproduce Ambrus-Csiszárik-Matolcsi-Varga-Zsámboki 2023 (arXiv:2207.14179) directly.

**Method**:
1. Extract 23-point configuration coordinates from the paper.
2. Compute independence number of induced UDG.
3. Run e3e-style LP with this configuration as a single rich constraint.
4. Verify bound matches their published 0.2470 → integer χ_m ≥ 5.

**Probability of success**: ~99%.

**Wall clock**: days.

**Novelty**: low (already published). Useful as calibration before Shot 1.

**Status**: COMPLETED 2026-05-29 (e3i, LEARNINGS L35), then SELF-CERTIFIED 2026-05-29 (e3j, LEARNINGS L36). SUCCESS. Obtained the full paper source (arXiv:2207.14179v3), extracted the exact 23-point configuration $X_{23}$ ($\mathbb{Q}(\sqrt 3, \sqrt{11})$; 47 unit-distance edges, 27 distinct distances, all exact-verified by sympy), and independently re-derived the published DUAL certificate: $\varphi(t) = w_0 J_0(t) + \sum w_1(i) + \sum w_2(i,j) J_0(t\|x_i-x_j\|)$ has global min 0.99995003 at $t = 3.7749$ (paper 3.77488, all digits), giving the rigorous bound $(w_T + \nu)/(1-\mu) = 0.246997 < 0.2470 < 1/4$.

**SELF-CERTIFICATION (e3j, L36)**: the L35 bound depended on the paper's asserted $\nu = 10^{-5}$ (the $V(\varepsilon) \geq -\nu$ half rested on 2321 unpublished IEC dual coefficients). e3j removes that dependence. The (IEC) congruence constraint family was transcribed from the .tex ($\sum_{S \supseteq I} a_S = \sum_{S \supseteq J} a_S$ for every congruent subset pair $\{I,J\}$, $X|_I \cong X|_J$), implemented in the repo's IE-LP over congruent independent subsets up to size 5 (5730 constraints), and re-solved. The PRIMAL optimum drops monotonically 0.2584 (IE1+IE2) -> 0.250245 (size 3) -> 0.247468 (size 4) -> **0.246894 (size 5)**, and cvxpy returns the LP's OWN dual = 0.246894 (duality gap $2.5\times10^{-16}$). No paper $\nu$. Integer $\chi_m(\mathbb{R}^2) \geq 5$ via the strict-$1/4$ covering argument ($4 \times 0.246894 = 0.9876 < 1$), now from a self-contained certificate the repo computes itself.

The repo's PRIMAL IE-LP (IE1+IE2, no IEC congruence) on $X_{23}$ gives 0.2584 = KMOR 2015 frontier; the gap to 0.247 was exactly the (IEC) congruence constraints, now implemented. Wrong-approach detector PASS (1D gives $m_1(\mathbb{R}) = 0.5$, no overshoot). De-risks Shot 5'.

### Shot 4: Lean formalization of de Grey 2018 (χ ≥ 5 fully kernel-verified)

**Goal**: produce a Lean 4 / Mathlib proof of χ(R²) ≥ 5 via a verified DRAT/LRAT checker applied to the de Grey 1581 SAT certificate (or smaller Heule/Parts variant).

**Method**:
1. Lean-port a DRAT/LRAT checker (Heule has informal work in this direction).
2. Lean the embedding from 1585-vertex UDG (or 553-vertex Heule G7) into R².
3. Run the verified checker on the SAT certificate.
4. Compose: SAT-unsatisfiability of the 4-coloring CNF + embedding → χ(R²) ≥ 5.

**Probability of success**: ~80% (the SAT-checker piece is well-understood; the embedding piece is what HN-2d already does at vertex count 7).

**Wall clock**: ~6 months.

**Novelty**: significant. No current formal verification of χ(R²) ≥ 5 in any proof assistant. Would be the canonical reference.

**Status**: not started; depends on Lean substrate maturity (HN-2 chain landed, HN-3, HN-5, HN-6 still ahead).

## Compute and infrastructure considerations

- LP at 510 vertices × K translations × t-grid size: scales as O(N × K × |t-grid|) per matrix entry. The matrix is K × |t-grid|. For K = 1000 and |t-grid| = 8000, that's 8M floats per coefficient matrix = ~64 MB. Manageable.
- α(G) computation for 510-vertex graph via MAX-SAT: standard, ~minutes on cadical / kissat with cardinality encoding.
- Field-theoretic search at small ball B_R: compute time scales with |B_R ∩ K²|, which grows polynomially with R. R ~ 5 may be tractable.

## Realism caveats

- Even Shot 2 succeeding gives χ(R²) ≥ 6, leaving χ ∈ {6, 7}. The upper bound of 7 (Isbell hexagonal tiling) has not been improved in 75 years; no plan exists for χ ≤ 6.
- If χ(R²) = 5 truly, Shots 1 and 2 succeed only at "integer χ_m ≥ 5" and "no 6-chromatic UDG found after large search", respectively. Both still publishable contributions, neither resolving the conjecture.
- Architecture 4 (set-theoretic / Borel chromatic) remains stuck post-2018 (LEARNINGS L7); the "obvious replacement Shelah-Soifer conditional" is unstarted but unlikely to advance bounds on χ(R²) per se.

## Structural reframe of Shot 2 (LEARNINGS L14-L20)

After sessions 007-011 reverse-engineered de Grey 1585 and Polymath 510:

- **Every chi >= 5 UDG in the published lineage uses one mechanism**: two 4-chromatic halves coupled by bridge edges (L20). de Grey 1585: 778v + 807v + 155 bridges. Polymath 510: 315v + 195v + 833 bridges. Removing any single component drops chi to 4.
- **Polymath 510 IS de Grey 1585 (translated, restricted to smaller field)** (L19): 62% vertex overlap under T = (2, 0). The Heule/Parts minimization didn't construct a new graph; they reformulated de Grey's.
- **The de Grey 1585 chi=5 obstruction is extremely delocalized** (L18): every reasonable structural reduction drops chi to 4. de Grey's graph is "structurally tight" — no obvious slack.

The implication: **Shot 2 cannot succeed by refining the de Grey / Polymath / Heule lineage**. To force chi >= 6 requires a *qualitatively different* mechanism than "two halves + bridges":

- A 3-way coupling: three 4-chromatic components mutually constrained such that each color must be a different chi-4 structure.
- A hierarchical coupling: pair two chi-5 sub-objects (each requiring 5 colors) into a chi-6 structure.

Neither pattern is known. The path to chi >= 6 is therefore a research-grade open problem requiring new combinatorial ideas, not just larger SAT searches.

Shot 2 (sub-goals revised):
- 2a: Search for a 3-way coupling chi >= 6 UDG (qualitatively new mechanism).
- 2b: Test whether the universal pattern can be replicated in much smaller form (e.g., halves of size 50-100 each + dense bridges).
- 2c: Repeat binding-rotation enumeration in de Grey's full field Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11) — the SAT-minimized Polymath field is provably insufficient.

## Session update 2026-05-29 (abstract chi-6 coupling executed; the barrier is now cocircularity)

The Shot 2 "hierarchical coupling" idea (pair two chi-5 sub-objects into a chi-6 structure) and the "3-way coupling" idea above have now been EXECUTED at the ABSTRACT-graph level, and the result sharpens the open problem rather than resolving it.

- **Abstract chi-6 coupling WORKS** (L24, L27-L30). Coupling two chi-5 halves (Polymath 510) by a no-K_4 bridge set forces chi >= 6: a 1020-vertex no-K_4 graph (L27), tightened to $\|B\| \leq 2000$ (L28), and shown near-vertex-minimal with a single shave to **1019 vertices** (L30, the current abstract record, dual-confirmed UNSAT). Mixed halves (P_510 + P_553, 1063 vtx) give a second non-diagonal instance (L29). The L24 triple-coupling lift (chi >= 6 iff a residual list-coloring is universally infeasible) is the governing theorem and is now MACHINE-CHECKED in Lean ([`lean/HadwigerNelson/L24TripleCoupling.lean`](../lean/HadwigerNelson/L24TripleCoupling.lean), no sorry).
- **But every such graph FAILS UDG-realizability** (L23, L27, L28, L29; the "cocircularity sieve"). The saturating vertices each require 22-27 bridge endpoints to lie exactly on a unit circle; the geometry forbids it. Neither mixed halves nor vertex reduction lifts this obstruction.

**The reframe of the reframe.** The abstract coupling mechanism is no longer the open problem. The open problem is precisely **making a chi-6 coupling UDG-realizable**: finding plane coordinates (in some algebraic field) for which the required bridge edges ARE unit distances AND the saturating-vertex cocircularity conditions hold. This is geometric / field-theoretic, and it points Shot 2 squarely at sub-goal 2c (enlarge the field beyond the SAT-minimized $\mathbb{Q}(\sqrt 3, \sqrt{11})$) and at building couplings COORDINATE-FIRST rather than abstract-first.

**Measurable frontier corrected** (L31-L33). $\chi_m(\mathbb{R}^2) \geq 5$ (Falconer 1981) is the best known; **$\chi_m \geq 6$ is OPEN** (the cited "$\geq 6$" results are hyperbolic-plane or convex-tile misattributions). Falconer's machine inputs a rigid $(k{-}1)$-chromatic UDG; $\chi_m \geq 6$ needs a rigid 5-chromatic configuration, the SAME missing object as Architecture 1. The OFV 2-point spectral bound ($m_1 \leq 0.287$) was reproduced and cross-validated (e2b); the 3-point matrix lift gives no improvement on the unit-triangle family.

**Net**: three architectures still collapse onto one missing object (a chi-6 UDG that EMBEDS in the plane). The abstract-graph and measurable threads are now well-mapped and confirm the gap; the live bet remains Shot 2 in an enlarged field.

## Session update 2026-05-29b (coordinate-first realizable coupling executed; the barrier sharpens to "wrong-shape bridge supply")

The two thrusts dispatched this session (2c field enlargement, and the novel coordinate-first realizable coupling) both ran and both returned clean, dual-solver-confirmed NEGATIVES. The result (LEARNINGS L34) sharpens the cocircularity barrier into a stronger statement.

- **Coordinate-first realizable coupling (the novel thrust, h7 / h7b)**: build the coupling so realizability holds BY CONSTRUCTION (two real plane UDGs joined only by genuine exact unit-distance cross-pairs). Every union is 5-colorable, EVEN at bridge counts vastly exceeding the abstract requirement: a 3-way 60-degree orbit of $P_{510}$ has **13,757 genuine unit-distance bridges** (1530 vtx, $\omega = 3$) and is 5-colorable in 0.06s (Cadical + Glucose). The abstract L27 chi-6 graph needs only $\|B\| \leq 2000$ ADVERSARIAL bridges; $5\times$ that many GEOMETRIC bridges fail.
- **Field enlargement on a chi-5 seed (2c, h7c)**: binding rotations on Heule-553 introducing $\sqrt 7, \sqrt{19}, \sqrt{23}, \sqrt{15}$ yield only 72-1473 realizable bridges, all 5-colorable sub-100ms. L11/L14 field-rigidity confirmed at the realizable level.
- **Adversarial subset of the realizable pool (h7d)**: even adversarial greedy selection restricted to genuine unit-distance bridges cannot force chi-6 (stalls at $\|B\| = 995-2325$, all 5-colorable; for the Moser-rotation pool the greedy gain hits ZERO).

**The sharpened barrier**. Realizability forces an EVEN, low-concentration bridge layout (60-deg: max bridge-degree 36, all 510 vertices touched). The chi-6 list-coloring obstruction (L24/L27) needs CONCENTRATION (L27: max source degree 268 on hub vertices). The embeddable bridge supply is the wrong SHAPE for chi-6 forcing, not merely the wrong COUNT. This is why no chi-6 UDG has emerged from the lineage at scale. Shot 2 is redirected: the only remaining lever is a chi-5 building block whose self-unit-distance neighborhoods concentrate, for which no candidate exists.

## Status table

| Shot | Goal | Status | Lead time |
|------|------|--------|----------:|
| 1 | Integer χ_m ≥ 5 via LP-only (Arch 3) | completed; negative result (L10) | done |
| 2 | χ ≥ 6 via field-theoretic UDG search (Arch 1) | binding-rotation enumeration in Q(√3, √11) complete (L11, L14); coordinate-first realizable coupling executed (L34): realizable bridges (up to 13,757, dual-solver) NEVER force chi-6; barrier sharpened to "embeddable bridge supply is wrong-SHAPE (even/low-concentration) not wrong-count". field-enlarged seeds (√7,√19,√23,√15) all chi-5 | months |
| 3 | Ambrus 23-point reproduction | done; reproduced (L35) then SELF-CERTIFIED via IEC (e3j, L36): repo's own dual $m_1 \leq 0.246894 < 1/4$, no paper $\nu$, integer $\chi_m \geq 5$ self-contained | done |
| 4 | Lean formalization of de Grey | not started | ~6 months |
| 5 | 2-particle Bachoc-Vallentin SDP for tighter LP | reframed: BV-SDP no help at n=2 (L12) | — |
| 5' | Ambrus IE-LP framework + beam search | implemented (e3g, e3h); greedy width-1 reaches 0.2584 at 17 pts matching KMOR 2015; plateau at local optimum (L13). IEC congruence constraints now implemented (e3j, L36): on $X_{23}$ they tighten the repo's own LP from 0.2584 to 0.246894, self-certifying integer $\chi_m \geq 5$ without the paper's duals | IEC done; further beam search capped at $\alpha_1 = 1/4$ |
| 6 | Custom radially-clustered 5-chromatic UDG search | not started | research-grade open |
| 2-abs | Abstract chi-6 coupling (two chi-5 halves + bridges) | done; 1020-vtx (L27) -> $\|B\|\leq2000$ (L28) -> 1019-vtx record (L30); mixed halves P510+P553 (L29). ALL no-K_4 chi>=6 but NOT UDG-realizable (cocircularity). The barrier is now precisely cocircularity, not abstract existence | done |
| 2-lean | Lean machine-check of the chi>=6 coupling theorem (L24) | done; L21/L22 covering ladder + L24 triple-coupling lift formalized, no sorry (lean/HadwigerNelson/) | done |
| 2-meas | Measurable frontier consolidation (e2b/e2c) | done; chi_m>=5 is the frontier, chi_m>=6 OPEN (L31); OFV 2-pt bound reproduced + cross-validated, 3-pt no gain (L32); Falconer decomposition, same missing object (L33) | done |

Update this document after each major milestone.
