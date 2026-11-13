"""Generate index.html (captions + list pills over assets/base.mp4) from the forced-alignment word times."""
import json, math
al = json.load(open('assets/align.json'))
NF = 995; DUR = NF / 30
starts = {}
for w in al: starts.setdefault(w['word'], []).append(w['start'])
def t(word, k=0): return starts[word][k]
# (start word, occurrence, lines, hero?)   '*' marks blue words
C = [
 ('SCROLL', 0, ['SCROLL YOUR', '*INSTAGRAM'], 0),
 ('IF', 0, ["IF IT'S JUST", 'YOUR *CARS'], 0),
 ('AND', 0, ['AND YOUR', '*WATCHES'], 0),
 ('AND', 1, ['AND YOUR', '*FANCY *DINNERS'], 0),
 ('JUST', 1, ['JUST THE', '*SAME *POST'], 0),
 ('TEN', 0, ['*10 *TIMES'], 1),
 ('IF', 1, ["IF THAT'S YOU"], 0),
 ('YOUR', 4, ['YOUR AUDIENCE'], 0),
 ('WILL', 0, ['WILL LEARN', '*ONE *THING'], 0),
 ('ABOUT', 0, ['ABOUT YOU'], 0),
 ('AND', 2, ['AND THEN JUST'], 0),
 ('LOSE', 0, ['*LOSE *ATTENTION'], 0),
 ('AND', 3, ["AND THAT'S", 'THE *PROBLEM'], 0),
 ('SO', 0, ["SO HERE'S", 'THE *FIX'], 0),
 ('FOUR', 0, ['*4 *TYPES', 'OF POSTS'], 0),
 ('FIRST', 0, ['FIRST'], 0),
 ('TEACH', 0, ['*TEACH'], 1),
 ('ONE', 1, ['ONE CONCEPT'], 0),
 ('THIRTY', 0, ['*30 *SECONDS'], 0),
 ('NEXT', 0, ['NEXT'], 0),
 ('THE', 3, ['THE *PROCESS'], 1),
 ('HOW', 0, ['HOW YOU PLAN'], 0),
 ('AND', 4, ['AND REVIEW'], 0),
 ('YOUR', 5, ['YOUR TRADES'], 0),
 ('NOT', 0, ['NOT JUST', 'YOUR *WINS'], 0),
 ('THIRD', 0, ['THIRD'], 0),
 ('YOUR', 7, ['YOUR *STORY'], 1),
 ('WHERE', 0, ['WHERE DID', 'YOU START?'], 0),
 ('WHERE', 1, ['WHERE ARE', 'YOU NOW?'], 0),
 ('AND', 5, ['AND HOW', 'EXACTLY'], 0),
 ('DID', 1, ['DID YOU', 'GET THERE?'], 0),
 ('FINALLY', 0, ['FINALLY'], 0),
 ('YOUR', 8, ['YOUR *OPINION'], 1),
 ('WHAT', 0, ['WHAT DOES THIS'], 0),
 ('INDUSTRY', 0, ['INDUSTRY', 'GET *WRONG?'], 0),
 ('A', 0, ['A *SKEPTICAL', 'AUDIENCE'], 0),
 ('NEEDS', 0, ['NEEDS', '*4 *REASONS'], 0),
 ('TO', 0, ['TO *TRUST YOU'], 0),
 ('NOT', 1, ['*NOT *1'], 1),
 ('SAVE', 0, ['*SAVE *THIS'], 1),
 ('AND', 6, ['AND CHECK YOUR'], 0),
 ('LAST', 0, ['LAST *10 *POSTS'], 0),
]
PILLS = [('01', 'TEACH', ('TEACH', 0), ('NEXT', 0)), ('02', 'PROCESS', ('THE', 3), ('THIRD', 0)),
         ('03', 'STORY', ('YOUR', 7), ('FINALLY', 0)), ('04', 'OPINION', ('YOUR', 8), ('A', 0))]
# cut points (output frames): a caption that starts within 4 frames after a cut switches exactly on the cut
_e = json.load(open('assets/edl.json')); CUTS = []; _t = 0
for _s in _e['segs']:
    CUTS.append(_t); _t += _s['src'][1] - _s['src'][0]
def fr(s):
    f = max(0, int(math.floor(s * 30 + 1e-6)))
    for c in CUTS:
        if 0 <= f - c <= 4: return c
    return f
