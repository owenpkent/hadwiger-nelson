# NIGHT_PLAN (template)

A gate-driven contract for unattended overnight runs. Adapted from the zeta repo;
see [`../ZETA_INNOVATION_TRANSFER.md`](../ZETA_INNOVATION_TRANSFER.md). Copy this
to `orchestrator_sessions/NIGHT_PLAN_<date>.md` and fill the queue.

The point is that **the validation gate is the trust boundary**: unvalidated math
never lands as if it were correct. Commit only on a passing gate; quarantine
everything else to a findings file.

## Protocol

For each task in the queue, in order:

1. Run the named **gate** first. The gate is a runnable check with a binary verdict,
   not a vibe.
2. **Gate passes** -> do the work, re-run the gate, then `git add -A && git commit`
   with a `feat:/fix:/docs:` message. **Do not push** (Owen authorizes pushes).
3. **Gate fails** -> append a dated entry to `_NIGHT_FINDINGS.md` (what was tried,
   the gate output, the suspected cause), mark the task BLOCKED, and move on. No
   commit.
4. **One honest attempt per task.** Do not loop on a failing gate; record it and
   continue. A money-pit instance (heavy-tailed SAT/SDP) gets one bounded budget,
   then BLOCKED.
5. End-of-run: update [`../PHASE_STATE.md`](../PHASE_STATE.md) (a dated block at the
   top + the Last-verified-state pin) and leave `_NIGHT_FINDINGS.md` in place.

## Gates available in this repo

- **k-colorability**: `solve_color(n, edges, k, symbreak=True, proof_path=...)`
  returns UNSAT with a checkable DRAT proof (or SAT with a coloring). Gate = the
  expected verdict matches.
- **Two-solver agreement**: `e1b_de_grey_skeleton.py` / `portfolio_sat.py` run
  independent solvers; gate = no disagreement (a disagreement is a soundness bug).
- **Exact re-embedding**: a candidate UDG re-embeds with exact arithmetic and every
  edge has squared distance exactly 1 (sympy), float residual < 1e-12 as a sanity
  pass.
- **Controls intact**: `python -m experiments._shared.smoke_test` still green
  (the Q^2/L^inf/R^1 colorings did not change), and
  `python -m experiments.lemma_db.build_db` reports 0 firewall violations.

## Risk tiers (tag every deferred item)

- **Tooling risk**: anything needing Lean `elan`/`lake` to be live, or nauty/pynauty
  (no C compiler on this host). Keep OFF the unsupervised path unless pre-verified.
- **Novel-construction risk**: a new gadget/UDG whose correctness is the whole point.
  Gate hard (two solvers + exact distances) before it counts.
- **Marginal / filler**: doc syncs, cache salvage, number re-checks. Safe to batch.

## Queue (fill in)

| # | Task | Gate | Risk tier | Budget | Outcome |
|---|------|------|-----------|--------|---------|
| 1 |      |      |           |        |         |
| 2 |      |      |           |        |         |

## Findings quarantine

Unvalidated or gate-failing results go to `orchestrator_sessions/_NIGHT_FINDINGS.md`
(dated, append-only), never into LEARNINGS or a commit, until a gate passes.
