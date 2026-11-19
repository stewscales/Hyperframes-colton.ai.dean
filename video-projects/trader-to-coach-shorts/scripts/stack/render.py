"""Render one stacked 1080x1920 short.
  picture: dark canvas  +  video panel (square crop of the 4K source per scripts/stack/geom.py, 2160 -> 1080, top and bottom
           faded into the canvas, gentle vignette)  +  #behind graphics, hidden wherever he is (person matte)  +  #front graphics
  sound:   clips/<id>/assets/voice.wav  +  the sound effects listed in clips/<id>/scene.json (peak-normalised, well under the voice)

  python3 -I scripts/stack/render.py <source.mp4> <selfie_segmenter.tflite> <overlay_root> <clip id> [...] [--crf N] [--debug DIR]
<overlay_root>/ov-<id>/ comes from scripts/stack/capture.js. Output: renders/<id>.mp4, clips/<id>/assets/base.mp4 (panel only, for Studio)."""
import sys, os, json, re, subprocess, numpy as np, cv2
exec(open('scripts/stack/kit.py').read().split('class Scene')[0])
args = sys.argv[1:]; opt = {}
while len(args) >= 2 and args[-2].startswith('--'): opt[args[-2]] = args[-1]; args = args[:-2]
SRC, SEG, OVROOT, ids = args[0], args[1], args[2], args[3:]; CRF = opt.get('--crf', '14'); DEBUG = opt.get('--debug')
INKc = np.array([0x0A, 0x0A, 0x0A], np.float32)
# panel fades: top 110 px and bottom 250 px ease into the canvas
ramp = np.ones(PS, np.float32); e = lambda u: u * u * (3 - 2 * u)
ramp[:110] = e(np.linspace(0, 1, 110)); ramp[PS - 250:] = e(np.linspace(1, 0, 250)); ramp = ramp[:, None, None]
exec(open('scripts/stack/matte.py').read())
class Layer:
    def __init__(self, d): self.d = d; self.idx = None
    def get(self, idx):
        if idx != self.idx:
            im = cv2.imread(f'{self.d}/f{idx:05d}.png', cv2.IMREAD_UNCHANGED); assert im is not None and im.shape == (CH, CW, 4), (self.d, idx)
            a = im[..., 3]; rows = np.flatnonzero(a.any(1)); self.idx = idx
            if rows.size == 0: self.box = None
            else:
                cols = np.flatnonzero(a.any(0)); y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
                self.box = (y0, y1, x0, x1); self.rgb = im[y0:y1, x0:x1, 2::-1].astype(np.float32); self.a = (im[y0:y1, x0:x1, 3].astype(np.float32) / 255)[..., None]
        return self.box
