# E17: exhaustive nauty search of the both-free class (K4-free AND K_{2,3}-free, chi >= 6?)

The door L69 left open, now unblocked by a working C toolchain: enumerate ALL
candidate 6-critical members of the UDG-necessary class per order n with a
custom-pruned geng (nauty 2.8.9), and chi-filter them. A hit would be the first
K_{2,3}-free K4-free graph with chi >= 6 (the necessary combinatorial shape of
any 6-chromatic UDG); a per-n exhaustive miss is a theorem about the class.

Artifacts:
- [`e17_window_table.py`](e17_window_table.py): per-n edge window (KY floor vs codegree ceiling).
- [`e17_prune.c`](e17_prune.c) + [`e17_build_geng.sh`](e17_build_geng.sh): geng PRUNE/PREPRUNE plugin
  (incremental K4 / K_{2,3} rejection + cherry-budget prune), built as `~/.local/bin/geng_hn`.
- [`e17_bothfree_filter.py`](e17_bothfree_filter.py): INDEPENDENT pure-Python both-free filter
  (global algorithm, disjoint code from the C plugin; the double-check layer).
- [`e17_nauty_host_search.py`](e17_nauty_host_search.py): pipeline driver (count-only /
  calibrate / res-mod parallel run with checkpointing under `_cache/e17/`).

## Search-space soundness (what "exhaustive" means here)

Any chi >= 6 member of the class contains a 6-critical subgraph that is itself
in the class (both properties are subgraph-closed). A 6-critical graph is
2-connected (Dirac), has min degree >= 5, m >= (28n-18)/10 (Kostochka-Yancey),
m <= n(1+sqrt(8n-7))/4 (codegree ceiling), and max degree <= (n-1)/2 (in a
codegree-<=-2 graph with mindeg 5: sum_{w in N(a)} (deg w - 1) <= 2(n-1)).
So enumerating geng -C -d5 -D[(n-1)/2] with the per-n edge window and both-free
pruning, then 5-colorability-filtering, decides "does the class contain a
chi >= 6 member on <= N vertices" once all n in [16, N] are complete.
Folkman floor (Lathrop-Radziszowski 2011): no K4-free chi >= 6 graph below
n = 16, so the sweep starts there.

## Window table (e17_window_table.py)

| n | KY floor | ceiling | window | width |
|---|----------|---------|--------|-------|
| 10-12 | 27..32 | 23..31 | EMPTY | - |
| 13 | 35 | 35 | 35..35 | 1 |
| 14 | 38 | 39 | 38..39 | 2 |
| 15 | 41 | 43 | 41..43 | 3 |
| 16 | 43 | 48 | 43..48 | 6 |
| 17 | 46 | 52 | 46..52 | 7 |
| 18 | 49 | 57 | 49..57 | 9 |
| 19 | 52 | 61 | 52..61 | 10 |
| 20 | 55 | 66 | 55..66 | 12 |
| 21 | 57 | 71 | 57..71 | 15 |
| 22 | 60 | 77 | 60..77 | 18 |
| 23 | 63 | 82 | 63..82 | 20 |
| 24 | 66 | 87 | 66..87 | 22 |
| 25 | 69 | 93 | 69..93 | 25 |
| 26 | 71 | 98 | 71..98 | 28 |

The n <= 12 emptiness reproduces the rigorous L63 corollary.

## Calibration gates

| gate | check | result |
|------|-------|--------|
| (a) plugin vs independent filter | geng_hn n=7/8/9 both-free counts vs stock geng piped through `e17_bothfree_filter.py` | PASS: 352 / 2001 / 15481 exact agreement, both before and after adding PREPRUNE + cherry budget; at n=9 the canonically-labeled output SETS are identical (labelg + diff) |
| (b) n=16 m=48 extremal cell | must emit exactly the Shrikhande graph, rejected on chi | PASS: `geng_hn -C -d5 -D6 16 48:48` emits EXACTLY 1 graph; verified 6-regular, all 120 codegrees == 2 (srg(16,6,2,2)), isomorphic to the Cayley-Z4xZ4 Shrikhande construction; portfolio: 3-colorable False, 4-colorable True, so chi = 4 and the pipeline rejects it (the -D6 there is cell-specific: m=48 forces 6-regularity by cherry convexity) |
| (c) Folkman floor | n=13,14,15 full windows must produce 0 chi>=6 hits | PASS: n=13 emits 0 graphs (0.2s), n=14 emits 0 graphs (4.6s), n=15 emits 11 both-free graphs, 9 DSATUR-5-colored + 2 SAT-5-colored, 0 hits (154s wall, 16-way split). Bonus exhaustive verdicts: the class has NO 6-critical candidate at all at n=13,14 and no chi>=6 member at n=15 |
| (d) core gate | `.venv/bin/python -m experiments._shared.smoke_test` | PASS: 9/9 (run after the geng_hn build and driver work) |
| (extra) hit path | M^3(C5) (n=47, chi=6) fed through the exact pipeline code path | PASS: DSATUR fails, in-process Cadical195 says 5-UNSAT, provisional JSON saved, main-process portfolio confirms 5-UNSAT and finds a valid 6-coloring; artifact removed (test, not a hit) |

