"""Render the cut + un-faded + punched-in + graded base video (1080x1920) from the 4K source.
Usage: python3 render_base.py <src.mov> <workdir> <audio.wav> <out.mp4> [--preview f1,f2,...]"""
import sys, json, subprocess, numpy as np, cv2
src, S, audio, dst = sys.argv[1:5]
preview = [int(x) for x in sys.argv[6].split(',')] if len(sys.argv) > 6 else None
edl = json.load(open(S + '/edl.json')); omap = edl['map']; segs = edl['segs']
lm = np.load(S + '/lm.npy'); align = json.load(open(S + '/align.json'))
UNF = np.load(S + '/unfade.npy')            # per-frame, per-channel (gain, offset) that maps a faded frame back to its clip's normal look
SW, SH, W, H = 2160, 3840, 1080, 1920
NOUT = len(omap)
seg_start = []; t = 0
for s in segs:
    seg_start.append(t); t += s['src'][1] - s['src'][0]
seg_start.append(t)
word = lambda w, k=0: round([a['start'] for a in align if a['word'] == w][k] * 30)

# ---------- zoom schedule (per output frame) ----------
z = np.ones(NOUT, np.float32)
def const(i, v): z[seg_start[i]:seg_start[i + 1]] = v
def creep(a, b, v0, v1): z[a:b] = np.linspace(v0, v1, b - a)
def punch(i, onset, v, base=1.0, ramp=4):
    a, b = seg_start[i], seg_start[i + 1]
    z[a:b] = base
    o = max(a, onset - 1)
    for k in range(o, b):
        u = min(1.0, (k - o + 1) / ramp); e = 1 - (1 - u) ** 3
        z[k] = base + (v - base) * e
creep(seg_start[0], seg_start[1], 1.00, 1.04)                 # hook: slow push
punch(1, word('SAME'), 1.08)                                   # "SAME post ten times"
punch(2, word('LOSE'), 1.06)                                   # "LOSE attention"
const(3, 1.10)                                                 # "and that's the problem"
const(4, 1.00)                                                 # "so here's the fix"
const(5, 1.08)                                                 # "four types of posts"
punch(6, word('TEACH'), 1.08)
punch(7, word('PROCESS'), 1.08)
const(8, 1.00)                                                 # "not just your wins"
punch(9, word('STORY'), 1.08)
creep(seg_start[10], seg_start[12], 1.02, 1.08)                # story questions: slow push
punch(12, word('OPINION'), 1.08)
punch(13, word('WRONG'), 1.06)
punch(14, word('FOUR', 1), 1.08)                               # "FOUR reasons"
const(15, 1.14)                                                # "not one"
creep(seg_start[16], seg_start[17], 1.00, 1.03)                # CTA: wide, gentle push
# zoom centre: per-segment median nose position (constant inside a segment -> no tracking wobble)
cen = np.zeros((NOUT, 2), np.float32)
for i in range(len(segs)):
    a, b = seg_start[i], seg_start[i + 1]
    cen[a:b] = np.median(lm[[omap[k]['show'] for k in range(a, b)], -1, :], axis=0)
a, b = seg_start[10], seg_start[12]; cen[a:b] = np.median(cen[a:b], axis=0)   # one centre across the slow push
json.dump({'z': [round(float(v), 4) for v in z], 'seg_start': seg_start}, open(S + '/zoom.json', 'w'))

# ---------- grade: slight shadow lift on the face only ----------
A_LIFT, P_LIFT = 0.07, 0.27
def grade(img, pts):
    """img float32 RGB 0..1 (1080x1920); pts: face-oval points in output pixels."""
    c = pts.mean(0); pts = c + (pts - c) * 1.06
    x0, y0 = np.floor(pts.min(0) - 90).astype(int); x1, y1 = np.ceil(pts.max(0) + 90).astype(int)
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    roi = img[y0:y1, x0:x1]
    mask = np.zeros(roi.shape[:2], np.float32)
    cv2.fillConvexPoly(mask, cv2.convexHull((pts - [x0, y0]).astype(np.int32)), 1.0)
    mask = cv2.GaussianBlur(mask, (0, 0), 22)
    Y = 0.2126 * roi[..., 0] + 0.7152 * roi[..., 1] + 0.0722 * roi[..., 2]
    Ys = cv2.GaussianBlur(Y, (0, 0), 3)
    x = Ys / P_LIFT; w = x * x * np.exp(2 * (1 - x))
    lift = np.minimum(A_LIFT * w / np.maximum(Ys, 0.02), 0.6) * mask          # fractional gain
    out = roi * (1 + lift[..., None])
    # keep the blue rim light from getting more saturated as it is lifted
    Yo = (0.2126 * out[..., 0] + 0.7152 * out[..., 1] + 0.0722 * out[..., 2])[..., None]
    out = Yo + (out - Yo) * (1 - 0.35 * np.clip(lift / 0.6, 0, 1))[..., None]
    img[y0:y1, x0:x1] = np.clip(out, 0, 1)
    return img

def make(frame4k, k):
    m = omap[k]; zz = float(z[k]); cx, cy = cen[k]
    cw, ch = SW / zz, SH / zz
    x0 = int(round(cx * SW * (1 - 1 / zz))); y0 = int(round(cy * SH * (1 - 1 / zz)))
    x0 = min(max(x0, 0), SW - int(round(cw))); y0 = min(max(y0, 0), SH - int(round(ch)))
    crop = frame4k[y0:y0 + int(round(ch)), x0:x0 + int(round(cw))]
    g = m['gain']
    if g > 1.0:
        u = UNF[m['show']]
        small = cv2.resize(crop.astype(np.float32), (W, H), interpolation=cv2.INTER_AREA) / 255.0
        small = small * u[:, 0] + u[:, 1]
    else:
        small = cv2.resize(crop, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    small = np.clip(small, 0, 1)
    pts = lm[m['show'], :-1, :] * [SW, SH]
    pts = (pts - [x0, y0]) * (W / cw)
    small = grade(small, pts)
    return np.clip(np.rint(small * 255), 0, 255).astype(np.uint8)

need = [m['show'] for m in omap]
want = set(preview) if preview else None
dec = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf', 'scale=in_color_matrix=bt709:in_range=tv,format=rgb24',
                        '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=SW * SH * 3)
enc = None
if not preview:
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                            '-i', audio, '-map', '0:v', '-map', '1:a',
                            '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '13',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                            '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
cur = -1; frame = None; fb = SW * SH * 3
last_needed = max(need)
for k in range(NOUT):
    tgt = need[k]
    if preview and k > max(want): break
    while cur < tgt:
        buf = dec.stdout.read(fb); cur += 1
        if len(buf) < fb: raise SystemExit(f'decode ended at {cur}')
        if cur == tgt: frame = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
    if preview:
        if k in want: cv2.imwrite(f'{dst}-{k:04d}.png', cv2.cvtColor(make(frame, k), cv2.COLOR_RGB2BGR))
        continue
    enc.stdin.write(make(frame, k).tobytes())
    if k % 100 == 0: print('frame', k, flush=True)
dec.kill()
if enc: enc.stdin.close(); enc.wait()
print('done', NOUT)
