"""02 — The bucket (stacked layout), v3: the final pass. ONE graphic for the whole reel: a bucket that does everything he
describes, on the word he says it, with one short label beside it per step. Sound off, the bucket tells it:
  HOOK          the reel opens on the punchline picture, centred in the card: hose on, bucket leaking, wet floor, under the
                headline "Before you spend a penny on ads / picture a bucket". On "picture a bucket" it wipes clean and
                slides to its place on the left -> "The bucket = Your business"; drops fall on "water", and on "the water's
                people" the drops ARE people -> "The water = People"
  FIRST 30 DAYS drops keep falling (by hand), the level climbs while the day counter runs 1 -> 30
  LEAKS         on "leaks" holes open in the sides and water runs out into small pools (hero caption LEAKS);
                "Leaks are normal" tick, "A perfect bucket" cross, "Biggest holes filled" tick as the two big holes are patched
  ADS = HOSE    on "hose" the hose arrives -> "The hose = Ads"; by hand = slow drops; then the hose is on: the stream lands
                with a splash, the surface churns, the level races up
                on a good bucket (every hole patched) it fills to the brim and the bucket glows: tick
                on a leaky bucket the patches come off, it gushes, the glow goes, the puddle spreads: cross (hero WET FLOOR)
  THE ENDING    on "backwards" the order most people use lands: 1 Hose, 2 Bucket; cross on "the hose first". Then the takeaway takes the headline, in the biggest type of the reel,
                and the bucket comes back to the centre of the card, the mirror of the opening shot:
                "FIX THE BUCKET." (hose off, every hole patched, floor dries)
                "THEN TURN ON THE HOSE." (hose on, it fills to the brim, glow). The end frame is held (clips.py: hold).
Nothing sits over his head or face: every caption is at his chest; LEAKS and WET FLOOR are caps in the blue bar there.
Camera as in clip 01. His words, voice and footage are untouched.
Run from the project folder: python3 -I scripts/stack/clip_02.py"""
import math
exec(open('scripts/stack/kit.py').read())
s = Scene('02-the-bucket', 'The bucket')
exec(open('scripts/stack/hook.py').read())
ST = s.E['starts']; NF, NV = s.NF, s.NV; DUR = NF / 30
B1, C1, C2, C3, FIN = F(258), F(749), F(1378), F(1729), F(1739)     # hook | first 30 days | leaks | hose | backwards | the takeaway
assert all(c in ST for c in (B1, C1, C2, C3, FIN)), (ST, B1, C1, C2, C3, FIN)
s.match = dict(ref=0, strength=0.8, only=[2, 3])        # the hose and the ending were shot later in the recording (warmer, brighter wall)
s.pinned_title('Before you spend a penny on ads', 'picture a bucket', 0, B1, big=True)
s.pinned_title('Your first job', 'fill the bucket', B1, C1)
s.pinned_title('Every bucket leaks', 'fill the biggest holes', C1, C2)
s.pinned_title('Think of ads', 'as a hose', C2, C3)
s.pinned_title('Most people', 'buy the hose first', C3, FIN)             # from FIN the headline is the takeaway itself (below)

s.captions([                                           # all at his chest; 'hero' = the key words, caps in the blue bar
    (0,        "First, let's",                  'chest'),
    (F(242),   'picture a *bucket*',            'chest'),
    (F(245),   'Your *business*',               'chest'),
    (F(247),   'is the *bucket*',               'chest'),
    (F(250),   'and then',                      'chest'),
    (F(252),   'we have *water*',               'chest'),
    (F(255),   "the water's *people*",          'chest'),
    (B1,       'First *30 days*',               'chest'),
    (F(261),   'your job is',                   'chest'),
    (F(264),   'to *fill* this bucket',         'chest'),
    (F(268),   'with the water',                'chest'),
    (C1,       'And every bucket',              'chest'),
    (F(752),   'leaks',                         'hero'),
    (F(753),   'Yours will too',                'chest'),
    (F(756),   "and that's",                    'chest'),
    (F(758),   'completely *normal*',           'chest'),
    (F(760),   "We're not trying",              'chest'),
    (F(763),   'to build a',                    'chest'),
    (F(766),   '*perfect* bucket',              'chest'),
    (F(768),   "we're trying to",               'chest'),
    (F(771),   'fill the',                      'chest'),
    (F(773),   '*biggest holes*',               'chest'),
    (C2,       'Think of *ads*',                'chest'),
    (F(1381),  'as a *hose*',                   'chest'),
    (F(1384),  'Up to now',                     'chest'),
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
    (F(1415),  "we've got a",                   'chest'),
    (F(1418),  'wet floor',                     'hero'),
    (C3,       'Most people',                   'chest'),
    (F(1731),  'do it *backwards*',             'chest'),
    (F(1734),  "they'll buy",                   'chest'),
    (F(1736),  'the *hose first*',              'chest'),
    (FIN,      'but now you know',              'chest'),
    (F(1743),  'the *right order*',             'chest', NV + 5),         # gone once he has said it: the end frame is the takeaway and the bucket
])

