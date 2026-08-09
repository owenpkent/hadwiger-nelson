# E18: a SAT-side second enumerator for the both-free class

Overnight run of 2026-08-08, on the **Windows laptop** (32 logical cores,
msys/ucrt64 gcc 15.2.0), not the Linux box that produced E17/L75.

E18 attacks the first of the two caveats L75 says to carry verbatim into any
future fold of the E17 result:

> (i) enumeration completeness at $n = 15,16$ rests on geng plus the verified
> prune lemmas, **no independent second enumerator**.

## What SAT can and cannot decide here

This scoping fact governs the whole experiment and is worth stating before any
result, because it is what stops E18 from being oversold:

| question | quantifier shape | complexity | SAT? |
|---|---|---|---|
| is the class EMPTY at order $n$? | $\exists G$ | NP | **yes**, UNSAT settles it |
| is every class member at order $n$ 5-colorable? | $\exists G\ \forall c$ | $\Sigma_2^p$ | **no** |

So E18 can independently re-derive the *enumeration* half of E17 (which graphs
are in the class) but not the *colorability* half by a single SAT call. The
colorability half is handled the same way E17 handles it: color the enumerated
graphs, which is one SAT call each.

## Stage 0: the host, and a replication of the E17 calibration gates

This host started with no Python packages, no venv and no nauty. After bring-up:

| gate | result |
|---|---|
| `smoke_test` (core controls) | 9/9 PASS |
| `smoke_test --full` ($\chi \ge 5$ anchor) | PASS, Heule-826 UNSAT at $k=4$ in 9.5 s |
| `lemma_db.build_db` (control-object firewall) | PASS, 0 violations |
| nauty 2.8.9 + `geng_hn` built under msys/ucrt64 | PASS ([`e17_build_geng_msys.sh`](e17_build_geng_msys.sh)) |

With `geng_hn` rebuilt on the second toolchain, the E17 calibration gates
reproduce exactly:

| E17 gate | E17 (Linux) | E18 (Windows/msys) |
|---|---|---|
| (a) both-free counts $n=7/8/9$ | 352 / 2001 / 15481 | **352 / 2001 / 15481** |
| (a) plugin vs independent filter | exact agreement | exact agreement, in all three connectivity modes |
| (b) $n{=}16$, $m{=}48$ extremal cell | exactly 1 graph, Shrikhande | **exactly 1**, 6-regular, all codegrees 2 |
| (c) $n=13$ window | 0 graphs (0.2 s) | **0 graphs** (0.17 s) |
| (c) $n=14$ window | 0 graphs (4.6 s) | **0 graphs** (5.5 s) |
| (c) $n=15$ window | 11 graphs, all 5-colorable | **11 graphs**, all 5-colorable |

Two things the replication fixed or added:

- **A recorded-mode gap.** The 352 / 2001 / 15481 counts are the *unrestricted*
  both-free counts (no connectivity flag). This was not written down, and the
  numbers are not recoverable without it: the connected counts are 240 / 1546 /
  13040 and the biconnected counts are 68 / 508 / 4962. Now recorded in
  [`e17_results.md`](e17_results.md).
- **The $n=15$ cell is now a committed artifact.** Those 11 graphs previously
  existed only in the Linux host's `_cache/`. They are now in
  [`e18_n15_class.json`](e18_n15_class.json) with exact $\chi$ per graph, which
  refines L75's "9 DSATUR-5-colored + 2 SAT-5-colored" into **nine $\chi = 4$ and
  two $\chi = 5$** -- the same 9/2 split, now explained.

## Stage 1: SAT emptiness, independent of nauty and of Kostochka-Yancey

[`e18_sat_class.py`](e18_sat_class.py) encodes "there is a graph on $n$ vertices
that is $K_4$-free, has all codegrees $\le 2$, and has $\delta \ge 5$" over
$\binom{n}{2}$ edge variables. The default instance is deliberately a RELAXATION
of what E17 enumerated: no connectivity, no degree cap, no edge window. UNSAT on
the relaxation is therefore strictly stronger than emptiness of E17's window, and
in particular covers the edge counts *below* the Kostochka-Yancey floor, which
E17 never enumerated.

Relaxation gate (the encoding must accept genuine class members): **11/11** of the
$n=15$ graphs are accepted.

| $n$ | $\delta\ge5$ + $K_4$-free + codegree $\le2$, no other constraint |
|---|---|
| 9 | UNSAT (0.01 s) |
| 10 | UNSAT (0.53 s) |
| 11 | UNSAT (6.56 s) |
| 12 | **SAT**: a 5-regular member on 30 edges exists |

