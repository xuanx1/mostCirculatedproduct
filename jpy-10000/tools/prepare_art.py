"""
Working artwork from the Wikimedia Commons photographs (source/):
  source/front-commons-3696.jpg, source/back-commons-3592.jpg  (Heavy Frisker, CC BY-SA 4.0)

The photos are large (3696 and 3592 px wide), so no AI upscaling is needed. Per side:
  1. Flatten: the note's four edges are found where the paper meets the green backdrop (the first
     sustained run of paper colour, sub-pixel), fitted with smooth curves (the photo shows slight lens
     bow), and the note is remapped onto a flat 3600 x 1710 rectangle (160 x 76 mm, 22.5 px/mm) with a
     Coons patch. A second pass on the result corrects what is left; a few px are trimmed so no
     backdrop shows.
  2. Level: the lighting is uneven and green-tinted. The paper's own colour is measured across the
     note (smooth, print-free areas), fitted as a smooth surface per channel and divided out, so the
     paper becomes an even warm cream; then a gentle mid-tone lift and a little more saturation, as
     the other explorers do.
Writes jpy-10000-front.png and jpy-10000-back.png.   Run: python tools/prepare_art.py
"""
import os
import numpy as np, cv2
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = {'front': 'source/front-commons-3696.jpg', 'back': 'source/back-commons-3592.jpg'}
TRIM = {'front': (4, 4, 4, 4), 'back': (7, 7, 4, 4)}          # top, bottom, left, right px after flattening
OW, OH = 3600, 1710
PAPER = np.array([246, 240, 222], np.float32)                 # warm cream


def S_of(im):
    lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 1.2), cv2.COLOR_BGR2LAB).astype(float)
    return lab[..., 0] + 2.0 * lab[..., 2] - 1.5 * lab[..., 1]          # paper: bright and warm; backdrop: green


def fit_edges(im, band, thr=None, deg=3):
    S = S_of(im); H, W = S.shape
    if thr is None:
        bg = np.median(np.concatenate([S[:4].ravel(), S[-4:].ravel(), S[:, :4].ravel(), S[:, -4:].ravel()]))
        thr = (bg + np.percentile(S, 75)) / 2
    def prof(arr):
        ok = arr > thr
        run = np.convolve(ok.astype(int), np.ones(10, int), 'valid')
        idx = np.where(run == 10)[0]
        if not len(idx):
            return None
        j = idx[0]
        if j == 0:
            return 0.0
        a0, a1 = arr[j - 1], arr[j]
        return j - 1 + (thr - a0) / (a1 - a0 + 1e-6)
    g = {'top': lambda i: S[:band, i], 'bottom': lambda i: S[H - band:, i][::-1],
         'left': lambda i: S[i, :band], 'right': lambda i: S[i, W - band:][::-1]}
    res = {}
    for side in g:
        n = W if side in ('top', 'bottom') else H
        pts = []
        for i in range(10, n - 10, 5):
            j = prof(g[side](i))
            if j is None:
                continue
            pts.append((i, j if side in ('top', 'left') else ((H if side == 'bottom' else W) - 1 - j)))
        p = np.array(pts, float); X, Y = p[:, 0], p[:, 1]
        for _ in range(10):                                   # robust: print near the edge is an outlier
            c = np.polyfit(X, Y, deg); r = np.abs(Y - np.polyval(c, X))
            keep = r < max(1.0, np.percentile(r, 80)); X, Y = X[keep], Y[keep]
        res[side] = c
    return res, thr


