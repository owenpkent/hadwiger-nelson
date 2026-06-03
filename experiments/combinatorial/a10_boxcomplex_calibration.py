"""A10 ADVERSARY kill-test: Stage-1 calibration of the box-complex Z/2-index bound.

The direction A10 proposes re-certifying chi >= 6 of the abstract chi-6 coupling
via the Lovasz-Babson-Kozlov bound chi(G) >= ind_Z2(B(G)) + 2, then extracting a
small topological core to reopen W3 realizability.

A10's OWN gate (Stage 1): compute the box-complex index on the 14-vertex
Moser x Moser chi-5 coupling (the smallest known no-K4 delocalized chi-5 graph,
from L24). If the index gives >= 3 (re-deriving chi >= 5), the method has teeth.
If it gives only 2, the box-complex index is too loose for couplings and A10 dies.

This script computes the box complex B(G), its reduced GF(2) homology, and the
Z/2-coindex lower bound (via connectivity), then reports the topological chi bound.

Box complex B(G) (Csorba / Matsushita convention): vertices are two disjoint
copies V x {1,2}; a simplex is a pair (A,B) of disjoint subsets with A,B nonempty
that are "completely joined" (every a in A adjacent to every b in B), encoded as
the set A x {1} cup B x {2}. The Z/2 action swaps the two copies and (A,B)->(B,A).
B(G) is a free Z/2-simplicial-complex and chi(G) >= ind_Z2(B(G)) + 2, where
ind_Z2 >= conn(B(G)) + 1 (a (c)-connected free Z/2-complex has coindex >= c+1).

We compute conn(B(G)) from reduced GF(2) Betti numbers (lowest dim with nonzero
reduced homology), giving the connectivity lower bound on the coindex, hence on chi.
"""
from __future__ import annotations

import itertools
import numpy as np


def moser_edges():
    return [(0, 1), (0, 2), (0, 4), (0, 5), (1, 2), (1, 3),
            (2, 3), (3, 6), (4, 5), (4, 6), (5, 6)]


def moser_x_moser_coupling():
    """14-vertex Moser x Moser chi-5 coupling with the L24 no-K4 14-bridge cover.

    H1 = vertices 0..6, H2 = vertices 7..13 (= H2-local 0..6 + 7).
    Bridges B* from L24 (H1-local, H2-local) pairs.
    """
    n = 14
    edges = set()
    for (a, b) in moser_edges():
        edges.add((a, b))           # H1
        edges.add((a + 7, b + 7))   # H2
    bridges = [(0, 0), (0, 1), (0, 3), (0, 4), (0, 6), (1, 0), (2, 6),
               (3, 6), (4, 6), (5, 1), (6, 1), (6, 3), (6, 5), (6, 6)]
    for (u, v) in bridges:
        edges.add((u, v + 7))
    E = set()
    for (a, b) in edges:
        E.add((min(a, b), max(a, b)))
    return n, E


def adjacency(n, E):
    A = [[False] * n for _ in range(n)]
    for (a, b) in E:
        A[a][b] = True
        A[b][a] = True
    return A


def common_neighbors_test(A, S):
    """Return True if every pair (across the bipartition) is adjacent. Used in box cx."""
    return True


def box_complex_maximal_simplices(n, E):
    """Maximal simplices of the box complex B(G).

    A simplex is a pair (A,B), A,B subseteq V disjoint, A,B nonempty, with
    A completely joined to B (every a in A adj every b in B), AND additionally
    the standard box-complex condition: every a in A has a common neighbor with
    the whole B side and vice versa (here encoded by 'completely joined' which is
    the Csorba box complex B0; the L-B-K bound uses this B0).

    We enumerate all completely-joined disjoint pairs (A,B), encode each as a
    frozenset of signed vertices {(v,0) for v in A} cup {(v,1) for v in B}, and
    return the maximal ones (for homology we expand to all faces).
    """
    A = adjacency(n, E)
    verts = list(range(n))
    # For tractability enumerate (A,B) by growing. n=14 -> at most 3^14 ~ 4.8M
    # assignments (each vertex: in A, in B, or out). Filter completely-joined.
    simplices = []
    # iterate over all 3^n assignments via product
    for assign in itertools.product((0, 1, 2), repeat=n):
        Aset = [v for v in verts if assign[v] == 1]
        Bset = [v for v in verts if assign[v] == 2]
        if not Aset or not Bset:
            continue
        ok = True
        for a in Aset:
            for b in Bset:
                if not A[a][b]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            simp = frozenset([(v, 0) for v in Aset] + [(v, 1) for v in Bset])
            simplices.append(simp)
    # keep maximal
    simplices.sort(key=len, reverse=True)
    maximal = []
    for s in simplices:
        if not any(s < m for m in maximal):
            maximal.append(s)
    return maximal


def all_faces(maximal):
    """All faces (nonempty subsets) of the maximal simplices, grouped by dimension."""
    faces = set()
    for m in maximal:
        elems = list(m)
        k = len(elems)
        # subsets of size 1..k
        for r in range(1, k + 1):
            for combo in itertools.combinations(elems, r):
                faces.add(frozenset(combo))
    by_dim = {}
    for f in faces:
        d = len(f) - 1
        by_dim.setdefault(d, []).append(f)
    return by_dim


