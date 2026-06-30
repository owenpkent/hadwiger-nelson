# State of the program

A one-page strategic snapshot. This is **rewritten, not appended** (unlike
[`experiments/PHASE_STATE.md`](experiments/PHASE_STATE.md), which stacks dated
blocks). Read this to re-orient on the whole program in one pass; read PHASE_STATE
for the operational edge.

## Thesis

The program bottoms out at **one missing object**: a unit-distance-realizable
flexible color-clamp, equivalently a $\chi=6$ UDG that embeds in the Euclidean
plane. The abstract object exists (a 48-vertex triangle-free SAT witness, L51-L53);
all difficulty is **W3**, its realizability in $\mathbb{R}^2$, which Theorem R
reduces to a cocircularity-with-distinct-centers condition. Every architecture
that is still alive routes through, or around, this single object. Backward-from-2050
calibration (L54) puts the program's probability mass on $\chi(\mathbb{R}^2)=6$ via
a finite UDG.

## The board

Known bounds: $5 \le \chi(\mathbb{R}^2) \le 7$ (de Grey 2018 lower; Isbell hex upper).

| Architecture | The wall | Live? |
|--------------|----------|-------|
| 1. Combinatorial / UDG | W3: realize the clamp. The host must be K4-free 6-critical, K_{2,3}-free (codegree wall L63), and outside the P510 lineage (forcing-sterility L57). | **Yes** - the main bet. Route ii: a wide imprimitive interface. |
| 2. Measurable / spectral | order-2 SDP at $X_{23}$ is FEASIBLE, so it cannot reach $\chi_m \ge 6$ (L72). | Closed at order-2. Only SE(2)-noncommutative survives. |
| 3. Fractional / Lovász $\vartheta$ | spectral bounds plateau at the classical line at runnable scale. | Stalled, no live increment. |
| 4. Set-theoretic / Borel | needs a local finite-UDG statement forcing $\chi_B \ge 6$ via the rotation group. | Dark horse. |

## The wall, as a sanity reflex (the three controls)

Every lower-bound argument must distinguish $\mathbb{R}^2$ from all three control
objects, or it is structurally wrong. These are enforced, not advisory:
`experiments/_shared/smoke_test.py` colors them on every run, and
`experiments/lemma_db/` fails CI if a control-blind node becomes load-bearing.

- $\mathbb{Q}^2$: $\chi = 2$ (Woodall). Combinatorial content must use density/topology of $\mathbb{R}$.
- $L^\infty$ plane: $\chi = 4$ (Chilakamarri). Geometric content must use Euclidean rigidity.
- $\mathbb{R}^1$: $\chi = 2$. Measure-theoretic content must use the rotation group $O(2)$.

## Honest odds

Sub-1% that this program resolves the conjecture. The realistic outputs are the
two structural notes already in the pipeline (C1 forcing-sterility + codegree;
C3 the symmetry-broken self-certifying solver), not a new bound. The value is a
clean, self-auditing map of exactly where every route is stuck.

## The single most-leveraged next move

**Build a new $\chi=5$ UDG outside the P510 lineage that carries a wide imprimitive
boundary interface** (route ii, L55-L56), and feed it to the existing forced-pair
SAT test. Forcing-sterility (L57) proves the missing object cannot come from the
known lineage, so a fresh construction principle is the prerequisite for everything
downstream. Run `python -m experiments.lemma_db.build_db --frontier` to see this
and the other attackable nodes.

---
Pinned state (commit, finding number, gates, papers): see the **Last verified state**
block at the bottom of [`experiments/PHASE_STATE.md`](experiments/PHASE_STATE.md).