_sfx = {}
def sfx_info(path):
    """(peak dBFS, onset s, peak time s) of a sound-effect file: library files often start with silence, so each one is trimmed
    to its onset and placed so the hit lands on the frame it belongs to (a whoosh is placed so its loudest point does)."""
    if path not in _sfx:
        x = np.frombuffer(subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-ar', '48000', '-ac', '2', '-f', 'f32le', '-'], stdout=subprocess.PIPE, check=True).stdout, np.float32).reshape(-1, 2)
        env = np.abs(x).max(1); pk = float(env.max()); on = int(np.argmax(env >= pk * 0.1)); _sfx[path] = (20 * np.log10(pk), max(0, on / 48000 - 0.004), int(np.argmax(env)) / 48000)
    return _sfx[path]

for cid in ids:
    E = build(cid); P, NF = E['pieces'], E['NF']; geom = json.load(open(f'clips/{cid}/geom.json')); scene = json.load(open(f'clips/{cid}/scene.json'))
    ovdir = f'{OVROOT}/ov-{cid}'; omap = json.load(open(ovdir + '/map.json'))['map']; assert len(omap) == NF, (len(omap), NF)
    behind, front = Layer(ovdir + '/behind'), Layer(ovdir + '/front')
    os.makedirs('renders', exist_ok=True); tmp = f'renders/{cid}.video.mp4'; dst = f'renders/{cid}.mp4'; base = f'clips/{cid}/assets/base.mp4'
    def encoder(path, crf):
        return subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{CW}x{CH}', '-r', str(FPS), '-i', '-',
                                 '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-g', '60',
                                 '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', path], stdin=subprocess.PIPE)
    # gentle vignette centred on his face: the wall darkens towards the edges so the white captions beside him read
    yy, xx = np.mgrid[0:PS, 0:PS].astype(np.float32); vig = []
    for g in geom:
        r = np.sqrt(((xx - g['nose'][0]) / 560) ** 2 + ((yy - g['nose'][1]) / 820) ** 2); u = np.clip((r - 0.45) / 0.75, 0, 1)
        vig.append((1 - 0.34 * u * u * (3 - 2 * u))[..., None])
    # footage from different parts of the recording is lit differently: bring every snippet towards the reference one
    # (per-channel gain + offset fitted on the wall and on his tee, applied at scene['match']['strength'])
    grade = [None] * len(geom); mt = scene.get('match')
    if mt:
        ref = geom[mt['ref']]['tone']; hb, lb = np.array(ref['wall']), np.array(ref['tee'])
        for si, g in enumerate(geom):
            if si == mt['ref']: continue
            ha, la = np.array(g['tone']['wall']), np.array(g['tone']['tee']); ga = (hb - lb) / (ha - la); kk = mt['strength']
            grade[si] = ((1 + kk * (ga - 1)).astype(np.float32), (kk * (lb - ga * la)).astype(np.float32)); print(cid, 'snippet', si, 'matched to', mt['ref'], 'gain', ga.round(3), flush=True)
    enc, encb = encoder(tmp, CRF), encoder(base + '.v.mp4', '20'); k = 0
    for (a, b), si in zip(P, E['snip_of']):
        x0 = geom[si]['x0']; fb = PS * PS * 3
        dec = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(a - 0.5) / FPS:.6f}', '-i', SRC, '-frames:v', str(b - a),
                                '-vf', f'crop=2160:2160:{x0}:0,scale=1080:1080:flags=lanczos+accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, bufsize=fb)
        for f in range(a, b):
            buf = dec.stdout.read(fb); assert len(buf) == fb, f'decode ended at source frame {f}'
            panel = np.frombuffer(buf, np.uint8).reshape(PS, PS, 3)
            if grade[si] is not None: panel = np.clip(panel.astype(np.float32) * grade[si][0] + grade[si][1] + 0.5, 0, 255).astype(np.uint8)
            canvas = np.empty((CH, CW, 3), np.float32); canvas[:] = INKc
            canvas[PY:PY + PS] = panel.astype(np.float32) * (ramp * vig[si]) + INKc * (1 - ramp)
            encb.stdin.write(np.clip(canvas + 0.5, 0, 255).astype(np.uint8).tobytes())
            idx = omap[k]
            box = behind.get(idx)
            if box is not None:
                y0, y1, x0b, x1b = box; m = np.zeros((CH, CW), np.float32); m[PY:PY + PS] = matte(panel)
                al = behind.a * (1 - m[y0:y1, x0b:x1b, None])
                canvas[y0:y1, x0b:x1b] = canvas[y0:y1, x0b:x1b] * (1 - al) + behind.rgb * al
                if DEBUG and k % 6 == 0: os.makedirs(DEBUG, exist_ok=True); cv2.imwrite(f'{DEBUG}/matte-{k:05d}.png', (m[PY:PY + PS] * 255).astype(np.uint8))
            box = front.get(idx)
            if box is not None:
                y0, y1, x0b, x1b = box
                canvas[y0:y1, x0b:x1b] = canvas[y0:y1, x0b:x1b] * (1 - front.a) + front.rgb * front.a
            enc.stdin.write(np.clip(canvas + 0.5, 0, 255).astype(np.uint8).tobytes()); k += 1
        dec.stdout.close(); dec.wait()
    enc.stdin.close(); encb.stdin.close(); assert enc.wait() == 0 and encb.wait() == 0 and k == NF
    # ---- sound: voice + effects ----
    voice = f'clips/{cid}/assets/voice.wav'; cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', tmp, '-i', voice]; fc = []; labs = ['[1:a]']
    for n, sx in enumerate(scene['sfx']):
        p = f'../../assets/sfx/{sx["file"]}'; cmd += ['-i', p]; pk, on, tpk = sfx_info(p); dur = 1.1
        t = sx['frame'] / FPS - ((tpk - on) if 'whoosh' in p else 0)                        # when the trimmed effect starts playing
        fc.append(f'[{n + 2}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={on:.4f}:{on + dur:.4f},asetpts=PTS-STARTPTS,afade=t=out:st={dur - 0.3:.3f}:d=0.3,volume={sx["gain_db"] - pk:.2f}dB,adelay={max(0, int(round(t * 1000)))}:all=1[s{n}]'); labs.append(f'[s{n}]')
    fc.append(''.join(labs) + f'amix=inputs={len(labs)}:normalize=0:duration=first,alimiter=limit=0.84:level=false[o]')
    subprocess.check_call(cmd + ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[o]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', dst]); os.remove(tmp)
    subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', base + '.v.mp4', '-i', voice, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', base]); os.remove(base + '.v.mp4')
    json.dump(dict(clip=cid, frames=NF, fps=FPS, size=[CW, CH], pieces=P, snippet_of_piece=E['snip_of'], out_start=E['starts'][:-1], crop_x0=[g['x0'] for g in geom]), open(f'clips/{cid}/edl.json', 'w'))
    print(cid, 'rendered', NF, 'frames ->', dst, f'{os.path.getsize(dst) / 1048576:.1f} MB', flush=True)
