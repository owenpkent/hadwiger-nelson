# GPU campaign results (L74)

Overnight run on an RTX 5090 (Blackwell, sm_120), CUDA torch `2.11.0+cu128`. Two
firewalled GPU campaigns on the [`gradient/`](../README.md) thread. **No bound moved.**
Both are honest negatives that sharpen L73 quantitatively, at a scale a single-run CPU
attack cannot reach. Every hard chromatic claim below is SAT-decided
(`adversarial.sat_chi`, CaDiCaL 1.95), never read off a loss value.

## Campaign alpha: legal-UDG realizer sweep

Threw a large multi-start realizer at every known host candidate: **16,384 random
embeddings each** (B=4096 x 4 seeds), GPU float32 search, top-8 float64 CPU refine with
an LBFGS polish. Verdict: **every host refuses to realize as a legal unit-distance
graph.**

| host | n | \|E\| | over-det (\|E\|-(2n-3)) | best max edge err | legal |
|------|---|-----|------|-------|-------|
| e15b_chi5_n29 (the χ=5 in-class prize) | 29 | 98 | +43 | 0.414 | **no** |
| e13_shrunk_18_from_M2_W5 | 18 | 79 | +46 | 0.506 | no |
| e13_shrunk_19_from_M2_W5 | 19 | 86 | +51 | 0.484 | no |
| e13_shrunk_20_from_M_grotzsch_apex | 20 | 86 | +49 | 0.713 | no |
| e13b_shrunk_18_from_M2_W5_emin | 18 | 76 | +43 | 0.467 | no |
| e13b_shrunk_19_from_M2_W5_emin | 19 | 82 | +47 | 0.509 | no |
| e13b_shrunk_20_from_M_grotzsch_apex_emin | 20 | 85 | +48 | 0.673 | no |
| e13b_aware_19_79 | 19 | 79 | +44 | 0.581 | no |
| e13b_aware_19_80 | 19 | 80 | +45 | 0.347 | no |

The best edge error never closes below ~0.35 (a legal UDG needs < 1e-6), and every host
is rigidity over-determined by +43 to +51 edges. This is the **continuous / rigidity
corroboration of the L63 codegree wall at GPU scale**: the plane geometry alone refuses
these graphs, no K_{2,3}-freeness argument invoked, now under 16k starts rather than one.
The n=29 χ=5 in-class graph is the notable case: realizing it would have been a new χ=5
UDG (the most-leveraged move), but it is over-determined by +43 and refuses.

Checkpoint: `_cache/alpha_results.json`. A host that DID realize legally would have been
flagged as a live χ≥6 candidate; none did.

## Campaign beta: adversarial UDG generator

The GD-native form of the live Arch-1 route, scaled from one run to **221,184 parallel
adversarial GDA runs** (54 configs over n∈{9,12,15,18,21,24}, target-degree∈{3,4,5},
τ∈{0.05,0.08,0.12}, B=4096 each). Each run does max_coords min_coloring at k=4, with a
below-target degree hinge + crispness reward forcing it to build a dense near-unit graph
and an anti-collapse penalty. The 96 densest / hardest survivors were legalized and
SAT-certified.

**Result: a monolithic χ=3 distribution.**

- χ histogram over all 96 verified survivors: **{3: 96}**. Not one reached even χ=4.
- Densest graph GD built: n=24, crisp |E|=77. Densest that legalized into a clean UDG:
  n=24, |E|=76, **χ=3**, non-edge gap 0.051.
- Peak soft-colorability-hardness config (n=15, deg=3, τ=0.08) reached 0.096, yet its
  verified graphs are still χ=3: the soft residual reflects imperfect soft coloring of a
  thickened graph, not genuine χ=4 structure.
- Only **4 of 96** densest emergent topologies legalized into clean UDGs; the other 92
  are over-determined near-unit clouds that cannot be realized cleanly (the same rigidity
  wall alpha hits, and the P510 near-unit-non-edge faithfulness trap of L73's follow-up 2).
  All 96, legal or not, are χ=3 by SAT.

**Reading.** Massive multi-start adversarial GD construction of unit-distance graphs
collapses to triangular-lattice-like, 3-chromatic patches. Maximizing unit-distance edge
count from a random cloud finds the densest packing of unit distances (the lattice), which
is exactly χ=3, and the k=4 colorability pressure does not lift it even to χ=4. The χ=4
Moser-spindle rigidity (two rhombi at an irrational rotation) is a geometrically isolated
target that smooth density/colorability pressure does not discover. This sharpens the L73
flagship negative from "one run → χ=3" to "10^5-scale multi-start → χ=3, never χ=4,"
consistent with the governing fact that GD is local and one-sided.

**Scope / honesty.** This is a property of THIS objective (density + soft-coloring +
spread), not a theorem that GD cannot build χ=4. A different objective, or Moser-seeded
starts, might. The claim is bounded: of the 96 densest/hardest survivors up to |E|=76,
every one is χ=3, and no χ≥5 candidate was flagged. No bound moved.

Checkpoint: `_cache/beta_results.json`, per-config log `_cache/beta_run.log`.

## Reproduce

```
python -m experiments.gradient.gpu.validate           # core gate, must pass first
python -m experiments.gradient.gpu.campaign_alpha      # realizer sweep
python -m experiments.gradient.gpu.campaign_beta       # adversarial generator
```
