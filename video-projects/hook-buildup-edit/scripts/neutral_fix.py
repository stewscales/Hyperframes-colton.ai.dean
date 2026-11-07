"""Apply a correction only to near-neutral colours (walls) inside a .cube LUT.

Saturated colours (skin) are left alone; weight fades from 1 at saturation 0
to 0 at saturation >= SAT_MAX.
Usage: python3 -I neutral_fix.py <in.cube> <out.cube> <r_gain> <g_gain> <b_gain>
"""
import sys
import numpy as np
src, dst, rg, gg, bg = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:6])
SAT_MAX = 0.22
gain = np.array([rg, gg, bg])
head, rows = [], []
for line in open(src):
    p = line.split()
    if len(p) == 3:
        try:
            rows.append([float(x) for x in p]); continue
        except ValueError:
            pass
    head.append(line)
a = np.array(rows)
mx, mn = a.max(1), a.min(1)
sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
w = np.clip(1 - sat / SAT_MAX, 0, 1)[:, None] * np.clip((mx - 0.35) / 0.25, 0, 1)[:, None]  # bright neutrals only
a = np.clip(a * (1 + w * (gain - 1)), 0, 1)
with open(dst, "w") as fh:
    fh.writelines(head)
    for r in a:
        fh.write(f"{r[0]:.6f} {r[1]:.6f} {r[2]:.6f}\n")
