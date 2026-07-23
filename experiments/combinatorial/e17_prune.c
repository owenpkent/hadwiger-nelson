/* e17_prune.c - geng PRUNE plugin for the E17 "both-free class" search:
 * reject any (partial) graph containing K4 or K_{2,3} as a subgraph.
 *
 * Contract (see ~/.local/src/nauty2_8_9/geng.c header, "PRUNE feature"):
 *     int PRUNE(graph *g, int n, int maxn)   nonzero => prune.
 * geng adds vertices 0,1,2,... in order; each intermediate graph is an induced
 * subgraph of all later graphs, and the PRUNE call for n implies the call for
 * n-1 already passed. Both target properties are subgraph-monotone, so any NEW
 * K4 or K_{2,3} must involve the last-added vertex x = n-1. Hence the
 * incremental check below is sound (pruned partials only extend to graphs with
 * the forbidden subgraph) and complete (every forbidden subgraph in a final
 * graph is caught when its highest vertex is added).
 *
 *   K_{2,3} as a subgraph  <=>  some vertex pair has >= 3 common neighbors.
 *   New violations via x:  (a) pair (u, x) with codeg >= 3,
 *                          (b) pair (p, q) both adjacent to x whose codegree
 *                              (now counting x) reaches 3.
 *   New K4 via x: an edge (p, q) inside N(x) with a common neighbor in N(x).
 *
 * CHERRY-BUDGET PRUNE (the second layer). In any K_{2,3}-free graph on maxn
 * vertices, cherries (paths of length 2) = sum_v C(deg v, 2) = sum over pairs
 * of codegrees <= 2 * C(maxn, 2). Degrees only grow along geng's augmentation
 * and the final graph obeys -d (geng_mindeg) and -e (geng_mine), so
 *     final cherries >= sum_v C(max(deg_now v, mindeg), 2)
 *                       + (maxn - n) * C(mindeg, 2)
 *                       + mindeg * max(0, 2*geng_mine - degree-floor sum)
 * (each extra degree unit above the floor adds >= mindeg cherries). If that
 * lower bound exceeds the budget, no completion is K_{2,3}-free: prune. This
 * is sound unconditionally (with mindeg = 0 it reduces to "current cherries
 * within budget").
 *
 * Build (documented in e17_build_geng.sh; nauty 2.8.9 source tree required):
 *   gcc -o ~/.local/bin/geng_hn -O4 -mpopcnt -march=native \
 *       -DMAXN=WORDSIZE -DWORDSIZE=32 -DPRUNE=e17_prune -DPREPRUNE=e17_prune \
 *       -I$NAUTY $NAUTY/geng.c e17_prune.c \
 *       $NAUTY/gtoolsW.o $NAUTY/nautyW1.o $NAUTY/nautilW1.o \
 *       $NAUTY/naugraphW1.o $NAUTY/schreier.o $NAUTY/naurng.o
 * (PREPRUNE runs the same test before geng's canonicity work: same soundness,
 * called on more candidates, cuts the expensive isomorphism layer.
 * WORDSIZE=32 build: m=1, one setword per vertex, n <= 32. E17 needs n <= 26.)
 */

#include "gtools.h"

extern int geng_mindeg, geng_maxdeg, geng_mine, geng_maxe, geng_connec;

int
e17_prune(graph *g, int n, int maxn)
{
    int x, u, a, b, d;
    setword nx, w;
    int nbrs[WORDSIZE];

    if (n < 2) return 0;

    /* cherry-budget prune (see header) */
    {
        int md = geng_mindeg;
        long budget = (long)maxn * (maxn - 1);   /* 2*C(maxn,2) */
        long lb = 0, degsum = 0;
        for (u = 0; u < n; ++u)
        {
            int e = POPCOUNT(g[u]);
            if (e < md) e = md;
            lb += (long)e * (e - 1) / 2;
            degsum += e;
        }
        lb += (long)(maxn - n) * md * (md - 1) / 2;
        degsum += (long)(maxn - n) * md;
        if (2L * geng_mine > degsum)
            lb += (2L * geng_mine - degsum) * md;
        if (lb > budget) return 1;
    }

    x = n - 1;
    nx = g[x];

    /* (a) codegree(u, x) >= 3 for some u < x  => K_{2,3} */
    for (u = 0; u < x; ++u)
        if (POPCOUNT(g[u] & nx) >= 3) return 1;

    d = 0;
    w = nx;
    while (w) { TAKEBIT(u, w); nbrs[d++] = u; }

    for (a = 0; a < d; ++a)
        for (b = a + 1; b < d; ++b)
        {
            int p = nbrs[a], q = nbrs[b];
            /* (b) x joined a pair whose codegree (including x) is now >= 3 */
            if (POPCOUNT(g[p] & g[q]) >= 3) return 1;
            /* K4 {x,p,q,c}: p~q and some c in N(x) & N(p) & N(q)
             * (c != x since x is not in g[x]; c != p,q likewise) */
            if ((g[p] & bit[q]) && (g[p] & g[q] & nx)) return 1;
        }

    return 0;
}
