r"""Driver for the two E18 `gold_*` runs (n=13, 14 break-free UNSAT), detachable.

Each run is one long CDCL call with no checkpointing, so the only defense
against environment kills is to run detached from any interactive session (Task
Scheduler) and hold the machine awake (ES_SYSTEM_REQUIRED, scoped to this
process). Runs sequentially: n=13 then n=14. Skips a run whose JSON already
exists.

Usage: python -m experiments.combinatorial.e18_gold_driver
"""
from __future__ import annotations

import ctypes
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "_cache" / "e18"
REPO = HERE.parents[1]
PY = REPO / ".venv" / "Scripts" / "python.exe"

RUNS = [(13, 35), (14, 38)]


def main():
    if os.name == "nt":
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    rc = 0
    for n, floor in RUNS:
        out = CACHE / f"gold_n{n}.json"
        if out.exists():
            print(f"gold n={n}: already done, skipping", flush=True)
            continue
        log = CACHE / f"gold_n{n}.log"
        with open(log, "w") as lf:
            r = subprocess.run(
                [str(PY), "-m", "experiments.combinatorial.e18_sat_class",
                 "--n", str(n), "--min-edges", str(floor), "--out", str(out)],
                cwd=str(REPO), stdout=lf, stderr=subprocess.STDOUT)
        print(f"gold n={n}: exit={r.returncode} json={out.exists()}", flush=True)
        rc = rc or r.returncode
    return rc


if __name__ == "__main__":
    sys.exit(main())
