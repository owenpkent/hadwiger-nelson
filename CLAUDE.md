# CLAUDE.md

Project-specific instructions for Claude Code. Read on every session start.

## What this repo is

A research-and-study project on the **Hadwiger-Nelson problem**: determining the chromatic number $\chi(\mathbb{R}^2)$ of the unit-distance graph on the Euclidean plane. Known bounds: $5 \leq \chi(\mathbb{R}^2) \leq 7$.

It contains:
- Layered docs (intuitive, undergraduate, graduate, research) on the problem
- A strategic landscape document (`docs/research_atlas/`) cataloging every known approach with its obstructions
- A computational experimental thread (`experiments/`) organized around four candidate proof architectures
- A Lean 4 / Mathlib formalization skeleton (`lean/`)

It is **not** a tool or product. It is a research codebase. Output: markdown documents, finite-graph constructions, SAT certificates, visualizations, and Lean proofs.

## About the owner

The owner is Owen, a wheelchair user with muscular dystrophy.

- **Typing is hard.** Be proactive. Make decisions. Don't ask for confirmation on small things.
- **Offer A/B/C choices** when input is needed. One letter is faster than a sentence.
- **PowerShell on Windows.** Use PowerShell syntax. Prefer single-line commands.

## Core conceptual framework

The project is organized around **four candidate proof architectures**:

1. **Combinatorial / Unit-Distance Graphs** (UDG): construct a finite unit-distance graph in $\mathbb{R}^2$ with chromatic number $\geq 6$ (or $\geq 7$). The de Grey 2018 result (1581 vertices, $\chi \geq 5$) lives here. SAT-driven.
2. **Measurable / spectral**: prove lower bounds on the *measurable* chromatic number $\chi_m$ using Falconer-style measure theory or autocorrelation / Fourier bounds. $\chi_m \geq 5$ is classical; $\chi_m \geq 6$ in recent work.
3. **Fractional / Lovász $\vartheta$**: fractional chromatic number $\chi_f$ and the spectrum of Cayley-graph-like operators on $\mathbb{R}^2$.
4. **Set-theoretic / axiomatic**: the Shelah-Soifer phenomenon and the dependence of $\chi(\mathbb{R}^2)$ on choice axioms; descriptive-set-theoretic refinements (Borel chromatic number).

## The wrong-approach detector discipline (inherited from the zeta repo)

The zeta-function repo uses the Davenport-Heilbronn $L$-function as its **wrong-approach detector**: any method in Architectures 1, 3, or 4 that does not distinguish $\zeta$ from $L_{\mathrm{DH}}$ is structurally wrong because $L_{\mathrm{DH}}$ has known off-line zeros.

The Hadwiger-Nelson analog uses three control objects:

- **$\mathbb{Q}^2$**: the unit-distance graph on $\mathbb{Q}^2$ has $\chi = 2$ (Woodall 1973). Any *combinatorial* method that gives $\chi(\mathbb{R}^2) \geq 5$ must use the topology / density of $\mathbb{R}$ in a way that fails on $\mathbb{Q}^2$. A graph-theoretic argument that "lifts" naively to $\mathbb{Q}^2$ and would imply $\chi(\mathbb{Q}^2) \geq 3$ is structurally wrong.
- **$L^\infty$ unit-distance graph on $\mathbb{R}^2$**: $\chi = 4$ exactly (Chilakamarri). Any *geometric* method that uses only the abstract structure of a normed plane (without invoking the existence of equilateral triangles, regular pentagons, or other rigidity specific to the Euclidean norm) is wrong.
- **$\mathbb{R}^1$ on the line**: trivially $\chi = 2$. Any *measure-theoretic* argument blind to the rotation group $O(2)$ would also constrain $\chi(\mathbb{R})$, which is impossible.

Implementation: `experiments/_shared/wrong_approach_detectors.py`. Architecture 2 (measurable) sits partly outside this discipline because measure-theoretic arguments can legitimately fail on $\mathbb{Q}^2$ (measure zero).

## Repository structure

