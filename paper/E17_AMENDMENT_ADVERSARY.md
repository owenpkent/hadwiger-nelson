# ADVERSARY report: the E17 amendment to the C1 paper (paper/main.tex)

Target: the uncommitted working-tree amendment that folds the E17 exhaustive
enumeration into the forcing-sterility + codegree note. Scope: correctness,
honesty, and publication-readiness of the PAPER as written, before commit and
arXiv upload. Ground truth: `experiments/combinatorial/e17_results.md`,
`e17_verification.md`, `e17_adversary.md` (all PASSED at code level), and
`experiments/LEARNINGS.md` L75.

Method: read the full diff (`git diff paper/main.tex paper/refs.bib
paper/arxiv/ARXIV_SUBMISSION.md`) and the full amended `main.tex` in context;
cross-checked every number against e17_results.md and the two vetting reports;
re-derived Lemma 2 by hand; re-derived the four search-space reductions and their
conjunction; extracted and standalone-compiled the arXiv tarball with
`~/.TinyTeX/bin/x86_64-linux/pdflatex` (no bibtex, as arXiv's AutoTeX does).

---

## Surface 1 - Numerical fidelity

Every headline number in the new Section 7 (sec:exhaustive), abstract, Table 2
(tab:e17), calibration/epistemic paragraphs, and outlook was checked against
e17_results.md and L75.

| Claim in paper | Location | Ground truth | Match |
|---|---|---|---|
| 11,315 order-16 candidates | abstract, Sec 7 proof, Table 2, disc. | e17_results.md L75/L109/L623 | yes |
| 11,291 DSATUR + 24 SAT (= 11,315) | Sec 7 proof, Table 2 | run log line 109 | yes |
| window 43..48 at n=16 | Sec 7 reduction (iii), Table 2 | window table line 39 | yes |
| windows 13:[35,35] 14:[38,39] 15:[41,43] | Table 2 | window table lines 36-38 | yes |
| class members 13->0, 14->0, 15->11, 16->11315 | Table 2 | run log lines 106-109 | yes |
| 15 split 9 DSATUR + 2 SAT | Table 2 | run log line 108 | yes |
| calibration counts 352 / 2001 / 15481 (n=7,8,9) | calibration para | gate (a), line 57 | yes |
| Shrikhande srg(16,6,2,2), codeg 2 everywhere, chi=4 | calibration para | gate (b), line 58 | yes |
| n<=16 verdict; smallest, if any, has n>=17 | Thm 2, abstract, disc. | verdict lines 111-118 | yes |
| n=17 wall: 4 parts of a 4096-split each >1700 cpu-s, > ~80 cpu-days | outlook | lines 87-89, 76 | yes |
| per-order multiplier ~29x to ~100x | outlook | lines 93-94 (100x, >29x) | yes |
| heuristic order ~26 | abstract, disc. target | Sec 6 density para (unchanged) | yes |

Arithmetic re-derived independently: KY floor = ceil(2.8n - 1.8) gives
43/38/41/35 at n=16/14/15/13; codegree ceiling floor(n(1+sqrt(8n-7))/4) gives
48/39/43/35. At n=16, (28*16-18)/10 = 43 exactly and 8*16-7 = 121 = 11^2 so the
ceiling is exactly 16*12/4 = 48. Windows match Table 2 exactly. The wall product
4096 * 1700 s = 80.6 days, consistent with "above roughly 80 cpu-days" (correctly
stated as a lower bound, since no sample part finished).

One imprecision, not a mismatch. Section 7 proof says the 24 SAT residues were
"each confirmed by three independent solvers." The original E17 run decided the
24 with a single in-process solver (Cadical195, e17_results.md line 109); the
three-solver confirmation is the post-hoc ADVERSARY pass (glucose42, minisat22,
Cadical195, plus randomized greedy; `e17_adversary.md` Attack 4). The phrase is
factually supported (three distinct solver codebases each returned SAT on each
residue), but Cadical195 is also the original decider, so strictly only two
confirmations are independent of the original decision. This is a wording nuance,
not a numeric error, and the underlying fact (all 24 genuinely 5-colorable,
4 methods, 0 disagreements) is over-determined. See Surface 5 for the related
acknowledgments-naming point.

Verdict: **SOUND** (one wording nuance flagged for Surface 5; no numeric error).

---

## Surface 2 - Theorem 2 and Lemma 2 soundness as written in LaTeX

**Theorem 2 (thm:exhaustive)** states: the class of K4-free, K_{2,3}-free graphs
contains no member with chi >= 6 on at most 16 vertices; hence the smallest such
graph, if one exists, has order at least 17. This is exactly the E17 verdict
(e17_results.md lines 111-118) and exactly the claimed scope (class = K4-free AND
K_{2,3}-free; chi >= 6; n <= 16; the n>=17 corollary). No overclaim.

**Lemma 2 (lem:maxdeg), re-derived from scratch.** Claim: every K_{2,3}-free
graph on n vertices with min degree >= 5 has max degree <= (n-1)/2. K_{2,3}-free
(as a subgraph) is equivalent to codegree <= 2 for every pair. Fix a. Count pairs
(w, x), w in N(a), x ~ w, x != a. Left: S = sum_{w~a}(deg w - 1) >= 4 deg(a) since
deg w >= 5. Right, grouping by x: S = sum_{x != a} |N(a) cap N(x)| <= 2(n-1) since
each codegree is <= 2 and there are n-1 endpoints. Hence 4 deg(a) <= 2(n-1), i.e.
deg(a) <= (n-1)/2 for every a. The paper's printed proof is exactly this and is
complete: it uses min degree >= 5 (for deg w - 1 >= 4) and K_{2,3}-freeness (for
codegree <= 2), and both are stated. The double count has no hidden double
counting (an edge ww' inside N(a) contributes 2 to each side symmetrically).
Matches VERIFIER Lemma A and ADVERSARY Attack 3 (exhaustively confirmed at
n=11..14). Not just gesturing: fully rigorous as printed.

**The four reductions and exhaustiveness of their conjunction.** The reduction to
a 6-critical member is correct: any chi >= 6 member contains a 6-critical subgraph
H; K4-freeness and K_{2,3}-freeness are subgraph-closed, so H is in the class at
order n(H) <= 16. H then satisfies all four constraints simultaneously: (i)
2-connected and min degree >= 5 (6-critical => min degree >= k-1 = 5, 2-connected;
cited JensenToft1995); (ii) KY floor m >= 2.8n - 1.8 (H is 6-critical; cited
KostochkaYancey2014); (iii) codegree ceiling (H is K_{2,3}-free); (iv) maxdeg cap
(Lemma 2). The n <= 12 window is empty (KY floor exceeds ceiling), so any such H
has n(H) in {13,...,16}, all of which are enumerated. The prune's subgraph-
monotonicity is stated correctly (both forbidden subgraphs persist along geng's
vertex-augmentation order, so rejecting at first appearance loses no class member;
the final graph is also checked, giving soundness). The contrapositive is valid:
all enumerated graphs 5-colorable => no 6-critical class member on <= 16 vertices
=> no chi >= 6 class member. The -C (2-connectivity) restriction loses no critical
object because H is itself 2-connected. This matches ADVERSARY Attack 3 and
VERIFIER Target 3 line-by-line.

**Machine/solver-independence overclaim check.** The paper does NOT claim the
enumeration is machine-independent or solver-independent. The epistemic-status
paragraph explicitly states completeness "rests on geng together with the verified
prune lemmas; no independent second enumerator was run." The proof labels itself
"an exhaustive computer enumeration." This is the correct, standard framing for a
computer-assisted theorem (Folkman-number convention), and it is honest.

Verdict: **SOUND**.

---

## Surface 3 - Honesty and caveat integrity

Both carry-verbatim caveats are present and not softened:

- Caveat (i), completeness at n=15,16 rests on geng plus the verified prune lemmas
  with no independent second enumerator, same epistemic position as the
  Folkman-number literature: present verbatim in the epistemic-status paragraph
  ("enumeration completeness at n = 15, 16 rests on geng together with the verified
  prune lemmas; no independent second enumerator was run at those orders. This is
  the same epistemic position as the Folkman-number literature").
- Caveat (ii), the two counting lemmas are formalization-ready but not Lean-proved:
  present verbatim ("elementary, formalization-ready double-counting arguments, but
  they have not yet been machine-verified in a proof assistant").

Honest-scope survives in all the required places: abstract ("We claim no new bound
on chi(R^2)"), intro Scope-and-honesty ("We move no bound on chi(R^2)"),
epistemic-status ("bounds the abstract class only: it moves no bound on chi(R^2)
and says nothing about UDG-realizability"), and Discussion Honest-limitations
item 4 ("No bound on chi(R^2) moved"). The Discussion also keeps the necessity
caveat ("In-class membership ... is a necessary condition for UDG-realizability,
not a sufficient one").

No place lets a reader infer a chi(R^2) bound moved, nor that the object was FOUND
rather than EXCLUDED. Every statement of the result is a non-existence claim
("contains no member", "finds every candidate there 5-colorable"). The rigorous
n>=17 and the heuristic n~26 are kept explicitly distinct in both the abstract and
the target-object quote.

Verdict: **SOUND**.

---

## Surface 4 - Citation integrity

- McKayPiperno2014 (new): refs.bib and the shipped main.bbl give "Practical graph
  isomorphism, II", J. Symbolic Comput. 60 (2014) 94-112, with a note that geng is
  distributed with nauty. Correct venue, correct pages, correct year; this is the
  canonical nauty reference. geng is indeed the tool used (E17 built geng_hn from
  nauty 2.8.9), so the cite is apt. Cited at the three right places: Sec 7 proof,
  calibration para (implicitly via the generator), and acknowledgments.
- KostochkaYancey2014: cited at the KY floor in Sec 6 and Sec 7 reduction (ii).
  Correct.
- LathropRadziszowski2011: cited at the Folkman number F_v(2,2,2,2,2;4)=16 in
  Sec 6, Sec 7 proof, calibration ("reproduces the Folkman floor"), and epistemic
  status ("same epistemic position as the Folkman-number literature"). Correct.
- JensenToft1995: cited at "6-critical is 2-connected and min degree >= 5 (standard
  critical-graph theory)". Correct.

Optional (not required): the Shrikhande graph / srg(16,6,2,2) is named in the
calibration paragraph without a citation. It is a well-known object (like naming
the Petersen graph), so an uncited mention is acceptable in a note; a Shrikhande
1959 or Brouwer-van Lint-Wilson reference would be a courtesy, not a requirement.

Verdict: **SOUND** (optional Shrikhande cite only).

---

## Surface 5 - Internal consistency

- Contribution count: abstract and intro both updated from "threefold" to
  "fourfold" with a new item (d); "None of the four ingredients is individually
  deep". No stale "threefold" / "three ingredients" survives (grep-confirmed).
- Discussion pincer: updated from two "opposite sides" to "three sides" with a
  third bullet (in-class graph on <= 16 vertices). Coherent. Minor stylistic note:
  a "pincer" is idiomatically a two-sided squeeze; "pincer ... from three sides"
  is a mild malapropism but unambiguous. Optional reword only.
- Outlook: the three local searches are correctly reframed as "three heuristic
  directions and, at small orders, one exhaustive one"; "exhaustive for n <= 16
  and heuristic for n up to 64" is consistent with the greedy search's stated
  17 <= n <= 64 range. No stale "three heuristic negatives" / "three independent
  directions" survives.
- Cross-references and numbering (from the compiled main.aux): sec:exhaustive =
  Section 7, thm:exhaustive = Theorem 2, lem:maxdeg = Lemma 2, tab:e17 = Table 2,
  sec:discussion = Section 8 (correctly bumped from 7). Proposition 1, Theorem 1,
  Lemma 1, Corollary 1, Table 1 unchanged. All \ref targets resolve; zero
  undefined references or citations in the compiled PDF.
- No contradiction with unchanged parts: Proposition 1's n>=13 core floor is
  subsumed (not contradicted) by Theorem 2's n>=17 for the class; Section 6's
  ceiling value 48 at n=16 matches Table 2; Section 6's heuristic n~26 matches the
  target-object quote's "heuristically of order at least roughly 26".
- Related to Surface 1: the acknowledgments name the program's SAT solvers as
  "CaDiCaL, MapleChrono, and Glucose", but the E17 residues were confirmed by
  CaDiCaL, Glucose, and MiniSat (MapleChrono was not run on them; MiniSat is not
  in the acknowledgments list). Section 7's unnamed "three independent solvers" is
  therefore a different triple than the acknowledgments' triple. Not a
  contradiction (Section 7 never names them), but a meticulous referee could
  notice the mismatch. Optional fix below.

Verdict: **SOUND** (two optional stylistic/naming items).

---

## Surface 6 - Compile and bundle

- paper/main.pdf is 12 pages (pdfinfo), matching the "12 pp" now stated in
  ARXIV_SUBMISSION.md (updated from 10 pp in both the validation note and the
  Comments field).
- The arXiv tarball paper/arxiv/forcing-sterility-arxiv.tar.gz extracts to
  main.tex, refs.bib, main.bbl. The tarball's main.tex is byte-identical to the
  working-tree paper/main.tex (diff -q: IDENTICAL); refs.bib likewise IDENTICAL.
- Critical arXiv check (AutoTeX runs LaTeX, not BibTeX): the shipped main.bbl
  already contains \bibitem{McKayPiperno2014} with the correct nauty reference, and
  all 11 cited keys are present in the bbl. So the new citation will NOT be
  undefined on arXiv.
- Standalone compile of the extracted tarball with TinyTeX pdflatex, two passes,
  no bibtex: exit 0 both passes, 12 pages, zero undefined references or citations,
  no errors, no "rerun to get cross-references right" / label-change warnings.

Verdict: **SOUND**.

---

## Overall verdict

All six attack surfaces are SOUND. The amendment faithfully and defensibly
represents the (already code-vetted) E17 result: every number matches ground
truth, Theorem 2 and Lemma 2 are correct and complete as printed, the reduction
chain is exhaustive, the two mandated caveats and the honest-scope sentence
survive intact, the nauty citation is correct and present in the shipped bbl, the
numbering and cross-references resolve cleanly, and the tarball compiles standalone
to 12 pages with zero undefined references.

## Recommendation: **SHIP**

## Blocker list: EMPTY.

No FIX-FIRST blockers. Three optional, non-blocking refinements (BUILDER may take
or leave; none affects correctness or honesty of the headline):

1. (Optional, precision) paper/main.tex, Section 7 proof (the sentence "the
   remaining 24 decided satisfiable by a complete SAT solver, each confirmed by
   three independent solvers"): either name the three (CaDiCaL, Glucose, MiniSat)
   or soften to "each independently reconfirmed 5-colorable by multiple solvers",
   to avoid implying (a) that the original run used three solvers, or (b) that the
   three match the acknowledgments' "CaDiCaL, MapleChrono, and Glucose" (they do
   not; MapleChrono did not touch the E17 residues, MiniSat did).
2. (Optional, courtesy) paper/main.tex, calibration paragraph in Section 7: add a
   citation for the Shrikhande graph / srg(16,6,2,2).
3. (Optional, style) paper/main.tex, Discussion first sentence ("pincer the
   missing ingredient from three sides"): "pincer" reads as a two-sided squeeze;
   consider "hem in ... from three sides" or "corner ... from three sides".

PASS here means the amendment survives this attack; it does not certify the
underlying enumeration (that trust base is geng + the two prune lemmas, honestly
disclosed in the paper and stress-tested in e17_verification.md and
e17_adversary.md, but not machine-checked).
