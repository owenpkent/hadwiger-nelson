r"""E25: cube-and-conquer for the cells the ladder cannot swallow whole.

E20's $n=18$ run exposed the limit of the hand-rolled split. Pinning the $t$
highest-indexed vertex pairs to unit clauses is a sound partition, but it is a
BLIND one: it ignores what the solver has learned about which variables matter,
and at $n=18$ the depth-5 branches of the sparse cells were still timing out after
four hours each. Splitting harder was not working because the split was not
splitting the difficulty.

SMS ships the right mechanism natively. `--simple-assignment-cutoff K` runs the
solver (optionally after `--prerun T` seconds of ordinary search) and emits a cube
whenever $K$ edge variables are assigned, so the partition is cut along the
solver's own decision structure; `--cube-file F --cube-line L` then solves cube
$L$ in isolation. This is Heule's cube-and-conquer, and the cutoff is a dial that
trades cube count against per-cube difficulty:

    n=18, m=53:  cutoff 40 -> 3 cubes    cutoff 55 -> 33 cubes    cutoff 70 -> 544

Sampled per-cube solve times at cutoff 70 on that cell were 0.11, 0.71, 0.77,
1.01 and 41.86 seconds, against a whole-cell budget of four hours that did not
finish.

THE VERDICT SIGNAL NEEDS CARE, which is the reason this module exists rather than
a flag on E20. A whole-cell run ends with `Result: 20` for UNSAT; a cube run ends
with `All cubes processed` and prints nothing else when the cube is refuted. So
"no model was printed" carries the verdict, and a silent failure (crash, timeout,
bad cube index) would look exactly like UNSAT unless it is checked for. Hence:

  * a cube is UNSAT only if the process exits 0 AND prints the completion line AND
    prints no model;
  * anything else is UNKNOWN, never UNSAT;
  * `--calibrate` demands that the machinery reproduce known answers in BOTH
    directions before it is trusted, including a POSITIVE control where the cubes
    must find a model (the ablated cell of E20, class properties removed, which is
    known satisfiable). Without that rung, a bug that makes every cube silently
    report nothing would read as a clean UNSAT.

Usage:
    python -m experiments.combinatorial.e25_cube --calibrate
    python -m experiments.combinatorial.e25_cube --n 18 --m 53 --cutoff 70 --jobs 7
"""
from __future__ import annotations

import argparse
import ast
import concurrent.futures as futures
import json
import os
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from e20_sigma2 import (build_class_cnf, verify_model, SMSG,   # noqa: E402
                        SAT, UNSAT, UNKNOWN)

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e25"
DONE_LINE = "All cubes processed"


def generate_cubes(n, cnf, cube_path, cutoff, prerun, chi=6, timeout=None):
    cmd = [SMSG, "-v", str(n), "--dimacs", str(cnf),
           "--min-chromatic-number", str(chi), "--connected",
           "--simple-assignment-cutoff", str(cutoff),
           "--prerun", str(prerun), "--cube-only-decisions"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    cubes = [ln for ln in p.stdout.splitlines() if ln.startswith("a ")]
    # A cube phase that solves the cell outright emits a model instead.
    models = [ln.strip() for ln in p.stdout.splitlines()
              if ln.startswith("[") and ln.strip().endswith("]")]
    pathlib.Path(cube_path).write_text("\n".join(cubes) + ("\n" if cubes else ""))
    return {"cubes": len(cubes), "models": models,
            "seconds": round(time.time() - t0, 1), "cmd": " ".join(cmd)}


def solve_cube(n, cnf, cube_path, line, chi=6, timeout=None):
    cmd = [SMSG, "-v", str(n), "--dimacs", str(cnf),
           "--min-chromatic-number", str(chi), "--connected",
           "--cube-file", str(cube_path), "--cube-line", str(line)]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"line": line, "result": UNKNOWN, "seconds": timeout,
                "why": "timeout"}
    out = p.stdout
    models = [ln.strip() for ln in out.splitlines()
              if ln.startswith("[") and ln.strip().endswith("]")]
    dt = round(time.time() - t0, 2)
    if models:
        return {"line": line, "result": SAT, "seconds": dt,
                "model": ast.literal_eval(models[-1])}
    if p.returncode == 0 and DONE_LINE in out:
        return {"line": line, "result": UNSAT, "seconds": dt}
    return {"line": line, "result": UNKNOWN, "seconds": dt,
            "why": f"rc={p.returncode}, no completion line",
            "tail": out.splitlines()[-4:]}


