# TODO

Task tracker for the Hadwiger-Nelson research repo.

## Bootstrap (scaffold landed 2026-05-25)

- [x] Write `docs/00_intuitive/what_is_the_problem.md` accessible exposition
- [x] Write `docs/01_undergraduate/moser_spindle.md` first chi >= 4 proof
- [x] Write `docs/01_undergraduate/hexagonal_upper_bound.md` Isbell tiling
- [x] Implement `experiments/_shared/unit_distance_graph.py` core UDG class
- [x] Implement `experiments/_shared/wrong_approach_detectors.py` Q^2 + L-infinity controls
- [x] Implement `experiments/_shared/smoke_test.py` sanity check on Moser spindle and small UDGs
- [ ] Write `experiments/combinatorial/e1a_moser_spindle.py` verify chi(Moser) = 4 via SAT
- [ ] Write `experiments/combinatorial/e1b_de_grey_skeleton.py` load de Grey graph data, verify chi >= 5

## Architecture 1: Combinatorial / UDG

- [ ] Survey: Polymath16 chronology and current smallest 5-chromatic UDG
- [ ] Reproduce: SAT-verify de Grey's 1581-vertex graph chi >= 5
- [ ] Explore: targeted constructions toward chi = 6 (Heule-style)
- [ ] Document SAT encoding conventions and reproducibility

## Architecture 2: Measurable / spectral

- [ ] Survey: Falconer 1981 proof of chi_m >= 5
- [ ] Implement autocorrelation / Fourier bound experiments
- [ ] Document recent chi_m >= 6 results and what they require

## Architecture 3: Fractional / Lovász theta

- [ ] Survey: Cranston-Rabern fractional chromatic bounds
- [ ] Compute chi_f on small UDGs via LP
- [ ] Explore Lovász theta on graph powers of UDGs

## Architecture 4: Set-theoretic / axiomatic

- [ ] Survey: Shelah-Soifer phenomenon (chi in ZF + DC vs ZFC)
- [ ] Document Borel chromatic number landscape

## Lean substrate

- [x] Initialize `lean/` with lakefile + lean-toolchain mirroring zeta repo (v4.13.0 + Mathlib v4.13.0)
- [x] Skeleton modules: `HadwigerNelson.Basic` (UDG type, chromatic number), `HadwigerNelson.MoserSpindle`, `HadwigerNelson.Controls`
- [ ] Install elan on this Windows machine and run `lake update` + `lake build` to confirm the substrate compiles
- [ ] Fill in HN-2 Moser spindle chi = 4 (replace stub with explicit vertices and proof)
- [ ] Fill in HN-5 Q^2 chi = 2 (Woodall parity argument)
- [ ] Fill in HN-6 L^infty chi = 4 (Chilakamarri construction)

## Cross-cutting

- [x] Decide on agent role spec strategy: copy from zeta repo verbatim, or adapt (adapted)
- [x] Six agent specs written under `.claude/agents/` (surveyor, builder, verifier, adversary, synthesizer, orchestrator)
- [ ] Set up `orchestrator_sessions/` continuity protocol
- [x] Write `docs/research_atlas/README.md` master landscape
- [x] Write `experiments/PROOF_ARCHITECTURES_PLAN.md`
