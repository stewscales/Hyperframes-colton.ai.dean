"""Voice track for each short: the source audio cut on exactly the frames of the picture (8 ms fades at every
join), then levelled to about -15 LUFS with a limiter. No music, no sound effects.
Usage (from the project folder): python3 -I scripts/cut_audio.py <source video> [clip ...]   ->  clips/<id>/assets/voice.wav"""
import sys, os, subprocess, json, re, numpy as np
exec(open('scripts/shorts.py').read().split("if __name__ == '__main__':")[0])
SRC = sys.argv[1]; ids = sys.argv[2:] or list(CLIPS); SR = 48000; SPF = SR // FPS; TARGET = -15.0
raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', SRC, '-map', '0:a:0', '-ar', str(SR), '-ac', '2', '-f', 's16le', '-'], stdout=subprocess.PIPE, check=True).stdout
X = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
def fade(x, n_in, n_out):
    x[:n_in] *= np.linspace(0, 1, n_in, dtype=np.float32)[:, None]; x[-n_out:] *= np.linspace(1, 0, n_out, dtype=np.float32)[:, None]; return x
def lufs(path):
    r = subprocess.run(['ffmpeg', '-nostdin', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], stderr=subprocess.PIPE, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])
for cid in ids:
    E = build(cid); P = E['pieces']; out = []
    for n, (a, b) in enumerate(P):
        seg = X[a * SPF:b * SPF].copy(); last = n == len(P) - 1; tail = E['C'].get('tail')
        if last and tail:                                  # voice ends at `cut`; room tone carries the picture to the end
            c = int(round(tail['cut'] * SR)) - a * SPF; x = int(0.03 * SR); t0 = int(round(tail['tone'] * SR))
            tone = X[t0:t0 + len(seg) - c + x].copy()
            seg[c - x:c] *= np.linspace(1, 0, x, dtype=np.float32)[:, None]; seg[c:] = 0
            tone[:x] *= np.linspace(0, 1, x, dtype=np.float32)[:, None]; seg[c - x:] += tone
        out.append(fade(seg, int((0.010 if n == 0 else 0.008) * SR), int((0.06 if last else 0.008) * SR)))
    y = np.concatenate(out); assert len(y) == E['NF'] * SPF
    d = f'clips/{cid}/assets'; os.makedirs(d, exist_ok=True); tmp = f'{d}/cut.f32'; y.tofile(tmp); dst = f'{d}/voice.wav'
    gain = 4.5
    for _ in range(4):
        subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', tmp,
                               '-af', f'highpass=f=70,volume={gain:.2f}dB,alimiter=limit=0.84:level=false', '-c:a', 'pcm_s24le', dst])
        L, pk = lufs(dst)
        if abs(L - TARGET) < 0.15: break
        gain += TARGET - L
    os.remove(tmp)
    print(f'{cid}: {len(y)/SR:.2f}s  gain {gain:+.2f} dB  {L:.1f} LUFS  peak {pk:.1f} dBFS', flush=True)
