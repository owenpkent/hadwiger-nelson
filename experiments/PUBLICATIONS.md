# PUBLICATIONS

Publication ledger for the Hadwiger-Nelson program: the place where candidate
publishable discoveries are **tracked** (a registry) and **evaluated** (a rubric).

This is a peer to [`LEARNINGS.md`](LEARNINGS.md) (the raw findings log) and
[`PROOF_ARCHITECTURES_PLAN.md`](PROOF_ARCHITECTURES_PLAN.md) (the experimental
plan). LEARNINGS records *what was found*; this file decides *what is worth
writing up, where, and in what order*. Maintained by SYNTHESIZER.

The discipline mirrors the program's existing honesty: every candidate carries
an explicit scope and the same adversarial scrutiny (wrong-approach detectors,
an ADVERSARY pass) before it ships. We do not over-claim. Most findings here are
honest negatives, diagnostics, or syntheses of known pieces; that is fine, and
the rubric scores it as such rather than inflating it.

---

## How to use this file

1. **A finding lands in LEARNINGS (L_N).** Ask: could anyone outside this repo
   want to cite it? If plausibly yes, give it a candidate ID (C_k) and add a row.
2. **Score it on the rubric** (V, N, S below). Scoring is a judgment call, not a
   computed metric. Be honest: the program's credibility rests on it.
3. **Assign a verdict and priority.** SHIP / DEVELOP / FOLD / PARK / ARCHIVE.
4. **Before SHIP**, a candidate must pass: (a) the relevant wrong-approach
   detector ($\mathbb{Q}^2$, $L^\infty$, $\mathbb{R}^1$), or be explicitly N/A;
   (b) an ADVERSARY pass hunting for the smallest counterexample / overclaim;
   (c) a correctness re-check of every headline number against its cache;
   (d) the **circularity (K1) test** below.
4b. **The circularity (K1) test.** For a candidate $X$, ask both directions: does
   $X$ provably imply $\chi(\mathbb{R}^2) \ge 6$, **and** does $\chi(\mathbb{R}^2)
   \ge 6$ provably imply $X$? If **both**, $X$ is a *reformulation*, not progress;
   it is publishable only as an explicitly-labeled equivalence, never as a step
   toward the bound. Apply this especially to Architecture 4 (Borel / Shelah-Soifer
   restatements) and Architecture 2 ($\chi_m$-SDP restatements), where a relabeling
   can pass (a), (b), and (c) while being circular. This pairs with the
   `bridge_chim_chi` node in [`lemma_db`](lemma_db/) (a $\chi_m$ bound does not
   load-bear an ordinary-$\chi$ target) and the bridge-vs-mirror test in
   [`../docs/researcher_mindset.md`](../docs/researcher_mindset.md).
5. **Log the decision** in the Decision log at the bottom (dated, append-only).

---

## The rubric

Three scored axes (each 0-3), plus readiness, venue, verdict, and priority.

### V - Verification (how decisively is it established?)
- **3** - machine-checked (Lean, sorry-free) **or** solver-certified UNSAT with a
  checkable DRAT proof.
- **2** - rigorous pen-and-paper proof, **or** a computation cross-validated by
  two independent methods/solvers.
- **1** - single-method computation or a heuristic with a strong, clean signal.
- **0** - conjecture / suggestive only.

### N - Novelty (is it new?)
- **3** - new result, not in the literature.
- **2** - new *synthesis* or *framing* of known pieces, or a new computational
  record (a wall crossed for the first time).
- **1** - independent reproduction of a known result.
- **0** - known / elementary; no priority claim.

### S - Significance (does anyone outside care?)
- **3** - moves a bound on $\chi(\mathbb{R}^2)$ or settles a stated open question.
- **2** - a clean decisive negative that *closes a route*, or a citable
  methodological law.
- **1** - a reusable diagnostic or tool others would adopt.
- **0** - internal-only; no external interest.

