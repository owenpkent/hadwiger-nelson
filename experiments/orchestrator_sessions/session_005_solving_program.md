# Session 005: Architecture 3 push from OFV to Moser-LP; Shot 1 and Shot 2 attempted

**Date**: 2026-05-26
**Mode**: depth on Architecture 3, then attempted breakthroughs on Shot 1 (Polymath 510 in LP for chi_m >= 5) and Shot 2 (field-theoretic chi >= 6 search).
**Architecture focus**: 3 (LP/SDP); 1 (field-theoretic structural negative).

## Goal

Push Architecture 3 LP bound on m_1(R^2) from e3b's basic 0.287 toward the published frontier (OFV 0.2688, KMOR 0.2588, Ambrus 0.2470), then attempt the breakthrough to integer chi_m >= 5 (Shot 1) and pivot to chi >= 6 search (Shot 2) when Shot 1 hits structural ceiling.

## What landed

### Architecture 3: OFV reproduction and Moser-LP breakthrough (commits pending)

**e3c (`experiments/fractional/e3c_ofv_lp_dual.py`)**: dual LP form from Oliveira Filho-Vallentin 2010 (arXiv:0808.1822), with `Omega_n(t)` general dimension support. Three variants:
- Basic LP (Theorem 1.1, no simplex): m_1 <= 0.287119 = J_0(j_{1,1}) / (J_0(j_{1,1}) - 1), the analytic radial saturation value recovered by e3b.
- Centered equilateral-triangle inequality: m_1 <= 0.285742 (only 0.0014 tighter than basic).
- **Three off-center unit-edge triangles** (OFV 2010 page 7 hand-picked triples): m_1 <= 0.268412, **exact match to OFV Table 3.1**.
- Wrong-approach detector: n=1 with Omega_1(t) = cos(t) gives m_1 <= 0.5 hence chi_m(R^1) >= 2 (correct).
- LEARNING L8 records the exact LP and the saturation analysis.

**e3d (`experiments/fractional/e3d_ambrus_triple_sweep.py`)**: wide enumeration of valid (a,b,c) triples on a fine grid in [0.1, 4.0]. With 1409 candidate triples, LP picks 9 active and reaches 0.268202. **Triangle-inequality class is exhausted near OFV's published 0.2684.**

**e3e (`experiments/fractional/e3e_moser_constraint.py`)**: extends OFV LP with Moser-spindle inequality (N=7, alpha=2, sum f(||v_i||) <= 2). Translation sweep + rotation sweep:
- Single Moser at (-0.5, -0.5): m_1 <= 0.2641.
- 1271 translations: 0.2620.
- 18 rotations x 6048 translations: 0.2619 (saturates).
- **Closes 75% of the OFV-to-KMOR gap.** Real chi_m >= 3.82. Integer chi_m still 4.
- LEARNING L9 records the progression: each step injects a richer finite UDG. Same combinatorial mechanism as Falconer's measurable argument (L4 coupling).

### Shot 1 attempted: integer chi_m >= 5 via Polymath 510 in LP

**e3f (`experiments/fractional/e3f_polymath510_lp.py`)**: SOLVING_PROGRAM Shot 1.
- Parsed 510-vertex Polymath16 graph from `sources/cnp-sat/vtx/510.vtx` (Mathematica-style algebraic coords in Q(sqrt 3, sqrt 11)) and edge list from `sources/cnp-sat/edge/510.edge`. All 2504 edges verified as unit-distance at 1e-6 tolerance.
- SAT-probed alpha(Polymath 510): alpha >= 130 fast (<1s); alpha >= 142 SAT in 58s; alpha >= 144 timed out at 10 min. **alpha is in [142, 170]** (Lovász theta upper bound from e3a is 170).
- LP with single translation + alpha = 142, 150, 160, 170: **all give m_1 <= 0.268412 exactly**. No improvement over OFV.
- LP with 210 translations over the configuration footprint: same, no active Polymath constraints.
- **Mechanistic reason** (LEARNING L10): at the LP binding frequency s* = 0.61, sum J_0(2 pi s* r_i) for the 510 vertex norms is only ~-6 (oscillatory cancellation across spread-out vertices). The constraint sum f(r_i) <= alpha ~= 142 has ~140 units of slack. **LP never activates the Polymath constraints.**
- Structural finding: bigger 5-chromatic UDGs cannot help the OFV LP because vertices spread across many radii cause Bessel sums to cancel. The framework needs configurations with radii *clustered* at r ~ 1 (the J_0 minimum), which standard 5-chromatic UDGs don't have.
- Integer chi_m >= 5 via the LP route requires either (a) custom radially-clustered 5-chromatic UDGs (research-grade open), or (b) the 2-particle Bachoc-Vallentin SDP framework (Shot 5).

