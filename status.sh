#!/usr/bin/env bash
# One screen of state. Run this instead of asking a model to re-derive it.
#
# Written for token cost: a session that starts by running this spends a few
# hundred tokens getting oriented rather than tens of thousands reading ledgers.
# If the ATTENTION line says nothing is needed, the right move is to walk away.
cd "$(dirname "$0")" || exit 1
C=experiments/combinatorial/_cache

echo "=============================================================="
echo " HADWIGER-NELSON  |  $(date '+%Y-%m-%d %H:%M')"
echo "=============================================================="

if [ -e "$C/STOP" ]; then
    echo
    echo ">>> ATTENTION NEEDED <<<"
    sed 's/^/    /' "$C/STOP"
else
    echo
    echo "ATTENTION: none. The queue is running or idle; nothing needs a human."
fi

echo
echo "-- established ------------------------------------------------"
echo "  chi>=6 both-free class: NONE on n<=17            (L78, theorem)"
echo "  f(6) >= 15: no K4-free 6-chromatic graph n<=14   (L81)"
echo "  56-vertex 4-critical UDG in Q(sqrt3,sqrt35)      (L82, new object)"
echo "  chi(R^2) bounds unmoved: 5 <= chi <= 7"

echo
echo "-- running ----------------------------------------------------"
running=$(pgrep -c smsg 2>/dev/null || echo 0)
echo "  solver processes: $running    load:$(uptime | sed 's/.*load average://')"
for f in "$C"/e25/n18_stuck.json "$C"/e25/n19_stuck.json; do
    [ -f "$f" ] && echo "  $(basename "$f"): $(tr -d '\n ' < "$f" | cut -c1-140)"
done

echo
echo "-- last 5 log lines -------------------------------------------"
[ -f "$C/autorun.log" ] && tail -5 "$C/autorun.log" | sed 's/^/  /' || echo "  (no autorun log yet)"

echo
echo "-- git --------------------------------------------------------"
echo "  $(git log --oneline -1)"
echo "  uncommitted: $(git status --porcelain | wc -l) files"
echo "=============================================================="
