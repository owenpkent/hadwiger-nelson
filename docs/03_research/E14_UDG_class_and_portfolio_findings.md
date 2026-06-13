# The UDG-Necessary Class and the Solver-Portfolio Wall

**Status:** living document. Covers the L63-L64 thread (the codegree wall, the
Folkman floor, the in-class generation experiment E14, and the solver-portfolio
finding). The central E14 question is OPEN at the time of writing; this document
states precisely what is settled, what is suggestive, and what is undecided.

**Date:** 2026-06-13. **Architecture:** 1 (combinatorial / unit-distance graphs).

---

## 0. One-paragraph summary

The program's bottleneck is a single missing object: a finite unit-distance
graph (UDG) in the plane with chromatic number $\ge 6$. We proved that the
obstruction to realizing such a graph from the abundant supply of abstract
$K_4$-free 6-chromatic graphs is a **codegree bound** (every planar UDG is
$K_{2,3}$-free), settled the abstract size floor at **16 vertices** using the
vertex Folkman literature, and then attacked the problem from the realizable
side by growing a real UDG ($P_{510}$) toward $\chi \ge 6$ while staying inside
the UDG-necessary class. That class turned out to be **liquid** (it resists
forcing), and the binding constraint on deciding the question turned out to be
**SAT-solver strategy, not mathematics**: the same instance took Cadical 12+
hours and MapleChrono 155 seconds. No bound on $\chi(\mathbb{R}^2)$ moved.

---

## 1. Background: the four-architecture program and the W3 wall

The Hadwiger-Nelson problem asks for $\chi(\mathbb{R}^2)$, known to lie in
$[5,7]$. This repository organizes attacks into four architectures; this
document is entirely Architecture 1 (build a finite UDG with $\chi \ge 6$).

A long line of experiments (L42-L62) established the **W3 wall**: the realizable
de Grey / Polymath16 lineage of $\chi=5$ UDGs contains no "clamp" and no
"alternator," the two abstract gadgets that would lift $\chi$ to 6. Exhaustive
classification of all ~2.29M non-adjacent vertex pairs across the lineage found
**zero** forced pairs (L57); a criticality scan proved the lineage is
forcing-sterile *by construction* (L59, via the Essential-Pair Lemma of L58).
The missing object, if it is a finite UDG, must be a **new** graph outside the
lineage.

Two routes to that new object were identified (L58, L60-L62):
- **Clamp route:** a $K_4$-free $\chi=5$ graph with a non-adjacent
  forced-different pair, realized at unit distance.
- **Phase-gadget route:** an **equality-alternator** (every proper 5-coloring
  colors exactly one of two non-adjacent pairs monochromatically), realized with
  two congruent rotation-related interfaces, closed into a necklace.

Both routes need the same scarce ingredient: a small, triangle-rich (so
UDG-plausible), $K_4$-free, 6-critical **host** graph. The blocker was the
absence of a graph enumerator (`nauty`) on this machine.

---

## 2. L63: the host factory works, but a codegree wall excludes everything it makes

### 2.1 The factory (positive)

We manufactured hosts without `nauty` using **Mycielski towers**:
- Seeds: $M(M(W_5))$ (27 vertices) and $M(M(C_5 + K_1))$ (25 vertices). Both are
  $K_4$-free (Mycielski preserves $K_4$-freeness: a $K_4$-free graph has
  triangle-free neighborhoods, so no shadow clique can close), 6-chromatic,
  vertex-critical, and **triangle-rich** (the wheel hub / apex inject triangles,
  giving the $\omega = 3$ substrate the phase route demands).
- A SAT-guided shrink (delete a vertex; the host drops to 5-colorable; push back
  to 5-UNSAT by adding $K_4$-safe blocking edges between same-colored
  non-adjacent pairs of successive SAT models; extract the vertex-critical core;
  recurse) drove the order down to **18 vertices** (84 triangles covering all 18
  vertices, degrees in $[7,12]$).

The alternator gadget (L60-L62) transfers to this triangle-rich substrate and is
**abundant**: 626 of 2449 disjoint edge pairs on the 18-vertex host are
alternators (~26%, versus 2.8% on the old 47-vertex triangle-free $M^3(C_5)$
host). Pair-swap involutions (the L61 congruence advantage) survive too (the
20-vertex core has $|\mathrm{Aut}| = 10$, with 3 of 5 sampled alternators
admitting an automorphism swapping the two pairs).

