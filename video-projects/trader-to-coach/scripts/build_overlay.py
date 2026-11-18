"""Build the graphics layer for the Trader to Coach YouTube edit.

Writes:
  index.html        Hyperframes composition (1920x1080 CSS px): proxy video + every graphic on one GSAP timeline
  assets/edit.json  punch-in schedule, sound-effect cues and frame count for render.py / mix_audio.py

Every time comes from the forced-aligned transcript (assets/words.json): T("phrase") is the moment the first
word of that phrase starts. Nothing is placed by eye against the plan's timecodes, because most of the plan's
trigger lines are not in the footage.

Run from the project folder: python3 -I scripts/build_overlay.py
"""
import json, re, math

FPS = 30
NF = 15871                      # source frames (529.03 s)
START = 12                       # the video starts here: the source opens with 0.4 s of him looking down
MIRO_IN, MIRO_OUT = 6895, 11060  # first / one-past-last frame of the Miro screen recording
BLUE, BONE, BLACK, GREY = '#2F6FED', '#F2EFE9', '#0A0A0A', '#E8E5DF'

# ---------------------------------------------------------------- transcript lookup
WORDS = json.load(open('assets/words.json'))
_n = lambda s: re.sub(r"[^a-z0-9' ]", '', s.lower().replace('’', "'")).strip()
_W = [_n(w['text']) for w in WORDS]
MISSING = []; SHORT = []
def _find(phrase, k=0):
    p = _n(phrase).split(); hits = [i for i in range(len(_W) - len(p) + 1) if _W[i:i + len(p)] == p]
    if len(hits) <= k:
        MISSING.append((phrase, k)); return 0, 0
    return hits[k], hits[k] + len(p) - 1
def T(phrase, k=0):
    """Start time (s) of the first word of the k-th occurrence of phrase."""
    return WORDS[_find(phrase, k)[0]]['start']
def TL(phrase, k=0):
    """Start time (s) of the LAST word of phrase."""
    return WORDS[_find(phrase, k)[1]]['start']
def E(phrase, k=0):
    """End time (s) of the last word of phrase."""
    return WORDS[_find(phrase, k)[1]]['end']
F = lambda t: int(round(t * FPS))            # seconds -> frame
P = lambda f: round(f / FPS, 5)              # frame -> GSAP time
LEAD = 2                                     # graphics land this many frames before their word

html, js, sfx, zooms = [], [], [], []
js.append('tl.set("#bar", { y: 132 }, 0);'); js.append('tl.set("#cta", { y: 306 }, 0);')    # both start off-screen below the frame
def hl(s):   # *word* -> blue
    return re.sub(r'\*(.+?)\*', r'<b>\1</b>', s)

