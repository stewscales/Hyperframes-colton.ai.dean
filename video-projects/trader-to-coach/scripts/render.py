"""Composite one stretch of the final 4K video: source frames -> punch-ins -> graphics layer -> H.264.
Works in YUV 4:2:0 throughout (no RGB round trip), so untouched picture areas stay exactly as in the source.

  python3 -I scripts/render.py <source.mp4> <overlay_dir> <first_frame> <end_frame> <out.mp4> [--crf N] [--preset P]

overlay_dir comes from scripts/capture.js (transparent 3840x2160 PNGs + map.json).
Punch-ins come from assets/edit.json: (start, end, zoom, ramp_in, ramp_out) in frames, scaled about the face."""
import sys, json, subprocess, collections, numpy as np, cv2
src, ovdir, f0, f1, dst = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
opt = dict(zip(sys.argv[6::2], sys.argv[7::2])); CRF = opt.get('--crf', '19'); PRESET = opt.get('--preset', 'medium')
W, H = 3840, 2160; CW, CH = W // 2, H // 2
edit = json.load(open('assets/edit.json')); omap = json.load(open(ovdir + '/map.json'))

def zoom_at(f):
    for a, b, zm, rin, rout, ax, ay in edit['zooms']:
        if a <= f < a + rin:
            u = (f - a + 1) / rin; return 1 + (zm - 1) * (1 - (1 - u) ** 3), ax, ay
        if a + rin <= f <= b: return zm, ax, ay
        if b < f <= b + rout:
            u = (f - b) / rout; return zm - (zm - 1) * (u * u * (3 - 2 * u)), ax, ay
    return 1.0, 0.5, 0.5

class Overlay:
    """One captured graphics frame, pre-converted to limited-range BT.709 YUV with alpha, cropped to what is visible."""
    def __init__(self, idx):
        im = cv2.imread(f'{ovdir}/f{idx:05d}.png', cv2.IMREAD_UNCHANGED); assert im is not None and im.shape[:2] == (H, W), idx
        if im.shape[2] == 3: im = np.dstack([im, np.full((H, W), 255, np.uint8)])       # a fully opaque frame is saved without alpha
        a = im[..., 3]; rows = np.flatnonzero(a.any(1)); self.empty = rows.size == 0
        if self.empty: return
        cols = np.flatnonzero(a.any(0))
        y0, y1 = rows[0] & ~1, (rows[-1] + 2) & ~1; x0, x1 = cols[0] & ~1, (cols[-1] + 2) & ~1
        self.box = (y0, y1, x0, x1)
        c = im[y0:y1, x0:x1].astype(np.float32); al = c[..., 3] / 255.0
        b, g, r = c[..., 0] / 255.0, c[..., 1] / 255.0, c[..., 2] / 255.0
        yl = 0.2126 * r + 0.7152 * g + 0.0722 * b
        self.ya = (16 + 219 * yl) * al; self.inv = 1 - al
        cb = 128 + 224 * (b - yl) / 1.8556; cr = 128 + 224 * (r - yl) / 1.5748
        m2 = lambda p: p.reshape(p.shape[0] // 2, 2, p.shape[1] // 2, 2).mean((1, 3))
        self.ua, self.va, self.cinv = m2(cb * al), m2(cr * al), 1 - m2(al)
    def apply(self, Y, U, V):
        if self.empty: return
        y0, y1, x0, x1 = self.box
        Y[y0:y1, x0:x1] = np.clip(Y[y0:y1, x0:x1] * self.inv + self.ya + 0.5, 0, 255).astype(np.uint8)
        s = (slice(y0 // 2, y1 // 2), slice(x0 // 2, x1 // 2))
        U[s] = np.clip(U[s] * self.cinv + self.ua + 0.5, 0, 255).astype(np.uint8)
        V[s] = np.clip(V[s] * self.cinv + self.va + 0.5, 0, 255).astype(np.uint8)
cache = collections.OrderedDict()
def overlay(idx):
    if idx not in cache:
        cache[idx] = Overlay(idx)
        if len(cache) > 3: cache.popitem(last=False)
    return cache[idx]

n = f1 - f0
dec = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{max(0, f0 / 30 - 0.01):.5f}', '-i', src, '-frames:v', str(n),
                        '-pix_fmt', 'yuv420p', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=W * H * 3 // 2)
enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                        '-c:v', 'libx264', '-preset', PRESET, '-crf', CRF, '-maxrate', '40M', '-bufsize', '80M', '-g', '60', '-x264-params', 'open-gop=0',
                        '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', dst], stdin=subprocess.PIPE)
ysz, csz = W * H, CW * CH
for f in range(f0, f1):
    buf = dec.stdout.read(ysz + 2 * csz); assert len(buf) == ysz + 2 * csz, f'decode ended at frame {f}'
    Y = np.frombuffer(buf, np.uint8, ysz).reshape(H, W); U = np.frombuffer(buf, np.uint8, csz, ysz).reshape(CH, CW); V = np.frombuffer(buf, np.uint8, csz, ysz + csz).reshape(CH, CW)
    z, ax, ay = zoom_at(f)
    if z > 1.0005:
        M = np.float32([[z, 0, (1 - z) * ax * W], [0, z, (1 - z) * ay * H]]); Mc = np.float32([[z, 0, (1 - z) * ax * CW], [0, z, (1 - z) * ay * CH]])
        Y = cv2.warpAffine(Y, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        U = cv2.warpAffine(U, Mc, (CW, CH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        V = cv2.warpAffine(V, Mc, (CW, CH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    idx = omap[f]
    if idx >= 0:
        ov = overlay(idx)
        if not ov.empty:
            if not Y.flags.writeable: Y, U, V = Y.copy(), U.copy(), V.copy()
            ov.apply(Y, U, V)
    enc.stdin.write(Y.tobytes()); enc.stdin.write(U.tobytes()); enc.stdin.write(V.tobytes())
    if (f - f0) % 300 == 0: print('frame', f, flush=True)
dec.kill(); enc.stdin.close(); enc.wait()
print('done', f0, f1)
