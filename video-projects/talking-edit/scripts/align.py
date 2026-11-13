"""Forced alignment (wav2vec2 CTC) of a known script to 16 kHz mono audio -> exact word start/end times.
Usage: python3 align.py <audio16k.wav> <out.json> ["WORDS IN CAPS"]"""
import sys, json, torch, torchaudio, numpy as np, wave
wav_path, out = sys.argv[1], sys.argv[2]
MAIN = "SCROLL YOUR INSTAGRAM IF IT'S JUST YOUR CARS AND YOUR WATCHES AND YOUR FANCY DINNERS JUST THE SAME POST TEN TIMES IF THAT'S YOU YOUR AUDIENCE WILL LEARN ONE THING ABOUT YOU AND THEN JUST LOSE ATTENTION AND THAT'S THE PROBLEM SO HERE'S THE FIX FOUR TYPES OF POSTS FIRST TEACH ONE CONCEPT THIRTY SECONDS NEXT THE PROCESS HOW YOU PLAN AND REVIEW YOUR TRADES NOT JUST YOUR WINS THIRD YOUR STORY WHERE DID YOU START WHERE ARE YOU NOW AND HOW EXACTLY DID YOU GET THERE FINALLY YOUR OPINION WHAT DOES THIS INDUSTRY GET WRONG A SKEPTICAL AUDIENCE NEEDS FOUR REASONS TO TRUST YOU NOT ONE SAVE THIS AND CHECK YOUR LAST TEN POSTS"
words = (sys.argv[3] if len(sys.argv) > 3 else MAIN).split()
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model().eval(); labels = bundle.get_labels(); dic = {c: i for i, c in enumerate(labels)}
with wave.open(wav_path) as w:
    assert w.getframerate() == 16000 and w.getnchannels() == 1
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
wavf = torch.from_numpy(x)[None]
with torch.inference_mode():
    em, _ = model(wavf); em = torch.log_softmax(em, dim=-1)
text = "|".join(words)
tokens = torch.tensor([[dic[c] for c in text]], dtype=torch.int32)
ali, scores = torchaudio.functional.forced_align(em, tokens, blank=0)
ali, scores = ali[0], scores[0].exp()
ratio = wavf.shape[1] / em.shape[1] / 16000
# token spans
spans = []; prev = 0; ti = -1
T = len(ali)
i = 0
tok_spans = torchaudio.functional.merge_tokens(ali, scores)
res = []; k = 0
cur = []
for sp, ch in zip(tok_spans, text):
    if ch == '|':
        res.append(cur); cur = []
    else: cur.append(sp)
res.append(cur)
out_words = []
for w, sps in zip(words, res):
    out_words.append({'word': w, 'start': round(sps[0].start * ratio, 3), 'end': round(sps[-1].end * ratio, 3), 'score': round(float(np.mean([s.score for s in sps])), 3)})
json.dump(out_words, open(out, 'w'), indent=0)
print(' '.join('[%.2f-%.2f %.2f]%s' % (w['start'], w['end'], w['score'], w['word']) for w in out_words))
