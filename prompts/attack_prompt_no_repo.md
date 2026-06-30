# Hadwiger-Nelson attack prompt (no-repo twin)

A self-contained creative-attack brief for a model that does NOT have this repo.
Precedence: the canonical, always-current brief is the `DEFAULT_BRIEF` in
[`.claude/workflows/hn-lens-attack.js`](../.claude/workflows/hn-lens-attack.js),
backed by [`experiments/LOAD_BEARING_FACTS.md`](../experiments/LOAD_BEARING_FACTS.md)
and [`experiments/FREEZE_LIST.md`](../experiments/FREEZE_LIST.md). This twin inlines
a frozen gist so a foreign model can work without file access. Re-sync it when the
frontier moves.

---

PROBLEM. The Hadwiger-Nelson problem: the chromatic number $\chi(\mathbb{R}^2)$ of
the unit-distance graph on the Euclidean plane (vertices = all points, edges = pairs
at distance exactly 1). Known: $5 \le \chi \le 7$ (de Grey 2018 lower via a 1581-vertex
unit-distance graph; Isbell hexagonal coloring upper).

FOUR ARCHITECTURES.
1. Combinatorial / unit-distance graphs: build a finite UDG with $\chi \ge 6$.
2. Measurable / spectral: lower-bound the measurable chromatic number $\chi_m$.
3. Fractional / Lovász $\vartheta$: fractional $\chi_f$ and Cayley-operator spectra.
4. Set-theoretic / Borel: the choice-axiom dependence and the Borel chromatic number.

THE ONE MISSING OBJECT (build on this; do not re-derive it).
- A unit-distance-realizable flexible color-clamp: a $\chi=5$ UDG with a NON-adjacent
  pair $(s,t)$ forced to different colors in EVERY proper 5-coloring. Contracting
  $s=t$ then forces $\chi \ge 6$. The ABSTRACT object exists (a SAT-verified
  48-vertex triangle-free witness). ALL difficulty is realizability in $\mathbb{R}^2$.
- Theorem R (exact iff): the clamp realizes IFF the host minus the split vertex
  realizes with the two neighbor-sets each on a radius-1 circle with DISTINCT centers.
- The known $\chi=5$ lineage (de Grey / Polymath, 199 to 874 vtx) is FORCING-STERILE:
  every non-adjacent pair is free. The missing object must come from a NEW UDG on a
  different principle, and it must be K4-free, 6-critical, and $K_{2,3}$-free (two unit
  circles meet in $\le 2$ points).
- Measurable: the order-2 SDP route at the relevant configuration is CLOSED. $\chi \le
  \chi_m$ always, and $\chi_m \ge 6$ does NOT imply $\chi \ge 6$.

THE THREE WRONG-APPROACH DETECTORS (every proposal must self-check against all three).
- $\mathbb{Q}^2$: the rational plane has $\chi = 2$ (Woodall). A combinatorial argument
  that lifts naively to $\mathbb{Q}^2$ (would give $\chi(\mathbb{Q}^2) \ge 3$) is wrong.
- $L^\infty$ plane: $\chi = 4$ (Chilakamarri). A geometric argument valid in every
  normed plane is wrong; it must use Euclidean rigidity (equilateral triangles,
  cocircularity, two-circle intersection).
- $\mathbb{R}^1$: $\chi = 2$. A measure-theoretic argument blind to the rotation group
  $O(2)$ is wrong.

KNOWN KILLS (do not re-propose): long-range forcing inside the known lineage;
single-vertex-port gadget chains; "RG leading eigenvalue" as a forcing diagnostic;
DOF/over-determination counting for realizability; norm-blind Borel/Steinhaus bounds;
map-type 6-colorings (Voronov needs 7); order-1/order-2 moment relaxations for
$\chi_m$; treating $\chi_m \ge 6$ as if it implied $\chi \ge 6$.

YOUR TASK. Reason from FIRST PRINCIPLES through whatever lens you are strongest in.
Derive why the Euclidean plane specifically (vs $\mathbb{Q}^2$, $L^\infty$,
$\mathbb{R}^1$) exhibits the structure you propose. Produce 2-4 PRECISE, FALSIFIABLE
conjectures, at least one of which you believe is unstated in the literature, each
with a concrete computation that would refute it. For each, run all three detectors
yourself. Wild but precise beats safe but vague. No em dashes.
