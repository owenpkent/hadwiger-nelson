# Gradient-descent attack surface

Continuous / gradient-based methods for the Hadwiger-Nelson program. This thread
answers one question: **where can gradient descent actually bite on $\chi(\mathbb{R}^2)$,
and where does it only pretend to?**

## The one hard constraint

$\chi$ is integer-valued and a coloring is discrete, so there is **no** global
differentiable objective whose minimum *is* $\chi(\mathbb{R}^2)$. Gradient descent is a
**local, one-sided** method:

- it can witness **existence** (a coloring $\Rightarrow$ $k$-colorable; an embedding
  $\Rightarrow$ realizable), so it produces **upper bounds** and **constructions**;
- it can **never** witness non-existence. A $\chi \ge 6$ claim (the thing HN needs)
  requires a **certificate**: a SAT UNSAT core or a dual SDP solution.

So GD lives in exactly two legitimate places: the **construction / search** side (the
geometry of $\mathbb{R}^2$ is continuous, so the search space is genuinely smooth) and
the **convex-dual** side (where the dual optimum is itself the certificate). Anything
that claims GD bounds $\chi(\mathbb{R}^2)$ from below without one of those certificates
is over-promising. Every script here routes its hard claim back through the SAT
[`lemma_db`](../lemma_db/) firewall or an exact computation.

## Wrong-approach-detector compliance

A pure **soft-coloring** objective (penalize monochromatic edges of a *fixed*
adjacency) is blind to the topology of $\mathbb{R}$: it lifts unchanged to
$\mathbb{Q}^2$, where $\chi = 2$ (Woodall). It therefore cannot prove anything
$\mathbb{R}^2$-specific on its own. The **coordinate** terms
(`edge_residual_loss`, `nonedge_margin_loss`, `soft_adjacency`) are what ground an
objective in the Euclidean plane: chromatic pressure only appears where points sit at
genuine unit distance. Option A is built around this; a version that maximized hardness
of an abstract adjacency alone would be structurally wrong, and is excluded by design.

## Shared core: [`diff_udg.py`](diff_udg.py)

torch (float64) primitives every option builds on:

| primitive | what it is |
|-----------|------------|
| `edge_residual_loss` | mean $(\lvert p_i-p_j\rvert^2-1)^2$ over edges that should be unit |
| `nonedge_margin_loss` | hinge keeping NON-edges off the unit circle (the term the legacy realizer omits) |
| `soft_adjacency` | $a_{ij}=\exp(-(d_{ij}-1)^2/2\tau^2)$: the graph as a smooth function of coordinates |
| `coloring_loss` | expected monochromatic-edge weight under a softmax coloring; $0 \Leftrightarrow$ properly colorable |
| `spread_penalty` | anti-collapse regularizer for the adversarial loop |
| `adam_minimize` | generic Adam driver |

Calibration graphs (`moser_spindle`, `triangular_lattice_patch`, `unit_triangle`) carry
a TRUE realization so every option can be checked against a known answer.

## The four options

### A. Adversarial coordinate $\leftrightarrow$ coloring co-optimization (flagship) -- [`adversarial.py`](adversarial.py)

The GD-native form of the live Arch-1 route. Solve

$$\max_{\text{coords}} \; \min_{\text{soft coloring}} \; \text{coloring\_loss}(\text{coords}, \text{coloring}).$$

The inner player finds the best soft $k$-coloring of the soft graph $a(\text{coords})$;
the outer player moves the vertex **positions** to make that best coloring as bad as
possible. A degree-budget term forces the outer player to actually BUILD a unit-distance
graph (without it the trivial optimum is "no edges"). Because the objective is driven by
real unit distances, it cannot lift to $\mathbb{Q}^2$.

- **Status: EXPERIMENTAL.** Calibrated and honest, not yet productive.
- **Validated:** the inner colorability oracle reproduces known $\chi$ exactly --
  unit triangle `loss@k=2 = 0.333` (one of three edges must be monochromatic), `@k=3 ~ 0`;
  $K_5$ `loss@k=4 = 0.1`, `@k=5 ~ 0`.
- **Honest negative:** naive alternating GDA from a random seed builds a real
  46-edge near-unit graph at the target density but only reaches $\chi=3$ -- it does
  **not** discover a hard-to-color UDG. Finding a $\chi\ge6$ UDG is the open problem
  itself; a single GDA run does not crack it.
- **Seeded from P510** ([`adversarial_p510.py`](adversarial_p510.py)): start at the
  real $\chi=5$ graph instead of random. Result: GDA does not push toward $\chi\ge6$.
  At a loose `tau` it relaxes density toward an easier 5-coloring; at a faithful `tau`
  it is gradient-starved and the colorability loss is flat. A structural caveat
  surfaced: P510 has hundreds of NON-edge pairs within ~0.014 of unit distance, so the
  global `soft_adjacency` cannot be made perfectly faithful to a dense real UDG without
  killing the gradient. Conclusion: Option A suits sparse / synthetic configs; dense
  real UDGs need a different edge model (optimize over the true edge set plus an
  explicit candidate-new-edge mechanism). The deformed graph is SAT-confirmed
  5-colorable (no prize).
