# Hadwiger-Nelson

A research-and-study project on the **chromatic number of the plane**: the smallest $k$ such that the points of $\mathbb{R}^2$ can be $k$-colored so that no two points at distance exactly $1$ receive the same color.

```
        5  ≤  χ(R²)  ≤  7
   (de Grey, 2018)  (Isbell, hexagonal tiling)
```

## Status

| Architecture | Thread | Current state |
|--------------|--------|---------------|
| 1. Combinatorial / UDG (SAT-driven) | de Grey 2018 → Polymath16 → smaller 5-chromatic UDGs | $\chi \geq 4$ Lean-verified (Moser spindle); $\chi \geq 5$ multi-solver SAT-verified on 510/517/529/553/826/1585; binding-rotation search exhausted in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ (L14); reverse-engineered Polymath 510 and de Grey 1585 as the "two 4-chromatic halves + bridges" coupling construction (L15-L20); covering lemma + list-coloring reformulation (L21-L22, both Lean-formalized); L21's 14-vertex Moser$^2$ abstract chi-5 graph proven NOT UDG-realizable via Positivstellensatz (L23); triple-coupling theorem for chi $\geq 6$ (L24); four obstruction classes catalogued (L25); Polymath 510 vertex-critical (L26); **first no-$K_4$ chi $\geq 6$ abstract graph constructed: $P_{510}^2$ + 2700 bridges, 1020 vertices, triple-solver SAT verified (L27), not UDG-realizable** |
| 2. Measurable / spectral | Falconer 1981; recent autocorrelation bounds | dossier landed (arch2_measurable_lineage.md); 512×512 autocorrelation experiment (e2a); $\chi_m \geq 5$ depends on a missing 6-chromatic finite UDG (L4) |
| 3. Fractional / Lovász $\vartheta$ | OFV 2010, KMOR 2015, Ambrus 2023 LP lineage | $m_1(\mathbb{R}^2) \leq 0.2584$ at 17 vertices via greedy beam search (e3h), matching KMOR 2015's published bound; integer $\chi_m \geq 4$, real $\geq 3.87$ |
| 4. Set-theoretic / axiomatic | Shelah-Soifer phenomenon | dossier landed (arch4_set_theoretic_lineage.md); 2003 conditional was made vacuous by de Grey 2018 (L7) |

## Verified results

- **`4 ≤ chromaticNumberOfPlane`** — Lean theorem in [`lean/HadwigerNelson/MoserBridge.lean`](lean/HadwigerNelson/MoserBridge.lean). Full pipeline: explicit 11-edge Moser-spindle graph on `Fin 7` → SAT-witness 4-coloring + `native_decide` non-3-coloring → `chromaticNumber = 4` → graph homomorphism to `planeUnitDistanceGraph` via 7 explicit Euclidean coordinates with $\sqrt{3}, \sqrt{11}, \sqrt{33}$ → `chromaticNumber_le_of_forall_imp`.

- **`χ ≥ 5` via multi-solver SAT** at six graphs in the Polymath16 / Heule / de Grey lineage: 510, 517, 529, 553, 826, and 1585 vertices (the last being the original de Grey 2018 graph that established `χ ≥ 5` historically). cadical195 + glucose4 independent agreement throughout. See [`experiments/LEARNINGS.md`](experiments/LEARNINGS.md) L3.

- **OFV 2010 reproduction**: $m_1(\mathbb{R}^2) \leq 0.268412$ exactly matches OFV Table 3.1 via 3-multiplier dual LP with simplex strengthening, see e3c and L8.

- **Architecture 3 LP frontier**: $m_1(\mathbb{R}^2) \leq 0.2584$ via greedy beam search over IE-LP configurations (e3h, L13). Closes 88% of the OFV (0.2684) to Ambrus (0.2470) gap. Reaching integer $\chi_m \geq 5$ requires $m_1 < 0.2$, currently open via this route.

- **Universal chi ≥ 5 mechanism identified (L14-L20)**: Every published $\chi \geq 5$ UDG (de Grey 1585, Polymath 510, Heule 553/826) is an instance of the "two 4-chromatic halves coupled by bridge edges" pattern. de Grey 1585 splits as 778v (C_6 core, chi=4) + 807v (asymmetric half, chi=4) + 155 bridges (L17). Polymath 510 has the same pattern: 315v + 195v + 833 bridges (L20). Polymath 510 is essentially a translated substructure of de Grey 1585 (62% vertex overlap under $T = (2, 0)$) (L19). The chi $\geq 5$ obstruction is delocalized (L18).

- **Covering lemma + list-coloring theorem (L21, L22)**: characterizes the bridge structure that forces chi $\geq 5$. $\chi(H_1 \cup H_2 \cup B) \geq 5$ iff $H_2$ is not list-colorable from lists $L(v) = [4] \setminus F(v)$ where $F(v) = \{c_1(u) : (u,v) \in B\}$. Single-vertex empty-list is the strongest local obstruction. Both theorems formally proven in Lean 4 + Mathlib with zero sorries ([`lean/HadwigerNelson/L21CoveringLemma.lean`](lean/HadwigerNelson/L21CoveringLemma.lean), [`L22ListColoring.lean`](lean/HadwigerNelson/L22ListColoring.lean)).

