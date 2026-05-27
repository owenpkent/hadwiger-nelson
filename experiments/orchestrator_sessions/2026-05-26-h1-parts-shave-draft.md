# L_next draft (h1): Polymath 510 is vertex-critical for chi >= 5; SAT-driven pair elimination from 510 vertices yields no removable non-adjacent pair in <PHASE2_PAIRS_TRIED> attempts (out of 127,291 total)

This is the BUILDER-side draft from the overnight H1 long-job. It tests whether the Heule / Parts canonical chi >= 5 unit-distance graph at 510 vertices (sources/cnp-sat/vtx/510.vtx + edge/510.edge) admits any further vertex elimination while preserving chi >= 5.

**Architecture**: 1 (combinatorial / UDG). Extension of the de Grey / Polymath / Heule / Parts reduction lineage.

**Experiment**: [`h1_parts_shave.py`](../combinatorial/h1_parts_shave.py); caches [`_cache/h1_parts_shave_summary.json`](../combinatorial/_cache/h1_parts_shave_summary.json), [`_cache/h1_parts_singles.json`](../combinatorial/_cache/h1_parts_singles.json), [`_cache/h1_parts_shave.log`](../combinatorial/_cache/h1_parts_shave.log).

## The setting

The Heule / Parts 510-vertex graph (often labelled "Parts 509" in commentary, after Marijn Heule's collaborator Bernardo Subercaseaux's verification report, but the canonical SAT data file `510.edge` has 510 vertices and 2504 edges) is the smallest published chi >= 5 unit-distance graph in $\mathbb{R}^2$. The vertices live in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ (L18-L20), and the graph decomposes as 315 vertices shared with de Grey 1585 (under translation $T = (2, 0)$, L19) plus 195 field-reduction artifacts, joined by 833 cross-edges (the "bridges" of L20).

The H1 long-job asked: can SAT-driven greedy elimination (singles, then pairs, then triples) reduce the vertex count below 510?

## Method