### 2.2 The codegree wall (the finding)

In a planar UDG, two unit circles meet in **at most 2 points**, so every vertex
pair has at most 2 common neighbors: **every UDG is $K_{2,3}$-free**. Counting
($\sum_v \binom{d_v}{2} \le 2\binom{n}{2}$) then forces

$$m \;\le\; \frac{n\bigl(1 + \sqrt{8n-7}\bigr)}{4}.$$

Every host the factory produces violates this:
- the 18-vertex host is edge-critical at $m = 76$ against a ceiling of $57$;
- all ~35 independent edge-critical cores (n = 18-24, both seed lineages,
  codegree-aware and unaware searches) sit at density $m/n \approx 4.2$ with
  126-148 codegree violations;
- the classic $M^3(C_5)$ host has **434** codegree violations (max codegree 11),
  which retroactively explains, on independent grounds, why the L52/L61 attempts
  to realize it as a UDG were hopeless.

**Rigorous corollary.** Combining the $K_{2,3}$ ceiling with the Kostochka-Yancey
6-critical floor $m \ge 2.8n - 1.8$: the floor exceeds the ceiling for $n \le
12$, so **any 6-chromatic UDG has a 6-critical core on at least 13 vertices.**

**Conditional corollary.** If $K_4$-free 6-critical graphs genuinely require
$m/n \approx 4.2$ at this scale, UDG-plausible hosts need $n \gtrsim 32$: the
phase-route gadget will not be tiny, and the 47-48-vertex scale of past attempts
was never the mistake.

### 2.3 The Folkman floor (literature, settles L51's $[9,48]$)

The minimum order of a $K_4$-free 6-chromatic graph is the vertex Folkman number
$F_v(2,2,2,2,2;4)$. The literature settles it: **$F_v(2,2,2,2,2;4) = 16$**, with
the only 16-vertex witnesses being the two Ramsey $(4,4)$-graphs (Paley-type,
$m \approx 60$). Both violate the codegree ceiling ($60 > 48$), so:
- the UDG-necessary class has **no member at the Folkman floor**; rigorously
  $n \ge 17$ inside the class;
- since the ceiling only reaches average degree 7.5 around $n \approx 26$, even
  Folkman-floor density excludes the class below $n \approx 26$;
- our factory's $n = 18$ output is only 2 above the true abstract floor.

References (added to `sources/`): Xu-Liang-Radziszowski, *Chromatic Vertex
Folkman Numbers* (arXiv:1612.08136); Nenov (arXiv:0903.3151); Kostochka-Yancey,
*Ore's conjecture on color-critical graphs is almost true* (arXiv:1209.1050);
Hassan-Jiang-Narvaez-Radziszowski-Xu (Graphs and Combinatorics 2023).

---

## 3. L64 / E14: generating inside the class from a real seed

The L63 redirect: stop manufacturing hosts *above* the UDG class and cutting
down. Generate *inside* the class, with $K_4$-freeness **and** $K_{2,3}$-freeness
as hard invariants, seeded from a real UDG.

### 3.1 Seed logic confirmed

$P_{510}$ (a Polymath16 $\chi=5$ UDG) is **automatically $K_4$-free and
$K_{2,3}$-free**, verified at load (codegree $\le 2$ everywhere). The realizable
lineage lives natively in the class L63 identified, so growth never has to leave
it.

### 3.2 The class is liquid

The grower adds blocking edges, each required to be $K_4$-safe and
codegree-safe, choosing greedily by how many sampled 5-colorings the edge kills.
Result: adding **524 model-guided plus blind edges (reaching 674 added,
$m = 3178$ on 510 vertices)** keeps the graph **5-colorable at every step**, with
no stuck signal (safe-edge headroom never ran out; $m = 3178$ is far below the
$\sim 8200$ codegree ceiling). Forcing $\chi \ge 6$ inside the class from this
seed is hard. This is consistent with the L45/L56/L57 "deep liquidity" picture:
the realizable neighborhood resists long-range forcing even when edges are
actively pushed into it.

This is **suggestive, not a theorem.** 674 safe edges without forcing $\chi \ge
6$ shows the class is hard to push from $P_{510}$; it does **not** show the class
caps at $\chi = 5$. The verdict is open (see Section 5).

