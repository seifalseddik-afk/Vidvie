#!/usr/bin/env bash
# Trace every cut-out letter form (traced/*.png) to SVG with VectorCraft's Image Trace.
set -euo pipefail
VC=${VECTORCRAFT_CLI:-vectorcraft-cli}
cd "$(dirname "$0")/traced"
for png in *.png; do
  "$VC" run --in "$png" --cmd select.all --cmd imageTrace.makeAndExpand \
     --params '{"preset":"Black and White Logo"}' --export "${png%.png}.svg" >/dev/null
done
echo "traced $(ls *.svg | wc -l) forms"
