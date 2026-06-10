export const meta = {
  name: 'hn-lens-attack',
  description: 'Token-optimized creative lens attack on Hadwiger-Nelson: big model generates, sonnet prunes and synthesizes',
  whenToUse: 'Run a creative first-principles round against the current frontier. Pass args {brief, lenses} to override the defaults; otherwise edit DEFAULT_BRIEF below to match the latest LEARNINGS entries.',
  phases: [
    { title: 'Generate', detail: 'first-principles lenses, novel falsifiable conjectures required' },
    { title: 'Adversary', detail: 'detector + known-kills stress test per proposal', model: 'sonnet' },
    { title: 'Synthesize', detail: 'rank survivors into a battle plan', model: 'sonnet' },
  ],
}

// Cost levers vs the 2026-06-09 run (which spent ~2.3M output tokens):
// 1. Adversary + synthesizer run on sonnet (checklist work; the creative product is the generators).
// 2. Synthesizer receives a TRIMMED projection of the material, not the full gen+adv JSON.
// 3. All prompts carry an explicit brevity instruction (thinking is the bulk of output spend).
// 4. Never pause mid-phase: in-flight agents are not checkpointed and re-run from zero on resume.

const DEFAULT_BRIEF = `
PROBLEM. Hadwiger-Nelson: chromatic number chi(R^2) of the unit-distance graph on the plane. Known: 5 <= chi <= 7 (de Grey 2018 lower via 1581-vtx UDG; Isbell hex upper). This repo (c:/Users/Owen/dev/hadwiger-nelson) is a research program; experiments/LEARNINGS.md is the ledger (update this brief from its top entries before each round).

CURRENT FRONTIER (build on this, do not re-derive it):
1. THE ONE MISSING OBJECT: a unit-distance-REALIZABLE "flexible color-clamp": a chi=5 UDG containing a NON-ADJACENT pair (s,t) forced to different colors in EVERY proper 5-coloring. Contracting s=t then gives chi>=6. The ABSTRACT object is a one-move construction (split a vertex w of any K4-free 6-critical graph H into non-adjacent s~A, t~B; SAT-verified 48-vtx triangle-free witness). ALL difficulty = W3 = unit-distance realizability in R^2.
2. Theorem R (exact iff): the clamp realizes IFF H-w realizes with the neighbor-sets A and B each lying on a radius-1 circle with DISTINCT centers s* != t*. Every clamp split vertex has degree >= 5, so {A,B} is a width >= 2 interface.
3. EXHAUSTIVELY DEAD (L45/L56/L57): in all 12 known chi-5 UDGs of the de Grey/Polymath lineage (199 to 874 vtx), every one of ~2.29M non-adjacent pairs is FREE: not forced-different, not forced-same. ALL color forcing in the lineage is adjacency-local. The missing object must come from a NEW chi-5 UDG built on a different principle.
4. THE MONOID OBSTRUCTION (L55): any gadget chain with single-vertex ports has its port relation confined (by S_k color symmetry) to the primitive monoid {0, I, J-I, J}; no color-shifter relations exist. The clamp question factors into (i) forced-same gadget [DEAD on lineage, L56/L57] or (ii) a WIDE interface (>= 2 boundary vertices) whose boundary-coloring transfer matrix is IMPRIMITIVE. Route (ii) is the only live combinatorial route.
5. MEASURABLE THREAD: chi_m(R^2) >= 5 classical (Falconer). The chi_m >= 6 attack (order-2 Lasserre moment SDP on Ambrus X_23 with O(2)-averaged J_0 Bochner kernel) is blocked on ONE engineering object: a custom sparse conic solver (S_k and O(2)-congruence reductions both built, validated, jointly insufficient: 48342 moment variables remain).
6. RIVAL HYPOTHESIS: de Grey's omega<=3 conjecture (predicts chi=5). The clamp ESCAPES its premise (forces a pair, never a clique), which is why the program's probability mass sits at chi=6.
7. Backward-from-2050 calibration (L54): most likely terminal answer chi=6 via finite UDG; dark horse = the definability split (the right question may be Borel chromatic chi_B, not chi).

THE WRONG-APPROACH DETECTORS (every proposal MUST self-check against all three):
- Q^2: the rational plane has chi=2 (Woodall). A combinatorial argument that lifts naively to Q^2 and would prove chi(Q^2)>=3 is structurally wrong. Euclidean content must enter through topology/density/rigidity of R.
- L^infty plane: chi=4 exactly (Chilakamarri). A geometric argument valid in every normed plane that proves >=5 is wrong; it must use Euclidean-specific rigidity (cocircularity, equilateral triangles, two unit circles meet in <=2 points).
- R^1: chi=2. A measure-theoretic argument blind to the rotation group O(2) is wrong.

KNOWN KILLS (do NOT re-propose; each is a logged negative result):
- Long-range forcing inside the known lineage (L45/L51/L56/L57: exhaustively absent).
- Single-vertex-port gadget chains / color-shifter relations (L55 monoid obstruction).
- "RG leading eigenvalue > 1" as a forcing diagnostic (L55: lambda_1 is coloring entropy, the OPPOSITE of forcing; right diagnostic is imprimitivity).
- DOF/over-determination counting or max-degree heuristics for realizability (L52: invalidated by P_510 at +1487 over-determination, degree 36).
- Groebner exact realizability beyond ~14 vertices (infeasible); single-hub rainbow forcing (Lemma L kills it: needs unit-K_k, but omega=3).
- Norm-blind Borel/Steinhaus lower bounds (fail L^infty detector: would over-prove chi>=7 where chi=4).
- Polygonal/map-type 6-colorings of the plane (collide with Voronov: map-type colorings need 7).
- Box-complex / topological coindex lower bounds as-is (calibrated: coind undershoots on chi=5 graphs).
- Degree-1 / order-1 moment relaxations for chi_m>=5 at X_23 (L43: margin 0, provably too weak; order-2 with IEC size-4 is the frontier).
- chi_m >= 6 does NOT imply chi >= 6 (chi <= chi_m always; the direction only helps via transfer principles).

REPO FACTS: Python + python-sat (cadical) + sympy exact arithmetic + networkx + cvxpy; Lean 4 skeleton; no C compiler on host (no nauty/pynauty); SAT solves on 500-2000 vtx UDGs are routine; exact Groebner to ~14 vtx.
`

