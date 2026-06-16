# TODO

Task tracker for the Hadwiger-Nelson research repo.

## Bootstrap (scaffold landed 2026-05-25)

- [x] Write `docs/00_intuitive/what_is_the_problem.md` accessible exposition
- [x] Write `docs/01_undergraduate/moser_spindle.md` first chi >= 4 proof
- [x] Write `docs/01_undergraduate/hexagonal_upper_bound.md` Isbell tiling
- [x] Implement `experiments/_shared/unit_distance_graph.py` core UDG class
- [x] Implement `experiments/_shared/wrong_approach_detectors.py` Q^2 + L-infinity controls
- [x] Implement `experiments/_shared/smoke_test.py` sanity check on Moser spindle and small UDGs
- [x] Write `experiments/combinatorial/e1a_moser_spindle.py` verify chi(Moser) = 4 via SAT (cadical195 + glucose4 agree)
- [x] Write `experiments/combinatorial/e1b_de_grey_skeleton.py` cadical195 + glucose4 agree on UNSAT for 510 / 517 / 529 / 553 / 826 / 1585 (the original de Grey 2018 graph)

## Architecture 1: Combinatorial / UDG

- [x] Survey: Polymath16 chronology and current smallest 5-chromatic UDG (dossier at `docs/research_atlas/arch1_sat_lineage.md`)
- [x] Reproduce: SAT-verify de Grey's lineage at 510 / 517 / 529 / 553 / 826 / 1585 vertices (multi-solver agreement, LEARNINGS L3)
- [ ] Explore: targeted constructions toward chi = 6 (Heule-style)
- [x] Field-extension orbit-search framework (e1d) for chi >= 6 via alternate ring extensions
  - [x] Tested 6 alternate rings {Q(sqrt p) : p = 7, 19, 23, 27, 31, 39} with Moser-spindle seed at orbit size 3-6
  - [x] Naive orbit-only search NEGATIVE: rotations don't auto-bind copies (LEARNINGS L11)
  - [x] Binding-rotation enumeration for Moser in Q(sqrt 3, sqrt 11): 16 single, 62 double, 4 triple bindings; full 62-stack is 211-vertex, density 3.46, chi = 4 (e1e/e1f/e1g, LEARNINGS L14)
  - [ ] Repeat binding-rotation enumeration in enriched fields Q(sqrt 3, sqrt 11, sqrt p) for small primes p
