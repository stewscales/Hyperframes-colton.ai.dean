"""Render the talking head (video only): cut to the EDL, baked-in fade removed, punch-ins per timeline.py,
slight shadow lift on the face only (same grade as the other reels). Source and output are both 1080x1920.
Run from the project folder: python3 -I scripts/render_th.py <facelm.task> <out.mp4> [--preview f1,f2,...]"""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
exec(open('scripts/timeline.py').read())
model, dst = sys.argv[1:3]
preview = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
W_, H_ = 1080, 1920; FB = W_ * H_ * 3
GAIN = np.load('assets/ungain.npy'); z = zoom_schedule()
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
def reader():
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', 'assets/raw.mov', '-vf', 'scale=in_color_matrix=bt709:in_range=tv,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=FB)
    cur = -1; img = None
    for k in range(NF):
        while cur < SHOW[k]:
            buf = p.stdout.read(FB); cur += 1; assert len(buf) == FB, f'decode ended at {cur}'
            if cur == SHOW[k]:
                img = np.frombuffer(buf, np.uint8).reshape(H_, W_, 3).astype(np.float32) / 255
                if not np.allclose(GAIN[cur], 1): img = np.clip(img * GAIN[cur], 0, 1)        # undo the baked-in fade
        yield k, img
    p.kill()
# ---- pass 1: face landmarks ----
lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, num_faces=1))
LM = []; cache = {}
for k, img in reader():
    s = SHOW[k]
    if s not in cache:
        r = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(np.rint(img * 255).astype(np.uint8))))
        if r.face_landmarks:
            pts = np.array([(l.x * W_, l.y * H_) for l in r.face_landmarks[0]]); cache[s] = np.vstack([pts[OVAL], pts[1:2]])
        else:
            print('no face at output frame', k, '(reusing previous)'); cache[s] = LM[-1]
    LM.append(cache[s])
LM = np.array(LM); cen = np.zeros((NF, 2), np.float32)
for a, b in centre_parts(): cen[a:b] = np.median(LM[a:b, -1, :], axis=0)
print('landmarks done; centres', [(a, np.round(cen[a]).tolist()) for a, _ in centre_parts()], flush=True)

A_LIFT, P_LIFT = 0.07, 0.27
def grade(img, pts):
    c = pts.mean(0); pts = c + (pts - c) * 1.06
    x0, y0 = np.floor(pts.min(0) - 90).astype(int); x1, y1 = np.ceil(pts.max(0) + 90).astype(int)
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W_), min(y1, H_)
    roi = img[y0:y1, x0:x1]
    mask = np.zeros(roi.shape[:2], np.float32)
    cv2.fillConvexPoly(mask, cv2.convexHull((pts - [x0, y0]).astype(np.int32)), 1.0)
    mask = cv2.GaussianBlur(mask, (0, 0), 22)
    Y = 0.2126 * roi[..., 0] + 0.7152 * roi[..., 1] + 0.0722 * roi[..., 2]
    Ys = cv2.GaussianBlur(Y, (0, 0), 3)
    x = Ys / P_LIFT; w = x * x * np.exp(2 * (1 - x))
    lift = np.minimum(A_LIFT * w / np.maximum(Ys, 0.02), 0.6) * mask
    o = roi * (1 + lift[..., None])
    Yo = (0.2126 * o[..., 0] + 0.7152 * o[..., 1] + 0.0722 * o[..., 2])[..., None]
    o = Yo + (o - Yo) * (1 - 0.35 * np.clip(lift / 0.6, 0, 1))[..., None]
    img[y0:y1, x0:x1] = np.clip(o, 0, 1)
    return img
def make(img, k):
    zz = float(z[k]); cx, cy = cen[k]; cw, ch = W_ / zz, H_ / zz
    x0 = min(max(cx * (1 - 1 / zz), 0), W_ - cw); y0 = min(max(cy * (1 - 1 / zz), 0), H_ - ch)      # keeps the nose where it is
    if zz > 1.0005:
        M = np.float32([[zz, 0, -x0 * zz], [0, zz, -y0 * zz]])
        out = np.clip(cv2.warpAffine(img, M, (W_, H_), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE), 0, 1)
    else: out = img.copy(); x0 = y0 = 0.0; zz = 1.0
    return np.clip(np.rint(grade(out, (LM[k, :-1, :] - [x0, y0]) * zz) * 255), 0, 255).astype(np.uint8)
enc = None
if not preview:
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W_}x{H_}', '-r', '30', '-i', '-',
                            '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '13',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
for k, img in reader():
    if preview:
        if k in preview: cv2.imwrite(f'{dst}-{k:04d}.png', cv2.cvtColor(make(img, k), cv2.COLOR_RGB2BGR))
        continue
    enc.stdin.write(make(img, k).tobytes())
if enc: enc.stdin.close(); enc.wait()
print('done', NF)
