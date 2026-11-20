# Coaches look rich — 4K talking-head reel

One pre-cut take (2160x3840, 30 fps) edited into a captioned reel at the same size and frame rate.

```bash
SRC=/path/to/551B6D1A-3716-4E6C-AFC2-A528C81F74D8.mp4
python3 -I scripts/build.py                                  # cut list, per-frame crop, captions -> index.html + scene.json
PLAYWRIGHT_PATH=/opt/npm-tools/node_modules/playwright node scripts/capture.js /tmp/ov   # caption layer as 2160x3840 PNGs
python3 -I scripts/render.py $SRC /tmp/ov                    # -> renders/coaches-look-rich-4k.mp4 (H.264 High, ~43 Mbps) + assets/base.mp4
```

- `assets/words.json` — word times (wav2vec2 forced alignment of the transcript); `assets/face.json` — face landmarks per source frame.
- The whole edit is at the top of `scripts/build.py`: `SHOTS` (source frames and zoom per shot), `CAPS` (caption chunks, `*key words*`), `CAP_Y`, `EYE_Y`.
- Key words sit on the brand-blue bar rather than in blue type: blue type alone was too dim on the navy tee in a full-frame shot.
- Media (`assets/*.mp4`, `assets/*.wav`, `renders/`) is regenerable and not committed.
