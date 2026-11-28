"""
Cut every GBP 50 feature out of the levelled artwork as a clean alpha cut-out, open the see-through
windows, and write everything the page needs.

Inputs  source/<side>-levelled.png      (tools/upscale.py: Real-ESRGAN x2 + levels, 3072 x 1620)
        source/sam/<side>-<id>.png      (tools/sam_masks.py: Segment Anything masks)
Outputs gbp-50-front.png / -back.png    page artwork: the clear parts of both windows are transparent
        feature-crops/<side>/<id>.png   each feature at full resolution, transparent background
        assets/layers/<side>-<id>.png   the same, framed on its box at page resolution (3 px per unit)
        assets/boxes.js                 where each layer sits, in 720 x 320 note units
        assets/masks.css                optical-effect masks as data URIs (opens from file://)
        assets/print-<side>.webp        exploded view: the print without the separately layered parts
        assets/substrate.webp           exploded view: the polymer film with its two clear windows
        feature-crops/contact-sheet.png every cut-out on a dark background, for review

Methods (all keep the original pixels; alpha is binary with a ~1 px anti-aliased edge):
  sam     a Segment Anything mask, holes filled, largest part kept, edge smoothed
  ellipse an ellipse fitted to a SAM mask (the round portrait frames)
  halo    the small window: its slightly greyer clear area, found by heavy smoothing
  ink     colour separation inside a seed box: strokes only, counters stay open
  discs   exact circles (the tactile dots)
Hand-cleaned files in assets/overrides/<side>-<id>.png always win.

Run:  python tools/cutouts.py
"""
import base64, io, json, math, os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VB_W, VB_H = 720, 320
PAD = 3                      # note units around each feature's box
PAGE_K = 1440 / VB_W * 1.5   # page layers: 3 px per note unit (1.5x the 1440 px face)
SAM = os.path.join(ROOT, 'source', 'sam')
LAYERS = os.path.join(ROOT, 'assets', 'layers')
CROPS = os.path.join(ROOT, 'feature-crops')
OVR = os.path.join(ROOT, 'assets', 'overrides')

# tactile dots: four clusters of four, left edge of the front (measured from the embossing shadows)
DOTS = [(x, y0 + dy) for y0 in (19.3, 79.3, 139.3, 199.3) for dy in (0, 10) for x in (28.5, 41.5)]

# side, id, method, geometry / options
FEATURES = [
    ('front', 'crown',        'sam',     dict(mask='front-crown')),
    ('front', 'hologram',     'sam',     dict(mask='front-hologram')),
    ('front', 'portrait',     'ellipse', dict(mask='front-oval')),
    ('front', 'window',       'window',  dict(frame='front-frame', oval='front-oval')),
    ('front', 'windowfoil',   'ink',     dict(seed=(124, 88, 198, 246), ink='foil', within='front-frame')),
    ('front', 'smallwindow',  'halo',    dict(seed=(620, 222, 690, 300))),
    ('front', 'raised',       'ink',     dict(seed=(224, 14, 486, 74), ink='black', t=70)),
    ('front', 'tactile',      'discs',   dict(dots=DOTS, r=2.7)),
    ('front', 'microprint',   'ink',     dict(seed=(474, 272, 626, 296), ink='black', t=95)),
    ('front', 'cashier',      'ink',     dict(seed=(12, 79, 74, 106), ink='red', t=14)),
    ('back',  'redfoil',      'sam',     dict(mask='back-redfoil')),
    ('back',  'portrait',     'ellipse', dict(mask='back-oval-b')),
    ('back',  'window',       'window',  dict(frame='back-frame-b', oval='back-oval-b')),
    ('back',  'smallwindow',  'mirror',  dict(of='smallwindow', seed=(30, 222, 100, 300))),   # the same window, seen from behind
    ('back',  'turing',       'sam',     dict(mask='back-turing')),
    ('back',  'tape',         'sam',     dict(mask='back-tape')),
    ('back',  'table',        'ink',     dict(seed=(58, 66, 308, 184), ink='outlined')),
    ('back',  'quote',        'ink',     dict(seed=(312, 258, 466, 286), ink='black', t=80)),
    ('back',  'signature',    'ink',     dict(seed=(370, 230, 476, 262), ink='white', drop_edge='left', min_size=2.2)),
    ('back',  'serial-v',     'ink',     dict(seed=(28, 50, 54, 220), ink='blue')),
    ('back',  'serial-h',     'ink',     dict(seed=(540, 269, 694, 294), ink='paper')),
]


