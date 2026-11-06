"""Remove the cast shadow behind the speaker.

Segments the speaker, rebuilds the wall as a smooth shadow-free surface
(robust 2D polynomial fit that ignores darker shadow pixels), keeps the
camera's own fine grain, and composites the speaker back on top.
Frame count, fps and audio are preserved exactly.

Usage: python3 -I remove_shadow.py <in.mp4> <out.mp4> <selfie.tflite> [--preview N,N,...]
"""
import sys, subprocess
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
preview = None
if len(sys.argv) > 5 and sys.argv[4] == "--preview":
    preview = set(int(x) for x in sys.argv[5].split(","))

W, H, FPS = 1080, 1920, 30
SMALL = 8                       # fit the wall at 1/8 resolution
COEF_EMA = 0.35                 # temporal smoothing of the wall model (weight of new frame)
MASK_EMA = 0.85

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=model),
    running_mode=vision.RunningMode.VIDEO,
    output_confidence_masks=True,
))


def guided_filter(I, p, r, eps):
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp_ = box(I), box(p)
    a = (box(I * p) - mI * mp_) / (box(I * I) - mI * mI + eps)
    b = mp_ - a * mI
    return box(a) * I + box(b)


# Polynomial basis (degree 3 in x,y) on the small grid and on the full grid
def basis(xs, ys):
    x = xs / W * 2 - 1
    y = ys / H * 2 - 1
    return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y,
                     x ** 3, x * x * y, x * y * y, y ** 3], axis=-1)

hs, ws = H // SMALL, W // SMALL
gy, gx = np.mgrid[0:hs, 0:ws].astype(np.float32)
B_small = basis((gx + 0.5) * SMALL, (gy + 0.5) * SMALL).reshape(-1, 10)
fy, fx = np.mgrid[0:H, 0:W].astype(np.float32)
B_full = basis(fx, fy)                       # H x W x 10


def fit_wall(small_img, wall_mask):
    """Robust fit: iteratively drop pixels darker than the model (the shadow)."""
    pix = small_img.reshape(-1, 3)
    keep = wall_mask.reshape(-1).copy()
    lum = pix.mean(axis=1)
    coef = None
    for _ in range(4):
        if keep.sum() < 200:
            break
        A = B_small[keep]
        coef, *_ = np.linalg.lstsq(A, pix[keep], rcond=None)
        pred = (B_small @ coef).mean(axis=1)
        keep = wall_mask.reshape(-1) & (lum > pred * 0.965)   # shadow sits below the fit
    return coef


reader = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", src,
                           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
writer = None
if preview is None:
    writer = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", src, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)

prev_m, coef_s = None, None
i = 0
nbytes = W * H * 3
while True:
    buf = reader.stdout.read(nbytes)
    if len(buf) < nbytes:
        break
    frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    res = seg.segment_for_video(
        mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)),
        int(i * 1000 / FPS))
    m = res.confidence_masks[0].numpy_view().astype(np.float32)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    m = guided_filter(grey, m, 12, 4e-3)
    m = np.clip((m - 0.30) / 0.45, 0, 1)
    m = np.clip(guided_filter(grey, m, 4, 1e-3), 0, 1)
    prev_m = m if prev_m is None else MASK_EMA * m + (1 - MASK_EMA) * prev_m
    m = prev_m

    f = frame.astype(np.float32) / 255.0
    # Wall pixels for fitting: well away from the person
    away = cv2.erode((m < 0.05).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
    small = cv2.resize(f, (ws, hs), interpolation=cv2.INTER_AREA)
    away_s = cv2.resize(away.astype(np.uint8), (ws, hs), interpolation=cv2.INTER_NEAREST) > 0
    c = fit_wall(small, away_s)
    if c is not None:
        coef_s = c if coef_s is None else COEF_EMA * c + (1 - COEF_EMA) * coef_s
    plate = np.clip(np.tensordot(B_full, coef_s, axes=([2], [0])), 0, 1).astype(np.float32)

    # Keep the camera's fine grain/texture (shadow edges are low-frequency, so they drop out)
    grain = f - cv2.GaussianBlur(f, (0, 0), 2.0)
    wall = np.clip(plate + grain, 0, 1)

    m3 = m[..., None]
    out = (np.clip(f * m3 + wall * (1 - m3), 0, 1) * 255).astype(np.uint8)

    if preview is not None:
        if i in preview:
            cv2.imwrite(f"{dst}-{i:05d}.png", out)
    else:
        writer.stdin.write(out.tobytes())
    i += 1

reader.wait()
if writer:
    writer.stdin.close()
    writer.wait()
print(f"frames={i}")
