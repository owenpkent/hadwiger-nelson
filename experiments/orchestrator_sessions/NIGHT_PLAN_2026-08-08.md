# NIGHT_PLAN 2026-08-08

Unattended overnight run. Host: **Windows 11 laptop** (32 logical cores, RTX 4070
Laptop 8 GB, msys/ucrt64 gcc 15.2.0). This is NOT the Linux/gcc box that ran E17
(L75) -- it started with no Python packages, no venv, no nauty. Protocol per
[`NIGHT_PLAN_TEMPLATE.md`](NIGHT_PLAN_TEMPLATE.md): gate first, commit only on
green, quarantine everything else to `_NIGHT_FINDINGS.md`, never push.

## The target

L75 carries two caveats "to carry verbatim into any future fold" (they are also
the open items for the C1 amend decision). Caveat (i) is the attackable one:

> enumeration completeness at $n=15,16$ rests on geng plus the verified prune
> lemmas, **no independent second enumerator**.

Tonight attacks that caveat with a *different technology* (SAT, not canonical
augmentation), and then tries to convert the same machinery into the "qualitatively
stronger prune" L75 names as the prerequisite for breaking the $n=17$ wall.

Key logical fact that scopes what SAT can and cannot do here:

- "the class is EMPTY at order $n$" is an $\exists$-statement -> **NP** -> a SAT
  UNSAT (with DRAT) is a complete, independent proof.
- "every class member at order $n$ is 5-colorable" is $\exists\forall$ -> $\Sigma_2^p$
  -> **not** SAT-encodable. That part stays geng's job.

So Stage 1 independently re-proves the emptiness half; Stage 2 tries to grow the
emptiness half far enough that it swallows the colorability half.

## Queue

| # | Task | Gate | Risk tier | Outcome |
|---|------|------|-----------|---------|
| 0 | Host bring-up: venv + networkx/python-sat/numpy/scipy/sympy | `smoke_test` 9/9, `smoke_test --full` chi>=5 anchor, `lemma_db.build_db` 0 violations | tooling | **PASS** (9/9; Heule-826 UNSAT@k=4 in 9.5 s; firewall clean) |
| 1 | Build nauty 2.8.9 + `geng_hn` on msys/ucrt64 (second toolchain) | both-free counts 352 / 2001 / 15481 at n=7/8/9; n=13,14 emit 0; n=15 emits 11 | tooling | **PASS**, all four gates reproduced exactly. Needed `./configure` + `-DAVOID_SYS_WAIT_H`; script committed as `e17_build_geng_msys.sh`. Recorded the missing flag context for the 352/2001/15481 numbers |
| 2 | **E18 Stage 1**: SAT class-emptiness, geng-free and KY-free, for n <= 14 | UNSAT + DRAT; encoder validated as a RELAXATION on positive controls at small n | novel | **PASS**. Relaxation gate 11/11. n<=11 UNSAT with no KY at all; **n=12 SAT** (new fact: the class first becomes nonempty at 12); n=13,14 UNSAT with the KY floor, independently of nauty |
| 3 | **E18 Stage 2**: add 6-critical (Gallai low-vertex) structure to the encoding; test whether n=15/16 go UNSAT | non-circular calibration at k=4 (must ACCEPT Grotzsch, REJECT non-critical); any UNSAT cross-checked against geng at n<=15 | novel | **NEGATIVE, gated**. Calibration 5/5 (accepts W5/C5/C7/Moser, rejects Q3). Still SAT at n=15,16,17,18: Gallai's local structure does not empty the space, so it does not break the n=17 wall |
| 4 | **E18 Stage 3** (added mid-run): exhaustive SAT enumeration as the second enumerator | cell EXHAUSTED + class-by-class match against geng | novel | **PASS at n=15**: 1,989 models -> 11 classes, all 11 match geng. n=16 comparison running |

## Soundness contract for Stage 1/2

Every UNSAT claim rests on the encoding being a **relaxation** of the real class:
every graph in the class must satisfy every clause. Enforced two ways:

1. **Positive-control replay**: known members of the class (and, at k=4, known
   critical graphs) are fed to the clause set as fixed assignments and must satisfy
   it. A relaxation failure shows up here as a violated clause.
2. **Model-side independence**: every SAT model is re-verified by
   [`e17_bothfree_filter.py`](../combinatorial/e17_bothfree_filter.py), which is
   disjoint code from the encoder.

DRAT proofs are emitted for the UNSAT runs. `drat-trim` is not on this host; the
proofs are archived for later checking rather than claimed as checked.

## Findings quarantine

`_NIGHT_FINDINGS.md` (dated, append-only).

## Outcome (end of run)

All four queued tasks green; nothing went to `_NIGHT_FINDINGS.md` (no gate failed).
Findings recorded as **L76**. Two items did not finish and are logged as TODOs
rather than claimed: the `gold_*` no-symmetry-breaking re-derivations of $n=13,14$
(one retired at 2.15 GB when host free memory hit 1.9 GB, which put the
enumeration branches at risk of an OOM cascade), and the $m=43$ cell of the
$n=16$ SAT census, which was PARKED after the blocking-clause wall was measured
at two split granularities (see `e18_results.md`); the census stands at
11,312/11,315 classes with zero contradictions.

Headline numbers, all reproduced on this host from a bare start:

| | |
|---|---|
| E17 gates (a)/(b)/(c) | reproduced exactly |
| $n=16$ geng count | **11,315** (matches L75) |
| $n=16$ coloring verdict | 11,291 DSATUR / **24** SAT / **0** hits (matches L75) |
| the 24 residues | **isomorphic to the committed set, 24/24** |
| $n=15$ SAT enumeration | EXHAUSTED, 11 classes, matches geng graph-for-graph |
| $n=16$ SAT enumeration | 11,312 / 11,315 classes, only-in-SAT **0**, violations **0** |
| Gallai prune | calibrated 5/5, still SAT at $n=15..18$, 18% prune vs ~99% needed |
| new fact | the class with $\delta\ge5$ first becomes nonempty at $n=12$ |

**No bound moved. No new $\chi\ge6$ candidate at any order.**

Protocol note: the template says commit on a green gate, but the repo's CLAUDE.md
requires per-action authorization for commits, so the run left everything
uncommitted and reported instead. Owen authorized the commit and push afterwards.
