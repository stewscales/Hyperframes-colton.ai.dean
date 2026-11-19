"""02 — The bucket (stacked layout). ONE graphic for the whole reel: a bucket that lives on the left of the card and does
everything he describes, with a small panel beside it that names what is happening. With the sound off the bucket alone
tells it:
  HOOK          headline + the empty bucket on screen from the first frame; "Bucket = Your business", the first drops fall,
                "Water = People"
  FIRST 30 DAYS drops keep falling (by hand), the level climbs while a Day 1 -> 30 bar runs; "Fill the bucket"
  LEAKS         holes open in the sides and water runs out ("LEAKS" behind his head); "Leaks are normal" tick,
                "A perfect bucket" cross, "Fill the biggest holes" tick: the two big holes are patched, the small ones still drip
  ADS = HOSE    the hose arrives ("ADS | HOSE" behind his head); by hand = slow drops, then the hose is turned on and the level
                races up; good bucket (every hole patched) -> full -> "Great"; leaky bucket -> the patches come off, it gushes,
                the puddle spreads -> "Wet floor" ("WET | FLOOR" behind his head)
  THE ORDER     the list starts backwards (hose first, cross), then re-orders itself: 1 Fill the bucket, 2 Fill the biggest
                holes, 3 Hose (ads); on the left the bucket is patched again, the puddle goes and it fills. Last frame: glow.
Camera as in clip 01: slow drift in every shot, tighter frame on alternate jump cuts, small punch-ins on the key words and
a zoom-through (with a whoosh) on the section changes. Nothing is cut or re-timed.
Run from the project folder: python3 -I scripts/stack/clip_02.py"""
import math
exec(open('scripts/stack/kit.py').read())
s = Scene('02-the-bucket', 'The bucket')
exec(open('scripts/stack/hook.py').read())
ST = s.E['starts']; NF = s.NF; DUR = NF / 30
B1, C1, C2, C3 = F(258), F(749), F(1378), F(1729)       # hook | first 30 days | leaks | hose | the order
assert len(ST) == 12 and (ST[2], ST[3], ST[5], ST[10]) == (B1, C1, C2, C3), ST
s.match = dict(ref=0, strength=0.8, only=[2, 3])        # the hose and the ending were shot later in the recording (warmer, brighter wall)
s.pinned_title('Before you run ads', 'picture a bucket', 0, B1, big=True)
s.pinned_title('Your first job', 'fill the bucket', B1, C1)
s.pinned_title('It will leak', 'fill the biggest holes', C1, C2)
s.pinned_title('Think of ads', 'as a hose', C2, C3)
s.pinned_title('Know the right order', 'bucket before hose', C3)

s.captions([
    (0,        "First, let's",                  'chest'),
    (F(242),   'picture a *bucket*',            'chest'),
    (F(245),   'Your *business*',               'chest'),
    (F(247),   'is the *bucket*',               'chest'),
    (F(250),   'and then',                      'right'),
    (F(252),   'we have *water*',               'chest'),
    (F(255),   "the water's *people*",          'chest'),
    (B1,       'First *30 days*',               'chest'),
    (F(261),   'your job is',                   'chest'),
    (F(264),   'to *fill* this bucket',         'chest'),
    (F(268),   'with the water',                'chest'),
    (C1,       'And every bucket',              'chest', F(752)),         # then "LEAKS" behind his head
    (F(753),   'Yours will too',                'chest'),
    (F(756),   "and that's",                    'left'),
    (F(758),   'completely *normal*',           'chest'),
    (F(760),   "We're not trying",              'chest'),
    (F(763),   'to build a',                    'chest'),
    (F(766),   '*perfect* bucket',              'chest'),
    (F(768),   "we're trying to",               'chest'),
    (F(771),   'fill the',                      'chest'),
    (F(773),   '*biggest holes*',               'chest'),
    (C2,       'Think of',                      'chest', F(1380)),        # then "ADS | HOSE" behind his head
    (F(1384),  'Up to now',                     'right'),
    (F(1387),  "you've been filling",           'chest'),
    (F(1390),  'the bucket',                    'chest'),
    (F(1392),  'by *hand*',                     'chest'),
    (F(1394),  'A *hose* does it',              'chest'),
    (F(1398),  'a lot *faster*',                'chest'),
    (F(1401),  'A hose on',                     'chest'),
    (F(1404),  'a *good* bucket',               'chest'),
    (F(1407),  "that's *great*",                'chest'),
    (F(1409),  'A hose on',                     'chest'),
    (F(1412),  'a *leaky* bucket',              'chest'),
    (F(1415),  "we've got a",                   'chest', F(1418)),        # then "WET | FLOOR" behind his head
    (C3,       'Most people',                   'left'),
    (F(1731),  'do it *backwards*',             'chest'),
    (F(1734),  "they'll buy",                   'chest'),
    (F(1736),  'the *hose first*',              'chest'),
    (F(1739),  'but now you know',              'chest'),
    (F(1743),  'the *right order*',             'chest'),
])

