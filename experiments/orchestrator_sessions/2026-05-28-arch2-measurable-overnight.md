# ORCHESTRATOR session: 2026-05-28 Arch-2 measurable / spectral overnight batch

## Mandate

Overnight unattended batch on Architecture 2 (measurable / spectral $\chi_m(\mathbb{R}^2)$).
Three threads: (1) SURVEYOR consolidate the measurable atlas section; (2) BUILDER
e2b spectral SDP for $m_1(\mathbb{R}^2)$ with mandatory cross-validation against the
Arch-3 OFV LP; (3) BUILDER e2c Falconer $\chi_m \geq 5$ rigorous-numerical. Explicit
instruction NOT to re-run the Arch-3 $m_1$ density LP, and to be honest about the
frontier (is $\chi_m \geq 6$ open?).

## What was already there (avoided duplication)

- A comprehensive [`arch2_measurable_lineage.md`](../../docs/research_atlas/arch2_measurable_lineage.md)
  dossier already existed (prior SURVEYOR), with the chronology, Falconer proof at
  the lemma level, the $\chi_m \geq 6$ misattribution audit, and per-method
  wrong-approach analysis. The survey thread became a CONSOLIDATION + focused
  spectral/SDP companion rather than a from-scratch survey.
- Arch-3 e3b/e3c already reproduce the OFV LP ($m_1 \leq 0.287119$ basic,
  $0.268412$ three-triangle, exact). These are the e2b cross-validation anchors.
- SDP backends available: cvxpy 1.9.0 with SCS and CLARABEL (PSD cones) and HiGHS
  (LP). No MOSEK / CVXOPT.

## Decisions and outcomes

### Thread 1 (SURVEYOR / consolidation) -> DONE, L31
- Wrote [`arch2_measurable.md`](../../docs/research_atlas/arch2_measurable.md), a
  spectral/SDP companion: the $k$-point SDP hierarchy (OFV 2-point, BNOFV/DMOV
  3-point), the project experiments e2a/e2b/e2c with certificates, and a sharpened
  $\chi_m \geq 6$-is-OPEN verdict.
- Added a pointer from the atlas README Architecture 2 section.
- **Frontier verdict (honest):** $\chi_m(\mathbb{R}^2) \geq 5$ (Falconer 1981) is
  the best known, unimproved in 45 years. $\chi_m(\mathbb{R}^2) \geq 6$ is OPEN.
  The literature "$\chi_m \geq 6$" results are hyperbolic-plane (DeCorte-Golubev)
  or convex-tile (Coulson) misattributions, NOT the canonical $\mathbb{R}^2$ result.

### Thread 2 (BUILDER e2b spectral SDP) -> DONE, L32
- [`e2b_spectral_sdp.py`](../measurable/e2b_spectral_sdp.py).
- **2-point cross-validation gate: PASS exactly.** Basic $0.287119$, three-triangle
  $0.268412$, both matching OFV 2010 / Arch-3 e3c to $< 5\times10^{-7}$. $\mathbb{R}^1$
  detector PASS ($m_1(\mathbb{R}) = 0.5$, no overshoot). Diagonal-$Z$ SDP gate PASS
  (reproduces scalar LP, proving the SDP relaxation is faithful / non-leaky).
- **3-point matrix SDP: no improvement** ($0.26840$ vs scalar $0.26841$). A
  94-triangle scalar sweep also saturates at $0.26833$. Honest conclusion: the
  unit-equilateral-triangle inequality family is exhausted near $0.268$; the
  tightening to KMOR $0.2588$ lives in the IE-atom LP (Arch 3 e3g/e3h, already
  $0.2584$), and the published $\sim 0.229$ 3-point regime needs the full DMOV
  $O(2)$-isotypic Jacobi SDP (beyond the SCS backend overnight).
- Modeling lesson recorded: the naive PRIMAL moment model is vacuous ($m_1 \leq 1$);
  the OFV bound is a genuine DUAL statement; the 3-point lift must add PSD matrix
  multipliers to the dual LP.

### Thread 3 (BUILDER e2c Falconer rigorous) -> DONE, L33
- [`e2c_falconer_rigorous.py`](../measurable/e2c_falconer_rigorous.py).
- **Plancherel / Wiener-Khinchin witness:** autocorrelation of a 1-avoiding
  hexagonal cell is positive-type (min DFT power $2\times10^{-10} \geq 0$) and
  vanishes on the unit circle to $5\times10^{-17}$. This is the analytic identity
  Falconer's averaging step (F4) rests on.
- **Density-route arithmetic made exact:** crosses to $\chi_m \geq 5$ only at
  $m_1 < 1/4$ (Ambrus 2023). Falconer 1981 reached $\geq 5$ earlier via rigidity.
