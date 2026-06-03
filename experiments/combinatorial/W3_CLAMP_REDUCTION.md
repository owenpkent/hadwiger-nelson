# W3 structural route: the clamp cocircularity reduction (generalizing Lemma L)

**Status (2026-06-02).** A rigorous reduction of clamp realizability (W3) to a
constrained framework-realization problem, generalizing L42's single-hub Lemma L.
The reduction is proved below and verified computationally
(`w3_clamp_cocircularity.py`). It does **not** prove a realizable clamp exists; it
proves the clamp route **escapes** the specific impossibility (unit-$K_k$) that
closes the single-hub route, and pins the residual hard step to one cocircularity
equation = a "flexible color-clamp," a question in combinatorial rigidity theory.

No bound moves. This is a coordinate: it converts "is a clamp realizable?" into a
sharper, machinery-backed question, and explains the L52 numerics.

---

## 0. Objects

- **Clamp.** A $K_4$-free graph $G$ with $\chi(G)=5$ and a **non-adjacent** pair
  $(s,t)$ that is **forced-different**: $c(s)\neq c(t)$ in every proper 5-coloring.
  Then $H:=G/\{s,t\}$ (identify $s,t$ to a vertex $w$) is **6-chromatic** (a proper
  5-coloring of $H$ would 5-color $G$ with $c(s)=c(t)$, impossible). Conversely (L51)
  splitting a vertex $w$ of any $K_4$-free 6-critical $H$ into non-adjacent $s,t$ with
  $N(s)=A$, $N(t)=B$, $A\sqcup B=N_H(w)$, yields a clamp; L51 exhibited an explicit
  48-vertex triangle-free one. Write $A=N_G(s)$, $B=N_G(t)$, $w$ = the contracted
  vertex.
- **Unit-distance realization** of $G$: an **injective** map $p:V(G)\to\mathbb{R}^2$
  (distinct vertices to distinct points, so that $G$ is a subgraph of the plane's
  unit-distance graph and $\chi(\mathbb{R}^2)\ge\chi(G)$) with
  $\lVert p(u)-p(v)\rVert=1$ for every edge $uv$. Extra unit distances on non-edges
  are harmless (they are also plane-UDG edges); vertex coincidences are not, hence
  injectivity.
- **Unit-cocircular** set: a finite point set lying on a common circle of radius
  **exactly 1**.
- $H-w$: the subgraph of $H$ (equivalently of $G$) induced on $V(H)\setminus\{w\}
  = V(G)\setminus\{s,t\}$, with edge set $E(G)$ restricted to those vertices.

## 1. The reduction (Theorem)

> **Theorem (R).** A clamp $G$ (split of $H$ at $w$ into $s\!\sim\!A$, $t\!\sim\!B$) is
> unit-distance realizable **iff** there is a unit-distance realization $q$ of $H-w$
> in which $A$ is unit-cocircular **and** $B$ is unit-cocircular.

**Proof.**
*( $\Rightarrow$ )* Let $p$ realize $G$. Its restriction to $V(H-w)$ realizes $H-w$
(those vertices carry exactly the edges of $H-w$). Each $a\in A$ satisfies
$\lVert p(s)-p(a)\rVert=1$ (edge $sa$), so $A\subseteq C(p(s),1)$, i.e. $A$ is
unit-cocircular with center $p(s)$. Likewise $B$ is unit-cocircular with center
$p(t)$.

*( $\Leftarrow$ )* Given such a $q$, the unit-cocircularity of $A$ means a radius-1
circle through $A$ exists; let $s^\*$ be **a** center of one. We also need the
realization injective: $s^\*\neq t^\*$ and both distinct from the $H-w$ points.
Extend $q$ by $p(s)=s^\*$, $p(t)=t^\*$. Then every $H-w$ edge is unit (from $q$),
every $sa$ is unit ($a\in A\subseteq C(s^\*,1)$), every $tb$ is unit; $s,t$
non-adjacent so no $st$ constraint. So $p$ realizes $G$. The required
$s^\*\neq t^\*$ is **the load-bearing condition, not a nuisance** (see §2): the
center freedom is $1$-parameter when $|A|=1$, **two discrete choices** when $|A|=2$,
and **pinned** when $|A|\ge 3$, so for the actual clamp ($|A|=8$) the centers are
fixed by $q$ and $s^\*\neq t^\*$ is a genuine constraint on the realization, not
generic. $\blacksquare$

