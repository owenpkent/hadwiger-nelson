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
- [x] Write `experiments/combinatorial/e1b_de_grey_skeleton.py` cadical195 + glucose4 agree on UNSAT for 510 / 517 / 529 / 553 / 826; 1585 in progress

## Architecture 1: Combinatorial / UDG

- [x] Survey: Polymath16 chronology and current smallest 5-chromatic UDG (dossier at `docs/research_atlas/arch1_sat_lineage.md`)
- [x] Reproduce: SAT-verify de Grey's lineage at 510 / 517 / 529 / 553 / 826 vertices (de Grey 1585 in progress)
- [ ] Explore: targeted constructions toward chi = 6 (Heule-style)
- [ ] Field-theoretic search direction (LEARNINGS L1): which closed-under-rotation rings refuse 5-colorings
- [x] Document SAT encoding conventions and reproducibility (e1a/e1b scripts + cache certificates)

## Architecture 2: Measurable / spectral

- [ ] Survey: Falconer 1981 proof of chi_m >= 5
- [ ] Implement autocorrelation / Fourier bound experiments
- [ ] Document recent chi_m >= 6 results and what they require

## Architecture 3: Fractional / Lovász theta

- [ ] Survey: Cranston-Rabern fractional chromatic bounds + Matolcsi-Ruzsa-Varga-Zsámboki 2023 (chi_f >= 4)
- [x] Compute Lovász theta on Polymath16 510: theta = 170.24, loose chi >= 3 only (LEARNINGS L5)
- [ ] Implement OFV / BNOFV rotation-invariant SDP framework (the right relaxation per L5)
- [ ] Reproduce MRVZ chi_f(R^2) >= 4 via their 27-vertex graph + symmetric LP

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
- [ ] Fill in HN-5 Q^2 chi = 2 (Woodall parity argument; predicate already over ℚ so should be tractable)
- [ ] Fill in HN-6 L^infty chi = 4 (Chilakamarri construction)

## Cross-cutting

- [x] Decide on agent role spec strategy: copy from zeta repo verbatim, or adapt (adapted)
- [x] Six agent specs written under `.claude/agents/` (surveyor, builder, verifier, adversary, synthesizer, orchestrator)
- [x] First session record landed at `experiments/orchestrator_sessions/session_001_bootstrap.md`
- [x] Write `docs/research_atlas/README.md` master landscape
- [x] Write `experiments/PROOF_ARCHITECTURES_PLAN.md`
