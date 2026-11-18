"""Shared timing for the shorts: cut list (EDL), framing schedule and captions for one clip.
Run from the project folder. `python3 -I scripts/shorts.py [clip]` prints the cut list and captions.
Everything is on the 30 fps grid of the source; audio is cut on exactly the same frames as the picture."""
import json, math, sys, re, numpy as np
exec(open('scripts/clips.py').read())
FPS = 30
WORDS = json.load(open('assets/words.json'))
DB = np.load('assets/db.npy')                       # 10 ms RMS level of the source voice track
THR = np.percentile(DB, 5) + 11                    # below this = pause
SIL = DB < THR
for _k in range(1, len(SIL) - 3):                   # a 1-2 frame blip barely over the threshold inside a pause is still pause
    if SIL[_k - 1] and not SIL[_k] and DB[_k] < THR + 4:
        _n = 1 if SIL[_k + 1] else (2 if (SIL[_k + 2] and DB[_k + 1] < THR + 4) else 0)
        if _n: SIL[_k:_k + _n] = True
MIRO = (6895, 11060)                               # screen recording in the long-form: never used
KEEP_AFTER, KEEP_BEFORE, MIN_PAUSE = 0.12, 0.07, 0.30   # a tightened pause keeps 0.12 s after the word and 0.07 s before the next
LEAD, TRAIL, TAIL = 0.07, 0.09, 0.36               # snippet lead-in / lead-out; the last snippet of a clip breathes for TAIL
SNAP = 6                                           # a word that starts within 6 frames after a cut switches on the cut
ZOOM = {'W': 1.02, 'M': 1.065, 'T': 1.11}; CREEP = 0.015; ZMAX = 1.125

def onset(t):
    """Start of speech at/just before aligned time t (end of the pause before it)."""
    k = int(round((t + 0.03) * 100))
    for j in range(k, k - 35, -1):
        if SIL[j]: return (j + 1) / 100, True
    return t, False
def offset(t):
    """End of speech at/just after aligned time t (start of the pause after it)."""
    k = int(round((t - 0.04) * 100))
    for j in range(k, k + 70):
        if SIL[j:j + 5].all(): return j / 100, True
    return t, False
def pauses(t0, t1):
    out = []; k0, k1 = int(t0 * 100), int(t1 * 100); j = k0
    while j < k1:
        if SIL[j]:
            e = j
            while e < k1 and SIL[e]: e += 1
            if (e - j) / 100 >= MIN_PAUSE: out.append((j / 100, e / 100))
            j = e
        else: j += 1
    return out

def build(cid):
    C = CLIPS[cid]; pieces = []; warn = []; snip_of = []
    for si, s in enumerate(C['snips']):
        i, j = s['w']; last = si == len(C['snips']) - 1
        on, ok = onset(WORDS[i]['start']);  off, ok2 = offset(WORDS[j]['end'])
        if 'start' in s: a = s['start']
        else:
            a = int(math.floor((on - LEAD) * FPS))
            if not ok: warn.append(f'snippet {si}: no pause before word {i}')
            elif not SIL[int(a / FPS * 100) + 1:int(on * 100)].all(): a += 1
        tail = C.get('tail')
        if last and tail: b = int(math.ceil((tail['cut'] + tail['hold']) * FPS))
        elif 'end' in s: b = s['end']
        else:
            if not ok2: warn.append(f'snippet {si}: no pause after word {j}')
            want = off + (TAIL if last else TRAIL)
            e = onset(WORDS[j + 1]['start'])[0] if j + 1 < len(WORDS) else off + 1      # where the next sentence starts
            b = int(math.ceil(min(want, e - 0.03) * FPS))
            if last and e - off < 0.28: warn.append(f'last snippet: only {e - off:.2f}s of pause after the last word')
        cuts = []
        for ps, pe in pauses(a / FPS, (tail['cut'] if last and tail else off)):
            ca = int(math.ceil((ps + KEEP_AFTER) * FPS)); cb = int(math.floor((pe - KEEP_BEFORE) * FPS))
            nxt = [w for w in range(i, j + 1) if WORDS[w]['start'] * FPS >= cb - 1][:1]     # first word after the pause
            if nxt:                                           # a lip smack / breath before it: start the shot just before the word instead
                ws = WORDS[nxt[0]]['start']
                on_w = onset(ws)[0]
                if math.floor(ws * FPS) - cb > 5 and int(on_w * 100) - 1 > int(cb / FPS * 100) and DB[int(cb / FPS * 100):int(on_w * 100) - 1].max() < THR + 9:
                    cb = max(cb, int(math.floor((on_w - LEAD) * FPS)))
            if cb - ca >= 4: cuts.append((ca, cb))
        p = a
        for ca, cb in cuts:
            pieces.append((p, ca)); snip_of.append(si); p = cb
        pieces.append((p, b)); snip_of.append(si)
    for a, b in pieces: assert b > a and not (a < MIRO[1] and b > MIRO[0]), (a, b)
    starts = np.cumsum([0] + [b - a for a, b in pieces]).tolist(); NF = starts[-1]
    def out_frame(t, snap=True):
        """Output frame for source time t (a time inside a removed pause maps to the next piece)."""
        f = int(math.floor(t * FPS + 1e-6))
        for (a, b), o in zip(pieces, starts):
            if f < a: return o
            if f < b: return o if (snap and f - a <= SNAP) else o + f - a
        return NF - 1
    return dict(C=C, pieces=pieces, starts=starts, NF=NF, snip_of=snip_of, warn=warn, out_frame=out_frame)

