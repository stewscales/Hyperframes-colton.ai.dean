"""Coaches look rich — a 4K (2160x3840) talking-head reel, edited from one pre-cut take.

The edit, all in one place:
  CUT      starts on the first frame his eyes are on the lens (the laptop-closing moment is gone), three pauses of 0.3 s+
           come down to about 0.16 s (each one is a jump cut onto a different framing), ends on the last word before he blinks.
  FRAMING  a tighter crop than the take (the source is 2160x3840; the crop is scaled back up to 2160x3840), centred on his
           face per shot: a base framing with a slow push, a punch-in on the two payoff lines; the camera follows his eye line
           slowly up and down so the framing holds when he leans in.
  CAPTIONS Montserrat, sentence case, 2-4 words, white, the key words on the brand-blue bar, on his upper chest
           (between his collar and the mic; inside Instagram's safe zones).
Nothing else: no titles, no transitions, no sound effects, no grade.

Writes index.html (the caption layer as a Hyperframes composition, authored at 1080x1920 and captured at 2x) and scene.json
(cut list, per-frame crop, captions) for scripts/render.py.   Run from the project folder: python3 -I scripts/build.py"""
import json, math, os, numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
FPS = 30; SW, SH = 2160, 3840; CW, CH = 1080, 1920
BLUE, INK = '#2F6FED', '#0A0A0A'
W = json.load(open('assets/words.json')); FACE = {r['n']: r for r in json.load(open('assets/face.json'))}

# ---------------- cut list (source frames, end exclusive) ----------------
# 33  = eyes on the lens, 2 frames before "Coaches" (0-32: closing the laptop, looking down)
# 113-116, 173-178, 308-313 = the middle of the three longest pauses (after "rich", "business", "lifestyle"); 176 is the take's own cut
# 392 = "converting" is out; he blinks from 392
SHOTS = [dict(a=33,  b=113, z=(1.18, 1.21)),            # Coaches are so focused on trying to look rich,
         dict(a=116, b=173, z=(1.32, 1.34)),            # they've completely forgot how to build a business.        (punch-in)
         dict(a=178, b=308, z=(1.18, 1.25)),            # Everyone's so focused on posting their watches and their cars and their lifestyle,   (slow push through the list)
         dict(a=313, b=392, z=(1.33, 1.37))]            # none of it actually matters, because the content isn't converting.   (punch-in)
EYE_Y = 0.35                                            # his eye line sits here in the frame (fraction of the height)
starts = np.cumsum([0] + [s['b'] - s['a'] for s in SHOTS]).tolist(); NF = starts[-1]
def out_frame(t):
    f = int(math.floor(t * FPS + 1e-6))
    for s, o in zip(SHOTS, starts):
        if f < s['a']: return o
        if f < s['b']: return o if f - s['a'] <= 3 else o + f - s['a']      # a word that starts right after a cut switches on the cut
    return NF - 1
for i, w in enumerate(W): assert any(s['a'] <= w['start'] * FPS - 0.5 and w['end'] * FPS <= s['b'] + 0.5 for s in SHOTS), ('a word is clipped by the cut', i, w)       # no word may be clipped

# ---------------- framing: one fixed camera per shot, centred on his face, with a slow push ----------------
crop = []                                               # per output frame: [zoom, source x of the frame's left edge, source y of its top edge]
CAP_Y, SIZE, WT = 1160, 56, 700                          # captions (1080x1920 px): upper chest, between collar and mic; well inside the safe zones
def smooth(v, sigma):                                   # gaussian low-pass with the ends held (the camera eases after him, it does not jitter)
    r = int(3 * sigma); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); return np.convolve(np.pad(v, r, mode='edge'), k / k.sum(), mode='valid')
for s in SHOTS:
    fr = [FACE[n] for n in range(s['a'], s['b'])]; assert all('nx' in r for r in fr); n = s['b'] - s['a']
    cx = float(np.median([r['nx'] for r in fr]))        # side to side the camera stays put ...
    ey = smooth(np.array([r['ey'] for r in fr]), 22)    # ... up and down it follows his eye line slowly, so his chin never sinks into the caption when he leans in
    for k in range(n):
        z = s['z'][0] + (s['z'][1] - s['z'][0]) * k / (n - 1)
        w_, h_ = SW / z, SH / z
        x0 = min(max(cx - w_ / 2, 40 if s['a'] < 176 else 0), SW - w_)          # the first half of the take has a 36 px dark strip down its left edge
        y0 = min(max(ey[k] - EYE_Y * h_, 0), SH - h_)
        crop.append([round(z, 5), round(x0, 2), round(y0, 2)])
        r = fr[k]; oy = lambda y: (y - y0) * z / 2      # source y -> output y at 1080x1920
        assert oy(r['fy'] - 0.42 * (r['cy'] - r['fy'])) > 0.05 * CH, ('the top of his hair comes too close to the top of the frame', s, k)
        assert oy(r['cy']) < CAP_Y - 100, ('his chin comes too close to the caption', s, k, oy(r['cy']))
    s['cx'], s['ey'] = round(cx), [round(float(ey.min())), round(float(ey.max()))]
assert max(c[0] for c in crop) <= 1.4

