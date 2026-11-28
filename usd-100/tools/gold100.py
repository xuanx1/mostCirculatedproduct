"""
The large gold 100 on the back, cut cleanly:
  digits  = blue outline + gold fill (by colour), holes filled except the counters of the 0s,
            which stay open (they are paper);
  halo    = the cream border printed around the digits (also inside the counters), grown as an even
            band from the clean digits rather than thresholded from the paper, so its edge is smooth.
Original pixels are kept. Writes feature-crops/back/gold-100.png, assets/layers/back-gold-100(-cut).png
and the box in assets/boxes.js.   Run: python tools/gold100.py
"""
import os, re, json
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (566, 34, 122, 246)        # note units: x, y, w, h (the whole numeral with its halo)
HALO = 3.2                       # cream border width, note units


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def main():
    im = Image.open(os.path.join(ROOT, 'usd-100-back.png')).convert('RGB')
    W, H = im.size; sx, sy = W / 720, H / 320
    x, y, w, h = BOX
    box = (round(x * sx), round(y * sy), round((x + w) * sx), round((y + h) * sy))
    rgb = np.asarray(im.crop(box))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    A, B = lab[..., 1] - 128, lab[..., 2] - 128
    blue = B < -22
    gold = (B > 28) & (A > 0)
    ink = ((blue | gold) * 255).astype(np.uint8)
    ink = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, disk(0.5 * sx))
    # keep the three digits (largest parts)
    n, lab_, st, _ = cv2.connectedComponentsWithStats(ink, 8)
    big = st[1:, cv2.CC_STAT_AREA].max()
    ink = np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > big * 0.2)[0]).astype(np.uint8) * 255
    # fill small gaps, keep the counters (large holes) open
    ff = ink.copy(); cv2.floodFill(ff, np.zeros((ink.shape[0] + 2, ink.shape[1] + 2), np.uint8), (0, 0), 255)
    holes = (~ff) & 255
    n, lab_, st, _ = cv2.connectedComponentsWithStats(holes, 8)
    small = np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] < (8 * sx) ** 2)[0])
    digits = ink.copy(); digits[small] = 255
    halo = cv2.dilate(digits, disk(HALO * sx))
    a = cv2.GaussianBlur(halo.astype(np.float32) / 255, (0, 0), 0.9)
    a = np.clip((a - 0.5) * 2.2 + 0.5, 0, 1)
    out = Image.fromarray(np.dstack([rgb, (a * 255).astype(np.uint8)]), 'RGBA')
    out.crop(out.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()) \
        .save(os.path.join(ROOT, 'feature-crops', 'back', 'gold-100.png'), optimize=True)
    kx, ky = 1440 / 720 * 1.5, 612 / 320 * 1.5
    page = out.resize((round(w * kx), round(h * ky)), Image.LANCZOS)
    for n_ in ('back-gold-100.png', 'back-gold-100-cut.png'):
        page.save(os.path.join(ROOT, 'assets', 'layers', n_), optimize=True)
    p = os.path.join(ROOT, 'assets', 'boxes.js'); s = open(p, encoding='utf8').read()
    s = re.sub(r'"back-gold-100": \[[^\]]*\]', '"back-gold-100": ' + json.dumps(list(BOX)), s)
    open(p, 'w', encoding='utf8').write(s)
    print('gold-100', page.size, 'box', BOX)


if __name__ == '__main__':
    main()
