# TOKEN_EFFICIENCY

The cost playbook for multi-agent rounds on this program. Adapted from the zeta
repo; see [`ZETA_INNOVATION_TRANSFER.md`](ZETA_INNOVATION_TRANSFER.md). The
2026-06-09 creative round spent ~2.3M output tokens; the levers below cut that
without losing the creative product. The creative work IS the generators; almost
everything else is checklist work that can run cheaper.

## Pre-fan-out checklist (run before any multi-agent sweep)

1. **Batch, do not solo.** One ADVERSARY over a whole gadget family returning an
   array beats N separate adversary agents. One BUILDER per lens, not per
   conjecture. Pass the work-list as one array to `parallel`/`pipeline`.
2. **Model-tier by task.** Put the expensive model only where invention happens
   (BUILDER proposing, SYNTHESIZER writing). Push rubric/checklist work
   (ADVERSARY scoring against the freeze list, detector self-checks, codegree
   checks, number re-verification) to Sonnet or Haiku. The
   [`hn-lens-attack`](../.claude/workflows/hn-lens-attack.js) workflow already does
   this (Sonnet on adversary + synthesis).
3. **Inline the data; forbid repo reads.** Hand the agent the CNF, the graph JSON,
   or the relevant LEARNINGS gist directly in the prompt. An agent that greps the
   repo to reconstruct context spends more than the context costs to inline.
   `FREEZE_LIST.md` + `LOAD_BEARING_FACTS.md` exist so this gist is one paste.
4. **Cap the prose.** Every output field has a purpose; carry an explicit brevity
   instruction. Thinking is the bulk of output spend, so cap chi-estimate
   justifications and "why plausible" essays.
5. **Order the flaky/expensive work LAST, and pipeline it.** The hard k=6 SAT and
   the order-2 SDP are heavy-tailed; put them at the end of a pipeline so the cheap
   stages are not blocked behind a barrier. Prefer `pipeline` over `parallel` for
   the solver portfolio so a slow solver does not stall the fast ones (the L64
   portfolio law: Cadical 12h vs Maple 155s on one instance).
6. **State a budget.** For an overnight sweep, name a token target and a stop rule
   (loop-until-dry or loop-until-budget), so a runaway generator does not burn the
   pool. The `budget` object in a workflow makes this a hard ceiling.
7. **Salvage before re-solving.** Check `experiments/**/_cache/` and
   `combinatorial/_cache/` for an existing witness or verdict before launching a
   solve. SAT/SDP runs are the program's most expensive single operations.

## Solver-cost notes specific to this program

- The symmetry-broken portfolio (`_shared/portfolio_sat.py`, `colorable_portfolio(..., symbreak=True)`)
  is the default for structured UNSAT: it crosses walls the naive encoding cannot,
  and it makes the calibration anchor (Heule-826 k=4) a ~6s check rather than minutes.
- PyPy gives ~5x on the pure-Python solver, but NOT on pysat code (it shells to a C
  extension). Invoke PyPy by full path for the pure-Python paths only.
- Exact Groebner realizability is feasible only to ~14 vertices; do not spend agent
  budget asking for larger exact realizations (use interval arithmetic + alpha-theory
  instead, per the decidability lens).

## See also

- [`orchestrator_sessions/NIGHT_PLAN_TEMPLATE.md`](orchestrator_sessions/NIGHT_PLAN_TEMPLATE.md)
  for the gate-driven overnight contract.
- [`PHASE_STATE.md`](PHASE_STATE.md) for what state to read on resume (so a session
  does not re-derive the edge, the single biggest avoidable cost).
