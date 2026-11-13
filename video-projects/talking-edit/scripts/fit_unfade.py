"""Measure how to undo the fade-to-black dips that are baked into the source.
The fades are a plain multiply, so each faded frame gets one gain per channel (median ratio against the
nearest clean frame of the same take, measured on mid/bright pixels only). Dark areas lose too much
precision under the fade to be scaled back up cleanly, so render_base.py takes those from the clean
reference frame instead (the camera is locked off and the background is static).
Usage: python3 fit_unfade.py <workdir> <src.mov>   -> writes ungain.npy (N,3) and unref.npy (N,)"""
import numpy as np, subprocess, sys
S, src = sys.argv[1], sys.argv[2]
fade = np.load(S + '/fade.npy'); N = len(fade)
B = [176, 294, 406, 498, 640, 788, 907]            # first frame of each new take
frames = sorted({k for b in B for k in range(b - 10, b + 11)})
sel = '+'.join(f'eq(n\\,{k})' for k in frames)
W, H = 540, 960
raw = subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf',
    f"select='{sel}',scale={W}:{H}:flags=area:in_color_matrix=bt709:in_range=tv,format=rgb24", '-vsync', '0', '-f', 'rawvideo', '-'])
F = dict(zip(frames, np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32) / 255))
gain = np.ones((N, 3), np.float32); ref = np.full(N, -1, np.int32)
for b in B:
    for k in range(b - 8, b + 9):
        f = fade[k]
        if f >= 0.985 or f < 0.20: continue
        r = k; step = -1 if k < b else 1
        while fade[r] < 0.985: r += step
        x, y = F[k], F[r]
        for c in range(3):
            xc, yc = x[..., c].ravel(), y[..., c].ravel()
            m = (yc > 0.25) & (yc < 0.85) & (xc > 0.02)
            gain[k, c] = np.median(yc[m] / xc[m])
        ref[k] = r
        print(k, 'ref', r, 'fade', round(float(f), 3), 'gain', np.round(gain[k], 3))
np.save(S + '/ungain.npy', gain); np.save(S + '/unref.npy', ref)
