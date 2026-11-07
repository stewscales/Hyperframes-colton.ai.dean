"""Remove the cast shadow on the wall by lifting shadowed wall pixels to the
lit-wall level. Nothing is replaced or blurred: each wall pixel is multiplied
by a smooth gain (luma) plus a small chroma offset, so camera grain/texture is
kept. Person, burned-in graphics (white/black), dark frames and anything that
isn't wall-coloured get weight 0 and are left untouched.

Works directly on full-range yuvj420p planes (no colour-space round trip).

Usage:
  python3 -I lift_shadow.py <in> <out.mp4> <selfie.tflite>
  python3 -I lift_shadow.py <in> <outdir> <selfie.tflite> --preview t1,t2,...
"""
import sys, os, subprocess
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

src, dst, model = sys.argv[1], sys.argv[2], sys.argv[3]
preview = [float(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else None

probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                 "stream=width,height", "-of", "csv=p=0", src]).decode().strip().split(",")
W, H = int(probe[0]), int(probe[1])
W2, H2, W4, H4 = W // 2, H // 2, W // 4, H // 4
FPS = 30

seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=model),
    running_mode=vision.RunningMode.IMAGE, output_confidence_masks=True))


def guided(I, p, r, eps):
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp_ = box(I), box(p)
    a = (box(I * p) - mI * mp_) / (box(I * I) - mI * mI + eps)
    return box(a) * I + box(mp_ - a * mI)


def normconv(img, w, sigma):
    num = cv2.GaussianBlur(img * w, (0, 0), sigma)
    den = cv2.GaussianBlur(w, (0, 0), sigma)
    return num / np.maximum(den, 1e-4), den


def ramp(x, a, b):  # 0 at a, 1 at b (works for a>b too)
    return np.clip((x - a) / (b - a), 0, 1)


gy, gx = np.mgrid[0:H4, 0:W4].astype(np.float32)
xn, yn = gx / W4 * 2 - 1, gy / H4 * 2 - 1
BASIS = np.stack([np.ones_like(xn), xn, yn, xn * xn, xn * yn, yn * yn,
                  xn ** 3, xn * xn * yn, xn * yn * yn, yn ** 3], -1).reshape(-1, 10)


class State:
    def __init__(self):
        self.prevq = None
        self.coef = None
        self.matte = None


