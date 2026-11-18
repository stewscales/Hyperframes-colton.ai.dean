#!/bin/bash
# Full rebuild of one or more clips after an edit in scripts/clips.py: voice -> talking head -> composition -> render -> verify.
# Usage (from the project folder): bash scripts/rebuild.sh <source video> <facelm.task> <clip id> ...
SRC="$1"; LM="$2"; shift 2
for id in "$@"; do
  python3 -I scripts/cut_audio.py "$SRC" $id || continue
  rm -f clips/$id/edl.json renders/$id.mp4
  python3 -I scripts/render_th.py "$SRC" "$LM" $id 2>&1 | grep -v "^W0000\|^INFO\|^$\|absl"
  python3 -I scripts/build_comp.py $id
  bash scripts/finish.sh $id | grep -v ALL-FINISHED
done
echo REBUILD-DONE
