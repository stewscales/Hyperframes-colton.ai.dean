#!/bin/bash
# For each clip: wait for its talking head, mux the voice, render the captioned short, verify it.
# Usage (from the project folder): bash scripts/finish.sh <clip id> ...
set -o pipefail
HF="npx --prefix /home/claude/hyperframes-colton.ai.dean hyperframes"
mkdir -p renders/logs
for id in "$@"; do
  until [ -f clips/$id/edl.json ]; do sleep 5; done
  bash scripts/mux.sh $id || { echo "$id MUX FAILED"; continue; }
  ( cd clips/$id && $HF lint > ../../renders/logs/$id-lint.log 2>&1; grep -E "errors|warnings" ../../renders/logs/$id-lint.log | head -1
    $HF render --quality high --output ../../renders/$id.mp4 > ../../renders/logs/$id-render.log 2>&1 ) || { echo "$id RENDER FAILED"; continue; }
  python3 -I scripts/verify.py $id
done
echo ALL-FINISHED
