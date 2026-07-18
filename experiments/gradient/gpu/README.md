# GPU-scaled gradient search (`gradient/gpu/`)

Batched, multi-start GPU versions of the [`gradient/`](../README.md) attack surface.
The parent thread runs one configuration at a time in float64 on the CPU. Gradient
descent on $\chi(\mathbb{R}^2)$ is a **local, one-sided** method, so a single run finds
a single local optimum (the documented honest negative: one adversarial GDA run reaches
only $\chi=3$). The way to make GD productive as a **candidate generator** is massive
multi-start: run thousands of independent optimizations in parallel and keep the rare
good tail. That is a batch dimension, and a batch dimension is what a GPU is for.

Hardware: developed on an RTX 5090 (Blackwell, sm_120), CUDA torch `2.11.0+cu128`.

## The discipline is unchanged

Nothing here relaxes the governing constraint. **GD never proves $\chi \ge 6$.**
Everything PROPOSES float unit-distance configurations; the exact chromatic number of
any survivor is decided by the SAT firewall (`adversarial.sat_chi`,
`f1pt_lib.sat_kcolor`), never by a loss value. The coordinate-grounded terms
(`edge_residual`, `nonedge_margin`, `soft_adjacency`) keep every objective anchored in
genuine Euclidean unit distances, so it cannot lift to $\mathbb{Q}^2$ (where $\chi=2$),
the wrong-approach detector a pure abstract-adjacency soft-coloring objective would fail.

## Precision split

The search runs in **float32 on the GPU** (the 5090 has ~1/64 FP64 throughput, and the
search only needs to PROPOSE candidates). Every survivor is re-refined in **float64 on
the CPU** (Adam + an LBFGS polish that drives rigid realizations to machine precision)
before its edges are read off and handed to SAT. A hard geometric claim is never read
off a float32 GPU tensor.

## Files

| file | what it is |
|------|------------|
| `batched_core.py` | device/dtype-parameterized, batched `(B,n,2)` versions of the `diff_udg` primitives + a batched Adam driver |
| `search.py` | `multistart_realize` (Option B at scale: B parallel embeddings of one graph, top-K float64 refine, legal-UDG verdict) and `soft_chi_oracle` (heuristic colorability witness) |
| `validate.py` | the calibration gate (smoke_test discipline): the batched core must reproduce known answers before any campaign is trusted |
| `campaign_alpha.py` | multi-start legal-UDG **realizer sweep** over the L63 host candidates + the $\chi=5$ $n{=}29$ in-class graph |
| `campaign_beta.py` | multi-start **adversarial UDG generator**: build hard-to-color near-unit graphs, legalize them, SAT their exact $\chi$ |
| `_cache/` | incremental checkpoints, run logs, and flagged candidates |

## Gate first

```
python -m experiments.gradient.gpu.validate
```

Asserts the batched realizer recovers the Moser spindle and a triangular-lattice patch
as legal UDGs (to ~1e-10), that $K_4$ correctly refuses to realize in the plane, and
that the batched coloring oracle reproduces the calibrated values (unit-triangle
`loss@k=2 ~ 0.333`, `@k=3 ~ 0`; $K_5$ `loss@k=4 = 0.1`, `@k=5 ~ 0`). A non-zero exit
means the core is untrustworthy; do not run the campaigns on a broken core.

## Campaigns

```
python -m experiments.gradient.gpu.campaign_alpha [--quick]
python -m experiments.gradient.gpu.campaign_beta  [--quick]
```

Alpha corroborates the L63 / rigidity wall at scale: rigidity-over-determined hosts
($\lvert E\rvert \gg 2\lvert V\rvert-3$) should refuse to realize as legal UDGs even
under thousands of random starts; a host that DID realize legally would be a live
$\chi\ge6$ candidate and is flagged loudly. Beta escalates the Option-A honest negative:
it builds dense near-unit graphs at scale and reports the SAT-exact $\chi$ distribution
of what GD constructs. Findings land in [`RESULTS.md`](RESULTS.md).
