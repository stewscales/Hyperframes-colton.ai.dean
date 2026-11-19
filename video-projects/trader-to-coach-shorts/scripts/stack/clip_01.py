"""01 — The wrong order (stacked layout), v3: the "premium business education" pass.
Each section has ONE graphic that tells its part with the sound off, and the camera does a little work as well:
  HOOK         big headline + a room of new coaches on screen from the first frame; a 90-day timeline runs and they drop
               out along it until "Day 90: most have quit"
               -> "Why they quit": Trading skill fills and ticks (not the problem), Build order shows 3-1-2 and fails
               -> "WRONG | ORDER" behind his head, punch-in
  WRONG ORDER  "Month 1" dashboard: every function is switched on as he names it; Spend, Workload and Complexity each
               climb a notch with every one, and max out on "whoever"
  RIGHT ORDER  "From day 1": Content is ticked off day after day, Messages grow bar by bar, "By you"; both sit on the bar
               underneath, which fills until "What people actually want" is found (tick, glow)
  CTA          the 90-Day Blueprint as a real document (cover + pages) with its three contents ticking off, then the
               message: "DOC" typed, sent, and the Blueprint comes back. Last frame: document + thread, glowing.
Camera: slow drift inside every shot, a tighter frame on alternate jump cuts, small punch-ins on the key words and a
zoom-through (with a whoosh) on the three section changes. Nothing is cut or re-timed: the voice is the source of truth.
Run from the project folder: python3 -I scripts/stack/clip_01.py"""
exec(open('scripts/stack/kit.py').read())
s = Scene('01-wrong-order', 'The wrong order')
exec(open('scripts/stack/hook.py').read())
C1, C2, C3 = F(67), F(184), F(1770)                     # hook -> wrong order -> right order -> CTA
ST = s.E['starts']; assert len(ST) == 10 and (ST[2], ST[5], ST[8]) == (C1, C2, C3), ST
s.match = dict(ref=0, strength=0.8, only=[3])           # the CTA was shot at the end of the recording (warmer, brighter wall)
s.pinned_title('Most trading coaches', 'quit in 90 days', 0, C1, big=True)
s.pinned_title('The wrong order', 'spend first', C1, C2)
s.pinned_title('The right order', 'volume first', C2, C3)
s.pinned_title('Want it step by step?', 'DM me “DOC”', C3)

s.captions([
    (0,        'Most traders',                  'chest'),
    (F(2),     'who try coaching',              'chest'),
    (F(5),     'will *quit*',                   'chest'),
    (F(7),     'in the first',                  'chest'),
    (F(10),    '*90 days*',                     'chest'),
    (F(12),    "it's not because",              'chest'),
    (F(15),    "they *can't trade*",            'chest'),
    (F(18),    'they just build',               'chest'),
    (F(21),    'everything in the',             'chest', F(24)),          # then "WRONG | ORDER" behind his head
    (C1,       'Someone will get',              'chest'),
    (F(70),    'into coaching',                 'right'),
    (F(72),    "and they'll just *spend*",      'chest', F(76)),          # then "ALL THE | MONEY" behind his head
    (F(79),    'They turn on',                  'chest'),
    (F(82),    'their *ads*',                   'chest'),
    (F(84),    'they hire a *setter*',          'chest'),
    (F(88),    'they hire a *closer*',          'chest'),
    (F(92),    'they get a',                    'chest'),
    (F(95),    '*content manager*',             'chest'),
    (F(97),    'whoever',                       'right'),
    (C2,       'At the start',                  'chest'),
    (F(187),   "it's all about",                'chest', F(190)),         # then "VOLUME" behind his head
    (F(191),   'lots of *content*',             'chest'),
    (F(194),   'lots of *messages*',            'chest'),
    (F(197),   'and you do them',               'chest'),
    (F(201),   'by *yourself*',                 'chest'),
    (F(203),   "because that's how",            'chest'),
    (F(206),   'you find out',                  'chest'),
    (F(209),   'what people',                   'chest'),
    (F(211),   '*actually want*',               'chest'),
    (C3,       'If you want this',              'chest'),
    (F(1774),  'laid out',                      'left'),
    (F(1776),  '*step by step*',                'chest'),
    (F(1779),  'with *checklists*',             'chest'),
    (F(1781),  'the *important parts*',         'chest'),
    (F(1784),  'send me a *message*',           'chest'),
    (F(1788),  'saying *DOC*',                  'chest'),
    (F(1790),  "and I'll send",                 'chest'),
    (F(1793),  'you this over',                 'chest'),
])
s.behind_text(F(24), C1, 'wrong', 'order', si=0)
s.behind_text(F(76), F(79), 'all the', 'money', si=1)
s.behind_text(F(190), F(191), None, 'volume', si=2)