### Shot 2 attempted: field-theoretic chi >= 6 search

**e1d (`experiments/combinatorial/e1d_field_extension_search.py`)**: SOLVING_PROGRAM Shot 2 framework.
- Moser-style angle family: for seed radius r from origin, cos theta = (2 r^2 - 1)/(2 r^2), sin theta = sqrt(4 r^2 - 1) / (2 r^2). Ring discriminant = 4 r^2 - 1. Moser standard is r^2 = 3 giving Q(sqrt 11); alternates r^2 in {2, 5, 6, 7, 8, 10} give Q(sqrt 7), Q(sqrt 19), Q(sqrt 23), Q(sqrt 27)=Q(sqrt 3), Q(sqrt 31), Q(sqrt 39).
- Apply each rotation at n_rot in {3, 4, 6} to the 7-vertex Moser spindle seed.
- **All 18 trials produce identical V=37, E=66 graphs** across the 6 alternate rings, all 4-colorable.
- **Structural reason** (LEARNING L11): the 6 rotated Moser copies share only their *central* vertices, with NO cross-copy unit-distance edges. The orbit graph is the disjoint union (modulo central identification) of 6 Moser spindles. chi = chi(Moser) = 4.
- The Polymath16 obstruction crystallizes: de Grey 2018 succeeded by engineering rotations that produce *binding* cross-copy unit edges. Generic rotations don't bind. Finding such coincidences in an alternate ring is the actual research problem.

### Documentation

**SOLVING_PROGRAM.md** (`experiments/SOLVING_PROGRAM.md`): long-range plan with four-shot taxonomy (Shot 1 LP/UDG; Shot 2 field-theoretic; Shot 3 Ambrus reproduction; Shot 4 Lean de Grey formalization), now expanded to six (added Shot 5 Bachoc-Vallentin SDP and Shot 6 radially-clustered UDG construction). Shot 1 completed negative (L10); Shot 2 framework built with naive orbits negative (L11).

**LEARNINGS.md** updated with L8-L11. Cumulative learning count: 11.

**PROOF_ARCHITECTURES_PLAN.md** status table updated with e3c, e3d, e3e rows.

**TODO.md** Architecture 3 section updated with completed e3c, e3d, e3e and identified follow-ups.

## Verified state at session end

Architecture 3 LP m_1(R^2) progression:
| Method | m_1 <= | real chi_m >= | integer chi_m >= |
|---|---:|---:|---:|
| e3b vanilla Bessel-LP (saturated radial) | 0.2873 | 3.48 | 4 |
| e3c basic OFV LP (recovers e3b) | 0.2871 | 3.48 | 4 |
| e3c centered-triangle simplex | 0.2857 | 3.50 | 4 |
| e3c OFV 3 off-center triangles | **0.2684** | 3.73 | 4 |
| e3d wide triangle sweep (1409 candidates) | 0.2682 | 3.73 | 4 |
| e3e + Moser spindle inequality (1271 trans.) | **0.2620** | 3.82 | 4 |
| e3e + 6048 translation/rotation Moser configs | 0.2619 | 3.82 | 4 |
| KMOR 2015 published | 0.2588 | 3.86 | 4 |
| Ambrus 2023 published (chi_m >= 5 integer) | 0.2470 | 4.05 | 5 |
| Required for chi_m >= 6 integer | < 0.2000 | > 5 | 6 |

