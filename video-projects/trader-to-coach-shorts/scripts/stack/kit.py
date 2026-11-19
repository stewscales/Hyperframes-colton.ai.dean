"""Shared kit for the stacked 1080x1920 shorts: layout constants, caption / title / behind-the-head text helpers and
page assembly. A clip's scene file (scripts/stack/clip_XX.py) builds a Scene and calls scene.write().

Layout (canvas px):   title zone 190-340  |  video panel 1080x1080 at y=360 (square crop of the 4K frame, no upscale;
its top and bottom fade into the dark canvas)  |  card zone 1250-1580 (kept clear of the apps' own buttons below ~1600).
Two graphic layers: #behind is composited BEHIND him (masked by a person matte in scripts/stack/render.py),
#front goes on top of everything. Times are frames at 30 fps; a tl.set at frame f is placed at f/30 - 0.001."""
import json, os, shutil, numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
exec(open('scripts/shorts.py').read().split("if __name__ == '__main__':")[0])
CW, CH, PY, PS = 1080, 1920, 360, 1080
BLUE, BONE, INK = '#2F6FED', '#F2EFE9', '#0A0A0A'
tm = lambda f: round(f / 30 - 0.001, 4) if f > 0 else 0
esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;')
def rich(t):
    """'*word*' -> brand-blue span, '|' -> line break."""
    out = []
    for line in t.split('|'):
        parts = line.split('*'); out.append('<span class="ln">' + ''.join(esc(p) if i % 2 == 0 else f'<span class="hl">{esc(p)}</span>' for i, p in enumerate(parts)) + '</span>')
    return ''.join(out)

_adv = {}
def text_width(text, size, weight=900, tracking=-0.035):
    """Rendered width in px of one line of Montserrat at this weight (advance widths from the font itself)."""
    if weight not in _adv:
        f = instancer.instantiateVariableFont(TTFont('assets/fonts/montserrat-latin-wght.woff2'), {'wght': weight}); cm = f.getBestCmap(); hm = f['hmtx']
        _adv[weight] = ({c: hm[g][0] for c, g in cm.items()}, f['head'].unitsPerEm)
    adv, upm = _adv[weight]
    return sum(adv[ord(c)] for c in text) / upm * size + tracking * size * (len(text) - 1)

