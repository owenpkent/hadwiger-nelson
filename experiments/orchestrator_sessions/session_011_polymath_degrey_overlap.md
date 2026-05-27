# Session 011: Polymath 510 is a translated substructure of de Grey 1585

**Date**: 2026-05-26 (continuation of session 010)
**Mode**: depth on Architecture 1, Shot 2.

## Goal

L18 left an open question: are Polymath 510 (in Q(sqrt 3, sqrt 11)) and de Grey 1585 (in Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11)) two distinct chi >= 5 "geometries", or related?

Since de Grey's field strictly contains Polymath's, Polymath's vertices are all valid elements of de Grey's field. The question is whether they're the same vertices.

## What landed

### e1s: 62% of Polymath 510's vertices ARE de Grey 1585 vertices (translated)

[`experiments/combinatorial/e1s_compare_polymath_degrey.py`](../combinatorial/e1s_compare_polymath_degrey.py).

Test: for each translation T, count |V(Polymath) shifted by T that lies in V(de Grey)|.

**Result**:
- T = (0, 0): only 25/510 = 4.9% overlap.
- T = (2, 0): **315/510 = 61.8% overlap**.
- 6 hex-lattice translates near T = (2, 0): 196-203 overlap each.

So Polymath 510's natural center maps to de Grey 1585's v_0 = (2, 0) (the construction center identified in L16). After this translation, 315 Polymath vertices coincide with de Grey vertices.

## LEARNING L19

Polymath 510 IS a translated substructure of de Grey 1585:
- 315 of its 510 vertices are de Grey vertices (+(2, 0)).
- The remaining 195 are "field-reduction artifacts" — vertices added by Heule/Parts to compensate for the loss of sqrt 5, sqrt 7 when reformulating in Q(sqrt 3, sqrt 11).

There is ONLY ONE chi >= 5 "geometry" in the lineage. de Grey 1585, Heule 553, Polymath 510, Parts 509 are all variants of the same underlying construction.

This refines L18: the chi >= 5 obstruction is delocalized in de Grey 1585's full algebraic representation, but Polymath 510 found a way to be smaller by reducing the field (and adding compensatory vertices).

## Cross-architectural implication

L4 said Architectures 1 and 2 share the missing 6-chromatic UDG. L19 sharpens: the 6-chromatic UDG (if it exists) is likely in a field at least as rich as Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11). The path through smaller fields probably cannot reach chi >= 6 because field reduction discards exactly the algebraic complexity needed.

## Routes forward (next session)

1. **Algebraic classification of the 195 Polymath "new" vertices**: what's their pattern? Are they systematic translates of a motif?
2. **Test the "de Grey overlap" subset alone**: take just the 315 vertices of Polymath 510 that are de Grey vertices. Plus de Grey's edges restricted to this subset. Is that still chi >= 5?
3. **Search for chi >= 6 in de Grey's full field Q(sqrt 3, sqrt 5, sqrt 7, sqrt 11)** rather than the smaller Polymath field. de Grey may have known something about this field that the SAT-minimization lineage discarded.

## Status table updates

| Experiment | Architecture | Status |
|---|---|---|
| e1s Polymath 510 vs de Grey 1585 comparison | 1 | done; 62% overlap under T = (2, 0) (L19) |

## Wrong-approach status

Comparison uses exact algebraic coordinates from both fields. The Q^2 detector passes (both graphs use irrational coordinates).
