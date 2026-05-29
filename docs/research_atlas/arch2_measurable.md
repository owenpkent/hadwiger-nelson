# Architecture 2: measurable / spectral $\chi_m(\mathbb{R}^2)$, the spectral-SDP companion

This file is the **spectral-and-SDP focused companion** to the full Architecture 2
dossier [`arch2_measurable_lineage.md`](arch2_measurable_lineage.md). The lineage
dossier covers the chronology, Falconer's proof at the lemma level, the
"$\chi_m \geq 6$" misattribution audit, and the per-method wrong-approach analysis.
This companion adds three things the lineage dossier left open:

1. the explicit $k$-point SDP hierarchy (Oliveira Filho-Vallentin 2-point;
   de Laat-Machado-Oliveira-Vallentin / Bachoc et al. 3-point and higher),
2. the project's own experimental results e2a / e2b / e2c with their certificates,
3. a sharpened, honest verdict on the $\chi_m(\mathbb{R}^2) \geq 6$ frontier.

The headline, stated once and plainly: **$\chi_m(\mathbb{R}^2) \geq 5$ (Falconer
1981) is the best known measurable lower bound on the Euclidean plane, with no
improvement in 45 years. $\chi_m(\mathbb{R}^2) \geq 6$ is OPEN.** The widely-cited
"$\chi_m \geq 6$" results live in the hyperbolic plane (DeCorte-Golubev 2018) or
in strictly-stronger restricted-region models (convex-tile / map-type colorings),
not in the canonical measurable problem on $\mathbb{R}^2$.

---

## 1. The bridge object: $m_1(\mathbb{R}^2)$ and the density route

The modern measurable lineage runs through the **density of $1$-avoiding sets**:

$$
m_1(\mathbb{R}^2) := \sup\{\bar\delta(A) : A \subseteq \mathbb{R}^2 \text{ measurable, } \|x-y\| \neq 1 \ \forall x,y \in A\},
$$

where $\bar\delta$ is the upper density. The structural bridge is

$$
\chi_m(\mathbb{R}^2) \geq \frac{1}{m_1(\mathbb{R}^2)},
$$

because in any measurable $k$-coloring the largest color class is $1$-avoiding and
has density $\geq 1/k$, so $1/k \leq m_1$.

**The density route gives $\chi_m \geq 5$ only once $m_1 < 1/4 = 0.25$ is proven.**
This is a recent event:

| Bound on $m_1(\mathbb{R}^2)$ | $1/m_1$ | $\chi_m \geq$ | Source |
|---:|---:|:---:|---|
| $\leq 0.287119$ | $3.483$ | $4$ | OFV 2010 basic 2-point LP |
| $\leq 0.268412$ | $3.726$ | $4$ | OFV 2010, three off-center unit triangles |
| $\leq 0.2588$ | $3.864$ | $4$ | Keleti-Matolcsi-OFV-Ruzsa 2015 |
| $\leq 0.2544$ | $3.931$ | $4$ | Ambrus-Matolcsi 2022 |
| $\leq 0.2470$ | $4.049$ | $\mathbf{5}$ | Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 |

So the density route only crossed into $\chi_m \geq 5$ in 2023. **Falconer reached
$\chi_m \geq 5$ in 1981 by a different mechanism** (density + a rigid finite
configuration; see the lineage dossier section 3 and e2c below) that did not need
$m_1 < 1/4$. To force $\chi_m \geq 6$ via the density route one needs
$m_1(\mathbb{R}^2) < 1/5 = 0.2000$, far below the current $0.247$. **This is open.**

---

## 2. The $k$-point SDP hierarchy

The LP and SDP methods for $m_1(\mathbb{R}^n)$ form a Lasserre-style hierarchy
indexed by the number of points jointly constrained.

### 2-point (Oliveira Filho-Vallentin 2010, arXiv:0808.1822)

A radial positive-type function on $\mathbb{R}^2$ has the Hankel form
$F(r) = \int_0^\infty J_0(2\pi r s)\, d\nu(s)$ with $\nu \geq 0$, where $J_0$ is the
Bessel function of order $0$ (the $O(2)$-zonal / radial Fourier kernel
$\Omega_2(t) = J_0(t)$). The autocorrelation $f = 1_A \star 1_{-A}$ of a measurable
$1$-avoiding set is of positive type, $f(0) = \delta$, $f(1) = 0$. The OFV dual LP

