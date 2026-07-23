r"""E17 window table: the per-n edge window for 6-critical members of the
"both-free" class (K4-free AND K_{2,3}-free).

Frame (L63 + the paper):
  - K_{2,3}-free (as a subgraph) == every vertex pair has codegree <= 2. Counting
    cherries: sum_v C(deg v, 2) <= 2 * C(n, 2), and convexity gives the ceiling
        m <= n * (1 + sqrt(8n - 7)) / 4.
  - Kostochka-Yancey for 6-critical graphs:  m >= (28n - 18) / 10, and every
    6-critical graph has min degree >= 5 (so also m >= ceil(5n/2)).
  - Folkman floor (Lathrop-Radziszowski 2011): the smallest K4-free graph with
    chi >= 6 has n = 16, so the search starts at n = 16.

Any chi >= 6 member of the class contains a 6-critical subgraph that is itself
in the class (both properties are subgraph-closed), so it suffices to search
connected graphs with min degree >= 5 and m in [KY floor, codegree ceiling]
for each n. The window is EMPTY for n <= 12 (the rigorous L63 corollary).

Run:  .venv/bin/python experiments/combinatorial/e17_window_table.py [nmax]
"""
from __future__ import annotations
import math
import sys


def ky_floor(n: int) -> int:
    """Kostochka-Yancey edge floor for a 6-critical graph on n vertices,
    combined with the min-degree-5 floor."""
    ky = math.ceil((28 * n - 18) / 10)
    mindeg = math.ceil(5 * n / 2)
    return max(ky, mindeg)


def codegree_ceiling(n: int) -> int:
    """Max edges of a K_{2,3}-free graph on n vertices (codegree <= 2)."""
    return math.floor(n * (1 + math.isqrt(8 * n - 7)) / 4) \
        if math.isqrt(8 * n - 7) ** 2 == 8 * n - 7 \
        else math.floor(n * (1 + math.sqrt(8 * n - 7)) / 4)


def window(n: int):
    """(mine, maxe) inclusive edge window for the E17 search at order n,
    or None if the window is empty."""
    lo, hi = ky_floor(n), codegree_ceiling(n)
    return (lo, hi) if lo <= hi else None


def main(nmax: int = 26) -> None:
    print(f"{'n':>3} {'KY floor':>9} {'ceiling':>8} {'window':>10} {'width':>6}")
    for n in range(10, nmax + 1):
        w = window(n)
        if w is None:
            print(f"{n:>3} {ky_floor(n):>9} {codegree_ceiling(n):>8} "
                  f"{'EMPTY':>10} {'-':>6}")
        else:
            lo, hi = w
            mark = "  <- search floor (Folkman n=16)" if n == 16 else ""
            print(f"{n:>3} {lo:>9} {hi:>8} {f'{lo}..{hi}':>10} "
                  f"{hi - lo + 1:>6}{mark}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 26)