**Remark (existence side: every clamp has $|A|+|B|\ge 5$).** $H=G/\{s,t\}$ is
6-chromatic, so it contains a 6-critical subgraph $H_0$. If $w\notin V(H_0)$ then
$H_0\subseteq H-w$, and $H-w$ is an **induced subgraph of $G$** (it is $G$ on
$V(G)\setminus\{s,t\}$), so $H_0\subseteq G$ gives $\chi(G)\ge 6$, contradicting
$\chi(G)=5$. Hence $w\in V(H_0)$, and $\delta(H_0)\ge 5$ (6-critical), so
$|A|+|B|=\deg_H(w)\ge\deg_{H_0}(w)\ge 5$ for **every** clamp. *(Verified on the
explicit clamp: $|A|=8$, $|B|=15$, $A\cap B=\varnothing$, edge split
$213+8+15=236$.)*

## 2. Generalization of Lemma L, and the escape

**Lemma L (L42, single-hub route).** A hub $h$ forcing $\chi\ge 6$ needs its forced
neighbor set on **one** unit circle (the hub's own circle $C(h,1)$) **and**
rainbow-forced. Rainbow-forced $\Rightarrow$ pairwise forced-different
$\Rightarrow$ (lineage) pairwise adjacent $\Rightarrow$ a unit-distance $K_k$.
Since $\omega(\mathbb{R}^2\text{-UDG})=3$, even $K_4$ is impossible (4 mutually
unit-distance points = a regular tetrahedron $\notin\mathbb{R}^2$). The single-hub
route is **closed by an impossibility.**

**Theorem (R) is the two-circle generalization.** The clamp needs the split
vertex's neighborhood on **two distinct** unit circles ($A$ on $C(s^\*,1)$, $B$ on
$C(t^\*,1)$, $s^\*\neq t^\*$), with **no** mutual-adjacency and **no** rainbow
requirement. Two points break the single-hub picture:

1. *Coloring side:* the clamp needs only the **pair** $(s,t)$ forced-different (two
   colors), never a rainbow-forced 5-set, so it never demands a unit-clique. This is
   the real escape: the unit-$K_k$ that closes the single hub is never invoked.
   (Unit-cocircular $\neq$ mutual-unit-distance: a radius-1 circle carries
   arbitrarily many points at non-unit pairwise distances; and $K_4$-freeness forbids
   an $A$-triangle, so $A\cup\{s\}$ is no clique.)
2. *Geometric side:* $s^\*\neq t^\*$ is exactly what separates the clamp from the
   hub. The degenerate $s^\*=t^\*$ forces $A\cup B$ onto **one** circle with $s=t$ —
   the single-hub configuration — which injectivity already forbids. So "two distinct
   centers" is the clamp's defining geometric feature.

> **The clamp route escapes Lemma L's unit-$K_k$ impossibility** (it never requires a
> unit-clique). The price is replacing one impossibility with an open flexibility
> question (§3), not a proof of realizability.

*Sanity check (in isolation only):* an explicit $3+2$ placement on two distinct unit
circles, 5 points distinct and **not** a unit clique, exists — confirming the target
is not a unit-$K_k$ obstruction. This is tautological (the points were placed on the
circles) and says nothing about the **coupled** problem of §3.

## 3. The residual hard step (where the difficulty now lives, not hidden)

(R) reduces realizability to: **realize $H-w$ with $A$ and $B$ unit-cocircular.**
Count the cocircularity equations. Forcing $k$ points onto a common radius-1 circle
is the intersection $\bigcap_{i=1}^k C(x_i,1)$ being non-empty, which is automatic
for $k\le 2$ and costs $\mathrm{codim}=k-2$ for $k\ge 3$ (each extra circle one
equation). For the minimum split-vertex degree 5, the cheapest split is $2+3$:
$$\mathrm{codim}(|A|{=}2)+\mathrm{codim}(|B|{=}3)=0+1=\boxed{1}$$
**one** unit-circumradius equation on the realization of $H-w$. So:

> **A clamp is realizable iff $H-w$ admits a unit-distance realization in which one
> chosen 3-subset of $N(w)$ has circumradius exactly 1.**

This is precisely a **flexible color-clamp**: $H-w$ must realize with at least a
1-parameter flex that can be tuned to satisfy the single circumradius equation.