def disk(r):
    r = max(1, int(round(r)))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def fill_holes(m):
    h, w = m.shape
    ff = m.copy()
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    return m | cv2.bitwise_not(ff)


def largest(m, keep_frac=0.0):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1:
        return m
    big = st[1:, 4].max()
    out = np.zeros_like(m)
    for k in range(1, n):
        if st[k, 4] >= max(big * keep_frac, 1) and (keep_frac > 0 or st[k, 4] == big):
            out[lab == k] = 255
    return out


def aa(binary, sigma=0.8):
    f = cv2.GaussianBlur(binary.astype(np.float32) / 255, (0, 0), sigma)
    return np.clip((f - 0.5) * 2.2 + 0.5, 0, 1)


def smooth(m, r):
    """round off a mask's outline: blur and re-threshold"""
    return ((cv2.GaussianBlur(m.astype(np.float32), (0, 0), r) > 127) * 255).astype(np.uint8)


MASKS = {}


class Art:
    def __init__(self, side):
        self.side = side
        self.rgb = np.asarray(Image.open(os.path.join(ROOT, 'source', f'{side}-levelled.png')).convert('RGB'))
        self.H, self.W = self.rgb.shape[:2]
        self.sx, self.sy = self.W / VB_W, self.H / VB_H
        self.s = (self.sx + self.sy) / 2

    def px(self, x, y):
        return int(round(x * self.sx)), int(round(y * self.sy))

    def rect(self, box):
        x0, y0, x1, y1 = box
        m = np.zeros((self.H, self.W), np.uint8)
        (a, b), (c, d) = self.px(x0, y0), self.px(x1, y1)
        m[b:d, a:c] = 255
        return m

    def sam(self, name):
        return (np.asarray(Image.open(os.path.join(SAM, name + '.png'))) > 127).astype(np.uint8) * 255


def ink_strokes(art, seed, kind, t=None):
    """binary strokes of one ink inside the seed box (full-image mask)"""
    rgb = art.rgb
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1] - 128, lab[..., 2] - 128
    S = art.rect(seed) > 0
    chroma = np.hypot(A, B)
    if kind == 'black':           # dark, near-neutral ink (blackletter, quote, microprint)
        m = (L < (t or 80)) & (chroma < 40)
    elif kind == 'red':           # red ink on the white polymer
        m = (A > (t or 22)) & (A > 0.6 * B) & (L < 230)          # red, not the yellow dots
    elif kind == 'white':         # white handwriting over the dark suit
        m = (L > 175) & (chroma < 20)
    elif kind == 'blue':          # dark blue serial over the red print
        m = (B < -2) & (L < 175) & (A < 30)
    elif kind == 'paper':         # anything printed on the white polymer
        pl = np.median(L[S])
        m = ((pl - L) > 45) | (chroma > 42)
    elif kind == 'foil':          # the window foil: gold (yellow) and green
        gold = ((B > 18) & (A > -25) & (L > 100)).astype(np.uint8) * 255
        gold[~S] = 0
        col = fill_holes(cv2.morphologyEx(largest(gold, 0.05), cv2.MORPH_CLOSE, disk(2.5 * art.s)))   # the foil column
        green = (((A < -14) & (L < 215)) & S).astype(np.uint8) * 255
        discs = cv2.morphologyEx(green, cv2.MORPH_OPEN, disk(1.6 * art.s))          # the two green foil discs
        discs = cv2.dilate(discs, disk(0.3 * art.s)) & cv2.morphologyEx(green, cv2.MORPH_CLOSE, disk(0.4 * art.s))
        discs = fill_holes(discs)
        m = (gold > 0) | ((col > 0) & (L > 200) & (B > 2)) | (discs > 0)   # gold, its pale sheen, the green discs
    elif kind == 'outlined':      # white letters with a dark outline (the table)
        white = ((L > 198) & (chroma < 18)).astype(np.uint8) * 255
        dark = ((L < 100) & S).astype(np.uint8) * 255
        u = cv2.morphologyEx((white | dark) & (S.astype(np.uint8) * 255), cv2.MORPH_CLOSE, disk(0.2 * art.s))
        n, lab_, st, _ = cv2.connectedComponentsWithStats(u, 8)
        m = np.zeros(u.shape, bool)
        for k in range(1, n):
            if st[k, 4] < (0.6 * art.s) ** 2 or st[k, 3] > 16 * art.sy or st[k, 2] > 70 * art.sx:
                continue                                    # specks, and big dark parts of the machine photo
            comp = lab_ == k
            wf = (white[comp] > 0).mean()
            if 0.1 < wf < 0.9:                            # a letter: both its white fill and its outline
                m |= comp
    else:
        raise ValueError(kind)
    m = m & S
    m = m.astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.12 * art.s))
    # drop specks: pieces smaller than a fraction of a glyph
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros_like(m)
    for k in range(1, n):
        if st[k, 4] >= (0.35 * art.s) ** 2:
            out[lab_ == k] = 255
    return out


