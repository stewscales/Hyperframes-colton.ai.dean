"""Single source of truth for the edit: where each word starts (output frames), where the B-roll sits,
and the punch-in schedule. Imported (via exec) by render_th.py, prep_broll.py and build_comp.py."""
import json, math
ALIGN = json.load(open('assets/align.json')); EDL = json.load(open('assets/edl.json'))
NF = EDL['n_out']                                   # 687 frames = 22.9 s
CUTS = []; _t = 0
for _a, _b in EDL['segs']:
    CUTS.append(_t); _t += _b - _a
_st = {}
for _w in ALIGN: _st.setdefault(_w['word'], []).append(_w['start'])
def W(word, k=0, snap=True):
    """Output frame on which a spoken word starts; a word that starts within 4 frames after a cut switches on the cut."""
    f = int(math.floor(_st[word][k] * 30 + 1e-6))
    if snap:
        for c in CUTS:
            if 0 <= f - c <= 4: return c
    return f
# ---- B-roll (output frame ranges, end exclusive). Each starts on a word and ends on a word or a cut. ----
BROLL = [
    ('day',    W('POSTING'),  W('AND', 0)),         # "Posting yourself in a Lamborghini"
    ('watch',  W('AND', 0),   CUTS[1]),             # "and flashing your watch" (watch collection clip)
    ('night',  W('EVERY'),    W('YOUR', 3)),        # "every other trading guru online" (one clean clip: night drive)
    ('wrist',  W('FLEXING'),  W('FLEXING') + 22),   # "flexing their..." (watch on the Lamborghini wheel, photo; kept short)
]
FADE = 4                                            # frames of dissolve when a B-roll clip hands back to the talking head
FADES_OUT = ('watch', 'night', 'wrist')             # day cuts straight into the watch clip
# ---- talking-head punch-ins: (start, end, kind, args) per stretch of face time ----
def zoom_schedule():
    z = [1.0] * NF
    def const(a, b, v):
        for k in range(a, b): z[k] = v
    def creep(a, b, v0, v1):
        for k in range(a, b): z[k] = v0 + (v1 - v0) * (k - a) / max(1, b - a - 1)
    def punch(a, b, onset, v, base, ramp=4):
        const(a, b, base); o = max(a, onset - 1)
        for k in range(o, b):
            u = min(1.0, (k - o + 1) / ramp); z[k] = base + (v - base) * (1 - (1 - u) ** 3)
    punch(0, CUTS[1], W('KILLING'), 1.10, 1.02)                       # hook: fast punch on "killing" (runs on under the B-roll)
    punch(CUTS[1], CUTS[2], W('IT', 1), 1.03, 1.08, ramp=5)           # tight on "doesn't make people want to buy", ease out on "it just makes you look like"
    const(W('YOUR', 3), CUTS[2], 1.12)                                # rehook: "your prospects don't care"
    punch(CUTS[2], CUTS[3], W('ACTUALLY'), 1.09, 1.03)                # "actually help them"
    creep(CUTS[3], W("THEY'RE"), 1.00, 1.05)                          # "the best trading coaches online..." slow push
    punch(W("THEY'RE"), CUTS[4], W('BUILDING'), 1.13, 1.06)           # "building trust"
    creep(CUTS[4], CUTS[5], 1.00, 1.03)                               # "if your whole brand is how rich you look"
    punch(CUTS[5], CUTS[6], W('WRONG'), 1.15, 1.11)                   # "the wrong audience"
    creep(CUTS[6], NF, 1.00, 1.03)                                    # CTA: wide, gentle push
    return z
# stretches that share one zoom centre (a centre change mid-stretch would read as a wobble)
def centre_parts():
    b = sorted({0, NF, *CUTS, W('YOUR', 3), W("THEY'RE")})
    return list(zip(b[:-1], b[1:]))
if __name__ == '__main__':
    print('frames', NF, 'cuts', CUTS); print('b-roll', BROLL); print('centre parts', centre_parts())
    z = zoom_schedule(); print('zoom at cuts', [(c, round(z[c - 1], 3) if c else None, round(z[c], 3)) for c in CUTS])
