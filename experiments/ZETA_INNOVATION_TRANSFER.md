# Innovations transferable from the zeta repo to Hadwiger-Nelson

Provenance: generated 2026-06-30 by a multi-agent audit of `C:\Users\Owen\dev\zeta function`
(six parallel extractors over its agent infra, attack prompts, token/ops docs, publication
discipline, research methodology, and program-state tracking; one synthesis pass that diffed
each extracted innovation against the actual HN repo state). 56 raw innovations deduplicated
into 15 actionable items, ranked by expected research leverage for finding a chi>=6 planar UDG
or advancing any of the four architectures.

This report deduplicates the extracted zeta innovations into actionable items, classifies each
against the actual HN repo state, and ranks by expected research leverage. Inspected on the HN
side: `.claude/agents/*`, `.claude/workflows/hn-lens-attack.js`, `CLAUDE.md`,
`experiments/{LEARNINGS,PROOF_ARCHITECTURES_PLAN,PUBLICATIONS,SOLVING_PROGRAM}.md`,
`experiments/_shared/*`, `experiments/orchestrator_sessions/`, `docs/research_atlas/`,
`docs/researcher_mindset.md`, and the memory index.

Headline: HN has already internalized the entire multi-agent and attack-prompt cluster, and most
of the publication-discipline cluster. The real transfer value is concentrated in a few
state-tracking and verification-infra items that HN genuinely lacks.

## What HN already has (do not re-create)

The single largest cluster of zeta innovations (six roles, the wrong-approach-detector-as-first-filter,
parallel BUILDER angle-diversity, four-layer verification, structured output contracts, SYNTHESIZER
as single writer, the marginal-suspicion prior, human escalation, generation-vs-judgment model-tiering,
and the four-architecture portfolio with kill criteria) is fully HN-native. Evidence:
`.claude/agents/adversary.md` runs the three controls as step 1 and enforces "can only falsify, not
confirm"; `orchestrator.md` carries per-phase fan-out counts, premature-pivot / sunk-cost anti-patterns,
falsifiability triggers, escalation to Owen, and an end-of-session handoff checklist; `hn-lens-attack.js`
model-tiers (Sonnet for adversary/synthesis, big model for generation) and documents cost levers. HN
even improved on zeta in two places: it uses three control objects instead of one, and it records a
per-architecture exemption (Architecture 2 may legitimately fail on Q^2 since the rationals are measure
zero). These need no new files.

## Category: verification and detector infrastructure (highest leverage)

### Wire the detectors into a CI smoke test that actually colors the controls
What it is: zeta runs the Davenport-Heilbronn control as an actual CI verdict via `smoke_test.py`.
Why it works: it converts "remember to check" into "the harness fails if a method is blind." HN status:
PARTIAL. `experiments/_shared/wrong_approach_detectors.py` defines the three controls and a
`run_detector()` harness, and `unit_distance_graph.py` has `chromatic_number_sat()`, but
`experiments/_shared/smoke_test.py` only constructs graphs and asserts vertex and edge counts. It never
colors anything, so the detector is library code, not an enforced gate. Adoption step: extend
`smoke_test.py` to assert chi=2 on the Q^2 and R^1 controls, chi=4 on the L^inf grid and Moser, and
UNSAT-at-4 on a small de Grey fragment, with a non-zero exit. This would have caught the S199/L403/T721
chi=4 erratum.

### Calibration against a known value before trusting any new solver or encoding
What it is: zeta caught a sign error (M(zeta) ~ -123 vs +0.08) by calibrating against a prior result
before committing. Why it works: a new computation that disagrees with an established calibration point
is presumed buggy, not novel, and the check runs before the expensive commit. HN status: PARTIAL. HN has
several solver paths (`portfolio_sat.py`, `hn_solver_cdcl.py`, `hn_solver_wl.py`, PyPy bench) and a
PUBLICATIONS V-axis that rewards two-solver cross-validation, but no standing baseline suite every new
computation must reproduce. Adoption step: fold a baseline suite (Moser=4, Q^2 fragment=2, L^inf=4,
de Grey HN-4 UNSAT-at-4) into the same gate as the detector smoke test, and state in `CLAUDE.md` that a
new solver is not trusted until it reproduces all four.

