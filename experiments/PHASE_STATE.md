# PHASE_STATE

The single operational state file for the Hadwiger-Nelson program. Adapted from
the zeta repo; see [`ZETA_INNOVATION_TRANSFER.md`](ZETA_INNOVATION_TRANSFER.md).

How this file relates to its peers:
- [`LEARNINGS.md`](LEARNINGS.md) is the permanent numbered findings log (what was found).
- [`PROOF_ARCHITECTURES_PLAN.md`](PROOF_ARCHITECTURES_PLAN.md) is the per-architecture plan.
- [`PUBLICATIONS.md`](PUBLICATIONS.md) is the publication ledger.
- **This file** is the resumable operational surface: the top is a reverse-chronological
  stack of dated session blocks, then stable sections (walls, falsifiability triggers,
  recommended deployments, and the Last-verified-state pin). A cold-resuming session
  should read the top N blocks plus the pin, not re-derive the edge.

Maintained by ORCHESTRATOR and SYNTHESIZER. Newest block at the top. Verdict
vocabulary: KILL / MIRROR / PARTIAL / CONFIRMED / CLOSED.

---

## Dated update stack (newest first)

> **Update (2026-08-14): L86 -- the $n=18$ wall is ENCODING-INDEPENDENT, and the
> ladder stops here.** Two structurally different attacks fail on the same sparse
> cells. CEGAR cube-and-conquer closed $m=53$ (5.8 cpu-h, zero timeouts,
> non-vacuity witness) and left cubes unfinished on $m=52$, $m=51$, $m=50$; an
> independent 2-QBF encoding, which reproduces every $n=15$ and $n=16$ cell in
> seconds and is therefore calibrated, returned UNKNOWN on $m=51$ at a 6-hour cap.
> $m=49$ skipped deliberately (hardest cell, verdict determined). So **$n=18$ is 6
> of 9 cells closed and is NOT a theorem**; ~135 cpu-hours bought zero closures on
> the open four. The wall is a fact about the problem at this order, not about our
> method, which is the only version of that claim that justifies stopping.
> **$n\le17$ is unaffected and remains the published claim.** Do not restart $n=18$
> without a new idea rather than a new budget (better symmetry breaking below the
> SMS minimality check, a class lemma that prunes the sparse end specifically, or
> different hardware). The queue is halted with a STOP file saying exactly this.