# ================= CAMERA: one base framing per shot (alternating on the jump cuts), punch-ins on the key words =================
base = [(1.00, 1.02), (1.05, 1.07), (1.00, 1.03), (1.02, 1.04), (1.00, 1.03), (1.02, 1.04), (1.00, 1.02), (1.05, 1.055), (1.00, 1.03), (1.05, 1.065), (1.00, 1.02), (1.03, 1.05), (1.00, 1.06)]
assert len(base) == len(ST) - 1, (len(base), len(ST))
for k, (z0, z1) in enumerate(base): s.shot(ST[k], ST[k + 1] if k + 2 < len(ST) else NF, z0, z1)     # the last shot (and its held end frame) is one slow push
for k in range(10): s.zoom[k] += 0.05 * (1 - k / 10) ** 2        # the first frames settle back with the headline
shot_end = lambda f: next(b for b in ST if b > f)
for w, dz in [(265, 0.03), (752, 0.04), (773, 0.04), (1383, 0.04), (1400, 0.03), (1418, 0.05)]:      # fill | leaks | biggest holes | hose | faster | wet floor
    s.punch(F(w), shot_end(F(w)), dz)
for c in (C1, C2, C3):                                  # section changes: a small zoom through the cut
    s.through(c, 0.045); s.sound(c, 'transitions/whoosh.mp3', -17)
assert s.zoom.max() <= 1.2 and s.zoom.min() >= 1.0, (s.zoom.min(), s.zoom.max())

J = s.js.append
def at(f, d=0): return round(tm(f) + d / 30, 4)
def pop(sel, f, d=0, frm='{ opacity: 0, scale: 0.4 }', dur=0.22, ease='back.out(2.4)'):
    J(f'tl.fromTo("{sel}", {frm}, {{ opacity: 1, scale: 1, x: 0, y: 0, duration: {dur}, ease: "{ease}", immediateRender: false }}, {at(f, d)});')
def row(sel, f, d=0): pop(sel, f, d, frm='{ opacity: 0, scale: 0.92, y: 14 }', dur=0.24, ease='back.out(1.8)')
def shake(sel, f, amp=10):
    for j, dx in enumerate([-amp, 0.8 * amp, -0.5 * amp, 0.3 * amp, 0]): J(f'tl.to("{sel}", {{ x: {dx:.1f}, duration: 0.05, ease: "power1.inOut" }}, {at(f, 1.5 * j)});')
def swap(a, b, f):                                      # the label beside the bucket changes; the bucket stays
    if a: J(f'tl.to("{a}", {{ opacity: 0, y: -16, duration: 0.14, ease: "power2.in" }}, {at(f, -4)});')
    if b: J(f'tl.fromTo("{b}", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power3.out", immediateRender: false }}, {at(f)});')
def tick(sel, f, d=0, snd=-11):
    J(f'tl.to("{sel}", {{ backgroundColor: "{BLUE}", color: "#ffffff", duration: 0.14 }}, {at(f, d)});')
    J(f'tl.fromTo("{sel}", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.22, ease: "back.out(2.8)", immediateRender: false }}, {at(f, d)});')
    if snd: s.sound(f + d, 'ui/click.wav', snd)
def cross(sel, f, d=0, snd=-14):
    pop(sel, f, d, frm='{ opacity: 0, scale: 0.4 }', ease='back.out(3)')
    if snd: s.sound(f + d, 'ui/pop.mp3', snd)
def lit(sel, f, d=0): J(f'tl.to("{sel}", {{ borderColor: "rgba(47,111,237,0.75)", duration: 0.2 }}, {at(f, d)});')
def warn(sel, f): J(f'tl.to("{sel}", {{ backgroundColor: "rgba(242,239,233,0.08)", borderColor: "rgba(242,239,233,0.55)", duration: 0.2 }}, {at(f)});'); shake(sel, f, 8)

# ================= THE BUCKET (svg 330 x 352 units; scaled from its bottom-left corner, so it grows up out of the card) =================
SC, SF = 1.3, 1.36                                      # scale beside the labels / scale centred for the ending
XO, XF = round(450 - 10 - 165 * SC, 1), round(450 - 10 - 165 * SF, 1)        # x offsets that centre it in the card (opening / ending)
YB, HW = 313, 172                                       # inside bottom of the bucket; height of a full bucket of water
Y = lambda L: round(YB - HW * L, 1)                     # y of the water surface at level L (0..1)
EMPTY = -0.07                                           # empty = the surface (and its ripple) is below the bottom
FR = F(244)                                             # "bucket": the opening picture wipes clean
f2 = F(1742)                                            # "...know the right order": the hose goes back on
LV = [(0, 0.62), (FR, 0.62), (FR + 16, EMPTY), (F(254), EMPTY), (F(254) + 38, 0.08), (B1 + 6, 0.08), (B1 + 88, 0.62), (F(752) + 2, 0.62), (F(771), 0.50), (F(774) + 2, 0.48),
      (F(1387), 0.47), (F(1393) + 12, 0.53), (F(1395) + 4, 0.53), (F(1400) + 14, 0.86), (F(1404), 0.87), (F(1408), 0.97), (F(1413) + 2, 0.97), (C3, 0.62), (FIN, 0.50),
      (f2 + 2, 0.50), (f2 + 38, 0.97)]
