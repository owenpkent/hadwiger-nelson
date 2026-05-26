# The hexagonal upper bound: $\chi(\mathbb{R}^2) \leq 7$

Tile the plane with regular hexagons slightly smaller than unit diameter. Color them with $7$ colors in a periodic pattern so that any two hexagons sharing a color are separated by more than $1$. Then no two points at unit distance ever share a color. Attributed to John R. Isbell around $1950$. Has not been improved in $75$ years.

## What we want

A function $\varphi : \mathbb{R}^2 \to \{1, \dots, 7\}$ such that $\lVert x - y \rVert = 1 \implies \varphi(x) \neq \varphi(y)$. Existence of any such $\varphi$ gives $\chi(\mathbb{R}^2) \leq 7$.

## The construction

### Step 1: tile with regular hexagons

A regular hexagon with **circumradius** $R$ (center to vertex) has **inradius** $r = \tfrac{R\sqrt{3}}{2}$ (center to edge midpoint) and **long diameter** $2R$ (vertex to opposite vertex).

Tile the plane with congruent regular hexagons of circumradius $R$ in the standard honeycomb pattern. Their centers form a triangular lattice with nearest-neighbor distance $2r = R \sqrt{3}$.

To make tiles disjoint, use a half-open convention: assign each shared edge / vertex to one of the adjacent hexagons by a fixed tie-breaking rule.

### Step 2: $7$-color the hexagonal lattice

View the center lattice as the ring of Eisenstein integers $\mathbb{Z}[\omega]$, where $\omega = e^{i \pi / 3}$. The element $\alpha = 2 + \omega$ has norm

$$
\lVert 2 + \omega \rVert^2 = (2 + \tfrac{1}{2})^2 + (\tfrac{\sqrt{3}}{2})^2 = \tfrac{25}{4} + \tfrac{3}{4} = 7.
$$

The quotient $\mathbb{Z}[\omega] / (\alpha)$ has exactly $7$ elements. Color each hexagon by its center's residue class modulo $\alpha$. This gives a periodic $7$-coloring of the lattice.

Two centers of the same color differ by an element of the sub-lattice $\alpha \mathbb{Z}[\omega]$. The shortest nonzero element of this sub-lattice has norm $\sqrt{7}$ in $\mathbb{Z}[\omega]$ coordinates. Each unit of $\mathbb{Z}[\omega]$-norm corresponds to a center spacing of $2r = R\sqrt{3}$, so the same-color centers are at physical distance

$$
\sqrt{7} \cdot 2r = \sqrt{7} \cdot R\sqrt{3} = R\sqrt{21}.
$$

So **same-colored centers are at distance $\geq R\sqrt{21}$**.

### Step 3: pick $R$ to make the coloring work

Two constraints.

**Within a hexagon.** Any two points in the same closed hexagon are at distance at most $2R$ (the long diameter). For them to never be at distance exactly $1$ we need

$$
2R < 1, \quad \text{i.e.,} \quad R < \tfrac{1}{2}.
$$

**Between same-colored hexagons.** Any two points in distinct same-colored hexagons are at distance at least $(\text{center distance}) - 2R \geq R\sqrt{21} - 2R = R(\sqrt{21} - 2)$. For this to exceed $1$ we need

$$
R(\sqrt{21} - 2) > 1, \quad \text{i.e.,} \quad R > \tfrac{1}{\sqrt{21} - 2} \approx 0.387.
$$

Both conditions are satisfied for any $R \in (0.387, 0.5)$. The standard choice is $R$ slightly less than $\tfrac{1}{2}$. Concretely $R = 0.49$ gives diameter $0.98$ and minimum same-color separation $\approx 2.245$.

### Step 4: verify

Two points at unit distance are either (a) in the same hexagon, which is impossible since $1 > 2R$, or (b) in different hexagons. If those hexagons share the same color, the centers are at distance at least $R\sqrt{21} \approx 2.245$, so any two points across them are at distance more than $R\sqrt{21} - 2R \approx 1.265 > 1$. Contradiction.

So unit-distance points always land in differently colored hexagons. $\square$

## Why is this the best known upper bound

The hexagonal lattice is optimal for sphere packing in the plane. The $7$-coloring uses the smallest sub-lattice whose norm exceeds $4$ (so that the diameter-minus-diameter slack permits unit separation). The next-larger sub-lattice norms are $9, 12, 13, 16, \dots$; none gives a 6-coloring because the slack is too tight.

A $6$-color scheme using non-hexagonal tiles (squares, irregular polygons, fractals) is not ruled out by any known argument, but $75$ years of attempts have produced nothing. Pritikin (1998) showed that any $6$-coloring of $\mathbb{R}^2$ in the standard sense (color classes of bounded measurable type) must have a color class with relatively high "distance-$1$-realizing" potential, ruling out broad classes of attempts.

## Wrong-approach check

The construction relies on Euclidean rotational and translational structure (regular hexagons exist; the Eisenstein lattice is Euclidean-isometric to a sub-lattice of $\mathbb{R}^2$). It does not work in $\mathbb{Q}^2$: there are no regular hexagons with rational vertices (the construction uses $\sqrt{3}$). In the $L^\infty$ metric, hexagons become squares and the analog gives only a $4$-color upper bound, matching $\chi(L^\infty\text{-UDG}) = 4$ on $\mathbb{R}^2$. So the approach is not norm-blind: it correctly fails on the controls where $\chi$ is smaller.

## Open: can we do $6$?

This is the upper-bound side of the Hadwiger-Nelson gap. To improve $7 \to 6$ requires either:
- A non-hexagonal tile that closes the lattice norm gap (very unlikely; the geometry is essentially settled by the Eisenstein argument).
- A non-tile construction (color classes that are not bounded polygons but, say, fractal stripes or stratified measure-theoretic sets).
- A measurable construction with structure that bypasses the Pritikin-style obstructions.

The structural conjecture in the atlas is that $\chi(\mathbb{R}^2) = 7$ matches the upper bound and the $7 \to 6$ improvement is impossible. This is unproven.

## Formal verification

The Lean target is `HadwigerNelson.Basic.IsbellUpperBound : chromaticNumberOfPlane ≤ 7`. The proof requires:
- Defining the half-open hexagonal partition of $\mathbb{R}^2$.
- Defining the Eisenstein-lattice-mod-$(2+\omega)$ coloring.
- A measure-theoretic / case-analysis lemma showing unit-distance pairs cross color classes.

This is VERIFIER target HN-$3$ in [`lean/README.md`](../../lean/README.md).

## References

- J. R. Isbell, attributed by Soifer; the construction circulated in the early 1950s without a stand-alone publication.
- A. Soifer, *The Mathematical Coloring Book*, Springer (2009), chapter 2 and chapter 3.
- D. R. Pritikin, *All unit-distance graphs of order 6197 are 6-chromatic*, J. Combin. Theory B 73 (1998).
- [`docs/research_atlas/README.md`](../research_atlas/README.md): atlas entry under "upper bound".
