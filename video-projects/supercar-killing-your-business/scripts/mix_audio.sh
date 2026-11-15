#!/bin/bash
# Final audio mix: voice (about -15 LUFS) + quiet music bed (about 21 dB under the voice) + a few low SFX on the cuts.
# The music drops out for a beat on the rehook ("Your prospects don't care", 9.35-10.05 s).
# SFX times follow timeline.py: B-roll in at frames 61 / 222 / 442, follow pill at 639.
# Usage (from the project folder): bash scripts/mix_audio.sh <talking-head video.mp4> <out base.mp4>
set -e
A=assets/audio; DUR=22.9
ffmpeg -nostdin -v error -y \
  -i $A/voice.wav -ss 21.0 -t $DUR -i $A/music-bed-cinematic-tech.mp3 \
  -i $A/bass-drop.mp3 -i $A/whoosh.mp3 -i $A/swipe.mp3 -i $A/click.wav -i $A/whoosh.mp3 -i $A/pop.mp3 \
  -filter_complex "
   [0:a]aresample=48000,apad=whole_dur=$DUR[v];
   [1:a]aresample=48000,highpass=f=60,volume=-24dB,volume=eval=frame:volume='clip((abs(t-9.70)-0.35)/0.15\,0\,1)',afade=t=in:d=0.15,afade=t=out:st=22.0:d=0.9[m];
   [2:a]aresample=48000,volume=-19dB,adelay=0|0[s0];
   [3:a]aresample=48000,volume=-18dB,adelay=1930|1930[s1];
   [4:a]aresample=48000,volume=-18dB,adelay=7250|7250[s2];
   [6:a]aresample=48000,volume=-18dB,adelay=14630|14630[s4];
   [7:a]aresample=48000,volume=-22dB,adelay=21300|21300[s5];
   [v][m][s0][s1][s2][s4][s5]amix=inputs=7:normalize=0:duration=first,alimiter=limit=0.89:level=false,atrim=end=$DUR[o]" \
  -map "[o]" -ar 48000 -c:a pcm_s24le $A/mix.wav
ffmpeg -nostdin -v error -y -i "$1" -i $A/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart "$2"