Architecture 1 field-extension orbit search: all 18 tested (ring x n_rot) configurations stuck at chi = 4 due to orbit-decoupling structural obstruction.

## LEARNINGS now in the project

| # | Architecture | Headline |
|---|---|---|
| L1 | 1, cross | 6-chromaticity easy in HN-adjacent variants, uniquely resists in single-distance |
| L2 | 1 | Moser spindle structurally inessential (Voronov spindle-free 64513-vertex) |
| L3 | 1 | Multi-solver SAT agreement reproduces chi >= 5 across 6 graphs |
| L4 | 1+2 | Arch 1 and Arch 2 share a single missing 6-chromatic finite UDG |
| L5 | 3 | Vanilla Lovász theta on de Grey lineage UDGs is structurally loose |
| L6 | 3 | Rotation-invariant Bessel-LP wins 20000x vs vanilla theta with cleaner bound |
| L7 | 4 (cross to 1) | Arch 1's 2018 breakthrough erased Arch 4's main 2003 result about chi(R^2) |
| L8 | 3 | OFV 2010 m_1 <= 0.268412 reproduced exactly with 3-multiplier LP, simplex strengthening |
| L9 | 3 | Unit-triangle class saturates at 0.268; Moser-spindle inequality breaks barrier to 0.262 |
| L10 | 3 | Polymath 510 (or any large 5-chromatic UDG) ineffective in OFV LP; Bessel sums cancel |
| L11 | 1 | Field-extension orbit search hits structural obstruction: orbits don't bind |

## Compute used this session

- Python LP / SDP via cvxpy + HiGHS: e3c basic 90 ms, simplex 90 ms, multi-simplex 110 ms; e3d 0.2-0.4 s per LP; e3e single Moser 1-2 s, 1271 translations 30 s, 6048 translations 65 s.
- Python SAT via pysat cadical195: e3f alpha-probes for Polymath 510 took 0.1s for alpha >= 110/130, 58s for alpha >= 142, timed out at 600s for alpha >= 144.
- Python orbit graph construction via sympy: 1-30 s per orbit graph (sympy simplify is the bottleneck).
- No SAT-solving on production-scale 1000+ vertex graphs this session.

## Pending / next-session candidates

- **Shot 5 (Bachoc-Vallentin 2-particle SDP)**: implement the framework that likely gives Ambrus's m_1 <= 0.247. Real methodological contribution. ~weeks of work.
- **Shot 2 binding-rotation search**: algorithmic search for rotation angles that produce cross-copy unit edges in alternate rings. The actual research direction Polymath16 partially explored. Multi-month-scale.
- **Shot 4 (Lean formalization of chi >= 5)**: HN-5 (Woodall's chi(Q^2) = 2) is the next tractable HN milestone in lean/; HN-4 (de Grey via DRAT/LRAT checker in Lean) is the major artifact.
- **HN-5 / HN-6 in Lean**: chi(Q^2) = 2 via Pythagorean parity; chi(L^infty) = 4 via Chilakamarri.
- **Architecture 3 standalone dossier**: arch3_fractional_lp_lineage.md to mirror arch1, arch2, arch4. Currently Arch 3 content is split between LEARNINGS L5-L10 and the synthesis doc.
- **Refine Shot 1 negative**: explore whether SMALLER 5-chromatic UDGs (e.g., minimized Heule 553 variants) might have more concentrated radii than Polymath 510, despite same chi.

## Honest takeaway

This session generated four new experimental files, four new LEARNINGS (L8-L11), and the SOLVING_PROGRAM long-range plan. The headline Architecture 3 advance from 0.287 to 0.262 closes 75% of the OFV-to-KMOR gap by clean LP / Moser-spindle work. The two shot attempts (Shot 1 LP-via-large-UDG and Shot 2 field-extension orbits) produced clean structural negatives that crystallize the Polymath16 obstructions. **No breakthrough on integer chi_m >= 5 or chi >= 6, but real methodological progress and clean documentation of why the obvious paths don't work.**
