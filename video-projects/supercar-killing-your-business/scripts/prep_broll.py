"""Prepare the B-roll as 1080x1920 30 fps clips cut to the exact frame counts in timeline.py:
  day / night / night2  Lamborghini POV driving clips (sections chosen before the dash shows its
                        "120 km/h speed limit exceeded" warning), graded to sit with the dark talking head
  urus                  the Urus photo with a slow push-in
  grid                  3x3 wall of the same flex posts ("every other trading guru online")
Every clip gets the same look (slightly darker, more contrast, a touch cooler, vignette) and a 5-frame settle on entry.
Run from the project folder: python3 -I scripts/prep_broll.py <day.mov> <night.mov> <photo.jpg> <out_dir>"""
import sys, subprocess, numpy as np, cv2
exec(open('scripts/timeline.py').read())
day_src, night_src, photo_src, out = sys.argv[1:5]
W_, H_ = 1080, 1920
LEN = {name: b - a for name, a, b in BROLL}
# first source frame (after conforming to 30 fps) of each driving section
START = {'day': 70, 'night': 45, 'night2': 120}

yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
RAD = np.sqrt(((xx - W_ / 2) / (W_ / 2)) ** 2 + ((yy - H_ / 2) / (H_ / 2)) ** 2) / np.sqrt(2)
def look(img, exp=1.0, con=1.0, sat=1.0, tint=(1, 1, 1), vig=0.3):
    """img float RGB 0..1"""
    img = img * exp
    img = (img - 0.4) * con + 0.4
    Y = (0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2])[..., None]
    img = Y + (img - Y) * sat
    img = img * np.array(tint, np.float32)
    if vig:
        r = cv2.resize(RAD, (img.shape[1], img.shape[0])) if img.shape[:2] != (H_, W_) else RAD
        img = img * (1 - vig * np.clip(r, 0, 1) ** 2.2)[..., None]
    return np.clip(img, 0, 1)
LOOK = {'day': dict(exp=0.90, con=1.16, sat=0.90, tint=(0.97, 1.0, 1.05), vig=0.38),
        'night': dict(exp=1.0, con=1.08, sat=1.0, tint=(0.98, 1.0, 1.03), vig=0.28),
        'urus': dict(exp=0.88, con=1.12, sat=0.95, tint=(0.97, 1.0, 1.04), vig=0.42)}
LOOK['night2'] = LOOK['night']

def encoder(path):
    return subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W_}x{H_}', '-r', '30', '-i', '-',
                             '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-g', '15',
                             '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
def u8(img): return np.clip(np.rint(img * 255), 0, 255).astype(np.uint8)
def crop_zoom(src, z, cx=0.5, cy=0.5):
    """src uint8 HxWx3 (9:16). Crop a 1/z window centred near (cx, cy) and resize to 1080x1920."""
    sh, sw = src.shape[:2]; cw, ch = sw / z, sh / z
    x0 = min(max(cx * sw - cw / 2, 0), sw - cw); y0 = min(max(cy * sh - ch / 2, 0), sh - ch)
    M = np.float32([[W_ / cw, 0, -x0 * W_ / cw], [0, H_ / ch, -y0 * H_ / ch]])
    return cv2.warpAffine(src, M, (W_, H_), flags=cv2.INTER_AREA if cw >= W_ else cv2.INTER_CUBIC)
settle = lambda k: 1 + 0.05 * (1 - min(1.0, k / 5)) ** 3          # 5-frame settle on entry

def frames(src, start, n, w, h):
    raw = subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf',
        f'fps=30,trim=start_frame={start}:end_frame={start + n},setpts=PTS-STARTPTS,scale={w}:{h}:flags=area:in_color_matrix=bt709:in_range=tv,format=rgb24', '-f', 'rawvideo', '-'])
    a = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3); assert len(a) == n, (src, len(a), n)
    return a

# ---- full-screen driving clips ----
for name, src in (('day', day_src), ('night', night_src), ('night2', night_src)):
    n = LEN[name]; fr = frames(src, START[name], n, 2160, 3840); e = encoder(f'{out}/{name}.mp4')
    for k in range(n):
        # night clips: sit 7% tighter and slightly high so the phone UI's small "VIEW" label at the bottom-left edge is cropped out
        zz, cy = (1.07, 0.46) if name.startswith('night') else (1.0, 0.5)
        e.stdin.write(u8(look(crop_zoom(fr[k], zz * settle(k), 0.5, cy).astype(np.float32) / 255, **LOOK[name])).tobytes())
    e.stdin.close(); e.wait(); del fr; print(name, n, 'frames', flush=True)

