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
- `e2a_falconer_baseline.py` — reproduce Falconer's $\chi_m \geq 5$.
- `e2b_autocorrelation.py` — compute autocorrelation upper bounds.
- `e2c_fourier_avoidance.py` — Fourier-analytic bounds on distance-1-avoiding sets.

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
| e1b de Grey skeleton | 1 | done for 510/517/553/826 (cadical195 + glucose4 agree on UNSAT); 1585 in progress |
| e1c Polymath16 smallest | 1 | not started |
| e1d $\chi \geq 6$ search | 1 | not started |
| e2a Falconer baseline | 2 | not started |
| e2b autocorrelation | 2 | not started |
| e2c Fourier avoidance | 2 | not started |
| e3a fractional small | 3 | not started (subsumed by e3a Lovász theta below) |
| e3a Lovász $\vartheta$ on Polymath16 510 | 3 | done; $\vartheta = 170.24$, loose chi >= 3 (LEARNINGS L5) |
| e3b Lovász $\vartheta$ | 3 | superseded by e3a above |
| e3c Bochner continuous | 3 | not started |
