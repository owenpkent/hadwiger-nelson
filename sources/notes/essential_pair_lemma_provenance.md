# Provenance check: the Essential-Pair Lemma

SURVEYOR provenance note. Scope: a targeted literature check on whether the
project's "Essential-Pair Lemma" is already known. Not a broad survey.

## The lemma under check

Project statement (see `paper/main.tex`, Section "The Essential-Pair Lemma",
Lemma `lem:essential` and Corollary `cor:critical-free`):

> Let G be k-chromatic and (s,t) a non-adjacent pair that is *forced*
> (forced-same: every proper k-coloring has c(s)=c(t); or forced-different:
> every proper k-coloring has c(s)!=c(t)). Then chi(G - s) >= k and
> chi(G - t) >= k.
>
> Corollary: a vertex-critical k-chromatic graph has no forced non-adjacent pair.

The project currently hedges this as "elementary, we are not aware of the exact
statement, possibly folklore" (`paper/main.tex` lines 199-204, 512-517).

## VERDICT

**(b) The lemma is an explicit, named result in a (non-refereed) preprint, and
its critical-graph corollary is stated and proved verbatim there.** It should be
attributed, not claimed as folklore-without-citation. The closest match is exact,
not approximate. The one caveat is that the source is an arXiv preprint with no
journal-ref, so it is best described as "stated in the literature but not, to our
knowledge, in a refereed venue."

### Primary reference (exact match)

**Jose Antonio Martin H., "Graph-Chromatic Implicit Relations," arXiv:0901.1255
[math.CO], 9 Jan 2009** (dated Oct. 2006 in the body; self-archived elsewhere as
"Hidden Edges in Graph Coloring"). No journal-ref, no DOI beyond the arXiv DOI;
appears to have remained an unrefereed preprint.

This paper's vocabulary is the project's vocabulary under a translation:

| Project term            | Martin 2009 term      | Definition                                   |
|-------------------------|-----------------------|----------------------------------------------|
| forced-different pair   | **implicit-edge** (non-drawn) | non-adjacent {i,j}, c(i)!=c(j) in every k-coloring (Def. 3.1) |
| forced-same pair        | **implicit-identity** | non-adjacent {i,j}, c(i)=c(j) in every k-coloring (Def. 3.8)  |

The exact corollary is **Theorem 3.17, "there are no implicit relations in
critical graphs"** (Section 3.6, p. 11-12). Its proof is the project's
contrapositive verbatim:

- Implicit-identity {a,b} (forced-same): "G - a remains k-chromatic which is
  absurd due to G is critical." This is exactly chi(G - s) >= k for forced-same.
- Implicit-edge {a,b} (forced-different, non-drawn): "the graph with vertices a
  and b removed (G - a - b) remains k-chromatic," contradicting criticality.

