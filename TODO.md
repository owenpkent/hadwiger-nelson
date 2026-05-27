# TODO

Task tracker for the Hadwiger-Nelson research repo.

## Bootstrap (scaffold landed 2026-05-25)

- [x] Write `docs/00_intuitive/what_is_the_problem.md` accessible exposition
- [x] Write `docs/01_undergraduate/moser_spindle.md` first chi >= 4 proof
- [x] Write `docs/01_undergraduate/hexagonal_upper_bound.md` Isbell tiling
- [x] Implement `experiments/_shared/unit_distance_graph.py` core UDG class
- [x] Implement `experiments/_shared/wrong_approach_detectors.py` Q^2 + L-infinity controls
- [x] Implement `experiments/_shared/smoke_test.py` sanity check on Moser spindle and small UDGs
- [x] Write `experiments/combinatorial/e1a_moser_spindle.py` verify chi(Moser) = 4 via SAT (cadical195 + glucose4 agree)
- [x] Write `experiments/combinatorial/e1b_de_grey_skeleton.py` cadical195 + glucose4 agree on UNSAT for 510 / 517 / 529 / 553 / 826 / 1585 (the original de Grey 2018 graph)

## Architecture 1: Combinatorial / UDG

- [x] Survey: Polymath16 chronology and current smallest 5-chromatic UDG (dossier at `docs/research_atlas/arch1_sat_lineage.md`)
- [x] Reproduce: SAT-verify de Grey's lineage at 510 / 517 / 529 / 553 / 826 / 1585 vertices (multi-solver agreement, LEARNINGS L3)
- [ ] Explore: targeted constructions toward chi = 6 (Heule-style)
- [x] Field-extension orbit-search framework (e1d) for chi >= 6 via alternate ring extensions
  - [x] Tested 6 alternate rings {Q(sqrt p) : p = 7, 19, 23, 27, 31, 39} with Moser-spindle seed at orbit size 3-6
  - [x] Naive orbit-only search NEGATIVE: rotations don't auto-bind copies (LEARNINGS L11)
  - [x] Binding-rotation enumeration for Moser in Q(sqrt 3, sqrt 11): 16 single, 62 double, 4 triple bindings; full 62-stack is 211-vertex, density 3.46, chi = 4 (e1e/e1f/e1g, LEARNINGS L14)
  - [ ] Repeat binding-rotation enumeration in enriched fields Q(sqrt 3, sqrt 11, sqrt p) for small primes p
- [x] Document SAT encoding conventions and reproducibility (e1a/e1b scripts + cache certificates)
- [x] Reverse-engineer Polymath 510 and de Grey 1585 (e1i-e1t)
  - [x] Polymath 510 has approximate C_6 about origin (92% coverage); C_6 closure is C_6-irreducible at 1155v / chi=5 (e1i/e1j/e1k, LEARNINGS L15)
  - [x] de Grey 1585's natural center is v_0 = (2, 0), approximate D_6 symmetry (~50% coverage per element) (e1l/e1m, LEARNINGS L16)
  - [x] de Grey 1585's chi = 5 obstruction is a three-component coupling: 778v core (chi 4) + 807v asymmetric (chi 4) + 155 bridges (e1n/e1o/e1p/e1q, LEARNINGS L17)
  - [x] de Grey 1585 obstruction is extremely delocalized: every reasonable structural reduction drops chi to 4 (e1r, LEARNINGS L18)
  - [x] Polymath 510 is essentially a translated substructure of de Grey 1585 (62% vertex overlap under T = (2, 0)) (e1s, LEARNINGS L19)
  - [x] Universal "two 4-chromatic halves + bridges" pattern: same mechanism in de Grey 1585 (778+807+155) and Polymath 510 (315+195+833) (e1t, LEARNINGS L20)
  - [x] Covering lemma: chi(H_1 + H_2 + B) >= 5 iff B is a set cover of the 4-coloring product (e1v, LEARNINGS L21)
  - [x] List-coloring reformulation: chi >= 5 iff H_2 not list-colorable from L(v) = [4] \ F(v) (e1w, LEARNINGS L22)
  - [x] L21's 14-vertex Moser² no-K_4 abstract chi-5 graph is NOT UDG-realizable (e1x numerical + h2 Positivstellensatz, LEARNINGS L23)
  - [x] Triple-coupling theorem for chi >= 6 lifts L22 to three halves (e1y, LEARNINGS L24)
  - [x] Four obstruction classes catalogued: W5² 12v adjacent-singleton, W5×Moser global, Moser² empty-list, W5×Golomb sparse-singleton (h3, LEARNINGS L25)
  - [x] Polymath 510 vertex-critical for chi >= 5: all 510 single-removals are 4-colorable (h1 Phase 1, LEARNINGS L26)
  - [ ] Complete H1 Phase 2 pair sweep: resume h1_parts_shave.py from index 56,500 (~2 hours; checkpointed)
  - [ ] Polymath 510 × Polymath 510 + no-K_4 bridges: chi >= 6 search via L24 triple-lift at the 5-color level (next chi-6 UDG target)
  - [ ] Search for 7-vertex 4-chromatic UDG distinct from Moser spindle (would re-open the 14v UDG chi-5 route; L25 future direction 1)
  - [ ] Pair Moser with 8-9-vertex UDGs from e1l (chain/pivot constructions); test no-K_4 chi-5 minima
  - [ ] Apply same-j linear-difference trick (h2) to de Grey 1585 and Polymath 510 bridges as a structural rank check
  - [ ] Lean formalization of the h2 Positivstellensatz certificate (`moser14_not_udg` theorem)
  - [ ] Investigate Haugstrup's R^4 600-cell / 120-cell construction (Polymath16 18th thread Jan 2026); extract graph, run L25 obstruction analysis

