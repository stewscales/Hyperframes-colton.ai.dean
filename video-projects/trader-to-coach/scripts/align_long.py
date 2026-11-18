"""Exact word timings for a long recording: wav2vec2 CTC emissions computed in overlapping chunks, then one
forced alignment of the (Whisper) transcript against the whole emission matrix.
Usage: python3 -I align_long.py <audio16k_mono.wav> <whisper words.json> <out words.json>"""
import sys, json, re, wave, numpy as np, torch, torchaudio
wav, words_p, out = sys.argv[1:4]
ONES = 'ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN TWELVE THIRTEEN FOURTEEN FIFTEEN SIXTEEN SEVENTEEN EIGHTEEN NINETEEN'.split()
TENS = '_ _ TWENTY THIRTY FORTY FIFTY SIXTY SEVENTY EIGHTY NINETY'.split()
def num(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + ' HUNDRED' + ('' if n % 100 == 0 else ' ' + num(n % 100))
    return num(n // 1000) + ' THOUSAND' + ('' if n % 1000 == 0 else ' ' + num(n % 1000))
def norm(t):
    t = t.upper().replace('%', ' PERCENT').replace('’', "'")
    t = re.sub(r'(\d),(\d)', r'\1\2', t)
    t = re.sub(r'\d+', lambda m: ' ' + num(int(m.group())) + ' ', t)
    return re.sub(r"[^A-Z' ]", ' ', t).split()
W = json.load(open(words_p))
toks = []; owner = []
for i, w in enumerate(W):
    for p in norm(w.get('text', w.get('word', ''))):
        toks.append(p); owner.append(i)
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model().eval(); labels = bundle.get_labels(); dic = {c: i for i, c in enumerate(labels)}
w = wave.open(wav); assert w.getframerate() == 16000 and w.getnchannels() == 1
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
SR, CH, CTX, HOP = 16000, 20, 2, 320
ems = []
with torch.inference_mode():
    for a in range(0, len(x), CH * SR):
        s0 = max(0, a - CTX * SR); s1 = min(len(x), a + (CH + CTX) * SR)
        e, _ = model(torch.from_numpy(x[s0:s1])[None]); e = torch.log_softmax(e[0], -1)
        t = (np.arange(e.shape[0]) * HOP + s0)                     # start sample of each emission frame
        keep = (t >= a) & (t < a + CH * SR)
        ems.append(e[torch.from_numpy(keep)])
em = torch.cat(ems)[None]; ratio = HOP / SR
text = '|'.join(toks); tokens = torch.tensor([[dic[c] for c in text]], dtype=torch.int32)
print('emission frames', em.shape[1], 'tokens', tokens.shape[1], flush=True)
ali, sc = torchaudio.functional.forced_align(em, tokens, blank=0)
spans = torchaudio.functional.merge_tokens(ali[0], sc[0].exp())
res = []; cur = []
for sp, ch in zip(spans, text):
    if ch == '|': res.append(cur); cur = []
    else: cur.append(sp)
res.append(cur); assert len(res) == len(toks)
out_w = [dict(text=w.get('text', w.get('word')), w_start=w['start'], start=None, end=None, score=[]) for w in W]
for sps, i in zip(res, owner):
    o = out_w[i]
    if o['start'] is None: o['start'] = round(sps[0].start * ratio, 3)
    o['end'] = round(sps[-1].end * ratio, 3); o['score'] += [s.score for s in sps]
for o in out_w:
    o['score'] = round(float(np.mean(o['score'])), 3) if o['score'] else None
    if o['start'] is None: o['start'] = o['end'] = o['w_start']
json.dump(out_w, open(out, 'w'), indent=0)
d = np.array([o['start'] - o['w_start'] for o in out_w])
print('words', len(out_w), 'median |shift vs whisper| %.2fs, p90 %.2fs, max %.2fs' % (np.median(np.abs(d)), np.percentile(np.abs(d), 90), np.abs(d).max()))
