"""Width-2 port-relation classification for the SPT/string-order route (L55 case ii).

Setting. A width-2 gadget interface is an ordered pair of ADJACENT port vertices
(a unit edge). Under k colors its boundary alphabet is X = ordered pairs of
distinct colors, |X| = k(k-1). The set of proper colorings of any gadget is
closed under global S_k recoloring, so the achievable port relation
R subset X x X is a UNION OF S_k-ORBITS on X x X. For k >= 4 there are exactly
7 orbits, indexed by the equality pattern between left pair (a,b) and right
pair (c,d) with a != b, c != d:

    e    : a=c, b=d        (identity)
    s    : a=d, b=c        (swap)
    Oac  : a=c only
    Oad  : a=d only
    Obc  : b=c only
    Obd  : b=d only
    dis  : {a,b} cap {c,d} empty

Definitions.
  STEALTH    : all four single-vertex marginals (L1R1, L1R2, L2R1, L2R2) admit
               both an equal-color and a distinct-color completion. A stealth
               relation is invisible to every width-1 sweep (L45/L56/L57 test
               exactly these marginals).
  PERSISTENT : no Boolean power R^n is the full relation J (forcing survives
               chains of every length; the L55-correct diagnostic, since
               primitivity = forcing decays to free).

Claim to verify (Conjecture C1, "width-2 stealth rigidity"): for k >= 5 the
ONLY nonempty stealth persistent union-of-orbits relation is {e, s}, i.e.
unordered-PAIR TRANSMISSION: {c(L1),c(L2)} = {c(R1),c(R2)}. For k = 4 the
disjointness class is complementary-pair transmission, so {e,s,dis} joins.

Also verifies the closure lemma: any gadget with relation subset {e,s}, plus a
K_{2,2} of unit edges between its own ports, is k-UNSAT (gives chi >= k+1).

Pure exact Boolean algebra, no floats. Runtime: seconds.
"""

from itertools import combinations, permutations, product

CLASS_NAMES = ["e", "s", "Oac", "Oad", "Obc", "Obd", "dis"]


def build_classes(k):
    X = [(a, b) for a in range(k) for b in range(k) if a != b]
    idx = {x: i for i, x in enumerate(X)}
    n = len(X)
    classes = {name: set() for name in CLASS_NAMES}
    for (a, b) in X:
        for (c, d) in X:
            ac, ad, bc, bd = a == c, a == d, b == c, b == d
            if ac and bd:
                name = "e"
            elif ad and bc:
                name = "s"
            elif ac:
                name = "Oac"
            elif ad:
                name = "Oad"
            elif bc:
                name = "Obc"
            elif bd:
                name = "Obd"
            else:
                name = "dis"
            classes[name].add((idx[(a, b)], idx[(c, d)]))
    return X, idx, classes


def compose(R, S, n):
    out_by_left = {}
    S_by_left = {}
    for (y, z) in S:
        S_by_left.setdefault(y, set()).add(z)
    comp = set()
    for (x, y) in R:
        for z in S_by_left.get(y, ()):
            comp.add((x, z))
    return comp


def relation_of(subset, classes):
    R = set()
    for name in subset:
        R |= classes[name]
    return R


def classes_of(R, classes):
    return frozenset(name for name in CLASS_NAMES if classes[name] & R)


def is_stealth(R, X):
    # marginals: positions (left_slot, right_slot) in {(0,0),(0,1),(1,0),(1,1)}
    for li, ri in product((0, 1), repeat=2):
        seen_eq = seen_ne = False
        for (xi, yi) in R:
            l, r = X[xi], X[yi]
            if l[li] == r[ri]:
                seen_eq = True
            else:
                seen_ne = True
            if seen_eq and seen_ne:
                break
        if not (seen_eq and seen_ne):
            return False
    return True


def is_persistent(R, classes, n, full_size):
    seen = set()
    P = set(R)
    while True:
        key = frozenset(P)
        if key in seen:
            return True  # cycled without ever reaching full
        seen.add(key)
        if len(P) == full_size:
            return False
        P = compose(P, R, n)


def k22_closure_unsat(R, X):
    # ports L1L2 and R1R2 joined by K_{2,2}: need a!=c, a!=d, b!=c, b!=d
    for (xi, yi) in R:
        (a, b), (c, d) = X[xi], X[yi]
        if a != c and a != d and b != c and b != d:
            return False
    return True


def run(k):
    X, idx, classes = build_classes(k)
    n = len(X)
    full_size = sum(len(v) for v in classes.values())
    persistent, stealth_persistent = [], []
    for r in range(1, 8):
        for subset in combinations(CLASS_NAMES, r):
            R = relation_of(subset, classes)
            if is_persistent(R, classes, n, full_size):
                persistent.append(subset)
                if is_stealth(R, X):
                    stealth_persistent.append(subset)
    print(f"k={k}: |X|={n}, full relation size={full_size}")
    print(f"  persistent nonempty relations ({len(persistent)}):")
    for s in persistent:
        print(f"    {{{', '.join(s)}}}")
    print(f"  STEALTH + persistent ({len(stealth_persistent)}):")
    for s in stealth_persistent:
        print(f"    {{{', '.join(s)}}}  <-- ")
    es = relation_of(("e", "s"), classes)
    print(f"  pair-transmitter {{e,s}}: closed under composition: "
          f"{classes_of(compose(es, es, n), classes) == frozenset(('e', 's'))}, "
          f"K22-closure k-UNSAT: {k22_closure_unsat(es, X)}")
    print()
    return stealth_persistent


if __name__ == "__main__":
    results = {}
    for k in (4, 5, 6, 7):
        results[k] = run(k)
    c1 = all(results[k] == [("e", "s")] for k in (5, 6, 7))
    print(f"C1 (k>=5: unique stealth persistent relation is {{e,s}}): {c1}")
