"""Better trader — talking-head reel (1080x1920, 30 fps) with two B-roll inserts.

  CUT      opens on "Be honest" (the first 0.7 s, him settling into frame, is gone). Pauses longer than 0.22 s are cut down
           to about 0.14 s; the beats the script relies on keep a little more air ("Yeah? Thought so.", "Think about that.",
           "...To strangers.", "...He just pressed record."). No words are cut. Ends just after "video".
  CAMERA   the take's own framing (the source is 1080x1920, so no base zoom). Four punch-ins to 108%, each one a cut, anchored
           at the bottom of the frame so his chin rises away from the captions (the last one holds through the send-off):  "Yeah? Thought so. ...doesn't it?" | "Not once ... win rate was" |
           "Coaching pays you for communicating" | "He just pressed record."
  B-ROLL   sales-call photo (slow 6% push), 1 s over "Hundreds of calls.";
           the filming clip over "Every day. On camera. To strangers." Straight cuts; his voice runs underneath.
  CAPTIONS the house style: Montserrat 800, bone white (#F2EFE9), one line of 1-5 words, a few key words in blue (#2F6FED);
           the five lines he asked to land (BETTER TRADER? / NOT ONCE. / WIN RATE / COMMUNICATING / HE JUST PRESSED RECORD.)
           in blue caps, a size up. Pop-in only (scale 0.9 -> 1, 0.16 s). The line sits just below his chin.
Run from the project folder: python3 -I scripts/build.py   ->  index.html + scene.json"""
import sys, json, math, wave, numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
FPS = 30; CW, CH = 1080, 1920; BLUE, BONE, INK = '#2F6FED', '#F2EFE9', '#0A0A0A'
W = json.load(open('assets/words.json')); FACE = {r['n']: r for r in json.load(open('assets/face.json'))}; NSRC = 1217
words = [w['word'] for w in W]; assert len(W) == 163
w_ = wave.open(sys.argv[1] if len(sys.argv) > 1 else "assets/th16.wav"); x = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768
DB = 20 * np.log10(np.sqrt((x[:len(x) // 160 * 160].reshape(-1, 160) ** 2).mean(1)) + 1e-6); QUIET = np.percentile(DB, 5) + 9
def speech_end(t):                                      # alignment ends can be early on a trailing consonant: run on while it is still loud
    k = int(t * 100)
    while k < len(DB) - 1 and DB[k] > QUIET and k < int(t * 100) + 12: k += 1
    return k / 100

# ---------------- cut list ----------------
START, END = 22, 1208                                   # source frames: 1.5 frames before "Be"; 3 frames after "video"
BEAT = {13: 0.30, 63: 0.30, 145: 0.30, 109: 0.24, 98: 0.22, 47: 0.20, 59: 0.20}       # word index -> pause kept after it (s)
cuts = []                                               # (first removed frame, first kept frame)
for i in range(len(W) - 1):
    e = speech_end(W[i]['end']); s = W[i + 1]['start']; gap = s - e
    if gap < 0.22: continue
    keep = BEAT.get(i, 0.14); a = math.ceil((e + 0.6 * keep) * FPS); b = math.floor((s - 0.4 * keep) * FPS)
    if b - a >= 2: cuts.append((a, b, i))
SHOTS = []; a0 = START
for a, b, i in cuts: SHOTS.append(dict(a=a0, b=a, after=i)); a0 = b
SHOTS.append(dict(a=a0, b=END, after=None))
FORCE = [W[142]['start']]                               # "He just pressed record": a cut-in with no time removed, so the punch lands on "He"
for t in FORCE:
    f = math.floor(t * FPS) - 1
    for k, s in enumerate(SHOTS):
        if s['a'] < f < s['b']: SHOTS[k:k + 1] = [dict(a=s['a'], b=f, after=None), dict(a=f, b=s['b'], after=s['after'])]; break
starts = np.cumsum([0] + [s['b'] - s['a'] for s in SHOTS]).tolist(); NF = starts[-1]
SRC = [f for s in SHOTS for f in range(s['a'], s['b'])]
for i, w in enumerate(W):                               # no word may be clipped by a cut
    assert any(s['a'] <= w['start'] * FPS - 0.5 and w['end'] * FPS <= s['b'] + 0.5 for s in SHOTS) or any(SHOTS[k]['b'] == SHOTS[k + 1]['a'] and SHOTS[k]['a'] <= w['start'] * FPS and w['end'] * FPS <= SHOTS[k + 1]['b'] for k in range(len(SHOTS) - 1)), ('word clipped', i, w)
def out_frame(t):
    f = int(math.floor(t * FPS + 1e-6))
    for s, o in zip(SHOTS, starts):
        if f < s['a']: return o
        if f < s['b']: return o if f - s['a'] <= 2 else o + f - s['a']
    return NF - 1
of = lambda i: out_frame(W[i]['start'])                 # output frame where word i starts

# ---------------- punch-ins (each a cut) and B-roll spans, in output frames ----------------
def shot_at(f): return next(k for k, (s, o) in enumerate(zip(SHOTS, starts)) if o <= f < o + s['b'] - s['a'])
cut_before = lambda i: starts[shot_at(of(i))]          # the cut just before word i
PUNCH = [(cut_before(14), cut_before(24)), (cut_before(48), cut_before(60)), (cut_before(99), of(104)), (cut_before(142), None)]     # the last one holds to the end
PUNCH = [(a, NF if b is None else b) for a, b in PUNCH]
for p0, p1 in PUNCH: assert p0 in starts and p1 > p0, (p0, p1)
BROLL = [dict(kind='still', a=of(41) - 3, b=of(41) + 27),                                         # 1 s over "Hundreds of calls." (back to him on "And")
         dict(kind='clip',  a=of(104) - 1, b=out_frame(speech_end(W[109]['end'])) + 1)]           # "Every day. On camera. To strangers."
for r in BROLL: r['n'] = r['b'] - r['a']
assert BROLL[0]['n'] == 30 and 45 <= BROLL[1]['n'] <= 60, [r['n'] for r in BROLL]
Z = 1.08; zoom = np.ones(NF)
for p0, p1 in PUNCH: zoom[p0:p1] = Z
anchor = []                                             # zoom centre per output frame: his nose x, the bottom of the frame (so a punch-in lifts his chin away from the captions)
for k, (s, o) in enumerate(zip(SHOTS, starts)):
    fr = [FACE[f] for f in range(s['a'], s['b'])]; ax = float(np.median([r['nx'] for r in fr])); ay = float(CH)
    anchor += [(round(ax, 1), round(ay, 1))] * (s['b'] - s['a'])

# ---------------- captions ----------------
CAP_Y, SIZE, EM = 1510, 58, 70                          # line top (px), size, emphasis size
CAPS = [(0, 'Be honest'), (2, 'are you a'), (5, '!BETTER TRADER?'), (7, 'than the guy'), (10, 'selling you a course'),
        (14, 'Yeah thought so'), (17, 'And it winds you up'), (22, "doesn't it"), (24, 'How is he the one'), (29, 'making *money* off it'),
        (33, 'I used to close sales'), (38, 'for trading coaches'), (41, 'Hundreds of calls'), (44, "And here's something"), (47, 'interesting'),
        (48, '!NOT ONCE.'), (50, 'did someone ask me'), (54, "what the coach's"), (57, '!WIN RATE was'), (60, 'Just think about that'),
        (64, "You don't necessarily know"), (68, "if he's a better trader"), (73, 'than you are'), (76, 'You followed him because'),
        (80, 'he explained something'), (83, 'in a way that'), (87, 'finally *clicked*'), (89, "And that's the difference"),
        (93, 'Trading pays you'), (96, 'for sitting quietly'), (99, 'Coaching pays you for'), (103, '!COMMUNICATING'),
        (104, 'Every day'), (106, 'On camera'), (108, 'To *strangers*'), (110, 'Some of the best traders'), (115, 'in the world'),
        (118, 'will never do that'), (122, 'So next time you see'), (127, 'someone with worse trades'), (131, 'than you selling a course'),
        (136, "He's not necessarily"), (139, 'a better trader'), (142, '!HE JUST'), (144, '!PRESSED RECORD.'), (146, 'Send this to that mate'),
        (151, "who's better than"), (154, 'every trading guru'), (157, "but hasn't posted"), (160, 'a single video')]
norm = lambda t: t.replace('!', '').replace('*', '').replace('?', '').replace('.', '').lower().split()
flat = [w for _, t in CAPS for w in norm(t)]; assert flat == [w.lower() for w in words], [(a, b) for a, b in zip(flat, [w.lower() for w in words]) if a != b][:3]
assert [i for i, _ in CAPS] == [0] + list(np.cumsum([len(norm(t)) for _, t in CAPS])[:-1])
_f = {wt: instancer.instantiateVariableFont(TTFont('assets/fonts/montserrat-latin-wght.woff2'), {'wght': wt}) for wt in (800, 900)}
def tw(t, size, wt):
    f = _f[wt]; cm = f.getBestCmap(); hm = f['hmtx']; return sum(hm[cm[ord(c)]][0] for c in t) / f['head'].unitsPerEm * size - 0.02 * size * (len(t) - 1)
esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;')
tm = lambda f: round(f / FPS - 0.001, 4) if f > 0 else 0
html, js, sched = [], [], []
for n, (w0, text) in enumerate(CAPS):
    f = 0 if n == 0 else of(w0)
    if w0 == 157: f = max(f, of(158) - 4)                # "but" is swallowed into "guru": the line changes just before "hasn't"
    if text.startswith('!'):                            # an emphasis line: blue caps a size up; a trailing lower-case word stays plain
        body = text[1:]; head = ' '.join(t for t in body.split() if t.upper() == t); tail = body[len(head):].strip()
        inner = f'<span class="em">{esc(head)}</span>' + (f' {esc(tail)}' if tail else ''); width = tw(head, EM, 900) + (tw(' ' + tail, SIZE, 800) if tail else 0)
    else:
        parts = text.split('*'); inner = ''.join(esc(p) if k % 2 == 0 else f'<span class="kw">{esc(p)}</span>' for k, p in enumerate(parts)); width = tw(text.replace('*', ''), SIZE, 800)
    assert width <= 860, ('caption too wide for the safe zone', text, round(width))
    html.append(f'<div id="cap{n}" class="cap"' + (' style="opacity:1"' if n == 0 else '') + f'><span class="ln">{inner}</span></div>')
    if n: js += [f'tl.set("#cap{n - 1}", {{ opacity: 0 }}, {tm(f)});', f'tl.set("#cap{n}", {{ opacity: 1 }}, {tm(f)});',
                 f'tl.fromTo("#cap{n} .ln", {{ scale: 0.9, y: 8 }}, {{ scale: 1, y: 0, duration: 0.16, ease: "power3.out", immediateRender: false }}, {tm(f)});']
    sched.append(dict(frame=f, text=text.replace('!', '').replace('*', '')))
inb_ = np.zeros(NF, bool)
for r in BROLL: inb_[r['a']:r['b']] = True
chin_out = lambda o: anchor[o][1] + (FACE[SRC[o]]['cy'] - anchor[o][1]) * zoom[o]
LAST_OFF = next((o for o in range(of(162), NF) if chin_out(o) > CAP_Y + 20), None)
if LAST_OFF is not None: js.append(f'tl.set("#cap{len(CAPS) - 1}", {{ opacity: 0 }}, {tm(LAST_OFF)});'); sched.append(dict(frame=LAST_OFF, text=''))
assert all(a['frame'] < b['frame'] for a, b in zip(sched, sched[1:])), [(a, b) for a, b in zip(sched, sched[1:]) if a['frame'] >= b['frame']]
# the caption line must stay clear of his chin on the talking-head frames (B-roll frames have no face to cover)
inb = np.zeros(NF, bool)
for r in BROLL: inb[r['a']:r['b']] = True
over = []
for o, f in enumerate(SRC):
    if inb[o]: continue
    z = zoom[o]; ay = anchor[o][1]; chin = ay + (FACE[f]['cy'] - ay) * z
    if chin > CAP_Y + 6: over.append((o, round(chin)))
comp = 'better-trader'; DUR = NF / FPS
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Better trader — Stew Scales</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: 'Montserrat'; src: url('assets/fonts/montserrat-latin-wght.woff2') format('woff2'); font-weight: 100 900; font-style: normal; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; }}
    #{comp} {{ position: relative; width: {CW}px; height: {CH}px; overflow: hidden; background: {INK}; font-family: 'Montserrat', sans-serif; }}
    #base {{ position: absolute; top: 0; left: 0; width: {CW}px; height: {CH}px; object-fit: cover; z-index: 1; }}
    #front {{ position: absolute; inset: 0; z-index: 2; }}
    body.capture, body.capture #{comp} {{ background: transparent; }}
    .cap {{ position: absolute; left: 0; width: {CW}px; top: {CAP_Y}px; height: 90px; display: flex; align-items: center; justify-content: center; opacity: 0; }}
    .ln {{ display: inline-block; white-space: nowrap; font-weight: 800; font-size: {SIZE}px; line-height: 1.1; letter-spacing: -0.02em; color: {BONE}; transform-origin: 50% 60%;
          text-shadow: 0 0 2px rgba(10,10,10,0.9), 0 2px 5px rgba(10,10,10,0.75), 0 0 18px rgba(10,10,10,0.6), 0 0 40px rgba(10,10,10,0.4); }}
    .kw, .em {{ color: {BLUE}; text-shadow: 0 0 2px rgba(5,5,10,1), 0 0 4px rgba(5,5,10,0.95), 0 2px 8px rgba(5,5,10,0.85), 0 0 22px rgba(5,5,10,0.65), 0 0 44px rgba(5,5,10,0.4); }}
    .kw {{ font-weight: 900; }}  .em {{ font-weight: 900; font-size: {EM}px; letter-spacing: -0.01em; }}
  </style>
</head>
<body>

<div id="{comp}" data-composition-id="{comp}" data-start="0" data-width="{CW}" data-height="{CH}">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base.mp4" data-volume="1"></audio>

  <div id="front">
{chr(10).join('    ' + h for h in html)}
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
open('index.html', 'w').write(page)
json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
           "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}, open('hyperframes.json', 'w'), indent=2)
json.dump({"id": comp, "name": "Better trader", "dimensions": {"width": CW, "height": CH}, "fps": FPS, "createdAt": "2026-11-23T07:00:00.000Z"}, open('meta.json', 'w'), indent=2)
json.dump(dict(comp=comp, fps=FPS, out_size=[CW, CH], frames=NF, shots=SHOTS, out_start=starts[:-1], src=SRC, zoom=[round(float(z), 4) for z in zoom], anchor=anchor,
               broll=BROLL, punch=PUNCH, captions=sched), open('scene.json', 'w'))
print(f'frames {NF} ({NF / FPS:.2f} s, from {(END - START) / FPS:.2f} s)  cuts {len(cuts)}  punch {PUNCH}  broll {[(r["kind"], r["a"], r["b"], r["n"]) for r in BROLL]}')
print('chin below the caption line on', len(over), 'talking-head frames', over[:12])
