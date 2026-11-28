"""
A clean €500 watermark, keeping the real one's geometry. Run after tools/watermark.py.

tools/watermark.py lifts the watermark from the 944 px scan: the shapes are real (a window grid in slight
perspective, "500" below it) but the layer is mostly scan noise. Here:
  - the window's straight lines are read off that recovered image (GRID) and drawn again as even, soft
    watermark lines;
  - the "500" is drawn in the note's own printed "500" (cut by colour from the front's lower left), placed and
    sized on the recovered figures (their proportions match: 1.98 : 1).
The result replaces assets/layers/watermark-ghost.png (same frame) and feature-crops/<side>/watermark.png.
Run: python tools/watermark_clean.py
"""
import os
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYER = os.path.join(ROOT, 'assets', 'layers', 'watermark-ghost.png')
NUMERAL = os.path.join(ROOT, 'assets', 'layers', 'front-numeral-cut.png')
RAW = os.path.join(ROOT, 'source', 'watermark-recovered.png')     # watermark.py's output, kept for re-runs
NUM_ZONE = 0.76            # below this fraction of the height: the "500"
# the window's lines as read on the recovered layer (630 x 843 px): slight perspective, as in the scan
GRID = [((95, 62), (110, 608)),            # left upright, full height
        ((218, 112), (238, 440)),          # middle upright
        ((396, 312), (408, 560)),          # right upright, lower half
        ((100, 112), (330, 128)),          # top rail
        ((120, 322), (490, 318)),          # middle rail
        ((120, 434), (470, 412)),          # lower rail
        ((180, 610), (470, 582))]          # sill


def main():
    if not os.path.exists(RAW) or os.path.getmtime(LAYER) > os.path.getmtime(RAW) + 1:
        Image.open(LAYER).save(RAW)                                  # keep the recovered (noisy) layer
    src = np.asarray(Image.open(RAW).convert('RGBA')).astype(np.float32)
    H, W = src.shape[:2]
    a = src[..., 3] / 255
    colour = np.median(src[..., :3][a > 0.3], 0)
    n = cv2.GaussianBlur(a, (0, 0), 3)
    n = n / max(n.max(), 1e-6)
    # ---- the grid: the window's lines, read off the recovered image (px of this 630 x 843 layer) ----
    stroke = np.zeros((H, W), np.float32)
    lw = max(6, int(W * 0.022))
    for (x1, y1), (x2, y2) in GRID:
        cv2.line(stroke, (round(x1 * W / 630), round(y1 * H / 843)), (round(x2 * W / 630), round(y2 * H / 843)), 1.0, lw, cv2.LINE_AA)
    stroke = cv2.GaussianBlur(stroke, (0, 0), lw * 0.45) * 0.7            # a watermark's soft line
    # ---- the "500": the recovered figures mark where it sits; its shape is the note's own printed "500"
    # (lower left of the front, cut by colour into source/watermark-500-shape.png: same typeface, same
    # 1.98 : 1 proportions as the recovered figures), fitted onto their box ----
    num = np.zeros((H, W), np.float32)
    z0 = int(H * NUM_ZONE)
    zone = cv2.GaussianBlur(a, (0, 0), 4)[z0:]
    zone = (zone / max(zone.max(), 1e-6) > 0.42).astype(np.uint8)
    zone[:, :int(W * 0.2)] = 0; zone[:, int(W * 0.75):] = 0
    ys, xs = np.nonzero(zone)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min() + z0, ys.max() + z0
    shape = Image.open(os.path.join(ROOT, 'source', 'watermark-500-shape.png')).convert('L')
    bw = bx1 - bx0 + 1; bh = round(bw * shape.height / shape.width)            # keep its proportions
    cy = (by0 + by1) // 2
    sh = np.asarray(shape.resize((bw, bh), Image.LANCZOS), np.float32) / 255
    top = max(0, cy - bh // 2)
    num[top:top + bh, bx0:bx0 + bw] = sh[:H - top]
    num = cv2.GaussianBlur(num, (0, 0), 1.4) * 0.8
    print('500 placed at', (int(bx0), int(top), int(bw), int(bh)))
    # ---- fade at the frame edge, as before ----
    yy, xx = np.mgrid[:H, :W]
    d = np.maximum(np.abs(xx - W / 2) / (W / 2), np.abs(yy - H / 2) / (H / 2))
    fade = np.clip((1 - d) / 0.08, 0, 1)
    alpha = np.clip(np.maximum(stroke, num), 0, 1) * fade * (src[..., 3].max() / 255)
    out = np.dstack([np.broadcast_to(colour, (H, W, 3)), alpha * 255]).astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')
    img.save(LAYER, optimize=True)
    big = img.resize((W * 2, H * 2), Image.LANCZOS)
    for side, im in (('front', big), ('back', big.transpose(Image.FLIP_LEFT_RIGHT))):
        im.save(os.path.join(ROOT, 'feature-crops', side, 'watermark.png'), optimize=True)
    print('watermark-ghost rebuilt', img.size)


if __name__ == '__main__':
    main()
