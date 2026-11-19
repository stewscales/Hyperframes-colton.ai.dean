"""The shared opening hook (words 0-25 of the long video): "Most traders who try coaching will quit in the first 90 days,
it's not because they can't trade, they just build everything in the wrong order."
exec() after kit.py and after creating the Scene `s`; then call add_hook(cut) where cut = output frame the hook ends on.
Edits: opening pinned title and day counter card both on screen from the first frame, the count running to 90 ("Quit") ->
"90 | DAYS" behind his head -> "Why they quit" card:
"They can't trade" struck out, "They build in the wrong order" lit -> "WRONG | ORDER" behind his head."""
F = s.F
def card_in(sel, f, dur=0.3):
    s.js.extend([f'tl.set("{sel}", {{ opacity: 1 }}, {tm(f)});',
                 f'tl.fromTo("{sel}", {{ y: 44, scale: 0.96 }}, {{ y: 0, scale: 1, duration: {dur}, ease: "back.out(1.4)", immediateRender: false }}, {tm(f)});'])
def card_out(sel, f): s.js.append(f'tl.to("{sel}", {{ opacity: 0, y: 24, duration: 0.12, ease: "power2.in" }}, {tm(f - 5)});')
CROSS = '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" fill="none"/></svg>'
TICK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.6 4.6L19 7.6" stroke="currentColor" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'

HOOK_CAPTIONS = lambda cut: [                          # short, one line, key words in blue (blue only over his dark tee, never over the wall)
    (0,        'Most traders',                  'chest'),
    (F(2),     'who try coaching',              'chest'),
    (F(5),     'will *quit*',                   'chest'),
    (F(7),     'in the first',                  'chest', F(10)),          # then "90 | DAYS" behind his head, on its own
    (F(12),    "it's not because",              'chest'),
    (F(15),    "they *can't trade*",            'chest'),
    (F(18),    'they just build',               'chest'),
    (F(21),    'everything in the',             'chest', F(24)),          # then "WRONG | ORDER" behind his head, on its own
]
def add_hook(cut, si=0):
    s.pinned_title('Why most trading coaches', 'quit in 90 days', 0, cut)
    s.behind_text(F(10), F(12), '90', 'days', si=si)
    s.behind_text(F(24), cut, 'wrong', 'order', si=si)
    s.sound(F(10), 'transitions/whoosh.mp3', -15)
    s.sound(F(24), 'impact/bass-drop.mp3', -16)
    # ---- hook card 1: the first 90 days ----
    d0, d1 = 0, F(11) + 4                                  # on screen from the very first frame; the count lands on 90 as he says "90 days"
    s.front.append('<div id="dayc" class="card" style="opacity:1"><div class="row"><div class="lab">Trader to coach</div><div id="quitp" class="pill2">Quit</div></div>'
                   '<div class="dayrow"><span class="dlab">Day</span><span id="dn" class="dnum">1</span><span class="dof">/ 90</span></div>'
                   '<div class="bar"><div id="barf" class="barf"></div></div></div>')
    s.js += [f'tl.to("#dn", {{ textContent: 90, snap: {{ textContent: 1 }}, duration: {(d1 - d0) / 30:.4f}, ease: "power1.in" }}, {tm(d0)});',
             f'tl.fromTo("#barf", {{ scaleX: 0.011 }}, {{ scaleX: 1, duration: {(d1 - d0) / 30:.4f}, ease: "power1.in", immediateRender: false }}, {tm(d0)});',
             f'tl.fromTo("#quitp", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.4)", immediateRender: false }}, {tm(d1)});',
             f'tl.to("#barf", {{ backgroundColor: "{BONE}", duration: 0.15 }}, {tm(d1)});']
    s.sound(d1, 'ui/click.wav', -11)
    card_out('#dayc', F(12))

    # ---- hook card 2: why they quit ----
    s.front.append('<div id="why" class="card"><div class="lab">Why they quit</div>'
                   f'<div id="wr0" class="wrow"><span id="wi0" class="wic">{CROSS}</span><span class="wt">They can&rsquo;t trade<span id="wst" class="strike"></span></span></div>'
                   f'<div id="wr1" class="wrow"><span id="wi1" class="wic">{TICK}</span><span class="wt">They build in the wrong order</span></div></div>')
    card_in('#why', F(12), 0.24)
    fs = F(17)                                             # "trade": not the reason
    s.js += [f'tl.fromTo("#wst", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.2, ease: "power2.out", immediateRender: false }}, {tm(fs)});',
             f'tl.fromTo("#wi0", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.6)", immediateRender: false }}, {tm(fs)});',
             f'tl.to("#wr0 .wt", {{ color: "rgba(242,239,233,0.42)", duration: 0.2 }}, {tm(fs)});',
             f'tl.fromTo("#wr1", {{ opacity: 0, x: -18 }}, {{ opacity: 0.5, x: 0, duration: 0.22, ease: "power3.out", immediateRender: false }}, {tm(F(18))});']
    s.sound(fs, 'ui/click.wav', -11)
    fw = F(24)                                             # "wrong order": the reason
    s.js += [f'tl.to("#wr1", {{ opacity: 1, backgroundColor: "rgba(47,111,237,0.20)", borderColor: "{BLUE}", duration: 0.16, ease: "power2.out" }}, {tm(fw)});',
             f'tl.fromTo("#wr1", {{ scale: 0.97 }}, {{ scale: 1, duration: 0.26, ease: "back.out(2.4)", immediateRender: false }}, {tm(fw)});',
             f'tl.fromTo("#wi1", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2.6)", immediateRender: false }}, {tm(fw)});']
    card_out('#why', cut)

    s.css.append(HOOK_CSS)
