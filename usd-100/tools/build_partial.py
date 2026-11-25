"""
Quick partial rebuild: re-extract only the named features, and rebuild the watermark ghost.
Much faster than the full run (no offset layers, no masks).

  python tools/build_partial.py seal latent-patch lion-head
  python tools/build_partial.py --ghost-only

The watermark ghost is built from assets/overrides/front-portrait-cut.png when present
(a hand-cleaned portrait), otherwise from the engraved portrait in the artwork.
Overrides in assets/overrides/ always win.
"""
import os, sys
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_features as EF       # noqa: E402
import isolate_features as IF       # noqa: E402

ROOT = EF.ROOT
LAYERS = os.path.join(ROOT, 'assets', 'layers')
OVR = os.path.join(ROOT, 'assets', 'overrides')


def override(name):
    p = os.path.join(OVR, name)
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None


def build_features(names):
    imgs = {s: Image.open(os.path.join(ROOT, f)).convert('RGB') for s, f in EF.SRC.items()}
    repaired = IF.repaired_front(imgs['front'])
    for fid, side, label, shape, g in EF.REGIONS:
        if fid not in names or (side, fid) in IF.SKIP:
            continue
        src = repaired if (side, fid) == ('front', 'portrait') else imgs[side]
        res = IF.isolate(src, side, fid, shape, g)
        d = os.path.join(EF.OUT, side)
        os.makedirs(d, exist_ok=True)
        Image.fromarray(IF.trim(res['cut']), 'RGBA').save(os.path.join(d, f'{fid}.png'), optimize=True)
        Image.fromarray(IF.trim(res['ink']), 'RGBA').save(os.path.join(d, f'{fid}-ink.png'), optimize=True)
        for key, suffix in (('cut', '-cut'), ('ink', '')):
            name = f'{side}-{fid}{suffix}.png'
            img = override(name) or IF.page_frame(res, side, fid, shape, g, res[key])
            img.save(os.path.join(LAYERS, name), optimize=True)
            print('wrote', name, '(override)' if override(name) else '')


def build_ghost():
    """Watermark: the same face as the portrait, rendered like a mould-made watermark:
    continuous tone (no engraving lines), faint, fading out at an oval edge."""
    src = override('front-portrait-cut.png')
    if src is None:
        print('no cleaned portrait in overrides; ghost left as is')
        return
    # the ghost layer's frame on the page (note units) and its pixel size
    old = Image.open(os.path.join(LAYERS, 'watermark-ghost.png'))
    W, H = old.size
    a = np.asarray(src, np.float32)
    rgb, alpha = a[..., :3], a[..., 3] / 255
    lum = rgb @ np.array([.299, .587, .114], np.float32)
    # fit the head into the oval: crop to the head (top ~88% of the portrait, without most of the coat)
    h0 = int(src.height * 0.88)
    lum, alpha = lum[:h0], alpha[:h0]
    lum = cv2.resize(lum, (W, H), interpolation=cv2.INTER_AREA)
    alpha = cv2.resize(alpha, (W, H), interpolation=cv2.INTER_AREA)
    lum = cv2.GaussianBlur(lum, (0, 0), max(2.0, W / 150))          # engraving lines -> tone
    paper = np.percentile(lum[alpha > 0.5], 97) if (alpha > 0.5).any() else 255
    dark = np.clip((paper - lum) / max(paper - np.percentile(lum[alpha > 0.5], 3), 1), 0, 1) ** 0.85
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    fade = np.clip((1.0 - d) / 0.22, 0, 1)
    fade = fade * fade * (3 - 2 * fade)
    a_out = dark * alpha * fade
    col = np.empty((H, W, 3), np.float32)
    col[...] = (96, 78, 58)
    ghost = Image.fromarray(np.dstack([col, a_out * 255]).astype(np.uint8), 'RGBA')
    ghost.save(os.path.join(LAYERS, 'watermark-ghost.png'), optimize=True)
    # presentation copies
    for side, img in (('front', ghost), ('back', ghost.transpose(Image.FLIP_LEFT_RIGHT))):
        os.makedirs(os.path.join(EF.OUT, side), exist_ok=True)
        img.save(os.path.join(EF.OUT, side, 'watermark-ink.png'), optimize=True)
    print('wrote watermark-ghost.png from the cleaned portrait')