assert all(a[0] < b[0] for a, b in zip(LV, LV[1:])), LV
def lv(f):
    for (f0, a), (f1, b) in zip(LV, LV[1:]):
        if f0 <= f <= f1: return a + (b - a) * (f - f0) / (f1 - f0)
    return LV[-1][1]
for (f0, a), (f1, b) in zip(LV, LV[1:]):
    if a != b: J(f'tl.to("#wg", {{ y: {Y(b)}, duration: {(f1 - f0) / 30:.4f}, ease: "sine.inOut" }}, {at(f0)});')
WAVE = 'M-120,0 ' + 'q15,-6 30,0 t30,0 ' * 8
TEAR = '<path d="M0,-11 C5,-4 7.5,0 7.5,4 A7.5,7.5 0 1 1 -7.5,4 C-7.5,0 -5,-4 0,-11Z"/>'
MAN = '<circle cx="0" cy="-9" r="6"/><path d="M-10,13 c0,-7.2 4.4,-11.4 10,-11.4 s10,4.2 10,11.4z"/>'       # a person, the size of a drop
edge = lambda y, side: (47 + 30 * (y - 128) / 190) if side < 0 else (283 - 30 * (y - 128) / 190)
HOLES = [(-1, 262, 10), (1, 250, 10), (-1, 298, 6), (1, 294, 6)]            # (side, y, radius): two big, two small
WID = lambda k, gush=False: (14 if gush else 9) if HOLES[k][2] > 8 else (8 if gush else 5)
REACH = lambda k: 36 if HOLES[k][2] > 8 else 20
def leak_path(k):
    side, y, r = HOLES[k]; x = edge(y, side)
    return f'M{x:.1f},{y} q{side * REACH(k) * 0.75:.1f},3 {side * REACH(k):.1f},{322 - y}'
HOSE = 'M143,72 Q160,84 165,128 L165,313'
BODY = 'M47,128 L283,128 L253,310 Q252,318 244,318 L86,318 Q78,318 77,310 Z'
# the reel opens on the punchline picture: hose on, every hole open and gushing, a wet floor (so these start visible)
svg = ['<svg id="bk" class="bk" viewBox="0 0 330 352" width="330" height="352">',
       '<defs><clipPath id="bkclip"><path d="M52,138 L278,138 L249,309 Q248,313 243,313 L87,313 Q82,313 81,309 Z"/></clipPath>'
       f'<radialGradient id="glg"><stop offset="0.4" stop-color="{BLUE}" stop-opacity="0.4"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient></defs>',
       '<ellipse id="glw" cx="165" cy="224" rx="196" ry="168" fill="url(#glg)" opacity="0"/>',                             # a good bucket glows
       '<path d="M-14,322 H344" stroke="rgba(242,239,233,0.14)" stroke-width="1.6" stroke-linecap="round"/>',                   # the floor
       f'<g id="pud"><ellipse cx="165" cy="325" rx="150" ry="11" fill="{BLUE}"/><ellipse cx="150" cy="322" rx="90" ry="3.5" fill="rgba(255,255,255,0.28)"/></g>',
       f'<path d="{BODY}" fill="#1B1C21"/>',
       f'<g id="hs"><path id="hsb" d="{HOSE}" fill="none" stroke="{BLUE}" stroke-width="14" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0"/>'
       f'<path id="hsbf" class="flow" d="{HOSE}" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="4" stroke-linecap="round" stroke-dasharray="10 14"/></g>']
drops = [(F(254) + 9 * i, 165, TEAR) for i in range(2)]                    # "water": the first drops
drops += [(F(256) - 2 + 9 * i, 165, MAN) for i in range(2)]                # "the water's people": the drops are people
drops += [(f, 165 + (6 if i % 2 else -6), TEAR) for i, f in enumerate(range(B1 + 4, B1 + 84, 6))]      # first 30 days: by hand, steadily
drops += [(f, 208, TEAR) for f in range(F(1387) + 2, F(1393) + 10, 9)]     # "filling the bucket by hand" (beside the hose)
svg += [f'<g id="dp{n}" fill="{BLUE}" opacity="0">{shape}</g>' for n, (_, _, shape) in enumerate(drops)]
svg += [f'<g clip-path="url(#bkclip)"><g id="wg"><g id="wv"><path d="{WAVE}V260 H-120 Z" fill="{BLUE}"/><path d="{WAVE}" fill="none" stroke="rgba(255,255,255,0.42)" stroke-width="3"/></g>'
        '<g id="spl"><ellipse id="splr" cx="165" cy="0" rx="22" ry="5.5" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="2.5"/><ellipse cx="165" cy="0" rx="13" ry="3.6" fill="rgba(255,255,255,0.55)"/>'
        '<circle id="spa" cx="149" cy="-7" r="3" fill="#A9C4FA"/><circle id="spb" cx="182" cy="-9" r="2.5" fill="#A9C4FA"/></g></g></g>',       # where the hose lands: it moves with the surface
        f'<path d="{BODY}" fill="none" stroke="{BONE}" stroke-width="5" stroke-linejoin="round"/>',
        f'<rect x="36" y="114" width="258" height="24" rx="12" fill="{BONE}"/>']