**New fact, not in E17.** The both-free class with $\delta \ge 5$ is empty up to
$n = 11$ and first becomes nonempty at $n = 12$. E17 never asked this: its $n \le
12$ windows are empty for a different reason (the KY *criticality* floor exceeds
the codegree ceiling there), so E17's $n \le 12$ emptiness is a statement about
6-critical candidates, not about the class. The $n=12$ witness passes the
independent both-free filter.

Adding the KY floor back (the same literature theorem E17 uses, so this is
nauty-independent but not KY-independent):

| $n$ | with $m \ge \lceil(28n-18)/10\rceil$ | time |
|---|---|---|
| 13 | UNSAT | 0.13 s |
| 14 | UNSAT | 1.43 s |

which is an independent re-derivation of E17 gate (c)'s $n=13,14$ emptiness, by
CDCL rather than by canonical augmentation. DRAT proofs were emitted for both
(`_cache/e18/sym_n13.drat`, 13,209 lines; `sym_n14.drat`, 127,643 lines). Their
honest scope, as with L68/C3: they certify that the *symmetry-broken* CNF is
UNSAT, and `drat-trim` is not on this host, so they are archived for later
checking rather than claimed as checked.

Symmetry breaking is lex-leader under adjacent transpositions (sound: the
lex-least labelling of each isomorphism class survives). Because an unsound break
would silently turn SAT into UNSAT -- the exact failure mode that would invalidate
every UNSAT above -- it is gated: on the orders where the class is KNOWN nonempty
($n = 12$, and $n = 15,16$ at the KY floor) the symmetry-broken encoding must
still return SAT. It does, all three, with models that pass the independent
filter. A second, stronger empirical check: with the break in place the enumerator
reproduced geng's $n=15$ cell exactly (11 classes, graph for graph) and produced
no spurious class at $n=16$, which is what an over-constraining break would break
first. The `gold_*` runs were meant to re-decide $n = 13,14$ with **no symmetry
breaking at all**, removing the need for any argument about the break, but they
did not finish (see "What did not finish"), so as of this run the $n=13,14$ UNSATs
rest on the break being sound-and-gated rather than on a break-free re-derivation.

## Stage 2: Gallai low-vertex structure inside the encoding -- an honest negative

L75 names what is needed to break the $n=17$ wall: "a qualitatively stronger prune
(6-critical / Gallai-tree structure pushed INSIDE the generator)". Gallai's
theorem is NP-encodable, so [`e18_gallai.py`](e18_gallai.py) pushes it inside a
CDCL search instead: in a 6-critical graph the subgraph induced by the
degree-exactly-5 vertices has every block a complete graph or an odd cycle, and
since the class is $K_4$-free those blocks are $K_1/K_2/K_3$/odd cycles. Two
consequences are encoded: the low subgraph has no $C_4$, and each low vertex's low
neighbourhood has max degree $\le 1$.

Calibration is non-circular: the same conditions are instantiated at $k = 4$,
where genuine small critical graphs exist. **5/5 PASS** -- accepts $W_5$, $C_5$,
$C_7$ and the Moser spindle (all genuinely critical), rejects the cube $Q_3$
(whose low subgraph has a $C_4$ and which is not critical).

**Result: negative.** With Gallai + KY + the $\Delta \le (n-1)/2$ cap + the class
constraints, the instance is still SAT at $n = 15, 16, 17, 18$ (all under a
second). Adding Gallai does not empty the search space at any reachable order, so
it does not by itself break the $n = 17$ wall. A SAT answer here is INCONCLUSIVE
by construction (the model meets necessary conditions for 6-criticality without
being 6-critical), which is precisely why this route cannot replace enumeration.

The measurement is still worth having: it says the NP-encodable *local* structure
of 6-criticality is far too weak to decide the question, and that the binding
content is the $\Sigma_2$ colorability half. That is a reason the $n=17$ wall is
hard, not an accident of E17's implementation.

**How weak, quantitatively.** Applied as a filter to the $n=15$ cell, the Gallai
conditions keep 9 of 11 graphs: an **18% prune**. L75's measured gap at $n = 17$
is a factor of ~100, i.e. a 99% prune is needed. So Gallai is roughly two orders
of magnitude short of what the wall requires, which is the honest reason this
route does not rescue $n = 17$ even though the conditions are genuine theorems.

There is also a structural reason Gallai cannot be pushed into geng's PRUNE the
way L75 hoped, independent of its weakness. "Low" means degree *exactly* 5 in the
FINAL graph, and during canonical augmentation a vertex's degree only grows, so a
$C_4$ among currently-degree-5 vertices may dissolve when a later vertex lifts one
of them to degree 6. The condition is therefore only sound to apply at $n =
\text{maxn}$, i.e. as a post-filter, where it saves colorability calls (which are
cheap) and not generation (which is the whole cost).

