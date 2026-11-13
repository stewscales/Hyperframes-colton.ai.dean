"""Render the hook clip (separate recording) as graded, punched-in 1080x1920 PNG frames that render_base.py
prepends to the main edit. The clip is variable frame rate, so it is first conformed to a constant 30 fps.
Usage: python3 render_hook.py <hook.mov> <facelm.task> <align-hook.json> <out_dir> <first_frame> <end_frame>"""
import sys, os, json, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src, model, align_p, out, F0, F1 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
SW, SH, W, H = 2160, 3840, 1080, 1920
N = F1 - F0
align = json.load(open(align_p))
word = lambda w, k=0: int(np.floor([a['start'] for a in align if a['word'] == w][k] * 30 + 1e-6)) - F0
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
base_vf = f"fps=30,trim=start_frame={F0}:end_frame={F1},setpts=PTS-STARTPTS"

# ---- pass 1: face landmarks at 1080x1920 ----
lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, num_faces=1))
p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf', base_vf + f',scale={W}:{H}:flags=area:in_color_matrix=bt709:in_range=tv,format=rgb24',
                      '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
lm = []
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    r = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(np.frombuffer(b, np.uint8).reshape(H, W, 3))))
    assert r.face_landmarks, f'no face in hook frame {len(lm)}'
    pts = np.array([(l.x, l.y) for l in r.face_landmarks[0]]); lm.append(np.vstack([pts[OVAL], pts[1:2]]))
lm = np.array(lm); assert len(lm) == N, (len(lm), N)

# ---- zoom: closer than the main edit's opening so the cut into it reads as a deliberate change of size ----
z = np.linspace(1.04, 1.07, N).astype(np.float32)
o = max(0, word('WRONG') - 1)
for k in range(o, N):                                   # punch on "WRONG", same 4-frame ease as the main edit
    u = min(1.0, (k - o + 1) / 4); e = 1 - (1 - u) ** 3
    z[k] = z[o] + (1.12 - z[o]) * e
cx, cy = np.median(lm[:, -1, :], axis=0)

# ---- grade: identical to render_base.py (slight shadow lift on the face only) ----
A_LIFT, P_LIFT = 0.07, 0.27
def grade(img, pts):
    c = pts.mean(0); pts = c + (pts - c) * 1.06
    x0, y0 = np.floor(pts.min(0) - 90).astype(int); x1, y1 = np.ceil(pts.max(0) + 90).astype(int)
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    roi = img[y0:y1, x0:x1]
    mask = np.zeros(roi.shape[:2], np.float32)
    cv2.fillConvexPoly(mask, cv2.convexHull((pts - [x0, y0]).astype(np.int32)), 1.0)
    mask = cv2.GaussianBlur(mask, (0, 0), 22)
    Y = 0.2126 * roi[..., 0] + 0.7152 * roi[..., 1] + 0.0722 * roi[..., 2]
    Ys = cv2.GaussianBlur(Y, (0, 0), 3)
    x = Ys / P_LIFT; w = x * x * np.exp(2 * (1 - x))
    lift = np.minimum(A_LIFT * w / np.maximum(Ys, 0.02), 0.6) * mask
    o_ = roi * (1 + lift[..., None])
    Yo = (0.2126 * o_[..., 0] + 0.7152 * o_[..., 1] + 0.0722 * o_[..., 2])[..., None]
    o_ = Yo + (o_ - Yo) * (1 - 0.35 * np.clip(lift / 0.6, 0, 1))[..., None]
    img[y0:y1, x0:x1] = np.clip(o_, 0, 1)
    return img

# ---- pass 2: 4K frames -> crop/zoom -> grade -> PNG ----
os.makedirs(out, exist_ok=True)
p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf', base_vf + ',scale=in_color_matrix=bt709:in_range=tv,format=rgb24',
                      '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=SW * SH * 3)
for k in range(N):
    b = p.stdout.read(SW * SH * 3); assert len(b) == SW * SH * 3, f'decode ended at {k}'
    fr = np.frombuffer(b, np.uint8).reshape(SH, SW, 3)
    zz = float(z[k]); cw, ch = SW / zz, SH / zz
    x0 = int(round(cx * SW * (1 - 1 / zz))); y0 = int(round(cy * SH * (1 - 1 / zz)))
    x0 = min(max(x0, 0), SW - int(round(cw))); y0 = min(max(y0, 0), SH - int(round(ch)))
    small = cv2.resize(fr[y0:y0 + int(round(ch)), x0:x0 + int(round(cw))], (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    pts = (lm[k, :-1, :] * [SW, SH] - [x0, y0]) * (W / cw)
    small = grade(small, pts)
    cv2.imwrite(f'{out}/{k:04d}.png', cv2.cvtColor(np.clip(np.rint(small * 255), 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
json.dump({'n': N, 'z': [round(float(v), 4) for v in z], 'wrong': word('WRONG')}, open(out + '/hook.json', 'w'))
print('hook frames', N, 'zoom', z[0], z[-1], 'WRONG at', word('WRONG'))
