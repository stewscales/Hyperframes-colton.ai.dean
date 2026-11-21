"""Coaches look rich, v2: the same pre-cut take (2160x3840, 30 fps) edited as a premium personal-brand reel.

  CUT      opens on the first frame his eyes are on the lens, two frames before "Coaches" (the laptop moment is gone).
           Pauses come down to about 0.1-0.15 s: after "rich", after "business" (the take's own cut is in there), after
           "lifestyle" (a breath goes too). Two cuts remove no time at all: on "watches" the camera cuts in for the list, and
           on "because" it resets for the payoff. Ends on "converting", then holds that frame for half a second while the push carries on.
  CAMERA   a tighter base framing (110% of the take), centred on his face; his eye line held a third of the way down, the
           camera following it slowly up and down. Each move has one job:
             opening   settles from 115% to 111% in the first 0.4 s, then an eased punch to +9% on "look rich" (the hook)
             thesis    "they've completely forgot how to build a business": a wider reset, slow push
             list      "Everyone's so focused on posting their" wide; cut in (+8%) on "watches", slow push through cars / lifestyle
             reversal  "none of it actually matters": the tightest frame of the reel (+20% on the base), a cut, not a move
             payoff    "because the content": reset, then an eased punch to +10% on "isn't converting", held to the end
           The output is 1440x2560: at its tightest the crop is 1700 px wide, so every output pixel still comes from the
           camera (nothing is upscaled).
  CAPTIONS Montserrat 800, bone white (#F2EFE9), the key word in brand blue (#2F6FED), one line of 1-5 words on his chest
           just below the mic, inside Instagram's safe zones and never over his face. A chunk pops in (scale 0.9 -> 1, 0.16 s, no bounce);
           a key word that comes later in its chunk turns blue on the frame it is spoken.

Writes index.html (the caption layer as a Hyperframes composition, authored at 1080x1920) and scene.json (cut list,
per-frame crop, captions) for scripts/capture.js and scripts/render.py.   Run from the project folder: python3 -I scripts/build.py"""
import json, math, numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
FPS = 30; SW, SH = 2160, 3840; CW, CH = 1080, 1920; OW, OH = 1440, 2560
BLUE, BONE, INK = '#2F6FED', '#F2EFE9', '#0A0A0A'
W = json.load(open('assets/words.json')); FACE = {r['n']: r for r in json.load(open('assets/face.json'))}
ws = lambda i: W[i]['start'] * FPS                      # source frame on which word i starts

# ---------------- cut list (source frames, end exclusive) ----------------
# A ends in the quiet after the "ch" of "rich" (3.80 s); B starts 2 frames before "they've"; 175 | 176 is the take's own cut;
# C starts 1 frame before "Everyone's"; C1 | C2 is a cut-in on "watches" with no time removed; D starts 2 frames before "none"
# (the breath before it is gone); D | E is a cut on "because" with no time removed (the gap there is already short);
# E ends on the last frame of "converting".
SHOTS = [dict(n='A',  a=33,  b=114),                   # Coaches are so focused on trying to look rich,
         dict(n='B',  a=116, b=175),                   # they've completely forgot how to build a business.
         dict(n='C1', a=180, b=240),                   # Everyone's so focused on posting their
         dict(n='C2', a=240, b=305),                   # watches and their cars and their lifestyle,
         dict(n='D',  a=314, b=345),                   # none of it actually matters,
         dict(n='E',  a=345, b=392)]                   # because the content isn't converting.
HOLD = 14                                              # frames the last frame is held (the ending lands instead of cutting off)
starts = np.cumsum([0] + [s['b'] - s['a'] for s in SHOTS]).tolist(); NV = starts[-1]; NF = NV + HOLD
SRC = [f for s in SHOTS for f in range(s['a'], s['b'])] + [SHOTS[-1]['b'] - 1] * HOLD      # source frame shown on each output frame
RUNS = []                                              # stretches of continuous footage (a cut-in with no time removed does not split one)
for s in SHOTS:
    if RUNS and RUNS[-1][1] == s['a']: RUNS[-1][1] = s['b']
    else: RUNS.append([s['a'], s['b']])
for i, w in enumerate(W): assert any(a <= w['start'] * FPS - 0.5 and w['end'] * FPS <= b + 0.5 for a, b in RUNS), ('a word is clipped by the cut', i, w)
def out_frame(t):
    f = int(math.floor(t * FPS + 1e-6))
    for s, o in zip(SHOTS, starts):
        if f < s['a']: return o
        if f < s['b']: return o if f - s['a'] <= 2 else o + f - s['a']      # a word that starts right after a cut shows on the cut
    return NV - 1
local = lambda s, f: int(round(f - s['a']))            # source frame -> frame within the shot

