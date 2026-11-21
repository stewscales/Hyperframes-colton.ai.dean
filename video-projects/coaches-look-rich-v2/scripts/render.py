"""Render the reel: 1440x2560, 30 fps, H.264 High (what Instagram takes best), from the cut list and per-frame crop in
scene.json, with the caption layer from scripts/capture.js on top and the cleaned-up voice underneath.

  python3 -I scripts/render.py <source.mp4> <caption dir> [--crf N] [--still N,N,...]

picture  source frame (full-range BT.709) -> a light prefilter for the downscale -> crop + scale (Lanczos; the crop is always
         wider than 1440 px, so nothing is upscaled) -> grade: black and white points a touch wider and a gentle S-curve
         (no hue or saturation change, so skin and the blue light stay as shot) -> a soft vignette centred on his face, a
         stronger fall-off (and less colour) along the top where the shelf and the figurine are -> a light unsharp mask -> captions -> limited-range BT.709 yuv420p.
sound    the take's own audio: 80 Hz high-pass, gentle noise reduction from a profile of the room's quiet moments (at most
         -7 dB), a small cut at 250 Hz and lift at 3.5 kHz for clarity; no compressor (the take is already even, and one lifted
         the s/t sounds and the room between words); cut on the picture frames (6 ms fades at every join); under the
         held frame the room's own tone carries on and fades out; brought to -14 LUFS with one fixed gain and a peak limiter at -1.5 dB. No music.
--still renders only those output frames to renders/still-<n>.png (for checking the look).
Output: renders/coaches-look-rich-v2.mp4, plus assets/base.mp4 (1080x1920, no captions) for the Hyperframes composition."""
import sys, os, json, subprocess, re, numpy as np, cv2
args = sys.argv[1:]; opt = {}
while len(args) >= 2 and args[-2].startswith('--'): opt[args[-2]] = args[-1]; args = args[:-2]
SRCV, OV = args[:2]; CRF = opt.get('--crf', '14'); STILLS = [int(x) for x in opt['--still'].split(',')] if '--still' in opt else None; AUDIO_ONLY = '--audio-only' in opt
sc = json.load(open('scene.json')); FPS = sc['fps']; SW, SH = sc['src_size']; OW, OH = sc['out_size']; NF = sc['frames']; crop = sc['crop']; SRC = sc['src']
omap = json.load(open(OV + '/map.json'))['map'] if os.path.exists(OV + '/map.json') else None
assert omap is None or len(omap) == NF

# ---- the look (built once) ----
x = np.arange(256) / 255.0; x1 = np.clip((x - 4 / 255) / (250 / 255 - 4 / 255), 0, 1)
K = 0.14; LUT = np.clip(np.round(((1 - K) * x1 + K * x1 * x1 * (3 - 2 * x1)) * 255), 0, 255).astype(np.uint8)        # levels 4-250 + gentle S-curve, same on R, G, B
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
r = np.sqrt(((xx - OW / 2) / (0.80 * OW)) ** 2 + ((yy - sc['eye_y'] * OH) / (0.72 * OH)) ** 2)
sm = lambda u: u * u * (3 - 2 * u)
TOP = 1 - sm(np.clip(yy / (0.20 * OH), 0, 1))           # 1 at the top edge -> 0 a fifth of the way down (above his hair): the shelf and the figurine
VIG = (1 - 0.20 * sm(np.clip((r - 0.45) / 0.65, 0, 1))) * (1 - 0.30 * TOP)          # edges -20%, the top up to -30% more: it reads as the light falling off
VIG = VIG[..., None].astype(np.float32); DESAT = (0.40 * TOP ** 1.5)[..., None].astype(np.float32)   # and the figurine's yellow is muted up there
def look(fr):
    fr = cv2.LUT(fr, LUT).astype(np.float32) * VIG
    g = fr @ np.float32([0.2126, 0.7152, 0.0722]); fr += (g[..., None] - fr) * DESAT
    bl = cv2.GaussianBlur(fr, (0, 0), 1.1)
    return np.clip(fr + 0.30 * (fr - bl) + 0.5, 0, 255).astype(np.uint8)                 # light unsharp mask: detail, no halos