for k, (side, y, r) in enumerate(HOLES):
    d = leak_path(k); xe = edge(y, side) + side * REACH(k)
    svg.append(f'<g id="lk{k}"><ellipse id="lp{k}" cx="{xe:.1f}" cy="323" rx="{REACH(k) * 0.42:.1f}" ry="3.6" fill="{BLUE}"/>'                    # a small pool where each leak lands
               f'<path id="lkb{k}" d="{d}" fill="none" stroke="{BLUE}" stroke-width="{WID(k, True)}" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0"/>'
               f'<path id="lkb{k}f" class="flow" d="{d}" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="{WID(k) / 3:.1f}" stroke-linecap="round" stroke-dasharray="10 14"/></g>')
for k, (side, y, r) in enumerate(HOLES):
    x = edge(y, side); pw = 3.2 * r; ph = 2.3 * r
    svg.append(f'<circle id="ho{k}" cx="{x:.1f}" cy="{y}" r="{r}" fill="#0A0A0A" stroke="{BONE}" stroke-width="3"/>')
    svg.append(f'<g id="pt{k}" opacity="0"><rect x="{x - pw / 2:.1f}" y="{y - ph / 2:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="{r * 0.5:.1f}" fill="{BONE}" stroke="#0A0A0A" stroke-width="2" transform="rotate({side * -14} {x:.1f} {y})"/>'
               f'<path d="M{x - r * 0.6:.1f},{y} h{r * 1.2:.1f} M{x:.1f},{y - r * 0.6:.1f} v{r * 1.2:.1f}" stroke="#0A0A0A" stroke-width="2.4" stroke-linecap="round" transform="rotate({side * -14} {x:.1f} {y})"/></g>')
TUBE = 'M-420,30 H-40 C30,30 70,26 108,50'              # long enough to run off the left of the frame wherever the bucket is
svg.append(f'<g id="hz"><path d="{TUBE}" fill="none" stroke="rgba(242,239,233,0.4)" stroke-width="28" stroke-linecap="round"/>'
           f'<path d="{TUBE}" fill="none" stroke="#2A2B31" stroke-width="23" stroke-linecap="round"/>'
           f'<g transform="translate(108,50) rotate(32)"><rect x="-6" y="-16" width="38" height="32" rx="7" fill="{BONE}"/><rect x="28" y="-11" width="14" height="22" rx="4" fill="{BLUE}"/></g>'
           f'<g id="hzt"><rect x="-2" y="10" width="86" height="40" rx="20" fill="{BLUE}"/><text x="41" y="39" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="26" letter-spacing="-0.5" fill="#fff">Ads</text></g></g>')
svg.append('</svg>')

# ---- the label beside the bucket: one short thing per step, all in the same two shapes (tile, row) ----
NSEG = 5
segs = lambda p: '<span class="sg">' + ''.join(f'<i id="{p}{k}"></i>' for k in range(NSEG)) + '</span>'
tile = lambda i, small, big: f'<div id="{i}" class="tl2"><small>{small}</small><b>{big}</b></div>'
pA = '<div id="pA" class="pn" style="opacity:1">' + tile('a0', 'The bucket', 'Your business') + tile('a1', 'The water', 'People') + '</div>'
pB = ('<div id="pB" class="pn"><div class="plab">First 30 days</div><div id="dayb" class="dayb">Day <b id="dayn">1</b></div>'
      '<div class="tlw"><div class="tlt"><div id="tlf" class="tlf"></div></div><span class="tlm" style="left:0">Day 1</span><span id="tl30" class="tlm" style="right:0">30</span></div></div>')
rowsC = [('Leaks are normal', 'ok'), ('A perfect bucket', 'bad'), ('Biggest holes filled', 'ok')]
pC = ('<div id="pC" class="pn">' + ''.join(f'<div id="c{k}" class="rw"><span id="ct{k}">{t}</span>' + (f'<span id="ck{k}" class="okr off">{TICK}</span>' if m == 'ok' else f'<span id="ck{k}" class="okr bad">{CROSS}</span>') + '</div>'
                                           for k, (t, m) in enumerate(rowsC)) + '</div>')
pD = ('<div id="pD" class="pn">' + tile('dt', 'The hose', 'Ads') +
      f'<div id="d0" class="rw"><span>By hand</span>{segs("dh")}</div><div id="d1" class="rw"><span>Hose</span>{segs("dz")}</div></div>')
pE = ('<div id="pE" class="pn">'
      f'<div id="e0" class="rw"><span>On a good bucket</span><span id="e0k" class="okr off">{TICK}</span></div>'
      f'<div id="e1" class="rw"><span>On a leaky bucket</span><span id="e1k" class="okr bad">{CROSS}</span></div></div>')
pF = ('<div id="pF" class="pn"><div class="plab">Backwards</div>'
      f'<div id="f0" class="rw num"><b class="onum">1</b><span>Hose (ads)</span><span id="fx" class="okr bad">{CROSS}</span></div>'
      '<div id="f1" class="rw num"><b class="onum">2</b><span>Bucket</span></div></div>')