# ---------------- camera: zoom per output frame (relative to the full take) ----------------
ease = lambda u: u * u * (3 - 2 * u)                    # smoothstep: zooms start and land softly
zoom = []
for s in SHOTS:
    n = s['b'] - s['a']; z = np.zeros(n); k = np.arange(n)
    if s['n'] == 'A':
        p0 = local(s, ws(7)) - 2                        # "look"
        z[:] = np.interp(k, [0, 12, p0], [1.15, 1.11, 1.13])
        z[:12] = 1.11 + 0.04 * (1 - ease(np.clip(k[:12] / 12, 0, 1)))             # the opening settle
        z[p0:] = 1.13 * (1 + 0.09 * ease(np.clip((k[p0:] - p0) / 9, 0, 1)))        # punch on "look rich"
    elif s['n'] == 'B':  z[:] = np.linspace(1.14, 1.17, n)
    elif s['n'] == 'C1': z[:] = np.linspace(1.10, 1.12, n)
    elif s['n'] == 'C2': z[:] = np.linspace(1.20, 1.23, n)      # a clear cut-in (+8%), not a nudge
    elif s['n'] == 'D':  z[:] = np.linspace(1.32, 1.33, n)      # tightest frame of the reel, +9% on the shot before
    elif s['n'] == 'E':
        p0 = local(s, ws(38)) - 2                       # "isn't"
        z[:] = np.interp(k, [0, p0], [1.12, 1.13])
        z[p0:] = 1.13 * (1 + 0.10 * ease(np.clip((k[p0:] - p0) / 9, 0, 1))) + 0.0003 * np.maximum(0, k[p0:] - p0 - 9)
    zoom += list(z)
zoom += list(zoom[-1] + 0.0015 * np.arange(1, HOLD + 1))  # the push carries on through the held frame, so the hold reads as a move, not a freeze
zoom = np.array(zoom); assert len(zoom) == NF and zoom.min() >= 1.0 and zoom.max() <= 1.5 * 0.999, 'never upscale: the crop must stay at least 1440 px wide'

# ---------------- camera: where it points ----------------
EYE_Y = 0.35                                            # his eye line sits a third of the way down the frame
CAP_Y, SIZE = 1336, 58                                  # caption line (1080x1920 px): mid chest, just below the clip-on mic (at the old chest line the mic
                                                        # showed between words), clear of Instagram's caption area (below ~1500) and its button column (x > ~960)
def smooth(v, sigma):
    r = int(3 * sigma); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); return np.convolve(np.pad(v, r, mode='edge'), k / k.sum(), mode='valid')
groups = [('A',), ('B',), ('C1', 'C2'), ('D', 'E')]     # C1|C2 and D|E are continuous footage: one camera axis each, so those cuts go straight in / out
crop = [None] * NF
for g in groups:
    ss = [s for s in SHOTS if s['n'] in g]; a, b = ss[0]['a'], ss[-1]['b']
    fr = [FACE[f] for f in range(a, b)]; assert all('nx' in r for r in fr)
    cx = float(np.median([r['nx'] for r in fr])); ey = smooth(np.array([r['ey'] for r in fr]), 22)
    o0 = starts[SHOTS.index(ss[0])]; last = SHOTS.index(ss[-1]) == len(SHOTS) - 1
    for k in range(b - a + (HOLD if last else 0)):
        o = o0 + k; z = zoom[o]; kk = min(k, b - a - 1); w_, h_ = SW / z, SH / z
        x0 = min(max(cx - w_ / 2, 40 if a < 176 else 0), SW - w_)              # the first half of the take has a dark strip down its left edge
        y0 = min(max(ey[kk] - EYE_Y * h_, 0), SH - h_)
        crop[o] = [round(float(z), 5), round(x0, 2), round(y0, 2)]
        r = fr[kk]; oy = lambda y: (y - y0) * z * CH / SH                       # source y -> caption-layer y (1080x1920)
        assert oy(r['fy'] - 0.42 * (r['cy'] - r['fy'])) > 0.05 * CH, ('too little headroom', g, k)
        assert oy(r['cy']) < CAP_Y - 90, ('his chin comes too close to the caption', g, k, round(oy(r['cy'])))
assert all(c is not None for c in crop)

# ---------------- captions ----------------
CAPS = [(0,  'Coaches are so focused',       0),       # (first word, text, key word index or None)
        (4,  'on trying to look rich',       8),
        (9,  "they've completely forgot",    None),
        (12, 'how to build a business',      16),
        (17, "Everyone's so focused",        None),
        (20, 'on posting their',             None),
        (23, 'watches',                      23),
        (24, 'and their cars',               26),
        (27, 'and their lifestyle',          29),
        (30, 'none of it actually matters',  30),
        (35, 'because the content',          None),
        (38, "isn't converting",             39)]
