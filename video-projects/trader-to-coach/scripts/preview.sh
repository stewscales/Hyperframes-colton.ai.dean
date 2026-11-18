#!/bin/bash
# Check graphics against the footage without rendering: bash scripts/preview.sh <source.mp4> <out.jpg> <cols> f1 f2 ...
# Captures the graphics at each frame (1080p), lays them over the matching source frame, and tiles the results.
set -e
SRC="$1"; OUT="$2"; COLS="$3"; shift 3
D=$(mktemp -d); LIST=$(echo "$@" | tr ' ' ',')
node scripts/capture.js "$LIST" "$D" 1 > /dev/null
i=0
for f in "$@"; do
  p=$(printf "%05d" $f); t=$(python3 -c "print(max(0,$f/30-0.01))")
  ffmpeg -nostdin -v error -y -ss $t -i "$SRC" -i "$D/f$p.png" -filter_complex "[0:v]scale=1920:1080[b];[b][1:v]overlay,scale=${TILE_W:-640}:-2,drawtext=text='$f':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black" -frames:v 1 -q:v 2 "$D/c$(printf "%03d" $i).jpg"
  i=$((i+1))
done
ROWS=$(( (i + COLS - 1) / COLS ))
ffmpeg -nostdin -v error -y -pattern_type glob -i "$D/c*.jpg" -vf "tile=${COLS}x${ROWS}" -frames:v 1 -q:v 2 "$OUT"
rm -rf "$D"