def decide(n, m, chi=6, cutoff=70, prerun=45, jobs=7, timeout=None,
           k4free=True, codeg2=True, quiet=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    abl = ("" if k4free else "_nok4") + ("" if codeg2 else "_nocodeg")
    tag = f"n{n}_m{m}_chi{chi}{abl}_c{cutoff}"
    cnf = CACHE / f"{tag}.cnf"
    build_class_cnf(n, m, cnf, k4free=k4free, codeg2=codeg2)
    cube_path = CACHE / f"{tag}.cubes"

    gen = generate_cubes(n, cnf, cube_path, cutoff, prerun, chi=chi)
    if gen["models"]:                       # cubing phase already found one
        edges = ast.literal_eval(gen["models"][-1])
        hit = verify_model(n, edges, chi, m=m, class_member=k4free and codeg2)
        out = {"n": n, "m": m, "result": SAT, "found_during_cubing": True,
               "hit": hit, "cubes": gen["cubes"], "elapsed_s": gen["seconds"]}
        (CACHE / f"{tag}.json").write_text(json.dumps(out, indent=2))
        return out
    if gen["cubes"] == 0:
        out = {"n": n, "m": m, "result": UNKNOWN, "cubes": 0,
               "why": "cubing produced neither cubes nor a model",
               "elapsed_s": gen["seconds"]}
        (CACHE / f"{tag}.json").write_text(json.dumps(out, indent=2))
        return out

    t0 = time.time()
    with futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        res = list(ex.map(lambda L: solve_cube(n, cnf, cube_path, L, chi, timeout),
                          range(1, gen["cubes"] + 1)))
    hits = [r for r in res if r["result"] == SAT]
    unk = [r for r in res if r["result"] == UNKNOWN]
    verdict = SAT if hits else (UNKNOWN if unk else UNSAT)
    out = {"n": n, "m": m, "chi": chi, "cutoff": cutoff, "cubes": gen["cubes"],
           "cubing_s": gen["seconds"], "solve_wall_s": round(time.time() - t0, 1),
           "solve_cpu_s": round(sum(r["seconds"] for r in res), 1),
           "result": verdict, "unknown_cubes": [r["line"] for r in unk],
           "max_cube_s": max((r["seconds"] for r in res), default=0)}
    if hits:
        out["hit"] = verify_model(n, hits[0]["model"], chi, m=m,
                                  class_member=k4free and codeg2)
    (CACHE / f"{tag}.json").write_text(json.dumps(out, indent=2))
    if not quiet:
        print(f"  n={n} m={m}: {verdict} via {gen['cubes']} cubes "
              f"[cubing {gen['cubing_s'] if 'cubing_s' in gen else gen['seconds']}s, "
              f"solve {out['solve_wall_s']}s wall / {out['solve_cpu_s']}s cpu, "
              f"slowest cube {out['max_cube_s']}s]", flush=True)
    return out


def calibrate(jobs=7):
    """Both directions, on cells whose answers are already established."""
    print("E25 calibration: cube-and-conquer against known answers", flush=True)
    ok = True

    r = decide(17, 52, cutoff=60, prerun=20, jobs=jobs, quiet=True)
    good = r["result"] == UNSAT
    ok &= good
    print(f"  [{'ok' if good else 'FAIL'}] n=17 m=52 -> {r['result']} "
          f"(want UNSAT, whole-cell baseline 13.3s): {r.get('cubes')} cubes, "
          f"{r.get('solve_cpu_s')}s cpu", flush=True)

    r = decide(16, 44, cutoff=55, prerun=20, jobs=jobs, quiet=True)
    good = r["result"] == UNSAT
    ok &= good
    print(f"  [{'ok' if good else 'FAIL'}] n=16 m=44 -> {r['result']} "
          f"(want UNSAT, whole-cell baseline 24.2s): {r.get('cubes')} cubes, "
          f"{r.get('solve_cpu_s')}s cpu", flush=True)

    # POSITIVE CONTROL: the ablated cell, known satisfiable (E20 ablation found a
    # verified chi>=6 model in 409s). If the cube path cannot find it, every UNSAT
    # above is suspect.
    r = decide(17, 52, cutoff=60, prerun=20, jobs=jobs, quiet=True,
               k4free=False, codeg2=False)
    good = r["result"] == SAT and (r.get("hit") or {}).get("chi_ge")
    ok &= good
    print(f"  [{'ok' if good else 'FAIL'}] n=17 m=52 ablated -> {r['result']} "
          f"(want SAT; independently chi>=6: "
          f"{(r.get('hit') or {}).get('chi_ge')})", flush=True)

    print(f"calibration: {'ALL PASS' if ok else 'FAILURE'}", flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--n", type=int)
    ap.add_argument("--m", type=int)
    ap.add_argument("--chi", type=int, default=6)
    ap.add_argument("--cutoff", type=int, default=70)
    ap.add_argument("--prerun", type=int, default=45)
    ap.add_argument("--jobs", type=int, default=7)
    ap.add_argument("--timeout", type=int, default=None)
    args = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if args.calibrate:
        return 0 if calibrate(jobs=args.jobs) else 1
    if args.n and args.m:
        r = decide(args.n, args.m, chi=args.chi, cutoff=args.cutoff,
                   prerun=args.prerun, jobs=args.jobs, timeout=args.timeout)
        return {UNSAT: 0, SAT: 2}.get(r["result"], 1)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
