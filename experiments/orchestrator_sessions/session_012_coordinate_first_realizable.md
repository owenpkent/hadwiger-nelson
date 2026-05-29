# Session 012: Coordinate-first realizable chi-6 coupling (Shot 2)

**Date**: 2026-05-29
**Architecture focus**: 1 (combinatorial / UDG), Shot 2.
**Outcome**: clean negative, dual-solver-confirmed; the cocircularity barrier sharpened into a stronger structural statement (LEARNINGS L34).

## What this session did

Took a serious, disciplined shot at Shot 2 (a finite UDG with chi >= 6) via two thrusts:

- **Thrust (coordinate-first realizable coupling)**: the novel response to the L23/L27/L28/L29 cocircularity barrier. Build the coupling COORDINATE-FIRST so realizability holds by construction (two real plane UDGs joined only by genuine exact unit-distance cross-pairs), then SAT-check chi >= 6. Scripts h7, h7b, h7d.
- **Thrust 2c (field enlargement on a chi-5 seed)**: binding rotations on Heule-553 introducing sqrt 7, sqrt 19, sqrt 23, sqrt 15. Script h7c.

Both returned NEGATIVE. No chi-6 UDG. The likely outcome (chi(R^2) may = 5).

## The decisive results

| Experiment | Construction | Bridges | chi verdict |
|---|---|---:|---|
| h7 (2-copy, 60-deg rot) | P_510 + rot60(P_510) | 4378 | 5-colorable (exceeds abstract L27 |B|=2700) |
| h7 (2-copy, translate (1,0)) | P_510 + P_510 + t | 2697 | 5-colorable (= abstract L27 count) |
| h7b (3-way 60-deg ORBIT) | P_510 at 0,60,120 deg | 13757 | 5-colorable, dual-solver, 0.06-0.13s |
| h7c (field-enlarge 553) | Heule-553 + binding-rot | 72-1473 | 5-colorable, sub-100ms |
| h7d (adversarial subset) | adversarial greedy on realizable pool | up to 2325 | 5-colorable, 12 rounds |

## The structural finding (L34)

Realizability forces an EVEN, low-concentration bridge layout (max bridge-degree ~36, all vertices touched). The chi-6 list-coloring obstruction (L24/L27) needs CONCENTRATION (L27 abstract: max source degree 268 on hubs). The embeddable bridge supply is the wrong SHAPE for chi-6 forcing, not the wrong COUNT. Even adversarial selection from the realizable pool cannot recover the concentration. This explains why no chi-6 UDG has emerged from the de Grey / Polymath lineage at scale.

The c2=c1 identical-coloring test (Cadical UNSAT in 0.0s for rot60) confirms the realizable bridges DO couple the copies non-trivially, like the abstract construction; they just admit a distinct-coloring escape that the concentrated abstract bridges close off.

## Discipline confirmed

- EXACT arithmetic: every bridge verified dist^2 == 1 via numpy prefilter then sympy simplify. P_510 coords parsed from sources/cnp-sat/vtx/510.vtx (Mathematica format), confirmed |v0 v1|^2 = 1 exact.
- Dual-solver: Cadical195 + Glucose4 agree (the orbit graph 5-colorability independently re-confirmed with Glucose, 0.06s).
- omega <= 3: no K_4 in any construction (exhaustive check).
- Wrong-approach detectors: PASS on Q^2 (chi=2), L^inf (chi=4), R^1 (chi=2), run inline. The construction does not collapse onto Q^2 because bridges are irrational Euclidean unit distances.
- SAT budget: every instance resolved fast (< 0.2s for unions; h7d capped at 2M conflicts/probe). No budget-limited indeterminacy. The negatives are decisive.
- All graphs persisted to experiments/combinatorial/_cache/h7*.json BEFORE SAT.

## Did Shot 2 move?

Not toward a positive. But the negative is new and sharper than the cocircularity barrier: L23/L27/L28/L29 showed specific abstract constructions fail to embed; L34 shows that building realizable-by-construction and probing the ENTIRE achievable bridge supply (up to 13,757 bridges, 5x the abstract requirement, plus adversarial subsets, plus enlarged fields) STILL cannot reach chi-6. The barrier is "the embeddable bridge supply is the wrong shape," not "we haven't found the right embedding."

## Files

- experiments/combinatorial/h7_coordinate_first.py
- experiments/combinatorial/h7b_orbit_coupling.py
- experiments/combinatorial/h7c_field_enlarge_seed.py
- experiments/combinatorial/h7d_realizable_adversarial.py
- experiments/combinatorial/_cache/h7_coordinate_first.json, h7b_orbit_coupling.json, h7c_field_enlarge_seed.json, h7d_realizable_adversarial.json
- experiments/combinatorial/_cache/h7*_graph.json (persisted candidate graphs)
- experiments/LEARNINGS.md (L34 at top)
- experiments/SOLVING_PROGRAM.md (session update 2026-05-29b + Shot 2 status row)

## Next session plan

Portfolio: Arch 1 has now closed both the abstract-coupling reduction (L29/L30) AND the coordinate-first realizable thrust (L34). The chi-6 UDG search via the P_510 / 553 lineage is exhausted across in-field rotations, enlarged-field rotations, full and adversarial realizable bridge supplies.

Recommended deployments (in priority order):
1. **(Low EV, cheap, finish-the-sweep)**: repeat h7 with de Grey 1585 and Heule 826 as the base copy, on the chance a denser seed gives concentrated realizable bridges. Runs in minutes. If it also spreads evenly, the lineage-wide "even-spread" pattern is fully documented.
2. **REBALANCE toward Arch 2/3**: the missing object (chi-6 UDG that embeds) is the same blocker for chi_m >= 6 (L31-L33). Arch 1 has been the dominant focus for many sessions; Arch 2 (Falconer rigidity at chi-5) and Arch 3 (Ambrus 23-point / OFV LP) have open engineering threads (Shot 3, Shot 5'). Consider a SURVEYOR + BUILDER pass there.
3. **Lean (Shot 4)**: the L24 triple-coupling is machine-checked; the next Lean target is the de Grey chi >= 5 DRAT/LRAT checker. Long lead, conceptually clean, immune to the chi-6 elusiveness.

Falsifiability trigger: Shot 2's coordinate-first thrust is CLOSED for the P_510/553 lineage (L34). The implicit trigger "if realizable-by-construction couplings across in-field and enlarged-field rotations plus adversarial subsets cannot force chi-6, the lineage cannot supply a chi-6 UDG by coupling" is met. Continuing to couple lineage halves is a documented dead end. Any future chi-6 UDG attempt needs a genuinely new chi-5 building block with concentrating self-unit-distance structure (none known).

No escalation to Owen required: no positive claim, no disproof of a known result.