const DEFAULT_LENSES = [
  { key: 'moduli', name: 'Inverse geometry / moduli of realizations', seed: 'Invert the search order: start from the geometric moduli space (two unit circles with distinct centers, a framework H-w pinned to them per Theorem R) and ask which abstract graphs a given configuration can support. Realization varieties, Cayley-Menger loci, frameworks with a 1-dim flex sweeping a cocircularity condition. Conjecture dimension formulas; propose continuation/homotopy search in moduli space rather than discrete graph search.' },
  { key: 'decidability', name: 'Logic / decidability / number-field staircase', seed: 'W3 for a fixed finite clamp is decidable (Tarski); the wall is computational. Where does chi jump as the coordinate field grows? Define the chromatic staircase of number fields; conjecture a Galois/height criterion for clamp-hosting fields. Can interval arithmetic + Smale alpha-theory certify a realization numerically with a posteriori exactness, bypassing Groebner limits at 20-50 vertices?' },
  { key: 'statmech', name: 'Statistical mechanics / tensor networks / SPT order', seed: 'The L55 monoid result smells like symmetry-protected topological order: nontrivial edge modes need a WIDE boundary carrying a projective representation. Width-2+ boundary transfer matrices = S_5-symmetric MPOs; H^2(S_5,U(1))=Z_2. Classify when an S_k-symmetric MPO on pair-ports can be imprimitive; propose SAT enumeration of all port relations achievable by <=15-vtx UDG gadgets with 2-vertex interfaces.' },
  { key: 'random', name: 'Random / extremal graph theory outside the lineage', seed: 'L57 proves the missing chi-5 UDG is OUTSIDE the lineage. What does a typical dense UDG look like? Random spindle-closures, random subsets of rotation-closed rings, Cayley graphs of finitely generated rotation subgroups. Conjecture a clamp-appearance threshold in edge density / algebraic complexity; propose a cheap out-of-lineage chi-5 UDG generator feeding the existing forced-pair SAT test.' },
  { key: 'upperbound', name: 'Upper-bound inversion / coloring the plane better', seed: 'If chi=6 a 6-coloring exists and all human colorings are map-type (Voronov forces 7 for those). What does a NON-map 6-coloring look like? Fractal color classes, substitution tilings with infinitely many orientations, Beatty/quasiperiodic colorings on rings. Pritikin: the plane minus density ~1/26000 is 6-colorable; conjecture where the defect concentrates. Or conjecture chi_m=7 while chi=6 via AC and how to detect that split.' },
  { key: 'se2', name: 'Harmonic analysis on the motion group SE(2)', seed: 'The repo Bochner kernel is the abelian shadow (O(2)-averaged J_0). The unit-distance graph is Cayley-like on SE(2) with infinite-dimensional Bessel-realized irreps. Do positivity/spectral bounds on SE(2) give strictly more than the abelian shadow? Conjecture a noncommutative Hoffman-type bound reaching chi_m >= 6 WITHOUT the sparse-SDP X_23 route; propose the smallest computable instance.' },
  { key: 'borel', name: 'Descriptive set theory / Borel chromatic number', seed: 'Dark horse: the right question may be chi_B. Bernshteyn local-to-Borel transfer converts finite combinatorics into Borel lower bounds. What LOCAL finite-UDG statement pushes chi_B >= 6 without the realizable clamp? Euclidean content must enter via the rotation group (irrational rotations, unique ergodicity), not norm-blind Steinhaus. Conjecture a chi_B >= 6 criterion as a finite expansion property of the unit-distance Schreier graph of a rotation action.' },
  { key: 'width2', name: 'Head-on width-2 interface classification', seed: 'The one live combinatorial route (L55 route ii). Ports are ordered pairs of vertices at fixed distance; port relations are S_5-symmetric subsets of (C^2)x(C^2) with 15 intersection-type orbits. Classify the imprimitive ones; which are realizable by small planar UDG gadgets (spindle chains sharing edges = width-2 interfaces)? Propose the exact SAT experiment enumerating port relations of spindle-chain gadgets and searching for imprimitive composition.' },
  { key: 'topology', name: 'Equivariant topology on configuration spaces', seed: 'Box complexes see only the abstract graph. The right space: the realization variety of unit-distance embeddings, fibered over colorings. Monodromy of the finite 5-coloring set along a FLEX of a flexible framework is a genuinely new invariant. Conjecture: a flexible chi-5 UDG whose flex monodromy acts without fixed points on its 5-colorings yields a chi>=6 certificate after closing the loop into a rigid graph. Make precise; smallest candidate (Bricard-style or 4-bar linkages inside spindle assemblies).' },
  { key: 'contrarian', name: 'Contrarian: the consensus is wrong', seed: 'Argue AGAINST the program. Position A: chi=5 and the clamp is non-realizable for an unproven deep reason (formulate the hidden rigidity theorem as a conjecture with a finite test). Position B: chi=7 and the 5-vs-6 fixation is survivorship bias (what is the smallest conceivable chi=7 mechanism given omega=3?). Pick the sharpest position, 2-3 falsifiable conjectures, and the experiment that would embarrass the chi=6 consensus fastest.' },
]

