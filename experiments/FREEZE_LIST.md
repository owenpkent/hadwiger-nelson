# FREEZE_LIST

Dead proposal shapes. Each is a logged negative result: do **not** re-propose it,
and reject any new idea that reduces to it before spending budget. This is the
human-readable twin of the `kill_*` nodes in [`lemma_db`](lemma_db/) (where the
control-blind kills also carry a firewall flag).

The single source for the creative-attack workflow's KNOWN-KILLS block is this
file; [`.claude/workflows/hn-lens-attack.js`](../.claude/workflows/hn-lens-attack.js)
points here. Update this file when a new negative lands in
[`LEARNINGS.md`](LEARNINGS.md), then mirror the one-line gist into the workflow
brief if needed.

## Escape condition

A proposal escapes the freeze list only if it does at least one of:

1. introduces a **new chi-5 UDG outside the P510 / de Grey lineage** carrying
   phase or imprimitive structure (route ii, L55-L56), **or**
2. lands a construction inside the **both-free class** (K4-free **and**
   K_{2,3}-free) with $\chi \ge 6$ (the codegree wall, L63), **or**
3. attacks the measurable bound by a route other than the order-2 SDP at $X_{23}$
   (that route is closed, L72), e.g. noncommutative SE(2).

Anything that does none of these is almost certainly already frozen.

## The list

| # | Dead shape | Why dead | Killed by |
|---|------------|----------|-----------|
| K1 | Long-range / non-adjacent forcing inside the known lineage | All ~2.29M non-adjacent pairs in the 12 known chi-5 UDGs are FREE; all forcing is adjacency-local | L45 / L51 / L56 / L57 |
| K2 | Single-vertex-port gadget chains / color-shifter relations | S_k color symmetry confines port relations to the primitive monoid {0, I, J-I, J} | L55 (monoid obstruction) |
| K3 | "RG leading eigenvalue > 1" as a forcing diagnostic | $\lambda_1$ is coloring entropy, the opposite of forcing; the right diagnostic is imprimitivity | L55 |
| K4 | DOF / over-determination counting or max-degree heuristics for realizability | Invalidated by P510 at +1487 over-determination, degree 36, yet realizable | L52 |
| K5 | Groebner exact realizability beyond ~14 vertices | Computationally infeasible at program scale | (tooling) |
| K6 | Single-hub rainbow forcing | Needs a unit-distance $K_k$, but $\omega = 3$ | Lemma L |
| K7 | Norm-blind Borel / Steinhaus lower bounds | Fail the $L^\infty$ detector: would over-prove $\chi \ge 7$ where $\chi = 4$ | $L^\infty$ control |
| K8 | Any combinatorial argument that lifts naively to $\mathbb{Q}^2$ | Would prove $\chi(\mathbb{Q}^2) \ge 3$, false | $\mathbb{Q}^2$ control |
| K9 | Polygonal / map-type 6-colorings of the plane | Collide with Voronov: map-type colorings need 7 | Voronov |
| K10 | Box-complex / topological coindex lower bounds as-is | Calibrated: coindex undershoots on known chi-5 graphs | calibration |
| K11 | Degree-1 / order-1 moment relaxations for $\chi_m \ge 5$ at $X_{23}$ | Margin 0, provably too weak | L43 |
| K12 | Order-2 measurable SDP at $X_{23}$ for $\chi_m \ge 6$ | FEASIBLE at order 2, so cannot certify even $\chi_m \ge 5$; route CLOSED | L72 |
| K13 | Treating $\chi_m \ge 6$ as if it implied $\chi \ge 6$ | $\chi \le \chi_m$ always; the direction only helps via a separate transfer principle | (the K1 circularity guard) |