def process(Y, U, V, st, k=1.0):
    """Y: HxW uint8, U,V: H2xW2 uint8 (full range). Returns new planes + debug weight."""
    Yh = cv2.resize(Y, (W2, H2), interpolation=cv2.INTER_AREA)
    Yq = cv2.resize(Yh, (W4, H4), interpolation=cv2.INTER_AREA).astype(np.float32)
    Uq = cv2.resize(U, (W4, H4), interpolation=cv2.INTER_AREA).astype(np.float32)
    Vq = cv2.resize(V, (W4, H4), interpolation=cv2.INTER_AREA).astype(np.float32)

    cut = st.prevq is None or np.abs(Yq - st.prevq).mean() > 18
    st.prevq = Yq

    # --- person matte (half res, edge-snapped) ---
    rgb = cv2.cvtColor(cv2.merge([Yh, U, V]), cv2.COLOR_YUV2RGB)
    m = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)).confidence_masks[0].numpy_view()
    m = cv2.resize(m.astype(np.float32), (W2, H2), interpolation=cv2.INTER_LINEAR)
    Ih = Yh.astype(np.float32) / 255
    m = np.clip(guided(Ih, m, 10, 2e-3), 0, 1)
    if not cut and st.matte is not None:
        m = np.maximum(m, 0.6 * st.matte)          # never let a fast-moving limb drop out for a frame
    st.matte = m
    person = ramp(m, 0.30, 0.60)                     # snapped matte edge; skin/hair/shirt also guarded by colour+luma
    person = cv2.dilate(person, np.ones((3, 3), np.uint8))

    pq = cv2.resize(person, (W4, H4), interpolation=cv2.INTER_AREA)
    bgq = 1 - pq

    # --- wall plate: robust polynomial fit of the lit wall ---
    valid = (bgq > 0.99) & (Yq > 30) & (Yq < 238)
    if valid.sum() < 2000:
        return Y, U, V, None
    mU, mV = np.median(Uq[valid]), np.median(Vq[valid])
    valid &= (np.abs(Uq - mU) < 10) & (np.abs(Vq - mV) < 10)
    valid = cv2.erode(valid.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    vi = valid.reshape(-1)
    yv = Yq.reshape(-1)
    keep = vi.copy()
    for _ in range(5):
        if keep.sum() < 1500:
            return Y, U, V, None
        cY, *_ = np.linalg.lstsq(BASIS[keep], yv[keep], rcond=None)
        pred = BASIS @ cY
        keep = vi & (yv > pred * 0.97)           # drop shadow (darker than lit-wall model)
    cU, *_ = np.linalg.lstsq(BASIS[keep], Uq.reshape(-1)[keep], rcond=None)
    cV, *_ = np.linalg.lstsq(BASIS[keep], Vq.reshape(-1)[keep], rcond=None)
    coef = np.stack([cY, cU, cV])
    st.coef = coef if (cut or st.coef is None) else 0.5 * coef + 0.5 * st.coef
    PY, PU, PV = [(BASIS @ c).reshape(H4, W4).astype(np.float32) for c in st.coef]
    # Anchor the plate to the real lit wall: spread the residual (actual lit wall - polynomial)
    # into the shadow with a multi-scale push-pull fill. At the shadow edge the plate then equals
    # the true lit-wall value, so the lifted area continues seamlessly (no light/dark outline).
    # anchor only on clearly-lit wall, well away from the faint outer edge of the shadow
    lit = vi & (yv > pred * 0.985)
    lit = cv2.erode(lit.reshape(H4, W4).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    def pushpull(R):
        out = None
        for sg in (48, 24, 12, 6, 3):
            v, d = normconv(R, lit, sg)
            out = v if out is None else out * (1 - ramp(d, 0.04, 0.3)) + v * ramp(d, 0.04, 0.3)
        return out
    PY = PY + pushpull(Yq - PY)
    PU = PU + pushpull(Uq - PU)
    PV = PV + pushpull(Vq - PV)

    # --- which pixels are wall (soft) ---
    def wall_weight(Yp, Up, Vp, PUp, PVp, PYp):
        r = Yp / np.maximum(PYp, 1)                                      # brightness relative to the lit wall here
        lw = ramp(r, 0.30, 0.40) * ramp(r, 1.10, 1.04)                   # not shirt/hair/black text, not white graphics
        lw = lw * ramp(Yp, 236, 226)
        d = np.maximum(np.abs(Up - PUp), np.abs(Vp - PVp))
        cw = ramp(d, 14, 8)                                              # wall-coloured only (excludes skin)
        return lw * cw

    # --- per-pixel shadow measurement at HALF res (2x2 averages): resolves sharp penumbra
    # edges without a contour line, while finer grain is kept by the multiplicative lift.
    up = lambda x: cv2.resize(x, (W2, H2), interpolation=cv2.INTER_CUBIC)
    PYh, PUh, PVh = up(PY), up(PU), up(PV)
    Yhf, Uf, Vf = Yh.astype(np.float32), U.astype(np.float32), V.astype(np.float32)
    # Burned-in black frame (intro card): dark region touching the top edge -> lock it and a margin.
    dark = (Yq < 16).astype(np.uint8)
    n, lab = cv2.connectedComponents(dark)
    top_ids = np.unique(lab[0][dark[0] > 0])
    frame_mask = np.isin(lab, top_ids[top_ids > 0]).astype(np.uint8)
    if frame_mask.sum() > 0.02 * frame_mask.size:
        # Stylised intro card (black frame + built-in vignette): the designed darkening can't be
        # separated from the shadow without artifacts, so these frames are passed through untouched.
        return Y, U, V, None
    # soft lock: fully locked within 6px (quarter res) of the frame, fading to free by 40px
    dist = cv2.distanceTransform(1 - frame_mask, cv2.DIST_L2, 5) if frame_mask.any() else np.full((H4, W4), 1e3, np.float32)
    frame_mask = 1 - ramp(dist, 6, 40)
    frame_mask = frame_mask.astype(np.float32)
    frame_h = cv2.resize(frame_mask, (W2, H2), interpolation=cv2.INTER_LINEAR)
    wh = (1 - person) * (1 - frame_h) * wall_weight(Yhf, Uf, Vf, PUh, PVh, PYh)
    # Smooth the wall weight into soft/blurred edges (e.g. a motion-blurred hand in front of the
    # shadow) so the lift fades out naturally instead of leaving a jagged shadow strip.
    # Solid person stays fully protected.
    core = ramp(m, 0.55, 0.85)
    wh = np.maximum(wh, cv2.GaussianBlur(wh, (0, 0), 6) * (1 - core) * (1 - frame_h))
    # Shadowed wall seen THROUGH an out-of-focus foreground (blurred hand near the lens): the
    # detector calls it person, but it has wall colour, shadow-range brightness and no sharp
    # detail, and it touches lifted wall. Sharp things (mic, face texture, hair) fail the test.
    lap = np.abs(cv2.Laplacian(cv2.GaussianBlur(Yhf, (0, 0), 1.0), cv2.CV_32F))
    sharp = cv2.GaussianBlur(lap, (0, 0), 4)
    soft = ramp(sharp, 1.6, 0.8)                               # 1 = blurred/featureless
    rr = Yhf / np.maximum(PYh, 1)
    dd = np.maximum(np.abs(Uf - PUh), np.abs(Vf - PVh))
    looks_wall = ramp(rr, 0.32, 0.42) * ramp(rr, 0.97, 0.90) * ramp(dd, 10, 5)
    near = cv2.GaussianBlur(cv2.dilate((wh > 0.5).astype(np.float32), np.ones((61, 61), np.uint8)), (0, 0), 8)
    through = looks_wall * soft * near * (1 - frame_h)
    through = cv2.GaussianBlur(through, (0, 0), 3)
    wh = np.maximum(wh, through)
    # Uncertain matte band: on motion-blurred edges the matte can snap to the shadow's edge
    # instead of the body's. Inside that band (outside the solid core), strictly wall-coloured
    # pixels at shadow brightness are wall. Shirt/hair (too dark) and skin (wrong chroma) fail.
    core_s = cv2.erode(ramp(m, 0.70, 0.90), np.ones((9, 9), np.uint8))
    band = np.clip(person - core_s, 0, 1)
    strict = ramp(rr, 0.38, 0.46) * ramp(rr, 0.95, 0.88) * ramp(dd, 7, 4)
    strict = cv2.morphologyEx(strict, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))   # drop isolated specks
    allow = band * strict * near * (1 - frame_h)
    wh = np.maximum(wh, cv2.GaussianBlur(allow, (0, 0), 1.5))
    Es = cv2.erode((wh > 0.9).astype(np.float32), np.ones((5, 5), np.uint8))
    Yden, _ = normconv(Yhf, np.maximum(wh, 1e-3), 1.5)   # light denoise (3px at 4K) along wall only
    graw = np.clip(PYh / np.maximum(Yden, 1), 0.8, 2.4)
    gfill, den = normconv(graw, Es, 3)
    Ufill, _ = normconv(Uf, Es, 3)
    Vfill, _ = normconv(Vf, Es, 3)
    ew = Es * wh
    gh = graw * ew + gfill * (1 - ew)
    LU = Uf * ew + Ufill * (1 - ew)
    LV = Vf * ew + Vfill * (1 - ew)
    support = ramp(den, 0.02, 0.15)                 # only where there is enough wall nearby to measure

    gh = np.clip(gh, 1.0, 2.2)
    s = ramp(gh - 1, 0.003, 0.012) * support       # small dead zone: lit wall is left exactly as is
    gh = 1 + (gh - 1) * s * k                     # k: per-frame strength (0 on motion-blurred frames, eased)
    dU = (PUh - LU) * s * k
    dV = (PVh - LV) * s * k

    # --- apply: chroma at half res, luma at full res ---
    Uo = np.clip(np.rint(Uf + dU * wh), 0, 255).astype(np.uint8)
    Vo = np.clip(np.rint(Vf + dV * wh), 0, 255).astype(np.uint8)
    gf = cv2.resize(1 + (gh - 1) * wh, (W, H), interpolation=cv2.INTER_LINEAR)
    # full-res luma guard: never lift white graphics / dark detail even at sub-half-res edges
    Yf = Y.astype(np.float32)
    PYf = cv2.resize(PYh, (W, H), interpolation=cv2.INTER_LINEAR)
    rf = Yf / np.maximum(PYf, 1)
    guard = ramp(rf, 0.28, 0.38) * ramp(rf, 1.10, 1.04) * ramp(Yf, 238, 228)
    gf = 1 + (gf - 1) * guard
    Yo = np.clip(np.rint(Yf * gf), 0, 255).astype(np.uint8)
    return Yo, Uo, Vo, (gh - 1) * wh


def read_planes(buf):
    n = W * H
    Y = np.frombuffer(buf, np.uint8, n).reshape(H, W)
    U = np.frombuffer(buf, np.uint8, n // 4, n).reshape(H2, W2)
    V = np.frombuffer(buf, np.uint8, n // 4, n + n // 4).reshape(H2, W2)
    return Y, U, V


fsize = W * H * 3 // 2
if preview:
    os.makedirs(dst, exist_ok=True)
    for t in preview:
        buf = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t}", "-i", src,
                                       "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "yuvj420p", "-"])
        Y, U, V = read_planes(buf)
        Yo, Uo, Vo, dbg = process(Y, U, V, State())
        to_bgr = lambda y, u, v: cv2.cvtColor(cv2.merge([cv2.resize(y, (W2, H2), interpolation=cv2.INTER_AREA), u, v]), cv2.COLOR_YUV2BGR)
        a, b = to_bgr(Y, U, V), to_bgr(Yo, Uo, Vo)
        dmap = np.zeros_like(a)
        if dbg is not None:
            dmap[..., 2] = np.clip(dbg * 400, 0, 255).astype(np.uint8)
            dmap[..., 1] = np.clip(np.abs(b.astype(int) - a.astype(int)).max(2) * 8, 0, 255).astype(np.uint8)
        row = np.hstack([cv2.resize(x, (540, 960)) for x in (a, b, dmap)])
        cv2.imwrite(os.path.join(dst, f"pv-{t:06.2f}.jpg"), row, [cv2.IMWRITE_JPEG_QUALITY, 92])
        cv2.imwrite(os.path.join(dst, f"after-{t:06.2f}.png"), b)
        cv2.imwrite(os.path.join(dst, f"before-{t:06.2f}.png"), a)
    sys.exit(0)

reader = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-f", "rawvideo",
                           "-pix_fmt", "yuvj420p", "-"], stdout=subprocess.PIPE, bufsize=fsize * 2)