# ================= CAMERA =================
s.shot(ST[0], ST[1], 1.00, 1.03)                        # hook: slow push
for k in range(10): s.zoom[k] += 0.05 * (1 - k / 10) ** 2        # the first frames settle back with the headline
s.shot(ST[1], ST[2], 1.06, 1.075); s.punch(F(24), ST[2], 0.04)   # tighter for the diagnosis; punch on "wrong order"
s.shot(ST[2], ST[3], 1.00, 1.025); s.punch(F(76), ST[3], 0.04)   # punch on "all the money"
s.shot(ST[3], ST[4], 1.06, 1.075)                       # the list of hires: tighter
s.shot(ST[4], ST[5], 1.00, 1.03);  s.punch(F(97), ST[5], 0.05)   # punch on "whoever"
s.shot(ST[5], ST[6], 1.02, 1.04);  s.punch(F(190), ST[6], 0.04)  # punch on "volume"
s.shot(ST[6], ST[7], 1.085, 1.095)                      # "by yourself": close
s.shot(ST[7], ST[8], 1.00, 1.035)
s.shot(ST[8], ST[9], 1.00, 1.03);  s.punch(F(1784), ST[9], 0.03); s.punch(F(1789), ST[9], 0.03)   # "send me a message" / "DOC"
for c in (C1, C2, C3):                                  # section changes: zoom through the cut
    s.through(c, 0.06); s.sound(c, 'transitions/whoosh.mp3', -15)
assert s.zoom.max() <= 1.2 and s.zoom.min() >= 1.0, (s.zoom.min(), s.zoom.max())

J = s.js.append
def at(f, d=0): return round(tm(f) + d / 30, 4)
def pop(sel, f, d=0, frm='{ opacity: 0, scale: 0.4 }', dur=0.22, ease='back.out(2.4)'):
    J(f'tl.fromTo("{sel}", {frm}, {{ opacity: 1, scale: 1, x: 0, y: 0, duration: {dur}, ease: "{ease}", immediateRender: false }}, {at(f, d)});')
def glow(sel, f, d=0):
    J(f'tl.to("{sel}", {{ borderColor: "rgba(47,111,237,0.8)", boxShadow: "0 26px 70px rgba(0,0,0,0.55), 0 0 64px rgba(47,111,237,0.38)", duration: 0.3, ease: "power2.out" }}, {at(f, d)});')
    J(f'tl.fromTo("{sel}", {{ scale: 1 }}, {{ scale: 1.018, duration: 0.14, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(f, d)});')
def shake(sel, f, amp=10):
    for j, dx in enumerate([-amp, 0.8 * amp, -0.5 * amp, 0.3 * amp, 0]): J(f'tl.to("{sel}", {{ x: {dx:.1f}, duration: 0.05, ease: "power1.inOut" }}, {at(f, 1.5 * j)});')
SEND = '<svg viewBox="0 0 24 24"><path d="M12 19V6M6.5 11.5L12 6l5.5 5.5" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'

# ================= HOOK: 90 days, and who is left =================
import random
PERSON = '<svg viewBox="0 0 24 28"><circle cx="12" cy="7.5" r="5.5" fill="currentColor"/><path d="M2.5 27.5c0-6.6 4.2-10.5 9.5-10.5s9.5 3.9 9.5 10.5z" fill="currentColor"/></svg>'
NP, STAY = 24, 4; D0, D1 = 6, 66                      # the 90 days run over the first two seconds
s.front.append('<div id="pg" class="card tall" style="opacity:1"><div class="chead"><div id="pgA" class="clbl"><i class="dot a"></i>New trading coaches</div>'
               '<div id="pgB" class="clbl"><i class="dot b"></i>Most have quit</div><div id="dayc" class="dayc">Day <b id="dayn">1</b></div></div>'
               '<div class="pgrid">' + ''.join(f'<i id="p{k}" class="pp">{PERSON}</i>' for k in range(NP)) + '</div>'
               '<div class="tlw"><div class="tlt"><div id="tlf" class="tlf"></div></div>'
               '<span class="tlm" style="left:0">Day 1</span><span class="tlm" style="left:33.33%; transform:translateX(-50%)">30</span>'
               '<span class="tlm" style="left:66.67%; transform:translateX(-50%)">60</span><span id="tl90" class="tlm" style="right:0">90</span></div></div>')
