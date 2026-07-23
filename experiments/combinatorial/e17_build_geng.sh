#!/usr/bin/env bash
# Build geng_hn: nauty geng with the E17 both-free PRUNE plugin (e17_prune.c).
# Mirrors the stock `geng` rule in the nauty makefile (W1 = WORDSIZE 32, MAXN 32)
# plus -DPRUNE=e17_prune. Requires the full nauty 2.8.9 source tree with its
# object files already built (they are, at ~/.local/src/nauty2_8_9).
#
# Usage: bash experiments/combinatorial/e17_build_geng.sh
set -euo pipefail

NAUTY="$HOME/.local/src/nauty2_8_9"
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="$HOME/.local/bin/geng_hn"

gcc -o "$OUT" -O4 -mpopcnt -march=native \
    -DMAXN=WORDSIZE -DWORDSIZE=32 -DPRUNE=e17_prune -DPREPRUNE=e17_prune \
    -I"$NAUTY" \
    "$NAUTY/geng.c" "$SRC/e17_prune.c" \
    "$NAUTY/gtoolsW.o" "$NAUTY/nautyW1.o" "$NAUTY/nautilW1.o" \
    "$NAUTY/naugraphW1.o" "$NAUTY/schreier.o" "$NAUTY/naurng.o"

echo "built $OUT"
"$OUT" --help 2>&1 | head -3 || true
