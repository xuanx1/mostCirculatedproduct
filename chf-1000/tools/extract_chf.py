"""
Cut the CHF 1000 note's security features out of the working artwork as clean alpha layers.

Note space: 320 x 722 units over the whole note (70 x 158 mm, portrait). The working artwork
(chf-1000-front.png / -back.png, 1600 x 3610) has exactly 5 px per unit, so every box below is a
whole-pixel crop and every layer keeps the artwork's original pixels (nothing is resampled).

For each feature it writes
  assets/layers/<side>-<id>.png       the feature on transparency, framed to its box (BOXES)
  feature-crops/<side>/<id>.png       the same, trimmed to its content (for review)
and also
  assets/boxes.js                     where every layer sits, in note units
  assets/masks.css                    masks for the optical effects, as data URIs (file:// safe)
  assets/offset-front.jpg / -back.jpg the offset print, with the separately layered features removed

How each edge is found ('mode'):
  sam       the handshake: Segment Anything (tools/sam_isolate.py writes the mask), cleaned here
  circle    the globe: an exact circle fitted to the sphere's rim
  numeral   the big intaglio 1000s: purple ink on light paper; small closing to make the guilloche
            inside the digits solid, then only small holes filled (the counters of the 0s stay open)
  gold      gold lettering (bank name): selected by colour, strokes kept, counters open
  dark      dark text on a busy ground (serials, microtext, tactile bars): ink darker than its own
            local background (black-hat), strokes kept
  chroma    the coloured corner marks of the see-through register on white
  rect/poly exact geometric shapes (security strip band, the window cross)

Hand-cleaned files in assets/overrides/ always win and are never overwritten.

  python tools/extract_chf.py            (run tools/sam_isolate.py first for the hand)
"""
import base64, io, json, math, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {'front': 'chf-1000-front.png', 'back': 'chf-1000-back.png'}
VW, VH, PX = 320, 722, 5
LAYERS = os.path.join(ROOT, 'assets', 'layers')
CROPS = os.path.join(ROOT, 'feature-crops')
OVR = os.path.join(ROOT, 'assets', 'overrides')
WORK = os.path.join(ROOT, 'source', 'masks')          # SAM masks (written by sam_isolate.py)

# the window cross (front coordinates): two bars, measured on the artwork
CROSS = [(63, 36, 17.5, 55), (45, 53, 53, 18)]        # x, y, w, h of the vertical and horizontal bars
STRIP = (0, 449, 320, 70)                             # security strip: full width, y 449..519
GLOBE = (221.5, 400.5, 68.5)                          # centre x, y, radius of the shimmering globe
ONE_BACK = [(31.7, 28), (39, 28), (39, 88.3), (27.7, 88.3), (27.7, 44.7), (14.7, 48.3), (12.3, 40.7)]   # the back's '1'
TACTILE_Y = [(38, 81), (160, 202), (281, 323), (401, 444), (527, 569), (648, 690)]   # six blocks a side

# id, side, box [x, y, w, h] (note units), mode, options
FEATURES = [
    ('hand',       'front', [0, 84, 320, 238],   'sam',     {}),
    ('globe',      'front', [150, 329, 143, 143], 'circle', {}),
    ('numeral',    'front', [16, 572, 202, 89],  'numeral', {}),
    ('bankname',   'front', [16, 657, 252, 45],  'gold',    {}),
    ('strip',      'front', list(STRIP),          'rect',    {}),
    ('cross',      'front', [42, 33, 59, 61],     'cross',   {}),
    ('register',   'front', [176, 537, 36, 35],   'chroma',  {}),
    ('microtext',  'front', [26, 158, 78, 76],    'micro',   {}),
    ('tactile',    'front', [0, 34, 320, 660],    'tactile', {}),
    ('numeral',    'back',  [6, 16, 186, 76],     'hatched', {}),
    ('bankname',   'back',  [10, 420, 48, 284],   'gold',    {}),
    ('serial-a',   'back',  [277, 207, 18, 139],  'dark',    {'k': 2.5, 'gain': 1.0, 'min': 3.0}),
    ('serial-b',   'back',  [70, 466, 17, 121],   'dark',    {'k': 2.5, 'gain': 1.0, 'min': 3.0}),
    ('register',   'back',  [112, 531, 38, 36],   'chroma',  {}),
    ('cross',      'back',  [219, 33, 59, 61],    'cross',   {}),
]


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def fill_small_holes(m, max_area):
    inv = cv2.bitwise_not(m)
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    out = m.copy()
    for k in range(1, n):
        x, y, w, h, a = st[k]
        touches = x == 0 or y == 0 or x + w >= m.shape[1] or y + h >= m.shape[0]
        if not touches and a <= max_area:
            out[lab == k] = 255
    return out