def cut_feature(art, fid, method, o):
    """returns the binary (0/255) silhouette of a feature, full-image size"""
    if method == 'sam':
        m = art.sam(o['mask'])
        for box in o.get('cut', []):
            m[art.rect(box) > 0] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(0.4 * art.s))
        m = fill_holes(largest(m))
        return smooth(m, 0.35 * art.s)
    if method == 'ellipse':
        m = largest(art.sam(o['mask']))
        cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        e = cv2.fitEllipse(max(cnts, key=cv2.contourArea))
        out = np.zeros_like(m)
        cv2.ellipse(out, e, 255, -1, lineType=cv2.LINE_8)
        return out
    if method == 'window':      # the frame and everything inside it (the portrait oval beside it is separate)
        oval = cut_feature(art, 'oval', 'ellipse', dict(mask=o['oval']))
        f = largest(art.sam(o['frame']), 0.05) | oval
        f = fill_holes(cv2.morphologyEx(f, cv2.MORPH_CLOSE, disk(1.5 * art.s)))
        f = smooth(largest(f), 0.4 * art.s)
        f[cv2.dilate(oval, disk(0.3 * art.s)) > 0] = 0
        return largest(cv2.morphologyEx(f, cv2.MORPH_OPEN, disk(1.0 * art.s)))
    if method == 'halo':
        x0, y0, x1, y1 = o['seed']
        L = cv2.cvtColor(art.rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
        b = cv2.GaussianBlur(L, (0, 0), 1.6 * art.s)
        S = art.rect(o['seed']) > 0
        ref = np.percentile(b[S], 92)                      # the opaque white around it
        m = ((b < ref - 4.0) & S).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(2 * art.s))
        m = fill_holes(largest(m))
        m = smooth(m, 1.2 * art.s)
        xs = np.nonzero(m.any(0))[0]
        c2 = xs.min() + xs.max()                          # the window is symmetric: average with its mirror
        mir = np.zeros_like(m)
        lo, hi = max(0, c2 - art.W + 1), min(art.W, c2 + 1)
        mir[:, lo:hi] = m[:, c2 - np.arange(lo, hi)]
        return smooth(((m.astype(np.float32) + mir) / 2 > 127).astype(np.uint8) * 255, 0.6 * art.s)
    if method == 'ink':
        st = ink_strokes(art, o['seed'], o['ink'], o.get('t'))
        if o.get('min_size'):                            # stray specks: pieces smaller than min_size units across
            n, lab_, stt, _ = cv2.connectedComponentsWithStats(st, 8)
            for k in range(1, n):
                if max(stt[k, 2] / art.sx, stt[k, 3] / art.sy) < o['min_size']:
                    st[lab_ == k] = 0
        if o.get('drop_edge') == 'left':                 # pieces cut by the seed's left edge belong to something else
            n, lab_, stt, _ = cv2.connectedComponentsWithStats(st, 8)
            xl = art.px(o['seed'][0], 0)[0]
            for k in range(1, n):
                if stt[k, 0] <= xl + 1:
                    st[lab_ == k] = 0
        if 'within' in o:
            w = fill_holes(cv2.morphologyEx(largest(art.sam(o['within']), 0.05), cv2.MORPH_CLOSE, disk(1.5 * art.s)))
            st[w == 0] = 0
        return cv2.dilate(st, disk(0.15 * art.s))
    if method == 'mirror':      # the same window seen from the reverse: mirrored, centred on the reverse's own window
        fm = MASKS[('front', o['of'])]
        m = fm[:, ::-1].copy()
        own = cut_feature(art, o['of'], 'halo', dict(seed=o['seed']))
        dx = int(round(np.nonzero(own.any(0))[0].mean() - np.nonzero(m.any(0))[0].mean()))
        dy = int(round(np.nonzero(own.any(1))[0].mean() - np.nonzero(m.any(1))[0].mean()))
        return np.roll(np.roll(m, dx, 1), dy, 0)
    if method == 'discs':
        m = np.zeros((art.H, art.W), np.uint8)
        for x, y in o['dots']:
            cv2.ellipse(m, (art.px(x, y)), (int(o['r'] * art.sx), int(o['r'] * art.sy)), 0, 0, 360, 255, -1)
        return m
    raise ValueError(method)


