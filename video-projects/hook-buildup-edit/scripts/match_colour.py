"""Match the colour/lighting of clips to a reference clip.

Measures three anchors in each clip (lit wall, skin, dark shirt) using person
segmentation + a skin-tone mask, then builds a per-channel tone curve that maps
each clip's anchors onto the reference's, and writes it as a .cube 3D LUT.

Usage:
  python3 -I match_colour.py measure <clip.mp4> <selfie.tflite>
  python3 -I match_colour.py lut <src.mp4> <ref.mp4> <selfie.tflite> <out.cube>
"""
import sys, subprocess, json
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

W, H = 1080, 1920


def frames(path, n=12):
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", path]))
    out = []
    for k in range(n):
        t = d * (k + 0.5) / n
        raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", path,
                                       "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"])
        if len(raw) == W * H * 3:
            out.append(np.frombuffer(raw, np.uint8).reshape(H, W, 3))
    return out


def anchors(path, model):
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=mpt.BaseOptions(model_asset_path=model),
        running_mode=vision.RunningMode.IMAGE, output_confidence_masks=True))
    wall, skin, shirt = [], [], []
    for f in frames(path):
        m = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,
                                 data=cv2.cvtColor(f, cv2.COLOR_BGR2RGB))).confidence_masks[0].numpy_view()
        m = cv2.resize(m, (W, H))
        person = cv2.erode((m > 0.7).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        bg = cv2.erode((m < 0.1).astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
        lum = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        # lit wall = brighter half of background (ignores the cast shadow)
        if bg.sum() > 1000:
            thr = np.median(lum[bg])
            wall.append(f[bg & (lum >= thr)])
        ycc = cv2.cvtColor(f, cv2.COLOR_BGR2YCrCb)
        sk = person & (ycc[..., 1] > 138) & (ycc[..., 1] < 178) & (ycc[..., 2] > 80) & (ycc[..., 2] < 128) & (lum > 60)
        if sk.sum() > 500:
            skin.append(f[sk])
        sh = person & (lum < 55)
        if sh.sum() > 500:
            shirt.append(f[sh])
    med = lambda L: np.median(np.concatenate(L), axis=0).tolist()   # BGR
    return {"wall": med(wall), "skin": med(skin), "shirt": med(shirt)}


def curve(src_pts, ref_pts):
    """Monotone piecewise-linear 0..255 curve through the anchor pairs."""
    xs = [0.0] + list(src_pts) + [255.0]
    ys = [0.0] + list(ref_pts)
    # top end: keep the slope of the last segment, capped to 255
    slope = (ys[-1] - ys[-2]) / max(xs[-2] - xs[-3], 1e-3) if len(ys) > 2 else 1.0
    ys = ys + [min(255.0, ys[-1] + slope * (255 - xs[-2]))]
    order = np.argsort(xs)
    xs, ys = np.array(xs)[order], np.maximum.accumulate(np.array(ys)[order])
    return np.interp(np.arange(256), xs, ys)


def main():
    if sys.argv[1] == "measure":
        print(json.dumps(anchors(sys.argv[2], sys.argv[3])))
        return
    _, _, src, ref, model, out = sys.argv
    a, b = anchors(src, model), anchors(ref, model)
    curves = []
    for c in range(3):  # B, G, R
        sp = [a["shirt"][c], a["skin"][c], a["wall"][c]]
        rp = [b["shirt"][c], b["skin"][c], b["wall"][c]]
        curves.append(curve(sp, rp))
    N = 33
    g = np.linspace(0, 255, N)
    with open(out, "w") as fh:
        fh.write(f'TITLE "match"\nLUT_3D_SIZE {N}\n')
        for bi in range(N):          # .cube: red fastest, then green, then blue
            for gi in range(N):
                for ri in range(N):
                    r = np.interp(g[ri], np.arange(256), curves[2]) / 255
                    gg = np.interp(g[gi], np.arange(256), curves[1]) / 255
                    bb = np.interp(g[bi], np.arange(256), curves[0]) / 255
                    fh.write(f"{r:.6f} {gg:.6f} {bb:.6f}\n")
    print(json.dumps({"src": a, "ref": b}))


main()