# ================= CAMERA =================
s.shot(ST[0], ST[1], 1.00, 1.02)
for k in range(10): s.zoom[k] += 0.05 * (1 - k / 10) ** 2        # the first frames settle back with the headline
s.shot(ST[1], ST[2], 1.05, 1.07)                        # "your business is the bucket": tighter
s.shot(ST[2], ST[3], 1.00, 1.03);  s.punch(F(265), ST[3], 0.03)  # punch on "fill"
s.shot(ST[3], ST[4], 1.02, 1.04);  s.punch(F(752), ST[4], 0.04)  # punch on "leaks"
s.shot(ST[4], ST[5], 1.00, 1.03);  s.punch(F(773), ST[5], 0.04)  # punch on "biggest holes"
s.shot(ST[5], ST[6], 1.02, 1.04);  s.punch(F(1383), ST[6], 0.04) # punch on "hose"
s.shot(ST[6], ST[7], 1.00, 1.02)
s.shot(ST[7], ST[8], 1.06, 1.08)                        # "a lot faster": tighter
s.shot(ST[8], ST[9], 1.00, 1.02)
s.shot(ST[9], ST[10], 1.05, 1.06); s.punch(F(1418), ST[10], 0.05)   # punch on "wet floor"
s.shot(ST[10], ST[11], 1.00, 1.03); s.punch(F(1743), ST[11], 0.04)  # punch on "the right order"
for c in (C1, C2, C3):                                  # section changes: zoom through the cut
    s.through(c, 0.06); s.sound(c, 'transitions/whoosh.mp3', -15)
assert s.zoom.max() <= 1.2 and s.zoom.min() >= 1.0, (s.zoom.min(), s.zoom.max())
s.behind_text(F(752), F(755), None, 'leaks', si=1)
s.behind_text(F(1380), ST[6], 'ads', 'hose', si=2, stagger=F(1383) - F(1380))
s.behind_text(F(1418), C3, 'wet', 'floor', si=2, stagger=F(1419) - F(1418))

J = s.js.append
def at(f, d=0): return round(tm(f) + d / 30, 4)
def pop(sel, f, d=0, frm='{ opacity: 0, scale: 0.4 }', dur=0.22, ease='back.out(2.4)'):
    J(f'tl.fromTo("{sel}", {frm}, {{ opacity: 1, scale: 1, x: 0, y: 0, duration: {dur}, ease: "{ease}", immediateRender: false }}, {at(f, d)});')
def glow(sel, f, d=0):
    J(f'tl.to("{sel}", {{ borderColor: "rgba(47,111,237,0.8)", boxShadow: "0 26px 70px rgba(0,0,0,0.55), 0 0 64px rgba(47,111,237,0.38)", duration: 0.3, ease: "power2.out" }}, {at(f, d)});')
    J(f'tl.fromTo("{sel}", {{ scale: 1 }}, {{ scale: 1.018, duration: 0.14, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(f, d)});')
def shake(sel, f, amp=10):
    for j, dx in enumerate([-amp, 0.8 * amp, -0.5 * amp, 0.3 * amp, 0]): J(f'tl.to("{sel}", {{ x: {dx:.1f}, duration: 0.05, ease: "power1.inOut" }}, {at(f, 1.5 * j)});')
def swap(a, b, f):                                      # the panel beside the bucket changes; the bucket stays
    if a: J(f'tl.to("{a}", {{ opacity: 0, y: -16, duration: 0.14, ease: "power2.in" }}, {at(f, -4)});')
    J(f'tl.fromTo("{b}", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power3.out", immediateRender: false }}, {at(f)});')
def tick(sel, f, d=0, snd=-11):
    J(f'tl.to("{sel}", {{ backgroundColor: "{BLUE}", color: "#ffffff", duration: 0.14 }}, {at(f, d)});')
    J(f'tl.fromTo("{sel}", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.22, ease: "back.out(2.8)", immediateRender: false }}, {at(f, d)});')
    if snd: s.sound(f + d, 'ui/click.wav', snd)

