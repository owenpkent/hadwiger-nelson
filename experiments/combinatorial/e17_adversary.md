# E17 ADVERSARY report: attack on the both-free exhaustive-search campaign

Target: the E17 claim that the both-free class (K4-free AND K_{2,3}-free) contains
NO chi >= 6 member on n <= 16 vertices, exhaustively, with a measured wall at n = 17
(`e17_results.md`, draft L75). This report attacks the exhaustiveness, not the
honesty of the scope statement (which is already careful: E17 bounds the abstract
class, makes no chi(R^2) claim).

Method: the ADVERSARY re-derives, re-implements, and fuzzes every load-bearing
step with code DISJOINT from the pipeline. Where the pipeline uses a tool
(nauty geng, python-sat), the ADVERSARY uses a second independent implementation
(a hand-written C both-free filter, a fourth K4/K_{2,3} checker, different SAT
solvers with a different variable mapping, a from-scratch prune harness linking
the UNMODIFIED `e17_prune.c`). All scratch under `_cache/e17/adversary/`.

Environment note (not a finding): the harness repeatedly killed long background
jobs mid-run. The residue re-derivation was therefore made crash-safe
(per-part append to `residues.jsonl`, resumable); this did not affect any result,
only the wall-clock path to it.

---

## Attack 1 - PRUNE / PREPRUNE soundness and completeness

Claim under attack: the incremental K4/K_{2,3} check in `e17_prune.c` prunes only
subtrees that cannot yield a both-free output, and never drops a both-free graph.

Evidence.

- **geng.c semantics (nauty 2.8.9, read in full).** PRUNE is called on each
  intermediate and final graph (`geng.c:2221,2250,2346,2374`); PREPRUNE earlier in
  `accept1b/accept2` (`geng.c:1742,1845,1973`). The documented contract (header
  lines 162-195): geng adds vertices 0,1,2,...; every intermediate graph is an
  induced subgraph of all later graphs; "a call to PRUNE for n implies the call for
  n-1 already passed." The plugin's incremental last-vertex-only check is therefore
  complete: since the parent (vertices 0..n-2) already passed, any new K4/K_{2,3}
  must involve x = n-1, and the plugin checks exactly those (codeg(u,x) >= 3;
  pairs in N(x) reaching codeg 3; a triangle inside N(x)). Using the same function
  for PRUNE and PREPRUNE is sound (both reject iff the graph is not both-free).
- **`-d5` constrains only FINAL graphs** (seed attack surface 1). Confirmed in
  source: `if (nx == maxn && xlb < mindeg) xlb = mindeg;` (`geng.c:2213,2338`) --
  the min-degree floor is imposed only at nx == maxn. Construction paths pass
  through low-degree intermediates by necessity (vertex 0 has degree < 5 until
  late), and geng does not prune them. Cross-checked end-to-end: the unique
  both-free 5-regular graph on 12 vertices (whose build path has low-degree
  intermediates) is emitted identically by `geng_hn` and by stock `geng -d5 -D5`
  + the independent filter.
- **Prune-harness fuzz** (`adv_prune_harness.c`, links `e17_prune.c` unmodified):
  - T1 soundness: 400,000 random (partial graph, mindeg, mine) trials. Whenever the
    real prune FIRED (272,589 times), all completions to maxn were brute-forced;
    **0 cases where a pruned partial had a valid both-free completion** with the
    right min-degree and edge window. Teeth check: a mutated prune with a halved
    budget DID produce broken witnesses on the same fuzz, so the test can detect
    unsoundness.
  - T4 completeness: 200,000 random build sequences replaying the prune at every
    order 1..maxn as geng does; of 99,065 that passed all prune calls, **0
    contained K4 or K_{2,3}**. No forbidden subgraph is ever missed.
  - T3 extension semantics (seed attack surface 3): the 16-vertex Shrikhande as a
    PARTIAL of maxn = 17 is NOT pruned (a graph whose every mindeg-5 extension dies
    is still output at its own order); adding a 17th vertex joined to 3 mutual
    neighbors DOES fire (codegree hits 3).
- **Independent re-check in the pipeline itself** never fired: across the 19 of 21
  re-run n=16 residue parts (2,300+ graphs), the ADVERSARY's third both-free
  implementation reported 0 both-free failures, matching the pipeline's own
  independent filter.

Verdict: **SOUND.**

---

## Attack 2 - the cherry-budget prune inequality (newest, least-tested code)

Claim under attack: `lb > budget => no completion is K_{2,3}-free` with the exact
constants in `e17_prune.c` on the safe (non-cutting) side.

