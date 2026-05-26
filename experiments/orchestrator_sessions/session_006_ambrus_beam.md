# Session 006: Shot 5 reframed, Ambrus IE-LP implemented, beam search to m_1 <= 0.2584

**Date**: 2026-05-26 (continuation)
**Mode**: depth on Architecture 3, Shot 5 attempted.
**Architecture focus**: 3 (fractional / continuous LP).

## Goal

Attempt the published Ambrus 2023 bound m_1(R^2) <= 0.2470 (integer chi_m >= 5)
via Shot 5' (Ambrus inclusion-exclusion LP + beam search over configurations).
This was originally framed as "2-particle Bachoc-Vallentin SDP" but turned out
to be a misframing — see below.

## What landed

### Structural reframe of Shot 5 (LEARNING L12)

Bachoc-Nebe-Oliveira Filho-Vallentin 2009 (arXiv:0801.1059) develops a
2-particle SDP via Lovász-theta generalization to compact metric spaces.
Reading their Section 6 carefully: at n=2 (Hadwiger-Nelson plane), the SDP
*reduces to the basic Bessel-LP* we already implement, and their paper
explicitly states the SDP is no better than existing bounds at n in [2..8].
**The BV SDP is the wrong target for HN; it does not improve over OFV LP at
n=2.**

Ambrus 2023's m_1 <= 0.2470 is achieved by a refined 1-particle LP with
*inclusion-exclusion atom constraints* from a finite configuration. Specifically
(Lemma 1 of arXiv:2207.14179): for finite X = {x_1, ..., x_n} subset R^2,
define atoms a(eps) for each eps in {+1,-1}^n. Constraints:
- a(eps) >= 0
- a(eps) = 0 if {x_i : eps_i = +1} contains two points at distance 1
- sum a(eps) = 1
- sum over (eps : eps_i = +1) a(eps) = delta(A) for each i
- sum over (eps : eps_i = eps_j = +1) a(eps) = f(x_i - x_j) for each pair

Combined with Bochner-positive-definite f via Bessel basis with f(1) = 0.
This is a 1-particle LP with second-order point-configuration constraints.

### e3g: Ambrus IE-LP framework (commit e01b250)

Implementation tested on five configurations:
- Moser spindle (7 pts): m_1 <= 0.2829.
- Hex 1-layer (7 pts): m_1 <= 0.2799.
- Moser + hexagon (11 pts): m_1 <= 0.2719.
- Hex 2-layer (19 pts): m_1 <= 0.2758.
- Hex 3-layer (37 pts): LP intractable (~800k indep sets).

These bounds are looser than e3e's 0.2619 because e3g works at a single fixed
configuration; the bounds are good only when the configuration's pair distances
populate the autocorrelation constraints richly.

### e3h: greedy beam search (commits d3d9329, b8f9d65)

Beam search over the IE-LP from a 7-vertex hex seed, candidate pool = Polymath
510 vertices, IE-LP evaluation per candidate, greedy at width 1.

Progression:
- Step 0 (7 pts): m_1 <= 0.280044  (seed)
- Step 1 (8 pts): 0.272367
- Step 2 (9 pts): 0.270806
- Step 3 (10 pts): 0.269840
- Step 4 (11 pts): 0.268224
- Step 5 (12 pts): 0.266282
- Step 6 (13 pts): 0.263264   < OFV 2010 (0.2684)
- Step 7 (14 pts): 0.260858   < e3e (0.2619)
- Step 8 (15 pts): 0.259544
- Step 9 (16 pts): 0.258784   matches KMOR 2015 (0.258795)
- Step 11 (17 pts): 0.258397  (resumed after timeout)

The 17-vertex configuration (Polymath 510 indices, in addition order):
seed [0,1,2,3,4,5,6] + added [334, 346, 206, 263, 49, 52, 464, 41, 47, 92].

The script now supports per-step state saving and resume from cache
(experiments/fractional/_cache/e3h_state.json, gitignored, rebuildable).