> **Update (2026-08-13, overnight): L84-L85, and $n=18$ is PARTIAL with a measured
> cost curve.** Three results, and they agree with each other. (1) **L84: all 23
> direction classes of de Grey's graph are ESSENTIAL, none redundant** -- deleting
> any single rotor residue mod $60^\circ$, including the class holding exactly ONE
> edge, collapses the graph to 4-colorable. So that edge lies in every 5-critical
> subgraph, and the construction has no removable part at the granularity of
> direction. L18's "delocalized" is now measured. (2) **L85: iterated assembly on
> the new $\mathbb{Q}(\sqrt3,\sqrt{35})$ core reaches depth 6 with 1,159 BINDING
> EDGES and $\chi=4$ throughout** -- binding is not the scarce ingredient, coupling
> is; local bindings accumulate without producing a global obstruction (the exact
> discrete echo of L74's continuous finding). (3) **$n=18$: cube-and-conquer closed
> $m=53$** (392 cubes, 5.8 cpu-h, 0 timeouts, non-vacuity witness) -- a cell the
> blind split never touched -- then walled: $m=52$ UNDECIDED after 30 cpu-h with 19
> of 551 cubes timed out, $m=51$ UNDECIDED after 61 cpu-h with 73 of 390. So **5 of
> 9 $n=18$ cells are closed** ($m=54..57$ by the E20 ladder, $m=53$ by cubes) and
> $n=18$ is NOT a theorem. Cost climbs 5-10x per edge removed and the timed-out
> FRACTION grows (0% $\to$ 3.5% $\to$ 19%), which is the honest signal that the
> sparse end needs a different idea rather than more hours. $n\le17$ unaffected and
> remains the published claim. Together L83/L84/L85 say the same thing from three
> directions: 5-chromaticity here is a GLOBALLY coupled property, not an
> accumulation of local structure, so neither ball-growing, nor skeleton-copying,
> nor rotation-piling will produce a new $\chi=5$ UDG.

> **Update (2026-08-12, later): L79-L82 -- four follow-ons, two of them negatives
> that redirect effort, plus a NEW OBJECT.** (1) **L82, the one to pull on**: the
> radius-3 ring census found a SECOND binding field. $\mathbb{Q}(\sqrt3,\sqrt{35})$
> (rotor $(1/6,\sqrt{35}/6)$) reaches $\chi=4$ on 48 edges more than the inert
> baseline, and its core is a VERTEX-CRITICAL 4-chromatic UDG on **56 vertices /
> 115 edges** that provably contains neither the Moser spindle nor Golomb (a
> 4-critical graph on 56 vertices cannot contain a 7- or 10-vertex 4-chromatic
> subgraph). A distinct 4-chromatic mechanism outside the lineage's field, which is
> the frontier's "new construction principle" one $\chi$-level below target.
> Artifact `combinatorial/e24_sqrt35_core.json`. Radius-4 test of whether it
> extends to $\chi=5$ is RUNNING, with the Moser field at radius 4 as its
> calibration (de Grey's graph lives in a 4-step ball, so that ball must reach
> $\chi=5$; if it does not, the generating set is too small and needs more rotors).
> (2) **L81: $f(6)\ge15$** -- no $K_4$-free 6-chromatic graph on $\le14$ vertices
> (E23, self-contained, no UDG content; $f(5)=11$ is Jensen-Royle, $f(6)\le47$ from
> the Mycielskian tower). The $n=15$ rung was STOPPED at a projected 100-300 cpu-h.
> (3) **L79, E21**: unit-distance geometry forbids odd cycles and $>6$-vertex
> components inside any neighborhood, which is strictly stronger than the class's
> $K_4$-free + codegree bound and is verified TIGHT on three real embeddings. It
> prunes 64% of the class and is still 2x SLOWER, because E20's cost is decoupled
> from class size. Belongs in `e17_prune.c` (worth ~3x to an enumerator), not in the
> decider. (4) **L80, E22**: the $n\le17$ verdicts CANNOT be LRAT-certified -- $\Phi$
> is satisfiable, so no propositional refutation exists to check. C1's caveat was
> corrected accordingly. (5) **E25**: SMS's native cube-and-conquer wired as the
> fallback for cells the ladder cannot swallow, calibrating now; sampled cubes on the
> stuck $n=18$ $m=53$ cell ran 0.11-41.9 s against a 4 h whole-cell budget that never
> finished. **$n=18$ status, honest**: 4 of 9 cells UNSAT (the dense end, $m=54..57$),
> the 5 sparse cells $m=49..53$ all UNKNOWN and recursively splitting; the earlier
> 40x-per-order projection was too optimistic and there is no defensible ETA.
> $n\le17$ is unaffected and remains the published claim.

> **Update (2026-08-12): L78, E20 -- the $\Sigma_2$ collapse, and $n=17$ is CLOSED.**
> The colorability half no longer needs its own pass. SMS ships a chromatic-number
> propagator (`graphPropagators/coloringCheck.cpp`) the program had never used --
> L77's own build note calls it "an unused coloring propagator" while patching it --
> and folding it into the SAME relaxation-gated cell CNF turns "does the both-free
> class contain a $\chi\ge6$ member on $n$ vertices?" into ONE CDCL run:
> `smsg -v n --min-chromatic-number 6 --dimacs <cell>`, `Result: 20` = the theorem.
> Cost now tracks search difficulty, not class size, and the class is never
> enumerated. **Calibration ALL RUNGS PASS before any trust**: triangle-free
> $\chi\ge4$ UNSAT at $n{=}10$ / SAT at $n{=}11$ with the model **isomorphic to
> Groetzsch** (external uniqueness theorem, both directions); $K_4$-free $\chi\ge5$
> at 10/11 (Jensen-Royle); per-cell non-vacuity; and the repo's own $n=15$/$n=16$
> verdicts reproduced by a third route. **Measured: $n=15$ 3.6 s (vs 420 s for the
> geng gate re-measured here today), $n=16$ 74.3 s (vs 66.3 cpu-h, ~3200x), $n=17$
> 0.83 cpu-h / 1202 s wall (vs the $>80$ cpu-days L75 measured).** VERDICT:
> **the both-free class has NO $\chi\ge6$ member on 17 vertices** -- all seven cells
> $m=46..52$ UNSAT, zero hits, zero unknowns; the dominant $m=46$ cell (E19 measured
> it at $>1.15$M classes and had to be written as a 64-way branch driver) falls in
> 736 s without emitting a graph. So **any both-free host, hence any host for a
> $\chi\ge6$ UDG clamp, has $n \ge 18$**. Bounds the CLASS, not $\chi(\mathbb{R}^2)$;
> W3 and the L63 codegree wall are untouched, and L75 caveat (ii) (Lean) is untouched.
> Now running as the always-on job: `--climb 18`, a resumable ladder over
> $n=18,19,20,\dots$ that auto-splits a timed-out cell into 32 cached branches and
> stops loudly on the first hit or first genuine wall. Artifacts:
> `combinatorial/e20_sigma2.py`, `combinatorial/e20_results.md`, `_cache/e20/`.
> `smsg` now builds on the Linux host too (Boost 1.83 user-local, no root).

> **Update (2026-08-09, late): L77 -- SAT modulo symmetries closes the E18 census.**
> Kirchweger-Szeider `smsg` built on this host (msys/ucrt64; `cadical_sms` static
> lib; minor portability patches), driven by `e18_sms_cell.py` over the SAME
> relaxation-gated cell CNF with NO lex-leader clauses (SMS owns canonicity,
> inside the solver). Calibration 8/8 exact before trust: $n=15$ cells 9/2/0 with
> 11/11 graph-for-graph vs the committed artifact; $n=16$ $m=44..48$ =
> 645/75/10/1/1, all EXHAUSTED, seconds each, models-per-class 1.0 throughout.
> **The parked $m=43$ cell: EXHAUSTED in 45.4 s** (10,583 solutions, one per
> class, 0 violations) -- the cell the blocking approach could not close at any
> split. Merge: **CENSUS COMPLETE**; compare: **11,315 vs 11,315, matched
> 11,315, only-in-geng 0, only-in-SAT 0, AGREE**. So **L75 caveat (i) is FULLY
> closed at $n=16$** (two independent enumerators, different technology,
> identical answer). The leftover blocking-clause branches grinding on this host
> were retired once the census closed. SMS is now the validated SAT-side
> enumerator for any $n=17$ attempt; the $n=17$ walls that remain are class size
> (~100x, L75) and the $\Sigma_2$ colorability half -- not enumeration tooling.
> Gold runs ($n=13,14$ break-free): relaunched with ~7 GB free; outcome recorded
> below when they land. Artifacts: `combinatorial/e18_sms_cell.py`,
> `combinatorial/_cache/e18/sms_*`, the L77 LEARNINGS entry, the
> `e18_results.md` addendum.

> **Update (2026-08-09): L76, E18 -- a second enumerator, and the Gallai prune killed.**
> Overnight run on a SECOND host (Windows laptop, 32 cores, msys/ucrt64 gcc; not the
> Linux box of L75), which began with no venv, no packages, no nauty. Three results.
> (1) **E17 replicates on an independent host/toolchain/OS**: all gates exact
> (352/2001/15481; $n=13,14$ empty; $n=15\to11$; $m=48\to$ Shrikhande), $n=16$ returns
> **exactly 11,315**, and coloring them reproduces the verdict to the residue
> (11,291 DSATUR / **24** SAT / 0 hits) with those 24 **isomorphic to the committed
> `e17_n16_sat_residues.json`, 24/24**. (2) **L75 caveat (i) is half-closed**: a
> SAT-side enumerator (CDCL + blocking clauses, not canonical augmentation)
> EXHAUSTED the $n=15$ cell and matched geng graph-for-graph (1,989 models $\to$ 11
> classes), and at $n=16$ FOUND all 11,315 classes with **only-in-SAT 0 and 0 property
> violations** (proved-exhausted coverage 11,312/11,315: five of six cells complete,
> only $m{=}43$ outstanding, PARKED after a measured wall: blocking-clause enumeration dies at ~$10^5$ clauses per solver at BOTH 8-way and 64-way splits, so the fix is SAT modulo symmetries, not more compute). Cost model: the binding quantity is models-per-class,
> ~250-370 unsplit but **~14 when a cell is split on the HIGHEST-indexed vertex pairs**
> (splitting on the lowest is useless -- lex-leader already pins them). (3) **NEGATIVE,
> calibrated 5/5: the Gallai low-vertex structure L75 named as the way past $n=17$ is
> ~2 orders of magnitude too weak** -- still SAT at $n=15..18$, and as a filter it
> prunes only 18% of the $n=15$ cell against the ~99% needed; it also cannot go inside
> geng (degrees only grow during augmentation, so "low" is only decidable at
> $n=\text{maxn}$, i.e. a post-filter over cheap coloring calls, not over generation).
> Reading: the $n=17$ wall is the $\Sigma_2$ colorability half, not missing local
> structure. NEW FACT along the way: the both-free class with $\delta\ge5$ is empty
> through $n=11$ and **first nonempty at $n=12$** (E17 never asked; its small-$n$
> emptiness is about 6-critical candidates via KY, not about the class).
> **No bound moved**; W3/realizability untouched; caveat (ii) untouched. Incomplete:
> the two `gold_*` no-symmetry-breaking re-derivations of $n=13,14$ (one retired at
> 2.15 GB when host free memory hit 1.9 GB) and the outstanding branches -- both cheap
> to finish on an idle machine. Artifacts: `combinatorial/e18_*.{py,md,json}`,
> `e17_build_geng_msys.sh`, `orchestrator_sessions/NIGHT_PLAN_2026-08-08.md`.

> **Update (2026-07-23): L75, E17 exhaustive nauty enumeration of the both-free class.**
> nauty 2.8.9 now BUILDS on this host (Linux/gcc), so the L69 "blocked on nauty" door is
> open and E17 walked through it: a custom-pruned geng (`geng_hn`, PRUNE/PREPRUNE plugin
> `combinatorial/e17_prune.c`: incremental $K_4$/$K_{2,3}$ rejection + cherry budget) plus
> two new sound caps proved for the class (maxdeg $\le(n-1)/2$; 2-connectivity via
> 6-criticality) enumerates ALL candidate $\chi\ge6$ members of the UDG-necessary class
> per $n$. Calibrated five-for-five: independent-filter agreement 352/2001/15481 at
> $n=7/8/9$ (identical canonical sets at $n=9$); the $n=16$, $m=48$ extremal cell emits
> exactly the Shrikhande srg(16,6,2,2), $\chi=4$, rejected; Folkman floor reproduced
> ($n=13,14$ empty, $n=15$: 11 graphs, all 5-colorable); smoke 9/9; hit path
> pre-validated on $M^3(C_5)$. **VERDICT: the both-free class contains NO $\chi\ge6$
> member on $n\le16$, EXHAUSTIVELY** ($n=16$ window 43..48: 11,315 both-free graphs,
> every one 5-colorable, 66.3 cpu-h / 4.4 h wall, 0 hits); the smallest, if any, has
> $n\ge17$. Upgrades the L65/L67/L69 heuristic negatives to a theorem-grade statement
> for $n\le16$ and confirms L69 from the inside ($K_{2,3}$ violations load-bearing).
> Measured wall: $n=17$ $>80$ cpu-days on this host (no mod=4096 sample part finished
> in 1,700 cpu-s); needs ~100x compute or a 6-critical/Gallai-structure prune inside
> the generator. Bounds the CLASS, not $\chi(\mathbb{R}^2)$; W3/realizability unchanged.
> VERIFIER + ADVERSARY passes are now COMPLETE, both GREEN: `combinatorial/e17_verification.md`
> (VERIFIED, 4/5 targets VERIFIED + 1 VERIFIED-WITH-CAVEAT, zero blocking findings) and
> `combinatorial/e17_adversary.md` (PASS, five attack surfaces SOUND, closed the
> residue-persistence caveat by re-deriving all 24 SAT residues, 0 disagreements). The 24
> residues are now tracked in `combinatorial/e17_n16_sat_residues.json`; the driver was
> patched to persist `sat_residue_g6` going forward. Two caveats carry into any fold: (i)
> enumeration completeness at $n=15,16$ rests on geng + the verified prune lemmas, no
> independent second enumerator; (ii) the two counting lemmas are formalization-ready but
> not yet Lean-proved. PUBLICATIONS: registered as C7, FOLD into C1, fold gate now
> SATISFIED; Owen decision still open (amend C1 before upload vs ship as-is + follow-up).

> **Update (2026-07-18): L74, the gradient thread SCALED TO GPU (RTX 5090).** New
> [`gradient/gpu/`](gradient/gpu/) module: a batched, device-parameterized `(B,n,2)`
> core (float32 GPU search into float64 CPU refine, the SAT firewall intact), validated
> against the same `diff_udg` calibration answers. Env facts settled: the 5090 (sm_120)
> needs `torch==2.11.0+cu128` (no 2.12 cu128 build); `python-sat` was silently missing
> (so `sat_chi` returned `None`), now installed and the core smoke gate passes 9/9. Four
> firewalled campaigns map the continuous surface exhaustively. **alpha** (realizer sweep,
> 16k starts/host): every E13/E13b host AND the $n{=}29$ $\chi{=}5$ in-class graph refuse
> to realize as legal UDGs (over-determined $+43$ to $+51$), a GPU-scale corroboration of
> the L63 rigidity wall. **beta** ($\sim$221k adversarial runs): densest 96 survivors all
> $\chi=3$, never even $\chi=4$ (GD builds lattice, not hardness). **gamma** (seeded from
> Moser/P510): the $\chi=3$ monolith is a REACHABILITY wall, not representational -- GD
> HOLDS a seeded $\chi=4$ ($2048/2048$ preserved) but GROWING it dilutes back to $\chi=3$.
> **delta** (the L74 lever, fixed rigid core + candidate-edge growth = de Grey's principle
> continuous): dilution SOLVED ($4096/4096$ core-hold at every size, $+19$ hardening edges
> onto the Moser core) yet $\chi$ stays $4$ -- the true ceiling is that the smallest known
> $\chi=5$ UDG is $\sim$500 vertices, out of reach of undirected growth. Net: the
> continuous surface can represent / preserve / grow-onto a hard core but cannot
> manufacture $\chi\ge5$; the path there stays SAT-based construction. No bound moved.

> **Update (2026-06-30): L73, the gradient-descent attack surface.** New
> [`gradient/`](gradient/) thread maps where continuous optimization can bite on
> $\chi(\mathbb{R}^2)$. Governing constraint stated: GD is local + one-sided, so it
> builds / finds upper bounds but never a $\chi\ge6$ lower bound (needs a SAT/dual
> certificate); a pure soft-coloring objective lifts to $\mathbb{Q}^2$ ($\chi=2$) and
> is excluded by design. Built + calibrated: shared torch core (`diff_udg.py`),
> (B) the legal-UDG realizer (`realize.py`, adds the non-edge margin the legacy
> realizer omits; Moser + triangular patch return LEGAL UDGs, $K_4$ fails),
> (D) the flexible-but-color-rigid gadget kill-test (`gadget_search.py`; flexible
> clamps exist at $k=2$, vanish below $k=5$, the kill-test cell stays empty),
> (A) the adversarial coordinate$\leftrightarrow$coloring co-optimization
> (`adversarial.py`; inner colorability oracle validated exactly on triangle/$K_5$;
> honest negative: naive GDA from a random seed builds a 46-edge near-unit graph but
> only $\chi=3$). (C) first-order spectral push spec'd against `fractional/`, not
> duplicated. No bound moved; runnable, firewalled infrastructure. Next: point B at
> the L63 host candidates, seed A from P510, build C in `fractional/`.

> **Update (2026-06-30): meta-infrastructure transfer from the zeta repo.**
> Audited the zeta-function repo for transferable methodology and adopted the real
> gaps (report: [`ZETA_INNOVATION_TRANSFER.md`](ZETA_INNOVATION_TRANSFER.md)).
> Shipped: (1) `_shared/smoke_test.py` now actually COLORS the controls and gates
> on them (Moser=4, Q^2=2, L^inf=4, R^1=2, unit triangle=3), plus a `--full`
> chi>=5 calibration (Heule-826 UNSAT at k=4 in ~6s via symbreak portfolio).
> (2) `lemma_db/` built: a 27-node proof-dependency DAG with a control-object
> firewall (CONFIRMED live: self-test fires on a planted Q^2/L^inf load-bearing
> edge and rolls back clean). (3) This file, `STATE_OF_THE_PROGRAM.md`,
> `FREEZE_LIST.md`, `LOAD_BEARING_FACTS.md`, `TOKEN_EFFICIENCY.md`, a NIGHT_PLAN
> template, the PUBLICATIONS K1 circularity gate, and attack-prompt twins.
> (4) `toy/` sandbox (the zeta toy analog, flagged after the first pass): a battery
> of known-chi finite graphs (SAT answer key) that GRADES a proposed chi-lower-bound
> technique on reproduce-target / reject-fakes / control-immune / k1-clean. Reference
> (exact-chi-by-SAT) all green; the clique and degree+1 demo candidates are caught;
> the controls are the firewall. Honest caveat: grades the technique, not the W3
> realizability lift. Consequence: the program is now resumable from one surface,
> structurally self-auditing, and technique-grading. No mathematical state changed.

> **Update (2026-06-15): L69-L72, the order-2 measurable verdict.** CLOSED the
> order-2 measurable route: at Ambrus's X_23, matrix-free order-2 (IEC up to
> subset size 4) is FEASIBLE, so it does not certify chi_m>=5 and by monotonicity
> cannot reach chi_m>=6 (L72, C4). Built and validated the matrix-free order-2
> SDP solver first (L70-L71, e3u). E16 top-down repair of M^3(C5) stalls; K_{2,3}
> violations are load-bearing for chi=6 (L69). Geombinatorics structural note
> drafted (no new bound).