Analytic audit. budget = maxn(maxn-1) = 2*C(maxn,2) is the exact max cherry count
of any K_{2,3}-free graph on maxn vertices (every codegree <= 2). The lower bound
lb sums (i) C(max(deg_v, mindeg), 2) over current vertices [final degree >= current
and >= mindeg, both valid], (ii) (maxn-n)*C(mindeg,2) for future vertices, (iii)
(2*mine - degsum)*mindeg for the extra degree units forced by the edge floor
[each unit lands on a vertex already at >= mindeg, adding >= mindeg cherries].
Each term is a genuine lower bound with no double counting, so lb <= (actual final
cherries) for every valid completion; lb > budget therefore contradicts
K_{2,3}-freeness. The strict `>` (not `>=`) is essential and correct.

Empirical teeth.

- **Boundary witness (T2).** The Shrikhande graph has cherries = 240 = budget
  EXACTLY at n = maxn = 16. The real prune (strict `>`) returns 0 (does NOT cut it),
  so the extremal cell survives -- exactly why gate (b) emits it. A mutated variant
  with `>=` returns 1 (WOULD lose the unique extremal graph). The implemented
  constant is thus on the exact safe side, and it is load-bearing to a single
  cherry.
- **Fuzz.** In T1 above, the faithful budget produced 0 broken witnesses over
  400k trials; the halved-budget mutant produced broken witnesses. The
  overcounted-mine mutant was also exercised.
- **End-to-end with the budget ACTIVE (mindeg>0, mine>0).** The n=12 `-d5 -D5`
  30:30 cell (mindeg=5, mine=30) and the n=13 `-C -d5 -D6` 35:35 cell (mindeg=5,
  mine=35) both reproduce exactly against stock geng + independent filter (1 and 0
  graphs respectively), so the budget as configured in the real binary loses
  nothing.

Verdict: **SOUND.**

---

## Attack 3 - search-space reductions: maxdeg cap, -C, edge window, KY floor

Claim under attack: every chi >= 6 member's 6-critical subgraph is both-free,
min-deg >= 5, 2-connected, maxdeg <= (n'-1)/2, and has m in [KY floor, codegree
ceiling] at its OWN order n' <= 16, and the per-n sweep covers every such (n', m').

Evidence.

- **maxdeg cap exhaustively verified** (`adv_maxdeg_lemma.py`). Over ALL both-free
  min-deg-5 graphs (enumerated with NO -D cap) at n = 11,12,13,14, the observed max
  degree never exceeds (n-1)//2; the bound is TIGHT at n=13 (maxdeg 6 = cap 6).
  The lemma proof (sum_{w~a}(deg w - 1) = sum_{x!=a} codeg(a,x) <= 2(n-1), and
  deg w - 1 >= 4 under mindeg 5, so deg a <= (n-1)/2) is confirmed. The general
  window uses -D(n-1)//2 = -D7 at n=16; -D6 appears only in gate (b), where m=48
  forces 6-regularity by cherry convexity.
- **KY floor is a valid lower bound at these small n**, and its applicability range
  is fine: Kostochka-Yancey holds for every k-critical graph with k >= 4 (no
  small-n exception; tight at K_6, n=6, m=15). Direct test: below-floor both-free
  min-deg-5 2-connected graphs DO exist (n=13: one graph at 33 edges vs floor 35;
  n=14: 53 graphs at 35-37 edges vs floor 38) and **every one is 5-colorable**, so
  the floor discards only non-critical graphs, exactly as the theorem guarantees.
  A 6-critical graph would have m >= floor and would not be discarded.
- **Exact-integer window audit** (no floating point): the script's `ky_floor`,
  `codegree_ceiling` agree with a from-scratch pure-integer recomputation for all
  n in [6,32]; endpoints round in the safe direction (ceil for the floor, floor for
  the ceiling); the window is EMPTY for every n' in [6,12], covering the small n'
  the results table abbreviates.
- **-C (2-connectivity) soundness** (seed attack surface 4). 6-critical graphs are
  2-connected (Dirac). Demonstrated at chi=4 scale: two W5 wheels glued at one rim
  vertex form a both-free chi=4 graph WITH a cutvertex; -C would skip it, but its
  4-critical block (a single W5) is 2-connected, both-free, and found at its own
  order n=6. No critical object is lost, because the sweep needs only the critical
  block, at its own n'.
- **Per-n coverage.** n' in [6,12] window-empty (rigorous arithmetic); n' = 13,14
  emit 0 both-free graphs (`geng_hn` re-run); n' = 15 emits 11, all 5-colorable;
  n' = 16 emits 11,315, all 5-colorable. Union covers every n' from 6 to 16.

Verdict: **SOUND.**

---

## Attack 4 - the chi filter (DSATUR fast path + SAT fallback + residue decisions)

Claim under attack: no graph is wrongly discarded as 5-colorable, so any genuine
5-UNSAT (a hit) would survive; the discard rule "5-colorable => not a hit" is sound.

Evidence.

