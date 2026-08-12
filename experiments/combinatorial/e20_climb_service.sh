#!/usr/bin/env bash
# Always-on driver for the E20 ladder (see e20_sigma2.py --climb).
#
# Safe to invoke from cron on any schedule and at boot: `flock -n` guarantees at
# most one instance, so a re-arm while the ladder is mid-cell is a no-op. The
# ladder itself is resumable at cell granularity, so a kill or a reboot costs
# only the in-flight cells.
#
# It STOPS being re-armed once the ladder reports something a human should read:
# exit 2 (a chi>=6 hit) or exit 1 (a cell that survives even the 32-way split).
# Both write STOP, and the wrapper refuses to run while STOP exists. Clear it by
# deleting the file after acting on what it says.
set -uo pipefail

REPO=/home/owen/dev/hadwiger-nelson
CACHE="$REPO/experiments/combinatorial/_cache/e20"
LOG="$CACHE/climb.log"
LOCK="$CACHE/.climb.lock"
STOP="$CACHE/STOP"
FROM="${1:-18}"

mkdir -p "$CACHE"
cd "$REPO" || exit 1
export PATH="$HOME/.local/bin:$PATH"

if [ -e "$STOP" ]; then
    exit 0
fi

(
    flock -n 9 || exit 0
    echo "=== climb from n=$FROM started $(date -Is) ===" >> "$LOG"
    "$REPO/.venv/bin/python" -m experiments.combinatorial.e20_sigma2 \
        --climb "$FROM" --jobs 7 --timeout 1800 --split-bits 5 --probe >> "$LOG" 2>&1
    rc=$?
    echo "=== climb exited rc=$rc at $(date -Is) ===" >> "$LOG"
    case $rc in
        2) echo "HIT: a chi>=6 both-free graph was found. See climb.json." > "$STOP" ;;
        1) echo "WALL: a cell survived the 32-way split. See climb.json." > "$STOP" ;;
    esac
) 9>"$LOCK"
