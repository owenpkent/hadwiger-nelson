# E20: the $\Sigma_2$ collapse

**Question.** Does the UDG-necessary "both-free" class ($K_4$-free, all codegrees
$\le 2$) contain a member with $\chi \ge 6$ on $n$ vertices?

**What changed.** Every prior attack split the two quantifiers: enumerate the class,
then color each member. E17 did it with canonical augmentation (geng + the E17
prune plugin), E18/E19 with SAT modulo symmetries and blocking clauses. Both pay a
cost proportional to the SIZE OF THE CLASS. That is why $n=16$ cost 66.3 cpu-h for
11,315 graphs and why L75 measured the $n=17$ wall at $> 80$ cpu-days.

E20 never enumerates the class. SMS ships a chromatic-number propagator
(`src/graphPropagators/coloringCheck.cpp`, `MinChromaticNumberChecker`) that this
program had never used: on a fully-defined candidate it searches for a
$(k-1)$-coloring and, on finding one, learns the clause "at least one of the
currently monochromatic non-adjacent pairs must become an edge". The $\forall$-half
of the $\Sigma_2$ question therefore becomes clause learning inside the same CDCL
solver whose minimality propagator already owns the $\exists$-half's isomorphism
problem:

```
smsg -v n --min-chromatic-number 6 --dimacs <cell CNF>
    Result: 20 (UNSAT)  ==  no member of that cell has chi >= 6      <- the theorem
    Result: 10 (SAT)    ==  a member with chi >= 6                   <- a hit
```

Cost is now governed by search difficulty, not by class size.

## Soundness

Identical framing to L75/E17; no new burden. Both class properties are
subgraph-closed, so if any member has $\chi \ge 6$ then some 6-CRITICAL member
does, on $n' \le n$ vertices. A 6-critical graph has $\delta \ge 5$, is connected
(indeed 2-connected), meets the Kostochka-Yancey edge floor, and with the class
properties meets the E17 maxdeg lemma $\Delta \le (n-1)/2$. So UNSAT on every cell
of every $n' \le N$ proves the class has no $\chi \ge 6$ member on $\le N$
vertices. The per-cell CNF is the same relaxation-gated `CriticalEncoding` used by
E18/E19, with NO lex-leader clauses (SMS owns canonicity). Gallai's low-vertex
conditions are OFF: sound only for the critical witness, and L76 measured them as
~2 orders of magnitude too weak to be worth the extra argument.

Two structural facts keep the collapse from losing solutions. SMS's minimality
clauses only ever exclude non-lex-minimal labellings, so no isomorphism class is
lost (and the default minimality cutoff makes the check WEAKER, which prunes less,
never more). A learned coloring clause excludes exactly the graphs on which the
witnessing coloring stays proper, all of which are 5-colorable, so it is sound.

Every SAT model at any rung is re-verified by code disjoint from the solver that
produced it: the E17 both-free filter for class membership, the repo's SAT
portfolio for the coloring half. A propagator bug cannot manufacture a hit.

## Calibration ladder (`--calibrate`): ALL RUNGS PASS

Nothing below was trusted before this passed.

| rung | check | expected | measured |
|------|-------|----------|----------|
| A | triangle-free, $\chi \ge 4$, $n=10$ | UNSAT | UNSAT, 0.13 s |
| A | triangle-free, $\chi \ge 4$, $n=11$ | SAT, Groetzsch | SAT 0.37 s; independently $\chi \ge 4$; **isomorphic to Groetzsch**; `J??XQedpfo?` |
| B | $K_4$-free, $\chi \ge 5$, $n=10$ | UNSAT (Jensen-Royle) | UNSAT, 0.26 s |
| B | $K_4$-free, $\chi \ge 5$, $n=11$ | SAT (Jensen-Royle) | SAT 0.32 s, independently $\chi \ge 5$; `J@Tc|^UxFr_` |
| E | $K_6$-free, $\chi \ge 6$, $n=7$ | UNSAT | UNSAT, 0.01 s |
| E | $K_6$-free, $\chi \ge 6$, $n=8$ | SAT | SAT 0.01 s, independently $\chi \ge 6$, **isomorphic to $C_5 + K_3$**; `GLr~~{` |
| C | non-vacuity, every production cell | SAT at $\chi\ge3$, model passes E17 filter | pass (the one exception, $n=15$ $m=43$, is a genuinely EMPTY cell) |
| D | $n=15$ window, $\chi \ge 6$ | UNSAT (L75) | UNSAT, **3.6 s** total |
| D | $n=16$ window, $\chi \ge 6$ | UNSAT (L75 census, L77 SMS census) | UNSAT, **74.3 s** total |

Rung A is the strongest of these: it is an external uniqueness theorem
(Chvatal 1974), it exercises the propagator in BOTH directions, and the returned
model is the Groetzsch graph itself rather than merely something 4-chromatic.

Rung E closes the gap that A and B leave: they exercise the propagator only at
$k=4$ and $k=5$, while production asks $k=6$. A $k$-critical graph has $n=k$ or
$n \ge k+2$ (never $k+1$), so a 6-chromatic graph on 7 vertices must contain
$K_6$, making "$K_6$-free, $\chi \ge 6$, $n=7$" UNSAT; at $n=8$ the join
$C_5 + K_3$ is 6-chromatic with clique number 5, making it SAT. Both land, and the
$n=8$ model is exactly $C_5 + K_3$.

## Measured cost, same verdicts

