r"""Width-2 port relation monoid classification (BUILDER, L55 route ii head-on).

Setup. A width-2 port is an ordered pair of vertices; with k colors and an EDGE
port (the pair at unit distance) the port state space is X = ordered pairs of
DISTINCT colors, |X| = k(k-1). A gadget G with two ports induces a relation
R(G) <= X x X: the set of (port1-state, port2-state) pairs realized over all
proper k-colorings of G. R(G) is invariant under the diagonal S_k action, so it
is a union of S_k-orbits on X x X. For k >= 4 the orbits of S_k on 4-tuples
(a,b,c,d) with a != b, c != d are the restricted-growth signatures: exactly 7
of them for edge ports (15 for ports at non-edge distance, where a = b is
allowed).

This script classifies, for each of the 2^7 - 1 (and 2^15 - 1) nonempty
S_k-symmetric relations R:
  - INFORMATIVE: no power R^n equals the full relation J (chains of R never
    blur to "anything goes"; this is the imprimitivity that L55 route ii needs)
  - PAIRWISE-FREE: each of the 4 cross-projections (slot i of port 1 vs slot j
    of port 2) realizes both "same color" and "different color" (so the
    relation is INVISIBLE to the L45/L56/L57 pairwise forcing sweeps)
  - SLOT1-FORCING: R avoids every orbit with a = c, i.e. any chain whose
    composed relation is <= R forces the two slot-1 vertices to differ
    (a non-adjacent forced-different pair = the W3 clamp payload).

Headline question: which relations are BOTH informative AND pairwise-free?
Prediction (to be confirmed by this run): exactly the set-transporters built
from O_ID (a=c, b=d) and O_SW (a=d, b=c), with T = O_ID u O_SW the unique
maximal one, and the monoid {ID, SW, T} containing the group Z/2 = {ID, SW}.
That Z/2 is the imprimitivity engine: an odd-length chain of SW-gadgets, or a
T-chain capped by a cone vertex over the far port, forces a non-adjacent pair
different while every single pair stays free.

Pure combinatorics: no SAT, no geometry. Output cached as JSON.
"""
from __future__ import annotations
import itertools, json, pathlib

import numpy as np

CACHE = pathlib.Path(__file__).resolve().parent / "_cache"
CACHE.mkdir(exist_ok=True)


def rgs(vals):
    """Restricted growth signature of a tuple (orbit label under S_k)."""
    seen, out = {}, []
    for v in vals:
        if v not in seen:
            seen[v] = len(seen)
        out.append(seen[v])
    return tuple(out)


def build(k, edge_port):
    """Return (states X, orbit signatures, orbit boolean matrices)."""
    C = range(k)
    if edge_port:
        X = [(a, b) for a in C for b in C if a != b]
    else:
        X = [(a, b) for a in C for b in C]
    idx = {p: i for i, p in enumerate(X)}
    mats = {}
    for (a, b) in X:
        for (c, d) in X:
            s = rgs((a, b, c, d))
            m = mats.setdefault(s, np.zeros((len(X), len(X)), dtype=bool))
            m[idx[(a, b)], idx[(c, d)]] = True
    return X, sorted(mats), mats


def powers_until_repeat(R):
    seen, out, P = set(), [], R.copy()
    while True:
        key = P.tobytes()
        if key in seen:
            return out
        seen.add(key)
        out.append(P)
        P = (P.astype(np.uint8) @ R.astype(np.uint8)) > 0


def cross_free(orbset, X):
    """True iff all 4 cross-projections realize both = and != (pairwise-free)."""
    # slot positions: port1 = (0,1), port2 = (2,3)
    need = {(i, j): set() for i in (0, 1) for j in (2, 3)}
    for sig in orbset:
        # sig is an rgs over (a,b,c,d); equality of slots i,j is sig[i]==sig[j]
        for (i, j) in need:
            need[(i, j)].add(sig[i] == sig[j])
    return all(v == {True, False} for v in need.values())


def classify(k, edge_port):
    X, sigs, mats = build(k, edge_port)
    n = len(X)
    J = np.ones((n, n), dtype=bool)
    results = []
    for r in range(1, len(sigs) + 1):
        for orbset in itertools.combinations(sigs, r):
            R = np.zeros((n, n), dtype=bool)
            for s in orbset:
                R |= mats[s]
            pows = powers_until_repeat(R)
            informative = not any(P.all() for P in pows)
            free = cross_free(orbset, X)
            slot1_forcing = all(s[0] != s[2] for s in orbset)
            if informative:
                results.append({
                    "orbits": [list(s) for s in orbset],
                    "informative": True,
                    "pairwise_free": free,
                    "slot1_forcing": slot1_forcing,
                    "n_powers_before_cycle": len(pows),
                })
    return sigs, results


def main():
    out = {}
    for (k, edge_port, label) in [(5, True, "k5_edge"), (5, False, "k5_any"),
                                  (4, True, "k4_edge")]:
        sigs, res = classify(k, edge_port)
        inf_free = [r for r in res if r["pairwise_free"]]
        # inclusion-maximal among informative+pairwise-free
        sets = [frozenset(tuple(s) for s in r["orbits"]) for r in inf_free]
        maximal = [r for r, s in zip(inf_free, sets)
                   if not any(s < t for t in sets)]
        out[label] = {
            "n_orbits": len(sigs),
            "orbit_signatures": [list(s) for s in sigs],
            "n_informative": len(res),
            "informative": res,
            "n_informative_and_pairwise_free": len(inf_free),
            "informative_and_pairwise_free": inf_free,
            "maximal_informative_free": maximal,
        }
        print(f"[{label}] orbits={len(sigs)} informative={len(res)} "
              f"informative+pairwise_free={len(inf_free)}")
        for r in inf_free:
            print("   free+informative:", r["orbits"],
                  "slot1_forcing=", r["slot1_forcing"])
        print("   maximal:", [r["orbits"] for r in maximal])

    # sanity: SW^2 = ID, T idempotent, for k=5 edge ports
    X, sigs, mats = build(5, True)
    ID = mats[(0, 1, 0, 1)]
    SW = mats[(0, 1, 1, 0)]
    T = ID | SW
    sw2 = (SW.astype(np.uint8) @ SW.astype(np.uint8)) > 0
    t2 = (T.astype(np.uint8) @ T.astype(np.uint8)) > 0
    print("SW o SW == ID :", bool((sw2 == ID).all()))
    print("T o T == T   :", bool((t2 == T).all()))
    out["sanity"] = {"SW_squared_is_ID": bool((sw2 == ID).all()),
                     "T_idempotent": bool((t2 == T).all())}

    (CACHE / "w2_port_monoid.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print("cached ->", CACHE / "w2_port_monoid.json")


if __name__ == "__main__":
    main()
