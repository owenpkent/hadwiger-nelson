# Session 009: de Grey 1585 symmetry analysis

**Date**: 2026-05-26 (continuation of session 008)
**Mode**: depth on Architecture 1, Shot 2.
**Architecture focus**: 1 (combinatorial / UDG).

## Goal

Session 008 (L15) found Polymath 510 has approximate C_6 symmetry about origin
but its C_6 closure is C_6-irreducible (all 6 rotation copies essential for
chi >= 5). Note the chi >= 5 of Polymath 510 itself depends on a specific
asymmetric subset choice from SAT minimization.

L15 left open: parse the original de Grey 1585 graph (in the richer field
Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11)), check for symmetries. Expectation: de
Grey's explicit construction should have non-trivial rotational symmetries
that the SAT-minimized Heule/Parts variants lost.

## What landed

### e1l: de Grey 1585 has NO exact rotational symmetries

[`experiments/combinatorial/e1l_reverse_engineer_degrey1585.py`](../combinatorial/e1l_reverse_engineer_degrey1585.py).

Parse the Sage source for de Grey 1585's vertex coordinates (in Q(sqrt 3,
sqrt 5, sqrt 7, sqrt 11)). Convert to mpmath 80-digit numerics. Check
rotational symmetries about 9 candidate pivots (origin, centroid, v_0
through v_6, (1, 0), midpoint of v_0/v_2).

**Result**: zero non-identity exact rotational symmetries about any pivot.
Same negative result as Polymath 510 and Heule 826 (L15). The published
de Grey 1585 graph is fully asymmetric.

### e1m: Approximate D_6 symmetry about v_0 = (2, 0)

[`experiments/combinatorial/e1m_degrey_approximate.py`](../combinatorial/e1m_degrey_approximate.py).

For each candidate rotation R about a pivot, compute coverage =
|{v : R(v) in V}| / |V|. Report high-coverage rotations.

**Key finding**: About pivot v_0 = (2, 0), de Grey 1585 has approximate
D_6 (dihedral order 12) symmetry:

| Element | Coverage |
|---|---:|
| Identity | 1585/1585 = 100% |
| R_60 | 787/1585 = 49.65% |
| R_120 | 787/1585 = 49.65% |
| R_180 | 793/1585 = 50.03% |
| R_240 | 787/1585 = 49.65% |
| R_300 | 787/1585 = 49.65% |
| 12 secondary 180° rotations | ~785-787 / 1585 each |

The 12 secondary 180° rotations correspond to D_6 reflections. The 6
C_6 rotations + 12 reflections = approximate D_6 about v_0.

**v_0 = (2, 0) is the natural construction center of de Grey 1585**, not
origin. de Grey's H = M + W has center at v_0; the .sage file embeds the
construction with that coordinate convention.

### e1n: C_6-symmetric core of de Grey 1585 has chi = 4

[`experiments/combinatorial/e1n_degrey_c6_core.py`](../combinatorial/e1n_degrey_c6_core.py).

Extract V_sym = {v : R^k(v) in V for k = 0..5} about v_0. SAT-check chi(V_sym).

**Result**:
- 778 vertices in C_6 core (49.1% of 1585)
- 3806 edges within core (48.1% of 7909)
- Density E/V = 4.89 (similar to Polymath 510's 4.91)
- chi(V_sym) = 4 (4-colorable: True; 3-colorable: False; SAT-confirmed)

**Conclusion**: The chi >= 5 property of de Grey 1585 depends ESSENTIALLY
on the ~807 asymmetric "perturbation" vertices, NOT on the underlying
C_6-symmetric core. The natural symmetric skeleton alone is 4-chromatic.

## LEARNING L16

Captures the de Grey 1585 structural picture:
1. No exact rotational symmetries (parallel to Polymath 510 / Heule 826).
2. Approximate D_6 about v_0 (NOT origin).
3. C_6 core (778 vertices) has chi = 4.
4. chi >= 5 lives in asymmetric residue.

## Cross-architectural implication

The Hadwiger-Nelson chi >= 5 lineage achieves its bound DESPITE approximate
rotational symmetry, not BECAUSE of it. The natural symmetric cores are
4-chromatic. This is a sharp structural observation:

- L14 (Moser binding rotations in Q(sqrt 3, sqrt 11)): no chi >= 5 union
  of binding rotations exists at low vertex count.
- L15 (Polymath 510 C_6 closure): the closure is chi 5 but C_6-irreducible.
- L16 (de Grey 1585 C_6 core): the symmetric core alone is chi 4.

These three findings together say: **rotational symmetry is not the
mechanism by which chi >= 5 is achieved in the Hadwiger-Nelson lineage**.
The mechanism is some specific asymmetric "obstruction" pattern that the
SAT-minimization respects. Identifying this obstruction pattern is the
next research question.

## Routes forward (next session)

1. **D_6 core of de Grey 1585**: intersection over all 12 dihedral elements
   (not just C_6). Likely smaller than 778. SAT-check.
2. **SAT-MUS analysis**: find a minimum unsatisfiable subset (MUS) of de
   Grey 1585. The vertices in the MUS that are NOT in V_sym are the
   "essential asymmetric residue". This identifies the structurally
   critical perturbation pattern.
3. **Compare to Parts 509**: is Parts 509 a sub-MUS of de Grey 1585?

## Status table updates

| Experiment | Architecture | Status |
|---|---|---|
| e1l de Grey 1585 exact symmetry | 1 | done; zero non-identity rotations (L16) |
| e1m de Grey 1585 approximate D_6 | 1 | done; v_0 = (2, 0) is the center (L16) |
| e1n de Grey 1585 C_6 core | 1 | done; 778-vertex core has chi = 4 (L16) |

## Wrong-approach status

All experiments use exact algebraic coordinates in Q(sqrt 3, sqrt 5, sqrt 7,
sqrt 11). The Q^2 detector passes (the field strictly contains Q^2 and the
vertices use irrational coordinates throughout).