### Readiness (pipeline stage)
`idea -> notes -> draft -> submission-ready -> submitted -> published`

### Verdict
- **SHIP** - ready or nearly; push to a venue now.
- **DEVELOP** - real content, but needs a write-up or one more result to stand alone.
- **FOLD** - strongest as a section/remark inside another candidate, not its own paper.
- **PARK** - genuine but premature; revisit when its mass or strength grows.
- **ARCHIVE** - recorded for completeness; not independently publishable
  (reproduction / known / internal).

### Priority
- **P1** - act now. Submission-ready or one decision away, with $S \ge 2$,
  $N \ge 2$, no fatal caveat.
- **P2** - next. Solid ($V \ge 2$ or $S \ge 2$) but needs writing or a decision.
- **P3** - later. Reproduction, low novelty, or weakened by a load-bearing caveat.

---

## Registry

| ID | Title | V | N | S | Ready | Venue (target) | Verdict | Pri |
|----|-------|---|---|---|-------|----------------|---------|-----|
| C1 | Forcing-sterility of the realizable lineage + codegree obstruction | 2 | 2 | 2 | submission-ready | arXiv math.CO + Geombinatorics | SHIP | P1 |
| C2 | Portfolio inversion at the SAT phase boundary (Cadical 12h vs Maple 155s) | 2 | 2 | 2 | notes | fold into C3 (decided) | FOLD->C3 | P2 |
| C3 | Structure-first solver + symmetry-broken CNF export (walls crossed) | 3 | 2 | 2 | draft (paper, 7pp, compiles) | arXiv cs.DM tool note / SAT workshop | DEVELOP | P2 |
| C4 | Matrix-free order-2 measurable SDP closes the route at $X_{23}$ | 1 | 2 | 2 | notes + verdict JSON | measurable-chromatic methods note | PARK | P3 |
| C5 | IE-LP + congruence (IEC) self-certification of $\chi_m \ge 5$ | 2 | 1 | 1 | notes | none (reproduction) | ARCHIVE | P3 |
| C6 | Lean formalization of the covering / list-coloring / triple-lift lemmas | 3 | 1 | 1 | code (sorry-free) | formalization note (when mass grows) | PARK | P3 |
| C7 | E17 exhaustive both-free enumeration: no $\chi \ge 6$ member at $n \le 16$ | 2 | 2 | 2 | notes (e17_results.md) | fold into C1 (amend) or C1 follow-up | FOLD->C1 | P1 |

Composite read: **C1 is the one live paper.** C2 and C3 are the two real
secondary products; both are stronger *attached* to or *alongside* C1 than alone.
C4-C6 are honest but not independently publishable as they stand. C7 is a direct
strengthening of C1's codegree-wall pillar; whether it amends C1 pre-upload or
becomes a follow-up is an Owen decision (see the C7 dossier and the decision log).

---

## Candidate dossiers

### C1 - Forcing-sterility + codegree obstruction
- **Source**: LEARNINGS L57-L59 (forcing census), L63 (codegree wall), L69 (core
  intrinsics). Drafted in [`paper/main.tex`](../paper/main.tex).
- **One line**: the realizable $\chi=5$ UDG lineage is forcing-sterile *by
  construction* (vertex-critical, so no forced non-adjacent pair, by the
  Essential-Pair Lemma), confirmed by an exhaustive $1{,}955{,}948$-pair SAT
  census; and the missing $\chi \ge 6$ object is pinched between the
  Kostochka-Yancey floor and the $K_{2,3}$-free codegree ceiling.
- **V=2**: exhaustive solver census (multi-solver), Lemma has an elementary pen
  proof. **N=2**: the Lemma is known (Martin 2009 Thm 3.17, honestly attributed);
  novelty is the *synthesis* + the by-construction observation + the codegree
  pincer. **S=2**: clean negative that reframes the search; no new bound.
- **Wrong-approach detector**: PASS. The codegree argument is genuinely Euclidean
  (two-circle rigidity, fails under $L^\infty$); the Lemma claims no bound, so
  $\mathbb{Q}^2$ is not in tension.