$$
\min z_0 \quad\text{s.t.}\quad z_0 + z_1 \geq 1,\quad z_0 + z_1 J_0(t) \geq 0\ \ \forall t \geq 0
$$

gives $m_1 \leq z_0$, with analytic optimum
$z_0 = J_0(j_{1,1})/(J_0(j_{1,1}) - 1) = 0.287119$, where $j_{1,1} \approx 3.8317$ is
the first positive zero of $J_1$ (the location of the absolute minimum of $J_0$).
The **simplex strengthening** adds, for each unit-edge equilateral triangle with
squared vertex norms $(a,b,c)$, the inequality $f(\sqrt a) + f(\sqrt b) + f(\sqrt c) \leq 1$
(a $1$-avoiding set meets a unit triangle in at most one vertex), dualized with
nonnegative multipliers. With three off-center triangles this reaches the
published $m_1 \leq 0.268412$ (OFV Table 3.1).

### 3-point and the SOS/atom refinements (KMOR 2015; Ambrus 2023; DMOV)

The 2-point bound saturates near $0.268$ for the unit-triangle family. Two distinct
ways to go further:

- **Inclusion-exclusion (IE) atom LP** (Keleti-Matolcsi-OFV-Ruzsa 2015; Ambrus et
  al. 2023). Take a finite point configuration with MANY distances (not only unit
  edges), partition into IE atoms, and impose linear constraints on the atom
  densities. KMOR 2015 reaches $m_1 \leq 0.2588$; Ambrus et al. 2023 reach
  $m_1 \leq 0.2470$ via a 23-point configuration found by beam search (months of
  compute). This is the strongest known route. It is *fractional/LP in spirit* and
  lives in the project's **Architecture 3** thread (e3g IE-LP framework, e3h beam
  search reaching $0.2584$, matching KMOR).

- **$k$-point matrix (SDP) hierarchy** (Bachoc-Nebe-Oliveira Filho-Vallentin 2009;
  de Laat-Machado-Oliveira Filho-Vallentin, k-point bounds). Promote the scalar LP
  multipliers to PSD matrix multipliers via the $O(2)$-isotypic block-diagonalization
  with Jacobi/Gegenbauer matrix kernels. The 2-point SDP at $n = 2$ reduces to the
  basic Bessel LP (BNOFV slides: at $n = 2$ the SDP gives only $\chi_m \geq 5$). The
  genuine 3-point SDP is heavier; the literature value for the 3-point density bound
  in $\mathbb{R}^2$ is in the $\sim 0.229$ regime (per the DMOV-style hierarchy), but
  this requires the full infinite-dimensional truncation, not a finite triangle
  family.

**Key project finding (e2b):** the matrix (SDP) lift on the OFV *unit-triangle*
family gives NO improvement over the scalar 2-point LP (both $\approx 0.2684$). The
tightening to $0.2588$ and below lives in the IE *atom* LP over multi-distance
configurations (Arch 3), not in the matrix lift on unit triangles. The published
$\sim 0.229$ 3-point regime requires the full $O(2)$-isotypic Jacobi SDP, which is
beyond the available cvxpy SCS/CLARABEL backend overnight. See section 4.

---

## 3. Falconer's $\chi_m \geq 5$: density + rigidity, and why it stalls at 5

Falconer's 1981 argument (lineage dossier section 3) is NOT the density-route
arithmetic of section 1. Its four steps:

- **(F1)** Suppose a measurable proper $4$-coloring; some class $A$ has positive
  upper density.
- **(F2)** Lebesgue density theorem: pass to a small ball where $A$ has density
  near $1$ on its own points.
- **(F3)** A rigid finite configuration $S$ (mobile under $\mathbb{R}^2 \rtimes O(2)$)
  whose unit-distance graph is $4$-chromatic, so "no monochromatic unit pair" plus
  "$4$ colors" over-constrains a high-density region.
- **(F4)** Measure-theoretic averaging over the motion group forces some copy of
  $S$ entirely into $A$: contradiction. The analytic engine is the
  autocorrelation / Wiener-Khinchin positivity $\widehat{R_A}(\xi) = |\widehat{1_A}(\xi)|^2 \geq 0$
  with the hard constraint $R_A(t) = 0$ at $|t| = 1$.

