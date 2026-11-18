# Trader to Coach — YouTube edit

4K long-form edit built from the plan doc, adapted to what is actually said in the footage.

- `scripts/align_long.py` — exact word timings for the whole video (`assets/words.json`)
- `scripts/build_overlay.py` — the edit itself: every graphic, punch-in and sound cue, timed from the transcript. Writes `index.html` (Hyperframes composition, 1920x1080 CSS px) and `assets/edit.json`
- `scripts/capture.js` — captures the graphics layer as transparent 4K PNGs (only frames that change)
- `scripts/render.py` / `scripts/render_all.sh` — composites source + punch-ins + graphics to 4K H.264 in 60 s chunks
- `scripts/mix_audio.py` — voice at -14 LUFS plus the quiet sound effects (no music)
- `scripts/preview.sh` — quick check of graphics over the footage without rendering

Not in git (regenerable, too large): the source video, `assets/base-proxy.mp4` (1080p proxy used by `index.html`
for Studio preview: `ffmpeg -i <source> -vf scale=1920:1080 -c:v libx264 -preset veryfast -crf 24 -c:a aac assets/base-proxy.mp4`),
`assets/audio/mix.wav` and everything under `renders/`.

## Thumbnail

`thumbnail/trader-to-coach-thumbnail.jpg` (1280x720). Sources: `frame-4130.png` (source frame 4130, "show up every time"),
`build_cutout.py` (cutout + outline -> `person.png`, needs a MediaPipe selfie-segmenter `.tflite`), `thumbnail.html` (layout),
`render.js` (Playwright render at 2x; downscale to 1280x720 with ffmpeg).