### 3.3 The overshoot method

Walking up to the UNSAT boundary one edge at a time pays a "threshold tax" every
step: in-class solve times exploded $130\,\text{s} \to 8631\,\text{s}$ over ~54
added edges (the 524-edge instance cost **2 CPU-hours** for one decisive solve).
The hard region is a **band** around the SAT/UNSAT threshold; solves on either
side are fast. The right algorithm therefore **jumps past the band** with free
(no-solve) blind safe-edge additions, then solves once on the cheap
overconstrained side, recovering minimality afterward with cheap UNSAT
re-checks. Empirically the band is **wide** (a +70-edge jump from 524 did not
clear it), so the current driver (`e14c`) uses +150 jumps with cheap
(1.5M-conflict) probes that return fast and trigger the next jump.

---

## 4. The solver-portfolio finding (the most concrete result)

On the **identical** 470-edge in-class instance:

| Solver | Verdict | Time |
|--------|---------|------|
| Cadical (CDCL, DRAT) | undecided | 12+ hours (killed) |
| MapleChrono (LRB + chronological backtracking) | SAT | 155 seconds |

A $\ge 280\times$ heuristic-dependent swing on one instance. This is the
heavy-tailed runtime behavior expected **at** a SAT phase boundary (Gomes-Selman):
early branching decisions can commit a solver to an exponentially large dead
region, and which solver wins is essentially a coin flip per instance.

**Consequence for the program.** This retroactively explains the h6
$510 \times 517$ instance abandoned as "SAT-intractable" after 66 Cadical-minutes
(L29/L30): it was very likely tractable for a different solver and was never
re-tried.

**Law.** Near-threshold $k$-colorability instances in this program must be run as
a solver **portfolio**, not a single solver:
- **Cadical** for the certificate-grade UNSAT proof of record (DRAT emission is
  its specialty);
- **MapleChrono / Glucose** for discovery (finding models, deciding hard SAT
  instances fast).

The 470-edge DIMACS is persisted under `_cache/e14_udg_class/` so the inversion
is reproducible.

---

## 5. What is open, and what would close it

The central E14 question is **undecided**. Three terminal outcomes, all
land-able:

1. **UNSAT** at some added-edge count: the first 6-chromatic graph in the
   UDG-necessary class ($K_4$-free + $K_{2,3}$-free). A shrink pass then
   minimizes it. This would make the phase-route gadget realizable-in-principle
   and is the prize. (It would still need an *explicit unit-distance embedding*
   to move $\chi(\mathbb{R}^2)$; in-class membership is necessary, not
   sufficient.)
2. **STUCK** (no safe edge placeable while still 5-colorable): the class caps
   below $\chi = 6$ from this seed, the UDG analog of $\chi(\mathbb{Q}^2) = 2$.
   A clean structural negative.
3. **Liquid to the cap** (reaches the edge budget still colorable): the class is
   surprisingly colorable and any witness is large, reframing the question.

The driver `e14c` runs to one of these unattended (it is self-limiting: budgets
cap every solve, `MAX_TOTAL` bounds the run, and it checkpoints every round).

---

## 6. Methodological lessons (transferable)

1. **Portfolio near the threshold.** One solver is a trap; the runtime swing is
   orders of magnitude. (Section 4.)
2. **Overshoot, don't walk.** The hard region is a band; jump past it with free
   edge additions and solve on the cheap side. (Section 3.3.)
3. **Generate inside the necessary class, not above it.** Manufacturing
   $K_4$-free 6-chromatic graphs and cutting down fails the codegree bound;
   enforce $K_{2,3}$-freeness as a hard invariant from the start. (Sections 2-3.)
4. **Checkpoint everything; harden the host.** The first overnight run died to
   machine sleep (froze the solver) plus a Windows auto-update reboot, not to
   anything mathematical. Disable sleep before unattended compute.

---

## 7. Honest bottom line

No bound on $\chi(\mathbb{R}^2)$ moved. The settled mathematical content is the
**codegree wall** (L63) and the **Folkman floor of 16** (literature). The
settled methodological content is the **portfolio law** (L64). The central
question E14 was built to answer is still open, and the reason it is hard to
answer is now understood to be SAT-solver strategy as much as mathematics.