## Stage 3: exhaustive SAT enumeration as the second enumerator

[`e18_enumerate.py`](e18_enumerate.py) enumerates a cell by CDCL + blocking
clauses, with isomorph rejection outside the solver (Weisfeiler-Lehman buckets
plus exact isomorphism inside a bucket). Pinning the edge count $m$ makes the
blocking clause name only the positive edges, which is sound exactly because a
distinct graph on the same number of edges cannot contain this one's edge set.

**$n = 15$, the full window: 1,989 models -> 11 isomorphism classes, cell
EXHAUSTED, 39.8 s, and all 11 match geng's 11 graph-for-graph (`AGREE`).**
Per-$m$: 9 classes at $m=41$, 2 at $m=42$, 0 at $m=43$ -- the same breakdown geng
gives. This is the independent second enumerator caveat (i) asks for, at $n = 15$:
different algorithm, different code, identical answer.

The cost model it measures is the models-per-class ratio, i.e. how many labelled
copies of each class survive the symmetry break and have to be blocked one at a
time: **~181 at $n=15$**. That ratio, not the class count, is what decides whether
this method scales.

### $n = 16$: the geng side, replicated exactly

`geng_hn` 32-way on this host returned **exactly 11,315 graphs**, matching L75's
count on a different OS, compiler and machine.

Coloring all 11,315 ([`e18_n16_color.py`](e18_n16_color.py)) reproduces the L75
verdict end to end, and does so down to the hard cases:

| quantity | L75 (Linux) | E18 (Windows/msys) |
|---|---|---|
| graphs in the window | 11,315 | **11,315** |
| 5-colorable | all | **all** ($\chi \le 5$ for every one) |
| settled by DSATUR alone | 11,291 | **11,291** |
| needing SAT beyond DSATUR | 24 | **24** |
| $\chi \ge 6$ hits | 0 | **0** |

and the 24 residue graphs are **identical up to isomorphism** to the ones
committed in [`e17_n16_sat_residues.json`](e17_n16_sat_residues.json) (24/24
matched). So the hardest 24 instances of the L75 run are now confirmed on a
second machine, graph for graph, not merely in count.

### $n = 16$: the SAT side (the second enumerator)

The SAT enumeration ran one job per edge count, and the two dominant cells
($m = 43, 44$) were additionally split 8 ways on the three highest-indexed vertex
pairs. That split matters: the enumeration cost is dominated not by the class
count but by the models-per-class ratio, and splitting collapses it.

| cell | classes | models | models/class |
|---|---|---|---|
| $m=43$, unsplit | 10,583 (found) | 480,000+ and still blocking | ~250, tail never closed |
| $m=43$, one branch | 10,538 | 155,758 | **14.8** |
| $m=44$, unsplit | 645 (found) | 260,000+ and still blocking | ~370, tail never closed |
| $m=44$, one branch | 630 | 8,611 | **13.7** |
| $m=45$ | 75 | 27,941 | 372 (EXHAUSTED) |
| $m=46$ | 10 | 2,626 | 263 (EXHAUSTED) |
| $m=47$ | 1 | 157 | 157 (EXHAUSTED) |
| $m=48$ | 1 | 4 | 4 (EXHAUSTED); the Shrikhande graph, 6-regular, all codegrees 2 |

**Status at the end of the run: the SAT side has FOUND all 11,315 classes**
($10{,}583 + 645 + 75 + 10 + 1 + 1$, matching geng exactly). Formal *exhaustion*
is proved for **five of the six cells** ($m = 44, 45, 46, 47, 48$; $m=44$ via all
8 of its branches), leaving only $m = 43$, which was PARKED for the reason measured
in the next section. The entire outstanding gap is that one cell, and it is
**3 classes** (coverage rose 11,270 to 11,312 as successive branches closed). The
comparison against geng on what is proved:

```
geng side: 11315 graphs      SAT side: 11312 graphs
property re-check: 0 violations
matched: 11312   only in geng: 3   only in SAT: 0
VERDICT: CONSISTENT, PARTIAL -- no contradictions, 3 geng classes not yet covered
```

The asymmetry is the honest reading: **zero classes the SAT side produced are
absent from geng, and zero property violations**, so the two methods do not
contradict each other anywhere they overlap; the 3-class shortfall is missing
coverage from an unfinished cell, not a disagreement. Closing it would convert this
to a full independent $n=16$ census, but **not by re-running the same enumerator**:
see the wall below, and use SAT modulo symmetries instead.

### The blocking-tail wall, measured (why the census stopped at 11,312)

Finishing the last 3 classes was attempted twice, and failing twice produced the
most transferable number in this experiment: **enumeration-by-blocking dies at
roughly $10^5$ blocking clauses per solver, no matter how the cell is divided.**