tm = lambda f: round(f / 30 - 0.001, 4) if f > 0 else 0
on = [fr(t(w, k)) for w, k, _, _ in C]; on[0] = 0
assert on == sorted(on) and len(set(on)) == len(on), on
def span(line):
    out = []
    for w in line.split(' '):
        out.append(f'<span class="hl">{w[1:]}</span>' if w.startswith('*') else w)
    return ' '.join(out)
caps = []
for i, (w, k, lines, hero) in enumerate(C):
    inner = ''.join(f'<span class="ln">{span(l)}</span>' for l in lines)
    caps.append(f'  <div id="cap-{i}" class="cap{" hero" if hero else ""}">{inner}</div>')
pills = [f'  <div id="pill-{i}" class="pill"><span class="num">{n}</span><span class="lab">{lab}</span></div>' for i, (n, lab, _, _) in enumerate(PILLS)]
js = []
for i in range(len(C)):
    a = on[i]; b = on[i + 1] if i + 1 < len(C) else None
    hero = C[i][3]
    if i == 0:
        js.append('tl.set("#cap-0", { opacity: 1, scale: 1 }, 0);')
    else:
        s0 = 0.82 if hero else 0.9
        ease = 'back.out(2.2)' if hero else 'power3.out'
        js.append(f'tl.set("#cap-{i}", {{ opacity: 1 }}, {tm(a)});')
        js.append(f'tl.fromTo("#cap-{i}", {{ scale: {s0} }}, {{ scale: 1, duration: {0.14 if hero else 0.1}, ease: "{ease}", immediateRender: false }}, {tm(a)});')
    if b is not None: js.append(f'tl.set("#cap-{i}", {{ opacity: 0 }}, {tm(b)});')
for i, (n, lab, (w0, k0), (w1, k1)) in enumerate(PILLS):
    a = fr(t(w0, k0)); b = fr(t(w1, k1))
    js.append(f'tl.set("#pill-{i}", {{ opacity: 1 }}, {tm(a)});')
    js.append(f'tl.fromTo("#pill-{i}", {{ y: 14, scale: 0.9 }}, {{ y: 0, scale: 1, duration: 0.16, ease: "power3.out", immediateRender: false }}, {tm(a)});')
    js.append(f'tl.set("#pill-{i}", {{ opacity: 0 }}, {tm(b)});')
ring = lambda r, c: ', '.join(f'{r*math.cos(a):.2f}px {r*math.sin(a):.2f}px 0 {c}' for a in [2 * math.pi * j / 24 for j in range(24)])
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Reel 2: The 4 Posts Every Trading Coach Needs — Stew Scales</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; }}
    #talking-edit {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0a0a0a; }}
    #base {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}

    /* Captions: bold, clean, white with a solid dark outline; key words in brand blue */
    .cap {{
      position: absolute; left: 60px; right: 60px; top: 1040px; height: 180px;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 68px; line-height: 1.12;
      letter-spacing: 0.005em; text-transform: uppercase; text-align: center; color: #ffffff;
      text-shadow: {ring(7, '#0a0a0a')}, {ring(4, '#0a0a0a')}, 0 8px 22px rgba(0,0,0,0.55);
      z-index: 20; opacity: 0; transform-origin: 50% 50%;
    }}
    .cap .ln {{ display: block; white-space: nowrap; }}
    .cap .hl {{ color: #2b95ff; }}
    .cap.hero {{ font-weight: 900; font-size: 98px; }}

    /* List counter pill (01-04), sits just above the caption */
    .pill {{
      position: absolute; left: 50%; top: 948px; margin-left: -170px; width: 340px; height: 62px;
      display: flex; align-items: center; justify-content: center; gap: 14px;
      background: rgba(10,10,10,0.92); border: 2px solid #007fff; border-radius: 999px;
      font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 32px; letter-spacing: 0.08em;
      z-index: 19; opacity: 0;
    }}
    .pill .num {{ color: #2b95ff; }}
    .pill .lab {{ color: #ffffff; }}
  </style>
</head>
<body>

<div id="talking-edit" data-composition-id="talking-edit" data-start="0" data-width="1080" data-height="1920">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base.mp4" data-volume="1"></audio>

{chr(10).join(pills)}

{chr(10).join(caps)}

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Caption/pill times come from forced alignment of the script to the audio (scripts/build_captions.py)
    {(chr(10) + '    ').join(js)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines["talking-edit"] = tl;
  </script>
</div>

</body>
</html>
'''
open('index.html', 'w').write(html)
print('chunks', len(C), 'onsets', on)
