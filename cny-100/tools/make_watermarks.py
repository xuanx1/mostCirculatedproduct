"""
The ¥100's paper features that a reflected-light image does not show, rebuilt from PBC's own images.

  python tools/make_watermarks.py        (after tools/extract_features.py and tools/sam_isolate.py)

1. Portrait watermark (人像水印). PBC: "位于票面正面左侧空白处. 透光观察, 可见毛泽东头像水印".
   Its position and size come from PBC's own transmitted-light animation of it
   (pbc.gov.cn/rmyh/xbrmb/imgs/shuiyin.gif, in source/pbc/): the animation was registered to the
   front image by template matching (scale 1.78, offset 0,205 in front-l.jpg pixels), and the engraved
   portrait was then fitted to the watermark face in it (normalised correlation 0.83): the
   watermark is the portrait at 0.66 of its size, at  x' = 0.66 x - 225.2,  y' = 0.66 y + 70.0
   (note units). The ghost is rebuilt from the engraved portrait (its own head silhouette, from the
   Segment Anything cut), blurred to continuous tone, as a mould-made watermark looks.
2. White watermark "100" (白水印). PBC: "位于票面正面横号码下方. 透光观察, 可以看到透光性很强的
   水印面额数字'100'". Its place and size come from PBC's animation of it (source/pbc/baishuiyin.gif,
   registered at scale 1.08, offset 170,579). The figures are clean geometry fitted to that image: each
   "0" the ellipse through the middle of its bright ring, the "1" a stem plus flag, one measured stroke
   width, drawn at 8x and reduced, so the edges are smooth and the counters open (see white_watermark).
3. See-through numeral (胶印对印图案): the offset that brings the reverse pieces, mirrored, onto the
   obverse pieces so that together they close into a complete "100" (printed; used in data.js).

Writes assets/layers/watermark-ghost.png, assets/layers/white-watermark.png and prints the boxes.
"""
import os
import numpy as np
import cv2
from PIL import Image, ImageSequence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, 'assets', 'layers')
PXU_X, PXU_Y = 1440 / 720 * 1.5, 715 / 320 * 1.5        # page-layer pixels per note unit
FIT = (0.66, -225.2, 70.0)                              # watermark = portrait * s + (ox, oy)
HEAD = (378, 8, 582, 228)                             # portrait crop used for the watermark (note units)


def boxes():
    d = {}
    for line in open(os.path.join(ROOT, 'assets', 'boxes.js'), encoding='utf8').read().split('const BOXES = ')[1:]:
        import json
        d = json.loads(line.strip().rstrip(';'))
    return d


def portrait_ghost():
    s, ox, oy = FIT
    x0, y0, x1, y1 = HEAD
    front = Image.open(os.path.join(ROOT, 'cny-100-front.png')).convert('RGB')
    sx, sy = front.width / 720, front.height / 320
    crop = np.asarray(front.crop((int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy))), np.float32)
    # the portrait's own silhouette (the Segment Anything cut), so the guilloche behind it is not used
    bx = boxes()['front-portrait']
    cut = Image.open(os.path.join(LAYERS, 'front-portrait-cut.png')).getchannel('A')
    full = Image.new('L', (round(bx[2] * sx), round(bx[3] * sy)), 0)
    full.paste(cut.resize(full.size, Image.LANCZOS))
    m = np.asarray(full.crop((round((x0 - bx[0]) * sx), round((y0 - bx[1]) * sy),
                              round((x1 - bx[0]) * sx), round((y1 - bx[1]) * sy))), np.float32) / 255
    m = cv2.resize(m, (crop.shape[1], crop.shape[0]))
    W, H = round((x1 - x0) * s * PXU_X), round((y1 - y0) * s * PXU_Y)
    lum = crop @ np.array([.299, .587, .114], np.float32)
    lum = cv2.resize(lum, (W, H), interpolation=cv2.INTER_AREA)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA)
    lum = cv2.GaussianBlur(lum, (0, 0), W / 150)          # engraved lines -> continuous tone
    inside = m > 0.5
    lo, hi = np.percentile(lum[inside], 2), np.percentile(lum[inside], 99)
    t = np.clip((hi - lum) / max(hi - lo, 1), 0, 1) ** 0.9 * 0.85 + 0.15   # the head itself reads, darker where shaded
    m = cv2.GaussianBlur(m, (0, 0), W / 60)                # the silhouette melts into the paper
    yy, xx = np.mgrid[0:H, 0:W]
    fade = np.clip((H * 0.98 - yy) / (H * 0.22), 0, 1)     # shoulders fade out
    fade = fade * fade * (3 - 2 * fade)
    a = t * m * fade
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (98, 84, 78)
    rgba[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(LAYERS, 'watermark-ghost.png'), optimize=True)
    box = [round(x0 * s + ox, 2), round(y0 * s + oy, 2), round((x1 - x0) * s, 2), round((y1 - y0) * s, 2)]
    print('watermark-ghost', (W, H), 'box', box)


