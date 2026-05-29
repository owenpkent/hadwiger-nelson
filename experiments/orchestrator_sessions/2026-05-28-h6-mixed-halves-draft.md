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

---

## Addendum 2026-05-28 (later): 510x517 loose-thread re-run (Recommendation A)

ORCHESTRATOR re-ran the single most promising loose thread from this session: the $P_{510} \cup P_{517}$ pair that was killed mid-SAT at $\|B\| = 1800$ with no verdict and no persisted bridge set.

**What changed in the tooling.** [`h6_mixed_halves.py`](../combinatorial/h6_mixed_halves.py) now persists the combined graph (`h6mix_<tag>_graph.json`) the INSTANT the greedy reaches sample-level-all-infeasible, BEFORE the expensive Stage-D SAT, so an environment kill during a long solve never loses the bridge set again. New `--sat-time-limit` flag. New decoupled decisive solver [`h6_mixed_decisive_sat.py`](../combinatorial/h6_mixed_decisive_sat.py): loads a persisted checkpoint, writes DIMACS, runs an UNCAPPED (no conf-budget) Cadical solve, and on UNSAT re-confirms with Glucose.

**What happened.** The greedy rebuilt deterministically to the identical $\|B\| = 1800$ all-infeasible checkpoint (round 6, skippedK4 $= 211$, all 85 sampled $c_1$ list-infeasible) and **persisted it** (`_cache/h6mix_510x517_B1800_graph.json`, snapshotted to avoid overwrite). The decisive uncapped Cadical solve on that exact 1027-vtx / 6883-edge / $\|B\| = 1800$ instance ran $\approx 66.5$ min of wall-clock and was killed by the environment **without resolving**. A parallel in-loop solve returned `sat = None` after $443$s.

**Verdict: $510\times517$ at $\|B\| = 1800$ is SAT-solver-intractable in budget.** Not a chi-6 confirmation, not a chi $\leq 5$ refutation. Honest non-result.

**What IS confirmed**: $\omega = 3$ on the persisted graph (exhaustive $K_4$ enumeration, $0$ $K_4$s, $< 1$s). UDG-realizability is N/A (no positive chi-6 to test).

**Impact on L29**: none to the headline. 517 did NOT yield a sub-$2000$-bridge chi-6 graph, so it does not beat L28's $\|B\| \leq 2000$. The L29 "two killed runs" paragraph is updated to record the resolved status (still unresolved, but now durably persisted). No L30 warranted (a genuinely new structural fact would have required either a confirmed chi $\geq 6$ at $\|B\| < 2000$ or a definitive SAT showing 1800 is below threshold; neither occurred).

**Durable artifacts for handoff** (all in `_cache/`, gitignored):
- `h6mix_510x517_B1800_graph.json` (the persisted 1027-vtx graph, tags patched)
- `h6mix_510x517_B1800_decisive.cnf` (exact DIMACS, 5135 vars, 45712 clauses)
- `h6mix_510x517_B1800_decisive.json` (the SAT-intractable verdict record)

**Next-session recommendation**: hand `h6mix_510x517_B1800_decisive.cnf` to kissat and/or cryptominisat with a multi-hour wall-clock budget. pysat's Cadical195 binding has no native wall-clock timeout (only the conf-budget proxy), so a standalone kissat binary is the right tool for a genuinely long run. If kissat resolves UNSAT, 517 forces chi-6 at $\|B\| = 1800 < 2000$ (the most bridge-economical mixed pair; would warrant L30). If SAT, 1800 is below threshold and L29's "near threshold" hint is downgraded.

## Files created / modified (addendum)

- modified `experiments/combinatorial/h6_mixed_halves.py` (checkpoint-persist before Stage-D SAT; `--sat-time-limit`)
- created `experiments/combinatorial/h6_mixed_decisive_sat.py`
- created `_cache/` artifacts: `h6mix_510x517_B1800_graph.json`, `h6mix_510x517_B1800_decisive.cnf`, `h6mix_510x517_B1800_decisive.json`, `h6mix_510x517_graph.json` (checkpoint), `h6mix_510x517_rerun_stdout.log`, `h6mix_510x517_B1800_decisive_stdout.log`
- modified `experiments/LEARNINGS.md` (L29 "two killed runs" paragraph: resolved status)
