# Trader to Coach — shorts (Instagram Reels / TikTok)

Eight 1080×1920 shorts cut from the clean 4K long-form recording (`Trader_to_Coach_-_full_video_FINAL.mp4`,
the same source as `../trader-to-coach/`). Each one is assembled from snippets of the long video, pauses
tightened, reframed vertical around the face with punch-ins on the cuts, reel captions on top. No music, no SFX.

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
python3 -I scripts/cut_audio.py $SRC               # clips/<id>/assets/voice.wav  (cut on the picture frames, ~-15 LUFS)
python3 -I scripts/check_audio.py                  # independent ASR pass over each cut vs the intended words
python3 -I scripts/render_th.py $SRC facelm.task   # clips/<id>/assets/th.mp4 + edl.json (4K -> 1080x1920, never upscaled)
python3 -I scripts/build_comp.py                   # clips/<id>/index.html (+ hyperframes.json, meta.json, captions.json)
bash scripts/finish.sh 01-wrong-order ...          # mux -> lint -> hyperframes render -> scripts/verify.py
```

- `scripts/clips.py` — the edit: snippets, framing per shot, caption corrections, blue key words, hero lines.
- `scripts/shorts.py` — cut list (pause tightening from the voice level in `assets/db.npy`), framing schedule, captions.
- `scripts/verify.py` — every-frame check of a render against its base and caption schedule + review sheets in `renders/review/`.
- Each `clips/<id>/` is a self-contained Hyperframes project (run `npx hyperframes preview|lint|render` inside it).
  Media (`assets/*.mp4`, `assets/*.wav`) and `renders/` are regenerable and not committed.

Captions are word-for-word what is said; transcript mis-hearings are corrected in `clips.py` (`fix`).