class Scene:
    def __init__(self, cid, title):
        self.cid, self.title = cid, title; self.E = build(cid); self.NF = self.E['NF']; self.wl = dict(word_list(self.E))
        self.geom = json.load(open(f'clips/{cid}/geom.json')); self.behind, self.front, self.js, self.css, self.sfx = [], [], [], [], []
        self.cuts = self.E['starts'][1:-1]
        self.match = None                                   # dict(ref=<snippet>, strength=0..1): colour-match the other snippets to this one
    def F(self, wi, d=0): return self.wl[wi] + d                       # output frame on which a spoken word starts
    def head(self, si=0):
        g = self.geom[si]; fh = g['chin_y'] - g['forehead_y']
        return dict(cx=g['nose'][0], top=PY + g['forehead_y'] - 0.30 * fh, forehead=PY + g['forehead_y'], chin=PY + g['chin_y'], left=g['face_x'][0], right=g['face_x'][1], fh=fh)
    # ---- pinned title above the panel ----
    def pinned_title(self, line1, bar, f0=3, f1=None):
        """Two-line title above the panel (second line in the blue bar). Call again for a second title later in the clip."""
        i = sum(1 for x in self.front if 'class="ttl' in x); t = f'#ttl{i}'
        if f0 == 0:                                         # the opening title is already there on the very first frame (it is the cover frame)
            self.front.append(f'<div id="ttl{i}" class="ttl on"><div class="t1">{esc(line1)}</div><div class="t2"><span>{esc(bar)}</span></div></div>')
            if f1: self.js.append(f'tl.to("{t}", {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, {tm(f1 - 4)});')
            return
        self.front.append(f'<div id="ttl{i}" class="ttl"><div class="t1">{esc(line1)}</div><div class="t2"><span>{esc(bar)}</span></div></div>')
        self.js += [f'tl.set("{t}", {{ opacity: 1 }}, {tm(f0)});',
                    f'tl.fromTo("{t} .t1", {{ y: -18, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {tm(f0)});',
                    f'tl.fromTo("{t} .t2", {{ scaleX: 0.6, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, {tm(f0 + 3)});']
        if f1: self.js.append(f'tl.to("{t}", {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, {tm(f1 - 4)});')
    # ---- captions: small, sentence case; they move between spots around him ----
    ENTER = {'chest': '{ y: 16, filter: "blur(7px)" }', 'low': '{ y: 16, filter: "blur(7px)" }', 'left': '{ x: -26, filter: "blur(7px)" }', 'right': '{ x: 26, filter: "blur(7px)" }', 'top': '{ y: -16, filter: "blur(7px)" }'}
    def captions(self, items):
        """items: (frame, text, spot[, last frame]); spot = chest | left | right | top | low. A caption stays until the next one."""
        items = sorted(items, key=lambda c: c[0])
        for i, c in enumerate(items):
            f, text, spot = c[:3]; end = c[3] if len(c) > 3 else (items[i + 1][0] if i + 1 < len(items) else None)
            side = spot in ('left', 'right')                    # nothing may run off the frame or into his face
            for ln in text.replace('*', '').split('|'):
                w = text_width(ln, 46 if side else 52, 800 if side else 700, -0.03); assert w <= (360 if side else 980), f'caption line too wide for the {spot} spot ({w:.0f}px): {ln!r}'
            self.front.append(f'<div id="cap{i}" class="cap {spot}"' + (' style="opacity:1"' if f == 0 else '') + f'>{rich(text)}</div>')
            self.js += ([] if f == 0 else [f'tl.set("#cap{i}", {{ opacity: 1 }}, {tm(f)});',
                        f'tl.fromTo("#cap{i}", {self.ENTER[spot]}, {{ x: 0, y: 0, filter: "blur(0px)", duration: 0.2, ease: "power3.out", immediateRender: false }}, {tm(f)});'
                        ]) + ([f'tl.set("#cap{i}", {{ opacity: 0 }}, {tm(end)});'] if end is not None and end < self.NF else [])
        self.caps = items
    # ---- big word(s) behind his head ----
    def behind_text(self, f0, f1, left=None, right=None, color=BLUE, si=0, max_size=150, stagger=3, tuck=2):
        """Heavy caps either side of his head at forehead height, each word tucked a little way behind him (the matte hides the
        tucked part) and following his head as it moves, so the tuck stays the same. Both words share one size: the largest at
        which each fits its side of the frame."""
        g = self.geom[si]; fh = g['chin_y'] - g['forehead_y']; cy = PY + g['forehead_y'] - 0.10 * fh; end = f1 if f1 is not None else self.NF
        trk = [t for t in g['head_track'] if f0 - 5 <= t[0] <= end + 5] or g['head_track']; cuts = set(self.E['starts'])
        sm = [(t[0], float(t[1]), float(t[2])) for t in trk]
        L0, R0 = min(t[1] for t in sm) + tuck, max(t[2] for t in sm) - tuck          # tightest spot on each side sets the size
        fit = [(L0 - 30) / text_width(w.upper(), 1) for w in [left] if w] + [(CW - 30 - R0) / text_width(w.upper(), 1) for w in [right] if w]
        size = int(min(max_size, min(fit)))
        for n, (w, side) in enumerate([(left, 'l'), (right, 'r')]):
            if not w: continue
            i = len(self.behind); col = 1 if side == 'l' else 2; x0 = sm[0][col] + (tuck if side == 'l' else -tuck)
            pos = f'right:{CW - x0:.1f}px' if side == 'l' else f'left:{x0:.1f}px'
            self.behind.append(f'<div id="bh{i}" class="bh" style="top:{cy - size / 2:.0f}px; {pos}; font-size:{size}px; color:{color}"><span id="bh{i}i" class="bhi">{esc(w)}</span></div>')
            fa = f0 + (stagger * n if left and right else 0); dx = 90 if side == 'l' else -90          # slides out from behind his head
            self.js += [f'tl.set("#bh{i}", {{ opacity: 1 }}, {tm(fa)});',
                        f'tl.fromTo("#bh{i}i", {{ x: {dx}, scale: 0.86 }}, {{ x: 0, scale: 1, duration: 0.34, ease: "back.out(1.6)", immediateRender: false }}, {tm(fa)});'
                        ] + ([f'tl.to("#bh{i}", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {tm(f1 - 4)});'] if f1 is not None else [])
            for (fa_, la, ra), (fb_, lb, rb) in zip(sm[:-1], sm[1:]):                                   # follow his head
                v = (lb if side == 'l' else rb) - sm[0][col]
                if any(fa_ < c <= fb_ for c in cuts): self.js.append(f'tl.set("#bh{i}", {{ x: {v:.1f} }}, {tm(fb_)});')
                else: self.js.append(f'tl.to("#bh{i}", {{ x: {v:.1f}, duration: {(fb_ - fa_) / 30:.4f}, ease: "none" }}, {tm(fa_)});')
    def sound(self, frame, name, gain_db):
        """gain_db = peak level of the effect in dBFS (the voice peaks at about -1.5): clicks about -11, pops -13, whooshes -15."""
        self.sfx.append(dict(frame=int(frame), file=name, gain_db=gain_db))
    # ---- page ----
    def write(self):
        cid = self.cid; comp = 't2c-short-' + cid; DUR = self.NF / 30; d = f'clips/{cid}'
        os.makedirs(f'{d}/assets/fonts', exist_ok=True); shutil.copyfile('assets/fonts/montserrat-latin-wght.woff2', f'{d}/assets/fonts/montserrat-latin-wght.woff2')
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(self.title)} — Stew Scales</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: 'Montserrat'; src: url('assets/fonts/montserrat-latin-wght.woff2') format('woff2'); font-weight: 100 900; font-style: normal; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #000; }}
    #{comp} {{ position: relative; width: {CW}px; height: {CH}px; overflow: hidden; background: {INK}; font-family: 'Montserrat', sans-serif; }}
    #base {{ position: absolute; top: 0; left: 0; width: {CW}px; height: {CH}px; object-fit: cover; z-index: 1; }}
    #behind, #front {{ position: absolute; inset: 0; }}
    #behind {{ z-index: 2; }}  #front {{ z-index: 3; }}
    /* capture passes (scripts/stack/capture.js): one layer at a time on a transparent page */
    body.capture, body.capture #{comp} {{ background: transparent; }}
    body.capture.pass-behind #front, body.capture.pass-front #behind {{ display: none; }}
    .hl {{ color: {BLUE}; }}
    .ln {{ display: block; white-space: nowrap; }}
    /* pinned title */
    .ttl {{ position: absolute; left: 0; width: {CW}px; top: {PY - 172}px; text-align: center; opacity: 0; }}
    .ttl .t1 {{ font-weight: 600; font-size: 44px; letter-spacing: -0.02em; color: {BONE}; opacity: 0; }}
    .ttl .t2 {{ margin-top: 10px; transform-origin: 50% 50%; opacity: 0; }}
    .ttl.on, .ttl.on .t1, .ttl.on .t2 {{ opacity: 1; }}
    .ttl .t2 span {{ display: inline-block; background: {BLUE}; color: #fff; font-weight: 800; font-size: 50px; letter-spacing: -0.025em; padding: 6px 22px 8px; border-radius: 10px; }}
    /* captions */
    .cap {{ position: absolute; font-weight: 700; font-size: 52px; line-height: 1.12; letter-spacing: -0.03em; color: #fff; text-align: center; opacity: 0;
           text-shadow: 0 2px 5px rgba(0,0,0,0.7), 0 0 20px rgba(0,0,0,0.55), 0 0 46px rgba(0,0,0,0.4); }}
    .cap.chest {{ left: 0; width: {CW}px; top: {PY + 690}px; }}
    .cap.low {{ left: 0; width: {CW}px; top: {PY + 780}px; }}
    .cap.top {{ left: 0; width: {CW}px; top: {PY + 36}px; }}
    .cap.left {{ left: 20px; width: 360px; top: {PY + 330}px; font-size: 46px; font-weight: 800; }}
    .cap.right {{ left: 700px; width: 360px; top: {PY + 330}px; font-size: 46px; font-weight: 800; }}
    /* big word behind his head */
    .bh {{ position: absolute; font-weight: 900; line-height: 1; letter-spacing: -0.035em; text-transform: uppercase; white-space: nowrap; opacity: 0;
          text-shadow: 0 6px 30px rgba(0,0,0,0.35); }}
    .bhi {{ display: inline-block; }}
    /* cards */
    .card {{ position: absolute; left: 60px; width: 900px; top: {PY + 894}px; height: 322px; border-radius: 34px; background: rgba(17,17,19,0.96); border: 1.5px solid rgba(242,239,233,0.14);
            box-shadow: 0 26px 70px rgba(0,0,0,0.55); opacity: 0; padding: 30px 32px; color: {BONE}; }}
    .card .lab {{ font-weight: 700; font-size: 24px; letter-spacing: 0.16em; text-transform: uppercase; color: rgba(242,239,233,0.55); }}
{chr(10).join(self.css)}
  </style>
</head>
<body>

<div id="{comp}" data-composition-id="{comp}" data-start="0" data-width="{CW}" data-height="{CH}">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base.mp4" data-volume="1"></audio>

  <div id="behind">
{chr(10).join('    ' + x for x in self.behind)}
  </div>
  <div id="front">
{chr(10).join('    ' + x for x in self.front)}
  </div>

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Generated by scripts/stack/ (frames at 30 fps; word times from forced alignment mapped through the cut list)
    {(chr(10) + '    ').join(self.js)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines["{comp}"] = tl;
  </script>
</div>

</body>
</html>
'''
        open(f'{d}/index.html', 'w').write(html)
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}, open(f'{d}/hyperframes.json', 'w'), indent=2)
        json.dump({"id": comp, "name": self.title, "dimensions": {"width": CW, "height": CH}, "fps": 30, "createdAt": "2026-11-19T04:00:00.000Z"}, open(f'{d}/meta.json', 'w'), indent=2)
        json.dump(dict(match=self.match, sfx=sorted(self.sfx, key=lambda s: s['frame']), captions=[dict(frame=c[0], text=c[1], spot=c[2]) for c in self.caps]), open(f'{d}/scene.json', 'w'), indent=1)
        print(cid, 'scene written:', len(self.caps), 'captions,', len(self.behind), 'behind-head words,', len(self.sfx), 'sounds')
