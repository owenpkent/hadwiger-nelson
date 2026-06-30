# Hadwiger-Nelson attack prompt (paste-ready chat twin)

For pasting into a fresh chat with a capable model that has a Python sandbox but no
repo. Same brief as the no-repo twin, plus an inlined ~40-line exact-arithmetic UDG
builder and k-colorability checker so the model can run the wrong-approach detectors
itself before trusting any conjecture. Plain Unicode math (no LaTeX surface).

Canonical source: the `DEFAULT_BRIEF` in `.claude/workflows/hn-lens-attack.js`,
backed by `experiments/LOAD_BEARING_FACTS.md` and `experiments/FREEZE_LIST.md`.

---

You are a research mathematician attacking the Hadwiger-Nelson problem: the
chromatic number chi(R^2) of the unit-distance graph on the Euclidean plane. Known:
5 <= chi <= 7. The frontier localizes to ONE missing object: a unit-distance-realizable
"flexible color-clamp", a chi=5 UDG with a non-adjacent pair (s,t) forced to different
colors in every proper 5-coloring (contracting s=t then gives chi >= 6). The abstract
object exists (48-vertex triangle-free SAT witness); all difficulty is realizing it in
R^2. The known chi=5 lineage is forcing-sterile, so the object must come from a NEW UDG
that is K4-free, 6-critical, and K_{2,3}-free.

Before you trust ANY lower-bound idea, run it against the three control objects whose
chromatic numbers are known and different from chi(R^2). A correct argument must
distinguish R^2 from all three:
  - Q^2 (rational plane): chi = 2. Combinatorial content must use density/topology of R.
  - L^infinity plane: chi = 4. Geometric content must use Euclidean rigidity.
  - R^1 (the line): chi = 2. Measure content must use the rotation group O(2).

You can build and color finite unit-distance graphs with this self-contained code
(exact arithmetic via fractions for the rational controls; floats with a tolerance
otherwise). Use it to sanity-check that your method does NOT over-prove on a control.

```python
from fractions import Fraction as F
from itertools import combinations
import pysat  # if available: from pysat.solvers import Solver ; else use the greedy/backtrack fallback

def edges_exact(points, dist2_target=F(1), metric="euclid2"):
    """points: list of coordinate tuples (Fraction or float). Returns unit-distance edges."""
    E = []
    for i, j in combinations(range(len(points)), 2):
        p, q = points[i], points[j]
        if metric == "euclid2":
            d = sum((a-b)**2 for a, b in zip(p, q))
        elif metric == "linf":
            d = max(abs(a-b) for a, b in zip(p, q))
        if d == dist2_target if metric=="euclid2" else d == 1:
            E.append((i, j))
    return E

def k_colorable(n, edges, k):
    """DPLL-free backtracking k-coloring (fine for the small controls). True if k-colorable."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    color = [-1]*n
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    def bt(idx):
        if idx == n: return True
        v = order[idx]
        used = {color[u] for u in adj[v] if color[u] != -1}
        for c in range(k):
            if c not in used:
                color[v] = c
                if bt(idx+1): return True
                color[v] = -1
        return False
    return bt(0)

def chromatic(n, edges, kmax=7):
    for k in range(1, kmax+1):
        if k_colorable(n, edges, k): return k
    return None

# Control checks (each should print its known value):
# Q^2 sample: rational points; the Q^2 UDG is bipartite, so chi must be 2.
q2 = [(F(0),F(0)),(F(1),F(0)),(F(0),F(1)),(F(3,5),F(4,5)),(F(4,5),F(3,5))]
print("Q^2 sample chi (expect 2):", chromatic(len(q2), edges_exact(q2)))
# L^infinity 4x4 king grid: chi must be 4.
grid = [(i, j) for i in range(4) for j in range(4)]
print("L^inf grid chi (expect 4):", chromatic(len(grid), edges_exact(grid, metric="linf")))
```

If your method, transcribed into a check on Q^2 or the L^inf grid, would force a value
above its known chi, your method is wrong. Discard it.

KNOWN KILLS (do not re-propose): long-range forcing inside the known lineage;
single-vertex-port gadget chains; "RG leading eigenvalue" forcing diagnostics;
DOF/over-determination counting; norm-blind Borel/Steinhaus; map-type 6-colorings;
order-1/2 moment relaxations for chi_m; treating chi_m >= 6 as implying chi >= 6.

YOUR TASK. From first principles, give 2-4 precise, falsifiable conjectures toward
realizing the missing object (or a genuinely different route), at least one unstated in
the literature, each with a concrete refuting computation, each self-checked against the
three controls above. Wild but precise beats safe but vague. No em dashes.
