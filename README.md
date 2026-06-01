# Hadwiger-Nelson

A research-and-study project on the **chromatic number of the plane**: the smallest $k$ such that the points of $\mathbb{R}^2$ can be $k$-colored so that no two points at distance exactly $1$ receive the same color.

```
        5  ≤  χ(R²)  ≤  7
   (de Grey, 2018)  (Isbell, hexagonal tiling)
```

## Status

| Architecture | Thread | Current state |
|--------------|--------|---------------|
| 1. Combinatorial / UDG (SAT-driven) | de Grey 2018 → Polymath16 → smaller 5-chromatic UDGs | $\chi \geq 4$ Lean-verified (Moser spindle); $\chi \geq 5$ multi-solver SAT-verified on 510/517/529/553/826/1585; binding-rotation search exhausted in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ (L14); reverse-engineered Polymath 510 and de Grey 1585 as the "two 4-chromatic halves + bridges" coupling construction (L15-L20); covering lemma + list-coloring reformulation (L21-L22, both Lean-formalized); L21's 14-vertex Moser$^2$ abstract chi-5 graph proven NOT UDG-realizable via Positivstellensatz (L23); triple-coupling theorem for chi $\geq 6$ (L24); four obstruction classes catalogued (L25); Polymath 510 vertex-critical (L26); first no-$K_4$ chi $\geq 6$ abstract graph $P_{510}^2$ + 2700 bridges, 1020 vtx (L27), tightened to $\|B\| \leq 2000$ then shaved to a **1019-vertex record** (L28, L30) and a second NON-diagonal instance $P_{510} \cup P_{553}$ (L29); ALL not UDG-realizable, barrier sharpened (L34) to "realizable bridges are the wrong shape for chi-6" (Direction A + Shot 2 closed); the cocircularity barrier was adversarially PRESSURE-TESTED (L42): no chi-6 UDG, but reduced to a crisp Lemma (in $P_{510}$ forced-different $=$ adjacent, so a realizable rainbow hub would need a unit-distance $K_5$), and the cocircularity obstruction itself is the classical $K_{2,3}$-freeness of UDGs; L24 triple-coupling lift and the chi $\geq 5$ bridge theorem (HN-4) Lean-formalized |
| 2. Measurable / spectral | Falconer 1981; OFV/DMOV spectral SDP; multi-class moment LP | $\chi_m(\mathbb{R}^2) \geq 5$ (Falconer) is the best known and **$\chi_m \geq 6$ is OPEN** (the cited "$\geq 6$" results are misattributions) (L31); OFV 2-point Bessel bound reproduced + cross-validated, 3-point no gain (e2b, L32); Falconer's $\chi_m \geq 5$ decomposed, gated on the same missing rigid 5-chromatic UDG as Arch 1 (e2c, L33); single-class density PROVABLY capped at $\geq 5$ (Croft floor $> 1/5$), so $\geq 6$ needs a JOINT argument (L37); the multi-class (joint $k$-coloring) measurable moment LP built + validated as the one un-capped route (e3k formulation $\to$ e3l IEC sharpness $\to$ e3m degree-1 backend $\to$ e3n order-2; L38-L41), but the naive order-2 SDP does not scale to $X_{23}$ (needs symmetry reduction) and has not yet produced a bound |
| 3. Fractional / Lovász $\vartheta$ | OFV 2010, KMOR 2015, Ambrus 2023 LP lineage | reproduced Ambrus 2023 and **SELF-CERTIFIED it in-repo**: the repo's own IE-LP + IEC congruence dual gives $m_1(\mathbb{R}^2) \leq 0.2469 < 1/4$, i.e. **integer $\chi_m \geq 5$** (e3i/e3j, L35/L36), solver-cross-checked; the LP density route is now capped at $\geq 5$ (conjectured $\alpha_1 = 1/4$) |
| 4. Set-theoretic / axiomatic | Shelah-Soifer phenomenon | dossier landed (arch4_set_theoretic_lineage.md); 2003 conditional was made vacuous by de Grey 2018 (L7) |

## Verified results