- [x] Document SAT encoding conventions and reproducibility (e1a/e1b scripts + cache certificates)
- [x] Reverse-engineer Polymath 510 and de Grey 1585 (e1i-e1t)
  - [x] Polymath 510 has approximate C_6 about origin (92% coverage); C_6 closure is C_6-irreducible at 1155v / chi=5 (e1i/e1j/e1k, LEARNINGS L15)
  - [x] de Grey 1585's natural center is v_0 = (2, 0), approximate D_6 symmetry (~50% coverage per element) (e1l/e1m, LEARNINGS L16)
  - [x] de Grey 1585's chi = 5 obstruction is a three-component coupling: 778v core (chi 4) + 807v asymmetric (chi 4) + 155 bridges (e1n/e1o/e1p/e1q, LEARNINGS L17)
  - [x] de Grey 1585 obstruction is extremely delocalized: every reasonable structural reduction drops chi to 4 (e1r, LEARNINGS L18)
  - [x] Polymath 510 is essentially a translated substructure of de Grey 1585 (62% vertex overlap under T = (2, 0)) (e1s, LEARNINGS L19)
  - [x] Universal "two 4-chromatic halves + bridges" pattern: same mechanism in de Grey 1585 (778+807+155) and Polymath 510 (315+195+833) (e1t, LEARNINGS L20)
  - [x] Covering lemma: chi(H_1 + H_2 + B) >= 5 iff B is a set cover of the 4-coloring product (e1v, LEARNINGS L21)
  - [x] List-coloring reformulation: chi >= 5 iff H_2 not list-colorable from L(v) = [4] \ F(v) (e1w, LEARNINGS L22)
  - [x] L21's 14-vertex Moser² no-K_4 abstract chi-5 graph is NOT UDG-realizable (e1x numerical + h2 Positivstellensatz, LEARNINGS L23)
  - [x] Triple-coupling theorem for chi >= 6 lifts L22 to three halves (e1y, LEARNINGS L24)
  - [x] Four obstruction classes catalogued: W5² 12v adjacent-singleton, W5×Moser global, Moser² empty-list, W5×Golomb sparse-singleton (h3, LEARNINGS L25)
  - [x] Polymath 510 vertex-critical for chi >= 5: all 510 single-removals are 4-colorable (h1 Phase 1, LEARNINGS L26)
  - [ ] Complete H1 Phase 2 pair sweep: resume h1_parts_shave.py from index 56,500 (~2 hours; checkpointed)
  - [x] Polymath 510 × Polymath 510 + no-K_4 bridges: FIRST no-K_4 chi >= 6 abstract graph found at 1020 vertices, 2700 bridges, triple-solver SAT verified (h5, LEARNINGS L27); not UDG-realizable due to L23-style cocircularity at scale across all 97 saturating vertices
  - [x] Binary-search bridge minimum for L27: tightened to |B| <= 2000 (700-bridge reduction, 26%); bracket now (1500, 2000]; obstruction class shifts from "97 always-saturating" to "43 always-saturating + 54 graded rainbow" (h6, LEARNINGS L28); F-profile correction to L27 (multi-modal, not bimodal)
  - [ ] Tighten bracket to (1500, 2000]: probe K=1750, 1850, 1900 with Cadical 60min + Glucose fallback; expected 1-2h per probe
  - [ ] Exhaustive Stage 2 local one-bridge search at K=2000 (~2000 trials, 5-min Cadical each, ~1-2 days)
  - [x] Refute R5 / R5' as stated (C_5 counterexample at k=3, U={v0,v2,v4}); both are false. The chi-6 forcing at P_510² is L24 applied to Polymath 510's specific algebraic embedding, not a clean rainbow-forcing or Hall-matching lemma
  - [ ] Find the correct structural primitive replacing R5 / R5': characterize bridge structures B between two chi-5 vertex-critical UDG halves under which L24 list-coloring infeasibility is realized in Q(sqrt 3, sqrt 11)
  - [ ] Glucose / Minisat verification at K=2000 to match L27 triple-solver standard
  - [ ] Smaller chi-6 abstract via mixed halves: try P_510 × P_517 + bridges (V=1027 marginally smaller), or P_510 + Moser + B via L24 triple form
  - [x] R5 rainbow-forcing conjecture (every chi-k vertex-critical graph forces rainbow on U with V\U inducing chi-(k-1)) REFUTED by C_5 counterexample at k=3, U={v_0, v_2, v_4}; proper 3-coloring (1,2,1,2,3) has c(U)={1,3} missing color 2. The Polymath 510 empirical rainbow is a consequence of L24 list-coloring infeasibility plus Polymath 510's specific algebraic structure, not a vertex-criticality + pigeonhole theorem.
  - [x] Coordinate-first realizable couplings (h7/h7b/h7c/h7d): up to 13,757 genuine unit-distance bridges, all 5-colorable; barrier sharpened to "realizable bridges are the wrong shape for chi-6" (L34)
  - [x] Adversarial pressure-test of the cocircularity barrier (F1): no chi-6 UDG; reduced to Lemma (L) "can 5 cocircular-at-unit points be rainbow-forced?" (no: needs unit-distance K_5); in P_510 forced-different = adjacent; cocircularity = classical K_{2,3}-freeness (f1pt_*.py, F1_pressure_test.md, L42)
  - [x] Shot-2 redirect (from L42): swept all 12 accessible chi-5 UDGs (510-874, L403, S199, T721) for LONG-RANGE color forcing -- NONE exist; forced-different = adjacent lineage-wide (shotB_longrange_forcing, L45)
  - [ ] Shot-2 follow-up (from L45): CONSTRUCT (not search) a chi-5 UDG with a non-adjacent forced-different pair -- the missing chi-6 ingredient, absent from the known lineage by a new-principle gap
  - [ ] Polymath16 prior-art check on the "long-range color forcing" reframing (is forced-different=adjacent for de Grey-lineage graphs already known?)
  - [ ] Cocircularity-softened UDG construction for L27: replace each obstructed bridge with 2-hop softening to estimate actual minimum chi-6 UDG vertex count
  - [ ] Search for 7-vertex 4-chromatic UDG distinct from Moser spindle (would re-open the 14v UDG chi-5 route; L25 future direction 1)
  - [ ] Pair Moser with 8-9-vertex UDGs from e1l (chain/pivot constructions); test no-K_4 chi-5 minima
  - [ ] Apply same-j linear-difference trick (h2) to de Grey 1585 and Polymath 510 bridges as a structural rank check
  - [ ] Lean formalization of the h2 Positivstellensatz certificate (`moser14_not_udg` theorem)
  - [ ] Investigate Haugstrup's R^4 600-cell / 120-cell construction (Polymath16 18th thread Jan 2026); extract graph, run L25 obstruction analysis
  - [ ] **Wildcard A (monotile/substitution forcing, from L54)**: hat/spectre matching rules as a SCAFFOLD that manufactures long-range forcing (the L45 gap). Build a hat metatile in Q(sqrt 3) via the UDG interface, attach a per-tile chi-5 gadget whose 5-colorings are in bijection with a 2-3 state tile label, SAT-check that matching-rule constraints force label-propagation, then test L51's contraction-UNSAT on the forced NON-adjacent pair and whether Theorem R cocircularity holds automatically from the rigid tile geometry. Runnable now (existing UDG + python-sat). Highest-leverage probe: could exhibit the first long-range forcing in the plane without compiler-gated nauty
  - [x] **Wildcard B (renormalized clamp, from L54)**: DONE (`combinatorial/wildcard_b_rg_transfer.py`, LEARNINGS L55). Corrected the brainstorm: $\lambda_1$ is coloring-entropy, NOT forcing; the diagnostic is imprimitivity / spectral gap. Result: color-symmetry ($S_k$ 2-transitivity) confines single-vertex-port relations to the primitive monoid $\{0,I,J{-}I,J\}$, RG/substitution conserves but cannot create imprimitivity, so the clamp FACTORS into (i) forced-same under $\omega\le3$ or (ii) a wide $\ge2$-vertex separator $=$ Theorem R's degree-$\ge5$ split. C_5 calibration reproduces L45/R5.
  - [x] **L55 follow-up (i)**: DONE, NEGATIVE on the realizable lineage (`combinatorial/shotC_forced_same.py`, LEARNINGS L56). Forced-same sweep (dual of L45) finds ZERO non-adjacent forced-same pairs across all 12 chi-5 UDGs (~22.5k pairs, 0 indeterminate); with L45, non-adjacent pairs are completely unforced. Splice lemma (forced-same + unit edge => clamp => chi>=6) verified exactly. The open object is still a NEW chi-5 UDG outside the lineage
  - [x] **Exhaustive forcing classification (shot D)**: DONE 11/12 (874 finishing) (`combinatorial/shotD_exhaustive_forcing.py`, LEARNINGS L57). EVERY non-adjacent pair classified (not sampled): ~2.29M pairs, ALL free, 0 forced, 0 indeterminate, 0 hits. Exhaustive upgrade of L45+L56 -- no long-range forcing anywhere in the lineage
  - [ ] **L55 follow-up (ii)** (the remaining combinatorial route): smallest WIDE-interface ($\ge2$-vertex separator) gadget whose boundary-coloring transfer matrix is imprimitive AND W3-realizable = Theorem R's degree-$\ge5$ split; the monotile (Wildcard A) is a candidate substrate
  - [ ] **L55 follow-up (ii)**: smallest WIDE-interface ($\ge2$-vertex separator) gadget whose boundary-coloring transfer matrix is imprimitive (escapes the monoid) AND is W3-realizable. This is Theorem R's degree-$\ge5$ split restated as a transfer-matrix target; reframes Wildcard A's monotile gadget search

