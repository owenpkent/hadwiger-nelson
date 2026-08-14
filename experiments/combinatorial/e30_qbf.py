r"""E30: stop hiding the universal quantifier. The question as a 2-QBF.

Everything so far answers $\exists G\,\forall c$ by CEGAR: the chromatic-number
propagator finds a $5$-colouring of a candidate, learns one clause forbidding it,
and hands the conflict back. That works (L78: $n\le17$ closed) and then walls,
and the shape of the wall says the encoding is the problem rather than the budget.
At $n=18$, cell $m=51$ left 73 of 390 cubes unfinished after 61 cpu-hours: the
solver is rediscovering colourability structure one counterexample at a time,
and the sparse cells have too many counterexamples to enumerate.

A 2-QBF puts the universal half INSIDE the formula, where the solver can reason
about it instead of sampling it:

    exists  E (edge variables, plus the class encoding's auxiliaries)
    forall  c (a colour assignment for every vertex)
        class(E)  AND  ( c is not a valid colouring  OR  c fails on some edge of E )

"c fails on some edge" is $\bigvee_{u<v} \bigl(x_{uv} \wedge \mathrm{same}(u,v,c)\bigr)$,
a circuit over both blocks. A model of this is a graph in the class no $5$-colouring
survives, which is exactly a $\chi\ge6$ member; unsatisfiability is exactly the
theorem. Nothing about the mathematics changes, only where the quantifier lives.

WHY IT MIGHT ALSO FIX CERTIFICATION. L80 showed the CEGAR verdicts cannot be
DRAT/LRAT-checked, and not for want of tooling: $\Phi_{n,m}$ is SATISFIABLE, so
there is no propositional refutation to check, and the unsatisfiability lives in a
semantic side condition outside the formula. In the QBF the side condition IS the
formula, so the object being refuted is the thing a QBF certificate talks about.
This module does not produce certificates, but it moves the question to where they
are possible.

HONEST ODDS. QBF solvers are temperamental and this may be worse than CEGAR. That
is why the ladder below is the same one E20 passed, run BEFORE any new claim: if
the QBF route cannot reproduce $n=15$ and $n=16$, it does not get to speak about
$n=18$. Cost is reported per cell either way, so a negative here is a measured
comparison rather than an impression.

ENCODING NOTES that matter for correctness.

  * Colour variables are five per vertex with an explicit validity gate (exactly
    one colour each). The universal player may choose an INVALID assignment, and
    those must be excused, or the adversary wins trivially by colouring nothing.
  * The class encoding's auxiliary variables (the reified degree counters) are
    existential and functionally determined by the edges, so they belong in the
    outer block. Putting them anywhere else would let the universal player
    sabotage the counters.
  * Every CNF clause becomes an `or` gate over its literals, so the existing
    verified `CriticalEncoding` is reused verbatim rather than re-derived.

Usage:
    python -m experiments.combinatorial.e30_qbf --calibrate
    python -m experiments.combinatorial.e30_qbf --n 18 --m 51 --timeout 3600
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from e18_gallai import CriticalEncoding, ky_floor, codegree_ceiling  # noqa: E402
from e20_sigma2 import SMSG, SAT, UNSAT, UNKNOWN, verify_model       # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e30"


def write_qcir(n, m, path, colors=5, k4free=True, codeg2=True, maxdeg=True):
    """Emit the 2-QBF: exists edges+aux, forall colours, in QCIR-G14."""
    enc = CriticalEncoding(n, k=colors + 1, k4free=k4free, codeg2=codeg2,
                           gallai_cyc=False, gallai_loc=False,
                           min_edges=m, max_edges=m,
                           maxdeg=((n - 1) // 2) if maxdeg else None,
                           symbreak=False, symbreak_all=False)
    pairs = list(itertools.combinations(range(n), 2))
    for rank, (i, j) in enumerate(pairs):
        assert enc.var(i, j) == rank + 1, "edge-variable order mismatch"

    nv = enc.cnf.nv
    # Universal colour variables come after every existential variable.
    col = {}
    nxt = nv + 1
    for v in range(n):
        for c in range(colors):
            col[(v, c)] = nxt
            nxt += 1
    gate = nxt                      # gate names continue the same numbering

    lines = ["#QCIR-G14"]
    lines.append("exists(" + ", ".join(str(i) for i in range(1, nv + 1)) + ")")
    lines.append("forall(" + ", ".join(str(col[(v, c)]) for v in range(n)
                                       for c in range(colors)) + ")")
    body = []

    def newgate():
        nonlocal gate
        gate += 1
        return gate - 1

    # class(E): one or-gate per clause, then a big and.
    clause_gates = []
    for cl in enc.cnf.clauses:
        g = newgate()
        body.append(f"{g} = or({', '.join(str(l) for l in cl)})")
        clause_gates.append(g)
    class_gate = newgate()
    body.append(f"{class_gate} = and({', '.join(map(str, clause_gates))})")

    # valid(c): every vertex takes exactly one colour.
    valid_parts = []
    for v in range(n):
        alo = newgate()
        body.append(f"{alo} = or({', '.join(str(col[(v, c)]) for c in range(colors))})")
        valid_parts.append(alo)
        for a, b in itertools.combinations(range(colors), 2):
            amo = newgate()
            body.append(f"{amo} = or({-col[(v, a)]}, {-col[(v, b)]})")
            valid_parts.append(amo)
    valid_gate = newgate()
    body.append(f"{valid_gate} = and({', '.join(map(str, valid_parts))})")

    # "c fails on some edge of E": OR over pairs of (edge present AND same colour).
    fail_parts = []
    for (i, j) in pairs:
        same = []
        for c in range(colors):
            g = newgate()
            body.append(f"{g} = and({col[(i, c)]}, {col[(j, c)]})")
            same.append(g)
        sameg = newgate()
        body.append(f"{sameg} = or({', '.join(map(str, same))})")
        conflict = newgate()
        body.append(f"{conflict} = and({enc.var(i, j)}, {sameg})")
        fail_parts.append(conflict)
    fail_gate = newgate()
    body.append(f"{fail_gate} = or({', '.join(map(str, fail_parts))})")

    # The universal player is excused when it plays an invalid colouring.
    excuse = newgate()
    body.append(f"{excuse} = or({-valid_gate}, {fail_gate})")
    out = newgate()
    body.append(f"{out} = and({class_gate}, {excuse})")

    lines.append(f"output({out})")
    lines.extend(body)
    pathlib.Path(path).write_text("\n".join(lines) + "\n")
    return {"vars_exists": nv, "vars_forall": len(col), "gates": gate - nxt,
            "clauses_reused": len(enc.cnf.clauses)}


def run_qbf(n, qcir, timeout=None):
    cmd = [SMSG, "-v", str(n), "--qcir", str(qcir), "--connected"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        # Every branch must return the same keys. The first version omitted
        # tail/models here, so the run CRASHED while reporting a timeout: the
        # verdict was correct and unreadable, which is the worst combination.
        return {"result": UNKNOWN, "seconds": timeout, "why": "timeout",
                "models": [], "cmd": " ".join(cmd), "tail": ["timeout"],
                "returncode": None}
    res = UNKNOWN
    for ln in p.stdout.splitlines():
        if ln.startswith("Result:"):
            res = {"10": SAT, "20": UNSAT}.get(ln.split()[-1], UNKNOWN)
    models = [ln.strip() for ln in p.stdout.splitlines()
              if ln.startswith("[") and ln.strip().endswith("]")]
    if res is UNKNOWN and models:
        res = SAT
    return {"result": res, "seconds": round(time.time() - t0, 2),
            "models": models, "cmd": " ".join(cmd),
            "tail": [t for t in p.stdout.splitlines() if t][-6:],
            "returncode": p.returncode}


def decide(n, m, timeout=None, quiet=False, **kw):
    CACHE.mkdir(parents=True, exist_ok=True)
    tag = f"qbf_n{n}_m{m}"
    qcir = CACHE / f"{tag}.qcir"
    stats = write_qcir(n, m, qcir, **kw)
    r = run_qbf(n, qcir, timeout=timeout)
    out = {"n": n, "m": m, **stats, **{k: r[k] for k in ("result", "seconds")},
           "tail": r["tail"]}
    (CACHE / f"{tag}.json").write_text(json.dumps(out, indent=2))
    if not quiet:
        print(f"  n={n} m={m}: {r['result']} ({r['seconds']}s) "
              f"[{stats['vars_exists']} exists, {stats['vars_forall']} forall, "
              f"{stats['gates']} gates]", flush=True)
    return out


def calibrate(timeout=600):
    """The same ladder E20 passed. The QBF route does not get to speak about n=18
    until it reproduces the orders where the answer is already known."""
    print("E30 calibration: the QBF encoding against known answers", flush=True)
    ok = True
    for n in (15, 16):
        lo, hi = ky_floor(n), codegree_ceiling(n)
        for m in range(lo, hi + 1):
            r = decide(n, m, timeout=timeout, quiet=True)
            good = r["result"] == UNSAT
            ok &= good
            print(f"  [{'ok' if good else 'FAIL'}] n={n} m={m} -> {r['result']} "
                  f"(want UNSAT) in {r['seconds']}s", flush=True)
            if not good:
                print(f"      tail: {r['tail']}", flush=True)
                print("  calibration: FAILURE", flush=True)
                return False
    print(f"calibration: {'ALL PASS' if ok else 'FAILURE'}", flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--m", type=int)
    ap.add_argument("--timeout", type=int, default=None)
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if args.calibrate:
        return 0 if calibrate(timeout=args.timeout or 600) else 1
    if args.n and args.m:
        r = decide(args.n, args.m, timeout=args.timeout)
        return {UNSAT: 0, SAT: 2}.get(r["result"], 1)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
