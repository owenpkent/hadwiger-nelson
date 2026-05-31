# SAT Machinery for Architecture A1: Heule (2019) + Knuth TAOCP V4F6

Research notes on the SAT-solving and proof-certification technology behind the
Hadwiger-Nelson Architecture A1 program (deciding $k$-colorability of finite
unit-distance graphs). Two sources:

1. Donald E. Knuth, *The Art of Computer Programming*, Vol 4, Fascicle 6,
   "Satisfiability" (Section 7.2.2.2), 2015. **NOTE: the extracted text is only a
   ~54-page free SAMPLE of the full ~310-page fascicle.** See the "Sample scope"
   caveat below.
2. Marijn J. H. Heule, "Trimming Graphs Using Clausal Proof Optimization", 2019,
   arXiv:1907.00929v2. Read in full (a 15-page paper).

---

## Executive summary: what this gives Architecture A1 (the SAT toolchain)

1. **Encoding.** A graph $G=(V,E)$ is $k$-colorable iff the CNF $F_k$ is SAT, using
   $k\lvert V\rvert$ one-hot variables $x_{v,c}$, "at-least-one-color" vertex clauses,
   and "adjacent-differ" edge clauses (Heule Sec 6.1; Knuth (15)-(17)).
2. **Lower bound.** $\chi(G)\ge k+1$ iff $F_k$ is UNSAT and $F_{k+1}$ is SAT.
   For A1 the load-bearing run is: $F_4$ UNSAT $\Rightarrow \chi\ge 5$; for $\chi\ge 6$
   we need $F_5$ UNSAT on a candidate graph.
3. **Symmetry breaking.** Fix three mutually-adjacent vertices to colors 1,2,3.
   Gives a ~$4\cdot3\cdot2 = 24\times$ speedup for $k=4$ (Heule Sec 6.1).
4. **At-most-one-color clauses are optional** (Knuth (17), Heule Sec 6.1): extra colors
   per vertex are harmless; blocked-clause elimination removes them anyway.
5. **Certificate.** Modern solvers emit a *clausal proof* of UNSAT (DRAT/DRUP),
   checkable in low-degree polynomial time by an independent checker via Reverse Unit
   Propagation (RUP) (Heule Sec 2).
6. **Independent verification.** A third party re-runs `drat-trim` on (CNF, proof) and
   trusts the UNSAT claim without trusting the solver. This is exactly how de Grey's
   $\chi\ge 5$ was confirmed by Heule.
7. **Core extraction = subgraph extraction.** An unsatisfiable core of $F_k$ is a
   subgraph that is still non-$k$-colorable. Shrinking the core shrinks the witness graph.
8. **Proof size correlates with core size** (Heule's central empirical observation):
   smaller UNSAT proof $\Rightarrow$ smaller core $\Rightarrow$ smaller witness graph.
9. **Trimming.** Heule's pipeline iteratively optimizes the proof to shrink the core,
   reducing the smallest known $\chi=5$ unit-distance graph from 553/2720 to 529/2670.
10. **Result data lives in repo.** The 529-vertex graph is `sources/cnp-sat/{vtx,edge}/529.*`
    with CNF `cnf/529-4.cnf`; sibling graphs 510, 517, 553, G2167 are present too.

---

## The verify-a-$\chi\ge 6$-claim pipeline (end-to-end)

This is the concrete recipe a BUILDER + VERIFIER pair would follow to credibly
establish and check $\chi(\mathbb{R}^2)\ge 6$ from a candidate unit-distance graph $G$,
drawing on both texts. It mirrors the established $\chi\ge 5$ pipeline (de Grey,
Polymath16, Heule) with $k$ shifted from 4 to 5.

**Step 0: get a candidate graph $G=(V,E)$ embeddable in the plane.**
This is the project bottleneck and is *not* a SAT task. It is BUILDER's job. The graph
must have exact unit-distance coordinates, conventionally in a number field such as
$\mathbb{Q}[\sqrt 3,\sqrt{11}]\times\mathbb{Q}[\sqrt 3,\sqrt{11}]$ (Heule Sec 5; the
de Grey/Polymath lineage). Heule's construction method (Minkowski sums of hexagon
graphs $H_R$, rotations $\theta_i$, merging) is the template for generating large
candidates; he built graphs up to 100,000 vertices this way (all 5-colorable, Heule
Sec 7). A $\chi\ge 6$ graph, if it exists, would be found by similar exploration.

**Step 1: encode $F_5$ (and $F_6$).** Build the CNF deciding whether $G$ is 5-colorable
using the one-hot encoding (Heule Sec 6.1, Knuth (15)-(16)):
- $5\lvert V\rvert$ variables $x_{v,c}$, $c\in\{1,\dots,5\}$.
- Vertex clauses $(x_{v,1}\lor\cdots\lor x_{v,5})$ for each $v$.
- Edge clauses $(\bar x_{v,c}\lor\bar x_{w,c})$ for each $\{v,w\}\in E$, each $c$.
- Omit at-most-one-color clauses (optional; Knuth (17), Heule Sec 6.1).
To certify $\chi(G)=6$ exactly you also encode $F_6$ and check it is SAT (a coloring
witness), but for the *lower bound* $\chi\ge 6$ only $F_5$ UNSAT is required.

