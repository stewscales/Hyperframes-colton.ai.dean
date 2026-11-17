"""Render the talking head (video only) from the two 4K takes: cut to the EDL, framed as in v1 (BASE crop per
take), punch-ins per timeline.py, slight shadow lift on the face only. Output 1080x1920, always downscaled from 4K.
Run from the project folder: python3 -I scripts/render_th.py <clipA.mov> <clipB.mov> <facelm.task> <out.mp4>"""
import sys, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
exec(open('scripts/timeline.py').read())
SRC = {'A': sys.argv[1], 'B': sys.argv[2]}; model, dst = sys.argv[3:5]
preview = None
W_, H_ = 1080, 1920; SW, SH = 2160, 3840; FB = SW * SH * 3
z = zoom_schedule()
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
def reader():
    """Yields (output frame index, 4K frame uint8 RGB) in order."""
    k = 0
    for clip, a, b in SEGS:
        p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', SRC[clip], '-vf',
                              f'trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,scale=in_color_matrix=bt709:in_range=tv,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, bufsize=FB)
        for _ in range(a, b):
            buf = p.stdout.read(FB); assert len(buf) == FB, f'decode ended at output frame {k}'
            fr = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
            yield k, fr; k += 1
        p.kill()
    for _ in range(END_HOLD):                                   # hold the last frame (see edl.py)
        yield k, fr; k += 1
    assert k == NF
def view(fr, k, zz, x0, y0):
    """The 1080x1920 picture for v1-frame window (x0, y0, 1080/zz, 1920/zz), cut from the 4K frame and downscaled."""
    s_, tx, ty = BASE[SHOW[k][0]]
    X0 = 2 * (x0 - tx) / s_; Y0 = 2 * (y0 - ty) / s_; Wc = 2 * (W_ / zz) / s_; Hc = 2 * (H_ / zz) / s_
    xi, yi, wi, hi = int(round(X0)), int(round(Y0)), int(round(Wc)), int(round(Hc))
    assert xi >= 0 and yi >= 0 and xi + wi <= SW and yi + hi <= SH and wi >= W_, (k, xi, yi, wi, hi)
    return cv2.resize(fr[yi:yi + hi, xi:xi + wi], (W_, H_), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
# ---- pass 1: face landmarks ----
lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, num_faces=1))
LM = []; cache = {}
for k, fr in reader():
    img = view(fr, k, 1.0, 0.0, 0.0)
    r = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(np.rint(img * 255).astype(np.uint8))))
    if r.face_landmarks:
        pts = np.array([(l.x * W_, l.y * H_) for l in r.face_landmarks[0]]); LM.append(np.vstack([pts[OVAL], pts[1:2]]))
    else:
        print('no face at output frame', k, '(reusing previous)'); LM.append(LM[-1])
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
def make(fr, k):
    zz = float(z[k]); cx, cy = cen[k]; cw, ch = W_ / zz, H_ / zz
    x0 = min(max(cx * (1 - 1 / zz), 0), W_ - cw); y0 = min(max(cy * (1 - 1 / zz), 0), H_ - ch)      # keeps the nose where it is
    out = view(fr, k, zz, x0, y0)
    return np.clip(np.rint(grade(out, (LM[k, :-1, :] - [x0, y0]) * zz) * 255), 0, 255).astype(np.uint8)
enc = None
if not preview:
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W_}x{H_}', '-r', '30', '-i', '-',
                            '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '13',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
for k, fr in reader():
    enc.stdin.write(make(fr, k).tobytes())
    if k % 100 == 0: print('frame', k, flush=True)
enc.stdin.close(); enc.wait()
print('done', NF)
