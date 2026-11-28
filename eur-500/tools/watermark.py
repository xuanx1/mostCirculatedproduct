"""
The watermark, recovered from the scan itself.

The ECB describes the EUR 500 watermark as the main motif (a window) and the value, seen against
the light in the blank area on the left of the front. The reflected-light scan still shows it
faintly: a window grid in perspective with "500" below it. This tool lifts that faint image out
of the original (not upscaled) scan, so the motif, its proportions and its position are the real
ones, and turns it into a soft grey layer the page can show:

  1. lightness of the blank area; the overprinted letters this scan carries across its lower right
     (warm grey, with a white rim) are masked and filled from the paper around them. Unlike other
     print they are not faded out of the layer afterwards, so no trace of their outline is left;
  2. the paper's slow shading is removed (large blur subtracted), JPEG noise smoothed
     (non-local means), so only the watermark's own light/dark modelling is left;
  3. darker-than-paper areas become a warm grey with matching alpha, faded out at the frame edge.

Writes assets/layers/watermark-ghost.png; its frame is WM_BOX (note units), read by the page
from assets/boxes.js ("watermark-ghost"). The back shows it mirrored at 720 - x - w.
Run: python tools/watermark.py   (after tools/cutouts.py, which writes boxes.js)
"""
import json, os, re
import numpy as np
import cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source', 'front-commons-944.jpg')
WM_BOX = (6, 58, 160, 186)          # x, y, w, h note units: the blank area holding window + 500
OUT_SCALE = 6                       # output px per source px (smooth, like the other layers)


def main():
    im = np.asarray(Image.open(SRC).convert('RGB'))
    H, W = im.shape[:2]
    sx, sy = W / 720, H / 320
    x, y, w, h = WM_BOX
    x0, y0, x1, y1 = int(round(x * sx)), int(round(y * sy)), int(round((x + w) * sx)), int(round((y + h) * sy))
    c = im[y0:y1, x0:x1]
    lab = cv2.cvtColor(c, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    # anything printed (letters, the flag's edge, the lavender band) is not watermark
    printed = ((L < 215) | (np.hypot(A, B) > 9)).astype(np.uint8) * 255
    printed = cv2.dilate(printed, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    # the overprinted letters (and their white rims): filled like print, but not faded out below
    over = ((np.abs(A - 4) < 9) & (np.abs(B - 10) < 10) & (L > 70) & (L < 175)).astype(np.uint8) * 255
    n, lab_, st, _ = cv2.connectedComponentsWithStats(over, 8)
    over = np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > 60)[0]).astype(np.uint8) * 255
    over = cv2.dilate(over, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    L8 = np.clip(L, 0, 255).astype(np.uint8)
    L8 = cv2.inpaint(L8, printed | over, 6, cv2.INPAINT_TELEA)
    printed[over > 0] = 0
    up = cv2.resize(L8, (c.shape[1] * OUT_SCALE, c.shape[0] * OUT_SCALE), interpolation=cv2.INTER_CUBIC)
    up = cv2.fastNlMeansDenoising(up, None, h=9, templateWindowSize=7, searchWindowSize=31)
    up = up.astype(np.float32)
    bg = cv2.GaussianBlur(up, (0, 0), 16 * OUT_SCALE)
    d = cv2.GaussianBlur(up - bg, (0, 0), 0.9 * OUT_SCALE)
    dark = np.clip(-d / 9.0, 0, 1) ** 0.85                 # thicker paper: the lines and the numeral
    pm = cv2.resize(printed, (up.shape[1], up.shape[0]), interpolation=cv2.INTER_NEAREST)
    dark *= 1 - cv2.GaussianBlur((pm > 0).astype(np.float32), (0, 0), 3 * OUT_SCALE) * 0.85
    # fade at the frame edge, so no box shows
    hh, ww = dark.shape
    yy, xx = np.mgrid[0:hh, 0:ww]
    e = np.minimum.reduce([xx, ww - 1 - xx, yy, hh - 1 - yy]).astype(np.float32)
    dark *= np.clip(e / (6 * OUT_SCALE), 0, 1)
    rgba = np.zeros((hh, ww, 4), np.uint8)
    rgba[..., :3] = (92, 78, 104)                          # a warm violet grey, like light through the paper
    rgba[..., 3] = (np.clip(dark, 0, 1) * 255).astype(np.uint8)
    out = os.path.join(ROOT, 'assets', 'layers', 'watermark-ghost.png')
    Image.fromarray(rgba, 'RGBA').resize((ww // 2, hh // 2), Image.LANCZOS).save(out, optimize=True)
    # record the frame (exact pixel box, in note units) in boxes.js
    bpath = os.path.join(ROOT, 'assets', 'boxes.js')
    txt = open(bpath, encoding='utf8').read()
    boxes = json.loads(re.search(r'const BOXES = (\{.*\});', txt, re.S).group(1))
    boxes['watermark-ghost'] = [round(x0 / sx, 3), round(y0 / sy, 3), round((x1 - x0) / sx, 3), round((y1 - y0) / sy, 3)]
    open(bpath, 'w', encoding='utf8').write(txt.split('const BOXES')[0] + 'const BOXES = ' + json.dumps(boxes, indent=1) + ';\n')
    print('watermark ->', out, boxes['watermark-ghost'])


if __name__ == '__main__':
    main()