def white_watermark():
    """The white "100" as clean geometry fitted to PBC's transmitted-light image of it.
    PBC's animation (240 x 200 px) shows a light monoline numeral: a "1" with a short flag and two oval
    "0"s with open counters. No printed 100 on the note has that figure style (the colour-shifting 100
    and the corner numerals are bold high-contrast serifs), so the figures are not borrowed from the
    print: each "0" is the ellipse fitted to the bright ring's outer and inner edges in the animation,
    the "1" is a straight stem plus flag fitted to its bright pixels, all at one measured stroke width.
    They are drawn as vector strokes at 8x and reduced (smooth anti-aliased edges), then very lightly
    softened, in a warm off-white at partial opacity (a bright watermark, not a white print).
    The frame and its place on the note are the ones measured from the animation (unchanged)."""
    fr = [np.asarray(f.convert('L')).astype(np.float32) for f in ImageSequence.Iterator(Image.open(
        os.path.join(ROOT, 'source', 'pbc', 'baishuiyin.gif')))]
    g = np.mean(fr[3:], axis=0)                            # the frames against the light
    bg = cv2.medianBlur(g.astype(np.uint8), 21).astype(np.float32)
    d = g - bg
    d[:50] = 0; d[:, :35] = 0; d[140:] = 0; d[:, 172:] = 0
    ys, xs = np.where(d > 25)
    gx0, gx1, gy0, gy1 = xs.min() - 4, xs.max() + 5, ys.min() - 4, ys.max() + 5
    k, ox, oy = 1.08, 170, 579                             # gif -> front-l.jpg pixels (registration)
    n = lambda X, Y: ((ox + X * k - 2) / 1595 * 720, (oy + Y * k - 2) / 791 * 320)
    (bx0, by0), (bx1, by1) = n(gx0, gy0), n(gx1, gy1)
    W, H = round((bx1 - bx0) * PXU_X * 2), round((by1 - by0) * PXU_Y * 2)
    sx, sy = W / (gx1 - gx0), H / (gy1 - gy0)              # gif px -> layer px

    # ---- fit the figures in gif pixels
    m = (cv2.GaussianBlur(d, (0, 0), 0.8) > 18).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    nl, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    comps = [i for i in range(1, nl) if st[i, cv2.CC_STAT_AREA] > 120]
    comps.sort(key=lambda i: st[i, cv2.CC_STAT_LEFT])
    one = comps[0]
    zeros = [[c for c in comps[1:] if st[c, cv2.CC_STAT_LEFT] < 128], [c for c in comps[1:] if st[c, cv2.CC_STAT_LEFT] >= 128]]
    rings, widths = [], []
    for zc in zeros:
        zm = np.isin(lab, zc).astype(np.uint8)
        zm = cv2.morphologyEx(zm, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        cs, hier = cv2.findContours(zm, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        outer = max(cs, key=cv2.contourArea)
        holes = [c for c, h in zip(cs, hier[0]) if h[3] >= 0]
        inner = max(holes, key=cv2.contourArea)
        (cxo, cyo), (wo, ho), ango = cv2.fitEllipse(outer)
        (cxi, cyi), (wi, hi), angi = cv2.fitEllipse(inner)
        widths.append(((wo - wi) + (ho - hi)) / 4)
        rings.append(((cxo + cxi) / 2, (cyo + cyi) / 2, (wo + wi) / 4, (ho + hi) / 4, (ango + angi) / 2))
    sw = float(np.mean(widths))                            # one stroke width for all three figures
    oy_, ox_ = np.nonzero(lab == one)
    top, bot = oy_.min() + sw / 2, oy_.max() - sw / 2
    stem = oy_ > top + 2.5 * sw                            # below the flag
    A = np.vstack([oy_[stem], np.ones(stem.sum())]).T
    (slope, icpt), *_ = np.linalg.lstsq(A, ox_[stem].astype(np.float64), rcond=None)
    sx_at = lambda y: slope * y + icpt
    flag = (oy_ < top + 2.5 * sw) & (ox_ < sx_at(oy_) - sw * 0.8)
    fx, fy = ox_[flag].min() + sw / 2, oy_[flag][ox_[flag] == ox_[flag].min()].mean()
    print('white-watermark fit: stroke %.2f gif px; 1 stem x=%.2f+%.3fy, %.1f..%.1f, flag to (%.1f, %.1f); 0s %s'
          % (sw, icpt, slope, top, bot, fx, fy, [tuple(round(v, 1) for v in r) for r in rings]))

    # ---- draw at 8x, reduce
    Q = 8
    cv = np.zeros((H * Q, W * Q), np.uint8)
    P = lambda X, Y: (int(round((X - gx0) * sx * Q)), int(round((Y - gy0) * sy * Q)))
    t = max(1, int(round(sw * (sx + sy) / 2 * Q)))
    for cx, cy, ax, ay, ang in rings:
        c = P(cx, cy)
        cv2.ellipse(cv, c, (int(round(ax * sx * Q)), int(round(ay * sy * Q))), ang, 0, 360, 255, t, cv2.LINE_AA)
    cv2.line(cv, P(sx_at(top), top), P(sx_at(bot), bot), 255, t, cv2.LINE_AA)
    cv2.line(cv, P(sx_at(top), top), P(fx, fy), 255, t, cv2.LINE_AA)
    a = cv2.resize(cv.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    a = cv2.GaussianBlur(a, (0, 0), 1.1)                   # a watermark's edge is soft, but smooth
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = (255, 252, 246)                        # warm paper white
    rgba[..., 3] = np.clip(a * 0.88 * 255, 0, 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(os.path.join(LAYERS, 'white-watermark.png'), optimize=True)
    print('white-watermark', (W, H), 'box', [round(bx0, 2), round(by0, 2), round(bx1 - bx0, 2), round(by1 - by0, 2)])


def register_fit():
    """Offset (note units) that puts the mirrored reverse pieces onto the obverse ones."""
    b = boxes()
    K = 8
    def load(name, mirror):
        im = Image.open(os.path.join(LAYERS, name + '.png')).getchannel('A')
        x, y, w, h = b[name]
        im = im.resize((round(w * K), round(h * K)))
        a = (np.asarray(im) > 128).astype(np.uint8)
        if mirror:
            a = a[:, ::-1]
            x = 720 - x - w
        return a, x, y
    f, fx, fy = load('front-register', False)
    r, rx, ry = load('back-register', True)
    H, W = 60 * K, 100 * K
    ox, oy = 10, 255
    def place(a, x, y, dx=0, dy=0):
        c = np.zeros((H, W), np.uint8)
        X, Y = round((x - ox + dx) * K), round((y - oy + dy) * K)
        c[Y:Y + a.shape[0], X:X + a.shape[1]] = a
        return c
    F = place(f, fx, fy)
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2.4 * K) | 1, int(2.4 * K) | 1))
    best = None
    for dx in np.arange(-6, 6.01, 0.25):
        for dy in np.arange(-6, 6.01, 0.25):
            R = place(r, rx, ry, dx, dy)
            U = F | R
            over = (F & R).sum()
            gaps = (cv2.morphologyEx(U, cv2.MORPH_CLOSE, ker) - U).sum()
            score = gaps + 3 * over
            if best is None or score < best[0]:
                best = (score, dx, dy)
    _, dx, dy = best
    w, h = b['back-register'][2], b['back-register'][3]
    print('register ghost box (mirrored back-register, on the front):',
          [round(720 - b['back-register'][0] - w + dx, 2), round(b['back-register'][1] + dy, 2), w, h], 'shift', dx, dy)


if __name__ == '__main__':
    portrait_ghost()
    white_watermark()
    register_fit()