# ================= THE BUCKET (svg, 330 x 352, 1 unit = 1 px of the card) =================
YB, HW = 313, 172                                       # inside bottom of the bucket; height of a full bucket of water
Y = lambda L: round(YB - HW * L, 1)                     # y of the water surface at level L (0..1)
LV = [(0, -0.07), (F(254), -0.07), (140, 0.08), (165, 0.08), (240, 0.62), (F(752) + 2, 0.62), (F(771), 0.50), (F(774) + 2, 0.48), (F(1387), 0.47), (590, 0.53),
      (600, 0.53), (640, 0.84), (F(1404), 0.86), (F(1408), 0.97), (F(1413) + 2, 0.97), (C3, 0.62), (F(1739), 0.50), (F(1739) + 5, 0.50), (890, 0.95)]
assert all(a[0] < b[0] for a, b in zip(LV, LV[1:])), LV
def lv(f):
    for (f0, a), (f1, b) in zip(LV, LV[1:]):
        if f0 <= f <= f1: return a + (b - a) * (f - f0) / (f1 - f0)
    return LV[-1][1]
for (f0, a), (f1, b) in zip(LV, LV[1:]):
    if a != b: J(f'tl.to("#wg", {{ y: {Y(b)}, duration: {(f1 - f0) / 30:.4f}, ease: "sine.inOut" }}, {at(f0)});')
WAVE = 'M-120,0 ' + 'q15,-6 30,0 t30,0 ' * 8
TEAR = 'M0,-11 C5,-4 7.5,0 7.5,4 A7.5,7.5 0 1 1 -7.5,4 C-7.5,0 -5,-4 0,-11Z'
edge = lambda y, side: (47 + 30 * (y - 128) / 190) if side < 0 else (283 - 30 * (y - 128) / 190)
HOLES = [(-1, 262, 10), (1, 250, 10), (-1, 298, 6), (1, 294, 6)]            # (side, y, radius): two big, two small
def leak_path(side, y, r):
    x = edge(y, side); reach = 36 if r > 8 else 20
    return f'M{x:.1f},{y} q{side * reach * 0.75:.1f},3 {side * reach:.1f},{322 - y}'
svg = ['<svg id="bk" class="bk" viewBox="0 0 330 352" width="330" height="352">',
       '<defs><clipPath id="bkclip"><path d="M52,138 L278,138 L249,309 Q248,313 243,313 L87,313 Q82,313 81,309 Z"/></clipPath></defs>',
       f'<g id="pud" opacity="0"><ellipse cx="165" cy="325" rx="150" ry="11" fill="{BLUE}"/><ellipse cx="150" cy="322" rx="96" ry="3.5" fill="rgba(255,255,255,0.28)"/></g>',
       '<path d="M47,128 L283,128 L253,310 Q252,318 244,318 L86,318 Q78,318 77,310 Z" fill="#1B1C21"/>',
       f'<g id="hs" opacity="0"><path id="hsb" d="M143,72 Q160,84 165,128 L165,313" fill="none" stroke="{BLUE}" stroke-width="14" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
       '<path class="flow" d="M143,72 Q160,84 165,128 L165,313" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="4" stroke-linecap="round" stroke-dasharray="10 14"/></g>']
drops = []                                              # (frame, x): one element each
drops += [(f, 165) for f in (F(254), F(254) + 9, F(254) + 18, F(254) + 27)]
drops += [(f, 165 + (6 if i % 2 else -6)) for i, f in enumerate(range(163, 238, 6))]
drops += [(f, 208) for f in range(F(1387) + 2, 588, 9)]                    # "filling the bucket by hand" (beside the hose)
svg += [f'<path id="dp{n}" d="{TEAR}" fill="{BLUE}" opacity="0"/>' for n in range(len(drops))]
svg += [f'<g clip-path="url(#bkclip)"><g id="wg"><g id="wv"><path d="{WAVE}V260 H-120 Z" fill="{BLUE}"/><path d="{WAVE}" fill="none" stroke="rgba(255,255,255,0.42)" stroke-width="3"/></g></g></g>',
        f'<path d="M47,128 L283,128 L253,310 Q252,318 244,318 L86,318 Q78,318 77,310 Z" fill="none" stroke="{BONE}" stroke-width="5" stroke-linejoin="round"/>',
        f'<rect x="36" y="114" width="258" height="24" rx="12" fill="{BONE}"/>']
for k, (side, y, r) in enumerate(HOLES):
    d = leak_path(side, y, r); w = 9 if r > 8 else 5
    svg.append(f'<g id="lk{k}" opacity="0"><path id="lkb{k}" d="{d}" fill="none" stroke="{BLUE}" stroke-width="{w}" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
               f'<path class="flow" d="{d}" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="{w / 3:.1f}" stroke-linecap="round" stroke-dasharray="10 14"/></g>')
