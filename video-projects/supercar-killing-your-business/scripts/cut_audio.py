"""Cut the voice track to the EDL (8 ms fades at every join), then level it.
Usage: python3 cut_audio.py <src.mov> <edl.json> <out_voice.wav> <gain_db>"""
import sys, json, subprocess
src, edl, out, gain = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3], float(sys.argv[4])
parts = []; labels = []
for i, (a, b) in enumerate(edl['segs']):
    d = (b - a) / 30
    parts.append(f"[0:a]aresample=48000,atrim=start={a/30:.6f}:end={b/30:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={d-0.008:.6f}:d=0.008[s{i}]")
    labels.append(f'[s{i}]')
fc = ';'.join(parts) + ';' + ''.join(labels) + f"concat=n={len(labels)}:v=0:a=1,highpass=f=70,volume={gain}dB,alimiter=limit=0.84:level=false[o]"
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[o]', '-ar', '48000', '-c:a', 'pcm_s24le', out])