Engineering note (load-bearing): the portfolio uses multiprocessing SPAWN
children, and a daemonic Pool worker may not spawn; therefore workers persist a
PROVISIONAL hit JSON immediately and the portfolio confirmation runs in the
main process (`finalize_hit`), after stop-the-world.

## Feasibility counts (geng_hn -u, BEFORE the full runs)

| n | window | maxdeg cap | both-free count | cpu cost | verdict |
|---|--------|-----------|-----------------|----------|---------|
| 13 | 35:35 | -D6 | 0 | 0.15 s | trivial, done in calibration |
| 14 | 38:39 | -D6 | 0 | 4.5 s | trivial, done in calibration |
| 15 | 41:43 | -D7 | 11 | ~40 min single-core equiv | done in calibration (split 16) |
| 16 | 43:48 | -D7 | 11,315 (final; the 2/64-part extrapolation of ~6,100 was ~2x low, parts vary) | 66.3 cpu-h actual => 4.4 h wall on 16 cores | LAUNCHED and COMPLETED (output volume vastly below the 1e9 wall) |
| 17 | 46:52 | -D8 | unknown (all 4 sample parts unfinished) | > 80 cpu-days, see below | WALL: do not launch |

The full n=16 -u count was intentionally aborted at 2/64 parts: the count walks
the identical tree as the real run (output volume is negligible), so paying the
count cost twice buys nothing (37 cpu-h was the 2/64-part extrapolation of the
count; the real run's final cost was 66.3 cpu-h, i.e. the extrapolation ran
~1.8x low, consistent with the ~2x-low graph-count extrapolation noted above).
Feasibility was decided from the completed parts.

### The n=17 feasibility wall (measured, not guessed)

Four sample parts of a mod=4096 split (`geng_hn -C -d5 -D8 -u 17 46:52 r/4096`,
r in {0, 1365, 2730, 4095}) each exceeded 1,700 cpu-seconds WITHOUT finishing
(killed at ~28-32 cpu-min each). Lower bound: 4096 x 1700 s > 80 cpu-days,
i.e. > 5 days wall on all 16 cores, and the true number is larger (no sample
part completed). Against the ~12 h wall-time criterion, n=17 is OUT for this
host. The per-n cost multiplier is consistent across the ladder:
n=15 -> n=16 is ~100x (2.4e3 -> 2.39e5 cpu-s final), and n=16 -> n=17 is > 29x
(a 1/4096 slice of n=16 averages 58 cpu-s vs > 1,700 cpu-s unfinished at
n=17), so n=18 is extrapolated at thousands of cpu-days: the
geng-enumeration route saturates at
n = 16 here, and n = 17 would need either ~a hundred cores for a week, or a
substantially stronger prune (e.g. 6-critical/Gallai structure pushed into the
tree, or clique-covering lower bounds), or a smarter canonical-form generator
specialized to near-extremal codegree-2 graphs.

## Run log (auto-appended by the driver)

| n | window | both-free graphs | DSATUR 5-col | SAT 5-col | hits | cpu | status |
|---|--------|------------------|--------------|-----------|------|-----|--------|
| 13 | 35..35 | 0 | 0 | 0 | 0 | 0.2s | complete (calibration) |
| 14 | 38..39 | 0 | 0 | 0 | 0 | 4.6s | complete (calibration) |
| 15 | 41..43 | 11 | 9 | 2 | 0 | 154s wall x16 | complete (calibration) |
| 16 | 43..48 | 11315 | 11291 | 24 | 0 | 238519s cpu (66.3 cpu-h, 15801s = 4.4h wall) | **complete, 0 hits: EXHAUSTIVE VERDICT** |