### The W3 wall, exhausted, then the codegree wall (L51-L65)

- [x] Abstract clamp EXISTS as a one-move vertex-split of a $K_4$-free 6-critical graph; 48-vtx triangle-free SAT-verified witness; obstruction relocated entirely onto W3 (lrf_abstract_clamp, L51)
- [x] W3 not decidable by DOF/degree counting; reduced to algebraic cocircularity (Theorem R: clamp realizable iff $H-w$ realizes with $N(w)$ split on two unit circles) (L52-L53)
- [x] Backward-from-2050 synthesis: most-likely terminal answer $\chi=6$ by a finite UDG; linchpin = the W3-realizable clamp (L54)
- [x] Clamp question FACTORS via $S_k$ color-symmetry monoid $\{0,I,J{-}I,J\}$ into (i) forced-same gadget or (ii) wide-interface split (wildcard_b_rg_transfer, L55)
- [x] Forced-same sweep NEGATIVE across the lineage (shotC, L56); EXHAUSTIVE forcing census: all ~2.29M non-adjacent pairs FREE (shotD, L57)
- [x] Essential-Pair Lemma (= Martin 2009 Thm 3.17): vertex-critical chi-5 graphs host no forced pair; all 9 lineage graphs vertex-critical, so forcing-sterile BY CONSTRUCTION (critscan_lineage, L58-L59)
- [x] Phase-gadget / equality-alternator route: abstract object EXISTS (e9, L60) but absent from the realizable lineage and needs a new host (e10-e12, L61-L62)
- [x] Host factory (nauty-free Mycielski towers): K4-free 6-critical hosts down to 18 vtx, alternator-abundant; but the CODEGREE WALL ($K_{2,3}$-free $\Rightarrow m \le n(1+\sqrt{8n-7})/4$) excludes every manufactured host (e13/e13b, L63); Folkman floor = 16 (literature)
- [x] E14: generate INSIDE the both-free class from $P_{510}$; the class is LIQUID (674 codegree-safe edges added, still 5-colorable); PORTFOLIO finding Cadical 12h vs Maple 155s (L64) -- **VERDICT STILL OPEN (e14c running)**
- [x] E15: greedy in-class growth caps at $\chi=4$ across $n=17$-64 (greedy limit, not non-existence); drove by the from-scratch hn_solver (L65)
- [x] Tooling: `_shared/portfolio_sat.py` (parallel-process SAT portfolio), `combinatorial/chromatic_lifter.py` (overshoot + invariants), `_shared/hn_solver.py` (from-scratch structure-first solver + benchmark); white paper `docs/03_research/hn_solver_whitepaper.md`
- [x] Geombinatorics-style paper draft `paper/main.tex` (compiles clean, census total corrected to 1,955,948 = nine chi-5 graphs)
- [ ] **E14 verdict**: let e14c overshoot resolve to UNSAT (first in-class chi-6 graph), STUCK (class caps below 6 from this seed), or the edge budget
- [x] **E15b annealing** (L67): local search (add+remove codegree-safe edges) over the both-free class, $n=26$-40, 19,330 restarts / 8 h under PyPy. Reaches in-class $\chi=5$ down to $n=29$ ($m=98$, portfolio-verified, `combinatorial/e15b_chi5_n29.json`) but NEVER $\chi=6$; density plateaus at ~0.84 of the codegree ceiling. Greedy$\to\chi4$ (L65), annealing$\to\chi5$, $\chi6$ resists. Heuristic negative, not non-existence
- [x] **E15-v2 / top-down repair** (L69): seed $M^3(C_5)$ ($\chi=6$, 6-critical), descend on codegree excess holding $\chi\ge6$ hard (forced-same paired rewires escape the criticality trap, pure removes sparsify). Drives excess $1068\to359$ ($-66\%$), $m\,236\to164$, to a portfolio-verified $K_4$-free $\chi=6$ floor (`e16_repair_floor.json`) that still has 166 codegree violations, then GENUINELY STALLS. Trade-rewires (denser min $\sim$460) and vertex-split growth do not break it. Third heuristic negative (greedy-up$\to\chi4$ L65, anneal-up$\to\chi5$ L67, repair-down$\to$stall): the $K_{2,3}$ violations are load-bearing for $\chi=6$ (L63 codegree wall, from the inside). Scripts `combinatorial/e16_topdown_repair.py`, `e16_verify_floor.py`
- [x] **E16 follow-up (sparsify, L69 addendum)**: added the $\chi$-preserving SPARSIFICATION operator (`try_sparsify`, `E16_SPARSIFY=1`). It strips the $m=164$ floor to $m=131$ = the Kostochka-Yancey 6-critical floor with excess PINNED at 359 (reduced by zero): the $K_{2,3}$ violations live entirely in the 6-critical core, so sparsification provably cannot reach in-class. Committed artifact `e16_repair_floor.json` is the $m=131$ edge-critical $K_4$-free $\chi=6$ graph (166 violations)
- [ ] **E16 remaining door (blocked on nauty)**: a NON-Mycielski sparse $\chi=6$ seed, or genuinely larger $n$ (codegree ceiling $\sim0.7n^{1.5}$ outruns the KY floor $2.8n$, so $K_{2,3}$-free 6-critical cores must exist eventually). Sourcing a sparse 6-critical graph outside the Mycielski family needs nauty, which does not install on this host (no compiler) -- so Arch-1 in-class search is blocked here; higher-leverage next moves are Arch-3 (LP plateau-break) or Arch-2 (sparse conic backend)
- [x] **hn_solver clause learning** (L66): CBJ + nogood learning in `_shared/hn_solver_cdcl.py`, validated correct. Backjumping is the real win (~15x vs MRV on $M^3$); nogoods cut nodes 6.3x but wall-time payoff is gated on watched literals. PyPy 3.11 adds 5.0x free; $M^3$ now ~78x faster than the old solver, all in Python. $M^4(C_5)$ k=6 still does not finish (node-count-bound)
- [ ] **hn_solver watched-literal nogood propagation**: O(1) nogood checks instead of the current linear scan, so learning's 6.3x node reduction pays off in wall time; the lever needed before $M^4$ is reachable in Python (then optionally a Rust/PyO3 core, NOT C; GPU is the wrong tool)
- [ ] **hn_solver as portfolio front-end**: run it with a small node budget first (resolves the structured-easy majority instantly), hand the hard residue to the CDCL portfolio
- [ ] **PyPy deployment**: run pure-Python solver-heavy experiments (E15-style) under PyPy (~5x); keep pysat-dependent work (portfolio, census) on CPython. PyPy path + caveats saved in project memory
- [x] **Paper finishing pass** (commit 1843e37): author block (Owen Kent), acknowledgments, folded in L69 (codegree violations intrinsic to the 6-critical core) + three-direction outlook; compiles clean (10 pp, 0 undefined refs/citations). Submission-ready draft `paper/main.tex`
- [x] **Bibliography verified** (web-checked June 2026): deGrey Geombinatorics 28(1):18-31, KostochkaYancey JCTB 109:73-101, Woodall JCTA 14:187-200, Spencer-Szemeredi-Trotter (Bollobas ed.) 293-303 all CONFIRMED. CORRECTED: Folkman value F_v(2,2,2,2,2;4)=16 now cited to its PRIMARY source Lathrop-Radziszowski JCMCC 78:119-128 (2011), not the mis-cited Xu-Liang-Radziszowski; the 510-vertex graph now cites Parts 2020 Geombinatorics 29(3):137-166; "Paley-type" descriptor of the witnesses removed (wrong; 16 is not a Paley order) and replaced with the complementary-pair density argument (m+m_bar=120 => ~60 each > ceiling 48)
- [ ] **Before submission (remaining)**: CONFIRM author name/affiliation (currently inferred "Owen Kent" from git/email); decide Geombinatorics submission

