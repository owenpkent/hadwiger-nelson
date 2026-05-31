# sources/notes/ — Comprehensive reading notes

Deep notes from a full read of the reference library (see `sources/LIBRARY.md` for the
catalog). Produced 2026-05-30 by reading the extracted text of every text-bearing PDF and
writing architecture-oriented notes keyed to the project's four proof architectures (A1
combinatorial/UDG, A2 measurable/spectral, A3 fractional/Lovasz theta, A4 axiomatic) and to
the current bottleneck: **a $\chi \ge 6$ unit-distance graph that embeds in the plane.**

Each file opens with an executive summary and an actionable-takeaways list, then gives
section/chapter-level detail with theorem statements and page/line references.

## Files

| File | Texts covered | Architecture |
|------|---------------|--------------|
| [01-soifer-mathematical-coloring-book.md](01-soifer-mathematical-coloring-book.md) | Soifer, *Mathematical Coloring Book* (2009) | A1, A2, A4 (HN-central) |
| [02-kechris-descriptive-set-theory.md](02-kechris-descriptive-set-theory.md) | Kechris, *Classical Descriptive Set Theory* (1995) | A4 |
| [03-stein-shakarchi-fourier-analysis.md](03-stein-shakarchi-fourier-analysis.md) | Stein-Shakarchi, *Fourier Analysis* (2003) | A2 |
| [04-fractional-graph-theory-and-bachoc-spectral.md](04-fractional-graph-theory-and-bachoc-spectral.md) | Scheinerman-Ullman *Fractional Graph Theory*; Bachoc-DeCorte-Oliveira-Vallentin (2014) | A3 (+A2) |
| [05-a1-constructions-degrey-exoo-voronov.md](05-a1-constructions-degrey-exoo-voronov.md) | de Grey (2018); Exoo-Ismailescu (2018); Voronov-Neopryatnaya-Dergachev (2022) | A1 |
| [06-sat-machinery-heule-knuth.md](06-sat-machinery-heule-knuth.md) | Heule (2019); Knuth TAOCP V4F6 *Satisfiability* (sample) | A1 |
| [07-knuth-vol3-sorting-searching.md](07-knuth-vol3-sorting-searching.md) | Knuth TAOCP V3 *Sorting and Searching* (image-only; reference) | (general) |
| [08-sdp-harmonic-analysis-oliveira-vallentin.md](08-sdp-harmonic-analysis-oliveira-vallentin.md) | DeCorte-Oliveira-Vallentin (2022); Oliveira (2016); Vallentin (2008 notes, 2014 slides); Briet-Oliveira-Vallentin (2010) | A2/A3 |
| [09-knuth-dancing-links.md](09-knuth-dancing-links.md) | Knuth TAOCP V4 Pre-Fascicle 5C *Dancing Links* (2019 draft) | A1 |
| [10-balogh-chen-li-hamming-distance.md](10-balogh-chen-li-hamming-distance.md) | Balogh-Chen-Li (2026), Hamming-cube distance graph | (adjacent; A3 methods) |
| [11-keleti-matolcsi-oliveira-ruzsa-avoiding-sets.md](11-keleti-matolcsi-oliveira-ruzsa-avoiding-sets.md) | Keleti-Matolcsi-Oliveira-Ruzsa (2016), planar avoiding sets | A2/A3 (primary source for $m_1(\mathbb{R}^2)$; corrects note 08) |
| [12-ambrus-2023-density-planar-avoiding-sets.md](12-ambrus-2023-density-planar-avoiding-sets.md) | Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki (2023), $m_1 < 1/4$ | A2/A3 (the $\chi_m \ge 5$ density crossing = repo L35/L36; IEC template for e3k) |
| [13-ambrus-circle-tangential-vector-balancing-helly.md](13-ambrus-circle-tangential-vector-balancing-helly.md) | Ambrus-Bozzai (2023) vector balancing; Arun (2023) Helly numbers | tangential (Ambrus-circle adjacency) |

## Cross-cutting findings (the through-line on the bottleneck)

The single most important result of this read is that the library makes the $\chi \ge 6$
bottleneck **structural and explainable**, not merely "not done yet":

