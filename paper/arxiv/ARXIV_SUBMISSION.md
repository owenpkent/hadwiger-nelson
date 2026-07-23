# arXiv submission packet: C1 (forcing-sterility + codegree note)

Ready-to-upload bundle and the metadata to paste into the arXiv submission form.
Venue decision (2026-06-16): **arXiv + Geombinatorics** (both).

## The upload file

`forcing-sterility-arxiv.tar.gz` (flat archive, 3 files):
- `main.tex` - the paper source
- `refs.bib` - the bibliography database
- `main.bbl` - the **compiled** bibliography

**Why the `.bbl` is included.** arXiv's current processing (the "Submission 1.5"
system, since April 2025) uses the shipped `main.bbl` if present, and otherwise
auto-detects and runs a bib-compiler (bibtex/biber). Shipping the compiled `.bbl`
is the safe, recommended practice (and is strictly required for non-standard bib
processors); the `.bbl` basename must match the main `.tex`. The bundle was
validated to compile standalone with `pdflatex` alone (no bibtex): **12 pages,
zero undefined references or citations.** Upload the tarball as-is.
Source: https://info.arxiv.org/help/submit_tex.html (verified 2026-07-23).

To regenerate the tarball after any edit to the paper:
```
cd paper
pdflatex main && bibtex main && pdflatex main && pdflatex main   # refresh main.bbl
cd arxiv
tar czf forcing-sterility-arxiv.tar.gz ../main.tex ../refs.bib ../main.bbl --transform 's,.*/,,'
# flat archive with main.tex at the top level. arXiv also accepts subdirectories,
# but flat is cleanest and is what this bundle ships.
```

## Step-by-step submission procedure (verified 2026-07-23)

All facts below were checked against arXiv's live help pages on 2026-07-23;
source URLs are inline. This is the primary/first submission, so the endorsement
step is the one that can actually block you: settle it first.

0. **Endorsement, before anything else.** See the account note below. A first-time
   `math.CO` author now needs a personal endorser (the academic-email shortcut was
   removed 2026-01-21). Arrange one, or start the submission and use the code arXiv
   shows you to request it.
1. **Log in / register** at https://arxiv.org with `owenpkent@gmail.com`.
2. **Start a new submission**, agree to the license terms, and pick a **license**
   (full option set below; CC BY 4.0 recommended).
3. **Upload the source**, not the PDF. arXiv rejects PDF built from LaTeX source;
   submit `forcing-sterility-arxiv.tar.gz` as-is
   (https://info.arxiv.org/help/submit/index.html). Total-size cap is 50 MB; this
   bundle is ~16 KB (https://info.arxiv.org/help/sizes.html).
4. **Let AutoTeX/Submission-1.5 build** and inspect the arXiv-generated PDF preview.
   Expect one benign hyperref warning from the `$\ge 6$` in the title; zero
   undefined refs/citations otherwise.
5. **Paste the form fields** (title, authors, categories, MSC, comments, abstract)
   from the "Form fields" section below.
6. **Submit.** The paper enters a **moderation queue**; moderators may reclassify
   the category or place a hold before it appears
   (https://info.arxiv.org/help/moderation/index.html). You get an identifier at
   submission; public listing happens at the next announcement.
7. **Announcement timing**: deadline **14:00 US Eastern**, announced **20:00 US
   Eastern**, Sunday through Thursday (nothing Fri/Sat; a submission in the Thu
   14:00 to Fri 14:00 window rolls to Sunday 20:00). A holiday freeze calendar
   applies, confirm the date on
   https://info.arxiv.org/help/availability.html .
8. **Then Geombinatorics** (parallel, by email) once the arXiv ID exists, so the
   preprint can be referenced. See that section below.

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

**License:** choose at submission. Owen's call. Full current option set
(https://info.arxiv.org/help/license/index.html, verified 2026-07-23):
1. arXiv.org perpetual non-exclusive license 1.0 (the "distribute" default)
2. **CC BY 4.0** (recommended for maximum reuse)
3. CC BY-SA 4.0
4. CC BY-NC-SA 4.0
5. CC BY-NC-ND 4.0
6. CC0 1.0 (public-domain dedication)

## arXiv account note

A first-time arXiv submission to `math.CO` requires **endorsement** unless the
account is already endorsed for the category. Endorsement is per endorsement
domain and does not carry across archives.

**Policy change to know (verified 2026-07-23).** As of 2026-01-21 (and 2025-12-10
for Mathematics specifically), an institutional/academic email **alone no longer
auto-endorses** a new author. Automatic endorsement now requires BOTH an academic
email AND prior authorship on an accepted arXiv paper in that domain. A genuinely
first-time author (no prior arXiv paper) will therefore need a **personal
endorsement from an established `math.CO` author**, even with a university email.
Line this up before submitting. Nothing in this bundle can resolve it.
Sources: https://info.arxiv.org/help/endorsement.html ,
https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/

## Geombinatorics (the parallel submission)

Geombinatorics submits by **email to the editor** (it is not an online-portal
journal). Verified 2026-07-23 on https://geombina.uccs.edu/editors-page :
- **Editor and Publisher:** Alexander Soifer (University of Colorado, Colorado
  Springs).
- **Send:** the PDF (`paper/main.pdf`) to **asoifer@uccs.edu**, together with a
  hand-signed copyright form (emailed as a JPEG attachment, or mailed).
- The journal is active as of 2026 (up to ~Vol. XXXVI). The de Grey (2018) and
  Parts (2020) papers in this lineage both appeared there, so it is the natural
  home for this note.
- Do this after the arXiv ID exists, so the preprint can be referenced.
- Re-confirm the copyright-form format and any current instructions on the
  editors page before sending.