cache = {}
def overlay(idx):
    if idx not in cache:
        cache.clear(); im = cv2.imread(f'{OV}/f{idx:05d}.png', cv2.IMREAD_UNCHANGED); assert im is not None and im.shape == (OH, OW, 4), (idx, None if im is None else im.shape)
        a = im[..., 3]; rows = np.flatnonzero(a.any(1))
        if rows.size == 0: cache[idx] = None
        else:
            cols = np.flatnonzero(a.any(0)); y0, y1, x0, x1_ = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
            cache[idx] = (y0, y1, x0, x1_, im[y0:y1, x0:x1_, 2::-1].astype(np.float32), (im[y0:y1, x0:x1_, 3].astype(np.float32) / 255)[..., None])
    return cache[idx]
def frame_out(src_rgb, k):
    z, x0, y0 = crop[k]; s = (SW / z) / OW; assert s >= 1.0, 'upscaling'
    pre = cv2.GaussianBlur(src_rgb, (0, 0), 0.5 * np.sqrt(s * s - 1)) if s > 1.02 else src_rgb       # prefilter so the downscale does not alias
    M = np.float32([[s, 0, x0 + 0.5 * s - 0.5], [0, s, y0 + 0.5 * s - 0.5]])             # output pixel -> source pixel
    return look(cv2.warpAffine(pre, M, (OW, OH), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE))
def comp(fr, k):
    if omap is not None:
        ov = overlay(omap[k])
        if ov is not None:
            a0, a1, b0, b1, rgb, al = ov
            fr[a0:a1, b0:b1] = np.clip(fr[a0:a1, b0:b1] * (1 - al) + rgb * al + 0.5, 0, 255).astype(np.uint8)
    return fr
def decode(a, n):
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(a - 0.5) / FPS:.6f}', '-i', SRCV, '-frames:v', str(n),
                          '-vf', 'scale=in_color_matrix=bt709:in_range=pc:flags=accurate_rnd+full_chroma_int+bicubic,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=SW * SH * 3)
    for _ in range(n):
        b = p.stdout.read(SW * SH * 3); assert len(b) == SW * SH * 3; yield np.frombuffer(b, np.uint8).reshape(SH, SW, 3)
    p.stdout.close(); p.wait()
os.makedirs('renders', exist_ok=True)
if STILLS:
    for k in STILLS:
        src = next(decode(SRC[k], 1)); cv2.imwrite(f'renders/still-{k}.png', cv2.cvtColor(comp(frame_out(src, k), k), cv2.COLOR_RGB2BGR))
        z, x0, y0 = crop[k]; s = (SW / z) / OW; M = np.float32([[s, 0, x0 + 0.5 * s - 0.5], [0, s, y0 + 0.5 * s - 0.5]])
        raw = cv2.warpAffine(src, M, (OW, OH), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP); cv2.imwrite(f'renders/still-{k}-raw.png', cv2.cvtColor(raw, cv2.COLOR_RGB2BGR))
    print('stills', STILLS); sys.exit(0)
def enc(path, w, h, crf, preset, extra=()):
    return subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
                             '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p', '-c:v', 'libx264', '-preset', preset, '-crf', crf, '-profile:v', 'high',
                             '-g', '60', '-bf', '2', *extra, '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', path], stdin=subprocess.PIPE)
tmp = 'renders/v.mp4'
if AUDIO_ONLY:                                          # keep the rendered picture, redo the sound
    subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'renders/coaches-look-rich-v2.mp4', '-map', '0:v', '-c', 'copy', tmp])
    subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'assets/base.mp4', '-map', '0:v', '-c', 'copy', 'assets/base.v.mp4'])