def reuse_numerals():
    """The colour-shift 10000 is overprinted by the coat hatching, so it never extracts cleanly. It is
    the same lettering as the large reverse 10000, which extracts cleanly. Fit that one onto the
    colour-shift numerals by template matching against the artwork (scale + offset search), and
    save it as the colour-shift layer."""
    src = Image.open(os.path.join(LAYERS, 'back-intaglio-10000-cut.png')).convert('RGBA')
    digits = src.crop(src.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox())
    # template: digits flattened on white, grayscale
    flat = Image.new('RGB', digits.size, 'white'); flat.paste(digits, (0, 0), digits)
    tpl0 = np.asarray(flat.convert('L'), np.float32)
    # search area in the artwork (full resolution)
    art = Image.open(os.path.join(ROOT, EF.SRC['front'])).convert('L')
    AW, AH = art.size; ax, ay = AW / EF.VB_W, AH / EF.VB_H
    x0, y0, x1, y1 = 556, 250, 720, 312
    area = np.asarray(art.crop((int(x0 * ax), int(y0 * ay), int(x1 * ax), int(y1 * ay))), np.float32)
    nominal_w, nominal_h = (715.5 - 568.2) * ax, (305.0 - 261.2) * ay
    best = (-1, None)
    for kw in np.linspace(0.94, 1.06, 13):
        for kh in np.linspace(0.94, 1.06, 13):
            w, h = int(nominal_w * kw), int(nominal_h * kh)
            if w >= area.shape[1] or h >= area.shape[0]:
                continue
            tpl = cv2.resize(tpl0, (w, h), interpolation=cv2.INTER_AREA)
            r = cv2.matchTemplate(area, tpl, cv2.TM_CCOEFF_NORMED)
            _, score, _, loc = cv2.minMaxLoc(r)
            if score > best[0]:
                best = (score, (loc[0], loc[1], w, h))
    score, (lx, ly, w, h) = best
    # refine digit by digit: the two printings space their digits slightly differently
    alpha = np.asarray(digits.getchannel('A'), np.float32)
    colsum = alpha.sum(0)
    Wd = digits.width
    cuts = [0]
    for k in range(1, 5):                                  # split at the 4 lowest columns near k/5
        lo, hi = int(Wd * (k / 5 - 0.07)), int(Wd * (k / 5 + 0.07))
        cuts.append(lo + int(np.argmin(colsum[lo:hi])))
    cuts.append(Wd)
    sxg, syg = w / digits.width, h / digits.height
    pieces = []
    for k in range(5):
        piece = digits.crop((cuts[k], 0, cuts[k + 1], digits.height))
        pw, ph = max(4, int(piece.width * sxg)), max(4, int(piece.height * syg))
        fl = Image.new('RGB', piece.size, 'white'); fl.paste(piece, (0, 0), piece)
        t = cv2.resize(np.asarray(fl.convert('L'), np.float32), (pw, ph), interpolation=cv2.INTER_AREA)
        ex, ey = int(lx + cuts[k] * sxg), int(ly)
        m = 18                                              # search ±18 px around the global fit
        X0, Y0 = max(0, ex - m), max(0, ey - m)
        win = area[Y0:min(area.shape[0], ey + ph + m), X0:min(area.shape[1], ex + pw + m)]
        if win.shape[0] > ph and win.shape[1] > pw:
            r = cv2.matchTemplate(win, t, cv2.TM_CCOEFF_NORMED)
            _, sc, _, (dx, dy) = cv2.minMaxLoc(r)
            ex, ey = X0 + dx, Y0 + dy
        pieces.append((piece, ex, ey, pw, ph))
    # matched placement, in note units
    nx0, ny0 = x0 + lx / ax, y0 + ly / ay
    nx1, ny1 = nx0 + w / ax, ny0 + h / ay
    frame = Image.open(os.path.join(LAYERS, 'front-ovi-10000.png'))
    W, H = frame.size
    fx, fy, fx1, fy1 = EF.bbox('poly', next(r for r in EF.REGIONS if (r[1], r[0]) == ('front', 'ovi-10000'))[4], EF.PAD)[0]
    px = lambda X, Y: (int(round((X - fx) / (fx1 - fx) * W)), int(round((Y - fy) / (fy1 - fy) * H)))
    (a0, b0), (a1, b1) = px(nx0, ny0), px(nx1, ny1)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for piece, ex, ey, pw, ph in pieces:                   # each digit at its own matched place
        (q0, r0), (q1, r1) = px(x0 + ex / ax, y0 + ey / ay), px(x0 + (ex + pw) / ax, y0 + (ey + ph) / ay)
        pr = piece.resize((max(1, q1 - q0), max(1, r1 - r0)), Image.LANCZOS)
        out.alpha_composite(pr, (max(0, q0), max(0, r0)))
    for name in ('front-ovi-10000.png', 'front-ovi-10000-cut.png'):
        out.save(os.path.join(OVR, name), optimize=True)       # kept by every later run
        out.save(os.path.join(LAYERS, name), optimize=True)
    out.crop(out.getchannel('A').getbbox()).save(os.path.join(EF.OUT, 'front', 'ovi-10000.png'), optimize=True)
    print(f'colour-shift 10000 matched to the artwork: score {score:.3f}, at x {nx0:.2f}-{nx1:.2f}, y {ny0:.2f}-{ny1:.2f}')


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--ghost-only' not in args:
        build_features(set(a for a in args if not a.startswith('--')))
    build_ghost()
    if '--numerals' in args:
        reuse_numerals()
