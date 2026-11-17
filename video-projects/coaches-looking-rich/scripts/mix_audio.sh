#!/bin/bash
# Final mix: voice (about -15 LUFS) + quiet music bed (about 21 dB under the voice). No added sound effects:
# the opening is the laptop's own closing sound on its own, and the music comes in on that sound (0.767 s).
# Usage (from the project folder): bash scripts/mix_audio.sh <talking-head video.mp4> <out base.mp4>
set -e
A=assets/audio; DUR=13.433333
ffmpeg -nostdin -v error -y -i $A/voice.wav -ss 21.0 -t 12.7 -i $A/music-bed-cinematic-tech.mp3 \
  -filter_complex "
   [0:a]aresample=48000,apad=whole_dur=$DUR[v];
   [1:a]aresample=48000,highpass=f=60,volume=-24dB,afade=t=in:d=0.04,afade=t=out:st=11.6:d=1.05,adelay=767|767[m];
   [v][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=false,atrim=end=$DUR[o]" \
  -map "[o]" -ar 48000 -c:a pcm_s24le $A/mix.wav
ffmpeg -nostdin -v error -y -i "$1" -i $A/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart "$2"