def keep_big(m, min_area):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros_like(m)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] >= min_area:
            out[lab == k] = 255
    return out


def aa(binary, sigma=0.8):
    """binary mask -> alpha with a ~1 px anti-aliased edge (no haze)"""
    f = cv2.GaussianBlur(binary.astype(np.float32) / 255, (0, 0), sigma)
    return np.clip((f - 0.5) * 2.2 + 0.5, 0, 1)


def otsu(values):
    v = np.clip(values, 0, 255).astype(np.uint8).reshape(-1, 1)
    t, _ = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return float(t)


def lab_of(rgb):
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    return lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128


def blackhat(L, k_px):
    bg = cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(k_px))
    return np.clip(bg - L, 0, None)


def px(box):
    x, y, w, h = box
    return int(round(x * PX)), int(round(y * PX)), int(round((x + w) * PX)), int(round((y + h) * PX))


def isolate(im, fid, side, box, mode, opt):
    x0, y0, x1, y1 = px(box)
    rgb = np.asarray(im)[y0:y1, x0:x1].copy()
    H, W = rgb.shape[:2]
    L, A, B = lab_of(rgb)
    strokes = None
    if mode == 'sam':
        p = os.path.join(WORK, f'{side}-{fid}.png')
        full = np.asarray(Image.open(p).convert('L'))
        m = (full[y0:y1, x0:x1] > 127).astype(np.uint8) * 255
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)          # the hands are one piece
        m = ((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
        m = fill_small_holes(m, int((14 * PX) ** 2))                     # SPECIMEN letters / highlights inside
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(4 * PX))            # ragged background tiles at the wrists
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
        m = ((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))) * 255).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(1.2 * PX))         # notches between the fingers' outlines
        m = ((cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2 * PX) > 127) * 255).astype(np.uint8)   # smooth contour
        cut = m
    elif mode == 'circle':
        cx, cy, r = GLOBE
        m = np.zeros((H, W), np.uint8)
        k = 4
        big = np.zeros((H * k, W * k), np.uint8)
        cv2.circle(big, (int((cx * PX - x0) * k), int((cy * PX - y0) * k)), int(r * PX * k), 255, -1, cv2.LINE_AA)
        a = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        return rgb, a, a
    elif mode == 'rect':
        a = np.ones((H, W), np.float32)
        return rgb, a, a
    elif mode == 'cross':
        k = 4
        big = np.zeros((H * k, W * k), np.uint8)
        for bx, by, bw, bh in CROSS:
            if side == 'back':
                bx = VW - bx - bw
            X0, Y0 = (bx * PX - x0) * k, (by * PX - y0) * k
            cv2.rectangle(big, (int(X0), int(Y0)), (int(X0 + bw * PX * k), int(Y0 + bh * PX * k)), 255, -1)
        big = cv2.morphologyEx(big, cv2.MORPH_OPEN, disk(1.2 * PX * k))   # the window's corners are softly rounded
        a = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        return rgb, a, a
    elif mode == 'numeral':
        bright = L >= np.percentile(L, 85)
        pL = np.median(L[bright])
        ink = np.clip(pL - L, 0, None) + np.clip(-B, 0, None) * 1.5      # purple: dark and blue
        t = otsu(ink)
        m = ((ink > t) * 255).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(1.0 * PX))           # guilloche inside the digits -> solid
        m = fill_small_holes(m, int((9 * PX) ** 2))                         # pattern gaps, not the 0s' counters
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(1.2 * PX))            # thin strays (SPECIMEN edges, lines)
        m = keep_big(m, int((10 * PX) ** 2))
        cut = m
        strokes = m
    elif mode == 'hatched':
        # the back's 1000: dark diagonal hatching inside a dark outline, the 1 on a purple ground.
        # Dark pixels only, hatching closed into solid digits, thin lines (the network's curves) opened off
        m = ((L < 92) * 255).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.9 * PX))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(1.6 * PX))
        m = fill_small_holes(m, int((6 * PX) ** 2))
        # the 1 stands on the purple ground, where darkness cannot tell it apart: it is cut to its outline,
        # traced on the artwork (note units); the three 0s on the light ground come from the threshold
        m[:, :int((50 - box[0]) * PX)] = 0
        k = 4
        big = Image.new('L', (W * k, H * k), 0)
        ImageDraw.Draw(big).polygon([((x - box[0]) * PX * k, (y - box[1]) * PX * k) for x, y in ONE_BACK], fill=255)
        one = np.asarray(big.resize((W, H), Image.LANCZOS))
        m = keep_big(m, int((12 * PX) ** 2))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(2.8 * PX))            # lattice texture stuck to the first 0
        m = keep_big(m, int((12 * PX) ** 2))
        m = np.maximum(m, ((one > 127) * 255).astype(np.uint8))
        cut = m
        strokes = m
    elif mode == 'micro':
        # the microtext: two blocks of tiny lettering at position B, measured on the artwork: dark letters on
        # a light ground (upper block) and light letters on a dark ground (lower block, cut by the yellow
        # diagonal). Inside each block only the letters' own marks are kept (no box of background)
        blocks = [('dark', [(29, 163), (57, 163), (57, 196), (29, 196)]),
                  ('light', [(29, 199), (48, 199), (48, 214), (70, 214), (70, 233), (52, 233), (29, 213)])]
        rows = np.zeros((H, W), np.uint8)
        for kind, poly in blocks:
            sm = np.zeros((H, W), np.uint8)
            cv2.fillPoly(sm, [np.array([((x - box[0]) * PX, (y - box[1]) * PX) for x, y in poly], np.int32)], 255)
            f = blackhat(L, 1.0 * PX) if kind == 'dark' else np.clip(L - cv2.morphologyEx(L, cv2.MORPH_OPEN, disk(1.0 * PX)), 0, None)
            t = max(otsu(f[sm > 0]), 6)
            mm = ((f > t) & (sm > 0)).astype(np.uint8) * 255
            if kind == 'light':                                            # not the yellow guilloche below the diagonal
                mm[(B > 25)] = 0
            rows |= keep_big(mm, 3)
        m = rows
        strokes = m
        cut = cv2.dilate(m, disk(0.25 * PX))
    elif mode == 'gold':
        gold = (B > 22) & (A > -8) & (L > 60) & (L < 215)
        m = gold.astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.25 * PX))
        m = keep_big(m, int((0.9 * PX) ** 2 * 3))
        strokes = m
        cut = cv2.dilate(m, disk(0.3 * PX))
    elif mode == 'chroma':
        chroma = np.sqrt(A ** 2 + B ** 2)
        m = ((chroma > 22) & (L < 235)).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.3 * PX))
        m = keep_big(m, int((1.2 * PX) ** 2 * 4))
        # the yellow rings (and anything else yellow) near the marks are not part of them
        if side == 'front':                                              # the yellow rings beside the front marks
            yellow = ((B > 40) & (A < 5)).astype(np.uint8) * 255
            m[cv2.dilate(yellow, disk(1)) > 0] = 0
        m = keep_big(m, int((1.2 * PX) ** 2 * 4))
        strokes = m
        cut = cv2.dilate(m, disk(0.3 * PX))
    elif mode in ('dark', 'tactile'):
        k = opt.get('k', 2.0)
        bh = blackhat(L, k * PX)
        if mode == 'tactile':
            seed = np.zeros((H, W), np.uint8)
            for ya, yb in TACTILE_Y:
                for xa, xb in ((0, 12), (308, 320)):
                    seed[int((ya - box[1]) * PX):int((yb - box[1]) * PX), int((xa - box[0]) * PX):int((xb - box[0]) * PX)] = 255
            bh = blackhat(L, 2.2 * PX)
            t = max(otsu(bh[seed > 0]), 14)
            m = ((bh > t) & (seed > 0)).astype(np.uint8) * 255
            m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, disk(0.4 * PX))
            m = keep_big(m, int((1.0 * PX) ** 2 * 3))
            # the bars are straight horizontal dashes: drop anything that is not wider than tall
            n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
            keep = np.zeros_like(m)
            for i in range(1, n):
                x, y, w, h, a = st[i]
                if w > 2.2 * h and h < 2.6 * PX:
                    keep[lab == i] = 255
            m = keep
        else:
            t = max(otsu(bh), 10) * opt.get('gain', 1.0)
            m = ((bh > t) * 255).astype(np.uint8)
            m = keep_big(m, 6)
            if opt.get('min'):                                           # whole characters only: no specks
                n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(m, disk(0.6 * PX)), 8)
                keep = np.zeros_like(m)
                for i in range(1, n):
                    if max(st[i, 2], st[i, 3]) >= opt['min'] * PX:
                        keep[lab == i] = 255
                m = m & keep
        strokes = m
        cut = cv2.dilate(m, disk(0.25 * PX))
    else:
        raise ValueError(mode)
    a_cut = aa(cut)
    if strokes is None:
        a_ink = a_cut
    else:
        a_ink = np.maximum(aa(strokes, 0.6), 0)
    return rgb, a_cut, a_ink


