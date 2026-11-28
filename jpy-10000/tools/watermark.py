"""
The watermarks, rebuilt as the page's paper layer (they are formed in the paper, so a reflected-light
photo does not show them). Official (BOJ security.htm, NPB design10):
  - the portrait watermark of Shibusawa Eiichi in the blank oval, plus the high-definition watermark:
    a continuous pattern of fine lines around the portrait, a diamond motif on the ¥10,000;
  - the bar-pattern watermark: three vertical bars on the ¥10,000.
The portrait is the note's own engraved portrait (cut by tools/sam_isolate.py), turned into the soft,
continuous tone a mould-made watermark has. The diamond pattern and the bars are drawn from the BOJ's
pictures of them (security4.png, security5.png): illustrative in size and spacing.
Writes assets/layers/watermark-ghost.png (box GHOST) and assets/layers/watermark-bars.png (box BARS).
Run after sam_isolate.py:  python tools/watermark.py
"""
import os
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, 'assets', 'layers')
GHOST = (313, 62, 158, 171)          # note units: exactly the printed ring's inside (measured: centre 392, 147.5; inner radii 79 x 85.5)
BARS = (619, 124, 36, 64)            # right of the portrait, left of the right identification mark
PORTRAIT_BOX = (414, 38, 240, 240)   # assets/boxes.js front-portrait frame (before PAD)
MM = 22.5                            # artwork px per mm (3600 px / 160 mm)
SEPIA = (96, 78, 58)


def page_px(box):                    # page layers: 1.5x the 1440 x 684 face
    return round(box[2] * 3), round(box[3] * 3 * 684 / 640)


