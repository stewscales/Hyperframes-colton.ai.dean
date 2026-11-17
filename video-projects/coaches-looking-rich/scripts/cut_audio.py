"""Voice track: the two takes cut to the EDL (short fades at the join), levelled. No music or effects.
Usage (from the project folder): python3 -I scripts/cut_audio.py <clipA.mov> <clipB.mov> <gain_db> <out.wav>"""
import sys, subprocess
exec(open('scripts/edl.py').read())
A, B, gain, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
(_, a0, b0), (_, a1, b1) = SEGS; b1 += END_HOLD; d0 = (b0 - a0) / 30; d1 = (b1 - a1) / 30
fc = (f"[0:a:0]aresample=48000,atrim=start={a0/30:.6f}:end={b0/30:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={d0-0.008:.6f}:d=0.008[s0];"
      f"[1:a:0]aresample=48000,atrim=start={a1/30:.6f}:end={b1/30:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={d1-0.06:.6f}:d=0.06[s1];"
      f"[s0][s1]concat=n=2:v=0:a=1,highpass=f=70,volume={gain}dB,alimiter=limit=0.84:level=false,apad=whole_dur={NF/30:.6f},atrim=end={NF/30:.6f}[o]")
subprocess.check_call(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', A, '-i', B, '-filter_complex', fc, '-map', '[o]', '-ar', '48000', '-c:a', 'pcm_s24le', out])
