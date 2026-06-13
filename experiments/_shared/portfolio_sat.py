r"""Portfolio k-colorability / SAT backend.

Motivated by the L64 finding: on the identical 470-edge in-class instance,
Cadical ran 12+ hours undecided while MapleChrono decided it in 155 s. Near a
SAT phase boundary, runtimes are heavy-tailed and heuristic-dependent (the
Gomes-Selman observation), so committing to a single solver is a trap. This
backend runs several CDCL solvers in PARALLEL PROCESSES and returns the FIRST
decisive answer together with the winning solver's identity, then terminates the
laggards.

Design notes.
- True wall-clock portfolio via `multiprocessing` (spawn-safe on Windows): each
  child builds its own solver from the shared clause list and solves to
  completion. The GIL is irrelevant because solvers run in separate processes.
- No per-solver conflict budget by default: unbounded solves are always decisive
  (True/False), so the first child to answer wins outright. An optional
  wall-clock `time_limit` bounds the whole call.
- Cadical stays in the roster because it is the certificate-grade solver (DRAT
  proofs) for the UNSAT proof of record; MapleChrono and Glucose carry the
  discovery load. The portfolio gets the best of both without choosing in
  advance.

CLI:  python portfolio_sat.py path/to/instance.cnf [--time 600] [--solvers MapleChrono,Cadical195,Glucose42]
"""
from __future__ import annotations
import multiprocessing as mp
import time
import sys

# Roster ordered by empirical discovery strength on this program's instances
# (Maple first, Cadical kept for certification / its occasional UNSAT wins).
DEFAULT_SOLVERS = ("MapleChrono", "Cadical195", "Glucose42")

_SOLVER_TABLE = {
    "Cadical195": "Cadical195",
    "Cadical153": "Cadical153",
    "MapleChrono": "MapleChrono",
    "MapleCM": "MapleCM",
    "Glucose42": "Glucose42",
    "Glucose3": "Glucose3",
    "Minisat22": "Minisat22",
}


def build_color_cnf(n, edges, k):
    """Direct (one-hot) k-coloring CNF. Returns (clauses, var) with var(v,c)."""
    def var(v, c):
        return v * k + c + 1
    cl = []
    for v in range(n):
        cl.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cl.append([-var(v, c1), -var(v, c2)])
    for (u, w) in edges:
        for c in range(k):
            cl.append([-var(u, c), -var(w, c)])
    return cl, var


def _worker(solver_name, clauses, want_model, q):
    """Child process: build the named solver, solve, push the verdict."""
    from pysat.solvers import (Cadical195, Cadical153, MapleChrono, MapleCM,  # noqa: F401
                               Glucose42, Glucose3, Minisat22)
    cls = {k: v for k, v in locals().items() if k in _SOLVER_TABLE}[solver_name]
    s = cls(bootstrap_with=clauses)
    try:
        t0 = time.time()
        res = s.solve()
        model = s.get_model() if (res and want_model) else None
        q.put((solver_name, res, model, round(time.time() - t0, 2)))
    finally:
        s.delete()


def portfolio_solve(clauses, solvers=DEFAULT_SOLVERS, time_limit=None,
                    want_model=False, verbose=False):
    """Run `solvers` in parallel processes; return the first decisive verdict.

    Returns dict: result (bool|None), winner (str|None), elapsed (s),
    model (list[int]|None), per_solver (name -> seconds, for any that finished).
    result is None only if the wall-clock time_limit was hit first.
    """
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    procs = {}
    for name in solvers:
        if name not in _SOLVER_TABLE:
            raise ValueError(f"unknown solver {name!r}; "
                             f"choices: {sorted(_SOLVER_TABLE)}")
        p = ctx.Process(target=_worker, args=(name, clauses, want_model, q),
                        daemon=True)
        p.start()
        procs[name] = p

    t0 = time.time()
    deadline = (t0 + time_limit) if time_limit else None
    winner = result = model = None
    per_solver = {}
    finished = 0
    try:
        while finished < len(procs):
            timeout = None if deadline is None else max(0.05, deadline - time.time())
            try:
                name, res, mdl, secs = q.get(timeout=timeout)
            except Exception:
                break  # queue.Empty -> wall-clock limit reached
            finished += 1
            per_solver[name] = secs
            if verbose:
                print(f"  [{name}] {res} in {secs}s", flush=True)
            if res is not None:
                winner, result, model = name, res, mdl
                break
    finally:
        for p in procs.values():
            if p.is_alive():
                p.terminate()
        for p in procs.values():
            p.join(timeout=1)
    return {"result": result, "winner": winner,
            "elapsed": round(time.time() - t0, 2),
            "model": model, "per_solver": per_solver}


def colorable_portfolio(n, edges, k, want_coloring=False, **kw):
    """k-colorability of a graph via the portfolio. If want_coloring and SAT,
    decode the winning model into a per-vertex coloring list."""
    clauses, var = build_color_cnf(n, edges, k)
    out = portfolio_solve(clauses, want_model=want_coloring, **kw)
    if want_coloring and out["result"] and out["model"]:
        mset = set(x for x in out["model"] if x > 0)
        out["coloring"] = [next(c for c in range(k) if var(v, c) in mset)
                           for v in range(n)]
    return out


def _read_dimacs(path):
    clauses, nv = [], 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in "cp":
                if line.startswith("p cnf"):
                    nv = int(line.split()[2])
                continue
            lits = [int(x) for x in line.split() if x != "0"]
            if lits:
                clauses.append(lits)
    return clauses, nv


def _main(argv):
    if not argv:
        print(__doc__)
        return
    path = argv[0]
    time_limit = None
    solvers = DEFAULT_SOLVERS
    i = 1
    while i < len(argv):
        if argv[i] == "--time":
            time_limit = float(argv[i + 1]); i += 2
        elif argv[i] == "--solvers":
            solvers = tuple(argv[i + 1].split(",")); i += 2
        else:
            i += 1
    clauses, nv = _read_dimacs(path)
    print(f"portfolio: {path} ({nv} vars, {len(clauses)} clauses), "
          f"solvers={list(solvers)}", flush=True)
    out = portfolio_solve(clauses, solvers=solvers, time_limit=time_limit,
                          verbose=True)
    verdict = {True: "SAT", False: "UNSAT", None: "TIMEOUT"}[out["result"]]
    print(f"RESULT: {verdict} | winner={out['winner']} | "
          f"elapsed={out['elapsed']}s | per_solver={out['per_solver']}")


if __name__ == "__main__":
    _main(sys.argv[1:])