def coons(e, H):
    T = lambda x: np.polyval(e['top'], x); B = lambda x: np.polyval(e['bottom'], x)
    L = lambda y: np.polyval(e['left'], y); R = lambda y: np.polyval(e['right'], y)
    def corner(vert, horiz):
        y = 0 if horiz == 'top' else H
        for _ in range(60):
            x = (L if vert == 'left' else R)(y); y = (T if horiz == 'top' else B)(x)
        return np.array([x, y])
    P00, P10, P01, P11 = corner('left', 'top'), corner('right', 'top'), corner('left', 'bottom'), corner('right', 'bottom')
    u = np.linspace(0, 1, OW)[None, :]; v = np.linspace(0, 1, OH)[:, None]
    tx = P00[0] + (P10[0] - P00[0]) * u; Tp = np.stack([tx + 0 * v, T(tx) + 0 * v], -1)
    bx = P01[0] + (P11[0] - P01[0]) * u; Bp = np.stack([bx + 0 * v, B(bx) + 0 * v], -1)
    ly = P00[1] + (P01[1] - P00[1]) * v; Lp = np.stack([L(ly) + 0 * u, ly + 0 * u], -1)
    ry = P10[1] + (P11[1] - P10[1]) * v; Rp = np.stack([R(ry) + 0 * u, ry + 0 * u], -1)
    uu, vv = u[..., None], v[..., None]
    return ((1 - vv) * Tp + vv * Bp + (1 - uu) * Lp + uu * Rp
            - ((1 - uu) * (1 - vv) * P00 + uu * (1 - vv) * P10 + (1 - uu) * vv * P01 + uu * vv * P11)).astype(np.float32)


def flatten(im):
    e1, thr = fit_edges(im, 140); P1 = coons(e1, im.shape[0])
    r1 = cv2.remap(im, P1[..., 0], P1[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    e2, _ = fit_edges(r1, 50, thr)
    e2['top'][-1] += 2; e2['left'][-1] += 2; e2['bottom'][-1] -= 2; e2['right'][-1] -= 2
    P2 = coons(e2, OH)
    Px = cv2.remap(P1[..., 0], P2[..., 0], P2[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    Py = cv2.remap(P1[..., 1], P2[..., 0], P2[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return cv2.remap(im, Px, Py, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)


def level(rgb, trim):
    t, b, l, r = trim
    im = rgb[t:rgb.shape[0] - b, l:rgb.shape[1] - r].astype(np.float32)
    im = cv2.resize(im, (OW, OH), interpolation=cv2.INTER_LANCZOS4)
    sm = cv2.resize(im, (OW // 8, OH // 8), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(np.clip(sm, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    ref = np.median(lab[lab[..., 0] > np.percentile(lab[..., 0], 70)], 0)
    paper = (np.sqrt(((lab[..., 1:] - ref[1:]) ** 2).sum(-1)) < 5) & (lab[..., 0] > ref[0] - 25)
    paper &= np.abs(cv2.Laplacian(cv2.GaussianBlur(lab[..., 0], (0, 0), 1), cv2.CV_32F)) < 4
    ys, xs = np.nonzero(paper)
    X, Y = xs / (OW / 8), ys / (OH / 8)
    A = np.stack([np.ones_like(X), X, Y, X * X, X * Y, Y * Y, X ** 3, Y ** 3, X * X * Y, X * Y * Y], 1)
    gy, gx = np.mgrid[0:OH, 0:OW].astype(np.float32); gx /= OW; gy /= OH
    G = np.stack([np.ones_like(gx), gx, gy, gx * gx, gx * gy, gy * gy, gx ** 3, gy ** 3, gx * gx * gy, gx * gy * gy], -1)
    illum = np.zeros((OH, OW, 3), np.float32)
    for c in range(3):
        v = sm[ys, xs, c]; coef = np.linalg.lstsq(A, v, rcond=None)[0]
        for _ in range(3):
            res = v - A @ coef; k = np.abs(res) < 2.5 * res.std(); coef = np.linalg.lstsq(A[k], v[k], rcond=None)[0]
        illum[..., c] = G @ coef
    out = 255 * (np.clip(im / illum * PAPER, 0, 255) / 255) ** 0.95
    return ImageEnhance.Color(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))).enhance(1.10)


def main():
    for side, src in SOURCES.items():
        im = cv2.imread(os.path.join(ROOT, src))
        flat = cv2.cvtColor(flatten(im), cv2.COLOR_BGR2RGB)
        level(flat, TRIM[side]).save(os.path.join(ROOT, f'jpy-10000-{side}.png'), optimize=True)
        print(side, im.shape[1], 'x', im.shape[0], '->', OW, 'x', OH)


if __name__ == '__main__':
    main()