def rgba(rgb, a):
    al = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    rgb = rgb.copy()
    rgb[al == 0] = 0                                  # fully transparent pixels carry no colour: small files
    return Image.fromarray(np.dstack([rgb, al]), 'RGBA')


def trim(img, margin=10):
    bb = img.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    if not bb:
        return img
    l, t, r, b = bb
    return img.crop((max(0, l - margin), max(0, t - margin), min(img.width, r + margin), min(img.height, b + margin)))


def save_layer(name, img):
    ov = os.path.join(OVR, name)
    if os.path.exists(ov):
        print('   using override', name)
        img = Image.open(ov).convert('RGBA').resize(img.size, Image.LANCZOS)
    img.save(os.path.join(LAYERS, name), optimize=True)
    return img


def mask_uri(img_alpha, max_side=700, mode='alpha'):
    a = img_alpha
    k = min(1.0, max_side / max(a.size))
    if k < 1:
        a = a.resize((max(1, round(a.width * k)), max(1, round(a.height * k))), Image.LANCZOS)
    m = Image.new('LA', a.size, 255)
    m.putalpha(a)
    buf = io.BytesIO()
    m.save(buf, 'PNG', optimize=True)
    return f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'


def main():
    os.makedirs(LAYERS, exist_ok=True)
    imgs = {s: Image.open(os.path.join(ROOT, f)).convert('RGB') for s, f in SRC.items()}
    boxes, report, made = {}, [], {}
    for fid, side, box, mode, opt in FEATURES:
        rgb, a_cut, a_ink = isolate(imgs[side], fid, side, box, mode, opt)
        name = f'{side}-{fid}'
        cut = save_layer(f'{name}-cut.png', rgba(rgb, a_cut))
        ink = save_layer(f'{name}.png', rgba(rgb, a_ink))
        made[name] = (cut, ink)
        os.makedirs(os.path.join(CROPS, side), exist_ok=True)
        trim(cut).save(os.path.join(CROPS, side, f'{fid}.png'), optimize=True)
        boxes[name] = box
        report.append(f'{side:5} {fid:10} {mode:8} {box}')
    extras(imgs, boxes, made)
    with open(os.path.join(ROOT, 'assets', 'boxes.js'), 'w', encoding='utf8') as f:
        f.write('// generated by tools/extract_chf.py: where each layer sits (320 x 722 note units)\n')
        f.write('const BOXES = ' + json.dumps(boxes) .replace('], ', '],\n  ').replace('{', '{\n  ').replace('}', '\n}') + ';\n')
    offset_layers(imgs, made, boxes)
    write_masks(imgs, made, boxes)
    print('\n'.join(report))


