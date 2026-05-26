# Hadwiger-Nelson

A research-and-study project on the **chromatic number of the plane**: the smallest $k$ such that the points of $\mathbb{R}^2$ can be $k$-colored so that no two points at distance exactly $1$ receive the same color.

```
        5  ≤  χ(R²)  ≤  7
   (de Grey, 2018)  (Isbell, hexagonal tiling)
```

## Status

| Architecture | Thread | Current state |
|--------------|--------|---------------|
| 1. Combinatorial / UDG (SAT-driven) | de Grey 2018 → Polymath16 → smaller 5-chromatic UDGs | $\chi \geq 4$ Lean-verified (Moser spindle); $\chi \geq 5$ multi-solver SAT-verified on 510/517/529/553/826/1585 including the original de Grey graph |
| 2. Measurable / spectral | Falconer 1981; recent autocorrelation bounds | not yet started |
| 3. Fractional / Lovász $\vartheta$ | Cranston-Rabern; spectral on Cayley graphs of $\mathbb{R}^2$ | not yet started |
| 4. Set-theoretic / axiomatic | Shelah-Soifer phenomenon | not yet started |

## Verified results

- **`4 ≤ chromaticNumberOfPlane`** — Lean theorem in [`lean/HadwigerNelson/MoserBridge.lean`](lean/HadwigerNelson/MoserBridge.lean). Full pipeline: explicit 11-edge Moser-spindle graph on `Fin 7` → SAT-witness 4-coloring + `native_decide` non-3-coloring → `chromaticNumber = 4` → graph homomorphism to `planeUnitDistanceGraph` via 7 explicit Euclidean coordinates with $\sqrt{3}, \sqrt{11}, \sqrt{33}$ → `chromaticNumber_le_of_forall_imp`.

- **`χ ≥ 5` via multi-solver SAT** at six graphs in the Polymath16 / Heule / de Grey lineage: 510, 517, 529, 553, 826, and 1585 vertices (the last being the original de Grey 2018 graph that established `χ ≥ 5` historically). cadical195 + glucose4 independent agreement throughout. See [`experiments/LEARNINGS.md`](experiments/LEARNINGS.md) L3.

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

The next planned experiment is `experiments/combinatorial/e1a_moser_spindle.py` (verify chi(Moser) = 4 via SAT). See [`experiments/PROOF_ARCHITECTURES_PLAN.md`](experiments/PROOF_ARCHITECTURES_PLAN.md) for the full slate.

## Latest session

See [`experiments/orchestrator_sessions/`](experiments/orchestrator_sessions/) for per-session ORCHESTRATOR records. Most recent: `session_001_bootstrap.md`.

## When in doubt

- The atlas ([`docs/research_atlas/README.md`](docs/research_atlas/README.md)) is the master reference.
- The plan ([`experiments/PROOF_ARCHITECTURES_PLAN.md`](experiments/PROOF_ARCHITECTURES_PLAN.md)) tracks experimental status.
- The wrong-approach detector ($\mathbb{Q}^2$ + $L^\infty$ + $\mathbb{R}^1$) is the structural sanity check.
