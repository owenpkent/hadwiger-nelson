# LOAD_BEARING_FACTS

Settled facts the program builds on. **Do not re-derive these.** A creative round
should treat them as given and reason past them. This is the curated "current
frontier" twin of the freeze list: the freeze list says what is dead, this says
what is established and load-bearing.

Single source for the creative-attack workflow's CURRENT-FRONTIER block;
[`.claude/workflows/hn-lens-attack.js`](../.claude/workflows/hn-lens-attack.js)
points here. Keep in sync with the top of [`LEARNINGS.md`](LEARNINGS.md) and the
`lemma_db` frontier.

## The one missing object

1. **The bottleneck is a single object**: a unit-distance-realizable flexible
   color-clamp. Take any K4-free 6-critical graph $H$, split a vertex $w$ into
   non-adjacent $s \sim A$, $t \sim B$; in every proper 5-coloring $s, t$ are
   forced different, so contracting $s = t$ gives $\chi \ge 6$. The abstract object
   exists: a SAT-verified 48-vertex triangle-free witness (L51-L53). All difficulty
   is **W3 = unit-distance realizability in $\mathbb{R}^2$**.

2. **Theorem R (exact iff)**: the clamp realizes IFF $H - w$ realizes with the
   neighbor-sets $A$ and $B$ each on a radius-1 circle with **distinct** centers
   $s^* \ne t^*$. Every clamp split vertex has degree $\ge 5$, so $\{A, B\}$ is a
   width $\ge 2$ interface (L51-L53).

3. **The lineage is forcing-sterile** (L57-L59): every one of ~2.29M non-adjacent
   pairs across the 12 known chi-5 UDGs (199 to 874 vtx) is FREE. The missing
   object must come from a NEW chi-5 UDG built on a different principle.

4. **The monoid obstruction** (L55): single-vertex-port gadget chains have their
   port relation confined to the primitive monoid {0, I, J-I, J}. The clamp
   question factors into (i) a forced-same gadget [dead on the lineage, L56-L57] or
   (ii) a WIDE interface ($\ge 2$ boundary vertices) whose boundary-coloring
   transfer matrix is **imprimitive**. Route (ii) is the only live combinatorial
   route.

5. **The codegree wall** (L63): UDG-realizability forces $K_{2,3}$-freeness (two
   unit circles meet in $\le 2$ points). This excludes every manufactured K4-free
   6-critical host. The wanted gadget needs all four of: K4-free, 6-critical,
   UDG-realizable-in-plane, not-$K_{2,3}$-excluded.

6. **The measurable thread**: $\chi_m(\mathbb{R}^2) \ge 5$ is classical (Falconer).
   The order-2 Lasserre SDP on Ambrus's $X_{23}$ is FEASIBLE, so it does not certify
   even $\chi_m \ge 5$ and cannot reach $\chi_m \ge 6$: **the order-2 measurable
   route is CLOSED** (L70-L72). Note $\chi \le \chi_m$ always, and $\chi_m \ge 6$
   does NOT imply $\chi \ge 6$.

7. **Calibration** (L54): backward-from-2050 puts the most likely terminal answer
   at $\chi = 6$ via a finite UDG. Dark horse: the right question may be the Borel
   chromatic number $\chi_B$, not $\chi$.

## Repo facts (capabilities, not conjectures)

- Stack: Python + python-sat (Cadical/Glucose/Maple) + sympy exact arithmetic +
  networkx + cvxpy; Lean 4 skeleton (sorry-free). PyPy gives ~5x on the pure-Python
  solver (not for pysat code).
- **No C compiler on host**: nauty / pynauty cannot install.
- SAT solves on 500-2000 vtx UDGs are routine; the symmetry-broken portfolio
  self-certifies the whole $\chi \ge 5$ lineage (M^4(C5) k=6, P510 k=4, de Grey
  1585 k=4 all UNSAT). Exact Groebner realizability tops out at ~14 vertices.
- The three controls are enforced gates: `smoke_test.py` (colors them) and
  `lemma_db/build_db.py` (firewall). See [`STATE_OF_THE_PROGRAM.md`](../STATE_OF_THE_PROGRAM.md).