HOOK_CSS = '''    .card .row { display: flex; justify-content: space-between; align-items: center; height: 44px; }
    /* day counter */
    .pill2 { background: #F2EFE9; color: #0A0A0A; font-weight: 800; font-size: 36px; letter-spacing: -0.02em; padding: 4px 24px 6px; border-radius: 26px; opacity: 0; }
    .dayrow { display: flex; align-items: baseline; gap: 18px; margin-top: 10px; height: 150px; }
    .dlab { font-weight: 700; font-size: 44px; letter-spacing: -0.02em; color: rgba(242,239,233,0.6); }
    .dnum { font-weight: 800; font-size: 136px; line-height: 1; letter-spacing: -0.04em; color: #fff; font-variant-numeric: tabular-nums; min-width: 190px; }
    .dof { font-weight: 700; font-size: 44px; letter-spacing: -0.02em; color: rgba(242,239,233,0.4); }
    .bar { margin-top: 22px; height: 14px; border-radius: 7px; background: rgba(242,239,233,0.12); overflow: hidden; }
    .barf { width: 100%; height: 100%; border-radius: 7px; background: #2F6FED; transform-origin: 0 50%; transform: scaleX(0.011); }
    /* why they quit */
    .wrow { display: flex; align-items: center; gap: 20px; height: 96px; margin-top: 18px; padding: 0 22px; border-radius: 22px; background: rgba(242,239,233,0.05); border: 2px solid rgba(242,239,233,0.10);
            font-weight: 800; font-size: 40px; letter-spacing: -0.03em; color: #fff; }
    #wr0 { margin-top: 24px; }  #wr1 { opacity: 0; }
    .wic { width: 44px; height: 44px; border-radius: 22px; display: flex; align-items: center; justify-content: center; opacity: 0; flex: none; }
    .wic svg { width: 26px; height: 26px; }
    #wi0 { background: rgba(242,239,233,0.16); color: #F2EFE9; }  #wi1 { background: #2F6FED; color: #fff; }
    .wt { position: relative; white-space: nowrap; }
    .strike { position: absolute; left: -6px; right: -6px; top: 54%; height: 4px; border-radius: 2px; background: #F2EFE9; transform-origin: 0 50%; transform: scaleX(0); }'''