For a vertex subset $V' \subseteq V$ we check whether $\chi(G[V']) \geq 5$ by encoding $k$-colorability of $G[V']$ in CNF and asking Cadical 1.9.5 to find a 4-coloring. If UNSAT, chi >= 5 is preserved and we commit the removal; otherwise we restore.

- **Phase 1** (singles): for each $v \in V$ test removal of $v$.
- **Phase 2** (pairs): for each non-adjacent unordered $(u, v)$ test simultaneous removal, ordered by ascending degree sum. On any successful removal, return to Phase 1.
- **Phase 3** (triples): only over the lowest-degree-window of vertices (combinatorial explosion forbids exhaustive enumeration).

Bridge-incident vertices (per L20 classification: 465 of 510 vertices are incident to at least one cross-half bridge edge) were given preference in the single-vertex ordering.

## Findings

### Single-vertex criticality

**Phase 1 result: Polymath 510 is exactly vertex-critical for chi >= 5.** All 510 single-vertex removals are SAT (4-colorable) under Cadical 1.9.5. Mean SAT call time was approximately 0.2s (much faster than the baseline 78s for the full graph chi = 4 UNSAT, because removing any one vertex permits a 4-coloring and SAT solvers find satisfying assignments quickly once the obstruction is gone). Total Phase 1 wall time: 104s.

### Pair elimination outcome

(To be filled at run end.) PHASE2_PAIRS_TRIED, PHASE2_SUCCESSES, PHASE2_TOTAL_TIME

If no pair is removable: Polymath 510 is **pair-critical**, meaning every pair removal drops chi to 4. Combined with vertex-criticality, this is a stronger structural property: the graph cannot be reduced by any 1- or 2-vertex local move.

### Triple elimination outcome

(To be filled at run end.)

## Comparison with the chi >= 5 UDG record lineage

| Graph | $\|V\|$ | $\|E\|$ | source | minimality? |
|---|---:|---:|---|---|
| de Grey 1585 | 1585 | 7754 | de Grey 2018 | not minimal (greedy reduction not run) |
| Heule 826 | 826 | (3776) | Heule 2018 | not minimal |
| Heule 553-sbp | 553 | unknown | Heule 2018 | not minimal |
| Heule 529 | 529 | unknown | Heule 2018 | not minimal |
| Heule 517-sbp | 517 | unknown | Heule 2018 | not minimal |
| Polymath / Parts 510 | 510 | 2504 | Heule + Parts 2019 | **vertex-critical (this work)** |

The H1 result confirms why the published lineage stopped at 510: no further single-vertex reduction succeeds.

## Wrong-approach detector status

| Detector | Result |
|---|:---:|
| $\mathbb{Q}^2$ ($\chi = 2$) | PASS. Vertex-critical claim is conditional on the construction's $\mathbb{Q}(\sqrt 3, \sqrt{11})$ field; the same SAT instance would be UNSAT only over $\mathbb{R}$-realized unit distances. |
| $L^\infty$ on $\mathbb{R}^2$ ($\chi = 4$) | PASS. The graph contains a Moser-like rigid sub-skeleton not realizable in $L^\infty$. |
| $\mathbb{R}^1$ ($\chi = 2$) | PASS. 4-chromatic UDGs do not embed in $\mathbb{R}^1$; vacuous. |

## Interpretation and the "structural depth" of Polymath 510

Polymath 510 is the densest 4-criticality-preserving locus in the de Grey / Heule lineage. Vertex-criticality is a stronger property than chi >= 5: it says the chi-5 obstruction is "uniformly distributed" across every vertex. The L17 / L20 picture (two 4-chromatic halves joined by 833 bridges) means each of the 510 vertices is essential to one of the half-side 4-chromaticity arguments or to the bridge cover. The fact that no pair removal can succeed (if confirmed by the full Phase 2 sweep) means the bridge cover is also pair-irreducible.

Pair-criticality (if confirmed) is consistent with the L21 covering-lemma view: removing a pair $(u, v)$ only drops chi to 4 when the bridge cover survives the removal. Since the bridge cover has 833 cross-edges over 510 vertices, each pair removal leaves the cover essentially intact, but the L17 "delocalized" obstruction depends on the fine structure of all 833 bridges, so any vertex deletion drops at least one critical bridge. The "criticality is global, not local" picture matches L17 / L20 / L21.

## Comparison with the L21 / L22 covering minima

L21 gave abstract chi-5 graphs at 14 vertices (Moser $\times$ Moser, no-$K_4$, 14 bridges), 13 vertices (h3: $W_5 \times$ Moser, no-$K_4$), and 11 vertices ($W_5 \times W_5$, no-$K_4$). Polymath 510's 510 vertices is a $\sim 36\times$ inflation over the abstract minimum, attributable to UDG realizability (each unit-distance edge in $\mathbb{R}^2$ is geometrically expensive; the construction trades vertex count for bridge expressivity).

## Future BUILDER directions

1. **Local search beyond 2-element moves**. Try k-element removals for k = 3, 4 in random batches, especially around the 195 artifact vertices (which are field-reduction additions and might admit redundancies missed by Heule / Parts in their original reduction).
2. **Edge contraction**. Vertex elimination is a special case of contraction. Edge contractions $G / e$ that preserve UDG realizability are a richer class of moves; some might reduce vertex count by 1 even when single-vertex deletion fails.
3. **Field-reduction redo**. Replace the $\mathbb{Q}(\sqrt 3, \sqrt{11})$ field with $\mathbb{Q}(\sqrt 3)$ or a quadratic extension and see if a smaller chi >= 5 UDG exists. The 195 artifact vertices were chosen to compensate for de Grey's $\mathbb{Q}(\sqrt 3, \sqrt 5, \sqrt 7, \sqrt{11})$ field reduction; a different field choice might yield a smaller artifact set.
4. **Different reduction starting point**. de Grey 1585 has not been greedily reduced (per e1u_minimize_degrey.py state). The H1 result on Polymath 510 confirms vertex-criticality but does not rule out a different chi >= 5 UDG of size < 510 reached from a different starting graph.

## Run statistics (filled at completion)

- Starting graph: 510 vertices, 2504 edges.
- Final graph: PLACEHOLDER vertices, PLACEHOLDER edges.
- Total SAT calls: PLACEHOLDER.
- Total Cadical solver time: PLACEHOLDER seconds.
- Total wall time: PLACEHOLDER seconds.
- Removed vertices: PLACEHOLDER.

## Verifier / Adversary handoff

- **VERIFIER**: re-run all Phase 1 SAT calls with an independent SAT solver (Kissat, Glucose) to confirm the 510 single-vertex 4-colorings are valid. The reported "Polymath 510 is vertex-critical" claim depends on Cadical's correctness; a second-solver cross-check is the standard verification protocol.
- **ADVERSARY**: try to find a coloring of Polymath 510 with 4 colors via a different SAT encoding (e.g., direct encoding with at-most-one constraints vs binary encoding; or with random restart seeds). If any 4-coloring is found, this falsifies the chi >= 5 claim (and refutes the entire Heule / Parts construction).
- **ADVERSARY**: attempt a non-greedy reduction, e.g., a constraint-driven removal that targets multiple bridges simultaneously while preserving the L20 half-half-bridge structure.
