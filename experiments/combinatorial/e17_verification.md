# E17 verification report (VERIFIER pass)

Date: 2026-07-23. Verifier: independent VERIFIER agent run.
Scope: the five verification targets listed in
[`e17_results.md`](e17_results.md), section "Verification targets (for
VERIFIER)". All scratch artifacts live under
`experiments/combinatorial/_cache/e17/verify/`. All Python via
`.venv/bin/python` from the repo root; geng binaries from `~/.local/bin`
(custom `geng_hn`, stock `geng`, `labelg`).

Environment note: an ADVERSARY agent was running its own E17 re-runs
concurrently on this host (`_cache/e17/adversary/`, including re-runs of the
n=16 residue parts and an n=15 split-consistency check). This inflates my
wall-clock times relative to the original run but has no effect on any count
or decision below. Timing columns in this report are therefore not
comparable to the originals and are not used as evidence.

Independence discipline used throughout: the recount filter
(`verify/v1_recount.py`) was written fresh from the mathematical definitions
(networkx decoding, clique enumeration for K4, common-neighbor pairs for
K_{2,3}); it shares no code or algorithm shape with either `e17_prune.c`
(incremental frontier checks) or `e17_bothfree_filter.py` (bitset edge
walks). SAT decisions in this pass use Glucose4 via pysat with a
freshly-written direct CNF encoding (`verify/v2_n15_cell.py:kcolor_glucose4`),
distinct from the pipeline's Cadical195 + `_shared.build_color_cnf` path;
every SAT model was decoded and re-checked edge-by-edge.

## Target 1: independent recount of gate (a), n = 7/8/9

Claim checked: stock geng output piped through an independent both-free
filter yields 352 / 2001 / 15481 both-free graphs at n = 7 / 8 / 9, in exact
agreement with `geng_hn`.

Commands and results (filter = `verify/v1_recount.py`, my own code):

```
~/.local/bin/geng -q 7 | .venv/bin/python v1_recount.py   -> 352 both-free of 1044
~/.local/bin/geng -q 8 | .venv/bin/python v1_recount.py   -> 2001 both-free of 12346
~/.local/bin/geng -q 9 | .venv/bin/python v1_recount.py   -> 15481 both-free of 274668
~/.local/bin/geng_hn -u 7   -> >Z 352 graphs generated
~/.local/bin/geng_hn -u 8   -> >Z 2001 graphs generated
~/.local/bin/geng_hn -u 9   -> >Z 15481 graphs generated
```

All three counts match the claimed 352 / 2001 / 15481 on both sides. The
totals 1044 / 12346 / 274668 are the known counts of all graphs on 7/8/9
vertices, confirming stock geng ran unconstrained (as in gate (a)).

Set-level check at n = 9 (stronger than counting): both 15481-line sets were
canonically labeled with `labelg -q`, sorted, and diffed:

```
labelg -q n9_stockgeng_myfilter.g6 | sort > n9_mine_canon.g6
labelg -q n9_genghn.g6            | sort > n9_genghn_canon.g6
diff -q ...  -> CANONICAL SETS IDENTICAL
```

**Status: VERIFIED.** 352 / 2001 / 15481 reproduced with independent code;
canonical sets identical at n = 9.

## Target 2: the n = 15 exhaustive cell

Claim checked: `geng_hn -C -d5 -D7 15 41:43` emits exactly 11 both-free
graphs, all 5-colorable.

Command (16-way res/mod split, `verify/v2_n15_cell.py`):

```
geng_hn -C -d5 -D7 -q 15 41:43 r/16   for r = 0..15
```

Result: exactly **11 graphs**. For every one of the 11: my independent
filter confirms K4-free and K_{2,3}-free; n = 15 with m in {41, 42} (inside
the window 41..43); degrees within 5..6 (respecting -d5/-D7); biconnected
(respecting -C); and **Glucose4 (pysat) finds a 5-coloring**, which I
decoded and validated edge-by-edge. The 11 canonical graph6 strings:

```
N?B@cXgULcKwtEiYBY_  N?`aaioIfDRcMSRdXHO  N?`adQWophLgKuUhWf?
N?`adQWorWEcUiKtWe_  N?`aeQSKbIfcicUpQN?  N?`bCbKTTSEWNEUhWZ?
N?`bCbKsPwEWieUhSk_  N?bB@aWYaiE[UMjSWs_  N?bB@aidaiLGeTUiSl?
N?r@`aiXcqIgUedhSj?  NCOce_iRBRSsFcpTEhO
```

Bonus reproduction of the pipeline's heuristic split: applying the driver's
own `dsatur_colors` to the 11 gives 9 DSATUR-5-colored and 2 residues
(`N?B@cXgULcKwtEiYBY_`, `N?`adQWophLgKuUhWf?`), matching the claimed 9 + 2;
both residues are 5-SAT per Glucose4.

**Status: VERIFIED.** 11 graphs, 0 chi >= 6 hits, second solver (Glucose4)
agrees on 5-colorability of every graph, colorings certificate-checked.

## Target 3: the two counting lemmas vs the C code

### Lemma A (maxdeg cap): full derivation

Let G be K_{2,3}-subgraph-free on n vertices with min degree >= 5.
K_{2,3}-freeness as a SUBGRAPH is equivalent to: every pair of distinct
vertices has at most 2 common neighbors (three common neighbors of any pair
form a K_{2,3}; a possible edge inside the pair is irrelevant for subgraph
containment). Fix a vertex a and count the pairs (w, x) with w in N(a),
x ~ w, x != a:

    S = sum_{w in N(a)} (deg(w) - 1).

Grouping by the endpoint x: for fixed x != a the number of admissible
midpoints w is |N(a) cap N(x)| = codeg(a, x) <= 2, and there are at most
n - 1 endpoints, so S <= 2(n - 1). Since every deg(w) >= 5, S >= 4 deg(a).
Hence 4 deg(a) <= 2(n - 1), i.e. deg(a) <= (n - 1)/2, and by integrality
deg(a) <= floor((n - 1)/2).

Code check: `maxdeg_cap(n) = (n - 1) // 2` in `e17_nauty_host_search.py`;
the run artifacts used -D6 at n = 13, 14, -D7 at n = 15, 16, -D8 at n = 17,
each equal to floor((n-1)/2). No off-by-one. (At n = 16 the cap 7 is not
tight: the extremal Shrikhande graph has maxdeg 6; a cap only needs
soundness.)

Empirical corroboration (exhaustive at n = 11, 12): any mindeg-5 graph on
n = 11 or 12 with a degree-6 vertex has m >= 31 (n=12) resp. m >= 28
(n=11), so the spaces below cover ALL such graphs up to the stated maxdeg:

```
geng -q -C -d5 -D6 11 28:33 | v1_recount.py  -> 0 both-free of 187,990
geng -q -C -d5 -D6 12 31:36 | v1_recount.py  -> 0 both-free of 10,614,224 (6-way split)
```

Zero both-free graphs with maxdeg 6 at n = 11, 12, exactly as the cap
(floor((n-1)/2) = 5) predicts.

### Lemma B (cherry budget): full derivation

Cherries (paths of length 2, distinct midpoint, unordered endpoints)
satisfy #cherries(G) = sum_v C(deg v, 2); double-counting by endpoint pair,
#cherries = sum over unordered pairs {x,y} of codeg(x, y). In a
K_{2,3}-free graph on N vertices every codegree is <= 2, so

    #cherries <= 2 C(N, 2) = N(N - 1).

C code: `budget = (long)maxn * (maxn - 1)`. Constant matches (N = maxn).

geng appends vertex n-1 joined to a subset of {0..n-2}: existing degrees
never decrease, and the FINAL graph must satisfy mindeg >= geng_mindeg (md)
and m >= geng_mine. For every completion G_final of the current partial g:

1. Each current vertex u finishes with degree >= max(deg_g(u), md), and
   C(., 2) is nondecreasing, so it contributes >= C(max(deg_g(u), md), 2)
   cherries. C code: `e = POPCOUNT(g[u]); if (e < md) e = md;
   lb += e*(e-1)/2`. Matches.
2. Each of the maxn - n future vertices finishes with degree >= md:
   >= C(md, 2) each. C code: `lb += (maxn - n) * md * (md - 1) / 2`
   (exact integer division: md(md-1) is even). Matches.
3. Let F = sum of the degree floors above
   (`degsum = sum max(deg_g(u), md) + (maxn - n) * md`). Final degree sum
   = 2m >= 2*geng_mine, so if 2*geng_mine > F at least 2*geng_mine - F
   degree units are added ABOVE the floors. Raising a degree from d (>= its
   floor >= md) to d+1 adds exactly d >= md cherries, so each unit adds
   >= md. C code: `if (2L * geng_mine > degsum)
   lb += (2L * geng_mine - degsum) * md`. Matches (and degenerates to
   adding 0 when md = 0, which keeps the bound valid, as the header
   claims).

So lb <= #cherries(G_final) for every reachable completion meeting -d/-e;
if lb > budget, no completion is K_{2,3}-free and the subtree can be pruned
without losing any output graph (completeness); pruning never adds outputs
(soundness of the emitted set is anyway re-checked graph-by-graph by the
pipeline's independent Python filter).

Strictness check (the one place an off-by-one would bite): the C test is
`lb > budget`, strict, so partials meeting the budget exactly survive. This
is necessary: equality is attained (Shrikhande at n = 16, m = 48 has all
120 codegrees = 2, cherries = 240 = 16*15 = budget), and a `>=` here would
silently kill the extremal cell that gate (b) depends on. Correct as
written.

### Incremental K4 / K_{2,3} rejection: constants

geng.c's PRUNE contract (nauty 2.8.9 source, read directly) states each
intermediate graph is an induced subgraph of all later ones, vertices are
added in order 0, 1, 2, ..., and "a call to PRUNE for n implies that the
call for n-1 already passed"; PREPRUNE "has the same meaning but is applied
earlier and more often". Both target properties are subgraph-monotone, so
checking only violations through the last-added vertex x = n-1 is complete:

- K_{2,3} with highest vertex x on the 2-side: pair (u, x) with
  codeg >= 3. C code case (a): `POPCOUNT(g[u] & nx) >= 3`. Threshold 3
  correct (codegree <= 2 is allowed).
- K_{2,3} with x on the 3-side: the 2-side pair (p, q) is inside N(x) and
  its codegree counting x reaches 3. C code case (b):
  `POPCOUNT(g[p] & g[q]) >= 3` over pairs p, q in N(x); g[p], g[q] include
  the fresh edges to x, so x is counted. Threshold 3 correct.
- K4 through x: an edge (p, q) inside N(x) plus a common neighbor c of p, q
  inside N(x). C code: `(g[p] & bit[q]) && (g[p] & g[q] & nx)`; c != x, p, q
  automatically (no self-loops). Complete: any K4 containing x consists of
  x plus a triangle inside N(x).

The e17_prune.c header's description of the contract matches the geng.c
source text. The `-C` note in geng.c ("connectivity test is done before
PRUNE but not necessarily before PREPRUNE") is irrelevant here because the
prune function does not use connectivity.

### Off-by-one findings

None found. All constants (thresholds 3 and 3, budget N(N-1), C(.,2) integer
divisions, the strict `>`, the (n-1)//2 cap, and the -D values actually
passed per n) check out against the derivations. Two harmless observations,
flagged for completeness:

1. `if (n < 2) return 0;` skips the cherry-budget check at n < 2. A missed
   prune opportunity at trivial levels only; never a correctness issue.
2. `geng_connec` is declared extern but unused. Cosmetic.

### Empirical legs backing the derivations

- Brute-force lower-bound certificate
  (`verify/v3_budget_lb_bruteforce.py`): the C lb formula, reimplemented
  verbatim, was compared against ALL completions of random 5-vertex
  partials to maxn = 8 (every subset of the 18 pairs at the 3 new vertices,
  which is exactly geng's reachable set), over md in {0,2,3} and three
  geng_mine settings per partial: **11,223,395 legal (partial, completion)
  instances, 0 violations of lb <= cherries(completion)**.
- Equivalence with mindeg/edge window active, positive count:
  `geng -q -C -d5 -D5 12 30:33 | v1_recount.py` -> 1 both-free of 7848 vs
  `geng_hn -u -C -d5 -D5 12 30:33` -> 1. Exact agreement.
- Equivalence with the extra-edge budget term active (2*geng_mine exceeds
  the degree-floor sum during the tree walk): n = 12 window 31:36 -D6,
  stock side 10,614,224 graphs -> 0 both-free; `geng_hn -u` -> 0. Agreement
  (both empty; see also the cap-lemma reading of the same run above).

Scope caveat: at the production windows (n >= 13) the stock-geng side is
computationally infeasible (the n = 13 cell alone exceeded 250 s just to
count, and n = 16 is astronomically larger), so no DIRECT stock-vs-geng_hn
equivalence exists at a production n with a positive count. Completeness of
the pruned enumeration at n = 15, 16 therefore rests on: the derivations
above (checked line by line), the geng.c contract, the brute-force
lower-bound certificate, and the small-n equivalences. This is the same
epistemic position as the original campaign, now independently re-derived.

**Status: VERIFIED.** Both lemmas re-derived in full; every constant in
e17_prune.c matches; no off-by-one anywhere; empirical legs all pass.

## Target 4: window arithmetic (exact integers)

Independent recomputation (`verify/v4_window_exact.py`), no floating point:
KY floor as max(ceil((28n-18)/10), ceil(5n/2)) via integer ceiling
division; codegree ceiling as the largest integer m with
2m^2 - nm - n^2(n-1) <= 0 (the exact form of n*C(2m/n,2) <= n(n-1)),
cross-checked against the closed form floor(n(1+sqrt(8n-7))/4) evaluated
exactly via an integer-square comparison ((4m-n)^2 <= n^2(8n-7)). Both
methods agree with each other at every n.

| n | my floor | my ceiling | e17_results.md | diff |
|---|----------|------------|----------------|------|
| 13 | 35 | 35 | 35..35 | none |
| 14 | 38 | 39 | 38..39 | none |
| 15 | 41 | 43 | 41..43 | none |
| 16 | 43 | 48 | 43..48 | none |
| 17 | 46 | 52 | 46..52 | none |
| 18 | 49 | 57 | 49..57 | none |

n = 10, 11, 12 recompute as EMPTY (floors 27/29/32 vs ceilings 23/27/31),
matching the table's "EMPTY" row. Spot check named in the target: at n = 16,
(28*16 - 18)/10 = 430/10 = 43 exactly, so ceil = 43; and 8*16 - 7 = 121 =
11^2 makes the n = 16 ceiling exact: 16*(1+11)/4 = 48.

**Status: VERIFIED.** Zero diffs n = 13..18; emptiness at n = 10..12
confirmed.

## Target 5: n = 16 checkpoint spot re-runs and the SAT residues

Part sample: `random.Random(17).sample(range(128), 8)` =
{6, 28, 44, 71, 74, 77, 93, 106}, plus part 35 added deliberately (the part
with the most SAT residues, 3). The sample happens to include two further
residue parts (77 and 106), so 5 of the 24 residue graphs fall inside the
re-run. Each part re-ran the exact original command

```
geng_hn -C -d5 -D7 -q 16 43:48 r/128
```

with every emitted graph re-checked by my independent both-free filter, the
DSATUR/SAT split reproduced with the driver's own `dsatur_colors`, and every
DSATUR residue decided by Glucose4 (my encoding) with the coloring validated
edge-by-edge (`verify/v5_n16_parts.py`).

| part | gen (mine / checkpoint) | dsatur (mine / ck) | sat (mine / ck) | verdict |
|------|-------------------------|--------------------|-----------------|---------|
| 6    | 45 / 45   | 45 / 45   | 0 / 0 | MATCH |
| 28   | 67 / 67   | 67 / 67   | 0 / 0 | MATCH |
| 35   | 130 / 130 | 127 / 127 | 3 / 3 | MATCH |
| 44   | 64 / 64   | 64 / 64   | 0 / 0 | MATCH |
| 71   | 67 / 67   | 67 / 67   | 0 / 0 | MATCH |
| 74   | 67 / 67   | 67 / 67   | 0 / 0 | MATCH |
| 77   | 67 / 67   | 66 / 66   | 1 / 1 | MATCH |
| 93   | 80 / 80   | 80 / 80   | 0 / 0 | MATCH |
| 106  | 31 / 31   | 30 / 30   | 1 / 1 | MATCH |

9/9 parts reproduce all three checkpoint numbers exactly; 618 graphs
re-emitted, 0 independent-filter failures. The 5 residue graphs recovered
from parts 106, 77, 35 (saved to `verify/n16_recovered_residues.g6`):

```
O?`D@bGSiiFGb_wqLc_kk   (part 106)  glucose4: 5-SAT, coloring validated
O?`D@`WbfOEKdQXoDeedA   (part 77)   glucose4: 5-SAT, coloring validated
O?`D@aWXEQIoJSwkQX_xK   (part 35)   glucose4: 5-SAT, coloring validated
O?`D@aWXAYTI[cdgJDPMQ   (part 35)   glucose4: 5-SAT, coloring validated
O?bB@_WxAUEMigTgrhAPw   (part 35)   glucose4: 5-SAT, coloring validated
```

Each is 5-colorable per Glucose4 (a solver independent of the pipeline's
Cadical195), with the model decoded and re-checked edge-by-edge. This
covers 5 of the 24 SAT residues; the remaining 19 sit in 18 further parts
identifiable from the checkpoint and were not re-enumerated here (timebox;
each part costs ~25-55 min of enumeration to recover a single discarded
graph, which is exactly why the persistence gap below matters).

Residue persistence finding: **the 24 SAT-residue graphs are NOT persisted
anywhere.** `checkpoint_n16_mod128.json` stores only per-part counts
(generated / dsatur_colored / sat_colored), `run_n16.log` the same, and no
`e17_hit_*.json` exists (correct, since there were no hits). The residue
GRAPHS themselves were discarded after the in-process Cadical195 said
5-SAT. The 21 residue-bearing parts are identifiable from the checkpoint
(parts 1, 15, 16, 18, 25, 35, 36, 43, 47, 58, 61, 65, 72, 76, 77, 78, 106,
111, 114, 116, 126; sat_colored sums to 24), so the residues are
recoverable by re-running those parts, as done here for parts 35, 77, 106.
Recommendation for the pipeline: persist the graph6 string of every
SAT-residue graph in the checkpoint (cost: a few bytes per part) so that
solver cross-checks do not require re-enumeration.

**Status: VERIFIED-WITH-CAVEAT.** All 9 sampled parts reproduce the
checkpoint exactly and all recovered residues are second-solver 5-SAT with
validated colorings; the caveat is the persistence gap: the pipeline
discards SAT-residue graphs, so full 24/24 residue cross-checking requires
re-enumerating 21 parts (~10-20 cpu-h). Not a correctness defect, a
reproducibility-cost defect.

## Overall verdict

**E17 VERIFIED (5 targets: 4 VERIFIED, 1 VERIFIED-WITH-CAVEAT), no blocking
findings.** Every recomputed number agrees with e17_results.md: the
352/2001/15481 calibration counts (with canonical-set equality at n = 9),
the 11-graph n = 15 cell (all 5-colorable under a second solver), the two
counting lemmas (re-derived in full; every constant in e17_prune.c correct;
no off-by-one), the exact-integer window table (zero diffs, n = 10..18),
and 9/9 sampled n = 16 parts (618 graphs, counts identical, 5 of 24 SAT
residues recovered and Glucose4-validated). The exhaustive verdict "the
both-free class contains no chi >= 6 member on n <= 16" stands as claimed,
with the epistemic caveats recorded below.

## What this proves / what remains

Proved by this pass (verification level: multi-solver + independent
recomputation; no Lean artifacts yet):

- The E17 pipeline's emitted graph sets, counts, and 5-colorability
  decisions reproduce exactly under independent code paths (my own filter,
  networkx decoding, Glucose4 with a fresh CNF encoding, edge-by-edge
  coloring validation). All 5-colorability claims checked here are
  POSITIVE (SAT) claims carrying explicit coloring certificates, so no
  DRAT/UNSAT machinery is needed for them.
- Lemma A (maxdeg cap) and Lemma B (cherry budget) are correct as
  mathematics and correctly implemented, constants included. Both are
  elementary double-counting arguments over finite graphs: prime
  candidates for Lean 4 formalization (Mathlib `SimpleGraph`, `Finset`
  double counting; no geometry needed). Statements as re-derived here:
  - A: any K_{2,3}-subgraph-free G on n vertices with min degree >= 5 has
    max degree <= floor((n-1)/2);
  - B: any K_{2,3}-subgraph-free G on N vertices has
    sum_v C(deg v, 2) <= N(N-1).
- The window arithmetic (KY floor, codegree ceiling) is exact.

What remains (honest gaps, none blocking within the stated scope):

1. **Enumeration completeness is not machine-checked.** "Exhaustive" rests
   on nauty/geng's canonical augmentation being complete, the PRUNE
   contract, and the two lemmas. I verified the lemmas, the contract text,
   the prune constants, a brute-force certificate of the budget lower
   bound (11.2M instances), and stock-geng equivalences at every
   computationally feasible n (7, 8, 9 unconstrained; 11, 12 with -d5 and
   windows). There is NO independent stock-side enumeration at n = 15, 16
   (infeasible by orders of magnitude), so geng itself remains a trusted
   component, exactly as in the original campaign and in the published
   Folkman-number literature this extends. A Lean-checked enumeration is
   far out of reach; a practical hardening would be a second independent
   generator (e.g. Brendan McKay's geng at a different version, or
   Meringer's genreg-style tooling where applicable) over the n = 15 cell.
2. **SAT residues should be persisted.** Pipeline change requested:
   store the graph6 of every DSATUR-residue graph in the checkpoint.
3. **Lean formalization of Lemmas A and B** is set up by this report
   (statements above) but not attempted in this pass; the repo's
   `lean/HadwigerNelson/` currently has no E17-adjacent file. Status of
   the two lemmas: Reduced (to elementary Mathlib-formalizable
   statements), not yet Proved-in-Lean.
4. The n = 17 wall measurements and the feasibility extrapolations in
   e17_results.md were NOT re-verified (outside the five listed targets).

Axiom set: standard informal mathematics only (finite combinatorics; no
choice-sensitive content anywhere in E17: all objects are finite). No
`sorry`, no `axiom`: nothing Lean-side was produced to contain either.

Publication-fold note (C7 into C1): nothing here blocks the fold. The two
caveats to carry verbatim into the atlas text: (i) enumeration
completeness at n = 15, 16 relies on geng + the verified prune lemmas, not
on an independent second enumerator; (ii) 5 of the 24 n = 16 SAT residues
were re-verified with a second solver, the other 19 are recoverable but
were not re-enumerated (persistence gap). Neither touches the headline
claim's logic; both are reproducibility-cost findings.
