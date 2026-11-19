"""08 — One thing at a time, opened with the hook from 01 (stacked layout).
Edits, in order:
  HOOK   pinned title  ->  "90 | DAYS" behind his head + day counter card running to 90 ("Quit")  ->  "Why they quit" card:
         "They can't trade" struck out, "They build in the wrong order" lit  ->  "WRONG | ORDER" behind his head
  RULE   new pinned title  ->  "ONE | THING" behind his head  ->  4-step loop card lighting up on each word (Add / Wait / Check / Next)
         ->  week card: ads switched on + three hires dropped into the same week  ->  "something broke": question marks on
         every change  ->  "BROKE" beside / behind his head.
Run from the project folder: python3 -I scripts/stack/clip_08.py"""
exec(open('scripts/stack/kit.py').read())
s = Scene('08-one-thing-at-a-time', 'One thing at a time')
exec(open('scripts/stack/hook.py').read())
CUT = F(1640)                                          # hook -> rule
s.match = dict(ref=1, strength=0.8)                    # the hook was shot earlier in the recording (bluer, darker wall): match it to the rest
add_hook(CUT)
s.pinned_title('The rule for scaling', 'your coaching business', CUT)

# ---- captions (word for word), moving between spots ----
s.captions(HOOK_CAPTIONS(CUT) + [
    (CUT,      'Do it',                         'chest', F(1642)),        # then "ONE | THING" behind his head
    (F(1644),  'at a time',                     'chest'),
    (F(1647),  '*Add* one thing',               'chest'),
    (F(1650),  '*wait*',                        'chest'),
    (F(1651),  '*check* if it worked',          'chest'),
    (F(1655),  'then we add',                   'chest'),
    (F(1658),  'the *next*',                    'chest'),
    (F(1660),  "Don't turn on",                 'chest'),
    (F(1663),  'your *ads*',                    'chest'),
    (F(1665),  '*hire* two,',                   'chest'),
    (F(1667),  'three people',                  'right'),
    (F(1669),  'all in the',                    'chest'),
    (F(1672),  '*same week*',                   'chest'),
    (F(1674),  'Because if',                    'chest'),
    (F(1676),  'something *breaks*',            'chest'),
    (F(1678),  "then you're not",               'chest'),
    (F(1681),  'going to know',                 'left'),
    (F(1684),  'what has',                      'chest'),
])
s.behind_text(F(1642), F(1647), 'One', 'thing', si=1)
s.behind_text(F(1686), None, None, 'broke', si=1)
s.sound(F(1642), 'transitions/whoosh.mp3', -15)
s.sound(F(1686), 'transitions/whoosh.mp3', -15)

# ---- rule card 1: the loop ----
steps = [('Add', F(1647)), ('Wait', F(1650)), ('Check', F(1651)), ('Next', F(1655))]
s.front.append('<div id="loop" class="card"><div class="row"><div class="lab">One change at a time</div><div id="rep" class="chip">&#8635; repeat</div></div><div class="steps">' +
               ''.join(f'<div id="st{i}" class="st"><div class="num">0{i + 1}</div><div class="nm">{n}</div></div>' for i, (n, _) in enumerate(steps)) + '</div></div>')
c0 = F(1647) - 8
card_in('#loop', c0, 0.32); s.sound(c0, 'ui/pop.mp3', -13)
for i, (n, f) in enumerate(steps):
    s.js += [f'tl.to("#st{i}", {{ backgroundColor: "{BLUE}", borderColor: "{BLUE}", color: "#ffffff", duration: 0.12, ease: "power2.out" }}, {tm(f)});',
             f'tl.fromTo("#st{i}", {{ scale: 0.92 }}, {{ scale: 1, duration: 0.26, ease: "back.out(2.4)", immediateRender: false }}, {tm(f)});']
    if i + 1 < len(steps):
        s.js.append(f'tl.to("#st{i}", {{ backgroundColor: "rgba(242,239,233,0.10)", borderColor: "rgba(242,239,233,0.30)", color: "{BONE}", duration: 0.16, ease: "power2.out" }}, {tm(steps[i + 1][1])});')
    s.sound(f, 'ui/click.wav', -11)
s.js.append(f'tl.fromTo("#rep", {{ opacity: 0, x: 14 }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "power3.out", immediateRender: false }}, {tm(F(1659))});')
card_out('#loop', F(1660))

# ---- rule card 2: everything in the same week ----
days = 'MTWTFSS'
drops = [('Ads', 0, F(1664)), ('Hire', 1, F(1666)), ('Hire', 2, F(1667)), ('Hire', 3, F(1668))]
cells = ''.join(f'<div class="day"><div class="dl">{d}</div>' + ''.join(f'<div id="dp{k}" class="dp">{n}<span id="q{k}" class="q">?</span></div>' for k, (n, c, _) in enumerate(drops) if c == i) + '</div>' for i, d in enumerate(days))
s.front.append('<div id="week" class="card"><div class="row"><div class="labs"><div id="wl" class="lab">Week 1</div><div id="wb" class="pill">Something broke</div></div>'
               '<div class="sw"><span>Ads</span><div id="swt" class="swt"><div id="swk" class="swk"></div></div></div></div>'
               f'<div id="days" class="days">{cells}<div id="wk" class="wk"></div></div></div>')