J(f'tl.to("#dayn", {{ textContent: 90, snap: {{ textContent: 1 }}, duration: {(D1 - D0) / 30:.4f}, ease: "none" }}, {at(D0)});')
J(f'tl.to("#tlf", {{ scaleX: 1, duration: {(D1 - D0) / 30:.4f}, ease: "none" }}, {at(D0)});')
order = list(range(NP)); random.Random(11).shuffle(order); gone = order[:NP - STAY]
for n, k in enumerate(gone):                          # they drop out one by one along the timeline, faster towards the end
    f = D0 + 3 + (D1 - D0 - 5) * (n / (len(gone) - 1)) ** 0.8
    J(f'tl.to("#p{k}", {{ color: "rgba(242,239,233,0.13)", scale: 0.8, y: 7, duration: 0.24, ease: "power2.in" }}, {round(f / 30 - 0.001, 4)});')
J(f'tl.to("#pgA", {{ opacity: 0, y: -10, duration: 0.14, ease: "power2.in" }}, {at(D1, -3)});')                    # day 90
J(f'tl.fromTo("#pgB", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out", immediateRender: false }}, {at(D1)});')
J(f'tl.to("#dayc", {{ backgroundColor: "{BLUE}", borderColor: "{BLUE}", duration: 0.14 }}, {at(D1)});')
J(f'tl.fromTo("#dayc", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(D1)});')
J(f'tl.to("#tl90", {{ color: "#ffffff", duration: 0.14 }}, {at(D1)});')
s.sound(D1, 'ui/click.wav', -12)
card_out('#pg', F(12))

# ---- why they quit: not skill, order ----
s.front.append('<div id="dg" class="card tall"><div class="chead"><div class="clbl"><i class="dot b"></i>Why they quit</div></div>'
               f'<div class="dgr"><span class="dgl">Trading skill</span><div class="dgt"><div id="dgf" class="mf"></div></div><span id="dgk" class="okr off2">{TICK}</span></div>'
               '<div id="dgr2" class="dgr two"><span class="dgl">Build order</span><div class="dgo">' + ''.join(f'<b id="dgo{k}" class="dgn">{n}</b>' for k, n in enumerate('312')) +
               f'</div><span id="dgx" class="okr bad">{CROSS}</span></div></div>')
card_in('#dg', F(12), 0.24)
J(f'tl.to("#dgf", {{ scaleX: 1, duration: {(F(17) - F(15)) / 30 + 0.1:.4f}, ease: "power2.inOut" }}, {at(F(15))});')           # "they can't trade": the skill is there
pop('#dgk', F(17), 3, frm='{ opacity: 0, scale: 0.4 }', ease='back.out(3)'); s.sound(F(17) + 3, 'ui/click.wav', -11)
for k in range(3):                                    # "they just build": 3, 1, 2
    pop(f'#dgo{k}', F(18), 4 * k, frm='{ opacity: 0, scale: 0.6, y: -16 }', ease='back.out(2.2)'); s.sound(F(18) + 4 * k, 'ui/pop.mp3', -17)
fx = F(24)                                            # "wrong order"
pop('#dgx', fx, 2, frm='{ opacity: 0, scale: 0.4 }', ease='back.out(3)')
J(f'tl.to(".dgn", {{ backgroundColor: "#3A3B40", borderColor: "rgba(242,239,233,0.6)", duration: 0.16 }}, {at(fx)});')
J(f'tl.to("#dgr2", {{ backgroundColor: "rgba(242,239,233,0.07)", boxShadow: "0 0 0 3px rgba(242,239,233,0.5)", duration: 0.2 }}, {at(fx)});')
shake('#dgr2', fx)
s.sound(fx, 'impact/bass-drop.mp3', -16)
card_out('#dg', C1)