const BRIEF = (args && args.brief) ? args.brief : DEFAULT_BRIEF
const LENSES = (args && args.lenses) ? args.lenses : DEFAULT_LENSES

const BREVITY = 'BUDGET DISCIPLINE: decide fast, write tight. Do not pad reasoning; reach conclusions in as few steps as the math allows. Every output field has a purpose; no field needs more than ~200 words unless its schema says otherwise.'

const GEN_SCHEMA = {
  type: 'object',
  required: ['lens', 'first_principles', 'conjectures', 'experiment', 'detector_self_check'],
  properties: {
    lens: { type: 'string' },
    first_principles: { type: 'string', description: 'Ground-up derivation of the angle in <= 350 words. Why THIS structure is where the Euclidean-specific content lives.' },
    conjectures: {
      type: 'array', minItems: 2, maxItems: 4,
      items: {
        type: 'object',
        required: ['name', 'statement', 'falsifiable_prediction', 'why_plausible', 'how_it_could_be_wrong', 'novelty_claim'],
        properties: {
          name: { type: 'string' },
          statement: { type: 'string', description: 'Precise mathematical statement, crisp enough to be falsified.' },
          falsifiable_prediction: { type: 'string', description: 'A concrete computation or observation that would refute it.' },
          why_plausible: { type: 'string' },
          how_it_could_be_wrong: { type: 'string' },
          novelty_claim: { type: 'string', description: 'Why you believe this is unstated in the literature; nearest prior art.' }
        }
      }
    },
    experiment: {
      type: 'object',
      required: ['description', 'repo_feasibility', 'est_cost'],
      properties: {
        description: { type: 'string', description: 'The single cheapest decisive experiment, runnable on this repo stack (python-sat, sympy, cvxpy, no C compiler).' },
        repo_feasibility: { type: 'string' },
        est_cost: { type: 'string' }
      }
    },
    detector_self_check: {
      type: 'object',
      required: ['Q2', 'Linf', 'R1'],
      properties: {
        Q2: { type: 'string' },
        Linf: { type: 'string' },
        R1: { type: 'string' }
      }
    },
    wildness: { type: 'number', description: '1-10 self-rating of distance from existing literature.' }
  }
}