else: main = enc(tmp, OW, OH, CRF, 'slow', ('-maxrate', '45M', '-bufsize', '90M')); base = enc('assets/base.v.mp4', 1080, 1920, '20', 'medium')
k = 0; last = None
runs = []                                               # decode contiguous stretches of source frames once each
for f in SRC:
    if runs and f == runs[-1][0] + runs[-1][1]: runs[-1][1] += 1
    elif runs and f == runs[-1][0] + runs[-1][1] - 1: runs[-1][2] += 1          # the held frame
    else: runs.append([f, 1, 0])
for a, n, hold in ([] if AUDIO_ONLY else runs):
    for src in decode(a, n):
        fr = frame_out(src, k); base.stdin.write(cv2.resize(fr, (1080, 1920), interpolation=cv2.INTER_AREA).tobytes()); main.stdin.write(comp(fr, k).tobytes()); k += 1; last = src
    for _ in range(hold):
        fr = frame_out(last, k); base.stdin.write(cv2.resize(fr, (1080, 1920), interpolation=cv2.INTER_AREA).tobytes()); main.stdin.write(comp(fr, k).tobytes()); k += 1
if not AUDIO_ONLY: main.stdin.close(); base.stdin.close(); assert main.wait() == 0 and base.wait() == 0 and k == NF, k
# ---- sound ----
SR = 48000; SPF = SR // FPS
def denoise(x, quiet, max_cut_db=7.0, n=2048, hop=512):
    """Gentle spectral noise reduction from a noise profile (the room's own quiet moments): per-bin Wiener-style gain,
    never below -max_cut_db, smoothed over time and frequency so it does not 'warble'. Same gain on both channels."""
    win = np.sqrt(np.hanning(n + 1)[:-1]).astype(np.float32)                    # sqrt-Hann analysis + synthesis: exact overlap-add at hop n/4
    mono = x.mean(1); pad = np.concatenate([np.zeros(n), mono, np.zeros(n)]).astype(np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(pad, n)[::hop] * win; S = np.fft.rfft(frames, axis=1)
    qf = np.lib.stride_tricks.sliding_window_view(quiet.mean(1).astype(np.float32), n)[::hop // 2] * win
    N = (np.abs(np.fft.rfft(qf, axis=1)) ** 2).mean(0)
    P = np.abs(S) ** 2; floor = 10 ** (-max_cut_db / 20)
    G = np.clip(1 - 1.5 * N / np.maximum(P, 1e-12), floor ** 2, 1) ** 0.5
    for t in range(1, len(G)): G[t] = np.maximum(G[t], 0.6 * G[t - 1] + 0.4 * G[t])   # opens at once, closes over ~50 ms
    k = np.ones(5) / 5; G = np.apply_along_axis(lambda g: np.convolve(g, k, mode='same'), 1, G)        # smooth across frequency
    out = np.zeros((len(pad) + n, 2), np.float32); norm = np.zeros(len(pad) + n, np.float32)
    for c in range(2):
        padc = np.concatenate([np.zeros(n), x[:, c], np.zeros(n)]).astype(np.float32)
        Fc = np.fft.rfft(np.lib.stride_tricks.sliding_window_view(padc, n)[::hop] * win, axis=1) * G
        y = np.fft.irfft(Fc, n=n, axis=1) * win
        for i, fr_ in enumerate(y): out[i * hop:i * hop + n, c] += fr_
    for i in range(len(G)): norm[i * hop:i * hop + n] += win ** 2
    out = out[:len(pad)] / np.maximum(norm[:len(pad), None], 1e-6)
    return out[n:n + len(x)]
hp = np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', SRCV, '-map', '0:a:0', '-af', 'highpass=f=80', '-ar', str(SR), '-ac', '2', '-f', 'f32le', '-'], stdout=subprocess.PIPE, check=True).stdout, np.float32).reshape(-1, 2)
QUIET = [(0.00, 0.10), (3.80, 3.90), (5.84, 6.00), (10.44, 10.52), (13.12, 13.20)]       # the room on its own (between words, no breath)
dn = denoise(hp, np.concatenate([hp[int(a * SR):int(b * SR)] for a, b in QUIET])); dn.tofile('renders/dn.f32')
X = np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'renders/dn.f32', '-af', 'equalizer=f=250:t=q:w=1.0:g=-2,equalizer=f=3500:t=q:w=1.0:g=1.5',
                                      '-f', 'f32le', '-'], stdout=subprocess.PIPE, check=True).stdout, np.float32).reshape(-1, 2).copy(); os.remove('renders/dn.f32')
