"""
Remove the word "specimen" from both sides of the EUR 500 artwork with LaMa inpainting (big-lama, TorchScript).

The overprint is opaque warm-grey lettering (Lab a ~ +4, b ~ +10, L 95-165) with a thin white rim, on a
diagonal. Per side:
  1. letter mask: the overprint's own colour, only inside a band polygon along the word; specks opened
     away, small pieces dropped, closed into solid letters, holes inside strokes filled, then grown over
     the white rim;
  2. LaMa fills the mask from the print around it, one letter at a time;
  3. side repairs (FILL_SPLIT, STARS, TIPS, SERIAL_FIX below): the front 'e' is filled with its counters
     and re-filled in two halves; the pink star it hid gets its top arm back from its own geometry; a
     white stroke LaMa drew under the front 'e' is filled again; on the back the 'p' hid digits 2-4 of
     the lower serial, which become copies of a clean '0' of the same serial (S00000004795, as at the top).

Reads source/<side>-artwork-specimen.png (made on first run from eur-500-<side>.png, the untouched
output of tools/upscale.py), writes eur-500-<side>.png.
Run:  python tools/remove_specimen.py [front|back] [--preview]      then  python tools/cutouts.py
The GPU step takes the shared .gpu-lock (see README).
Model: big-lama.pt (Suvorov et al., LaMa; TorchScript release of simple-lama-inpainting); path in LAMA or
the LAMA_MODEL environment variable.
"""
import os, sys, shutil
import numpy as np, cv2
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAMA = os.environ.get('LAMA_MODEL', r'C:/Users/65963/AppData/Local/Temp/claude/c0d258789f1d297c/94e98cd5-0543-44a8-952a-896d58182aaf/scratchpad/lama/big-lama.pt')
# the word's centre line (first letter, last letter) and half-width of the band, px of the 3072 x 1574 artwork
LINE = {'front': ((300, 1290), (2800, 250), 230),
        'back':  ((300, 1300), (2790, 240), 230)}
GROW = 11            # px: the white rim (~7 px) plus a margin


def band(side, shape):
    (x0, y0), (x1, y1), hw = LINE[side]
    d = np.array([x1 - x0, y1 - y0], np.float32); d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * hw; e = d * hw
    p0, p1 = np.array([x0, y0]) - e, np.array([x1, y1]) + e
    poly = np.array([p0 + n, p1 + n, p1 - n, p0 - n], np.int32)
    z = np.zeros(shape, np.uint8); cv2.fillPoly(z, [poly], 255)
    return z


def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def letters(rgb, side):
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    grey = (np.abs(A - 4) < 8) & (np.abs(B - 10) < 9) & (L > 90) & (L < 172)
    m = (grey & (band(side, L.shape) > 0)).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(2))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m, 8)
    m = np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] > 1500)[0]).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(5))
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    n, lab_, st, _ = cv2.connectedComponentsWithStats((~ff) & 255, 8)
    m[np.isin(lab_, 1 + np.nonzero(st[1:, cv2.CC_STAT_AREA] < 1500)[0])] = 255      # specks inside strokes
    return cv2.dilate(m, disk(GROW))


def lama(rgb, m, pad=128):
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.jit.load(LAMA, map_location=dev).eval()
    res = rgb.copy()
    n, lab_, st, _ = cv2.connectedComponentsWithStats((m > 127).astype(np.uint8), 8)
    for k in range(1, n):                 # one letter at a time: a small crop keeps LaMa at its trained scale
        x, y, w, h, _ = st[k]
        y0, y1 = max(0, y - pad), min(rgb.shape[0], y + h + pad)
        x0, x1 = max(0, x - pad), min(rgb.shape[1], x + w + pad)
        crop = res[y0:y1, x0:x1]
        mc = ((lab_[y0:y1, x0:x1] == k) * 255).astype(np.uint8)
        hh, ww = crop.shape[:2]; H, W = (hh + 7) // 8 * 8, (ww + 7) // 8 * 8
        im = np.pad(crop, ((0, H - hh), (0, W - ww), (0, 0)), mode='reflect')
        mk = np.pad(mc, ((0, H - hh), (0, W - ww)))
        t = torch.from_numpy(np.ascontiguousarray(im)).permute(2, 0, 1)[None].float().div(255).to(dev)
        tm = torch.from_numpy((mk > 127).astype(np.float32))[None, None].to(dev)
        with torch.no_grad():
            out = model(t, tm)[0].permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()[:hh, :ww]
        a = cv2.GaussianBlur(mc.astype(np.float32) / 255, (0, 0), 1.2)[..., None]
        res[y0:y1, x0:x1] = (crop * (1 - a) + out * a).astype(np.uint8)
    return res


# ---- per-side repairs -------------------------------------------------------------------------
# letters (picked by a point inside them) whose counters are filled too, and which get a second LaMa pass
# split at x: the front 'e' sits where the lavender stripes meet the pink grid, and one pass blends the two
# into a pale letter-shaped patch; re-filling its right part from the pink grid, then its left part, does not
FILL_SPLIT = {'front': [((1022, 978), 1032)]}
# five-point stars whose hidden arm is put back from their own geometry (flat offset ink: their own colour):
# centre, outer radius (px, measured from the four visible tips; upright, inner radius 0.382 R), sample box
STARS = {'front': [((1062.0, 1119.0), 96.7, (1045, 1110, 1080, 1150))]}
# small second passes: (box, test) LaMa again over the pixels the test picks in the box
#   front: a thin white stroke LaMa drew from the right 0's outline into the gap under the 'e'
TIPS = {'front': [((2462, 430, 2508, 505), 'white')]}
# back, lower serial S00000004795: the 'p' covered digits 2-4 (LaMa redraws them, not exactly); a clean '0'
# of the same serial (x 783-829) is copied over each, at the serial's own pitch (49.75 px)
SERIAL_FIX = {'back': [((783, 1168, 46, 72), [(584, 1168), (634, 1168), (683, 1168)])]}


