"""Render the talking head (picture only) for each short from the 4K long-form source: cut to the EDL, reframed
to 1080x1920 around his face, framing changes / push-ins per scripts/shorts.py. Always downscaled from 4K (never
upscaled), colour untouched.
Usage (from the project folder): python3 -I scripts/render_th.py <source video> <facelm.task> [clip ...]
  ->  clips/<id>/assets/th.mp4  and  clips/<id>/edl.json"""
import sys, os, json, subprocess, numpy as np, cv2, mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
exec(open('scripts/shorts.py').read().split("if __name__ == '__main__':")[0])
SRC, model = sys.argv[1:3]; ids = sys.argv[3:] or list(CLIPS)
W_, H_ = 1080, 1920; SW, SH = 3840, 2160; BW = 1216                     # base window in the source: 1216x2160 (9:16 of full height)
lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.IMAGE, num_faces=1))

def decode(a, b, vf, w, h):
    """Frames a..b-1 of the source through filter chain vf as RGB arrays (frame-accurate input seek)."""
    fb = w * h * 3
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(a - 0.5) / FPS:.6f}', '-i', SRC, '-frames:v', str(b - a), '-vf', vf,
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=fb)
    for k in range(a, b):
        buf = p.stdout.read(fb); assert len(buf) == fb, f'decode ended at source frame {k}'
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    p.stdout.close(); p.wait()

for cid in ids:
    E = build(cid); P, NF = E['pieces'], E['NF']; z = zoom_schedule(E); nsn = len(E['C']['snips'])
    # ---- pass 1: where his nose is, per snippet (median) ----
    pts = [[] for _ in range(nsn)]
    for (a, b), si in zip(P, E['snip_of']):
        for n, fr in enumerate(decode(a, b, 'scale=960:540:flags=area,scale=in_color_matrix=bt709:in_range=tv', 960, 540)):
            if n % 3: continue
            r = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(fr)))
            if r.face_landmarks: pts[si].append((r.face_landmarks[0][1].x * SW, r.face_landmarks[0][1].y * SH))
    cen = [np.median(np.array(p), axis=0) for p in pts]; assert all(len(p) > 5 for p in pts)
    print(cid, 'nose per snippet', [np.round(c).tolist() for c in cen], flush=True)
    # ---- pass 2: render ----
    os.makedirs(f'clips/{cid}/assets', exist_ok=True); dst = f'clips/{cid}/assets/th.mp4'
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W_}x{H_}', '-r', str(FPS), '-i', '-',
                            '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '13',
                            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
    k = 0; crops = []
    for (a, b), si in zip(P, E['snip_of']):
        nx, ny = cen[si]; bx = int(round(min(max(nx - BW / 2, 0), SW - BW)))        # base window: nose centred, full height
        ax, ay = nx - bx, ny                                                        # zooms keep his nose where it is
        for fr in decode(a, b, f'crop={BW}:{SH}:{bx}:0,scale=in_color_matrix=bt709:in_range=tv', BW, SH):
            zz = float(z[k]); cw, ch = int(round(BW / zz)), int(round(SH / zz))
            x0 = int(round(min(max(ax * (1 - 1 / zz), 0), BW - cw))); y0 = int(round(min(max(ay * (1 - 1 / zz), 0), SH - ch)))
            assert cw >= W_ and ch >= H_, (k, zz)
            enc.stdin.write(cv2.resize(fr[y0:y0 + ch, x0:x0 + cw], (W_, H_), interpolation=cv2.INTER_AREA).tobytes())
            crops.append((bx + x0, y0, cw, ch)); k += 1
    enc.stdin.close(); assert enc.wait() == 0 and k == NF
    json.dump(dict(clip=cid, frames=NF, fps=FPS, pieces=P, snippet_of_piece=E['snip_of'], out_start=E['starts'][:-1],
                   zoom=[round(float(v), 4) for v in z], crop=crops, nose=[c.tolist() for c in cen]), open(f'clips/{cid}/edl.json', 'w'))
    print(cid, 'rendered', NF, 'frames', flush=True)
