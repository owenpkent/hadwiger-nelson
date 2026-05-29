# ORCHESTRATOR session 2026-05-29: Shot 3, Ambrus 2023 reproduction

## Mandate

SHOT 3 of SOLVING_PROGRAM: reproduce Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023
(arXiv:2207.14179v3) directly, landing the project's first integer
$\chi_m(\mathbb{R}^2) \geq 5$ via the inclusion-exclusion LP route. Probability ~99%,
novelty low, value = calibration of the IE-LP pipeline and de-risking Shot 5'.

## Outcome: SUCCESS (full)

Integer $\chi_m(\mathbb{R}^2) \geq 5$ achieved, dual-certified, wrong-approach
detector PASS.

### Thread 1 (SURVEYOR): config extraction. COMPLETE.

The arXiv PDF previously returned binary-only (L12), so the source tarball was
downloaded instead (`arxiv.org/e-print/2207.14179`, 184 KB), extracting
`main_final_version.tex`. The paper prints:

- Exact symbolic coordinates of $X_{23}$ (Appendix Table 1) as complex numbers
  in $\mathbb{Q}(\sqrt 3, \sqrt{11}, \sqrt{33})$ where $\sqrt{33} = \sqrt 3\sqrt{11}$,
  so the field is the lineage's $\mathbb{Q}(\sqrt 3, \sqrt{11})$.
- The dual certificate non-IEC part (Table 2): $w_0 = 0.378583$, $w_T = 0.246973$,
  $w_1(1) = 1.059384$, and 26 nonzero $w_2(i,j)$.
- The verification constants $\nu = 10^{-5}$, $\mu = 6\times10^{-5}$, and the
  final bound $(w_T+\nu)/(1-\mu) = 0.24699\ldots < 0.2470$.

Config archived: `experiments/fractional/_cache/ambrus_23point_config.json`.

CAVEAT documented: the full dual has 2350 nonzero coeffs, of which 2321 are
(IEC) congruence duals $w_c$ that the paper does NOT print (website only).

### Thread 2 (BUILDER): reproduction. COMPLETE (with honest gap).

`experiments/fractional/e3i_ambrus_reproduce.py`:
- (A) Parsed + exact-verified all 23 coordinates: $G_{23}$ has exactly 47 edges
  (each $\|x_i-x_j\|^2=1$ by sympy), 27 distinct squared distances (matches),
  min degree 2 (matches), float/exact edge sets agree.
- (B) Primal IE-LP (e3g framework, IE1+IE2, NO IEC) on $X_{23}$: 13552 atom
  vars, optimum 0.258405 in 5.0 s (cvxpy + HiGHS). This is the KMOR 2015
  frontier, NOT 0.247. The 0.0114 gap is the 5868 (IEC) congruence constraints
  the e3g framework does not implement.
- (C) Dual certificate $\varphi(t) \geq 1$ re-derived from the 29 printed
  coefficients: global min 0.99995003 at $t = 3.7749$ (paper 3.77488), tail
  $> 1.0107$, $|w_0|+\sum|w_2| = 1.93062 < 2$. Rigorous bound 0.246997.

### Thread 3 (VERIFIER): certification. COMPLETE.

- Dual-certified: the rigorous bound is a dual-feasible point (Prop. 1 = weak
  LP duality), not primal-only. The $W(t)\geq 1$ half re-derived independently;
  the $V(\varepsilon)\geq 0$ half relies on the paper's asserted $V \geq -\nu$
  (needs their 2321 unpublished IEC duals).
- $m_1 < 1/4$ strictly: $0.246997 < 0.25$ confirmed.
- Integer $\chi_m \geq 5$ via covering: 4 classes cover $\leq 4\times0.246997 =
  0.98799 < 1$. Threshold is exactly $m_1 < 1/4$; strictness forces color 5.
- Wrong-approach detector (1D analog) PASS: $m_1(\mathbb{R}) = 0.500000$,
  $\chi_m(\mathbb{R}) \geq 2$, no overshoot. $\mathbb{Q}^2$ is the legit
  measure-zero exemption.

## The one genuinely new structural finding

The primal experiment isolates WHERE the KMOR-2015-to-Ambrus-2023 improvement
lives: the (IEC) congruence constraints, not config richness or a higher SDP.
Same $X_{23}$, same 13552 atoms: IE1+IE2 gives 0.2584, IE1+IE2+IEC gives 0.247.
$X_{23}$ is engineered for congruence (27 distances among 253 pairs). This makes
"implement IEC in e3g" a sharp, bounded next step.

## Architecture portfolio note

Arch-3 density route (Route A of L33) is now CAPPED at $\chi_m \geq 5$: the paper
conjectures $\alpha_1(\mathbb{R}^2) = 1/4$ (fractional $\chi_f = 4$, record
$\chi_{gf} = 3.9954 < 4$), so $m_1 < 1/5$ is unreachable. Pushing to $\chi_m \geq 6$
needs Falconer Route B with a rigid 5-chromatic config = the Arch-1 missing
object (L33). Do not over-invest Arch 3 chasing $\chi_m \geq 6$ via density.

## Recommended next deployments

- **A (close the primal gap, bounded, ~1 session)**: BUILDER implements (IEC)
  congruence constraints in `e3g`/`e3i`. Target: primal LP on $X_{23}$ self-reaches
  0.247 without the paper's website duals. Makes the repo's bound primal-self-certifying.
- **B (Shot 5', now de-risked)**: BUILDER runs beam search with the calibrated
  IE+IEC pipeline from a Moser seed, attempting $X_{24+}$ below 0.247. Low EV for
  a NEW frontier (Arch 3 capped near 1/4), but validates the search machinery.
- **C (Lean, Shot 4)**: the dual certificate $\varphi(t)\geq 1$ is a finite,
  checkable analytic inequality + a finite $V(\varepsilon)\geq 0$ check. A future
  Lean target: formalize Prop. 1 and verify $m_1 \leq 0.247$ given the (published)
  duals. Smaller than the de Grey SAT-checker port.

Recommended: A this-or-next session (bounded, makes the repo self-certifying);
defer B (capped EV); C is a longer Lean track.

## Falsifiability triggers

None hit. Shot 3 succeeded as predicted (~99%). The Arch-3 ceiling ($\chi_m \geq 5$,
not 6) is a known bounded-ceiling fact, now confirmed numerically, not a dead end
to abandon: it is the correct stopping point for the density route.

## Escalation to Owen

No escalation needed. This reproduces a published, peer-relevant result; no novel
claim of $\chi = k$. Flagging for awareness only: the repo now holds an integer
$\chi_m(\mathbb{R}^2) \geq 5$ that is independently dual-verified on the analytic side.

## Files (all absolute)

- `c:\Users\Owen\dev\hadwiger-nelson\experiments\fractional\e3i_ambrus_reproduce.py`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\fractional\_cache\ambrus_23point_config.json`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\fractional\_cache\e3i_ambrus_reproduce.json`
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\fractional\_cache\main_final_version.tex` (paper source)
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\fractional\_cache\ambrus_src.tar.gz` (full arXiv tarball)
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\LEARNINGS.md` (L35)
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\PROOF_ARCHITECTURES_PLAN.md` (e3i row)
- `c:\Users\Owen\dev\hadwiger-nelson\experiments\SOLVING_PROGRAM.md` (Shot 3 status)
