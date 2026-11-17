"""Generate index.html: talking head (assets/base.mp4, audio already mixed) + captions.
Caption style is the established one: Montserrat 800 white, solid dark outline, a few key words in brand blue,
hero size for the lines that carry the point. Times are forced-aligned word starts on the 30 fps grid.
Run from the project folder: python3 -I scripts/build_comp.py"""
import math
exec(open('scripts/timeline.py').read())
DUR = NF / 30
tm = lambda f: round(f / 30 - 0.001, 4) if f > 0 else 0
# (frame, lines, hero?)  '*' = blue. Word-for-word what is said. Blue only on: rich / business / matters / converting.
CAPS = [
 (W('COACHES'),      ['COACHES ARE', 'SO FOCUSED'], 0),
 (W('ON', 0),        ['ON TRYING TO', 'LOOK *RICH'], 0),
 (W("THEY'VE"),      ["THEY'VE COMPLETELY", 'FORGOT'], 0),
 (W('HOW'),          ['HOW TO BUILD', 'A *BUSINESS'], 0),
 (W("EVERYONE'S"),   ["EVERYONE'S", 'SO FOCUSED'], 0),
 (W('ON', 1),        ['ON POSTING'], 0),
 (W('THEIR', 0),     ['THEIR WATCHES'], 0),
 (W('AND', 0),       ['AND THEIR CARS'], 0),
 (W('AND', 1),       ['AND THEIR', 'LIFESTYLE'], 0),
 (W('NONE'),         ['NONE OF IT'], 1),
 (W('ACTUALLY'),     ['ACTUALLY', '*MATTERS'], 1),
 (W('BECAUSE'),      ['BECAUSE', 'THE CONTENT'], 0),
 (W("ISN'T"),        ["ISN'T", '*CONVERTING'], 1),
]
on = [f for f, _, _ in CAPS]; assert on == sorted(on) and len(set(on)) == len(on), on
span = lambda line: ' '.join(f'<span class="hl">{w[1:]}</span>' if w.startswith('*') else w for w in line.split(' '))
caps = [f'  <div id="cap-{i}" class="cap{" hero" if hero else ""}">' + ''.join(f'<span class="ln">{span(l)}</span>' for l in lines) + '</div>' for i, (_, lines, hero) in enumerate(CAPS)]
js = []
for i, (a, lines, hero) in enumerate(CAPS):
    js.append(f'tl.set("#cap-{i}", {{ opacity: 1 }}, {tm(a)});')
    js.append(f'tl.fromTo("#cap-{i}", {{ scale: {0.82 if hero else 0.9} }}, {{ scale: 1, duration: {0.14 if hero else 0.1}, ease: "{"back.out(2.2)" if hero else "power3.out"}", immediateRender: false }}, {tm(a)});')
    if i + 1 < len(CAPS): js.append(f'tl.set("#cap-{i}", {{ opacity: 0 }}, {tm(on[i + 1])});')
ring = lambda r, c: ', '.join(f'{r*math.cos(x):.2f}px {r*math.sin(x):.2f}px 0 {c}' for x in [2 * math.pi * j / 24 for j in range(24)])
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Coaches Are So Focused On Trying To Look Rich — Stew Scales</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; }}
    #coaches-looking-rich {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0a0a0a; }}
    #base {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
    /* Captions: bold, clean, white with a solid dark outline; key words in brand blue */
    .cap {{
      position: absolute; left: 60px; right: 60px; top: 1040px; height: 180px;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 68px; line-height: 1.12; letter-spacing: 0.005em;
      text-transform: uppercase; text-align: center; color: #ffffff;
      text-shadow: {ring(7, '#0a0a0a')}, {ring(4, '#0a0a0a')}, 0 8px 22px rgba(0,0,0,0.55);
      z-index: 20; opacity: 0; transform-origin: 50% 50%;
    }}
    .ln {{ display: block; white-space: nowrap; }}
    .hl {{ color: #2b95ff; }}
    .cap.hero {{ font-weight: 900; font-size: 98px; line-height: 1.07; }}
  </style>
</head>
<body>

<div id="coaches-looking-rich" data-composition-id="coaches-looking-rich" data-start="0" data-width="1080" data-height="1920">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base.mp4" data-volume="1"></audio>

{chr(10).join(caps)}

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Times come from forced alignment of the spoken words to the audio (scripts/timeline.py + scripts/build_comp.py)
    {(chr(10) + '    ').join(js)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines["coaches-looking-rich"] = tl;
  </script>
</div>

</body>
</html>
'''
open('index.html', 'w').write(html)
print('captions', len(CAPS), 'onsets', on)
