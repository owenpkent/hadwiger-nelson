"""Wildcard B (renormalized clamp): the RG / transfer-matrix go/no-go for
whether long-range color forcing can ACCUMULATE across scales of a substitution
structure, given that L45 proves it is absent at every finite scale in the
de Grey / Polymath lineage (forced-different = adjacent).

The 2050 retrodiction brainstorm proposed: define an RG step on a substitution
tiling, build a "forcing-coupling" transfer matrix across one inflation, and read
off the leading eigenvalue; eigenvalue > 1 means forcing is a RELEVANT operator.

That slogan is WRONG, and correcting it is the first result here. The leading
eigenvalue of a coloring transfer matrix counts the GROWTH RATE OF THE NUMBER OF
PROPER COLORINGS (the coloring entropy). lambda_1 > 1 means MANY colorings, which
is the OPPOSITE of forcing. The correct RG diagnostic is the SPECTRAL GAP, i.e.
whether |lambda_2| / |lambda_1| stays < 1 (forcing/correlation decays; route
dead) or equals 1 (long-range correlation survives the inflation limit; forcing
is relevant). Equivalently and more sharply, in the port-to-port picture below:
long-range forcing exists IFF the per-tile color-port relation is IMPRIMITIVE.

Port-to-port picture (the faithful model of a clamp).
A "tile gadget" with a left port and a right port induces a relation
R in {0,1}^{k x k}: R[a,b] = 1 iff some proper k-coloring of the gadget colors
the left port a and the right port b. Chaining n gadgets composes the relation
by BOOLEAN matrix product R^(n). The two ends (non-adjacent, distance n) are
FORCED DIFFERENT iff (R^n)[c, c] = 0 for every color c, i.e. the boolean n-th
power has an all-zero diagonal: no color can survive from one end to the other.

A non-adjacent forced-different pair = a clamp (L51-L53). So:

    a clamp at distance n  <=>  R^n has zero diagonal.

If R is PRIMITIVE (irreducible + aperiodic) then R^n -> all-ones, the diagonal
fills in, and forcing dies at finite range: this is the L45 regime
(forced-different = adjacent, range 1). If R is a non-identity PERMUTATION (a
"color shifter", e.g. b = a + 1 mod k) then R^n is the shift by n, whose diagonal
is zero for all n not divisible by k: forcing persists at ALL scales. So:

    long-range color forcing is RELEVANT under inflation
        <=>  the inflation drives the effective port relation toward an
             IMPRIMITIVE (permutation-like) matrix, not a primitive one.

This script (a) calibrates the diagnostic on the canonical port relations and on
C_5 (the repo's R5 refutation: C_5 has NO non-adjacent forced-different pair),
(b) runs a Fibonacci substitution on a pair of port relations and reports whether
forcing is relevant or irrelevant as a function of the per-tile gadget, and
(c) states the sharpened target this hands to Wildcard A. The color-symmetric
single-vertex-port relations form a primitive monoid {0, I, J-I, J}: a single-
port "color shifter" is impossible, so a chain can never build the rich Z_k
forcing. The clamp must therefore use a WIDE (>= 2-vertex) interface, and the
question factors into (i) forced-SAME (relation I) under omega <= 3 and (ii) an
imprimitive boundary-coloring transfer matrix on a >= 2-vertex separator (the
clamp's degree->= 5 split, Theorem R / L53). No floating point in the boolean
algebra; eigenvalues are reported only as the spectral-gap commentary.
"""

from __future__ import annotations

import itertools

import numpy as np