- **Caveats (load-bearing, already in the paper)**: no bound on $\chi(\mathbb{R}^2)$
  moves; the Lemma is elementary/known; the $m/n \approx 4.2$ density figure is
  empirical over ~35 cores, not a theorem.
- **ADVERSARY pass (2026-06-16): PASSED, zero blockers.** Every headline number
  independently re-derived from source and exact (census total 1,955,948, all nine
  Table 1 rows, codegree ceiling at n=16 (=48) and n=18 (floor 57), KY crossover at
  n=13, M^3(C5) 434 violations / max codeg 11, the m=131 / 166-violation floor).
  The Essential-Pair Lemma proof is airtight under line-by-line audit; no overclaim;
  wrong-approach detector passes. SHOULD-FIX items applied: clarified the
  forced-same -> chi>=6 certificate (was an overcomplicated "splice"), led the
  priority attribution with the refereed Jensen-Toft over the unrefereed Martin
  preprint, marked the 1155-vertex caveat as an unpublished program observation,
  deleted the stale build.log. Recompiles clean (10 pp).
- **Decisions (2026-06-16)**: author = "Owen P. Kent / Independent
  researcher / owenpkent@gmail.com" (TODO comment removed from the .tex). Venue =
  **both**: arXiv math.CO for the public record + Geombinatorics submission.
- **arXiv bundle READY (2026-06-16)**: `paper/arxiv/forcing-sterility-arxiv.tar.gz`
  (flat: main.tex + refs.bib + main.bbl), validated to compile standalone WITHOUT
  bibtex (arXiv AutoTeX does not run bibtex), 10 pp / 0 undefined. Form metadata
  (title, abstract, math.CO + math.MG, MSC, comments) in
  `paper/arxiv/ARXIV_SUBMISSION.md`.
- **Remaining to submit (human steps)**: upload the tarball to arXiv (may need a
  one-time math.CO endorsement on a new account); email the same main.pdf to
  Geombinatorics (confirm current editor/process).
- **Verdict**: SHIP, P1. Adversary-cleared, author + venue set, arXiv bundle built.

### C2 - Portfolio inversion at the SAT phase boundary
- **Source**: LEARNINGS L64; write-up
  [`docs/03_research/E14_UDG_class_and_portfolio_findings.md`](../docs/03_research/E14_UDG_class_and_portfolio_findings.md).
  Persisted DIMACS for the 470-edge instance.
- **One line**: on one identical near-threshold $k$-colorability instance,
  **Cadical ran 12+ h without deciding while MapleChrono returned SAT in 155 s**
  (a $\ge 280\times$ heuristic swing), the heavy-tailed behavior expected at a SAT
  phase boundary; the operational law is "run a solver *portfolio*, never a single
  solver" near threshold.
- **V=2** (reproducible, persisted instance). **N=2** (a concrete, citable
  methodological observation in the UDG-SAT setting). **S=2** (a law others doing
  UDG colorability would adopt; retroactively explains the L29/L30 "intractable"
  abandonment).
- **Why FOLD**: too thin for a standalone paper, but a strong subsection of C3's
  tool note. It is the most citable methodological nugget the program has.
- **Decision (2026-06-16)**: fold into **C3**, not C1. C1 is a bound-free
  structural note and is submission-ready; a SAT-methodology remark would dilute
  its focus and disturb a clean draft. The portfolio law is solver methodology =
  C3's territory.
- **Verdict**: FOLD into C3, P2.

### C3 - Structure-first solver + symmetry-broken CNF export
- **Source**: LEARNINGS L65 (hn_solver), L66 (CBJ + nogoods + PyPy), L68
  (watched-literal negative + the symmetry-broken export win). White paper:
  [`docs/03_research/hn_solver_whitepaper.md`](../docs/03_research/hn_solver_whitepaper.md).
