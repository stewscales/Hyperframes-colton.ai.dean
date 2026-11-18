#!/bin/bash
# Full 4K render in 60-second chunks (so a fix only re-renders the chunks it touches), then join and add the audio.
#   bash scripts/render_all.sh <source.mp4> <overlay_dir> <audio.wav> <out.mp4> [chunk numbers to (re)render...]
set -eo pipefail
SRC="$1"; OV="$2"; AUD="$3"; OUT="$4"; shift 4
NF=15871; STEP=1800; START=12   # START: first source frame used (see assets/edit.json)
mkdir -p renders/chunks
N=$(( (NF + STEP - 1) / STEP ))
for i in $(seq 0 $((N - 1))); do
  if [ $# -gt 0 ] && ! [[ " $* " == *" $i "* ]]; then continue; fi
  a=$((i * STEP)); b=$((a + STEP)); [ $b -gt $NF ] && b=$NF; [ $a -lt $START ] && a=$START
  python3 -I scripts/render.py "$SRC" "$OV" $a $b renders/chunks/c$(printf "%02d" $i).mp4 --crf 20 --preset fast | tail -1
done
ls renders/chunks/c*.mp4 | sed "s#renders/chunks/#file '#; s#\$#'#" > renders/chunks/list.txt
ffmpeg -nostdin -v error -y -f concat -safe 0 -i renders/chunks/list.txt -i "$AUD" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -movflags +faststart "$OUT"