**Why it stalls at $5$.** Step (F3) needs a rigid $(k-1)$-chromatic finite
configuration to output $\chi_m \geq k$. For $k = 5$ a $4$-chromatic rigid object
(the Moser spindle, $7$ vertices) suffices. For $k = 6$ Falconer's machine needs a
$5$-chromatic rigid configuration. The only known $5$-chromatic finite UDGs are the
de Grey 2018 / Polymath16 objects with $509+$ vertices; they are not "rigid and
small" in Falconer's sense, and crucially no $6$-chromatic UDG exists at all. **This
is the cross-architecture coupling:** Falconer's $\chi_m \geq 5 \to \geq 6$ upgrade
is blocked by the SAME missing object (a $6$-chromatic finite UDG in $\mathbb{R}^2$,
or a small $5$-chromatic rigid configuration) that blocks Architecture 1's
$\chi \geq 5 \to \geq 6$. See LEARNINGS L4 and the experiment e2c below.

---

## 4. Project experiments e2a / e2b / e2c (with certificates)

| Experiment | What it does | Result | Certificate |
|---|---|---|---|
| [`e2a`](../../experiments/measurable/e2a_falconer_autocorrelation.py) | autocorrelation of a $1$-avoiding hexagonal cell (illustration) | $R_A$ vanishes on the unit circle | FFT, illustrative |
| [`e2b`](../../experiments/measurable/e2b_spectral_sdp.py) | 2-point spectral LP + 3-point matrix SDP | **2-point: $m_1 \leq 0.287119$ (basic), $0.268412$ (3-triangle), gate PASS exact**; **3-point matrix lift: no improvement ($0.26840$)** | cvxpy + HiGHS (LP) / SCS (SDP); dual-certified |
| [`e2c`](../../experiments/measurable/e2c_falconer_rigorous.py) | Falconer $\chi_m \geq 5$ decomposition: Plancherel witness + density arithmetic + rigidity | Wiener-Khinchin positivity confirmed (min power $2\times10^{-10} \geq 0$), $R_A(1) = 0$ to $5\times10^{-17}$; Moser spindle $\chi = 4$ via SAT | FFT + cvxpy + pysat/cadical |

**e2b cross-validation verdict (the correctness gate).** The 2-point bounds match
the published OFV 2010 values to $< 5\times10^{-7}$ (basic $0.287119$, three-triangle
$0.268412$), and the $\mathbb{R}^1$ wrong-approach detector returns
$m_1(\mathbb{R}) \leq 0.5$ exactly ($\chi_m(\mathbb{R}) \geq 2$, no overshoot). The
3-point matrix SDP, with $Z$ forced diagonal, reproduces the scalar LP ($0.26840$),
confirming the SDP is a faithful (non-leaky) relaxation; with $Z$ free PSD it
delivers no further improvement on the unit-triangle family. A 94-triangle scalar
sweep also saturates at $0.26833$. Honest conclusion: the unit-equilateral-triangle
inequality family is exhausted near $0.268$; further progress is an IE-atom-LP
(Arch 3) or full-DMOV-SDP question.

**e2c verdict.** The analytic identity Falconer's (F4) rests on is confirmed
numerically (positive-type autocorrelation, exact unit-circle vanishing). The
density-route arithmetic is made exact (crosses to $\geq 5$ only at Ambrus 2023's
$m_1 < 1/4$). The rigidity upgrade is named precisely: $\chi_m \geq 6$ via Falconer
needs a $5$-chromatic rigid configuration, the Arch-1 missing object.

---

## 5. Wrong-approach detector status (Architecture 2)

Architecture 2 is partly exempt from the $\mathbb{Q}^2$ control (rationals have
Lebesgue measure zero, so a measurable method may legitimately be blind to
$\mathbb{Q}^2$). The binding controls are $\mathbb{R}^1$ ($\chi_m = 2$) and
$L^\infty$ ($\chi = 4$).