## Category: state tracking (high to medium leverage)

### lemma_db: a queryable proof-dependency DAG with a control-object firewall
What it is: a DuckDB graph of the whole proof skeleton (typed nodes, load-bearing vs annotation edges, a
`frontier` view, and a `dh_audit` that gates CI if a wrong-approach node sits on a load-bearing path to
the target). Why it works: it makes three otherwise-manual things automatic, namely "what can I work on
now," "is the effort still non-circular," and "where is the believed-but-unproven gap." HN status:
MISSING, and this is the single biggest absent innovation. HN has a Lean skeleton (`DeGreyLowerBound.lean`,
the L24 triple-coupling lift) and a flat LEARNINGS, but no machine-queryable dependency graph. Adoption
step: create `experiments/lemma_db/` modeling the path to the one blocker (a chi-6 UDG embeddable in the
plane), with a `control_buildable` flag {Q^2, L^inf, R^1} and a `control_audit` that exits non-zero if a
node satisfiable on Q^2 (chi=2) or L^inf (chi=4) is load-bearing for a chi>=5 claim. Wire it into the
same CI entry point as the smoke test. This is the structural-firewall analog of the zeta D-H firewall,
specialized to HN's already-defined controls.

### PHASE_STATE.md: one operational state file with a Last-verified-state pin
What it is: a reverse-chronological dated-update stack plus stable sections (current wall per
architecture, falsifiability triggers, recommended next deployments, and a "Last verified state" block
pinning commit + finding number + Lean status). Why it works: it makes each session a pure function of
prior state, so a cold-resuming agent reads the top N blocks instead of re-deriving the edge, and the
commit pin keeps the narrative from drifting from git. HN status: MISSING. HN's operational state is
scattered across about seven dated memory files plus `orchestrator_sessions/*.md`; `orchestrator.md`
mandates a handoff but names no canonical file. Adoption step: create `experiments/PHASE_STATE.md` with
the dated-update stack (verdict vocabulary KILL / MIRROR / PARTIAL / CONFIRMED / CLOSED), a
falsifiability-trigger list (e.g. order-2 measurable = TRIGGERED-CLOSED per L72), and a "Last verified
state" pin (current commit, L72, sorry-free, P510 k=4 cracked via symbreak L68). Point the orchestrator
and synthesizer specs at it.