# ================= WRONG ORDER: the "Month 1" dashboard =================
funcs = [('Ads', F(83)), ('Setter', F(87)), ('Closer', F(91)), ('Content manager', F(95))]
meters = ['Spend', 'Workload', 'Complexity']; NS = 5
s.front.append('<div id="m1" class="card tall"><div class="chead"><div class="clbl"><i class="dot b"></i>Month 1</div><div id="m1w" class="pillb">+ whoever</div></div>'
               '<div class="fg">' + ''.join(f'<div class="fs"><div id="fn{k}" class="fn"><span class="fnn">{n}</span><span id="tg{k}" class="tg"><i id="tk{k}" class="tgk"></i></span></div></div>' for k, (n, _) in enumerate(funcs)) + '</div>'
               '<div class="mm">' + ''.join(f'<div class="mc"><div id="ml{j}" class="mlb">{m}</div><div class="segs">' + ''.join(f'<i id="sg{j}{n}"></i>' for n in range(NS)) + '</div></div>' for j, m in enumerate(meters)) + '</div></div>')
card_in('#m1', C1, 0.26)
def seg(j, n, f, d):
    J(f'tl.to("#sg{j}{n}", {{ backgroundColor: "{BLUE}", duration: 0.1 }}, {at(f, d)});')
    J(f'tl.fromTo("#sg{j}{n}", {{ scaleY: 1.8 }}, {{ scaleY: 1, duration: 0.24, ease: "power3.out", immediateRender: false }}, {at(f, d)});')
J(f'tl.to("#ml0", {{ color: "#ffffff", duration: 0.15 }}, {at(F(75))});')                        # "spend": the meter he is about to fill
J(f'tl.fromTo("#ml0", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(F(75))});')
s.sound(F(76), 'ui/pop.mp3', -14)                                                                  # "all the money" (behind his head)
for k, (n, f) in enumerate(funcs):                    # each function lands on its word and is switched on; every meter climbs a notch
    pop(f'#fn{k}', f, frm='{ opacity: 0, scale: 0.78, y: -18 }', dur=0.26, ease='back.out(2)')
    J(f'tl.to("#tg{k}", {{ backgroundColor: "{BLUE}", duration: 0.14 }}, {at(f, 4)});')
    J(f'tl.to("#tk{k}", {{ x: 28, backgroundColor: "#ffffff", duration: 0.16, ease: "power3.out" }}, {at(f, 4)});')
    J(f'tl.to("#fn{k}", {{ borderColor: "rgba(47,111,237,0.75)", duration: 0.16 }}, {at(f, 4)});')
    for j in range(3): seg(j, k, f, 5 + 2 * j)
    if k == 0: J(f'tl.to("#ml1, #ml2", {{ color: "#ffffff", duration: 0.15 }}, {at(f, 5)});')
    s.sound(f, 'ui/click.wav', -11)
fw = F(97)                                            # "whoever": everything maxed, all at once
pop('#m1w', fw, frm='{ opacity: 0, scale: 0.6, x: 14 }'); s.sound(fw, 'ui/pop.mp3', -13)
for j in range(3): seg(j, NS - 1, fw, 2 + 2 * j)
J(f'tl.to(".segs i", {{ backgroundColor: "{BONE}", duration: 0.18 }}, {at(fw, 9)});')
shake('#m1', fw + 9, 8)
card_out('#m1', C2)

# ================= RIGHT ORDER: "From day 1" =================
ND, NB = 14, 8; TK = TICK
s.front.append('<div id="v1" class="card tall"><div class="chead"><div class="clbl"><i class="dot a"></i>From day 1</div><div id="vby" class="pilla">By you</div></div>'
               '<div class="vg"><div><div id="vl0" class="mlb">Content</div><div class="cal">' + ''.join(f'<i id="vc{n}" class="vc">{TK}</i>' for n in range(ND)) + '</div></div>'
               '<div><div id="vl1" class="mlb">Messages</div><div class="bars">' + ''.join(f'<span class="vbs" style="height:{28 + 80 * n / (NB - 1):.0f}px"><i id="vb{n}" class="vbar"></i></span>' for n in range(NB)) + '</div></div></div>'
               f'<div class="vres"><div id="vrf" class="vrf"></div><span class="vrt">What people actually want</span><span id="vrk" class="okr inv">{TICK}</span></div></div>')
card_in('#v1', C2, 0.26)
fc = F(191)                                           # "lots of content": one a day, every day
J(f'tl.to("#vl0", {{ color: "#ffffff", duration: 0.15 }}, {at(fc)});'); s.sound(fc, 'ui/click.wav', -13)
for n in range(ND):
    J(f'tl.to("#vc{n}", {{ backgroundColor: "{BLUE}", borderColor: "{BLUE}", color: "#ffffff", duration: 0.1 }}, {at(fc, 4 * n)});')
    J(f'tl.fromTo("#vc{n}", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.22, ease: "back.out(2.6)", immediateRender: false }}, {at(fc, 4 * n)});')