**VERDICT (2026-07-23): the both-free class contains NO chi >= 6 member on
n <= 16 vertices, exhaustively.** Every one of the 11,315 both-free candidates
in the n=16 window is 5-colorable (11,291 by DSATUR instantly, 24 by
in-process Cadical195); every graph geng_hn emitted passed the INDEPENDENT
Python both-free re-check (0 disagreements across all 11,315 + the 11 at
n=15). Combined with the per-n sweep n=13,14,15 and the Folkman floor, the
smallest K4-free K_{2,3}-free graph with chi >= 6, if one exists, has
n >= 17. (Run log `_cache/e17/run_n16.log`, checkpoint
`_cache/e17/checkpoint_n16_mod128.json`; the run is resumable per res/mod
part by re-running the same command.)

## Wrong-approach detector self-assessment

- **Q^2 (chi = 2)**: the class constraints (K4-free, K_{2,3}-free) are
  NECESSARY conditions for Euclidean UDGs and hold equally for rational-point
  UDGs; nothing in E17 lifts to a chi(Q^2) >= 3 claim. E17 makes NO chi(R^2)
  claim at all: a hit would be an abstract candidate whose UDG realizability is
  a separate, explicitly-open step (the L63/L74 rigidity wall). PASS.
- **L^infty (chi = 4)**: in the L^infty plane two unit spheres can share a
  segment, so codegree is unbounded and the K_{2,3}-free premise dissolves.
  The search is built on strict-convexity rigidity specific to the Euclidean
  norm (two unit circles meet in <= 2 points). An L^infty analog of E17 simply
  does not exist, as required. PASS.
- **R^1 (chi = 2)**: the R^1 UDG has max degree 2; the search space (min
  degree 5) is empty there. PASS trivially.

## Prior art / comparison

- Folkman-number lineage: Lathrop-Radziszowski 2011 established that the
  smallest K4-free graph with chi >= 6 has n = 16 (via enumeration among
  maximal triangle-free-complement structures). E17 refines the question to
  the UDG-necessary BOTH-free class and pushes an exhaustive per-n verdict.
- The extremal calibration object, srg(16,6,2,2) = Shrikhande, is the unique
  K4-free codegree-2 extremal graph at n=16 m=48 (the rook's graph R_4 is the
  other srg with these parameters but contains K4); its chi = 4.
- L63/L65/L67/L69 gave three-directional HEURISTIC negatives (greedy-up,
  anneal-up, repair-down) on in-class chi >= 6 at small n; E17 is the first
  EXHAUSTIVE statement, closing the "maybe the local searches just missed it"
  objection up to the feasibility wall.

## Verification targets (for VERIFIER)

1. Re-run gate (a) with an independent K4/K_{2,3} implementation (or
   networkx): counts 352/2001/15481 at n=7/8/9 for the both-free class.
2. Independently confirm the n=15 exhaustive cell: 11 both-free graphs in
   window 41..43 with -C -d5 -D7, all 5-colorable (second SAT solver).
3. Check the maxdeg cap lemma (deg <= (n-1)/2 under codegree <= 2 and
   mindeg 5) and the cherry-budget inequality in e17_prune.c against the
   written derivations; both are one-paragraph counting arguments suitable
   for Lean formalization.
4. Confirm KY floor arithmetic: 6-critical => m >= (28n-18)/10; at n=16
   ceil(43.0) = 43; and the ceiling floor(n(1+sqrt(8n-7))/4) values in the
   window table.
5. When run_n16 completes: re-verify a random sample of its checkpointed
   per-part counts by re-running those geng_hn parts, and re-decide 5-col
   for any SAT-residue graphs with a different solver.

## Adversarial test cases (for ADVERSARY)

1. Feed the pipeline a graph WITH a K4 and one WITH a K_{2,3} via the Python
   filter (is_k4_free / is_k23_free) and confirm rejection (the selftest
   battery already covers K4, K_{2,3}, C5, Petersen; extend at will).