for k, (side, y, r) in enumerate(HOLES):
    x = edge(y, side); pw = 3.2 * r; ph = 2.3 * r
    svg.append(f'<circle id="ho{k}" cx="{x:.1f}" cy="{y}" r="{r}" fill="#0A0A0A" stroke="{BONE}" stroke-width="3" opacity="0"/>')
    svg.append(f'<g id="pt{k}" opacity="0"><rect x="{x - pw / 2:.1f}" y="{y - ph / 2:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="{r * 0.5:.1f}" fill="{BONE}" stroke="#0A0A0A" stroke-width="2" transform="rotate({side * -14} {x:.1f} {y})"/>'
               f'<path d="M{x - r * 0.6:.1f},{y} h{r * 1.2:.1f} M{x:.1f},{y - r * 0.6:.1f} v{r * 1.2:.1f}" stroke="#0A0A0A" stroke-width="2.4" stroke-linecap="round" transform="rotate({side * -14} {x:.1f} {y})"/></g>')
svg.append('<g id="hz" opacity="0"><path d="M-40,30 C30,30 70,26 108,50" fill="none" stroke="rgba(242,239,233,0.4)" stroke-width="28" stroke-linecap="round"/>'
           '<path d="M-40,30 C30,30 70,26 108,50" fill="none" stroke="#2A2B31" stroke-width="23" stroke-linecap="round"/>'
           f'<g transform="translate(108,50) rotate(32)"><rect x="-6" y="-16" width="38" height="32" rx="7" fill="{BONE}"/><rect x="28" y="-11" width="14" height="22" rx="4" fill="{BLUE}"/></g>'
           f'<g id="hzt"><rect x="4" y="-30" width="92" height="42" rx="21" fill="{BLUE}"/><text x="50" y="1" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="27" letter-spacing="-0.5" fill="#fff">Ads</text></g></g>')
svg.append('</svg>')

# ---- panels beside the bucket ----
segs = lambda p, n: '<span class="sg">' + ''.join(f'<i id="{p}{k}"></i>' for k in range(n)) + '</span>'
NSEG = 6
pA = ('<div id="pA" class="pn" style="opacity:1"><div class="chead"><div class="clbl"><i class="dot a"></i>Picture this</div></div>'
      '<div class="sl"><div id="a0" class="rw big"><b>Bucket</b><i>=</i><span>Your business</span></div></div>'
      '<div class="sl"><div id="a1" class="rw big"><b>Water</b><i>=</i><span>People</span></div></div></div>')
pB = ('<div id="pB" class="pn"><div class="chead"><div class="clbl"><i class="dot a"></i>First 30 days</div><div id="dayc" class="dayc">Day <b id="dayn">1</b></div></div>'
      '<div class="jl">Your job</div><div id="jb" class="jb">Fill the bucket</div>'
      '<div class="tlw"><div class="tlt"><div id="tlf" class="tlf"></div></div><span class="tlm" style="left:0">Day 1</span><span id="tl30" class="tlm" style="right:0">30</span></div></div>')
rowsC = [('Leaks are normal', 'ok'), ('A perfect bucket', 'bad'), ('Fill the biggest holes', 'ok')]
pC = ('<div id="pC" class="pn"><div class="chead"><div class="clbl"><i class="dot b"></i>Every bucket leaks</div></div>' +
      ''.join(f'<div id="c{k}" class="rw"><span id="ct{k}">{t}</span>' + (f'<span id="ck{k}" class="okr off">{TICK}</span>' if m == 'ok' else f'<span id="ck{k}" class="okr bad">{CROSS}</span>') + '</div>' for k, (t, m) in enumerate(rowsC)) + '</div>')
pD = ('<div id="pD" class="pn"><div class="chead"><div class="clbl"><i class="dot a"></i>Ads = a hose</div></div>'
      f'<div id="d0" class="rw mid"><span>By hand</span>{segs("dh", NSEG)}</div>'
      f'<div id="d1" class="rw mid"><span>Hose</span>{segs("dz", NSEG)}</div><div id="dfast" class="pilla low">A lot faster</div></div>')
pE = ('<div id="pE" class="pn"><div class="chead"><div class="clbl"><i class="dot a"></i>A hose on a…</div></div>'
      '<div id="e0" class="rw tall"><span>Good bucket</span><em id="e0p" class="st ok">Great</em></div>'
      '<div id="e1" class="rw tall"><span>Leaky bucket</span><em id="e1p" class="st bad">Wet floor</em></div></div>')
