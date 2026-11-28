"""
Pearl ink (パールインキ). Official: tilt the note and a pink sheen shows in the blank margins at its left
and right ends (BOJ security.htm, NPB design10). The ink is a clear pearlescent coat, invisible in a
flat photo, so its extent is drawn from the BOJ's diagram (security1.png box (6), security9.png): a
band down each end, from the outer edge to the print, over the middle of the note's height.
Illustrative extent. Writes assets/layers/pearl-mask.png (box PEARL_BOX, both bands, soft edges).
Run: python tools/pearl.py
"""
import os
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PEARL_BOX = (0, 70, 720, 176)                 # note units: x, y, w, h (the mask covers both ends)
BANDS = [(2, 76, 60, 162), (654, 76, 64, 162)]  # left and right bands, note units
PX = 2                                        # 2 px per note unit


def main():
    bx, by, bw, bh = PEARL_BOX
    W, H = bw * PX, round(bh * PX * (684 / 320) / 2)     # y units are taller on the 160 x 76 mm note
    sy = H / bh
    m = np.zeros((H, W), np.float32)
    for x, y, w, h in BANDS:
        cv2.rectangle(m, (int((x - bx) * PX), int((y - by) * sy)), (int((x + w - bx) * PX), int((y + h - by) * sy)), 1, -1)
    m = cv2.GaussianBlur(m, (0, 0), 5 * PX)
    a = (np.clip(m, 0, 1) * 255).astype(np.uint8)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., :3] = 255; rgba[..., 3] = a
    Image.fromarray(rgba, 'RGBA').save(os.path.join(ROOT, 'assets', 'layers', 'pearl-mask.png'), optimize=True)
    # the glow piece shown when the feature is highlighted: a soft pink sheen in the same bands
    g = np.zeros((H, W, 4), np.uint8); g[..., 0], g[..., 1], g[..., 2] = 246, 160, 196; g[..., 3] = (a * 0.55).astype(np.uint8)
    Image.fromarray(g, 'RGBA').save(os.path.join(ROOT, 'assets', 'layers', 'front-pearl.png'), optimize=True)
    print('pearl mask', W, H)


if __name__ == '__main__':
    main()