said = [w['word'].lower() for w in W]
assert ' '.join(t for _, t, _ in CAPS).lower().split() == said, 'captions must be exactly the words he says'
assert [i for i, _, _ in CAPS] == [0] + list(np.cumsum([len(t.split()) for _, t, _ in CAPS])[:-1])
_f = instancer.instantiateVariableFont(TTFont('assets/fonts/montserrat-latin-wght.woff2'), {'wght': 800}); _cm = _f.getBestCmap(); _hm = _f['hmtx']; _upm = _f['head'].unitsPerEm
tw = lambda t: sum(_hm[_cm[ord(c)]][0] for c in t) / _upm * SIZE - 0.02 * SIZE * (len(t) - 1)
esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;')
tm = lambda f: round(f / FPS - 0.001, 4) if f > 0 else 0
html_caps, js, sched = [], [], []
for i, (w0, text, key) in enumerate(CAPS):
    assert tw(text) <= 820, ('caption too wide for the safe zone', text, tw(text))
    f = 0 if i == 0 else out_frame(W[w0]['start']); spans = []
    for j, word in enumerate(text.split()):
        wi = w0 + j
        if wi == key:
            late = wi != w0; fk = out_frame(W[wi]['start'])
            spans.append(f'<span id="k{i}" class="kw{" late" if late else ""}">{esc(word)}</span>')
            if late: js += [f'tl.to("#k{i}", {{ color: "{BLUE}", duration: 0.08, ease: "none" }}, {tm(fk)});',
                            f'tl.fromTo("#k{i}", {{ scale: 1.045 }}, {{ scale: 1, duration: 0.2, ease: "power2.out", immediateRender: false }}, {tm(fk)});']   # small enough not to touch its neighbours
            sched.append(dict(frame=fk, key=word))
        else: spans.append(esc(word))
    html_caps.append(f'<div id="cap{i}" class="cap"' + (' style="opacity:1"' if i == 0 else '') + f'><span class="ln">{" ".join(spans)}</span></div>')
    if i: js += [f'tl.set("#cap{i - 1}", {{ opacity: 0 }}, {tm(f)});', f'tl.set("#cap{i}", {{ opacity: 1 }}, {tm(f)});',
                 f'tl.fromTo("#cap{i} .ln", {{ scale: 0.9, y: 8 }}, {{ scale: 1, y: 0, duration: 0.16, ease: "power3.out", immediateRender: false }}, {tm(f)});']
    sched.append(dict(frame=f, text=text))
caps_on = [c['frame'] for c in sched if 'text' in c]; assert all(a < b for a, b in zip(caps_on, caps_on[1:])), caps_on
comp = 'coaches-look-rich-v2'; DUR = NF / FPS
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
    body.capture, body.capture #{comp} {{ background: transparent; }}      /* scripts/capture.js: the caption layer alone, on a transparent page */
    .cap {{ position: absolute; left: 0; width: {CW}px; top: {CAP_Y}px; text-align: center; opacity: 0; }}
    .ln {{ display: inline-block; white-space: nowrap; font-weight: 800; font-size: {SIZE}px; line-height: 1.1; letter-spacing: -0.02em; color: {BONE}; transform-origin: 50% 60%;
          text-shadow: 0 0 2px rgba(10,10,10,0.85), 0 2px 5px rgba(10,10,10,0.7), 0 0 18px rgba(10,10,10,0.55), 0 0 40px rgba(10,10,10,0.35); }}
    .kw {{ display: inline-block; color: {BLUE}; font-weight: 900; transform-origin: 50% 60%;
          text-shadow: 0 0 2px rgba(5,5,10,1), 0 0 4px rgba(5,5,10,0.95), 0 2px 8px rgba(5,5,10,0.85), 0 0 22px rgba(5,5,10,0.65), 0 0 44px rgba(5,5,10,0.4); }}
    .kw.late {{ color: {BONE}; }}
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
json.dump({"id": comp, "name": "Coaches look rich (v2)", "dimensions": {"width": CW, "height": CH}, "fps": FPS, "createdAt": "2026-11-21T14:00:00.000Z"}, open('meta.json', 'w'), indent=2)
json.dump(dict(comp=comp, fps=FPS, src_size=[SW, SH], out_size=[OW, OH], frames=NF, footage_frames=NV, hold=HOLD, shots=SHOTS, out_start=starts[:-1],
               src=SRC, crop=crop, eye_y=EYE_Y, captions=sched), open('scene.json', 'w'))
print(f'frames {NF} ({NF / FPS:.2f} s, {HOLD} held)  zoom {zoom.min():.3f}-{zoom.max():.3f}  tightest crop {SW / zoom.max():.0f} px wide')
print('shots', [(s['n'], s['a'], s['b'], o) for s, o in zip(SHOTS, starts)])
print('captions', [(c['frame'], c.get('text') or ('key: ' + c['key'])) for c in sched])