w0 = F(1660)
s.js += [f'tl.set("#week", {{ opacity: 1 }}, {tm(w0)});',
         f'tl.fromTo("#week", {{ y: 40, scale: 0.97 }}, {{ y: 0, scale: 1, duration: 0.26, ease: "power3.out", immediateRender: false }}, {tm(w0)});',
         f'tl.to("#swk", {{ x: 44, duration: 0.16, ease: "power2.inOut" }}, {tm(F(1662))});',
         f'tl.to("#swt", {{ backgroundColor: "{BLUE}", duration: 0.16, ease: "power2.inOut" }}, {tm(F(1662))});']
s.sound(F(1662), 'ui/click.wav', -10)
for k, (n, c, f) in enumerate(drops):
    s.js += [f'tl.set("#dp{k}", {{ opacity: 1 }}, {tm(f)});',
             f'tl.fromTo("#dp{k}", {{ y: -46, scale: 0.8 }}, {{ y: 0, scale: 1, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, {tm(f)});']
    s.sound(f, 'ui/pop.mp3', -14)
fsw = F(1672)                                        # "same week": the whole week lights up
s.js += [f'tl.fromTo("#wk", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.24, ease: "power3.out", immediateRender: false }}, {tm(fsw)});',
         f'tl.to("#wl", {{ color: "{BLUE}", duration: 0.2 }}, {tm(fsw)});']
fb = F(1677)                                         # "breaks"
s.js += [f'tl.to("#wl", {{ opacity: 0, duration: 0.08 }}, {tm(fb)});',
         f'tl.fromTo("#wb", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.2)", immediateRender: false }}, {tm(fb)});',
         f'tl.to("#wk", {{ borderColor: "rgba(242,239,233,0.85)", duration: 0.12 }}, {tm(fb)});'] + \
        [f'tl.to("#week", {{ x: {dx}, duration: 0.05, ease: "power1.inOut" }}, {tm(fb) + 0.05 * j:.4f});' for j, dx in enumerate([-11, 10, -7, 5, -2, 0])]
s.sound(fb, 'impact/bass-drop.mp3', -16)
for k in range(len(drops)):                           # "then you're not going to know": a question mark on every change
    f = F(1678) + 4 * k
    s.js += [f'tl.fromTo("#q{k}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, {tm(f)});',
             f'tl.to("#dp{k}", {{ backgroundColor: "rgba(242,239,233,0.14)", color: "{BONE}", duration: 0.15 }}, {tm(f)});']

s.css.append('''    .chip { font-weight: 700; font-size: 24px; color: #2F6FED; opacity: 0; }
    /* the loop */
    .steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin-top: 30px; }
    .st { height: 164px; border-radius: 24px; background: rgba(242,239,233,0.05); border: 2px solid rgba(242,239,233,0.12); color: rgba(242,239,233,0.5);
          display: flex; flex-direction: column; justify-content: center; padding-left: 24px; }
    .st .num { font-weight: 700; font-size: 24px; letter-spacing: 0.08em; opacity: 0.75; }
    .st .nm { font-weight: 800; font-size: 46px; letter-spacing: -0.03em; margin-top: 4px; }
    /* the week */
    .labs { position: relative; height: 44px; flex: 1; }
    .labs .lab { position: absolute; left: 0; top: 7px; }
    .pill { position: absolute; left: 0; top: 0; background: #F2EFE9; color: #0A0A0A; font-weight: 800; font-size: 26px; letter-spacing: -0.01em; padding: 5px 18px 6px; border-radius: 22px; opacity: 0; transform-origin: 0 50%; }
    .sw { display: flex; align-items: center; gap: 16px; font-weight: 700; font-size: 30px; letter-spacing: -0.02em; }
    .swt { width: 92px; height: 48px; border-radius: 24px; background: rgba(242,239,233,0.2); position: relative; }
    .swk { position: absolute; left: 4px; top: 4px; width: 40px; height: 40px; border-radius: 20px; background: #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.4); }
    .days { position: relative; display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin-top: 30px; }
    .day { height: 164px; border-radius: 20px; background: rgba(242,239,233,0.05); border: 2px solid rgba(242,239,233,0.10); display: flex; flex-direction: column; align-items: center; padding-top: 14px; }
    .dl { font-weight: 700; font-size: 24px; color: rgba(242,239,233,0.5); }
    .dp { position: relative; margin-top: 22px; width: 96px; height: 58px; border-radius: 16px; background: #2F6FED; color: #fff; font-weight: 800; font-size: 28px; letter-spacing: -0.02em;
          display: flex; align-items: center; justify-content: center; opacity: 0; }
    .q { position: absolute; right: -12px; top: -16px; width: 38px; height: 38px; border-radius: 19px; background: #F2EFE9; color: #0A0A0A; font-weight: 900; font-size: 26px; display: flex; align-items: center; justify-content: center; opacity: 0; }
    .wk { position: absolute; left: -9px; right: -9px; top: -9px; bottom: -9px; border-radius: 28px; border: 3px solid #2F6FED; opacity: 0; }''')
s.write()
