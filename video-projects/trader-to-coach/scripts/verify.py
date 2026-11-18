"""Check a finished render against the source, frame by frame (small scale, streaming).
For every output frame: mean difference from the source frame it came from. Frames with no punch-in and no
graphic must match the source (codec noise only); anything else that differs is reported.
  python3 -I scripts/verify.py <source.mp4> <final.mp4> <overlay_dir>"""
import sys, json, subprocess, numpy as np
src, fin, ovdir = sys.argv[1:4]
edit = json.load(open('assets/edit.json')); omap = json.load(open(ovdir + '/map.json')); S0 = edit['start']; NF = edit['nf']
W, H = 320, 180
def stream(p, ss=None):
    cmd = ['ffmpeg', '-nostdin', '-v', 'error'] + (['-ss', f'{ss:.5f}'] if ss else []) + ['-i', p, '-vf', f'scale={W}:{H}:flags=area,format=gray', '-f', 'rawvideo', '-']
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 64)
a, b = stream(src, S0 / 30 - 0.01), stream(fin)
zoomed = np.zeros(NF, bool)
for z0, z1, zm, rin, rout, *_ in edit['zooms']: zoomed[z0:z1 + rout + 1] = True
# No graphic ever sits in the top-right of the frame (cards are lower-left, bars and the CTA along the bottom),
# so apart from punch-ins and the full-screen title that area must be the source, untouched.
html = open('index.html').read()
import re
t_in = float(re.search(r'tl\.to\("#title", \{ opacity: 1.*?\}, ([\d.]+)\)', html).group(1)); t_out = float(re.search(r'tl\.to\("#title", \{ opacity: 0, duration: ([\d.]+).*?\}, ([\d.]+)\)', html).group(2))
title = np.zeros(NF, bool); title[int(t_in * 30) - 1:int(t_out * 30) + 8] = True
R = (slice(0, 80), slice(176, 320))
d = []; n = 0; prev = None; frozen = []
while True:
    x, y = a.stdout.read(W * H), b.stdout.read(W * H)
    if len(y) < W * H: break
    assert len(x) == W * H, f'source ended early at {n}'
    xs, ys = np.frombuffer(x, np.uint8).reshape(H, W).astype(np.int16), np.frombuffer(y, np.uint8).reshape(H, W).astype(np.int16)
    d.append(float(np.abs(xs[R] - ys[R]).mean()))
    if prev is not None and np.abs(ys - prev).mean() < 0.02: frozen.append(n)
    prev = ys; n += 1
a.kill(); d = np.array(d); f = np.arange(n) + S0
print('output frames', n, '(expected', NF - S0, ')')
clean = ~zoomed[f] & ~title[f]
print('frames outside punch-ins and the title:', int(clean.sum()), '| top-right area vs source: max diff %.2f, mean %.2f' % (d[clean].max(), d[clean].mean()))
print('frames with punch-in:', int(zoomed[f].sum()), '| diff median %.2f' % np.median(d[zoomed[f]]))
odd = [int(k + S0) for k in np.flatnonzero(clean & (d > 1.5))]; print('unexpected differences at source frames:', odd[:30], len(odd))
runs = []
for k in frozen:
    if runs and k == runs[-1][1] + 1: runs[-1][1] = k
    else: runs.append([k, k])
miro = edit['miro']
print('repeated-frame runs longer than 3 frames outside the screen recording and title:', [r for r in runs if r[1] - r[0] >= 3 and not (miro[0] - S0 <= r[0] < miro[1] - S0) and not title[r[0] + S0]][:20])
