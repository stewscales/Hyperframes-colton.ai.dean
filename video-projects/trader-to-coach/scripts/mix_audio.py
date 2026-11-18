"""Final audio: the original voice track brought up to YouTube loudness (-14 LUFS, peaks limited to about -1 dB),
plus the quiet sound effects listed in assets/edit.json. No music.
  python3 -I scripts/mix_audio.py <source.mp4> <out.wav> [voice_gain_db]"""
import sys, json, subprocess
src, out = sys.argv[1], sys.argv[2]; gain = float(sys.argv[3]) if len(sys.argv) > 3 else 5.8
sfx = json.load(open('assets/edit.json'))['sfx']
cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', src]
fc = [f'[0:a]aresample=48000,highpass=f=60,volume={gain}dB,alimiter=limit=0.86:level=false[v]']; labels = ['[v]']
for i, (name, t, db) in enumerate(sfx):
    cmd += ['-i', f'assets/audio/{name}']
    fc.append(f'[{i + 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume={db}dB,adelay={int(round(t * 1000))}:all=1[s{i}]'); labels.append(f'[s{i}]')
fc.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.86:level=false[o]')
subprocess.check_call(cmd + ['-filter_complex', ';'.join(fc), '-map', '[o]', '-ar', '48000', '-c:a', 'pcm_s24le', out])