def gf2_rank(M):
    """Rank over GF(2) of a 0/1 numpy matrix."""
    M = (M % 2).astype(np.uint8).copy()
    rows, cols = M.shape
    r = 0
    for c in range(cols):
        piv = -1
        for i in range(r, rows):
            if M[i, c]:
                piv = i
                break
        if piv == -1:
            continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        r += 1
        if r == rows:
            break
    return r


def reduced_betti_gf2(by_dim):
    """Reduced GF(2) Betti numbers. Augment with the empty face (dim -1)."""
    dims = sorted(by_dim.keys())
    maxd = max(dims)
    # index faces per dim; include empty set at dim -1 for reduced homology
    idx = {}
    idx[-1] = {frozenset(): 0}
    for d in range(0, maxd + 1):
        idx[d] = {f: i for i, f in enumerate(sorted(by_dim.get(d, []), key=lambda x: sorted(map(tuple, x))))}
    counts = {d: len(idx[d]) for d in idx}

    def boundary(d):
        """Boundary matrix from C_d to C_{d-1} over GF(2), rows = (d-1)-faces."""
        rows = counts.get(d - 1, 0)
        cols = counts.get(d, 0)
        M = np.zeros((rows, cols), dtype=np.uint8)
        if cols == 0 or rows == 0:
            return M
        col_faces = sorted(by_dim.get(d, []), key=lambda x: sorted(map(tuple, x))) if d >= 0 else [frozenset()]
        for j, f in enumerate(col_faces):
            elems = list(f)
            if d == 0:
                # boundary of a vertex is the empty face
                M[idx[-1][frozenset()], j] = 1
            else:
                for e in elems:
                    sub = f - {e}
                    M[idx[d - 1][sub], j] = 1
        return M

    ranks = {}
    for d in range(0, maxd + 1):
        ranks[d] = gf2_rank(boundary(d))
    betti = {}
    for d in range(0, maxd + 1):
        cd = counts.get(d, 0)
        rk_d = ranks.get(d, 0)            # rank of d_d : C_d -> C_{d-1}
        rk_d1 = ranks.get(d + 1, 0)       # rank of d_{d+1}: C_{d+1} -> C_d
        betti[d] = cd - rk_d - rk_d1
    return betti, counts


def main():
    print("=== A10 Stage-1 calibration: box-complex Z/2-index on Moser x Moser chi-5 ===\n")
    n, E = moser_x_moser_coupling()
    print(f"Coupling graph: n={n}, |E|={len(E)}")

    # sanity: chromatic number via brute (small). Confirm chi=5 (4-UNSAT, 5-SAT).
    def chromatic(n, E):
        A = adjacency(n, E)
        for k in range(1, n + 1):
            # greedy DSATUR-ish exact backtracking
            color = [-1] * n
            order = sorted(range(n), key=lambda v: -sum(A[v]))

            def bt(i):
                if i == len(order):
                    return True
                v = order[i]
                used = set(color[u] for u in range(n) if A[v][u] and color[u] >= 0)
                for c in range(k):
                    if c not in used:
                        color[v] = c
                        if bt(i + 1):
                            return True
                        color[v] = -1
                return False
            if bt(0):
                return k
        return n

    chi = chromatic(n, E)
    print(f"chi(coupling) = {chi}  (expect 5 per L24)\n")

    print("Building box complex B(G)...")
    maximal = box_complex_maximal_simplices(n, E)
    print(f"  maximal simplices: {len(maximal)}")
    if maximal:
        print(f"  max simplex dimension: {max(len(m) for m in maximal) - 1}")
    by_dim = all_faces(maximal)
    print(f"  total faces by dim: { {d: len(v) for d, v in sorted(by_dim.items())} }")

    print("\nComputing reduced GF(2) homology of B(G)...")
    betti, counts = reduced_betti_gf2(by_dim)
    print(f"  reduced Betti (GF2): {betti}")

    # connectivity = (lowest dim d with reduced H_d != 0) - 1
    nz = [d for d, b in betti.items() if b != 0]
    if not nz:
        conn = max(by_dim.keys())  # contractible-ish; very high connectivity (degenerate)
        print("  reduced homology vanishes in all computed dims (degenerate).")
    else:
        first_nonzero = min(nz)
        conn = first_nonzero - 1
    print(f"  connectivity (homological lower bound) conn = {conn}")

    # coindex >= conn + 1 ; chi >= coindex + 2 >= conn + 3
    coind_lb = conn + 1
    chi_lb = coind_lb + 2
    print(f"\n  ==> ind_Z2(B(G)) >= coind >= conn+1 = {coind_lb}")
    print(f"  ==> topological chi bound: chi >= coind+2 >= {chi_lb}")
    print(f"\n  GATE: need chi_lb >= 5 (ind >= 3) for A10 to proceed.")
    print(f"  RESULT: chi_lb = {chi_lb}  ->  {'PASS gate (proceed to Stage 2)' if chi_lb >= 5 else 'FAIL gate (box index too loose; A10 dies)'}")


if __name__ == "__main__":
    main()