order = ['Hose (ads)', 'Fill the bucket', 'Fill the biggest holes']           # as it starts: backwards
pF = ('<div id="pF" class="pn"><div class="chead"><div id="fA" class="clbl"><i class="dot b"></i>Backwards</div><div id="fB" class="clbl"><i class="dot a"></i>The right order</div></div>' +
      ''.join(f'<b id="on{k}" class="onum" style="top:{62 + 82 * k}px">{k + 1}</b>' for k in range(3)) +
      ''.join(f'<div id="or{k}" class="orow" style="top:{62 + 82 * k}px"><span>{t}</span><span id="ok{k}" class="okr off">{TICK}</span>' + (f'<span id="ox" class="okr bad ox">{CROSS}</span>' if k == 0 else '') + '</div>' for k, t in enumerate(order)) + '</div>')
s.front.append('<div id="bkc" class="card tall" style="opacity:1"><div class="flr"></div>' + ''.join(svg) + pA + pB + pC + pD + pE + pF + '</div>')

# ---- always moving: the surface of the water, and whatever is flowing ----
kw = round(DUR / 1.6); kf = round(DUR / 0.3)
J(f'gsap.set("#wg", {{ y: {Y(LV[0][1])} }});')
J(f'tl.to("#wv", {{ x: -60, duration: {DUR / kw:.6f}, ease: "none", repeat: {kw - 1} }}, 0);')
J(f'tl.to(".flow", {{ strokeDashoffset: -24, duration: {DUR / kf:.6f}, ease: "none", repeat: {kf - 1} }}, 0);')
for n, (f, x) in enumerate(drops):                    # a drop falls and joins the water
    J(f'tl.set("#dp{n}", {{ opacity: 1, x: {x}, y: -34 }}, {at(f)});')
    J(f'tl.to("#dp{n}", {{ y: {Y(lv(f + 7)) + 4}, duration: {7 / 30:.4f}, ease: "power2.in" }}, {at(f)});')
    J(f'tl.set("#dp{n}", {{ opacity: 0 }}, {at(f + 7)});')
def flow_on(g, base, f, d=0, dur=0.2):
    J(f'tl.set("#{base}", {{ strokeDashoffset: 1 }}, {at(f, d)});'); J(f'tl.set("#{g}", {{ opacity: 1 }}, {at(f, d)});')
    J(f'tl.to("#{base}", {{ strokeDashoffset: 0, duration: {dur}, ease: "power1.in" }}, {at(f, d)});')
def flow_off(g, base, f, d=0, dur=0.2):
    J(f'tl.to("#{base}", {{ strokeDashoffset: -1, duration: {dur}, ease: "power1.in" }}, {at(f, d)});'); J(f'tl.set("#{g}", {{ opacity: 0 }}, {at(f, d + dur * 30)});')
def patch_on(k, f, d=0, snd=-12):
    J(f'tl.fromTo("#pt{k}", {{ opacity: 0, scale: 0.2, y: 0, rotation: 0, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, y: 0, rotation: 0, duration: 0.24, ease: "back.out(2.6)", immediateRender: false }}, {at(f, d)});')      # y / rotation in the to-vars too: a patch that fell off comes back in place
    flow_off(f'lk{k}', f'lkb{k}', f, d + 1)
    if snd: s.sound(f + d, 'ui/click.wav', snd)
def patch_off(k, f, d=0):
    J(f'tl.to("#pt{k}", {{ y: 70, rotation: {40 if HOLES[k][0] > 0 else -40}, opacity: 0, duration: 0.3, ease: "power2.in", transformOrigin: "50% 50%" }}, {at(f, d)});')
    flow_on(f'lk{k}', f'lkb{k}', f, d + 2)

# ================= HOOK: the bucket is your business, the water is people =================
J(f'tl.fromTo("#bk", {{ scale: 1.05 }}, {{ scale: 1.12, duration: 0.4, ease: "back.out(1.8)", transformOrigin: "0% 100%" }}, 0);')    # the svg is shown at 1.12x, growing up out of the card
pop('#a0', F(246), frm='{ opacity: 0, scale: 0.8, y: -16 }', dur=0.26, ease='back.out(2)'); s.sound(F(246), 'ui/click.wav', -12)      # "your business is the bucket"
for i in range(4): s.sound(F(254) + 9 * i + 7, 'ui/pop.mp3', -19)                                                               # "water": the first drops land
pop('#a1', F(256), frm='{ opacity: 0, scale: 0.8, y: -16 }', dur=0.26, ease='back.out(2)'); s.sound(F(256), 'ui/click.wav', -12)      # "the water's people"

