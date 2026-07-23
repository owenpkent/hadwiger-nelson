r"""E17 independent both-free filter: K4-free AND K_{2,3}-free decision for
graph6-encoded graphs, in pure Python.

INDEPENDENCE CONTRACT: this module is the double-check layer for the C PRUNE
plugin (e17_prune.c) and must not share code or algorithm shape with it. The C
plugin checks incrementally against the last-added vertex during geng's
augmentation; this module decodes the finished graph and checks GLOBALLY:
  - K_{2,3} as a subgraph  <=>  some vertex pair has >= 3 common neighbors
    (checked over ALL pairs, not just pairs at the frontier);
  - K4  <=>  some edge (u,v) has two adjacent common neighbors
    (checked over all edges).
Adjacency is Python arbitrary-precision int bitsets, graph6 decoding is local
(no networkx in the hot path; networkx is used only in --selftest as a third
opinion on the decoder).

CLI (used as the pipe target for stock-geng cross-counts):
    geng -q 8 | .venv/bin/python e17_bothfree_filter.py --count
    ... | e17_bothfree_filter.py --pass      # echo both-free lines to stdout
    .venv/bin/python e17_bothfree_filter.py --selftest
"""
from __future__ import annotations
import sys


def graph6_to_adj(line: str):
    """Decode a graph6 line (n <= 62 supported; enough for E17) into
    (n, adj) where adj[v] is an int bitmask of neighbors."""
    s = line.strip()
    if s.startswith(">>graph6<<"):
        s = s[len(">>graph6<<"):]
    data = [ord(c) - 63 for c in s]
    if any(d < 0 or d > 63 for d in data):
        raise ValueError(f"bad graph6 char in {s!r}")
    n = data[0]
    if n == 63:
        raise ValueError("n >= 63 not supported by this decoder")
    bits = data[1:]
    adj = [0] * n
    idx = 0          # index into the upper-triangle bit stream
    for v in range(1, n):
        for u in range(v):
            byte, off = divmod(idx, 6)
            if byte < len(bits) and (bits[byte] >> (5 - off)) & 1:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
            idx += 1
    return n, adj


def is_k23_free(n: int, adj) -> bool:
    """No vertex pair (adjacent or not) has 3+ common neighbors."""
    for u in range(n):
        au = adj[u]
        for v in range(u + 1, n):
            if (au & adj[v]).bit_count() >= 3:
                return False
    return True


def is_k4_free(n: int, adj) -> bool:
    """No edge has two adjacent common neighbors."""
    for u in range(n):
        au = adj[u]
        w = au >> (u + 1)
        v = u + 1
        while w:
            if w & 1:
                common = au & adj[v]
                a = 0
                cc = common
                while cc:
                    if cc & 1:
                        if adj[a] & common & ~((1 << (a + 1)) - 1):
                            return False
                    cc >>= 1
                    a += 1
            w >>= 1
            v += 1
    return True


def is_bothfree(line: str) -> bool:
    n, adj = graph6_to_adj(line)
    return is_k23_free(n, adj) and is_k4_free(n, adj)


def _selftest() -> None:
    import networkx as nx
    # decoder cross-check + property cross-check vs networkx on random graphs
    import random
    random.seed(17)
    bad = 0
    for trial in range(300):
        n = random.randint(4, 12)
        p = random.uniform(0.1, 0.9)
        G = nx.gnp_random_graph(n, p, seed=trial)
        line = nx.to_graph6_bytes(G, header=False).decode().strip()
        n2, adj = graph6_to_adj(line)
        assert n2 == n
        for u, v in G.edges():
            assert (adj[u] >> v) & 1 and (adj[v] >> u) & 1
        assert sum(a.bit_count() for a in adj) == 2 * G.number_of_edges()
        # reference property checks via networkx
        ref_k4 = any(len(c) >= 4 for c in nx.find_cliques(G)) if n else False
        ref_k23 = False
        nodes = list(G.nodes())
        for i in range(n):
            for j in range(i + 1, n):
                cn = set(G[nodes[i]]) & set(G[nodes[j]])
                if len(cn) >= 3:
                    ref_k23 = True
                    break
            if ref_k23:
                break
        if is_k4_free(n, adj) != (not ref_k4):
            bad += 1
        if is_k23_free(n, adj) != (not ref_k23):
            bad += 1
    print(f"selftest: {bad} disagreements over 300 random graphs")
    assert bad == 0
    # known answers: K4 itself, K_{2,3} itself, C5, Petersen
    tests = [
        (nx.complete_graph(4), False, True),
        (nx.complete_bipartite_graph(2, 3), True, False),
        (nx.cycle_graph(5), True, True),
        (nx.petersen_graph(), True, True),
    ]
    for G, k4f, k23f in tests:
        line = nx.to_graph6_bytes(G, header=False).decode().strip()
        n, adj = graph6_to_adj(line)
        assert is_k4_free(n, adj) == k4f, G
        assert is_k23_free(n, adj) == k23f, G
    print("selftest: known-answer battery OK (K4, K_{2,3}, C5, Petersen)")


def main(argv) -> None:
    if "--selftest" in argv:
        _selftest()
        return
    mode = "--count" if "--count" in argv else "--pass"
    total = kept = 0
    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith(">"):
            continue
        total += 1
        if is_bothfree(line):
            kept += 1
            if mode == "--pass":
                out.write(line + "\n")
    print(f"e17_bothfree_filter: {kept} both-free of {total} read",
          file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
