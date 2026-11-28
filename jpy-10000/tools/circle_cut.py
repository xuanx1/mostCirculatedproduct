"""
Round seals are cut as exact circles: the seal's printed extent (by colour or darkness) gives the
smallest enclosing circle, and everything inside it is kept. No edge guessing.

  python tools/circle_cut.py            (cuts both seals)
"""
import os, sys
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_features as EF  # noqa: E402

ROOT = EF.ROOT
# id: (centre x, centre y, radius) in note units, and how the seal's ink is told apart
SEALS = {
    'seal': ((251, 246.5, 33), 'red'),     # the Governor's seal (総裁之印), printed in vermilion
}


def cut(fid, geom, kind):
    im = Image.open(os.path.join(ROOT, EF.SRC['front'])).convert('RGB')
    W, H = im.size
    sx, sy = W / EF.VB_W, H / EF.VB_H
    cx, cy, r = geom
    x0, y0, x1, y1 = cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6
    box = (int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy))
    crop = np.asarray(im.crop(box))
    # find the seal's outer circle directly (Hough), near the expected centre and size
    gray = cv2.GaussianBlur(cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY), (0, 0), 2)
    ecx, ecy, er = (cx - x0) * sx, (cy - y0) * sy, r * (sx + sy) / 2
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=10, param1=120, param2=40,
                               minRadius=int(er * 0.75), maxRadius=int(er * 1.1))
    cands = [] if circles is None else circles[0]
    cands = [c for c in cands if np.hypot(c[0] - ecx, c[1] - ecy) < er * 0.25]
    ccx, ccy, rad = max(cands, key=lambda c: c[2]) if cands else (ecx, ecy, er * 0.95)
    if kind in ('green', 'red'):        # centre and radius from the seal's own colour
        lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB).astype(np.float32)
        dev = (np.median(lab[..., 1]) - lab[..., 1]) if kind == 'green' else (lab[..., 1] - np.median(lab[..., 1]))
        gm = (dev > 18).astype(np.uint8)
        gm = cv2.morphologyEx(gm, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        ys, xs = np.nonzero(gm)
        ccx, ccy = np.median(xs), np.median(ys)
        # the printed ring's outer edge: per direction, the outermost seal-coloured pixel within reach of the
        # expected circle; a least-squares circle through those points gives the exact centre and radius
        # (the characters inside would bias a centre taken from all the ink)
        pts = []
        ang_all = np.arctan2(ys - ccy, xs - ccx); rr = np.hypot(xs - ccx, ys - ccy)
        for k in range(360):
            a0 = np.deg2rad(k - 180)
            sel = (np.abs(np.angle(np.exp(1j * (ang_all - a0)))) < np.deg2rad(0.6)) & (rr < er * 1.12)
            if sel.sum():
                q = np.argmax(np.where(sel, rr, -1)); pts.append((xs[q], ys[q]))
        P = np.array(pts, np.float64)
        for _ in range(3):                                  # fit, drop outliers, refit
            A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
            cx_, cy_, c_ = np.linalg.lstsq(A, (P ** 2).sum(1), rcond=None)[0]
            r_ = np.sqrt(c_ + cx_ ** 2 + cy_ ** 2)
            d = np.abs(np.hypot(P[:, 0] - cx_, P[:, 1] - cy_) - r_)
            P = P[d < max(2.0, np.percentile(d, 85))]
        ccx, ccy, rad = cx_, cy_, r_
    ink = gray
    m = np.zeros(ink.shape, np.uint8)
    cv2.circle(m, (int(round(ccx)), int(round(ccy))), int(round(rad + (0.5 if kind in ('green', 'red') else 1.5))), 255, -1, lineType=cv2.LINE_AA)
    a = m.astype(np.float32) / 255
    out = Image.fromarray(np.dstack([crop, (a * 255).astype(np.uint8)]), 'RGBA')
    bb = out.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    pres = out.crop((max(0, bb[0] - 12), max(0, bb[1] - 12), min(out.width, bb[2] + 12), min(out.height, bb[3] + 12)))
    pres.save(os.path.join(EF.OUT, 'front', f'{fid}.png'), optimize=True)
    ink_png = os.path.join(EF.OUT, 'front', f'{fid}-ink.png')
    if os.path.exists(ink_png):
        os.remove(ink_png)
    # page layer, framed to the box the page uses
    shape, g = next((rr[3], rr[4]) for rr in EF.REGIONS if (rr[1], rr[0]) == ('front', fid))
    (px0, py0, px1, py1), _ = EF.bbox(shape, g, EF.PAD)
    frame = Image.new('RGBA', (int(round((px1 - px0) * sx)), int(round((py1 - py0) * sy))), (0, 0, 0, 0))
    frame.alpha_composite(out, (int(round((x0 - px0) * sx)), int(round((y0 - py0) * sy))))
    kk = 1440 / W * 1.5
    frame = frame.resize((round(frame.width * kk), round(frame.height * kk)), Image.LANCZOS)
    for name in (f'front-{fid}-cut.png', f'front-{fid}.png'):
        frame.save(os.path.join(ROOT, 'assets', 'layers', name), optimize=True)
    print(f'{fid}: circle radius {rad / sx:.1f} note units')


if __name__ == '__main__':
    for fid, (geom, kind) in SEALS.items():
        cut(fid, geom, kind)