s.front.append('<div id="bkc" class="card tall" style="opacity:1">' + ''.join(svg) + pA + pB + pC + pD + pE + pF + '</div>')
# the takeaway, where the headline has been all along: the biggest type of the reel
LA, LB = 'FIX THE BUCKET.', 'THEN TURN ON THE HOSE.'
sa = min(96, int(880 / text_width(LA, 1, 900, -0.02))); sb = min(66, int(820 / text_width(LB, 1, 900, -0.02)))
s.front.append(f'<div id="fin" class="fin"><div class="fa" style="font-size:{sa}px"><span class="lkm"><i id="fa">{LA}</i></span></div>'
               f'<div class="fbw"><span id="fb" class="fb" style="font-size:{sb}px"><i id="fbt">{LB}</i></span></div></div>')

# ---- always moving: the surface of the water, whatever is flowing, the splash under the hose ----
kw = round(DUR / 1.6); kf = round(DUR / 0.3); ks = round(DUR / 0.5)
J(f'gsap.set("#wg", {{ y: {Y(LV[0][1])} }}); gsap.set("#wv", {{ transformOrigin: "50% 0%", scaleY: 1.8 }}); gsap.set("#bk", {{ x: {XO}, scale: {SC * 0.95:.3f}, transformOrigin: "0% 100%" }});')
J(f'tl.to("#wv", {{ x: -60, duration: {DUR / kw:.6f}, ease: "none", repeat: {kw - 1} }}, 0);')
J(f'tl.to(".flow", {{ strokeDashoffset: -24, duration: {DUR / kf:.6f}, ease: "none", repeat: {kf - 1} }}, 0);')
J(f'tl.fromTo("#splr", {{ scale: 0.55, opacity: 0.9, transformOrigin: "50% 50%" }}, {{ scale: 1.7, opacity: 0, duration: {DUR / ks:.6f}, ease: "power1.out", repeat: {ks - 1} }}, 0);')
J(f'tl.fromTo("#spa", {{ y: 0, opacity: 1 }}, {{ y: -13, x: -5, opacity: 0, duration: {DUR / ks:.6f}, ease: "power1.out", repeat: {ks - 1} }}, 0);')
J(f'tl.fromTo("#spb", {{ y: 0, opacity: 1 }}, {{ y: -16, x: 6, opacity: 0, duration: {DUR / ks:.6f}, ease: "power1.out", repeat: {ks - 2} }}, {DUR / ks / 2:.6f});')
for n, (f, x, _) in enumerate(drops):                 # a drop falls and joins the water
    J(f'tl.set("#dp{n}", {{ x: {x}, y: 16 }}, {at(f)});')
    J(f'tl.fromTo("#dp{n}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.07, immediateRender: false }}, {at(f)});')
    J(f'tl.to("#dp{n}", {{ y: {Y(lv(f + 7)) + 4}, duration: {7 / 30:.4f}, ease: "power2.in" }}, {at(f)});')
    J(f'tl.set("#dp{n}", {{ opacity: 0 }}, {at(f + 7)});')
def flow_on(g, base, f, d=0, dur=0.2):
    J(f'tl.set("#{base}", {{ strokeDashoffset: 1 }}, {at(f, d)});'); J(f'tl.set("#{base}f", {{ opacity: 0 }}, {at(f, d)});'); J(f'tl.set("#{g}", {{ opacity: 1 }}, {at(f, d)});')
    J(f'tl.to("#{base}", {{ strokeDashoffset: 0, duration: {dur}, ease: "power1.in" }}, {at(f, d)});')
    J(f'tl.to("#{base}f", {{ opacity: 1, duration: 0.1 }}, {at(f, d + dur * 30 - 1)});')                 # the moving highlight only once the stream has arrived
def flow_off(g, base, f, d=0, dur=0.2):
    J(f'tl.to("#{base}f", {{ opacity: 0, duration: 0.05 }}, {at(f, d)});')
    J(f'tl.to("#{base}", {{ strokeDashoffset: -1, duration: {dur}, ease: "power1.in" }}, {at(f, d)});'); J(f'tl.set("#{g}", {{ opacity: 0 }}, {at(f, d + dur * 30)});')
def hose_on(f, d=0):                                  # the stream reaches the water: a splash where it lands, and the surface churns
    flow_on('hs', 'hsb', f, d, 0.16)
    J(f'tl.to("#spl", {{ opacity: 1, duration: 0.1 }}, {at(f, d + 4)});'); J(f'tl.to("#wv", {{ scaleY: 1.8, duration: 0.3, ease: "power2.out" }}, {at(f, d + 4)});')
def hose_off(f, d=0):
    flow_off('hs', 'hsb', f, d, 0.14)
    J(f'tl.to("#spl", {{ opacity: 0, duration: 0.1 }}, {at(f, d + 2)});'); J(f'tl.to("#wv", {{ scaleY: 1, duration: 0.5, ease: "power2.out" }}, {at(f, d + 2)});')
