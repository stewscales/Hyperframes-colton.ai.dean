"""08 — One thing at a time, opened with the hook from 01 (stacked layout).
Edits, in order:
  HOOK   pinned title  ->  "90 | DAYS" behind his head + day counter card running to 90 ("Quit")  ->  "Why they quit" card:
         "They can't trade" struck out, "They build in the wrong order" lit  ->  "WRONG | ORDER" behind his head
  RULE   new pinned title  ->  "ONE | THING" behind his head  ->  ONE calendar that tells the whole rule:
           clean 3-week calendar  ->  "Add one thing": one change lands in week 1  ->  "wait": the week ticks off day by day
           ->  "check if it worked": the week locks into a solid bar, "Stable"  ->  "then we add the next": week 2 opens
           ->  "Don't ... all in the same week": the calendar clears and three changes pile into one week
           ->  "breaks": it fails, a question mark on every change  ->  the three changes spread out, one per week, and
           each week locks in turn: the last frame is three stable weeks under "One thing at a time".
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
    (F(1684),  'what has *broke*',              'chest'),
])
s.behind_text(F(1642), F(1647), 'One', 'thing', si=1)
s.sound(F(1642), 'transitions/whoosh.mp3', -15)


# ---- the calendar: one graphic for the whole rule ----
ROWS, DAYS = 3, 'MTWTFSS'
def cal_rows():
    out = []
    for r in range(ROWS):
        cells = ''.join(f'<div id="c{r}{c}" class="cc cr{r}"><span id="t{r}{c}" class="tk">{TICK}</span></div>' for c in range(7))
        out.append(f'<div id="row{r}" class="crow"><div class="slot">Week {r + 1}</div><div class="cells"><div id="bar{r}" class="cbar"></div>{cells}</div>'
                   f'<div id="ok{r}" class="okb"><span class="okr">{TICK}</span>Stable</div></div>')
    return ''.join(out)
s.front.append('<div id="cal" class="card cal"><div class="chead"><div id="lblA" class="clbl"><i class="dot a"></i>One thing at a time</div>'
               '<div id="lblB" class="clbl"><i class="dot b"></i>All in the same week</div></div>'
               '<div class="dlet"><span></span><div>' + ''.join(f'<b>{d}</b>' for d in DAYS) + '</div><span></span></div>'
               f'<div class="rows">{cal_rows()}'
               # changes (chips). a* = the right way, x* = the pile-up. All sit in week 1's slot; x1/x2 start out over week 1's days.
               '<div id="a0" class="chg">Ads</div><div id="a1" class="chg" style="top:72px">Hire</div>'
               '<div id="x0" class="chg">Ads<i id="xq0" class="q">?</i></div><div id="x1" class="chg" style="left:192px">Hire<i id="xq1" class="q">?</i></div>'
               '<div id="x2" class="chg" style="left:384px">Hire<i id="xq2" class="q">?</i></div>'
               f'<div id="brk" class="brk"><span class="brr">{CROSS}</span></div></div></div>')
J = s.js.append
def at(f, d=0): return round(tm(f) + d / 30, 4)
def land(sel, f): J(f'tl.set("{sel}", {{ opacity: 1 }}, {at(f)});'); J(f'tl.fromTo("{sel}", {{ y: -34, scale: 0.8 }}, {{ y: 0, scale: 1, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, {at(f)});')
def ticks(r, f, step, upto=7):
    for c in range(upto):
        J(f'tl.fromTo("#t{r}{c}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.6)", immediateRender: false }}, {at(f, c * step)});')
        J(f'tl.to("#c{r}{c}", {{ backgroundColor: "rgba(47,111,237,0.30)", borderColor: "rgba(47,111,237,0.75)", duration: 0.14 }}, {at(f, c * step)});')
def lock(r, f):                                        # the seven days join into one solid bar, then "Stable"
    J(f'tl.set("#bar{r}", {{ opacity: 1 }}, {at(f)});')
    J(f'tl.fromTo("#bar{r}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.24, ease: "power3.inOut", immediateRender: false }}, {at(f)});')
    J(f'tl.to(".cr{r}", {{ backgroundColor: "rgba(47,111,237,0)", borderColor: "rgba(47,111,237,0)", duration: 0.14 }}, {at(f, 4)});')
    J(f'tl.fromTo("#ok{r}", {{ opacity: 0, x: -14 }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, {at(f, 5)});')
def clear(r, f):
    J(f'tl.to("#row{r} .tk, #bar{r}, #ok{r}", {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, {at(f)});')
    J(f'tl.to(".cr{r}", {{ backgroundColor: "rgba(242,239,233,0.06)", borderColor: "rgba(242,239,233,0.14)", duration: 0.14 }}, {at(f)});')
def dim(r, f, v): J(f'tl.to("#row{r}", {{ opacity: {v}, duration: 0.2, ease: "power2.out" }}, {at(f)});')

c0 = F(1647) - 8                                       # 1. a clean, simple calendar
card_in('#cal', c0, 0.32); s.sound(c0, 'ui/pop.mp3', -13)
land('#a0', F(1647)); s.sound(F(1647), 'ui/click.wav', -11)            # "Add one thing"
ticks(0, F(1650), 2); s.sound(F(1650), 'ui/click.wav', -13)            # 2. "wait": the week completes, day by day
lock(0, F(1651) + 2); s.sound(F(1651) + 2, 'ui/click.wav', -11)        # 3. "check if it worked": stable
dim(1, F(1655), 1); land('#a1', F(1655) + 2); s.sound(F(1655) + 2, 'ui/pop.mp3', -14)   # 4. "then we add the next": week 2 opens only now
ticks(1, F(1658), 3, upto=4)

R0 = F(1660) - 5                                       # "Don't...": wipe, and show the opposite
clear(0, R0); clear(1, R0); J(f'tl.to("#a0, #a1", {{ opacity: 0, y: -16, duration: 0.14, ease: "power2.in" }}, {at(R0)});'); dim(1, R0, 0.4)
J(f'tl.to("#lblA", {{ opacity: 0, y: -10, duration: 0.14, ease: "power2.in" }}, {at(R0)});')
J(f'tl.fromTo("#lblB", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out", immediateRender: false }}, {at(F(1660))});')
for k, f in enumerate([F(1664), F(1665), F(1667)]):    # "your ads" / "hire two," / "three people": all into week 1
    land(f'#x{k}', f); s.sound(f, 'ui/pop.mp3', -14)
J(f'tl.to("#row0", {{ backgroundColor: "rgba(242,239,233,0.07)", boxShadow: "0 0 0 3px rgba(242,239,233,0.55)", duration: 0.22, ease: "power2.out" }}, {at(F(1672))});')   # "same week"
fb = F(1677)                                           # "breaks"
J(f'tl.fromTo("#brk", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.6)", immediateRender: false }}, {at(fb)});')
for j, dx in enumerate([-12, 10, -7, 5, -2, 0]): J(f'tl.to("#cal", {{ x: {dx}, duration: 0.05, ease: "power1.inOut" }}, {at(fb, 1.5 * j)});')
s.sound(fb, 'impact/bass-drop.mp3', -16)
for k in range(3):                                     # "then you're not going to know": which one was it?
    J(f'tl.fromTo("#xq{k}", {{ opacity: 0, scale: 0.3 }}, {{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(3)", immediateRender: false }}, {at(F(1678), 2 * k)});')
    J(f'tl.to("#x{k}", {{ backgroundColor: "#3A3B40", duration: 0.12 }}, {at(F(1678), 2 * k)});')

V0 = F(1678) + 8                                       # 5. the fix, and the last frame: one change per week, each week stable
J(f'tl.to("#xq0, #xq1, #xq2, #brk", {{ opacity: 0, scale: 0.6, duration: 0.12, ease: "power2.in" }}, {at(V0)});')
J(f'tl.to("#row0", {{ backgroundColor: "rgba(242,239,233,0)", boxShadow: "0 0 0 3px rgba(242,239,233,0)", duration: 0.16 }}, {at(V0)});')
J(f'tl.to("#lblB", {{ opacity: 0, y: -10, duration: 0.12, ease: "power2.in" }}, {at(V0)});')
J(f'tl.fromTo("#lblA", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out", immediateRender: false }}, {at(V0, 3)});')
J(f'tl.to("#x0, #x1, #x2", {{ backgroundColor: "{BLUE}", duration: 0.16 }}, {at(V0)});')
J(f'tl.to("#x1", {{ x: -192, y: 72, duration: 0.3, ease: "power3.inOut" }}, {at(V0, 1)});')
J(f'tl.to("#x2", {{ x: -384, y: 144, duration: 0.32, ease: "power3.inOut" }}, {at(V0, 2)});')
dim(1, V0 + 3, 1); dim(2, V0 + 5, 1)
for r in range(ROWS):
    f = V0 + 6 + 3 * r + (1 if r else 0)
    ticks(r, f, 1); lock(r, f + 6); s.sound(f + 6, 'ui/click.wav', -12 - r)
J(f'tl.to("#cal", {{ borderColor: "rgba(47,111,237,0.8)", boxShadow: "0 26px 70px rgba(0,0,0,0.55), 0 0 64px rgba(47,111,237,0.38)", duration: 0.3, ease: "power2.out" }}, {at(V0, 22)});')
J(f'tl.fromTo("#cal", {{ scale: 1 }}, {{ scale: 1.018, duration: 0.14, ease: "power2.out", yoyo: true, repeat: 1, immediateRender: false }}, {at(V0, 22)});')
assert V0 + 6 + 3 * 2 + 1 + 6 + 5 + 6 <= s.NF - 9, 'the last frame must be finished and held'

s.css.append('''    /* the calendar */
    .card.cal { top: 1244px; height: 352px; padding: 26px 28px; }
    .chead { position: relative; height: 48px; }
    .clbl { position: absolute; left: 0; top: 0; display: flex; align-items: center; gap: 14px; font-weight: 800; font-size: 36px; letter-spacing: -0.03em; color: #fff; white-space: nowrap; }
    #lblB { opacity: 0; }
    .dot { width: 16px; height: 16px; border-radius: 8px; display: inline-block; }  .dot.a { background: #2F6FED; }  .dot.b { background: #F2EFE9; }
    .dlet { display: grid; grid-template-columns: 170px 440px 190px; column-gap: 22px; margin-top: 10px; height: 30px; }
    .dlet div { display: grid; grid-template-columns: repeat(7, 56px); column-gap: 8px; }
    .dlet b { text-align: center; font-weight: 700; font-size: 26px; line-height: 30px; color: rgba(242,239,233,0.55); }
    .rows { position: relative; margin-top: 8px; }
    .crow { display: grid; grid-template-columns: 170px 440px 190px; column-gap: 22px; height: 60px; margin-bottom: 12px; align-items: center; border-radius: 16px; }
    #row1, #row2 { opacity: 0.4; }
    .slot { height: 56px; border-radius: 16px; border: 2px dashed rgba(242,239,233,0.22); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 28px; letter-spacing: -0.02em; color: rgba(242,239,233,0.55); }
    .cells { position: relative; display: grid; grid-template-columns: repeat(7, 56px); column-gap: 8px; height: 56px; }
    .cc { position: relative; z-index: 1; border-radius: 14px; background: rgba(242,239,233,0.06); border: 2px solid rgba(242,239,233,0.14); display: flex; align-items: center; justify-content: center; }
    .tk { opacity: 0; color: #fff; display: flex; }  .tk svg { width: 30px; height: 30px; }
    .cbar { position: absolute; left: 0; top: 0; width: 440px; height: 56px; border-radius: 16px; background: #2F6FED; transform-origin: 0 50%; opacity: 0; }
    .okb { display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 32px; letter-spacing: -0.03em; color: #fff; opacity: 0; }
    .okr { width: 40px; height: 40px; border-radius: 20px; background: #2F6FED; color: #fff; display: flex; align-items: center; justify-content: center; flex: none; }  .okr svg { width: 24px; height: 24px; }
    .chg { position: absolute; left: 0; top: 2px; width: 170px; height: 56px; border-radius: 16px; background: #2F6FED; color: #fff; font-weight: 800; font-size: 32px; letter-spacing: -0.02em;
           display: flex; align-items: center; justify-content: center; opacity: 0; z-index: 3; box-shadow: 0 6px 18px rgba(0,0,0,0.35); }
    .q { position: absolute; right: -12px; top: -14px; width: 38px; height: 38px; border-radius: 19px; background: #F2EFE9; color: #0A0A0A; font-style: normal; font-weight: 900; font-size: 26px; display: flex; align-items: center; justify-content: center; opacity: 0; }
    .brk { position: absolute; left: 654px; top: 2px; height: 56px; display: flex; align-items: center; opacity: 0; }
    .brr { width: 40px; height: 40px; border-radius: 20px; background: #F2EFE9; color: #0A0A0A; display: flex; align-items: center; justify-content: center; }  .brr svg { width: 24px; height: 24px; }''')
s.write()
