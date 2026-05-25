# TODO

Task tracker for the Hadwiger-Nelson research repo.

## Bootstrap (scaffold landed 2026-05-25)

- [ ] Write `docs/00_intuitive/what_is_the_problem.md` — accessible exposition
- [ ] Write `docs/01_undergraduate/moser_spindle.md` — first chi >= 4 proof
- [ ] Write `docs/01_undergraduate/hexagonal_upper_bound.md` — Isbell tiling
- [ ] Implement `experiments/_shared/unit_distance_graph.py` — core UDG class
- [ ] Implement `experiments/_shared/wrong_approach_detectors.py` — Q^2 + L-infinity controls
- [ ] Implement `experiments/_shared/smoke_test.py` — sanity check on Moser spindle and small UDGs
- [ ] Write `experiments/combinatorial/e1a_moser_spindle.py` — verify chi(Moser) = 4 via SAT
- [ ] Write `experiments/combinatorial/e1b_de_grey_skeleton.py` — load de Grey graph data, verify chi >= 5

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

- [ ] Initialize `lean/` with elan + lakefile mirroring the zeta repo's Phase 1 substrate
- [ ] Define UDG type and chromatic_number in Lean
- [ ] Formalize Moser spindle chi = 4 as VERIFIER target 1

## Cross-cutting

- [ ] Decide on agent role spec strategy: copy from zeta repo verbatim, or adapt
- [ ] Set up `orchestrator_sessions/` continuity protocol
- [ ] Write `docs/research_atlas/README.md` master landscape
- [ ] Write `experiments/PROOF_ARCHITECTURES_PLAN.md`
