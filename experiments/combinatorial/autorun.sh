#!/usr/bin/env bash
# Model-free autonomous runner for the combinatorial thread.
#
# The point of this file is TOKEN COST. Everything below runs on cron with no
# model in the loop, so the machine can work for days at zero cost. A model is
# worth invoking only when a decision is genuinely needed, and the script signals
# exactly that by writing STOP with a reason. Until STOP exists, there is nothing
# for a human or a model to do.
#
# Work queue, in order. Each step is skipped if already done (its ledger records
# the verdict), so re-running is free and a kill costs only the in-flight step.
#   1. the five stuck n=18 cells, via cube-and-conquer (e25_n18_stuck.py)
#   2. n=19, if and only if n=18 closed completely
#
# Stop conditions, all of which write STOP and halt the queue:
#   HIT    a chi>=6 member was found and independently verified. This is the
#          result the whole program is for; it must not be buried in a log.
#   WALL   a step could not close even with cube-and-conquer.
#   GATE   a calibration gate failed, meaning nothing downstream is trustworthy.
#
# Cron re-arms this every 15 minutes; flock keeps it single-instance.
set -uo pipefail

REPO=/home/owen/dev/hadwiger-nelson
CACHE="$REPO/experiments/combinatorial/_cache"
LOG="$CACHE/autorun.log"
LOCK="$CACHE/.autorun.lock"
STOP="$CACHE/STOP"
PY="$REPO/.venv/bin/python"

mkdir -p "$CACHE"
cd "$REPO" || exit 1
export PATH="$HOME/.local/bin:$PATH"

[ -e "$STOP" ] && exit 0

say() { echo "[$(date -Is)] $*" >> "$LOG"; }
halt() { echo "$1" > "$STOP"; say "HALT: $1"; exit "${2:-0}"; }

(
    flock -n 9 || exit 0

    # Step 0: the calibration gate, enforced by the machine rather than by me.
    # Production never runs on an uncalibrated tool. If the gate has not passed,
    # run it; if it fails, halt with GATE so a human sees it instead of a pile of
    # untrustworthy UNSATs.
    if [ ! -f "$CACHE/e25/gate_passed" ]; then
        if grep -q "ALL PASS" "$CACHE/e25/calib3.log" 2>/dev/null; then
            touch "$CACHE/e25/gate_passed"; say "gate: PASS (existing run)"
        elif grep -q "FAILURE" "$CACHE/e25/calib3.log" 2>/dev/null; then
            halt "GATE FAILED: e25_cube calibration did not pass. Nothing
downstream is trustworthy. See _cache/e25/calib3.log; the positive control is the
rung that matters (it proves the cube path can return SAT where a model exists)." 1
        elif pgrep -f "e25_cube --calibrate" >/dev/null; then
            say "gate: calibration still running, waiting"; exit 0
        else
            say "gate: no verdict on record, running calibration"
            $PY -m experiments.combinatorial.e25_cube --calibrate --jobs 7 \
                > "$CACHE/e25/calib3.log" 2>&1
            grep -q "ALL PASS" "$CACHE/e25/calib3.log" \
                && { touch "$CACHE/e25/gate_passed"; say "gate: PASS"; } \
                || halt "GATE FAILED: see _cache/e25/calib3.log." 1
        fi
    fi

    # Step 1: the stuck n=18 cells.
    if [ ! -f "$CACHE/e25/n18_done" ]; then
        say "step 1: n=18 stuck cells via cube-and-conquer"
        $PY -m experiments.combinatorial.e25_n18_stuck --jobs 7 >> "$LOG" 2>&1
        rc=$?
        case $rc in
            0) touch "$CACHE/e25/n18_done"; say "n=18 COMPLETE (all cells UNSAT)" ;;
            2) halt "HIT: a chi>=6 both-free graph was found at n=18. See
_cache/e25/n18_stuck.json and the run log. This is the result the program exists
to find; verify it independently before anything else." 2 ;;
            *) halt "WALL at n=18: cube-and-conquer left cells undecided. See
_cache/e25/n18_stuck.json for which cubes timed out. n<=17 is unaffected." 1 ;;
        esac
    fi

    # Step 2: n=19, only once n=18 is genuinely closed.
    if [ -f "$CACHE/e25/n18_done" ] && [ ! -f "$CACHE/e25/n19_done" ]; then
        say "step 2: n=19"
        $PY -m experiments.combinatorial.e25_n18_stuck --n 19 \
            --cells 52,53,54,55,56,57,58,59,60 --jobs 7 >> "$LOG" 2>&1
        rc=$?
        case $rc in
            0) touch "$CACHE/e25/n19_done"; say "n=19 COMPLETE" ;;
            2) halt "HIT at n=19. See _cache/e25/n19_stuck.json." 2 ;;
            *) halt "WALL at n=19. n<=18 stands." 1 ;;
        esac
    fi

    say "queue idle: nothing left that does not need a decision"
) 9>"$LOCK"