ICON = {
 'ok':  f'<svg class="ic" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="{BLUE}"/><path d="M9 16.5l5 5 9-10" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 'x':   f'<svg class="ic" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="none" stroke="{GREY}" stroke-opacity=".55" stroke-width="2.5"/><path d="M11 11l10 10M21 11l-10 10" fill="none" stroke="{GREY}" stroke-opacity=".8" stroke-width="3.2" stroke-linecap="round"/></svg>',
 'q':   f'<svg class="ic" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="none" stroke="{BLUE}" stroke-width="2.5"/><text x="16" y="22.5" text-anchor="middle" font-family="Inter" font-weight="800" font-size="19" fill="{BLUE}">?</text></svg>',
 'dot': f'<svg class="ic" viewBox="0 0 32 32"><circle cx="16" cy="16" r="6" fill="{BLUE}"/></svg>',
 'arr': f'<svg class="ic" viewBox="0 0 32 32"><path d="M6 16h18M17 9l7 7-7 7" fill="none" stroke="{BLUE}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}
def show(sel, f, dur=6, y=22, ease='power3.out'):
    js.append(f'tl.fromTo("{sel}", {{ opacity: 0, y: {y} }}, {{ opacity: 1, y: 0, duration: {P(dur)}, ease: "{ease}" }}, {P(f)});')
def hide(sel, f, dur=4):
    js.append(f'tl.to("{sel}", {{ opacity: 0, duration: {P(dur)}, ease: "power1.in" }}, {P(f)});')

# ---------------------------------------------------------------- components
_cards = []
def _claim(cid, f0, f1):
    """One graphic at a time in the lower third: start after the previous one has faded (5 frames)."""
    if _cards:
        assert f0 > _cards[-1][0], f'{cid} is out of order'
        f0 = max(f0, _cards[-1][1] + 5)
    if f1 - f0 < 26: SHORT.append((cid, f0, f1))
    _cards.append((f0, f1, cid)); return f0, f1
def card(cid, t_in, t_out, label=None, head=None, rows=(), chips=(), width=None, extra_html=''):
    """Lower-left card. rows: (time|None, html, icon|'01'); chips: (time|None, text, 'on'|'x'|'ok'). time None = with the card."""
    f0, f1 = _claim(cid, F(t_in) - LEAD, F(t_out))
    h = [f'<div class="card" id="{cid}"' + (f' style="width:{width}px"' if width else '') + '>']
    if label: h.append(f'  <div class="lab">{label}</div>')
    if head: h.append(f'  <div class="hd">{hl(head)}</div>')
    h.append(extra_html)
    if chips:
        h.append(f'  <div class="chipw" id="{cid}-cw"><div class="chips">')
        for i, (t, txt, st) in enumerate(chips):
            h.append(f'    <div class="chip {st}" id="{cid}-c{i}">{txt}</div>')
        h.append('  </div></div>')
    if rows:
        h.append('  <div class="rows">')
        for i, (t, txt, ic) in enumerate(rows):
            icon = ICON.get(ic, f'<span class="num">{ic}</span>' if ic else '')
            h.append(f'    <div class="rw{" on" if t is None else ""}" id="{cid}-r{i}"><div class="row">{icon}<span>{hl(txt)}</span></div></div>')
        h.append('  </div>')
    h.append('</div>'); html.append('\n'.join(x for x in h if x))
    show(f'#{cid}', f0)
    for i, (t, _, _) in enumerate(rows):
        if t is not None:   # the card grows upward by one line as the row fades in
            js.append(f'tl.fromTo("#{cid}-r{i}", {{ height: 0, opacity: 0 }}, {{ height: "auto", opacity: 1, duration: {P(6)}, ease: "power2.out" }}, {P(max(F(t) - LEAD, f0))});')
    if chips and chips[0][0] is not None and F(chips[0][0]) - LEAD > f0 + 2:      # no empty chip row before the first chip is said
        js.append(f'tl.fromTo("#{cid}-cw", {{ height: 0 }}, {{ height: "auto", duration: {P(6)}, ease: "power2.out" }}, {P(F(chips[0][0]) - LEAD - 2)});')
    for i, (t, _, _) in enumerate(chips):
        if t is None: js.append(f'tl.set("#{cid}-c{i}", {{ opacity: 1 }}, {P(f0)});')
        else: js.append(f'tl.fromTo("#{cid}-c{i}", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: {P(6)}, ease: "back.out(2)" }}, {P(F(t) - LEAD)});')
    hide(f'#{cid}', f1)
    return f0, f1

def impact(iid, t_in, t_out, text, sub=None, hit=True):
    f0, f1 = _claim(iid, F(t_in) - LEAD, F(t_out))
    words = text.split(); fs = 104 if len(text) <= 16 else 86 if len(text) <= 20 else 72
    html.append(f'<div class="impact" id="{iid}"><div class="box" style="font-size:{fs}px">' + ' '.join(f'<span id="{iid}-w{i}">{w}</span>' for i, w in enumerate(words)) + '</div>'
                + (f'<div class="isub" id="{iid}-s">{hl(sub[1])}</div>' if sub else '') + '</div>')
    js.append(f'tl.fromTo("#{iid}", {{ opacity: 0, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: {P(4)}, ease: "power2.out" }}, {P(f0)});')
    for i in range(len(words)):
        js.append(f'tl.fromTo("#{iid}-w{i}", {{ opacity: 0, scale: 0.2 }}, {{ opacity: 1, scale: 1, duration: {P(8)}, ease: "back.out(2.2)" }}, {P(f0 + 2 * i)});')
    if sub: show(f'#{iid}-s', F(sub[0]) - LEAD, 5, 10)
    js.append(f'tl.to("#{iid}", {{ opacity: 0, scale: 1.12, duration: {P(5)}, ease: "power2.in" }}, {P(f1)});')
    if hit: sfx.append(('bass-drop.mp3', P(f0), -19))

def zoom(t_in, t_out, z, ramp_in=8, ramp_out=10):
    z = {1.10: 1.12, 1.08: 1.09, 1.07: 1.08}[z]
    zooms.append((F(t_in) - 1, F(t_out), z, ramp_in, ramp_out, 0.50 if t_in < 300 else 0.46, 0.33))

# bottom bar (roadmap + phase label; doubles as the cover for Miro's prompt box)
_slot = [0]
def bar_up(f):   js.append(f'tl.to("#bar", {{ y: 0, duration: {P(9)}, ease: "power3.out" }}, {P(f)});'); js.append(f'tl.to("#thin", {{ opacity: 0, duration: {P(4)} }}, {P(f)});')
def bar_down(f): js.append(f'tl.to("#bar", {{ y: 132, duration: {P(8)}, ease: "power2.in" }}, {P(f)});'); js.append(f'tl.to("#thin", {{ opacity: 1, duration: {P(6)} }}, {P(f + 5)});')
def slot(side, t_in, t_out, label, head, pop=False, frames=False):
    _slot[0] += 1; sid = f'sl{_slot[0]}'
    f0 = t_in if frames else F(t_in) - LEAD; f1 = t_out if frames else F(t_out) - 6
    SLOTS.append((side, f0, f1, head))
    html_bar[side].append(f'<div class="sl" id="{sid}"><div class="slab">{label}</div><div class="shd">{hl(head)}</div></div>')
    if pop: js.append(f'tl.fromTo("#{sid}", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: {P(8)}, ease: "back.out(2.4)" }}, {P(f0)});')
    else: js.append(f'tl.fromTo("#{sid}", {{ opacity: 0, x: {-36 if side == "l" else 36} }}, {{ opacity: 1, x: 0, duration: {P(8)}, ease: "power3.out" }}, {P(f0)});')
    hide(f'#{sid}', f1, 4)
def lit(n, f, on=True):
    for sel in (f'#thin .seg{n} i', f'#bar .seg{n} i'):
        js.append(f'tl.to("{sel}", {{ opacity: {1 if on else 0}, duration: {P(9)}, ease: "power2.out" }}, {P(f)});')
    js.append(f'tl.to("#bar .seg{n} .sn, #bar .seg{n} .sd", {{ opacity: {1 if on else 0.42}, duration: {P(9)} }}, {P(f)});')
def pulse(n, f):
    js.append(f'tl.fromTo("#bar .seg{n}", {{ scale: 1 }}, {{ scale: 1.1, duration: {P(5)}, ease: "power2.out", yoyo: true, repeat: 1 }}, {P(f)});')
html_bar = {'l': [], 'r': []}; SLOTS = []

def bucket(bid, t_in, t_out, label, rows, script):
    svg = f'''  <svg class="bk" viewBox="0 0 440 330" width="440" height="330">
    <defs><clipPath id="{bid}-clip"><path d="M104 62 L132 290 L308 290 L336 62 Z"/></clipPath></defs>
    <line x1="24" y1="318" x2="416" y2="318" stroke="{BONE}" stroke-opacity=".22" stroke-width="3" stroke-linecap="round"/>
    <ellipse id="{bid}-pud" cx="220" cy="318" rx="0" ry="0" fill="{BLUE}"/>
    <path id="{bid}-hs" d="M246 30 Q236 70 232 300" stroke="{BLUE}" stroke-width="12" fill="none" stroke-linecap="round" stroke-dasharray="18 10" opacity="0"/>
    {''.join(f'<circle id="{bid}-d{i}" cx="{x}" cy="10" r="7" fill="{BLUE}" opacity="0"/>' for i, x in enumerate((150, 196, 242, 284, 172, 264)))}
    <g clip-path="url(#{bid}-clip)"><rect id="{bid}-w" x="90" y="290" width="260" height="280" fill="{BLUE}"/></g>
    <path id="{bid}-s0" class="st" d="M106 190 Q84 250 74 316"/><path id="{bid}-s1" class="st" d="M334 170 Q358 245 370 316"/><path id="{bid}-s2" class="st" d="M326 236 Q342 280 348 316"/>
    <path d="M100 58 L130 286 Q131 296 141 296 L299 296 Q309 296 310 286 L340 58" fill="none" stroke="{BONE}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    <line x1="88" y1="58" x2="352" y2="58" stroke="{BONE}" stroke-width="9" stroke-linecap="round"/>
    <circle id="{bid}-h0" class="hole" cx="109" cy="190" r="9"/><circle id="{bid}-h1" class="hole" cx="331" cy="170" r="9"/><circle id="{bid}-h2" class="hole" cx="323" cy="236" r="9"/>
    <g id="{bid}-hose" opacity="0"><path d="M452 4 C 380 -8, 310 -6, 268 16" stroke="{GREY}" stroke-width="16" fill="none" stroke-linecap="round"/><rect x="236" y="12" width="34" height="22" rx="5" fill="{GREY}" transform="rotate(-24 253 23)"/></g>
  </svg>'''
    f0, f1 = card(bid, t_in, t_out, label=label, rows=rows, width=560, extra_html=svg)
    script(bid, f0, f1)
def level(bid, y, f, dur_f, ease='power1.inOut'):
    js.append(f'tl.to("#{bid}-w", {{ attr: {{ y: {y} }}, duration: {P(dur_f)}, ease: "{ease}" }}, {P(f)});')
def drops(bid, f, f_end, land=280, every=7):
    k = 0; ff = f
    while ff + 12 < f_end:
        d = f'#{bid}-d{k % 6}'
        js.append(f'tl.fromTo("{d}", {{ attr: {{ cy: 10 }}, opacity: 1 }}, {{ attr: {{ cy: {land} }}, duration: {P(11)}, ease: "power1.in", immediateRender: false }}, {P(ff)});')
        js.append(f'tl.set("{d}", {{ opacity: 0 }}, {P(ff + 11)});')
        ff += every; k += 1
def leak(bid, i, f, f_end, drip=True):
    js.append(f'tl.fromTo("#{bid}-h{i}", {{ opacity: 0, scale: 0 }}, {{ opacity: 1, scale: 1, duration: {P(6)}, ease: "back.out(3)", transformOrigin: "50% 50%" }}, {P(f)});')
    js.append(f'tl.set("#{bid}-s{i}", {{ opacity: 1 }}, {P(f + 3)});')
    n = max(1, math.ceil((f_end - f - 3) / 12))
    js.append(f'tl.fromTo("#{bid}-s{i}", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -42, duration: {P(12)}, ease: "none", repeat: {n - 1} }}, {P(f + 3)});')
    if drip: sfx.append(('pop.mp3', P(f), -25))

# ================================================================ THE EDIT
# ---- HOOK (0:00 - 0:14) -------------------------------------------------
html.append('<div class="hookc" id="c1"><span>Most traders who try coaching</span><span>will <b>QUIT</b> in the first 90 days</span></div>')
show('#c1', 6, 6, 26); hide('#c1', F(T("it's not because")) - 3)
html.append('<div class="hookc" id="c2"><span>They build everything</span><span>in the <b>WRONG ORDER</b></span></div>')
show('#c2', F(T('they just build')) - LEAD, 6, 26); hide('#c2', F(T('so in this video')) - 6)
zoom(T('quit in the first'), T("it's not because") - 0.05, 1.10)
zoom(T('wrong order'), T('so in this video') - 0.1, 1.08, ramp_out=8)

# title card: "So in this video I'm going to break down the right order"
TI0, TI1 = F(T('so in this video')) - 4, F(T("we'll do it in 3 phases")) - 2
html.append('<div id="title"><div class="t1">TRADER TO COACH</div><div class="t2">The 90-Day Blueprint</div><div class="t3">Building a Coaching Business from Scratch</div></div>')
js.append(f'tl.to("#title", {{ opacity: 1, duration: {P(5)}, ease: "power1.out" }}, {P(TI0)});')
js.append(f'tl.fromTo("#title .t1", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: {P(8)}, ease: "power3.out" }}, {P(TI0 + 3)});')
js.append(f'tl.fromTo("#title .t2", {{ opacity: 0, y: 44 }}, {{ opacity: 1, y: 0, duration: {P(9)}, ease: "power3.out" }}, {P(TI0 + 5)});')
js.append(f'tl.fromTo("#title .t3", {{ opacity: 0 }}, {{ opacity: 0.7, duration: {P(9)}, ease: "power1.out" }}, {P(TI0 + 9)});')
js.append(f'tl.to("#title", {{ opacity: 0, duration: {P(6)}, ease: "power1.in" }}, {P(TI1 - 6)});')

# roadmap intro: "we'll do it in 3 phases, 90 days"
b0 = TI1 - 2
bar_up(b0)
slot('l', b0 + 2, F(T("so what's the wrong order")) - 7, 'THE PLAN', '3 phases', frames=True)
slot('r', F(T('90 days and')) - LEAD, F(T("so what's the wrong order")) - 4, 'TIMELINE', '*90* days', pop=True, frames=True)
for n in (1, 2, 3): lit(n, F(T('3 phases')) + 5 * (n - 1))
for n in (1, 2, 3): lit(n, F(T("so what's the wrong order")) - 4, on=False)

# ---- CORE CONCEPT (0:14 - 0:58) ----------------------------------------
slot('l', T("so what's the wrong order"), T('someone will get into coaching') - 0.1, 'THE PROBLEM', 'The *wrong* order')
bar_down(F(T('someone will get into coaching')) - 2)

card('k1', T('ads', 0) - 0.3, T("here's the problem") - 0.25, label='DAY ONE: SPEND ALL THE MONEY',
     chips=[(T('ads', 0), 'ADS', 'on'), (T('setter', 0), 'A SETTER', 'on'), (T('closer', 0), 'A CLOSER', 'on'), (T('content manager'), 'A CONTENT MANAGER', 'on')], width=630)
card('k2', T("here's the problem"), T('if what you have works') - 0.15, label='THE PROBLEM',
     head="Ads and people don't *create* anything.", rows=[(T('you just add to what'), "They only add to what you've already got.", 'arr')], width=670)
zoom(T("here's the problem"), T('you just add to what') - 0.1, 1.08)
card('k3', T('if what you have works'), T('and at the start you') - 0.1, label='ADS + PEOPLE MULTIPLY',
     rows=[(T('if what you have works'), 'It works &rarr; *more* of what works', 'ok'), (T("if it doesn't work"), "It doesn't &rarr; *more* mess", 'x')], width=630)
card('k4', T('and at the start you'), T("so there's nothing to multiply") - 0.1, label="AT THE START, YOU DON'T KNOW",
     rows=[(T("don't know what works"), 'What works', 'q'), (T("don't know which message"), 'Which message lands', 'q'),
           (T("don't know what people will say"), 'What people say before they buy', 'q'), (T("don't even know"), 'Your sales process', 'q')], width=650)
zoom(T("so there's nothing to multiply"), T("at the start it's all about") - 0.15, 1.08)
impact('i1', T('volume', 0), T('lots of messages') - 0.1, 'VOLUME FIRST')
zoom(T('volume', 0), T('lots of messages') + 0.3, 1.10)
card('k5', T('lots of content'), T("so here's the order") - 0.15, label='AT THE START',
     chips=[(T('lots of content'), 'LOTS OF CONTENT', 'on'), (T('lots of messages'), 'LOTS OF MESSAGES', 'on'), (T('by yourself'), 'DONE BY YOU', 'ok')], width=630)

# ---- PHASE 1 (0:58 - 3:25) ----------------------------------------------
p1 = F(T('phase one')) - LEAD
bar_up(p1); lit(1, p1 + 4); sfx.append(('whoosh.mp3', P(p1), -21))
slot('l', p1 + 2, F(T('first i want to picture')) - 4, 'PHASE 1', 'Brand &amp; Build', frames=True)
slot('r', F(T('days one to thirty')) - LEAD, F(T('first i want to picture')) - 4, 'DAYS', '*1 &ndash; 30*', frames=True)
bar_down(F(T('first i want to picture')) - 2)

def scene_fill(b, f0, f1):
    drops(b, F(T('then we have water')), f1 - 4)
    level(b, 150, F(T('then we have water')) + 10, f1 - 8 - F(T('then we have water')) - 10, 'none')
bucket('bA', T('first i want to picture') + 0.1, T('there are four things') - 0.15, 'PICTURE A BUCKET',
       [(T('your business is the bucket'), 'The bucket = *your business*', 'dot'), (T('then we have water'), 'The water = *people*', 'dot'),
        (T('first thirty days your job'), 'Days 1&ndash;30: *fill it*', 'arr')], scene_fill)

card('n1', T('number one is your positioning'), T('i coach traders') - 0.12, label='1 OF 4', head='*01* &nbsp;Positioning',
     rows=[(T('who do you help'), 'Who you help + what you help them with', 'arr')], width=670)
card('n1b', T('i coach traders'), T('number two') - 0.2, label='YOUR ONE SENTENCE',
     rows=[(T('i coach traders'), '&ldquo;I coach traders&rdquo; &mdash; too wide', 'x'), (T('i help young people'), '&ldquo;I help young people travel the world with trading&rdquo;', 'ok')], width=690)
zoom(T("they'll start to listen"), T('number two') - 0.25, 1.07)
card('n2', T('number two'), T('when someone lands') - 0.15, label='2 OF 4', head='*02* &nbsp;Brand foundation',
     chips=[(T('your profile'), 'PROFILE', 'on'), (T('your bio'), 'BIO', 'on'), (T('the proof you'), 'PROOF', 'on'), (T('your story'), 'YOUR STORY', 'on')], width=670)
card('n2b', T("you don't need a logo"), T('number three') - 0.2, label='SKIP FOR NOW',
     chips=[(T('a logo'), 'LOGO', 'x'), (T('a website'), 'WEBSITE', 'x')],
     rows=[(T("your brand's going to get"), 'Your brand gets sharp *as* you post, not before', 'arr')], width=670)
card('n3', T('number three'), T('so you pick a few') - 0.15, label='3 OF 4', head='*03* &nbsp;Content engine',
     rows=[(T('this is the volume part'), 'The volume part: the most important part of the 90 days', 'arr')], width=670)
zoom(T('this is the volume part'), T('so you pick a few') - 0.2, 1.07)
card('n3b', T('something like you want'), T('and then show up') - 0.12, label='PICK YOUR OWN PACE',
     rows=[(T('four to five'), '*4&ndash;5* Instagram Reels a week', 'dot'), (T('two to three long'), '*2&ndash;3* long-form YouTube videos', 'dot'), (T('repurpose them'), 'Repurpose across every other platform', 'arr')], width=670)
impact('i2', T('show up every time'), T('your first content') - 0.1, 'SHOW UP EVERY TIME', hit=False)
zoom(T('show up every time'), T('your first content') - 0.1, 1.10)
card('n3c', T('the early content'), T('number four') - 0.2, label='EARLY CONTENT',
     head="Isn't there to be perfect.", rows=[(T("it's there to teach you"), "It's there to *teach* you what people respond to", 'arr')], width=670)
card('n4', T('number four'), T("don't build a big course") - 0.15, label='4 OF 4', head='*04* &nbsp;Offer + conversations',
     chips=[(T('who is it for'), "WHO IT'S FOR", 'on'), (T('what they get'), 'WHAT THEY GET', 'on'), (T('how long it runs'), 'HOW LONG', 'on'), (T('a price you can'), 'THE PRICE', 'on')], width=690)
card('n4b', T("don't build a big course"), T('then go and have') - 0.15, label='A SIMPLE OFFER',
     rows=[(T("don't build a big course"), 'A big course', 'x'), (T("don't record hundreds"), 'Hundreds of videos', 'x'), (T('just keep it simple'), 'Keep it *simple*', 'ok')], width=580)
card('n4c', T('not a setter'), T('i know this might seem') - 0.1, label='WHO HAS THE CONVERSATIONS?',
     chips=[(T('not a setter'), 'A SETTER', 'x'), (T('not a closer'), 'A CLOSER', 'x'), (TL('not a closer you'), 'YOU', 'ok')], width=630)
zoom(TL('not a closer you'), T('i know this might seem') - 0.1, 1.10)
card('n4d', T('every conversation every call'), T('if you hire someone on day one') - 0.2, label='DO IT YOURSELF', head='Every call is *research*',
     rows=[(T('you hear the questions'), 'The questions people ask', 'dot'), (T('you hear why they say no'), 'Why they say no', 'dot'),
           (T('you hear their problems'), 'Their problems, in their own words', 'dot'), (T('and all of this goes back'), 'It all feeds your *content* and your *offer*', 'arr')], width=670)
zoom(T('if you hire someone on day one'), T("so that's phase one") - 0.05, 1.07)
card('n5', T("so that's phase one"), T('phase two') - 0.3, label='PHASE 1 &middot; RECAP',
     rows=[(T('one clear sentence'), 'One clear sentence', 'ok'), (T('simple profile'), 'A simple profile', 'ok'), (T('lots of content', 1), 'Lots of content', 'ok'),
           (T('simple offer'), 'A simple offer', 'ok'), (T('lots of conversations'), 'Lots of conversations, by you', 'ok')], width=630)

# ---- PHASE 2 (3:25 - 6:08) ----------------------------------------------
p2 = F(T('phase two', 0)) - LEAD
bar_up(p2); lit(2, p2 + 4); sfx.append(('whoosh.mp3', P(p2), -21))
slot('l', p2 + 2, F(T("let's go back to the bucket")) - 4, 'PHASE 2', 'Fix the leaks', frames=True)
slot('r', F(T('days 31 to 60')) - LEAD, F(T("let's go back to the bucket")) - 4, 'DAYS', '*31 &ndash; 60*', frames=True)
bar_down(F(T("let's go back to the bucket")) - 2)

def scene_leaks(b, f0, f1):
    js.append(f'tl.set("#{b}-w", {{ attr: {{ y: 150 }} }}, {P(f0)});')
    h = F(T('holes on it'))
    for i in range(3): leak(b, i, h + 8 * i, f1)
    level(b, 228, h + 6, f1 - h - 10, 'none')
    js.append(f'tl.to("#{b}-pud", {{ attr: {{ rx: 180, ry: 7 }}, duration: {P(f1 - h - 16)}, ease: "power1.out" }}, {P(h + 14)});')
bucket('bB', T("let's go back to the bucket") + 0.1, T("so how'd you find it") - 0.15, 'BACK TO THE BUCKET',
       [(T('a bucket with holes'), 'Your business is a bucket with *holes*', 'dot'), (T('and every bucket leaks'), '*Every* bucket leaks. Yours will too', 'dot'),
        (T("we're trying to fill the biggest"), 'Fix the *biggest* holes first', 'arr')], scene_leaks)
zoom(T('and every bucket leaks'), T("we're not trying to build") - 0.15, 1.08)

# pipeline: "So how'd you find it? You draw the path. Let me show you."
pf0, pf1 = _claim('pipe', F(T("so how'd you find it")) - LEAD, MIRO_IN)
NODES = ['SEES YOUR CONTENT', 'FOLLOWS', 'TALKS TO YOU', 'BUYS']
html.append('<div class="pipe" id="pipe"><div class="lab">DRAW THE PATH</div><div class="prow">' +
            ''.join((f'<svg class="parr" id="pa{i}" viewBox="0 0 60 24"><path d="M2 12h50M42 3l11 9-11 9" fill="none" stroke="{BONE}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>' if i else '') + f'<div class="pnode" id="pn{i}">{n}</div>' for i, n in enumerate(NODES)) + '</div></div>')
show('#pipe', pf0)
pstart = pf0 + 3          # the path builds as soon as the panel is up (an empty panel reads as a glitch)
for i in range(4):
    f = pstart + 7 * i
    if i: js.append(f'tl.fromTo("#pa{i}", {{ opacity: 0, x: -14 }}, {{ opacity: 1, x: 0, duration: {P(6)}, ease: "power2.out" }}, {P(f - 3)});')
    js.append(f'tl.fromTo("#pn{i}", {{ opacity: 0, scale: 0.7 }}, {{ opacity: 1, scale: 1, duration: {P(7)}, ease: "back.out(2)" }}, {P(f)});')
    sfx.append(('click.wav', P(f), -25))
js.append(f'tl.set("#pipe", {{ opacity: 0 }}, {P(pf1)});')

# ---- Miro screen recording: the bar stays up (it also hides Miro's "What shall we do next?" box) ----
js.append(f'tl.set("#bar", {{ y: 0 }}, {P(MIRO_IN)});'); js.append(f'tl.set("#thin", {{ opacity: 0 }}, {P(MIRO_IN)});')
slot('l', MIRO_IN + 6, F(T('so let me get straight into')) - 4, 'LIVE PIPELINE', 'From stranger to customer', frames=True)
slot('r', T('box one'), T('and then it goes on'), 'STEP 1', 'Sees your content')
slot('r', T('and then it goes on'), T('and then to talk to'), 'STEP 2', 'Follows you')
slot('r', T('and then to talk to'), E('you start a conversation'), 'STEP 3', 'Talks to you')
slot('r', T('and then they buy'), T('so let me get straight into') - 0.1, 'STEP 4', '*Buys*')
slot('l', T("so let's say 10,000"), T('then we go into example two') - 0.2, 'EXAMPLE 1', '10,000 see &rarr; 300 follow')
slot('r', T("that's 97"), T("so one thing i'd", 0) - 0.1, 'THE LEAK', '*97%* drop', pop=True)
slot('r', T("so one thing i'd", 0), T('or some free education') - 0.15, 'THE FIX', 'Add a *call to action*')
slot('r', T('or some free education'), T('then we go into example two') - 0.2, 'THE FIX', 'Give a *reason* to follow')
slot('l', T('then we go into example two'), T("so one thing i'd", 1) - 0.15, 'EXAMPLE 2', 'People talk. Nobody buys.')
slot('r', T('99'), T("so one thing i'd", 1) - 0.15, 'THE LEAK', '*99%* leave here', pop=True)
slot('l', T("so one thing i'd", 1), T('so one all at a time') - 0.3, 'THE FIX', 'Your *sales process*')
slot('r', T("you're closing and you're setting"), T('then also') - 0.2, 'CLOSING', 'Learn how to sell')
slot('r', T('then also'), T('and i think one of') - 0.15, 'SETTING', 'Spot where interest drops')
slot('r', T('let them do'), T('find out the pain points') - 0.1, 'SETTING', 'Let *them* do the talking')
slot('r', T('find out the pain points'), T('but help them out') - 0.1, 'SETTING', 'Find the *pain points*')
slot('r', T('but help them out'), T('so i definitely') - 0.1, 'SETTING', '*Help* them first')
slot('l', F(T('so one all at a time')) - LEAD, MIRO_OUT - 5, 'THE RULE', '*One* leak at a time', frames=True)
slot('r', T('you find the biggest leak'), T('change it'), 'STEP 1', 'Find the biggest leak')
slot('r', T('change it'), T('check your numbers'), 'STEP 2', 'Change one thing')
slot('r', T('check your numbers'), T('if that works'), 'STEP 3', 'Check your numbers')
slot('r', T('if that works'), T('you just keep doing this') + 0.2, 'STEP 4', 'Then the *next* leak')

# ---- PHASE 3 (6:08 - 8:12) ----------------------------------------------
p3 = MIRO_OUT
lit(3, p3 + 4); sfx.append(('whoosh.mp3', P(p3), -21))
slot('l', p3 + 2, F(T('this is the part everyone')) - 4, 'PHASE 3', 'Scale', frames=True)
slot('r', F(T('day 61')) - LEAD, F(T('this is the part everyone')) - 4, 'DAYS', '*61 &ndash; 90*', frames=True)
bar_down(F(T('this is the part everyone')) - 2)

card('s1', T('this is the part everyone'), T('but first check the bucket') - 0.2, label='PHASE 3', head='The part everyone wants to start with',
     chips=[(T('the ads'), 'THE ADS', 'on'), (T('the team'), 'THE TEAM', 'on')], rows=[(T('and now it all'), '*Now* it finally makes sense', 'ok')], width=670)
impact('i3', T('check the bucket'), T('before we start with anything') - 0.1, 'CHECK THE BUCKET')
zoom(T('but first check the bucket'), T('before we start with anything') - 0.1, 1.10)
card('s2', T('are people moving'), T("if there's still one big hole") - 0.15, label='DOES THE PATH WORK?',
     chips=[(T('the content to the following'), 'CONTENT', 'on'), (T('to the following'), 'FOLLOWING', 'on'), (T('to the talking'), 'TALKING', 'on'), (TL('to your choice selling'), 'SELLING', 'on')], width=720)
card('s3', T("if there's still one big hole"), T('as we start') - 0.2, label='STILL ONE BIG HOLE?',
     head='Go back to *Phase 2* and fix it.', rows=[(T("this doesn't have to be"), "It doesn't have to be day 61", 'arr')], width=650)

def scene_hose(b, f0, f1):
    js.append(f'tl.set("#{b}-w", {{ attr: {{ y: 232 }} }}, {P(f0)});')
    drops(b, F(T("you've been filling the bucket")), F(T('a hose does it')) - 2, every=14)
    level(b, 222, F(T("you've been filling the bucket")), F(T('a hose does it')) - F(T("you've been filling the bucket")), 'none')
    hs = F(T('a hose does it')) - LEAD
    js.append(f'tl.to("#{b}-hose", {{ opacity: 1, duration: {P(6)} }}, {P(F(T("think of ads as a hose")) + 12)});')
    js.append(f'tl.set("#{b}-hs", {{ opacity: 1 }}, {P(hs)});')
    js.append(f'tl.fromTo("#{b}-hs", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -56, duration: {P(8)}, ease: "none", repeat: {math.ceil((f1 - hs) / 8) - 1} }}, {P(hs)});')
    wet = F(T('a hose on a leaky bucket'))
    level(b, 96, hs + 4, wet - hs - 4, 'power1.out')
    for i in range(3): leak(b, i, wet + 4 * i, f1, drip=False)
    level(b, 150, wet + 6, f1 - wet - 8, 'none')
    js.append(f'tl.to("#{b}-pud", {{ attr: {{ rx: 196, ry: 9 }}, duration: {P(f1 - wet - 14)}, ease: "power1.out" }}, {P(wet + 12)});')
bucket('bD', T('think of ads as a hose') - 0.6, T('so we only turn it on') - 0.1, 'ADS = A HOSE',
       [(T('up to now'), 'By hand: slow', 'dot'), (T('a hose on a good bucket'), 'Good bucket + hose = *great*', 'ok'),
        (T('a hose on a leaky bucket'), 'Leaky bucket + hose = *wet floor*', 'x')], scene_hose)
card('s4', T('so if we start small'), T('now people') - 0.25, label='TURNING ADS ON',
     rows=[(T('so if we start small'), 'Start small', 'dot'), (T('and if it works'), 'If it works, increase it', 'arr'), (T("and if your numbers aren't"), "Numbers not there yet? *Wait*", 'x'),
           (T('no ads is perfectly fine'), 'No ads is perfectly fine', 'ok')], width=630)
impact('i4', T("we hire when we're drowning"), T('when your inbox') - 0.15, "HIRE WHEN YOU'RE DROWNING", sub=(T('not just before'), 'Not before.'))
zoom(T("we hire when we're drowning"), T('when your inbox') - 0.15, 1.10)
card('s5', T('when your inbox'), T("if you don't have time to be") - 0.15, label='WHEN TO HIRE',
     rows=[(T('when your inbox'), 'Your inbox is full', 'dot'), (T("you don't have time to reply"), 'No time to reply', 'dot'), (T('12 hours'), 'People left on delivered for 12+ hours', 'dot'),
           (T("that's when we start hiring"), "*That's* when you hire", 'ok')], width=670)
card('s6', T('the work comes first'), T('and this is where phase one') - 0.15, label='THE ORDER',
     rows=[(T('the work comes first'), 'The work comes *first*', 'ok'), (T('the hire comes second'), 'The hire comes *second*', 'arr')], width=580)
zoom(T('the work comes first'), T('and this is where phase one') - 0.15, 1.07)
card('s7', T('and this is where phase one'), T('now you can tell the sales team') + 0.2, label='THE PAYOFF', head='Phase 1 pays you back',
     rows=[(T('you already know the job'), 'You already know the job', 'ok'), (T('you know what people are'), 'You know what people ask', 'ok'), (T('you know how to message'), 'You know how to message people', 'ok')], width=630)
card('s8', T('the one thing you never'), T('and the last rule') - 0.3, label='KEEP IT YOURS', head='Never hand over',
     chips=[(T('your face'), 'YOUR FACE', 'ok'), (T('your voice'), 'YOUR VOICE', 'ok'), (TL('and your content'), 'YOUR CONTENT', 'ok')],
     rows=[(T("they're buying from you"), "They're buying from *you*", 'arr')], width=670)
zoom(T("they're buying from you"), T('and the last rule') - 0.3, 1.08)
impact('i5', T('one thing at a time'), T('add one thing') - 0.2, 'ONE THING AT A TIME')
zoom(T('one thing at a time'), T('add one thing') - 0.2, 1.10)
card('s9', T('add one thing'), T("don't turn on your ads") - 0.2, label='THE LAST RULE',
     chips=[(T('add one thing'), 'ADD ONE THING', 'on'), (T('wait', 1), 'WAIT', 'on'), (T('check if it worked'), 'CHECK', 'on'), (T('then we add the next'), 'ADD THE NEXT', 'ok')], width=720)
card('s10', T("don't turn on your ads"), T("that's the whole thing") - 0.2, label='NOT ALL IN THE SAME WEEK',
     chips=[(T("don't turn on your ads"), 'ADS', 'x'), (T('hire two'), 'TWO OR THREE HIRES', 'x')],
     rows=[(T('because if something breaks'), "If something breaks, you won't know what broke", 'arr')], width=690)

# ---- CLOSE (8:12 - 8:49) ------------------------------------------------
r0 = F(T('brand and volume first')) - LEAD
bar_up(r0)
slot('l', r0 + 2, F(T('so now let me give you')) - 4, 'THE WHOLE THING', 'In the *right* order', frames=True)
pulse(1, F(T('brand and volume first'))); pulse(2, F(T('fix the holes', 0))); pulse(3, F(T('then scale')))
bar_down(F(T('so now let me give you')) - 2)
card('z1', T('one pour water in') - 0.2, T('most people do it backwards') - 0.15, label='THE WHOLE 90 DAYS',
     rows=[(T('one pour water in'), 'Pour water in', '1'), (T('two fix the holes'), 'Fix the holes', '2'), (T('three get your hose on'), 'Get your hose on', '3')], width=540)
card('z2', T('most people do it backwards'), T('one quick but important') - 0.15, label='MOST PEOPLE DO IT BACKWARDS',
     rows=[(T("they'll buy the hose first"), 'They buy the hose first', 'x'), (T('but now you know'), 'Now you know the *right order*', 'ok')], width=630)
zoom(T('but now you know'), T('one quick but important') - 0.15, 1.08)
html.append('<div class="disc" id="disc">Business coaching only. Not financial or trading advice. Results vary and nothing in this video is promised.</div>')
show('#disc', F(T('one quick but important')) - LEAD, 6, 14); hide('#disc', F(T('if you want this laid out')) - 6)

# CTA: "send me a message saying doc"
c0 = F(T('if you want this laid out')) - LEAD; cdoc = F(T('send me a message')) - LEAD
html.append(f'''<div id="cta"><svg class="doc" viewBox="0 0 96 120"><path d="M14 6h46l22 22v80a6 6 0 0 1-6 6H14a6 6 0 0 1-6-6V12a6 6 0 0 1 6-6z" fill="none" stroke="{BLUE}" stroke-width="6" stroke-linejoin="round"/><path d="M58 6v24h24" fill="none" stroke="{BLUE}" stroke-width="6" stroke-linejoin="round"/><path d="M26 56h44M26 74h44M26 92h28" stroke="{BLUE}" stroke-width="6" stroke-linecap="round"/></svg>
  <div class="ctxt"><div class="lab">FREE RESOURCE</div><div class="chd">The 90-Day Blueprint</div><div class="csub">Step by step, with checklists</div></div>
  <div class="cbox" id="cbox"><div class="cb1">MESSAGE ME</div><div class="cb2">&ldquo;DOC&rdquo;</div></div></div>''')
js.append(f'tl.to("#thin", {{ opacity: 0, duration: {P(4)} }}, {P(c0)});')
js.append(f'tl.to("#cta", {{ y: 0, duration: {P(12)}, ease: "power3.out" }}, {P(c0)});')
js.append(f'tl.fromTo("#cbox", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: {P(9)}, ease: "back.out(2.2)" }}, {P(cdoc)});')
npulse = (NF - cdoc - 12) // 24
js.append(f'tl.fromTo("#cbox", {{ boxShadow: "0 0 0 0 rgba(47,111,237,0.0)" }}, {{ boxShadow: "0 0 0 14px rgba(47,111,237,0.34)", duration: {P(12)}, ease: "sine.inOut", yoyo: true, repeat: {npulse * 2 - 1} }}, {P(cdoc + 9)});')
sfx.append(('notification.mp3', P(cdoc), -21))
zoom(T('send me a message'), T('thank you') - 0.1, 1.07)

assert not MISSING and not SHORT, (MISSING, SHORT)

# ================================================================ page
CSS = f'''
@font-face {{ font-family: 'Inter'; font-weight: 500; src: url('assets/fonts/inter-latin-500-normal.woff2') format('woff2'); }}
@font-face {{ font-family: 'Inter'; font-weight: 600; src: url('assets/fonts/inter-latin-600-normal.woff2') format('woff2'); }}
@font-face {{ font-family: 'Inter'; font-weight: 700; src: url('assets/fonts/inter-latin-700-normal.woff2') format('woff2'); }}
@font-face {{ font-family: 'Inter'; font-weight: 800; src: url('assets/fonts/inter-latin-800-normal.woff2') format('woff2'); }}
@font-face {{ font-family: 'Inter'; font-weight: 900; src: url('assets/fonts/inter-latin-900-normal.woff2') format('woff2'); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ background: transparent; }}
#trader-to-coach {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; font-family: 'Inter', sans-serif; color: {BONE}; }}
#base {{ position: absolute; inset: 0; width: 1920px; height: 1080px; object-fit: cover; z-index: 0; }}
body.capture #base {{ display: none; }}
b {{ color: {BLUE}; font-weight: inherit; }}
.lab {{ font-weight: 600; font-size: 22px; letter-spacing: 0.1em; text-transform: uppercase; color: {BLUE}; }}

/* lower-left cards */
.card {{ position: absolute; left: 72px; bottom: 140px; max-width: 720px; padding: 28px 34px 30px; background: rgba(10,10,10,0.93);
  border: 1.5px solid rgba(47,111,237,0.6); border-radius: 18px; box-shadow: 0 18px 50px rgba(0,0,0,0.45); opacity: 0; z-index: 10; }}
.card .hd {{ margin-top: 10px; font-weight: 800; font-size: 48px; line-height: 1.12; letter-spacing: -0.03em; }}
.card .rows {{ margin-top: 5px; }}
.card .rw {{ overflow: hidden; height: 0; opacity: 0; }}
.card .rw.on {{ height: auto; opacity: 1; }}
.card .row {{ display: flex; align-items: flex-start; gap: 14px; padding-top: 13px; font-weight: 600; font-size: 34px; line-height: 1.2; letter-spacing: -0.015em; }}
.card .row .ic {{ flex: none; width: 36px; height: 36px; margin-top: 3px; }}
.card .row .num {{ flex: none; width: 44px; height: 44px; margin-top: -1px; border-radius: 10px; background: {BLUE}; color: #fff; font-weight: 800; font-size: 24px; display: flex; align-items: center; justify-content: center; }}
.card .chipw {{ overflow: hidden; }}
.card .chips {{ padding: 16px 2px 4px; display: flex; flex-wrap: wrap; gap: 12px; }}
.chip {{ padding: 11px 20px 12px; border-radius: 999px; font-weight: 700; font-size: 28px; letter-spacing: 0.04em; opacity: 0; transform-origin: 50% 50%;
  background: rgba(242,239,233,0.1); border: 1.5px solid rgba(242,239,233,0.4); color: {BONE}; }}
.chip.ok {{ background: {BLUE}; border-color: {BLUE}; color: #fff; }}
.chip.x {{ background: transparent; border-color: rgba(232,229,223,0.35); color: rgba(232,229,223,0.6); text-decoration: line-through; text-decoration-thickness: 2.5px; }}
.card .bk {{ display: block; margin: 12px auto 0; overflow: visible; }}
.bk .st {{ fill: none; stroke: {BLUE}; stroke-width: 6; stroke-linecap: round; stroke-dasharray: 12 9; opacity: 0; }}
.bk .hole {{ fill: {BLACK}; stroke: {BONE}; stroke-width: 3; opacity: 0; }}

/* hook lines */
.hookc {{ position: absolute; left: 0; right: 0; top: 770px; display: flex; flex-direction: column; align-items: center; gap: 4px; opacity: 0; z-index: 12;
  font-weight: 800; font-size: 66px; line-height: 1.1; letter-spacing: -0.03em; text-align: center; }}
.hookc span {{ padding: 6px 26px 10px; background: rgba(10,10,10,0.9); border-radius: 12px; white-space: nowrap; }}

/* impact text */
.impact {{ position: absolute; left: 0; right: 0; top: 760px; display: flex; flex-direction: column; align-items: center; gap: 12px; opacity: 0; z-index: 14; transform-origin: 50% 50%; }}
.impact .box {{ padding: 10px 36px 16px; background: {BLACK}; border-radius: 14px; font-weight: 900; font-size: 104px; line-height: 1; letter-spacing: -0.04em; color: {BLUE}; white-space: nowrap; }}
.impact .box span {{ display: inline-block; opacity: 0; transform-origin: 50% 60%; }}
.impact .box span + span {{ margin-left: 0.24em; }}
.impact .isub {{ padding: 6px 22px 8px; background: rgba(10,10,10,0.9); border-radius: 10px; font-weight: 700; font-size: 38px; letter-spacing: -0.02em; opacity: 0; }}

/* title card */
#title {{ position: absolute; inset: 0; background: {BLACK}; display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; z-index: 30; }}
#title .t1 {{ font-weight: 600; font-size: 30px; letter-spacing: 0.26em; color: {BLUE}; opacity: 0; }}
#title .t2 {{ margin-top: 22px; font-weight: 800; font-size: 132px; line-height: 1.02; letter-spacing: -0.035em; opacity: 0; }}
#title .t3 {{ margin-top: 30px; font-weight: 500; font-size: 34px; letter-spacing: -0.005em; opacity: 0; }}

/* roadmap: thin line (always on) and the full bottom bar */
#thin {{ position: absolute; left: 192px; width: 1536px; top: 1056px; height: 4px; display: flex; gap: 12px; opacity: 0; z-index: 5; }}
#thin .seg {{ position: relative; flex: 1; height: 4px; border-radius: 2px; background: rgba(242,239,233,0.3); }}
#thin .seg i {{ position: absolute; inset: 0; border-radius: 2px; background: {BLUE}; opacity: 0; }}
#bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: 128px; background: {BLACK}; border-top: 2px solid {BLUE}; z-index: 20; }}
#bar .side {{ position: absolute; top: 0; height: 126px; width: 520px; }}
#bar-l {{ left: 56px; }} #bar-r {{ right: 56px; }}
#bar .sl {{ position: absolute; top: 0; height: 126px; display: flex; flex-direction: column; justify-content: center; gap: 4px; opacity: 0; white-space: nowrap; }}
#bar-l .sl {{ left: 0; align-items: flex-start; transform-origin: 0 50%; }} #bar-r .sl {{ right: 0; align-items: flex-end; transform-origin: 100% 50%; }}
#bar .slab {{ font-weight: 600; font-size: 20px; letter-spacing: 0.12em; color: {BLUE}; }}
#bar .shd {{ font-weight: 800; font-size: 40px; line-height: 1.08; letter-spacing: -0.03em; }}
#bar-c {{ position: absolute; left: 590px; width: 740px; top: 0; height: 126px; display: flex; gap: 14px; align-items: center; }}
#bar-c .seg {{ flex: 1; transform-origin: 50% 50%; }}
#bar-c .ln {{ position: relative; height: 8px; border-radius: 4px; background: rgba(242,239,233,0.25); }}
#bar-c .ln i {{ position: absolute; inset: 0; border-radius: 4px; background: {BLUE}; opacity: 0; }}
#bar-c .sn {{ margin-top: 12px; font-weight: 700; font-size: 23px; letter-spacing: 0.06em; opacity: 0.42; white-space: nowrap; }}
#bar-c .sd {{ margin-top: 3px; font-weight: 500; font-size: 18px; letter-spacing: 0.08em; opacity: 0.42; color: {GREY}; }}

/* pipeline */
.pipe {{ position: absolute; left: 0; right: 0; bottom: 150px; display: flex; flex-direction: column; align-items: center; gap: 16px; opacity: 0; z-index: 12; }}
.pipe .lab {{ padding: 8px 18px; background: rgba(10,10,10,0.92); border-radius: 999px; }}
.pipe .prow {{ display: flex; align-items: center; gap: 14px; padding: 22px 26px; background: rgba(10,10,10,0.93); border: 1.5px solid rgba(47,111,237,0.6); border-radius: 22px; box-shadow: 0 18px 50px rgba(0,0,0,0.45); }}
.pnode {{ padding: 20px 30px 22px; border-radius: 14px; background: {BLUE}; color: #fff; font-weight: 800; font-size: 32px; letter-spacing: 0.01em; white-space: nowrap; opacity: 0; transform-origin: 50% 50%; }}
.parr {{ width: 60px; height: 24px; opacity: 0; }}

/* disclaimer + CTA */
.disc {{ position: absolute; left: 72px; bottom: 140px; width: 760px; padding: 18px 24px 20px; background: rgba(10,10,10,0.93); border-left: 5px solid {BLUE}; border-radius: 10px; font-weight: 500; font-size: 27px; line-height: 1.3; opacity: 0; z-index: 10; }}
#cta {{ position: absolute; left: 0; right: 0; bottom: 0; height: 302px; background: rgba(10,10,10,0.94); border-top: 2px solid {BLUE}; z-index: 25; display: flex; align-items: center; padding: 0 110px; gap: 44px; }}
#cta .doc {{ width: 112px; height: 140px; flex: none; }}
#cta .ctxt {{ flex: 1; }}
#cta .lab {{ font-size: 24px; }}
#cta .chd {{ margin-top: 10px; font-weight: 800; font-size: 76px; line-height: 1.04; letter-spacing: -0.035em; }}
#cta .csub {{ margin-top: 12px; font-weight: 500; font-size: 32px; color: {GREY}; }}
#cta .cbox {{ flex: none; padding: 22px 46px 26px; border-radius: 22px; background: {BLUE}; color: #fff; text-align: center; opacity: 0; transform-origin: 50% 50%; }}
#cta .cb1 {{ font-weight: 700; font-size: 30px; letter-spacing: 0.14em; }}
#cta .cb2 {{ margin-top: 2px; font-weight: 900; font-size: 104px; line-height: 1; letter-spacing: -0.03em; }}
'''
SEGS = [('BRAND &amp; BUILD', 'DAYS 1&ndash;30'), ('FIX THE LEAKS', 'DAYS 31&ndash;60'), ('SCALE', 'DAYS 61&ndash;90')]
BAR = ('<div id="thin">' + ''.join(f'<div class="seg seg{i + 1}"><i></i></div>' for i in range(3)) + '</div>\n'
       '<div id="bar"><div class="side" id="bar-l">' + ''.join(html_bar['l']) + '</div><div id="bar-c">' +
       ''.join(f'<div class="seg seg{i + 1}"><div class="ln"><i></i></div><div class="sn">{a}</div><div class="sd">{b}</div></div>' for i, (a, b) in enumerate(SEGS)) +
       '</div><div class="side" id="bar-r">' + ''.join(html_bar['r']) + '</div></div>')
# the thin line appears once the intro bar goes away and stays until the CTA card
DUR = NF / FPS
page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Trader to Coach: The 90-Day Blueprint — Stew Scales</title>
  <script src="assets/gsap.min.js"></script>
  <style>{CSS}</style>
</head>
<body>

<div id="trader-to-coach" data-composition-id="trader-to-coach" data-start="0" data-width="1920" data-height="1080">

  <video id="base" data-start="0" data-duration="{DUR:.4f}" data-track-index="0" src="assets/base-proxy.mp4" muted playsinline></video>
  <audio id="base-audio" data-start="0" data-duration="{DUR:.4f}" data-track-index="1" src="assets/base-proxy.mp4" data-volume="1"></audio>

{BAR}

{chr(10).join(html)}

  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // Generated by scripts/build_overlay.py. Times are frames / 30, taken from the forced-aligned transcript.
    {(chr(10) + '    ').join(js)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines["trader-to-coach"] = tl;
  </script>
</div>

</body>
</html>
'''
open('index.html', 'w').write(page)
zooms.sort()
for (a0, a1, *_), (b0, *_r) in zip(zooms, zooms[1:]): assert b0 > a1 + 12, ('zooms too close', a0, a1, b0)
for a, b, *_ in zooms: assert not (a < MIRO_OUT and b > MIRO_IN), 'no punch-ins over the screen recording'
json.dump({'nf': NF, 'fps': FPS, 'start': START, 'miro': [MIRO_IN, MIRO_OUT], 'zooms': zooms, 'sfx': sorted(sfx, key=lambda s: s[1]),
           'cards': sorted(_cards)}, open('assets/edit.json', 'w'), indent=1)
for side in 'lr':
    ss = sorted(x for x in SLOTS if x[0] == side)
    for (_, a0, a1, h0), (_, b0, b1, h1) in zip(ss, ss[1:]):
        if b0 < a1 + 4 or a1 - a0 < 20: print('SLOT PROBLEM', side, a0, a1, h0, '|', b0, b1, h1)
    if ss[-1][2] - ss[-1][1] < 20: print('SLOT SHORT', ss[-1])
print('cards', len(_cards), 'zooms', len(zooms), 'sfx', len(sfx), 'tweens', len(js))
