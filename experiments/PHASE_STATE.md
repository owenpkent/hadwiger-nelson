# PHASE_STATE

The single operational state file for the Hadwiger-Nelson program. Adapted from
the zeta repo; see [`ZETA_INNOVATION_TRANSFER.md`](ZETA_INNOVATION_TRANSFER.md).

How this file relates to its peers:
- [`LEARNINGS.md`](LEARNINGS.md) is the permanent numbered findings log (what was found).
- [`PROOF_ARCHITECTURES_PLAN.md`](PROOF_ARCHITECTURES_PLAN.md) is the per-architecture plan.
- [`PUBLICATIONS.md`](PUBLICATIONS.md) is the publication ledger.
- **This file** is the resumable operational surface: the top is a reverse-chronological
  stack of dated session blocks, then stable sections (walls, falsifiability triggers,
  recommended deployments, and the Last-verified-state pin). A cold-resuming session
  should read the top N blocks plus the pin, not re-derive the edge.

Maintained by ORCHESTRATOR and SYNTHESIZER. Newest block at the top. Verdict
vocabulary: KILL / MIRROR / PARTIAL / CONFIRMED / CLOSED.

---

## Dated update stack (newest first)

> **Update (2026-06-30): meta-infrastructure transfer from the zeta repo.**
> Audited the zeta-function repo for transferable methodology and adopted the real
> gaps (report: [`ZETA_INNOVATION_TRANSFER.md`](ZETA_INNOVATION_TRANSFER.md)).
> Shipped: (1) `_shared/smoke_test.py` now actually COLORS the controls and gates
> on them (Moser=4, Q^2=2, L^inf=4, R^1=2, unit triangle=3), plus a `--full`
> chi>=5 calibration (Heule-826 UNSAT at k=4 in ~6s via symbreak portfolio).
> (2) `lemma_db/` built: a 27-node proof-dependency DAG with a control-object
> firewall (CONFIRMED live: self-test fires on a planted Q^2/L^inf load-bearing
> edge and rolls back clean). (3) This file, `STATE_OF_THE_PROGRAM.md`,
> `FREEZE_LIST.md`, `LOAD_BEARING_FACTS.md`, `TOKEN_EFFICIENCY.md`, a NIGHT_PLAN
> template, the PUBLICATIONS K1 circularity gate, and attack-prompt twins.
> (4) `toy/` sandbox (the zeta toy analog, flagged after the first pass): a battery
> of known-chi finite graphs (SAT answer key) that GRADES a proposed chi-lower-bound
> technique on reproduce-target / reject-fakes / control-immune / k1-clean. Reference
> (exact-chi-by-SAT) all green; the clique and degree+1 demo candidates are caught;
> the controls are the firewall. Honest caveat: grades the technique, not the W3
> realizability lift. Consequence: the program is now resumable from one surface,
> structurally self-auditing, and technique-grading. No mathematical state changed.

> **Update (2026-06-15): L69-L72, the order-2 measurable verdict.** CLOSED the
> order-2 measurable route: at Ambrus's X_23, matrix-free order-2 (IEC up to
> subset size 4) is FEASIBLE, so it does not certify chi_m>=5 and by monotonicity
> cannot reach chi_m>=6 (L72, C4). Built and validated the matrix-free order-2
> SDP solver first (L70-L71, e3u). E16 top-down repair of M^3(C5) stalls; K_{2,3}
> violations are load-bearing for chi=6 (L69). Geombinatorics structural note
> drafted (no new bound).

> **Update (2026-06-11): L63, the codegree wall.** The nauty-free host factory
> works (n=18 K4-free 6-critical graphs, alternators abundant), but UDG-realizability
> forces K_{2,3}-freeness, which excludes every manufactured host (L63, into C1).
> PARTIAL: hosts exist abstractly, none survive the codegree ceiling. Next: generate
> inside the both-free class from P510 (E14).

