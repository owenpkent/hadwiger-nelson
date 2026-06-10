# Proof Architectures Plan

The experimental thread is organized around the same four-architecture framework used in the zeta-function repo. Each architecture has its own subdirectory under `experiments/`.

## The four architectures

### Architecture 1: Combinatorial / UDG

**Aim**: produce a finite unit-distance graph $G$ in $\mathbb{R}^2$ with $\chi(G) \geq 6$, or push lower bounds via SAT.

**Why this is the primary thread**: the only architecture that has produced a strict improvement ($\chi \geq 5$, de Grey 2018) in 70 years.

**Experiments**:
- `e1a_moser_spindle.py` — verify $\chi(\text{Moser}) = 4$ via SAT; baseline sanity check.
- `e1b_de_grey_skeleton.py` — load de Grey's 1581-vertex graph; verify $\chi \geq 5$.
- `e1c_polymath16_smallest.py` — current smallest known 5-chromatic UDG.
- `e1d_six_chromatic_search.py` — targeted search for $\chi \geq 6$ constructions.

**Wrong-approach gate**: every construction is exact (vertex coords in a number field $K$); we verify that the same graph, restricted to $K \cap \mathbb{Q}^2 = \mathbb{Q}^2$, gives a $\chi = 2$ subgraph, confirming the construction uses the algebraic extension nontrivially.

### Architecture 2: Measurable / spectral

**Aim**: prove $\chi_m(\mathbb{R}^2) \geq 6$ or push the spectral / Fourier bounds.

**Experiments**:
- `e2a_falconer_autocorrelation.py` — autocorrelation of a 1-avoiding hexagonal cell; the Plancherel seed (illustration).
- `e2b_spectral_sdp.py` — OFV 2-point radial-Fourier ($J_0$/Hankel) LP + DMOV-style 3-point matrix SDP for $m_1(\mathbb{R}^2)$; cross-validated against Arch-3 e3c.
- `e2c_falconer_rigorous.py` — Falconer's $\chi_m \geq 5$ decomposed: Wiener-Khinchin witness + exact density-route arithmetic + the rigid 4-chromatic configuration (Moser spindle).

**Wrong-approach gate**: experiments must reference the $O(2)$ rotation group; reductions to $\mathbb{R}^1$ should hit a trivial bound, not the actual $\chi_m \geq 5$ value.

### Architecture 3: Fractional / Lovász $\vartheta$ / spectral

**Aim**: compute fractional chromatic and Lovász $\vartheta$ on UDGs, and explore Bochner integral formulations on $\mathbb{R}^2$.

**Experiments**:
- `e3a_fractional_chromatic_small.py` — LP for $\chi_f$ on the Moser spindle and de Grey-lineage graphs.
- `e3b_lovasz_theta.py` — SDP via cvxpy for $\vartheta(G)$ on the same graphs.
- `e3c_bochner_continuous.py` — continuous formulation on $\mathbb{R}^2$ via Bochner / spherical functions.

**Wrong-approach gate**: same experiment must give $\chi_f(L^\infty\text{-UDG}) \leq 4$ to confirm metric dependence.

### Architecture 4: Set-theoretic / axiomatic

**Aim**: clarify the dependence of $\chi$ on choice, refine Borel chromatic.

**Experiments**: largely expository / Lean-formalization-only at this stage. The "experiments" are existence/independence arguments rather than computations.

## Shared infrastructure

`experiments/_shared/`:
- `unit_distance_graph.py` — UDG class; vertices as exact symbolic coordinates; edges induced by exact distance $= 1$; SAT colorability check.
- `wrong_approach_detectors.py` — implementations of the $\mathbb{Q}^2$, $L^\infty$, and $\mathbb{R}^1$ controls; helper to run any candidate-method on these.
- `smoke_test.py` — confirms (a) Moser spindle has $\chi = 4$, (b) $\mathbb{Q}^2$ control gives $\chi = 2$ on test points, (c) $L^\infty$ control gives $\chi = 4$ on a square grid.

## Execution order

