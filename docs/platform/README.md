# ASSAY: an autonomous mathematical research loop built to distrust itself

> An assay is the test you run on ore before you believe it is gold. This platform
> is named for the test, not for the mining.

## The thesis

Most autonomous research systems are optimized to **find** results. This one is
optimized to **not believe false ones**, and treats finding as the easy half.

That is not a stylistic preference. It comes from a measurement. Over one working
session on the Hadwiger-Nelson program, the loop produced three genuine results and
**five defects that would have produced confident, wrong mathematics**. Every one of
the five was caught by a gate rather than by inspection, and four of the five were
silent: they produced a clean-looking answer with no error anywhere.

| defect | what it would have claimed | what caught it |
|--------|---------------------------|----------------|
| Wrong Kostochka-Yancey floor at $k=5$ | An empty edge window reported as a checked UNSAT ("no such graph") | Calibration rung demanding a KNOWN answer ($f(5)=11$) |
| Hardcoded $n=19$ window as 52..60 (true: 52..61) | "$n=19$ COMPLETE" with cell $m=61$ never tested | Failure-mode audit against the computed window |
| Rotor applied to $(1,0)$ only, not the generating set | A field reported inert that in fact binds | Calibration rung demanding the Moser spindle appear where it lives |
| Cube driver blind to "solved during prerun" | A decided cell reported UNKNOWN (fail-safe direction) | Positive-control rung |
| $\chi\ge5$ negatives from an uncalibrated ladder | "No field reaches $\chi\ge5$" as if it meant something | Calibration against de Grey's graph, which must be findable and was not |

The last one is the important one. The system had produced a *correct-looking
negative result* across eight number fields. The gate that would license it (find
$\chi=5$ where it provably exists) failed, which downgraded the negative from
"evidence about fields" to "evidence about my generator set". No amount of
additional compute would have revealed that; only the gate did.

**Design consequence:** a result that has not passed a gate is not a weak result,
it is not a result. The platform enforces this mechanically rather than relying on
the discipline of whoever is driving.

## The five invariants

Everything in `experiments/` is expected to satisfy these. They are the platform.

### 1. Calibrate before trusting, in both directions

A tool is not trusted until it reproduces known answers, and the ladder must
include cases where the tool must say YES and cases where it must say NO. A
one-directional gate passes trivially for a tool that always answers the same way.

Concretely, the $\Sigma_2$ decision procedure is calibrated at every chromatic
threshold it can be asked about: $k=4$ against Groetzsch (an external uniqueness
theorem, so the returned model must BE the Groetzsch graph), $k=5$ against
Jensen-Royle, $k=6$ against $C_5 + K_3$. It reproduces the repo's own $n=15$ and
$n=16$ verdicts by a third independent route before it is allowed to speak about
$n=17$.

### 2. Non-vacuity: an unsatisfiable answer on an empty problem is not evidence

An UNSAT is meaningful only if the thing being searched could have existed. Every
cell that comes back UNSAT is re-run at a weaker threshold where it MUST be
satisfiable, and the witness must be certified a genuine member by code disjoint
from the solver that produced it. A cell that fails this is downgraded, never
counted.

This is the guard that distinguishes "no such graph exists" from "I asked a
question with no possible answers".

### 3. Positive controls: prove the search can succeed before trusting it to fail

For every negative result, run the same machinery on a nearby problem where a
positive answer is known to exist. If the search cannot find what is there, its
failure to find anything elsewhere means nothing.

This is what the ablation ladder does: strip the class constraints, and the
pipeline must return SAT in the same $n$ / degree / edge-count regime. It is also
what killed the ring census's $\chi\ge5$ claims.

### 4. Structural firewalls: control objects that must never break

The program carries three control objects with known answers that any correct
method must respect: $\chi(\mathbb{Q}^2)=2$, $\chi(L^\infty \text{ on } \mathbb{R}^2)=4$,
$\chi(\mathbb{R}^1)=2$. A technique that "proves" something about $\mathbb{R}^2$
while also proving it about $\mathbb{Q}^2$ is structurally wrong, and the firewall
(`experiments/lemma_db/`) fails the build if such a lemma ever lands on a
load-bearing path.

Every new search runs its control first. The ring census runs $\mathbb{Q}^2$ as
rung one, before any positive claim about any other field.

### 5. Independent re-verification of every positive