def leak_on(k, f, d=0, gush=False):
    J(f'tl.set("#lkb{k}", {{ attr: {{ "stroke-width": {WID(k, gush)} }} }}, {at(f, d)});'); flow_on(f'lk{k}', f'lkb{k}', f, d)
    J(f'tl.set("#lp{k}", {{ scale: 0, transformOrigin: "50% 50%" }}, {at(f, d)});'); J(f'tl.to("#lp{k}", {{ scale: 1, duration: 0.2, ease: "power2.out" }}, {at(f, d + 5)});')     # its pool forms once the stream has reached the floor
def hole_on(k, f, d=0):
    J(f'tl.fromTo("#ho{k}", {{ opacity: 0, scale: 0.2, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, {at(f, d)});')
def patch_on(k, f, d=0, snd=-12):
    J(f'tl.fromTo("#pt{k}", {{ opacity: 0, scale: 0.2, y: 0, rotation: 0, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, y: 0, rotation: 0, duration: 0.24, ease: "back.out(2.6)", immediateRender: false }}, {at(f, d)});')      # y / rotation in the to-vars too: a patch that fell off comes back in place
    flow_off(f'lk{k}', f'lkb{k}', f, d + 1)
    if snd: s.sound(f + d, 'ui/click.wav', snd)
def patch_off(k, f, d=0):
    J(f'tl.to("#pt{k}", {{ y: 70, rotation: {40 if HOLES[k][0] > 0 else -40}, opacity: 0, duration: 0.3, ease: "power2.in", transformOrigin: "50% 50%" }}, {at(f, d)});')
    leak_on(k, f, d + 2, gush=True)
def puddle(f, d, to, dur):
    J(f'tl.to("#pud", {{ scaleX: {to}, scaleY: {to}, duration: {dur}, ease: "{"power2.out" if to else "power2.in"}", transformOrigin: "50% 50%" }}, {at(f, d)});')
def glow_bucket(f, on, d=0): J(f'tl.to("#glw", {{ opacity: {1 if on else 0}, duration: {0.4 if on else 0.2}, ease: "power2.out" }}, {at(f, d)});')

# ================= HOOK: the punchline picture in the middle of the card, wiped clean on "picture a bucket" =================
J(f'tl.to("#bk", {{ scale: {SC}, duration: 0.4, ease: "back.out(1.8)" }}, 0);')
hose_off(FR, -2)                                                                                                                # hose off and away
J(f'tl.to("#hz", {{ x: -220, opacity: 0, duration: 0.3, ease: "power2.in" }}, {at(FR)});')
for k in range(4):                                                                                                              # the leaks stop, the holes close
    flow_off(f'lk{k}', f'lkb{k}', FR, 1 + k, 0.16)
    J(f'tl.to("#ho{k}", {{ opacity: 0, scale: 0.2, duration: 0.16, ease: "power2.in", transformOrigin: "50% 50%" }}, {at(FR, 4 + k)});')
puddle(FR, 2, 0, 0.4)
J(f'tl.to("#bk", {{ x: 0, duration: 0.5, ease: "power3.inOut" }}, {at(FR)});')                                                 # and the bucket takes its place: the labels go beside it
s.sound(FR, 'transitions/whoosh.mp3', -18)
row('#a0', F(246)); s.sound(F(246), 'ui/click.wav', -12)                                                                        # "your business is the bucket"
row('#a1', F(256), 2); s.sound(F(256) + 2, 'ui/click.wav', -12)                                                                 # "the water's people"

# ================= FIRST 30 DAYS: fill it =================
swap('#pA', '#pB', B1)
d0, d1 = F(259), B1 + 88
J(f'tl.to("#dayn", {{ textContent: 30, snap: {{ textContent: 1 }}, duration: {(d1 - d0) / 30:.4f}, ease: "none" }}, {at(d0)});')
J(f'tl.to("#tlf", {{ scaleX: 1, duration: {(d1 - d0) / 30:.4f}, ease: "none" }}, {at(d0)});')
J(f'tl.to("#dayb", {{ color: "{BLUE}", duration: 0.14 }}, {at(d1)});'); J(f'tl.to("#tl30", {{ color: "#ffffff", duration: 0.14 }}, {at(d1)});')
J(f'tl.fromTo("#dayb", {{ scale: 1 }}, {{ scale: 1.08, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(d1)});')
assert d1 <= C1 - 3

# ================= EVERY BUCKET LEAKS =================
swap('#pB', '#pC', C1)
fl = F(752)                                           # "leaks": the holes open and the water runs out
for k in range(4): hole_on(k, fl, 3 * k); leak_on(k, fl, 3 * k + 2)
s.sound(fl, 'ui/pop.mp3', -15)
row('#c0', fl, 4); tick('#ck0', F(759))               # the label arrives with the leaks; ticked on "completely normal"
row('#c1', F(766)); cross('#ck1', F(767)); J(f'tl.to("#ct1", {{ color: "rgba(242,239,233,0.45)", duration: 0.2 }}, {at(F(767))});')      # "a perfect bucket": not the aim
row('#c2', F(771))                                    # "fill the biggest holes": the two big ones are patched
patch_on(0, F(773), 0); patch_on(1, F(773), 6, snd=0)
tick('#ck2', F(774), 2, snd=0); lit('#c2', F(774), 2)

