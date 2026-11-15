"""Render the talking head: cut to the EDL, punched in per timeline.py, slight shadow lift on the face only
(same grade as the talking-edit project), 1080x1920 from the 4K source. Video only; audio is muxed by mix_audio.sh.
Run from the project folder: python3 -I scripts/render_th.py <src.mov> <facelm.task> <out.mp4> [--preview f1,f2,...]"""
import sys, json, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
exec(open('scripts/timeline.py').read())
src, model, dst = sys.argv[1:4]
preview = [int(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 else None
SW, SH, W_, H_ = 2160, 3840, 1080, 1920
need = [f for a, b in EDL['segs'] for f in range(a, b)]; assert len(need) == NF
z = zoom_schedule()
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
VF = 'scale=in_color_matrix=bt709:in_range=tv,format=rgb24'

# ---- pass 1: face landmarks for every kept frame (1080x1920) ----
lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, num_faces=1))
p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf', f'scale={W_}:{H_}:flags=area:in_color_matrix=bt709:in_range=tv,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
keep = set(need); lm = {}; i = 0; last = None
while True:
    b = p.stdout.read(W_ * H_ * 3)
    if len(b) < W_ * H_ * 3: break
    if i in keep:
        r = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(np.frombuffer(b, np.uint8).reshape(H_, W_, 3))))
        if r.face_landmarks:
            pts = np.array([(l.x, l.y) for l in r.face_landmarks[0]]); last = np.vstack([pts[OVAL], pts[1:2]])
        else: print('no face in source frame', i, '(reusing previous)')
        lm[i] = last
    i += 1
LM = np.array([lm[f] for f in need])                         # NF x 37 x 2
cen = np.zeros((NF, 2), np.float32)
for a, b in centre_parts(): cen[a:b] = np.median(LM[a:b, -1, :], axis=0)
print('landmarks done; nose centres', [(a, np.round(cen[a], 3).tolist()) for a, _ in centre_parts()], flush=True)

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

def make(fr, k):
    zz = float(z[k]); cx, cy = cen[k]; cw, ch = SW / zz, SH / zz
    x0 = int(round(cx * SW * (1 - 1 / zz))); y0 = int(round(cy * SH * (1 - 1 / zz)))
    x0 = min(max(x0, 0), SW - int(round(cw))); y0 = min(max(y0, 0), SH - int(round(ch)))
    small = cv2.resize(fr[y0:y0 + int(round(ch)), x0:x0 + int(round(cw))], (W_, H_), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    pts = (LM[k, :-1, :] * [SW, SH] - [x0, y0]) * (W_ / cw)
    return np.clip(np.rint(grade(small, pts) * 255), 0, 255).astype(np.uint8)

# ---- pass 2: 4K -> crop/zoom -> grade -> encode ----
dec = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf', VF, '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=SW * SH * 3)
enc = None
if not preview:
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W_}x{H_}', '-r', '30', '-i', '-',
                            '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '13',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
cur = -1; fb = SW * SH * 3
for k in range(NF):
    if preview and k > max(preview): break
    while cur < need[k]:
        buf = dec.stdout.read(fb); cur += 1
        if len(buf) < fb: raise SystemExit(f'decode ended at {cur}')
    fr = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
    if preview:
        if k in preview: cv2.imwrite(f'{dst}-{k:04d}.png', cv2.cvtColor(make(fr, k), cv2.COLOR_RGB2BGR))
        continue
    enc.stdin.write(make(fr, k).tobytes())
    if k % 100 == 0: print('frame', k, flush=True)
dec.kill()
if enc: enc.stdin.close(); enc.wait()
print('done', NF)
