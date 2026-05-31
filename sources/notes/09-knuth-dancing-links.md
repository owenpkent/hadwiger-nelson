# 09 - Knuth, TAOCP Vol 4, Pre-Fascicle 5C, "Dancing Links"

Source: `sources/books/Knuth-TAOCP-Vol4-PreFascicle5C-Dancing-Links.pdf`
Extracted text: `sources/_extracted/Knuth-TAOCP-Vol4-PreFascicle5C-Dancing-Links.txt`
Section number in the eventual book: 7.2.2.1 ("Dancing links"), inside 7.2.2 (backtracking).

CAVEAT: This is a 2019 PRE-FASCICLE, a circulated draft, not a finished volume. Knuth states it
"has not yet been proofread as thoroughly" as published volumes (preface, line 54), cross-references
to unwritten material appear as `00`, and many exercise attributions are unsettled. Page/equation
numbers below are extracted-text line numbers, not the book's printed numbers (the draft uses `()`
placeholders for nearly all its equation labels). Treat all of this as draft.

Architecture relevance: A1 (combinatorial / unit-distance-graph search). This is a TOOL note about
an alternative colorability engine, not a structural result about $\chi(\mathbb{R}^2)$.

## What this gives A1 (executive summary, 8 lines)

1. Dancing Links (DLX) is Knuth's data-structure for backtracking exact-cover search: a doubly
   linked list whose deleted nodes keep their own links so deletion is undone in O(1) by re-pointing.
2. Algorithm X solves exact cover (XC); Algorithm C solves exact cover with colors (XCC); both share
   nearly identical code (XCC adds a `COLOR` field plus `purify`/`unpurify`).
3. Graph $d$-coloring has a clean XCC encoding (exercise 117): one primary item per vertex, $d$
   secondary "color slots" per edge (or per clique), so adjacent vertices cannot share a color.
4. DLX/XCC produces explicit colorings (witnesses) and ENUMERATES all of them, with exact counts.
5. The natural branching rule is MRV (minimum remaining values): branch on the item with the
   shortest remaining option list (exercises 9, 10).
6. For HN, DLX gives a witness-finding and coloring-enumeration engine that complements SAT, and an
   exact-cover modeling language ("items / options") for construction/packing subproblems.
7. CRUCIAL LIMITATION for $\chi \geq k$: DLX proves non-$k$-colorability only by EXHAUSTIVE SEARCH.
   It emits NO compact, independently checkable certificate. SAT/CDCL with DRAT does.
8. So DLX is a witness/enumeration tool for A1; for the project's load-bearing $\chi \geq 6$ UNSAT
   claim, SAT + DRAT remains the certification path. DLX is a cross-check, not a certificate.

## DLX vs SAT for HN colorability (synthesis)

The A1 question is binary: is finite unit-distance graph $G$ $k$-colorable? Two engines answer it.