## Architecture 2: Measurable / spectral

- [x] Survey: Falconer 1981 proof of chi_m >= 5; consolidated measurable frontier (chi_m >= 5 best known, >= 6 OPEN; "do >= 6" citations are misattributions) (L31; atlas arch2_measurable.md)
- [x] Falconer autocorrelation illustration (e2a) + OFV 2-point Bessel SDP/LP reproduced & cross-validated, 3-point no gain (e2b, L32)
- [x] Falconer chi_m >= 5 decomposed; gated on the same missing rigid 5-chromatic UDG as Arch 1 (e2c, L33)
- [x] Single-class density PROVABLY capped at chi_m >= 5 (Croft floor 0.22936 > 1/5); >= 6 needs a JOINT argument (L37)
- [x] Multi-class (joint k-coloring) measurable moment LP, the one un-capped route to chi_m >= 6:
  - [x] Formulation + enumeration prototype (e3k, L38); Formulation-1/2 cross-color IEC "sharpness" layer (e3l, L39)
  - [x] Degree-1 scalable moment backend (never enumerates colorings), validated (e3m, L40)
  - [x] Order-2 Lasserre lift (IEC up to subset size 4), correct but naive build does not scale (e3n, L41)
  - [x] Restore + TRACK the Ambrus X_23 config (now at `experiments/fractional/data/`); run degree-1 IEC on X_23 k=4 -> margin 0, provably too weak (carries IEC only to size 2) (L43)
  - [x] Lossless S_k color-symmetrization, proved + validated (e3m `symmetrize`, shotA_symmetry_validation, L44)
  - [x] S_k-block-diagonalized order-1 SDP, reproduces e3m exactly, PSD side 1+nk -> n (e3p, L46)
  - [x] S_k-block-diagonalized order-2 SDP (Murota multiplicity alignment), reproduces e3n exactly, runs Moser where e3n OOMs (e3q, L47)
  - [x] O(2)-congruence variable reduction (== size-<=4 IEC, structurally), validated (e3q `congruence_reduce`, L49)
  - [x] Probe: order-2 never strictly beats order-1 at runnable scale -> no shortcut to validate the lift (intermediate_probe, L50)
  - [x] **Blocker diagnosis (L70, e3r)**: both shortcuts ruled out. $X_{23}$ has TRIVIAL geometric symmetry ($\|\mathrm{Aut}\|=1$, beam-search-found, asymmetric) so blocks cannot shrink below the $S_k$ size (~735); the $S_k$-reduced affine map is 100% DENSE (Murota basis $F$ dense, $C_o=F^\top E_o F$ full), so a `scipy.sparse` assembly is ~292 GiB > the ~195 GiB dense largest block. Probe `fractional/e3r_order2_sparsity_probe.py`
  - [x] **Matrix-free operator BUILT + validated (L70 addendum, e3s)**: forward $A$ (form $M(y)$ $D\times D$ from orbit incidence, project $C_{\text{block}}=\frac1d\sum_l P_l M P_l^\top$) and adjoint $A^\top$ ($D\times D$ intermediate $W$, reduce over orbit incidence), reproducing e3q's dense map to $\le1.4\mathrm{e}{-13}$ (forward + adjoint identity) on triangle/rhombus/Moser. Footprint $O(D^2)$: ~294 MB at X_23 vs ~195 GiB dense (~680x) -- the RAM wall is GONE. Script `fractional/e3s_order2_operator.py`
  - [x] **Matrix-free SOLVER built + validated (L71, e3u)**: linearized (proximal) ADMM wrapping e3s -- split the PSD (4 eigen-projections), gradient step via `apply_AT`, sparse x-update QP (no PSD). Validated vs e3q dense margins 3/3 (rhombus k=4 feasible prim->1e-7; Moser k=3 certifies prim plateaus 0.278; Moser k=4 feasible prim->6e-6). Certificate = infeasibility of {PSD+NORM+MARG}, seen as the primal residual not closing. Script `fractional/e3u_order2_solver.py`
  - [x] **k=4 == k=5 size collapse (e3t)**: X_23 order-2 reduces to n_orb=48342 / 4 blocks / max 735 for BOTH k (congruence classes of size-<=4 subsets saturate at k=4). So the chi_m>=6 frontier (k=5) costs the same as the chi_m>=5 validation (k=4)
  - [x] **OSQP-cached x-update** (done): cvxpy OOMs at X_23 (35 GiB DPP canonicalization); replaced with OSQP-direct (constant P,A factorized once, q updated per iter, warm-start). Re-validated 3/3, ~2x faster
  - [x] **X_23 k=4 VERDICT (L72): FEASIBLE** -- order-2 does NOT certify chi_m>=5 at k=4 (matrix-free run, 5120 iters/5.4h; margin 1.24->0.0021 monotone, no plateau). By color-monotonicity k=4 feasible => k=5 feasible => order-2 cannot certify chi_m>=6. **The order-2 measurable SDP route is CLOSED** (answers L41/L48/L50; order-2 IEC-size-4 reach < the size-5 the single-class needed, L36). k=5 not run (provably futile). Verdict `fractional/e3u_x23_k4_verdict.json`
  - [ ] **Redirect (if pursuing the measurable >=6 route at all)**: order-3 lift (IEC size 6) is the formal continuation but its moment matrix is far larger (likely impractical even matrix-free); the honest read is the measurable SDP hierarchy is not a near-term route to chi_m>=6, shifting weight to the Arch-1 missing object (L33)
  - [ ] Alternative to the matrix-free build: find a SYMMETRIC config that crosses $1/4$ (so the de Laat-Vallentin symmetry collapse applies and order-2 becomes cheap). Sidesteps the wall but is itself the hard problem X_23's asymmetry already solved for the single-class bound

