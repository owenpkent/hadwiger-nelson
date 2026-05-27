# Session 007: Field-theoretic binding-rotation search for chi >= 6 (Shot 2)

**Date**: 2026-05-26 (continuation)
**Mode**: depth on Architecture 1, Shot 2.
**Architecture focus**: 1 (combinatorial / UDG).

## Goal

Execute Shot 2 of SOLVING_PROGRAM as identified by LEARNING L11 (the "actual research problem"): find rotation angles theta in Q(sqrt 3, sqrt 11) such that R_theta(M) produces cross-copy unit-distance edges with the Moser spindle M, and use those rotations to build chi >= 5 or chi >= 6 finite UDGs.

L11 established that NAIVE orbit graphs (rotate M by Moser-style angles in alternate rings) give chi = 4 because rotated copies are disjoint (modulo central identification). The unexplored move was: search systematically for ANGLES that produce cross-copy unit edges (the "de Grey miracle").

## What landed

### e1e: Single binding-rotation enumeration on Moser

[`experiments/combinatorial/e1e_binding_rotation_moser.py`](../combinatorial/e1e_binding_rotation_moser.py).

For each ordered pair (v_i, v_j) of Moser-spindle vertices with v_i not at origin and v_j not at origin, we solve

  <p, q> cos t + det[p|q] sin t = (|p|^2 + |q|^2 - 1) / 2  on cos^2 + sin^2 = 1

for (cos t, sin t). Result: **16 unique single-binding rotations** about origin. Each catches at most 2 cross-copy unit edges. M union R_theta(M) for any of the 16 has |V| in [10, 13], |E| in [17, 24], chi = 4.

Phase 3 (stacking pairs) and Phase 4 (greedy iterative expansion) both fail to break chi = 4. Phase 4 settles into a periodic attractor at E/V ~ 2.27 even out to 19 iterations (|V|=121, |E|=275).

### e1f: Double-binding rotations about origin

[`experiments/combinatorial/e1f_double_binding_search.py`](../combinatorial/e1f_double_binding_search.py).

For each pair of unit-edge constraints {(p_1, q_1), (p_2, q_2)}, solve the 2x2 linear system in (cos t, sin t) uniquely, then check unit-circle compatibility. The unit-circle condition is generically incompatible; double-bindings exist only when the field's algebra permits the accident.

Result: **only 6 double-binding rotations** exist for Moser in Q(sqrt 3, sqrt 11) about origin, and **all 6 are DEGENERATE**: the second binding constraint is satisfied by vertex coincidence (R_theta(p_2) lands on an existing M-vertex), not by a genuinely new cross edge. Cross-edge count = 0 for all 6. The full 6-rotation union has |V|=29, |E|=61, chi = 4.

This is a striking algebraic finding: Q(sqrt 3, sqrt 11) does not admit non-trivial double-binding rotations of the Moser spindle about origin.

### e1g: Pivot-varied double-binding search

[`experiments/combinatorial/e1g_pivot_double_binding.py`](../combinatorial/e1g_pivot_double_binding.py).

Vary the rotation pivot over all 7 Moser vertices. For each pivot, repeat the double-binding enumeration. Total: **62 distinct double-binding rotations** across all 7 pivots. Pivot v_0 (origin) has 6 (degenerate per e1f); pivots v_1, v_2, v_4, v_5 have 11 each; pivots v_3 and v_6 (the outer tips, related by the Moser angle) have 6 each.

Cross-edge multiplicities:
- 0 cross edges: 6 rotations (all at origin, the v_0 set)
- 1 cross edge: 16 rotations (single bindings that became double via a second weak constraint)
- 2 cross edges: 36 rotations
- 3 cross edges: **4 rotations** (the algebraic "triple bindings")

The 4 triple-binding rotations are paired: 2 at pivot v_3 and 2 at pivot v_6, with constraint pair (1,4) + (2,5) and its swap. These are the algebraic miracles for the Moser spindle in Q(sqrt 3, sqrt 11).

**The full union** of all 62 double-binding rotations across all 7 pivots:
- |V| = 211 (after dedup; 7 + 62*7 = 441 raw, ~230 coincidences)
- |E| = 731
- E/V = 3.46 (vs Moser 1.57, vs de Grey 1581's 5.00, Polymath 510's 4.91)
- chi = 4

## LEARNING L14 (committed to LEARNINGS.md)

The field-theoretic rigidity of Q(sqrt 3, sqrt 11) over the Moser spindle is now precisely localized:
- 16 single-binding rotations
- 6 double-binding rotations about origin (all degenerate)
- 62 double-binding rotations across all 7 pivots
- 4 triple-binding rotations
- Full stacked union: 211 vertices, 731 edges, density 3.46, chi = 4

The de Grey "miracle" is much rarer than expected. Reaching chi = 5 from binding rotations alone needs >> 1581 vertices in this field. Reaching chi = 6 needs structurally different objects.

## Routes forward (next session)

1. **Field enlargement**: repeat enumeration in Q(sqrt 3, sqrt 11, sqrt p) for small primes p. Does sqrt 2, sqrt 5, sqrt 7 admit additional triple bindings?
2. **5-chromatic seed**: use Heule G7 (553 vertices, chi = 5) as seed instead of Moser. Find binding rotations of THAT into a chi >= 6 graph.
3. **Reverse-engineer de Grey**: characterize de Grey 1581's rotations as binding rotations; identify the minimal subset producing chi >= 5.

None are closable in a single session. The framework (e1e, e1f, e1g) is the right substrate for all three.

## Status table updates

| Experiment | Architecture | Status |
|---|---|---|
| e1e Moser binding-rotation | 1 | done; greedy plateau at E/V=2.27, chi=4 (L14) |
| e1f Moser double-binding (origin) | 1 | done; 6 rotations all degenerate, chi=4 (L14) |
| e1g Moser double-binding (all pivots) | 1 | done; 62 rotations, 4 triple-binding, 211-vertex union, chi=4 (L14) |

## Wrong-approach status

All experiments respect the Euclidean rotation group O(2) and use irrational coordinates throughout. None lift to Q^2. The Q^2 detector passes uniformly.

## Cross-architectural implication

L14 sharpens L4's coupling: not only do Architectures 1 and 2 share the missing 6-chromatic UDG, but the obstacle is FIELD-THEORETIC. Both architectures are stuck at the chi/chi_m = 5 level until a richer algebraic field admits the rotation miracles needed.
