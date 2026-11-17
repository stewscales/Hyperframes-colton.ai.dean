"""Cut list (v2, from the two original 4K takes; same edit as v1).
  clip A = IMG_3362.MOV    laptop close + "Coaches are so focused ... build a business."
  clip B = IMG_3366_1.MOV  "Everyone's so focused ... isn't converting."
SEGS: (clip, first frame, end frame exclusive). Audio follows these exactly.
BASE: the framing v1 was built on (how the earlier 1080p export was cropped from the 4K), per clip:
      old_1080 = s * (4K px / 2) + (tx, ty). Punch-ins are applied on top of this framing.
After the last word (clip B frame 534) he blinks and then starts to move, so, as in v1, the last eyes-open
frame is held for END_HOLD frames to let the line land (the audio keeps running: real room tone)."""
SEGS = [('A', 272, 448), ('B', 323, 535)]
END_HOLD = 14
BASE = {'A': (1.1393, -0.4, -36.65), 'B': (1.1869, -77.1, -179.3)}
SHOW = [(c, f) for c, a, b in SEGS for f in range(a, b)] + [(SEGS[-1][0], SEGS[-1][2] - 1)] * END_HOLD
NF = len(SHOW)
CUTS = [0, SEGS[0][2] - SEGS[0][1]]
