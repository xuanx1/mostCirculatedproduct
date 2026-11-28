"""
Clean alpha extraction of each security feature, with edges detected from the image.

For every feature in extract_features.REGIONS (whose boxes are only seeds):
  1. ink vs paper is separated in Lab space (darkness + colour deviation from the
     local paper), with the threshold chosen automatically (Otsu) inside the seed box;
  2. the feature's own shape is recovered by morphology:
       graphic  - engraving is closed into one solid silhouette, holes filled
       text     - glyph strokes kept as they are (text lines / numerals / line art)
       foil     - the Kinegram is found by its colour (chroma), outline traced
       gold     - gold print found by its colour
       thread   - the dark metal windows
     and only connected pieces that belong to the seed (mostly inside it) are kept;
  3. alpha is binary with a ~1 px anti-aliased edge: inside the outline the pixels are
     fully opaque, outside fully transparent. No partial transparency, so no haze.

Writes, per feature:
  feature-crops/<side>/<id>.png        solid cut-out (silhouette, original pixels)
  feature-crops/<side>/<id>-ink.png    ink only (crisp strokes, paper removed)
  assets/layers/<side>-<id>.png        ink only, framed for the page (exploded view)
  assets/layers/<side>-<id>-cut.png    silhouette, framed for the page (glow highlight)
  assets/masks/*.png                   masks that clip the page's optical effects

Run via tools/extract_features.py (it calls this at the end), or directly:
  python tools/isolate_features.py
"""
import json, math, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_features as EF  # noqa: E402  (REGIONS, bbox, PAD, paths)

ROOT, VB_W, VB_H = EF.ROOT, EF.VB_W, EF.VB_H
OUT, MASKS = EF.OUT, EF.MASKS
LAYERS = os.path.join(ROOT, 'assets', 'layers')
MARGIN = 6          # note units of context around each seed box

# mode, closing radius (note units) for 'graphic', optional exclusion boxes (note units)
MODE = {
    ('front', 'hologram'):      ('shape', 0),        # the foil stripe is a die-cut band: its outline is the cut
    ('front', 'numeral'):       ('dark', 0),         # deep-intaglio 10000: dark ink only, counters open
    ('front', 'tactile-left'):  ('dark', 0),         # the 11 raised diagonal strokes
    ('front', 'tactile-right'): ('dark', 0),
    ('back', 'numeral-big'):    ('red', 0),          # the large vermilion 10000
    ('back', 'numeral-small'):  ('dark', 0),
    ('back', 'wordmark'):       ('dark', 0),         # NIPPON (source lettering for the latent NIPPON)
}
SKIP = {('front', 'watermark'), ('back', 'watermark'),   # rebuilt: tools/watermark.py
        ('front', 'seal'),                               # exact circle: tools/circle_cut.py
        ('front', 'portrait'), ('front', 'numeral-br'),    # Segment Anything: tools/sam_isolate.py
        ('front', 'cartouche'), ('back', 'station')}       # cut along their engraving: tools/engrave_cut.py
CLIP = set()
OVI_COUNTERS = []
HATCH_REMOVE = set()
LARGEST = set()
SEED_SOLID = set()
FILL_UNDER = {}
TRACED_SOLID = set()
FORCE = {}
THRESH = {}
EXCLUDE = {('front', 'numeral'): [(306.5, 100, 20, 90)]}   # the watermark window's ring, beside the last 0

# page masks: name -> (side, id, which)
PAGE_MASKS = {
    'holo-front':   ('front', 'hologram', 'cut'),
}


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def fill_holes(m):
    """Fill enclosed holes of a binary (0/255) mask."""
    h, w = m.shape
    ff = m.copy()
    pad = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 255)
    return m | cv2.bitwise_not(ff)


