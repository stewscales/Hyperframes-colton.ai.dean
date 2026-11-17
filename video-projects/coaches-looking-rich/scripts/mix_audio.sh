#!/bin/bash
# Final audio: the voice track only (about -15 LUFS). No music, no added sound effects; the opening is the
# laptop's own closing sound. Usage (from the project folder): bash scripts/mix_audio.sh <talking-head video.mp4> <out base.mp4>
set -e
ffmpeg -nostdin -v error -y -i "$1" -i assets/audio/voice.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart "$2"