# ---------------------------------------------------------------- generated (not cut) layers
FLAG_WM = (97, 622, 56)            # Swiss-flag watermark: centre x, y, side (illustrative size; SNB brochure photo)
GLOBE_WM = (218, 586, 55)          # globe watermark: centre x, y, radius (from the SNB brochure's transmitted-light photo)
WM_BOX = [62, 526, 216, 132]       # one image holds both watermarks
UVG = (221, 93, 67)                # ultraviolet globe: centre x, y, radius (SNB brochure UV photo, scaled to the note)
TRI = [(38, 293), (64, 247), (90, 293)]   # the triangle window on the back
THREAD_Y = (271, 283)              # the security thread: a horizontal band, seen in the triangle


def extras(imgs, boxes, made):
    """Layers that cannot be cut from a reflected-light photo: drawn from the SNB's descriptions."""
    S = PX
    # ---- watermark: the note's own globe as soft continuous tone + the outline of the Swiss flag
    x, y, w, h = WM_BOX
    W, H = w * S, h * S
    tone = np.zeros((H, W), np.float32)
    front = np.asarray(imgs['front'].convert('L')).astype(np.float32)
    gx, gy, gr = GLOBE
    src = front[int((gy - gr) * S):int((gy + gr) * S), int((gx - gr) * S):int((gx + gr) * S)]
    cx, cy, r = GLOBE_WM
    d = int(2 * r * S)
    src = cv2.resize(src, (d, d), interpolation=cv2.INTER_AREA)
    src = cv2.GaussianBlur(src, (0, 0), 6)                                # engraving -> continuous tone
    t = np.clip((np.percentile(src, 97) - src) / max(np.percentile(src, 97) - np.percentile(src, 3), 1), 0, 1)
    yy, xx = np.mgrid[0:d, 0:d]
    rr = np.hypot(xx - d / 2, yy - d / 2) / (d / 2)
    disc = np.clip((1 - rr) / 0.06, 0, 1)
    rim = np.exp(-((rr - 0.97) / 0.035) ** 2) * 0.55                     # watermarks show their outline darker
    g = (0.25 + 0.55 * t) * disc + rim
    ox, oy = int((cx - r - x) * S), int((cy - r - y) * S)
    tone[oy:oy + d, ox:ox + d] = np.maximum(tone[oy:oy + d, ox:ox + d], g)
    # flag: a square outline with the cross outline inside (the brochure: "the outline of the Swiss flag")
    fx, fy, fs = FLAG_WM
    k = 4
    big = Image.new('L', (W * k, H * k), 0)
    dr = ImageDraw.Draw(big)
    X0, Y0 = (fx - fs / 2 - x) * S * k, (fy - fs / 2 - y) * S * k
    side = fs * S * k
    lw = int(2.0 * S * k)
    dr.rounded_rectangle([X0, Y0, X0 + side, Y0 + side], radius=int(2 * S * k), outline=255, width=lw)
    arm, bar = side * 0.56 / 2, side * 0.18 / 2                           # Swiss cross proportions
    c0x, c0y = X0 + side / 2, Y0 + side / 2
    pts = [(c0x - bar, c0y - arm), (c0x + bar, c0y - arm), (c0x + bar, c0y - bar), (c0x + arm, c0y - bar),
           (c0x + arm, c0y + bar), (c0x + bar, c0y + bar), (c0x + bar, c0y + arm), (c0x - bar, c0y + arm),
           (c0x - bar, c0y + bar), (c0x - arm, c0y + bar), (c0x - arm, c0y - bar), (c0x - bar, c0y - bar)]
    dr.polygon(pts, outline=255, width=lw)
    fl = np.asarray(big.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5)), np.float32) / 255
    tone = np.maximum(tone, fl)
    col = np.empty((H, W, 3), np.float32)
    col[...] = (88, 70, 92)                                               # a neutral, slightly violet paper shadow
    wm = Image.fromarray(np.dstack([col, np.clip(tone, 0, 1) * 255]).astype(np.uint8), 'RGBA')
    save_layer('watermark-ghost.png', wm)
    boxes['watermark-ghost'] = WM_BOX
    os.makedirs(os.path.join(CROPS, 'front'), exist_ok=True)
    trim(wm).save(os.path.join(CROPS, 'front', 'watermark.png'), optimize=True)

    # ---- the ultraviolet globe, from the SNB brochure's own UV photograph (source/found/)
    p = os.path.join(ROOT, 'source', 'found', 'snb-brochure-uv-globe.png')
    if os.path.exists(p):
        uv = np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
        # the globe disc in that photo (pixels): fitted by hand on the photo, see README
        ucx, ucy, ur = UV_SRC_CIRCLE
        crop = uv[int(ucy - ur):int(ucy + ur), int(ucx - ur):int(ucx + ur)]
        cx, cy, r = UVG
        d = int(2 * r * S)
        crop = cv2.resize(crop, (d, d), interpolation=cv2.INTER_CUBIC)
        lum = crop @ np.array([.299, .587, .114], np.float32)
        lo, hi = np.percentile(lum, 8), np.percentile(lum, 99.5)
        t = np.clip((lum - lo) / max(hi - lo, 1), 0, 1) ** 0.9
        yy, xx = np.mgrid[0:d, 0:d]
        rr = np.hypot(xx - d / 2, yy - d / 2) / (d / 2)
        a = t * np.clip((1 - rr) / 0.025, 0, 1)
        col = np.empty((d, d, 3), np.float32)
        col[...] = (226, 240, 196)                                        # the pale yellow-green glow in the photo
        g = Image.fromarray(np.dstack([col, a * 255]).astype(np.uint8), 'RGBA')
        save_layer('front-uvglobe.png', g)
        boxes['front-uvglobe'] = [cx - r, cy - r, 2 * r, 2 * r]
        trim(g).save(os.path.join(CROPS, 'front', 'uvglobe.png'), optimize=True)

    # ---- the security thread (seen against the light): a continuous line, with the Swiss flag
    #      and 1000 at regular intervals (drawn from the SNB's description; repeat spacing illustrative)
    y0, y1 = THREAD_Y
    W, H = VW * S, int((y1 - y0) * S)
    th = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(th)
    dr.rectangle([0, int(H * 0.18), W * 2, int(H * 1.82)], fill=(58, 52, 66, 235))
    step = 40 * S * 2
    xx = 8 * S * 2
    try:
        from PIL import ImageFont
        font = ImageFont.truetype('arialbd.ttf', int(H * 1.05))
    except Exception:
        font = None
    while xx < W * 2:
        fsz = int(H * 1.2)
        fy = int(H * 0.4)
        dr.rectangle([xx, fy, xx + fsz, fy + fsz], fill=(214, 40, 40, 255))
        cxx, cyy = xx + fsz / 2, fy + fsz / 2
        a_, b_ = fsz * 0.3, fsz * 0.1
        dr.rectangle([cxx - b_, cyy - a_, cxx + b_, cyy + a_], fill=(255, 255, 255, 255))
        dr.rectangle([cxx - a_, cyy - b_, cxx + a_, cyy + b_], fill=(255, 255, 255, 255))
        dr.text((xx + fsz + 3 * S * 2, int(H * 0.32)), '1000', fill=(236, 230, 240, 255), font=font)
        xx += step
    th = th.resize((W, H), Image.LANCZOS)
    save_layer('thread.png', th)
    boxes['thread'] = [0, y0, VW, y1 - y0]

    # ---- the triangle window on the back: its own pixels inside the triangle (outline traced on the art)
    box = [36, 244, 56, 52]
    bx0, by0, bx1, by1 = px(box)
    rgb = np.asarray(imgs['back'])[by0:by1, bx0:bx1]
    k = 4
    big = Image.new('L', ((bx1 - bx0) * k, (by1 - by0) * k), 0)
    ImageDraw.Draw(big).polygon([((x - box[0]) * S * k, (y - box[1]) * S * k) for x, y in TRI], fill=255)
    a = np.asarray(big.resize((bx1 - bx0, by1 - by0), Image.LANCZOS), np.float32) / 255
    img = rgba(rgb, a)
    save_layer('back-triangle-cut.png', img)
    save_layer('back-triangle.png', img)
    boxes['back-triangle'] = box
    trim(img).save(os.path.join(CROPS, 'back', 'triangle.png'), optimize=True)

    # ---- Microperf: a Swiss cross of equidistant holes (illustrative: hole pitch and cross size are
    #      not published; the position is the SNB brochure's position D)
    box = [52, 462, 44, 44]
    W, H = box[2] * S, box[3] * S
    mp = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(mp)
    c = box[2] / 2
    arm, half = 18, 6                                   # note units: cross half-length, half bar width
    pitch = 2.0
    v = -arm
    while v <= arm + 1e-6:
        u = -arm
        while u <= arm + 1e-6:
            if (abs(u) <= half or abs(v) <= half):
                X, Y = (c + u) * S * 2, (c + v) * S * 2
                rr = 0.42 * S * 2
                dr.ellipse([X - rr, Y - rr, X + rr, Y + rr], fill=(255, 252, 236, 255))
            u += pitch
        v += pitch
    mp = mp.resize((W, H), Image.LANCZOS)
    save_layer('front-microperf.png', mp)
    boxes['front-microperf'] = box
    trim(mp).save(os.path.join(CROPS, 'front', 'microperf.png'), optimize=True)

    # ---- Tilt effect: the Swiss cross that stands out when the note is tilted backwards
    #      (illustrative: drawn from the SNB brochure photo at position C)
    box = [32, 323, 93, 43]
    W, H = box[2] * S, box[3] * S
    tl = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(tl)
    cx, cy = (80 - box[0]) * S * 2, (344 - box[1]) * S * 2
    arm, bar = 15 * S * 2, 5 * S * 2
    dr.rectangle([cx - bar, cy - arm, cx + bar, cy + arm], fill=(255, 246, 200, 255))
    dr.rectangle([cx - arm, cy - bar, cx + arm, cy + bar], fill=(255, 246, 200, 255))
    tl = tl.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    save_layer('front-tilt.png', tl)
    boxes['front-tilt'] = box
    trim(tl).save(os.path.join(CROPS, 'front', 'tilt.png'), optimize=True)