```
hadwiger-nelson/
├── docs/
│   ├── 00_intuitive/            intuitive-level explanations
│   ├── 01_undergraduate/        Moser spindle, hexagonal upper bound, basic UDG
│   ├── 02_graduate/             measurable chromatic, AC issues, fractional χ
│   ├── 03_research/             open frontiers, proof program, eight directions
│   ├── implications/            why HN matters (Ramsey theory, geometry, complexity)
│   ├── solutions/               known proof attempts (de Grey, Polymath16, etc.)
│   └── research_atlas/          master research map; all approaches, failures, ML directions
├── experiments/
│   ├── PROOF_ARCHITECTURES_PLAN.md  the test plan with per-architecture status
│   ├── LEARNINGS.md             cross-cutting findings synthesis
│   ├── PUBLICATIONS.md          publication ledger: registry + rubric for publishable discoveries
│   ├── _shared/                 UDG interface, wrong-approach detectors, smoke test
│   ├── combinatorial/           Arch 1 (SAT-driven finite UDG search)
│   ├── measurable/              Arch 2 (Falconer-style, Fourier-analytic)
│   ├── fractional/              Arch 3 (χ_f, Lovász ϑ, spectral)
│   ├── axiomatic/               Arch 4 (Shelah-Soifer, Borel χ)
│   └── orchestrator_sessions/   per-session ORCHESTRATOR plans
├── lean/                        Lean 4 / Mathlib formal verification skeleton
├── paper/                       C1 note (forcing-sterility + codegree) + arxiv/ bundle
├── paper_solver/                C3 note (symmetry-broken SAT self-certification) + arxiv/ bundle
├── .claude/agents/              Agent role specs (cloned from zeta repo conventions)
├── sources/                     source PDFs (de Grey, Soifer, Falconer, etc.)
├── visualizations/              manim scenes
├── CLAUDE.md                    this file
├── README.md                    project overview
└── TODO.md                      task tracking
```

## Tech stack

- **Language**: Python (primary). Lean 4 (formal verification).
- **Python libraries**: `networkx` (graph manipulation), `python-sat` (SAT encoding), `numpy`, `scipy`, `sympy`, `matplotlib`, `cvxpy` (for Lovász ϑ).
- **SAT solvers**: cadical / kissat / cryptominisat. The de Grey / Polymath16 lineage uses SAT for $k$-colorability decisions on finite UDGs.
- **Visualization**: manim. `pip install manim`.
- **Formal verification**: Lean 4 + Mathlib (`lean/`).

## Conventions

- **Exact arithmetic** for unit-distance graphs: vertices live in number fields (e.g., $\mathbb{Q}(\sqrt{3})$ for hexagonal lattices, $\mathbb{Q}(\sqrt{3}, \sqrt{11})$ for Moser spindle and de Grey graphs). Use `sympy` for exact symbolic distances; `mpmath` only for floating-point sanity checks.
- **Data format**: graphs serialize as JSON (vertices as exact symbolic coords, edges as index pairs) or DIMACS / CNF for SAT instances. Stored alongside the script.
- **Caching**: SAT runs on large graphs are slow. Cache witnesses (colorings, unsat cores) under `experiments/**/_cache/`.
- **UDG interface**: every unit-distance graph implements `vertices()`, `edges()`, `chromatic_number_sat(k)` returning a coloring or UNSAT proof.

## Style

- **No em dashes** anywhere. (Global preference. Use periods, colons, parentheses, or hyphens.)
- Inline math in markdown uses `$...$` for inline, `$$...$$` for display.
- In chat output, use Unicode and plain text for math (no KaTeX surface).
- Code: explanatory module-level docstrings, minimal inline comments. Comments explain WHY, not WHAT.

## LEARNINGS.md conventions