- **L21's 14-vertex Moser$^2$ abstract chi-5 graph is NOT UDG-realizable (L23)**: certified by a degree-1 Positivstellensatz over $\mathbb{Q}(\sqrt{33})$: $\frac{5 - \sqrt{33}}{6} g_1 + \frac{-15 + \sqrt{33}}{18} g_2 + g_3 = -\frac{2}{3}$ for same-$j$ bridge differences, with Groebner basis = $\{1\}$ cross-check. Max simultaneously realizable bridge subset is 7 of 14 (50%). The geometric obstruction is cocircularity: $H_2$'s vertex 6 needs 5 cocircular endpoints in $H_1$ at radius 1, but the canonical Moser embedding gives radii in $[0.51, 5.94]$.

- **Triple-coupling theorem for chi $\geq 6$ (L24)**: $\chi(H_1 \cup H_2 \cup H_3 \cup B_{12} \cup B_{13} \cup B_{23}) \geq 6$ iff for every proper 5-coloring of $H_1$, the residual list-coloring on $(H_2 \cup H_3 \cup B_{23})$ is infeasible. 1767 random no-$K_4$ three-Moser configurations yield ZERO chi $\geq 6$ instances; conjecture C5 says three Moser spindles + no-$K_4$ bridges cap at chi = 5. The chi-6 UDG path must use either non-4-choosable halves or chi-5 halves (Polymath 510 $\times$ Polymath 510 + bridges is the natural next target).

- **Four no-$K_4$ chi=5 obstruction classes (L25)**: smallest abstract record is $W_5 \times W_5$ at $V = 12$, $\|B\| = 11$ (adjacent-singleton obstruction), but $W_5$ itself is not a UDG. Three structural obstruction shapes realize L22: empty-list (Moser$^2$), adjacent-singleton ($W_5^2$), global non-local ($W_5 \times$ Moser).

- **Polymath 510 is vertex-critical for $\chi \geq 5$ (L26)**: all 510 single-vertex removals are 4-colorable (Cadical SAT, 104s). Phase 2 pair-removal sweep landed zero successes in 56,500 of 127,291 pairs before the agent crashed on API overload; the script checkpoints and resumes.

- **First no-$K_4$ chi $\geq 6$ abstract graph (L27)**: $P_{510} \cup P_{510} \cup B$ with $\|B\| = 2700$ bridges on 1020 vertices, $\omega = 3$, $\chi \geq 6$ triple-solver SAT verified (Cadical 87s, Glucose 353s, Minisat 735s). First constructive chi-6 abstract structure in the de Grey / Polymath lineage that does NOT use a $K_n$ cross-clique trick. Validates the L21 $\to$ L24 covering ladder end-to-end at the chi-5 level. **Not UDG-realizable** in $\mathbb{R}^2$: all 97 saturating $H_2$-vertices fail cocircularity (L23 obstruction at scale). New conjectured obstruction class: rainbow forcing driven by Polymath 510's vertex-criticality.

- **Bridge minimum tightened to $\|B\| \leq 2000$ (L28)**: 700-bridge reduction (26%) on the L27 construction, Cadical UNSAT at $K = 2000$ (1687s). Bracket $(1500, 2000]$. Triggers obstruction-class shift from "97 always-saturating" to "43 always-saturating + 54 graded rainbow"; chi-6 forcing now relies on joint distribution of partial saturations rather than universal saturation. Refines conjecture R5 to R5' (Hall-matching over restricted color lists). UDG realizability unchanged.

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
├── sources/                     source PDFs
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

See [`experiments/PROOF_ARCHITECTURES_PLAN.md`](experiments/PROOF_ARCHITECTURES_PLAN.md) for the full slate of experiments (e1a-e1t, e2a, e3a-e3h all landed).

## Long-range research program

See [`experiments/SOLVING_PROGRAM.md`](experiments/SOLVING_PROGRAM.md) for the six-shot taxonomy of substantive attacks on the conjecture. Three of four architectures gate on the same missing combinatorial object: **a finite unit-distance graph in $\mathbb{R}^2$ with chromatic number $\geq 6$**. Found once, three barriers collapse.

## Latest sessions

See [`experiments/orchestrator_sessions/`](experiments/orchestrator_sessions/) for per-session ORCHESTRATOR records. Most recent:
- `session_011_polymath_degrey_overlap.md` — Polymath 510 is a translated substructure of de Grey 1585; 62% vertex overlap under $T = (2, 0)$.
- `session_010_obstruction_mechanism.md` — de Grey 1585's chi = 5 obstruction is a three-component coupling (C_6 core + asymmetric half + 155 bridges). Universal "two halves + bridges" pattern.
- `session_009_degrey1585.md` — de Grey 1585 symmetry analysis: natural center $v_0 = (2, 0)$; approximate D_6; C_6-symmetric core has chi = 4.
- `session_008_reverse_engineer_polymath510.md` — Polymath 510 has approximate C_6 about origin (92% coverage); C_6 closure is 1155v, chi = 5, C_6-irreducible.
- `session_007_field_theoretic_binding.md` — Binding-rotation enumeration in $\mathbb{Q}(\sqrt 3, \sqrt{11})$ for chi >= 6; 211-vertex union, density 3.46, chi = 4.
- `session_006_ambrus_beam.md` — Shot 5 reframed to Ambrus IE-LP; greedy beam search to $m_1 \leq 0.2584$ matching KMOR 2015.

## When in doubt

- The atlas ([`docs/research_atlas/README.md`](docs/research_atlas/README.md)) is the master reference.
- The plan ([`experiments/PROOF_ARCHITECTURES_PLAN.md`](experiments/PROOF_ARCHITECTURES_PLAN.md)) tracks experimental status.
- The wrong-approach detector ($\mathbb{Q}^2$ + $L^\infty$ + $\mathbb{R}^1$) is the structural sanity check.
