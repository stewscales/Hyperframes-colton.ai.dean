"""Cut list. The source is one 14 s clip (1080x1920, 30 fps) with a fade-to-black dip baked in between two takes
(darkest at frame 201). The edit: start as the hands reach for the laptop, remove the dip, hold the last good
frame so the final line can land.
  SEGS      source frame ranges kept (end exclusive); audio follows these exactly
  show(f)   which source frame is displayed for source time f (frames too dark to restore show the nearest good one)
  END_HOLD  extra frames at the end showing the last frame before he blinks"""
SEGS = [(22, 198), (200, 413)]
FADE_MIN = 0.33                     # frames faded darker than this are not restored; the nearest usable frame is held
TAKE2_FIRST_GOOD = 204              # first frame of take 2 with fade >= FADE_MIN
END_HOLD = 14
def show(f):
    return TAKE2_FIRST_GOOD if 200 <= f < TAKE2_FIRST_GOOD else f
SHOW = [show(f) for a, b in SEGS for f in range(a, b)] + [SEGS[-1][1] - 1] * END_HOLD
NF = len(SHOW)
CUTS = [0, SEGS[0][1] - SEGS[0][0]]
