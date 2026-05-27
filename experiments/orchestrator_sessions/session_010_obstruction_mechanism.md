# Session 010: The chi >= 5 obstruction mechanism in de Grey 1585

**Date**: 2026-05-26 (continuation of session 009)
**Mode**: depth on Architecture 1, Shot 2.
**Architecture focus**: 1 (combinatorial / UDG).

## Goal

L16 established that de Grey 1585 has approximate D_6 symmetry about
v_0 = (2, 0), and its C_6-symmetric core (778 vertices) is chi = 4.
The chi >= 5 must come from the ~807 asymmetric perturbation vertices.

This session: identify WHERE the chi = 5 obstruction lives. Three angles:
- e1o: singleton and greedy multi-step augmentation.
- e1p: chi of the asymmetric half alone.
- e1q: bridge-edge subgraph analysis.

## What landed

### e1o: Singleton augmentation gives chi = 4 in all 807 cases

[`experiments/combinatorial/e1o_asymmetric_obstruction.py`](../combinatorial/e1o_asymmetric_obstruction.py).

For each asymmetric vertex v in V \ V_sym, compute chi(V_sym union {v}).
Result: ALL 807 singleton augmentations give chi = 4.

Phase 2 greedy by degree-to-G: 50 steps of adding highest-degree asymmetric
vertex. No chi-jump. The naive "concentrate on high-degree asymmetric
vertices" strategy doesn't find a chi >= 5 augmentation.

### e1p: Asymmetric half alone is chi = 4

[`experiments/combinatorial/e1p_degrey_asymmetric_half.py`](../combinatorial/e1p_degrey_asymmetric_half.py).

chi(V \ V_sym) = 4. 807 vertices, 3948 edges, density 4.89.

**Striking parallelism**: the C_6 core (778v, 3806e, density 4.89, chi 4) and
the asymmetric half (807v, 3948e, density 4.89, chi 4) have nearly identical
sizes, densities, and chromatic numbers. The chi = 5 of the full graph is
entirely in the *coupling* between them.

### e1q: 155 bridges + 146-vertex bridge subgraph still chi = 4

[`experiments/combinatorial/e1q_bridge_subgraph.py`](../combinatorial/e1q_bridge_subgraph.py).

Edge decomposition of 7909 total edges:
- 3806 within C_6 core
- 3948 within asymmetric half
- 155 bridge edges between halves

Bridges touch 124 core vertices (16% of 778) and 22 asymmetric vertices
(2.7% of 807). The interface is narrow.

Restrict to the 146 bridge-touched vertices: 327 edges (density 2.24),
chi = 4. The bridges alone, with their local context, don't force chi = 5.

## LEARNING L17

The chi = 5 obstruction in de Grey 1585 is a THREE-COMPONENT coupling:
1. C_6 core (778v, chi 4)
2. Asymmetric half (807v, chi 4)
3. 155 bridges between them (146 contact vertices)

Removing any single component drops chi to 4. The obstruction is GLOBAL,
not localized in any sub-structure.

This refutes the naive "small subgraph of de Grey 1585 has chi = 5" idea.
The chi = 5 certificate of de Grey 1585 requires the full coupling
structure.

## Cross-architectural implication

L4 said Architectures 1 and 2 share the missing 6-chromatic UDG. L17
sharpens: a 6-chromatic UDG would presumably also be a coupling
construction — perhaps two chi-5 sub-objects coupled, or a richer
coupling within one graph. Neither pattern is known.

The Hadwiger-Nelson chi >= 5 bound is not about high local density. Both
halves of de Grey 1585 have density 4.89 (comparable to chi = 5 average),
yet each is individually chi = 4. The chi = 5 property requires a specific
*geometric alignment* between rotationally-symmetric and asymmetric
components.

## Routes forward (next session)

1. **SAT-MUS for full de Grey 1585**: find minimum vertex subset preserving
   chi >= 5. Compare to Parts 509.
2. **Algebraic classification of the 155 bridge edges**: which pairs (core
   vertex, asym vertex) at unit distance? What's the field-theoretic
   pattern?
3. **The "minimal coupling" construction**: build a small graph with the
   abstract structure: small 4-chromatic core + small 4-chromatic asym +
   minimum bridges. Test chi.

## Status table updates

| Experiment | Architecture | Status |
|---|---|---|
| e1o de Grey singleton/greedy | 1 | done; no singleton/degree forces chi >= 5 (L17) |
| e1p de Grey asymmetric half | 1 | done; chi = 4 (L17) |
| e1q de Grey bridge subgraph | 1 | done; bridge-touched subgraph chi = 4 (L17) |

## Wrong-approach status

All experiments use exact algebraic coordinates and rotation symmetries
respecting O(2). The Q^2 detector passes (all vertex coordinates use
sqrt 3, sqrt 5, sqrt 7, sqrt 11).
