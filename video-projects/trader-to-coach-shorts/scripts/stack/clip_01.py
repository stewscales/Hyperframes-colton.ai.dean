"""01 — The wrong order (stacked layout). Opens with the shared hook, then three sections, each with ONE graphic that tells its part:
  WRONG ORDER  "Month one" card: every hire lands as he names it and the Spend bar climbs to full, while Proven stays empty ("?")
               + "ALL THE | MONEY" behind his head
  RIGHT ORDER  "Day one: volume" card: Content and Messages fill tile by tile, tagged "By you", and feed the bar underneath until
               "What people actually want" is found  + "VOLUME" behind his head
  CTA          the 90-Day Blueprint ticks off (step by step / checklists / the important parts), then becomes a message thread:
               "DOC" is typed and sent, and the Blueprint comes back. Last frame: the thread, glowing.
Run from the project folder: python3 -I scripts/stack/clip_01.py"""
exec(open('scripts/stack/kit.py').read())
s = Scene('01-wrong-order', 'The wrong order')
exec(open('scripts/stack/hook.py').read())
C1, C2, C3 = F(67), F(184), F(1770)                     # hook -> wrong order -> right order -> CTA
s.match = dict(ref=0, strength=0.8, only=[3])           # the CTA was shot at the end of the recording (warmer, brighter wall)
add_hook(C1)
s.pinned_title('The wrong order', 'spend first', C1, C2)
s.pinned_title('The right order', 'volume first', C2, C3)
s.pinned_title('Want it step by step?', 'Message me “DOC”', C3)

