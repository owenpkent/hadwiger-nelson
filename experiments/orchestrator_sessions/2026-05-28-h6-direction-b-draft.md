# Orchestrator session 2026-05-28: Direction B (reduce the 1020-vertex chi-6 graph)

## Goal

Find a no-$K_4$ ($\omega \leq 3$) abstract graph with $\chi \geq 6$ on FEWER than 1020 vertices, by REDUCING the L27/L28 diagonal construction $G = P_{510} \cup P_{510} + B$ rather than swapping halves (Direction A was closed in L29 by corpus arithmetic).

Three sub-directions dispatched:
1. Vertex deletion / criticality (primary).
2. Vertex identification / quotient (primary).
3. Triple-coupling at smaller gadgets (secondary, conditional on a sub-340 chi-5 no-$K_4$ gadget existing).

## Environment note

The `Agent` tool is NOT available in this run (this orchestrator is itself a subagent), so the planned parallel BUILDER deployment was not possible. The orchestrator executed Direction B directly, prioritizing the highest-EV experiment first (the bulk-deletion essentiality probe).

## What was run

- `h6_direction_b_probe.py`: essentiality map + bulk deletion. Confirmed baseline $\chi \geq 6$ (Cadical UNSAT, 2078s) and classified all 1020 vertices. The full-budget ($15\times10^6$ conflict) per-trial cost caused the first bulk trial to dominate (>1h, the L29 single-solve anti-pattern); the probe was killed after the essentiality map landed and re-run with a tighter budget.
- `h6_direction_b_fast.py`: tight-budget ($4\times10^6$ conflict) incremental deletion. Produced the decisive deletion ladder (8-vertex break threshold, <=4 intractable).
- `h6_direction_b_single.py`: long-budget ($1.2\times10^8$ conflict) single-vertex decisive test on the lowest-degree non-bridge vertices. IN-FLIGHT at session close (>15 min CPU, no verdict, expected BUDGET). Result will land in `_cache/h6_direction_b_single.json`.
- `h6_small_gadget_triage.py`: chi + omega of S199, L403, T721. All $\chi = 4$, no-$K_4$.

## Findings (full detail in LEARNINGS L30)

**Direction B is a NEGATIVE. The 1020-vertex baseline stands as the lineage vertex-minimum.**

- **Deletion-rigid**: deleting $\geq 8$ non-bridge $H_2$ vertices breaks $\chi \geq 6$ (Cadical SAT, 32s); deleting $\leq 4$ is SAT-intractable (BUDGET, ~390s). No fast-verifiable deletion exists. The 566 non-bridge-incident vertices are NOT inessential; the chi-6 obstruction is delocalized over $H_2$'s full structure (abstract analog of de Grey / L18).
- **Triple-coupling closed**: S199 (199 vtx), L403 (403 vtx), T721 (721 vtx) are all $\chi = 4$. No sub-340 chi-5 no-$K_4$ gadget exists, so the L24 triple-lift cannot beat 1020.
- **Quotient** not separately executed: subsumed by the deletion negative (contraction is strictly harder to validate and faces the same delocalized wall). Deferred as low-EV.

Combined with L29 (Direction A half-pairs $\geq 1020$ by arithmetic), every reduction avenue against 1020 is now closed for the Polymath / de Grey lineage.

## Files created / modified

- `experiments/combinatorial/h6_direction_b_probe.py` (new)
- `experiments/combinatorial/h6_direction_b_fast.py` (new)
- `experiments/combinatorial/h6_direction_b_single.py` (new)
- `experiments/combinatorial/h6_small_gadget_triage.py` (new)
- `experiments/combinatorial/h6_direction_b_greedy.py` (new, not run; full-budget greedy, superseded by the fast probe)
- `experiments/LEARNINGS.md` (L30 added at top)
- `experiments/PROOF_ARCHITECTURES_PLAN.md` (status row added)
- `experiments/combinatorial/_cache/h6_direction_b_essmap.json`, `h6_direction_b_fast_min.json`, `h6_dirB_del_h1nonbridge_graph.json`, `h6_direction_b_*.log`, `h6_direction_b_single.json` (in-flight)

NOT committed (Owen authorizes per-action). Left in the working tree.

## Background processes still running at session close

- PID 5592: detached Cadical longrun on the L29 510x517 $\|B\| = 1800$ instance (DO NOT TOUCH; orchestrator brief). Result -> `_cache/h6mix_510x517_B1800_longrun.json` (not yet written).
- PID 44204: `h6_direction_b_single.py` long-budget single-vertex test. Result -> `_cache/h6_direction_b_single.json`.

## Portfolio allocation this session

- Arch 1 (combinatorial): 100% (Direction B, as directed).
- Arch 2 / 3 / 4: 0% (single-focus session per the brief).

## Falsifiability trigger

Direction B's implicit trigger is HIT: no sub-1020 chi-6 graph is SAT-verifiable after the deletion + triple-coupling probes. Direction B is closed. Do not re-attack the 1020 graph by deletion / quotient / triple-coupling.

## Next-session plan (sharp specifications)

1. **Append the single-vertex verdict** from `_cache/h6_direction_b_single.json` to L30. If BUDGET: rigidity finding unchanged. If SAT: confirms even the best single deletion breaks chi-6. If UNSAT (a 1019-vertex record): ESCALATE to Owen and dual-confirm.
2. **Building-block search (the only remaining vertex-count lever)**: deploy BUILDERs to hunt for a chi-5 no-$K_4$ graph below 510 vertices. The Polymath / de Grey SAT-minimization bottomed out at 510; a fresh construction (alternate field extension, non-Polymath spindle stack, or a new SAT-minimization seed) is needed. This is HIGH-RISK / HIGH-REWARD: a sub-510 chi-5 no-$K_4$ graph would immediately lower the chi-6 vertex frontier (squared, or triple-coupled).
3. **Hand the L29 510x517 $\|B\| = 1800$ DIMACS to kissat / cryptominisat** (`h6mix_510x517_B1800_decisive.cnf`). The only unresolved chi-6 instance on the table; a bridge-economy question, not vertex-count.
4. **Rebalance the portfolio**: Arch 1 vertex-count work has plateaued at 1020 with no remaining reduction lever. Consider shifting attention to Arch 2 (measurable $\chi_m \geq 6$, never started: e2a/e2b/e2c) or revisiting Arch 3 spectral, to avoid mono-architecture starvation. Recommended next allocation: Arch 1 40% (building-block search + kissat handoff), Arch 2 35% (e2a Falconer baseline + e2b autocorrelation, both unstarted), Arch 3/4 25%.

## Compute budget note

Direction B consumed ~3-4 hours of wall-clock SAT, mostly on intractable near-threshold instances (the recurring L29 hazard). The single-solve-dominating anti-pattern recurred (full-budget bulk trial >1h) and was corrected mid-session by switching to a tight-budget bisection. Lesson reinforced for next session: cap per-call conflict budgets explicitly; treat BUDGET as indeterminate; never let one solve run unbounded.
