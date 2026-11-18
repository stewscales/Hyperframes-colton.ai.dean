"""Check a rendered short against its cut list and caption schedule, on every frame, and write review sheets.
  - frame count / size / fps
  - picture outside the caption band matches clips/<id>/assets/base.mp4 frame for frame (no dropped / shifted frames)
  - a caption is on screen on every frame, and it changes exactly on the scheduled frames (and nowhere else)
  - sheets: renders/review/<id>-captions.jpg (one tile per caption, 4 frames after it lands) and
            renders/review/<id>-cuts.jpg (first frame after each cut, full frame)
Run from the project folder: python3 -I scripts/verify.py <clip> [...]"""
import sys, os, json, subprocess, numpy as np, cv2
W_, H_ = 1080, 1920; Y0, Y1 = 960, 1300
def frames(path):
    fb = W_ * H_ * 3
    p = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE, bufsize=fb)
    while True:
        b = p.stdout.read(fb)
        if len(b) < fb: break
        yield np.frombuffer(b, np.uint8).reshape(H_, W_, 3)
os.makedirs('renders/review', exist_ok=True); ok_all = True
for cid in sys.argv[1:]:
    edl = json.load(open(f'clips/{cid}/edl.json')); caps = json.load(open(f'clips/{cid}/captions.json')); NF = edl['frames']
    on = [c['frame'] for c in caps]; cuts = edl['out_start']
    info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,nb_frames', '-of', 'csv=p=0', f'renders/{cid}.mp4'], capture_output=True, text=True).stdout.strip()
    masks = []; out_diff = []; cap_tiles = {}; cut_tiles = {}; want_cap = {f + 4 if f + 4 < NF else NF - 1: i for i, f in enumerate(on)}
    n = 0
    for fr, bs in zip(frames(f'renders/{cid}.mp4'), frames(f'clips/{cid}/assets/base.mp4')):
        d = np.abs(fr.astype(np.int16) - bs.astype(np.int16)).max(axis=2)
        out_diff.append(max(float(d[:Y0 - 60].mean()), float(d[Y1 + 60:].mean())))
        masks.append(cv2.resize((d[Y0:Y1] > 48).astype(np.uint8), (270, 85), interpolation=cv2.INTER_AREA) > 0)
        if n in want_cap:
            t = cv2.resize(fr[300:1320], (286, 270), interpolation=cv2.INTER_AREA); cv2.putText(t, f'{want_cap[n]}@{on[want_cap[n]]}', (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA); cap_tiles[want_cap[n]] = t
        if n in cuts or n == NF - 1:
            t = cv2.resize(fr, (216, 384), interpolation=cv2.INTER_AREA); cv2.putText(t, f'f{n} z{edl["zoom"][n]:.3f}', (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA); cut_tiles[n] = t
        n += 1
    probs = []
    if n != NF: probs.append(f'frames {n} != {NF}')
    if max(out_diff) > 4: probs.append(f'picture differs from base outside captions (max mean diff {max(out_diff):.1f} at frame {int(np.argmax(out_diff))})')
    area = np.array([m.sum() for m in masks]); empty = [k for k in range(n) if area[k] < 150]
    if empty: probs.append(f'no caption on frames {empty[:12]}{"..." if len(empty) > 12 else ""}')
    # caption identity: compare the text mask a few frames after each onset (settled) with every frame of its span
    bounds = on + [NF]; changes = []
    for i in range(len(on)):
        a, b = bounds[i], bounds[i + 1]; ref = masks[min(a + 5, b - 1)]
        for k in range(min(a + 4, b - 1), b):
            iou = (masks[k] & ref).sum() / max(1, (masks[k] | ref).sum())
            if iou < 0.55: probs.append(f'caption {i} looks different on frame {k} (iou {iou:.2f})'); break
        if i:
            prev = masks[max(bounds[i - 1] + 5, a - 1) if a - 1 >= bounds[i - 1] + 5 else a - 1]
            iou = (masks[min(a + 5, b - 1)] & prev).sum() / max(1, (masks[min(a + 5, b - 1)] | prev).sum())
            same_text = caps[i]['lines'] == caps[i - 1]['lines']
            if iou > 0.8 and not same_text: probs.append(f'caption {i} did not change on frame {a} (iou {iou:.2f})')
            sw = (masks[a] & masks[a - 1]).sum() / max(1, (masks[a] | masks[a - 1]).sum())
            changes.append(round(float(sw), 2))
    def sheet(tiles, cols, path):
        ks = sorted(tiles); t0 = tiles[ks[0]]; rows = (len(ks) + cols - 1) // cols
        S = np.zeros((rows * t0.shape[0], cols * t0.shape[1], 3), np.uint8)
        for j, k in enumerate(ks): S[(j // cols) * t0.shape[0]:(j // cols + 1) * t0.shape[0], (j % cols) * t0.shape[1]:(j % cols + 1) * t0.shape[1]] = tiles[k]
        cv2.imwrite(path, S, [cv2.IMWRITE_JPEG_QUALITY, 88])
    sheet(cap_tiles, 6, f'renders/review/{cid}-captions.jpg'); sheet(cut_tiles, 7, f'renders/review/{cid}-cuts.jpg')
    print(f'{cid}: {info}  frames {n}/{NF}  captions {len(on)}  max off-caption diff {max(out_diff):.2f}  min caption area {int(area.min())}  ->', 'OK' if not probs else 'PROBLEMS: ' + '; '.join(probs), flush=True)
    ok_all &= not probs
sys.exit(0 if ok_all else 1)