- **One line**: a from-scratch, color-symmetry-breaking colorability solver, plus
  a symmetry-broken CNF *export* that lets a production CDCL engine cross walls the
  naive encoding could not - **$M^4(C_5)$ k=6 UNSAT in 22 s, $P_{510}$ k=4 UNSAT in
  1.66 s, de Grey 1585 k=4 UNSAT in 19.5 min**, each with an optional DRAT proof;
  the entire known $\chi(\mathbb{R}^2) \ge 5$ program is now self-certifiable on one
  workstation.
- **V=3** (DRAT-certified, equisat-validated over 1000+ instances, zero verdict
  disagreements). **N=2** (the symmetry break is a standard sound construction,
  honestly flagged; novelty is wiring the program's native break into a portfolio
  and *measuring* that it crosses the walls, plus the self-certification capability).
  **S=2** (reusable tooling; an independent from-the-graph confirmation of the
  $\chi \ge 5$ lineage).
- **Honest boundary (must stay in any write-up)**: symmetry breaking crushes
  *structured* UNSAT but does **not** tame *phase-transition* hardness (the E14
  overshoot instances remain a money pit). Do not conflate the two difficulties.
- **Why DEVELOP not SHIP**: the white paper is a draft and a tooling artifact;
  a publishable version wants a clean benchmark table, the C2 portfolio law folded
  in, and a sharp framing (applied SAT, or an arXiv tool note). Decide venue.
- **Progress (2026-06-16)**: paper draft built at
  [`paper_solver/main.tex`](../paper_solver/main.tex) (7 pp, compiles clean, 0
  undefined refs). C2 folded in as Section "Two methodological findings" (portfolio
  law + regime boundary). Framing: arXiv cs.DM tool note, with the SAT workshop
  (Pragmatics of SAT) as an alternate. Remaining to SHIP: (a) DONE - SAT
  bibliography web-verified (SURVEYOR, all 10 entries against primary sources;
  Heule2018verify upgraded to its published Geombinatorics 28(1):32-50 venue, PySAT
  filled to LNCS 10929:428-437; no TODO-VERIFY markers remain, recompiles clean);
  (b) DONE - ADVERSARY pass run. **Soundness of the symmetry break is WATERTIGHT**
  (exhaustive model-count: the broken CNF has exactly one satisfying assignment per
  coloring-up-to-permutation; 0 false-UNSAT over thousands of SAT+UNSAT instances).
  Most timings reproduce against caches. Found + FIXED: A2 (de Grey 1581 vs 1585
  reconciled), B1 (P510 k=4 is NOT a wall and NOT the historically-abandoned
  instance - it solves naively in ~110s; reframed to ~110s->1.66s ~66x; the genuine
  wall is M^4 k=6; misattribution traced L29/L30->L68->paper), B2 (M^4 26s vs 22s =
  proof emission, flagged), B3 (swing stated as >270x, was >=280x). Blocker A1 =
  the flagship "de Grey 1585 k=4 19.5 min" had NO backing artifact (only a 92-min
  NAIVE cache existed): **RESOLVED** by an actual symmetry-broken solve = **18.1
  min** (1088 s, Cadical195, UNSAT, clique 3; vs 92.2 min naive), persisted +
  reproducible via `combinatorial/e1u_degrey_symbreak_k4.py` (cache gitignored per
  convention; the measured value is recorded in the paper, LEARNINGS L68, and here).
  Paper updated 19.5 -> 18 min in all three places; recompiles clean (7pp).
  (c) decide arXiv cs.DM vs SAT workshop (author already confirmed, shared with C1).
- **arXiv bundle READY (2026-06-16)**: `paper_solver/arxiv/symmetry-broken-sat-arxiv.tar.gz`
  (flat: main.tex + refs.bib + main.bbl), validated to compile standalone without
  bibtex, 7 pp / 0 undefined. Paste-ready metadata (cs.DM primary + math.CO cross,
  MSC, abstract) in `paper_solver/arxiv/ARXIV_SUBMISSION.md`.
