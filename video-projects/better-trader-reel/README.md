# Better trader — talking-head reel with two B-roll inserts

1080x1920 / 30 fps, cut from one phone take (81102175-…mp4) with a sales-call photo and a 2-second filming clip.

```bash
TH=/path/to/81102175-04FF-4EC0-AE04-B19A925A1C23.mp4
ffmpeg -i $TH -ac 1 -ar 16000 assets/th16.wav             # (not committed) the level map the cut uses
python3 -I scripts/build.py                               # cut list, punch-ins, B-roll spans, captions -> index.html + scene.json
PLAYWRIGHT_PATH=/opt/npm-tools/node_modules/playwright node scripts/capture.js /tmp/ov
python3 -I scripts/render.py $TH sales-photo.jpg IMG_3197.mov /tmp/ov            # -> renders/better-trader.mp4
python3 -I scripts/render.py $TH sales-photo.jpg IMG_3197.mov /tmp/ov --no-music # voice only
```

- Word times: wav2vec2 forced alignment of what he says (not the script where it differs: "than you are", "Just think about that", "that mate").
- Captions: bone white, key words blue, five emphasis lines in blue caps; the line sits just below his chin (punch-ins are anchored at the bottom of the frame so his chin rises away from it).
