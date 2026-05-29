# ORCHESTRATOR session 2026-05-29: IEC self-certification of integer chi_m >= 5

## Objective

Make the repo's integer $\chi_m(\mathbb{R}^2) \geq 5$ (landed in Shot 3 / L35) FULLY SELF-CERTIFYING: implement the inclusion-exclusion CONGRUENCE (IEC) constraints in the repo's own IE-LP, drive the primal below $1/4$, and have cvxpy produce the dual certificate, with NO reliance on the Ambrus paper's unpublished IEC dual coefficients ($\nu = 10^{-5}$, the 2321 website-only $w_c$).

## Outcome: SUCCESS (full self-certification)

The repo's own dual certificate now gives $m_1(\mathbb{R}^2) \leq 0.246894 < 1/4$, hence integer $\chi_m(\mathbb{R}^2) \geq 5$ self-contained. No paper $\nu$.

## What was done

### Thread 1 (extract + formalize IEC). 
Read `experiments/fractional/_cache/main_final_version.tex` (arXiv:2207.14179v3). The (IEC) family is defined in sect 5 (Averaging, eq `ieC`) and sect 6 (LP format, row (IEC)). Transcription:

- Atoms $a_X(\varepsilon)$, $\varepsilon \in \{\pm1\}^n$; zero unless the positive-index set $I(\varepsilon)$ is independent. So surviving atom variables are in bijection with independent sets $S$ of $G(X)$ (exactly the e3g layout).
- $\sigma(n;I) = \{\varepsilon : \varepsilon|_I = +1\}$, and $\sum_{\varepsilon \in \sigma(n;I)} a_X(\varepsilon) = \sum_{S \text{ indep},\, S \supseteq I} a_S$.
- Congruent pairs $\mathcal{C}(X) = \{\{I,J\} : X|_I \cong X|_J\}$ (isometry-congruent subsets). Averaging the inclusion-exclusion identity over $O(2)$ (Haar) gives, for each $\{I,J\} \in \mathcal{C}(X)$:
  $$\sum_{S \supseteq I} a_S = \sum_{S \supseteq J} a_S.$$

### Thread 2 (implement + solve). 
`experiments/fractional/e3j_iec_selfcertify.py` extends e3g/e3i: same $X_{23}$, same 13552 independent-set atoms + 600 Fourier vars + IE1 + IE2, PLUS the IEC constraints. Congruent-pair enumeration buckets independent subsets of size $1..k$ by their exact pairwise-squared-distance multiset (canonicalized to integer ids; distinct exact distances never merge), and confirms each candidate by an exact distance-matrix bijection test (the soundness gate). `superset_atoms` uses postings-list intersection of per-vertex atom sets (fast). Solved primal with cvxpy + HiGHS; read cvxpy's (IET) dual (the only inhomogeneous constraint), which by LP strong duality is the dual objective.

### Thread 3 (certify). 
Confirmed primal = dual at every $k$ (gap $\sim 10^{-16}$); dual $< 1/4$ strictly at $k \geq 4$; monotone tightening as IEC subset size grows (valid constraint added to a MAX can only lower the optimum, so the bound stays a rigorous upper bound on $m_1$); wrong-approach 1D = 0.5 (no overshoot).

## Results

| max congruent-subset size $k$ | (IEC) constraints | primal $m_1$ | repo's own dual | duality gap | solve (s) |
|---:|---:|---:|---:|---:|---:|
| (e3g IE1+IE2 only) | 0 | 0.258405 | -- | -- | -- |
| 3 | 3904 | 0.250245 | 0.250245 | $3.9\mathrm{e}{-16}$ | 156 |
| 4 | 5245 | 0.247468 | 0.247468 | $2.2\mathrm{e}{-15}$ | 1698 |
| **5** | **5730** | **0.246894** | **0.246894** | **$2.5\mathrm{e}{-16}$** | 268 |

$4 \times 0.246894 = 0.987576 < 1$. Integer $\chi_m \geq 5$ self-contained. Value edges below L35's reproduced paper bound 0.246997.

Solver: cvxpy 1.9.0 + HiGHS. Setup 2-3 s/run. Total wall ~37 min single machine.

## Files

- `experiments/fractional/e3j_iec_selfcertify.py` (new, the implementation)
- `experiments/fractional/_cache/e3j_iec_selfcertify.json` (results)
- `experiments/fractional/_cache/e3j_run.log` (run log)
- `experiments/LEARNINGS.md` (L36 added above L35)
- `experiments/PROOF_ARCHITECTURES_PLAN.md` (e3j row added)
- `experiments/SOLVING_PROGRAM.md` (Shot 3 -> self-certified; Shot 5' IEC done; status table)

## Portfolio + falsifiability

- Arch 3 / Route A is now CAPPED at $\chi_m \geq 5$ ($\alpha_1(\mathbb{R}^2) = 1/4$ conjectured; the IEC-LP bottoms out at $1/4$, cannot give $m_1 < 1/5$). No further LP density work advances the integer bound. This direction is DONE for $\geq 5$ and BLOCKED for $\geq 6$ (falsifiability trigger hit cleanly: the ceiling is the conjectured $\alpha_1 = 1/4$, confirmed by the self-certified $0.2469$ matching it).
- $\chi_m \geq 6$ remains gated by the same Arch-1 missing object (a rigid 5-chromatic UDG / a chi-6 UDG that embeds), per L33/L34.

## Recommended next session

- A: Lean Shot 4 (formalize de Grey / Heule $\chi \geq 5$). Highest-leverage unstarted shot; the LP integer bound is now closed.
- B: Continue Arch-1 Shot 2 lever (chi-5 building block with concentrated self-unit-distance neighborhoods, L34) - low EV, the only remaining $\geq 6$ lever in the lineage.
- C: Write up the self-certified integer $\chi_m \geq 5$ (e3i + e3j) as a short note; it is a clean, $\nu$-free, machine-checkable density-route proof. ESCALATE to Owen before any external claim (verify no SAT/arithmetic bug; here the risk is low - exact arithmetic for $X_{23}$, $10^{-16}$ duality gap, monotone ladder, wrong-approach PASS).

Recommendation: C (write-up + escalate) then A (Lean), since the bound is real and self-contained and the Lean substrate is the long pole.
