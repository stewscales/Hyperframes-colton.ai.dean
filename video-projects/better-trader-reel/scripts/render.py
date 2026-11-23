"""Render the reel at 1080x1920 / 30 fps (H.264 High, faststart) from scene.json: talking head (cut list + punch-ins), the two
B-roll inserts, the caption layer from scripts/capture.js, and the cleaned-up voice with a very quiet music bed.

  python3 -I scripts/render.py <talking head.mp4> <sales photo.jpg> <filming clip.mov> <caption dir> [--music-db N] [--no-music]

picture  talking head: full-range BT.709 -> punch-ins (Lanczos, 108%, about his chin) -> a light grade (levels 3-253 and a
         gentle S-curve, same on R, G, B, so skin stays as shot) -> captions.
         sales photo: covers the frame, slow 6% push towards the screens and his hands (no grade: it is already graded).
         filming clip: autorotated, downscaled 2160x3840 -> 1080x1920, the same light grade.
sound    his voice only from the talking head (the B-roll clip's own sound is not used): 80 Hz high-pass, gentle noise
         reduction from a profile of the room between words (at most -7 dB), a small cut at 250 Hz and lift at 3.5 kHz;
         cut on the picture frames with 6 ms fades. Music bed (assets/sfx library) --music-db below the voice (default 23 dB),
         faded in and out. Voice at -14 LUFS, peaks limited to -1.5 dB.
Output: renders/better-trader.mp4 (+ assets/base.mp4 without captions, for the Hyperframes composition)."""
import sys, os, json, subprocess, re, numpy as np, cv2
args = sys.argv[1:]; opt = {}
flags = [a for a in args if a == '--no-music']; args = [a for a in args if a != '--no-music']
while len(args) >= 2 and args[-2].startswith('--'): opt[args[-2]] = args[-1]; args = args[:-2]
TH, PHOTO, CLIP, OV = args[:4]; MUSIC_DB = float(opt.get('--music-db', 23)); NO_MUSIC = bool(flags)
sc = json.load(open('scene.json')); FPS = sc['fps']; CW, CH = sc['out_size']; NF = sc['frames']; SRC = sc['src']; ZOOM = sc['zoom']; ANCH = sc['anchor']
omap = json.load(open(OV + '/map.json'))['map']; assert len(omap) == NF
x = np.arange(256) / 255.0; x1 = np.clip((x - 3 / 255) / (253 / 255 - 3 / 255), 0, 1); K = 0.08
LUT = np.clip(np.round(((1 - K) * x1 + K * x1 * x1 * (3 - 2 * x1)) * 255), 0, 255).astype(np.uint8)
grade = lambda fr: cv2.LUT(fr, LUT)
def decode(path, vf, w, h, extra=()):
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', *extra, '-i', path, '-vf', vf + ',format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=w * h * 3)
    while True:
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3: break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.stdout.close(); p.wait()
# ---- talking head: every source frame we need, in order ----
assert all(a <= b for a, b in zip(SRC, SRC[1:]))          # cuts only remove time, so the source can be streamed (holding it all would not fit in memory)
_th = enumerate(decode(TH, 'scale=in_color_matrix=bt709:in_range=pc:flags=accurate_rnd+full_chroma_int+bicubic', CW, CH)); _cur = [-1, None]
def th_frame(n):
    while _cur[0] < n: _cur[0], _cur[1] = next(_th)
    assert _cur[0] == n; return _cur[1]
