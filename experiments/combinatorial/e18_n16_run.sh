#!/usr/bin/env bash
# The n=16 cell, enumerated twice by two different technologies.
#
#   geng_hn  : canonical augmentation (E17's method), 32-way res/mod split. This
#              is the toolchain replication -- same algorithm, different OS and
#              compiler than the L75 run, which recorded 11,315 graphs / 66 cpu-h.
#   e18      : CDCL + blocking clauses + external isomorph rejection, one job per
#              edge count m in the window 43..48. This is the INDEPENDENT second
#              enumerator that L75 caveat (i) asks for.
#
# The two answers are compared class-by-class by e18_n16_compare.py.
set -u
PY=/c/Users/Owen/dev/hadwiger-nelson/.venv/Scripts/python.exe
export PATH="$HOME/.local/bin:$PATH"
cd /c/Users/Owen/dev/hadwiger-nelson
O=experiments/combinatorial/_cache/e18
mkdir -p "$O"

# --- geng side (fast: the L75 run took 66 cpu-h, spread here over 32 cores) ---
for r in $(seq 0 31); do
    ( geng_hn -Cq -d5 -D7 16 43:48 $r/32 > "$O/n16_geng_$r.g6" 2>/dev/null ) &
done

# --- SAT side, one job per edge count ---
for m in 43 44 45 46 47 48; do
    ( $PY -m experiments.combinatorial.e18_enumerate --n 16 --m $m \
        --budget 4000000 --out "$O/enum_n16_m$m.json" \
        > "$O/enum_n16_m$m.log" 2>&1
      echo "exit=$? $(date -Is)" >> "$O/enum_n16_m$m.log" ) &
done

wait
cat "$O"/n16_geng_*.g6 > "$O/n16_geng_all.g6"
echo "geng n=16 total: $(wc -l < "$O/n16_geng_all.g6")"
echo "n16 battery done $(date -Is)"