writer = subprocess.Popen(
    ["ffmpeg", "-nostdin", "-v", "error", "-y",
     "-f", "rawvideo", "-pix_fmt", "yuvj420p", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-i", src, "-map", "0:v", "-map", "1:a", "-map_metadata", "1",
     "-c:v", "libx265", "-preset", "medium", "-x265-params", "crf=13:log-level=error",
     "-pix_fmt", "yuvj420p", "-color_range", "pc", "-colorspace", "bt709", "-color_trc", "bt709",
     "-color_primaries", "bt709", "-tag:v", "hvc1", "-c:a", "copy", "-movflags", "+faststart", dst],
    stdin=subprocess.PIPE)
# Per-frame strength: 0 on heavily motion-blurred frames (shadow model unreliable there),
# eased back to 1 over 6 frames either side so the shadow never snaps on/off.
P99 = os.environ.get("BLUR_P99")
strength = None
if P99:
    p99 = np.load(P99)
    blurred = np.where(p99 < 9.0)[0]
    idx = np.arange(len(p99))
    dist = np.min(np.abs(idx[:, None] - blurred[None, :]), axis=1) if len(blurred) else np.full(len(p99), 99)
    strength = np.clip(dist / 6.0, 0, 1)
st = State()
i = 0
while True:
    buf = reader.stdout.read(fsize)
    if len(buf) < fsize:
        break
    Y, U, V = read_planes(buf)
    k = 1.0 if strength is None or i >= len(strength) else float(strength[i])
    if k <= 0:
        Yo, Uo, Vo = Y, U, V
        st.prevq = None                       # force a fresh start after the blurred run
    else:
        Yo, Uo, Vo, _ = process(Y, U, V, st, k)
    writer.stdin.write(Yo.tobytes()); writer.stdin.write(Uo.tobytes()); writer.stdin.write(Vo.tobytes())
    i += 1
    if i % 50 == 0:
        print(f"frame {i}", flush=True)
reader.wait(); writer.stdin.close(); writer.wait()
print(f"frames={i}")