# ================= FIRST 30 DAYS: fill it =================
swap('#pA', '#pB', B1)
d0, d1 = F(259), 240
J(f'tl.to("#dayn", {{ textContent: 30, snap: {{ textContent: 1 }}, duration: {(d1 - d0) / 30:.4f}, ease: "none" }}, {at(d0)});')
J(f'tl.to("#tlf", {{ scaleX: 1, duration: {(d1 - d0) / 30:.4f}, ease: "none" }}, {at(d0)});')
J(f'tl.to("#jb", {{ color: "#ffffff", duration: 0.15 }}, {at(F(265))});')                                                       # "fill"
J(f'tl.fromTo("#jb", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(F(265))});')
J(f'tl.to("#dayc", {{ backgroundColor: "{BLUE}", borderColor: "{BLUE}", duration: 0.14 }}, {at(d1)});'); J(f'tl.to("#tl30", {{ color: "#ffffff", duration: 0.14 }}, {at(d1)});')
s.sound(F(265), 'ui/click.wav', -13)

# ================= EVERY BUCKET LEAKS =================
swap('#pB', '#pC', C1)
fl = F(752)                                           # "leaks": the holes open and the water runs out
for k in range(4):
    J(f'tl.fromTo("#ho{k}", {{ opacity: 0, scale: 0.2, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, {at(fl, 3 * k)});')
    flow_on(f'lk{k}', f'lkb{k}', fl, 3 * k + 2); s.sound(fl + 3 * k, 'ui/pop.mp3', -15)
for k, f in enumerate([F(753), F(764), F(771)]):      # each line arrives as he gets to it
    pop(f'#c{k}', f, frm='{ opacity: 0, scale: 0.9, y: 14 }', dur=0.24, ease='back.out(1.8)')
tick('#ck0', F(759))                                  # "completely normal"
pop('#ck1', F(767), frm='{ opacity: 0, scale: 0.4 }', ease='back.out(3)'); J(f'tl.to("#ct1", {{ color: "rgba(242,239,233,0.45)", duration: 0.2 }}, {at(F(767))});'); s.sound(F(767), 'ui/pop.mp3', -14)   # not a perfect bucket
fb = F(773)                                           # "biggest holes": the two big ones are patched
patch_on(0, fb, 0); patch_on(1, fb, 6)
tick('#ck2', F(774), 2, snd=0)
J(f'tl.to("#c2", {{ borderColor: "rgba(47,111,237,0.75)", duration: 0.2 }}, {at(F(774), 2)});')

# ================= ADS = A HOSE =================
swap('#pC', '#pD', C2)
J(f'tl.fromTo("#hz", {{ opacity: 0, x: -150 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "back.out(1.5)", immediateRender: false }}, {at(F(1380))});')     # "ads ... hose": it arrives, not yet on
J(f'tl.fromTo("#hzt", {{ scale: 1 }}, {{ scale: 1.16, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, transformOrigin: "50% 50%", immediateRender: false }}, {at(F(1383))});')
s.sound(F(1383), 'ui/pop.mp3', -14)
pop('#d0', F(1387), frm='{ opacity: 0, scale: 0.9, y: 14 }', dur=0.24, ease='back.out(1.8)')                                    # "you've been filling the bucket by hand": one notch
J(f'tl.to("#dh0", {{ backgroundColor: "{BLUE}", duration: 0.12 }}, {at(F(1393))});'); s.sound(F(1393), 'ui/click.wav', -13)
fh = F(1395) + 5                                      # "a hose does it a lot faster": turned on
pop('#d1', F(1394), frm='{ opacity: 0, scale: 0.9, y: 14 }', dur=0.24, ease='back.out(1.8)')
flow_on('hs', 'hsb', fh, 0, 0.16); s.sound(fh, 'transitions/whoosh.mp3', -17)
for k in range(NSEG):
    J(f'tl.to("#dz{k}", {{ backgroundColor: "{BLUE}", duration: 0.1 }}, {at(fh, 3 + 3 * k)});')
    J(f'tl.fromTo("#dz{k}", {{ scaleY: 1.8 }}, {{ scaleY: 1, duration: 0.22, ease: "power3.out", immediateRender: false }}, {at(fh, 3 + 3 * k)});')
pop('#dfast', F(1399), frm='{ opacity: 0, scale: 0.6, y: 10 }'); s.sound(F(1399), 'ui/pop.mp3', -14)
# ---- good bucket / leaky bucket ----
swap('#pD', '#pE', ST[8])
pop('#e0', F(1404), frm='{ opacity: 0, scale: 0.9, y: 14 }', dur=0.24, ease='back.out(1.8)')
patch_on(2, F(1404), 2); patch_on(3, F(1404), 6)      # "a good bucket": every hole patched, so it fills
pop('#e0p', F(1408), ease='back.out(3)'); s.sound(F(1408), 'ui/click.wav', -11)                                                 # "great"
J(f'tl.to("#e0", {{ borderColor: "rgba(47,111,237,0.75)", duration: 0.2 }}, {at(F(1408))});')
pop('#e1', F(1412), frm='{ opacity: 0, scale: 0.9, y: 14 }', dur=0.24, ease='back.out(1.8)')
fk = F(1413)                                          # "leaky": the patches come off and it gushes
for k in range(4):
    patch_off(k, fk, 2 * k); J(f'tl.to("#lkb{k}", {{ attr: {{ "stroke-width": {14 if HOLES[k][2] > 8 else 8} }}, duration: 0.3 }}, {at(fk, 2 * k + 2)});')
