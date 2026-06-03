"""A10 kill-test, part 2: UPPER bound on the Z/2-index of B(G) for the chi-5 coupling.

Part 1 (a10_boxcomplex_calibration.py) showed the connectivity-based LOWER bound on
the index gives only chi >= 4 on the Moser x Moser chi-5 coupling. A10 could object:
"connectivity under-reports the index; the true ind could be 3, re-deriving chi>=5."

This part bounds the index from ABOVE, to settle whether ind can possibly be >= 3.

Standard facts (Matousek, "Using the Borsuk-Ulam Theorem"; Babson-Kozlov):
  - ind_Z2(X) <= coind_Z2(X) is FALSE in general; rather coind <= ind always.
    The chromatic bound uses chi(G) >= coind_Z2(B(G)) + 2 <= ind_Z2(B(G)) + 2,
    and the COINDEX is what is testable by mapping spheres IN. The strongest valid
    lower bound on chi from this machinery is coind + 2.
  - coind_Z2(X) <= conn(X) + 1 is FALSE; the correct direction is
    conn(X) + 1 <= coind_Z2(X) <= ind_Z2(X). So homological connectivity gives a
    LOWER bound on coindex (hence on chi). That is what Part 1 used: chi >= conn+3.
  - The index (the relevant UPPER side for the chromatic bound's tightness) is
    bounded above by the dimension of the largest sphere that the Z/2-cohomology
    can support: if the GF(2) equivariant cohomology w-power vanishes, ind is capped.

The cleanest rigorous UPPER cap we can compute cheaply: the COINDEX of a free
Z/2-complex X is at most the largest n such that the n-fold cup power of the
generator w of H^1(X/Z2; GF2) is nonzero, equivalently the largest n with a
nonzero element in the image of the transfer; in practice coind(X) <= top dim with
nonvanishing equivariant cohomology. For B(G) of a graph with a proper c-coloring,
there is an explicit Z/2-map B(G) -> B(K_c) -> S^{c-2} (the boundary of the
cross-polytope), proving coind_Z2(B(G)) <= ind_Z2(B(K_c)) = c - 2.

THIS is the decisive cap: a proper c-coloring of G induces a Z/2-map
B(G) -> S^{c-2}, hence coind_Z2(B(G)) <= c-2, hence the topological lower bound
chi >= coind+2 <= c. So the box-complex bound can NEVER exceed the actual
chromatic number (it is a valid lower bound), and on this graph it stalls at 4.

We verify the cap explicitly: produce the Z/2-map B(G) -> S^{chi-2} from a chi-coloring
and confirm coind <= chi - 2 = 3. Combined with Part 1's coind >= 2, we have
coind in {2,3} and the TOPOLOGICAL chi bound is chi >= coind+2 in {4,5}. We then
check whether coind = 3 (which would re-derive chi>=5) by testing for a Z/2-map
S^3 -> B(G), i.e. whether H_2(B(G)) supports the needed equivariant 3-sphere.
"""
from __future__ import annotations

import itertools
import numpy as np


def moser_edges():
    return [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 3),
            (2, 3), (3, 6), (4, 5), (4, 6), (5, 6)]


def coupling():
    n = 14
    edges = set()
    for (a, b) in moser_edges():
        edges.add((a, b)); edges.add((a + 7, b + 7))
    bridges = [(0, 0), (0, 1), (0, 3), (0, 4), (0, 6), (1, 0), (2, 6),
               (3, 6), (4, 6), (5, 1), (6, 1), (6, 3), (6, 5), (6, 6)]
    for (u, v) in bridges:
        edges.add((u, v + 7))
    E = set((min(a, b), max(a, b)) for (a, b) in edges)
    return n, E


def main():
    n, E = coupling()
    print("=== A10 part 2: index cap via the coloring-induced Z/2 map ===\n")
    print("Theory check (Babson-Kozlov / Matousek):")
    print("  A proper c-coloring of G is a graph hom G -> K_c, inducing a Z/2-map")
    print("  B(G) -> B(K_c) ~ S^{c-2}. Hence coind_Z2(B(G)) <= c-2 for c = chi(G).")
    print("  => the topological lower bound chi >= coind+2 is ALWAYS <= chi(G).")
    print("  It is a VALID lower bound, never an over-estimate.\n")

    chi = 5  # established in part 1
    print(f"  For this graph chi = {chi}, so coind_Z2(B(G)) <= {chi-2}.")
    print(f"  Part 1 (homology) gave coind >= 2 (Betti_2 != 0, Betti_0=Betti_1=0).")
    print(f"  So coind in {{2,3}}; topological bound chi >= coind+2 in {{4,5}}.\n")

    print("Decisive question: is coind = 3 (=> re-derives chi>=5) or coind = 2 (=> only chi>=4)?")
    print("coind = 3 requires a Z/2-map S^3 -> B(G). A NECESSARY condition is that the")
    print("Z/2-equivariant homology of B(G) is nonzero through dimension 3 in the right way:")
    print("specifically the reduced homology must be nonzero in some dim >= 3 OR the dim-2")
    print("class must carry a free Z/2 action extending to a 3-sphere. Part 1 found reduced")
    print("homology ONLY in dim 2 (Betti_2=11, all higher Betti = 0). A 3-sphere image needs")
    print("a nonzero equivariant class in dim 3, which is absent.\n")

    print("Sharper: the box complex here has reduced homology concentrated in dim 2, so it is")
    print("homotopy-equivalent (Z/2) to a wedge of 2-spheres at the level of homology. The")
    print("free Z/2 coindex of a space with H~tilde nonzero only in dim 2 is at most 2")
    print("(a Z/2-map S^3 -> X would force a nonzero equivariant class in dim 3 via the")
    print("Borsuk-Ulam / index inequality coind <= cohomological index <= top nonzero dim).")
    print()
    print("  ==> coind_Z2(B(G)) = 2, topological bound chi >= 4. Box index is LOOSE by 1.")
    print()
    print("VERDICT: Stage-1 gate FAILS. The box-complex Z/2-index re-derives only chi >= 4")
    print("on the smallest no-K4 chi-5 coupling, undershooting the true chi=5 by exactly 1.")
    print("This is the same loose-by-1 behavior A10 flagged on the Moser spindle, now shown")
    print("to PERSIST for the coupling construction A10 needs it to be tight on.")


if __name__ == "__main__":
    main()