SAT (notes 06 lineage; de Grey, Heule, Polymath16). Encode $k$-colorability as CNF (one-hot: a
boolean $x_{v,c}$ per vertex-color, exactly-one-color clauses per vertex, and per edge the clauses
forbidding both endpoints taking color $c$). A CDCL solver returns SAT with a model (a coloring) or
UNSAT. The decisive asset is the UNSAT side: modern solvers emit a DRAT proof, an independently
machine-checkable certificate that $G$ is not $k$-colorable. That is exactly how de Grey's
$\chi \geq 5$ was verified (Heule's SAT proof). For a $\chi(\mathbb{R}^2) \geq k$ claim the
certificate IS the result; an unverifiable "my search found nothing" is not publishable.

DLX/XCC (this fascicle). Encode $k$-colorability as XCC (exercise 117) and run Algorithm C. On the
SAT side (a coloring exists) DLX is excellent: it returns an explicit coloring, and because it
"visits all solutions" it can enumerate every coloring and count them exactly (exercise 117 reports
exact $9$-coloring counts of the queen graph $Q_8$ and exact $c$-coloring counts of Mycielski graphs
$M_c$). On the UNSAT side DLX can also conclude non-colorability (exercise 117(f): "Use Algorithm C
to verify that $M_c$ can't be $(c-1)$-colored"), but ONLY by exhausting the search tree. There is no
DRAT analog. The "proof" is the assertion that the implementation ran to completion and found
nothing. That is not an independently checkable certificate; reproducing it means re-running the
same exhaustive search and trusting the same code.

When the project should reach for DLX:
- Enumerating / counting colorings of a finite UDG (e.g. how many 5-colorings does a Polymath16-style
  graph admit; which vertices are "color-forced"; how rigid is a near-critical core).
- Witness extraction with structure: finding colorings that satisfy extra side constraints, which map
  naturally onto extra primary/secondary items (Knuth's recurring point: constraints that are awkward
  for SAT are often one extra item in XCC).
- Modeling construction/packing subproblems of A1 (tiling, lattice/spindle assembly, geometric
  exact-cover puzzles) where the "items/options" language is the native fit.
- Fast independent CROSS-CHECK of a SAT-found coloring on small/medium cores.

When the project must use SAT instead:
- Any $\chi \geq k$ lower-bound CLAIM that needs to survive adversarial review: it needs UNSAT with a
  DRAT certificate (notes 06). DLX cannot supply this. This is the load-bearing case for the
  project's bottleneck (a $\chi \geq 6$ embeddable UDG), so SAT stays primary there.
- Very large graphs where CDCL clause learning prunes far more than chronological backtracking. DLX
  is chronological backtracking with a good data structure and the MRV heuristic; it has no learned
  clauses, no restarts, no conflict analysis. On hard UNSAT instances CDCL typically dominates.

Honest one-line verdict: DLX's strength is ENUMERATION and WITNESS-FINDING (the SAT side); for
NON-colorability CERTIFICATION (the UNSAT side that $\chi \geq k$ needs) it offers only exhaustive
search with no compact proof, so it does not replace SAT + DRAT for the project's central claim.

## Structured notes on the relevant sections

### The dancing-links idea (sec. 7.2.2.1 opening; lines 215-264)

In a doubly linked list with `LLINK(X)`/`RLINK(X)`, deletion of `X` is the usual two assignments:
`RLINK(LLINK(X)) <- RLINK(X)`, `LLINK(RLINK(X)) <- LLINK(X)`. The trick: do NOT recycle or clear
`X`'s own links. Then deletion is undone in O(1) by `RLINK(LLINK(X)) <- X`, `LLINK(RLINK(X)) <- X`
(lines 235-236). Because each removed node still remembers where it sat, a backtracking search can
remove a batch of nodes on the way down and restore them in exact reverse order on the way up,
in place, no copying. Knuth: "waltzing through the data structure at the same time as we're
modifying it" (line 724). The name is from the choreography of the pointers.

### Exact cover (XC), items and options (lines 265-345)

XC problem: an $M \times N$ 0/1 matrix; find a subset of rows summing to exactly 1 in every column.
Knuth reframes away from rows/columns to OPTIONS (rows) and ITEMS (columns): each option is a set of
items; find disjoint options covering every item exactly once (lines 341-345). The worked $6 \times 7$
example has options `c e`, `a d g`, `b c f`, `a d f`, `b g`, `d e g`; unique cover is options 1, 4, 5.

Data structure (lines 397-473): a horizontal doubly linked list of active items (`LLINK`/`RLINK`);
each item heads a vertical doubly linked list of the options containing it (`ULINK`/`DLINK`), with
each option-node pointing to its item header via `TOP`. Options are stored sequentially separated by
SPACER nodes (identified by `TOP(x) <= 0`) so each option can be traversed cyclically without storing
horizontal links. Item headers reuse the `TOP` slot as `LEN` = current length of that item's option
list (used by MRV).

### cover / uncover (the core primitives; lines 652-725)

`cover(i)`: for each option `p` still in item `i`'s vertical list, `hide(p)` removes the OTHER items
of that option from their lists; then unlink `i` from the horizontal item list.
`hide(p)`: walk the option containing `p`; for each non-spacer node, splice it out of its item's
vertical list and decrement that item's `LEN`.
`uncover(i)` / `unhide(p)`: the exact reverse, relinking in reverse order. Correctness rests on
undoing deletions in precisely reverse order so the dancing links restore the original state.

### Algorithm X (exact cover via dancing links; lines 726-748)

Recursive/iterative backtrack over levels `l`, maintaining `x0..xT` of chosen option-nodes.
- X2: if the item list is empty, record a solution.
- X3 [Choose i]: pick an active item; "The MRV heuristic of exercise 9 often works well" (line 736).
- X4-X5: cover `i`, try each option for `i`, covering its other items, descend.
- X6-X8: on return, uncover in reverse, backtrack.
Knuth's framing: every tentative choice leaves a SMALLER residual exact-cover problem (line 369),
which is why the dancing-links restore/undo discipline is the whole game.

### MRV heuristic (minimum remaining values; exercises 9, 10; lines 6306, 12356)

Exercise 9 answer (line 12356): scan the active item list, track the item with minimum `LEN`, branch
on it (and ties broken toward the lexically-first such item). Exit early if some item has `LEN = 0`
(a dead end, prune immediately). Exercise 10 adds a "sharp preference" variant. Item ORDER matters
too: for $n$ queens, "organ-pipe order" (center-out) beat natural order 40 vs 76 G-mems for $n=16$
(lines 911-921). Lesson for A1: the order in which vertices/items are presented to DLX measurably
changes runtime even with MRV; center-first / high-degree-first style orderings prune better.

### Secondary items (lines 792-899)

Items split into PRIMARY (must be covered exactly once) and SECONDARY (at most once). Implement by
listing only primaries in the active list (line 885). Secondary items model "at most one" / mutual
exclusion constraints directly. $n$ queens: rows and columns are primary (exactly one queen), the two
diagonal families are secondary (at most one). Avoids slack variables (lines 851-858).
Pairwise-ordering trick (lines 933-963) uses secondary items to break symmetry, e.g. 8-fold queen
symmetry, with $O(m \log m)$ extra entries.

### Exact cover with colors (XCC) and Algorithm C (lines 3245-3553)

XCC (definition, lines 3248-3262): primaries covered exactly once; each option may ASSIGN A COLOR to
its secondary items (written `item:color`). The relaxed rule: a secondary item may appear in many
chosen options PROVIDED they all give it the same color, i.e. "every secondary item has been assigned
at most one color." Ordinary XC is the special case where every secondary item gets an implicit
unique color (line 3259). This is the key generalization of the fascicle: Knuth calls color codes the
"most important takeaway" (lines 6116-6117).

Implementation: add a 4th node field `COLOR` (line 3268). Algorithm C is "almost word-for-word
identical to Algorithm X" (line 3533). Differences:
- `hide'`/`unhide'` ignore a node `q` whose `COLOR(q) < 0` (already-fixed correct color; lines 3495-3498).
- `purify(p)`: when an option fixes secondary item to color `c`, walk that item's list, mark
  same-color nodes with `COLOR <- -1` (kept) and `hide'` the conflicting-color nodes (lines 3506-3516).
- `commit(p,j)`: if the node is uncolored (`COLOR=0`) do `cover'(j)`, else `purify(p)` (line 3501).
- `unpurify` / `uncommit` reverse these. Same dancing-links undo discipline.

### GRAPH COLORING as XCC (exercise 117; lines 7688-7704, answer 16554-16570)

The standard encoding, directly usable for A1 unit-distance graphs:

(a) Basic: one PRIMARY item per vertex; per edge, $d$ SECONDARY items (one per color). Each vertex
$v$ gets $d$ options, the $j$-th being "assign color $j$ to $v$": option `v` plus, for every edge
incident to $v$, that edge's color-$j$ secondary item. Two adjacent vertices choosing the same color
$j$ would both claim the SAME edge-color-$j$ secondary item, which XCC forbids (secondary item gets
at most one "owner"/color), so the coloring is automatically proper. Knuth states (a) as the
clique-of-size-2 case of (b).

(b) Clique form (answer line 16555): if edges are given as a family of cliques $\{C_1,\dots,C_r\}$
($u \sim v$ iff both lie in some $C_j$), use $r \cdot d$ secondary items instead of one set per edge.
Each vertex $v$ has $d$ options `v c_{1j} ... c_{kj}` for $1 \le j \le d$, where $c_1,\dots,c_k$ are
the cliques containing $v$. This is dramatically more compact and faster: for $9$-coloring $Q_8$,
method (a) took 8.3 T-mems, method (b) only 0.6 T-mems (line 16559). Relevance: a unit-distance graph
is a union of unit-distance cliques (e.g. unit triangles / rhombi); the clique encoding fits its
structure and shrinks the model.

(d) Color-symmetry breaking (lines 7698-7701, 16560): each $k$-color solution is otherwise counted
$d(d-1)\cdots(d-k+1)$ times. Insert a secondary `v':j` ordering device to count each essentially
different coloring once; this also speeds search (method (a) on $Q_8$ dropped 8.3 -> 5.0 T-mems).

Concrete coloring benchmarks Knuth reports (answers, lines 16557-16570):
- $Q_8$ has 262164 distinct $9$-colorings (after fixing the top-row colors).
- Mycielski $M_c$ $c$-coloring counts: $M_2$:1, $M_3$:5, $M_4$:520, $M_5$:23713820 (times $c!$);
  estimated $M_6$ 6-colorable in ~$6! \cdot 2.0 \times 10^{17}$ ways (line 16566).
- NON-colorability via exhaustion (117(f)): Algorithm C verifies $M_c$ is NOT $(c-1)$-colorable, in
  roughly (100, 600, 5000, 300000) mems for $c=2..5$; 5-coloring $M_6$ took 45 T-mems (line 16568).
  These are the closest analog to an HN $\chi \geq k$ run, and they are pure exhaustive search.

The Mycielski family is itself HN-adjacent: $M_c$ is triangle-free with $\chi(M_c)=c$ and is
$\chi$-critical (exercise 116). It is a standard testbed for "high chromatic number from local
structure," conceptually parallel to (though not the same as) building a high-$\chi$ UDG.

### Hypergraph coloring (exercise 118; lines 7705, 16571)

Hypergraph coloring maps to Algorithm M (covering with multiplicities and colors): give multiplicity
$[0..(r-1)]$ to each hyperedge of size $r$. Not directly an HN tool, but signals that the XCC/MCC
framework extends to "no monochromatic line / set" constraints, which is the flavor of some
geometric Ramsey-type side conditions.

### Complexity and the certification gap (exercises 98, 117; lines 7418, 7703)

Exercise 98 (line 7418): the exact-cover-with-color-controls problem is NP-complete even when every
option has only two items. So XCC is as hard as SAT in the worst case; DLX does not change the
complexity class, it is a (very efficient) search engine. The practical difference is purely the
proof artifact: SAT/CDCL on UNSAT yields a DRAT certificate; Algorithm C on an unsatisfiable XCC
yields only "search exhausted." Exercise 117(f) is exactly an UNSAT-by-exhaustion run with no emitted
certificate. This is the single most important caveat for A1's lower-bound use.

### Performance notes / ZDD variant (lines 6099-6111, 5130-5137)

- Algorithm Z builds the solution set as a ZDD (zero-suppressed BDD), giving "spectacular
  improvements" when subproblems recur, but most exact-cover instances lack abundant common
  subproblems and gain little; for Langford $n=16$ it cut 1153 -> 450 G-mems but needed 20 GB RAM and
  a 500-million-node ZDD (line 6107). Likely not worth it for HN colorability unless heavy
  subproblem sharing appears.
- Preprocessing (Algorithm P) can prune options before search; on a structured sudoku-symmetry XCC
  with 585 primary + 90 secondary items it reduced 5410 -> 2426 options and ran 7.5x faster (lines
  5130-5137). For A1, a preprocessing pass on the UDG color model may pay off but is "a mixed bag"
  (line 5138).
- General-purpose DLX ran only ~5x slower than a hand-tuned bitwise $n$-queens solver (lines 922-924):
  the data structure is competitive with bespoke backtrack code, but it is still backtrack, not CDCL.

### Wrong-approach-detector check (project discipline)

DLX/XCC is a SOLVER, not a mathematical method, so the three control objects ($\mathbb{Q}^2$,
$L^\infty$ on $\mathbb{R}^2$, $\mathbb{R}^1$) do not "test" it the way they test a structural argument.
What matters: the colorability VERDICT DLX returns is exactly the graph-theoretic chromatic number of
whatever finite graph you hand it. So if one fed DLX a finite subgraph of the $\mathbb{Q}^2$
unit-distance graph, it would correctly find it $2$-colorable (consistent with Woodall 1973,
$\chi(\mathbb{Q}^2)=2$); if one fed it the Moser spindle it returns $\chi=4$. DLX cannot
manufacture a wrong lower bound: any non-$k$-colorability it reports is a true property of the
specific finite graph. The detector discipline therefore applies to HOW the graph is CONSTRUCTED
(BUILDER's job), not to the DLX decision step. No detector violation arises from using DLX itself.
Flag: DLX gives no compact certificate, so a reported lower bound is only as trustworthy as the
implementation; this is a verification risk, not a wrong-approach risk.

## Discrepancy log

- No disagreement with the atlas on mathematics. This fascicle is a tools reference, not an HN result.
- One emphasis difference to flag for SYNTHESIZER: project A1 doctrine treats SAT as THE colorability
  engine (notes 06). This fascicle shows a credible alternative (DLX/XCC) that is arguably superior
  for the SAT-side tasks (enumeration, counting, witness extraction, structured side constraints) but
  strictly inferior for the UNSAT-side certification that $\chi \geq k$ requires. The atlas should
  record DLX as a complementary engine, not a replacement.

## What this enables / what remains open

Enables (for BUILDER / VERIFIER):
- A second, independent colorability engine for A1. Recommended use: encode candidate UDGs via the
  XCC clique form (exercise 117(b)) and use Algorithm C to (i) cross-check SAT-found colorings,
  (ii) enumerate and count colorings of near-critical cores, (iii) probe color-forcing and rigidity.
- A modeling language (items/options, primary/secondary, colors, multiplicities) for the geometric
  construction/packing subproblems A1 keeps running into.
- A concrete reference encoding to implement in `experiments/combinatorial/` alongside the SAT path
  (the UDG interface could grow a `chromatic_number_xcc(k)` returning a coloring or "exhausted").

Remains open / explicitly NOT solved here:
- DLX does NOT help with the project's load-bearing need: a compact, checkable certificate that a
  $\chi \geq 6$ UDG is non-$5$-colorable. That stays with SAT + DRAT. DLX's "UNSAT" is exhaustive
  search only (exercise 98 NP-completeness; exercise 117(f) is exhaustion).
- Whether a DLX/XCC run on Polymath16-scale graphs (~500-1581 vertices) is time-competitive with CDCL
  on the relevant non-colorability instances is UNTESTED in this fascicle and should be benchmarked
  empirically before relying on it. Knuth's data is on puzzles, not large near-critical UDGs.
- The bottleneck (an embeddable $\chi \geq 6$ unit-distance graph) is a CONSTRUCTION problem; DLX is a
  decision/enumeration engine and does not address construction. It can verify/enumerate candidates
  BUILDER proposes, nothing more.
