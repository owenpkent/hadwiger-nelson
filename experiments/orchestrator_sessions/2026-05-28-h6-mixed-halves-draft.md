# ORCHESTRATOR session draft: Direction A (mixed-half chi-6 search)

Date: 2026-05-28
Architecture portfolio focus this session: Arch 1 (combinatorial / UDG), Direction A.
Cycle run: BUILDER -> VERIFIER -> ADVERSARY -> SYNTHESIZER (full).

## Goal

Test whether two DISTINCT chi-5 halves $H_1 \neq H_2$ joined by a no-$K_4$ bridge set $B$ can force $\chi \geq 6$ at fewer than the 1020 vertices and/or fewer than the $\leq 2000$ bridges of the L27/L28 diagonal construction $P_{510} \cup P_{510} + B$, or with a different algebraic field structure.

## What was deployed

- BUILDER: new script [`h6_mixed_halves.py`](../combinatorial/h6_mixed_halves.py), generalizing the diagonal template [`h5_polymath_squared.py`](../combinatorial/h5_polymath_squared.py) to two distinct halves loaded from separate `.edge` files. Three parallel runs: (510, 517), (510, 553), (510, 826).
- VERIFIER: new script [`h6_mixed_verify.py`](../combinatorial/h6_mixed_verify.py). Independent exhaustive $K_4$ enumeration + exact (no-budget) dual-solver UNSAT (Cadical195 + Glucose4).
- ADVERSARY: new script [`h6_mixed_cocirc.py`](../combinatorial/h6_mixed_cocirc.py). 30-digit mpmath cocircularity sieve on the bridge-source sets.
- SYNTHESIZER: LEARNINGS L29, this draft, plan-table row.

## Results

| Pair | $\|V\|$ | Verdict | $\|B\|$ | $\omega$ | $\chi \geq 6$ | UDG-realizable |
|---|---:|---|---:|---:|---|---|
| $P_{510} \cup P_{553}$ | 1063 | **CHI_6_CONFIRMED** | 2400 | 3 | yes (Cadical 54s + Glucose 99s UNSAT) | NO (0/92 cocircular) |
| $P_{510} \cup P_{517}$ | 1027 | inconclusive (killed mid-SAT at $\|B\| = 1800$) | 1800+ | n/a | unresolved (SAT-hard) | n/a |
| $P_{510} \cup P_{826}$ | 1336 | inconclusive (killed mid-SAT at $\|B\| = 2400$) | 2400+ | n/a | unresolved | n/a |

Baseline (L27/L28 diagonal): 1020 vtx, $\|B\| \leq 2000$.

## Verdict on Direction A (honest)

Mixed halves do **NOT** beat the diagonal baseline.
- Vertex count: impossible to beat. Every corpus half is $\geq 510$ vertices, so any pair is $\geq 1020$; $510 + 553 = 1063 > 1020$. Closed by corpus arithmetic, not by search failure.
- Bridges: $\|B\| = 2400 > 2000$. No evidence of bridge economy.
- Genuine win: **field-structure diversity**. The chi-6 forcing is realized between two NON-isomorphic chi-5 halves (distinct edge counts 2504 vs 2722), refuting the hypothesis that L27/L28's forcing was a diagonal $H_1 \cong H_2$ artifact. This is the first non-diagonal no-$K_4$ chi-6 abstract graph.

## Falsifiability trigger status

Direction A's implicit trigger ("mixed halves beat 1020 vtx or 2000 bridges") is **HIT NEGATIVE**: it cannot beat vertex count (corpus arithmetic) and did not beat bridges. Direction A is therefore CLOSED as a vertex-count / bridge-economy strategy. It is retained only as evidence that the L24 obstruction is field-agnostic.

## Recommended next deployments (for the next ORCHESTRATOR session)

A. **Re-run $P_{510} \cup P_{517}$ with a long, uncapped Stage-D SAT** (Cadical 1-2 h wall, then Glucose). The $\|B\| = 1800$ SAT-hardness is the single most promising loose thread: 517 may force chi-6 at $\|B\| < 2000$. Sharp spec: patch `h6_mixed_halves.py` to persist `B` to a graph artifact at every sample-level-all-infeasible checkpoint (so a kill does not lose the bridge set), and raise the final `sat_time_limit`.

B. **Pivot the "sub-1020 chi-6 abstract graph" goal away from half-pairs.** Two concrete angles for 3-5 parallel BUILDERs: (1) vertex identification / quotient on the 1020 diagonal graph to merge vertices while preserving chi >= 6 and omega <= 3; (2) L24 triple-coupling at three SMALLER gadgets (the Moser spindle as a coupling gadget, not a half).

C. **L28-style bridge-minimum probe on the L29 510x553 graph** to convert the $\|B\| \leq 2400$ upper bound into a tight greedy-suffix minimum (lower priority; the graph is larger than baseline so the minimum is not record-relevant).

Recommended: A and B in parallel next session (A is one re-run, B is the real forward progress). C is optional cleanup.

## Compute used

Three ~1 h BUILDER runs (two killed by environment before verdict), one ~3 min VERIFIER, one ~1 min ADVERSARY sieve. Well within budget. No escalation to Owen warranted: the positive result is a larger-than-baseline abstract graph (not a UDG, not a claimed $\chi(\mathbb{R}^2)$ improvement), and the cocircularity sieve confirms non-realizability, so no over-claim risk.

## Files created / modified

- created `experiments/combinatorial/h6_mixed_halves.py`
- created `experiments/combinatorial/h6_mixed_verify.py`
- created `experiments/combinatorial/h6_mixed_cocirc.py`
- created cache artifacts under `experiments/combinatorial/_cache/`: `h6mix_510x553_graph.json`, `h6mix_510x553_summary.json`, `h6mix_510x553_search_log.json`, `h6mix_510x553_verify.json`, `h6mix_510x553_cocirc.json`, plus logs and 5-coloring caches for all three pairs (517/826 partial)
- modified `experiments/LEARNINGS.md` (added L29 at top)
- modified `experiments/PROOF_ARCHITECTURES_PLAN.md` (added h5/h6 status rows)
- created this draft
