# Next experiments (proposed 2026-06-09, post L58/L59)

All runnable locally on the existing stack (python-sat/cadical, sympy exact arithmetic, networkx, cvxpy; no C compiler). Ranked by expected information per unit cost. Source material: LEARNINGS L58/L59 and the cached lens dossier (`orchestrator_sessions/_tmp_lens_material/COMPACT_DOSSIER.txt`).

Standing rule from L59: candidate generation must PRESERVE chi-redundancy (never SAT-minimize), and every forcing sweep should pre-filter with the $O(n)$ criticality scan (`critscan_lineage.py` pattern), since only chi-redundant vertices can host forced pairs.

## STATUS (updated 2026-06-09 after first runs)

- **E0 DONE**: shotD 874 finished; L57 closed at 12/12 (2,309,264 pairs, all free).
- **E1 DONE, POSITIVE (L60)**: 693 abstract equality-alternators in M^3(C5), one independently verified. The phase object exists.
- **E3 DONE, NEGATIVE-as-predicted (L60)**: Z6 necklace of P510 is 5-SAT; lineage graphs have no phase to close on.
- **E1b DONE (L61)**: minimizing all 693 alternators is VACUOUS (all stay 47 vtx) because a 6-critical host is irreducible; min alternator order = min K4-free 6-critical order (same bottleneck as the clamp). ~1/3 carry a pair-swap involution (built-in congruence). M^3(C5) is triangle-free (omega=2) = worst realizability substrate.
- **E12 DONE, NEGATIVE (L62)**: born-realized alternator ABSENT from all 9 chi-5 lineage graphs (top-60 core, 500-coloring sampling filter); no two-edge forcing. Route 2 (free object from the lineage) is dead.
- **NEW TOP PRIORITY -> route 1**: build/obtain a small omega=3 (triangle-RICH, K4-free) 6-critical graph as a realizable alternator/clamp host. Triangles = rigid unit rhombi/spindles, so this is both smaller than 47 and far more UDG-friendly. No nauty on this host, so the source must be a construction: Hajos/Ore merges of small chi-5 unit-distance pieces (Moser spindles), or the repo's h5/h6 lineage. Then build alternators/clamps on it and attempt exact (Groebner if <= 14) or numeric (L52 embedder) realization.

## E0. shotD graph 874 (DONE)

Closed L57 at 12/12, all free.

## Tier 1: cheap gates on the headline route (hours each)

### E1. Abstract Equality-Alternator existence (gates the whole phase-gadget route)
New script `combinatorial/e9_alternator_abstract.py`. Three stages sharing a phase-detector core (extendable-core pruning of the interface transfer relation, BFS Z-labeling, period $p$ = gcd of closed-walk discrepancies; pure networkx, exact):
1. CONTROLS (minutes, soundness): unit-edge chain at $k=2$ must give $p=2$; triangle strip at $k=3$ must give $p=3$; 3-rail ladder $p=1$; single-port $J{-}I$ chain at $k=5$ must give $p=1$ (L55 monoid); and the $k=7$ control: ANY stealth $p\ge2$ at $k=7$ contradicts the hex coloring and flags a bug.
2. M3(C5) double-merge sweep (minutes): over all ~25k pairs of independent edges of the 47-vtx Mycielski tower, merge both endpoint pairs and 5-SAT; any UNSAT is an abstract Z/2 "flipper slice" witness.
3. Small-cell enumeration: abstract cells (graph $F$ on $\le 8$-10 vtx, arbitrary cross relation), ask whether ANY has every recurrent SCC of the 5-color transfer digraph with period $\ge 2$.
Decision semantics: a witness means the phase route has an object to chase (then realizability becomes the question, but with NO cocircularity clamp equations). A clean negative at small $n$ bounds the object's size from below and redirects to wider interfaces.

### E2. Rich-center rainbow scan on P510 (Theorem R in its native form; never tested)
New script `combinatorial/rich_center_scan.py`. L45/L56/L57 scanned only pairs of EXISTING vertices; the clamp endpoints $s,t$ are NEW points at circle centers. (1) Enumerate non-vertex intersection points of unit circles around vertex pairs (numpy prefilter, mpmath 50-digit confirm, sympy exact on collisions); keep centers with $\ge 6$ unit-incident vertices ($\ge6$ floor is rigorous: a rainbow-forced 5-set of vertices would contradict L57 or $\omega=3$). (2) One cadical query per center by $S_5$ symmetry: forbid color 5 on the circle section; UNSAT $\Rightarrow$ an explicit $\|V\|{+}1$-vertex 6-chromatic UDG, immediately. (3) Two-circle pair pass for clamp certificates (forbid color 4 on $A$, color 5 on $B$). Use P510 first (NOT S199; erratum L58). ~2-4 h.