s.sound(fk, 'ui/pop.mp3', -13)
fw = F(1418)                                          # "wet floor"
J(f'tl.fromTo("#pud", {{ opacity: 1, scaleX: 0.25, scaleY: 0.4, transformOrigin: "50% 50%" }}, {{ scaleX: 1, scaleY: 1, duration: {(fw + 8 - (fk + 10)) / 30:.4f}, ease: "power2.out", immediateRender: false }}, {at(fk, 10)});')
J(f'tl.set("#pud", {{ opacity: 1 }}, {at(fk, 10)});')
pop('#e1p', fw, ease='back.out(3)'); s.sound(fw, 'impact/bass-drop.mp3', -16)
J(f'tl.to("#e1", {{ backgroundColor: "rgba(242,239,233,0.08)", borderColor: "rgba(242,239,233,0.55)", duration: 0.2 }}, {at(fw)});')
shake('#e1', fw, 8)

# ================= THE ORDER =================
swap('#pE', '#pF', C3)
fx = F(1738)                                          # "the hose first": that is the backwards part
pop('#ox', fx, frm='{ opacity: 0, scale: 0.4 }', ease='back.out(3)'); s.sound(fx, 'ui/pop.mp3', -13)
J(f'tl.to("#or0", {{ backgroundColor: "rgba(242,239,233,0.08)", borderColor: "rgba(242,239,233,0.55)", duration: 0.2 }}, {at(fx)});')
shake('#or0', fx, 8)
fo = F(1739)                                          # "but now you know the right order": the list re-orders itself
J(f'tl.to("#ox", {{ opacity: 0, scale: 0.5, duration: 0.14, ease: "power2.in" }}, {at(fo, -2)});')
J(f'tl.to("#or0", {{ y: 164, backgroundColor: "rgba(242,239,233,0.05)", borderColor: "rgba(242,239,233,0.14)", duration: 0.5, ease: "power3.inOut" }}, {at(fo)});')
J(f'tl.to("#or1, #or2", {{ y: -82, duration: 0.5, ease: "power3.inOut" }}, {at(fo, 2)});')
J(f'tl.to("#fA", {{ opacity: 0, y: -10, duration: 0.14, ease: "power2.in" }}, {at(fo, -2)});')
J(f'tl.fromTo("#fB", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out", immediateRender: false }}, {at(fo, 2)});')
s.sound(fo, 'transitions/whoosh.mp3', -17)
for k in range(4): patch_on(k, fo, 4 + 3 * k, snd=0)  # ... and on the left that order plays out: patched, dry floor, filling
J(f'tl.to("#pud", {{ scaleX: 0, scaleY: 0, duration: 0.6, ease: "power2.in", transformOrigin: "50% 50%" }}, {at(fo, 6)});')
for n, (row, f) in enumerate([(1, F(1742)), (2, F(1742) + 5), (0, F(1743) + 2)]):      # 1, 2, 3 tick off in the new order
    tick(f'#ok{row}', f, snd=-12)
    J(f'tl.to("#or{row}", {{ borderColor: "rgba(47,111,237,0.75)", duration: 0.2 }}, {at(f)});')
    J(f'tl.to("#on{n}", {{ backgroundColor: "{BLUE}", color: "#ffffff", borderColor: "{BLUE}", duration: 0.16 }}, {at(f)});')
fg = F(1743) + 6
glow('#bkc', fg)
assert fg + 9 <= NF - 9 and LV[-1][0] <= NF - 9, 'the last frame must be finished and held'

