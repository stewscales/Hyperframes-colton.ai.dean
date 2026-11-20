"""Render the reel at the source's own size and frame rate (2160x3840, 30 fps): the cut list and per-frame crop from scene.json,
the caption layer captured by scripts/capture.js on top, the voice cut on exactly the same frames.

  python3 -I scripts/render.py <source.mp4> <caption dir> [--crf N] [--only a-b]

picture: source frames decoded to full-range RGB -> crop + scale back to 2160x3840 (Lanczos; no sharpening, no grade) -> captions
         -> H.264 High, limited-range BT.709, yuv420p, faststart (what Instagram expects)
sound:   the take's own audio, cut on the picture frames (short fades at every join), levelled to about -15 LUFS under a limiter
Output: renders/coaches-look-rich-4k.mp4, plus assets/base.mp4 (a 1080p copy without captions for the Hyperframes composition)."""
import sys, os, json, subprocess, re, numpy as np, cv2
args = sys.argv[1:]; opt = {}
while len(args) >= 2 and args[-2].startswith('--'): opt[args[-2]] = args[-1]; args = args[:-2]
SRC, OV = args[:2]; CRF = opt.get('--crf', '13')
sc = json.load(open('scene.json')); FPS = sc['fps']; W, H = sc['size']; NF = sc['frames']; crop = sc['crop']
omap = json.load(open(OV + '/map.json'))['map']; assert len(omap) == NF
lo, hi = (int(x) for x in opt['--only'].split('-')) if '--only' in opt else (0, NF)
os.makedirs('renders', exist_ok=True); name = 'coaches-look-rich-4k' + (f'-{lo}-{hi}' if '--only' in opt else ''); tmp = f'renders/{name}.video.mp4'; dst = f'renders/{name}.mp4'
def enc(path, w, h, crf, preset):
    return subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p', '-c:v', 'libx264', '-preset', preset, '-crf', crf, '-profile:v', 'high',
                             '-g', '60', '-bf', '2', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-video_track_timescale', '30000', path], stdin=subprocess.PIPE)
main, base = enc(tmp, W, H, CRF, 'slow'), enc('assets/base.v.mp4', W // 2, H // 2, '20', 'medium')
cache = {}
def overlay(idx):
    if idx not in cache:
        cache.clear(); im = cv2.imread(f'{OV}/f{idx:05d}.png', cv2.IMREAD_UNCHANGED); assert im is not None and im.shape == (H, W, 4), idx
        a = im[..., 3]; rows = np.flatnonzero(a.any(1))
        if rows.size == 0: cache[idx] = None
        else:
            cols = np.flatnonzero(a.any(0)); y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
            cache[idx] = (y0, y1, x0, x1, im[y0:y1, x0:x1, 2::-1].astype(np.float32), (im[y0:y1, x0:x1, 3].astype(np.float32) / 255)[..., None])
    return cache[idx]
k = 0; fb = W * H * 3
for s in sc['shots']:
    dec = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(s["a"] - 0.5) / FPS:.6f}', '-i', SRC, '-frames:v', str(s['b'] - s['a']),
                            '-vf', 'scale=in_color_matrix=bt709:in_range=pc:flags=accurate_rnd+full_chroma_int+bicubic,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=fb)
    for f in range(s['a'], s['b']):
        buf = dec.stdout.read(fb); assert len(buf) == fb, f'decode ended at source frame {f}'
        if lo <= k < hi:
            z, x0, y0 = crop[k]                           # output pixel (X, Y) shows source pixel (x0 + (X + 0.5) / z - 0.5, ...)
            M = np.float32([[1 / z, 0, x0 + 0.5 / z - 0.5], [0, 1 / z, y0 + 0.5 / z - 0.5]])
            fr = cv2.warpAffine(np.frombuffer(buf, np.uint8).reshape(H, W, 3), M, (W, H), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
            base.stdin.write(cv2.resize(fr, (W // 2, H // 2), interpolation=cv2.INTER_AREA).tobytes())
            ov = overlay(omap[k])
            if ov is not None:
                a0, a1, b0, b1, rgb, al = ov
                fr[a0:a1, b0:b1] = np.clip(fr[a0:a1, b0:b1] * (1 - al) + rgb * al + 0.5, 0, 255).astype(np.uint8)
            main.stdin.write(fr.tobytes())
        k += 1
    dec.stdout.close(); dec.wait()
main.stdin.close(); base.stdin.close(); assert main.wait() == 0 and base.wait() == 0 and k == NF
# ---- sound ----
SR = 44100; SPF = SR // FPS
X = np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', SRC, '-map', '0:a:0', '-ar', str(SR), '-ac', '2', '-f', 's16le', '-'], stdout=subprocess.PIPE, check=True).stdout, np.int16).reshape(-1, 2).astype(np.float32) / 32768
parts = []
for n, s in enumerate(sc['shots']):
    seg = X[s['a'] * SPF:s['b'] * SPF].copy(); assert len(seg) == (s['b'] - s['a']) * SPF, 'the audio is shorter than the picture'
    fi = int((0.010 if n == 0 else 0.006) * SR); fo = int((0.050 if n == len(sc['shots']) - 1 else 0.006) * SR)
    seg[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]; seg[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]; parts.append(seg)
y = np.concatenate(parts)[lo * SPF:hi * SPF]; y.tofile('renders/cut.f32'); voice = 'assets/voice.wav'
def lufs(p):
    r = subprocess.run(['ffmpeg', '-nostdin', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], stderr=subprocess.PIPE, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])
gain = 4.0
for _ in range(4):
    subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'renders/cut.f32', '-af', f'highpass=f=70,volume={gain:.2f}dB,alimiter=limit=0.84:level=false', '-c:a', 'pcm_s24le', voice])
    L, pk = lufs(voice)
    if abs(L + 15) < 0.3: break
    gain += -15 - L
os.remove('renders/cut.f32'); print(f'voice: gain {gain:+.1f} dB -> {L:.1f} LUFS, peak {pk:.1f} dBFS', flush=True)
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', tmp, '-i', voice, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', dst]); os.remove(tmp)
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'assets/base.v.mp4', '-i', voice, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'assets/base.mp4']); os.remove('assets/base.v.mp4')
print('rendered', hi - lo, 'frames ->', dst, f'{os.path.getsize(dst) / 1048576:.1f} MB', flush=True)
