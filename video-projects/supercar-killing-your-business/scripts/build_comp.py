"""Generate index.html: talking head (assets/base.mp4, audio already mixed) + B-roll clips + hook title +
captions + follow pill. All times come from timeline.py (forced-aligned word starts), on the 30 fps grid.
Caption style is the same as the talking-edit project: Montserrat 800 white, solid dark outline, key words in blue.
Run from the project folder: python3 -I scripts/build_comp.py"""
import math
exec(open('scripts/timeline.py').read())
DUR = NF / 30
tm = lambda f: round(f / 30 - 0.001, 4) if f > 0 else 0          # GSAP time that lands on frame f
# captions: (frame, lines, hero?)   '*' marks blue words: only the key word of the main beats (killing / guru / don't care / trust / wrong / follow)
CAPS = [
 (W('POSTING'),      ['POSTING YOURSELF'], 0),
 (W('IN'),           ['IN A LAMBORGHINI'], 0),
 (W('AND', 0),       ['AND FLASHING', 'YOUR WATCH'], 0),
 (W('IT', 0),        ["IT DOESN'T", 'MAKE PEOPLE'], 0),
 (W('WANT'),         ['WANT TO BUY', 'FROM YOU'], 0),
 (W('IT', 1),        ['IT JUST MAKES', 'YOU LOOK LIKE'], 0),
 (W('EVERY'),        ['EVERY OTHER'], 0),
 (W('TRADING', 0),   ['TRADING *GURU'], 1),
 (W('ONLINE', 0),    ['ONLINE'], 0),
 (W('YOUR', 3),      ['YOUR PROSPECTS'], 0),
 (W("DON'T"),        ["*DON'T *CARE", 'ABOUT YOUR CAR'], 0),
 (W('THEY'),         ['THEY CARE ABOUT'], 0),
 (W('WHETHER'),      ['WHETHER YOU CAN'], 0),
 (W('ACTUALLY', 0),  ['ACTUALLY HELP THEM'], 0),
 (W('THE', 0),       ['THE BEST'], 0),
 (W('TRADING', 1),   ['TRADING COACHES', 'ONLINE'], 0),
 (W("AREN'T"),       ["AREN'T FLEXING"], 0),
 (W('THEIR'),        ['THEIR LIFESTYLE'], 0),
 (W("THEY'RE"),      ["THEY'RE THE ONES"], 0),
 (W('BUILDING'),     ['BUILDING *TRUST'], 1),
 (W('IF'),           ['IF YOUR', 'WHOLE BRAND'], 0),
 (W('IS', 1),        ['IS HOW RICH', 'YOU LOOK'], 0),
 (W("YOU'RE"),       ["YOU'RE POSTING TO"], 0),
 (W('THE', 2),       ['THE *WRONG', 'AUDIENCE'], 1),
 (W('FOLLOW'),       ['*FOLLOW'], 1),
 (W('AND', 1),       ["AND I'LL SHOW YOU"], 0),
 (W('WHAT'),         ['WHAT TO', 'ACTUALLY POST'], 0),
]
on = [f for f, _, _ in CAPS]
assert on == sorted(on) and len(set(on)) == len(on), on
TITLE_END = on[0]                                                  # hook title holds until the first caption
T2, T3 = W('IS', 0, snap=False), W('YOUR', 1, snap=False)          # "IS KILLING", "YOUR BUSINESS"
PILL_ON = W('AND', 1)
def span(line):
    return ' '.join(f'<span class="hl">{w[1:]}</span>' if w.startswith('*') else w for w in line.split(' '))
caps = [f'  <div id="cap-{i}" class="cap{" hero" if hero else ""}">' + ''.join(f'<span class="ln">{span(l)}</span>' for l in lines) + '</div>'
        for i, (_, lines, hero) in enumerate(CAPS)]
js = []
for i, (a, lines, hero) in enumerate(CAPS):
    b = on[i + 1] if i + 1 < len(CAPS) else None
    js.append(f'tl.set("#cap-{i}", {{ opacity: 1 }}, {tm(a)});')
    js.append(f'tl.fromTo("#cap-{i}", {{ scale: {0.82 if hero else 0.9} }}, {{ scale: 1, duration: {0.14 if hero else 0.1}, ease: "{"back.out(2.2)" if hero else "power3.out"}", immediateRender: false }}, {tm(a)});')
    if b is not None: js.append(f'tl.set("#cap-{i}", {{ opacity: 0 }}, {tm(b)});')
# hook title: whole claim readable on frame 0; each line lights up on its word
js += [f'tl.set("#t2", {{ color: "#ffffff" }}, {tm(T2)});', f'tl.set("#t2 .hl", {{ color: "#2b95ff" }}, {tm(T2)});',
       f'tl.fromTo("#t2", {{ scale: 0.86 }}, {{ scale: 1, duration: 0.14, ease: "back.out(2.2)", immediateRender: false }}, {tm(T2)});',
       f'tl.set("#t3", {{ color: "#ffffff" }}, {tm(T3)});',
       f'tl.fromTo("#t3", {{ scale: 0.86 }}, {{ scale: 1, duration: 0.14, ease: "back.out(2.2)", immediateRender: false }}, {tm(T3)});',
       f'tl.set("#title", {{ opacity: 0 }}, {tm(TITLE_END)});',
       f'tl.set("#follow", {{ opacity: 1 }}, {tm(PILL_ON)});',
       f'tl.fromTo("#follow", {{ y: 14, scale: 0.9 }}, {{ y: 0, scale: 1, duration: 0.16, ease: "power3.out", immediateRender: false }}, {tm(PILL_ON)});']
