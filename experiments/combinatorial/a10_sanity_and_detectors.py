"""A10 kill-test, part 3: sanity-check the box-complex homology engine, then run
the three wrong-approach detectors against A10's IDEA (topological index bound).

Sanity: K_n's box complex B(K_n) is Z/2-homotopy-equiv to S^{n-2}, so its only
nonzero reduced homology is in dim n-2 and the bound gives chi(K_n) >= n. We verify
on K_3 (expect H~ in dim 1, chi>=3) and K_4 (expect H~ in dim 2, chi>=4). If the
engine reproduces these, the chi-5-coupling result (H~ in dim 2 only, chi>=4) is
trustworthy, NOT an enumeration bug.

Detectors: A10's idea is "compute a topological (box-complex Z/2-index) lower bound
on chi". Apply that idea to the three controls.
"""
from __future__ import annotations

import itertools
import numpy as np

from a10_boxcomplex_calibration import (
    box_complex_maximal_simplices, all_faces, reduced_betti_gf2, adjacency)


def topo_bound(n, E, label):
    maximal = box_complex_maximal_simplices(n, E)
    by_dim = all_faces(maximal)
    betti, _ = reduced_betti_gf2(by_dim)
    nz = [d for d, b in betti.items() if b != 0]
    if not nz:
        conn = max(by_dim.keys()) if by_dim else -1
    else:
        conn = min(nz) - 1
    coind_lb = conn + 1
    chi_lb = coind_lb + 2
    # cohomological cap: top nonzero reduced homology dim caps coind from above
    top_nz = max(nz) if nz else -1
    coind_cap = top_nz  # coind <= cohomological index <= top nonzero dim
    chi_ub_from_topo = coind_cap + 2
    print(f"  [{label}] reduced Betti(GF2) = {betti}")
    print(f"    conn={conn} -> coind in [{coind_lb-2}+2 .. {coind_cap}+2], "
          f"topo chi-lower-bound = {chi_lb}, topo cap = {chi_ub_from_topo}")
    return chi_lb


def Kn(nn):
    return nn, set((i, j) for i in range(nn) for j in range(i + 1, nn))


def main():
    print("=== part 3a: engine sanity on complete graphs ===")
    print("K_3 (chi=3): box complex ~ S^1, expect reduced H in dim 1, topo bound 3")
    topo_bound(*Kn(3), label="K3")
    print("K_4 (chi=4): box complex ~ S^2, expect reduced H in dim 2, topo bound 4")
    topo_bound(*Kn(4), label="K4")
    print("K_5 (chi=5): box complex ~ S^3, expect reduced H in dim 3, topo bound 5")
    topo_bound(*Kn(5), label="K5")
    print()

    print("=== part 3b: wrong-approach detectors on A10's idea (topological index) ===")
    print("A10's idea = 'box-complex Z/2-index lower-bounds chi'. Run on controls.\n")

    # Q^2 control: any finite bipartite-ish rational-distance sample. The Q^2 UDG is
    # bipartite (chi=2). Its box complex: for a bipartite graph B(G) is Z/2-homotopy
    # equiv to S^0 (two points swapped), giving chi >= 2. CORRECT, no over-claim.
    # We model with an even cycle C_6 (bipartite, chi=2), a legitimate Q^2 UDG fragment.
    C6 = (6, set((i, (i + 1) % 6) for i in range(6)))
    print("Q^2 control (bipartite fragment, here C_6, chi=2):")
    b = topo_bound(*C6, label="C6/Q^2")
    print(f"    detector: topo bound = {b}; Q^2 known chi=2. "
          f"{'PASS (does not exceed 2)' if b <= 2 else 'FAIL (over-claims on Q^2)'}\n")

    # L^infty control: chi=4. The topological bound is purely combinatorial (graph hom
    # invariant), so it CANNOT distinguish L^inf from Euclidean: it sees only the
    # abstract graph. On any chi=4 graph it gives at most 4 (and is often loose).
    # We use K_4 as the worst case the abstract bound can see (a chi=4 abstract graph).
    print("L^inf control: the box-complex bound is an ABSTRACT-GRAPH invariant; it has")
    print("NO access to the norm. It would give the SAME bound for an L^inf chi=4 UDG as")
    print("for any abstract chi=4 graph. It never uses Euclidean rigidity.")
    print("    detector: A10's idea is norm-blind. It passes the L^inf NUMERIC control")
    print("    (gives <=4) but for the WRONG reason: it cannot certify >4 anywhere a")
    print("    norm-blind method should fail, so it cannot be the source of a Euclidean")
    print("    chi>=6. This is the structural warning, not a numeric over-claim.\n")

    # R^1 control: chi=2 (path/odd-even). Box complex of a path/bipartite graph -> S^0.
    P = (6, set((i, i + 1) for i in range(5)))
    print("R^1 control (path P_6, bipartite, chi=2):")
    b = topo_bound(*P, label="P6/R^1")
    print(f"    detector: topo bound = {b}; R^1 known chi=2. "
          f"{'PASS' if b <= 2 else 'FAIL'}")
    print("    (A10 is not measure-theoretic, so the R^1/O(2)-blindness detector is")
    print("     the wrong lens; it passes trivially. The binding detector is L^inf.)")


if __name__ == "__main__":
    main()