- Run: `python -m experiments.gradient.adversarial` (random seed) or
  `python -m experiments.gradient.adversarial_p510` (P510 seed)

### B. The legal-UDG realizer (patched) -- [`realize.py`](realize.py)

Realize an abstract graph (e.g. a manufactured $K_4$-free 6-critical host) as a
unit-distance graph in $\mathbb{R}^2$: drive `edge_residual` to 0 **and** keep every
non-edge off the unit circle (`nonedge_margin`). The legacy realizer
([`combinatorial/realizability_w3_clamp.py`](../combinatorial/realizability_w3_clamp.py))
minimizes only the edge residual; a zero of that can still be an *illegal* drawing with
an accidental extra unit edge, which changes $\chi$. This is the fix.

- **Status: working, calibrated.** Moser spindle and a triangular-lattice patch come
  back as legal UDGs to machine precision (`max_edge_err ~ 1e-16`, healthy non-edge
  gap); $K_4$ (which needs $\mathbb{R}^3$) correctly fails to realize.
- **Applied to the L63 hosts** ([`realize_hosts.py`](realize_hosts.py)): every
  manufactured $K_4$-free 6-chromatic host (E13/E13b) FAILS to realize as a legal UDG
  (`max_edge_err ~ 0.5`) and is rigidity over-determined by +43 to +51 edges
  ($\lvert E\rvert - (2\lvert V\rvert-3) \gg 0$). This is the CONTINUOUS / rigidity
  corroboration of L63's codegree wall, fully independent of SAT: the geometry alone
  refuses these graphs. A host that DID realize legally would be a live $\chi\ge6$
  candidate; none does.
- Run: `python -m experiments.gradient.realize` (calibration) or
  `python -m experiments.gradient.realize_hosts` (the L63 hosts)

### C. First-order spectral push (spec, builds on the existing SDP thread)

Vector-chromatic number / Lovász $\vartheta$ is a low-rank (Burer-Monteiro) SDP: assign
unit vectors to vertices minimizing the max edge inner product, solved by **Riemannian
gradient descent on the sphere**. The *dual* optimum is a certificate, so this is the one
surface where GD yields a **lower** bound. For the plane this is the measurable / moment
SDP truncated to a Fourier / spherical-harmonic basis.

- **Status: spec'd, not re-implemented here** -- it reuses the
  [`fractional/`](../fractional/) machinery (e3a Lovász $\vartheta$, the order-2 moment
  solver e3u). L72 closed the order-2 *measurable* route at $X_{23}$; the open spectral
  lever is a first-order method on a richer basis or the noncommutative $SE(2)$ bound,
  pushing scale past the interior-point ceiling. Build it as an increment in
  `fractional/`, not a duplicate here.

### D. Flexible-but-color-rigid gadget search (the kill-test) -- [`gadget_search.py`](gadget_search.py)

[`rigidity_w3_escape.py`](../combinatorial/rigidity_w3_escape.py) names the single object
the UDG program may turn on: a gadget that is **geometrically flexible** (a 1-parameter
flex moves its two terminals, so the bridge distance is tunable, escaping the W3
over-determination) yet **color-rigid** (terminals clamped in every proper 5-coloring).
This makes both halves runnable and composable:

- **flex side** (linear algebra): terminal pair is flexible iff appending
  $\nabla\lvert p_s-p_t\rvert^2$ to the rigidity matrix raises its rank;
- **clamp side** (SAT): terminals are clamped at $k$ iff no proper $k$-coloring gives
  them the same / a free color (`same` / `diff` / `free`).

- **Status: working, calibrated.** Flexible clamps DO exist at low $k$ (a unit path
  forces a same-class pair SAME at $k=2$ and still flexes; rhombus likewise) but vanish
  far below $k=5$; the unit pentagon and Moser spindle have no flexible clamp at all.
  The kill-test asks for one that survives to $k=5$ -- that cell stays empty for every
  small gadget, reproducing the structural reality. GD enters by deforming a
  parametrized gadget while this SAT test scores the terminals, climbing the highest-$k$
  column toward 5.
- Run: `python -m experiments.gradient.gadget_search`

## What is and is not claimed

Built and calibrated: the differentiable core, the legal-UDG realizer (B), the gadget
kill-test (D), and the adversarial harness (A) with a validated colorability oracle. **No
bound moved.** The thread is infrastructure: it makes the continuous search surface
runnable and honest, with every hard claim routed back to SAT. The flagship's honest
negative (naive GDA does not reach $\chi>5$ from a random seed) is itself the finding that
points at the next levers.