> **Update (2026-06-11): L63, the codegree wall.** The nauty-free host factory
> works (n=18 K4-free 6-critical graphs, alternators abundant), but UDG-realizability
> forces K_{2,3}-freeness, which excludes every manufactured host (L63, into C1).
> PARTIAL: hosts exist abstractly, none survive the codegree ceiling. Next: generate
> inside the both-free class from P510 (E14).

> **Update (2026-06-09): L57-L62, forcing-sterility + the phase-gadget route.**
> Exhaustive forcing census: all ~2.29M non-adjacent pairs across the 12 known
> chi-5 UDGs are FREE (L57, the Essential-Pair Lemma explains it: the lineage is
> vertex-critical, so forcing-sterile by construction). Phase-gadget dichotomy and
> the alternator analysis bypass W3 framing (L58-L62). This became C1.

> **Update (2026-06-02): L51-L56, the clamp and backward-from-2050.** The abstract
> flexible color-clamp EXISTS (48-vtx triangle-free SAT witness); W3 reduces to
> cocircularity with distinct centers (Theorem R, L51-L53). Backward-from-2050:
> most likely terminal answer chi=6 by a finite UDG; the linchpin is the W3
> realizable clamp; the RG diagnostic is imprimitivity, not leading eigenvalue;
> forced-same sweep NEGATIVE across the lineage (L54-L56).