- **Verdict**: DEVELOP -> SHIP-ready, P2. **All C3 adversary findings cleared**
  (soundness watertight; all numbers backed), bundle built. Remaining: the venue
  call (arXiv cs.DM default vs SAT workshop) and Owen's upload action.

### C4 - Matrix-free order-2 measurable SDP, route closed at $X_{23}$
- **Source**: LEARNINGS L70 (blocker diagnosis), L71 (matrix-free solver), L72
  (the $X_{23}$ k=4 FEASIBLE verdict). Verdict JSON
  `fractional/e3u_x23_k4_verdict.json`.
- **One line**: a matrix-free linearized-ADMM order-2 measurable SDP solver
  (removing the ~195 GiB RAM wall) RAN on Ambrus's $X_{23}$ and returned a decisive
  negative - order-2 (IEC up to subset size 4) does not certify even
  $\chi_m \ge 5$, and by color-monotonicity cannot reach $\chi_m \ge 6$; **the
  order-2 measurable route is closed.**
- **V=1** (first-order ADMM verdict; validated 3/3 on small configs, but *no
  independent $X_{23}$-scale cross-check* exists - the dense map is the wall the
  solver was built to avoid; "feasible" = absence of a certificate, so there is no
  certificate object to externally verify). **N=2** (the matrix-free build is real;
  the closure is a new negative). **S=2** (closes a route several entries chased).
- **Why PARK**: the V=1 caveat is load-bearing for a *publication* - a referee
  would want either an independent verification or a certifying outcome, and this is
  neither. It is a strong *internal* redirect (throws weight back to the Arch-1
  object) but a weak standalone paper. Revisit if the engineering (matrix-free
  conic solver for symmetry-trivial SDPs) is itself framed as the contribution.
- **Wrong-approach detector**: N/A (O(2)-averaged Euclidean SDP; the e3i/e3j 1D
  control guards the LP lineage).
- **Verdict**: PARK, P3.

### C5 - IE-LP + IEC self-certification of $\chi_m \ge 5$
- **Source**: LEARNINGS L36 (e3j). Self-certified ($m_1 \le 0.246894 < 1/4$,
  repo primal + cvxpy dual at machine precision).
- **V=2** (self-certified, dual gap ~machine precision). **N=1** (independent
  reproduction of Ambrus 2023). **S=1**.
- **Why ARCHIVE**: clean and verified, but it reproduces a published bound; no
  priority. Valuable internally as a checked re-derivation, not as a paper.
- **Verdict**: ARCHIVE, P3.

### C6 - Lean formalizations
- **Source**: TODO "Lean substrate"; `lean/HadwigerNelson/L21CoveringLemma.lean`,
  `L22ListColoring.lean`, plus the triple-lift bridge (memory: L24, DeGreyLowerBound).
- **V=3** (machine-checked, sorry-free). **N=1-2** (formalizing known/own lemmas).
  **S=1**.
- **Why PARK**: a formalization note needs more mass (e.g. the HN-4 $\chi \ge 5$
  bridge end-to-end, or the $\mathbb{Q}^2$ / $L^\infty$ controls formalized) before
  it is a standalone ITP/CPP-style contribution. The corpus is growing in the right
  direction.
- **Verdict**: PARK, P3.

### C7 - E17 exhaustive both-free enumeration (no $\chi \ge 6$ member at $n \le 16$)
- **Source**: LEARNINGS L75. Report + verification/adversary target lists in
  [`combinatorial/e17_results.md`](combinatorial/e17_results.md); artifacts
  `combinatorial/e17_*.{py,c,sh}`, `combinatorial/_cache/e17/` (run log, checkpoint),
  `~/.local/bin/geng_hn` (rebuildable via `e17_build_geng.sh`).
