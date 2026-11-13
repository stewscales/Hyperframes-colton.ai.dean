"""Pre-pass: face-oval landmarks for every source frame (normalised coords), holes filled within each clip."""
import sys, json, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src, S = sys.argv[1], sys.argv[2]
fade = np.load(S + '/fade.npy'); bounds = json.load(open(S + '/edl.json'))['bounds']
W, H = 1080, 1920
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=S + '/facelm.task'), running_mode=vision.RunningMode.IMAGE, num_faces=1))
OVAL = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-vf', 'scale=in_color_matrix=bt709:in_range=tv,format=rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
out = []; i = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    if fade[i] < 0.985:
        fr = np.clip(fr.astype(np.float32) / max(fade[i], 0.2), 0, 255).astype(np.uint8)
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr)))
    if r.face_landmarks and fade[i] >= 0.2:
        pts = np.array([(l.x, l.y) for l in r.face_landmarks[0]])
        out.append(np.vstack([pts[OVAL], pts[1:2]]))
    else:
        out.append(None)
    i += 1
N = len(out); miss = [k for k in range(N) if out[k] is None]
clip = lambda f: int(np.searchsorted(bounds, f, side='right'))
for k in miss:
    cands = [j for j in range(N) if out[j] is not None and clip(j) == clip(k) and j not in miss]
    j = min(cands, key=lambda j: abs(j - k)); out[k] = out[j]
arr = np.array(out)                        # N x 37 x 2  (36 oval points + nose)
np.save(S + '/lm.npy', arr)
print('frames', N, 'missing filled', len(miss), miss[:40])
d = np.abs(np.diff(arr[:, -1, :], axis=0)).max(1)
print('max nose jump/frame (norm):', d.max().round(4), 'at', int(d.argmax()))