---

## Current wall, per architecture

| Arch | Approach | Current wall | Status |
|------|----------|--------------|--------|
| 1 UDG | finite chi>=6 UDG via the realizable clamp | W3 = unit-distance realizability of the clamp; the host must be K4-free 6-critical AND K_{2,3}-free AND outside the P510 lineage. In-class nonexistence is now CLOSED for n<=17 (L78, the Sigma_2 collapse: no chi>=6 member exists, so any host has n>=18), on top of the n<=16 enumeration (L75) and its independent second-enumerator census (L77: 11,315/11,315 AGREE). The enumeration wall L75 measured at n=17 (>80 cpu-days) is GONE, not scaled: E20 answers the question without enumerating. The W3 wall itself is unchanged | OPEN, the live route (route ii: wide imprimitive interface) |
| 2 measurable | chi_m>=6 via SDP | order-2 at X_23 is FEASIBLE; route CLOSED. Higher order or noncommutative SE(2) is the only remaining measurable lever | CLOSED (order-2); SE(2) open |
| 3 fractional/spectral | chi_f, Lovász theta | plateau at the classical line at runnable scale | OPEN, no live increment |
| 4 axiomatic | Borel chromatic chi_B | needs a local finite-UDG statement that pushes chi_B>=6 via the rotation group (not norm-blind Steinhaus) | OPEN, dark horse |