const ADV_SCHEMA = {
  type: 'object',
  required: ['verdict', 'kills', 'detector_results', 'prior_art_collisions', 'surviving_kernel', 'cheapest_decisive_test', 'steelman'],
  properties: {
    verdict: { type: 'string', enum: ['kill', 'wound', 'survive'] },
    kills: { type: 'array', items: { type: 'string' } },
    detector_results: {
      type: 'object',
      required: ['Q2', 'Linf', 'R1'],
      properties: {
        Q2: { type: 'string', enum: ['pass', 'fail', 'na'] },
        Linf: { type: 'string', enum: ['pass', 'fail', 'na'] },
        R1: { type: 'string', enum: ['pass', 'fail', 'na'] }
      }
    },
    prior_art_collisions: { type: 'array', items: { type: 'string' } },
    surviving_kernel: { type: 'string', description: 'Strongest idea that survives, even if the stated form dies. Empty if nothing.' },
    cheapest_decisive_test: { type: 'string' },
    steelman: { type: 'string', description: 'Best version of the proposal after your attacks.' }
  }
}

const genPrompt = (lens) => `You are BUILDER, a creative research mathematician on the Hadwiger-Nelson program. Generate a genuinely NOVEL first-principles attack through one assigned lens, with falsifiable conjectures. You are licensed to be wrong; you are NOT licensed to be derivative or vague.
${BREVITY}
${BRIEF}
YOUR ASSIGNED LENS: ${lens.name}
SEED (deviate freely if first principles lead elsewhere):
${lens.seed}
REQUIREMENTS:
- Reason from FIRST PRINCIPLES: derive why the Euclidean plane specifically (vs Q^2, vs L^infty, vs R^1) should exhibit the structure you propose.
- At least one conjecture must be something you believe has NEVER been stated in the literature. Wild but precise beats safe but vague.
- Every conjecture needs a falsifiable prediction checkable with this repo's stack.
- Do NOT re-propose anything on the KNOWN KILLS list; build PAST those walls.
- You may Read repo files for grounding (experiments/LEARNINGS.md, experiments/combinatorial/W3_CLAMP_REDUCTION.md, docs/research_atlas/README.md) but spend most of your budget THINKING. Working directory: c:/Users/Owen/dev/hadwiger-nelson.
- No em dashes anywhere in your output.
Return ONLY the structured output.`

