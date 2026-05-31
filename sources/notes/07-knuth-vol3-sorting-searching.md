# Knuth, TAOCP Vol 3: "Sorting and Searching" - Reference Notes

Source: `sources/books/Knuth-TAOCP-Vol3-Sorting-and-Searching.pdf` (792 pp, 2nd ed. 1998).

**Important:** this PDF is a **scanned image with no text layer** (text extraction yielded
0 words). These notes are therefore a *structural reference* compiled from the book's known
organization, not a close reading of this copy. To search or quote it you would need to OCR
the PDF first (e.g. `ocrmypdf` or `tesseract`). It is also the least HN-relevant text in the
library: a general algorithms reference, not a chromatic-number source. Kept for
implementation craft, not for the mathematics of the problem.

## Relevance to the project (honest assessment)

This book serves **no** proof architecture directly. Its value is purely as an
implementation backstop for the A1 computational pipeline (`experiments/combinatorial/`),
where the real work is graph construction in exact arithmetic and SAT solving. Specific
points where it could help:

- **Hashing (Ch 6.4)** for *coincidence detection*. The hardest engineering step in the
  Voronov / de Grey / Heule embedding constructions is "removing coincidences": when you
  build a unit-distance graph by Minkowski sums and rotations, many generated points
  collide and must be identified as one vertex. That is a dictionary/hashing problem over
  exact algebraic coordinates (elements of $\mathbb{Q}(\sqrt3,\sqrt{11})$ etc.). Hashing
  canonical exact representations is exactly Ch 6.4 material. (See Soifer notes Ch 14.6
  "Removing Coincidences" and the SAT-machinery notes on $G_{2167}$.)
- **Sorting / searching (Ch 5, 6.1-6.2)** for edge-list canonicalization, deduplication,
  and nearest-pair queries when verifying that claimed edges are exactly unit distance
  (cf. `sources/cnp-sat/check/check_dist_one.py`).
- **Balanced trees / digital search (6.2-6.3)** for spatial indexing if a search ever needs
  approximate-then-exact unit-distance neighbor lookups at scale.

None of this touches the chi >= 6 bottleneck mathematically; it only affects how fast and
how correctly the construction code runs.

## Structural map (for navigation; standard TAOCP Vol 3 contents)

**Chapter 5 - Sorting**
- 5.1 Combinatorial properties of permutations (inversions, runs, tableaux, Young
  tableaux / RSK correspondence).
- 5.2 Internal sorting: insertion, exchange (incl. quicksort), selection (heapsort),
  distribution; detailed average-case analyses.
- 5.3 Optimum sorting: minimum-comparison sorting and merging, selection (lower bounds via
  decision trees).
- 5.4 External sorting: merge patterns, polyphase/cascade merge, tape/disk models.
- 5.5 Summary, history, bibliography of sorting.

**Chapter 6 - Searching**
- 6.1 Sequential searching.
- 6.2 Searching by comparison of keys: binary search, binary search trees, balanced trees
  (AVL), multiway trees (B-trees).
- 6.3 Digital searching: tries, Patricia.
- 6.4 **Hashing**: hash functions, separate chaining, open addressing, analysis of load
  factor. (The most likely useful chapter for this project, per above.)
- 6.5 Retrieval on secondary keys.

## Action items

- If exact-coordinate coincidence detection ever becomes a bottleneck in BUILDER code, the
  reference is Ch 6.4; pair a canonical exact-arithmetic key (sympy normal form) with a hash
  table rather than pairwise distance checks (which are $O(n^2)$ and dominate large-graph
  assembly).
- If close text reference to this volume is ever needed, OCR it first; until then treat it
  as a paper-only reference.