- **The recheck guard actually fires.** Feeding the exact worker `process_cell()`
  via a fake generator: a Petersen plant takes the DSATUR-discard path; a K4 plant
  and a K_{2,3} plant each make the worker RAISE `PLUGIN BUG` (the guard is not
  dead code). (Seed attack surface 1: is_k4_free/is_k23_free reject on both.)
- **No discard on a FAILED DSATUR without the SAT fallback.** Confirmed in the
  worker source and exercised: dsatur=None -> `sat5_inprocess` -> discard only if
  that returns True.
- **DSATUR never returns an improper coloring** (`adv_dsatur_fuzz.py`): 440,922
  calls over both-free graphs at n=9..12 for k in {3,4,5}, **0 improper colorings**.
  So a non-None DSATUR result is always a genuine proper coloring; a 5-UNSAT graph
  can never be discarded by the fast path. This closes the "DSATUR bug hides a hit"
  hole GENERALLY, not just on the sampled graphs.
- **Hit path validated end-to-end through the exact worker code** (seed attack
  surface / gate extra): M^3(C5) minus a vertex (chi = 5) is correctly discarded
  (DSATUR / in-process Cadical both find a 5-coloring; independently chi = 5 exactly
  via minisat22 5-SAT + glucose42 4-UNSAT). M^3(C5) itself (chi = 6): DSATUR fails
  -> in-process Cadical 5-UNSAT -> provisional JSON -> `finalize_hit` portfolio-
  confirms 5-UNSAT and returns a valid 6-coloring (validated edge-by-edge);
  independent minisat22 also 5-UNSAT.
- **All 24 SAT-residue graphs re-derived and independently colored** (seed attack
  surface 2). The pipeline never persisted them, so the ADVERSARY re-ran all 21
  n=16 parts whose checkpoint showed sat_colored > 0 (crash-safe, resumable). All
  21 parts completed and match the checkpoint EXACTLY (2,600 graphs re-generated;
  generated / dsatur / residue counts all agree), with **0 both-free failures** and
  **0 DSATUR-coloring-validation failures**. All 24 residues were each decided by
  FOUR independent methods -- glucose42 and minisat22 (their own variable mapping),
  the pipeline's Cadical195, and randomized-greedy -- and every one is 5-colorable
  (in fact 4-colorable, chi-exactly-5 count = 0), with **0 disagreements** across
  all methods and all 24 graphs. Not one residue is a hidden hit.
- **The SAT encoding is itself correct**: `build_color_cnf` gives the right verdict
  on K3..K7 (5-colorable iff n<=5) and C5 (2-UNSAT, 3-SAT).

Verdict: **SOUND.** No residue is a hidden hit (24/24 confirmed, 0 disagreements).

---

## Attack 5 - wrong-approach detector self-assessment

Audited against the repo control-object discipline (CLAUDE.md).

- **Q^2 (chi = 2).** E17 is a NON-EXISTENCE result about an abstract graph class;
  it proves an UPPER bound (5-colorability) on class members, not a lower bound, so
  the Q^2 detector (which catches false LOWER-bound arguments) is structurally
  inapplicable. The real safeguard is that the class is a correct NECESSARY
  over-approximation of Euclidean UDGs: K4-free (a unit-distance K4 needs a regular
  tetrahedron, impossible in R^2) and K_{2,3}-free (two vertices at unit distance
  from 3 common points would put 3 points on the intersection of two unit circles,
  which meet in <= 2 points). Both hold for rational-point UDGs too, and nothing in
  E17 lifts to chi(Q^2) >= 3. PASS.
- **L^infty (chi = 4).** In the L^infty plane two unit spheres can share a segment,
  so codegree is unbounded and the K_{2,3}-free premise dissolves. The class is
  built on Euclidean strict-convexity rigidity; an L^infty analog of E17 does not
  exist. PASS.
- **R^1 (chi = 2).** The R^1 UDG has max degree 2; the min-degree-5 search space is
  empty. PASS trivially.

Caveat: because E17 is a non-existence theorem rather than a lower-bound method, the
three detectors are partly vacuous here; the load-bearing sanity check is the
necessity of K4-free AND K_{2,3}-free for R^2 UDGs, which holds. The results file's
honest-scope line ("this bounds the CLASS, not chi(R^2)") is accurate.

Verdict: **SOUND-WITH-CAVEAT** (detectors pass but are partly inapplicable by
construction; the operative safeguard, class necessity, is verified).

---

## Independent calibration reproduction (not one of the five, but load-bearing)

- **Gate (a) reproduced two independent ways.** Exact both-free counts 352 / 2001 /
  15481 at n = 7/8/9 (`geng_hn -u` vs stock `geng | filter`). Canonical SETS
  identical at n=9 between `geng_hn` and a hand-written C both-free filter
  (`adv_k23filter.c`, a FOURTH implementation) piped from stock geng. Positive-count
  set identity at n=12 `-d5 -D5` (1 graph) and n=12 `-C -d5 -D5` (1 graph, -C
  included) against the C filter.
