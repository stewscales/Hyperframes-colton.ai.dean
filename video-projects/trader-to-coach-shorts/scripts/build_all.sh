#!/bin/bash
# Build shorts end to end at the source's own 3840x2160: voice -> composition -> caption capture -> 4K render -> verify.
# Usage (from the project folder): bash scripts/build_all.sh <source video> <scratch dir for caption captures> [clip id ...]
# Set SKIP_AUDIO=1 to keep the existing clips/<id>/assets/voice.wav (cut list unchanged).
SRC="$1"; OV="$2"; shift 2
IDS="$@"; [ -z "$IDS" ] && IDS=$(ls clips)
export PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-/opt/npm-tools/node_modules/playwright}
for id in $IDS; do
  [ -n "$SKIP_AUDIO" ] && [ -f clips/$id/assets/voice.wav ] || python3 -I scripts/cut_audio.py "$SRC" $id || continue
  python3 -I scripts/build_comp.py $id > /dev/null
  rm -rf "$OV/ov-$id"; node scripts/capture.js $id "$OV/ov-$id" || continue
  python3 -I scripts/render_4k.py "$SRC" "$OV" $id || continue
  python3 -I scripts/verify.py "$SRC" $id
done
echo BUILD-DONE
