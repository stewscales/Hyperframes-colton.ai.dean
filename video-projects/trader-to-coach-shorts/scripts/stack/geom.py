"""Where he is, per snippet, for the stacked 1080x1920 layout: the square crop of the 4K frame that becomes the
video panel (2160x2160 -> 1080x1080, never upscaled, centred on his nose) and his head geometry inside that panel.
Also the left / right edge of his head silhouette at forehead height (from the person segmenter), which is where words tucked
behind his head are anchored.
Run from the project folder: python3 -I scripts/stack/geom.py <source video> <facelm.task> <selfie_segmenter.tflite> [clip ...]  ->  clips/<id>/geom.json"""
import sys, os, json, subprocess, numpy as np, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
exec(open('scripts/shorts.py').read().split("if __name__ == '__main__':")[0])
SRC, model, segm = sys.argv[1:4]; ids = sys.argv[4:] or list(CLIPS); SW, SH = 3840, 2160
SEG = segm; exec(open('scripts/stack/matte.py').read())
lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, num_faces=1))
for cid in ids:
    E = build(cid); nsn = len(E['C']['snips']); pts = [[] for _ in range(nsn)]
    for (a, b), si in zip(E['pieces'], E['snip_of']):
        p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(a - 0.5) / FPS:.6f}', '-i', SRC, '-t', f'{(b - a) / FPS:.6f}', '-vf', 'fps=10,scale=960:540:flags=area',
                              '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=960 * 540 * 3)
        while True:
            buf = p.stdout.read(960 * 540 * 3)
            if len(buf) < 960 * 540 * 3: break
            r = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.frombuffer(buf, np.uint8).reshape(540, 960, 3).copy()))
            if r.face_landmarks:
                L = r.face_landmarks[0]; pts[si].append([L[1].x * SW, L[1].y * SH, L[10].y * SH, L[152].y * SH, L[234].x * SW, L[454].x * SW])
        p.stdout.close(); p.wait()
    out = []
    for si in range(nsn):
        m = np.median(np.array(pts[si]), axis=0); x0 = int(round(min(max(m[0] - SH / 2, 0), SW - SH) / 2) * 2)
        g = dict(x0=x0, nose=[(m[0] - x0) / 2, m[1] / 2], forehead_y=m[2] / 2, chin_y=m[3] / 2, face_x=[(m[4] - x0) / 2, (m[5] - x0) / 2], n=len(pts[si]))
        # head silhouette at forehead height through the snippet: [output frame, left x, right x] in panel px (same matte as the render)
        fh = g['chin_y'] - g['forehead_y']; r0, r1 = int(g['forehead_y'] - 0.30 * fh), int(g['forehead_y'] + 0.15 * fh); trk = []; tone = []
        for (a, b), sj, o in zip(E['pieces'], E['snip_of'], E['starts']):
            if sj != si: continue
            p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(a - 0.5) / FPS:.6f}', '-i', SRC, '-frames:v', str(b - a),
                                  '-vf', f'crop=2160:2160:{x0}:0,scale=1080:1080:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=1080 * 1080 * 3)
            for n in range(b - a):
                buf = p.stdout.read(1080 * 1080 * 3); assert len(buf) == 1080 * 1080 * 3
                if n % 3: continue
                pan = np.frombuffer(buf, np.uint8).reshape(1080, 1080, 3); nx = int(g['nose'][0])
                if n % 15 == 0:                               # tone samples: wall either side of his head, and his tee (mean RGB)
                    tone.append([pan[140:340, nx + 220:nx + 420].reshape(-1, 3).mean(0), pan[140:340, nx - 420:nx - 220].reshape(-1, 3).mean(0), pan[660:760, nx - 140:nx + 140].reshape(-1, 3).mean(0)])
                cols = np.flatnonzero((matte(pan)[r0:r1] > 0.5).any(0))
                if cols.size: trk.append([o + n, int(cols[0]), int(cols[-1])])
            p.stdout.close(); p.wait()
        g['head_track'] = trk
        tn = np.median(np.array(tone), axis=0); g['tone'] = dict(wall=((tn[0] + tn[1]) / 2).round(2).tolist(), tee=tn[2].round(2).tolist())
        out.append(g)
    json.dump(out, open(f'clips/{cid}/geom.json', 'w'), indent=1); print(cid, json.dumps(out)[:300], flush=True)
