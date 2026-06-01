# Publishable Findings Assessment

Honest assessment of what this project has produced that could become a publication,
and what each candidate would need first. Written 2026-06-01.

**Read this first.** The headline is a negative: **nothing here moves the known
bounds.** $\chi(\mathbb{R}^2) \in [5,7]$ and $\chi_m(\mathbb{R}^2) \in [5,7]$ are
unchanged. There is no 6-chromatic unit-distance graph, no $\chi_m \geq 6$, no
improved upper bound, no resolution of any case of the problem. So there is no
"major theorem" result. Everything below is in the tier of structural/experimental
notes, a method-in-progress, or verification work.

**Provenance caveat.** Most of the findings below were produced by earlier agent
sessions (LEARNINGS L1-L34). They have NOT all been independently re-verified. The
measurable-moment thread (e3k-e3q, L39-L49) and the lineage forcing sweep (L45) WERE
built and cross-checked in the 2026-06-01 session (each new solver gated against an
independent reference: e3p/e3q vs e3n, the congruence reduction vs e3n+IEC). Treat
every other claim as "candidate, pending independent verification and a prior-art
check" until that work is done. The plane-chromatic
community (Soifer, de Grey, Heule, the Polymath16 participants, Oliveira-Vallentin,
Ambrus-Matolcsi) is small and sophisticated; several observations below may be
known to them. None should be claimed as novel without a literature check.

---

## Tier 1: plausibly publishable as a focused note

### F1. A structural explanation of why $\chi \geq 6$ has resisted post-2018 SAT search

**STATUS: pressure-tested 2026-06-01 (adversary, LEARNINGS L42). No break (no chi-6
UDG). Sharpened from a vague heuristic into a partly-rigorous mechanism plus a clean
open problem. The geometric obstruction turned out to be classical; the candidate
novelty narrowed to one reframing.** See `experiments/combinatorial/F1_pressure_test.md`.

**The claim.** The reason no 6-chromatic unit-distance graph has emerged from the
de Grey / Polymath16 / Heule lineage despite eight years of search is a specific
structural obstruction, not merely insufficient compute.

**The sharpened, partly-rigorous core (L42).** The single-hub chi-6 forcing route
reduces to one lemma:

> **Lemma (L).** Can 5 points cocircular at unit radius be rainbow-forced (forced to
> 5 distinct colors in every proper 5-coloring) in a unit-distance graph? If yes and
> it embeds, a hub at the circle center gives a chi-6 UDG; if no, the route is blocked.

For the lineage it provably fails, by a clean SAT-certified mechanism: **in $P_{510}$,
two vertices are forced-different in every proper 5-coloring if and only if they are
adjacent** (0/300 random non-adjacent pairs forced; 78/78 forced pairs in the
high-degree core are unit edges). So a rainbow-forced 5-set would be a unit-distance
$K_5$, which does not exist ($\omega = 3$); and cocircular points are mutually
non-adjacent except at 60-degree gaps (a sub-$C_6$, $\chi = 2$). Supporting: the max
cocircular-at-unit subset of $P_{510}$ is 36 (one vertex's neighborhood, vs the
abstract requirement 268); and a DOF count shows the abstract coupled chi-6 graphs
are over-determined by $\sim 5000$ equations in 3 unknowns, so non-realizability is a
counting fact, not a contingency. Smallest in-vitro gadget: the wheel $W_6$.