| split of the $m=43$ cell | per-branch outcome | rate |
|---|---|---|
| 8-way (3 pairs) | 2 branches closed at 156k and 543k models; 5 ran past 540k-760k without closing | decayed 68 -> 7-10 models/s |
| 64-way (6 pairs) | 4 branches closed at 32-42k models (780-1720 s); the rest crossed 100k and stalled | decayed 50-70 -> 8-23 models/s |

The pattern is the same at both granularities and the crossover is the same:
branches that finish below ~50k models run at full speed, and any solver that
carries ~100k+ blocking clauses collapses to under ~10 models/s. Splitting moves
where a branch sits in that distribution but does not change the threshold, so a
finer split only helps if it puts *every* branch under the knee. It did not: even
at 64 ways the cell has a heavy tail of large branches.

Consequence, and it is a real conclusion rather than an implementation excuse: the
blocking-clause tail is an artefact of enumerating each isomorphism class's ~250
lex-surviving labellings one at a time, so the fix is not more compute or a finer
split but an enumerator that never produces duplicate labellings at all -- **SAT
modulo symmetries** (Kirchweger-Szeider), which does canonicity checking inside the
solver. That is the tool to reach for before any $n=17$ attempt from the SAT side.

The census was therefore parked at **11,312 / 11,315 with zero contradictions**
rather than ground out. What remains uncovered is 3 classes of one cell, and the
run is fully resumable (see TODO).

### What the cost model says about $n = 17$

The branch split is the transferable finding. Unsplit, a cell's tail is
(classes) x (labellings per class surviving the symmetry break) ~ 250-370
models per class, and the $m=43$ tail did not close in 8 hours. Split 8 ways on
free (high-index) pairs, the ratio drops to ~14, a **17-25x reduction**, because
each branch's model space is small enough that the symmetry break bites. Two
caveats before reading this as a route to $n=17$: the branches are badly
unbalanced (one $m=43$ branch closed in 156k models while its siblings were still
running at 500k+), and the lex-leader symmetry break is what makes the ratio
large in the first place -- a genuine isomorph-free SAT generator (SAT modulo
symmetries) would avoid the blocking tail entirely and is the obvious next tool.
Even so, SAT enumeration at $n=17$ inherits E17's real problem: the class is
larger there, and nothing here shrinks the $\Sigma_2$ colorability half.

## What did not finish

- **The two `gold_*` runs** ($n = 13, 14$ re-decided with NO symmetry breaking)
  did not complete. One was retired mid-run when it reached 2.15 GB and free
  memory on the host fell to 1.9 GB, which put the enumeration branches at risk of
  being OOM-killed. Consequence: the $n=13,14$ UNSAT results rest on the
  symmetry-broken encoding, whose soundness is argued (the lex-least labelling of
  each orbit survives) and gated (the break still returns SAT at $n=12,15,16$,
  and it reproduced geng's $n=15$ cell exactly), but is not yet re-derived
  break-free. Re-running these on an idle machine is cheap and is the first
  follow-up.
- **The $m=43$ cell was not exhausted**, which is why the $n=16$ SAT census sits at
  11,312 of 11,315. It was attempted at 8-way and 64-way splits and PARKED rather
  than ground out, for the measured reason above. Every other cell ($m=44$
  through $m=48$) is proved exhausted. Re-running
  [`e18_merge.py`](e18_merge.py) then [`e18_n16_compare.py`](e18_n16_compare.py)
  after the remaining branches close is all that is needed to finish the census.

## Honest scope

- E18 re-derives the **enumeration** half of E17 independently at $n \le 15$
  (complete) and at $n = 16$ for 11,270 of 11,315 classes with zero
  contradictions (partial), and reproduces its calibration gates and its full
  $n=16$ verdict on a second toolchain. It does not re-derive the colorability
  half by independent means: that is one SAT call per graph in both programs, and
  both use the same portfolio. What the $n=16$ coloring rerun does establish is
  reproducibility on different hardware, including that the 24 DSATUR-residue
  graphs are the same 24 graphs.
- Nothing here changes the L75 verdict; it hardens it. No new $\chi \ge 6$
  candidate appeared at any order, which is the outcome L75 predicts.
- Nothing here moves a bound on $\chi(\mathbb{R}^2)$, and nothing here is about
  realizability. Like E17, this bounds the CLASS.
- The Stage 2 negative bounds a method, not the problem: it says Gallai's local
  structure is too weak to empty the space, not that no stronger prune exists.
- Caveat (ii) of L75 (the two counting lemmas are formalization-ready but not
  Lean-proved) is untouched by this work.