# ---------------------------------------------------------------------------
# Boolean matrix algebra (exact; entries in {0, 1}).
# ---------------------------------------------------------------------------
def bool_matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Boolean matrix product: (A B)[i,j] = OR_k (A[i,k] AND B[k,j])."""
    return ((A.astype(bool) @ B.astype(bool)) > 0).astype(np.uint8)


def bool_power(R: np.ndarray, n: int) -> np.ndarray:
    out = np.eye(R.shape[0], dtype=np.uint8)
    for _ in range(n):
        out = bool_matmul(out, R)
    return out


def is_primitive(R: np.ndarray, max_pow: int = 64) -> bool:
    """R is primitive iff some boolean power is all-ones (strictly positive)."""
    P = R.copy()
    for _ in range(max_pow):
        if P.all():
            return True
        P = bool_matmul(P, R)
    return P.all()


def forcing_distances(R: np.ndarray, nmax: int = 30) -> list[int]:
    """Distances n in [1, nmax] at which the two ends are FORCED DIFFERENT,
    i.e. boolean R^n has an all-zero diagonal (no color survives end to end)."""
    out = []
    P = R.copy()
    for n in range(1, nmax + 1):
        if np.trace(P) == 0:  # zero diagonal (boolean entries)
            out.append(n)
        P = bool_matmul(P, R)
    return out


def is_color_symmetric(R: np.ndarray) -> bool:
    """A port relation that comes from a GADGET must be invariant under permuting
    the color classes (relabeling any proper coloring by pi in S_k is still
    proper): R[a,b] == R[pi a, pi b] for all pi. It suffices to test generators
    of S_k: the transposition (0 1) and the k-cycle (0 1 ... k-1)."""
    k = R.shape[0]
    transp = list(range(k)); transp[0], transp[1] = 1, 0
    cyc = [(i + 1) % k for i in range(k)]
    for perm in (transp, cyc):
        P = np.array(perm)
        if not np.array_equal(R, R[np.ix_(P, P)]):
            return False
    return True


def spectral_gap(R: np.ndarray) -> tuple[float, float, float]:
    """Return (lambda_1, |lambda_2|, gap) of the {0,1} matrix over the reals.
    gap = 1 - |lambda_2| / lambda_1. gap == 0 (within tol) <=> long-range
    correlation survives (forcing relevant). The leading eigenvalue itself is
    the coloring-entropy growth rate and is NOT the forcing diagnostic."""
    ev = np.linalg.eigvals(R.astype(float))
    mags = np.sort(np.abs(ev))[::-1]
    lam1 = float(mags[0])
    lam2 = float(mags[1]) if len(mags) > 1 else 0.0
    gap = 1.0 - lam2 / lam1 if lam1 > 0 else 1.0
    return lam1, lam2, gap


# ---------------------------------------------------------------------------
# Canonical port relations on k colors.
# ---------------------------------------------------------------------------
def rel_identity(k: int) -> np.ndarray:
    return np.eye(k, dtype=np.uint8)


def rel_shift(k: int, s: int = 1) -> np.ndarray:
    """Color-shifter: right port = left port + s (mod k). A permutation."""
    R = np.zeros((k, k), dtype=np.uint8)
    for a in range(k):
        R[a, (a + s) % k] = 1
    return R


def rel_differ(k: int) -> np.ndarray:
    """Single edge: right port != left port (J - I). Primitive for k >= 3."""
    return (np.ones((k, k), dtype=np.uint8) - np.eye(k, dtype=np.uint8))


# ---------------------------------------------------------------------------
# Faithful calibration: C_5 has no non-adjacent forced-different pair (R5
# refutation in the repo). Brute-force every proper 3-coloring and check.
# ---------------------------------------------------------------------------
def c5_forced_different_pairs() -> dict:
    n, k = 5, 3
    edges = [(i, (i + 1) % n) for i in range(n)]
    colorings = [
        c for c in itertools.product(range(k), repeat=n)
        if all(c[u] != c[v] for u, v in edges)
    ]
    forced = []
    for i in range(n):
        for j in range(i + 1, n):
            if all(c[i] != c[j] for c in colorings):
                forced.append((i, j))
    adjacent = set(map(tuple, (sorted(e) for e in edges)))
    nonadjacent_forced = [p for p in forced if p not in adjacent]
    return {
        "n_proper_3colorings": len(colorings),
        "forced_different_pairs": forced,
        "all_forced_are_adjacent": all(p in adjacent for p in forced),
        "nonadjacent_forced_different": nonadjacent_forced,
    }


# ---------------------------------------------------------------------------
# Fibonacci substitution on port relations: a -> a b, b -> a.
# A supertile relation is the boolean product of its constituent tile relations.
# ---------------------------------------------------------------------------
def fibonacci_inflate(Ra: np.ndarray, Rb: np.ndarray, levels: int) -> list[dict]:
    """Iterate a -> ab, b -> a on port relations and report, per level, whether
    the effective a-supertile relation is primitive (forcing dies) or imprimitive
    (forcing can persist), plus its long-range forcing distances."""
    rows = []
    A, B = Ra.copy(), Rb.copy()
    for lvl in range(1, levels + 1):
        A, B = bool_matmul(A, B), A  # a->ab (A then B), b->a (old A)
        prim = is_primitive(A)
        fd = forcing_distances(A, nmax=2 * A.shape[0] + 2)
        lam1, lam2, gap = spectral_gap(A)
        rows.append({
            "level": lvl,
            "a_supertile_primitive": prim,
            "forcing_distances": fd,
            "lambda1": round(lam1, 4),
            "abs_lambda2": round(lam2, 4),
            "spectral_gap": round(gap, 4),
        })
    return rows


def report_relation(name: str, R: np.ndarray) -> None:
    prim = is_primitive(R)
    fd = forcing_distances(R)
    sym = is_color_symmetric(R)
    long_range = len(fd) > 1
    # A gadget can realize R only if it is color-symmetric. Long-range forcing
    # needs imprimitive R. The obstruction: the two conditions are incompatible
    # for single-vertex ports.
    flag = "gadget-realizable" if sym else "NOT realizable (breaks S_k)"
    forces = "LONG-RANGE forcing" if long_range else ("range-1 only" if fd else "no forced-diff")
    print(f"  {name:18s} color-sym={sym!s:5s} [{flag:26s}]  "
          f"{forces:18s}  forced@{fd[:6]}{'...' if len(fd) > 6 else ''}")


def enumerate_single_port_symmetric(k: int) -> list[dict]:
    """The color-symmetric (gadget-realizable) single-vertex-port relations are
    EXACTLY the four determined by (diagonal value, off-diagonal value), because
    S_k is 2-transitive (transitive on the diagonal and on ordered distinct
    pairs). Build all four and report forcing behavior. This is the structural
    reason single-vertex forcing is local."""
    out = []
    for diag in (0, 1):
        for off in (0, 1):
            R = np.full((k, k), off, dtype=np.uint8)
            np.fill_diagonal(R, diag)
            assert is_color_symmetric(R)  # all four are color-symmetric
            fd = forcing_distances(R)
            vacuous = (diag == 0 and off == 0)  # all-zero = gadget has NO coloring
            out.append({
                "diag": diag, "off": off,
                "meaning": {(1, 0): "I (forces SAME)", (0, 1): "J-I (forces DIFFER, range 1)",
                            (1, 1): "J (no constraint)", (0, 0): "0 (uncolorable, vacuous)"}[(diag, off)],
                "vacuous": vacuous,
                "long_range_forcing": (len(fd) > 1) and not vacuous,
            })
    return out


def main() -> None:
    k = 5
    print("Wildcard B: RG / transfer-matrix go/no-go for long-range color forcing")
    print("=" * 74)
    print("\nCorrection to the brainstorm: lambda_1 is the coloring-entropy growth")
    print("rate, NOT the forcing diagnostic. The diagnostic is the spectral GAP")
    print("(gap=0 => forcing relevant) <=> the port relation is IMPRIMITIVE.\n")

    print(f"[1] Canonical k={k} color-port relations:")
    report_relation("identity", rel_identity(k))
    report_relation("shift +1 (perm)", rel_shift(k, 1))
    report_relation("shift +2 (perm)", rel_shift(k, 2))
    report_relation("differ (J - I)", rel_differ(k))

    print("\n[2] Calibration on C_5 (repo R5 refutation: no non-adjacent forced pair):")
    c5 = c5_forced_different_pairs()
    print(f"  proper 3-colorings: {c5['n_proper_3colorings']}")
    print(f"  forced-different pairs: {c5['forced_different_pairs']}")
    print(f"  all forced pairs are ADJACENT: {c5['all_forced_are_adjacent']}")
    print(f"  non-adjacent forced-different: {c5['nonadjacent_forced_different']} "
          f"(empty confirms L45/R5)")

    print("\n[3] Fibonacci substitution a->ab, b->a, on per-tile port relations.")
    print("    Case (i): both tiles are 'differ' gadgets (the realizable lineage):")
    for row in fibonacci_inflate(rel_differ(k), rel_differ(k), levels=5):
        print(f"      L{row['level']}: primitive={row['a_supertile_primitive']!s:5s}"
              f"  gap={row['spectral_gap']:.3f}  forced@{row['forcing_distances'][:5]}")
    print("    Case (ii): tile a is a 'shift +1' color-shifter, tile b identity:")
    for row in fibonacci_inflate(rel_shift(k, 1), rel_identity(k), levels=5):
        print(f"      L{row['level']}: primitive={row['a_supertile_primitive']!s:5s}"
              f"  gap={row['spectral_gap']:.3f}  forced@{row['forcing_distances'][:5]}")

    print("\n[5] Why SINGLE-vertex ports cannot force long-range (the obstruction).")
    print("    A gadget's port relation must be color-symmetric (S_k-invariant).")
    print("    By 2-transitivity of S_k, the only such single-port relations are:")
    for r in enumerate_single_port_symmetric(k):
        tag = "VACUOUS" if r["vacuous"] else f"long-range forcing = {r['long_range_forcing']}"
        print(f"      diag={r['diag']} off={r['off']}: {r['meaning']:32s} {tag}")
    print("    No NON-VACUOUS relation gives long-range forcing. The color-SHIFTER")
    print("    that would (shift +1 in [1]) is NOT color-symmetric, so no gadget")
    print("    realizes it. These four relations are CLOSED under boolean product")
    print("    (a monoid: I is the unit; (J-I)(J-I)=J; J absorbs), and all are")
    print("    primitive-or-trivial. So a CHAIN of single-vertex-port gadgets keeps")
    print("    the s-t relation inside {0, I, J-I, J} and can never reach the rich")
    print("    Z_k (shift) forcing. That is the structural ceiling on the")
    print("    'two halves + bridges' / pairwise-port mechanism (L14-L20).")

    print("\n[6] Verdict and sharpened target.")
    print("    (a) The brainstorm's 'lambda_1 > 1' is the wrong diagnostic; the")
    print("        right one is imprimitivity / spectral gap of the port relation.")
    print("    (b) The RG/substitution step CONSERVES imprimitivity but cannot")
    print("        CREATE it: primitive ('differ') gadgets stay primitive under")
    print("        inflation (case i), so substitution is not a free lunch.")
    print("    (c) The single-port relations form a primitive monoid {0,I,J-I,J},")
    print("        so a chain forces s!=t only by composing to J-I, which needs")
    print("        either a direct differ-edge (adjacent; trivial) or a forced-SAME")
    print("        (I) sub-gadget spliced to a differ-edge. The clamp question thus")
    print("        FACTORS into two concrete sub-questions:")
    print("          (i)  can a planar UDG (omega<=3) force two NON-adjacent")
    print("               vertices to the SAME color (realize relation I)?")
    print("          (ii) the genuinely WIDE-interface case (>=2-vertex separator)")
    print("               where the boundary-coloring transfer matrix can be")
    print("               imprimitive without collapsing into the monoid -- this is")
    print("               exactly the clamp's degree->=5 split (Theorem R / L53).")
    print("    => The RG/substitution step only conserves the monoid, so it helps")
    print("       ONLY through case (ii). Sharpened target for Wildcard A: the")
    print("       SMALLEST wide-interface gadget with an imprimitive boundary-")
    print("       coloring transfer matrix that is unit-distance realizable (W3);")
    print("       and separately, settle sub-question (i) (forced-same under omega<=3).")


if __name__ == "__main__":
    main()
