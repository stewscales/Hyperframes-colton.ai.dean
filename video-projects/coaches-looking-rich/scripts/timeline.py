"""Single source of truth for timing: word start frames (from forced alignment) and the punch-in schedule.
exec'd by render_th.py and build_comp.py (run from the project folder)."""
import json, math
exec(open('scripts/edl.py').read())
ALIGN = json.load(open('assets/align.json'))
_st = {}
for _w in ALIGN: _st.setdefault(_w['word'], []).append(_w['start'])
def W(word, k=0, snap=True):
    """Output frame on which a spoken word starts; a word that starts within 4 frames after the cut switches on the cut."""
    f = int(math.floor(_st[word][k] * 30 + 1e-6))
    if snap and 0 <= f - CUTS[1] <= 4: return CUTS[1]
    return f
LOOK_UP = 27                        # he looks up from the closed laptop (clip A frame 299)
def zoom_schedule():
    z = [1.0] * NF
    def creep(a, b, v0, v1):
        for k in range(a, b): z[k] = v0 + (v1 - v0) * (k - a) / max(1, b - a - 1)
    def ease(a, b, onset, v0, v1, ramp=4):
        o = max(a, onset - 1)
        for k in range(o, b):
            u = min(1.0, (k - o + 1) / ramp); z[k] = v0 + (v1 - v0) * (1 - (1 - u) ** 3)
    creep(0, LOOK_UP, 1.00, 1.015)                                   # wide: the laptop closes
    creep(LOOK_UP, W("THEY'VE"), 1.09, 1.11)                         # cut in as he looks up: "Coaches are so focused on trying to look rich"
    creep(W("THEY'VE"), CUTS[1], 1.03, 1.03); ease(W("THEY'VE"), CUTS[1], W('BUSINESS'), 1.03, 1.08)   # "...how to build a BUSINESS"
    creep(CUTS[1], W('NONE'), 1.00, 1.00)                            # the list steps in: watches / cars / lifestyle
    ease(CUTS[1], W('NONE'), W('WATCHES'), 1.00, 1.04, 3); ease(CUTS[1], W('NONE'), W('CARS'), 1.04, 1.08, 3); ease(CUTS[1], W('NONE'), W('LIFESTYLE'), 1.08, 1.12, 3)
    creep(W('NONE'), W("ISN'T") - 1, 1.03, 1.05)                     # reset: "None of it actually matters, because the content"
    b = W("ISN'T") - 1; creep(b, NF, 1.05, 1.05); ease(b, NF, W("ISN'T"), 1.05, 1.12)
    c0 = W("ISN'T") + 4; 
    for k in range(c0, NF): z[k] = 1.12 + 0.02 * (k - c0) / (NF - 1 - c0)                                # keeps pushing through the final hold
    return z
def centre_parts():
    b = [0, LOOK_UP, W("THEY'VE"), CUTS[1], W('NONE'), NF]
    return list(zip(b[:-1], b[1:]))
