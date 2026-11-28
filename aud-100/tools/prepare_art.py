"""
Working artwork for the Australian $100 (2020) from the Wikimedia Commons scans in source/.

  python tools/prepare_art.py

Per side:
  1. Crop to the note edge: the scans are already cut to the note, with a few px of the dark scanner
     background left along parts of some edges; those rows/columns are trimmed.
  2. Resize to the working size 3072 x 1264 (the note is 158 x 65 mm, 2.431 : 1).
  3. Level: the light polymer tint set near white, a gentle mid-tone lift (as usd-100/tools/upscale.py).
  4. Clear windows: the scanner lid shows black through the top-to-bottom window and the small fan
     window. Inside each window the black is matted out against the backing colour, so the page shows
     what is behind the note through the clear polymer; the print in the window (fan, owls, Shrine,
     wattle) keeps its own pixels, and embossing keeps its light-and-dark relief as partial alpha.
Writes aud-100-front.png / aud-100-back.png (RGBA), source/window-<side>.png (the clear area) and
source/flat-<side>.png (levelled, before the matte). No upscaling: the Commons originals are 8319 and
8218 px wide, so they are reduced, not enlarged.
"""
import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')
OUT_W, OUT_H = 3072, 1264
VB_W, VB_H = 720, 320
# where the clear areas are (note units, Melba side; the Monash side is the mirror image).
# Only seeds: the matte itself follows the dark backing in the scan.
WINDOWS = {
    'main': (170, 0, 170, 320),        # top-to-bottom window
    'fan':  (583, 196, 106, 116),      # small window: the embossed fan, wattle and leaf shapes
}
NOT_WINDOW = [(580, 186, 50, 19), (580, 186, 26, 30)]
NOT_WINDOW_BACK = [(543, 190, 20, 130)]       # the large 100's 1, beside the window on the Monash side


def source(side):
    for name in (f'{side}-commons-bavhah.jpg',):
        p = os.path.join(SRC, name)
        if os.path.exists(p) and os.path.getsize(p) > 100000:
            return p, name