# ================= ADS = A HOSE =================
swap('#pC', '#pD', C2)
J(f'tl.fromTo("#hz", {{ opacity: 0, x: -220 }}, {{ opacity: 1, x: 0, duration: 0.36, ease: "back.out(1.5)", immediateRender: false }}, {at(F(1383), -5)});')     # in place as he says "hose"; not yet on
row('#dt', F(1383)); s.sound(F(1383), 'ui/click.wav', -12)
row('#d0', F(1392))                                   # "by hand": one notch (the drops have been falling since "you've been filling")
J(f'tl.to("#dh0", {{ backgroundColor: "{BLUE}", duration: 0.12 }}, {at(F(1393))});'); s.sound(F(1393), 'ui/click.wav', -13)
fh = F(1395) + 3                                      # "a hose does it a lot faster": turned on
row('#d1', F(1395))
hose_on(fh); s.sound(fh, 'transitions/whoosh.mp3', -18)
for k in range(NSEG):
    J(f'tl.to("#dz{k}", {{ backgroundColor: "{BLUE}", duration: 0.1 }}, {at(fh, 3 + 3 * k)});')
    J(f'tl.fromTo("#dz{k}", {{ scaleY: 1.8 }}, {{ scaleY: 1, duration: 0.22, ease: "power3.out", immediateRender: false }}, {at(fh, 3 + 3 * k)});')
lit('#d1', F(1399))                                   # "a lot faster"
# ---- on a good bucket / on a leaky bucket ----
G1 = F(1401); assert G1 in ST
swap('#pD', '#pE', G1)
row('#e0', F(1403))
patch_on(2, F(1405), 0); patch_on(3, F(1405), 4, snd=0)        # "a good bucket": every hole patched, so it fills to the brim
tick('#e0k', F(1408)); lit('#e0', F(1408)); glow_bucket(F(1408), True)                                                          # "great"
row('#e1', F(1411))
fk = F(1413)                                          # "leaky": the patches come off, it gushes, the glow goes
for k in range(4): patch_off(k, fk, 2 * k)
glow_bucket(fk, False); s.sound(fk, 'ui/pop.mp3', -13)
fw = F(1418)                                          # "wet floor"
J(f'tl.set("#pud", {{ opacity: 1 }}, {at(fk, 8)});'); J(f'tl.fromTo("#pud", {{ scaleX: 0.2, scaleY: 0.3, transformOrigin: "50% 50%" }}, {{ scaleX: 1, scaleY: 1, duration: {(fw + 8 - (fk + 8)) / 30:.4f}, ease: "power2.out", immediateRender: false }}, {at(fk, 8)});')
cross('#e1k', fw, snd=0); s.sound(fw, 'impact/bass-drop.mp3', -16); warn('#e1', fw)

# ================= BACKWARDS =================
fbk = F(1733)                                         # "backwards"
swap('#pE', '#pF', fbk)
row('#f0', fbk, 2); row('#f1', fbk, 6)                # the order most people use: 1 hose, 2 bucket
cross('#fx', F(1738), snd=-13); warn('#f0', F(1738))  # "the hose first": that is the mistake

# ================= THE TAKEAWAY: FIX THE BUCKET. / THEN TURN ON THE HOSE. =================
swap('#pF', None, FIN)
J(f'tl.to("#bk", {{ x: {XF}, scale: {SF}, duration: 0.55, ease: "power3.inOut" }}, {at(FIN)});')                               # back to the middle of the card: the mirror of the opening shot
J(f'tl.set("#fa", {{ opacity: 1 }}, {at(FIN, 2)});'); J(f'tl.fromTo("#fa", {{ yPercent: 108 }}, {{ yPercent: 0, duration: 0.36, ease: "power4.out", immediateRender: false }}, {at(FIN, 2)});')
hose_off(FIN)                                         # hose off; every hole patched; the floor dries
for k in range(4): patch_on(k, FIN, 4 + 3 * k, snd=(-12 if k == 0 else 0))
puddle(FIN, 6, 0, 0.5)
J(f'tl.set("#fb", {{ opacity: 1 }}, {at(f2)});'); J(f'tl.fromTo("#fb", {{ scaleX: 0.3 }}, {{ scaleX: 1, duration: 0.3, ease: "power4.out", immediateRender: false }}, {at(f2)});')
J(f'tl.fromTo("#fbt", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out", immediateRender: false }}, {at(f2, 3)});')
hose_on(f2, 2); s.sound(f2, 'transitions/whoosh.mp3', -17)                                                                     # then the hose, and it fills to the brim
fg = LV[-1][0] - 3                                    # full: the bucket and the card glow, the headline lands once more; then everything holds
glow_bucket(fg, True)
J(f'tl.to("#bkc", {{ borderColor: "rgba(47,111,237,0.8)", boxShadow: "0 26px 70px rgba(0,0,0,0.55), 0 0 64px rgba(47,111,237,0.38)", duration: 0.3, ease: "power2.out" }}, {at(fg)});')
J(f'tl.fromTo("#fin", {{ scale: 1 }}, {{ scale: 1.035, duration: 0.15, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(fg)});')
s.sound(fg, 'ui/click.wav', -12)
assert fg + 12 <= NF - 8 and f2 + 12 <= NF - 45, ('the takeaway must be complete and held', fg, f2, NF)