- **One line**: with nauty newly buildable (Linux/gcc host), a custom-pruned geng
  exhaustively enumerated the UDG-necessary both-free class ($K_4$-free AND
  $K_{2,3}$-free) per $n$: **NO $\chi \ge 6$ member exists on $n \le 16$** (the
  $n=16$ window holds 11,315 both-free graphs, every one 5-colorable); the smallest
  such graph, if any, has $n \ge 17$; measured feasibility wall at $n=17$
  ($> 80$ cpu-days on this host).
- **V=2**: exhaustive enumeration with a calibrated generator, cross-checked by an
  independent pure-Python membership filter (exact agreement at $n=7/8/9$, identical
  canonical sets at $n=9$; Shrikhande extremal-cell and Folkman-floor gates pass).
  Not V=3: no end-to-end machine-checked certificate of enumeration COMPLETENESS
  (the two counting lemmas are Lean-suitable and queued for VERIFIER).
- **N=2**: a new computational floor for a class the literature does not treat (the
  Folkman lineage covers $K_4$-free alone; the $K_{2,3}$-free refinement is this
  program's UDG-necessary framing). Arguably N=3 if framed as a standalone
  Folkman-style class result; scored conservatively.
- **S=2**: upgrades C1's codegree-wall pillar from three heuristic negatives
  (L65/L67/L69) to a theorem-grade exhaustive statement for $n \le 16$, and closes
  the small-$n$ in-class search route.
- **Wrong-approach detector**: PASS (Euclidean strict-convexity premise; dissolves
  in $L^\infty$, empty on $\mathbb{R}^1$, no $\mathbb{Q}^2$ lift; see L75).
- **K1 circularity**: clean. The result neither implies nor is implied by
  $\chi(\mathbb{R}^2) \ge 6$; it bounds a necessary class of hosts.
- **Why FOLD**: exactly the shape of a C1 strengthening (one theorem-grade
  statement + a small table), not a standalone paper.
- **Gate before folding**: SATISFIED. The VERIFIER + ADVERSARY passes listed in
  e17_results.md have both COMPLETED, both GREEN (`e17_verification.md`: VERIFIED,
  4/5 targets VERIFIED + 1 VERIFIED-WITH-CAVEAT, zero blocking findings;
  `e17_adversary.md`: PASS, five attack surfaces SOUND). SYNTHESIZER still does not
  edit `paper/main.tex`; the amend-C1-vs-ship-as-is choice remains an Owen decision
  (see decision log).
- **Verdict**: FOLD into C1, P1 (it gates the C1 upload decision, flagged for Owen:
  (A) amend C1 pre-upload after the E17 verifier/adversary passes, or (B) ship C1
  as-is and fold L75 into a follow-up note).

---

## What is NOT a candidate (and why)

Tracked so the bar stays honest. These are real findings that are *not*
independently publishable:
- The reverse-engineering of de Grey 1585 / Polymath 510 structure (L15-L25):
  internal understanding, no external claim.
- The W3 / clamp factorization and the long forcing-search lineage (L51-L62):
  the route's *output* (forcing-sterility) is C1; the intermediate probes are not.
- The host-factory / in-class construction negatives (L63-L69): the *conclusion*
  (codegree wall) is in C1; the individual heuristic negatives are not standalone.

---

## Decision log

Append-only, dated. One line per decision.

- 2026-06-16 - Ledger created. Initial scoring of C1-C6 from program state at
  L72. C1 = the live paper (SHIP/P1). C2 folds into C1 or C3. C3 is the strongest
  secondary product (DEVELOP/P2). C4-C6 parked/archived with reasons recorded.
- 2026-06-16 - Owen: pursue C1 (ship) + C3 (develop). C2 fold decided -> into C3
  (keep C1 bound-free and undisturbed). Tracks opened: C1 ADVERSARY read + number
  re-verify + blocker resolution; C3 tool-note development with C2 as a subsection.
- 2026-06-16 - C3 developed: white paper reshaped into a 7-pp paper draft
  (`paper_solver/main.tex`, compiles clean), C2 folded in as the methodology
  section. C1 ADVERSARY pass launched (background). C3 still needs bib verification
  + an ADVERSARY pass + venue decision before SHIP.
- 2026-06-16 - C1 ADVERSARY pass returned: PASSED, zero blockers, all numbers
  re-derived exact, Lemma airtight. SHOULD-FIX items applied (splice -> direct
  certificate, Jensen-Toft-led attribution, 1155-vtx caveat marked unpublished,
  build.log removed); recompiles clean (10 pp). C1 now adversary-cleared; only the
  two human decisions (author/affiliation, venue) remain before submit.
- 2026-06-16 - Owen decisions: author confirmed as-is (TODO removed from both
  .tex); C1 venue = arXiv math.CO + Geombinatorics (both). Session work committed.
- 2026-06-16 - C1 arXiv bundle built + validated (paper/arxiv/, standalone compile
  no-bibtex, 10pp) with paste-ready metadata. C3 SAT bibliography web-verified by
  SURVEYOR (all 10 entries, primary sources; Heule->Geombinatorics 28(1):32-50,
  PySAT->LNCS 10929). Both "both" tasks done.
- 2026-06-16 - C3 arXiv bundle built + validated (paper_solver/arxiv/, standalone
  no-bibtex compile, 7pp) with paste-ready cs.DM+math.CO metadata. Both papers now
  have validated arXiv bundles; C3 is SHIP-ready pending the venue call + upload.
- 2026-06-16 - C3 ADVERSARY pass: soundness WATERTIGHT (exhaustive model-count),
  but 2 blockers + 3 should-fix on number substantiation/framing. Applied A2/B1/B2/
  B3/C3 text fixes (recompiles clean 7pp). A1 (unbacked de Grey 19.5 min, vs a
  92-min naive cache) RESOLVED: real symmetry-broken de Grey 1585 k=4 run = 18.1 min
  (e1u, persisted), paper updated 19.5->18 min, LEARNINGS L68 corrected. All C3
  adversary findings now cleared; C3 is adversary-clean, pending only the venue call
  + its arXiv bundle.
- 2026-06-16 - Author name finalized to **Owen P. Kent** (was "Owen Kent"). Updated
  both papers + both ARXIV_SUBMISSION.md; PDFs rebuilt and both arXiv tarballs
  regenerated.
- 2026-07-23 - L75 (E17 exhaustive both-free enumeration: no $\chi \ge 6$ member at
  $n \le 16$, wall at $n=17$) evaluated and registered as **C7**: V=2 N=2 S=2, verdict
  **FOLD into C1**, P1. It strengthens C1's codegree-wall pillar from three heuristic
  negatives to an exhaustive $n \le 16$ statement. DECISION FLAGGED FOR OWEN before
  the C1 upload: (A) amend C1 (`paper/main.tex`) with the exhaustive statement first
  (small delta; requires the queued E17 VERIFIER/ADVERSARY passes to clear), or
  (B) ship C1 as-is and fold L75 into a follow-up note. No edit made to
  `paper/main.tex`; C1 remains SHIP/P1 with its built arXiv bundle, not yet uploaded.
- 2026-07-23 - E17 VERIFIER + ADVERSARY passes both returned GREEN
  (`combinatorial/e17_verification.md`: VERIFIED, 4/5 targets VERIFIED + 1
  VERIFIED-WITH-CAVEAT, zero blocking findings; `combinatorial/e17_adversary.md`:
  PASS, five attack surfaces SOUND, closed the residue-persistence caveat by
  re-deriving all 24 SAT residues with 0 disagreements). C7's fold gate is now
  SATISFIED. Two caveats carry verbatim into any fold text: (i) enumeration
  completeness at $n=15,16$ relies on geng + the verified prune lemmas, no
  independent second enumerator; (ii) the two counting lemmas are
  formalization-ready but not yet Lean-proved. The amend-C1-vs-ship-as-is decision
  remains with Owen.