## Architecture 3: Fractional / Lovász theta

- [ ] Survey: Cranston-Rabern fractional chromatic bounds + Matolcsi-Ruzsa-Varga-Zsámboki 2023 (chi_f >= 4)
- [x] Compute Lovász theta on Polymath16 510: theta = 170.24, loose chi >= 3 only (LEARNINGS L5)
- [x] Basic OFV rotation-invariant Bessel-LP: $m_1 \leq 0.287$, $\chi_m \geq 4$ in 30 ms (LEARNINGS L6)
- [x] Refine basis to match OFV's published $m_1 \leq 0.2688$ (e3c, 3 off-center unit triangles, exact match, LEARNINGS L8)
- [x] Wide-triangle sweep shows triangle inequalities saturate near 0.2682 (e3d, LEARNINGS L9)
- [x] Moser-spindle inequality breaks triangle saturation: $m_1 \leq 0.2619$, $\chi_m \geq 4$ real $\geq 3.82$ (e3e, LEARNINGS L9)
- [x] Shot 1: 5-chromatic UDG (Polymath 510) in LP — NEGATIVE structural result; Bessel sums cancel across spread-out 510 vertices (e3f, LEARNINGS L10)
- [x] Ambrus 2023 IE-LP framework: confirmed 1-particle LP with inclusion-exclusion atoms, NOT a 2-particle SDP (e3g, LEARNINGS L12)
- [x] Beam search over IE-LP configurations: reached $m_1 \leq 0.2584$ at 17 vertices, matches KMOR 2015 (e3h, LEARNINGS L13)
- [x] Break the 0.258 plateau toward Ambrus 2023 $m_1 \leq 0.2470$: DONE via IEC, not beam search (e3j, LEARNINGS L36). KEY DIAGNOSIS: $0.2584$ is the IE1+IE2 LP CEILING -- the IE1+IE2 primal gives $0.25840$ even on Ambrus's EXACT optimal $X_{23}$ config (e3i), identical to the e3h beam plateau on Polymath 510, so NO better configuration could have broken it; the beam sub-approaches below were structurally moot. The only lever was the (IEC) congruence constraints. e3j adds them and self-certifies (repo's own primal + cvxpy dual, gap ~machine precision): IEC size 3 $\to0.250245$, size 4 $\to0.247468$, size 5 $\to$ **$0.246894 < 1/4$**, giving a $\nu$-free integer $\chi_m(\mathbb{R}^2)\ge5$. Size-3 rung re-verified live 2026-06-15.
  - ~~Beam width >= 2 / vertex-swap / alternate seeds / constructive pool~~ (moot: cannot beat the IE1+IE2 ceiling, only IEC can)