PL, PW = 452, 420                                      # the label column (card px)
s.css.append(f'''    .card.tall {{ top: 1244px; height: 352px; padding: 0; }}
    .bk {{ position: absolute; left: 10px; top: 0; overflow: visible; transform-origin: 0 100%; }}
    .pn {{ position: absolute; left: {PL}px; width: {PW}px; top: 26px; height: 300px; display: flex; flex-direction: column; justify-content: center; gap: 12px; opacity: 0; }}
    .plab {{ font-weight: 800; font-size: 30px; line-height: 36px; letter-spacing: -0.02em; color: rgba(242,239,233,0.62); white-space: nowrap; }}
    /* one row shape and one tile shape for every label */
    .rw {{ position: relative; height: 84px; flex: none; border-radius: 18px; background: rgba(242,239,233,0.05); border: 2px solid rgba(242,239,233,0.14); display: flex; align-items: center; justify-content: space-between;
          padding: 0 16px 0 22px; font-weight: 800; font-size: 32px; letter-spacing: -0.03em; color: #fff; white-space: nowrap; opacity: 0; }}
    .rw.num {{ justify-content: flex-start; gap: 16px; padding-left: 16px; }}  .rw.num .okr {{ margin-left: auto; }}
    .tl2 {{ height: 104px; flex: none; border-radius: 18px; background: #1D1E23; border: 2px solid rgba(47,111,237,0.75); display: flex; flex-direction: column; justify-content: center; padding: 0 22px; opacity: 0; }}
    .tl2 small {{ font-weight: 800; font-size: 22px; line-height: 26px; letter-spacing: 0.1em; text-transform: uppercase; color: #5B8DF3; }}
    .tl2 b {{ font-weight: 800; font-size: 40px; line-height: 46px; letter-spacing: -0.035em; color: #fff; white-space: nowrap; }}
    .okr.off {{ background: rgba(242,239,233,0.12); color: rgba(242,239,233,0); }}  .okr.bad {{ background: #F2EFE9; color: #0A0A0A; opacity: 0; }}
    .onum {{ width: 46px; height: 46px; flex: none; border-radius: 23px; border: 2px solid rgba(242,239,233,0.3); color: rgba(242,239,233,0.85); font-weight: 800; font-size: 26px; display: flex; align-items: center; justify-content: center; }}
    /* first 30 days */
    .dayb {{ font-weight: 900; font-size: 100px; line-height: 1; letter-spacing: -0.045em; color: #fff; white-space: nowrap; transform-origin: 0 50%; margin-top: -6px; }}
    .dayb b {{ display: inline-block; width: 132px; font-weight: 900; font-variant-numeric: tabular-nums; }}
    .tlw {{ position: relative; height: 54px; flex: none; margin-top: 6px; }}
    .tlt {{ position: absolute; left: 0; right: 0; top: 0; height: 14px; border-radius: 7px; background: rgba(242,239,233,0.12); overflow: hidden; }}
    .tlf {{ position: absolute; inset: 0; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0.012); }}
    .tlm {{ position: absolute; top: 22px; font-weight: 700; font-size: 26px; letter-spacing: -0.02em; color: rgba(242,239,233,0.6); white-space: nowrap; }}
    /* by hand / hose */
    .sg {{ display: grid; grid-template-columns: repeat({NSEG}, 30px); column-gap: 6px; height: 22px; }}  .sg i {{ border-radius: 6px; background: rgba(242,239,233,0.14); }}
    /* the takeaway, in the headline's place */
    .fin {{ position: absolute; left: 0; width: {CW}px; top: {PY - 226}px; text-align: center; transform-origin: 50% 60%; }}
    .fa {{ font-weight: 900; line-height: 1; letter-spacing: -0.02em; color: #fff; white-space: nowrap; }}
    .lkm {{ display: inline-block; overflow: hidden; padding: 0 6px 0.05em; }}  .lkm i {{ display: block; font-style: normal; opacity: 0; }}
    .fbw {{ margin-top: 10px; }}
    .fb {{ display: inline-block; background: #2F6FED; border-radius: 14px; padding: 10px 26px 14px; font-weight: 900; line-height: 1; letter-spacing: -0.02em; color: #fff; white-space: nowrap; transform-origin: 50% 50%; opacity: 0; }}
    .fb i {{ display: block; font-style: normal; opacity: 0; }}''')
for t, sz, w, lim in [('Your business', 40, 800, PW - 48), ('Biggest holes filled', 32, 800, PW - 42 - 40 - 10), ('On a leaky bucket', 32, 800, PW - 42 - 40 - 10), ('Hose (ads)', 32, 800, PW - 36 - 62 - 56),
                      ('Day 30', 100, 900, PW)]:
    assert text_width(t, sz, w, -0.03) <= lim, (t, round(text_width(t, sz, w, -0.03)), lim)
print('takeaway sizes', sa, sb, '| frames', NF, 'footage', NV, '| fix', FIN, 'hose', f2, 'full', LV[-1][0], '| sounds', len(s.sfx))
s.write()