2. Try to 5-color the two SAT-residue n=16 graphs from the parts log by hand
   / DSATUR with different tie-breaks (they were SAT-5-colorable; a coloring
   exists and DSATUR's failure is heuristic only).
3. Attack the soundness of the incremental PRUNE: construct a both-free graph
   on n vertices whose every one-vertex-extension contains K4 or K_{2,3};
   confirm geng_hn still OUTPUTS the n-vertex graph itself (pruning applies
   to extensions, not the passed graph).
4. Attack -C: exhibit a chi >= 6 both-free graph that is NOT 2-connected
   (impossible: its 6-critical subgraph is 2-connected and still both-free;
   the sweep would find THAT graph at its own n).

## Draft LEARNINGS entry (for SYNTHESIZER)

### L75 (draft). E17: the nauty door of L69 is OPEN and closes with a
THEOREM-GRADE negative: the both-free class (K4-free AND K_{2,3}-free, the
UDG-necessary class) contains NO chi >= 6 member on n <= 16 vertices,
EXHAUSTIVELY, with a measured feasibility WALL at n = 17. The gcc host let
us build `geng_hn` (nauty 2.8.9 geng + custom PRUNE/PREPRUNE plugin
`e17_prune.c`): incremental K4/K_{2,3} rejection at the last-added vertex
(sound+complete by subgraph-monotonicity along geng's augmentation order)
plus a cherry-budget prune (final cherries >= sum C(max(deg,5),2) + 10 per
future vertex vs the K_{2,3} budget 2C(n,2)), plus two NEW sound search-space
caps proved for the class: maxdeg <= (n-1)/2 (codegree <= 2 + mindeg 5 force
sum_{w~a}(deg w - 1) <= 2(n-1)) and 2-connectivity (any chi >= 6 member
contains a 6-critical subgraph; 6-critical graphs are 2-connected with
mindeg >= 5 and KY floor m >= (28n-18)/10; the codegree ceiling
n(1+sqrt(8n-7))/4 is automatic). Calibration: (a) plugin vs an independent
pure-Python filter agrees EXACTLY at n=7/8/9 (352/2001/15481 both-free
graphs; canonical SETS identical at n=9 via labelg); (b) the extremal n=16
m=48 cell emits EXACTLY ONE graph = the Shrikhande srg(16,6,2,2)
(isomorphism-checked vs the Cayley Z4xZ4 construction), chi = 4, correctly
rejected; (c) the Folkman floor holds: n=13/14 windows contain ZERO
both-free graphs at all, n=15 contains 11, all 5-colorable; (d) smoke test
9/9; (extra) the hit path was pre-validated end-to-end on M^3(C_5) (DSATUR
fail -> Cadical 5-UNSAT -> provisional JSON -> main-process portfolio
confirm + valid 6-coloring). THE MAIN RUN: the n=16 full window (43..48
edges, KY floor to codegree ceiling; geng -C -d5 -D7, 128 checkpointed
res/mod parts on 16 cores) completed in 238,519 cpu-s (66.3 cpu-h, 4.4 h
wall): **11,315 both-free candidates, every one 5-colorable** (11,291 by
DSATUR instantly, 24 by in-process Cadical195), 0 independent-filter
disagreements, 0 hits. So with the Folkman floor: the smallest K4-free
K_{2,3}-free chi >= 6 graph, if one exists, has n >= 17. This upgrades the
three-directional HEURISTIC negatives (greedy-up L65, anneal-up L67,
repair-down L69) to an exhaustive statement at the scale where they
operated, and confirms L69's conjecture from the inside: at accessible n the
K_{2,3} violations really are load-bearing for chi = 6. THE WALL: four
sample parts of an n=17 mod=4096 split each ran > 1,700 cpu-s unfinished =>
n=17 > 80 cpu-days on this host (> 5 days on all 16 cores; vs 58 cpu-s per
equivalent n=16 slice, a > 29x per-n multiplier; n=15 -> 16 was ~100x), so
n=17 needs either ~100x compute or a fundamentally stronger prune
(Gallai-tree / 6-critical structure inside the generator, not just
subgraph-freeness). Wrong-approach detectors: PASS (the class premise is
Euclidean strict-convexity rigidity; nothing lifts to Q^2 / L^infty / R^1;
see e17_results.md). Honest scope: this bounds the CLASS, not chi(R^2), and
does not touch the realizability wall (L63/L74); note the codegree
ceiling/KY-floor asymptotics (0.7 n^1.5 vs 2.8n) still guarantee the class
is nonempty of 6-critical candidates for large n, so the object may simply
live beyond enumeration reach. Artifacts:
`combinatorial/e17_*.{py,c,sh,md}`, `~/.local/bin/geng_hn` (rebuildable via
`e17_build_geng.sh`), `combinatorial/_cache/e17/` (checkpoint + run log).