**The novelty problem (literature check).** The geometric obstruction (cocircularity:
a hub's unit-distance neighbors lie on its unit circle) is the CLASSICAL fact that
$K_{2,3}$ is a forbidden subgraph for unit-distance graphs (two unit circles meet in
at most two points; every graph on $\le 5$ vertices is a UDG iff it omits $K_4$ and
$K_{2,3}$). That is textbook, not a discovery. F1's only candidate novelty is the
**color-forcing-locality** observation: that chi-6 coupling needs LONG-RANGE color
forcing (non-adjacent forced-different pairs) and the lineage has only LOCAL forcing
(forced-different $=$ adjacent). Whether that reframing is itself new requires a
check against the Polymath16 threads.

**What it is NOT.** Not a theorem about all UDGs. The mechanism is proved for
$P_{510}$ and the triangular lattice only; the L28 graded (distributed-source)
rainbow route is closed only empirically plus the DOF count, not by theorem. One
L34 sentence ("realizability forces the even, low-concentration layout") was an
over-statement specific to rigid orbits and is retracted in L42.

**The genuinely useful output: a clean open problem.** Find a chi-5 unit-distance
graph with **long-range color forcing** (a non-adjacent pair forced-different in
every proper 5-coloring). That is exactly what a chi-6 coupling needs and exactly
what the lineage lacks. This is the right, falsifiable target, and is the most
publishable nugget here (a focused note: the reduction to Lemma (L), the
forced-different$=$adjacent fact for $P_{510}$, and the reframing).

**Venue.** Geombinatorics / experimental-mathematics note, IF the
forced-different-locality reframing survives a Polymath16 prior-art check.

### F2. Structural anatomy of the de Grey / Polymath / Heule $\chi \geq 5$ lineage

**The claim (LEARNINGS L15-L20).**
- No non-identity exact rotational symmetry survives SAT minimization (Polymath-510,
  Heule-826, de Grey-1585 all checked).
- The $\chi \geq 5$ obstruction is extremely DELOCALIZED: every reasonable
  structural reduction (cores, halves, bridge-touched subgraphs, up to 75% of the
  original) drops $\chi$ to 4 (L18).
- **Polymath-510 is de Grey-1585 translated and field-reduced**: 315/510 = 62% of
  Polymath vertices coincide with de Grey vertices under $T = (2,0)$ (L19). The
  Heule/Parts minimization reformulated de Grey rather than constructing a new graph.
- Every $\chi \geq 5$ graph in the lineage is "two $\chi$-4 halves + bridge edges"
  (L20).
- **No LONG-RANGE color forcing anywhere in the lineage (L45, this session).** Across
  all 12 accessible chi-5 UDGs (510, 517, 529, 553, 610, 633, 803, 826, 874, L403,
  S199, T721; $n$ from 199 to 874), a vertex pair is forced to differ in every proper
  5-coloring IF AND ONLY IF it is a unit-distance edge (0 exceptions, 0 indeterminate
  over $\sim$24000 merge-SAT tests). This upgrades the $P_{510}$ observation (L42) to
  a lineage-wide fact and sharpens the open problem: the chi-6 ingredient (a chi-5 UDG
  with a non-adjacent forced-different pair) is genuinely ABSENT from the known
  lineage and must be CONSTRUCTED by a new principle, not found by searching.

**What it would need.** Independent recomputation of the 62% overlap and the
reductions; a prior-art check against the Polymath16 project pages and Soifer's book
(the participants documented their constructions thoroughly, so some of this may be
known); rigorous statements. The L45 forcing sweep is independently reproducible
(`experiments/combinatorial/shotB_longrange_forcing.py`). Lower novelty than F1 and
higher folklore risk.

**Venue.** Same as F1; possibly folded into F1 as the "background structure" section.

---

## Tier 2: a novel method, but no result yet

### F3. A multi-class measurable moment relaxation as the un-capped route to $\chi_m \geq 6$

**The setup (LEARNINGS L37-L41; experiments e3k-e3n).** Single-class avoiding-set
density is PROVABLY capped at $\chi_m \geq 5$: Croft's construction gives
$m_1(\mathbb{R}^2) \geq 0.22936 > 1/5$, so $1/m_1 \leq 4.36$ and no improvement to
the density upper bound can reach 6. To pass 5 the argument must use the JOINT
structure of all color classes.

**What was built.** A Lasserre / moment hierarchy over the pairwise (and, at order
2, up to size-4) COLOR-MARGINALS of the distribution over proper $k$-colorings of a
configuration, with each per-color autocorrelation forced Bochner-positive and
vanishing at distance 1, AND a multi-class analog of the Ambrus 2023
inclusion-exclusion CONGRUENCE constraints. The key new ingredient is
**Formulation 2** (cross-color congruence: "red-next-to-blue" patterns coupled to
their isometric images), which is NOT covered by the $\alpha_1 = 1/4$ density cap.
The full stack (all validated against an independent reference or against each
other): e3k (formulation) $\to$ e3l (IEC sharpness) $\to$ e3m (degree-1 scalable
backend) $\to$ e3n (order-2, naive) $\to$ e3p (order-1 $S_k$-block-diagonalized,
L46) $\to$ e3q (order-2 $S_k$-block-diagonalized + $O(2)$-congruence variable
reduction, L47/L49).

**The symmetry reduction, completed and characterized (L44-L49, this session).** The
order-2 SDP is invariant under two groups, and BOTH reductions are now built and
proven correct (each reproduces the naive reference exactly, no fake certificate):
- $S_k$ (color relabeling) acts on the COLOR axis. It is lossless (L44) and block-
  diagonalizes the PSD into pieces whose size is INDEPENDENT of $k$ (L46/L47).
  Correct construction needed the Murota multiplicity-alignment, not the naive
  eigenbasis (the order-2 rep has irreps with multiplicity $>1$). Speedup 50-380x;
  e3q runs Moser order-2 in 6 s where the naive e3n OOMs at 25 GB.
- $O(2)$ (geometric congruence) acts on the VERTEX axis: congruent colored sub-
  configurations share a moment variable (L49, $\equiv$ the size-$\le4$ IEC done
  structurally).

**Honest status.** It has NOT produced a bound, and this session established WHY the
order-2 frontier on $X_{23}$ is hard in a precise, structural way. Degree-1 IEC on
$X_{23}$ $k=4$ gives margin 0 (L43): it carries IEC only to subset size 2, but the
single-class crossing of $1/4$ needed size 5, so degree-1 cannot even reproduce
$\chi_m \geq 5$. The order-2 lift carries IEC to size 4 and is the natural next
strength, but on $X_{23}$ it has $\sim98{,}627$ moment variables and PSD blocks up to
$\sim735$. The two symmetry reductions, though both correct, are TOGETHER
insufficient to make this fit a standard (dense-assembly) solver: $S_k$ shrinks the
blocks but not the variable count, and $O(2)$ shrinks the variables only $\sim2\times$
($98{,}627 \to 48{,}342$) because $X_{23}$ is geometrically generic at the 4-point
level (27 distinct distances, but distinct 4-point combinations). This is the honest
boundary of what symmetry buys.

**What it would need to be publishable.** Either (a) a CUSTOM SPARSE conic assembly
(the de Laat-Vallentin / DeCorte-Oliveira-Vallentin machinery never forms dense
affine maps) to run order-2 on $X_{23}$: $k=4$ to reproduce $\chi_m \geq 5$ from the
joint angle (a methods result), then $k=5$ as the open $\geq 6$ frontier; or (b) a
careful theoretical demonstration that Formulation 2 is strictly stronger than the
single-class cap, independent of a numerical bound. The infrastructure (a) needs is
now fully specified and de-risked: the two symmetry reductions are built and
validated, so only the sparse solver back-end remains. $X_{23}$ is also now tracked
(no longer a reproducibility debt).

**Venue (if it produces a bound).** A discrete-geometry / optimization venue
(Discrete & Computational Geometry, Mathematical Programming, Experimental Math).

---

## Tier 3: verification value, not novel mathematics

### F4. Self-certified reproduction of Ambrus 2023, $\chi_m(\mathbb{R}^2) \geq 5$
The repo reproduces $m_1(\mathbb{R}^2) \leq 0.246894 < 1/4$ using its OWN dual
certificate (the IEC congruence family re-derived in-repo), independent of the
paper's website-only dual coefficients (L35/L36). Useful verification; not new
mathematics. NOTE (resolved L43, this session): the 23-point input is now tracked at
`experiments/fractional/data/ambrus_23point_config.json` and loads from there, so
this is reproducible from a clean clone (the earlier reproducibility debt is closed).

### F5. Independent SAT re-verification of the lineage
cadical + glucose agree on UNSAT (non-4-colorability) for the de Grey 1585 and the
510/517/529/553/826 Polymath/Heule variants. Confirms the state of the art; not
novel.

### F6. Lean $\chi \geq 5$ bridge theorem
A machine-checked (no `sorry`) reduction: a graph hom into the plane unit-distance
graph plus non-4-colorability yields $5 \leq \chi(\mathbb{R}^2)$
(`lean/HadwigerNelson/DeGreyLowerBound.lean`). This is groundwork. A FINISHED
kernel-verified $\chi(\mathbb{R}^2) \geq 5$ (adding an LRAT-checked certificate and
a $\sim 2500$-edge exact embedding) WOULD be publishable (CPP / ITP), and would be
the first formal verification of the bound. It is not done.

---

## The bottom line and the recommended path

The single most write-up-worthy item is **F1**: the cocircularity / wrong-shape-bridge
explanation of the $\chi \geq 6$ barrier. It is concrete, non-obvious, and explains a
real phenomenon, and it is the closest to a self-contained story.

Before any of this is publishable, three things are owed:
1. **Independent re-verification** of the earlier-session computations (only e3l-e3n
   were re-run this session).
2. **A literature / prior-art check** against Polymath16, Soifer, Ambrus-Matolcsi,
   and Oliveira-Vallentin, to confirm novelty.
3. **Rigor**: converting heuristic observations (especially the F1 "concentration"
   barrier) into falsifiable statements, and either proving a restricted case or
   framing honestly as experimental.

**Recommended next step.** F1 has now been pressure-tested (L42, no break, sharpened
to a classical obstruction plus one reframing). The two live, precisely-scoped open
directions are: (i) for the measurable route F3, build the custom sparse conic solver
that the (now complete and validated) symmetry reductions feed, to run order-2 on
$X_{23}$ and test $\chi_m \geq 5/6$ from the joint angle; (ii) for the integer route,
attempt to CONSTRUCT a chi-5 UDG with long-range color forcing (L45 showed none exist
in the known lineage). Both are research-grade; neither is a quick win. The most
publishable SHORT item remains F1 (with a Polymath16 prior-art check). The honest
meta-finding of the 2026-06-01 session: the measurable order-2 attack is reduced to
one well-defined engineering problem (sparse SDP at $X_{23}$ scale), and symmetry
alone provably will not crack it.

---

## Verification debt ledger

| Finding | Re-verified this session? | Prior-art checked? | Rigorous statement? |
|---|---|---|---|
| F1 cocircularity barrier | Yes (L42 adversary) | Partial (cocircularity = classical $K_{2,3}$; reframing unchecked) | Partial (Lemma L + $P_{510}$ locality rigorous; "all UDGs" heuristic) |
| F2 lineage anatomy | No | No | Partial |
| F3 multi-class moment LP | Yes (e3l-e3n) | No | Valid relaxation, no bound |
| F4 Ambrus reproduction | No (input missing) | N/A (reproduction) | Yes |
| F5 SAT re-verification | No | N/A | Yes |
| F6 Lean bridge theorem | No | N/A | Yes (but incomplete goal) |