# ---- Urus photo: slow push-in on the car ----
photo = cv2.cvtColor(cv2.imread(photo_src), cv2.COLOR_BGR2RGB)
n = LEN['urus']; e = encoder(f'{out}/urus.mp4')
for k in range(n):
    u = k / max(1, n - 1); z = 1.10 + 0.10 * (1 - (1 - u) ** 2)
    e.stdin.write(u8(look(crop_zoom(photo, z * settle(k), 0.55, 0.56).astype(np.float32) / 255, **LOOK['urus'])).tobytes())
e.stdin.close(); e.wait(); print('urus', n, 'frames', flush=True)

# ---- 3x3 grid ----
n = LEN['grid']; TW, TH, GAP, MX = 324, 576, 14, 40
MY = (H_ - 3 * TH - 2 * GAP) // 2
SS = 2                                                           # supersample for clean rounded corners
mask = np.zeros((TH * SS, TW * SS), np.float32)
cv2.rectangle(mask, (18 * SS, 0), ((TW - 18) * SS - 1, TH * SS - 1), 1.0, -1); cv2.rectangle(mask, (0, 18 * SS), (TW * SS - 1, (TH - 18) * SS - 1), 1.0, -1)
for cx_, cy_ in ((18, 18), (TW - 18, 18), (18, TH - 18), (TW - 18, TH - 18)): cv2.circle(mask, (cx_ * SS, cy_ * SS), 18 * SS, 1.0, -1)
mask = cv2.resize(mask, (TW, TH), interpolation=cv2.INTER_AREA)
tw, th = 432, 768
dayf = frames(day_src, 0, 170, tw, th); nightf = frames(night_src, 0, 170, tw, th)
ph = cv2.resize(photo, (tw * 2, th * 2), interpolation=cv2.INTER_AREA)
def tile(kind, arg, k):
    if kind == 'day': img = dayf[min(arg + k, 169)]
    elif kind == 'night': img = nightf[min(arg + k, 169)]
    else:
        z, cx, cy = arg; z = z + 0.06 * k / n; cw, ch = ph.shape[1] / z, ph.shape[0] / z
        x0 = min(max(cx * ph.shape[1] - cw / 2, 0), ph.shape[1] - cw); y0 = min(max(cy * ph.shape[0] - ch / 2, 0), ph.shape[0] - ch)
        img = cv2.warpAffine(ph, np.float32([[tw / cw, 0, -x0 * tw / cw], [0, th / ch, -y0 * th / ch]]), (tw, th), flags=cv2.INTER_AREA)
    key = 'urus' if kind == 'urus' else kind
    return look(cv2.resize(img, (TW, TH), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, **{**LOOK[key], 'vig': 0.2})
TILES = [('day', 68), ('night', 40), ('urus', (1.25, 0.55, 0.58)),
         ('urus', (1.6, 0.6, 0.55)), ('day', 15), ('night', 95),
         ('night', 10), ('urus', (1.05, 0.5, 0.5)), ('day', 105)]
BG = np.array([10, 10, 10], np.float32) / 255
e = encoder(f'{out}/grid.mp4')
for k in range(n):
    canvas = np.empty((H_, W_, 3), np.float32); canvas[:] = BG
    for i, (kind, arg) in enumerate(TILES):
        r, c = divmod(i, 3); x = MX + c * (TW + GAP); y = MY + r * (TH + GAP)
        u = np.clip((k + 4 - i) / 5, 0, 1)                       # one tile per frame, each pops over 5 frames; the first is already up on frame 0 (no black frame)
        if u <= 0: continue
        ez = 1 - (1 - u) ** 3; s = 0.82 + 0.18 * ez
        t = tile(kind, arg, k) * 0.86                            # a little dimmer so the caption reads on top
        if s < 0.999:
            w2, h2 = max(2, int(round(TW * s))), max(2, int(round(TH * s)))
            t2 = cv2.resize(t, (w2, h2), interpolation=cv2.INTER_AREA); m2 = cv2.resize(mask, (w2, h2), interpolation=cv2.INTER_AREA) * ez
            xo, yo = x + (TW - w2) // 2, y + (TH - h2) // 2
        else:
            t2, m2, xo, yo = t, mask, x, y
        roi = canvas[yo:yo + t2.shape[0], xo:xo + t2.shape[1]]
        roi[:] = roi * (1 - m2[..., None]) + t2 * m2[..., None]
    zg = 1.0 + 0.045 * k / max(1, n - 1)                         # slow push on the whole wall
    M = cv2.getRotationMatrix2D((W_ / 2, H_ / 2), 0, zg)
    e.stdin.write(u8(cv2.warpAffine(canvas, M, (W_, H_), flags=cv2.INTER_LINEAR, borderValue=tuple(float(v) for v in BG))).tobytes())
e.stdin.close(); e.wait(); print('grid', n, 'frames')
