r"""E19 branch driver for the dominant n=17 cell (m=46), built to be RESUMABLE.

The m=46 cell is >1.15M classes (measured before two environment kills lost the
unsplit runs), so it must not live or die as one process. This driver splits the
cell 64 ways on the six highest-indexed vertex pairs (`--split 6:idx`, unit
clauses; a sound exact partition of the model space -- each class's lex-minimal
labelling has definite values on the pinned pairs, so every class is emitted by
exactly the branch containing its minimal labelling), runs branches in a small
process pool, and SKIPS any branch whose summary JSON already reports
EXHAUSTED. Killing this driver at any moment therefore loses only the in-flight
branches, and re-running it resumes where it left off.

It also asserts ES_SYSTEM_REQUIRED so Modern Standby does not freeze the
machine mid-run (scoped: released when this process exits).

Usage: python -m experiments.combinatorial.e19_m46_branches [--jobs 8]
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e19"
REPO = HERE.parents[1]
PY = REPO / ".venv" / "Scripts" / "python.exe"

M = 46
SPLIT_BITS = 6


def branch_done(idx):
    p = CACHE / f"sms_n17_m{M}_s{SPLIT_BITS}_{idx}.json"
    if not p.exists():
        return False
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError:
        return False
    return bool(d.get("exhausted")) and d.get("property_violations") == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    if os.name == "nt":
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

    todo = [i for i in range(2 ** SPLIT_BITS) if not branch_done(i)]
    print(f"m={M}: {2 ** SPLIT_BITS - len(todo)} branches already done, "
          f"{len(todo)} to run, {args.jobs} at a time", flush=True)

    running = {}
    t0 = time.time()
    while todo or running:
        while todo and len(running) < args.jobs:
            idx = todo.pop(0)
            log = open(CACHE / f"run_m{M}_s{idx}.log", "w")
            p = subprocess.Popen(
                [str(PY), "-m", "experiments.combinatorial.e19_sms_n17",
                 "--m", str(M), "--split", f"{SPLIT_BITS}:{idx}"],
                cwd=str(REPO), stdout=log, stderr=subprocess.STDOUT)
            running[idx] = (p, log)
        time.sleep(10)
        for idx in list(running):
            p, log = running[idx]
            if p.poll() is not None:
                log.close()
                ok = branch_done(idx)
                print(f"  branch {idx}: exit={p.returncode} done={ok} "
                      f"({time.time() - t0:.0f}s elapsed)", flush=True)
                del running[idx]
                if not ok and p.returncode != 0:
                    print(f"  branch {idx} FAILED; will need a re-run", flush=True)

    done = sum(branch_done(i) for i in range(2 ** SPLIT_BITS))
    hits = []
    tot_models = tot_dsatur = tot_sat = 0
    for i in range(2 ** SPLIT_BITS):
        p = CACHE / f"sms_n17_m{M}_s{SPLIT_BITS}_{i}.json"
        if p.exists():
            d = json.loads(p.read_text())
            tot_models += d.get("models", 0)
            tot_dsatur += d.get("dsatur_ok", 0)
            tot_sat += d.get("sat_ok", 0)
            if d.get("hits"):
                hits.append(i)
    complete = done == 2 ** SPLIT_BITS
    summary = {
        "m": M, "branches_done": done, "branches_total": 2 ** SPLIT_BITS,
        "complete": complete, "models": tot_models,
        "dsatur_ok": tot_dsatur, "sat_ok": tot_sat,
        "branches_with_hits": hits, "elapsed_s": round(time.time() - t0, 1),
    }
    (CACHE / f"m{M}_branch_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)
    return 0 if complete and not hits else 1


if __name__ == "__main__":
    sys.exit(main())
