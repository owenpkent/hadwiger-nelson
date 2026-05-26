# The measurable chromatic number $\chi_m(\mathbb{R}^2)$

A refinement of the Hadwiger-Nelson chromatic number that requires the color classes to be measurable (in the Lebesgue sense). Sometimes substantially easier to bound from below than $\chi(\mathbb{R}^2)$ itself, because measure-theoretic tools open up.

## Definition

A **measurable $k$-coloring** of $\mathbb{R}^2$ is a partition $\mathbb{R}^2 = A_1 \cup A_2 \cup \cdots \cup A_k$ where each $A_i$ is Lebesgue-measurable and no $A_i$ contains two points at Euclidean distance exactly $1$.

The **measurable chromatic number** is

$$
\chi_m(\mathbb{R}^2) := \min \{ k : \text{a measurable } k\text{-coloring exists} \}.
$$

It is immediate that $\chi(\mathbb{R}^2) \leq \chi_m(\mathbb{R}^2)$. The chromatic number is the unrestricted minimum over all partitions, and measurable colorings form a strict subset of admissible partitions.

The variant $\chi_B(\mathbb{R}^2)$ requires Borel color classes, sitting strictly between $\chi$ and $\chi_m$:

$$
\chi(\mathbb{R}^2) \leq \chi_B(\mathbb{R}^2) \leq \chi_m(\mathbb{R}^2).
$$

## Why measurability is a strong restriction

The set $\mathbb{R}^2$ has plenty of "pathological" partitions (using the axiom of choice). Shelah-Soifer (2003) show that in ZF + DC (without full choice), $\chi(\mathbb{R}^2)$ can take values not realized in ZFC. Measurability cuts out the AC-dependent constructions and forces structurally honest colorings.

In practice, every "natural" construction (the hexagonal tiling giving $\chi \leq 7$, the Polymath16 sets giving $\chi \geq 5$) lives in the measurable world. So $\chi_m$ is the chromatic number of *constructible* colorings.

## Falconer's theorem (1981): $\chi_m(\mathbb{R}^2) \geq 5$

**Statement**: every measurable partition of $\mathbb{R}^2$ into $\leq 4$ unit-distance-avoiding sets is impossible.

**Proof sketch**. Suppose $\mathbb{R}^2 = A_1 \cup A_2 \cup A_3 \cup A_4$ is a measurable 4-coloring. By translation-invariance of Lebesgue measure and the partition condition, the lower density of each $A_i$ is $\frac{1}{4}$ (additivity over translations).

Let $f_i$ be the indicator function of $A_i$. The **autocorrelation** of $f_i$ is

$$
(f_i \star \tilde{f}_i)(t) := \int_{\mathbb{R}^2} f_i(x) f_i(x + t)\, dx
$$

(in the appropriate density / Cesaro sense). Since $A_i$ avoids distance 1, $(f_i \star \tilde{f}_i)(t) = 0$ whenever $\lVert t \rVert = 1$.

Sum the four autocorrelations. Since $\sum_i f_i \equiv 1$,

$$
\sum_i (f_i \star \tilde{f}_i)(t) = 1 \quad \text{for almost every } t.
$$

In particular, for $\lVert t \rVert = 1$ this gives $0 = 1$, a contradiction. Done.

(The above is a textbook sketch. The actual proof requires care with the density formulation, in particular replacing the integrals with their Cesaro averages over balls of growing radius; see Soifer Ch. 9.)

Falconer's original published proof (J. Combin. Theory A 31, 1981) goes through an *autocorrelation-on-the-Fourier-side* refinement that is robust to the density issues. Bukh has expository notes that streamline the argument.

## The push to $\chi_m \geq 6$ (recent)

Improvements after Falconer used:
- Spherical harmonic decompositions of the autocorrelation.
- Higher-order density bounds via the Selberg sieve adapted to $\mathbb{R}^2$.
- Connections to fractional chromatic numbers and Lovász $\vartheta$.

The bound $\chi_m \geq 6$ is recent. Anchors and exact references will be filled in by the Architecture 2 SURVEYOR dossier (forthcoming as [`arch2_measurable_lineage.md`](../research_atlas/arch2_measurable_lineage.md)).

## Why $\chi_m$ can differ from $\chi$ (in principle)

Without measurability, an AC-dependent partition can route distance-1 pairs into different color classes using pathological non-measurable witnesses. Shelah-Soifer show this is not vacuous: under ZF + DC, $\chi(\mathbb{R}^2)$ can exceed the measurable value, or alternatively the (measurable) value can exceed the unrestricted infimum, depending on which model of set theory is chosen.

In ZFC (Lebesgue measure exists; "most" sets are measurable in some informal sense), the gap $\chi_m - \chi$ is widely believed to be small or zero, but this is unproven.

## Wrong-approach detectors for Architecture 2

Architecture 2 is partly exempt from the $\mathbb{Q}^2$ detector ($\chi(\mathbb{Q}^2) = 2$ by Woodall), because $\mathbb{Q}^2$ has Lebesgue measure zero and measure-theoretic arguments degenerate there.

But Architecture 2 must engage with the $\mathbb{R}^1$ detector ($\chi(\mathbb{R}) = 2$ trivially). A measure-theoretic argument that gives $\chi_m \geq 5$ but works identically on $\mathbb{R}^1$ is structurally wrong: $\mathbb{R}^1$ has $\chi = 2$ by the floor-mod-2 coloring, and any measurable argument that constrains $\chi_m(\mathbb{R})$ to 5 contradicts this. Falconer's proof uses the 2D rotation group $O(2)$ essentially (the autocorrelation vanishes on the full unit *circle* of translates, not just on one direction); this is what saves it from over-applying to $\mathbb{R}^1$.

The $L^\infty$ detector ($\chi = 4$, Chilakamarri) is also informative. A measurable argument that ignores the specifically Euclidean inner product structure (using only an abstract normed-plane setup) would have to fail on $L^\infty$. Falconer's autocorrelation is rotation-equivariant in the Euclidean sense; this distinguishes it from norm-blind arguments.

## What's tractable computationally

Several things in the Architecture 2 spirit:

- **Numerical Falconer obstruction**: discretize a $[0, L]^2$ window on a fine grid, take indicator functions of candidate 4-coloring sets, compute the autocorrelation via FFT, verify the obstruction empirically. This is a finite-precision shadow of Falconer; it does not prove anything but illustrates the obstruction at scale.
- **Spectral bound on finite UDGs**: the smallest eigenvalue of the adjacency matrix of a UDG, when normalized, gives a lower bound related to the Cayley-graph $\vartheta$ value on $\mathbb{R}^2$. This connects Architecture 2 to Architecture 3.
- **Reproduction of recent $\chi_m \geq 6$ machinery**: implement the spherical-harmonic decomposition used in the modern proofs and verify the obstruction at small parameters.

These will be detailed in the SURVEYOR dossier and tracked as `e2X` experiments under [`experiments/measurable/`](../../experiments/measurable/).

## References

- K.J. Falconer, *The realization of distances in measurable subsets covering $\mathbb{R}^n$*, J. Combin. Theory A 31 (1981).
- A. Soifer, *The Mathematical Coloring Book*, Springer (2009), chapter 9 (measurable chromatic number).
- S. Shelah and A. Soifer, *Axiom of choice and chromatic number of the plane*, J. Combin. Theory A 103 (2003).
- B. Bukh, expository notes on Falconer's theorem (linked from CMU homepage).
- (Recent $\chi_m \geq 6$ references: filled in by Architecture 2 surveyor.)
