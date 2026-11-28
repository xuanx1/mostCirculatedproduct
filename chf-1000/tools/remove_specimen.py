"""
Remove the SPECIMEN overprint from the SNB's images (both sides) with LaMa inpainting.

The overprint is translucent grey lettering over very busy print, so a colour test alone finds only parts of
the strokes. But the word is a plain sans-serif set on one straight line, so its letters are reconstructed
geometrically: SPECIMEN is rendered in a matching sans (DejaVu Sans Bold / Arial Bold), and its placement
(centre, angle, size) is fitted to each side by maximising how many of its pixels are "overprint-like"
(greyer and darker than their own neighbourhood). The fitted letters, grown a few px, are the mask; LaMa
(big-lama, TorchScript) fills them from the print around them.

Reads source/<side>-artwork-specimen.png (the untouched artwork, made on first run), writes chf-1000-<side>.png.
Run: python tools/remove_specimen.py [--preview]     then   python tools/extract_chf.py
"""
import os, sys, shutil
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMA = os.environ.get('LAMA_MODEL', r'C:/Users/65963/AppData/Local/Temp/claude/c0d258789f1d297c/94e98cd5-0543-44a8-952a-896d58182aaf/scratchpad/lama/big-lama.pt')
# first guess per side (artwork px, 1600 x 3610): the word's two ends (S end, N end)
GUESS = {'front': ((140, 3500), (1330, 260)), 'back': ((300, 3500), (1530, 170))}
FONTS = ['C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/verdanab.ttf']


def overprint_score(rgb):
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, C = lab[..., 0], np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)
    mL = cv2.medianBlur(L.astype(np.uint8), 61).astype(np.float32)
    mC = cv2.medianBlur(np.clip(C * 4, 0, 255).astype(np.uint8), 61).astype(np.float32) / 4
    return np.clip((mL - L) / 25, 0, 1) * np.clip((mC + 4 - C) / 10, 0, 1)        # darker AND greyer


def render(font, text_h, length, ang, centre, shape, track=0.0):
    """SPECIMEN, cap height text_h, stretched to `length` along angle `ang` about `centre`."""
    f = ImageFont.truetype(font, int(text_h * 1.38))
    w0 = sum(f.getlength(c) for c in 'SPECIMEN') + track * text_h * 7
    img = Image.new('L', (int(w0 + text_h), int(text_h * 2)), 0)
    d = ImageDraw.Draw(img); x = text_h / 2
    for c in 'SPECIMEN':
        d.text((x, text_h * 1.0), c, font=f, fill=255, anchor='ls'); x += f.getlength(c) + track * text_h
    bb = img.getbbox(); img = img.crop(bb)
    img = img.resize((max(2, int(length)), max(2, int(img.height * length / img.width))), Image.LANCZOS)
    a = np.asarray(img, np.float32) / 255
    h, w = a.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    M[0, 2] += centre[0] - w / 2; M[1, 2] += centre[1] - h / 2
    return cv2.warpAffine(a, M, (shape[1], shape[0]))


def fit(side, rgb):
    k = 0.25                                                 # fit at quarter size, refine at half
    S = overprint_score(cv2.resize(rgb, None, fx=k, fy=k, interpolation=cv2.INTER_AREA))
    (x0, y0), (x1, y1) = GUESS[side]
    best = None
    for font in [f for f in FONTS if os.path.exists(f)]:
        for dl in (0.94, 1.0, 1.06):
            L0 = np.hypot(x1 - x0, y1 - y0) * k * dl
            for th in np.arange(0.10, 0.17, 0.01):          # cap height as a share of the length
                for dang in np.arange(-2, 2.01, 0.5):
                    ang = np.degrees(np.arctan2(-(y1 - y0), x1 - x0)) + dang
                    for dx in range(-12, 13, 4):
                        for dy in range(-12, 13, 4):
                            c = ((x0 + x1) / 2 * k + dx, (y0 + y1) / 2 * k + dy)
                            m = render(font, L0 * th, L0, ang, c, S.shape)
                            v = (m * S).sum() / (m.sum() + 1e-6) - 0.35 * ((1 - m) * S * (cv2.dilate(m, np.ones((15, 15))) > 0.1)).sum() / (m.sum() + 1e-6)
                            if best is None or v > best[0]:
                                best = (v, font, L0 / k, th, ang, (c[0] / k, c[1] / k))
    print(side, 'fit score %.3f' % best[0], os.path.basename(best[1]), 'len %.0f cap %.2f ang %.1f centre (%.0f, %.0f)' % (best[2], best[3], best[4], *best[5]))
    _, font, Lf, th, ang, c = best
    return render(font, Lf * th, Lf, ang, c, rgb.shape[:2])


def lama(rgb, m):
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.jit.load(LAMA, map_location=dev).eval()
    out = rgb.copy()
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    for i in range(1, n):                                    # one letter at a time, with context around it
        x, y, w, h, _ = st[i]; pad = 120
        x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(rgb.shape[1], x + w + pad), min(rgb.shape[0], y + h + pad)
        crop, mc = out[y0:y1, x0:x1], (lab[y0:y1, x0:x1] == i).astype(np.uint8) * 255
        hh, ww = crop.shape[:2]; H, W = (hh + 7) // 8 * 8, (ww + 7) // 8 * 8
        im = np.pad(crop, ((0, H - hh), (0, W - ww), (0, 0)), mode='reflect'); mk = np.pad(mc, ((0, H - hh), (0, W - ww)))
        t = torch.from_numpy(im).permute(2, 0, 1)[None].float().div(255).to(dev)
        tm = torch.from_numpy((mk > 127).astype(np.float32))[None, None].to(dev)
        with torch.no_grad():
            r = model(t, tm)[0].permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()[:hh, :ww]
        a = cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 1.2)[..., None]
        out[y0:y1, x0:x1] = (crop * (1 - a) + r * a).astype(np.uint8)
    return out


def main():
    preview = '--preview' in sys.argv
    for side in ('front', 'back'):
        art = os.path.join(ROOT, f'chf-1000-{side}.png')
        keep = os.path.join(ROOT, 'source', f'{side}-artwork-specimen.png')
        if not os.path.exists(keep):
            shutil.copyfile(art, keep)
        rgb = np.asarray(Image.open(keep).convert('RGB'))
        letters = fit(side, rgb)
        m = cv2.dilate((letters > 0.35).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
        if preview:
            ov = rgb.copy(); ov[m > 0] = (0.4 * ov[m > 0] + [0, 150, 0]).astype(np.uint8)
            Image.fromarray(ov).save(os.path.join(ROOT, 'source', f'{side}-specimen-mask-preview.png')); continue
        Image.fromarray(lama(rgb, m)).save(art, optimize=True)
        print(side, 'SPECIMEN removed')


if __name__ == '__main__':
    main()
