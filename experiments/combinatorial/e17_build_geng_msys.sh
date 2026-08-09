#!/usr/bin/env bash
# Windows / msys-ucrt64 variant of e17_build_geng.sh.
#
# Differences from the Linux script: no `make` on this host, so nauty's own
# object files are compiled explicitly here; the ucrt64 gcc is put on PATH first
# so that Git Bash's /mingw64 stubs do not shadow it. Produces the same
# geng_hn binary (WORDSIZE 32, MAXN 32, PRUNE/PREPRUNE = e17_prune).
#
# Usage: bash experiments/combinatorial/e17_build_geng_msys.sh
set -euo pipefail

export PATH="/c/Tools/msys/ucrt64/bin:$PATH"
NAUTY="$HOME/.local/src/nauty2_8_9"
SRC="$(cd "$(dirname "$0")" && pwd)"
OUT="$HOME/.local/bin/geng_hn.exe"
mkdir -p "$HOME/.local/bin"

cd "$NAUTY"
[ -f nauty.h ] || ./configure >/dev/null

# The W1 objects: WORDSIZE 32 / MAXN 32 builds of the nauty core, plus the
# wordsize-independent helpers. Compiled by hand because make is absent.
# AVOID_SYS_WAIT_H: the shipped nauty.h assumes a POSIX host; mingw has no
# <sys/wait.h>. nauty's own header exposes this exact escape hatch.
CF="-O4 -mpopcnt -march=native -I$NAUTY -DMAXN=WORDSIZE -DWORDSIZE=32 -DAVOID_SYS_WAIT_H"
for f in nauty nautil naugraph; do
    [ -f "${f}W1.o" ] || gcc $CF -c -o "${f}W1.o" "${f}.c"
done
[ -f gtoolsW.o ] || gcc $CF -c -o gtoolsW.o gtools.c
[ -f schreier.o ] || gcc -O4 -I"$NAUTY" -c -o schreier.o schreier.c
[ -f naurng.o ] || gcc -O4 -I"$NAUTY" -c -o naurng.o naurng.c

gcc -o "$OUT" $CF -DPRUNE=e17_prune -DPREPRUNE=e17_prune \
    "$NAUTY/geng.c" "$SRC/e17_prune.c" \
    "$NAUTY/gtoolsW.o" "$NAUTY/nautyW1.o" "$NAUTY/nautilW1.o" \
    "$NAUTY/naugraphW1.o" "$NAUTY/schreier.o" "$NAUTY/naurng.o"

# Stock geng too: the calibration gate needs an unpruned reference stream.
gcc -o "$HOME/.local/bin/geng.exe" $CF \
    "$NAUTY/geng.c" \
    "$NAUTY/gtoolsW.o" "$NAUTY/nautyW1.o" "$NAUTY/nautilW1.o" \
    "$NAUTY/naugraphW1.o" "$NAUTY/schreier.o" "$NAUTY/naurng.o"

echo "built $OUT"