1. **The chromatic lever and the embeddability lever are decoupled** (notes 01, 05). The
   governing invariant is the *Euclidean dimension* of a graph (Soifer Ch 13):
   $\mathrm{Edim}(G) \le 2\Delta(G)$ (Lovasz-Saks-Schrijver), so whether a graph embeds in
   the plane as a unit-distance graph is controlled by **maximum degree, not chromatic
   number**. The graphs that embed (flexible, low-degree, high-girth) are exactly the ones
   hard to push past $\chi = 4$. O'Donnell's embedding machinery (Ch 14) embeds abstract
   graphs by attaching odd cycles to a foundation independent set, which can force a 4th
   color but never a 5th. The entire 25-year embedding literature produced only $\chi = 4$
   UDGs by this route.

2. **The $\chi = 5$ constructions escaped via rigidity, not flexibility** (note 05). de
   Grey / Exoo-Ismailescu / Voronov all reduce to a two-gadget pattern: gadget A forces a
   *monochromatic equilateral triangle* (via the $\sqrt 3$ distance, plus $\sqrt{11}$ when a
   Moser spindle is present) in every 4-coloring; gadget B forbids it locally. The
   load-bearing object is the rigid $\sqrt 3 / \sqrt{11}$ structure absent from
   $\mathbb{Q}^2$. This is the opposite of O'Donnell's flexibility bet.

3. **Two concrete obstacles to $\chi \ge 6$** (note 05): (a) *gadget side* - forcing every
   5-coloring needs a small 5-chromatic rigid base to replace the spindle, and none is known
   (the smallest 5-chromatic UDG is ~509 vertices, and SAT-minimization strips its symmetry,
   so 5-chromaticity does not concentrate in a small rigid core); (b) *computational side* -
   Voronov report Kissat could not decide 5-colorability of a ~29k-54k-vertex iterated
   product in 1 CPU-month, and a 5-coloring blocker must kill far more colorings than a
   4-coloring blocker. No impossibility theorem exists, only a consistent cost explosion.