UV_SRC_CIRCLE = (198, 142, 92)     # the globe in source/found/snb-brochure-uv-globe.png (px)


def offset_layers(imgs, made, boxes):
    """Offset print: what lies under the intaglio and the foils. Intaglio line-work inside the
    intaglio features is closed over by the surrounding tint (a line is thinner than the kernel);
    the foil features (globe, strip) are filled from their surroundings."""
    plan = {'front': (['hand', 'numeral', 'bankname', 'tactile'], ['globe', 'strip']),
            'back': (['numeral', 'bankname', 'serial-a', 'serial-b'], [])}
    for side, im in imgs.items():
        rgb = np.asarray(im).copy()
        Hh, Ww = rgb.shape[:2]
        lines, solids = np.zeros((Hh, Ww), np.uint8), np.zeros((Hh, Ww), np.uint8)
        for group, target in ((plan[side][0], lines), (plan[side][1], solids)):
            for fid in group:
                name = f'{side}-{fid}'
                if name not in made:
                    continue
                a = np.asarray(made[name][0].getchannel('A'))
                x0, y0, x1, y1 = px(boxes[name])
                target[y0:y1, x0:x1] = np.maximum(target[y0:y1, x0:x1], a)
        k = disk(7)
        closed = cv2.merge([cv2.morphologyEx(rgb[..., c], cv2.MORPH_CLOSE, k) for c in range(3)])
        closed = cv2.merge([cv2.morphologyEx(closed[..., c], cv2.MORPH_CLOSE, disk(11)) for c in range(3)])
        m = cv2.GaussianBlur(cv2.dilate(lines, disk(3)).astype(np.float32) / 255, (0, 0), 2)[..., None]
        out = (rgb * (1 - m) + closed * m).astype(np.uint8)
        if solids.any():
            q = 4
            small = cv2.resize(out, (Ww // q, Hh // q), interpolation=cv2.INTER_AREA)
            ms = cv2.resize(cv2.dilate((solids > 40).astype(np.uint8) * 255, disk(4)), (Ww // q, Hh // q), interpolation=cv2.INTER_NEAREST)
            f = cv2.inpaint(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), ms, 14, cv2.INPAINT_TELEA)
            f = cv2.cvtColor(cv2.resize(f, (Ww, Hh), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
            b = cv2.GaussianBlur(cv2.dilate(solids, disk(4)).astype(np.float32) / 255, (0, 0), 3)[..., None]
            out = (out * (1 - b) + f * b).astype(np.uint8)
        Image.fromarray(out).resize((960, 2166), Image.LANCZOS).save(
            os.path.join(ROOT, 'assets', f'offset-{side}.jpg'), quality=88, optimize=True)


def write_masks(imgs, made, boxes):
    """Effect masks as data URIs (browsers fetch mask images with CORS, which file:// can't satisfy)."""
    out = ['/* generated by tools/extract_chf.py: effect masks as data URIs, as plain rules so they are parsed once */']
    # globe: the sphere itself
    out.append(f'.globe-fx{{-webkit-mask-image:{mask_uri(made["front-globe"][0].getchannel("A"))};mask-image:{mask_uri(made["front-globe"][0].getchannel("A"))}}}')
    # strip: the silver print (map of the language regions, outline of Switzerland, the large 1000):
    # light, low-colour pixels of the band -> rainbow when the note is tilted backwards
    x0, y0, x1, y1 = px(STRIP)
    rgb = np.asarray(imgs['front'])[y0:y1, x0:x1]
    L, A, B = lab_of(rgb)
    chroma = np.sqrt(A ** 2 + B ** 2)
    silver = ((L > 175) & (chroma < 26)).astype(np.uint8) * 255
    silver = cv2.morphologyEx(silver, cv2.MORPH_OPEN, disk(1))
    silver = keep_big(silver, 25)
    sm = Image.fromarray(cv2.GaussianBlur(silver, (0, 0), 1.2))
    u = mask_uri(sm, 1600)
    out.append(f'.strip-fx .rainbow{{-webkit-mask-image:{u};mask-image:{u}}}')
    os.makedirs(os.path.join(ROOT, 'source', 'masks'), exist_ok=True)
    sm.save(os.path.join(ROOT, 'source', 'masks', 'strip-silver.png'))
    # triangle: the glittering thread in the window
    bx0, by0, bx1, by1 = px([40, 266, 50, 22])
    rgb = np.asarray(imgs['back'])[by0:by1, bx0:bx1]
    L, A, B = lab_of(rgb)
    gl = ((L > 200)).astype(np.uint8) * 255
    u = mask_uri(Image.fromarray(cv2.GaussianBlur(gl, (0, 0), 1.0)), 600)
    out.append(f'.tri-fx{{-webkit-mask-image:{u};mask-image:{u}}}')
    # intaglio line-work of each face, for the lilac flow through the engraving (hand test)
    for side, cls in (('front', '.flow-front'), ('back', '.flow-back')):
        im = imgs[side].resize((480, 1083), Image.LANCZOS)
        L = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        bg = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, disk(4)), (0, 0), 3)
        lines = (bg - L - 8) > 0
        a = Image.fromarray((lines * 255).astype(np.uint8)).convert('1')
        buf = io.BytesIO(); a.save(buf, 'PNG', optimize=True)
        u = f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")'
        out.append(f'{cls}{{-webkit-mask-mode:luminance;mask-mode:luminance;-webkit-mask-image:{u};mask-image:{u}}}')
    open(os.path.join(ROOT, 'assets', 'masks.css'), 'w', encoding='utf8').write('\n'.join(out))


if __name__ == '__main__':
    main()
