"""Person matte for the 1080x1080 video panel (shared by geom.py and render.py). exec() this file after setting SEG = path
to the selfie segmenter .tflite. matte(panel_rgb_uint8) -> float32 0..1, edge-aware (follows hair and ears), zero outside the
head-and-shoulders region of the panel."""
import numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
_seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=SEG), running_mode=vision.RunningMode.IMAGE, output_confidence_masks=True))
RX0, RX1, RY0, RY1 = 120, 960, 0, 840                 # part of the panel the matte is computed for
def _guided(I, p, r, eps):
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp_ = box(I), box(p); a = (box(I * p) - mI * mp_) / (box(I * I) - mI * mI + eps); b = mp_ - a * mI
    return box(a) * I + box(b)
def matte(panel):
    roi = np.ascontiguousarray(panel[RY0:RY1, RX0:RX1])
    res = _seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=roi)); ms = [m.numpy_view().astype(np.float32) for m in res.confidence_masks]
    m = ms[-1] if len(ms) == 1 else 1 - ms[0]
    m = cv2.resize(m.reshape(m.shape[0], m.shape[1]), (RX1 - RX0, RY1 - RY0), interpolation=cv2.INTER_LINEAR)
    g = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    a = _guided(g, m, 12, 1.5e-3); a = np.clip((a - 0.35) / 0.4, 0, 1); a = np.clip(_guided(g, a, 4, 4e-4), 0, 1); a = np.clip((a - 0.08) / 0.84, 0, 1)
    out = np.zeros(panel.shape[:2], np.float32); out[RY0:RY1, RX0:RX1] = a
    return out
