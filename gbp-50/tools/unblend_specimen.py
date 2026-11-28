"""
Remove the translucent SPECIMEN overprint by un-blending it rather than inventing what is under it.
The overprint is a grey film laid over the print: observed = orig * (1 - a*s) + k * a*s, where s is the
letter shape (soft) and a, k its opacity and grey. Inside the letters the print still shows through,
so dividing the film back out recovers the real engraving. a and k are fitted per channel by comparing
letter pixels with the print just outside them (normalised convolution). Letter edges, where the fit is
weakest, get a light LaMa touch-up (tools/remove_specimen.py's model) in a thin ring only.

Reads source/<side>-levelled-specimen.png (the untouched levelled image), writes source/<side>-levelled.png.
Run: python tools/unblend_specimen.py [--preview]   then   python tools/cutouts.py
"""
import os, sys
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import remove_specimen as RS

ROOT = RS.ROOT


def letters(rgb, side):
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, C = lab[..., 0], np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    zone = np.zeros(L.shape, np.uint8); cv2.fillPoly(zone, [np.array(RS.BANDS[side], np.int32)], 255)
    m = ((L < 165) & (C < 40) & (zone > 0)).astype(np.uint8) * 255
    for x0, y0, x1, y1 in RS.KEEP_OUT.get(side, []):
        m[y0:y1, x0:x1] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m, 8)
    m = np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > 1500)[0]).astype(np.uint8) * 255
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    holes = (~ff) & 255
    n, lab_, st, _ = cv2.connectedComponentsWithStats(holes, 8)
    m[np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] < 400)[0])] = 255     # specks inside strokes
    return m


def main():
    preview = '--preview' in sys.argv
    for side in RS.BANDS:
        src = os.path.join(ROOT, 'source', f'{side}-levelled-specimen.png')
        rgb = np.asarray(Image.open(src).convert('RGB'))
        m = letters(rgb, side)
        s = np.clip(cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.6) * 1.15, 0, 1)
        f = rgb.astype(np.float32)
        outside = (cv2.dilate(m, np.ones((5, 5), np.uint8)) == 0).astype(np.float32)
        sig = 14
        num = cv2.GaussianBlur(f * outside[..., None], (0, 0), sig)
        den = cv2.GaussianBlur(outside, (0, 0), sig)[..., None] + 1e-4
        local = num / den                                    # the print around each letter pixel
        core = (cv2.erode(m, np.ones((7, 7), np.uint8)) > 0) & (den[..., 0] > 0.05)
        # fit observed = (1-a)*local + a*k per channel on the letter cores (least squares on obs vs local)
        out = f.copy()
        for c in range(3):
            x, y = local[..., c][core], f[..., c][core]
            A = np.vstack([x, np.ones_like(x)]).T
            (g, b), *_ = np.linalg.lstsq(A, y, rcond=None)     # y = g*x + b, g = 1-a, b = a*k
            g = float(np.clip(g, 0.2, 1.0))
            print(side, 'ch', c, 'gain %.3f offset %.1f' % (g, b))
            gs = 1 - (1 - g) * s; bs = b * s
            out[..., c] = (f[..., c] - bs) / gs
        out = np.clip(out, 0, 255).astype(np.uint8)
        # thin ring on the letter edges: LaMa touch-up
        ring = cv2.dilate(m, np.ones((9, 9), np.uint8)) & ~cv2.erode(m, np.ones((9, 9), np.uint8))
        if preview:
            Image.fromarray(out).save(os.path.join(ROOT, 'source', f'{side}-unblend-preview.png')); continue
        out = RS.lama(out, ring)
        Image.fromarray(out).save(os.path.join(ROOT, 'source', f'{side}-levelled.png'), optimize=True)
        print(side, 'SPECIMEN un-blended ->', f'source/{side}-levelled.png')


if __name__ == '__main__':
    main()