def bbox_units(art, m):
    ys, xs = np.nonzero(m)
    x0, x1 = xs.min() / art.sx - PAD, (xs.max() + 1) / art.sx + PAD
    y0, y1 = ys.min() / art.sy - PAD, (ys.max() + 1) / art.sy + PAD
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(VB_W, x1), min(VB_H, y1)
    return [round(float(v), 2) for v in (x0, y0, x1 - x0, y1 - y0)]


def frame_rgba(art, rgba_full, box):
    """crop a full-size RGBA onto a box (note units) and scale it to page resolution"""
    x, y, w, h = box
    (a, b), (c, d) = art.px(x, y), art.px(x + w, y + h)
    im = Image.fromarray(rgba_full[b:d, a:c], 'RGBA')
    return im.resize((max(1, round(w * PAGE_K)), max(1, round(h * PAGE_K * (art.sy / art.sx)))), Image.LANCZOS)


def window_alpha(art, win_masks):
    """Page artwork alpha: the windows' clear polymer is see-through (a little haze stays), while
    everything printed or foiled on the window stays opaque. Colour-to-alpha against the clear tone."""
    rgb = art.rgb.astype(np.float32)
    win = np.zeros((art.H, art.W), np.uint8)
    for m in win_masks:
        win |= m
    win = cv2.morphologyEx(win, cv2.MORPH_CLOSE, disk(1.2 * art.s))   # no seam where the oval meets the frame
    inside = win > 0
    lum = rgb @ np.float32([.299, .587, .114])
    ref = np.percentile(rgb[inside & (lum > np.percentile(lum[inside], 70))], 50, axis=0)   # clear tone
    # print on the window is opaque ink (light grey, gold, maroon...): anything that differs from the clear
    # tone is kept solid in its own colour; only the clear polymer itself becomes see-through
    dev = np.max(np.abs(rgb - ref), axis=2) / 255
    a_ink = np.clip((dev - 0.035) / 0.09, 0, 1)
    HAZE = 0.14
    a = np.maximum(a_ink, HAZE)
    soft = aa(win, 1.0 * art.s)                                   # the window's edge fades in over ~1 unit
    alpha = 1 - soft * (1 - a)
    # (colours are kept as scanned: the haze shows the clear tone faintly over whatever lies behind)
    col = rgb
    return np.dstack([col, alpha * 255]).astype(np.uint8), win


def png_data_uri(img):
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    return 'url("data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode() + '")'


def mask_rule(sel, alpha_img, max_side=600):
    a = alpha_img.getchannel('A') if alpha_img.mode == 'RGBA' else alpha_img.convert('L')
    k = min(1.0, max_side / max(a.size))
    if k < 1:
        a = a.resize((round(a.width * k), round(a.height * k)), Image.LANCZOS)
    m = Image.new('LA', a.size, 255)
    m.putalpha(a)
    u = png_data_uri(m)
    return f'{sel}{{-webkit-mask-image:{u};mask-image:{u}}}'