parts = []
for i, s in enumerate(sc['shots']):
    lastshot = i == len(sc['shots']) - 1; b = s['b'] + (4 if lastshot else 0)              # under the held frame: the real room tail (4 frames), then room tone
    seg = X[s['a'] * SPF:b * SPF].copy(); assert len(seg) == (b - s['a']) * SPF
    joined_prev = i > 0 and sc['shots'][i - 1]['b'] == s['a']; joined_next = not lastshot and sc['shots'][i + 1]['a'] == s['b']
    fi = 0 if joined_prev else int((0.010 if i == 0 else 0.006) * SR); fo = 0 if joined_next else int(0.006 * SR)
    if fi: seg[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
    if fo and not lastshot: seg[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    parts.append(seg)
y = np.concatenate(parts); need = NF * SPF - len(y)
# room tone under the held frame: steady noise with the room's own spectrum and level (taken from three quiet moments of the
# processed take), cross-faded in after the real tail and faded out; seeded, so every render is identical
quiet = np.concatenate([X[int(a * SR):int(b * SR)] for a, b in QUIET])
nfft = 1024; win = np.hanning(nfft).astype(np.float32)
psd = np.mean([np.abs(np.fft.rfft(quiet[i:i + nfft] * win[:, None], axis=0)) ** 2 for i in range(0, len(quiet) - nfft, nfft // 4)], axis=0)
L = need + int(0.05 * SR); rng = np.random.default_rng(7); wn = rng.standard_normal((L, 2)).astype(np.float32)
Wf = np.fft.rfft(wn, axis=0); fr = np.fft.rfftfreq(L, 1 / SR); shape = np.stack([np.interp(fr, np.fft.rfftfreq(nfft, 1 / SR), np.sqrt(psd[:, c])) for c in range(2)], 1)
bed = np.fft.irfft(Wf * shape, n=L, axis=0).astype(np.float32); bed *= np.sqrt((quiet ** 2).mean(0) / (bed ** 2).mean(0))
xf = int(0.05 * SR); ramp = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
y[-xf:] = y[-xf:] * (1 - ramp) + bed[:xf] * ramp; y = np.concatenate([y, bed[xf:]])
fo = int(0.30 * SR); y[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]; assert len(y) == NF * SPF
y.tofile('renders/cut.f32'); voice = 'assets/voice.wav'
# level: one fixed gain to -14 LUFS, then a peak limiter (loudnorm's own dynamic mode would act as a second compressor)
def lufs(args):
    r = subprocess.run(['ffmpeg', '-nostdin', *args, '-af', 'ebur128=peak=true', '-f', 'null', '-'], stderr=subprocess.PIPE, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])
raw = ['-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'renders/cut.f32']; g = -14 - lufs(raw)
for _ in range(3):
    subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', *raw, '-af', f'volume={g:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=false', '-ar', str(SR), '-c:a', 'pcm_s24le', voice])
    L_ = lufs(['-i', voice])
    if abs(L_ + 14) < 0.15: break
    g += -14 - L_
print(f'voice: {g:+.1f} dB -> {L_:.1f} LUFS', flush=True)
os.remove('renders/cut.f32')
dst = 'renders/coaches-look-rich-v2.mp4'
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', tmp, '-i', voice, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', str(SR), '-shortest', '-movflags', '+faststart', dst]); os.remove(tmp)
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'assets/base.v.mp4', '-i', voice, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'assets/base.mp4']); os.remove('assets/base.v.mp4')
print('rendered', NF, 'frames ->', dst, f'{os.path.getsize(dst) / 1048576:.1f} MB', flush=True)