A model returned by a solver is re-checked by different code before it is called a
result: class membership by a separately written filter, the colouring half by the
repo's SAT portfolio. A propagator bug cannot manufacture a hit.

## Architecture

Five layers, deliberately separated so that the expensive layer is the thin one.

```
  interface     status.sh                    one screen; the only thing a human reads
       |
  signal        STOP file                    written ONLY when a decision is needed
       |                                     (HIT / WALL / GATE)
  queue         autorun.sh                   cron + flock; model-free forever
       |
  gates         calibrate / probe / ablate   refuse to run uncalibrated
       |
  compute       e17..e25, smsg, geng, SAT    exact arithmetic, no model in the loop
```

**The economics are the point.** The compute layer runs for days at zero token
cost. A language model is invoked only when the signal layer says a decision is
needed. The interface layer exists so that when a model IS invoked, it spends a few
hundred tokens getting oriented instead of tens of thousands re-reading ledgers.

### Signal semantics

The queue halts on exactly three conditions, each writing `STOP` with a written
reason:

- **HIT** — the object being searched for was found and independently verified.
  This is the result the program exists for; it must never be buried in a log.
- **WALL** — a step could not be closed by any available method. The distinction
  from HIT matters: a wall is a fact about our tools, not about mathematics.
- **GATE** — a calibration failed. Nothing downstream is trustworthy, so the queue
  stops rather than accumulating untrustworthy answers.

**No STOP file means there is nothing for a human to do.** That is the entire
contract, and it is what makes the loop genuinely hands-off.

### Resumability

Every unit of work caches its verdict, so a kill, a reboot, or a power cut costs
only the in-flight unit. `@reboot` cron restarts the queue; `flock` keeps it
single-instance; orphaned solvers (whose parent died) are reaped at the top of each
run, because holding the lock proves no legitimate run is in flight.

## Adding an experiment

The checklist that makes a new module part of the platform rather than a script
beside it:

1. **State the question so that both answers are informative.** "Does X exist at
   $n$?" is good. "Search for X" is not: it has no failure condition.
2. **Write the calibration ladder before the experiment.** At least one rung where
   the answer must be YES and one where it must be NO, against answers established
   outside this repo where possible.
3. **Name the control object** the method must respect, and run it first.
4. **Add a non-vacuity probe** for every negative the experiment can produce.
5. **Re-verify positives with disjoint code.**
6. **Compute parameters, never type them.** Windows, bounds and thresholds derived
   from a formula that is asserted against a known case. (The $n=19$ defect above
   was a typed window.)
7. **Make the verdict a file**, so the queue can resume and `status.sh` can read it.
8. **Record the honest scope** in the module docstring: what the result does NOT
   establish. The docstring is where a future session learns what it may cite.

## Landscape: what already exists, and where this differs

The autonomous-mathematics field in 2026 has three broad families. This platform
is deliberately in none of them, and the distinction is worth stating precisely.

### Family 1: formal proof search (LLM proposes, Lean verifies)

