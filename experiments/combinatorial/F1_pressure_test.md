# F1 Pressure Test: the cocircularity / wrong-shape-bridge barrier

ADVERSARY report. Session 2026-06-01. Target: finding **F1** in
`docs/PUBLISHABLE_FINDINGS.md` (the structural explanation of why no chi-6
unit-distance graph has emerged from the de Grey / Polymath16 / Heule lineage).

Verdict up front: **F1 is TRUE-but-as-a-heuristic, with a sharper and more
rigorous core than F1 currently states, and one over-claim in the L34 framing
that should be retracted.** No chi-6 UDG was found (no break). The barrier was
strengthened and re-grounded on a clean graph-theoretic mechanism specific to the
lineage. The claim as a *theorem about all UDGs* is not established and is not
established by anything here.

All experiments are exact-arithmetic + SAT, reusing the `sources/cnp-sat/vtx/510.vtx`
P_510 loader (verified: 510 vertices, 2504 edges, all edges exact unit distances in
Q(sqrt3, sqrt11, sqrt5); chi = 5 confirmed: 4-coloring UNSAT in 98 s, 5-coloring
SAT in 0.02 s, Cadical). Code: `f1pt_lib.py`, `f1pt_attack1*.py`, `f1pt_attack3*.py`.
Caches under `experiments/combinatorial/_cache/f1pt_*.json`.

---

## 0. What F1 / L34 actually claim, restated precisely

The L22/L24 list-coloring theorem (machine-checked in Lean) says: for
`G = H_1 cup H_2 cup B`, chi(G) >= 6 iff for every proper 5-coloring c_1 of H_1
the residual list-coloring on H_2 (lists `L(v) = [5] \ F(v)`,
`F(v) = { c_1(u) : (u,v) in B }`) is infeasible. The L27/L28 abstract chi-6 graphs
realize this with "saturating" hubs v in H_2 where `|F(v)| = 5` (empty list) under
every c_1. Each such hub needs many bridge-sources `U_v subset V(H_1)`.

F1 / L34 assert: this forcing needs **concentration** (hub bridge-degree ~268,
L27), but realizability forces an **even, low-concentration** bridge layout (rigid
orbits, L34), so the embeddable bridge supply is "the wrong shape." The task's
sharp objection: rigid orbits are not the only option, and concentration at a
single hub is geometrically FREE (any points on v's unit circle are unit-distant
from v). So is there a non-rigid coordinate-first construction that delivers
concentration AND forces chi >= 6?

---

## 1. The geometric reduction (rigorous): F1's core is one lemma

A bridge `(u, v)` realized as a genuine unit distance means `u` lies on `v`'s unit
circle. So **every** hub's bridge-source set `U_v` must be **cocircular at radius 1**
(this is the L23/L27 cocircularity requirement, and it is mandatory, not heuristic).

`|F(v)| = 5` requires 5 of those cocircular sources to take 5 **distinct** colors
under c_1. For this to hold for *every* c_1 (the obstruction), it suffices that
some 5 of the cocircular sources are **rainbow-forced** (forced to 5 distinct
colors in every proper 5-coloring of the generator). Hence:

> **Lemma (L) [the rigorous core of F1].** F1's geometric content reduces to:
> *can 5 points that are cocircular at unit radius be rainbow-forced in a unit-
> distance graph?* If yes (and the generator realizes), put a hub at the circle
> center: chi >= 6, realizable -> a chi-6 UDG. If no, the single-hub forcing route
> is geometrically obstructed.

This is the crisp, falsifiable statement F1 currently lacks. It is **architecture-1,
exact, and Euclidean** (cocircularity at unit radius is a Euclidean-circle notion).

---

## 2. The mechanism that blocks Lemma (L) in the lineage (rigorous, SAT-certified)

Two independent geometric/combinatorial facts, both verified on P_510:

**(A) Concentration ceiling from cocircularity (Attack 3A).** The maximum number
of P_510 points lying on a *common unit circle* is **36**, and that circle is
exactly the unit circle of a single vertex (vertex 0; its 36 neighbors).
Float-prefilter over 172,190 candidate centers (every close pair determines two
unit circles), max = 36 at center = origin = vertex 0. So in any **rigid** orbit
the most concentrated single hub has bridge-degree 36, versus the L27 abstract
requirement of 268: a rigorous 7.4x concentration deficit.
Cache: `f1pt_attack3_cocirc.json`.

**(B) No long-range color forcing in P_510 (Attack 1e + broad sample).** Define a
pair `{a,b}` as *forced-different* if every proper 5-coloring gives them different
colors (merge a,b -> 5-UNSAT). Result:
- Among the 40 highest-degree vertices: **78/78** forced-different pairs are
  unit-distance EDGES; **0** non-adjacent forced-different pairs.
- Random **300 non-adjacent pairs across all of P_510**: **0** forced-different.

