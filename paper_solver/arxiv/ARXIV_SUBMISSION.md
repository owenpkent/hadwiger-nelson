# arXiv submission packet: C3 (symmetry-broken SAT self-certification)

Ready-to-upload bundle and the metadata to paste into the arXiv submission form.
Planned framing: arXiv `cs.DM` primary + `math.CO` cross-list; the SAT workshop
(Pragmatics of SAT) is the alternate venue.

## The upload file

`symmetry-broken-sat-arxiv.tar.gz` (flat archive, 3 files):
- `main.tex` - the paper source
- `refs.bib` - the bibliography database (web-verified)
- `main.bbl` - the **compiled** bibliography

**Why the `.bbl` is included.** arXiv's AutoTeX runs LaTeX but does **not** run
BibTeX; the bibliography comes from the shipped `main.bbl`. The bundle was
validated to compile standalone with `pdflatex` alone (no bibtex): **7 pages, zero
undefined references or citations.** Upload the tarball as-is.

To regenerate after any edit to the paper:
```
cd paper_solver
pdflatex main && bibtex main && pdflatex main && pdflatex main   # refresh main.bbl
cd arxiv
tar czf symmetry-broken-sat-arxiv.tar.gz ../main.tex ../refs.bib ../main.bbl --transform 's,.*/,,'
# (or copy the three files in flat and tar them; the archive must be flat, no leading dir)
```

## Form fields (paste these)

**Title**
```
Symmetry-broken SAT self-certifies the plane's chi >= 5 lower bound (and where it stops)
```

**Authors**
```
Owen Kent
```
(Independent researcher. Correspondence: owenpkent@gmail.com.)

**Primary category:** `cs.DM` (Discrete Mathematics)
**Cross-list:** `math.CO` (Combinatorics)

**MSC class:** 05C15, 05C85, 68T20
**ACM class:** F.2.2, G.2.2

**Comments:** `7 pages`

**Abstract** (plain text; arXiv accepts inline `$...$`):
```
The lower bound $\chi(\mathbb{R}^2) \ge 5$ on the chromatic number of the plane
rests on certifying that specific finite unit-distance graphs (UDGs) are not
4-colorable. These certifications are k-colorability SAT instances whose naive
one-hot encoding carries the full k! color-permutation symmetry, and several of
them have been reported as practically intractable. We report a simple but
decisive engineering result: exporting a sound symmetry break (clique-fixing plus
first-appearance color precedence) as a CNF preamble lets an off-the-shelf CDCL
solver decide all of them, each with an optional machine-checkable DRAT proof.
Concretely, $M^4(C_5)$ at $k=6$ (UNSAT) is intractable under the naive encoding
but a 22 s solve once broken; the 510-vertex Polymath16 graph at $k=4$ (UNSAT)
drops from ~110 s to 1.66 s; and de Grey's 1585-vertex graph at $k=4$ (UNSAT), the
actual $\chi(\mathbb{R}^2) \ge 5$ certificate, from ~92 min to 18 min. The entire
known $\chi(\mathbb{R}^2) \ge 5$ computational program is thereby self-certifiable
on a single workstation. We pair this with two methodological findings. First, a
portfolio law: near the colorability phase boundary, single-solver runtime is
heavy-tailed and misleading; on one identical in-class instance CaDiCaL did not
finish in 12 hours while MapleChrono returned SAT in 155 seconds (a factor
exceeding 270). Second, an honest regime boundary: the symmetry break crushes
structured UNSAT but does not tame phase-transition hardness, so it certifies
everything currently known and does not shortcut the search for a new chi >= 6
object. The symmetry break itself is standard; the contribution is wiring it into
the Hadwiger-Nelson pipeline, measuring that it crosses the specific walls, and
mapping where it stops.
```

**License:** choose at submission (CC BY 4.0 recommended). Owen's call.

## Notes

- A first-time arXiv submission to `cs.DM` may require **endorsement** unless the
  account is already endorsed for the category. One-time human step.
- **Reproducibility**: all timings are from open-source components (PySAT ->
  CaDiCaL / MapleChrono / Glucose) on one workstation. The de Grey 18.1 min figure
  is backed by `experiments/combinatorial/e1u_degrey_symbreak_k4.py` (cached). The
  equisatisfiability / soundness validation is in
  `experiments/_shared/symbreak_bench.py`.
- **SAT-workshop alternate**: if targeting Pragmatics of SAT or a similar venue
  instead of (or in addition to) arXiv, the same source builds; check the venue's
  page limit and LIPIcs/whatever style requirement before reformatting.