def talking(o):
    fr = th_frame(SRC[o]); z = ZOOM[o]
    if z > 1.0001:
        ax, ay = ANCH[o]; s = 1 / z
        M = np.float32([[s, 0, ax * (1 - s) + 0.5 * s - 0.5], [0, s, ay * (1 - s) + 0.5 * s - 0.5]])
        fr = cv2.warpAffine(fr, M, (CW, CH), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    return grade(fr)
# ---- B-roll ----
photo = cv2.cvtColor(cv2.imread(PHOTO), cv2.COLOR_BGR2RGB); PH, PW = photo.shape[:2]; s0 = max(CW / PW, CH / PH)
def still(k, n):
    u = k / max(1, n - 1); z = 1.0 + 0.06 * u; cx = PW / 2 + 40 * u; cy = PH / 2 + 50 * u          # push gently towards the screens / hands
    s = 1 / (s0 * z); M = np.float32([[s, 0, cx - CW / 2 * s + 0.5 * s - 0.5], [0, s, cy - CH / 2 * s + 0.5 * s - 0.5]])
    src = cv2.GaussianBlur(photo, (0, 0), 0.4) if s > 1.02 else photo
    return cv2.warpAffine(src, M, (CW, CH), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
clip = list(decode(CLIP, 'scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv', CW, CH))
NCLIP = next(r['n'] for r in sc['broll'] if r['kind'] == 'clip'); assert len(clip) >= NCLIP, (len(clip), NCLIP); COFF = min(2, len(clip) - NCLIP)   # skip up to 2 frames of camera start
inb = {}
for r in sc['broll']:
    for k in range(r['n']): inb[r['a'] + k] = (r, k)
cache = {}
def overlay(idx):
    if idx not in cache:
        cache.clear(); im = cv2.imread(f'{OV}/f{idx:05d}.png', cv2.IMREAD_UNCHANGED); assert im is not None and im.shape == (CH, CW, 4)
        a = im[..., 3]; rows = np.flatnonzero(a.any(1))
        if rows.size == 0: cache[idx] = None
        else:
            cols = np.flatnonzero(a.any(0)); y0, y1, x0, x1_ = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
            cache[idx] = (y0, y1, x0, x1_, im[y0:y1, x0:x1_, 2::-1].astype(np.float32), (im[y0:y1, x0:x1_, 3].astype(np.float32) / 255)[..., None])
    return cache[idx]
def enc(path, crf, preset):
    return subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{CW}x{CH}', '-r', str(FPS), '-i', '-',
                             '-vf', 'scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p', '-c:v', 'libx264', '-preset', preset, '-crf', crf, '-profile:v', 'high',
                             '-g', '60', '-bf', '2', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', path], stdin=subprocess.PIPE)
os.makedirs('renders', exist_ok=True); tmp = 'renders/v.mp4'; main = enc(tmp, '15', 'slow'); base = enc('assets/base.v.mp4', '20', 'medium')
for o in range(NF):
    if o in inb:
        th_frame(SRC[o]); r, k = inb[o]; fr = still(k, r['n']) if r['kind'] == 'still' else grade(clip[COFF + k])
    else: fr = talking(o)
    base.stdin.write(fr.tobytes())
    ov = overlay(omap[o])
    if ov is not None:
        a0, a1, b0, b1, rgb, al = ov; fr = fr.copy(); fr[a0:a1, b0:b1] = np.clip(fr[a0:a1, b0:b1] * (1 - al) + rgb * al + 0.5, 0, 255).astype(np.uint8)
    main.stdin.write(fr.tobytes())
main.stdin.close(); base.stdin.close(); assert main.wait() == 0 and base.wait() == 0
# ---- sound ----
SR = 48000; SPF = SR // FPS
v2 = open('../coaches-look-rich-v2/scripts/render.py').read(); exec(v2[v2.index('def denoise('):v2.index('hp = np.frombuffer(')])        # the same gentle noise reduction as the last reel
hp = np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', TH, '-map', '0:a:0', '-af', 'highpass=f=80', '-ar', str(SR), '-ac', '2', '-f', 'f32le', '-'], stdout=subprocess.PIPE, check=True).stdout, np.float32).reshape(-1, 2)
W = json.load(open('assets/words.json'))
quiet = [(a['end'] + 0.08, b['start'] - 0.06) for a, b in zip(W, W[1:]) if b['start'] - a['end'] > 0.35]
dn = denoise(hp, np.concatenate([hp[int(a * SR):int(b * SR)] for a, b in quiet])); dn.tofile('renders/dn.f32')
X = np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'renders/dn.f32', '-af', 'equalizer=f=250:t=q:w=1.0:g=-2,equalizer=f=3500:t=q:w=1.0:g=1.5',
                                  '-f', 'f32le', '-'], stdout=subprocess.PIPE, check=True).stdout, np.float32).reshape(-1, 2).copy(); os.remove('renders/dn.f32')
parts = []
for i, s in enumerate(sc['shots']):
    seg = X[s['a'] * SPF:s['b'] * SPF].copy(); assert len(seg) == (s['b'] - s['a']) * SPF
    jp = i > 0 and sc['shots'][i - 1]['b'] == s['a']; jn = i + 1 < len(sc['shots']) and sc['shots'][i + 1]['a'] == s['b']
    fi = 0 if jp else int((0.010 if i == 0 else 0.006) * SR); fo = 0 if jn else int((0.08 if i == len(sc['shots']) - 1 else 0.006) * SR)
    if fi: seg[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
    if fo: seg[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    parts.append(seg)
y = np.concatenate(parts); assert len(y) == NF * SPF; y.tofile('renders/voice.f32')
def lufs(a):
    r = subprocess.run(['ffmpeg', '-nostdin', *a, '-af', 'ebur128=peak=true', '-f', 'null', '-'], stderr=subprocess.PIPE, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])
raw = ['-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'renders/voice.f32']; gv = -14 - lufs(raw)
DUR = NF / FPS; mix = 'renders/mix.wav'
if NO_MUSIC:
    fc = f'[0:a]volume={gv:.2f}dB,alimiter=limit=0.84:attack=3:release=60:level=false[o]'; ins = raw
else:
    M = '../../assets/music/music-bed-cinematic-tech.mp3'; OFF = 22.0                                   # a steady stretch of the bed (no swells or drops)
    gm = -14 - MUSIC_DB - lufs(['-ss', str(OFF), '-t', f'{DUR:.3f}', '-i', M])
    fc = (f'[0:a]volume={gv:.2f}dB[v];[1:a]atrim=0:{DUR:.3f},asetpts=PTS-STARTPTS,aresample={SR},aformat=channel_layouts=stereo,volume={gm:.2f}dB,'
          f'afade=t=in:st=0:d=0.8,afade=t=out:st={DUR - 1.4:.3f}:d=1.4[m];[v][m]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.84:attack=3:release=60:level=false[o]')
    ins = raw + ['-ss', str(OFF), '-i', M]
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[o]', '-ar', str(SR), '-c:a', 'pcm_s24le', mix])
print(f'voice {gv:+.1f} dB; music {"off" if NO_MUSIC else f"{MUSIC_DB:.0f} dB under the voice"}; mix {lufs(["-i", mix]):.1f} LUFS', flush=True)
dst = 'renders/better-trader' + ('-no-music' if NO_MUSIC else '') + '.mp4'
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', tmp, '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-shortest', '-movflags', '+faststart', dst])
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'assets/base.v.mp4', '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'assets/base.mp4'])
for f_ in (tmp, 'assets/base.v.mp4', 'renders/voice.f32'): os.remove(f_)
print('rendered', NF, 'frames ->', dst, f'{os.path.getsize(dst) / 1048576:.1f} MB', flush=True)