The single-vertex deletion consequence for the forced-different case is also
present, one inferential step away, in the proof of **Theorem 3.2** (p. 4-5,
"Implicit Edges and Independent Sets") and **Theorem 3.4** ("Implicit Edge
invariant"): both run the same "(k-1)-color G-s, give s the new color k"
construction the project uses in its proof sketch. So the project's exact
phrasing (delete *one* endpoint) is recoverable from Martin's Theorems 3.2/3.4
and is what Theorem 3.17(i) does for the forced-same half.

Nuance worth flagging: Martin's Theorem 3.17 proof for the *implicit-edge* half
deletes *both* endpoints (G - a - b), which is a slightly weaker statement than
the project's chi(G - s) >= k for a single s. The single-vertex version for
forced-different is the natural strengthening and follows from the same one-line
recolor argument (give s color k after a (k-1)-coloring of G - s); the project's
proof sketch is correct and is essentially Martin's Theorem 3.2 argument run
once. So: the corollary (critical => no forced pair) is identical; the precise
single-deletion lemma is a trivial sharpening of what Martin writes.

### Secondary reference (same author, follow-on)

**Jose Antonio Martin H., "Minimal non-extensible precolorings and
implicit-relations," arXiv:1104.0510 [math.CO], 2011.** Re-uses the
implicit-edge / implicit-identity framework (here: implicit-edges and
implicit-identities arising from 2-vertex non-extensible precolorings). Same
notion of forced same/different color, framed via precoloring extension. Closeness:
same concept, same author, but the critical-graph corollary is the 2009 paper.

### Standard-compendium anchor (for the "this is standard critical-graph theory" framing)

**T. R. Jensen and B. Toft, "Graph Coloring Problems," Wiley, 1995** (cited as
[17] inside Martin 2009). The underlying facts the lemma rests on (in a k-critical
graph every vertex is critical, chi(G - v) = k - 1; the deletion/recoloring moves)
are standard Dirac-Gallai critical-graph theory catalogued there. I did **not**
locate a statement in Jensen-Toft phrased directly as "no non-adjacent pair in a
critical graph is forced same/different." So Jensen-Toft supports the *framing*
("immediate from standard critical-graph facts") but is not a citable instance of
the exact statement. Honest caveat: I checked Jensen-Toft by topic via secondary
sources and the Martin citation, not by a full page-level read of the 1995 book.

## What I read vs. did not read

- **Read in full (text-extracted from PDF):** Martin 2009 (arXiv:0901.1255), all
  14 pages, including Definitions 3.1/3.8, Theorems 3.2, 3.4, 3.17, and Section
  3.6 on critical graphs. Quotations above are from that extraction.
- **Read abstract/metadata only:** Martin 2011 (arXiv:1104.0510); the abstract
  and table of contents (sections on critical and double-critical graphs).
- **Not opened directly (topic-level only):** Jensen-Toft 1995; the
  Dirac/Gallai/Ore/Stiebitz-Toft critical-graph primary literature. The
  "uniquely colorable graphs" / "defining sets" survey literature
  (e.g. Mahmoodian et al.) uses a *different* notion (uniqueness of the whole
  partition), which is related but not the per-pair forcing notion; I did not
  find the exact pairwise statement there.

## Recommended attribution language for the paper

Replace the current "we are not aware of this exact statement" hedge with:

> The lemma is elementary and is essentially known. The corollary, that a
> vertex-critical k-chromatic graph admits no forced non-adjacent pair, appears
> as Theorem 3.17 ("there are no implicit relations in critical graphs") of
> Martin [Graph-Chromatic Implicit Relations, arXiv:0901.1255, 2009], where
> forced-different and forced-same pairs are called implicit-edges and
> implicit-identities; the single-deletion form we use is a one-line sharpening
> of his Theorems 3.2 and 3.17. The result is also implicit in standard
> critical-graph theory (Dirac-Gallai; see Jensen and Toft, Graph Coloring
> Problems, 1995). We state and prove it for self-containedness and make no
> priority claim.

If the authors prefer to be conservative about citing an unrefereed preprint:
state it as "we are not aware of a refereed source, but the statement appears as
Theorem 3.17 of the preprint [Martin 2009] and is immediate from standard
critical-graph facts (Jensen-Toft 1995)."

## Discrepancy log

- The project's `paper/main.tex` (lines 199-201, 514-516) and the `% TODO:
  literature check` comments assert "we are not aware of this exact statement."
  This survey contradicts that: the exact statement (corollary form) is
  Theorem 3.17 of Martin 2009. Flagging, not silently editing main.tex. The
  hedge should be downgraded from "apparently new / folklore" to "known, see
  [Martin 2009]; possibly also folklore in critical-graph theory."
- The project uses "forced-same / forced-different / clamp"; Martin uses
  "implicit-identity / implicit-edge." A reader cross-referencing should be told
  the translation, since Martin's "implicit-edge" is the *different*-color
  relation (counterintuitive: an "edge" forces *different* colors), which is the
  reverse of the naming intuition one might expect.

## What this enables / what remains open

- **Enables (for the paper / SYNTHESIZER):** the Essential-Pair Lemma can be
  attributed cleanly. The `% TODO: literature check` comments in `paper/main.tex`
  can be resolved by inserting the Martin 2009 citation and the Jensen-Toft
  framing. This removes the only open priority hedge in Section "The
  Essential-Pair Lemma."
- **Enables (for BUILDER / ADVERSARY):** Martin 2009 also contains adjacent
  machinery the program may want: the Kempe-chain characterizations (Thms 3.15,
  3.16) of forced pairs, and the chromatic-polynomial reduction P(G/e,k)=0 for an
  implicit-edge (Thm 3.12). These give alternate certificates of forcing beyond
  the SAT route used in the lineage census, and may be a faster filter.
- **Remains open (provenance):** I did not page-read Jensen-Toft 1995 nor the
  Stiebitz-Toft critical-graph survey; a refereed primary source for the exact
  pairwise statement (if one exists) was not found. If the authors want a
  refereed citation rather than a preprint, a deeper read of Jensen-Toft and the
  Stiebitz-Scheide-Toft-Favrholdt graph-edge-coloring book is the next step. The
  preprint's lack of a journal-ref is the only weakness in the citation.
- **Remains open (math):** none for the lemma itself. It is settled. The forcing
  *absence* in the realizable lineage (the program's actual obstruction) is a
  separate, still-open structural question and is unaffected by this provenance
  result.