def trim_edges(a, side):
    """Rows/columns at the edges that still hold dark scanner background (the clear window, which
    shows the same black, is left out of the count)."""
    L = a.mean(axis=2)
    H, W = L.shape
    dark = L < 80
    x, _, w, _ = WINDOWS['main']
    if side == 'back':
        x = VB_W - x - w
    dark[:, int((x - 8) / VB_W * W):int((x + w + 8) / VB_W * W)] = False

    def run(lines):
        n = 0
        for v in lines:
            if v > 0.004:
                n += 1
            else:
                break
        return n
    t = run(dark[:40].mean(axis=1))
    b = run(dark[::-1][:40].mean(axis=1))
    l = run(dark[:, :40].mean(axis=0))
    r = run(dark[:, ::-1][:, :40].mean(axis=0))
    k = max(1, W // 2000)                      # one more px of edge blur at this scan size
    return a[t + k:H - b - k, l + k:W - r - k], (t, b, l, r)


def brighten(img):
    a = np.asarray(img, np.float32)
    lum = a @ np.array([.299, .587, .114], np.float32)
    paper = np.percentile(lum, 95)                           # the light polymer tint
    black = np.percentile(lum, 0.3)
    a = np.clip((a - black) / max(paper - black, 1) * 242, 0, 255)
    a = 255 * (a / 255) ** 0.95
    return Image.fromarray(a.astype(np.uint8))


def window_matte(rgb, side):
    """Alpha for the clear windows: 0 where the scan shows the black backing, rising to 1 for print."""
    H, W = rgb.shape[:2]
    sx, sy = W / VB_W, H / VB_H
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    chroma = np.hypot(A, B)
    backing = L < 100                      # the black backing, with its sheen (print is far lighter)
    seed = np.zeros((H, W), np.uint8)
    for k, (x, y, w, h) in WINDOWS.items():
        if side == 'back':
            x = VB_W - x - w
        seed[int(y * sy):int((y + h) * sy), int(x * sx):int((x + w) * sx)] = 255
    for x, y, w, h in NOT_WINDOW:                 # Rosina's hand and fan (intaglio) beside the small window
        if side == 'back':
            x = VB_W - x - w
        seed[int(y * sy):int((y + h) * sy), int(x * sx):int((x + w) * sx)] = 0
    for x, y, w, h in (NOT_WINDOW_BACK if side == 'back' else []):
        seed[int(y * sy):int((y + h) * sy), int(x * sx):int((x + w) * sx)] = 0
    m = (backing * 255).astype(np.uint8) & seed
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    # the clear area is a few large connected regions; dark intaglio lines nearby are small
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > (6 * sx) ** 2:
            keep[lab_ == i] = 255
    # the window's extent: clear area plus the print standing in it (enclosed print = holes, filled)
    hull = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(1.2 * sx) | 1,) * 2))
    # holes = background pieces that don't reach the note edge (the window itself runs edge to edge,
    # so a flood fill from one corner would also take the whole far side of the note)
    n, lab_, st, _ = cv2.connectedComponentsWithStats(cv2.bitwise_not(hull), 4)
    for i in range(1, n):
        x, y, w, h, _a = st[i]
        if x > 0 and y > 0 and x + w < W and y + h < H:
            hull[lab_ == i] = 255
    hull &= seed
    # the backing's sheen varies across the window: its local level from the backing pixels around
    # (normalised blur); each pixel is matted against that
    bmask = ((hull > 0) & backing).astype(np.float32)
    sig = 3 * sx
    Bl = cv2.GaussianBlur(L * bmask, (0, 0), sig) / np.maximum(cv2.GaussianBlur(bmask, (0, 0), sig), 1e-3)
    bk = np.median(rgb[keep > 0], axis=0).astype(np.float32)
    # lighter than the backing = print (or embossed relief) in the window
    a = np.clip((L - Bl - 10) / 70.0, 0, 1)
    # broad print in the window (foil owl, fan, Shrine, wattle, leaves) is opaque throughout, including
    # its darker shading; only thin line-work and embossing keep partial alpha
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(r * sx) | 1,) * 2)
    solid = (((L - Bl) > 70) & (hull > 0)).astype(np.uint8) * 255
    solid = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, k(0.8))
    # fill only small holes (shading inside the foil): the flying owl's open wings stay clear
    n_, lab2, st2, _ = cv2.connectedComponentsWithStats(cv2.bitwise_not(solid), 4)
    for i in range(1, n_):
        if st2[i, cv2.CC_STAT_AREA] < (3.5 * sx) ** 2:
            solid[lab2 == i] = 255
    solid = cv2.morphologyEx(solid, cv2.MORPH_OPEN, k(1.6))
    solid = cv2.erode(solid, k(0.3))
    a = np.maximum(a, cv2.GaussianBlur(solid.astype(np.float32) / 255, (0, 0), 0.7))
    inside = cv2.GaussianBlur((hull > 0).astype(np.float32), (0, 0), 1.2)
    alpha = 1 - inside * (1 - a)
    safe = np.maximum(alpha, 0.2)[..., None]
    col = np.clip((rgb.astype(np.float32) - bk * (1 - safe)) / safe, 0, 255)
    col = rgb * (1 - inside[..., None]) + col * inside[..., None]
    return col.astype(np.uint8), alpha, (hull > 0)


def main():
    for side in ('front', 'back'):
        path, name = source(side)
        im = np.asarray(Image.open(path).convert('RGB'))
        cropped, cut = trim_edges(im, side)
        img = Image.fromarray(cropped).resize((OUT_W, OUT_H), Image.LANCZOS)
        img = brighten(img)
        rgb = np.asarray(img)
        img.save(os.path.join(SRC, f'flat-{side}.png'), optimize=True)   # levelled, before the matte (foil colours)
        col, alpha, clear = window_matte(rgb, side)
        out = np.dstack([col, (alpha * 255).round().astype(np.uint8)])
        Image.fromarray(out, 'RGBA').save(os.path.join(ROOT, f'aud-100-{side}.png'), optimize=True)
        Image.fromarray((clear * 255).astype(np.uint8)).save(os.path.join(SRC, f'window-{side}.png'), optimize=True)
        print(side, name, im.shape[1::-1], 'trim t/b/l/r', cut, '->', (OUT_W, OUT_H))


if __name__ == '__main__':
    main()
