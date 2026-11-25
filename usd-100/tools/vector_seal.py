"""
The Federal Reserve System seal, rebuilt from the public-domain vector on Wikimedia Commons
(File:Seal_of_the_United_States_Federal_Reserve_System.svg, linked from en.wikipedia.org/wiki/Federal_Reserve),
saved as source/frb-seal-commons.svg and rendered to source/frb-seal-commons-996.png.

The note prints the same seal on a black base: the lettering band is black with paper-coloured
letters. So the vector is registered onto the scan (template match over scale and position), its
lettering band is inverted, and it is tinted with the note's own ink and paper colours.

Writes feature-crops/front/frb-seal.png, assets/layers/front-frb-seal(-cut).png and the seal's box
in assets/boxes.js.   Run: python tools/vector_seal.py
"""
import os, re, json
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUESS = (119, 152.6)                 # note units, near the seal's centre
BAND = (0.705, 0.878)                # lettering band, as a fraction of the seal's radius (black on the note)
INK = np.array([18, 18, 22.])


def main():
    note_img = Image.open(os.path.join(ROOT, 'usd-100-front.png')).convert('RGB')
    W, H = note_img.size; sx, sy = W / 720, H / 320
    note = np.asarray(note_img.convert('L')).astype(np.float32)
    hi = Image.open(os.path.join(ROOT, 'source', 'frb-seal-commons-996.png')).convert('RGBA')
    va = np.asarray(hi).astype(np.float32); a = va[..., 3] / 255
    lum = va[..., :3].mean(-1) * a + 255 * (1 - a)
    N = hi.width
    yy, xx = np.mgrid[:N, :N]; rr = np.hypot(xx - N / 2 + .5, yy - N / 2 + .5) / (N / 2)
    band = np.clip(np.minimum(rr - BAND[0], BAND[1] - rr) * N / 2 + .5, 0, 1)     # 1 inside, ~1 px edge
    lum_note = lum * (1 - band) + (255 - lum) * band                               # black base, light letters
    # register the black-based seal on the scan
    cx, cy = GUESS[0] * sx, GUESS[1] * sy
    x0, y0 = int(cx - 260), int(cy - 260); roi = note[y0:y0 + 520, x0:x0 + 520].copy()
    best = (-1, 0, (0, 0))
    for d in range(280, 400):
        t = cv2.resize(lum_note.astype(np.float32), (d, d), interpolation=cv2.INTER_AREA)
        _, v, _, l = cv2.minMaxLoc(cv2.matchTemplate(roi, t, cv2.TM_CCOEFF_NORMED))
        if v > best[0]:
            best = (v, d, l)
    score, D, (mx, my) = best
    X, Y = x0 + mx, y0 + my
    # paper colour from just outside the seal
    m = 40; nc = np.asarray(note_img.crop((X - m, Y - m, X + D + m, Y + D + m))).astype(np.float32)
    gy, gx = np.mgrid[:nc.shape[0], :nc.shape[1]]; r2 = np.hypot(gx - (D / 2 + m), gy - (D / 2 + m))
    ring = nc[(r2 > D / 2 + 8) & (r2 < D / 2 + m)]; Lr = ring.mean(-1)
    paper = np.median(ring[Lr > np.percentile(Lr, 60)], 0)

    def tint(lum_, alpha, size):
        L = cv2.resize(lum_.astype(np.float32), size, interpolation=cv2.INTER_AREA)[..., None] / 255
        A = cv2.resize(alpha.astype(np.float32), size, interpolation=cv2.INTER_AREA)
        rgb = INK * (1 - L) + paper * L
        return Image.fromarray(np.dstack([rgb, A * 255]).clip(0, 255).astype(np.uint8), 'RGBA')

    big = tint(lum_note, a, (N, N)); out = Image.new('RGBA', (N + 24, N + 24)); out.alpha_composite(big, (12, 12))
    out.save(os.path.join(ROOT, 'feature-crops', 'front', 'frb-seal.png'), optimize=True)
    ccx, ccy, rx, ry, P = (X + D / 2) / sx, (Y + D / 2) / sy, D / 2 / sx, D / 2 / sy, 2
    kx, ky = 1440 / 720 * 1.5, 612 / 320 * 1.5
    fr = Image.new('RGBA', (round((2 * rx + 2 * P) * kx), round((2 * ry + 2 * P) * ky)))
    fr.alpha_composite(tint(lum_note, a, (round(2 * rx * kx), round(2 * ry * ky))), (round(P * kx), round(P * ky)))
    for n in ('front-frb-seal.png', 'front-frb-seal-cut.png'):
        fr.save(os.path.join(ROOT, 'assets', 'layers', n), optimize=True)
    box = [round(ccx - rx - P, 2), round(ccy - ry - P, 2), round(2 * rx + 2 * P, 2), round(2 * ry + 2 * P, 2)]
    p = os.path.join(ROOT, 'assets', 'boxes.js'); s = open(p, encoding='utf8').read()
    s = re.sub(r'"front-frb-seal": \[[^\]]*\]', '"front-frb-seal": ' + json.dumps(box), s)
    open(p, 'w', encoding='utf8').write(s)
    print(f'match {score:.3f}  centre ({ccx:.1f}, {ccy:.1f})  box {box}')


if __name__ == '__main__':
    main()
