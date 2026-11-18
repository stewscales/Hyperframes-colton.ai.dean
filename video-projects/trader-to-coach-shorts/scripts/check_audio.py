"""Independent listen-through of each cut voice track: wav2vec2 (CTC, greedy) transcript of the cut audio next to
the words the cut list says should be there, with a word-level diff. Run from the project folder:
python3 -I scripts/check_audio.py [clip ...]     (reads clips/<id>/assets/voice.wav, or renders/<id>.mp4 with --final)"""
import sys, re, subprocess, difflib, numpy as np, torch, torchaudio
exec(open('scripts/shorts.py').read().split("if __name__ == '__main__':")[0])
final = '--final' in sys.argv; ids = [a for a in sys.argv[1:] if not a.startswith('--')] or list(CLIPS)
B = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H; model = B.get_model().eval(); labels = B.get_labels()
norm = lambda t: re.sub(r"[^A-Z' ]", '', t.upper().replace('-', ' '))
NUM = {'90': 'NINETY', '12': 'TWELVE', '3': 'THREE'}
for cid in ids:
    src = f'renders/{cid}.mp4' if final else f'clips/{cid}/assets/voice.wav'
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', src, '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'], stdout=subprocess.PIPE, check=True).stdout
    x = torch.from_numpy(np.frombuffer(raw, np.float32).copy())[None]
    with torch.inference_mode(): em, _ = model(x)
    idx = em[0].argmax(-1).tolist(); out = []; prev = None
    for i in idx:
        if i != prev and i != 0: out.append(labels[i])
        prev = i
    hyp = ''.join(out).replace('|', ' ').split()
    E = build(cid); ref = []
    for wi, _ in word_list(E):
        for t in norm(NUM.get(re.sub(r'\W', '', WORDS[wi]['text']), WORDS[wi]['text'])).split(): ref.append(t)
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False); diffs = [f"{' '.join(ref[a:b]) or '-'} => {' '.join(hyp[c:d]) or '-'}" for op, a, b, c, d in sm.get_opcodes() if op != 'equal']
    print(f"{cid}: {len(ref)} words, match {sm.ratio():.2f}\n   heard: {' '.join(hyp)}\n   diffs: {' | '.join(diffs)}", flush=True)
