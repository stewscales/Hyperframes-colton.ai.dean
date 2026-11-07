#!/usr/bin/env bash
# Hook -> buildup -> footage, 0.1s crossfades at each join. Run from the project folder.
# Hook: 0-5.2s. Buildup: picture to 2.967s (before hand covers lens), last frame held
# while the final "s" of "formats" plays (audio to 3.133s). Footage: 1.067-11.0s (drops
# the phone-handling at the start and the reach at the end).
set -e
ffmpeg -nostdin -v error -y -i assets/1-hook.mp4 -i assets/2-buildup.mp4 -i assets/3-footage.mp4 -filter_complex "
[0:v]trim=start=0:end=5.2,setpts=PTS-STARTPTS,settb=1/30[h];
[1:v]trim=start=0:end=2.966667,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop=5,settb=1/30[b];
[2:v]trim=start=1.066667:end=11.0,setpts=PTS-STARTPTS,settb=1/30[f];
[h][b]xfade=transition=fade:duration=0.1:offset=5.1[hb0];[hb0]settb=1/30[hb];
[hb][f]xfade=transition=fade:duration=0.1:offset=8.133333[v];
[0:a]atrim=start=0:end=5.1,asetpts=PTS-STARTPTS,afade=t=out:st=5.085:d=0.015[ha];
[1:a]atrim=start=0:end=3.133333,asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=3.118:d=0.015[ba];
[2:a]atrim=start=1.066667:end=11.0,asetpts=PTS-STARTPTS,afade=t=out:st=9.9:d=0.033[fa];
[ha][ba]concat=n=2:v=0:a=1[hba];
[hba][fa]acrossfade=d=0.1:c1=nofade:c2=tri[a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart renders/hook-buildup-footage-v1.mp4
