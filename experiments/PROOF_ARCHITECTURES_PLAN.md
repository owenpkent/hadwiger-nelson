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
| e2a Falconer baseline | 2 | not started |
| e2b autocorrelation | 2 | not started |
| e2c Fourier avoidance | 2 | not started |
| e3a fractional small | 3 | not started (subsumed by e3a Lovász theta below) |
| e3a Lovász $\vartheta$ on Polymath16 510 | 3 | done; $\vartheta = 170.24$, loose chi >= 3 (LEARNINGS L5) |
| e3b OFV Bessel-LP for $m_1(\mathbb{R}^2)$ | 3 | done; $m_1 \leq 0.287$ giving $\chi_m \geq 4$ in 30 ms via cvxpy + HiGHS (LEARNINGS L6) |
| e3c OFV multi-simplex LP for $m_1(\mathbb{R}^2)$ | 3 | done; $m_1 \leq 0.268412$ giving $\chi_m \geq 4$ (real $\geq 3.73$) via 3 off-center unit triangles, exact match to OFV 2010 Table 3.1 (LEARNINGS L8) |
| e3d wide-triangle sweep | 3 | done; 1409 candidate triples on $0.1$-grid saturates near 0.2682; triangle class exhausted (LEARNINGS L9) |
| e3e Moser-spindle LP inequality | 3 | done; $m_1 \leq 0.2619$ via Moser-spindle ($N=7, \alpha=2$) translations + OFV triangles, closes 75% of OFV-to-KMOR gap; $\chi_m \geq 4$ (real $\geq 3.82$) (LEARNINGS L9) |
| e3f Polymath 510 in LP (Shot 1) | 3 | done; structural negative, LP ignores Polymath 510 constraint due to Bessel-sum cancellation across 510 vertices (LEARNINGS L10) |
| e3g Ambrus inclusion-exclusion LP framework | 3 | done; implemented IE-LP. Moser 0.283, hex 2-layer 0.276, Moser+hex 0.272. Single-config bounds limited; LEARNINGS L12 |
| e3h IE-LP beam search over Polymath 510 pool | 3 | done; m_1 $\leq$ 0.2584 at 17 vertices, matches KMOR 2015 (0.2588). Plateau at greedy width 1 (LEARNINGS L13) |