| Method | Uses Euclidean rigidity / $O(2)$? | $\mathbb{R}^1$ detector | $L^\infty$ detector | Verdict |
|---|---|---|---|---|
| Falconer 1981 (density + rigid config) | yes: 2D Lebesgue density; rigid non-collinear config; $O(2)$-mobility | passes (no rigid $4$-chromatic UDG on the line; UDG bipartite) | passes (config edges are Euclidean) | PASS |
| OFV 2010 (2-point LP) | yes: radial kernel $\Omega_2 = J_0$, $O(2)$-invariant | passes ($\Omega_1 = \cos$ gives $m_1(\mathbb{R}) = 1/2$, correct) | passes ($L^\infty$ "circle" is a square, wrong harmonic object) | PASS |
| BNOFV / DMOV ($k$-point SDP) | yes: $O(2)$-isotypic Jacobi/Gegenbauer kernels | passes ($S^0$ degenerates, $\chi_m \geq 2$) | passes (no standard $L^\infty$ spherical harmonics) | PASS |
| Ambrus 2023 (IE-atom LP) | yes: configuration with Euclidean distances $1, \sqrt 3, \dots$ | passes (config is intrinsically 2D / non-collinear) | passes (edges become different $L^\infty$ distances) | PASS |
| e2b (this project) | yes: $J_0$ radial kernel; $\mathbb{R}^1$ detector run inline | **passes, verified: $m_1(\mathbb{R}) \leq 0.5$** | not run (LP would need $L^\infty$ kernel) | PASS |

Every method engages the $O(2)$ rotation group and Euclidean rigidity, and none
overshoots on $\mathbb{R}^1$. The lineage is structurally sound. The shared
obstruction is combinatorial (the missing $6$-chromatic / $5$-chromatic-rigid object),
not a detector failure.

---

## 6. The $\chi_m(\mathbb{R}^2) \geq 6$ frontier: is it open? YES.

Stated as plainly as possible for the atlas record:

- **$\chi_m(\mathbb{R}^2) \geq 5$**: proven, Falconer 1981 (rigidity route) and
  re-proven via Ambrus 2023 $m_1 < 1/4$ (density route). State of the art.
- **$\chi_m(\mathbb{R}^2) \geq 6$**: **OPEN. No published proof.** Both available
  routes are blocked:
  - density route needs $m_1(\mathbb{R}^2) < 1/5 = 0.2$ (current best $0.247$);
  - Falconer rigidity route needs a small $5$-chromatic rigid configuration, i.e.
    effectively the Arch-1 missing $6$-chromatic UDG.
- The "$\chi_m \geq 6$" results in the literature are **misattributions** to the
  Euclidean plane: they are DeCorte-Golubev 2018 (hyperbolic plane, $d \geq 12$;
  exponential volume growth is load-bearing and does not transfer to $\mathbb{R}^2$)
  and Coulson 2002 / Townsend / Woodall (convex-tile / map-type colorings, a
  strictly stronger model than Lebesgue-measurable).

**Falsifiability trigger for this lane.** If a session claims $\chi_m(\mathbb{R}^2) \geq 6$,
VERIFIER must check: (a) does it imply $m_1 < 1/5$, contradicting the Arch-3 lower-bound
experiments? (b) does the $\mathbb{R}^1$ detector degenerate it to $\geq 2$? (c) does
it implicitly construct a $6$-chromatic finite UDG (an independent Arch-1 breakthrough
to be SAT-checked)? Any genuine $\chi_m \geq 6$ on $\mathbb{R}^2$ is escalate-to-Owen.

---

## 7. References

See [`arch2_measurable_lineage.md`](arch2_measurable_lineage.md) section "References"
for the full verified citation table. Key spectral/SDP anchors:

- Oliveira Filho, Vallentin, *Fourier analysis, linear programming, and densities of
  distance avoiding sets in $\mathbb{R}^n$*, JEMS 12 (2010), arXiv:0808.1822.
- Bachoc, Nebe, Oliveira Filho, Vallentin, *Lower bounds for measurable chromatic
  numbers*, GAFA (2009), arXiv:0801.1059.
- Keleti, Matolcsi, Oliveira Filho, Ruzsa, *Better bounds for planar sets avoiding
  unit distances*, DCG (2015), arXiv:1501.00168.
- Ambrus, Csiszarik, Matolcsi, Varga, Zsamboki, *The density of planar sets avoiding
  unit distances*, Math. Programming (2023), arXiv:2207.14179.
- DeCorte, Oliveira Filho, Vallentin, *Density estimates of $1$-avoiding sets via
  higher order correlations* (the $k$-point hierarchy), arXiv:1809.05453.
- DeCorte, Golubev, *Lower bounds for the measurable chromatic number of the
  hyperbolic plane*, DCG (2018), arXiv:1708.01081 (hyperbolic, does NOT transfer).
- Falconer, *The realization of distances in measurable subsets covering
  $\mathbb{R}^n$*, J. Combin. Theory A 31 (1981), 184-189.
