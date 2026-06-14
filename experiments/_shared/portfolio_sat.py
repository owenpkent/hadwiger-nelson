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


def _greedy_clique(n, edges):
    """A maximal clique by greedy max-degree extension (cheap, not maximum)."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if u != v:
            adj[u].add(v)
            adj[v].add(u)
    clq = []
    for v in sorted(range(n), key=lambda x: -len(adj[x])):
        if all(u in adj[v] for u in clq):
            clq.append(v)
    return clq, adj


def _max_clique(n, edges, core_size=64):
    """Exact maximum clique restricted to the high-degree core (cliques live
    among high-degree vertices, so this is both cheap and exact at program
    scale). A bigger seed clique pins more colors and gives a stronger symmetry
    break than the greedy clique. Falls back to greedy if networkx is missing or
    the exact search finds nothing larger.

    Cheap because the program's graphs are sparse and K4-free in the UDG-necessary
    class (max clique <= 3) and triangle-free up the Mycielski tower (max clique
    2); find_cliques on a bounded core never blows up there.
    """
    greedy, adj = _greedy_clique(n, edges)
    if n == 0:
        return greedy
    try:
        import networkx as nx
    except Exception:
        return greedy
    deg = [len(adj[v]) for v in range(n)]
    core = sorted(range(n), key=lambda x: -deg[x])[:max(1, min(n, core_size))]
    cs = set(core)
    G = nx.Graph()
    G.add_nodes_from(core)
    for u in core:
        for w in adj[u]:
            if w in cs and u < w:
                G.add_edge(u, w)
    best = greedy
    for clq in nx.find_cliques(G):
        if len(clq) > len(best):
            best = clq
    return best


def build_color_cnf_symbreak(n, edges, k, return_meta=False, max_clique=True):
    r"""One-hot k-coloring CNF augmented with the color-permutation symmetry
    break that hn_solver applies natively, so a CDCL solver inherits it.

    Two ingredients, both sound (every proper coloring has a representative that
    satisfies them, obtained by relabeling colors in order of first appearance
    along the chosen vertex order with the seed clique pinned first):

      (1) CLIQUE FIXING. A greedy maximal clique C = [u_0, ..., u_{w-1}] is pinned
          u_j := color j by unit clauses. This kills the w! relabelings of the
          clique outright and gives an immediate omega > k refutation.
      (2) FIRST-APPEARANCE PRECEDENCE. With the vertices ordered clique-first then
          degree-descending as v_0, v_1, ..., color c (>= 1) may appear at v_i
          only if color c-1 already appears at some earlier vertex:
              x[v_i][c]  ->  OR_{j<i} x[v_j][c-1].
          Equivalently colors are numbered by order of first appearance, the same
          canonical frame hn_solver searches. The companion bound x[v_i][c]=0 for
          c > i (a vertex cannot introduce a color past its own rank) is added as
          units; with the clique pinned the effective rank is offset by the
          clique size.

    Equisatisfiable with build_color_cnf: the extra clauses only remove symmetric
    duplicates, never a color class. Validated by zero verdict disagreements vs
    the naive encoding in the self-test.

    Returns (clauses, var); with return_meta also the (order, clique) used.
    """
    def var(v, c):
        return v * k + c + 1

    clq = _max_clique(n, edges) if max_clique else _greedy_clique(n, edges)[0]
    if len(clq) > k:
        # omega > k: trivially UNSAT, return a contradiction
        unsat = [[1], [-1]]
        return (unsat, var, (clq, clq)) if return_meta else (unsat, var)
    clqset = set(clq)
    # vertex order: clique first (pins colors 0..w-1), then degree-descending
    deg = [0] * n
    for u, v in edges:
        if u != v:
            deg[u] += 1
            deg[v] += 1
    rest = sorted((v for v in range(n) if v not in clqset), key=lambda x: -deg[x])
    order = clq + rest
    rank = {v: i for i, v in enumerate(order)}

    cl = []
    # base one-hot: at-least-one + at-most-one per vertex, edge clauses
    for v in range(n):
        cl.append([var(v, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                cl.append([-var(v, c1), -var(v, c2)])
    for (u, w) in edges:
        for c in range(k):
            cl.append([-var(u, c), -var(w, c)])

    # (1) clique fixing (len(clq) <= k guaranteed above)
    for j, v in enumerate(clq):
        cl.append([var(v, j)])               # unit: v has color j

    # (2) first-appearance precedence + rank bound
    for i, v in enumerate(order):
        for c in range(k):
            if c > i:
                cl.append([-var(v, c)])      # rank bound: cannot introduce > rank
            elif c >= 1:
                # x[v][c] -> OR_{j<i} x[order[j]][c-1]
                clause = [-var(v, c)]
                for j in range(i):
                    clause.append(var(order[j], c - 1))
                cl.append(clause)

    if return_meta:
        return cl, var, (order, clq)
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


def colorable_portfolio(n, edges, k, want_coloring=False, symbreak=False, **kw):
    """k-colorability of a graph via the portfolio. If want_coloring and SAT,
    decode the winning model into a per-vertex coloring list.

    symbreak=True uses the color-permutation symmetry-broken encoding
    (build_color_cnf_symbreak), which gives the CDCL solvers the native symmetry
    break hn_solver carries and is dramatically faster on the structured
    instances this program generates (e.g. ~167x on M^3(C5) k=5 UNSAT, and it
    decides M^4(C5) k=6 UNSAT which the naive encoding cannot). The decoded
    coloring is identical in meaning; only symmetric duplicates are pruned."""
    builder = build_color_cnf_symbreak if symbreak else build_color_cnf
    clauses, var = builder(n, edges, k)
    out = portfolio_solve(clauses, want_model=want_coloring, **kw)
    if want_coloring and out["result"] and out["model"]:
        mset = set(x for x in out["model"] if x > 0)
        out["coloring"] = [next(c for c in range(k) if var(v, c) in mset)
                           for v in range(n)]
    return out


def solve_color(n, edges, k, symbreak=True, want_model=False, proof_path=None,
                budget=None, solver="Cadical195", max_clique=True):
    r"""Decide k-colorability and, on UNSAT, optionally emit a DRAT proof for a
    certificate-grade record. This is the recommended entry point for the
    in-class E14/E15 decisive solves: symbreak=True hands the CDCL solver the
    color-permutation symmetry break (so M^4 k=6 / P510 k=4 become tractable, and
    the UNSAT proofs are far smaller, ~66x on M^3), and proof_path captures the
    machine-checkable certificate.

    Returns a dict: result (bool|None for budget-exhausted), model (per-vertex
    coloring list if want_model and SAT), proof_path (written iff UNSAT and
    proof_path given), proof_lines (count), elapsed (s), clique (the seed clique),
    encoding ("symbreak"|"naive").

    Honest scope of the certificate: the DRAT proof certifies that the
    symmetry-broken CNF is UNSAT. The symmetry-breaking clauses are sound (every
    proper coloring keeps a representative), so this entails the graph is not
    k-colorable; it is not a DRAT proof of the naive CNF (which is intractable,
    the reason symmetry breaking is used). Verify externally with drat-trim if a
    fully mechanical end-to-end check is wanted.
    """
    import time as _time
    from pysat.solvers import (Cadical195, Cadical153, MapleChrono, MapleCM,  # noqa: F401
                               Glucose42, Glucose3, Minisat22)
    if symbreak:
        clauses, var, meta = build_color_cnf_symbreak(
            n, edges, k, return_meta=True, max_clique=max_clique)
        clique = meta[1]
    else:
        clauses, var = build_color_cnf(n, edges, k)
        clique = []
    cls = {k_: v for k_, v in locals().items() if k_ in _SOLVER_TABLE}[solver]
    want_proof = proof_path is not None
    s = cls(bootstrap_with=clauses, with_proof=want_proof)
    try:
        t0 = _time.time()
        if budget is not None:
            s.conf_budget(budget)
            res = s.solve_limited()
        else:
            res = s.solve()
        elapsed = round(_time.time() - t0, 3)
        model = None
        if res and want_model:
            mset = set(x for x in s.get_model() if x > 0)
            model = [next(c for c in range(k) if var(v, c) in mset)
                     for v in range(n)]
        proof_lines = 0
        written = None
        if res is False and want_proof:
            proof = s.get_proof()        # DRAT lines (pysat)
            proof_lines = len(proof)
            # An empty trace means Cadical refuted the formula in preprocessing /
            # unit propagation (trivially checkable); only write a file for a real
            # search proof, so an empty .drat is never left as a misleading record.
            if proof_lines > 0:
                pathlib_path = __import__("pathlib").Path(proof_path)
                pathlib_path.parent.mkdir(parents=True, exist_ok=True)
                pathlib_path.write_text("\n".join(proof) + "\n")
                written = str(pathlib_path)
        return {"result": res, "model": model, "proof_path": written,
                "proof_lines": proof_lines, "elapsed": elapsed,
                "clique": list(clique),
                "encoding": "symbreak" if symbreak else "naive"}
    finally:
        s.delete()


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