- **`4 ≤ chromaticNumberOfPlane`** — Lean theorem in [`lean/HadwigerNelson/MoserBridge.lean`](lean/HadwigerNelson/MoserBridge.lean). Full pipeline: explicit 11-edge Moser-spindle graph on `Fin 7` → SAT-witness 4-coloring + `native_decide` non-3-coloring → `chromaticNumber = 4` → graph homomorphism to `planeUnitDistanceGraph` via 7 explicit Euclidean coordinates with $\sqrt{3}, \sqrt{11}, \sqrt{33}$ → `chromaticNumber_le_of_forall_imp`.

- **`χ ≥ 5` via multi-solver SAT** at six graphs in the Polymath16 / Heule / de Grey lineage: 510, 517, 529, 553, 826, and 1585 vertices (the last being the original de Grey 2018 graph that established `χ ≥ 5` historically). cadical195 + glucose4 independent agreement throughout. See [`experiments/LEARNINGS.md`](experiments/LEARNINGS.md) L3.

- **OFV 2010 reproduction**: $m_1(\mathbb{R}^2) \leq 0.268412$ exactly matches OFV Table 3.1 via 3-multiplier dual LP with simplex strengthening, see e3c and L8.

- **Integer $\chi_m(\mathbb{R}^2) \geq 5$, self-certified in-repo (L35, L36)**: reproduced the Ambrus 2023 bound from its exact 23-point config (47 unit edges, verified in $\mathbb{Q}(\sqrt 3, \sqrt{11})$), then closed the certificate gap by implementing the inclusion-exclusion congruence (IEC) constraints in the repo's own IE-LP. The repo's own cvxpy dual gives $m_1 \leq 0.246894 < 1/4$ (no reliance on the paper's unpublished duals); the $1/4$ crossing (hence integer $\chi_m \geq 5$ by the covering argument) is solver-independent (HiGHS + SCS). The earlier beam-search frontier was $m_1 \leq 0.2584$ (e3h, L13). The density route is now capped at $\chi_m \geq 5$ (conjectured $\alpha_1 = 1/4$).

- **Universal chi ≥ 5 mechanism identified (L14-L20)**: Every published $\chi \geq 5$ UDG (de Grey 1585, Polymath 510, Heule 553/826) is an instance of the "two 4-chromatic halves coupled by bridge edges" pattern. de Grey 1585 splits as 778v (C_6 core, chi=4) + 807v (asymmetric half, chi=4) + 155 bridges (L17). Polymath 510 has the same pattern: 315v + 195v + 833 bridges (L20). Polymath 510 is essentially a translated substructure of de Grey 1585 (62% vertex overlap under $T = (2, 0)$) (L19). The chi $\geq 5$ obstruction is delocalized (L18).

- **Covering lemma + list-coloring theorem (L21, L22)**: characterizes the bridge structure that forces chi $\geq 5$. $\chi(H_1 \cup H_2 \cup B) \geq 5$ iff $H_2$ is not list-colorable from lists $L(v) = [4] \setminus F(v)$ where $F(v) = \{c_1(u) : (u,v) \in B\}$. Single-vertex empty-list is the strongest local obstruction. Both theorems formally proven in Lean 4 + Mathlib with zero sorries ([`lean/HadwigerNelson/L21CoveringLemma.lean`](lean/HadwigerNelson/L21CoveringLemma.lean), [`L22ListColoring.lean`](lean/HadwigerNelson/L22ListColoring.lean)).

- **L21's 14-vertex Moser$^2$ abstract chi-5 graph is NOT UDG-realizable (L23)**: certified by a degree-1 Positivstellensatz over $\mathbb{Q}(\sqrt{33})$: $\frac{5 - \sqrt{33}}{6} g_1 + \frac{-15 + \sqrt{33}}{18} g_2 + g_3 = -\frac{2}{3}$ for same-$j$ bridge differences, with Groebner basis = $\{1\}$ cross-check. Max simultaneously realizable bridge subset is 7 of 14 (50%). The geometric obstruction is cocircularity: $H_2$'s vertex 6 needs 5 cocircular endpoints in $H_1$ at radius 1, but the canonical Moser embedding gives radii in $[0.51, 5.94]$.

- **Triple-coupling theorem for chi $\geq 6$ (L24)**: $\chi(H_1 \cup H_2 \cup H_3 \cup B_{12} \cup B_{13} \cup B_{23}) \geq 6$ iff for every proper 5-coloring of $H_1$, the residual list-coloring on $(H_2 \cup H_3 \cup B_{23})$ is infeasible. 1767 random no-$K_4$ three-Moser configurations yield ZERO chi $\geq 6$ instances; conjecture C5 says three Moser spindles + no-$K_4$ bridges cap at chi = 5. The chi-6 UDG path must use either non-4-choosable halves or chi-5 halves (Polymath 510 $\times$ Polymath 510 + bridges is the natural next target).

- **Four no-$K_4$ chi=5 obstruction classes (L25)**: smallest abstract record is $W_5 \times W_5$ at $V = 12$, $\|B\| = 11$ (adjacent-singleton obstruction), but $W_5$ itself is not a UDG. Three structural obstruction shapes realize L22: empty-list (Moser$^2$), adjacent-singleton ($W_5^2$), global non-local ($W_5 \times$ Moser).

- **Polymath 510 is vertex-critical for $\chi \geq 5$ (L26)**: all 510 single-vertex removals are 4-colorable (Cadical SAT, 104s). Phase 2 pair-removal sweep landed zero successes in 56,500 of 127,291 pairs before the agent crashed on API overload; the script checkpoints and resumes.

- **First no-$K_4$ chi $\geq 6$ abstract graph (L27)**: $P_{510} \cup P_{510} \cup B$ with $\|B\| = 2700$ bridges on 1020 vertices, $\omega = 3$, $\chi \geq 6$ triple-solver SAT verified (Cadical 87s, Glucose 353s, Minisat 735s). First constructive chi-6 abstract structure in the de Grey / Polymath lineage that does NOT use a $K_n$ cross-clique trick. Validates the L21 $\to$ L24 covering ladder end-to-end at the chi-5 level. **Not UDG-realizable** in $\mathbb{R}^2$: all 97 saturating $H_2$-vertices fail cocircularity (L23 obstruction at scale). New conjectured obstruction class: rainbow forcing driven by Polymath 510's vertex-criticality.

- **Bridge minimum tightened to $\|B\| \leq 2000$ (L28)**: 700-bridge reduction (26%) on the L27 construction, Cadical UNSAT at $K = 2000$ (1687s), dual-confirmed (Glucose UNSAT 10550s). Bracket $(1500, 2000]$. Triggers F-profile shift from "97 always-saturating" to "43 always-saturating + 54 graded". L27's R5 rainbow-forcing conjecture is REFUTED by a $C_5$ counterexample. UDG realizability unchanged.

- **Second NON-diagonal chi $\geq 6$ graph + a 1019-vertex record (L29, L30)**: mixed halves $P_{510} \cup P_{553} + B$ (1063 vtx, $\|B\| = 2400$, $\omega = 3$, dual-solver $\chi \geq 6$) show the chi-6 forcing is not an artifact of the diagonal $H_1 = H_2$ symmetry (Direction A). Mixed halves cannot beat the 1020-vertex baseline (every corpus half is $\geq 510$). Deletion probing then shaved the diagonal graph to a **1019-vertex** no-$K_4$ $\chi \geq 6$ graph (single long-budget vertex removal, UNSAT confirmed twice; bulk deletion of $\geq 8$ breaks chi-6). The true vertex-minimum is open ($\leq 1019$).

- **Realizability vs chi-6 forcing are structurally in tension (L34, Shot 2)**: building couplings coordinate-first (so plane-embedding holds by construction, joined only by genuine unit-distance bridges) NEVER forces $\chi \geq 6$, even with 13,757 real bridges ($5\times$ the abstract requirement) on a 3-way $P_{510}$ orbit. Realizable bridges come out even / low-concentration while chi-6 forcing needs concentration; the bridges geometry supplies and the bridges chi-6 needs are disjoint. This sharpens the L23/L27 cocircularity barrier and closes the coupling route for the published lineage.

- **Measurable frontier corrected (L31-L33)**: $\chi_m(\mathbb{R}^2) \geq 5$ (Falconer 1981) is the best known measurable bound; **$\chi_m \geq 6$ is OPEN** (the widely-cited "$\geq 6$" results are misattributions: DeCorte-Golubev is the hyperbolic plane, Coulson/Townsend are convex-tile colorings). The OFV 2-point spectral bound was reproduced from the radial-Fourier side and the 3-point matrix lift gave no improvement (e2b); Falconer's $\chi_m \geq 5$ decomposes into a density route and a rigidity route, both gated at $\geq 6$ by the same missing rigid 5-chromatic UDG as Architecture 1 (e2c).

- **`5 ≤ chromaticNumberOfPlane` bridge theorem, Lean-formalized (HN-4 groundwork)**: [`lean/HadwigerNelson/DeGreyLowerBound.lean`](lean/HadwigerNelson/DeGreyLowerBound.lean), zero sorry, axioms = {propext, Classical.choice, Quot.sound}. A graph hom into `planeUnitDistanceGraph` plus non-4-colorability yields $5 \leq \chi(\mathbb{R}^2)$ (the chi $\geq 5$ analog of `MoserBridge`). Reduces a full formal de Grey $\chi \geq 5$ to supplying one non-4-colorable embeddable UDG; the remaining LRAT-checker + 2500-edge embedding pieces are scoped in [`lean/SHOT4_PLAN.md`](lean/SHOT4_PLAN.md).

## Structure (mirrors the zeta-function research repo)

```
hadwiger-nelson/
├── docs/
│   ├── 00_intuitive/            what is the problem
│   ├── 01_undergraduate/        Moser spindle, hexagonal upper bound
│   ├── 02_graduate/             measurable chromatic number, AC issues
│   ├── 03_research/             open frontiers, proof program
│   ├── implications/            why HN matters
│   ├── solutions/               known proof attempts / lineages
│   └── research_atlas/          master research map
├── experiments/
│   ├── PROOF_ARCHITECTURES_PLAN.md
│   ├── LEARNINGS.md
│   ├── _shared/                 UDG interface; wrong-approach detectors (Q², L∞)
│   ├── combinatorial/           Arch 1: finite UDG construction + SAT
│   ├── measurable/              Arch 2: measure-theoretic
│   ├── fractional/              Arch 3: fractional χ, spectral, Lovász ϑ
│   └── axiomatic/               Arch 4: set-theoretic / Shelah-Soifer
├── lean/                        Lean 4 / Mathlib formal verification skeleton
├── sources/                     source data + reference library
│   ├── LIBRARY.md               annotated catalog of 19 source texts
│   ├── notes/                   deep per-text reading notes + synthesis
│   ├── cnp-sat/                 Polymath16/Heule graph + SAT data
│   └── *.dimacs / *.vtx / ...   de Grey / Heule / Polymath16 graph files
├── visualizations/              manim scenes
├── CLAUDE.md                    project instructions for Claude Code
├── README.md                    this file
└── TODO.md                      task tracking
```

## Wrong-approach detectors (the structural discipline)

This project inherits the Davenport-Heilbronn discipline from the zeta repo. For Hadwiger-Nelson the analogous control objects are:

- **$\mathbb{Q}^2$**: the unit-distance graph on the rational plane has $\chi = 2$ (Woodall, 1973). Any combinatorial method that proves $\chi(\mathbb{R}^2) \geq 5$ must use something that fails on $\mathbb{Q}^2$, namely the topology / density of $\mathbb{R}$.
- **$L^\infty$ unit-distance graph on $\mathbb{R}^2$**: $\chi = 4$ exactly. Any geometric method must use the Euclidean metric, not generic norm structure.
- **$\mathbb{R}$ on the line**: trivially $\chi = 2$. Any "dimension-blind" measure-theoretic argument that does not use the 2D rotation group fails here.

Implementation: `experiments/_shared/wrong_approach_detectors.py`.

## Tech stack

- **Python**: primary. `networkx` (graph manipulation), `pysat` / `python-sat` (SAT encoding of $k$-colorability), `numpy`, `scipy`, `matplotlib`.
- **SAT**: cadical / kissat / cryptominisat for the UDG colorability searches.
- **Lean 4 / Mathlib**: formal-verification skeleton in `lean/`.
- **Visualization**: manim for animations of UDGs, colorings, the Moser spindle, de Grey's graph.

## Running

```powershell
# Install Python deps (once)
pip install -r requirements.txt

# Smoke test the shared infrastructure
python -m experiments._shared.smoke_test
#   expect: 6/6 tests passed (Moser spindle 7 vertices 11 edges; Q^2, L^infty, R^1 controls)

# Build the Lean substrate (once elan is installed)
cd lean
lake exe cache get   # fetches Mathlib v4.13.0 oleans
lake build           # 1859 modules
```

See [`experiments/PROOF_ARCHITECTURES_PLAN.md`](experiments/PROOF_ARCHITECTURES_PLAN.md) for the full slate of experiments (Arch 1: e1a-e1y, h1-h7, f1pt; Arch 2/3: e2a-e2c, e3a-e3n all landed).

## Publishable findings

See [`docs/PUBLISHABLE_FINDINGS.md`](docs/PUBLISHABLE_FINDINGS.md) for an honest, tiered assessment of what is and is not publishable. Bottom line: **nothing moves the known bounds.** The strongest candidate (F1, the structural explanation of the $\chi \geq 6$ wall) was adversarially pressure-tested (L42) and is real-but-modest: its geometric core is the classical $K_{2,3}$-freeness of unit-distance graphs, and what survives is one clean open problem -- *find a chi-5 UDG with long-range color forcing (a non-adjacent pair forced-different in every proper 5-coloring)*, exactly what a chi-6 coupling needs and what the de Grey / Polymath lineage lacks.

## Long-range research program

See [`experiments/SOLVING_PROGRAM.md`](experiments/SOLVING_PROGRAM.md) for the six-shot taxonomy of substantive attacks on the conjecture. Three of four architectures gate on the same missing combinatorial object: **a finite unit-distance graph in $\mathbb{R}^2$ with chromatic number $\geq 6$**. Found once, three barriers collapse.

## Latest findings

Newest at the top; see [`experiments/LEARNINGS.md`](experiments/LEARNINGS.md) for full entries.
- **L42** — F1 (cocircularity barrier) adversarially pressure-tested: no chi-6 UDG; reduced to a crisp Lemma; cocircularity $=$ classical $K_{2,3}$-freeness; open reframing "long-range color forcing." See [`docs/PUBLISHABLE_FINDINGS.md`](docs/PUBLISHABLE_FINDINGS.md) and [`experiments/combinatorial/F1_pressure_test.md`](experiments/combinatorial/F1_pressure_test.md).
- **L38-L41** — the multi-class measurable moment LP toward $\chi_m \geq 6$: formulation (e3k), IEC sharpness (e3l), degree-1 backend (e3m), order-2 (e3n, naive build does not scale).
- **L37** — 19-text reference library read; single-class density route pinned as capped at $\chi_m \geq 5$.
- **L35/L36** — integer $\chi_m(\mathbb{R}^2) \geq 5$ reproduced and self-certified in-repo.
- **L34** — coordinate-first realizable couplings (up to 13,757 unit-distance bridges) never force chi-6 (later sharpened by L42).

Per-session ORCHESTRATOR records (Arch-1 reverse-engineering, sessions 006-011) are in [`experiments/orchestrator_sessions/`](experiments/orchestrator_sessions/).

## When in doubt

- The atlas ([`docs/research_atlas/README.md`](docs/research_atlas/README.md)) is the master reference.
- The plan ([`experiments/PROOF_ARCHITECTURES_PLAN.md`](experiments/PROOF_ARCHITECTURES_PLAN.md)) tracks experimental status.
- The wrong-approach detector ($\mathbb{Q}^2$ + $L^\infty$ + $\mathbb{R}^1$) is the structural sanity check.