## Falsifiability triggers

- order-2 measurable certifies chi_m>=5 at X_23 -> **TRIGGERED-CLOSED (L72): it is FEASIBLE, route closed.**
- a forced non-adjacent pair found anywhere in the known lineage -> NOT-TRIGGERED (L57: exhaustively free).
- a manufactured K4-free 6-critical host that is also K_{2,3}-free -> NOT-TRIGGERED, and now EXHAUSTIVE for n<=17 (L63: codegree wall; L75: no such host on n<=16; L78: none on n=17 either, so any future trigger lives at n>=18). The E20 ladder is climbing n and will move this line as it goes.
- the firewall (`lemma_db`) reports a violation -> NOT-TRIGGERED (audit clean as of 2026-06-30).

## Recommended next deployments

1. **The one most-leveraged move:** a NEW chi-5 UDG outside the P510 lineage carrying
   a wide imprimitive interface (route ii of L55). Feed candidates to the existing
   forced-pair SAT test. See `lemma_db --frontier`: `new_chi5_outside_lineage`.
2. The descriptive-set-theory dark horse: a local finite-UDG criterion for chi_B>=6.
3. Measurable: the noncommutative SE(2) spectral bound, if a smallest computable
   instance can be pinned (the abelian shadow is exhausted).

(L75/E17 does not reorder this list: closing the small-n in-class enumeration door
reinforces move 1's premise that the missing object needs a NEW construction
principle, not more search at small n.)

