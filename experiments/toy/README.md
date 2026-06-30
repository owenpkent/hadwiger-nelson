# The HN toy sandbox

A checkable training ground for chi-lower-bound techniques. The Hadwiger-Nelson
analog of the zeta repo's function-field toy; see
[`../ZETA_INNOVATION_TRANSFER.md`](../ZETA_INNOVATION_TRANSFER.md).

In the zeta repo, curves over a finite field are the toy world where the Riemann
Hypothesis is a **theorem** (Weil), so a proposed proof-move can be graded right or
wrong. Here the analog is simpler and sharper: the chromatic number of a finite
graph is **decidable** by SAT, so it is the answer key. A proposed lower-bound
TECHNIQUE can be graded against a battery of known-chi graphs, and a soft, circular,
or control-blind technique is caught on contact.

```powershell
python -m experiments.toy.play          # grade the reference + two bad candidates
python -m experiments.toy.test_toy      # the smoke test
```

## Why it helps

Architecture 1 (finite UDG) has a cheap gradient already: chi is SAT-decidable, so
a candidate graph is scored instantly. The binding constraint there is W3
(realizability), not chi. But Architectures 2, 3, and 4 propose lower-bound
TECHNIQUES (spectral, topological, measure-theoretic) whose soundness and
non-circularity are NOT obvious and whose lift is expensive. This sandbox is where
you vet such a technique before investing:

1. **Reproduce the known answer.** A technique must reach chi>=6 where chi>=6 is
   real (the SAT answer key), and must not over-claim it where chi<6.
2. **Survive the firewall.** The three controls (Q^2 chi=2, L^infty chi=4, R^1
   chi=2) are graded instances. A technique that paints a control above its true chi
   is structurally wrong, the analog of a Davenport-Heilbronn-blind argument.
3. **Stay clean.** A candidate only ever receives the abstract graph (n, edges),
   never the answer key, so it cannot read chi off the instance.

## The battery (`instances.py`)

| Tier | Instance | chi | why it is here |
|------|----------|-----|----------------|
| positive | K6 | 6 | trivial chi>=6 (a clique bound gets it free) |
| positive | K7 | 7 | a second clear target |
| positive | M^3(C5) | 6 | **the hard positive: chi=6 with omega=2**, the clamp-route regime |
| sub-6 | C5 | 3 | a small odd cycle |
| sub-6 | Moser spindle | 4 | a real UDG at chi=4 |
| sub-6 | M^2(C5) | 5 | **the fake: chi exactly 5**, a technique that calls it >=6 is wrong |
| control | Q^2 sample | 2 | rational plane is bipartite (Woodall) |
| control | L^infty king-grid | 4 | chi=4 exactly (Chilakamarri) |
| control | R^1 chain | 2 | blind to the rotation group O(2) |

The answer key (`known_chi`) is hidden from candidates and verified against SAT in
`test_toy.py`. The controls reuse `experiments/_shared/wrong_approach_detectors.py`,
so the toy and the [`smoke_test`](../_shared/smoke_test.py) gate stay consistent.

## Writing a candidate (`grader.py`)

```python
from experiments.toy import grade, ToyData

def my_candidate(data: ToyData) -> int | None:
    # build a LOWER BOUND on chi from data.n and data.edges only.
    # return None if your technique is uninstantiable on this graph.
    ...

print(grade(my_candidate, "my candidate").report())
```

The grader scores four flags; all green is the bar:

| check | meaning |
|-------|---------|
| `reproduces_target` | bound >= 6 on every known chi>=6 instance |
| `rejects_fakes` | bound < 6 on every known chi<6 instance |
| `control_immune` | bound <= known chi on every control (the firewall) |
| `k1_clean` | structural: the candidate only saw (n, edges), never the answer |

The **reference** (`sat_lower_bound`) returns exact chi by SAT and scores all green:
it is the known-correct technique in the toy. Two demonstration bad candidates show
the grader has teeth: `clique_lower_bound` (omega) fails `reproduces_target` because
omega <= 3 in the unit-distance / triangle-free regime (it cannot see chi=6 on
M^3(C5)); `max_degree_plus_one` fails `control_immune` because it paints the L^infty
king-grid 9 where chi=4.

## The honest caveat

The toy grades the **technique**, it cannot contain the **obstruction**. chi is
decidable here only because the graphs are finite; the real wall is W3, the
unit-distance realizability of a chi>=6 host in R^2 (Groebner-walled past ~14
vertices). A green scorecard means "sound and control-clean on finite graphs," NOT
"lifts to a planar UDG." The delta between green-here and an actual embedding is the
compass, not the proof. This mirrors the zeta toy's caveat exactly: there the
finite, single-circle Frobenius spectrum cannot contain zeta's accumulating one.