> **Update (2026-06-09): L57-L62, forcing-sterility + the phase-gadget route.**
> Exhaustive forcing census: all ~2.29M non-adjacent pairs across the 12 known
> chi-5 UDGs are FREE (L57, the Essential-Pair Lemma explains it: the lineage is
> vertex-critical, so forcing-sterile by construction). Phase-gadget dichotomy and
> the alternator analysis bypass W3 framing (L58-L62). This became C1.

> **Update (2026-06-02): L51-L56, the clamp and backward-from-2050.** The abstract
> flexible color-clamp EXISTS (48-vtx triangle-free SAT witness); W3 reduces to
> cocircularity with distinct centers (Theorem R, L51-L53). Backward-from-2050:
> most likely terminal answer chi=6 by a finite UDG; the linchpin is the W3
> realizable clamp; the RG diagnostic is imprimitivity, not leading eigenvalue;
> forced-same sweep NEGATIVE across the lineage (L54-L56).

---

## Current wall, per architecture

| Arch | Approach | Current wall | Status |
|------|----------|--------------|--------|
| 1 UDG | finite chi>=6 UDG via the realizable clamp | W3 = unit-distance realizability of the clamp; the host must be K4-free 6-critical AND K_{2,3}-free AND outside the P510 lineage | OPEN, the live route (route ii: wide imprimitive interface) |
| 2 measurable | chi_m>=6 via SDP | order-2 at X_23 is FEASIBLE; route CLOSED. Higher order or noncommutative SE(2) is the only remaining measurable lever | CLOSED (order-2); SE(2) open |
| 3 fractional/spectral | chi_f, Lovász theta | plateau at the classical line at runnable scale | OPEN, no live increment |
| 4 axiomatic | Borel chromatic chi_B | needs a local finite-UDG statement that pushes chi_B>=6 via the rotation group (not norm-blind Steinhaus) | OPEN, dark horse |

## Falsifiability triggers

- order-2 measurable certifies chi_m>=5 at X_23 -> **TRIGGERED-CLOSED (L72): it is FEASIBLE, route closed.**
- a forced non-adjacent pair found anywhere in the known lineage -> NOT-TRIGGERED (L57: exhaustively free).
- a manufactured K4-free 6-critical host that is also K_{2,3}-free -> NOT-TRIGGERED (L63: codegree wall).
- the firewall (`lemma_db`) reports a violation -> NOT-TRIGGERED (audit clean as of 2026-06-30).

## Recommended next deployments

1. **The one most-leveraged move:** a NEW chi-5 UDG outside the P510 lineage carrying
   a wide imprimitive interface (route ii of L55). Feed candidates to the existing
   forced-pair SAT test. See `lemma_db --frontier`: `new_chi5_outside_lineage`.
2. The descriptive-set-theory dark horse: a local finite-UDG criterion for chi_B>=6.
3. Measurable: the noncommutative SE(2) spectral bound, if a smallest computable
   instance can be pinned (the abelian shadow is exhausted).

---

## Last verified state

- **Commit:** `2675776` (master, pushed; in sync with origin as of 2026-06-30).
- **Latest finding:** L72 (order-2 measurable route CLOSED).
- **Lean:** sorry-free (incremental build with cached Mathlib oleans).
- **Canonical SAT witness state:** the whole chi>=5 lineage is self-certifiable on
  one workstation via the symmetry-broken portfolio (M^4(C5) k=6, P510 k=4, de Grey
  1585 k=4 all UNSAT, optional DRAT). L68 / C3.
- **Gates green:** `python -m experiments._shared.smoke_test` (core) and
  `python -m experiments.lemma_db.build_db` (firewall, 0 violations) both pass.
  `smoke_test --full` confirms Heule-826 UNSAT at k=4 (~6s).
- **Papers:** C1 (forcing-sterility + codegree) SHIP/P1, arXiv bundle built. C3
  (symmetry-broken solver) DEVELOP->SHIP-ready/P2, arXiv bundle built. Both pending
  Owen's upload action.
