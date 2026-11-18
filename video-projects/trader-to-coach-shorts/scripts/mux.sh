#!/bin/bash
# Talking head + levelled voice -> clips/<id>/assets/base.mp4 (what the composition plays). Usage: bash scripts/mux.sh <clip id> ...
set -e
for id in "$@"; do
  ffmpeg -nostdin -v error -y -i clips/$id/assets/th.mp4 -i clips/$id/assets/voice.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart clips/$id/assets/base.mp4
  echo "$id base.mp4 $(ffprobe -v error -show_entries format=duration -of csv=p=0 clips/$id/assets/base.mp4)s"
done