def component_at(m, pt):
    n, lab_, st, _ = cv2.connectedComponentsWithStats((m > 0).astype(np.uint8), 8)
    k = lab_[pt[1], pt[0]]
    if k == 0:
        raise SystemExit(f'no letter at {pt}')
    return ((lab_ == k) * 255).astype(np.uint8)


def fill_holes(m):
    ff = m.copy(); cv2.floodFill(ff, np.zeros((m.shape[0] + 2, m.shape[1] + 2), np.uint8), (0, 0), 255)
    return m | ((~ff) & 255)


def star_poly(c, R, n=5):
    r = R * 0.382
    pts = []
    for i in range(2 * n):
        a = -np.pi / 2 + i * np.pi / n
        rr = R if i % 2 == 0 else r
        pts.append((c[0] + rr * np.cos(a), c[1] + rr * np.sin(a)))
    return np.array(pts)


def fix_stars(out, side, hidden):
    rng = np.random.default_rng(0)
    for c, R, (x0, y0, x1, y1) in STARS.get(side, []):
        q = 4                                                    # 4x supersampled edge
        # render only around the star
        bx0, by0 = int(c[0] - R - 4), int(c[1] - R - 4); bw, bh = int(2 * R + 8), int(2 * R + 8)
        sub = np.zeros((bh * q, bw * q), np.uint8)
        pts = ((star_poly(c, R) - [bx0, by0]) * q).astype(np.int32)
        cv2.fillPoly(sub, [pts], 255)
        a = cv2.resize(sub, (bw, bh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        a *= (hidden[by0:by0 + bh, bx0:bx0 + bw] > 0)            # only where the letter hid it
        samp = out[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
        col = samp.mean(0) + rng.normal(0, 1, (bh, bw, 3)) * samp.std(0)
        reg = out[by0:by0 + bh, bx0:bx0 + bw].astype(np.float32)
        out[by0:by0 + bh, bx0:bx0 + bw] = np.clip(reg * (1 - a[..., None]) + col * a[..., None], 0, 255).astype(np.uint8)
    return out


def fix_tips(out, side):
    for (x0, y0, x1, y1), test in TIPS.get(side, []):
        lab = cv2.cvtColor(out[y0:y1, x0:x1], cv2.COLOR_RGB2LAB).astype(np.float32)
        if test == 'white':
            sel = (lab[..., 0] > np.percentile(lab[..., 0], 50) + 25)
        m = np.zeros(out.shape[:2], np.uint8)
        m[y0:y1, x0:x1] = cv2.dilate(sel.astype(np.uint8) * 255, disk(4))
        out = lama(out, m, pad=96)
    return out


def fix_serial(out, side):
    for (sx, sy, w, h), targets in SERIAL_FIX.get(side, []):
        glyph = out[sy:sy + h, sx:sx + w].astype(np.float32)
        yy, xx = np.mgrid[0:h, 0:w]
        e = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
        a = np.clip(e / 4, 0, 1)[..., None]                       # feathered patch edge
        for tx, ty in targets:
            dst = out[ty:ty + h, tx:tx + w].astype(np.float32)
            out[ty:ty + h, tx:tx + w] = (dst * (1 - a) + glyph * a).astype(np.uint8)
    return out


def remove(rgb, side):
    m = letters(rgb, side)
    out = rgb.copy()
    special = np.zeros_like(m)
    for pt, split in FILL_SPLIT.get(side, []):
        special |= fill_holes(component_at(m, pt))
    out = lama(out, m | special)
    for pt, split in FILL_SPLIT.get(side, []):
        me = fill_holes(component_at(m, pt))
        right = me.copy(); right[:, :split] = 0; right = cv2.dilate(right, disk(8)); right[:, :split - 8] = 0
        out = lama(out, right, pad=200)
        left = me.copy(); left[:, split:] = 0; left = cv2.dilate(left, disk(8)); left[:, split + 8:] = 0
        out = lama(out, left, pad=200)
    out = fix_stars(out, side, m | special)
    out = fix_tips(out, side)
    return fix_serial(out, side), m | special


def run(side, preview=False):
    art = os.path.join(ROOT, f'eur-500-{side}.png')
    keep = os.path.join(ROOT, 'source', f'{side}-artwork-specimen.png')
    if not os.path.exists(keep):
        shutil.copyfile(art, keep)
    rgb = np.asarray(Image.open(keep).convert('RGB'))
    if preview:
        m = letters(rgb, side)
        ov = rgb.copy(); ov[m > 0] = (0.4 * ov[m > 0] + [0, 150, 0]).astype(np.uint8)
        Image.fromarray(ov).save(os.path.join(ROOT, 'source', f'{side}-specimen-mask-preview.png'))
        print(side, 'mask px', int((m > 0).sum())); return
    out, _ = remove(rgb, side)
    Image.fromarray(out).save(art, optimize=True)
    print(side, ': specimen removed ->', art)


if __name__ == '__main__':
    sides = [a for a in sys.argv[1:] if a in ('front', 'back')] or ['front', 'back']
    for sd in sides:
        run(sd, '--preview' in sys.argv)
