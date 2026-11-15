"""Cut list for the talking head: tighten pauses, keep the delivery natural.
Reads a 16 kHz mono wav of the raw clip; pauses of 0.25 s or more are shortened so about 0.13 s of air is left
(0.07 s after the last word, 0.06 s before the next). Cuts sit on the 30 fps frame grid.
Usage: python3 build_cuts.py <raw16k.wav> <n_video_frames> <out edl.json>"""
import sys, json, wave, numpy as np
wav, N, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
w = wave.open(wav); assert w.getframerate() == 16000 and w.getnchannels() == 1 and w.getsampwidth() == 2
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
m = len(x) // 160; db = 20 * np.log10(np.sqrt((x[:m * 160].reshape(m, 160) ** 2).mean(1)) + 1e-6)
THR = np.percentile(db, 5) + 11
MIN_GAP, END_PAD, START_PAD, MIN_REMOVE = 0.25, 0.07, 0.06, 3
sp = db > THR
# bridge blips: a "speech" run shorter than 30 ms inside silence is noise, a silence shorter than 40 ms is inside a word
gaps = []; st = None
for i, v in enumerate(list(sp) + [True]):
    if not v and st is None: st = i
    if v and st is not None:
        gaps.append([st / 100, i / 100]); st = None
merged = []
for g in gaps:
    if merged and g[0] - merged[-1][1] < 0.03: merged[-1][1] = g[1]
    else: merged.append(g)
cuts = []
for ga, gb in merged:
    if gb - ga < MIN_GAP: continue
    if ga <= 0.0:                                   # leading silence
        r1 = int(np.floor((gb - START_PAD) * 30))
        if r1 >= 1: cuts.append((0, r1))
        continue
    if gb >= m / 100 - 0.011:                       # trailing silence: leave a short tail
        r0 = int(np.ceil((ga + 0.20) * 30))
        if r0 < N: cuts.append((r0, N))
        continue
    r0 = int(np.ceil((ga + END_PAD) * 30)); r1 = int(np.floor((gb - START_PAD) * 30))
    if r1 - r0 >= MIN_REMOVE: cuts.append((r0, r1))
segs = []; cur = 0
for r0, r1 in cuts:
    if r0 > cur: segs.append([cur, r0])
    cur = r1
if cur < N: segs.append([cur, N])
t = 0
for i, (a, b) in enumerate(segs):
    print('seg %2d src %3d-%3d (%.3f-%.3fs) len %3d -> out frame %3d (%.3fs)' % (i, a, b, a / 30, b / 30, b - a, t, t / 30)); t += b - a
print('pauses >= %.2fs:' % MIN_GAP, ' '.join('%.2f-%.2f' % tuple(g) for g in merged if g[1] - g[0] >= MIN_GAP))
print('total', t, 'frames = %.2fs (from %.2fs)' % (t / 30, N / 30))
json.dump({'segs': segs, 'n_src': N, 'n_out': t, 'thr_db': float(THR)}, open(out, 'w'))