---

## Last verified state

- **2026-08-09 late (L77):** the SMS closure artifacts (`combinatorial/e18_sms_cell.py`,
  `_cache/e18/sms_*`, the closed `enum_n16_m43.json`, the L77 LEARNINGS entry, the
  `e18_results.md` addendum, this block) are UNCOMMITTED pending Owen's authorization.
  The E17/E18 artifact sets of the earlier blocks ARE committed and pushed
  (`8e21aa5..d2e45ee`; the previous "UNCOMMITTED" note here was stale the moment those
  commits landed). The $n=16$ census is COMPLETE and AGREE (11,315/11,315); no
  outstanding $m=43$ compute exists. Remaining compute: the two `gold_*` break-free
  runs ($n=13,14$), relaunched this session. `smsg` lives at
  `~/.local/src/sat-modulo-symmetries/build/src/smsg.exe` (needs
  `C:\Tools\msys\ucrt64\bin` on PATH; rebuild = cmake+ninja per L77).
- **Latest finding:** L77 (SMS closes the E18 census; caveat (i) of L75 fully closed
  at $n=16$). L72 remains the latest measurable verdict.
- **Host:** this session ran on the Linux/gcc box (venv `.venv`, `geng_hn` in
  `~/.local/bin`); earlier "no compiler / nauty absent" host notes are superseded on
  this machine.
- **Lean:** sorry-free (incremental build with cached Mathlib oleans).
- **Canonical SAT witness state:** the whole chi>=5 lineage is self-certifiable on
  one workstation via the symmetry-broken portfolio (M^4(C5) k=6, P510 k=4, de Grey
  1585 k=4 all UNSAT, optional DRAT). L68 / C3.
- **Gates green:** `python -m experiments._shared.smoke_test` (core) and
  `python -m experiments.lemma_db.build_db` (firewall, 0 violations) both pass.
  `smoke_test --full` confirms Heule-826 UNSAT at k=4 (~6s).
- **Papers:** C1 (forcing-sterility + codegree) SHIP/P1, arXiv bundle built. C3
  (symmetry-broken solver) DEVELOP->SHIP-ready/P2, arXiv bundle built. Both pending
  Owen's upload action. NEW Owen decision flagged (PUBLICATIONS 2026-07-23): amend
  C1 with L75's exhaustive strengthening before upload, or ship as-is and fold L75
  into a follow-up.