**Step 2: add symmetry-breaking predicates.** Pick a triangle of three mutually
unit-distant vertices (a $K_3$, present in every CNP graph) and fix them to colors
1, 2, 3 via unit clauses. For $k=5$ this gives a $5\cdot4\cdot3 = 60\times$ color-symmetry
reduction (the $k=4$ analog was $24\times$, Heule Sec 6.1). Crawford-style lex-leader
predicates (Knuth, "Symmetry breaking", index p.105; Heule ref [6]) generalize this.
Store the symmetry-broken instance as the `*-5-sbp.cnf` analog of the repo's
`*-4-sbp.cnf` files.

**Step 3: solve $F_5$ and emit a clausal proof.** Run a modern CDCL solver that emits a
DRAT/DRUP proof on UNSAT. The repo's CLAUDE.md names **cadical / kissat / cryptominisat**;
Heule used **glucose 3.0** (Sec 6.2) with randomized VSIDS initialization. Knuth's
"Algorithm C" (CDCL, Knuth index p.62-71, 132) is the conceptual solver class here.
If UNSAT: emit `proof.drat`. If SAT: $G$ is 5-colorable, $\chi(G)\le 5$, reject this
candidate and return to Step 0.
- *Practical*: randomize the decision heuristic seed and solve many times; keep the
  smallest proof (Heule Sec 6.2 found proof sizes ranging 1,809 to 49,838 clause-addition
  steps across 100 seeds on the same formula). Small proof now pays off in Step 5.

**Step 4: independently check the proof.** Run **`drat-trim`** (Heule-Hunt-Wetzler;
https://github.com/marijnheule/drat-trim) or a formally-verified checker (Knuth
mentions verified checkers; Heule refs [7,19], e.g. the ACL2 and Isabelle-verified
checkers) on (CNF, `proof.drat`). The checker validates each added clause by RUP:
assign all literals in the clause to false, run unit propagation against the
accumulated formula, confirm a conflict (Heule Sec 2). This is **polynomial-time and
solver-independent**: the verifier does not trust the SAT solver at all. A clean run
certifies $F_5$ UNSAT, hence $\chi(G)\ge 6$, hence $\chi(\mathbb{R}^2)\ge 6$ (by
de Bruijn-Erdos, the finite-graph bound lifts to the plane; Heule Sec 1, ref [4]).
The proof should be "small enough to verify in a few seconds", which Heule explicitly
achieved for the 529 graph (Sec 6.3).

**Step 5 (optional but expected): trim to a minimal witness.** Use Heule's clausal
proof optimization (Sec 4) to shrink the UNSAT core, i.e. the witness subgraph, so the
published result is a small vertex-critical graph rather than the bulky search graph.
This is `OptimizeProof` + `TrimFormulaInteract` + the classical destructive
minimal-core pass (Heule Fig 3-4, Sec 4.2). Output: a small $\chi=6$ graph plus its
short DRAT proof, both publishable and re-checkable.

**Trust chain.** The only trusted code is the proof checker (`drat-trim` or a
verified checker). The SAT solver, the encoder, and the graph generator can all be
buggy: a bad encoding or a wrong UNSAT claim would be caught at Step 4. This is what
made de Grey's $\chi\ge 5$ believable: Marijn Heule re-derived and DRAT-checked the
UNSAT, so the community did not have to trust de Grey's solver.

**Detector-discipline note (project wrong-approach check).** This pipeline is honestly
combinatorial (Arch 1) and respects the controls: the encoding uses only the abstract
graph $G$, but the *graph itself* is built from Euclidean rigidity (unit distances,
$K_3$ triangles, hexagon Minkowski sums in $\mathbb{Q}[\sqrt3,\sqrt{11}]$). The SAT
machinery does not "lift to $\mathbb{Q}^2$" because the input graph does not embed in
$\mathbb{Q}^2$ with the same chromatic number ($\chi(\mathbb{Q}^2)=2$, Woodall). The SAT
toolchain is content-neutral: it certifies $\chi(G)$ for whatever $G$ you feed it, so the
detector burden lives entirely in Step 0 (the graph), not in Steps 1-5 (the certification).

---

## Per-text notes 1: Knuth, TAOCP V4F6 "Satisfiability" (the sample)

### Sample scope: what this excerpt DOES and does NOT cover

The full fascicle is ~310 pages (front matter says viii + 310). The table of contents
(lines 242-309) lists the real structure: Example applications (p.4), Backtracking
algorithms (p.27), Random clauses (p.47), Resolution of clauses (p.54), Clause-learning
algorithms (p.60), Monte Carlo algorithms (p.77), the Local Lemma (p.81),
Message-passing (p.90), Preprocessing (p.95), Encoding constraints (p.97), Unit
propagation and forcing (p.103), Symmetry breaking (p.105), Satisfiability-preserving
maps (p.107), 100 test cases (p.113), Tuning (p.124), Parallelism (p.128), History
(p.129), Exercises (p.133), Answers (p.185), Index (p.292).

