"""
The Onyx cowrie as its own line-work: the same detection the gold colour-flow uses (printed lines
darker than their surroundings), at full resolution, clipped to the shell outline, with the
overprinted serial digits removed.

Writes:
  assets/layers/front-cowrie-lines.png   gold lines on transparent (page highlight / exploded view)
  feature-crops/front/cowrie.png         the extracted lines in their printed colours
  feature-crops/front/cowrie-ink.png     same as cowrie.png
Run: python tools/cowrie_lines.py
"""
import os, sys
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_features as EF  # noqa: E402

ROOT = EF.ROOT
BOX = (562, 0, 118, 114)                                   # x, y, w, h in note units (page frame)
SERIAL = (664, 62, 26, 156)                                # vertical serial (removed from the lines)
# the visible part of the shell: its oval edge on the right, the portrait's hair on the lower left
OUTLINE = [(568, 0), (671, 0), (675, 14), (675, 30), (672, 45), (667, 60), (660, 75), (652, 88),
           (643, 100), (636, 108), (634, 100), (632, 84), (629, 66), (621, 50), (610, 38), (598, 27),
           (584, 14)]


def main():
    im = Image.open(os.path.join(ROOT, EF.SRC['front'])).convert('RGB')
    W, H = im.size
    sx, sy = W / EF.VB_W, H / EF.VB_H
    k = W / 1080                                            # the flow mask is made at 1080 px wide
    x, y, w, h = BOX
    box = (int(x * sx), int(y * sy), int((x + w) * sx), int((y + h) * sy))
    rgb = np.asarray(im.crop(box))
    hh, ww = rgb.shape[:2]
    px = lambda X, Y: (int(round((X - x) * sx)), int(round((Y - y) * sy)))

    L = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    r = max(1, int(round(4 * k)))
    bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))), (0, 0), 3 * k)
    lines = (bg - L - 8) > 0                                 # same rule as the colour-flow mask
    # the shell is printed in pale gold: keep yellowish print, drop the dark hair engraving
    B = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 2].astype(np.float32)
    lines &= (B > np.percentile(B, 20) + 4) & (L > 150)

    # remove the serial digits printed over the shell
    sb = np.zeros((hh, ww), bool)
    a0, b0 = px(SERIAL[0], SERIAL[1]); a1, b1 = px(SERIAL[0] + SERIAL[2], SERIAL[1] + SERIAL[3])
    sb[max(0, b0):b1, max(0, a0):a1] = True
    digits = cv2.dilate(((L < 150) & sb).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    lines &= ~digits

    # clip to the shell
    shell = np.zeros((hh, ww), np.uint8)
    cv2.fillPoly(shell, [np.array([px(a, b) for a, b in OUTLINE], np.int32)], 255)
    lines &= shell > 0
    # drop isolated specks
    n, lab, st, _ = cv2.connectedComponentsWithStats(lines.astype(np.uint8), 8)
    keep = np.zeros_like(lines)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 12:
            keep |= lab == i
    alpha = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 0.6)
    alpha = np.clip(alpha * 1.6, 0, 1)

    a8 = (alpha * 255).astype(np.uint8)
    ink = Image.fromarray(np.dstack([rgb, a8]), 'RGBA')
    gold = np.empty((hh, ww, 3), np.uint8); gold[...] = (168, 120, 31)
    page = Image.fromarray(np.dstack([gold, a8]), 'RGBA')
    kpage = 1440 / W * 1.5
    page.resize((round(ww * kpage), round(hh * kpage)), Image.LANCZOS).save(
        os.path.join(ROOT, 'assets', 'layers', 'front-cowrie-lines.png'), optimize=True)
    bb = ink.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    crop = ink.crop((max(0, bb[0] - 12), max(0, bb[1] - 12), min(ww, bb[2] + 12), min(hh, bb[3] + 12)))
    os.makedirs(os.path.join(EF.OUT, 'front'), exist_ok=True)
    crop.save(os.path.join(EF.OUT, 'front', 'cowrie.png'), optimize=True)
    crop.save(os.path.join(EF.OUT, 'front', 'cowrie-ink.png'), optimize=True)
    print(f'cowrie lines: {int(keep.sum())} px of line-work, frame {list(BOX)}')


if __name__ == '__main__':
    main()