- **Newest entries at the top.** When adding L_N, insert it directly below the format note in the header, not at the bottom. The file documents this in its own header.
- **Numbering is monotonic.** L1, L2, ..., L_N never re-numbered. New entries get the next N regardless of position in the file (so the top of the file currently shows L20, then L19, ..., down to L1 at the bottom).
- **Escape pipes inside math in table cells**: write `$\|V\|$`, not `$|V|$`. Markdown renderers treat unescaped `|` as a column separator and break the alignment row, sometimes rendering it as emoji. The backslash escape is invisible to LaTeX but tells Markdown the pipe is literal.
- **Don't put two `$...$` math blocks on the same table row without thinking** about whether some pipe regex might confuse them. `$\chi(H_1)$ | Half 2 | $\chi(H_2)$` is fine — the pipes between math blocks are real column separators. But a fix-up script that greedy-matches `$...|...$` will corrupt this; use the targeted `\$\|...\|\$` pattern instead. See [`experiments/_shared/fix_table_pipes.py`](experiments/_shared/fix_table_pipes.py).

## Git commits

```powershell
git add -A; git commit -m "docs: add Moser spindle exposition"; git push
```

Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.

Never commit or push without per-action authorization.

## Agent infrastructure

This repo can be operated using the same six-agent role spec as the zeta repo (SURVEYOR / BUILDER / VERIFIER / ADVERSARY / SYNTHESIZER / ORCHESTRATOR). See the zeta repo's `.claude/agents/` for the canonical specs; copy or adapt as needed.

## Known landmarks

- **Moser spindle** (1961): 7-vertex unit-distance graph with $\chi = 4$. Built from two rhombi of unit edges, vertex coordinates in $\mathbb{Q}(\sqrt{3}, \sqrt{11})$.
- **Hexagonal upper bound** (Isbell, ~1950): tile the plane with regular hexagons of diameter slightly less than 1, color with 7 colors in a repeating pattern. Gives $\chi(\mathbb{R}^2) \leq 7$.
- **de Grey 2018**: 1581-vertex UDG with $\chi \geq 5$. Verified by Marijn Heule (SAT proof). $\chi(\mathbb{R}^2) \geq 5$.
- **Polymath16**: reduced to UDGs with $\sim 510$ vertices proving $\chi \geq 5$.
- **Falconer 1981**: $\chi_m(\mathbb{R}^2) \geq 5$ for the *measurable* chromatic number.
- **Shelah-Soifer**: under ZF + DC (no full AC), $\chi(\mathbb{R}^2)$ can differ from its ZFC value.
- **$\mathbb{Q}^2$**: $\chi = 2$ (Woodall 1973). The structural control.

## When in doubt

- The atlas (`docs/research_atlas/README.md`) is the master reference for what's been tried and what's stuck.
- The plan (`experiments/PROOF_ARCHITECTURES_PLAN.md`) is the master reference for the experimental thread.
- The wrong-approach detector ($\mathbb{Q}^2$ has $\chi = 2$; $L^\infty$ on $\mathbb{R}^2$ has $\chi = 4$) is the structural sanity check.
- [`STATE_OF_THE_PROGRAM.md`](STATE_OF_THE_PROGRAM.md) is the one-page strategic snapshot; [`experiments/PHASE_STATE.md`](experiments/PHASE_STATE.md) is the resumable operational state (start here on a cold session).

## Gates and calibration discipline

Two runnable gates enforce the structural discipline. Run them before trusting a
new solver, encoding, or lower-bound argument, and wire them into CI.

- **Detector + calibration gate**: `python -m experiments._shared.smoke_test`
  actually *colors* the controls and asserts their known values (Moser $\chi=4$,
  $\mathbb{Q}^2$ $\chi=2$, $L^\infty$ $\chi=4$, $\mathbb{R}^1$ $\chi=2$, unit
  triangle $\chi=3$). `--full` adds the $\chi \ge 5$ anchor (a published
  5-chromatic UDG must be UNSAT at $k=4$). **Calibration rule: a new solver or
  encoding is not trusted until it reproduces this baseline.** Non-zero exit = a
  baseline broke.
- **Control-object firewall**: `python -m experiments.lemma_db.build_db` fails if
  any node whose argument is also valid on a control sits on a load-bearing path to
  a larger $\chi$ claim (it would over-prove on the control). `--frontier` lists the
  open nodes ready to attack; `--deps chi_r2_ge6` lists the goal's prerequisites.