- **Rigidity object named:** Moser spindle ($7$ vtx, $\chi = 4$, SAT-confirmed) is
  Falconer's (F3) rigid $4$-chromatic configuration giving $\chi_m \geq 5$.
  $\chi_m \geq 6$ via Falconer needs a $5$-chromatic rigid config = the Arch-1
  missing object.
- Honest scope: e2c does not reprove $\chi_m \geq 5$ from scratch (the (F4)
  measure-theoretic limit is not a finite overnight certificate); it verifies the
  identity, the arithmetic, and names the missing input.

## Files created / modified (all absolute)

Created:
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\measurable\e2b_spectral_sdp.py`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\measurable\e2c_falconer_rigorous.py`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\measurable\_cache\e2b_spectral_sdp.json`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\measurable\_cache\e2c_falconer_rigorous.json`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\measurable\_cache\e2b_run.log`
- `c:\Users\Owen\dev\hadwiger-nelson\docs\research_atlas\arch2_measurable.md`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\orchestrator_sessions\2026-05-28-arch2-measurable-overnight.md` (this file)

Modified:
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\LEARNINGS.md` (added L31, L32, L33 above L30)
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\PROOF_ARCHITECTURES_PLAN.md` (e2a/e2b/e2c status rows + experiment list)
- `c:\Users\Owen\dev\hadwiger-nelson\docs\research_atlas\README.md` (Arch-2 companion pointer)

NOT touched (owned by other running processes, per mandate):
- `experiments/combinatorial/_cache/h6mix_510x517_B1800_longrun.json`
- `experiments/combinatorial/_cache/h6_direction_b_single.json`

## Portfolio allocation (post-session)

This session spent ~100% on Arch 2, by mandate. Running tally of the default
portfolio (Arch1 40% / Arch2 25% / Arch3 15% / Arch4 10% / cross 10%):
- Arch 1: dominant in recent sessions (L14-L30, the chi-6 abstract-graph lineage).
- Arch 2: this session brings it current (e2a/e2b/e2c all landed; dossier + companion).
- Arch 3: e3a-e3h done; $m_1 \leq 0.2584$ (matches KMOR). Open: push toward Ambrus
  0.2470 / 0.247 via beam width $\geq 2$.
- Arch 4: largely expository; Lean L21/L22 landed.

Recommendation: Arch 2 is now SATURATED at the available-tooling frontier. The
remaining Arch-2 levers (full DMOV $O(2)$-isotypic SDP; pushing $m_1 < 1/5$) need
either MOSEK or the Arch-3 IE-LP beam search. Rebalance back toward Arch 1
(building-block search for a sub-510 chi-5 no-$K_4$ UDG, per L30) and Arch 3
(IE-LP beam width $\geq 2$ toward 0.247).

## Pending agent outputs (deadlines)

- The detached Arch-1 jobs (`h6mix_510x517_B1800_longrun.json`,
  `h6_direction_b_single.json`) are owned elsewhere; check them next Arch-1 session.

## Recommended next deployments (sharp specs)

A. **Arch 3 BUILDER (highest EV on the measurable bound):** IE-LP beam search with
   beam width $\geq 2$ + vertex-swap local search over the Polymath-510 point pool,
   target $m_1 < 0.255$ toward Ambrus 0.2470. This is the only route that can move
   the measurable lower bound ($\chi_m \geq 5 \to$ closer to a $\geq 6$ threshold at
   $m_1 < 0.2$). Backend: cvxpy + HiGHS (LP, fast).

B. **Arch 1 BUILDER (vertex-count frontier, per L30):** building-block search for a
   chi-5 no-$K_4$ graph below 510 vertices (the only lever left to beat the 1020
   chi-6 record). Fresh field extension or non-Polymath spindle stack.

C. **Arch 2 stretch (only if MOSEK becomes available):** implement the full DMOV
   3-point $O(2)$-isotypic Jacobi/Gegenbauer SDP for $m_1(\mathbb{R}^2)$ toward the
   $\sim 0.229$ regime. Without MOSEK this is not tractable; do NOT attempt on SCS.

## Falsifiability triggers

- **Arch 2 $\chi_m \geq 6$ (this session's lane):** the trigger "if neither the
  density route ($m_1 < 1/5$) nor the Falconer rigidity route (a small 5-chromatic
  rigid config) is reachable with available tooling, document $\chi_m \geq 6$ as a
  blocked frontier coupled to the Arch-1 missing object" is MET. Arch 2 is parked at
  $\chi_m \geq 5$; further progress is gated on Arch 1 / Arch 3.
- No new escalation to Owen. No claimed proof, no claimed disproof. Everything in
  the working tree, uncommitted, per per-action authorization policy.