def ghost():
    art = Image.open(os.path.join(ROOT, 'jpy-10000-front.png')).convert('L')
    W, H = art.size; sx, sy = W / 720, H / 320
    gw, gh = round(GHOST[2] * sx), round(GHOST[3] * sy)                 # artwork px (isotropic)
    # the engraved portrait and its silhouette (SAM cut, framed on the PAD box)
    cut = Image.open(os.path.join(LAYERS, 'front-portrait-cut.png'))
    px0, py0 = PORTRAIT_BOX[0] - 4, PORTRAIT_BOX[1] - 4
    pw, ph = PORTRAIT_BOX[2] + 8, PORTRAIT_BOX[3] + 8
    sil = np.asarray(cut.getchannel('A').resize((round(pw * sx), round(ph * sy)), Image.LANCZOS), np.float32) / 255
    lum = np.asarray(art.crop((round(px0 * sx), round(py0 * sy), round(px0 * sx) + sil.shape[1], round(py0 * sy) + sil.shape[0])), np.float32)
    ys, xs = np.nonzero(sil > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    lum, sil = lum[y0:y1, x0:x1], sil[y0:y1, x0:x1]
    # scale: head near the top of the oval, shoulders running out at its foot (proportions kept)
    k = gh * 0.88 / lum.shape[0]
    lum = cv2.resize(lum, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    sil = cv2.resize(sil, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    tone = np.zeros((gh, gw), np.float32); mask = np.zeros((gh, gw), np.float32)
    # centre the HEAD in the oval (the shoulders are not symmetric, so the whole bust is not the reference)
    top = sil[: int(sil.shape[0] * 0.45)]
    hx = (np.arange(top.shape[1])[None, :] * top).sum() / max(top.sum(), 1)
    ox = int(round(gw / 2 - hx)); oy = round(0.09 * gh)
    ty0, sy0 = max(0, oy), max(0, -oy)
    hh = min(gh - ty0, lum.shape[0] - sy0)
    tx0, sx0 = max(0, ox), max(0, -ox)
    ww = min(gw - tx0, lum.shape[1] - sx0)
    tone[:] = 255
    tone[ty0:ty0 + hh, tx0:tx0 + ww] = lum[sy0:sy0 + hh, sx0:sx0 + ww]
    mask[ty0:ty0 + hh, tx0:tx0 + ww] = sil[sy0:sy0 + hh, sx0:sx0 + ww]
    # engraving lines -> continuous tone (a watermark has no line-work)
    tone = cv2.GaussianBlur(tone, (0, 0), 0.35 * MM)
    paper = np.percentile(tone[mask > 0.5], 97)
    dark = np.clip((paper - tone) / max(paper - np.percentile(tone[mask > 0.5], 3), 1), 0, 1) ** 0.85
    mask = cv2.GaussianBlur(mask, (0, 0), 0.5 * MM)
    portrait = dark * mask
    # the high-definition pattern: a lattice of fine diamonds with fine horizontal lines, around the portrait
    yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
    cw, ch = 3.0 * MM, 2.8 * MM
    u = (xx / cw + yy / ch); v = (xx / cw - yy / ch)
    line = lambda t: np.clip(1 - np.abs(t - np.round(t)) * (cw / (0.16 * MM)), 0, 1)   # ~0.16 mm wide lines
    lattice = np.maximum(line(u), line(v))
    hatch = 0.35 * np.clip(1 - np.abs((yy / (0.3 * MM)) % 1 - 0.5) * 6, 0, 1)
    pattern = np.maximum(lattice * 0.4, hatch * 0.4) * (1 - np.clip(mask * 1.6, 0, 1))
    # the oval: everything fades out at its edge
    d = np.sqrt(((xx - gw / 2) / (gw / 2)) ** 2 + ((yy - gh / 2) / (gh / 2)) ** 2)
    fade = np.clip((1 - d) / 0.03, 0, 1); fade = fade * fade * (3 - 2 * fade)    # a short fade: it fills the oval to the ring
    alpha = np.clip(portrait, 0, 1) * fade          # the portrait only: the drawn diamond lattice is left out (it was illustrative)
    rgba = np.zeros((gh, gw, 4), np.uint8); rgba[..., :3] = SEPIA; rgba[..., 3] = (alpha * 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').resize(page_px(GHOST), Image.LANCZOS).save(os.path.join(LAYERS, 'watermark-ghost.png'), optimize=True)
    # presentation copies (full resolution): front, and the reverse (the same watermark, mirrored)
    full = Image.fromarray(rgba, 'RGBA')
    for side, im in (('front', full), ('back', full.transpose(Image.FLIP_LEFT_RIGHT))):
        im.save(os.path.join(ROOT, 'feature-crops', side, 'watermark.png'), optimize=True)
        stale = os.path.join(ROOT, 'feature-crops', side, 'watermark-ink.png')
        if os.path.exists(stale):
            os.remove(stale)
    print('watermark-ghost', page_px(GHOST))


def bars():
    sx, sy = 3600 / 720, 1710 / 320
    w, h = round(BARS[2] * sx), round(BARS[3] * sy)
    a = np.zeros((h, w), np.float32)
    bw, gap = 1.6 * MM, 1.25 * MM
    x0 = (w - (3 * bw + 2 * gap)) / 2
    for i in range(3):
        xa = x0 + i * (bw + gap)
        cv2.rectangle(a, (round(xa), round(0.06 * h)), (round(xa + bw), round(0.94 * h)), 1, -1)
    a = cv2.GaussianBlur(a, (0, 0), 0.18 * MM)
    # bars are thinner paper: lighter against the light; a sepia rim lets them read on the cream paper
    rim = np.clip(cv2.GaussianBlur(a, (0, 0), 0.25 * MM) - a * 0.85, 0, 1) * 1.6
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = a[..., None] * np.array([255, 253, 246]) + (1 - a[..., None]) * np.array(SEPIA)
    rgba[..., 3] = np.clip(np.maximum(a * 0.9, rim), 0, 1) * 255
    Image.fromarray(rgba.astype(np.uint8), 'RGBA').resize(page_px(BARS), Image.LANCZOS).save(os.path.join(LAYERS, 'watermark-bars.png'), optimize=True)
    print('watermark-bars', page_px(BARS))


if __name__ == '__main__':
    ghost()
    bars()