## Architecture 2: Measurable / spectral

- [ ] Survey: Falconer 1981 proof of chi_m >= 5
- [ ] Implement autocorrelation / Fourier bound experiments
- [ ] Document recent chi_m >= 6 results and what they require

## Architecture 3: Fractional / Lovász theta

- [ ] Survey: Cranston-Rabern fractional chromatic bounds + Matolcsi-Ruzsa-Varga-Zsámboki 2023 (chi_f >= 4)
- [x] Compute Lovász theta on Polymath16 510: theta = 170.24, loose chi >= 3 only (LEARNINGS L5)
- [x] Basic OFV rotation-invariant Bessel-LP: $m_1 \leq 0.287$, $\chi_m \geq 4$ in 30 ms (LEARNINGS L6)
- [x] Refine basis to match OFV's published $m_1 \leq 0.2688$ (e3c, 3 off-center unit triangles, exact match, LEARNINGS L8)
- [x] Wide-triangle sweep shows triangle inequalities saturate near 0.2682 (e3d, LEARNINGS L9)
- [x] Moser-spindle inequality breaks triangle saturation: $m_1 \leq 0.2619$, $\chi_m \geq 4$ real $\geq 3.82$ (e3e, LEARNINGS L9)
- [x] Shot 1: 5-chromatic UDG (Polymath 510) in LP — NEGATIVE structural result; Bessel sums cancel across spread-out 510 vertices (e3f, LEARNINGS L10)
- [x] Ambrus 2023 IE-LP framework: confirmed 1-particle LP with inclusion-exclusion atoms, NOT a 2-particle SDP (e3g, LEARNINGS L12)
- [x] Beam search over IE-LP configurations: reached $m_1 \leq 0.2584$ at 17 vertices, matches KMOR 2015 (e3h, LEARNINGS L13)
- [ ] Break the 0.258 greedy plateau toward Ambrus 2023 $m_1 \leq 0.2470$ (would give integer $\chi_m \geq 5$):
  - [ ] Beam width >= 2 in e3h (keep top-K branches)
  - [ ] Vertex-swap local search starting from the 17-pt configuration
  - [ ] Restart from alternate seeds (Moser spindle, Heule fragments)
  - [ ] Constructive candidate pool (generate unit-distance neighbors in Q(sqrt 3, sqrt 11) lattice instead of fixed Polymath 510)
- [ ] Reproduce MRVZ chi_f(R^2) >= 4 via their 27-vertex graph + symmetric LP
- [ ] Architecture 3 dossier: docs/research_atlas/arch3_fractional_lp_lineage.md (currently spread across LEARNINGS L5-L13)

## Architecture 4: Set-theoretic / axiomatic

- [ ] Survey: Shelah-Soifer phenomenon (chi in ZF + DC vs ZFC)
- [ ] Document Borel chromatic number landscape

## Lean substrate

- [x] Initialize `lean/` with lakefile + lean-toolchain mirroring zeta repo (v4.13.0 + Mathlib v4.13.0)
- [x] Skeleton modules: `HadwigerNelson.Basic` (UDG type, chromatic number), `HadwigerNelson.MoserSpindle`, `HadwigerNelson.Controls`
- [x] `lake update` + `lake exe cache get` + `lake build` end-to-end (1859/1859 modules, commit 3b82e91)
- [x] `unitDistanceGraph_adj` lemma proved (clean iff via `rw [SimpleGraph.fromRel_adj]` + dist_comm)
- [x] Fill in HN-2a `moserSpindle.Colorable 4` (proved via e1a witness + per-edge decide)
- [x] Fill in HN-2b `¬ moserSpindle.Colorable 3` (proved via native_decide over $3^7$ functions)
- [x] Fill in HN-2c `moserSpindle.chromaticNumber = 4` (glued via `Nat.sInf_upward_closed_eq_succ_iff` and `Colorable.mono`)
- [x] Fill in HN-2d bridge `moserSpindle` to `planeUnitDistanceGraph` — `four_le_chromaticNumberOfPlane` proved (commit pending)
- [x] L21 covering lemma formalized (`lean/HadwigerNelson/L21CoveringLemma.lean`, h4 VERIFIER, zero sorries)
- [x] L22 list-coloring theorem formalized (`lean/HadwigerNelson/L22ListColoring.lean`, h4 VERIFIER, zero sorries, `L21_iff_L22` proved)
- [x] Bridge graph definitions formalized (`lean/HadwigerNelson/Bridges.lean`)
- [ ] Fill in HN-5 Q^2 chi = 2 (Woodall parity argument; predicate already over ℚ so should be tractable)
- [ ] Fill in HN-6 L^infty chi = 4 (Chilakamarri construction)
- [ ] L23 h2 Positivstellensatz certificate formalization: `moser14_not_udg` theorem
- [ ] L24 triple-lift theorem formalization (3-half chi >= 6 form)
- [ ] Concrete instantiation: `bridgeGraph moserSpindle moserSpindle B_14` chromatic = 5 via L22 + `native_decide` (H4 noted out-of-scope)

## Cross-cutting

- [x] Decide on agent role spec strategy: copy from zeta repo verbatim, or adapt (adapted)
- [x] Six agent specs written under `.claude/agents/` (surveyor, builder, verifier, adversary, synthesizer, orchestrator)
- [x] First session record landed at `experiments/orchestrator_sessions/session_001_bootstrap.md`
- [x] Write `docs/research_atlas/README.md` master landscape
- [x] Write `experiments/PROOF_ARCHITECTURES_PLAN.md`