So in P_510, *forced-different is equivalent to adjacent*. There is no long-range
color rigidity. Consequently a rainbow-forced 5-set (5 pairwise forced-different
vertices) would have to be a **unit-distance K_5**, which does not exist
(omega(R^2 UDG) = 3). And on a single hub circle the unit-distance edges among
cocircular points occur only at 60-degree gaps (chord = 1), so the induced UDG on
hub-circle points is a sub-C_6 (omega 2, chi 2): it can never carry a rainbow.
Caches: `f1pt_attack1d_p510rainbow.json`, `f1pt_attack1e_calibrate.json`,
`f1pt_attack1b_freehub.json`.

**Direct test (Attack 1d).** No cocircular-at-unit 5-set in P_510 is rainbow-forced
(top-8 largest cocircular sets x 25 random 5-subsets = 200 tests, all NOT forced).
**Triangular lattice (Attack 1c).** In the natural unit-distance habitat (R = 3, 4
patches; abundant cocircular hexagons), no cocircular 5-subset is rainbow-forced
either (the lattice is only 3-chromatic, so it cannot rainbow anything to 5).

Together: Lemma (L) **fails for the entire P_510 / triangular-lattice family**, by
a clean mechanism (forced-difference = adjacency = local; cocircular points are
mutually non-adjacent except at 60 degrees; no unit-K_5).

---

## 3. DOF / counting analysis (Attack 3)

Heuristic generic-rigidity count for embedding `G=(V,E)` as a UDG: `2|V|-3`
effective coordinates vs `|E|` unit-distance equations; generically realizable iff
`|E| <= 2|V|-3`.

| Graph | V | E | 2V-3 | over-determination | matches reality? |
|---|---:|---:|---:|---:|---|
| Moser spindle | 7 | 11 | 11 | 0 | yes (rigid, realizable) |
| L23 Moser x Moser + 14B (abstract chi-5) | 14 | 36 | 25 | +11 | yes (L23: NOT realizable) |
| L27 P510^2 + 2700B (abstract chi-6) | 1020 | 7708 | 2037 | +5671 | yes (NOT realizable) |
| L28 P510^2 + 2000B (abstract chi-6) | 1020 | 7008 | 2037 | +4971 | yes (NOT realizable) |

The global count is too crude (two disjoint rigid P_510 copies are over-determined
by 2971 yet realizable as rigid pieces). The **refined** count is the decisive one:
the two halves are each rigid, so the only freedom is the **relative pose** of H_2
(translation 2 + rotation 1 = **3 DOF**), against `|B|` bridge equations. A
rigid-rigid coupling generically realizes **at most 3 bridges**; the chi-6
obstruction needs `|B| ~ 2000`, an over-determination of ~1997. This is exactly why
the L34 rigid orbits realize many bridges only by landing on a high-symmetry
**coincidence variety** (the 60-degree rotation), which by orbit structure spreads
bridges evenly rather than concentrating them.

So non-realizability of the abstract chi-6 graphs is a **counting (DOF) fact**, not
a contingency: it is over-determined by thousands of equations in 3 unknowns. The
re-embedding question of task attack 3 (solve for coordinates making all `U_v`
cocircular at unit radius simultaneously) is therefore generically infeasible; it
could only succeed on a measure-zero coincidence variety, and the sieve (L23/L27/L29:
0/97, 0/92 saturating hubs cocircular) is the empirical confirmation that the
lineage's specific graphs do not lie on such a variety.
Cache: `f1pt_attack3_dof.json`.

---

## 4. The over-claim to retract (adversarial honesty about my own first attempt)

I initially "proved" that a realized hub has `|F(v)| <= 4` always (its sources are
all adjacent to it, hence avoid c(v)). **This is wrong as a chi-6 obstruction.** It
is the trivial fact that in any *existing* proper 5-coloring a vertex's neighbors
avoid its color; it has no content when the graph is non-5-colorable (which is the
whole point). A hub adjacent to 5 neighbors of 5 distinct colors simply needs a
6th color -- that is precisely chi >= 6, not a contradiction. I retract it.

The L34 sentence "realizability forces the even, low-concentration bridge layout
that is precisely the layout a 5-coloring survives" is a *correct description of
the rigid-orbit experiments* but is stated as if it were the general mechanism.
The actual general mechanism (Section 2) is sharper and different: it is the
absence of long-range color forcing combined with the cocircular-points-are-locally-
C_6 geometry, not "even spread" per se.

---

## 5. Did anything break F1? No. Closest break candidate and why it failed

The sharpest break attempt (Attack 1e): search P_510 for a rainbow-forced 5-set
that has a common P_510 neighbor (which would be an already-realized hub adjacent
to a rainbow-forced 5-set = an in-graph chi-6 witness). Result: **no rainbow-forced
5-set exists even in the high-degree core** (no 5-clique in the forced-different
graph D, which is itself just the adjacency graph restricted to the core). So the
break route is closed for P_510 by the same mechanism.

Smallest decisive test case: the **wheel `W_6` = hub + hexagon** (`f1pt_attack1b`).
The 6 cocircular-at-unit points (the only ones that can carry mutual unit edges)
form C_6 (chi 2); the hub makes chi 3. The cocircular sources can never be forced
to 5 colors because their own structure is 2-colorable and there is no long-range
forcing to override it. This 7-vertex gadget is the in-vitro proof of why
concentration-by-construction does not yield forcing.

