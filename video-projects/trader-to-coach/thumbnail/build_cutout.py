"""Cut Jude out of one 4K frame for the thumbnail.
  python3 -I thumbnail/build_cutout.py <frame.png> <selfie_segmenter.tflite> <out person.png>
Person segmentation -> edge-aware matte (guided filter) -> edge colours cleaned of the grey wall ->
mic clip painted out -> light grade -> bone-white outline baked in underneath. Output is RGBA."""
import sys, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src, model, out = sys.argv[1:4]
X0, X1 = 700, 3340                                  # crop of the 3840x2160 frame that holds him (shoulders can run off the right)
im = cv2.imread(src)[:, X0:X1]; H, W = im.shape[:2]
# paint out the lav mic (frame coords about x 1870-2000, y 1480-1610)
mm = np.zeros((H, W), np.uint8); cv2.rectangle(mm, (1868 - X0, 1478), (2002 - X0, 1612), 255, -1)
im = cv2.inpaint(im, mm, 9, cv2.INPAINT_TELEA)
rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, output_confidence_masks=True))
res = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
masks = [m.numpy_view().astype(np.float32) for m in res.confidence_masks]
m = masks[-1] if len(masks) == 1 else 1 - masks[0]   # single mask = person; multiclass = everything but background
m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
def guided(I, p, r, eps):
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp_ = box(I), box(p); a = (box(I * p) - mI * mp_) / (box(I * I) - mI * mI + eps); b = mp_ - a * mI
    return box(a) * I + box(b)
f = im.astype(np.float32) / 255
grey = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
a = guided(grey, m, 28, 2e-3); a = np.clip((a - 0.35) / 0.4, 0, 1)
a = np.clip(guided(grey, a, 8, 5e-4), 0, 1)
a = np.clip((a - 0.06) / 0.9, 0, 1)
# keep only the main connected body (drops stray bits of shelf / light tube)
n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8)); big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
keep = cv2.dilate((lab == big).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
a = a * keep
# the chair back shows between his neck and shoulder and gets picked up as "person": cut it out by hand
poly = np.array([(150, 100), (203, 100), (216, 150), (238, 198), (252, 224), (172, 268), (140, 282), (128, 200)], np.int32) + [760, 780]
cut = np.zeros((H, W), np.float32); cv2.fillPoly(cut, [poly], 1.0)
a = a * (1 - cv2.GaussianBlur(cut, (0, 0), 2.0))
# edge colours: remove the wall's contribution so no grey fringe shows on the blue background
bgm = (a < 0.02).astype(np.float32)
B = cv2.GaussianBlur(f * bgm[..., None], (0, 0), 30) / np.maximum(cv2.GaussianBlur(bgm, (0, 0), 30), 1e-3)[..., None]
F = np.clip((f - (1 - a[..., None]) * B) / np.maximum(a[..., None], 0.2), 0, 1)
fg = np.where((a[..., None] > 0.02) & (a[..., None] < 0.98), F, f)
# grade: a little brighter and punchier, slightly warmer skin
lum = cv2.GaussianBlur(cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY), (0, 0), 6)
wl = np.clip((lum - 0.16) / 0.22, 0, 1); wl = (wl * wl * (3 - 2 * wl))[..., None]                   # skin and hair highlights only: the tee stays black
fg = fg * (1 - wl) + (np.clip(fg * 1.12, 0, 1) ** 0.88) * wl                                        # lift the face out of the shadows
fg = np.clip((fg - 0.45) * 1.10 + 0.45, 0, 1) * np.array([0.97, 1.0, 1.03], np.float32)             # BGR
fg = np.clip(fg, 0, 1)
# bone-white outline under the cutout
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
ring = cv2.GaussianBlur(cv2.dilate((a > 0.5).astype(np.float32), k), (0, 0), 2.0)
bone = np.array([0xE9, 0xEF, 0xF2], np.float32) / 255
alpha = np.maximum(a, ring)
col = (fg * a[..., None] + bone * (1 - a[..., None]))
rgba = np.dstack([np.clip(col * 255 + 0.5, 0, 255).astype(np.uint8), np.clip(alpha * 255 + 0.5, 0, 255).astype(np.uint8)])
cv2.imwrite(out, rgba)
print('person', rgba.shape, 'masks', len(masks), 'coverage %.2f' % float((a > 0.5).mean()))
