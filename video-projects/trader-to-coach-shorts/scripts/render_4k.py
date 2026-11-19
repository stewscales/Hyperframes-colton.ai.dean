"""Render one short at the source's own size (3840x2160, full frame, no crop or zoom): the cut list from
scripts/shorts.py, the caption layer captured by scripts/capture.js composited on top, voice from cut_audio.py.
Works in YUV 4:2:0 throughout (no RGB round trip), so the picture outside the captions is the source's, re-encoded once.

  python3 -I scripts/render_4k.py <source.mp4> <overlay_root> <clip id> [...] [--crf N] [--preset P]

<overlay_root>/ov-<id>/ comes from scripts/capture.js. Output: renders/<id>.mp4 and clips/<id>/edl.json."""
import sys, os, json, subprocess, collections, numpy as np, cv2
exec(open('scripts/shorts.py').read().split("if __name__ == '__main__':")[0])
args = sys.argv[1:]; opt = {}
while len(args) >= 2 and args[-2].startswith('--'): opt[args[-2]] = args[-1]; args = args[:-2]
SRC, OVROOT, ids = args[0], args[1], args[2:]
CRF = opt.get('--crf', '18'); PRESET = opt.get('--preset', 'fast')
W, H = 3840, 2160; CW, CH = W // 2, H // 2; ysz, csz = W * H, CW * CH

class Overlay:
    """One captured caption frame (a band of the 4K frame), as limited-range BT.709 YUV with alpha, cropped to what is visible."""
    def __init__(self, path, band):
        im = cv2.imread(path, cv2.IMREAD_UNCHANGED); assert im is not None and im.shape[:2] == (band[1] - band[0], W) and im.shape[2] == 4, path
        a = im[..., 3]; rows = np.flatnonzero(a.any(1)); self.empty = rows.size == 0
        if self.empty: return
        cols = np.flatnonzero(a.any(0))
        y0, y1 = rows[0] & ~1, (rows[-1] + 2) & ~1; x0, x1 = cols[0] & ~1, (cols[-1] + 2) & ~1
        assert y0 > 0 and y1 < im.shape[0], 'caption touches the edge of the captured band'
        c = im[y0:y1, x0:x1].astype(np.float32); al = c[..., 3] / 255.0
        self.box = (band[0] + y0, band[0] + y1, x0, x1)
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

for cid in ids:
    E = build(cid); P, NF = E['pieces'], E['NF']; ovdir = f'{OVROOT}/ov-{cid}'
    meta = json.load(open(ovdir + '/map.json')); omap, band = meta['map'], meta['band']; assert len(omap) == NF, (len(omap), NF)
    os.makedirs('renders', exist_ok=True); tmp = f'renders/{cid}.video.mp4'; dst = f'renders/{cid}.mp4'
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', PRESET, '-crf', CRF, '-maxrate', '45M', '-bufsize', '90M', '-g', '60', '-x264-params', 'open-gop=0',
                            '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', tmp], stdin=subprocess.PIPE)
    cache = collections.OrderedDict(); k = 0
    for a, b in P:
        dec = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(a - 0.5) / FPS:.6f}', '-i', SRC, '-frames:v', str(b - a),
                                '-pix_fmt', 'yuv420p', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=ysz + 2 * csz)
        for f in range(a, b):
            buf = bytearray(dec.stdout.read(ysz + 2 * csz)); assert len(buf) == ysz + 2 * csz, f'decode ended at source frame {f}'
            Y = np.frombuffer(buf, np.uint8, ysz).reshape(H, W); U = np.frombuffer(buf, np.uint8, csz, ysz).reshape(CH, CW); V = np.frombuffer(buf, np.uint8, csz, ysz + csz).reshape(CH, CW)
            idx = omap[k]
            if idx >= 0:
                if idx not in cache:
                    cache[idx] = Overlay(f'{ovdir}/f{idx:05d}.png', band)
                    if len(cache) > 3: cache.popitem(last=False)
                cache[idx].apply(Y, U, V)
            enc.stdin.write(buf); k += 1
        dec.stdout.close(); dec.wait()
    enc.stdin.close(); assert enc.wait() == 0 and k == NF
    subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', tmp, '-i', f'clips/{cid}/assets/voice.wav', '-map', '0:v', '-map', '1:a',
                           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', dst]); os.remove(tmp)
    json.dump(dict(clip=cid, frames=NF, fps=FPS, size=[W, H], pieces=P, snippet_of_piece=E['snip_of'], out_start=E['starts'][:-1]), open(f'clips/{cid}/edl.json', 'w'))
    print(cid, 'rendered', NF, 'frames ->', dst, f'{os.path.getsize(dst) / 1048576:.1f} MB', flush=True)