# ---------------- captions ----------------
CAPS = [(0,  '*Coaches* are so focused'),                # (index of the first word, text; *key words* in brand blue)
        (4,  'on trying to *look rich*'),
        (9,  "they've completely forgot"),
        (12, 'how to build a *business*'),
        (17, "Everyone's so focused"),
        (20, 'on posting their'),
        (23, '*watches*'),
        (24, 'and their *cars*'),
        (27, 'and their *lifestyle*'),
        (30, '*none of it* actually matters'),
        (35, 'because the content'),
        (38, "*isn't converting*")]
said = ' '.join(w['word'] for w in W).lower()            # the captions are exactly the words he says, in order
assert ' '.join(t.replace('*', '') for _, t in CAPS).lower() == said, 'captions differ from the transcript'
assert [i for i, _ in CAPS] == [0] + list(np.cumsum([len(t.split()) for _, t in CAPS])[:-1]), 'caption word indices'
_f = instancer.instantiateVariableFont(TTFont('assets/fonts/montserrat-latin-wght.woff2'), {'wght': 800}); _cm = _f.getBestCmap(); _hm = _f['hmtx']; _upm = _f['head'].unitsPerEm
tw = lambda t: sum(_hm[_cm[ord(c)]][0] for c in t) / _upm * SIZE - 0.03 * SIZE * (len(t) - 1)
esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;')
def rich(t): return ''.join(esc(p) if i % 2 == 0 else f'<span class="hl">{esc(p)}</span>' for i, p in enumerate(t.split('*')))
tm = lambda f: round(f / FPS - 0.001, 4) if f > 0 else 0
html_caps, js, sched = [], [], []
for i, (wi, text) in enumerate(CAPS):
    assert tw(text.replace('*', '')) + 34 * (text.count('*') // 2) <= 880, ('caption too wide', text, tw(text.replace('*', '')))
    f = 0 if i == 0 else out_frame(W[wi]['start']); sched.append(dict(frame=f, text=text.replace('*', '')))
    html_caps.append(f'<div id="cap{i}" class="cap"' + (' style="opacity:1"' if i == 0 else '') + f'>{rich(text)}</div>')
    if i: js += [f'tl.set("#cap{i - 1}", {{ opacity: 0 }}, {tm(f)});', f'tl.set("#cap{i}", {{ opacity: 1 }}, {tm(f)});',
                 f'tl.fromTo("#cap{i}", {{ y: 14, filter: "blur(6px)" }}, {{ y: 0, filter: "blur(0px)", duration: 0.18, ease: "power3.out", immediateRender: false }}, {tm(f)});']
assert all(a['frame'] < b['frame'] for a, b in zip(sched, sched[1:])), sched
comp = 'coaches-look-rich'; DUR = NF / FPS
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Coaches look rich — Stew Scales</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: 'Montserrat'; src: url('assets/fonts/montserrat-latin-wght.woff2') format('woff2'); font-weight: 100 900; font-style: normal; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; }}
    #{comp} {{ position: relative; width: {CW}px; height: {CH}px; overflow: hidden; background: {INK}; font-family: 'Montserrat', sans-serif; }}
    #base {{ position: absolute; top: 0; left: 0; width: {CW}px; height: {CH}px; object-fit: cover; z-index: 1; }}
    #front {{ position: absolute; inset: 0; z-index: 2; }}
    body.capture, body.capture #{comp} {{ background: transparent; }}      /* scripts/capture.js: the caption layer alone, on a transparent page, at 2x */
    .cap {{ position: absolute; left: 0; width: {CW}px; top: {CAP_Y}px; text-align: center; white-space: nowrap; font-weight: {WT}; font-size: {SIZE}px; line-height: 1.12; letter-spacing: -0.03em; color: #fff; opacity: 0;
           text-shadow: 0 2px 5px rgba(0,0,0,0.75), 0 0 20px rgba(0,0,0,0.6), 0 0 46px rgba(0,0,0,0.45); }}
    .cap .hl {{ display: inline-block; background: {BLUE}; color: #fff; font-weight: 800; padding: 1px 14px 5px; margin: 0 3px; border-radius: 12px; text-shadow: none; box-shadow: 0 6px 20px rgba(0,0,0,0.35); }}   /* key words: white on the brand-blue bar (blue type alone is too dim on his navy tee) */
  </style>
</head>
<body>

<div id="{comp}" data-composition-id="{comp}" data-start="0" data-width="{CW}" data-height="{CH}">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base.mp4" data-volume="1"></audio>

  <div id="front">
{chr(10).join('    ' + x for x in html_caps)}
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Generated by scripts/build.py (frames at 30 fps; word times from forced alignment, mapped through the cut list)
    {(chr(10) + '    ').join(js)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines["{comp}"] = tl;
  </script>
</div>

</body>
</html>
'''
open('index.html', 'w').write(html)
json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
           "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}, open('hyperframes.json', 'w'), indent=2)
json.dump({"id": comp, "name": "Coaches look rich (4K)", "dimensions": {"width": CW, "height": CH}, "fps": FPS, "createdAt": "2026-11-20T15:00:00.000Z"}, open('meta.json', 'w'), indent=2)
json.dump(dict(comp=comp, fps=FPS, size=[SW, SH], frames=NF, shots=SHOTS, out_start=starts[:-1], crop=crop, captions=sched), open('scene.json', 'w'))
print('frames', NF, f'({DUR:.2f} s)  shots', [(s['a'], s['b'], s['z'], s['cx'], s['ey']) for s in SHOTS])
print('captions', [(c['frame'], c['text']) for c in sched])