- [x] **CEILING (L36/L37)**: the single-class density route is PROVABLY CAPPED at $\chi_m\ge5$ (Croft floor $m_1\ge0.22936>1/5$, so $1/m_1\le4.36<5$). $\chi_m\ge6$ needs either the multi-class order-2 SDP (Arch-2 sparse conic backend, L48/L50) or the Arch-1 rigid 5-chromatic object (L33). No further integer-bound payoff from improving the single-class $m_1$ upper bound below 0.2469.
- [ ] Reproduce MRVZ chi_f(R^2) >= 4 via their 27-vertex graph + symmetric LP (the remaining FRESH Arch-3 LP task; distinct fractional-chromatic route, needs the MRVZ graph)
- [ ] Architecture 3 dossier: docs/research_atlas/arch3_fractional_lp_lineage.md (currently spread across LEARNINGS L5-L13)

## Architecture 4: Set-theoretic / axiomatic

- [ ] Survey: Shelah-Soifer phenomenon (chi in ZF + DC vs ZFC)
- [ ] Document Borel chromatic number landscape

## Lean substrate

- [x] Initialize `lean/` with lakefile + lean-toolchain mirroring zeta repo (v4.13.0 + Mathlib v4.13.0)
- [x] Skeleton modules: `HadwigerNelson.Basic` (UDG type, chromatic number), `HadwigerNelson.MoserSpindle`, `HadwigerNelson.Controls`
- [x] `lake update` + `lake exe cache get` + `lake build` end-to-end (1859/1859 modules, commit 3b82e91)
- [x] `unitDistanceGraph_adj` lemma proved (clean iff via `rw [SimpleGraph.fromRel_adj]` + dist_comm)
- [x] Fill in HN-2a `moserSpindle.Colorable 4` (proved via e1a witness + per-edge decide)
- [x] Fill in HN-2b `¬ moserSpindle.Colorable 3` (proved via native_decide over $3^7$ functions)
- [x] Fill in HN-2c `moserSpindle.chromaticNumber = 4` (glued via `Nat.sInf_upward_closed_eq_succ_iff` and `Colorable.mono`)
- [x] Fill in HN-2d bridge `moserSpindle` to `planeUnitDistanceGraph` — `four_le_chromaticNumberOfPlane` proved (commit pending)
- [x] L21 covering lemma formalized (`lean/HadwigerNelson/L21CoveringLemma.lean`, h4 VERIFIER, zero sorries)
- [x] L22 list-coloring theorem formalized (`lean/HadwigerNelson/L22ListColoring.lean`, h4 VERIFIER, zero sorries, `L21_iff_L22` proved)
- [x] Bridge graph definitions formalized (`lean/HadwigerNelson/Bridges.lean`)
- [ ] Fill in HN-5 Q^2 chi = 2 (Woodall parity argument; predicate already over ℚ so should be tractable)
- [ ] Fill in HN-6 L^infty chi = 4 (Chilakamarri construction)
- [ ] L23 h2 Positivstellensatz certificate formalization: `moser14_not_udg` theorem
- [ ] L24 triple-lift theorem formalization (3-half chi >= 6 form)
- [ ] Concrete instantiation: `bridgeGraph moserSpindle moserSpindle B_14` chromatic = 5 via L22 + `native_decide` (H4 noted out-of-scope)

