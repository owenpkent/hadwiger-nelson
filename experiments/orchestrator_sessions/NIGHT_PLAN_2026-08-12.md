# Overnight plan, 2026-08-12 into 2026-08-13

Written at 21:10 local. The machine has 8 cores and they are already committed, so
this plan is about SEQUENCING and STOP CONDITIONS, not about adding work. Last
night's failure mode was the opposite: four jobs stacked to load 22 on 8 cores,
which made every measurement unreliable and let a diverging search burn hours
unnoticed.

## Core budget, stated because it is the binding constraint

| job | cores | started | expected |
|-----|-------|---------|----------|
| n=18 via cube-and-conquer (autorun step 1) | 7 | 21:03 | hours; unknown tail |
| E27 direction ablation on de Grey 1585 | 1 | 19:57 | ~4 h (23 units, each a k=4 SAT on 1585 vertices) |
| E29 iterated assembly (nice 19) | scavenges | 21:09 | minutes to ~1 h per depth |

That is the whole machine. **Nothing else starts tonight**, and E29 runs at nice 19
precisely so it yields to the other two rather than competing with them.

## What each job can produce, and what it means

### 1. n=18 (the flagship)

Cells m=53, 52, 51, 50, 49 in that order, easiest first. Cells 54..57 are already
UNSAT from the E20 ladder.

* **All five UNSAT** -> the published claim extends from $n \le 17$ to $n \le 18$:
  any host for a $\chi \ge 6$ UDG clamp has $n \ge 19$. This is the single most
  valuable outcome available tonight, and it folds straight into C1 next to L78.
* **Any cell UNKNOWN** -> WALL, written to STOP with which cubes timed out.
  Honest and useful: it bounds what this hardware can do and says the next order
  needs a different idea, not more hours.
* **A HIT** -> the queue stops immediately and loudly. Verify independently before
  anything else; this is the result the whole program exists to find.

Guarded by: per-cube 1800 s timeout, an UNKNOWN cube never counted as UNSAT, and a
non-vacuity probe on every cell that comes back UNSAT.

### 2. E27 direction ablation

Delete each of the 23 direction classes from de Grey's graph and ask whether
$\chi \ge 5$ survives.

* **All 23 essential** -> quantifies L18's "extremely delocalized" into a
  statement worth quoting: there is no small skeleton for a new construction to
  copy.
* **Some redundant** -> the redundant classes are scaffolding, and the essential
  ones are the binding skeleton. That would be the most actionable structural
  result of the night, because it says what a new construction must reproduce.

### 3. E29 iterated assembly (the upside bet)

E28 showed one rotation on the new 56-vertex core binds but leaves $\chi = 4$.
This iterates, which is what actually built the lineage. Three distinguishable
outcomes, all informative, listed in the module docstring; the one that matters is
$\chi \ge 5$, which would be a 5-chromatic UDG outside the lineage's field.

Capped at depth 6 and 900 points so it cannot diverge.

## Stop conditions

The queue writes `_cache/STOP` and halts on HIT, WALL, or GATE, and cron will not
re-arm it while that file exists. E27 and E29 are single runs that end on their
own. **If STOP is absent in the morning, the queue is still working and nothing
needs a human.**

## What NOT to do tonight

* Do not start E23 ($f(6)$ at $n=15$): projected 100-300 cpu-h, and it would
  starve the flagship. $f(6) \ge 15$ is banked.
* Do not restart the blind-split route on n=18. It diverged to depth 15 with
  branches still timing out; it is retired in `_cache/e20/RETIRED_split_route.txt`.
* Do not grow balls in any field. L83 measured that dead: radius 8 on 78
  generators is $\sim 3.5 \times 10^{17}$ points against the 1,585 de Grey uses.

## Morning checklist

1. `./status.sh` -- if ATTENTION is none, read the logs; if not, read the STOP file.
2. `_cache/e25/n18_stuck.json` -- per-cell verdicts, cube counts, slowest cube.
3. `_cache/e27/summary_residue.json` -- essential vs redundant direction classes.
4. `_cache/e29/result.json` -- best chi reached and the assembly history.
5. If n=18 closed: amend C1 (Theorem 2 to $n \le 18$) and update L78, PHASE_STATE,
   LOAD_BEARING_FACTS item 5b.
