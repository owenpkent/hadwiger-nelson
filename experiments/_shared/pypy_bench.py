r"""PyPy-vs-CPython benchmark for the pure-Python core of hn_solver_cdcl.

Runs only kcolor_learn (no pysat, no numpy), so PyPy's JIT applies fully. Usage:
  python      experiments/_shared/pypy_bench.py          # CPython, M3 only
  <pypy> experiments/_shared/pypy_bench.py --m4          # PyPy, M3 + M4 ceiling
"""
import sys
import time
import pathlib
import platform

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hn_solver_cdcl import kcolor_learn  # noqa: E402


def cycle(m):
    return m, [(j, (j + 1) % m) for j in range(m)]


def myc(nn, e):
    out = list(e)
    for u, v in e:
        out += [(nn + u, v), (nn + v, u)]
    for j in range(nn):
        out.append((nn + j, 2 * nn))
    return 2 * nn + 1, out


def main():
    do_m4 = "--m4" in sys.argv
    cur = cycle(5)
    lev = {}
    for L in range(1, 5):
        cur = myc(*cur)
        lev[L] = cur

    print(f"interpreter: {platform.python_implementation()} "
          f"{platform.python_version()}", flush=True)

    n, e = lev[3]
    # warmup so the JIT compiles the hot loop before timing
    kcolor_learn(*lev[2], k=4, max_learn=0)
    for ml in (0, 8):
        t = time.perf_counter()
        v, s = kcolor_learn(n, e, 5, max_learn=ml, return_stats=True)
        dt = time.perf_counter() - t
        print(f"  M3(C5) k=5 ml={ml}: {v} nodes={s['nodes']:,} "
              f"{dt:.2f}s ({s['nodes'] / dt:,.0f} n/s)", flush=True)

    if do_m4:
        n, e = lev[4]
        t = time.perf_counter()
        v, s = kcolor_learn(n, e, 6, max_learn=0, node_limit=400_000_000,
                            return_stats=True)
        dt = time.perf_counter() - t
        print(f"  M4(C5) k=6 ml=0: {v} nodes={s['nodes']:,} "
              f"{dt:.1f}s ({s['nodes'] / dt:,.0f} n/s)", flush=True)


if __name__ == "__main__":
    main()