# B-roll clips: start on their frame, end 1 ms before the frame on which the talking head returns
vids = []
for i, (name, a, b) in enumerate(BROLL):
    fo = name in FADES_OUT
    st = round(a / 30 - 0.0004, 4); dur = round((b + (FADE if fo else 0)) / 30 - 0.001 - st, 4)   # a hair early so the clip is up on frame a
    vids.append(f'  <div id="wrap-{name}" class="broll-wrap"><video id="broll-{name}" class="broll" data-start="{st}" data-duration="{dur}" data-track-index="{2 + i % 2}" src="assets/broll/{name}.mp4" muted playsinline></video></div>')
    if fo:   # short dissolve back to the talking head: frames b..b+FADE-1 at falling opacity, gone on frame b+FADE
        js.append(f'tl.to("#wrap-{name}", {{ opacity: 0, duration: {round((FADE + 1) / 30, 4)}, ease: "none" }}, {round((b - 1) / 30, 4)});')
ring = lambda r, c: ', '.join(f'{r*math.cos(x):.2f}px {r*math.sin(x):.2f}px 0 {c}' for x in [2 * math.pi * j / 24 for j in range(24)])
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Your Supercar Is Killing Your Business — Stew Scales</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; }}
    #supercar-killing-your-business {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0a0a0a; }}
    #base {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    .broll-wrap {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; z-index: 5; pointer-events: none; }}
    .broll {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; object-fit: cover; }}

    /* Captions: bold, clean, white with a solid dark outline; key words in brand blue */
    .cap, #title {{
      position: absolute; left: 60px; right: 60px;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      font-family: 'Montserrat', sans-serif; text-transform: uppercase; text-align: center; color: #ffffff;
      z-index: 20; transform-origin: 50% 50%;
    }}
    .cap {{
      top: 1040px; height: 180px; font-weight: 800; font-size: 68px; line-height: 1.12; letter-spacing: 0.005em;
      text-shadow: {ring(7, '#0a0a0a')}, {ring(4, '#0a0a0a')}, 0 8px 22px rgba(0,0,0,0.55);
      opacity: 0;
    }}
    .ln {{ display: block; white-space: nowrap; }}
    .hl {{ color: #2b95ff; }}
    .cap.hero {{ font-weight: 900; font-size: 98px; }}

    /* Hook title: the claim, three lines, same family as the hero captions */
    #title {{
      top: 950px; height: 340px; font-weight: 900; font-size: 104px; line-height: 1.07; letter-spacing: 0.0em;
      text-shadow: {ring(8, '#0a0a0a')}, {ring(5, '#0a0a0a')}, 0 10px 26px rgba(0,0,0,0.6);
    }}
    #title .ln {{ transform-origin: 50% 50%; }}
    #t2, #t3, #t2 .hl {{ color: #7c7c7c; }}   /* not yet spoken: solid grey with the full outline (stays crisp over the white shirt) */

    /* Follow pill on the CTA, sits just above the caption (same pill as the list counters in Reel 2) */
    #follow {{
      position: absolute; left: 50%; top: 936px; margin-left: -245px; width: 490px; height: 70px;
      display: flex; align-items: center; justify-content: center; gap: 16px;
      background: rgba(10,10,10,0.92); border: 2px solid #007fff; border-radius: 999px;
      font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 34px; letter-spacing: 0.06em;
      z-index: 19; opacity: 0;
    }}
    #follow .num {{ color: #2b95ff; }}
    #follow .lab {{ color: #ffffff; }}
  </style>
</head>
<body>

<div id="supercar-killing-your-business" data-composition-id="supercar-killing-your-business" data-start="0" data-width="1080" data-height="1920">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base.mp4" data-volume="1"></audio>

  <!-- B-roll: full-frame, cut in on word starts; clips that return to the talking head dissolve out over 4 frames -->
{chr(10).join(vids)}

  <div id="title">
    <span id="t1" class="ln">YOUR SUPERCAR</span>
    <span id="t2" class="ln">IS <span class="hl">KILLING</span></span>
    <span id="t3" class="ln">YOUR BUSINESS</span>
  </div>

  <div id="follow"><span class="num">FOLLOW</span><span class="lab">@JUDESTEWY</span></div>

{chr(10).join(caps)}

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Times come from forced alignment of the script to the audio (scripts/timeline.py + scripts/build_comp.py)
    {(chr(10) + '    ').join(js)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines["supercar-killing-your-business"] = tl;
  </script>
</div>

</body>
</html>
'''
open('index.html', 'w').write(html)
print('captions', len(CAPS), 'onsets', on); print('title lines at', 0, T2, T3, 'until', TITLE_END, '| follow pill at', PILL_ON)