### E3. Necklace closure probe Z6(P510) (single SAT call first)
Build the exact union of $\rho_{\pi/3}^j(P_{510})$, $j=0..5$, about the origin with all cross-band unit edges detected exactly in sympy (reuse `h7b_orbit_coupling.py` code paths; band-1/band-2 cross-richness already verified there), then ONE cadical 5-SAT call (+ glucose dual-confirm if UNSAT). Minutes. SAT is the expected outcome and stages the follow-up: resonance census (angles serving many cross pairs at once, exact two-circle solve) and the diagonal kill screen, per the L58 dichotomy.

### E4. Twist spectroscopy of the chi-5 nine
New script `combinatorial/twist_spectroscopy.py`. For each graph: extract the exact geometric symmetry group of the embedding (centroid + same-radius candidate isometries, certified in sympy); for each non-identity $\sigma$ with no orbit-internal adjacency, merge color variables along $\sigma$-orbits and 5-SAT (also the $c\circ\sigma = \pi\circ c$ variants over cycle-type-compatible $\pi$). A sector imposing $\sim n$ simultaneous equalities that L57 never touched; any UNSAT is the first global forcing in the lineage AND a necklace seed. Hours.

## Tier 2: graded searches and new sectors (overnight scale)

### E5. Width-2 7-bit profile machinery
(a) Profile sweep: classify pairs of disjoint unit edges in P510's high-degree core by which of the 7 $S_5$-orbital patterns (e, s, Oac, Oad, Obc, Obd, dis) are realized (7 incremental SAT probes per pair). Any missing bit is a candidate for the verified D4 stacking theorem (a 5-colorable $K_4$-free plus-framed gadget with dis present, one overlap + one transporter bit missing, stacks to a realizable clamp; fail-safe under collisions). (b) Abstract existence FIRST: SAT/enumeration hunt for such a $K_4$-free gadget at $n\le25$ (adversary exhibited $n=11$ witnesses at $k=4$; the $k=5$ $K_4$-free case is the gate). The 0-7 deficiency fitness is the first GRADED search signal the integer thread has had.

### E6. Toroidal sector (Aperiodic Chromatic Rigidity, both directions)
(a) `combinatorial/toroidal_wrap_sweep.py`: rank-1 quotients $G/\mathbb{Z}v$ with wrap edges over non-adjacent pairs of 510/517 (loop-free pairs only); 5-SAT each quotient; forcing invisible to single contractions. (b) Torus 6-coloring SAT: conservative cell discretization of small flat tori (cells conflict iff Minkowski difference meets the unit circle mod $L$); a SAT 6-coloring REFUTES Aperiodic Chromatic Rigidity and is the first doubly periodic 6-coloring; growing UNSAT resolution evidence supports it.

## Tier 3: measurable-thread workarounds (day-scale builds, cvxpy only)

### E7. Per-apex-color SE(2) spin blocks
`measurable/e2d_se2_spin_triangle_sdp.py` with the L58 correction: matrix-Herglotz blocks PER apex color (the apex-summed version provably collapses to the e3c/L9 LP at 3.72). Near-LP scale after $S_k$ reduction. Question: does the first genuinely 3-point noncommutative constraint move the 2-point ceiling (3.4829) / triangle LP (3.72)? Includes the sanity ladder (drop spin blocks => reproduce L6/L9 values).

### E8. Dual-lattice periodic order-2 SDP
$L$-periodic measurable colorings have Fourier support on $L^*$: the blocked 48342-variable order-2 system collapses to $O(10^3)$ lattice variables. Build for square/hex/one quadratic-irrational lattice, reuse the $S_k$ reduction + $J_0$ kernel. Infeasibility at 6 classes = "no $L$-periodic measurable 6-coloring", a new theorem AND the first live exercise of the blocked order-2 machinery.

## Tier 4: generation pipeline (continuous background)

### E9. Redundancy-preserving chi-5 generator
Generate UN-minimized chi-5 candidates born-realized (two-copy coincidence-wall unions of P510, $C_6$/$C_3$ closures, exact ring patches with foreign split-prime rotations); gate each with (i) 5-chromatic, (ii) criticality scan (keep only graphs WITH redundant vertices), then run forcing tests ONLY at redundant vertices. This is the L59-corrected version of every previous outside-lineage search. Caveat L51: redundancy is necessary, not sufficient.

## Suggested order

E0 (running) -> E1 + E3 (same day, both gate the phase route) -> E2 -> E4 -> E5(b) abstract gadget hunt -> E6(b) torus SAT -> E7/E8 as the measurable track in parallel -> E9 as standing background. Decision point after E1-E4: if all four come back negative/SAT-everywhere, the lineage is closed in every known sector and ALL budget moves to generation (E9) plus the measurable track.
