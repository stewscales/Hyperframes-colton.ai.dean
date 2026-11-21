# Coaches look rich — v2 (premium edit)

The same pre-cut take as `../coaches-look-rich-4k/` (2160x3840, 30 fps), re-edited: tighter pauses, two no-time cut-ins,
eased punch-ins on the key lines, a light grade, cleaned-up voice, bone-white captions with blue key words.
Output 1440x2560 / 30 fps / H.264 High: every output pixel comes from the camera (the tightest crop is 1624 px wide).

```bash
SRC=/path/to/551B6D1A-3716-4E6C-AFC2-A528C81F74D8.mp4
python3 -I scripts/build.py                                  # cut list, camera, captions -> index.html + scene.json
PLAYWRIGHT_PATH=/opt/npm-tools/node_modules/playwright node scripts/capture.js /tmp/ov   # caption layer at 1440x2560
python3 -I scripts/render.py $SRC /tmp/ov                    # -> renders/coaches-look-rich-v2.mp4
python3 -I scripts/render.py $SRC /tmp/ov --still 0,200      # just a few graded stills (renders/still-*.png), for checking the look
python3 -I scripts/render.py $SRC /tmp/ov --audio-only 1     # keep the picture, redo the sound
```

- The edit lives at the top of `scripts/build.py` (`SHOTS`, the zoom per shot, `CAPS`); the look and the sound at the top of `scripts/render.py`.
- No music: the voice carries it; the music library has one cinematic bed, which fights a 12-second spoken reel.