1. Land `_shared/` + `e1a_moser_spindle.py` + `smoke_test.py` — baseline that everything works.
2. Land `e1b_de_grey_skeleton.py` — reproduce the state of the art.
3. Pick one of Architecture 1d / 2b / 3a for first exploratory work.
4. Maintain `LEARNINGS.md` after each experiment with structural findings.

## Status table

| Experiment | Architecture | Status |
|------------|--------------|--------|
| e1a Moser spindle | 1 | done (cadical195 + glucose4 agree on chi = 4) |
| e1b de Grey skeleton | 1 | done for 510/517/529/553/826/1585 (cadical195 + glucose4 agree on UNSAT across all six, including the original de Grey 2018 graph) |
| e1c Polymath16 smallest | 1 | not started |
| e1d field-extension orbit search ($\chi \geq 6$) | 1 | framework built; orbit-only naive negative across 6 alternate rings (LEARNINGS L11) |
| e1e Moser binding-rotation search ($\chi \geq 6$) | 1 | done; 16 single bindings in $\mathbb{Q}(\sqrt 3, \sqrt{11})$; greedy stacking plateaus at $E/V = 2.27$, chi = 4 (LEARNINGS L14) |
| e1f Moser double-binding (origin pivot) | 1 | done; only 6 double-bindings, ALL degenerate (cross = 0); union $V=29, E=61$, chi = 4 (LEARNINGS L14) |
| e1g Moser double-binding (all 7 pivots) | 1 | done; 62 double-bindings, 4 with triple cross edges; union $V=211, E=731$, density 3.46, chi = 4 (LEARNINGS L14) |
| e1i Polymath 510 / Heule 826 symmetry analysis | 1 | done; both have NO non-identity exact rotational symmetries (SAT-minimization destroyed them) (LEARNINGS L15) |
| e1j Polymath 510 approximate C_6 symmetry | 1 | done; R_60 covers 92.35%, R_120 92.16%, etc. (LEARNINGS L15) |
| e1k Polymath 510 C_6 closure & minimal subset | 1 | done; closure $V=1155, E=10397$, chi=5; ALL 6 rotation copies essential (C_6-irreducible) (LEARNINGS L15) |
| e1l de Grey 1585 exact symmetry analysis | 1 | done; no non-identity exact rotational symmetries about 9 pivots (LEARNINGS L16) |
| e1m de Grey 1585 approximate symmetry | 1 | done; approximate D_6 about $v_0 = (2, 0)$, ~50% coverage per non-identity element (LEARNINGS L16) |
| e1n de Grey 1585 C_6 core extraction | 1 | done; 778-vertex core has chi = 4; chi>=5 depends on asymmetric residue (LEARNINGS L16) |
| e1o de Grey singleton/greedy augmentation | 1 | done; no singleton/degree-greedy addition forces chi >= 5 (LEARNINGS L17) |
| e1p de Grey asymmetric half chi | 1 | done; chi = 4 (807 vertices, 3948 edges, density 4.89) (LEARNINGS L17) |
| e1q de Grey bridge subgraph | 1 | done; 155 bridges touch 124 core + 22 asym vertices; bridge-touched subgraph chi = 4 (LEARNINGS L17) |
| e1r de Grey targeted reductions | 1 | done; every reduction (including 75% of original) drops chi to 4. Obstruction is extremely delocalized (LEARNINGS L18) |
| e1s Polymath 510 vs de Grey 1585 vertex comparison | 1 | done; 315/510 = 62% of Polymath vertices match de Grey under T = (2, 0). Polymath 510 is a translated substructure of de Grey + 195 field-reduction artifacts (LEARNINGS L19) |
| e1t Polymath/de-Grey overlap chi | 1 | done; 315-vertex overlap is chi = 4; 195-artifact is chi = 4. Polymath 510 has same "two halves + bridges" pattern as de Grey 1585 (LEARNINGS L20) |
| h5 Polymath-squared chi >= 6 (diagonal) | 1 | done; $P_{510} \cup P_{510} + B$, 1020 vtx, $\|B\| = 2700$, no-$K_4$, triple-solver chi >= 6, NOT UDG-realizable (LEARNINGS L27) |
| h6 bridge-minimum probe | 1 | done; tightened diagonal $\|B\|$ from 2700 to $\leq 2000$, graded rainbow forcing obstruction (LEARNINGS L28) |
| h6 mixed-halves chi >= 6 (Direction A) | 1 | done; $P_{510} \cup P_{553} + B$, 1063 vtx, $\|B\| = 2400$, no-$K_4$, dual-solver chi >= 6, NOT UDG-realizable. First NON-diagonal chi-6 no-$K_4$ graph. Mixed halves do NOT beat 1020-vtx / 2000-bridge baseline; only win is field-structure diversity. 510x826 inconclusive (killed mid-SAT) (LEARNINGS L29) |
| h6 mixed-halves 510x517 re-run (Direction A loose thread) | 1 | done; bridge set rebuilt + PERSISTED at $\|B\| = 1800$ (1027 vtx, 6883 edges, $\omega = 3$ exhaustive), then uncapped Cadical ran ~66.5 min without resolving => SAT-intractable in budget. Not a chi-6 confirmation, not a refutation. DIMACS persisted (`h6mix_510x517_B1800_decisive.cnf`) for future kissat/cryptominisat handoff. New tooling: checkpoint-persist in `h6_mixed_halves.py` + decoupled `h6_mixed_decisive_sat.py`. L29 unchanged, no L30 (LEARNINGS L29 addendum) |
| h6 Direction B reduce below 1020 (deletion / quotient / triple-coupling) | 1 | done; PARTIAL. New record: a **1019-vtx** no-K_4 chi >= 6 graph (delete H2 vtx 1014; UNSAT confirmed twice, 1973s + independent 1892s). NOT single-vertex-rigid, but bulk-deletion-rigid: deleting >= 8 non-bridge H2 vtx breaks chi-6 (Cadical SAT 32s), deleting 2/4 is SAT-intractable (BUDGET ~390s). 566 non-bridge vtx are NOT inessential (delocalized obstruction tolerating one peripheral loss). Triple-coupling closed: S199/L403/T721 all chi=4, no sub-340 chi-5 no-K_4 gadget. True vertex-minimum OPEN: <= 1019, with 1018/1016 SAT-intractable to decide (LEARNINGS L30) |
| F1 pressure-test (cocircularity barrier, adversarial) | 1 | done; no chi-6 UDG (no break). SHARPENED: in $P_{510}$ forced-different $=$ adjacent (SAT-certified, 0/300 non-adj pairs forced), so the single-hub chi-6 route reduces to Lemma (L) "can 5 cocircular-at-unit points be rainbow-forced?" which fails (needs unit-distance $K_5$, $\omega=3$). Cocircularity $=$ classical $K_{2,3}$-freeness (not novel). L34 "even spread" framing retracted. Open reframing: find a chi-5 UDG with LONG-RANGE color forcing. Files `f1pt_*.py`, report `F1_pressure_test.md`, ledger in `docs/PUBLISHABLE_FINDINGS.md` (LEARNINGS L42) |
| lrf C_6-closure long-range forcing | 1 | done; the $V=1155$ symmetric $C_6$ closure of $P_{510}$ (non-minimal, exactly realizable, $\chi=5$) has NO long-range forcing (1774 pairs, 0 non-adjacent forced-different), extending L45 past the SAT-minimized lineage (LEARNINGS L51) |
| lrf abstract clamp construction | 1 | done; the abstract L45 ingredient (a $K_4$-free $\chi=5$ graph with a non-adjacent forced-different pair at $k=5$) EXISTS as a one-move vertex-split of a $K_4$-free 6-critical graph; explicit SAT-verified 48-vtx triangle-free witness; relocates the $\chi\ge6$-by-coupling obstruction onto W3 (UDG realizability) alone (LEARNINGS L51) |
| realizability W3 clamp (calibrated) | 1 | done; a calibrated unit-distance embedder fails to realize the 48-vtx clamp (evidence, not proof); DECISIVE negative-about-method: the realizable $P_{510}$ (over-det $+1487$, max-deg $36$) INVALIDATES the DOF and degree heuristics, so W3 is not decidable by counting -- it is the algebraic cocircularity (L42) question (LEARNINGS L52) |
| W3 clamp cocircularity reduction (Theorem R) | 1 | done; adversary-reviewed exact reduction generalizing Lemma L: a clamp is realizable IFF $H-w$ realizes with $N(w)$ split into two unit circles (distinct centers); the clamp ESCAPES the unit-$K_k$ impossibility; residual = a flexible color-clamp (one circumradius equation for a degree-5 split). Note `W3_CLAMP_REDUCTION.md` (LEARNINGS L53) |
| backward-from-2050 retrodiction synthesis | all 4 | done; meta-synthesis (no code, no bound). 8 adversary-stress-tested 2050 worlds + 5 wildcards integrated. MOST LIKELY = $\chi=6$ by a finite UDG; cross-world LINCHPIN = the W3 realizable clamp (~5/8 worlds route through it); DARK HORSE = the $\chi_B$ definability split. Value call: probably 6 (clamp escapes de Grey 2026 $\omega\le3$). Surfaces two runnable wildcard probes (monotile-forcing, renormalized-clamp) attacking the L45 gap from outside the de Grey/Polymath lineage. Session `orchestrator_sessions/2026-06-02-backward-from-2050-synthesis.md` (LEARNINGS L54) |
| wildcard B: renormalized clamp (RG transfer matrix) | 1 | done; corrects the brainstorm ($\lambda_1$ is coloring-entropy, NOT forcing; the diagnostic is imprimitivity / spectral gap). Color-symmetry ($S_k$ 2-transitivity) confines single-vertex-port relations to the primitive monoid $\{0,I,J{-}I,J\}$, so a chain cannot reach $\mathbb{Z}_k$ forcing; the clamp FACTORS into (i) forced-same under $\omega\le3$ or (ii) a wide $\ge2$-vertex separator $=$ Theorem R's degree-$\ge5$ split. RG/substitution conserves but cannot create imprimitivity. Script `combinatorial/wildcard_b_rg_transfer.py` (LEARNINGS L55) |
| forced-same sweep (L55 sub-question i) | 1 | done; NEGATIVE. Dual of L45 (add edge $a$-$b$, 5-UNSAT $\Rightarrow$ forced-same): ZERO non-adjacent forced-same pairs across all 12 chi-5 UDGs (~22.5k pairs, 0 indeterminate). With L45 this proves non-adjacent pairs in the lineage are COMPLETELY UNFORCED (all forcing is local). Splice lemma (forced-same $+$ unit edge $\Rightarrow$ clamp $\Rightarrow\chi\ge6$) verified exactly on $K_6-e$. Remaining route = sub-question (ii). Script `combinatorial/shotC_forced_same.py` (LEARNINGS L56) |
| EXHAUSTIVE forcing classification (shot D) | 1 | done (11/12 complete, 874 at ~96%); upgrades L45+L56 from sampled to EXHAUSTIVE. Classifies EVERY non-adjacent pair as forced-different / forced-same / free: ~2.29M pairs, ALL free, 0 forced, 0 indeterminate, 0 hits. No long-range forcing anywhere in the lineage; the missing chi>=6 object must be a NEW UDG outside it. Checkpointed/resumable script `combinatorial/shotD_exhaustive_forcing.py` (LEARNINGS L57) |
| creative round 2: 10-lens first-principles attack | all 4 | done; 9/10 lenses delivered, adversary-pruned (workflow `hn-first-principles-attack`; reusable optimized version `.claude/workflows/hn-lens-attack.js`). Products: the PHASE-GADGET DICHOTOMY (W3-free, born-realized certificates: imprimitive interface transfer $+$ rational angle $\Rightarrow$ finite $\chi\ge6$ necklace; irrational $\Rightarrow \chi_m,\chi_B\ge6$), the Equality-Alternator target (width-2, provably invisible to L45/L56/L57), the Essential-Pair Lemma (proved), four unsearched lineage sectors, Aperiodic Chromatic Rigidity $+$ Constructible Plateau conjectures, two sparse-solver workarounds. ERRATUM: S199/L403/T721 are $\chi=4$; the chi-5 lineage members are the nine numbered graphs (LEARNINGS L58) |
| vertex-criticality scan of the chi-5 nine | 1 | done; ALL NINE vertex-critical (0 redundant, 0 indeterminate, ~5145 solves, ~105 min). Via the Essential-Pair Lemma the lineage PROVABLY cannot host forced pairs: L57's exhaustive freeness is a corollary (forcing-sterile BY CONSTRUCTION, since SAT minimization drives to criticality). Policy: never minimize; criticality scan $=$ $O(n)$ pre-filter replacing $O(n^2)$ pair sweeps. Script `combinatorial/critscan_lineage.py` (LEARNINGS L59) |
| E1 abstract Equality-Alternator existence | 1 | done; POSITIVE. 693/25143 independent edge-pairs of $M^3(C_5)$ are equality-alternators (every proper 5-coloring colors exactly one of two non-adjacent pairs same); one independently verified by all 4 patterns. The $p=2$ phase object of L58 EXISTS (alternator analog of L51's abstract clamp); difficulty relocates to realizing it as a UDG with congruent rotation-related interfaces. Scripts `combinatorial/e9_alternator_abstract.py` + `e9_alternator_verify.py` (LEARNINGS L60) |
| E3 Z6 necklace closure of P510 | 1 | done; NEGATIVE-as-predicted. Exact $\mathbb{Z}_6$ closure of $P_{510}$ (60-deg, 868 vtx, 5740 edges, $K_4$-free) is 5-SAT. A naive rational-angle closure of a LINEAGE graph cannot manufacture $\chi\ge6$ (the lineage has no phase structure: L57 free, L59 critical); the necklace needs a phase-carrying alternator seed, not a lineage graph. Script `combinatorial/e10_necklace_z6.py` (LEARNINGS L60) |
| E1b alternator W3 (minimize + congruence) | 1 | done; structural. Minimizing all 693 M^3(C5) alternators is VACUOUS (all stay 47 vtx): a 6-critical host is irreducible, so min alternator order $=$ min K4-free 6-critical order (same bottleneck as the clamp, L51 floor $[9,48]$). $\sim$1/3 carry a pair-swap INVOLUTION (built-in congruence the clamp lacks). $M^3(C_5)$ is triangle-free ($\omega=2$) $=$ worst realizability substrate; need a small $\omega=3$ host or the born-realized lineage sweep. Script `combinatorial/e11_alternator_w3.py` (LEARNINGS L61) |
| E12 born-realized alternator sweep (lineage) | 1 | done; NEGATIVE. All 9 chi-5 graphs (top-60 core, 500 diverse colorings via sampling filter): ZERO born-realized alternators, no pair-of-pairs $(e_1,e_2)$ with $G+e_1+e_2$ 5-UNSAT. Extends L57/L59 sterility from single pairs to TWO-EDGE forcing; the alternator, like the clamp, must come from a NEW graph. Mono-rate $\sim0.2$ across all 9 (L57 liquidity confirmed). Route 1 (small $\omega=3$ 6-critical host) is now the sole live phase-route door. Script `combinatorial/e12_born_alternator.py` (LEARNINGS L62) |
| e2a Falconer autocorrelation (illustration) | 2 | done; FFT autocorrelation of a 1-avoiding hexagonal cell vanishes on the unit circle (pedagogical seed) |
| e2b spectral SDP/LP for $m_1(\mathbb{R}^2)$ | 2 | done; 2-point bound reproduced EXACTLY ($m_1 \leq 0.287119$ basic, $0.268412$ 3-triangle; cross-validation gate PASS vs e3c/OFV 2010 to $<5\mathrm{e}{-7}$); $\mathbb{R}^1$ detector PASS ($0.5$); 3-point matrix (SDP) lift gives NO improvement on the unit-triangle family ($0.26840$); tightening lives in IE-atom LP (Arch 3) / full DMOV $O(2)$-isotypic SDP (beyond SCS backend) (LEARNINGS L32) |
| e2c Falconer $\chi_m \geq 5$ rigorous-numerical | 2 | done; Plancherel/Wiener-Khinchin witness (positive-type, $R_A(1)=0$ to $5\mathrm{e}{-17}$); density route crosses to $\geq 5$ only at Ambrus 2023 $m_1 < 1/4$; rigidity route needs a $5$-chromatic rigid config $=$ Arch-1 missing object; $\chi_m \geq 6$ OPEN (LEARNINGS L33) |
| Arch-2 survey: measurable / spectral frontier | 2 | done; consolidated $\chi_m \geq 5$ unimproved 45 yrs, $\geq 6$ OPEN, "$\geq 6$" results are hyperbolic/convex-tile misattributions; $k$-point hierarchy mapped; companion atlas `arch2_measurable.md` written (LEARNINGS L31) |
| e3a fractional small | 3 | not started (subsumed by e3a Lovász theta below) |
| e3a Lovász $\vartheta$ on Polymath16 510 | 3 | done; $\vartheta = 170.24$, loose chi >= 3 (LEARNINGS L5) |
| e3b OFV Bessel-LP for $m_1(\mathbb{R}^2)$ | 3 | done; $m_1 \leq 0.287$ giving $\chi_m \geq 4$ in 30 ms via cvxpy + HiGHS (LEARNINGS L6) |
| e3c OFV multi-simplex LP for $m_1(\mathbb{R}^2)$ | 3 | done; $m_1 \leq 0.268412$ giving $\chi_m \geq 4$ (real $\geq 3.73$) via 3 off-center unit triangles, exact match to OFV 2010 Table 3.1 (LEARNINGS L8) |
| e3d wide-triangle sweep | 3 | done; 1409 candidate triples on $0.1$-grid saturates near 0.2682; triangle class exhausted (LEARNINGS L9) |
| e3e Moser-spindle LP inequality | 3 | done; $m_1 \leq 0.2619$ via Moser-spindle ($N=7, \alpha=2$) translations + OFV triangles, closes 75% of OFV-to-KMOR gap; $\chi_m \geq 4$ (real $\geq 3.82$) (LEARNINGS L9) |
| e3f Polymath 510 in LP (Shot 1) | 3 | done; structural negative, LP ignores Polymath 510 constraint due to Bessel-sum cancellation across 510 vertices (LEARNINGS L10) |
| e3g Ambrus inclusion-exclusion LP framework | 3 | done; implemented IE-LP. Moser 0.283, hex 2-layer 0.276, Moser+hex 0.272. Single-config bounds limited; LEARNINGS L12 |
| e3h IE-LP beam search over Polymath 510 pool | 3 | done; m_1 $\leq$ 0.2584 at 17 vertices, matches KMOR 2015 (0.2588). Plateau at greedy width 1 (LEARNINGS L13) |
| e3i Ambrus 2023 reproduction (Shot 3) | 3 | done; **first integer $\chi_m(\mathbb{R}^2) \geq 5$ by LP.** Extracted exact 23-point config $X_{23}$ (47 edges, 27 distances, exact-verified); dual certificate $\varphi(t)$ re-derived to all digits, rigorous $m_1 \leq 0.246997 < 1/4$ (paper 0.24699). Primal IE1+IE2 gives 0.2584 (gap = the 5868 IEC congruence constraints, identified). Arch-3 density route CAPPED at $\chi_m \geq 5$ ($\alpha_1 = 1/4$ conjectured). (LEARNINGS L35) |
| e3p / e3q symmetry-reduced SDP + intermediate probe | 2/3 | done; the COMPLETE symmetry-reduction program (Parts 1+2), built and gated against the naive engine (no fake certificates). **e3p** (L46): $S_k$-block-diagonalized order-1, reproduces e3m exactly, PSD side $1+nk\to n$ (independent of $k$; X_23 $93\to23$, ~100x faster). **e3q** (L47): $S_k$-block-diagonalized order-2 via Murota multiplicity alignment (the naive eigenbasis provably fails: irreps with mult>1; alignment residual ~1e-13), reproduces e3n on triangle+rhombus, runs Moser order-2 in 6s where naive e3n OOMs at 25GB; +O(2)-congruence variable reduction (L49, == size-<=4 IEC). **HONEST BOUNDARY** (L48/L49/L50): X_23 order-2 has ~98627 moment variables; $S_k$ shrinks blocks but not variables, $O(2)$ halves variables only (98627->48342, generic config), so the two reductions TOGETHER do not fit X_23 order-2 in dense cvxpy (48342 vars x blocks up to 735 -> 171 GiB affine map). Probe (L50): order-2 never strictly beats order-1 at runnable scale -> no shortcut. The route reduces to ONE prerequisite: a custom SPARSE conic backend (de Laat-Vallentin) (LEARNINGS L43-L50) |
| e3n order-2 moment / Lasserre | 2/3 | done; the L40 strength-increment (IEC up to subset size 4 vs degree-1's size 2). Order-2 moment matrix (empty+singleton+proper-pair patterns, entries size-<=4 moments, shared-var consistency) + PSD + Bochner + IEC<=4. Validated: cert path live (triangle k=2 infeasible), no false cert (rhombus k=4 margin ~0 with 672 size-3 IEC). KEY FINDING: naive order-2 DOES NOT SCALE -- $\|B\|=1+nk+(\binom{n}{2}k^2-Ek)$ explodes (n=4->93, n=7->321, X_23->4141) and even n=4 takes ~13s (cvxpy PSD canon.); first build OOMed >1GB at $\|B\|$~180 (fixed via sparse vec(M)=Sy map). X_23 frontier REQUIRES symmetry reduction (de Laat-Vallentin block-diagonalization). No strict order-2>order-1 separation at small scale (LEARNINGS L41) |
| e3m moment / Lasserre backend | 2/3 | done; the L38/L39 barrier-(a) SCALABILITY fix. Degree-1 (pairwise) color-marginal moment relaxation + Lasserre order-1 PSD moment matrix + per-color Bochner + e3l IEC keys (now linear on moments); never enumerates colorings (poly in $n$). Cross-validates vs e3l (margin $\leq 10^{-10}$ on small configs), passes $\chi_m\leq7$ gate, PSD cert path live (triangle $k=2$/Moser $k=3$ infeasible), scales to 19 pts in seconds. Methodological lesson: SCS first-order noise ($10^{-5}$) faked a $\chi_m\geq6$ certificate; CLARABEL interior-point ($10^{-9}$) kills it. No config certifies. Next: restore+track $X_{23}$, run $k=4$ (validate $\geq5$); lift to order-2 moments if degree-1 misses (LEARNINGS L40) |
| e3l multi-class IEC (Formulation 1 + 2) | 2/3 | done; the L38 "sharpness" layer BUILT + VALIDATED. Both IEC formulations (per-color monochromatic + full joint-pattern cross-color, bijection-transported, deduped) added as hard equalities on the joint-coloring atoms. Soundness gate PASS: $\chi_m \leq 7$ ($k=7$ on rhombus, 3234 IEC incl. 3192 cross-color) stays feasible (margin 0); cert path live (no-proper-coloring => chi_m>=k+1). INERT on all enumerable rigid configs ($\leq 7$ pts, $k\in\{4,5\}$, margin 0 even with ~9000 cross-color constraints). Isolates L38 barrier (a) scalability as the SOLE remaining wall; IEC keys are backend-agnostic, ready for a Lasserre/moment port (LEARNINGS L39) |
| e3j IEC self-certification | 3 | done; **integer $\chi_m(\mathbb{R}^2) \geq 5$ now FULLY SELF-CERTIFYING.** Derived the (IEC) congruence family from the .tex, implemented it in the repo's IE-LP (congruent independent-subset pairs up to size 5, 5730 constraints), re-solved. Primal $m_1 = 0.246894$ with the repo's OWN cvxpy dual = 0.246894 (gap $2.5\mathrm{e}{-16}$), no paper $\nu$. Monotone ladder 0.2584 -> 0.250245 -> 0.247468 -> 0.246894 as IEC subset size grows. $4 \times 0.246894 = 0.9876 < 1$, so integer $\chi_m \geq 5$ self-contained. Wrong-approach 1D = 0.5 (no overshoot). HiGHS, 156-1698 s per solve. (LEARNINGS L36) |
