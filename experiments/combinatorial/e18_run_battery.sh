#!/usr/bin/env bash
# E18 overnight battery. Four emptiness decisions plus the symmetry-break
# soundness gate, all in parallel (this host has 32 logical cores).
#
#   gold_n   : no symmetry breaking at all -> the UNSAT answer needs no argument
#              about the break being sound. Slow.
#   sym_n    : lex-leader under adjacent transpositions, DRAT emitted. Fast.
#   satgate_n: orders where the class is KNOWN nonempty; the symmetry-broken
#              encoding must still return SAT there, or the break is over-
#              constraining and every sym_* UNSAT is worthless.
set -u
PY=/c/Users/Owen/dev/hadwiger-nelson/.venv/Scripts/python.exe
cd /c/Users/Owen/dev/hadwiger-nelson
OUT=experiments/combinatorial/_cache/e18
mkdir -p "$OUT"

run () {  # name, extra args...
    local name="$1"; shift
    ( $PY -m experiments.combinatorial.e18_sat_class "$@" \
        --out "$OUT/$name.json" > "$OUT/$name.log" 2>&1
      echo "exit=$? $(date -Is)" >> "$OUT/$name.log" ) &
}

# Kostochka-Yancey floor m >= ceil((28n-18)/10): 13 -> 35, 14 -> 38, 15 -> 41, 16 -> 43.
run gold_n13    --n 13 --min-edges 35
run gold_n14    --n 14 --min-edges 38
run sym_n13     --n 13 --min-edges 35 --symbreak --proof "$OUT/sym_n13.drat"
run sym_n14     --n 14 --min-edges 38 --symbreak --proof "$OUT/sym_n14.drat"

# Symmetry-break soundness gate: these MUST come back SAT.
run satgate_n12 --n 12 --symbreak
run satgate_n15 --n 15 --min-edges 41 --symbreak
run satgate_n16 --n 16 --min-edges 43 --symbreak

wait
echo "battery done $(date -Is)"
