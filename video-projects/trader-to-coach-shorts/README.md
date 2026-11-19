# Trader to Coach — shorts (Instagram / TikTok)

Eight shorts cut from the clean 4K long-form recording (`Trader_to_Coach_-_full_video_FINAL.mp4`, the same source as
`../trader-to-coach/`). Each one is assembled from snippets of the long video with pauses tightened and reel captions
on top. **Exported at the source's own size: 3840×2160 landscape, full frame — no crop, no zoom.** No music, no SFX.
(The first pass was a 1080×1920 vertical reframe with punch-ins; it read as too zoomed in and was dropped — see git history.)

| Clip | Built from (words in `assets/words.json`) |
| --- | --- |
| `01-wrong-order` | hook → "they turn on their ads, hire a setter…" → "at the start it's all about volume" → message me DOC |
| `02-the-bucket` | picture a bucket → every bucket leaks → ads are a hose → "most people buy the hose first" |
| `03-conversations-yourself` | "go and have the conversations yourself… every call is research" |
| `04-hire-when-drowning` | hire when drowning → the work comes first → never hand over face / voice / content |
| `05-first-content` | your first content won't be good → pick 3–4 topics, your own pace → show up every time |
| `06-too-wide` | "I coach traders" is too wide → you don't need a logo or a website |
| `07-ads-dont-create` | ads and people don't create anything… nothing to multiply |
| `08-one-thing-at-a-time` | add one thing, wait, check, then the next |

## Pipeline (run from this folder)

```bash
SRC=/path/to/Trader_to_Coach_-_full_video_FINAL.mp4
python3 -I scripts/shorts.py                       # print cut lists + captions (edit scripts/clips.py to change them)
bash scripts/build_all.sh $SRC /tmp/t2c-captions   # all clips: voice -> composition -> caption capture -> 4K render -> verify
bash scripts/build_all.sh $SRC /tmp/t2c-captions 03-conversations-yourself   # just one
python3 -I scripts/check_audio.py --final          # independent ASR pass over each render vs the intended words
```

Steps inside `build_all.sh`: `cut_audio.py` (voice cut on the picture frames, ~-15 LUFS) → `build_comp.py`
(`clips/<id>/index.html`, authored 1920×1080) → `capture.js` (caption layer as transparent PNGs at 2×) →
`render_4k.py` (source frames + captions composited in YUV, one H.264 encode) → `verify.py`.

- `scripts/clips.py` — the edit: snippets, caption corrections, blue key words, hero lines.
- `scripts/shorts.py` — cut list (pause tightening from the voice level in `assets/db.npy`) and captions.
- `scripts/verify.py` — every-frame check of a render against the source frames and caption schedule + review sheets in `renders/review/`.
- Each `clips/<id>/` is a Hyperframes composition (captions over `assets/base.mp4`; `npx hyperframes lint` inside it).
  The 4K export goes through `render_4k.py` rather than `hyperframes render` (4K capture of the whole frame is far slower).
  Media (`assets/*.mp4`, `assets/*.wav`) and `renders/` are regenerable and not committed.

Captions are word-for-word what is said; transcript mis-hearings are corrected in `clips.py` (`fix`).

## Stacked 1080x1920 reels (current style) — `scripts/stack/`

Clips 01, 02 and 08 are built in the stacked vertical style: pinned headline on top, the talking-head panel (a square crop of
the 4K frame, never upscaled) in the middle, one card of motion graphics underneath, captions at his chest.

```bash
SRC=/path/to/Trader_to_Coach_-_full_video_FINAL.mp4
python3 -I scripts/cut_audio.py $SRC 02-the-bucket                           # voice track on the cut list (after any change in clips.py)
python3 -I scripts/stack/geom.py $SRC facelm.task selfie.tflite 02-the-bucket  # head position / tone per shot -> clips/<id>/geom.json
bash scripts/stack/build.sh $SRC selfie.tflite /tmp/t2c-stack 02             # clip_02.py -> capture both layers -> render (picture + voice + SFX)
```

- `scripts/stack/kit.py` — layout, pinned titles, captions (`chest`, `hero` = caps in the blue bar), words behind his head, camera (`shot` / `punch` / `through`), page assembly.
- `scripts/stack/clip_NN.py` — one scene file per reel: titles, captions, camera, the card graphics and their timing (every time is `F(word index)`, so the graphics follow the cut).
- `scripts/stack/render.py` — decodes the cut list, moves the camera, composites the captured layers (behind-head layer through a person matte), mixes voice + effects.
- `scripts/clips.py` per-clip options: `tight` (pause tightening), `hold` (frames the last picture frame is held), `start` / `end` (first / last source frame of a snippet).

House rules that came out of review: nothing over his head or face (clip 02 uses chest captions only), key words in blue or in the
blue bar, one short label per step beside the graphic, every graphic lands on its word, the first and the last frame are chosen by eye.