- **Gate (b) reproduced independently** (`adv_shrikhande_chi.py`): the n=16 m=48
  cell emits exactly 1 graph = Shrikhande srg(16,6,2,2) (6-regular, all 120
  codegrees 2), isomorphic to the Cayley Z4xZ4 construction, chi = 4 exactly
  (3-UNSAT under glucose42 AND minisat22; 4-SAT with an edge-validated coloring).
  Correctly rejected, not a false hit.
- **Gate (c) reproduced at the boundary**: stock `geng -k -C -d5 -D6 13 35:35`
  generated 70,707,289 K4-free graphs; the independent C filter found 0 both-free,
  matching `geng_hn`'s 0. `geng_hn` re-run gives 0 at n=13,14.
- **Gate (d)**: core smoke test 9/9.
- **res/mod partition is exact** (attack on the split the n=16 verdict depends on):
  at n=15, the mod=16 and mod=64 unions have IDENTICAL canonical sets (11 graphs).
  A 3-way check including the unsplit run is in progress. Two different split
  granularities partitioning the same set identically is the key evidence that the
  128-way n=16 split loses / duplicates nothing.
- **Binary provenance**: `geng_hn` rebuilt from source produces a byte-identical
  canonical output set to the installed binary on the n=12 cell.

---

## Overall verdict: PASS

The E17 exhaustiveness claim survives sustained adversarial attack on all five
priority surfaces plus independent calibration reproduction. No BROKEN finding, no
counterexample, no 5-UNSAT residue, no lost graph. The single novel C component
(`e17_prune.c`) is fuzz-verified sound and complete; the two novel lemmas (maxdeg
cap, cherry budget) are confirmed by both exhaustive small-n enumeration and the
boundary witness; the chi filter cannot discard a hit; the wrong-approach detectors
pass on the operative (necessity) reading.

PASS means "survives this attack," not "certified correct": undiscovered failures
outside the tested surfaces remain possible, and the exhaustiveness rests on the
correctness of mature but here-unverified nauty machinery (-C, -d, -D, res/mod),
which the ADVERSARY has cross-checked against an independent generator + filter for
n <= 14 and via mod16 = mod64 partition agreement.

### Blockers to the C7-into-C1 publication fold

None are soundness blockers. Conditions / notes for the fold:

1. **Framing (must-carry, not a defect).** The result is a NON-EXISTENCE THEOREM
   about the abstract both-free class for n <= 16, with a measured feasibility wall
   at n = 17. It moves no bound on chi(R^2) and does not touch UDG realizability
   (the L63/L74 wall). The results file and draft L75 already state this; the
   publication must keep that scope explicit.
2. **Trust base.** Exhaustiveness = (nauty geng correctness) AND (PRUNE plugin
   soundness+completeness) AND (chi filter soundness). Only the middle and last are
   novel and both are verified here; the geng dependency is cross-checked but not
   formally proved. State this trust base in the write-up.
3. **Formalization gap (VERIFIER hand-off).** The maxdeg cap and cherry-budget are
   one-paragraph counting arguments; neither is Lean-formalized yet. Not a blocker
   (both hold under exhaustive small-n checks and the boundary witness), but worth a
   note if the fold claims machine-checked status.
4. **Residue completeness: CLOSED.** All 24 of 24 n=16 SAT-residues are
   independently re-confirmed 5-colorable (indeed 4-colorable) with 0
   disagreements across four methods; all 21 residue parts match the checkpoint
   with 0 both-free and 0 coloring-validation failures (`residues.jsonl`,
   `adv_residue_attack.json`). No open residue.

Artifacts (all absolute):
`/home/owen/Documents/dev/hadwiger-nelson/experiments/combinatorial/_cache/e17/adversary/`
  - `adv_prune_harness.c` (T1-T4 prune fuzz, links `e17_prune.c` unmodified)
  - `adv_k23filter.c` (fourth independent both-free filter)
  - `adv_maxdeg_lemma.py` (maxdeg cap + KY-floor exhaustive attack)
  - `adv_connectivity_demo.py` (-C / critical-block demonstration)
  - `adv_chifilter_plants.py` (fake-geng plants + Mycielski worker path)
  - `adv_dsatur_fuzz.py` (DSATUR properness, 440k calls)
  - `adv_shrikhande_chi.py` (independent gate (b))
  - `adv_residue_capture.py` + `residues.jsonl` + `adv_residue_attack.json`
    (crash-safe residue re-derivation + independent multi-solver attack)
  - `adv_n15_splitconsistency.sh` + `n15_*.canon` (res/mod partition check)
