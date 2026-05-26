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

**Status**: FRAMEWORK BUILT, INITIAL EXPERIMENTS NEGATIVE (LEARNING L11). The naive form — rotate Moser spindle by Moser-style angles in 6 alternate rings (Q(sqrt 7), Q(sqrt 19), Q(sqrt 23), Q(sqrt 27)=Q(sqrt 3), Q(sqrt 31), Q(sqrt 39)) at orbit sizes 3-6 — produces graphs of |V|=37, |E|=66 that are *all* 4-colorable. Structural reason: rotated copies share central vertices but have no cross-copy unit-distance edges, so the orbit graph is the disjoint union (modulo central identification) of Moser spindles, chi = 4. The de Grey 2018 construction works because *specific* rotation choices accidentally produce cross-copy unit edges; finding such coincidences in alternate rings is the actual research problem. Future work: algorithmic search for binding rotations + ML-driven configuration discovery. Multi-month-scale beyond a session.

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

**Status**: not started; deferred unless Shot 1 hits unexpected obstacles.

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

## Status table

| Shot | Goal | Status | Lead time |
|------|------|--------|----------:|
| 1 | Integer χ_m ≥ 5 via LP-only (Arch 3) | completed; negative result (L10) | done |
| 2 | χ ≥ 6 via field-theoretic UDG search (Arch 1) | framework built; orbit-only negative (L11) | months |
| 3 | Ambrus 23-point reproduction | deferred | days |
| 4 | Lean formalization of de Grey | not started | ~6 months |
| 5 | 2-particle Bachoc-Vallentin SDP for tighter LP | reframed: BV-SDP no help at n=2 (L12) | — |
| 5' | Ambrus IE-LP framework + beam search | implemented (e3g, e3h); greedy width-1 reaches 0.2584 at 17 pts matching KMOR 2015; plateau at local optimum (L13) | weeks for width-2 / swap |
| 6 | Custom radially-clustered 5-chromatic UDG search | not started | research-grade open |

Update this document after each major milestone.