fb = F(194)                                           # "lots of messages": more every time
J(f'tl.to("#vl1", {{ color: "#ffffff", duration: 0.15 }}, {at(fb)});'); s.sound(fb, 'ui/click.wav', -13)
for n in range(NB): J(f'tl.to("#vb{n}", {{ scaleY: 1, duration: 0.3, ease: "back.out(1.7)" }}, {at(fb, 4 * n)});')
assert fc + 4 * ND <= F(203) and fb + 4 * NB <= F(203)
pop('#vby', F(201), frm='{ opacity: 0, scale: 0.6, x: 14 }'); s.sound(F(201), 'ui/pop.mp3', -14)          # "by yourself"
J(f'tl.fromTo("#vrf", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {(F(210) - F(203)) / 30:.4f}, ease: "power2.inOut", immediateRender: false }}, {at(F(203))});')   # "because that's how you find out what people..."
J(f'tl.to(".vrt", {{ color: "#ffffff", duration: 0.2 }}, {at(F(206))});')
pop('#vrk', F(210), 1, ease='back.out(3)'); s.sound(F(210) + 1, 'ui/click.wav', -11)         # "actually want": found
glow('#v1', F(210), 4)
card_out('#v1', C3)

# ================= CTA: the Blueprint, then the message =================
MINI = '<span class="mini"><i></i></span>'
rows = [('Step by step', F(1776)), ('Checklists', F(1780)), ('The important parts', F(1782))]
s.front.append('<div id="d1" class="card tall">'
               '<div id="dmk" class="dmk"><div id="pg2" class="pg2"></div><div class="cov"><div class="cvb"><span class="cvk">90</span><span class="cvd">DAY</span></div>'
               '<div class="cvt">Blueprint</div>' + ''.join(f'<div class="cvr"><i></i><b style="width:{w}px"></b></div>' for w in (132, 150, 104)) + '<div class="cvf"></div><div id="shn" class="shn"></div></div></div>'
               '<div id="dls" class="dls"><div class="dtt">90-Day Blueprint</div>' +
               ''.join(f'<div class="drow"><span id="dk{k}" class="okr off">{TICK}</span><span id="dl{k}" class="dl">{n}</span></div>' for k, (n, _) in enumerate(rows)) + '</div>'
               '<div id="thr" class="thr"><div id="hint" class="hint">Send the word <b>DOC</b></div>'
               '<div id="bo" class="bub out">DOC</div>'
               f'<div id="bi" class="bub in">{MINI}90-Day Blueprint</div>'
               f'<div class="inp"><span id="ph" class="ph">Message</span><span class="ty"><b id="ty0">D</b><b id="ty1">O</b><b id="ty2">C</b></span><span id="snd" class="snd">{SEND}</span></div></div></div>')
card_in('#d1', C3, 0.26)
J(f'tl.fromTo("#dmk", {{ y: 70, rotation: -13, opacity: 0 }}, {{ y: 0, rotation: -5, opacity: 1, duration: 0.42, ease: "back.out(1.5)", immediateRender: false }}, {at(C3, 2)});')    # the document slides up out of the card
J(f'tl.fromTo("#pg2", {{ rotation: 0, x: 0 }}, {{ rotation: 7, x: 14, duration: 0.4, ease: "power3.out", immediateRender: false }}, {at(C3, 8)});')                               # its pages fan out behind the cover
J(f'tl.fromTo("#shn", {{ x: 0 }}, {{ x: 620, duration: 0.6, ease: "power2.inOut", immediateRender: false }}, {at(C3, 14)});')                                                    # one pass of light over the cover
for k, (n, f) in enumerate(rows):                     # the three things he lists tick off as he says them
    J(f'tl.to("#dk{k}", {{ backgroundColor: "{BLUE}", color: "#ffffff", duration: 0.14 }}, {at(f)});')
    J(f'tl.fromTo("#dk{k}", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.22, ease: "back.out(2.8)", immediateRender: false }}, {at(f)});')
    J(f'tl.to("#dl{k}", {{ color: "#ffffff", duration: 0.14 }}, {at(f)});')
    s.sound(f, 'ui/click.wav', -12)