def keep_seeded(m, seed, min_inside=0.55, min_area=12):
    """Keep connected components that lie mostly inside the seed region."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros_like(m)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_area:
            continue
        comp = lab == i
        if (comp & seed).sum() / area >= min_inside:
            out[comp] = 255
    return out


def ink_map(rgb, mode):
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    bright = L >= np.percentile(L, 90)
    pL, pA, pB = np.median(L[bright]), np.median(A[bright]), np.median(B[bright])
    dark = np.clip(pL - L, 0, None)
    chroma = np.sqrt((A - pA) ** 2 + (B - pB) ** 2)
    if mode == 'dark':                           # dark print only: not the pale tints and guilloche under it
        ink = np.clip(pL - L - 25, 0, None) * 1.6
    elif mode == 'red':                          # vermilion / pink print (a* well above the paper)
        ink = np.clip(A - pA, 0, None) * 4.0
    elif mode == 'green':                          # green print only (the serials), not the brown script
        ink = np.clip(pA - A, 0, None) * 4.0
    elif mode == 'yellow':                       # bright yellow print only (the small 100s)
        ink = np.clip(B - pB, 0, None) * 3.0 * (L > 120)
    elif mode == 'script':                       # brown handwriting: warm hue, mid-dark, never black or grey
        warm = (B - pB > 10) & (A - pA > 2) & (L > 70) & (L < pL - 12)
        ink = np.where(warm, (pL - L) + (B - pB), 0).astype(np.float32)
    elif mode == 'black':                        # black ink only (signatures, titles): dark and neutral
        ink = dark * (np.abs(B - pB) < 12) * (np.abs(A - pA) < 12)
    elif mode == 'blue':                         # the blue ribbon only, not the print beside or over it
        ink = np.clip(pB - B, 0, None) * 3.0
    elif mode == 'foil':
        ink = chroma * 2.2 + np.abs(L - pL) * 0.8
    elif mode == 'gold':
        ink = chroma * 2.0 + dark * 0.6
    else:
        ink = dark + chroma * 0.8
    return ink, (pL, pA, pB)


def otsu(values):
    v = np.clip(values, 0, 255).astype(np.uint8).reshape(-1, 1)
    t, _ = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return float(t)


def clone(rgb, sx, sy, box, d, feather=1.5):
    """Clone-stamp: replace box (note units) with the image shifted by d (note units), feathered."""
    x, y, w, h = box
    dx, dy = d
    H, W = rgb.shape[:2]
    m = np.zeros((H, W), np.float32)
    m[int(y * sy):int((y + h) * sy), int(x * sx):int((x + w) * sx)] = 1
    m = cv2.GaussianBlur(m, (0, 0), feather * sx)[..., None]
    M = np.float32([[1, 0, -dx * sx], [0, 1, -dy * sy]])     # dst(x) = src(x + d)
    src = cv2.warpAffine(rgb, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return (rgb * (1 - m) + src * m).astype(np.uint8)


def isolate(im, side, fid, shape, g):
    mode, close_u = MODE[(side, fid)]
    W, H = im.size
    sx, sy = W / VB_W, H / VB_H
    s_avg = (sx + sy) / 2
    (_, _, _, _), (x, y, w, h) = EF.bbox(shape, g, 0)
    # working crop: seed box + context
    wx0, wy0 = max(0, x - MARGIN), max(0, y - MARGIN)
    wx1, wy1 = min(VB_W, x + w + MARGIN), min(VB_H, y + h + MARGIN)
    px = lambda X, Y: (int(round((X - wx0) * sx)), int(round((Y - wy0) * sy)))
    box = (int(round(wx0 * sx)), int(round(wy0 * sy)), int(round(wx1 * sx)), int(round(wy1 * sy)))
    rgb = np.asarray(im.crop(box).convert('RGB'))
    hh, ww = rgb.shape[:2]

    # seed: the given outline (rect / ellipse / polygon) in working-crop pixels
    seed_img = Image.new('L', (ww, hh), 0)
    d = ImageDraw.Draw(seed_img)
    if shape == 'ellipse':
        d.ellipse([*px(x, y), *px(x + w, y + h)], fill=255)
    elif shape == 'poly':
        d.polygon([px(a, b) for a, b in g], fill=255)
    else:
        d.rectangle([*px(x, y), *px(x + w, y + h)], fill=255)
    for ex, ey, ew, eh in EXCLUDE.get((side, fid), ()):
        d.rectangle([*px(ex, ey), *px(ex + ew, ey + eh)], fill=0)
    seed = np.asarray(seed_img) > 0

    if (side, fid) in FILL_UNDER:
        hole = np.zeros(rgb.shape[:2], np.uint8)
        for bx, by, bw, bh in FILL_UNDER[(side, fid)]:
            Lb = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0]
            y0_, y1_ = max(0, int((by - wy0) * sy)), max(0, int((by + bh - wy0) * sy))
            x0_, x1_ = max(0, int((bx - wx0) * sx)), max(0, int((bx + bw - wx0) * sx))
            box_ = np.zeros_like(hole); box_[y0_:y1_, x0_:x1_] = 255
            dark = (Lb < np.median(Lb[seed]) - 30).astype(np.uint8) * 255     # the overprinted characters
            hole |= dark & box_
        hole = cv2.dilate(hole, disk(2.5))
        rgb = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), hole, 6, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    ink, paper = ink_map(rgb, mode)
    t = otsu(ink[seed]) * THRESH.get((side, fid), 1.0)
    if mode in ('text', 'black', 'dark', 'red'):
        t = max(t * 0.85, 18)              # keep thin strokes
    m = ((ink > t) * 255).astype(np.uint8)
    m[~cv2.dilate(seed.astype(np.uint8), disk(1.5 * s_avg)).astype(bool)] = 0   # nothing far outside the seed
    if (side, fid) in CLIP:
        m[~seed] = 0                       # touches other print: don't let the closing fuse with it

    if mode == 'outlined':
        # fill every closed outline (the digits), then remove anything thin (open hatch lines)
        # and grow the surviving bodies back inside the filled shape: opening by reconstruction
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.3 * s_avg))
        filled = fill_holes(m)
        core = cv2.morphologyEx(filled, cv2.MORPH_OPEN, disk(close_u * s_avg))
        rec = core
        for _ in range(40):
            nxt = cv2.bitwise_and(cv2.dilate(rec, disk(2)), filled)
            if np.array_equal(nxt, rec):
                break
            rec = nxt
        m = keep_seeded(fill_holes(rec), seed, 0.6, int((1.0 * s_avg) ** 2 * 6))
        if (side, fid) in LARGEST:                     # one object: detach background hatching, keep it
            core = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(3 * s_avg))
            n, lab, st, _ = cv2.connectedComponentsWithStats(core, 8)
            if n > 1:
                core = ((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
                m = cv2.bitwise_and(cv2.dilate(core, disk(3.3 * s_avg)), m)   # regrow only near the core
        if (side, fid) == ('front', 'ovi-100'):
            # the counters of the 0s are paper, not ink. Each is searched for only inside its own 0
            # (OVI_COUNTERS, note units), as the paper there, merged and made convex, so it can't spill
            # through gaps in the 0's outline; only that is cut out of the filled digits.
            # script strokes stuck to the digits are thin: open them off (while the 0s are still solid),
            # then regrow only into the digits
            core = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(1.6 * s_avg))
            m = cv2.bitwise_and(cv2.dilate(core, disk(0.6 * s_avg)), m)
            bare = ((ink < t * 0.55) * 255).astype(np.uint8)
            bare = cv2.morphologyEx(bare, cv2.MORPH_OPEN, disk(0.6 * s_avg))
            counters = np.zeros_like(m)
            for ecx, ecy, erx, ery in OVI_COUNTERS:
                zone = np.zeros_like(m)
                cv2.ellipse(zone, (int((ecx - wx0) * sx), int((ecy - wy0) * sy)), (int(erx * sx), int(ery * sy)), 0, 0, 360, 255, -1)
                pts = cv2.findNonZero(cv2.bitwise_and(bare, zone))
                if pts is not None and len(pts) > 20:
                    cv2.fillConvexPoly(counters, cv2.convexHull(pts), 255)
            m = cv2.bitwise_and(m, cv2.bitwise_not(counters))
        cut = m
        strokes = cv2.bitwise_and(((ink > t * 0.9) * 255).astype(np.uint8), cv2.dilate(m, disk(1)))
    elif mode in ('graphic', 'foil', 'gold', 'thread', 'blue'):
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.25 * s_avg))              # specks
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(close_u * s_avg))          # engraving -> solid
        m = fill_holes(m)
        m = keep_seeded(m, seed, 0.5, int((0.4 * s_avg) ** 2 * 8))
        if mode == 'foil':
            # the foil is one convex die-cut shape: take the largest piece, trace it, smooth it
            cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if cnts:
                c = max(cnts, key=cv2.contourArea)
                hull = cv2.convexHull(c)
                m = np.zeros_like(m)
                cv2.fillPoly(m, [hull], 255)
        for poly in FORCE.get((side, fid), ()):
            cv2.fillPoly(m, [np.array([px(a, b) for a, b in poly], np.int32)], 255)
        cut = m
        strokes = cv2.bitwise_and(((ink > t * 0.9) * 255).astype(np.uint8), cv2.dilate(m, disk(1)))
    elif mode == 'quill':
        lab_ = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
        Lq, Aq, Bq = lab_[..., 0], lab_[..., 1], lab_[..., 2]
        gold = ((Bq - np.median(Bq)) > 10) & (Lq > 95) & ((Aq - np.median(Aq)) > -2)
        gm = (gold & seed).astype(np.uint8) * 255
        gm = cv2.morphologyEx(gm, cv2.MORPH_CLOSE, disk(0.7 * s_avg))
        gm = keep_seeded(gm, seed, 0.6, int((1.0 * s_avg) ** 2 * 4))
        # inside the feather, drop what is not the quill: black text over it and the blue ribbon
        cq = np.sqrt((Aq - np.median(Aq)) ** 2 + (Bq - np.median(Bq)) ** 2)
        foreign = ((Lq < 110) & (cq < 14)) | ((Bq - np.median(Bq)) < -8)
        foreign = cv2.dilate(foreign.astype(np.uint8), disk(0.25 * s_avg)) > 0
        # the feather's silhouette, then rebuild the feather under the text/ribbon from the gold around it
        gm = fill_holes(cv2.morphologyEx(gm, cv2.MORPH_CLOSE, disk(2.2 * s_avg)))
        n_, lab_cc, st_, _ = cv2.connectedComponentsWithStats(gm, 8)
        if n_ > 1:                                   # the feather is one piece
            gm = ((lab_cc == 1 + int(np.argmax(st_[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
        # the upper feather is convex: big outlined letters over its edge leave notches; close them with
        # the hull of the upper part and rebuild what was under the letters from the gold around it
        rows = (np.arange(gm.shape[0]) / sy + wy0) < 195
        upper = gm.copy(); upper[~rows] = 0
        pts = cv2.findNonZero(upper)
        added = np.zeros_like(gm)
        if pts is not None:
            cv2.fillConvexPoly(added, cv2.convexHull(pts), 255)
            added[~rows] = 0
            added = cv2.bitwise_and(added, cv2.bitwise_not(gm))
            gm = cv2.bitwise_or(gm, added)
        hole = ((foreign & (gm > 0)) | (added > 0)).astype(np.uint8) * 255
        rgb = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), hole, 5, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
        gm = cv2.morphologyEx(gm, cv2.MORPH_OPEN, disk(1.2 * s_avg))          # ragged bits of script/inkwell
        n_, lab_cc, st_, _ = cv2.connectedComponentsWithStats(gm, 8)
        if n_ > 1:
            gm = ((lab_cc == 1 + int(np.argmax(st_[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
        gm = ((cv2.GaussianBlur(gm.astype(np.float32), (0, 0), 1.0 * s_avg) > 127) * 255).astype(np.uint8)   # smooth edge
        cut = strokes = gm
    elif mode == 'shape':
        cut = (seed * 255).astype(np.uint8)
        strokes = cv2.bitwise_and(m, cut)
        if (side, fid) in HATCH_REMOVE:
            # straight background hatching (long diagonal/straight runs) is not part of the feature
            L = int(6 * s_avg)
            kernels = [np.eye(L, dtype=np.uint8), np.fliplr(np.eye(L, dtype=np.uint8)),
                       np.ones((1, L), np.uint8), np.ones((L, 1), np.uint8)]
            hatch = np.zeros_like(strokes)
            for k in kernels:
                hatch |= cv2.morphologyEx(strokes, cv2.MORPH_OPEN, k)
            strokes = cv2.bitwise_and(strokes, cv2.bitwise_not(cv2.dilate(hatch, disk(1))))
            strokes = keep_seeded(strokes, seed, 0.5, int((0.4 * s_avg) ** 2 * 4))
    elif mode == 'traced':
        # hand-traced outline: the shape is exact; ink = the printing inside it
        if (side, fid) in SEED_SOLID:
            cut = strokes = (seed * 255).astype(np.uint8)
        elif (side, fid) in TRACED_SOLID:
            # the reverse Merlion is the gold fill only: keep the gold inside the traced outline,
            # minus the thin contour line that runs around it
            gold, _ = ink_map(rgb, 'gold')
            inner = cv2.erode((seed * 255).astype(np.uint8), disk(1.4 * s_avg))
            gm = ((gold > otsu(gold[inner > 0]) * 0.8) * 255).astype(np.uint8) & inner
            gm = fill_holes(cv2.morphologyEx(gm, cv2.MORPH_CLOSE, disk(0.6 * s_avg)))
            gm = cv2.morphologyEx(gm, cv2.MORPH_OPEN, disk(0.5 * s_avg))
            cut = strokes = gm
        else:   # line art (the obverse Merlion is an outline only): the strokes are the shape
            strokes = cv2.bitwise_and(m, (seed * 255).astype(np.uint8))
            cut = cv2.dilate(strokes, disk(0.3 * s_avg))
    else:  # text / line art (incl. yellow marks and script)
        strokes = keep_seeded(m, seed, 0.55, int((0.25 * s_avg) ** 2 * 6))
        # a thin margin around the strokes; counters (inside O, A, D, 0, 4, 6...) stay open
        cut = cv2.dilate(strokes, disk(0.45 * s_avg))
    if mode == 'thread':
        strokes = cut

    # alpha: binary + ~1px anti-aliased edge
    def aa(binary):
        f = cv2.GaussianBlur(binary.astype(np.float32) / 255, (0, 0), 0.8)
        return np.clip((f - 0.5) * 2.2 + 0.5, 0, 1)

    a_cut = aa(cut)
    # ink: strokes fully opaque, with a short ramp only at stroke edges
    ramp = np.clip((ink - t * 0.75) / max(t * 0.5, 1), 0, 1)
    a_ink = np.maximum(ramp * (cv2.dilate(strokes, disk(1)) > 0), aa(cv2.erode(strokes, disk(1))))
    a_ink = np.clip(a_ink * (a_cut > 0.02 if mode not in ('text', 'black', 'dark', 'red') else 1), 0, 1)
    # colour for the ink layer: un-mix the paper from partially covered edge pixels
    pr = cv2.cvtColor(np.uint8([[paper]]), cv2.COLOR_LAB2RGB)[0, 0].astype(np.float32)
    safe = np.maximum(a_ink, 0.15)[..., None]
    ink_rgb = np.clip((rgb.astype(np.float32) - pr * (1 - safe)) / safe, 0, 255)

    cut_rgba = np.dstack([rgb, (a_cut * 255).astype(np.uint8)])
    ink_rgba = np.dstack([ink_rgb.astype(np.uint8), (a_ink * 255).astype(np.uint8)])
    return dict(cut=cut_rgba, ink=ink_rgba, origin=(wx0, wy0), box_px=box, sx=sx, sy=sy, t=t, mask=cut)


def trim(arr, margin=12):
    a = arr[..., 3]
    ys, xs = np.where(a > 6)
    if not len(xs):
        return arr
    y0, y1 = max(0, ys.min() - margin), min(arr.shape[0], ys.max() + margin + 1)
    x0, x1 = max(0, xs.min() - margin), min(arr.shape[1], xs.max() + margin + 1)
    return arr[y0:y1, x0:x1]


def page_frame(res, side, fid, shape, g, arr):
    """Re-frame onto the PAD box the page uses (data.js / script.js boxes) at 1.5x screen size."""
    (x0, y0, x1, y1), _ = EF.bbox(shape, g, EF.PAD)
    sx, sy = res['sx'], res['sy']
    ox, oy = res['box_px'][:2]
    bx0, by0 = int(round(x0 * sx)) - ox, int(round(y0 * sy)) - oy
    bx1, by1 = int(round(x1 * sx)) - ox, int(round(y1 * sy)) - oy
    H, W = arr.shape[:2]
    frame = np.zeros((by1 - by0, bx1 - bx0, 4), np.uint8)
    sx0, sy0 = max(0, bx0), max(0, by0)
    sx1, sy1 = min(W, bx1), min(H, by1)
    frame[sy0 - by0:sy1 - by0, sx0 - bx0:sx1 - bx0] = arr[sy0:sy1, sx0:sx1]
    img = Image.fromarray(frame, 'RGBA')
    scale = 1440 / (VB_W * sx) * 1.5
    return img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)


def main():
    os.makedirs(LAYERS, exist_ok=True)
    os.makedirs(MASKS, exist_ok=True)
    imgs = {s: Image.open(os.path.join(ROOT, f)).convert('RGB') for s, f in EF.SRC.items()}
    framed = {}
    report = []
    full_masks = {}
    results = {}
    order = list(EF.REGIONS)
    for fid, side, label, shape, g in order:
        if (side, fid) in SKIP:
            continue
        src = imgs[side]
        res = isolate(src, side, fid, shape, g)
        results[(side, fid)] = res
        d = os.path.join(OUT, side)
        os.makedirs(d, exist_ok=True)
        if not any(os.path.exists(os.path.join(ROOT, 'assets', 'overrides', f'{side}-{fid}{x}.png')) for x in ('', '-cut')):
            Image.fromarray(trim(res['cut']), 'RGBA').save(os.path.join(d, f'{fid}.png'), optimize=True)
            Image.fromarray(trim(res['ink']), 'RGBA').save(os.path.join(d, f'{fid}-ink.png'), optimize=True)
        # (hand-cleaned features keep the cleaned image in feature-crops: no auto copy is written)
        pc = page_frame(res, side, fid, shape, g, res['cut'])
        pi = page_frame(res, side, fid, shape, g, res['ink'])
        # hand-edited images in assets/overrides/ always win (see assets/overrides/README.txt)
        ov = os.path.join(ROOT, 'assets', 'overrides')
        for name, key in ((f'{side}-{fid}.png', 'ink'), (f'{side}-{fid}-cut.png', 'cut')):
            if os.path.exists(os.path.join(ov, name)):
                img = Image.open(os.path.join(ov, name)).convert('RGBA').resize((pc if key == 'cut' else pi).size, Image.LANCZOS)
                if key == 'cut':
                    pc = img
                else:
                    pi = img
                report.append(f'      using override {name}')
        pc.save(os.path.join(LAYERS, f'{side}-{fid}-cut.png'), optimize=True)
        pi.save(os.path.join(LAYERS, f'{side}-{fid}.png'), optimize=True)
        framed[(side, fid)] = {'cut': pc, 'ink': pi}
        if (side, fid) in OFFSET_BLOBS:
            x0, y0, x1, y1 = res['box_px']
            mk = full_masks.setdefault(side + ':' + fid, np.zeros((imgs[side].height, imgs[side].width), np.uint8))
            mk[y0:y1, x0:x1] = np.maximum(mk[y0:y1, x0:x1], res['mask'])
        report.append(f'{side:5} {fid:18} {MODE[(side, fid)][0]:8} t={res["t"]:.0f}')
    # the rebuilt watermark has no separate silhouette: reuse it for the glow
    # (the watermark ghost glows on its own image: no -cut copy)
    # page masks (white + alpha), kept light
    for name, (side, fid, which) in PAGE_MASKS.items():
        ovp = os.path.join(ROOT, 'assets', 'overrides', f'{side}-{fid}{"-cut" if which == "cut" else ""}.png')
        src_img = Image.open(ovp).convert('RGBA') if os.path.exists(ovp) else framed[(side, fid)][which]
        a = src_img.getchannel('A')          # hand-cleaned images shape the effects too
        m = Image.new('RGBA', a.size, (255, 255, 255, 0))
        m.putalpha(a)
        k = min(1.0, 900 / max(m.size))
        if k < 1:
            m = m.resize((round(m.width * k), round(m.height * k)), Image.LANCZOS)
        m.save(os.path.join(MASKS, f'{name}.png'), optimize=True)
    # page boxes: where each framed layer sits on the note (note units), read by the page
    boxes = {}
    for fid, side, label, shape, g in EF.REGIONS:
        (x0, y0, x1, y1), _ = EF.bbox(shape, g, EF.PAD)
        boxes[f'{side}-{fid}'] = [round(x0, 2), round(y0, 2), round(x1 - x0, 2), round(y1 - y0, 2)]
    with open(os.path.join(ROOT, 'assets', 'boxes.js'), 'w', encoding='utf8') as f:
        f.write('// generated by tools/isolate_features.py: where each extracted layer sits (720x320 note units)' + chr(10))
        f.write('const BOXES = ' + json.dumps(boxes, indent=1) + ';' + chr(10))
    write_offset_layers(imgs, full_masks)
    import shutil
    shutil.rmtree(MASKS, ignore_errors=True)          # embedded in assets/masks.css; no loose copies
    # (assets/masks.css and the unused-layer clean-up are done last, by tools/build.py)
    print('\n'.join(report))
    contact_sheet()


# solid features (not ink lines) removed from the offset print
OFFSET_BLOBS = {('front', 'hologram')}          # the foil is not print: filled from the paper around it
# the artwork's own watermark areas (the watermark lives in the paper layer)
OFFSET_ELLIPSES = {'front': [], 'back': []}


def write_offset_layers(imgs, masks):
    """Offset-print layers: what is printed under the intaglio.
    Intaglio/letterpress are dark ink lines over light offset tints. A per-channel morphological
    closing spreads the light tint over the dark lines (a line is thinner than the kernel, so the
    tint on either side closes over it), keeping the tint's local texture. Lines are found as
    pixels darker than their local background; only those pixels are replaced. Solid features
    (foil, gold patch, thread windows, the artwork's own watermark) are then filled from the
    cleaned surroundings."""
    for side, im in imgs.items():
        W, H = im.size
        sx, sy = W / VB_W, H / VB_H
        rgb = np.asarray(im.convert('RGB'))
        L = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        k = disk(7)
        closed = cv2.merge([cv2.morphologyEx(rgb[..., c], cv2.MORPH_CLOSE, k) for c in range(3)])
        closed = cv2.merge([cv2.morphologyEx(closed[..., c], cv2.MORPH_CLOSE, disk(11)) for c in range(3)])
        bgL = cv2.cvtColor(closed, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        a = np.clip((bgL - L - 6) / 14, 0, 1)                      # how much darker than the tint
        a = cv2.GaussianBlur(a, (0, 0), 1.0)[..., None]
        out = (rgb * (1 - a) + closed * a).astype(np.uint8)
        # solid features + old watermark
        blobs = np.zeros((H, W), np.uint8)
        for key in OFFSET_BLOBS:
            if key[0] == side and (side + ':' + key[1]) in masks:
                blobs = np.maximum(blobs, masks[side + ':' + key[1]])
        for cx, cy, rx, ry in OFFSET_ELLIPSES[side]:
            cv2.ellipse(blobs, (int(cx * sx), int(cy * sy)), (int(rx * sx), int(ry * sy)), 0, 0, 360, 255, -1)
        blobs = cv2.dilate((blobs > 40).astype(np.uint8) * 255, disk(5))
        q = 4
        small = cv2.resize(out, (W // q, H // q), interpolation=cv2.INTER_AREA)
        ms = cv2.resize(blobs, (W // q, H // q), interpolation=cv2.INTER_NEAREST)
        f = cv2.inpaint(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), ms, 12, cv2.INPAINT_TELEA)
        f = cv2.cvtColor(cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
        b = cv2.GaussianBlur(blobs.astype(np.float32) / 255, (0, 0), 3.0)[..., None]
        out = (out * (1 - b) + f * b).astype(np.uint8)
        Image.fromarray(out).resize((2160, 1026), Image.LANCZOS).save(
            os.path.join(ROOT, 'assets', f'offset-{side}.jpg'), quality=90, optimize=True)


def linework_rules():
    """Line-work of each face (engraved lines darker than their surroundings) as mask rules,
    for the gold flow through the guilloche."""
    import base64, io
    rules = []
    for side, cls in (('front', '.flow-front'), ('back', '.flow-back')):
        im = Image.open(os.path.join(ROOT, EF.SRC[side])).convert('RGB').resize((1080, 513), Image.LANCZOS)
        L = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(4)), (0, 0), 3)
        lines = (bg - L - 8) > 0                          # binary: compresses far better, the sweep softens it
        m = Image.new('LA', im.size, 255)
        m.putalpha(Image.fromarray((lines * 255).astype(np.uint8)))
        m = m.convert('LA')
        a = m.getchannel('A').convert('1')
        buf = io.BytesIO(); a.save(buf, 'PNG', optimize=True)          # 1-bit image used as a luminance mask
        u = f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'
        rules.append(f'{cls}{{-webkit-mask-mode:luminance;mask-mode:luminance;}}')
        rules.append(f'{cls}{{-webkit-mask-image:{u};mask-image:{u}}}')
    return rules


def write_mask_css():
    """Masks as data URIs. Browsers fetch mask images with CORS, which file:// can't satisfy; data
    URIs always load, so the page also works opened from disk. Plain rules (not CSS variables): a
    variable holding a data URI is re-parsed on every style recalc."""
    import base64, io
    def uri(img, maxside=600):
        if img is None:
            return None
        img = img.convert('RGBA')
        k = min(1.0, maxside / max(img.size))
        if k < 1:
            img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
        m = Image.new('LA', img.size, 255)
        m.putalpha(img.getchannel('A'))
        buf = io.BytesIO(); m.save(buf, 'PNG', optimize=True)
        return f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'
    L = lambda n: Image.open(os.path.join(LAYERS, n)) if os.path.exists(os.path.join(LAYERS, n)) else None
    rules = {
        '.holo-diff, .holo-face, .holo-spec': uri(L('front-hologram-cut.png')),     # the foil stripe
        '.latent-front': uri(L('latent-front-mask.png'), 900),                  # the 10000 hidden in the cartouche (tools/latent.py)
        '.latent-back': uri(L('latent-back-mask.png'), 900),                    # NIPPON on the reverse
        '.pearl-fx': uri(L('pearl-mask.png'), 900),                             # the two pearl-ink margins (tools/pearl.py)
    }
    out = ['/* generated by tools/isolate_features.py: effect masks as data URIs, as plain rules so they are parsed once */']
    for sel, u in rules.items():
        if u is None:
            continue
        out.append(f'{sel}{{-webkit-mask-image:{u};mask-image:{u}}}')
    out += linework_rules()
    open(os.path.join(ROOT, 'assets', 'masks.css'), 'w', encoding='utf8').write('\n'.join(out))


def contact_sheet():
    files = []
    for side in ('front', 'back'):
        d = os.path.join(OUT, side)
        for f in sorted(os.listdir(d)):
            if f.endswith('.png') and not f.endswith('-ink.png'):
                files += [(side, f), (side, f.replace('.png', '-ink.png'))]
    cols, cw, ch = 6, 280, 230
    rows = math.ceil(len(files) / cols)
    sheet = Image.new('RGB', (cols * cw, rows * ch), 'white')
    chk = Image.new('RGB', (cw, ch))
    dc = ImageDraw.Draw(chk)
    for yy in range(0, ch, 10):
        for xx in range(0, cw, 10):
            dc.rectangle([xx, yy, xx + 9, yy + 9], fill=(205, 205, 205) if (xx + yy) // 10 % 2 else (245, 245, 245))
    ds = ImageDraw.Draw(sheet)
    for i, (side, f) in enumerate(files):
        p = os.path.join(OUT, side, f)
        if not os.path.exists(p):
            continue
        t = Image.open(p)
        t.thumbnail((260, 200))
        cx, cy = (i % cols) * cw, (i // cols) * ch
        sheet.paste(chk, (cx, cy))
        sheet.paste(t, (cx + (cw - t.width) // 2, cy + 8), t)
        ds.text((cx + 6, cy + ch - 18), f'{side}/{f}', fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, 'contact-sheet.png'))


if __name__ == '__main__':
    main()
