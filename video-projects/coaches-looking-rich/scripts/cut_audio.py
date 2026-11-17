"""Cut the voice track to the EDL (8 ms fades at the join), keep the natural tail, level it.
Usage (from the project folder): python3 -I scripts/cut_audio.py <gain_db> <out.wav>"""
import sys, subprocess
exec(open('scripts/edl.py').read())
gain, out = float(sys.argv[1]), sys.argv[2]
(a0, b0), (a1, _) = SEGS; d0 = (b0 - a0) / 30
fc = (f"[0:a]aresample=48000,asplit[x][y];"
      f"[x]atrim=start={a0/30:.6f}:end={b0/30:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={d0-0.008:.6f}:d=0.008[s0];"
      f"[y]atrim=start={a1/30:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008[s1];"
      f"[s0][s1]concat=n=2:v=0:a=1,highpass=f=70,volume={gain}dB,alimiter=limit=0.84:level=false,apad=whole_dur={NF/30:.6f},atrim=end={NF/30:.6f}[o]")
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', 'assets/raw.mov', '-filter_complex', fc, '-map', '[o]', '-ar', '48000', '-c:a', 'pcm_s24le', out])
