# Two offers — talking-head reel with two B-roll inserts and two text cards

1080x1920 / 30 fps, cut from one phone take (92E79A12-…mp4) with the desk/filming clip (IMG_3216) and the night drive (IMG_3255).
Same house style, look and sound as `../better-trader-reel/`.

```bash
TH=/path/to/92E79A12-8BEF-4452-8C9C-39BFB0399CA3.mp4
ffmpeg -i $TH -ac 1 -ar 16000 /tmp/th16.wav
python3 -I scripts/build.py /tmp/th16.wav               # cut list, punch-ins, B-roll spans, cards, captions -> index.html + scene.json
PLAYWRIGHT_PATH=/opt/npm-tools/node_modules/playwright node scripts/capture.js /tmp/ov
python3 -I scripts/render.py $TH IMG_3216.mov IMG_3255.mov /tmp/ov     # -> renders/two-offers.mp4   (--no-music for voice only)
```

- Captions are what he says (confirmed with him where the speech tools disagreed: "for trading coaches", "the same mistake with content", "want to be part of your own world").
- He sits lower in frame in this take than in better-trader, so the caption line is 16 px lower (1526).