**The extracted text contains ONLY:**
- Front matter: preface, contents, notation notes (lines 1-321).
- **The full "Example applications" subsection, pages 1-26** (lines 323-2375). This is
  the problem definition + ten worked SAT formulations.
- **The Index and Glossary, pages 292-310** (lines 2376-4544).

**The extracted text does NOT contain the body of:**
- Backtracking algorithms (Algorithm A brute-force, Algorithm B, **Algorithm D = DPLL**,
  Algorithm L = lookahead with the BIMP/TIMP structures) -- only named in TOC/index.
- Resolution of clauses (resolution rule, resolution proofs, width, the Davis-Putnam
  operation) -- only named.
- **Clause-learning algorithms (Algorithm C = CDCL): conflict analysis, learned clauses,
  watched literals, VSIDS activity scores, restarts, purging** -- only named in TOC and
  index (CDCL index entry p.62-71, 132).
- **Unit propagation and forcing** as a standalone treatment (p.103) -- only named;
  unit propagation is *used* informally in the examples.
- **Certificates of unsatisfiability / clausal proofs (p.69-71)** -- only named in the
  index ("Certificates of unsatisfiability, 69-71, 157, 169, 176, 178"; "Clausal proofs,
  see Certificates of unsatisfiability"). The RUP/RAT/DRAT machinery that A1 most needs
  is therefore in the full fascicle, **not in this sample**. (Heule's paper is the actual
  source for that machinery in these notes.)
- **Autarkies** (index p.44, 71, 146, 152, 177, 214-217; "Autarky principle, 44") -- only
  named.
- **Symmetry breaking** body (p.105-114) -- only named; the index entry explicitly lists
  "in graph coloring, 99-100, 114, 171, 179, 187" and "lex-leader 111, 283".
- All exercises and answers, the 100-benchmark empirical study, tuning, parallelism, history.

So: for everything except the *encoding of problems into CNF*, this sample tells you a
technique exists and points at a page, but does not give the algorithm. A reader must
consult the full fascicle (or, for proofs/certificates, Heule's paper and the DRAT
literature) for CDCL internals, resolution theory, and certificate formats.

### Problem definition and notation (lines 331-489)

- **CNF / SAT.** $F(x_1,\dots,x_n)$ in conjunctive normal form = AND of clauses, each
  clause an OR of literals. Satisfiable iff some assignment makes $F=1$. Knuth example (1).
- **Literal / variable / complement.** $\bar v$ is the complement; $\lvert l\rvert$ is the
  underlying variable; $l$ positive if $\lvert l\rvert = l$. Strictly distinct literals
  have distinct variables.
- **Set view.** A clause is a set of literals; a formula is a set of clauses; shorthand
  drops braces, e.g. $F=\{1\bar2,23,\bar1\bar3,\bar1\bar23\}$ (Knuth (3)). *A1 use*: this
  is exactly how `.cnf` DIMACS files encode the coloring instance.
- **SAT as a covering problem** (Knuth (4)): satisfiable iff coverable by a set $L$ of
  strictly distinct literals (one per variable). $T_n = \{\{x_i,\bar x_i\}\}$ forces a
  consistent total assignment.
- **kSAT, unit/binary/ternary clauses, empty clause $\epsilon$** (always false, the UNSAT
  witness), **tautological clauses** $\wp$ (contain $v$ and $\bar v$, harmless and dropped).
  *A1 use*: the empty clause $\epsilon$ being derived is precisely the end of a $\chi\ge k+1$
  UNSAT proof.
- **Monotonic clauses** (all literals same sign), e.g. the van der Waerden clauses. Knuth
  notes (exercise 10) any formula can be made monotonic, so monotonicity is no easier.

### The ten example encodings (the heart of the sample, pages 4-26)

For each: what it is, and a one-line "how A1 graph-coloring instances use it".

1. **van der Waerden / equally-spaced-digits** `waerden(j,k;n)` (Knuth (9)-(10), lines
   490-628). Clauses forbidding $j$ equally spaced 0s or $k$ equally spaced 1s; SAT iff
   $n < W(j,k)$. State-of-the-art SAT solvers computed large $W(j,k)$ and lower bounds.
   *A1 use*: archetype of "SAT decides an extremal-combinatorics threshold", which is
   exactly the $\chi\ge k$ question (find $n$/graph where the constraint flips to UNSAT).

2. **Exact cover / Langford pairs** `langford(n)`, `langford'(n)` (Knuth (11)-(14), lines
   629-693). Encodes "select rows so each column appears once" via the
   **at-most-one / exactly-one $S_1$ function**. Two encodings: naive
   $1+\binom{p}{2}$ clauses (Knuth (13): one at-least-one clause + pairwise
   $(\bar y_j\lor\bar y_k)$), versus a $3p-5$-clause encoding with auxiliary variables
   (Knuth, exercise 12). *A1 use*: the pairwise "$\bar y_j\lor\bar y_k$" is identical in
   form to the edge clauses $(\bar x_{v,c}\lor\bar x_{w,c})$ and to the optional
   at-most-one-color clauses (Knuth (17)). The auxiliary-variable trick is how you avoid
   $\binom{k}{2}$ blowup when $k$ is large.

3. **Graph coloring** (Knuth (15)-(17), lines 694-710). THE directly relevant encoding.
   $nd$ variables $v_j$ = "$v$ has color $j$"; clauses:
   - (15) at-least-one-color: $(v_1\lor\cdots\lor v_d)$ for each vertex.
   - (16) proper: $(\bar u_j\lor\bar v_j)$ for each edge $u\!-\!v$ and color $j$.
   - (17) at-most-one-color: $(\bar v_i\lor\bar v_j)$ -- **OPTIONAL**; "vertices with more
     than one color are harmless". Knuth notes a multi-color solution just gives extra
     valid colorings.
   *A1 use*: this is **exactly Heule's encoding** (Sec 6.1) with $d=k$. McGregor graph
   example: 110 vertices, 324 edges $\to$ 1406 clauses on 440 variables, "a modern SAT
   solver can polish off quickly". The repo `cnf/*-4.cnf` files are this construction at
   $d=4$.

4. **Cardinality constraints** (Knuth (18)-(21), lines 853-928). For bounding the number
   of vertices of one color:
   - **Sinz sequential-counter** (Knuth (18)-(19)): $(n-r)r$ new variables $s^k_j$,
     encodes $x_1+\cdots+x_n\le r$. Used to cap McGregor's red regions at 7 with 1538
     clauses / 721 vars.
   - **Bailleux-Boufkhad binary-tree (totalizer)** (Knuth (20)-(21)): even better; 1216
     clauses / 399 vars for the same. Built on a complete binary tree with $b^k_j$ counter
     variables.
   - Identity $S_{\ge r}(x)=S_{\le n-r}(\bar x)$ flips at-least into at-most.
   *A1 use*: if a $\chi\ge 6$ search wants to constrain color-class sizes (e.g. force a
   balanced coloring to prune, or to study fractional/measure analogs), these are the
   standard encodings. Also relevant to Arch 3 (fractional) experiments.

5. **Integer factoring** (Knuth (22)-(24), lines 929-1033). Binary multiplier as a Boolean
   chain; **Tseytin encoding** (Knuth (24)): each gate $t\gets u\land v$, $t\gets u\lor v$,
   $t\gets u\oplus v$ becomes 3-4 clauses. This is THE general "circuit-to-CNF" rule.
   *A1 use*: Tseytin encoding is how any auxiliary Boolean computation (cardinality
   counters, symmetry predicates, virtual-edge constraints) gets compiled into clauses
   without exponential "multiplying out" (Davis-Putnam quote, line 991).

6. **Fault testing** (single-stuck-at faults, lines 1034-1501). Larrabee's active-path
   "sharped" variables; comparing good circuit $F$ vs faulty $F'$. Shows SAT proving
   *undetectability* = UNSAT. *A1 use*: same UNSAT-as-impossibility-proof pattern; also
   the "tarnished/downstream" pruning is a model for only-encode-what-matters.

7. **Learning a Boolean function** (DNF discovery, lines 1502-1625). $2MN$ variables
   $p_{i,j},q_{i,j}$ for term membership. *A1 use*: tangential; illustrates auxiliary-variable
   encodings and the overfitting caveat (a SAT model fitting data is not a proof).

8. **Bounded model checking** (lines 1626-1828, Conway's Life). Unroll a transition
   relation $T(X_t,X_{t+1})$ over $r$ steps into $mr$ clauses (Knuth (33)-(34)); Tseytin
   for the transition. *A1 use*: not directly, but the "unroll + auxiliary vars per copy"
   pattern recurs in any temporal/iterated SAT encoding.

9. **Mutual exclusion** (Alice/Bob protocols, lines 1878-2147). **Invariants** (Knuth
   (50)-(52)): prove $\Phi$ invariant by showing $\Phi(X)\land(X\to X')\land\neg\Phi(X')$
   is UNSAT; then induction bounds the search depth. *A1 use*: the technique of proving an
   *invariant* via a small UNSAT instance, then using it to shrink the main search, is
   conceptually echoed by Heule's "block the 19 colorings" auxiliary clauses (Sec 5-6):
   add known-true constraints to cut the search and the proof.

10. **Digital tomography** (lines 2148-2372, Cheshire cat). Pure cardinality-constraint
    SAT (row/column/diagonal sums); SAT vs IP comparison. *A1 use*: again the cardinality
    encodings (18)-(21); also a candid note that SAT solvers can be *worse* than IP/LP on
    pure counting problems, relevant when choosing tools for Arch 3.

### What the sample says about A1-critical machinery (pointers only)

These are present **only as index/TOC pointers** in the sample; listed so a reader knows
where to look in the full fascicle:

- **DPLL** (Algorithm D): Knuth index "DPLL ... algorithm, 32-33, 62"; the
  Davis-Putnam-Logemann-Loveland backtracking-with-unit-propagation core. *A1 use*: the
  decision procedure underneath every $k$-colorability check; not in sample.
- **Unit propagation / Boolean constraint propagation** (BCP): index "BCP ... see Unit
  propagation"; "Unit propagation and forcing" p.103. *A1 use*: the engine that, given a
  partial coloring, forces or refutes; also the engine of RUP proof checking. The sample
  uses it informally (e.g. Langford unit clause $8$ forcing $x_8=1$, lines 676-679) but
  gives no algorithm.
- **CDCL / clause learning** (Algorithm C): index p.62-71, 132. Conflict-driven clause
  learning, **watched literals** (index "watch", "Lazy data structures 30-34"), VSIDS
  activity, restarts/flushing, clause purging. *A1 use*: the solver class that actually
  cracks de Grey-scale instances; Heule's glucose is a CDCL solver. Not in sample.
- **Resolution** (p.54-65): resolution rule, resolution width lower bounds
  (Ben-Sasson-Wigderson, index p.57-58, 153, 231), extended resolution (p.60, 71, 133).
  *A1 use*: the proof system underlying RUP/DRAT; a DRAT proof is essentially a
  compressed resolution/RAT derivation of $\epsilon$. Not in sample.
- **Certificates of unsatisfiability** (p.69-71): index entry exists; body absent.
  *A1 use*: THE thing that makes $\chi\ge k$ believable. Covered instead by Heule below.
- **Autarkies** (p.44, 71, 146, 152, 177, 214-217): a partial assignment that satisfies
  every clause it touches; can be applied without branching. *A1 use*: a preprocessing /
  pruning principle; "black and blue principle" (index p.146, 216). Not in sample.
- **Symmetry breaking** (p.105-114): index "in graph coloring 99-100, 114, 171, 179, 187";
  "lex-leader 111, 283"; "Breaking symmetries ... 99-100". *A1 use*: exactly Heule's
  color-symmetry fixing; the full fascicle has the lex-leader (Crawford et al.) general
  method. Body not in sample.
- **Preprocessing: blocked-clause elimination, variable elimination, failed literals**
  (p.95-97): index "Blocked clauses 102, 215, 260, 261, 269"; "Elimination of variables".
  *A1 use*: Heule's at-most-one-color clauses are removed by blocked-clause elimination
  (Sec 6.1, ref [18]). Body not in sample.

---

## Per-text notes 2: Heule (2019), "Trimming Graphs Using Clausal Proof Optimization"

This paper IS the A1 certification + minimization technology. Detailed reconstruction.

### Core idea (Abstract, Sec 1)

- An UNSAT proof induces an **unsatisfiable core** (the subset of original clauses
  actually used). For a coloring instance, that core = a subgraph that is still
  non-$k$-colorable.
- **Central empirical observation**: *proof size correlates with core size*. Smaller
  proof of unsatisfiability $\Rightarrow$ smaller unsatisfiable core $\Rightarrow$ smaller
  witness subgraph (Sec 1, Sec 6.2; Fig 9 shows smallest proof yields 963-vertex subgraph
  vs 1609 for the largest proof).
- **Key methodological inversion**: existing minimal-unsatisfiable-core (MUS) algorithms
  delete clauses arbitrarily; if they delete the "wrong" vertex's clause, proving the
  remainder still needs $\chi=5$ becomes wildly expensive (proof jumps from ~10,000 clauses
  to millions; Sec 4.2). Heule instead **postpones deletion of arbitrary clauses as long
  as possible**, removing clauses only through trimming + proof optimization.

### Preliminaries (Sec 2)

- Standard CNF / literal / clause / assignment definitions.
- $F\rvert_\alpha$ = $F$ with satisfied clauses dropped and falsified literals removed.
- **Unit clause rule / unit propagation**: iterate $F\rvert_l$ for unit clauses $(l)$ until
  none remain; if the empty clause $\bot$ appears, a **conflict** was derived.
- **Redundant clause**: $C$ is redundant w.r.t. $F$ if $F$ and $F\land C$ are
  satisfiability-equivalent. Adding redundant clauses preserves satisfiability.
- **Clausal derivation / proof**: a sequence $C_{m+1},\dots,C_n$; accumulated formulas
  $F_i=\{C_1,\dots,C_i\}$; correct if each $C_i$ ($i>m$) is redundant w.r.t. $F_{i-1}$ and
  the redundancy is poly-time checkable. A **proof** derives the empty clause $\bot$,
  certifying UNSAT.
- **RUP (Reverse Unit Propagation)**: $C_i$ has the RUP property iff unit propagation on
  $F_{i-1}\rvert_\alpha$ (where $\alpha$ falsifies all literals of $C_i$) yields a conflict.
  The **justification** of $C_i$ = the clauses used to derive that conflict. "Most
  SAT-solving techniques can be compactly expressed as RUP" (Sec 2).
- **DRUP** = RUP proofs + **deletion information** (deletion drastically cuts checking
  cost). All techniques in the paper work with deletion too. (Note: the broader literature
  uses **DRAT** = Deletion + Resolution Asymmetric Tautology, a strict superset of DRUP
  that also handles RAT clauses from extended resolution / blocked-clause addition; the
  checker `drat-trim` handles both. Heule simplifies presentation to RUP/DRUP here.)
- **Example 1 (Fig 1)**: a 7-clause formula with proof $y, z, \bot$; the justification DAG
  shows clause $(x\lor z)$ is unused, hence not in the core. Multiple justifications exist;
  swapping independent steps gives another valid proof. This multiplicity is what the
  optimizer exploits.
- **CNP background**: de Bruijn-Erdos (ref [4]) makes $\chi(\mathbb{R}^2)$ equal the max
  $\chi$ over finite unit-distance graphs. Moser Spindle ($\chi=4$), Isbell 7-coloring
  upper bound. de Grey 2018: 1581 vertices, $\chi=5$ (ref [10]).

### Graph-construction operations (Sec 2, Fig 2)

- **Minkowski sum** $A\oplus B = \{a+b\}$ (ref [12], Hadwiger 1950).
- **Rotation** $\theta_i$ about origin by $\arccos\frac{2i-1}{2i}$; if $p$ is at distance
  $\sqrt i$ from origin then $p$ and $\theta_i(p)$ are exactly unit distance apart (so an
  edge appears). $\theta_3$ applied to $A\oplus B$ builds the Moser Spindle.
- **Merging** vertices.
These three operations generate all the large candidate graphs.

### Clausal proof optimization (Sec 4) -- the algorithm

Built on top of the **`drat-trim`** checker (refs [15,27]), extended to optimize proofs
and extract cores. Existing baseline = **backward checking** (ref [9]): mark the empty
clause, validate in reverse, mark clauses required for each marked clause's RUP
justification; unmarked clauses are skipped. After verification, marked formula clauses =
an unsatisfiable core; marked proof clauses = an optimized proof. **One proof can yield
multiple cores** (unlike a resolution proof), because the propagation order affects which
clauses get marked.

Two new extensions:

**4.1 Justification Order Shuffling** (`OptimizeProof`, Fig 3):
```
OptimizeProof(P, F):
  do
    J := ComputeJustification(P, F)
    J := RemoveRedundancy(J)      # drop clauses in no justification
    P := ShuffleProof(J)          # random valid reorder + literal shuffle
  while progress
  return P
```
- `RemoveRedundancy`: removes proof clauses not occurring in any justification.
- `ShuffleProof`: random topological permutation respecting justification dependencies
  (each $C$ later than its justification clauses, earlier than clauses depending on it);
  also shuffles literals within clauses. Reshuffling lets the next `ComputeJustification`
  find a *different, possibly smaller* justification.
- **Clause deletion postponement**: a clause $C$ can be deleted once no later clause uses
  it, but Heule deliberately **postpones deletion within a sliding window** (window grows
  each iteration) so $C$ can be pulled back into later justifications. This is the
  "postpone deletion as long as possible" idea concretely.

**4.2 Iterative formula trimming** (Fig 4): two algorithms.

```
TrimFormulaPlain(F):              TrimFormulaInteract(F):
  Fcore := F                        Fcore := F
  do                                do
    P := ComputeProof(Fcore)          P := ComputeProof(Fcore)
    P := OptimizeProof(P, Fcore)      P := OptimizeProof(P, Fcore)
    Fcore := ComputeCore(P, Fcore)    P := OptimizeProof(P, F)    # <-- uses FULL F
  while progress                      Fcore := ComputeCore(P, F)  # <-- core from full F
  return Fcore                      while progress
                                    return Fcore
```
- **Key property exploited by `TrimFormulaInteract`**: if a (D)RUP proof $P$ is correct for
  $F$, it is correct for any $F'\supseteq F$ (extra clauses cannot break a RUP conflict).
  So a proof of the trimmed `Fcore` is also a valid proof of the full `F`. Re-optimizing
  against the full `F` gives the optimizer more room AND lets it **reintroduce** a
  previously-removed clause into the core if doing so enables a smaller proof/core. This
  is the main contribution.
- `Fcore` size need not decrease monotonically (a low-quality proof in line 3 can grow it);
  loop runs while there is net progress (measured by `Fcore` reduction).
- Final step: classical **destructive minimal-core** method (ref [5], Chinneck-Dravnieks)
  to reduce `Fcore` to an actually-minimal unsatisfiable core. Core size varies a lot with
  removal order, so run it thousands of times on a cluster and keep the smallest (Sec 4.2,
  Sec 6.2).
- `TrimFormulaPlain` performs badly because it removes edge clauses and symmetry-breaking
  predicates from the core; Heule fixed it by adding those back each iteration (Sec 6.2).

### The candidate graph $G_{2167}$ (Sec 5)

- Points in $\mathbb{Q}[\sqrt3,\sqrt{11}]\times\mathbb{Q}[\sqrt3,\sqrt{11}]$.
- $H_R$ = regular hexagon of radius $R$ plus its center (7 points); $H'_R$ = $H_R$ rotated
  90 degrees.
- $H_{1/3}\oplus H_{1/3}\oplus H_{1/3}$ = a 37-vertex / 48-edge triangular grid of diameter
  1, 3-colorable (Fig 5 left).
- Adding $\oplus H'_{(\sqrt3+\sqrt{11})/6}$ makes it non-3-colorable (259 vertices, 1056
  edges, 720 of them between grids; Fig 5 right).
- Further Minkowski sums reveal/break color-clustering patterns (Figs 6, 7).
- $C_{13} := H_{1/3}\cup H'_{(\sqrt3+\sqrt{11})/6}$. Then
  **$G_{2167} = C_{13}^{\oplus 8}$ restricted to points within distance 2 of the central
  vertex**: 2167 vertices, 16512 edges, average degree > 15 (high for a $\chi=4$ graph).
- Observed 4-coloring structure: vertical monochromatic lines; points $1/3$ apart get
  different colors; points $2/3$ apart (same vertical) get the same color. "$1/3$ is a
  **virtual edge**" -- forcing a distance-$1/3$ vertex to match the origin's color kills all
  4-colorings. *Repo*: `vtx/G2167.vtx` is this graph.

### The concrete HN result (Sec 6) -- the numbers

- **Encoding (Sec 6.1)**: the one-hot $F_k$ above. At-most-one-color clauses optional
  (blocked-clause elimination, ref [18]) -- slightly better without. **Symmetry breaking**
  (ref [6]): fix $(0,0)\!\to\!1$, $(1,0)\!\to\!2$, $(1/2,\sqrt3/2)\!\to\!3$ (a unit-distance
  triangle present in all their graphs); $\approx 24 = 4\cdot3\cdot2$ speedup for the $k=4$
  proof.
- **Reducing the large part (Sec 6.2)**:
  - Start: $F_4^+$ = "is $G_{2167}$ 4-colorable?" + symmetry breaking + 19 clauses blocking
    the 19 surviving 4-colorings of the distance-2 vertices. **UNSAT, 8668 variables,
    68237 clauses.**
  - Solver: **glucose 3.0** (ref [2]), no preprocessing, randomized VSIDS init. 100 seeds:
    smallest proof **1809** clause-additions, largest **49838**; default (no randomization)
    **2475**. Smallest proof $\to$ 963-vertex subgraph; largest $\to$ 1609-vertex (Fig 9).
  - `TrimFormulaInteract` beats `TrimFormulaPlain` (Fig 10); subgraphs converge toward
    ~500-550 over 20 iterations.
  - Exploiting near-3-fold symmetry: union with 120-degree rotations as a new starting
    graph, rerun. Yields **$L_{393}$** (393 vertices; symmetric with one added vertex).
    *Repo*: `vtx/L403.vtx`, `edge/L403.edge` (the slightly-larger symmetric variant).
- **Finalizing (Sec 6.3)**:
  - $L_{393}$ needs a "small part" to force $\chi=5$. The $G_{553}$ small part (134 vtx)
    alone leaves it 4-colorable. Fix: expand small part by merging 60-degree rotated copies
    $\to$ **$S_{181}$** (181 vertices). *Repo*: `vtx/S199.vtx`, `edge/S199.edge` (variant).
  - $L_{393}\cup S_{181}$ has $\chi=5$; re-trim $\to$ small part of 137 vertices.
  - **Final graph $G_{529}$: 529 vertices, 2670 edges** (down from $G_{553}$'s
    553 vertices / 2720 edges). Almost 120-degree rotationally symmetric; vertex-critical
    (each vertex can be the unique 5th-color vertex). Fig 11.
  - **Total cost: ~100,000 CPU hours.**
- **$G_{529}$ is the repo's `sources/cnp-sat/{vtx,edge}/529.*` with CNF `cnf/529-4.cnf`.**
  Heule published it (https://github.com/marijnheule/CNP-SAT) as a point list + edge list,
  plus a CNF for 4-colorability and a DRAT proof "that can be validated in a few seconds"
  (Sec 6.3). The repo also carries siblings 510, 517, 553 and G2167 from this lineage.

### How this makes a $\chi\ge k$ claim VERIFIABLE (Sec 1, 6.3)

- The published artifact = (graph as points+edges) + (CNF $F_4$) + (DRAT/DRUP proof).
- Anyone re-runs `drat-trim` (or a formally-verified checker, refs [7,19]) on (CNF, proof):
  poly-time, solver-independent confirmation that $F_4$ is UNSAT, hence the graph has
  $\chi\ge 5$, hence $\chi(\mathbb{R}^2)\ge 5$.
- This is the mechanism by which de Grey's $\chi\ge 5$ became trusted: an independent DRAT
  check, not faith in the original solver. The same artifact triple is what a $\chi\ge 6$
  claim must ship (with $F_5$ instead of $F_4$).

### Conclusions / open (Sec 7)

- New trimming algorithm + new graph $\Rightarrow$ 553/2720 down to 529/2670, more symmetric.
- Symmetry "may provide insight how to obtain a $\chi=6$ unit-distance graph (if they exist)".
- Built graphs up to 100,000 vertices via these methods; **all were 5-colorable.** No
  $\chi=6$ graph found. This is direct evidence of the project bottleneck: the construction
  toolkit (Minkowski sums of $H_R$ in $\mathbb{Q}[\sqrt3,\sqrt{11}]$) has not produced a
  $\chi\ge 6$ graph despite reaching 100k vertices.

---

## Cross-text synthesis and tool map

| Need | Knuth sample | Heule paper | Repo / tools |
| --- | --- | --- | --- |
| CNF coloring encoding | (15)-(17), p.6 | Sec 6.1 | `cnf/*-4.cnf` |
| At-most-one-color (optional) | (17) | Sec 6.1 (blocked-clause elim) | -- |
| Symmetry breaking | index p.105 (pointer only) | Sec 6.1 (fix $K_3$ to 1,2,3; $24\times$) | `*-4-sbp.cnf` |
| Cardinality / counters | (18)-(21) | -- | (Arch 3 relevant) |
| Tseytin gate-to-CNF | (24) | -- | encoders |
| Unit propagation | informal in examples | Sec 2 (drives RUP) | -- |
| DPLL / CDCL solver | named only (Alg D/C) | glucose 3.0 used | cadical/kissat/cryptominisat |
| Resolution / RAT theory | named only (p.54) | RUP in Sec 2; DRAT in refs | -- |
| Clausal proof (DRAT/DRUP) | named only (p.69-71) | Sec 2 (full) | DRAT proofs in CNP-SAT |
| Proof checking / core | named only | Sec 4, `drat-trim` extended | `drat-trim` |
| Core minimization | -- | Sec 4.2 + destructive (ref [5]) | cluster runs |
| Graph construction | -- | Sec 2, 5 (Minkowski/rotate/merge) | `vtx/`, `edge/` |

**Bottleneck restated.** Both texts make clear the SAT+certification machinery for
$\chi\ge k$ is mature and content-neutral. The 529-graph result shows the *whole pipeline*
(encode $\to$ solve $\to$ proof $\to$ trim $\to$ DRAT-check) works at scale and produces
re-verifiable artifacts. The missing piece is purely Step 0: a planar-embeddable
unit-distance graph with $\chi\ge 6$. Heule's negative evidence (100k-vertex graphs all
5-colorable) is the strongest signal that new construction ideas, not new SAT technology,
are what A1 needs.

---

## What this enables / what remains open

**Enables (for downstream agents):**
- BUILDER: the exact recipe to certify any candidate $G$ as $\chi\ge 6$ (encode $F_5$ with
  one-hot + $K_3$ symmetry breaking, solve with cadical/kissat/cryptominisat emitting DRAT,
  check with `drat-trim`). And the construction template (Minkowski sums of $H_{1/3}$ and
  $H'_{(\sqrt3+\sqrt{11})/6}$, rotations $\theta_i$, distance-2 truncation) that produced
  $G_{2167}\to G_{529}$.
- VERIFIER: the trust chain reduces to one trusted component, the DRAT checker. A $\chi\ge6$
  claim is acceptable iff its (CNF, DRAT) pair passes `drat-trim` (ideally also a
  formally-verified checker, refs [7,19]).
- SYNTHESIZER: the repo's `529.vtx/.edge` + `529-4.cnf` are exactly Heule's $G_{529}$;
  510/517/553/G2167/L403/S199 are the same lineage. These are ready-made regression fixtures
  for any A1 tooling (each should DRAT-check as $\chi\ge5$).

**Open / caveats:**
- **The Knuth sample lacks the CDCL/resolution/certificate body.** For DPLL, CDCL internals
  (watched literals, VSIDS, restarts, purging), resolution-width theory, autarkies, and the
  symmetry-breaking algorithm, consult the full ~310-page fascicle. The certificate/DRAT
  machinery in these notes comes from Heule, not from the sample. Any claim about Knuth's
  treatment of those topics here is a pointer (TOC/index page number), not read content.
- **DRAT vs DRUP precision**: Heule's paper presents RUP/DRUP to simplify; the deployed
  checker `drat-trim` supports the strictly more expressive DRAT (RAT clauses, needed for
  extended resolution and blocked-clause reasoning). A $\chi\ge6$ proof using preprocessing
  that adds RAT clauses needs DRAT, not just DRUP. (Not in the read texts; flagged for
  VERIFIER.)
- **No $\chi\ge6$ graph exists yet.** The single hardest open input. The SAT side is solved;
  the geometry side is not.
- **Scaling to $k=5$, $F_5$ UNSAT** has not been demonstrated in either text. The 529 result
  is $F_4$ UNSAT. Whether $F_5$ UNSAT proofs on a (hypothetical, likely larger) $\chi=6$
  graph stay "checkable in seconds" is unknown; proof size could be far larger. Flag for
  BUILDER/VERIFIER: budget for substantial proof sizes and possibly cube-and-conquer
  parallel solving (Knuth index "Cube and conquer", p.129; not in sample body).
- **Detector discipline** sits entirely in Step 0 (the graph must use Euclidean rigidity and
  must not embed $\chi$-faithfully in $\mathbb{Q}^2$ or the $L^\infty$ plane). The SAT
  toolchain itself is detector-neutral and cannot catch a structurally-wrong construction.