| window | prior route | E20 | ratio |
|--------|-------------|-----|-------|
| $n=15$ | 420 s (geng, `--calibrate` gate (c), this host, today) | 3.6 s | ~117x |
| $n=16$ | 66.3 cpu-h (L75) / full SMS census (L77) | 74.3 s | ~3200x |
| $n=17$ | $> 80$ cpu-days measured (L75) | **0.83 cpu-h** (1202 s wall on 7 jobs) | $> 2300$x |

## Verdict at $n=17$

**THEOREM: the both-free class has no $\chi \ge 6$ member on 17 vertices.**
All seven cells UNSAT, zero hits, zero unknowns.

| $m$ | 46 | 47 | 48 | 49 | 50 | 51 | 52 |
|-----|----|----|----|----|----|----|----|
| result | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT | UNSAT |
| seconds | 735.7 | 1200.4 | 777.8 | 170.9 | 53.4 | 23.7 | 13.3 |

The dominant cell is $m=46$, which E19 measured at $> 1.15$M isomorphism classes
and which forced that module to be written as a 64-way resumable branch driver. E20
decides it in 736 seconds without emitting a single graph.

This extends the L75 statement (no $\chi \ge 6$ member on $n \le 16$) by one order:
**any both-free host, hence any host for a $\chi \ge 6$ UDG clamp, has $n \ge 18$.**
Artifacts: `_cache/e20/sweep_n17_chi6.json`, `_cache/e20/n17_m*.json`.

## What this does NOT do

It bounds the CLASS, not $\chi(\mathbb{R}^2)$. W3 (unit-distance realizability of
the clamp) is untouched, and the L63 codegree wall still says that manufactured
hosts fail realizability. The value is exhaustiveness: C1's "no small host exists"
claim gets stronger, and the search for the missing object is pushed further from
"more search at small $n$" toward "a new construction principle".

## Controls beyond the ladder

* **Non-vacuity (`--probe`)**: an UNSAT on an EMPTY cell is information-free, so
  every production UNSAT is followed by the same CNF at $\chi \ge 3$, which must be
  SAT with a model the disjoint E17 filter certifies as a genuine class member.
* **Ablation + positive control (`--ablate`), MEASURED at $n=17$, $m=52$**: at fixed $n, m$, decide $\chi \ge 6$
  with (i) the full class, (ii) codegree $\le 2$ dropped, (iii) $K_4$-free dropped,
  (iv) both dropped. Rung (iv) is the end-to-end positive control: in the same
  $n$ / degree / edge-count regime with the class properties removed, the pipeline
  MUST return SAT. If it does, the unablated UNSAT is a fact about the class rather
  than a failure of the search. Rungs (ii)/(iii) measure directly which class
  property does the killing, testing L69's claim that $K_{2,3}$-freeness is
  load-bearing for $\chi = 6$.

  | ablation | result | seconds |
  |----------|--------|---------|
  | class ($K_4$-free + codeg $\le 2$) | UNSAT | 13.3 |
  | drop codeg $\le 2$ ($K_{2,3}$ allowed) | UNKNOWN (900 s cap) | 900.8 |
  | drop $K_4$-free | UNSAT | 17.9 |
  | drop both **[POSITIVE CONTROL]** | **SAT**, model independently $\chi\ge6$ | 409.2 |

  The control PASSES: in the same $n$ / degree / edge-count regime with the class
  properties removed, the pipeline does return SAT, so the unablated UNSAT is a
  fact about the class. The two middle rows localize the obstruction: dropping
  $K_4$-freeness barely changes anything, while dropping the codegree bound leaves
  the cell undecided at 900 s. At this order it is $K_{2,3}$-freeness, the
  constraint that comes from planar unit-distance geometry, that forces
  5-colorability. Direct support for L69.

## The always-on ladder (`--climb`)

`--climb 18 --jobs 7 --timeout 14400 --split-bits 5 --probe` decides every cell of
$n = 18, 19, 20, \dots$ in order. Resumable at cell granularity (a finished cell
caches its JSON and is skipped on restart), so it survives kills and reboots. A cell
exceeding the timeout is retried as 32 independent unit-clause branches, each itself
cached and resumable; the cell is UNSAT iff every branch is. The ladder stops loudly
on the first hit, or on the first cell that survives even the split, and records
where it stopped. State: `_cache/e20/climb.json`.

Each rung is a theorem-grade statement of the form "no $\chi \ge 6$ both-free graph
exists on $\le N$ vertices", which is exactly the exhaustiveness claim C1 leans on.

## Reproduce

```bash
python -m experiments.combinatorial.e20_sigma2 --calibrate      # the ladder, ~2 min
python -m experiments.combinatorial.e20_sigma2 --window 17      # cells of n=17
python -m experiments.combinatorial.e20_sigma2 --n 17 --sweep --jobs 7
python -m experiments.combinatorial.e20_sigma2 --ablate --n 17 --m 52 --timeout 900
python -m experiments.combinatorial.e20_sigma2 --climb 18 --jobs 7 --timeout 14400 --probe
```

Host: Linux, 8 cores, 31 GB. `smsg` built from source at
`~/.local/bin/smsg` (SMS `63958bd`, bundled `cadical_sms`, Boost 1.83 user-local at
`~/.local`; no root needed). Repo gates green on this host: `smoke_test` 9/9,
`lemma_db` firewall 0 violations, and the full E17 nauty calibration
(`e17_nauty_host_search --calibrate`) ALL GATES PASS, including the Shrikhande
extremal cell and the $n=15$ window at 420 s.
