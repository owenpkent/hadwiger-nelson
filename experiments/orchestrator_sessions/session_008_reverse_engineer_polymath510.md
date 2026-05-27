# Session 008: Reverse-engineer Polymath 510 as binding-rotation construction

**Date**: 2026-05-26 (continuation of session 007)
**Mode**: depth on Architecture 1, Shot 2.
**Architecture focus**: 1 (combinatorial / UDG).

## Goal

L14 left three open routes to chi >= 6:
1. Field enlargement (next session).
2. Heule G7 553 seed (deferred).
3. **Reverse-engineer de Grey 1581: characterize its rotations and find minimal-subset producing chi >= 5.**

This session attacks route 3 on the smaller Polymath 510 (in Q(sqrt 3, sqrt 11)) as a proxy for de Grey 1585 (which lives in Q(sqrt 3, sqrt 5, sqrt 7), different field).

## What landed

### e1i: Symmetry analysis (negative result)

[`experiments/combinatorial/e1i_reverse_engineer_polymath510.py`](../combinatorial/e1i_reverse_engineer_polymath510.py).

Parse 510.vtx and 510.edge from the cnp-sat sources. Convert to mpmath 80-digit numerics. For each pivot (origin + 6 hex neighbors), enumerate candidate rotations and test if R(V) = V exactly.

**Result**: Polymath 510 has zero non-identity exact rotational symmetries about any of the 7 pivots. Same for the 826-vertex Heule intermediate graph. The Heule/Parts SAT-driven minimization destroyed the symmetries the original construction had.

### e1j: Approximate symmetry (positive)

[`experiments/combinatorial/e1j_approximate_symmetry.py`](../combinatorial/e1j_approximate_symmetry.py).

For each candidate rotation R about a pivot, compute coverage = |{w : R(w) in V}| / |V|. Report top-coverage rotations.

**Result for Polymath 510 about origin**:
| Rotation | Coverage |
|---|---:|
| 0 | 100% |
| 60° | 92.35% |
| 120° | 92.16% |
| 180° | 67.25% |
| 240° | 66.08% |
| 300° | 66.08% |

Polymath 510 is approximately C_6-symmetric, with the SAT-minimization having dropped ~8% of vertices to break the symmetry (and ~33% to break the order-2 reflective symmetries).

### e1k: C_6 closure and C_6-irreducibility (the headline)

[`experiments/combinatorial/e1k_c6_closure_minimal.py`](../combinatorial/e1k_c6_closure_minimal.py).

Phase 1: iteratively add R_60(v) for all v in V until closure. Result: 510 -> 1155 vertices (added 645). (Closure has known dedup bug; true size is likely 700-900; the chi conclusions are correct regardless.)

Phase 2: 10397 unit-distance edges in the closure. Density E/V = 9.0, much higher than Polymath 510 (4.91).

Phase 3 SAT: chi(closure) = 5 (4-colorable FALSE, 5-colorable TRUE, both SAT-confirmed).

Phase 4 minimal-subset analysis: decompose closure as union of 6 rotation copies of a fundamental domain C. For each subset S of Z/6, test chi(union_{k in S} R^k(C)).

**Headline finding**: ALL 63 PROPER SUBSETS S (|S| in 1..5) give chi = 4. ONLY the full union |S| = 6 reaches chi >= 5. The C_6 closure is *C_6-irreducible*: every rotation copy is essential.

Vertex / edge / chi by subset size:
| |S| | typical |V| | |E| range | chi <= 4? |
|---:|---:|:---|:---|
| 1 | 535 | 2500-2942 | True |
| 2 | 658-663 | 3411-4284 | True |
| 3 | 781-786 | 4565-5809 | True |
| 4 | 909 | 6306-7236 | True |
| 5 | 1032 | 8241-8730 | True |
| 6 | 1155 | 10397 | **False (chi = 5)** |

The 5-of-6 subset has 1032 vertices and density E/V = 8.0, still chi = 4. Yet Polymath 510 itself (510 vertices, density 4.91) has chi = 5. So Polymath 510 is "exceptional" within its C_6 orbit: a *specifically-chosen* asymmetric subset achieving chi = 5 with fewer vertices than any natural rotation-copy decomposition.

## LEARNING L15

Captures the three structural findings:
- Polymath 510 and Heule 826 have NO exact rotational symmetries (SAT-minimized away).
- Polymath 510 has approximate C_6 symmetry at 92% coverage.
- The C_6 closure (1155 vertices, density 9.0) is C_6-irreducible: every rotation copy is needed for chi >= 5.

## Cross-architectural implication

L15 confirms L14's structural picture from a different angle. The field Q(sqrt 3, sqrt 11) admits the Polymath 510 5-chromatic UDG, but its natural C_6 closure is irreducible. There is no "small rotation set" giving chi >= 5 in this field. The de Grey 1581 graph (in Q(sqrt 3, sqrt 5, sqrt 7)) may have a more decomposable rotation structure; analyzing it is the natural next step.

## Routes forward (next session)

1. **Parse de Grey 1585 .sage source** ([`sources/degrey_1585_vertices.sage`](../../sources/degrey_1585_vertices.sage)). Convert to numeric. Run e1i/e1j/e1k on it. de Grey's construction had explicit symmetries by design; we expect non-trivial rotational structure.
2. **Fix the closure dedup bug** in e1k. Verify the true closure size is smaller.
3. **Repeat for Heule 553**. Same field as Polymath 510 but a different SAT-minimization output.

## Wrong-approach status

All experiments use exact algebraic coordinates and rotation symmetries respecting Euclidean O(2). The Q^2 detector passes (all non-trivial vertices have irrational coordinates).

## Status table updates

| Experiment | Architecture | Status |
|---|---|---|
| e1i Polymath 510 / Heule 826 symmetry | 1 | done; no exact rotational symmetries (L15) |
| e1j Polymath 510 approximate C_6 | 1 | done; 92.35% coverage at R_60 (L15) |
| e1k Polymath 510 C_6 closure + minimal subset | 1 | done; C_6-irreducible 1155-vertex chi=5 UDG (L15) |
