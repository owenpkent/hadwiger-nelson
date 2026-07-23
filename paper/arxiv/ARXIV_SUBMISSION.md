# arXiv submission packet: C1 (forcing-sterility + codegree note)

Ready-to-upload bundle and the metadata to paste into the arXiv submission form.
Venue decision (2026-06-16): **arXiv + Geombinatorics** (both).

## The upload file

`forcing-sterility-arxiv.tar.gz` (flat archive, 3 files):
- `main.tex` - the paper source
- `refs.bib` - the bibliography database
- `main.bbl` - the **compiled** bibliography

**Why the `.bbl` is included.** arXiv's AutoTeX runs LaTeX but does **not** run
BibTeX. The bibliography therefore comes from the shipped `main.bbl`. The bundle
was validated to compile standalone with `pdflatex` alone (no bibtex):
**12 pages, zero undefined references or citations.** Upload the tarball as-is.

To regenerate the tarball after any edit to the paper:
```
cd paper
pdflatex main && bibtex main && pdflatex main && pdflatex main   # refresh main.bbl
cd arxiv
tar czf forcing-sterility-arxiv.tar.gz ../main.tex ../refs.bib ../main.bbl --transform 's,.*/,,'
# (or copy the three files in flat and tar them; the archive must be flat, no leading dir)
```

## Form fields (paste these)

**Title**
```
Forcing-sterility of the realizable unit-distance lineage and a codegree obstruction to chi >= 6
```

**Authors**
```
Owen P. Kent
```
(Independent researcher. Correspondence: owenpkent@gmail.com.)

**Primary category:** `math.CO` (Combinatorics)
**Cross-list:** `math.MG` (Metric Geometry)

**MSC class:** 05C15, 52C10 (optionally 05C10)

**Comments:** `12 pages`

**Abstract** (plain text; arXiv accepts inline `$...$`):
```
The chromatic number of the plane, $\chi(\mathbb{R}^2)$, is known only to lie in
$[5,7]$. The lower bound $\chi(\mathbb{R}^2) \ge 5$ rests on finite unit-distance
graphs (UDGs): de Grey (2018) exhibited the first such graph with $\chi \ge 5$,
and the Polymath16 project reduced the order to roughly 510 vertices. A natural
route to $\chi(\mathbb{R}^2) \ge 6$ would locate, somewhere in this realizable
lineage of $\chi = 5$ UDGs, a non-adjacent vertex pair forced to distinct colors
in every proper 5-coloring (a clamp); realizing such a pair lifts the chromatic
number to 6. This note records a negative structural result: the realizable
lineage contains no such forcing, and provably so. We recall an elementary lemma
(the Essential-Pair Lemma, essentially known) which implies that a vertex-critical
5-chromatic graph cannot host any forced non-adjacent pair. We confirm the
consequence by an exhaustive computational census: all 1,955,948 non-adjacent
pairs across the nine $\chi = 5$ lineage graphs are free, with zero forced pairs
of either kind. Since the lineage is vertex-critical, this is a one-line corollary
of the Lemma, and the deeper point is conceptual: the lineage was produced by
SAT-driven minimization, which drives graphs toward vertex-criticality, and
criticality deletes exactly the vertices that could host forcing. The lineage is
forcing-sterile by construction. We then frame the search for the missing
$\chi \ge 6$ object through a codegree obstruction: every planar UDG is
$K_{2,3}$-free, so its edge count is bounded by $m \le n(1+\sqrt{8n-7})/4$;
combined with the Kostochka-Yancey lower bound for 6-critical graphs and the
vertex Folkman number $F_v(2,2,2,2,2;4) = 16$, this excludes every small dense
Folkman-type host. The missing object must lie in the class of graphs that are
simultaneously $K_4$-free and $K_{2,3}$-free. For that class we prove an
exhaustive negative: a custom-pruned geng enumeration over the full edge window
between the Kostochka-Yancey floor and the codegree ceiling shows that the class
contains no member with chromatic number at least 6 on at most 16 vertices (all
11,315 candidates in the order-16 window are 5-colorable), so the smallest such
graph, if one exists, has at least 17 vertices; density heuristics place it
closer to order 26 or beyond. We claim no new bound on $\chi(\mathbb{R}^2)$.
```

**License:** choose at submission (CC BY 4.0 recommended for maximum reuse; the
arXiv non-exclusive default is also fine). Owen's call.

## arXiv account note

A first-time arXiv submission to `math.CO` may require **endorsement** unless the
account is already endorsed for the category. If prompted, that is a one-time
human step (request endorsement from an established author or via an institutional
email). Nothing in this bundle can resolve it.

## Geombinatorics (the parallel submission)

Geombinatorics submits by **email to the editor** (it is not an online-portal
journal). The deliverable is the same `paper/main.pdf`. Confirm the current
editor and submission instructions on the journal page before sending; the de
Grey (2018) and Parts (2020) papers in this lineage both appeared there, so it is
the natural home for this note.