## Cross-cutting

- [x] Decide on agent role spec strategy: copy from zeta repo verbatim, or adapt (adapted)
- [x] Six agent specs written under `.claude/agents/` (surveyor, builder, verifier, adversary, synthesizer, orchestrator)
- [x] First session record landed at `experiments/orchestrator_sessions/session_001_bootstrap.md`
- [x] Write `docs/research_atlas/README.md` master landscape
- [x] Write `experiments/PROOF_ARCHITECTURES_PLAN.md`

### Publication tracking

- [x] Publication ledger `experiments/PUBLICATIONS.md`: registry + rubric (V/N/S, verdict, priority) for evaluating publishable discoveries. Initial scoring C1-C6 at L72. C1 (forcing-sterility + codegree note) = SHIP/P1; C3 (solver + symmetry-broken export) = DEVELOP/P2; C2 (portfolio inversion) folds into C1/C3
- [x] **C1 SHIP-ready**: ADVERSARY pass passed (0 blockers, SHOULD-FIX applied, 10pp clean); author + venue (arXiv math.CO + Geombinatorics) set; **arXiv bundle built + validated** `paper/arxiv/forcing-sterility-arxiv.tar.gz` + `ARXIV_SUBMISSION.md`. Remaining = human upload steps (arXiv endorsement if new account; email Geombinatorics)
- [x] **C3 develop**: white paper reshaped into a 7-pp paper draft `paper_solver/main.tex` (compiles clean, 0 undefined refs); C2 portfolio law folded in as the methodology section
- [x] **C3 bib verified**: SAT bibliography web-verified (SURVEYOR, 10 entries vs primary sources; Heule->Geombinatorics 28(1):32-50, PySAT->LNCS 10929:428-437; no TODO-VERIFY left)
- [ ] **C3 SHIP**: ADVERSARY pass + re-check headline timings against caches, decide arXiv cs.DM vs SAT workshop, then build its arXiv bundle (mirror C1)
- [ ] **When a new L_N lands**: evaluate it in `experiments/PUBLICATIONS.md` (candidate or not), score, log the decision