4. **A2/A3 can make continuous progress while A1 is stuck** (notes 03, 04, 08, 11; repo L35/L36).
   $\chi_f(\mathbb{R}^2)$ and $\chi_m(\mathbb{R}^2)$ are real-valued targets pushed by better
   fractional cliques / better measures, needing no integer $\chi \ge 6$ graph. The operator
   Hoffman/Lovasz bound (Bachoc et al.) turns this into an SDP over measures, with Euclidean
   rigidity entering through the Bessel symbol $\hat\nu = J_0$ of the unit-distance convolution
   operator. The Oliveira-Vallentin lineage (note 08) upgrades this: the cone of **completely
   positive** functions characterizes the max density $m_1(\mathbb{R}^2)$ of a distance-avoiding
   set *exactly* (a convergent Lasserre-type hierarchy $\vartheta' = \mathrm{las}_1 \ge
   \mathrm{las}_2 \to \alpha$). **Quantitative ledger (settled against the KMOR and Ambrus primaries
   and the repo's own L35/L36):** the bare 2-point $J_0$ LP gives $m_1(\mathbb{R}^2) \le 0.2683$
   ($\chi_m \ge 4$); KMOR 2016's point-set bound $m_1 \le 0.258795$ was just short ($\chi_m \ge 4$);
   and **Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 reaches $m_1 \le 0.246894 < 1/4$, giving
   $\chi_m(\mathbb{R}^2) \ge 5$** (inclusion-exclusion congruence constraints on a 23-point config;
   reproduced and self-certified in-repo, L35/L36). So the single-class density route DOES reach
   $\chi_m \ge 5$. (The measurable $\chi_m \ge 5$ is ALSO Falconer 1981, by a separate earlier
   argument.) The figure $0.229$ is Croft's LOWER bound, not an upper bound.

5. **Hard ceiling (notes 08, 11; repo L36): the density route is CAPPED at $\chi_m(\mathbb{R}^2) \ge 5$
   and cannot reach $\ge 6$.** Croft's explicit avoiding-set construction has density $0.22936$, so
   $m_1(\mathbb{R}^2) \ge 0.22936 > 1/5$, hence $1/m_1 \le 4.36 < 5$. The density bound
   $\chi_m \ge 1/m_1$ therefore cannot certify 6 (it would need $m_1 < 1/5$). Pushing the
   *measurable* number past 5 needs a fundamentally different functional (multi-point /
   multi-class / multi-distance), not a sharper single-set density. This is a SECOND, independent
   obstruction, distinct from the A1 "$\chi \ge 6$ embeddable graph" bottleneck. Detector-clean
   (correctly norm/dimension dependent; $\mathbb{R}^1$ degenerate; $\mathbb{Q}^2$ measure-exempt).

6. **The verify-a-$\chi\ge6$-claim pipeline is well-understood** (note 06). Encode 5-colorability
   as one-hot CNF (+ $K_3$ symmetry breaking), solve with cadical/kissat/cryptominisat emitting
   a DRAT proof, independently check UNSAT with `drat-trim` (giving $\chi \ge 6$ via de
   Bruijn-Erdos), then trim to a small vertex-critical witness via Heule's proof-optimization.
   The bottleneck is geometric (finding the graph), not certificational.

7. **A4 is orthogonal but sharpened** (notes 01, 02). The unit-distance Shelah-Soifer graph
   (Payne, Soifer Ch 46.7) has $\chi_{ZFC} = 2$ but $\chi_{ZFS} \ge 3$, built by tiling with
   translated Woodall-$\mathbb{Q}^2$ copies. Kechris supplies the regularity package (analytic
   sets are universally measurable + have the Baire property) that a *Borel* chromatic number
   would rest on, but the actual result (Kechris-Solecki-Todorcevic 1999, the $G_0$ dichotomy)
   is a library gap. Note also: de Bruijn-Erdos, which licenses the whole SAT program, requires
   the Axiom of Choice (flagged repeatedly in Soifer).

## Detector check (all confirmed in-corpus)

- $\chi(\mathbb{Q}^2) = 2$ (Woodall): proved in Soifer Ch 11 via the odd-denominator coset
  mechanism. Every $\chi = 5$ construction's rigidity ($\sqrt3$, $\sqrt{11}$) is exactly what
  fails over $\mathbb{Q}^2$. (Note 01, 05.)
- $\chi(L^\infty \text{ plane}) = 4$ (Chilakamarri): NOT in this corpus; the spectral bound
  "moves with the unit ball," so it is not blind to the norm (note 04).
- $\chi(\mathbb{R}^1) = 2$: the A2 Fourier route routes through the 2D Bessel symbol $J_0$
  (not the 1D $\cos$), so it genuinely uses $O(2)$; the 1D analogue correctly returns 2
  (note 03, 04).

## Library gaps surfaced by the read (priority for acquisition)

- ~~Ambrus-Csiszarik-Matolcsi-Varga-Zsamboki 2023 (the $m_1 < 1/4$ / $\chi_m \ge 5$ density paper)~~
  **ACQUIRED 2026-05-30** (note 12). Was previously only a `.tex` in `experiments/fractional/_cache`;
  now the PDF is in `sources/papers/`. Note 12 extracts the IEC congruence construction in full and
  gives a concrete "Formulation 2" (joint-pattern cross-color IEC) as the candidate path for the
  e3k multi-class LP toward $\chi_m \ge 6$.
- ~~Oliveira-Vallentin SDP / distance-avoiding-set papers~~ **ACQUIRED 2026-05-30** (note 08:
  DeCorte-Oliveira-Vallentin 2022 + Oliveira 2016 + Vallentin 2008/2014). These were the prior
  top gap; they reach $\chi_m \ge 5$ and prove the $\ge 6$ density ceiling.
- ~~Keleti-Matolcsi-Oliveira-Ruzsa (2016)~~ **ACQUIRED 2026-05-30** (note 11). Reading it
  corrected note 08: the true upper bound is $m_1(\mathbb{R}^2) \le 0.258795$ ($\chi_m \ge 4$),
  and $0.229$ is Croft's lower bound. Remaining sub-gap: Croft's original 1967 paper for the
  lower-bound construction details (cited, not in-library).
- **Kechris-Solecki-Todorcevic, "Borel chromatic numbers" (1999)** (A4): the $G_0$ dichotomy
  (note 02).
- **Polymath16 reduction narrative** (A1): blog/wiki only, no clean arXiv paper.
- **Falconer 1981 original** (A2): pre-arXiv (note 01 has the proof via Soifer Ch 9).
- **Full Knuth TAOCP V4F6** (A1): we have only the ~54-page sample (note 06).