s.css.append('''    .card.tall { top: 1244px; height: 352px; padding: 0; }
    .bk { position: absolute; left: 14px; top: 0; overflow: visible; transform-origin: 0 100%; transform: scale(1.12); }
    .flr { position: absolute; left: 28px; width: 336px; top: 318px; height: 2px; border-radius: 1px; background: rgba(242,239,233,0.14); }
    .pn { position: absolute; left: 366px; right: 28px; top: 26px; height: 300px; opacity: 0; }
    .rw { position: relative; height: 70px; margin-top: 12px; border-radius: 18px; background: rgba(242,239,233,0.05); border: 2px solid rgba(242,239,233,0.14); display: flex; align-items: center; justify-content: space-between;
          padding: 0 14px 0 20px; font-weight: 800; font-size: 32px; letter-spacing: -0.03em; color: #fff; white-space: nowrap; opacity: 0; }
    .rw.tall { height: 96px; margin-top: 16px; }  .rw.mid { height: 80px; margin-top: 16px; }
    .sl { height: 96px; margin-top: 16px; border-radius: 18px; border: 2px dashed rgba(242,239,233,0.18); }
    .rw.big { height: 96px; margin: -2px; justify-content: flex-start; gap: 12px; font-size: 34px; background: #1D1E23; border-color: rgba(47,111,237,0.75); }
    .rw.big b { color: #2F6FED; font-weight: 800; }  .rw.big i { font-style: normal; color: rgba(242,239,233,0.5); }
    .okr.off { background: rgba(242,239,233,0.12); color: rgba(242,239,233,0); }  .okr.bad { background: #F2EFE9; color: #0A0A0A; opacity: 0; }
    /* first 30 days */
    .dayc { position: absolute; right: 0; top: 0; height: 48px; padding: 0 18px; border-radius: 24px; border: 2px solid rgba(242,239,233,0.24); background: rgba(242,239,233,0.06); color: #fff; font-weight: 800; font-size: 30px; letter-spacing: -0.02em; line-height: 44px; white-space: nowrap; }
    .dayc b { display: inline-block; width: 40px; text-align: right; font-weight: 800; font-variant-numeric: tabular-nums; }
    .jl { margin-top: 26px; font-weight: 700; font-size: 28px; letter-spacing: -0.02em; color: rgba(242,239,233,0.6); }
    .jb { margin-top: 2px; font-weight: 800; font-size: 54px; letter-spacing: -0.04em; color: rgba(242,239,233,0.6); transform-origin: 0 50%; white-space: nowrap; }
    .tlw { position: relative; margin-top: 30px; height: 54px; }
    .tlt { position: absolute; left: 0; right: 0; top: 0; height: 14px; border-radius: 7px; background: rgba(242,239,233,0.12); overflow: hidden; }
    .tlf { position: absolute; inset: 0; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0.012); }
    .tlm { position: absolute; top: 22px; font-weight: 700; font-size: 26px; letter-spacing: -0.02em; color: rgba(242,239,233,0.6); white-space: nowrap; }
    /* by hand / hose */
    .sg { display: grid; grid-template-columns: repeat(6, 30px); column-gap: 6px; height: 22px; }  .sg i { border-radius: 6px; background: rgba(242,239,233,0.14); }
    .pilla { position: absolute; background: #2F6FED; color: #fff; font-weight: 800; font-size: 30px; letter-spacing: -0.02em; padding: 3px 20px 5px; border-radius: 22px; opacity: 0; }
    .pilla.low { right: 0; top: 256px; }
    /* good bucket / leaky bucket */
    .st { font-style: normal; font-weight: 800; font-size: 28px; letter-spacing: -0.02em; padding: 5px 18px 7px; border-radius: 22px; opacity: 0; }
    .st.ok { background: #2F6FED; color: #fff; }  .st.bad { background: #F2EFE9; color: #0A0A0A; }
    /* the order */
    #fB { opacity: 0; }
    .onum { position: absolute; left: 0; width: 48px; height: 48px; margin-top: 10px; border-radius: 24px; border: 2px solid rgba(242,239,233,0.3); color: rgba(242,239,233,0.8); font-weight: 800; font-size: 28px; display: flex; align-items: center; justify-content: center; }
    .orow { position: absolute; left: 62px; right: 0; height: 68px; border-radius: 18px; background: rgba(242,239,233,0.05); border: 2px solid rgba(242,239,233,0.14); display: flex; align-items: center; justify-content: space-between;
            padding: 0 14px 0 20px; font-weight: 800; font-size: 30px; letter-spacing: -0.03em; color: #fff; white-space: nowrap; }
    .ox { position: absolute; right: 14px; top: 12px; }''')
for t, sz, w, lim in [('Bucket = Your business', 34, 800, 506 - 44 - 24), ('Fill the bucket', 54, 800, 506), ('Fill the biggest holes', 32, 800, 506 - 34 - 40 - 12), ('Every bucket leaks', 36, 800, 506 - 30),
                      ('Ads = a hose', 36, 800, 506 - 30), ('Leaky bucket', 32, 800, 506 - 34 - 170), ('Fill the biggest holes', 30, 800, 506 - 62 - 34 - 40 - 10), ('First 30 days', 36, 800, 506 - 30 - 150)]:
    assert text_width(t, sz, w, -0.03) <= lim, (t, round(text_width(t, sz, w, -0.03)), lim)
s.write()
