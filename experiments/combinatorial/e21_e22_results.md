# E21 and E22: a real constraint that does not pay, and a certificate that cannot exist

Two experiments run against the E20 decision procedure. Both are negative in the
useful sense: each says something structural, and each redirects effort.

## E21: the neighborhood geometry the class was throwing away

### The mathematics (new, and it stands on its own)

In a unit-distance graph, $N(v)$ lies on the unit circle centered at $v$, and two
points on that circle are at distance $1$ exactly when they subtend $60^\circ$.
Writing neighbors as angles, edges inside $G[N(v)]$ join angles differing by
exactly $60^\circ$, so a cycle inside a neighborhood is a closed walk of
$\pm 60^\circ$ steps. Hence:

* (N1) every vertex of $G[N(v)]$ has degree $\le 2$;
* (N2) no ODD cycle lies inside a neighborhood, and $C_4$ forces a repeated
  angle, so the only surviving cycle is $C_6$;
* (N3) one component of $G[N(v)]$ uses one residue class mod $60^\circ$, of which
  there are six, so EVERY COMPONENT HAS AT MOST SIX VERTICES.

**What is new.** Codegree $\le 2$ already implies (N1), no-$C_3$ (= $K_4$-free),
and no-$C_4$ (opposite vertices of such a $C_4$ would have three common
neighbors, counting $v$). It does NOT imply no-$C_5$, which is exactly
$W_5$-freeness, nor no-$C_7$, nor (N3). L25 already recorded that $W_5$ is not a
UDG; it was never made a constraint on the search.

### Both gates, run before anything was built on it

| gate | result |
|------|--------|
| Is the refinement new? | $W_5$ is $K_4$-free with max codegree $2$, so the CURRENT class admits it, yet it is not a UDG. **New content.** |
| Does it hold on real UDGs? | de Grey 1585, Heule 826, Heule 874: max degree inside a neighborhood **2**, largest neighborhood component **6**, odd cycles **0**, non-$C_6$ cycles **0**. Claims survive, and both bounds are TIGHT. |

### The encodings, and the measured negative

| encoding | clauses at $n=16$ | $n=16$, $m=48$ | $n=17$, $m=47$ |
|----------|------------------|----------------|----------------|
| none (E20 baseline) | 72,220 | 1.9-3.9 s | **1,200.4 s** |
| brute force: forbid every (hub, $C_5$) | 648,796 | 9.7 s | not run |
| bipartite neighborhoods (witness the 2-coloring) | 75,580 | 2.2 s | **2,523.1 s** |

The second encoding is strictly stronger than the first (it kills every odd cycle,
not just $C_5$) at 3,360 clauses instead of 576,576, and it is still **2.1x
slower** on the hard cell.

### Why, and this is the point

The refinement is not vacuous. Checked against the committed $n=15$ class
artifact, **7 of the 11 members are excluded** by it: it removes most of the
class. And the search still gets slower.

That is exactly what E20's central claim predicts, seen from the other side. The
whole content of L78 is that the cost of this procedure is decoupled from the size
of the class, because the class is never enumerated. Once that is true, cutting
the class no longer buys time; it only adds clauses and (in the bipartite
encoding) $n(n-1)$ free auxiliary variables for the solver to branch on. A
constraint that would have been worth a $3\times$ speedup to an ENUMERATOR is
worth nothing to a DECIDER.

### Where the refinement should go instead

To the generator, not the decider. E17's `geng` prune pays per graph produced, so
a filter excluding $64\%$ of the class is worth roughly $3\times$ there. Anyone
re-running the census route should put (N2) into `e17_prune.c`. For the decision
route it is recorded and set aside.

The mathematics also belongs in C1 regardless of the timing: it is a strictly
stronger UDG-necessary condition than the pair the note currently uses, verified
tight against three graphs with explicit embeddings.

## E22: the verdicts cannot be certified by LRAT, and the reason is structural

The amended C1 claimed a certified version was "possible in principle (the solver
used can emit LRAT)". That is wrong, and E22 establishes why.

`smsg --lrat-output` does emit a proof (5.2 MB for the $n=15$, $m=41$ cell; the
default is binary, `--cadical-config no-binary` gives text). An independent
checker (`lrat-check` from drat-trim) **rejects it**.

That rejection is correct behavior. The decisive observation:

> $\Phi_{n,m}$ is SATISFIABLE. Its models are precisely the class members at that
> order and edge count. Plain CaDiCaL on the $n=15$, $m=41$ cell without the
> propagators returns a $41$-edge model.

So the unsatisfiability being reported is not that of $\Phi_{n,m}$; it is that of
$\Phi_{n,m}$ together with a semantic side condition ("no proper $5$-coloring")
that is not part of the formula. **No propositional refutation of $\Phi_{n,m}$
exists to be checked**, so no DRAT/LRAT checker can validate the run, at any
budget, with any tooling. The non-vacuity control that makes an UNSAT meaningful
is the same fact that makes it uncertifiable in this format.

### What a certificate must actually be

Three families, discharged separately:

1. **Coloring clauses**: each is justified by exhibiting the $5$-coloring $c$ that
   produced it. Checking is $O(n^2)$: confirm the pairs the clause lists are
   exactly the monochromatic non-adjacent pairs of $c$. Any graph avoiding all of
   them is properly $5$-colored by $c$, which is the clause's content.
2. **Minimality clauses**: justified once and for all by the lexicographic
   minimality theorem of Kirchweger-Szeider, a proof about the propagator rather
   than a per-run artifact.
3. **The CDCL part**: genuinely LRAT-checkable, given 1 and 2 as axioms.

### The cleaner route

The question is natively $\exists G\, \forall c$, a 2-QBF, and `smsg` accepts QCIR
input for exactly that fragment ("currently only supports 2QBF starting with an
existential quantifier"). Posing it as a QBF puts the universal half inside the
formula, where a certificate can reach it. That is the real next hardening, and it
replaces the LRAT sentence in the paper.

## Status

Both findings are folded into C1's epistemic-status paragraph, which now states
precisely what is and is not certifiable instead of promising a hardening that
cannot work as described. No bound moved; the $n \le 17$ verdict is unchanged.