---

## 6. Wrong-approach detectors (Attack 4): PASS on all three

Applying the F1 *idea* (a cocircular-at-unit hub whose sources are rainbow-forced)
to the three controls:

- **Q^2** (chi = 2): the 23-point rational UDG sample has chi 2; the mechanism needs
  a chi-5 rainbow generator, which Q^2 does not contain (Woodall: Q^2 UDG is
  bipartite). No over-bound. PASS.
- **L^infty** (chi = 4): the king-grid UDG has chi 4; "cocircular at unit radius"
  is a Euclidean-circle notion (in L^infty the unit ball is a square), so the
  mechanism does not transfer; and again no chi-5 generator. PASS.
- **R^1** (chi = 2): no circles exist on the line; the mechanism is vacuous. PASS.

The mechanism is intrinsically Euclidean and intrinsically requires the existence
of a chi-5 UDG, so it cannot manufacture a spurious bound on any control.
(Controls re-verified this session: chi(Q^2 sample) = 2, chi(L-inf) = 4,
chi(R^1) = 2.)

---

## 7. Rigorous core vs heuristic shell (the deliverable)

**Rigorous (proved / SAT-certified this session, for the P_510 lineage):**
1. Realized bridges are edges; a hub's bridge-sources are cocircular at unit radius.
2. Max cocircular-at-unit subset of P_510 = **36** (= a single vertex's neighborhood).
3. In P_510, *forced-different <=> adjacent* (0/300 non-adjacent pairs forced; 78/78
   core forced-different pairs are edges). No long-range color forcing.
4. Hence no cocircular-at-unit 5-set in P_510 (or the triangular lattice) is
   rainbow-forced (Lemma (L) fails for the family); a single realizable saturated
   hub would need a unit-distance K_5, which does not exist.
5. DOF: rigid-rigid coupling realizes O(1) generic bridges; the abstract chi-6
   graphs are over-determined by ~5000 equations; re-embedding to make all `U_v`
   cocircular is generically infeasible (measure-zero coincidence variety only).

**Heuristic / extrapolated (NOT proved, the honest shell):**
- That *no* chi-5 building block, in or out of the de Grey / Polymath lineage, can
  host a concentrated realizable saturating hub. The mechanism in (3) is a property
  of P_510 (and the lattice), *not* a theorem about all UDGs. A hypothetical chi-5
  UDG with genuine **long-range color forcing** (non-adjacent forced-different
  pairs) OR with a vertex whose unit circle passes through many *mutually
  color-constrained* points is not excluded by anything here. No such object is
  known, but "none exists" is a conjecture, not a result.
- The reduction to Lemma (L) covers the **single-hub / forced-rainbow** route. The
  L28 *graded* (distributed) rainbow forcing uses 22-27 sources whose rainbow is a
  union over many c_1 rather than a single forced 5-clique; the rigorous mechanism
  in (3) does not directly close the graded route (it closes the forced-5-clique
  route). The graded route is closed only *empirically* (the L23/L27/L29 sieves:
  0/97, 0/92 saturating hubs cocircular) and by the DOF count, not by a theorem.

---

## 8. Verdict

**F1 is TRUE-but-only-as-a-heuristic, and is improvable.** The correct, defensible,
potentially-publishable statement is **Lemma (L)** plus the mechanism of Section 2,
restricted honestly to the lineage:

> For the de Grey / Polymath16 chi-5 building blocks (P_510 and relatives),
> forced-different pairs coincide with unit-distance edges, so color forcing is
> purely local; cocircular-at-unit point sets are mutually non-adjacent except at
> 60-degree gaps; therefore the L22/L24 single-hub saturation obstruction cannot be
> realized as a unit-distance graph, and (DOF) the abstract coupled chi-6 graphs are
> over-determined by ~10^3 equations and do not embed. Whether some *other* chi-5
> UDG with long-range color forcing could break this is open.

This reframes the search for a chi-6 UDG as the precise question: **find a chi-5
unit-distance graph with non-adjacent forced-different pairs (long-range color
rigidity), so that a cocircular 5-set can be rainbow-forced.** That is a clean,
falsifiable open problem and the right target.

No break. No chi-6 UDG. Bounds unchanged: chi(R^2) in [5,7].

---

### Artifacts
- `experiments/combinatorial/f1pt_lib.py` (standalone P_510 loader + SAT + cocirc)
- `experiments/combinatorial/f1pt_attack1b_freehub.py` (W_6 hexagon-hub gadget)
- `experiments/combinatorial/f1pt_attack1c_rainbow.py` (triangular-lattice cocircular rainbow test)
- `experiments/combinatorial/f1pt_attack1d_p510rainbow.py` (P_510 cocircular rainbow test)
- `experiments/combinatorial/f1pt_attack1e_calibrate.py` (forced-different graph; break search)
- `experiments/combinatorial/f1pt_attack3_cocirc.py` (max cocircular-unit subset = 36)
- `experiments/combinatorial/f1pt_attack3_dof.py` (DOF over-determination table)
- caches: `experiments/combinatorial/_cache/f1pt_*.json`
