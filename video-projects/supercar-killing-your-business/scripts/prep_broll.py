"""Prepare the B-roll as 1080x1920 30 fps clips cut to the exact frame counts in timeline.py:
  day    Lamborghini POV, daytime (section before the dash shows its speed warning)
  watch  watch collection clip (720x1280, full range), opening shot of the watches in hand
  night  Lamborghini POV, night
  wrist  photo: watch on the Lamborghini wheel, slow push-in
Every clip gets the same look (slightly darker, more contrast, a touch cooler, vignette) and a 5-frame settle on
entry. Clips that hand back to the talking head carry FADE extra frames for the dissolve.
Run from the project folder: python3 -I scripts/prep_broll.py <day.mov> <night.mov> <watch.mp4> <wrist.jpg> <out_dir>"""
import sys, subprocess, numpy as np, cv2
exec(open('scripts/timeline.py').read())
day_src, night_src, watch_src, wrist_src, out = sys.argv[1:6]
W_, H_ = 1080, 1920
LEN = {name: b - a + (FADE if name in FADES_OUT else 0) for name, a, b in BROLL}

yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
RAD = np.sqrt(((xx - W_ / 2) / (W_ / 2)) ** 2 + ((yy - H_ / 2) / (H_ / 2)) ** 2) / np.sqrt(2)
def look(img, exp=1.0, con=1.0, sat=1.0, tint=(1, 1, 1), vig=0.3):
    """img float RGB 0..1"""
    img = (img * exp - 0.4) * con + 0.4
    Y = (0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2])[..., None]
    img = (Y + (img - Y) * sat) * np.array(tint, np.float32)
    return np.clip(img * (1 - vig * np.clip(RAD, 0, 1) ** 2.2)[..., None], 0, 1)
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
def frames(src, start, n, w, h, rng='tv', flags='area'):
    raw = subprocess.check_output(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf',
        f'fps=30,trim=start_frame={start}:end_frame={start + n},setpts=PTS-STARTPTS,scale={w}:{h}:flags={flags}:in_color_matrix=bt709:in_range={rng},format=rgb24', '-f', 'rawvideo', '-'])
    a = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3); assert len(a) == n, (src, len(a), n)
    return a
def render(name, n, frame_fn, **lk):
    e = encoder(f'{out}/{name}.mp4')
    for k in range(n): e.stdin.write(u8(look(frame_fn(k).astype(np.float32) / 255, **lk)).tobytes())
    e.stdin.close(); e.wait(); print(name, n, 'frames', flush=True)

fr = frames(day_src, 70, LEN['day'], 2160, 3840)
render('day', LEN['day'], lambda k: crop_zoom(fr[k], settle(k)), exp=0.90, con=1.16, sat=0.90, tint=(0.97, 1.0, 1.05), vig=0.38)

fr = frames(watch_src, 3, LEN['watch'], 1440, 2560, rng='pc', flags='lanczos')
nw = LEN['watch']
render('watch', nw, lambda k: crop_zoom(fr[k], (1.0 + 0.05 * k / (nw - 1)) * settle(k), 0.5, 0.45), exp=0.90, con=1.10, sat=0.95, tint=(0.97, 1.0, 1.04), vig=0.38)

# night: 7% tighter and slightly high so the car UI's small "VIEW" label at the bottom-left edge is cropped out
fr = frames(night_src, 45, LEN['night'], 2160, 3840)
render('night', LEN['night'], lambda k: crop_zoom(fr[k], 1.07 * settle(k), 0.5, 0.46), exp=1.0, con=1.08, sat=1.0, tint=(0.98, 1.0, 1.03), vig=0.28)
del fr

wp = cv2.cvtColor(cv2.imread(wrist_src), cv2.COLOR_BGR2RGB)
h9 = wp.shape[0]; w9 = int(round(h9 * 9 / 16)); x9 = (wp.shape[1] - w9) // 2; wp = wp[:, x9:x9 + w9]     # centre 9:16
nr = LEN['wrist']
render('wrist', nr, lambda k: crop_zoom(wp, (1.04 + 0.10 * (1 - (1 - k / (nr - 1)) ** 2)) * settle(k), 0.47, 0.44), exp=0.94, con=1.08, sat=0.97, tint=(0.98, 1.0, 1.03), vig=0.36)
