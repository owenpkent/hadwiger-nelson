# hn_solver: a structure-first k-colorability solver for the Hadwiger-Nelson program

**A white paper.** Status: living document. Date: 2026-06-13.
Code: [`experiments/_shared/hn_solver.py`](../../experiments/_shared/hn_solver.py).
Benchmark: [`experiments/_shared/hn_solver_bench.py`](../../experiments/_shared/hn_solver_bench.py),
results [`hn_solver_bench_results.md`](../../experiments/_shared/hn_solver_bench_results.md).

---

## 1. What it is and why it exists

`hn_solver` is a from-scratch decision procedure for graph $k$-colorability,
written in pure Python, built specifically for the Hadwiger-Nelson computational
program. It is **not** a general-purpose SAT solver and is **not** intended to
compete with CDCL solvers (MapleChrono, Cadical) on large industrial instances.

It exists because the program repeatedly answers one narrow question, "is this
graph $k$-colorable," on graphs with a great deal of exploitable structure
(triangle-rich unit-distance graphs, Mycielskians, near-critical graphs), and
because the L64 portfolio finding exposed how heuristic-dependent black-box SAT
solving is near a phase boundary. A solver built on the program's own structural
findings has two payoffs:

1. **It exposes structure a SAT solver hides.** In particular it natively breaks
   the color-permutation symmetry that a one-hot SAT encoding carries, and it can
   count coloring *patterns* (colorings up to color permutation), the object the
   "deep liquidity" findings (L57, L62, L65) actually care about.
2. **It is a transparent baseline.** Every decision is a search-tree expansion we
   can inspect and budget, not an opaque conflict-driven trajectory.

The honest positioning: a research instrument that is fast on small-to-medium
structured instances and exposes useful structure, with a clearly understood
ceiling.

## 2. Design

All four ingredients are implemented from scratch with no SAT backend.

**Color-class symmetry breaking.** A vertex may introduce color $c$ only if
$c \le 1 + (\text{max color used so far})$. The $k!$ relabelings of any coloring
collapse to a single canonical representative. A one-hot SAT encoding carries all
$k!$ symmetric assignments unless symmetry-breaking clauses are added by hand;
`hn_solver` bakes the break into the search. This is the single largest source of
its speed (Section 4).

**Clique seeding.** A greedy maximal clique is colored $1..\omega$ up front
(forced distinct), which pins the symmetry-broken frame and yields an immediate
$\omega > k \Rightarrow$ UNSAT certificate (visible in the benchmark as the
complete-graph rows, decided in 0 search nodes).

**MRV branching with forward checking.** The next vertex to color is the
uncolored vertex with the fewest available colors (minimum remaining values),
max-degree tiebreak; a vertex whose available-color set is wiped out triggers an
immediate backtrack.

**Pattern counting.** `count_patterns(n, edges, k, cap)` returns the number of
proper $k$-colorings up to color permutation, bounded by `cap`. SAT solvers do
not give this; it is a direct measurement of coloring-space liquidity, the
quantity behind L57/L62.

**Node budget.** `kcolor(..., node_limit=N)` returns `None` if the search exceeds
$N$ tree-node expansions, so the solver is bounded and never hangs. The same
budget powers the benchmark's honest "where does it break" measurement.

## 3. Correctness

`hn_solver` is validated by cross-validation, not by trust:

- **Decision agreement.** Across 60 random graphs in the self-test plus 24
  benchmark instance/$k$ pairs (84 total), the verdict agrees with the
  MapleChrono SAT backend on **every** instance: zero disagreements. A single
  disagreement would be a bug; there are none.
- **Witness validity.** Every coloring it returns on a SAT instance is checked
  proper (no monochromatic edge).
- **Counter validity.** `count_patterns` matches a brute-force orbit count on
  every tiny graph tested, including the known value of 5 three-coloring patterns
  for $C_5$.

## 4. Benchmark results

Measured against MapleChrono (in-process, via `pysat`) at each instance's two
hardest $k$ values, $k = \chi - 1$ (UNSAT) and $k = \chi$ (SAT). Full table in
[`hn_solver_bench_results.md`](../../experiments/_shared/hn_solver_bench_results.md);
selected rows:

| instance | k | hn verdict | hn nodes | hn time | maple time | winner |
|---|--:|:--:|--:|--:|--:|:--:|
| K8 (clique) | 7 | UNSAT | 0 | 0.0 ms | 10.6 ms | hn (clique seed) |
| M^2(C5) 23v tri-free | 4 | UNSAT | 882 | 9.5 ms | 1.24 s | hn ~130x |
| M^3(C5) 47v tri-free | 5 | UNSAT | 447,720 | 11.8 s | 31.9 s | hn 1.7x |
| rand G(40,0.3) | 5 | UNSAT | 122 | 4.4 ms | 5.43 s | hn ~1200x |
| rand G(60,0.25) | 5 | UNSAT | 335 | 24 ms | 5.31 s | hn ~220x |
| lineage P510 | 5 | SAT | 508 | 168 ms | 9.28 s | hn ~55x |
| M^4(C5) 95v tri-free | 7 | SAT | 94 | 8.3 ms | 4.7 ms | maple ~2x |

**Headline:** zero correctness disagreements; `hn_solver` is faster on 21 of 24
instance/$k$ pairs, sometimes by two to three orders of magnitude.

**Why it wins, stated fairly.** The wins are over the *naive one-hot SAT
encoding*, which carries the full color-permutation symmetry. `hn_solver` breaks
that symmetry natively, so it proves UNSAT without exploring symmetric subtrees
and finds SAT witnesses in a canonical frame. The three losses are all trivial
SAT instances finished by both solvers in under 10 ms, where the compiled C
constant factor beats Python. Important honesty: a CDCL solver *given a
symmetry-broken encoding* (lex-leader or clique-fixing clauses) would close most
of this gap. The win is real for the program because `portfolio_sat` uses the
naive encoding, so `hn_solver` genuinely complements it.

**Where it breaks (the ceiling).** Up the Mycielski tower the node count grows
super-exponentially: 882 at $M^2(C_5)$, 447,720 at $M^3(C_5)$. $M^3$ at 11.8 s is
already the point where the lead over MapleChrono shrinks to 1.7x. One level
further, $M^4(C_5)$ $k=6$ UNSAT, and the lineage $P_{510}$ at $k=4$ UNSAT, were
**intractable for the pure-Python search within budget** in our runs (and hard
even for MapleChrono). The cause is structural: `hn_solver` has **no clause
learning**, so it cannot record and reuse the conflict reasons that let CDCL
prune. This is the fundamental ceiling.

## 5. Honest limitations

1. **No clause/nogood learning.** The dominant limitation. The search rediscovers
   conflicts instead of learning from them, so hard UNSAT instances blow up. This
   is why $M^4(C_5)$ and lineage-scale UNSAT are out of reach.
2. **Pure Python constant factor.** Tens of thousands of nodes per second, versus
   a compiled solver's millions of propagations per second. Even with a smaller
   search tree, the per-node cost loses on anything large.
3. **The symmetry-breaking win is against a naive encoding.** It is not evidence
   of beating CDCL in general, only of beating the unsymmetried one-hot SAT
   formulation the program currently uses.
4. **Greedy clique seeding, not maximum clique.** A maximum-clique seed would give
   stronger UNSAT certificates; the greedy one can miss them.

## 6. Room for improvement (prioritized)

Ordered by expected payoff for this program:

1. **Conflict / nogood learning.** DONE and measured, with an instructive
   outcome (see [`hn_solver_cdcl.py`](../../experiments/_shared/hn_solver_cdcl.py)).
   We implemented conflict-directed backjumping (Prosser CBJ) plus nogood
   learning, validated correct (zero verdict disagreements vs the chronological
   solver and the portfolio over 200 random graphs x 3 colors). The clean
   soundness fact that makes it tractable: under the symmetry ceiling a wipeout
   happens only when a vertex's neighbors already occupy all $k$ colors, a pure
   graph conflict, so conflict analysis needs no symmetry explanation.
   **Result (after a parameter sweep that corrected a premature conclusion).**
   The headline win is the BACKJUMPING with a cheap fixed order, not the nogoods.
   On $M^3(C_5)$ $k=5$ UNSAT: the MRV chronological solver takes 447,720 nodes /
   13.3 s; pure CBJ (max_learn=0) takes 516,549 nodes but **1.2 s, 11.4x faster**,
   because the fixed-order per-node cost is far below MRV's per-node
   minimum-remaining-values scan. Nogood learning then reduces the node count
   (max_learn=8: 81,850 nodes, 6.3x fewer) but does NOT reduce wall time in pure
   Python (2.5 s), and a large nogood cap is actively counterproductive
   (max_learn=20: 66,651 nodes but 17.7 s, the per-node linear nogood scan
   balloons). Across instances (CBJ max_learn=8 vs chronological): $M^2$ 2.6x,
   $M^3$ 5.3x, sparse random UNSAT 2.5x, but a denser random where MRV's dynamic
   ordering resolves in a few nodes is 0.2x (slower). So CBJ wins where the search
   is genuinely hard and loses where smart ordering nails it quickly. $M^4(C_5)$
   $k=6$ UNSAT stays out of reach in pure Python (pure CBJ needs >60M nodes; the
   learning variant's node reduction is eaten by per-node cost). **Conclusion:**
   backjumping is a real, free win on hard instances; nogood learning reduces
   nodes but its wall-time payoff is gated on watched-literal propagation (O(1)
   checks instead of the current linear scan) and/or a compiled core, which is
   what $M^4$ needs. Methodological lesson: sweep the parameter before concluding
   (a bad max_learn default first hid the 11x CBJ win).

   **Addendum (watched-literal propagation, DONE, instructive negative).**
   Implemented the named lever in [`hn_solver_wl.py`](../../experiments/_shared/hn_solver_wl.py):
   two-watched-literal nogood propagation with integer literal ids
   ($L = \text{pos}\cdot k + c$) and flat list-of-lists indexing (no dict/tuple on
   the hot path, so PyPy's JIT compiles the propagation loop). Validated correct:
   zero verdict disagreements vs `hn_solver`, `hn_solver_cdcl`, AND the portfolio
   over 300 random graphs $\times$ 4 colors, plus witness validity. The honest
   result: watched literals beat the `hn_solver_cdcl` linear scan by ~2.3x under
   PyPy (M^3 nogood path 0.56 s $\to$ 0.24 s), but STILL LOSE to pure CBJ (0.16 s)
   on M^3. The bottleneck was misdiagnosed as propagation speed; it is really the
   WEAKNESS of the learned clauses. A Prosser CBJ conflict set is large and
   non-asserting, so even propagated in O(1) it does not cut enough nodes to repay
   its per-node cost (87,621 learned-path nodes at 359k n/s = 0.24 s vs 516,549
   bare-path nodes at 3.28M n/s = 0.16 s). The real fix is 1UIP-quality clause
   learning, which is exactly what a production CDCL solver already has, motivating
   item 7 below over a deeper pure-Python engine capped by Python's per-node speed.
2. **Stronger propagation.** Full arc-consistency on color domains, or a DSATUR
   dynamic ordering (branch on the vertex with the most distinctly-colored
   neighbors), would shrink the tree before learning is even needed.
3. **PyPy (DONE, ~5x free) then a compiled core.** Measured: running the
   pure-Python solver under PyPy 3.11 gives a clean **5.0x** speedup on the
   pure-CBJ path with zero code changes (M^3(C5) k=5 UNSAT: CPython 0.87 s vs
   PyPy 0.17 s; 3.4x on the less-JIT-friendly nogood path). Stacked with the CBJ
   win the M^3 instance went from 13.3 s (old MRV solver) to 0.17 s, ~78x, all in
   Python. PyPy is the recommended first step. Caveat: it accelerates only the
   pure-Python solver; pysat (the portfolio, the census) is a C extension that
   runs poorly under PyPy, so keep those on CPython. Beyond PyPy, a Rust/PyO3
   core (not C, for memory safety on the watched-literal machinery) buys the
   remaining constant factor, but note M^4(C5) k=6 UNSAT did not finish even
   under PyPy (>400M nodes), so the node count, addressed by item 1, is the wall
   before the constant factor is.
4. **Maximum-clique seeding.** Replace the greedy clique with an exact maximum
   clique on the high-degree core (cheap at program scale) for stronger immediate
   UNSAT certificates.
5. **Incrementality for the forcing tests.** The census (L57) and the lifter
   (L64/L65) repeatedly ask "is $G + e$ / $G/e$ colorable." An incremental
   interface that reuses search state across single-edge perturbations would make
   `hn_solver` a fast forcing oracle, complementing the SAT route.
6. **Use as a structural pre-filter in the portfolio.** Run `hn_solver` with a
   small node budget first; it resolves the structured-easy majority instantly,
   and only the genuinely hard residue is handed to the CDCL portfolio. This
   turns the symmetry-breaking win into a portfolio-level speedup.
7. **Symmetry-broken SAT export (DONE, the breakthrough).** Emit the
   clique-fixing and first-appearance-precedence clauses `hn_solver` uses as a CNF
   preamble for the portfolio, so a production CDCL solver inherits the symmetry
   break it otherwise lacks. Implemented as
   [`build_color_cnf_symbreak`](../../experiments/_shared/portfolio_sat.py) and
   exposed via `colorable_portfolio(..., symbreak=True)`. Two ingredients, both
   sound (every proper coloring keeps one representative): (1) a greedy maximal
   clique pinned to colors $0..\omega-1$ by unit clauses; (2) colors numbered by
   order of first appearance along a clique-first / degree-descending order,
   $x[v_i][c] \to \bigvee_{j<i} x[v_j][c-1]$, with rank-bound units. Validated
   EQUISATISFIABLE with the naive one-hot encoding (zero verdict disagreements,
   zero bad witnesses over 1000+ instances;
   [`symbreak_bench.py`](../../experiments/_shared/symbreak_bench.py)).

   **This is the move that breaks the ceiling.** It combines the program's native
   symmetry advantage with a production CDCL engine's 1UIP learning, watched
   literals, VSIDS, and restarts, so the two instances Section 4 called
   intractable become routine (Cadical195, single isolated run):

   | instance | naive one-hot | symmetry-broken | |
   |---|--:|--:|:--|
   | $M^3(C_5)$ $k{=}5$ UNSAT | 7.0 s | **0.05 s** | ~146x |
   | $M^4(C_5)$ $k{=}6$ UNSAT | wall (intractable) | **21.9 s** | newly decided |
   | $P_{510}$ $k{=}4$ UNSAT | wall (L29/L30 abandoned) | **1.66 s** | newly decided |
   | $P_{510}$ $k{=}5$ SAT | -- | **instant** | -- |

   So the program now has an independent, certificate-capable proof that
   $\chi(M^4(C_5)) \ge 7$ and that $P_{510}$ is genuinely $\chi=5$ (not just
   asserted), both previously out of reach. The symmetry break is the same one
   `hn_solver` searches; here it is handed to a solver that also learns, which is
   the combination that wins. This is the recommended default for the in-class
   E14-style decisions (L64): every portfolio member gets the break, so the
   Cadical-vs-MapleChrono heuristic swing shrinks.

## 7. Bottom line

`hn_solver` is a correct, transparent, structure-first colorability solver that is
genuinely fast on the small-to-medium structured instances the program generates,
and that contributes a capability (pattern counting) no SAT solver offers. Its
own ceiling is the absence of clause learning. The decisive lesson of this work
is that the fix is not to keep growing a pure-Python learning engine (watched
literals were added and still lose to pure CBJ because Prosser conflict sets are
weak, and Python caps the per-node speed) but to EXPORT the solver's symmetry
break to a production CDCL engine that already learns at 1UIP quality. That
combination (item 7) decides $M^4(C_5)$ $k=6$ UNSAT in 22 s and $P_{510}$ $k=4$
UNSAT in under 2 s, both previously intractable. `hn_solver` is thus best deployed
two ways at once: as a structural front end that resolves the easy majority
instantly, and as the SOURCE of the symmetry-breaking CNF preamble that makes the
CDCL portfolio world-class on the hard residue.
