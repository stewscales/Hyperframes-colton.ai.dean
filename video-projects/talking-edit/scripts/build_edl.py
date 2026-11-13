"""Build the cut list (EDL) from the audio envelope + fade analysis.
Outputs edl.json: keep segments in source frames, the clip each belongs to, and a per-output-frame
map (source frame to display, un-fade gain)."""
import json, sys
import numpy as np
S = sys.argv[1]
db = np.load(S + '/db.npy'); fade = np.load(S + '/fade.npy'); dips = np.load(S + '/dips.npy')
N = len(fade); n = len(db); floor = np.percentile(db, 5); THR = floor + 11
sp = db > THR
gaps = []; st = None
for i, v in enumerate(sp):
    if not v and st is None: st = i
    if v and st is not None:
        if i - st >= 10: gaps.append((st / 100, i / 100))
        st = None
if st is not None: gaps.append((st / 100, n / 100))
bounds = [int(d[3]) for d in dips]                       # first frame of each new clip
clip_of = lambda fr: int(np.searchsorted(bounds, fr, side='right'))
clip_rng = [(([0] + bounds)[i], (bounds + [N])[i]) for i in range(len(bounds) + 1)]
good = []
for a, b in clip_rng:
    g = [x for x in range(a, b) if fade[x] >= 0.20]
    good.append((g[0], g[-1]))
END_PAD, START_PAD, MIN_REMOVE = 0.05, 0.04, 3
cuts = []                                                # (remove_from, remove_to) in frames, exclusive end
for ga, gb in gaps:
    if ga == 0:
        cuts.append((0, int(np.floor((gb - START_PAD) * 30)))); continue
    if gb >= n / 100 - 0.02:
        cuts.append((int(np.ceil((ga + 0.25) * 30)), N)); continue          # leave a 0.25s tail at the end
    r0 = int(np.ceil((ga + END_PAD) * 30)); r1 = int(np.floor((gb - START_PAD) * 30))
    has_dip = any(r0 - 6 <= b <= r1 + 6 for b in bounds)
    if has_dip or r1 - r0 >= MIN_REMOVE:
        cuts.append((r0, max(r1, r0)))
# every dip must be cut even if the audio gap is tiny: make sure unusable frames are never shown (handled by holds)
# Manual overrides at fade dips (checked against the envelope): keep the word tails, drop only dark frames
OVERRIDE = {406: (402, 408), 498: (499, 503), 640: (637, 640)}
for b, (r0, r1) in OVERRIDE.items():
    cuts = [c for c in cuts if not (c[0] - 8 <= b <= c[1] + 8)] + [(r0, r1)]
segs = []; cur = 0
for r0, r1 in sorted(cuts):
    if r0 > cur: segs.append([cur, r0])
    cur = max(cur, r1)
if cur < N: segs.append([cur, N])
# split segments that straddle a clip boundary without a cut (shouldn't happen) and assign clip by majority
out = []; omap = []
for a, b in segs:
    mid = (a + b) // 2
    # a segment belongs to the clip that contains most of it; boundary handled by nearest dip
    c = clip_of(a if (b - a) < 4 else a + 3)
    c_end = clip_of(b - 1 if (b - a) < 4 else b - 4)
    assert c == c_end, (a, b, c, c_end)
    g0, g1 = good[c]
    out.append({'src': [a, b], 'clip': c})
    for x in range(a, b):
        d = min(max(x, g0), g1)
        omap.append({'src': x, 'show': d, 'gain': round(float(1 / max(fade[d], 0.2)), 4) if fade[d] < 0.985 else 1.0, 'seg': len(out) - 1})
print('gaps(thr %.1f):' % THR, ' '.join('%.2f-%.2f' % g for g in gaps))
t = 0
for i, s in enumerate(out):
    a, b = s['src']; holds = sum(1 for m in omap if m['seg'] == i and m['show'] != m['src'])
    mg = max(m['gain'] for m in omap if m['seg'] == i)
    print('seg %2d clip %d src %4d-%4d (%.3f-%.3fs) len %3d -> out %.3fs  holds %d maxgain %.2f' % (i, s['clip'], a, b, a / 30, b / 30, b - a, t / 30, holds, mg))
    t += b - a
print('total frames', t, '= %.2fs (from %.2fs)' % (t / 30, N / 30))
json.dump({'segs': out, 'map': omap, 'bounds': bounds}, open(S + '/edl.json', 'w'))