### STATE_OF_THE_PROGRAM.md: one-page strategic snapshot
What it is: a short, rewritten-not-appended strategic map (thesis paragraph, four-row wall table, honest
odds, one named next move) that the operational log points to. Why it works: it splits documents by
altitude so a re-orienting reader gets the whole-program posture in one read. HN status: MISSING. HN has
`PROOF_ARCHITECTURES_PLAN.md` (a plan, not a snapshot) and a README overview, but no terse one-page map
naming a single priority. Adoption step: write it with the thesis ("the program bottoms out at one
missing object: a chi-6 UDG embeddable in the plane / the W3-realizable clamp"), a four-row table with a
"the wall" column built from the three controls, and the single most-leveraged move (a NEW chi-5 UDG
outside the lineage carrying a wide imprimitive interface, route (ii) of L55).

## Category: creative-attack and prompt engineering (medium to low; mostly already absorbed)

### Standing freeze-list + load-bearing-facts blocks
What it is: a typed list of dead proposal shapes (with the result that killed each and a two-clause
escape) plus a curated do-not-re-derive settled-facts block. Why it works: it converts vague novelty
pressure into a membership test, and stops a fresh agent re-walking known-dead paths. HN status: PARTIAL.
The raw material is excellent but lives only inside the `hn-lens-attack.js` DEFAULT_BRIEF (its KNOWN KILLS
and CURRENT FRONTIER), not as standalone citable files. Adoption step: promote them to
`experiments/FREEZE_LIST.md` and `experiments/LOAD_BEARING_FACTS.md`, keeping the workflow brief pointing
at them so they stay single-source.

### No-repo and chat-paste twins of the attack prompt
What it is: in-repo, no-repo, and paste-ready chat variants of one prompt, the last inlining a
control-object reconstruction so a sandboxed foreign model can run the falsification itself. HN status:
PARTIAL. The DEFAULT_BRIEF is effectively the in-repo twin with controls and kills inlined, but there is
no no-repo or chat twin with an inlined exact-arithmetic UDG plus colorability check. Adoption step:
derive the two twins; low priority because the in-repo path covers the common case.

### Localize-to-one-object framing, the one-line ship test, single-lane discipline, kill criteria
These attack-prompt items are already present in HN under different names: the one-object localization is
the documented frontier ("all difficulty = W3 realizability"); the bridge-vs-mirror and
name-the-irreducible-step tests live in `docs/researcher_mindset.md`; the kill criteria map onto the
three controls plus the L72 level argument. No new adoption needed beyond keeping `researcher_mindset.md`
load-bearing rather than decorative. Flagged as effectively-already-held.

## Category: token economy and overnight operations (medium to low)

### Token-efficiency playbook + pre-fan-out checklist
What it is: a consolidated cost playbook (batch-N-into-one-array, model-tier judgment to Sonnet/Haiku,
inline data and forbid reads, state a budget, order flaky work last, salvage from disk) plus a 7-item
pre-fan-out checklist. HN status: MISSING as a document, though `hn-lens-attack.js` already practices
model-tiering and `CLAUDE.md` mandates the `_cache` witness store. Adoption step: add
`experiments/TOKEN_EFFICIENCY.md` with the checklist adapted to HN (one batched ADVERSARY over a gadget
family, order the hard k=6 SAT / order-2 SDP last, pipeline the solver portfolio rather than barrier it,
salvage solved instances from `_cache`). Reference it from `orchestrator.md`.

### Gate-driven overnight contract (NIGHT_PLAN)
What it is: a numbered gated task queue where each task names a validation gate, commits only if the gate
passes, quarantines failures to a findings file, and bounds attempts; deferred items are risk-tiered. Why
it works: the gate is the trust boundary, so unvalidated math never lands as correct, and risk-tiering
keeps tooling-risky work (Lean elan/lake, nauty which cannot install on this host) off the unsupervised
path. HN status: PARTIAL. HN has `orchestrator_sessions/` and falsifiability triggers but no standing
gate-as-trust-boundary contract. Adoption step: add a NIGHT_PLAN template with HN gates
("chromatic_number_sat returns UNSAT with a checkable DRAT core," "graph re-embeds with exact arithmetic
< 1e-12," "Q^2 control still returns chi=2"), commit-only-on-pass, and a `_NIGHT_FINDINGS.md` quarantine.

## Category: publication discipline (medium to low; largely adopted)

### Add the circularity (K1) gate question to the rubric
What it is: a two-directional implication test (does X imply the conjecture AND does the conjecture imply
X) that flags reformulations dressed as progress. HN status: PARTIAL. `PUBLICATIONS.md` has a V/N/S
rubric and a pre-SHIP checklist (detector, ADVERSARY, number re-check) but no circularity test, so an
Architecture-4 Borel/Shelah-Soifer relabeling or an Architecture-2 chi_m-SDP restatement could pass
everything while being a relabeling. Adoption step: add gate question 4b, applied especially to Arch 4
and Arch 2 candidates; pairs with the existing bridge-vs-mirror test.

### Parked/pre-empted section + lit-check-before-drafting + bundle field
HN status: PARTIAL, mostly adopted. `PUBLICATIONS.md` already separates discovery from paper, uses C# ids,
bundles C2 into C3, and keeps an append-only decision log. Missing: a standing Parked/pre-empted section
seeded from the atlas failures, and an explicit "lit-check before any prose" rule. Adoption step: add
both; cheap, prevents writing up a known spindle variant.

### Obstruction-map survey as a paper
What it is: a publishable survey whose content is the map of where everything is stuck (a scorecard plus a
four-property irreducibility bracket), claiming no new theorem. HN status: PARTIAL. `docs/research_atlas/`
is the raw material and C1 is a partial obstruction note, but there is no single survey operationalizing
"all four architectures bottom out at one object." Adoption step: draft it from the atlas with a scorecard
(produces-finite-witness / respects-Q^2 / respects-L^inf / reaches chi>=6) and a four-property gadget
conjunction (K4-free + 6-critical + UDG-realizable-in-plane + not-K_{2,3}-excluded), each droppable by a
distinct host-factory result (L63/L69). A genuine secondary product beyond C1/C3.

### Bridge-finder oracle over a chromatic/embedding corpus
The generative half of lemma_db (feature-match proven theorems against the missing object, with a single
hard discriminating gate). HN status: MISSING. Defer until the static lemma_db exists; the discriminating
gate is "uses Euclidean-specific rigidity that fails for L^inf" vs "abstract-normed-plane only"
(auto-demote the latter, since L^inf has chi=4).

## Innovations that do NOT transfer or are zeta-math-specific

None of the extracted items are purely zeta-math-specific in a way that blocks transfer: every one had a
clean HN analog because the architecture/control-object structure was deliberately cloned. The closest to
non-transferable is the marginal-positivity / zero-buffer prior, which in zeta is anchored to a measured
quantity (a six-direction zero margin). HN has no such measured margin, so it transfers only as the weaker
qualitative rule "comfort equals suspicion, attack the cleanest construction first" (already implicit in
the ADVERSARY spec). Treat it as adopted-in-spirit, not as a new artifact.

## Prioritized adoption shortlist

1. Extend `smoke_test.py` to actually color the controls and a calibration baseline (low effort, high
   leverage, catches solver/encoding bugs and erratum-class errors). Fold in the calibration suite.
2. Build `experiments/lemma_db/` with a control-object firewall and CI audit (high effort, high leverage;
   the biggest missing structural-honesty tool and the natural home for the one-object program).
3. Create `experiments/PHASE_STATE.md` with a Last-verified-state pin (medium effort, high leverage;
   collapses seven scattered memory files into one resumable surface).
4. Create `STATE_OF_THE_PROGRAM.md` (medium effort, medium leverage; one-page strategic map with a single
   named next move).
5. Add the circularity (K1) gate question to `PUBLICATIONS.md` (low effort, medium leverage; the one
   publication filter HN's rubric structurally lacks).
6. Promote the freeze-list and load-bearing-facts blocks out of the workflow brief into standing files
   (low effort, medium leverage).
7. Add `TOKEN_EFFICIENCY.md` + the NIGHT_PLAN gate contract (medium effort, medium leverage for overnight
   autonomy safety).
8. Lower priority: the prompt twins, the obstruction-map survey paper, the bridge-finder oracle, and the
   README Status changelog (the last is mostly cosmetic parity, not research leverage).

## Addendum: the toy sandbox (missed in the first pass)

The initial six-cluster audit did not scan `experiments/toy/`, so it missed one of the zeta repo's
strongest innovations. The zeta toy is a checkable training ground: function fields are a world where RH
is a theorem with the same proof skeleton, so a proposed proof-move is graded right or wrong
(reproduce-Weil / reject-fakes / k1-clean / DH-immune), manufacturing the value-signal that is provably
absent on the real problem.

HN status: MISSING, now BUILT (`experiments/toy/`). A battery of finite graphs with KNOWN chi (SAT is the
answer key) grades a proposed chi-lower-bound TECHNIQUE on four flags: reproduces-target / rejects-fakes /
control-immune / k1-clean. The reference (exact-chi-by-SAT) scores all green; demo candidates
`clique_lower_bound` (omega, fails reproduces-target on triangle-free M^3(C5)) and `max_degree_plus_one`
(fails control-immune on the L^infty grid) show the grader has teeth. The three controls are the firewall,
the exact analog of the zeta toy's Davenport-Heilbronn firewall.

Key difference, honestly noted: in HN the abstract chi is SAT-decidable, so Architecture 1 already has a
cheap gradient and the toy's value concentrates on Architecture 2/3/4 heuristic techniques (spectral,
topological, measure). The shared caveat is identical: the toy grades the technique on finite graphs, it
cannot contain the W3 realizability obstruction. The delta between a green scorecard and an actual planar
UDG is the compass.