s.captions(HOOK_CAPTIONS(C1) + [
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
s.behind_text(F(76), F(79), 'all the', 'money', si=1)
s.behind_text(F(190), F(191), None, 'volume', si=2)
s.sound(F(76), 'transitions/whoosh.mp3', -15)
s.sound(F(190), 'transitions/whoosh.mp3', -15)

J = s.js.append
def at(f, d=0): return round(tm(f) + d / 30, 4)
def pop(sel, f, d=0, frm='{ opacity: 0, scale: 0.4 }', dur=0.22, ease='back.out(2.4)'):
    J(f'tl.fromTo("{sel}", {frm}, {{ opacity: 1, scale: 1, x: 0, y: 0, duration: {dur}, ease: "{ease}", immediateRender: false }}, {at(f, d)});')
def glow(sel, f, d=0):
    J(f'tl.to("{sel}", {{ borderColor: "rgba(47,111,237,0.8)", boxShadow: "0 26px 70px rgba(0,0,0,0.55), 0 0 64px rgba(47,111,237,0.38)", duration: 0.3, ease: "power2.out" }}, {at(f, d)});')
    J(f'tl.fromTo("{sel}", {{ scale: 1 }}, {{ scale: 1.018, duration: 0.14, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(f, d)});')
DOC = ('<svg viewBox="0 0 48 60"><path d="M6 2h24l12 12v40a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V6a4 4 0 0 1 4-4z" fill="#F2EFE9"/><path d="M30 2v9a3 3 0 0 0 3 3h9z" fill="#C9C5BC"/>'
       '<path d="M11 26h26M11 35h26M11 44h17" stroke="#2F6FED" stroke-width="3.6" stroke-linecap="round"/></svg>')
SEND = '<svg viewBox="0 0 24 24"><path d="M12 19V6M6.5 11.5L12 6l5.5 5.5" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'

# ================= WRONG ORDER: "Month one" =================
items = [('Ads', F(83)), ('Setter', F(87)), ('Closer', F(91)), ('Content manager', F(95))]
s.front.append('<div id="m1" class="card tall"><div class="chead"><div class="clbl"><i class="dot b"></i>Month one</div><div id="m1w" class="pillb">+ whoever</div></div>'
               '<div class="g4">' + ''.join(f'<div class="g4s"><div id="m1c{k}" class="g4c">{n}</div></div>' for k, (n, _) in enumerate(items)) + '</div>'
               '<div class="mt"><span id="m1sl" class="ml">Spend</span><div class="mtr"><div id="m1s" class="mf"></div></div></div>'
               '<div class="mt"><span class="ml">Proven</span><div class="mtr"><span id="m1q" class="q qin">?</span></div></div></div>')
card_in('#m1', C1, 0.26)
J(f'tl.to("#m1sl", {{ color: "#ffffff", duration: 0.15 }}, {at(F(75))});')                       # "spend"
for k, (n, f) in enumerate(items):                    # each hire lands on its word; the spend bar climbs a quarter each time
    pop(f'#m1c{k}', f, frm='{ opacity: 0, scale: 0.7, y: -18 }', dur=0.26, ease='back.out(2)')
    J(f'tl.to("#m1s", {{ scaleX: {(k + 1) / 4}, duration: 0.3, ease: "power3.out" }}, {at(f, 2)});')
    s.sound(f, 'ui/click.wav', -11)
fw = F(97)                                            # "whoever": all spend, nothing proven
pop('#m1w', fw, frm='{ opacity: 0, scale: 0.6, x: 14 }'); s.sound(fw, 'ui/pop.mp3', -14)
J(f'tl.to("#m1s", {{ backgroundColor: "{BONE}", duration: 0.2 }}, {at(fw, 5)});')
pop('#m1q', fw, 7, frm='{ opacity: 0, scale: 0.3 }', ease='back.out(3)')
card_out('#m1', C2)

# ================= RIGHT ORDER: "Day one: volume" =================
NT = 10
def vrow(k, name):
    return (f'<div class="vrow"><div class="vchip">{name}</div><div class="vts">' + ''.join(f'<i id="v{k}t{c}" class="vt"></i>' for c in range(NT)) +
            f'</div><div id="vy{k}" class="vby">By you</div></div>')
s.front.append('<div id="v1" class="card vol"><div class="chead"><div class="clbl"><i class="dot a"></i>Day one: volume</div></div>'
               f'{vrow(0, "Content")}{vrow(1, "Messages")}'
               f'<div class="vres"><div id="vrf" class="vrf"></div><span class="vrt">What people actually want</span><span id="vrk" class="okr inv">{TICK}</span></div></div>')
card_in('#v1', C2, 0.26)
for k, (f0, f1) in enumerate([(F(191), F(194)), (F(194), F(197))]):       # "lots of content" / "lots of messages": the rows fill tile by tile
    step = (f1 - f0 - 6) / (NT - 1)
    for c in range(NT):
        J(f'tl.to("#v{k}t{c}", {{ backgroundColor: "{BLUE}", borderColor: "{BLUE}", duration: 0.12 }}, {at(f0, c * step)});')
        J(f'tl.fromTo("#v{k}t{c}", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.2, ease: "back.out(2.6)", immediateRender: false }}, {at(f0, c * step)});')
    s.sound(f0, 'ui/click.wav', -13)
for k in range(2):                                    # "by yourself"
    pop(f'#vy{k}', F(201), 3 * k, frm='{ opacity: 0, scale: 0.6, x: -12 }')
s.sound(F(201), 'ui/pop.mp3', -14)
J(f'tl.fromTo("#vrf", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {(F(211) - F(206)) / 30:.4f}, ease: "power2.inOut", immediateRender: false }}, {at(F(206))});')   # "you find out what people..."
J(f'tl.to(".vrt", {{ color: "#ffffff", duration: 0.2 }}, {at(F(209))});')
pop('#vrk', F(211), 2, ease='back.out(3)'); s.sound(F(211) + 2, 'ui/click.wav', -11)        # "actually want": found
glow('#v1', F(211), 4)
card_out('#v1', C3)

# ================= CTA: the Blueprint, then the message =================
rows = [('Step by step', F(1776)), ('Checklists', F(1780)), ('The important parts', F(1782))]
s.front.append('<div id="d1" class="card tall">'
               f'<div id="doc" class="docw"><div class="dico">{DOC}</div><div class="dtx"><div class="dtt">90-Day Blueprint</div>' +
               ''.join(f'<div class="drow"><span id="dk{k}" class="okr off">{TICK}</span><span id="dl{k}" class="dl">{n}</span></div>' for k, (n, _) in enumerate(rows)) + '</div></div>'
               '<div id="thr" class="thr"><div class="thh">Direct message</div><div id="hint" class="hint">Send the word <b>DOC</b></div>'
               '<div id="bo" class="bub out">DOC</div>'
               f'<div id="bi" class="bub in"><span class="mdoc">{DOC}</span>90-Day Blueprint</div>'
               f'<div class="inp"><span id="ph" class="ph">Message</span><span class="ty"><b id="ty0">D</b><b id="ty1">O</b><b id="ty2">C</b></span><span id="snd" class="snd">{SEND}</span></div></div></div>')
card_in('#d1', C3, 0.26)
for k, (n, f) in enumerate(rows):                     # the three things he lists tick off as he says them
    J(f'tl.to("#dk{k}", {{ backgroundColor: "{BLUE}", color: "#ffffff", duration: 0.14 }}, {at(f)});')
    J(f'tl.fromTo("#dk{k}", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.22, ease: "back.out(2.8)", immediateRender: false }}, {at(f)});')
    J(f'tl.to("#dl{k}", {{ color: "#ffffff", duration: 0.14 }}, {at(f)});')
    s.sound(f, 'ui/click.wav', -12)
fm = F(1784)                                          # "send me a message": the card becomes the conversation
J(f'tl.to("#doc", {{ opacity: 0, y: -22, duration: 0.16, ease: "power2.in" }}, {at(fm, -4)});')
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
glow('#d1', fr, 8)
assert fr + 8 + 9 <= s.NF - 9, 'the last frame must be finished and held'

s.css.append('''    .card.tall { top: 1244px; height: 352px; padding: 26px 28px; }
    .card.vol { top: 1244px; height: 352px; padding: 26px 28px; }
    /* month one */
    .pillb { position: absolute; right: 0; top: 2px; background: #F2EFE9; color: #0A0A0A; font-weight: 800; font-size: 30px; letter-spacing: -0.02em; padding: 3px 20px 5px; border-radius: 22px; opacity: 0; }
    .g4 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 14px; margin-top: 14px; }
    .g4s { height: 58px; border-radius: 16px; border: 2px dashed rgba(242,239,233,0.2); }
    .g4c { height: 58px; margin: -2px; border-radius: 16px; background: #2F6FED; color: #fff; font-weight: 800; font-size: 32px; letter-spacing: -0.02em; display: flex; align-items: center; justify-content: center; opacity: 0; }
    .mt { display: grid; grid-template-columns: 150px 1fr; align-items: center; margin-top: 16px; height: 36px; }
    .ml { font-weight: 800; font-size: 30px; letter-spacing: -0.02em; color: rgba(242,239,233,0.6); }
    .mtr { position: relative; height: 22px; border-radius: 11px; background: rgba(242,239,233,0.10); }
    .mf { position: absolute; inset: 0; border-radius: 11px; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0); }
    .q.qin { right: auto; left: 10px; top: -8px; }
    /* day one: volume */
    .vrow { display: grid; grid-template-columns: 196px 458px 150px; column-gap: 20px; align-items: center; height: 56px; margin-top: 12px; }
    .vchip { height: 56px; border-radius: 16px; background: rgba(242,239,233,0.10); border: 2px solid rgba(242,239,233,0.22); color: #fff; font-weight: 800; font-size: 32px; letter-spacing: -0.02em; display: flex; align-items: center; justify-content: center; }
    .vts { display: grid; grid-template-columns: repeat(10, 1fr); column-gap: 8px; height: 56px; }
    .vt { border-radius: 10px; background: rgba(242,239,233,0.06); border: 2px solid rgba(242,239,233,0.14); }
    .vby { font-weight: 800; font-size: 30px; letter-spacing: -0.02em; color: #fff; opacity: 0; white-space: nowrap; }
    .vres { position: relative; margin-top: 18px; height: 66px; border-radius: 18px; background: rgba(242,239,233,0.07); border: 2px solid rgba(242,239,233,0.14); overflow: hidden; display: flex; align-items: center; justify-content: space-between; padding: 0 16px 0 24px; }
    .vrf { position: absolute; inset: 0; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0); }
    .vrt { position: relative; font-weight: 800; font-size: 34px; letter-spacing: -0.03em; color: rgba(242,239,233,0.6); }
    .okr.inv { position: relative; background: #fff; color: #2F6FED; opacity: 0; }
    /* the Blueprint */
    .docw { position: absolute; left: 28px; right: 28px; top: 26px; display: grid; grid-template-columns: 210px 1fr; column-gap: 30px; align-items: center; height: 300px; }
    .dico { height: 262px; display: flex; align-items: center; justify-content: center; }  .dico svg { height: 248px; filter: drop-shadow(0 12px 26px rgba(0,0,0,0.5)); }
    .dtt { font-weight: 800; font-size: 46px; letter-spacing: -0.035em; color: #fff; white-space: nowrap; }
    .drow { display: flex; align-items: center; gap: 16px; margin-top: 18px; }
    .okr.off { background: rgba(242,239,233,0.12); color: rgba(242,239,233,0); }
    .dl { font-weight: 700; font-size: 34px; letter-spacing: -0.03em; color: rgba(242,239,233,0.55); white-space: nowrap; }
    /* the message */
    .thr { position: absolute; left: 28px; right: 28px; top: 22px; height: 308px; opacity: 0; }
    .thh { font-weight: 700; font-size: 28px; letter-spacing: -0.02em; color: rgba(242,239,233,0.55); height: 36px; }
    .hint { position: absolute; left: 0; right: 0; top: 92px; text-align: center; font-weight: 700; font-size: 44px; letter-spacing: -0.03em; color: rgba(242,239,233,0.5); }  .hint b { color: #fff; font-weight: 800; }
    .bub { position: absolute; display: flex; align-items: center; font-weight: 800; letter-spacing: -0.03em; white-space: nowrap; opacity: 0; }
    .bub.out { right: 0; top: 44px; height: 66px; padding: 0 30px; border-radius: 33px 33px 10px 33px; background: #2F6FED; color: #fff; font-size: 38px; transform-origin: 100% 100%; }
    .bub.in { left: 0; top: 124px; height: 84px; padding: 0 30px 0 18px; gap: 16px; border-radius: 30px 30px 30px 10px; background: #26272C; border: 2px solid rgba(242,239,233,0.12); color: #fff; font-size: 36px; transform-origin: 0 100%; }
    .mdoc { display: flex; }  .mdoc svg { height: 58px; }
    .inp { position: absolute; left: 0; right: 0; bottom: 0; height: 68px; border-radius: 34px; border: 2px solid rgba(242,239,233,0.2); background: rgba(242,239,233,0.05); display: flex; align-items: center; padding: 0 8px 0 28px; }
    .ph { position: absolute; left: 28px; font-weight: 600; font-size: 32px; letter-spacing: -0.02em; color: rgba(242,239,233,0.4); }
    .ty { font-weight: 800; font-size: 36px; letter-spacing: 0.01em; color: #fff; }  .ty b { opacity: 0; font-weight: 800; }
    .snd { margin-left: auto; width: 52px; height: 52px; border-radius: 26px; background: rgba(242,239,233,0.14); color: rgba(242,239,233,0.6); display: flex; align-items: center; justify-content: center; }  .snd svg { width: 28px; height: 28px; }''')
s.write()
