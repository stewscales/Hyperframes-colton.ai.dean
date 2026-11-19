"""Generate clips/<id>/index.html (+ hyperframes.json, meta.json) for each short: the full original landscape
frame (assets/base.mp4 = the cut, for Studio preview) + captions. Authored at 1920x1080 and captured at 2x, so the
export is the source's own 3840x2160.
Caption style is the established reel one: Montserrat 800 white, solid dark outline, a few key words in brand
blue, hero size for the line that carries the point. Captions change on the word (30 fps grid) and on cuts.
Run from the project folder: python3 -I scripts/build_comp.py [clip ...]"""
import sys, os, json, math, shutil
exec(open('scripts/shorts.py').read().split("if __name__ == '__main__':")[0])
tm = lambda f: round(f / 30 - 0.001, 4) if f > 0 else 0
FS, FS_HERO = 76, 106                     # caption sizes in the 1920x1080 authoring frame (x2 in the 4K export)
CAP_H = 300; CAP_TOP = 700               # caption block: centred on y = 850, over his chest, clear of his chin and the frame edge
ring = lambda r, c: ', '.join(f'{r*math.cos(x):.2f}px {r*math.sin(x):.2f}px 0 {c}' for x in [2 * math.pi * j / 24 for j in range(24)])
esc = lambda t: t.replace('&', '&amp;').replace('"', '&quot;')
span = lambda line: ' '.join(f'<span class="hl">{esc(w[1:])}</span>' if w.startswith('*') else esc(w) for w in line.split(' '))
HF = {"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
      "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}
for cid in (sys.argv[1:] or list(CLIPS)):
    E = build(cid); NF = E['NF']; DUR = NF / 30; CAPS = captions(E); comp = 't2c-short-' + cid
    on = [c[0] for c in CAPS]; assert on == sorted(on) and len(set(on)) == len(on) and on[0] == 0, on
    caps = [f'  <div id="cap-{i}" class="cap{" hero" if hero else ""}">' + ''.join(f'<span class="ln">{span(l)}</span>' for l in lines) + '</div>' for i, (_, lines, hero, _) in enumerate(CAPS)]
    js = []
    for i, (a, lines, hero, _) in enumerate(CAPS):
        js.append(f'tl.set("#cap-{i}", {{ opacity: 1 }}, {tm(a)});')
        js.append(f'tl.fromTo("#cap-{i}", {{ scale: {0.82 if hero else 0.9} }}, {{ scale: 1, duration: {0.14 if hero else 0.1}, ease: "{"back.out(2.2)" if hero else "power3.out"}", immediateRender: false }}, {tm(a)});')
        if i + 1 < len(CAPS): js.append(f'tl.set("#cap-{i}", {{ opacity: 0 }}, {tm(on[i + 1])});')
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(E['C']['title'])} — Stew Scales</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: 'Montserrat'; src: url('assets/fonts/montserrat-var-subset.woff2') format('woff2'); font-weight: 100 900; font-style: normal; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; }}
    #{comp} {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0a0a0a; }}
    body.capture, body.capture #{comp} {{ background: transparent; }}
    #base {{ position: absolute; top: 0; left: 0; width: 1920px; height: 1080px; object-fit: cover; z-index: 1; }}
    /* Captions: bold, clean, white with a solid dark outline; key words in brand blue */
    .cap {{
      position: absolute; left: 160px; right: 160px; top: {CAP_TOP}px; height: {CAP_H}px;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: {FS}px; line-height: 1.12; letter-spacing: 0.005em;
      text-transform: uppercase; text-align: center; color: #ffffff;
      text-shadow: {ring(FS * 7 / 68, '#0a0a0a')}, {ring(FS * 4 / 68, '#0a0a0a')}, 0 {FS * 8 / 68:.1f}px {FS * 22 / 68:.1f}px rgba(0,0,0,0.55);
      z-index: 20; opacity: 0; transform-origin: 50% 50%;
    }}
    .ln {{ display: block; white-space: nowrap; }}
    .hl {{ color: #2b95ff; }}
    .cap.hero {{ font-weight: 900; font-size: {FS_HERO}px; line-height: 1.07; }}
  </style>
</head>
<body>

<div id="{comp}" data-composition-id="{comp}" data-start="0" data-width="1920" data-height="1080">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base.mp4" data-volume="1"></audio>

{chr(10).join(caps)}

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Times come from forced alignment of the spoken words to the audio, mapped through the cut list (scripts/shorts.py + scripts/build_comp.py)
    {(chr(10) + '    ').join(js)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines["{comp}"] = tl;
  </script>
</div>

</body>
</html>
'''
    d = f'clips/{cid}'; os.makedirs(f'{d}/assets/fonts', exist_ok=True)
    shutil.copyfile('assets/fonts/montserrat-var-subset.woff2', f'{d}/assets/fonts/montserrat-var-subset.woff2')   # each clip stays a self-contained project
    open(f'{d}/index.html', 'w').write(html)
    json.dump(HF, open(f'{d}/hyperframes.json', 'w'), indent=2)
    json.dump({"id": comp, "name": E['C']['title'], "dimensions": {"width": 1920, "height": 1080}, "fps": 30, "createdAt": "2026-11-18T19:00:00.000Z"}, open(f'{d}/meta.json', 'w'), indent=2)
    json.dump([dict(frame=a, lines=l, hero=h) for a, l, h, _ in CAPS], open(f'{d}/captions.json', 'w'))
    print(cid, 'captions', len(CAPS), f'{DUR:.2f}s')
