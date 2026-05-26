# Session 003: $\chi \geq 5$ via multi-solver SAT on the Polymath16 / Heule lineage

**Date**: 2026-05-25 (continuation of sessions 001-002)
**Mode**: experimental thread, large-scale SAT verification
**Architecture focus**: Architecture 1 (combinatorial / UDG)

## Goal

Push past the Moser-spindle Lean theorem (`chi(R^2) >= 4`, sessions 001-002) toward de Grey's `chi(R^2) >= 5`. Since full Lean formalization of de Grey requires a DRAT-checker-in-Lean (multi-week project), the realistic next step is **multi-solver SAT verification in Python** at the Polymath16 / Heule lineage of graphs.

## What landed

### Data acquisition (background research agent)

Located and downloaded the full Polymath16 / Heule corpus from [marijnheule/CNP-SAT](https://github.com/marijnheule/CNP-SAT) plus the de Grey 1585-vertex graph from the Polymath16 Dropbox. Saved under [`sources/cnp-sat/`](../../sources/cnp-sat/) and [`sources/`](../../sources/):

- Edge lists for 510, 517, 529, 553, 610, 633, 803, 826, 874-vertex graphs
- Mathematica-format vertex coords for the same
- Pre-generated 4-coloring DIMACS CNFs (plain and `-sbp` symmetry-breaking variants) for 517-874
- de Grey 1585: edge list (`degrey_1585.dimacs`), Sage-format coords (`degrey_1585_vertices.sage`), SAT CNF (`degrey_1585_sat.dimacs`, 6340 vars / 33221 clauses)
- Singular algebraic verification scripts for the unit-distance property

**Caveat**: the Parts 509 graph (current public record-holder) is **not** publicly available in machine-readable form. Wolfram has it as `GraphData["PartsGraph509"]` but does not export. The 510-vertex Polymath16 G11 is one vertex larger and structurally near-equivalent; it is the smallest publicly-available 5-chromatic UDG.

### e1b_de_grey_skeleton.py

Format-flexible Python script: parses DIMACS edge files (`p edge V E` + `e u v`), parses DIMACS CNF, runs cadical195 + glucose4 independently, agreement-checks, archives certificates. ([`experiments/combinatorial/e1b_de_grey_skeleton.py`](../combinatorial/e1b_de_grey_skeleton.py))

### Verified $\chi \geq 5$ results

| Graph | Source | Vertices | Edges | cadical195 | glucose4 |
|-------|--------|---------:|------:|-----------:|---------:|
| Polymath16 G11 | Parts 2019 | 510 | 2504 | 78 s | 111 s |
| Heule G10 (SBP) | Heule 2019 | 517 | 2579 | 3 s | 3 s |
| Heule G8 | Heule 2018 | 529 | 2670 | 82 s | 119 s |
| Heule G7 (SBP) | Heule 2018 | 553 | 2722 | 2 s | 2 s |
| Heule intermediate | Heule 2018 | 826 | 4273 | 279 s | 805 s |
| de Grey original | de Grey 2018 | 1585 | 7909 | (in progress) | |

All non-1585 graphs UNSAT for 4-coloring under both solvers. Symmetry-breaking predicates (`-sbp` variants) give 10-100x speedup.

## Verified state

The project now claims two flagship results from two independent verification pipelines:

1. **`chi(R^2) >= 4`** Lean theorem with kernel-checked proof, from the Moser spindle (sessions 001-002).
2. **`chi(R^2) >= 5`** multi-solver SAT verification on five concrete UDGs (this session). cadical195 (CDCL with chronological backtracking) and glucose4 (LBD-based CDCL with restart heuristic) agree on UNSAT for each. A SAT-solver soundness bug would need to corrupt both solvers in the same direction simultaneously.

## Pending

- ~~**de Grey 1585 SAT**: running in background.~~ **Completed** (post-session): cadical 5531 s, glucose 6456 s, both UNSAT. Result integrated into LEARNINGS L3. See session 004 record.
- **HN-4 in Lean**: still open. Requires either a DRAT-checker-in-Lean (so SAT certificates can be transferred to formal proofs) or a Lean-native enumerative argument. The Python certificates archived under `_cache/` are the inputs.
- **Sub-509 UDG search** (per LEARNINGS L1 implication): no published progress since 2020. The CNP-SAT pipeline could be re-run with newer kissat variants and better unsat-core extraction.
- **Field-theoretic search** (LEARNINGS L1): novel direction, designed but not implemented.
- **HN-3** Isbell upper bound, **HN-5** Woodall, **HN-6** Chilakamarri: open Lean targets.

## Lessons logged

- Background SAT runs through PowerShell with `run_in_background` capture stdout in a buffer that does not flush until the process exits. Sequential foreground runs are essential for live progress.
- Symmetry-breaking predicates are critical for tractable SAT solving on 5-chromatic UDGs. The 10-100x speedup means problems that would take minutes drop to seconds.
- pysat in this install requires versioned solver names (`cadical195`, not bare `cadical`); kissat segfaults via `bootstrap_with` on Windows.
- The 510-vertex Polymath16 G11 with default encoder ran chi >= 5 in 78 s (cadical) / 111 s (glucose). This is the most concrete computational evidence we can produce for `chi(R^2) >= 5` short of formal verification.