fm = F(1784)                                          # "send me a message": the list becomes the conversation (the document stays)
J(f'tl.to("#dls", {{ opacity: 0, y: -22, duration: 0.16, ease: "power2.in" }}, {at(fm, -4)});')
J(f'tl.fromTo("#thr", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.24, ease: "power3.out", immediateRender: false }}, {at(fm)});')
ft = F(1789)                                          # "doc": typed letter by letter
J(f'tl.to("#ph", {{ opacity: 0, duration: 0.06 }}, {at(ft)});')
for k in range(3):
    J(f'tl.set("#ty{k}", {{ opacity: 1 }}, {at(ft, 3 * k)});'); s.sound(ft + 3 * k, 'ui/click.wav', -17)
J(f'tl.to("#snd", {{ backgroundColor: "{BLUE}", color: "#ffffff", duration: 0.12 }}, {at(ft)});')
fs2 = F(1790)                                         # sent
J(f'tl.fromTo("#snd", {{ scale: 0.8 }}, {{ scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, {at(fs2)});')
J(f'tl.to("#ty0, #ty1, #ty2", {{ opacity: 0, duration: 0.08 }}, {at(fs2)});')
J(f'tl.to("#hint", {{ opacity: 0, y: -10, duration: 0.12, ease: "power2.in" }}, {at(fs2, -2)});')
J(f'tl.to("#ph", {{ opacity: 1, duration: 0.12 }}, {at(fs2, 3)});')
J(f'tl.to("#snd", {{ backgroundColor: "rgba(242,239,233,0.14)", color: "rgba(242,239,233,0.6)", duration: 0.2 }}, {at(fs2, 4)});')
pop('#bo', fs2, 1, frm='{ opacity: 0, scale: 0.7, y: 70 }', dur=0.28, ease='back.out(1.6)'); s.sound(fs2, 'ui/send-message.mp3', -14)
fr = F(1792) + 3                                      # "...send you this over": the Blueprint arrives
pop('#bi', fr, frm='{ opacity: 0, scale: 0.8, x: -30 }', dur=0.3, ease='back.out(1.8)'); s.sound(fr, 'ui/notification.mp3', -14)
J(f'tl.fromTo("#dmk", {{ scale: 1 }}, {{ scale: 1.05, duration: 0.16, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(fr, 4)});')     # this is what arrives
glow('#d1', fr, 8)
assert fr + 8 + 9 <= s.NF - 9, 'the last frame must be finished and held'

