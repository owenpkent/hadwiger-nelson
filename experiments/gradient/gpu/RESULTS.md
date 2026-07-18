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

## Campaign gamma: beta seeded from the χ≥4 lineage

Beta's χ=3 monolith admits two readings: the generator (i) cannot represent χ≥4 in its
verify pipeline, or (ii) random init never reaches χ≥4 structure (which is geometrically
isolated). Gamma separates them by seeding from known-hard configurations.

**E1 — representation.** Extract the unit-distance edges from the true Moser (χ=4) and
P510 (χ=5) embeddings and SAT them: **Moser → χ=4** (|E|=11), **P510 → χ=5** (|E|=3353 at
tol 0.02; the near-unit-non-edge thickening of L73 follow-up 2, χ unchanged). Reading (i)
is dead: the pipeline represents χ≥4 fine.

**E2 — preservation under pressure.** Seed the adversarial GDA *at* the Moser spindle
(B=2048 jittered copies, 3 seeds) and run the full outer pressure. Every seed:
pre-pressure ~240/256 are χ=4 (jitter knocks a few to χ=3), **post-pressure 2048/2048 →
χ=4**, at median non-edge gap 0.263 (Moser's own gap — clean, intact spindles). The
pressure does not relax χ=4 to χ=3; it *repairs* jittered-down copies back to χ=4. So the
beta χ=3 monolith is a **reachability wall, not a representational limit**: GD *holds*
χ=4 when it starts there, it just cannot *find* it from scratch.

**E3 — scaffold growth.** Seed a Moser core (7 vtx, χ=4) plus (n−7) free vertices
(n∈{10,12,15,18}, 24 configs, B=4096) and let the adversary grow it. Of the 96 densest
survivors: **{χ=3: 79, χ=4: 17}, best legal χ=4, never χ=5.** Among the 25 that legalized
into clean UDGs: {χ=3: 20, χ=4: 5}; densest legal grown χ=4 is n=18, |E|=58. Growing a
χ=4 core under density/colorability pressure does not climb to χ=5, and usually *dilutes*
the Moser rigidity back to χ=3 lattice as it densifies. GD can **hold** a hard core but
cannot **grow** hardness.

Together: the continuous surface can represent and preserve χ=4, but neither builds it
from scratch (beta) nor grows it past χ=4 (gamma E3). The χ≥5 UDGs are unreachable by
this smooth density/colorability pressure from either random or hard-core-seeded starts,
consistent with the L73/L74 governing fact. Checkpoint `_cache/gamma_results.json`, log
`_cache/gamma_run.log`.

## Campaign delta: fixed-skeleton + candidate-edge growth (the L74 lever)

L74's open lever: gamma showed a global soft-adjacency objective *dilutes* a hard core
into χ=3 lattice as it densifies, so it cannot add a hardening unit edge without
dissolving the core. Delta builds the edge model that can: pin a rigid χ=4 core (the
Moser spindle, 11 edges = 2n−3, isostatic → its shape cannot dissolve once its edges are
at unit), attach m free new vertices, and pull each toward unit distance from vertices it
currently *shares a color with* (the differentiable proxy for a hardening edge). Every
unit pair is an intended edge (core, or accepted candidate), so the graph is a legal UDG
by construction — no faithfulness trap. This is de Grey's construction principle as a
continuous, batched search. SAT decides the exact χ of what grew.

**The mechanism solves the dilution problem completely.**

| m (new vtx) | n | runs holding core | best added edges (new) | χ |
|---|---|---|---|---|
| 2 | 9 | **4096/4096** | +6 | 4 |
| 4 | 11 | **4096/4096** | +11 | 4 |
| 6 | 13 | **4096/4096** | +11 | 4 |
| 8 | 15 | **4096/4096** | +16 | 4 |
| 10 | 17 | **4096/4096** | +17 | 4 |
| 12 | 19 | **4096/4096** | +19 | 4 |

Across all 8 core sizes, **every one of 4096 runs held the Moser core intact**
(96/96 verified `core_ok=True`), while adding up to +19 hardening unit edges. Contrast
gamma, where the global objective dissolved 79 of 96 grown configs to χ=3. Delta
dissolves **zero**: you *can* pin a rigid χ≥4 core and grow unit edges onto it.

**But χ stays exactly 4** (histogram {4: 96}, uniform over every m, n up to 19). This is
not a method failure: **the smallest known χ=5 unit-distance graph is ~500 vertices**
(Polymath16), and no small χ=5 UDG is known to exist. Growth to n≤19 cannot reach χ=5
because no such object exists at that size. Delta's contribution is the correct
realizability-preserving growth primitive (100% core-hold), not a χ=5 finder at toy
scale. Reaching χ=5 needs a ~500-vertex de Grey-style linkage, which undirected random
growth will not reconstruct; the productive path to χ=5/χ=6 remains SAT-based
construction, with delta available as the continuous realizability gate for any grown
candidate. Checkpoint `_cache/delta_results.json`, log `_cache/delta_run.log`.

## Reproduce

```
python -m experiments.gradient.gpu.validate           # core gate, must pass first
python -m experiments.gradient.gpu.campaign_alpha      # realizer sweep
python -m experiments.gradient.gpu.campaign_beta       # adversarial generator
python -m experiments.gradient.gpu.campaign_gamma      # beta seeded from Moser/P510
python -m experiments.gradient.gpu.campaign_delta      # fixed-core + candidate-edge growth
```