DeepMind's **AlphaProof Nexus** pairs frontier LLMs with the Lean proof assistant,
whose compiler mechanically checks every step. Its subagents run "Ralph loops":
multi-turn inference episodes that refine a proof sketch, recompile it in Lean, and
feed the compiler's error message into the next turn. The full agent adds an
evolutionary population of proof sketches with Elo-style ranking, plus AlphaProof
as a callable tool on subgoals. Reported results include 9 of 353 open Erdos
problems (two open for 56 years) at a few hundred dollars per problem, 44 of 492
OEIS conjectures, and a 15-year-old question in algebraic geometry.
[[paper](https://arxiv.org/abs/2605.22763)]
[[coverage](https://the-decoder.com/google-deepminds-alphaproof-nexus-solves-decades-old-math-problems-for-a-few-hundred-dollars/)]

Related: **Numina-Lean-Agent** orchestrates natural-language proving with Lean
verification via Claude Code; **Rethlas & Archon** splits the work into a
natural-language planner and a Lean compiler-filler.

**How ASSAY differs.** Lean gives these systems *soundness for free*: a proof that
compiles is correct, so the entire epistemic burden collapses onto the kernel. Our
results are not Lean-checkable, and (L80) provably not even DRAT/LRAT-checkable,
because the object being refuted is not a propositional formula: $\Phi$ is
satisfiable, and what is unsatisfiable is $\Phi$ plus a semantic side condition.
When the kernel cannot carry the burden, the gates must. That is the whole reason
this platform's invariants are heavier than a Lean-based system's need to be.

### Family 2: LLM-guided evolutionary program search

**FunSearch** evolves a Python function that constructs a solution, scored by a
deterministic evaluator; **AlphaEvolve** generalizes it to arbitrary mutable code
blocks. **PatternBoost** alternates local search with a transformer trained on good
constructions. These have produced human-competitive results in extremal
combinatorics (cap sets, admissible tuples, no-isosceles sets). Open-source
descendants include **CodeEvolve** and **ImprovEvolve**.
[[FunSearch overview](https://www.emergentmind.com/topics/funsearch-algorithm)]
[[CodeEvolve](https://arxiv.org/html/2510.14150)]

**How ASSAY differs.** These are *constructive*: they find objects, and an object
is self-verifying (you check the construction). They cannot produce a nonexistence
result, which is what most of this program's questions are. Our gradient thread
(L73/L74) is the closest analogue and hit exactly that ceiling: continuous search
can represent, preserve and grow a hard core but cannot manufacture $\chi\ge5$,
because the objective is one-sided. A nonexistence claim needs a decision
procedure and an epistemic story, which is the gap this platform fills.

### Family 3: agentic research assistants

**MathCoPilot** and similar systems target human-AI symbiosis in the research
workflow: literature retrieval, planning, drafting.
[[MathCoPilot](https://arxiv.org/html/2607.14582v1)]
[[agentic researcher guide](https://arxiv.org/pdf/2603.15914)]

**How ASSAY differs.** Those keep a human in the loop by design. This keeps the
human OUT of the loop by design, and spends its engineering on the signal that
tells you when to come back.

### The honest positioning

ASSAY is not more capable than any of the above. It is narrower and more paranoid.
Its contribution is the epistemic layer: **calibration ladders, non-vacuity probes,
positive controls, structural firewalls and downgrade-on-doubt semantics, applied
to computational results that no proof assistant can currently certify.** The
measured justification is the table at the top of this document.

The natural convergence: a system in Family 1 that adopted these invariants would
be able to trust its *unformalizable* computational steps, which is currently the
weakest link when a Lean proof depends on a SAT certificate or an exhaustive
search. That is the interesting direction, and it is where this platform should go
if it grows beyond one problem.

## Known limitations

Stated because a platform document that lists only strengths is itself a failure of
the thesis.

- **Cube completeness is assumed.** The cube-and-conquer path rests on SMS's cubes
  partitioning the space. Evidence is one agreement with a whole-cell answer plus a
  positive control. If cubes ever failed to partition, an UNSAT would be wrong and
  no current gate would catch it. This is the deepest unguarded assumption.
- **Gates test the tool, not the mathematics.** A calibration ladder can only
  demand known answers; it cannot detect an error in a reduction lemma that is
  wrong in a way no known case exercises.
- **The counting lemmas are not machine-verified.** They are formalization-ready
  double-counting arguments, and Lean-proving them is the obvious hardening.
- **No cost model.** The queue does not estimate whether a step is feasible before
  starting it, which is why $n=18$ burned hours in a diverging split before a human
  noticed. A predicted-cost gate belongs in the queue.
- **One problem domain.** Every invariant here was derived from Hadwiger-Nelson
  work. They are stated generally, but they have been tested in one place.

## Files

| path | role |
|------|------|
| `experiments/combinatorial/autorun.sh` | the queue: cron, flock, orphan reaping, STOP semantics |
| `status.sh` | the interface: one screen of state |
| `experiments/_shared/smoke_test.py` | control-object gate (Moser=4, $\mathbb{Q}^2$=2, $L^\infty$=4, $\mathbb{R}^1$=2) |
| `experiments/lemma_db/build_db.py` | structural firewall over the proof-dependency DAG |
| `experiments/combinatorial/e20_sigma2.py` | the $\Sigma_2$ decision procedure and its ladder |
| `experiments/combinatorial/e25_cube.py` | cube-and-conquer, with the fail-safe verdict rules |
| `experiments/PHASE_STATE.md` | resumable operational state |
| `experiments/LEARNINGS.md` | permanent numbered findings log |
| `experiments/PUBLICATIONS.md` | publication triage and the circularity gate |