s.css.append('''    .card.tall { top: 1244px; height: 352px; padding: 26px 28px; }
    .pillb, .pilla { position: absolute; right: 0; top: 2px; font-weight: 800; font-size: 30px; letter-spacing: -0.02em; padding: 3px 20px 5px; border-radius: 22px; opacity: 0; }
    .pillb { background: #F2EFE9; color: #0A0A0A; }  .pilla { background: #2F6FED; color: #fff; }
    .mlb { height: 34px; font-weight: 800; font-size: 28px; letter-spacing: -0.02em; color: rgba(242,239,233,0.6); transform-origin: 0 50%; white-space: nowrap; }
    .mf { position: absolute; inset: 0; border-radius: 12px; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0); }
    /* hook: 90 days, and who is left */
    #pgB { opacity: 0; }
    .dayc { position: absolute; right: 0; top: 0; height: 48px; padding: 0 20px; border-radius: 24px; border: 2px solid rgba(242,239,233,0.24); background: rgba(242,239,233,0.06); color: #fff; font-weight: 800; font-size: 32px; letter-spacing: -0.02em; line-height: 44px; white-space: nowrap; }
    .dayc b { display: inline-block; width: 44px; text-align: right; font-weight: 800; font-variant-numeric: tabular-nums; }
    .pgrid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px 0; margin-top: 16px; justify-items: center; }
    .pp { width: 58px; height: 68px; color: #2F6FED; display: block; }  .pp svg { width: 58px; height: 68px; display: block; }
    .tlw { position: relative; margin-top: 22px; height: 54px; }
    .tlt { position: absolute; left: 0; right: 0; top: 0; height: 12px; border-radius: 6px; background: rgba(242,239,233,0.12); overflow: hidden; }
    .tlf { position: absolute; inset: 0; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0.012); }
    .tlm { position: absolute; top: 20px; font-weight: 700; font-size: 26px; letter-spacing: -0.02em; color: rgba(242,239,233,0.6); white-space: nowrap; }
    /* hook: why they quit */
    .dgr { display: grid; grid-template-columns: 250px 1fr 40px; column-gap: 22px; align-items: center; height: 84px; margin-top: 16px; padding: 0 18px; border-radius: 20px; background: rgba(242,239,233,0.05); border: 2px solid rgba(242,239,233,0.10); }
    .dgl { font-weight: 800; font-size: 34px; letter-spacing: -0.03em; color: #fff; white-space: nowrap; }
    .dgt { position: relative; height: 24px; border-radius: 12px; background: rgba(242,239,233,0.10); }
    .okr.off2 { opacity: 0; }  .okr.bad { background: #F2EFE9; color: #0A0A0A; opacity: 0; }
    .dgo { display: flex; gap: 14px; }
    .dgn { width: 96px; height: 56px; border-radius: 16px; background: #2F6FED; border: 2px solid #2F6FED; color: #fff; font-weight: 800; font-size: 36px; display: flex; align-items: center; justify-content: center; opacity: 0; }
    /* month 1: the dashboard */
    .fg { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 12px; margin-top: 14px; }
    .fs { height: 66px; border-radius: 16px; border: 2px dashed rgba(242,239,233,0.18); }
    .fn { height: 66px; margin: -2px; border-radius: 16px; background: #1D1E23; border: 2px solid rgba(242,239,233,0.2); display: flex; align-items: center; justify-content: space-between; padding: 0 14px 0 22px; opacity: 0; }
    .fnn { font-weight: 800; font-size: 30px; letter-spacing: -0.02em; color: #fff; white-space: nowrap; }
    .tg { position: relative; width: 62px; height: 34px; border-radius: 17px; background: rgba(242,239,233,0.18); flex: none; }
    .tgk { position: absolute; left: 4px; top: 4px; width: 26px; height: 26px; border-radius: 13px; background: #F2EFE9; }
    .mm { display: grid; grid-template-columns: repeat(3, 1fr); column-gap: 24px; margin-top: 22px; }
    .segs { display: grid; grid-template-columns: repeat(5, 1fr); column-gap: 6px; height: 20px; margin-top: 8px; }
    .segs i { border-radius: 6px; background: rgba(242,239,233,0.12); }
    /* day 1: volume */
    .vg { display: grid; grid-template-columns: 408px 404px; justify-content: space-between; margin-top: 16px; }
    .cal { display: grid; grid-template-columns: repeat(7, 48px); gap: 10px 12px; margin-top: 8px; }
    .vc { height: 49px; border-radius: 10px; background: rgba(242,239,233,0.06); border: 2px solid rgba(242,239,233,0.14); display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0); }  .vc svg { width: 24px; height: 24px; }
    .bars { display: flex; align-items: flex-end; gap: 12px; height: 108px; margin-top: 8px; }
    .vbs { position: relative; width: 40px; border-radius: 8px; background: rgba(242,239,233,0.07); display: block; }
    .vbar { position: absolute; inset: 0; border-radius: 8px; background: #2F6FED; transform-origin: 50% 100%; transform: scaleY(0); }
    .vres { position: relative; margin-top: 18px; height: 68px; border-radius: 18px; background: rgba(242,239,233,0.07); border: 2px solid rgba(242,239,233,0.14); overflow: hidden; display: flex; align-items: center; justify-content: space-between; padding: 0 14px 0 24px; }
    .vrf { position: absolute; inset: 0; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0); }
    .vrt { position: relative; font-weight: 800; font-size: 34px; letter-spacing: -0.03em; color: rgba(242,239,233,0.6); }
    .okr.inv { position: relative; background: #fff; color: #2F6FED; opacity: 0; }
    /* the Blueprint: a document, not an icon */
    .dmk { position: absolute; left: 36px; top: -46px; width: 236px; height: 330px; transform: rotate(-5deg); transform-origin: 50% 80%; opacity: 0; }
    .pg2 { position: absolute; inset: 0; border-radius: 10px; background: #CFCBC2; box-shadow: 0 14px 30px rgba(0,0,0,0.5); transform-origin: 50% 100%; }
    .cov { position: absolute; inset: 0; border-radius: 10px; background: #F2EFE9; overflow: hidden; box-shadow: 0 20px 44px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,0,0,0.25); }
    .cvb { height: 156px; background: #2F6FED; padding: 18px 20px 0; }
    .cvk { display: block; font-weight: 900; font-size: 104px; line-height: 0.86; letter-spacing: -0.06em; color: #fff; }
    .cvd { display: block; margin-top: 8px; font-weight: 800; font-size: 28px; letter-spacing: 0.22em; color: #fff; }
    .cvt { padding: 14px 20px 4px; font-weight: 800; font-size: 34px; letter-spacing: -0.035em; color: #0A0A0A; }
    .cvr { display: flex; align-items: center; gap: 10px; margin: 11px 20px 0; }  .cvr i { width: 16px; height: 16px; border-radius: 4px; background: #2F6FED; flex: none; }  .cvr b { height: 8px; border-radius: 4px; background: #C4C0B7; display: block; }
    .cvf { position: absolute; left: 0; right: 0; bottom: 0; height: 8px; background: #2F6FED; }
    .shn { position: absolute; top: -20%; left: -70%; width: 34%; height: 140%; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.5), rgba(255,255,255,0)); transform: skewX(-18deg); }
    .dls { position: absolute; left: 336px; right: 28px; top: 44px; }
    .dtt { font-weight: 800; font-size: 44px; letter-spacing: -0.035em; color: #fff; white-space: nowrap; }
    .drow { display: flex; align-items: center; gap: 16px; margin-top: 20px; }
    .okr.off { background: rgba(242,239,233,0.12); color: rgba(242,239,233,0); }
    .dl { font-weight: 700; font-size: 34px; letter-spacing: -0.03em; color: rgba(242,239,233,0.55); white-space: nowrap; }
    /* the message */
    .thr { position: absolute; left: 336px; right: 28px; top: 22px; height: 308px; opacity: 0; }
    .hint { position: absolute; left: 0; right: 0; top: 84px; text-align: center; font-weight: 700; font-size: 44px; letter-spacing: -0.03em; color: rgba(242,239,233,0.6); white-space: nowrap; }  .hint b { color: #fff; font-weight: 800; }
    .bub { position: absolute; display: flex; align-items: center; font-weight: 800; letter-spacing: -0.03em; white-space: nowrap; opacity: 0; }
    .bub.out { right: 0; top: 20px; height: 66px; padding: 0 30px; border-radius: 33px 33px 10px 33px; background: #2F6FED; color: #fff; font-size: 38px; transform-origin: 100% 100%; }
    .bub.in { left: 0; top: 108px; height: 92px; padding: 0 28px 0 18px; gap: 16px; border-radius: 30px 30px 30px 10px; background: #26272C; border: 2px solid rgba(242,239,233,0.12); color: #fff; font-size: 34px; transform-origin: 0 100%; }
    .mini { display: block; width: 46px; height: 62px; border-radius: 5px; background: #F2EFE9; overflow: hidden; flex: none; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }  .mini i { display: block; height: 28px; background: #2F6FED; }
    .inp { position: absolute; left: 0; right: 0; bottom: 0; height: 68px; border-radius: 34px; border: 2px solid rgba(242,239,233,0.2); background: rgba(242,239,233,0.05); display: flex; align-items: center; padding: 0 8px 0 28px; }
    .ph { position: absolute; left: 28px; font-weight: 600; font-size: 32px; letter-spacing: -0.02em; color: rgba(242,239,233,0.4); }
    .ty { font-weight: 800; font-size: 36px; letter-spacing: 0.01em; color: #fff; }  .ty b { opacity: 0; font-weight: 800; }
    .snd { margin-left: auto; width: 52px; height: 52px; border-radius: 26px; background: rgba(242,239,233,0.14); color: rgba(242,239,233,0.6); display: flex; align-items: center; justify-content: center; }  .snd svg { width: 28px; height: 28px; }''')
for t, sz, w, lim in [('Content manager', 30, 800, 416 - 36 - 62 - 16), ('90-Day Blueprint', 44, 800, 536), ('The important parts', 34, 700, 536 - 56), ('Send the word DOC', 44, 700, 536),
                      ('What people actually want', 34, 800, 844 - 100), ('Blueprint', 34, 800, 196), ('New trading coaches', 36, 800, 844 - 190), ('Complexity', 28, 800, 265)]:
    assert text_width(t, sz, w, -0.03) <= lim, (t, text_width(t, sz, w, -0.03), lim)
s.write()
