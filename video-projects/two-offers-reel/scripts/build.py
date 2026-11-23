"""Two offers — talking-head reel (1080x1920, 30 fps) with two B-roll inserts, in the house style of better-trader-reel.

  CUT      opens on "I've generated" (eyes on the lens; the first second, him settling, is gone). Pauses longer than 0.22 s
           come down to about 0.14 s; the turns in the argument keep a little more air (after "the wrong buyers", "...the
           results", "...your own world", "...spending £5,000" and "...two completely different offers"). No words are cut.
           Ends 0.7 s after "offering", on him looking into the lens.
  CAMERA   the take's own framing. Four punch-ins, each a cut on a sentence break, anchored at the bottom of the frame so his
           chin rises away from the captions:  "They're attracting the wrong buyers" 108% | "Because someone's spending
           £5,000..." 110% | "For someone spending £50, you don't need the same convincing..." 110% | the last line 112%, held.
  B-ROLL   the desk / filming clip over "long-form YouTube videos, breaking down your strategy" (2.4 s);
           the night drive over "Show off your lifestyle" (1.3 s). Straight cuts; his voice runs underneath.
  OVERLAYS one small card above his head: "£5,000 / AUTHORITY + TRUST" on "you need content that builds authority and it
           builds trust"; "£50 / ATTENTION + DESIRE" on "you need short-form content that grabs attention and it creates desire".
  CAPTIONS the house style: Montserrat 800, bone white (#F2EFE9), one line of 1-5 words, blue (#2F6FED) for the few lines he
           asked to land, in caps a size up. Pop-in only (scale 0.9 -> 1, 0.16 s). Same position as the last reel.
Run from the project folder: python3 -I scripts/build.py <th16.wav>   ->  index.html + scene.json"""
import sys, json, math, wave, numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
FPS = 30; CW, CH = 1080, 1920; BLUE, BONE, INK = '#2F6FED', '#F2EFE9', '#0A0A0A'
W = json.load(open('assets/words.json')); FACE = {r['n']: r for r in json.load(open('assets/face.json'))}; NSRC = 1460
words = [w['word'] for w in W]; assert len(W) == 160
w_ = wave.open(sys.argv[1] if len(sys.argv) > 1 else "assets/th16.wav"); x = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768
DB = 20 * np.log10(np.sqrt((x[:len(x) // 160 * 160].reshape(-1, 160) ** 2).mean(1)) + 1e-6); QUIET = np.percentile(DB, 5) + 9
def speech_end(t):                                      # alignment ends can be early on a trailing consonant: run on while it is still loud
    k = int(t * 100)
    while k < len(DB) - 1 and DB[k] > QUIET and k < int(t * 100) + 12: k += 1
    return k / 100

# ---------------- cut list ----------------
START, END = 30, 1460                                   # source frames: 2 frames before "I've"; to the end of the take (1.2 s after "offering", so the last line breathes)
BEAT = {22: 0.24, 39: 0.20, 80: 0.30, 102: 0.24, 123: 0.30, 139: 0.30, 151: 0.44}     # word index -> pause kept after it (s)
cuts = []                                               # (first removed frame, first kept frame)
for i in range(len(W) - 1):
    e = speech_end(W[i]['end']); s = W[i + 1]['start']; gap = s - e
    if gap < 0.22: continue
    keep = BEAT.get(i, 0.14); a = math.ceil((e + 0.6 * keep) * FPS); b = math.floor((s - 0.4 * keep) * FPS)
    if b - a >= 2: cuts.append((a, b, i))
SHOTS = []; a0 = START
for a, b, i in cuts: SHOTS.append(dict(a=a0, b=a, after=i)); a0 = b
SHOTS.append(dict(a=a0, b=END, after=None))
FORCE = [W[18]['start'], W[23]['start'], W[152]['start'] - 0.10]               # cut-ins with no time removed, so the first punch lands on "They're" and ends on "If"
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
PUNCH = [(cut_before(18), cut_before(23)), (cut_before(65), cut_before(81)), (cut_before(124), cut_before(140)), (cut_before(152), None)]     # the last one holds to the end
PUNCH = [(a, NF if b is None else b) for a, b in PUNCH]
for p0, p1 in PUNCH: assert p0 in starts and p1 > p0, (p0, p1)
BROLL = [dict(kind='desk',  a=of(42) - 2, b=starts[shot_at(of(50))], src0=30),                    # "long-form YouTube videos, breaking down your strategy" (back to him for "analysing")
         dict(kind='drive', a=of(103) - 1, b=out_frame(speech_end(W[106]['end'])) + 2, src0=26)]   # "Show off your lifestyle" (back to him for "your personality")
for r in BROLL: r['n'] = r['b'] - r['a']
assert 60 <= BROLL[0]['n'] <= 90 and 30 <= BROLL[1]['n'] <= 45, [r['n'] for r in BROLL]
ZS = [1.08, 1.10, 1.10, 1.12]; zoom = np.ones(NF)                  # the comparison and the last line a step further
for (p0, p1), Z in zip(PUNCH, ZS): zoom[p0:p1] = Z
anchor = []                                             # zoom centre per output frame: his nose x, the bottom of the frame (so a punch-in lifts his chin away from the captions)
for k, (s, o) in enumerate(zip(SHOTS, starts)):
    fr = [FACE[f] for f in range(s['a'], s['b'])]; ax = float(np.median([r['nx'] for r in fr])); ay = float(CH)
    anchor += [(round(ax, 1), round(ay, 1))] * (s['b'] - s['a'])

# ---------------- captions ----------------
CAP_Y, SIZE, EM = 1526, 58, 70                          # line top (px), size, emphasis size
CAPS = [("i've generated", "I've generated"), ("nearly two million pounds", "[NEARLY £2 MILLION]"), ("for trading coaches", "for trading coaches"),
        ("but i keep seeing the same", "But I keep seeing the same"), ("mistake with content", "*mistake* with content"),
        ("they're attracting", "They're attracting"), ("the wrong buyers", "the [WRONG BUYERS]"),
        ("if you're selling a", "If you're selling a"), ("five k mentorship", "[£5,000 MENTORSHIP]"),
        ("you need content", "you need content"), ("that builds authority", "that builds [AUTHORITY]"), ("and it builds trust", "and it builds [TRUST]"),
        ("it's like long form", "It's like long-form"), ("youtube videos", "YouTube videos"), ("breaking down", "breaking down"), ("your strategy", "your strategy"),
        ("analysing your trades", "analysing your trades"), ("explaining your psychology", "explaining your psychology"),
        ("and showing people", "and showing people"), ("you actually know", "you actually know"), ("what you're doing", "what you're doing"),
        ("because someone's", "Because someone's"), ("spending five k", "spending £5,000"), ("they need to trust", "they need to trust"),
        ("that you can get them", "that you can get them"), ("the results", "the results"),
        ("if you're selling a", "If you're selling a"), ("fifty pound product", "[£50 PRODUCT]"), ("it's completely different", "it's completely different"),
        ("you need short form", "You need short-form"), ("content", "content"), ("that grabs attention", "that grabs [ATTENTION]"), ("and it creates desire", "and it creates [DESIRE]"),
        ("show off your lifestyle", "Show off your lifestyle"), ("your personality", "your personality"), ("your wins and your results", "your wins and your results"),
        ("make people want to be", "Make people want to be"), ("part of your own world", "part of your own world"),
        ("for someone spending fifty pounds", "For someone spending £50"), ("you don't need the same", "you don't need the same"),
        ("convincing as someone", "convincing as someone"), ("spending five k", "spending £5,000"),
        ("just stop using the same", "Just stop using the same"), ("content strategy for", "content strategy for"),
        ("two completely", "[TWO COMPLETELY]"), ("different offers", "[DIFFERENT OFFERS.]"),
        ("your content should sell", "Your content should sell"), ("what you're actually", "what you're actually"), ("offering", "*offering*")]
flat = ' '.join(s for s, _ in CAPS).split(); assert flat == [w.lower() for w in words], [(i, a, b) for i, (a, b) in enumerate(zip(flat, [w.lower() for w in words])) if a != b][:3]
CAPS = [(int(i), d) for i, (_, d) in zip([0] + list(np.cumsum([len(s.split()) for s, _ in CAPS])[:-1]), CAPS)]
_f = {wt: instancer.instantiateVariableFont(TTFont('assets/fonts/montserrat-latin-wght.woff2'), {'wght': wt}) for wt in (800, 900)}
def tw(t, size, wt):
    f = _f[wt]; cm = f.getBestCmap(); hm = f['hmtx']; return sum(hm[cm[ord(c)]][0] for c in t) / f['head'].unitsPerEm * size - 0.02 * size * (len(t) - 1)
esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;')
tm = lambda f: round(f / FPS - 0.001, 4) if f > 0 else 0
html, js, sched = [], [], []
for n, (w0, text) in enumerate(CAPS):
    f = 0 if n == 0 else of(w0)
    import re
    segs = re.split(r'(\[[^\]]+\]|\*[^*]+\*)', text); inner = ''; width = 0
    for sg in segs:
        if not sg: continue
        if sg.startswith('['): inner += f'<span class="em">{esc(sg[1:-1])}</span>'; width += tw(sg[1:-1], EM, 900)
        elif sg.startswith('*'): inner += f'<span class="kw">{esc(sg[1:-1])}</span>'; width += tw(sg[1:-1], SIZE, 900)
        else: inner += esc(sg); width += tw(sg, SIZE, 800)
    assert width <= 860, ('caption too wide for the safe zone', text, round(width))
    html.append(f'<div id="cap{n}" class="cap"' + (' style="opacity:1"' if n == 0 else '') + f'><span class="ln">{inner}</span></div>')
    if n: js += [f'tl.set("#cap{n - 1}", {{ opacity: 0 }}, {tm(f)});', f'tl.set("#cap{n}", {{ opacity: 1 }}, {tm(f)});',
                 f'tl.fromTo("#cap{n} .ln", {{ scale: 0.9, y: 8 }}, {{ scale: 1, y: 0, duration: 0.16, ease: "power3.out", immediateRender: false }}, {tm(f)});']
    sched.append(dict(frame=f, text=re.sub(r'[\[\]*]', '', text)))
# ---------------- text overlays: one small card above his head ----------------
OVL = [dict(a=of(30), b=BROLL[0]['a'], big='£5,000', small='AUTHORITY + TRUST'),       # "you need content that builds authority and it builds trust"
       dict(a=of(91), b=BROLL[1]['a'], big='£50', small='ATTENTION + DESIDE')]          # "you need short-form content that grabs attention and it creates desire"
OVL[1]['small'] = 'ATTENTION + DESIRE'
OV_Y, OV_H = 250, 142                                    # card top and height (px): below Instagram's top bar, above his hair (83% of the first cut)
for k, ov in enumerate(OVL):
    html.append(f'<div id="ov{k}" class="ov"><div class="ovc"><div class="ovb">{esc(ov["big"])}</div><div class="ovs">{esc(ov["small"])}</div></div></div>')
    js += [f'tl.set("#ov{k}", {{ opacity: 1 }}, {tm(ov["a"])});',
           f'tl.fromTo("#ov{k} .ovc", {{ scale: 0.9, y: 8 }}, {{ scale: 1, y: 0, duration: 0.18, ease: "power3.out", immediateRender: false }}, {tm(ov["a"])});',
           f'tl.set("#ov{k}", {{ opacity: 0 }}, {tm(ov["b"])});']
    hair = min(anchor[o][1] + (FACE[SRC[o]]['fy'] - 0.42 * (FACE[SRC[o]]['cy'] - FACE[SRC[o]]['fy']) - anchor[o][1]) * zoom[o] for o in range(ov['a'], ov['b']))
    assert hair > OV_Y + OV_H + 12, ('the card would touch his hair', k, round(hair)); ov['hair_min'] = round(hair); ov['n'] = ov['b'] - ov['a']
HOOK = ('YOUR CONTENT IS ATTRACTING', 'THE WRONG BUYERS'); HOOK_N = 60     # the opening text hook, frames 0-59
hs = min(46, int(820 / max(tw(HOOK[0], 1, 900), tw(HOOK[1], 1, 900))))
html.append(f'<div id="hook" class="ov hk" style="opacity:1"><div class="ovc hkc"><div class="hk1" style="font-size:{hs}px">{esc(HOOK[0])}</div><div class="hk2" style="font-size:{hs}px">{esc(HOOK[1])}</div></div></div>')
js.append(f'tl.set("#hook", {{ opacity: 0 }}, {tm(HOOK_N)});')
hook_hair = min(anchor[o][1] + (FACE[SRC[o]]['fy'] - 0.42 * (FACE[SRC[o]]['cy'] - FACE[SRC[o]]['fy']) - anchor[o][1]) * zoom[o] for o in range(HOOK_N))
inb_ = np.zeros(NF, bool)
for r in BROLL: inb_[r['a']:r['b']] = True
chin_out = lambda o: anchor[o][1] + (FACE[SRC[o]]['cy'] - anchor[o][1]) * zoom[o]
LAST_OFF = out_frame(speech_end(W[159]['end'])) + 10      # the last caption clears 1/3 s after "offering": the end frame is just him
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
comp = 'two-offers'; DUR = NF / FPS
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Two offers — Stew Scales</title>
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
    .ov {{ position: absolute; left: 0; width: {CW}px; top: {OV_Y}px; height: {OV_H}px; display: flex; justify-content: center; opacity: 0; }}
    .ovc {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: {OV_H}px; padding: 0 37px; border-radius: 18px; background: rgba(10,10,10,0.80);
           box-shadow: 0 10px 30px rgba(0,0,0,0.35); transform-origin: 50% 50%; }}
    .ovb {{ font-weight: 900; font-size: 70px; line-height: 1; letter-spacing: -0.02em; color: {BLUE}; }}
    .ov.hk {{ height: auto; }}  .hkc {{ height: auto; padding: 22px 34px 24px; }}
    .hk1, .hk2 {{ font-weight: 900; line-height: 1.12; letter-spacing: -0.01em; white-space: nowrap; }}  .hk1 {{ color: {BONE}; }}  .hk2 {{ color: {BLUE}; }}
    .ovs {{ margin-top: 10px; font-weight: 800; font-size: 27px; line-height: 1; letter-spacing: 0.08em; color: {BONE}; }}
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
json.dump({"id": comp, "name": "Two offers", "dimensions": {"width": CW, "height": CH}, "fps": FPS, "createdAt": "2026-11-23T08:00:00.000Z"}, open('meta.json', 'w'), indent=2)
json.dump(dict(comp=comp, fps=FPS, out_size=[CW, CH], frames=NF, shots=SHOTS, out_start=starts[:-1], src=SRC, zoom=[round(float(z), 4) for z in zoom], anchor=anchor,
               broll=BROLL, punch=PUNCH, overlays=OVL, captions=sched), open('scene.json', 'w'))
print(f'frames {NF} ({NF / FPS:.2f} s, from {(END - START) / FPS:.2f} s)  cuts {len(cuts)}  punch {PUNCH}  broll {[(r["kind"], r["a"], r["b"], r["n"]) for r in BROLL]}')
print('hook', hs, 'px; his hair is at', round(hook_hair), 'in the first 2 s'); print('chin below the caption line on', len(over), 'talking-head frames', over[:12])