**Crucial honesty: codim is "how many equations," not "how solvable."** Solvability
needs $\mathrm{flex}(H-w)\ge\mathrm{codim}$. A generic *minimally rigid* $H-w$ has
**zero** internal flex, so even codim $1$ is generically **unsatisfiable** — one
equation on a rigid graph is as dead as nineteen. The "$1$ vs $19$" contrast below
means *fewer equations to clear*, **not** that degree-5 is tractable: degree-5 is
gated on the **same** unproven flex of $H-w$ as the apex case, with a smaller deficit.
This is consistent with L52 (the calibrated embedder failed on the actual clamp). The
honest content of (R) is that the residual is a **rigidity question** (does $H-w$'s
rigidity matroid leave the cocircularity constraint satisfiable?) rather than the
unit-$K_k$ *impossibility* — a reframing into rigidity-theoretic terms, not yet an
application of a rigidity theorem.

**Why the explicit Mycielski clamp is hopeless (explains L52).** Its split vertex is
the Mycielskian apex, degree 23, split $8+15$: cost
$\mathrm{codim}(8)+\mathrm{codim}(15)=6+13=19$ equations. The apex high degree is a
**construction artifact** of the Mycielski tower, not intrinsic to clamps. This is
exactly why the L52 calibrated solver failed with residuals piled on the apex edges,
and it sharpens the L52 conclusion: the obstruction is the 19 forced cocircularities,
not a DOF or degree count (which $P_{510}$ shows are not predictive).

## 4. The precise open problem (the next rung)

> **Does there exist a $K_4$-free 6-critical graph $H$ with a degree-5 vertex $w$
> such that $H-w$ has a unit-distance realization in which a 3-subset of $N(w)$ has
> circumradius 1?** Equivalently: a realizable flexible color-clamp.

This is now decidable in principle by exact elimination (Gröbner, as in
`h2_groebner_moser14.py`) once a **small** low-degree clamp is in hand, and it lives
in rigidity theory rather than ad hoc search. The complementary L45 fact (the
realizable lineage has no clamp at all) says realizable graphs found so far avoid
this structure; (R) says what a realizable clamp must look like (a low-degree split
vertex with a tunable cocircular 3-subset). Bridging the two is the chi$\ge 6$
integer frontier.

---

### Verification ledger
| Claim | Check | Status |
|---|---|---|
| Edge decomposition $E(G)=E(H{-}w)\sqcup(s{\sim}A)\sqcup(t{\sim}B)$ | `w3_clamp_cocircularity.py` [1] | PASS ($213{+}8{+}15{=}236$) |
| $\|A\|+\|B\|=\deg_H(w)\ge5$ (6-critical core) | [1] | PASS ($23\ge5$) |
| unit-$K_4$ impossible ($\omega=3$) | [2] | PASS |
| two-circle $3{+}2$ split satisfiable **in isolation** (tautological, not the coupled problem) | [2] | PASS |
| cheapest deg-5 split costs 1 circumradius equation | [3] | PASS |
| Mycielski apex split costs 19 equations | [3] | PASS |

### Honest scope (what this is and is NOT)
- **(R) is elementary.** It is essentially the defining property of unit-distance
  graphs ("a vertex's neighbors lie on its unit circle") specialized to a non-adjacent
  split pair, so the two centers decouple. The only non-obvious step is that
  non-adjacency removes the $\lVert s^\*-t^\*\rVert$ constraint, exposing $s^\*\neq
  t^\*$ as the escape condition. It is immediate to anyone fluent in UDG/rigidity; the
  value is making the form **exact** and naming the residual object precisely.
- **Prior art.** Cocircularity as a UDG device is **classical** (L42's caveat:
  $K_{2,3}$ is a forbidden unit-distance subgraph because two unit circles meet in
  $\le 2$ points; textbook, not a discovery). (R) reuses it; no new geometry.
- **Same residual object as before.** The "flexible color-clamp" was already named in
  `rigidity_w3_escape.py` (the dossier's A5). (R) sharpens its *form* (an exact iff +
  a per-vertex circumradius-equation count + the cheapest split) but bottoms out at
  the **identical** open problem; **no mathematical content is proven past L51/L52.**
- The **escape** is from Lemma L *specifically* (the unit-$K_k$ impossibility). It does
  **not** prove a realizable clamp exists; $H-w$ may lack the needed flex (generically
  it does). That residual is the open problem.
- **"Imports power"?** Honestly: it **reframes** W3 into rigidity-theoretic *language*
  (rigidity matroid, exact elimination). No rigidity *theorem* is invoked or computed
  here. The power is potential, not yet drawn. **No bound moves.**