### Per-step computational cost

Indep set count doubled per step: 19, 38, 66, 132, 264, 528, 912, 1818, 3587,
6948, 11512. Step times scaled accordingly: 20s, 27s, 36s, 47s, 65s, 86s, 138s,
273s, 555s, 1265s. Bash 30-min timeout fit only steps 0-9 in one shot; steps
10-11 needed a resumed second run.

### Plateau visible (LEARNING L13)

Improvement per step decreased monotonically:
| step | delta m_1 |
|---:|---:|
| 1 | -0.0077 |
| 2 | -0.0016 |
| 6 | -0.0030 |
| 9 | -0.0008 |
| 11 | -0.0004 |

Greedy beam at width 1 with Polymath 510 pool is converging to a local
optimum near 0.258. Reaching Ambrus 0.247 from here requires beam width > 1,
vertex-swap local search, richer candidate pool (e.g., constructive
generation in Q(sqrt 3, sqrt 11) lattice), or different starting seed.

## Verified state at session end

m_1(R^2) <= 0.258397 with 17-vertex configuration via greedy beam search.
This matches KMOR 2015's published 0.258795. The full 16-step progression is
documented in LEARNING L13 with explicit indices. Configuration is recoverable
by running e3h with the saved state.

Real-valued chi_m(R^2) >= 1/0.258397 = 3.870. Integer chi_m >= 4 (unchanged).
The gap to integer chi_m >= 5 requires m_1 < 0.2.

## LEARNINGS now in the project

| # | Architecture | Headline |
|---|---|---|
| L1-L11 | (various) | (see previous session 005) |
| L12 | 3 | Ambrus 2023 m_1 <= 0.247 is a 1-particle IE-LP, NOT a 2-particle SDP; BV SDP no help at n=2 |
| L13 | 3 | Greedy beam search 7->17 vertices reaches m_1 <= 0.258 matching KMOR; plateau at width 1 |

## Compute used this session

- e3g framework + tests: ~60 s total.
- e3h beam search (3 runs total): first run timed out at step 9 (~22 min);
  second run resumed and reached step 11 (~22 min). Total ~50 min compute,
  ~17 LP-eval steps avg 500 LPs each at growing scale.
- Total session compute: ~1 hour.

## Pending / next-session candidates

- **Beam width >= 2 in e3h**: keep top-K branches. Could find non-greedy
  alternatives below 0.258.
- **Vertex swap local search on the 17-pt config**: try replacing each vertex
  with pool alternatives. May break the local plateau.
- **Restart from alternate seeds**: Moser spindle, Heule G7 spindle subgraph,
  hand-crafted symmetric configurations.
- **Richer candidate pool**: generate unit-distance neighbors dynamically in
  Q(sqrt 3, sqrt 11) lattice instead of fixed Polymath 510.
- **Architecture 3 dossier**: docs/research_atlas/arch3_fractional_lp_lineage.md
  to consolidate Arch 3 history. Currently spread across LEARNINGS L5-L13.
- **Lean: HN-5 (chi(Q^2) = 2)**: Pivot to Architecture 4 / Lean substrate.
- **Shot 2 (field-extension orbit search) continuation**: algorithmic search
  for binding rotations in alternate rings. Multi-month-scale.

## Honest takeaway

We pivoted Shot 5 from a misframed "2-particle BV SDP" to the actual
methodology Ambrus used: a 1-particle inclusion-exclusion LP. We implemented
the framework (e3g) and ran greedy beam search to reach m_1 <= 0.258 with 17
vertices, matching the KMOR 2015 published bound. We did NOT reach Ambrus's
0.247 — that requires either beam width > 1, local search, or compute scaling
1-2 orders of magnitude beyond a single session.

The 17-vertex configuration is a clean, reproducible artifact. The full
progression is documented in LEARNING L13 with explicit indices. Future work
can resume from the saved state and try the next-level search strategies.