def word_list(E):
    """[(word index, output frame)] in playing order (each snippet's words mapped in its own pieces)."""
    out = []
    for si, s in enumerate(E['C']['snips']):
        ps = [(p, o) for p, o, k in zip(E['pieces'], E['starts'], E['snip_of']) if k == si]
        for wi in range(s['w'][0], s['w'][1] + 1):
            f = int(math.floor(E['C'].get('onset', {}).get(wi, WORDS[wi]['start']) * FPS + 1e-6)); fo = None
            for (a, b), o in ps:
                if f < a: fo = o; break
                if f < b: fo = o if f - a <= SNAP else o + f - a; break
            if fo is None: fo = ps[-1][1] + ps[-1][0][1] - ps[-1][0][0] - 1
            out.append((wi, fo))
    return out

def zoom_schedule(E):
    """Per output frame zoom. Framing changes on cuts; inside a shot only ever a quick push-in on a key word."""
    NF = E['NF']; z = np.zeros(NF); wl = dict(word_list(E)); cutset = set(E['starts'][:-1])
    marks = []                                                   # (output frame, level, on a cut?)
    for si, s in enumerate(E['C']['snips']):
        first = [o for o, k in zip(E['starts'], E['snip_of']) if k == si][0]
        marks.append((first, s['z'], True))
        for wi, lv in sorted(s.get('steps', {}).items()):
            f = wl[wi]; marks.append((f, lv, f in cutset))
    marks.sort(); assert len({m[0] for m in marks}) == len(marks), marks
    for n, (f, lv, oncut) in enumerate(marks):
        end = marks[n + 1][0] if n + 1 < len(marks) else NF
        v0 = ZOOM[lv]; v1 = min(v0 + CREEP * min(1, (end - f) / 150), ZMAX)
        for k in range(f, end): z[k] = v0 + (v1 - v0) * (k - f) / max(1, end - f - 1)
        if not oncut:                                             # push-in: 4-frame ease from the previous framing
            prev = z[f - 1]; assert v0 > prev, ('push-out inside a shot', f)
            o = f - 1
            for k in range(o, min(o + 4, end)):
                u = (k - o + 1) / 4; tgt = z[k] if k >= f else v0
                z[k] = prev + (tgt - prev) * (1 - (1 - u) ** 3)
    assert z.min() >= 1 and z.max() <= ZMAX + 1e-9
    return z

clean = lambda t: re.sub(r"[^A-Z0-9'%$\" -]", '', t.upper()).strip()
def captions(E):
    """[(output frame, [lines], hero)] - phrases of a few words, broken at punctuation and at every cut."""
    C = E['C']; fix, hl, hero, brk, join = (C.get(k, {} if k == 'fix' else set()) for k in ('fix', 'hl', 'hero', 'brk', 'join'))
    wl = word_list(E); cutset = set(E['starts'])
    phrases = [[]]; prev_txt = ''
    for n, (wi, fo) in enumerate(wl):
        txt = fix.get(wi, WORDS[wi]['text'])
        newp = n > 0 and (wi in brk or ((fo in cutset and wl[n - 1][1] != fo) or prev_txt[-1:] in '.,?!' or wi != wl[n - 1][0] + 1) and wi not in join)
        if newp and phrases[-1]: phrases.append([])
        if txt: phrases[-1].append((wi, fo, clean(txt)))
        prev_txt = WORDS[wi]['text']
    caps = []
    for ph in phrases:
        if not ph: continue
        big = any(wi in hero for wi, _, _ in ph); lim = 30 if any(wi in C.get('wide', ()) for wi, _, _ in ph) else 22
        L = len(' '.join(t for _, _, t in ph)); k = max(1, math.ceil(L / lim)); groups = []; cur = []; tgt = L / k
        for item in ph:
            cl = len(' '.join(t for _, _, t in cur))
            if cur and len(groups) < k - 1 and cl + 1 + len(item[2]) / 2 > tgt: groups.append(cur); cur = []
            cur.append(item)
        groups.append(cur)
        for g in groups:
            toks = [('*' if wi in hl else '') + t for wi, _, t in g]; plain = [t for _, _, t in g]; tot = len(' '.join(plain))
            if tot <= (11 if big else 13) or len(g) == 1: lines = [' '.join(toks)]
            else:
                best = min(range(1, len(g)), key=lambda c: abs(len(' '.join(plain[:c])) - len(' '.join(plain[c:]))))
                lines = [' '.join(toks[:best]), ' '.join(toks[best:])]
            assert all(len(l.replace('*', '')) <= (12 if big else 19) for l in lines), lines
            caps.append((g[0][1], lines, 1 if big else 0, g[0][0]))
    # two captions can land on the same frame only if alignment is off; nudge
    for n in range(1, len(caps)):
        if caps[n][0] <= caps[n - 1][0]: caps[n] = (caps[n - 1][0] + 2,) + caps[n][1:]
    return caps

if __name__ == '__main__':
    for cid in ([sys.argv[1]] if len(sys.argv) > 1 else CLIPS):
        E = build(cid); print(f"\n=== {cid}  {E['NF']} frames = {E['NF']/FPS:.2f}s  pieces {len(E['pieces'])}  {E['warn'] or ''}")
        wl = word_list(E)
        for (a, b), o, si in zip(E['pieces'], E['starts'], E['snip_of']):
            ws = ' '.join(f"{WORDS[wi]['text']}" for wi, fo in wl if o <= fo < o + b - a)
            first = [wi for wi, fo in wl if o <= fo < o + b - a][:1]
            print(f"  out {o:4d} ({o/FPS:5.2f}s) src {a}-{b} ({a/FPS:.2f}-{b/FPS:.2f}) s{si} w{first}: {ws}")
        for f, lines, big, wi in captions(E): print(f"     cap @{f:4d} w{wi:<5d}{'HERO ' if big else '     '}{' / '.join(lines)}")
