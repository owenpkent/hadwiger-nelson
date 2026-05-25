# The Moser spindle: $\chi(\mathbb{R}^2) \geq 4$

A finite 7-vertex unit-distance graph that cannot be 3-colored. Constructed by William and Leo Moser in 1961. The first nontrivial lower bound for the chromatic number of the plane; held for 57 years until de Grey (2018) replaced it with $\chi \geq 5$.

## What we want to prove

There is a finite set $V \subset \mathbb{R}^2$ and a set of unit-distance pairs $E \subset \binom{V}{2}$ such that the graph $(V, E)$ has chromatic number exactly $4$. Since every unit-distance pair in any $V \subset \mathbb{R}^2$ must receive different colors in a valid coloring of the plane, this immediately gives $\chi(\mathbb{R}^2) \geq 4$.

## The construction

Start with a **unit rhombus**: two equilateral triangles glued along a common edge. Place

$$
A = (0, 0), \quad B = (1, 0), \quad C = \left(\tfrac{1}{2}, \tfrac{\sqrt{3}}{2}\right), \quad D = \left(\tfrac{3}{2}, \tfrac{\sqrt{3}}{2}\right).
$$

The five pairs at distance exactly $1$ are $AB$, $AC$, $BC$, $BD$, $CD$. The diagonal $AD$ has length $\sqrt{3}$ (not a unit edge). So this 4-vertex graph is two triangles $ABC$ and $BCD$ glued along edge $BC$.

Now rotate this rhombus about $A$ by an angle $\theta$ to get a second copy with vertices $A, B', C', D'$. Choose $\theta$ so that $D$ and $D'$ are exactly at unit distance.

The squared distance between $D$ and its rotated image is

$$
\lVert D - D' \rVert^2 = 2 \lVert D \rVert^2 \left(1 - \cos \theta\right) = 6 (1 - \cos \theta),
$$

since $\lVert D \rVert = \sqrt{3}$. Setting this equal to $1$ gives $\cos \theta = \tfrac{5}{6}$, so

$$
\theta = \arccos\left(\tfrac{5}{6}\right).
$$

The resulting 7 vertices are $A, B, C, D, B', C', D'$, and the 11 unit-distance pairs are

$$
\{AB, AC, BC, BD, CD,\ AB', AC', B'C', B'D', C'D',\ DD'\}.
$$

(Five edges in each rhombus, plus the connecting edge $DD'$.)

This matches the smoke-test output: 7 vertices, 11 edges. See [`experiments/_shared/unit_distance_graph.py:moser_spindle`](../../experiments/_shared/unit_distance_graph.py).

## Why $\chi \geq 4$

We show no 3-coloring exists. Suppose toward contradiction that $\varphi : \{A, B, C, D, B', C', D'\} \to \{1, 2, 3\}$ assigns different colors to every unit-distance pair.

**Step 1: in the first rhombus, $\varphi(A) = \varphi(D)$.**

The four vertices $A, B, C, D$ contain two triangles $ABC$ and $BCD$, each requiring three distinct colors. WLOG $\varphi(B) = 1, \varphi(C) = 2$. The triangle $ABC$ forces $\varphi(A) = 3$ (the only color left). The triangle $BCD$ forces $\varphi(D) = 3$ (same reason). So $\varphi(A) = \varphi(D)$.

**Step 2: same in the second rhombus: $\varphi(A) = \varphi(D')$.**

By the identical argument applied to vertices $A, B', C', D'$.

**Step 3: contradiction.**

From steps 1 and 2, $\varphi(D) = \varphi(D')$. But $DD'$ is a unit-distance edge, so they must have different colors. Contradiction.

Therefore $\chi(\text{Moser spindle}) \geq 4$.

## Why $\chi \leq 4$

Exhibit a 4-coloring. One works as follows: assign $\varphi(A) = 1$, $\varphi(B) = 2$, $\varphi(C) = 3$, $\varphi(D) = 4$, $\varphi(B') = 3$, $\varphi(C') = 4$, $\varphi(D') = 2$. Check every unit-distance edge by hand (or by SAT).

## Why this bound stalled at $4$ for 57 years

Every natural variant of the spindle (adding more rhombi, more rotations) still admits a 4-coloring for small vertex counts. The minimum number of vertices required to *force* $\chi \geq 5$ is at least in the hundreds. De Grey's 2018 graph has $1581$ vertices, and Polymath16 reduced it to around $510$.

The Moser spindle illustrates the architecture but does not scale: composing more spindles makes the graph 4-colorable again because the rotational obstruction is not "rigid enough". The de Grey graph adds higher-order algebraic constraints in the same number field.

## Wrong-approach check

The Moser spindle proof uses the equilateral triangle (a unit-distance subgraph that requires 3 colors). In $\mathbb{Q}^2$, no equilateral triangle exists at all (because $\sqrt{3} \notin \mathbb{Q}$, the vertex $C = (1/2, \sqrt{3}/2)$ is not rational). So the proof technique correctly fails on the $\mathbb{Q}^2$ control: $\chi(\mathbb{Q}^2) = 2$, and the spindle construction has nothing to say there. Good.

In the $L^\infty$ metric on $\mathbb{R}^2$, the analog of the equilateral triangle exists but the spindle's rotation argument breaks (rotation is not an $L^\infty$ isometry). The proof again does not over-shoot. Good.

## Reproduce in code

```powershell
python -m experiments._shared.smoke_test
```

The first two checks confirm 7 vertices and 11 edges. To verify $\chi = 4$ via SAT:

```python
from experiments._shared.unit_distance_graph import moser_spindle
g = moser_spindle()
chi, coloring = g.chromatic_number_sat(k_max=7)
print(chi, coloring)  # expect: 4, [color list]
```

This is the content of the planned `experiments/combinatorial/e1a_moser_spindle.py`.

## Formal verification

The Lean target is `HadwigerNelson.MoserSpindle.MoserSpindleIsFourChromatic`. The proof reduces to two decidable claims on a finite graph (4-colorability and non-3-colorability). See [`lean/HadwigerNelson/MoserSpindle.lean`](../../lean/HadwigerNelson/MoserSpindle.lean).

## References

- L. Moser and W. Moser, *Solution to Problem 10*, Canadian Math. Bull. 4 (1961), 187-189.
- A. Soifer, *The Mathematical Coloring Book*, Springer (2009), chapter 2.
- [`docs/research_atlas/README.md`](../research_atlas/README.md): atlas entry.
