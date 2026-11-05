"""Reframe + relight + background-blur Jude's face-cam.

Usage: python3 -I facecam_pro.py <in.mp4> <out.mp4> <model.tflite> [--preview N,N,...]
Keeps exact frame count / fps; audio is muxed straight from the source (copy).
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

W, H, FPS = 720, 1280, 30

# ── Framing: 1.2x zoom, centred on Jude, eyes ~40% down the frame ──
ZOOM = 1.2
CW, CH = int(round(W / ZOOM)), int(round(H / ZOOM))   # 600 x 1067
CX = 368                                              # subject centre x in source
EYE_Y = 520                                           # eye line in source
CL = int(np.clip(CX - CW // 2, 0, W - CW))
CT = int(np.clip(EYE_Y - 0.37 * CH, 0, H - CH))

BLUR_SIGMA = 9          # "slight" background blur
MASK_EMA = 0.6          # temporal smoothing of matte (weight of current frame)

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=model),
    running_mode=vision.RunningMode.VIDEO,
    output_confidence_masks=True,
))

# Precomputed vignette (applied after crop, on output canvas)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2)
vignette = (1.0 - 0.22 * np.clip(r - 0.35, 0, 1) ** 1.5)[..., None]

# Tone curve LUT: gentle S-curve with lifted mids
x = np.linspace(0, 1, 256)
curve = x + 0.10 * np.sin(np.pi * x) * (1 - x)          # lift mids/shadows
curve = curve + 0.06 * np.sin(2 * np.pi * x) * -0.5      # mild S contrast
curve = np.clip(curve, 0, 1)
LUT = (curve * 255).astype(np.uint8)


def grade(img_f, matte):
    """img_f float32 0..1 BGR; matte float32 0..1 (person=1)."""
    # Key light: very soft (wide) version of the matte so there is no edge band
    soft = cv2.GaussianBlur(matte, (0, 0), 45)[..., None]
    img_f = img_f * (0.95 + 0.10 * soft)
    # Warm white balance (BGR): pull blue down a touch, red up a touch
    img_f[..., 0] *= 0.965
    img_f[..., 2] *= 1.025
    img_f = np.clip(img_f, 0, 1)
    u8 = (img_f * 255).astype(np.uint8)
    u8 = cv2.LUT(u8, LUT)
    # Saturation +8%
    hsv = cv2.cvtColor(u8, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.08, 0, 255)
    u8 = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return u8


reader = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
    stdout=subprocess.PIPE)
writer = None
if preview is None:
    writer = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", src, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", dst],
        stdin=subprocess.PIPE)

prev = None
i = 0
frame_bytes = W * H * 3
while True:
    buf = reader.stdout.read(frame_bytes)
    if len(buf) < frame_bytes:
        break
    frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
                                int(i * 1000 / FPS))
    matte = res.confidence_masks[0].numpy_view().astype(np.float32)
    if matte.shape != (H, W):
        matte = cv2.resize(matte, (W, H), interpolation=cv2.INTER_LINEAR)
    matte = np.clip((matte - 0.25) / 0.5, 0, 1)            # tighten edges
    matte = cv2.GaussianBlur(matte, (0, 0), 3)             # feather
    prev = matte if prev is None else MASK_EMA * matte + (1 - MASK_EMA) * prev
    matte = prev

    f = frame.astype(np.float32) / 255.0
    # Edge-aware blur: blur only background pixels (normalised convolution)
    inv = (1 - matte)[..., None]
    num = cv2.GaussianBlur(f * inv, (0, 0), BLUR_SIGMA)
    den = cv2.GaussianBlur(inv, (0, 0), BLUR_SIGMA)
    if den.ndim == 2: den = den[..., None]
    bg = num / np.maximum(den, 1e-3)
    comp = f * matte[..., None] + bg * (1 - matte[..., None])
    out = grade(comp, matte)

    # Reframe
    out = out[CT:CT + CH, CL:CL + CW]
    out = cv2.resize(out, (W, H), interpolation=cv2.INTER_LANCZOS4)
    # Gentle sharpen (unsharp) to counter the upscale
    soft = cv2.GaussianBlur(out, (0, 0), 1.2)
    out = cv2.addWeighted(out, 1.35, soft, -0.35, 0)
    out = np.clip(out.astype(np.float32) * vignette, 0, 255).astype(np.uint8)

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
print(f"frames={i} crop=({CL},{CT},{CW}x{CH})")
