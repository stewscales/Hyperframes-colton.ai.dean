#!/bin/bash
# Build stacked shorts end to end: scene -> capture both graphic layers -> render (picture + voice + sound effects).
# Usage (from the project folder): bash scripts/stack/build.sh <source video> <selfie_segmenter.tflite> <scratch dir> <NN> [...]   e.g. 08
SRC="$1"; SEG="$2"; OV="$3"; shift 3
export PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-/opt/npm-tools/node_modules/playwright}
for n in "$@"; do
  id=$(basename $(ls -d clips/$n-*))
  python3 -I scripts/stack/clip_$n.py || continue
  rm -rf "$OV/ov-$id"; node scripts/stack/capture.js $id "$OV/ov-$id" || continue
  python3 -I scripts/stack/render.py "$SRC" "$SEG" "$OV" $id 2>&1 | grep -v "^W0000\|^INFO\|^$\|absl"
done