const advPrompt = (gen) => `You are ADVERSARY on the Hadwiger-Nelson program. A BUILDER produced the proposal below. Try to KILL it: counterexamples, gaps, detector failures, collisions with known negative results, category errors. Then report honestly what survives.
${BREVITY}
${BRIEF}
THE PROPOSAL (JSON):
${JSON.stringify(gen, null, 1)}
ATTACK CHECKLIST:
1. Run all three detectors seriously; re-derive, do not trust the author's self-check.
2. Check every conjecture against the KNOWN KILLS list and the L42-L57 results in the brief.
3. Hunt for the SMALLEST counterexample: k=2 or 3, paths/cycles, Moser spindle, K_{3,3}, one spindle chain.
4. Category errors: chi vs chi_m vs chi_f vs chi_B; assuming forcing where L57 proves freeness; circular dependence on the open wall.
5. Prior art: Polymath16, KMOR/de Laat-Vallentin, Bernshteyn, classical rigidity.
6. Feasibility on this repo stack (no C compiler; SAT + sympy + cvxpy).
Verdict: kill = nothing usable; wound = stated form dies, kernel survives; survive = withstands attack.
You may Read repo files to check claims (cwd c:/Users/Owen/dev/hadwiger-nelson). No em dashes.
Return ONLY the structured output.`

phase('Generate')
log('Spawning ' + LENSES.length + ' lens generators (main model); adversary passes run on sonnet as each finishes')

const results = await pipeline(
  LENSES,
  (lens) => agent(genPrompt(lens), { label: 'gen:' + lens.key, phase: 'Generate', schema: GEN_SCHEMA, agentType: 'builder' }),
  (gen, lens) => gen
    ? agent(advPrompt(gen), { label: 'adv:' + lens.key, phase: 'Adversary', schema: ADV_SCHEMA, agentType: 'adversary', model: 'sonnet' }).then(adv => ({ lens: lens.key, gen, adv }))
    : null
)

const material = results.filter(Boolean)
log('Generated and stress-tested ' + material.length + ' of ' + LENSES.length + ' lens proposals')
if (material.length < LENSES.length) {
  log('Dropped ' + (LENSES.length - material.length) + ' lens(es) due to agent failure; synthesis proceeds on survivors')
}

phase('Synthesize')
const survivors = material.filter(m => m.adv && m.adv.verdict !== 'kill')
log(survivors.length + ' survive adversary; ' + (material.length - survivors.length) + ' killed outright')

// Trimmed projection: the synthesizer does not need detector self-checks, novelty
// essays, or feasibility prose; passing the full gen+adv JSON roughly triples its prompt.
const trimmed = material.map(m => ({
  lens: m.lens,
  conjectures: m.gen.conjectures.map(c => ({ name: c.name, statement: c.statement, falsifiable_prediction: c.falsifiable_prediction })),
  experiment: m.gen.experiment.description,
  verdict: m.adv.verdict,
  kills: m.adv.kills,
  surviving_kernel: m.adv.surviving_kernel,
  cheapest_decisive_test: m.adv.cheapest_decisive_test,
  steelman: m.adv.steelman,
}))

const synthPrompt = `You are SYNTHESIZER on the Hadwiger-Nelson program. Below are ${trimmed.length} lens proposals, each with an adversary verdict. Integrate them into a single ranked battle plan.
${BREVITY}
${BRIEF}
THE MATERIAL (JSON):
${JSON.stringify(trimmed, null, 1)}
DELIVER (plain markdown, your entire return value):
1. TOP 3 NOVEL CONJECTURES: restate each crisply, with falsifiable prediction, adversary status, and why it earns its rank. Prefer (a) genuinely new, (b) detector-clean, (c) decidable by a cheap repo experiment.
2. RANKED ATTACK PLAN by expected-information-per-cost: for each surviving direction, the one decisive experiment, what each outcome would mean, and which wall (W3 integer / sparse-SDP measurable) it attacks or routes around.
3. CROSS-LENS SYNERGIES: where two lenses are secretly the same attack or compose.
4. THE GRAVEYARD: one line per killed idea with the kill reason.
5. VERDICT: did this round produce anything genuinely new, or did everything bottom out at the same two walls again? Be honest.
No em dashes anywhere.`

const synthesis = await agent(synthPrompt, { label: 'synthesize', phase: 'Synthesize', agentType: 'synthesizer', model: 'sonnet' })

return { synthesis, survivors_count: survivors.length, killed: material.filter(m => m.adv && m.adv.verdict === 'kill').map(m => m.lens), material }