def main():
    os.makedirs(LAYERS, exist_ok=True)
    arts = {s: Art(s) for s in ('front', 'back')}
    boxes, masks, framed = {}, {}, {}
    for side, fid, method, o in FEATURES:
        art = arts[side]
        m = cut_feature(art, fid, method, o)
        masks[(side, fid)] = m
        MASKS[(side, fid)] = m
        alpha = aa(m) if method not in ('discs', 'ellipse') else aa(m, 0.9)
        rgba = np.dstack([art.rgb, (alpha * 255).astype(np.uint8)])
        box = bbox_units(art, m)
        name = f'{side}-{fid}'
        boxes[name] = box
        # full-resolution presentation crop
        ys, xs = np.nonzero(m)
        mg = 12
        crop = rgba[max(0, ys.min() - mg):ys.max() + mg, max(0, xs.min() - mg):xs.max() + mg]
        os.makedirs(os.path.join(CROPS, side), exist_ok=True)
        Image.fromarray(crop, 'RGBA').save(os.path.join(CROPS, side, f'{fid}.png'), optimize=True)
        page = frame_rgba(art, rgba, box)
        ov = os.path.join(OVR, name + '.png')
        if os.path.exists(ov):
            page = Image.open(ov).convert('RGBA').resize(page.size, Image.LANCZOS)
            print('  override', name)
        page.save(os.path.join(LAYERS, name + '.png'), optimize=True)
        framed[name] = page
        print(f'{side:5} {fid:12} {method:8} box {box}')

    # ---- page artwork: open the windows ----
    for side, art in arts.items():
        wins = [masks[(side, 'window')], masks[(side, 'portrait')], masks[(side, 'smallwindow')]]
        rgba, _ = window_alpha(art, wins)
        Image.fromarray(rgba, 'RGBA').save(os.path.join(ROOT, f'gbp-50-{side}.png'), optimize=True)
        art.rgba = rgba
        print('artwork', side, 'windows opened')
        # the window cut-outs carry the see-through alpha too (their highlight must not fill the window in)
        for fid in ('window', 'portrait', 'smallwindow'):
            m = masks[(side, fid)]
            a = (aa(m) * rgba[..., 3]).astype(np.uint8)
            cut = np.dstack([rgba[..., :3], a])
            name = f'{side}-{fid}'
            if not os.path.exists(os.path.join(OVR, name + '.png')):
                frame_rgba(art, cut, boxes[name]).save(os.path.join(LAYERS, name + '.png'), optimize=True)
            ys, xs = np.nonzero(m)
            Image.fromarray(cut[max(0, ys.min() - 12):ys.max() + 12, max(0, xs.min() - 12):xs.max() + 12], 'RGBA') \
                .save(os.path.join(CROPS, side, f'{fid}.png'), optimize=True)

    try:
        import extras
    except ImportError:
        extras = None
    if extras:
        extras.build(arts, masks, boxes, framed)

    with open(os.path.join(ROOT, 'assets', 'boxes.js'), 'w', encoding='utf8') as f:
        f.write('// generated by tools/cutouts.py: where each extracted layer sits (720x320 note units)\n')
        f.write('const BOXES = ' + json.dumps(boxes, indent=1) + ';\n')
    contact_sheet()


def contact_sheet():
    files = []
    for side in ('front', 'back'):
        d = os.path.join(CROPS, side)
        files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.png')]
    cols, cw, ch = 6, 300, 250
    rows = math.ceil(len(files) / cols)
    sheet = Image.new('RGB', (cols * cw, rows * ch), (40, 40, 46))
    ds = ImageDraw.Draw(sheet)
    for i, p in enumerate(files):
        t = Image.open(p).convert('RGBA')
        t.thumbnail((cw - 20, ch - 40))
        bg = Image.new('RGBA', t.size, (22, 24, 30, 255))
        bg.alpha_composite(t)
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(bg.convert('RGB'), (x + 10, y + 10))
        ds.text((x + 10, y + ch - 22), os.path.relpath(p, CROPS).replace(os.sep, '/'), fill=(230, 230, 230))
    sheet.save(os.path.join(CROPS, 'contact-sheet.png'))


if __name__ == '__main__':
    main()
